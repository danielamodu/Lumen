"""Sibyl memory snapshot and restore (disaster recovery for the source of truth).

Sibyl is the one component that must never lose data: Postgres tables are
rebuildable projections, but the COLD journal exists only here. These tools
make "delete Sibyl" a recoverable disaster instead of an extinction event.

Usage from the repo root:
    python scripts/snapshot_sibyl.py snapshot [--source DIR] [--dest DIR]
    python scripts/snapshot_sibyl.py restore ARCHIVE [--dest DIR] [--force]

Defaults: source ~/.sibyl-memory, dest ./backups (gitignored).
A snapshot is a timestamped .tar.gz containing the store files plus a
manifest.json with per-file SHA-256 hashes, with an archive-level .sha256
sidecar. Restore verifies the sidecar (if present), then every member hash,
and refuses to extract over a non-empty directory without --force.

Production note: SQLite stores are checkpointed via the online backup API, so
snapshots are crash-consistent without stopping the app. For belt-and-braces,
layer Railway volume snapshots underneath on a schedule.
"""

import argparse
import hashlib
import json
import shutil
import sqlite3
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE = Path.home() / ".sibyl-memory"
DEFAULT_DEST = REPO_ROOT / "backups"


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


# SQLite sidecar files that are meaningless without the live process.
_VOLATILE_SUFFIXES = ("-wal", "-shm", "-journal",
                      ".db-wal", ".db-shm", ".db-journal")


def _stable_copy(db_path: Path, workdir: Path) -> Path:
    """Checkpoint a live SQLite file into a standalone consistent copy.

    Uses the online backup API (crash-consistent, works while the store is
    open), so snapshots never need the app stopped. Falls back to a plain
    copy if the file isn't a readable SQLite database.
    """
    out = workdir / db_path.name
    try:
        src = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            dst = sqlite3.connect(out)
            try:
                src.backup(dst)
            finally:
                dst.close()
        finally:
            src.close()
        return out
    except Exception:
        shutil.copy2(db_path, out)
        return out


def _collect_members(source: Path, workdir: Path) -> list:
    """Return (arcname, real_path) pairs: checkpointed DBs, raw other files.

    Live -wal/-shm sidecars are excluded by design — the checkpointed copy
    already contains their committed data, and they cannot exist standalone
    (Windows refuses to even create orphan -shm files).
    """
    pairs = []
    for p in sorted(source.rglob("*")):
        if not p.is_file():
            continue
        arcname = p.relative_to(source).as_posix()
        if p.suffix == ".db":
            pairs.append((arcname, _stable_copy(p, workdir)))
        elif p.name.endswith(_VOLATILE_SUFFIXES):
            continue
        else:
            pairs.append((arcname, p))
    return pairs


def snapshot_sibyl(source_dir: Path | str = DEFAULT_SOURCE,
                   dest_dir: Path | str = DEFAULT_DEST) -> Path:
    """Snapshot a Sibyl store directory. Returns the archive path."""
    source, dest = Path(source_dir), Path(dest_dir)
    if not source.exists():
        raise FileNotFoundError(f"Sibyl store not found: {source}")
    dest.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    archive = dest / f"sibyl-snapshot-{stamp}.tar.gz"

    members = [p for p in sorted(source.rglob("*")) if p.is_file()]
    if not members:
        raise ValueError(f"Sibyl store is empty: {source}")

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        pairs = _collect_members(source, workdir)
        manifest_files = [
            {"name": arcname, "sha256": _sha256_file(real),
             "size": real.stat().st_size}
            for arcname, real in pairs
        ]
        manifest = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "source": str(source),
            "files": manifest_files,
        }
        manifest_path = workdir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        with tarfile.open(archive, "w:gz") as tar:
            for arcname, real in pairs:
                tar.add(real, arcname=arcname)
            tar.add(manifest_path, arcname="manifest.json")

    (archive.parent / (archive.name + ".sha256")).write_text(
        _sha256_file(archive) + f"  {archive.name}\n"
    )
    print(f"Snapshot: {len(members)} file(s) -> {archive}")
    return archive


def restore_sibyl(archive: Path | str, dest_dir: Path | str,
                  force: bool = False) -> Path:
    """Restore a snapshot after verifying integrity. Returns dest dir.

    The store process must be STOPPED first (or the destination must never
    have been opened live): restoring over an open SQLite database leaves
    stale WAL-index state that shadows the restored bytes on Windows.
    --force overwrites a quiesced non-empty directory, never a live one.
    """
    archive, dest = Path(archive), Path(dest_dir)
    if not archive.is_file():
        raise FileNotFoundError(f"Archive not found: {archive}")

    sidecar = archive.parent / (archive.name + ".sha256")
    if sidecar.exists():
        expected = sidecar.read_text().split()[0]
        actual = _sha256_file(archive)
        if actual != expected:
            raise ValueError(
                "Archive integrity check FAILED (tampered or corrupt). "
                "Refusing to restore."
            )

    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.iterdir()) and not force:
        raise ValueError(
            f"Destination {dest} is not empty. Re-run with --force to "
            "overwrite (destructive)."
        )

    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getnames()
        if "manifest.json" not in members:
            raise ValueError("Archive has no manifest.json. Refusing.")
        tar.extractall(dest, filter="data")
    try:
        manifest = json.loads((dest / "manifest.json").read_text())
        for entry in manifest["files"]:
            member = dest / entry["name"]
            if not member.is_file() or _sha256_file(member) != entry["sha256"]:
                raise ValueError(
                    f"Member integrity check FAILED: {entry['name']}. "
                    "Restored store is untrustworthy."
                )
    finally:
        # The manifest is the archive's record, not store data: never leave
        # it inside the live store (it would pollute future snapshots).
        try:
            (dest / "manifest.json").unlink(missing_ok=True)
        except TypeError:  # Python < 3.8 compat (missing_ok unavailable)
            manifest_path = dest / "manifest.json"
            if manifest_path.exists():
                manifest_path.unlink()
    print(f"Restored {len(manifest['files'])} file(s) -> {dest} (verified)")
    return dest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    snap = sub.add_parser("snapshot", help="Snapshot a Sibyl store")
    snap.add_argument("--source", default=str(DEFAULT_SOURCE))
    snap.add_argument("--dest", default=str(DEFAULT_DEST))
    rest = sub.add_parser("restore", help="Restore a snapshot")
    rest.add_argument("archive")
    rest.add_argument("--dest", default=str(DEFAULT_SOURCE))
    rest.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    if args.cmd == "snapshot":
        snapshot_sibyl(args.source, args.dest)
    else:
        restore_sibyl(args.archive, args.dest, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
