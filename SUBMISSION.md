# Lumen — Hackathon Submission

### Memory Load-Bearing (40 points)

When Sibyl memory is deleted via `python demo/wipe.py`, the intelligence of the entire system collapses into complete blindness. Without the **COLD** journal, raw historical evidence is eliminated; without the **WARM** pattern tier, win rates and negative constraint heuristics vanish; without the **HOT** session cache, pre-turn briefing fails. When `brief()` is queried post-wipe, it returns `warning: None`, `pattern: None`, and `cross_domain: None`. The Pitch, Post, and Ask agents lose all historical adaptation, reverting to unguided stochastic guesses and repeating known failure modes. This failure is deterministic and verifiable in under 60 seconds via `demo/wipe.py` and `demo/loop_demo.py`, proving that memory in Lumen is not decorative logging or transient caching, but the fundamental load-bearing engine of agent competence.

### Innovation (25 points)

Lumen is not a vertical agent; it is a horizontal outcome memory primitive that sits beneath any agent framework. While most agent implementations treat memory as a chat log, vector similarity store, or episodic scratchpad, Lumen focuses strictly on empirical outcome learning: tracking what was tried, what result occurred, and whether it won or lost. The core structural breakthrough is cross-domain behavioral synthesis: because all domain operations resolve to a unified `user` entity within Sibyl memory, successful patterns established in one domain (such as the Ask agent discovering that providing context produces a 70% win rate) are automatically surfaced to completely separate agents (such as the Pitch agent). Cross-domain learning across distinct agents without custom point-to-point wiring is structurally impossible without a unified, typed memory substrate like Sibyl.

### Technical Execution (20 points)

Lumen delivers an end-to-end, production-grade technical implementation verified across all layers: 5 automated pytest unit tests covering journal persistence, pattern recalculation, negative warning heuristics, cross-domain inference, and wipe guarantees with 100% passing results; a high-concurrency FastAPI backend with 5 endpoints (`/brief`, `/record`, `/wipe`, `/seed`, `/demo/step`) featuring strict Pydantic validation and CORS configuration; an editorial Next.js 14 frontend built with Tailwind CSS, custom design tokens, and real-time reactive brief cards; three live Google Antigravity agents autonomously reading and updating memory; and an automated, zero-input demonstration script (`demo/loop_demo.py`) that visually proves real-time pattern shifts and the load-bearing delete test.

### Pitch (15 points)

Lumen is the memory primitive that turns any stateless agent into one that compounds competence over time.

### PMF Bonus (10 points)

Lumen directly serves the solo builder — early-stage founders, technical freelancers, and independent creators — who continuously make high-stakes communication and operational decisions across pitching investors, publishing public content, and conducting cold outreach. Today, these builders repeat costly tactical mistakes because their AI tooling operates in silos with zero empirical feedback: an agent writes an email or deck, the pitch fails, and the next session starts from blank ignorance. Every pitch, post, and ask creates a concrete empirical outcome signal that is currently discarded; Lumen captures these signals, distills them into actionable behavioral constraints, and acts as an autonomous learning mirror that makes the user and their agents sharper with every interaction.

### Base Integration

Lumen is an active on-chain intelligence market built on Base. In Phase 12, the x402 HTTP Payment Required standard was implemented and deployed live: agents query `/market/brief` to access cross-user aggregate patterns and receive an HTTP 402 with USDC-on-Base payment requirements (`0.01 USDC`). Upon providing payment proof via the `X-Payment-Proof` header, the server returns verified cross-user winning heuristics, sample size, and contributor counts. This turns Lumen from a private memory layer into an autonomous intelligence market on Base, where agents pay for collective competence and contributors earn protocol rewards without requiring human intervention.
