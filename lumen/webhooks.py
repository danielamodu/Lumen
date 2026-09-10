"""Webhook system for Lumen pattern shift notifications."""

import json
import logging
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import requests

from api import db as _db

WEBHOOKS_FILE = Path.home() / ".sibyl-memory" / "webhooks.json"

# Delivery policy: attempts, then dead-letter. Tests monkeypatch these small.
_MAX_DELIVERY_ATTEMPTS = 5
_RETRY_BASE_SECONDS = 60
_RETRY_MAX_SECONDS = 3600
# A worker that claimed a row but died releases it after this lease expires.
_DELIVERY_LEASE_SECONDS = 300
_DELIVERY_BATCH_LIMIT = 10

# Set once we warn about file fallback so concurrent requests don't spam logs.
_pg_fallback_warned = False


def _warn_fallback(reason: str) -> None:
    """Log file-fallback once per process (keeps request logs readable)."""
    global _pg_fallback_warned
    if not _pg_fallback_warned:
        _pg_fallback_warned = True
        logging.getLogger("lumen.webhooks").warning(
            "webhooks: %s. Using file fallback (transitional).", reason
        )


def _load_webhooks() -> dict:
    """Load webhooks from JSON file."""
    if not WEBHOOKS_FILE.exists():
        return {}
    try:
        with open(WEBHOOKS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_webhooks(webhooks: dict) -> None:
    """Save webhooks to JSON file."""
    WEBHOOKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(WEBHOOKS_FILE, "w") as f:
        json.dump(webhooks, f, indent=2)


from api.security import validate_callback_url, sign_webhook_payload


def register_webhook(
    tenant_id: str,
    user_id: str,
    domain: str,
    callback_url: str,
    threshold: float = 0.10
) -> dict:
    """Register a webhook for pattern shift notifications with SSRF validation.

    Returns the webhook record including its ID.
    Postgres primary, file fallback (transitional).
    """
    # SSRF Protection: validate URL scheme and block private/loopback/cloud metadata IPs
    validated_url = validate_callback_url(callback_url)

    webhook_id = "wh_" + secrets.token_hex(8)
    webhook = {
        "id": webhook_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "domain": domain,
        "callback_url": validated_url,
        "threshold": threshold,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
        "last_fired": None,
        "fire_count": 0
    }

    if _db.is_configured():
        try:
            _pg_insert_webhook(webhook)
            return webhook
        except Exception as exc:
            _warn_fallback(f"Postgres insert failed ({type(exc).__name__})")
    else:
        _warn_fallback("DATABASE_URL not set")

    webhooks = _load_webhooks()
    webhooks[webhook_id] = webhook
    _save_webhooks(webhooks)

    return webhook


def delete_webhook(webhook_id: str, tenant_id: str) -> bool:
    """Delete a webhook. Returns True if deleted,
    False if not found (or not owned by this tenant).

    Postgres primary, file fallback (transitional).
    """
    if _db.is_configured():
        try:
            return _pg_delete_webhook(webhook_id, tenant_id)
        except Exception as exc:
            _warn_fallback(f"Postgres delete failed ({type(exc).__name__})")
    else:
        _warn_fallback("DATABASE_URL not set")

    webhooks = _load_webhooks()

    if webhook_id not in webhooks:
        return False

    # Ensure tenant owns this webhook (Row-level access lock)
    if webhooks[webhook_id].get("tenant_id") != tenant_id:
        return False

    del webhooks[webhook_id]
    _save_webhooks(webhooks)
    return True


def list_webhooks(tenant_id: str, user_id: str = None,
                  domain: str = None) -> list:
    """List webhooks for a tenant, strictly isolated to tenant.

    Postgres primary, file fallback (transitional).
    """
    if _db.is_configured():
        try:
            return _pg_list_webhooks(tenant_id, user_id, domain)
        except Exception as exc:
            _warn_fallback(f"Postgres list failed ({type(exc).__name__})")
    else:
        _warn_fallback("DATABASE_URL not set")

    webhooks = _load_webhooks()
    result = []

    for wh in webhooks.values():
        if wh.get("tenant_id") != tenant_id:
            continue
        if user_id and wh.get("user_id") != user_id:
            continue
        if domain and wh.get("domain") != domain:
            continue
        result.append(wh)

    return result


# ---------------------------------------------------------------------------
# Postgres primary (Neon). Delivery rows form an outbox: check_and_fire
# ENQUEUES, deliver_due_webhooks() delivers with retries, and failures end as
# dead-lettered rows instead of silent thread deaths.
# ---------------------------------------------------------------------------

def _row_to_webhook(row: dict) -> dict:
    created = row.get("created_at")
    last_fired = row.get("last_fired")
    return {
        "id": row["id"],
        "tenant_id": row["tenant_id"],
        "user_id": row["user_id"],
        "domain": row["domain"],
        "callback_url": row["callback_url"],
        "threshold": float(row.get("threshold", 0.10)),
        "created_at": created.isoformat() if created else None,
        "active": row.get("active", True),
        "last_fired": last_fired.isoformat() if last_fired else None,
        "fire_count": row.get("fire_count", 0),
    }


def _pg_insert_webhook(webhook: dict) -> None:
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO webhooks (id, tenant_id, user_id, domain, "
                "callback_url, threshold, active, fire_count) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    webhook["id"], webhook["tenant_id"], webhook["user_id"],
                    webhook["domain"], webhook["callback_url"],
                    webhook["threshold"], webhook["active"],
                    webhook["fire_count"],
                ),
            )


def _pg_delete_webhook(webhook_id: str, tenant_id: str) -> bool:
    """Delete only if owned by the tenant. Deliveries cascade."""
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM webhooks WHERE id = %s AND tenant_id = %s",
                (webhook_id, tenant_id),
            )
            return cur.rowcount == 1


def _pg_list_webhooks(tenant_id: str, user_id: str = None,
                      domain: str = None) -> list:
    query = ("SELECT id, tenant_id, user_id, domain, callback_url, "
             "threshold, created_at, active, last_fired, fire_count "
             "FROM webhooks WHERE tenant_id = %s")
    params: list = [tenant_id]
    if user_id:
        query += " AND user_id = %s"
        params.append(user_id)
    if domain:
        query += " AND domain = %s"
        params.append(domain)
    query += " ORDER BY created_at"
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [_row_to_webhook(r) for r in cur.fetchall()]


def _pg_enqueue_delivery(webhook_id: str, payload: dict) -> None:
    from psycopg.types.json import Json
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO webhook_deliveries (webhook_id, payload) "
                "VALUES (%s, %s)",
                (webhook_id, Json(payload)),
            )
            cur.execute(
                "UPDATE webhooks SET last_fired = now(), "
                "fire_count = fire_count + 1 WHERE id = %s",
                (webhook_id,),
            )


def _retry_delay_seconds(attempts: int) -> int:
    """Exponential backoff after `attempts` failures (1-based), capped."""
    delay = _RETRY_BASE_SECONDS * (2 ** max(0, attempts - 1))
    return min(delay, _RETRY_MAX_SECONDS)


def deliver_due_webhooks(limit: int = _DELIVERY_BATCH_LIMIT) -> dict:
    """Deliver due outbox rows. Returns {"delivered": n, "failed": n}.

    Safe for concurrent workers: claiming uses FOR UPDATE SKIP LOCKED, and
    rows orphaned by a crashed worker (stale 'delivering' lease) are reaped.
    Exhausted rows become status='failed' (dead-letter), never silent loss.
    """
    stats = {"delivered": 0, "failed": 0}
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            # Reap orphaned claims whose lease expired.
            cur.execute(
                "UPDATE webhook_deliveries SET status = 'pending' "
                "WHERE status = 'delivering' "
                "AND next_retry_at < now() - make_interval(secs => %s)",
                (_DELIVERY_LEASE_SECONDS,),
            )
            # Claim due rows atomically.
            cur.execute(
                "UPDATE webhook_deliveries SET status = 'delivering', "
                "next_retry_at = now() + make_interval(secs => %s) "
                "WHERE id IN (SELECT id FROM webhook_deliveries "
                "WHERE status = 'pending' AND next_retry_at <= now() "
                "ORDER BY next_retry_at LIMIT %s FOR UPDATE SKIP LOCKED) "
                "RETURNING id, webhook_id, payload, attempts",
                (_DELIVERY_LEASE_SECONDS, limit),
            )
            claimed = cur.fetchall()
    for row in claimed:
        payload = row["payload"]
        if isinstance(payload, str):
            payload = json.loads(payload)
        try:
            callback_url = _delivery_callback_url(row["webhook_id"])
            _post_delivery(callback_url, payload)
        except Exception as exc:
            _pg_settle_delivery(row["id"], row["attempts"], ok=False,
                                error=f"{type(exc).__name__}: {exc}"[:500])
            stats["failed"] += 1
        else:
            _pg_settle_delivery(row["id"], row["attempts"], ok=True)
            stats["delivered"] += 1
    return stats


def _delivery_callback_url(webhook_id: str) -> str:
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT callback_url FROM webhooks WHERE id = %s",
                (webhook_id,),
            )
            row = cur.fetchone()
    if row is None:
        raise ValueError(f"Webhook {webhook_id} no longer exists")
    return row["callback_url"]


def _pg_settle_delivery(delivery_id: int, attempts: int, ok: bool,
                        error: Optional[str] = None) -> None:
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            if ok:
                cur.execute(
                    "UPDATE webhook_deliveries SET status = 'delivered' "
                    "WHERE id = %s",
                    (delivery_id,),
                )
            else:
                used = attempts + 1
                if used >= _MAX_DELIVERY_ATTEMPTS:
                    cur.execute(
                        "UPDATE webhook_deliveries SET status = 'failed', "
                        "attempts = %s, last_error = %s WHERE id = %s",
                        (used, error, delivery_id),
                    )
                else:
                    cur.execute(
                        "UPDATE webhook_deliveries SET status = 'pending', "
                        "attempts = %s, last_error = %s, "
                        "next_retry_at = now() + make_interval(secs => %s) "
                        "WHERE id = %s",
                        (used, error,
                         _retry_delay_seconds(used), delivery_id),
                    )


def _spawn_delivery_worker() -> None:
    """Fire the outbox worker in a background thread (non-blocking record())."""
    thread = threading.Thread(
        target=_delivery_worker_entrypoint,
        daemon=True,
    )
    thread.start()


def _delivery_worker_entrypoint() -> None:
    try:
        deliver_due_webhooks()
    except Exception as exc:
        # Non-fatal: rows stay pending for the next worker pass.
        print(f"Webhook delivery worker error: {type(exc).__name__}")


def check_and_fire_webhooks(
    tenant_id: str,
    user_id: str,
    domain: str,
    pattern_before: dict,
    pattern_after: dict,
    current_brief: dict
) -> int:
    """Check if pattern shifted enough to fire webhooks.
    
    Returns number of webhooks fired.
    
    pattern_before and pattern_after are WARM pattern 
    entity body dicts with win_rate, loss_rate, avg_signal.
    """
    if not pattern_before or not pattern_after:
        return 0
    
    win_before = pattern_before.get("win_rate", 0.0)
    win_after = pattern_after.get("win_rate", 0.0)
    loss_before = pattern_before.get("loss_rate", 0.0)
    loss_after = pattern_after.get("loss_rate", 0.0)
    avg_before = pattern_before.get("avg_signal", 0.0)
    avg_after = pattern_after.get("avg_signal", 0.0)
    
    win_shift = abs(win_after - win_before)
    loss_shift = abs(loss_after - loss_before)
    crossed_zero = (
        (avg_before <= 0 and avg_after > 0) or
        (avg_before >= 0 and avg_after < 0)
    )
    
    shift = {
        "win_rate_before": win_before,
        "win_rate_after": win_after,
        "loss_rate_before": loss_before,
        "loss_rate_after": loss_after,
        "avg_signal_before": avg_before,
        "avg_signal_after": avg_after,
        "crossed_zero": crossed_zero
    }
    
    webhooks = _matching_webhooks(tenant_id, user_id, domain)
    fired = 0

    for webhook_id, wh in webhooks:
        threshold = wh.get("threshold", 0.10)
        should_fire = (
            win_shift >= threshold or
            loss_shift >= threshold or
            crossed_zero
        )

        if not should_fire:
            continue

        payload = {
            "event": "pattern_shift",
            "user_id": user_id,
            "domain": domain,
            "tenant_id": tenant_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "shift": shift,
            "current_brief": current_brief
        }

        _fire_one(webhook_id, wh, payload)
        fired += 1

    return fired


def _matching_webhooks(tenant_id: str, user_id: str,
                       domain: str) -> list:
    """Active webhooks for this tenant/user/domain as (id, record) pairs.

    Postgres primary, file fallback (transitional).
    """
    if _db.is_configured():
        try:
            rows = _pg_list_webhooks(tenant_id, user_id, domain)
            return [(r["id"], r) for r in rows if r.get("active", True)]
        except Exception as exc:
            _warn_fallback(f"Postgres match failed ({type(exc).__name__})")
    else:
        _warn_fallback("DATABASE_URL not set")
    webhooks = _load_webhooks()
    matched = []
    for webhook_id, wh in webhooks.items():
        if not wh.get("active", True):
            continue
        if wh.get("tenant_id") != tenant_id:
            continue
        if wh.get("user_id") != user_id:
            continue
        if wh.get("domain") != domain:
            continue
        matched.append((webhook_id, wh))
    return matched


def _fire_one(webhook_id: str, wh: dict, payload: dict) -> None:
    """Enqueue (Postgres) or thread-fire (file fallback) one delivery."""
    if _db.is_configured():
        try:
            _pg_enqueue_delivery(webhook_id, payload)
            # Deliver in background — don't block the record() call.
            _spawn_delivery_worker()
            return
        except Exception as exc:
            _warn_fallback(f"Postgres enqueue failed ({type(exc).__name__})")
    # File fallback: legacy fire-and-forget thread.
    thread = threading.Thread(
        target=_fire_webhook,
        args=(webhook_id, wh["callback_url"], payload),
        daemon=True
    )
    thread.start()


def _post_delivery(callback_url: str, payload: dict) -> None:
    """POST one delivery with HMAC-SHA256 signature. Raises on failure."""
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    signature = sign_webhook_payload(payload_bytes)
    # allow_redirects=False: the callback URL is SSRF-validated at
    # registration, but following a 30x here would let it redirect into the
    # internal network / cloud metadata, bypassing that check.
    response = requests.post(
        callback_url,
        data=payload_bytes,
        timeout=10,
        allow_redirects=False,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "lumen-webhooks/0.1.0",
            "X-Lumen-Event": "pattern_shift",
            "X-Lumen-Signature": signature
        }
    )
    response.raise_for_status()


def _fire_webhook(webhook_id: str,
                  callback_url: str,
                  payload: dict) -> None:
    """Fire a single webhook. Legacy file-fallback path (background thread)."""
    try:
        _post_delivery(callback_url, payload)
        # Update fire metadata (file store only; pg path does it on enqueue).
        webhooks = _load_webhooks()
        wh = webhooks.get(webhook_id)
        if wh is not None:
            wh["last_fired"] = datetime.now(timezone.utc).isoformat()
            wh["fire_count"] = wh.get("fire_count", 0) + 1
            _save_webhooks(webhooks)
    except Exception as exc:
        # Non-fatal: log without leaking credentials
        print(f"Webhook {webhook_id} delivery error: {type(exc).__name__}")

