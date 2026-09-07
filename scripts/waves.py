#!/usr/bin/env python3
"""Wind -> waves -> bed shear stress in Køge Bugt, hourly, 1995-2025.

Why this and not a current model: in a shallow bay the thing that lifts sediment off the
bed is the orbital motion under waves, and that is computable from wind alone given the
fetch. Currents redistribute what the waves have already lifted - important, but a
second-order question that needs data we do not have.

Chain:
  wind speed + direction  ->  fetch in that direction (ray-cast to the OSM coastline)
                          ->  fetch-limited wave height and period (Young & Verhagen 1996,
                             shallow-water form, which is the right one for a 5-15 m bay)
                          ->  bottom orbital velocity (linear wave theory)
                          ->  bed shear stress (Swart friction factor)
                          ->  compared against the critical stress for a LIVE bed and a
                             DEAD one, which differ by roughly a factor of five

The live/dead comparison is the point. Biofilm, tube worms and eelgrass raise the erosion
threshold several-fold; hypoxia and trawling remove them. The same weather over a dead bed
resuspends far more often, and resuspended sulphidic mud is itself an oxygen sink.

Usage:  python3 scripts/waves.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, read_json, write_json

G = 9.81
RHO = 1015.0            # brackish Køge Bugt water
KS = 0.005              # bed roughness, m - fine sediment with some ripple
DEPTHS = (3.0, 5.0, 10.0)

# Critical bed shear stress, Pa. Ranges from the cohesive-sediment literature; the point
# is the ratio, not the exact value.
TAU_C = {
    "dead bed (no biology)": 0.10,
    "live bed (biofilm, fauna, eelgrass)": 0.50,
}
WEATHER = os.path.join(RAW, "weather")


def _np():
    import numpy as np
    return np


def load_wind(np):
    """Concatenate the fetched archive chunks into arrays."""
    times, spd, drc, prc, tmp = [], [], [], [], []
    for f in sorted(os.listdir(WEATHER)):
        if not f.startswith("wind_"):
            continue
        h = read_json(os.path.join(WEATHER, f))["hourly"]
        times += h["time"]
        spd += h["wind_speed_10m"]
        drc += h["wind_direction_10m"]
        prc += h.get("precipitation") or [None] * len(h["time"])
        tmp += h.get("temperature_2m") or [None] * len(h["time"])
    f = lambda a: np.array([x if x is not None else np.nan for x in a], dtype=float)
    return times, f(spd), f(drc), f(prc), f(tmp)


def fetch_lookup(np, direction):
    """Fetch in metres for each wind direction, from the precomputed 5-degree table."""
    tab = read_json(os.path.join(WEATHER, "fetch.json"))
    keys = np.array(sorted(int(k) for k in tab))
    vals = np.array([tab[str(k)] for k in keys], dtype=float)
    idx = (np.round(direction / 5.0).astype(int) * 5) % 360
    pos = np.searchsorted(keys, idx)
    pos = np.clip(pos, 0, len(keys) - 1)
    return vals[pos]


def young_verhagen(np, U, F, d):
    """Shallow-water fetch-limited wave growth. Returns significant height and peak period.

    Young & Verhagen (1996). Reduces to deep-water Pierson-Moskowitz when depth is large,
    and correctly caps wave growth in shallow water - which matters here, because a 3 m
    bay cannot grow the waves a 120 km fetch would otherwise imply.
    """
    U = np.maximum(U, 0.5)
    delta = G * d / U**2
    chi = G * F / U**2
    A1 = 0.493 * delta**0.75
    B1 = 3.13e-3 * chi**0.57
    # eps is non-dimensional ENERGY (g^2 E / U^4), so Hs = 4 sqrt(E), not eps*U^2/g.
    eps = 3.64e-3 * (np.tanh(A1) * np.tanh(B1 / np.tanh(A1)))**1.74
    Hs = 4.0 * np.sqrt(np.maximum(eps, 0.0)) * U**2 / G

    A2 = 0.331 * delta**1.01
    B2 = 5.215e-4 * chi**0.73
    nu = 0.133 * (np.tanh(A2) * np.tanh(B2 / np.tanh(A2)))**-0.37
    Tp = U / (nu * G)
    return Hs, np.clip(Tp, 0.5, 20.0)


def wavenumber(np, Tp, d):
    """Solve the linear dispersion relation by fixed-point iteration."""
    omega = 2 * np.pi / Tp
    k = omega**2 / G                       # deep-water first guess
    for _ in range(40):
        k = omega**2 / (G * np.tanh(np.clip(k * d, 1e-6, 50)))
    return k


def bed_shear(np, Hs, Tp, d):
    """Bottom orbital velocity and wave-induced bed shear stress."""
    k = wavenumber(np, Tp, d)
    sh = np.sinh(np.clip(k * d, 1e-6, 50))
    ub = np.pi * Hs / (Tp * sh)
    A = ub * Tp / (2 * np.pi)              # orbital semi-excursion
    r = np.clip(A / KS, 1.1, 1e6)
    fw = np.exp(5.213 * r**-0.194 - 5.977)  # Swart
    fw = np.clip(fw, 0.002, 0.3)
    return ub, 0.5 * RHO * fw * ub**2


def main():
    np = _np()
    if not os.path.exists(os.path.join(WEATHER, "fetch.json")):
        log("fetch.json missing - run the fetch computation first")
        return 1
    times, U, D, P, T = load_wind(np)
    log(f"{len(times):,} hourly records, {times[0][:10]} to {times[-1][:10]}")

    F = fetch_lookup(np, D)
    months = np.array([int(t[5:7]) for t in times])
    years = np.array([int(t[:4]) for t in times])

    res = {"period": [times[0], times[-1]], "hours": len(times),
           "critical_shear_Pa": TAU_C, "depths_m": list(DEPTHS), "by_depth": {}}

    log("\n=== hours per year above the resuspension threshold ===")
    log(f"  {'depth':>7}{'':4}" + "".join(f"{k.split(' (')[0]:>26}" for k in TAU_C))
    yrs = len(set(years.tolist()))
    for d in DEPTHS:
        Hs, Tp = young_verhagen(np, U, F, d)
        ub, tau = bed_shear(np, Hs, Tp, d)
        row = {"mean_Hs_m": round(float(np.nanmean(Hs)), 3),
               "p99_Hs_m": round(float(np.nanpercentile(Hs, 99)), 2),
               "mean_tau_Pa": round(float(np.nanmean(tau)), 4),
               "exceedance": {}}
        cells = ""
        for name, tc in TAU_C.items():
            ex = tau > tc
            hrs = float(ex.sum()) / yrs
            row["exceedance"][name] = {
                "hours_per_year": round(hrs, 1),
                "pct_of_time": round(float(ex.mean()) * 100, 2),
                "by_month": {int(m): round(float((ex & (months == m)).sum()) / yrs, 1)
                             for m in range(1, 13)},
            }
            cells += f"{hrs:>20,.0f} h/yr"
        log(f"  {d:>5.0f} m{'':4}{cells}")
        res["by_depth"][str(d)] = row

    # seasonality at the depth where the contrast is clearest
    d = 5.0
    Hs, Tp = young_verhagen(np, U, F, d)
    ub, tau = bed_shear(np, Hs, Tp, d)
    log(f"\n=== seasonality of resuspension at {d:.0f} m, hours per year ===")
    log(f"  {'month':>6}{'live bed':>12}{'dead bed':>12}{'ratio':>9}")
    names = "JanFebMarAprMayJunJulAugSepOctNovDec"
    for m in range(1, 13):
        sel = months == m
        lv = float(((tau > TAU_C["live bed (biofilm, fauna, eelgrass)"]) & sel).sum()) / yrs
        dd = float(((tau > TAU_C["dead bed (no biology)"]) & sel).sum()) / yrs
        bar = "#" * int(dd / 8)
        log(f"  {names[(m-1)*3:m*3]:>6}{lv:>12,.0f}{dd:>12,.0f}{dd/max(lv,0.1):>8.1f}x  {bar}")

    # which winds do the damage
    log("\n=== which wind directions resuspend (dead bed, 5 m) ===")
    ex = tau > TAU_C["dead bed (no biology)"]
    sect = {"N": (337.5, 22.5), "NE": (22.5, 67.5), "E": (67.5, 112.5), "SE": (112.5, 157.5),
            "S": (157.5, 202.5), "SW": (202.5, 247.5), "W": (247.5, 292.5), "NW": (292.5, 337.5)}
    tot = float(ex.sum())
    res["by_sector"] = {}
    for s, (a, b) in sect.items():
        m = (D >= a) & (D < b) if a < b else ((D >= a) | (D < b))
        n = float((ex & m).sum())
        share = n / tot * 100 if tot else 0
        res["by_sector"][s] = {"share_of_resuspension_pct": round(share, 1),
                               "hours_per_year": round(n / yrs, 1),
                               "fetch_km": round(float(np.nanmean(F[m])) / 1000, 1)}
        log(f"  {s:>3}  fetch {np.nanmean(F[m])/1000:>6.1f} km   "
            f"{n/yrs:>6,.0f} h/yr   {share:>5.1f}% of all resuspension  "
            + "#" * int(share / 2))

    write_json(os.path.join(DERIVED, "waves.json"), res)
    log("\nwrote data/derived/waves.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
