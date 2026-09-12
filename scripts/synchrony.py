#!/usr/bin/env python3
"""Do stations move together, and do the water-body lines fall where they stop?

The water bodies are management units. Nothing in the data drew them. This asks what
grouping stations by them gains, on one criterion only: **co-movement over time**.
Similar levels are not evidence of a shared cause; two stations that are low for
unrelated reasons look alike in a map of means and share nothing. Moving together -
the same months bad, the same years worse than usual - is what a shared water or a
shared driver produces. So:

1. Anomalies. Each station's own seasonal cycle is removed: from each station-month
   the station's median for that calendar month is subtracted, provided that calendar
   month has at least MIN_YEARS years of data at the station (else it is dropped).
2. Per station pair, on months both have an anomaly (at least MIN_OVERLAP of them),
   Kendall's tau-b between the two anomaly series. For bed oxygen, also event
   co-occurrence: months below a conventional threshold, both-in-event against
   either-in-event.
3. Chance by time shift, not by random baskets. One station's series is rotated by
   whole years inside the pair's joint window (Jan of the first shared year to Dec of
   the last), which keeps its calendar months, its season-free structure and its
   autocorrelation, and breaks only the alignment in time. The pair co-moves beyond
   chance if its tau exceeds the shifted taus at level ALPHA. No comparison with
   shuffled or size-matched groups of stations is made anywhere: a random basket
   shares no cause, so beating one proves nothing.
4. Distance is its own axis: great-circle km per pair, results binned.
5. The deciding comparison: within the same water body against different water
   bodies, at matched distance (bin by bin).
6. The data's own groups: a graph whose edges are the beyond-chance pairs, its
   connected components, and Louvain communities on it (stated method, fixed seeds).

Water-body membership is the positional overlay in
docs/data/areas/station_waterbody_overlay.json (point-in-polygon on the panel's own
station positions, keyed by the panel's own station ids), not a join on station
numbers.

The pairwise loop is a small C kernel (compiled once into $TMPDIR). Peak memory: the
station x month grid (1,415 x 564 float32, 3 MB) twice, plus per-pair shift results,
pairs x 47 x 6 bytes - under 20 MB for every pair that clears MIN_OVERLAP.

Reads   docs/data/areas/stations_series.{json,bin},
        docs/data/areas/station_waterbody_overlay.json, data/derived/areas.json
Writes  data/derived/synchrony.json
"""
import array
import ctypes
import datetime
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import warnings

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json

AREAS = os.path.join(ROOT, "docs", "data", "areas")

VARS = ["oxy_bed", "oxysat_bed", "sal_bed", "temp_bed"]
# Values no instrument in these waters can produce. Negative oxygen is KEPT (it sits
# below every event threshold and Kendall's tau only uses ranks).
PLAUSIBLE_MAX = {"oxy_bed": 25.0, "oxysat_bed": 300.0}
MIN_YEARS = 5            # years per calendar month for a station's climatology
MIN_OVERLAP = 60         # shared anomaly months for a pair to be compared
MIN_NULL_OVERLAP = 30    # shared months for one shifted copy to count in the null
MIN_SHIFTS = 19          # valid shifts needed; p resolves to 1/20 = 0.05
ALPHA = 0.05
EVENT_THRESHOLDS = [4.0, 2.0]   # mg/l, conventions, not physiology
MIN_EVENT_MONTHS = 5     # months in which either station is in an event
NEAR_KM = 20.0
BINS = [0, 2, 5, 10, 15, 20, 30, 50, 75, 100, 150, 200, 300, 500, 1e9]
MIN_CELL = 5             # pairs per (bin, within/across) cell to enter the pooled figure
KNN = 5                  # spatial neighbours for the contiguity rule
LOUVAIN_SEEDS = [0, 1, 2, 3, 4]
FINE_BINS = list(range(0, 52, 2)) + [75, 100, 150, 200, 300, 500, 1e9]
MIN_YEAR_MONTHS = 4      # anomaly months in a year for the within-year layer
# Robustness: same-day sampling (dates from the raw CTD) and many tests (BH FDR).
CTD = os.path.join(ROOT, "data", "raw", "oda", "ctd.csv.gz")
ROBUST_VARS = ["oxy_bed", "sal_bed"]
BED_BIT = {"oxy_bed": 1, "sal_bed": 2}
BED_PARAM = {"Oxygen indhold": 1, "Salinitet": 2}
DIFF_DAY_GAPS = [1, 5]   # a pair-month is kept if the nearest two casts are >= this
                         # many days apart: 1 = different day, 5 = past one
                         # synoptic weather spell (a stated choice)
FDR_Q = 0.05

KERNEL = r"""
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
static double taub(const float*a,const float*b,int n){
  long long S=0,n1=0,n2=0,n0=(long long)n*(n-1)/2;
  for(int i=0;i<n;i++){float ai=a[i],bi=b[i];
    for(int j=i+1;j<n;j++){float da=ai-a[j],db=bi-b[j];
      int sa=(da>0)-(da<0),sb=(db>0)-(db<0);
      S+=sa*sb; n1+=(sa==0); n2+=(sb==0);}}
  double den=sqrt((double)(n0-n1)*(double)(n0-n2));
  return den>0? (double)S/den : NAN;
}
static int window(const float*A,const float*B,int M,int*base,int*L){
  int first=-1,last=-1;
  for(int t=0;t<M;t++) if(!isnan(A[t])&&!isnan(B[t])){if(first<0)first=t;last=t;}
  if(first<0) return 0;
  *base=12*(first/12); *L=last/12-first/12+1; return 1;
}
/* shift k rotates B by 12k months inside the pair's whole-year window; k=0 observed */
void pair_tau(const float*X,int M,const int32_t*pairs,int P,int Lmax,
              float*tau,int16_t*nn,int16_t*Lout){
  float*a=malloc(M*sizeof(float)),*b=malloc(M*sizeof(float));
  for(int p=0;p<P;p++){
    const float*A=X+(size_t)pairs[2*p]*M,*B=X+(size_t)pairs[2*p+1]*M;
    for(int k=0;k<Lmax;k++){tau[(size_t)p*Lmax+k]=NAN;nn[(size_t)p*Lmax+k]=0;}
    int base,L; if(!window(A,B,M,&base,&L)){Lout[p]=0;continue;}
    Lout[p]=L; int W=12*L;
    for(int k=0;k<L;k++){int n=0;
      for(int t=0;t<W;t++){float av=A[base+t],bv=B[base+(t+12*k)%W];
        if(!isnan(av)&&!isnan(bv)){a[n]=av;b[n]=bv;n++;}}
      nn[(size_t)p*Lmax+k]=n; tau[(size_t)p*Lmax+k]= n>=2? (float)taub(a,b,n):NAN;}
  }
  free(a);free(b);
}
void pair_events(const float*X,int M,const int32_t*pairs,int P,int Lmax,float thr,
                 int16_t*both,int16_t*either,int16_t*nn,int16_t*Lout){
  for(int p=0;p<P;p++){
    const float*A=X+(size_t)pairs[2*p]*M,*B=X+(size_t)pairs[2*p+1]*M;
    for(int k=0;k<Lmax;k++){size_t q=(size_t)p*Lmax+k;both[q]=0;either[q]=0;nn[q]=0;}
    int base,L; if(!window(A,B,M,&base,&L)){Lout[p]=0;continue;}
    Lout[p]=L; int W=12*L;
    for(int k=0;k<L;k++){int n=0,bo=0,ei=0;
      for(int t=0;t<W;t++){float av=A[base+t],bv=B[base+(t+12*k)%W];
        if(!isnan(av)&&!isnan(bv)){n++; int ea=av<thr, eb=bv<thr; bo+=ea&&eb; ei+=ea||eb;}}
      size_t q=(size_t)p*Lmax+k; both[q]=bo; either[q]=ei; nn[q]=n;}
  }
}
"""


def kernel():
    h = hashlib.sha1(KERNEL.encode()).hexdigest()[:12]
    so = os.path.join(tempfile.gettempdir(), f"synchrony_kernel_{h}.so")
    if not os.path.exists(so):
        src = so[:-3] + ".c"
        with open(src, "w") as f:
            f.write(KERNEL)
        subprocess.run(["gcc", "-O3", "-shared", "-fPIC", "-o", so, src, "-lm"],
                       check=True)
    lib = ctypes.CDLL(so)
    fp, ip = ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int32)
    sp = ctypes.POINTER(ctypes.c_int16)
    lib.pair_tau.argtypes = [fp, ctypes.c_int, ip, ctypes.c_int, ctypes.c_int,
                             fp, sp, sp]
    lib.pair_events.argtypes = [fp, ctypes.c_int, ip, ctypes.c_int, ctypes.c_int,
                                ctypes.c_float, sp, sp, sp, sp]
    return lib


def ptr(a, t):
    return a.ctypes.data_as(ctypes.POINTER(t))


def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(lon2 - lon1)
    h = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(h))


def r(x, d=4):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(float(x), d)


def load():
    meta = json.load(open(os.path.join(AREAS, "stations_series.json")))
    raw = open(os.path.join(AREAS, "stations_series.bin"), "rb").read()
    ov = json.load(open(os.path.join(AREAS, "station_waterbody_overlay.json")))
    ids = [s["id"] for s in meta["stations"]]
    assert ids == ov["station_ids"], "overlay and panel station lists differ"
    return meta, raw, ov


def grid(meta, raw, key):
    S, M = len(meta["stations"]), meta["months"]
    v = next(x for x in meta["variables"] if x["key"] == key)
    n, o = v["n"], v["offset"]
    st = np.frombuffer(raw, np.uint16, n, o)
    mo = np.frombuffer(raw, np.uint16, n, o + 2 * n)
    val = np.frombuffer(raw, np.float32, n, o + 4 * n)
    X = np.full((S, M), np.nan, np.float32)
    X[st, mo] = val
    return X, v


def anomalies(X):
    S, M = X.shape
    Y = M // 12
    Xr = X[:, :Y * 12].reshape(S, Y, 12)
    cnt = np.sum(~np.isnan(Xr), axis=1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        clim = np.nanmedian(Xr, axis=1)
    clim[cnt < MIN_YEARS] = np.nan
    A = np.full_like(X, np.nan)
    A[:, :Y * 12] = (Xr - clim[:, None, :]).reshape(S, Y * 12)
    return A, cnt >= MIN_YEARS


def within_year(A):
    """Remove each station's own median anomaly per year: month-scale only."""
    S, M = A.shape
    Y = M // 12
    Ar = A[:, :Y * 12].reshape(S, Y, 12)
    n = np.sum(~np.isnan(Ar), axis=2)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        med = np.nanmedian(Ar, axis=2)
    med[n < MIN_YEAR_MONTHS] = np.nan
    B = np.full_like(A, np.nan)
    B[:, :Y * 12] = (Ar - med[:, :, None]).reshape(S, Y * 12)
    return B


def overlap_pairs(P):
    f = P.astype(np.float32)
    ov = f @ f.T
    i, j = np.nonzero(np.triu(ov >= MIN_OVERLAP, 1))
    return np.ascontiguousarray(np.stack([i, j], 1).astype(np.int32)), ov[i, j]


def shift_p(obs, null, valid):
    """p = (1 + #null >= obs) / (1 + #valid), per pair; None-like where too few."""
    nvalid = valid.sum(1)
    ge = ((null >= obs[:, None]) & valid).sum(1)
    p = (1 + ge) / (1 + nvalid)
    return p, nvalid


def bin_of(d):
    return np.searchsorted(BINS, d, side="right") - 1


def bin_label(b):
    lo, hi = BINS[b], BINS[b + 1]
    return f"{lo:g}-{hi:g} km" if hi < 1e8 else f">={lo:g} km"


def pooled(binx, same, val, keep, nbins=len(BINS) - 1):
    """Within minus across, bin by bin, weighted by the within-pair count."""
    num = den = 0.0
    used = 0
    for b in range(nbins):
        mb = keep & (binx == b)
        mw, ma = mb & same, mb & ~same
        nw, na = int(mw.sum()), int(ma.sum())
        if nw >= MIN_CELL and na >= MIN_CELL:
            num += nw * (val[mw].mean() - val[ma].mean())
            den += nw
            used += 1
    return (num / den if den else None), int(den), used


def jackknife(binx, same, val, keep, wi, wj):
    groups = sorted(set(wi[keep].tolist()) | set(wj[keep].tolist()))
    groups = [g for g in groups if g >= 0]
    est = []
    for g in groups:
        d, _, _ = pooled(binx, same, val, keep & (wi != g) & (wj != g))
        if d is not None:
            est.append(d)
    G = len(est)
    if G < 3:
        return None, G
    e = np.array(est)
    return float(np.sqrt((G - 1) / G * np.sum((e - e.mean()) ** 2))), G


def compare(binx, same, assigned, keep, val, wi, wj, kind, dist):
    """Bin table and pooled distance-matched difference, within vs across."""
    k = keep & assigned
    rows = []
    for b in range(len(BINS) - 1):
        mb = k & (binx == b)
        mw, ma = mb & same, mb & ~same
        rows.append({"bin": bin_label(b),
                     "within_n": int(mw.sum()), "across_n": int(ma.sum()),
                     f"within_{kind}": r(val[mw].mean()) if mw.any() else None,
                     f"across_{kind}": r(val[ma].mean()) if ma.any() else None,
                     "within_median_km": r(np.median(dist[mw]), 1) if mw.any() else None,
                     "across_median_km": r(np.median(dist[ma]), 1) if ma.any() else None})
    d, w, used = pooled(binx, same, val, k)
    se, G = jackknife(binx, same, val, k, wi, wj)
    fb = np.searchsorted(FINE_BINS, dist, side="right") - 1
    dfine, wfine, ufine = pooled(fb, same, val, k, len(FINE_BINS) - 1)
    return {"by_bin": rows,
            "pooled_within_minus_across": r(d),
            "pooled_weight_within_pairs": w, "bins_used": used,
            "jackknife_se_leave_one_waterbody_out": r(se), "jackknife_waterbodies": G,
            "fine_bins_pooled_within_minus_across": r(dfine),
            "fine_bins_weight_within_pairs": wfine, "fine_bins_used": ufine}


def components(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    lab = [find(x) for x in range(n)]
    uniq = {v: i for i, v in enumerate(sorted(set(lab)))}
    return np.array([uniq[v] for v in lab])


def knn_graph(lat, lon):
    n = len(lat)
    D = haversine(lat[:, None], lon[:, None], lat[None, :], lon[None, :])
    np.fill_diagonal(D, np.inf)
    nb = [set() for _ in range(n)]
    k = min(KNN, n - 1)
    for i in range(n):
        for j in np.argsort(D[i])[:k]:
            nb[i].add(int(j))
            nb[int(j)].add(i)
    return nb, D


def connected_within(members, nb):
    ms = set(members)
    seen, stack = {members[0]}, [members[0]]
    while stack:
        x = stack.pop()
        for y in nb[x]:
            if y in ms and y not in seen:
                seen.add(y)
                stack.append(y)
    return len(seen) == len(ms)


def rand_index(a, b):
    n = len(a)
    if n < 2:
        return None
    same_a = a[:, None] == a[None, :]
    same_b = b[:, None] == b[None, :]
    iu = np.triu_indices(n, 1)
    return float((same_a[iu] == same_b[iu]).mean())


def describe_groups(labels, nodes, ids, lat, lon, wb, areas, names, nb, D, span):
    out, sizes = [], []
    for g in range(labels.max() + 1):
        mem = [int(x) for x in np.nonzero(labels == g)[0]]
        sizes.append(len(mem))
        if len(mem) < 2:
            continue
        w = [int(wb[nodes[m]]) for m in mem]
        spanned = sorted({areas[x] for x in w if x >= 0})
        sub = D[np.ix_(mem, mem)]
        out.append({
            "n_stations": len(mem),
            "contiguous": connected_within(mem, nb),
            "n_waterbodies": len(spanned),
            "n_outside_any_waterbody": sum(1 for x in w if x < 0),
            "waterbodies": [{"id": a, "name": names.get(a)} for a in spanned],
            "max_span_km": r(sub[np.isfinite(sub)].max(), 1),
            "median_first_year": r(np.median([span[nodes[m], 0] for m in mem]), 1),
            "median_last_year": r(np.median([span[nodes[m], 1] for m in mem]), 1),
            "centroid": [r(np.mean(lat[mem]), 3), r(np.mean(lon[mem]), 3)],
            "stations": [ids[nodes[m]] for m in mem],
        })
    out.sort(key=lambda g: -g["n_stations"])
    # water bodies split across groups
    split = {}
    for m, node in enumerate(nodes):
        a = int(wb[node])
        if a >= 0:
            split.setdefault(areas[a], []).append(int(labels[m]))
    sizes_arr = np.bincount(labels)
    wbs = []
    for a, labs in split.items():
        if len(labs) < 2:
            continue
        s = set(labs)
        wbs.append({"id": a, "name": names.get(a), "n_stations": len(labs),
                    "n_groups": len(s),
                    "n_groups_of_2_or_more": sum(1 for x in s if sizes_arr[x] >= 2),
                    "n_singletons": sum(1 for x in s if sizes_arr[x] == 1)})
    wbs.sort(key=lambda x: -x["n_stations"])
    multi = [g for g in out]
    summ = {
        "n_groups": int(labels.max() + 1),
        "n_groups_of_2_or_more": len(multi),
        "n_singletons": int(sum(1 for s in sizes if s == 1)),
        "largest_group": int(max(sizes)),
        "stations_in_largest_group": int(max(sizes)),
        "groups_2plus_contiguous": sum(1 for g in multi if g["contiguous"]),
        "groups_2plus_within_one_waterbody":
            sum(1 for g in multi if g["n_waterbodies"] <= 1),
        "groups_2plus_spanning_2plus_waterbodies":
            sum(1 for g in multi if g["n_waterbodies"] >= 2),
        "waterbodies_with_2plus_stations": len(wbs),
        "waterbodies_in_one_group": sum(1 for w in wbs if w["n_groups"] == 1),
        "waterbodies_split_across_2plus_groups":
            sum(1 for w in wbs if w["n_groups"] >= 2),
    }
    return summ, out, wbs


def graph_part(nodes, ids, lat_all, lon_all, wb, areas, names, pairs, beyond, tau0,
               dist, same, assigned, span):
    import networkx as nx
    n = len(nodes)
    pos = {int(s): k for k, s in enumerate(nodes)}
    e = pairs[beyond]
    edges = [(pos[int(a)], pos[int(b)]) for a, b in e]
    lat, lon = lat_all[nodes], lon_all[nodes]
    nb, D = knn_graph(lat, lon)
    knn_edge_km = [float(D[i, j]) for i in range(n) for j in nb[i] if j > i]
    cc = components(n, edges)
    cc_summary, cc_groups, cc_wbs = describe_groups(cc, nodes, ids, lat, lon, wb,
                                                    areas, names, nb, D, span)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for (a, b), w in zip(edges, tau0[beyond]):
        G.add_edge(a, b, weight=float(w))
    runs = []
    for s in LOUVAIN_SEEDS:
        comms = nx.community.louvain_communities(G, weight="weight", resolution=1.0,
                                                 seed=s)
        lab = np.empty(n, int)
        for k, c in enumerate(sorted(comms, key=lambda c: (-len(c), min(c)))):
            for x in c:
                lab[x] = k
        runs.append(lab)
    lv = runs[0]
    lv_summary, lv_groups, lv_wbs = describe_groups(lv, nodes, ids, lat, lon, wb,
                                                    areas, names, nb, D, span)
    # near pairs: do data groups and water bodies agree on who belongs together?
    agree = {}
    ia = np.array([pos.get(int(a), -1) for a in pairs[:, 0]])
    ib = np.array([pos.get(int(b), -1) for b in pairs[:, 1]])
    innode = (ia >= 0) & (ib >= 0)
    for name, lab in (("components", cc), ("louvain_seed0", lv)):
        sg = np.zeros(len(pairs), bool)
        sg[innode] = lab[ia[innode]] == lab[ib[innode]]
        m = innode & assigned & (dist < NEAR_KM)
        agree[name] = {
            "pairs_near_both_assigned": int(m.sum()),
            "same_group_same_wb": int((m & sg & same).sum()),
            "same_group_diff_wb": int((m & sg & ~same).sum()),
            "diff_group_same_wb": int((m & ~sg & same).sum()),
            "diff_group_diff_wb": int((m & ~sg & ~same).sum()),
        }
    return {
        "n_nodes": n, "n_edges": len(edges),
        "contiguity_rule": f"symmetric {KNN}-nearest-neighbour graph over the "
                           f"graph's stations (great-circle, land ignored); a group "
                           f"is contiguous if its stations are connected through "
                           f"links among themselves",
        "knn_link_km_median": r(np.median(knn_edge_km), 1) if knn_edge_km else None,
        "knn_link_km_p90": r(np.percentile(knn_edge_km, 90), 1) if knn_edge_km else None,
        "connected_components": {"summary": cc_summary, "groups": cc_groups,
                                 "waterbodies": cc_wbs},
        "louvain": {"method": "networkx louvain_communities, weight = observed tau, "
                              "resolution 1.0, seed 0 reported",
                    "seeds": LOUVAIN_SEEDS,
                    "n_communities_by_seed": [int(x.max() + 1) for x in runs],
                    "rand_index_vs_seed0": [r(rand_index(lv, x)) for x in runs[1:]],
                    "summary": lv_summary, "groups": lv_groups, "waterbodies": lv_wbs},
        "near_pair_agreement": agree,
    }


def analyse_tau(lib, key, meta, raw, ov, names, out_counts, layer="all"):
    S, M = len(meta["stations"]), meta["months"]
    X, vmeta = grid(meta, raw, key)
    c = {"stations_with_data": int((~np.isnan(X)).any(1).sum()),
         "station_months": int((~np.isnan(X)).sum())}
    if key in PLAUSIBLE_MAX:
        bad = X > PLAUSIBLE_MAX[key]
        c["dropped_implausible"] = int(bad.sum())
        X[bad] = np.nan
    A, okcm = anomalies(X)
    if layer == "within_year":
        A = within_year(A)
    PA = ~np.isnan(A)
    has = PA.any(1)
    first = np.where(has, PA.argmax(1), 0)
    last = np.where(has, M - 1 - PA[:, ::-1].argmax(1), 0)
    span = np.stack([meta["year0"] + first // 12, meta["year0"] + last // 12], 1)
    c["stations_with_a_climatology_month"] = int(okcm.any(1).sum())
    c["anomaly_station_months"] = int(PA.sum())
    c["stations_with_anomalies"] = int(PA.any(1).sum())
    pairs, ovn = overlap_pairs(PA)
    c["pairs_overlap_ge_min"] = len(pairs)
    Lmax = M // 12
    P = len(pairs)
    tau = np.empty((P, Lmax), np.float32)
    nn = np.empty((P, Lmax), np.int16)
    L = np.empty(P, np.int16)
    A = np.ascontiguousarray(A, np.float32)
    lib.pair_tau(ptr(A, ctypes.c_float), M, ptr(pairs, ctypes.c_int32), P, Lmax,
                 ptr(tau, ctypes.c_float), ptr(nn, ctypes.c_int16),
                 ptr(L, ctypes.c_int16))
    tau0 = tau[:, 0].astype(np.float64)
    null = tau[:, 1:].astype(np.float64)
    valid = (nn[:, 1:] >= MIN_NULL_OVERLAP) & np.isfinite(null)
    p, nvalid = shift_p(tau0, null, valid)
    dec = (nvalid >= MIN_SHIFTS) & np.isfinite(tau0)
    beyond = dec & (p <= ALPHA)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        nullv = np.where(valid, null, np.nan)
        mu = np.nanmean(nullv, axis=1)
        sd = np.nanstd(nullv, axis=1, ddof=1)
    del nullv
    c["pairs_decidable"] = int(dec.sum())
    c["pairs_too_thin_for_null"] = int((~dec).sum())
    c["pairs_beyond_chance"] = int(beyond.sum())
    c["stations_in_decidable_pairs"] = int(len(np.unique(pairs[dec])))
    c["overlap_months_decidable_median"] = r(np.median(ovn[dec]), 1) if dec.any() else None
    c["window_years_decidable_median"] = r(np.median(L[dec]), 1) if dec.any() else None
    c["valid_shifts_decidable_median"] = r(np.median(nvalid[dec]), 1) if dec.any() else None
    c["null_tau_mean_decidable"] = r(np.nanmean(np.where(valid, null, np.nan)[dec])) if dec.any() else None

    lat = np.array([s["lat"] for s in meta["stations"]])
    lon = np.array([s["lon"] for s in meta["stations"]])
    wb = np.array(ov["waterbody_index"])
    i, j = pairs[:, 0], pairs[:, 1]
    dist = haversine(lat[i], lon[i], lat[j], lon[j])
    binx = bin_of(dist)
    wi, wj = wb[i], wb[j]
    assigned = (wi >= 0) & (wj >= 0)
    same = assigned & (wi == wj)
    st_dec = np.unique(pairs[dec])
    c["stations_in_decidable_pairs_assigned_to_a_waterbody"] = int((wb[st_dec] >= 0).sum())
    c["waterbodies_among_decidable_stations"] = int(len(set(wb[st_dec][wb[st_dec] >= 0].tolist())))
    c["decidable_pairs_both_assigned"] = int((dec & assigned).sum())
    c["decidable_pairs_same_waterbody"] = int((dec & same).sum())
    c["decidable_pairs_colocated_0km"] = int((dec & (dist < 0.05)).sum())

    by_distance = []
    for b in range(len(BINS) - 1):
        m = dec & (binx == b)
        by_distance.append({"bin": bin_label(b), "pairs": int(m.sum()),
                            "beyond_chance": int((m & beyond).sum()),
                            "share_beyond": r((m & beyond).sum() / m.sum()) if m.any() else None,
                            "median_tau": r(np.median(tau0[m])) if m.any() else None})
    near = dec & (dist < NEAR_KM)
    far = dec & (dist >= NEAR_KM)
    near_far = {
        "near_km_cut": NEAR_KM,
        "near_pairs": int(near.sum()), "far_pairs": int(far.sum()),
        "near_and_co_moving": int((near & beyond).sum()),
        "far_and_co_moving": int((far & beyond).sum()),
        "near_not_co_moving": int((near & ~beyond).sum()),
        "far_not_co_moving": int((far & ~beyond).sum()),
        "share_near_co_moving": r((near & beyond).sum() / near.sum()) if near.any() else None,
        "share_far_co_moving": r((far & beyond).sum() / far.sum()) if far.any() else None,
        "near_pairs_same_wb": int((near & same).sum()),
        "near_pairs_diff_wb": int((near & assigned & ~same).sum()),
        "near_not_co_moving_same_wb": int((near & ~beyond & same).sum()),
        "near_not_co_moving_diff_wb": int((near & ~beyond & assigned & ~same).sum()),
    }
    wva = {
        "share_beyond_chance": compare(binx, same, assigned, dec,
                                       beyond.astype(float), wi, wj, "share", dist),
        "mean_tau": compare(binx, same, assigned, dec, tau0, wi, wj, "tau", dist),
    }
    ids = [s["id"] for s in meta["stations"]]
    areas = ov["areas"]
    graph = graph_part(st_dec, ids, lat, lon, wb, areas, names, pairs[dec],
                       beyond[dec], tau0[dec], dist[dec], same[dec], assigned[dec],
                       span)
    res = {"layer": layer,
           "label": vmeta["label"], "unit": vmeta["unit"], "depth": vmeta["depth"],
           "counts": c, "by_distance": by_distance, "near_far": near_far,
           "within_vs_across_matched_distance": wva, "graph": graph}
    if layer == "all":
        edges = [[ids[int(a)], ids[int(b)], r(d, 2), r(t), r(pp)]
                 for (a, b), d, t, pp in zip(pairs[beyond], dist[beyond],
                                             tau0[beyond], p[beyond])]
        res["edges_beyond_chance"] = {"columns": ["station_a", "station_b", "km",
                                                  "tau", "p_shift"], "rows": edges}
    out_counts[key] = c
    state = {"X": X, "A": A, "PA": PA, "pairs": pairs, "dec": dec, "beyond": beyond,
             "p": p, "tau0": tau0, "nvalid": nvalid, "mu": mu, "sd": sd,
             "dist": dist, "binx": binx, "wi": wi, "wj": wj, "same": same,
             "assigned": assigned}
    return res, X, (lat, lon, wb), state


def analyse_events(lib, X, meta, geo, thr):
    M = meta["months"]
    lat, lon, wb = geo
    PX = ~np.isnan(X)
    pairs, ovn = overlap_pairs(PX)
    Lmax = M // 12
    P = len(pairs)
    both = np.empty((P, Lmax), np.int16)
    either = np.empty((P, Lmax), np.int16)
    nn = np.empty((P, Lmax), np.int16)
    L = np.empty(P, np.int16)
    X = np.ascontiguousarray(X, np.float32)
    lib.pair_events(ptr(X, ctypes.c_float), M, ptr(pairs, ctypes.c_int32), P, Lmax,
                    ctypes.c_float(thr), ptr(both, ctypes.c_int16),
                    ptr(either, ctypes.c_int16), ptr(nn, ctypes.c_int16),
                    ptr(L, ctypes.c_int16))
    b0, e0 = both[:, 0].astype(float), either[:, 0].astype(float)
    assessed = e0 >= MIN_EVENT_MONTHS
    with np.errstate(invalid="ignore", divide="ignore"):
        J = np.where(either > 0, both / np.maximum(either, 1), np.nan)
    J0 = J[:, 0]
    valid = (nn[:, 1:] >= MIN_NULL_OVERLAP) & (either[:, 1:] > 0)
    p, nvalid = shift_p(np.nan_to_num(J0, nan=-1), np.nan_to_num(J[:, 1:], nan=-1),
                        valid)
    dec = assessed & (nvalid >= MIN_SHIFTS)
    beyond = dec & (p <= ALPHA)
    i, j = pairs[:, 0], pairs[:, 1]
    dist = haversine(lat[i], lon[i], lat[j], lon[j])
    binx = bin_of(dist)
    wi, wj = wb[i], wb[j]
    assigned = (wi >= 0) & (wj >= 0)
    same = assigned & (wi == wj)
    rows = []
    for bb in range(len(BINS) - 1):
        m = dec & (binx == bb)
        rows.append({"bin": bin_label(bb), "pairs": int(m.sum()),
                     "beyond_chance": int((m & beyond).sum()),
                     "months_both": int(b0[m].sum()), "months_either": int(e0[m].sum()),
                     "pooled_both_over_either": r(b0[m].sum() / e0[m].sum()) if e0[m].sum() else None})
    near, far = dec & (dist < NEAR_KM), dec & (dist >= NEAR_KM)
    return {
        "threshold_mg_l": thr,
        "counts": {"pairs_raw_overlap_ge_min": P,
                   "pairs_with_ge_min_event_months": int(assessed.sum()),
                   "pairs_decidable": int(dec.sum()),
                   "pairs_beyond_chance": int(beyond.sum()),
                   "stations_in_decidable_pairs": int(len(np.unique(pairs[dec]))),
                   "decidable_pairs_both_assigned": int((dec & assigned).sum()),
                   "decidable_pairs_same_waterbody": int((dec & same).sum())},
        "near_far": {"near_pairs": int(near.sum()), "far_pairs": int(far.sum()),
                     "near_and_co_occurring": int((near & beyond).sum()),
                     "far_and_co_occurring": int((far & beyond).sum()),
                     "share_near": r((near & beyond).sum() / near.sum()) if near.any() else None,
                     "share_far": r((far & beyond).sum() / far.sum()) if far.any() else None},
        "by_distance": rows,
        "within_vs_across_matched_distance": {
            "share_beyond_chance": compare(binx, same, assigned, dec,
                                           beyond.astype(float), wi, wj, "share",
                                           dist),
            "both_over_either": compare(binx, same, assigned, dec,
                                        np.nan_to_num(J0), wi, wj, "jaccard", dist),
        },
    }


def sampling_days(meta):
    """Every (station, month, day) whose cast fed a bed oxygen or salinity value.

    Streams the CTD extract one line at a time and replicates stations_series.flush,
    so a date is attached to exactly the station-months the panel holds. Peak memory:
    one cast's rows plus nine bytes per cast kept. Cached in $TMPDIR by the
    extract's size and mtime so reruns skip the pass.
    """
    import gzip
    from cube import mon
    from formats import num
    from series import WANT, uq
    stt = os.stat(CTD)
    cache = os.path.join(tempfile.gettempdir(),
                         f"synchrony_days_{int(stt.st_mtime)}_{stt.st_size}.npz")
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=False)
        out = {k: z[k] for k in ("st", "mo", "day", "fl")}
        out["_counts"] = json.loads(str(z["counts"]))
        return out
    sidx = {s["id"]: i for i, s in enumerate(meta["stations"])}
    ast, amo, aday, afl = (array.array("H"), array.array("H"), array.array("i"),
                           array.array("B"))
    n = {"casts": 0, "casts_panel_station": 0,
                               "casts_with_bed_oxy_or_sal": 0, "bad_dates": 0,
                               "short_lines": 0, "reopened_casts": 0}
    other_stations = set()
    closed = set()
    cur, rows = None, []

    def flush():
        if not rows or cur is None or cur[2] is None:
            return
        k = sidx.get(cur[0])
        if k is None:
            other_stations.add(cur[0])
            return
        n["casts_panel_station"] += 1
        lo = min(d for d, _ in rows)
        hi = max(d for d, _ in rows)
        cut = hi - (hi - lo) * 0.25
        fl = 0
        for d, par in rows:
            if d >= cut:
                fl |= BED_PARAM.get(par, 0)
        if not fl:
            return
        try:
            dt = cur[1]
            day = datetime.date(int(dt[:4]), int(dt[4:6]), int(dt[6:8])).toordinal()
        except ValueError:
            n["bad_dates"] += 1
            return
        n["casts_with_bed_oxy_or_sal"] += 1
        ast.append(k)
        amo.append(cur[2])
        aday.append(day)
        afl.append(fl)

    with gzip.open(CTD, "rt", encoding="iso-8859-1") as fh:
        hdr = fh.readline().rstrip("\r\n").split(";")
        ix = {c: i for i, c in enumerate(hdr)}
        nc = len(hdr)
        i_st, i_dat, i_par = ix["ObservationsStedNr"], ix["Dato"], ix["Parameter"]
        i_kr, i_or, i_d = ix["KorrigeretResultat"], ix["OriginalResultat"], ix["Dybde (m)"]
        for line in fh:
            f = line.rstrip("\r\n").split(";")
            if len(f) != nc:
                n["short_lines"] += 1
                continue
            st, dat = uq(f[i_st]), uq(f[i_dat])
            if cur is None or (st, dat) != (cur[0], cur[1]):
                flush()
                rows = []
                if (st, dat) in closed:
                    n["reopened_casts"] += 1
                closed.add((st, dat))
                cur = (st, dat, mon(dat))
                n["casts"] += 1
            if cur[2] is None:
                continue
            par = uq(f[i_par])
            if par not in WANT:
                continue
            v = num(f[i_kr])
            if v is None:
                v = num(f[i_or])
            d = num(f[i_d])
            if v is not None and d is not None:
                rows.append((d, par))
        flush()
    n["ctd_stations_not_in_panel"] = len(other_stations)
    out = {"st": np.frombuffer(ast, np.uint16).copy(),
           "mo": np.frombuffer(amo, np.uint16).copy(),
           "day": np.frombuffer(aday, np.int32).copy(),
           "fl": np.frombuffer(afl, np.uint8).copy()}
    np.savez(cache, counts=json.dumps(n), **out)
    out["_counts"] = n
    log(f"  sampling days: {n}")
    return out


def day_index(days, key, S, M):
    """First day and day count per station-month, plus the few with several days."""
    m = (days["fl"] & BED_BIT[key]) > 0
    code = days["st"][m].astype(np.int64) * M + days["mo"][m]
    dd = days["day"][m]
    o = np.lexsort((dd, code))
    code, dd = code[o], dd[o]
    keep = np.ones(len(code), bool)
    keep[1:] = (code[1:] != code[:-1]) | (dd[1:] != dd[:-1])
    code, dd = code[keep], dd[keep]
    first = np.full(S * M, -1, np.int32)
    nday = np.zeros(S * M, np.int16)
    uniq, start, cnt = np.unique(code, return_index=True, return_counts=True)
    first[uniq] = dd[start]
    nday[uniq] = cnt
    multi = {int(u): dd[s:s + c] for u, s, c in zip(uniq, start, cnt) if c > 1}
    return first.reshape(S, M), nday.reshape(S, M), multi


def pair_gaps(i, j, months, first, nday, multi, M):
    """Smallest day difference between the two stations' casts, per month; -1 unknown."""
    g = np.abs(first[i, months].astype(np.int64) - first[j, months])
    miss = (nday[i, months] == 0) | (nday[j, months] == 0)
    g[miss] = -1
    for t in np.nonzero(((nday[i, months] > 1) | (nday[j, months] > 1)) & ~miss)[0]:
        m = int(months[t])
        da = multi.get(i * M + m, first[i, m:m + 1])
        db = multi.get(j * M + m, first[j, m:m + 1])
        g[t] = int(np.abs(da[:, None].astype(np.int64) - db[None, :]).min())
    return g.astype(np.int32)


def near_far_shares(flag, keep, dist):
    near, far = keep & (dist < NEAR_KM), keep & (dist >= NEAR_KM)
    return {"near_pairs": int(near.sum()), "far_pairs": int(far.sum()),
            "near_beyond": int((near & flag).sum()), "far_beyond": int((far & flag).sum()),
            "share_near": r((near & flag).sum() / near.sum()) if near.any() else None,
            "share_far": r((far & flag).sum() / far.sum()) if far.any() else None}


def robustness(lib, key, meta, st, days):
    S, M = len(meta["stations"]), meta["months"]
    Lmax = M // 12
    first, nday, multi = day_index(days, key, S, M)
    PX = ~np.isnan(st["X"])
    have = nday > 0
    A, PA, pairs = st["A"], st["PA"], st["pairs"]
    dec, beyond, tau0 = st["dec"], st["beyond"], st["tau0"]
    dist, binx, wi, wj = st["dist"], st["binx"], st["wi"], st["wj"]
    same, assigned = st["same"], st["assigned"]
    recovery = {
        "panel_station_months": int(PX.sum()),
        "panel_station_months_with_a_recovered_day": int((PX & have).sum()),
        "panel_stations": int(PX.any(1).sum()),
        "panel_stations_with_a_recovered_day": int((PX & have).any(1).sum()),
        "panel_station_months_with_2plus_days": int((PX & (nday > 1)).sum()),
        "recovered_station_months_not_in_panel": int((~PX & have).sum()),
    }
    P = len(pairs)
    gl = []
    n_known = np.zeros(P, np.int32)
    n_close = {G: np.zeros(P, np.int32) for G in DIFF_DAY_GAPS}
    for q in range(P):
        i, j = int(pairs[q, 0]), int(pairs[q, 1])
        months = np.nonzero(PA[i] & PA[j])[0]
        g = pair_gaps(i, j, months, first, nday, multi, M)
        gl.append((months, g))
        n_known[q] = int((g >= 0).sum())
        for G in DIFF_DAY_GAPS:
            n_close[G][q] = int(((g >= 0) & (g < G)).sum())

    # (b) how common is same-day sampling, within vs across, on the tested pairs
    k = dec & assigned
    how = {"pairs": "decidable pairs of the main (all-months) analysis",
           "pair_months_with_known_days": int(n_known[dec].sum()),
           "pair_months_unknown_day": int(sum(len(gl[q][1]) for q in np.nonzero(dec)[0])
                                          - n_known[dec].sum())}
    for G in DIFF_DAY_GAPS:
        lab = "same_day" if G == 1 else f"within_{G - 1}_days"
        frac = np.where(n_known > 0, n_close[G] / np.maximum(n_known, 1), 0.0)
        blk = {}
        for name, m in (("within_same_waterbody", k & same),
                        ("across_waterbodies", k & ~same)):
            blk[name] = {"pairs": int(m.sum()),
                         "pair_months": int(n_known[m].sum()),
                         f"{lab}_pair_months": int(n_close[G][m].sum()),
                         f"share_{lab}": r(n_close[G][m].sum() / n_known[m].sum())
                         if n_known[m].sum() else None,
                         f"pairs_with_any_{lab}_month": int((m & (n_close[G] > 0)).sum())}
        blk["matched_distance_per_pair_share"] = compare(
            binx, same, assigned, dec, frac, wi, wj, "share", dist)
        how[lab] = blk

    # (a) the deciding test on months the two stations were sampled apart
    diff = {}
    for G in DIFF_DAY_GAPS:
        tau = np.empty((P, Lmax), np.float32)
        nn = np.empty((P, Lmax), np.int16)
        L = np.empty(P, np.int16)
        CH = 4000
        for c0 in range(0, P, CH):
            c1 = min(P, c0 + CH)
            ext = np.empty((S + c1 - c0, M), np.float32)
            ext[:S] = A
            pc = np.empty((c1 - c0, 2), np.int32)
            for kk, q in enumerate(range(c0, c1)):
                i, j = int(pairs[q, 0]), int(pairs[q, 1])
                months, g = gl[q]
                row = ext[S + kk]
                row[:] = A[i]
                row[months[g < G]] = np.nan     # g < G includes unknown (-1)
                pc[kk] = (S + kk, j)
            t_ = np.empty((c1 - c0, Lmax), np.float32)
            n_ = np.empty((c1 - c0, Lmax), np.int16)
            l_ = np.empty(c1 - c0, np.int16)
            lib.pair_tau(ptr(ext, ctypes.c_float), M, ptr(pc, ctypes.c_int32),
                         c1 - c0, Lmax, ptr(t_, ctypes.c_float),
                         ptr(n_, ctypes.c_int16), ptr(l_, ctypes.c_int16))
            tau[c0:c1], nn[c0:c1], L[c0:c1] = t_, n_, l_
        t0 = tau[:, 0].astype(np.float64)
        null = tau[:, 1:].astype(np.float64)
        valid = (nn[:, 1:] >= MIN_NULL_OVERLAP) & np.isfinite(null)
        p, nvalid = shift_p(t0, null, valid)
        d2 = (nn[:, 0] >= MIN_OVERLAP) & (nvalid >= MIN_SHIFTS) & np.isfinite(t0)
        b2 = d2 & (p <= ALPHA)
        both = d2 & dec
        diff[f"gap_ge_{G}_days"] = {
            "counts": {"pairs_start": P, "pairs_decidable": int(d2.sum()),
                       "pairs_beyond_chance": int(b2.sum()),
                       "decidable_pairs_same_waterbody": int((d2 & same).sum()),
                       "decidable_pairs_both_assigned": int((d2 & assigned).sum()),
                       "decidable_in_both_analyses": int(both.sum()),
                       "decidable_in_both_same_waterbody": int((both & same).sum()),
                       "overlap_months_decidable_median":
                           r(np.median(nn[d2, 0]), 1) if d2.any() else None},
            "near_far": near_far_shares(b2, d2, dist),
            "within_vs_across_matched_distance": {
                "share_beyond_chance": compare(binx, same, assigned, d2,
                                               b2.astype(float), wi, wj, "share", dist),
                "mean_tau": compare(binx, same, assigned, d2, t0, wi, wj, "tau", dist)},
            "same_pairs_all_months": {
                "what": "the pairs decidable in both analyses, scored on all months, "
                        "so any change is not a change of pair set",
                "near_far": near_far_shares(beyond, both, dist),
                "share_beyond_chance": compare(binx, same, assigned, both,
                                               beyond.astype(float), wi, wj, "share",
                                               dist),
                "mean_tau": compare(binx, same, assigned, both, tau0, wi, wj, "tau",
                                    dist)},
            "same_pairs_these_months": {
                "share_beyond_chance": compare(binx, same, assigned, both,
                                               b2.astype(float), wi, wj, "share", dist),
                "mean_tau": compare(binx, same, assigned, both, t0, wi, wj, "tau",
                                    dist)},
        }
        log(f"      gap >= {G} d: {int(d2.sum()):,} decidable, {int(b2.sum()):,} beyond")
    return {"date_recovery": recovery, "how_common": how, "different_day": diff}


def bh(p, q):
    m = len(p)
    rej = np.zeros(m, bool)
    if not m:
        return rej
    o = np.argsort(p, kind="stable")
    ok = np.nonzero(p[o] <= q * np.arange(1, m + 1) / m)[0]
    if len(ok):
        rej[o[:ok[-1] + 1]] = True
    return rej


def fdr_part(st):
    dec, p, tau0 = st["dec"], st["p"], st["tau0"]
    mu, sd, nvalid = st["mu"], st["sd"], st["nvalid"]
    dist, binx, wi, wj = st["dist"], st["binx"], st["wi"], st["wj"]
    same, assigned = st["same"], st["assigned"]
    P = len(p)
    with np.errstate(invalid="ignore", divide="ignore"):
        z = (tau0 - mu) / sd
    pn = np.array([0.5 * math.erfc(x / math.sqrt(2)) if np.isfinite(x) else 1.0
                   for x in z])
    out = {"family": "all decidable pairs of the variable, one family",
           "q": FDR_Q, "pairs_in_family": int(dec.sum()),
           "min_attainable_shift_p": r(1 / (1 + nvalid[dec].max())) if dec.any() else None,
           "uncorrected_beyond_chance": int(st["beyond"].sum())}
    for name, pv in (("shift_p", p), ("normal_approx_p", pn)):
        rej = np.zeros(P, bool)
        rej[dec] = bh(pv[dec], FDR_Q)
        blk = {"pairs_passing": int(rej.sum()),
               "largest_p_passing": r(pv[rej].max(), 6) if rej.any() else None,
               "near_far": near_far_shares(rej, dec, dist),
               "within_vs_across_matched_distance":
                   compare(binx, same, assigned, dec, rej.astype(float), wi, wj,
                           "share", dist)}
        if name == "normal_approx_p":
            blk["calibration_uncorrected_p_le_alpha"] = int((dec & (pn <= ALPHA)).sum())
            blk["calibration_agree_with_shift_rule"] = int(
                (dec & ((pn <= ALPHA) == st["beyond"])).sum())
        out[name] = blk
    return out


def main():
    lib = kernel()
    meta, raw, ov = load()
    ad = json.load(open(os.path.join(ROOT, "data", "derived", "areas.json")))
    names = {k: v.get("name") for k, v in ad["areas"].items()}
    out = {
        "_what": "Co-movement of station anomalies against distance and against the "
                 "official water bodies. Levels are never compared; only whether two "
                 "stations are unusual in the same months.",
        "_status": "Water-body membership is the overlay, a model assumption. No "
                   "random or size-matched baskets of stations are used anywhere; "
                   "chance is judged by shifting one station's series in time.",
        "_generated_by": "scripts/synchrony.py",
        "inputs": {
            "panel": "docs/data/areas/stations_series.json + .bin (monthly median per "
                     "station-month; 'bed' = readings in the deepest quarter of each "
                     "cast's sampled depth range, so a single-depth cast counts as "
                     "both bed and surface)",
            "stations_in_panel": len(meta["stations"]),
            "months_in_panel": meta["months"], "year0": meta["year0"],
            "waterbody_assignment": "docs/data/areas/station_waterbody_overlay.json: "
                                    "point-in-polygon of the panel's own station "
                                    "positions against the VP3 water bodies; keyed by "
                                    "the panel's own station ids (identical list and "
                                    "order, asserted), so no station-number join is "
                                    "involved",
            "stations_inside_a_waterbody": ov["n_inside"],
            "waterbodies": len(ov["areas"]),
        },
        "construction": {
            "variables": VARS,
            "plausibility_drop_above": PLAUSIBLE_MAX,
            "anomaly_rule": "station-month value minus the station's median for that "
                            "calendar month; calendar months with fewer than "
                            "min_years_per_calendar_month years at the station are "
                            "dropped",
            "min_years_per_calendar_month": MIN_YEARS,
            "co_movement": "Kendall tau-b between the two anomaly series on months both "
                           "have an anomaly",
            "min_overlap_months": MIN_OVERLAP,
            "shift_null": "one station's series rotated by k whole years (k = 1..L-1) "
                          "inside the pair's joint window, Jan of the first to Dec of "
                          "the last shared year (L years); a shift counts if it leaves "
                          "at least min_null_overlap_months shared months",
            "min_null_overlap_months": MIN_NULL_OVERLAP,
            "min_valid_shifts": MIN_SHIFTS,
            "p_value": "(1 + number of valid shifts with tau >= observed) / (1 + "
                       "number of valid shifts), one-sided",
            "alpha": ALPHA,
            "multiple_testing": "none per pair; the pair counts are shares against a "
                                "per-pair 5% false-positive rate",
            "events": "bed oxygen below each threshold in a station-month (raw values, "
                      "not anomalies), on months both stations measured; both/either "
                      "per pair; same whole-year shift null (which keeps calendar "
                      "months, so seasonal co-occurrence is in the null)",
            "event_thresholds_mg_l": EVENT_THRESHOLDS,
            "event_thresholds_are": "conventions (4 and 2 mg/l as commonly used "
                                    "reporting lines), not measured tolerances",
            "min_event_months_either": MIN_EVENT_MONTHS,
            "distance": "great-circle (haversine, R = 6371 km) between station "
                        "positions; land is ignored",
            "distance_bins_km": [b for b in BINS[:-1]] + ["inf"],
            "near_km": NEAR_KM,
            "within_vs_across": "per distance bin, pairs with both stations in the "
                                "same water body against pairs in different ones "
                                "(stations outside every polygon excluded); pooled "
                                "difference = mean over bins of (within - across) "
                                "weighted by within-pair count, over bins with at "
                                "least min_pairs_per_cell in both cells; uncertainty "
                                "by leave-one-water-body-out jackknife",
            "min_pairs_per_cell": MIN_CELL,
            "graph": "nodes = stations in at least one decidable pair; edges = pairs "
                     "beyond chance; groups = connected components, and Louvain "
                     "communities (weight = tau)",
            "knn_for_contiguity": KNN,
            "fine_bins_km": [b for b in FINE_BINS[:-1]] + ["inf"],
            "fine_bins_are": "a check on distance left over inside the main bins; "
                             "same pooling rule",
            "within_year_layer": "the same analysis after also subtracting each "
                                 "station's own median anomaly for each year (years "
                                 "with fewer than min_months_per_year anomaly months "
                                 "dropped), so shared trends, steps and "
                                 "year-to-year swings are removed and only "
                                 "month-scale co-movement remains; reported under "
                                 "variables.<key>.within_year",
            "min_months_per_year": MIN_YEAR_MONTHS,
            "group_years": "median first and last year of each group's stations' "
                           "anomaly records, to see whether groups sort by era",
            "sampling_days": "dates recovered by streaming data/raw/oda/ctd.csv.gz "
                             "with the panel's own cast logic (cast = station + "
                             "Dato; bed = depth >= deepest - 25% of the cast's "
                             "depth range over the panel's parameters; station "
                             "key = ObservationsStedNr, the panel's own id); a "
                             "cast gives its date to a station-month for a "
                             "variable if that variable has a bed reading in it",
            "pair_month_gap": "for a pair and a month, the smallest day difference "
                              "between any cast of one station and any cast of the "
                              "other that fed the monthly value; 0 = same day",
            "different_day_rule": "the deciding test rerun after removing, pair by "
                                  "pair, the months whose gap is below the stated "
                                  "number of days (and months with no recovered "
                                  "date); the same shift null, the same minimum "
                                  "overlap (applied after removal) and the same "
                                  "minimum shifts",
            "different_day_min_gap_days": DIFF_DAY_GAPS,
            "robustness_variables": ROBUST_VARS,
            "fdr": "Benjamini-Hochberg at q over all decidable pairs of a variable, "
                   "on (a) the shift-null p itself and (b) a normal approximation "
                   "z = (tau - mean of the valid shifted taus) / their sd, "
                   "p = upper tail; (a) cannot go below 1 / (1 + number of shifts), "
                   "so (b) is given as well with a calibration count",
            "fdr_q": FDR_Q,
        },
        "variables": {},
    }
    days = sampling_days(meta)
    out["inputs"]["ctd_sampling_days"] = days["_counts"]
    counts = {}
    for key in VARS:
        log(f"  {key}")
        res, X, geo, st = analyse_tau(lib, key, meta, raw, ov, names, counts)
        res["within_year"] = analyse_tau(lib, key, meta, raw, ov, names, {},
                                         layer="within_year")[0]
        if key in ROBUST_VARS:
            log("    same-day sampling and FDR")
            res["same_day_sampling"] = robustness(lib, key, meta, st, days)
            res["fdr"] = fdr_part(st)
        if key == "oxy_bed":
            res["events"] = [analyse_events(lib, X, meta, geo, t)
                             for t in EVENT_THRESHOLDS]
        out["variables"][key] = res
        c = res["counts"]
        log(f"    {c['pairs_decidable']:,} decidable pairs, "
            f"{c['pairs_beyond_chance']:,} beyond chance")
    write_json(os.path.join(ROOT, "data", "derived", "synchrony.json"), out)
    log("  wrote data/derived/synchrony.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
