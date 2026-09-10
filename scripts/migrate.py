"""Run SQL migrations against Neon using the DIRECT (unpooled) URL.

Usage from the repo root:
    python scripts/migrate.py

Reads .env (gitignored) for DATABASE_URL_UNPOOLED, falling back to
DATABASE_URL. Never prints connection strings. Idempotent: the SQL files use
CREATE TABLE IF NOT EXISTS, so re-running is safe.
"""

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (no new dependency): KEY=VALUE lines only."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        os.environ.setdefault(key, value)


def main() -> int:
    _load_dotenv(REPO_ROOT / ".env")
    from api.db import get_conn

    migrations_dir = REPO_ROOT / "migrations"
    files = sorted(migrations_dir.glob("*.sql"))
    if not files:
        print("No migration files found in migrations/.")
        return 1

    # Direct URL for DDL per neon-postgres skill (falls back gracefully).
    os.environ["LUMEN_MIGRATE_DIRECT"] = "1"
    with get_conn(unpooled=True) as conn:
        with conn.cursor() as cur:
            for path in files:
                print(f"Applying {path.name} ...")
                cur.execute(path.read_text())
    print(f"Done. Applied {len(files)} migration file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
