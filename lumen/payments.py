"""Base mainnet USDC payment verification for Lumen."""

import json
import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from web3 import Web3

from api import db as _db

# Base mainnet RPC
BASE_RPC_URL = "https://mainnet.base.org"

# USDC on Base mainnet
USDC_CONTRACT = "0x83363266e35bc7cc0509e06cc9b69da3ad762913"

# Recipient wallet (Base mainnet USDC)
RECIPIENT = "0xf821447c6bd7c54e5fc2bd92239f4d8ed73c52f0"

# Minimum payment: 0.01 USDC = 10000 units (6 decimals)
MIN_AMOUNT_UNITS = 10000

# Max transaction age: 1 hour
MAX_TX_AGE_SECONDS = 3600

# Used transaction hashes store
USED_TX_FILE = Path.home() / ".sibyl-memory" / "used_txs.json"

# Serializes the check-reserve-record sequence and guards the used-tx file so
# concurrent requests (FastAPI runs sync handlers in a threadpool) cannot
# replay a single payment across multiple /market/brief calls.
_verify_lock = threading.Lock()
_in_progress: set = set()

# A pending (uncompleted) Postgres reservation older than this is treated as
# abandoned (crashed verifier) and reaped on the next reserve attempt, so a
# crash between reserve and release can never brick a payment hash forever.
_RESERVATION_TTL_SECONDS = 600

# Set once we warn about file fallback so concurrent requests don't spam logs.
_pg_fallback_warned = False


def _warn_fallback(reason: str) -> None:
    """Log file-fallback once per process (keeps request logs readable)."""
    global _pg_fallback_warned
    if not _pg_fallback_warned:
        _pg_fallback_warned = True
        logging.getLogger("lumen.payments").warning(
            "used_txs: %s. Using file fallback (transitional).", reason
        )

# USDC Transfer event ABI (minimal)
USDC_TRANSFER_ABI = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": True,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": False,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]

# ERC20 balanceOf/transfer ABI (minimal)
ERC20_ABI = [
    {
        "inputs": [
            {"name": "account", "type": "address"}
        ],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    }
]


def _load_used_txs() -> set:
    """Load set of used transaction hashes."""
    if not USED_TX_FILE.exists():
        return set()
    try:
        with open(USED_TX_FILE, "r") as f:
            data = json.load(f)
        return set(data.get("used", []))
    except Exception:
        return set()


def _save_used_tx(tx_hash: str) -> None:
    """Mark a transaction hash as used (atomic write, lock-guarded)."""
    USED_TX_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _verify_lock:
        used = _load_used_txs()
        used.add(tx_hash.lower())
        tmp = USED_TX_FILE.with_name(USED_TX_FILE.name + ".tmp")
        with open(tmp, "w") as f:
            json.dump({"used": list(used)}, f)
        tmp.replace(USED_TX_FILE)


# ---------------------------------------------------------------------------
# Postgres primary (Neon). Completed rows (amount_units NOT NULL) are consumed
# payments; pending rows (NULL amount) are in-flight reservations owned by a
# verifier right now. The PK makes the reserve atomic across processes and
# machines — the file + in-memory set only ever guarded one process.
# ---------------------------------------------------------------------------

def _pg_is_used(tx_hash_lower: str) -> bool:
    """True if a COMPLETED payment row exists for this hash."""
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM used_txs "
                "WHERE tx_hash = %s AND amount_units IS NOT NULL",
                (tx_hash_lower,),
            )
            return cur.fetchone() is not None


def _pg_try_reserve(tx_hash_lower: str) -> bool:
    """Atomically reserve this hash. True if WE won it, False if taken.

    Reaps abandoned reservations (pending older than the TTL) first so a
    crashed verifier can never brick a hash forever.
    """
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM used_txs WHERE amount_units IS NULL "
                "AND used_at < now() - make_interval(secs => %s)",
                (_RESERVATION_TTL_SECONDS,),
            )
            cur.execute(
                "INSERT INTO used_txs (tx_hash) VALUES (%s) "
                "ON CONFLICT (tx_hash) DO NOTHING",
                (tx_hash_lower,),
            )
            return cur.rowcount == 1


def _pg_record(tx_hash_lower: str, amount_units: int, from_address: str) -> None:
    """Complete a reservation (or record directly as safety net)."""
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO used_txs (tx_hash, amount_units, from_address) "
                "VALUES (%s, %s, %s) "
                "ON CONFLICT (tx_hash) DO UPDATE SET "
                "amount_units = EXCLUDED.amount_units, "
                "from_address = EXCLUDED.from_address, "
                "used_at = now()",
                (tx_hash_lower, amount_units, from_address),
            )


def _pg_release(tx_hash_lower: str) -> None:
    """Release our pending reservation after a FAILED verification.

    Only deletes pending rows — a completed payment is never touched, so a
    late failure verdict can never un-consume a valid payment.
    """
    try:
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM used_txs "
                    "WHERE tx_hash = %s AND amount_units IS NULL",
                    (tx_hash_lower,),
                )
    except Exception:
        pass  # best-effort: stale reservations self-heal via TTL


def _record_used(tx_hash_lower: str, amount_units: int, from_address: str) -> None:
    """Record a VALID payment as consumed (Postgres primary, file fallback)."""
    if _db.is_configured():
        try:
            _pg_record(tx_hash_lower, amount_units, from_address)
            return
        except Exception as exc:
            _warn_fallback(f"Postgres record failed ({type(exc).__name__})")
    _save_used_tx(tx_hash_lower)


def verify_usdc_payment(tx_hash: str) -> dict:
    """Verify a USDC payment on Base mainnet.
    
    Args:
        tx_hash: Transaction hash to verify.
        
    Returns dict with:
        valid: bool
        reason: str (if not valid)
        amount_usdc: float (if valid)
        from_address: str (if valid)
        
    Does NOT raise — always returns a dict.
    """
    if not tx_hash or not tx_hash.startswith("0x"):
        return {
            "valid": False,
            "reason": "Invalid transaction hash format."
        }

    tx_hash_lower = tx_hash.lower()

    # Reserve this tx: reject if already consumed, or if another request is
    # verifying it right now. Postgres reserve is atomic across processes and
    # machines; the in-memory set + file guard the single-process fallback.
    # On invalid payments a Postgres reservation is released; only valid
    # payments are ever recorded as consumed.
    use_pg = _db.is_configured()
    reserved_pg = False
    with _verify_lock:
        if use_pg:
            try:
                if _pg_is_used(tx_hash_lower) or tx_hash_lower in _in_progress:
                    return {
                        "valid": False,
                        "reason": "Transaction hash already used."
                    }
                if not _pg_try_reserve(tx_hash_lower):
                    return {
                        "valid": False,
                        "reason": "Transaction hash already used."
                    }
                reserved_pg = True
            except Exception as exc:
                _warn_fallback(
                    f"Postgres reserve failed ({type(exc).__name__})"
                )
                use_pg = False
        if not use_pg:
            used = _load_used_txs()
            if tx_hash_lower in used or tx_hash_lower in _in_progress:
                return {
                    "valid": False,
                    "reason": "Transaction hash already used."
                }
        _in_progress.add(tx_hash_lower)

    try:
        result = _verify_usdc_payment_onchain(tx_hash, tx_hash_lower)
    finally:
        with _verify_lock:
            _in_progress.discard(tx_hash_lower)

    if use_pg and reserved_pg and not result.get("valid"):
        _pg_release(tx_hash_lower)
    return result


def _verify_usdc_payment_onchain(tx_hash: str, tx_hash_lower: str) -> dict:
    """Perform the onchain verification for a tx already reserved by
    verify_usdc_payment. Records the hash as used only on a valid payment."""
    try:
        w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
        
        if not w3.is_connected():
            return {
                "valid": False,
                "reason": "Cannot connect to Base mainnet RPC."
            }
        
        # Get transaction receipt
        try:
            receipt = w3.eth.get_transaction_receipt(tx_hash)
        except Exception:
            return {
                "valid": False,
                "reason": "Transaction not found or not confirmed."
            }
        
        if receipt is None:
            return {
                "valid": False,
                "reason": "Transaction not confirmed yet."
            }
        
        if receipt["status"] != 1:
            return {
                "valid": False,
                "reason": "Transaction failed onchain."
            }
        
        # Get transaction for timestamp
        try:
            tx = w3.eth.get_transaction(tx_hash)
            block = w3.eth.get_block(receipt["blockNumber"])
            tx_timestamp = block["timestamp"]
        except Exception:
            return {
                "valid": False,
                "reason": "Cannot fetch transaction details."
            }
        
        # Check transaction age
        now = int(time.time())
        age = now - tx_timestamp
        if age > MAX_TX_AGE_SECONDS:
            return {
                "valid": False,
                "reason": (
                    f"Transaction too old "
                    f"({age // 60} minutes). "
                    f"Must be within 1 hour."
                )
            }
        
        # Parse USDC Transfer logs
        usdc_address = Web3.to_checksum_address(
            USDC_CONTRACT
        )
        recipient_checksum = Web3.to_checksum_address(
            RECIPIENT
        )
        
        usdc_contract = w3.eth.contract(
            address=usdc_address,
            abi=USDC_TRANSFER_ABI
        )
        
        # Find Transfer event to our wallet
        transfer_found = False
        amount_units = 0
        from_address = ""
        
        try:
            logs = usdc_contract.events.Transfer().process_receipt(
                receipt
            )
        except Exception:
            logs = []
        
        for log in logs:
            to_addr = log["args"]["to"]
            if (Web3.to_checksum_address(to_addr) == 
                    recipient_checksum):
                amount_units = log["args"]["value"]
                from_address = log["args"]["from"]
                transfer_found = True
                break
        
        if not transfer_found:
            return {
                "valid": False,
                "reason": (
                    "No USDC transfer to Lumen wallet "
                    "found in this transaction."
                )
            }
        
        if amount_units < MIN_AMOUNT_UNITS:
            amount_usdc = amount_units / 1_000_000
            return {
                "valid": False,
                "reason": (
                    f"Insufficient payment: "
                    f"{amount_usdc:.4f} USDC. "
                    f"Minimum: 0.01 USDC."
                )
            }
        
        # Valid payment — mark as used
        _record_used(tx_hash_lower, amount_units, from_address)
        
        return {
            "valid": True,
            "amount_usdc": amount_units / 1_000_000,
            "from_address": from_address,
            "tx_hash": tx_hash,
            "reason": None
        }
        
    except Exception as exc:
        return {
            "valid": False,
            "reason": f"Verification error: {str(exc)}"
        }
