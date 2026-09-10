"""Postgres (Neon) connection helper for Lumen system-state tables.

Scope: tenants, used_txs, webhooks + delivery outbox ONLY. Sibyl memory is
the source of truth for all intelligence; nothing here may cache patterns or
briefs in a way that survives deletion of the Sibyl store (see
tests/test_load_bearing.py).

Connection rules (per neon-postgres skill):
- App query traffic -> DATABASE_URL (pooled, `-pooler` hostname).
- Migrations/dumps/admin -> DATABASE_URL_UNPOOLED (direct, no `-pooler`).
"""

import os
from contextlib import contextmanager

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:  # pragma: no cover - surfaced clearly at call time
    psycopg = None
    dict_row = None


def _require_driver():
    if psycopg is None:
        raise RuntimeError(
            "psycopg is not installed. Run: pip install -r requirements.txt"
        )


def is_configured() -> bool:
    """True when a Postgres URL is available (Neon linked)."""
    return bool(os.environ.get("DATABASE_URL"))


def _dsn(unpooled: bool = False) -> str:
    if unpooled:
        dsn = os.environ.get("DATABASE_URL_UNPOOLED") or os.environ.get("DATABASE_URL")
    else:
        dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise RuntimeError(
            "DATABASE_URL is not set. Run `neon env pull` or copy it from "
            "the Neon dashboard into .env (gitignored)."
        )
    return dsn


@contextmanager
def get_conn(unpooled: bool = False):
    """Yield a Postgres connection (dict rows), closing it on exit.

    Short-lived connections by design: Neon pooler + scale-to-zero handle the
    pooling server-side; the app never holds idle connections open.
    """
    _require_driver()
    conn = psycopg.connect(_dsn(unpooled), row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
