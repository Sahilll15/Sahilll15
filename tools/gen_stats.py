#!/usr/bin/env python3
"""Generate assets/panel-stats.svg — a custom IDE-themed stats panel built from
live GitHub data. Run locally (`python3 tools/gen_stats.py`) or via the
stats-refresh workflow. Requires `gh` authenticated (GH_TOKEN in CI)."""
import collections
import datetime
import json
import os
import subprocess

USER = "Sahilll15"
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "panel-stats.svg")

# theme
ACID, BLUE, INK, DIM, FAINT, BG, PANEL = (
    "#e2ff2d", "#5b8cff", "#f4f6f3", "#7e8576", "#4c5346", "#0b0e09", "#0d100c",
)


def gh(path):
    return json.loads(subprocess.check_output(["gh", "api", "--paginate", path], text=True))


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    user = json.loads(subprocess.check_output(["gh", "api", f"/users/{USER}"], text=True))
    repos = gh(f"/users/{USER}/repos?per_page=100")
    own = [r for r in repos if not r.get("fork")]

    stars = sum(r["stargazers_count"] for r in own)
    forks = sum(r["forks_count"] for r in own)
    langs = collections.Counter(r["language"] for r in own if r.get("language"))
    top = langs.most_common(6)
    total = sum(c for _, c in top) or 1
    since = datetime.datetime.fromisoformat(user["created_at"].replace("Z", "+00:00")).strftime("%b %Y")
    synced = datetime.datetime.utcnow().strftime("%d %b %Y")

    overview = [
        ("repositories", user["public_repos"]),
        ("total stars", stars),
        ("total forks", forks),
        ("followers", user["followers"]),
        ("following", user["following"]),
        ("member since", since),
    ]

    rows = []
    for i, (label, val) in enumerate(overview):
        y = 150 + i * 30
        rows.append(
            f'<text x="48" y="{y}" class="m" font-size="14" fill="{DIM}">{esc(label)}</text>'
            f'<text x="430" y="{y}" text-anchor="end" class="m" font-size="14" fill="{INK}">{esc(val)}</text>'
        )

    bars = []
    BARX, BARW = 760, 300
    for i, (lang, count) in enumerate(top):
        y = 150 + i * 30
        pct = count / total * 100
        w = max(6, round(BARW * count / top[0][1]))
        bars.append(
            f'<text x="600" y="{y}" class="m" font-size="13.5" fill="{INK}">{esc(lang)}</text>'
            f'<rect x="{BARX}" y="{y-11}" width="{BARW}" height="9" rx="4.5" fill="{FAINT}" opacity="0.4"/>'
            f'<rect x="{BARX}" y="{y-11}" width="0" height="9" rx="4.5" fill="{ACID}">'
            f'<animate attributeName="width" from="0" to="{w}" dur="1.1s" begin="{0.15*i:.2f}s" fill="freeze" calcMode="spline" keyTimes="0;1" keySplines="0.22 1 0.36 1"/></rect>'
            f'<text x="{BARX+BARW+14}" y="{y}" class="m" font-size="12.5" fill="{ACID}">{pct:.0f}%</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 380" width="1200" height="380" fill="none" role="img" aria-label="github stats">
  <defs>
    <filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="12" stdDeviation="20" flood-color="#000000" flood-opacity="0.5"/></filter>
    <clipPath id="cw"><rect x="20" y="16" width="1160" height="348" rx="14"/></clipPath>
    <style>.m{{font-family:'JetBrains Mono','SF Mono',ui-monospace,'Courier New',monospace;}}</style>
  </defs>
  <rect x="20" y="16" width="1160" height="348" rx="14" fill="{PANEL}" stroke="{ACID}" stroke-opacity="0.16" filter="url(#sh)"/>
  <g clip-path="url(#cw)">
    <rect x="20" y="16" width="1160" height="40" fill="{BG}"/>
    <circle cx="50" cy="36" r="6.5" fill="#ff5f57"/><circle cx="72" cy="36" r="6.5" fill="#febc2e"/><circle cx="94" cy="36" r="6.5" fill="{ACID}"><animate attributeName="opacity" values="0.5;1;0.5" dur="2.6s" repeatCount="indefinite"/></circle>
    <text x="600" y="41" text-anchor="middle" class="m" font-size="13" fill="{DIM}">sahil@dev: ~/insights</text>
    <text x="1156" y="41" text-anchor="end" class="m" font-size="12" fill="{FAINT}">gh</text>
    <line x1="20" y1="56" x2="1180" y2="56" stroke="#ffffff" stroke-opacity="0.06"/>

    <text x="48" y="92" class="m" font-size="14"><tspan fill="{ACID}">❯</tspan><tspan fill="#d6dcc8"> gh</tspan><tspan fill="#a8d962"> stats</tspan><tspan fill="{BLUE}"> --user {USER}</tspan></text>

    <text x="48" y="124" class="m" font-size="11" letter-spacing="2" fill="{FAINT}">OVERVIEW</text>
    {''.join(rows)}

    <text x="600" y="124" class="m" font-size="11" letter-spacing="2" fill="{FAINT}">TOP LANGUAGES</text>
    {''.join(bars)}

    <text x="48" y="346" class="m" font-size="12.5"><tspan fill="{ACID}">✓</tspan><tspan fill="{DIM}"> synced {synced} · live snapshot</tspan></text>
  </g>
</svg>
'''
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"wrote {OUT}: repos={user['public_repos']} stars={stars} forks={forks} langs={top}")


if __name__ == "__main__":
    main()
