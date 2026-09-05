"""Base mainnet USDC payment verification for Lumen."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from web3 import Web3

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
    """Mark a transaction hash as used."""
    USED_TX_FILE.parent.mkdir(parents=True, exist_ok=True)
    used = _load_used_txs()
    used.add(tx_hash.lower())
    with open(USED_TX_FILE, "w") as f:
        json.dump({"used": list(used)}, f)


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
    
    # Check if already used
    used = _load_used_txs()
    if tx_hash_lower in used:
        return {
            "valid": False,
            "reason": "Transaction hash already used."
        }
    
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
        _save_used_tx(tx_hash_lower)
        
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
