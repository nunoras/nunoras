import argparse
import base64
import io
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parent.parent

WIDTH = 830
THUMB = 230
PAD = 12

BOARD = "/gh/ - github"
NAV = "[Home] [Catalog] [Bottom]"
NAME = "Nuno"
STAMP = " 11/18/26(Wed)02:14:07 No.000417 [Reply]"
FILE_NAME = "fellowstitch.png"
FILE_INFO = " (60 KB, 460x460)"
GREENTEXT = [
    ">be me",
    ">live in Sintra, Portugal",
    ">AI-native engineer",
    ">currently building FellowStitch, pic related",
    ">stack: TypeScript, Rust, Python, Postgres",
]
QUESTION = "what are you up to?"
REPLY_NAME = "Anonymous"
REPLY_NO = " No.000418"
REPLY_QUOTE = ">>000417"
REPLY_TEXT = "based (｀・ω・´)b"
TAG_LEFT = "other generators"
TAG_RIGHT = "fellowstitch.com ↗"

THEMES = {
    "dark": {
        "page": "#111111",
        "line": "#3a3a3a",
        "muted": "#888888",
        "dim": "#999999",
        "text": "#dddddd",
        "strong": "#ffffff",
        "reply": "#181818",
        "box": "#ffffff",
    },
    "light": {
        "page": "#ffffff",
        "line": "#d0d0d0",
        "muted": "#777777",
        "dim": "#666666",
        "text": "#222222",
        "strong": "#000000",
        "reply": "#f3f3f3",
        "box": "#ffffff",
    },
}


class Face:
    def __init__(self, family, font):
        self.family = family
        self.font = font
        self.cmap = font.getBestCmap()
        self.advances = font["hmtx"].metrics
        self.units = font["head"].unitsPerEm

    def width(self, text, size):
        return sum(self.advances[self.cmap[ord(ch)]][0] for ch in text) * size / self.units

    def css(self):
        buffer = io.BytesIO()
        self.font.flavor = "woff2"
        self.font.save(buffer)
        data = base64.b64encode(buffer.getvalue()).decode()
        return f"@font-face{{font-family:{self.family};src:url(data:font/woff2;base64,{data}) format('woff2')}}"


def subset_face(family, font, text):
    options = subset.Options()
    options.layout_features = []
    options.name_IDs = ["*"]
    options.hinting = False
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=text)
    subsetter.subset(font)
    return Face(family, font)


def sans_face(path, weight, family, text):
    font = instantiateVariableFont(TTFont(path), {"wght": weight})
    return subset_face(family, font, text)


def text(x, y, body, size, fill, family, weight="normal", extra=""):
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}"{extra}>{escape(body)}</text>'


def underline(x, y, width, fill):
    return f'<rect x="{x:.1f}" y="{y + 2:.1f}" width="{width:.1f}" height="1" fill="{fill}"/>'


def tag(x, y, body, mono, anchor_right=False):
    size = 9
    width = mono.width(body, size) + 10
    left = x - width if anchor_right else x
    return (
        f'<rect x="{left:.1f}" y="{y}" width="{width:.1f}" height="15" fill="#000000"/>'
        + text(left + 5, y + 11, body, size, "#ffffff", mono.family)
    )


def render(theme, sans, bold, mono, picture, style):
    c = THEMES[theme]
    out = []
    out.append(text(10, 17, BOARD, 11, c["muted"], mono.family))
    out.append(text(WIDTH - 10, 17, NAV, 11, c["muted"], mono.family, extra=' text-anchor="end"'))
    out.append(f'<rect x="1" y="24" width="{WIDTH - 2}" height="1" fill="{c["line"]}"/>')

    y = 48
    out.append(f'<rect x="{PAD}.5" y="{y - 10}.5" width="11" height="11" rx="2" fill="{c["box"]}" stroke="{c["dim"]}"/>')
    x = PAD + 16
    out.append(text(x, y, NAME, 13, c["strong"], bold.family, "bold"))
    x += bold.width(NAME, 13)
    out.append(text(x, y, STAMP, 13, c["text"], sans.family))

    y += 18
    out.append(text(PAD, y, "File: ", 11, c["dim"], sans.family))
    x = PAD + sans.width("File: ", 11)
    out.append(text(x, y, FILE_NAME, 11, c["text"], sans.family))
    out.append(underline(x, y, sans.width(FILE_NAME, 11), c["text"]))
    out.append(text(x + sans.width(FILE_NAME, 11), y, FILE_INFO, 11, c["dim"], sans.family))

    top = y + 8
    out.append(f'<rect x="{PAD - 0.5}" y="{top - 0.5}" width="{THUMB + 1}" height="{THUMB + 1}" fill="none" stroke="{c["line"]}"/>')
    out.append(f'<image x="{PAD}" y="{top}" width="{THUMB}" height="{THUMB}" style="image-rendering:pixelated" href="data:image/png;base64,{picture}"/>')
    out.append(tag(PAD + 6, top + 6, TAG_LEFT, mono))
    out.append(tag(PAD + THUMB - 6, top + THUMB - 21, TAG_RIGHT, mono, anchor_right=True))

    gx = PAD + THUMB + 16
    gy = top + 22
    for line in GREENTEXT:
        out.append(text(gx, gy, line, 13.5, c["text"], sans.family))
        gy += 21.6
    gy += 21.6
    out.append(text(gx, gy, QUESTION, 13.5, c["strong"], sans.family))
    cursor_x = gx + sans.width(QUESTION, 13.5) + 3
    out.append(f'<rect class="cursor" x="{cursor_x:.1f}" y="{gy + 1}" width="7" height="2" fill="{c["strong"]}"/>')

    ry = top + THUMB + 10
    box_w = max(bold.width(REPLY_NAME, 12.5) + sans.width(REPLY_NO, 12.5), sans.width(REPLY_TEXT, 12.5)) + 20
    box_h = 3 * 18 + 12
    out.append(f'<rect x="40.5" y="{ry + 0.5}" width="{box_w:.1f}" height="{box_h}" fill="{c["reply"]}" stroke="{c["line"]}"/>')
    ly = ry + 19
    out.append(text(50, ly, REPLY_NAME, 12.5, c["strong"], bold.family, "bold"))
    out.append(text(50 + bold.width(REPLY_NAME, 12.5), ly, REPLY_NO, 12.5, c["text"], sans.family))
    ly += 18
    out.append(text(50, ly, REPLY_QUOTE, 12.5, c["strong"], sans.family))
    out.append(underline(50, ly, sans.width(REPLY_QUOTE, 12.5), c["strong"]))
    ly += 18
    out.append(text(50, ly, REPLY_TEXT, 12.5, c["text"], sans.family))

    height = ry + box_h + 12
    frame = f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" fill="{c["page"]}" stroke="{c["line"]}"/>'
    body = "\n".join([frame, *out])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
        f'role="img" aria-label="An imageboard post by Nuno">\n<style>{style}</style>\n{body}\n</svg>\n'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sans", required=True, type=Path)
    parser.add_argument("--mono", required=True, type=Path)
    args = parser.parse_args()

    letters = "".join([NAME, STAMP, FILE_NAME, FILE_INFO, QUESTION, REPLY_NAME, REPLY_NO, REPLY_QUOTE, REPLY_TEXT, "File:_", *GREENTEXT])
    sans = sans_face(args.sans, 400, "post", letters)
    bold = sans_face(args.sans, 700, "postbold", letters)
    mono = subset_face("board", TTFont(args.mono), BOARD + NAV + TAG_LEFT + TAG_RIGHT)
    picture = base64.b64encode((ROOT / "assets" / "fellowstitch.png").read_bytes()).decode()

    style = (
        sans.css() + bold.css() + mono.css()
        + "text{white-space:pre}.cursor{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    )

    for theme in THEMES:
        (ROOT / "assets" / f"post-{theme}.svg").write_text(render(theme, sans, bold, mono, picture, style), encoding="utf-8")


if __name__ == "__main__":
    main()
