"""Aggregate Yahoo scoreboard stats across multiple weeks, correctly recomputing
ratio stats (AVG, OPS, ERA, WHIP) from their underlying components.

Input (stdin or --input): JSON with a list of weekly scoreboards and a team nickname
map.

{
  "teams_map": {"469.l.103062.t.1": "子亘", ...},
  "display_order": ["子亘", "峻維", ...],
  "title": "3 Weeks Total Stats",
  "weeks": [
    <scoreboard_json_week1>,
    <scoreboard_json_week2>,
    <scoreboard_json_week3>
  ]
}

Each <scoreboard_json_weekN> is the raw output of mcp__yahoo-fantasy__get_league_scoreboard.

Output (stdout): JSON in build_grid.py input format.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats import (  # noqa: E402
    BATTER_CATS,
    PITCHER_CATS,
    PITCHER_LOWER_IS_BETTER,
    get_stat,
)

# Ratio stats are recomputed from components, not summed directly.
RATIO_CATS = {"AVG", "OPS"} | PITCHER_LOWER_IS_BETTER  # AVG, OPS, BB(p), ERA, WHIP
# BB(pitcher) is technically a counting stat but happens to also be in
# PITCHER_LOWER_IS_BETTER; pull it back out.
RATIO_CATS.discard("BB")
COUNTING_BATTER = [c for c in BATTER_CATS if c not in RATIO_CATS]
COUNTING_PITCHER = [c for c in PITCHER_CATS if c not in RATIO_CATS]


def parse_ip(ip_str: str) -> float:
    """Yahoo stores IP as 'X.Y' where .1 = 1/3, .2 = 2/3 innings."""
    s = str(ip_str).strip()
    if "." in s:
        whole, frac = s.split(".", 1)
        whole = int(whole)
        if frac == "0":
            return float(whole)
        if frac == "1":
            return whole + 1 / 3
        if frac == "2":
            return whole + 2 / 3
        # Fallback for unexpected formats
        return float(s)
    return float(s)


def parse_h_ab(h_ab: str) -> tuple[int, int]:
    h, ab = h_ab.split("/")
    return int(h), int(ab)


def num(x) -> float:
    if isinstance(x, str):
        x = x.strip()
        if x == "" or x == "-":
            return 0.0
        # handle ".217" style
        if x.startswith(".") or x.startswith("-."):
            x = "0" + x if x.startswith(".") else "-0" + x[1:]
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def aggregate_team(raw_weeks: list[dict]) -> dict:
    """Given a list of this team's weekly stat dicts, return aggregated batter/pitcher."""
    batter_sums = {c: 0 for c in COUNTING_BATTER}
    pitcher_sums = {c: 0 for c in COUNTING_PITCHER}

    sum_h = sum_ab = 0
    weighted_ops_num = 0.0
    weighted_ops_den = 0  # total AB
    sum_ip = 0.0
    sum_er = 0.0
    sum_hits_allowed = 0.0

    for wk in raw_weeks:
        # Counting stats — sum directly using SSoT cat lists.
        for c in COUNTING_BATTER:
            batter_sums[c] += int(num(get_stat(wk, "batter", c)))
        for c in COUNTING_PITCHER:
            pitcher_sums[c] += int(num(get_stat(wk, "pitcher", c)))

        # Ratio stat components — H/AB for AVG, AB-weighted for OPS.
        h, ab = parse_h_ab(wk["H/AB"])
        sum_h += h
        sum_ab += ab
        weighted_ops_num += num(get_stat(wk, "batter", "OPS")) * ab
        weighted_ops_den += ab

        # Pitching ratios — reconstruct ER and hits-allowed from published ratios.
        ip = parse_ip(wk["IP"])
        bb_p = int(num(get_stat(wk, "pitcher", "BB")))
        sum_ip += ip
        sum_er += num(get_stat(wk, "pitcher", "ERA")) * ip / 9.0
        sum_hits_allowed += num(get_stat(wk, "pitcher", "WHIP")) * ip - bb_p

    avg = sum_h / sum_ab if sum_ab else 0.0
    ops_avg = weighted_ops_num / weighted_ops_den if weighted_ops_den else 0.0
    era_cum = (sum_er * 9.0 / sum_ip) if sum_ip else 0.0
    whip_cum = ((sum_hits_allowed + pitcher_sums["BB"]) / sum_ip) if sum_ip else 0.0

    batter_out = dict(batter_sums)
    batter_out["AVG"] = round(avg, 3)
    batter_out["OPS"] = round(ops_avg, 3)

    pitcher_out = dict(pitcher_sums)
    pitcher_out["ERA"] = round(era_cum, 2)
    pitcher_out["WHIP"] = round(whip_cum, 2)

    return {"batter": batter_out, "pitcher": pitcher_out}


def extract_per_team_weeks(weeks: list[dict]) -> dict[str, list[dict]]:
    """Return {team_key: [week_stats_dict, ...]}"""
    per_team: dict[str, list[dict]] = {}
    for scoreboard in weeks:
        for matchup in scoreboard.get("matchups", []):
            for t in matchup.get("teams", []):
                per_team.setdefault(t["team_key"], []).append(t["stats"])
    return per_team


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", help="JSON input (else stdin)")
    ap.add_argument("--output", "-o", help="Output JSON path (else stdout)")
    args = ap.parse_args()

    raw = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
    payload = json.loads(raw)

    teams_map = payload["teams_map"]
    display_order = payload.get("display_order")
    title = payload.get("title", "Cumulative Stats")
    weeks = payload["weeks"]

    per_team_weeks = extract_per_team_weeks(weeks)

    teams_out = []
    # emit in display_order if given, else by teams_map iteration
    nickname_to_key = {v: k for k, v in teams_map.items()}
    if display_order:
        keys_in_order = [nickname_to_key[n] for n in display_order if n in nickname_to_key]
    else:
        keys_in_order = list(teams_map.keys())

    for team_key in keys_in_order:
        if team_key not in per_team_weeks:
            continue
        agg = aggregate_team(per_team_weeks[team_key])
        teams_out.append({
            "name": teams_map[team_key],
            "batter": agg["batter"],
            "pitcher": agg["pitcher"],
        })

    result = {"title": title, "teams": teams_out}
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(out + "\n", encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
