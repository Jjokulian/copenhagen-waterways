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
     Bathing water is a long, dense, spatially replicated marine record - annual
     quality per station, most stations tagged with the marine water body they sit
     in. If the polygon is a real unit, two stations inside one should co-vary more
     than two stations either side of a boundary.

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
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (DERIVED, RAW, ROOT, log, plain_r, plain_r2, read_json,
                    write_doc, write_json)
import claims
import live

NAT = os.path.join(RAW, "national")
OUT = os.path.join(ROOT, "docs", "OBSERVING.md")
OBS_JSON = os.path.join(DERIVED, "observing.json")
MIN_STATION_YEARS = 15         # years of bathing record a station needs
MIN_BELOW_EXCELLENT = 3        # years below Excellent before a station is informative
MIN_PAIRS_PER_WB = 3           # station pairs a water body needs for its coherence
BOUNDARY_NEAR_KM = 15          # stations this close across a boundary are compared
BOUNDARY_MIN_PAIRS = 6         # cross-boundary pairs a water-body pair needs
ACCEPT_R2 = 0.4                # DCE's acceptance criterion, used by the noise floor
DCE = "DCE-STATMOD-2015"       # the statistical-model report, pinned in claims.d/water.json

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
# The noise floor of an acceptance criterion - shown on METHOD_LAB.md, not here.
#
# NOT DCE's procedure: DCE select stepwise on cross-validated error, offer each
# candidate over many period windows and check on held-out data. This runs a
# simpler, exhaustive in-sample search over small subsets of pure-noise
# candidates, under stipulated conditions - white noise, autocorrelation, and
# autocorrelation with a shared drift. The conditions are chosen, not measured
# from DCE's series (see C-ML-REPLICATION, C-ML-SERIES-DECLINE).
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
                    "share_passing": round(sum(1 for v in best if v >= ACCEPT_R2) / len(best), 3)})
    return {"candidates": N_CANDIDATES, "max_terms": MAX_TERMS, "acceptance_r2": ACCEPT_R2,
            "subsets_searched": sum(math.comb(N_CANDIDATES, k)
                                    for k in range(1, MAX_TERMS + 1)),
            "trials": N_TRIALS, "cases": out}


def dce_table3(cd):
    """Tabel 3 of the pinned DCE report, parsed: how many models it lists, and how
    many select each variable. The text extraction interleaves the table's columns,
    so in each half three counts are taken independently - variable groups, R2
    values and the ja/nej of the systematic-deviation column - and the parse is
    refused unless they agree."""
    t = claims._norm(claims.pin_text(cd, DCE))
    a = t.find("Tabel 3: Oversigt")
    b = t.find("De forklaringsvariable, som giver den bedste beskrivelse")
    if a < 0 or b < a:
        raise live.Unjustified(f"Tabel 3 not found in the pinned text of {DCE}")
    var = r"(?:N-load|P-load|temp|vind|salt|irr|BV|Q)"
    grp = re.compile(r"%s(?:,%s)*,?" % (var, var))
    models = []
    for part in t[a:b].split("Tabel 3 fortsat"):
        body = part[part.find("vurdering") + len("vurdering"):]
        groups, cur, r2, yn = [], None, 0, 0
        for tk in body.split():
            if grp.fullmatch(tk):
                # "N-load, vind" is one model's list: a trailing comma continues it
                if cur is not None and cur.endswith(","):
                    cur += " " + tk
                else:
                    if cur is not None:
                        groups.append(cur)
                    cur = tk
                continue
            if cur is not None:
                groups.append(cur)
                cur = None
            if re.fullmatch(r"\d+\.\d+", tk) and float(tk) <= 1:
                r2 += 1
            elif tk in ("ja", "nej"):
                yn += 1
        if cur is not None:
            groups.append(cur)
        if not (len(groups) == r2 == yn):
            raise live.Unjustified(f"Tabel 3 of {DCE} does not parse consistently: "
                                   f"{len(groups)} variable lists, {r2} R2 values, "
                                   f"{yn} ja/nej")
        models += [set(re.findall(var, g)) for g in groups]
    has = lambda v: sum(1 for m in models if v in m)
    return {"models": len(models), "with_bv": has("BV"), "with_vind": has("vind"),
            "with_nload": has("N-load"), "with_pload": has("P-load")}


def load():
    wb = {f["properties"]["ov_id"]: f["properties"]
          for f in read_json(os.path.join(NAT, "marin_overordnet.geojson"))["features"]}
    st = []
    for p in (f["properties"] for f in
              read_json(os.path.join(NAT, "badevand.geojson"))["features"]):
        s = {y: SCORE[p["quality_" + y]] for y in YEARS if p.get("quality_" + y) in SCORE}
        if p.get("wbid") in wb and len(s) >= MIN_STATION_YEARS:
            st.append({"wb": p["wbid"], "name": p["name"], "lat": p["latitude"],
                       "lon": p["longitude"], "s": s,
                       "informative": sum(1 for v in s.values() if v < 4) >= MIN_BELOW_EXCELLENT})
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
        if len(rs) >= MIN_PAIRS_PER_WB:
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


def boundaries(wb, st, intern, near_km=BOUNDARY_NEAR_KM, min_pairs=BOUNDARY_MIN_PAIRS):
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


def _plain_r(r, thing, other):
    """plain_r on live values: the same words, with every number carrying its chain."""
    r2 = r * r
    shrink = 1 - (1 - r2) ** 0.5
    return (f"{100 * r2:.1f}% of the wobble in {thing} is shared with {other}; "
            f"knowing {other} shrinks your error guessing {thing} by {100 * shrink:.0f}%")


def _plain_r2(r2):
    shrink = 1 - (1 - r2) ** 0.5
    return (f"accounts for {100 * r2:.0f}% of the wobble and shrinks prediction error "
            f"by {100 * shrink:.0f}% against just guessing the average")


def _nm(name):
    """A name is an identifier: one with digits in it ("Skagerrak, 12 sm") is code."""
    return f"`{name}`" if re.search(r"\d", str(name)) else name


def _case(c):
    """A noise-floor condition, described from its own parameters."""
    s = f"{c['n_points']} points, " + ("white noise" if not c["phi"] else f"autocorrelated ($\\varphi$ = {c['phi']})")
    return s + (f", plus a shared decline of {c['trend_sd']} SD" if c["trend_sd"] else "")


def render(d):
    """d is observing.json loaded live; the DCE report's figures are readings of its
    pinned text, so every number on the page has a chain. Every assertion is a
    claim in claims.d/w1-ob.json, marked here, and refused unless it is confirmed
    against these very words. The simulated noise floor is on METHOD_LAB.md."""
    cd, _, _ = claims.load()
    cache = {}
    R = lambda text: claims.resolve(cd, text, cache)[0]
    C, B, E = live.claim, live.claim_begin, live.CLAIM_END
    o = []
    a = o.append
    cv, sz, bd, p, t3 = d["coverage"], d["sizes"], d["boundary"], d["params"], d["dce_table3"]
    n29 = R(f"{{read:{DCE}:29|statistiske modeller for 29 kystnære overvågningsstationer}}")
    n22 = R(f"{{read:{DCE}:22|som repræsenterer 22 vandområder}}")
    n15y = R(f"{{read:{DCE}:15|lange tidsserier (> 15 år)}}")
    acc = R(f"{{read:{DCE}:0.4|tentativt sat til mindst 0,4}}")
    mean56 = R(f"{{read:{DCE}:0.56|har et gennemsnit på 0,56}}")
    o4 = R(f"{{read:{DCE}:4|iltkoncentration er under hhv. 4 mg/L}}")
    o2 = R(f"{{read:{DCE}:2|4 mg/L og 2 mg/L, i den måned, hvor antallet af dage med lave iltkoncentrationer er højest}}")
    y6 = R(f"{{read:{DCE}:6|Der bruges 6 års data til beregning af månedsfrekvenser}}")
    per6 = R(f"{{read:{DCE}:6|Der fremkommer én indikator værdi pr. 6. år}}")
    cut25 = R(f"{{read:{DCE}:25|fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration}}")
    min15 = R(f"{{read:{DCE}:15|minimumsgrænsen tentativt sat til 15 datapunkter}}")
    n_fall = R("{read:MSFD28:48|den samlede kvælstoftilførsel til marine kystafsnit med 48 %}")
    p_fall = R("{read:MSFD28:62|for hele Danmark 62 %}")
    kemi, ctd = R("{fig:kemi_rows}"), R("{fig:ctd_rows}")
    # Tabel 2's list is quoted, not counted: a reading states a number its phrase
    # prints, and this phrase prints none
    tabel2 = "vind, temp, salt, irr, BV, Q, N-load og P-load"
    if claims._norm("forkortelserne " + tabel2) not in claims._norm(claims.pin_text(cd, DCE)):
        raise live.Unjustified(f"the pinned text of {DCE} no longer lists '{tabel2}'")

    a("# What Denmark measures, and where\n")
    a(B("C-OB-UNIT") + "The nitrogen requirement is computed **per water body**. Status, "
      "environmental target and indsatsbehov are each one number attached to one polygon, "
      "and the chain assumes that polygon is uniform enough for one number to describe "
      "it." + E + " This page asks where the instruments actually are, what they sample, "
      "and whether the polygon behaves as one thing.\n")
    a(C("C-OB-SOURCES", "Sources: DCE/Aarhus Universitet's method report for the marine "
        f"indsatsbehov (2015), and the national VP3 layers - {sz['n']} marine water bodies "
        f"and {d['n_bathing_total']:,} bathing stations with annual quality 1991-2018, "
        f"{d['n_bathing_marine']:,} of them tagged with a marine water body.") + "\n")

    a("## 1. Sizes\n")
    a("These are all *one water body* each:\n")
    a("| km² | name | type |")
    a("|---:|---|---|")
    for r in list(sz["smallest"]) + [None] + list(sz["largest"]):
        if r is None:
            a("| | … | |")
            continue
        a(f"| {r[0]:,.1f} | {_nm(r[1])} | `{r[2]}` |")
    a("")
    a(C("C-OB-SIZES", f"The largest is {sz['largest'][-1][0] / sz['smallest'][0][0]:,.0f} times "
        f"the smallest. {sz['n']} polygons, {sz['total']:,.0f} km², {sz['n_types']} distinct "
        f"type codes, of which {sz['n_irrelevant']} are typed `Ej relevant`. Median "
        f"{sz['median']:.1f} km², mean {sz['mean']:.1f} km² - the mean is "
        f"{sz['mean'] / sz['median']:.1f} times the median because the {sz['n_irrelevant']} "
        f"open-sea polygons typed `Ej relevant` carry "
        f"{100 * sz['irrelevant_area'] / sz['total']:.0f}% of the area.") + "\n")

    a("## 2. Where the statistical models are\n")
    a(C("C-OB-DCE-SCOPE", f"DCE built statistical models for **{n29} coastal stations "
        f"representing {n22} water bodies**, on data from **1990-2012**, where series longer "
        f"than {n15y} years exist. The caption on their own validation table calls them "
        "*fjordmodellerne*.") + "\n")
    a(C("C-OB-COVERAGE", "Matching every station area named in that table against the "
        f"national polygon set by name gives **{cv['area']:,.0f} km² of {cv['total']:,.0f} km² "
        f"- {cv['pct']:.1f}% of Danish marine water-body area**. The match takes in "
        f"{cv['n_matched']} polygons where DCE count {n22} water bodies, so it may include "
        "polygons DCE did not model: the share is what the names give, not DCE's own "
        "figure.") + "\n")
    a(C("C-OB-UNMODELLED", "The largest water bodies the name match finds no statistical "
        "model for:") + "\n")
    a("| km² | name |")
    a("|---:|---|")
    for r in cv["unmodelled"]:
        a(f"| {r[0]:,.1f} | {_nm(r[1])} |")
    a("")
    a(C("C-OB-KOEGE-MODEL", f"Køge Bugt — `DKCOAST201`, {d['koege_area_km2']:,.0f} km², the "
        "water this project is about — has no statistical model. Its requirement comes "
        "from DHI's mechanistic model instead: DHI's table of computed requirements lists "
        "it under that model (`MEK`). DCE's meta-analysis, which transfers what is known "
        "from modelled water bodies to similar unmodelled ones, is for water bodies that "
        "neither kind of model covers.") + "\n")

    a("## 3. What the statistical layer is allowed to consider\n")
    a(C("C-OB-TABEL2", "The models in `Tabel 3` draw their explanatory variables from a "
        f"fixed list given in `Tabel 2` (*{tabel2}*): nutrient loads (N and P), freshwater "
        "flow, wind stress, irradiance, salinity, water-column stability, and **surface** "
        "water temperature. Bottom-water temperature is not on the list. Stratification "
        f"appears only as `vandsøjlestabilitet`, selected in {t3['with_bv']} of the "
        f"{t3['models']} models in `Tabel 3`.") + "\n")
    a(C("C-OB-NOT-ON-LIST", "That list is worth reading for what is not on it. An oxygen "
        "deficit is a balance — what removes oxygen against what resupplies it — and the "
        "routes on both sides are many. Imported organic matter exerts its demand directly, "
        "with no growth step in between. Ammonium exerts a demand by being oxidised. "
        "Sulphide from disturbed sediment consumes oxygen as it is oxidised. A kill of any "
        "cause leaves a decaying mass. None of those is a candidate variable; warming and "
        "stratification are, as surface temperature and water-column stability. What "
        "belongs to a missing driver shows up, if anywhere, in the coefficients of "
        "candidates that move with it, or in what the model leaves unexplained. The "
        "enumeration is in [OXYGEN.md](OXYGEN.md).") + "\n")
    a(C("C-OB-OXYGEN-TRIGGER", "The oxygen requirement itself comes from no regression at "
        "all. It is a **binary trigger** on an indicator that is the share of time oxygen "
        f"sits below {o4} mg/L and {o2} mg/L **in the single month where low-oxygen days "
        f"are most numerous**, computed from {y6} years of measurements, yielding **one "
        f"value per water body per {per6} years**. Oxygen is sampled far more often than "
        "that; this is about what survives the aggregation. Every month but one of every "
        "year is set aside before the number is formed, and the collapse over years "
        "removes what is left of the temporal signal, including any trend within the "
        "window.") + "\n")
    a(C("C-OB-SAMPLING", "DCE state that oxygen is measured at a frequency that does not "
        "necessarily catch short deficits: *\"målingerne af ilt foretages med en frekvens, "
        "som ikke nødvendigvis fanger kortvarige iltsvind\"*.") + " "
      + C("C-OB-FLAT-CUT", f"If the trigger fires, the requirement is a flat {cut25}% cut in "
          "total nitrogen concentration, chosen because it is *\"større end de normale "
          "år-til-år variationer\"* and because *\"det vurderes\"* to be the minimum that "
          "will move the system. A judged round number, not a fitted response.") + "\n")
    a("> **Scope of this section.** " + C("C-OB-SCOPE", "Everything above is read from the "
      "statistical modelling report (Timmermann et al. 2015), its `Tabel 2` and `Tabel 3`, "
      "except the line on Køge Bugt, which is read from DHI's table. The mechanistic "
      "modelling layer itself (DHI; Erichsen and co-authors) is among this project's pinned "
      "sources but is not examined here, so nothing here is a claim about what it does.")
      + "\n")

    a("## 4. The fitting window ends in 2012\n")
    a(C("C-OB-DECLINE", "The models are fitted on **1990-2012**. Over most of that window "
        "Danish nutrient inputs fell: DCE's marine strategy note puts the fall from 1990 to "
        f"2010 in total nitrogen input to the coastal waters at {n_fall}%, and in total "
        f"phosphorus input at {p_fall}%.") + " "
      + C("C-OB-COLLINEAR", "A regression on candidates that fall together cannot tell them "
          "apart: a stepwise selection gives their shared variance to whichever it picks "
          "first.") + "\n")
    a(C("C-OB-DCE-TNDRIFT", "DCE report that the TN models *\"har generelt en tendens til "
        "systematiske afvigelser over tid, idet de høje TN-koncentrationer observeret i "
        "starten af 1990’erne underestimeres\"*, and that the low concentrations late in "
        "the period are overestimated. The other indicators show it less, which DCE "
        "attribute to *\"tidsforsinkelsen pga. ophobning af organisk bundet kvælstof i "
        "sedimenterne\"* — the time lag from nitrogen accumulating in the sediments.") + " "
      + C("C-OB-MISSING-COVARIATE", "A predicted range compressed against a trending "
          "observed series is what a missing trending variable would produce, and the one "
          "DCE name is not among the candidates in `Tabel 2`.") + "\n")
    a(C("C-OB-AFTER2012", "Whatever changed after 2012 — in the sewers, on the coast or at "
        "sea — cannot be estimated from a series that stops in 2012: not because its effect "
        "is absent, but because the data end.") + "\n")
    a(C("C-OB-R2DEF", f"One of several acceptance criteria is **$R^2$ ≥ {acc}**, described in "
        "the report as *tentativt sat*. DCE define $R^2$ as one minus the sum of squared "
        "differences between model and observation over the sum of squared deviations of "
        "the observations from their mean.") + " "
      + C("C-OB-R2-NOTCORR", "That is not the square of a correlation: a model whose "
          "predictions are biased or compressed scores lower on it, and it can fall below "
          "zero.") + "\n")

    a("### What that criterion returns when there is nothing there\n")
    a(C("C-OB-DCE-DESIGN", "Each data point is *\"gennemsnit af målinger for en sæson "
        f"(år)\"* — one seasonal mean per year — with a stated minimum of {min15} points. "
        "`Tabel 3` shows the few variables selected per model, chosen as those *\"som giver "
        "den største forklaringskraft\"*: stepwise, by cross-validated regression on a "
        "calibration part of the data, with each candidate offered over many period "
        "windows, then evaluated on held-out data. [The method lab](METHOD_LAB.md) sets out "
        "the procedure as the report describes it.") + "\n")
    a(C("C-OB-QUESTION", f"So the question is not whether a mean $R^2$ of {mean56} is high. "
        "It is what a search like this returns **when there is no relation there at all** - "
        "and whether the reported $R^2$ was measured on data the search did not see.") + "\n")
    a("> What a simplified version of that search returns from pure noise is simulated, so "
      "it is shown on the method page: [the noise floor of an acceptance "
      "criterion](METHOD_LAB.md), computed by `noise_floor()` in `scripts/observing.py`.\n")
    a(C("C-OB-DCE-MEAN", f"DCE report a mean $R^2$ of **{mean56}** across all their "
        "models.") + "\n")
    a("> " + C("C-OB-R2-OPEN", "[The method lab](METHOD_LAB.md) simulates a simpler, "
      "exhaustive in-sample search on pure noise, which clears this criterion more often "
      "than not on autocorrelated series. Whether DCE's reported $R^2$ carries evidence "
      "depends on whether it was measured on their held-out data, which the report does "
      "not say.") + "\n")
    a(C("C-OB-NOT-FALSE", "None of this shows the relations are false.") + " "
      + C("C-OB-NTEST", "A test that would speak to the nitrogen term specifically is the "
          "$R^2$ of the N-load term alone against a model containing only the climate "
          "variables.") + "\n")

    a("## 5. Is a water body one thing? A test\n")
    a(C("C-OB-BATHING", "Bathing water is a long, dense, spatially replicated marine record: "
        f"{d['n_bathing_total']:,} stations, one quality class per year from 1991 to 2018, "
        f"{d['n_bathing_marine']:,} of them tagged with the marine water body they sit in. "
        "That is enough replication to ask the question directly.") + "\n")
    v = d["variance"]
    a(C("C-OB-VARIANCE", f"Take all {v['n_obs']:,} beach-year observations of the "
        f"{v['n_stations']} stations with at least {p['min_station_years']} years of "
        f"record, in {v['n_wb']} water bodies. Remove the national year-to-year swing "
        "first, so a warm wet summer everywhere does not count as structure. Split what is "
        "left three ways:") + "\n")
    a("| where the variation lives | share |")
    a("|---|---:|")
    a(f"| between water bodies | **{100 * v['share_between_wb']:.1f}%** |")
    a(f"| between beaches *inside* one water body | **{100 * v['share_between_st']:.1f}%** |")
    a(f"| year to year at a single beach | {100 * v['share_within']:.1f}% |")
    a("")
    a("*(" + C("C-OB-VARIANCE-PLAIN", "In plain words: if you had to guess how one beach did "
      "in one year, knowing which water body it is in gets you "
      f"{100 * v['share_between_wb']:.0f}% of the way. Knowing which beach — inside that "
      f"same water body — gets you {100 * v['share_between_st']:.0f}%, "
      f"{v['share_between_st'] / v['share_between_wb']:.1f} times as much. The unit that "
      "policy treats as uniform explains less than the differences within it.") + ")*\n")
    a(C("C-OB-NOISE", "The last row is large partly because a four-class grade is a coarse "
        "instrument. Grading noise enters that row in full, and the first two only through "
        "averages over each beach's years and each water body's beaches, where it is small; "
        "the comparison that carries the argument is the first two rows against each "
        "other.") + "\n")
    a("### The same thing said as correlations\n")
    a(C("C-OB-INTERNAL", f"Restricting to stations with at least {p['min_station_years']} "
        f"years of record and at least {p['min_below_excellent']} years below *Excellent* "
        "(so there is something to correlate), and to water bodies with at least "
        f"{p['min_pairs_per_wb']} pairs of such stations — **{d['internal']['n_wb']} water "
        "bodies**:") + "\n")
    mr = d["internal"]["mean_r"]
    a("> " + C("C-OB-MEANR", "Mean pairwise correlation between two stations **inside the "
      f"same water body**: **r = {mr:+.3f}**.") + "\n")
    a("*(" + C("C-OB-R-PLAIN", "In plain words: r is not a verdict, it is a co-wobble score "
      "— the average of how far one beach sits above its own usual, in units of its own "
      "usual wobble, times the same for the other beach. The divisor is the two "
      "**spreads**, not the two means, which is what keeps it between minus one and plus "
      "one and lets $r^2$ be read as a share. Here that means: "
      + _plain_r(mr, 'one beach', 'the other')) + ".)*\n")
    areas = sorted(w["area"] for w in d["internal"]["all"])
    worst = d["internal"]["worst"]
    if all(any(abs(w["area"] - x) < 1e-9 for w in worst) for x in areas[:2]):
        a(C("C-OB-SMALLEST", "The least internally coherent water bodies include the two "
            "smallest tested:") + "\n")
    else:
        a("The least internally coherent water bodies:\n")
    a("| km² | water body | stations | mean r |")
    a("|---:|---|---:|---:|")
    for r in worst:
        a(f"| {r['area']:,.1f} | {_nm(r['name'])} | {r['n_st']} | {r['r']:+.3f} |")
    a("")
    a("Matched on separation, against pairs that straddle a boundary:\n")
    a("| separation | same water body | different water bodies |")
    a("|---|---|---|")
    shown = []
    for r in d["by_distance"]:
        if r["same_n"] < 8 or r["diff_n"] < 8:
            continue
        shown.append(r)
        a(f"| {r['bin_km'][0]}–{r['bin_km'][1]} km | {r['same_r']:+.3f} "
          f"({r['same_n']:,}) | {r['diff_r']:+.3f} ({r['diff_n']:,}) |")
    a("")
    if shown:
        far = shown[-1]
        a(C("C-OB-DISTANCE", "The boundary carries some information at the shorter "
            f"separations and almost **none past {far['bin_km'][0]} km**, where two stations "
            f"in the same water body correlate at {far['same_r']:+.3f} and two in different "
            f"ones at {far['diff_r']:+.3f}. At that range, knowing that two points are in the "
            "same water body tells you little about whether they behave alike.") + "\n")

    a("## 6. Boundaries that separate things which behave alike\n")
    a(C("C-OB-BOUNDARIES", f"Of {bd['testable']} pairs of water bodies with at least "
        f"{p['boundary_min_pairs']} station pairs within {p['boundary_near_km']} km of each "
        f"other across the boundary, **{bd['n_failed']} "
        f"({100 * bd['n_failed'] / bd['testable']:.0f}%)** have stations that agree *across* "
        "the boundary more than either body's own stations agree among themselves. For "
        "those pairs the boundary carries negative information.") + "\n")
    a("| across | own A | own B | pairs | A │ B |")
    a("|---:|---:|---:|---:|---|")
    for r in bd["failed"]:
        a(f"| {r['cross_r']:+.3f} | {r['a_r']:+.3f} | {r['b_r']:+.3f} | {r['n_pairs']} "
          f"| {_nm(r['a'])} │ {_nm(r['b'])} |")
    a("")
    cut = {frozenset((str(r["a"]), str(r["b"]))) for r in bd["failed"]}
    if (frozenset(("Flensborg Fjord, indre", "Flensborg Fjord, ydre")) in cut
            and frozenset(("Vejle Fjord, indre", "Vejle Fjord, ydre")) in cut):
        a(C("C-OB-FJORDS", "Among them, Flensborg Fjord and Vejle Fjord are each one fjord "
            "divided into an inner and an outer water body, and in both the division fails "
            "this test. DCE have one model station in each of the two fjords (`KFF2` in "
            "Flensborg Fjord, `4273` in Vejle Fjord).") + "\n")

    if d.get("koege"):
        k = d["koege"]
        a("## 7. Køge Bugt, cut north and south\n")
        a(C("C-OB-KOEGE-SEARCH", f"Køge Bugt is one water body with {k['n']} informative "
            "bathing stations. Searching every north/south cut for the one that best "
            "separates them:") + "\n")
        a("> " + C("C-OB-KOEGE-CUT", f"The cut falls at **{k['lat']:.3f}°N**, at "
          f"*{_nm(k['at'])}*, with {k['n_north']} stations north of it and {k['n_south']} "
          f"south. Pairs on the same side correlate at **r = {k['within_r']:+.3f}** on "
          f"average; pairs across the cut at **r = {k['across_r']:+.3f}** - "
          f"{k['across_r'] / k['within_r']:.2f} of it.") + "\n")
        a(C("C-OB-KOEGE-CAVEAT", "Because the cut is the best of every one tried, its "
            "contrast is the largest these stations allow, and some contrast would appear "
            "even in a water that behaves as one; nothing here measures how much. The "
            "northern stations are " + "; ".join(_nm(x) for x in k["north"]) + ".") + "\n")

    a("## Two records side by side\n")
    a("| | stations | water bodies | years | data points entering the analysis |")
    a("|---|---:|---:|---|---:|")
    a(f"| Bathing water (faecal indicator) | {v['n_stations']} | {v['n_wb']} "
      f"| 1991–2018 | {v['n_obs']:,} station-years |")
    a(f"| Nutrient/chlorophyll/Kd models | {n29} | {n22} | 1990–2012 | at least {min15} "
      f"seasonal means per model, {t3['models']} models |")
    a(f"| Oxygen indicator | — | per water body | rolling {y6}-year | **one value per water "
      f"body per {per6} years** |")
    a("")
    a(C("C-OB-TWO-RECORDS", f"The bathing record's {v['n_obs']:,} station-years cover "
        f"{v['n_wb']} water bodies against the models' {n22}, and run to 2018 rather than "
        "2012.") + " "
      + C("C-OB-ARCHIVE-LARGER", "Neither is the whole of what Denmark measures in the sea: "
          f"the national monitoring archive this project holds - {kemi} water-chemistry "
          f"rows and {ctd} CTD rows - is larger than both. The comparison here is only "
          "about replication inside water bodies.") + "\n")

    a("## What this does and does not show\n")
    a(C("C-OB-CANNOT-ADJUDICATE", "The bathing analysis above **cannot adjudicate the "
        "nitrogen chain**. It grades bathing quality from faecal indicator bacteria, not "
        "chlorophyll, so the finding that a water body is internally incoherent is a finding "
        "about faecal contamination and is not proof that chlorophyll behaves the same way "
        "inside one.") + "\n")
    a(C("C-OB-SEWAGE", "The bathing record is also a direct measurement of something else: "
        f"faecal contamination reaching the shore, recorded at {v['n_stations']} stations in "
        f"{v['n_wb']} water bodies and through 2018 - more stations, and later years, than "
        "the nutrient models were fitted on.") + "\n")
    a(C("C-OB-CHL-UNTESTED", "Whether a water body is a coherent unit **for chlorophyll** "
        f"is not tested here. DCE fitted models only where series ran longer than {n15y} "
        f"years, and with {n29} stations across {n22} water bodies most of those water "
        "bodies have one such station — one station cannot disagree with itself.") + "\n")
    a(C("C-OB-PROPOSAL", "The constructive version is not \"scrap the water bodies\". It is "
        "that the partition is an empirical question with an empirical answer, and the data "
        "to answer it for chlorophyll would be a second long series in each water body that "
        "has one.") + "\n")
    return "\n".join(o) + "\n"


def main(argv=()):
    """Compute from the national layers, store, and render the page from what was
    stored. --render renders from the stored data/derived/observing.json alone."""
    if "--render" not in argv:
        wb, st = load()
        total, hit, harea = coverage(wb)
        hit_ids = {p["ov_id"] for p in hit}
        unmod = sorted((p for p in wb.values() if p["ov_id"] not in hit_ids),
                       key=lambda p: -p["ov_stoe"])[:12]
        sizes = sorted((p["ov_stoe"], p["ov_navn"], p["ov_typ"]) for p in wb.values())
        intern = internal(wb, st)
        testable, failed = boundaries(wb, st, intern)
        bathing = read_json(os.path.join(NAT, "badevand.geojson"))["features"]
        n_bathing = len(bathing)
        # not every station carries a marine water-body id: some none, some another kind
        n_marine = sum(1 for f in bathing if f["properties"].get("wbid") in wb)
        cd, _, _ = claims.load()
        d = {
            "coverage": {"total": total, "area": harea, "pct": 100 * harea / total,
                         "n_matched": len(hit),
                         "unmodelled": [(p["ov_stoe"], p["ov_navn"]) for p in unmod]},
            "sizes": {"n": len(wb), "total": total,
                      "median": sorted(s[0] for s in sizes)[len(sizes) // 2],
                      "mean": total / len(sizes),
                      "n_types": len({p["ov_typ"] for p in wb.values()}),
                      "n_irrelevant": sum(1 for p in wb.values() if p["ov_typ"] == "Ej relevant"),
                      "irrelevant_area": sum(p["ov_stoe"] for p in wb.values()
                                             if p["ov_typ"] == "Ej relevant"),
                      "smallest": sizes[:4], "largest": sizes[-4:]},
            "internal": {"n_wb": len(intern),
                         "mean_r": sum(v["r"] for v in intern.values()) / len(intern),
                         "worst": sorted(intern.values(), key=lambda v: v["r"])[:6],
                         "all": sorted(intern.values(), key=lambda v: v["area"])},
            "by_distance": by_distance(st),
            "boundary": {"testable": testable, "n_failed": len(failed), "failed": failed},
            "koege": split_koege(st),
            "koege_area_km2": wb["DKCOAST201"]["ov_stoe"] if "DKCOAST201" in wb else None,
            "n_bathing_total": n_bathing,
            "n_bathing_marine": n_marine,
            "dce_table3": dce_table3(cd),
            "variance": variance_components(st),
            "noise_floor": noise_floor(),
            "params": {"min_station_years": MIN_STATION_YEARS,
                       "min_below_excellent": MIN_BELOW_EXCELLENT,
                       "min_pairs_per_wb": MIN_PAIRS_PER_WB,
                       "boundary_near_km": BOUNDARY_NEAR_KM,
                       "boundary_min_pairs": BOUNDARY_MIN_PAIRS},
        }
        write_json(OBS_JSON, d)
    try:
        # the simulated noise floor is shown on METHOD_LAB.md, not here
        write_doc(OUT, render(live.live_json(OBS_JSON)))
    except (live.Unjustified, claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote docs/OBSERVING.md ({os.path.getsize(OUT):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
