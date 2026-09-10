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
from figures import provenance

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
    nogeom = 0          # counted, so the provenance can say what it dropped
    for f in d["features"]:
        g = f.get("geometry") or {}
        parts = g.get("coordinates") or []
        if g.get("type") == "LineString":
            parts = [parts]
        elif g.get("type") != "MultiLineString":
            nogeom += 1
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
    # What each figure counted as the same thing, written by the code that did
    # the counting. Three published figures for this quantity disagreed and all
    # rested on the same layer and the same graph; they differed only here, in
    # which typologies were treated as one class. So the class is recorded, and
    # so are the other defensible classes and what each would have given.
    mix = by.get("mix", 0.0)
    total = surface + pipe + other
    nsurf = sum(n[k] for k in SURFACE)
    npipe = sum(n[k] for k in PIPE)
    nall = sum(n.values()) + nogeom     # every feature in the layer
    out["features_in_layer"] = nall
    out["features_without_line_geometry"] = nogeom
    out["mix_km"] = round(mix, 1)
    out["surface_plus_mix_km"] = round(surface + mix, 1)
    alt = [("surface only: Skybrudsveje, Groenne veje, Forsinkelsesveje",
            round(surface, 1)),
           ("surface plus mixed alignment", round(surface + mix, 1)),
           ("every alignment in the layer, pipe included", round(total, 1))]
    code = "scripts/conveyance.py:main"
    out["_provenance"] = {
        "surface_km": provenance(
            counts_as="an alignment whose typologi is Skybrudsveje, Groenne veje "
                      "or Forsinkelsesveje - water carried where a person can see "
                      "it. 'mix' is NOT counted: it carries water on the surface "
                      "only in part, and nothing in the layer says which part.",
            # the formula is the literal code, so it is written as code: its two
            # constants are km per degree, a spherical approximation, not claims
            calculation="sum of segment lengths over every LineString of those "
                        "features, each segment `hypot(dlon * 111.320 * cos(lat), "
                        "dlat * 110.574)` km",
            code=code, unit="km", n_in=nall, n_used=nsurf,
            excluded=[("feature with no line geometry - nothing to measure", nogeom), ("typologi 'mix' - surface only in part", n.get("mix", 0)),
                      ("typologi 'Skybrudsledning' - pipe, counted separately", npipe)],
            alternatives=alt),
        "surface_plus_mix_km": provenance(
            counts_as="the surface typologies AND 'mix' - every alignment that "
                      "could carry water on the surface for some of its length",
            calculation="surface_km + the summed length of typologi 'mix'",
            code=code, unit="km", n_in=nall, n_used=nsurf + n.get("mix", 0),
            excluded=[("feature with no line geometry - nothing to measure", nogeom), ("typologi 'Skybrudsledning' - pipe", npipe)],
            alternatives=alt),
        "pipe_km": provenance(
            counts_as="an alignment whose typologi is Skybrudsledning - water in "
                      "a pipe, out of sight",
            calculation="sum of segment lengths over those features, as above",
            code=code, unit="km", n_in=nall, n_used=npipe,
            excluded=[("feature with no line geometry - nothing to measure", nogeom), ("every surface and mixed typologi", nall - npipe)]),
        "surface_to_pipe": provenance(
            counts_as="the surface-only class against the pipe class - the ratio "
                      "changes with the surface definition, so it carries it",
            calculation="surface_km / pipe_km",
            code=code, n_in=nall, n_used=nsurf + npipe,
            alternatives=[("surface only / pipe", round(surface / pipe, 2)),
                          ("surface plus mix / pipe", round((surface + mix) / pipe, 2))]),
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
