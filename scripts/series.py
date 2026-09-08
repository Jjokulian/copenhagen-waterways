#!/usr/bin/env python3
"""Per-area monthly series, several variables, so the map can be interrogated.

A map that shows where data exists and will not let you look at it is opaque. The
question a reader actually has is comparative — put oxygen against chlorophyll here,
or light against temperature — and answering it needs the series themselves, not a
coverage flag.

The CTD extract is long-format: one row per parameter per depth per cast, with the
parameter named in its own column. That makes several variables available from one
pass, and it makes depth available, which matters more than it looks. **Oxygen at
the surface and oxygen near the bed are different variables**, and the entire
iltsvind question is about the second. Splitting them is not a refinement; conflating
them would make the series meaningless.

Depth split: surface is the shallowest quarter of a cast, bed is the deepest quarter,
computed per cast rather than at a fixed metre, because a fixed metre is the surface
in one place and the bottom in another.

Two Danish-format traps, both silent, both hit already in this project:
  * decimals use a comma, so float("8,47") raises and a bare except turns the whole
    column into None;
  * every field is quoted, so a fast split leaves '"19890830"' and the date never
    parses. Rows whose field count does not match the header are skipped rather than
    read at shifted offsets.

Reads   data/raw/oda/ctd.csv.gz, data/raw/national/marin_overordnet.geojson
Writes  docs/data/areas/series.json
"""
import collections
import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json
from cube import NMON, load_polygons, locate, mon, num

# parameter -> (key, label, unit, split by depth?)
WANT = {
    "Oxygen indhold": ("oxy", "Oxygen", "mg/l", True),
    "Temperatur": ("temp", "Temperature", "°C", True),
    "Salinitet": ("sal", "Salinity", "‰", True),
    "Fluorescens": ("fluo", "Fluorescence (chlorophyll proxy)", "rel", False),
    "Oxygenmætning": ("oxysat", "Oxygen saturation", "%", True),
}


def uq(v):
    v = v.strip()
    return v[1:-1] if len(v) > 1 and v[0] == '"' and v[-1] == '"' else v


def main():
    """Stream one cast at a time.

    The first version of this held every cast in a dict and then processed them,
    which reached 541 MB against 737 MB free and took the machine down with it.
    Rows for one cast are contiguous in the file - checked, 61,534 cast-runs over
    six million rows with none reopened after closing - so a cast can be completed
    and discarded as its key changes, and peak memory becomes one cast plus the
    output grid. The contiguity assumption is asserted rather than trusted: a key
    that reappears after closing is counted and reported.
    """
    polys = load_polygons()
    n = len(polys)
    acc = collections.defaultdict(list)
    pos, where = {}, {}
    closed = set()
    reopened = skipped = ncast = 0
    cur, rows = None, []

    def flush():
        nonlocal rows
        if not rows or cur is None:
            rows = []
            return
        st, m = cur[0], cur[2]
        k = where.get(st)
        if k is None and st in pos:
            k = locate(polys, *pos[st])
            where[st] = k
        if k is not None:
            depths = sorted({d for d, _, _ in rows})
            lo_cut = depths[0] + (depths[-1] - depths[0]) * 0.25
            hi_cut = depths[-1] - (depths[-1] - depths[0]) * 0.25
            for d, par, v in rows:
                key, _lab, _u, split = WANT[par]
                if not split:
                    acc[(key, k, m)].append(v)
                    continue
                if d <= lo_cut:
                    acc[(key + "_surf", k, m)].append(v)
                if d >= hi_cut:
                    acc[(key + "_bed", k, m)].append(v)
        rows = []

    p = os.path.join("data", "raw", "oda", "ctd.csv.gz")
    with gzip.open(p, "rt", encoding="iso-8859-1") as fh:
        hdr = fh.readline().rstrip("\r\n").split(";")
        ix = {c: i for i, c in enumerate(hdr)}
        need = ("ObservationsStedNr", "Dato", "Parameter", "Dybde (m)",
                "KorrigeretResultat", "OriginalResultat", "Længde", "Bredde")
        if any(c not in ix for c in need):
            log("  CTD columns missing")
            return 1
        nc = len(hdr)
        for line in fh:
            f = line.rstrip("\r\n").split(";")
            if len(f) != nc:
                skipped += 1
                continue
            st, dat = uq(f[ix["ObservationsStedNr"]]), uq(f[ix["Dato"]])
            if (st, dat) != (cur[0], cur[1]) if cur else True:
                flush()
                if (st, dat) in closed:
                    reopened += 1
                closed.add((st, dat))
                m = mon(dat)
                cur = (st, dat, m)
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
            if v is None or d is None:
                continue
            rows.append((d, par, v))
    flush()
    log(f"  {ncast:,} casts, {len(pos):,} stations, {skipped:,} rows skipped"
        + (f", {reopened:,} casts REOPENED (contiguity broken)" if reopened else ""))
    log(f"  {sum(1 for v in where.values() if v is not None):,} stations placed")

    series, meta = {}, []
    keys = sorted({k for k, _, _ in acc})
    for key in keys:
        col = [None] * (n * NMON)
        filled = 0
        for (kk, a, m), vals in acc.items():
            if kk != key:
                continue
            vals.sort()
            col[a * NMON + m] = round(vals[len(vals) // 2], 3)
            filled += 1
        series[key] = col
        base = key.split("_")[0]
        lab = next(v[1] for v in WANT.values() if v[0] == base)
        unit = next(v[2] for v in WANT.values() if v[0] == base)
        depth = ("near the bed" if key.endswith("_bed")
                 else "near the surface" if key.endswith("_surf") else "whole cast")
        meta.append({"key": key, "label": lab, "unit": unit, "depth": depth,
                     "filled": filled})
        log(f"    {key:12} {filled:,} area-months")

    write_json(os.path.join(ROOT, "docs", "data", "areas", "series.json"),
               {"_what": "Monthly median per water body per variable, from the ODA "
                         "CTD extract. Arrays are area-major: index = area * months "
                         "+ month, null where nothing was measured.",
                "_depth": "Variables ending _surf are the shallowest quarter of each "
                          "cast and _bed the deepest quarter, computed per cast. A "
                          "fixed metre would be the surface in one place and the "
                          "bottom in another.",
                "_missing": "Nitrogen and phosphorus are not here. They live in "
                            "ODA's vandkemi topic, which this project has not "
                            "extracted, so the comparison a reader most wants - "
                            "nutrients against oxygen - cannot yet be made.",
                "months": NMON, "variables": meta, "series": series})
    log("  wrote docs/data/areas/series.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
