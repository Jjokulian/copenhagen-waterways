#!/usr/bin/env python3
"""Download the WFS layers listed in layers.json into data/raw/.

Two sources: the Copenhagen municipal server (the city's own plan geometry) and
Miljøstyrelsen's national water-plan server (the discharge points those pipes end
at). National layers are clipped to the metropolitan municipalities by attribute.

Usage:
    python3 scripts/fetch_wfs.py                      # everything not yet present
    python3 scripts/fetch_wfs.py --force              # re-fetch everything
    python3 scripts/fetch_wfs.py --source vp3         # one source only
    python3 scripts/fetch_wfs.py sp_kloakoplande      # named layers only
"""
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RAW, fetch, log, read_json, write_json, axis_order_ok, swap_axes, in_cph

CATALOGUE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "layers.json")
MAX_PARSE_BYTES = 80 * 1024 * 1024  # this box has ~300 MB of RAM to play with


def wfs_url(source, layer):
    return source["endpoint"] + "?" + urllib.parse.urlencode({
        "service": "WFS",
        "version": source.get("version", "1.0.0"),
        "request": "GetFeature",
        "typeName": f"{source['prefix']}:{layer}",
        "outputFormat": "application/json",
        "srsName": "EPSG:4326",
    })


def apply_filter(feats, flt):
    """Clip a national layer to the Copenhagen area.

    Prefer the attribute filter (exact, uses the publisher's own municipality names),
    but many layers carry no municipality column - fall back to a bounding box so we
    do not silently discard the whole layer.
    """
    if not flt or not feats:
        return feats, 0, None
    prop = flt["property"]
    has_prop = any(prop in (f.get("properties") or {}) for f in feats[:200])
    if has_prop:
        allowed = {v.strip().lower() for v in flt["in"]}
        kept = [f for f in feats
                if str((f.get("properties") or {}).get(prop, "")).strip().lower() in allowed]
        how = prop
    else:
        kept = [f for f in feats if in_cph(f.get("geometry"))]
        how = "bbox"
    return kept, len(feats) - len(kept), how


def fetch_layer(source, spec, force=False):
    name = spec["name"]
    out = os.path.join(RAW, f"{name}.geojson")
    if os.path.exists(out) and not force:
        log(f"  skip {name} (already present)")
        return None

    url = wfs_url(source, name)
    raw = fetch(url, timeout=240)
    if len(raw) > MAX_PARSE_BYTES:
        log(f"  !! {name}: {len(raw)/1e6:.0f} MB - too large to parse here; saved unvalidated")
        os.makedirs(RAW, exist_ok=True)
        with open(out, "wb") as f:
            f.write(raw)
        return {"layer": name, "source": source["id"], "bytes": len(raw), "validated": False}

    try:
        gj = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        snippet = raw[:200].decode("utf-8", "replace").replace("\n", " ")
        log(f"  !! {name}: not JSON (likely an OWS exception): {snippet}")
        return {"layer": name, "error": "non-json response"}

    feats = gj.get("features")
    if feats is None:
        return {"layer": name, "error": f"no 'features' key; got {list(gj)[:5]}"}

    # WFS 1.0.0 and 1.1.0 disagree about EPSG:4326 axis order. Normalise to [lon, lat].
    order = axis_order_ok(feats)
    if order is False:
        log(f"  ~~ {name}: coordinates were [lat, lon]; swapping")
        for f in feats:
            swap_axes(f.get("geometry"))
    elif order is None and feats:
        log(f"  ?? {name}: could not verify coordinates fall inside Copenhagen")

    total = len(feats)
    feats, dropped, how = apply_filter(feats, source.get("filter"))
    gj["features"] = feats

    geom_types = sorted({f["geometry"]["type"] for f in feats if f.get("geometry")})
    write_json(out, gj)
    extra = f" (clipped by {how}: kept {len(feats)} of {total})" if dropped else ""
    log(f"  ok  {name}: {len(feats)} features, {','.join(geom_types) or 'none'}{extra}")
    return {
        "layer": name,
        "source": source["id"],
        "theme": spec.get("theme"),
        "title_da": spec.get("title_da"),
        "title_en": spec.get("title_en"),
        "note": spec.get("note"),
        "features": len(feats),
        "features_before_filter": total if dropped else None,
        "clipped_by": how if dropped else None,
        "geometry_types": geom_types,
        "properties": sorted(feats[0].get("properties", {})) if feats else [],
        "source_url": url,
        "licence": source.get("licence"),
        "file": f"data/raw/{name}.geojson",
    }


def main():
    argv = sys.argv[1:]
    force = "--force" in argv
    only_source = argv[argv.index("--source") + 1] if "--source" in argv else None
    named = [a for a in argv if not a.startswith("-") and a != only_source]

    cat = read_json(CATALOGUE)
    manifest, failed = [], []

    for source in cat["sources"]:
        if only_source and source["id"] != only_source:
            continue
        layers = [l for l in source["layers"] if not named or l["name"] in named]
        if not layers:
            continue
        log(f"\n[{source['id']}] {source['name']}")
        log(f"  {source['endpoint']}  ({len(layers)} layer(s))")
        for spec in layers:
            try:
                r = fetch_layer(source, spec, force)
                if r and "error" not in r:
                    manifest.append(r)
                elif r:
                    failed.append((spec["name"], r["error"]))
            except Exception as e:  # one dead layer must not stop the harvest
                log(f"  !! {spec['name']}: {e}")
                failed.append((spec["name"], str(e)))

    if manifest:
        path = os.path.join(RAW, "_manifest.json")
        existing = read_json(path) if os.path.exists(path) else []
        by_name = {m["layer"]: m for m in existing if isinstance(m, dict)}
        by_name.update({m["layer"]: m for m in manifest})
        write_json(path, sorted(by_name.values(),
                                key=lambda m: (m.get("source") or "", m.get("theme") or "", m["layer"])))
        log(f"\nmanifest: {len(by_name)} layers -> data/raw/_manifest.json")
    if failed:
        log(f"\n{len(failed)} layer(s) failed:")
        for n, e in failed:
            log(f"  {n}: {e[:140]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
