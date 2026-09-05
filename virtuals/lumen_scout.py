"""Lumen Scout — a G.A.M.E agent powered by Lumen memory."""

import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from game_sdk.game.agent import Agent, WorkerConfig
from game_sdk.game.worker import Worker
from virtuals.lumen_functions import LUMEN_GAME_FUNCTIONS

GAME_API_KEY = os.environ.get("GAME_API_KEY", "")

if not GAME_API_KEY:
    raise ValueError(
        "GAME_API_KEY not set. "
        "Get one from https://console.game.virtuals.io"
    )


def get_agent_state(function_results, current_state):
    """Build agent state from function results."""
    state = current_state or {}
    
    if function_results:
        for result in function_results:
            if result.get("fn_name") == "get_lumen_brief":
                state["last_brief"] = result.get("data", {})
            elif result.get("fn_name") == "record_lumen_outcome":
                state["last_record"] = result.get("data", {})
    
    return state


# Compatibility shims for game-sdk argument variants
_orig_worker_init = Worker.__init__
def _compat_worker_init(self, *args, **kwargs):
    if "model" in kwargs and "model_name" not in kwargs:
        kwargs["model_name"] = kwargs.pop("model")
    return _orig_worker_init(self, *args, **kwargs)
Worker.__init__ = _compat_worker_init

_orig_agent_init = Agent.__init__
def _compat_agent_init(self, *args, **kwargs):
    if "model" in kwargs and "model_name" not in kwargs:
        kwargs["model_name"] = kwargs.pop("model")
    if "get_agent_state_fn" not in kwargs and len(args) < 5:
        kwargs["get_agent_state_fn"] = kwargs.get("get_state_fn", lambda res, cur: cur or {})
    if "workers" in kwargs and kwargs["workers"]:
        converted = []
        for w in kwargs["workers"]:
            if isinstance(w, Worker):
                converted.append(WorkerConfig(
                    id="lumen_worker",
                    worker_description=w.description,
                    get_state_fn=w.get_state_fn,
                    action_space=list(w.action_space.values())
                ))
            else:
                converted.append(w)
        kwargs["workers"] = converted
    return _orig_agent_init(self, *args, **kwargs)
Agent.__init__ = _compat_agent_init

_orig_agent_run = Agent.run
def _compat_agent_run(self, *args, **kwargs):
    try:
        return _orig_agent_run(self)
    except TypeError:
        return _orig_agent_run(self, *args, **kwargs)
Agent.run = _compat_agent_run


# Create the Lumen Scout worker
lumen_worker = Worker(
    api_key=GAME_API_KEY,
    description=(
        "You are Lumen Scout, an agent powered by persistent "
        "outcome memory. Before taking any action, you ALWAYS "
        "call get_lumen_brief to check what has worked and "
        "failed in the past. After every action, you ALWAYS "
        "call record_lumen_outcome to teach your memory what "
        "happened. You never repeat known failures. You double "
        "down on patterns that work. Your memory persists across "
        "sessions — you get smarter every time you act."
    ),
    get_state_fn=get_agent_state,
    action_space=LUMEN_GAME_FUNCTIONS,
    model="Llama-3.1-405B-Instruct"
)

# Create the Lumen Scout agent
lumen_agent = Agent(
    api_key=GAME_API_KEY,
    name="Lumen Scout",
    agent_goal=(
        "Help users make better decisions by learning from "
        "their past outcomes. Before each action, consult "
        "Lumen memory. After each action, record what happened. "
        "Surface patterns and warnings from memory to guide "
        "the next decision. Get smarter with every session."
    ),
    agent_description=(
        "Lumen Scout is an autonomous agent with persistent "
        "outcome memory powered by Lumen and Sibyl Memory. "
        "It learns what works for a specific user across any "
        "domain — pitch, post, ask, trade, or any activity "
        "with measurable outcomes. Unlike stateless agents, "
        "Lumen Scout remembers every win and every loss and "
        "applies that memory before acting. Delete the memory "
        "and the agent goes blind. The memory is load-bearing."
    ),
    workers=[lumen_worker],
    model="Llama-3.1-405B-Instruct"
)


def run_lumen_scout(task: str, user_id: str = "scout_user"):
    """Run Lumen Scout on a task.
    
    Args:
        task: What the agent should help with.
        user_id: User ID for memory scoping.
    """
    print(f"\n{'='*60}")
    print(f"LUMEN SCOUT — GAME AGENT")
    print(f"{'='*60}")
    print(f"Task: {task}")
    print(f"User: {user_id}")
    print(f"Memory: Lumen (Sibyl substrate)")
    print(f"{'='*60}\n")
    
    result = lumen_agent.run(
        session_id=f"lumen_scout_{user_id}",
        task=task
    )
    
    return result


if __name__ == "__main__":
    run_lumen_scout(
        task=(
            "I am about to pitch Lumen to a crypto fund. "
            "Check my memory for patterns from past pitches "
            "and help me prepare the strongest opening. "
            "After I tell you how it went, record the outcome."
        ),
        user_id="alex"
    )
