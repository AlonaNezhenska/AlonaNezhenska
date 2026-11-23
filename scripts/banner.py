"""Builds the animated profile banner: ALONA flies together in the site colours,
the pixel cat walks along the top and hops into the O, which glows.
usage: python -I banner.py <Archivo.ttf> <out.svg>"""
import sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

font_path, out = sys.argv[1], sys.argv[2]
f = instancer.instantiateVariableFont(TTFont(font_path), {"wght": 900, "wdth": 112})
gs, cmap, upem = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm

W, H = 1200, 340
SIZE = 190                       # px per em
s = SIZE / upem
BASE = 222                       # baseline y
TRACK = 0.03 * SIZE
COLS = ["#b6ff3b", "#ff4fa3", "#3fd8ff", "#a98bff", "#ffb03a"]
word = "ALONA"

glyphs = [gs[cmap[ord(ch)]] for ch in word]
total = sum(g.width * s for g in glyphs) + TRACK * (len(word) - 1)
x = (W - total) / 2
letters = []
for i, (ch, g) in enumerate(zip(word, glyphs)):
    sp = SVGPathPen(gs)
    g.draw(TransformPen(sp, (s, 0, 0, -s, x, BASE)))
    bp = BoundsPen(gs)
    g.draw(TransformPen(bp, (s, 0, 0, -s, x, BASE)))
    letters.append(dict(ch=ch, d=sp.getCommands(), b=bp.bounds, col=COLS[i]))
    x += g.width * s + TRACK

# scattered start positions (dx, dy, rotation) — like the site intro
SCAT = [(-260, -120, -28), (-90, 150, 22), (40, -170, 14), (150, 140, -24), (300, -90, 30)]

O = letters[2]["b"]
ocx, ocy = (O[0] + O[2]) / 2, (O[1] + O[3]) / 2
otw = O[2] - O[0]
top = min(l["b"][1] for l in letters)

# ---- pixel cat (same art as the site), faces left ----
CAT = """.....................aa.....
....a........a......abca....
...ada......ada....abca.....
..adda.....adda....abca.....
.addda....adddda...abca.....
.addddaaaacdddda....abca....
.addacbbbbcdadda....abca....
.adabbbbbbbbaada.....abca...
.adbbbbbbbbbbdda......abca..
.abbbcbbbbcbbbdda.....abca..
.abefgbbbbefgbbdaaaaaacbca..
aabhfgbfbbhfgbaaacccccbbca..
.abbgbfcfbbgbbbbdbbbbbbca...
aabbbbbbbbbbbbaaabbbbbbca...
..abbbbbbbbbbicbbbbbbbbca...
...adijjjiiiicbbbbbbbbbca...
....abeckccccbbbbbbbbbbca...
....abbbbbbbbbbbbbbbbbbca...
....adbbbbbbbbbbbcbbbbbbca..
.....addbbbbbbbbbdcbbbbbca..
.....adddbbbbbbcdddcccbbbca.
....adddaabbbbcaddddaacbbba.
....adda..abbbcaddda..acbba.
.....aa..abbbcaddda..accba..""".split("\n")
PAL = {'a': '#171717', 'b': '#3b3b3b', 'c': '#2c2c2c', 'd': '#212121', 'e': '#ddf9a6', 'f': '#000',
       'g': '#b0f22c', 'h': '#cbf676', 'i': '#4fa94c', 'j': '#6fff6a', 'k': '#c8f174'}
P = 3.4                                  # px per cat pixel
cw, ch_ = len(CAT[0]) * P, len(CAT) * P
rects = []
for y, row in enumerate(CAT):
    xx = 0
    while xx < len(row):
        c = row[xx]
        if c == '.':
            xx += 1
            continue
        run = 1
        while xx + run < len(row) and row[xx + run] == c:
            run += 1
        rects.append(f'<rect x="{xx*P:.1f}" y="{y*P:.1f}" width="{run*P+.3:.1f}" height="{P+.3:.1f}" fill="{PAL[c]}"/>')
        xx += run
cat = "".join(rects)

T = 11  # seconds per loop
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catsprite import CatSprite
cs = CatSprite()
SC = 3
cw, ch_ = cs.size(SC)
G = cs.ground_offset(SC)
start_x = letters[-1]["b"][2] + 30        # right of the last A
stop_x = ocx                              # above the O
paw_y = top + 2                           # paws on top of the letters
# animation: hidden while letters fly in, walk along the tops, crouch, wiggle, pounce into the O
t_walk0, t_walk1 = .19 * T, .44 * T
d_cr = len(cs.frames_of("crouch")) / cs.meta["anims"]["crouch"]["fps"]
d_wg = len(cs.frames_of("wiggle")) / cs.meta["anims"]["wiggle"]["fps"]
d_lp = len(cs.frames_of("leap")) / cs.meta["anims"]["leap"]["fps"]
t_leap = t_walk1 + d_cr + d_wg
t_end = t_leap + d_lp
ev = cs.timeline([("walk", t_walk1), ("crouch", None), ("wiggle", None), ("leap", None), ("leap", T - t_end)])
cat_svg, cat_css = cs.instance("cat", ev, T, scale=SC)
def at(t, x, py, o=1, rot=0, sc=1):
    tr = f"translate({x-cw/2:.1f}px,{py-G:.1f}px) translate({cw/2:.1f}px,{G:.1f}px) rotate({rot}deg) scale({sc}) translate({-cw/2:.1f}px,{-G:.1f}px)"
    return f"{t/T*100:.2f}%{{transform:{tr};opacity:{o}}}"
land_y = ocy + ch_ * .25
mv = [at(0, start_x, paw_y, 0), at(t_walk0 - .01, start_x, paw_y, 0), at(t_walk0, start_x, paw_y),
      at(t_walk1, stop_x, paw_y), at(t_leap, stop_x, paw_y),
      at(t_leap + d_lp * .45, stop_x, paw_y - 40, 1, -12, .85),
      at(t_end, stop_x, land_y, .9, -38, .45), at(t_end + .25, stop_x, land_y, 0, -40, .3), at(T, stop_x, land_y, 0, -40, .3)]
glow_on = t_end / T * 100
css = f"""
.l{{transform-box:fill-box;transform-origin:center;animation:fly {T}s cubic-bezier(.2,.8,.2,1) infinite}}
.l path{{animation:paint {T}s linear infinite}}
{''.join(f'.l{i}{{--dx:{dx}px;--dy:{dy}px;--r:{r}deg;animation-delay:{0}s}} .l{i} path{{--c:{letters[i]["col"]}}}' for i,(dx,dy,r) in enumerate(SCAT))}
@keyframes fly{{0%{{transform:translate(var(--dx),var(--dy)) rotate(var(--r));opacity:0}}3%{{opacity:1}}
 15%,90%{{transform:none;opacity:1}}97%,100%{{transform:none;opacity:0}}}}
@keyframes paint{{0%,15%{{fill:#f4f1ea}}19%,100%{{fill:var(--c)}}}}
.cat-m{{animation:catm {T}s linear infinite}}@keyframes catm{{{''.join(mv)}}}
{cat_css}
.glow{{transform-box:fill-box;transform-origin:center;animation:glow {T}s ease-in-out infinite}}
@keyframes glow{{0%,{glow_on-1:.1f}%{{opacity:0;transform:scale(.4)}}{glow_on+5:.1f}%{{opacity:1;transform:scale(1.05)}}
 60%{{transform:scale(.92)}}67%{{transform:scale(1.04)}}74%{{transform:scale(.95)}}88%{{opacity:1;transform:scale(1)}}96%,100%{{opacity:0}}}}
.tag{{animation:tag {T}s ease infinite}}
@keyframes tag{{0%,20%{{opacity:0;transform:translateY(8px)}}28%,90%{{opacity:1;transform:none}}97%,100%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.l,.l path,.cat-m,.cat-f,.glow,.tag{{animation:none}}.l path{{fill:var(--c)}}.cat-m{{opacity:0}}}}
"""

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="ALONA: Alona Nezhenska, software engineer">
<title>Alona Nezhenska</title>
<defs>
 <radialGradient id="bg" cx="50%" cy="40%" r="70%"><stop offset="0" stop-color="#17141f"/><stop offset="1" stop-color="#0b0a10"/></radialGradient>
 <radialGradient id="o" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#b6ff3b" stop-opacity=".95"/><stop offset=".45" stop-color="#3fd8ff" stop-opacity=".55"/><stop offset=".75" stop-color="#a98bff" stop-opacity=".2"/><stop offset="1" stop-color="#a98bff" stop-opacity="0"/></radialGradient>
 <radialGradient id="b1"><stop offset="0" stop-color="#ff4fa3" stop-opacity=".16"/><stop offset="1" stop-color="#ff4fa3" stop-opacity="0"/></radialGradient>
 <filter id="cg" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="0" stdDeviation="3" flood-color="#b6ff3b" flood-opacity=".45"/></filter>
 {cs.defs()}
 <radialGradient id="b2"><stop offset="0" stop-color="#3fd8ff" stop-opacity=".14"/><stop offset="1" stop-color="#3fd8ff" stop-opacity="0"/></radialGradient>
</defs>
<style>{css}</style>
<rect width="{W}" height="{H}" rx="22" fill="url(#bg)"/>
<circle cx="170" cy="60" r="260" fill="url(#b1)"/><circle cx="1060" cy="300" r="300" fill="url(#b2)"/>
<circle class="glow" cx="{ocx:.1f}" cy="{ocy:.1f}" r="{otw*.42:.1f}" fill="url(#o)"/>
{''.join(f'<g class="l l{i}"><path d="{l["d"]}"/></g>' for i,l in enumerate(letters))}
<g filter="url(#cg)">{cat_svg}</g>
<g class="tag" font-family="'Segoe UI',-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif" text-anchor="middle">
 <text x="{W/2}" y="{BASE+52}" font-size="21" font-weight="600" fill="#f4f1ea">Software engineer who builds things with data &amp; AI</text>
 <text x="{W/2}" y="{BASE+84}" font-size="15" fill="#8a8597" letter-spacing="2">HERIOT-WATT · EDINBURGH · ALONANEZHENSKA.CO.UK</text>
</g>
</svg>'''
open(out, "w", encoding="utf-8").write(svg)
print("wrote", out, len(svg) // 1024, "KB; O centre", round(ocx), round(ocy), "cat", round(cw), "x", round(ch_))
