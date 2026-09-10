#!/usr/bin/env python3
"""Re-score the nine hypotheses that were blocked on the vandkemi fetch.

TRIAGE.md named ODA vandkemi (Emne_10_11) as the blocker for A1, A2, A5, A7, B4,
E2, E11, K1 and K2. The fetch has happened - 1,805,827 rows, 1,126 stations, 147
parameters, 1970-2026 - so the classification "blocked on a fetch" is stale for
all nine and has to be replaced by what the data actually supports.

The first thing this does is not a test. It is an availability matrix: for each
hypothesis, which of the variables its consequence needs are now in hand, with n,
station count and year span for each. That matters more than it sounds, because
a blocker can hide a second blocker. A hypothesis listed as "blocked on the
vandkemi fetch" may have needed river load or species counts as well, and while
the first lock was closed nobody had to notice the second. Unlocking one door
does not tell you how many doors there are.

Only then the tests, and only the ones whose null is computable under the
constraint actually imposed - which is the standard PLAN.md sets and which this
project has got wrong four times.

    python3 scripts/rescore.py             # availability matrix, then tests
    python3 scripts/rescore.py --matrix    # matrix only

Writes data/derived/rescore.json.
"""
import collections
import csv
import gzip
import io
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, log

SRC = os.path.join(RAW, "oda", "kemi.csv.gz")
TEMPS = os.path.join(DERIVED, "surface_temp.csv.gz")
OUT = os.path.join(DERIVED, "rescore.json")

# The exact parameter strings, verified against the enum sweep rather than
# guessed - and with the unit each must carry, because 14 of 147 parameters in
# this file appear under more than one.
P = {
    "chl":  ("Klorofyl a", "µg/l"),
    "o2":   ("Oxygen indhold", "mg/l"),
    "tn":   ("Nitrogen,total N", "µg/l"),
    "tp":   ("Phosphor, total-P", "µg/l"),
    "dip":  ("Ortho-phosphat-P", "µg/l"),
    "nox":  ("Nitrit+nitrat-N", "µg/l"),
    "nh4":  ("Ammoniak+ammonium-N", "µg/l"),
    "si":   ("Silicium", "µg/l"),
    "ph":   ("pH", "pH"),
    "sal":  ("Salinitet", "psu"),
    "ss":   ("Suspenderede stoffer", "mg/l"),
}

# What each hypothesis needs, split into what this fetch could supply and what
# it never could. The second column is the point of the exercise.
NEEDS = {
    "A1": (["chl", "o2"], ["river load (Vandloeb STOFTRANSPORT - a different "
                           "ODA endpoint; run() hardcodes Hav)"]),
    "A2": (["tp", "dip", "chl"], ["river P flux (STOFTRANSPORT)"]),
    "A5": (["tn", "dip", "si"], []),
    "A7": (["dip", "o2"], ["river input for the 'without a matching input' "
                           "clause (STOFTRANSPORT)"]),
    "B4": (["ss"], ["stream stations - this extract is the Hav topic, so "
                    "riverine POC is not in it at all",
                    "sediment organic content at the receiving coast"]),
    "E2": (["nh4", "o2"], []),
    "E11": (["nh4", "ph"], ["temperature and salinity at the same bottle "
                            "(joined from CTD by station-day, not same-hour)"]),
    "K1": (["si", "nox", "nh4"], ["phytoplankton counts - OBIS eMoF, not held"]),
    "K2": (["tn", "tp", "si"], ["species assemblage - not held"]),
}

# molar masses for the ratios; the archive is in ug/l of the element
MM = {"n": 14.007, "p": 30.974, "si": 28.086}


def num(s):
    try:
        return float((s or "").replace(",", "."))
    except (ValueError, AttributeError):
        return None


def main(argv):
    want = {v[0]: (k, v[1]) for k, v in P.items()}
    have = {k: {"n": 0, "stations": set(), "y0": None, "y1": None}
            for k in P}
    # per station-date-depth cell, for the ratio and coupling tests
    cells = collections.defaultdict(dict)
    dropped_unit = 0

    log(f"reading {os.path.relpath(SRC)}")
    with gzip.open(SRC, "rb") as fh:
        for row in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"),
                                  delimiter=";"):
            spec = want.get(row.get("Parameter"))
            if not spec:
                continue
            key, unit = spec
            if (row.get("Enhed") or "").strip() != unit:
                dropped_unit += 1
                continue
            if (row.get("ResultatAttribut") or "").strip() in ("<", ">"):
                continue
            if row.get("Prøvetype") not in ("Enkeltprøve", "Blandingsprøve"):
                continue
            v = num(row.get("Resultat"))
            d = (row.get("Startdato") or "").strip()
            dep = num(row.get("GennemsnitsDybde_m"))
            st = row.get("ObservationsStedNr")
            if v is None or len(d) != 8 or dep is None or dep == 99:
                continue
            h = have[key]
            h["n"] += 1
            h["stations"].add(st)
            y = d[:4]
            h["y0"] = y if h["y0"] is None or y < h["y0"] else h["y0"]
            h["y1"] = y if h["y1"] is None or y > h["y1"] else h["y1"]
            cells[(st, d, round(dep, 1))][key] = v

    log(f"  {len(cells):,} station-date-depth cells, "
        f"{dropped_unit:,} rows dropped on unit")

    matrix = {}
    for hyp, (needs, still) in NEEDS.items():
        rows = {}
        for k in needs:
            h = have[k]
            rows[k] = {"parameter": P[k][0], "n": h["n"],
                       "stations": len(h["stations"]),
                       "years": f"{h['y0']}-{h['y1']}" if h["y0"] else None}
        got = all(have[k]["n"] > 0 for k in needs)
        matrix[hyp] = {
            "fetch_supplied": rows,
            "all_fetch_variables_present": got,
            "still_missing": still,
            "class": ("testable now" if got and not still else
                      "partly unblocked - a second blocker was behind the first"
                      if got else "still blocked"),
        }

    log("\n" + "=" * 74)
    log("AVAILABILITY after the fetch")
    log("=" * 74)
    for hyp in NEEDS:
        m = matrix[hyp]
        log(f"\n{hyp}: {m['class'].upper()}")
        for k, r in m["fetch_supplied"].items():
            log(f"    {r['parameter'][:34]:<34} {r['n']:>8,} rows  "
                f"{r['stations']:>5} stations  {r['years']}")
        for s in m["still_missing"]:
            log(f"    STILL MISSING: {s}")

    out = {"_what": "Re-scoring of the nine hypotheses TRIAGE.md listed as "
                    "blocked on the ODA vandkemi fetch, now that it has run.",
           "_caution": "A blocker can hide a blocker. Several of these needed "
                       "something the vandkemi fetch never could supply, and "
                       "while the first lock was shut nobody had to notice.",
           "cells": len(cells), "matrix": matrix,
           "counts": {k: {"n": v["n"], "stations": len(v["stations"]),
                          "years": f"{v['y0']}-{v['y1']}" if v["y0"] else None}
                      for k, v in have.items()}}

    tally = collections.Counter(m["class"] for m in matrix.values())
    log("\n" + "=" * 74)
    for c, n in tally.most_common():
        log(f"  {n} of 9: {c}")
    out["tally"] = dict(tally)

    if "--matrix" not in argv:
        out["tests"] = run_tests(cells)

    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"\nwrote {os.path.relpath(OUT)}")
    return 0


def run_tests(cells):
    """The tests whose null is computable from this extract alone."""
    res = {}

    # K1/K2, first half: the Si:DIN molar ratio through time. Diatoms are
    # silicon-limited below about 1:1, so the level matters and not only the
    # trend. The assemblage half stays blocked - this is the driver, not the
    # response, and saying otherwise would be the error this project keeps
    # finding in other people's work.
    by_year = collections.defaultdict(list)
    for (st, d, dep), c in cells.items():
        if dep > 10:
            continue
        si, nox, nh4 = c.get("si"), c.get("nox"), c.get("nh4")
        if si is None or nox is None:
            continue
        din = nox + (nh4 or 0.0)
        if din <= 0 or si <= 0:
            continue
        by_year[d[:4]].append((si / MM["si"]) / (din / MM["n"]))
    ratio = {}
    for y in sorted(by_year):
        v = sorted(by_year[y])
        if len(v) < 100:
            continue
        ratio[y] = {"n": len(v), "median": round(v[len(v) // 2], 3),
                    "share_below_1": round(sum(1 for x in v if x < 1) / len(v), 3)}
    res["K1_si_din_molar_surface"] = ratio
    log("\nK1/K2 driver: surface Si:DIN molar ratio by year "
        "(diatoms are Si-limited below 1)")
    ys = sorted(ratio)
    for y in ys[:3] + ["..."] + ys[-3:] if len(ys) > 6 else ys:
        if y == "...":
            log("    ...")
            continue
        r = ratio[y]
        log(f"    {y}  median {r['median']:>7.2f}   "
            f"below 1: {100*r['share_below_1']:>4.0f}%   n={r['n']:,}")

    # A7 weak form: does bottom-water DIP rise through the summer? The strong
    # form needs river input to rule out, and that is a different endpoint.
    deep = collections.defaultdict(list)
    for (st, d, dep), c in cells.items():
        if dep < 15 or c.get("dip") is None:
            continue
        deep[int(d[4:6])].append(c["dip"])
    dip = {}
    for m in sorted(deep):
        v = sorted(deep[m])
        if len(v) < 50:
            continue
        dip[m] = {"n": len(v), "median": round(v[len(v) // 2], 1)}
    res["A7_bottom_dip_by_month"] = dip
    log("\nA7 weak form: median ortho-P below 15 m, by month (ug/l)")
    for m in sorted(dip):
        log(f"    {m:>2}  {dip[m]['median']:>7.1f}   n={dip[m]['n']:,}")

    # E11: the un-ionised ammonia fraction, which is what is toxic. Needs pH
    # and ammonium in the SAME bottle - the join is the test of whether the
    # archive can support the hypothesis at all.
    both = [(c["ph"], c["nh4"]) for c in cells.values()
            if c.get("ph") is not None and c.get("nh4") is not None]
    log(f"\nE11: bottles carrying BOTH pH and ammonium: {len(both):,}")
    if both:
        # Emerson 1975 pKa at 15 C, freshwater form - indicative only, the
        # salinity correction is not applied and is not negligible in a fjord
        pka = 9.56
        frac = sorted(1.0 / (1.0 + 10 ** (pka - ph)) * nh4 for ph, nh4 in both)
        n = len(frac)
        res["E11_unionised_nh3_ug_l"] = {
            "n_bottles_with_both": n, "median": round(frac[n // 2], 3),
            "p95": round(frac[95 * n // 100], 3), "max": round(frac[-1], 2),
            "caveat": "pKa at 15 C, no salinity or in-situ temperature "
                      "correction; indicative of magnitude only."}
        log(f"    un-ionised NH3, median {frac[n//2]:.3f} ug/l, "
            f"p95 {frac[95*n//100]:.3f}, max {frac[-1]:.1f}")
    else:
        res["E11_unionised_nh3_ug_l"] = {"n_bottles_with_both": 0}
    return res


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
