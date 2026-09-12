#!/usr/bin/env python3
"""Livestock baskets: monitoring stations grouped by the livestock density of the
land that drains to their water body, compared against random baskets.

NAIVE BY CONSTRUCTION. CHR sites are herd registrations, not where manure is
spread; DE is a regulatory unit; livestock is 2024 while the stations span
decades; the catchment -> water body link is built here by coastal adjacency.

Personal/company data rule: CHR records are read and used in memory only. Every
output is an area total (per catchment, per water body, per basket). No CHR
number, CVR number or single farm is written. A catchment or species cell with
fewer than SUPPRESS_BELOW contributing herd registrations has its livestock
figures suppressed in the output (it would describe one or two farms).

Peak memory: the marine layer as a JSON object graph (~320 MB measured) while it
is converted to numpy, then numpy arrays of boundary points (a few million
float64) and the station-month panel (~0.7 M records). Null draws are chunked.
"""
import collections
import csv
import gzip
import io
import json
import math
import os
import sys
import time

import numpy as np

ROOT = "/home/user/projects/copenhagen-waterways"
# intermediates (the CTD depth/repeat pass, about 13 minutes) are cached outside the repo
SCR = os.path.join(os.environ.get("TMPDIR", "/tmp"), "copenhagen-livestock")
CHR = "/home/user/projects/danish-livestock/data/chr_2024.json"
CATCH = os.path.join(ROOT, "data/raw/national/vp3_2e2025_kystvand_opland_afg.geojson")
MARINE = os.path.join(ROOT, "data/raw/national/marin_overordnet.geojson")
OVERLAY = os.path.join(ROOT, "docs/data/areas/station_waterbody_overlay.json")
SERIES = os.path.join(ROOT, "docs/data/areas/stations_series.json")
SERIESBIN = os.path.join(ROOT, "docs/data/areas/stations_series.bin")
MAAL = os.path.join(ROOT, "data/raw/oda/maaledybde.csv.gz")
CTDX = os.path.join(SCR, "ctd_repeat_depth.json")
OUT = os.path.join(ROOT, "data/derived/livestock_baskets.json")

sys.path.insert(0, os.path.join(ROOT, "scripts"))
from formats import num  # noqa: E402

R = 6371008.8
LAT0 = math.radians(56.0)
RNG = np.random.default_rng(20260912)

# ---- construction choices (all stated in the output) ----
SUMMER = (6, 7, 8, 9)
MIN_SUMMER_MONTHS = 4
NEAR_ABSENT_FRACTION = 0.2
SAL_CUT = 20.0
DEPTH_CUT = 10.0
DENSIFY_M = 50.0
CELL_M = 250.0
CELL_M_ALTS = (100.0, 250.0, 500.0)
CLEAN_SHARE = 0.8
MIN_TOUCH_POINTS = 5
SUPPRESS_BELOW = 3
PERIOD2_FROM = 2010
N_NULL = 10000
N_NULL_STRATA = 5000
N_AUC_NULL = 1000
N_PROFILE = 1000
N_INTERCH = 500
Q = (0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95)
CATTLE, PIGS = 12, 15
VARS = ("oxy_bed", "oxysat_bed", "fluo")
T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:7.1f}s] {msg}", flush=True)


def r4(x):
    if x is None:
        return None
    x = float(x)
    if math.isnan(x):
        return None
    return round(x, 4)


def qdict(v):
    v = np.asarray(v, dtype=np.float64)
    v = v[~np.isnan(v)]
    if len(v) == 0:
        return {"n": 0}
    qs = np.quantile(v, Q)
    d = {"n": int(len(v))}
    for q, x in zip(Q, qs):
        d[f"q{int(round(q * 100)):02d}"] = r4(x)
    d["min"], d["max"] = r4(v.min()), r4(v.max())
    d["iqr"] = r4(qs[4] - qs[2])
    d["q90_minus_q10"] = r4(qs[5] - qs[1])
    return d


def band_summary(a):
    a = np.asarray(a, dtype=np.float64)
    a = a[~np.isnan(a)]
    if len(a) == 0:
        return {"n": 0}
    return {"n": int(len(a)), "min": r4(a.min()), "q005": r4(np.quantile(a, 0.005)),
            "q025": r4(np.quantile(a, 0.025)), "q50": r4(np.quantile(a, 0.5)),
            "q975": r4(np.quantile(a, 0.975)), "q995": r4(np.quantile(a, 0.995)),
            "max": r4(a.max())}


# ---------------------------------------------------------------- geometry
def feature_polys(geom):
    parts = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return [[np.asarray(r, dtype=np.float64)[:, :2] for r in p] for p in parts]


def local_xy(lon, lat):
    return R * np.radians(lon) * math.cos(LAT0), R * np.radians(lat)


def ring_area_km2(a):
    lam, phi = np.radians(a[:, 0]), np.radians(a[:, 1])
    x, y = R * lam * np.cos(phi), R * phi          # sinusoidal: equal-area
    return abs(0.5 * np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y)) / 1e6


def poly_area_km2(polys):
    return sum(ring_area_km2(p[0]) - sum(ring_area_km2(h) for h in p[1:]) for p in polys)


def pip_many(feats, px, py, band=0.001):
    """Even-odd point in polygon for many points against many features at once,
    using latitude bands so each point meets only the edges crossing its band."""
    X1, Y1, X2, Y2, F = [], [], [], [], []
    for fi, polys in enumerate(feats):
        for p in polys:
            for a in p:
                b = np.roll(a, -1, axis=0)
                X1.append(a[:, 0]); Y1.append(a[:, 1]); X2.append(b[:, 0]); Y2.append(b[:, 1])
                F.append(np.full(len(a), fi, np.int32))
    X1, Y1, X2, Y2, F = (np.concatenate(z) for z in (X1, Y1, X2, Y2, F))
    keep = Y1 != Y2
    X1, Y1, X2, Y2, F = X1[keep], Y1[keep], X2[keep], Y2[keep], F[keep]
    y0 = min(py.min(), np.minimum(Y1, Y2).min()) - band
    blo = np.floor((np.minimum(Y1, Y2) - y0) / band).astype(np.int64)
    bhi = np.floor((np.maximum(Y1, Y2) - y0) / band).astype(np.int64)
    reps = bhi - blo + 1
    eidx = np.repeat(np.arange(len(X1)), reps)
    off = np.arange(reps.sum()) - np.repeat(np.cumsum(reps) - reps, reps)
    eb = np.repeat(blo, reps) + off
    o = np.argsort(eb, kind="stable")
    eb, eidx = eb[o], eidx[o]
    pb = np.floor((py - y0) / band).astype(np.int64)
    po = np.argsort(pb, kind="stable")
    pbs = pb[po]
    ub, ustart = np.unique(pbs, return_index=True)
    uend = np.append(ustart[1:], len(pbs))
    parity = np.zeros((len(px), len(feats)), np.uint8)
    el = np.searchsorted(eb, ub, "left")
    er = np.searchsorted(eb, ub, "right")
    for k in range(len(ub)):
        if er[k] == el[k]:
            continue
        P = po[ustart[k]:uend[k]]
        E = eidx[el[k]:er[k]]
        yy, xx = py[P][:, None], px[P][:, None]
        y1, y2, x1, x2 = Y1[E], Y2[E], X1[E], X2[E]
        cond = ((y1 > yy) != (y2 > yy)) & (xx < x1 + (yy - y1) * (x2 - x1) / (y2 - y1))
        pi, ei = np.nonzero(cond)
        np.add.at(parity, (P[pi], F[E][ei]), 1)
    inside = (parity % 2) == 1
    nhit = inside.sum(1)
    return np.where(nhit > 0, inside.argmax(1), -1), nhit


def densify(a, step):
    x, y = local_xy(a[:, 0], a[:, 1])
    x2, y2 = np.roll(x, -1), np.roll(y, -1)
    L = np.hypot(x2 - x, y2 - y)
    n = np.maximum(1, np.ceil(L / step)).astype(np.int64)
    idx = np.repeat(np.arange(len(x)), n)
    t = (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)) / np.repeat(n, n)
    return x[idx] + t * (x2 - x)[idx], y[idx] + t * (y2 - y)[idx]


def boundary_points(polys, step):
    xs, ys = [], []
    for p in polys:
        for a in p:
            x, y = densify(a, step)
            xs.append(x); ys.append(y)
    return np.concatenate(xs), np.concatenate(ys)


def cellkey(x, y, cell):
    return np.floor(x / cell).astype(np.int64) * 10_000_000 + np.floor(y / cell).astype(np.int64)


def touch_counts(cx, cy, mkeys_sorted, mids_sorted, cell, nmar):
    """For boundary points of one catchment: how many points have each marine body
    within their 3x3 cell neighbourhood (reach between one cell and ~2.8 cells)."""
    pairs_p, pairs_m = [], []
    ix = np.floor(cx / cell).astype(np.int64)
    iy = np.floor(cy / cell).astype(np.int64)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            k = (ix + dx) * 10_000_000 + (iy + dy)
            lo = np.searchsorted(mkeys_sorted, k, "left")
            hi = np.searchsorted(mkeys_sorted, k, "right")
            cnt = hi - lo
            for j in range(int(cnt.max()) if len(cnt) else 0):
                m = cnt > j
                pairs_p.append(np.nonzero(m)[0])
                pairs_m.append(mids_sorted[lo[m] + j])
    if not pairs_p:
        return np.zeros(nmar, np.int64)
    pp = np.concatenate(pairs_p); mm = np.concatenate(pairs_m)
    u = np.unique(pp.astype(np.int64) * 1000 + mm)
    return np.bincount((u % 1000).astype(np.int64), minlength=nmar)


def norm_name(s):
    s = s.lower().replace("å", "aa")        # Århus / Aarhus: one letter, two spellings
    for ch in ",.-()/":
        s = s.replace(ch, " ")
    return " ".join(s.split())


# ---------------------------------------------------------------- statistics
def group_median(sidx, vals, nst, minn):
    o = np.lexsort((vals, sidx))
    s, v = sidx[o], vals[o]
    cnt = np.bincount(s, minlength=nst)
    start = np.cumsum(cnt) - cnt
    med = np.full(nst, np.nan)
    ok = cnt >= max(minn, 1)
    lo = start[ok] + (cnt[ok] - 1) // 2
    hi = start[ok] + cnt[ok] // 2
    med[ok] = 0.5 * (v[lo] + v[hi])
    return med, cnt


def cles_less(a, b):
    """P(a < b) + 0.5 P(a == b), by counting all (a, b) pairs."""
    a = np.asarray(a); b = np.sort(np.asarray(b))
    if len(a) == 0 or len(b) == 0:
        return None
    lt = len(b) - np.searchsorted(b, a, "right")
    eq = np.searchsorted(b, a, "right") - np.searchsorted(b, a, "left")
    return float((lt.sum() + 0.5 * eq.sum()) / (len(a) * len(b)))


def cles_less_batch(A, B):
    """Row-wise P(A < B) for matrices of draws x members."""
    out = np.empty(A.shape[0])
    for i in range(0, A.shape[0], 100):
        a = A[i:i + 100][:, :, None]; b = B[i:i + 100][:, None, :]
        out[i:i + 100] = ((a < b).sum((1, 2)) + 0.5 * (a == b).sum((1, 2))) / (A.shape[1] * B.shape[1])
    return out


def kendall_tau_b(x, y):
    x = np.asarray(x); y = np.asarray(y)
    n = len(x)
    if n < 3:
        return None
    sx = np.sign(x[:, None] - x[None, :]); sy = np.sign(y[:, None] - y[None, :])
    iu = np.triu_indices(n, 1)
    sx, sy = sx[iu], sy[iu]
    s = float((sx * sy).sum())
    tx = float((sx != 0).sum()); ty = float((sy != 0).sum())
    return s / math.sqrt(tx * ty) if tx and ty else None


def pair_auc(vals, labels):
    """Section 4 of the methods: of all (within-basket pair, across-basket pair)
    comparisons, the share that put the within pair closer. 0.5 = baskets tell
    nothing about closeness."""
    n = len(vals)
    iu = np.triu_indices(n, 1)
    d = np.abs(vals[iu[0]] - vals[iu[1]])
    same = labels[iu[0]] == labels[iu[1]]
    w, a = d[same], np.sort(d[~same])
    if len(w) == 0 or len(a) == 0:
        return None, int(len(w)), int(len(a))
    gt = len(a) - np.searchsorted(a, w, "right")
    eq = np.searchsorted(a, w, "right") - np.searchsorted(a, w, "left")
    return float((gt.sum() + 0.5 * eq.sum()) / (len(w) * len(a))), int(len(w)), int(len(a))


def pair_diffs(vals, groups):
    n = len(vals)
    iu = np.triu_indices(n, 1)
    d = np.abs(vals[iu[0]] - vals[iu[1]])
    same = groups[iu[0]] == groups[iu[1]]
    return d[same], d[~same]


def place(real, null):
    null = np.asarray(null, dtype=np.float64)
    null = null[~np.isnan(null)]
    if real is None or len(null) == 0:
        return {}
    ge = int((null >= real).sum()); le = int((null <= real).sum())
    absn = np.abs(null - np.median(null))
    far = int((absn >= abs(real - np.median(null))).sum())
    lo, hi = np.quantile(null, [0.025, 0.975])
    if real > null.max() or real < null.min():
        verdict = "outside the whole null range (beats the floor by a wide margin)"
    elif real > hi or real < lo:
        verdict = "outside the central 95% of the null but inside its range (beats noise, not by a wide margin)"
    else:
        verdict = "inside the central 95% of the null (does not beat the noise floor)"
    return {"real": r4(real), "null": band_summary(null), "draws": int(len(null)),
            "draws_at_or_above_real": ge, "draws_at_or_below_real": le,
            "draws_at_least_as_far_from_null_median": far, "verdict": verdict}


# ---------------------------------------------------------------- loading
def load_panel():
    meta = json.load(open(SERIES))
    buf = open(SERIESBIN, "rb").read()
    out = {}
    for v in meta["variables"]:
        n, o = v["n"], v["offset"]
        st = np.frombuffer(buf, "<u2", n, o).astype(np.int64)
        mo = np.frombuffer(buf, "<u2", n, o + 2 * n).astype(np.int64)
        val = np.frombuffer(buf, "<f4", n, o + 4 * n).astype(np.float64)
        out[v["key"]] = (st, mo, val, v)
    return meta, out


def main():
    res = {"_what": ("Monitoring stations grouped by the 2024 livestock density (CHR herd "
                     "registrations, DE) of the coastal catchments that touch their water body, "
                     "compared on long-term summer bed oxygen, bed oxygen saturation and "
                     "fluorescence, against random baskets of the same sizes. A NAIVE, immediate "
                     "estimate of a driver's effect, not an attribution."),
           "_naive": [
               "CHR sites are herd registrations (where the herd is registered), not where manure is spread.",
               "DE (dyreenheder) is a regulatory unit, not nitrogen or phosphorus.",
               "Livestock is the 2024 register; the station summers span decades (a 2010+ sensitivity is included).",
               "The catchment -> marine water body link is a construction of this script (coastal adjacency), not a code in either source.",
               "A water body's catchments are only the land that touches it directly: an outer fjord does not inherit its inner fjord's catchment here.",
               "Low-livestock land is not low-load land: urban and sewage loads are not in this grouping.",
           ],
           "_privacy": (f"CHR records were used in memory only. Outputs are area totals. Catchment or "
                        f"species cells with fewer than {SUPPRESS_BELOW} contributing herd registrations "
                        f"(DE > 0) are suppressed, and so is the density derived from them."),
           "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    # ---------------- catchments
    cj = json.load(open(CATCH))
    cats = []
    for f in cj["features"]:
        p = f["properties"]
        polys = feature_polys(f["geometry"])
        cats.append({"op_id": str(p["op_id"]), "op_navn": p["op_navn"], "areal_field": p["areal"],
                     "polys": polys, "area_km2": poly_area_km2(polys)})
    nc = len(cats)
    first = cj["features"][0]["geometry"]["coordinates"]
    while isinstance(first[0], list):
        first = first[0]
    res["sources"] = {
        "catchments": {
            "layer": "vp3_2endelig2025:vp3_2e2025_kystvand_opland_afg",
            "url": "https://wfs2-miljoegis.mim.dk/vp3_2endelig2025/ows",
            "request": ("https://wfs2-miljoegis.mim.dk/vp3_2endelig2025/ows?service=WFS&version=2.0.0"
                        "&request=GetFeature&typeNames=vp3_2endelig2025:vp3_2e2025_kystvand_opland_afg"
                        "&outputFormat=application/json&srsName=EPSG:4326"),
            "downloaded_utc": "2026-09-12T13:49:21Z", "http_status": 200, "bytes": 10563338,
            "file": "data/raw/national/vp3_2e2025_kystvand_opland_afg.geojson",
            "features": nc, "numberMatched": cj.get("numberMatched"),
            "crs_declared": cj.get("crs", {}).get("properties", {}).get("name"),
            "axis_order_checked": (f"coordinates are lon,lat (first vertex of 'Roskilde Fjord, ydre' "
                                   f"is {first[0]}, {first[1]})"),
            "op_type_values": sorted({f["properties"]["op_type"] for f in cj["features"]}),
            "areal_field_vs_geometry": None},
        "marine": {"file": "data/raw/national/marin_overordnet.geojson"},
        "livestock": {"file": "/home/user/projects/danish-livestock/data/chr_2024.json"},
        "stations": {"overlay": "docs/data/areas/station_waterbody_overlay.json",
                     "panel": "docs/data/areas/stations_series.json + .bin"},
        "depth_register": "data/raw/oda/maaledybde.csv.gz (BundDybde_m)",
        "raw_ctd_for_replicates_and_depth_fallback": "data/raw/oda/ctd.csv.gz (streamed once)"}
    del cj
    ratio = np.array([c["area_km2"] / c["areal_field"] for c in cats if c["areal_field"]])
    res["sources"]["catchments"]["areal_field_vs_geometry"] = {
        "what": "geometry area (sinusoidal equal-area, km2) / 'areal' field",
        "min": r4(ratio.min()), "median": r4(np.median(ratio)), "max": r4(ratio.max()),
        "reading": "if near 1, 'areal' is km2 and the geometry area is used throughout"}
    log(f"catchments {nc}, area ratio median {np.median(ratio):.4f}")

    # ---------------- farms -> catchments
    herds = json.load(open(CHR))
    lon = np.array([h["lon"] for h in herds], np.float64)
    lat = np.array([h["lat"] for h in herds], np.float64)
    de = np.array([h.get("DE") or 0.0 for h in herds], np.float64)
    code = np.array([h.get("DYRKODE") if h.get("DYRKODE") is not None else -1 for h in herds], np.int64)
    dupkey = collections.Counter((h.get("CHRNR"), h.get("DYRKODE")) for h in herds)
    n_dup = sum(c - 1 for c in dupkey.values() if c > 1)
    n_herd_ids = len({h.get("CHRNR") for h in herds})
    del herds, dupkey
    grp = np.where(code == CATTLE, 0, np.where(code == PIGS, 1, 2))
    fi, nhit = pip_many([c["polys"] for c in cats], lon, lat)
    log(f"farms placed: {int((fi >= 0).sum())} of {len(fi)}")
    tot = np.zeros(nc); bygrp = np.zeros((nc, 3)); nrec = np.zeros(nc, np.int64)
    ncontrib = np.zeros(nc, np.int64); ncontrib_g = np.zeros((nc, 3), np.int64)
    ins = fi >= 0
    np.add.at(tot, fi[ins], de[ins])
    np.add.at(bygrp, (fi[ins], grp[ins]), de[ins])
    np.add.at(nrec, fi[ins], 1)
    pos = ins & (de > 0)
    np.add.at(ncontrib, fi[pos], 1)
    np.add.at(ncontrib_g, (fi[pos], grp[pos]), 1)
    area = np.array([c["area_km2"] for c in cats])
    dens = tot / area
    national = float(tot.sum() / area.sum())
    res["farms"] = {
        "records": int(len(de)), "distinct_herd_registrations_CHRNR": n_herd_ids,
        "records_repeating_a_herd_and_species": int(n_dup),
        "records_with_DE_gt_0": int((de > 0).sum()), "DE_total_all_records": r4(de.sum()),
        "species_groups": {"cattle": "DYRKODE 12 (Kvæg)", "pigs": "DYRKODE 15 (Svin)",
                           "other": "every other DYRKODE (horses, sheep, goats, poultry, fish, ...)"},
        "DE_total_by_group_all_records": {g: r4(de[grp == i].sum()) for i, g in enumerate(("cattle", "pigs", "other"))},
        "records_in_a_catchment": int(ins.sum()),
        "records_in_no_catchment": int((~ins).sum()),
        "records_in_no_catchment_with_DE_gt_0": int(((~ins) & (de > 0)).sum()),
        "DE_in_no_catchment": r4(de[~ins].sum()),
        "records_in_more_than_one_catchment": int((nhit > 1).sum()),
        "DE_in_catchments": r4(tot.sum()), "catchment_area_km2": r4(area.sum()),
        "national_density_DE_per_km2": r4(national),
        "method": "point in polygon (even-odd, all rings) on WGS84 lon/lat; catchment area from the geometry (sinusoidal equal-area)"}

    # ---------------- marine layer, adjacency
    mj = json.load(open(MARINE))
    mar = []
    for f in mj["features"]:
        p = f["properties"]
        mar.append({"ov_id": p["ov_id"], "ov_navn": p["ov_navn"], "mst_id": str(p.get("mst_id")),
                    "ov_kat": p.get("ov_kat"), "polys": feature_polys(f["geometry"])})
    res["sources"]["marine"]["crs_declared"] = mj.get("crs", {}).get("properties", {}).get("name")
    res["sources"]["marine"]["features"] = len(mar)
    del mj
    nm = len(mar)
    mx, my, mid = [], [], []
    for k, m in enumerate(mar):
        x, y = boundary_points(m["polys"], DENSIFY_M)
        mx.append(x); my.append(y); mid.append(np.full(len(x), k, np.int64))
    mx, my, mid = np.concatenate(mx), np.concatenate(my), np.concatenate(mid)
    log(f"marine boundary points {len(mx):,}")
    cbx = [boundary_points(c["polys"], DENSIFY_M) for c in cats]

    link_alts = {}
    touch_main = None
    for cell in CELL_M_ALTS:
        u = np.unique(cellkey(mx, my, cell) * 1000 + mid)
        mk, mm = u // 1000, u % 1000
        touch = np.array([touch_counts(x, y, mk, mm, cell, nm) for x, y in cbx])
        if cell == CELL_M:
            touch_main = touch
        cls = collections.Counter()
        prim = []
        for i in range(nc):
            t = touch[i]
            if t.sum() < MIN_TOUCH_POINTS:
                cls["none"] += 1; prim.append(-1); continue
            k = int(t.argmax()); share = t[k] / t.sum()
            cls["clean" if share >= CLEAN_SHARE else "ambiguous"] += 1
            prim.append(k)
        link_alts[str(int(cell))] = {"cell_m": cell, "reach_m": [cell, round(cell * 2 * math.sqrt(2))],
                                     "classes": dict(cls), "primary": prim}
    del mx, my, mid

    names_m = [norm_name(m["ov_navn"]) for m in mar]
    exact_by_name = {n: k for k, n in enumerate(names_m)}
    links = []
    lc = collections.Counter()
    for i, c in enumerate(cats):
        t = touch_main[i]; tsum = int(t.sum())
        nn = norm_name(c["op_navn"])
        k_name = exact_by_name.get(nn, -1)
        k_code = next((k for k, m in enumerate(mar) if m["mst_id"] == c["op_id"]), -1)
        if tsum < MIN_TOUCH_POINTS:
            k, share, cls = -1, None, "none"
        else:
            k = int(t.argmax()); share = float(t[k] / tsum)
            cls = "clean" if share >= CLEAN_SHARE else "ambiguous"
        others = [{"ov_id": mar[j]["ov_id"], "ov_navn": mar[j]["ov_navn"],
                   "coast_km": r4(t[j] * DENSIFY_M / 1000)}
                  for j in np.argsort(-t)[:4] if t[j] > 0]
        if k >= 0:
            ta, tb = set(nn.split()), set(names_m[k].split())
            jac = len(ta & tb) / len(ta | tb)
            nm_check = "exact" if nn == names_m[k] else ("partial" if jac > 0 else "different")
        else:
            nm_check, jac = "no link", None
        alts = {cs: (mar[a["primary"][i]]["ov_id"] if a["primary"][i] >= 0 else None)
                for cs, a in link_alts.items()}
        lc[(cls, nm_check)] += 1
        links.append({"op_id": c["op_id"], "op_navn": c["op_navn"], "class": cls,
                      "linked_ov_id": mar[k]["ov_id"] if k >= 0 else None,
                      "linked_ov_navn": mar[k]["ov_navn"] if k >= 0 else None,
                      "primary_share_of_coast": r4(share),
                      "coast_touch_km": r4(tsum * DENSIFY_M / 1000),
                      "touching": others,
                      "name_check": nm_check, "name_token_jaccard": r4(jac),
                      "ov_id_with_exactly_this_name": mar[k_name]["ov_id"] if k_name >= 0 else None,
                      "code_check_op_id_eq_marine_mst_id": (mar[k_code]["ov_id"] if k_code >= 0 else None),
                      "code_check_agrees_with_link": (k_code == k) if k >= 0 and k_code >= 0 else None,
                      "link_at_other_cell_sizes": alts,
                      "_k": k})
    res["link_construction"] = {
        "_status": ("A CONSTRUCTION. Neither layer carries a code linking a catchment to the "
                    "water body it drains into. Each catchment is linked to the marine water body "
                    "its boundary touches along the most coast."),
        "method": (f"Both layers' boundaries densified to <= {DENSIFY_M:g} m; marine boundary points "
                   f"hashed to a {CELL_M:g} m grid; a catchment boundary point 'touches' a water body "
                   f"when that body has a boundary point in its 3x3 cell neighbourhood (reach "
                   f"{CELL_M:g} to ~{CELL_M * 2 * math.sqrt(2):.0f} m). Coast touch length = touching "
                   f"points x {DENSIFY_M:g} m. Link = the body with most touching points. "
                   f"clean: that body holds >= {CLEAN_SHARE:.0%} of the touching points; ambiguous: "
                   f"less; none: fewer than {MIN_TOUCH_POINTS} touching points."),
        "checks": ("name: normalised op_navn vs the linked ov_navn (exact / partial token overlap / "
                   "different). code: catchment op_id equals a marine feature's mst_id; this equality "
                   "was noticed in the data, is not documented as a key, and is used only as a check."),
        "counts_by_class_and_name_check": {f"{a} / {b}": v for (a, b), v in sorted(lc.items())},
        "counts_by_class": dict(collections.Counter(l["class"] for l in links)),
        "code_check": dict(collections.Counter(
            "no marine mst_id equals op_id" if l["code_check_op_id_eq_marine_mst_id"] is None
            else ("agrees" if l["code_check_agrees_with_link"] else
                  ("disagrees" if l["code_check_agrees_with_link"] is False else "catchment unlinked"))
            for l in links)),
        "sensitivity_cell_size": {cs: {"classes": a["classes"],
                                       "links_differing_from_main": sum(
                                           1 for i in range(nc) if a["primary"][i] != link_alts[str(int(CELL_M))]["primary"][i])}
                                  for cs, a in link_alts.items()}}
    log(f"links: {res['link_construction']['counts_by_class']}")

    # ---------------- per-catchment totals (area level, suppressed where thin)
    catout = []
    for i, c in enumerate(cats):
        sup = ncontrib[i] < SUPPRESS_BELOW
        g = {}
        for j, gn in enumerate(("cattle", "pigs", "other")):
            g[gn] = None if ncontrib_g[i, j] < SUPPRESS_BELOW else r4(bygrp[i, j])
        # secondary suppression: with the total shown, one hidden cell would be
        # total minus the others, so the smallest shown cell is hidden as well
        if any(x is None for x in g.values()):
            shown = [(x, k) for k, x in g.items() if x is not None]
            if shown:
                g[min(shown)[1]] = None
        catout.append({"op_id": c["op_id"], "op_navn": c["op_navn"], "area_km2": r4(c["area_km2"]),
                       "areal_field": c["areal_field"],
                       "herd_records_inside": int(nrec[i]), "herd_records_with_DE_gt_0": int(ncontrib[i]),
                       "DE_total": None if sup else r4(tot[i]),
                       "DE_by_group": None if sup else g,
                       "DE_per_km2": None if sup else r4(dens[i]),
                       "DE_per_km2_cattle": None if sup or g["cattle"] is None else r4(bygrp[i, 0] / area[i]),
                       "DE_per_km2_pigs": None if sup or g["pigs"] is None else r4(bygrp[i, 1] / area[i]),
                       "suppressed": bool(sup),
                       "linked_ov_id": links[i]["linked_ov_id"], "link_class": links[i]["class"]})
    res["catchments"] = catout
    thr = NEAR_ABSENT_FRACTION * national
    order = np.argsort(dens)
    res["near_absent_catchments"] = {
        "rule": (f"catchment density < {NEAR_ABSENT_FRACTION:g} x the all-catchment density "
                 f"({r4(national)} DE/km2), i.e. < {r4(thr)} DE/km2. Stated before looking."),
        "threshold_DE_per_km2": r4(thr),
        "catchments": [{"op_navn": cats[i]["op_navn"], "op_id": cats[i]["op_id"],
                        "area_km2": r4(area[i]),
                        "DE_per_km2": None if ncontrib[i] < SUPPRESS_BELOW else r4(dens[i]),
                        "linked_ov_navn": links[i]["linked_ov_navn"], "link_class": links[i]["class"]}
                       for i in order if dens[i] < thr],
        "catchment_density_distribution_area_weighted_note": "catchment densities, one per catchment, unweighted:",
        "catchment_density_quantiles": qdict(dens)}

    # ---------------- water body densities
    wb_de = np.zeros(nm); wb_area = np.zeros(nm); wb_ncat = np.zeros(nm, np.int64)
    wb_allclean = np.ones(nm, bool); wb_cats = collections.defaultdict(list)
    wb_ncontrib = np.zeros(nm, np.int64)
    for i, l in enumerate(links):
        k = l["_k"]
        if k < 0:
            continue
        wb_de[k] += tot[i]; wb_area[k] += area[i]; wb_ncat[k] += 1; wb_ncontrib[k] += ncontrib[i]
        wb_cats[k].append(cats[i]["op_navn"])
        if not (l["class"] == "clean" and l["name_check"] == "exact"):
            wb_allclean[k] = False
    wb_dens = np.where(wb_ncat > 0, wb_de / np.maximum(wb_area, 1e-9), np.nan)

    # ---------------- stations
    ov = json.load(open(OVERLAY))
    meta, panel = load_panel()
    sids = [s["id"] for s in meta["stations"]]
    assert sids == ov["station_ids"], "overlay and panel station order differ"
    ns = len(sids)
    ovid_to_k = {m["ov_id"]: k for k, m in enumerate(mar)}
    st_wb = np.array([ovid_to_k[ov["areas"][w]] if w >= 0 else -1 for w in ov["waterbody_index"]], np.int64)
    st_dens = np.array([wb_dens[k] if k >= 0 else np.nan for k in st_wb])
    st_class = np.where(st_wb < 0, 0, np.where(np.isnan(st_dens), 1, 2))

    # summer station medians
    def summer_medians(key, year_from=None):
        st, mo, val, _ = panel[key]
        m = np.isin(mo % 12 + 1, SUMMER)
        if year_from:
            m &= (1980 + mo // 12) >= year_from
        med, cnt = group_median(st[m], val[m], ns, MIN_SUMMER_MONTHS)
        return med, cnt

    smed = {k: summer_medians(k) for k in VARS + ("sal_bed", "temp_bed")}
    plaus = {"oxy_bed": (0.0, 20.0), "oxysat_bed": (0.0, 200.0), "sal_bed": (0.0, 40.0)}
    res["panel_plausibility"] = {
        "what": ("station-month values in the panel outside a physically plausible range, counted and "
                 "NOT removed: every statistic here is a median or quantile, which such values barely move"),
        "counts": {k: {"range": list(r), "outside": int(((panel[k][2] < r[0]) | (panel[k][2] > r[1])).sum()),
                       "of": int(len(panel[k][2]))} for k, r in plaus.items()}}
    smed2 = {k: summer_medians(k, PERIOD2_FROM) for k in VARS}

    # depth
    reg = collections.defaultdict(list)
    with gzip.open(MAAL, "rb") as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";"):
            x = num((r.get("BundDybde_m") or "").strip('"'))
            if x is not None:
                reg[(r.get("ObservationsstedNr") or "").strip()].append(x)
    ctdx = json.load(open(CTDX)) if os.path.exists(CTDX) else None
    depth = np.full(ns, np.nan); dsrc = collections.Counter()
    for i, s in enumerate(sids):
        if s in reg:
            depth[i] = float(np.median(reg[s])); dsrc["register_median_BundDybde"] += 1
        elif ctdx and s in ctdx["max_sampled_depth"]:
            depth[i] = float(ctdx["max_sampled_depth"][s]); dsrc["ctd_max_sampled_depth_lower_bound"] += 1
        else:
            dsrc["unknown"] += 1

    has_o2 = ~np.isnan(smed["oxy_bed"][0])
    res["stations"] = {
        "panel_stations": ns,
        "outside_any_marine_water_body": int((st_class == 0).sum()),
        "in_water_body_with_no_linked_catchment": int((st_class == 1).sum()),
        "in_water_body_with_linked_catchment": int((st_class == 2).sum()),
        "with_summer_bed_oxygen_(>=%d_summer_months)" % MIN_SUMMER_MONTHS: int(has_o2.sum()),
        "basketable_with_summer_bed_oxygen": int((has_o2 & (st_class == 2)).sum()),
        "open_water_no_catchment_with_summer_bed_oxygen": int((has_o2 & (st_class == 1)).sum()),
        "outside_polygons_with_summer_bed_oxygen": int((has_o2 & (st_class == 0)).sum()),
        "depth_source_counts": dict(dsrc),
        "summer_definition": f"months {SUMMER}; a station's value is the median of all its summer station-month values (each itself a monthly median in the panel), all years 1980+, stations with >= {MIN_SUMMER_MONTHS} summer station-months",
        "fluorescence_note": "the panel's fluorescence is whole-cast ('fluo'), not a surface layer; it is used as present",
    }
    # open water, reported separately (not forced)
    ow = collections.defaultdict(list)
    for i in np.nonzero((st_class == 1) & has_o2)[0]:
        ow[st_wb[i]].append(smed["oxy_bed"][0][i])
    allow = np.array([smed["oxy_bed"][0][i] for i in np.nonzero((st_class == 1) & has_o2)[0]])
    res["open_water_stations"] = {
        "what": "stations in marine water bodies that no catchment touches; not basketed",
        "summer_bed_oxygen_station_medians": qdict(allow),
        "by_water_body": sorted([{"ov_id": mar[k]["ov_id"], "ov_navn": mar[k]["ov_navn"],
                                  "stations": len(v), "median_of_station_medians": r4(np.median(v))}
                                 for k, v in ow.items()], key=lambda d: -d["stations"])}

    # water body table (stations and densities)
    wbtab = []
    for k in range(nm):
        n_st = int(((st_wb == k) & has_o2).sum())
        if wb_ncat[k] == 0 and n_st == 0:
            continue
        wbtab.append({"ov_id": mar[k]["ov_id"], "ov_navn": mar[k]["ov_navn"],
                      "linked_catchments": wb_cats.get(k, []),
                      "catchment_area_km2": r4(wb_area[k]) if wb_ncat[k] else None,
                      "DE_per_km2": (r4(wb_dens[k]) if wb_ncat[k] and wb_ncontrib[k] >= SUPPRESS_BELOW
                                     else (None if wb_ncat[k] == 0 else "suppressed")),
                      "stations_with_summer_bed_oxygen": n_st,
                      "median_summer_bed_oxygen_of_stations": r4(np.nanmedian(smed["oxy_bed"][0][(st_wb == k) & has_o2])) if n_st else None,
                      "all_links_clean_and_name_exact": bool(wb_allclean[k]) if wb_ncat[k] else None})
    res["water_bodies"] = sorted(wbtab, key=lambda d: (d["DE_per_km2"] is None or isinstance(d["DE_per_km2"], str),
                                                        d["DE_per_km2"] if isinstance(d["DE_per_km2"], float) else 0))

    # ---------------- baskets
    basket_set = st_class == 2

    def assign(sd, mask):
        """Tertile labels from station-weighted cuts over the stations in mask, plus near-absent."""
        lab = np.full(ns, -1, np.int64)
        d = sd[mask]
        c1, c2 = np.quantile(d, [1 / 3, 2 / 3])
        lab[mask & (sd <= c1)] = 0
        lab[mask & (sd > c1) & (sd <= c2)] = 1
        lab[mask & (sd > c2)] = 2
        near = mask & (sd < thr)
        return lab, near, (c1, c2)

    lab, near, cuts = assign(st_dens, basket_set)
    names = ("low", "mid", "high")

    wb_supp = (wb_ncat > 0) & (wb_ncontrib < SUPPRESS_BELOW)
    st_supp = np.array([bool(wb_supp[k]) if k >= 0 else False for k in st_wb])
    supp_dens = wb_dens[wb_supp]

    def safe(x):
        """A cut or range end that equals a suppressed water body's density would
        disclose a one- or two-herd total; it is withheld."""
        return "suppressed" if np.any(np.abs(supp_dens - x) < 1e-9) else r4(x)

    def basket_defs(lab, near, cuts, mask_data):
        out = {}
        for b in range(3):
            m = (lab == b) & mask_data
            mr = m & ~st_supp
            out[names[b]] = {"stations": int(m.sum()), "water_bodies": int(len(set(st_wb[m]))),
                             "density_range_DE_per_km2_unsuppressed_water_bodies":
                                 [safe(st_dens[mr].min()), safe(st_dens[mr].max())] if mr.any() else None,
                             "water_bodies_with_suppressed_density": int(len(set(st_wb[m & st_supp])))}
        m = near & mask_data
        out["near_absent"] = {"stations": int(m.sum()), "water_bodies": int(len(set(st_wb[m]))),
                              "water_body_names": sorted({mar[k]["ov_navn"] for k in st_wb[m]}),
                              "note": "overlaps the low tertile; it is its extreme end, not a fourth disjoint basket"}
        out["cuts_DE_per_km2"] = [safe(cuts[0]), safe(cuts[1])]
        return out

    res["baskets"] = {
        "rule": ("Stations in a water body with at least one linked catchment. Tertiles of the station "
                 "density (station-weighted cut points; whole water bodies move together, so sizes are "
                 "unequal): low <= cut1 < mid <= cut2 < high. near_absent: density < "
                 f"{NEAR_ABSENT_FRACTION:g} x national."),
        "definition_on_stations_with_summer_bed_oxygen": basket_defs(lab, near, cuts, has_o2),
    }

    # ---------------- comparison machinery
    def compare(v, lab, near, mask):
        m = mask & ~np.isnan(v)
        out = {}
        for b in range(3):
            mb = m & (lab == b)
            out[names[b]] = qdict(v[mb])
            out[names[b]]["water_bodies"] = int(len(set(st_wb[mb])))
            if mb.sum() >= 2:
                w_same, w_diff = pair_diffs(v[mb], st_wb[mb])
                out[names[b]]["where_the_spread_lives"] = {
                    "abs_diff_station_pairs_same_water_body": qdict(w_same),
                    "abs_diff_station_pairs_different_water_body": qdict(w_diff)}
        mn = m & near
        out["near_absent"] = qdict(v[mn])
        out["near_absent"]["water_bodies"] = int(len(set(st_wb[mn])))
        hi, lo = v[m & (lab == 2)], v[m & (lab == 0)]
        na = v[mn]
        out["contrasts"] = {
            "median_high_minus_median_low": r4(np.median(hi) - np.median(lo)) if len(hi) and len(lo) else None,
            "median_near_absent_minus_median_high": r4(np.median(na) - np.median(hi)) if len(na) and len(hi) else None,
            "P(high station < low station)": r4(cles_less(hi, lo)),
            "P(high station < near_absent station)": r4(cles_less(hi, na)) if len(na) else None}
        mt = m & (lab >= 0)
        out["kendall_tau_b_station_density_vs_value"] = r4(kendall_tau_b(st_dens[mt], v[mt])) if mt.sum() > 2 else None
        # water-body level
        ks = sorted(set(st_wb[mt]))
        if len(ks) > 2:
            wv = [np.median(v[mt & (st_wb == k)]) for k in ks]
            out["kendall_tau_b_water_body_density_vs_median_value"] = r4(kendall_tau_b(wb_dens[ks], np.array(wv)))
            out["water_bodies_in_tau"] = len(ks)
        auc, nw, nacr = pair_auc(v[mt], lab[mt]) if mt.sum() > 3 else (None, 0, 0)
        out["pair_auc_within_vs_across_tertiles"] = {
            "value": r4(auc), "within_pairs": nw, "across_pairs": nacr,
            "reading": "share of (within-basket pair, across-basket pair) comparisons where the within pair is closer; 0.5 = the baskets say nothing"}
        allv = v[mt]
        out["all_basketed"] = qdict(allv)
        return out

    def station_null(v, lab, near, mask, ndraw, with_auc=0, with_quant=False):
        m = mask & ~np.isnan(v) & (lab >= 0)
        vals = v[m]; L = lab[m]; N = near[m]
        n = len(vals)
        ih, il, ina = np.nonzero(L == 2)[0], np.nonzero(L == 0)[0], np.nonzero(N)[0]
        dhl, dnh, cl = [], [], []
        quant = {b: {"q10": [], "q50": [], "q90": []} for b in names}
        for s in range(0, ndraw, 500):
            k = min(500, ndraw - s)
            P = np.argsort(RNG.random((k, n)), axis=1)
            V = vals[P]
            H, Lo = V[:, ih], V[:, il]
            dhl.append(np.median(H, 1) - np.median(Lo, 1))
            if len(ina):
                dnh.append(np.median(V[:, ina], 1) - np.median(H, 1))
            cl.append(cles_less_batch(H, Lo))
            if with_quant:
                for b in range(3):
                    X = V[:, np.nonzero(L == b)[0]]
                    qq = np.quantile(X, [0.1, 0.5, 0.9], axis=1)
                    quant[names[b]]["q10"].append(qq[0]); quant[names[b]]["q50"].append(qq[1]); quant[names[b]]["q90"].append(qq[2])
        out = {"dhl": np.concatenate(dhl), "dnh": np.concatenate(dnh) if dnh else np.array([]),
               "cles": np.concatenate(cl)}
        if with_auc:
            out["auc"] = np.array([pair_auc(vals[RNG.permutation(n)], L)[0] for _ in range(with_auc)])
        if with_quant:
            out["quant"] = {b: {q: np.concatenate(x) for q, x in d.items()} for b, d in quant.items()}
        return out

    wb_with = np.array(sorted(set(st_wb[basket_set])))

    def block_null(v, mask, ndraw):
        """Shuffle the densities among water bodies (station sets per water body kept
        whole), then rerun the same basket procedure: sizes follow the procedure."""
        m0 = mask & ~np.isnan(v)
        dhl, dnh, cl, sizes = [], [], [], []
        base = wb_dens.copy()
        for _ in range(ndraw):
            d2 = base.copy()
            d2[wb_with] = base[RNG.permutation(wb_with)]
            sd = np.where(st_wb >= 0, d2[np.maximum(st_wb, 0)], np.nan)
            l2, n2, _c = assign(sd, basket_set)
            m = m0 & (l2 >= 0)
            hi, lo, na = v[m & (l2 == 2)], v[m & (l2 == 0)], v[m & n2]
            if len(hi) == 0 or len(lo) == 0:
                continue
            dhl.append(np.median(hi) - np.median(lo))
            dnh.append(np.median(na) - np.median(hi) if len(na) else np.nan)
            cl.append(cles_less(hi, lo))
            sizes.append((len(lo), len(hi), len(na)))
        sizes = np.array(sizes)
        return {"dhl": np.array(dhl), "dnh": np.array(dnh), "cles": np.array(cl),
                "sizes": {"low": band_summary(sizes[:, 0]), "high": band_summary(sizes[:, 1]),
                          "near_absent": band_summary(sizes[:, 2])}}

    def floor_report(cmp, sn, bn=None):
        c = cmp["contrasts"]
        out = {"station_level": {
            "what": "random baskets of stations with exactly the real basket sizes (values permuted among basketed stations)",
            "median_high_minus_median_low": place(c["median_high_minus_median_low"], sn["dhl"]),
            "median_near_absent_minus_median_high": place(c["median_near_absent_minus_median_high"], sn["dnh"]) if len(sn["dnh"]) else None,
            "P(high station < low station)": place(c["P(high station < low station)"], sn["cles"])}}
        if "auc" in sn:
            out["station_level"]["pair_auc_within_vs_across"] = place(cmp["pair_auc_within_vs_across_tertiles"]["value"], sn["auc"])
        if bn is not None:
            out["water_body_block_level"] = {
                "what": ("the constrained null of methods section 7: densities shuffled among water bodies, "
                         "each water body's stations kept together, the same tertile/near-absent procedure rerun; "
                         "basket sizes follow the procedure (distribution given)"),
                "basket_sizes": bn["sizes"],
                "median_high_minus_median_low": place(c["median_high_minus_median_low"], bn["dhl"]),
                "median_near_absent_minus_median_high": place(c["median_near_absent_minus_median_high"], bn["dnh"]),
                "P(high station < low station)": place(c["P(high station < low station)"], bn["cles"])}
        return out

    # ---------------- main comparison, all variables
    comps = {}
    for key in VARS:
        v = smed[key][0]
        cmp = compare(v, lab, near, basket_set)
        log(f"{key}: compare done")
        sn = station_null(v, lab, near, basket_set, N_NULL, with_auc=N_AUC_NULL if key == "oxy_bed" else 0,
                          with_quant=True)
        bn = block_null(v, basket_set, N_NULL)
        cmp["noise_floor"] = floor_report(cmp, sn, bn)
        # ubiquitous part: what every random basket shows
        ub = {}
        for b in names:
            ub[b] = {q: {"random_baskets": band_summary(sn["quant"][b][q]),
                         "real_basket": cmp[b].get({"q10": "q10", "q50": "q50", "q90": "q90"}[q])}
                     for q in ("q10", "q50", "q90")}
        cmp["ubiquitous_part"] = {
            "what": ("the station-level quantiles every random basket of this size reproduces: the band "
                     "across draws is what any basket would show (national, 'Denmarkness'), not local"),
            "by_basket_size": ub}
        comps[key] = cmp
        log(f"{key}: nulls done; high-low {cmp['contrasts']['median_high_minus_median_low']}")
    res["comparison_all_years"] = comps

    # seasonal profile of bed oxygen: ubiquitous across random baskets
    st, mo, val, _ = panel["oxy_bed"]
    keep = basket_set[st] & has_o2[st]
    st_r, cm_r, val_r = st[keep], mo[keep] % 12, val[keep]
    basket_st = np.nonzero(basket_set & has_o2)[0]
    real_lab = lab.copy()

    def profile(labarr):
        L = labarr[st_r]
        prof = np.full((3, 12), np.nan)
        for b in range(3):
            mb = L == b
            for mth in range(12):
                x = val_r[mb & (cm_r == mth)]
                if len(x):
                    prof[b, mth] = np.median(x)
        return prof

    real_prof = profile(real_lab)
    sizes_real = [int((real_lab[basket_st] == b).sum()) for b in range(3)]
    profs = np.empty((N_PROFILE, 3, 12))
    min_month = collections.Counter()
    for d in range(N_PROFILE):
        l2 = np.full(ns, -1, np.int64)
        perm = RNG.permutation(basket_st)
        l2[perm[:sizes_real[0]]] = 0
        l2[perm[sizes_real[0]:sizes_real[0] + sizes_real[1]]] = 1
        l2[perm[sizes_real[0] + sizes_real[1]:]] = 2
        p = profile(l2)
        profs[d] = p
        for b in range(3):
            min_month[int(np.nanargmin(p[b])) + 1] += 1
    res["ubiquitous_seasonal_profile_bed_oxygen"] = {
        "what": (f"median bed oxygen (mg/l) of all station-month values by calendar month, per basket; "
                 f"{N_PROFILE} random station baskets of the real tertile sizes {sizes_real}"),
        "real_baskets": {names[b]: [r4(x) for x in real_prof[b]] for b in range(3)},
        "random_band_min": [r4(np.nanmin(profs[:, :, m])) for m in range(12)],
        "random_band_max": [r4(np.nanmax(profs[:, :, m])) for m in range(12)],
        "month_of_minimum_across_random_baskets": {str(k): v for k, v in sorted(min_month.items())},
        "month_of_minimum_real": {names[b]: int(np.nanargmin(real_prof[b])) + 1 for b in range(3)},
        "random_basket_count": 3 * N_PROFILE}
    log("profile done")

    # ---------------- strata
    sal = smed["sal_bed"][0]
    strata_def = {
        f"brackish_bed_salinity_lt_{SAL_CUT:g}": ~np.isnan(sal) & (sal < SAL_CUT),
        f"marine_bed_salinity_ge_{SAL_CUT:g}": ~np.isnan(sal) & (sal >= SAL_CUT),
        f"shallow_depth_le_{DEPTH_CUT:g}m": ~np.isnan(depth) & (depth <= DEPTH_CUT),
        f"deep_depth_gt_{DEPTH_CUT:g}m": ~np.isnan(depth) & (depth > DEPTH_CUT)}
    base = list(strata_def)
    for a in base[:2]:
        for b in base[2:]:
            strata_def[f"{a} & {b}"] = strata_def[a] & strata_def[b]
    strata = {"cuts": {"bed_salinity": (f"{SAL_CUT:g} per mille, station summer median of sal_bed "
                                        f"(>= {MIN_SUMMER_MONTHS} summer months); stated before looking: roughly "
                                        "the Belt Sea transition between Baltic-influenced and Kattegat/Skagerrak bottom water"),
                       "depth": (f"{DEPTH_CUT:g} m, station bottom depth = median BundDybde_m of the depth register "
                                 "(maaledybde), else the deepest CTD sample (a lower bound); the project's own DEEP_M "
                                 "in scripts/hypodraft_ctd.py uses the same 10 m"),
                       "baskets": "the global basket assignment is kept; only the station set is restricted"},
              "unknown": {"bed_salinity": int((basket_set & has_o2 & np.isnan(sal)).sum()),
                          "depth": int((basket_set & has_o2 & np.isnan(depth)).sum())},
              "results": {}}
    for sname, smask in strata_def.items():
        out = {}
        for key in ("oxy_bed", "oxysat_bed"):
            v = smed[key][0]
            mask = basket_set & smask
            cmp = compare(v, lab, near, mask)
            mm = mask & ~np.isnan(v)
            if (mm & (lab == 2)).sum() >= 3 and (mm & (lab == 0)).sum() >= 3:
                sn = station_null(v, lab, near, mask, N_NULL_STRATA)
                bn = block_null(v, mask, N_NULL_STRATA)
                cmp["noise_floor"] = floor_report(cmp, sn, bn)
            else:
                cmp["noise_floor"] = "too few stations in the high or low basket (< 3)"
            out[key] = cmp
        strata["results"][sname] = out
        log(f"stratum {sname} done")
    res["strata"] = strata

    # ---------------- sensitivities
    sens = {}
    v2 = smed2["oxy_bed"][0]
    cmp = compare(v2, lab, near, basket_set)
    sn = station_null(v2, lab, near, basket_set, N_NULL_STRATA)
    bn = block_null(v2, basket_set, N_NULL_STRATA)
    cmp["noise_floor"] = floor_report(cmp, sn, bn)
    sens[f"oxy_bed_summers_from_{PERIOD2_FROM}"] = cmp
    cleanset = basket_set & np.array([wb_allclean[k] if k >= 0 else False for k in st_wb])
    lab_c, near_c, cuts_c = assign(st_dens, cleanset)
    v = smed["oxy_bed"][0]
    cmp = compare(v, lab_c, near_c, cleanset)
    sn = station_null(v, lab_c, near_c, cleanset, N_NULL_STRATA)
    cmp["noise_floor"] = floor_report(cmp, sn)
    cmp["baskets"] = basket_defs(lab_c, near_c, cuts_c, has_o2)
    sens["oxy_bed_only_water_bodies_whose_links_are_all_clean_and_name_exact"] = cmp
    res["sensitivity"] = sens
    log("sensitivity done")

    # ---------------- repeat-measurement spread vs between-station spread (owner's addition)
    rep = {"question": ("Reading (a): the livestock grouping is a bad basket. Reading (b): no grouping is "
                        "better, because stations are alike - between-station spread no larger than the "
                        "spread of repeat measurements of one station. Decided by comparing the two.")}
    for key in VARS:
        st, mo, val, _ = panel[key]
        summ = np.isin(mo % 12 + 1, SUMMER)
        ok = summ & basket_set[st] & ~np.isnan(smed[key][0])[st]
        s, m, x = st[ok], mo[ok], val[ok]
        o = np.lexsort((m, s)); s, m, x = s[o], m[o], x[o]
        # A: same station, same summer, consecutive months
        adj = (s[1:] == s[:-1]) & (m[1:] - m[:-1] == 1) & ((m[1:] // 12) == (m[:-1] // 12))
        dA = np.abs(x[1:] - x[:-1])[adj]
        # B: two stations, same year-month
        oc = np.argsort(m, kind="stable"); sm, mm_, xm = s[oc], m[oc], x[oc]
        cells, cstart = np.unique(mm_, return_index=True)
        cend = np.append(cstart[1:], len(mm_))
        dsw, dsb, dxb = [], [], []
        for a, b in zip(cstart, cend):
            if b - a < 2:
                continue
            ss, xx = sm[a:b], xm[a:b]
            iu = np.triu_indices(b - a, 1)
            d = np.abs(xx[iu[0]] - xx[iu[1]]).astype(np.float32)
            wa, wb_ = st_wb[ss[iu[0]]], st_wb[ss[iu[1]]]
            la, lb = lab[ss[iu[0]]], lab[ss[iu[1]]]
            dsw.append(d[wa == wb_]); dsb.append(d[(wa != wb_) & (la == lb)]); dxb.append(d[la != lb])
        dsw, dsb, dxb = (np.concatenate(z) if z else np.array([]) for z in (dsw, dsb, dxb))
        dall = np.concatenate([dsw, dsb, dxb])
        # D: interchangeability null for station long-term medians
        med_obs, cnt = group_median(s, x, ns, MIN_SUMMER_MONTHS)
        keepst = ~np.isnan(med_obs) & basket_set
        def spreads(med):
            out = {"all": np.subtract(*np.quantile(med[keepst], [0.75, 0.25]))}
            for b in range(3):
                mb = keepst & (lab == b)
                out[names[b]] = np.subtract(*np.quantile(med[mb], [0.75, 0.25])) if mb.sum() > 3 else np.nan
            return out
        obs_sp = spreads(med_obs)
        ocell = np.lexsort((s, m))   # records ordered by cell
        s_c, m_c, x_c = s[ocell], m[ocell], x[ocell]
        null_sp = collections.defaultdict(list)
        for _ in range(N_INTERCH):
            pr = np.lexsort((RNG.random(len(x_c)), m_c))   # shuffle within each year-month cell
            xs = x_c[pr]
            med_n, _ = group_median(s_c, xs, ns, MIN_SUMMER_MONTHS)
            for kk, vv in spreads(med_n).items():
                null_sp[kk].append(vv)
        interch = {}
        for kk in obs_sp:
            nl = np.array(null_sp[kk])
            interch[kk] = {"observed_iqr_of_station_medians": r4(obs_sp[kk]),
                           "null_iqr_if_interchangeable": band_summary(nl),
                           "draws_with_null_iqr_ge_observed": int((nl >= obs_sp[kk]).sum()),
                           "ratio_observed_to_null_median": r4(obs_sp[kk] / np.median(nl)) if np.median(nl) > 0 else None}
        rep[key] = {
            "repeat_A_same_station_consecutive_summer_months_abs_diff": qdict(dA),
            "between_B_two_stations_same_year_month_abs_diff": {
                "all_pairs": qdict(dall),
                "same_water_body": qdict(dsw),
                "different_water_body_same_basket": qdict(dsb),
                "different_basket": qdict(dxb)},
            "ratio_median_between_all_to_median_repeat": r4(np.median(dall) / np.median(dA)) if len(dA) and np.median(dA) > 0 else None,
            "ratio_median_same_basket_diff_wb_to_repeat": r4(np.median(dsb) / np.median(dA)) if len(dsb) and len(dA) else None,
            "ratio_median_different_basket_to_same_basket_diff_wb": r4(np.median(dxb) / np.median(dsb)) if len(dsb) and len(dxb) else None,
            "interchangeability_null_for_station_medians": {
                "what": (f"each summer station-month value shuffled among the stations measured in the same "
                         f"year-month (so every station keeps its own months and count, only who-measured-what "
                         f"is broken); station medians recomputed; {N_INTERCH} draws. If the observed spread of "
                         f"station medians sits inside this null, the stations are interchangeable for this variable."),
                "by_set": interch}}
        log(f"repeat {key} done")
    # C: same-day replicate casts from the raw CTD
    if ctdx:
        reps = ctdx["replicates"]
        sid_set = {s: i for i, s in enumerate(sids)}
        dC, dCm, dCs = [], [], []
        for s, dat, bed, dm in reps:
            a, b = bed[0], bed[1]
            d = abs(a - b)
            dC.append(d)
            if abs(dm[0] - dm[1]) <= 1.0:
                dCm.append(d)
                if int(dat[4:6]) in SUMMER and s in sid_set and basket_set[sid_set[s]]:
                    dCs.append(d)
        rep["repeat_C_same_day_replicate_casts_bed_oxygen"] = {
            "what": ("station-dates carrying two or more survey numbers (UndersoegelsesNr) that each have "
                     "near-bed oxygen (mg/l, deepest quarter of that cast, the panel's rule); |first - second|. "
                     "Limits: a second survey number the same day may be a different programme, gear or time "
                     "of day, so this is a repeat of the station, not a laboratory replicate; it is a "
                     "single-cast value while the panel holds monthly medians."),
            "station_dates_scanned": ctdx["station_dates"],
            "station_dates_with_2plus_casts": ctdx["station_dates_with_2plus_casts_with_bed_oxygen"],
            "oxygen_units_seen": ctdx["oxygen_units"],
            "all": qdict(dC), "casts_reaching_within_1m_of_each_other": qdict(dCm),
            "summer_basketed_stations_within_1m": qdict(dCs)}
    res["repeat_vs_between"] = rep

    # ---------------- readings, computed from the numbers above
    readings = {}
    for key in VARS:
        c = comps[key]
        fl = c["noise_floor"]["station_level"]["median_high_minus_median_low"]
        bl = c["noise_floor"]["water_body_block_level"]["median_high_minus_median_low"]
        it = rep[key]["interchangeability_null_for_station_medians"]["by_set"]
        interchangeable_all = it["all"]["draws_with_null_iqr_ge_observed"] > 0.025 * N_INTERCH
        within = {b: (it[b]["draws_with_null_iqr_ge_observed"] > 0.025 * N_INTERCH) for b in names}
        beats_station = fl.get("verdict", "").startswith("outside the whole")
        beats_block = bl.get("verdict", "").startswith("outside the whole")
        if interchangeable_all:
            r = "(b) stations interchangeable for this variable: their spread is no larger than repeat measurement would give"
        elif beats_station and beats_block:
            r = ("livestock contrast beats both floors widely; within-basket spread: " +
                 ", ".join(f"{b} {'interchangeable' if within[b] else 'NOT uniform'}" for b in names))
        else:
            r = ("(a) population is NOT uniform (station spread exceeds the interchangeability null) and the "
                 "livestock line does not account for it by a wide margin: not uniform but unexplained by livestock")
        readings[key] = {"station_null_verdict": fl.get("verdict"), "block_null_verdict": bl.get("verdict"),
                         "stations_interchangeable_overall": bool(interchangeable_all),
                         "within_basket_interchangeable": within, "reading": r,
                         "rule": ("interchangeable if at least 2.5% of interchangeability draws reach the observed "
                                  "IQR of station medians; 'beats widely' = outside the whole range of the null draws")}
    res["readings"] = readings
    for l in links:
        del l["_k"]
    res["links"] = links
    res["construction_choices"] = {
        "summer_months": list(SUMMER), "min_summer_station_months": MIN_SUMMER_MONTHS,
        "near_absent_fraction_of_national": NEAR_ABSENT_FRACTION, "bed_salinity_cut": SAL_CUT,
        "depth_cut_m": DEPTH_CUT, "boundary_densify_m": DENSIFY_M, "adjacency_cell_m": CELL_M,
        "adjacency_cell_alternatives_m": list(CELL_M_ALTS), "clean_link_share": CLEAN_SHARE,
        "min_touch_points": MIN_TOUCH_POINTS, "suppress_below_herds": SUPPRESS_BELOW,
        "period_sensitivity_from": PERIOD2_FROM, "null_draws": N_NULL, "null_draws_strata": N_NULL_STRATA,
        "auc_null_draws": N_AUC_NULL, "profile_draws": N_PROFILE, "interchangeability_draws": N_INTERCH,
        "rng_seed": 20260912, "quantiles": list(Q),
        "area": "catchment area from the geometry on a sinusoidal equal-area projection (R = 6371008.8 m)",
        "distance": "local equirectangular metres at 56 N for adjacency"}
    with open(OUT, "w") as fo:
        json.dump(res, fo, ensure_ascii=False, indent=1)
    log(f"wrote {OUT}")


if __name__ == "__main__":
    main()
