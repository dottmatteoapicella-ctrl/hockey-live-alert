"""Conservative adapter for observed Big Balls NHL schema."""
from hockey_strategy import pair

def decode(row):
    if not isinstance(row, dict) or row.get("id") is None:
        return None
    status = row.get("status")
    if status not in ("live", "finished"):
        return None
    score, lines = row.get("score"), row.get("linescore")
    if not isinstance(score, dict) or not isinstance(lines, dict):
        return None
    total = [score.get("home"), score.get("away")]
    h, a = lines.get("home"), lines.get("away")
    if not pair(total) or not isinstance(h,list) or not isinstance(a,list) or len(h)!=len(a) or not 1<=len(h)<=3:
        return None
    periods = [list(p) for p in zip(h,a)]
    if not all(map(pair,periods)) or [sum(h),sum(a)]!=total:
        return None
    # Array length alone is not proof of the current or completed period.
    return dict(id=str(row["id"]), status=status, total=total, periods=periods,
                confirmed_periods=False)

def diagnostic(rows):
    counts = dict(live=0, finished=0, valid_arrays=0, rejected=0, confirmed_periods=0)
    for row in rows:
        if not isinstance(row,dict) or row.get("status") not in ("live","finished"):
            continue
        counts[row["status"]]+=1
        decoded=decode(row)
        counts["valid_arrays" if decoded else "rejected"]+=1
    return counts
