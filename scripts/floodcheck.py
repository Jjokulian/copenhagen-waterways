#!/usr/bin/env python3
"""Draw the real coastline on top of a flood sheet's own aerial photo, at a proposed
position, so a human (or a model that can look at an image) can say yes or no.

The automatic registration in floodreg.py answers "where do the water masks correlate
best". That is the right question and it produced four confident sheets, but on three it
returned candidates that disagree, and a correlation peak is not something anyone can
eyeball. This renders the check that IS eyeballable: if the position is right, the real
water outlines trace the coastlines in the photograph.

Usage:
  python3 scripts/floodcheck.py candidates <sheet>          every variant, as images
  python3 scripts/floodcheck.py at <sheet> <lat_nw> <lon_nw>
  python3 scripts/floodcheck.py grid <sheet> <lat_nw> <lon_nw> [step_m] [n]
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, log, read_json

OUT = os.path.join(DERIVED, "floodmaps")
SCRATCH = os.environ.get("FLOODCHECK_OUT", "/tmp/floodcheck")
LATM = 111320.0
WIDTH = 620          # rendered width of each panel


def _np():
    import numpy as np
    return np


def _pil():
    from PIL import Image
    return Image


def sheet_photo(sheet, meta, Image, width=WIDTH):
    """The sheet's map frame, downsampled, as an RGB image."""
    im = Image.open(os.path.join(OUT, f"{sheet}.render.png")).convert("RGB")
    fx0, fy0, fx1, fy1 = meta["frame"]
    im = im.crop((fx0, fy0, fx1 + 1, fy1 + 1))
    scale = width / im.width
    return im.resize((width, max(1, int(im.height * scale))), Image.LANCZOS), scale


def water_panel(bounds, size, Image):
    """A filled raster of real water for the same bounds, for side-by-side comparison.

    Only rings above a minimum size: the point is to compare unmistakable shapes - the
    harbour, a lagoon, the sea - not 400 ditches.
    """
    from PIL import ImageDraw
    import floodreg
    w_lon, s_lat, e_lon, n_lat = bounds
    im = Image.new("RGB", size, (18, 24, 32))
    dr = ImageDraw.Draw(im)
    lonm = 111320.0 * math.cos(math.radians((s_lat + n_lat) / 2))
    sx = size[0] / ((e_lon - w_lon) * lonm)
    sy = size[1] / ((n_lat - s_lat) * LATM)
    for ring in floodreg.water_rings():
        xs = [c[0] for c in ring]
        ys = [c[1] for c in ring]
        if max(xs) < w_lon - 0.02 or min(xs) > e_lon + 0.02:
            continue
        if max(ys) < s_lat - 0.02 or min(ys) > n_lat + 0.02:
            continue
        # rough extent in metres; skip the small stuff
        if (max(xs) - min(xs)) * lonm < 120 and (max(ys) - min(ys)) * LATM < 120:
            continue
        pts = [((c[0] - w_lon) * lonm * sx, (n_lat - c[1]) * LATM * sy) for c in ring]
        if len(pts) > 2:
            dr.polygon(pts, fill=(70, 150, 220))
    return im


def draw_water(im, bounds, colour=(255, 40, 40), width_px=2):
    """Trace real water polygons over the image, given its WGS84 bounds."""
    from PIL import ImageDraw
    import floodreg
    w_lon, s_lat, e_lon, n_lat = bounds
    dr = ImageDraw.Draw(im)
    lonm = 111320.0 * math.cos(math.radians((s_lat + n_lat) / 2))
    sx = im.width / ((e_lon - w_lon) * lonm)
    sy = im.height / ((n_lat - s_lat) * LATM)
    n = 0
    for ring in floodreg.water_rings():
        pts = []
        for c in ring:
            if not (w_lon - 0.02 <= c[0] <= e_lon + 0.02
                    and s_lat - 0.02 <= c[1] <= n_lat + 0.02):
                continue
            pts.append(((c[0] - w_lon) * lonm * sx, (n_lat - c[1]) * LATM * sy))
        if len(pts) > 2:
            dr.line(pts + [pts[0]], fill=colour, width=width_px)
            n += 1
    return n


def bounds_for(meta, lat_nw, lon_nw):
    fx0, fy0, fx1, fy1 = meta["frame"]
    mpp = meta["m_per_px"]
    w_m = (fx1 - fx0 + 1) * mpp
    h_m = (fy1 - fy0 + 1) * mpp
    lat_s = lat_nw - h_m / LATM
    lonm = 111320.0 * math.cos(math.radians(lat_nw - h_m / 2 / LATM))
    return (lon_nw, lat_s, lon_nw + w_m / lonm, lat_nw), w_m, h_m


def mask_image(sheet, meta, size, Image):
    """The sheet's own big-water mask, as an image the same size as the photo panel."""
    import numpy as np
    m = mask_bigwater(sheet, meta, np, K=8, fill=0.95)
    im = Image.fromarray((m * 255).astype("uint8")).convert("RGB")
    return im.resize(size, Image.NEAREST)


def overlay_image(sheet, meta, bounds, size, Image):
    """Sheet water in red, real water in blue, agreement in white. One picture, one
    question: do the coastlines coincide?"""
    import numpy as np
    a = np.asarray(mask_image(sheet, meta, size, Image).convert("L")) > 127
    b = np.asarray(water_panel(bounds, size, Image).convert("L")) > 60
    out = np.zeros((size[1], size[0], 3), dtype="uint8")
    out[..., 0] = np.where(a, 235, 0)
    out[..., 2] = np.where(b, 235, 0)
    out[a & b] = (255, 255, 255)
    return Image.fromarray(out, "RGB")


def render_one(sheet, meta, lat_nw, lon_nw, tag, Image, mode="side"):
    im, _ = sheet_photo(sheet, meta, Image)
    b, w_m, h_m = bounds_for(meta, lat_nw, lon_nw)
    if mode == "overlay":
        im = overlay_image(sheet, meta, b, im.size, Image)
        n = 0
    elif mode == "masks":
        left = mask_image(sheet, meta, im.size, Image)
        right = water_panel(b, im.size, Image)
        combo = Image.new("RGB", (im.width * 2 + 8, im.height), (0, 0, 0))
        combo.paste(left, (0, 0))
        combo.paste(right, (im.width + 8, 0))
        n = 0
        im = combo
    elif mode == "side":
        right = water_panel(b, im.size, Image)
        combo = Image.new("RGB", (im.width * 2 + 8, im.height), (0, 0, 0))
        combo.paste(im, (0, 0))
        combo.paste(right, (im.width + 8, 0))
        n = 0
        im = combo
    else:
        n = draw_water(im, b)
    os.makedirs(SCRATCH, exist_ok=True)
    p = os.path.join(SCRATCH, f"{sheet}_{tag}.png")
    im.save(p)
    log(f"  {tag:22} NW {lat_nw:.5f},{lon_nw:.5f}  {w_m/1000:.1f}x{h_m/1000:.1f} km  "
        f"{n} water rings  -> {p}")
    return p


def mask_bigwater(sheet, meta, np, K=8, fill=0.80):
    """The sheet's real water bodies, from the band classification already on disk.

    The 2012 sheets paint depth bands over the harbour and the sea as well as over
    streets - verified here: a sample of open water comes back as exactly (154,199,224),
    the 0.2-0.5 m band colour, with zero variance. So the sea is a large solid region of
    palette colour, and a flooded street is a thin one.

    Block-averaging at K and keeping only blocks that are almost entirely painted
    therefore separates them: a 15 m cell over a harbour is 100% painted, the same cell
    over a 6 m wide flooded street is not. What survives is the coastline, which is the
    feature worth registering against.
    """
    band = np.load(os.path.join(OUT, f"{sheet}.band.npy"))
    m = (band > 0).astype(np.float32)
    h, w = m.shape
    m = m[:h // K * K, :w // K * K]
    m = m.reshape(h // K, K, w // K, K).mean(axis=(1, 3))
    return (m >= fill).astype(np.float32)


def largest_blob(m, np, keep=1):
    """Keep only the k largest connected components of a binary mask.

    On these sheets the largest painted-water component IS the sea, and the sea is the
    one feature whose shape is unambiguous. Everything else the mask picks up - basins,
    ponds, wide flooded junctions - is either small or genuinely ambiguous, and it is
    what has been pulling the correlation to wrong optima.
    """
    h, w = m.shape
    lab = np.zeros((h, w), np.int32)
    sizes, cur = {}, 0
    ys, xs = np.nonzero(m)
    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if lab[sy, sx]:
            continue
        cur += 1
        stack, n = [(sy, sx)], 0
        lab[sy, sx] = cur
        while stack:
            y, x = stack.pop()
            n += 1
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < h and 0 <= nx < w and m[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = cur
                    stack.append((ny, nx))
        sizes[cur] = n
    top = sorted(sizes, key=sizes.get, reverse=True)[:keep]
    out = np.zeros_like(m)
    for t in top:
        out[lab == t] = 1.0
    return out, [sizes[t] for t in top]


def iou_map(V, S, np):
    """IoU of S against V at every offset, computed for the whole plane at once.

    Intersection comes from an FFT cross-correlation. The union needs the sum of V under
    the window at each offset, which is an integral image. Doing it this way turns a
    283,000-position search from hours into a second, which is what makes a fine grid
    affordable and therefore what makes the answer trustworthy.
    """
    Vh, Vw = V.shape
    Sh, Sw = S.shape
    fs = (Vh, Vw)
    inter = np.fft.irfft2(np.fft.rfft2(V, fs) * np.conj(np.fft.rfft2(S, fs)), fs)
    inter = inter[:Vh - Sh + 1, :Vw - Sw + 1]

    ii = np.zeros((Vh + 1, Vw + 1))
    ii[1:, 1:] = np.cumsum(np.cumsum(V, axis=0), axis=1)
    vsum = (ii[Sh:, Sw:] - ii[:-Sh, Sw:] - ii[Sh:, :-Sw] + ii[:-Sh, :-Sw])
    vsum = vsum[:inter.shape[0], :inter.shape[1]]

    union = S.sum() + vsum - inter
    iou = np.where(union > 0, inter / np.maximum(union, 1e-9), 0.0)

    # Zero-mean normalised cross-correlation, which is the right tool and neither of the
    # two wrong ones tried first. IoU only rewards agreeing water, so it is indifferent
    # to putting open sea where the sheet shows suburbs. A plain +-1 matched filter
    # overcorrects: with a 3% water template the land term dominates and the optimum
    # becomes "point the frame at somewhere with no water at all". ZNCC removes both
    # means and both scales, so it measures the shape of the agreement rather than its
    # amount, which is what registration actually needs.
    #
    # V is binary, so sum(V^2) over a window equals sum(V), and one integral image does
    # for both moments.
    n = float(S.size)
    s_mean = float(S.mean())
    s_std = float(S.std()) or 1e-9
    v_mean = vsum / n
    v_var = np.maximum(vsum / n - v_mean * v_mean, 0.0)
    v_std = np.sqrt(v_var)
    zncc = (inter / n - s_mean * v_mean) / (s_std * np.maximum(v_std, 1e-9))

    # Precision: of the big water the SHEET paints, how much lands on real water. This
    # is the asymmetric criterion the problem actually has. The sheet may legitimately
    # omit water - it only paints inside its own catchment, so a harbour just outside
    # the boundary is absent - but wherever it does paint a large water body, that has
    # to BE a water body. IoU and ZNCC both penalise the legitimate omission.
    #
    # It has one degenerate solution: park the whole frame in open sea and precision
    # goes to 1. Ruled out by requiring the frame to be mostly land, which every one of
    # these sheets visibly is.
    prec = inter / max(float(S.sum()), 1.0)
    prec = np.where(v_mean < 0.35, prec, 0.0)
    return iou, inter, zncc, vsum, prec


def cmd_refine(sheet, meta, clat, clon, radius_m, K, np, Image, top=5):
    """Search a tight window at fine resolution, ranked by IoU rather than raw peak."""
    import floodreg
    mpp = meta["m_per_px"]
    cell = mpp * K
    S = mask_bigwater(sheet, meta, np, K=K, fill=0.95)
    keep = int(os.environ.get("FLOODCHECK_BLOBS", "0"))
    if keep:
        S, sz = largest_blob(S, np, keep=keep)
        log(f"  kept {keep} largest blob(s): {sz} cells")
    fx0, fy0, fx1, fy1 = meta["frame"]
    w_m = (fx1 - fx0 + 1) * mpp
    h_m = (fy1 - fy0 + 1) * mpp
    lonm = 111320.0 * math.cos(math.radians(clat))
    # window: the sheet's own footprint plus the search radius on every side
    win = (clon - (w_m / 2 + radius_m) / lonm, clat - (h_m / 2 + radius_m) / LATM,
           clon + (w_m / 2 + radius_m) / lonm, clat + (h_m / 2 + radius_m) / LATM)
    V = floodreg.raster(floodreg.water_rings(), cell, win, Image, np)
    log(f"  sheet mask {S.shape} ({S.mean()*100:.1f}% water)   search raster {V.shape}"
        f"   cell {cell:.1f} m")
    if S.shape[0] >= V.shape[0] or S.shape[1] >= V.shape[1]:
        log("  search window too small for the sheet")
        return []
    M_iou, inter, M_zncc, vsum, M = iou_map(V, S, np)
    flat = M.ravel()
    idx = np.argsort(flat)[::-1]
    picks, seen = [], []
    for i in idx:
        r, c = divmod(int(i), M.shape[1])
        if any(abs(r - rr) < 20 and abs(c - cc) < 20 for rr, cc in seen):
            continue
        seen.append((r, c))
        picks.append({"lat_nw": win[3] - r * cell / LATM,
                      "lon_nw": win[0] + c * cell / lonm,
                      "precision": round(float(M[r, c]), 4),
                      "zncc": round(float(M_zncc[r, c]), 4),
                      "iou": round(float(M_iou[r, c]), 4),
                      "overlap_cells": int(inter[r, c]),
                      "water_in_frame": int(vsum[r, c])})
        if len(picks) >= top:
            break
    return picks


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    np, Image = _np(), _pil()
    cmd = argv[0]
    sheets = read_json(os.path.join(OUT, "_sheets.json"))

    if cmd == "candidates":
        import floodreg
        sheet = argv[1]
        meta = sheets[sheet]
        catch = {"amager": "Amager", "bispebjerg": "Bispebjerg",
                 "kbhvest": "København Vest"}.get(sheet, sheet)
        r = floodreg.register(OUT, sheet, meta, catch, np, Image, verbose=False)
        for v in r["variants"]:
            if not v.get("ok"):
                continue
            render_one(sheet, meta, v["lat_nw"], v["lon_nw"],
                       v["variant"].replace(" ", "_").replace("%", "pc"), Image)
        return 0

    if cmd == "refine":
        sheet = argv[1]
        clat, clon = float(argv[2]), float(argv[3])
        radius = float(argv[4]) if len(argv) > 4 else 2500.0
        K = int(argv[5]) if len(argv) > 5 else 4
        picks = cmd_refine(sheet, sheets[sheet], clat, clon, radius, K, np, Image)
        for i, p in enumerate(picks):
            log(f"  #{i+1}  prec {p['precision']:.3f}  ZNCC {p['zncc']:+.3f}  IoU {p['iou']:.3f}  "
                f"overlap {p['overlap_cells']:>6,}  real water in frame "
                f"{p['water_in_frame']:>7,}  NW {p['lat_nw']:.5f},{p['lon_nw']:.5f}")
            render_one(sheet, sheets[sheet], p["lat_nw"], p["lon_nw"], f"r{i+1}", Image,
                       mode=os.environ.get("FLOODCHECK_MODE", "side"))
        return 0

    if cmd == "at":
        sheet, lat, lon = argv[1], float(argv[2]), float(argv[3])
        render_one(sheet, sheets[sheet], lat, lon, "at", Image,
                   mode=os.environ.get("FLOODCHECK_MODE", "side"))
        return 0

    if cmd == "grid":
        sheet, lat, lon = argv[1], float(argv[2]), float(argv[3])
        step = float(argv[4]) if len(argv) > 4 else 300.0
        n = int(argv[5]) if len(argv) > 5 else 1
        lonm = 111320.0 * math.cos(math.radians(lat))
        for dy in range(-n, n + 1):
            for dx in range(-n, n + 1):
                render_one(sheet, sheets[sheet], lat + dy * step / LATM,
                           lon + dx * step / lonm, f"g{dy:+d}{dx:+d}", Image)
        return 0

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
