"""Does a basket built on k dimensions agree with the basket built on all the rest?

The earlier run compared a k-subset against a DISJOINT EQUAL-SIZED subset, and
averaged. Two things are wrong with that.

  The comparison. An arbitrary other k-subset may itself produce a garbage basketing,
  so agreeing with it establishes nothing. The complement is the strongest alternative
  available: every dimension not used to build the basket, pooled. ARI(P_F, P_~F) asks
  whether what F says about these stations is what everything else says.

  The averaging. Reporting a mean over all pairs lets bad baskets vote. If random
  k-combinations mostly do not produce good baskets, the mean measures what bad
  baskets have in common - a popularity contest among them - and it will look like
  agreement. The question "are random 2-combinations good basket creation?" is
  answered by the DISTRIBUTION of complement agreement, not by its centre, so the
  distribution is what is reported: quartiles, extremes, how many subsets clear the
  permuted floor, and which dimensions the good ones contain.

AND IT IS THE PART THAT SCALES. Each test costs exactly two clusterings - the subset
and its complement - so the cost is linear in the number of draws and INDEPENDENT of
how large the combinatorial space is. Nine variables happen to admit exhaustive
enumeration (2^9 - 2 = 510 subsets); fifty do not, and never will. Anything that
weighs subsets against each other needs the whole space to mean anything and is
therefore 2^V; the complement comparison needs one well-defined alternative per draw
and is therefore O(draws). Sampling loses nothing here: with --draws the same
distribution is estimated from a sample, and the distribution is the answer.

Reads   docs/data/areas/stations_series.{json,bin}, station_waterbody_overlay.json
Writes  docs/data/areas/partition_complement[_permuted].json

usage: partition_complement.py [NGROUPS] [--permuted]
"""
import array
import collections
import itertools
import math
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json
from partition_stability import D, MIN_MONTHS, MAX_STATIONS, load, deviations, ari
from partition_contiguous import (KNN, build_graph, components,
                                  agglomerate_contiguous, contiguous_null)
from partition_subspace import pair_corr, distances_cached

NGROUPS = 84
VARS = None                    # restrict to named variables, e.g. the true sensors
DRAWS = 0                      # 0 = exhaustive where affordable
PERMUTE = "--permuted" in sys.argv
_av = sys.argv[1:]
for i, a in enumerate(_av):
    if a == "--draws" and i + 1 < len(_av):
        DRAWS = int(_av[i + 1])
    elif a == "--vars" and i + 1 < len(_av):
        VARS = _av[i + 1].split(",")
    elif a.isdigit() and (i == 0 or _av[i - 1] != "--draws"):
        NGROUPS = int(a)


def quantiles(v):
    v = sorted(v)
    q = lambda p: v[min(len(v) - 1, int(p * len(v)))]
    return {"min": round(v[0], 3), "q25": round(q(.25), 3), "median": round(q(.5), 3),
            "q75": round(q(.75), 3), "max": round(v[-1], 3),
            "mean": round(sum(v) / len(v), 3)}


def main():
    meta, ov, per = load()
    smeta = meta["stations"]
    wb = ov["waterbody_index"]
    keys = [v["key"] for v in meta["variables"]]
    if VARS:
        # Derived channels are not extra evidence. Salinity is computed from
        # conductivity and temperature, oxygen saturation from oxygen, temperature
        # and salinity - so a "disjoint half" containing oxysat and one containing
        # oxy+temp+sal share information by construction. Restricting to the true
        # sensors asks whether the structure was inferred or handed over.
        missing = [v for v in VARS if v not in keys]
        if missing:
            raise SystemExit(f"unknown variables: {missing}; have {keys}")
        keys = [k for k in keys if k in VARS]
    V = len(keys)

    counts = collections.Counter()
    for q in keys:
        for s, d in per[q].items():
            if len(d) >= MIN_MONTHS:
                counts[s] += 1
    usable = sorted(s for s, c in counts.items()
                    if c == V and smeta[s].get("lat") is not None)[:MAX_STATIONS]
    n = len(usable)
    log(f"  {n} stations x {V} variables"
        + ("   [PERMUTED]" if PERMUTE else ""))

    if PERMUTE:
        rnd = random.Random(97)
        for q in keys:
            bym = collections.defaultdict(list)
            for s in usable:
                for m, v in per[q].get(s, {}).items():
                    bym[m].append((s, v))
            for m, rows in bym.items():
                vals = [v for _, v in rows]
                rnd.shuffle(vals)
                for (s, _), nv in zip(rows, vals):
                    per[q][s][m] = nv

    devs = {q: deviations(per[q], usable) for q in keys}
    pts = [smeta[s] for s in usable]
    adj, _ = build_graph(pts, KNN)
    ncomp = len(components(adj))
    k_groups = max(ncomp, min(NGROUPS, int(n * 0.8)))
    official = [wb[s] for s in usable]
    sizes = sorted(collections.Counter(x for x in official
                                       if x is not None and x >= 0).values(),
                   reverse=True) or [2] * k_groups
    nulls = [contiguous_null(adj, sizes, s) for s in (11, 22, 33, 44, 55, 66)]
    ari0 = sum(ari(nulls[a], nulls[b]) for a in range(len(nulls))
               for b in range(a + 1, len(nulls))) / (len(nulls) * (len(nulls) - 1) / 2)
    log(f"  {k_groups} groups, {ncomp} component(s), contiguous null ARI {ari0:+.3f}")

    mats = [pair_corr(usable, devs[q]) for q in keys]

    # Only the subsets actually tested get clustered, plus their complements: two
    # clusterings per draw, whatever the size of the space. Exhaustive enumeration is
    # a convenience at V=9, not a requirement of the method.
    rnd = random.Random(5)
    tested = {}
    for k in range(1, V // 2 + 1):
        total = math.comb(V, k)
        if DRAWS and DRAWS < total:
            seen = set()
            while len(seen) < DRAWS:
                seen.add(tuple(sorted(rnd.sample(range(V), k))))
            tested[k] = sorted(seen)
        else:
            tested[k] = list(itertools.combinations(range(V), k))
    need = sorted({f for subs in tested.values() for f in subs}
                  | {tuple(i for i in range(V) if i not in f)
                     for subs in tested.values() for f in subs})
    log(f"  {sum(len(v) for v in tested.values())} subsets tested"
        f" -> {len(need)} clusterings"
        + (f" (sampled {DRAWS}/size)" if DRAWS else " (exhaustive)"))
    part = {}
    for i, sub in enumerate(need):
        part[sub] = agglomerate_contiguous(distances_cached(n, mats, sub),
                                           adj, k_groups)
        if (i + 1) % 100 == 0:
            log(f"    clustered {i+1}/{len(need)}")

    # PER PAIR, NOT PER PARTITION. ARI is itself an aggregate over all 11,175 station
    # pairs, so reporting a distribution of ARIs still rests on a mean - it was just
    # moved one level down. The question "do they agree about who they bundle
    # together" is a fact about a PAIR, and collapsing it loses exactly what is worth
    # knowing: which stations are always bundled, which never are, and which sit on a
    # boundary that the choice of features decides.
    npair = n * (n - 1) // 2
    agree_n = array.array("I", bytes(4 * npair))
    tog_n = array.array("I", bytes(4 * npair))
    trials = 0
    for k in range(1, V // 2 + 1):
        for f in tested[k]:
            comp = tuple(i for i in range(V) if i not in f)
            pf, pc = part[f], part[comp]
            trials += 1
            i = 0
            for a in range(n):
                fa, ca = pf[a], pc[a]
                for b in range(a + 1, n):
                    tf = pf[b] == fa
                    if tf == (pc[b] == ca):
                        agree_n[i] += 1
                    if tf:
                        tog_n[i] += 1
                    i += 1
    hist = [0] * 10
    for v in agree_n:
        hist[min(9, int(v * 10 // trials))] += 1
    tog_hist = [0] * 10
    for v in tog_n:
        tog_hist[min(9, int(v * 10 // trials))] += 1
    log(f"\n  PER-PAIR over {npair} station pairs and {trials} subset/complement "
        f"trials - no mean taken:")
    log("    subset and complement AGREE about the pair, by decile of trials:")
    log("      " + "  ".join(f"{d*10}-{d*10+10}%:{hist[d]}" for d in range(10)))
    log("    pair BUNDLED TOGETHER by the subset, by decile of trials:")
    log("      " + "  ".join(f"{d*10}-{d*10+10}%:{tog_hist[d]}" for d in range(10)))

    out = []
    for k in range(1, V // 2 + 1):
        subs = tested[k]
        rows = []
        for f in subs:
            comp = tuple(i for i in range(V) if i not in f)
            rows.append((ari(part[f], part[comp]), f))
        vals = [r[0] for r in rows]
        rows.sort(reverse=True)
        name = lambda f: "+".join(keys[i] for i in f)
        out.append({
            "features_in_basket": k, "subsets": len(subs),
            "of_possible": math.comb(V, k),
            "complement_size": V - k,
            "complement_agreement": quantiles(vals),
            "best": [{"features": name(f), "ari": round(a, 3)} for a, f in rows[:3]],
            "worst": [{"features": name(f), "ari": round(a, 3)} for a, f in rows[-3:]],
            "vs_official": quantiles([ari(part[f], official) for f in subs])})
        qs = out[-1]["complement_agreement"]
        log(f"    k={k} vs complement({V-k}): median {qs['median']:+.3f}  "
            f"[{qs['min']:+.3f} .. {qs['max']:+.3f}]  q25 {qs['q25']:+.3f} "
            f"q75 {qs['q75']:+.3f}   best: {name(rows[0][1])}")

    tag = ("_permuted" if PERMUTE else "") + (f"_{len(keys)}v" if VARS else "")
    write_json(os.path.join(D, f"partition_complement{tag}.json"), {
        "_what": "Each feature subset's basketing compared against the basketing "
                 "built from every dimension it left out.",
        "_why": "An arbitrary other subset may itself produce a garbage basketing, so "
                "agreeing with it establishes nothing; the complement is the "
                "strongest alternative available. And a MEAN over pairs lets bad "
                "baskets vote - if random k-combinations mostly do not produce good "
                "baskets, the mean measures what bad baskets have in common. The "
                "distribution answers whether random k-combinations are good basket "
                "creation at all.",
        "_reading": "Read the spread, not the centre. A high median with a tight "
                    "spread means most k-combinations find the same structure. A low "
                    "median with a long right tail means most are junk and a few "
                    "specific dimensions carry everything - in which case the "
                    "identity of those dimensions is the finding, and any average "
                    "over subsets is a popularity contest.",
        "_per_pair": "ARI is an aggregate over all station pairs, so a distribution "
                     "of ARIs still rests on a mean one level down. per_pair holds "
                     "the undigested version: for each of the station pairs, how "
                     "many of the subset/complement trials agreed about it, and how "
                     "many bundled it together. A bimodal agreement histogram means "
                     "the kind-classification is decided for most pairs and "
                     "contested for a few; a flat one means the features decide the "
                     "answer.",
        "per_pair": {"pairs": npair, "trials": trials,
                     "agreement_by_decile": hist,
                     "bundled_together_by_decile": tog_hist},
        "permuted": PERMUTE, "stations": n, "groups": k_groups,
        "contiguous_null_ari": round(ari0, 3), "variables": keys, "results": out})
    log(f"\n  wrote partition_complement{tag}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
