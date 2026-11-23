"""Cat dividers for the profile README, using the animated sprite (scripts/catsprite.py).
cat-walk.svg   the cat trots across the line
cat-sit.svg    walks in, sits down, blinks, gets up and walks off
cat-sleep.svg  walks in, sits, lies down, curls up and sleeps (zzz)
usage: python scripts/dividers.py
"""
import os
from catsprite import CatSprite

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
cat = CatSprite()
W, S = 900, 2
cw, chh = cat.size(S)
G = cat.ground_offset(S)
H = int(chh + 6)
CX = W / 2 - cw / 2           # x that puts the cat in the middle

LINE = ('<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="#b6ff3b" stop-opacity="0"/>'
        '<stop offset=".2" stop-color="#b6ff3b"/><stop offset=".4" stop-color="#ff4fa3"/><stop offset=".6" stop-color="#3fd8ff"/>'
        '<stop offset=".8" stop-color="#a98bff"/><stop offset="1" stop-color="#ffb03a" stop-opacity="0"/></linearGradient>'
        '<filter id="gl" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#b6ff3b" flood-opacity=".35"/></filter>')


def svg(name, parts, moves, extra="", extra_css="", label=""):
    """parts: animation timeline; moves: [(time_s, x, opacity)] for the cat's position."""
    ev = cat.timeline(parts)
    T = round(ev[-1][2] + ev[-1][3], 3)
    g, css = cat.instance("c", ev, T, scale=S)
    kf = "".join(f"{t/T*100:.2f}%{{transform:translate({x:.1f}px,0);opacity:{o}}}" for t, x, o in moves)
    css += f".c-m{{animation:m {T}s linear infinite}}@keyframes m{{{kf}}}{extra_css}"
    body = (f'<rect x="0" y="{G:.1f}" width="{W}" height="2" rx="1" fill="url(#ln)" opacity=".8"/>'
            f'<g filter="url(#gl)">{g}</g>{extra}')
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">'
           f'<defs>{cat.defs()}{LINE}</defs><style>{css}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>{body}</svg>')
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(out)
    return T


# walking across, right to left (the cat faces left)
T = svg("cat-walk.svg", [("walk", 9)], [(0, W + 10, 1), (9, -cw - 10, 1)], label="pixel cat trotting across")

# walk in, sit down, blink, stand up, walk off
walk_in, sd = 3.2, len(cat.frames_of("sit_down")) / cat.meta["anims"]["sit_down"]["fps"]
parts = [("walk", walk_in), ("sit_down", None), ("sit", 4.5), ("sit_down", None, True), ("walk", 3.2)]
t1 = walk_in + sd + 4.5 + sd
T = svg("cat-sit.svg", parts,
        [(0, W + 10, 1), (walk_in, CX, 1), (t1, CX, 1), (t1 + 3.2, -cw - 10, 1)], label="pixel cat sitting down")

# walk in, sit, lie down, curl up, sleep with zzz
ld = len(cat.frames_of("lie_down")) / cat.meta["anims"]["lie_down"]["fps"]
sleep = 9
parts = [("walk", walk_in), ("sit_down", None), ("sit", 1.2), ("lie_down", None), ("sleep", sleep)]
Ttot = walk_in + sd + 1.2 + ld + sleep
z0 = (walk_in + sd + 1.2 + ld) / Ttot * 100
zx, zy = CX + cw * .3, G - chh * .55
zs = "".join(f'<text class="z z{i}" x="{zx+i*9:.0f}" y="{zy-i*4:.0f}" font-family="Consolas,Menlo,monospace" font-weight="700" '
             f'font-size="{13+i*3}" fill="{c}">z</text>' for i, c in enumerate(["#3fd8ff", "#a98bff", "#ff4fa3"]))
zcss = "".join(f".z{i}{{opacity:0;animation:z{i} {Ttot:.3f}s infinite}}@keyframes z{i}{{0%,{z0+i*4:.1f}%{{opacity:0;transform:none}}"
               f"{z0+i*4+3:.1f}%{{opacity:1}}{min(99,z0+i*4+14):.1f}%{{opacity:0;transform:translate(18px,-28px)}}100%{{opacity:0}}}}" for i in range(3))
T = svg("cat-sleep.svg", parts,
        [(0, W + 10, 0), (.3, W - 20, 1), (walk_in, CX, 1), (Ttot - .5, CX, 1), (Ttot, CX, 0)],
        extra=zs, extra_css=zcss, label="pixel cat falling asleep")
print("ok", {n: os.path.getsize(os.path.join(OUT, n)) // 1024 for n in ("cat-walk.svg", "cat-sit.svg", "cat-sleep.svg")})
