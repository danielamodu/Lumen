"""One-time import of tenants.json rows into the Postgres tenants table.

Usage from the repo root:
    python scripts/import_tenants.py

Legacy rows keyed by RAW api key are hashed on the way in (raw secrets must
never land in Postgres). Rows already keyed by 64-hex hash pass through.
Existing rows win: INSERT ... ON CONFLICT DO NOTHING. Never prints keys.
Run once per environment, then keep tenants.json as a cold backup.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from api.env import load_local_env  # noqa: E402  (explicit, no side effects)

load_local_env(REPO_ROOT / ".env")

from api.auth import _load_tenants, hash_api_key  # noqa: E402
from api.db import get_conn  # noqa: E402

_HASHED_RE = re.compile(r"^[0-9a-f]{64}$")


def main() -> int:
    rows = _load_tenants()
    if not rows:
        print("tenants.json is empty or missing — nothing to import.")
        return 0

    imported, skipped = 0, 0
    with get_conn(unpooled=True) as conn:
        with conn.cursor() as cur:
            for key, info in rows.items():
                if _HASHED_RE.match(key):
                    key_hash = key
                else:
                    key_hash = hash_api_key(key)  # legacy raw key -> hash
                cur.execute(
                    "INSERT INTO tenants (key_hash, tenant_id, name, active) "
                    "VALUES (%s, %s, %s, %s) "
                    "ON CONFLICT (key_hash) DO NOTHING",
                    (
                        key_hash,
                        info.get("tenant_id", ""),
                        info.get("name", ""),
                        info.get("active", True),
                    ),
                )
                if cur.rowcount:
                    imported += 1
                else:
                    skipped += 1
    print(f"Done. Imported {imported} row(s), skipped {skipped} existing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
