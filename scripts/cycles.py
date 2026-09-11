#!/usr/bin/env python3
"""Three cycles over one water sample, and a continuous season.

The vandkemi extract carries a clock on every row, which lets three periodic
forcings be placed on each measurement instead of none:

  the day     the sun's elevation at that instant and place
  the year    where in the season it falls - continuously, see below
  the month   the moon's altitude and illuminated fraction, and so the
  (synodic)   spring-neap position

and one measured covariate, surface temperature, joined from the CTD extract on
station and date because vandkemi has a clock and no temperature while CTD has
temperature and no clock.

WHY THE SEASONAL CONTROL IS NOT A MONTH. The first version of this binned
samples by calendar month, and a month is a step function laid over something
with no steps in it: the 31st of March and the 1st of April are the same week and
land in different cells, and the walls fall in the middle of the spring and
autumn turns, which are the transitions that carry the most change. So the
control here is a moving window - each sample is compared with the other samples
at its own station within +-W days, itself excluded. Continuous, no boundary, and
W is a dial that gets turned rather than a convention that gets inherited.

WHY NOT REPLACE SEASON WITH TEMPERATURE. Because the calendar carries what
temperature does not: photoperiod history, the spectral shift through the year,
and the phenological triggers that fire on a date and then latch - first frost,
overwintering stage, whether a species has already switched mode. Temperature at
the instant of sampling is a state; the season is an accumulation. Both are kept.

WHAT THE MOON CAN AND CANNOT DO, so the result is not oversold. Full moonlight is
roughly 0.1 to 0.3 lux against 100,000 for direct sun - about a millionth. It
cannot drive photosynthesis at any level these instruments resolve, and a
positive oxygen result attributed to moonlight would be a mistake. Its plausible
routes are indirect: the diel vertical migration of grazing zooplankton tracks
moonlight, and the spring-neap cycle moves mixing energy. Those are what is
tested, and the tidal half of it is forcing rather than response - see
ephemeris.py on why water level is not inferred here.

Writes data/derived/cycles.json.
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

from common import DERIVED, RAW, log
from cube import utm32_to_wgs84
from daylight import solar_elevation
import clock
from ephemeris import moon_altitude, moon_illumination, spring_neap

SRC = os.path.join(RAW, "oda", "kemi.csv.gz")
TEMPS = os.path.join(DERIVED, "surface_temp.csv.gz")
OUT = os.path.join(DERIVED, "cycles.json")

# (key, unit reported, THE UNIT THE ARCHIVE MUST SAY, low, high)
#
# The unit is checked per row, not assumed. enums.py found 14 of 147 parameters
# carrying more than one unit, and two of them are not strays: Orthophosphat is
# 565 rows in ug/l against 353 in mg/l, and integrated primary production is
# split between mg/(m2*d) and mg/(m3*d), which are not even convertible without
# a depth. Chlorophyll is 185,313 rows in ug/l and exactly one in mg/l - a
# thousandfold error that no range filter can see, because a plausible mg/l
# value is also a plausible ug/l value. Oxygen and saturation are single-unit
# today; this guard is here so that stops being something anyone has to
# remember.
PARAMS = {"Oxygen indhold": ("o2", "mg/l", "mg/l", 0.0, 25.0),
          "Oxygenmætning": ("sat", "%", "pct", 0.0, 250.0),
          "Klorofyl a": ("chl", "µg/l", "µg/l", 0.0, 500.0)}
MAX_DEPTH = 3.0
# Teknisk anvisning for marin overvaagning, Kap. 5 (Kaas & Markager 1998),
# "Pelagiale parametre - proevetagning i felten", is the nearest guide to what
# these mean, and it does not settle them:
#   Enkeltproeve     one bottle at one depth
#   Blandingsproeve  the word is in none of the pinned chapters (4, 5, 6). Kap. 5
#                    says "Hvis en vanddybde repraesenteres af vand taget med
#                    flere vandhentere, skal vandet fra disse vandhentere
#                    blandes" - before subsampling for nutrients, chlorophyll and
#                    primary production, not oxygen. Reading ODA's label as such a
#                    pool at one depth is an inference; kept as a point sample. A
#                    small minority of the surface oxygen rows (count not stored).
#   Dybdeintegreret  integrated over 0-10 m, 0-25 m, or the whole photic zone.
#                    2,265 of these carry a nominal depth of 3 m or less and
#                    would enter a surface filter as if they were point samples,
#                    and 2,870 report a depth of 99, which is a sentinel.
#                    Excluded: an integral is not a measurement at its midpoint.
# The instruction also says nutrients are measured on single samples precisely
# so a result can be tied to one depth, temperature and salinity.
POINT_TYPES = {"Enkeltprøve", "Blandingsprøve"}
WINDOWS = (10, 20, 30, 45)


def sun_bin(e):
    return ("night" if e < -6 else "twilight" if e < 0 else
            "0-10" if e < 10 else "10-20" if e < 20 else
            "20-30" if e < 30 else "30-40" if e < 40 else "40+")


SUN_ORDER = ["night", "twilight", "0-10", "10-20", "20-30", "30-40", "40+"]
MOON_ORDER = ["down", "up dark", "up half", "up bright"]
TIDE_ORDER = ["spring", "mid", "neap"]
TEMP_ORDER = ["<4", "4-8", "8-12", "12-16", "16-20", "20+"]


def moon_bin(alt, frac):
    if alt < 0:
        return "down"
    return "up bright" if frac > 0.75 else "up half" if frac > 0.35 else "up dark"


def temp_bin(t):
    if t is None:
        return None
    for lim, name in ((4, "<4"), (8, "4-8"), (12, "8-12"),
                      (16, "12-16"), (20, "16-20")):
        if t < lim:
            return name
    return "20+"


def load_temps():
    if not os.path.exists(TEMPS):
        log(f"  no {os.path.relpath(TEMPS)} yet - temperature axis skipped")
        return {}
    out = {}
    with gzip.open(TEMPS, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["temp_c"]:
                out[(r["station"], r["date"])] = float(r["temp_c"])
    log(f"  {len(out):,} station-days of surface temperature")
    return out


def deviations(samples, window, key):
    """Leave-one-out deviation from the same station within +-window days.

    samples: list of (station, ordinal, value, dict-of-bins).
    Returns {bin_value: (n, mean_deviation)} for the axis named by `key`,
    and the number of samples that had any neighbour at all."""
    by_station = {}
    for s in samples:
        by_station.setdefault(s[0], []).append(s)
    acc, used = {}, 0
    for rows in by_station.values():
        rows.sort(key=lambda r: r[1])
        ords = [r[1] for r in rows]
        # prefix sums make the window mean O(1) per sample instead of O(n)
        pre = [0.0]
        for r in rows:
            pre.append(pre[-1] + r[2])
        lo = hi = 0
        for i, r in enumerate(rows):
            while ords[lo] < r[1] - window:
                lo += 1
            while hi < len(rows) and ords[hi] <= r[1] + window:
                hi += 1
            n = hi - lo - 1                       # excluding self
            if n < 1:
                continue
            mean = (pre[hi] - pre[lo] - r[2]) / n
            b = r[3].get(key)
            if b is None:
                continue
            a = acc.setdefault(b, [0, 0.0])
            a[0] += 1
            a[1] += r[2] - mean
            used += 1
    return ({b: {"n": a[0], "dev": round(a[1] / a[0], 4)} for b, a in acc.items()},
            used)


def read_samples(temps, params=None):
    """The surface samples every analysis of the diurnal cycle uses, placed in
    time by scripts/clock.py. detectable.py imports this, so the synthetic
    recovery runs on exactly the samples the real estimate does.

    Returns ({key: [(station, ordinal, value, bins, utc, (lon, lat))]}, info).
    info["clock"] counts, by clock class, the samples that passed every other
    filter; only "observed" ones are placed."""
    params = params or PARAMS
    pos, store = {}, {spec[0]: [] for spec in params.values()}
    rows = dropped = 0
    skipped = {"type": 0, "censored": 0, "unit": 0}
    clock_classes = collections.Counter()
    log(f"reading {os.path.relpath(SRC)}")
    with gzip.open(SRC, "rb") as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"),
                                  delimiter=";"):
            rows += 1
            spec = params.get(row.get("Parameter"))
            if not spec:
                continue
            key, _, unit_required, lo, hi = spec
            if (row.get("Enhed") or "").strip() != unit_required:
                skipped["unit"] += 1
                continue
            d = (row.get("Startdato") or "").strip()
            if len(d) != 8 or not d.isdigit():
                continue
            try:
                dep = float((row.get("GennemsnitsDybde_m") or "").replace(",", "."))
                v = float((row.get("Resultat") or "").replace(",", "."))
            except ValueError:
                continue
            if dep > MAX_DEPTH:
                continue
            if row.get("Prøvetype") not in POINT_TYPES:
                skipped["type"] += 1
                continue
            # "<" means Resultat carries the DETECTION LIMIT, not the
            # measurement - 85,035 rows of it. Reading a bound as a value biases
            # the parameter high, so these are counted and dropped rather than
            # quietly averaged in. "ikke paavist" is a real zero (all 80 are
            # PFAS sums with nothing detected) but is not one of these three.
            if (row.get("ResultatAttribut") or "").strip() in ("<", ">"):
                skipped["censored"] += 1
                continue
            if not (lo <= v <= hi):
                dropped += 1
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
            lon, lat = pos[st]
            try:
                day = dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))
            except ValueError:
                continue
            # one continuous time axis: the instant clock.py derives, or nothing
            utc, cls = clock.instant(row.get("DataLeverandørnavn"), d, row.get("Startklok"))
            clock_classes[cls] += 1
            if cls != "observed":
                continue
            frac, _ = moon_illumination(utc)
            bins = {
                "sun": sun_bin(solar_elevation(lat, lon, utc)),
                "moon": moon_bin(moon_altitude(lat, lon, utc), frac),
                "tide": spring_neap(frac),
                # Both extracts write the date as YYYYMMDD. An earlier version
                # hyphenated it here before the lookup and every join missed,
                # which showed up as "0% joined to a temperature" rather than as
                # an error - the analysis ran to completion with an empty axis.
                "temp": temp_bin(temps.get((st, d))),
            }
            store[key].append((st, day.toordinal(), v, bins, utc, (lon, lat)))
            if sum(len(s) for s in store.values()) % 50000 == 0:
                log(f"  {sum(len(s) for s in store.values()):,} placed")
    return store, {"rows": rows, "dropped": dropped, "skipped": skipped,
                   "clock": dict(clock_classes)}


def main(argv):
    temps = load_temps()
    store, info = read_samples(temps)
    dropped, skipped = info["dropped"], info["skipped"]
    out = {"_what": "Deviation from the same station within a moving window of "
                    "+-W days, itself excluded. Season is continuous; no month.",
           "_moon_caveat": "Full moonlight is about a millionth of sunlight and "
                           "cannot drive photosynthesis. Any moon term here is "
                           "grazer behaviour or spring-neap mixing, not light.",
           "_tide_caveat": "Lunar phase is forcing. Water level is not inferred; "
                           "DMI oceanObs is the observation that would close it.",
           "_types_kept": sorted(POINT_TYPES),
           "skipped_depth_integrated": skipped["type"],
           "skipped_censored_detection_limit": skipped["censored"],
           "skipped_wrong_unit": skipped["unit"],
           "_clock": "Every instant from scripts/clock.py. Samples whose clock is a "
                     "filled-in default, or whose supplier's convention is mixed or "
                     "untestable, are not placed against the sun; they are counted "
                     "in skipped_clock.",
           "skipped_clock": {k: v for k, v in info["clock"].items() if k != "observed"},
           "windows_days": list(WINDOWS), "dropped_impossible": dropped,
           "temperature_station_days": len(temps), "results": {}}

    log(f"\nexcluded: {skipped['type']:,} depth-integrated or pooled samples, "
        f"{skipped['censored']:,} at or beyond a detection limit, "
        f"{skipped['unit']:,} carrying the wrong unit")
    for pname, (key, unit, _, _, _) in PARAMS.items():
        s = store[key]
        if not s:
            continue
        matched = sum(1 for r in s if r[3]["temp"] is not None)
        if temps and not matched:
            raise SystemExit(
                f"{pname}: a temperature table with {len(temps):,} station-days "
                "joined to nothing. That is a key mismatch, not an absence of "
                "data - check the date format on both sides before trusting any "
                "other axis in this run.")
        log(f"\n=== {pname}  ({len(s):,} surface samples, "
            f"{100*matched/len(s):.0f}% joined to a temperature)")
        res = {"n": len(s), "unit": unit,
               "temperature_matched_pct": round(100 * matched / len(s), 1),
               # every placed sample by sun bin, whatever its neighbours: the
               # by_window counts include only samples with a same-station
               # neighbour, so they are not a share of n and must not be read as one
               "sun_counts": dict(collections.Counter(r[3]["sun"] for r in s)),
               "by_window": {}}
        for w in WINDOWS:
            res["by_window"][w] = {}
            log(f"  window +-{w} days")
            for axis, order in (("sun", SUN_ORDER), ("moon", MOON_ORDER),
                                ("tide", TIDE_ORDER), ("temp", TEMP_ORDER)):
                dev, used = deviations(s, w, axis)
                res["by_window"][w][axis] = dev
                shown = [b for b in order if b in dev and dev[b]["n"] >= 50]
                if shown:
                    log(f"    {axis:<5} " + "  ".join(
                        f"{b}={dev[b]['dev']:+.3f}" for b in shown))
        out["results"][key] = res

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"\nwrote {os.path.relpath(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
