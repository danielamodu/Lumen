"""SDK integration tests — requires api/server.py running."""

import pytest
import requests
from lumen_memory import Lumen
from lumen_memory.exceptions import (
    LumenValidationError,
    LumenConnectionError
)

import os
API_URL = os.environ.get("LUMEN_API_URL", "https://lumen-memory-production.up.railway.app")
DEMO_KEY = "lmn_demo0000000000000000000000000000"


def server_is_running():
    try:
        res = requests.post(
            f"{API_URL}/seed",
            json={},
            headers={"X-Lumen-Key": DEMO_KEY},
            timeout=10
        )
        return res.status_code == 200
    except Exception:
        return False


requires_server = pytest.mark.skipif(
    not server_is_running(),
    reason="Lumen API server not running"
)


@requires_server
def test_sdk_record_and_brief_roundtrip():
    """SDK record() then brief() returns populated result."""
    lumen = Lumen(base_url=API_URL, api_key=DEMO_KEY)
    lumen.wipe()
    
    lumen.record("sdk_user", "pitch",
                 "led with problem", "got meeting", 1)
    lumen.record("sdk_user", "pitch",
                 "led with features", "got ghosted", -1)
    lumen.record("sdk_user", "pitch",
                 "led with problem", "got follow-up", 1)
    
    brief = lumen.brief("sdk_user", "pitch", 
                        "about to pitch")
    
    assert brief.raw_outcomes == 3
    assert brief.pattern is not None
    assert brief.warning is not None


@requires_server
def test_sdk_custom_domain():
    """SDK works with any domain string."""
    lumen = Lumen(base_url=API_URL, api_key=DEMO_KEY)
    
    lumen.record("sdk_user", "code_review",
                 "reviewed without tests", "missed bug", -1)
    lumen.record("sdk_user", "code_review",
                 "ran tests first", "clean merge", 1)
    lumen.record("sdk_user", "code_review",
                 "ran tests first", "caught 2 bugs", 1)
    
    brief = lumen.brief("sdk_user", "code_review",
                        "about to review a PR")
    assert brief.raw_outcomes == 3
    assert brief.pattern is not None


@requires_server
def test_isolation_between_tenants():
    """Two tenants cannot see each other's data.

    Provisions a real second tenant via /tenants/create (requires the
    admin key to be configured server-side via LUMEN_ADMIN_KEY). Skips
    cleanly if no admin key is available in the environment.
    """
    admin_key = os.environ.get("LUMEN_ADMIN_KEY")
    if not admin_key:
        pytest.skip(
            "LUMEN_ADMIN_KEY not set — cannot provision a second "
            "tenant to test isolation."
        )

    # Tenant 1 uses demo key
    lumen1 = Lumen(base_url=API_URL, api_key=DEMO_KEY)
    lumen1.wipe()
    lumen1.record("alex", "pitch",
                  "led with problem", "got meeting", 1)
    lumen1.record("alex", "pitch",
                  "led with problem", "got follow-up", 1)
    lumen1.record("alex", "pitch",
                  "led with features", "ghosted", -1)

    brief1 = lumen1.brief("alex", "pitch", "test")
    assert brief1.raw_outcomes == 3

    # Mint a genuinely separate tenant with the admin key.
    create_res = requests.post(
        f"{API_URL}/tenants/create",
        json={"name": "isolation-test"},
        headers={"X-Lumen-Key": admin_key},
        timeout=10,
    )
    assert create_res.status_code == 200, (
        f"Could not create second tenant: "
        f"{create_res.status_code} {create_res.text}"
    )
    tenant2_key = create_res.json()["api_key"]

    lumen2 = Lumen(base_url=API_URL, api_key=tenant2_key)

    # The new tenant shares the same user_id "alex" but is scoped to a
    # different tenant_id, so it must see zero of tenant 1's outcomes.
    brief2 = lumen2.brief("alex", "pitch", "test")
    assert brief2.raw_outcomes == 0, (
        f"Tenant isolation failed. "
        f"Second tenant saw {brief2.raw_outcomes} outcomes "
        f"that belong to the demo tenant."
    )


def test_sdk_validation_error():
    """SDK raises LumenValidationError for invalid signal."""
    lumen = Lumen(base_url=API_URL, api_key=DEMO_KEY)
    
    with pytest.raises(LumenValidationError):
        lumen.record("alex", "pitch", "action", 
                     "outcome", 99)


def test_sdk_connection_error():
    """SDK raises LumenConnectionError when server unreachable."""
    lumen = Lumen(base_url="http://localhost:9999", api_key=DEMO_KEY)
    
    with pytest.raises(LumenConnectionError):
        lumen.brief("alex", "pitch", "test")
