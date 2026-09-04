"""Regenerate the derived art that index.html inlines as base64.

index.html carries its images inline so that the PNG export never depends on the
network and never taints the export canvas. That makes the blobs opaque, so this
script rebuilds every one of them from the logo masters in ../assets.

    python tools/build_assets.py            # write ../assets/*.png
    python tools/build_assets.py --emit-b64 # also drop <name>.b64 next to them

Requires: pillow, numpy.
"""

import argparse
import base64
import io
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# The masters are flat two-colour JPEGs; these are the two grounds they sit on.
NAVY_GROUND = (9, 21, 71)      # IBRAHIM LOGO-02.jpg — white art on navy
WHITE_GROUND = (255, 255, 255)  # IBRAHIM LOGO-03.jpg — navy art on white
PATTERN_INK = (16, 28, 82)     # navy tile, for the light palette

# Fraction of the lockup height that is calligraphy; below it sit the "Masjid"
# script and the "IBRAHIM" wordmark, which are too legible to use as a ghost.
CREST_CUT = 0.762


def save(img, name, emit_b64):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True, compress_level=9)
    png = buf.getvalue()
    (ASSETS / f"{name}.png").write_bytes(png)
    if emit_b64:
        (ASSETS / f"{name}.b64").write_text(base64.b64encode(png).decode())
    print(f"  {name+'.png':20} {img.size[0]:4d}x{img.size[1]:<4d} {len(png)/1024:7.1f} KB")


def trim(img, threshold=8):
    """Crop away fully transparent / black margins."""
    channel = img.getchannel("A") if img.mode == "RGBA" else img
    return img.crop(channel.point(lambda p: 255 if p > threshold else 0).getbbox())


def alpha_from(path, ground, ink, floor=0.06, span=0.88):
    """Alpha = how far each pixel travelled from the ground toward the ink.

    Contrast is stretched by (floor, span) so JPEG ringing around the strokes
    does not leave a haze of the original background colour.
    """
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    ground = np.array(ground, dtype=np.float32)
    ink = np.array(ink, dtype=np.float32)
    projected = ((a - ground) * (ink - ground)).sum(2) / ((ink - ground) ** 2).sum()
    return np.clip((np.clip(projected, 0, 1) - floor) / span, 0, 1)


def build_logo_masks(emit_b64):
    """Greyscale masks whose level is the alpha the page tints at runtime."""
    alpha = alpha_from(ASSETS / "IBRAHIM LOGO-02.jpg", NAVY_GROUND, WHITE_GROUND)
    mask = trim(Image.fromarray((alpha * 255).round().astype(np.uint8), "L"))

    width = 820
    logo = mask.resize((width, round(mask.size[1] * width / mask.size[0])), Image.LANCZOS)
    save(logo, "logo-mask", emit_b64)

    crest = trim(mask.crop((0, 0, mask.size[0], int(mask.size[1] * CREST_CUT))))
    width = 620
    crest = crest.resize((width, round(crest.size[1] * width / crest.size[0])), Image.LANCZOS)
    save(crest, "crest-mask", emit_b64)


def build_pattern(emit_b64, tile=120, supersample=6):
    """A seamless 8-point khatam lattice, drawn 3x3 and cropped to the centre tile."""
    size = tile * supersample
    big = Image.new("L", (size * 3, size * 3), 0)
    draw = ImageDraw.Draw(big)
    stroke = int(1.15 * supersample)

    for gx in range(-1, 7):
        for gy in range(-1, 7):
            cx, cy = gx * size / 2, gy * size / 2
            rot = math.pi / 4 if (gx + gy) % 2 else 0.0
            # two overlapping squares make the eight-pointed star
            for k in (0, 1):
                draw.polygon(
                    [
                        (
                            cx + size * 0.19 * math.cos(rot + k * math.pi / 4 + i * math.pi / 2),
                            cy + size * 0.19 * math.sin(rot + k * math.pi / 4 + i * math.pi / 2),
                        )
                        for i in range(4)
                    ],
                    outline=255,
                    width=stroke,
                )

    for i in range(-6, 13):  # the connective diagonal net
        draw.line([(i * size / 2, -size), (i * size / 2 + 4 * size, 3 * size)],
                  fill=110, width=int(0.8 * supersample))
        draw.line([(i * size / 2, 3 * size), (i * size / 2 + 4 * size, -size)],
                  fill=110, width=int(0.8 * supersample))

    alpha = big.crop((size, size, 2 * size, 2 * size)).resize((tile, tile), Image.LANCZOS)
    white = Image.merge("RGBA", (Image.new("L", (tile, tile), 255),) * 3 + (alpha,))
    save(white, "pattern", emit_b64)

    dark = np.asarray(white).copy()
    dark[..., 0], dark[..., 1], dark[..., 2] = PATTERN_INK
    save(Image.fromarray(dark, "RGBA"), "pattern-dark", emit_b64)


def build_qr(emit_b64, source="donate-qr.png", quiet=4, scale=8):
    """Re-render the donation QR from its own module grid, so it stays crisp.

    The original was a JPEG; snapping it back to modules removes the artefacts
    without touching the payload (https://payments.madinaapps.com/masjidibrahimtx).
    """
    path = ASSETS / source
    if not path.exists():
        print(f"  skipping QR — {source} not found")
        return

    a = np.asarray(Image.open(path).convert("L"))
    dark = a < 128
    ys, xs = np.where(dark)
    crop = Image.fromarray(
        (~dark[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]).astype(np.uint8) * 255, "L"
    )

    for modules in range(21, 78, 2):
        grid = np.asarray(crop.resize((modules, modules), Image.BOX)) < 128
        rebuilt = Image.fromarray((~grid).astype(np.uint8) * 255, "L").resize(
            crop.size, Image.NEAREST
        )
        if np.abs(np.asarray(rebuilt).astype(int) - np.asarray(crop).astype(int)).mean() < 6:
            break
    else:
        raise SystemExit("could not find a clean module grid for the QR")

    n = modules + 2 * quiet
    out = np.ones((n, n), bool)
    out[quiet:quiet + modules, quiet:quiet + modules] = ~grid
    img = Image.fromarray(out.astype(np.uint8) * 255, "L").resize(
        (n * scale, n * scale), Image.NEAREST
    ).convert("1")
    save(img, "donate-qr", emit_b64)
    print(f"  QR rebuilt at {modules} modules")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-b64", action="store_true",
                        help="also write <name>.b64 for pasting into index.html")
    args = parser.parse_args()

    print(f"writing to {ASSETS}")
    build_logo_masks(args.emit_b64)
    build_pattern(args.emit_b64)
    build_qr(args.emit_b64)
