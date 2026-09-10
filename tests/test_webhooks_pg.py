"""Postgres-backed webhook tests (Neon). Skipped without DATABASE_URL.

These prove the 1.4 upgrade: registration/listing/deletion through Postgres,
shift detection enqueues to the outbox, the worker delivers with signature,
failures retry with backoff and end dead-lettered (never silently lost).
Each test cleans up its own rows — nothing persists.
"""

import uuid

import pytest

from api.env import load_local_env

load_local_env()  # local dev only; production injects env directly

from api.db import get_conn, is_configured
from lumen import webhooks

pytestmark = pytest.mark.skipif(
    not is_configured(), reason="DATABASE_URL not set (Neon not linked)"
)

CALLBACK_URL = "https://example.com/lumen-hook"

BEFORE = {"win_rate": 0.30, "loss_rate": 0.70, "avg_signal": -0.40}
AFTER = {"win_rate": 0.60, "loss_rate": 0.40, "avg_signal": 0.20}
BRIEF = {"warning": None, "pattern": "x", "cross_domain": None,
         "confidence": "10 outcomes recorded.", "raw_outcomes": 10}


def _tenant() -> str:
    return f"wh-test-{uuid.uuid4().hex[:8]}"


def _cleanup_tenant(tenant_id: str) -> None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Deliveries cascade from webhooks.
            cur.execute("DELETE FROM webhooks WHERE tenant_id = %s",
                        (tenant_id,))


def _deliveries_for(webhook_id: str) -> list:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, status, attempts, last_error "
                "FROM webhook_deliveries WHERE webhook_id = %s ORDER BY id",
                (webhook_id,),
            )
            return list(cur.fetchall())


class _FakeResponse:
    def __init__(self, status_code: int = 200):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise IOError(f"HTTP {self.status_code}")


def _no_async(monkeypatch):
    """Disable the background worker; tests drive delivery synchronously."""
    monkeypatch.setattr(webhooks, "_spawn_delivery_worker", lambda: None)


def test_pg_register_list_delete_roundtrip():
    tenant = _tenant()
    try:
        wh = webhooks.register_webhook(tenant, "u1", "pitch", CALLBACK_URL)
        assert wh["id"].startswith("wh_")
        assert wh["fire_count"] == 0

        listed = webhooks.list_webhooks(tenant)
        assert [w["id"] for w in listed] == [wh["id"]]
        assert webhooks.list_webhooks(tenant, domain="post") == []

        assert webhooks.delete_webhook(wh["id"], "wrong-tenant") is False
        assert webhooks.delete_webhook(wh["id"], tenant) is True
        assert webhooks.list_webhooks(tenant) == []
    finally:
        _cleanup_tenant(tenant)


def test_pg_fire_enqueues_and_delivers(monkeypatch):
    """Shift -> outbox row -> signed delivery -> fire_count.

    Proves nothing is lost between detection and delivery.
    """
    _no_async(monkeypatch)
    seen = {}

    def _fake_post(url, data=None, timeout=None,
                   allow_redirects=None, headers=None):
        seen["url"] = url
        seen["headers"] = headers or {}
        return _FakeResponse(200)

    monkeypatch.setattr(webhooks.requests, "post", _fake_post)
    tenant = _tenant()
    try:
        wh = webhooks.register_webhook(tenant, "u1", "pitch", CALLBACK_URL)
        fired = webhooks.check_and_fire_webhooks(
            tenant, "u1", "pitch", BEFORE, AFTER, BRIEF)
        assert fired == 1

        rows = _deliveries_for(wh["id"])
        assert len(rows) == 1 and rows[0]["status"] == "pending"

        stats = webhooks.deliver_due_webhooks()
        assert stats == {"delivered": 1, "failed": 0}
        assert seen["url"] == CALLBACK_URL
        assert seen["headers"].get("X-Lumen-Signature", "").startswith("sha256=")
        assert _deliveries_for(wh["id"])[0]["status"] == "delivered"

        listed = webhooks.list_webhooks(tenant)
        assert listed[0]["fire_count"] == 1
        assert listed[0]["last_fired"] is not None
    finally:
        _cleanup_tenant(tenant)


def test_pg_retry_then_dead_letter(monkeypatch):
    """Persistent failure retries, then dead-letters with the error kept."""
    _no_async(monkeypatch)
    monkeypatch.setattr(webhooks, "_MAX_DELIVERY_ATTEMPTS", 2)
    monkeypatch.setattr(webhooks, "_RETRY_BASE_SECONDS", 0)

    def _boom(url, **kwargs):
        raise ConnectionError("refused")

    monkeypatch.setattr(webhooks.requests, "post", _boom)
    tenant = _tenant()
    try:
        wh = webhooks.register_webhook(tenant, "u1", "pitch", CALLBACK_URL)
        assert webhooks.check_and_fire_webhooks(
            tenant, "u1", "pitch", BEFORE, AFTER, BRIEF) == 1

        first = webhooks.deliver_due_webhooks()
        assert first == {"delivered": 0, "failed": 1}
        rows = _deliveries_for(wh["id"])
        assert rows[0]["status"] == "pending"  # scheduled for retry
        assert rows[0]["attempts"] == 1

        second = webhooks.deliver_due_webhooks()
        assert second == {"delivered": 0, "failed": 1}
        rows = _deliveries_for(wh["id"])
        assert rows[0]["status"] == "failed"  # dead-lettered, not lost
        assert rows[0]["attempts"] == 2
        assert "ConnectionError" in (rows[0]["last_error"] or "")
    finally:
        _cleanup_tenant(tenant)


def test_pg_inactive_webhook_does_not_fire(monkeypatch):
    _no_async(monkeypatch)
    tenant = _tenant()
    try:
        wh = webhooks.register_webhook(tenant, "u1", "pitch", CALLBACK_URL)
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE webhooks SET active = FALSE WHERE id = %s",
                            (wh["id"],))
        assert webhooks.check_and_fire_webhooks(
            tenant, "u1", "pitch", BEFORE, AFTER, BRIEF) == 0
        assert _deliveries_for(wh["id"]) == []
    finally:
        _cleanup_tenant(tenant)


def test_file_fallback_when_pg_unconfigured(tmp_path, monkeypatch):
    """Legacy file store still registers, lists, fires, and deletes."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL_UNPOOLED", raising=False)
    monkeypatch.setattr(webhooks, "WEBHOOKS_FILE",
                        tmp_path / "webhooks.json")
    monkeypatch.setattr(webhooks.requests, "post",
                        lambda url, **kw: _FakeResponse(200))

    wh = webhooks.register_webhook("t-file", "u1", "pitch", CALLBACK_URL)
    assert webhooks.list_webhooks("t-file")[0]["id"] == wh["id"]
    assert webhooks.check_and_fire_webhooks(
        "t-file", "u1", "pitch", BEFORE, AFTER, BRIEF) == 1
    assert webhooks.delete_webhook(wh["id"], "t-file") is True
