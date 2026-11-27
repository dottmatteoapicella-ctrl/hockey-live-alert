def reserve_odds(state,now):
    day=now.date().isoformat()
    month=day[:7]
    b=state.setdefault("odds_budget",{})
    if b.get("month")!=month:
        b.clear()
        b.update(month=month,monthly=0,blocked=False)
    if b.get("day")!=day:
        b.update(day=day,daily=0)
    slot=int(now.timestamp())//5400
    if b.get("blocked") or b.get("slot")==slot or b["daily"]>=16 or b["monthly"]>=496:
        return False
    b.update(slot=slot,daily=b["daily"]+1,monthly=b["monthly"]+1)
    return True
