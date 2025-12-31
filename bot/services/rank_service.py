from typing import Tuple, List

RANK_THRESHOLDS: List[Tuple[str, int]] = [
    ("D·Y Legend", 100000),
    ("Shadow Reaver", 90000),
    ("Fallen Wraith", 75000),
    ("Chaos Commander", 50500),
    ("Chaos Vanguard", 35000),
    ("Oblivion Force", 25500),
    ("Eclipse II", 20000),
    ("Eclipse I", 15000),
    ("Venom Adept III", 11000),
    ("Venom Adept II", 9000),
    ("Venom Adept I", 7500),
    ("Stormbreaker", 5000),
    ("Shadow Hunter", 3500),
    ("Nightshade", 2900),
    ("Major Warden", 1750),
    ("Reaper Novice", 1000),
    ("Sentinel", 500),
    ("Initiate", 0),
]


def get_rank_by_dep(dep: int) -> str:
    for name, threshold in RANK_THRESHOLDS:
        if dep >= threshold:
            return name
    return "Initiate"


def rank_order(name: str) -> int:
    # Higher index == higher rank
    names = [r[0] for r in reversed(RANK_THRESHOLDS)]
    try:
        return names.index(name)
    except ValueError:
        return 0


def multiplier_for_rank(rank_name: str) -> int:
    # If rank >= Venom Adept II -> x2; if >= Oblivion Force -> x3
    # We compare by thresholds
    order = {n: i for i, (n, _) in enumerate(RANK_THRESHOLDS[::-1])}
    va2_index = order.get('Venom Adept II', 0)
    of_index = order.get('Oblivion Force', 0)
    r_index = order.get(rank_name, 0)
    if r_index >= of_index:
        return 3
    if r_index >= va2_index:
        return 2
    return 1
