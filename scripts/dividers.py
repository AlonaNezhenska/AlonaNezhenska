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
# the middle cat just stays sitting in the middle, blinking now and then
sit_t = len(cat.frames_of("sit")) / cat.meta["anims"]["sit"]["fps"]
T = svg("cat-sit.svg", [("sit", sit_t)], [(0, CX, 1), (sit_t, CX, 1)], label="pixel cat sitting")

# the ending scene from the portfolio: walk in, lie down, sleep (zzz)... a mouse tiptoes past,
# the cat opens one eye, the mouse freezes, the eye closes, the mouse bolts
ld = len(cat.frames_of("lie_down")) / cat.meta["anims"]["lie_down"]["fps"]
S0 = walk_in + sd + 1.2 + ld                      # moment the cat is asleep
TIP, FRZ, RUN, AFTER = 2.8, 1.3, .9, 4.5
w0 = S0 + 1.2                                     # mouse starts tiptoeing
parts = [("walk", walk_in), ("sit_down", None), ("sit", 1.2), ("lie_down", None),
         ("sleep", w0 + TIP - S0), ("wink", FRZ), ("sleep", RUN + .2 + AFTER)]
ev = cat.timeline(parts)
Ttot = round(ev[-1][2] + ev[-1][3], 3)
cat_g, css = cat.instance("c", ev, Ttot, scale=S)
kf = "".join(f"{t/Ttot*100:.2f}%{{transform:translate({x:.1f}px,0);opacity:{o}}}"
             for t, x, o in [(0, W + 10, 0), (.3, W - 20, 1), (walk_in, CX, 1), (Ttot - .5, CX, 1), (Ttot, CX, 0)])
css += f".c-m{{animation:m {Ttot}s linear infinite}}@keyframes m{{{kf}}}"
# mouse
mev = cat.timeline([("mouse_tiptoe", w0 + TIP), ("mouse_freeze", FRZ), ("mouse_idle", .2), ("mouse_run", Ttot - (w0 + TIP + FRZ + .2))])
mouse_g, mcss = cat.instance("mo", mev, Ttot, scale=S)
face = CX + 7 * S                                  # left edge of the curled cat's face
mfreeze = face - 34 * S                            # mouse window x so its nose stops just short of the face
mk = [(0, -cw, 0), (w0 - .01, -cw, 0), (w0, -cw * .9, 1), (w0 + TIP, mfreeze, 1), (w0 + TIP + FRZ + .2, mfreeze, 1),
      (w0 + TIP + FRZ + .2 + RUN, W + 20, 1), (w0 + TIP + FRZ + .2 + RUN + .05, W + 20, 0), (Ttot, W + 20, 0)]
css += mcss + ".mo-m{animation:mo " + str(Ttot) + "s linear infinite}@keyframes mo{" + "".join(
    f"{t/Ttot*100:.2f}%{{transform:translate({x:.1f}px,0);opacity:{o}}}" for t, x, o in mk) + "}"
# zzz: only while really asleep (not during the wink)
zx, zy = CX + cw * .3, G - chh * .55
zs = "".join(f'<text class="z z{i}" x="{zx+i*9:.0f}" y="{zy-i*4:.0f}" font-family="Consolas,Menlo,monospace" font-weight="700" '
             f'font-size="{13+i*3}" fill="{c}">z</text>' for i, c in enumerate(["#3fd8ff", "#a98bff", "#ff4fa3"]))
s0p, wkp = S0 / Ttot * 100, (w0 + TIP) / Ttot * 100
css += "".join(f".z{i}{{opacity:0;animation:z{i} {Ttot}s infinite}}@keyframes z{i}{{0%,{s0p+i*3:.1f}%{{opacity:0;transform:none}}"
               f"{s0p+i*3+2:.1f}%{{opacity:1}}{min(wkp-1, s0p+i*3+12):.1f}%{{opacity:0;transform:translate(18px,-28px)}}100%{{opacity:0}}}}" for i in range(3))
body = (f'<rect x="0" y="{G:.1f}" width="{W}" height="2" rx="1" fill="url(#ln)" opacity=".8"/>'
        f'<g filter="url(#gl)">{cat_g}</g>{mouse_g}{zs}')
out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
       f'aria-label="pixel cat falls asleep; a mouse sneaks past and the cat opens one eye">'
       f'<defs>{cat.defs()}{LINE}</defs><style>{css}@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}</style>{body}</svg>')
open(os.path.join(OUT, "cat-sleep.svg"), "w", encoding="utf-8").write(out)
print("ok", {n: os.path.getsize(os.path.join(OUT, n)) // 1024 for n in ("cat-walk.svg", "cat-sit.svg", "cat-sleep.svg")})
