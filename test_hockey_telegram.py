import unittest
from unittest.mock import patch
from hockey_telegram import Telegram

class TelegramTest(unittest.TestCase):
    def test_delivery_id(self):
        t=Telegram("unused","unused")
        for value in (None,False,True,0,-1,"12",12):
            with patch.object(t,"call",return_value={"message_id":value}):
                self.assertEqual(t.send("test"),12 if type(value) is int and value==12 else None)
