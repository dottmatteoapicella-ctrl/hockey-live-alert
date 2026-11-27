import unittest
from unittest.mock import patch
from datetime import datetime,timezone
from hockey_engine import cycle
class PreservePrematch(unittest.TestCase):
    def test_earliest(self):
        old=dict(teams=["chiblackhawks","nyrangers"],prices={"chiblackhawks":2.2,"nyrangers":1.7},start="2026-11-27T22:37:00+00:00",captured="2026-11-27T22:20:00+00:00")
        new=dict(teams=["chicagoblackhawks","newyorkrangers"],prices={"chicagoblackhawks":2.1,"newyorkrangers":1.8},start=old["start"],captured="2026-11-27T22:31:00+00:00")
        state={"prematch":{"legacy":old}}
        with patch("hockey_engine.prematch",return_value=new):
            report=cycle(state,[],[{"league":"NHL"}],datetime(2026,11,27,22,31,tzinfo=timezone.utc))
        self.assertEqual(state["prematch"],{"legacy":old})
        self.assertEqual(report["prematch_preserved"],1)
        self.assertEqual(report["cached_fixtures"][0]["captured"],old["captured"])
