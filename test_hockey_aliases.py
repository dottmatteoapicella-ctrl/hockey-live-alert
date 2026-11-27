import unittest
from hockey_odds import name
class AliasTest(unittest.TestCase):
    def test_aliases(self):
        self.assertEqual(name("WAS Capitals"),name("Washington Capitals"))
        self.assertEqual(name("FLA"),name("Florida Panthers"))
        self.assertNotEqual(name("BOS Bruins"),name("TOR Maple Leafs"))
