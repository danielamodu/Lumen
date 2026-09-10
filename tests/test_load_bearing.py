"""Load-bearing contract: Lumen's intelligence lives ONLY in Sibyl memory.

Delete Sibyl -> the product goes blind. This is the thesis of the product,
so it is enforced as an automated gate, not a demo anecdote. Every Phase 1
task (Postgres sidecars, snapshots, evals) must keep these tests green:
- derived stores may change, but blindness-without-Sibyl must hold;
- nothing may cache intelligence outside the store in a way that survives it.
"""

import os

from lumen.memory import get_client
from lumen.core import record, brief


def _isolated_db(tmp_path, name="load_bearing.db"):
    """Point the client at a fresh isolated store. Returns its path."""
    db_file = str(tmp_path / name)
    get_client(path=db_file)
    return db_file


def _delete_sibyl(db_file):
    """Delete the Sibyl store and reopen empty at the same location.

    Returns once the client is pointed at the empty store.
    """
    client = get_client()
    storage = getattr(client, "_storage", None)
    if storage is not None and hasattr(storage, "close"):
        try:
            storage.close()
        except Exception:
            pass
    os.remove(db_file)
    assert not os.path.exists(db_file), "Sibyl store was not actually deleted"
    get_client(path=db_file)


def test_sight_requires_memory(tmp_path):
    """Fresh memory sees nothing; one recorded win produces a pattern."""
    _isolated_db(tmp_path)

    before = brief("gate_user", "pitch", "cold")
    assert before["pattern"] is None
    assert before["warning"] is None
    assert before["raw_outcomes"] == 0

    record("gate_user", "pitch", "opened with their problem",
           "got the meeting", 1)

    after = brief("gate_user", "pitch", "cold")
    assert after["raw_outcomes"] == 1
    assert after["pattern"] is not None
    assert "opened with their problem" in after["pattern"]


def test_delete_sibyl_blinds_product(tmp_path):
    """THE gate: deleting the Sibyl store removes all intelligence."""
    db_file = _isolated_db(tmp_path)
    record("gate_user", "pitch", "opened with their problem",
           "got the meeting", 1)
    assert brief("gate_user", "pitch", "cold")["pattern"] is not None

    _delete_sibyl(db_file)

    wiped = brief("gate_user", "pitch", "cold")
    assert wiped["pattern"] is None
    assert wiped["warning"] is None
    assert wiped["cross_domain"] is None
    assert wiped["raw_outcomes"] == 0
    assert "No pattern yet" in wiped["confidence"]


def test_patterns_come_from_store_not_process(tmp_path):
    """A reopened client on the same file sees the same patterns.

    Fails if intelligence ever lives in process memory instead of Sibyl —
    which would also break the delete-gate above.
    """
    db_file = _isolated_db(tmp_path)
    record("gate_user", "pitch", "opened with their problem",
           "got the meeting", 1)

    get_client(path=db_file)  # force re-open from disk

    again = brief("gate_user", "pitch", "cold")
    assert again["raw_outcomes"] == 1
    assert again["pattern"] is not None
