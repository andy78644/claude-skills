"""Load or create the team-nickname config for yahoo-fantasy-stats.

Config location (per league):
    $YAHOO_FANTASY_STATS_CONFIG_DIR/{league_key}.json
    (default $YAHOO_FANTASY_STATS_CONFIG_DIR = ~/.config/yahoo-fantasy-stats)

Config schema:
{
  "league_key": "469.l.103062",
  "league_name": "optional label",
  "teams": {
    "469.l.103062.t.1": "子亘",
    ...
  },
  "display_order": ["子亘", "峻維", ...]   // optional; defaults to teams dict order
}

Usage:
    # Print resolved mapping (stdout JSON)
    python3 load_config.py --league-key 469.l.103062

    # Bootstrap a template from Yahoo's team list (reads JSON from stdin or --teams-json)
    python3 load_config.py --init --league-key 469.l.103062 --teams-json yahoo_teams.json

The Yahoo team list is the exact output of mcp__yahoo-fantasy__get_league_teams:
    [{"team_key": "...", "name": "...", "manager": "..."}, ...]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def config_dir() -> Path:
    env = os.environ.get("YAHOO_FANTASY_STATS_CONFIG_DIR")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".config" / "yahoo-fantasy-stats"


def config_path(league_key: str) -> Path:
    return config_dir() / f"{league_key}.json"


def load(league_key: str) -> dict | None:
    p = config_path(league_key)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"WARN: {p} is not valid JSON: {e}", file=sys.stderr)
        return None


def resolve_names(league_key: str, yahoo_teams: list[dict]) -> dict:
    """Return {'teams': {team_key: nickname}, 'display_order': [nickname, ...], 'source': 'config'|'fallback'}.

    yahoo_teams: list of {team_key, name, manager} from get_league_teams.
    If config exists, use it; otherwise fall back to Yahoo's team.name field.
    """
    cfg = load(league_key)
    if cfg and cfg.get("teams"):
        team_map: dict[str, str] = dict(cfg["teams"])
        # Make sure every yahoo team has a mapping; fall back to team.name for missing ones
        for t in yahoo_teams:
            team_map.setdefault(t["team_key"], t.get("name", t["team_key"]))
        order = cfg.get("display_order") or [
            team_map[t["team_key"]] for t in yahoo_teams
        ]
        return {"teams": team_map, "display_order": order, "source": "config"}

    team_map = {t["team_key"]: t.get("name", t["team_key"]) for t in yahoo_teams}
    return {
        "teams": team_map,
        "display_order": [team_map[t["team_key"]] for t in yahoo_teams],
        "source": "fallback",
    }


def init_template(league_key: str, yahoo_teams: list[dict], force: bool = False) -> Path:
    """Write a config template to ~/.config/.../{league_key}.json. Nicknames default to Yahoo team.name."""
    p = config_path(league_key)
    if p.exists() and not force:
        raise FileExistsError(f"{p} already exists. Use --force to overwrite.")
    p.parent.mkdir(parents=True, exist_ok=True)

    teams = {t["team_key"]: t.get("name", t["team_key"]) for t in yahoo_teams}
    template = {
        "league_key": league_key,
        "league_name": "",
        "teams": teams,
        "display_order": list(teams.values()),
        "_note": "Replace the values in `teams` with your preferred display nicknames. `display_order` controls the row order in output tables.",
    }
    p.write_text(json.dumps(template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def _cli() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--league-key", required=True)
    ap.add_argument("--teams-json", help="Path to Yahoo get_league_teams output (or stdin).")
    ap.add_argument("--init", action="store_true", help="Create a template config file.")
    ap.add_argument("--force", action="store_true", help="With --init, overwrite existing file.")
    args = ap.parse_args()

    if args.init:
        if args.teams_json:
            yahoo_teams = json.loads(Path(args.teams_json).read_text(encoding="utf-8"))
        elif not sys.stdin.isatty():
            yahoo_teams = json.loads(sys.stdin.read())
        else:
            ap.error("--init needs --teams-json or JSON piped on stdin")
        path = init_template(args.league_key, yahoo_teams, force=args.force)
        print(f"Wrote template to {path}")
        print("Edit the `teams` values to set display nicknames, then rerun the skill.")
        return 0

    # Resolve-and-print mode
    yahoo_teams = None
    if args.teams_json:
        yahoo_teams = json.loads(Path(args.teams_json).read_text(encoding="utf-8"))
    elif not sys.stdin.isatty():
        stdin_raw = sys.stdin.read().strip()
        if stdin_raw:
            yahoo_teams = json.loads(stdin_raw)

    if yahoo_teams is None:
        # No yahoo teams provided — just return the raw config if it exists
        cfg = load(args.league_key)
        print(json.dumps(cfg or {}, ensure_ascii=False, indent=2))
        return 0

    resolved = resolve_names(args.league_key, yahoo_teams)
    print(json.dumps(resolved, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
