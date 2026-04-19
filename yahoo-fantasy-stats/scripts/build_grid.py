"""Build the weekly / cumulative H2H grid PNG for Yahoo Fantasy Baseball.

Input JSON (stdin or --input file):
{
  "title": "Week3 Final",
  "teams": [
    {
      "name": "子亘",
      "batter": {"R": 35, "HR": 6, "RBI": 28, "SB": 7, "BB": 29, "AVG": 0.217, "OPS": 0.66},
      "pitcher": {"W": 2, "SV": 3, "K": 42, "QS": 0, "BB": 20, "ERA": 4.04, "WHIP": 1.32}
    }, ...
  ]
}

Output:
- PNG at --output path
- Strength summary JSON to stdout:
  {"title": "...", "strengths": {"子亘": {"total": -22, "batter": -13, "pitcher": -9}, ...}}
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_png import html_to_png  # noqa: E402
from stats import BATTER_CATS, PITCHER_CATS, PITCHER_LOWER_IS_BETTER  # noqa: E402

ALL_COLS = [("batter", c) for c in BATTER_CATS] + [("pitcher", c) for c in PITCHER_CATS]
COL_HEADERS = BATTER_CATS + PITCHER_CATS


def _cmp(a: float, b: float, lower_better: bool) -> int:
    if a == b:
        return 0
    if lower_better:
        return 1 if a < b else -1
    return 1 if a > b else -1


def compute_h2h(team_i: dict, team_j: dict) -> list[int]:
    """Return list of 14 ints (+1/0/-1), one per category in COL_HEADERS order."""
    out = []
    for cat in BATTER_CATS:
        out.append(_cmp(team_i["batter"][cat], team_j["batter"][cat], False))
    for cat in PITCHER_CATS:
        lb = cat in PITCHER_LOWER_IS_BETTER
        out.append(_cmp(team_i["pitcher"][cat], team_j["pitcher"][cat], lb))
    return out


def compute_all(teams: list[dict]) -> dict:
    """Return {team_name: {matrix: [[row_of_14], ...], row_totals: [...], total: int,
                          batter: int, pitcher: int}}"""
    result = {}
    names = [t["name"] for t in teams]
    for i, ti in enumerate(teams):
        matrix = []
        row_totals = []
        for j, tj in enumerate(teams):
            if i == j:
                row = [0] * 14
            else:
                row = compute_h2h(ti, tj)
            matrix.append(row)
            row_totals.append(sum(row))
        batter_sum = sum(sum(row[:7]) for row in matrix)
        pitcher_sum = sum(sum(row[7:]) for row in matrix)
        result[ti["name"]] = {
            "matrix": matrix,
            "row_totals": row_totals,
            "total": batter_sum + pitcher_sum,
            "batter": batter_sum,
            "pitcher": pitcher_sum,
            "opponents": names,
        }
    return result


def fmt_stat(cat: str, val) -> str:
    if cat in ("AVG", "OPS"):
        return f"{val:.3f}".lstrip("0") if 0 <= val < 1 else f"{val:.3f}"
    if cat in ("ERA", "WHIP"):
        return f"{val:.2f}"
    return str(int(val)) if float(val).is_integer() else str(val)


def cell_class(v: int) -> str:
    if v > 0:
        return "pos"
    if v < 0:
        return "neg"
    return "zero"


def render_summary_table(teams: list[dict], strengths: dict) -> str:
    """Top summary — each team's raw stats + strength totals."""
    head_cells = "".join(f"<th>{c}</th>" for c in COL_HEADERS)
    rows = []
    for t in teams:
        name = t["name"]
        s = strengths[name]
        stat_cells = "".join(
            f"<td>{fmt_stat(cat, t['batter'][cat])}</td>" for cat in BATTER_CATS
        ) + "".join(
            f"<td>{fmt_stat(cat, t['pitcher'][cat])}</td>" for cat in PITCHER_CATS
        )
        rows.append(
            f"<tr><th class='name'>{name}</th>{stat_cells}"
            f"<td class='total-cell'>{s['total']}</td>"
            f"<td class='sub'>{s['batter']}</td>"
            f"<td class='sub'>{s['pitcher']}</td></tr>"
        )
    return f"""
<table class='summary'>
  <thead>
    <tr><th></th>{head_cells}<th class='total-cell'>Total</th><th class='sub'>Batter</th><th class='sub'>Pitcher</th></tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
</table>
"""


def render_h2h_grid(team_name: str, team_names: list[str], data: dict) -> str:
    head_cells = "".join(f"<th>{c}</th>" for c in COL_HEADERS)
    rows = []
    matrix = data["matrix"]
    row_totals = data["row_totals"]
    my_idx = team_names.index(team_name)
    for j, opp in enumerate(team_names):
        is_self = j == my_idx
        row_cls = "self" if is_self else ""
        cells = "".join(
            f"<td class='{cell_class(v)}'>{v}</td>" for v in matrix[j]
        )
        rows.append(
            f"<tr class='{row_cls}'><th class='name'>{opp}</th>{cells}"
            f"<td class='row-total'>{row_totals[j]}</td></tr>"
        )
    return f"""
<table class='h2h'>
  <caption>{team_name}</caption>
  <thead>
    <tr><th></th>{head_cells}<th>Total</th></tr>
  </thead>
  <tbody>
    {''.join(rows)}
  </tbody>
  <tfoot>
    <tr><th colspan='15' class='strength'>Strength: {data['total']}  (Batter {data['batter']} / Pitcher {data['pitcher']})</th></tr>
  </tfoot>
</table>
"""


CSS = """
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 28px;
  font-family: -apple-system, "Helvetica Neue", "PingFang TC", "Microsoft JhengHei", Arial, sans-serif;
  background: #ffffff;
  color: #222;
  font-size: 14px;
}
h1 { margin: 0 0 20px 0; font-size: 30px; text-align: center; letter-spacing: 1px; }
table { border-collapse: collapse; margin: 0 auto 20px auto; }
th, td {
  border: 1px solid #a9a9a9;
  padding: 4px 8px;
  text-align: center;
  min-width: 30px;
  white-space: nowrap;
}
th { background: #f2f2f2; font-weight: 600; }
th.name { background: #fafafa; text-align: center; min-width: 46px; font-weight: 700; color: #2d6f4a; }
table.summary { font-size: 14px; }
table.summary td.total-cell { background: #cfe2f3; font-weight: 700; }
table.summary td.sub { background: #ead1dc; }
table.summary th.name { font-size: 15px; }
table.summary { margin-bottom: 32px; }
table.h2h { font-size: 13px; }
table.h2h caption {
  caption-side: top;
  font-size: 17px;
  font-weight: 700;
  padding: 6px;
  background: #e8f0ff;
  color: #1d4080;
  border: 1px solid #a9a9a9;
  border-bottom: none;
}
table.h2h th { font-size: 12px; }
table.h2h td { padding: 2px 5px; min-width: 24px; }
table.h2h th.name { color: #333; background: #fafafa; }
table.h2h tr.self th.name { color: #b26a00; background: #fff2b3; }
table.h2h tr.self td { background: #fff2b3; }
table.h2h td.pos { color: #0a6b0a; }
table.h2h td.neg { color: #a61c1c; }
table.h2h td.zero { color: #888; }
table.h2h td.row-total { font-weight: 700; background: #f3f3f3; color: #000; }
table.h2h tfoot th.strength {
  text-align: right;
  font-weight: 600;
  background: #f9f9f9;
  padding: 5px 10px;
  font-size: 12px;
}
.grid { display: grid; grid-template-columns: repeat(3, max-content); gap: 20px 24px; justify-content: center; }
"""


def render_html(payload: dict) -> str:
    title = payload.get("title", "H2H Grid")
    teams = payload["teams"]
    team_names = [t["name"] for t in teams]
    computed = compute_all(teams)
    strengths = {n: {"total": computed[n]["total"], "batter": computed[n]["batter"], "pitcher": computed[n]["pitcher"]} for n in team_names}

    summary_html = render_summary_table(teams, strengths)
    grids = "".join(render_h2h_grid(n, team_names, computed[n]) for n in team_names)

    return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>{title}</title>
<style>{CSS}</style>
</head><body>
<h1>{title}</h1>
{summary_html}
<div class='grid'>{grids}</div>
</body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", help="JSON input file (else stdin)")
    ap.add_argument("--output", "-o", required=True, help="PNG output path")
    ap.add_argument("--width", type=int, default=2200)
    ap.add_argument("--height", type=int, default=2800)
    ap.add_argument("--html-only", action="store_true", help="Save HTML next to PNG, skip screenshot")
    args = ap.parse_args()

    raw = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
    payload = json.loads(raw)

    html = render_html(payload)

    html_path = Path(args.output).with_suffix(".html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")

    if not args.html_only:
        html_to_png(html, args.output, width=args.width, height=args.height)

    # Print summary JSON to stdout
    team_names = [t["name"] for t in payload["teams"]]
    computed = compute_all(payload["teams"])
    summary = {
        "title": payload.get("title", ""),
        "strengths": {
            n: {
                "total": computed[n]["total"],
                "batter": computed[n]["batter"],
                "pitcher": computed[n]["pitcher"],
            }
            for n in team_names
        },
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
