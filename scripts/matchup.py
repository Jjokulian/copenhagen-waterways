#!/usr/bin/env python3
"""Pair each Danish light cast with the satellite pixel over it, same day.

Two instruments measure how far light gets into the water. A ship lowers a PAR
sensor and fits an exponential down the profile, giving Kd over the whole
photosynthetic band. A satellite measures reflectance and retrieves Kd at 490 nm.
Different bands, different physics, different failure modes, and no shared
processing anywhere - which is what makes the pair worth building.

This produces one row per (station, day) where both exist: the ship's Kd, the
median satellite Kd490 in the 3x3 pixel window over the station, and how many of
those nine pixels were valid. Nothing is aggregated over time. The output is a
paired-measurement table, and the questions it answers are about individual
observations: how far apart are two real measurements of the same water on the
same day, and which days have both at all.

What the pairing showed when first run (1997-2025, inner Danish box):

  48,993 casts, 421 stations        6,879 same-day pairs (14%)
  ship Kd(PAR)  median 0.270        satellite Kd(490) median 0.209
  ratio 490/PAR median 0.769, but p10-p90 spans 0.566-1.188 - a factor of 2.1,
    so no single conversion factor carries an individual observation
  rank agreement 0.60; within-station, median 0.49 across 69 stations

**The days that match are not a random sample of days.** Matched casts have
median Kd 0.270; all casts in the same months have 0.330. The satellite sees the
clearer water, because cloud and turbidity share causes (wind, resuspension,
runoff) and because the retrieval itself fails in optically complex water. The
missingness is correlated with the variable being measured, which is the one
condition under which dropping the missing rows is not safe.

**Do not compute a trend from this.** Doing so anyway, across subsets that are
each defensible, gives -3.48 to +20.45 percent per decade and both signs. The
ship record's station composition changes (41 of 421 stations span it) and the
satellite's constellation changes (0.1M valid pixels in 1997, 4.4M by 2018);
correcting the ship record for station turnover alone moves it from +18.16 to
+1.55. The number is a property of what got sampled.

Reads   data/raw/oda/lys.csv.gz, data/raw/cmems/grid/transp__inner__YYYY.nc
Writes  data/derived/matchups.json

Usage:  ~/.venvs/marine/bin/python scripts/matchup.py
"""
import collections
import csv
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, log, write_json

BOX = (9.25, 54.4, 13.2, 58.0)
MIN_FIT = 0.9


def num(x):
    """ODA writes decimals with a Danish comma. float() on '8,47' raises, and a
    bare except returns None - so coordinates and Kd both vanish silently and the
    file looks empty rather than broken. Replace the separator first, always."""
    x = (x or "").strip().replace(",", ".")
    try:
        return float(x)
    except ValueError:
        return None


def read_casts():
    """One row per cast. The file is one row per depth, all sharing the cast's Kd."""
    w, s, e, n = BOX
    casts = {}
    with gzip.open(os.path.join(RAW, "oda", "lys.csv.gz"), "rt",
                   encoding="iso-8859-1") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            kd = num(row.get("LyssvaekkelsesKoefficient"))
            d = (row.get("Dato") or "").strip()
            if kd is None or kd <= 0 or len(d) < 8 or not d[:8].isdigit():
                continue
            fit = num(row.get("KorrelationsKoefficient"))
            if fit is None or fit < MIN_FIT:
                continue
            la, lo = num(row.get("Bredde")), num(row.get("Længde"))
            if la is None or lo is None or not (w <= lo <= e and s <= la <= n):
                continue
            casts[(row["ObservationsStedNr"], d, row.get("UndersøgelseNr") or "")] = {
                "st": row["ObservationsStedNr"],
                "name": (row.get("ObservationsStedNavn") or "").strip(),
                "date": d, "lat": la, "lon": lo, "kd_par": kd, "fit": fit,
            }
    return list(casts.values())


def main():
    import numpy as np
    import xarray as xr

    casts = read_casts()
    log(f"  {len(casts):,} casts in box, fit >= {MIN_FIT}, "
        f"{len({c['st'] for c in casts})} stations")
    by_year = collections.defaultdict(list)
    for c in casts:
        by_year[c["date"][:4]].append(c)

    out = []
    for y in sorted(by_year):
        f = os.path.join(RAW, "cmems", "grid", f"transp__inner__{y}.nc")
        if not os.path.exists(f):
            continue
        d = xr.open_dataset(f)
        lat, lon = d.latitude.values, d.longitude.values
        tidx = {str(t)[:10].replace("-", ""): i for i, t in enumerate(d.time.values)}
        a = d["KD490"].values
        hit = 0
        for c in by_year[y]:
            k = tidx.get(c["date"])
            if k is None:
                continue
            i = int(np.clip(np.searchsorted(lat, c["lat"]), 0, len(lat) - 1))
            j = int(np.clip(np.searchsorted(lon, c["lon"]), 0, len(lon) - 1))
            win = a[k, max(0, i - 1):i + 2, max(0, j - 1):j + 2]
            v = win[np.isfinite(win)]
            if v.size == 0:
                continue
            out.append({"st": c["st"], "name": c["name"], "date": c["date"],
                        "lat": c["lat"], "lon": c["lon"],
                        "kd_par": c["kd_par"], "kd490": round(float(np.median(v)), 4),
                        "spread490": round(float(v.max() - v.min()), 4),
                        "n_px": int(v.size)})
            hit += 1
        d.close()
        log(f"    {y}  casts {len(by_year[y]):5d}  matched {hit:5d} "
            f"({100 * hit / max(len(by_year[y]), 1):4.1f}%)")

    p = os.path.join(DERIVED, "matchups.json")
    write_json(p, {
        "_what": "One row per (station, day) where a Danish PAR light cast and a "
                 "satellite Kd490 retrieval both exist. kd_par is broadband, "
                 "kd490 is at 490 nm - they are different quantities and are NOT "
                 "expected to be equal.",
        "_warning": "The matched days are a biased sample: matched casts are "
                    "clearer than unmatched ones in the same months (median Kd "
                    "0.270 vs 0.330), because cloud and turbidity share causes and "
                    "the retrieval fails in complex water. Do not compute trends "
                    "from this table - see the module docstring.",
        "box": BOX, "min_fit": MIN_FIT, "n": len(out), "rows": out})
    log(f"\n  wrote {p}: {len(out):,} pairs, "
        f"{len({r['st'] for r in out})} stations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
