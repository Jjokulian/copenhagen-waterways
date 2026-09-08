#!/usr/bin/env python3
"""Do the same baskets emerge from independent halves of the feature space?

Every earlier test on this data compares a partition against a null, which is still
conditioned on the features chosen: it answers "given these measurements, is this
grouping better than chance". It cannot answer whether the grouping is a property of
the places or an artifact of what happened to be measured.

Stability answers that, and needs no null and no assumed partition:

    Cluster the stations using a random subset of the variables.
    Cluster them again using a DISJOINT random subset.
    Ask how much the two agree.

A basket that appears only when oxygen is in the subset is an oxygen artifact. A
basket that appears whichever variables are drawn is a property of the stations. And
if agreement RISES as the subsets grow, the derivations are converging on something;
if it stays flat and low, there is nothing to converge on.

Agreement is the adjusted Rand index: the proportion of station pairs the two
partitions agree about (together, or apart), corrected for the agreement two random
partitions of the same shape would reach by chance. 0 is chance, 1 is identity.

The official partition is scored on the same axis - its ARI against each derived
partition - so it is one candidate among the derivations rather than the thing being
graded.

**Deliberately coarse.** Earlier runs matched the official granularity, about four
stations per group, where a random partition scored 0.917 and the statistic had no
room left. Here the target is a dozen groups over a few hundred stations, which is
where a comparison can still discriminate.

Reads   docs/data/areas/stations_series.{json,bin}, station_waterbody_overlay.json
Writes  docs/data/areas/partition_stability.json
"""
import array
import collections
import itertools
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json

D = os.path.join(ROOT, "docs", "data", "areas")
# Granularity is a knob, and it has to be, because comparing a derived partition
# against the official one at DIFFERENT granularities is not a comparison: ARI is
# depressed by a group-count mismatch on its own, so a low score would be
# uninterpretable. Pass a count to match the official one and the derived-vs-derived
# column becomes the control - if agreement collapses there too, the granularity
# killed the test rather than the official partition failing it.
NGROUPS = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 12
MIN_MONTHS = 36
MIN_SHARED = 12
MAX_STATIONS = 150
PAIRS_PER_SIZE = 12


def load():
    meta = json.load(open(os.path.join(D, "stations_series.json"), encoding="utf-8"))
    blob = open(os.path.join(D, "stations_series.bin"), "rb").read()
    ov = json.load(open(os.path.join(D, "station_waterbody_overlay.json"),
                       encoding="utf-8"))
    per = {}
    for v in meta["variables"]:
        n, o = v["n"], v["offset"]
        si = array.array("H"); si.frombytes(blob[o:o + 2 * n])
        mo = array.array("H"); mo.frombytes(blob[o + 2 * n:o + 4 * n])
        va = array.array("f"); va.frombytes(blob[o + 4 * n:o + 8 * n])
        d = collections.defaultdict(dict)
        for i in range(n):
            d[si[i]][mo[i]] = va[i]
        per[v["key"]] = d
    return meta, ov, per


def deviations(d, stations):
    """Remove the month effect: every station shares a season, and leaving it in
    makes every pair of stations look alike."""
    bym = collections.defaultdict(list)
    for s in stations:
        for m, v in d.get(s, {}).items():
            bym[m].append(v)
    mu = {m: sum(v) / len(v) for m, v in bym.items() if len(v) >= 3}
    return {s: {m: v - mu[m] for m, v in d.get(s, {}).items() if m in mu}
            for s in stations}


def distances(stations, devs):
    """1 - correlation, averaged over whichever variables in the subset have enough
    shared months for the pair. A pair with no usable variable gets the neutral 1.0."""
    n = len(stations)
    dist = [[1.0] * n for _ in range(n)]
    for a in range(n):
        for b in range(a + 1, n):
            rs = []
            for dv in devs:
                da, db = dv.get(stations[a], {}), dv.get(stations[b], {})
                common = da.keys() & db.keys()
                if len(common) < MIN_SHARED:
                    continue
                xs = [da[m] for m in common]
                ys = [db[m] for m in common]
                mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
                sxx = sum((x - mx) ** 2 for x in xs)
                syy = sum((y - my) ** 2 for y in ys)
                if sxx <= 0 or syy <= 0:
                    continue
                rs.append(sum((x - mx) * (y - my) for x, y in zip(xs, ys))
                          / (sxx * syy) ** 0.5)
            if rs:
                dist[a][b] = dist[b][a] = 1.0 - sum(rs) / len(rs)
    return dist


def agglomerate(dist, k):
    groups = [[i] for i in range(len(dist))]
    while len(groups) > k:
        best = None
        for i in range(len(groups)):
            gi = groups[i]
            for j in range(i + 1, len(groups)):
                gj = groups[j]
                d = sum(dist[a][b] for a in gi for b in gj) / (len(gi) * len(gj))
                if best is None or d < best[0]:
                    best = (d, i, j)
        _, i, j = best
        groups[i] += groups[j]
        groups.pop(j)
    lab = [0] * len(dist)
    for gi, g in enumerate(groups):
        for a in g:
            lab[a] = gi
    return lab


def ari(a, b):
    """Adjusted Rand index between two label vectors."""
    n = len(a)
    tab = collections.Counter(zip(a, b))
    ra = collections.Counter(a)
    rb = collections.Counter(b)
    c2 = lambda x: x * (x - 1) / 2
    idx = sum(c2(v) for v in tab.values())
    ea = sum(c2(v) for v in ra.values())
    eb = sum(c2(v) for v in rb.values())
    exp = ea * eb / c2(n) if n > 1 else 0
    mx = (ea + eb) / 2
    return round((idx - exp) / (mx - exp), 3) if mx != exp else 0.0


def beta_fit(draws):
    """Moment-match a Beta to the per-draw agreements, and read off what a basket
    is worth.

    The point of doing this at all: a basket used as a prior for one of its members
    supplies a mean by pooling, and supplies a CONCENTRATION by nothing whatsoever.
    Beta(a, b) is pseudo-counts and a + b is what the prior is worth in observations,
    so an untested boundary is the standard route to a confident prior nobody earned.

    Two separate numbers come out and they are not interchangeable:

      m       mean agreement. How much of the boundary reproduces when the feature
              space it was derived from is swapped for a disjoint one. This is the
              corrective: a group of n members is worth about m*n pseudo-observations
              rather than n. Laplace's +1/+2 in structure, estimated instead of
              assumed.

      kappa   a + b of the fitted Beta. This is how well m itself is pinned down
              ACROSS DRAWS - the reproducibility of the stability estimate, not the
              pooling licence. Conflating it with the licence would be the same
              category error this file exists to test for.

    ARI runs below zero (two partitions can agree less than chance), and a Beta does
    not, so draws are clipped at 0. That is a floor, not a rescaling: a negative ARI
    and a zero ARI both mean the boundary carries nothing, and the difference between
    them is not information about how much.
    """
    v = [min(1.0, max(0.0, x)) for x in draws]
    n = len(v)
    m = sum(v) / n
    var = sum((x - m) ** 2 for x in v) / (n - 1) if n > 1 else 0.0
    # kappa is undefined where the draws are degenerate (all identical, or the mean
    # pinned at an end) - report the mean and say so rather than emit a number the
    # data does not support.
    if var <= 0 or not (0 < m < 1) or var >= m * (1 - m):
        return {"mean_agreement": round(m, 3), "alpha": None, "beta": None,
                "kappa": None, "worth_per_member": round(m, 3),
                "note": "too few or too uniform draws to pin the concentration"}
    kappa = m * (1 - m) / var - 1
    return {"mean_agreement": round(m, 3),
            "alpha": round(m * kappa, 2), "beta": round((1 - m) * kappa, 2),
            "kappa": round(kappa, 2), "worth_per_member": round(m, 3)}


def main():
    rng = random.Random(31)
    meta, ov, per = load()
    wb = ov["waterbody_index"]
    keys = sorted(per)
    counts = collections.Counter()
    for k in keys:
        for s, d in per[k].items():
            if len(d) >= MIN_MONTHS and wb[s] >= 0:
                counts[s] += 1
    stations = [s for s, c in counts.items() if c == len(keys)]
    stations.sort(key=lambda s: -sum(len(per[k].get(s, {})) for k in keys))
    stations = sorted(stations[:MAX_STATIONS])
    log(f"  {len(stations)} stations measured on all {len(keys)} variables")
    if len(stations) < 40:
        log("  too few for a stability test")
        return 1
    devs = {k: deviations(per[k], stations) for k in keys}
    official = [wb[s] for s in stations]
    log(f"  official partition puts them in {len(set(official))} water bodies")

    cache = {}
    def part(subset):
        if subset not in cache:
            cache[subset] = agglomerate(
                distances(stations, [devs[k] for k in subset]), NGROUPS)
        return cache[subset]

    out = []
    for size in (1, 2, 3, 4):
        if 2 * size > len(keys):
            break
        pairs, seen = [], set()
        for _ in range(PAIRS_PER_SIZE * 6):
            if len(pairs) >= PAIRS_PER_SIZE:
                break
            pick = rng.sample(keys, 2 * size)
            a, b = tuple(sorted(pick[:size])), tuple(sorted(pick[size:]))
            if (a, b) in seen or (b, a) in seen:
                continue
            seen.add((a, b))
            pairs.append((a, b))
        cross, vs_off = [], []
        for a, b in pairs:
            pa, pb = part(a), part(b)
            cross.append(ari(pa, pb))
            vs_off.append(ari(pa, official))
            vs_off.append(ari(pb, official))
        mean = lambda v: round(sum(v) / len(v), 3)
        fit = beta_fit(cross)
        out.append({"features_per_half": size, "pairs": len(pairs),
                    "agreement_between_halves": mean(cross),
                    "best": max(cross), "worst": min(cross),
                    "agreement_with_official": mean(vs_off),
                    "prior_strength": fit})
        k = "-" if fit["kappa"] is None else f"{fit['kappa']:.1f}"
        log(f"    {size} feature(s) per half: derived-vs-derived ARI "
            f"{mean(cross):+.3f}  (worst {min(cross):+.3f}, best {max(cross):+.3f})"
            f"   derived-vs-official {mean(vs_off):+.3f}"
            f"   worth/member {fit['worth_per_member']:.3f}  kappa {k}")

    write_json(os.path.join(D, "partition_stability%s.json" % ("" if NGROUPS == 12 else "_g%d" % NGROUPS)), {
        "_what": "Do the same station groupings emerge from disjoint random halves "
                 "of the measured variables?",
        "_why": "A null test is conditioned on the features chosen and cannot say "
                "whether a grouping is a property of the places or of what happened "
                "to be measured. Agreement between derivations from disjoint "
                "feature subsets can, and assumes no partition at all.",
        "_reading": "agreement_between_halves is the adjusted Rand index: 0 is what "
                    "two random partitions of the same shape reach, 1 is identity. "
                    "Rising with features_per_half means the derivations converge; "
                    "flat and near zero means there is nothing to converge on.",
        "_prior_strength": "What a basket is worth as a Bayesian prior. Pooling the "
                           "members of a group gives a prior MEAN; nothing in the "
                           "membership rule gives it a concentration, and Beta(a,b) "
                           "priors are pseudo-counts where a+b is what the prior is "
                           "worth in observations. worth_per_member is the "
                           "corrective: a group of n members is worth about "
                           "worth_per_member * n pseudo-observations, not n. kappa is "
                           "a separate quantity - how well the agreement itself is "
                           "pinned down across draws - and is not the pooling "
                           "licence.",
        "_limit": "One clustering method (average linkage on 1 - correlation), one "
                  "granularity (%d groups), and only the stations measured on every "
                  "variable - which are the best-observed ones, so this is the "
                  "friendliest case rather than a representative one. The Beta fit "
                  "is exact only where the functional being predicted is a "
                  "proportion; for a continuous one the same role is played by a "
                  "normal-normal shrinkage weight and worth_per_member scales a "
                  "precision rather than a count." % NGROUPS,
        "groups": NGROUPS, "stations": len(stations),
        "official_groups_here": len(set(official)),
        "variables": keys, "results": out})
    log(f"\n  wrote partition_stability{'' if NGROUPS == 12 else f'_g{NGROUPS}'}.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
