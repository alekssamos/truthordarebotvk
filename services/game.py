from typing import Any, List, Tuple


def make_pairs_of_players(players: list) -> List[Tuple[Any, Any]]:
    "Генерирует пары игроков"
    from itertools import combinations

    pairs = list(combinations(players, 2)) + list(combinations(players[::-1], 2))
    return pairs
