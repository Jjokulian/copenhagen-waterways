#!/usr/bin/env python3
"""How wrong is a water-body figure computed from n stations?

The disagreement between stations inside one water body is not merely evidence that
a basket is badly drawn. It is the **error term of an extrapolation**, and it can be
measured rather than assumed: take n of the stations that measured in a given month,
average them, and compare that to what all of them together say. Repeat over every
month and every subset. The result is an error-against-n curve, per variable, per
place — and it says where the extrapolation breaks instead of whether it does.

That is `X14` answered retrospectively. The proposal was to buy forty sensors to find
out whether one station can stand for a water body; for the variables the CTD record
already carries, the answer is in the record.

Method, and its honest limit. For each month where k stations measured, and each
n from 1 to k-1, every n-subset (sampled, not exhaustive, above a few) gives a mean;
the error is that mean minus the k-station mean. The k-station mean is a stand-in for
the truth and is itself only an estimate — so these curves are a **lower bound on the
error**, because the target they are measured against carries error of its own. Where
a curve is already alarming at n=1, that conclusion is safe; where it looks
acceptable, it may not be.

Peak memory: the station-month arrays, a few hundred thousand points at eight bytes,
plus per-month grouping. Bounded by the extract.

Reads   docs/data/areas/stations_series.{json,bin}, station_waterbody_overlay.json
Writes  docs/data/areas/extrapolation.json
"""
import array
import collections
import itertools
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json

D = os.path.join(ROOT, "docs", "data", "areas")
MIN_STATIONS = 4          # below this there is no curve to draw
MIN_MONTHS = 12
MAX_SUBSETS = 60          # per (month, n); exhaustive below this


def load():
    meta = json.load(open(os.path.join(D, "stations_series.json"), encoding="utf-8"))
    blob = open(os.path.join(D, "stations_series.bin"), "rb").read()
    ov = json.load(open(os.path.join(D, "station_waterbody_overlay.json"),
                        encoding="utf-8"))
    out = {}
    for v in meta["variables"]:
        n, o = v["n"], v["offset"]
        si = array.array("H"); si.frombytes(blob[o:o + 2 * n])
        mo = array.array("H"); mo.frombytes(blob[o + 2 * n:o + 4 * n])
        va = array.array("f"); va.frombytes(blob[o + 4 * n:o + 8 * n])
        out[v["key"]] = (si, mo, va, v)
    return meta, ov, out


def curve(groups, rng):
    """errors by n, pooled over months."""
    err = collections.defaultdict(list)
    for vals in groups:
        k = len(vals)
        full = sum(vals) / k
        for n in range(1, k):
            combos = list(itertools.combinations(range(k), n))
            if len(combos) > MAX_SUBSETS:
                combos = [tuple(rng.sample(range(k), n)) for _ in range(MAX_SUBSETS)]
            for c in combos:
                err[n].append(sum(vals[i] for i in c) / n - full)
    out = {}
    for n, e in err.items():
        e2 = sorted(abs(x) for x in e)
        rmse = (sum(x * x for x in e) / len(e)) ** 0.5
        out[n] = {"rmse": round(rmse, 3),
                  "p50": round(e2[len(e2) // 2], 3),
                  "p90": round(e2[int(0.9 * len(e2))], 3),
                  "n_est": len(e)}
    return out


def main():
    rng = random.Random(7)
    meta, ov, series = load()
    wb = ov["waterbody_index"]
    areas = ov["areas"]
    results = []
    for key, (si, mo, va, vmeta) in series.items():
        bybody = collections.defaultdict(lambda: collections.defaultdict(list))
        for i in range(len(si)):
            w = wb[si[i]]
            if w >= 0:
                bybody[w][mo[i]].append(va[i])
        for w, months in bybody.items():
            groups = [v for v in months.values() if len(v) >= MIN_STATIONS]
            if len(groups) < MIN_MONTHS:
                continue
            nstat = len({s for s in range(len(si)) if wb[si[s]] == w})
            c = curve(groups, rng)
            if 1 not in c:
                continue
            results.append({
                "variable": key, "label": vmeta["label"], "depth": vmeta["depth"],
                "unit": vmeta["unit"], "area": areas[w],
                "months": len(groups),
                "max_stations": max(len(g) for g in groups),
                "curve": {str(n): c[n] for n in sorted(c)},
            })
            log(f"    {key:12} {areas[w]:10} {len(groups):4d} months, up to "
                f"{max(len(g) for g in groups)} stations, "
                f"n=1 rmse {c[1]['rmse']}")
    results.sort(key=lambda r: -r["curve"]["1"]["rmse"])
    write_json(os.path.join(D, "extrapolation.json"), {
        "_what": "How wrong a water-body figure is when computed from n stations "
                 "instead of all of them. Errors are in the variable's own unit.",
        "_method": "For each month where k>=4 stations measured, every n-subset "
                   "(sampled above 60) gives a mean; the error is that mean minus "
                   "the k-station mean, pooled over months.",
        "_limit": "The k-station mean stands in for the truth and is itself an "
                  "estimate, so these are a LOWER BOUND on the error. A curve that "
                  "already looks bad at n=1 is safe to believe; one that looks "
                  "acceptable may not be.",
        "results": results,
    })
    log(f"\n  {len(results)} variable-area curves -> extrapolation.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
