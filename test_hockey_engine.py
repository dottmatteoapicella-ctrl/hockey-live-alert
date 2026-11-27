import unittest
from datetime import datetime,timezone
from hockey_engine import cycle

class EngineTest(unittest.TestCase):
    def test_unconfirmed(self):
        state={}
        row=dict(id=1,status="live",score=dict(home=0,away=0),linescore=dict(home=[0,0],away=[0,0]))
        r=cycle(state,[row],[],datetime(2026,11,27,tzinfo=timezone.utc))
        self.assertEqual(r["cycle"]["valid_scores"],1)
        self.assertEqual(r["cycle"]["unconfirmed_periods"],1)
        self.assertEqual(r["cycle"]["alerts"],0)
        self.assertFalse(state.get("alerts"))
