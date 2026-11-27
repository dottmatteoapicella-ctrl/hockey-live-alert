"""H2 delivery for verified favorites; no provider calls."""
from hockey_odds import favorite,name
from hockey_strategy import pair
from hockey_tracking import register,settle

def deliver_h2(state,rows,telegram,persist,enabled=False,final_winner_verified=False):
    if not enabled:
        return
    records=state.get("prematch",{}).values()
    for row in rows:
        if not isinstance(row,dict) or row.get("id") is None:
            continue
        teams=[name(row.get(k)) for k in ("home","away")]
        if not all(teams) or teams[0]==teams[1]:
            continue
        score=row.get("score")
        total=[score.get("home"),score.get("away")] if isinstance(score,dict) else None
        if not pair(total):
            continue
        mid=str(row["id"])
        key=mid+":hockey2"
        alerts=state.setdefault("alerts",{})
        if row.get("status")=="live":
            fav=favorite(row,records)
            if fav is None or total[1-fav[0]]-total[fav[0]]<2 or key in alerts:
                continue
            idx,prices=fav
            register(state,mid,"hockey2",idx,teams,prices[idx])
            r=alerts[key]
            r["text"]="HOCKEY2 | SPERIMENTALE\n"+" - ".join(teams)+"\nFavorita: "+teams[idx]+"\nPunteggio: "+str(total[0])+"-"+str(total[1])+"\nQuota pre-match: "+str(prices[idx])+"\nQuota live: non disponibile"
            # Persist intent before sending; ambiguous delivery is never retried blindly.
            persist()
            message=telegram.send(r["text"])
            if type(message) is int and message>0:
                r["message_id"]=message
            persist()
        elif row.get("status")=="finished" and final_winner_verified and total[0]!=total[1]:
            r=alerts.get(key)
            if not r or r.get("teams")!=teams or not r.get("message_id"):
                continue
            settle(state,mid,teams,[],0 if total[0]>total[1] else 1)
            persist()
            if type(r.get("result")) is bool and not r.get("edited"):
                r["edited"]=telegram.edit(r["message_id"],r["text"]+"\nEsito: "+("VINCENTE" if r["result"] else "PERDENTE"))
                persist()
