"""Night city from my GitHub contributions.

Every week of the last year is a building (taller = more contributions that week), each lit
window is a day I contributed (colour = how busy that day was), and my pixel cat runs across
the rooftops. Reads the public contributions calendar, so it needs no token.

usage: python scripts/city.py [user] [out.svg]
"""
import datetime as dt
import math
import random
import re
import sys
import urllib.request

USER = sys.argv[1] if len(sys.argv) > 1 else "AlonaNezhenska"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/city.svg"

# ---------- data ----------
req = urllib.request.Request(f"https://github.com/users/{USER}/contributions",
                             headers={"User-Agent": "Mozilla/5.0 (profile-city)"})
page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
cells = {m.group(2): (m.group(1), int(m.group(3)))
         for m in re.finditer(r'<td[^>]*data-date="([\d-]+)"[^>]*id="(contribution-day-component-[\d-]+)"[^>]*data-level="(\d)"', page)}
counts = {}
for m in re.finditer(r'<tool-tip[^>]*for="(contribution-day-component-[\d-]+)"[^>]*>([^<]*)</tool-tip>', page):
    t = m.group(2)
    n = 0 if t.startswith("No contributions") else int(re.match(r"([\d,]+)", t).group(1).replace(",", ""))
    counts[m.group(1)] = n
days = sorted((date, lvl, counts.get(cid, 0)) for cid, (date, lvl) in cells.items())
if len(days) < 300:
    sys.exit(f"only found {len(days)} days, not overwriting {OUT}")

# group into Sunday-starting weeks (the same columns as GitHub's graph)
weeks = []
for date, lvl, n in days:
    d = dt.date.fromisoformat(date)
    if not weeks or d.weekday() == 6:
        weeks.append([])
    weeks[-1].append((d, lvl, n))
total = sum(n for _, _, n in days)
streak = best_streak = 0
for _, _, n in days:
    streak = streak + 1 if n else 0
    best_streak = max(best_streak, streak)
wk_tot = [sum(n for _, _, n in w) for w in weeks]
peak = max(wk_tot) or 1
best_i = wk_tot.index(peak)

# ---------- layout ----------
W, H, GROUND, PAD = 900, 300, 268, 18
N = len(weeks)
step = (W - 2 * PAD) / N
bw = step - 2
HMIN, HMAX = 66, 172
rnd0 = random.Random(3)
# busy weeks: taller with more contributions. quiet weeks: short dark buildings (always shorter than any busy one)
heights = [HMIN + (HMAX - HMIN) * math.sqrt(t / peak) if t else rnd0.uniform(22, 58) for t in wk_tot]
tops = [GROUND - h for h in heights]
LIT = {1: "#a98bff", 2: "#3fd8ff", 3: "#ff4fa3", 4: "#b6ff3b"}
rnd = random.Random(7)

out = []
# stars and moon
for _ in range(70):
    x, y, r = rnd.uniform(0, W), rnd.uniform(8, GROUND - HMAX - 6), rnd.choice([.6, .8, 1, 1.3])
    out.append(f'<circle class="st" style="animation-delay:{rnd.uniform(0,4):.2f}s" cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#f4f1ea"/>')
out.append('<circle cx="826" cy="54" r="22" fill="#f4f1ea" opacity=".92"/><circle cx="836" cy="47" r="20" fill="url(#sky)"/>')

# faint skyline far behind, for depth
bx0 = 0
while bx0 < W:
    bw2, bh2 = rnd.uniform(14, 34), rnd.uniform(40, 120)
    out.append(f'<rect x="{bx0:.0f}" y="{GROUND-bh2:.0f}" width="{bw2:.0f}" height="{bh2:.0f}" fill="#1b1729" opacity=".8"/>')
    bx0 += bw2 + rnd.uniform(0, 6)

# buildings
for i, w in enumerate(weeks):
    x, top, h = PAD + i * step, tops[i], heights[i]
    out.append(f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="#15131d"/>'
               f'<rect x="{x:.1f}" y="{top:.1f}" width="{bw:.1f}" height="1.6" fill="#2c2838"/>')
    # one window per day, top to bottom
    ww, wh = max(3, bw * .5), 4.2
    wx = x + (bw - ww) / 2
    for d_i, (d, lvl, n) in enumerate(w):
        wy = top + 5 + d_i * 7
        if wy + wh > GROUND - 3:
            break
        if lvl:
            cls = ' class="fl"' if rnd.random() < .15 else ""
            out.append(f'<rect{cls} x="{wx:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{wh}" fill="{LIT[lvl]}"/>')
        else:
            out.append(f'<rect x="{wx:.1f}" y="{wy:.1f}" width="{ww:.1f}" height="{wh}" fill="#1f1c2a"/>')
    # extra dim windows lower down on tall buildings, for a city feel
    y = top + 5 + 7 * 7
    while y + wh < GROUND - 4:
        if rnd.random() < .22:
            out.append(f'<rect x="{wx:.1f}" y="{y:.1f}" width="{ww:.1f}" height="{wh}" fill="#ffb03a" opacity=".22"/>')
        y += 7

# antenna + sign on the busiest week
bx = PAD + best_i * step + bw / 2
out.append(f'<rect x="{bx-.6:.1f}" y="{tops[best_i]-16:.1f}" width="1.2" height="16" fill="#3a3646"/>'
           f'<circle class="bl" cx="{bx:.1f}" cy="{tops[best_i]-17:.1f}" r="2.2" fill="#ff4fa3"/>')
label = f"best week · {peak}"
lx = min(max(bx, 70), W - 70)
out.append(f'<g font-family="Consolas,Menlo,monospace" font-size="11" text-anchor="middle">'
           f'<rect x="{lx-52:.0f}" y="{tops[best_i]-42:.0f}" width="104" height="17" rx="4" fill="#0b0a10" stroke="#ff4fa3" stroke-opacity=".7"/>'
           f'<text x="{lx:.0f}" y="{tops[best_i]-30:.0f}" fill="#ff4fa3">{label}</text></g>')

# ground line
out.append(f'<rect x="0" y="{GROUND}" width="{W}" height="2" fill="url(#ln)"/>'
           f'<rect x="0" y="{GROUND+2}" width="{W}" height="{H-GROUND-2}" fill="#0b0a10"/>')

# ---------- the cat: walks along level roofs, leaps between different heights (faces right) ----------
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catsprite import CatSprite
cs = CatSprite()
SC = 1.15
cw, ch = cs.size(SC)
G = cs.ground_offset(SC)
T = round(max(20, N * .45), 1)
last = len(tops) - 1
seg = T * .9 / last                       # seconds per building
t0 = T * .02
cx = lambda i: PAD + i * step + bw / 2
WALK, LEAP = cs.meta["anims"]["walk"], cs.meta["anims"]["leap"]
mv, ev = [], []                            # movement keyframes, sprite frame events (anim, frame, start, dur)
ev.append(("walk", 0, 0, t0))
wf = 0
for i in range(last + 1):
    t = t0 + i * seg
    mv.append((t, cx(i), tops[i]))
    if i == last:
        break
    dh = tops[i + 1] - tops[i]
    if abs(dh) < 5:                        # level enough: trot along
        n = max(1, round(seg * WALK["fps"]))
        for k in range(n):
            ev.append(("walk", wf % WALK["frames"], t + k * seg / n, seg / n)); wf += 1
    else:                                  # leap: arc up over the gap, legs stretched
        mid = min(tops[i], tops[i + 1]) - 10 - abs(dh) * .2
        mv.append((t + seg * .5, (cx(i) + cx(i + 1)) / 2, mid))
        for k in range(LEAP["frames"]):
            ev.append(("leap", k, t + k * seg / LEAP["frames"], seg / LEAP["frames"]))
ev.append(("walk", 0, t0 + last * seg, T - (t0 + last * seg)))
cat_svg, cat_css = cs.instance("cat", ev, T, scale=SC, flip=True)
kf = "".join(f"{tt/T*100:.3f}%{{transform:translate({x-cw/2:.1f}px,{y-G:.1f}px)}}" for tt, x, y in mv)
kf += f"100%{{transform:translate({cx(last)-cw/2:.1f}px,{tops[-1]-G:.1f}px)}}"
css = (f".cat-m{{animation:run {T}s linear infinite}}@keyframes run{{{kf}}}{cat_css}"
       f".fade{{animation:fade {T}s linear infinite}}@keyframes fade{{0%{{opacity:0}}2%,92%{{opacity:1}}96%,100%{{opacity:0}}}}"
       ".st{animation:tw 4s ease-in-out infinite}@keyframes tw{50%{opacity:.25}}"
       ".fl{animation:fl 3s steps(1) infinite}@keyframes fl{0%,85%{opacity:1}86%,92%{opacity:.25}93%{opacity:1}}"
       ".bl{animation:bl 1.6s steps(1) infinite}@keyframes bl{50%{opacity:.2}}"
       f"@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.cat-m{{transform:translate({bx-cw/2:.1f}px,{tops[best_i]-G:.1f}px)}}}}")
cat = f'<g class="fade" filter="url(#gl)">{cat_svg}</g>'

first, lastday = days[0][0], days[-1][0]
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Night city made from {USER}'s GitHub contributions: {total} in the last year, best week {peak}, longest streak {best_streak} days">
<title>{total} contributions in the last year</title>
<defs>
 <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0a10"/><stop offset="1" stop-color="#1a1530"/></linearGradient>
 <linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="#b6ff3b" stop-opacity="0"/><stop offset=".2" stop-color="#b6ff3b"/><stop offset=".4" stop-color="#ff4fa3"/><stop offset=".6" stop-color="#3fd8ff"/><stop offset=".8" stop-color="#a98bff"/><stop offset="1" stop-color="#ffb03a" stop-opacity="0"/></linearGradient>
 <filter id="gl" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="0" stdDeviation="2" flood-color="#b6ff3b" flood-opacity=".4"/></filter>
 {cs.defs()}
</defs>
<style>{css}</style>
<rect width="{W}" height="{H}" rx="16" fill="url(#sky)"/>
<g font-family="'Segoe UI',-apple-system,Helvetica,Arial,sans-serif">
 <text x="22" y="34" font-size="17" font-weight="700" fill="#b6ff3b">My year in code</text>
 <text x="22" y="54" font-size="12" fill="#8a8597">{total} contributions · longest streak {best_streak} days · each building is a week, each lit window a day</text>
</g>
{"".join(out)}
{cat}
<text x="{W-18}" y="{H-12}" font-family="Consolas,Menlo,monospace" font-size="10" fill="#4d4958" text-anchor="end">{first} → {lastday} · redrawn daily</text>
</svg>'''
open(OUT, "w", encoding="utf-8").write(svg)
print(f"wrote {OUT}: {len(svg)//1024} KB, {len(days)} days, {N} weeks, {total} contributions, best week {peak}, streak {best_streak}")
