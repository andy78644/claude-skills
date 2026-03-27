---
name: yahoo-fantasy
description: Analyze your Yahoo Fantasy sports team, evaluate roster health, compare free agents, and recommend add/drop moves. Use when user asks about fantasy team, waiver wire, roster moves, or player analysis.
---

# Yahoo Fantasy Team Analyzer

Perform a comprehensive analysis of the user's Yahoo Fantasy team and recommend roster moves.

## Phase 1: Authentication & League Discovery

First, get leagues. If this fails with an auth error, run authentication:

```
mcp__yahoo-fantasy__get_leagues
```

If auth is needed:
1. Call `mcp__yahoo-fantasy__authenticate` (no args) — this opens the browser
2. Ask user to paste the `code=` value from the redirect URL
3. Call `mcp__yahoo-fantasy__authenticate` with the code
4. Retry `get_leagues`

Display available leagues and ask user which one to analyze (if multiple). For each league found, note the `league_key` and `my_team_key`.

## Phase 2: Roster Analysis

Get the current roster:

```
mcp__yahoo-fantasy__get_roster(team_key)
```

For each rostered player, collect:
- Name, position, status (injured/healthy/DTD)
- Injury notes
- Player key (for stats lookup)

**Flag immediately:**
- Any player with IL/IR status
- Day-to-day (DTD) players
- Players on bye week (NFL)

## Phase 3: Player Stats Deep-Dive

For each rostered player (parallelize where possible), get stats across multiple periods:

```
mcp__yahoo-fantasy__get_player_stats(player_key, stat_period="last14")
mcp__yahoo-fantasy__get_player_stats(player_key, stat_period="lastweek")
```

Also get season stats for context:
```
mcp__yahoo-fantasy__get_player_stats(player_key, stat_period="season")
```

**Build a player scorecard for each rostered player:**

| Metric | Last Week | Last 14 Days | Season |
|--------|-----------|--------------|--------|
| Key stats per position | ... | ... | ... |

**Identify underperformers:** Players whose last-14-day stats are significantly below their season averages (>20% drop in key categories).

**Identify hot players:** Players trending upward (last week >> season average).

## Phase 4: Current Matchup Context

Get the current week matchup to understand what categories/positions matter most right now:

```
mcp__yahoo-fantasy__get_matchup(team_key)
```

Note:
- Current score vs opponent
- Categories where you're ahead/behind
- Categories still being played
- Which positions are streaming opportunities

## Phase 5: Free Agent Analysis

Search for top available free agents by position. Focus on positions where your roster is weakest:

```
mcp__yahoo-fantasy__get_free_agents(league_key, position="...", count=20)
```

**Priority positions to check:**
- Any position where you have an injured player
- Positions where your starters are underperforming
- Streaming positions (RP in MLB, flexible spots)

For promising free agents (top 5-10 per weak position), get their recent stats:
```
mcp__yahoo-fantasy__get_player_stats(fa_player_key, stat_period="last14")
mcp__yahoo-fantasy__get_player_stats(fa_player_key, stat_period="lastweek")
```

## Phase 6: Recent News & Injury Verification

Use web search to verify player statuses and get recent news for:
1. Any injured rostered players (return timeline?)
2. Top free agent candidates (recent performance, role changes)
3. Players with unusual stat drops (trade rumors? role reduction?)

Search pattern: `"[Player Name]" fantasy [sport] [2025 or current year] news injury`

**Cross-reference:** Yahoo injury status vs. actual recent news. Yahoo data can lag — verify with news.

## Phase 7: Analysis & Recommendations

### Roster Health Report

```
ROSTER STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Active & Healthy: [list]
⚠️  Day-to-Day: [list + injury note]
🚑 Injured/IL: [list + expected return]
📉 Cold streak: [list + recent stats]
🔥 Hot streak: [list + recent stats]
```

### Waiver/Free Agent Targets

For each recommended move, provide:

```
RECOMMENDED MOVE #N
━━━━━━━━━━━━━━━━━
ADD:  [Player Name] ([Position]) — [team]
DROP: [Player Name] ([Position]) — [team]

Why ADD: [last14 stats] | [recent news/role]
Why DROP: [underperforming data] or [injury] or [better option available]
Risk: Low/Medium/High — [brief reason]
Matchup boost: [if relevant to current week categories]
```

### Priority Order

Rank recommendations by urgency:
1. **Immediate** — injury replacement needed now
2. **High** — significant upgrade available
3. **Consider** — marginal improvements, monitor

### Streaming Suggestions (if applicable)

For one-start/two-start pitchers (MLB) or matchup-based players (NBA/NFL), list weekly streaming targets from free agents.

## Analysis Framework by Sport

### MLB Fantasy
**Key stats by position:**
- SP: ERA, WHIP, K/9, wins, QS
- RP: Saves, holds, ERA, WHIP
- C/1B/2B/3B/SS: AVG, HR, RBI, R, SB (as applicable)
- OF: AVG, HR, RBI, R, SB

**Drop triggers:** ERA > 5.00 (SP), AVG < .220 with no power, losing closer role

**Add triggers:** New closer, player hot for 10+ days, injury fill-in getting starts

### NBA Fantasy
**Key stats:** PTS, REB, AST, STL, BLK, 3PM, FG%, FT%, TO (negative)

**Drop triggers:** Coming off bench, minutes restriction, cold 2+ weeks with no role security

**Add triggers:** Injury promotion to starter, recent uptick in minutes/usage, back-to-back schedule advantage

### NFL Fantasy
**Key stats by position:**
- QB: Pass yards, TDs, rush contribution, INTs (negative)
- RB: Rush yards, TDs, receptions, snap %, target share
- WR/TE: Targets, receptions, yards, TDs, air yards
- K: FG%, distance, team scoring opportunities
- DEF: Points allowed, sacks, TOs

**Drop triggers:** Losing WR1 role, RB committee reduction, team's offense struggling

**Add triggers:** Handcuff with injury to starter, emerging target share, favorable ROS schedule

## Output Format

1. **Quick Summary** — 3-5 bullet health check of team
2. **Roster Status Table** — all players with status/trend
3. **Top 3 Recommended Moves** — specific add/drop pairs with reasoning
4. **Watch List** — players to monitor (not act on yet)
5. **This Week's Focus** — matchup-specific advice

Keep analysis actionable. Prioritize moves that address current injuries or significant underperformance over marginal upgrades.
