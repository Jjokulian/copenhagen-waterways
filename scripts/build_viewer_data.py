#!/usr/bin/env python3
"""Compact the raw layers into a bundle a browser can actually load.

data/raw is ~131 MB, most of it two storm-surge dike layers at survey precision.
This keeps only the layers the map draws, only the attributes it shows, and rounds
coordinates to ~1 m. Output: data/derived/viewer/.

Usage:  python3 scripts/build_viewer_data.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, MANUAL, RAW, log, read_json, write_json

PRECISION = 5  # ~1 m at this latitude; plenty for a city-scale map

# layer -> (output name, attributes to carry through)
BUNDLE = {
    "sp_kloakoplande": ("sewer_catchments", ["label", "kloaksystem_status", "kloaksystem_plan",
                                             "renseanlaeg", "befgrad_status", "befgrad_plan"]),
    "skp_bassiner_pladser_kk": ("basins", ["klima_id", "projekt_navn", "typologi", "vandopland",
                                           "forventet_ibrugtagning"]),
    "skp_veje_tunneller_kk": ("tunnels_roads", ["klima_id", "projekt_navn", "typologi", "vandopland"]),
    "skp_skybrudsoplande": ("catchments", None),
    "skp_terraenaend": ("terrain_changes", ["type", "kapacitet", "tvaersnit"]),
    "lar_registreringer": ("lar", None),
    "dp_regnvandsafledning_l": ("rain_lines", ["element", "under_element", "byrumstype"]),
    "vand_oversigtskort": ("water", None),
    "kbh_kysttyper": ("coast", None),
    "vp3_basis_2019_punkt_rbu_udl": ("discharge_points", ["pkt_navn", "bgv_type", "vol_sb",
                                                          "vol_fbas", "komm_navn"]),
    "vp3_basis_2019_punkt_rens_udl": ("treatment_plants", ["pkt_navn", "godk_pe", "rens_sta",
                                                           "komm_navn"]),
}


def round_coords(c, p=PRECISION):
    if isinstance(c, (int, float)):
        return round(c, p)
    return [round_coords(x, p) for x in c]


def slim(path, keep):
    gj = read_json(path)
    out = []
    for f in gj["features"]:
        geom = f.get("geometry")
        if not geom:
            continue
        geom = {"type": geom["type"], "coordinates": round_coords(geom["coordinates"])}
        props = f.get("properties") or {}
        if keep is not None:
            props = {k: props.get(k) for k in keep if props.get(k) not in (None, "")}
        else:
            props = {k: v for k, v in props.items() if v not in (None, "")}
        out.append({"type": "Feature", "properties": props, "geometry": geom})
    return {"type": "FeatureCollection", "features": out}


def main():
    outdir = os.path.join(DERIVED, "viewer")
    os.makedirs(outdir, exist_ok=True)
    index, total = [], 0

    for layer, (out_name, keep) in BUNDLE.items():
        src = os.path.join(RAW, f"{layer}.geojson")
        if not os.path.exists(src):
            log(f"  -- {layer}: not downloaded, skipping")
            continue
        gj = slim(src, keep)
        dst = os.path.join(outdir, f"{out_name}.geojson")
        write_json(dst, gj)
        size = os.path.getsize(dst)
        total += size
        index.append({"name": out_name, "source_layer": layer,
                      "features": len(gj["features"]), "bytes": size})
        log(f"  {out_name:20} {len(gj['features']):>6} features  {size/1e6:>6.2f} MB")

    # the joined registry, if it has been built
    reg = os.path.join(DERIVED, "constructions.geojson")
    if os.path.exists(reg):
        gj = read_json(reg)
        for f in gj["features"]:
            if f.get("geometry"):
                f["geometry"]["coordinates"] = round_coords(f["geometry"]["coordinates"])
        dst = os.path.join(outdir, "constructions.geojson")
        write_json(dst, gj)
        size = os.path.getsize(dst)
        total += size
        index.append({"name": "constructions", "source_layer": "derived",
                      "features": len(gj["features"]), "bytes": size})
        log(f"  {'constructions':20} {len(gj['features']):>6} features  {size/1e6:>6.2f} MB")
    else:
        log("  -- constructions.geojson not built yet (run build_registry.py)")

    # field observations (hand-collected, never overwritten by a fetch)
    obs = os.path.join(MANUAL, "observations.geojson")
    if os.path.exists(obs):
        gj = read_json(obs)
        dst = os.path.join(outdir, "observations.geojson")
        write_json(dst, {"type": "FeatureCollection", "features": gj.get("features", [])})
        n = len(gj.get("features", []))
        total += os.path.getsize(dst)
        index.append({"name": "observations", "source_layer": "manual", "features": n,
                      "bytes": os.path.getsize(dst)})
        log(f"  {'observations':20} {n:>6} features")
    else:
        log("  -- no field observations yet (viz/log.html -> scripts/observations.py import)")

    # georeferenced flood-model overlays, if control points have been set
    geo = os.path.join(DERIVED, "floodmaps", "_georef.json")
    if os.path.exists(geo):
        g = read_json(geo)
        # only ship sheets whose registration was actually accepted
        ok = {k: v for k, v in g.items() if v.get("confident")}
        write_json(os.path.join(outdir, "floodmaps.json"), ok)
        skipped = len(g) - len(ok)
        log(f"  {'floodmaps':20} {len(ok):>6} georeferenced sheet(s)"
            + (f"  ({skipped} not confident, withheld)" if skipped else ""))
        for k in ok:
            src = os.path.join(DERIVED, "floodmaps", f"{k}.depth.png")
            if os.path.exists(src):
                import shutil
                shutil.copy2(src, os.path.join(outdir, f"{k}.depth.png"))
                web = src.replace(".depth.png", ".depth.web.png")
                if os.path.exists(web):
                    shutil.copy2(web, os.path.join(outdir, f"{k}.depth.web.png"))
    else:
        log("  -- no georeferenced flood sheets yet (viz/georef.html -> floodmaps.py georef)")

    gap = os.path.join(DERIVED, "floodgap.json")
    if os.path.exists(gap):
        import shutil
        shutil.copy2(gap, os.path.join(outdir, "floodgap.json"))
        log(f"  {'floodgap':20} analysis copied")

    write_json(os.path.join(outdir, "index.json"), index)
    log(f"\nbundle: {total/1e6:.1f} MB in data/derived/viewer/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
