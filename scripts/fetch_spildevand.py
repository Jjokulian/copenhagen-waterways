#!/usr/bin/env python3
"""Danish wastewater outfalls with the discharge attached, from spildevandsdata.dk.

`B1` calls per-outfall overflow volume the single most valuable missing series in
the register, and `B2` and `B3` want the same for separate stormwater and for
treatment plants. This gets the annual form of all three.

spildevandsdata.dk is a static Leaflet export of a PULS extract. Its layers are
plain `.js` files holding one GeoJSON assignment each, so no login, no API and no
CVR gate - the PULS application itself is behind one, and this is the same data
already published.

What it does and does not give:

  * **Per outfall, per year.** Volume in cubic metres, count of overflow events,
    nitrogen and phosphorus in kilogrammes, the reduced impervious area behind it,
    the owning utility and the structure type.
  * **Not per event.** `B1`'s discriminating test is oxygen and shore condition in
    the days after an overflow against that event's volume, and an annual total
    cannot do it. It can rank outfalls, size the flux, and say where to look.
  * **Mostly modelled, not gauged.** Danish utilities report overflow volume to
    PULS largely from runoff models over the connected area, not from meters at
    the structure. So this is a modelled quantity that arrives looking like a
    measurement - the exact substitution this project exists to notice. Treat the
    number as an estimate whose error is unstated, and note that a modelled volume
    cannot be used to validate a model of the same runoff.

Structure types, which matter because they are not the same thing:
    OV   overflow from a combined system      OS   overflow structure
    OF   overflow with filter/screen          OK   overflow to a basin
    UR   untreated discharge                  Bypass   plant bypass

Writes  data/raw/spildevand/*.geojson  and a merged data/derived/outfalls.json

Usage:  python3 scripts/fetch_spildevand.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, fetch, log, write_json

BASE = "https://spildevandsdata.dk/layers/"
LAYERS = {
    "combined_overflow":  ("Flleskloakeredeoverlbm3_2.js",
                           "Combined-sewer overflow structures, m3/yr"),
    "separate_stormwater": ("Regnvandssepareredeudlbm3_1.js",
                            "Separate stormwater outfalls, m3/yr"),
    "plant_discharge":    ("Renseanlgudledtvand1000m3_6.js",
                           "Treatment plants, discharged water 1000 m3/yr"),
    "plant_bod":          ("RenseanlgrensningsgradBI5_3.js",
                           "Treatment plants, BOD5 removal rate"),
    "plant_n":            ("RenseanlgrensningsgradN_5.js",
                           "Treatment plants, nitrogen removal rate"),
    "plant_p":            ("RenseanlgrensningsgradP_4.js",
                           "Treatment plants, phosphorus removal rate"),
}


def parse(raw):
    """Each file is `var json_<name> = {...};` - one GeoJSON object."""
    s = raw.decode("utf-8", "replace")
    return json.loads(s[s.index("{"):].rstrip().rstrip(";"))


def numeric(features, key):
    """The overflow layers store numbers as numbers; the treatment-plant layers
    store the same kinds of quantity as strings, and one field name arrives with
    its encoding already broken ('Ind Vandm\ufffd'). Coerce rather than skip, or
    four of the six layers silently summarise to nothing."""
    out = []
    for f in features:
        v = f["properties"].get(key)
        if isinstance(v, bool) or v is None:
            continue
        if isinstance(v, (int, float)):
            out.append(v)
            continue
        if isinstance(v, str):
            t = v.strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
            try:
                out.append(float(t))
            except ValueError:
                pass
    return out


def main():
    dest = os.path.join(RAW, "spildevand")
    os.makedirs(dest, exist_ok=True)
    out = {}
    for name, (fn, what) in LAYERS.items():
        try:
            gj = parse(fetch(BASE + fn, timeout=180))
        except Exception as e:
            log(f"  {name:22} FAILED {type(e).__name__}: {str(e)[:70]}")
            continue
        feats = gj["features"]
        p = os.path.join(dest, name + ".geojson")
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(gj, fh, ensure_ascii=False)
        keys = list(feats[0]["properties"]) if feats else []
        totals = {}
        for k in keys:
            v = numeric(feats, k)
            if len(v) > len(feats) * 0.3 and any(x for x in v):
                totals[k] = {"n": len(v), "sum": round(sum(v), 1),
                             "median": sorted(v)[len(v) // 2]}
        out[name] = {"what": what, "file": fn, "n": len(feats),
                     "fields": keys, "totals": totals}
        log(f"  {name:22} {len(feats):6,} features  {os.path.getsize(p)/1e6:5.1f} MB")
    write_json(os.path.join(DERIVED, "outfalls.json"),
               {"_what": "Danish wastewater outfalls and treatment plants with "
                         "annual discharge, from the spildevandsdata.dk PULS "
                         "extract.",
                "_limits": "Annual, not per event - B1's discriminating test needs "
                           "per-event volume and this cannot supply it. Overflow "
                           "volumes are largely modelled from runoff over the "
                           "connected area rather than gauged at the structure.",
                "source": BASE, "layers": out})
    for name, r in out.items():
        print(f"\n{name} - {r['what']}  ({r['n']:,} features)")
        for k, t in r["totals"].items():
            print(f"    {k:24} n={t['n']:6,}  total {t['sum']:>16,.0f}  "
                  f"median {t['median']:>10,.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
