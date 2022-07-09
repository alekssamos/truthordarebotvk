import unittest
from services.game import make_pairs_of_players as make # type: ignore

class TestServicesGameMakePairs(unittest.TestCase):
    def setUp(self):
        self.        players = list("qwerty")

    def test_forward(self):
        expected_pairs = [('q', 'w'), ('w', 'e'), ('e', 'r'), ('r', 't'), ('t', 'y')]
        pairs = make(self.players, False)
        self.assertCountEqual(expected_pairs, pairs)
        self.assertListEqual(expected_pairs, pairs)

    def test_backward(self):
        expected_pairs = [('w', 'q'), ('e', 'w'), ('r', 'e'), ('t', 'r'), ('y', 't')]
        pairs = make(self.players, True)
        self.assertCountEqual(expected_pairs, pairs)
        self.assertListEqual(expected_pairs, pairs)

    def test_together(self):
        expected_pairs = [
                ('q', 'w'), ('w', 'e'), ('e', 'r'), ('r', 't'), ('t', 'y'),
                ('w', 'q'), ('e', 'w'), ('r', 'e'), ('t', 'r'), ('y', 't')
        ]
        pairs = make(self.players, False) + make(self.players, True)
        self.assertCountEqual(expected_pairs, pairs)
        self.assertListEqual(expected_pairs, pairs)

if __name__ == "__main__":
    unittest.main()
    