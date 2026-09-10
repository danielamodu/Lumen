# Lumen
**Outcome Memory Layer for AI Agents**

> The primitive that makes any agent learn from experience —  
> not fine-tuning, not RAG. Just memory.

Powered by [Sibyl Memory](https://sibyllabs.org) · Built on Base

---

### The Problem

Agents today are stateless reasoners. They can be brilliant in a single session and make the identical mistake the next day because nothing persisted. The standard fix — bigger context windows, RAG, fine-tuning — addresses retrieval, not learning. Lumen addresses learning.

---

### What Lumen Does

Lumen is a backend primitive. Any agent writes outcomes to it and reads learned patterns from it. The agent gets smarter. The human gets a mirror.

---

## The Delete Test

The hackathon requires: delete the memory layer and the product must stop working.

Run this (one command, full extinction-and-resurrection arc through the real API):

```bash
python demo/delete_test.py          # blind-but-200: all-None briefs, void records
python demo/delete_test.py --hard   # fail-closed: 503 on every memory endpoint
```

What breaks (both modes):
- brief() returns warning: None, pattern: None, cross_domain: None for every domain
- The three agents have no learned patterns — they open every session identically regardless of past outcomes
- Cross-domain learning collapses entirely — the Ask domain's 70% win rate cannot inform the Pitch domain because there is no unified user entity to link them
- The automated demo sequence produces empty state at every step
- `--hard` goes further: `/brief`, `/record` and `/market/brief` answer HTTP 503
  ("Sibyl memory missing or empty") — the product refuses, not just degrades

What does NOT break:
- The FastAPI server still runs (`/health` answers)
- The Next.js frontend still loads
- In soft mode, record() still writes events

But those writes have nowhere to learn from. The loop is broken. Without Sibyl memory, Lumen is a logging tool. With it, Lumen learns. Restore the snapshot and every pattern returns sight-for-sight.

(Manual version: `python demo/wipe.py` wipes the local store; `python demo/seed.py` + `python demo/loop_demo.py` show the loop.)

---

## Why Not Just Use Postgres?

A competent Postgres schema could replicate Sibyl's individual properties:
- UNIQUE constraint on entities
- Append-only journal via insert-only triggers
- Typed cross-references via foreign keys

What it cannot replicate in this context:
- The opinionated tier schema (HOT/WARM/COLD) that enforces session bridging by convention across every agent without custom engineering
- The MCP server that lets any Claude-based agent read and write memory without a custom integration layer
- The cross-tenant isolation that makes multi-user memory safe by default

Lumen was built in 10 days. Postgres would have taken 3 of those days to architect correctly. Sibyl gave us the right schema on day one.

---

### Architecture

```
┌─────────────────────────────────────────────┐
│                 LUMEN CORE                  │
│                                             │
│ record(user, domain, action, outcome, sig)  │
│ brief(user, domain, context)                │
│                                             │
│ ┌─────────────────────────────────────────┐ │
│ │              SIBYL MEMORY               │ │
│ │                                         │ │
│ │ COLD → outcome journal                  │ │
│ │ WARM → learned patterns                 │ │
│ │ HOT  → session briefing cache           │ │
│ │ REF  → domain rules                     │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
       ↑                     ↑             ↑
  Pitch Agent            Post Agent    Ask Agent
 (Antigravity)          (Antigravity) (Antigravity)
       ↑                     ↑             ↑
┌─────────────────────────────────────────────┐
│             FastAPI · port 8000             │
│ /brief /record /market/brief /webhooks      │
│ /tenants /memory/events /memory/patterns    │
│ /wipe /seed /demo/step /health              │
└─────────────────────────────────────────────┘
                       ↑
┌─────────────────────────────────────────────┐
│          Next.js Frontend · port 3000       │
│     Brief Panels · Outcome Recorder ·       │
│      Watch Lumen Learn · Wipe Panel         │
└─────────────────────────────────────────────┘
```

---

### How The Memory Loop Works

1. **record()** — An agent reports what it tried and what happened. One COLD journal entry is written. `_recalculate_patterns()` reads all COLD entries for that user+domain and updates the WARM pattern entity. Single source of truth enforced by Sibyl's UNIQUE constraint.

2. **brief()** — Before acting, an agent calls `brief()`. Lumen reads the WARM pattern entity, checks other domains for the same user entity, constructs a cross-domain insight if >= 3 outcomes exist in other domains, writes the result to HOT state, and returns a structured dict. The agent's behavior changes based on what memory says.

3. **The cross-domain moment** — All outcomes across all agents resolve to the same WARM user entity in Sibyl memory. When the Ask agent records a win, the Pitch agent's next brief surfaces that win as a cross-domain insight. This is structurally impossible without a unified entity store. This is what Sibyl enables.

---

### Demo Agents

- **Pitch** — helps frame investment pitches. Learns which opening strategies win meetings vs get ghosted.
- **Post** — helps craft content hooks. Learns which formats drive engagement vs silence.
- **Ask** — helps frame requests and cold outreach. Learns which context-setting approaches get responses.

Each agent calls `brief()` before acting and `record()` after outcome. Each agent is independently dumb. Together, through shared Sibyl memory, they build a unified model of what works for this specific user.

**Any domain works.** Lumen is not limited to pitch, post, and ask. Any agent can define its own domain string:

```python
lumen.record(
    user_id="alex",
    domain="code_review",
    action="reviewed PR without running tests",
    outcome="missed a bug in production",
    signal=-1
)
```

The pattern learning works identically regardless of domain.

---

## Live API

The Lumen API is live at:
https://lumen-memory-production.up.railway.app

```python
# Use immediately — no setup required
from lumen_memory import Lumen
lumen = Lumen()  # connects to live API by default
```

Or hit the API directly:
```bash
curl -X POST https://lumen-memory-production.up.railway.app/brief \
  -H "Content-Type: application/json" \
  -H "X-Lumen-Key: lmn_demo0000000000000000000000000000" \
  -d '{"user_id":"you","domain":"pitch",
       "context":"about to pitch"}'
```

---

### Quickstart

```bash
# Clone and install
git clone https://github.com/danielamodu/Lumen.git
cd Lumen
pip install -r requirements.txt
pip install -e ./sdk          # lumen_memory client SDK (SDK examples + Virtuals agent)

# Seed 33 demo outcomes
python demo/seed.py

# Run the automated demo sequence
python demo/loop_demo.py

# Start the API
python api/server.py

# Start the frontend (separate terminal)
cd frontend && npm install && npm run dev

# Run a live agent session
python agents/pitch_agent.py

# Run tests
pytest tests/ -v
```

---

### Stack

- **Memory:** Sibyl Memory (sibyl-memory-client==0.8.0)
- **Agents:** Antigravity (Google Gemini)
- **API:** FastAPI + Uvicorn
- **Frontend:** Next.js 14 + Tailwind CSS
- **Chain:** Base mainnet — live on-chain USDC payment verification gating `/market/brief` (x402-style 402 flow, chain ID 8453, replay-protected)
- **Language:** Python 3.10+

---

### What's Next

- **Cross-user pattern market** — the paid `/market/brief` endpoint with on-chain USDC settlement on Base (x402-style) is already live; next is scaling it to many contributors so agents can price and trade each other's learned patterns.
- **Virtuals Protocol** — Lumen as a shared memory substrate for Virtuals agent swarms. Every agent in the swarm learns from every other agent's outcomes.
- **Pattern confidence scoring** — weight recent outcomes more heavily than old ones. Memory that forgets gracefully.

---

## The Market

Lumen is not just personal memory. It's a network.

Every outcome recorded by every agent contributes to aggregate patterns. Any agent can query what works across all users for a domain — and pay for that intelligence in USDC on Base.

```bash
# Demo mode — skips real settlement (real tx-hash path shown below)
curl -X POST \
  https://lumen-memory-production.up.railway.app/market/brief \
  -H "Content-Type: application/json" \
  -H "X-Lumen-Key: lmn_demo0000000000000000000000000000" \
  -H "X-Payment-Proof: demo_payment_proof_base_usdc" \
  -d '{"domain":"pitch","context":"pitching crypto funds"}'
```

Response:
```json
{
  "aggregate_win_rate": 0.54,
  "top_winning_actions": [
    "led with their problem",
    "opened with the pain point",
    "started with their context"
  ],
  "sample_size": 33,
  "contributors": 1,
  "payment": {
    "amount_paid": "0.01",
    "currency": "USDC",
    "network": "base"
  }
}
```

**Real payment (on-chain verification).** Send 0.01 USDC on Base mainnet to `0xf821447c6bd7c54e5fc2bd92239f4d8ed73c52f0`, then pass the transaction hash as the proof. Lumen verifies the transfer amount, recipient, and age on-chain (Base mainnet, chain ID 8453) and rejects reused hashes:

```bash
curl -X POST \
  https://lumen-memory-production.up.railway.app/market/brief \
  -H "Content-Type: application/json" \
  -H "X-Lumen-Key: lmn_demo0000000000000000000000000000" \
  -H "X-Payment-Proof: 0x<your_base_usdc_tx_hash>" \
  -d '{"domain":"pitch","context":"pitching crypto funds"}'
```

With no `X-Payment-Proof` header at all, the endpoint returns HTTP 402 with full payment instructions (recipient, USDC contract, chain ID) — a real x402-style paywall.

The x402 payment standard means any agent can participate in this market autonomously — no human required to approve the transaction.

---

## Virtuals Protocol Integration

Lumen is available as a G.A.M.E function set for any 
Virtuals Protocol agent.

```bash
pip install game-sdk==0.1.5  # the version Lumen Scout was tested against
pip install -e ./sdk         # local lumen_memory client SDK (this repo)
```

```python
from game_sdk.game.worker import Worker
from virtuals.lumen_functions import LUMEN_GAME_FUNCTIONS

worker = Worker(
    api_key=GAME_API_KEY,
    description="An agent with persistent outcome memory.",
    action_space=LUMEN_GAME_FUNCTIONS
)
```

Any G.A.M.E agent with LUMEN_GAME_FUNCTIONS in its 
action space can:
- Call get_lumen_brief before acting
- Call record_lumen_outcome after acting
- Get cross-domain insights from shared Sibyl memory
- Get smarter with every session

Lumen Scout — a demo G.A.M.E agent powered by Lumen 
memory — is in virtuals/lumen_scout.py.
