# Lumen — Hackathon Submission

### Memory Load-Bearing (40 points)

When Sibyl memory is deleted via `python demo/wipe.py`, the intelligence of the entire system collapses into complete blindness. Without the **COLD** journal, raw historical evidence is eliminated; without the **WARM** pattern tier, win rates and negative constraint heuristics vanish; without the **HOT** session cache, pre-turn briefing fails. When `brief()` is queried post-wipe, it returns `warning: None`, `pattern: None`, and `cross_domain: None`. The Pitch, Post, and Ask agents lose all historical adaptation, reverting to unguided stochastic guesses and repeating known failure modes. This failure is deterministic and verifiable in under 60 seconds via `demo/wipe.py` and `demo/loop_demo.py`, proving that memory in Lumen is not decorative logging or transient caching, but the fundamental load-bearing engine of agent competence.

### Innovation (25 points)

Lumen is not a vertical agent; it is a horizontal outcome memory primitive that sits beneath any agent framework. While most agent implementations treat memory as a chat log, vector similarity store, or episodic scratchpad, Lumen focuses strictly on empirical outcome learning: tracking what was tried, what result occurred, and whether it won or lost. The core structural breakthrough is cross-domain behavioral synthesis: because all domain operations resolve to a unified `user` entity within Sibyl memory, successful patterns established in one domain (such as the Ask agent discovering that providing context produces a 70% win rate) are automatically surfaced to completely separate agents (such as the Pitch agent). Cross-domain learning across distinct agents without custom point-to-point wiring is structurally impossible without a unified, typed memory substrate like Sibyl.

Lumen integrates with Virtuals Protocol G.A.M.E framework as a drop-in memory function set. Any G.A.M.E agent adds persistent outcome learning with two lines of code. Lumen Scout demonstrates this — a G.A.M.E agent that consults Lumen memory before every action and records outcomes after. Its memory functions are verified standalone (no credits needed); the live agent run awaits GAME compute credits, and the Scout waits gracefully until they land. The memory is load-bearing either way: Lumen Scout without Sibyl memory has no patterns, no warnings, no cross-domain insights. It goes blind.

### Technical Execution (20 points)

Lumen delivers an end-to-end technical implementation verified across all layers: 47 passing pytest tests (+5 memory-quality evals) covering journal persistence, pattern recalculation, negative warning heuristics, cross-domain inference, the automated delete-Sibyl blindness contract, snapshot/restore drills, Postgres-backed tenants/payments/webhooks, and fail-closed mode; a FastAPI backend with 14 endpoints (`/brief`, `/record`, `/market/brief`, `/market/domains`, `/webhooks`, `/tenants/*`, `/memory/*`, `/wipe`, `/seed`, `/demo/step`, `/health`) featuring strict Pydantic validation, rate limiting, and security headers; measured memory quality (pattern/warning precision 1.00 on separable histories, obey-the-brief policy beats random choice 1.00 vs 0.51); a Neon Postgres layer for system state with Sibyl kept as the sole source of truth; an editorial Next.js 14 frontend with Tailwind CSS, custom design tokens, and real-time reactive brief cards; three live Google Antigravity agents autonomously reading and updating memory; and a one-command, judge-ready extinction demo (`python demo/delete_test.py`, plus `--hard` fail-closed mode with HTTP 503s) that proves the load-bearing delete test end-to-end with sight-for-sight resurrection from snapshot.

### Pitch (15 points)

Lumen is the memory primitive that turns any stateless agent into one that compounds competence over time.

### PMF Bonus (10 points)

Lumen directly serves the solo builder — early-stage founders, technical freelancers, and independent creators — who continuously make high-stakes communication and operational decisions across pitching investors, publishing public content, and conducting cold outreach. Today, these builders repeat costly tactical mistakes because their AI tooling operates in silos with zero empirical feedback: an agent writes an email or deck, the pitch fails, and the next session starts from blank ignorance. Every pitch, post, and ask creates a concrete empirical outcome signal that is currently discarded; Lumen captures these signals, distills them into actionable behavioral constraints, and acts as an autonomous learning mirror that makes the user and their agents sharper with every interaction.

### Base Integration

Lumen implements real onchain USDC payment verification on Base mainnet (chain ID 8453). The /market/brief endpoint returns HTTP 402 with payment details when called without proof. Agents send 0.01 USDC to 0xf821447c6bd7c54e5fc2bd92239f4d8ed73c52f0 on Base mainnet, pass the transaction hash as X-Payment-Proof, and the server verifies onchain via the Base RPC:

1. Transaction exists and is confirmed
2. Contains a USDC Transfer event to our wallet
3. Amount >= 0.01 USDC
4. Transaction is < 1 hour old
5. Transaction hash not previously used (replay protection)

This is not simulated. The verification calls https://mainnet.base.org and reads the actual transaction receipt. Any agent on any framework can participate in the Lumen pattern market by paying 0.01 USDC on Base mainnet.

