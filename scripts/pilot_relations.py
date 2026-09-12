#!/usr/bin/env python3
"""Pilot: known relations offered to a network as node functions, on dissolved oxygen.

The idea (relations/README.md in statistical-methods): a network of ReLUs builds a
known relation out of many kinks; a node that computes it does it in one. So the
relations of `relations/library.py` (forms with learnable constants, fed learned
combinations of the inputs) and `relations/laws.py` (TEOS-10 laws with measured
constants, wired to the record's own salinity, temperature, depth and position) are
offered in the first layer beside ordinary units. Every first-layer node carries a
learnable scalar gate with an L1 penalty, so a relation that fits costs one gate
where units imitating it cost several. Afterwards the gates are read.

Target: dissolved oxygen (mg/l) per CTD measurement from the ODA extract. Compared
on whole stations held out: the water body's mean (and water body by month), a plain
MLP, and the same MLP with relation and law nodes in its first layer.

    python scripts/pilot_relations.py parse            stream ctd.csv.gz -> sample .npz
    python scripts/pilot_relations.py train --kind both --seeds 0 1 2
    python scripts/pilot_relations.py report           baselines + assemble the JSON
    python scripts/pilot_relations.py train --split time --kind both --seeds 0 1 2 3 4
    python scripts/pilot_relations.py extrap-report    extrapolation splits -> own JSON

The extrapolation splits (SPLITS) keep the station partition and add a condition -
later years, the warmest measurements, marine or brackish water - so the test rows
lie outside what was trained on; see the section above extrap_report().

Run under scripts/runbig -m 3G -- ~/.venvs/relations/bin/python ... (torch, gsw).

Peak memory. parse: the reservoir (CAP measurements x 40 bytes) plus one set entry
per (station, date) cast seen, to count casts that reopen, plus one cast's rows.
train/report: the reservoir sample as float32 arrays plus torch (a few hundred MB).

Reads   data/raw/oda/ctd.csv.gz, data/raw/oda/stations.csv
Writes  data/derived/pilot_relations_sample.npz, pilot_relations_parse.json,
        pilot_relations_runs/*.json, pilot_relations.json,
        pilot_relations_extrap_runs/*.json, pilot_relations_extrap.json
"""
import argparse
import collections
import json
import os
import random
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from formats import num  # noqa: E402  the declared ODA number format

ROOT = os.path.dirname(HERE)
RELATIONS_DIR = os.environ.get(
    "RELATIONS_DIR", os.path.join(os.path.dirname(ROOT), "statistical-methods", "relations"))
CTD = os.path.join(ROOT, "data", "raw", "oda", "ctd.csv.gz")
STATIONS = os.path.join(ROOT, "data", "raw", "oda", "stations.csv")
DERIVED = os.path.join(ROOT, "data", "derived")
SAMPLE = os.path.join(DERIVED, "pilot_relations_sample.npz")
PARSE_JSON = os.path.join(DERIVED, "pilot_relations_parse.json")
RUNS = os.path.join(DERIVED, "pilot_relations_runs")
OUT = os.path.join(DERIVED, "pilot_relations.json")


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def uq(v):
    v = v.strip()
    return v[1:-1] if len(v) > 1 and v[0] == '"' and v[-1] == '"' else v


# ---------------------------------------------------------------- constructions

PARAMS = {"Oxygen indhold": ("o2", "mg/l"), "Temperatur": ("t", "grader C"),
          "Salinitet": ("s", "promille")}
SLOT = {"o2": 0, "t": 1, "s": 2}
QA_OK, KV_OK, ATTR_OK = "C, Faglig kontrol", "Godkendt", "="
FACTOR_RANGE = (0.5, 2.0)            # scripts/surface_temp.py, scripts/depth_clock.py
RANGES = {"t": (-2.0, 30.0), "s": (0.0, 40.0),   # scripts/surface_temp.py
          "o2": (0.0, 25.0)}                     # scripts/depth_clock.py
LON, LAT = (3.0, 16.0), (53.0, 59.0)             # scripts/stations_series.py

# flag bits carried by every complete measurement; which are APPLIED is decided in
# prepare() and recorded with the number each one removes
FLAGS = [
    ("date_invalid", "Dato is not a valid YYYYMMDD calendar date"),
    ("qa_not_C", "a row of the measurement has QANiveau other than 'C, Faglig kontrol' "
                 "(the other value seen is 'B, Elektronisk kontrol')"),
    ("kvalitet_not_godkendt", "a row has Kvalitet other than 'Godkendt' "
                              "(the other value seen is 'Fagligt forbehold')"),
    ("attribut_not_equals", "a row has ResultatAttribut '<' or '>': a censored value, "
                            "not a measurement"),
    ("factor_outside", f"a row has KorrektionsFaktor outside {FACTOR_RANGE[0]}-"
                       f"{FACTOR_RANGE[1]} (the project's bound, surface_temp.py)"),
    ("conflicting_duplicate", "two rows for the same parameter at the same station, "
                              "date and depth carry different corrected values"),
    ("t_out_of_range", f"temperature outside {RANGES['t']} C"),
    ("s_out_of_range", f"salinity outside {RANGES['s']} promille"),
    ("o2_out_of_range", f"oxygen outside {RANGES['o2']} mg/l"),
    ("depth_negative", "Dybde (m) below zero"),
    ("position_outside", f"no position, or Længde/Bredde outside lon {LON} lat {LAT}"),
    ("no_water_body", "the CTD rows carry no Lokalitetsnavn (water body name)"),
    ("sonde_999", "SondeNr 999 ('Ukendt', unknown sonde) on the oxygen row"),
    ("water_body_not_in_register", "the Lokalitetsnavn is not among the Vandomraade names "
                                   "of data/raw/oda/stations.csv"),
]
BIT = {k: 1 << i for i, (k, _) in enumerate(FLAGS)}

APPLIED = ["date_invalid", "qa_not_C", "kvalitet_not_godkendt", "attribut_not_equals",
           "factor_outside", "conflicting_duplicate", "t_out_of_range", "s_out_of_range",
           "o2_out_of_range", "depth_negative", "position_outside", "no_water_body"]
NOT_APPLIED = {
    "sonde_999": "Not applied. 999 means the sonde is not recorded, not that the value "
                 "is bad; the rows carrying it include the bottle-sampler ('Ketcher') "
                 "history, so dropping them selects by era rather than by quality. "
                 "Counted so the effect is visible.",
    "water_body_not_in_register": "Not applied. The name is the extract's own water-body "
                                  "label for the station and serves as the group; it is "
                                  "counted so a reader sees how much rests on names the "
                                  "register does not confirm.",
}

CAP = 400_000
SPLIT_SEED = 0
SPLIT = (0.7, 0.1, 0.2)          # train / validation / test, by share of STATIONS
INPUTS = ["temperature", "salinity", "depth", "lat", "lon", "day_of_year", "year"]
LAW_NODES = [("p", "pressure"), ("SA", "absolute_salinity"),
             ("CT", "conservative_temperature"), ("rho", "density"),
             ("sigma0", "sigma0"), ("O2sol", "oxygen_solubility")]
CFG = {"first_layer_nodes": 64, "hidden2": 32, "lambda_gate_l1": 1e-3,
       "mu_next_layer_l2": 5e-4,
       "_penalties": "loss = MSE(standardised) + lambda * sum|gate| over ALL first-layer "
                     "nodes (ordinary units too) + mu * ||W2||^2 on the weights leaving the "
                     "first layer. Node outputs are batch-normalised (no affine) before the "
                     "gate, so a gate is the node's scale; the L2 on W2 stops the network "
                     "from shrinking a gate and growing its outgoing weight instead "
                     "(network slimming, Liu et al. 2017).",
       "weight_decay": 1e-4, "lr": 3e-3, "batch": 4096, "max_epochs": 80,
       "_max_epochs_note": "raised from 40 after a first round in which one plain run "
                           "(seed 2) reached the cap with its best epoch at 37; all runs "
                           "were then repeated at 80 so no network is cut off before early "
                           "stopping",
       "patience": 6, "grad_clip_norm": 5.0, "gate_init": 1.0,
       "form_param_init": "1.0 + 0.1 * N(0,1) for every form constant",
       "active_gate_threshold": 0.05}


# ---------------------------------------------------------------------- parse

def load_waterbodies():
    """station -> (VandomraadeNr, Vandomraade); counts stations with several."""
    wb, names, multi, rows, bad = {}, {}, set(), 0, 0
    with open(STATIONS, encoding="iso-8859-1") as fh:
        hdr = fh.readline().rstrip("\r\n").split(";")
        ix = {c: i for i, c in enumerate(hdr)}
        for line in fh:
            rows += 1
            f = line.rstrip("\r\n").split(";")
            if len(f) != len(hdr):
                bad += 1
                continue
            s, w = uq(f[ix["ObservationsstedNr"]]), uq(f[ix["VandomraadeNr"]])
            if not w:
                continue
            if s in wb and wb[s] != w:
                multi.add(s)
            wb.setdefault(s, w)
            names[w] = uq(f[ix["Vandomraade"]])
    return wb, names, {"rows": rows, "bad_rows": bad, "stations": len(wb),
                       "water_bodies": len(names),
                       "stations_with_several_water_bodies": len(multi)}


def parse(args):
    import datetime as dt
    t0 = time.time()
    wbmap, wbnames, wbinfo = load_waterbodies()
    log(f"stations register: {wbinfo}")
    # The CTD extract and the register are largely different station universes
    # (scripts/cube.py: 35 stations in both), so the station NUMBER join finds almost
    # nothing. Each CTD row carries its own water-body name, Lokalitetsnavn; that is
    # the group used here, checked against the register's Vandomraade names.
    regnames = set(wbnames.values())
    number_by_name = {v: k for k, v in wbnames.items()}
    station_lok = {}
    cur_lok = ""
    cap = args.cap
    rng = random.Random(args.seed)
    R = {"station": np.zeros(cap, np.int32), "date": np.zeros(cap, np.int32),
         "depth": np.zeros(cap, np.float32), "t": np.zeros(cap, np.float32),
         "s": np.zeros(cap, np.float32), "o2": np.zeros(cap, np.float32),
         "o2_orig": np.zeros(cap, np.float32), "lon": np.zeros(cap, np.float32),
         "lat": np.zeros(cap, np.float32), "mask": np.zeros(cap, np.uint16),
         "wb": np.full(cap, -1, np.int32)}
    st_index, wb_index = {}, {}
    C = collections.Counter()
    masks = collections.Counter()          # flag mask -> complete measurements
    incomplete = collections.Counter()     # which of o2,t,s present -> measurements
    units = collections.Counter()
    differ = collections.Counter()
    seen = 0
    closed = set()
    cur, cast, cast_ok = None, {}, True

    def flush():
        nonlocal seen
        for dk, m in cast.items():
            present = (m[0] is not None) | (m[1] is not None) << 1 | (m[2] is not None) << 2
            if present != 7:
                incomplete[present] += 1
                continue
            o2, t, s = m[0], m[1], m[2]
            fl = m[3] | (0 if cast_ok else BIT["date_invalid"])
            if not RANGES["t"][0] <= t <= RANGES["t"][1]: fl |= BIT["t_out_of_range"]
            if not RANGES["s"][0] <= s <= RANGES["s"][1]: fl |= BIT["s_out_of_range"]
            if not RANGES["o2"][0] <= o2 <= RANGES["o2"][1]: fl |= BIT["o2_out_of_range"]
            if m[7] < 0: fl |= BIT["depth_negative"]
            lo, la = m[4], m[5]
            if lo is None or la is None or not (LON[0] < lo < LON[1] and LAT[0] < la < LAT[1]):
                fl |= BIT["position_outside"]
            w = cur_lok or None
            if w is None: fl |= BIT["no_water_body"]
            elif w not in regnames: fl |= BIT["water_body_not_in_register"]
            masks[fl] += 1
            seen += 1
            if seen <= cap:
                i = seen - 1
            else:
                i = rng.randrange(seen)
                if i >= cap:
                    continue
            R["station"][i] = st_index.setdefault(cur[0], len(st_index))
            R["date"][i] = int(cur[1]) if cast_ok else 0
            R["depth"][i] = m[7]
            R["t"][i], R["s"][i], R["o2"][i] = t, s, o2
            R["o2_orig"][i] = np.nan if m[6] is None else m[6]
            R["lon"][i] = np.nan if lo is None else lo
            R["lat"][i] = np.nan if la is None else la
            R["mask"][i] = fl
            R["wb"][i] = -1 if w is None else wb_index.setdefault(w, len(wb_index))
        cast.clear()

    A, B, Cc = b'"Oxygen indhold"', b'"Temperatur"', b'"Salinitet"'
    proc = subprocess.Popen(["zcat", CTD], stdout=subprocess.PIPE, bufsize=1 << 20)
    fh = proc.stdout
    hdr = fh.readline().decode("iso-8859-1").rstrip("\r\n").split(";")
    ix = {c: i for i, c in enumerate(hdr)}
    nc = len(hdr)
    iPar, iEnh, iSt, iDat, iDep = (ix[k] for k in ("Parameter", "Enhed", "ObservationsStedNr",
                                                   "Dato", "Dybde (m)"))
    iKor, iOrg, iFac = ix["KorrigeretResultat"], ix["OriginalResultat"], ix["KorrektionsFaktor"]
    iQA, iKv, iAt, iSo = ix["QANiveau"], ix["Kvalitet"], ix["ResultatAttribut"], ix["SondeNr"]
    iLon, iLat, iLok = ix["Længde"], ix["Bredde"], ix["Lokalitetsnavn"]
    rows = 0
    for raw in fh:
        rows += 1
        if rows % 5_000_000 == 0:
            log(f"  {rows:,} rows, {seen:,} complete measurements, {time.time()-t0:.0f}s")
        if args.max_rows and rows > args.max_rows:
            break
        if not (A in raw or B in raw or Cc in raw):
            continue
        f = raw.decode("iso-8859-1").rstrip("\r\n").split(";")
        if len(f) != nc:
            C["prefiltered_rows_wrong_column_count"] += 1
            continue
        p = PARAMS.get(uq(f[iPar]))
        if p is None:
            C["prefilter_hits_other_parameter"] += 1
            continue
        key, unit = p
        C[f"rows_{key}"] += 1
        u = uq(f[iEnh])
        if u != unit:
            units[f"{key}|{u}"] += 1
            continue
        st, dat = uq(f[iSt]), uq(f[iDat])
        if cur is None or (st, dat) != cur:
            flush()
            if (st, dat) in closed:
                C["casts_reopened"] += 1
            closed.add((st, dat))
            cur = (st, dat)
            cur_lok = uq(f[iLok])
            if station_lok.setdefault(st, cur_lok) != cur_lok:
                C["casts_whose_station_changed_Lokalitetsnavn"] += 1
        elif uq(f[iLok]) != cur_lok:
            C["rows_Lokalitetsnavn_differs_within_cast"] += 1
            try:
                dt.date(int(dat[:4]), int(dat[4:6]), int(dat[6:8]))
                cast_ok = len(dat) == 8
            except ValueError:
                cast_ok = False
        d = num(f[iDep])
        if d is None:
            C[f"rows_{key}_no_depth"] += 1
            continue
        corr, orig, fac = num(f[iKor]), num(f[iOrg]), num(f[iFac])
        if orig is not None and corr is not None and orig != corr:
            differ[key] += 1
        if fac is not None and fac != 1.0:
            C[f"rows_{key}_factor_not_1"] += 1
        if corr is None:
            C[f"rows_{key}_no_corrected_value"] += 1
            if orig is not None:
                C[f"rows_{key}_no_corrected_but_original"] += 1
            continue
        fl = 0
        if uq(f[iQA]) != QA_OK: fl |= BIT["qa_not_C"]
        if uq(f[iKv]) != KV_OK: fl |= BIT["kvalitet_not_godkendt"]
        if uq(f[iAt]) != ATTR_OK: fl |= BIT["attribut_not_equals"]
        if fac is not None and not FACTOR_RANGE[0] <= fac <= FACTOR_RANGE[1]:
            fl |= BIT["factor_outside"]
        dk = round(d, 3)
        m = cast.get(dk)
        if m is None:
            m = cast[dk] = [None, None, None, 0, None, None, None, d]
        sl = SLOT[key]
        if m[sl] is not None:
            C[f"duplicate_rows_{key}"] += 1
            if m[sl] != corr:
                fl |= BIT["conflicting_duplicate"]
        else:
            m[sl] = corr
            if key == "o2":
                m[4], m[5], m[6] = num(f[iLon]), num(f[iLat]), orig
        if key == "o2" and uq(f[iSo]) == "999":
            fl |= BIT["sonde_999"]
        m[3] |= fl
    flush()
    proc.stdout.close()
    rc = proc.wait()
    complete_read = not args.max_rows or rows <= args.max_rows
    n = min(seen, cap)
    log(f"{rows:,} rows, {seen:,} complete measurements, {n:,} kept, zcat exit {rc}, "
        f"{time.time()-t0:.0f}s")
    stations = sorted(st_index, key=st_index.get)
    wbs = sorted(wb_index, key=wb_index.get)
    os.makedirs(DERIVED, exist_ok=True)
    np.savez(SAMPLE, **{k: v[:n] for k, v in R.items()},
             station_ids=np.array(stations), wb_names=np.array(wbs),
             wb_ids=np.array([number_by_name.get(w, "") for w in wbs]))
    summary = {
        "rows_read": rows, "whole_file_read": complete_read, "zcat_exit": rc,
        "max_rows": args.max_rows, "reservoir_seed": args.seed, "cap": cap,
        "complete_measurements": seen, "kept_in_sample": n,
        "counts": dict(C), "units_skipped": dict(units),
        "rows_corrected_differs_from_original": dict(differ),
        "incomplete_measurements_by_present": {
            "+".join(k for k, b in (("o2", 1), ("t", 2), ("s", 4)) if pr & b) or "none": c
            for pr, c in incomplete.items()},
        "population_flag_masks": {str(k): v for k, v in masks.items()},
        "casts": len(closed), "stations_register": wbinfo,
        "station_join": {
            "ctd_stations_with_o2_t_or_s_rows": len(station_lok),
            "of_which_number_in_stations_csv": sum(1 for s in station_lok if s in wbmap),
            "of_which_Lokalitetsnavn_in_stations_csv_names":
                sum(1 for v in station_lok.values() if v in regnames),
            "distinct_Lokalitetsnavn": len(set(station_lok.values())),
            "distinct_Lokalitetsnavn_in_register": len(set(station_lok.values()) & regnames)},
        "seconds": round(time.time() - t0, 1),
    }
    with open(PARSE_JSON, "w") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    log(f"wrote {SAMPLE} and {PARSE_JSON}")
    return 0


# -------------------------------------------------------------------- prepare

def seq_removal(mask_counts):
    """Apply APPLIED in order to {mask: count}; how many each removes, and how many
    NOT_APPLIED would remove from what is left."""
    left = dict(mask_counts)
    out = {}
    for k in APPLIED:
        b = BIT[k]
        out[k] = {"flagged": int(sum(c for m, c in mask_counts.items() if m & b)),
                  "removed_in_order": int(sum(c for m, c in left.items() if m & b))}
        left = {m: c for m, c in left.items() if not m & b}
    rest = {k: int(sum(c for m, c in left.items() if m & BIT[k])) for k in NOT_APPLIED}
    return out, int(sum(left.values())), rest


def prepare():
    """The filtered sample, dates, law nodes, station split and standardisation.
    Deterministic; every step is recorded in the returned `constructions`."""
    sys.path.insert(0, RELATIONS_DIR)
    import laws
    Z = np.load(SAMPLE)
    D = {k: Z[k] for k in Z.files}
    with open(PARSE_JSON) as f:
        P = json.load(f)
    mask = D["mask"].astype(np.int64)
    sample_counts = collections.Counter(mask.tolist())
    pop_rm, pop_left, pop_rest = seq_removal({int(k): v for k, v in P["population_flag_masks"].items()})
    smp_rm, smp_left, smp_rest = seq_removal(sample_counts)
    keep = np.ones(len(mask), bool)
    for k in APPLIED:
        keep &= (mask & BIT[k]) == 0
    # a filter concentrated in a few years selects by era as well as by quality
    yr_all = D["date"].astype(np.int64) // 10000
    yr_tot = collections.Counter(yr_all.tolist())
    by_year = {}
    for k in ("qa_not_C", "kvalitet_not_godkendt", "sonde_999"):
        c = collections.Counter(yr_all[(mask & BIT[k]) > 0].tolist())
        by_year[k] = {str(y): round(c[y] / yr_tot[y], 3) for y in sorted(c)
                      if c[y] / yr_tot[y] >= 0.5}
    D = {k: (v[keep] if v.ndim and len(v) == len(mask) else v) for k, v in D.items()}

    date = D["date"].astype(np.int64)
    y, mo, dd = date // 10000, (date // 100) % 100, date % 100
    ystart = (y - 1970).astype("datetime64[Y]").astype("datetime64[D]")
    mstart = ((y - 1970) * 12 + (mo - 1)).astype("datetime64[M]").astype("datetime64[D]")
    doy = ((mstart + (dd - 1).astype("timedelta64[D]")) - ystart).astype(np.int64) + 1

    T, S, dep = D["t"].astype(float), D["s"].astype(float), D["depth"].astype(float)
    lon, lat = D["lon"].astype(float), D["lat"].astype(float)
    with np.errstate(all="ignore"):
        st = laws.record_state(S, T, dep, lon, lat)
    Lraw = np.stack([np.asarray(st[k], float) for k, _ in LAW_NODES], 1)
    finite = np.all(np.isfinite(Lraw), 1)
    in_funnel = np.asarray(st["in_funnel"], bool)
    law_nonfinite = int((~finite).sum())
    sel = finite
    D = {k: (v[sel] if v.ndim and len(v) == len(sel) else v) for k, v in D.items()}
    y, mo, doy, Lraw, in_funnel = y[sel], mo[sel], doy[sel], Lraw[sel], in_funnel[sel]

    X = np.stack([D["t"], D["s"], D["depth"], D["lat"], D["lon"],
                  doy.astype(np.float32), y.astype(np.float32)], 1).astype(np.float64)
    target = D["o2"].astype(np.float64)

    # split by station: whole stations to train, validation or test
    stations = np.unique(D["station"])
    r = np.random.default_rng(SPLIT_SEED)
    perm = r.permutation(stations)
    n1 = int(round(SPLIT[0] * len(perm)))
    n2 = n1 + int(round(SPLIT[1] * len(perm)))
    part = np.zeros(D["station"].max() + 1, np.int8)
    part[perm[n1:n2]] = 1
    part[perm[n2:]] = 2
    which = part[D["station"]]
    tr, va, te = which == 0, which == 1, which == 2

    mu, sd = X[tr].mean(0), X[tr].std(0)
    lmu, lsd = Lraw[tr].mean(0), Lraw[tr].std(0)
    ymu, ysd = target[tr].mean(), target[tr].std()
    cons = {
        "target": {"choice": "KorrigeretResultat of 'Oxygen indhold' (Enhed 'mg/l'); no "
                             "fallback to OriginalResultat when it is empty",
                   "rows_corrected_differs_from_original": P["rows_corrected_differs_from_original"],
                   "oxygen_rows_without_corrected_value": P["counts"].get("rows_o2_no_corrected_value", 0),
                   "sample_measurements_corrected_differs_from_original":
                       int(np.sum(np.isfinite(D["o2_orig"]) & (D["o2_orig"] != D["o2"])))},
        "temperature_salinity": "KorrigeretResultat of 'Temperatur' (Enhed 'grader C') and "
                                "'Salinitet' (Enhed 'promille' only; other units skipped)",
        "measurement": "rows sharing (ObservationsStedNr, Dato, Dybde (m) rounded to 1 mm) "
                       "joined; complete = all three parameters present. Casts (station, "
                       "date) are grouped as contiguous runs and a cast that reopens is "
                       "counted (casts_reopened in parse.counts).",
        "prefilter": "lines are kept for splitting only if they contain '\"Oxygen "
                     "indhold\"', '\"Temperatur\"' or '\"Salinitet\"' - relies on every "
                     "field being quoted (formats.py); rows with the wrong column count "
                     "are counted and skipped, as formats.py requires",
        "sample": f"reservoir sample (Algorithm R, seed {P['reservoir_seed']}) of at most "
                  f"{P['cap']:,} complete measurements, drawn BEFORE the filters so each "
                  "filter's effect is also counted on the whole population",
        "filters_applied_in_order": [{"flag": k, "meaning": dict(FLAGS)[k],
                                      "population": pop_rm[k], "sample": smp_rm[k]}
                                     for k in APPLIED],
        "filters_not_applied": [{"flag": k, "reason": v,
                                 "population_would_remove": pop_rest[k],
                                 "sample_would_remove": smp_rest[k]}
                                for k, v in NOT_APPLIED.items()],
        "years_where_a_flag_covers_half_or_more_of_the_sample": {
            "_what": "share of the year's sampled complete measurements carrying the flag, "
                     "listed only where it is 0.5 or more. qa_not_C is applied, so those "
                     "years are largely absent from the data the models see.",
            **by_year},
        "population_after_filters": pop_left, "sample_after_filters": smp_left,
        "law_outputs_not_finite_removed_from_sample": law_nonfinite,
        "sample_used": int(len(target)),
        "position": "Længde/Bredde of the oxygen row (the station's position in the extract)",
        "water_body": {
            "choice": "the CTD row's own Lokalitetsnavn (one per station), checked against "
                      "the Vandomraade names of data/raw/oda/stations.csv",
            "deviation_from_brief": "the brief named a join of ObservationsStedNr into "
                                    "stations.csv (ObservationsstedNr -> VandomraadeNr). That "
                                    "join finds few CTD stations - the two files are largely "
                                    "different station universes (scripts/cube.py documents "
                                    "35 in both) - so it would have discarded most of the "
                                    "data. Counts in parse.station_join.",
            "station_join": P.get("station_join")},
        "split": {"by": "station (whole stations held out)", "seed": SPLIT_SEED,
                  "shares_of_stations": dict(zip(("train", "validation", "test"), SPLIT)),
                  "stations": {"train": int(n1), "validation": int(n2 - n1),
                               "test": int(len(perm) - n2)},
                  "measurements": {"train": int(tr.sum()), "validation": int(va.sum()),
                                   "test": int(te.sum())}},
        "inputs": {"names": INPUTS, "day_of_year": "integer day of year from Dato, as "
                   "given", "year": "calendar year from Dato, as given",
                   "standardisation": "subtract the training-station mean, divide by the "
                                      "training-station standard deviation (inputs, law "
                                      "outputs and the target alike)"},
        "laws": {"call": "laws.record_state(SP=salinity, t=temperature, depth, lon, lat) on "
                         "raw values, float64, then standardised",
                 "nodes": [n for _, n in LAW_NODES],
                 "assumption": "ODA 'promille' salinity read as PSS-78 Practical Salinity",
                 "oxygen_solubility_unit": "umol/kg, left unconverted: the next layer's "
                                           "weight absorbs the scale",
                 "share_in_teos10_funnel": round(float(in_funnel.mean()), 4)},
        "model_config": CFG,
    }
    return {"X": ((X - mu) / sd).astype(np.float32), "L": ((Lraw - lmu) / lsd).astype(np.float32),
            "y": ((target - ymu) / ysd).astype(np.float32), "target": target,
            "ymu": ymu, "ysd": ysd, "tr": tr, "va": va, "te": te, "wb": D["wb"],
            "month": mo, "station": D["station"], "wb_names": D["wb_names"],
            "constructions": cons,
            # raw arrays and the station partition (0 train, 1 validation, 2 test), so
            # apply_split() can cut by condition and re-standardise on its own rows
            "Xraw": X, "Lraw": Lraw, "year": y, "which": which}


# --------------------------------------------------------------------- models

def metrics(y, p):
    sse = float(np.sum((y - p) ** 2))
    sst = float(np.sum((y - y.mean()) ** 2))
    return {"r2": round(1 - sse / sst, 4), "rmse_mg_l": round(float(np.sqrt(sse / len(y))), 4),
            "n": int(len(y))}


def make_net(kind, n_in, n_laws):
    import torch
    from torch import nn
    sys.path.insert(0, RELATIONS_DIR)
    from library import RELATIONS
    xp = torch      # library.py runs under torch directly since statistical-methods 5a48c5f
    forms = list(RELATIONS.values()) if kind == "relation" else []
    n_law = n_laws if kind == "relation" else 0
    n_relu = CFG["first_layer_nodes"] - len(forms) - n_law

    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.forms = forms
            self.relu = nn.Linear(n_in, n_relu)
            self.form_in = nn.ModuleList([nn.Linear(n_in, r.arity) for r in forms])
            self.form_par = nn.ParameterList(
                [nn.Parameter(1.0 + 0.1 * torch.randn(len(r.params))) for r in forms])
            n = n_relu + len(forms) + n_law
            self.norm = nn.BatchNorm1d(n, affine=False)
            self.gate = nn.Parameter(torch.full((n,), CFG["gate_init"]))
            self.l2 = nn.Linear(n, CFG["hidden2"])
            self.out = nn.Linear(CFG["hidden2"], 1)
            self.names = ([f"unit_{i:02d}" for i in range(n_relu)]
                          + [f"form:{r.key}" for r in forms]
                          + [f"law:{nm}" for _, nm in LAW_NODES][:n_law])

        def first(self, x, law):
            parts = [torch.relu(self.relu(x))]
            for r, lin, p in zip(self.forms, self.form_in, self.form_par):
                z = lin(x)
                out = r.fn(*[z[:, i] for i in range(r.arity)],
                           *[p[i] for i in range(len(r.params))], xp=xp)
                parts.append(out.unsqueeze(1))
            if n_law:
                parts.append(law)
            return torch.cat(parts, 1)

        def forward(self, x, law, gate_mask=None):
            g = self.gate if gate_mask is None else self.gate * gate_mask
            h = self.norm(self.first(x, law)) * g
            return self.out(torch.relu(self.l2(h))).squeeze(1)

    return Net()


def train(args):
    import torch
    # one thread: the matrices are small, and on a shared, oversubscribed CPU several
    # torch threads spin against each other (a smoke run stalled past ten minutes)
    torch.set_num_threads(int(os.environ.get("PILOT_THREADS", "1")))
    P = prepare()
    outdir, prefix = RUNS, ""
    if args.split:
        P = apply_split(P, args.split)
        outdir, prefix = EXTRAP_RUNS, args.split + "__"
        log(f"split {args.split}: {P['split_info']['measurements']}")
    os.makedirs(outdir, exist_ok=True)
    X = torch.from_numpy(P["X"]); L = torch.from_numpy(P["L"]); Y = torch.from_numpy(P["y"])
    idx = {k: torch.from_numpy(np.nonzero(P[k])[0]) for k in ("tr", "va", "te")}
    kinds = ["plain", "relation"] if args.kind == "both" else [args.kind]
    lam = args.lam if args.lam is not None else CFG["lambda_gate_l1"]
    for seed in args.seeds:
        for kind in kinds:
            t0 = time.time()
            torch.manual_seed(seed)
            net = make_net(kind, X.shape[1], L.shape[1])
            special = {"gate"} | {n for n, _ in net.named_parameters() if n.startswith("form_par")}
            opt = torch.optim.AdamW(
                [{"params": [p for n, p in net.named_parameters() if n not in special],
                  "weight_decay": CFG["weight_decay"]},
                 {"params": [p for n, p in net.named_parameters() if n in special],
                  "weight_decay": 0.0}], lr=CFG["lr"])
            gen = torch.Generator().manual_seed(seed)

            def predict(ii, gate_mask=None):
                net.eval()
                out = []
                with torch.no_grad():
                    for s in range(0, len(ii), 65536):
                        b = ii[s:s + 65536]
                        out.append(net(X[b], L[b], gate_mask))
                return torch.cat(out).numpy().astype(np.float64)

            best, best_state, best_ep, bad, nonfinite, hist = np.inf, None, -1, 0, False, []
            tri = idx["tr"]
            for ep in range(CFG["max_epochs"]):
                net.train()
                perm = tri[torch.randperm(len(tri), generator=gen)]
                tot = 0.0
                for s in range(0, len(perm), CFG["batch"]):
                    b = perm[s:s + CFG["batch"]]
                    if len(b) < 2:
                        continue
                    pred = net(X[b], L[b])
                    mse = torch.mean((pred - Y[b]) ** 2)
                    loss = (mse + lam * net.gate.abs().sum()
                            + CFG["mu_next_layer_l2"] * (net.l2.weight ** 2).sum())
                    if not torch.isfinite(loss):
                        nonfinite = True
                        break
                    opt.zero_grad()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(net.parameters(), CFG["grad_clip_norm"])
                    opt.step()
                    tot += float(mse.detach()) * len(b)
                if nonfinite:
                    log(f"  {kind} seed {seed}: NON-FINITE loss at epoch {ep}")
                    break
                pv = predict(idx["va"])
                vm = float(np.mean((pv - P["y"][P["va"]]) ** 2))
                hist.append((round(tot / len(tri), 5), round(vm, 5)))
                log(f"    {kind} seed {seed} epoch {ep}: train mse {tot/len(tri):.4f} "
                    f"val mse {vm:.4f} |gate| mean {float(net.gate.abs().mean()):.3f} "
                    f"{time.time()-t0:.0f}s")
                if vm < best - 1e-5:
                    best, best_ep, bad = vm, ep, 0
                    best_state = {k: v.detach().clone() for k, v in net.state_dict().items()}
                else:
                    bad += 1
                    if bad >= CFG["patience"]:
                        break
            if best_state is not None:
                net.load_state_dict(best_state)
            ysd, ymu = P["ysd"], P["ymu"]
            res = {"kind": kind, "seed": seed, "lambda_gate_l1": lam,
                   "epochs_run": len(hist), "best_epoch": best_ep, "nonfinite_loss": nonfinite,
                   "history_train_mse_val_mse_standardised": hist,
                   "n_params": int(sum(p.numel() for p in net.parameters()))}
            for part in ("va", "te"):
                pr = predict(idx[part]) * ysd + ymu
                res[{"va": "validation", "te": "test"}[part]] = metrics(P["target"][P[part]], pr)
            g = net.gate.detach().numpy().astype(float)
            w2 = net.l2.weight.detach().norm(dim=0).numpy().astype(float)
            res["nodes"] = [{"node": n, "gate": round(float(gi), 5),
                             "gate_abs": round(abs(float(gi)), 5),
                             "effective": round(abs(float(gi)) * float(wi), 5)}
                            for n, gi, wi in zip(net.names, g, w2)]
            isunit = np.array([n.startswith("unit_") for n in net.names])
            res["units_active"] = int(np.sum(np.abs(g[isunit]) > CFG["active_gate_threshold"]))
            res["units_total"] = int(isunit.sum())
            res["sum_abs_gate_units"] = round(float(np.abs(g[isunit]).sum()), 4)
            res["sum_abs_gate_relations"] = round(float(np.abs(g[~isunit]).sum()), 4)
            if kind == "relation":
                abl = {}
                for label, m in (("relations_and_laws_off", isunit), ("units_off", ~isunit)):
                    pr = predict(idx["te"], torch.from_numpy(m.astype(np.float32))) * ysd + ymu
                    abl[label] = metrics(P["target"][P["te"]], pr)
                res["test_ablation_without_retraining"] = abl
                res["forms"] = []
                for r, lin, p in zip(net.forms, net.form_in, net.form_par):
                    W = lin.weight.detach().numpy()
                    res["forms"].append({
                        "form": r.key, "params": dict(zip(r.params, [round(float(v), 4) for v in p.detach()])),
                        "input_weights": [dict(zip(INPUTS, [round(float(v), 4) for v in row])) for row in W],
                        "input_bias": [round(float(v), 4) for v in lin.bias.detach()]})
            res["seconds"] = round(time.time() - t0, 1)
            if args.split:
                res["split"] = args.split
            name = prefix + f"{kind}_seed{seed}" + ("" if lam == CFG["lambda_gate_l1"] else f"_lam{lam:g}")
            with open(os.path.join(outdir, name + ".json"), "w") as f:
                json.dump(res, f, indent=1)
            log(f"  {name}: test R2 {res['test']['r2']} RMSE {res['test']['rmse_mg_l']} "
                f"val R2 {res['validation']['r2']} epochs {len(hist)} best {best_ep} "
                f"{res['seconds']}s")
    return 0


# --------------------------------------------------------------------- report

def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def aggregate_baselines(P):
    """The water body's mean and the water body by month, taken from the training rows
    and predicted on the test rows, with every fallback counted."""
    target, tr, te = P["target"], P["tr"], P["te"]
    wb, month = P["wb"], P["month"]
    gmean = target[tr].mean()
    nwb = int(wb.max()) + 1
    s = np.bincount(wb[tr], target[tr], nwb); c = np.bincount(wb[tr], None, nwb)
    wbm = np.where(c > 0, s / np.maximum(c, 1), np.nan)
    p_wb = wbm[wb[te]]
    fb_wb = int(np.isnan(p_wb).sum())
    p_wb = np.where(np.isnan(p_wb), gmean, p_wb)
    key = wb * 12 + (month - 1)
    s2 = np.bincount(key[tr], target[tr], nwb * 12); c2 = np.bincount(key[tr], None, nwb * 12)
    wbmm = np.where(c2 > 0, s2 / np.maximum(c2, 1), np.nan)
    p_wbm = wbmm[key[te]]
    fb_wbm = int(np.isnan(p_wbm).sum())
    p_wbm = np.where(np.isnan(p_wbm), p_wb, p_wbm)
    return {
        "water_body_mean": {**metrics(target[te], p_wb),
                            "test_measurements_whose_water_body_has_no_training_station":
                                fb_wb, "fallback": "training mean over all stations"},
        "water_body_by_month_mean": {**metrics(target[te], p_wbm),
                                     "test_measurements_without_training_cell": fb_wbm,
                                     "fallback": "the water body's mean, then the overall "
                                                 "training mean"},
        "training_mean_everywhere": metrics(target[te], np.full(te.sum(), gmean)),
    }, key


def network_summary(runs, lam):
    """Held-out R^2 and RMSE per network kind over its seeds, at gate penalty lam."""
    summary = {}
    for kind in ("plain", "relation"):
        rs = [r for r in runs if r["kind"] == kind and r["lambda_gate_l1"] == lam]
        if not rs:
            continue
        r2 = np.array([r["test"]["r2"] for r in rs]); rm = np.array([r["test"]["rmse_mg_l"] for r in rs])
        summary[kind] = {"seeds": [r["seed"] for r in rs],
                         "test_r2_per_seed": r2.tolist(), "test_rmse_per_seed": rm.tolist(),
                         "test_r2_mean": round(float(r2.mean()), 4),
                         "test_r2_sd": round(float(r2.std(ddof=1)), 4) if len(rs) > 1 else None,
                         "test_rmse_mean": round(float(rm.mean()), 4),
                         "test_rmse_sd": round(float(rm.std(ddof=1)), 4) if len(rs) > 1 else None,
                         "units_active_per_seed": [r["units_active"] for r in rs],
                         "n_params": rs[0]["n_params"],
                         "nonfinite_runs": [r["seed"] for r in rs if r["nonfinite_loss"]]}
    return summary


def gate_summary(rel):
    """Every relation and law gate of the relation runs `rel`, ranked, with its
    stability across their seeds."""
    names = [n["node"] for n in rel[0]["nodes"] if not n["node"].startswith("unit_")]
    G = np.array([[next(x["gate_abs"] for x in r["nodes"] if x["node"] == nm) for nm in names] for r in rel])
    E = np.array([[next(x["effective"] for x in r["nodes"] if x["node"] == nm) for nm in names] for r in rel])
    ranks = np.argsort(np.argsort(-G, 1), 1) + 1
    order = np.argsort(G.mean(0))[::-1]
    pairs = [(i, j) for i in range(len(rel)) for j in range(i + 1, len(rel))]
    top5 = [set(np.argsort(-G[i])[:5]) for i in range(len(rel))]
    return {
        "_what": "|gate| of every relation and law node at the best validation epoch, "
                 "ranked by the mean over seeds; rank 1 = largest. 'effective' is "
                 "|gate| times the norm of the node's outgoing weights (node outputs "
                 "are batch-normalised, so this is its scale of contribution).",
        "seeds": [r["seed"] for r in rel],
        "ranked": [{"node": names[k], "gate_abs_per_seed": [round(float(v), 4) for v in G[:, k]],
                    "gate_abs_mean": round(float(G[:, k].mean()), 4),
                    "rank_per_seed": ranks[:, k].tolist(),
                    "effective_per_seed": [round(float(v), 4) for v in E[:, k]]}
                   for k in order],
        "spearman_between_seeds_gate_abs": {f"{rel[i]['seed']}-{rel[j]['seed']}":
                                            round(spearman(G[i], G[j]), 3) for i, j in pairs},
        "spearman_between_seeds_effective": {f"{rel[i]['seed']}-{rel[j]['seed']}":
                                             round(spearman(E[i], E[j]), 3) for i, j in pairs},
        "top5_common_to_all_seeds": sorted(names[k] for k in set.intersection(*top5)),
        "top5_per_seed": {str(r["seed"]): [names[k] for k in np.argsort(-G[i])[:5]]
                          for i, r in enumerate(rel)},
    }


def report(args):
    P = prepare()
    target, te = P["target"], P["te"]
    wb = P["wb"]
    baselines, key = aggregate_baselines(P)

    def within_share(groups, yv):
        k = np.unique(groups, return_inverse=True)[1]
        m = np.bincount(k, yv) / np.bincount(k)
        return round(float(np.sum((yv - m[k]) ** 2) / np.sum((yv - yv.mean()) ** 2)), 4)

    variance = {
        "_what": "share of oxygen variance lying WITHIN groups (sum of squares about the "
                 "group's own mean over sum of squares about the overall mean); a group "
                 "mean cannot express this part at all",
        "within_water_body_all_stations": within_share(wb, target),
        "within_water_body_by_month_all_stations": within_share(key, target),
        "within_water_body_test_stations": within_share(wb[te], target[te]),
        "within_station_all": within_share(P["station"], target),
        "total_variance_mg2_l2": round(float(target.var()), 4),
        "water_bodies_in_sample": int(len(np.unique(wb))),
    }
    runs = []
    for fn in sorted(os.listdir(RUNS)):
        if fn.endswith(".json"):
            with open(os.path.join(RUNS, fn)) as f:
                r = json.load(f)
            r["file"] = fn
            runs.append(r)
    main_lam = CFG["lambda_gate_l1"]
    summary = network_summary(runs, main_lam)
    rel = [r for r in runs if r["kind"] == "relation" and r["lambda_gate_l1"] == main_lam]
    gates = gate_summary(rel) if rel else None
    sens = [{"file": r["file"], "kind": r["kind"], "seed": r["seed"],
             "lambda_gate_l1": r["lambda_gate_l1"], "test": r["test"],
             "units_active": r["units_active"]}
            for r in runs if r["lambda_gate_l1"] != main_lam]
    with open(PARSE_JSON) as f:
        parse_summary = json.load(f)
    parse_summary.pop("population_flag_masks", None)
    parse_summary["counts"].setdefault("casts_reopened", 0)   # Counter omits zeros
    out = {"_what": "Pilot: relations and laws offered as first-layer nodes to a network "
                    "predicting dissolved oxygen (mg/l) per ODA CTD measurement, against a "
                    "plain network and water-body means, on whole stations held out.",
           "_script": "scripts/pilot_relations.py",
           "_library": {"forms": os.path.join(RELATIONS_DIR, "library.py"),
                        "laws": os.path.join(RELATIONS_DIR, "laws.py"),
                        "torch_note": "The first run (copenhagen-waterways 1ec48a4) was trained "
                                      "through a shim, because library.py's _pos() then "
                                      "called xp.maximum(z, 0), which torch refuses (9 of 17 "
                                      "forms failed). statistical-methods 5a48c5f fixed _pos() "
                                      "with xp.clip; since then the library is imported "
                                      "under torch directly."},
           "constructions": P["constructions"],
           "parse": parse_summary,
           "variance": variance,
           "baselines": baselines,
           "networks": summary,
           "relation_gates": gates,
           "runs": runs,
           "sensitivity_other_lambda": sens}
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    log(f"wrote {OUT}")
    log(json.dumps({"variance": variance, "baselines": baselines, "networks": summary}, indent=1))
    return 0


# -------------------------------------------------------------- extrapolation
#
# Known relations should matter most OUTSIDE the conditions trained on, which a
# station split does not test. Each split below keeps the station partition of the
# first run (whole stations held out) and adds a condition: training and validation
# stations contribute only rows inside the training condition, test stations only
# rows outside it, so early stopping never sees the test condition either.

EXTRAP_RUNS = os.path.join(DERIVED, "pilot_relations_extrap_runs")
EXTRAP_OUT = os.path.join(DERIVED, "pilot_relations_extrap.json")
TIME_TRAIN_LAST, TIME_TEST_FIRST = 2008, 2014
TEMP_QUANTILE = 0.9
SAL_MARINE = 30.0
SPLITS = {
    "in_range": "whole stations held out and no condition: the first run's split, "
                "repeated with the library imported under torch directly, as the "
                "comparison for every gate below",
    "time": f"train on years <= {TIME_TRAIN_LAST}, test on years >= {TIME_TEST_FIRST}; "
            f"the years between are a gap used by neither side",
    "temperature": f"train below the {TEMP_QUANTILE} quantile of temperature, test at "
                   "or above it (the warmest share)",
    "salinity_brackish_to_marine": f"train on salinity < {SAL_MARINE:g}, test on "
                                   f">= {SAL_MARINE:g}",
    "salinity_marine_to_brackish": f"train on salinity >= {SAL_MARINE:g}, test on "
                                   f"< {SAL_MARINE:g}",
}


def split_conditions(P, name):
    """(training condition, test condition, record of the choice) over every row."""
    yr, T, S = P["year"], P["Xraw"][:, 0], P["Xraw"][:, 1]
    info = {"rule": SPLITS[name]}
    if name == "in_range":
        a = b = np.ones(len(yr), bool)
    elif name == "time":
        a, b = yr <= TIME_TRAIN_LAST, yr >= TIME_TEST_FIRST
        info.update(train_years=[int(yr[a].min()), TIME_TRAIN_LAST],
                    test_years=[TIME_TEST_FIRST, int(yr[b].max())],
                    gap_years=[TIME_TRAIN_LAST + 1, TIME_TEST_FIRST - 1],
                    why="cut from the sample's year distribution so both sides are well "
                        "populated; the gap years are also the ones the QA-level filter "
                        "left thin (see pilot_relations.json constructions)")
    elif name == "temperature":
        q = float(np.quantile(T, TEMP_QUANTILE))
        a, b = T < q, T >= q
        info.update(quantile=TEMP_QUANTILE, threshold_C=round(q, 3),
                    threshold_from="every filtered sample measurement, all stations")
    else:
        br, ma = S < SAL_MARINE, S >= SAL_MARINE
        a, b = (br, ma) if name.endswith("to_marine") else (ma, br)
        info.update(boundary_promille=SAL_MARINE,
                    boundary_from="the Venice system (1958): euhaline water from 30; "
                                  "ODA 'promille' read as practical salinity")
    info["share_of_sample_in_training_condition"] = round(float(a.mean()), 4)
    info["share_of_sample_in_test_condition"] = round(float(b.mean()), 4)
    return a, b, info


def apply_split(P, name):
    """P with an extrapolation split's train/validation/test masks, re-standardised on
    its own training rows."""
    a, b, info = split_conditions(P, name)
    w = P["which"]
    tr, va, te = (w == 0) & a, (w == 1) & a, (w == 2) & b
    Xr, Lr, t = P["Xraw"], P["Lraw"], P["target"]
    mu, sd = Xr[tr].mean(0), Xr[tr].std(0)
    lmu, lsd = Lr[tr].mean(0), Lr[tr].std(0)
    ymu, ysd = t[tr].mean(), t[tr].std()
    info["measurements"] = {
        "train": int(tr.sum()), "validation": int(va.sum()), "test": int(te.sum()),
        "unused_test_condition_on_train_or_validation_stations": int(((w != 2) & b & ~a).sum()),
        "unused_training_condition_on_test_stations": int(((w == 2) & a & ~b).sum()),
        "unused_in_neither_condition": int((~a & ~b).sum())}
    info["stations"] = {"train": int(len(np.unique(P["station"][tr]))),
                        "validation": int(len(np.unique(P["station"][va]))),
                        "test": int(len(np.unique(P["station"][te])))}
    Q = dict(P)
    Q.update(X=((Xr - mu) / sd).astype(np.float32), L=((Lr - lmu) / lsd).astype(np.float32),
             y=((t - ymu) / ysd).astype(np.float32), ymu=ymu, ysd=ysd, tr=tr, va=va, te=te,
             split_info=info)
    return Q


def extrap_report(args):
    P0 = prepare()
    lam = CFG["lambda_gate_l1"]
    io2 = [n for _, n in LAW_NODES].index("oxygen_solubility")
    runs = []
    if os.path.isdir(EXTRAP_RUNS):
        for fn in sorted(os.listdir(EXTRAP_RUNS)):
            if fn.endswith(".json"):
                with open(os.path.join(EXTRAP_RUNS, fn)) as f:
                    r = json.load(f)
                r["file"] = fn
                r.pop("history_train_mse_val_mse_standardised", None)
                runs.append(r)
    splits, cons = {}, {}
    for name in SPLITS:
        P = apply_split(P0, name)
        cons[name] = P["split_info"]
        base, _ = aggregate_baselines(P)
        tr, te, t, x = P["tr"], P["te"], P["target"], P["Lraw"][:, io2]
        slope, icpt = np.polyfit(x[tr], t[tr], 1)
        base["law_only_oxygen_solubility_linear"] = {
            **metrics(t[te], icpt + slope * x[te]),
            "intercept_mg_l": round(float(icpt), 4),
            "slope_mg_l_per_umol_kg": round(float(slope), 6)}
        rs = [r for r in runs if r.get("split") == name]
        rel = [r for r in rs if r["kind"] == "relation" and r["lambda_gate_l1"] == lam]
        splits[name] = {
            "baselines": base, "networks": network_summary(rs, lam),
            "relation_gates": gate_summary(rel) if rel else None,
            "relation_ablation_without_retraining_per_seed":
                {str(r["seed"]): r["test_ablation_without_retraining"] for r in rel},
            # the L1 penalty shrinks gates per optimizer step, so a split with fewer
            # training rows (fewer steps per epoch) leaves every gate larger
            "relation_optimizer_steps_to_best_epoch_mean": round(float(np.mean(
                [(r["best_epoch"] + 1) * int(np.ceil(tr.sum() / CFG["batch"])) for r in rel])), 1)
                if rel else None,
            "test_oxygen_mean_mg_l": round(float(t[te].mean()), 4),
            "test_oxygen_variance_mg2_l2": round(float(t[te].var()), 4)}
    # do the wired laws' gates grow outside the training conditions?
    laws_vs = {}
    ref = splits["in_range"]["relation_gates"]
    if ref:
        refd = {x["node"]: x for x in ref["ranked"]}
        ref_level = float(np.mean([x["gate_abs_mean"] for x in ref["ranked"]]))
        for name in SPLITS:
            g = splits[name]["relation_gates"]
            if name == "in_range" or not g:
                continue
            level = float(np.mean([x["gate_abs_mean"] for x in g["ranked"]]))
            laws_vs[name] = {"_level": {
                "_what": "mean |gate| over all 23 relation and law nodes. The L1 penalty "
                         "acts per optimizer step, so the whole gate level differs between "
                         "splits; 'relative_ratio' divides each gate by its split's level "
                         "before comparing, and the rank needs no such correction",
                "split": round(level, 4), "in_range": round(ref_level, 4)}}
            for x in g["ranked"]:
                if not x["node"].startswith("law:"):
                    continue
                r0 = refd[x["node"]]["gate_abs_mean"]
                laws_vs[name][x["node"]] = {
                    "gate_abs_mean": x["gate_abs_mean"], "in_range_gate_abs_mean": r0,
                    "ratio_to_in_range": round(x["gate_abs_mean"] / max(r0, 1e-9), 3),
                    "relative_ratio": round((x["gate_abs_mean"] / level) /
                                            max(r0 / ref_level, 1e-9), 3),
                    "mean_rank": round(float(np.mean(x["rank_per_seed"])), 2),
                    "in_range_mean_rank": round(float(np.mean(refd[x["node"]]["rank_per_seed"])), 2),
                    "gate_abs_per_seed": x["gate_abs_per_seed"]}
    out = {"_what": "Extrapolation test of the relations pilot: the same comparisons as "
                    "pilot_relations.json, on splits that hold out whole stations AND a "
                    "condition (later years, the warmest measurements, marine or brackish "
                    "water), plus a law-only baseline. 'runs' omits per-epoch histories; "
                    "they stay in data/derived/pilot_relations_extrap_runs/.",
           "_script": "scripts/pilot_relations.py (train --split NAME; extrap-report)",
           "_first_run": "data/derived/pilot_relations.json (copenhagen-waterways 1ec48a4)",
           "_library": {"forms": os.path.join(RELATIONS_DIR, "library.py"),
                        "laws": os.path.join(RELATIONS_DIR, "laws.py"),
                        "torch": "imported under torch directly (statistical-methods 5a48c5f); "
                                 "the in_range split is rerun with it so every gate compared "
                                 "here comes from the same code"},
           "constructions": {
               "inherited": "sample, filters, target column, water-body join, inputs, law "
                            "nodes, network, penalties and training settings exactly as in "
                            "pilot_relations.json 'constructions' (re-derived by the same "
                            "prepare())",
               "station_partition": P0["constructions"]["split"],
               "condition_within_partition": "training and validation stations keep only "
                                             "rows in the training condition, test "
                                             "stations only rows in the test condition; "
                                             "standardisation, water-body means and the "
                                             "law-only fit come from the training rows",
               "law_only_baseline": "ordinary least squares of oxygen (mg/l) on O2sol "
                                    "(umol/kg, laws.record_state) over the training rows: "
                                    "the simplest law-only model",
               "seeds": "5 per network kind and split (0-4)",
               "model_config": CFG,
               "splits": cons},
           "splits": splits,
           "law_gates_against_in_range": laws_vs,
           "runs": runs}
    with open(EXTRAP_OUT, "w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    log(f"wrote {EXTRAP_OUT}")
    for name, s in splits.items():
        row = {k: (v["r2"], v["rmse_mg_l"]) for k, v in s["baselines"].items()}
        row.update({k: (v["test_r2_mean"], v["test_r2_sd"], v["test_rmse_mean"])
                    for k, v in s["networks"].items()})
        log(f"{name}: n_test {cons[name]['measurements']['test']} {row}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("parse"); a.add_argument("--cap", type=int, default=CAP)
    a.add_argument("--max-rows", type=int, default=0); a.add_argument("--seed", type=int, default=0)
    b = sub.add_parser("train"); b.add_argument("--kind", default="both",
                                                 choices=["plain", "relation", "both"])
    b.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    b.add_argument("--lam", type=float, default=None)
    b.add_argument("--split", choices=list(SPLITS), default=None,
                   help="an extrapolation split; runs go to pilot_relations_extrap_runs/")
    sub.add_parser("report")
    sub.add_parser("extrap-report")
    args = ap.parse_args()
    return {"parse": parse, "train": train, "report": report,
            "extrap-report": extrap_report}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
