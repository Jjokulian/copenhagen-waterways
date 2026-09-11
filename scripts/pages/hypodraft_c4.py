#!/usr/bin/env python3
"""Writes docs/hypodrafts/C4.md: a hypothesis draft, as generated text.

Every hypothesis ID is a checked reference, every chemical species a checked
species, and every number either read live or quoted from the page as committed
({q:`@@/mbi_bottom_salinity_arkona_bornholm_P20250527.nc`}, see draftkit.py) because nothing in the repository stores it yet.

    python3 scripts/pages/hypodraft_c4.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draftkit

REL = "docs/hypodrafts/C4.md"
TEXT = r"""# {ref:C4|title}

## 1. The observable consequence

The falsifiable half of {ref:C4} is **ordered propagation**: a wind-forced inflow event at month
τ produces a bottom-salinity anomaly whose **peak lag increases monotonically along the
path** Belts/Øresund → Arkona → Bornholm → Gotland Deep ({q:Deep (@@). Pre-registered}). Pre-registered windows,
from a bolus crossing {q:bolus crossing @@ of bed} of bed at a few cm s⁻¹ with a stall in the Bornholm Basin:
strait bed {q:strait bed @@, Arkona}, Arkona {q:months, Arkona @@, Bornholm}, Bornholm {q:Arkona 0–3, Bornholm @@, Gotland salinity}, Gotland salinity {q:Gotland salinity @@, Gotland}, Gotland oxygen
{q:Gotland oxygen @@ decaying over} decaying over {q:decaying over @@. **The}. **The lag structure is asserted, not fitted**; the test is
whether the peaks fall in it, in order.

**Falsified if** the peak-lag vector is not monotone along the path, or the Gotland
salinity peak sits at lag ≤ {q:sits at lag ≤ @@, or the ordering}, or the ordering statistic (Kendall τ of peak lag against
along-path distance) lies inside §3's null.

Secondary: an event should raise `sal_bed` **without** raising `sal_surf`. If both rise
together it is barotropic exchange with no stratification consequence, and {ref:C4}'s
"strengthens stratification above them" clause fails at the Danish end.

## 2. The data (counts verified here)

| Source | What | Verified | Error class |
|---|---|---|---|
| `docs/data/areas/stations_series.{json,bin}` | monthly median/station | `sal_bed` {fig:da_sal_bed_n} / {fig:da_sal_bed_st} stations; `oxy_bed` {fig:da_oxy_bed_n} / {fig:da_oxy_bed_st}; `sal_surf` {fig:da_sal_surf_n}. Layout checked: last offset + {q:last offset + @@ = file size} = file size | **`3`** (median; "near the bed" is a bin of varying depth), **`6`** (no time-of-day) |
| same, values | — | `oxy_bed`: {q:values | — | `oxy_bed`: @@} < 0, 40 > {q:0, 40 > @@ — impossible. `sal_bed`:} — impossible. `sal_bed`: {q:`sal_bed`: @@ exact} exact zeros, {q:56 exact zeros, @@ > 36 ‰} > {q:zeros, 4 > @@ | **1**; **4**} | **`1`**; **`4`** where saturation-% rows sit in an mg/l column |
| `data/raw/oda/maaledybde.csv.gz` | `BundDybde_m` per visit | {fig:da_maal_rows} rows; {fig:da_maal_stations_bottom} stations carry a depth | **`5`** ({q:| **5** (@@ box stations have} box stations have none) |
| `.../mbi_bottom_salinity_arkona_bornholm_P20250527.nc` | `sob_ark`, `sob_bor` | {q:`sob_bor` | @@ daily,} daily, 1993-01-01→2024-12-31, {q:| 11,688 daily, 1993-@@1-01→2024-12-31, 0 missing. Title} missing. Title *"from Reanalysis"*, `BALTICSEA_MULTIYEAR_PHY_003_011` | **{q:`BALTICSEA_MULTIYEAR_PHY_003_011` | **@@ — model, not} — model, not datum** |
| `.../mbi_sto2tz_gotland_P20250527.nc` | `so`,`to`,`oxy` × {q:| `so`,`to`,`oxy` × @@ depths | 385} depths | {q:240 depths | @@ steps; `so`/`to` 383} steps; `so`/`to` {q:steps; `so`/`to` @@ valid profiles,} valid profiles, **`oxy` {q:valid profiles, **`oxy` @@}** (2005-{q:**`oxy` 226** (2005-@@→2024-12). Title *"from}→2024-{q:**`oxy` 226** (2005-11→2024-@@). Title *"from}). Title *"from Observations Reprocessing"*, `INSITU_BAL_..._013_032` | **`3`** (regridded monthly / {q:monthly / @@ from discrete} from discrete casts) |
| `data/raw/marine/wind_baltic_{n,c,s}.json` | hourly {q:json` | hourly @@ wind} wind | {q:m wind | @@ each, 1995-01-01→2025-12-31, 0} each, 1995-01-01→2025-12-31, {q:rows each, 1995-@@1-01→2025-12-31, 0 NaN;} NaN; points {q:0 NaN; points @@ | **7**; **6**} | **`7`**; **`6`** — *no point over the Kattegat or the Belts* |
| IOW/Mohrholz MBI list | the published inflow record | **Not held** — `DATA_QUEUE.md:49` queues it for {ref:A5}/{ref:C1}/{ref:C4} | — |

**Two defects found while verifying; do not inherit them.** (a) `_FillValue` is {q:them.** (a) `_FillValue` is @@e36 and a naive}e36 and a
naive read does not mask it — the 2012 annual mean at {q:mean at @@ then computes} then computes as {q:then computes as @@³⁴. (b) `docs/data/baltic/gotland.json`}³⁴.
(b) `docs/data/baltic/gotland.json` labels `oxy` **mg/l** and its `_provenance` calls the
product a reanalysis; the source netCDF declares units `0.001` (volume fraction ⇒ ml l⁻¹)
and *Observations Reprocessing*. The established {q:The established @@ for} for
2014–2018 reproduce exactly as **annual maxima at {q:**annual maxima at @@ in native units**} in native units** (×{q:native units** (×@@ for mg l⁻¹).} for
mg l⁻¹). So the Gotland file, not the Arkona/Bornholm file, is observation-derived: the
chain runs Danish stations → Gotland, and `sob_ark`/`sob_bor` are only a model check.

**Station panel (verified).** Box {q:(verified).** Box @@ with a} with a bottom
depth, {q:bottom depth, @@ with median} with median depth ≥ {q:median depth ≥ @@, **20** with}, **{q:with median depth ≥ @@}** with ≥ {q:with ≥ @@ monthly `sal_bed`} monthly `sal_bed` medians in
1993–2024 ({q:medians in 1993–2024 (@@; 4,822 station-months). Month-of-year}; {q:1993–2024 (120–381; @@ station-months). Month-of-year} station-months). Month-of-year counts Jan→Dec:
[{q:counts Jan→Dec: [@@] — a}] — a **{q:311] — a **@@:1 summer sampling bias**,}:1 summer sampling
bias**, and the reason a month-matched null is mandatory.

**Event index (built and run here).** Eastward u at {q:Eastward u at @@, daily mean,}, daily mean, {q:daily mean, @@-day running}-day
running sum as the westerly burst × the preceding {q:the preceding @@-day easterly}-day easterly deficit ({q:deficit (@@-day gap)}-day gap) as
preconditioning. Winter maxima rank **2002/03 first (peak window ending
2003-01-18)** and **2014/15 second (ending 2014-12-20)**. Without the preconditioning term
2014/15 ranks only seventh — preconditioning is not optional. Whether those winters are
the events they appear to be **cannot be confirmed in-repo**: the IOW record is not held
and I will not assert dates from memory.

## 3. The null, under the constraint I impose

I compare **one** strait composite against **one** Gotland series over 1995–2024. Under
that constraint the usual quoted null — "significant at n = {q:"significant at n = @@" — is wrong}" — is wrong by
an order of magnitude: Gotland deep salinity is a slow reservoir with effective sample size
of order ten. **Compute, do not quote.**

- **`N1`, primary: circular shift of the event index by whole years**, {q:years**, @@ non-zero} non-zero shifts
  over 1993–2024. Whole years preserve event seasonality, the summer sampling bias and
  every series' autocorrelation; only the alignment dies. **p floor {q:dies. **p floor @@ — state it,} — state
  it, never exceed it.**
- **`N2`: {q:- **N2: @@ Fourier phase-randomised} Fourier phase-randomised surrogates** of each response, preserving spectrum
  and marginal. Continuous p, but it Gaussianises inflow's pulse-like character. `N1` and `N2`
  bound the answer from two sides; take the more conservative.
- **The {q:- **The @@ are not} are not {q:are not @@ replicates** —} replicates** — they are {q:they are @@ positions in} positions in one hydrographic
  regime. The statistic is the median across positions of a per-station z-anomaly, the
  panel shifts as one, and the null is over **time only**: cross-station spread buys
  precision, not degrees of freedom. Not a water-body aggregation — positions are listed
  individually under a stated depth-and-box rule, and the sensitivity run is {q:run is @@ single-station fits}
  single-station fits reported as a *distribution of lags*, not {q:lags*, not @@ tests. If} tests. If only the
  composite shows the signal, the composite made it.

## 4. Procedure

1. Build the wind index above; winter maxima; top *k* onsets (k = {q:(k = @@ pre-declared, not} pre-declared,
   not chosen after seeing the answer).
2. Per station, subtract that station's **own** month-of-year median from `sal_bed`,
   `sal_surf`, `oxy_bed`; divide by its IQR. Never pool before de-seasoning.
3. Same for `sob_ark`/`sob_bor` (monthly means) and Gotland `so`/`oxy` at {q:Gotland `so`/`oxy` at @@, after masking}, after
   masking > {q:after masking > @@e30, in native}e30, in native units.
4. Superposed-epoch composite at lags {q:composite at lags @@…+24 months per}…+{q:lags −12…+@@ per site;} per site; record the peak lag.
5. Statistic: Kendall τ of peak lag against along-path distance (Belts {q:distance (Belts @@, Arkona}, Arkona {q:(Belts 0 km, Arkona @@, Bornholm ~230, Gotland},
   Bornholm {q:Arkona ~120, Bornholm @@, Gotland ~380).}, Gotland {q:Bornholm ~230, Gotland @@). 6. Recompute}).
6. Recompute τ under `N1` and `N2`.
7. Secondary: same on `sal_bed − sal_surf`; biphasic check on `oxy_bed`.

## 5. What a result would and would not license

**Would.** A clean falsification if the order breaks — cheap, and the statistic is robust
to every calibration error in §2. Otherwise weak corroboration, capped at p ≈ {q:capped at p ≈ @@. **Would not.** (a)}.

**Would not.** (a) The effective event count is **{q:effective event count is **@@}**, not {q:count is **2–3**, not @@; no effect size}; no effect size is
estimable, and the Gotland *oxygen* limb (2005-{q:*oxygen* limb (2005-@@→2024-12) holds at}→2024-{q:*oxygen* limb (2005-11→2024-@@) holds at}) holds at most one large event —
n ≈ {q:event — n ≈ @@, no p at}, no p at all, reportable only as narrative. (b) Nothing about {ref:C4}'s contribution to
**{ref:O1}** in Danish water: the straits are the valve for a basin whose deep water Denmark does
not produce, so a ventilated Gotland Deep does not transfer to Danish coastal deficit, and
this design cannot make it. (c) It does not test "entirely exogenous to Danish policy" —
exogeneity of the *wind* is assumed, and exogeneity of the *consequences* is a different
claim. (d) Salinity is computed from conductivity and temperature, saturation from oxygen,
temperature and salinity: `sal_bed`, `temp_bed`, `oxysat_bed` are **one** piece of
evidence, not three.

**Smallest improvement:** fetch the IOW/Mohrholz MBI statistics (`DATA_QUEUE.md:49`),
replacing a self-built proxy with the published chronology {ref:C4} names and turning the §2
coincidence at 2003-01-18 and 2014-12-20 from suggestive into checked.
"""


def main(argv):
    return 0 if draftkit.build(REL, TEXT) is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
