---
name: yahoo-fantasy
description: Analyze your Yahoo Fantasy sports team, evaluate roster health, compare free agents, and recommend add/drop moves. Use when user asks about fantasy team, waiver wire, roster moves, or player analysis.
---

# Yahoo Fantasy Team Analyzer

Comprehensive analysis of the user's Yahoo Fantasy team with actionable roster moves.

## Opt-in deep-dive phases

Load these detail files ONLY when the user's request triggers them. Skip otherwise — web searches are expensive.

| Trigger keywords | Load file |
|---|---|
| "深度分析" / "advanced stats" / "regression" / "xStats" / "dig into [player]" | `phases/advanced-metrics.md` |
| "找潛力新秀" / "breakout" / "prospect" / "rookie" / "young player" | `phases/breakout-scanner.md` |

## Phase 1: Auth & league discovery

Call `get_leagues`. On auth error: `authenticate` (no args) → user pastes `code=` from redirect → `authenticate(code=...)` → retry.

If multiple leagues, ask which. Record `league_key` and `my_team_key`.

**League settings** (canonical cat list): `get_league_settings(league_key)` returns `stat_categories` with `stat_id → display_name` and `sort_order` (1 = higher better, 0 = lower better). Use this — don't hardcode or guess cats. Feeds Phase 4 matchup diff and Phase 7 category-fit rubric.

**Player key lookup**: `search_players(league_key, name="...")` returns `player_key` for stats calls. Never guess keys.

## Phase 2: Roster analysis

### 2a. Week range
`get_matchup(team_key)` → `week_start`, `week_end`.

### 2b. Daily lineup scan
For each day in range, parallel-call `get_roster(team_key, date="YYYY-MM-DD")`. Per player per day record: `selected_position`, `is_bench`, `is_injured_reserve`.

### 2c. Schedule verification (avoid flagging off-days)

Cross-reference `GP` from Phase 3's `lastweek` result: if GP < active days, the gap is team off-days — not a lineup mistake. No extra API needed.

**Flag decision table:**

| Situation | Flag? |
|---|---|
| BN + team had game + player was scheduled to play/start | Yes |
| BN + team had game + player not scheduled (e.g. SP on non-start day) | No — correct |
| BN + team had no game | No — off-day |
| BN + `is_injured_reserve: true` | No — IL slot is separate |
| DTD player active at risk | Yes |
| NFL bye-week player in active slot | Yes |
| NA-status player in active slot | Yes — blocks the slot |
| Pitcher in P slot vs SP/RP slot | No — stats score identically |

### 2d. Today's lineup check
`get_roster(team_key)` (no date = today).

For every `is_bench: true`, `is_injured_reserve: false`:
- **Hitter**: flag if clearly stronger than active player at an eligible position
- **Pitcher**: flag only if confirmed start (SP) or save/hold opp (RP) today
- **NA in active slot**: always flag

Output per flag:
- Hitter: `SWAP: [BN player] → [slot], bench [active player]`
- NA: `MOVE: [NA player] out of [slot] → BN, activate [BN player]`

## Phase 3: Player stats

Batch all rostered players in 2 parallel calls:
```
get_roster_stats(team_key, stat_period="lastweek")
get_roster_stats(team_key, stat_period="season")
```

`get_roster_stats` accepts `season | lastweek | last30`. `last14` is NOT supported. `last30` returns HTTP 400 in the first ~2 weeks of the season — skip if it fails.

Single-player fallback: `get_player_stats(player_key, stat_period=..., date=...)`. Periods: `season | week | lastweek | last14 | last30 | date` (`date` requires `date="YYYY-MM-DD"`).

**Identify:**
- Underperformers: lastweek >20% below season in key cats
- Hot streaks: lastweek well above season average

## Phase 4: Current matchup

Reuse `get_matchup` from 2a. Note: score vs opp, cats ahead/behind, cats still live, streaming opportunities.

## Phase 5: Free agents

```
get_free_agents(league_key, position="...", include_stats=true)
```

`include_stats=true` avoids separate stats calls. `count` must be an int — omit to use default (25).

**Priority positions:** injured spots, underperforming starters, streaming slots (RP in MLB, flex).

**Ownership trend** (`percent_owned` + `percent_owned_delta`):
- Rising >10% WoW → market sees breakout, act fast
- Falling >10% WoW but production still solid → possible dip-buy

## Phase 6: News verification

Web search for: injured rostered players (return timeline), top FA candidates, unusual stat drops (role change / trade rumor).

Pattern: `"[Player Name]" fantasy [sport] news injury`

Yahoo injury status can lag — news is authoritative.

## Phase 7: Scoring & report

Every add/drop candidate gets a **composite 0–100 score** so trade-offs are explicit. Trust the tier, not 2-point gaps — inputs include estimation.

### Composite score

| Dimension | Weight | Notes |
|---|---|---|
| **Category fit** (live matchup / team cat needs) | 25 | See rubric below — dominant factor |
| Production vs replacement | 20 | Season stats vs median FA at same position |
| Role / opportunity | 15 | Starter lock, closer role, bell-cow, target share secured |
| Trend | 15 | lastweek vs season; direction over last 14–30 days |
| Underlying agreement | 10 | xStats vs surface — ONLY if `advanced-metrics` phase ran |
| Positional scarcity | 10 | C / SS / TE → full 10; OF / WR / RP → 3–5 |
| Schedule | 5 | Games left this week; ROS opponent strength |

If `advanced-metrics` did NOT run, rescale remaining weights ×100/90 so max stays 100.

### Category fit rubric (0–25)

This is what turns "good player" into "good FOR US, THIS WEEK". For each scoring cat in your league:

1. Get current matchup gap (you − opponent) from Phase 4.
2. Project the player's contribution this week (season rate × games remaining).
3. Apply matchup-state multiplier:

| Cat state | Multiplier |
|---|---|
| Tight, gap ≤ 2 — swing cat | ×3 |
| Behind 3–5, games remain | ×1.5 |
| Leading 3–5 | ×1.0 |
| Locked (ahead ≥ 6, OR behind ≥ 6 with no games left) | ×0.2 |

Negative cats (ERA, WHIP, NBA TO): **invert direction** — a high-ERA pitcher actively hurts when you lead ERA.

Sum weighted contributions across all cats → normalize to 0–25.

**Special cases:**
- **ROS / season-long questions** (no live matchup): substitute matchup-state with your team's season cat ranks — bottom-3 ranks ×2, top-3 ×0.5.
- **H2H-points / rotisserie leagues**: collapse cat fit to "projected points / z-score". No matchup multipliers.

### Tiers & swap threshold

| Score | Tier | Action |
|---|---|---|
| 85+ | Must add | drop almost anyone |
| 70–84 | High priority | drop weakest bench / cold player |
| 55–69 | Solid | add if clear drop candidate exists |
| 40–54 | Streamer / watch | weekly plug-ins or injury cover only |
| <40 | Pass | |

**Recommend a swap only if ADD − DROP ≥ 15.** Smaller gaps = churn, don't move.

### Report layout

Roster health block:
```
ROSTER
Active healthy: ...
Day-to-day: ... (injury note)
IL/Injured: ... (return ETA, stash-worthy?)
Cold: ...
Hot: ...
Regression watch: ...  (only if advanced-metrics ran)
```

Scored move block (full breakdown for top 3, one-liner for rest):
```
ADD: [Player] ([Pos]) — [team]    Score: XX (Tier)
DROP: [Player] ([Pos]) — [team]   Score: YY (Tier)
Gap: +Z

Breakdown — ADD:
  Cat fit       22/25  (swings SB +3, HR +1)
  Production    15/20
  Role          14/15
  Trend         11/15
  Underlying     7/10
  Scarcity       3/10
  Schedule       5/5

Why ADD: [one line]
Why DROP: [one line]
Risk: Low | Med | High — [reason]
```

One-liner for lower-priority candidates: `ADD X (72) / DROP Y (58) — gap 14, skip`.

### Streaming (if applicable)
MLB 2-start SPs, NBA back-to-back plays, NFL favorable matchups. Score using only **Category fit + Schedule** — short-term plays; other dimensions don't apply.

## Sport-specific cheat sheet

**MLB**
- SP core: ERA, WHIP, K/9, W, QS
- RP core: SV, HLD, ERA, WHIP
- Bats core: AVG, HR, RBI, R, SB
- Drop: ERA > 5.00 (SP), AVG < .220 no power, lost closer role
- Add: new closer, 10+ day hot streak, call-up getting starts
- IL stash: IL slots are separate — hold high-upside injured players

**NBA**
- Core: PTS, REB, AST, STL, BLK, 3PM, FG%, FT%, TO (neg)
- Drop: bench role, minutes restriction, cold 2+ weeks no role security
- Add: injury-driven promotion, usage/minutes uptick, favorable b2b

**NFL**
- QB: pass yds/TD, rush, INT (neg)
- RB: rush yds/TD, rec, snap %, target share
- WR/TE: targets, receptions, yds, TD, air yards
- Drop: lost WR1 role, RB committee reduction, offense collapsing
- Add: handcuff after starter injury, emerging target share, favorable ROS

## Final output structure
1. Quick summary (3–5 bullets) — include 1–2 line callout of which cats are swing cats this week
2. Roster status table
3. Top 3 scored moves (full breakdown) + one-liners for the next 3–5
4. Watch list
5. This week's focus

Keep it actionable. Injuries and significant underperformance > marginal upgrades.
