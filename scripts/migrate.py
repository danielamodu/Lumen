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

from api.env import load_local_env  # noqa: E402  (explicit, no side effects)


def main() -> int:
    load_local_env(REPO_ROOT / ".env")
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
