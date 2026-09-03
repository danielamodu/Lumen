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

Run this:
```bash
python demo/wipe.py
```

What breaks:
- brief() returns warning: None, pattern: None, cross_domain: None for every domain
- The three agents have no learned patterns — they open every session identically regardless of past outcomes
- Cross-domain learning collapses entirely — the Ask domain's 70% win rate cannot inform the Pitch domain because there is no unified user entity to link them
- The automated demo sequence produces empty state at every step

What does NOT break:
- The FastAPI server still runs
- The Next.js frontend still loads
- record() still writes events

But those writes have nowhere to learn from. The loop is broken. Without Sibyl memory, Lumen is a logging tool. With it, Lumen learns.

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
│    /brief  /record  /wipe  /seed  /demo/step│
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

### Quickstart

```bash
# Clone and install
git clone https://github.com/danielamodu/Lumen.git
cd Lumen
pip install -r requirements.txt

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
- **Chain:** Base (x402 payment layer — roadmap)
- **Language:** Python 3.10+

---

### What's Next

- **x402 integration** — expose `/brief` as a paid endpoint on Base. Agents pay USDC to query another user's learned patterns. Cross-user learning as a market.
- **Virtuals Protocol** — Lumen as a shared memory substrate for Virtuals agent swarms. Every agent in the swarm learns from every other agent's outcomes.
- **Pattern confidence scoring** — weight recent outcomes more heavily than old ones. Memory that forgets gracefully.
