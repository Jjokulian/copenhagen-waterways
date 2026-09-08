#!/usr/bin/env python3
"""Ask a satellite whether a water body is one thing.

OBSERVING.md tests that question with bathing water, because bathing water is the
only dense replicated marine record Denmark has. It answers it - a water body
explains about 8% of the variation inside it - but with a faecal indicator, which
is not the variable anyone is arguing about.

A satellite has no such limitation. It sees every pixel of every water body on the
same day with the same instrument, which is complete spatial replication of an
optical variable, and it has been doing so since 2015. So the question X14 proposes
buying forty sensors to answer is already answered in the archive, for the decade
that has passed, for the variables light and colour.

The mechanism is Sentinel Hub's Statistical API, which is the important part: the
pixels stay on Copernicus infrastructure and only the summary travels. A request
names a polygon, a period and an evalscript, and returns mean, standard deviation
and percentiles per interval. **The standard deviation within one polygon is the
spatial heterogeneity of that water body** - which is exactly the quantity the
one-station-per-water-body assumption requires to be small.

Two numbers come back per area per interval, and the second is the one that
matters:

    mean    the water's colour - a turbidity and chlorophyll proxy
    stDev   how much that colour varies ACROSS the polygon on a single day

Honest limits, stated here because they bound every conclusion drawn downstream:

  * Coastal water is optically complex. Reflectance is a proxy for turbidity, not a
    calibrated measurement of it, and the mineral, chlorophyll and CDOM
    contributions are not separated by this script. Separating them needs the
    regionally tuned CMEMS products - which is the point of Z8 and a different
    fetch.
  * Cloud. Denmark loses most days, and residual cloud is the main source of
    spurious high values. Pixels are masked on the scene classification, which is
    imperfect at water edges.
  * Sentinel-2 revisits every few days at 10-20 m; good for fjords, poor for daily
    dynamics. Sentinel-3 is daily at 300 m: better cadence, too coarse for the
    narrow areas. This uses Sentinel-2 because most Danish water bodies are small.
  * A satellite sees the surface. Everything about bottom water is invisible to it.

Reads   data/derived/areas.json  (polygon centroids and areas)
        ~/.cdse-client-id, ~/.cdse-client-secret
Writes  data/raw/satellite/watercolour.json

Usage:  python3 scripts/fetch_satellite.py [--limit N] [--from YYYY-MM-DD] [--to ...]
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, log, read_json, write_json

TOKEN_URL = ("https://identity.dataspace.copernicus.eu/auth/realms/CDSE"
             "/protocol/openid-connect/token")
STATS_URL = "https://sh.dataspace.copernicus.eu/api/v1/statistics"
DEST = os.path.join(RAW, "satellite")

# Sentinel-2 scene classification: 6 is water. 3, 8, 9, 10 are shadow, cloud
# medium, cloud high and cirrus - excluded, because residual cloud over water is
# the dominant source of spurious brightness.
EVALSCRIPT = """//VERSION=3
function setup() {
  return {
    input: [{bands: ["B03", "B04", "B08", "SCL", "dataMask"]}],
    output: [{id: "idx", bands: 2, sampleType: "FLOAT32"},
             {id: "dataMask", bands: 1}]
  };
}
function evaluatePixel(s) {
  var water = (s.SCL === 6) ? 1 : 0;
  var clear = (s.SCL !== 3 && s.SCL !== 8 && s.SCL !== 9 && s.SCL !== 10) ? 1 : 0;
  // B04 (red) rises with suspended matter; B03/B04 shifts with what is suspended
  var ratio = s.B04 > 0 ? s.B03 / s.B04 : 0;
  return {idx: [s.B04, ratio], dataMask: [s.dataMask * water * clear]};
}"""


def num(v):
    """The API returns the string "NaN" where a statistic is undefined."""
    if v is None or isinstance(v, str):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f          # NaN as a float, too


def token():
    cid = open(os.path.expanduser("~/.cdse-client-id")).read().strip()
    sec = open(os.path.expanduser("~/.cdse-client-secret")).read().strip()
    body = urllib.parse.urlencode({"grant_type": "client_credentials",
                                   "client_id": cid, "client_secret": sec}).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=body),
                                timeout=60) as r:
        return json.load(r)["access_token"]


def stats(tok, bbox, frm, to, interval="P10D", res=0.0015, tries=3):
    body = {
        "input": {"bounds": {"bbox": list(bbox),
                             "properties": {"crs":
                                            "http://www.opengis.net/def/crs/EPSG/0/4326"}},
                  "data": [{"type": "sentinel-2-l2a",
                            "dataFilter": {"mosaickingOrder": "leastCC"}}]},
        "aggregation": {"timeRange": {"from": frm + "T00:00:00Z",
                                      "to": to + "T23:59:59Z"},
                        "aggregationInterval": {"of": interval},
                        "evalscript": EVALSCRIPT,
                        "resx": res, "resy": res},
        "calculations": {"default": {}},
    }
    req = urllib.request.Request(
        STATS_URL, data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + tok,
                 "Content-Type": "application/json"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r), None
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "replace")[:200]
            if e.code in (429, 500, 502, 503) and attempt < tries - 1:
                time.sleep(10 * (attempt + 1))
                continue
            return None, f"HTTP {e.code}: {msg}"
        except Exception as e:
            if attempt < tries - 1:
                time.sleep(10 * (attempt + 1))
                continue
            return None, f"{type(e).__name__}: {e}"
    return None, "exhausted retries"


def bbox_of(area, span_km=None):
    """A box around the area's centroid, sized from its own area."""
    lon, lat = area["centroid"][0], area["centroid"][1]
    # side of a square with the same area, capped so a huge polygon does not
    # become a request the size of the Baltic
    side_km = min((area["area_km2"] ** 0.5), 25.0)
    dlat = side_km / 111.0 / 2
    dlon = dlat / max(0.2, abs(__import__("math").cos(__import__("math")
                                                      .radians(lat))))
    return (round(lon - dlon, 4), round(lat - dlat, 4),
            round(lon + dlon, 4), round(lat + dlat, 4))


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from", dest="frm", default="2023-04-01")
    ap.add_argument("--to", dest="to", default="2023-09-30")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--interval", default="P10D")
    a = ap.parse_args(argv)

    os.makedirs(DEST, exist_ok=True)
    areas = read_json(os.path.join(DERIVED, "areas.json"))["areas"]
    # biggest first: they carry the most pixels and the most stations to compare to
    picked = sorted(areas.values(), key=lambda r: -r["area_km2"])
    if a.limit:
        picked = picked[:a.limit]

    tok = token()
    log(f"  token acquired; {len(picked)} areas, {a.frm}..{a.to}, {a.interval}")
    out, failed = {}, 0
    for i, area in enumerate(picked, 1):
        bb = bbox_of(area)
        r, err = stats(tok, bb, a.frm, a.to, a.interval)
        if err:
            failed += 1
            log(f"  [{i}/{len(picked)}] {area['name'][:30]:30} {err[:70]}")
            time.sleep(2)
            continue
        rows = []
        for x in (r.get("data") or []):
            band = (x.get("outputs", {}).get("idx", {})
                    .get("bands", {}).get("B0", {}).get("stats", {}))
            # an interval with no valid water pixels comes back as the STRING
            # "NaN" rather than as null, which is easy to round() by accident
            m, sd = num(band.get("mean")), num(band.get("stDev"))
            if m is None:
                continue
            n = band.get("sampleCount") or 0
            nodata = band.get("noDataCount") or 0
            rows.append({"from": x["interval"]["from"][:10],
                         "mean": round(m, 5),
                         "stdev": None if sd is None else round(sd, 5),
                         "px": n - nodata})
        out[area["id"]] = {"name": area["name"], "area_km2": area["area_km2"],
                           "bbox": bb, "intervals": rows}
        log(f"  [{i}/{len(picked)}] {area['name'][:30]:30} {len(rows)} intervals")
        time.sleep(1.5)

    p = os.path.join(DEST, "watercolour.json")
    write_json(p, {"_what": "Sentinel-2 water-colour statistics per marine area. "
                            "mean is a turbidity proxy; stdev is spatial "
                            "heterogeneity WITHIN the polygon on one date.",
                   "_limits": "Reflectance proxy, not calibrated turbidity. Cloud "
                              "masked on scene classification, imperfectly. "
                              "Surface only.",
                   "period": [a.frm, a.to], "interval": a.interval,
                   "areas": out})
    log(f"\nwrote {p} ({os.path.getsize(p)/1e3:.0f} KB); "
        f"{len(out)} areas, {failed} failed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
