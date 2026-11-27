"""Normalized scores: pairs of nonnegative integer goals, home then away.
Completed periods must be confirmed by the feed adapter, not inferred from score.
"""
def pair(p):
    return isinstance(p,(tuple,list)) and len(p)==2 and all(type(x) is int and x>=0 for x in p)

def signals(completed,current, favorite=None):
    if not isinstance(completed,list) or len(completed)>2 or not all(map(pair,completed)) or not pair(current):
        return []
    out=[]
    n=len(completed)
    if n==1 and sum(current)==0 and sum(completed[0])==0:
        out.append("hockey4")
    if n==2 and sum(current)==0 and sum(p[0]-p[1] for p in completed)==0:
        out.append("hockey5")
    if type(favorite) is int and favorite in (0,1):
        other=1-favorite
        if n==1 and sum(current)==0 and completed[0][favorite]<completed[0][other]:
            out.append("hockey1")
        if sum(p[other]-p[favorite] for p in completed+[current])>=2:
            out.append("hockey2")
        if n==2 and sum(current)==0 and sum(p[favorite]-p[other] for p in completed)<0:
            out.append("hockey3")
    return out

def outcome(strategy,completed,favorite=None,final_winner=None):
    if not isinstance(completed,list) or len(completed)>3 or not all(map(pair,completed)):
        return None
    if strategy in ("hockey4","hockey5"):
        i=1 if strategy=="hockey4" else 2
        return sum(completed[i])>0 if len(completed)>i else None
    if type(favorite) is not int or favorite not in (0,1):
        return None
    if strategy=="hockey3":
        return sum(p[favorite]-p[1-favorite] for p in completed)>=0 if len(completed)==3 else None
    if strategy in ("hockey1","hockey2") and type(final_winner) is int and final_winner in (0,1):
        return favorite==final_winner
    return None

def reserve(state,day,kind):
    limits={"live":288,"results":200,"extra":412}
    if kind not in limits: return False
    if state.get("day")!=day:
        state.clear()
        state.update(day=day,live=0,results=0,extra=0,blocked=False)
    if state.get("blocked") or sum(state[k] for k in limits)>=900 or state[kind]>=limits[kind]:
        return False
    state[kind]+=1
    return True
