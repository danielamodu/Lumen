# Lumen — project memory

## What this is
Lumen is an outcome-memory layer for AI agents (demo/competition project, not
production SaaS — prioritize demo evidence and load-bearing behavior over
hardening). Agents `record` outcomes and fetch `brief`s with learned patterns.
Tagline: "Your agents forget. Lumen remembers."

## Architecture
- **COLD tier**: append-only outcome journal (pipe-delimited `LUMEN|...` lines).
  `|` in free text is sanitized to `/` — never reintroduce raw pipes.
- **WARM tier**: per user:domain pattern entities (win/loss rates, avg signal).
- **HOT tier**: `brief()` output surfaced before acting.
- Substrate: Sibyl Memory (`sibyl-memory-client`), local file or Railway volume.
- Delete-test gate (load-bearing proof): fresh user → `pattern: None`; after a
  recorded outcome → pattern string. If this breaks, the memory is broken.

## Layout
- `api/server.py` — FastAPI app; `api/security.py` — rate limiting, sanitizing,
  SSRF guards, webhook signing; `api/auth.py` — tenant API keys (hashed at rest).
- `lumen/core.py`, `lumen/memory.py`, `lumen/payments.py` (Base mainnet USDC
  verification), `lumen/webhooks.py` (pattern-shift delivery, no redirects).
- `sdk/` — local `lumen_memory` client (editable install via `-e ./sdk`).
- `virtuals/` — G.A.M.E agent (`lumen_scout.py`, lazy agent build; standalone
  function test needs no credits) + `lumen_functions.py`.
- `frontend/` — Next.js 14 landing + `/live` console. No `dangerouslySetInnerHTML`;
  React escapes at render, so API text must stay unescaped (no `html.escape`).
- `tests/` — `test_core.py`, `test_security.py`; SDK tests under `sdk/tests/`.

## Environment
- `LUMEN_DEMO_KEY` (public demo credential), `LUMEN_ADMIN_KEY` (unset = admin
  endpoints disabled), `LUMEN_WEBHOOK_SECRET` (unset = ephemeral per-process
  secret), `LUMEN_FORCE_HTTPS`, `LUMEN_TRUST_PROXY_DEPTH` (0 = direct peer IP),
  `LUMEN_RATE_LIMIT`, `GAME_API_KEY` (Scout only).
- Live: API `https://lumen-memory-production.up.railway.app`,
  frontend `https://lumen-frontend-production-06e5.up.railway.app`.

## Gotchas (learned the hard way)
- `requirements.txt`: `web3>=6.20,<8` (range, NOT exact — an exact old pin
  forces source builds of `ckzg`/`lru-dict` with no py3.13 wheels, failing
  without MSVC); `game-sdk==0.1.5` (Scout shims tuned to it); pytest `<10`.
  Run pip from the repo root so `-e ./sdk` resolves.
- `railway.json`/root `Dockerfile` start `python api/server.py`, so
  `railway up --service lumen-frontend` deploys the API into that slot — the
  Next.js site needs its own service config (root dir `frontend`).
- Shell is Windows PowerShell 5.1: one command per line, no `&&` chaining,
  no `head`/`grep` (use tool equivalents).
