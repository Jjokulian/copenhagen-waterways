"""Fetch the city's own drainage structures: gully gratings and manholes.

Found by reading the WFS capabilities rather than by guessing, and they matter
because until now this project had catchments, outfalls and plans but **not one
structure**: every shaft spacing and gully density in the retrofit argument was a
stated convention. These two layers are the municipality's GeoDanmark objects, they
carry a registration date per feature, and the gratings carry a z coordinate.

  k101:rist    123,806 gully gratings   - the street inlets the retrofit cuts over
  k101:broend   85,816 manholes/wells   - the shafts a bore would start and end at

Fetched a page at a time rather than in one request, because this box has a few
hundred MB of RAM and a single response would be tens of megabytes of JSON. A bbox
would have been the obvious filter and it silently returns nothing: WFS 1.0.0 reads
the bbox in the layer's native CRS, not in the srsName you asked the output in. So
this pages with WFS 2.0.0 count/startIndex, which needs no CRS at all, and clips to
the window afterwards.

Writes data/raw/structures/{rist,broend}.json - lists of [lon, lat, z, type, date].
"""
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import RAW, fetch, log

WFS = "https://wfs-kbhkort.kk.dk/k101/ows"
# Copenhagen and the inner suburbs, the same window the architecture view uses.
BOX = (12.40, 55.58, 12.74, 55.76)
TILES = 6
LAYERS = {
    "rist": ("ristetype", "gully gratings"),
    "broend": ("broendtype", "manholes and wells"),
}


def page_url(layer, start, count):
    q = {
        "service": "WFS", "version": "2.0.0", "request": "GetFeature",
        "typeNames": "k101:" + layer, "outputFormat": "application/json",
        "srsName": "EPSG:4326", "count": str(count), "startIndex": str(start),
    }
    return WFS + "?" + urllib.parse.urlencode(q)


def points(geom):
    """Both layers are MultiPoint, usually of one point. Take them all."""
    if not geom:
        return []
    if geom["type"] == "Point":
        return [geom["coordinates"]]
    if geom["type"] == "MultiPoint":
        return geom["coordinates"]
    return []


def main():
    out_dir = os.path.join(RAW, "structures")
    os.makedirs(out_dir, exist_ok=True)
    PAGE = 5000
    for layer, (type_field, what) in LAYERS.items():
        rows, start, kept_out = [], 0, 0
        while True:
            try:
                raw = fetch(page_url(layer, start, PAGE), timeout=240)
                d = json.loads(raw.decode("utf-8"))
            except Exception as e:
                log(f"  {layer} page at {start:,} failed: {e}")
                break
            feats = d.get("features", [])
            for f in feats:
                p = f.get("properties") or {}
                for c in points(f.get("geometry")):
                    lon, lat = float(c[0]), float(c[1])
                    if not (BOX[0] <= lon <= BOX[2] and BOX[1] <= lat <= BOX[3]):
                        kept_out += 1
                        continue
                    rows.append([round(lon, 7), round(lat, 7),
                                 (round(float(c[2]), 2) if len(c) > 2 else None),
                                 p.get(type_field),
                                 (p.get("registreringfra_dato") or "")[:10]])
            n = len(feats)
            del d, feats
            start += PAGE
            if n < PAGE:
                break
            if start % 25000 == 0:
                log(f"    {layer}: {start:,} read, {len(rows):,} in window")
        path = os.path.join(out_dir, layer + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rows, f, separators=(",", ":"))
        dated = sorted(r[4] for r in rows if r[4])
        log(f"  {layer}: {len(rows):,} {what} in the window "
            f"({kept_out:,} outside it), dates "
            f"{dated[0] if dated else '?'} to {dated[-1] if dated else '?'}, "
            f"median {dated[len(dated)//2] if dated else '?'}")
        log(f"    -> {path} ({os.path.getsize(path)/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
