#!/usr/bin/env python3
"""Apples and oranges on times: what each clock value in the water-chemistry extract is.

The technical instruction for Danish marine monitoring asks for sampling times in
UTC (docs/DATA_SOURCES.md). `Startklok` in the ODA extract is not UTC in any era,
and it is not one kind of thing. This measures what it is, per supplier and era,
counting one visit per station, date and clock value, and writes the conventions
scripts/clock.py applies.

THE TEST. Fieldwork keeps local working hours. So compare each station with itself
in the weeks either side of every summer-time change. A Danish wall clock does not
move. A UTC clock moves an hour back at the spring change and forward in autumn. A
wall clock with the offset ADDED - a local time somebody took for UTC and converted
to Danish time - moves the other way. The jump, (spring shift - autumn shift) / 2
in minutes, is about zero for a wall clock, minus an hour for UTC and plus an hour
for the offset added. Weekdays only; the median per station, then the median across
stations, so a changing mix of stations cannot make a jump.

DEFAULTS. Until the changeover, two clock values stand for "no time": with the
added offset taken off they read exactly noon and three in the morning. They
alternate with summer time, and for some suppliers they are every value there is.
They are tested separately from the rest, because a default that moves with the
offset is exactly what made the whole old era look like one convention.

The constant hour cannot be seen by a jump, only the part that changes with summer
time. It is anchored by the default itself: with the offset taken off, it is
exactly noon, which is what a filled-in midday looks like.

    python3 scripts/clockzone.py

Reads data/raw/oda/kemi.csv.gz. Writes data/derived/clock_convention.json.
"""
import collections
import csv
import datetime as dt
import gzip
import io
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, ROOT, log
import clock
from cube import utm32_to_wgs84
from daylight import solar_elevation

SRC = os.path.join(RAW, "oda", "kemi.csv.gz")
OUT = os.path.join(DERIVED, "clock_convention.json")
WINDOW_DAYS = 21        # either side of a change: long enough to find a station twice
MIN_PAIRS = 8           # station comparisons per season before a verdict is given
WALL_TOLERANCE = 15     # minutes: a clean convention jumps by nothing or by an hour,
ADDED_OR_UTC = 45       # so anything between these is a mix no single rule converts


def verdict(j, nsp, nau):
    if j is None or min(nsp, nau) < MIN_PAIRS:
        return "untested"
    if abs(j) <= WALL_TOLERANCE:
        return "wall"
    if j >= ADDED_OR_UTC:
        return "offset-added"
    if j <= -ADDED_OR_UTC:
        return "utc"
    return "ambiguous"


def jump(shifts):
    sp, au = shifts.get("spring", []), shifts.get("autumn", [])
    if not sp or not au:
        return None, len(sp), len(au)
    return (statistics.median(sp) - statistics.median(au)) / 2, len(sp), len(au)


def main(argv):
    log(f"reading {os.path.relpath(SRC, ROOT)}")
    seen, visits = set(), []
    pos = {}
    with gzip.open(SRC, "rb") as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";"):
            d, m = (row.get("Startdato") or "").strip(), clock.parse(row.get("Startklok"))
            if m is None or len(d) != 8 or not d.isdigit():
                continue
            st = row.get("ObservationsStedNr")
            if (st, d, m) in seen:
                continue
            seen.add((st, d, m))
            try:
                day = dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))
            except ValueError:
                continue
            if st not in pos:
                try:
                    pos[st] = utm32_to_wgs84(float(row["X_UTM32"]), float(row["Y_UTM32"]))
                except (ValueError, KeyError, TypeError):
                    pos[st] = None
            visits.append((st, day, m, (row.get("DataLeverandørnavn") or "").strip()))
    seen = None
    log(f"  {len(visits):,} visits")

    # station medians either side of each change, per class of value
    cell = collections.defaultdict(list)
    for st, day, m, sup in visits:
        if day.weekday() >= 5:
            continue
        cand = day.year <= clock.DEFAULTS_UNTIL and clock.is_default_candidate(m, clock.offset(day))
        for season, t in clock.changes(day.year):
            off = (day - t).days
            if 0 < abs(off) <= WINDOW_DAYS:
                side = "after" if off > 0 else "before"
                cell[(st, sup, day.year, season, cand, side)].append(m)
    shifts = collections.defaultdict(lambda: collections.defaultdict(list))
    for (st, sup, y, season, cand, side), v in cell.items():
        if side == "before" and (a := cell.get((st, sup, y, season, cand, "after"))):
            s = statistics.median(a) - statistics.median(v)
            era = clock.era_of(y)
            shifts[("era", era, cand)][season].append(s)
            shifts[("cell", f"{era} | {sup}", cand)][season].append(s)
            shifts[("year", y, cand)][season].append(s)

    def entry(key, n, n_default):
        j, nsp, nau = jump(shifts.get((key[0], key[1], False), {}))
        jd, dsp, dau = jump(shifts.get((key[0], key[1], True), {}))
        return {"visits": n, "defaults": n_default,
                "jump_min": None if j is None else round(j, 1),
                "pairs_spring": nsp, "pairs_autumn": nau,
                "jump_of_defaults_min": None if jd is None else round(jd, 1),
                "verdict": verdict(j, nsp, nau)}

    count, dflt = collections.Counter(), collections.Counter()
    for st, day, m, sup in visits:
        era = clock.era_of(day.year)
        is_d = day.year <= clock.DEFAULTS_UNTIL and clock.is_default_candidate(m, clock.offset(day))
        for k in (("era", era), ("cell", f"{era} | {sup}")):
            count[k] += 1
            dflt[k] += is_d
    eras = {}
    for label, _ in clock.ERAS:
        eras[label] = entry(("era", label), count[("era", label)], dflt[("era", label)])
    eras["to-1980"]["verdict"] = "no summer time"
    cells = {k[1]: entry(k, count[k], dflt[k]) for k in count if k[0] == "cell"}
    for k, c in cells.items():
        if k.startswith("to-1980 |"):
            c["verdict"] = "no summer time"
    years = {}
    for (kind, y, cand), sh in shifts.items():
        if kind == "year" and not cand:
            j, nsp, nau = jump(sh)
            years[str(y)] = {"jump_min": None if j is None else round(j, 1),
                             "pairs_spring": nsp, "pairs_autumn": nau}

    out = {"_what": "What each Startklok value in the water-chemistry extract is, per "
                    "supplier and era, from a per-station test at every summer-time "
                    "change. Read by scripts/clock.py.",
           "_verdicts": "wall: Danish wall clock, UTC = clock - offset. offset-added: "
                        "wall clock with the offset added, UTC = clock - 2 x offset. "
                        "utc: UTC. ambiguous: a mix no single rule converts. untested: "
                        "too few station comparisons; the era's verdict is used. no "
                        "summer time: before 1980 a convention cannot be seen.",
           "params": {"window_days": WINDOW_DAYS, "min_pairs": MIN_PAIRS,
                      "wall_tolerance_min": WALL_TOLERANCE,
                      "offset_added_or_utc_min": ADDED_OR_UTC},
           "eras": eras, "cells": cells, "years": dict(sorted(years.items()))}
    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    clock._conv.clear()

    # what the adopted conventions make of the archive: every class, and for the
    # observed times, how many fall in the dark and at what local hour
    cls = collections.Counter()
    dark = collections.Counter()
    hours = collections.defaultdict(list)
    for st, day, m, sup in visits:
        utc, c = clock.instant(sup, day.strftime("%Y%m%d"), f"{m // 60}{m % 60:02d}")
        era = clock.era_of(day.year)
        cls[(era, c)] += 1
        if c == "observed" and pos.get(st):
            lon, lat = pos[st]
            dark[(era, "n")] += 1
            dark[(era, "below")] += solar_elevation(lat, lon, utc) < 0
            loc = utc + dt.timedelta(hours=clock.offset(day))
            hours[era].append(loc.hour + loc.minute / 60)
    out["classes"] = {era: {c: cls[(era, c)] for c in clock.CLASSES if cls[(era, c)]}
                      for era, _ in clock.ERAS}
    out["observed_check"] = {}
    for era, _ in clock.ERAS:
        if dark[(era, "n")]:
            q = statistics.quantiles(hours[era], n=20)
            out["observed_check"][era] = {
                "n": dark[(era, "n")],
                "sun_below_horizon_pct": round(100 * dark[(era, "below")] / dark[(era, "n")], 2),
                "local_hour_p05": round(q[0], 2), "local_hour_median":
                round(statistics.median(hours[era]), 2), "local_hour_p95": round(q[-1], 2)}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")

    log(f"\n{'era':10}{'verdict':16}{'jump':>7}{'defaults':>10}   classes")
    for era, e in eras.items():
        j = "-" if e["jump_min"] is None else f"{e['jump_min']:+.0f}"
        log(f"{era:10}{e['verdict']:16}{j:>7}{e['defaults']:>10,}   "
            + ", ".join(f"{c} {n:,}" for c, n in out["classes"][era].items()))
    log("\nobserved times under the adopted conventions:")
    for era, e in out["observed_check"].items():
        log(f"  {era:10} {e['n']:>7,} visits, sun below the horizon {e['sun_below_horizon_pct']}%, "
            f"local hour p05/median/p95 {e['local_hour_p05']}/{e['local_hour_median']}/"
            f"{e['local_hour_p95']}")
    log(f"\nwrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
