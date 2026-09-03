"""Cross-user pattern market for Lumen."""

from collections import Counter
from lumen.memory import get_client


def get_aggregate_patterns(domain: str) -> dict:
    """Compute aggregate patterns across all users for a domain.
    
    Reads all events to aggregate outcomes for a given domain.
    
    Returns:
    - aggregate_win_rate: float
    - aggregate_loss_rate: float  
    - aggregate_avg_signal: float
    - top_winning_actions: list of str (up to 5)
    - top_losing_actions: list of str (up to 5)
    - sample_size: int (total outcomes across all users)
    - contributors: int (distinct users)
    - domain: str
    """
    memory = get_client()
    
    # Read all events to find patterns for this domain
    all_events = memory.read_events()
    
    domain_lower = domain.strip().lower()
    prefix = "LUMEN|"
    
    winning_actions = []
    losing_actions = []
    signals = []
    user_ids_seen = set()
    
    for ev in all_events:
        acted_list = ev.get("acted") or []
        for act in acted_list:
            if not isinstance(act, str):
                continue
            if not act.startswith(prefix):
                continue
            
            parts = act.split("|")
            if len(parts) < 7:
                continue
            if parts[0] != "LUMEN":
                continue
            if parts[5] != "SEP":
                continue
            if parts[2] != domain_lower:
                continue
                
            try:
                sig = int(parts[3])
            except ValueError:
                continue
                
            user_id = parts[1]
            action = parts[4]
            
            user_ids_seen.add(user_id)
            signals.append(sig)
            
            if sig == 1:
                winning_actions.append(action)
            elif sig == -1:
                losing_actions.append(action)
    
    if not signals:
        return {
            "aggregate_win_rate": 0.0,
            "aggregate_loss_rate": 0.0,
            "aggregate_avg_signal": 0.0,
            "top_winning_actions": [],
            "top_losing_actions": [],
            "sample_size": 0,
            "contributors": 0,
            "domain": domain_lower
        }
    
    total = len(signals)
    wins = sum(1 for s in signals if s == 1)
    losses = sum(1 for s in signals if s == -1)
    
    # Count action frequencies
    win_counts = Counter(winning_actions)
    loss_counts = Counter(losing_actions)
    
    top_wins = [action for action, _ in win_counts.most_common(5)]
    top_losses = [action for action, _ in loss_counts.most_common(5)]
    
    return {
        "aggregate_win_rate": round(wins / total, 2),
        "aggregate_loss_rate": round(losses / total, 2),
        "aggregate_avg_signal": round(sum(signals) / total, 2),
        "top_winning_actions": top_wins,
        "top_losing_actions": top_losses,
        "sample_size": total,
        "contributors": len(user_ids_seen),
        "domain": domain_lower
    }
