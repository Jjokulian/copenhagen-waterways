#!/usr/bin/env python3
"""Locate a flood sheet on the map by matching its water against the city's water.

Why this is not one clean algorithm
-----------------------------------
The seven sheets do not share one orthophoto. Their exposures differ enough that no
single water detector works on all of them: Bispebjerg's darkest pixel is luminance 53
where kbhvest's is 4, and Bispebjerg's lakes render near-black with no blue cast at all
while Indre By's harbour is distinctly blue. A detector tuned on Indre By finds 10.7% of
that sheet as water and 0.1% of Bispebjerg; a percentile-based one that finds Bispebjerg's
lakes moves Indre By 500 m off.

So instead of trusting one detector, run six independent ones and see whether they land
in the same place. Agreement between methods that fail differently is real evidence;
a single confident-looking answer is not. Sheets where the variants disagree are reported
as unresolved rather than guessed, and go to viz/georef.html for hand-placed points.

Two other things that had to be handled:
  * The flood bands are painted in blue and are the largest blue thing on the sheet.
    Left in, they swamp the water signal - on Bispebjerg they cover 18.8% of the frame.
    They are masked out using the classification from `floodmaps.py extract`.
  * Searching all of Copenhagen locks onto the wrong water; Bispebjerg landed at latitude
    55.61, south of the city. Each sheet names its catchment in its own title, so the
    search is limited to a window around that catchment.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RAW, log, read_json

LATM = 111320.0
LONM = 111320.0 * math.cos(math.radians(55.66))
NEIGHBOURS = ((-1, 0), (1, 0), (0, -1), (0, 1))

# How far a sheet's centre may sit from its catchment's centroid.
CENTRE_TOLERANCE_M = 2500.0
# Two variants count as agreeing if their answers are within this distance.
AGREE_TOLERANCE_M = 90.0


def _erode(x, np):
    o = x.copy()
    for dy, dx in NEIGHBOURS:
        o &= np.roll(np.roll(x, dy, 0), dx, 1)
    return o


def _dilate(x, np):
    o = x.copy()
    for dy, dx in NEIGHBOURS:
        o |= np.roll(np.roll(x, dy, 0), dx, 1)
    return o


def _open_close(m, np):
    """Drop specks (boats, wet roofs), then fill small holes."""
    return _erode(_dilate(_dilate(_erode(m, np), np), np), np)


def blockmean(a, k, np):
    h, w = a.shape[0] // k * k, a.shape[1] // k * k
    a = a[:h, :w]
    if a.ndim == 3:
        return a.reshape(h // k, k, w // k, k, a.shape[2]).mean((1, 3))
    return a.reshape(h // k, k, w // k, k).mean((1, 3))


def _sheet_arrays(outdir, sheet, meta, K, np, Image):
    """Block-averaged sheet colours, plus the fraction of each cell free of flood paint."""
    a = np.asarray(Image.open(os.path.join(outdir, f"{sheet}.render.png")).convert("RGB"))
    fx0, fy0, fx1, fy1 = meta["frame"]
    crop = a[fy0:fy1 + 1, fx0:fx1 + 1].astype(np.float32)

    band = np.load(os.path.join(outdir, f"{sheet}.band.npy"))
    band = band[:crop.shape[0], :crop.shape[1]]
    painted = band > 0
    grown = painted.copy()
    for s in (1, 2, 3):     # JPEG smears the paint into neighbouring pixels
        grown[s:, :] |= painted[:-s, :]
        grown[:-s, :] |= painted[s:, :]
        grown[:, s:] |= painted[:, :-s]
        grown[:, :-s] |= painted[:, s:]
    return blockmean(crop, K, np), blockmean((~grown).astype(np.float32), K, np)


def mask_blue(outdir, sheet, meta, np, Image, K=16, gr=9, br=9, lum=70):
    """Water as it looks on the darker sheets: green- and blue-dominant, and dark."""
    sm, clean = _sheet_arrays(outdir, sheet, meta, K, np, Image)
    r, g, b = sm[:, :, 0], sm[:, :, 1], sm[:, :, 2]
    m = (g - r > gr) & (b - r > br) & (sm.mean(axis=2) < lum) & (clean >= 0.7)
    return _open_close(m, np)


def mask_adaptive(outdir, sheet, meta, np, Image, K=16, pct=8, stdp=65):
    """Water as the darkest, smoothest, bluest cells of THIS sheet, by percentile.

    Exposure-independent, which is what the brighter sheets need.
    """
    sm, clean = _sheet_arrays(outdir, sheet, meta, K, np, Image)
    r, b = sm[:, :, 0], sm[:, :, 2]
    lum = sm.mean(axis=2)
    h, w = lum.shape
    pad = np.pad(lum, 2, mode="edge")
    s1 = np.zeros((h, w), np.float32)
    s2 = np.zeros((h, w), np.float32)
    for dy in range(5):
        for dx in range(5):
            v = pad[dy:dy + h, dx:dx + w]
            s1 += v
            s2 += v * v
    std = np.sqrt(np.maximum(s2 / 25.0 - (s1 / 25.0) ** 2, 0))

    def z(x):
        return (x - x.mean()) / (x.std() or 1)

    score = z(-lum) + z(b - r)
    score[clean < 0.7] = -1e6
    score[std > np.percentile(std, stdp)] = -1e6
    usable = score > -1e5
    if usable.sum() < 40:
        return np.zeros_like(lum, dtype=bool)
    return _open_close(score >= np.percentile(score[usable], 100 - pct), np)


VARIANTS = [
    ("blue K16",       16, lambda o, s, m, np, I: mask_blue(o, s, m, np, I, K=16)),
    ("blue K8",         8, lambda o, s, m, np, I: mask_blue(o, s, m, np, I, K=8)),
    ("blue loose K16", 16, lambda o, s, m, np, I: mask_blue(o, s, m, np, I, K=16,
                                                            gr=5, br=5, lum=95)),
    ("adapt 6% K16",   16, lambda o, s, m, np, I: mask_adaptive(o, s, m, np, I, K=16, pct=6)),
    ("adapt 12% K16",  16, lambda o, s, m, np, I: mask_adaptive(o, s, m, np, I, K=16,
                                                                pct=12, stdp=75)),
    ("adapt 8% K8",     8, lambda o, s, m, np, I: mask_adaptive(o, s, m, np, I, K=8, pct=8)),
]


# ---------------------------------------------------------------- reference water
_RINGS = None


def water_rings():
    """Water polygons from the city layer, plus OSM water if it has been fetched.

    OSM adds the canals and small lakes the municipal overview map generalises away,
    which matters on the inland sheets where there is little else to match.
    """
    global _RINGS
    if _RINGS is not None:
        return _RINGS
    rings = []
    d = read_json(os.path.join(RAW, "vand_oversigtskort.geojson"))
    for f in d["features"]:
        g = f.get("geometry")
        if not g:
            continue
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for poly in polys:
            if poly and len(poly[0]) > 3:
                rings.append(poly[0])
    osm = os.path.join(RAW, "osm", "landcover.json")
    if os.path.exists(osm):
        for f in read_json(osm):
            if f.get("kind") == "water" and len(f.get("ring") or []) > 3:
                rings.append(f["ring"])
    _RINGS = rings
    return rings


def raster(rings, cell, bounds, Image, np):
    from PIL import ImageDraw
    w0, s0, e0, n0 = bounds
    W = max(4, int((e0 - w0) * LONM / cell))
    H = max(4, int((n0 - s0) * LATM / cell))
    im = Image.new("1", (W, H), 0)
    dr = ImageDraw.Draw(im)
    for ring in rings:
        pts = [((lo - w0) * LONM / cell, (n0 - la) * LATM / cell) for lo, la in ring]
        if all(x < -20 or x > W + 20 or y < -20 or y > H + 20 for x, y in pts):
            continue
        dr.polygon(pts, fill=1)
    return np.asarray(im)


def correlate(V, S, np):
    H, W = V.shape
    h, w = S.shape
    fh = 1 << int(np.ceil(np.log2(H + h)))
    fw = 1 << int(np.ceil(np.log2(W + w)))
    A = V.astype(np.float32) - V.mean()
    B = S.astype(np.float32) - S.mean()
    C = np.fft.irfft2(np.fft.rfft2(A, (fh, fw)) * np.fft.rfft2(B[::-1, ::-1], (fh, fw)),
                      (fh, fw))
    return C[h - 1:H, w - 1:W]


def iou(V, S, r, c, np):
    H, W = V.shape
    h, w = S.shape
    if r < 0 or c < 0 or r + h > H or c + w > W:
        return 0.0
    v = V[r:r + h, c:c + w]
    u = (v | S).sum()
    return float((v & S).sum() / u) if u else 0.0


def catchment_centroid(name):
    d = read_json(os.path.join(RAW, "skp_skybrudsoplande.geojson"))
    f = next((x for x in d["features"]
              if x["properties"].get("opland_kort_navn") == name), None)
    if not f:
        return None
    xs, ys = [], []

    def walk(c):
        if isinstance(c, list) and c and isinstance(c[0], (int, float)):
            xs.append(c[0])
            ys.append(c[1])
        elif isinstance(c, list):
            for sub in c:
                walk(sub)
    walk(f["geometry"]["coordinates"])
    return sum(xs) / len(xs), sum(ys) / len(ys)


def register(outdir, sheet, meta, catchment, np, Image, verbose=True):
    """Run every variant, then report where they agree."""
    centre = catchment_centroid(catchment)
    if not centre:
        return None
    clon, clat = centre
    fx0, fy0, fx1, fy1 = meta["frame"]
    mpp = meta["m_per_px"]
    fw = (fx1 - fx0 + 1) * mpp
    fh = (fy1 - fy0 + 1) * mpp
    R = CENTRE_TOLERANCE_M
    win = (clon - (fw / 2 + R) / LONM, clat - (fh / 2 + R) / LATM,
           clon + (fw / 2 + R) / LONM, clat + (fh / 2 + R) / LATM)

    rings = water_rings()
    results = []
    for name, K, fn in VARIANTS:
        S = fn(outdir, sheet, meta, np, Image)
        if S.mean() < 0.002:
            results.append({"variant": name, "ok": False, "reason": "no usable water mask"})
            continue
        cell = mpp * K
        V = raster(rings, cell, win, Image, np)
        if S.shape[0] >= V.shape[0] or S.shape[1] >= V.shape[1]:
            results.append({"variant": name, "ok": False, "reason": "sheet exceeds window"})
            continue
        C = correlate(V, S, np)
        r, c = np.unravel_index(int(np.argmax(C)), C.shape)
        results.append({
            "variant": name, "ok": True,
            "lon_nw": win[0] + c * cell / LONM,
            "lat_nw": win[3] - r * cell / LATM,
            "z": round(float((C[r, c] - C.mean()) / (C.std() or 1)), 2),
            "iou": round(iou(V, S, int(r), int(c), np), 3),
            "water_fraction": round(float(S.mean()), 4),
        })
        if verbose:
            g = results[-1]
            log(f"      {name:16} {g['lat_nw']:.5f},{g['lon_nw']:.5f}  "
                f"z={g['z']:5.2f}  IoU={g['iou']:.3f}")

    usable = [r for r in results if r.get("ok")]
    if not usable:
        return {"resolved": False, "variants": results, "reason": "no variant produced a mask"}

    # largest cluster of mutually-agreeing answers
    best = []
    for a in usable:
        grp = [b for b in usable
               if math.hypot((b["lon_nw"] - a["lon_nw"]) * LONM,
                             (b["lat_nw"] - a["lat_nw"]) * LATM) <= AGREE_TOLERANCE_M]
        if len(grp) > len(best):
            best = grp
    lon = sum(g["lon_nw"] for g in best) / len(best)
    lat = sum(g["lat_nw"] for g in best) / len(best)
    spread = max((math.hypot((g["lon_nw"] - lon) * LONM, (g["lat_nw"] - lat) * LATM)
                  for g in best), default=0.0)
    return {
        "resolved": True,
        "lon_nw": lon, "lat_nw": lat,
        "agree": len(best), "variants_run": len(usable),
        "spread_m": round(spread, 1),
        "best_iou": max(g["iou"] for g in best),
        "variants": results,
    }
