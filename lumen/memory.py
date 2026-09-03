"""Memory client configuration and initialization for Lumen."""

from sibyl_memory_client import MemoryClient

_client = None


def _optimize_sqlite(client):
    """Enable SQLite WAL journal mode and normal synchronous mode for fast transactions."""
    if client is not None and hasattr(client, "_storage") and hasattr(client._storage, "connection"):
        try:
            with client._storage.connection() as conn:
                conn.execute("PRAGMA journal_mode = WAL;")
                conn.execute("PRAGMA synchronous = NORMAL;")
        except Exception:
            pass
    return client


def get_client(path=None):
    """Return the active MemoryClient instance or initialize one with the given path.

    If path is provided, initializes and sets a new MemoryClient instance for that path.
    If no client exists yet, initializes the default client at ~/.sibyl-memory/lumen_demo.db.
    """
    global _client
    if path:
        if _client is not None and hasattr(_client, "_storage") and hasattr(_client._storage, "close"):
            try:
                _client._storage.close()
            except Exception:
                pass
        _client = _optimize_sqlite(MemoryClient.local(path))
    if _client is None:
        _client = _optimize_sqlite(MemoryClient.local("~/.sibyl-memory/lumen_demo.db"))
    return _client
