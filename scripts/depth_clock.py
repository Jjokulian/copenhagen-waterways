#!/usr/bin/env python3
"""Oxygen at depth against the sun, using whatever clock is available.

This is the analysis that section 17 of OPEN_PROBLEMS.md says cannot be done,
written so that it can be done as well as the data currently allows and better
the moment somebody hands in the missing column. It is the worked example of the
three-state contract in IF_YOU_HAVE_THE_DATA.md: the same code, three qualities
of answer, and it says which one it gave.

THE PROBLEM. The water-chemistry extract carries Startklok on 100.0% of its
1,805,827 rows. The CTD extract carries 53,710,760 measurements at depth and no
clock at all - ODA offers no time field for that topic, verified against the
portal's own output-field list. So the archive can time surface chemistry and
cannot time the profile, and hypoxia is a bottom-water phenomenon. Everything
this project has been able to say about the diurnal cycle is about the top three
metres.

THREE CLOCK SOURCES, in descending quality, and the output records which was used
per measurement:

  supplied   data/dropin/ctd_visit_times.csv, station;date;time_utc per cast.
             The real thing. Anyone holding cruise logs or field sheets can
             produce it, and it also CHECKS the borrowed clock below rather
             than merely replacing it.

  borrowed   the same station on the same day in the water-chemistry extract.
             99% of its station-days carry a single Startklok, so a station-day
             is effectively one moment, and 123,866 of 155,182 CTD station-days
             (80%) have such a match. A cast and a bottle on the same visit are
             usually within minutes; where they are not, this is wrong by hours
             and nothing in the data says which.

  none       the remaining 20%. Excluded rather than guessed.

WHAT WOULD FALSIFY THE BORROWING. If supplied times arrive, the difference
between supplied and borrowed is measurable per cast, and this reports its
distribution. A median offset near zero with a tight spread means the borrowed
clock was sound and every conclusion drawn from it stands. A wide spread means
it was not, and the conclusions drawn from it go with it. That check cannot be
run today, which is the honest state of it - the machinery is here so that it
runs on the day the file appears rather than being invented afterwards to
defend a result.

    python3 scripts/depth_clock.py                 borrowed clock
    python3 scripts/depth_clock.py --max-rows N    a quick pass over the head

Writes data/derived/depth_clock.json.
"""
import collections
import csv
import datetime as dt
import gzip
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, ROOT, log
from cube import utm32_to_wgs84
from daylight import solar_elevation, danish_offset, parse_klok

CTD = os.path.join(RAW, "oda", "ctd.csv.gz")
KEMI = os.path.join(RAW, "oda", "kemi.csv.gz")
SUPPLIED = os.path.join(ROOT, "data", "dropin", "ctd_visit_times.csv")
OUT = os.path.join(DERIVED, "depth_clock.json")

O2 = "Oxygen indhold"
FACTOR_RANGE = (0.5, 2.0)       # see surface_temp.py: per-parameter, not general
DEPTH_BANDS = [(0, 3, "0-3 m"), (3, 10, "3-10 m"), (10, 20, "10-20 m"),
               (20, 90, "below 20 m")]
SUN_ORDER = ["night", "twilight", "0-10", "10-20", "20-30", "30+"]


def sun_bin(e):
    return ("night" if e < -6 else "twilight" if e < 0 else "0-10" if e < 10
            else "10-20" if e < 20 else "20-30" if e < 30 else "30+")


def band(d):
    for lo, hi, name in DEPTH_BANDS:
        if lo <= d < hi:
            return name
    return None


def num(s):
    try:
        return float((s or "").replace(",", "."))
    except (ValueError, AttributeError):
        return None


def load_supplied():
    """station;date;time_utc -> {(station, YYYYMMDD): (h, m)}"""
    if not os.path.exists(SUPPLIED):
        return {}
    out = {}
    with open(SUPPLIED, encoding="utf-8", errors="replace") as f:
        sample = f.read(4096)
        f.seek(0)
        delim = ";" if sample.count(";") >= sample.count(",") else ","
        for r in csv.DictReader(f, delimiter=delim):
            r = {(k or "").strip().lower(): v for k, v in r.items()}
            st, d, t = r.get("station"), r.get("date"), r.get("time_utc")
            if not (st and d and t):
                continue
            d = d.replace("-", "").strip()
            t = t.strip()
            try:
                h, mi = int(t[:2]), int(t[3:5]) if len(t) >= 5 else 0
            except ValueError:
                continue
            out[(st.strip(), d)] = (h, mi)
    log(f"  supplied clock: {len(out):,} station-days from "
        f"{os.path.relpath(SUPPLIED, ROOT)}")
    return out


def load_borrowed():
    """The water-chemistry clock, per station-day, where it is unambiguous."""
    seen = {}
    ambiguous = set()
    with gzip.open(KEMI, "rb") as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"),
                                  delimiter=";"):
            k = parse_klok(row.get("Startklok"))
            if not k:
                continue
            key = (row.get("ObservationsStedNr"), (row.get("Startdato") or "").strip())
            if key in seen and seen[key] != k:
                ambiguous.add(key)      # more than one visit: do not guess
            seen[key] = k
    for key in ambiguous:
        seen.pop(key, None)
    log(f"  borrowed clock: {len(seen):,} unambiguous station-days "
        f"({len(ambiguous):,} discarded as multi-visit)")
    return seen


def main(argv):
    maxrows = next((int(a.split("=", 1)[1]) for a in argv
                    if a.startswith("--max-rows=")), 0)
    supplied = load_supplied()
    borrowed = load_borrowed()

    pos = {}
    # station-window cell -> [n, sum]; and the samples, for the fixed effect
    cells = collections.defaultdict(lambda: [0, 0.0])
    samples = []
    src_count = collections.Counter()
    offsets = []                      # supplied minus borrowed, in minutes
    rows = used = 0

    log(f"reading {os.path.relpath(CTD, ROOT)}")
    with gzip.open(CTD, "rb") as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"),
                                  delimiter=";"):
            rows += 1
            if maxrows and rows > maxrows:
                break
            if rows % 10000000 == 0:
                log(f"  {rows:,} rows, {used:,} placed")
            if row.get("Parameter") != O2:
                continue
            d = (row.get("Dato") or "").strip()
            st = row.get("ObservationsStedNr")
            if len(d) != 8 or not st:
                continue
            key = (st, d)
            clk, src = supplied.get(key), "supplied"
            if clk is None:
                clk, src = borrowed.get(key), "borrowed"
            if clk is None:
                src_count["none"] += 1
                continue
            if src == "supplied" and key in borrowed:
                b = borrowed[key]
                offsets.append((clk[0] * 60 + clk[1]) - (b[0] * 60 + b[1]))
            k = num(row.get("KorrektionsFaktor"))
            if k is not None and not (FACTOR_RANGE[0] <= k <= FACTOR_RANGE[1]):
                continue
            v = num(row.get("KorrigeretResultat")) or num(row.get("OriginalResultat"))
            dep = num(row.get("Dybde (m)"))
            if v is None or dep is None or not (0.0 <= v <= 25.0) or dep < 0:
                continue
            bnd = band(dep)
            if bnd is None:
                continue
            if st not in pos:
                try:
                    pos[st] = utm32_to_wgs84(float(row["X_UTM32"]),
                                             float(row["Y_UTM32"]))
                except (ValueError, KeyError, TypeError):
                    pos[st] = None
            if not pos[st]:
                continue
            lon, lat = pos[st]
            try:
                day = dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))
            except ValueError:
                continue
            # the supplied file is UTC by contract; the borrowed clock is
            # Startklok, which the technical instruction requires in UTC too
            when = dt.datetime.combine(day, dt.time(clk[0], clk[1]))
            el = solar_elevation(lat, lon, when)
            # season and site removed the same way as cycles.py: deviation from
            # the same station, same depth band, within a 20-day window
            cell = (st, bnd, day.toordinal() // 20)
            cells[cell][0] += 1
            cells[cell][1] += v
            samples.append((cell, bnd, sun_bin(el), v, src))
            src_count[src] += 1
            used += 1

    log(f"\n{used:,} oxygen measurements placed in time, of {rows:,} rows")
    for s in ("supplied", "borrowed", "none"):
        if src_count[s]:
            log(f"  {s:<10} {src_count[s]:>10,}")

    acc = collections.defaultdict(lambda: [0, 0.0])
    for cell, bnd, sb, v, src in samples:
        n, tot = cells[cell]
        if n < 2:
            continue
        acc[(bnd, sb)][0] += 1
        acc[(bnd, sb)][1] += v - tot / n

    out = {"_what": "Oxygen at depth against the sun's elevation, season and "
                    "site removed by a 20-day window at each station and depth "
                    "band.",
           "_clock": "supplied = data/dropin/ctd_visit_times.csv; borrowed = the "
                     "same station-day in the water-chemistry extract, which "
                     "carries a clock on every row; none = excluded.",
           "measurements": used, "rows_scanned": rows,
           "clock_source": dict(src_count),
           "deviation": {}}
    log("\ndeviation from the same station's own 20-day mean, mg/l:")
    log(f"  {'depth':<12}" + "".join(f"{b:>10}" for b in SUN_ORDER))
    for _, _, bnd in DEPTH_BANDS:
        cellrow = []
        for sb in SUN_ORDER:
            a = acc.get((bnd, sb))
            cellrow.append(f"{a[1]/a[0]:+10.3f}" if a and a[0] >= 30 else f"{'-':>10}")
            if a and a[0] >= 30:
                out["deviation"][f"{bnd}|{sb}"] = {"n": a[0],
                                                   "dev": round(a[1] / a[0], 4)}
        log(f"  {bnd:<12}" + "".join(cellrow))

    if offsets:
        offsets.sort()
        n = len(offsets)
        out["borrowed_clock_check"] = {
            "n": n, "median_min": offsets[n // 2],
            "p5_min": offsets[n // 20], "p95_min": offsets[19 * n // 20],
            "within_30_min_pct": round(
                100 * sum(1 for o in offsets if abs(o) <= 30) / n, 1)}
        log(f"\nBORROWED CLOCK CHECKED against {n:,} supplied times: "
            f"median {offsets[n//2]:+d} min, "
            f"{out['borrowed_clock_check']['within_30_min_pct']}% within half an hour")
    else:
        out["borrowed_clock_check"] = None
        log("\nNo supplied times, so the borrowed clock is UNCHECKED. "
            "Drop ctd_visit_times.csv into data/dropin/ and rerun: this reports "
            "the offset distribution and either supports every conclusion above "
            "or withdraws it.")

    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
