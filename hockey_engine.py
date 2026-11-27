"""Shadow engine: no network or Telegram delivery."""
from hockey_feed import decode
from hockey_odds import prematch, favorite, stamp
from hockey_tracking import statistics
from hockey_strategy import pair
from datetime import timedelta

def cycle(state, matches, odds, now):
    cache=state.setdefault("prematch",{})
    accepted=0
    nhl_rows=0
    for row in odds:
        if not isinstance(row,dict):
            continue
        if str(row.get("league","")).strip().casefold()=="nhl":
            nhl_rows+=1
        record=prematch(row,now)
        if record:
            accepted+=1
            key="|".join(sorted(record["teams"]))+"|"+record["start"]
            cache[key]=record
    for key,record in list(cache.items()):
        start=stamp(record.get("start"))
        if not start or start<now-timedelta(days=3):
            del cache[key]
    report=dict(live=0,valid_scores=0,favorites=0,unconfirmed_periods=0,alerts=0,h2_candidates=0,total_scores=0)
    for row in matches:
        if not isinstance(row,dict) or row.get("status")!="live":
            continue
        report["live"]+=1
        score=row.get("score")
        total=[score.get("home"),score.get("away")] if isinstance(score,dict) else None
        fav=favorite(row,cache.values())
        if pair(total) and row.get("id") is not None:
            report["total_scores"]+=1
            if fav is not None and total[1-fav[0]]-total[fav[0]]>=2:
                report["h2_candidates"]+=1
        decoded=decode(row)
        if not decoded:
            continue
        report["valid_scores"]+=1
        if fav is not None:
            report["favorites"]+=1
        if not decoded["confirmed_periods"]:
            report["unconfirmed_periods"]+=1
    return dict(cycle=report,cached=len(cache),odds_rows=len(odds),nhl_odds_rows=nhl_rows,prematch_accepted=accepted,statistics=statistics(state))
