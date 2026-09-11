#!/usr/bin/env python3
"""Counts the hypothesis drafts and open problems quote from files held in this repository.

Earlier sessions counted these by hand in a shell and typed the results into the
drafts in docs/hypodrafts/ and docs/openproblems/. Here they are counted by a
script and stored, so the pages read them live, and a change in a file shows up
as a changed number instead of a stale one. Every field is declared in
data/manual/number_constructions.d/drafts-b.json.

Counts an earlier session made from EXTERNAL sources (OBIS, EMODnet, PANGAEA,
downloaded reports) are not here: nothing in the repository holds them, so the
pages carry them as quotations of the draft as committed, which is what they are.

    scripts/heavy python3 scripts/drafts_b_counts.py

Writes data/derived/drafts_b_counts.json.
"""
import collections
import csv
import gzip
import io
import json
import os
import re
import sqlite3
import sys
from array import array

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, MANUAL, RAW, ROOT, log

SERIES = os.path.join(ROOT, "docs", "data", "areas", "stations_series.json")
SERIES_BIN = os.path.join(ROOT, "docs", "data", "areas", "stations_series.bin")
PORTAL = os.path.join(MANUAL, "data_sources_2.json")
MAALEDYBDE = os.path.join(RAW, "oda", "maaledybde.csv.gz")
SEABED = os.path.join(RAW, "geus", "seabed_sediment_dk.gpkg")
MFS = os.path.join(RAW, "national", "sw_mfs_tilstand.geojson")
OUT = os.path.join(DERIVED, "drafts_b_counts.json")
# the ODA topics the drafts cite, by the name data_sources_2.json records them under
PORTAL_TOPICS = {"ctd": "Feltmaaling / CTD", "vandkemi": "Vandkemi",
                 "sedimentkemi_sporstof": "Sedimentkemi Sporstof",
                 "lyssvaekkelse": "Lyssvaekkelse", "maaledybde": "Maaledybde"}


def series():
    """The monthly station panel: totals, and distinct stations per variable read
    from the binary itself (n uint16 station indices at each variable's offset)."""
    meta = json.load(open(SERIES, encoding="utf-8"))
    raw = open(SERIES_BIN, "rb").read()
    out = {"total_station_months": sum(v["n"] for v in meta["variables"]),
           "n_stations": len(meta["stations"]), "months": meta["months"],
           "n_variables": len(meta["variables"]), "bin_bytes": len(raw), "variables": {}}
    for v in meta["variables"]:
        idx = array("H")
        idx.frombytes(raw[v["offset"]:v["offset"] + 2 * v["n"]])
        out["variables"][v["key"]] = {"n": v["n"], "stations": len(set(idx))}
    return out


def portal():
    """Station counts the ODA portal returned, as recorded by hand in the register."""
    d = json.load(open(PORTAL, encoding="utf-8"))
    entry = next(s for s in d["sources"] if s.get("id") == "ODA-STATION-COUNTS-CORRECTION")
    out = {}
    for slug, name in PORTAL_TOPICS.items():
        key = next(k for k in entry["verified_counts"] if k.split(" (")[0] == name)
        m = re.fullmatch(r"([\d,]+) with no period, ([\d,]+) with 1970-2026",
                         entry["verified_counts"][key].strip())
        out[slug] = {"no_period": int(m.group(1).replace(",", "")),
                     "with_period": int(m.group(2).replace(",", ""))}
    return out


def maaledybde():
    rows, st, bund, same_x = 0, set(), set(), 0
    with gzip.open(MAALEDYBDE, "rb") as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";"):
            rows += 1
            s = r.get("ObservationsstedNr")
            st.add(s)
            if (r.get("BundDybde_m") or "").strip():
                bund.add(s)
            if r.get("X_UTM32") == r.get("X_UTM321"):
                same_x += 1
    return {"rows": rows, "stations": len(st), "stations_with_bottom_depth": len(bund),
            "rows_x_equals_x1": same_x}


def seabed():
    c = sqlite3.connect(f"file:{SEABED}?mode=ro", uri=True)
    q = lambda sql: c.execute(sql).fetchall()
    out = {"features": q("select count(*) from Seabed_sedimen")[0][0],
           "classes": q("select count(distinct sedimenten) from Seabed_sedimen")[0][0],
           "by_class": {k: n for k, n in q("select sedimenten, count(*) from Seabed_sedimen "
                                           "group by sedimenten")},
           "by_scale": {str(k): n for k, n in q("select scale, count(*) from Seabed_sedimen "
                                                "group by scale")},
           "campaigns": q("select count(distinct mapping) from Seabed_sedimen")[0][0]}
    c.close()
    return out


def mfs():
    """The national layer that carries river-basin-specific pollutant status."""
    props = [f["properties"] for f in json.load(open(MFS, encoding="utf-8"))["features"]]
    flag = lambda v: str(v).strip().lower() not in ("", "none", "0", "nej", "false")
    kind = collections.Counter(re.match(r"[A-Z]*", p.get("eusurfacew") or "").group(0) for p in props)
    return {"points": len(props), "by_type": dict(kind),
            "biota": sum(flag(p.get("maaltbiota")) for p in props),
            "water": sum(flag(p.get("maaltvand")) for p in props),
            "sediment": sum(flag(p.get("maaltsedim")) for p in props),
            "no_matrix": sum(not any(flag(p.get(k)) for k in ("maaltbiota", "maaltvand", "maaltsedim"))
                             for p in props),
            "distinct_qecode": len({p.get("qecode") for p in props}),
            "distinct_qestatusor": len({p.get("qestatusor") for p in props}),
            "distinct_da_oekolog": len({p.get("da_oekolog") for p in props}),
            "distinct_aktivstart": len({p.get("aktivstart") for p in props})}



def plankton():
    """The CMEMS phytoplankton grid on disk: yearly files, their span, which year is
    partial (well under the typical size), and the data variables in the newest file.
    The variables need netCDF4, which lives in the marine venv, not in the build's
    Python - so they are read there, and a missing venv is an error, not a guess."""
    import glob, statistics, subprocess
    files = sorted(glob.glob(os.path.join(RAW, "cmems", "grid", "plankton__inner__*.nc")))
    years = [int(re.search(r"__(\d{4})\.nc$", f).group(1)) for f in files]
    sizes = [os.path.getsize(f) for f in files]
    typical = statistics.median(sizes) if sizes else 0
    venv = os.path.expanduser("~/.venvs/marine/bin/python")
    r = subprocess.run([venv, "-c", "import netCDF4, sys, json; d = netCDF4.Dataset(sys.argv[1]); "
                        "print(json.dumps([v for v in d.variables if v not in d.dimensions]))",
                        files[-1]], capture_output=True, text=True, check=True)
    variables = json.loads(r.stdout)
    return {"n_files": len(files), "first_year": min(years), "last_year": max(years),
            "partial_years": [y for y, z in zip(years, sizes) if z < typical / 2],
            "variables": variables, "n_variables": len(variables)}

def main(argv):
    out = {"_what": "Counts of files held in this repository that the hypothesis drafts "
                    "and open problems quote, each read by this script rather than typed.",
           "stations_series": series(), "oda_portal": portal(),
           "maaledybde": maaledybde(), "seabed": seabed(), "mfs": mfs()}
    os.makedirs(DERIVED, exist_ok=True)
    out["plankton"] = plankton()
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
