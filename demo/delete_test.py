"""THE DELETE TEST — judge-ready proof that Sibyl is the load-bearing layer.

One command:  python demo/delete_test.py

Arc (all through the real HTTP API, all on an isolated store — real data
untouched):
  1. SIGHT ..... seed history via POST /record, show a rich POST /brief.
  2. SNAPSHOT .. back the store up (scripts/snapshot_sibyl.py).
  3. EXTINCTION  delete every store file, reopen empty (= server restart
                 after `rm -rf ~/.sibyl-memory`).
  4. DEAD ...... brief returns all-None; new records land in a void with no
                 history; no webhook can ever fire. The product doesn't work.
  5. RESURRECT . restore the snapshot, reopen, full memory back sight-for-
                 sight (pattern equality, not just non-None).

Exit code 0 + "VERDICT: SIBYL IS LOAD-BEARING" iff every gate holds.
"""

import glob
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("LUMEN_FORCE_HTTPS", "false")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient  # noqa: E402

from api.server import app  # noqa: E402
from lumen.memory import get_client  # noqa: E402
from scripts.snapshot_sibyl import snapshot_sibyl, restore_sibyl  # noqa: E402

H = {"X-Lumen-Key": "lmn_demo0000000000000000000000000000"}
USER, DOMAIN = "demo_judge_001", "pitch"

WINS = [
    ("opened with their problem", "got the meeting"),
    ("led with their problem", "replied interested within 2 hours"),
    ("opened with the pain point", "agreed to pilot term sheet"),
]
LOSSES = [
    ("led with product demo", "ghosted"),
    ("showed the deck first", "no response after 5 days"),
]


def _close_store():
    client = get_client()
    storage = getattr(client, "_storage", None)
    if storage is not None and hasattr(storage, "close"):
        try:
            storage.close()
        except Exception:
            pass


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="lumen-delete-test-"))
    store_dir = tmp / "store"
    store_dir.mkdir()
    get_client(path=str(store_dir / "judge.db"))
    c = TestClient(app)

    print("=" * 64)
    print("1. SIGHT — seeding history through POST /record")
    print("=" * 64)
    for action, outcome in WINS:
        r = c.post("/record", json={
            "user_id": USER, "domain": DOMAIN,
            "action": action, "outcome": outcome, "signal": 1}, headers=H)
        assert r.json()["status"] == "ok", r.text
    for action, outcome in LOSSES:
        r = c.post("/record", json={
            "user_id": USER, "domain": DOMAIN,
            "action": action, "outcome": outcome, "signal": -1}, headers=H)
        assert r.json()["status"] == "ok", r.text
    sight = c.post("/brief", json={
        "user_id": USER, "domain": DOMAIN,
        "context": "about to pitch a crypto fund"}, headers=H).json()
    print(f"   raw_outcomes: {sight['raw_outcomes']}")
    print(f"   pattern: {sight['pattern']}")
    print(f"   warning: {sight['warning']}")
    assert sight["raw_outcomes"] == 5 and sight["pattern"] and sight["warning"]

    print("=" * 64)
    print("2. SNAPSHOT — backing up Sibyl")
    print("=" * 64)
    archive = snapshot_sibyl(store_dir, tmp / "backups")

    print("=" * 64)
    print("3. EXTINCTION — rm -rf the Sibyl store, restart empty")
    print("=" * 64)
    _close_store()
    for f in glob.glob(str(store_dir / "judge.db") + "*"):
        os.remove(f)
    get_client(path=str(store_dir / "judge.db"))

    print("=" * 64)
    print("4. DEAD — the product without Sibyl")
    print("=" * 64)
    dead = c.post("/brief", json={
        "user_id": USER, "domain": DOMAIN,
        "context": "about to pitch a crypto fund"}, headers=H).json()
    print(f"   brief: pattern={dead['pattern']}, warning={dead['warning']}, "
          f"cross_domain={dead['cross_domain']}, "
          f"raw_outcomes={dead['raw_outcomes']}")
    assert (dead["pattern"] is None and dead["warning"] is None
            and dead["cross_domain"] is None and dead["raw_outcomes"] == 0)

    orphan = c.post("/record", json={
        "user_id": USER, "domain": DOMAIN,
        "action": "tried something new", "outcome": "who knows",
        "signal": 1}, headers=H).json()
    after_orphan = c.post("/brief", json={
        "user_id": USER, "domain": DOMAIN, "context": "x"}, headers=H).json()
    print(f"   record into the void: {orphan['status']} — but brief sees "
          f"only {after_orphan['raw_outcomes']} orphan outcome(s), "
          f"zero history, zero learning")
    assert after_orphan["raw_outcomes"] == 1
    assert after_orphan["confidence"] == "1 outcomes recorded. Pattern is early."

    health = c.get("/health").json()
    print(f"   plumbing check: /health -> {health} (doors open, rooms empty)")

    print("=" * 64)
    print("5. RESURRECT — restore the snapshot, memory returns sight-for-sight")
    print("=" * 64)
    _close_store()
    for f in store_dir.iterdir():
        if f.is_file():
            f.unlink()
    restore_sibyl(archive, store_dir)
    get_client(path=str(store_dir / "judge.db"))
    back = c.post("/brief", json={
        "user_id": USER, "domain": DOMAIN,
        "context": "about to pitch a crypto fund"}, headers=H).json()
    print(f"   raw_outcomes: {back['raw_outcomes']}")
    print(f"   pattern: {back['pattern']}")
    assert back["raw_outcomes"] == 5
    assert back["pattern"] == sight["pattern"]

    print("=" * 64)
    print("VERDICT: SIBYL IS LOAD-BEARING — delete it and Lumen goes blind;")
    print("         restore it and every pattern returns exactly.")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
