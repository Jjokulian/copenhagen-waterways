#!/usr/bin/env python3
"""Which seabed each light station sits on, and whether the bed shows in the water.

Near-bed turbidity is a property of what the bed is made of. A muddy bed holds
fine material that lifts at low shear and stays up; a sand bed with current over
it has little to give; gravel, till and rock have essentially nothing. So the
casts whose lower half attenuates MORE than their upper half - about a quarter of
them, the ones running against the spectral trend in LIGHT.md - should not be
scattered at random. They should sit on mud.

That is a falsifiable prediction about data already collected, and this tests it.

The substrate map is GEUS's Havbundssedimentkort, distributed as a GeoPackage,
which is SQLite - so it opens with the standard library and no GIS stack. Its
geometry is GeoPackage Binary: a short header, then ordinary WKB, parsed here
with struct. Point-in-polygon is ray casting with holes subtracted.

Two things about the map that bound every conclusion:

  * It is a **compilation of surveys at different scales**, from 1:5,000 to
    1:500,000, recorded per polygon in `scale`. A class assigned at 1:500,000 is
    a much weaker assertion about a specific station than one at 1:5,000, and the
    map does not become more precise by being drawn as a hard line.
  * The surveys behind it were mostly commissioned to find aggregate or to map
    habitat, not to characterise the whole seabed evenly. Where it is detailed
    reflects where somebody wanted something.

Reads   data/raw/geus/seabed_sediment_dk.gpkg, data/raw/oda/lys.csv.gz
Writes  data/derived/substrate.json

Usage:  ~/.venvs/marine/bin/python scripts/substrate.py
"""
import collections
import csv
import gzip
import math
import os
import sqlite3
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, log, write_json

GPKG = os.path.join(RAW, "geus", "seabed_sediment_dk.gpkg")


def num(x):
    x = (x or "").strip().replace(",", ".")
    try:
        return float(x)
    except ValueError:
        return None


def rings_of(blob):
    """GeoPackage Binary -> list of rings, each a list of (x, y). Holes included,
    flagged by position: ring 0 of each polygon is the shell, the rest are holes."""
    if blob[:2] != b"GP":
        return []
    flags = blob[3]
    env = (flags >> 1) & 0x07
    skip = {0: 0, 1: 32, 2: 48, 3: 48, 4: 64}.get(env, 0)
    p = 8 + skip
    out = []

    def dims_of(typ):
        """ISO WKB encodes the coordinate count in the type: +1000 Z, +2000 M,
        +3000 ZM. This map is 3006 - MultiPolygon ZM - so every point carries
        FOUR doubles, not two. Reading it as two silently yields nothing."""
        return {0: 2, 1: 3, 2: 3, 3: 4}[typ // 1000]

    def read_polygon(p, nd):
        (nring,) = struct.unpack_from("<I", blob, p)
        p += 4
        polys = []
        for _ in range(nring):
            (npt,) = struct.unpack_from("<I", blob, p)
            p += 4
            raw = struct.unpack_from("<%dd" % (nd * npt), blob, p)
            p += 8 * nd * npt
            pts = []
            for k in range(npt):
                pts.append(raw[k * nd])
                pts.append(raw[k * nd + 1])
            polys.append(pts)
        return polys, p

    order, typ = struct.unpack_from("<BI", blob, p)
    p += 5
    nd = dims_of(typ)
    if typ % 1000 == 3:
        polys, p = read_polygon(p, nd)
        out.append(polys)
    elif typ % 1000 == 6:
        (npoly,) = struct.unpack_from("<I", blob, p)
        p += 4
        for _ in range(npoly):
            _o, t2 = struct.unpack_from("<BI", blob, p)
            p += 5
            polys, p = read_polygon(p, dims_of(t2))
            out.append(polys)
    return out


def inside(pts, x, y):
    """Ray casting on a flat coordinate list [x0,y0,x1,y1,...]."""
    n = len(pts) // 2
    c = False
    j = n - 1
    for i in range(n):
        xi, yi = pts[2 * i], pts[2 * i + 1]
        xj, yj = pts[2 * j], pts[2 * j + 1]
        if (yi > y) != (yj > y):
            if x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                c = not c
        j = i
    return c


def bbox(pts):
    xs = pts[0::2]
    ys = pts[1::2]
    return min(xs), min(ys), max(xs), max(ys)


def load_polygons():
    c = sqlite3.connect(GPKG)
    out = []
    for fid, cls, scale, blob in c.execute(
            'select fid, sedimenten, scale, Shape from Seabed_sedimen'):
        for polys in rings_of(blob):
            shell = polys[0]
            out.append({"fid": fid, "cls": cls, "scale": scale,
                        "shell": shell, "bb": bbox(shell),
                        "holes": [(h, bbox(h)) for h in polys[1:]]})
    c.close()
    return out


def classify(parts, x, y):
    """Finest-scale polygon wins where they overlap: a 1:5,000 survey beats a
    1:500,000 compilation over the same water, which is the whole point of
    recording the scale."""
    best = None
    for p in parts:
        x0, y0, x1, y1 = p["bb"]
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            continue
        if not inside(p["shell"], x, y):
            continue
        if any(hx0 <= x <= hx1 and hy0 <= y <= hy1 and inside(h, x, y)
               for h, (hx0, hy0, hx1, hy1) in p["holes"]):
            continue
        if best is None or p["scale"] < best["scale"]:
            best = p
    return best


def read_station_geometry():
    """Per station: UTM32 position, and the share of its casts whose lower half
    attenuates more than its upper half."""
    p = os.path.join(RAW, "oda", "lys.csv.gz")
    pos, cur, buf, casts = {}, None, [], collections.defaultdict(list)

    def slope(zs, ls):
        n = len(zs)
        zm, lm = sum(zs) / n, sum(ls) / n
        den = sum((z - zm) ** 2 for z in zs)
        return None if den <= 0 else sum((z - zm) * (l - lm)
                                         for z, l in zip(zs, ls)) / den

    def flush():
        nonlocal buf
        if cur is not None and len(buf) >= 8:
            buf.sort()
            zs = [b[0] for b in buf]
            ls = [b[1] for b in buf]
            if zs[-1] - zs[0] >= 2.0:
                mid = len(zs) // 2
                su, sl = slope(zs[:mid + 1], ls[:mid + 1]), slope(zs[mid:], ls[mid:])
                if su is not None and sl is not None and su < 0 and sl < 0:
                    casts[cur[0]].append((-sl / -su, zs[0], zs[-1]))
        buf = []

    with gzip.open(p, "rt", encoding="iso-8859-1") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            key = (row["ObservationsStedNr"], (row.get("Dato") or "").strip(),
                   row.get("UndersøgelseNr") or "")
            if key != cur:
                flush()
                cur = key
            st = row["ObservationsStedNr"]
            if st not in pos:
                x, y = num(row.get("X_UTM32")), num(row.get("Y_UTM32"))
                if x and y:
                    pos[st] = (x, y, (row.get("ObservationsStedNavn") or "").strip())
            z, pct = num(row.get("Dybde (m)")), num(row.get("Lysprocent"))
            if z is not None and pct is not None and pct > 0:
                buf.append((z, math.log(pct)))
    flush()
    return pos, casts


def main():
    parts = load_polygons()
    log(f"  {len(parts):,} polygon parts, "
        f"{len({p['cls'] for p in parts})} substrate classes")
    pos, casts = read_station_geometry()
    log(f"  {len(pos):,} stations with UTM position, "
        f"{sum(len(v) for v in casts.values()):,} refitted casts")

    rows, unplaced = [], 0
    for st, (x, y, name) in pos.items():
        cs = casts.get(st) or []
        if len(cs) < 10:
            continue
        hit = classify(parts, x, y)
        if hit is None:
            unplaced += 1
            continue
        rs = [c[0] for c in cs]
        rows.append({"station": st, "name": name, "cls": hit["cls"],
                     "scale": hit["scale"], "n_casts": len(rs),
                     "steepens_pct": round(100 * sum(1 for r in rs if r > 1) / len(rs), 1),
                     "median_ratio": round(sorted(rs)[len(rs) // 2], 3),
                     "median_start": round(sorted(c[1] for c in cs)[len(cs) // 2], 2)})
    log(f"  {len(rows):,} stations placed on the map, {unplaced} outside it")

    by = collections.defaultdict(list)
    for r in rows:
        by[r["cls"]].append(r)
    summary = []
    for cls, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
        st = sorted(r["steepens_pct"] for r in rs)
        summary.append({
            "cls": cls, "n_stations": len(rs),
            "n_casts": sum(r["n_casts"] for r in rs),
            "median_steepens_pct": round(st[len(st) // 2], 1),
            "median_ratio": round(sorted(r["median_ratio"] for r in rs)[len(rs) // 2], 3),
            "median_start_depth": round(
                sorted(r["median_start"] for r in rs)[len(rs) // 2], 2),
        })
    write_json(os.path.join(DERIVED, "substrate.json"),
               {"_what": "Each light station placed on the GEUS seabed substrate "
                         "map, with the share of its casts whose lower half "
                         "attenuates more than its upper half.",
                "_limits": "The map is a compilation at scales from 1:5,000 to "
                           "1:500,000; the finest-scale polygon wins where they "
                           "overlap. Surveys were commissioned for aggregate and "
                           "habitat, so detail follows past commercial interest.",
                "by_class": summary, "stations": rows})
    print(f"\n{'substrate':28} {'stations':>9} {'casts':>8} {'steepens':>9} "
          f"{'ratio':>7} {'start m':>8}")
    for s in summary:
        print(f"  {s['cls'][:26]:26} {s['n_stations']:9,} {s['n_casts']:8,} "
              f"{s['median_steepens_pct']:8.1f}% {s['median_ratio']:7.3f} "
              f"{s['median_start_depth']:8.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
