"""Webhook system for Lumen pattern shift notifications."""

import json
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
import requests

WEBHOOKS_FILE = Path.home() / ".sibyl-memory" / "webhooks.json"


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


def register_webhook(
    tenant_id: str,
    user_id: str,
    domain: str,
    callback_url: str,
    threshold: float = 0.10
) -> dict:
    """Register a webhook for pattern shift notifications.
    
    Returns the webhook record including its ID.
    """
    webhook_id = "wh_" + secrets.token_hex(8)
    webhook = {
        "id": webhook_id,
        "tenant_id": tenant_id,
        "user_id": user_id,
        "domain": domain,
        "callback_url": callback_url,
        "threshold": threshold,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
        "last_fired": None,
        "fire_count": 0
    }
    
    webhooks = _load_webhooks()
    webhooks[webhook_id] = webhook
    _save_webhooks(webhooks)
    
    return webhook


def delete_webhook(webhook_id: str, tenant_id: str) -> bool:
    """Delete a webhook. Returns True if deleted, 
    False if not found."""
    webhooks = _load_webhooks()
    
    if webhook_id not in webhooks:
        return False
    
    # Ensure tenant owns this webhook
    if webhooks[webhook_id].get("tenant_id") != tenant_id:
        return False
    
    del webhooks[webhook_id]
    _save_webhooks(webhooks)
    return True


def list_webhooks(tenant_id: str, user_id: str = None,
                  domain: str = None) -> list:
    """List webhooks for a tenant, optionally filtered."""
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
    
    webhooks = _load_webhooks()
    fired = 0
    
    for webhook_id, wh in webhooks.items():
        if not wh.get("active", True):
            continue
        if wh.get("tenant_id") != tenant_id:
            continue
        if wh.get("user_id") != user_id:
            continue
        if wh.get("domain") != domain:
            continue
        
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
        
        # Fire in background thread — don't block the 
        # record() call
        thread = threading.Thread(
            target=_fire_webhook,
            args=(webhook_id, wh["callback_url"], payload),
            daemon=True
        )
        thread.start()
        fired += 1
        
        # Update fire metadata
        wh["last_fired"] = datetime.now(timezone.utc).isoformat()
        wh["fire_count"] = wh.get("fire_count", 0) + 1
    
    if fired > 0:
        _save_webhooks(webhooks)
    
    return fired


def _fire_webhook(webhook_id: str, 
                  callback_url: str, 
                  payload: dict) -> None:
    """Fire a single webhook. Runs in background thread."""
    try:
        response = requests.post(
            callback_url,
            json=payload,
            timeout=10,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "lumen-webhooks/0.1.0",
                "X-Lumen-Event": "pattern_shift"
            }
        )
        response.raise_for_status()
    except Exception as exc:
        # Log but don't crash — webhook failures are 
        # non-fatal
        print(f"Webhook {webhook_id} failed: {exc}")
