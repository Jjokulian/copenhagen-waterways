#!/usr/bin/env python3
"""Counts over the four ODA extracts that docs/DATA_SOURCES.md warns about.

The page's archive section is a list of traps in the ODA downloads: units that change
within a parameter, undeclared sentinels, censoring behind a column name, a correction
factor that means different things for different parameters. Each figure it gives is
counted here, over every row of every extract, and stored - so the page states a count
this script made, not a sentence it once printed.

Rows shorter than the header are fragments of a broken note field (see
scripts/clockzone.py); they are counted apart and read no further.

Peak memory: counters keyed by parameter, unit and station (a few thousand entries),
plus the bottom depths of the maaledybde extract (one float per row, about 150,000).
Nothing grows with the size of the ctd extract, which is streamed row by row.

    scripts/heavy python3 scripts/ds_facts.py      # -> data/derived/ds_facts.json
"""
import csv
import gzip
import json
import io
import os
import statistics
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, log, write_json
from formats import num

ODA = os.path.join(RAW, "oda")
OUT = os.path.join(DERIVED, "ds_facts.json")

# Chosen, not measured. Each is stored beside the count it defines.
SHALLOW_M = 3.0             # a nominal depth this shallow enters a surface filter
LIGHT_MAX_PCT = 110.0       # light more than this share of surface light is not reading noise
FACTOR_BAND = (0.5, 2.0)    # a correction factor outside this band is more than an adjustment
# The parameters the technical instruction's nutrient chapter (Kap. 6) covers:
# nutrients, TOC and POC, under the names the kemi extract uses.
NUTRIENTS = ["Ortho-phosphat-P", "Orthophosphat", "Phosphor, total-P", "Nitrogen,total N",
             "Nitrit+nitrat-N", "Nitrit-N", "Nitrat-N", "Ammoniak+ammonium-N", "Ammonium-N",
             "Silicium", "Siliciumdioxid", "Total organisk kulstof",
             "Partikulært organisk kulstof"]
FACTOR_PARAMS = ("Temperatur", "Salinitet", "Fluorescens")
# A section is reread only when its extract or its own code changes: the ctd extract
# takes minutes, and a new kemi count should not cost it.
VERSION = {"kemi": 2, "lys": 2, "maaledybde": 1, "ctd": 1}


def _rows(name):
    """(header index, row iterator) of one extract, decoded as ODA writes it."""
    fh = gzip.open(os.path.join(ODA, name + ".csv.gz"), "rb")
    rd = csv.reader(io.TextIOWrapper(fh, encoding="latin-1", newline=""), delimiter=";")
    head = next(rd)
    return {h: i for i, h in enumerate(head)}, rd


def _col(h, prefix, *contains):
    return next(i for k, i in h.items() if k.startswith(prefix) and all(c in k for c in contains))


class Years:
    def __init__(self):
        self.lo = self.hi = None

    def add(self, s):
        y = s.strip()[:4]
        if len(y) == 4 and y.isdigit():
            self.lo = y if self.lo is None or y < self.lo else self.lo
            self.hi = y if self.hi is None or y > self.hi else self.hi

    def out(self):
        return [int(self.lo), int(self.hi)] if self.lo else None


def kemi():
    h, rd = _rows("kemi")
    P, E, R, A = h["Parameter"], h["Enhed"], h["Resultat"], h["ResultatAttribut"]
    T, D, S = _col(h, "Pr", "vetype"), h["GennemsnitsDybde_m"], h["Startdato"]
    units, lt, notdet = defaultdict(Counter), Counter(), Counter()
    n = short = neg = d99 = integ = shallow = sat_n = 0
    sat_max, years = None, Years()
    for r in rd:
        if len(r) < len(h):
            short += 1
            continue
        n += 1
        p = r[P]
        units[p][r[E]] += 1
        years.add(r[S])
        v = num(r[R])
        if v is not None and v < 0:
            neg += 1
        if r[A] == "<":
            lt[p] += 1
        elif r[A] == "ikke påvist":
            notdet[p] += 1
        dep = num(r[D])
        if dep == 99.0:
            d99 += 1
        if r[T] == "Dybdeintegreret prøve":
            integ += 1
            if dep is not None and dep <= SHALLOW_M:
                shallow += 1
        if p == "Oxygenmætning" and v is not None:
            sat_n += 1
            sat_max = v if sat_max is None or v > sat_max else sat_max
    multi = {p: dict(u) for p, u in units.items() if len([k for k in u if k.strip()]) > 1}
    return {"rows_read": n, "short_rows": short, "years": years.out(),
            "parameters": len(units), "parameters_multi_unit": len(multi), "units": multi,
            "negative_results": neg,
            "nutrient_rows": sum(sum(units[p].values()) for p in NUTRIENTS if p in units),
            "nutrient_rows_censored_lt": sum(lt[p] for p in NUTRIENTS),
            "nutrient_parameters": NUTRIENTS,
            "not_detected_by_parameter": dict(notdet),
            "depth_exactly_99": d99, "integrated": integ, "integrated_shallow": shallow,
            "shallow_threshold_m": SHALLOW_M,
            "saturation_rows": sat_n, "saturation_max_pct": sat_max}


def ctd():
    h, rd = _rows("ctd")
    P, F, O, K, D = h["Parameter"], h["KorrektionsFaktor"], h["OriginalResultat"], \
        h["KorrigeretResultat"], h["Dato"]
    lo, hi = FACTOR_BAND
    per = {p: {"rows": 0, "with_factor": 0, "factor_not_1": 0, "outside_band": 0,
               "max_factor": None} for p in FACTOR_PARAMS}
    n = short = all3 = product = 0
    years = Years()
    for r in rd:
        if len(r) < len(h):
            short += 1
            continue
        n += 1
        if n % 5_000_000 == 0:
            log(f"  ctd: {n:,} rows")
        years.add(r[D])
        f = num(r[F]) if r[F] else None
        if f is not None and r[O] and r[K]:
            o, k = num(r[O]), num(r[K])
            if o is not None and k is not None:
                all3 += 1
                ks = r[K].strip()
                dec = len(ks.split(",", 1)[1]) if "," in ks else 0
                # equal to within the rounding of the stored corrected value
                if abs(k - o * f) <= 0.5 * 10 ** -dec + 1e-9 * abs(k):
                    product += 1
        s = per.get(r[P])
        if s is not None:
            s["rows"] += 1
            if f is not None:
                s["with_factor"] += 1
                if f != 1:
                    s["factor_not_1"] += 1
                if f < lo or f > hi:
                    s["outside_band"] += 1
                if s["max_factor"] is None or f > s["max_factor"]:
                    s["max_factor"] = f
    return {"rows_read": n, "short_rows": short, "years": years.out(),
            "rows_with_all_three": all3, "rows_where_product_holds": product,
            "factor_band": list(FACTOR_BAND), "by_parameter": per}


def lys():
    h, rd = _rows("lys")
    L, Y, D = h["Lysprocent"], h["YIntercept"], h["Dato"]
    NOTE = _col(h, "Lyssv", "Bem")
    TA, AF = h["TekniskAnvisningAnvendt"], h["Afsluttet"]
    n = short = over = y9 = noted = noted_blank = 0
    lmax, years, ta, af = None, Years(), Counter(), Counter()
    for r in rd:
        if len(r) < len(h):
            short += 1
            continue
        n += 1
        years.add(r[D])
        v = num(r[L])
        if v is not None:
            if v > LIGHT_MAX_PCT:
                over += 1
            lmax = v if lmax is None or v > lmax else lmax
        y = r[Y].strip()
        if num(y) == 9999999:
            y9 += 1
        # the migration note says the intercept "was set to 9999999" where the source
        # lacked it; what the column holds on those rows is counted, not assumed
        if "9999999" in r[NOTE]:
            noted += 1
            if not y:
                noted_blank += 1
        ta[r[TA]] += 1
        af[r[AF]] += 1
    return {"rows_read": n, "short_rows": short, "years": years.out(),
            "light_threshold_pct": LIGHT_MAX_PCT, "light_above_threshold": over,
            "light_max_pct": lmax, "yintercept_9999999": y9,
            "yintercept_note_rows": noted, "yintercept_note_blank_rows": noted_blank,
            "teknisk_anvisning_values": dict(ta), "afsluttet_values": dict(af)}


def maaledybde():
    h, rd = _rows("maaledybde")
    B, ST, SV, NAME, D = h["BundDybde_m"], h["SigtTilBund"], h["SigtDybdeMedVandkikkert"], \
        h["ObservationsstedNavn"], h["StartDato"]
    TA = h["TekniskAnvisningAnvendt"]
    n = short = 0
    tilbund, kikkert, ta, years = Counter(), Counter(), Counter(), Years()
    bottom = defaultdict(list)
    for r in rd:
        if len(r) < len(h):
            short += 1
            continue
        n += 1
        years.add(r[D])
        tilbund[r[ST]] += 1
        kikkert[r[SV]] += 1
        ta[r[TA]] += 1
        b = num(r[B])
        if b is not None:
            bottom[r[NAME]].append(b)
    tops = sorted(((max(v), k) for k, v in bottom.items()), reverse=True)[:3]
    station = lambda k: {"station": k, "max_m": max(bottom[k]),
                         "median_m": statistics.median(bottom[k]), "readings": len(bottom[k])}
    hirts = [k for k in bottom if k.strip() == "Hirtshals 15 m"]
    return {"rows_read": n, "short_rows": short, "years": years.out(),
            "secchi_to_bottom": tilbund.get("True", 0),
            "secchi_by_water_telescope": kikkert.get("True", 0),
            "deepest_stations": [station(k) for _, k in tops],
            "hirtshals_15m": station(hirts[0]) if hirts else None,
            "teknisk_anvisning_values": dict(ta)}


def main():
    out = {"_what": "Counts over every row of the four ODA extracts, for the warnings in "
                    "docs/DATA_SOURCES.md. Thresholds are chosen and stored beside what "
                    "they define."}
    try:
        old = json.load(open(OUT, encoding="utf-8"))
    except (OSError, ValueError):
        old = {}
    for name, fn in (("kemi", kemi), ("lys", lys), ("maaledybde", maaledybde), ("ctd", ctd)):
        raw = os.path.join(ODA, name + ".csv.gz")
        st = os.stat(raw)
        sig = f"{name}.csv.gz:{st.st_size}:{int(st.st_mtime)}:v{VERSION[name]}"
        prev = old.get(name) or {}
        # a section written before sections were signed (version 1) stands if the
        # output is newer than its extract
        legacy = ("read_from" not in prev and prev and VERSION[name] == 1
                  and os.path.getmtime(OUT) > st.st_mtime)
        if prev.get("read_from") == sig or legacy:
            out[name] = dict(prev, read_from=sig)
            log(f"{name}: unchanged since it was last read")
            continue
        log(f"reading {name}")
        out[name] = dict(fn(), read_from=sig)
    write_json(OUT, out)
    log(f"wrote {os.path.relpath(OUT)}")


if __name__ == "__main__":
    main()
