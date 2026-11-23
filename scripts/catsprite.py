"""Animated pixel cat for SVGs shown on GitHub.

Embeds assets/cat-sheet.png (drawn by the portfolio's tools/cat-studio) once per SVG and shows one
frame at a time through a clipped window. Frames and movement are plain CSS keyframes, which GitHub
plays inside <img>-embedded SVGs.

    cat = CatSprite()
    defs = cat.defs()                                   # put inside <defs>
    events = cat.timeline([("walk", 2.5), ("sit_down", None), ("sit", 3)])   # (anim, seconds or None = once)
    svg_group, css = cat.instance("c1", events, total=T, scale=3, motion=[...], flip=False)
"""
import base64, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")


class CatSprite:
    def __init__(self, sheet=os.path.join(ASSETS, "cat-sheet.png"), meta=os.path.join(ASSETS, "cat-sheet.json")):
        self.png = base64.b64encode(open(sheet, "rb").read()).decode()
        self.meta = json.load(open(meta))
        self.FW, self.FH = self.meta["frame"]
        self.ground = self.meta["ground"]
        self.cols = max(a["frames"] for a in self.meta["anims"].values())
        self.rows = len(self.meta["anims"])

    def defs(self):
        return (f'<image id="catsheet" width="{self.cols*self.FW}" height="{self.rows*self.FH}" '
                f'image-rendering="pixelated" style="image-rendering:pixelated;image-rendering:crisp-edges" '
                f'href="data:image/png;base64,{self.png}"/>')

    def frames_of(self, anim, seconds=None, reverse=False):
        """List of (frame_index, duration) for one animation. seconds=None plays it once."""
        a = self.meta["anims"][anim]
        n, d = a["frames"], 1 / a["fps"]
        seq = list(range(n))[::-1] if reverse else list(range(n))
        if seconds is None:
            return [(anim, f, d) for f in seq]
        out, t, i = [], 0.0, 0
        while t < seconds - 1e-6:
            out.append((anim, seq[i % n], min(d, seconds - t)))
            t += d; i += 1
        return out

    def timeline(self, parts):
        """parts: (anim, seconds|None[, reverse]) → [(anim, frame, start, dur)]"""
        ev, t = [], 0.0
        for p in parts:
            anim, secs = p[0], p[1]
            rev = len(p) > 2 and p[2]
            for (a, f, d) in self.frames_of(anim, secs, rev):
                ev.append((a, f, t, d)); t += d
        return ev

    def frame_xy(self, anim, f):
        return f * self.FW, self.meta["anims"][anim]["row"] * self.FH

    def instance(self, name, events, total, scale=3, flip=False):
        """Returns (svg, css). The cat's frame window is FW×FH art pixels, scaled; its paws touch
        y = ground_offset(scale) inside the group, horizontally centred at width/2. Move it by
        animating the outer group with class `{name}-m` (you write that keyframe yourself)."""
        W, H = self.FW * scale, self.FH * scale
        kf = []
        for (a, f, t, d) in events:
            x, y = self.frame_xy(a, f)
            kf.append(f"{t/total*100:.3f}%{{transform:translate({-x}px,{-y}px)}}")
        a, f, t, d = events[-1]
        x, y = self.frame_xy(a, f)
        kf.append(f"100%{{transform:translate({-x}px,{-y}px)}}")
        css = (f".{name}-f{{animation:{name}-f {total}s infinite;animation-timing-function:steps(1,end)}}"
               f"@keyframes {name}-f{{{''.join(kf)}}}")
        inner = f'<g class="{name}-f"><use href="#catsheet"/></g>'
        if flip:
            inner = f'<g transform="translate({self.FW},0) scale(-1,1)">{inner}</g>'
        svg = (f'<g class="{name}-m"><svg width="{W}" height="{H}" viewBox="0 0 {self.FW} {self.FH}" overflow="hidden" '
               f'shape-rendering="crispEdges">{inner}</svg></g>')
        return svg, css

    def size(self, scale):
        return self.FW * scale, self.FH * scale

    def ground_offset(self, scale):
        """distance from the top of the cat's window to its paws"""
        return (self.ground - .5) * scale
