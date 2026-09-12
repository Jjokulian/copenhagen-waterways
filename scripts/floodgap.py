#!/usr/bin/env python3
"""Compare where the 2012 model says Copenhagen floods against what was planned there.

The city modelled a 100-year cloudburst in 2012 and published the result as pictures.
It then wrote a cloudburst plan full of basins, retention squares and tunnels. Because
the model was never released as data, the obvious question was awkward to ask:

    does the plan put infrastructure where the model says the water goes?

`floodmaps.py autoref` georeferences the sheets, which makes the question answerable.
This script answers it for every sheet that registered confidently.

Method: rasterise everything onto one 10 m grid, take a distance transform out from the
planned works, and read off how far each flooded cell is from the nearest intervention.
Also crosses the flooding with sewer type, because flooding over a combined sewer is not
the same event as flooding over a separate one - there the water is mixed with sewage.

Usage:  python3 scripts/floodgap.py
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, read_json, write_doc, write_json
import live

CELL = 10.0                     # metres
LATM = 111320.0
LONM = 111320.0 * math.cos(math.radians(55.68))
FLOOD_DEPTH_MIN = 2             # band index 2 = 0.1 m; band 1 (0.05-0.1) is a wet film
NEAR_M = (50, 100, 200)
HOTSPOT_MIN_CELLS = 40          # 4000 m2, i.e. bigger than a road junction
HOTSPOT_MIN_BAND = 3            # band index 3 = 0.2 m and deeper
HOTSPOT_MIN_DISTANCE_M = 100    # further than this from any planned work
OUT = os.path.join(DERIVED, "floodgap.json")

BANDS = [None, "0.05-0.1", "0.1-0.2", "0.2-0.5", "0.5-1", "1-2", ">2"]
BAND_MID = [0, 0.075, 0.15, 0.35, 0.75, 1.5, 2.5]   # for a volume estimate

# What counts as a cloudburst intervention, and whether it is built or only planned.
WORKS = [
    ("skp_bassiner_pladser_kk", "basin or retention square", "planned"),
    ("skp_veje_tunneller_kk", "cloudburst road, pipe or tunnel", "planned"),
    ("skp_terraenaend", "terrain modification", "planned"),
    ("skp_igangsatte_prj_kk", "project in progress", "in_progress"),
    ("skp_afsluttede_prj_kk", "project completed", "completed"),
]


def _np():
    import numpy as np
    return np


def _pil():
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    return Image


class Grid:
    """A metric raster over a WGS84 bounding box, north-up."""

    def __init__(self, west, south, east, north, cell=CELL):
        self.west, self.south, self.east, self.north = west, south, east, north
        self.cell = cell
        self.W = max(1, int((east - west) * LONM / cell))
        self.H = max(1, int((north - south) * LATM / cell))

    def xy(self, lon, lat):
        return ((lon - self.west) * LONM / self.cell,
                (self.north - lat) * LATM / self.cell)

    def lonlat(self, x, y):
        return (self.west + x * self.cell / LONM,
                self.north - y * self.cell / LATM)


def rasterise(grid, geoms, Image, np, width=3):
    """Burn polygons and lines onto the grid."""
    from PIL import ImageDraw
    im = Image.new("1", (grid.W, grid.H), 0)
    dr = ImageDraw.Draw(im)
    for kind, coords in geoms:
        pts = [grid.xy(lo, la) for lo, la in coords]
        if all(x < -20 or x > grid.W + 20 or y < -20 or y > grid.H + 20 for x, y in pts):
            continue
        if kind == "poly" and len(pts) > 2:
            dr.polygon(pts, fill=1)
        elif len(pts) > 1:
            dr.line(pts, fill=1, width=width)
    return np.asarray(im).copy()


def iter_geoms(path):
    """Yield ('poly'|'line', ring) for every part of every feature in a GeoJSON."""
    if not os.path.exists(path):
        return
    for f in read_json(path)["features"]:
        g = f.get("geometry")
        if not g:
            continue
        t, c = g["type"], g["coordinates"]
        if t == "Polygon":
            yield "poly", c[0]
        elif t == "MultiPolygon":
            for poly in c:
                yield "poly", poly[0]
        elif t == "LineString":
            yield "line", c
        elif t == "MultiLineString":
            for ln in c:
                yield "line", ln
        elif t == "Point":
            yield "line", [c, c]
        elif t == "MultiPoint":
            for p in c:
                yield "line", [p, p]


def distance_transform(seed, np, cell=CELL):
    """Two-pass chamfer distance in metres from the seed cells.

    scipy is not available on this machine; the 3x3 chamfer with weights (1, sqrt2) is
    accurate to about 4% for Euclidean distance, which is far finer than anything else
    in this comparison.
    """
    INF = 1e9
    d = np.where(seed, 0.0, INF).astype(np.float64)
    a, b = 1.0, math.sqrt(2.0)
    H, W = d.shape
    for y in range(H):
        row = d[y]
        if y > 0:
            prev = d[y - 1]
            row = np.minimum(row, prev + a)
            row[1:] = np.minimum(row[1:], prev[:-1] + b)
            row[:-1] = np.minimum(row[:-1], prev[1:] + b)
        for x in range(1, W):
            if row[x - 1] + a < row[x]:
                row[x] = row[x - 1] + a
        d[y] = row
    for y in range(H - 1, -1, -1):
        row = d[y]
        if y < H - 1:
            nxt = d[y + 1]
            row = np.minimum(row, nxt + a)
            row[1:] = np.minimum(row[1:], nxt[:-1] + b)
            row[:-1] = np.minimum(row[:-1], nxt[1:] + b)
        for x in range(W - 2, -1, -1):
            if row[x + 1] + a < row[x]:
                row[x] = row[x + 1] + a
        d[y] = row
    return d * cell


def load_flood(grid, sheets, geo, np, Image):
    """Highest modelled depth band per grid cell, across all registered sheets."""
    depth = np.zeros((grid.H, grid.W), np.uint8)
    used = []
    for sheet, g in geo.items():
        if not g.get("confident"):
            continue
        band = np.load(os.path.join(DERIVED, "floodmaps", f"{sheet}.band.npy"))
        m = sheets[sheet]
        mpp = m["m_per_px"]
        b = g["bounds_wgs84"]
        h, w = band.shape
        ys, xs = np.nonzero(band)
        if not len(ys):
            continue
        # sheet pixel -> metres from the sheet's NW corner -> grid cell
        gx = ((b["west"] - grid.west) * LONM + xs * mpp) / grid.cell
        gy = ((grid.north - b["north"]) * LATM + ys * mpp) / grid.cell
        gx = gx.astype(np.int64)
        gy = gy.astype(np.int64)
        ok = (gx >= 0) & (gx < grid.W) & (gy >= 0) & (gy < grid.H)
        v = band[ys[ok], xs[ok]]
        np.maximum.at(depth, (gy[ok], gx[ok]), v)
        used.append(sheet)
    return depth, used


def label_clusters(mask, np, min_cells):
    """Connected components (4-connected) via an iterative flood fill."""
    H, W = mask.shape
    lab = np.zeros((H, W), np.int32)
    out = []
    cur = 0
    ys, xs = np.nonzero(mask)
    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if lab[sy, sx]:
            continue
        cur += 1
        stack = [(sy, sx)]
        lab[sy, sx] = cur
        cells = []
        while stack:
            y, x = stack.pop()
            cells.append((y, x))
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = cur
                    stack.append((ny, nx))
        if len(cells) >= min_cells:
            out.append(cells)
    return out


def main(argv=()):
    if "--report" in argv:
        # the page alone, from the stored result - no rasters, no distance transforms
        write_report(live.live_json(OUT))
        log("wrote docs/FLOOD_GAP.md from data/derived/floodgap.json")
        return 0
    np, Image = _np(), _pil()
    geo_path = os.path.join(DERIVED, "floodmaps", "_georef.json")
    if not os.path.exists(geo_path):
        log("no georeferenced sheets - run floodmaps.py autoref first")
        return 1
    geo = read_json(geo_path)
    sheets = read_json(os.path.join(DERIVED, "floodmaps", "_sheets.json"))
    good = {k: v for k, v in geo.items() if v.get("confident")}
    if not good:
        log("no sheet is confidently georeferenced yet")
        return 1

    west = min(v["bounds_wgs84"]["west"] for v in good.values())
    east = max(v["bounds_wgs84"]["east"] for v in good.values())
    south = min(v["bounds_wgs84"]["south"] for v in good.values())
    north = max(v["bounds_wgs84"]["north"] for v in good.values())
    grid = Grid(west, south, east, north)
    log(f"grid {grid.W} x {grid.H} cells of {CELL:.0f} m "
        f"({grid.W*grid.H*CELL*CELL/1e6:.0f} km2)  from {len(good)} sheet(s)")

    depth, used = load_flood(grid, sheets, geo, np, Image)
    cell_m2 = CELL * CELL

    # The 2012 sheets carry depth bands over lakes and the harbour as well as over land.
    # Water standing on water is not a problem a cloudburst basin solves, so it is
    # excluded from the comparison and reported separately. Part of that paint was
    # placement error - it shrank when the sheets were registered against each other -
    # so the share on water is not a test of placement. (A check that the classified
    # cells match the palette exactly, i.e. are paint and not photographed water, was
    # once run and not stored.)
    import floodreg
    water = rasterise(grid, [("poly", r) for r in floodreg.water_rings()], Image, np)
    flooded_all = depth >= FLOOD_DEPTH_MIN
    flooded = flooded_all & ~water
    on_water = int((flooded_all & water).sum())
    log(f"sheets used: {', '.join(sorted(used))}")
    log(f"modelled flooding at >= 0.1 m: {flooded_all.sum()*cell_m2/1e6:.2f} km2 total, "
        f"{flooded.sum()*cell_m2/1e6:.2f} km2 on land "
        f"({on_water*cell_m2/1e6:.2f} km2 painted over lakes and harbour)")

    # --- planned works
    layers = {}
    for layer, label, status in WORKS:
        geoms = list(iter_geoms(os.path.join(RAW, f"{layer}.geojson")))
        layers[layer] = (rasterise(grid, geoms, Image, np), label, status)
        log(f"  {label:32} {len(geoms):>5} parts")

    any_work = np.zeros_like(flooded)
    built = np.zeros_like(flooded)
    for layer, (r, label, status) in layers.items():
        any_work |= r
        if status in ("completed", "in_progress"):
            built |= r

    log("computing distance transforms ...")
    d_any = distance_transform(any_work, np)
    d_built = distance_transform(built, np)

    total = int(flooded.sum())
    from floodmaps import BANDS as LEGEND      # the sheets' own legend classes
    missing = sorted(set(sheets) - set(used))
    res = {
        "generated_from": sorted(used),
        "n_sheets_used": len(used),
        "sheets_missing": missing,
        "params": {"cell_m": CELL, "near_m": list(NEAR_M),
                   "flood_depth_min_m": LEGEND[FLOOD_DEPTH_MIN - 1]["lo"],
                   "hotspot_min_area_m2": round(HOTSPOT_MIN_CELLS * CELL * CELL),
                   "hotspot_min_depth_m": LEGEND[HOTSPOT_MIN_BAND - 1]["lo"],
                   "hotspot_min_distance_m": HOTSPOT_MIN_DISTANCE_M},
        "band_bounds": {BANDS[i]: {"lo_m": LEGEND[i - 1]["lo"], "hi_m": LEGEND[i - 1]["hi"]}
                        for i in range(1, 7)},
        "grid": {"cell_m": CELL, "width": grid.W, "height": grid.H,
                 "bounds": {"west": west, "south": south, "east": east, "north": north}},
        "caveats": [
            "The flood model is 2012 calculations of a 2010 scenario; the plan is 2018 "
            "with later addenda. This compares two snapshots taken years apart.",
            ("Only sheets that registered confidently are included; missing: "
             + ", ".join(missing) + ".") if missing else
            "Every extracted sheet registered confidently and is included.",
            f"Distances are to any part of a planned work, which is generous: being "
            f"{NEAR_M[0]} m from a cloudburst road is not the same as being protected by it.",
            "The sheets paint depth over lakes and the harbour as well as over land. "
            "Those cells are excluded here - water standing on water is not something a "
            "cloudburst basin addresses - and reported as flooded_over_water_km2.",
        ],
        "flooded_area_km2": round(total * cell_m2 / 1e6, 3),
        "by_band": {},
        "coverage": {},
        "by_sewer_system": {},
        "hotspots": [],
    }

    for i in range(1, 7):
        n = int(((depth == i) & ~water).sum())
        if n:
            res["by_band"][BANDS[i]] = {"cells": n, "area_m2": round(n * cell_m2)}

    for m in NEAR_M:
        res["coverage"][f"within_{m}m_of_any_planned_work"] = round(
            float((flooded & (d_any <= m)).sum()) / total, 3) if total else None
        res["coverage"][f"within_{m}m_of_a_built_or_started_project"] = round(
            float((flooded & (d_built <= m)).sum()) / total, 3) if total else None

    # --- QA: flooding must be under-represented on open water. If the registration were
    # wrong, flood cells would land in water at roughly the water's share of the grid;
    # landing well below that is independent evidence the sheets are placed correctly.
    baseline = float(water.mean())
    res["qa_flood_vs_water"] = {
        "water_share_of_grid": round(baseline, 3),
        "note": "Values below the baseline mean flooding avoids open water, as it should.",
        "by_band": {},
    }
    for i in range(1, 7):
        m = depth == i
        n = int(m.sum())
        if n:
            res["qa_flood_vs_water"]["by_band"][BANDS[i]] = {
                "cells": n, "share_in_water": round(float((m & water).sum()) / n, 3)}
    res["flooded_over_water_km2"] = round(on_water * cell_m2 / 1e6, 3)
    res["flooded_total_km2"] = round(int(flooded_all.sum()) * cell_m2 / 1e6, 3)
    worst = max((v["share_in_water"] for v in res["qa_flood_vs_water"]["by_band"].values()),
                default=0.0)
    res["qa_flood_vs_water"]["passes"] = bool(worst < baseline)

    # --- crossed with sewer system type
    kl = os.path.join(RAW, "sp_kloakoplande.geojson")
    if os.path.exists(kl):
        by_sys = defaultdict(list)
        for f in read_json(kl)["features"]:
            g = f.get("geometry")
            if not g:
                continue
            sysname = (f["properties"].get("kloaksystem_status") or "unspecified")
            polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
            for poly in polys:
                by_sys[sysname].append(("poly", poly[0]))
        allcatch = rasterise(grid, [g for gs in by_sys.values() for g in gs], Image, np)
        inside = int((flooded & allcatch).sum())
        # Shares are of flooding that falls INSIDE a mapped sewer catchment. The layer
        # does not tile the city - parks, rail land and quaysides are outside it - so
        # normalising by total flooding would understate every category.
        res["sewer_catchment_coverage"] = {
            "catchment_share_of_grid": round(float(allcatch.mean()), 3),
            "flooded_cells_inside_a_catchment": inside,
            "flooded_cells_total": total,
            "share_of_flooding_inside": round(inside / total, 3) if total else None,
        }
        # Report the base rate alongside the flood share. Without it the numbers
        # mislead: a high share of flooding over combined sewer means little when most
        # of the mapped area is combined sewer; the ratio of the two is the finding.
        catch_cells = int(allcatch.sum())
        for sysname, geoms in by_sys.items():
            r = rasterise(grid, geoms, Image, np)
            n = int((flooded & r).sum())
            area_share = float(r.sum()) / catch_cells if catch_cells else 0.0
            if n:
                flood_share = n / inside if inside else 0.0
                res["by_sewer_system"][sysname] = {
                    "flooded_area_m2": round(n * cell_m2),
                    "share_of_flooding_in_mapped_catchments": round(flood_share, 3),
                    "share_of_mapped_catchment_area": round(area_share, 3),
                    "concentration_ratio": round(flood_share / area_share, 2) if area_share else None,
                    "share_of_all_flooding": round(n / total, 3),
                }

    # --- the worst unaddressed places
    far = flooded & (d_any > HOTSPOT_MIN_DISTANCE_M) & (depth >= HOTSPOT_MIN_BAND)
    clusters = label_clusters(far, np, HOTSPOT_MIN_CELLS)
    log(f"unaddressed clusters (>=0.2 m, >100 m from any planned work): {len(clusters)}")
    spots = []
    for cells in clusters:
        ys = [c[0] for c in cells]
        xs = [c[1] for c in cells]
        cy, cx = sum(ys) / len(ys), sum(xs) / len(xs)
        lon, lat = grid.lonlat(cx + 0.5, cy + 0.5)
        vol = sum(BAND_MID[depth[y, x]] for y, x in cells) * cell_m2
        spots.append({
            "lon": round(lon, 6), "lat": round(lat, 6),
            "area_m2": round(len(cells) * cell_m2),
            "max_depth_band": BANDS[int(max(depth[y, x] for y, x in cells))],
            "implied_volume_m3": round(vol),
            "distance_to_nearest_planned_work_m": round(
                float(min(d_any[y, x] for y, x in cells))),
        })
    spots.sort(key=lambda s: -s["implied_volume_m3"])
    res["hotspots"] = spots[:40]
    res["hotspot_totals"] = {
        "clusters": len(spots),
        "area_m2": round(sum(s["area_m2"] for s in spots)),
        "implied_volume_m3": round(sum(s["implied_volume_m3"] for s in spots)),
    }

    write_json(OUT, res)
    write_json(os.path.join(DERIVED, "viewer", "flood_hotspots.geojson"), {
        "type": "FeatureCollection",
        "features": [{"type": "Feature",
                      "geometry": {"type": "Point", "coordinates": [s["lon"], s["lat"]]},
                      "properties": {k: v for k, v in s.items() if k not in ("lon", "lat")}}
                     for s in spots],
    })

    log("\n--- how much modelled flooding is near a planned work ---")
    for m in NEAR_M:
        a = res["coverage"][f"within_{m}m_of_any_planned_work"]
        b = res["coverage"][f"within_{m}m_of_a_built_or_started_project"]
        log(f"  within {m:>3} m:  any planned work {a*100:5.1f}%    "
            f"built or started {b*100:5.1f}%")
    q = res["qa_flood_vs_water"]
    log(f"\n--- QA: does modelled flooding avoid open water? ---")
    log(f"  water is {q['water_share_of_grid']*100:.1f}% of the grid; flooding lands there:")
    for k, v in q["by_band"].items():
        log(f"    {k:>9} {v['share_in_water']*100:5.1f}%")
    log(f"  {'PASS' if q['passes'] else 'FAIL'} - every band is below the baseline"
        if q["passes"] else "  FAIL - a band is over-represented in water; check registration")

    cov = res.get("sewer_catchment_coverage", {})
    log("\n--- flooding by sewer system underneath ---")
    if cov:
        log(f"  (sewer catchments cover {cov['catchment_share_of_grid']*100:.0f}% of the grid "
            f"and contain {cov['share_of_flooding_inside']*100:.0f}% of the flooding)")
    log(f"  {'system':44}{'of area':>9}{'of flood':>10}{'ratio':>8}")
    for k, v in sorted(res["by_sewer_system"].items(),
                       key=lambda x: -(x[1]["share_of_flooding_in_mapped_catchments"] or 0)):
        log(f"  {k[:44]:44}{v['share_of_mapped_catchment_area']*100:>8.1f}%"
            f"{v['share_of_flooding_in_mapped_catchments']*100:>9.1f}%"
            f"{(v['concentration_ratio'] or 0):>7.2f}x")
    log("  ratio ~1 means flooding is spread in proportion to how much area that system "
        "covers,\n  i.e. no concentration - the inner city is simply combined-sewer almost "
        "everywhere.")
    t = res["hotspot_totals"]
    log(f"\n--- unaddressed hotspots ---")
    log(f"  {t['clusters']} clusters, {t['area_m2']/1e6:.2f} km2, "
        f"implying {t['implied_volume_m3']:,} m3 of standing water")
    log("  worst five:")
    for s in spots[:5]:
        log(f"    {s['lat']:.5f},{s['lon']:.5f}  {s['area_m2']:>7,} m2  "
            f"max {s['max_depth_band']:>8}  {s['implied_volume_m3']:>7,} m3  "
            f"{s['distance_to_nearest_planned_work_m']:>4} m from anything planned")
    write_report(live.live_json(OUT))
    render_map(grid, depth, layers, spots, np, Image)
    log("\nwrote data/derived/floodgap.json, viewer/flood_hotspots.geojson "
        "and docs/FLOOD_GAP.md")
    return 0


BAND_RGB = [(0, 0, 0), (247, 251, 255), (209, 226, 242), (154, 199, 224),
            (81, 156, 204), (28, 107, 176), (8, 48, 107)]


def render_map(grid, depth, layers, spots, np, Image):
    """One picture of the finding: modelled flooding, what is planned, what is built."""
    from PIL import ImageDraw
    import floodreg
    H, W = depth.shape
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (13, 17, 23)

    water = rasterise(grid, [("poly", r) for r in floodreg.water_rings()], Image, np)
    img[water] = (27, 58, 92)

    # planned works in grey, built or started in amber, so the gap is the picture
    planned = np.zeros((H, W), bool)
    built = np.zeros((H, W), bool)
    for layer, (r, label, status) in layers.items():
        if status == "planned":
            planned |= r
        else:
            built |= r
    # Works first, flooding on top. Painting the built works last hid the flooding
    # exactly where something had been built, which understates the problem visually.
    img[planned & ~built] = (70, 78, 88)
    img[built] = (255, 209, 102)
    for i in range(1, 7):
        img[depth == i] = BAND_RGB[i]

    im = Image.fromarray(img, "RGB")
    dr = ImageDraw.Draw(im)
    for s_ in spots:
        x, y = grid.xy(s_["lon"], s_["lat"])
        r = max(9.0, math.sqrt(s_["area_m2"]) / grid.cell)
        dr.ellipse([x - r, y - r, x + r, y + r], outline=(255, 92, 122), width=3)

    scale = 1500 / im.width
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, 470, 128], fill=(13, 17, 23))
    dr.text((12, 10), "Modelled 100-year flooding (2012), recovered from PDF",
            fill=(230, 237, 243))
    for i, (c, t) in enumerate([
            ((154, 199, 224), "modelled flood depth (light = shallow)"),
            ((70, 78, 88), "cloudburst works: planned only"),
            ((255, 209, 102), "cloudburst works: built or started"),
            ((255, 92, 122), "deep water, nothing planned within 100 m")]):
        y = 34 + i * 22
        dr.rectangle([14, y, 30, y + 12], fill=c)
        dr.text((40, y - 1), t, fill=(180, 190, 200))
    dst = os.path.join(ROOT, "docs", "flood_gap_map.png")
    im.save(dst, optimize=True)
    log(f"wrote docs/flood_gap_map.png  ({im.width}x{im.height})")


def write_report(res):
    """The page, from the stored result read live: every number links to its field, and
    every assertion is a checked claim (LIVE_NUMBERS.md section 11), registered in
    data/manual/claims.d/w3-fr.json with what it rests on. What the page once said and
    could not justify is in docs/ARCHIVE.md, not here."""
    C = live.claim
    o = []
    w = o.append
    c, p, bb = res["coverage"], res["params"], res["band_bounds"]
    near = list(p["near_m"])

    def band(label):
        """A depth class, printed from the legend bounds it stands for."""
        lo, hi = bb[label]["lo_m"], bb[label]["hi_m"]
        return f"{lo:g}–{hi:g} m" if hi is not None else f"over {lo:g} m"

    w("# Does the cloudburst plan go where the water goes?\n")
    w(C("C-FR-FG-WHAT", "Generated by `scripts/floodgap.py`. It compares the city's 2012 flood "
        "sheets - calculated flood scenarios for a hundred-year event, recovered here from the "
        "PDFs they were published in - with the cloudburst works in the city's cloudburst-plan "
        "map layers.") + "\n")
    missing = list(res["sheets_missing"])
    names = ", ".join(res["generated_from"])
    if missing:
        w(C("C-FR-FG-SHEETS", f"Covers **{names}**: the sheets the pipeline flags as confidently "
            f"placed. {', '.join(missing)} {'is' if len(missing) == 1 else 'are'} not "
            "included.") + "\n")
    else:
        w(C("C-FR-FG-SHEETS", f"Covers all {res['n_sheets_used']} sheets: **{names}**. Every "
            "sheet the pipeline extracted carries its flag as confidently placed, and is "
            "used.") + "\n")

    w("## The headline\n")
    w(C("C-FR-FG-AREA", f"Across {res['flooded_area_km2']:g} km² of modelled flooding **on "
        f"land** at {p['flood_depth_min_m']:g} m or deeper, with a further "
        f"{res['flooded_over_water_km2']:g} km² of painted depth falling on mapped lakes and "
        "harbour and excluded here:") + "\n")
    w("| Distance | Near *any* planned work | Near something **built or started** |")
    w("|---|---:|---:|")
    for m in near:
        a = c[f"within_{int(m)}m_of_any_planned_work"]
        b = c[f"within_{int(m)}m_of_a_built_or_started_project"]
        w(f"| within {m} m | {a * 100:.1f}% | {b * 100:.1f}% |")
    w("")
    far = near[-1]
    a_far = c[f"within_{int(far)}m_of_any_planned_work"]
    b_far = c[f"within_{int(far)}m_of_a_built_or_started_project"]
    w(C("C-FR-FG-NEAR", f"{a_far * 100:.0f}% of the modelled flooding on land lies within "
        f"{far} m of some part of a planned work, and {b_far * 100:.0f}% within {far} m of a "
        "project the city's layers list as started or completed.") + "\n")
    w(C("C-FR-FG-GENEROUS", f"Read the distances as generous. Being {near[0]} m from a "
        "cloudburst road is not the same as being protected by it, and this counts any part of "
        "any planned work.") + "\n")

    w("## Modelled depth\n")
    w(C("C-FR-FG-BANDS", "Land area by the deepest band any sheet paints on each cell; the "
        "bands are the classes of the sheets' own legend.") + "\n")
    w("| Band | Area (m²) |")
    w("|---|---:|")
    for k, v in res["by_band"].items():
        w(f"| {band(k)} | {v['area_m2']:,} |")
    w("")

    q = res["qa_flood_vs_water"]
    base = q["water_share_of_grid"]
    shares = {k: v["share_in_water"] for k, v in q["by_band"].items()}
    w("## Does the modelled flooding avoid open water?\n")
    w(C("C-FR-FG-WATERSHARE", f"Open water is {base * 100:.1f}% of the study area. The share "
        "of each band's painted cells that falls in mapped open water:") + "\n")
    w("| Band | Share falling in open water |")
    w("|---|---:|")
    for k, v in shares.items():
        w(f"| {band(k)} | {v * 100:.1f}% |")
    w("")
    w(C("C-FR-FG-NOTEST", "Painted depth that lands on mapped open water may be paint the "
        "city put on lakes and the harbour or error in where a sheet is placed, and nothing "
        "here separates the two, so a band's share in open water cannot test the placement: "
        "it is shown, not scored.") + "\n")

    cov = res.get("sewer_catchment_coverage")
    w("## What is underneath it\n")
    if cov:
        w(C("C-FR-FG-CATCH", f"Sewer catchments cover "
            f"{cov['catchment_share_of_grid'] * 100:.0f}% of the study area and contain "
            f"{cov['share_of_flooding_inside'] * 100:.0f}% of the flooding. Shares below are of "
            "that portion.") + "\n")
    w("| System | Share of area | Share of flooding | Ratio |")
    w("|---|---:|---:|---:|")
    for k, v in sorted(res["by_sewer_system"].items(),
                       key=lambda x: -(x[1]["share_of_flooding_in_mapped_catchments"] or 0)):
        r = v["concentration_ratio"]
        w(f"| `{k}` | {v['share_of_mapped_catchment_area'] * 100:.1f}% | "
          f"{v['share_of_flooding_in_mapped_catchments'] * 100:.1f}% | "
          + (f"{r:g}×" if r is not None else "—") + " |")
    w("")
    comb = res["by_sewer_system"].get("Fælleskloakeret")
    if comb:
        r = comb["concentration_ratio"]
        w(C("C-FR-FG-COMBINED", f"{comb['share_of_flooding_in_mapped_catchments'] * 100:.0f}% "
            "of the flooding inside mapped catchments lies over catchments recorded as combined "
            "sewer (`Fælleskloakeret`), a system that carries sewage and urban runoff together; "
            f"they make up {comb['share_of_mapped_catchment_area'] * 100:.0f}% of the mapped "
            f"catchment area, so flooding lies over them {r:g} times as often as their share of "
            "the area would give.") + "\n")

    t = res["hotspot_totals"]
    w("## Places with deep water and nothing planned nearby\n")
    w(C("C-FR-FG-HOTSPOTS", f"{t['clusters']} clusters of at least "
        f"{p['hotspot_min_area_m2']:,} m², at {p['hotspot_min_depth_m']:g} m or deeper, more "
        f"than {p['hotspot_min_distance_m']} m from any planned work — {t['area_m2']:,} m² "
        f"holding an implied {t['implied_volume_m3']:,} m³. The largest by implied volume are "
        "listed; every cluster is in `data/derived/viewer/flood_hotspots.geojson`.") + "\n")
    w("| lat, lon | Area (m²) | Max depth | Implied volume (m³) | Nearest planned work |")
    w("|---|---:|---|---:|---:|")
    for s_ in res["hotspots"]:
        w(f"| {s_['lat']:.5f}, {s_['lon']:.5f} | {s_['area_m2']:,} | "
          f"{band(s_['max_depth_band'])} | {s_['implied_volume_m3']:,} | "
          f"{s_['distance_to_nearest_planned_work_m']} m |")
    w("")
    w(C("C-FR-FG-VOLUME", "Volumes are the depth-band midpoint times area, so they are "
        "indicative only.") + "\n")

    w("## Caveats\n")
    w("- " + C("C-FR-FG-SNAPSHOTS", "The sheets are titled flood maps at a hundred-year event "
               "in 2010, and the city's dataset record says they are based on calculations "
               "from 2012; the works are the city's layers as fetched for this project, whose "
               "alignments carry expected commissioning years into the late 2030s. This "
               "compares two snapshots taken years apart."))
    w("- " + C("C-FR-FG-PAINT", "Painted depth that falls on mapped lakes and harbour - "
               f"{res['flooded_over_water_km2']:g} km² at {p['flood_depth_min_m']:g} m or deeper "
               "- is excluded from the flood area and reported separately, because water "
               "standing on water is not something a cloudburst basin addresses. It may be "
               "paint the city put on water or error in where a sheet is placed: the area fell "
               "when the sheets were registered against each other, so some of it was "
               "placement."))
    w("")
    write_doc(os.path.join(ROOT, "docs", "FLOOD_GAP.md"), "\n".join(o))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
