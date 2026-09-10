#!/usr/bin/env python3
"""Rotate the flood sheets by the meridian convergence they were placed without.

floodmaps.py says, at the point where it decides two control points are enough:
"No rotation: every sheet has north up (the north arrow confirms it)". The north
arrow on a Danish municipal sheet is GRID north - the sheets are drawn in ETRS89
/ UTM zone 32N, whose central meridian is 9 degrees east. Copenhagen is about
3.6 degrees east of it, and grid north there bears 2.90 to 2.98 degrees clockwise
of true north depending on the sheet.

The sheets were placed true-north-up. Over a half-diagonal of 1.8 to 6.9 km that
mislocates the corners by 94 to 350 m, against quoted registration errors of 14
to 91 m. **The unmodelled rotation is 2.4 to 7.5 times the error the pipeline
reports for itself** (per sheet: data/derived/convergence.json). An earlier
version of this docstring said four to ten times, worked out loosely by hand;
the first stored figures contradicted it - which is what a residual looks like when the model cannot
represent the transform: the fit absorbs the rotation into a wrong scale and a
wrong offset, and then reports the leftovers as its accuracy.

Verified empirically rather than from a sign convention: walking 2 km along a
line of constant UTM easting - grid north by definition - drifts 102.9 m east,
so grid north bears +2.97 degrees. The sheet content must therefore be rotated
CLOCKWISE by that angle to sit on a true-north map.

The world files are WGS84 geographic, so this is not a rotation in the space the
file is written in: a degree of longitude is cos(latitude) shorter than a degree
of latitude. The rotation is composed on the ground in metres and then converted
back, which is why the four coefficients below are not a rotation matrix.

    python3 scripts/convergence.py --dry-run
    python3 scripts/convergence.py            # rewrites docs/data/flood2012/*.pgw

Then rerun scripts/terraincheck.py: it scores whether modelled flooding sits
below local ground more often than the streets do, and it never saw this
rotation, so it is an independent test rather than a restatement.

RESULT, AND WHY THIS IS NOT APPLIED. Run on 2026-09-10 against all seven sheets,
the terrain check's mean lift moved from -17.0 to -16.3 percentage points - +0.6,
inside the +-4 scatter between sheets; three improved, two got worse, Noerrebro
did not move. The world files were restored. The rotation is geometrically real
and this script computes it correctly, but applied on top of a fit that had no
rotation term it inherits the scale and offset that fit used to absorb it. The
correct use is as a KNOWN CONSTANT inside a fresh orthophoto-to-orthophoto
registration - the sheets carry an aerial photograph underneath the flood paint,
which the water-polygon correlation threw away - not as a patch on the old one.
"""
import glob
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT, log

DEST = os.path.join(ROOT, "docs", "data", "flood2012")
CENTRAL_MERIDIAN = 9.0
M_PER_DEG_LAT = 110574.0
M_PER_DEG_LON = 111320.0


def convergence_deg(lon, lat):
    """Angle from true north to grid north, positive clockwise."""
    return math.degrees(math.atan(math.tan(math.radians(lon - CENTRAL_MERIDIAN))
                                  * math.sin(math.radians(lat))))


def read_pgw(path):
    with open(path) as f:
        v = [float(x.strip()) for x in f if x.strip()]
    return v            # A, D, B, E, C, F


def rotate(path, width, height, dry):
    A, D, B, E, C, F = read_pgw(path)
    if abs(D) > 1e-12 or abs(B) > 1e-12:
        log(f"  {os.path.basename(path):<20} already carries a rotation - skipped")
        return None
    # sheet centre, so the rotation pivots there and the placement does not walk
    cx, cy = (width - 1) / 2.0, (height - 1) / 2.0
    lon_c = A * cx + C
    lat_c = E * cy + F
    gamma = convergence_deg(lon_c, lat_c)
    th = math.radians(gamma)
    mlon = M_PER_DEG_LON * math.cos(math.radians(lat_c))

    sx = A * mlon                 # ground metres per pixel, east
    sy = -E * M_PER_DEG_LAT       # ground metres per pixel, north (E is negative)

    # clockwise on the ground: X' = X cos + Y sin ; Y' = -X sin + Y cos
    A2 = (sx * math.cos(th)) / mlon
    B2 = (-sy * math.sin(th)) / mlon
    D2 = (-sx * math.sin(th)) / M_PER_DEG_LAT
    E2 = (-sy * math.cos(th)) / M_PER_DEG_LAT
    # hold the centre fixed
    C2 = lon_c - (A2 * cx + B2 * cy)
    F2 = lat_c - (D2 * cx + E2 * cy)

    shift = math.hypot(cx * sx, cy * sy) * abs(th)
    log(f"  {os.path.basename(path)[:-4]:<16} centre {lon_c:8.4f},{lat_c:7.4f}  "
        f"gamma {gamma:+.3f}deg  corner moves {shift:5.0f} m")
    if not dry:
        with open(path, "w") as f:
            for v in (A2, D2, B2, E2, C2, F2):
                f.write(f"{v:.12f}\n")
    return {"sheet": os.path.basename(path)[:-4], "gamma_deg": round(gamma, 3),
            "corner_shift_m": round(shift, 1)}


def main(argv):
    dry = "--dry-run" in argv
    from PIL import Image
    n, res = 0, []
    for p in sorted(glob.glob(os.path.join(DEST, "*.pgw"))):
        png = p[:-4] + ".png"
        if not os.path.exists(png):
            continue
        with Image.open(png) as im:
            w, h = im.size
        r = rotate(p, w, h, dry)
        if r is not None:
            n += 1
            res.append(r)
    _record(res)
    log(f"\n{'would rotate' if dry else 'rotated'} {n} world file(s)")
    if not dry:
        log("now run scripts/terraincheck.py - it is the independent test")
    return 0


def _record(res):
    """The figures CLAIMS.md quotes about the unmodelled rotation, written down so
    they are data and not a remembered printout: per sheet the convergence and the
    corner displacement it causes, against the registration error the pipeline
    reports for itself."""
    import json
    geo = os.path.join(ROOT, "data", "derived", "floodmaps", "_georef.json")
    g = json.load(open(geo, encoding="utf-8")) if os.path.exists(geo) else {}
    for r in res:
        rec = g.get(r["sheet"], {})
        err = rec.get("standard_error_m") or rec.get("spread_m")
        r["stated_error_m"] = err
        r["shift_over_error"] = round(r["corner_shift_m"] / err, 1) if err else None
    ratios = [r["shift_over_error"] for r in res if r["shift_over_error"]]
    out = {
        "_what": "Meridian convergence per flood sheet and the corner displacement it "
                 "causes when a grid-north sheet is placed true-north-up.",
        "sheets": res,
        "n_sheets": len(res),
        "gamma_min_deg": min(r["gamma_deg"] for r in res),
        "gamma_max_deg": max(r["gamma_deg"] for r in res),
        "shift_min_m": min(r["corner_shift_m"] for r in res),
        "shift_max_m": max(r["corner_shift_m"] for r in res),
        "stated_error_min_m": min(r["stated_error_m"] for r in res if r["stated_error_m"]),
        "stated_error_max_m": max(r["stated_error_m"] for r in res if r["stated_error_m"]),
        "shift_over_error_min": min(ratios),
        "shift_over_error_max": max(ratios),
    }
    p = os.path.join(ROOT, "data", "derived", "convergence.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    log(f"wrote {os.path.relpath(p, ROOT)}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
