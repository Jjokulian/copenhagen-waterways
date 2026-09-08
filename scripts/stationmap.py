#!/usr/bin/env python3
"""Every ODA marine station, positioned, with which streams it carries.

The 4D map drew 1,018 grey dots and its legend called them the only long repeated
marine series in Danish open data. They were bathing-water stations, and that claim
is false: ODA's register holds 6,258 positioned marine stations, and the topic
extracts show 1,527 of them carrying CTD profiles back to 1970.

This emits all of them, with a per-station flag for each topic, so the map can show
which instrument was ever in the water at a place rather than one programme's
stations captioned as though they were the whole observing system.

Reads   data/raw/oda/stations.csv, data/raw/oda/*_stations.tsv
Writes  docs/data/areas/stations.json
"""
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RAW, ROOT, log, write_json
from cube import num, utm32_to_wgs84

TOPICS = [("ctd", "CTD profiles"), ("lys", "Light attenuation"),
          ("maaledybde", "Secchi and bottom depth")]


def main():
    members = {}
    for key, label in TOPICS:
        p = os.path.join(RAW, "oda", f"{key}_stations.tsv")
        if not os.path.exists(p):
            log(f"  {key}: no station list")
            continue
        got = set()
        with open(p, encoding="utf-8") as fh:
            r = csv.DictReader(fh, delimiter="\t")
            for row in r:
                nr = (row.get("nr") or "").strip()
                if nr:
                    got.add(nr)
        members[key] = got
        log(f"  {key:12} {len(got):,} stations")

    out, seen = [], set()
    with open(os.path.join(RAW, "oda", "stations.csv"), encoding="iso-8859-1") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            if (row.get("Observationsstedtype") or "").strip() != "Hav":
                continue
            nr = (row.get("ObservationsstedNr") or "").strip()
            if nr in seen:
                continue
            X, Y = num(row.get("X_UTM32")), num(row.get("Y_UTM32"))
            if X is None or Y is None or X < 100000 or Y < 5_000_000:
                continue
            seen.add(nr)
            lon, lat = utm32_to_wgs84(X, Y)
            flags = sum(1 << i for i, (k, _) in enumerate(TOPICS)
                        if nr in members.get(k, ()))
            out.append([round(lon, 4), round(lat, 4), flags])
    write_json(os.path.join(ROOT, "docs", "data", "areas", "stations.json"),
               {"_what": "Every ODA marine observation station with a position. "
                         "Third element is a bitmask over the topics listed in "
                         "'topics'; 0 means the station is in the register but "
                         "carries none of the extracted topics.",
                "topics": [t[1] for t in TOPICS],
                "n": len(out), "stations": out})
    with_any = sum(1 for s in out if s[2])
    log(f"  {len(out):,} positioned marine stations, {with_any:,} carrying an "
        f"extracted topic")
    return 0


if __name__ == "__main__":
    sys.exit(main())
