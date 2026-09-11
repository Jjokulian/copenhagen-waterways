#!/usr/bin/env python3
"""Small counts and computed values the site's overview pages quote.

Each of these was once typed into a page by hand: "ten of twenty pathways", "11
usable pairs", the sun's height at 09:00 on the solstices, "680 points (392 in
København)", "357 project pages", "roughly 8 MB each". Typed, they go stale the
moment their source changes - and "roughly 8 MB each" was already wrong, the
seven sheets run from under ten to nearly thirty megabytes. Computed here from
the file that holds them, they are stored with the rest of the derived data and
reach a page through live.py like any other number.

Nothing here is new analysis. Every value is a count over, a sum over, or a
direct computation from a file another script or a fetch already wrote:

  pathways_*        data/manual/nitrogen_pathways.json - enumerated nitrogen
                    pathways, and those with status UNQUANTIFIED
  floodalign_pairs  data/derived/floodalign.json - overlapping sheet pairs that
                    passed the peak-to-rival test and entered the bundle
  sun_*             scripts/daylight.py's NOAA solar elevation at a stated
                    reference point in central Copenhagen, on the two solstices,
                    with Danish legal time converted to UTC by scripts/clock.py
  vp3_rbu_*         data/raw/vp3_basis_2019_punkt_rbu_udl.geojson - the
                    rain-dependent discharge points of the metro clip
  plan_categories   data/raw/plan_projects.json - project pages per category
  kbhkort_*         data/raw/_manifest.json and the files it lists - the city
                    WFS layers fetched, and their size on disk
  floodmap_pdf_mb_* data/raw/floodmaps/*.pdf - the published flood sheets
  hypotheses_n      data/derived/hypotheses.json - lettered hypotheses, and the
  groups_n          groups they are filed under
  drafts_n          docs/hypodrafts/ and docs/openproblems/ - per-hypothesis
                    draft pages (not the README, triage or audit pages)
  kemi_parameters   data/derived/enums.json - distinct Parameter values in the
  ctd_parameters    water-chemistry and the CTD extract
  light_start_depth_diff_pct
                    data/derived/light.json - the depth of eleven per cent light
                    from casts started deep against casts started shallow
  gated_*           scripts/unlock.py - sources the register classifies as gated,
                    and the drop-in slots written for them
  fat_*, carbohydrate_cod_g_per_g
                    stoichiometry on a chosen reference compound: tripalmitin
                    for fat, glucose for carbohydrate

    python3 scripts/meta_facts.py

Writes data/derived/meta_facts.json.
"""
import collections
import datetime as dt
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, MANUAL, RAW, ROOT, log, read_json
import clock
from daylight import solar_elevation
import unlock

OUT = os.path.join(DERIVED, "meta_facts.json")
# The reference point for the solstice examples: Rådhuspladsen, central
# Copenhagen. Chosen, not measured.
REF_LAT, REF_LON = 55.6761, 12.5683
SOLSTICES = {"winter": dt.date(2025, 12, 21), "summer": dt.date(2025, 6, 21)}
KBHKORT = "wfs-kbhkort.kk.dk"
# Standard atomic masses, g/mol, and the reference compounds for "fat" and
# "carbohydrate". A sewage fat is a mixture; tripalmitin stands in for it.
MASS = {"C": 12.011, "H": 1.008, "N": 14.007, "O": 15.999}
TRIPALMITIN = {"C": 51, "H": 98, "O": 6}
GLUCOSE = {"C": 6, "H": 12, "O": 6}


def elevation_at_local(day, hour, minute=0):
    """Sun elevation at the reference point at a Danish legal clock time."""
    utc = dt.datetime.combine(day, dt.time(hour, minute)) - dt.timedelta(hours=clock.offset(day))
    return round(solar_elevation(REF_LAT, REF_LON, utc), 2)


def molar(f):
    return sum(MASS[e] * n for e, n in f.items())


def cod_per_g(f):
    """Grams of O2 to oxidise one gram of CcHhOo to CO2 and H2O."""
    o2 = f.get("C", 0) + f.get("H", 0) / 4 - f.get("O", 0) / 2
    return o2 * 2 * MASS["O"] / molar(f)


def mb(path):
    return round(os.path.getsize(os.path.join(ROOT, path)) / 1e6, 1)


def main(argv):
    pw = read_json(os.path.join(MANUAL, "nitrogen_pathways.json"))["pathways"]
    fa = read_json(os.path.join(DERIVED, "floodalign.json"))
    rbu = read_json(os.path.join(RAW, "vp3_basis_2019_punkt_rbu_udl.geojson"))["features"]
    plans = read_json(os.path.join(RAW, "plan_projects.json"))
    manifest = read_json(os.path.join(RAW, "_manifest.json"))
    kbh = [m for m in manifest if KBHKORT in m.get("source_url", "")]
    vols = [float(f["properties"]["vol_sb"]) for f in rbu
            if f["properties"].get("vol_sb") not in (None, "", 0, "0")]
    pdfs = [os.path.getsize(p) / 1e6 for p in glob.glob(os.path.join(RAW, "floodmaps", "*.pdf"))]
    hyp = read_json(os.path.join(DERIVED, "hypotheses.json"))
    enums = read_json(os.path.join(DERIVED, "enums.json"))
    light = read_json(os.path.join(DERIVED, "light.json"))
    drafts = [f for d in ("hypodrafts", "openproblems")
              for f in glob.glob(os.path.join(ROOT, "docs", d, "*.md"))
              if os.path.basename(f) not in ("README.md", "TRIAGE.md", "AUDIT.md")]
    out = {
        "_what": "Counts and computed values quoted by the overview pages, each "
                 "derived from the file named in its field description.",
        "pathways_total": len(pw),
        "pathways_unquantified": sum(1 for p in pw if p.get("status") == "UNQUANTIFIED"),
        "floodalign_pairs": len(fa.get("pairs", [])),
        "sun_reference_lat": REF_LAT,
        "sun_reference_lon": REF_LON,
        "sun_winter_0900": elevation_at_local(SOLSTICES["winter"], 9),
        "sun_summer_0900": elevation_at_local(SOLSTICES["summer"], 9),
        "sun_winter_1300": elevation_at_local(SOLSTICES["winter"], 13),
        "vp3_rbu_points": len(rbu),
        "vp3_rbu_kobenhavn": sum(1 for f in rbu if f["properties"].get("komm_navn") == "København"),
        "vp3_rbu_se_sf": sum(1 for f in rbu if f["properties"].get("bgv_type") in ("SE", "SF")),
        "vp3_rbu_with_volume": len(vols),
        "vp3_rbu_volume_m3": round(sum(vols)),
        "plan_pages": len(plans),
        "plan_categories": dict(collections.Counter(p.get("category") for p in plans).most_common()),
        "kbhkort_layers_fetched": len(kbh),
        "kbhkort_raw_mb": round(sum(os.path.getsize(os.path.join(ROOT, m["file"])) for m in kbh
                                    if os.path.exists(os.path.join(ROOT, m["file"]))) / 1e6, 1),
        "dike_raw_mb": round(mb("data/raw/hmax263_dige.geojson") + mb("data/raw/hmax285_dige.geojson"), 1),
        "floodmap_pdfs": len(pdfs),
        "floodmap_pdf_mb_min": round(min(pdfs), 1) if pdfs else None,
        "floodmap_pdf_mb_max": round(max(pdfs), 1) if pdfs else None,
        "hypotheses_n": len(hyp["hypotheses"]),
        "groups_n": len(hyp["groups"]),
        "drafts_n": len(drafts),
        "kemi_parameters": len(enums["kemi"]["categorical"]["Parameter"]),
        "ctd_parameters": len(enums["ctd"]["categorical"]["Parameter"]),
        # how much deeper useful light reaches when the sensor starts deep: the
        # landing page's "differing by 30%" between the two start-depth medians
        "light_start_depth_diff_pct": round(
            100 * (light["start_depth"]["z11_deep_start"] / light["start_depth"]["z11_shallow_start"] - 1), 1),
        "gated_sources": len(unlock.gated_sources()),
        "gated_slots": len(unlock.SLOTS),
        "fat_n_frac_pct": round(100 * MASS["N"] * TRIPALMITIN.get("N", 0) / molar(TRIPALMITIN), 3),
        "fat_c_frac": round(MASS["C"] * TRIPALMITIN["C"] / molar(TRIPALMITIN), 4),
        "fat_cod_g_per_g": round(cod_per_g(TRIPALMITIN), 3),
        "carbohydrate_cod_g_per_g": round(cod_per_g(GLUCOSE), 3),
    }
    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    for k, v in out.items():
        if not k.startswith("_"):
            log(f"  {k:<24} {v}")
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
