#!/usr/bin/env python3
"""Register a flood sheet against an already-placed one, by matching the photographs.

The four sheets that registered automatically overlap the three that did not - they are
tiles of the same aerial survey, flown in the same year - so the pixels in the overlap
genuinely depict the same ground. That makes this an image-to-image registration rather
than a feature-matching problem, and image-to-image is the thing that actually works:
no dependence on rare landmarks, no dependence on a person, and it inherits the accuracy
of the reference sheet.

Method, which is the obvious one done carefully:

  1. Resample both sheets onto one metric grid over their overlap, from their current
     georeferencing.
  2. Drop everything that is not photograph - the depth painting, the catchment outline,
     the legend - using the band classification already on disk. The painting differs
     between sheets because each paints its own catchment, so leaving it in would be
     matching the annotations rather than the ground.
  3. Locally normalise both to zero mean and unit variance in a moving window. The sheets
     were rendered at different scales and exposures; without this the correlation
     chases brightness instead of structure.
  4. Masked normalised cross-correlation over all offsets, by FFT.
  5. Report the peak, and how far it stands above the next best peak elsewhere - because
     a correlation maximum means nothing if the surface is flat, which is what sank the
     road-network attempt.

Usage:
  python3 scripts/floodalign.py <target> [reference ...]
  python3 scripts/floodalign.py bispebjerg ladegaardsaaen osterbro norrebro
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, log, read_json

OUT = os.path.join(DERIVED, "floodmaps")
# The depth legend, as printed. Anything within a few levels of these is drawn, not
# photographed.
PALETTE_RGB = [(247, 251, 255), (209, 226, 242), (154, 199, 224),
               (81, 156, 204), (28, 107, 176), (8, 48, 107)]
LATM = 111320.0
CELL_M = 4.0          # resampling resolution
SEARCH_M = float(os.environ.get("FLOODALIGN_SEARCH", 600.0))      # how far to look for the peak
NORM_WIN_M = 120.0    # moving window for local contrast normalisation


def _np():
    import numpy as np
    return np


def _pil():
    from PIL import Image
    return Image


def sheet_grid(sheet, geo, sheets, box, cell, np, Image):
    """Sample a sheet's photograph onto a metric grid, with the painting masked out."""
    b = geo[sheet]["bounds_wgs84"]
    m = sheets[sheet]
    fx0, fy0, fx1, fy1 = m["frame"]
    rgb = Image.open(os.path.join(OUT, f"{sheet}.render.png")).convert("RGB")
    rgb = rgb.crop((fx0, fy0, fx1 + 1, fy1 + 1))
    C = np.asarray(rgb).astype(np.int16)
    A = C.mean(axis=2).astype(np.float32)
    band = np.load(os.path.join(OUT, f"{sheet}.band.npy"))
    h, w = A.shape
    band = band[:h, :w]

    w_lon, s_lat, e_lon, n_lat = box
    lonm = 111320.0 * math.cos(math.radians((s_lat + n_lat) / 2))
    W = max(2, int((e_lon - w_lon) * lonm / cell))
    H = max(2, int((n_lat - s_lat) * LATM / cell))
    lons = w_lon + (np.arange(W) + 0.5) * cell / lonm
    lats = n_lat - (np.arange(H) + 0.5) * cell / LATM
    px = ((lons - b["west"]) / (b["east"] - b["west"]) * w).astype(np.int64)
    py = ((b["north"] - lats) / (b["north"] - b["south"]) * h).astype(np.int64)
    okx = (px >= 0) & (px < w)
    oky = (py >= 0) & (py < h)
    pxc = np.clip(px, 0, w - 1)
    pyc = np.clip(py, 0, h - 1)
    # Mask every drawn thing, not just the depth palette. The band array covers the
    # painted depths; it does not cover the black catchment outline or the white legend
    # box, and each sheet draws its OWN catchment - so leaving those in means correlating
    # one sheet's annotations against another's, which is a bias and not a signal.
    # The overlay is drawn in a known, small set of exact colours; the photograph
    # underneath is muted. Both tests below are deliberately generous, because throwing
    # away too much photograph costs a little correlation while letting one sheet's
    # annotations into the comparison biases the answer.
    ann = np.zeros(A.shape, bool)
    ann |= band > 0                                    # classified depth painting
    for r, g, b in PALETTE_RGB:                        # the palette, within a tolerance
        ann |= ((np.abs(C[..., 0] - r) <= 6)
                & (np.abs(C[..., 1] - g) <= 6)
                & (np.abs(C[..., 2] - b) <= 6))
    sat = C.max(axis=2) - C.min(axis=2)
    ann |= (sat > 34) & (C[..., 2] >= C[..., 0])       # saturated blues - all overlay
    ann |= A < 34                                      # the black catchment outline
    ann |= A > 244                                     # legend panel and its swatches
    # grow it, because an anti-aliased line is wider than its core
    d = ann.copy()
    d[1:, :] |= ann[:-1, :]; d[:-1, :] |= ann[1:, :]
    d[:, 1:] |= ann[:, :-1]; d[:, :-1] |= ann[:, 1:]
    ann = d

    G = A[np.ix_(pyc, pxc)]
    M = (~ann[np.ix_(pyc, pxc)]) & oky[:, None] & okx[None, :]
    return G, M.astype(np.float32)


def gradient(G, M, np):
    """Gradient magnitude, which is what survives a change of season or exposure.

    Two sheets can be flown in different years and printed at different brightness; a
    roof is a different colour in each and an edge is in the same place in both. Matching
    on structure rather than tone is the standard fix and it is what rescues the pairs
    where plain intensity correlation goes flat.
    """
    gy = np.zeros_like(G); gx = np.zeros_like(G)
    gy[1:-1, :] = G[2:, :] - G[:-2, :]
    gx[:, 1:-1] = G[:, 2:] - G[:, :-2]
    # a gradient is only meaningful where both neighbours are valid
    my = np.zeros_like(M); mx = np.zeros_like(M)
    my[1:-1, :] = M[2:, :] * M[:-2, :]
    mx[:, 1:-1] = M[:, 2:] * M[:, :-2]
    mm = my * mx * M
    return np.sqrt(gx * gx + gy * gy) * mm, mm


def local_norm(G, M, win, np):
    """Zero mean, unit variance in a moving window, over valid pixels only."""
    def boxsum(X):
        c = np.zeros((X.shape[0] + 1, X.shape[1] + 1), np.float64)
        c[1:, 1:] = np.cumsum(np.cumsum(X, 0), 1)
        k = win
        H, W = X.shape
        y0 = np.clip(np.arange(H) - k, 0, H); y1 = np.clip(np.arange(H) + k + 1, 0, H)
        x0 = np.clip(np.arange(W) - k, 0, W); x1 = np.clip(np.arange(W) + k + 1, 0, W)
        return (c[np.ix_(y1, x1)] - c[np.ix_(y0, x1)]
                - c[np.ix_(y1, x0)] + c[np.ix_(y0, x0)])
    n = boxsum(M)
    s = boxsum(G * M)
    q = boxsum(G * G * M)
    mean = s / np.maximum(n, 1)
    var = np.maximum(q / np.maximum(n, 1) - mean * mean, 0)
    out = (G - mean) / np.sqrt(np.maximum(var, 1e-6))
    out[n < 8] = 0.0
    return out * M


def masked_ncc(A, MA, B, MB, np):
    """Normalised cross-correlation of B against A over every offset, masks respected."""
    fs = (A.shape[0] + B.shape[0], A.shape[1] + B.shape[1])
    F = lambda X: np.fft.rfft2(X, fs)
    num = np.fft.irfft2(F(A) * np.conj(F(B)), fs)
    da = np.fft.irfft2(F(A * A) * np.conj(F(MB)), fs)
    db = np.fft.irfft2(F(MA) * np.conj(F(B * B)), fs)
    cnt = np.fft.irfft2(F(MA) * np.conj(F(MB)), fs)
    den = np.sqrt(np.maximum(da, 0) * np.maximum(db, 0))
    ncc = np.where((den > 1e-6) & (cnt > 0.05 * cnt.max()), num / np.maximum(den, 1e-9), 0)
    return ncc, cnt


def align(target, refs, np, Image):
    geo = read_json(os.path.join(OUT, "_georef.json"))
    sheets = read_json(os.path.join(OUT, "_sheets.json"))
    bt = geo[target]["bounds_wgs84"]
    results = []
    for ref in refs:
        br = geo[ref]["bounds_wgs84"]
        w = max(bt["west"], br["west"]); e = min(bt["east"], br["east"])
        s = max(bt["south"], br["south"]); n = min(bt["north"], br["north"])
        if e <= w or n <= s:
            continue
        lonm = 111320.0 * math.cos(math.radians((s + n) / 2))
        area = (e - w) * lonm * (n - s) * LATM / 1e6
        pad_lon = SEARCH_M / lonm
        pad_lat = SEARCH_M / LATM
        box = (w - pad_lon, s - pad_lat, e + pad_lon, n + pad_lat)

        GA, MA = sheet_grid(ref, geo, sheets, box, CELL_M, np, Image)
        GB, MB = sheet_grid(target, geo, sheets, box, CELL_M, np, Image)
        if os.environ.get("FLOODALIGN_GRAD", "1") == "1":
            GA, MA = gradient(GA, MA, np)
            GB, MB = gradient(GB, MB, np)
        k = max(1, int(NORM_WIN_M / CELL_M))
        A = local_norm(GA, MA, k, np)
        B = local_norm(GB, MB, k, np)

        ncc, cnt = masked_ncc(A, MA, B, MB, np)
        # a shift of (dy, dx) cells appears at index (dy % fs0, dx % fs1)
        R = int(SEARCH_M / CELL_M)
        best = None
        H, W = ncc.shape
        for dy in range(-R, R + 1):
            row = ncc[dy % H]
            for dx in range(-R, R + 1):
                v = row[dx % W]
                if best is None or v > best[0]:
                    best = (v, dy, dx)
        v, dy, dx = best
        # second-best outside 150 m, to test whether the peak is a peak
        rival = -9
        for dy2 in range(-R, R + 1):
            for dx2 in range(-R, R + 1):
                if abs(dy2 - dy) * CELL_M < 150 and abs(dx2 - dx) * CELL_M < 150:
                    continue
                vv = ncc[dy2 % H, dx2 % W]
                if vv > rival:
                    rival = vv
        shift_m = (dx * CELL_M, -dy * CELL_M)   # east, north
        results.append({"ref": ref, "overlap_km2": round(area, 2), "ncc": round(float(v), 4),
                        "rival": round(float(rival), 4),
                        "ratio": round(float(v / rival), 2) if rival > 0 else None,
                        "shift_east_m": shift_m[0], "shift_north_m": shift_m[1],
                        "new_west": bt["west"] + shift_m[0] / lonm,
                        "new_north": bt["north"] + shift_m[1] / LATM})
        r = results[-1]
        log(f"  vs {ref:16} overlap {area:5.2f} km²   NCC {v:+.4f}  next-best {rival:+.4f}"
            f"  ratio {r['ratio']}   shift E{shift_m[0]:+.0f} N{shift_m[1]:+.0f} m")
    return results


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    np, Image = _np(), _pil()
    if argv[0] == "bundle":
        bundle(np, Image)
        return 0
    target = argv[0]
    refs = argv[1:] or ["norrebro", "osterbro", "ladegaardsaaen", "indre-by"]
    log(f"aligning {target} against already-placed sheets "
        f"(cell {CELL_M:.0f} m, search ±{SEARCH_M:.0f} m)")
    res = align(target, refs, np, Image)
    if not res:
        log("  no overlap with any reference")
        return 1
    good = [r for r in res if r["ratio"] and r["ratio"] > 1.25]
    log("")
    if not good:
        log("  no reference gave a peak that stands clear of its surroundings — the same")
        log("  failure mode as the road-network attempt. Not accepting a shift.")
        return 0
    ew = sum(r["shift_east_m"] * r["overlap_km2"] for r in good) / sum(r["overlap_km2"] for r in good)
    nw = sum(r["shift_north_m"] * r["overlap_km2"] for r in good) / sum(r["overlap_km2"] for r in good)
    log(f"  {len(good)} reference(s) with a clear peak; area-weighted shift "
        f"E{ew:+.0f} N{nw:+.0f} m")
    spread = max(math.hypot(r["shift_east_m"] - ew, r["shift_north_m"] - nw) for r in good)
    log(f"  they disagree by at most {spread:.0f} m")
    return 0




# --------------------------------------------------------------------- bundle

SHEETS_ALL = ["amager", "bispebjerg", "indre-by", "kbhvest",
              "ladegaardsaaen", "norrebro", "osterbro"]

# Absolute anchors: sheets whose position is tied to the ground by control points a
# person reported, with the standard error of that tie. The image alignment can make
# every sheet consistent with every other, but a stack of relative shifts is only
# determined up to one global translation - these are what nail it to the Earth.
# Anisotropic on purpose. Bispebjerg's two control points sat at almost the same height
# on the sheet, so they pin its easting well and say almost nothing about its northing -
# the vertical baseline between them was 191 m on a 4.5 km sheet. Anchoring northing at
# the same strength as easting would import that weakness as if it were evidence.
ANCHORS = {"amager": (58.0, 58.0), "kbhvest": (58.0, 58.0),
           "bispebjerg": (91.0, 600.0)}


def bundle(np, Image, min_ratio=1.25):
    """Solve every sheet's position at once from all the pairwise image alignments.

    Each usable pair gives one equation, offset(target) - offset(reference) = measured
    shift, weighted by how much they overlap and how decisively the peak beat its
    rivals. The control-point anchors give the absolute equations. Least squares over
    all of it produces the one set of positions that is simultaneously self-consistent
    and tied to the ground, which no sheet-by-sheet procedure can.
    """
    geo = read_json(os.path.join(OUT, "_georef.json"))
    obs = []
    log("measuring every overlapping pair\n")
    for t in SHEETS_ALL:
        for r in SHEETS_ALL:
            if r <= t:
                continue
            res = align(t, [r], np, Image)
            if not res:
                continue
            o = res[0]
            if not o["ratio"] or o["ratio"] < min_ratio:
                log(f"    ({t} vs {r}: ratio {o['ratio']} - rejected)")
                continue
            w = o["overlap_km2"] * math.log(o["ratio"])
            obs.append((t, r, o["shift_east_m"], o["shift_north_m"], w, o))
    idx = {s: i for i, s in enumerate(SHEETS_ALL)}
    n = len(SHEETS_ALL)
    rows, be, bn, wts = [], [], [], []
    for t, r, se, sn, w, _ in obs:
        row = [0.0] * n
        row[idx[t]] = 1.0
        row[idx[r]] = -1.0
        rows.append(row); be.append(se); bn.append(sn); wts.append(w)
    we, wn = list(wts), list(wts)
    for s, (sig_e, sig_n) in ANCHORS.items():
        row = [0.0] * n
        row[idx[s]] = 1.0
        rows.append(row); be.append(0.0); bn.append(0.0)
        we.append((100.0 / sig_e) ** 2 / 100.0)
        wn.append((100.0 / sig_n) ** 2 / 100.0)
    A = np.array(rows)
    We = np.sqrt(np.array(we))[:, None]; Wn = np.sqrt(np.array(wn))[:, None]
    xe = np.linalg.lstsq(A * We, np.array(be) * We[:, 0], rcond=None)[0]
    xn = np.linalg.lstsq(A * Wn, np.array(bn) * Wn[:, 0], rcond=None)[0]

    log(f"\n{len(obs)} usable pairs + {len(ANCHORS)} anchors -> {n} positions\n")
    log(f"  {'sheet':16}{'dE m':>8}{'dN m':>8}")
    for s in SHEETS_ALL:
        log(f"  {s:16}{xe[idx[s]]:>+8.0f}{xn[idx[s]]:>+8.0f}")
    resid = []
    for (t, r, se, sn, w, _) in obs:
        de = (xe[idx[t]] - xe[idx[r]]) - se
        dn = (xn[idx[t]] - xn[idx[r]]) - sn
        resid.append(math.hypot(de, dn))
    if resid:
        log(f"\n  pair residuals: rms {math.sqrt(sum(r*r for r in resid)/len(resid)):.0f} m,"
            f" worst {max(resid):.0f} m")
    log(f"\n  how far each anchored sheet moved from its control points:")
    for s, (se_, sn_) in ANCHORS.items():
        log(f"    {s:16} E{xe[idx[s]]:+6.0f} m ({abs(xe[idx[s]])/se_:.1f} sigma)"
            f"   N{xn[idx[s]]:+6.0f} m ({abs(xn[idx[s]])/sn_:.1f} sigma)")
    unconstrained = [s for s in SHEETS_ALL
                     if s not in ANCHORS and not any(t == s or r == s for t, r, *_ in obs)]
    if unconstrained:
        log(f"\n  NOT SOLVED (no usable pair, no anchor): {', '.join(unconstrained)}")
    sol = {s: (float(xe[idx[s]]), float(xn[idx[s]])) for s in SHEETS_ALL}
    import json as _json
    _json.dump({"shifts_m": sol,
                "pair_rms_m": round(math.sqrt(sum(r*r for r in resid)/len(resid)), 1) if resid else None,
                "pairs": [{"a": t, "b": r, "dE": se, "dN": sn, "ncc": o["ncc"],
                           "ratio": o["ratio"], "overlap_km2": o["overlap_km2"]}
                          for t, r, se, sn, w, o in obs],
                "unconstrained": unconstrained},
               open(os.path.join(DERIVED, "floodalign.json"), "w"), indent=1)
    log(f"\n  wrote data/derived/floodalign.json")
    return sol, obs, resid


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
