"""Wipe script to demonstrate load-bearing nature of Sibyl memory."""

import glob
import os
from pprint import pprint
from lumen.core import brief
from lumen.memory import get_client


def run_wipe():
    """Delete the Sibyl database file, reinitialize, and verify brief returns empty state."""
    db_path = os.path.normpath(os.path.expanduser("~/.sibyl-memory/lumen_demo.db"))

    client = get_client()
    if client is not None and hasattr(client, "_storage") and hasattr(client._storage, "close"):
        try:
            client._storage.close()
        except Exception:
            pass

    # 1. Delete DB file and any auxiliary SQLite files
    for f in glob.glob(db_path + "*"):
        try:
            os.remove(f)
        except OSError:
            pass

    # 2. Reinitialize empty client
    get_client(path=db_path)

    # 3. Call brief after wipe
    result = brief("alex", "pitch", "about to pitch a crypto fund today")

    # 4. Print result
    print("=== BRIEF AFTER WIPE ===")
    pprint(result)
    return result


if __name__ == "__main__":
    run_wipe()
