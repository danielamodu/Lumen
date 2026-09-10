"""Local .env loader for scripts and tests ONLY.

Production (Railway) injects environment variables directly; app runtime code
(api/server.py and everything it imports) must NEVER call this — it reads
os.environ only. Importing this module has no side effects; loading happens
only when load_local_env() is called explicitly.
"""

import os
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_local_env(path: Path | None = None) -> bool:
    """Load KEY=VALUE lines from .env (gitignored) with setdefault semantics.

    Returns True if the file existed. Never overwrites real environment values
    and never prints values (connection strings stay out of logs).
    """
    env_file = path or (_repo_root() / ".env")
    if not env_file.exists():
        return False
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        if key:
            os.environ.setdefault(key, value)
    return True
