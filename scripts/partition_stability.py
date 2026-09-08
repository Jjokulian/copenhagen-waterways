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
NGROUPS = 12
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
        out.append({"features_per_half": size, "pairs": len(pairs),
                    "agreement_between_halves": mean(cross),
                    "best": max(cross), "worst": min(cross),
                    "agreement_with_official": mean(vs_off)})
        log(f"    {size} feature(s) per half: derived-vs-derived ARI "
            f"{mean(cross):+.3f}  (worst {min(cross):+.3f}, best {max(cross):+.3f})"
            f"   derived-vs-official {mean(vs_off):+.3f}")

    write_json(os.path.join(D, "partition_stability.json"), {
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
        "_limit": "One clustering method (average linkage on 1 - correlation), one "
                  "granularity (%d groups), and only the stations measured on every "
                  "variable - which are the best-observed ones, so this is the "
                  "friendliest case rather than a representative one." % NGROUPS,
        "groups": NGROUPS, "stations": len(stations),
        "official_groups_here": len(set(official)),
        "variables": keys, "results": out})
    log(f"\n  wrote partition_stability.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
