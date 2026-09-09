"""How much manure has to leave the farm that made it.

NITROGEN.md predicts that a per-catchment nitrogen quota bites on mineral
fertiliser first and only later on the herd - and that when it does, the manure
nitrogen has to leave the holding, because the animals are not optional. That
prediction can be checked today rather than after the law bites, because both halves
are in open registers:

  CHR     every livestock site, with the business that runs it and its animal units
          (`DE`, the unit the manure regulation itself uses)
  Marker  every declared field parcel, with the operator's CVR and its area

They join on CVR. A business whose animal units exceed what its own declared land can
take is a business that must place manure somewhere else - a contract with a
neighbour, a separation plant, or an export.

**Both layers were found by the sibling project `danish-livestock`, which mapped the
57,860 sites and documented the two traps below; this script fetches from the same
primary source rather than copying its data.**

Two traps, from that documentation and confirmed here:
  * GeoServer's JSON writer declares UTF-8 and emits ISO-8859-1.
  * The herd-size columns do not always partition the herd, so `DE` is the only
    measure that is comparable across species - which is why this uses it.

The threshold is stated, not measured: 1.4 and 1.7 DE/ha are the classic harmony
limits. Denmark moved to a kg N/ha rule in 2017, so these are indicative of the
pressure rather than a test of legal compliance.

Writes data/derived/manure.json.
"""
import csv
import io
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, fetch, log

WFS = "https://geodata.fvm.dk/geoserver/ows"
CHR_LAYER = "Jordbrugsanalyser:CHR24"
MARKER_LAYER = "Marker:Marker_2025"
LIMITS = (1.4, 1.7, 2.3)


def wfs_fold(layer, fields, fold, page=20000):
    """Attributes only, as CSV, folded a page at a time.

    Skipping geometry turns gigabytes into megabytes - and folding rather than
    collecting keeps 616,000 parcels from ever existing as 616,000 dicts, which is
    the difference between running here and taking the machine down with it.
    """
    start, seen = 0, 0
    while True:
        q = {"service": "WFS", "version": "2.0.0", "request": "GetFeature",
             "typeNames": layer, "outputFormat": "csv", "propertyName": fields,
             "count": str(page), "startIndex": str(start)}
        raw = fetch(WFS + "?" + urllib.parse.urlencode(q), timeout=300)
        text = raw.decode("latin-1")            # the writer lies about its encoding
        n = 0
        for row in csv.DictReader(io.StringIO(text)):
            fold(row)
            n += 1
        del text, raw
        seen += n
        log(f"    {layer}: {seen:,} rows")
        if n < page:
            return seen
        start += page


def num(x):
    try:
        return float(str(x).replace(",", "."))
    except Exception:
        return 0.0


def main():
    de_by_cvr, counter = {}, [0]

    def take_site(r):
        counter[0] += 1
        cvr = (r.get("CVRNR") or "").strip()
        if cvr and cvr != "0":
            de_by_cvr[cvr] = de_by_cvr.get(cvr, 0.0) + num(r.get("DE"))

    wfs_fold(CHR_LAYER, "CVRNR,DE,DYRKODE", take_site)
    sites = counter[0]
    total_de = sum(de_by_cvr.values())

    ha_by_cvr = {}

    def take_parcel(r):
        cvr = (r.get("CVR") or "").strip()
        if cvr:
            ha_by_cvr[cvr] = ha_by_cvr.get(cvr, 0.0) + num(r.get("IMK_areal"))

    wfs_fold(MARKER_LAYER, "CVR,IMK_areal", take_parcel)

    both = [(c, de_by_cvr[c], ha_by_cvr[c]) for c in de_by_cvr
            if ha_by_cvr.get(c, 0) > 1 and de_by_cvr[c] > 0]
    ratios = sorted(((d / h, d, h, c) for c, d, h in both), reverse=True)
    vals = [x[0] for x in ratios]

    def pct(p):
        return vals[min(len(vals) - 1, int(len(vals) * (1 - p / 100)))] if vals else 0

    over = {}
    for lim in LIMITS:
        n = sum(1 for v in vals if v > lim)
        d = sum(x[1] for x in ratios if x[0] > lim)
        over[str(lim)] = {"businesses": n, "share_of_businesses_pct": 100 * n / len(vals),
                          "animal_units": d, "share_of_herd_pct": 100 * d / total_de}

    out = {
        "_what": "Animal units against declared land, per business, from two open "
                 "registers that join on CVR.",
        "_source": {"chr": CHR_LAYER, "marker": MARKER_LAYER, "wfs": WFS,
                    "found_by": "the sibling project danish-livestock, which mapped "
                                "these layers and documented their traps"},
        "_stated": "1.4 / 1.7 / 2.3 DE per hectare are the classic harmony limits. "
                   "Denmark moved to a kg N/ha rule in 2017, so these indicate "
                   "pressure rather than legal compliance.",
        "sites": sites,
        "cvrs_with_animals": len(de_by_cvr),
        "cvrs_with_land": len(ha_by_cvr),
        "cvrs_with_both": len(both),
        "animal_units_total": total_de,
        "animal_units_on_matched": sum(x[1] for x in both),
        "percentiles_de_per_ha": {str(p): pct(p) for p in (50, 75, 90, 95, 99)},
        "over_limit": over,
    }
    p = os.path.join(DERIVED, "manure.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    log(f"  {sites:,} sites, {len(de_by_cvr):,} CVRs with animals, "
        f"{total_de:,.0f} animal units")
    log(f"  {len(both):,} businesses have both animals and declared land")
    for lim in LIMITS:
        o = over[str(lim)]
        log(f"  above {lim} DE/ha: {o['businesses']:,} businesses "
            f"({o['share_of_businesses_pct']:.0f}%), {o['animal_units']:,.0f} "
            f"animal units ({o['share_of_herd_pct']:.0f}% of the herd)")
    log(f"  wrote {p}")


if __name__ == "__main__":
    main()
