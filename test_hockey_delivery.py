import unittest
from unittest.mock import Mock
from hockey_delivery import deliver_h2

class DeliveryTest(unittest.TestCase):
    def test_delivery(self):
        state={"prematch":{"x":{"teams":["home","away"],"prices":{"home":1.5,"away":2.5},"start":"2026-11-27T20:00:00+00:00","captured":"2026-11-27T19:00:00+00:00"}}}
        row={"id":1,"status":"live","home":"Home","away":"Away","kickoff_utc":"2026-11-27T20:00:00+00:00","score":{"home":0,"away":2}}
        tg=Mock()
        tg.send.return_value=12
        tg.edit.return_value=True
        persist=Mock()
        deliver_h2(state,[row],tg,persist)
        tg.send.assert_not_called()
        deliver_h2(state,[row,row],tg,persist,True)
        tg.send.assert_called_once()
        row.update(status="finished",score={"home":3,"away":2})
        deliver_h2(state,[row],tg,persist,True)
        tg.edit.assert_not_called()
        deliver_h2(state,[row,row],tg,persist,True,True)
        tg.edit.assert_called_once()
        self.assertTrue(state["alerts"]["1:hockey2"]["result"])
