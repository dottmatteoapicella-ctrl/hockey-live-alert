import os,json,urllib.request,urllib.error
from datetime import datetime,timezone,timedelta
from pathlib import Path
from hockey_state import load,save
from hockey_strategy import reserve
from hockey_engine import cycle
from hockey_odds_budget import reserve_odds

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None

def main():
    now=datetime.now(timezone.utc)
    path=Path("hockey_state.enc")
    secret=os.environ["HOCKEY_STATE_SECRET"]
    state=load(path,secret,initialize=False)
    key=os.environ["BIGBALLS_API_KEY"]
    budget=state.setdefault("budget",{})
    slot=int(now.timestamp())//300
    if state.get("last_slot")==slot or not reserve(budget,now.date().isoformat(),"live"):
        print("HOCKEY_REQUEST skipped")
        return
    state["last_slot"]=slot
    save(path,secret,state)
    rows_by_id={}
    for index,day in enumerate((now.date(),now.date()-timedelta(days=1))):
        if index:
            if not reserve(budget,now.date().isoformat(),"extra"):
                break
            save(path,secret,state)
        url="https://api.bigballsdata.com/v1/matches?sport=ice_hockey&league=nhl&date="+day.isoformat()+"&limit=50"
        try:
            req=urllib.request.Request(url,headers={"x-api-key":key,"Accept":"application/json"})
            with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as response:
                data=json.load(response)
        except urllib.error.HTTPError as e:
            if e.code in (401,403,429):
                budget["blocked"]=True
            save(path,secret,state)
            print("HOCKEY_HTTP",e.code)
            break
        except (OSError,ValueError):
            print("HOCKEY_REQUEST unavailable")
            continue
        print("HOCKEY_HTTP",200)
        batch=data.get("data") if isinstance(data,dict) else None
        if not isinstance(batch,list):
            print("HOCKEY_RESPONSE invalid")
            continue
        for row in batch:
            if isinstance(row,dict) and row.get("id") is not None:
                rows_by_id.setdefault(str(row["id"]),row)
    rows=list(rows_by_id.values())
    # Log only non-sensitive schema evidence, never infer periods from arrays.
    for row in rows:
        if not isinstance(row,dict) or row.get("status") not in ("live","finished"):
            continue
        evidence={k:row[k] for k in ("status","round","period","current_period","period_number","clock","score","linescore") if k in row}
        print("HOCKEY_PERIOD_EVIDENCE",json.dumps(evidence)[:2000])
    odds=[]
    odds_key=os.getenv("MOVIODDS_API_KEY")
    if odds_key and reserve_odds(state,now):
        save(path,secret,state)
        try:
            req=urllib.request.Request("https://moviodds.com/odds?sport=ice_hockey",headers={"X-API-Key":odds_key,"Accept":"application/json"})
            with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as response:
                payload=json.load(response)
            batch=payload.get("matches") if isinstance(payload,dict) else None
            if isinstance(batch,list):
                odds=batch
            print("HOCKEY_ODDS_HTTP",200,"rows",len(odds))
        except urllib.error.HTTPError as e:
            if e.code in (401,403,429):
                state["odds_budget"]["blocked"]=True
            print("HOCKEY_ODDS_HTTP",e.code)
        except (OSError,ValueError):
            print("HOCKEY_ODDS unavailable")
        save(path,secret,state)
    print("HOCKEY_ODDS_BUDGET",json.dumps(state.get("odds_budget",{})))
    print("HOCKEY_REPORT",json.dumps(cycle(state,rows,odds,now)))
    print("HOCKEY_BUDGET",json.dumps(budget))
    save(path,secret,state)

if __name__=="__main__":
    main()
