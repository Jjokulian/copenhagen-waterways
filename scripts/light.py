#!/usr/bin/env python3
"""K11: is there enough light at the bed for anything to root there?

Eelgrass has a hard requirement, not a preference. Below roughly 11-14% of surface
irradiance at the bed it does not grow slowly; it dies. That threshold is what the
Danish Kd indicator is built on - the environmental target for light attenuation is
derived by assuming eelgrass needs about 14% of surface light at its target depth.

So the indicator and the requirement are two ends of the same calculation, and the
calculation can be run directly from the raw record instead of inherited from an
assessment. ODA publishes, per cast:

    LyssvaekkelsesKoefficient   Kd, the attenuation coefficient, fitted per cast
    Lysprocent                  the percentage of surface light at each measured depth
    KorrelationsKoefficient     the fit quality of that regression
    Dybde (m)                   the depth each Lysprocent belongs to

and, in the Maaledybde topic, BundDybde_m - the actual depth of the seabed under
the ship. Which makes the question arithmetic:

    light at the bed  =  100 * exp(-Kd * bottom depth)
    potential depth   =  -ln(0.11) / Kd     the deepest a plant could still root

This computes both, per cast, and then asks the question the indicator is supposed
to answer and never quite does: has the potential depth limit improved over the
record, and where?

Group I applies to the answer as much as to anyone else's. The trend is recomputed
on stations present throughout the record, so a change in *where* Denmark measures
cannot masquerade as a change in the sea.

Reads   data/raw/oda/lys.csv.gz, data/raw/oda/maaledybde.csv.gz
Writes  data/derived/light.json, docs/LIGHT.md

Usage:  python3 scripts/light.py
"""
import collections
import csv
import gzip
import math
import re
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, write_json, write_doc
import calendar
import live

ODA = os.path.join(RAW, "oda")
OUT = os.path.join(ROOT, "docs", "LIGHT.md")

# The eelgrass light requirement, as a share of surface irradiance at the bed.
# DCE derive the Kd environmental target from the upper end of this range.
REQ_LO, REQ_HI = 0.11, 0.14
GROWTH = range(3, 10)          # March-September, the eelgrass growing season
MIN_FIT = 0.9                  # discard casts whose Kd regression fits badly
MIN_STATION_YEARS = 8          # years of casts before a station gets its own trend
STABLE_WINDOW = 5              # years at each end a station must appear in
MIN_PROFILE_POINTS = 8         # readings a profile needs before it is split in halves
MIN_PROFILE_SPAN = 2.0         # metres a profile must span to be split
START_SPLIT = 2.0              # m: profiles starting above this are "shallow-start"
MIN_BAND_CASTS = 150           # casts a start-depth band needs to be shown
SHALLOW_SECCHI = 5             # m: bottom depth that counts as shallow for Secchi eras
LIGHT_JSON = os.path.join(DERIVED, "light.json")


def num(x):
    x = (x or "").strip().replace(",", ".")
    try:
        return float(x)
    except ValueError:
        return None


def read_casts():
    """One record per light cast: station, date, Kd, and the fit quality."""
    p = os.path.join(ODA, "lys.csv.gz")
    casts, dropped = {}, collections.Counter()
    with gzip.open(p, "rt", encoding="iso-8859-1") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            kd = num(row.get("LyssvaekkelsesKoefficient"))
            d = (row.get("Dato") or "").strip()
            if kd is None or kd <= 0:
                dropped["no usable Kd"] += 1
                continue
            if len(d) < 8 or not d[:8].isdigit():
                dropped["no usable date"] += 1
                continue
            r = num(row.get("KorrelationsKoefficient"))
            key = (row["ObservationsStedNr"], d, row.get("UndersøgelseNr") or "")
            casts[key] = {
                "key": key,
                "station": row["ObservationsStedNr"],
                "name": (row.get("ObservationsStedNavn") or "").strip(),
                "year": int(d[:4]), "month": int(d[4:6]), "date": d[:8],
                "kd": kd, "fit": r,
                "lat": num(row.get("Bredde")), "lon": num(row.get("Længde")),
                "ta": (row.get("TekniskAnvisningAnvendt") or "").strip(),
                "supplier": (row.get("DataleverandørNavn") or "").strip(),
            }
    return list(casts.values()), dropped


def read_secchi():
    """Secchi depth against bottom depth, and how often the disc was on the bed.

    A Secchi disc cannot be seen deeper than the bottom, so in shallow water the
    recorded "clarity" is the depth of the seabed and not a property of the water.
    ODA is honest about it and publishes the flag - SigtTilBund, sight-to-bottom -
    which is what makes this checkable at all.

    The extract behind this was itself truncated once: run without an explicit
    period it returned 4,044 rows over two years at 194 stations, against 151,204
    rows over 1980-2026 at 1,429 stations with the period set. Numbers computed on
    the truncated file overstated the shallow-water censored share by about a
    factor of 1.7. See the guard in fetch_oda.py.
    """
    p = os.path.join(ODA, "maaledybde.csv.gz")
    if not os.path.exists(p):
        return None
    rows, flag = [], collections.Counter()
    with gzip.open(p, "rt", encoding="iso-8859-1") as fh:
        for r in csv.DictReader(fh, delimiter=";"):
            sec, bot = num(r.get("SigtDybde_m")), num(r.get("BundDybde_m"))
            d = (r.get("StartDato") or "").strip()
            if not sec or sec <= 0:
                continue
            flag[(r.get("SigtTilBund") or "").strip()] += 1
            if bot and bot > 0 and len(d) >= 4 and d[:4].isdigit():
                rows.append((sec, bot, int(d[:4])))
    if not rows:
        return None
    at_bed = lambda rs: 100 * sum(1 for s, b, _ in rs if s >= b - 0.01) / len(rs)
    bands = []
    for lo, hi in ((0, 5), (5, 10), (10, 20), (20, 40), (40, 200)):
        sub = [r for r in rows if lo <= r[1] < hi]
        if len(sub) < 50:
            continue
        bands.append({"from": lo, "to": hi, "n": len(sub),
                      "median_secchi": round(statistics.median(r[0] for r in sub), 1),
                      "at_bed_pct": round(at_bed(sub), 1)})
    eras = []
    for lo, hi in ((1980, 1995), (1995, 2005), (2005, 2015), (2015, 2027)):
        sub = [r for r in rows if lo <= r[2] < hi]
        sh = [r for r in sub if r[1] < SHALLOW_SECCHI]
        if len(sub) < 50:
            continue
        eras.append({"from": lo, "to": hi - 1, "n": len(sub),
                     "at_bed_pct": round(at_bed(sub), 1),
                     "n_shallow": len(sh),
                     "shallow_at_bed_pct": round(at_bed(sh), 1) if len(sh) > 30 else None})
    return {"n_secchi": sum(flag.values()), "flag": dict(flag),
            "n_paired": len(rows), "years": [min(r[2] for r in rows),
                                             max(r[2] for r in rows)],
            "at_bed_pct": round(at_bed(rows), 1), "bands": bands, "eras": eras}


def read_profiles():
    """Refit each cast from its own measurements, top half against bottom half.

    ODA publishes one Kd per cast, fitted over the whole profile, and the file
    also carries the measurements it was fitted to - one row per depth, typically
    every half metre. Refitting the halves separately asks a question the single
    number cannot answer: **is the attenuation the same all the way down?**

    If the water were uniform and the instrument ideal, the two halves would agree.
    They do not, and the direction is the informative part.
    """
    p = os.path.join(ODA, "lys.csv.gz")
    out, cur, buf = {}, None, []

    def slope(zs, ls):
        n = len(zs)
        zm = sum(zs) / n
        lm = sum(ls) / n
        den = sum((z - zm) ** 2 for z in zs)
        if den <= 0:
            return None
        return sum((z - zm) * (l - lm) for z, l in zip(zs, ls)) / den

    def flush():
        nonlocal buf
        if cur is not None and len(buf) >= MIN_PROFILE_POINTS:
            buf.sort()
            zs = [b[0] for b in buf]
            ls = [b[1] for b in buf]
            if zs[-1] - zs[0] >= MIN_PROFILE_SPAN:
                mid = len(zs) // 2
                su = slope(zs[:mid + 1], ls[:mid + 1])
                sl = slope(zs[mid:], ls[mid:])
                if su is not None and sl is not None and su < 0 and sl < 0:
                    out[cur] = {"kd_upper": -su, "kd_lower": -sl,
                                "z0": zs[0], "zmax": zs[-1], "n": len(zs)}
        buf = []

    with gzip.open(p, "rt", encoding="iso-8859-1") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            key = (row["ObservationsStedNr"], (row.get("Dato") or "").strip(),
                   row.get("UndersøgelseNr") or "")
            if key != cur:
                flush()
                cur = key
            z = num(row.get("Dybde (m)"))
            pct = num(row.get("Lysprocent"))
            if z is not None and pct is not None and pct > 0:
                buf.append((z, math.log(pct)))
    flush()
    return out


def read_depths():
    """Bottom depth per station, from the Maaledybde topic."""
    p = os.path.join(ODA, "maaledybde.csv.gz")
    if not os.path.exists(p):
        return {}, {}
    bydate, bystation = {}, collections.defaultdict(list)
    with gzip.open(p, "rt", encoding="iso-8859-1") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            b = num(row.get("BundDybde_m"))
            if b is None or b <= 0:
                continue
            st = row["ObservationsstedNr"]
            d = (row.get("StartDato") or "").strip()
            bydate[(st, d)] = b
            bystation[st].append(b)
    return bydate, {k: statistics.median(v) for k, v in bystation.items()}


def slope_per_decade(pairs):
    """OLS slope of y on year, per decade, with its own n."""
    pairs = [(x, y) for x, y in pairs if y is not None]
    if len(pairs) < 12:
        return None, len(pairs)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None, len(pairs)
    b = sum((xs[i] - mx) * (ys[i] - my) for i in range(len(xs))) / den
    return 10.0 * b, len(pairs)


def analyse():
    casts, dropped = read_casts()
    bydate, bystation = read_depths()
    log(f"  {len(casts):,} light casts; dropped {dict(dropped)}")

    good = [c for c in casts if c["fit"] is None or c["fit"] >= MIN_FIT]
    season = [c for c in good if c["month"] in GROWTH]
    for c in season:
        # the deepest a plant needing this share of surface light could root
        c["z_lo"] = -math.log(REQ_HI) / c["kd"]     # 14% requirement, shallower
        c["z_hi"] = -math.log(REQ_LO) / c["kd"]     # 11% requirement, deeper
        # the sounding from the same visit if there is one, else the station's
        # median sounding. (An earlier version looked the date up as "" and so
        # always fell back to the median, while the page said "under the ship".)
        same = bydate.get((c["station"], c["date"]))
        b = same or bystation.get(c["station"])
        c["bottom_source"] = "same day" if same else ("station median" if b else None)
        c["bottom"] = b
        c["at_bed"] = 100 * math.exp(-c["kd"] * b) if b else None

    years = sorted({c["year"] for c in season})
    by_year = collections.defaultdict(list)
    for c in season:
        by_year[c["year"]].append(c)

    # trend on every cast, and again on stations present at both ends, so that a
    # change in where Denmark measures cannot look like a change in the sea
    first, last = years[0], years[-1]
    early = {c["station"] for c in season if c["year"] <= first + STABLE_WINDOW - 1}
    late = {c["station"] for c in season if c["year"] >= last - STABLE_WINDOW + 1}
    stable = early & late
    all_pairs = [(c["year"], c["z_hi"]) for c in season]
    stable_pairs = [(c["year"], c["z_hi"]) for c in season if c["station"] in stable]
    s_all, n_all = slope_per_decade(all_pairs)
    s_stable, n_stable = slope_per_decade(stable_pairs)

    per_station = {}
    by_st = collections.defaultdict(list)
    for c in season:
        by_st[c["station"]].append(c)
    for st, cs in by_st.items():
        if len({c["year"] for c in cs}) < MIN_STATION_YEARS:
            continue
        s, n = slope_per_decade([(c["year"], c["z_hi"]) for c in cs])
        if s is None:
            continue
        per_station[st] = {
            "name": cs[0]["name"], "n_casts": len(cs),
            "years": [min(c["year"] for c in cs), max(c["year"] for c in cs)],
            "median_kd": round(statistics.median(c["kd"] for c in cs), 3),
            "median_z11": round(statistics.median(c["z_hi"] for c in cs), 2),
            "trend_m_per_decade": round(s, 3),
            "lat": cs[0]["lat"], "lon": cs[0]["lon"],
        }

    withbed = [c for c in season if c["at_bed"] is not None]
    meets = [c for c in withbed if c["at_bed"] >= 100 * REQ_LO]

    secchi = read_secchi()
    prof = read_profiles()
    log(f"  {len(prof):,} casts refittable in halves")
    geom, deep = [], []
    for lo, hi in ((0.0, 0.6), (0.6, 1.1), (1.1, 2.1), (2.1, 3.1),
                   (3.1, 5.1), (5.1, 30.0)):
        band = [prof[c["key"]] for c in season
                if c["key"] in prof and lo <= prof[c["key"]]["z0"] < hi]
        if len(band) < MIN_BAND_CASTS:
            continue
        rs = [b["kd_lower"] / b["kd_upper"] for b in band]
        geom.append({"from": lo, "to": hi, "n": len(band),
                     "kd_upper": round(statistics.median(b["kd_upper"] for b in band), 3),
                     "kd_lower": round(statistics.median(b["kd_lower"] for b in band), 3),
                     "ratio": round(statistics.median(rs), 3),
                     "steepens": round(100 * sum(1 for r in rs if r > 1) / len(rs), 1)})
    deep = [c for c in season if c["key"] in prof and prof[c["key"]]["z0"] >= START_SPLIT]
    shallow = [c for c in season if c["key"] in prof and prof[c["key"]]["z0"] < START_SPLIT]

    return {
        "n_casts_total": len(casts), "n_casts_good_fit": len(good),
        "n_growth_season": len(season),
        "n_stations": len({c["station"] for c in season}),
        "years": [first, last],
        "casts_per_year": {str(y): len(by_year[y]) for y in years},
        "kd": {
            "median": round(statistics.median(c["kd"] for c in season), 3),
            "p10": round(sorted(c["kd"] for c in season)[len(season) // 10], 3),
            "p90": round(sorted(c["kd"] for c in season)[9 * len(season) // 10], 3),
        },
        "z11": {
            "median": round(statistics.median(c["z_hi"] for c in season), 2),
            "p10": round(sorted(c["z_hi"] for c in season)[len(season) // 10], 2),
            "p90": round(sorted(c["z_hi"] for c in season)[9 * len(season) // 10], 2),
        },
        "z14_median": round(statistics.median(c["z_lo"] for c in season), 2),
        "trend": {
            "all_casts_m_per_decade": None if s_all is None else round(s_all, 3),
            "n_all": n_all,
            "stable_stations_m_per_decade": None if s_stable is None else round(s_stable, 3),
            "n_stable": n_stable, "n_stable_stations": len(stable),
        },
        "yearly_median_z11": {str(y): round(statistics.median(c["z_hi"]
                                                             for c in by_year[y]), 2)
                              for y in years},
        "bed": {
            "n_with_bottom_depth": len(withbed),
            "n_meeting_11pct": len(meets),
            "share_meeting": round(len(meets) / len(withbed), 3) if withbed else None,
            "n_same_day": sum(1 for c in withbed if c["bottom_source"] == "same day"),
            "n_station_median": sum(1 for c in withbed if c["bottom_source"] == "station median"),
        },
        # the choices this analysis rests on, stored so the page prints them from here
        "params": {"req_lo_pct": round(100 * REQ_LO), "req_hi_pct": round(100 * REQ_HI),
                   "min_fit": MIN_FIT, "growth_first_month": GROWTH[0],
                   "growth_last_month": GROWTH[-1], "min_station_years": MIN_STATION_YEARS,
                   "stable_window_years": STABLE_WINDOW,
                   "min_profile_points": MIN_PROFILE_POINTS,
                   "min_profile_span_m": MIN_PROFILE_SPAN, "start_split_m": START_SPLIT,
                   "min_band_casts": MIN_BAND_CASTS, "shallow_secchi_m": SHALLOW_SECCHI},
        "geometry": geom,
        "start_depth": {
            "n_profiles": len(prof),
            "n_deep_start": len(deep), "n_shallow_start": len(shallow),
            "z11_deep_start": round(statistics.median(c["z_hi"] for c in deep), 2)
            if deep else None,
            "z11_shallow_start": round(statistics.median(c["z_hi"] for c in shallow), 2)
            if shallow else None,
            "kd_deep_start": round(statistics.median(c["kd"] for c in deep), 3)
            if deep else None,
            "kd_shallow_start": round(statistics.median(c["kd"] for c in shallow), 3)
            if shallow else None,
        },
        "secchi": secchi,
        "per_station": per_station,
        "suppliers": dict(collections.Counter(c["supplier"] for c in season).most_common(6)),
    }


def render(d):
    """d is light.json loaded live: every number below carries its field."""
    o = []
    a = o.append
    t, p = d["trend"], d["params"]
    lo, hi = p["req_lo_pct"], p["req_hi_pct"]
    months = f"{calendar.month_name[p['growth_first_month']]}–{calendar.month_name[p['growth_last_month']]}"
    a("# Is there enough light at the bed?\n")
    a(f"Eelgrass has a requirement, not a preference. Below roughly **{lo}–{hi}% of "
      "surface light at the seabed** it does not grow slowly — it dies. The Danish "
      "light-attenuation target is built on the same number from the other "
      "direction: the environmental objective for Kd is derived by assuming "
      f"eelgrass needs about {hi}% of surface irradiance at the depth it is supposed "
      "to reach.\n")
    a("So the indicator and the requirement are two ends of one calculation, and "
      "the calculation can be run from the raw record rather than inherited from an "
      "assessment. ODA publishes the attenuation coefficient per cast, with the fit "
      "quality of the regression that produced it. Two lines of arithmetic follow:\n")
    a("```\nlight at the bed   =  100 · exp(−Kd · bottom depth)\n"
      "potential depth    =  −ln(r) / Kd      r the light requirement: the deepest a plant could root\n```\n")

    a("## What the record contains\n")
    a("| | |\n|---|---:|")
    a(f"| Light casts in the record | {d['n_casts_total']:,} |")
    a(f"| …with a usable Kd regression (r ≥ {p['min_fit']}, or no fit reported) | {d['n_casts_good_fit']:,} |")
    a(f"| …in the {months} growing season | {d['n_growth_season']:,} |")
    a(f"| Stations | {d['n_stations']:,} |")
    a(f"| Years covered | {d['years'][0]}–{d['years'][1]} |")
    a("")
    a(f"Attenuation runs from Kd = {d['kd']['p10']} (p10, the clearest casts) to "
      f"{d['kd']['p90']} (p90, the murkiest), median {d['kd']['median']}.\n")

    a("## The depth a plant could reach\n")
    a(f"Converting each cast to the deepest point still receiving {lo}% of surface "
      "light:\n")
    a(f"> Median **{d['z11']['median']} m**. The clearest casts (p90) reach "
      f"{d['z11']['p90']} m; the murkiest (p10) reach only {d['z11']['p10']} m. At "
      f"the stricter {hi}% requirement the median falls to **{d['z14_median']} m**.\n")
    a("That is the whole eelgrass question in one number per cast, and it is "
      "computed from a measurement rather than from a model of a reference "
      "condition.\n")

    a("## Has it improved?\n")
    a("This is the question decades of load reduction are supposed to have "
      "answered.\n")
    a("| | metres per decade | casts |")
    a("|---|---:|---:|")
    a(f"| All casts | {t['all_casts_m_per_decade']} | {t['n_all']:,} |")
    a(f"| Only stations present at both ends of the record "
      f"({t['n_stable_stations']} stations) | {t['stable_stations_m_per_decade']} "
      f"| {t['n_stable']:,} |")
    a("")
    a(f"*Both ends* means casts in the first and in the last {p['stable_window_years']} "
      f"years of the record; {t['n_stable_stations']} stations qualify, so the second "
      "row rests on those alone.\n")
    a("The second row is the check that matters, and it is the one nobody runs. If "
      "a trend appears on all casts but not on the stations measured throughout, it "
      "is a trend in **where Denmark chose to measure**, not in the water — "
      f"hypothesis {live.ref('I1', title=True)}, put to the record rather than "
      "asserted.\n")

    if d["bed"]["n_with_bottom_depth"]:
        b = d["bed"]
        a("## And does the light actually reach the bed?\n")
        a(f"Where a bottom depth is known ({b['n_with_bottom_depth']:,} casts: "
          f"{b['n_same_day']:,} from a sounding on the same day, "
          f"{b['n_station_median']:,} from the station's median sounding), the share "
          f"where the seabed receives at least {lo}% of surface light is "
          f"**{100 * b['share_meeting']:.0f}%**.\n")

    st = sorted(d["per_station"].values(), key=lambda s: s["trend_m_per_decade"])
    if st:
        a("## Station by station\n")
        a(f"Stations with at least {p['min_station_years']} years of growing-season "
          "casts, sorted by trend: the darkening end and the brightening end. A "
          "negative number is water getting darker.\n")
        a(f"| station | casts | years | median Kd | median depth at {lo}% | m/decade |")
        a("|---|---:|---|---:|---:|---:|")
        shown = st if len(st) <= 20 else st[:10] + [None] + st[-10:]
        for s in shown:
            if s is None:
                a("| … | | | | | |")
                continue
            name = s["name"][:34]
            name = f"`{name}`" if re.search(r"\d", name) else name
            a(f"| {name} | {s['n_casts']} | {s['years'][0]}–{s['years'][1]} "
              f"| {s['median_kd']} | {s['median_z11']} m "
              f"| {s['trend_m_per_decade']:+.2f} |")
        a("")

    g = d.get("geometry") or []
    sd = d.get("start_depth") or {}
    if g:
        a("## The number depends on where the sensor started\n")
        a("Every figure above rests on Kd, and Kd is a straight line fitted to the "
          "logarithm of light against depth. That fit assumes attenuation is the "
          "same all the way down. ODA publishes the measurements the line was "
          "fitted to, so the assumption can be checked rather than granted: refit "
          f"the top half of each profile against the bottom half. {sd['n_profiles']:,} "
          f"casts carry enough points to allow it — at least {p['min_profile_points']} "
          f"readings spanning at least {p['min_profile_span_m']} m.\n")
        a("| profile starts at | casts | Kd top half | Kd bottom half | ratio | "
          "steepens with depth |")
        a("|---|---:|---:|---:|---:|---:|")
        for r in g:
            a(f"| {r['from']:.1f} – {r['to']:.1f} m | {r['n']:,} | {r['kd_upper']} | "
              f"{r['kd_lower']} | **{r['ratio']}** | {r['steepens']}% |")
        a("")
        steep = [r["steepens"] for r in g]
        ratios = [r["ratio"] for r in g]
        rising = all(x <= y for x, y in zip(ratios, ratios[1:]))
        a("**The bottom half attenuates less, and the gap closes the deeper the "
          "profile begins.** That ordering is the whole result. It runs opposite to "
          "resuspension — a turbid layer over the bed would make the bottom half "
          f"steeper, and it does so in only {min(steep):.0f}–{max(steep):.0f}% of "
          "casts, outweighed on average by something else.\n")
        a("The something else is that a PAR sensor counts photons across the whole "
          "band without distinguishing them, and water absorbs the band unevenly - as "
          "an earlier version of this page put it, "
          + live.was("ea77da4", "docs/LIGHT.md",
                       'band unevenly — @@. The red')
          + ". The red part of the light is gone near the "
          "surface, and what continues downward is the fraction water attenuates "
          "least. So the apparent broadband Kd falls with depth **in perfectly "
          "uniform water**, purely because the surviving spectrum has shifted. If "
          "that is the mechanism, the effect must fade for profiles that begin below "
          "the red-absorbing layer, because the red is already gone. It does: the "
          f"ratio runs from {g[0]['ratio']} for profiles starting at the surface to "
          f"{g[-1]['ratio']} for those starting below {g[-1]['from']} m, "
          + ("rising at every step" if rising else "rising overall though not at every step")
          + ".\n")
        a("> **What follows is that Kd measured this way is not a property of the "
          "water.** It is a property of the water and the depth window jointly. Two "
          "casts in identical water, one begun near the surface and one begun "
          "deeper, return different numbers. The indicator, the target derived from "
          "it, and every figure on this page inherit that.\n")
        if sd.get("z11_deep_start") and sd.get("z11_shallow_start"):
            a(f"Splitting the growth-season casts on where they started: "
              f"{sd['n_shallow_start']:,} began above {p['start_split_m']} m and give a "
              f"median Kd of {sd['kd_shallow_start']} and a median depth reaching "
              f"{lo}% of {sd['z11_shallow_start']} m; {sd['n_deep_start']:,} began "
              f"below {p['start_split_m']} m and give {sd['kd_deep_start']} and "
              f"{sd['z11_deep_start']} m. Neither is the true number. They are two "
              "answers from one record, separated by a choice nobody documents "
              "making.\n")
        a("The measurement that would separate the two explanations — spectral "
          "attenuation rather than one broadband coefficient — is not made anywhere "
          "in the Danish programme. A single number cannot say whether the light "
          "stopped because something was in the water or because water is red-"
          f"absorbing and the sensor started shallow. That is {live.ref('Z8', title=True)} "
          "again, one layer below where it is stated.\n")
    sc = d.get("secchi")
    if sc:
        bands = sc["bands"]
        a("## The other optical record measures the seabed when the water is shallow\n")
        a("Kd is not the only transparency number Denmark holds. There is also "
          f"Secchi depth — a white disc lowered until it disappears — {sc['n_secchi']:,} "
          f"readings, {sc['n_paired']:,} of them paired with a bottom depth, "
          f"{sc['years'][0]}–{sc['years'][1]}. It has one hard limit: **a disc cannot "
          "be seen deeper than the bottom.** Where the water is shallower than the "
          "water is clear, the number recorded is the depth of the seabed.\n")
        a("ODA is straightforward about this and publishes the flag — "
          "`SigtTilBund`, sight-to-bottom — which is the only reason any of this "
          f"can be checked. It is set on {sc['flag']['True']:,} of "
          f"{sc['n_secchi']:,} readings.\n")
        a("| bottom depth | readings | median Secchi | disc reached the bed |")
        a("|---|---:|---:|---:|")
        for b in bands:
            a(f"| {b['from']}–{b['to']} m | {b['n']:,} | {b['median_secchi']} m | "
              f"**{b['at_bed_pct']}%** |")
        a("")
        rare = next((b for b in bands if b["at_bed_pct"] < 1), None)
        a(f"So in water under {bands[0]['to']} m, {bands[0]['at_bed_pct']}% of the "
          "readings are measurements of bathymetry wearing the units of clarity."
          + (f" From {rare['from']} m down it essentially stops happening "
             f"({rare['at_bed_pct']}%)." if rare else "")
          + " The censoring is not an error — it is what the instrument does — but "
          "it is **one-sided**: it can only make the water look less clear than it "
          "is, never more, and only in the shallows.\n")
        a("**And the censored share is not constant, which is the part that "
          "matters for any series built from it.**\n")
        a(f"| period | readings | disc reached the bed | in water under {p['shallow_secchi_m']} m |")
        a("|---|---:|---:|---:|")
        for e in sc["eras"]:
            sh = "—" if e["shallow_at_bed_pct"] is None else f"{e['shallow_at_bed_pct']}%"
            a(f"| {e['from']}–{e['to']} | {e['n']:,} | {e['at_bed_pct']}% | {sh} |")
        a("")
        a("A time-varying censored fraction is a time-varying bias, so a Secchi "
          "trend computed across these eras is partly a trend in how often the "
          "instrument hit the ground. **Why it varies is not settled here.** "
          "Cleaner water would raise it, because a disc that can be seen further "
          "reaches the bed more often; so would a shift of effort toward shallower "
          "stations; so would a change in field practice. Those are not separable "
          "from this table, and the direction of the resulting bias is "
          "uncomfortable: a genuine improvement in clarity partly hides itself, "
          "because the readings that would show it are the ones that get capped.\n")
        a("The same caution as the Kd section, arrived at from the other side. "
          "Neither of Denmark's two transparency records is a clean measurement of "
          "the water alone — one depends on where the sensor started, the other on "
          "how deep the sea is underneath it.\n")
    a("## What this does and does not settle\n")
    a("It settles the arithmetic, which was never in doubt, and it puts a number on "
      "the thing the Kd indicator is a proxy for. What it cannot settle is *why* the "
      "light is where it is. Kd is one broadband number and its causes do not "
      "separate — phytoplankton, resuspended mineral sediment, coloured dissolved "
      "organic matter and drifted detritus all darken water identically at this "
      f"resolution. That is {live.ref('Z8')}, and it is why a Kd exceedance is "
      "attributed to algae by assumption rather than by measurement.\n")
    a("It also cannot see the shading that happens *after* the light has passed "
      "through the water. Epiphytes growing on the leaf shade the host at the blade "
      f"surface, where no water-column measurement reaches ({live.ref('Z9', title=True)}), "
      "so the nutrient-to-light pathway can operate with every number on this page "
      "looking acceptable.\n")
    return "\n".join(o) + "\n"


def main(argv=()):
    """Analyse the raw record, store it, and render the page from what was stored.
    --render renders from the stored data/derived/light.json without re-reading."""
    if "--render" not in argv:
        d = analyse()
        write_json(LIGHT_JSON, d)
        log(f"  {d['n_growth_season']:,} growth-season casts, {d['n_stations']} stations")
    try:
        write_doc(OUT, render(live.live_json(LIGHT_JSON)))
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote docs/LIGHT.md ({os.path.getsize(OUT):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
