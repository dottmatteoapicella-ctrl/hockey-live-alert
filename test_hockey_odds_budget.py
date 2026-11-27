import unittest
from datetime import datetime,timezone,timedelta
from hockey_odds_budget import reserve_odds
class BudgetTest(unittest.TestCase):
    def test_budget(self):
        s={}
        n=datetime(2026,11,1,tzinfo=timezone.utc)
        self.assertTrue(reserve_odds(s,n))
        self.assertFalse(reserve_odds(s,n))
        for i in range(1,16):
            self.assertTrue(reserve_odds(s,n+timedelta(minutes=90*i)))
        s["odds_budget"]["monthly"]=496
        self.assertFalse(reserve_odds(s,n+timedelta(days=1)))
        self.assertTrue(reserve_odds(s,datetime(2026,12,1,tzinfo=timezone.utc)))
        s["odds_budget"]["blocked"]=True
        self.assertFalse(reserve_odds(s,datetime(2026,12,2,tzinfo=timezone.utc)))
