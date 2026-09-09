"""Does the recovered 2012 flood model sit where the ground is low?

The whole "where the water wants to go" argument rests on a model nobody here has
ever checked against an independent measurement. Now one is available: the national
elevation model, fetched live from Dataforsyningen with a token, at whatever
resolution is asked for.

The test is deliberately local. Comparing a flooded pixel to the city's overall
elevation would only rediscover that Copenhagen slopes; what matters is whether
modelled water sits **below its own neighbourhood**. So each pixel is scored against
the median terrain of the block around it, at several block sizes, and the flooded
pixels are compared with a random sample of land in the same sheet.

Reading the result needs one number from the sheet's own provenance: the sheets are
mutually consistent to 23 m but tied to the ground with standard errors of **58-91 m**.
A block smaller than that is being compared against terrain the sheet may not actually
be over.

Which is why this runs on **every** sheet rather than one. They were placed two
different ways - three by ensemble water cross-correlation, four from control points a
resident read off a web map - and if the georeferencing is what hides a terrain
relationship, the tightly placed sheets should show more of one than the loose ones.
If none of them shows it, including the tightest, that points the other way: at a
flood model whose extent follows the sewer network rather than the ground.

Writes data/derived/terraincheck.json.
"""
import io
import json
import math
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, ROOT, fetch, log, read_json

WCS = "https://api.dataforsyningen.dk/dhm_wcs_DAF"
TOKEN_FILE = os.path.expanduser("~/.data-forsyningen-token")
SHEETS = None                           # all of them; a name limits it to one
GRID_M = 5
WINDOWS = (50, 100, 200)
A, F = 6378137.0, 1 / 298.257223563
E2 = F * (2 - F); EP2 = E2 / (1 - E2); K0 = 0.9996; LON0 = math.radians(9.0)


def ll2utm(np, lon, lat):
    """WGS84 to UTM 32N. Written out because this box has no projection library."""
    lat = np.radians(lat); lon = np.radians(lon)
    N = A / np.sqrt(1 - E2 * np.sin(lat) ** 2)
    T = np.tan(lat) ** 2
    C = EP2 * np.cos(lat) ** 2
    Ax = np.cos(lat) * (lon - LON0)
    M = A * ((1 - E2/4 - 3*E2**2/64 - 5*E2**3/256) * lat
             - (3*E2/8 + 3*E2**2/32 + 45*E2**3/1024) * np.sin(2*lat)
             + (15*E2**2/256 + 45*E2**3/1024) * np.sin(4*lat)
             - (35*E2**3/3072) * np.sin(6*lat))
    x = K0*N*(Ax + (1-T+C)*Ax**3/6 + (5-18*T+T*T+72*C-58*EP2)*Ax**5/120) + 500000.0
    y = K0*(M + N*np.tan(lat)*(Ax**2/2 + (5-T+9*C+4*C*C)*Ax**4/24
            + (61-58*T+T*T+600*C-330*EP2)*Ax**6/720))
    return x, y


def street_points(np, gx0, gy0, sx, sy, Wp, Hp, want=30000):
    """Background sample taken along streets, not uniformly over the sheet.

    A bare-earth model interpolates the ground *under* buildings, and buildings are
    most of a city's area - so a uniform background sample is largely made of
    invented terrain, while the modelled flooding is mostly on streets. Comparing the
    two measures the difference between streets and building footprints as much as
    anything about water. Sampling both from the street network removes that.

    Returns pixel columns and rows, or None if the road extract is not present.
    """
    path = os.path.join(RAW, "osm", "roads.json")
    if not os.path.exists(path):
        return None
    lon0, lon1 = sorted((gx0, gx0 + Wp * sx))
    lat0, lat1 = sorted((gy0, gy0 + Hp * sy))
    cols, rows = [], []
    for way in read_json(path):
        for a in range(len(way) - 1):
            x1, y1 = way[a]; x2, y2 = way[a + 1]
            if not (lon0 <= x1 <= lon1 and lat0 <= y1 <= lat1):
                continue
            for t in (0.0, 0.25, 0.5, 0.75):     # a few points per segment
                lo = x1 + (x2 - x1) * t; la = y1 + (y2 - y1) * t
                cols.append((lo - gx0) / sx)
                rows.append((la - gy0) / sy)
    if len(cols) < 500:
        return None
    c = np.array(cols); r = np.array(rows)
    keep = (c >= 0) & (c < Wp) & (r >= 0) & (r < Hp)
    c, r = c[keep], r[keep]
    if c.size > want:
        idx = np.random.default_rng(3).choice(c.size, want, replace=False)
        c, r = c[idx], r[idx]
    return c, r


def one_sheet(np, Image, sheet, token, out):
    d = os.path.join(ROOT, "docs", "data", "flood2012")
    if not os.path.exists(os.path.join(d, sheet + ".pgw")):
        return
    sx, _, _, sy, gx0, gy0 = [float(v) for v in
                              open(os.path.join(d, sheet + ".pgw")).read().split()]
    img = Image.open(os.path.join(d, sheet + ".png")).convert("RGBA")
    fl = np.array(img)
    Wp, Hp = img.size
    lon = np.array([gx0, gx0 + Wp * sx]); lat = np.array([gy0, gy0 + Hp * sy])
    ex, ny = ll2utm(np, lon, lat)
    x0, x1 = int(min(ex)), int(max(ex))
    y0, y1 = int(min(ny)), int(max(ny))
    w, h = (x1 - x0) // GRID_M, (y1 - y0) // GRID_M
    q = {"service": "WCS", "version": "1.0.0", "request": "GetCoverage",
         "coverage": "dhm_terraen", "crs": "EPSG:25832",
         "bbox": f"{x0},{y0},{x1},{y1}", "width": str(w), "height": str(h),
         "format": "GTiff", "token": token}
    raw = fetch(WCS + "?" + urllib.parse.urlencode(q), timeout=240)
    if raw[:4] not in (b"II*\x00", b"MM\x00*"):
        log(f"  {sheet}: WCS returned {raw[:80]!r}")
        return
    tif = os.path.join(DERIVED, "dhm_" + sheet + ".tif")
    with open(tif, "wb") as f:
        f.write(raw)
    dem = np.array(Image.open(tif), dtype="float32")
    H, W = dem.shape
    px, py = (x1 - x0) / W, (y1 - y0) / H

    def anomaly(metres):
        B = max(2, int(round(metres / px)))
        hh, ww = (H // B) * B, (W // B) * B
        med = np.median(dem[:hh, :ww].reshape(hh//B, B, ww//B, B), axis=(1, 3))
        a = np.full_like(dem, np.nan)
        a[:hh, :ww] = dem[:hh, :ww] - np.kron(med, np.ones((B, B), dtype="float32"))
        return a

    def grab(col, row, arr):
        lo = gx0 + col * sx; la = gy0 + row * sy
        e, n = ll2utm(np, lo, la)
        cx = ((e - x0) / px).astype(int); cy = ((y1 - n) / py).astype(int)
        ok = (cx >= 0) & (cx < W) & (cy >= 0) & (cy < H)
        v = np.full(lo.size, np.nan, dtype="float32")
        v[ok] = arr[cy[ok], cx[ok]]
        return v

    rng = np.random.default_rng(20260910)
    ys, xs = np.nonzero(fl[:, :, 3] > 0)
    if ys.size < 500:
        log(f"  {sheet}: only {ys.size} flooded pixels, skipped")
        return
    sel = rng.choice(ys.size, size=min(8000, ys.size), replace=False)
    fcol = xs[sel].astype(float); frow = ys[sel].astype(float)
    st = street_points(np, gx0, gy0, sx, sy, Wp, Hp)
    if st is None:
        bcol = rng.integers(0, Wp, 30000).astype(float)
        brow = rng.integers(0, Hp, 30000).astype(float)
        basis = "uniform"
    else:
        bcol, brow = st
        basis = "streets"
    zb = grab(bcol, brow, dem); zf = grab(fcol, frow, dem)
    rec = {"flooded_pixels": int(ys.size), "grid_m": GRID_M,
           "background": basis, "windows": {}}
    for win in WINDOWS:
        an = anomaly(win)
        ab = grab(bcol, brow, an); af = grab(fcol, frow, an)
        lb = np.isfinite(ab) & (zb > 0.5)         # land only: drop harbour and lakes
        lf = np.isfinite(af) & (zf > 0.5)
        if lf.sum() < 200 or lb.sum() < 200:
            continue
        rec["windows"][str(win)] = {
            "flooded_median_m": float(np.median(af[lf])),
            "background_median_m": float(np.median(ab[lb])),
            "flooded_below_local_pct": float(100 * np.mean(af[lf] < 0)),
            "background_below_local_pct": float(100 * np.mean(ab[lb] < 0)),
            "lift_pct_points": float(100 * (np.mean(af[lf] < 0) - np.mean(ab[lb] < 0))),
            "n_flooded": int(lf.sum()),
        }
    out[sheet] = rec
    w50 = rec["windows"].get("50")
    if w50:
        log(f"  {sheet:16} flooded {w50['flooded_median_m']:+.2f} m vs background "
            f"{w50['background_median_m']:+.2f} m   below-local "
            f"{w50['flooded_below_local_pct']:.0f}% vs "
            f"{w50['background_below_local_pct']:.0f}%   "
            f"lift {w50['lift_pct_points']:+.0f} pp")


def main():
    import numpy as np
    from PIL import Image
    if not os.path.exists(TOKEN_FILE):
        log("  no Dataforsyningen token - skipping")
        return
    token = io.open(TOKEN_FILE, encoding="utf-8").read().strip()
    d = os.path.join(ROOT, "docs", "data", "flood2012")
    sheets = SHEETS or sorted(f[:-4] for f in os.listdir(d) if f.endswith(".pgw"))
    if len(sys.argv) > 1:
        sheets = [sys.argv[1]]
    prov = {}
    pj = os.path.join(DERIVED, "viewer", "floodmaps.json")
    if os.path.exists(pj):
        prov = {k: {a: v[a] for a in ("method", "agree", "spread_m") if a in v}
                for k, v in read_json(pj).items()}
    out = {}
    for sheet in sheets:
        try:
            one_sheet(np, Image, sheet, token, out)
        except Exception as e:                    # one sheet is not the job
            log(f"  {sheet}: {type(e).__name__}: {e}")
    doc = {
        "_what": "Modelled 2012 flooding against the national elevation model, "
                 "scored against local terrain, per sheet.",
        "_measured": {"dem": "dhm_terraen via Dataforsyningen WCS", "grid_m": GRID_M},
        "_read_with": "The sheets were placed two ways and are tied to the ground "
                      "with standard errors of 58-91 m. If georeferencing is what "
                      "hides a terrain relationship, the tightly placed sheets "
                      "should show more of one.",
        "provenance": prov,
        "sheets": out,
    }
    p = os.path.join(DERIVED, "terraincheck.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    lifts = [(s, r["windows"]["50"]["lift_pct_points"]) for s, r in out.items()
             if "50" in r["windows"]]
    if lifts:
        log(f"  lift at 50 m, best to worst: " + ", ".join(
            f"{s} {v:+.0f}" for s, v in sorted(lifts, key=lambda x: -x[1])))
    log(f"  wrote {p}")


if __name__ == "__main__":
    main()
