# Phase 3: Rank Comparison Table

Produces the summary table comparing actual W-L-T standings against the strength-value rankings derived from Phase 1 (weekly H2H sum) and Phase 2 (cumulative stats H2H).

## Prerequisites

You must have already run:
- Phase 1 for **each played week** (or have a saved sum) → sum of weekly H2H strength per team
- Phase 2 once → cumulative total / batter / pitcher strengths

If not yet run, do those first. Aggregate weekly strengths by summing each team's `total` value across all weeks.

## Step 1: Get actual standings

```
mcp__yahoo-fantasy__get_league_standings(league_key)
```

Extract per team (look up nickname via Phase 0.3's `teams[team_key]`):
- `name` (nickname)
- `W`, `L`, `T` (wins/losses/ties)
- `PCT` (win pct)
- `GB` (games behind leader, may be `"-"` for #1)
- `rank` (current standing)

## Step 2: Aggregate weekly strengths

For each team, sum the per-week `total` strength values produced by Phase 1 across all played weeks. Call this `weekly_h2h_strength`.

Compute `weekly_h2h_rank` by ordering teams from highest to lowest strength (1 = strongest).

## Step 3: Use Phase 2 outputs

From Phase 2's stdout JSON, get for each team:
- `cumulative_total` (== batter + pitcher)
- `cumulative_batter`
- `cumulative_pitcher`

Compute ranks for each (1 = strongest). Lower-is-better stats are already handled inside the strength calculation, so just sort descending.

## Step 4: Compute rank differentials

For each team:
- `diff_actual_vs_weekly = actual_rank - weekly_h2h_rank`
- `diff_actual_vs_cumulative = actual_rank - cumulative_total_rank`

Positive number = the team's actual rank is *worse* than what their stats suggest (i.e., underperforming relative to strength). The reference image labels this as "數值越大，代表比較衰" (higher = unluckier).

## Step 5: Build the input JSON

```json
{
  "teams": [
    {
      "name": "子亘",
      "actual": {"W": 17, "L": 22, "T": 3, "PCT": 0.44, "GB": "11", "rank": 8},
      "weekly": {"strength": -122, "rank": 10},
      "cumulative_total": {"strength": -66, "rank": 10},
      "cumulative_batter": {"strength": -15, "rank": 7},
      "cumulative_pitcher": {"strength": -51, "rank": 12},
      "diff_weekly": -2,
      "diff_cumulative": -2
    }
  ]
}
```

Order teams by actual rank ascending (1 first) for the output.

Save to `/tmp/yahoo-fantasy-stats/rank.json`.

## Step 6: Render

```bash
python3 /Users/andy78644/Project/claude-skills/yahoo-fantasy-stats/scripts/build_rank.py \
  --input /tmp/yahoo-fantasy-stats/rank.json \
  --output /tmp/yahoo-fantasy-stats/rank.png
```

## Step 7: Show the result

Tell the user the PNG path. Optionally call out the most extreme `diff` values — those are the "luckiest" and "unluckiest" teams of the season.
