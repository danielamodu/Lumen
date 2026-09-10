"""Fail-closed mode (LUMEN_REQUIRE_MEMORY): memory endpoints 503 without Sibyl.

Default (flag off): blind-but-200 on empty memory — existing behavior,
covered by the rest of the suite. Flag on: /brief, /record and
/market/brief refuse; /health, /seed, /wipe stay open (plumbing + recovery).
"""

from fastapi.testclient import TestClient

from api.server import app
from lumen.memory import get_client

H = {"X-Lumen-Key": "lmn_demo0000000000000000000000000000"}
RECORD = {"user_id": "hard_user", "domain": "pitch",
          "action": "did a thing", "outcome": "it worked", "signal": 1}
BRIEF = {"user_id": "hard_user", "domain": "pitch", "context": "cold"}
MARKET = {"domain": "pitch", "context": "cold"}


def _client(tmp_path):
    get_client(path=str(tmp_path / "hard.db"))
    return TestClient(app)


def test_flag_off_serves_blind_but_200(tmp_path, monkeypatch):
    """Default posture unchanged: empty memory, 200s with Nones."""
    monkeypatch.delenv("LUMEN_REQUIRE_MEMORY", raising=False)
    c = _client(tmp_path)
    assert c.get("/health").status_code == 200
    res = c.post("/brief", json=BRIEF, headers=H)
    assert res.status_code == 200
    assert res.json()["pattern"] is None


def test_flag_on_503s_memory_endpoints_when_empty(tmp_path, monkeypatch):
    """Fail-closed: no memory -> 503 on product endpoints, 200 on plumbing."""
    monkeypatch.setenv("LUMEN_REQUIRE_MEMORY", "true")
    c = _client(tmp_path)
    assert c.get("/health").status_code == 200
    assert c.post("/brief", json=BRIEF, headers=H).status_code == 503
    assert c.post("/record", json=RECORD, headers=H).status_code == 503
    assert c.post("/market/brief", json=MARKET, headers=H).status_code == 503


def test_flag_on_serves_once_memory_exists(tmp_path, monkeypatch):
    """Restore flips 503 back to 200 — the resurrection half of the demo."""
    monkeypatch.setenv("LUMEN_REQUIRE_MEMORY", "true")
    c = _client(tmp_path)
    assert c.post("/brief", json=BRIEF, headers=H).status_code == 503
    # Recovery seeding bypasses the HTTP layer here because /seed and /wipe
    # intentionally operate on the real default store, never a test store.
    from lumen.core import record
    record("demo:hard_user", "pitch", "did a thing", "it worked", 1)
    assert c.post("/brief", json=BRIEF, headers=H).status_code == 200
    assert c.post("/record", json=RECORD, headers=H).status_code == 200
