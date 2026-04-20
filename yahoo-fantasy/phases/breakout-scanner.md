# Breakout / Prospect Scanner

Load when user asks for breakout candidates, rookies, prospects, young players, or "找潛力新秀".

Goal: surface high-upside adds that raw counting stats won't reveal — players whose **role just changed** or whose **minor-league / college pedigree** signals a ceiling above their current ownership.

## Flow

1. `get_free_agents(league_key, position="...", include_stats=true)` per position of interest.
2. Filter candidates: age ≤ 25 (look up age via web search if missing from MCP output), OR rostered % rising >10% WoW.
3. For each candidate, one web search to check pedigree + current role.

## Search patterns

| Sport | Query template |
|---|---|
| MLB | `"[Player]" prospect ranking 2026 MLB Pipeline FanGraphs OR Baseball America` |
| MLB recent call-up | `"[Player]" called up 2026 AAA stats role` |
| NBA | `"[Player]" rookie fantasy 2026 role minutes starter` |
| NFL | `"[Player]" target share snap count breakout 2026` |

## Breakout signals

### MLB
- Recent call-up with **AAA OPS > .900** (bat) or **AAA ERA < 3.00 + K/9 > 10** (arm)
- Top-100 prospect list appearance in any of the major rankings
- Playing time secured by starter injury/trade, not a platoon
- Rising launch angle + Barrel% trend (confirms swing change)

### NBA
- Injury-driven promotion + **minutes doubling** from prior month
- Rookie starting (draft pedigree matters — lottery picks > late 1st > 2nd)
- USG% climbing week-over-week
- G-League stash getting first NBA starts

### NFL
- Target share rising 2+ consecutive weeks on a young WR/TE (ceiling play)
- RB2 promoted to RB1 via injury on a high-volume offense
- Rookie WR with rising air yards — box score lags target quality
- Handcuff RB where starter is DTD

### Universal
- **Ownership % trending up >10% WoW** = market consensus, move fast
- **Ownership % < 30% + clear role change** = earliest adopter window

## Output format

For each candidate:
```
CANDIDATE: [Player] ([Pos]) — [team]
Age: [N]  |  Owned: [X%] ([+Y% WoW])
Role change: [what just changed]
Skill indicator: [AAA stat / prospect rank / advanced rate]
Add priority: High | Monitor | Speculative
Roster fit: [who to drop, or "watch list only"]
```

## How to fold into the main report

Put breakout adds in their **own block** after the standard Recommended Moves section — they're different risk class (ceiling plays, not proven production). Label clearly so the user doesn't mix them with floor-based adds.
