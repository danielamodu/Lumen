"""Seed script for Lumen demonstration with 30 days of realistic outcomes and counterfactual engineering."""

import glob
import os
from pprint import pprint
from lumen.core import record, brief
from lumen.memory import get_client


def seed_outcomes(user_id: str = "alex"):
    """Seed 33 realistic outcomes for user 'alex' (or scoped user_id) across pitch (12), post (11), and ask (10) domains."""
    db_path = os.path.expanduser("~/.sibyl-memory/lumen_demo.db")
    for f in glob.glob(db_path + "*"):
        try:
            os.remove(f)
        except OSError:
            pass
    get_client(path=db_path)

    # These are example domains. Lumen accepts any domain string.
    # 1. Seed Pitch Domain (12 outcomes: 6 losses, 6 wins)
    pitch_outcomes = [
        # 6 Losses (signal = -1)
        ("led with product demo", "no response after 5 days", -1),
        ("showed the deck first", "ghosted after initial call", -1),
        ("opened with features", "declined politely - didn't see need", -1),
        ("led with product demo", "feedback was too technical, no follow-up", -1),
        ("showed the deck first", "lost attention in first 5 minutes", -1),
        ("opened with features", "asked to email materials, never replied", -1),
        # 6 Wins (signal = 1)
        ("led with their problem", "got a meeting booked for next week", 1),
        ("opened with the pain point", "partner asked for immediate follow-up", 1),
        ("started with their context", "engaged deeply on ROI, scheduled partner call", 1),
        ("led with their problem", "replied interested within 2 hours", 1),
        ("opened with the pain point", "agreed to pilot term sheet", 1),
        ("opened with the pain point", "secured follow-up with investment committee", 1),
    ]

    # 2. Seed Post Domain (11 outcomes: 4 losses, 7 wins)
    post_outcomes = [
        # 4 Losses (signal = -1)
        ("generic announcement", "low reach and zero comments", -1),
        ("link drop", "algorithmic penalty, 12 impressions", -1),
        ("product update post", "no reposts or meaningful replies", -1),
        ("generic announcement", "crickets after 24 hours", -1),
        # 7 Wins (signal = 1)
        ("opened with a question", "started high-engagement debate with 45 replies", 1),
        ("shared a personal story", "viral reach, 120 bookmarks and 30 DMs", 1),
        ("posted a counterintuitive take", "quote tweeted by industry leaders", 1),
        ("opened with a question", "300+ likes and 5 customer inquiries", 1),
        ("shared a personal story", "high save rate and positive discussion", 1),
        ("posted a counterintuitive take", "shared in multiple private communities", 1),
        ("opened with a question", "generated 8 qualified inbound leads", 1),
    ]

    # 3. Seed Ask Domain (10 outcomes: 3 losses, 7 wins)
    ask_outcomes = [
        # 3 Losses (signal = -1)
        ("cold ask with no context", "ignored completely", -1),
        ("asked without establishing value first", "declined without explanation", -1),
        ("cold ask with no context", "left on read for 2 weeks", -1),
        # 7 Wins (signal = 1)
        ("gave full context before asking", "warm intro made within an hour", 1),
        ("established mutual benefit first", "enthusiastic yes, hopped on call", 1),
        ("referenced shared connection", "intro accepted and meeting scheduled", 1),
        ("gave full context before asking", "got the intro and direct intro to CEO", 1),
        ("established mutual benefit first", "agreed to collaborate on research", 1),
        ("referenced shared connection", "immediate response offering mentorship", 1),
        ("gave full context before asking", "got the investment intro", 1),
    ]

    for action, outcome, sig in pitch_outcomes:
        record(user_id, "pitch", action, outcome, sig)

    for action, outcome, sig in post_outcomes:
        record(user_id, "post", action, outcome, sig)

    for action, outcome, sig in ask_outcomes:
        record(user_id, "ask", action, outcome, sig)


def run_seed():
    """Execute complete seed routine and counterfactual demonstration."""
    print("Seeding 30 days of outcomes for user 'alex'...")
    seed_outcomes()
    print("Seeding complete: 12 pitch, 11 post, 10 ask outcomes recorded.\n")

    # Step 1 — Show brief BEFORE contradiction
    print("=== BRIEF BEFORE CONTRADICTION ===")
    before_brief = brief("alex", "pitch", "about to pitch a crypto fund today")
    pprint(before_brief)

    # Step 2 — Add one contradicting outcome
    print("\nAdding contradicting outcome: 'led with product demo' resulted in a win (signal=1)...")
    record("alex", "pitch", "led with product demo", "got a meeting — they loved the demo", 1)

    # Step 3 — Show brief AFTER contradiction
    print("\n=== BRIEF AFTER CONTRADICTION ===")
    after_brief = brief("alex", "pitch", "about to pitch a crypto fund today")
    pprint(after_brief)

    # Step 4 — The delete test setup
    print("\n=== DELETE TEST ===")
    print("To demonstrate Sibyl is load-bearing, run:")
    print("  python demo/wipe.py")
    print("Then call brief() again: warning, pattern, cross_domain all return None.")


if __name__ == "__main__":
    run_seed()
