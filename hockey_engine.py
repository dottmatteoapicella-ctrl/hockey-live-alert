"""Shadow engine: no network or Telegram delivery."""
from hockey_feed import decode
from hockey_odds import prematch, favorite, stamp
from hockey_tracking import statistics
from datetime import timedelta

def cycle(state, matches, odds, now):
    cache=state.setdefault("prematch",{})
    for row in odds:
        if not isinstance(row,dict):
            continue
        record=prematch(row,now)
        if record:
            key="|".join(sorted(record["teams"]))+"|"+record["start"]
            cache[key]=record
    for key,record in list(cache.items()):
        start=stamp(record.get("start"))
        if not start or start<now-timedelta(days=3):
            del cache[key]
    report=dict(live=0,valid_scores=0,favorites=0,unconfirmed_periods=0,alerts=0)
    for row in matches:
        if not isinstance(row,dict) or row.get("status")!="live":
            continue
        report["live"]+=1
        decoded=decode(row)
        if not decoded:
            continue
        report["valid_scores"]+=1
        if favorite(row,cache.values()) is not None:
            report["favorites"]+=1
        if not decoded["confirmed_periods"]:
            report["unconfirmed_periods"]+=1
    return dict(cycle=report,cached=len(cache),statistics=statistics(state))
