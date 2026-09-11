#!/usr/bin/env python3
"""Facts the hypothesis drafts cite from the CTD extract, computed and stored.

The drafts in docs/hypodrafts/ were written with counts "verified in this
session" by one-off passes over data/raw/oda/ctd.csv.gz that stored nothing. A
number nobody can re-derive is a typed number. This pass re-derives the ones
the drafts actually print, from the whole file, and writes them where a page
can read them live: data/derived/hypodraft_ctd.json.

  C1   station-days carrying temperature and salinity, with at least
       `MIN_LEVELS` distinct depths of each, with oxygen in mg/l, joined to a
       recorded bottom depth, reaching `DEEP_M`; deepest oxygen within
       `NEAR_M` of the deepest temperature; distinct stations and years.
  I5   rows whose KorrektionsFaktor is exactly one, and rows whose original
       and corrected results differ.
  E12  Dihydrogensulfid rows per station.
  Z2   first and last year of FDOM.
  C1   SondeNavn '999 - Ukendt' rows for temperature, salinity and oxygen.
  C6   temperature values carrying at most one decimal.

A station-day is one ObservationsStedNr on one Dato. Rows are grouped by a
flush on key change, not a dict of every key: the extract is written cast by
cast. A key that reopens after it was flushed is counted (`reopened_keys`) and
its second run treated as a separate station-day - the count says how much that
matters. Peak memory is the set of flushed C1 keys, one small tuple per
station-day.

    scripts/heavy python3 scripts/hypodraft_ctd.py

Reads data/raw/oda/ctd.csv.gz and data/raw/oda/maaledybde.csv.gz.
Writes data/derived/hypodraft_ctd.json.
"""
import collections
import csv
import gzip
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, ROOT, log

CTD = os.path.join(RAW, "oda", "ctd.csv.gz")
MAAL = os.path.join(RAW, "oda", "maaledybde.csv.gz")
OUT = os.path.join(DERIVED, "hypodraft_ctd.json")
MIN_LEVELS = 4        # distinct depths of T and of S for a usable density profile
NEAR_M = 1.5          # deepest oxygen this close to the deepest temperature
DEEP_M = 10.0         # a profile "reaching" deep water, in metres
T, S, O = "Temperatur", "Salinitet", "Oxygen indhold"


def num(s):
    try:
        return float((s or "").replace(",", "."))
    except ValueError:
        return None


def main(argv):
    maxrows = next((int(a.split("=", 1)[1]) for a in argv if a.startswith("--max-rows=")), 0)
    # bottom depth per station-day, from the depth register
    maal_days, maal_bottom = set(), set()
    with gzip.open(MAAL, "rb") as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";"):
            k = (r.get("ObservationsstedNr"), (r.get("StartDato") or "").strip())
            maal_days.add(k)
            if num(r.get("BundDybde_m")) is not None:
                maal_bottom.add(k)
    log(f"  maaledybde: {len(maal_days):,} station-days, {len(maal_bottom):,} with a bottom depth")

    rows = factor_one = factor_other = factor_blank = differ = both_results = 0
    h2s = collections.Counter()
    fdom_years = []
    unknown_probe = collections.Counter()
    temp_total = temp_le1dec = 0
    c = collections.Counter()
    stations, years = set(), set()
    flushed, reopened = set(), 0
    cur, depths = None, None

    def flush(key, d):
        nonlocal reopened
        if key in flushed:
            reopened += 1
        flushed.add(key)
        nt, ns, no = len(d[T]), len(d[S]), len(d[O])
        if not (nt and ns):
            return
        c["ts"] += 1
        stations.add(key[0])
        years.add(key[1][:4])
        if nt >= MIN_LEVELS and ns >= MIN_LEVELS:
            c["ts_levels"] += 1
            if no:
                c["ts_levels_o"] += 1
                if key in maal_bottom:
                    c["ts_levels_o_bottom"] += 1
                    if max(d[T]) >= DEEP_M:
                        c["ts_levels_o_bottom_deep"] += 1
        if no and max(d[O]) >= max(d[T]) - NEAR_M:
            c["o_near_deepest_t"] += 1

    log(f"reading {os.path.relpath(CTD, ROOT)}")
    with gzip.open(CTD, "rb") as fh:
        rd = csv.reader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";")
        h = next(rd)
        ix = {name: i for i, name in enumerate(h)}
        i_st, i_d, i_p, i_u = ix["ObservationsStedNr"], ix["Dato"], ix["Parameter"], ix["Enhed"]
        i_z, i_k, i_o, i_r = ix["Dybde (m)"], ix["KorrektionsFaktor"], ix["OriginalResultat"], ix["KorrigeretResultat"]
        i_sn = ix["SondeNavn"]
        for row in rd:
            if len(row) != len(h):
                continue
            rows += 1
            if maxrows and rows > maxrows:
                break
            if rows % 10_000_000 == 0:
                log(f"  {rows:,} rows")
            k = (row[i_k] or "").strip()
            if not k:
                factor_blank += 1
            elif num(k) == 1.0:
                factor_one += 1
            else:
                factor_other += 1
            o, r = (row[i_o] or "").strip(), (row[i_r] or "").strip()
            if o and r:
                both_results += 1
                if num(o) != num(r):
                    differ += 1
            p = row[i_p]
            st, d = row[i_st], (row[i_d] or "").strip()
            if p == "Dihydrogensulfid":
                h2s[st] += 1
            elif p == "FDOM" and len(d) == 8:
                fdom_years.append(int(d[:4]))
            if p in (T, S, O) and row[i_sn].startswith("999"):
                unknown_probe[p] += 1
            if p == T:
                temp_total += 1
                v = o.split(",")
                if len(v) == 1 or len(v[1]) <= 1:
                    temp_le1dec += 1
            if p not in (T, S, O) or len(d) != 8:
                continue
            if p == O and (row[i_u] or "").strip() != "mg/l":
                continue
            z = num(row[i_z])
            if z is None:
                continue
            key = (st, d)
            if key != cur:
                if cur is not None:
                    flush(cur, depths)
                cur, depths = key, {T: set(), S: set(), O: set()}
            depths[p].add(z)
        if cur is not None:
            flush(cur, depths)

    top = h2s.most_common(1)[0] if h2s else (None, 0)
    out = {
        "_what": "Counts the hypothesis drafts cite from the CTD extract, re-derived from "
                 "the whole file by scripts/hypodraft_ctd.py.",
        "rows": rows,
        "c1": {"min_levels": MIN_LEVELS, "near_m": NEAR_M, "deep_m": DEEP_M,
               "station_days_ts": c["ts"], "with_levels": c["ts_levels"],
               "with_levels_and_oxygen": c["ts_levels_o"],
               "with_levels_oxygen_bottom": c["ts_levels_o_bottom"],
               "with_levels_oxygen_bottom_deep": c["ts_levels_o_bottom_deep"],
               "oxygen_near_deepest_t": c["o_near_deepest_t"],
               "stations": len(stations), "first_year": int(min(years)) if years else None,
               "last_year": int(max(years)) if years else None,
               "reopened_keys": reopened,
               "maaledybde_station_days": len(maal_days),
               "maaledybde_with_bottom": len(maal_bottom),
               "unknown_probe_rows": {"temperature": unknown_probe[T],
                                      "salinity": unknown_probe[S],
                                      "oxygen": unknown_probe[O]}},
        "correction": {"rows": rows, "factor_one": factor_one, "factor_other": factor_other,
                       "factor_blank": factor_blank, "rows_with_both_results": both_results,
                       "original_differs": differ},
        "h2s": {"rows": sum(h2s.values()), "stations": len(h2s),
                "top_station": top[0], "top_station_rows": top[1]},
        "fdom": {"rows": len(fdom_years), "first_year": min(fdom_years) if fdom_years else None,
                 "last_year": max(fdom_years) if fdom_years else None},
        "temperature_decimals": {"rows": temp_total, "at_most_one_decimal": temp_le1dec},
    }
    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(json.dumps(out["c1"], indent=1))
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
