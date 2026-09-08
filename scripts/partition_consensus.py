"""Popularity weighting, but only among baskets that earned a vote.

partition_complement.py established the qualification: every feature subset's
basketing was compared against the basketing built from all the dimensions it left
out, and on real data the WORST subset at every size beat the BEST subset under
permutation - 0.369 against 0.152 at one feature, 0.472 against 0.244 at four. The
distributions do not overlap. Random k-combinations do explain their complements
here, so averaging across them is not a popularity contest among bad baskets and a
consensus is licensed.

It is licensed CONDITIONALLY, so the condition is carried in the arithmetic rather
than in a footnote. Each subset votes with weight

    w_F = ARI(P_F, P_~F) - max(permuted ARI at that size)

its demonstrated ability to explain what it did not see, net of what the same
procedure reaches on data with the station-to-value tie cut. A subset that could not
clear the permuted ceiling would get weight zero and be silent. None are, here.

The votes are cast per station PAIR - the weighted fraction of subsets putting a and
b in the same basket - because that is the quantity partitions can be averaged over
without choosing a labelling. Clustering the resulting co-association matrix under
the same contiguity constraint gives the consensus basketing.

Then the only question left: does the consensus agree with the drawn water bodies?

Reads   docs/data/areas/stations_series.{json,bin}, station_waterbody_overlay.json,
        partition_complement[_permuted].json
Writes  docs/data/areas/partition_consensus.json
"""
import collections
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json
from partition_stability import D, MIN_MONTHS, MAX_STATIONS, load, deviations, ari
from partition_contiguous import (KNN, build_graph, components,
                                  agglomerate_contiguous, contiguous_null)
from partition_subspace import pair_corr, distances_cached

NGROUPS = 84


def main():
    meta, ov, per = load()
    smeta = meta["stations"]
    wb = ov["waterbody_index"]
    keys = [v["key"] for v in meta["variables"]]
    V = len(keys)

    counts = collections.Counter()
    for q in keys:
        for s, d in per[q].items():
            if len(d) >= MIN_MONTHS:
                counts[s] += 1
    usable = sorted(s for s, c in counts.items()
                    if c == V and smeta[s].get("lat") is not None)[:MAX_STATIONS]
    n = len(usable)
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
    log(f"  {n} stations, {k_groups} groups, contiguous null ARI {ari0:+.3f}")

    perm = json.load(open(os.path.join(D, "partition_complement_permuted.json"),
                          encoding="utf-8"))
    ceil = {r["features_in_basket"]: r["complement_agreement"]["max"]
            for r in perm["results"]}
    log("  permuted ceiling per size: "
        + "  ".join(f"k={k}:{v:+.3f}" for k, v in sorted(ceil.items())))

    mats = [pair_corr(usable, devs[q]) for q in keys]
    part = {}
    allsub = [c for k in range(1, V) for c in itertools.combinations(range(V), k)]
    for i, sub in enumerate(allsub):
        part[sub] = agglomerate_contiguous(distances_cached(n, mats, sub),
                                           adj, k_groups)
        if (i + 1) % 150 == 0:
            log(f"    clustered {i+1}/{len(allsub)}")

    co = [[0.0] * n for _ in range(n)]
    wtot = 0.0
    voters, silenced = [], 0
    for k in range(1, V // 2 + 1):
        for f in [s for s in allsub if len(s) == k]:
            comp = tuple(i for i in range(V) if i not in f)
            w = ari(part[f], part[comp]) - ceil.get(k, 0.0)
            if w <= 0:
                silenced += 1
                continue
            lab = part[f]
            wtot += w
            voters.append((w, f))
            for a in range(n):
                la = lab[a]; ca = co[a]
                for b in range(a + 1, n):
                    if lab[b] == la:
                        ca[b] += w; co[b][a] += w
    log(f"  {len(voters)} subsets voted, {silenced} silenced by the permuted ceiling")

    dist = [[1.0 - co[a][b] / wtot if a != b else 0.0 for b in range(n)]
            for a in range(n)]
    consensus = agglomerate_contiguous(dist, adj, k_groups)

    a_off = ari(consensus, official)
    a_null = sum(ari(consensus, nl) for nl in nulls) / len(nulls)
    per_voter = [(ari(consensus, part[f]), f) for _, f in voters]
    per_voter.sort(reverse=True)
    name = lambda f: "+".join(keys[i] for i in f)
    top = sorted(voters, reverse=True)[:5]

    log(f"\n  consensus vs official water bodies : ARI {a_off:+.3f}"
        f"   (contiguous null {a_null:+.3f}, lift {a_off - a_null:+.3f})")
    log(f"  consensus vs its own voters        : ARI {sum(x for x,_ in per_voter)/len(per_voter):+.3f}"
        f"  best {per_voter[0][0]:+.3f} ({name(per_voter[0][1])})")

    write_json(os.path.join(D, "partition_consensus.json"), {
        "_what": "A consensus basketing built by weighted voting among feature "
                 "subsets, each weighted by how well its basketing explained the "
                 "dimensions it did not use.",
        "_why": "Averaging across subsets is only meaningful once the subsets are "
                "shown to produce good baskets. partition_complement.py showed the "
                "worst real subset beats the best permuted one at every size, so "
                "every subset qualifies and the weighting is licensed. The weight "
                "carries the condition: complement agreement minus the permuted "
                "ceiling, so a subset that could not clear it would be silent.",
        "_reading": "consensus_vs_official is the headline. Its floor is "
                    "consensus_vs_contiguous_null - a fixed contiguous partition "
                    "scored against random connected ones - not zero.",
        "stations": n, "groups": k_groups, "voters": len(voters),
        "silenced": silenced, "permuted_ceiling": ceil,
        "contiguous_null_ari": round(ari0, 3),
        "consensus_vs_official": round(a_off, 3),
        "consensus_vs_contiguous_null": round(a_null, 3),
        "official_lift": round(a_off - a_null, 3),
        "consensus_vs_voters_mean": round(sum(x for x, _ in per_voter)
                                          / len(per_voter), 3),
        "heaviest_voters": [{"features": name(f), "weight": round(w, 3)}
                            for w, f in top],
        "closest_to_consensus": [{"features": name(f), "ari": round(a, 3)}
                                 for a, f in per_voter[:5]]})
    log("\n  wrote partition_consensus.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
