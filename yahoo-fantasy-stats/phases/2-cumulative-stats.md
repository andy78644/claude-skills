# Phase 2: Cumulative Stats H2H Grid

Same layout as Phase 1, but stats are summed across multiple weeks (typically all played weeks of the season).

## Inputs needed

- `league_key`
- `weeks`: list of week numbers to sum (default: 1..current_week-1)
- Resolved nickname mapping + `display_order` (from Phase 0.3)

## Step 1: Fetch stats for each week

Loop through `weeks` and call:

```
mcp__yahoo-fantasy__get_league_scoreboard(league_key, week=W)
```

Run these in parallel where possible (one tool call per week, all in the same message). Keep each week's raw scoreboard output — you'll feed them directly to `aggregate.py` next.

## Step 2: Build aggregate input

Counting stats can be summed, but ratio stats (AVG, OPS, ERA, WHIP) can't be simply averaged across weeks — they must be recomputed from their underlying components. `scripts/aggregate.py` handles this correctly (IP `.1/.2` notation, AB-weighted OPS, ER/hits-allowed reconstruction from the published ratios).

Build one JSON file bundling all fetched weeks plus the nickname map:

```json
{
  "teams_map": { "<team_key>": "<nickname>", ... },
  "display_order": ["<nickname>", ...],
  "title": "3 Weeks Total Stats",
  "weeks": [
    <raw_scoreboard_week1>,
    <raw_scoreboard_week2>,
    ...
  ]
}
```

- `teams_map` / `display_order` come from Phase 0.3.
- Each entry in `weeks` is the **unmodified** output of `mcp__yahoo-fantasy__get_league_scoreboard` — `aggregate.py` reads `matchups[].teams[].team_key` and `matchups[].teams[].stats`.
- `title` defaults to `"Cumulative Stats"` if omitted; set it to something descriptive like `"5 Weeks Total Stats"`.

Save to `/tmp/yahoo-fantasy-stats/agg_input.json`.

## Step 3: Aggregate → render

```bash
python3 /Users/andy78644/Project/claude-skills/yahoo-fantasy-stats/scripts/aggregate.py \
  --input /tmp/yahoo-fantasy-stats/agg_input.json \
  --output /tmp/yahoo-fantasy-stats/cumulative.json

python3 /Users/andy78644/Project/claude-skills/yahoo-fantasy-stats/scripts/build_grid.py \
  --input /tmp/yahoo-fantasy-stats/cumulative.json \
  --output /tmp/yahoo-fantasy-stats/cumulative.png
```

`aggregate.py` emits `build_grid.py`-compatible JSON. Capture `build_grid.py`'s stdout strength summary (same shape as Phase 1) for use by Phase 3.

The rendered summary table includes Total / Batter / Pitcher **rank** columns (1–12, computed from the strength values) next to the strength cells — same layout as Phase 1.

## Step 4: Show the result

Print the PNG path. Because `aggregate.py` recomputes ratios from the published weekly ratios (not from raw H/AB/ER components, which the scoreboard endpoint doesn't expose), AVG/OPS are accurate to within rounding; ERA/WHIP may differ by ±1 in borderline H2H comparisons vs. a true component-level computation. Flag this only if the user asks for maximum precision.
