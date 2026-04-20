# Advanced Metrics Deep-Dive

Load when user asks for deep analysis, regression check, underlying-stat review, or names a specific player to dig into.

Source: web search — these are NOT in the Yahoo MCP. Cost is non-trivial, so scope to flagged players (from Phase 2–3) plus any player the user named.

## Search patterns

| Sport | Query template |
|---|---|
| MLB batter | `"[Player]" statcast 2026 wOBA xBA Barrel` |
| MLB pitcher | `"[Player]" fangraphs 2026 FIP xFIP CSW SIERA` |
| NBA | `"[Player]" basketball-reference 2026 USG TS minutes` |
| NFL | `"[Player]" playerprofiler OR fantasypros target share air yards 2026` |

Prefer: Fangraphs, Baseball Savant, Basketball Reference, PlayerProfiler, Rotowire. Avoid aggregator blogs.

## Metrics & regression signals

### MLB batters
Collect: `wOBA`, `wRC+`, `ISO`, `BABIP`, `K%`, `BB%`, `Barrel%`, `Hard-Hit%`, `xBA`, `xSLG`.

| Signal | Read |
|---|---|
| `BABIP > .350` | Expect cooling — hot streak is partly luck |
| `xBA − AVG > .030` | Unlucky — expect rebound, consider buy-low |
| `AVG − xBA > .030` | Overperforming — expect regression |
| `Barrel% < 5%` with high HR | Power unsustainable |
| `Hard-Hit% > 45%` with low output | Quality contact, results coming |
| `wRC+ > 130` season-long | Legit hitter, don't drop on a cold week |

### MLB pitchers
Collect: `FIP`, `xFIP`, `SIERA`, `K-BB%`, `CSW%`, `SwStr%`, `GB%`.

| Signal | Read |
|---|---|
| `ERA − FIP > 1.00` | ERA will rise — fade before market catches up |
| `FIP − ERA > 1.00` | ERA will fall — buy-low window |
| `CSW% > 30%` | Elite stuff, trust the strikeouts |
| `SwStr% > 13%` | Dominant whiff rate, K upside |
| `K-BB% > 20%` | Ace-level underlying skill |
| `GB% > 50%` | Ground-ball profile, WHIP-friendly in tough parks |

### NBA
Collect: `USG%`, `TS%`, 7-day vs 30-day minutes, `+/-`.

| Signal | Read |
|---|---|
| Minutes 7d > 30d avg and USG up | Expanding role — add |
| `TS% > 58%` with `USG% > 25%` | Efficient volume scorer |
| Negative `+/-` trend + coach flux | Role risk — fade |

### NFL
Collect: `Target share`, `Air yards`, `Snap %`, red zone touches.

| Signal | Read |
|---|---|
| Target share rising 2+ weeks | Emerging WR/TE regardless of box score |
| Air yards > receiving yards for 3+ weeks | Big play coming, buy-low |
| Snap % > 70% with role change | Workhorse emerging |
| Red zone touches > 3/game | TD dependence → floor builder |

## How to fold into the main report

Add a **Regression watch** block to Roster Health showing any player where underlying stats disagree with surface results. In **Why ADD / Why DROP** reasons, cite the specific xStat gap or rate (e.g. `FIP 3.20 vs ERA 5.40 — ERA will fall`) — this is what separates this skill's recommendation from the Yahoo default view.
