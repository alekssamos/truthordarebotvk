from typing import Any, List, Optional, Tuple


def make_pairs_of_players(
    players: list,
    back_order:Optional[bool] = False
) -> List[Tuple[Any, Any]]:
    "Генерирует пары игроков"
    if len(players) < 2: return [] # type: ignore
    pairs:list = []
    for i in range(len(players)):
        pair = None
        try:
            pair = [players[i], players[i+1]]
            if back_order:
                pair = pair[::-1]
            pairs.append((pair[0], pair[1]))
        except IndexError:
            pass
    return pairs
