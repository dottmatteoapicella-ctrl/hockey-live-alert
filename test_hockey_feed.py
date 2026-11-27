import unittest
from hockey_feed import decode, diagnostic

class FeedTest(unittest.TestCase):
    def test_live_arrays(self):
        row=dict(id=1,status="live",score=dict(home=2,away=2),linescore=dict(home=[2,0],away=[2,0]))
        self.assertEqual(decode(row)["periods"],[[2,2],[0,0]])
        self.assertFalse(decode(row)["confirmed_periods"])
        self.assertEqual(diagnostic([row])["valid_arrays"],1)
        row["score"]["home"]=3
        self.assertIsNone(decode(row))
    def test_finished_aggregate_not_period_proof(self):
        row=dict(id=2,status="finished",score=dict(home=3,away=5),linescore=dict(home=[3],away=[5]))
        self.assertFalse(decode(row)["confirmed_periods"])
