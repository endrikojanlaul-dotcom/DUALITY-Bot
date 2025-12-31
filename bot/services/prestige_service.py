from typing import Tuple


def prestige_threshold_for_level(level: int) -> int:
    # Level 1-10: every 100,000
    if level <= 10:
        return 100_000 * level
    if level <= 20:
        # levels 11-20 are every 500,000
        return 100_000 * 10 + 500_000 * (level - 10)
    if level <= 30:
        return 100_000 * 10 + 500_000 * 10 + 1_000_000 * (level - 20)
    # Above 30: exponential-ish growth: base + (level-30)*2_000_000
    return 100_000 * 10 + 500_000 * 10 + 1_000_000 * 10 + 2_000_000 * (level - 30)


def compute_prestige(lifetime_dep: int) -> int:
    # Determine prestige level given lifetime_dep
    level = 0
    while True:
        threshold = prestige_threshold_for_level(level + 1)
        if lifetime_dep >= threshold:
            level += 1
            continue
        break
    return level
