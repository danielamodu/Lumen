"""Postgres-backed tenant tests (Neon). Skipped without DATABASE_URL.

These prove the 1.2 cutover: create/resolve round-trips through Postgres,
unknown/inactive keys still 401, and the file fallback still works when the
database is unconfigured. Each test cleans up its own rows — nothing persists.
"""

import uuid

import pytest
from fastapi import HTTPException

from api.env import load_local_env

load_local_env()  # local dev only; production injects env directly

from api import auth
from api.db import get_conn, is_configured

pytestmark = pytest.mark.skipif(
    not is_configured(), reason="DATABASE_URL not set (Neon not linked)"
)


def _delete_row(hashed_key: str) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tenants WHERE key_hash = %s", (hashed_key,))


def test_pg_create_and_resolve_roundtrip():
    key, info = auth.create_tenant(f"pg-probe-{uuid.uuid4().hex[:8]}")
    try:
        resolved = auth.resolve_tenant(key)
        assert resolved["tenant_id"] == info["tenant_id"]
        assert resolved["name"] == info["name"]
        assert resolved["is_admin"] is False
    finally:
        _delete_row(auth.hash_api_key(key))


def test_pg_unknown_key_401():
    with pytest.raises(HTTPException) as exc_info:
        auth.resolve_tenant("lmn_" + "0" * 32)
    assert exc_info.value.status_code == 401


def test_pg_inactive_key_401():
    key, info = auth.create_tenant(f"pg-inactive-{uuid.uuid4().hex[:8]}")
    hashed = auth.hash_api_key(key)
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE tenants SET active = FALSE WHERE key_hash = %s",
                    (hashed,),
                )
        with pytest.raises(HTTPException) as exc_info:
            auth.resolve_tenant(key)
        assert exc_info.value.status_code == 401
    finally:
        _delete_row(hashed)


def test_file_fallback_when_pg_unconfigured(tmp_path, monkeypatch):
    """File store still works with no database (transitional path)."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_UNPOOLED", raising=False)
    monkeypatch.setattr(auth, "TENANTS_FILE", tmp_path / "tenants.json")
    key, info = auth.create_tenant("fallback-probe")
    resolved = auth.resolve_tenant(key)
    assert resolved["tenant_id"] == info["tenant_id"]
