import math
from hockey_strategy import outcome
STRATEGIES=tuple("hockey"+str(i) for i in range(1,6))
def register(state,match_id,strategy,favorite,teams,prematch=None,live_odds=None):
    if strategy not in STRATEGIES: return None
    key=str(match_id)+":"+strategy
    alerts=state.setdefault("alerts",{})
    if key in alerts: return None
    alerts[key]={"match_id":str(match_id),"strategy":strategy,"favorite":favorite,"teams":list(teams),"prematch":prematch,"live_odds":live_odds,"result":None,"message_id":None}
    return key
def settle(state,match_id,teams,completed,final_winner=None):
    changed=[]
    for key,r in state.get("alerts",{}).items():
        if r["match_id"]!=str(match_id) or r["teams"]!=list(teams) or r["result"] is not None: continue
        result=outcome(r["strategy"],completed,r["favorite"],final_winner)
        if result is not None:
            r["result"]=result
            changed.append(key)
    return changed
def statistics(state):
    out={}
    for s in STRATEGIES:
        rows=[r for r in state.get("alerts",{}).values() if r["strategy"]==s and r.get("message_id")]
        verified=[r for r in rows if type(r["result"]) is bool]
        wins=sum(r["result"] for r in verified)
        priced=[r for r in verified if type(r.get("live_odds")) in (float,int) and math.isfinite(r["live_odds"]) and r["live_odds"]>1]
        profit=sum(r["live_odds"]-1 if r["result"] else -1 for r in priced)
        out[s]={"alerts":len(rows),"wins":wins,"losses":len(verified)-wins,"pending":len(rows)-len(verified),"success_pct":100*wins/len(verified) if verified else None,"priced":len(priced),"roi_pct":100*profit/len(priced) if priced else None}
    return out
