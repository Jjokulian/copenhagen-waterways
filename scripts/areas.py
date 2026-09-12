#!/usr/bin/env python3
"""There is no Denmark. There are 123 marine areas with different causes.

Every published figure in this argument is a national aggregate: one share of the
land-borne load, one indsatsbehov ladder. Aggregation is where the information goes:
a number that is true of Denmark need not be true of any one place in it.

So this script refuses the aggregate and builds one record per marine water body:
what presses on it, what is observed in it, over which years each of those streams
exists, and - stated as plainly as the rest - what cannot be modelled there and why.

Assignment is by nearest point on the marine boundary, via a grid hash over the
1.47 M boundary vertices, with the largest distance per layer and area recorded so a
reader can see how firm the assignment is. Outfalls sit on land; bathing stations sit on the
shore; dumping grounds sit in the water. One rule, one distance, no hidden choices.

The cross-sectional estimate at the end is a cum hoc effect size and is labelled as
one. It regresses a sewage-driven outcome (bathing quality) on sewage pressure
(treatment-plant PE and rain-conditioned outfall density), across areas rather than
across years, because the open data have more areas than they have years of
comparable observation.

Output: data/derived/areas.json. The page, docs/AREAS.md, is written from it by
scripts/pages/areas.py, so every number on the page is read back from this file
with its chain rather than formatted straight from memory.

Usage:  scripts/heavy python3 scripts/areas.py
"""
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, MANUAL, RAW, ROOT, log, read_json, write_json
import lineage

NAT = os.path.join(RAW, "national")
OUT_JSON = os.path.join(DERIVED, "areas.json")

CELL = 0.05           # grid cell, degrees
STRIDE = 4            # keep every Nth boundary vertex; ~15 m spacing, ample at 20 km
MAX_ASSIGN_KM = 20.0  # beyond this a point belongs to no marine area

YEARS = [f"{y:02d}" for y in list(range(91, 100)) + list(range(0, 19))]
YEAR_NUM = {y: (1900 + int(y) if int(y) >= 91 else 2000 + int(y)) for y in YEARS}
SCORE = {"Excellent": 4, "Good": 3, "Good or Sufficient": 3, "Sufficient": 2, "Poor": 1}

# The water bodies with a station-level statistical model, by id, as DHI's method
# report lists them (Tabel 5 of DHI-MODEL-DEL1-2015), matched by number and name in
# data/manual/statistical_models.json. It replaced a six-letter name match, which
# flagged water bodies DHI does not list and missed some it does.
MODELLED_IDS = {i for e in read_json(os.path.join(MANUAL, "statistical_models.json"))["entries"]
                for i in e["ids"]}
MODEL_WINDOW = (1990, 2012)

# Point and polygon layers to attribute to areas. (file, key, what it is, kind)
PRESSURES = [
    ("punkt_rbu_udl", "rbu", "rain-conditioned outfalls (overflows and separate storm)", "point"),
    ("punkt_rens_udl", "rens", "wastewater treatment plants", "point"),
    ("punkt_havdam_udl", "havdam", "marine aquaculture discharge", "point"),
    ("klappladser", "klap", "licensed dredged-material dumping grounds", "poly"),
    ("raastofomr", "raastof", "raw-material extraction areas", "poly"),
]

# What the lineage of cum_hoc.tests.2.r needs from the run, kept as the run reads
# it (record_cum_hoc_r, at the end). Read-only: nothing here feeds areas.json.
TRACE = {}


def haversine(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(math.radians, (la1, lo1, la2, lo2))
    h = (math.sin((la2 - la1) / 2) ** 2
         + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(h))


class Assigner:
    """Nearest marine water body, by boundary vertex, via a grid hash."""

    def __init__(self, features):
        self.lat, self.lon, self.wb = [], [], []
        self.grid = collections.defaultdict(list)
        for i, f in enumerate(features):
            for poly in f["geometry"]["coordinates"]:
                for ring in poly:
                    for x, y in ring[::STRIDE]:
                        n = len(self.lat)
                        self.lat.append(y)
                        self.lon.append(x)
                        self.wb.append(i)
                        self.grid[(int(y / CELL), int(x / CELL))].append(n)
        log(f"  index: {len(self.lat):,} boundary vertices in {len(self.grid):,} cells")

    def nearest(self, lat, lon, max_km=MAX_ASSIGN_KM):
        cy, cx = int(lat / CELL), int(lon / CELL)
        best, best_d = None, None
        rings = int(max_km / (CELL * 111.0)) + 1
        for r in range(rings + 1):
            got = False
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if r and max(abs(dy), abs(dx)) != r:
                        continue
                    for n in self.grid.get((cy + dy, cx + dx), ()):
                        got = True
                        d = haversine(lat, lon, self.lat[n], self.lon[n])
                        if best_d is None or d < best_d:
                            best, best_d = self.wb[n], d
            # one extra ring after the first hit, so a near-miss in the next cell wins
            if best is not None and got and r > 0:
                break
        if best_d is not None and best_d <= max_km:
            return best, best_d
        return None, None


def centroid(geom):
    def walk(c, depth):
        if depth == 0:
            return [c]
        out = []
        for x in c:
            out += walk(x, depth - 1)
        return out
    t = geom["type"]
    depth = {"Point": 0, "LineString": 1, "Polygon": 2, "MultiPolygon": 3,
             "MultiLineString": 2, "MultiPoint": 1}[t]
    pts = walk(geom["coordinates"], depth)
    return sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts)


def load_bathing(wb_ids):
    st = []
    doc = read_json(os.path.join(NAT, "badevand.geojson"))
    TRACE["badevand"] = doc
    for p in (f["properties"] for f in doc["features"]):
        s = {YEAR_NUM[y]: SCORE[p["quality_" + y]]
             for y in YEARS if p.get("quality_" + y) in SCORE}
        if s:
            st.append({"wb": p.get("wbid") if p.get("wbid") in wb_ids else None,
                       "name": p["name"], "lat": p["latitude"], "lon": p["longitude"],
                       "s": s})
    return st


def slope(pairs):
    """OLS slope of value on year, per decade."""
    if len(pairs) < 8:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return 10.0 * sum((xs[i] - mx) * (ys[i] - my) for i in range(len(xs))) / den


def pearson(u, v):
    n = len(u)
    if n < 6:
        return None
    mu, mv = sum(u) / n, sum(v) / n
    su = math.sqrt(sum((t - mu) ** 2 for t in u))
    sv = math.sqrt(sum((t - mv) ** 2 for t in v))
    if su == 0 or sv == 0:
        return None
    return sum((u[i] - mu) * (v[i] - mv) for i in range(n)) / (su * sv)


def build():
    mdoc = read_json(os.path.join(NAT, "marin_overordnet.geojson"))
    marine = mdoc["features"]
    TRACE["marine"] = mdoc
    props = [f["properties"] for f in marine]
    wb_ids = {p["ov_id"] for p in props}
    idx = {p["ov_id"]: i for i, p in enumerate(props)}

    log("building the boundary index")
    A = Assigner(marine)
    TRACE["A"] = A

    rec = {}
    for i, p in enumerate(props):
        modelled = p["ov_id"] in MODELLED_IDS
        rec[p["ov_id"]] = {
            "id": p["ov_id"], "name": p["ov_navn"], "area_km2": p["ov_stoe"],
            "type": p["ov_typ"], "category": p["ov_kat"],
            "district": p.get("distr_na"), "catchment": p.get("ho_na"),
            "natural": p.get("na_kun_stm"),
            "centroid": [round(v, 4) for v in centroid(marine[i]["geometry"])],
            "pressure": {}, "observation": {}, "streams": [],
            "has_statistical_model": modelled,
        }

    # ---- pressures ------------------------------------------------------
    for fn, key, what, kind in PRESSURES:
        path = os.path.join(NAT, f"{fn}.geojson")
        if not os.path.exists(path):
            continue
        doc = read_json(path)
        feats = doc["features"]
        if fn == "punkt_rens_udl":
            TRACE[key] = {"doc": doc, "got": []}
        far = 0
        for f in feats:
            lat, lon = centroid(f["geometry"])
            w, d = A.nearest(lat, lon)
            if key in TRACE:
                TRACE[key]["got"].append((w, d))
            if w is None:
                far += 1
                continue
            r = rec[props[w]["ov_id"]]["pressure"].setdefault(
                key, {"what": what, "n": 0, "max_dist_km": 0.0})
            r["n"] += 1
            r["max_dist_km"] = round(max(r["max_dist_km"], d), 1)
            q = f["properties"]
            if key == "rbu" and q.get("vol_sb"):
                r["basin_m3"] = r.get("basin_m3", 0) + q["vol_sb"]
            if key == "rens":
                r["pe"] = r.get("pe", 0) + (q.get("godk_pe") or 0)
                r.setdefault("stages", {})
                s = q.get("rens_sta") or "ukendt"
                r["stages"][s] = r["stages"].get(s, 0) + 1
            if key == "raastof" and q.get("udlobsdato"):
                r.setdefault("permits_expire", []).append(q["udlobsdato"][:4])
        log(f"  {key:8} {len(feats):>6,} features, {far:,} beyond {MAX_ASSIGN_KM:.0f} km")

    # ---- observation: bathing water -------------------------------------
    st = load_bathing(wb_ids)
    per = collections.defaultdict(list)
    for s in st:
        if s["wb"]:
            per[s["wb"]].append(s)
    TRACE.update(st=st, per=per)
    for w, v in per.items():
        yrs = sorted({y for s in v for y in s["s"]})
        allpairs = [(y, s["s"][y]) for s in v for y in s["s"]]
        informative = [s for s in v if sum(1 for q in s["s"].values() if q < 4) >= 3]
        rr = None
        if len(informative) >= 3:
            common = sorted(set.intersection(*[set(s["s"]) for s in informative])) \
                if all(s["s"] for s in informative) else []
            rs = []
            for a in range(len(informative)):
                for b in range(a + 1, len(informative)):
                    ys = sorted(set(informative[a]["s"]) & set(informative[b]["s"]))
                    if len(ys) >= 12:
                        c = pearson([informative[a]["s"][y] for y in ys],
                                    [informative[b]["s"][y] for y in ys])
                        if c is not None:
                            rs.append(c)
            if rs:
                rr = sum(rs) / len(rs)
        rec[w]["observation"]["bathing"] = {
            "stations": len(v), "informative_stations": len(informative),
            "first_year": yrs[0], "last_year": yrs[-1],
            "mean_score": round(sum(p[1] for p in allpairs) / len(allpairs), 3),
            "sub_excellent_share": round(
                sum(1 for p in allpairs if p[1] < 4) / len(allpairs), 3),
            "trend_per_decade": None if slope(allpairs) is None else round(slope(allpairs), 3),
            "internal_r": None if rr is None else round(rr, 3),
        }
        rec[w]["streams"].append({"stream": "Bathing water quality", "from": yrs[0],
                                  "to": yrs[-1], "n": len(v), "cadence": "annual class"})

    # ---- observation: hazardous substances -------------------------------
    #
    # WITHDRAWN. This block used to assign every point in sw_mfs_tilstand to its
    # nearest marine water body within MAX_ASSIGN_KM, and 66 of 123 bodies came out
    # carrying a hazardous-substance observation count. Every one of those was
    # freshwater: the layer holds 152 DKLAKE and 104 DKRIVER points and ZERO DKCOAST.
    # Assigning a lake monitoring point to the sea because the sea is within 20 km
    # manufactured marine coverage that does not exist - a modelled value in a column
    # shaped like a measured one, which is exactly the class 7 error this project
    # audits elsewhere. It is ours.
    #
    # The layer is also unusable for the purpose on its own terms: every point carries
    # the same qecode ("QE3-3 - River Basin Specific Pollutants") and a status code
    # with NO analyte, concentration or unit, so even where it applies it says that
    # something was assessed, not what was found.
    #
    # The absence is now reported as an absence, below.
    hz = []
    for f in hz:
        lat, lon = centroid(f["geometry"])
        w, d = A.nearest(lat, lon)
        if w is None:
            continue
        q = f["properties"]
        r = rec[props[w]["ov_id"]]["observation"].setdefault(
            "hazardous", {"stations": 0, "first_year": None, "matrices": {}})
        r["stations"] += 1
        y = (q.get("aktivstart") or "")[-4:]
        if y.isdigit():
            r["first_year"] = min(int(y), r["first_year"] or 9999)
        for m, lab in (("maaltvand", "water"), ("maaltsedim", "sediment"),
                       ("maaltbiota", "biota")):
            if q.get(m) == "Ja":
                r["matrices"][lab] = r["matrices"].get(lab, 0) + 1

    # ---- observation: the statistical model, and its window --------------
    for w, r in rec.items():
        if r["has_statistical_model"]:
            r["streams"].append({"stream": "DCE statistical model (TN/TP/Chl a/Kd)",
                                 "from": MODEL_WINDOW[0], "to": MODEL_WINDOW[1],
                                 "n": None, "cadence": "fitted once, 1990-2012"})
        h = r["observation"].get("hazardous")
        if h and h["first_year"]:
            r["streams"].append({"stream": "Hazardous substances", "from": h["first_year"],
                                 "to": 2019, "n": h["stations"], "cadence": "campaign"})
        r["streams"].sort(key=lambda s: s["from"])

    # ---- what cannot be modelled, and why --------------------------------
    for r in rec.values():
        gaps = []
        if not r["has_statistical_model"]:
            gaps.append("No station-level statistical model relates nutrient load to "
                        "an indicator here. Its requirement comes from DHI's mechanistic "
                        "model, a meta-analysis, or neither: the requirement table of "
                        "DHI's method report (Tabel 6) says which.")
        b = r["observation"].get("bathing")
        if not b:
            gaps.append("No bathing station: there is no long, repeated observation "
                        "of any marine variable here in the open data.")
        elif b["informative_stations"] < 3:
            gaps.append("Fewer than three bathing stations vary enough to correlate, "
                        "so whether this area behaves as one unit cannot be tested.")
        if "hazardous" not in r["observation"]:
            gaps.append("No marine hazardous-substance monitoring point. The national "
                        "layer sw_mfs_tilstand holds 256 points, all freshwater "
                        "(152 lake, 104 river) and none marine, and carries no analyte "
                        "or concentration. This gap applies to all 123 water bodies.")
        if r["area_km2"] > 500 and (b or {}).get("stations", 0) < 6:
            gaps.append(f"{r['area_km2']:,.0f} km² described by "
                        f"{(b or {}).get('stations', 0)} shore observations.")
        r["not_modelled"] = gaps
        r["n_gaps"] = len(gaps)
    return props, rec


def hazardous_layer():
    """The national hazardous-substance layer, counted by water type: why no marine
    water body carries a hazardous-substance observation here."""
    feats = read_json(os.path.join(NAT, "sw_mfs_tilstand.geojson"))["features"]
    kinds = collections.Counter((f["properties"].get("eusurfacew") or "")[:6] for f in feats)
    return {"points": len(feats), "lake": kinds.get("DKLAKE", 0),
            "river": kinds.get("DKRIVE", 0), "coast": kinds.get("DKCOAS", 0)}


def summarize(rec):
    """The state-of-knowledge counts, stored so the page reads them with a chain."""
    sets = {
        "all": list(rec.values()),
        "modelled": [r for r in rec.values() if r["has_statistical_model"]],
        "with_bathing": [r for r in rec.values() if r["observation"].get("bathing")],
        "testable": [r for r in rec.values()
                     if (r["observation"].get("bathing") or {}).get("informative_stations", 0) >= 3],
        "neither": [r for r in rec.values() if not r["has_statistical_model"]
                    and not r["observation"].get("bathing")],
    }
    return {"sea_km2": round(sum(r["area_km2"] for r in rec.values()), 1),
            "sets": {k: {"n": len(v), "km2": round(sum(r["area_km2"] for r in v), 1)}
                     for k, v in sets.items()}}


def cum_hoc(rec):
    """Cross-sectional effect size: sewage pressure against a sewage outcome.

    This is a correlation across areas at one time, not a causal estimate, and the
    only reason to prefer it to the national aggregate is that it has one unit of
    replication per area with data (the count is stored with the result), where the
    aggregate has one."""
    rows = []
    for r in rec.values():
        b = r["observation"].get("bathing")
        if not b or b["stations"] < 2 or not r["area_km2"]:
            continue
        rbu = r["pressure"].get("rbu", {})
        rens = r["pressure"].get("rens", {})
        rows.append({
            "id": r["id"], "name": r["name"], "area": r["area_km2"],
            "outfalls_per_km2": rbu.get("n", 0) / r["area_km2"],
            "pe_per_km2": rens.get("pe", 0) / r["area_km2"],
            "basin_m3_per_km2": rbu.get("basin_m3", 0) / r["area_km2"],
            "sub_excellent": b["sub_excellent_share"],
            "mean_score": b["mean_score"],
            "trend": b["trend_per_decade"],
        })
    out = {"n_areas": len(rows), "tests": []}
    for pred in ("outfalls_per_km2", "pe_per_km2", "basin_m3_per_km2"):
        x = [math.log10(1 + r[pred]) for r in rows]
        for outcome in ("sub_excellent", "mean_score"):
            y = [r[outcome] for r in rows]
            c = pearson(x, y)
            if c is not None:
                out["tests"].append({"predictor": "log10(1+%s)" % pred,
                                     "outcome": outcome, "r": round(c, 3),
                                     "r2": round(c * c, 3), "n": len(rows)})
    out["rows"] = sorted(rows, key=lambda r: -r["outfalls_per_km2"])
    return out


# ---- lineage: how cum_hoc.tests.2.r was made -------------------------------
#
# PROVENANCE_SPEC.md, its first number. Everything below READS what the run above
# did - TRACE, rec, ch - and writes docs/data/lineage/cum_hoc_r.json. The reasons
# quoted are the ones this file states; where it states none, the record says so.
LINEAGE_TEST = 2           # cum_hoc.tests[2]: log10(1+pe_per_km2) against sub_excellent
WFS = "https://wfs2-miljoegis.mim.dk/vp3basis2019/ows"
SERVED = ("served by MiljøGIS (wfs2-miljoegis.mim.dk, Miljøministeriet), workspace "
          "vp3basis2019; who compiled the rows is not recorded in the file")
ME = "this project, in scripts/areas.py"


def _quart(xs, nd=4):
    s = sorted(xs)
    n = len(s)
    if not n:
        return None

    def q(f):
        k = f * (n - 1)
        i = int(k)
        j = min(i + 1, n - 1)
        return round(s[i] + (s[j] - s[i]) * (k - i), nd)
    return {"n": n, "min": round(s[0], nd), "q1": q(.25), "median": q(.5),
            "q3": q(.75), "max": round(s[-1], nd)}


def _ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    out = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return out


def _nearest_exhaustive(A, lat, lon, max_km):
    """The rule as the docstring states it: the nearest kept boundary vertex within
    max_km, searching every cell that reach needs east-west as well as north-south,
    with no early stop. The vertex is picked on a local flat-earth distance and its
    distance then taken by haversine, as Assigner.nearest reports it."""
    ky = 111.2
    kx = 111.2 * math.cos(math.radians(lat))
    ry, rx = int(max_km / (CELL * ky)) + 1, int(max_km / (CELL * kx)) + 1
    cy, cx = int(lat / CELL), int(lon / CELL)
    best, bd = None, None
    for dy in range(-ry, ry + 1):
        for dx in range(-rx, rx + 1):
            for n in A.grid.get((cy + dy, cx + dx), ()):
                e = ((A.lat[n] - lat) * ky) ** 2 + ((A.lon[n] - lon) * kx) ** 2
                if bd is None or e < bd:
                    best, bd = n, e
    if best is None:
        return None, None
    d = haversine(lat, lon, A.lat[best], A.lon[best])
    return (A.wb[best], d) if d <= max_km else (None, None)


def record_cum_hoc_r(rec, ch):
    t = ch["tests"][LINEAGE_TEST]
    if (t["predictor"], t["outcome"]) != ("log10(1+pe_per_km2)", "sub_excellent"):
        raise RuntimeError("cum_hoc.tests[2] is no longer the PE test: move LINEAGE_TEST")
    here = os.path.abspath(__file__)
    lines, quote = lineage.lines, lineage.quote
    # this file's own lines are searched above this section, never inside it
    UNTIL = "# ---- lineage: how cum_hoc"
    src = lambda first, last=None: lines(here, first, last, until=UNTIL)
    say = lambda first, last=None: quote(here, first, last, until=UNTIL)
    A, per, st = TRACE["A"], TRACE["per"], TRACE["st"]
    mdoc, bdoc, pdoc = TRACE["marine"], TRACE["badevand"], TRACE["rens"]["doc"]
    marine, bath, plants = mdoc["features"], bdoc["features"], pdoc["features"]
    got = TRACE["rens"]["got"]
    props = [f["properties"] for f in marine]
    wb_ids = {p["ov_id"] for p in props}
    rows = ch["rows"]
    ids = [r["id"] for r in rows]
    meta = lambda d: {k: v for k, v in d.items() if k != "features"}
    rel = lambda p: os.path.relpath(p, ROOT)
    fetched = lambda layer: f"{WFS} typeName=vp3basis2019:{layer}, by scripts/fetch_national.py"
    P_MARINE = os.path.join(NAT, "marin_overordnet.geojson")
    P_RENS = os.path.join(NAT, "punkt_rens_udl.geojson")
    P_BATH = os.path.join(NAT, "badevand.geojson")

    # ---- the number itself, reproduced from the rows it was computed over
    x0 = [math.log10(1 + r["pe_per_km2"]) for r in rows]
    y0 = [r["sub_excellent"] for r in rows]
    c0 = pearson(x0, y0)
    if round(c0, 3) != t["r"]:
        raise RuntimeError(f"lineage: rows give r={c0}, areas.json says {t['r']}")

    # ---- plants: where each went, and what PE that carries
    def pe_by(assign):
        s = collections.Counter()
        for f, (w, _) in zip(plants, assign):
            if w is not None:
                s[props[w]["ov_id"]] += f["properties"].get("godk_pe") or 0
        return s
    base = pe_by(got)
    for i in ids:
        if base.get(i, 0) != rec[i]["pressure"].get("rens", {}).get("pe", 0):
            raise RuntimeError(f"lineage: PE of {i} does not reproduce")
    assigned = [(f, w, d) for f, (w, d) in zip(plants, got) if w is not None]
    pe_file = sum(f["properties"].get("godk_pe") or 0 for f in plants)
    pe_kept = sum(f["properties"].get("godk_pe") or 0 for f, _, _ in assigned)
    no_pe = [i for i, f in enumerate(plants) if not f["properties"].get("godk_pe")]
    fict = [i for i, f in enumerate(plants) if "fiktiv" in (f["properties"].get("pkt_navn") or "").lower()]
    names = collections.Counter(f["properties"].get("pkt_navn") for f in plants)
    twice = sorted(n for n, c in names.items() if c > 1)
    ptypes = collections.Counter(f["properties"].get("pkt_type") for f in plants)
    reach_ew = 4 * CELL * 111.2 * math.cos(math.radians(56.0))
    rings = int(MAX_ASSIGN_KM / (CELL * 111.0)) + 1

    # ---- bathing: labels, matching, pooling
    label_n = collections.Counter()
    label_years = collections.defaultdict(set)
    for f in bath:
        for y in YEARS:
            v = f["properties"].get("quality_" + y)
            label_n[v if v is not None else "(empty)"] += 1
            if v is not None:
                label_years[v].add(YEAR_NUM[y])
    span = {k: [min(v), max(v)] for k, v in label_years.items()}
    unmatched = collections.Counter()
    for f in bath:
        p = f["properties"]
        if any(p.get("quality_" + y) in SCORE for y in YEARS) and p.get("wbid") not in wb_ids:
            w = p.get("wbid")
            unmatched["DKLAKE… (a lake code)" if isinstance(w, str) and w.upper().startswith("DKLAKE")
                      else ("(empty)" if w is None else w)] += 1
    n_matched = sum(1 for s in st if s["wb"])
    one_station = sum(1 for w, v in per.items() if len(v) == 1)
    zero_area = sum(1 for w, v in per.items() if len(v) >= 2 and not rec[w]["area_km2"])
    lake_i = next(i for i, f in enumerate(bath)
                  if str(f["properties"].get("wbid") or "").upper().startswith("DKLAKE"))
    odd_i = next(i for i, f in enumerate(bath) if f["properties"].get("wbid") not in wb_ids
                 and not str(f["properties"].get("wbid") or "").upper().startswith("DKLAKE"))
    sy = {i: sum(len(s["s"]) for s in per[i]) for i in ids}

    def share(i, keep=lambda y: True, hit=lambda q: q < 4):
        v = [q for s in per[i] for y, q in s["s"].items() if keep(y)]
        return round(sum(1 for q in v if hit(q)) / len(v), 3) if v else None

    # where the spread lives, by place: station shares within and between bodies
    stn = [(i, sum(1 for q in s["s"].values() if q < 4) / len(s["s"])) for i in ids for s in per[i]]
    grand = sum(v for _, v in stn) / len(stn)
    mean_of = {i: sum(v for j, v in stn if j == i) / sum(1 for j, _ in stn if j == i) for i in ids}
    ssw = sum((v - mean_of[i]) ** 2 for i, v in stn)
    ssb = sum((mean_of[i] - grand) ** 2 for i, _ in stn)

    # ---- reruns, each with one imposed choice changed
    R = {}
    g10 = [A.nearest(*centroid(f["geometry"]), max_km=10.0) for f in plants]
    R["R1"] = pearson([math.log10(1 + pe_by(g10).get(r["id"], 0) / r["area"]) for r in rows], y0)
    gx = [_nearest_exhaustive(A, *centroid(f["geometry"]), MAX_ASSIGN_KM) for f in plants]
    moved = sum(1 for a, b in zip(got, gx) if a[0] is not None and b[0] is not None and a[0] != b[0])
    gained = sum(1 for a, b in zip(got, gx) if a[0] is None and b[0] is not None)
    lost10 = sum(1 for a, b in zip(got, g10) if a[0] is not None and b[0] is None)
    pex = pe_by(gx)
    R["R2"] = pearson([math.log10(1 + pex.get(r["id"], 0) / r["area"]) for r in rows], y0)
    R["R3"] = pearson([r["pe_per_km2"] for r in rows], y0)
    R["R4"] = pearson(x0, [share(i, hit=lambda q: q == 1) for i in ids])
    late = [(x, share(i, keep=lambda y: y >= 2011)) for x, i in zip(x0, ids)]
    late = [(x, y) for x, y in late if y is not None]
    R["R5"] = pearson([a for a, _ in late], [b for _, b in late])
    ones = [r for r in rec.values() if (r["observation"].get("bathing") or {}).get("stations", 0) >= 1
            and r["area_km2"]]
    R["R6"] = pearson([math.log10(1 + r["pressure"].get("rens", {}).get("pe", 0) / r["area_km2"])
                       for r in ones], [r["observation"]["bathing"]["sub_excellent_share"] for r in ones])
    R["R7"] = pearson(_ranks(x0), _ranks(y0))
    pos = [(x, y) for x, y in zip(x0, y0) if x > 0]
    R["R8"] = pearson([a for a, _ in pos], [b for _, b in pos])
    rr = {k: (None if v is None else round(v, 3)) for k, v in R.items()}
    tested = lambda *ks: "; ".join(f"{k}: r = {rr[k]:+.3f}" for k in ks)

    L = lineage.Lineage("cum_hoc_r", number={
        "file": "data/derived/areas.json", "path": f"cum_hoc.tests.{LINEAGE_TEST}.r",
        "value": t["r"], "n": t["n"], "predictor": t["predictor"], "outcome": t["outcome"],
        "unrounded": c0,
        "says": ("The Pearson correlation, across the marine water bodies with two or more "
                 "bathing stations, between log10(1 + approved treatment-plant person-"
                 "equivalents per km² of water body) and the share of station-years whose "
                 "bathing class is not \"Excellent\"."),
        "producer": "scripts/areas.py", "page": "docs/AREAS.md",
        "page_line": lines("scripts/pages/areas.py", 'for t in ch["tests"]:', "{t['n']} |"),
        "page_note": "The page prints the stored value with a sign and three decimals: "
                     "the only arithmetic after the producer."})

    # ---- the records, in their own words
    def mwhere(f):
        c = f["geometry"]["coordinates"]
        return {"geometry": f["geometry"]["type"], "vertices": sum(len(r) for p in c for r in p),
                "first_vertex": c[0][0][0]}
    L.record("marin_overordnet", P_MARINE, marine,
             columns=["ov_id", "ov_navn", "ov_stoe", "geometry (every 4th boundary vertex)"],
             published_by=SERVED, fetched_from=fetched("vp3_basis_2019_marin_overordnet"),
             props=lambda f: f["properties"], where=mwhere, file_meta=meta(mdoc),
             pick=lambda rs: [0, 1, 2],
             marked=["`ov_id` is a water-body code: the unit this number is counted in is "
                     "this code, imposed by whoever drew the partition.",
                     "The geometry is a boundary someone drew. Which authority drew it, and on "
                     "what basis any one line was set, is not recorded in the file.",
                     "`ov_stoe` is an area the layer states. The file carries no unit for it; "
                     "areas.py takes it as km² and does not recompute it from the geometry."])
    L.record("punkt_rens_udl", P_RENS, plants, columns=["godk_pe", "geometry (Point)"],
             published_by=SERVED, fetched_from=fetched("vp3_basis_2019_punkt_rens_udl"),
             props=lambda f: f["properties"], file_meta=meta(pdoc),
             where=lambda f: {"geometry": f["geometry"]["type"],
                              "coordinates": f["geometry"]["coordinates"]},
             pick=lambda rs: [0, 1, 2] + [i for i in fict if i in no_pe][:1],
             marked=["`godk_pe` is an approved figure in person-equivalents (`godk`). The file "
                     "states neither the approval behind it nor what one person-equivalent is; "
                     "both are constructions made before this file.",
                     f"`pkt_type` reads {dict(ptypes)} across the {len(plants)} rows; the layer "
                     "is named `punkt_rens_udl`, one point per row.",
                     f"{len(fict)} rows are named by the layer itself as fictitious (\"fiktivt\" "
                     f"or \"fiktiv\" in `pkt_navn`); {sum(1 for i in fict if i not in no_pe)} of "
                     "them carry a `godk_pe`.",
                     f"{len(no_pe)} rows have no `godk_pe`."])
    L.record("badevand", P_BATH, bath,
             columns=["id", "wbid"] + ["quality_" + y for y in YEARS],
             published_by=SERVED, fetched_from=fetched("vp3basis2019_badevand"),
             props=lambda f: f["properties"], file_meta=meta(bdoc),
             pick=lambda rs: [0, 1, lake_i, odd_i],
             marked=["`wbid` is the water-body code the layer gives each station: a category "
                     "imposed when the layer was compiled, by someone the file does not name. "
                     f"{sum(unmatched.values())} stations with a scored year carry a `wbid` that "
                     "matches no `ov_id` in the marine layer exactly.",
                     "`quality_91` … `quality_18` hold one class per station per year. The rule "
                     "that makes a class, and who set it, are not in the file, and no copy of "
                     "such a rule is pinned in this repository. The label set changes: "
                     + "; ".join(f"\"{k}\" appears {v[0]}–{v[1]}" for k, v in sorted(span.items())) + ".",
                     f"\"Not classified\" ({label_n.get('Not classified', 0)}) and empty "
                     f"({label_n.get('(empty)', 0)}) station-years are in the file; areas.py drops them."])

    # ---- the steps, from the records up to r
    wq, wref = say("So this script refuses the aggregate", "exists, and - stated as plainly")
    L.step("S1", "identity", "A water body is one feature of the marine layer",
           [lines(build, 'props = [f["properties"] for f in marine]', 'wb_ids = {p["ov_id"]'),
            lines(build, '"id": p["ov_id"], "name": p["ov_navn"], "area_km2": p["ov_stoe"],')],
           imposes="Every feature of `marin_overordnet` is one water body, keyed by its `ov_id`; "
                   "everything below is counted per `ov_id`.",
           inputs=[{"file": rel(P_MARINE), "columns": ["ov_id", "ov_navn", "ov_stoe"], "rows": len(marine)}],
           outputs={"water_bodies": len(props)}, branch="water bodies",
           why=wq, why_ref=wref,
           author="the partition: not recorded in the file; using it as the unit: " + ME,
           alternative="positions (the station), or a partition drawn for this variable",
           counted_as_one=f"One water body = one feature of `marin_overordnet`, keyed by `ov_id` "
                          f"({len(props)} of them).")
    L.step("S2", "identity", "A treatment plant is one row of the plant layer",
           [src('("punkt_rens_udl", "rens"'), lines(build, "for f in feats:", "lat, lon = centroid")],
           imposes="Every row of `punkt_rens_udl` is one plant, placed at its one point. "
                   f"{len(twice)} `pkt_navn` values occur twice ({', '.join(twice)}), each time in a "
                   "different `komm_navn`; each row counts on its own.",
           inputs=[{"file": rel(P_RENS), "columns": ["godk_pe", "geometry"], "rows": len(plants)}],
           outputs={"plants": len(plants)}, branch="pressure", author=ME,
           counted_as_one="One treatment plant = one row of `punkt_rens_udl`: one point, one `godk_pe`.")
    aq, aref = say("Assignment is by nearest point on the marine boundary",
                     "shore; dumping grounds sit in the water. One rule")
    L.step("S3", "grouping", "Each plant goes to the water body with the nearest boundary vertex, within 20 km",
           [src("CELL = 0.05", "MAX_ASSIGN_KM = 20.0"),
            lines(Assigner.__init__, "for x, y in ring[::STRIDE]:", "self.grid[(int(y / CELL)"),
            lines(Assigner.nearest, "cy, cx = int(lat / CELL)", "return None, None"),
            lines(build, "far = 0", "far += 1")],
           imposes=("A plant belongs to the water body owning the nearest kept boundary vertex "
                    f"(every {STRIDE}th vertex, `STRIDE`; {len(A.lat):,} kept), and to none if no "
                    f"vertex is found within `MAX_ASSIGN_KM` = {MAX_ASSIGN_KM:.0f} km. The search walks "
                    f"square rings of {CELL}° grid cells out from the plant's cell, {rings} rings at "
                    "most, and stops after the first ring beyond its own cell in which it met any "
                    f"vertex. A cell is {CELL}° of longitude wide, so east–west the {rings} rings reach "
                    f"about {reach_ew:.1f} km at 56° N, not {MAX_ASSIGN_KM:.0f}: a plant "
                    f"{reach_ew:.0f}–{MAX_ASSIGN_KM:.0f} km east or west of the nearest boundary is "
                    "dropped as if it were beyond 20 km, and a nearer vertex in an outer ring can "
                    "lose to a farther one in an inner ring. What the plant discharges into is not "
                    "read; the layer has no column for it."),
           inputs=[{"file": rel(P_RENS), "columns": ["geometry"], "rows": len(plants)},
                   {"file": rel(P_MARINE), "columns": ["geometry"], "rows": len(marine),
                    "vertices_kept": len(A.lat)}],
           outputs={"assigned": len(assigned), "dropped_no_vertex_found": len(plants) - len(assigned),
                    "water_bodies_with_a_plant": len({w for _, w, _ in assigned}),
                    "distance_km_of_assigned": _quart([d for _, _, d in assigned], 2),
                    "godk_pe_in_file": pe_file, "godk_pe_assigned": pe_kept,
                    "godk_pe_dropped": pe_file - pe_kept},
           branch="pressure", why=aq + " For the value 20 km itself: no reason recorded; its "
           "comment says only what it does (\"beyond this a point belongs to no marine area\").",
           why_ref=aref, author=ME,
           alternative="the receiving water named in each plant's discharge permit, or the "
                       "drainage path to the sea; a shorter or longer distance; the exhaustive "
                       "nearest-vertex search the docstring describes",
           tested=tested("R1", "R2"),
           counted_as_one="A plant belongs to the water body whose boundary is nearest to its point, "
                          "whatever its effluent reaches.")
    L.step("S4", "convention", "Sewage pressure is the sum of approved person-equivalents",
           lines(build, "if key == \"rens\":", 'r["pe"] = r.get("pe", 0) + (q.get("godk_pe") or 0)'),
           imposes="A water body's sewage pressure is the sum of `godk_pe` over the plants assigned to "
                   "it: an approved capacity, not a measured or modelled load. Treatment stage "
                   "(`rens_sta`) is counted into `stages` but does not enter the pressure.",
           inputs=[{"file": rel(P_RENS), "columns": ["godk_pe"], "rows": len(assigned)}],
           outputs={"water_bodies_with_pe_above_0": sum(1 for r in rec.values()
                                                        if r["pressure"].get("rens", {}).get("pe")),
                    "of_the_test_rows": sum(1 for r in rows if r["pe_per_km2"] > 0)},
           branch="pressure", author=ME,
           alternative="the number of plants; PE weighted by treatment stage (`rens_sta` is in the "
                       "layer); a measured or modelled discharge, which this layer does not carry",
           counted_as_one="One approved person-equivalent (`godk_pe`) = one unit of sewage pressure, "
                          "whatever the plant treats, however it treats it, and wherever its effluent goes.")
    L.step("S5", "filling in", "No value, or no plant, counts as zero",
           [lines(build, 'r["pe"] = r.get("pe", 0) + (q.get("godk_pe") or 0)'),
            lines(cum_hoc, 'rens = r["pressure"].get("rens", {})'),
            lines(cum_hoc, '"pe_per_km2": rens.get("pe", 0) / r["area_km2"],')],
           imposes="A plant with no `godk_pe` adds 0. A water body with no plant assigned gets a "
                   "pressure of 0 - which is also what it gets if its plants sit 12-20 km "
                   "east or west of the boundary (S3).",
           inputs=[{"file": rel(P_RENS), "columns": ["godk_pe"], "rows": len(plants)}],
           outputs={"plants_without_godk_pe": len(no_pe),
                    "of_them_assigned": sum(1 for i in no_pe if got[i][0] is not None),
                    "test_rows_with_zero_pressure": sum(1 for r in rows if r["pe_per_km2"] == 0)},
           branch="pressure", author=ME,
           alternative="leave such water bodies out (R8), or mark a missing `godk_pe` as unknown",
           tested=tested("R8"),
           counted_as_one="A missing `godk_pe`, and a water body with no plant assigned, both = zero pressure.")
    L.step("S6", "convention", "Pressure is divided by the water body's stated area",
           [lines(build, '"id": p["ov_id"], "name": p["ov_navn"], "area_km2": p["ov_stoe"],'),
            lines(cum_hoc, '"pe_per_km2": rens.get("pe", 0) / r["area_km2"],')],
           imposes="PE per km² of sea surface, using `ov_stoe` as the area; a large open-water body "
                   "and a small fjord with the same plants get very different values.",
           inputs=[{"file": rel(P_MARINE), "columns": ["ov_stoe"], "rows": len(rows)}],
           outputs={"pe_per_km2": _quart([r["pe_per_km2"] for r in rows], 2)},
           branch="pressure", author=ME,
           alternative="per km of coastline, per volume or flushing time, or not divided at all")
    L.step("S7", "identity", "A bathing station is one row of the bathing layer",
           lines(load_bathing, "for p in (f[\"properties\"] for f in doc[\"features\"]):", "return st"),
           imposes="Every row of `badevand` is one station with one class per year; a row with no "
                   "scored year is not a station here.",
           inputs=[{"file": rel(P_BATH), "columns": ["id", "wbid", "quality_91 … quality_18"],
                    "rows": len(bath)}],
           outputs={"rows_in_file": len(bath), "stations_with_a_scored_year": len(st)},
           branch="outcome", author=ME,
           counted_as_one="One bathing station = one row of `badevand` (its `id`).")
    L.step("S8", "selection", "Which yearly classes count",
           [src('YEARS = [f"{y:02d}"', "YEAR_NUM = {y:"), src("SCORE = {"),
            lines(load_bathing, 's = {YEAR_NUM[y]: SCORE[p["quality_" + y]]', "if s:")],
           imposes="A station-year counts when its `quality_YY` is one of the SCORE labels; "
                   "\"Not classified\" and empty years are dropped.",
           inputs=[{"file": rel(P_BATH), "columns": ["quality_" + y for y in YEARS],
                    "rows": len(bath), "station_years": len(bath) * len(YEARS)}],
           outputs={"station_years_by_label": dict(label_n.most_common()),
                    "kept": sum(v for k, v in label_n.items() if k in SCORE),
                    "dropped": sum(v for k, v in label_n.items() if k not in SCORE)},
           branch="outcome", author=ME)
    L.step("S9", "classification", "The labels, and the scores put on them",
           src("SCORE = {"),
           imposes="The file's labels are used as they are written. \"Good or Sufficient\", which the "
                   f"file uses {span.get('Good or Sufficient', ['?', '?'])[0]}–"
                   f"{span.get('Good or Sufficient', ['?', '?'])[1]}, is scored 3, the same as "
                   f"\"Good\", which appears from {span.get('Good', ['?'])[0]}.",
           inputs=[{"file": rel(P_BATH), "columns": ["quality_" + y for y in YEARS], "rows": len(bath)}],
           outputs={"score": SCORE, "label_years": span},
           branch="outcome", author="the labels: not recorded in the file or in this repository; "
                                    "the scores: " + ME,
           alternative="score each label regime on its own; use only 2011–2018, one label set (R5)",
           tested=tested("R5"),
           counted_as_one="\"Good or Sufficient\" (to 2010) = \"Good\" (from 2011) = score 3.")
    L.step("S10", "grouping", "Each station goes to the water body its own `wbid` names",
           [lines(load_bathing, '"wb": p.get("wbid") if p.get("wbid") in wb_ids else None,'),
            lines(build, "for s in st:", 'per[s["wb"]].append(s)')],
           imposes="A station belongs to the water body whose `ov_id` equals its `wbid` exactly; any "
                   "other `wbid` - a lake code, a code spelt differently, a stray value - puts it in "
                   "none. This is the dataset's own category, not the distance rule: the module "
                   "docstring says bathing stations are assigned with the plants' rule (\"One rule, "
                   "one distance\"), and the code does not do that.",
           inputs=[{"file": rel(P_BATH), "columns": ["wbid"], "rows": len(st)}],
           outputs={"stations_matched": n_matched, "stations_unmatched": len(st) - n_matched,
                    "unmatched_wbid": dict(unmatched.most_common()),
                    "water_bodies_with_a_station": len(per)},
           branch="outcome", author="`wbid`: not recorded in the file; using it: " + ME,
           alternative="the distance rule used for the plants, or a spelling-tolerant match")
    L.step("S11", "convention", "\"Sub-excellent\" is any class below \"Excellent\"",
           lines(build, '"sub_excellent_share": round(', "p[1] < 4) / len(allpairs), 3),"),
           imposes="The outcome is the share of pooled station-years scored below 4, rounded to three "
                   "decimals before the correlation; \"Good\", \"Sufficient\", \"Good or Sufficient\" "
                   "and \"Poor\" count alike.",
           inputs=[{"from": "S9, S10", "rows": sum(sy.values())}],
           outputs={"sub_excellent": _quart(y0, 3)},
           branch="outcome", author=ME,
           alternative="the share \"Poor\" (R4); the mean score (the page's next row, tests[3])",
           tested=tested("R4"),
           counted_as_one="Every class other than \"Excellent\" = one outcome, \"sub-excellent\".")
    L.step("S12", "identity", "Station-years are pooled across stations and years",
           lines(build, 'allpairs = [(y, s["s"][y]) for s in v for y in s["s"]]'),
           imposes="All classed years of all stations in a water body, 1991–2018, go into one share; "
                   "a station classed in 28 years weighs 28 times a station classed once, and the two "
                   "label regimes (S9) are pooled.",
           inputs=[{"from": "S10", "stations": sum(len(per[i]) for i in ids)}],
           outputs={"station_years_in_test": sum(sy.values()),
                    "classed_years_per_station": _quart([len(s["s"]) for i in ids for s in per[i]], 1)},
           branch="outcome", author=ME,
           alternative="average the stations' own shares; one period only (R5)",
           counted_as_one="One station-year = one member of a water body's share, every station and "
                          "every year 1991–2018 pooled.")
    sq, sref = quote(cum_hoc, "This is a correlation across areas at one time", "aggregate has one.")
    L.step("S13", "selection", "Which water bodies enter the correlation",
           lines(cum_hoc, 'b = r["observation"].get("bathing")', "continue"),
           imposes="A water body enters when it has two or more bathing stations and a nonzero area.",
           inputs=[{"from": "S1, S10", "rows": len(rec)}],
           outputs={"water_bodies": len(rec), "no_bathing_station": len(rec) - len(per),
                    "one_station": one_station, "zero_area": zero_area, "kept": len(rows)},
           branch="the correlation", why=sq + " For the minimum of two stations: no reason recorded.",
           why_ref=sref, author=ME, alternative="one station or more (R6); three informative stations",
           tested=tested("R6"))
    L.step("S14", "functional form", "The pressure is taken as log10(1 + x)",
           lines(cum_hoc, 'for pred in ("outfalls_per_km2", "pe_per_km2", "basin_m3_per_km2"):',
                 "x = [math.log10(1 + r[pred]) for r in rows]"),
           imposes="x = log10(1 + PE per km²). The 1 is added in the units of PE per km², so it "
                   "decides where water bodies with little pressure sit relative to those with none.",
           inputs=[{"from": "S6", "rows": len(rows)}],
           outputs={"x": _quart(x0)},
           branch="the correlation", author=ME,
           alternative="no transform (R3); ranks (R7); another offset", tested=tested("R3", "R7"))
    cq, cref = say("The cross-sectional estimate at the end is a cum hoc", "comparable observation.")
    L.step("S15", "functional form", "Pearson's r across water bodies, each one point",
           [lines(pearson, "def pearson(u, v):", "return sum("),
            lines(cum_hoc, "y = [r[outcome] for r in rows]", '"r2": round(c * c, 3), "n": len(rows)})')],
           imposes="A straight-line association between x and y, every water body weighted equally "
                   "whatever its area or number of stations; rounded to three decimals.",
           inputs=[{"from": "S11, S14", "rows": len(rows)}],
           outputs={"r": t["r"], "r_unrounded": round(c0, 6), "r2": t["r2"], "n": t["n"]},
           branch="the correlation", why=cq, why_ref=cref, author=ME,
           alternative="rank correlation (R7); weighting by stations or area",
           tested=tested("R7"),
           counted_as_one="One water body = one point in the correlation, whatever its area or its "
                          "number of stations.")

    # ---- where each branch ends
    L.end("outcome", "record", "`quality_YY` as written in `badevand`, one per station per year, "
          "with the station's `wbid`", record="badevand", author="not recorded in the file",
          steps=["S7", "S8", "S10"])
    L.end("outcome", "construction", "the bathing classes themselves (\"Excellent\" … \"Poor\", and "
          "\"Good or Sufficient\" to 2010): a class rule someone set", record="badevand",
          author="not recorded in the file or in this repository", steps=["S9"])
    L.end("outcome", "construction", "`wbid`: the water-body code each station was filed under",
          record="badevand", author="not recorded in the file", steps=["S10"])
    L.end("pressure", "record", "`godk_pe` and the point, as written in `punkt_rens_udl`",
          record="punkt_rens_udl", author="not recorded in the file", steps=["S2", "S4"])
    L.end("pressure", "construction", "the person-equivalent, and the approval that sets each "
          "`godk_pe`", record="punkt_rens_udl", author="not recorded in the file", steps=["S4"])
    L.end("water bodies", "record", "`ov_id` and `ov_stoe` as written in `marin_overordnet`",
          record="marin_overordnet", author="not recorded in the file", steps=["S1", "S6"])
    L.end("water bodies", "construction", "the marine water-body polygons: boundaries someone drew",
          record="marin_overordnet", author="not recorded in the file; the layer is served under "
          "vp3basis2019", steps=["S1", "S3"])
    L.end("pressure", "construction", f"`MAX_ASSIGN_KM` = {MAX_ASSIGN_KM:.0f}, `STRIDE` = {STRIDE}, "
          f"`CELL` = {CELL}: the assignment's distances", author=ME + "; no reason recorded for 20 km",
          steps=["S3"])
    L.end("the correlation", "construction", "two stations, the 1 in log10(1 + x), the line at "
          "\"Excellent\", Pearson's r", author=ME + "; no reason recorded for any of these values",
          steps=["S11", "S13", "S14", "S15"])
    L.note("model_output", "None found on this chain. `godk_pe` is an approved figure, the classes "
           "are labels the file carries, and the areas are the layer's own. Whether a class was "
           "computed from measured samples, and how, is not stated in the file.")

    # ---- the spread first: every pair behind r
    pairs = [{"id": r["id"], "name": r["name"], "area_km2": r["area"], "stations": len(per[r["id"]]),
              "station_years": sy[r["id"]], "plants": rec[r["id"]]["pressure"].get("rens", {}).get("n", 0),
              "pe": rec[r["id"]]["pressure"].get("rens", {}).get("pe", 0),
              "pe_per_km2": round(r["pe_per_km2"], 3), "x": round(x, 4), "y": y}
             for r, x, y in zip(rows, x0, y0)]
    pairs.sort(key=lambda p: (p["x"], p["y"]))
    top = lambda k, rev: [p["id"] for p in sorted(pairs, key=lambda p: p[k], reverse=rev)[:5]]
    L.spread(n=len(pairs), x_label="log10(1 + pe_per_km2)",
             y_label="sub_excellent: share of station-years below \"Excellent\"",
             x=_quart(x0), y=_quart(y0, 3),
             zero_x=sum(1 for p in pairs if p["x"] == 0),
             tails={"highest_x": top("x", True), "highest_y": top("y", True),
                    "lowest_y": top("y", False)},
             dropped={
                 "water_bodies_left_out": len(rec) - len(rows),
                 "within_between": {
                     "stations": len(stn), "ss_within": round(ssw, 4), "ss_between": round(ssb, 4),
                     "share_within": round(ssw / (ssw + ssb), 3),
                     "what": "Each station's own share of sub-excellent years, split into variance "
                             "among the stations of one water body and variance between water "
                             "bodies. r sees only one pooled share per water body."},
                 "line": f"The line through the {len(pairs)} pairs accounts for r² = {t['r2']} of the "
                         "variance of their shares."},
             where={"place": "within against between water bodies, above",
                    "time": "one period only, 2011–2018: rerun R5",
                    "depth, season": "not applicable: one class per station per year"},
             pairs=pairs)

    # ---- robustness
    L.rerun("R1", f"maximum assignment distance {MAX_ASSIGN_KM:.0f} km → 10 km (same search)",
            {"step": "S3", "MAX_ASSIGN_KM": [MAX_ASSIGN_KM, 10.0]}, rr["R1"], len(rows), "S3",
            headline=True, note=f"{lost10} plants that were assigned at 20 km are assigned to none at 10 km.")
    L.rerun("R2", "exhaustive nearest vertex within a true 20 km, east-west as well as north-south",
            {"step": "S3", "search": ["rings stop early; ~12 km east-west", "every cell within 20 km"]},
            rr["R2"], len(rows), "S3",
            note=f"{gained} plants dropped by the search are within 20 km of a boundary; {moved} "
                 "assigned plants change water body.")
    L.rerun("R3", "no log transform: x = pe_per_km2", {"step": "S14"}, rr["R3"], len(rows), "S14")
    L.rerun("R4", "outcome threshold moved: share of station-years \"Poor\"", {"step": "S11"},
            rr["R4"], len(rows), "S11")
    L.rerun("R5", "one label set: station-years 2011–2018 only", {"step": "S9, S12"},
            rr["R5"], len(late), "S9")
    L.rerun("R6", "one bathing station or more, instead of two", {"step": "S13"},
            rr["R6"], len(ones), "S13")
    L.rerun("R7", "rank (Spearman) correlation instead of Pearson", {"step": "S14, S15"},
            rr["R7"], len(rows), "S15")
    L.rerun("R8", "only water bodies with pressure above zero", {"step": "S5"},
            rr["R8"], len(pos), "S5")

    L.aside("`punkt_rbu_udl` (rain-conditioned outfalls)", "read by areas.py and assigned by the same "
            "rule, but it enters tests 0, 1, 4 and 5, not this one")
    L.aside("`punkt_havdam_udl`, `klappladser`, `raastofomr`, `sw_mfs_tilstand`, "
            "`data/manual/statistical_models.json`", "read by areas.py; nothing from them reaches this number")
    L.aside("`rens_sta` (treatment stage)", "counted into each water body's `stages`, not into the pressure")
    return L.write()


def main():
    props, rec = build()
    ch = cum_hoc(rec)
    write_json(OUT_JSON, {"assignment": {"rule": "nearest marine boundary vertex",
                                         "max_km": MAX_ASSIGN_KM},
                          "summary": summarize(rec), "hazardous_layer": hazardous_layer(),
                          "cum_hoc": ch, "areas": rec})
    # after areas.json is written, so the record of how it was made cannot alter it
    log(f"wrote {os.path.relpath(record_cum_hoc_r(rec, ch), ROOT)}")
    nothing = [r for r in rec.values()
               if not r["has_statistical_model"] and not r["observation"].get("bathing")]
    log(f"\nwrote {os.path.relpath(OUT_JSON, ROOT)} - now run scripts/pages/areas.py")
    log(f"  {len(rec)} areas; {sum(1 for r in rec.values() if r['has_statistical_model'])} "
        f"modelled; {len(nothing)} with neither model nor observation")
    for t in ch["tests"]:
        log(f"  {t['predictor']:28} -> {t['outcome']:15} r={t['r']:+.3f} n={t['n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
