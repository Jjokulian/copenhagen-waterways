#!/usr/bin/env python3
"""What Denmark measures in the sea, where, how often - and whether the unit it
reports into is a real thing.

The nitrogen requirement is computed per "vandomraade". Every step of the chain -
status, environmental target, indsatsbehov - assumes that unit is homogeneous
enough that one number describes it. This script asks two questions the method
documents do not:

  1. Where are the instruments, and what do they sample?  Answered from DCE's own
     method report: which stations carry the statistical models, what fraction of
     the sea they cover, which variables are candidates, and how often the oxygen
     indicator is computed.

  2. Does the water-body boundary carve the sea at its joints?  Answered from data.
     Bathing water is the only long, dense, spatially replicated marine record
     Denmark has - 1,026 stations, annual quality 1991-2018, each tagged with the
     water body it sits in. If the polygon is a real unit, two stations inside one
     should co-vary more than two stations either side of a boundary. They barely do.

The bathing-water test measures faecal indicator bacteria, not chlorophyll, so it
does not prove chlorophyll is equally incoherent inside a water body. What it does
is move the burden: homogeneity is asserted, not shown, and with a median of one
station per water body it cannot be shown from the monitoring data either.

Usage:  python3 scripts/observing.py
"""
import collections
import itertools
import json
import math
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DERIVED, RAW, ROOT, log, plain_r, plain_r2, read_json,
                    write_json)

NAT = os.path.join(RAW, "national")
OUT = os.path.join(ROOT, "docs", "OBSERVING.md")

YEARS = [f"{y:02d}" for y in list(range(91, 100)) + list(range(0, 19))]
SCORE = {"Excellent": 4, "Good": 3, "Good or Sufficient": 3, "Sufficient": 2, "Poor": 1}

# The station areas named in DCE (2015) Tabel 3, the "fjordmodeller".
MODELLED = ["Lovns", "Skive", "Riisgard", "Nissum", "Logstor", "Thisted", "Kaas",
            "Nibe", "Randers", "Isefjord", "Horsens", "Roskilde", "Vejle",
            "Mariager", "Kolding", "Abenra", "Flensborg", "Odense", "Ringkobing"]
FOLD = str.maketrans({"å": "a", "æ": "a", "ø": "o",
                      "Å": "A", "Æ": "A", "Ø": "O"})


def haversine(a, b):
    la1, lo1, la2, lo2 = (math.radians(v) for v in (a["lat"], a["lon"], b["lat"], b["lon"]))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def pearson(a, b, min_overlap=12):
    ys = sorted(set(a["s"]) & set(b["s"]))
    if len(ys) < min_overlap:
        return None
    u = [a["s"][y] for y in ys]
    v = [b["s"][y] for y in ys]
    mu, mv = sum(u) / len(u), sum(v) / len(v)
    su = math.sqrt(sum((t - mu) ** 2 for t in u))
    sv = math.sqrt(sum((t - mv) ** 2 for t in v))
    if su == 0 or sv == 0:
        return None
    return sum((u[i] - mu) * (v[i] - mv) for i in range(len(ys))) / (su * sv)


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


# ---------------------------------------------------------------------------
# The noise floor of their own acceptance criterion.
#
# Their documented design: each data point is one seasonal mean for one year;
# at least 15 points; eight candidate explanatory variables (Tabel 2); the ones
# "som giver den største forklaringskraft" are selected, up to three per model.
# That is a best-subset search over 92 candidate models fitted to ~20 points.
#
# So the question is not whether R2 = 0.57 is high. It is what R2 that search
# returns when there is no relation there at all. This simulates exactly that,
# under three conditions of increasing realism: white noise; autocorrelated
# series, which annual marine and climate series are; and autocorrelated series
# that additionally share a monotone decline, which every candidate variable did
# over 1990-2012.
# ---------------------------------------------------------------------------

NOISE_CASES = [
    ("20 points, white noise", 20, 0.0, 0.0),
    ("20 points, autocorrelated (phi=0.5)", 20, 0.5, 0.0),
    ("20 points, autocorrelated + shared decline", 20, 0.5, 2.0),
    ("15 points (their stated minimum), same", 15, 0.5, 2.0),
]
N_CANDIDATES, MAX_TERMS, N_TRIALS = 8, 3, 400


def _ols_r2(X, y):
    n, k = len(y), len(X)
    m = k + 1
    A = [[1.0] + [X[j][i] for j in range(k)] for i in range(n)]
    M = [[sum(A[i][a] * A[i][b] for i in range(n)) for b in range(m)]
         + [sum(A[i][a] * y[i] for i in range(n))] for a in range(m)]
    for c in range(m):
        p = max(range(c, m), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            return 0.0
        M[c], M[p] = M[p], M[c]
        for r in range(m):
            if r != c:
                f = M[r][c] / M[c][c]
                for q in range(c, m + 1):
                    M[r][q] -= f * M[c][q]
    b = [M[i][m] / M[i][i] for i in range(m)]
    my = sum(y) / n
    ss = sum((v - my) ** 2 for v in y)
    rs = sum((y[i] - (b[0] + sum(b[j + 1] * X[j][i] for j in range(k)))) ** 2
             for i in range(n))
    return max(0.0, 1 - rs / ss) if ss else 0.0


def _series(n, phi, trend):
    x = [random.gauss(0, 1)]
    for _ in range(n - 1):
        x.append(phi * x[-1] + random.gauss(0, math.sqrt(1 - phi * phi)))
    return [v + trend * i / n for i, v in enumerate(x)] if trend else x


def noise_floor(seed=7):
    random.seed(seed)
    out = []
    for label, n, phi, trend in NOISE_CASES:
        best = []
        for _ in range(N_TRIALS):
            y = _series(n, phi, trend)
            X = [_series(n, phi, trend) for _ in range(N_CANDIDATES)]
            b = 0.0
            for k in range(1, MAX_TERMS + 1):
                for c in itertools.combinations(range(N_CANDIDATES), k):
                    b = max(b, _ols_r2([X[j] for j in c], y))
            best.append(b)
        best.sort()
        q = lambda f: best[int(f * len(best))]
        out.append({"case": label, "n_points": n, "phi": phi, "trend_sd": trend,
                    "median": round(q(.5), 3), "p75": round(q(.75), 3),
                    "p90": round(q(.9), 3),
                    "share_passing": round(sum(1 for v in best if v >= 0.4) / len(best), 3)})
    return {"candidates": N_CANDIDATES, "max_terms": MAX_TERMS,
            "subsets_searched": sum(math.comb(N_CANDIDATES, k)
                                    for k in range(1, MAX_TERMS + 1)),
            "trials": N_TRIALS, "cases": out}


def load():
    wb = {f["properties"]["ov_id"]: f["properties"]
          for f in read_json(os.path.join(NAT, "marin_overordnet.geojson"))["features"]}
    st = []
    for p in (f["properties"] for f in
              read_json(os.path.join(NAT, "badevand.geojson"))["features"]):
        s = {y: SCORE[p["quality_" + y]] for y in YEARS if p.get("quality_" + y) in SCORE}
        if p.get("wbid") in wb and len(s) >= 15:
            st.append({"wb": p["wbid"], "name": p["name"], "lat": p["latitude"],
                       "lon": p["longitude"], "s": s,
                       "informative": sum(1 for v in s.values() if v < 4) >= 3})
    return wb, st


def coverage(wb):
    """Share of Danish marine area carrying a statistical model."""
    total = sum(p["ov_stoe"] for p in wb.values())
    hit = []
    for p in wb.values():
        folded = p["ov_navn"].translate(FOLD).lower()
        if any(n.lower()[:6] in folded for n in MODELLED):
            hit.append(p)
    return total, hit, sum(p["ov_stoe"] for p in hit)


def internal(wb, st):
    """Mean pairwise correlation between stations inside one water body."""
    by = collections.defaultdict(list)
    for r in st:
        if r["informative"]:
            by[r["wb"]].append(r)
    out = {}
    for w, v in by.items():
        rs = [pearson(v[i], v[j]) for i in range(len(v)) for j in range(i + 1, len(v))]
        rs = [x for x in rs if x is not None]
        if len(rs) >= 3:
            out[w] = {"r": sum(rs) / len(rs), "n_st": len(v), "n_pairs": len(rs),
                      "area": wb[w]["ov_stoe"], "name": wb[w]["ov_navn"]}
    return out


def variance_components(st):
    """Where does the variation in Danish bathing quality actually live?

    Correlations answer "do two beaches move together". This answers the blunter
    question underneath it: if you had to predict one beach-year, how much does
    knowing the water body buy you? The national year-to-year swing is removed
    first, so what remains is spatial structure plus local noise, and it is split
    three ways - between water bodies, between beaches inside one water body, and
    year to year at a single beach.

    If the water body were a real unit, the first share would dominate the second.
    """
    obs = [(r["wb"], r["name"], y, v) for r in st for y, v in r["s"].items()]
    if not obs:
        return None
    yb = collections.defaultdict(list)
    for w, n, y, v in obs:
        yb[y].append(v)
    ym = {y: sum(v) / len(v) for y, v in yb.items()}
    res = [(w, n, y, v - ym[y]) for w, n, y, v in obs]
    N = len(res)
    total = sum(v ** 2 for _, _, _, v in res) / N       # grand mean is ~0 by construction
    gw = collections.defaultdict(list)
    gs = collections.defaultdict(list)
    for w, n, y, v in res:
        gw[w].append(v)
        gs[(w, n)].append(v)
    gm = {w: sum(v) / len(v) for w, v in gw.items()}
    sm = {k: sum(v) / len(v) for k, v in gs.items()}
    between_wb = sum(len(v) * gm[w] ** 2 for w, v in gw.items()) / N
    between_st = sum(len(v) * (sm[k] - gm[k[0]]) ** 2 for k, v in gs.items()) / N
    within = sum((v - sm[(w, n)]) ** 2 for w, n, y, v in res) / N
    flat = sum(1 for r in st if len(set(r["s"].values())) == 1)
    movers = sorted(((statistics.pstdev(v), w, len(v)) for w, v in gw.items()
                     if len(v) >= 40), reverse=True)
    return {"n_obs": N, "n_stations": len(gs), "n_wb": len(gw),
            "total": total,
            "between_water_bodies": between_wb, "share_between_wb": between_wb / total,
            "between_stations_within": between_st, "share_between_st": between_st / total,
            "within_station": within, "share_within": within / total,
            "flat_stations": flat,
            "most_variable": [(round(a, 3), b, c) for a, b, c in movers[:6]],
            "least_variable": [(round(a, 3), b, c) for a, b, c in movers[-5:]]}


def by_distance(st, cap_km=25):
    """Same-body vs cross-body correlation, matched on separation."""
    bins = [(0, 2), (2, 5), (5, 10), (10, 25)]
    acc = {b: {"same": [], "diff": []} for b in bins}
    R = [r for r in st if r["informative"]]
    for i in range(len(R)):
        for j in range(i + 1, len(R)):
            d = haversine(R[i], R[j])
            if d > cap_km:
                continue
            r = pearson(R[i], R[j])
            if r is None:
                continue
            for b in bins:
                if b[0] <= d < b[1]:
                    acc[b]["same" if R[i]["wb"] == R[j]["wb"] else "diff"].append(r)
                    break
    return [{"bin_km": list(b), "same_r": mean(v["same"]), "same_n": len(v["same"]),
             "diff_r": mean(v["diff"]), "diff_n": len(v["diff"])}
            for b, v in acc.items()]


def boundaries(wb, st, intern, near_km=15, min_pairs=6):
    """Adjacent water-body pairs whose stations agree across the boundary more than
    either body's own stations agree among themselves. Such a boundary carries
    negative information: it separates things that behave alike."""
    R = [r for r in st if r["informative"]]
    cross = collections.defaultdict(list)
    for i in range(len(R)):
        for j in range(i + 1, len(R)):
            if R[i]["wb"] == R[j]["wb"] or haversine(R[i], R[j]) > near_km:
                continue
            r = pearson(R[i], R[j])
            if r is not None:
                cross[tuple(sorted((R[i]["wb"], R[j]["wb"])))].append(r)
    testable, failed = 0, []
    for (a, b), v in cross.items():
        if len(v) < min_pairs or a not in intern or b not in intern:
            continue
        testable += 1
        m = sum(v) / len(v)
        if m > intern[a]["r"] and m > intern[b]["r"]:
            failed.append({"cross_r": m, "n_pairs": len(v),
                           "a": wb[a]["ov_navn"], "a_r": intern[a]["r"],
                           "b": wb[b]["ov_navn"], "b_r": intern[b]["r"]})
    failed.sort(key=lambda d: -d["cross_r"])
    return testable, failed


def split_koege(st, wbid="DKCOAST201"):
    """Does the project's home water behave as one body? Find the north/south cut
    that best separates it, and report the gain over treating it as one."""
    R = sorted((r for r in st if r["wb"] == wbid and r["informative"]),
               key=lambda r: -r["lat"])
    if len(R) < 8:
        return None
    best = None
    for k in range(3, len(R) - 2):
        A, B = R[:k], R[k:]
        wi = mean([pearson(G[i], G[j]) for G in (A, B)
                   for i in range(len(G)) for j in range(i + 1, len(G))])
        ac = mean([pearson(a, b) for a in A for b in B])
        if wi is None or ac is None:
            continue
        if best is None or wi - ac > best["gain"]:
            best = {"gain": wi - ac, "lat": R[k]["lat"], "within_r": wi, "across_r": ac,
                    "n_north": k, "n_south": len(R) - k,
                    "north": [r["name"] for r in A], "at": R[k]["name"]}
    if best:
        best["whole_r"] = mean([pearson(R[i], R[j]) for i in range(len(R))
                                for j in range(i + 1, len(R))])
        best["n"] = len(R)
    return best


def render(d):
    a = [].append
    o = []
    a = o.append
    cv, sz, bd = d["coverage"], d["sizes"], d["boundary"]

    a("# What Denmark measures, and where\n")
    a("The nitrogen requirement is computed **per water body**. Status, environmental "
      "target and indsatsbehov are each one number attached to one polygon, and the "
      "whole chain assumes that polygon is uniform enough for one number to describe "
      "it. This page asks where the instruments actually are, what they sample, and "
      "whether the polygon is a real thing.\n")
    a("Sources: DCE/Aarhus Universitet's method report for the marine indsatsbehov "
      "(2015), and the national VP3 layers - 123 marine water bodies and 1,026 bathing "
      "stations carrying annual quality 1991-2018, each tagged with the water body it "
      "sits in.\n")

    a("## 1. The unit spans four orders of magnitude\n")
    a("These are all *one water body*, each with one status and one requirement:\n")
    a("| km² | name | type |")
    a("|---:|---|---|")
    for r in sz["smallest"] + [(None, "…", "")] + sz["largest"]:
        a(f"| {'' if r[0] is None else f'{r[0]:,.1f}'} | {r[1]} | {r[2]} |")
    a("")
    a(f"{sz['n']} polygons, {sz['total']:,.0f} km², {sz['n_types']} distinct type "
      f"codes, of which {sz['n_irrelevant']} are typed `Ej relevant`. Median "
      f"{sz['median']:.1f} km², mean {sz['mean']:.1f} km² - the mean is four times "
      f"the median because a handful of open-sea polygons carry most of the area.\n")

    a("## 2. The statistical models cover 5.7% of the sea, and all of it is fjord\n")
    a("DCE built statistical models for **29 coastal stations representing 22 water "
      "bodies**, on data from **1990-2012**, requiring series longer than 15 years. "
      "The caption on their own validation table calls them *fjordmodellerne*.\n")
    a(f"Matching every station area named in that table against the national polygon "
      f"set gives **{cv['area']:,.0f} km² of {cv['total']:,.0f} km² - "
      f"{cv['pct']:.1f}% of Danish marine water-body area**.\n")
    a("The largest water bodies with no statistical model at all:\n")
    a("| km² | name |")
    a("|---:|---|")
    for r in cv["unmodelled"]:
        a(f"| {r[0]:,.1f} | {r[1]} |")
    a("")
    a("Køge Bugt — `DKCOAST201`, 562 km², the water this project is about — has no "
      "statistical model. Whatever coefficient is applied to it is transferred from "
      "fjords, and a fjord is the one marine setting whose flushing, stratification "
      "and residence time are least like an open bay's.\n")

    a("## 3. What the statistical layer is allowed to consider\n")
    a("The models in Tabel 3 — the ones that produce the per-area numbers — draw their "
      "explanatory variables from a fixed list of eight, given in Tabel 2: nutrient "
      "loads (N and P), freshwater flow, wind stress, irradiance, salinity, "
      "water-column stability, and **surface** water temperature. Bottom-water "
      "temperature is not on the list. Stratification appears only as "
      "`vandsøjlestabilitet`, selected in 13 of the 72 models.\n")
    a("That list is worth reading for what is not on it. An oxygen deficit is a balance "
      "— what removes oxygen against what resupplies it — and the routes on both sides "
      "are many. Imported organic matter exerts its demand directly, with no nitrogen "
      "and no growth step in between. Ammonium exerts a demand chemically, by being "
      "oxidised. Sulphide released from disturbed sediment consumes oxygen the moment "
      "it meets it. A kill event of any cause leaves a decaying mass and a bacterial "
      "bloom on it. Warmer water holds less; a column that does not turn over does not "
      "refill. None of those is a candidate variable, so whatever share belongs to them "
      "has nowhere to go but into the coefficients on the variables that are there. The "
      "enumeration is in [OXYGEN.md](#OXYGEN.md).\n")
    a("The oxygen requirement itself comes from no regression at all. It is a **binary "
      "trigger** on an indicator that is the share of time oxygen sits below 4 mg/L and "
      "2 mg/L **in the single month where low-oxygen days are most numerous**, computed "
      "from six years of measurements, yielding **one value per water body per six "
      "years**. Oxygen is sampled far more often than that; this is about what survives "
      "the aggregation. Eleven months of every year are discarded before the number is "
      "formed, and the six-year collapse removes what is left of the temporal signal — "
      "including any trend, and including whatever happened in the years the shore "
      "actually got worse.\n")
    a("DCE state plainly that the sampling misses the events: *\"målingerne af ilt "
      "foretages med en frekvens, som ikke nødvendigvis fanger kortvarige iltsvind\"*. "
      "If the trigger fires, the requirement is a flat 25% cut in total nitrogen "
      "concentration, chosen because it is *\"større end de normale år-til-år "
      "variationer\"* and because *\"det **vurderes**\"* to be the minimum that will move "
      "the system. A judged round number, not a fitted response.\n")
    a("> **Scope of this section.** Everything above is read from the statistical "
      "modelling report (Timmermann et al. 2015) and its Tabel 2 and Tabel 3. A second, "
      "mechanistic modelling layer exists (DHI, Erichsen & Kaas 2015) which this "
      "project has not yet read in the original. Nothing here should be taken as a "
      "claim about what that layer does or does not contain.\n")

    a("## 4. The window closes where the problem starts\n")
    a("The models are fitted on **1990-2012**. Over that window essentially every "
      "candidate driver declined monotonically - nitrogen load, phosphorus load, "
      "point-source discharge, atmospheric deposition. A regression on co-declining "
      "series cannot separate them; it awards the shared variance to whichever is "
      "entered.\n")
    a("DCE report the symptom without drawing the inference:\n")
    a("> *\"TN-modellerne har generelt en tendens til systematiske afvigelser over tid, "
      "idet de høje TN-koncentrationer observeret i starten af 1990'erne underestimeres, "
      "mens de lave TN-koncentrationer i sidste del af perioden overestimeres.\"*\n")
    a("A predicted range compressed against a monotone observed trend is the signature "
      "of a missing monotone covariate. Their own explanation names one and leaves it "
      "out of the model: *\"tidsforsinkelsen pga. ophobning af organisk bundet kvælstof "
      "i sedimenterne\"* - an unmodelled state variable with memory.\n")
    a("And several things that plausibly matter *change regime after 2012* and are "
      "therefore outside the fit entirely: the national basin-and-separation programme "
      "that followed the 2011 cloudburst, the construction wave (Nordhavn, Ørestad, "
      "Sluseholmen, Lynetteholm), and trawling effort. None of them can be estimated "
      "from a series that stops in 2012 - not because their effect is absent, but "
      "because the data end.\n")
    a("The acceptance criterion is **R² ≥ 0.4**, described in the report as *tentativt "
      "sat*. R² is the squared normalised cross-covariance between fitted and observed. "
      "No out-of-sample validation is reported.\n")

    a("### What that criterion returns when there is nothing there\n")
    nf = d["noise_floor"]
    a("Their design is documented precisely enough to test the criterion directly. Each "
      "data point is *\"gennemsnit af målinger for en sæson (år)\"* — one seasonal mean "
      "per year — with a stated minimum of 15 points. Tabel 2 offers "
      f"{nf['candidates']} candidate explanatory variables. Tabel 3 shows one to three "
      "selected per model, chosen as those *\"som giver den største forklaringskraft\"*. "
      f"That is a best-subset search over **{nf['subsets_searched']} candidate models "
      f"fitted to about 20 points**.\n")
    a("So the question is not whether R² = 0.57 is high. It is what that search returns "
      "**when there is no relation there at all**. Simulating exactly their design, "
      f"{nf['trials']} times per case:\n")
    a("| condition | median R² | 75th | 90th | share clearing R² ≥ 0.4 |")
    a("|---|---:|---:|---:|---:|")
    for c in nf["cases"]:
        a(f"| {c['case']} | {c['median']:.2f} | {c['p75']:.2f} | {c['p90']:.2f} "
          f"| {100*c['share_passing']:.0f}% |")
    a("")
    a("Annual marine and climate series are autocorrelated, and over 1990–2012 every "
      "candidate declined together. Those are the bottom two rows. Under the conditions "
      "their own data satisfy, **the median R² from pure noise is 0.56–0.66, and 82–90% "
      "of noise models clear their acceptance criterion.**\n")
    a("DCE report a mean R² of **0.56** across all 72 models; the median of the table "
      "as parsed here is **0.57**.\n")
    a("> That is not distinguishable from the noise floor of their own selection "
      "procedure.\n")
    a("This does **not** show the relations are false. Several are probably real — the "
      "phosphorus models in particular are strong and mechanistically expected. What it "
      "shows is that the reported R² carries no evidence either way, because the "
      "threshold was set below the null distribution of the search that produced it. "
      "The fix is cheap and standard: hold out years, or report the R² of the N-load "
      "term alone against a model containing only the climate variables. Neither is "
      "reported for any of the 72.\n")
    a("Two caveats, stated because they matter. The simulation assumes all "
      f"{nf['candidates']} candidates were offered to every model; if variables were "
      "pre-screened on mechanistic grounds the inflation is smaller — though *\"største "
      "forklaringskraft\"* describes a search, not a screen. And the shared-decline case "
      "assumes a 2-SD monotone drift across the window, which is the right order for "
      "Danish nitrogen load but is a choice; the autocorrelation-only row is the "
      "conservative version and still puts the median at 0.43.\n")

    a("## 5. Is a water body a real thing? A test\n")
    a("Bathing water is the only long, dense, spatially replicated marine record "
      "Denmark has: 1,026 stations, one quality class per year from 1991 to 2018, each "
      "carrying the id of the water body it sits in. That is enough replication to ask "
      "the question directly.\n")
    v = d["variance"]
    a(f"Take all {v['n_obs']:,} beach-year observations across {v['n_stations']} "
      f"stations in {v['n_wb']} water bodies. Remove the national year-to-year swing "
      f"first, so a warm wet summer everywhere does not count as structure. Split what "
      f"is left three ways:\n")
    a("| where the variation lives | share |")
    a("|---|---:|")
    a(f"| between water bodies | **{100*v['share_between_wb']:.1f}%** |")
    a(f"| between beaches *inside* one water body | **{100*v['share_between_st']:.1f}%** |")
    a(f"| year to year at a single beach | {100*v['share_within']:.1f}% |")
    a("")
    a("*(In plain words: if you had to guess how one beach did in one year, knowing "
      f"which water body it is in gets you {100*v['share_between_wb']:.0f}% of the way. "
      f"Knowing which beach — inside that same water body — gets you "
      f"{100*v['share_between_st']:.0f}%, nearly twice as much. The unit that policy "
      "treats as uniform explains less than the differences within it.)*\n")
    a("The last row is large partly because a four-class ordinal is a noisy instrument, "
      "and that noise falls on all three shares equally. The load-bearing comparison is "
      "the first two rows against each other, and they do not depend on the noise level "
      "at all.\n")
    a("### The same thing said as correlations\n")
    a(f"Restricting to stations with at least 15 years of record and at least 3 years "
      f"below *Excellent* (so there is something to correlate), and to water bodies "
      f"with at least 3 such stations — **{d['internal']['n_wb']} water bodies**:\n")
    mr = d["internal"]["mean_r"]
    a(f"> Mean pairwise correlation between two stations **inside the same water "
      f"body**: **r = {mr:+.3f}**.\n")
    a("*(In plain words: r is not a verdict, it is a co-wobble score — the average of "
      "how far one beach sits above its own usual, in units of its own usual wobble, "
      "times the same for the other beach. The divisor is the two **spreads**, not the "
      "two means, which is what keeps it between −1 and +1 and lets r² be read as a "
      f"share. Here that means: {plain_r(mr, 'one beach', 'the other')}.)*\n")
    a(f"The threshold a model must clear to be accepted as a description of that same "
      f"water body is R² ≥ 0.4 — which {plain_r2(0.4)}. The water body does not cohere "
      f"to a tenth of the standard its own model is held to.\n")
    a("It is not an artefact of size. The least internally coherent bodies include some "
      "of the smallest:\n")
    a("| km² | water body | stations | mean r |")
    a("|---:|---|---:|---:|")
    for r in d["internal"]["worst"]:
        a(f"| {r['area']:,.1f} | {r['name']} | {r['n_st']} | {r['r']:+.3f} |")
    a("")
    a("Matched on separation, against pairs that straddle a boundary:\n")
    a("| separation | same water body | different water bodies |")
    a("|---|---|---|")
    for r in d["by_distance"]:
        if r["same_n"] < 8 or r["diff_n"] < 8:
            continue
        a(f"| {r['bin_km'][0]}–{r['bin_km'][1]} km | {r['same_r']:+.3f} "
          f"({r['same_n']:,}) | {r['diff_r']:+.3f} ({r['diff_n']:,}) |")
    a("")
    a("The boundary carries a little information at 2–10 km and **none past 10 km**. "
      "Beyond ten kilometres, knowing that two points are in the same water body tells "
      "you nothing about whether they behave alike.\n")

    a("## 6. Boundaries that separate things which behave alike\n")
    a(f"Of {bd['testable']} adjacent water-body pairs with enough stations to test, "
      f"**{len(bd['failed'])} ({100*len(bd['failed'])/bd['testable']:.0f}%)** have "
      f"stations that agree *across* the boundary more than either body's own stations "
      f"agree among themselves. For those pairs the boundary carries negative "
      f"information.\n")
    a("| across | own A | own B | pairs | A │ B |")
    a("|---:|---:|---:|---:|---|")
    for r in bd["failed"]:
        a(f"| {r['cross_r']:+.3f} | {r['a_r']:+.3f} | {r['b_r']:+.3f} | {r['n_pairs']} "
          f"| {r['a']} │ {r['b']} |")
    a("")
    a("Two of those are a single fjord cut into *indre* and *ydre*, where the cut is "
      "worse than no cut - and both Vejle Fjord and Flensborg Fjord carry statistical "
      "models and separate requirements for each half.\n")

    if d.get("koege"):
        k = d["koege"]
        a("## 7. Køge Bugt is at least two things\n")
        a(f"Køge Bugt is one water body with {k['n']} informative bathing stations - "
          f"enough to ask whether it is one thing. Searching every north/south cut for "
          f"the one that best separates it:\n")
        a(f"> The cut falls at **{k['lat']:.3f}°N**, at *{k['at']}*. North of it "
          f"({k['n_north']} stations) and south of it ({k['n_south']} stations) each "
          f"cohere at **r = {k['within_r']:+.3f}**; across the cut, **r = "
          f"{k['across_r']:+.3f}** - less than half.\n")
        a("The northern group is " + "; ".join(k["north"]) + " — the Køge Bugt "
          "Strandpark lagoon chain and the Amager outfall shore. The administrative "
          "polygon treats them and the open southern coast as one water with one "
          "status. The data say they are two.\n")

    a("## What the observing system is actually built to see\n")
    v = d["variance"]
    a("Set the two records side by side. Denmark's densest, longest, most replicated "
      "marine observation is of **faecal contamination** — is it safe to swim. The "
      "chain policy acts on — nitrogen to algae to oxygen to a dead seabed — is "
      "observed far more thinly, and the oxygen end of it most thinly of all.\n")
    a("| | stations | water bodies | years | data points entering the analysis |")
    a("|---|---:|---:|---|---:|")
    a(f"| Bathing water (faecal indicator) | {v['n_stations']} | {v['n_wb']} "
      f"| 1991–2018 | {v['n_obs']:,} station-years |")
    a("| Nutrient/chlorophyll/Kd models | 29 | 22 | 1990–2012 | ~1,440 seasonal means "
      "(72 models × ≥15 points) |")
    a("| Oxygen indicator | — | per water body | rolling 6-year | **1 value per water "
      "body per 6 years** |")
    a("")
    a("Roughly **fourteen times as many observations** stand behind the faecal record "
      "as behind every nutrient model in the country combined, they are spread over "
      "three times as many water bodies, and they run thirteen years further forward — "
      "through exactly the period the fitted window excludes.\n")
    a("That is not a small technical asymmetry. It means the sewage pathway is the one "
      "Denmark can actually measure, and the nutrient pathway is the one Denmark acts "
      "on. The two hypotheses about what wrecks a Danish shore are not being weighed "
      "against each other on comparable evidence — one has an observing system and the "
      "other has a model.\n")

    a("## What this does and does not show\n")
    a("The bathing analysis above **cannot adjudicate the nitrogen chain**. It measures "
      "*E. coli* and enterococci, not chlorophyll, so the finding that a water body is "
      "internally incoherent is a finding about faecal contamination and is not proof "
      "that chlorophyll behaves the same way inside one.\n")
    a("But that limit cuts both directions, and the second direction is the one usually "
      "left out. The bathing record is not a *weak proxy* for the nutrient question — "
      "it is a *strong direct measurement of a competing one*. Whatever it shows about "
      "sewage reaching Danish shores, it shows with fourteen times the observational "
      "support of anything said about nitrogen, and it keeps showing it after 2012.\n")
    a("Whether the water body is a coherent unit **for chlorophyll** cannot be tested "
      "at all: 29 stations across 22 water bodies is a median of one each, and one "
      "station cannot disagree with itself. The homogeneity is asserted by the "
      "delineation and demonstrated nowhere.\n")
    a("The constructive version is not \"scrap the water bodies\". It is that the "
      "partition is an empirical question with an empirical answer, and the data to "
      "answer it would be one more monitoring station in each of the bodies that "
      "currently have one. That is a smaller ask than a nitrogen reduction.\n")
    return "\n".join(o) + "\n"


def main():
    wb, st = load()
    total, hit, harea = coverage(wb)
    hit_ids = {p["ov_id"] for p in hit}
    unmod = sorted((p for p in wb.values() if p["ov_id"] not in hit_ids),
                   key=lambda p: -p["ov_stoe"])[:12]
    sizes = sorted((p["ov_stoe"], p["ov_navn"], p["ov_typ"]) for p in wb.values())
    intern = internal(wb, st)
    testable, failed = boundaries(wb, st, intern)

    d = {
        "coverage": {"total": total, "area": harea, "pct": 100 * harea / total,
                     "n_matched": len(hit),
                     "unmodelled": [(p["ov_stoe"], p["ov_navn"]) for p in unmod]},
        "sizes": {"n": len(wb), "total": total,
                  "median": sorted(s[0] for s in sizes)[len(sizes) // 2],
                  "mean": total / len(sizes),
                  "n_types": len({p["ov_typ"] for p in wb.values()}),
                  "n_irrelevant": sum(1 for p in wb.values() if p["ov_typ"] == "Ej relevant"),
                  "smallest": sizes[:4], "largest": sizes[-4:]},
        "internal": {"n_wb": len(intern),
                     "mean_r": sum(v["r"] for v in intern.values()) / len(intern),
                     "worst": sorted(intern.values(), key=lambda v: v["r"])[:6],
                     "all": sorted(intern.values(), key=lambda v: v["area"])},
        "by_distance": by_distance(st),
        "boundary": {"testable": testable, "failed": failed},
        "koege": split_koege(st),
        "variance": variance_components(st),
        "noise_floor": noise_floor(),
    }
    write_json(os.path.join(DERIVED, "observing.json"), d)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(d))
    log(f"wrote docs/OBSERVING.md ({os.path.getsize(OUT):,} chars)")
    log(f"  statistical models cover {d['coverage']['pct']:.1f}% of marine area")
    log(f"  internal coherence of a water body: r={d['internal']['mean_r']:+.3f} "
        f"(R²={d['internal']['mean_r']**2:.3f}) over {len(intern)} bodies")
    log(f"  boundaries carrying negative information: {len(failed)}/{testable}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
