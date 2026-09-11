#!/usr/bin/env python3
"""The local counts behind the B1 draft (combined sewer overflow), re-derived.

docs/hypodrafts/B1.md verified its data table by hand: the bathing-site layer,
the combined-overflow layer, the national overflow-structure register, their
name join, a critical rainfall depth per structure, and which kind of outfall
lies nearest each bathing site. Every one of those is recomputed here from the
held files and written to data/derived/hypodraft_b1.json.

Critical rainfall depth: storage (`vol_sb` + `vol_fbas`, m3) over the reduced
area (`Red areal`, ha), in mm - one hectare under one millimetre is ten cubic
metres. Only structures whose CSO name matches exactly one register point, with
positive storage and positive area, carry one.

Nearest outfall: for each bathing site, the nearest register point whose
structure type is combined (OV, OS, OF, OK, Bypass) or separate (SE, SF), by
great-circle distance.

    scripts/heavy python3 scripts/hypodraft_b1.py
"""
import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, ROOT, log

OUT = os.path.join(DERIVED, "hypodraft_b1.json")
COMBINED = {"OV", "OS", "OF", "OK", "Bypass"}
SEPARATE = {"SE", "SF"}


def feats(path):
    return json.load(open(path, encoding="utf-8"))["features"]


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))]


def main(argv):
    sites = feats(os.path.join(RAW, "national", "badevand.geojson"))
    cso = feats(os.path.join(RAW, "spildevand", "combined_overflow.geojson"))
    rbu = feats(os.path.join(RAW, "national", "punkt_rbu_udl.geojson"))
    cp = [f["properties"] for f in cso]
    rp = [f["properties"] for f in rbu]
    vol = lambda p: p.get("Vand_(m3/ aar)")
    out = {"_what": "Local counts behind docs/hypodrafts/B1.md, re-derived by "
                    "scripts/hypodraft_b1.py.",
           "sites": len(sites),
           "cso": {"n": len(cp), "names_unique": len({p["Navn"] for p in cp}),
                   "spills_null": sum(p.get("Antal overløb") is None for p in cp),
                   "volume_null": sum(vol(p) is None for p in cp),
                   "volume_zero": sum(vol(p) == 0 for p in cp),
                   "type": dict(collections.Counter(p["Bygværkstype"] for p in cp))},
           "rbu": {"n": len(rp),
                   "vol_sb_nonnull": sum(p.get("vol_sb") is not None for p in rp),
                   "vol_sb_zero": sum(p.get("vol_sb") == 0 for p in rp),
                   "vol_fbas_nonnull": sum(p.get("vol_fbas") is not None for p in rp),
                   "vol_fbas_zero": sum(p.get("vol_fbas") == 0 for p in rp),
                   "type": dict(collections.Counter(p["bgv_type"] for p in rp))}}
    out["cso"]["spills_null_pct"] = round(100 * out["cso"]["spills_null"] / len(cp), 1)

    by_name = collections.defaultdict(list)
    for p in rp:
        by_name[p["pkt_navn"]].append(p)
    names = {p["Navn"] for p in cp}
    out["join"] = {"cso_names": len(names), "matched": sum(1 for n in names if n in by_name)}
    depths = []
    for p in cp:
        m = by_name.get(p["Navn"], [])
        if len(m) != 1:
            continue
        store = (m[0].get("vol_sb") or 0) + (m[0].get("vol_fbas") or 0)
        area = p.get("Red areal") or 0
        if store > 0 and area > 0:
            depths.append(store / (area * 10.0))
    out["critical_depth_mm"] = {"n": len(depths), "p10": round(q(depths, 0.10), 2),
                                "median": round(q(depths, 0.50), 2),
                                "p90": round(q(depths, 0.90), 1), "max": round(max(depths))}

    pts = [(f["geometry"]["coordinates"], f["properties"]["bgv_type"]) for f in rbu
           if f.get("geometry") and f["properties"]["bgv_type"] in COMBINED | SEPARATE]

    def km(a, b):
        (lo1, la1), (lo2, la2) = a, b
        x = math.radians(lo2 - lo1) * math.cos(math.radians((la1 + la2) / 2))
        y = math.radians(la2 - la1)
        return 6371.0 * math.hypot(x, y)
    near = []
    for f in sites:
        s = f["geometry"]["coordinates"]
        d, t = min((km(s, c), t) for c, t in pts)
        near.append((d, "combined" if t in COMBINED else "separate"))
    ds = [d for d, _ in near]
    out["nearest"] = {"combined": sum(k == "combined" for _, k in near),
                      "separate": sum(k == "separate" for _, k in near),
                      "median_km": round(q(ds, 0.5), 2),
                      "within_1km": sum(d <= 1 for d in ds), "within_2km": sum(d <= 2 for d in ds)}
    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(json.dumps({k: v for k, v in out.items() if k != "_what"}, ensure_ascii=False))
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
