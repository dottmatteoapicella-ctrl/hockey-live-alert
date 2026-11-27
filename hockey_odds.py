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

ALIASES = {
    "anaheimducks": [
        "anaducks",
        "ana"
    ],
    "bostonbruins": [
        "bosbruins",
        "bos"
    ],
    "buffalosabres": [
        "bufsabres",
        "buf"
    ],
    "calgaryflames": [
        "cgyflames",
        "cgy"
    ],
    "carolinahurricanes": [
        "carhurricanes",
        "car"
    ],
    "chicagoblackhawks": [
        "chiblackhawks",
        "chi"
    ],
    "coloradoavalanche": [
        "colavalanche",
        "col"
    ],
    "columbusbluejackets": [
        "cbjbluejackets",
        "clsbluejackets",
        "cbj"
    ],
    "dallasstars": [
        "dalstars",
        "dal"
    ],
    "detroitredwings": [
        "detredwings",
        "det"
    ],
    "edmontonoilers": [
        "edmoilers",
        "edm"
    ],
    "floridapanthers": [
        "flapanthers",
        "fla"
    ],
    "losangeleskings": [
        "lakings",
        "lakkings",
        "lak"
    ],
    "minnesotawild": [
        "minwild",
        "min"
    ],
    "montrealcanadiens": [
        "mtlcanadiens",
        "moncanadiens",
        "mtl"
    ],
    "nashvillepredators": [
        "nshpredators",
        "naspredators",
        "nsh"
    ],
    "newjerseydevils": [
        "njdevils",
        "njddevils",
        "njd"
    ],
    "newyorkislanders": [
        "nyislanders",
        "nyiislanders",
        "nyi"
    ],
    "newyorkrangers": [
        "nyrangers",
        "nyrrangers",
        "nyr"
    ],
    "ottawasenators": [
        "ottsenators",
        "ott"
    ],
    "philadelphiaflyers": [
        "phiflyers",
        "phi"
    ],
    "pittsburghpenguins": [
        "pitpenguins",
        "pit"
    ],
    "sanjosesharks": [
        "sjsharks",
        "sjssharks",
        "sjs"
    ],
    "seattlekraken": [
        "seakraken",
        "sea"
    ],
    "stlouisblues": [
        "stlblues",
        "stl"
    ],
    "tampabaylightning": [
        "tblightning",
        "tbllightning",
        "tbl"
    ],
    "torontomapleleafs": [
        "tormapleleafs",
        "tor"
    ],
    "utahmammoth": [
        "utamammoth",
        "utah",
        "uta"
    ],
    "vancouvercanucks": [
        "vancanucks",
        "van"
    ],
    "vegasgoldenknights": [
        "veggoldenknights",
        "vgkgoldenknights",
        "vgk"
    ],
    "washingtoncapitals": [
        "wascapitals",
        "was",
        "wshcapitals",
        "wsh"
    ],
    "winnipegjets": [
        "wpgjets",
        "wpg"
    ]
}

def name(value):
    if isinstance(value,dict):
        value=value.get("name")
    normalized=re.sub(r"[^a-z0-9]","",value.casefold()) if isinstance(value,str) else ""
    return next((team for team,aliases in ALIASES.items() if normalized in aliases),normalized)

def prematch(row,now):
    if not isinstance(row,dict):
        return None
    if row.get("in_play") is not False or row.get("stale") is True or str(row.get("league","")).strip().casefold()!="nhl":
        return None
    start,poll=stamp(row.get("kickoff_utc")),stamp(row.get("polled_at"))
    teams=[name(row.get(k)) for k in ("home","away")]
    if not start or not poll or start<=now or not timedelta(0)<=now-poll<=timedelta(minutes=15) or not all(teams) or teams[0]==teams[1]:
        return None
    prices={}
    for q in row["quotes"] if isinstance(row.get("quotes"),list) else []:
        if not isinstance(q,dict) or str(q.get("group_id"))!="972" or str(q.get("market_id"))!="973" or q.get("group_name")!="Game" or q.get("line")!="To Win" or (q.get("suspended") is not False and q.get("suspended") is not None) or q.get("phase") not in (None,"prematch","pre_match"):
            continue
        side=name(q.get("side"))
        ts=stamp(q.get("ts"))
        p=q.get("odds_dec")
        if side not in teams or not ts or not timedelta(0)<=now-ts<=timedelta(hours=2) or ts>=start or ts>poll or type(p) not in (int,float) or not math.isfinite(p) or p<=1:
            continue
        if side in prices and prices[side]!=p:
            return None
        prices[side]=p
    if len(prices)!=2 or prices[teams[0]]==prices[teams[1]]:
        return None
    return dict(teams=teams,prices=prices,start=start.isoformat(),captured=now.isoformat())

def favorite_diagnostic(row,records):
    teams=[name(row.get(k)) for k in ("home","away")]
    start=stamp(row.get("kickoff_utc"))
    if not start or not all(teams) or teams[0]==teams[1]:
        return None,"invalid_live_identity"
    candidates=[]
    reasons=set()
    for r in records:
        if not isinstance(r,dict):
            continue
        rt=set(name(t) for t in r.get("teams",[]))
        if rt!=set(teams):
            if rt.intersection(teams):
                reasons.add("one_team_only")
            continue
        rs,cap=stamp(r.get("start")),stamp(r.get("captured"))
        if not rs or not cap or cap>=min(rs,start):
            reasons.add("invalid_capture")
            continue
        if abs(rs-start)>timedelta(minutes=30):
            reasons.add("kickoff_mismatch")
            continue
        normalized_prices={}
        conflict=False
        for k,v in r.get("prices",{}).items():
            canonical=name(k)
            if canonical in normalized_prices and normalized_prices[canonical]!=v:
                conflict=True
            normalized_prices[canonical]=v
        if conflict:
            reasons.add("invalid_prices")
            continue
        p=[normalized_prices.get(t) for t in teams]
        if all(type(x) in (int,float) and math.isfinite(x) and x>1 for x in p) and p[0]!=p[1]:
            candidates.append((0 if p[0]<p[1] else 1,p))
        else:
            reasons.add("invalid_prices")
    if len(candidates)==1:
        return candidates[0],"matched"
    if candidates:
        return None,"ambiguous"
    for reason in ("invalid_prices","kickoff_mismatch","invalid_capture","one_team_only"):
        if reason in reasons:
            return None,reason
    return None,"no_cached_team_pair"

def favorite(row,records):
    return favorite_diagnostic(row,records)[0]
