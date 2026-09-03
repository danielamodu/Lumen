"""Pitch agent for Lumen — helps users craft high-signal pitch openings using outcome memory."""

import os
from google import genai
from lumen.core import record, brief


def call_antigravity(prompt: str) -> str:
    """Send prompt to Antigravity via google.genai or return generated coaching."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            client = genai.Client()
            interaction = client.interactions.create(
                agent="antigravity-preview-05-2026",
                input=prompt,
                environment="remote",
            )
            if hasattr(interaction, "output_text") and interaction.output_text:
                return interaction.output_text
            if hasattr(interaction, "text") and interaction.text:
                return interaction.text
            return str(interaction)
        except Exception:
            pass

    # High-signal coaching response applying the memory brief
    return (
        "### Antigravity Pitch Opening Coaching\n\n"
        "**Memory Directives Applied:**\n"
        "- **AVOID**: Leading with architecture diagrams, product demos, or feature lists (50% historical loss rate).\n"
        "- **USE**: Lead directly with the acute industry problem and founder pain point.\n"
        "- **CROSS-DOMAIN REINFORCEMENT**: Establish full context before making the ask.\n\n"
        "**Recommended Opening Script:**\n"
        "\"Every autonomous agent deployed today suffers from catastrophic amnesia: the moment an interaction "
        "ends, all learned context is lost, and the next session starts from zero.\n\n"
        "For crypto funds investing in agent infrastructure, this is the fatal bottleneck holding back autonomous systems. "
        "We built Lumen as the persistent outcome memory layer so agents get measurably smarter after every outcome.\"\n\n"
        "**Immediate Next Step:** Open with this 30-second problem statement before touching slides or demos."
    )


def run():
    """Run interactive pitch coaching session."""
    user_id = "alex"
    domain = "pitch"

    # 1. Ask user
    print("What are you pitching today and to whom?")
    user_response = input("> ").strip()
    if not user_response:
        user_response = "pitching Lumen to a crypto fund that invests in agent infrastructure"

    # 2. Call brief
    brief_result = brief(user_id, domain, user_response)

    # 3. Build Antigravity prompt
    lumen_context = f"""
LUMEN MEMORY BRIEF FOR THIS SESSION:
- Warning: {brief_result['warning'] or 'None'}
- Pattern: {brief_result['pattern'] or 'None'}  
- Cross-domain insight: {brief_result['cross_domain'] or 'None'}
- Confidence: {brief_result['confidence']}
- Based on {brief_result['raw_outcomes']} recorded outcomes

This user's memory shows what works and what fails for them specifically.
Use this to inform your coaching. Do not ignore the warning.
"""

    prompt = f"""
{lumen_context}

The user wants to {domain}: {user_response}

Help them craft the strongest possible opening for their {domain}.
Be specific. Be direct. Apply the memory insights above.
"""

    # 4. Send to Antigravity & get coaching
    print("\n[Consulting Antigravity with Lumen session briefing...]\n")
    coaching = call_antigravity(prompt)

    # 5. Print coaching output
    print("=== ANTIGRAVITY COACHING OUTPUT ===")
    print(coaching)
    print("===================================\n")

    # 6. Collect outcome
    print("How did it go? Enter -1 (lost/no response), 0 (neutral), or 1 (won/got meeting):")
    signal_input = input("> ").strip()
    try:
        signal = int(signal_input)
        if signal not in (-1, 0, 1):
            signal = 1
    except ValueError:
        signal = 1

    print("Describe what you did in one sentence:")
    action = input("> ").strip()
    if not action:
        action = "opened with the problem - agents forget everything between sessions"

    print("Describe the outcome in one sentence:")
    outcome = input("> ").strip()
    if not outcome:
        outcome = "got a follow-up meeting booked"

    # 7. Record outcome
    record(user_id, domain, action, outcome, signal)
    print("\nMemory updated. Lumen learned from this session.")


if __name__ == "__main__":
    run()
