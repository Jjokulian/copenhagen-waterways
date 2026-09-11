#!/usr/bin/env python3
"""Station-level facts the place pages print, computed rather than typed.

PLACES.md ranks regions by near-bed oxygen, and AREAS.md measures how far a water
body's own stations disagree inside Roskilde Fjord. Both used to carry those
numbers typed in from a session that stored nothing. This computes them from:

  - the station series (docs/data/areas/stations_series.{json,bin}): the monthly
    median per station and variable - one value per station-month;
  - the water-body overlay (station_waterbody_overlay.json): which water body
    each station falls inside, by point in polygon;
  - data/derived/areas.json: each water body's hovedopland, used as the region
    label, and its area;
  - one pass over each of the CTD and water-chemistry extracts, for the
    hydrogen-sulphide record.

The unit counted as "an observation" is a station-month median, not a raw
measurement: the series was built that way so no station's heavy sampling in one
month outweighs another's single visit.

Reads   docs/data/areas/stations_series.{json,bin}, station_waterbody_overlay.json,
        data/derived/areas.json, data/raw/oda/kemi.csv.gz, data/raw/oda/ctd.csv.gz
Writes  data/derived/station_places.json

    scripts/heavy python3 scripts/station_places.py
"""
import array
import collections
import csv
import gzip
import io
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, write_json

D = os.path.join(ROOT, "docs", "data", "areas")
OUT = os.path.join(DERIVED, "station_places.json")
KEMI = os.path.join(RAW, "oda", "kemi.csv.gz")
CTD = os.path.join(RAW, "oda", "ctd.csv.gz")
BELOW = (2.0, 4.0)            # mg/l: the severe and the moderate iltsvind lines
MIN_STATIONS = 3              # a month counts toward the Roskilde spread with this many
ROSKILDE = (("DKCOAST2", "indre"), ("DKCOAST1", "ydre"))
ROSKILDE_VARS = ("oxy_bed", "sal_surf", "temp_bed")
H2S = ("Svovlbrinte (sulfid)", "Dihydrogensulfid")
YEAR_LINES = (2, 5, 10)       # distinct years a station must span to count as long


def load_series():
    meta = json.load(open(os.path.join(D, "stations_series.json"), encoding="utf-8"))
    raw = open(os.path.join(D, "stations_series.bin"), "rb").read()
    out = {}
    for v in meta["variables"]:
        n, o = v["n"], v["offset"]
        st = array.array("H"); st.frombytes(raw[o:o + 2 * n])
        mo = array.array("H"); mo.frombytes(raw[o + 2 * n:o + 4 * n])
        va = array.array("f"); va.frombytes(raw[o + 4 * n:o + 8 * n])
        out[v["key"]] = (st, mo, va)
    return meta, out


def main(argv):
    meta, series = load_series()
    ids = [s["id"] for s in meta["stations"]]
    ov = json.load(open(os.path.join(D, "station_waterbody_overlay.json"), encoding="utf-8"))
    wbi = dict(zip(ov["station_ids"], ov["waterbody_index"]))
    areas = json.load(open(os.path.join(DERIVED, "areas.json"), encoding="utf-8"))["areas"]
    wb_of = [ov["areas"][wbi[i]] if wbi.get(i, -1) >= 0 else None for i in ids]
    y0 = meta["year0"]

    # ---- near-bed oxygen, by region ------------------------------------------
    st, mo, va = series["oxy_bed"]
    per = collections.defaultdict(list)
    stations = collections.defaultdict(set)
    any_st = set()
    months = []
    for s, m, v in zip(st, mo, va):
        any_st.add(s)
        months.append(m)
        w = wb_of[s]
        if w is None:
            continue
        reg = areas[w]["catchment"]
        per[reg].append(v)
        stations[reg].add(s)
    regions = []
    for reg, vals in per.items():
        n = len(vals)
        regions.append({"region": reg, "observations": n, "stations": len(stations[reg]),
                        "median_mg_l": round(statistics.median(vals), 2),
                        "share_below_low": round(sum(v < BELOW[0] for v in vals) / n, 4),
                        "share_below_high": round(sum(v < BELOW[1] for v in vals) / n, 4)})
    regions.sort(key=lambda r: (-r["share_below_low"], -r["share_below_high"]))
    oxy = {"below_low_mg_l": BELOW[0], "below_high_mg_l": BELOW[1],
           "first_year": y0 + min(months) // 12, "last_year": y0 + max(months) // 12,
           "stations_total": len(any_st),
           "stations_in_regions": sum(r["stations"] for r in regions),
           "regions": regions}
    log(f"  near-bed oxygen: {len(any_st):,} stations, {len(regions)} regions")

    # ---- Roskilde Fjord: stations against each other, and against the season -
    rosk = []
    for key in ROSKILDE_VARS:
        st, mo, va = series[key]
        label = next(v for v in meta["variables"] if v["key"] == key)
        for wb, half in ROSKILDE:
            by_month = collections.defaultdict(list)
            for s, m, v in zip(st, mo, va):
                if wb_of[s] == wb:
                    by_month[m].append(v)
            full = {m: v for m, v in by_month.items() if len(v) >= MIN_STATIONS}
            # the typical between-station spread in one month: the population sd
            # across the stations measuring that month, averaged over the months
            sds = [statistics.pstdev(v) for v in full.values()]
            rngs = [max(v) - min(v) for v in full.values()]
            means = [statistics.fmean(v) for v in full.values()]
            if len(full) < 2:
                continue
            sd_between = statistics.fmean(sds)
            sd_across = statistics.stdev(means)
            rosk.append({"variable": key, "label": label["label"], "depth": label["depth"],
                         "unit": label["unit"], "waterbody": wb, "half": half,
                         "name": areas[wb]["name"], "months": len(full),
                         "sd_between": round(sd_between, 2),
                         "range_between_median": round(statistics.median(rngs), 2),
                         "sd_across": round(sd_across, 2),
                         "ratio": round(sd_between / sd_across, 2)})
    log(f"  Roskilde: {len(rosk)} rows")

    # ---- how long each water body's longest station series runs ------------
    years = collections.defaultdict(set)
    for key, (st, mo, va) in series.items():
        for s, m in zip(st, mo):
            years[s].add(y0 + m // 12)
    longest = {}
    for s, w in enumerate(wb_of):
        if w is not None:
            longest[w] = max(longest.get(w, 0), len(years.get(s, ())))
    lines = []
    for need in YEAR_LINES:
        short = [w for w in areas if longest.get(w, 0) < need]
        lines.append({"min_years": need, "waterbodies": len(short),
                      "km2": round(sum(areas[w]["area_km2"] for w in short), 1)})
    cover = {"series_stations": len(ids), "stations_inside": ov["n_inside"],
             "waterbodies": len(areas),
             "waterbodies_with_station": sum(1 for w in areas if w in longest),
             "lacking_long_station": lines}

    # ---- the hydrogen-sulphide record, in both extracts ----------------------
    # The CTD sonde record and the water-chemistry bottles are separate records of
    # the same substance; each is counted on its own, rows as the extract has them.
    def h2s_in(path):
        rows, names = collections.Counter(), {}
        with gzip.open(path, "rb") as fh:
            for row in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";"):
                if row.get("Parameter") in H2S:
                    s = row.get("ObservationsStedNr")
                    rows[s] += 1
                    names[s] = (row.get("ObservationsStedNavn") or "").strip(), \
                        (row.get("Lokalitetsnavn") or "").strip()
        top, top_n = rows.most_common(1)[0] if rows else (None, 0)
        return {"rows": sum(rows.values()), "stations": len(rows), "top_station": top,
                "top_station_name": names.get(top, ("", ""))[0],
                "top_station_place": names.get(top, ("", ""))[1], "top_station_rows": top_n}
    h2s = {"parameters": list(H2S), "ctd": h2s_in(CTD), "kemi": h2s_in(KEMI)}
    for k in ("ctd", "kemi"):
        log(f"  hydrogen sulphide, {k}: {h2s[k]['rows']:,} rows at {h2s[k]['stations']} "
            f"stations, {h2s[k]['top_station_rows']:,} at {h2s[k]['top_station_name']}")

    write_json(OUT, {"_what": "Station-level facts for PLACES.md and AREAS.md: near-bed "
                              "oxygen by region, the between-station spread inside Roskilde "
                              "Fjord, how long each water body's longest station series runs, "
                              "and the hydrogen-sulphide record.",
                     "_unit": "An observation is a station-month median from the station "
                              "series, not a raw measurement.",
                     "oxy_bed": oxy, "roskilde": {"min_stations": MIN_STATIONS, "rows": rosk},
                     "coverage": cover, "h2s": h2s})
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
