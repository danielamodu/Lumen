# Lumen — Hackathon Submission

### The entrant

The entrant is an agent ensemble (Pitch, Post, Ask, plus Lumen Scout on
Virtuals G.A.M.E.) that recalls and acts through one Sibyl-backed memory.
Every claim below is runnable — nothing is asserted without a command.

### Memory Load-Bearing (40 points)

The decision changes because of memory — read this first:

- WITHOUT memory (fresh user, no history): the agent guesses. Brief returns
  `warning: None, pattern: None`, confidence "0 outcomes recorded."
- WITH memory (same user, 12 recorded outcomes): the brief commands
  "High win rate (100%) when you 'opened with their problem'" and warns off
  the 40%-loss opener. The agent's next action differs.
- Measured: a policy that obeys the brief wins 1.00 vs 0.51 for random
  choice (margin +0.49, `pytest evals/ -v -s`). Pattern/warning precision
  1.00 on separable histories, 1.00 with noise injected.

Then the extinction proof: when Sibyl memory is deleted via
`python demo/delete_test.py` (`--hard` for fail-closed HTTP 503s), the
intelligence of the entire system collapses into complete blindness. Without
the **COLD** journal, raw historical evidence is eliminated; without the
**WARM** pattern tier, win rates and negative constraint heuristics vanish;
without the **HOT** session cache, pre-turn briefing fails. When `brief()`
is queried post-wipe, it returns `warning: None`, `pattern: None`, and
`cross_domain: None`. The Pitch, Post, and Ask agents lose all historical
adaptation, reverting to unguided stochastic guesses and repeating known
failure modes. Restore the snapshot and every pattern returns sight-for-sight
(pattern equality asserted, not eyeballed).

Fresh sessions, not fixtures: every test and demo opens a new client against
the store (the restart equivalent — no in-process state survives; proven by
`test_patterns_come_from_store_not_process`). Reproduce the whole arc in
under 60 seconds: `python demo/delete_test.py --hard`.

This failure is deterministic and automated. Memory in Lumen is not
decorative logging or transient caching, but the fundamental load-bearing
engine of agent competence.

### Partner stacks claimed: Base only (x1.15)

One verified stack is claimed: **Base** — the `/market/brief` endpoint
verifies real USDC transfers against Base mainnet receipts on every call
(recipient, amount, 1-hour freshness, replay protection), exercised end to
end in `tests/test_payments_pg.py` including a two-thread single-winner
replay race. **Virtuals is deliberately NOT claimed as a second stack:**
Lumen Scout's memory functions are verified standalone, but the live agent
run awaits GAME compute credits, and an unrun integration must not count.
Claiming x1.15 honestly beats risking x1.25 on an unrun stack.

### Innovation (25 points)

Lumen is not a vertical agent; it is a horizontal outcome memory primitive that sits beneath any agent framework. While most agent implementations treat memory as a chat log, vector similarity store, or episodic scratchpad, Lumen focuses strictly on empirical outcome learning: tracking what was tried, what result occurred, and whether it won or lost. The core structural breakthrough is cross-domain behavioral synthesis: because all domain operations resolve to a unified `user` entity within Sibyl memory, successful patterns established in one domain (such as the Ask agent discovering that providing context produces a 70% win rate) are automatically surfaced to completely separate agents (such as the Pitch agent). Cross-domain learning across distinct agents without custom point-to-point wiring is structurally impossible without a unified, typed memory substrate like Sibyl.

Lumen integrates with Virtuals Protocol G.A.M.E framework as a drop-in memory function set. Any G.A.M.E agent adds persistent outcome learning with two lines of code. Lumen Scout demonstrates this — a G.A.M.E agent that consults Lumen memory before every action and records outcomes after. Its memory functions are verified standalone (no credits needed); the live agent run awaits GAME compute credits, and the Scout waits gracefully until they land. The memory is load-bearing either way: Lumen Scout without Sibyl memory has no patterns, no warnings, no cross-domain insights. It goes blind.

### Technical Execution (20 points)

Lumen delivers an end-to-end technical implementation verified across all layers: 47 passing pytest tests (+5 memory-quality evals) covering journal persistence, pattern recalculation, negative warning heuristics, cross-domain inference, the automated delete-Sibyl blindness contract, snapshot/restore drills, Postgres-backed tenants/payments/webhooks, and fail-closed mode; a FastAPI backend with 14 endpoints (`/brief`, `/record`, `/market/brief`, `/market/domains`, `/webhooks`, `/tenants/*`, `/memory/*`, `/wipe`, `/seed`, `/demo/step`, `/health`) featuring strict Pydantic validation, rate limiting, and security headers; measured memory quality (pattern/warning precision 1.00 on separable histories, obey-the-brief policy beats random choice 1.00 vs 0.51); a Neon Postgres layer for system state with Sibyl kept as the sole source of truth; an editorial Next.js 14 frontend with Tailwind CSS, custom design tokens, and real-time reactive brief cards; three live Google Antigravity agents autonomously reading and updating memory; and a one-command, judge-ready extinction demo (`python demo/delete_test.py`, plus `--hard` fail-closed mode with HTTP 503s) that proves the load-bearing delete test end-to-end with sight-for-sight resurrection from snapshot.

### Pitch (15 points)

Lumen is the memory primitive that turns any stateless agent into one that compounds competence over time.

### PMF Bonus (10 points)

Lumen directly serves the solo builder — early-stage founders, technical freelancers, and independent creators — who continuously make high-stakes communication and operational decisions across pitching investors, publishing public content, and conducting cold outreach. This is the builder we designed for (no traction claimed): today, these builders repeat costly tactical mistakes because their AI tooling operates in silos with zero empirical feedback: an agent writes an email or deck, the pitch fails, and the next session starts from blank ignorance. Every pitch, post, and ask creates a concrete empirical outcome signal that is currently discarded; Lumen captures these signals, distills them into actionable behavioral constraints, and acts as an autonomous learning mirror that makes the user and their agents sharper with every interaction.

### Base Integration

Lumen implements real onchain USDC payment verification on Base mainnet (chain ID 8453). The /market/brief endpoint returns HTTP 402 with payment details when called without proof. Agents send 0.01 USDC to 0xf821447c6bd7c54e5fc2bd92239f4d8ed73c52f0 on Base mainnet, pass the transaction hash as X-Payment-Proof, and the server verifies onchain via the Base RPC:

1. Transaction exists and is confirmed
2. Contains a USDC Transfer event to our wallet
3. Amount >= 0.01 USDC
4. Transaction is < 1 hour old
5. Transaction hash not previously used (replay protection)

This is not simulated. The verification calls https://mainnet.base.org and reads the actual transaction receipt. Any agent on any framework can participate in the Lumen pattern market by paying 0.01 USDC on Base mainnet.

