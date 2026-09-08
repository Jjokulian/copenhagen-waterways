"""Exhaustive feature-subspace basketing, scored on the dimensions it did NOT use.

Two things were wrong with the earlier stability runs, and this fixes both.

1. THIN SAMPLING. They drew 12 disjoint pairs of feature subsets per size. At three
   features per half that is 12 of 840 pairs - 1.4% of the combinatorial space, and
   the number reported was an average over a sliver of it. Exhaustive enumeration is
   affordable here for a reason worth stating: the expensive object is the PARTITION
   PER SUBSET, and there are only C(9,k) of those, at most 126. Every disjoint pair
   is then a cheap ARI between two cached labellings. 255 clusterings buy all 1,569
   pairs.

2. THE WRONG QUESTION. Agreement between two derived baskets asks whether two
   subsets of features produce the same grouping. That is stability of the DERIVATION,
   and it is bounded above by how concentrated the space of derivable partitions is -
   if average linkage under a contiguity constraint at fixed granularity maps nearly
   any feature subset onto nearly the same partition, two derivations agree for
   procedural reasons and the data never enter. What was actually wanted is the
   held-out question: build baskets on k dimensions, then ask what they are worth on
   the dimensions that were not used.

   held_out_lift = rho*(partition, v) - rho*(contiguous null, v)   for every v not in
   the subset. This is a train/test split in feature space rather than in rows, and it
   cannot be satisfied by a procedure that ignores the data.

3. AND THE CONTROL THAT SETTLES (2). Permute each variable's values across stations
   WITHIN month. Month effects, marginal distributions, station counts, the neighbour
   graph, the granularity and the procedure are all preserved exactly; only the tie
   between a station and its values is cut. Rerun the same enumeration. Whatever
   agreement survives is the stability volume of the derivable space - the procedure
   agreeing with itself for no reason at all - and every real figure must be read
   against it, not against zero.

Reads   docs/data/areas/stations_series.{json,bin}, station_waterbody_overlay.json
Writes  docs/data/areas/partition_subspace.json

usage: partition_subspace.py [NGROUPS] [--permuted]
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
from partition_stability import (D, MIN_MONTHS, MIN_SHARED, MAX_STATIONS, load,
                                 deviations, distances, ari)
from partition_score import icc
from partition_contiguous import (KNN, build_graph, components,
                                  agglomerate_contiguous, contiguous_null)

NGROUPS = 84
PERMUTE = "--permuted" in sys.argv
for a in sys.argv[1:]:
    if a.isdigit():
        NGROUPS = int(a)



def pair_corr(stations, dev):
    """Pairwise correlation for ONE variable, flat upper triangle, NaN where the pair
    lacks enough shared months.

    This exists because the enumeration recomputes nothing. Building a subset's
    distance matrix by looping over its variables costs sum_k C(9,k)*k = 837 variable
    passes over 11,175 station pairs; the correlations themselves only depend on the
    variable, so 9 passes suffice and a subset is then an average of cached numbers.
    The first attempt took the 837-pass route and was heading for eighty minutes.
    """
    n = len(stations)
    out = array.array("f", [float("nan")]) * (n * (n - 1) // 2)
    k = 0
    for a in range(n):
        da = dev.get(stations[a], {})
        for b in range(a + 1, n):
            db = dev.get(stations[b], {})
            common = da.keys() & db.keys()
            if len(common) >= MIN_SHARED:
                xs = [da[m] for m in common]
                ys = [db[m] for m in common]
                mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
                sxx = sum((x - mx) ** 2 for x in xs)
                syy = sum((y - my) ** 2 for y in ys)
                if sxx > 0 and syy > 0:
                    out[k] = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
                              / (sxx * syy) ** 0.5)
            k += 1
    return out


def distances_cached(n, mats, subset):
    """Identical to partition_stability.distances(), assembled from cached
    correlations. A pair with no usable variable in the subset keeps the neutral 1.0.
    """
    dist = [[1.0] * n for _ in range(n)]
    cols = [mats[i] for i in subset]
    k = 0
    for a in range(n):
        ra = dist[a]
        for b in range(a + 1, n):
            tot = 0.0; cnt = 0
            for c in cols:
                v = c[k]
                if v == v:                      # NaN check without importing math
                    tot += v; cnt += 1
            if cnt:
                d = 1.0 - tot / cnt
                ra[b] = d; dist[b][a] = d
            k += 1
    return dist


def main():
    meta, ov, per = load()
    smeta = meta["stations"]
    wb = ov["waterbody_index"]
    keys = [v["key"] for v in meta["variables"]]
    V = len(keys)

    counts = collections.Counter()
    for k in keys:
        for s, d in per[k].items():
            if len(d) >= MIN_MONTHS:
                counts[s] += 1
    usable = sorted(s for s, c in counts.items()
                    if c == V and smeta[s].get("lat") is not None)[:MAX_STATIONS]
    n = len(usable)
    log(f"  {n} stations x {V} variables"
        + ("   [VALUES PERMUTED WITHIN MONTH - procedural control]" if PERMUTE else ""))

    if PERMUTE:
        rnd = random.Random(97)
        for k in keys:                    # cut station<->value, keep everything else
            bym = collections.defaultdict(list)
            for s in usable:
                for m, v in per[k].get(s, {}).items():
                    bym[m].append((s, v))
            for m, rows in bym.items():
                vals = [v for _, v in rows]
                rnd.shuffle(vals)
                for (s, _), nv in zip(rows, vals):
                    per[k][s][m] = nv

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
    log(f"  graph {sum(len(a) for a in adj)//2} edges, {ncomp} component(s); "
        f"{k_groups} groups; {len(nulls)} null partitions")

    # months-per-variable, for scoring a partition on a held-out dimension
    idx = {s: i for i, s in enumerate(usable)}
    months_of = {}
    for q in keys:
        bym = collections.defaultdict(list)
        for s in usable:
            for m, v in per[q].get(s, {}).items():
                bym[m].append((idx[s], v))
        months_of[q] = [r for r in bym.values() if len(r) >= 4]

    # one correlation pass per variable, then every subset is an average of cached
    # numbers. Verified against the original distances() before use.
    mats = [pair_corr(usable, devs[q]) for q in keys]
    chk = (0, 2)
    ref = distances(usable, [devs[keys[i]] for i in chk])
    got = distances_cached(n, mats, chk)
    worst = max(abs(ref[a][b] - got[a][b]) for a in range(n) for b in range(n))
    assert worst < 1e-6, f"cached distances disagree with the original by {worst}"
    log(f"  cached correlations verified against distances() (max diff {worst:.2e})")

    # every distinct subset, clustered once
    part = {}
    subsets = [c for k in (1, 2, 3, 4) for c in itertools.combinations(range(V), k)]
    for c, sub in enumerate(subsets):
        lab = agglomerate_contiguous(distances_cached(n, mats, sub), adj, k_groups)
        part[sub] = lab
        if (c + 1) % 50 == 0:
            log(f"    clustered {c+1}/{len(subsets)} subsets")

    def score(lab, q):
        r = icc(months_of[q], lambda s: lab[s])
        return r["icc"] if r else None
    null_score = {q: [x for x in (score(nl, q) for nl in nulls) if x is not None]
                  for q in keys}
    null_pair = [ari(nulls[a], nulls[b])
                 for a in range(len(nulls)) for b in range(a + 1, len(nulls))]
    ari0 = sum(null_pair) / len(null_pair)
    log(f"  contiguous null: ARI0 {ari0:+.3f}   "
        + "  ".join(f"{q}:{sum(v)/len(v):.2f}" for q, v in list(null_score.items())[:3])
        + " ...")

    out = []
    for k in (1, 2, 3, 4):
        subs = [s for s in subsets if len(s) == k]
        pairs = [(a, b) for a, b in itertools.combinations(subs, 2)
                 if not set(a) & set(b)]
        agree = [ari(part[a], part[b]) for a, b in pairs]
        vs_off = [ari(part[a], official) for a in subs]
        held = []
        for a in subs:
            for vi in range(V):
                if vi in a:
                    continue
                q = keys[vi]
                sc = score(part[a], q)
                if sc is None or not null_score[q]:
                    continue
                held.append(sc - sum(null_score[q]) / len(null_score[q]))
        m = lambda v: round(sum(v) / len(v), 3)
        out.append({
            "features_per_basket": k, "subsets": len(subs),
            "disjoint_pairs_all": len(pairs),
            "derived_vs_derived": m(agree),
            "derived_vs_derived_lift": round(m(agree) - ari0, 3),
            "spread": [round(min(agree), 3), round(max(agree), 3)],
            "derived_vs_official_lift": round(m(vs_off) - ari0, 3),
            "held_out_dims": V - k, "held_out_scores": len(held),
            "held_out_lift": m(held),
            "held_out_spread": [round(min(held), 3), round(max(held), 3)]})
        log(f"    k={k}: {len(subs):3d} subsets, ALL {len(pairs):4d} disjoint pairs"
            f"   d-v-d {m(agree):+.3f} (lift {m(agree)-ari0:+.3f})"
            f"   HELD-OUT lift {m(held):+.3f} over {len(held)} scores"
            f"  [{min(held):+.3f},{max(held):+.3f}]")

    tag = "_permuted" if PERMUTE else ""
    write_json(os.path.join(D, f"partition_subspace{tag}.json"), {
        "_what": "Every distinct feature subset of size 1-4 clustered once, then "
                 "compared against every disjoint subset (exhaustive, not sampled) "
                 "and scored on the dimensions it did not use.",
        "_why": "Agreement between two derived baskets is stability of the "
                "DERIVATION and is bounded by how concentrated the space of "
                "derivable partitions is - a procedure that ignores the data can "
                "score well on it. held_out_lift cannot be earned that way: it asks "
                "what baskets built on k dimensions are worth on the dimensions "
                "left out.",
        "_control": "Run with --permuted to shuffle each variable's values across "
                    "stations within month. Everything except the station-to-value "
                    "tie is preserved. Whatever agreement survives is the procedure "
                    "agreeing with itself, and is the floor for every figure here.",
        "_reading": "derived_vs_derived_lift is over ARI0, two random connected "
                    "partitions. held_out_lift is the mean-square ratio of the "
                    "derived partition minus that of the null partitions, on a "
                    "variable the partition never saw; 0 means the baskets carry "
                    "nothing about it beyond being connected blobs.",
        "permuted": PERMUTE, "stations": n, "groups": k_groups,
        "contiguous_null_ari": round(ari0, 3), "variables": keys, "results": out})
    log(f"\n  wrote partition_subspace{tag}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
