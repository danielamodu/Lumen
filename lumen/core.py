"""Core outcome memory module for Lumen."""

from datetime import datetime, timezone
from sibyl_memory_client.exceptions import NotFoundError
from lumen.memory import get_client


def _safe_get_entity(memory, kind: str, name: str):
    """Retrieve an entity safely, returning None if the entity is not found."""
    try:
        return memory.get_entity(kind, name)
    except NotFoundError:
        return None
    except Exception as exc:
        if "not found" in str(exc).lower():
            return None
        raise exc


def _recalculate_patterns(user_id: str, domain: str) -> dict:
    """Read COLD events for user+domain, compute pattern metrics, and update WARM pattern entity.

    Computes:
    - total_outcomes (int)
    - win_rate (float rounded to 2 decimal places)
    - loss_rate (float rounded to 2 decimal places)
    - avg_signal (float rounded to 2 decimal places)
    - recent_wins (list of str, up to 3 most recent winning actions)
    - recent_losses (list of str, up to 3 most recent losing actions)
    - last_calculated (ISO 8601 timestamp)
    """
    memory = get_client()
    events = memory.read_events()

    prefix = f"LUMEN|{user_id}|{domain}|"
    matching_events = []

    for ev in events:
        acted_list = ev.get("acted") or []
        for act in acted_list:
            if isinstance(act, str) and act.startswith(prefix):
                parts = act.split("|")
                # Format: LUMEN|user_id|domain|signal|action|SEP|outcome
                if len(parts) >= 7 and parts[0] == "LUMEN" and parts[5] == "SEP":
                    try:
                        sig = int(parts[3])
                    except ValueError:
                        sig = 0
                    action_str = parts[4]
                    outcome_str = parts[6]
                    matching_events.append({
                        "signal": sig,
                        "action": action_str,
                        "outcome": outcome_str,
                    })
                break

    total_outcomes = len(matching_events)
    if total_outcomes == 0:
        win_rate = 0.0
        loss_rate = 0.0
        avg_signal = 0.0
        recent_wins = []
        recent_losses = []
    else:
        win_count = sum(1 for e in matching_events if e["signal"] == 1)
        loss_count = sum(1 for e in matching_events if e["signal"] == -1)
        win_rate = round(win_count / total_outcomes, 2)
        loss_rate = round(loss_count / total_outcomes, 2)
        avg_signal = round(sum(e["signal"] for e in matching_events) / total_outcomes, 2)
        recent_wins = [e["action"] for e in matching_events if e["signal"] == 1][:3]
        recent_losses = [e["action"] for e in matching_events if e["signal"] == -1][:3]

    pattern_body = {
        "user_id": user_id,
        "domain": domain,
        "total_outcomes": total_outcomes,
        "win_rate": win_rate,
        "loss_rate": loss_rate,
        "avg_signal": avg_signal,
        "recent_wins": recent_wins,
        "recent_losses": recent_losses,
        "last_calculated": datetime.now(timezone.utc).isoformat(),
    }

    memory.set_entity("pattern", f"{user_id}:{domain}", pattern_body)
    return pattern_body


def record(
    user_id: str,
    domain: str,
    action: str,
    outcome: str,
    signal: int,
    tenant_id: str = "demo"
) -> None:
    """Record one outcome to Sibyl memory and recalculate patterns for user+domain.

    Parameters:
    - user_id: str — identifies the user
    - domain: str — non-empty string identifying domain
    - action: str — what the user tried
    - outcome: str — what happened
    - signal: int — must be -1 (loss), 0 (neutral), or 1 (win)
    - tenant_id: str — multi-tenant isolation id (defaults to 'demo')
    """
    if not domain or not isinstance(domain, str):
        raise ValueError("Domain must be a non-empty string.")
    domain = domain.strip().lower()
    if signal not in (-1, 0, 1):
        raise ValueError(f"Signal must be -1, 0, or 1, got {signal}")

    memory = get_client()

    # Capture pattern BEFORE recalculation
    pattern_entity_before = _safe_get_entity(
        memory, "pattern", f"{user_id}:{domain}"
    )
    pattern_before = (
        pattern_entity_before.get("body") 
        if pattern_entity_before else None
    )

    # 1. Get or create WARM entity for user
    user_entity = _safe_get_entity(memory, "user", user_id)
    if user_entity and isinstance(user_entity.get("body"), dict):
        user_body = user_entity["body"]
        domains = list(user_body.get("domains", []))
        if domain not in domains:
            domains.append(domain)
        total_outcomes = user_body.get("total_outcomes", 0) + 1
    else:
        domains = [domain]
        total_outcomes = 1

    updated_user_body = {
        "domains": domains,
        "total_outcomes": total_outcomes,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    memory.set_entity("user", user_id, updated_user_body)

    # 2. Write one COLD journal event
    event_str = f"LUMEN|{user_id}|{domain}|{signal}|{action}|SEP|{outcome}"
    memory.write_event(acted=[event_str])

    # 3. Recalculate pattern for user+domain
    pattern_after = _recalculate_patterns(user_id, domain)

    # Check and fire webhooks
    if pattern_before is not None:
        current_brief = brief(user_id, domain, "")
        from lumen.webhooks import check_and_fire_webhooks
        check_and_fire_webhooks(
            tenant_id=tenant_id,
            user_id=user_id,
            domain=domain,
            pattern_before=pattern_before,
            pattern_after=pattern_after,
            current_brief=current_brief
        )


def brief(user_id: str, domain: str, context: str) -> dict:
    """Read learned patterns from Sibyl memory and return structured guidance for an agent.

    Parameters:
    - user_id: str
    - domain: str
    - context: str — what the user is about to do this session

    Returns a dict with:
    - "warning": str or None — the strongest negative pattern if signal average < 0. None if no pattern.
    - "pattern": str or None — the clearest positive pattern if signal average > 0. None if no pattern.
    - "cross_domain": str or None — insight from other domains if combined outcomes >= 3. None otherwise.
    - "confidence": str — e.g. "12 outcomes recorded. Pattern is stable." or "3 outcomes recorded. Pattern is early."
    - "raw_outcomes": int — total number of COLD outcomes for this user+domain
    """
    domain = domain.strip().lower()
    memory = get_client()

    # 1. Read current domain pattern from WARM tier
    pattern_entity = _safe_get_entity(memory, "pattern", f"{user_id}:{domain}")
    pattern_body = pattern_entity.get("body") if pattern_entity else None

    if pattern_body is None:
        raw_outcomes = 0
        avg_signal = 0.0
        win_rate = 0.0
        loss_rate = 0.0
        recent_wins = []
        recent_losses = []
    else:
        raw_outcomes = pattern_body.get("total_outcomes", 0)
        avg_signal = pattern_body.get("avg_signal", 0.0)
        win_rate = pattern_body.get("win_rate", 0.0)
        loss_rate = pattern_body.get("loss_rate", 0.0)
        recent_wins = pattern_body.get("recent_wins", [])
        recent_losses = pattern_body.get("recent_losses", [])

    # 2. Compute warning if losses exist
    warning = None
    if raw_outcomes > 0 and recent_losses:
        primary_loss = recent_losses[0]
        loss_pct = int(round(loss_rate * 100))
        warning = f"High loss rate ({loss_pct}%) when you '{primary_loss}'. Consider alternative approaches."

    # 3. Compute positive pattern if wins exist
    pattern = None
    if raw_outcomes > 0 and recent_wins:
        primary_win = recent_wins[0]
        win_pct = int(round(win_rate * 100))
        pattern = f"High win rate ({win_pct}%) when you '{primary_win}'. Continue this approach."

    # 4. Compute cross-domain insights from other domains
    cross_domain = None
    user_entity = _safe_get_entity(memory, "user", user_id)
    if user_entity and isinstance(user_entity.get("body"), dict):
        all_domains = user_entity["body"].get("domains", [])
        other_domains = [d for d in all_domains if d != domain]
        other_patterns = []

        for other_d in other_domains:
            other_p = _safe_get_entity(memory, "pattern", f"{user_id}:{other_d}")
            if other_p and isinstance(other_p.get("body"), dict):
                other_patterns.append(other_p["body"])

        total_other_outcomes = sum(p.get("total_outcomes", 0) for p in other_patterns)
        if total_other_outcomes >= 3:
            # Select the most informative other domain pattern (highest win rate, then total outcomes)
            best_other = max(other_patterns, key=lambda p: (p.get("win_rate", 0.0), p.get("total_outcomes", 0)))
            other_name = best_other.get("domain", "").capitalize()
            other_win_pct = int(round(best_other.get("win_rate", 0.0) * 100))
            other_wins = best_other.get("recent_wins", [])
            other_losses = best_other.get("recent_losses", [])

            if other_wins:
                leading_win_action = other_wins[0]
                cross_domain = (
                    f"Your {other_name} domain shows {other_win_pct}% win rate with '{leading_win_action}'. "
                    f"Consider similar framing for {domain}."
                )
            elif other_losses:
                other_loss_pct = int(round(best_other.get("loss_rate", 0.0) * 100))
                leading_loss_action = other_losses[0]
                cross_domain = (
                    f"Caution from {other_name} domain ({other_loss_pct}% loss rate with '{leading_loss_action}'). "
                    f"Avoid similar patterns in {domain}."
                )
            else:
                cross_domain = (
                    f"Your {other_name} domain shows {other_win_pct}% win rate across {best_other.get('total_outcomes', 0)} outcomes."
                )

    # 5. Compute confidence string
    if raw_outcomes == 0:
        confidence = "0 outcomes recorded. No pattern yet."
    elif raw_outcomes < 5:
        confidence = f"{raw_outcomes} outcomes recorded. Pattern is early."
    elif raw_outcomes < 10:
        confidence = f"{raw_outcomes} outcomes recorded. Pattern is developing."
    else:
        confidence = f"{raw_outcomes} outcomes recorded. Pattern is stable."

    result = {
        "warning": warning,
        "pattern": pattern,
        "cross_domain": cross_domain,
        "confidence": confidence,
        "raw_outcomes": raw_outcomes,
    }

    # 6. Write result to HOT state
    memory.set_state(f"brief:{user_id}:{domain}", result)

    return result
