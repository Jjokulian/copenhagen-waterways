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
