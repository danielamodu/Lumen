"""API key authentication for Lumen multi-tenant routing with cryptographic security."""

import hashlib
import hmac
import json
import logging
import os
import secrets
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import Header, HTTPException
from fastapi.security import APIKeyHeader

from api.security import hash_api_key, secure_compare, validate_user_identifier
from api import db as _db

# DEMO_KEY is an intentionally public, shared demo credential (documented in
# the README). It grants access only to the isolated "demo" tenant.
DEMO_KEY = os.environ.get("LUMEN_DEMO_KEY", "lmn_demo0000000000000000000000000000")

# ADMIN_KEY can mint tenants, so it must never be hardcoded in source. It is
# read from the environment only. If unset, admin endpoints are disabled.
ADMIN_KEY = os.environ.get("LUMEN_ADMIN_KEY")

TENANTS_FILE = Path.home() / ".sibyl-memory" / "tenants.json"

# Guards read-modify-write of the tenants file so concurrent create/migrate
# operations (FastAPI runs sync handlers in a threadpool) can't lose updates
# or interleave into a corrupt file. Only used by the file fallback path.
_tenants_lock = threading.Lock()

# Set once we warn about file fallback so concurrent requests don't spam logs.
_pg_fallback_warned = False

api_key_header = APIKeyHeader(name="X-Lumen-Key", auto_error=False)


def _warn_fallback(reason: str) -> None:
    """Log file-fallback once per process (keeps request logs readable)."""
    global _pg_fallback_warned
    if not _pg_fallback_warned:
        _pg_fallback_warned = True
        logging.getLogger("lumen.auth").warning(
            "Tenants: %s. Using file fallback (transitional).", reason
        )


def _load_tenants() -> dict:
    """Load tenants from JSON file. Returns empty dict if file doesn't exist."""
    if not TENANTS_FILE.exists():
        return {}
    try:
        with open(TENANTS_FILE, "r") as f:
            return json.load(f)
    except Exception as exc:
        # Never silently treat a corrupt file as "no tenants" without a trace —
        # that would 401 every existing tenant. Log loudly so it's diagnosable.
        logging.getLogger("lumen.auth").error(
            "Failed to read tenants file %s: %s", TENANTS_FILE, exc
        )
        return {}


def _save_tenants(tenants: dict) -> None:
    """Save tenants securely to JSON file (atomic write to avoid corruption)."""
    TENANTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = TENANTS_FILE.with_name(TENANTS_FILE.name + ".tmp")
    with open(tmp, "w") as f:
        json.dump(tenants, f, indent=2)
    tmp.replace(TENANTS_FILE)


# ---------------------------------------------------------------------------
# Postgres primary (Neon). The file store below stays as transitional fallback.
# ---------------------------------------------------------------------------

def _pg_lookup(hashed_key: str) -> Optional[dict]:
    """Fetch one tenant row by hashed key. Returns None if unknown."""
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT tenant_id, name, active FROM tenants WHERE key_hash = %s",
                (hashed_key,),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return {
        "tenant_id": row["tenant_id"],
        "name": row["name"],
        "active": row["active"],
    }


def _pg_insert(hashed_key: str, tenant_info: dict) -> None:
    """Insert a tenant row. Raises on duplicate key (caller decides)."""
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tenants (key_hash, tenant_id, name, active) "
                "VALUES (%s, %s, %s, %s)",
                (
                    hashed_key,
                    tenant_info["tenant_id"],
                    tenant_info["name"],
                    tenant_info.get("active", True),
                ),
            )


def _resolve_pg(api_key: str, hashed_key: str) -> dict:
    """Resolve via Postgres. Raises HTTPException 401 if invalid/inactive.

    Only connection/SQL errors propagate as non-HTTP exceptions (which the
    caller turns into file fallback); auth failures always raise 401.
    """
    tenant = _pg_lookup(hashed_key)
    if not tenant:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    if not tenant.get("active", True):
        raise HTTPException(status_code=401, detail="API key is inactive.")
    return {
        "tenant_id": tenant["tenant_id"],
        "name": tenant["name"],
        "active": tenant.get("active", True),
        "is_admin": False,
    }


def _resolve_file(api_key: str, hashed_key: str) -> dict:
    """Resolve via the legacy JSON file (transitional fallback)."""
    tenants = _load_tenants()

    # Check hashed key first, fallback to raw key with auto-migration
    tenant = tenants.get(hashed_key)
    if not tenant and api_key in tenants:
        # Legacy raw key found: auto-migrate to hashed key under the lock, and
        # re-read inside it so a concurrent create/migrate can't be lost or
        # corrupt the file.
        with _tenants_lock:
            tenants = _load_tenants()
            if api_key in tenants:
                tenant = tenants.pop(api_key)
                tenants[hashed_key] = tenant
                _save_tenants(tenants)
            else:
                tenant = tenants.get(hashed_key)

    if not tenant:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key."
        )
    if not tenant.get("active", True):
        raise HTTPException(
            status_code=401,
            detail="API key is inactive."
        )

    return {
        "tenant_id": tenant["tenant_id"],
        "name": tenant["name"],
        "active": tenant.get("active", True),
        "is_admin": False
    }


def resolve_tenant(api_key: Optional[str]) -> dict:
    """Resolve an API key to tenant info using constant-time verification.
    
    Returns dict with tenant_id, name, active, is_admin.
    Raises HTTPException 401 if key is invalid or inactive.
    """
    if not api_key or not isinstance(api_key, str):
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Pass X-Lumen-Key header."
        )
    
    # Constant-time comparison for standard keys
    if secure_compare(api_key, DEMO_KEY):
        return {
            "tenant_id": "demo",
            "name": "Demo Tenant",
            "active": True,
            "is_admin": False
        }
    if ADMIN_KEY and secure_compare(api_key, ADMIN_KEY):
        return {
            "tenant_id": "admin",
            "name": "Admin",
            "active": True,
            "is_admin": True
        }
    
    # Check tenant store via SHA-256 hash — Postgres primary, file fallback.
    hashed_key = hash_api_key(api_key)
    if _db.is_configured():
        try:
            return _resolve_pg(api_key, hashed_key)
        except HTTPException:
            raise
        except Exception as exc:
            _warn_fallback(
                f"Postgres lookup failed ({type(exc).__name__})"
            )
    else:
        _warn_fallback("DATABASE_URL not set")
    return _resolve_file(api_key, hashed_key)


def require_admin(api_key: Optional[str]) -> dict:
    """Like resolve_tenant but requires admin key."""
    tenant = resolve_tenant(api_key)
    if not tenant.get("is_admin"):
        raise HTTPException(
            status_code=403,
            detail="Admin key required for this endpoint."
        )
    return tenant


def create_tenant(name: str) -> tuple[str, dict]:
    """Create a new tenant with hashed key storage. Returns (api_key, tenant_info)."""
    api_key = "lmn_" + secrets.token_hex(16)
    tenant_id = "tenant_" + secrets.token_hex(6)
    tenant_info = {
        "tenant_id": tenant_id,
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True
    }
    
    # Store hashed key so raw secret is never stored at rest.
    # Postgres primary, file fallback (transitional).
    hashed_key = hash_api_key(api_key)
    if _db.is_configured():
        try:
            _pg_insert(hashed_key, tenant_info)
            return api_key, tenant_info
        except Exception as exc:
            _warn_fallback(
                f"Postgres insert failed ({type(exc).__name__})"
            )
    else:
        _warn_fallback("DATABASE_URL not set")
    with _tenants_lock:
        tenants = _load_tenants()
        tenants[hashed_key] = tenant_info
        _save_tenants(tenants)

    return api_key, tenant_info


def scope_user_id(tenant_id: str, user_id: str) -> str:
    """Prepend tenant_id to user_id for strict row-level memory isolation.
    
    Sanitizes user_id to prevent colon injection and tenant prefix spoofing:
    "alex" → "demo:alex" for demo tenant
    "tenant_1:alex" → "demo:tenant_1_alex" (colon sanitized, preventing bypass)
    """
    # Sanitize user_id by replacing colons to prevent IDOR prefix spoofing
    sanitized_user = user_id.replace(":", "_").strip() if user_id else "default"
    return f"{tenant_id}:{sanitized_user}"

