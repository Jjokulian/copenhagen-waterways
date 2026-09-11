#!/usr/bin/env python3
"""Facts the hypothesis drafts cite from held files, computed and stored.

Companion to hypodraft_ctd.py, for everything that does not need the CTD
extract: file row counts, station counts, spans, layer feature counts and the
like, which the drafts in docs/hypodrafts/ once typed from one-off checks. Each
is re-derived here from the file named and written to
data/derived/hypodraft_facts.json, so a page reads it live.

    scripts/heavy python3 scripts/hypodraft_facts.py
"""
import collections
import csv
import glob
import gzip
import io
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, ROOT, log

OUT = os.path.join(DERIVED, "hypodraft_facts.json")


def num(s):
    try:
        return float((s or "").replace(",", "."))
    except ValueError:
        return None


def gz_rows(path):
    with gzip.open(path, "rb") as fh:
        yield from csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";")


def weather():
    years = set()
    for f in sorted(glob.glob(os.path.join(RAW, "weather", "wind_*.json"))):
        for t in json.load(open(f, encoding="utf-8"))["hourly"]["time"]:
            years.add(int(t[:4]))
    return {"n_years": len(years), "first_year": min(years), "last_year": max(years)}


def maaledybde():
    rows, with_bottom = 0, set()
    for r in gz_rows(os.path.join(RAW, "oda", "maaledybde.csv.gz")):
        rows += 1
        if num(r.get("BundDybde_m")) is not None:
            with_bottom.add(r.get("ObservationsstedNr"))
    return {"rows": rows, "stations_with_bottom": len(with_bottom)}


def lys():
    rows, coords = 0, set()
    for r in gz_rows(os.path.join(RAW, "oda", "lys.csv.gz")):
        rows += 1
        if num(r.get("X_UTM32")) is not None and num(r.get("Y_UTM32")) is not None:
            coords.add(r.get("ObservationsStedNr"))
    return {"rows": rows, "stations_with_coordinates": len(coords)}


def kemi():
    orthop = set()
    for r in gz_rows(os.path.join(RAW, "oda", "kemi.csv.gz")):
        if r.get("Parameter") == "Ortho-phosphat-P":
            orthop.add(r.get("ObservationsStedNr"))
    return {"orthophosphate_stations": len(orthop)}


def seabed():
    c = sqlite3.connect(os.path.join(RAW, "geus", "seabed_sediment_dk.gpkg"))
    scales = [r[0] for r in c.execute("select scale from Seabed_sedimen") if r[0]]
    return {"polygons": c.execute("select count(*) from Seabed_sedimen").fetchone()[0],
            "mapping_programmes": len({r[0] for r in c.execute("select kortlaegni from Seabed_sedimen")}),
            "scale_min": min(scales), "scale_max": max(scales)}


def areas():
    a = json.load(open(os.path.join(ROOT, "docs", "data", "areas", "areas.json"), encoding="utf-8"))
    return {"n": len(a["areas"])}


def series():
    s = json.load(open(os.path.join(ROOT, "docs", "data", "areas", "stations_series.json"), encoding="utf-8"))
    return {"station_months": sum(v["n"] for v in s["variables"]),
            "stations": len(s["stations"]), "variables": len(s["variables"])}


def series_by_variable():
    """Values and distinct stations per variable of the monthly station series,
    read from the binary layout its .json describes."""
    import numpy as np
    base = os.path.join(ROOT, "docs", "data", "areas")
    s = json.load(open(os.path.join(base, "stations_series.json"), encoding="utf-8"))
    raw = open(os.path.join(base, "stations_series.bin"), "rb").read()
    out = {}
    for v in s["variables"]:
        st = np.frombuffer(raw, dtype=np.uint16, count=v["n"], offset=v["offset"])
        out[v["key"]] = {"n": v["n"], "stations": int(len(np.unique(st)))}
    return {"months": s["months"], "year0": s["year0"], "by_variable": out,
            "bin_bytes": len(raw)}


def stations_register():
    rows, st, transect = 0, set(), set()
    first, last = None, None
    with open(os.path.join(RAW, "oda", "stations.csv"), encoding="latin-1") as f:
        for r in csv.DictReader(f, delimiter=";"):
            rows += 1
            k = r.get("ObservationsstedNr")
            st.add(k)
            if (r.get("TransektSlutX_UTM32") or "").strip():
                transect.add(k)
            for d in ((r.get("StartDato") or "").strip(), (r.get("SlutDato") or "").strip()):
                if len(d) == 8 and d.isdigit():
                    first = d if first is None or d < first else first
                    last = d if last is None or d > last else last
    iso = lambda d: f"{d[:4]}-{d[4:6]}-{d[6:]}" if d else None
    return {"rows": rows, "stations": len(st), "with_transect_end": len(transect),
            "first_date": iso(first), "last_date": iso(last)}


def layers():
    hov = json.load(open(os.path.join(RAW, "national", "hovedoplande.geojson"), encoding="utf-8"))
    with gzip.open(os.path.join(RAW, "oda", "ctd.csv.gz"), "rt", encoding="latin-1") as fh:
        ncol = len(fh.readline().rstrip("\n").split(";"))
    return {"hovedoplande_features": len(hov["features"]),
            "ctd_bytes": os.path.getsize(os.path.join(RAW, "oda", "ctd.csv.gz")),
            "ctd_columns": ncol}


def enums():
    e = json.load(open(os.path.join(DERIVED, "enums.json"), encoding="utf-8"))["ctd"]["categorical"]
    return {"probe_ids_known": len([k for k in e["SondeNr"] if k != "999"]),
            "technical_instruction_values": len(e["TekniskAnvisningAnvendt"]),
            "supplier_values": len(e["DataleverandørNavn"])}


def hazardous():
    """The national river-basin-specific-pollutant status network: its stations,
    by the kind of water body they belong to, and how many measure sediment."""
    fs = json.load(open(os.path.join(RAW, "national", "sw_mfs_tilstand.geojson"),
                        encoding="utf-8"))["features"]
    p = [f["properties"] for f in fs]
    body = lambda x, pre: (x.get("eusurfacew") or "").startswith(pre)
    return {"total": len(p), "sediment": sum(x.get("maaltsedim") == "Ja" for x in p),
            "lake": sum(body(x, "DKLAKE") for x in p), "river": sum(body(x, "DKRIVER") for x in p),
            "coast": sum(body(x, "DKCOAST") for x in p)}


def sign_flips():
    f = json.load(open(os.path.join(ROOT, "docs", "data", "areas", "flags.json"), encoding="utf-8"))
    fl = [x for x in f["flags"] if x["flag"] == "batch_sign_flip"]
    months = sorted({x["month"] for x in fl})
    return {"station_months": len(fl), "stations": len({x["station"] for x in fl}),
            "first_month": months[0] if months else None, "last_month": months[-1] if months else None}


def main(argv):
    out = {"_what": "Facts the hypothesis drafts cite from held files, re-derived by "
                    "scripts/hypodraft_facts.py."}
    for name, fn in (("weather", weather), ("maaledybde", maaledybde), ("lys", lys),
                     ("kemi", kemi), ("seabed", seabed), ("areas", areas), ("series", series),
                     ("enums", enums), ("hazardous", hazardous), ("sign_flips", sign_flips),
                     ("series_by_variable", series_by_variable),
                     ("stations_register", stations_register), ("layers", layers)):
        out[name] = fn()
        log(f"  {name}: {out[name]}")
    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
