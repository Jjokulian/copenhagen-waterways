#!/usr/bin/env python3
"""Score a partition, per variable: what is it predictive FOR?

A partition is not good or bad in general. It is good *for a variable*, because each
variable carries its own notion of two places being alike. Salinity is conservative,
so a gradient in it means two water masses; oxygen is produced and consumed in place,
so a gradient can mean the water differs or merely that the biology does. Asking
whether the water bodies are "right" has no answer. Asking what they predict does.

The statistic is the intraclass correlation, computed **within month**:

    ICC = between-basket variance / (between + within)

read as: pick two stations at random in the same month. If they are in the same
basket, how much more alike are they than two stations picked without regard to
basket?

CHANCE HERE IS 0.5, NOT 0. What is computed is the mean-square ratio
MSB / (MSB + MSW), not the ANOVA estimator (MSB - MSW) / (MSB + (k-1) MSW). Under
random labels both mean squares are unbiased for the same variance, so the ratio
tends to one half - simulated at 0.4988 over 20 runs of 150 stations in 12 random
groups. A raw value near 0.5 therefore means the partition tells you NOTHING, and
only the lift over a shape-matched null is readable on its own. See docs/GLOSSARY.md.

**Within month is the whole trick.** Every station in Denmark shares a season. Pool
across months and the seasonal signal lands in the between-basket term, and every
partition — including a deliberately absurd one — scores well. Removing the month
first leaves only the spatial question.

Two controls are computed beside the real partition, because a number with nothing to
compare it to is not a result:

  * **shuffled** — station labels permuted at random, keeping the basket sizes. This
    is what zero looks like given this sampling design.
  * **latitude bands** — baskets of equal count cut by latitude, ignoring hydrography
    entirely. A partition that cannot beat horizontal stripes is not encoding much.

Reads   docs/data/areas/stations_series.{json,bin}, station_waterbody_overlay.json
Writes  docs/data/areas/partition_score.json
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
    """Pooled within-month variance components. months: [(station, value)] per month."""
    sw = sb = 0.0
    nw = nb = 0
    used = 0
    for rows in months:
        groups = collections.defaultdict(list)
        for s, v in rows:
            g = label(s)
            if g is not None:
                groups[g].append(v)
        groups = {g: v for g, v in groups.items() if v}
        if len(groups) < 2 or sum(len(v) for v in groups.values()) < 4:
            continue
        used += 1
        allv = [x for v in groups.values() for x in v]
        gm = sum(allv) / len(allv)
        for g, v in groups.items():
            m = sum(v) / len(v)
            sb += len(v) * (m - gm) ** 2
            nb += 1
            for x in v:
                sw += (x - m) ** 2
                nw += 1
    if used < 12 or nb <= used or nw <= nb:
        return None
    msb = sb / max(1, nb - used)          # between-group, within-month
    msw = sw / max(1, nw - nb)
    tot = msb + msw
    return {"icc": round(msb / tot, 3) if tot > 0 else None,
            "months": used, "between_ms": round(msb, 4), "within_ms": round(msw, 4)}


def main():
    rng = random.Random(11)
    meta, ov, series = load()
    wb = ov["waterbody_index"]
    stations = meta["stations"]

    # control A: shuffled labels, basket sizes preserved
    real = [w for w in wb]
    shuf = real[:]
    rng.shuffle(shuf)

    # control B: latitude bands, equal station count, as many bands as real baskets
    order = sorted(range(len(stations)), key=lambda i: stations[i]["lat"])
    nb = len({w for w in real if w >= 0}) or 1
    band = [0] * len(stations)
    for rank, i in enumerate(order):
        band[i] = rank * nb // len(order)

    # control C: the one that actually isolates hydrography.
    #
    # Shuffling keeps the real baskets' very unequal sizes and destroys geography;
    # the latitude stripes keep compactness and equal sizes but ignore hydrography.
    # Neither varies one thing at a time, and they disagree about which variables
    # the partition helps with - surface oxygen saturation gains +0.065 over the
    # shuffle and +0.408 over stripes, which is not a small discrepancy.
    #
    # This control matches BOTH: baskets with the same size distribution as the
    # real ones, grown greedily from random seeds by nearest-neighbour, so they are
    # spatially compact blobs of the right sizes that follow no hydrography at all.
    # What the real partition beats here is what its boundaries know that mere
    # compactness does not.
    def compact_null(seed):
        rnd = random.Random(seed)
        sizes = sorted(collections.Counter(w for w in real if w >= 0).values(),
                       reverse=True)
        free = {i for i in range(len(stations)) if real[i] >= 0}
        lab = [None] * len(stations)
        for gi, size in enumerate(sizes):
            if not free:
                break
            seed_i = rnd.choice(sorted(free))
            sx, sy = stations[seed_i]["lon"], stations[seed_i]["lat"]
            near = sorted(free, key=lambda i:
                          (stations[i]["lon"] - sx) ** 2
                          + (stations[i]["lat"] - sy) ** 2)[:size]
            for i in near:
                lab[i] = gi
                free.discard(i)
        return lab
    compacts = [compact_null(s) for s in (3, 5, 8)]

    out = []
    for key, (si, mo, va, vmeta) in series.items():
        bym = collections.defaultdict(list)
        for i in range(len(si)):
            bym[mo[i]].append((si[i], va[i]))
        months = [r for r in bym.values() if len(r) >= 4]
        r_real = icc(months, lambda s: real[s] if real[s] >= 0 else None)
        r_shuf = icc(months, lambda s: shuf[s] if shuf[s] >= 0 else None)
        r_band = icc(months, lambda s: band[s])
        if not r_real:
            continue
        cs = [icc(months, (lambda c: lambda s: c[s])(c)) for c in compacts]
        cs = [c for c in cs if c]
        r_cmp = ({"icc": round(sum(c["icc"] for c in cs) / len(cs), 3),
                  "runs": len(cs),
                  "spread": round(max(c["icc"] for c in cs)
                                  - min(c["icc"] for c in cs), 3)} if cs else None)
        lift = (round(r_real["icc"] - r_cmp["icc"], 3) if r_cmp else None)
        out.append({"variable": key, "label": vmeta["label"],
                    "depth": vmeta["depth"], "unit": vmeta["unit"],
                    "water_bodies": r_real, "shuffled": r_shuf,
                    "latitude_bands": r_band, "size_matched_compact": r_cmp,
                    "lift_over_compact": lift})
        log(f"    {key:12} real {r_real['icc']}  shuffled {r_shuf['icc'] if r_shuf else '—'}"
            f"  stripes {r_band['icc'] if r_band else '—'}"
            f"  compact {r_cmp['icc'] if r_cmp else '—'}"
            f"  LIFT {lift}")

    out.sort(key=lambda r: -(r["lift_over_compact"] or -9))
    write_json(os.path.join(D, "partition_score.json"), {
        "_what": "How much of the between-station variation each variable's values "
                 "are explained by water-body membership, within month.",
        "_reading": "CHANCE IS 0.5, NOT 0: this is the mean-square ratio "
                    "MSB/(MSB+MSW), not the ANOVA ICC, and under random labels both "
                    "mean squares estimate the same variance so the ratio tends to "
                    "one half (simulated 0.4988). Read 'lift' - the difference from "
                    "the compact null - not the raw value. 1 = two stations in the "
                    "same basket agree completely and "
                    "membership tells you everything; 0 = membership tells you "
                    "nothing beyond the month.",
        "_controls": "shuffled = station labels permuted with basket sizes kept, "
                     "which is what zero looks like under this sampling design. "
                     "latitude_bands = equal-count horizontal stripes ignoring "
                     "hydrography; a partition that cannot beat stripes is not "
                     "encoding much. size_matched_compact = baskets with the same "
                     "size distribution as the real ones, grown from random seeds "
                     "by nearest neighbour: compact blobs of the right sizes that "
                     "follow no hydrography. It is the only control that varies "
                     "one thing at a time, and lift_over_compact is the number to "
                     "read - the other two disagree with each other.",
        "_limit": "Stations are not placed at random and are denser in some baskets "
                  "than others, so this scores the partition AS SAMPLED rather than "
                  "the partition. It cannot distinguish a well-drawn basket from a "
                  "basket whose stations happen to sit close together.",
        "results": out})
    log(f"\n  {len(out)} variables scored -> partition_score.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
