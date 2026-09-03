"""SDK integration tests — requires api/server.py running."""

import pytest
import requests
from lumen_memory import Lumen
from lumen_memory.exceptions import (
    LumenValidationError,
    LumenConnectionError
)

API_URL = "http://localhost:8000"
DEMO_KEY = "lmn_demo0000000000000000000000000000"
ADMIN_KEY = "lmn_admin000000000000000000000000000"


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
    """Two tenants cannot see each other's data."""
    # Tenant 1 uses demo key
    lumen1 = Lumen(
        base_url=API_URL,
        api_key=DEMO_KEY
    )
    lumen1.wipe()
    lumen1.record("alex", "pitch",
                  "led with problem", "got meeting", 1)
    lumen1.record("alex", "pitch",
                  "led with problem", "got follow-up", 1)
    lumen1.record("alex", "pitch",
                  "led with features", "ghosted", -1)
    
    brief1 = lumen1.brief("alex", "pitch", "test")
    assert brief1.raw_outcomes == 3

    # Tenant 2 creates fresh connection 
    # Uses a different user_id scoping by using admin key
    lumen2 = Lumen(
        base_url=API_URL,
        api_key=ADMIN_KEY
    )
    
    # Admin tenant sees alex with 0 outcomes 
    # because admin:alex != demo:alex
    brief2 = lumen2.brief("alex", "pitch", "test")
    assert brief2.raw_outcomes == 0, (
        f"Tenant isolation failed. "
        f"Admin tenant saw {brief2.raw_outcomes} outcomes "
        f"that belong to demo tenant."
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
