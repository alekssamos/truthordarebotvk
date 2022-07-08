import unittest
from services.game import make_pairs_of_players # type: ignore

class TestServicesGameMakePairs(unittest.TestCase):
    def test_make_pairs_of_players(self):
        players = [1,2,3]
        expected_pairs = [(1, 2), (1, 3), (2, 3), (3, 2), (3, 1), (2, 1)]
        pairs = make_pairs_of_players(players)
        self.assertCountEqual(expected_pairs, pairs)
        self.assertListEqual(expected_pairs, pairs)

if __name__ == "__main__":
    unittest.main()
    