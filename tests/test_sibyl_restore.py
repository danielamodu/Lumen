"""Restore-and-replay drill: deletion of Sibyl must be survivable.

This is the operational twin of the load-bearing gate
(tests/test_load_bearing.py): the gate proves the product goes blind without
Sibyl; this drill proves sight comes back from a snapshot. If this test ever
fails, backups are decoration.
"""

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.snapshot_sibyl import snapshot_sibyl, restore_sibyl
from lumen.memory import get_client
from lumen.core import record, brief

USER, DOMAIN = "drill_user", "pitch"


def _seeded_store(path: Path, n: int = 3):
    """Point the client at path and record n wins. Returns brief result."""
    get_client(path=str(path))
    for i in range(n):
        record(USER, DOMAIN, f"drill action {i}", "drill win", 1)
    result = brief(USER, DOMAIN, "cold")
    assert result["raw_outcomes"] == n
    assert result["pattern"] is not None
    return result


def _release_and_wipe(store_dir: Path) -> None:
    """Close the client handle, then delete every store file (extinction)."""
    client = get_client()
    storage = getattr(client, "_storage", None)
    if storage is not None and hasattr(storage, "close"):
        try:
            storage.close()
        except Exception:
            pass
    for p in store_dir.iterdir():
        if p.is_file():
            p.unlink()
    assert list(store_dir.iterdir()) == []


def test_snapshot_restore_roundtrip(tmp_path):
    """Extinction -> blindness -> restore -> sight. The whole point."""
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    backups = tmp_path / "backups"
    db_file = store_dir / "drill.db"

    before = _seeded_store(db_file)  # sight

    archive = snapshot_sibyl(store_dir, backups)
    assert archive.is_file()
    assert (backups / (archive.name + ".sha256")).is_file()

    _release_and_wipe(store_dir)  # extinction event

    # Blindness, proven against a fresh empty store. (The target directory
    # stays empty: restoring over a LIVE open database leaves stale WAL
    # state that shadows restored bytes, so the drill restores into the
    # quiesced empty dir — same rule production follows.)
    get_client(path=str(tmp_path / "scratch.db"))
    wiped = brief(USER, DOMAIN, "cold")
    assert wiped["pattern"] is None and wiped["raw_outcomes"] == 0

    restore_sibyl(archive, store_dir)
    get_client(path=str(db_file))  # reopen resurrected store
    after = brief(USER, DOMAIN, "cold")
    assert after["raw_outcomes"] == 3
    assert after["pattern"] == before["pattern"]  # same sight, not a copy


def test_restore_rejects_tampered_archive(tmp_path):
    """A flipped byte anywhere must refuse, not restore garbage."""
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    _seeded_store(store_dir / "drill.db")
    archive = snapshot_sibyl(store_dir, tmp_path / "backups")

    tampered = tmp_path / "tampered.tar.gz"
    shutil.copy(archive, tampered)
    shutil.copy(str(archive) + ".sha256", str(tampered) + ".sha256")
    data = bytearray(tampered.read_bytes())
    data[len(data) // 2] ^= 0xFF
    tampered.write_bytes(bytes(data))

    with pytest.raises(ValueError, match="integrity check FAILED"):
        restore_sibyl(tampered, tmp_path / "evil", force=True)


def test_restore_refuses_nonempty_without_force(tmp_path):
    """No silent overwrites of a live store."""
    store_dir = tmp_path / "store"
    store_dir.mkdir()
    _seeded_store(store_dir / "drill.db")
    archive = snapshot_sibyl(store_dir, tmp_path / "backups")

    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "live.db").write_text("live data")

    with pytest.raises(ValueError, match="not empty"):
        restore_sibyl(archive, occupied)
    assert (occupied / "live.db").read_text() == "live data"
