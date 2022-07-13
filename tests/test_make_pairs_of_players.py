import unittest


class TestServicesGameMakePairs(unittest.TestCase):
    def setUp(self):
        self.players = list("qwerty")

    def test_forward(self):
        from services.game import make_pairs_of_players as make  # type: ignore

        expected_pairs = [("q", "w"), ("w", "e"), ("e", "r"), ("r", "t"), ("t", "y")]
        pairs = make(self.players, False)
        self.assertCountEqual(expected_pairs, pairs)
        self.assertListEqual(expected_pairs, pairs)

    def test_backward(self):
        from services.game import make_pairs_of_players as make  # type: ignore

        expected_pairs = [("w", "q"), ("e", "w"), ("r", "e"), ("t", "r"), ("y", "t")]
        pairs = make(self.players, True)
        self.assertCountEqual(expected_pairs, pairs)
        self.assertListEqual(expected_pairs, pairs)

    def test_together(self):
        from services.game import make_pairs_of_players as make  # type: ignore

        expected_pairs = [
            ("q", "w"),
            ("w", "e"),
            ("e", "r"),
            ("r", "t"),
            ("t", "y"),
            ("w", "q"),
            ("e", "w"),
            ("r", "e"),
            ("t", "r"),
            ("y", "t"),
        ]
        pairs = make(self.players, False) + make(self.players, True)
        self.assertCountEqual(expected_pairs, pairs)
        self.assertListEqual(expected_pairs, pairs)


if __name__ == "__main__":
    unittest.main()
