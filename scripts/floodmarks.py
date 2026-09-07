#!/usr/bin/env python3
"""Mark candidate landmarks on the unplaced flood sheets, so a person can name them.

The registration in floodreg.py and the scoring in floodcheck.py both failed on Amager,
Bispebjerg and København Vest. What is missing is not arithmetic - it is the step where
someone looks at a beach and says which beach. This produces the picture that makes that
step take a minute:

  - one annotated overview per sheet, with numbered markers
  - a contact sheet of zoomed crops, one per marker, so each is actually legible

Give back a NAME for any two markers on a sheet ("that is Damhussoeen") and geocoding
turns it into a coordinate; scripts/floodmaps.py georef does the rest and reports its own
residual, so a bad answer announces itself.

Usage:  python3 scripts/floodmarks.py [sheet ...]
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, read_json

OUT = os.path.join(DERIVED, "floodmaps")
DEST = os.path.join(ROOT, "viz", "georef_marks")

# Marker positions as a fraction of the map frame, picked by eye off the sheets for
# being distinctive, well separated, and point-like enough to carry a coordinate.
MARKS = {
    "amager": [
        ("1", 0.885, 0.047, "angular harbour basin with piers, top right"),
        ("2", 0.945, 0.235, "open water / bay on the east edge"),
        ("3", 0.900, 0.300, "enclosed basin inshore of the coast"),
        ("4", 0.115, 0.085, "pale water body in open ground, top left"),
        ("5", 0.957, 0.652, "beach and sand strip on the east edge"),
        ("6", 0.549, 0.972, "running track / sports ground, bottom"),
        ("7", 0.075, 0.055, "canal junction, far top left"),
    ],
    "bispebjerg": [
        ("1", 0.345, 0.395, "large dark lake or marsh, left of centre"),
        ("2", 0.800, 0.325, "white oval - stadium or arena, right of centre"),
        ("3", 0.965, 0.125, "coastline / shore, top right corner"),
        ("4", 0.430, 0.820, "regular green blocks - cemetery, bottom centre"),
        ("5", 0.130, 0.130, "open parkland with structures, top left"),
        ("6", 0.700, 0.130, "pale water body, upper right"),
    ],
    "kbhvest": [
        ("1", 0.255, 0.480, "long narrow lake running NW-SE, left of centre"),
        ("2", 0.365, 0.145, "dark lake, top centre"),
        ("3", 0.855, 0.760, "harbour basin with piers, bottom right"),
        ("4", 0.560, 0.975, "open water at the bottom edge"),
        ("5", 0.180, 0.545, "pale flooded area at the lake's south end"),
        ("6", 0.930, 0.560, "dense quays / rail area, right edge"),
    ],
}
CROP_M = 900.0        # metres each way around a marker in the zoomed crop


def _pil():
    from PIL import Image, ImageDraw
    return Image, ImageDraw


def frame_image(sheet, meta, Image):
    im = Image.open(os.path.join(OUT, f"{sheet}.render.png")).convert("RGB")
    fx0, fy0, fx1, fy1 = meta["frame"]
    return im.crop((fx0, fy0, fx1 + 1, fy1 + 1))


def ring(dr, x, y, r, label, colour=(255, 60, 60)):
    dr.ellipse([x - r, y - r, x + r, y + r], outline=colour, width=max(2, r // 7))
    dr.ellipse([x - 2, y - 2, x + 2, y + 2], fill=colour)
    bx, by = x + r + 4, y - r - 4
    dr.rectangle([bx, by, bx + 13 * len(label) + 8, by + 30], fill=(0, 0, 0))
    dr.text((bx + 5, by + 7), label, fill=(255, 230, 60))


def main(argv):
    Image, ImageDraw = _pil()
    os.makedirs(DEST, exist_ok=True)
    sheets = read_json(os.path.join(OUT, "_sheets.json"))
    index = {}

    for sheet in (argv or list(MARKS)):
        meta = sheets[sheet]
        marks = MARKS[sheet]
        base = frame_image(sheet, meta, Image)
        W, H = base.size
        mpp = meta["m_per_px"]

        # --- overview
        ov = base.copy()
        dr = ImageDraw.Draw(ov)
        for label, fx, fy, _desc in marks:
            ring(dr, fx * W, fy * H, max(26, W // 55), label)
        ov.thumbnail((1500, 1500))
        p_ov = os.path.join(DEST, f"{sheet}_overview.png")
        ov.save(p_ov)

        # --- contact sheet of crops
        n = len(marks)
        cols = 3
        rows = (n + cols - 1) // cols
        tile = 430
        sheet_im = Image.new("RGB", (cols * tile, rows * tile), (12, 14, 18))
        sd = ImageDraw.Draw(sheet_im)
        half = CROP_M / mpp
        for i, (label, fx, fy, desc) in enumerate(marks):
            cx, cy = fx * W, fy * H
            # clamp so a marker near an edge still gets a full, centred-ish crop
            x0 = min(max(0, int(cx - half)), max(0, W - int(2 * half)))
            y0 = min(max(0, int(cy - half)), max(0, H - int(2 * half)))
            box = (x0, y0, x0 + int(2 * half), y0 + int(2 * half))
            c = base.crop(box).resize((tile, tile), Image.LANCZOS)
            cx_in = (cx - x0) / (2 * half) * tile
            cy_in = (cy - y0) / (2 * half) * tile
            cd = ImageDraw.Draw(c)
            ring(cd, cx_in, cy_in, 34, label, colour=(255, 90, 90))
            sheet_im.paste(c, ((i % cols) * tile, (i // cols) * tile))
            sd.rectangle([(i % cols) * tile, (i // cols) * tile + tile - 22,
                          (i % cols) * tile + tile, (i // cols) * tile + tile],
                         fill=(0, 0, 0))
            sd.text(((i % cols) * tile + 6, (i // cols) * tile + tile - 18),
                    f"{label}  {desc[:44]}", fill=(220, 230, 240))
        p_cs = os.path.join(DEST, f"{sheet}_marks.png")
        sheet_im.save(p_cs)

        index[sheet] = {
            "frame_px": [W, H],
            "m_per_px": mpp,
            "extent_km": [round(W * mpp / 1000, 2), round(H * mpp / 1000, 2)],
            "map_scale": meta.get("map_scale"),
            "marks": [{"label": l, "fx": fx, "fy": fy, "desc": d,
                       "px": round(fx * W, 1), "py": round(fy * H, 1)}
                      for l, fx, fy, d in marks],
        }
        log(f"  {sheet:12} {W}x{H} px, {W*mpp/1000:.1f}x{H*mpp/1000:.1f} km, "
            f"{len(marks)} marks -> {os.path.basename(p_ov)}, {os.path.basename(p_cs)}")

    with open(os.path.join(DEST, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    log(f"\nwrote {DEST}/index.json")
    log("Name any two marks per sheet and floodmaps.py georef can place it.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
