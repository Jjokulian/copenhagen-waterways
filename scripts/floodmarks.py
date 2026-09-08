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
# Dots for the click-and-report loop: a person finds each on a map and reports its
# coordinate. Several, spread out, on point-like features - so their clicking noise
# averages down instead of becoming a systematic offset.
DOTS = {
    "amager": [
        (0.885, 0.047), (0.945, 0.300), (0.957, 0.652),
        (0.549, 0.972), (0.100, 0.070), (0.075, 0.905),
    ],
    # Chosen to sit ON something with recognisable geometry - a lake's corner, a
    # stadium, a marina basin, a motorway junction - rather than on featureless housing,
    # because a dot on a repeating suburb cannot be placed accurately by anyone.
    # Bispebjerg's first two points sat at almost the same height, which is why its
    # standard error is 91 m against 58 m elsewhere: with the scale fixed, vertical
    # position is only as good as the vertical spread of the points. These two are
    # deliberately at the top and the bottom.
    "bispebjerg": [
        (0.760, 0.088), (0.300, 0.905),
    ],
    "kbhvest": [
        (0.243, 0.452), (0.176, 0.540), (0.838, 0.742),
        (0.548, 0.962), (0.118, 0.135), (0.905, 0.548),
    ],
}
DOT_CROP_M = 350.0    # half-width of each zoom inset, metres

CROP_M = 900.0        # metres each way around a marker in the zoomed crop
GRID_M = 500.0        # reference grid spacing on the overview, in metres


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


def dot_sheet(sheet, meta, Image, ImageDraw):
    """One image: the whole sheet with numbered dots, and a zoom inset for each."""
    base = frame_image(sheet, meta, Image)
    W, H = base.size
    mpp = meta["m_per_px"]
    dots = DOTS[sheet]

    def dot(dr, x, y, r, lab):
        col = (255, 45, 45)
        dr.ellipse([x - r * 2.4, y - r * 2.4, x + r * 2.4, y + r * 2.4],
                   outline=col, width=max(2, r // 8))
        dr.ellipse([x - r, y - r, x + r, y + r], outline=col, width=max(3, r // 4))
        dr.ellipse([x - r // 3, y - r // 3, x + r // 3, y + r // 3], fill=col)
        bx, by = x + r * 2.6, y - r * 2.6
        dr.rectangle([bx, by, bx + 42, by + 40], fill=(0, 0, 0))
        dr.text((bx + 15, by + 12), lab, fill=(255, 235, 60))

    ov = base.copy()
    d = ImageDraw.Draw(ov)
    for i, (fx, fy) in enumerate(dots, 1):
        dot(d, fx * W, fy * H, max(18, W // 90), str(i))
    ov_target_h = ((len(dots) + 1) // 2) * 420
    ov = ov.resize((max(1, int(ov.width * ov_target_h / ov.height)), ov_target_h),
                   Image.LANCZOS)
    if ov.width > 900:
        ov.thumbnail((900, 10**6))

    tile, half = 420, DOT_CROP_M / mpp
    insets = []
    for i, (fx, fy) in enumerate(dots, 1):
        cx, cy = fx * W, fy * H
        x0 = min(max(0, int(cx - half)), max(0, W - int(2 * half)))
        y0 = min(max(0, int(cy - half)), max(0, H - int(2 * half)))
        c = base.crop((x0, y0, x0 + int(2 * half), y0 + int(2 * half))
                      ).resize((tile, tile), Image.LANCZOS)
        cd = ImageDraw.Draw(c)
        dot(cd, (cx - x0) / (2 * half) * tile, (cy - y0) / (2 * half) * tile, 16, str(i))
        cd.rectangle([0, tile - 20, tile, tile], fill=(0, 0, 0))
        cd.text((6, tile - 16), f"{i}   {2*DOT_CROP_M:.0f} m across", fill=(225, 235, 245))
        insets.append(c)

    cols = 2
    rows = (len(insets) + cols - 1) // cols
    right_w, right_h = cols * tile, rows * tile
    out = Image.new("RGB", (ov.width + 8 + right_w, max(ov.height, right_h)), (10, 12, 16))
    out.paste(ov, (0, 0))
    for i, c in enumerate(insets):
        out.paste(c, (ov.width + 8 + (i % cols) * tile, (i // cols) * tile))
    return out


def main(argv):
    Image, ImageDraw = _pil()
    os.makedirs(DEST, exist_ok=True)
    sheets = read_json(os.path.join(OUT, "_sheets.json"))
    index = {}

    if argv and argv[0] == "dots":
        for sheet in (argv[1:] or list(DOTS)):
            meta = sheets[sheet]
            im = dot_sheet(sheet, meta, Image, ImageDraw)
            p = os.path.join(DEST, f"{sheet}_dots.jpg")
            im.save(p, quality=90, optimize=True)
            W = meta["frame"][2] - meta["frame"][0] + 1
            H = meta["frame"][3] - meta["frame"][1] + 1
            index[sheet] = {"m_per_px": meta["m_per_px"], "frame_px": [W, H],
                            "dots": [{"n": i, "fx": fx, "fy": fy,
                                      "px": round(fx * W, 1), "py": round(fy * H, 1)}
                                     for i, (fx, fy) in enumerate(DOTS[sheet], 1)]}
            log(f"  {sheet:12} {len(DOTS[sheet])} dots -> {os.path.basename(p)}")
        with open(os.path.join(DEST, "dots.json"), "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=1)
        log(f"\nwrote {DEST}/dots.json")
        return 0

    for sheet in (argv or list(MARKS)):
        meta = sheets[sheet]
        marks = MARKS[sheet]
        base = frame_image(sheet, meta, Image)
        W, H = base.size
        mpp = meta["m_per_px"]

        # --- overview, with a reference grid so a place can be pointed at as well as
        # named. Columns A.. across, rows 1.. down, one cell per 500 m so a grid
        # reference is also a rough distance.
        ov = base.copy()
        dr = ImageDraw.Draw(ov)
        cell_px = GRID_M / mpp
        ncol = int(W / cell_px) + 1
        nrow = int(H / cell_px) + 1
        for i in range(1, ncol):
            x = i * cell_px
            dr.line([(x, 0), (x, H)], fill=(255, 235, 60), width=2)
        for j in range(1, nrow):
            y = j * cell_px
            dr.line([(0, y), (W, y)], fill=(255, 235, 60), width=2)
        for i in range(ncol):
            for j in range(nrow):
                ref = f"{chr(65+i)}{j+1}"
                bx, by = i * cell_px + 6, j * cell_px + 6
                dr.rectangle([bx, by, bx + 13 * len(ref) + 8, by + 30], fill=(0, 0, 0))
                dr.text((bx + 5, by + 7), ref, fill=(255, 235, 60))
        for label, fx, fy, _desc in marks:
            ring(dr, fx * W, fy * H, max(26, W // 55), label)
        ov.thumbnail((2000, 2000))
        p_ov = os.path.join(DEST, f"{sheet}_overview.jpg")
        ov.save(p_ov, quality=88, optimize=True)

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
        p_cs = os.path.join(DEST, f"{sheet}_marks.jpg")
        sheet_im.save(p_cs, quality=90, optimize=True)

        index[sheet] = {
            "frame_px": [W, H],
            "m_per_px": mpp,
            "extent_km": [round(W * mpp / 1000, 2), round(H * mpp / 1000, 2)],
            "map_scale": meta.get("map_scale"),
            "grid_m": GRID_M,
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
