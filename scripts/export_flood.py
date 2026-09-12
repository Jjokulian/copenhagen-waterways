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
from common import DERIVED, ROOT, log, read_json, write_doc
import live

SRC = os.path.join(DERIVED, "floodmaps")
DEST = os.path.join(ROOT, "docs", "data", "flood2012")
WGS84_PRJ = ('GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],'
             'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]')

BANDS = [(1, "0.05-0.1 m"), (2, "0.1-0.2 m"), (3, "0.2-0.5 m"),
         (4, "0.5-1 m"), (5, "1-2 m"), (6, "over 2 m")]
# sheet keys are file-safe; the README names the districts
SHEET_NAMES = {"amager": "Amager", "bispebjerg": "Bispebjerg", "indre-by": "Indre By",
               "kbhvest": "København Vest", "ladegaardsaaen": "Ladegårdsåen",
               "norrebro": "Nørrebro", "osterbro": "Østerbro"}


def main(argv=()):
    if "--readme" in argv:
        write_readme()
        log("wrote docs/data/flood2012/README.md from its manifest")
        return 0
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

    # Counts and accuracy from the registration itself, so the README states what
    # the files say today rather than what was true when it was first written.
    from floodmaps import BANDS as LEGEND
    manifest["bands"] = [{"value": i, "lo_m": b["lo"], "hi_m": b["hi"]}
                         for i, b in enumerate(LEGEND, start=1)]
    sh = manifest["sheets"]
    manifest["n_sheets"] = len(sh)
    manifest["n_autoref"] = sum(1 for v in sh.values() if (v["method"] or "").startswith("autoref"))
    manifest["n_control_points"] = sum(1 for v in sh.values()
                                       if "control points" in (v["method"] or ""))
    ses = [v["standard_error_m"] for v in sh.values() if v["standard_error_m"] is not None]
    manifest["standard_error_min_m"] = min(ses) if ses else None
    manifest["standard_error_max_m"] = max(ses) if ses else None
    # the manifest's own prose, rebuilt from the same records (it once said four and
    # three where the placement now is the other way round)
    manifest["what"] = manifest["what"].replace("seven published", f"{len(sh)} published")
    manifest["provenance"][2] = (
        f"Position: an ensemble water cross-correlation for {manifest['n_autoref']} sheets; "
        f"control points located on a web map by a resident for "
        f"{manifest['n_control_points']}; then sheet-to-sheet image registration on masked "
        "gradient images and a bundle adjustment over the sheets that overlap usefully.")
    ba = manifest.get("bundle_adjustment") or {}
    manifest["accuracy"] = (
        (f"Mutually consistent to {ba['pair_rms_m']:g} m RMS across overlapping sheets, "
         if ba.get("pair_rms_m") is not None else "")
        + (f"tied to the ground by control points with standard errors of "
           f"{min(ses):g}-{max(ses):g} m. " if ses else "")
        + ("".join(f"{n.capitalize()} is not tied to the other sheets by the bundle "
                   "adjustment and rests on its own control points. "
                   for n in (ba.get("unconstrained") or []))))
    with open(os.path.join(DEST, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    write_readme()
    total = sum(os.path.getsize(os.path.join(DEST, f)) for f in os.listdir(DEST))
    log(f"\nwrote {len(manifest['sheets'])} sheets to docs/data/flood2012/ "
        f"({total/1e6:.1f} MB)")
    return 0



def _reading(sid, value, phrase):
    """A number read from a pinned document, refused unless the pinned copy holds the
    phrase (tags set aside and entities read, as the claims register compares it).
    Each reading gets its own phrase: two readings with one phrase would share an id."""
    import claims as _claims
    d = _claims.load()[0]
    if _claims._flat(phrase) not in _claims._flat(_claims.pin_text(d, sid)):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    return live._mk(value, ["reading", sid, "phrase", phrase, _claims._meta(d, sid)])


def write_readme():
    """The README, from the manifest read live: every count and error links to it, and
    every assertion is a checked claim registered in data/manual/claims.d/w3-dq.json
    with what it rests on (LIVE_NUMBERS.md section 11). What it once said and could not
    justify is in docs/ARCHIVE.md, not here.

    The rasters hold legend colours, not band numbers: floodmaps.py writes each band's
    RGB with full opacity where a band was read and transparent black elsewhere, so the
    table maps colour to depth band."""
    from floodmaps import BANDS as LEGEND
    C = live.claim
    m = live.live_json(os.path.join(DEST, "manifest.json"))
    gap = live.live_json(os.path.join(DERIVED, "floodgap.json"))
    ba = m.get("bundle_adjustment") or {}
    un = list(ba.get("unconstrained") or [])
    if [(b["lo"], b["hi"]) for b in LEGEND] != [(b["lo_m"], b["hi_m"]) for b in m["bands"]]:
        raise SystemExit("the manifest's bands differ from floodmaps.BANDS - rerun the export")
    event = _reading("FLOOD2012-AMAGER", 100, "ved en 100 års hændelse i 2010")
    o = []
    w = o.append
    w(f"# {m['name']}\n")
    w(C("C-DQ-F-WHAT", f"Modelled inundation depth at a {event}-year event in 2010, as the "
        "Amager sheet's title names it, from the flood scenarios of Københavns Kommune's "
        "cloudburst plans.") + " " +
      C("C-DQ-F-RECOVERED", f"Recovered from the {m['n_sheets']} published PDF sheets and "
        "placed back on the map.") + "\n")
    w("## How to load it\n")
    w("Open any `<sheet>.png` in QGIS. " +
      C("C-DQ-F-FILES", "Beside it the export writes a `.pgw` world file, holding the pixel "
        "size and the centre of the top-left pixel, and a `.prj` naming `WGS 84`, "
        "`EPSG:4326`.") + "\n")
    w(C("C-DQ-F-COLOURS", "Each pixel is a depth band's legend colour, fully opaque where a "
        "band was read and fully transparent where none was. The colours stand for these "
        "bands:") + "\n")
    w("| colour | depth |")
    w("|---|---|")
    for b, leg in zip(m["bands"], LEGEND):
        hexcode = "#" + "".join("%02x" % c for c in leg["rgb"])
        depth = (f"{b['lo_m']:g}–{b['hi_m']:g} m" if b["hi_m"] is not None
                 else f"over {b['lo_m']:g} m")
        w(f"| `{hexcode}` | {depth} |")
    w("| transparent | no band read |\n")
    w("## Where it came from\n")
    w("- " + C("C-DQ-F-BANDS", "Depth bands read against the printed legend palette."))
    w("- " + C("C-DQ-F-SCALE", "Scale from each sheet's own scale bar, via the PDF text "
               "layer."))
    w("- " + C("C-DQ-F-POSITION", "Position: an ensemble water cross-correlation for "
               f"{m['n_autoref']} sheets; control points reported by a resident for "
               f"{m['n_control_points']}; then sheet-to-sheet image registration on masked "
               "gradient images and a bundle adjustment over the sheets that overlap "
               "usefully.") + "\n")
    w("## How accurate it is\n")
    acc = []
    if ba.get("pair_rms_m") is not None:
        acc.append(f"Mutually consistent to {ba['pair_rms_m']:g} m RMS across overlapping "
                   "sheets")
    if m.get("standard_error_min_m") is not None:
        acc.append(f"tied to the ground by control points with standard errors of "
                   f"{m['standard_error_min_m']:g}–{m['standard_error_max_m']:g} m")
    if acc:
        w(C("C-DQ-F-ACC", ", ".join(acc) + "."))
    if un:
        w(C("C-DQ-F-NORREBRO", f"{', '.join(SHEET_NAMES.get(n, n) for n in un)} "
            + ("is" if len(un) == 1 else "are") + " the exception: no overlapping pair "
            "produced a usable correlation peak, so the bundle adjustment could not tie "
            + ("it" if len(un) == 1 else "them") + " to the rest; "
            + ("its" if len(un) == 1 else "their") + " position rests on "
            + ("its" if len(un) == 1 else "their") + " own control points alone."))
    w("")
    w("## What to be careful of\n")
    w("- " + C("C-DQ-F-YEARS", "The model is a 2012 calculation of a 2010 scenario.") + " "
      + C("C-DQ-F-SINCE", "Anything built after the calculation is not in it."))
    w("- " + C("C-DQ-F-WATER", "The sheets paint depth over open water as well as over land: "
               f"{gap['flooded_over_water_km2']:g} km² of it falls on the open-water polygons "
               "`floodgap.py` checks against. Water standing on water is not modelled "
               "flooding; filter it against a water layer if that matters to you."))
    w("- " + C("C-DQ-F-RECOVERY", "This is a recovery of a published figure, not a hydraulic "
               "model run. Errors in the recovery are ours, not the city's.") + "\n")
    w("## Licence\n")
    w(C("C-DQ-F-LICENCE", "The underlying model is Københavns Kommune's, published as open "
        "data via opendata.dk.") + " " +
      C("C-DQ-F-TERMS", "This georeferencing is offered on the same terms. Attribute both.")
      + "\n")
    w("Method, code and the arguments built on it: "
      "https://jjokulian.github.io/copenhagen-waterways/")
    write_doc(os.path.join(DEST, "README.md"), "\n".join(o) + "\n")

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
