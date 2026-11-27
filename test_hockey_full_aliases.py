import unittest
from hockey_odds import ALIASES,name,favorite
class FullAliases(unittest.TestCase):
    def test_unique(self):
        self.assertEqual(len(ALIASES),32)
        seen={}
        for team,aliases in ALIASES.items():
            for alias in [team]+aliases:
                self.assertEqual(name(alias),team)
                self.assertNotIn(alias,seen)
                seen[alias]=team
    def test_legacy_cache(self):
        row=dict(home="Chicago Blackhawks",away="New York Rangers",kickoff_utc="2026-11-27T22:30:00Z")
        r=dict(teams=["chiblackhawks","nyrangers"],prices={"chiblackhawks":2.2,"nyrangers":1.7},start="2026-11-27T22:37:00Z",captured="2026-11-27T22:29:00Z")
        self.assertEqual(favorite(row,[r]),(1,[2.2,1.7]))
        self.assertIsNone(favorite(row,[dict(r,captured="2026-11-27T22:30:00Z")]))
        self.assertIsNone(favorite(row,[r,r]))
