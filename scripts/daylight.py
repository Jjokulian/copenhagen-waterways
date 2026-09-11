#!/usr/bin/env python3
"""What the sun was doing when the water was sampled.

The vandkemi extract carries a clock time on 100.0% of its 1.8 million rows
(`Startklok`), which PLAN.md said the archive did not have. The first thing done
with it was a histogram of clock hours, and that was the wrong instrument.

At 55.7 degrees north a clock hour is not a light level. Sunrise in Copenhagen
runs from about 03:25 in late June to about 08:45 in late December, and the sun
never gets higher than roughly 11 degrees at midwinter noon against 58 degrees at
midsummer noon. So 09:00 in December is a sample taken in the dark or in the first
grey of dawn, and 09:00 in June is a sample taken after five hours of
photosynthesis. Binning both into "09" says the two are the same measurement
condition, which is exactly the error the clock column was supposed to fix.

The physically meaningful quantity is the sun's elevation above the horizon at
that place and that instant - and, for a diurnal signal that integrates, the hours
of light that have already fallen on the water before the bottle went in. This
computes both, per row, from the sample's own position.

Solar position by the NOAA algorithm, written out rather than imported: this box
has no ephemeris library and the accuracy needed here (a degree) is far inside
what the series gives (about 0.01 degrees).

TIME ZONE. ODA does not document what Startklok is, and it turned out to be
several things: filled-in defaults, wall-clock times with the offset added, and
wall-clock times, by supplier and era. scripts/clockzone.py measures which is
which at every summer-time change, and the measures here use the instant
scripts/clock.py derives from that - only where it derives one. The fixed
readings (UTC, Danish, a flat +1 or +2) are still counted, as controls.

IMPOSSIBLE VALUES. Two rows of 13,289 report oxygen saturation at 74,332% and
90,972%, and one reports 32.6 mg/l. Left in, the two moved December's dawn bin
from 94% to 542% - three rows in a hundred and seventy thousand, deciding a
published number. All three carry ODA's weakest control level (`B, Elektronisk
kontrol`) and a migration note saying the source status was still "MST Under
kontrol", so the archive does distinguish them; but dropping all 7,787
electronically-controlled rows to catch three is worse than the disease. The
filter here is physics and is stated as such: saturation in [0, 250]% (a dense
bloom reaches perhaps 200), concentration in [0, 25] mg/l (fresh water at 0 C
saturates near 14.6). Everything dropped is counted and reported.

THE SEASONAL CONFOUND, which is the whole difficulty. Oxygen solubility falls as
water warms, and high sun means summer. Sorting oxygen by sun elevation across
the whole record therefore shows concentration *falling* as the sun rises -
which is solubility, and says nothing about photosynthesis. The diurnal question
can only be asked inside a month, where the season is held still and the sun
elevation still varies by thirty degrees across the working day. That is what
this reports; the pooled table is kept beside it as the demonstration of what
pooling does.

Month is not enough on its own, though, because which stations get visited at
dawn is not random - a station sampled early is often a different kind of water
from one sampled at noon. So the measure that is actually reported is a
fixed-effects one: every sample is expressed as its deviation from the mean of
its own station in its own calendar month of its own year, and those deviations
are averaged by sun elevation. Season and site both drop out, and what is left
is the within-visit-window variation, which is the only place a diurnal signal
could honestly show up.

WHAT IT FOUND, so the next reader does not have to run it to know. Once season
and site are removed, surface oxygen does not vary with the sun's elevation: the
deviations are +-0.01 mg/l against a mean near 10, and they do not grow when the
comparison is restricted to the station-months that span most of a day. There is
contrast to detect a signal with - the median station-month spans 5.3 degrees of
elevation and 3,591 of them span more than 15 - so this is an absence of signal
and not an absence of evidence.

That is not a licence to forget the diurnal problem; it relocates it. The record
is sampled between about 09:00 and 15:00 Danish time, with 4% of samples below
the horizon. What this shows is that inside the sampled window the water does not
swing much. It says nothing whatever about the pre-dawn minimum, because the
archive almost never visits it - and the pre-dawn minimum is the value an oxygen
threshold is about. The dimension is present in the data and flat where it is
observed; the part that would matter is still unobserved.

Writes data/derived/daylight.json.
"""
import csv
import datetime as dt
import gzip
import io
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, log
import clock
from cube import utm32_to_wgs84

SRC = os.path.join(RAW, "oda", "kemi.csv.gz")
OUT = os.path.join(DERIVED, "daylight.json")


def solar_elevation(lat, lon, when_utc):
    """Sun elevation in degrees, NOAA. `when_utc` is a naive UTC datetime."""
    jd = (when_utc - dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + 2451545.0
    t = (jd - 2451545.0) / 36525.0
    l0 = (280.46646 + t * (36000.76983 + 0.0003032 * t)) % 360.0
    m = 357.52911 + t * (35999.05029 - 0.0001537 * t)
    mr = math.radians(m)
    e = 0.016708634 - t * (0.000042037 + 0.0000001267 * t)
    c = (math.sin(mr) * (1.914602 - t * (0.004817 + 0.000014 * t))
         + math.sin(2 * mr) * (0.019993 - 0.000101 * t)
         + math.sin(3 * mr) * 0.000289)
    true_long = l0 + c
    omega = 125.04 - 1934.136 * t
    app_long = true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))
    eps0 = 23.0 + (26.0 + (21.448 - t * (46.815 + t * (0.00059 - t * 0.001813))) / 60.0) / 60.0
    eps = math.radians(eps0 + 0.00256 * math.cos(math.radians(omega)))
    decl = math.asin(math.sin(eps) * math.sin(math.radians(app_long)))

    y = math.tan(eps / 2.0) ** 2
    l0r = math.radians(l0)
    eqtime = 4.0 * math.degrees(
        y * math.sin(2 * l0r) - 2 * e * math.sin(mr)
        + 4 * e * y * math.sin(mr) * math.cos(2 * l0r)
        - 0.5 * y * y * math.sin(4 * l0r) - 1.25 * e * e * math.sin(2 * mr))

    mins = when_utc.hour * 60 + when_utc.minute + when_utc.second / 60.0
    tst = (mins + eqtime + 4.0 * lon) % 1440.0
    ha = math.radians(tst / 4.0 - 180.0)
    latr = math.radians(lat)
    cosz = (math.sin(latr) * math.sin(decl)
            + math.cos(latr) * math.cos(decl) * math.cos(ha))
    return 90.0 - math.degrees(math.acos(max(-1.0, min(1.0, cosz))))


def sun_events(lat, lon, day):
    """(sunrise, solar noon, sunset) as UTC hours, or None where the sun does
    not cross the horizon. Bisection on elevation: cheaper to write correctly
    than the closed form, and this runs once per station-day, not per row."""
    noon = None
    best = -100.0
    for i in range(0, 1440, 10):
        t = dt.datetime.combine(day, dt.time()) + dt.timedelta(minutes=i)
        el = solar_elevation(lat, lon, t)
        if el > best:
            best, noon = el, i / 60.0
    if best < 0:
        return None, noon, None

    def cross(a, b):
        for _ in range(24):
            mid = (a + b) / 2.0
            t = dt.datetime.combine(day, dt.time()) + dt.timedelta(hours=mid)
            if solar_elevation(lat, lon, t) < 0:
                a = mid
            else:
                b = mid
        return (a + b) / 2.0

    lo = dt.datetime.combine(day, dt.time())
    rise = cross(0.0, noon) if solar_elevation(lat, lon, lo) < 0 else 0.0
    end = solar_elevation(lat, lon, lo + dt.timedelta(hours=23.99))
    setr = cross(24.0, noon) if end < 0 else 24.0
    return rise, noon, setr


def danish_offset(d):
    """UTC offset of Danish legal time on this date, in hours - with the historical
    rules, which the present EU rule is not: no summer time before 1980, and until
    1995 it ended in September. The rules live in clock.py, which every clock
    reading now goes through."""
    import clock
    return clock.offset(d)


def parse_klok(s):
    """'400' -> (4, 0); '1330' -> (13, 30). Blank or nonsense -> None."""
    s = (s or "").strip()
    if not s.isdigit():
        return None
    v = int(s)
    h, mi = divmod(v, 100)
    if h > 23 or mi > 59:
        return None
    return h, mi


def bin_of(el):
    if el < -6:
        return "night"
    if el < 0:
        return "twilight"
    if el < 10:
        return "0-10"
    if el < 20:
        return "10-20"
    if el < 30:
        return "20-30"
    if el < 40:
        return "30-40"
    return "40+"


ORDER = ["night", "twilight", "0-10", "10-20", "20-30", "30-40", "40+"]


def main(argv):
    want = {"Oxygen indhold", "Oxygenmætning", "Klorofyl a", "Nitrogen,total N"}
    only = [a for a in argv if not a.startswith("--")]
    if only:
        want = set(only)
    tz_arg = next((a.split("=", 1)[1] for a in argv if a.startswith("--tz=")), None)

    pos = {}          # station -> (lon, lat), computed once
    ZONES = ("utc", "danish", "cet", "cest", "clock")
    counts = {tz: {b: 0 for b in ORDER} for tz in ZONES}
    by_month = {tz: {m: {b: 0 for b in ORDER} for m in range(1, 13)} for tz in ZONES}
    # n, sum - pooled (the confounded view) and per month (the honest one)
    pooled = {p: {b: [0, 0.0] for b in ORDER} for p in ("o2", "sat")}
    monthly = {p: {m: {b: [0, 0.0] for b in ORDER} for m in range(1, 13)}
               for p in ("o2", "sat")}
    # (station, year-month) -> [n, sum] and the samples themselves, for the
    # fixed-effects pass. Surface oxygen is about 90,000 rows; holding them is
    # 10 MB, against re-reading a 1.8 million row file twice.
    cells = {p: {} for p in ("o2", "sat")}
    samples = {p: [] for p in ("o2", "sat")}
    RANGE = {"sat": (0.0, 250.0), "o2": (0.0, 25.0)}
    dropped = {"sat": 0, "o2": 0}
    hours_hist = {}
    rows = used = noclock = nopos = 0
    clock_classes = {}

    log(f"reading {os.path.relpath(SRC)}")
    with gzip.open(SRC, "rb") as fh:
        rd = csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";")
        for row in rd:
            rows += 1
            if row.get("Parameter") not in want:
                continue
            k = parse_klok(row.get("Startklok"))
            if not k:
                noclock += 1
                continue
            d = (row.get("Startdato") or "").strip()
            if len(d) != 8 or not d.isdigit():
                continue
            st = row.get("ObservationsStedNr")
            if st not in pos:
                try:
                    pos[st] = utm32_to_wgs84(float(row["X_UTM32"]),
                                             float(row["Y_UTM32"]))
                except (ValueError, KeyError, TypeError):
                    pos[st] = None
            if not pos[st]:
                nopos += 1
                continue
            lon, lat = pos[st]
            try:
                day = dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))
            except ValueError:
                continue
            local = dt.datetime.combine(day, dt.time(k[0], k[1]))
            used += 1
            hours_hist[k[0]] = hours_hist.get(k[0], 0) + 1
            # the fixed readings are controls; the measures use the instant
            # scripts/clock.py gives, and only where it gives one
            utc, cls = clock.instant(row.get("DataLeverandørnavn"), d, row.get("Startklok"))
            clock_classes[cls] = clock_classes.get(cls, 0) + 1
            readings = [("utc", local),
                        ("danish", local - dt.timedelta(hours=danish_offset(day))),
                        ("cet", local - dt.timedelta(hours=1)),
                        ("cest", local - dt.timedelta(hours=2))]
            if utc is not None:
                readings.append(("clock", utc))
            for tz, when in readings:
                el = solar_elevation(lat, lon, when)
                b = bin_of(el)
                counts[tz][b] += 1
                by_month[tz][day.month][b] += 1
                if tz != "clock":
                    continue
                which = {"Oxygen indhold": "o2", "Oxygenmætning": "sat"}.get(
                    row.get("Parameter"))
                if not which:
                    continue
                try:
                    v = float((row.get("Resultat") or "").replace(",", "."))
                    dep = float((row.get("GennemsnitsDybde_m") or "").replace(",", "."))
                except ValueError:
                    continue
                if dep > 3.0:            # the diurnal signal lives at the surface
                    continue
                lo, hi = RANGE[which]
                if not (lo <= v <= hi):
                    dropped[which] += 1
                    continue
                pooled[which][b][0] += 1
                pooled[which][b][1] += v
                monthly[which][day.month][b][0] += 1
                monthly[which][day.month][b][1] += v
                cell = (st, day.year, day.month)
                c = cells[which].setdefault(cell, [0, 0.0])
                c[0] += 1
                c[1] += v
                samples[which].append((cell, b, v))
            if used % 50000 == 0:
                log(f"  {used:,} measurements placed")

    # Does the (absent) signal appear where the day is actually spanned? A flat
    # fixed-effects result means nothing if every cell was sampled at one hour, so
    # the same estimate is recomputed on progressively higher-contrast subsets. A
    # real diurnal signal would make the high bin positive and grow down the list.
    contrast = {}
    for p in ("o2", "sat"):
        cellvals = {}
        for cell, b, v in samples[p]:
            cellvals.setdefault(cell, []).append((b, v))
        elev_rank = {b: i for i, b in enumerate(ORDER)}
        rows_out = []
        for label, need in (("all", 0), ("spans 2 bins", 2), ("spans 3 bins", 3),
                            ("spans 4 bins", 4)):
            acc, ncell = {}, 0
            for cell, vs in cellvals.items():
                if len(vs) < 2:
                    continue
                span = (max(elev_rank[b] for b, _ in vs)
                        - min(elev_rank[b] for b, _ in vs) + 1)
                if span < need:
                    continue
                ncell += 1
                mean = sum(v for _, v in vs) / len(vs)
                for b, v in vs:
                    a = acc.setdefault(b, [0, 0.0])
                    a[0] += 1
                    a[1] += v - mean
            rows_out.append({"subset": label, "cells": ncell,
                             "deviation": {b: round(a[1] / a[0], 4)
                                           for b, a in acc.items() if a[0] >= 30}})
        contrast[p] = rows_out

    # fixed effects: deviation from the sample's own station-month mean
    fixed = {}
    for p in ("o2", "sat"):
        acc = {b: [0, 0.0] for b in ORDER}
        for cell, b, v in samples[p]:
            n, tot = cells[p][cell]
            if n < 2:                       # a cell of one has no within-variation
                continue
            acc[b][0] += 1
            acc[b][1] += v - tot / n
        fixed[p] = {b: {"n": a[0],
                        "mean_deviation": round(a[1] / a[0], 4) if a[0] else None}
                    for b, a in acc.items()}

    out = {
        "source": os.path.relpath(SRC),
        "parameters": sorted(want),
        "rows_scanned": rows, "measurements_used": used,
        "no_clock": noclock, "no_position": nopos,
        "stations": len([p for p in pos.values() if p]),
        "note": ("Startklok is several things by supplier and era; "
                 "scripts/clockzone.py measures which. The measures use "
                 "scripts/clock.py's instant, which excludes filled-in defaults "
                 "and mixed conventions; the fixed readings are controls."),
        "clock_classes": clock_classes,
        "elevation_bins": ORDER,
        "counts": counts,
        "by_month": by_month,
        "clock_hours": hours_hist,
        "reading_used_for_the_measures": "clock",
        "surface_pooled": {p: {b: {"n": v[0],
                                   "mean": round(v[1] / v[0], 3) if v[0] else None}
                               for b, v in bins.items()}
                           for p, bins in pooled.items()},
        "dropped_as_physically_impossible": dropped,
        "surface_fixed_effects": fixed,
        "contrast_ladder": contrast,
        "fixed_effects_note": ("Deviation from the mean of the same station in "
                               "the same calendar month of the same year. Season "
                               "and site both drop out."),
        "surface_by_month": {p: {m: {b: {"n": v[0],
                                         "mean": round(v[1] / v[0], 3) if v[0] else None}
                                     for b, v in bins.items()}
                                 for m, bins in months.items()}
                             for p, months in monthly.items()},
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")

    log(f"\n{used:,} measurements of {sorted(want)} at {out['stations']} stations")
    log(f"{'bin':<10}" + "".join(f"{t.upper():>13}" for t in ZONES))
    for b in ORDER:
        log(f"{b:<10}" + "".join(
            f"{counts[t][b]:>9,} {100*counts[t][b]/max(used,1):>2.0f}%" for t in ZONES))
    dark = {t: counts[t]["night"] + counts[t]["twilight"] for t in ZONES}
    log("  below the horizon: " + ", ".join(
        f"{t}={100*dark[t]/max(used,1):.1f}%" for t in ZONES))

    for p, label, unit in (("sat", "oxygen saturation", "%"),
                           ("o2", "oxygen concentration", "mg/l")):
        log(f"\nsurface (<=3 m) {label} by sun elevation "
            f"- POOLED, confounded by season:")
        for b in ORDER:
            v = out["surface_pooled"][p][b]
            if v["n"]:
                log(f"  {b:<10} n={v['n']:>7,}   {v['mean']} {unit}")
        log(f"  within a month, where the season is held still:")
        log("  month " + "".join(f"{b:>9}" for b in ORDER[2:]) + "     n")
        for m in range(1, 13):
            row = out["surface_by_month"][p][m]
            n = sum(row[b]["n"] for b in ORDER)
            if n < 200:
                continue
            log(f"  {m:>5}  " + "".join(
                (f"{row[b]['mean']:>9}" if row[b]["n"] >= 30 else f"{'-':>9}")
                for b in ORDER[2:]) + f"  {n:>7,}")
        log(f"  dropped as physically impossible: {dropped[p]}")
        log(f"  DEVIATION from the same station's own mean that month "
            f"({unit}), season and site removed:")
        for b in ORDER:
            v = fixed[p][b]
            if v["n"] >= 30:
                log(f"    {b:<10} n={v['n']:>7,}   {v['mean_deviation']:+.3f}")
        log("  and the same, on cells that span more of the day "
            "(a real signal would grow):")
        for r in contrast[p]:
            d = r["deviation"]
            log(f"    {r['subset']:<14} {r['cells']:>6,} cells   " + "  ".join(
                f"{b}={d[b]:+.3f}" for b in ORDER if b in d))
    log(f"\nwrote {os.path.relpath(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
