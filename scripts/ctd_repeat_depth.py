#!/usr/bin/env python3
"""One streaming pass over ODA ctd.csv.gz (piped from zcat on stdin).

Emits, per station: the deepest sampled depth (a lower bound on the bottom depth,
used only where the depth register maaledybde has none).
Emits, per station-date with two or more survey numbers (UndersoegelsesNr) that
each carry near-bed oxygen: the near-bed oxygen of each cast, computed with the
same rule as scripts/stations_series.py (deepest quarter of the cast's depth range,
median of the oxygen readings there). These are same-day repeat casts: the
closest thing to a replicate measurement the record holds.

Peak memory: one station-date's rows at a time, plus one float per station and a
few floats per replicate station-date. Bounded by the largest single station-date.
Oxygen rows are kept only when Enhed is mg/l (read per row, formats.py rule).
"""
import collections
import json
import os
import statistics
import sys

sys.path.insert(0, "/home/user/projects/copenhagen-waterways/scripts")
from formats import num  # noqa: E402

OUT = sys.argv[1]


def uq(s):
    return s[1:-1] if len(s) >= 2 and s[0] == '"' and s[-1] == '"' else s


def main():
    fh = sys.stdin
    hdr = [uq(c) for c in fh.readline().rstrip("\r\n").split(";")]
    ix = {c: i for i, c in enumerate(hdr)}
    nc = len(hdr)
    iS, iD, iU = ix["ObservationsStedNr"], ix["Dato"], ix["UndersoegelsesNr"]
    iP, iE, iZ = ix["Parameter"], ix["Enhed"], ix["Dybde (m)"]
    iO, iK = ix["OriginalResultat"], ix["KorrigeretResultat"]
    maxdepth = {}
    units = collections.Counter()
    reps = []          # (station, date, [bed oxygen per cast], [dmax per cast])
    nsd = nsd_multi = skipped = reopened = rows = 0
    closed = set()
    cur = None
    casts = collections.defaultdict(lambda: ([], []))   # survey -> (depths, (d, o2))

    def flush():
        nonlocal nsd_multi
        if cur is None or not casts:
            return
        bed, dm = [], []
        for u, (depths, oxy) in casts.items():
            if not oxy or not depths:
                continue
            lo, hi = min(depths), max(depths)
            cut = hi - (hi - lo) * 0.25
            v = [o for d, o in oxy if d >= cut]
            if v:
                bed.append(statistics.median(v))
                dm.append(hi)
        if len(bed) >= 2:
            nsd_multi += 1
            reps.append((cur[0], cur[1], bed, dm))

    for line in fh:
        rows += 1
        f = line.rstrip("\r\n").split(";")
        if len(f) != nc:
            skipped += 1
            continue
        st, dat = uq(f[iS]), uq(f[iD])
        if cur is None or (st, dat) != cur:
            flush()
            casts.clear()
            if (st, dat) in closed:
                reopened += 1
            closed.add((st, dat))
            cur = (st, dat)
            nsd += 1
        d = num(uq(f[iZ]))
        if d is None:
            continue
        if d > maxdepth.get(st, -1.0):
            maxdepth[st] = d
        u = uq(f[iU])
        c = casts[u]
        c[0].append(d)
        if uq(f[iP]) == "Oxygen indhold":
            unit = uq(f[iE])
            units[unit] += 1
            if unit != "mg/l":
                continue
            v = num(uq(f[iK]))
            if v is None:
                v = num(uq(f[iO]))
            if v is not None:
                c[1].append((d, v))
    flush()
    with open(OUT, "w") as fo:
        json.dump({"rows": rows, "skipped_bad_columns": skipped,
                   "station_dates": nsd, "station_dates_reopened": reopened,
                   "station_dates_with_2plus_casts_with_bed_oxygen": nsd_multi,
                   "oxygen_units": dict(units), "max_sampled_depth": maxdepth,
                   "replicates": reps}, fo)
    print(f"rows {rows:,} station-dates {nsd:,} multi {nsd_multi:,} "
          f"reopened {reopened:,} skipped {skipped:,} units {dict(units)}")


main()
