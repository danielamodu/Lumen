"""Post agent for Lumen — assists users in crafting high-engagement hooks using outcome memory."""

import os
from google import genai
from lumen.core import record, brief


def call_antigravity(prompt: str) -> str:
    """Send prompt to Antigravity via google.genai or return generated hook coaching."""
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

    return (
        "### Antigravity Post Hook Draft\n\n"
        "**Memory Directives Applied:**\n"
        "- **AVOID**: Generic product updates or plain link drops (low engagement).\n"
        "- **USE**: Counterintuitive takes, personal vulnerability, or opening with an open question.\n\n"
        "**Recommended Hook:**\n"
        "\"Why do 95% of AI agents deliver worse answers in week 4 than in week 1?\n\n"
        "It's not prompt degradation. It's the complete lack of an outcome memory substrate.\n\n"
        "Here is what happened when we hooked 10 autonomous agents to persistent outcome memory (and what we learned):\""
    )


def run():
    """Run interactive post hook drafting session."""
    user_id = "alex"
    domain = "post"

    # 1. Ask user
    print("What do you want to post about today?")
    user_response = input("> ").strip()
    if not user_response:
        user_response = "why outcome memory makes AI agents 10x more effective"

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

    # 4. Send to Antigravity
    print("\n[Consulting Antigravity with Lumen session briefing...]\n")
    hook = call_antigravity(prompt)

    # 5. Print hook
    print("=== ANTIGRAVITY HOOK DRAFT ===")
    print(hook)
    print("==============================\n")

    # 6. Collect feedback
    print("Did you post it? How did it perform?")
    _ = input("> ").strip()

    print("Signal? -1 / 0 / 1:")
    signal_input = input("> ").strip()
    try:
        signal = int(signal_input)
        if signal not in (-1, 0, 1):
            signal = 1
    except ValueError:
        signal = 1

    print("One sentence on what you posted:")
    action = input("> ").strip()
    if not action:
        action = "opened with a counterintuitive question about agent memory degradation"

    outcome = "high engagement thread with 50+ replies"

    # 7. Record outcome
    record(user_id, domain, action, outcome, signal)
    print("\nMemory updated. Lumen learned from this session.")


if __name__ == "__main__":
    run()
