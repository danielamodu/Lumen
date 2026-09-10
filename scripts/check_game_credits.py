"""Check GAME API key status without spending compute.

The free-credits issue ("accepted but not reflecting") can be key-side
(wrong/revoked key) or account-side (credits not attached). This script hits
only the token exchange — authentication, zero compute — and reports exactly
which one it is. Run locally with your key set:

    $env:GAME_API_KEY = '<your key>'   # PowerShell (this session only)
    python scripts/check_game_credits.py

The key is NEVER printed (only first/last 4 chars) and never leaves your
machine. Send the printed verdict (not the key) to the Virtuals team.
"""

import os
import sys

import requests

TOKEN_URL = "https://api.virtuals.io/api/accesses/tokens"


def _mask(key: str) -> str:
    if len(key) <= 10:
        return "***"
    return f"{key[:4]}...{key[-4:]} (len {len(key)})"


def main() -> int:
    key = os.environ.get("GAME_API_KEY", "").strip()
    if not key:
        print("GAME_API_KEY is not set in this session.")
        print("Set it first:  $env:GAME_API_KEY = '<your key>'")
        return 2
    print(f"Key present: {_mask(key)}")

    try:
        response = requests.post(
            TOKEN_URL,
            json={"data": {}},
            headers={"x-api-key": key},
            timeout=20,
        )
    except Exception as exc:
        print(f"NETWORK ERROR: could not reach the GAME API: "
              f"{type(exc).__name__}: {exc}")
        return 1

    body = response.text[:300].replace(key, "***")
    print(f"Token endpoint -> HTTP {response.status_code}")
    print(f"Response (truncated): {body}")

    if response.status_code == 200:
        try:
            token = response.json()["data"]["accessToken"]
        except Exception:
            token = ""
        if token:
            print()
            print("VERDICT: KEY VALID — the key authenticates (token "
                  "issued). If agent runs still fail on credits/quota, the "
                  "free compute was not attached to THIS key's account. "
                  "Tell the team: 'token exchange returns 200 but runs "
                  "report insufficient credits', plus the exact run error "
                  "from python virtuals/lumen_scout.py.")
            return 0
    print()
    print(f"VERDICT: KEY REJECTED — HTTP {response.status_code} with no "
          "usable token (a dummy key also gets a non-200 here). The key is "
          "invalid, revoked, or belongs to a different account than the "
          "accepted application. Fix is on your side: copy the key fresh "
          "from https://console.game.virtuals.io (the accepted account) "
          "and retry. No team ticket needed yet.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
