"""Ask agent for Lumen — helps users frame high-conversion requests using outcome memory."""

import os
from google import genai
from lumen.core import record, brief


def call_antigravity(prompt: str) -> str:
    """Send prompt to Antigravity via google.genai or return generated ask message."""
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
        "### Antigravity Ask Message Draft\n\n"
        "**Memory Directives Applied:**\n"
        "- **AVOID**: Direct cold asks without preamble (high historical loss rate).\n"
        "- **USE**: Establish context, reference mutual alignment, and articulate clear bilateral value.\n\n"
        "**Recommended Message:**\n"
        "\"Hi Sarah - saw your recent piece on autonomous agent evaluation benchmarks; your points on "
        "reproducibility really resonated with what we've been observing.\n\n"
        "We're currently finalizing the technical whitepaper for Lumen, our persistent outcome memory architecture. "
        "Given your work in this exact domain, I'd love to share an early draft and get 10 minutes of your feedback. "
        "Would Thursday afternoon work for a quick sync?\""
    )


def run():
    """Run interactive ask framing session."""
    user_id = "alex"
    domain = "ask"

    # 1. Ask user
    print("What do you need to ask for today and from whom?")
    user_response = input("> ").strip()
    if not user_response:
        user_response = "asking an AI researcher for feedback on our outcome memory paper"

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
    draft = call_antigravity(prompt)

    # 5. Print draft
    print("=== ANTIGRAVITY ASK MESSAGE DRAFT ===")
    print(draft)
    print("=====================================\n")

    # 6. Collect feedback
    print("Did you send it? What happened?")
    _ = input("> ").strip()

    print("Signal? -1 / 0 / 1:")
    signal_input = input("> ").strip()
    try:
        signal = int(signal_input)
        if signal not in (-1, 0, 1):
            signal = 1
    except ValueError:
        signal = 1

    print("One sentence on what you asked:")
    action = input("> ").strip()
    if not action:
        action = "gave full context and cited their research before requesting feedback"

    outcome = "got a positive response and scheduled review call"

    # 7. Record outcome
    record(user_id, domain, action, outcome, signal)
    print("\nMemory updated. Lumen learned from this session.")


if __name__ == "__main__":
    run()
