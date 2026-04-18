# Phase 1: Weekly H2H Final Grid

Reproduces the "Week N Final" table — every team's stats for one week, plus a 12×12 H2H grid showing each team's wins/losses against every other team across the 14 categories.

## Inputs needed

- `league_key`
- `week` (integer; if user didn't specify, ask or default to `current_week - 1`)
- Resolved nickname mapping + `display_order` (from Phase 0.3 — `teams: {team_key: nickname}` and ordered nicknames list)

## Step 1: Fetch weekly stats

Call:

```
mcp__yahoo-fantasy__get_league_scoreboard(league_key, week=N)
```

This returns matchup data with each team's stats for the week. Extract for each team:

```
batter: R, HR, RBI, SB, BB, AVG, OPS
pitcher: W, SV, K, QS, BB, ERA, WHIP
```

Yahoo's stat IDs map (verify with actual response — adjust if different):
- 7=R, 12=HR, 13=RBI, 16=SB, 18=BB(batter), 3=AVG, 55=OPS
- 28=W, 32=SV, 42=K, 50=QS, 39=BB(pitcher), 26=ERA, 27=WHIP

If a team did not play (bye) or stats are missing, use 0 for counting stats and skip the comparison for ratio stats (treat as tie).

## Step 2: Build the input JSON

For each scoreboard entry, look up the nickname via `teams[team_key]` (from Phase 0.3). Emit teams in the order given by `display_order` (not the order Yahoo returned them).

Compose this exact structure:

```json
{
  "title": "Week3 Final",
  "teams": [
    {
      "name": "子亘",
      "batter": {"R": 35, "HR": 6, "RBI": 28, "SB": 7, "BB": 29, "AVG": 0.217, "OPS": 0.66},
      "pitcher": {"W": 2, "SV": 3, "K": 42, "QS": 0, "BB": 20, "ERA": 4.04, "WHIP": 1.32}
    }
  ]
}
```

Save the JSON to `/tmp/yahoo-fantasy-stats/week{N}.json`.

## Step 3: Render the PNG

```bash
python3 /Users/andy78644/Project/claude-skills/yahoo-fantasy-stats/scripts/build_grid.py \
  --input /tmp/yahoo-fantasy-stats/week3.json \
  --output /tmp/yahoo-fantasy-stats/week3.png
```

The script:
1. Computes the 12×12 H2H matrix and per-team strength totals
2. Generates HTML matching the reference layout
3. Renders PNG via headless Chrome

It also prints the strength summary JSON to stdout — capture it if Phase 3 will use it:

```json
{
  "weekly": {
    "子亘": {"total": -22, "batter": -13, "pitcher": -9},
    ...
  }
}
```

## Step 4: Show the result

Tell the user the PNG path. If they ask about a specific matchup, you can read the JSON output to answer.
