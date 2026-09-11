#!/usr/bin/env python3
"""Facts the landing page states that no other script stores.

The landing page is generated (scripts/pages/landing.py). These few values are the
ones nothing else in the repository computes: the size on disk of the two things
it offers for download, the span of the Gotland Deep record and how much of it lies
under the hypoxia line below the halocline, and how many of the retrofit model's
dimensions are stated conventions rather than measurements.

    python3 scripts/landing_facts.py

Reads viz/, docs/data/flood2012/, docs/data/baltic/gotland.{json,bin} and
docs/data/section3d.json. Writes data/derived/landing_facts.json.
"""
import array
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, ROOT, log, write_json

OUT = os.path.join(DERIVED, "landing_facts.json")
GOT = os.path.join(ROOT, "docs", "data", "baltic")
DEPTH_M = 100.0      # the depth the baltic page shows the Gotland Deep below the halocline
O2_MG_L = 2.0        # the hypoxia line: the lower of the two thresholds DCE's model uses


def dir_mb(rel):
    total = 0
    for dp, _, fs in os.walk(os.path.join(ROOT, rel)):
        for f in fs:
            total += os.path.getsize(os.path.join(dp, f))
    return round(total / 1e6, 1)


def gotland():
    g = json.load(open(os.path.join(GOT, "gotland.json"), encoding="utf-8"))
    T, D = len(g["times"]), len(g["depths"])
    a = array.array("f")
    with open(os.path.join(GOT, "gotland.bin"), "rb") as f:
        a.frombytes(f.read())
    if len(a) != len(g["vars"]) * T * D:
        raise SystemExit("gotland.bin does not match the layout gotland.json declares")
    oxy = g["vars"].index("oxy") * T * D
    deep = [i for i, d in enumerate(g["depths"]) if -d >= DEPTH_M]
    months = all_below = cells = cells_below = 0
    for t in range(T):
        vals = [a[oxy + t * D + i] for i in deep]
        vals = [v for v in vals if not math.isnan(v) and abs(v) < 1e30]
        if not vals:
            continue
        months += 1
        all_below += all(v < O2_MG_L for v in vals)
        cells += len(vals)
        cells_below += sum(v < O2_MG_L for v in vals)
    first, last = g["times"][0], g["times"][-1]
    span = (int(last[:4]) - int(first[:4])) * 12 + int(last[5:7]) - int(first[5:7]) + 1
    return {"first_month": first, "last_month": last, "months": T,
            "months_with_deep_data": months,
            "span_years": round(span / 12, 1),
            "months_all_below_pct": round(100 * all_below / months, 1),
            "cells_below_pct": round(100 * cells_below / cells, 1)}


def main(argv):
    s3d = json.load(open(os.path.join(ROOT, "docs", "data", "section3d.json"), encoding="utf-8"))
    out = {"_what": "Values the landing page states that no other script stores: download "
                    "sizes, the Gotland Deep record against the hypoxia line, and the "
                    "retrofit model's stated dimensions.",
           "params": {"depth_m": DEPTH_M, "o2_mg_l": O2_MG_L},
           "viz_mb": dir_mb("viz"),
           "flood2012_mb": dir_mb(os.path.join("docs", "data", "flood2012")),
           "gotland": gotland(),
           "section3d": {"stated": sum(p.get("kind") == "STATED" for p in s3d["params"]),
                         "total": len(s3d["params"])}}
    write_json(OUT, out)
    log(f"wrote {os.path.relpath(OUT, ROOT)}: {json.dumps({k: v for k, v in out.items() if k != '_what'})}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
