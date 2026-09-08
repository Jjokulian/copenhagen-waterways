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
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, read_json, write_json

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

    a("## 3. The instruments are at the surface, and oxygen is sampled once per six years\n")
    a("The candidate explanatory variables are nutrient loads, freshwater flow, wind "
      "stress, irradiance, salinity, water-column stability and **surface** water "
      "temperature. Bottom-water temperature is not a candidate anywhere. Stratification "
      "enters only as `vandsøjlestabilitet`, and is selected in 13 of the 72 published "
      "models.\n")
    a("Iltsvind is a bottom-water phenomenon, and so is the terminus of the fedtemøg "
      "cycle. Neither has a bottom-water driver in the model.\n")
    a("> The oxygen indicator itself, from DCE's Tabel 4: the share of time oxygen is "
      "below 4 mg/L and 2 mg/L **in the single month where low-oxygen days are most "
      "numerous**; six years of data go into the monthly frequencies; **one indicator "
      "value emerges per six years**.\n")
    a("DCE also state plainly that the sampling misses the events: *\"målingerne af ilt "
      "foretages med en frekvens, som ikke nødvendigvis fanger kortvarige iltsvind\"*. "
      "That single number per six years is not fitted to anything. It is a **binary "
      "trigger**: if it fires, the requirement is a flat 25% cut in total nitrogen "
      "concentration, chosen because it is *\"større end de normale år-til-år "
      "variationer\"* and because *\"det **vurderes**\"* to be the minimum that will move "
      "the system.\n")

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
      "Two monotone declining series clear |r| ≥ 0.63 without any causal connection "
      "between them. No out-of-sample validation is reported, and the explanatory "
      "variables were selected per station as the best-performing subset, which "
      "inflates R² further.\n")

    a("## 5. Is a water body a real thing? A test\n")
    a("Bathing water is the only long, dense, spatially replicated marine record "
      "Denmark has: 1,026 stations, one quality class per year from 1991 to 2018, each "
      "carrying the id of the water body it sits in. If the polygon is a real unit, its "
      "own stations should co-vary.\n")
    a(f"Restricting to stations with at least 15 years of record and at least 3 years "
      f"below *Excellent* (so there is something to correlate), and to water bodies "
      f"with at least 3 such stations - **{d['internal']['n_wb']} water bodies**:\n")
    a(f"> Mean pairwise correlation between two stations **inside the same water "
      f"body**: **r = {d['internal']['mean_r']:+.3f}**, i.e. **R² = "
      f"{d['internal']['mean_r']**2:.3f}**.\n")
    a("Two stations in one legally-uniform water body share about four percent of their "
      "year-to-year variance. The model acceptance threshold for describing that same "
      "water body is ten times higher.\n")
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

    a("## What this does and does not show\n")
    a("Bathing quality is a faecal indicator measure. Its variance is driven by local "
      "rain and outfalls, so **low spatial coherence here is not proof that chlorophyll "
      "is equally incoherent inside a water body.** That test cannot be run: the marine "
      "monitoring programme puts 29 stations across 22 modelled water bodies — a median "
      "of one each — so there is no replication to run it on.\n")
    a("What it does show is that the water body is not, in general, a unit within which "
      "measurable marine state is homogeneous - and that the one variable Denmark does "
      "measure at enough points to check the assumption does not support it. "
      "Homogeneity is asserted by the delineation, not demonstrated by it. The burden "
      "belongs on the side making the assertion, and it is discharged nowhere in the "
      "method documents.\n")
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
