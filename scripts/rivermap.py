#!/usr/bin/env python3
"""Render docs/river_map.png - the same geography as the flood-gap map, asked a
different question.

FLOOD_GAP.md asks: is there a cloudburst work near the modelled flooding? This asks:
is there a *surface* route near it, or only a pipe?

The premise is that the recovered 2012 flood model is not only a risk map. It is a
survey of where water in Copenhagen wants to go when you stop forcing it into a pipe -
the city's natural drainage, drawn by the terrain, mapped at 10 m. If you were going to
put rainwater rivers anywhere, those are the alignments, and they are already known.

So the map separates the cloudburst plan into two things that are usually counted
together:

  SURFACE  Skybrudsveje, Grønne veje, Forsinkelsesveje, terrain modification -
           conveyance in the open, which can be a river.
  BURIED   Skybrudsledninger and tunnels - conveyance in a pipe, which cannot.

and then highlights the flood paths that have neither within 100 m. Those are the
alignments where a rainwater river is both indicated by the terrain and absent from
the plan.

Usage:  python3 scripts/rivermap.py   (after floodmaps.py autoref)
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import floodgap as fg
from common import DERIVED, RAW, ROOT, log, read_json, write_json

NEAR_M = 100.0
MIN_CORRIDOR_CELLS = 60          # 6,000 m2 - a corridor, not a puddle

# The cloudburst plan, split by whether the water would be visible.
SURFACE_TYPOLOGIES = {"Skybrudsveje", "Grønne veje", "Forsinkelsesveje", "mix"}
BURIED_TYPOLOGIES = {"Skybrudsledning"}


def split_veje(path):
    """Yield ('surface'|'buried', geometry parts) from the cloudburst road layer."""
    surf, bur = [], []
    for f in read_json(path)["features"]:
        g = f.get("geometry")
        if not g:
            continue
        t = f["properties"].get("typologi")
        dst = surf if t in SURFACE_TYPOLOGIES else (bur if t in BURIED_TYPOLOGIES else None)
        if dst is None:
            continue
        c = g["coordinates"]
        if g["type"] == "LineString":
            dst.append(("line", c))
        elif g["type"] == "MultiLineString":
            dst += [("line", ln) for ln in c]
    return surf, bur


def main():
    np, Image = fg._np(), fg._pil()
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
    grid = fg.Grid(west, south, east, north)
    depth, used = fg.load_flood(grid, sheets, geo, np, Image)

    import floodreg
    water = fg.rasterise(grid, [("poly", r) for r in floodreg.water_rings()], Image, np)
    flooded = (depth >= fg.FLOOD_DEPTH_MIN) & ~water
    cell_m2 = fg.CELL * fg.CELL
    total = int(flooded.sum())
    log(f"grid {grid.W}x{grid.H}, flood paths {total*cell_m2/1e6:.2f} km² "
        f"from {len(good)} sheets: {', '.join(sorted(used))}")

    # --- the plan, split by whether the water would be visible
    surf_g, bur_g = split_veje(os.path.join(RAW, "skp_veje_tunneller_kk.geojson"))
    surf_g += list(fg.iter_geoms(os.path.join(RAW, "skp_terraenaend.geojson")))
    surface = fg.rasterise(grid, surf_g, Image, np, width=2)
    buried = fg.rasterise(grid, bur_g, Image, np, width=2)
    basins = fg.rasterise(
        grid, list(fg.iter_geoms(os.path.join(RAW, "skp_bassiner_pladser_kk.geojson"))),
        Image, np)
    log(f"  surface conveyance {len(surf_g):>5} parts   buried {len(bur_g):>5} parts")

    # --- combined-sewer catchments, because that is where the overflow risk is
    comb = [("poly", r) for f in read_json(
                os.path.join(RAW, "sp_kloakoplande.geojson"))["features"]
            if (f["properties"].get("kloaksystem_status") or "") == "Fælleskloakeret"
            and f.get("geometry")
            for r in ([f["geometry"]["coordinates"][0][0]]
                      if f["geometry"]["type"] == "MultiPolygon"
                      else [f["geometry"]["coordinates"][0]])]
    combined = fg.rasterise(grid, comb, Image, np, width=1)

    log("computing distance transforms ...")
    d_surf = fg.distance_transform(surface, np)
    d_bur = fg.distance_transform(buried, np)
    d_bas = fg.distance_transform(basins, np)

    near_s = flooded & (d_surf <= NEAR_M)
    near_b = flooded & (d_bur <= NEAR_M)
    near_any = flooded & ((d_surf <= NEAR_M) | (d_bur <= NEAR_M) | (d_bas <= NEAR_M))
    gap = flooded & ~near_any

    pct = lambda m: round(float(int(m.sum())) / total * 100, 1) if total else 0.0
    res = {
        "generated_from": sorted(used),
        "note": ("The flood model is read here as a survey of the city's natural surface "
                 "drainage. Cells are the 10 m grid of floodgap.py; 'near' is within "
                 f"{NEAR_M:.0f} m."),
        "flood_path_km2": round(total * cell_m2 / 1e6, 3),
        "near_surface_conveyance_pct": pct(near_s),
        "near_buried_conveyance_pct": pct(near_b),
        "near_anything_pct": pct(near_any),
        "no_surface_route_pct": pct(flooded & ~near_s),
        "gap_pct": pct(gap),
        "gap_km2": round(float(int(gap.sum())) * cell_m2 / 1e6, 3),
        "corridors": [],
    }
    log(f"  flood path within {NEAR_M:.0f} m of surface conveyance : "
        f"{res['near_surface_conveyance_pct']:.1f}%")
    log(f"  ...of a buried pipe                          : "
        f"{res['near_buried_conveyance_pct']:.1f}%")
    log(f"  ...of anything at all                        : {res['near_anything_pct']:.1f}%")
    log(f"  NO surface route within {NEAR_M:.0f} m               : "
        f"{res['no_surface_route_pct']:.1f}%")

    # --- the corridors: where a river is indicated and absent
    deep = depth >= 4          # >= 0.5 m; a real flow path, not a wet street
    cand = deep & ~water & ~near_s
    clusters = fg.label_clusters(cand, np, MIN_CORRIDOR_CELLS)
    clusters.sort(key=len, reverse=True)
    log(f"  {len(clusters)} corridor candidates >= {MIN_CORRIDOR_CELLS*cell_m2:,.0f} m²")
    # the count of every candidate, stored: "corridors" below lists only the largest
    res["corridor_candidates"] = len(clusters)
    for cells in clusters[:14]:
        ys = [c[0] for c in cells]
        xs = [c[1] for c in cells]
        cy, cx = sum(ys) / len(ys), sum(xs) / len(xs)
        lon, lat = grid.lonlat(cx, cy)
        # elongation: a corridor is long and thin, a pond is round
        span_y = (max(ys) - min(ys) + 1) * fg.CELL
        span_x = (max(xs) - min(xs) + 1) * fg.CELL
        res["corridors"].append({
            "lon": round(lon, 6), "lat": round(lat, 6),
            "area_m2": len(cells) * cell_m2,
            "length_m": round(max(span_x, span_y)),
            "elongation": round(max(span_x, span_y) / max(1.0, min(span_x, span_y)), 1),
            "in_combined_catchment": bool(combined[int(cy), int(cx)]),
        })
    write_json(os.path.join(DERIVED, "rivermap.json"), res)

    # ----------------------------------------------------------------- render
    from PIL import ImageDraw
    H, W = depth.shape
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (14, 18, 24)
    img[combined] = (46, 32, 34)                    # combined-sewer catchment wash
    img[water] = (24, 52, 84)
    img[basins] = (58, 62, 70)
    img[buried] = (120, 96, 104)                    # a pipe: the water is not visible
    img[surface] = (52, 148, 110)                   # a surface route: it could be a river
    for i in range(2, 7):
        img[(depth == i) & ~water] = fg.BAND_RGB[i]
    # dilate the flood paths by one cell so they read against the dense plan
    fl = flooded.copy()
    fl[1:] |= flooded[:-1]; fl[:-1] |= flooded[1:]
    fl[:, 1:] |= flooded[:, :-1]; fl[:, :-1] |= flooded[:, 1:]
    img[fl & ~flooded & ~water] = (96, 150, 194)
    img[gap] = (255, 138, 92)                       # indicated, and nothing there

    im = Image.fromarray(img, "RGB")
    dr = ImageDraw.Draw(im)
    for c in res["corridors"]:
        x, y = grid.xy(c["lon"], c["lat"])
        r = max(11.0, math.sqrt(c["area_m2"]) / grid.cell)
        dr.ellipse([x - r, y - r, x + r, y + r], outline=(120, 255, 200), width=3)

    scale = 1500 / im.width
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    dr = ImageDraw.Draw(im)
    dr.rectangle([0, 0, 560, 172], fill=(14, 18, 24))
    dr.text((12, 10), "Where the water wants to go, and whether the plan lets it",
            fill=(232, 238, 244))
    dr.text((12, 26), "2012 flood model (recovered) vs the cloudburst plan, split by "
                      "surface or pipe", fill=(150, 162, 172))
    for i, (col, t) in enumerate([
            ((154, 199, 224), "modelled flood path - the natural drainage"),
            ((52, 148, 110), "planned SURFACE route (could carry a river)"),
            ((120, 96, 104), "planned PIPE (water stays buried)"),
            ((58, 62, 70), "basin or retention square"),
            ((46, 32, 34), "combined-sewer catchment"),
            ((255, 138, 92), f"flood path with no route within {NEAR_M:.0f} m"),
            ((120, 255, 200), "corridor candidate: deep, and no surface route")]):
        y = 52 + i * 17
        dr.rectangle([14, y, 30, y + 11], fill=col)
        dr.text((40, y - 1), t, fill=(184, 194, 204))
    dst = os.path.join(ROOT, "docs", "river_map.png")
    im.save(dst, optimize=True)
    log(f"wrote docs/river_map.png  ({im.width}x{im.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
