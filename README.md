# Claude Skills

A collection of Claude Code skills for various workflows and integrations.

## Skills

| Skill | Description |
|-------|-------------|
| [yahoo-fantasy](./yahoo-fantasy/) | Yahoo Fantasy Sports team analysis and waiver wire recommendations |

## Installation

Copy any skill folder into your Claude Code skills directory:

```bash
# Install a specific skill
cp -r yahoo-fantasy ~/.claude/skills/
```

Or clone the whole repo and symlink:

```bash
git clone https://github.com/andy78644/claude-skills.git ~/claude-skills
ln -s ~/claude-skills/yahoo-fantasy ~/.claude/skills/yahoo-fantasy
```

## Usage

After installing, invoke with:

```
/yahoo-fantasy
```

Or let Claude auto-trigger based on context.

## Requirements

- [Claude Code](https://claude.ai/code)
- Relevant MCP servers per skill (see each skill's README)
