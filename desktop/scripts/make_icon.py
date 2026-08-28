#!/usr/bin/env python3
"""Paint the ColdBrew app icon as PNG + multi-size ICO. Exact 破 glyph."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "assets"
PNG = OUT_DIR / "icon.png"
ICO = OUT_DIR / "icon.ico"
SIZES = (16, 24, 32, 48, 64, 128, 256)

INK = (42, 24, 16, 255)
GOLD = (196, 92, 20, 255)
CREAM = (247, 239, 227, 255)
COPPER = (232, 168, 114, 255)
BLADES = [
    (232, 168, 114, 255),
    (245, 215, 110, 255),
    (255, 107, 168, 255),
    (94, 231, 255, 255),
    (128, 240, 188, 255),
]


def font_for(size: int) -> ImageFont.FreeTypeFont:
    for name in ("msyhbd.ttc", "msyh.ttc", "simhei.ttf", "simsun.ttc"):
        path = Path(r"C:\Windows\Fonts") / name
        if path.is_file():
            try:
                return ImageFont.truetype(str(path), size=size, index=0)
            except OSError:
                continue
    return ImageFont.load_default()


def paint(size: int) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    pad = max(1, size // 32)
    box = [pad, pad, size - pad - 1, size - pad - 1]
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse(box, fill=(196, 92, 20, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=max(1, size // 18)))
    image = Image.alpha_composite(image, glow)
    draw = ImageDraw.Draw(image)
    draw.ellipse(box, fill=INK)
    ring = max(1, size // 28)
    draw.ellipse(box, outline=GOLD, width=ring)
    cx = cy = size / 2
    radius = size * 0.42
    for index, color in enumerate(BLADES):
        angle = math.radians(-90 + index * 72)
        x2 = cx + math.cos(angle) * radius
        y2 = cy + math.sin(angle) * radius
        x1 = cx + math.cos(angle) * radius * 0.38
        y1 = cy + math.sin(angle) * radius * 0.38
        width = max(1, size // 22)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=width)
    glyph = "破"
    font = font_for(int(size * 0.46))
    bbox = draw.textbbox((0, 0), glyph, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size - tw) / 2 - bbox[0]
    y = (size - th) / 2 - bbox[1] - size * 0.02
    draw.text((x + 1, y + 1), glyph, font=font, fill=(0, 0, 0, 90))
    draw.text((x, y), glyph, font=font, fill=CREAM)
    inner = [pad + ring * 3, pad + ring * 3, size - pad - ring * 3 - 1, size - pad - ring * 3 - 1]
    if size >= 32:
        draw.ellipse(inner, outline=COPPER, width=max(1, ring // 2))
    return image


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    master = paint(512)
    master.save(PNG)
    icons = [paint(size) for size in SIZES]
    icons[-1].save(ICO, format="ICO", sizes=[(size, size) for size in SIZES], append_images=icons[:-1])
    print(f"PNG {PNG}")
    print(f"ICO {ICO}")


if __name__ == "__main__":
    main()
