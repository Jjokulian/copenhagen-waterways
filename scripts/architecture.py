"""The separated architecture, as a map of where it would happen.

PROGRAMME.md section 2 argues an architecture: rain out of the combined sewer, the
spare basins retired, the rain stream to a terminal water, the foul stream steady to
a plant. That argument is written in prose and in rates. This writes the third form -
**where**, on the actual city, each piece of it lands - and the classification is the
whole point:

  MEASURED   the sewer-catchment layer: which catchments are combined today, what
             each one has for impervious area and person equivalents, and which
             plant it drains to. Also the city's OWN plan for each catchment, which
             is how the map can say what is already intended and what is not.
  MEASURED   the national outfall register: overflow structures, their type, and the
             basin volume registered behind them.
  MEASURED   the cloudburst basins the city has built or is building.
  PROPOSED   the pond cells and the polder outline. Schematic, and labelled as such
             on the page - nobody has surveyed a cell boundary.

The scenario arithmetic lives in the page rather than here, so that a reader can see
the numbers move and the assumptions that move them. What this file provides is the
stock each scenario multiplies: hectares, person equivalents, structures, basin m3.

Writes docs/data/architecture.json.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, MANUAL, RAW, ROOT, log, read_json
from programme import AMAGER, RAIN_MM_H, RUNOFF_C, VESTAMAGER_HA, _inside

# Copenhagen and the inner suburbs. Everything outside is dropped rather than drawn
# faintly: this is a map of one city's plumbing, not a regional overview.
BOX = (12.40, 55.58, 12.74, 55.76)
SIMPLIFY_DEG = 6e-5          # ~5 m north-south. Catchment edges are administrative.

# Which status string is which architecture. The register's vocabulary is longer than
# the distinction that matters here, which is: does rain share a pipe with sewage?
CLASSES = {
    "Fælleskloakeret": ("combined", "Rain and sewage in one pipe"),
    "Fælleskloakeret, vejvand til recipient": ("combined_road_out",
                                               "Combined, but road water goes out separately"),
    "Separatkloakeretopland tilkoblet fællessystemet": ("separate_into_combined",
                                                        "Separated, then joined to the combined system"),
    "Spildevandskloakeret": ("foul_only", "Sewage only - rain is already elsewhere"),
    "Separatkloakeret, tag- og vejvand til recipient": ("separate",
                                                        "Separated: roof and road water to a receiving water"),
    "Separatkloakeret, vejvand til recipient": ("separate_road",
                                                "Separated: road water to a receiving water"),
    "3-strenget separat kloaksystem med separat inddeling af husspildevand, tagvand og vejvand":
        ("three_pipe", "Three pipes: sewage, roof water and road water apart"),
    "Separat, dele af matriklen separat": ("part_separate", "Partly separated"),
}


def rdp(pts, eps):
    """Ramer-Douglas-Peucker, iterative. Boundaries here are drawn lines, not
    measurements, so removing a vertex removes no information."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        ax, ay = pts[i]
        bx, by = pts[j]
        dx, dy = bx - ax, by - ay
        n = math.hypot(dx, dy)
        best, bi = -1.0, -1
        for k in range(i + 1, j):
            px, py = pts[k]
            d = (abs(dy * px - dx * py + bx * ay - by * ax) / n if n else
                 math.hypot(px - ax, py - ay))
            if d > best:
                best, bi = d, k
        if bi >= 0 and best > eps:
            keep[bi] = True
            stack += [(i, bi), (bi, j)]
    return [p for p, k in zip(pts, keep) if k]


def rings_of(geom, eps=SIMPLIFY_DEG, keep_holes=False):
    """Outer rings only, simplified and rounded. Holes in a sewer catchment are
    courtyards; at this scale they are noise."""
    out = []
    t = geom["type"]
    polys = [geom["coordinates"]] if t == "Polygon" else geom["coordinates"]
    if t not in ("Polygon", "MultiPolygon"):
        return out
    for poly in polys:
        for i, ring in enumerate(poly):
            if i and not keep_holes:
                continue
            pts = [(float(x), float(y)) for x, y, *_ in ring]
            pts = rdp(pts, eps)
            if len(pts) >= 4:
                out.append([[round(x, 5), round(y, 5)] for x, y in pts])
    return out


def centroid(rings):
    xs = [p[0] for r in rings for p in r]
    ys = [p[1] for r in rings for p in r]
    return [round(sum(xs) / len(xs), 5), round(sum(ys) / len(ys), 5)] if xs else None


def in_box(x, y):
    return BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]



def structures(cats):
    """Gully gratings and manholes, counted into the catchments they stand in.

    From scripts/fetch_structures.py. Two things about this layer are worth carrying
    forward rather than smoothing over. It has a **z coordinate on every point**, so
    the city has a dense elevation sample along its own streets. And it has a type
    column - `ristetype`, `broendtype` - which is **empty**: every one of the 123,806
    gratings and 94% of the 85,816 wells says only that a structure is there. So this
    can say how many and where, and cannot say what any of them is. That is the
    unfilled-field class in this project's error taxonomy, in the city's own register.
    """
    d = os.path.join(RAW, "structures")
    if not os.path.exists(os.path.join(d, "rist.json")):
        return None
    CELL = 0.004
    grid, polys = {}, []
    for n, c in enumerate(cats):
        for ring in c["g"]:
            xs = [q[0] for q in ring]
            ys = [q[1] for q in ring]
            b = (min(xs), min(ys), max(xs), max(ys))
            polys.append((ring, b, n))
            for i in range(int(b[0] / CELL), int(b[2] / CELL) + 1):
                for j in range(int(b[1] / CELL), int(b[3] / CELL) + 1):
                    grid.setdefault((i, j), []).append(len(polys) - 1)

    def hit(x, y):
        for k in grid.get((int(x / CELL), int(y / CELL)), ()):
            ring, b, n = polys[k]
            if not (b[0] <= x <= b[2] and b[1] <= y <= b[3]):
                continue
            ins = False
            for a in range(len(ring)):
                xi, yi = ring[a - 1]
                xj, yj = ring[a]
                if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                    ins = not ins
            if ins:
                return n
        return None

    out = {}
    for layer, key in (("rist", "ri"), ("broend", "br")):
        pts = read_json(os.path.join(d, layer + ".json"))
        typed = sum(1 for q in pts if q[3])
        dates = sorted(q[4] for q in pts if q[4])
        n_in = 0
        for lon, lat, z, t, dt in pts:
            n = hit(lon, lat)
            if n is None:
                continue
            cats[n][key] = cats[n].get(key, 0) + 1
            n_in += 1
        out[layer] = {
            "total": len(pts), "in_a_catchment": n_in,
            "typed": typed, "type_field_empty_pct": 100 * (1 - typed / len(pts)),
            "first": dates[0] if dates else None, "last": dates[-1] if dates else None,
            "median_date": dates[len(dates) // 2] if dates else None,
        }
        del pts
    return out


def buildings(cats):
    """Count buildings into the catchments they stand in, from the OSM extract.

    Any scheme that is priced per property needs a denominator, and PE is not one:
    person equivalents count load, not addresses. The extract is 45 MB of Overpass
    JSON and this box has a few hundred MB of RAM, so it is scanned as a byte stream
    for the bounding box each element already carries rather than parsed - the
    centroid of a building's bbox is well inside the building at this scale.

    Adds `bu` to each catchment. Returns the total counted, or None if no extract.
    """
    import re
    path = os.path.join(RAW, "osm", "buildings.json")
    if not os.path.exists(path):
        return None
    CELL = 0.004
    grid, polys = {}, []
    for n, c in enumerate(cats):
        for ring in c["g"]:
            xs = [q[0] for q in ring]
            ys = [q[1] for q in ring]
            b = (min(xs), min(ys), max(xs), max(ys))
            polys.append((ring, b, n))
            for i in range(int(b[0] / CELL), int(b[2] / CELL) + 1):
                for j in range(int(b[1] / CELL), int(b[3] / CELL) + 1):
                    grid.setdefault((i, j), []).append(len(polys) - 1)

    def hit(x, y):
        for k in grid.get((int(x / CELL), int(y / CELL)), ()):
            ring, b, n = polys[k]
            if not (b[0] <= x <= b[2] and b[1] <= y <= b[3]):
                continue
            ins = False
            for a in range(len(ring)):
                xi, yi = ring[a - 1]
                xj, yj = ring[a]
                if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                    ins = not ins
            if ins:
                return n
        return None

    pat = re.compile(rb'"minlat":\s*([\d.]+),\s*"minlon":\s*([\d.]+),'
                     rb'\s*"maxlat":\s*([\d.]+),\s*"maxlon":\s*([\d.]+)')
    total, placed, tail = 0, 0, b""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(1 << 22)
            if not chunk:
                break
            buf = tail + chunk
            for m in pat.finditer(buf):
                total += 1
                a, b_, c_, d = (float(x) for x in m.groups())
                n = hit((b_ + d) / 2, (a + c_) / 2)
                if n is not None:
                    cats[n]["bu"] = cats[n].get("bu", 0) + 1
                    placed += 1
            tail = buf[-200:]
    return {"in_extract": total, "in_a_catchment": placed}


def street_metres(cats):
    """Road centreline inside the combined-sewered catchments, by island.

    The bore runs manhole to manhole under a street, so the length of the job is a
    length of street rather than an area. OSM is the only road geometry this project
    has fetched, and the copy here carries no tags - service roads, alleys and paths
    are in it and cannot be told from a carriageway - so **this is an upper bound**,
    and it is the honest one to quote: a real programme would work down from it as
    the utility rules streets out, not up from a guess.

    Returns metres, or None if the OSM extract is not present in this clone.
    """
    path = os.path.join(RAW, "osm", "roads.json")
    if not os.path.exists(path):
        return None
    CELL = 0.004                                   # ~250 m: index, not geometry
    grid, polys = {}, []
    for c in cats:
        if not (c["c"].startswith("combined") or c["c"] == "separate_into_combined"):
            continue
        for ring in c["g"]:
            xs = [q[0] for q in ring]
            ys = [q[1] for q in ring]
            b = (min(xs), min(ys), max(xs), max(ys))
            polys.append((ring, b, c["i"]))
            for i in range(int(b[0] / CELL), int(b[2] / CELL) + 1):
                for j in range(int(b[1] / CELL), int(b[3] / CELL) + 1):
                    grid.setdefault((i, j), []).append(len(polys) - 1)

    def hit(x, y):
        for k in grid.get((int(x / CELL), int(y / CELL)), ()):
            ring, b, isl = polys[k]
            if not (b[0] <= x <= b[2] and b[1] <= y <= b[3]):
                continue
            ins = False
            for a in range(len(ring)):
                xi, yi = ring[a - 1]
                xj, yj = ring[a]
                if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                    ins = not ins
            if ins:
                return isl
        return None

    R = 6371000.0
    out = {"amager": 0.0, "mainland": 0.0, "all_roads_in_extract": 0.0}
    for w in read_json(path):
        for a in range(len(w) - 1):
            x1, y1 = w[a]
            x2, y2 = w[a + 1]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            d = math.hypot((x2 - x1) * math.cos(math.radians(my)) * math.pi / 180 * R,
                           (y2 - y1) * math.pi / 180 * R)
            out["all_roads_in_extract"] += d
            isl = hit(mx, my)
            if isl:
                out[isl] += d
    return {k: round(v) for k, v in out.items()}


def plan_pipe_ends():
    """How close the planned cloudburst pipes come to a receiving water, at their ends.

    Asked because the argument leans on "20% of the flood path has a planned pipe
    within 100 m", and a reader can fairly hear that as *a pipe that already goes
    somewhere*. It does not: `skp_veje_tunneller_kk` is a segmented network, not a
    set of routed lines, so a segment's end is usually another segment rather than an
    outlet. This measures exactly that, and the honest use of the numbers is as
    evidence about the LAYER - it cannot say where any route discharges. Distance is
    to the coastline and the harbour polygon, whichever is nearer.

    Returns None if the plan layer or the harbour extract is missing.
    """
    plan = os.path.join(RAW, "skp_veje_tunneller_kk.geojson")
    if not os.path.exists(plan):
        return None
    pts = []
    for f in read_json(os.path.join(DERIVED, "viewer", "coast.geojson"))["features"]:
        g = f["geometry"]
        parts = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        for line in parts:
            pts += [(float(x), float(y)) for x, y, *_ in line]
    hv = os.path.join(RAW, "havn.geojson")
    if os.path.exists(hv):
        def walk(c):
            if isinstance(c[0], (int, float)):
                pts.append((float(c[0]), float(c[1])))
            else:
                for q in c:
                    walk(q)
        for f in read_json(hv)["features"]:
            if f.get("geometry"):
                walk(f["geometry"]["coordinates"])
    CELL, R = 0.01, 6371000.0
    grid = {}
    for x, y in pts:
        grid.setdefault((int(x / CELL), int(y / CELL)), []).append((x, y))

    def nearest(x, y, rings=4):
        best = float("inf")
        i0, j0 = int(x / CELL), int(y / CELL)
        for r in range(rings + 1):
            for i in range(i0 - r, i0 + r + 1):
                for j in range(j0 - r, j0 + r + 1):
                    if r and max(abs(i - i0), abs(j - j0)) != r:
                        continue
                    for cx, cy in grid.get((i, j), ()):
                        d = math.hypot(
                            (cx - x) * math.cos(math.radians(y)) * math.pi / 180 * R,
                            (cy - y) * math.pi / 180 * R)
                        best = min(best, d)
            if best < r * CELL * 0.5 * 111000:
                break
        return best

    ds = []
    for f in read_json(plan)["features"]:
        if (f["properties"].get("typologi") or "") != "Skybrudsledning":
            continue
        g = f.get("geometry") or {}
        parts = ([g["coordinates"]] if g.get("type") == "LineString"
                 else g.get("coordinates", []))
        ends = [q for line in parts if len(line) > 1 for q in (line[0], line[-1])]
        if ends:
            ds.append(min(nearest(q[0], q[1]) for q in ends))
    if not ds:
        return None
    ds.sort()
    return {
        "n": len(ds),
        "median_m": round(ds[len(ds) // 2]),
        "within_50m": sum(1 for x in ds if x <= 50),
        "within_200m": sum(1 for x in ds if x <= 200),
        "within_500m": sum(1 for x in ds if x <= 500),
        "_means": "Evidence about the plan layer, which is segmented. It is NOT a "
                  "statement about where any cloudburst route discharges - that is "
                  "in the project pages, one at a time, and is not established here.",
    }


def main():
    codes = read_json(os.path.join(MANUAL, "codelists.json"))["bygvaerkstype"]
    streams = read_json(os.path.join(DERIVED, "streams.json"))

    # ---- catchments: the layer the whole architecture acts on
    cats, totals = [], {}
    src = read_json(os.path.join(RAW, "sp_kloakoplande.geojson"))
    for f in src["features"]:
        p, g = f["properties"], f.get("geometry")
        if not g:
            continue
        rings = rings_of(g)
        if not rings:
            continue
        c = centroid(rings)
        if not in_box(*c):
            continue
        st = p.get("kloaksystem_status") or ""
        pl = p.get("kloaksystem_plan") or ""
        cls = CLASSES.get(st, ("unknown", "Not recorded"))[0]
        plan = CLASSES.get(pl, ("unknown", "Not recorded"))[0]
        cats.append({
            "l": p.get("label"),
            "c": cls, "p": plan,
            "ha": round(p.get("befaestet_areal_status") or 0, 2),
            "pe": int(p.get("pe_status") or 0),
            "pl": (p.get("renseanlaeg") or "").replace("Renseanlæg ", "") or None,
            "i": "amager" if _inside(c[0], c[1], AMAGER) else "mainland",
            "g": rings,
        })

    for c in cats:
        t = totals.setdefault(c["c"], {"n": 0, "ha": 0.0, "pe": 0,
                                       "planned_change_ha": 0.0})
        t["n"] += 1
        t["ha"] += c["ha"]
        t["pe"] += c["pe"]
        if c["p"] != c["c"]:
            t["planned_change_ha"] += c["ha"]

    # ---- outfalls: which retire when the rain leaves the pipe
    outs = []
    for f in read_json(os.path.join(DERIVED, "viewer", "discharge_points.geojson"))["features"]:
        g, p = f.get("geometry"), f["properties"]
        if not g or g["type"] != "Point":
            continue
        x, y = g["coordinates"][:2]
        if not in_box(x, y):
            continue
        t = p.get("bgv_type")
        outs.append({
            "n": p.get("pkt_navn"), "t": t,
            "cs": bool(codes.get(t, {}).get("combined_sewer")),
            "sb": p.get("vol_sb") or 0, "fb": p.get("vol_fbas") or 0,
            "k": p.get("komm_navn"),
            "x": round(x, 5), "y": round(y, 5),
        })

    # ---- the cloudburst basins the city is building anyway
    basins = []
    for f in read_json(os.path.join(DERIVED, "viewer", "basins.geojson"))["features"]:
        g, p = f.get("geometry"), f["properties"]
        if not g:
            continue
        rings = rings_of(g, eps=SIMPLIFY_DEG * 2)
        if not rings:
            continue
        c = centroid(rings)
        if not in_box(*c):
            continue
        basins.append({"n": p.get("projekt_navn"), "t": p.get("typologi"),
                       "y": p.get("forventet_ibrugtagning"),
                       "o": p.get("vandopland"), "x": c[0], "y_": c[1]})

    # ---- coastline. Lines rather than polygons in the source, so it is drawn as a
    # stroke: the map's ground truth is the sewer layer, and the coast is there to
    # let a reader recognise the city.
    coast = []
    for f in read_json(os.path.join(DERIVED, "viewer", "coast.geojson"))["features"]:
        g = f.get("geometry") or {}
        if g.get("type") not in ("LineString", "MultiLineString"):
            continue
        parts = ([g["coordinates"]] if g["type"] == "LineString"
                 else g["coordinates"])
        for line in parts:
            pts = [(float(x), float(y)) for x, y, *_ in line]
            if not any(in_box(x, y) for x, y in pts):
                continue
            pts = rdp(pts, SIMPLIFY_DEG * 2)
            if len(pts) >= 2:
                coast.append([[round(x, 5), round(y, 5)] for x, y in pts])

    bld = buildings(cats)
    if bld:
        log(f"  buildings: {bld['in_extract']:,} in the extract, "
            f"{bld['in_a_catchment']:,} inside a catchment")
    struct = structures(cats)
    if struct:
        for k, v in struct.items():
            log(f"  {k}: {v['total']:,} points, {v['in_a_catchment']:,} inside a "
                f"catchment, type column empty on {v['type_field_empty_pct']:.0f}%, "
                f"registered {v['first']} to {v['last']}")
    streets = street_metres(cats)
    ends = plan_pipe_ends()
    if ends:
        log(f"  planned cloudburst pipe segments: {ends['n']}, "
            f"{ends['within_50m']} with an end within 50 m of water, "
            f"median {ends['median_m']:,} m")
    if streets:
        log(f"  street inside combined catchments: "
            f"{(streets['amager'] + streets['mainland'])/1000:,.0f} km "
            f"(of {streets['all_roads_in_extract']/1000:,.0f} km in the extract)")

    out = {
        "_what": "Where the separated architecture would act, on the sewer layer "
                 "the city actually has.",
        "_measured": "Catchment class, plan, impervious area, person equivalents "
                     "and plant are the municipal sewer-catchment layer. Outfall "
                     "type and basin volume are the national RBU register. Basins "
                     "are the city's cloudburst projects.",
        "_proposed": "The polder outline and the pond cells are schematic. Nothing "
                     "in this project has surveyed them.",
        "box": BOX,
        "classes": {v[0]: v[1] for v in CLASSES.values()},
        "catchments": cats,
        "outfalls": outs,
        "basins": basins,
        "coast": coast,
        "totals": totals,
        "outfall_totals": {
            "combined_structures": sum(1 for o in outs if o["cs"]),
            "separate_outlets": sum(1 for o in outs if not o["cs"]),
            "combined_basin_m3": sum(o["sb"] + o["fb"] for o in outs if o["cs"]),
            "separate_basin_m3": sum(o["sb"] + o["fb"] for o in outs if not o["cs"]),
        },
        "rain": {
            "design_mm_h": RAIN_MM_H, "runoff_c": RUNOFF_C,
            "record": streams["rain_record"],
            "foul_stated": streams["foul_stated"],
            "ponds": streams["ponds"],
            # The pond areas in streams.json are computed for Amager's impervious
            # area. The page scales them to whatever scope is selected, so it needs
            # to know what they were computed on.
            "ponds_basis_ha": streams["amager"]["combined_sewered_impervious_ha"],
        },
        "street_m": streets,
        "structures": struct,
        "buildings": bld,
        "plan_pipe_ends": ends,
        "_street_note": "Road centreline inside the combined catchments, from the "
                        "OSM extract. The copy here has no tags, so paths and "
                        "service roads are included and this is an upper bound on "
                        "the length of street a rain line would follow.",
        "polder": {"ha": VESTAMAGER_HA,
                   "ring": [[12.548, 55.618], [12.585, 55.607], [12.612, 55.588],
                            [12.606, 55.571], [12.575, 55.566], [12.548, 55.578],
                            [12.536, 55.596], [12.548, 55.618]],
                   "_note": "Schematic. An indication of position and rough extent, "
                            "not a boundary."},
    }
    p = os.path.join(ROOT, "docs", "data", "architecture.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    log(f"  {len(cats)} catchments, {len(outs)} outfalls, {len(basins)} basins, "
        f"{len(coast)} coast rings")
    for k, v in sorted(totals.items(), key=lambda x: -x[1]["ha"]):
        log(f"    {v['ha']:9,.0f} ha  {v['pe']:9,.0f} pe  {v['n']:4d}  {k}")
    log(f"  wrote {p} ({os.path.getsize(p)/1e6:.2f} MB)")


if __name__ == "__main__":
    main()
