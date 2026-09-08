#!/usr/bin/env python3
"""Derived baskets that must be spatially contiguous - the fair fight.

Every stability run so far let the derived partitions be any grouping at all. They
could interleave: a basket of stations scattered across the country, another one
threaded between them. The official water bodies cannot do that. They are contiguous
by construction, so comparing them against derivations that are not is not a
comparison, and it is unfair in the official partition's disfavour.

This constrains the derivations to the same shape. A basket may only contain stations
you can walk between, neighbour to neighbour, without stepping outside the basket -
"connected without excluding data sources in between". Formally: clusters start as
single stations and only ever merge with an ADJACENT cluster, so connectedness in the
neighbour graph is preserved by induction.

TWO NEIGHBOUR GRAPHS, because adjacency is itself a modelling decision and pretending
otherwise would be the error this project is about:

  knn    k nearest stations by distance on the sphere. Available nationally, cheap,
         and WRONG across land: two stations either side of a peninsula are close in
         kilometres and not connected by water.

  water  the same graph with every edge that crosses the OSM coastline removed, so an
         edge means "you can go straight from a to b without touching land". This is
         the physically meaningful one. It is only available where the coastline
         extract reaches (lon 11.0-13.7, lat 54.4-56.3 - Zealand, the Sound and the
         western Baltic), so it runs on a subset of stations and the two graphs are
         compared on their overlap. The coastline comes from OSM, NOT from the water
         body polygons, which would reimport the assumption under test.

THE NULL MATTERS MORE HERE THAN ANYWHERE ELSE. Contiguity by itself makes two
partitions agree: constrain any two groupings of the same points to be connected
blobs of the same sizes and they will share pairs far above chance, because both are
mostly reporting geography. The adjusted Rand index corrects for chance against
ARBITRARY partitions, not against contiguity-constrained ones, so a raw ARI here is
not readable. Every figure is therefore reported against `contiguous_null`: two
independent random connected partitions of matched size distribution, grown by
breadth-first accretion on the same graph. What is left after subtracting it is what
the MEASUREMENTS know beyond what the map already said.

Reads   docs/data/areas/stations_series.{json,bin}, station_waterbody_overlay.json,
        data/raw/osm/coastline.json
Writes  docs/data/areas/partition_contiguous.json

usage: partition_contiguous.py [NGROUPS]
"""
import collections
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json
from partition_stability import (D, MIN_MONTHS, MAX_STATIONS, PAIRS_PER_SIZE, load,
                                 deviations, distances, ari, beta_fit)

NGROUPS = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 12
KNN = 6
COAST = os.path.join(ROOT, "data", "raw", "osm", "coastline.json")


def km(a, b):
    """Equirectangular, which is accurate enough over Danish distances and does not
    need a trig library on the hot path."""
    la = (a["lat"] + b["lat"]) / 2 * 0.017453292519943295
    dx = (a["lon"] - b["lon"]) * 111.32 * (1 - la * la / 2 + la ** 4 / 24)
    dy = (a["lat"] - b["lat"]) * 110.57
    return (dx * dx + dy * dy) ** 0.5


def crosses(p, q, segs):
    """Does segment p-q properly cross any coastline segment? Both endpoints are
    marine stations, so ANY crossing means the straight line went ashore - a
    conservative rule, and the one that matches 'without touching land'."""
    def side(a, b, c):
        return ((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
    for r, s in segs:
        d1, d2 = side(p, q, r), side(p, q, s)
        if (d1 > 0) == (d2 > 0):
            continue
        d3, d4 = side(r, s, p), side(r, s, q)
        if (d3 > 0) != (d4 > 0):
            return True
    return False


def coastline_index(cell=0.05):
    """Grid index of coastline segments. 132,000 segments tested per candidate edge
    would be 60 million tests; bucketing makes it a few hundred."""
    try:
        ways = json.load(open(COAST, encoding="utf-8"))
    except OSError:
        return None, None
    grid = collections.defaultdict(list)
    lo = [9e9, 9e9, -9e9, -9e9]
    for w in ways:
        for i in range(len(w) - 1):
            a, b = tuple(w[i]), tuple(w[i + 1])
            lo[0] = min(lo[0], a[0]); lo[1] = min(lo[1], a[1])
            lo[2] = max(lo[2], a[0]); lo[3] = max(lo[3], a[1])
            x0, x1 = sorted((a[0], b[0])); y0, y1 = sorted((a[1], b[1]))
            for cx in range(int(x0 / cell), int(x1 / cell) + 1):
                for cy in range(int(y0 / cell), int(y1 / cell) + 1):
                    grid[(cx, cy)].append((a, b))
    return grid, lo


def near_segs(grid, p, q, cell=0.05):
    x0, x1 = sorted((p[0], q[0])); y0, y1 = sorted((p[1], q[1]))
    out = []
    for cx in range(int(x0 / cell), int(x1 / cell) + 1):
        for cy in range(int(y0 / cell), int(y1 / cell) + 1):
            out.extend(grid.get((cx, cy), ()))
    return out


def build_graph(pts, k, grid=None, cell=0.05):
    """Symmetrised k-nearest-neighbour graph, optionally with land-crossing edges
    dropped. Dropping edges can disconnect the graph, which is not a failure - it is
    the map saying two places are not reachable - so components are reported."""
    n = len(pts)
    adj = [set() for _ in range(n)]
    dropped = 0
    for i in range(n):
        order = sorted(range(n), key=lambda j: km(pts[i], pts[j]))[1:k + 1]
        for j in order:
            if grid is not None:
                p = (pts[i]["lon"], pts[i]["lat"]); q = (pts[j]["lon"], pts[j]["lat"])
                if crosses(p, q, near_segs(grid, p, q, cell)):
                    dropped += 1
                    continue
            adj[i].add(j); adj[j].add(i)
    return adj, dropped


def components(adj):
    n = len(adj); seen = [False] * n; comps = []
    for s in range(n):
        if seen[s]:
            continue
        stack, c = [s], []
        seen[s] = True
        while stack:
            u = stack.pop(); c.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True; stack.append(v)
        comps.append(c)
    return comps


def agglomerate_contiguous(dist, adj, k):
    """Average linkage, but a merge is only ever between ADJACENT clusters, so every
    cluster stays connected in the graph. Returns labels, or None if the graph has
    more components than the requested group count - in which case the constraint,
    not the data, decided the answer, and saying so beats returning a number."""
    n = len(dist)
    mem = {i: [i] for i in range(n)}
    cadj = {i: set(adj[i]) for i in range(n)}
    ncomp = len(components(adj))
    if k < ncomp:
        return None
    while len(mem) > k:
        best = None
        for i, ns in cadj.items():
            gi = mem[i]
            for j in ns:
                if j <= i:
                    continue
                gj = mem[j]
                d = sum(dist[a][b] for a in gi for b in gj) / (len(gi) * len(gj))
                if best is None or d < best[0]:
                    best = (d, i, j)
        if best is None:
            break
        _, i, j = best
        mem[i] += mem.pop(j)
        cadj[i] |= cadj.pop(j)
        cadj[i].discard(i); cadj[i].discard(j)
        for s in cadj.values():
            if j in s:
                s.discard(j); s.add(i)
        cadj[i].discard(i)
    lab = [0] * n
    for gi, (_, g) in enumerate(sorted(mem.items())):
        for a in g:
            lab[a] = gi
    return lab


def contiguous_null(adj, sizes, seed):
    """A random CONNECTED partition of matched size distribution: pick a free seed,
    grow by breadth-first accretion until the size is met. This is the reference the
    derived partitions have to beat, because two contiguous partitions agree with
    each other well above chance for no reason but contiguity."""
    rnd = random.Random(seed)
    n = len(adj)
    free = set(range(n))
    lab = [None] * n
    gi = 0
    for size in sizes:
        if not free:
            break
        start = rnd.choice(sorted(free))
        blob = [start]; free.discard(start)
        frontier = [start]
        while len(blob) < size and frontier:
            u = frontier.pop(0)
            for v in sorted(adj[u]):
                if v in free and len(blob) < size:
                    free.discard(v); blob.append(v); frontier.append(v)
        for i in blob:
            lab[i] = gi
        gi += 1
    for i in range(n):                      # leftovers join their nearest labelled
        if lab[i] is None:
            lab[i] = gi; gi += 1
    return lab


def main():
    rng = random.Random(23)
    meta, ov, per = load()
    stations_meta = meta["stations"]
    wb = ov["waterbody_index"]

    keys = [v["key"] for v in meta["variables"]]
    counts = collections.Counter()
    for k in keys:
        for s, d in per[k].items():
            if len(d) >= MIN_MONTHS:
                counts[s] += 1
    usable = sorted(s for s, c in counts.items() if c == len(keys)
                    and stations_meta[s].get("lat") is not None)
    if len(usable) > MAX_STATIONS:              # same cap as partition_stability,
        usable = usable[:MAX_STATIONS]          # so the two runs are comparable
    log(f"  {len(usable)} stations measured on all {len(keys)} variables")

    devs = {k: deviations(per[k], usable) for k in keys}
    pts = [stations_meta[s] for s in usable]
    official = [wb[s] for s in usable]
    sizes = sorted(collections.Counter(x for x in official if x is not None
                                       and x >= 0).values(), reverse=True)
    if not sizes:
        sizes = [max(1, len(usable) // NGROUPS)] * NGROUPS

    grid, extent = coastline_index()
    graphs = {}
    adj_knn, _ = build_graph(pts, KNN)
    graphs["knn"] = (adj_knn, list(range(len(pts))))
    log(f"  knn graph: {sum(len(a) for a in adj_knn)//2} edges, "
        f"{len(components(adj_knn))} component(s)")

    if grid:
        inside = [i for i, p in enumerate(pts)
                  if extent[0] <= p["lon"] <= extent[2]
                  and extent[1] <= p["lat"] <= extent[3]]
        log(f"  coastline covers lon {extent[0]:.2f}-{extent[2]:.2f} "
            f"lat {extent[1]:.2f}-{extent[3]:.2f}: {len(inside)} of {len(pts)} "
            f"stations inside")
        if len(inside) >= 20:
            sub = [pts[i] for i in inside]
            adj_w, dropped = build_graph(sub, KNN, grid)
            log(f"  water graph: {sum(len(a) for a in adj_w)//2} edges "
                f"({dropped} candidate edges crossed land), "
                f"{len(components(adj_w))} component(s)")
            graphs["water"] = (adj_w, inside)
            adj_k2, _ = build_graph(sub, KNN)
            graphs["knn_same_area"] = (adj_k2, inside)

    out = {}
    for gname, (adj, idx) in graphs.items():
        sub_stations = [usable[i] for i in idx]
        sub_official = [official[i] for i in idx]
        ncomp = len(components(adj))
        # Scale the group count to the subset, and never ask for more groups than
        # half the stations. The first run asked for 84 groups over 25 stations: the
        # agglomeration loop never executed, every partition was all-singletons, and
        # every ARI was exactly 0.000. That is the constraint answering, not the
        # data, and it looked like a finding.
        # The degeneracy is k >= n: agglomeration does n-k merges, so asking for at
        # least as many groups as stations executes no merges at all and every
        # partition comes out all-singletons with ARI exactly 0.000. Cap at 0.8n,
        # which leaves the official granularity (84 groups over 150 stations, mean
        # size 1.79) reachable - a n/2 cap silently clustered to 75 instead, and the
        # official lift moved from about 0 to +0.06 on that change alone.
        want = max(2, round(NGROUPS * len(idx) / len(pts)))
        k = max(ncomp, min(want, max(2, int(len(idx) * 0.8))))
        ssz = [max(1, round(s * len(idx) / len(pts))) for s in sizes] or [len(idx)]
        log(f"\n  [{gname}] {len(idx)} stations, {ncomp} component(s), "
            f"clustering to {k} groups")

        cache = {}
        def part(subset):
            if subset not in cache:
                cache[subset] = agglomerate_contiguous(
                    distances(sub_stations, [devs[q] for q in subset]), adj, k)
            return cache[subset]

        nulls = [contiguous_null(adj, ssz, s) for s in (101, 202, 303, 404)]
        nn = [ari(nulls[a], nulls[b]) for a in range(len(nulls))
              for b in range(a + 1, len(nulls))]
        null_floor = sum(nn) / len(nn)
        log(f"    contiguous null vs itself: ARI {null_floor:+.3f}  "
            f"<- the floor everything below must beat")

        rows = []
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
                seen.add((a, b)); pairs.append((a, b))
            cross, vs_off = [], []
            for a, b in pairs:
                pa, pb = part(a), part(b)
                if pa is None or pb is None:
                    continue
                cross.append(ari(pa, pb))
                vs_off.append(ari(pa, sub_official))
                vs_off.append(ari(pb, sub_official))
            if not cross:
                continue
            m = lambda v: round(sum(v) / len(v), 3)
            rows.append({"features_per_half": size, "pairs": len(cross),
                         "agreement_between_halves": m(cross),
                         "lift_over_contiguous_null": round(m(cross) - null_floor, 3),
                         "agreement_with_official": m(vs_off),
                         "official_lift": round(m(vs_off) - null_floor, 3),
                         "prior_strength": beta_fit(cross)})
            log(f"    {size} feature(s)/half: derived-vs-derived {m(cross):+.3f} "
                f"(lift {m(cross)-null_floor:+.3f})   "
                f"derived-vs-official {m(vs_off):+.3f} "
                f"(lift {m(vs_off)-null_floor:+.3f})")
        out[gname] = {"stations": len(idx), "components": ncomp, "groups": k,
                      "contiguous_null_ari": round(null_floor, 3), "results": rows}

    write_json(os.path.join(D, "partition_contiguous.json"), {
        "_what": "Feature-subspace stability with the derived partitions forced to "
                 "be spatially contiguous, which is the shape the official water "
                 "bodies already have.",
        "_why": "Unconstrained derivations may interleave; water bodies cannot. "
                "Comparing them was not like for like, and was unfair to the "
                "official partition.",
        "_reading": "RAW ARI IS NOT READABLE HERE. Contiguity alone makes two "
                    "partitions agree well above chance, and the adjusted Rand "
                    "index corrects for chance against arbitrary partitions, not "
                    "contiguous ones. Read lift_over_contiguous_null: agreement "
                    "minus what two random connected partitions of the same size "
                    "distribution reach on the same graph. That is what the "
                    "measurements know beyond what the map already said.",
        "_graphs": "knn = k nearest neighbours by distance, national, but crosses "
                   "land. water = the same with edges crossing the OSM coastline "
                   "removed, so an edge means reachable in a straight line without "
                   "touching land; only where the coastline extract reaches. "
                   "knn_same_area is knn restricted to the water graph's stations, "
                   "so the two are comparable. The coastline is OSM, not the water "
                   "body polygons, which would reimport the assumption under test.",
        "knn_k": KNN, "requested_groups": NGROUPS, "graphs": out})
    log("\n  wrote partition_contiguous.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
