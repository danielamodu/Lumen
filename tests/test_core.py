"""Unit tests for Lumen core module."""

import pytest
from lumen.memory import get_client
from lumen.core import record, brief


@pytest.fixture(autouse=True)
def fresh_db(tmp_path):
    """Ensure each test executes against a fresh isolated database."""
    db_file = str(tmp_path / "test_lumen.db")
    get_client(path=db_file)
    return db_file


def test_record_writes_cold_event_and_creates_warm_pattern():
    """Test 1: record() writes a COLD event and creates a WARM pattern entity.

    - Call record("alex", "pitch", "led with product demo", "no response", -1)
    - Assert the WARM pattern entity kind="pattern", name="alex:pitch" exists
    - Assert total_outcomes == 1
    - Assert loss_rate == 1.0
    """
    record("alex", "pitch", "led with product demo", "no response", -1)

    memory = get_client()
    pattern_entity = memory.get_entity("pattern", "alex:pitch")
    assert pattern_entity is not None
    body = pattern_entity["body"]
    assert body["total_outcomes"] == 1
    assert body["loss_rate"] == 1.0


def test_brief_returns_warning_when_signal_is_negative():
    """Test 2: brief() returns a warning when signal is negative.

    - Seed 3 losing records for user "alex", domain "pitch"
    - Call brief("alex", "pitch", "about to pitch a fund")
    - Assert result["warning"] is not None
    - Assert result["confidence"] contains "3 outcomes"
    """
    record("alex", "pitch", "led with product demo", "no response", -1)
    record("alex", "pitch", "sent raw deck", "ghosted", -1)
    record("alex", "pitch", "rushed the pitch", "declined", -1)

    result = brief("alex", "pitch", "about to pitch a fund")
    assert result["warning"] is not None
    assert "3 outcomes" in result["confidence"]


def test_cross_domain_insight_appears_when_other_domains_have_outcomes():
    """Test 3: cross_domain insight appears when other domains have outcomes.

    - Seed 3 pitch outcomes (all losses) for user "alex"
    - Seed 3 ask outcomes (all wins) for user "alex"
    - Call brief("alex", "pitch", "pitching today")
    - Assert result["cross_domain"] is not None
    """
    record("alex", "pitch", "led with product demo", "no response", -1)
    record("alex", "pitch", "sent raw deck", "ghosted", -1)
    record("alex", "pitch", "rushed the pitch", "declined", -1)

    record("alex", "ask", "gave full context before asking", "got intro", 1)
    record("alex", "ask", "customized mutual benefit", "accepted", 1)
    record("alex", "ask", "referenced mutual connection", "got meeting", 1)

    result = brief("alex", "pitch", "pitching today")
    assert result["cross_domain"] is not None


def test_brief_returns_none_when_no_outcomes_exist():
    """Test 4: brief() returns None for warning and pattern when no outcomes exist.

    - Call brief("newuser", "pitch", "first time")
    - Assert result["warning"] is None
    - Assert result["pattern"] is None
    - Assert result["raw_outcomes"] == 0
    """
    result = brief("newuser", "pitch", "first time")
    assert result["warning"] is None
    assert result["pattern"] is None
    assert result["raw_outcomes"] == 0


def test_record_then_brief_round_trip():
    """Test 5: record() then brief() round trip.

    - Call record 5 times with mixed signals for user "bob", domain "post"
    - Call brief("bob", "post", "about to post")
    - Assert result["raw_outcomes"] == 5
    """
    record("bob", "post", "long technical thread", "high engagement", 1)
    record("bob", "post", "generic link drop", "zero engagement", -1)
    record("bob", "post", "short question post", "moderate engagement", 0)
    record("bob", "post", "code snippet with breakdown", "viral", 1)
    record("bob", "post", "unformatted wall of text", "negative comments", -1)

    result = brief("bob", "post", "about to post")
    assert result["raw_outcomes"] == 5


def test_custom_domain_works():
    """Test that custom domain strings work beyond pitch/post/ask."""
    record("alex", "code_review", 
           "reviewed without running tests", 
           "missed bug in prod", -1)
    record("alex", "code_review",
           "ran full test suite before reviewing",
           "caught 3 bugs before merge", 1)
    record("alex", "code_review",
           "ran full test suite before reviewing", 
           "clean merge no issues", 1)
    
    result = brief("alex", "code_review", 
                   "about to review a PR")
    assert result["raw_outcomes"] == 3
    assert result["pattern"] is not None
    assert result["warning"] is not None

