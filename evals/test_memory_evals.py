"""Memory quality evals: prove Lumen improves decisions, don't assert it.

Each eval seeds a synthetic history with KNOWN ground truth, then scores
what brief() surfaces. On perfectly separable data the scores must be
perfect — anything less is a regression in the product's core promise.
Run:  pytest evals/ -v -s   (-s shows the metrics table)

These evals are the sales evidence AND the regression suite for all future
memory-quality work (thresholds, decay, retrieval changes must move these
numbers up, never down).
"""

import random

from lumen.memory import get_client
from lumen.core import record, brief

GOOD_ACTION = "opened with their problem"
BAD_ACTION = "led with product demo"
DOMAIN = "pitch"


def _isolated_db(tmp_path):
    db_file = str(tmp_path / "eval.db")
    get_client(path=db_file)
    return db_file


def _seed_separable_history(n_good=6, n_bad=6, user="eval_user",
                            domain=DOMAIN, noise_neutrals=0):
    for _ in range(n_good):
        record(user, domain, GOOD_ACTION, "got the meeting", 1)
    for _ in range(n_bad):
        record(user, domain, BAD_ACTION, "ghosted", -1)
    for i in range(noise_neutrals):
        record(user, domain, f"small talk {i}", "no signal", 0)


def test_pattern_precision_on_separable_history(tmp_path, capsys):
    """Warning must name the bad action, pattern the good one. Exactly."""
    _isolated_db(tmp_path)
    _seed_separable_history()
    result = brief("eval_user", DOMAIN, "about to pitch")

    pattern_hit = GOOD_ACTION in (result["pattern"] or "")
    warning_hit = BAD_ACTION in (result["warning"] or "")
    precision = (pattern_hit + warning_hit) / 2
    print(f"\n[EVAL] separable precision: {precision:.2f} "
          f"(pattern={pattern_hit}, warning={warning_hit})")

    assert result["raw_outcomes"] == 12
    assert pattern_hit, f"pattern missed good action: {result['pattern']}"
    assert warning_hit, f"warning missed bad action: {result['warning']}"
    assert precision == 1.0


def test_robustness_to_noise_and_neutrals(tmp_path, capsys):
    """Neutral chatter must not dethrone the true pattern."""
    _isolated_db(tmp_path)
    _seed_separable_history(noise_neutrals=4)
    result = brief("eval_user", DOMAIN, "about to pitch")

    pattern_hit = GOOD_ACTION in (result["pattern"] or "")
    warning_hit = BAD_ACTION in (result["warning"] or "")
    print(f"\n[EVAL] noisy precision: {(pattern_hit + warning_hit) / 2:.2f} "
          f"over {result['raw_outcomes']} outcomes")

    assert pattern_hit and warning_hit


def test_min_sample_confidence_ladder(tmp_path, capsys):
    """Confidence wording must track evidence: early < developing < stable."""
    _isolated_db(tmp_path)
    labels = {}
    for i in range(10):
        record("ladder_user", DOMAIN, GOOD_ACTION, "win", 1)
        labels[i + 1] = brief("ladder_user", DOMAIN, "x")["confidence"]
    print(f"\n[EVAL] confidence ladder: 1->{labels[1]!r} "
          f"5->{labels[5]!r} 10->{labels[10]!r}")

    assert "early" in labels[1]
    assert "developing" in labels[5]
    assert "stable" in labels[10]


def test_cross_domain_surfaces_with_evidence(tmp_path):
    """3+ outcomes elsewhere must produce a cross-domain insight."""
    _isolated_db(tmp_path)
    record("xd_user", DOMAIN, GOOD_ACTION, "win", 1)
    assert brief("xd_user", DOMAIN, "x")["cross_domain"] is None
    for _ in range(3):
        record("xd_user", "ask", "gave context first", "got intro", 1)
    result = brief("xd_user", DOMAIN, "x")
    assert result["cross_domain"] is not None
    assert "Ask" in result["cross_domain"]


def test_follow_memory_beats_baseline(tmp_path, capsys):
    """A policy that obeys the brief must beat random choice. The sale.

    Ground truth is fixed: GOOD_ACTION always wins, BAD_ACTION always loses.
    The brief-trained policy picks the pattern action; the baseline flips a
    coin (seeded). Margin must be decisive, not marginal.
    """
    _isolated_db(tmp_path)
    _seed_separable_history()
    result = brief("eval_user", DOMAIN, "about to pitch")

    truth = {GOOD_ACTION: 1.0, BAD_ACTION: 0.0}
    policy_action = GOOD_ACTION if result["pattern"] else BAD_ACTION
    policy_wins = sum(truth[policy_action] for _ in range(100)) / 100

    rng = random.Random(7)
    baseline_wins = sum(
        truth[rng.choice([GOOD_ACTION, BAD_ACTION])] for _ in range(100)
    ) / 100
    margin = policy_wins - baseline_wins
    print(f"\n[EVAL] policy win rate: {policy_wins:.2f} vs "
          f"baseline: {baseline_wins:.2f} (margin +{margin:.2f})")

    assert policy_wins == 1.0
    assert margin >= 0.40, f"memory margin too thin: +{margin:.2f}"
