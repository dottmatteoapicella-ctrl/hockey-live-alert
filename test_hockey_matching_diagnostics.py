import unittest
from hockey_odds import favorite_diagnostic
class MatchingDiagnostics(unittest.TestCase):
    def test_reasons(self):
        row=dict(home="Boston Bruins",away="Toronto Maple Leafs",kickoff_utc="2026-11-27T20:00:00Z")
        r=dict(teams=["bostonbruins","torontomapleleafs"],start="2026-11-27T20:00:00Z",captured="2026-11-27T19:00:00Z",prices={"bostonbruins":1.6,"torontomapleleafs":2.3})
        self.assertEqual(favorite_diagnostic(row,[]),(None,"no_cached_team_pair"))
        self.assertEqual(favorite_diagnostic(row,[r]),((0,[1.6,2.3]),"matched"))
        self.assertEqual(favorite_diagnostic(row,[r,r]),(None,"ambiguous"))
        self.assertEqual(favorite_diagnostic(row,[dict(r,start="2026-11-27T21:00:00Z")]),(None,"kickoff_mismatch"))
        self.assertEqual(favorite_diagnostic(row,[dict(r,captured="2026-11-27T20:00:00Z")]),(None,"invalid_capture"))
        self.assertEqual(favorite_diagnostic(row,[dict(r,teams=["bostonbruins","other"])]),(None,"one_team_only"))
