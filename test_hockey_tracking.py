import unittest
from hockey_tracking import register,settle,statistics
class TrackingTests(unittest.TestCase):
    def test_tracking(self):
        s={}
        k=register(s,"1","hockey4",None,["A","B"],live_odds=1.5)
        self.assertIsNone(register(s,"1","hockey4",None,["A","B"]))
        s["alerts"][k]["message_id"]=1
        self.assertEqual(settle(s,"1",["B","A"],[(0,0),(1,0)]),[])
        self.assertEqual(settle(s,"1",["A","B"],[(0,0),(1,0)]),[k])
        self.assertEqual(statistics(s)["hockey4"]["roi_pct"],50)
        self.assertIsNone(statistics(s)["hockey1"]["roi_pct"])
