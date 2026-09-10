#!/usr/bin/env python3
"""How many kilometres of the cloudburst plan carry water on the surface, computed.

Three numbers for one quantity were on this site, none of them derived. The
landing page said 210 km of alignments that could carry a river; PROGRAMME.md and
SOLUTIONS.md said 169 km of surface conveyance against 71 km of pipe; and the
layer they all describe measures 280 km end to end. All three were typed into a
string literal, which is how three of them came to disagree without anyone
noticing - and there are about 348 such literals across the generators.

So this measures it. `skp_veje_tunneller_kk` carries a `typologi` per feature,
and the split that matters is whether the water is on the surface where a person
can see it or in a pipe where they cannot - which is the whole argument
PROGRAMME.md builds on the figure.

  Groenne veje         green roads, surface
  Skybrudsveje         cloudburst roads, surface
  Forsinkelsesveje     retention roads, surface
  Skybrudsledning      cloudburst PIPE
  mix                  reported as its own class rather than assigned

Lengths are summed on the WGS84 geometry with a cosine correction for latitude,
which is accurate to well under a percent over a city and is not the limiting
error here - the classification is.

Writes data/derived/conveyance.json.
"""
import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, ROOT, log, read_json

SRC = os.path.join(RAW, "skp_veje_tunneller_kk.geojson")
OUT = os.path.join(DERIVED, "conveyance.json")
SURFACE = {"Grønne veje", "Skybrudsveje", "Forsinkelsesveje"}
PIPE = {"Skybrudsledning"}


def seg_km(ln):
    t = 0.0
    for a, b in zip(ln, ln[1:]):
        dx = (b[0] - a[0]) * 111.320 * math.cos(math.radians(a[1]))
        dy = (b[1] - a[1]) * 110.574
        t += math.hypot(dx, dy)
    return t


def main():
    d = read_json(SRC)
    by = collections.Counter()
    n = collections.Counter()
    for f in d["features"]:
        g = f.get("geometry") or {}
        parts = g.get("coordinates") or []
        if g.get("type") == "LineString":
            parts = [parts]
        elif g.get("type") != "MultiLineString":
            continue
        t = (f["properties"].get("typologi") or "ukendt").strip()
        by[t] += sum(seg_km(p) for p in parts)
        n[t] += 1

    surface = sum(v for k, v in by.items() if k in SURFACE)
    pipe = sum(v for k, v in by.items() if k in PIPE)
    other = sum(v for k, v in by.items() if k not in SURFACE and k not in PIPE)
    out = {
        "_what": "Cloudburst plan alignment length by typology, measured from "
                 "skp_veje_tunneller_kk rather than quoted.",
        "_why": "Three different figures for this quantity were published on this "
                "site, all of them typed into string literals: 210 km on the "
                "landing page, 169 km in two documents, and a layer that measures "
                "280 km end to end.",
        "features": sum(n.values()),
        "by_typologi": {k: {"km": round(v, 1), "features": n[k]}
                        for k, v in sorted(by.items(), key=lambda x: -x[1])},
        "surface_km": round(surface, 1),
        "pipe_km": round(pipe, 1),
        "unclassified_km": round(other, 1),
        "total_km": round(surface + pipe + other, 1),
        "surface_to_pipe": round(surface / pipe, 2) if pipe else None,
    }
    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    for k, v in out["by_typologi"].items():
        log(f"  {k:<22} {v['km']:>7.1f} km  ({v['features']} features)")
    log(f"\n  surface {out['surface_km']} km, pipe {out['pipe_km']} km, "
        f"other {out['unclassified_km']} km  -> total {out['total_km']} km")
    log(f"  surface:pipe = {out['surface_to_pipe']}")
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
