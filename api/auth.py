"""API key authentication for Lumen multi-tenant routing."""

import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastapi import Header, HTTPException
from fastapi.security import APIKeyHeader

DEMO_KEY = "lmn_demo0000000000000000000000000000"
ADMIN_KEY = "lmn_admin000000000000000000000000000"

TENANTS_FILE = Path.home() / ".sibyl-memory" / "tenants.json"

api_key_header = APIKeyHeader(name="X-Lumen-Key", auto_error=False)


def _load_tenants() -> dict:
    """Load tenants from JSON file. Returns empty dict if file doesn't exist."""
    if not TENANTS_FILE.exists():
        return {}
    with open(TENANTS_FILE, "r") as f:
        return json.load(f)


def _save_tenants(tenants: dict) -> None:
    """Save tenants to JSON file."""
    TENANTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TENANTS_FILE, "w") as f:
        json.dump(tenants, f, indent=2)


def resolve_tenant(api_key: Optional[str]) -> dict:
    """Resolve an API key to tenant info.
    
    Returns dict with tenant_id, name, active.
    Raises HTTPException 401 if key is invalid or inactive.
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Pass X-Lumen-Key header."
        )
    
    # Check hardcoded keys first
    if api_key == DEMO_KEY:
        return {
            "tenant_id": "demo",
            "name": "Demo Tenant",
            "active": True,
            "is_admin": False
        }
    if api_key == ADMIN_KEY:
        return {
            "tenant_id": "admin", 
            "name": "Admin",
            "active": True,
            "is_admin": True
        }
    
    # Check tenant store
    tenants = _load_tenants()
    tenant = tenants.get(api_key)
    
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
    
    return {**tenant, "is_admin": False}


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
    """Create a new tenant. Returns (api_key, tenant_info)."""
    api_key = "lmn_" + secrets.token_hex(16)
    tenant_id = "tenant_" + secrets.token_hex(6)
    tenant_info = {
        "tenant_id": tenant_id,
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "active": True
    }
    
    tenants = _load_tenants()
    tenants[api_key] = tenant_info
    _save_tenants(tenants)
    
    return api_key, tenant_info


def scope_user_id(tenant_id: str, user_id: str) -> str:
    """Prepend tenant_id to user_id for Sibyl memory isolation.
    
    "alex" → "demo:alex" for demo tenant
    "alex" → "tenant_abc123:alex" for real tenant
    """
    return f"{tenant_id}:{user_id}"
