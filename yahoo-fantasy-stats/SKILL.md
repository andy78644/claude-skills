---
name: yahoo-fantasy-stats
description: Generate Yahoo Fantasy Baseball weekly/cumulative H2H comparison tables and ranking analysis as PNG images. Use when user asks for fantasy stats tables, weekly H2H matrix, cumulative stats grid, or rank comparison report.
---

# Yahoo Fantasy Stats Tables

Produces three PNG report tables from Yahoo Fantasy Baseball league data:

| Phase | Output | Detail file |
|-------|--------|-------------|
| 1 | Weekly H2H final grid (single week, all teams vs all teams across 14 cats) | `phases/1-weekly-final.md` |
| 2 | Cumulative H2H grid (sum across N weeks) | `phases/2-cumulative-stats.md` |
| 3 | Rank comparison: actual standings vs strength-derived ranks | `phases/3-rank-comparison.md` |

User can request a single phase or all three.

## Phase 0: Setup

### 0.1 Authenticate

Try a cheap MCP call first. If it fails with auth error, run authentication flow:

```
mcp__yahoo-fantasy__get_leagues
```

If auth needed:
1. Call `mcp__yahoo-fantasy__authenticate` (no args) to open browser
2. Ask user to paste the `code=` value from the redirect URL
3. Call `mcp__yahoo-fantasy__authenticate` with the code
4. Retry `get_leagues`

### 0.2 League discovery

From `get_leagues`, identify the MLB league. If multiple, ask user which one. Save:
- `league_key`
- `current_week` (from league info)

### 0.3 Team list + nickname resolution

Get the raw team list:

```
mcp__yahoo-fantasy__get_league_teams(league_key)
```

Then resolve display nicknames by piping the Yahoo output through `load_config.py`:

```bash
echo '<yahoo_teams_json>' | python3 scripts/load_config.py --league-key <league_key>
```

This returns:

```json
{
  "teams": {"469.l.103062.t.1": "子亘", ...},
  "display_order": ["子亘", "峻維", ...],
  "source": "config" | "fallback"
}
```

- `source: "config"` — the user has `~/.config/yahoo-fantasy-stats/{league_key}.json` set up with custom nicknames. Use it as-is.
- `source: "fallback"` — no config file found. The mapping is just `team_key → Yahoo team name`. This works but doesn't give custom nicknames.

**If source is `fallback`**, ask the user:

> 沒有找到暱稱設定檔。要用 Yahoo 的 team name 繼續，還是先建一份 nickname 設定檔？

If they want to set up:

```bash
echo '<yahoo_teams_json>' | python3 scripts/load_config.py --init --league-key <league_key>
```

This writes a template at `~/.config/yahoo-fantasy-stats/{league_key}.json`. Tell the user to edit the `teams` values (currently Yahoo team names) into their preferred nicknames, and adjust `display_order` for their preferred row ordering. Then re-run the skill.

**Store the resolved `teams` dict and `display_order`** — they are the canonical mapping and row order used by every subsequent phase.

## Routing

Ask the user which output they want unless it's clear from the request:

- "週報" / "week N final" / "本週對戰結果" → Phase 1
- "累積" / "cumulative" / "賽季總和" → Phase 2
- "排名比較" / "rank comparison" / "強弱值" → Phase 3 (auto runs 1+2 first to get strength values)
- "全部" / "all three" → run all three sequentially

For Phase 3, you must have run Phase 1 (sum across weeks) and Phase 2 first to get the strength values per team.

## Output convention

All scripts write PNG files to `/tmp/yahoo-fantasy-stats/`. Tell the user the absolute path when done so they can open it.

## Computation rules (used across phases)

**Stat categories** — order matters for rendering:

- Batter (7, higher is better): `R, HR, RBI, SB, BB, AVG, OPS`
- Pitcher (7): `W, SV, K, QS, BB, ERA, WHIP`
  - Higher is better: `W, SV, K, QS`
  - Lower is better: `BB, ERA, WHIP` (BB here = walks issued)

**H2H comparison** between team_i and team_j for each stat:

```
+1 if team_i is better
-1 if team_j is better
 0 if tied
```

**Strength score for team_i** = sum over all (j ≠ i, all 14 stats) of the comparison value. Each H2H matchup contributes a number in [-14, +14]; total strength is in [-154, +154] for a 12-team league.

**Sub-strengths**:
- Batter strength: only sum the 7 batter cats
- Pitcher strength: only sum the 7 pitcher cats

## Dependencies

Scripts use only Python stdlib + Chrome headless (already installed at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`). No `pip install` required.
