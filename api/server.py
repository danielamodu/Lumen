"""FastAPI server for Lumen outcome memory layer."""

import glob
import os
import sys
from pathlib import Path
from typing import Optional

# Ensure repository root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, Security, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import uvicorn

from lumen.core import record, brief
from lumen.memory import get_client
from lumen.webhooks import (
    register_webhook, delete_webhook, 
    list_webhooks, check_and_fire_webhooks
)
from lumen.market import get_aggregate_patterns
from demo.seed import seed_outcomes

DEMO_PAYMENT_PROOF = "demo_payment_proof_base_usdc"
LUMEN_WALLET = "0x0000000000000000000000000000000000000000"
MARKET_PRICE_USDC = "0.01"
from api.auth import (
    resolve_tenant,
    require_admin,
    create_tenant,
    scope_user_id,
    DEMO_KEY,
    ADMIN_KEY,
    api_key_header,
)

app = FastAPI(title="Lumen API", description="Outcome memory layer for AI agents")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BriefRequest(BaseModel):
    user_id: str = "alex"
    domain: str = "pitch"
    context: str = ""

    @field_validator("domain")
    @classmethod
    def normalize_domain(cls, v):
        if not v or not v.strip():
            raise ValueError("Domain must be a non-empty string.")
        return v.strip().lower()


class RecordRequest(BaseModel):
    user_id: str
    domain: str
    action: str
    outcome: str
    signal: int


class WebhookCreateRequest(BaseModel):
    user_id: str
    domain: str
    callback_url: str
    threshold: float = 0.10

    @field_validator("threshold")
    @classmethod
    def validate_threshold(cls, v):
        if not 0.01 <= v <= 1.0:
            raise ValueError(
                "Threshold must be between 0.01 and 1.0"
            )
        return v

    @field_validator("domain")
    @classmethod
    def normalize_domain(cls, v):
        if not v or not v.strip():
            raise ValueError("Domain must be a non-empty string.")
        return v.strip().lower()


class MarketBriefRequest(BaseModel):
    domain: str
    context: str = ""

    @field_validator("domain")
    @classmethod
    def normalize_domain(cls, v):
        if not v or not v.strip():
            raise ValueError(
                "Domain must be a non-empty string."
            )
        return v.strip().lower()


class DemoStepRequest(BaseModel):
    step: int = Field(..., ge=1, le=5)


class CreateTenantRequest(BaseModel):
    name: str


def _wipe_internal():
    """Wipe the Sibyl SQLite memory database cleanly."""
    db_path = os.path.normpath(os.path.expanduser("~/.sibyl-memory/lumen_demo.db"))
    client = get_client()
    if client is not None and hasattr(client, "_storage") and hasattr(client._storage, "close"):
        try:
            client._storage.close()
        except Exception:
            pass

    for f in glob.glob(db_path + "*"):
        try:
            os.remove(f)
        except OSError:
            pass

    get_client(path=db_path)


@app.post("/brief")
def get_brief(
    req: BriefRequest,
    api_key: str = Security(api_key_header),
):
    """Retrieve the session briefing for a user and domain."""
    tenant = resolve_tenant(api_key)
    scoped_user = scope_user_id(tenant["tenant_id"], req.user_id)
    try:
        res = brief(scoped_user, req.domain, req.context)
        return res
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/record")
def record_outcome(
    req: RecordRequest,
    api_key: str = Security(api_key_header),
):
    """Record a single interaction outcome to Sibyl memory and recalculate patterns."""
    tenant = resolve_tenant(api_key)
    scoped_user = scope_user_id(tenant["tenant_id"], req.user_id)
    try:
        record(
            scoped_user,
            req.domain,
            req.action,
            req.outcome,
            req.signal,
            tenant_id=tenant["tenant_id"]
        )
        return {"status": "ok", "message": "Outcome recorded."}
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/webhooks")
def create_webhook(
    req: WebhookCreateRequest,
    api_key: str = Security(api_key_header)
):
    """Register a webhook for pattern shift notifications."""
    tenant = resolve_tenant(api_key)
    scoped_user = scope_user_id(
        tenant["tenant_id"], req.user_id
    )
    webhook = register_webhook(
        tenant_id=tenant["tenant_id"],
        user_id=scoped_user,
        domain=req.domain,
        callback_url=req.callback_url,
        threshold=req.threshold
    )
    return webhook


@app.get("/webhooks")
def get_webhooks(
    user_id: str = "alex",
    domain: str = None,
    api_key: str = Security(api_key_header)
):
    """List webhooks for the current tenant."""
    tenant = resolve_tenant(api_key)
    scoped_user = scope_user_id(
        tenant["tenant_id"], user_id
    )
    webhooks = list_webhooks(
        tenant_id=tenant["tenant_id"],
        user_id=scoped_user,
        domain=domain
    )
    return {"webhooks": webhooks, "count": len(webhooks)}


@app.delete("/webhooks/{webhook_id}")
def remove_webhook(
    webhook_id: str,
    api_key: str = Security(api_key_header)
):
    """Delete a webhook."""
    tenant = resolve_tenant(api_key)
    deleted = delete_webhook(webhook_id, tenant["tenant_id"])
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Webhook not found or access denied."
        )
    return {"status": "ok", 
            "message": f"Webhook {webhook_id} deleted."}


@app.post("/wipe")
def wipe_memory(api_key: str = Security(api_key_header)):
    """Wipe all memory stored in the database."""
    tenant = resolve_tenant(api_key)
    if tenant["tenant_id"] not in ("demo", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Wipe/seed only available for demo tenant.",
        )
    try:
        _wipe_internal()
        return {"status": "ok", "message": "Memory wiped."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/seed")
def seed_memory(api_key: str = Security(api_key_header)):
    """Seed 33 realistic outcomes across all domains."""
    tenant = resolve_tenant(api_key)
    if tenant["tenant_id"] not in ("demo", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Wipe/seed only available for demo tenant.",
        )
    try:
        _wipe_internal()
        scoped_user = scope_user_id(tenant["tenant_id"], "alex")
        seed_outcomes(scoped_user)
        return {"status": "ok", "message": "Memory seeded."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/demo/step")
def run_demo_step(
    req: DemoStepRequest,
    api_key: str = Security(api_key_header),
):
    """Execute a single step in the 5-step interactive demonstration sequence."""
    tenant = resolve_tenant(api_key)
    if tenant["tenant_id"] not in ("demo", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Wipe/seed only available for demo tenant.",
        )

    user_id = scope_user_id(tenant["tenant_id"], "alex")
    domain = "pitch"
    demo_context = "pitching an AI infrastructure fund on agent memory"

    try:
        if req.step == 1:
            # Step 1: seed + return Session 1 brief
            _wipe_internal()
            seed_outcomes(user_id)
            brief_dict = brief(user_id, domain, demo_context)
            step_label = "Session 1 — Memory loaded from Sibyl"
            action_taken = "Seeded 33 outcomes into Sibyl memory"

        elif req.step == 2:
            # Step 2: record loss (product demo, ghosted) + return Session 2 brief
            record(
                user_id,
                domain,
                "opened with product architecture diagram",
                "no reply after 7 days",
                -1,
            )
            brief_dict = brief(user_id, domain, demo_context)
            step_label = "Session 2 — Loss recorded, warning intensified"
            action_taken = "Recorded loss (-1) with product demo"

        elif req.step == 3:
            # Step 3: record win (led with problem, got meeting) + return Session 3 brief
            record(
                user_id,
                domain,
                "opened with the problem — agents forget everything",
                "got a meeting booked same day",
                1,
            )
            brief_dict = brief(user_id, domain, demo_context)
            step_label = "Session 3 — Contradicting win recorded, pattern shifted"
            action_taken = "Recorded win (+1) with problem-first approach"

        elif req.step == 4:
            # Step 4: wipe memory + return empty brief
            _wipe_internal()
            brief_dict = brief(user_id, domain, demo_context)
            step_label = "Session 4 — Memory wiped (The Delete Test)"
            action_taken = "Wiped all outcomes. brief() returns empty state."

        elif req.step == 5:
            # Step 5: reset + seed + return baseline
            _wipe_internal()
            seed_outcomes(user_id)
            brief_dict = brief(user_id, domain, demo_context)
            step_label = "Session 5 — Baseline re-seeded"
            action_taken = "Restored 33 baseline outcomes into memory"

        return {
            "step": req.step,
            "step_label": step_label,
            "action_taken": action_taken,
            "brief": brief_dict,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/tenants/create")
def create_tenant_endpoint(
    req: CreateTenantRequest,
    api_key: str = Security(api_key_header),
):
    """Create a new tenant with dedicated API key."""
    require_admin(api_key)
    key, info = create_tenant(req.name)
    return {
        "api_key": key,
        "tenant_id": info["tenant_id"],
        "name": info["name"],
    }


@app.get("/health")
def health_check():
    """Health check endpoint for Railway deployment."""
    return {"status": "ok", "service": "lumen-api"}


@app.get("/tenants/me")
def get_tenant_info(
    api_key: str = Security(api_key_header),
):
    """Retrieve tenant metadata for the authenticated key."""
    tenant = resolve_tenant(api_key)
    return {
        "tenant_id": tenant["tenant_id"],
        "name": tenant["name"],
        "active": tenant["active"],
    }


@app.post("/market/brief")
def market_brief(
    req: MarketBriefRequest,
    x_payment_proof: Optional[str] = Header(
        None, alias="X-Payment-Proof"
    ),
    api_key: str = Security(api_key_header)
):
    """Query aggregate patterns across all users.
    
    Requires x402 payment of 0.01 USDC on Base.
    For demo: pass X-Payment-Proof: 
    demo_payment_proof_base_usdc header.
    """
    tenant = resolve_tenant(api_key)
    
    # Check payment proof
    if x_payment_proof != DEMO_PAYMENT_PROOF:
        # Return 402 Payment Required
        return JSONResponse(
            status_code=402,
            content={
                "error": "payment_required",
                "amount": MARKET_PRICE_USDC,
                "currency": "USDC",
                "network": "base",
                "recipient": LUMEN_WALLET,
                "description": (
                    f"Lumen market brief — "
                    f"{req.domain} domain aggregate"
                ),
                "retry_header": "X-Payment-Proof",
                "docs": (
                    "Pay 0.01 USDC on Base to "
                    "https://lumen-memory-production"
                    ".up.railway.app, then retry "
                    "with X-Payment-Proof: "
                    "<tx_hash>"
                )
            }
        )
    
    # Payment valid — return aggregate patterns
    try:
        result = get_aggregate_patterns(req.domain)
        result["payment"] = {
            "amount_paid": MARKET_PRICE_USDC,
            "currency": "USDC",
            "network": "base",
            "status": "verified"
        }
        return result
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail=str(exc)
        )


@app.get("/market/domains")
def market_domains(
    api_key: str = Security(api_key_header)
):
    """List domains that have market data available."""
    tenant = resolve_tenant(api_key)
    
    memory = get_client()
    all_events = memory.read_events()
    
    domains = set()
    for ev in all_events:
        acted_list = ev.get("acted") or []
        for act in acted_list:
            if isinstance(act, str) and act.startswith("LUMEN|"):
                parts = act.split("|")
                if len(parts) >= 7:
                    domains.add(parts[2])
    
    return {
        "domains": sorted(list(domains)),
        "count": len(domains)
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
