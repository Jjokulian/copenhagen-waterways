#!/usr/bin/env python3
"""What size of signal could this archive have seen? Synthetic recovery on the real schedule.

cycles.py found no diurnal variation in surface oxygen once season and site were
removed: deviations within about 0.02 mg/l on a mean near 10. That is a null, and
a null is the weakest thing a measurement can produce, because it cannot
distinguish "the effect is absent" from "the instrument could not have seen it".

This converts it into a bound, and it needs no model of how the sea works. The
method is to stipulate a signal - a diurnal cycle of known amplitude, keyed to
the sun's elevation, which is the shape photosynthesis would produce - impose it
on the REAL sample times, positions and station-days from the archive, and run
the SAME estimator cycles.py runs. If the estimator recovers 0.4 of a 0.5 mg/l
amplitude and 0.02 of a 0.05, then the detection limit lies between, and the
observed null says the true amplitude is under it.

The realism of the world model does not enter. Nothing here claims the sea
behaves this way. The claim is only: IF it did, at this amplitude, would this
sampling schedule and this estimator have found it? That is a question about the
instrument, and the instrument is real - every timestamp, position and visit
pattern below is taken from the 1.8 million row extract rather than invented.

WHAT IT ALSO TESTS. cycles.py reported that 96% of samples fall between 09:00 and
15:00 and asserted that this is why the pre-dawn minimum is invisible. That was a
plausible story with nothing behind it. Here it is measurable: the same synthetic
signal is recovered twice, once on the real times and once on times spread evenly
across the day, and the difference between the two recoveries is the cost of the
working day - in mg/l, not in rhetoric.

    python3 scripts/detectable.py

Writes data/derived/detectable.json.
"""
import collections
import csv
import datetime as dt
import gzip
import io
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, ROOT, log
from cube import utm32_to_wgs84
from daylight import solar_elevation, parse_klok

SRC = os.path.join(RAW, "oda", "kemi.csv.gz")
OUT = os.path.join(DERIVED, "detectable.json")
AMPLITUDES = [0.0, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
WINDOW = 10          # days, as in cycles.py's tightest control
# Measured, not stipulated - and measured where the thing being tested cannot
# contaminate it. Two earlier versions were wrong in different ways. The first
# asserted 0.8 mg/l, so the bound was only as good as a guess. The second measured
# the within-cell residual spread of the archive, which is CIRCULAR: that residual
# contains whatever diurnal signal exists, so a large real cycle would inflate the
# yardstick used to rule a large real cycle out. The estimate is now taken only
# from cells whose samples all fall in the SAME sun-elevation bin, where no
# diurnal variance can enter by construction.
NOISE = None


def sun_bin(e):
    return ("night" if e < -6 else "twilight" if e < 0 else "0-10" if e < 10
            else "10-20" if e < 20 else "20-30" if e < 30 else "30+")


ORDER = ["night", "twilight", "0-10", "10-20", "20-30", "30+"]


def load_schedule():
    """The real thing: every surface oxygen visit, with its true instant.

    Also returns the archive's own within-cell residual spread, which is the
    noise the synthetic run must reproduce for its bound to mean anything."""
    pos, out, vals = {}, [], []
    with gzip.open(SRC, "rb") as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"),
                                  delimiter=";"):
            if row.get("Parameter") != "Oxygen indhold":
                continue
            if row.get("Prøvetype") not in ("Enkeltprøve", "Blandingsprøve"):
                continue
            k = parse_klok(row.get("Startklok"))
            d = (row.get("Startdato") or "").strip()
            if not k or len(d) != 8:
                continue
            try:
                dep = float((row.get("GennemsnitsDybde_m") or "").replace(",", "."))
            except ValueError:
                continue
            if dep > 3.0 or dep == 99:
                continue
            st = row.get("ObservationsStedNr")
            if st not in pos:
                try:
                    pos[st] = utm32_to_wgs84(float(row["X_UTM32"]),
                                             float(row["Y_UTM32"]))
                except (ValueError, KeyError, TypeError):
                    pos[st] = None
            if not pos[st]:
                continue
            try:
                day = dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))
            except ValueError:
                continue
            v = None
            if (row.get("ResultatAttribut") or "").strip() not in ("<", ">") \
                    and (row.get("Enhed") or "").strip() == "mg/l":
                v = num_(row.get("Resultat"))
                if v is not None and not (0.0 <= v <= 25.0):
                    v = None
            out.append((st, day, k[0] * 60 + k[1], pos[st]))
            vals.append(((st, day.toordinal() // WINDOW), v))
    log(f"  {len(out):,} real surface-oxygen visits, "
        f"{len({o[0] for o in out}):,} stations")

    # Noise, taken where the signal cannot reach it. A cell here is a station and
    # a 10-day window as before, but only cells in which EVERY sample shares a
    # sun-elevation bin are used, so the spread within them cannot contain a
    # diurnal term whatever its size.
    binof = {}
    for (cell, v), (st, day, minute, (lon, lat)) in zip(vals, out):
        when = dt.datetime.combine(day, dt.time(minute // 60, minute % 60))
        binof[(cell, id(v))] = sun_bin(solar_elevation(lat, lon, when))
    cellbins = collections.defaultdict(set)
    cells = collections.defaultdict(lambda: [0, 0.0])
    for (cell, v), (st, day, minute, (lon, lat)) in zip(vals, out):
        when = dt.datetime.combine(day, dt.time(minute // 60, minute % 60))
        cellbins[cell].add(sun_bin(solar_elevation(lat, lon, when)))
        if v is not None:
            cells[cell][0] += 1
            cells[cell][1] += v
    single = {c for c, b in cellbins.items() if len(b) == 1}
    dev = []
    for cell, v in vals:
        if v is None or cell not in single:
            continue
        n, tot = cells[cell]
        if n >= 2:
            dev.append(v - tot / n)
    log(f"  noise taken from {len(single):,} single-sun-bin cells of "
        f"{len(cellbins):,} (the rest could contain the signal being tested)")
    if len(dev) > 100:
        m = sum(dev) / len(dev)
        sd = (sum((x - m) ** 2 for x in dev) / (len(dev) - 1)) ** 0.5
    else:
        sd = 0.8
    log(f"  measured within-cell residual sd: {sd:.3f} mg/l (n={len(dev):,})")
    return out, sd


def num_(s):
    try:
        return float((s or "").replace(",", "."))
    except (ValueError, AttributeError):
        return None


def recover(schedule, amp, rng, noise, spread_hours=False):
    """Impose a cycle of amplitude `amp`, then run cycles.py's estimator on it.

    Returns the recovered peak-to-trough spread across sun-elevation bins - the
    quantity cycles.py reports and found to be about 0.02 mg/l in the real data."""
    cells = collections.defaultdict(lambda: [0, 0.0])
    rows = []
    for st, day, minute, (lon, lat) in schedule:
        if spread_hours:
            minute = rng.randrange(0, 1440)     # the same visits, any hour
        when = dt.datetime.combine(day, dt.time(minute // 60, minute % 60))
        el = solar_elevation(lat, lon, when)
        # the signal: proportional to sun above the horizon, which is the shape
        # photosynthetic production would impose. Amplitude is peak-to-trough.
        s = amp * (max(0.0, math.sin(math.radians(max(el, 0.0)))) - 0.5)
        # everything this does not model - season, site, weather, real variance
        v = 10.0 + s + rng.gauss(0.0, noise)
        cell = (st, day.toordinal() // WINDOW)
        cells[cell][0] += 1
        cells[cell][1] += v
        rows.append((cell, sun_bin(el), v))
    acc = collections.defaultdict(lambda: [0, 0.0])
    for cell, sb, v in rows:
        n, tot = cells[cell]
        if n < 2:
            continue
        acc[sb][0] += 1
        acc[sb][1] += v - tot / n
    devs = {b: a[1] / a[0] for b, a in acc.items() if a[0] >= 30}
    if not devs:
        return 0.0, {}
    return max(devs.values()) - min(devs.values()), devs


def main(argv):
    log(f"reading the real sampling schedule from {os.path.relpath(SRC, ROOT)}")
    schedule, noise = load_schedule()
    rng = random.Random(0)          # deterministic: a bound must be repeatable

    out = {"_what": "Recovery of a stipulated diurnal signal imposed on the REAL "
                    "sample times, positions and visit pattern of the archive.",
           "_not": "This claims nothing about how the sea behaves. It asks only "
                   "whether this schedule and this estimator could have SEEN a "
                   "signal of a given size.",
           "n_visits": len(schedule),
           "noise_sd_mg_l": round(noise, 4),
           "noise_source": "measured: within-cell residual sd of the archive "
                           "itself, same station and same 10-day window",
           "window_days": WINDOW, "observed_real_spread_mg_l": 0.0294,
           "observed_spread_note": "max minus min across sun bins carrying "
                                   "n>=1000 in cycles.json; the two thinnest "
                                   "bins (n~340) are noise-dominated and excluded",
           "runs": []}

    log(f"\n{'imposed':>9}  {'recovered':>10}  {'if sampled':>11}   cost of")
    log(f"{'amplitude':>9}  {'(real hrs)':>10}  {'round clock':>11}   the working day")
    for amp in AMPLITUDES:
        got, _ = recover(schedule, amp, random.Random(1), noise)
        even, _ = recover(schedule, amp, random.Random(1), noise, spread_hours=True)
        out["runs"].append({"imposed": amp, "recovered_real_hours": round(got, 4),
                            "recovered_even_hours": round(even, 4),
                            "fraction_recovered": round(got / amp, 3) if amp else None})
        log(f"{amp:9.2f}  {got:10.3f}  {even:11.3f}   "
            + (f"{100*(1-got/even):5.0f}% lost" if even > 0.02 else ""))

    # where the recovered signal first clears the real observed spread
    limit = None
    for r in out["runs"]:
        if r["imposed"] and r["recovered_real_hours"] > out["observed_real_spread_mg_l"]:
            limit = r["imposed"]
            break
    out["detection_limit_mg_l"] = limit
    log("")
    if limit is not None:
        log(f"An imposed cycle of {limit} mg/l is recovered ABOVE the "
            f"{out['observed_real_spread_mg_l']} mg/l actually observed.")
        log(f"So the real surface diurnal amplitude is BELOW about {limit} mg/l - "
            "a bound, not a null.")
    else:
        log("No imposed amplitude cleared the observed spread: this schedule "
            "cannot bound the diurnal cycle at all, which is itself the finding.")

    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
