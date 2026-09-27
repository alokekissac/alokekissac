"""Build a 'Top languages' card from this account's public, non-fork repos (GitHub API)."""
import json, os, sys, urllib.request

USER = os.environ.get("GH_USER", "alokekissac")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
SKIP = {"Jupyter Notebook"}          # notebook outputs inflate byte counts
COLORS = {"Python": "#3572A5", "Java": "#b07219", "JavaScript": "#f1e05a", "HTML": "#e34c26",
          "CSS": "#663399", "TypeScript": "#3178c6", "Shell": "#89e051", "Kotlin": "#A97BFF"}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
totals = {}
for repo in repos:
    if repo["fork"] or repo["name"].lower() == USER.lower():
        continue
    for lang, n in get(repo["languages_url"]).items():
        if lang not in SKIP:
            totals[lang] = totals.get(lang, 0) + n
top = sorted(totals.items(), key=lambda kv: -kv[1])[:6]
total = sum(n for _, n in top) or 1

W, H = 480, 70 + 34 * ((len(top) + 1) // 2) + 20
bar, x = "", 25
for lang, n in top:
    w = 430 * n / total
    bar += f'<rect x="{x:.1f}" y="62" width="{max(w - 2, 1):.1f}" height="10" fill="{COLORS.get(lang, "#8b949e")}"/>'
    x += w
items = ""
for i, (lang, n) in enumerate(top):
    cx, cy = 25 + (i % 2) * 220, 104 + (i // 2) * 34
    items += (f'<circle cx="{cx + 6}" cy="{cy - 5}" r="6" fill="{COLORS.get(lang, "#8b949e")}"/>'
              f'<text x="{cx + 20}" y="{cy}" class="t">{lang} <tspan class="p">{100 * n / total:.1f}%</tspan></text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>.h{{font:700 18px 'Segoe UI',Ubuntu,Arial,sans-serif;fill:#00ff9d}}.t{{font:600 14px 'Segoe UI',Ubuntu,Arial,sans-serif;fill:#cbd5e1}}.p{{fill:#64748b}}</style>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="#040711"/>
<text x="25" y="40" class="h">Top Languages</text>
<clipPath id="c"><rect x="25" y="62" width="430" height="10" rx="5"/></clipPath><g clip-path="url(#c)">{bar}</g>
{items}
</svg>'''
os.makedirs("dist", exist_ok=True)
open("dist/top-langs.svg", "w").write(svg)
print(top)
