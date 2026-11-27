import os,json,urllib.request,urllib.error
from datetime import datetime,timezone
from pathlib import Path
from hockey_state import load,save
from hockey_strategy import reserve
from hockey_engine import cycle

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        return None

def main():
    now=datetime.now(timezone.utc)
    path=Path("hockey_state.enc")
    secret=os.environ["HOCKEY_STATE_SECRET"]
    state=load(path,secret,initialize=os.getenv("HOCKEY_INITIALIZE")=="true")
    key=os.environ["BIGBALLS_API_KEY"]
    budget=state.setdefault("budget",{})
    slot=int(now.timestamp())//300
    if state.get("last_slot")==slot or not reserve(budget,now.date().isoformat(),"live"):
        print("HOCKEY_REQUEST skipped")
        return
    state["last_slot"]=slot
    save(path,secret,state)
    url="https://api.bigballsdata.com/v1/matches?sport=ice_hockey&league=nhl&date="+now.date().isoformat()+"&limit=50"
    try:
        req=urllib.request.Request(url,headers={"x-api-key":key,"Accept":"application/json"})
        with urllib.request.build_opener(NoRedirect()).open(req,timeout=25) as response:
            data=json.load(response)
    except urllib.error.HTTPError as e:
        if e.code in (401,403,429):
            budget["blocked"]=True
        save(path,secret,state)
        print("HOCKEY_HTTP",e.code)
        return
    except (OSError,ValueError):
        print("HOCKEY_REQUEST unavailable")
        return
    rows=data.get("data") if isinstance(data,dict) else None
    if not isinstance(rows,list):
        print("HOCKEY_RESPONSE invalid")
        return
    print("HOCKEY_REPORT",json.dumps(cycle(state,rows,[],now)))
    save(path,secret,state)

if __name__=="__main__":
    main()
