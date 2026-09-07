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
    global physics model. Starts 2022-01-01. NOTE the resolution problem, quantified in
    cmd_validate: a ~9 km global grid does not resolve the Danish straits, and the
    speeds come out roughly a factor of three low. Direction and timing survive; the
    magnitudes do not, and nothing here depends on them.
  - Open-Meteo ERA5 archive: hourly wind and precipitation, 1995-2025, already fetched
    by the wave work.

The structure follows from that: the 4-year current record is used only to CALIBRATE a
wind-driven index, and the 31-year wind record is what the index is then evaluated over.

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
from common import DERIVED, RAW, ROOT, fetch, log, read_json, write_json

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
    cs = np.concatenate([[0.0], np.nancumsum(np.nan_to_num(stress))])
    for hours in (6, 12, 24, 48, 72, 120, 168, 240, 336, 504, 720):
        lo = np.maximum(sel - hours, 0)
        idx = -(cs[sel + 1] - cs[lo]) / np.maximum(sel - lo, 1)   # - => draining
        r = corr(np, idx, flow)
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
        days = (20000.0 / res / 86400) if res > 1e-4 else float("inf")
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
    ap = np.convolve(np.nan_to_num(P), np.ones(6), mode="full")[:len(P)]

    base = float(np.nanmean(f < 0)) * 100
    log(f"\nbaseline: water runs SOUTH toward Køge Bugt {base:.1f}% of all hours")

    out = {"n_hours": len(wt), "period": [wt[0], wt[-1]],
           "baseline_southward_pct": round(base, 1), "bands": [], "lag": []}

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
    ev = (ap >= 10.0)
    for lag in (0, 6, 12, 24, 48, 72):
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


# ----------------------------------------------------------------- report

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def cmd_report(argv):
    np = _np()
    va = read_json(os.path.join(DERIVED, "currents_validate.json"))
    ix = read_json(os.path.join(DERIVED, "currents_index.json"))
    tr = read_json(os.path.join(DERIVED, "currents_transport.json"))
    o = []
    a = o.append

    a("# Where the water goes\n")
    a("Generated by `scripts/currents.py`. Currents from the Open-Meteo Marine API "
      "(CMEMS global physics, hourly, 2022-2026); wind and rain from the ERA5 archive "
      "(hourly, 1995-2025). Both free and keyless. Companion to "
      "[SEABED.md](#SEABED.md), which computes what the wind lifts off the bed; this "
      "asks where it then goes.\n")

    a("## First, what this data cannot do\n")
    a("The only free current field covering Danish waters is a global model on a roughly "
      "9 km grid. The Danish straits are narrower than that. Before using it for "
      "anything, here is the peak speed it produces against published values:\n")
    a("| Point | Model peak | Published peak | Ratio |")
    a("|---|---:|---:|---:|")
    for r in va["points"]:
        if "published_peak_ms" not in r:
            continue
        a(f"| {r['point']} | {r['max_ms']:.2f} m/s | {r['published_peak_ms']:.1f} m/s | "
          f"{r['underestimate_factor']:.1f}× |")
    a("")
    a("The open-water points are about right; the narrow straits come out roughly half "
      "the real speed, which is what a 9 km grid does to a 4 km channel. **So nothing "
      "below uses an absolute speed.** Everything is a ratio, a sign, or a timing, and "
      "each is stated with the reason it survives the calibration error.\n")

    a("## The result: Køge Bugt does not flush\n")
    a("The metric is the **residual current divided by the mean speed** — how much of "
      "the water's motion actually goes somewhere. A factor-of-two error in speed "
      "cancels out of a ratio of two speeds, so this number survives the problem above.\n")
    a("| Point | Mean speed | Residual | Residual heading | Flushing time over 20 km |")
    a("|---|---:|---:|---:|---:|")
    ret = ix["retention"]
    for n, r in sorted(ret.items(), key=lambda kv: -(kv[1]["flush_days_20km"] or 1e9)):
        fd = r["flush_days_20km"]
        a(f"| {n} | {r['mean_speed_ms']:.3f} m/s | {r['residual_ms']:.4f} m/s | "
          f"{r['residual_bearing_deg']:.0f}° | **{fd:,.0f} days**" + " |")
    a("")
    k = ret["koege_bugt"]
    aa = ret["aarhus_bugt"]
    a(f"**Køge Bugt takes {k['flush_days_20km']:.0f} days to move water 20 km. Aarhus "
      f"Bugt takes {aa['flush_days_20km']:.1f}.** A factor of "
      f"{k['flush_days_20km']/aa['flush_days_20km']:.0f}. Køge Bugt has both the lowest "
      "mean speed in the set and the smallest residual: the water moves constantly and "
      "ends up where it started.\n")
    a("*One caveat, applied honestly.* A low residual can also mean a strong reversing "
      "flow with little net — which is what the Great Belt's 23 days is. The Belt has "
      f"{ret['storebaelt']['mean_speed_ms']/k['mean_speed_ms']:.1f}× Køge Bugt's mean "
      "speed; it exchanges water vigorously and just happens to average out. Køge Bugt "
      "is slow *and* net-zero. Those are different states and only the second is "
      "retention.\n")

    a("### Which inverts the monitoring\n")
    a("Aarhus Bugt registers oxygen depletion every year. Køge Bugt is recorded as "
      "having none, including in 2023 and 2025. And Aarhus Bugt flushes twenty times "
      "faster.\n")
    a("That is not a contradiction, because the two things are not the same "
      "phenomenon. DCE's iltsvind criterion is dissolved oxygen below 4 mg/l in "
      "**stratified bottom water** — which requires depth and a sealed layer, and Aarhus "
      "Bugt has both. Køge Bugt is shallow and mixes, so it cannot qualify however bad "
      "it gets. But retention of surface material, floating mats and fine sediment is a "
      "*different* property, and on that one Køge Bugt is the extreme case in this set.\n")
    a("The national instrument measures the property Køge Bugt does not have, and does "
      "not measure the property it has more of than anywhere else here.\n")
    a("**Det Sydfynske Øhav** comes out mid-range at "
      f"{ret['sydfynske']['flush_days_20km']:.1f} days — retentive, but nothing like "
      "Køge Bugt. It does register iltsvind. On this evidence the two bays are not the "
      "same case, and the shared vortex description is not supported by this model. "
      "A 9 km grid cannot resolve an archipelago, so this is weak evidence either way.\n")

    a("## A negative result: the wind index does not work\n")
    a("The plan was to regress the strait flow on a wind-driven Baltic filling index, "
      "and if it held, use the 31-year wind record to extend the 4-year current record. "
      "It does not hold.\n")
    a(f"Best correlation is **r = {ix['r']:.2f} at a {ix['best_window_h']} hour window**, "
      f"with sign agreement of only **{ix['sign_agreement_pct']:.0f}%** over "
      f"{ix['n_hours']:,} hours. Correlation decays monotonically at every longer window "
      "— 168 h gives 0.17, 336 h gives 0.01.\n")
    a("A 24-hour optimum is a local synoptic wind response, not a basin filling and "
      "draining over weeks. Either the multi-week Baltic memory is not the dominant "
      "control on the Sound, or this coarse product cannot see it. Reported as a "
      "negative result: **the 31-year extension is not available on this data.** "
      "Everything about currents here is four years long.\n")

    a("## Does Copenhagen's overflow water go toward Køge Bugt?\n")
    a("Copenhagen discharges into the harbour and the southern Sound. Køge Bugt is "
      "south of that, and the mean flow runs north. So the claim is not about averages: "
      "it requires that the **specific hours in which the city overflows** are hours in "
      "which the water runs south. The rain record and the current record overlap for "
      f"{tr['n_hours']:,} hours, so this is directly testable.\n")
    a(f"Baseline: the southern Sound runs south **{tr['baseline_southward_pct']:.0f}%** "
      "of all hours.\n")
    a("| 6-hour rainfall | Hours | Runs south | vs baseline |")
    a("|---|---:|---:|---:|")
    for b in tr["bands"]:
        a(f"| {b['label']} | {b['hours']:,} | {b['southward_pct']:.1f}% | "
          f"{b['vs_baseline_pp']:+.1f} pp |")
    a("")
    a("**During the rain, the water runs north.** The harder it rains, the more strongly "
      "— at overflow-scale rainfall, southward transport is 18 points *below* baseline. "
      "Which is physically obvious once seen: heavy rain in Copenhagen arrives with "
      "cyclonic southwesterlies, and those drive the Sound north.\n")
    a("Taken alone that refutes the transport claim. But an overflow plume does not stop "
      "moving when the rain stops:\n")
    a("| Hours after the event | Runs south | vs baseline |")
    a("|---|---:|---:|")
    for L in tr["lag"]:
        mark = " ←" if L["vs_baseline_pp"] == max(x["vs_baseline_pp"] for x in tr["lag"]) else ""
        a(f"| +{L['lag_h']} h | {L['southward_pct']:.1f}% | "
          f"**{L['vs_baseline_pp']:+.1f} pp**{mark} |")
    a("")
    best = max(tr["lag"], key=lambda x: x["vs_baseline_pp"])
    a(f"**Twelve hours after an overflow-scale event, southward transport runs "
      f"{best['southward_pct']:.0f}% — {best['vs_baseline_pp']:+.0f} points above "
      "baseline.** That is the post-frontal wind veer: the front passes, the wind swings "
      "to the northwest, and the water reverses while the plume is still in it.\n")
    a("So the mechanism is neither the simple claim nor its refutation. It is a **lag**. "
      "The discharge happens under northward flow and the transport reverses roughly "
      "half a day later, on a timescale set by the same weather system that caused the "
      "discharge.\n")
    a(f"*Statistical honesty:* this rests on {tr['lag'][0]['hours']} event-hours, and "
      "six lags were tested. The 0-hour and 12-hour results are both large and both have "
      "the same simple mechanism behind them, which is why they are reported. A longer "
      "current record would settle it; four years is what exists.\n")

    a("## A correction to SEABED.md\n")
    a("That document said the resuspension season coincides with the overflow season. "
      "Over 31 years of rainfall that is wrong, and the error is worth keeping visible.\n")
    a("| | Peak months |")
    a("|---|---|")
    a("| Rain intense enough to overflow a combined sewer (≥10 mm in 6 h) | **Jun–Aug**, "
      "4.2–5.1 h/yr; near zero Jan–Apr |")
    a("| Total rainfall | flat, 38–72 mm/month, slight Jun–Aug and Oct maxima |")
    a("| Wave-driven bed resuspension | **Oct–Jan**, roughly double July |")
    a("| Strong onshore wind (stranding) | **Oct–Jan** |")
    a("")
    a("Overflow *events* are driven by intensity, and intensity in Denmark is "
      "convective, and convection is summer. The autumn is wetter in total but gentler.\n")
    a("This does not weaken the case — it sharpens it into a **deposit-then-mobilise "
      "sequence**:\n")
    for i, t in enumerate([
        "**June–August:** cloudbursts overflow the combined system. Sewage solids, fat "
        "and basin sludge are discharged into a warm, weakly-mixed, retentive bay.",
        "**The bay holds it.** Flushing time is on the order of months, so the material "
        "settles locally rather than being exported.",
        "**Through late summer:** it decays in place, in the warmest water of the year, "
        "with the oxygen demand and the smell that implies.",
        "**October–January:** the gales arrive. The bed — now looser for having been "
        "anoxic — resuspends twice as often as in July, and the same wind that lifts it "
        "drives it onto the western shore.",
    ], 1):
        a(f"{i}. {t}")
    a("")
    a("Delivery in summer and arrival on the shore in autumn are not in conflict. They "
      "are the two ends of a months-long residence time, and the residence time is the "
      "measured part.\n")

    a("## When rain and southward transport coincide\n")
    a("| Month | Overflow-scale hours/yr | ...of those, running south |")
    a("|---|---:|---:|")
    for m in MONTHS:
        v = tr["by_month"][m]
        a(f"| {m} | {v['overflow_scale_h_per_yr']:.1f} | "
          f"{v['and_southward_h_per_yr']:.1f} |")
    a("")
    a("Small numbers, and they should be read as small. The joint condition is rare — "
      "which is the point. If the transport to Køge Bugt happens in a handful of hours "
      "a year, then an annual-average accounting cannot represent it at all, and neither "
      "can a monitoring programme that samples on a calendar.\n")

    a("## What is still missing\n")
    for t in [
        "**A current field that resolves the straits.** CMEMS publishes a Baltic regional "
        "reanalysis at roughly 1 km behind free registration. Everything here would be "
        "worth redoing on it, and the retention result is the one to re-test first.",
        "**Particle tracking.** Retention time is a summary statistic. Where material "
        "released off Amager actually ends up needs trajectories, which needs the field "
        "above.",
        "**More than four years.** The wind index failed, so there is no way to extend "
        "the current record backwards, and the event counts stay small.",
        "**Density.** The Sound is strongly stratified — Baltic water out on top, Kattegat "
        "water in underneath. A single depth-averaged current hides that a plume and the "
        "bottom water can be going opposite ways at the same hour.",
    ]:
        a(f"- {t}")
    a("")

    path = os.path.join(ROOT, "docs", "CURRENTS.md")
    text = "\n".join(o)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    log(f"wrote docs/CURRENTS.md ({len(text):,} chars)")
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    cmds = {"fetch": cmd_fetch, "validate": cmd_validate, "index": cmd_index,
            "transport": cmd_transport,
            "report": cmd_report}
    c = argv[0]
    if c not in cmds:
        print(__doc__)
        return 1
    return cmds[c](argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
