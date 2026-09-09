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

Writes data/derived/terraincheck.json.
"""
import io
import json
import math
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, ROOT, fetch, log

WCS = "https://api.dataforsyningen.dk/dhm_wcs_DAF"
TOKEN_FILE = os.path.expanduser("~/.data-forsyningen-token")
SHEET = "indre-by"                      # one of the four that registered automatically
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


def main():
    import numpy as np
    from PIL import Image
    if not os.path.exists(TOKEN_FILE):
        log("  no Dataforsyningen token - skipping")
        return
    token = io.open(TOKEN_FILE, encoding="utf-8").read().strip()
    d = os.path.join(ROOT, "docs", "data", "flood2012")
    sx, _, _, sy, gx0, gy0 = [float(v) for v in
                              open(os.path.join(d, SHEET + ".pgw")).read().split()]
    img = Image.open(os.path.join(d, SHEET + ".png")).convert("RGBA")
    fl = np.array(img)
    Wp, Hp = img.size
    corners = [(gx0, gy0), (gx0 + Wp*sx, gy0 + Hp*sy)]
    lon = np.array([c[0] for c in corners]); lat = np.array([c[1] for c in corners])
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
        log(f"  WCS did not return a GeoTIFF: {raw[:120]!r}")
        return
    tif = os.path.join(DERIVED, "dhm_" + SHEET + ".tif")
    with open(tif, "wb") as f:
        f.write(raw)
    dem = np.array(Image.open(tif), dtype="float32")
    H, W = dem.shape
    px, py = (x1 - x0) / W, (y1 - y0) / H
    log(f"  DHM {W}x{H} at {px:.1f} m over {SHEET}")

    def anomaly(metres):
        B = max(2, int(round(metres / px)))
        hh, ww = (H // B) * B, (W // B) * B
        med = np.median(dem[:hh, :ww].reshape(hh//B, B, ww//B, B), axis=(1, 3))
        out = np.full_like(dem, np.nan)
        out[:hh, :ww] = dem[:hh, :ww] - np.kron(med, np.ones((B, B), dtype="float32"))
        return out

    def grab(col, row, arr):
        lo = gx0 + col * sx; la = gy0 + row * sy
        e, n = ll2utm(np, lo, la)
        cx = ((e - x0) / px).astype(int); cy = ((y1 - n) / py).astype(int)
        ok = (cx >= 0) & (cx < W) & (cy >= 0) & (cy < H)
        out = np.full(lo.size, np.nan, dtype="float32")
        out[ok] = arr[cy[ok], cx[ok]]
        return out

    rng = np.random.default_rng(20260909)
    alpha = fl[:, :, 3] > 0
    ys, xs = np.nonzero(alpha)
    bcol = rng.integers(0, Wp, 30000).astype(float)
    brow = rng.integers(0, Hp, 30000).astype(float)
    zb_all = grab(bcol, brow, dem)
    water_share = float(np.mean(zb_all[np.isfinite(zb_all)] <= 0.5))
    out = {
        "_what": "Modelled 2012 flooding against the national elevation model, "
                 "scored locally.",
        "_measured": {"sheet": SHEET, "dem": "dhm_terraen via Dataforsyningen WCS",
                      "grid_m": GRID_M, "flooded_pixels": int(alpha.sum())},
        "_provenance_limit": "The sheets are mutually consistent to 23 m RMS but tied "
                             "to the ground with standard errors of 58-91 m, so a "
                             "window below that size compares against terrain the "
                             "sheet may not be over.",
        "water_share_of_background": water_share,
        "windows": {},
    }
    sel = rng.choice(ys.size, size=min(8000, ys.size), replace=False)
    fcol = xs[sel].astype(float); frow = ys[sel].astype(float)
    for win in WINDOWS:
        an = anomaly(win)
        ab = grab(bcol, brow, an); af = grab(fcol, frow, an)
        zf = grab(fcol, frow, dem)
        lb = np.isfinite(ab) & (zb_all > 0.5)          # land only: drop harbour, lakes
        lf = np.isfinite(af) & (zf > 0.5)
        out["windows"][str(win)] = {
            "background_median_m": float(np.median(ab[lb])),
            "background_below_local_pct": float(100 * np.mean(ab[lb] < 0)),
            "flooded_median_m": float(np.median(af[lf])),
            "flooded_below_local_pct": float(100 * np.mean(af[lf] < 0)),
            "n_flooded": int(lf.sum()), "n_background": int(lb.sum()),
        }
        r = out["windows"][str(win)]
        log(f"  {win:>3} m window: flooded {r['flooded_median_m']:+.2f} m "
            f"({r['flooded_below_local_pct']:.0f}% below local) vs background "
            f"{r['background_median_m']:+.2f} m "
            f"({r['background_below_local_pct']:.0f}%)")
    p = os.path.join(DERIVED, "terraincheck.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    log(f"  wrote {p}")


if __name__ == "__main__":
    main()
