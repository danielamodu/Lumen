"""Loop demo for Lumen — automated end-to-end demonstration of the learning loop."""

import glob
import os
import sys
import time
from pathlib import Path
from demo.seed import seed_outcomes
from lumen.core import record, brief
from lumen.memory import get_client

# Ensure UTF-8 output encoding on Windows terminals for emoji / unicode glyphs
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main():
    """Run the automated Lumen learning loop demonstration."""
    # Step 0 — Reset and seed
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
    seed_outcomes()
    print("Lumen initialized. 33 outcomes loaded into Sibyl memory.")

    # Step 1 — Show the opening brief (Session 1)
    result = brief("alex", "pitch", "pitching an AI infrastructure fund on agent memory")

    print("\n" + "=" * 60)
    print("SESSION 1 — LUMEN BRIEF FOR ALEX (PITCH DOMAIN)")
    print("=" * 60)
    print(f"  Outcomes recorded : {result['raw_outcomes']}")
    print(f"  Confidence        : {result['confidence']}")
    print(f"\n  ⚠️  WARNING       : {result['warning']}")
    print(f"  ✅ PATTERN        : {result['pattern']}")
    print(f"  🔗 CROSS-DOMAIN   : {result['cross_domain']}")
    print("=" * 60)

    # Step 2 — Simulate Session 1 outcome (a loss)
    time.sleep(2)

    print("\n[Session 1 complete]")
    print("Alex led with the product demo. Got ghosted.\n")

    record(
        "alex",
        "pitch",
        "opened with product architecture diagram",
        "no reply after 7 days",
        -1,
    )

    print("→ Outcome written to Sibyl memory (COLD journal).")
    print("→ Pattern recalculated (WARM tier updated).")
    time.sleep(1)

    # Step 3 — Show brief has changed (Session 2)
    result2 = brief("alex", "pitch", "pitching an AI infrastructure fund on agent memory")

    print("\n" + "=" * 60)
    print("SESSION 2 — LUMEN BRIEF FOR ALEX (PITCH DOMAIN)")
    print("=" * 60)
    print(f"  Outcomes recorded : {result2['raw_outcomes']}")
    print(f"  Confidence        : {result2['confidence']}")
    print(f"\n  ⚠️  WARNING       : {result2['warning']}")
    print(f"  ✅ PATTERN        : {result2['pattern']}")
    print(f"  🔗 CROSS-DOMAIN   : {result2['cross_domain']}")
    print("=" * 60)

    # Highlight the change
    if result2["raw_outcomes"] != result["raw_outcomes"]:
        print(
            f"\n  → Outcomes: {result['raw_outcomes']} → "
            f"{result2['raw_outcomes']} (+1)"
        )

    # Step 4 — Simulate Session 2 outcome (a win that contradicts)
    time.sleep(2)

    print("\n[Session 2 complete]")
    print("Alex tried leading with the problem. Got a meeting.\n")

    record(
        "alex",
        "pitch",
        "opened with the problem — agents forget everything",
        "got a meeting booked same day",
        1,
    )

    print("→ Outcome written to Sibyl memory (COLD journal).")
    print("→ Pattern recalculated (WARM tier updated).")
    time.sleep(1)

    # Step 5 — Show brief after win (Session 3)
    result3 = brief("alex", "pitch", "pitching an AI infrastructure fund on agent memory")

    print("\n" + "=" * 60)
    print("SESSION 3 — LUMEN BRIEF FOR ALEX (PITCH DOMAIN)")
    print("=" * 60)
    print(f"  Outcomes recorded : {result3['raw_outcomes']}")
    print(f"  Confidence        : {result3['confidence']}")
    print(f"\n  ⚠️  WARNING       : {result3['warning']}")
    print(f"  ✅ PATTERN        : {result3['pattern']}")
    print(f"  🔗 CROSS-DOMAIN   : {result3['cross_domain']}")
    print("=" * 60)

    # Show the delta explicitly
    print("\n  MEMORY DELTA:")
    print(f"  Session 1 raw_outcomes : {result['raw_outcomes']}")
    print(f"  Session 3 raw_outcomes : {result3['raw_outcomes']}")
    print(f"  Warning changed        : {'YES' if result['warning'] != result3['warning'] else 'NO'}")
    print(f"  Pattern changed        : {'YES' if result['pattern'] != result3['pattern'] else 'NO'}")

    # Step 6 — The wipe moment
    time.sleep(2)

    print("\n" + "=" * 60)
    print("DELETE TEST — REMOVING SIBYL MEMORY")
    print("=" * 60)
    print("Deleting ~/.sibyl-memory/lumen_demo.db ...")
    time.sleep(1)

    # Delete and reinitialize
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

    print("Sibyl memory deleted.")
    print("Calling brief() on fresh empty memory...\n")
    time.sleep(1)

    result_wiped = brief("alex", "pitch", "pitching an AI infrastructure fund on agent memory")

    print("=" * 60)
    print("SESSION AFTER WIPE — LUMEN BRIEF FOR ALEX")
    print("=" * 60)
    print(f"  Outcomes recorded : {result_wiped['raw_outcomes']}")
    print(f"  Confidence        : {result_wiped['confidence']}")
    print(f"\n  ⚠️  WARNING       : {result_wiped['warning']}")
    print(f"  ✅ PATTERN        : {result_wiped['pattern']}")
    print(f"  🔗 CROSS-DOMAIN   : {result_wiped['cross_domain']}")
    print("=" * 60)

    print("\n  Without Sibyl memory:")
    print("  → warning      : None")
    print("  → pattern      : None")
    print("  → cross_domain : None")
    print("  → The agent has no memory. It cannot learn.")
    print("  → Delete Sibyl. Lumen goes blind.")

    # Step 7 — Final summary
    print("\n" + "=" * 60)
    print("LUMEN — OUTCOME MEMORY LAYER")
    print("=" * 60)
    print("  3 sessions demonstrated.")
    print("  Each session wrote to Sibyl COLD journal.")
    print("  Each write recalculated the WARM pattern tier.")
    print("  Each brief read from WARM and wrote to HOT state.")
    print("  Cross-domain insight surfaced from Ask domain memory.")
    print("  Delete Sibyl: agent goes blind. Memory is load-bearing.")
    print("=" * 60)


if __name__ == "__main__":
    main()
