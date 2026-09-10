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
from daylight import solar_elevation, danish_offset, parse_klok
from ephemeris import moon_altitude, moon_illumination, spring_neap

SRC = os.path.join(RAW, "oda", "kemi.csv.gz")
TEMPS = os.path.join(DERIVED, "surface_temp.csv.gz")
OUT = os.path.join(DERIVED, "cycles.json")

PARAMS = {"Oxygen indhold": ("o2", "mg/l", 0.0, 25.0),
          "Oxygenmætning": ("sat", "%", 0.0, 250.0),
          "Klorofyl a": ("chl", "µg/l", 0.0, 500.0)}
MAX_DEPTH = 3.0
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


def main(argv):
    temps = load_temps()
    pos, store = {}, {k: [] for _, (k, _, _, _) in
                      [(p, PARAMS[p]) for p in PARAMS]}
    rows = dropped = 0
    log(f"reading {os.path.relpath(SRC)}")
    with gzip.open(SRC, "rb") as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"),
                                  delimiter=";"):
            rows += 1
            spec = PARAMS.get(row.get("Parameter"))
            if not spec:
                continue
            key, _, lo, hi = spec
            k = parse_klok(row.get("Startklok"))
            d = (row.get("Startdato") or "").strip()
            if not k or len(d) != 8 or not d.isdigit():
                continue
            try:
                dep = float((row.get("GennemsnitsDybde_m") or "").replace(",", "."))
                v = float((row.get("Resultat") or "").replace(",", "."))
            except ValueError:
                continue
            if dep > MAX_DEPTH:
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
            utc = (dt.datetime.combine(day, dt.time(k[0], k[1]))
                   - dt.timedelta(hours=danish_offset(day)))
            frac, _ = moon_illumination(utc)
            bins = {
                "sun": sun_bin(solar_elevation(lat, lon, utc)),
                "moon": moon_bin(moon_altitude(lat, lon, utc), frac),
                "tide": spring_neap(frac),
                "temp": temp_bin(temps.get((st, f"{d[:4]}-{d[4:6]}-{d[6:]}"))),
            }
            store[key].append((st, day.toordinal(), v, bins))
            if sum(len(s) for s in store.values()) % 50000 == 0:
                log(f"  {sum(len(s) for s in store.values()):,} placed")

    out = {"_what": "Deviation from the same station within a moving window of "
                    "+-W days, itself excluded. Season is continuous; no month.",
           "_moon_caveat": "Full moonlight is about a millionth of sunlight and "
                           "cannot drive photosynthesis. Any moon term here is "
                           "grazer behaviour or spring-neap mixing, not light.",
           "_tide_caveat": "Lunar phase is forcing. Water level is not inferred; "
                           "DMI oceanObs is the observation that would close it.",
           "windows_days": list(WINDOWS), "dropped_impossible": dropped,
           "temperature_station_days": len(temps), "results": {}}

    for pname, (key, unit, _, _) in PARAMS.items():
        s = store[key]
        if not s:
            continue
        matched = sum(1 for r in s if r[3]["temp"] is not None)
        log(f"\n=== {pname}  ({len(s):,} surface samples, "
            f"{100*matched/len(s):.0f}% joined to a temperature)")
        res = {"n": len(s), "unit": unit,
               "temperature_matched_pct": round(100 * matched / len(s), 1),
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
