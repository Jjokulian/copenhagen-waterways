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
    for p in (f["properties"] for f in
              read_json(os.path.join(NAT, "badevand.geojson"))["features"]):
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
    marine = read_json(os.path.join(NAT, "marin_overordnet.geojson"))["features"]
    props = [f["properties"] for f in marine]
    wb_ids = {p["ov_id"] for p in props}
    idx = {p["ov_id"]: i for i, p in enumerate(props)}

    log("building the boundary index")
    A = Assigner(marine)

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
        feats = read_json(path)["features"]
        far = 0
        for f in feats:
            lat, lon = centroid(f["geometry"])
            w, d = A.nearest(lat, lon)
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


def main():
    props, rec = build()
    ch = cum_hoc(rec)
    write_json(OUT_JSON, {"assignment": {"rule": "nearest marine boundary vertex",
                                         "max_km": MAX_ASSIGN_KM},
                          "summary": summarize(rec), "hazardous_layer": hazardous_layer(),
                          "cum_hoc": ch, "areas": rec})
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
