#!/usr/bin/env python3
"""Per-station monthly series, so the water bodies can be judged rather than assumed.

Every other view in this project aggregates into the 123 official water bodies, and
so inherits them. That is the thing the project keeps objecting to elsewhere: a
basket asserts that what is inside it is alike, and nobody checks. Even a name as
obviously singular as "Roskilde Fjord" is a claim about the water, not a fact about
it.

This emits the same variables keyed by **station** instead of by area, so the
question can be asked the other way round: where do measurements actually differ,
and do the boundaries fall where the differences are? A station carries a position,
so any partition - the official one, or one derived from the data - can be laid over
it afterwards and judged.

Output is packed binary rather than JSON, three parallel arrays per variable:

    station index  uint16
    month index    uint16   (months since 1980-01)
    value          float32

Eight bytes per point, which is about a fifteenth of what the same point costs as
JSON, and it loads into typed arrays without parsing.

Peak memory: one CTD cast at a time plus the accumulated points, which is bounded by
the number of station-months actually measured - a few hundred thousand at eight
bytes. Well inside the budget. The casts are streamed and flushed on key change; the
file is contiguous per cast and a key that reopens is counted and reported.

Reads   data/raw/oda/ctd.csv.gz
Writes  docs/data/areas/stations_series.bin, stations_series.json
"""
import array
import collections
import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json
from cube import NMON, Y0, load_polygons, locate, mon, num
from series import WANT, uq

OUT = os.path.join(ROOT, "docs", "data", "areas")


def main():
    polys = load_polygons()
    pts = collections.defaultdict(lambda: (array.array("H"), array.array("H"),
                                           array.array("f")))
    cell = collections.defaultdict(list)      # (var, station, month) -> values
    pos, skipped, reopened, ncast = {}, 0, 0, 0
    closed = set()
    cur, rows = None, []

    def flush():
        nonlocal rows
        if rows and cur is not None:
            st, m = cur[0], cur[2]
            depths = sorted({d for d, _, _ in rows})
            lo_cut = depths[0] + (depths[-1] - depths[0]) * 0.25
            hi_cut = depths[-1] - (depths[-1] - depths[0]) * 0.25
            for d, par, v in rows:
                key, _l, _u, split = WANT[par]
                if not split:
                    cell[(key, st, m)].append(v)
                    continue
                if d <= lo_cut:
                    cell[(key + "_surf", st, m)].append(v)
                if d >= hi_cut:
                    cell[(key + "_bed", st, m)].append(v)
        rows = []

    p = os.path.join("data", "raw", "oda", "ctd.csv.gz")
    with gzip.open(p, "rt", encoding="iso-8859-1") as fh:
        hdr = fh.readline().rstrip("\r\n").split(";")
        ix = {c: i for i, c in enumerate(hdr)}
        nc = len(hdr)
        for line in fh:
            f = line.rstrip("\r\n").split(";")
            if len(f) != nc:
                skipped += 1
                continue
            st, dat = uq(f[ix["ObservationsStedNr"]]), uq(f[ix["Dato"]])
            if cur is None or (st, dat) != (cur[0], cur[1]):
                flush()
                if (st, dat) in closed:
                    reopened += 1
                closed.add((st, dat))
                cur = (st, dat, mon(dat))
                ncast += 1
            if cur[2] is None:
                continue
            par = uq(f[ix["Parameter"]])
            if par not in WANT:
                continue
            if st not in pos:
                lo, la = num(uq(f[ix["Længde"]])), num(uq(f[ix["Bredde"]]))
                if lo and la and 3 < lo < 16 and 53 < la < 59:
                    pos[st] = (lo, la)
            v = num(uq(f[ix["KorrigeretResultat"]]))
            if v is None:
                v = num(uq(f[ix["OriginalResultat"]]))
            d = num(uq(f[ix["Dybde (m)"]]))
            if v is not None and d is not None:
                rows.append((d, par, v))
    flush()
    log(f"  {ncast:,} casts, {len(pos):,} positioned stations, {skipped:,} skipped"
        + (f", {reopened:,} REOPENED" if reopened else ""))

    # Stations get an index. Which water body a station "is in" is NOT written
    # here: a position is an observation, a water body is a polygon somebody drew,
    # and putting the second inside the first is how a model assumption starts
    # being read as a property of the data. The mapping goes to its own file,
    # labelled as the overlay it is, so it can be drawn over the points or ignored.
    sts = sorted(pos)
    sidx = {s: i for i, s in enumerate(sts)}
    where = [(lambda k: k if k is not None else -1)(locate(polys, *pos[s]))
             for s in sts]
    log(f"  {sum(1 for w in where if w >= 0):,} of {len(sts):,} fall inside some "
        f"water body polygon")

    for (key, st, m), vals in cell.items():
        if st not in sidx:
            continue
        v = sorted(vals)
        q = len(v)
        med = v[q // 2] if q % 2 else (v[q // 2 - 1] + v[q // 2]) / 2
        a, b, c = pts[key]
        a.append(sidx[st])
        b.append(m)
        c.append(med)

    blob = bytearray()
    meta = []
    for key in sorted(pts):
        a, b, c = pts[key]
        off = len(blob)
        blob += a.tobytes() + b.tobytes() + c.tobytes()
        base = key.split("_")[0]
        meta.append({
            "key": key, "n": len(a), "offset": off,
            "label": next(v[1] for v in WANT.values() if v[0] == base),
            "unit": next(v[2] for v in WANT.values() if v[0] == base),
            "depth": ("near the bed" if key.endswith("_bed")
                      else "near the surface" if key.endswith("_surf")
                      else "whole cast"),
        })
        log(f"    {key:12} {len(a):,} station-months")
    with open(os.path.join(OUT, "stations_series.bin"), "wb") as f:
        f.write(bytes(blob))
    write_json(os.path.join(OUT, "stations_series.json"), {
        "_what": "Monthly median per STATION per variable. The unit is a position, "
                 "not a water body, so any partition can be laid over it and "
                 "judged instead of assumed.",
        "_layout": "For each variable in order: n uint16 station indices, then n "
                   "uint16 month indices, then n float32 values, at the stated "
                   "byte offset in stations_series.bin.",
        "year0": Y0, "months": NMON,
        "_not_here": "Which water body each station falls in is deliberately "
                     "absent. That is a model assumption, not a property of the "
                     "measurement, and it lives in station_waterbody_overlay.json.",
        "stations": [{"id": s, "lon": round(pos[s][0], 4),
                      "lat": round(pos[s][1], 4)} for s in sts],
        "variables": meta,
    })
    write_json(os.path.join(OUT, "station_waterbody_overlay.json"), {
        "_what": "Which VP3 water-body polygon each station falls inside, by index "
                 "into 'areas'. -1 means no polygon contains it.",
        "_status": "**This is a model assumption, not data.** The water bodies are "
                   "administrative units drawn for the Water Framework Directive. "
                   "Whether the sea changes where these lines are is an open "
                   "question - see X22 - and it is kept in a separate file so that "
                   "assuming it requires loading it on purpose.",
        "_derived_from": "data/raw/national/marin_overordnet.geojson, "
                         "point-in-polygon against station positions",
        "areas": [p["id"] for p in polys],
        "station_ids": sts,
        "waterbody_index": where,
        "n_inside": sum(1 for w in where if w >= 0),
    })
    log(f"  wrote stations_series.bin ({len(blob)/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
