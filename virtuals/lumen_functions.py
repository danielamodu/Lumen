"""Lumen memory functions for Virtuals G.A.M.E agents."""

from game_sdk.game.custom_types import (
    Function, 
    Argument,
    FunctionResultStatus
)
from lumen_memory import Lumen

# Initialize Lumen client pointing to live Railway API
lumen = Lumen(
    base_url="https://lumen-memory-production.up.railway.app",
    api_key="lmn_demo0000000000000000000000000000"
)


def get_lumen_brief(user_id: str, domain: str, 
                    context: str) -> tuple:
    """Get a Lumen memory brief for a user and domain.
    
    Returns (FunctionResultStatus, message, data)
    """
    try:
        result = lumen.brief(
            user_id=user_id,
            domain=domain,
            context=context
        )
        
        summary_parts = []
        if result.warning:
            summary_parts.append(f"WARNING: {result.warning}")
        if result.pattern:
            summary_parts.append(f"PATTERN: {result.pattern}")
        if result.cross_domain:
            summary_parts.append(
                f"CROSS-DOMAIN: {result.cross_domain}"
            )
        
        summary = (
            " | ".join(summary_parts) 
            if summary_parts 
            else f"No patterns yet. {result.confidence}"
        )
        
        return (
            FunctionResultStatus.DONE,
            summary,
            {
                "warning": result.warning,
                "pattern": result.pattern,
                "cross_domain": result.cross_domain,
                "confidence": result.confidence,
                "raw_outcomes": result.raw_outcomes
            }
        )
    except Exception as e:
        return (
            FunctionResultStatus.FAILED,
            f"Lumen brief failed: {str(e)}",
            {}
        )


def record_lumen_outcome(
    user_id: str,
    domain: str, 
    action: str,
    outcome: str,
    signal: int
) -> tuple:
    """Record an outcome to Lumen memory.
    
    Returns (FunctionResultStatus, message, data)
    """
    try:
        if signal not in (-1, 0, 1):
            return (
                FunctionResultStatus.FAILED,
                f"Signal must be -1, 0, or 1. Got: {signal}",
                {}
            )
        
        result = lumen.record(
            user_id=user_id,
            domain=domain,
            action=action,
            outcome=outcome,
            signal=signal
        )
        
        signal_label = {
            1: "WIN (+1)",
            0: "NEUTRAL (0)", 
            -1: "LOSS (-1)"
        }[signal]
        
        return (
            FunctionResultStatus.DONE,
            f"Outcome recorded: {signal_label} — {action}",
            {"status": result.status, "message": result.message}
        )
    except Exception as e:
        return (
            FunctionResultStatus.FAILED,
            f"Lumen record failed: {str(e)}",
            {}
        )


# G.A.M.E Function definitions
lumen_brief_function = Function(
    fn_name="get_lumen_brief",
    fn_description=(
        "Get a memory brief from Lumen before acting. "
        "Returns learned patterns from past outcomes — "
        "what worked, what failed, and cross-domain insights. "
        "Call this BEFORE taking any action to get memory-driven guidance."
    ),
    args=[
        Argument(
            name="user_id",
            type="string",
            description="The user or agent ID to get patterns for"
        ),
        Argument(
            name="domain",
            type="string", 
            description=(
                "The activity domain — e.g. 'pitch', 'post', "
                "'ask', 'trade', 'outreach', or any custom domain"
            )
        ),
        Argument(
            name="context",
            type="string",
            description=(
                "What you are about to do this session. "
                "Helps contextualize the brief."
            )
        )
    ],
    executable=get_lumen_brief
)

lumen_record_function = Function(
    fn_name="record_lumen_outcome",
    fn_description=(
        "Record an outcome to Lumen memory after acting. "
        "Call this AFTER completing an action to teach Lumen "
        "what worked and what didn't. "
        "Signal: 1=win/success, 0=neutral, -1=loss/failure."
    ),
    args=[
        Argument(
            name="user_id",
            type="string",
            description="The user or agent ID recording the outcome"
        ),
        Argument(
            name="domain",
            type="string",
            description="The activity domain"
        ),
        Argument(
            name="action",
            type="string",
            description="What the agent tried — one sentence"
        ),
        Argument(
            name="outcome",
            type="string",
            description="What happened — one sentence"
        ),
        Argument(
            name="signal",
            type="integer",
            description="1 for win/success, 0 for neutral, -1 for loss/failure"
        )
    ],
    executable=record_lumen_outcome
)

# Export both functions as a list for easy import
LUMEN_GAME_FUNCTIONS = [
    lumen_brief_function,
    lumen_record_function
]
