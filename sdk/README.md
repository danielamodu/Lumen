# lumen-memory

Outcome memory layer for AI agents. 
Any agent learns from experience — not fine-tuning, not RAG. 
Just memory.

## Install

```bash
pip install lumen-memory
```

## Quickstart

Start the Lumen API server first:
```bash
python api/server.py
```

Then in your agent:

```python
from lumen_memory import Lumen

lumen = Lumen(base_url="http://localhost:8000")

# Record an outcome after your agent acts
lumen.record(
    user_id="alex",
    domain="pitch",
    action="led with their problem",
    outcome="got a meeting booked",
    signal=1
)

# Get a brief before your agent acts
brief = lumen.brief(
    user_id="alex",
    domain="pitch", 
    context="about to pitch a crypto fund"
)

if brief.warning:
    print(f"Warning: {brief.warning}")
if brief.pattern:
    print(f"Pattern: {brief.pattern}")
if brief.cross_domain:
    print(f"Cross-domain: {brief.cross_domain}")
```

## Any domain works

```python
lumen.record("alex", "code_review", 
             "reviewed without tests", "missed bug", -1)
lumen.record("alex", "negotiation",
             "led with their problem", "closed deal", 1)
```

## Powered by Sibyl Memory
