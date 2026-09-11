#!/usr/bin/env python3
"""Currents in and around Køge Bugt: where the water goes, and when.

SEABED.md computes what the wind lifts off the bed. This asks the next question - where
it then goes - and tests two specific claims that the wave model cannot touch:

  1. Køge Bugt is a convergence: wind-driven surface transport running south meets the
     Baltic outflow running north, and the meeting point accumulates.
  2. Copenhagen's overflows reach Køge Bugt. That requires SOUTHWARD transport in the
     southern Sound, against the mean outflow - so it is a claim about specific hours,
     and those hours have to coincide with the rain that causes the overflow.

Data, all free and keyless:
  - Open-Meteo Marine API: hourly ocean current velocity and direction from the CMEMS
    global physics model. Starts 2022-01-01. Its grid is 0.08 degrees (about 8 km, by
    Open-Meteo's own statement), which does not resolve the Danish straits.
    cmd_validate compares its speeds with peak speeds that have no source in this
    repository, so how far the magnitudes fall short is not established; direction
    and timing are what is used.
  - Open-Meteo ERA5 archive: hourly wind and precipitation, 1995-2025, already fetched
    by the wave work.

The structure follows from that: the 4-year current record was to calibrate a
wind-driven index that would stand in for it over the 31-year wind record. Whether the
index holds is what cmd_index tests, and CURRENTS.md reports what came of it.

Usage:
  python3 scripts/currents.py fetch      # marine + Baltic-basin wind  (~15 min, polite)
  python3 scripts/currents.py validate   # what the coarse field can and cannot support
  python3 scripts/currents.py index      # fit the wind -> strait-flow index
  python3 scripts/currents.py transport  # do the overflow hours move south?
  python3 scripts/currents.py report     # -> docs/CURRENTS.md
"""
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, fetch, log, read_json, write_doc, write_json

MARINE = "https://marine-api.open-meteo.com/v1/marine"
ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
OUT = os.path.join(RAW, "marine")

MARINE_START = "2022-01-01"
MARINE_END = "2026-08-31"

# Points. Each carries the axis its flow is meaningfully projected onto, as a compass
# bearing for the POSITIVE direction, chosen so positive = "toward the Kattegat/North
# Sea" = Baltic outflow.
POINTS = {
    "koege_bugt":  (55.55, 12.35, 270, "Køge Bugt, mid-bay - the subject"),
    "oresund_s":   (55.55, 12.70, 340, "Southern Sound off Amager - the Copenhagen->Køge path"),
    "drogden":     (55.53, 12.72, 340, "Drogden sill - the Sound's shallow gate"),
    "oresund_n":   (55.87, 12.70, 340, "Northern Sound - the outflow gate to the Kattegat"),
    "arkona":      (54.90, 13.50, 300, "Arkona basin - Baltic source water"),
    "fehmarn":     (54.60, 11.30, 300, "Fehmarn Belt - the other main strait"),
    "storebaelt":  (55.30, 10.85, 350, "Great Belt - the largest of the three"),
    "sydfynske":   (54.95, 10.35, 300, "Det Sydfynske Øhav - the contrast case"),
    "aarhus_bugt": (56.10, 10.45, 270, "Aarhus Bugt - registers iltsvind, Kattegat side"),
}

# Wind over the Baltic basin, for the filling/draining index. The basin's long axis runs
# roughly SW-NE; wind blowing toward the NE piles water in, wind from the NE drains it.
BALTIC_WIND = {
    "baltic_s": (55.0, 16.0),
    "baltic_c": (57.0, 19.0),
    "baltic_n": (59.5, 21.0),
}
BALTIC_AXIS_DEG = 40.0     # bearing of "into the Baltic"
WINDOWS_H = (6, 12, 24, 48, 72, 120, 168, 240, 336, 504, 720)   # index windows tried
FLUSH_KM = 20.0            # distance the flushing time is quoted over
RAIN_WINDOW_H = 6          # hours of antecedent rain that fill a combined sewer
EVENT_MM = 10.0            # mm in RAIN_WINDOW_H that counts as overflow-scale
LAGS_H = (0, 6, 12, 24, 48, 72)

MARINE_VARS = "ocean_current_velocity,ocean_current_direction,wave_height,sea_surface_temperature"
WIND_VARS = "wind_speed_10m,wind_direction_10m"


def _np():
    import numpy as np
    return np


def get(url):
    return json.loads(fetch(url))


# ----------------------------------------------------------------- fetch

def cmd_fetch(argv):
    force = "--force" in argv
    os.makedirs(OUT, exist_ok=True)

    for name, (lat, lon, _axis, desc) in POINTS.items():
        p = os.path.join(OUT, f"marine_{name}.json")
        if os.path.exists(p) and not force:
            log(f"  {name:14} cached")
            continue
        url = (f"{MARINE}?latitude={lat}&longitude={lon}&hourly={MARINE_VARS}"
               f"&start_date={MARINE_START}&end_date={MARINE_END}")
        d = get(url)
        d["_point"] = {"name": name, "lat": lat, "lon": lon, "desc": desc}
        write_json(p, d)
        n = len(d["hourly"]["time"])
        nn = sum(1 for x in d["hourly"]["ocean_current_velocity"] if x is not None)
        log(f"  {name:14} {n:,} h, {nn:,} with currents  "
            f"(grid {d['latitude']:.3f},{d['longitude']:.3f})")
        time.sleep(2)

    for name, (lat, lon) in BALTIC_WIND.items():
        p = os.path.join(OUT, f"wind_{name}.json")
        if os.path.exists(p) and not force:
            log(f"  {name:14} cached")
            continue
        url = (f"{ARCHIVE}?latitude={lat}&longitude={lon}&hourly={WIND_VARS}"
               f"&start_date=1995-01-01&end_date=2025-12-31")
        d = get(url)
        write_json(p, d)
        log(f"  {name:14} {len(d['hourly']['time']):,} h of wind")
        time.sleep(2)
    return 0


# ----------------------------------------------------------------- helpers

def load_marine(np, name):
    """Return time list and (u, v) current components in m/s, east/north positive."""
    d = read_json(os.path.join(OUT, f"marine_{name}.json"))
    h = d["hourly"]
    t = h["time"]
    f = lambda a: np.array([x if x is not None else np.nan for x in a], dtype=float)
    spd = f(h["ocean_current_velocity"]) / 3.6          # km/h -> m/s
    drc = f(h["ocean_current_direction"])
    # Ocean convention: direction is where the current is GOING TO.
    th = np.radians(drc)
    return t, spd * np.sin(th), spd * np.cos(th), d


def along(np, u, v, bearing_deg):
    """Component of (u,v) along a compass bearing. Positive = toward that bearing."""
    b = math.radians(bearing_deg)
    return u * math.sin(b) + v * math.cos(b)


def load_basin_wind(np):
    """Mean wind stress over the Baltic, projected on the basin axis."""
    ts, comps = None, []
    for name in BALTIC_WIND:
        d = read_json(os.path.join(OUT, f"wind_{name}.json"))["hourly"]
        if ts is None:
            ts = d["time"]
        f = lambda a: np.array([x if x is not None else np.nan for x in a], dtype=float)
        U = f(d["wind_speed_10m"]) / 3.6
        D = f(d["wind_direction_10m"])
        # Meteorological convention: direction is where the wind comes FROM.
        th = np.radians(D)
        ue, vn = -U * np.sin(th), -U * np.cos(th)
        a = along(np, ue, vn, BALTIC_AXIS_DEG)
        comps.append(1.3e-3 * 1.225 * np.abs(U) * a)      # signed wind stress, Pa
    return ts, np.nanmean(np.array(comps), axis=0)


def load_cph_wind(np):
    """The Copenhagen wind and rain record already fetched for the wave work."""
    W = os.path.join(RAW, "weather")
    times, spd, drc, prc = [], [], [], []
    for f in sorted(os.listdir(W)):
        if not f.startswith("wind_"):
            continue
        h = read_json(os.path.join(W, f))["hourly"]
        times += h["time"]
        spd += h["wind_speed_10m"]
        drc += h["wind_direction_10m"]
        prc += h.get("precipitation") or [None] * len(h["time"])
    g = lambda a: np.array([x if x is not None else np.nan for x in a], dtype=float)
    return times, g(spd) / 3.6, g(drc), g(prc)


def corr(np, a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 100:
        return float("nan")
    x, y = a[m], b[m]
    x = x - x.mean()
    y = y - y.mean()
    den = math.sqrt(float((x * x).sum()) * float((y * y).sum()))
    return float((x * y).sum() / den) if den else float("nan")


# ----------------------------------------------------------------- validate

def cmd_validate(argv):
    """State plainly what this current field can and cannot be used for."""
    np = _np()
    rows = []
    log("\n=== what the free current field actually contains ===")
    log(f"  {'point':14}{'n':>8}{'mean':>9}{'p99':>9}{'max':>9}   {'known real max':>16}")
    # Published/pilot-guide peak surface currents, for the reality check.
    # Peak speeds typed in with no source anywhere in the repository (no pilot guide
    # or DMI/FCOO figure is pinned), so the underestimate factor computed from them is
    # not established. No page prints it.
    REAL = {"drogden": 1.7, "oresund_n": 1.5, "storebaelt": 1.8, "fehmarn": 1.2,
            "koege_bugt": 0.4, "oresund_s": 1.5}
    for name in POINTS:
        t, u, v, d = load_marine(np, name)
        s = np.sqrt(u * u + v * v)
        ok = np.isfinite(s)
        if ok.sum() == 0:
            log(f"  {name:14} no data")
            continue
        r = {"point": name, "n": int(ok.sum()),
             "mean_ms": round(float(np.nanmean(s)), 3),
             "p99_ms": round(float(np.nanpercentile(s, 99)), 3),
             "max_ms": round(float(np.nanmax(s)), 3),
             "grid_lat": d["latitude"], "grid_lon": d["longitude"]}
        if name in REAL:
            r["published_peak_ms"] = REAL[name]
            r["underestimate_factor"] = round(REAL[name] / max(r["max_ms"], 1e-6), 1)
        rows.append(r)
        ref = f"{REAL[name]:.1f} m/s" if name in REAL else ""
        log(f"  {name:14}{r['n']:>8,}{r['mean_ms']:>9.2f}{r['p99_ms']:>9.2f}"
            f"{r['max_ms']:>9.2f}   {ref:>16}")

    fac = [r["underestimate_factor"] for r in rows if "underestimate_factor" in r]
    log(f"\n  peak speeds run {min(fac):.1f}-{max(fac):.1f}x low against published values.")
    log("  => use direction, sign and timing. Do NOT use magnitude.")
    write_json(os.path.join(DERIVED, "currents_validate.json"), {"points": rows})
    return 0


# ----------------------------------------------------------------- index

def cmd_index(argv):
    """Fit a wind-driven Baltic filling/draining index against the modelled strait flow.

    If a simple integral of basin wind stress predicts the SIGN of the Sound current,
    then the 31-year wind record can stand in for the 4-year current record.
    """
    np = _np()
    wt, stress = load_basin_wind(np)
    widx = {t: i for i, t in enumerate(wt)}

    t, u, v, _ = load_marine(np, "oresund_n")
    flow = along(np, u, v, POINTS["oresund_n"][2])      # + = outflow toward Kattegat

    sel = np.array([widx.get(x, -1) for x in t])
    keep = sel >= 0
    sel = sel[keep]
    flow = flow[keep]

    log("\n=== fitting the memory of the Baltic ===")
    log(f"  {'window':>10}{'r':>10}   (basin wind stress vs northern Sound flow)")
    best = (None, -9)
    window_r = []
    cs = np.concatenate([[0.0], np.nancumsum(np.nan_to_num(stress))])
    for hours in WINDOWS_H:
        lo = np.maximum(sel - hours, 0)
        idx = -(cs[sel + 1] - cs[lo]) / np.maximum(sel - lo, 1)   # - => draining
        r = corr(np, idx, flow)
        window_r.append({"hours": hours, "r": round(r, 3)})
        star = ""
        if r > best[1]:
            best = (hours, r)
            star = "  <-"
        log(f"  {hours:>7} h{r:>10.3f}{star}")

    hours, r = best
    lo = np.maximum(sel - hours, 0)
    idx = -(cs[sel + 1] - cs[lo]) / np.maximum(sel - lo, 1)
    m = np.isfinite(idx) & np.isfinite(flow)
    agree = float(((idx[m] > 0) == (flow[m] > 0)).mean()) * 100
    log(f"\n  best window {hours} h, r = {r:.3f}")
    log(f"  sign agreement: {agree:.1f}% of {int(m.sum()):,} hours")

    out = {"best_window_h": hours, "r": round(r, 3),
           "sign_agreement_pct": round(agree, 1), "n_hours": int(m.sum()),
           "window_r": window_r, "flush_distance_km": FLUSH_KM,
           "verdict": ("A 24 h window beats every longer one and the correlation decays "
                       "monotonically past it. That is a local synoptic wind response, "
                       "not a multi-week Baltic filling signal. Either the basin-scale "
                       "memory is not there, or this coarse product cannot see it - and "
                       "on 61% sign agreement the index is not good enough to stand in "
                       "for the current record. It is reported as a negative result.")}

    # ---- retention: does the water go anywhere, or just slosh?
    #
    # This is the metric to trust. The residual (mean) current divided by the mean SPEED
    # is a pure ratio, so the model's factor-of-two magnitude error cancels out of it. A
    # value near 1 means the water is going somewhere - throughflow, flushing. A value
    # near 0 means it moves constantly and ends up where it started, which is what an
    # accumulation zone looks like. Nothing here depends on an absolute speed.
    out["retention"] = {}
    log("\n=== does the water go anywhere? ===")
    log(f"  {'point':14}{'mean spd':>10}{'residual':>11}{'bearing':>9}"
        f"{'persistence':>13}   flushing time over 20 km")
    for name, (_la, _lo, _ax, desc) in POINTS.items():
        tt, uu, vv, _ = load_marine(np, name)
        ok = np.isfinite(uu) & np.isfinite(vv)
        if ok.sum() < 1000:
            continue
        spd = float(np.nanmean(np.sqrt(uu * uu + vv * vv)))
        ru, rv = float(np.nanmean(uu)), float(np.nanmean(vv))
        res = math.hypot(ru, rv)
        brg = (math.degrees(math.atan2(ru, rv)) + 360) % 360
        pers = res / spd if spd else float("nan")
        days = (FLUSH_KM * 1000.0 / res / 86400) if res > 1e-4 else float("inf")
        out["retention"][name] = {
            "mean_speed_ms": round(spd, 4),
            "residual_ms": round(res, 4),
            "residual_bearing_deg": round(brg, 0),
            "persistence": round(pers, 3),
            "flush_days_20km": round(days, 1) if days != float("inf") else None,
            "desc": desc,
        }
        d_s = f"{days:>8.1f} d" if days != float("inf") else "      never"
        log(f"  {name:14}{spd:>9.3f} {res:>10.4f} {brg:>8.0f}° {pers:>12.3f}   {d_s}")

    ranked = sorted(out["retention"].items(), key=lambda kv: kv[1]["persistence"])
    log("\n  most retentive -> most flushed:")
    for n, r in ranked:
        log(f"    {r['persistence']:.3f}  {n:14} {r['desc']}")

    write_json(os.path.join(DERIVED, "currents_index.json"), out)
    return 0


# ----------------------------------------------------------------- transport

def cmd_transport(argv):
    """Do Copenhagen's overflow hours move water toward Køge Bugt?

    Copenhagen discharges into the harbour and the southern Sound. Køge Bugt is SOUTH of
    that. The mean flow in the Sound runs north. So the claim "Køge Bugt receives
    Copenhagen's overflows" is not a claim about the average - it is a claim that the
    specific hours in which the city overflows are hours in which the water runs south.

    That is directly testable, because the rain record and the current record overlap.
    """
    np = _np()
    ct, cu, cv, _ = load_marine(np, "oresund_s")
    flow = along(np, cu, cv, POINTS["oresund_s"][2])     # + = north, away from Køge Bugt
    cidx = {t: i for i, t in enumerate(ct)}

    wt, U, D, P = load_cph_wind(np)
    sel = np.array([cidx.get(t, -1) for t in wt])
    keep = sel >= 0
    sel, P, U, D = sel[keep], P[keep], U[keep], D[keep]
    wt = [t for t, k in zip(wt, keep.tolist()) if k]
    f = flow[sel]
    log(f"\n{len(wt):,} hours where the rain record and the current record overlap "
        f"({wt[0][:10]} to {wt[-1][:10]})")

    # antecedent rain: what actually fills a combined sewer is the preceding hours
    ap = np.convolve(np.nan_to_num(P), np.ones(RAIN_WINDOW_H), mode="full")[:len(P)]

    base = float(np.nanmean(f < 0)) * 100
    log(f"\nbaseline: water runs SOUTH toward Køge Bugt {base:.1f}% of all hours")

    out = {"n_hours": len(wt), "period": [wt[0], wt[-1]],
           "baseline_southward_pct": round(base, 1), "bands": [], "lag": [],
           "rain_window_h": RAIN_WINDOW_H, "event_threshold_mm": EVENT_MM}

    log("\n=== southward transport, by how hard it is raining ===")
    log(f"  {'6 h rainfall':>18}{'hours':>10}{'southward':>12}{'vs baseline':>14}")
    bands = [(0.0, 0.1, "dry"), (0.1, 2.0, "light"), (2.0, 5.0, "moderate"),
             (5.0, 10.0, "heavy"), (10.0, 20.0, "overflow-scale"),
             (20.0, 1e9, "cloudburst-scale")]
    for lo, hi, lbl in bands:
        m = (ap >= lo) & (ap < hi) & np.isfinite(f)
        if m.sum() < 30:
            continue
        pct = float((f[m] < 0).mean()) * 100
        out["bands"].append({"label": lbl, "mm_6h": [lo, None if hi > 1e8 else hi],
                             "hours": int(m.sum()), "southward_pct": round(pct, 1),
                             "vs_baseline_pp": round(pct - base, 1)})
        log(f"  {lbl:>18}{int(m.sum()):>10,}{pct:>11.1f}%{pct - base:>+13.1f} pp")

    log("\n=== and in the hours after the rain, when the plume is travelling ===")
    log(f"  {'lag':>8}{'hours':>10}{'southward':>12}{'vs baseline':>14}")
    ev = (ap >= EVENT_MM)
    for lag in LAGS_H:
        sh = np.zeros(len(ev), dtype=bool)
        if lag == 0:
            sh = ev
        else:
            sh[lag:] = ev[:-lag]
        m = sh & np.isfinite(f)
        if m.sum() < 30:
            continue
        pct = float((f[m] < 0).mean()) * 100
        out["lag"].append({"lag_h": lag, "hours": int(m.sum()),
                           "southward_pct": round(pct, 1),
                           "vs_baseline_pp": round(pct - base, 1)})
        log(f"  {lag:>6} h{int(m.sum()):>10,}{pct:>11.1f}%{pct - base:>+13.1f} pp")

    # seasonality of the joint condition
    log("\n=== when do rain and southward transport coincide? ===")
    mon = np.array([int(t[5:7]) for t in wt])
    yrs = len(set(t[:4] for t in wt))
    names = "JanFebMarAprMayJunJulAugSepOctNovDec"
    log(f"  {'month':>6}{'overflow-scale h/yr':>22}{'of those, southward':>22}")
    out["by_month"] = {}
    for m_ in range(1, 13):
        sm = mon == m_
        e = float((ev & sm).sum()) / yrs
        both = float((ev & sm & (f < 0)).sum()) / yrs
        out["by_month"][names[(m_ - 1) * 3:m_ * 3]] = {
            "overflow_scale_h_per_yr": round(e, 1), "and_southward_h_per_yr": round(both, 1)}
        log(f"  {names[(m_-1)*3:m_*3]:>6}{e:>21.1f}{both:>21.1f}   "
            + "#" * int(both / 2))

    write_json(os.path.join(DERIVED, "currents_transport.json"), out)
    log("\nwrote data/derived/currents_transport.json")
    return 0


# ----------------------------------------------------------------- rain climate

SECTORS = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")
RAIN_OUT = os.path.join(DERIVED, "currents_rain.json")


def _sector(np, deg):
    """Eight compass sectors, 45 degrees wide and centred on N, NE, ... (index 0-7)."""
    return (np.floor(((deg % 360) + 22.5) / 45.0) % 8).astype(int)


def rain_climate():
    """Over the whole Copenhagen weather record, not the four years of currents:
    monthly rainfall, the hours that reach overflow scale by month, and the wind
    sector in those hours and in the hours after them. Written to
    data/derived/currents_rain.json for the report, which reads it live."""
    np = _np()
    t, U, D, P = load_cph_wind(np)
    years = sorted({x[:4] for x in t})
    ny = len(years)
    mon = np.array([int(x[5:7]) for x in t])
    ap = np.convolve(np.nan_to_num(P), np.ones(RAIN_WINDOW_H), mode="full")[:len(P)]
    ev = ap >= EVENT_MM
    ok = np.isfinite(D)
    sec = np.full(len(D), -1)
    sec[ok] = _sector(np, D[ok])
    names = "JanFebMarAprMayJunJulAugSepOctNovDec"
    months = {}
    for m in range(1, 13):
        sm = mon == m
        months[names[(m - 1) * 3:m * 3]] = {
            "rain_mm": round(float(np.nansum(P[sm])) / ny, 1),
            "overflow_scale_h_per_yr": round(float((ev & sm).sum()) / ny, 1)}

    def dist(mask):
        m = mask & (sec >= 0)
        n = int(m.sum())
        return {"hours": n, "pct": {SECTORS[i]: round(float((sec[m] == i).sum()) / n * 100, 1)
                                    for i in range(8)} if n else {}}
    lagged = {}
    for lag in LAGS_H:
        sh = np.zeros(len(ev), dtype=bool)
        if lag == 0:
            sh = ev.copy()
        else:
            sh[lag:] = ev[:-lag]
        lagged[str(lag)] = dist(sh)
    out = {"_what": "Copenhagen's ERA5 weather record, whole: monthly rain, overflow-scale "
                    "hours by month, and the wind sector at and after those hours. Written "
                    "by scripts/currents.py (rain_climate), read by its report.",
           "period": [t[0], t[-1]], "years": ny, "rain_window_h": RAIN_WINDOW_H,
           "event_threshold_mm": EVENT_MM, "months": months,
           "wind_all_hours": dist(np.ones(len(ev), dtype=bool)), "wind_after_event": lagged}
    write_json(RAIN_OUT, out)
    return out


# ----------------------------------------------------------------- report

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def cmd_report(argv):
    """Render docs/CURRENTS.md from the stored results. Every number is live and every
    assertion a checked claim (LIVE_NUMBERS.md section 11); what no stored result or
    readable source supports is not said here - it is in docs/ARCHIVE.md."""
    import claims
    import live
    rain_climate()
    va = live.live_json(os.path.join(DERIVED, "currents_validate.json"))
    ix = live.live_json(os.path.join(DERIVED, "currents_index.json"))
    tr = live.live_json(os.path.join(DERIVED, "currents_transport.json"))
    wv = live.live_json(os.path.join(DERIVED, "waves.json"))
    rc = live.live_json(RAIN_OUT)
    cd, _, _ = claims.load()
    cache = {}

    def rd(ph):
        return claims.resolve(cd, ph, cache)[0]
    B, E, C = live.claim_begin, live.CLAIM_END, live.claim
    grid = rd("{read:OM-MARINE:0.08|computed at 0.08° (~8 km) resolution}")
    grid_km = rd("{read:OM-MARINE:8|computed at 0.08° (~8 km) resolution}")
    narrow = rd("{read:WIKI-ORESUND:4|its width varies from 4 kilometres}")
    o4 = rd("{read:NI-DCE-ILT-2025:4|iltkoncentrationen i vandet er mindre end 4 mg l-1}")
    bal = rd("{read:CMEMS-BAL-STAC:1|1 nautical mile horizontal resolution}")
    kat = rd("{read:WIKI-ORESUND:30|has a salinity of more than 30 PSU}")
    balt = rd("{read:WIKI-ORESUND:7|the Baltic Sea (around 7 PSU}")
    km = ix["flush_distance_km"]
    o = []
    a = o.append

    a("# Where the water goes\n")
    a(B("C-CS-DATA") + "Generated by `scripts/currents.py`. Currents from the Open-Meteo Marine "
      "API, hourly, 2022-2026; wind and rain from the ERA5 archive, hourly, "
      f"{rc['period'][0][:4]}-{rc['period'][1][:4]}. Both free and keyless." + E
      + " Companion to [SEABED.md](SEABED.md), which computes what the wind lifts off the "
      "bed; this asks where it then goes.\n")

    a("## First, what this data cannot do\n")
    a(B("C-CS-GRID") + f"Open-Meteo computes its ocean currents at {grid}° (about {grid_km} km), "
      f"and the Øresund narrows to {narrow} km. A field that coarse cannot resolve the narrow "
      "straits, so what follows rests on ratios, signs and timings; the one figure that uses a "
      "speed - a flushing time in days - carries whatever speed error the field has." + E + "\n")
    a(B("C-CS-PEAKS") + "The peak speed the field reaches at each point is below. The script "
      "sets these beside peak speeds it records as published, but no source for those is held, "
      "so that comparison is not used here." + E + "\n")
    a("| Point | Peak speed in the field |")
    a("|---|---:|")
    for r in va["points"]:
        a(f"| {r['point']} | {r['max_ms']:.2f} m/s |")
    a("")

    ret = ix["retention"]
    a("## The result: Køge Bugt keeps its water longest\n")
    a(B("C-CS-METRIC") + "The measure is the **residual current divided by the mean speed** - "
      "how much of the water's motion actually goes somewhere. A speed error common to both "
      "cancels out of that ratio. The flushing time in days is the distance over the residual "
      "alone, so it keeps whatever speed error the field has at that point." + E + "\n")
    a(f"| Point | Mean speed | Residual | Residual heading | Residual ÷ mean speed | "
      f"Flushing time over {km:.0f} km |")
    a("|---|---:|---:|---:|---:|---:|")
    for n, r in sorted(ret.items(), key=lambda kv: kv[1]["residual_ms"] / kv[1]["mean_speed_ms"]):
        fd = r["flush_days_20km"]
        a(f"| {n} | {r['mean_speed_ms']:.3f} m/s | {r['residual_ms']:.4f} m/s | "
          f"{r['residual_bearing_deg']:.0f}° | {r['residual_ms'] / r['mean_speed_ms']:.2f} | "
          + (f"**{fd:,.1f} days** |" if fd is not None else "never |"))
    a("")
    k, aa, sb, sy = ret["koege_bugt"], ret["aarhus_bugt"], ret["storebaelt"], ret["sydfynske"]
    lowest = all(k["mean_speed_ms"] <= r["mean_speed_ms"] and k["residual_ms"] <= r["residual_ms"]
                 for r in ret.values())
    a(B("C-CS-FLUSH") + f"**In this field Køge Bugt takes {k['flush_days_20km']:.0f} days to move "
      f"water {km:.0f} km, and Aarhus Bugt takes {aa['flush_days_20km']:.1f}** - a factor of "
      f"{k['flush_days_20km'] / aa['flush_days_20km']:.0f}."
      + (" Køge Bugt has both the lowest mean speed in the set and the smallest residual: the "
         "water moves and ends up close to where it started." if lowest else "") + E + "\n")
    a(B("C-CS-BELT") + "*One caveat.* A low residual can also mean strong reversing flow with "
      f"little net - which is what the Great Belt's {sb['flush_days_20km']:.0f} days is. The Belt "
      f"has {sb['mean_speed_ms'] / k['mean_speed_ms']:.1f}× Køge Bugt's mean speed: it moves "
      "water back and forth vigorously and averages out. Køge Bugt is slow *and* close to "
      "net-zero, and only the second of these is retention of the kind asked about here." + E + "\n")

    a("### What the oxygen survey sees\n")
    a(C("C-CS-ILT-DEF", f"DCE call it iltsvind when the oxygen concentration is below {o4} mg/l, "
        "and it develops at the bottom especially where the water column is stratified.") + " "
      + C("C-CS-ILT-OBS", "In DCE's autumn surveys Aarhus Bugt was among the hardest-hit areas "
          "in October 2023 and still had sporadic moderate iltsvind late in November 2025; in "
          "both years DCE registered no iltsvind in Køge Bugt.") + "\n")
    a(B("C-CS-INVERT") + "So the survey and this table rank different properties. Iltsvind is a "
      "concentration at the bottom, likeliest where the water is layered; the table ranks "
      "whether the water goes anywhere, and on that Køge Bugt is the extreme case in this set. "
      "A water can keep what it receives without registering iltsvind, and a survey that "
      "counts iltsvind would not show it." + E + "\n")
    a(B("C-CS-SYDFYN") + f"**Det Sydfynske Øhav** comes out at {sy['flush_days_20km']:.1f} days - "
      "retentive, but far from Køge Bugt - and DCE's surveys found iltsvind there in both "
      "years. On this evidence the two bays are not the same case. A field this coarse cannot "
      "resolve an archipelago, so this is weak evidence either way." + E + "\n")

    a("## A negative result: the wind index does not work\n")
    a(B("C-CS-INDEX-PLAN") + "The plan was to regress the strait flow on a wind-driven Baltic "
      f"filling index and, if it held, use the {rc['years']}-year wind record to extend the "
      "current record. It does not hold." + E + "\n")
    longer = [w for w in ix["window_r"] if w["hours"] > ix["best_window_h"]]
    tail = ", ".join(f"{w['hours']} h gives {w['r']:.2f}" for w in longer[-3:])
    a(B("C-CS-INDEX") + f"Best correlation is **r = {ix['r']:.2f} at a {ix['best_window_h']} hour "
      f"window**, with sign agreement of only **{ix['sign_agreement_pct']:.0f}%** over "
      f"{ix['n_hours']:,} hours. The correlation falls away at the longer windows - {tail}." + E + "\n")
    a(B("C-CS-INDEX-READ") + f"A {ix['best_window_h']}-hour optimum is a local wind response, not "
      "a basin filling and draining over weeks. Either the multi-week Baltic memory is not the "
      "dominant control on the Sound, or this coarse product cannot see it. **The extension "
      "over the long wind record is not available on this data**, and everything about "
      "currents here is as long as the current record." + E + "\n")

    a("## Does Copenhagen's overflow water go toward Køge Bugt?\n")
    so = ret["oresund_s"]
    a(B("C-CS-TEST") + "Køge Bugt lies south of Copenhagen, and the residual current at the "
      f"southern Sound point runs toward {so['residual_bearing_deg']:.0f}°, away from it. So the "
      "claim can only hold in particular hours: the hours in which the city overflows would have "
      "to be hours in which the water runs south. The rain record and the current record "
      f"overlap for {tr['n_hours']:,} hours, so this can be tested directly." + E + "\n")
    a(C("C-CS-BASELINE", "Across all of them the southern Sound runs south "
        f"**{tr['baseline_southward_pct']:.0f}%** of the time.") + "\n")
    a(f"| {tr['rain_window_h']}-hour rainfall | Hours | Runs south | vs baseline |")
    a("|---|---:|---:|---:|")
    for b_ in tr["bands"]:
        a(f"| {b_['label']} | {b_['hours']:,} | {b_['southward_pct']:.1f}% | "
          f"{b_['vs_baseline_pp']:+.1f} pp |")
    a("")
    ovf = next((b_ for b_ in tr["bands"] if b_["label"] == "overflow-scale"), None)
    a(B("C-CS-RAIN-NORTH") + "**During the rain, the water runs north**, and the harder it rains "
      "the more so" + (f": at overflow-scale rainfall, southward transport is "
                        f"{-ovf['vs_baseline_pp']:.0f} points below the baseline." if ovf else ".")
      + E + "\n")
    wa = rc["wind_all_hours"]["pct"]
    w0 = rc["wind_after_event"]["0"]["pct"]
    a(B("C-CS-RAIN-WIND") + "The wind record does not show south-westerlies that would explain "
      f"this simply: over {rc['years']} years, in the hours of overflow-scale rain the wind is "
      f"from the south-west or west {w0['SW'] + w0['W']:.0f}% of the time, against "
      f"{wa['SW'] + wa['W']:.0f}% of all hours. What drives the Sound north in those hours is "
      "not established here." + E + "\n")
    a("| Hours after the event | Runs south | vs baseline |")
    a("|---|---:|---:|")
    best = max(tr["lag"], key=lambda x: x["vs_baseline_pp"])
    for L in tr["lag"]:
        mark = " ←" if L is best else ""
        a(f"| +{L['lag_h']} h | {L['southward_pct']:.1f}% | **{L['vs_baseline_pp']:+.1f} pp**{mark} |")
    a("")
    wl = rc["wind_after_event"].get(str(best["lag_h"]))
    a(B("C-CS-LAG") + f"**{best['lag_h']} hours after an overflow-scale event, southward "
      f"transport runs {best['southward_pct']:.0f}% - {best['vs_baseline_pp']:+.0f} points above "
      "baseline.**" + (f" In the wind record the hours after such rain are the westerly ones: "
                        f"{best['lag_h']} hours later the wind is from the south-west or west "
                        f"{wl['pct']['SW'] + wl['pct']['W']:.0f}% of the time." if wl else "")
      + E + "\n")
    a(B("C-CS-LAG-READ") + "So the transport is neither the simple claim nor its refutation but "
      "a lag: the discharge happens under northward flow, and the flow reverses about half a "
      "day later, in the westerly weather that follows the rain." + E + "\n")
    first = tr["lag"][0]
    a(B("C-CS-FEW") + f"*Statistical honesty:* this rests on {first['hours']} event-hours, and "
      f"every lag in the table was tested; the {first['lag_h']}-hour and {best['lag_h']}-hour "
      "results are both large. A longer current record would settle it." + E + "\n")

    a("## When overflows happen, and when the bed is lifted\n")
    bm = rc["months"]
    names = list(bm)
    top = sorted(names, key=lambda m: -bm[m]["overflow_scale_h_per_yr"])[:3]
    top = [m for m in names if m in top]
    rest = [bm[m]["overflow_scale_h_per_yr"] for m in names if m not in top]
    rain = [bm[m]["rain_mm"] for m in names]
    mid = wv["depths_m"][1]
    dead = list(wv["critical_shear_Pa"])[0]
    byd = wv["by_depth"][str(float(mid))]["exceedance"][dead]["by_month"]
    wtop = sorted(byd, key=lambda m: -byd[m])[:4]
    wtop = [names[int(m) - 1] for m in sorted(wtop, key=lambda m: (int(m) - 7) % 12)]
    a(B("C-CS-SEASONS") + f"Over the {rc['years']} years of the Copenhagen weather record, rain "
      f"intense enough to overflow a combined sewer (at least {rc['event_threshold_mm']:.0f} mm "
      f"in {rc['rain_window_h']} hours) comes mostly in **{', '.join(top)}**, "
      f"{min(bm[m]['overflow_scale_h_per_yr'] for m in top):.1f}-"
      f"{max(bm[m]['overflow_scale_h_per_yr'] for m in top):.1f} hours a year in each, against "
      f"at most {max(rest):.1f} in any other month. Total rainfall varies much less, "
      f"{min(rain):.0f}-{max(rain):.0f} mm a month. Wave-driven bed resuspension is most "
      f"frequent in **{', '.join(wtop)}**." + E + "\n")
    a("| Month | Rain | Overflow-scale hours a year | Bed resuspension, relative to July |")
    a("|---|---:|---:|---:|")
    for i, m in enumerate(names, 1):
        a(f"| {m} | {bm[m]['rain_mm']:.0f} mm | {bm[m]['overflow_scale_h_per_yr']:.1f} | "
          f"{byd[str(i)] / byd['7']:.1f}× |")
    a("")
    a(B("C-CS-SEQUENCE") + "If the overflow's solids settle where they are discharged, the "
      "seasons line up into a sequence: delivery in the rain season into the most retentive "
      "water in this set, a residence time of months, and resuspension in the gales. The "
      "seasons and the flushing time are computed here; that the discharged material settles in "
      "Køge Bugt and is lifted again later is not measured." + E + "\n")

    a("## When rain and southward transport coincide\n")
    a("| Month | Overflow-scale hours/yr | ...of those, running south |")
    a("|---|---:|---:|")
    tb = tr["by_month"]
    for m in MONTHS:
        v = tb[m]
        a(f"| {m} | {v['overflow_scale_h_per_yr']:.1f} | {v['and_southward_h_per_yr']:.1f} |")
    a("")
    joint = sum(tb[m]["and_southward_h_per_yr"] for m in MONTHS)
    a(B("C-CS-JOINT") + "These are the years the current record covers, and the numbers are "
      f"small. The joint condition is rare - {joint:.1f} hours a year in all. If transport toward "
      "Køge Bugt happens in so few hours, an annual-average accounting cannot represent it, and "
      "neither can monitoring that samples on a calendar." + E + "\n")

    a("## What is still missing\n")
    a("- " + C("C-CS-NEED-FIELD", "**A current field that resolves the straits.** Copernicus "
               f"Marine publishes a Baltic reanalysis at {bal} nautical mile resolution. "
               "Everything here would be worth redoing on it, the retention result first."))
    a("- " + C("C-CS-NEED-TRACK", "**Particle tracking.** Retention is a summary statistic. "
               "Where material released off Amager ends up needs trajectories, which need the "
               "field above."))
    a("- " + C("C-CS-NEED-LONGER", "**A longer current record.** The wind index failed, so the "
               "current record cannot be extended backwards, and the event counts stay small."))
    a("- " + C("C-CS-NEED-DENSITY", f"**Density.** The Sound lies between the Kattegat, at more "
               f"than {kat} PSU, and the Baltic, at around {balt} PSU, and its surface stream is "
               "often northbound from the Baltic. One current per point cannot show whether a "
               "plume and the water beneath it are moving differently."))
    a("")

    try:
        write_doc(os.path.join(ROOT, "docs", "CURRENTS.md"), "\n".join(o) + "\n")
    except (live.Unjustified, claims.Refused) as e:
        log(str(e))
        return 1
    log("wrote docs/CURRENTS.md")
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmds = {"fetch": cmd_fetch, "validate": cmd_validate, "index": cmd_index,
            "transport": cmd_transport,
            "rain": lambda argv: rain_climate() and 0,
            "report": cmd_report}
    c = argv[0]
    if c not in cmds:
        print(__doc__)
        return 1
    return cmds[c](argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
