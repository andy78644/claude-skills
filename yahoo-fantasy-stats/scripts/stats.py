"""Single source of truth for the league's scoring categories.

All scripts (build_grid.py, aggregate.py) import from here so the cat
list / lower-is-better set / stat_id alias is defined exactly once.

Yahoo's get_league_scoreboard returns each team's stats dict keyed by
LABEL (e.g. stats["QS"]). The numeric stat_id is also published in the
matchup's `stat_winners` array. We key by label everywhere; the stat_id
column below is reference-only (handy for debugging or future label
divergence across leagues).

If a league reports a different label for a category, add the alias to
the LABEL_ALIASES map below — then `get_stat()` will find it.
"""
from __future__ import annotations

# (canonical_label, stat_id, lower_is_better)
BATTER_CATS_DEF = [
    ("R",   7,  False),
    ("HR",  12, False),
    ("RBI", 13, False),
    ("SB",  16, False),
    ("BB",  18, False),
    ("AVG", 3,  False),
    ("OPS", 55, False),
]

PITCHER_CATS_DEF = [
    ("W",   28, False),
    ("SV",  32, False),
    ("K",   42, False),
    ("QS",  83, False),
    ("BB",  39, True),   # walks allowed
    ("ERA", 26, True),
    ("WHIP", 27, True),
]

BATTER_CATS = [c for c, _, _ in BATTER_CATS_DEF]
PITCHER_CATS = [c for c, _, _ in PITCHER_CATS_DEF]
PITCHER_LOWER_IS_BETTER = {c for c, _, lb in PITCHER_CATS_DEF if lb}

# In the scoreboard payload, batter BB is keyed "BB_B" and pitcher BB
# is "BB_P" because both share the same canonical label "BB".
SCOREBOARD_LABEL = {
    ("batter", "BB"): "BB_B",
    ("pitcher", "BB"): "BB_P",
}

# Per-category alias list. First match wins. Add labels here if a
# league reports a stat under a non-default name.
LABEL_ALIASES: dict[str, list[str]] = {
    # canonical → [aliases to try in scoreboard stats dict]
    # e.g. "QS": ["QS", "Quality Starts", "83"],
}


def scoreboard_key(side: str, cat: str) -> str:
    """Return the key used in the scoreboard `stats` dict for a given cat."""
    return SCOREBOARD_LABEL.get((side, cat), cat)


def get_stat(stats: dict, side: str, cat: str):
    """Look up a stat value from a scoreboard `stats` dict, trying aliases."""
    primary = scoreboard_key(side, cat)
    if primary in stats:
        return stats[primary]
    for alias in LABEL_ALIASES.get(cat, []):
        if alias in stats:
            return stats[alias]
    raise KeyError(f"stat {cat!r} (side={side}) not found in scoreboard payload; "
                   f"keys={sorted(stats.keys())}")
