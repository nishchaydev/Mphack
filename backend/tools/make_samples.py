"""Render the synthetic "handwritten" answer pages in samples/.

These are stand-ins so the demo runs end to end. Replace them with photos of
real handwriting written by your team (see POC_GUIDE.md) before the finale.

    .venv/bin/python backend/tools/make_samples.py
"""
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "backend" / "fonts"
OUT = ROOT / "samples"

W, H = 1240, 1754  # A4 at 150 DPI
MARGIN_X = 150
LINE_GAP = 58
FIRST_LINE_Y = 250
INK = (28, 42, 110)
RULE = (196, 212, 236)

hand = ImageFont.truetype(str(FONTS / "Kalam-Regular.ttf"), 38, layout_engine=ImageFont.Layout.RAQM)
hand_small = ImageFont.truetype(str(FONTS / "Kalam-Regular.ttf"), 30, layout_engine=ImageFont.Layout.RAQM)
printed = ImageFont.truetype(str(FONTS / "Mukta-Regular.ttf"), 22, layout_engine=ImageFont.Layout.RAQM)


def paper(rng, booklet, page_no):
    img = Image.new("RGB", (W, H), (251, 250, 244))
    d = ImageDraw.Draw(img)
    for y in range(FIRST_LINE_Y + 12, H - 120, LINE_GAP):
        d.line([(60, y), (W - 60, y)], fill=RULE, width=2)
    d.line([(MARGIN_X - 20, 150), (MARGIN_X - 20, H - 100)], fill=(232, 160, 160), width=2)
    # Printed booklet header with a fake barcode.
    d.rectangle([60, 50, W - 60, 140], outline=(150, 150, 150), width=2)
    d.text((80, 62), "Answer Booklet · उत्तर पुस्तिका", font=printed, fill=(90, 90, 90))
    d.text((80, 98), f"Fictitious code: {booklet}    Page {page_no}", font=printed, fill=(90, 90, 90))
    x = W - 420
    while x < W - 80:
        bar = rng.choice([2, 3, 5])
        d.rectangle([x, 62, x + bar, 128], fill=(40, 40, 40))
        x += bar + rng.choice([2, 3, 4])
    d.text((80, H - 80), "SYNTHETIC DEMO SAMPLE · not a real student script", font=printed, fill=(175, 175, 175))
    return img


def bleed_through(rng, img):
    """Faint mirrored writing from the back of the sheet, as on 54-60 GSM paper."""
    layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(layer)
    for y in range(FIRST_LINE_Y + 40, H - 300, LINE_GAP * 2):
        d.text((MARGIN_X + rng.randint(0, 80), y), "संसद कानून व्यवस्था न्यायालय अधिकार", font=hand, fill=255)
    layer = layer.transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(2))
    ghost = Image.new("RGB", (W, H), (150, 160, 190))
    img.paste(ghost, (0, 0), layer.point(lambda v: int(v * 0.10)))


def wrap(text, font, width):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def write_lines(rng, img, lines, start_line=0):
    """Write each paragraph onto the ruled lines with a little jitter and tilt."""
    row = start_line
    for para in lines:
        for visual in wrap(para, hand, W - MARGIN_X - 110):
            y = FIRST_LINE_Y + row * LINE_GAP - 40 + rng.randint(-3, 3)
            layer = Image.new("RGBA", (W, LINE_GAP + 40), (0, 0, 0, 0))
            ink = tuple(max(0, c + rng.randint(-12, 12)) for c in INK)
            ImageDraw.Draw(layer).text((MARGIN_X + rng.randint(-4, 10), 8), visual, font=hand, fill=ink + (235,))
            layer = layer.rotate(rng.uniform(-0.5, 0.5), resample=Image.BICUBIC, center=(MARGIN_X, 30))
            img.paste(layer, (0, y), layer)
            row += 1
        row += 0  # paragraphs sit on consecutive lines, like real answers
    return row


def wobble(d, p1, p2, rng, width=3):
    (x1, y1), (x2, y2) = p1, p2
    n = max(2, int(math.dist(p1, p2) / 18))
    pts = []
    for i in range(n + 1):
        t = i / n
        jitter = 0 if i in (0, n) else rng.uniform(-1.6, 1.6)
        nx, ny = (y2 - y1), -(x2 - x1)
        norm = math.hypot(nx, ny) or 1
        pts.append((x1 + (x2 - x1) * t + jitter * nx / norm, y1 + (y2 - y1) * t + jitter * ny / norm))
    d.line(pts, fill=INK, width=width, joint="curve")


def resistor(d, p1, p2, rng, vertical=False):
    (x1, y1), (x2, y2) = p1, p2
    pts, zig = [], 8
    for i in range(zig + 1):
        t = i / zig
        off = 0 if i in (0, zig) else (16 if i % 2 else -16)
        if vertical:
            pts.append((x1 + off, y1 + (y2 - y1) * t))
        else:
            pts.append((x1 + (x2 - x1) * t, y1 + off))
    for a, b in zip(pts, pts[1:]):
        wobble(d, a, b, rng)


def battery(d, x, y, rng, label):
    wobble(d, (x - 34, y), (x + 34, y), rng, 4)
    wobble(d, (x - 18, y + 18), (x + 18, y + 18), rng, 6)
    d.text((x + 46, y - 6), label, font=hand_small, fill=INK)


def ce_circuit(rng, img):
    d = ImageDraw.Draw(img)
    cx, cy = 640, 820
    d.ellipse([cx - 80, cy - 80, cx + 80, cy + 80], outline=INK, width=3)
    wobble(d, (cx - 30, cy - 50), (cx - 30, cy + 50), rng, 6)          # base bar
    wobble(d, (cx - 30, cy - 22), (cx + 40, cy - 70), rng)             # collector
    wobble(d, (cx - 30, cy + 22), (cx + 40, cy + 70), rng)             # emitter
    d.polygon([(cx + 40, cy + 70), (cx + 16, cy + 66), (cx + 30, cy + 48)], fill=INK)  # NPN arrow out
    wobble(d, (cx + 40, cy - 70), (cx + 40, cy - 160), rng)
    wobble(d, (cx + 40, cy + 70), (cx + 40, cy + 230), rng)
    # Base side: RB and VBB.
    wobble(d, (cx - 30, cy), (cx - 150, cy), rng)
    resistor(d, (cx - 330, cy), (cx - 150, cy), rng)
    d.text((cx - 270, cy - 70), "RB", font=hand_small, fill=INK)
    wobble(d, (cx - 330, cy), (cx - 420, cy), rng)
    wobble(d, (cx - 420, cy), (cx - 420, cy + 80), rng)
    battery(d, cx - 420, cy + 80, rng, "VBB")
    wobble(d, (cx - 420, cy + 98), (cx - 420, cy + 230), rng)
    # Collector side: RC and VCC.
    resistor(d, (cx + 40, cy - 160), (cx + 40, cy - 330), rng, vertical=True)
    d.text((cx + 70, cy - 270), "RC", font=hand_small, fill=INK)
    wobble(d, (cx + 40, cy - 330), (cx + 330, cy - 330), rng)
    wobble(d, (cx + 330, cy - 330), (cx + 330, cy - 40), rng)
    battery(d, cx + 330, cy - 40, rng, "VCC")
    wobble(d, (cx + 330, cy - 22), (cx + 330, cy + 230), rng)
    # Common ground rail.
    wobble(d, (cx - 420, cy + 230), (cx + 330, cy + 230), rng)
    for i, half in enumerate((36, 24, 12)):
        wobble(d, (cx + 40 - half, cy + 254 + i * 14), (cx + 40 + half, cy + 254 + i * 14), rng)
    for text, pos in (("B", (cx - 70, cy - 50)), ("C", (cx + 56, cy - 120)), ("E", (cx + 56, cy + 90)),
                      ("IB", (cx - 140, cy + 14)), ("IC", (cx + 60, cy - 220))):
        d.text(pos, text, font=hand_small, fill=INK)
    # Current arrows drawn by hand (the font has no arrow glyphs).
    wobble(d, (cx - 100, cy + 36), (cx - 60, cy + 36), rng, 2)
    d.polygon([(cx - 56, cy + 36), (cx - 68, cy + 30), (cx - 68, cy + 42)], fill=INK)
    wobble(d, (cx + 112, cy - 216), (cx + 112, cy - 186), rng, 2)
    d.polygon([(cx + 112, cy - 180), (cx + 106, cy - 192), (cx + 118, cy - 192)], fill=INK)


def finish(rng, img):
    img = img.rotate(rng.uniform(-0.35, 0.35), resample=Image.BICUBIC, fillcolor=(251, 250, 244))
    return img.filter(ImageFilter.GaussianBlur(0.5))


def main():
    answers = json.loads((ROOT / "backend" / "demo_data" / "sample_answers.json").read_text(encoding="utf-8"))
    OUT.mkdir(exist_ok=True)
    for booklet, pages in answers.items():
        rng = random.Random(booklet)
        for i, page in enumerate(pages, start=1):
            img = paper(rng, booklet, i)
            bleed_through(rng, img)
            write_lines(rng, img, page["lines"])
            if page.get("diagram") == "ce_circuit":
                ce_circuit(rng, img)
            path = OUT / f"{booklet}_p{i}.png"
            finish(rng, img).save(path, optimize=True)
            print("wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
