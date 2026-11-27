import unittest
from datetime import datetime, timezone, timedelta
from hockey_engine import cycle

class H2ShadowTest(unittest.TestCase):
    def test_total_only(self):
        now=datetime(2026,11,27,21,tzinfo=timezone.utc)
        start=(now-timedelta(hours=1)).isoformat()
        state={"prematch":{"x":{"teams":["home","away"],"prices":{"home":1.5,"away":2.5},"start":start,"captured":(now-timedelta(hours=2)).isoformat()}}}
        row={"id":1,"status":"live","home":"Home","away":"Away","kickoff_utc":start,"score":{"home":0,"away":2}}
        report=cycle(state,[row],[],now)["cycle"]
        self.assertEqual(report["h2_candidates"],1)
        self.assertEqual(report["alerts"],0)
        row["score"]["away"]=1
        self.assertEqual(cycle(state,[row],[],now)["cycle"]["h2_candidates"],0)
        self.assertEqual(cycle({},[row],[],now)["cycle"]["h2_candidates"],0)
