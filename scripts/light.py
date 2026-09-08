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
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, write_json

ODA = os.path.join(RAW, "oda")
OUT = os.path.join(ROOT, "docs", "LIGHT.md")

# The eelgrass light requirement, as a share of surface irradiance at the bed.
# DCE derive the Kd environmental target from the upper end of this range.
REQ_LO, REQ_HI = 0.11, 0.14
GROWTH = range(3, 10)          # March-September, the eelgrass growing season
MIN_FIT = 0.9                  # discard casts whose Kd regression fits badly


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
                "station": row["ObservationsStedNr"],
                "name": (row.get("ObservationsStedNavn") or "").strip(),
                "year": int(d[:4]), "month": int(d[4:6]),
                "kd": kd, "fit": r,
                "lat": num(row.get("Bredde")), "lon": num(row.get("Længde")),
                "ta": (row.get("TekniskAnvisningAnvendt") or "").strip(),
                "supplier": (row.get("DataleverandørNavn") or "").strip(),
            }
    return list(casts.values()), dropped


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
        b = bydate.get((c["station"], "")) or bystation.get(c["station"])
        c["bottom"] = b
        c["at_bed"] = 100 * math.exp(-c["kd"] * b) if b else None

    years = sorted({c["year"] for c in season})
    by_year = collections.defaultdict(list)
    for c in season:
        by_year[c["year"]].append(c)

    # trend on every cast, and again on stations present at both ends, so that a
    # change in where Denmark measures cannot look like a change in the sea
    first, last = years[0], years[-1]
    early = {c["station"] for c in season if c["year"] <= first + 4}
    late = {c["station"] for c in season if c["year"] >= last - 4}
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
        if len({c["year"] for c in cs}) < 8:
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
        },
        "per_station": per_station,
        "suppliers": dict(collections.Counter(c["supplier"] for c in season).most_common(6)),
    }


def render(d):
    o = []
    a = o.append
    t = d["trend"]
    a("# Is there enough light at the bed?\n")
    a("Eelgrass has a requirement, not a preference. Below roughly **11–14% of "
      "surface light at the seabed** it does not grow slowly — it dies. The Danish "
      "light-attenuation target is built on the same number from the other "
      "direction: the environmental objective for Kd is derived by assuming "
      "eelgrass needs about 14% of surface irradiance at the depth it is supposed "
      "to reach.\n")
    a("So the indicator and the requirement are two ends of one calculation, and "
      "the calculation can be run from the raw record rather than inherited from an "
      "assessment. ODA publishes the attenuation coefficient per cast, with the fit "
      "quality of the regression that produced it. Two lines of arithmetic follow:\n")
    a("```\nlight at the bed   =  100 · exp(−Kd · bottom depth)\n"
      "potential depth    =  −ln(0.11) / Kd      the deepest a plant could root\n```\n")

    a("## What the record contains\n")
    a(f"| | |\n|---|---:|")
    a(f"| Light casts in the record | {d['n_casts_total']:,} |")
    a(f"| …with a usable Kd regression (r ≥ {MIN_FIT}) | {d['n_casts_good_fit']:,} |")
    a(f"| …in the March–September growing season | {d['n_growth_season']:,} |")
    a(f"| Stations | {d['n_stations']:,} |")
    a(f"| Years covered | {d['years'][0]}–{d['years'][1]} |")
    a("")
    a(f"Attenuation runs from Kd = {d['kd']['p10']} at the clearest tenth to "
      f"{d['kd']['p90']} at the murkiest, median {d['kd']['median']}.\n")

    a("## The depth a plant could reach\n")
    a(f"Converting each cast to the deepest point still receiving 11% of surface "
      f"light:\n")
    a(f"> Median **{d['z11']['median']} m**. The clearest tenth of casts reach "
      f"{d['z11']['p90']} m; the murkiest tenth reach only {d['z11']['p10']} m. At "
      f"the stricter 14% requirement the median falls to **{d['z14_median']} m**.\n")
    a("That is the whole eelgrass question in one number per cast, and it is "
      "computed from a measurement rather than from a model of a reference "
      "condition.\n")

    a("## Has it improved?\n")
    a("This is the question thirty-five years of load reduction is supposed to have "
      "answered.\n")
    a("| | metres per decade | casts |")
    a("|---|---:|---:|")
    a(f"| All casts | {t['all_casts_m_per_decade']} | {t['n_all']:,} |")
    a(f"| Only stations present at both ends of the record "
      f"({t['n_stable_stations']} stations) | {t['stable_stations_m_per_decade']} "
      f"| {t['n_stable']:,} |")
    a("")
    a("The second row is the check that matters, and it is the one nobody runs. If "
      "a trend appears on all casts but not on the stations measured throughout, it "
      "is a trend in **where Denmark chose to measure**, not in the water — the `I1` "
      "hypothesis, tested rather than asserted.\n")

    if d["bed"]["n_with_bottom_depth"]:
        b = d["bed"]
        a("## And does the light actually reach the bed?\n")
        a(f"Where the bottom depth under the ship is also recorded "
          f"({b['n_with_bottom_depth']:,} casts), the share where the seabed "
          f"receives at least 11% of surface light is "
          f"**{100*b['share_meeting']:.0f}%**.\n")

    st = sorted(d["per_station"].values(), key=lambda s: s["trend_m_per_decade"])
    if st:
        a("## Station by station\n")
        a("Stations with at least eight years of growing-season casts, sorted by "
          "trend. A negative number is water getting darker.\n")
        a("| station | casts | years | median Kd | median depth at 11% | m/decade |")
        a("|---|---:|---|---:|---:|---:|")
        for s in st[:10] + ([("…",)] if len(st) > 20 else []) + st[-10:]:
            if isinstance(s, tuple):
                a("| … | | | | | |")
                continue
            a(f"| {s['name'][:34]} | {s['n_casts']} | {s['years'][0]}–{s['years'][1]} "
              f"| {s['median_kd']} | {s['median_z11']} m "
              f"| {s['trend_m_per_decade']:+.2f} |")
        a("")

    a("## What this does and does not settle\n")
    a("It settles the arithmetic, which was never in doubt, and it puts a number on "
      "the thing the Kd indicator is a proxy for. What it cannot settle is *why* the "
      "light is where it is. Kd is one broadband number and its causes do not "
      "separate — phytoplankton, resuspended mineral sediment, coloured dissolved "
      "organic matter and drifted detritus all darken water identically at this "
      "resolution. That is `Z8`, and it is why a Kd exceedance is attributed to "
      "algae by assumption rather than by measurement.\n")
    a("It also cannot see the shading that happens *after* the light has passed "
      "through the water. Epiphytes growing on the leaf shade the host at the blade "
      "surface, where no water-column measurement reaches (`Z9`), so the "
      "nutrient-to-light pathway can operate with every number on this page looking "
      "acceptable.\n")
    return "\n".join(o) + "\n"


def main():
    d = analyse()
    write_json(os.path.join(DERIVED, "light.json"), d)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(d))
    log(f"wrote docs/LIGHT.md ({os.path.getsize(OUT):,} chars)")
    log(f"  {d['n_growth_season']:,} growth-season casts, {d['n_stations']} stations, "
        f"{d['years'][0]}-{d['years'][1]}")
    log(f"  median depth reaching 11% of surface light: {d['z11']['median']} m")
    log(f"  trend all casts {d['trend']['all_casts_m_per_decade']} m/decade; "
        f"stable stations {d['trend']['stable_stations_m_per_decade']} m/decade")
    return 0


if __name__ == "__main__":
    sys.exit(main())
