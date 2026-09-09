"""The two streams, in rates rather than in annual totals.

PROGRAMME.md section 2 says the rain stream is the large one and the foul stream is
the small, steady one. That is the whole architecture of the separated system, so it
should be arithmetic rather than an adjective - and the arithmetic has to be in
**rates**, because a year is exactly the averaging window that hides the thing.

What is measured here and what is stated:

  MEASURED   hourly rainfall over Copenhagen, ERA5 via Open-Meteo, 1995-2025,
             already fetched for the wave work. Every rain figure below is that
             record, not a design storm.
  MEASURED   the combined-sewered impervious area on Amager, from the municipal
             sewer-catchment layer (programme.amager_split).
  STATED     a runoff coefficient of 0.8 for paved surface, dry-weather sewage of
             130 l per person per day, and a morning peak factor of 2.0. These are
             ordinary design conventions, not observations from this project, and
             they are named so the arithmetic can be redone with other numbers.
  STATED     Stokes settling in still water at 10 degC for quartz-density grains.
             Real ponds are not still, so a settling velocity is an upper bound on
             what a pond of that area can capture, and the areas below are floors.

The foul side deliberately carries no population figure. Nobody in this project has
sourced one for the island, so the comparison is written as an *equivalence* instead:
how many people's morning peak one hectare of paved surface matches in an hour of
rain. That needs no census, and it is the number the architecture turns on.

Writes data/derived/streams.json.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, log, read_json
from programme import RAIN_MM_H, RUNOFF_C, amager_split, VESTAMAGER_HA

# Stated conventions. Both are design figures in ordinary use; neither is measured here.
DWF_L_PER_PERSON_DAY = 130.0
MORNING_PEAK_FACTOR = 2.0
# Stokes, 10 degC: dynamic viscosity of water, and the grain and water densities.
MU, RHO_S, RHO_W, G = 1.307e-3, 2650.0, 999.7, 9.81
GRAINS_UM = (100, 50, 20, 10, 5)


def hourly_rain():
    """Every hourly precipitation value in the fetched Copenhagen record, in mm."""
    W = os.path.join(RAW, "weather")
    out = []
    years = set()
    for f in sorted(os.listdir(W)):
        if not f.startswith("wind_"):
            continue
        h = read_json(os.path.join(W, f))["hourly"]
        for t, p in zip(h["time"], h.get("precipitation") or []):
            if p is None:
                continue
            out.append(float(p))
            years.add(t[:4])
    return out, len(years)


def pct(sorted_vals, q):
    if not sorted_vals:
        return float("nan")
    i = min(len(sorted_vals) - 1, max(0, int(round(q / 100 * (len(sorted_vals) - 1)))))
    return sorted_vals[i]


def settling_m_per_h(d_um):
    """Stokes terminal velocity, m/h. Quadratic in diameter, which is the point:
    the pond that catches sand is small and the pond that catches silt is not."""
    d = d_um * 1e-6
    return (RHO_S - RHO_W) * G * d * d / (18 * MU) * 3600


def main():
    rain, n_years = hourly_rain()
    wet = sorted(p for p in rain if p > 0)
    total = sum(rain)
    ha = amager_split()["Amager"]
    m2 = ha * 1e4

    def flow(mm_h):
        """m3/s off the impervious area at that hourly intensity."""
        return m2 * (mm_h / 1000.0) * RUNOFF_C / 3600.0

    # The foul side, per thousand people, in the same units.
    dwf_1000 = 1000 * DWF_L_PER_PERSON_DAY / 1000.0 / 86400.0        # m3/s
    peak_1000 = dwf_1000 * MORNING_PEAK_FACTOR

    hours_at = {}
    for thr in (1, 2, 5, 10, 15):
        hours_at[thr] = sum(1 for p in rain if p >= thr) / n_years

    design_q = flow(RAIN_MM_H)
    max_hour = max(rain)
    p999 = pct(wet, 99.9)
    annual_mm = total / n_years
    annual_m3 = m2 * (annual_mm / 1000.0) * RUNOFF_C

    ponds = []
    for d in GRAINS_UM:
        v = settling_m_per_h(d)                    # m/h
        a_peak = design_q * 3600 / v               # m2 to pass the design hour
        ponds.append({
            "grain_um": d, "settling_m_per_h": v,
            "area_ha_at_design_hour": a_peak / 1e4,
            "share_of_vestamager_pct": a_peak / 1e4 / VESTAMAGER_HA * 100,
            # The other bound: the same filter fed at a steady rate all year, which
            # is what storage upstream of it buys.
            "area_ha_if_fed_steadily": annual_m3 / (v * 8760) / 1e4,
        })

    out = {
        "_what": "The rain stream and the foul stream as rates, for Amager.",
        "rain_record": {
            "source": "ERA5 hourly via Open-Meteo, point 55.641N 12.414E",
            "years": n_years, "hours": len(rain),
            "mean_annual_mm": annual_mm,
            "wet_hours_per_year": len(wet) / n_years,
            "hours_per_year_at_or_above_mm": hours_at,
            "median_wet_hour_mm": pct(wet, 50),
            "p99_wet_hour_mm": pct(wet, 99),
            "p999_wet_hour_mm": p999,
            "max_hour_mm": max_hour,
        },
        "amager": {
            "combined_sewered_impervious_ha": ha,
            "runoff_coefficient_stated": RUNOFF_C,
            "annual_runoff_m3": annual_m3,
            "design_intensity_mm_h_stated": RAIN_MM_H,
            "flow_m3_s": {
                "median_wet_hour": flow(pct(wet, 50)),
                "design_hour": design_q,
                "p999_wet_hour": flow(p999),
                "wettest_hour_on_record": flow(max_hour),
            },
        },
        "foul_stated": {
            "dwf_l_per_person_day": DWF_L_PER_PERSON_DAY,
            "morning_peak_factor": MORNING_PEAK_FACTOR,
            "dwf_m3_s_per_1000_people": dwf_1000,
            "morning_peak_m3_s_per_1000_people": peak_1000,
            "people_matched_per_impervious_ha_in_design_hour":
                flow(RAIN_MM_H) / ha / peak_1000 * 1000,
            "people_matched_by_amager_in_design_hour": design_q / peak_1000 * 1000,
            "people_matched_by_amager_at_median_wet_hour":
                flow(pct(wet, 50)) / peak_1000 * 1000,
        },
        "ponds": ponds,
        "_stated": ("Runoff coefficient, dry-weather flow per person and the morning "
                    "peak factor are design conventions, not measurements from this "
                    "project. Settling is Stokes in still water at 10 degC, so the "
                    "pond areas are floors."),
    }
    p = os.path.join(DERIVED, "streams.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    log(f"  {n_years} years of hourly rain, {annual_mm:.0f} mm/yr, "
        f"wettest hour {max_hour:.1f} mm")
    log(f"  Amager {ha:,.0f} impervious ha -> {design_q:.1f} m3/s in a "
        f"{RAIN_MM_H:.0f} mm hour = the morning peak of "
        f"{design_q/peak_1000*1000:,.0f} people")
    for r in ponds:
        log(f"  {r['grain_um']:>4} um  v={r['settling_m_per_h']:7.2f} m/h  "
            f"peak-fed {r['area_ha_at_design_hour']:8.1f} ha  "
            f"steady-fed {r['area_ha_if_fed_steadily']:6.2f} ha")
    log(f"  wrote {p}")


if __name__ == "__main__":
    main()
