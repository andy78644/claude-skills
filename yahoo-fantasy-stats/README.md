# yahoo-fantasy-stats

Generates three Yahoo Fantasy Baseball report tables as PNG images:

1. **Weekly H2H Final** — one week, every team vs every team across the 14 scoring categories
2. **Cumulative Stats H2H** — same matrix but summed across multiple weeks
3. **Rank Comparison** — actual W-L-T standings vs strength-derived rankings (shows who's lucky / unlucky)

## Install

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/andy78644/claude-skills.git ~/claude-skills
ln -s ~/claude-skills/yahoo-fantasy-stats ~/.claude/skills/yahoo-fantasy-stats
```

Or copy the folder directly into `~/.claude/skills/`.

## Requirements

- Claude Code
- Yahoo Fantasy MCP server (`mcp__yahoo-fantasy__*` tools available in your session)
- Python 3.10+ (stdlib only, no `pip install`)
- Chrome / Chromium — used headlessly to render HTML to PNG

## First-time setup (per league)

The skill uses your Yahoo team names out of the box, but most leagues have custom nicknames that don't match Yahoo's team/manager fields. Set up a one-time config per league:

### Option A — let the skill guide you

Run the skill once. When it reports `source: fallback`, answer yes to the setup prompt. Claude will:

1. Call `mcp__yahoo-fantasy__get_league_teams` for your league
2. Pipe the output to `scripts/load_config.py --init --league-key <key>`
3. Write a template to `~/.config/yahoo-fantasy-stats/<league_key>.json`

Then open that file, replace the names in `teams` with your league's nicknames, and adjust `display_order` to your preferred row ordering. Re-run the skill.

### Option B — manual

Copy `config.example.json` to `~/.config/yahoo-fantasy-stats/<your-league-key>.json`, then fill in your real `team_key`s and nicknames. Find your league key by running `mcp__yahoo-fantasy__get_leagues`.

### Config file format

```json
{
  "league_key": "469.l.103062",
  "league_name": "My League",
  "teams": {
    "469.l.103062.t.1": "Alice",
    "469.l.103062.t.2": "Bob"
  },
  "display_order": ["Alice", "Bob"]
}
```

- `teams` — map of Yahoo team_key → display nickname
- `display_order` — optional; controls row order in output tables. Defaults to the `teams` insertion order.
- Override the config dir with `YAHOO_FANTASY_STATS_CONFIG_DIR` env var.

## Usage

Invoke the skill:

```
/yahoo-fantasy-stats
```

Or just describe what you want:

> 幫我產 week 5 的 final 表
> Generate this season's cumulative stats table
> Show me the rank comparison

Claude will run through Phase 0 (auth + league + team nicknames) then the requested phase.

PNGs are written to `/tmp/yahoo-fantasy-stats/`.

## Files

```
yahoo-fantasy-stats/
├── SKILL.md                        # main entry + routing
├── phases/
│   ├── 1-weekly-final.md
│   ├── 2-cumulative-stats.md
│   └── 3-rank-comparison.md
├── scripts/
│   ├── aggregate.py                # Phase 2 multi-week aggregator (ratio recompute)
│   ├── build_grid.py               # Phase 1/2 renderer
│   ├── build_rank.py               # Phase 3 renderer
│   ├── load_config.py              # nickname config loader
│   └── render_png.py               # headless Chrome HTML→PNG
├── config.example.json             # template for per-league config
└── README.md
```

## Computation notes

**Scoring categories** (higher-is-better unless noted):

- Batter: `R, HR, RBI, SB, BB, AVG, OPS`
- Pitcher: `W, SV, K, QS`, plus `BB, ERA, WHIP` (lower-is-better)

**Strength score** for each team = sum, over every other team and every category, of:
- `+1` if you're ahead in that category
- `-1` if you're behind
- `0` if tied

Max range for a 12-team league: `[-154, +154]`. Sum across the whole league is always `0`.

## Troubleshooting

- **`Chrome not found`** — edit `scripts/render_png.py` `CHROME_CANDIDATES` with your browser path.
- **Wrong stat IDs** — Yahoo's scoreboard returns stats dual-indexed by label (`R`, `HR`, etc.) and numeric id. The scripts use the label form, so stat-id changes across seasons won't break anything.
- **Cumulative ratio stats off** — AVG/OPS/ERA/WHIP can't be simply averaged across weeks; Phase 2 docs explain the options.
