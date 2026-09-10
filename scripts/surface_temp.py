#!/usr/bin/env python3
"""Surface temperature and salinity per station-day, from the CTD extract.

The two halves of a seasonal question are in different files. Vandkemi carries a
clock time on every row and almost no temperature (1,316 rows in 1.8 million).
CTD carries temperature on a large fraction of its rows, at depth, and no clock
at all - only Dato. So neither file can ask what the water was doing, thermally,
at the hour a bottle was filled. They join on station and date.

This reduces the 448 MB CTD extract to the join key: for every station-day, the
mean of the surface (<=3 m) measurements of temperature and salinity. Written as
a small gzipped CSV so the analysis does not have to re-read the large file, and
so the reduction is inspectable rather than buried inside another script.

Why the mean rather than the shallowest reading: a CTD cast returns many samples
in the top three metres and they differ by hundredths of a degree. The mean is
the more stable estimate and does not depend on which bin the sonde happened to
report first.

Writes data/derived/surface_temp.csv.gz.
"""
import csv
import gzip
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, log

SRC = os.path.join(RAW, "oda", "ctd.csv.gz")
OUT = os.path.join(DERIVED, "surface_temp.csv.gz")
MAX_DEPTH = 3.0
WANT = {"Temperatur": "t", "Salinitet": "s"}
# physically possible in Danish coastal water, generously bounded
RANGE = {"t": (-2.0, 30.0), "s": (0.0, 40.0)}


def num(s):
    try:
        return float((s or "").replace(",", "."))
    except ValueError:
        return None


def main():
    acc = {}
    rows = kept = dropped = 0
    log(f"reading {os.path.relpath(SRC)} (this is the 448 MB one)")
    with gzip.open(SRC, "rb") as fh:
        rd = csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";")
        for row in rd:
            rows += 1
            if rows % 2000000 == 0:
                log(f"  {rows:,} rows, {len(acc):,} station-days held")
            w = WANT.get(row.get("Parameter"))
            if not w:
                continue
            d = num(row.get("Dybde (m)"))
            if d is None or d > MAX_DEPTH or d < 0:
                continue
            v = num(row.get("KorrigeretResultat")) or num(row.get("OriginalResultat"))
            if v is None:
                continue
            lo, hi = RANGE[w]
            if not (lo <= v <= hi):
                dropped += 1
                continue
            date = (row.get("Dato") or "").strip()[:10]
            st = row.get("ObservationsStedNr")
            if not date or not st:
                continue
            a = acc.setdefault((st, date), [0, 0.0, 0, 0.0])
            i = 0 if w == "t" else 2
            a[i] += 1
            a[i + 1] += v
            kept += 1

    os.makedirs(DERIVED, exist_ok=True)
    with gzip.open(OUT, "wt", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["station", "date", "n_t", "temp_c", "n_s", "salinity"])
        for (st, date), a in sorted(acc.items()):
            wr.writerow([st, date, a[0], round(a[1] / a[0], 3) if a[0] else "",
                         a[2], round(a[3] / a[2], 3) if a[2] else ""])
    log(f"\n{rows:,} CTD rows -> {kept:,} surface readings "
        f"-> {len(acc):,} station-days")
    log(f"  {dropped:,} dropped as out of physical range")
    log(f"wrote {os.path.relpath(OUT)} "
        f"({os.path.getsize(OUT)/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
