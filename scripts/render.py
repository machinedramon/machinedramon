#!/usr/bin/env python3
"""Render the animated terminal SVGs for the profile README.

Writes assets/terminal.svg (desktop) and assets/terminal-mobile.svg (phones).
Animations are plain CSS keyframes with per-element delays, the same technique
github-readme-stats relies on, so they run inside GitHub's <img> rendering.
"""

from pathlib import Path
from xml.sax.saxutils import escape

USER = "machinedramon"
FULL_NAME = "Diego Augusto Santos Ferreira"
AREAS = "systems · gamedev · web3"
STACK = ["rust", "c++", "c#", "typescript", "dart", "python", "godot", "solana"]
# Showcased repos; empty hides the `ls ~/public` block.
PUBLIC = []
PLAN = ["> contributing to rust-lang/rust"]

OUT = Path(__file__).resolve().parent.parent / "assets"

C = {
    "bg": "#0a0c0f",
    "bar": "#11141a",
    "line": "#1c2129",
    "txt": "#c9d1d9",
    "dim": "#6e7681",
    "hi": "#f0f6fc",
    "acc": "#e5484d",
    "cyan": "#3dd6d0",
}


# ---------------------------------------------------------------- helpers

def delay(t, *extra):
    return f' style="animation-delay:{", ".join(f"{x:.2f}s" for x in (t,) + extra)}"'


# ------------------------------------------------------------------- layout

class Term:
    """Builds the animated lines of the terminal body."""

    def __init__(self, x, y, lh, char_t=0.045):
        self.x, self.y, self.lh = x, y, lh
        self.t = 0.5
        self.char_t = char_t
        self.out = []

    def gap(self, n=0.5):
        self.y += self.lh * n

    def cmd(self, text):
        parts = [f'<tspan class="k" fill="{C["acc"]}"{delay(self.t)}>$ </tspan>']
        t = self.t + 0.25
        for ch in text:
            parts.append(f'<tspan class="k"{delay(t)}>{escape(ch)}</tspan>')
            t += self.char_t
        self.out.append(
            f'<text x="{self.x}" y="{self.y}" xml:space="preserve" fill="{C["txt"]}">{"".join(parts)}</text>'
        )
        self.t = t + 0.3
        self.y += self.lh

    def row(self, segs, extra=""):
        """segs: list of (dx, text, color)."""
        texts = "".join(
            f'<text x="{self.x + dx}" y="{self.y}" xml:space="preserve" fill="{color}">{escape(text)}</text>'
            for dx, text, color in segs
        )
        self.out.append(f'<g class="o"{delay(self.t)}>{texts}{extra}</g>')
        self.t += 0.07
        self.y += self.lh

    def glitch_row(self, dx, text):
        x, y, t = self.x + dx, self.y, self.t + 0.6
        g = "".join(
            f'<text class="fx {cls}" x="{x}" y="{y}" fill="{color}"{delay(t)}>{escape(text)}</text>'
            for color, cls in ((C["acc"], "g1"), (C["cyan"], "g2"))
        )
        self.row([(dx, text, C["hi"])], extra=g)

    def block(self):
        self.t += 0.2
        self.gap()


def render(mobile):
    W = 480 if mobile else 960
    fs = 14 if mobile else 15
    lh = 21 if mobile else 23
    cw = fs * 0.6  # approx monospace advance, only used for column offsets
    pad = 22 if mobile else 30
    bar_h = 36

    T = Term(pad, bar_h + 34, lh)

    T.cmd("whoami")
    T.row([(0, USER, C["hi"])])
    T.row([(0, f"# {FULL_NAME}", C["dim"])])
    T.block()

    T.cmd("cat /etc/motd")
    T.glitch_row(0, "hello, friend.")
    T.gap()
    T.row([(0, AREAS, C["txt"])])
    T.block()

    T.cmd("ls ~/stack")
    if mobile:
        half = (len(STACK) + 1) // 2
        T.row([(0, "  ".join(STACK[:half]), C["txt"])])
        T.row([(0, "  ".join(STACK[half:]), C["txt"])])
    else:
        T.row([(0, "  ".join(STACK), C["txt"])])
    T.block()

    if PUBLIC:
        T.cmd("ls -1 ~/public")
        name_w = max(len(n) for n, _ in PUBLIC)
        for name, desc in PUBLIC:
            if mobile:
                T.row([(0, name, C["hi"])])
                T.row([(cw * 2, desc, C["dim"])])
            else:
                T.row([(0, name, C["hi"]), (cw * (name_w + 3), desc, C["dim"])])
        T.block()

    T.cmd("cat ~/.plan")
    for line in PLAN:
        T.row([(0, line, C["txt"])])
    T.block()

    # final prompt + blinking cursor
    cur_t = T.t + 0.2
    T.out.append(
        f'<text class="k" x="{T.x}" y="{T.y}" fill="{C["acc"]}"{delay(cur_t)}>$</text>'
        f'<rect class="cur" x="{T.x + cw * 2:.1f}" y="{T.y - fs + 2}" width="{cw:.1f}" height="{fs + 2}" '
        f'fill="{C["txt"]}"{delay(cur_t)}/>'
    )
    T.y += lh

    status_h = 30
    H = int(T.y + 18 + status_h)

    # status bar (tmux style)
    sy = H - status_h
    status = (
        f'<rect x="0" y="{sy}" width="{W}" height="{status_h}" fill="{C["bar"]}"/>'
        f'<line x1="0" y1="{sy}" x2="{W}" y2="{sy}" stroke="{C["line"]}"/>'
        f'<rect x="0" y="{sy}" width="{cw * 6 + 20:.0f}" height="{status_h}" fill="{C["acc"]}"/>'
        f'<text x="10" y="{sy + 20}" fill="{C["bg"]}" font-weight="700">[0] sh</text>'
        f'<text x="{W - 12}" y="{sy + 20}" fill="{C["dim"]}" text-anchor="end">127.0.0.1</text>'
    )

    title = f"{USER}@127.0.0.1: ~" if not mobile else f"{USER}: ~"
    bar = (
        f'<rect x="0" y="0" width="{W}" height="{bar_h}" fill="{C["bar"]}"/>'
        f'<line x1="0" y1="{bar_h}" x2="{W}" y2="{bar_h}" stroke="{C["line"]}"/>'
        + "".join(f'<circle cx="{18 + i * 18}" cy="{bar_h / 2}" r="5.5" fill="#3a3f47"/>' for i in range(3))
        + f'<text x="{W / 2}" y="{bar_h / 2 + 5}" text-anchor="middle" fill="{C["dim"]}">{escape(title)}</text>'
    )

    style = f"""
text{{font-family:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,"Liberation Mono",monospace;font-size:{fs}px}}
.k{{opacity:0;animation:on .01s linear forwards}}
.o{{opacity:0;animation:rise .35s ease-out forwards}}
.cur{{opacity:0;animation:blink 1.06s steps(1) infinite}}
.fx{{opacity:0;animation:g1 5.5s steps(1) infinite}}
.g2{{animation-name:g2}}
.band{{animation:scan 7s linear infinite}}
@keyframes on{{to{{opacity:1}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:none}}}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
@keyframes scan{{from{{transform:translateY(0)}}to{{transform:translateY({H + 160}px)}}}}
@keyframes g1{{0%{{opacity:0}}86%{{opacity:.85;transform:translate(-2px,0)}}87%{{opacity:.7;transform:translate(2px,-1px)}}88%{{opacity:.85;transform:translate(-1px,1px)}}89%{{opacity:0;transform:none}}}}
@keyframes g2{{0%{{opacity:0}}86%{{opacity:.85;transform:translate(2px,0)}}87%{{opacity:.7;transform:translate(-2px,1px)}}88%{{opacity:.85;transform:translate(1px,-1px)}}89%{{opacity:0;transform:none}}}}
@media (prefers-reduced-motion:reduce){{
  .k,.o,.cur{{animation:none;opacity:1}}
  .fx,.band{{display:none}}
}}
"""

    defs = f"""
<clipPath id="win"><rect width="{W}" height="{H}" rx="10"/></clipPath>
<pattern id="lines" width="4" height="3" patternUnits="userSpaceOnUse">
  <rect width="4" height="1" fill="#000" opacity=".35"/>
</pattern>
<linearGradient id="bandg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/>
  <stop offset=".5" stop-color="#fff" stop-opacity=".035"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<radialGradient id="vig" cx=".5" cy=".45" r=".75">
  <stop offset=".6" stop-color="#000" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity=".45"/>
</radialGradient>
<filter id="glow" x="-10%" y="-10%" width="120%" height="120%">
  <feGaussianBlur stdDeviation="2.2" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
"""

    band = (
        f'<rect class="band" x="0" y="-160" width="{W}" height="160" fill="url(#bandg)"/>'
    )

    alt = f"{USER} — {AREAS} — {', '.join(STACK)}"
    newline = "\n"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(alt)}">
<title>{escape(alt)}</title>
<style>{style}</style>
<defs>{defs}</defs>
<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="{C["bg"]}"/>
{bar}
<g filter="url(#glow)">
{newline.join(T.out)}
</g>
{status}
<rect width="{W}" height="{H}" fill="url(#lines)" opacity=".5"/>
{band}
<rect width="{W}" height="{H}" fill="url(#vig)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="none" stroke="{C["line"]}"/>
</svg>
"""


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "terminal.svg").write_text(render(mobile=False), encoding="utf-8")
    (OUT / "terminal-mobile.svg").write_text(render(mobile=True), encoding="utf-8")


if __name__ == "__main__":
    main()
