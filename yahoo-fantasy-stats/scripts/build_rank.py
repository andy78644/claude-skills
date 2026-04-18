"""Build the rank comparison table PNG (Image 3).

Input JSON (stdin or --input):
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
    }, ...
  ]
}

Teams should be pre-sorted by actual rank ascending for display.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_png import html_to_png  # noqa: E402


CSS = """
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 32px;
  font-family: -apple-system, "Helvetica Neue", "PingFang TC", "Microsoft JhengHei", Arial, sans-serif;
  background: #ffffff;
  color: #222;
  font-size: 15px;
}
table { border-collapse: collapse; margin: 0 auto; }
th, td {
  border: 1px solid #9a9a9a;
  padding: 6px 10px;
  text-align: center;
  white-space: nowrap;
}
.section-actual { background: #dceafc; color: #2a4980; font-weight: 700; }
.section-weekly { background: #fbd6b8; color: #7a3d12; font-weight: 700; }
.section-cumulative { background: #d6e8c7; color: #3f6022; font-weight: 700; }
.section-diff { background: #f5f5f5; color: #333; font-weight: 700; }
.group-header th { font-size: 16px; padding: 8px 10px; }
.sub-header th { font-size: 13px; font-weight: 600; }
.team-name { font-weight: 800; color: #2d6f4a; text-align: center; }
.actual-cell { background: #eff6fd; }
.weekly-strength { background: #fde2cf; }
.weekly-rank { background: #fde2cf; font-weight: 700; }
.cum-strength { background: #e4f1d5; }
.cum-rank { background: #e4f1d5; font-weight: 700; }
.diff-pos { color: #a61c1c; font-weight: 700; }
.diff-neg { color: #0a6b0a; font-weight: 700; }
.diff-zero { color: #888; }
.footer-note { margin-top: 16px; text-align: center; font-size: 13px; color: #666; }
.footer-note strong { color: #444; }
"""


def diff_class(v: int) -> str:
    if v > 0:
        return "diff-pos"
    if v < 0:
        return "diff-neg"
    return "diff-zero"


def fmt_pct(v) -> str:
    try:
        return f"{float(v):.3f}"
    except (TypeError, ValueError):
        return str(v)


def render_html(payload: dict) -> str:
    teams = payload["teams"]

    group_header = """
    <tr class='group-header'>
      <th class='section-actual' colspan='5'>實際排名</th>
      <th></th>
      <th class='section-weekly' colspan='2'>逐周對戰</th>
      <th class='section-cumulative' colspan='6'>累積數據</th>
      <th></th>
      <th class='section-diff' colspan='2'>排名差值</th>
    </tr>
    """

    sub_header = """
    <tr class='sub-header'>
      <th class='section-actual'>W-L-T</th>
      <th class='section-actual'>PCT</th>
      <th class='section-actual'>GB</th>
      <th class='section-actual'>Rank</th>
      <th class='section-actual'></th>
      <th>Team</th>
      <th class='section-weekly'>強弱值</th>
      <th class='section-weekly'>排名</th>
      <th class='section-cumulative' colspan='2'>投打</th>
      <th class='section-cumulative' colspan='2'>打者</th>
      <th class='section-cumulative' colspan='2'>投手</th>
      <th></th>
      <th class='section-diff'>實際-逐周</th>
      <th class='section-diff'>實際-累積</th>
    </tr>
    <tr class='sub-header'>
      <th class='section-actual'></th>
      <th class='section-actual'></th>
      <th class='section-actual'></th>
      <th class='section-actual'></th>
      <th class='section-actual'></th>
      <th></th>
      <th class='section-weekly'></th>
      <th class='section-weekly'></th>
      <th class='section-cumulative'>強弱值</th>
      <th class='section-cumulative'>排名</th>
      <th class='section-cumulative'>強弱值</th>
      <th class='section-cumulative'>排名</th>
      <th class='section-cumulative'>強弱值</th>
      <th class='section-cumulative'>排名</th>
      <th></th>
      <th class='section-diff'></th>
      <th class='section-diff'></th>
    </tr>
    """

    rows = []
    for t in teams:
        a = t["actual"]
        w = t["weekly"]
        ct = t["cumulative_total"]
        cb = t["cumulative_batter"]
        cp = t["cumulative_pitcher"]
        wlt = f"{a['W']}-{a['L']}-{a['T']}"
        rows.append(f"""
        <tr>
          <td class='actual-cell'>{wlt}</td>
          <td class='actual-cell'>{fmt_pct(a['PCT'])}</td>
          <td class='actual-cell'>{a['GB']}</td>
          <td class='actual-cell'>{a['rank']}</td>
          <td></td>
          <td class='team-name'>{t['name']}</td>
          <td class='weekly-strength'>{w['strength']}</td>
          <td class='weekly-rank'>{w['rank']}</td>
          <td class='cum-strength'>{ct['strength']}</td>
          <td class='cum-rank'>{ct['rank']}</td>
          <td class='cum-strength'>{cb['strength']}</td>
          <td class='cum-rank'>{cb['rank']}</td>
          <td class='cum-strength'>{cp['strength']}</td>
          <td class='cum-rank'>{cp['rank']}</td>
          <td></td>
          <td class='{diff_class(t['diff_weekly'])}'>{t['diff_weekly']}</td>
          <td class='{diff_class(t['diff_cumulative'])}'>{t['diff_cumulative']}</td>
        </tr>
        """)

    title = payload.get("title", "Rank Comparison")

    return f"""<!doctype html>
<html><head><meta charset='utf-8'><title>{title}</title>
<style>{CSS}</style>
</head><body>
<table>
  <thead>{group_header}{sub_header}</thead>
  <tbody>{''.join(rows)}</tbody>
</table>
<p class='footer-note'>數值為「實際」減去「逐週對戰 or 累積數據」。<strong>數值越大，代表比較衰</strong>。</p>
</body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", help="JSON input file (else stdin)")
    ap.add_argument("--output", "-o", required=True, help="PNG output path")
    ap.add_argument("--width", type=int, default=1500)
    ap.add_argument("--height", type=int, default=800)
    ap.add_argument("--html-only", action="store_true")
    args = ap.parse_args()

    raw = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
    payload = json.loads(raw)

    html = render_html(payload)
    html_path = Path(args.output).with_suffix(".html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")

    if not args.html_only:
        html_to_png(html, args.output, width=args.width, height=args.height)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
