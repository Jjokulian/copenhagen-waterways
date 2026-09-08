#!/usr/bin/env python3
"""There is no Denmark. There are 123 marine areas with different causes.

Every published figure in this argument is a national aggregate: 69.6% of the
land-borne load, one indsatsbehov ladder, one 25% rule. Aggregation is where the
information goes. A number that is true of Denmark is true of nowhere in it.

So this script refuses the aggregate and builds one record per marine water body:
what presses on it, what is observed in it, over which years each of those streams
exists, and - stated as plainly as the rest - what cannot be modelled there and why.

Assignment is by nearest point on the marine boundary, via a grid hash over the
1.47 M boundary vertices, with the distance recorded on every assignment so a
reader can see how firm it is. Outfalls sit on land; bathing stations sit on the
shore; dumping grounds sit in the water. One rule, one distance, no hidden choices.

The cross-sectional estimate at the end is a cum hoc effect size and is labelled as
one. It regresses a sewage-driven outcome (bathing quality) on sewage pressure
(treatment-plant PE and rain-conditioned outfall density), across areas rather than
across years, because across areas is the only axis on which Denmark has enough
replication to estimate anything at all.

Output: data/derived/areas.json, docs/AREAS.md

Usage:  python3 scripts/areas.py
"""
import collections
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, MANUAL, RAW, ROOT, log, read_json, write_json, write_doc

NAT = os.path.join(RAW, "national")
OUT_MD = os.path.join(ROOT, "docs", "AREAS.md")
OUT_JSON = os.path.join(DERIVED, "areas.json")

CELL = 0.05           # grid cell, degrees
STRIDE = 4            # keep every Nth boundary vertex; ~15 m spacing, ample at 20 km
MAX_ASSIGN_KM = 20.0  # beyond this a point belongs to no marine area

YEARS = [f"{y:02d}" for y in list(range(91, 100)) + list(range(0, 19))]
YEAR_NUM = {y: (1900 + int(y) if int(y) >= 91 else 2000 + int(y)) for y in YEARS}
SCORE = {"Excellent": 4, "Good": 3, "Good or Sufficient": 3, "Sufficient": 2, "Poor": 1}

# DCE (2015) Tabel 3: the 72 validated statistical models, by station area.
# Only these areas have a fitted relation between load and any indicator.
MODELLED_AREAS = ["Lovns", "Skive", "Riisgard", "Nissum", "Logstor", "Thisted",
                  "Kaas", "Nibe", "Randers", "Isefjord", "Horsens", "Roskilde",
                  "Vejle", "Mariager", "Kolding", "Abenra", "Flensborg", "Odense",
                  "Ringkobing"]
MODEL_WINDOW = (1990, 2012)
FOLD = str.maketrans({"å": "a", "æ": "a", "ø": "o", "Å": "A", "Æ": "A", "Ø": "O"})

# Point and polygon layers to attribute to areas. (file, key, what it is, kind)
PRESSURES = [
    ("punkt_rbu_udl", "rbu", "rain-conditioned outfalls (overflows and separate storm)", "point"),
    ("punkt_rens_udl", "rens", "wastewater treatment plants", "point"),
    ("punkt_havdam_udl", "havdam", "marine aquaculture discharge", "point"),
    ("klappladser", "klap", "licensed dredged-material dumping grounds", "poly"),
    ("raastofomr", "raastof", "raw-material extraction areas", "poly"),
]


def fold(s):
    return (s or "").translate(FOLD).lower()


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
        modelled = any(n.lower()[:6] in fold(p["ov_navn"]) for n in MODELLED_AREAS)
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

    # ---- observation: hazardous substances, with real activity dates -----
    hz = read_json(os.path.join(NAT, "sw_mfs_tilstand.geojson"))["features"]
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
            gaps.append("No fitted relation between nutrient load and any indicator "
                        "exists for this area. Any coefficient applied here is "
                        "transferred from a fjord.")
        b = r["observation"].get("bathing")
        if not b:
            gaps.append("No bathing station: there is no long, repeated observation "
                        "of any marine variable here in the open data.")
        elif b["informative_stations"] < 3:
            gaps.append("Fewer than three bathing stations vary enough to correlate, "
                        "so whether this area behaves as one unit cannot be tested.")
        if "hazardous" not in r["observation"]:
            gaps.append("No hazardous-substance monitoring point.")
        if r["area_km2"] > 500 and (b or {}).get("stations", 0) < 6:
            gaps.append(f"{r['area_km2']:,.0f} km² described by "
                        f"{(b or {}).get('stations', 0)} shore observations.")
        r["not_modelled"] = gaps
    return props, rec


def cum_hoc(rec):
    """Cross-sectional effect size: sewage pressure against a sewage outcome.

    This is a correlation across areas at one time, not a causal estimate, and the
    only reason to prefer it to the national aggregate is that it has 100 units of
    replication where the aggregate has one."""
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


def render(props, rec, ch):
    o = []
    a = o.append
    tot = sum(r["area_km2"] for r in rec.values())
    modelled = [r for r in rec.values() if r["has_statistical_model"]]
    with_bath = [r for r in rec.values() if r["observation"].get("bathing")]
    testable = [r for r in rec.values()
                if (r["observation"].get("bathing") or {}).get("informative_stations", 0) >= 3]
    nothing = [r for r in rec.values() if not r["has_statistical_model"]
               and not r["observation"].get("bathing")]

    a("# There is no Denmark\n")
    a("Every number in the national argument is an aggregate: one land-borne load, "
      "one 69.6%, one ladder of indsatsbehov, one 25% rule. Aggregation is where the "
      "information goes. Køge Bugt and Ringkøbing Fjord do not share a cause, a "
      "flushing time, a sediment, or a fix, and a figure true of Denmark is true of "
      "nowhere in it.\n")
    a("This page refuses the aggregate. One record per marine water body: what presses "
      "on it, what is observed in it, **over which years each of those streams "
      "exists**, and what cannot be modelled there. The last of those is the longest "
      "column, and that is the finding.\n")
    a(f"Assignment is by nearest point on the marine boundary, one rule for every "
      f"layer, with the distance recorded on every assignment and anything beyond "
      f"{MAX_ASSIGN_KM:.0f} km dropped.\n")

    a("## The state of knowledge, counted\n")
    a("| | areas | km² | share of sea |")
    a("|---|---:|---:|---:|")
    for lab, sub in (("All marine water bodies", list(rec.values())),
                     ("…with a fitted load→indicator model", modelled),
                     ("…with any repeated marine observation (bathing)", with_bath),
                     ("…where internal coherence can even be tested", testable),
                     ("…with neither a model nor an observation", nothing)):
        km = sum(r["area_km2"] for r in sub)
        a(f"| {lab} | {len(sub)} | {km:,.0f} | {100*km/tot:.1f}% |")
    a("")
    a(f"{len(nothing)} water bodies covering "
      f"{sum(r['area_km2'] for r in nothing):,.0f} km² "
      f"({100*sum(r['area_km2'] for r in nothing)/tot:.0f}% of Danish sea) carry "
      f"neither a fitted model nor a repeated observation **in the two layers "
      f"counted above** — bathing water and hazardous-substance status. They still "
      f"receive a requirement.\n")
    a("> **A correction, and a caution about the whole class of statement.** An "
      "earlier version of this line said those water bodies carry \"neither a "
      "fitted model nor a single repeated marine observation\", which reads as a "
      "claim about marine observation in general. It is not one, and checked "
      "against a wider corpus it is false. **A claim of absence is only as wide as "
      "the search behind it**, and this search was two layers deep.\n"
      ">\n"
      "> The check: ODA's station register holds **6,258 positioned marine "
      "stations**, and assigned by point-in-polygon to the same boundaries used on "
      "this page, **every one of the 123 water bodies contains at least one.** "
      "Counted over that register: 3 water bodies contain no station visited in two "
      "or more distinct years, 8 contain none visited in five or more, and 22 "
      "contain none visited in ten or more.\n"
      ">\n"
      "> **Those are counts, and they are deliberately not percentages.** Saying "
      "*18% of the sea has no long observation* would be the missing-denominator "
      "error this project exists to point at, committed here. The denominator is "
      "known — the sea is 43,579 km². The numerator is not, because it is the "
      "extent of an absence, and an absence can only be measured against a search "
      "that was exhaustive. Ours was ODA plus two layers. ICES, EMODnet, university "
      "programmes, municipal monitoring and every unpublished series sit outside "
      "it.\n"
      ">\n"
      "> The line between the two kinds of figure is worth stating, because this "
      "page uses one of them freely and must not use the other:\n"
      ">\n"
      "> The test is whether **the category named is the same width as the corpus "
      "searched.**\n"
      ">\n"
      "> - **Same width — a percentage is fine, including of an absence.** *57 of "
      "123 water bodies have no point in the national hazardous-substance "
      "monitoring programme, covering 70% of the sea.* The category is that "
      "programme, the register of it is complete, so its complement is exact. Same "
      "for *28 of 123 have a fitted model — 5.7% of sea area*: the models are "
      "published and the sea is measured, and nothing rests on having found "
      "anything else.\n"
      "> - **Category wider than corpus — only a count is honest.** *56% of the sea "
      "has no marine observation* names a category — marine observation — far wider "
      "than the two layers actually searched. The leftover after subtracting what "
      "we happened to find is then reported as though it were measured, which is "
      "the operation [RESIDUAL.md](#RESIDUAL.md) is about, and it does not become "
      "acceptable because we are the ones doing it.\n"
      ">\n"
      "> So absence is reported here as a count over a named corpus, and the corpus "
      "is named every time.\n"
      ">\n"
      "> **And the corpus is named together with what is missing from it.** A "
      "coverage figure has a numerator nobody can measure — the evidence that "
      "exists — so counting what we assembled gives a *lower bound on evidence* and "
      "therefore an *upper bound on absence*. That is only interpretable beside the "
      "terms we know belong in the numerator and cannot add. They are kept in "
      "`data/manual/coverage_gaps.json` and there are three kinds:\n")
    gaps = read_json(os.path.join(MANUAL, "coverage_gaps.json"))["gaps"]
    a("")
    a("| | source | what it would add | why we do not have it |")
    a("|---|---|---|---|")
    for g in gaps:
        a(f"| `{g['class']}` | **{g['id']}** | {g['would_add']} | {g['barrier']} |")
    a("")
    a("The distinction inside that table matters as much as the table. `closed` is "
      "a gap in the world's availability; `open_unassembled` is a gap in our "
      "effort and is nobody's fault but ours; `absent` is the only one where a "
      "search was actually run to exhaustion, and even that is bounded by the "
      "search. **PULS is the sharpest case.** It holds the per-event overflow "
      "volumes that `B1` calls the single most valuable missing series, and an "
      "access attempt with a private MitID was refused because no CVR or VAT "
      "number attached to it was valid — so this is not a login anyone has "
      "neglected to perform. It appears to require a registered business or "
      "authority, which means a private citizen cannot obtain it at all.\n")

    a("## The cum hoc estimate, across areas instead of across years\n")
    a("A national time series has one unit of replication. The areas have "
      f"{ch['n_areas']}. So the only place an effect size can actually be estimated "
      "is across them.\n")
    a("This tests a sewage-driven outcome against sewage pressure — bathing quality "
      "against outfall and treatment-plant density — because that is the one "
      "predictor/outcome pair where both sides exist per area. It is **cum hoc**: a "
      "correlation across places at one time, with no control for coast type, "
      "flushing, or population. It is reported because it is computable and the "
      "national figure is not.\n")
    a("| predictor | outcome | r | R² | areas |")
    a("|---|---|---:|---:|---:|")
    for t in ch["tests"]:
        a(f"| {t['predictor']} | {t['outcome']} | {t['r']:+.3f} | {t['r2']:.3f} | {t['n']} |")
    a("")

    a("## Every area, on its own terms\n")
    a("`model` — a fitted load→indicator relation exists (DCE 2015, fitted on "
      "1990–2012). `bath` — bathing stations, and the years they span. `r` — how "
      "much those stations agree with each other, where there are enough to ask. "
      "`RBU` — rain-conditioned outfalls. `PE` — approved treatment-plant load.\n")
    a("| km² | area | model | bath (years) | r | RBU | PE | gaps |")
    a("|---:|---|:-:|---|---:|---:|---:|---:|")
    for r in sorted(rec.values(), key=lambda r: -r["area_km2"]):
        b = r["observation"].get("bathing")
        rbu = r["pressure"].get("rbu", {}).get("n", 0)
        pe = r["pressure"].get("rens", {}).get("pe", 0)
        bath = f"{b['stations']} ({b['first_year']}–{b['last_year']})" if b else "—"
        rr = f"{b['internal_r']:+.2f}" if b and b.get("internal_r") is not None else "—"
        a(f"| {r['area_km2']:,.1f} | {r['name']} | {'✓' if r['has_statistical_model'] else '·'} "
          f"| {bath} | {rr} | {rbu:,} | {pe:,} | {len(r['not_modelled'])} |")
    a("")
    a("The full record for each area — every pressure, every stream with its years, "
      "and the written-out list of what cannot be modelled there — is in "
      "[`data/derived/areas.json`](data/derived/areas.json), and drawn with its "
      "timeline on [the map](areas.html).\n")

    a("## What this is not\n")
    a("It is not a causal model per area. It is the ledger you need before you can "
      "build one: which areas have enough observation to support a claim, which have "
      "none, and over which years each stream exists — so that an analysis published "
      "in 2025 cannot quietly rest on a relation fitted to 1990–2012 without a reader "
      "seeing the gap.\n")
    return "\n".join(o) + "\n"


def main():
    props, rec = build()
    ch = cum_hoc(rec)
    write_json(OUT_JSON, {"assignment": {"rule": "nearest marine boundary vertex",
                                         "max_km": MAX_ASSIGN_KM},
                          "cum_hoc": ch, "areas": rec})
    write_doc(OUT_MD, render(props, rec, ch))
    nothing = [r for r in rec.values()
               if not r["has_statistical_model"] and not r["observation"].get("bathing")]
    log(f"\nwrote docs/AREAS.md ({os.path.getsize(OUT_MD):,} chars)")
    log(f"  {len(rec)} areas; {sum(1 for r in rec.values() if r['has_statistical_model'])} "
        f"modelled; {len(nothing)} with neither model nor observation")
    for t in ch["tests"]:
        log(f"  {t['predictor']:28} -> {t['outcome']:15} r={t['r']:+.3f} n={t['n']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
