#!/usr/bin/env python3
"""Publish the recovered flood model as a dataset other people can load.

Københavns Kommune published its 2012 cloudburst model as seven PDF sheets with the
geospatial metadata removed - no /Measure, no /GPTS, no /Viewport. This project put it
back: depth bands read from the palette, scale from each sheet's own scale bar, position
from an ensemble registration, resident-reported control points, sheet-to-sheet image
alignment and a bundle adjustment over all seven.

That makes this the only public georeferenced copy of the model, and a dataset is more
useful to more people than an argument about it. Everything here loads directly in QGIS:
a PNG carrying the depth bands, a world file placing it, and a .prj naming the CRS.

Output: docs/data/flood2012/

Usage:  python3 scripts/export_flood.py
"""
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, read_json

SRC = os.path.join(DERIVED, "floodmaps")
DEST = os.path.join(ROOT, "docs", "data", "flood2012")
WGS84_PRJ = ('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],'
             'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]')

BANDS = [(1, "0.05-0.1 m"), (2, "0.1-0.2 m"), (3, "0.2-0.5 m"),
         (4, "0.5-1 m"), (5, "1-2 m"), (6, "over 2 m")]


def main():
    os.makedirs(DEST, exist_ok=True)
    geo = read_json(os.path.join(SRC, "_georef.json"))
    sheets = read_json(os.path.join(SRC, "_sheets.json"))
    align = None
    p = os.path.join(DERIVED, "floodalign.json")
    if os.path.exists(p):
        align = read_json(p)

    manifest = {
        "name": "Copenhagen 2012 cloudburst flood model, georeferenced",
        "what": ("Modelled inundation depth for a 100-year rainfall event on the 2010 "
                 "city, from Københavns Kommune's Skybrudsplan. Recovered from the "
                 "seven published PDF sheets, whose geospatial metadata had been "
                 "stripped, and placed back on the map."),
        "crs": "EPSG:4326",
        "pixel_values": {str(i): lab for i, lab in BANDS},
        "pixel_value_0": "no modelled flooding, or outside the sheet",
        "provenance": [
            "Depth bands read by exact match against the printed legend palette.",
            "Scale from each sheet's own scale bar, via the PDF text layer.",
            "Position: an ensemble water cross-correlation for four sheets; control "
            "points located on a web map by a resident for three; then sheet-to-sheet "
            "image registration on masked gradient images and a bundle adjustment over "
            "all seven together.",
        ],
        "accuracy": ("Mutually consistent to 23 m RMS across overlapping sheets, tied to "
                     "the ground by control points with standard errors of 58-91 m. "
                     "Nørrebro is the exception: no overlapping pair produced a usable "
                     "correlation peak and it has no control points, so it keeps its "
                     "original automatic position and is not known to be consistent "
                     "with the rest."),
        "caveats": [
            "The model is a 2012 calculation of a 2010 scenario. Nordhavn, most of "
            "Ørestad, Sluseholmen and Teglholmen, and much of Refshaleøen have been "
            "built since and are not in it - 344 ha of today's impervious surface, 8.1% "
            "of the city, lies outside every sheet.",
            "The sheets paint depth over lakes and the harbour as well as over land. "
            "Water standing on water is not modelled flooding; filter it against a water "
            "layer if that matters to you.",
            "This is a recovery of a published figure, not a hydraulic model run. Errors "
            "in the recovery are ours, not the city's.",
        ],
        "licence": ("The underlying model is Københavns Kommune's, published as open "
                    "data via opendata.dk. This georeferencing is offered on the same "
                    "terms. Attribute both."),
        "sheets": {},
    }

    for sheet, g in sorted(geo.items()):
        b = g.get("bounds_wgs84")
        if not b:
            continue
        src_png = os.path.join(SRC, f"{sheet}.depth.png")
        if not os.path.exists(src_png):
            log(f"  {sheet}: no depth raster, skipped")
            continue
        shutil.copyfile(src_png, os.path.join(DEST, f"{sheet}.png"))

        from PIL import Image
        w, h = Image.open(src_png).size
        # world file: pixel sizes and the CENTRE of the top-left pixel
        px = (b["east"] - b["west"]) / w
        py = (b["north"] - b["south"]) / h
        with open(os.path.join(DEST, f"{sheet}.pgw"), "w") as f:
            f.write(f"{px:.12f}\n0.0\n0.0\n{-py:.12f}\n"
                    f"{b['west'] + px/2:.10f}\n{b['north'] - py/2:.10f}\n")
        with open(os.path.join(DEST, f"{sheet}.prj"), "w") as f:
            f.write(WGS84_PRJ)

        manifest["sheets"][sheet] = {
            "raster": f"{sheet}.png",
            "world_file": f"{sheet}.pgw",
            "size_px": [w, h],
            "bounds_wgs84": b,
            "m_per_px": g.get("m_per_px_from_scalebar"),
            "method": g.get("method"),
            "standard_error_m": g.get("standard_error_m"),
            "bundle_applied": bool((g.get("bundle") or {}).get("applied")),
        }
        log(f"  {sheet:16} {w}x{h} px  ->  png + pgw + prj")

    if align:
        manifest["bundle_adjustment"] = {
            "pair_rms_m": align.get("pair_rms_m"),
            "pairs_used": len(align.get("pairs") or []),
            "unconstrained": align.get("unconstrained"),
        }
    for extra in ("floodgap.json",):
        s = os.path.join(DERIVED, extra)
        if os.path.exists(s):
            shutil.copyfile(s, os.path.join(DEST, extra))

    with open(os.path.join(DEST, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    readme = f"""# Copenhagen 2012 cloudburst flood model, georeferenced

{manifest['what']}

## How to load it

Open any `<sheet>.png` in QGIS. The matching `.pgw` world file and `.prj` sit beside it,
so it lands in the right place in EPSG:4326 with no further steps.

Pixel values are depth bands, not metres:

| value | depth |
|---|---|
{chr(10).join(f"| {i} | {lab} |" for i, lab in BANDS)}
| 0 | no modelled flooding, or outside the sheet |

## Where it came from

{chr(10).join('- ' + p for p in manifest['provenance'])}

## How accurate it is

{manifest['accuracy']}

## What to be careful of

{chr(10).join('- ' + c for c in manifest['caveats'])}

## Licence

{manifest['licence']}

Method, code and the arguments built on it: https://jjokulian.github.io/copenhagen-waterways/
"""
    with open(os.path.join(DEST, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)
    total = sum(os.path.getsize(os.path.join(DEST, f)) for f in os.listdir(DEST))
    log(f"\nwrote {len(manifest['sheets'])} sheets to docs/data/flood2012/ "
        f"({total/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
