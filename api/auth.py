"""API key authentication for Lumen multi-tenant routing with cryptographic security."""

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import Header, HTTPException
from fastapi.security import APIKeyHeader

from api.security import hash_api_key, secure_compare, validate_user_identifier

# DEMO_KEY is an intentionally public, shared demo credential (documented in
# the README). It grants access only to the isolated "demo" tenant.
DEMO_KEY = os.environ.get("LUMEN_DEMO_KEY", "lmn_demo0000000000000000000000000000")

# ADMIN_KEY can mint tenants, so it must never be hardcoded in source. It is
# read from the environment only. If unset, admin endpoints are disabled.
ADMIN_KEY = os.environ.get("LUMEN_ADMIN_KEY")

TENANTS_FILE = Path.home() / ".sibyl-memory" / "tenants.json"

api_key_header = APIKeyHeader(name="X-Lumen-Key", auto_error=False)


def _load_tenants() -> dict:
    """Load tenants from JSON file. Returns empty dict if file doesn't exist."""
    if not TENANTS_FILE.exists():
        return {}
    try:
        with open(TENANTS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_tenants(tenants: dict) -> None:
    """Save tenants securely to JSON file."""
    TENANTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TENANTS_FILE, "w") as f:
        json.dump(tenants, f, indent=2)


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
    
    # Check tenant store via SHA-256 hash
    hashed_key = hash_api_key(api_key)
    tenants = _load_tenants()
    
    # Check hashed key first, fallback to raw key with auto-migration
    tenant = tenants.get(hashed_key)
    if not tenant and api_key in tenants:
        # Legacy raw key found: auto-migrate to hashed key
        tenant = tenants.pop(api_key)
        tenants[hashed_key] = tenant
        _save_tenants(tenants)
    
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
    
    # Store hashed key in tenants.json so raw secret is never stored at rest
    hashed_key = hash_api_key(api_key)
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

