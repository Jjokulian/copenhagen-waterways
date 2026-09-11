#!/usr/bin/env python3
"""Writes docs/hypodrafts/C6.md: a hypothesis draft, as generated text.

Every hypothesis ID is a checked reference, every chemical species a checked
species, and every number either read live or quoted from the page as committed
({q:…@@…}, a located quotation - see draftkit.py) because nothing in the repository stores it yet.

    python3 scripts/pages/hypodraft_c6.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draftkit

REL = "docs/hypodrafts/C6.md"
TEXT = r"""# {ref:C6|title}

Draft only. Nothing here has been run; the counts were verified by reading the files.

## What is not in dispute

Weiss (1970) makes the solubility ceiling deterministic in temperature and salinity.
That half of {ref:C6} needs no test. The testable residue is the Q10 half: **at constant
organic supply, does warmer bottom water sit further below its own ceiling?**

## Observable consequence, stated to be falsified

Define the near-bed apparent deficit, per station-month:

> `D = C_sat(T_bed, S_bed) − O_bed` (mg/l), `C_sat` = Weiss 1970, mL/L × {q:Weiss 1970, mL/L × @@. `D` is solubility-neutral}.

`D` is solubility-neutral by construction. If temperature acted on near-bed oxygen
*only* through the ceiling, `D` would be independent of `T`.

**Falsifiable claim:** *within a fixed station and a fixed calendar month, across years,
`D` does not rise with that year's near-bed temperature.* A pooled within-cell slope
β̂ ≤ {q:within-cell slope β̂ ≤ @@, or one indistinguishable}, or one indistinguishable from {q:indistinguishable from @@ under the} under the permutation null below, falsifies {ref:C6}'s
non-thermodynamic content at the resolution this archive has.

**Subsidiary claim about the regulated statistic:** *the `< 4 mg/l` flag ranks stations
by consumption, not by ceiling height.* Falsified if station-level flag rates under
`O < 4` and under an equal-rate deficit flag rank stations differently.

## Data, with verified counts

`docs/data/areas/stations_series.{json,bin}` — {fig:da_series_months} station-months (sum over the nine
variables, confirmed), {fig:da_series_stations} stations, months {q:stations, months @@ (Jan} (Jan 1980 – Sep 2026). Near-bed: `oxy_bed` {fig:da_oxy_bed_n} · `temp_bed` {fig:da_temp_bed_n} · `sal_bed` {fig:da_sal_bed_n} ·
`oxysat_bed` {fig:da_oxysat_bed_n}.

- Triple join `oxy_bed ∩ temp_bed ∩ sal_bed`: **{q:sal_bed`: **@@**; after}**; after a plausibility filter
  ({q:a plausibility filter (@@ ≤ O ≤} ≤ O ≤ {q:≤ O ≤ @@ ≤ T ≤} ≤ T ≤ {q:≤ T ≤ @@ ≤ S ≤} ≤ S ≤ {q:0 ≤ S ≤ @@): **76,305 rows over}): **{q:S ≤ 40): **@@ over 1,314 stations**, 44} over {q:**76,305 rows over @@**, 44 dropped.}**, {q:over 1,314 stations**, @@ dropped. - Cells} dropped.
- Cells = (station × calendar month). With ≥ {q:With ≥ @@ distinct years:} distinct years: **{q:distinct years: **@@ cells, 63,262 rows,} cells, {q:years: **3,282 cells, @@ rows, 395 stations**.}
  rows, {q:cells, 63,262 rows, @@**. With ≥}**. With ≥ {q:stations**. With ≥ @@. With ≥}. With ≥ {q:641. With ≥ @@. - Within-cell}.
- Within-cell SD of `temp_bed`: median **{q:`temp_bed`: median **@@** (q10 1.03,}** (q10 {q:median **1.55 °C** (q10 @@, q90 2.26) —}, q90 {q:°C** (q10 1.03, q90 @@) — real leverage.}) — real leverage.
- Reproduced prior work on this join: `O < 4 mg/l` monthly rate {q:monthly rate @@ (Feb) →} (Feb) → {q:(Feb) → @@ (Sep), **23.6-fold**;}
  (Sep), **{q:→ 0.2119 (Sep), **@@**; recomputed `< 30}**; recomputed `< 30 %` saturation **{q:%` saturation **@@**; median `temp_bed`}**; median `temp_bed`
  {q:`temp_bed` @@ (Feb)} (Feb) / {q:°C (Feb) / @@ (Aug). - Reference} (Aug).
- Reference for the subsidiary claim: an *equal-rate* deficit flag `D > 5.13 mg/l`
  (same {q:mg/l` (same @@ overall rate)} overall rate) is **{q:rate) is **@@** seasonally, and}** seasonally, and {q:**13.9-fold** seasonally, and @@ of `O <} of `O < 4`
  station-months also exceed it. The two statistics differ at the margin, not in bulk.

**Error classes present.** ({q:classes present.** (@@) value errors}) value errors — `oxy_bed` spans {q:`oxy_bed` spans @@, `oxysat_bed`},
`oxysat_bed` to {q:`oxysat_bed` to @@, `temp_surf`}, `temp_surf` to {q:`temp_surf` to @@; the}; the filter removes {q:filter removes @@ of the} of the join.
({q:spans −9.93 to @@81.6 mg/l, `oxysat_bed`}) quantisation — raw `Temperatur` is written with at most one decimal on {fig:da_tdec_one} of {fig:da_tdec_rows} rows over the whole extract ({calc@K-SUBSET-SHARE:da_tdec_one / da_tdec_rows * 100|.0f}%; an earlier sample put it at {q:decimal on @@ sampled rows;}); where it is,
{q:141,731 sampled rows; @@ → ±0.015 mg/l} → {q:±0.05 °C → @@ in `C_sat` (|dC_sat/dT|} in `C_sat` (|dC_sat/dT| = {q:`C_sat` (|dC_sat/dT| = @@ at 4 °C,} at {q:= 0.29 at @@ at 16 °C),} at {q:4 °C, 0.18 at @@), negligible against a}), negligible
against a deficit that reaches {q:deficit that reaches @@. (3) aggregation}. ({q:reaches 14.6 mg/l. (@@) aggregation — these}) aggregation — these are monthly *medians*,
and "near the bed" is itself a within-cast selection, so the T, S and O medians of one
station-month need not come from the same cast. ({q:same cast. (@@) unfilled —}) unfilled — {q:unfilled — @@ `oxy_bed` cells} `oxy_bed` cells
carry no saturation; `SondeNavn` is `999 - Ukendt` on the raw rows inspected. ({q:rows inspected. (@@) absent dimension}) absent
dimension — see below. ({q:see below. (@@) is avoided:}) is avoided: the unit is a station, never a water body.

**Class 6, stated not ignored.** The raw header (`data/raw/oda/ctd.csv.gz`, {fig:da_ctd_columns} columns)
has `Dato` as `19701013` — a date, no hour, and no other time field. Oxygen has a diel
cycle, and sampling hour plausibly covaries with season (short winter days compress
sampling toward midday). The confound has the *same sign* as the hypothesis. It is not
correctable from this archive and it caps what any result licenses.

## Circularity, handled

Archived `oxysat_bed` is computed from O, T and S; using it as the outcome against T as
the regressor would be circular, so **it is never the outcome here**. It is used once as a
check: recomputed Weiss saturation matches the archived value to a median {q:a median @@ percentage points,}
percentage points, r = {q:percentage points, r = @@, n =}, n = {q:0.9948, n = @@ — so the} — so the archive's saturation rests on
essentially the same solubility function and `D` adds no second, rival model.

`D` contains T through `C_sat` deliberately — that is the *removal* of the solubility
channel, not circularity, because Weiss is exact and external to this dataset. The
residual risk is errors-in-variables: an error ε in T enters `D` with slope {q:`D` with slope @@ to −0.29 and} to
{q:@@ and the regressor} and the regressor with slope +{q:regressor with slope +@@, so it induces}, so it induces a **negative** spurious slope. The
test is therefore conservative in the direction that matters; with σ_ε ≈ {q:with σ_ε ≈ @@ against σ_T =} against
σ_T = {q:against σ_T = @@ the attenuation is} the attenuation is {q:the attenuation is @@. Salinity is}. Salinity is computed from conductivity and
temperature, so it carries T error too, but dC_sat/dS = {q:dC_sat/dS = @@ per psu} per psu — a {q:psu — a @@ error propagates to}
error propagates to under {q:propagates to under @@. Negligible. ##}. Negligible.

## Procedure

1. Read the three near-bed arrays at the offsets in the `.json`; key on
   `station_index × 1000 + month_index`; filter as above → {q:filter as above → @@. 2. Compute `C_sat`}.
2. Compute `C_sat` (Weiss) and `D`. Keep cells with ≥ {q:cells with ≥ @@ (3,282 cells). 3.} ({q:8 years (@@ cells). 3. Centre} cells).
3. Centre T and D on their cell means. Estimate β̂ = Σ(t̃·d̃)/Σ(t̃²) — the station ×
   calendar-month fixed-effects slope of deficit on temperature, mg/l per °C.
4. **Null, computed under the constraint actually imposed.** {q:actually imposed.** @@ permutations: within} permutations: within
   each cell independently, permute D across years with T held in place. This preserves
   cell means, the seasonal cycle, every station effect and both marginals, destroying
   only the within-cell T–D pairing. Two-sided p = fraction with |β*| ≥ |β̂|. Report the
   permutation SD *and* the OLS SE and their ratio: near-bed deficits at neighbouring
   stations in the same month are the same water mass sampled twice, so the textbook SE
   assumes an independence the data does not have, by an unknown factor. That ratio is
   the size of the error a quoted null would have made.
5. Repeat with D linearly detrended on year within each cell, so that forty years of
   warming meeting forty years of changing nutrient load cannot manufacture β̂. Report
   both, and the {q:and the @@-year variants.}-year variants.
6. Subsidiary: per station, flag rate under `O < 4` and under `D > 5.13`; Spearman ρ
   over {q:Spearman ρ over @@; count stations}; count stations flagged by one and not the other. Null: permute
   calendar-month labels within station.
7. Confirmatory version, if step 4 clears: rebuild `D` from *same-cast* T, S, O by
   streaming `ctd.csv.gz` ({q:`ctd.csv.gz` (@@ gz), removing} gz), removing the class-{q:the class-@@ pairing gap.} pairing gap.

## What a result would and would not license

**Would.** A positive β̂ surviving the permutation null and the detrending licenses:
near-bed temperature moves near-bed oxygen beyond solubility, within station and within
calendar month, in this archive — which is exactly the gap {ref:C6} names, since the standing
models carry surface temperature only.

**Would not.** It does not identify respiration: warm within-month anomalies co-occur
with weak wind and stronger stratification, so the deficit may be failed ventilation
rather than Q10. It cannot calibrate Q10 at all — converting a respiration *rate* to a
standing deficit needs a ventilation timescale this archive does not record (class 6).
It says nothing about water bodies. And β̂ ≈ {q:And β̂ ≈ @@ would **not** refute} would **not** refute {ref:C6} in nature; it
would refute it at the resolution of monthly medians taken at an unrecorded hour.
"""


def main(argv):
    return 0 if draftkit.build(REL, TEXT) is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
