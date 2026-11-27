"""Only unambiguous two-way NHL Game/To Win prematch quotes."""
import math
import re
from datetime import datetime, timezone, timedelta

def stamp(value):
    try:
        d=datetime.fromisoformat(value.replace("Z","+00:00"))
        return d.astimezone(timezone.utc) if d.tzinfo else None
    except (AttributeError,ValueError,TypeError):
        return None

ALIASES = {"washingtoncapitals":["wascapitals","was"],"floridapanthers":["flapanthers","fla"],"bostonbruins":["bosbruins","bos"],"torontomapleleafs":["tormapleleafs","tor"]}

def name(value):
    if isinstance(value,dict):
        value=value.get("name")
    normalized=re.sub(r"[^a-z0-9]","",value.casefold()) if isinstance(value,str) else ""
    return next((team for team,aliases in ALIASES.items() if normalized in aliases),normalized)

def prematch(row,now):
    if row.get("in_play") is not False or row.get("stale") is True or str(row.get("league","")).strip().casefold()!="nhl":
        return None
    start,poll=stamp(row.get("kickoff_utc")),stamp(row.get("polled_at"))
    teams=[name(row.get(k)) for k in ("home","away")]
    if not start or not poll or start<=now or not timedelta(0)<=now-poll<=timedelta(minutes=15) or not all(teams) or teams[0]==teams[1]:
        return None
    prices={}
    for q in row.get("quotes") or []:
        if not isinstance(q,dict) or str(q.get("group_id"))!="972" or str(q.get("market_id"))!="973" or q.get("group_name")!="Game" or q.get("line")!="To Win" or q.get("suspended") not in (False,None) or q.get("phase") not in (None,"prematch","pre_match"):
            continue
        side=name(q.get("side"))
        ts=stamp(q.get("ts"))
        p=q.get("odds_dec")
        if side not in teams or not ts or not timedelta(0)<=now-ts<=timedelta(hours=2) or ts>=start or type(p) not in (int,float) or not math.isfinite(p) or p<=1:
            continue
        if side in prices and prices[side]!=p:
            return None
        prices[side]=p
    if len(prices)!=2 or prices[teams[0]]==prices[teams[1]]:
        return None
    return dict(teams=teams,prices=prices,start=start.isoformat(),captured=now.isoformat())

def favorite(row,records):
    teams=[name(row.get(k)) for k in ("home","away")]
    start=stamp(row.get("kickoff_utc"))
    if not start or not all(teams) or teams[0]==teams[1]:
        return None
    candidates=[]
    for r in records:
        rs,cap=stamp(r.get("start")),stamp(r.get("captured"))
        if set(r.get("teams",[]))!=set(teams) or not rs or not cap or cap>=min(rs,start) or abs(rs-start)>timedelta(minutes=30):
            continue
        p=[r.get("prices",{}).get(t) for t in teams]
        if all(type(x) in (int,float) and math.isfinite(x) and x>1 for x in p) and p[0]!=p[1]:
            candidates.append((0 if p[0]<p[1] else 1,p))
    return candidates[0] if len(candidates)==1 else None
