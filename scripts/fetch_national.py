#!/usr/bin/env python3
"""Fetch the national water-plan layers, for the map of what Denmark measures and when.

Everything else in this project is Copenhagen-shaped. This is not: the argument about
whether the nitrogen requirement rests on an adequate observing system is a national
argument, and it needs the national geometry - all 119 marine water bodies, the main
catchments, and the things the monitoring does and does not point at.

Several of these layers are here because reading the method documents raised a specific
question:

  klappladser      where dredged material is legally dumped - the Lynetteholm question,
                   and the Øresund link's spill, at national scale
  raastofomr       raw-material extraction areas - the candidate terminal waters from
                   PROGRAMME.md section 2, which have never been screened for it
  skaldyrvande     designated shellfish waters - where extractive aquaculture is already
                   contemplated
  badevand         bathing water, which carries a per-station annual quality series and
                   is the only long ecological record with a fixed seasonal window
  sw_mfs_tilstand  surface water status for hazardous substances

Usage:  python3 scripts/fetch_national.py [--force]
"""
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RAW, fetch, log, write_json

BASE = "https://wfs2-miljoegis.mim.dk/vp3basis2019/ows"
DEST = os.path.join(RAW, "national")

LAYERS = [
    ("vp3_basis_2019_marin_overordnet", "marine water bodies - the 119 under the WFD"),
    ("vp3_basis_2019_hovedoplande", "main catchments"),
    ("vp3basis2019_badevand", "bathing water stations, with annual quality 1991-2018"),
    ("vp3basis2019_klappladser", "licensed dredged-material dumping sites"),
    ("vp3basis2019_raastofomr", "raw-material extraction areas"),
    ("vp3basis2019_skaldyrvande", "designated shellfish waters"),
    ("vp3_basis_2019_punkt_havdam_udl", "marine aquaculture discharge points"),
    ("vp3basis2019_sw_mfs_tilstand", "surface water status, hazardous substances"),
    ("vp3_basis_2019_ov_maalestation_vandl", "stream monitoring stations"),
    ("vp3_basis_2019_ov_maalestation_soe", "lake monitoring stations"),
]


def main(argv):
    force = "--force" in argv
    os.makedirs(DEST, exist_ok=True)
    for layer, what in LAYERS:
        short = layer.replace("vp3_basis_2019_", "").replace("vp3basis2019_", "")
        p = os.path.join(DEST, f"{short}.geojson")
        if os.path.exists(p) and not force:
            n = len(json.load(open(p, encoding="utf-8")).get("features") or [])
            log(f"  {short:22} cached, {n:,} features")
            continue
        q = {"service": "WFS", "version": "1.1.0", "request": "GetFeature",
             "typeName": "vp3basis2019:" + layer,
             "outputFormat": "application/json", "srsName": "EPSG:4326"}
        try:
            d = json.loads(fetch(BASE + "?" + urllib.parse.urlencode(q), timeout=300))
        except Exception as e:
            log(f"  {short:22} FAILED: {type(e).__name__} {str(e)[:60]}")
            continue
        d["_what"] = what
        write_json(p, d)
        log(f"  {short:22} {len(d.get('features') or []):>6,} features  "
            f"{os.path.getsize(p)/1e6:>6.1f} MB   {what}")
        time.sleep(1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
