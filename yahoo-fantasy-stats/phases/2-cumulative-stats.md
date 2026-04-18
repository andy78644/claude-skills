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

Run these in parallel where possible (one tool call per week, all in the same message).

## Step 2: Aggregate per team

For each team, sum the **counting** stats (R, HR, RBI, SB, BB, W, SV, K, QS, pitcher BB) across all weeks.

For **ratio** stats (AVG, OPS, ERA, WHIP), you can't simply average week values — you need the underlying components. Two options, in order of preference:

**Option A (preferred)** — recompute from totals if MCP exposes the components:
- AVG = H / AB
- OPS = OBP + SLG (each from components)
- ERA = (ER × 9) / IP
- WHIP = (BB + H) / IP

If the scoreboard response includes H, AB, OBP, SLG, ER, IP, BB allowed, hits allowed — sum those across weeks then recompute.

**Option B (fallback)** — use season-to-date stats directly via `get_roster_stats(team_key, stat_period="season")`. Less precise (includes any pre-week-1 data) but always available.

If neither works cleanly, document the limitation in the output and use the simple weekly average for ratios — flag it in your message to the user.

## Step 3: Build the input JSON

Identical schema to Phase 1 — look up nicknames via `teams[team_key]` and emit teams in `display_order`. Only difference is `title`:

```json
{
  "title": "3 Weeks Total Stats",
  "teams": [...]
}
```

Save to `/tmp/yahoo-fantasy-stats/cumulative.json`.

## Step 4: Render

```bash
python3 /Users/andy78644/Project/claude-skills/yahoo-fantasy-stats/scripts/build_grid.py \
  --input /tmp/yahoo-fantasy-stats/cumulative.json \
  --output /tmp/yahoo-fantasy-stats/cumulative.png
```

Capture the strength summary stdout (same shape as Phase 1) for use by Phase 3.

## Step 5: Show the result

Print the PNG path and note any ratio-stat caveats from Step 2.
