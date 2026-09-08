#!/usr/bin/env python3
"""Floor, official, ceiling: how much of the available structure do the baskets get?

A null tells you the partition beats chance. It cannot tell you how much better a
partition could have been. For that you need the other end of the scale — a partition
derived FROM the data rather than imposed on it — and then the official one has a
position between two references instead of a bare number.

    floor    a size- and shape-matched random partition
    official the VP3 water bodies
    derived  stations clustered by how alike their measurements actually are

**The ceiling must be scored out of sample or it is meaningless.** A partition fitted
to the data will score well on that data by construction; that is what fitting is. So
the months are split: odd months build the clusters, even months score every
partition. The official partition and the null are scored on the same even months, so
all three numbers are comparable and none of them is fitted to what it is scored on.

Method. For each variable, take stations with enough months. Remove the month effect
(every station shares a season, and leaving it in flatters everything). Compute
station-to-station similarity as the correlation of those deviations over shared
months. Cluster by average-linkage agglomeration down to the same number of groups
the official partition uses on the same stations. Score all three by intraclass
correlation on the held-out months.

This does not produce "the right boundaries". It produces an upper bound on what any
partition of this granularity could have achieved for this variable, which is what
makes the official number readable.

Reads   docs/data/areas/stations_series.{json,bin}, station_waterbody_overlay.json
Writes  docs/data/areas/partition_ceiling.json
"""
import array
import collections
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json

D = os.path.join(ROOT, "docs", "data", "areas")
MIN_MONTHS = 24          # per station, to make a correlation worth computing
MIN_SHARED = 12          # months two stations must share to be comparable


def load():
    meta = json.load(open(os.path.join(D, "stations_series.json"), encoding="utf-8"))
    blob = open(os.path.join(D, "stations_series.bin"), "rb").read()
    ov = json.load(open(os.path.join(D, "station_waterbody_overlay.json"),
                       encoding="utf-8"))
    out = {}
    for v in meta["variables"]:
        n, o = v["n"], v["offset"]
        si = array.array("H"); si.frombytes(blob[o:o + 2 * n])
        mo = array.array("H"); mo.frombytes(blob[o + 2 * n:o + 4 * n])
        va = array.array("f"); va.frombytes(blob[o + 4 * n:o + 8 * n])
        out[v["key"]] = (si, mo, va, v)
    return meta, ov, out


def icc(months, label):
    sw = sb = 0.0
    nw = nb = used = 0
    for rows in months:
        g = collections.defaultdict(list)
        for s, v in rows:
            k = label(s)
            if k is not None:
                g[k].append(v)
        g = {k: v for k, v in g.items() if v}
        if len(g) < 2 or sum(len(v) for v in g.values()) < 4:
            continue
        used += 1
        allv = [x for v in g.values() for x in v]
        gm = sum(allv) / len(allv)
        for k, v in g.items():
            m = sum(v) / len(v)
            sb += len(v) * (m - gm) ** 2
            nb += 1
            for x in v:
                sw += (x - m) ** 2
                nw += 1
    if used < 8 or nb <= used or nw <= nb:
        return None
    msb = sb / max(1, nb - used)
    msw = sw / max(1, nw - nb)
    return round(msb / (msb + msw), 3) if msb + msw > 0 else None


def cluster(stations, dev, k):
    """Average-linkage agglomeration on correlation distance. No scipy on this box,
    and one distance matrix does not justify a dependency."""
    idx = {s: i for i, s in enumerate(stations)}
    n = len(stations)
    dist = [[1.0] * n for _ in range(n)]
    for a in range(n):
        da = dev[stations[a]]
        for b in range(a + 1, n):
            db = dev[stations[b]]
            common = da.keys() & db.keys()
            if len(common) < MIN_SHARED:
                continue
            xs = [da[m] for m in common]
            ys = [db[m] for m in common]
            mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
            sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            sxx = sum((x - mx) ** 2 for x in xs)
            syy = sum((y - my) ** 2 for y in ys)
            r = sxy / ((sxx * syy) ** 0.5) if sxx > 0 and syy > 0 else 0.0
            dist[a][b] = dist[b][a] = 1.0 - r
    groups = [[i] for i in range(n)]
    while len(groups) > k:
        best = None
        for i in range(len(groups)):
            for j in range(i + 1, len(groups)):
                d = sum(dist[a][b] for a in groups[i] for b in groups[j]) \
                    / (len(groups[i]) * len(groups[j]))
                if best is None or d < best[0]:
                    best = (d, i, j)
        _, i, j = best
        groups[i] = groups[i] + groups[j]
        groups.pop(j)
    lab = {}
    for gi, g in enumerate(groups):
        for a in g:
            lab[stations[a]] = gi
    return lab


def main():
    rng = random.Random(23)
    meta, ov, series = load()
    wb = ov["waterbody_index"]
    out = []
    for key, (si, mo, va, vmeta) in series.items():
        per = collections.defaultdict(dict)
        for i in range(len(si)):
            per[si[i]][mo[i]] = va[i]
        stations = sorted(s for s, d in per.items()
                          if len(d) >= MIN_MONTHS and wb[s] >= 0)
        if len(stations) < 20:
            continue
        # month effect removed on the FIT half only, then reused on both
        fit = {m for m in range(meta["months"]) if m % 2 == 1}
        mmean = {}
        for m in fit:
            vals = [per[s][m] for s in stations if m in per[s]]
            if len(vals) >= 4:
                mmean[m] = sum(vals) / len(vals)
        dev = {s: {m: per[s][m] - mmean[m] for m in per[s] if m in mmean}
               for s in stations}
        dev = {s: d for s, d in dev.items() if len(d) >= MIN_SHARED}
        stations = sorted(dev)
        if len(stations) < 20:
            continue
        k = len({wb[s] for s in stations})
        if k < 2 or k >= len(stations):
            continue
        found = cluster(stations, dev, k)

        # score every partition on the HELD-OUT even months
        test = collections.defaultdict(list)
        for s in stations:
            for m, v in per[s].items():
                if m % 2 == 0:
                    test[m].append((s, v))
        months = [r for r in test.values() if len(r) >= 4]
        if len(months) < 8:
            continue
        sizes = collections.Counter(wb[s] for s in stations)
        shuffled = stations[:]
        rng.shuffle(shuffled)
        null = {}
        it = iter(shuffled)
        for gi, (grp, size) in enumerate(sizes.items()):
            for _ in range(size):
                try:
                    null[next(it)] = gi
                except StopIteration:
                    break
        r_off = icc(months, lambda s: wb[s] if wb[s] >= 0 else None)
        r_nul = icc(months, lambda s: null.get(s))
        r_cei = icc(months, lambda s: found.get(s))
        if None in (r_off, r_nul, r_cei):
            continue
        # "Ceiling" is optimistic naming. Average-linkage on correlation distance
        # is ONE clustering, and it can lose to the official partition - it did,
        # for bottom oxygen. When that happens the ratio is not merely wrong, it
        # is undefined, and reporting 3.566 would be worse than reporting nothing.
        # The honest reading of that case is the interesting one: enclosure
        # boundaries encoded something this method could not recover.
        span = r_cei - r_nul
        beats = r_cei <= r_off
        captured = (None if beats or span <= 0.001
                    else round((r_off - r_nul) / span, 3))
        out.append({"variable": key, "label": vmeta["label"],
                    "depth": vmeta["depth"], "stations": len(stations),
                    "groups": k, "test_months": len(months),
                    "floor_random": r_nul, "official": r_off,
                    "derived_candidate": r_cei,
                    "official_beats_derived": beats,
                    "share_of_available_structure": captured})
        log(f"    {key:12} {len(stations):4d} stns  {k:3d} groups   "
            f"floor {r_nul:.3f}  official {r_off:.3f}  derived {r_cei:.3f}   "
            + (f"official BEATS derived" if beats else f"captured {captured}"))
    out.sort(key=lambda r: -(r["share_of_available_structure"] or -9))
    write_json(os.path.join(D, "partition_ceiling.json"), {
        "_what": "Each variable scored three ways on held-out months: a "
                 "size-matched random partition (floor), the official water bodies, "
                 "and stations clustered by measured similarity (ceiling).",
        "_out_of_sample": "Clusters are built on odd months and every partition is "
                          "scored on even months. A partition fitted to the data it "
                          "is scored on wins by construction; that is fitting, not "
                          "structure.",
        "_reading": "share_of_available_structure = (official - floor) / (derived "
                    "- floor), and is null where the official partition beat the "
                    "derived one. 1.0 would mean the official partition captures "
                    "everything this method could find at that granularity; 0 means "
                    "it does no better than random groups of the same sizes.",
        "_when_official_wins": "official_beats_derived means agglomerative "
                               "clustering on correlation distance found nothing as "
                               "good as the drawn boundaries. That is evidence FOR "
                               "the partition on that variable: enclosure encoded "
                               "something the method could not recover from the "
                               "measurements alone.",
        "_limit": "The derived partition is a lower bound on the best possible partition - "
                  "average-linkage on correlation distance is one clustering among "
                  "many, and a better method would raise it, lowering every "
                  "captured share.",
        "results": out})
    log(f"\n  {len(out)} variables -> partition_ceiling.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
