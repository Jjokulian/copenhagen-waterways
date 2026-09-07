#!/usr/bin/env python3
"""Field observations of where rain actually goes.

Nothing in the open record says this. The national technical standard calibrates
overflow models against measurements taken *inside* overflow structures - five clearly
separable events at the structure. Nothing in that chain observes a street. So there is
no dataset saying whether the modelled 0.2 m at a given corner is really 0.4 m because a
gully has been blocked since 2019.

These records are that missing layer. They are kept apart from everything else in the
project: `data/manual/observations.geojson` is hand-collected ground truth, never
overwritten by a fetch script.

Usage:
    python3 scripts/observations.py import [file]   # merge an export from viz/log.html
    python3 scripts/observations.py list
    python3 scripts/observations.py stats
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import MANUAL, log, read_json, write_json

STORE = os.path.join(MANUAL, "observations.geojson")
DEFAULT_IMPORT = os.path.join(MANUAL, "observations.import.json")

# Depth classes, matching the 2012 flood-model legend so the two can be compared.
DEPTH = ["dry", "<0.05", "0.05-0.1", "0.1-0.2", "0.2-0.5", "0.5-1", ">1"]
FLOW = ["standing", "slow", "fast", "torrent"]
DRAIN = ["clear", "slow", "blocked", "surcharging", "none", "unseen"]
RAIN = ["none", "light", "moderate", "heavy", "cloudburst"]
BBOX = (12.30, 55.50, 12.80, 55.80)


def empty():
    return {
        "type": "FeatureCollection",
        "_what": "Field observations of surface water in Copenhagen, collected on foot.",
        "_why": "No open dataset records observed street-level ponding; models are "
                "calibrated inside overflow structures, not on streets.",
        "_schema": {
            "observed_at": "ISO 8601 timestamp",
            "accuracy_m": "GPS accuracy. Above ~30 m an observation locates a street, "
                          "not a gully - do not over-read it.",
            "depth_class": DEPTH,
            "flow": FLOW,
            "drain": DRAIN + ["  ('surcharging' = water rising OUT of the drain, which "
                              "means the pipe below is full)"],
            "rain": RAIN,
            "note": "free text",
        },
        "features": [],
    }


def validate(f, i):
    """Return a list of problems with one feature. Empty list means it is usable."""
    errs = []
    g = f.get("geometry") or {}
    c = g.get("coordinates")
    if g.get("type") != "Point" or not (isinstance(c, list) and len(c) >= 2):
        return [f"#{i}: not a point"]
    lon, lat = c[0], c[1]
    if not (BBOX[0] <= lon <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]):
        errs.append(f"#{i}: {lon:.4f},{lat:.4f} is outside the Copenhagen area")
    p = f.get("properties") or {}
    if p.get("depth_class") not in DEPTH:
        errs.append(f"#{i}: depth_class {p.get('depth_class')!r} not one of {DEPTH}")
    for key, allowed in (("flow", FLOW), ("drain", DRAIN), ("rain", RAIN)):
        v = p.get(key)
        if v is not None and v not in allowed:
            errs.append(f"#{i}: {key} {v!r} not one of {allowed}")
    if not p.get("observed_at"):
        errs.append(f"#{i}: no observed_at timestamp")
    return errs


def key(f):
    p = f["properties"]
    return (p.get("observed_at"), round(f["geometry"]["coordinates"][0], 6),
            round(f["geometry"]["coordinates"][1], 6))


def cmd_import(args):
    src = args[0] if args else DEFAULT_IMPORT
    if not os.path.exists(src):
        log(f"nothing to import at {src}")
        log("Export from viz/log.html on your phone, save it there, and re-run.")
        return 1
    incoming = read_json(src)
    feats = incoming.get("features", incoming if isinstance(incoming, list) else [])
    store = read_json(STORE) if os.path.exists(STORE) else empty()

    seen = {key(f) for f in store["features"]}
    added, dupes, bad = 0, 0, []
    for i, f in enumerate(feats):
        errs = validate(f, i)
        if errs:
            bad.extend(errs)
            continue
        if key(f) in seen:
            dupes += 1
            continue
        seen.add(key(f))
        store["features"].append(f)
        added += 1

    store["features"].sort(key=lambda f: f["properties"].get("observed_at") or "")
    write_json(STORE, store)
    log(f"imported {added} observation(s); {dupes} already present; {len(bad)} rejected")
    for e in bad[:12]:
        log(f"  {e}")
    log(f"\nstore now holds {len(store['features'])} observation(s) -> "
        "data/manual/observations.geojson")
    if added:
        log("Re-run build_viewer_data.py to show them on the map.")
    return 0


def cmd_list(args):
    if not os.path.exists(STORE):
        log("no observations yet")
        return 0
    for f in read_json(STORE)["features"]:
        p, c = f["properties"], f["geometry"]["coordinates"]
        bits = [p.get("flow"), p.get("drain"), p.get("rain")]
        log(f"  {p.get('observed_at','?')[:16]}  {c[1]:.5f},{c[0]:.5f} "
            f"±{p.get('accuracy_m','?')}m  depth {p.get('depth_class'):>9}  "
            f"{' · '.join(b for b in bits if b)}")
        if p.get("note"):
            log(f"      {p['note']}")
    return 0


def cmd_stats(args):
    if not os.path.exists(STORE):
        log("no observations yet")
        return 0
    feats = read_json(STORE)["features"]
    log(f"{len(feats)} observation(s)")
    if not feats:
        return 0
    for field in ("depth_class", "flow", "drain", "rain"):
        c = Counter(f["properties"].get(field) for f in feats)
        c.pop(None, None)
        if c:
            log(f"  {field:12} " + ", ".join(f"{k}={v}" for k, v in c.most_common()))
    acc = [f["properties"].get("accuracy_m") for f in feats
           if isinstance(f["properties"].get("accuracy_m"), (int, float))]
    if acc:
        acc.sort()
        log(f"  {'accuracy':12} median {acc[len(acc)//2]} m, worst {acc[-1]} m")
    surch = [f for f in feats if f["properties"].get("drain") == "surcharging"]
    if surch:
        log(f"\n  {len(surch)} observation(s) of a drain SURCHARGING - water leaving the "
            "pipe upward. Those are the ones worth reporting to HOFOR.")
    return 0


COMMANDS = {"import": cmd_import, "list": cmd_list, "stats": cmd_stats}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        return 1
    return COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
