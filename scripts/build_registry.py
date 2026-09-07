#!/usr/bin/env python3
"""Join the Spildevandsplan prose to the map geometry, and report what does not join.

Copenhagen keeps these in two disconnected places:

  * planer.kk.dk project pages  - what is claimed: purpose, volumes, owner, parcels.
    Keyed by a plan number (A1.14, K1.57).
  * kk.dk WFS layers            - where it is: polygons and alignments.
    Keyed by a cloudburst number ("klima_id": BIR7.5, KV86, VEL45).

Nothing publishes the mapping between the two. But the plan pages cite the klima_id
in their titles and body text, so we recover the link by scanning for known ids.

The output deliberately keeps the misses. A basin that is described but never drawn,
or drawn but never described, is exactly the kind of gap worth seeing.

Usage:  python3 scripts/build_registry.py
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, log, read_json, write_json

# Layers that carry a klima_id, and the property it lives under.
GEOM_SOURCES = [
    ("skp_bassiner_pladser_kk", "klima_id", "basin_or_square"),
    ("skp_veje_tunneller_kk", "klima_id", "road_pipe_or_tunnel"),
    ("skp_igangsatte_prj_kk", "klima_id", "project_in_progress"),
    ("skp_afsluttede_prj_kk", "klimaid", "project_completed"),
]

# Cloudburst catchment prefixes seen in the data, expanded for readers.
PREFIX = {
    "AM": "Amager",
    "BIR": "Bispebjerg / Ryparken",
    "IB": "Indre By",
    "KV": "København Vest / Valby",
    "NO": "Nørrebro",
    "OS": "Østerbro",
    "VEL": "Vesterbro / Ladegårdsåen",
    "F": "Frederiksberg-related",
}


def norm_id(s):
    """'BIR 7.5' and 'bir7.5' both normalise to 'BIR7.5'."""
    return re.sub(r"\s+", "", (s or "")).upper()


def centroid(geom):
    """Rough centroid: mean of all vertices. Good enough to place a marker or label."""
    xs, ys = [], []

    def walk(c):
        if isinstance(c, list) and c and isinstance(c[0], (int, float)):
            xs.append(c[0])
            ys.append(c[1])
        elif isinstance(c, list):
            for sub in c:
                walk(sub)

    if not geom:
        return None
    walk(geom.get("coordinates"))
    if not xs:
        return None
    return [round(sum(xs) / len(xs), 6), round(sum(ys) / len(ys), 6)]


def load_geometry():
    """klima_id -> list of geometry records drawn from every layer that uses the key."""
    index = defaultdict(list)
    for layer, key, kind in GEOM_SOURCES:
        path = os.path.join(RAW, f"{layer}.geojson")
        if not os.path.exists(path):
            log(f"  (missing {layer}.geojson - run fetch_wfs.py first)")
            continue
        gj = read_json(path)
        for feat in gj["features"]:
            props = feat.get("properties") or {}
            kid = norm_id(props.get(key))
            if not kid:
                continue
            index[kid].append({
                "layer": layer,
                "kind": kind,
                "properties": props,
                "geometry": feat.get("geometry"),
                "centroid": centroid(feat.get("geometry")),
            })
        log(f"  {layer}: {sum(1 for f in gj['features'] if norm_id((f.get('properties') or {}).get(key)))} keyed features")
    return index


def find_ids(project, known):
    """Which known klima_ids does this project page cite?

    Restricted to the ids that actually exist in the geometry, so a stray token
    like 'A3' in prose cannot invent a match.
    """
    haystack = " ".join([project.get("title") or "", " ".join(project.get("sections", {}).values())])
    hits = set()
    for m in re.finditer(r"\b([A-ZÆØÅ]{1,4})\s?(\d+(?:\.\d+)*[A-Za-z]?)\b", haystack):
        cand = norm_id(m.group(1) + m.group(2))
        if cand in known:
            hits.add(cand)
    return sorted(hits)


# A cubic-metre figure in this prose can mean two completely different things:
# a tank that holds 10,000 m3, or an outfall that releases 148,000 m3 *per year*.
# Adding those together would be meaningless, so classify before using.
STORAGE_CUES = ("bassin", "magasin", "opbevar", "forsinkelsesvolumen", "sparebassin",
                "volumen", "opmagasin", "rumfang", "kapacitet til at opbevare",
                "tilbageholde", "reservoir")
FLOW_CUES = ("årlig", "årligt", "hvert år", "pr. år", "per år", "om året",
             "overløbsmængde", "udledt", "udledes", "aflastning", "aflastes",
             "pumpet", "pumpes", "afledes", "i gennemsnit")


def classify_volume(context):
    """'storage', 'annual_flow', or 'unclear' for one m3 figure, from its sentence."""
    c = context.lower()
    flow = any(k in c for k in FLOW_CUES)
    storage = any(k in c for k in STORAGE_CUES)
    if flow and not storage:
        return "annual_flow"
    if storage and not flow:
        return "storage"
    if flow and storage:
        # "550.000 m3 ... hvert år ... tilbage til kloaksystemet" - flow wins when the
        # sentence is explicitly periodic.
        return "annual_flow" if any(k in c for k in ("årlig", "hvert år", "pr. år",
                                                     "per år", "om året")) else "unclear"
    return "unclear"


def split_volumes(project):
    """Partition a project's m3 hits into storage / annual flow / unclear."""
    out = {"storage": [], "annual_flow": [], "unclear": []}
    for hit in project.get("measures", {}).get("volume_m3", []) or []:
        out[classify_volume(hit["context"])].append(hit)
    return out


def best_volume(vols):
    """Largest figure that actually describes stored volume."""
    return max((v["value"] for v in vols["storage"]), default=None)


def main():
    proj_path = os.path.join(RAW, "plan_projects.json")
    if not os.path.exists(proj_path):
        log("data/raw/plan_projects.json missing - run fetch_plan_projects.py first")
        return 1

    log("indexing geometry ...")
    geom = load_geometry()
    known = set(geom)
    log(f"  {len(known)} unique klima_id with geometry\n")

    projects = read_json(proj_path)
    log(f"matching {len(projects)} plan project pages ...")

    entries, matched_ids = [], set()
    for p in projects:
        ids = find_ids(p, known)
        matched_ids.update(ids)
        vols = split_volumes(p)
        entries.append({
            "plan_id": p.get("klima_id"),
            "title": p.get("title"),
            "category": p.get("category"),
            "url": p.get("url"),
            "klima_ids": ids,
            "catchments": sorted({PREFIX.get(re.match(r"^[A-ZÆØÅ]+", i).group(0), "?")
                                  for i in ids if re.match(r"^[A-ZÆØÅ]+", i)}),
            "headline_volume_m3": best_volume(vols),
            "annual_flow_m3_per_year": max((v["value"] for v in vols["annual_flow"]), default=None),
            "unclear_volumes_m3": [v["value"] for v in vols["unclear"]],
            "volume_hits": vols,
            # A page citing several klima_ids gives no way to know which structure the
            # figure belongs to, so its volume must not be counted against any of them.
            "volume_attribution": ("unambiguous" if len(ids) == 1 else
                                   "shared" if ids else "no_geometry"),
            "measures": p.get("measures", {}),
            "mentions_hofor": p.get("mentions_hofor"),
            "has_geometry": bool(ids),
            "sections": p.get("sections", {}),
            "tables": p.get("tables", []),
        })

    orphan_ids = sorted(known - matched_ids)

    # --- constructions.geojson: every keyed geometry, enriched with any prose we found
    by_kid = defaultdict(list)
    for e in entries:
        for kid in e["klima_ids"]:
            by_kid[kid].append(e)

    features = []
    for kid, recs in sorted(geom.items()):
        docs = by_kid.get(kid, [])
        sure_docs = [d for d in docs
                     if d["volume_attribution"] == "unambiguous" and d["headline_volume_m3"]]
        shared_docs = [d for d in docs
                       if d["volume_attribution"] == "shared" and d["headline_volume_m3"]]
        vol = max((d["headline_volume_m3"] for d in sure_docs), default=None)
        vol_shared = max((d["headline_volume_m3"] for d in shared_docs), default=None)
        for r in recs:
            props = dict(r["properties"])
            props.update({
                "klima_id": kid,
                "kind": r["kind"],
                "source_layer": r["layer"],
                "catchment": PREFIX.get(re.match(r"^[A-ZÆØÅ]+", kid).group(0), "?")
                             if re.match(r"^[A-ZÆØÅ]+", kid) else "?",
                "documented": bool(docs),
                "plan_titles": [d["title"] for d in docs][:5],
                "plan_urls": [d["url"] for d in docs][:5],
                "claimed_volume_m3": vol,
                "claimed_volume_m3_shared": vol_shared,
                "volume_is_attributable": vol is not None,
            })
            features.append({"type": "Feature", "properties": props, "geometry": r["geometry"]})

    write_json(os.path.join(DERIVED, "constructions.geojson"),
               {"type": "FeatureCollection", "features": features})

    documented = sum(1 for f in features if f["properties"]["documented"])
    attributable = {f["properties"]["klima_id"]: f["properties"]["claimed_volume_m3"]
                    for f in features if f["properties"].get("claimed_volume_m3")}
    shared = {f["properties"]["klima_id"]: f["properties"]["claimed_volume_m3_shared"]
              for f in features if f["properties"].get("claimed_volume_m3_shared")}
    flow_pages = [e for e in entries if e["annual_flow_m3_per_year"]]

    by_cat = Counter(e["category"] for e in entries)
    log("\n--- coverage ---")
    log(f"  plan project pages              : {len(entries)}")
    log(f"  ... linked to geometry          : {sum(1 for e in entries if e['has_geometry'])}")
    log(f"  klima_id in geometry            : {len(known)}")
    log(f"  ... cited by some plan page     : {len(matched_ids)}")
    log(f"  ... drawn but never described   : {len(orphan_ids)}")
    log(f"  construction features written   : {len(features)} ({documented} with prose)")
    log("\n  by plan category: " + ", ".join(f"{k}={v}" for k, v in by_cat.most_common()))

    log("\n--- claimed volumes (m3 figures are classified, not summed blindly) ---")
    log(f"  storage, attributable to one structure : {sum(attributable.values()):>12,.0f} m3"
        f"  across {len(attributable)} structures")
    log(f"  storage, page cites several ids        : {sum(shared.values()):>12,.0f} m3"
        f"  across {len(shared)} structures (NOT added - attribution unknown)")
    log(f"  annual discharge/pumped volumes        : {sum(e['annual_flow_m3_per_year'] for e in flow_pages):>12,.0f} m3/year"
        f"  across {len(flow_pages)} pages (a rate, not storage)")
    unclear = sum(len(e["unclear_volumes_m3"]) for e in entries)
    log(f"  figures needing a human read           : {unclear:>12,} ")

    write_json(os.path.join(DERIVED, "registry.json"), {
        "generated_from": ["data/raw/plan_projects.json", "data/raw/*.geojson"],
        "caveats": [
            "klima_id <-> plan-number links are reconstructed by citation scanning, not official.",
            "m3 figures are classified as storage / annual_flow / unclear from their sentence; "
            "only 'storage' figures on pages citing exactly one klima_id are attributed to a structure.",
            "Depths and diameters come from planning prose, not survey. No open source gives "
            "surveyed invert levels for Copenhagen sewers.",
        ],
        "counts": {
            "plan_projects": len(entries),
            "plan_projects_with_geometry": sum(1 for e in entries if e["has_geometry"]),
            "unique_klima_id_with_geometry": len(known),
            "klima_id_cited_by_a_plan_page": len(matched_ids),
            "klima_id_with_geometry_but_no_plan_page": len(orphan_ids),
            "construction_features": len(features),
            "storage_m3_attributable": round(sum(attributable.values())),
            "storage_m3_shared_attribution": round(sum(shared.values())),
            "annual_flow_m3_per_year": round(sum(e["annual_flow_m3_per_year"] for e in flow_pages)),
            "volume_figures_needing_human_read": sum(len(e["unclear_volumes_m3"]) for e in entries),
        },
        "klima_id_without_documentation": orphan_ids,
        "projects": entries,
    })
    log("\nwrote data/derived/constructions.geojson and data/derived/registry.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
