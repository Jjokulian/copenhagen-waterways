#!/usr/bin/env python3
"""Apply hand-judged sheet offsets from the viewer's debug mode.

The seven flood sheets are placed by two different machines: four by image
correlation against a rendered street mask (20-30 m), three by resident-reported
control points refined by correlation (58-91 m).  Neither can see what a person
who knows the city sees at a glance - that a whole sheet sits a block north of
where its streets say it should be.

So viz/index.html has a "Move sheets (debug)" mode: pick a sheet, drag it or
nudge it with the arrow keys, and it reports the shift in metres.  This script
takes that report back:

    scripts/apply_offsets.py offsets.json          # or - to read stdin
    scripts/apply_offsets.py offsets.json --dry-run

The offsets are a pure translation.  A sheet whose scale or rotation is wrong
cannot be fixed this way, and a person dragging cannot honestly judge a 2% scale
error, so nothing here pretends to.  The translation is recorded in the sheet's
record as `manual_offset_m` next to the machine's own error estimate, because a
number a person moved by hand and a number a correlation produced are not the
same kind of number and the file should not flatten them together.

After applying:  scripts/build_viewer_data.py   (reships floodmaps.json)
                 scripts/terraincheck.py        (the agreement figures change)
                 scripts/programme.py           (PROGRAMME.md quotes them)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEOREF = os.path.join(ROOT, "data", "derived", "floodmaps", "_georef.json")


def shift(rec, dlon, dlat):
    """Translate one sheet's bounds and corners. Returns the metres actually moved."""
    b = rec["bounds_wgs84"]
    lat0 = (b["north"] + b["south"]) / 2
    b["west"] += dlon
    b["east"] += dlon
    b["north"] += dlat
    b["south"] += dlat
    rec["corners_for_maplibre"] = [
        [b["west"], b["north"]], [b["east"], b["north"]],
        [b["east"], b["south"]], [b["west"], b["south"]],
    ]
    return (dlon * 111320 * math.cos(math.radians(lat0)), dlat * 110540)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    dry = "--dry-run" in argv[1:]
    if not args:
        print(__doc__)
        return 2

    text = sys.stdin.read() if args[0] == "-" else open(args[0], encoding="utf-8").read()
    offsets = json.loads(text)

    geo = json.load(open(GEOREF, encoding="utf-8"))
    unknown = [k for k in offsets if k not in geo]
    if unknown:
        print("no such sheet(s): " + ", ".join(unknown))
        print("known: " + ", ".join(sorted(geo)))
        return 1

    for k, o in offsets.items():
        rec = geo[k]
        # the viewer reports both; the degrees are authoritative, the metres are
        # for reading, and disagreement between them means a hand-edited file
        dlon, dlat = float(o["dlon"]), float(o["dlat"])
        dx, dy = shift(rec, dlon, dlat)
        if "dx_m" in o and abs(dx - float(o["dx_m"])) > 1.0:
            print(f"  ! {k}: reported {o['dx_m']} m east, degrees say {dx:.1f} m")
        prev = rec.get("manual_offset_m", [0.0, 0.0])
        rec["manual_offset_m"] = [round(prev[0] + dx, 1), round(prev[1] + dy, 1)]
        rec["manual_offset_note"] = (
            "Moved by hand in the viewer's debug mode by someone reading the "
            "streets under the sheet. This is a judgement, not a measurement, "
            "and it replaces no part of the registration error above.")
        print(f"  {k:16} {dx:+7.1f} m E  {dy:+7.1f} m N"
              f"   (cumulative {rec['manual_offset_m'][0]:+.1f}, "
              f"{rec['manual_offset_m'][1]:+.1f})")

    if dry:
        print("\n--dry-run: nothing written")
        return 0

    with open(GEOREF, "w", encoding="utf-8") as f:
        json.dump(geo, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"\nwrote {os.path.relpath(GEOREF, ROOT)}")
    print("now run: scripts/build_viewer_data.py, then scripts/terraincheck.py")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
