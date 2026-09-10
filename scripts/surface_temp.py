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

THE CORRECTION FACTOR. KorrigeretResultat is exactly OriginalResultat times
KorrektionsFaktor - verified on 199,999 of 199,999 rows carrying all three - so
a wrong factor corrupts the corrected value silently and by construction. The
enum sweep found factors outside 0.5-2.0 in every parameter of this extract: 606
temperature rows, worst 80x; 79 salinity rows, worst 2346x; 124 of 2,601
hydrogen sulphide rows, worst 11,472x. Fluorescence has 156,974 (2.3%) and those
are probably legitimate, since a fluorometer is calibrated against extracted
chlorophyll and rescaling is the whole point - but an 80x temperature is not a
calibration, it is an error.

A physical range check does not catch this. A factor of 0.5 on 18 C gives 9 C,
which is a perfectly ordinary Danish sea temperature and wrong. So the factor
itself is bounded here, generously, and everything rejected is counted.

BUT THE COLUMN MEANS DIFFERENT THINGS PER PARAMETER, and the bound below is only
correct because this script reads temperature and salinity and nothing else.
From the technical instructions:

  Ilt (Kap. 4)          "Faktor: O2-Winkler/O2-elektrode" - the electrochemical
                        sonde is checked against a Winkler iodometric titration
                        on a bottle from 1 m, and if they disagree by more than
                        0.3 mg O2/l the whole profile is multiplied by the ratio.
                        Genuine instrument bias compensation. Where the Winkler
                        bottle fell in a gradient the profile is instead
                        corrected by the MEAN factor from other stations the
                        same day, so some corrected values carry a calibration
                        derived somewhere else entirely.

  Fluorescens (Kap. 2)  NOT bias compensation. The instruction says a
                        fluorescence signal "kan derfor ikke direkte omsattes
                        til en pigment koncentration, selvom mange fabrikater i
                        deres programmer angiver, at udlaesninger er i ug Chl
                        l-1" - the manufacturers' claim is wrong - and that
                        fluorescence per chlorophyll varies biologically, so
                        "et varierende FChl forhold [er] ikke et udtryk for
                        instrument problemer". The factor is a unit conversion
                        plus a live calibration against measured chlorophyll.
                        Its 156,974 rows outside 0.5-2.0, up to 201x, are
                        CORRECT. A bound like the one below would delete good
                        data. Do not reuse this guard on fluorescence.

  CTD T, C, D (Kap. 1)  Calibration coefficients estimated by the manufacturer
                        or the institution, sensors recalibrated at least
                        annually and checked against tank and in-situ
                        references. The correction lives inside the sensor.
                        NO post-hoc multiplicative factor is described at all -
                        so the 606 temperature rows with a factor up to 80x and
                        the 79 salinity rows up to 2346x are not a documented
                        procedure applied badly. They have no basis in the
                        instruction, which is why bounding them is safe here.

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
FACTOR_RANGE = (0.5, 2.0)      # a drift correction; anything else is a fault


def num(s):
    try:
        return float((s or "").replace(",", "."))
    except ValueError:
        return None


def main():
    acc = {}
    rows = kept = dropped = badfactor = 0
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
            k = num(row.get("KorrektionsFaktor"))
            if k is not None and not (FACTOR_RANGE[0] <= k <= FACTOR_RANGE[1]):
                badfactor += 1
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
    log(f"  {badfactor:,} dropped on a correction factor outside "
        f"{FACTOR_RANGE[0]}-{FACTOR_RANGE[1]}")
    log(f"wrote {os.path.relpath(OUT)} "
        f"({os.path.getsize(OUT)/1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
