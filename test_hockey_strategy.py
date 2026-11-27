import unittest
from hockey_strategy import signals,outcome,reserve
class HockeyTests(unittest.TestCase):
    def test_signals(self):
        self.assertEqual(signals([(0,1)],(0,0),0),["hockey1"])
        self.assertEqual(signals([], (0,2),0),["hockey2"])
        self.assertEqual(signals([(0,1),(1,1)],(0,0),0),["hockey3"])
        self.assertEqual(signals([(0,0)],(0,0)),["hockey4"])
        self.assertEqual(signals([(0,1),(1,0)],(0,0)),["hockey5"])
        self.assertEqual(signals([(0,0)],(1,0)),[])
        self.assertEqual(signals([],(-1,2),0),[])
    def test_outcomes(self):
        self.assertTrue(outcome("hockey1",[],0,0))
        self.assertFalse(outcome("hockey2",[],0,1))
        self.assertTrue(outcome("hockey3",[(0,1),(0,0),(1,0)],0))
        self.assertTrue(outcome("hockey4",[(0,0),(1,0)]))
        self.assertFalse(outcome("hockey5",[(0,0),(1,1),(0,0)]))
        self.assertIsNone(outcome("hockey5",[(0,0),(0,0)]))
    def test_budget(self):
        s={}
        for k,n in [("live",288),("results",200),("extra",412)]:
            for _ in range(n): self.assertTrue(reserve(s,"day1",k))
            self.assertFalse(reserve(s,"day1",k))
        self.assertTrue(reserve(s,"day2","live"))
