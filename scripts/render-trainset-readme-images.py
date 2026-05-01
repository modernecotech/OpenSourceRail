#!/usr/bin/env python3
"""Render README trainset images from the current OSR design basis.

These are deliberately deterministic bitmap diagrams rather than AI
concept art: the labels and geometry need to track the final 17 m
self-contained car module exactly.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"

NAVY = (15, 38, 67)
BLUE = (28, 98, 156)
GREEN = (33, 116, 71)
INK = (22, 31, 42)
MUTED = (92, 102, 114)
PAPER = (246, 248, 250)
LINE = (176, 184, 194)
BODY = (224, 228, 232)
GLASS = (140, 188, 214)
DOOR = (10, 43, 82)
SKIRT = (61, 68, 78)
SEAT = (42, 104, 152)
BATTERY = (46, 58, 82)
SOLAR = (32, 74, 128)
YELLOW = (241, 187, 69)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


F12 = font(12)
F14 = font(14)
F16 = font(16)
F18 = font(18)
F20B = font(20, True)
F24B = font(24, True)
F32B = font(32, True)
F42B = font(42, True)


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], s: str, fill=INK, f=F16) -> None:
    draw.text(xy, s, fill=fill, font=f)


def panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str | None = None) -> None:
    draw.rounded_rectangle(box, radius=10, fill=(255, 255, 255), outline=LINE, width=2)
    if title:
        text(draw, (box[0] + 18, box[1] + 14), title, NAVY, F20B)


def train_car(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    *,
    label: str | None = None,
    show_bogies: bool = True,
) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=BODY, outline=(178, 184, 190), width=2)
    draw.rectangle((x + 5, y + h - 18, x + w - 5, y + h - 10), fill=BLUE)
    draw.rectangle((x + 20, y + 26, x + w // 2 - 26, y + 62), fill=GLASS, outline=(116, 150, 168))
    draw.rectangle((x + w // 2 + 26, y + 26, x + w - 20, y + 62), fill=GLASS, outline=(116, 150, 168))
    door_w = 38
    draw.rectangle((x + w // 2 - door_w // 2, y + 20, x + w // 2 + door_w // 2, y + h - 14), fill=DOOR)
    draw.line((x + w // 2, y + 22, x + w // 2, y + h - 16), fill=(190, 205, 220), width=1)
    draw.rectangle((x + 34, y - 10, x + 76, y + 2), fill=(93, 99, 110))
    draw.rectangle((x + w - 76, y - 10, x + w - 34, y + 2), fill=(93, 99, 110))
    draw.rectangle((x + 32, y + h + 3, x + w - 32, y + h + 14), fill=SKIRT)
    if show_bogies:
        bog_w = 70
        for bx in (x + 56, x + w - 56 - bog_w):
            draw.rounded_rectangle((bx, y + h + 18, bx + bog_w, y + h + 39), radius=4, fill=(31, 36, 44))
            for cx in (bx + 18, bx + 52):
                draw.ellipse((cx - 8, y + h + 25, cx + 8, y + h + 41), fill=(18, 22, 28))
    if label:
        tw = draw.textlength(label, font=F14)
        text(draw, (int(x + w / 2 - tw / 2), y - 34), label, NAVY, F14)


def draw_dimension(draw: ImageDraw.ImageDraw, x1: int, y: int, x2: int, label: str) -> None:
    draw.line((x1, y, x2, y), fill=MUTED, width=2)
    draw.line((x1, y - 5, x1, y + 5), fill=MUTED, width=2)
    draw.line((x2, y - 5, x2, y + 5), fill=MUTED, width=2)
    tw = draw.textlength(label, font=F14)
    text(draw, (int((x1 + x2 - tw) / 2), y + 8), label, MUTED, F14)


def draw_solar_canopy(draw: ImageDraw.ImageDraw, x: int, y: int, w: int) -> None:
    draw.polygon([(x, y + 22), (x + w, y), (x + w - 15, y + 34), (x - 15, y + 56)], fill=(204, 214, 220), outline=LINE)
    cols = 9
    for i in range(cols):
        px = x + 12 + i * ((w - 40) // cols)
        draw.polygon([(px, y + 24), (px + 70, y + 16), (px + 64, y + 36), (px - 6, y + 44)], fill=SOLAR, outline=(20, 54, 92))
    for px in (x + 70, x + w - 80):
        draw.rectangle((px, y + 48, px + 8, y + 150), fill=(104, 112, 122))


def render_infographic() -> None:
    img = Image.new("RGB", (1536, 1024), PAPER)
    d = ImageDraw.Draw(img)
    text(d, (34, 24), "OpenSourceRail final rolling-stock basis", NAVY, F42B)
    text(d, (38, 74), "17 m self-contained cars | one powered bogie + one trailer bogie per car | under-seat Na-ion | station charging", GREEN, F20B)

    panel(d, (24, 116, 1512, 372), "3-car light-metro reference")
    x0, y0, cw, ch, gap = 92, 210, 390, 78, 18
    for i, label in enumerate(("Car A - self-contained", "Car B - self-contained", "Car C - self-contained")):
        train_car(d, x0 + i * (cw + gap), y0, cw, ch, label=label)
        if i < 2:
            d.rectangle((x0 + (i + 1) * cw + i * gap, y0 + 10, x0 + (i + 1) * cw + i * gap + gap, y0 + ch - 8), fill=(76, 80, 88))
    draw_dimension(d, x0, y0 + 140, x0 + 3 * cw + 2 * gap, "57 m nominal consist, 56.6 m over cowls/couplers")
    text(d, (78, 326), "No cab, no windscreen: sensor cowls at both ends. No roof solar on the train. No continuous catenary.", INK, F18)

    panel(d, (24, 398, 738, 720), "Per-car layout")
    bx, by = 70, 492
    d.rounded_rectangle((bx, by, bx + 620, by + 150), radius=28, fill=(236, 239, 242), outline=LINE, width=2)
    d.rectangle((bx + 274, by + 8, bx + 346, by + 142), fill=(218, 224, 230), outline=LINE)
    d.rectangle((bx + 288, by + 28, bx + 332, by + 122), fill=DOOR)
    for sx in (bx + 34, bx + 174, bx + 408, bx + 548):
        d.rounded_rectangle((sx, by + 20, sx + 74, by + 42), radius=5, fill=SEAT)
        d.rounded_rectangle((sx, by + 108, sx + 74, by + 130), radius=5, fill=SEAT)
        d.rectangle((sx, by + 48, sx + 74, by + 65), fill=BATTERY)
        d.rectangle((sx, by + 85, sx + 74, by + 102), fill=BATTERY)
    text(d, (70, 664), "20 seats per car. Battery modules sit below the longitudinal benches.", INK, F16)
    text(d, (70, 690), "The centre door zone stays clear and low-floor; capacity scales by adding cars.", INK, F16)

    panel(d, (768, 398, 1512, 720), "Passenger and energy basis")
    rows = [
        ("Seats", "60 per 3-car trainset"),
        ("AW2 nominal capacity", "330 passengers for planning"),
        ("AW3 crush reference", "420 passengers for structure/egress"),
        ("Onboard battery", "360 kWh usable, 120 kWh per car"),
        ("Charging", "Automated conductive charge at stops"),
        ("Station spacing", "About 1 km, about 60 s dwell"),
    ]
    for i, (k, v) in enumerate(rows):
        y = 464 + i * 38
        text(d, (810, y), k, NAVY, F16)
        text(d, (1058, y), v, INK, F16)
        d.line((802, y + 27, 1470, y + 27), fill=(224, 229, 234), width=1)

    panel(d, (24, 748, 738, 992), "Station charging, not route power")
    draw_solar_canopy(d, 86, 812, 560)
    d.rectangle((82, 934, 646, 942), fill=(78, 82, 88))
    train_car(d, 170, 862, 390, 62, show_bogies=False)
    d.line((360, 820, 360, 862), fill=YELLOW, width=5)
    text(d, (88, 952), "Solar + stationary battery at stations buffers PV/grid energy.", INK, F16)
    text(d, (88, 976), "Trains charge during normal passenger dwell.", INK, F16)

    panel(d, (768, 748, 1512, 992), "Why this is the final design basis")
    bullets = [
        "One common 17 m module simplifies fabrication and spares.",
        "One powered bogie per car keeps traction modular.",
        "Under-seat Na-ion keeps mass low and avoids roof batteries.",
        "Driverless onboard sensing removes most signalling cost.",
        "No train roof solar: solar belongs on stations and depots.",
    ]
    for i, b in enumerate(bullets):
        y = 812 + i * 34
        d.ellipse((812, y + 5, 824, y + 17), fill=GREEN)
        text(d, (840, y), b, INK, F16)

    img.save(ROOT / "a_clean_infographic_technical_presentation_image_s.png")


def render_hero() -> None:
    img = Image.new("RGB", (2200, 920), (235, 226, 210))
    d = ImageDraw.Draw(img)
    # Sky gradient.
    for y in range(920):
        t = y / 920
        r = int(246 * (1 - t) + 210 * t)
        g = int(238 * (1 - t) + 198 * t)
        b = int(220 * (1 - t) + 174 * t)
        d.line((0, y, 2200, y), fill=(r, g, b))
    # Background city blocks.
    for i, x in enumerate(range(-80, 2200, 140)):
        h = 80 + (i % 5) * 28
        d.rectangle((x, 520 - h, x + 120, 650), fill=(190, 158, 125))
        d.rectangle((x + 18, 520 - h + 22, x + 38, 520 - h + 46), fill=(136, 116, 96))
    # Solar station canopy.
    draw_solar_canopy(d, 360, 250, 1080)
    d.rectangle((0, 630, 2200, 920), fill=(206, 190, 168))
    d.rectangle((0, 670, 2200, 760), fill=(168, 160, 150))
    d.line((0, 792, 2200, 760), fill=(78, 76, 76), width=5)
    d.line((0, 842, 2200, 810), fill=(78, 76, 76), width=5)
    # Train.
    x0, y0, cw, ch, gap = 470, 575, 360, 88, 16
    for i in range(3):
        train_car(d, x0 + i * (cw + gap), y0, cw, ch)
        if i < 2:
            d.rectangle((x0 + (i + 1) * cw + i * gap, y0 + 10, x0 + (i + 1) * cw + i * gap + gap, y0 + ch - 8), fill=(58, 60, 66))
    # Sensor cowls.
    d.rounded_rectangle((x0 - 52, y0 + 4, x0 + 12, y0 + ch - 4), radius=20, fill=BODY, outline=LINE, width=2)
    d.rounded_rectangle((x0 + 3 * cw + 2 * gap - 12, y0 + 4, x0 + 3 * cw + 2 * gap + 52, y0 + ch - 4), radius=20, fill=BODY, outline=LINE, width=2)
    text(d, (72, 72), "OpenSourceRail", NAVY, F42B)
    text(d, (76, 128), "Catenary-free driverless trains charged at solar-buffered stations", GREEN, F24B)
    text(d, (76, 176), "17 m self-contained cars | one centre door per side | under-seat sodium-ion batteries", INK, F20B)
    img.save(OUT / "osr-final-design-hero.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    render_infographic()
    render_hero()
    print("wrote final-design README images")


if __name__ == "__main__":
    main()
