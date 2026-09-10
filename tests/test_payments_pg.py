"""Postgres-backed payment replay tests (Neon). Skipped without DATABASE_URL.

These prove the 1.3 upgrade: the reserve is atomic across processes (PK +
INSERT ... ON CONFLICT), exactly one concurrent verifier wins, failed
verifications release their reservation, and stale reservations self-heal.
Each test cleans up its own rows — nothing persists.
"""

import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest

from api.env import load_local_env

load_local_env()  # local dev only; production injects env directly

from api.db import get_conn, is_configured
from lumen import payments

pytestmark = pytest.mark.skipif(
    not is_configured(), reason="DATABASE_URL not set (Neon not linked)"
)


def _fake_hash() -> str:
    return "0x" + (uuid.uuid4().hex + uuid.uuid4().hex)[:64]


def _delete_row(tx_hash_lower: str) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM used_txs WHERE tx_hash = %s", (tx_hash_lower,))


def test_pg_reserve_is_atomic():
    """First reserve wins, second loses, release frees it again."""
    tx = _fake_hash()
    try:
        assert payments._pg_try_reserve(tx) is True
        assert payments._pg_try_reserve(tx) is False
        assert payments._pg_is_used(tx) is False  # pending, not consumed
        payments._pg_release(tx)
        assert payments._pg_try_reserve(tx) is True
    finally:
        _delete_row(tx)


def test_pg_completed_payment_blocks_reuse():
    """A recorded payment can never be reserved again."""
    tx = _fake_hash()
    try:
        payments._pg_record(tx, 10000, "0xabc")
        assert payments._pg_is_used(tx) is True
        assert payments._pg_try_reserve(tx) is False
        payments._pg_release(tx)  # must NOT touch completed rows
        assert payments._pg_is_used(tx) is True
    finally:
        _delete_row(tx)


def test_pg_stale_reservation_self_heals():
    """A crashed verifier's abandoned reservation expires via TTL."""
    tx = _fake_hash()
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO used_txs (tx_hash, used_at) VALUES "
                    "(%s, now() - make_interval(secs => %s))",
                    (tx, payments._RESERVATION_TTL_SECONDS + 60),
                )
        assert payments._pg_try_reserve(tx) is True
    finally:
        _delete_row(tx)


def _fake_onchain_valid(tx_hash: str, tx_hash_lower: str) -> dict:
    payments._record_used(tx_hash_lower, 10000, "0xabc")
    return {"valid": True, "amount_usdc": 0.01,
            "from_address": "0xabc", "tx_hash": tx_hash, "reason": None}


def test_concurrent_verify_single_winner(monkeypatch):
    """Two simultaneous verifications of one payment: exactly one wins."""
    monkeypatch.setattr(
        payments, "_verify_usdc_payment_onchain", _fake_onchain_valid
    )
    tx = _fake_hash()
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(payments.verify_usdc_payment, [tx, tx]))
        valid = [r for r in results if r.get("valid")]
        used = [r for r in results
                if r.get("reason") == "Transaction hash already used."]
        assert len(valid) == 1
        assert len(used) == 1
        assert payments._pg_is_used(tx) is True
    finally:
        _delete_row(tx)


def test_invalid_verification_releases_reservation(monkeypatch):
    """A failed verification frees the hash for a later retry."""
    calls = []

    def _fake_invalid(tx_hash: str, tx_hash_lower: str) -> dict:
        calls.append(tx_hash_lower)
        return {"valid": False, "reason": "No USDC transfer found."}

    monkeypatch.setattr(payments, "_verify_usdc_payment_onchain", _fake_invalid)
    tx = _fake_hash()
    try:
        first = payments.verify_usdc_payment(tx)
        second = payments.verify_usdc_payment(tx)
        assert first["valid"] is False
        assert second["valid"] is False
        assert len(calls) == 2, "second call was wrongly blocked as used"
        assert payments._pg_is_used(tx) is False
    finally:
        _delete_row(tx)


def test_file_fallback_when_pg_unconfigured(tmp_path, monkeypatch):
    """File guard still closes the replay race with no database."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_UNPOOLED", raising=False)
    monkeypatch.setattr(
        payments, "USED_TX_FILE", tmp_path / "used_txs.json"
    )
    monkeypatch.setattr(
        payments, "_verify_usdc_payment_onchain", _fake_onchain_valid
    )
    tx = _fake_hash()
    first = payments.verify_usdc_payment(tx)
    second = payments.verify_usdc_payment(tx)
    assert first["valid"] is True
    assert second["reason"] == "Transaction hash already used."
