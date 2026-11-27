import unittest
from datetime import datetime,timezone
from hockey_odds import prematch,favorite

class OddsTest(unittest.TestCase):
    def test_strict(self):
        now=datetime(2026,11,27,19,tzinfo=timezone.utc)
        row=dict(league="NHL",in_play=False,home="Boston Bruins",away="Toronto Maple Leafs",kickoff_utc="2026-11-27T20:00:00Z",polled_at="2026-11-27T18:59:00Z")
        row["quotes"]=[dict(group_id=972,market_id=973,group_name="Game",line="To Win",suspended=False,side=t,odds_dec=p,ts="2026-11-27T18:55:00Z") for t,p in [(row["home"],1.6),(row["away"],2.3)]]
        record=prematch(row,now)
        self.assertIsNotNone(record)
        self.assertEqual(favorite(row,[record]),(0,[1.6,2.3]))
        self.assertIsNone(favorite(row,[record,record]))
        row["quotes"][0]["suspended"]=None
        self.assertIsNone(prematch(row,now))
