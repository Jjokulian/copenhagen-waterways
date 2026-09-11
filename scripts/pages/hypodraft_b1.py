#!/usr/bin/env python3
"""Writes docs/hypodrafts/B1.md: a hypothesis draft, as generated text.

Every hypothesis ID is a checked reference, every chemical species a checked
species, and every number either read live or quoted from the page as committed
({q:…@@…}, a located quotation - see draftkit.py) because nothing in the repository stores it yet.

    python3 scripts/pages/hypodraft_b1.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draftkit

REL = "docs/hypodrafts/B1.md"
TEXT = r"""# {ref:B1|title}

## 1. The observable consequence

{ref:B1} asks to be discriminated *"against per-outfall discharge volume."* That regressor is not
a datum — it is a model output (class **`7`**) driven by rainfall, which drives every rival
too, so regressing it on a rainfall-driven response tests rainfall. This draft takes a
**weaker, falsifiable half**: combined systems deliver *raw sewage* to the shore,
event-timed, on a schedule set by their own storage. Two consequences, neither using a
modelled volume.

**`C1` — the class contrast.** At bathing sites whose nearest rain-conditioned outfall is
**combined** (`OV/OS/OF/OK/Bypass`), the faecal-indicator response to antecedent rainfall is
**steeper** than where the nearest is **separate** stormwater (`SE/SF`), at equal distance,
region, month and rainfall. Faecal indicator is sewage-specific: the typetal put combined
overflow at Tot-N {q:overflow at Tot-N @@ against 2 for} against {q:overflow at Tot-N 1@@ mg/l against 2 for} for separate stormwater. *Falsified if the class × rain
interaction is inside §3's null, or negative.* {ref:B2} alone predicts a rain main effect in
**both** arms and a null interaction — so this is the {ref:B1}/{ref:B2} discrimination.

**`C2` — the storage kink.** A combined structure spills only once rain exceeds its storage.
`(vol_sb + vol_fbas)` over `Red areal` gives a **critical rainfall depth in mm** per
structure, from engineering attributes fixed in time. {ref:B1} predicts a **kink** at that
site-specific, *a-priori* depth, with no free breakpoint. *Falsified if the kink amplitude
at each site's own threshold sits inside the null from permuting thresholds.*

**How the shared-rainfall confound breaks.** Rainfall enters both arms of `C1` identically
and cancels in the contrast. In `C2` the *location* of the threshold is the signal, and it
varies for reasons the weather does not know: runoff, riverine POC, buoyancy, resuspension
and bather density are all smooth in rainfall and none carries a basin volume. No modelled
overflow volume enters either statistic.

## 2. The data (counts verified here)

| Source | What | Verified | Error class |
|---|---|---|---|
| EEA **WISE_BWD** `[latest].[timeseries_MonitoringResult]`, via `discodata.eea.europa.eu/sql` | per-sample E. coli + enterococci, dated | **{q:enterococci, dated | **@@ DK samples, 2008–2024, 1,437} DK samples, 2008–2024, {q:samples, 2008–2024, @@ site ids**,} site ids**, {q:1,437 site ids**, @@/yr; 0 nulls;}/yr; {q:**172,440 DK samples, 2@@08–2024, 1,437 site ids**,} nulls; **{q:~9,000/yr; 0 nulls; **@@ at limit of detection**;} at limit of detection**; {q:of detection**; @@ flagged `missingValue`} flagged `missingValue` yet carrying a value | **`2`** LOD censoring; **`1`** the {q:LOD censoring; **1** the @@; **6** no clock}; **`6`** no clock time |
| same, `[timeseries_SeasonalPeriod]` | dated episode log | **{q:log | **@@ `shortTermPollution` periods} `shortTermPollution` periods (2011–2024)**, {q:`shortTermPollution` periods (2011–2024)**, @@ `bathingProhibition` (2017–), 76} `bathingProhibition` (2017–), {q:755 `bathingProhibition` (2017–), @@ `abnormalSituation`, 76 `cyanobacteriaBloom`} `abnormalSituation`, {q:(2017–), 76 `abnormalSituation`, @@ `cyanobacteriaBloom` | **5**} `cyanobacteriaBloom` | **`5`** — declaration is discretionary |
| same, sample flags | — | **{q:| — | **@@ `shortTermPollutionSample`**, 1,205 `replacementSample`, 22,912} `shortTermPollutionSample`**, {q:| **1,272 `shortTermPollutionSample`**, @@ `replacementSample`, 22,912 `preSeasonSample`} `replacementSample`, {q:`shortTermPollutionSample`**, 1,205 `replacementSample`, @@ `preSeasonSample` | **3**} `preSeasonSample` | **`3`** — the Directive permits discarding the first and substituting the second, so the compliance statistic drops precisely the overflow samples; the raw table keeps them |
| `data/raw/national/badevand.geojson` | {fig:db_sites} sites, lat/lon, `DKBW…` | joins to WISE ids exactly; {q:WISE ids exactly; @@ > 1,026 because} > {fig:db_sites} because delisted sites persist | **`5`** |
| `data/raw/spildevand/combined_overflow.geojson` | {fig:db_cso} CSOs; `Red areal`, annual volume, `Antal overløb` | `Antal overløb` **null for {fig:db_cso_spills_null} of {fig:db_cso} ({calc@K-SUBSET-SHARE:db_cso_spills_null / db_cso * 100|.1f}%)**; volume null {fig:db_cso_vol_null}, zero {fig:db_cso_vol_zero} | **`5`**; volume itself **`7`**, unused here |
| `data/raw/national/punkt_rbu_udl.geojson` | {fig:db_rbu} RBU points; `vol_sb`, `vol_fbas` | `vol_sb` non-null {fig:db_vol_sb} ({fig:db_vol_sb_zero} zeros); `vol_fbas` {fig:db_vol_fbas} ({fig:db_vol_fbas_zero} zeros) | **`5`** |
| the two together | joinable? | **{fig:db_join_matched} of {fig:db_join_names} CSO names** match `pkt_navn`; the register disagrees with itself — `OV` {fig:db_cso_ov} vs {fig:db_rbu_ov}, `OF` {fig:db_cso_of} vs {fig:db_rbu_of} — and `UR`, `ikke oplyst` are in no codelist | **{q:codelist | **@@ — schema/vintage conflation**} — schema/vintage conflation** |
| **derived here** | critical rainfall depth | **{fig:db_depth_n} CSOs** with a unique name-join, positive basin volume and positive reduced area; p10 **{fig:db_depth_p10} mm**, median **{fig:db_depth_median} mm**, p90 **{fig:db_depth_p90} mm**, max {fig:db_depth_max} mm — the tail is a unit error, trim above p95 | **`1`** in the tail |
| **derived here** | site → nearest outfall | **{fig:db_near_combined} sites combined-nearest, {fig:db_near_separate} separate-nearest**; median distance {fig:db_near_median_km} km; **{fig:db_near_1km} within {q:0.87 km; **540 within @@**, 741 within 2}**, {fig:db_near_2km} within {q:km**, 741 within @@ | — |} | — |
| **rainfall — the gap** | gauge series | DMI metObs `precip_past1h`/`precip_past10min`, the right source, needs **one free API key**. Key-free fallback NOAA GHCN-Daily: {q:GHCN-Daily: @@ Danish} Danish stations carry PRCP, **only three run past 2020** — too sparse. `data/raw/weather/*` and `marine/wind_*` are **Open-Meteo reanalysis**, not gauges | **`7`** if reanalysis is substituted |

**Off-repo sources, and whether each is a production path separate from modelled volume.**
*Measured* overflow at national scale does not exist. What does:

- **WISE_BWD** (above), CC-BY EEA, {q:(above), CC-BY EEA, @@ streamed — **fully} streamed — **fully separate**: laboratory counts
  and municipal declarations, no hydraulic model in the chain.
- **Vesthimmerlands Forsyning**, `/spildevand/overloebsdata` — **measured**: {q:**measured**: @@ sensor-instrumented}
  sensor-instrumented structures, monthly counts and volumes, 2025 plus archive, HTML
  tables, no API. Inland and tiny, but a real knowledge-level-{q:knowledge-level-@@ set.} set.
- **Copenhagen Badevandsudsigten**, `kbh.badevand.dk` (DHI/HOFOR) — ingests **measured**
  overflow on a {q:overflow on a @@-minute cycle; host}-minute cycle; host did not resolve from here, archive not known public.
  **The highest-value fetch for {ref:B1}.**
- **PULS API**, `puls-api.miljoeportal.dk` — live, undocumented. Same production path, but
  would carry the per-structure *knowledge level* (TA DP02 {q:level* (TA DP02 @@) that names}) that names an instrumented
  subset.
- **MST/EnviDan/AAU (2020), *Standardiseret bestemmelse af overløb*** — national overflow
  uncertainty **{q:overflow uncertainty **@@**, reducible to}**, reducible to {q:**~110%**, reducible to @@ for 20–40 M} for {q:to ~50% for @@ M DKK/yr; the} M DKK/yr; the citation for class 7,
  not data. **Waterbase-UWWTD** is agglomeration-annual, class 3 and {q:class 3 and @@. **MiljøGIS `vp3basis2019`}. **MiljøGIS
  `vp3basis2019` WFS now {q:WFS now @@s** — the}s** — the repo's own fetch path is dead.

## 3. The null, under the constraint I impose

**Computed, not quoted.** The nominal null for {q:null for @@ is wrong} is wrong by two orders of
magnitude: sampling is day-clustered — over 2011–2024, **{q:— over 2011–2024, **@@ fall on 1,425 distinct} fall on {q:fall on @@ distinct dates**,}
distinct dates**, {q:distinct dates**, @@ per date,} per date, {q:per date, @@ sampling days} sampling days a season. Weather is common within a day
and correlated across the country, so the independent unit is the **site-day cluster**, and
even those {q:even those @@ are not} are not independent draws on weather.

- **`N1` (primary, `C1`): permute the class label** across sites within strata of
  (distance decile × region × outfall count within {q:outfall count within @@), 10,000 draws}), {q:within 2 km), @@ draws — destroys} draws — destroys the
  combined/separate contrast, preserves rainfall, geography, season and site baselines.
- **`N2` (`C1`): circular shift of the daily rainfall field by whole years**, {q:years**, @@ non-zero} non-zero
  shifts over 2008–2024, preserving seasonality, day-clustering and autocorrelation.
  **p floor {q:autocorrelation. **p floor @@ — state it,} — state it, never exceed it.** Report the more conservative of `N1`
  and `N2`.
- **`N3` (`C2`): permute the predicted threshold** across structures within a spill-volume
  stratum: keeps the kink, destroys the link to a site's own storage.
- **Left-censoring is not small**: {q:not small**: @@ values sit} values sit at the LOD. Fit a
  censored-normal on log10 counts; a substitution rule invents the effect.
- **Sites are positions, not replicates**, never aggregated into water bodies: the unit is
  outfall-to-site distance, which is what the mechanism has.

## 4. Procedure

1. Stream the DK subset of `timeseries_MonitoringResult` and `timeseries_SeasonalPeriod`
   from DISCODATA; join to `badevand.geojson` on `DKBW…`.
2. Per site: nearest combined and nearest separate RBU point, and counts within {q:counts within @@ and} and
   {q:@@. Keep the geometry;}. Keep the geometry; aggregate nothing.
3. Rainfall: obtain a DMI key, then antecedent depth over {q:depth over @@ before each} before each sample
   at the nearest gauge. Until then the design is stated, not run.
4. **`C1`:** censored regression of log10 E. coli on rain × class, site fixed effects, month,
   distance, year. Report the interaction. Repeat on enterococci — a second organism, not a
   second dataset.
5. **`C2`:** for the {fig:db_depth_n} threshold-bearing CSOs and their nearest sites, test the jump at
   each site's own predicted depth, standardised and summed across sites.
6. **Anchor:** samples inside a declared `shortTermPollution` period against matched samples
   at the same site and month outside one — the arm that uses no rain model at all.
7. Null under `N1`, `N2`, `N3`.

## 5. What a result would and would not license

**Would.** That combined systems deliver sewage-specific contamination to the shore,
event-timed, near their outfalls, across {q:outfalls, across @@ seasons and} seasons and {q:seasons and @@ — and} — and via `C2` that the
timing is set by storage, not weather alone. It separates {ref:B1} from {ref:B2} on a signature rather
than a shared driver, and falsification is equally available and cheap.

**Would not.** (a) **Nothing about oxygen.** This is {ref:B1}'s delivery limb ({ref:O9}, weakly {ref:O2}),
not {ref:O1}; faecal indicators are not COD, so the oxygen claim stays unscored. (b) No load, no
volume, no attribution — there is no denominator, so any "share of" is out of reach by
construction. (c) The window is **bathing season only**, set by human use and so circular
per `NITROGEN.md`. (d) Sampling is **selected against the exposure** — crews avoid storms,
and a replacement sample supersedes a short-term-pollution one — which attenuates toward
zero, so a positive result survives it but a null does **not** license "no effect".
(e) E. coli and enterococci are two counts from one sample and one visit: one piece of
evidence, not two.

**Smallest improvement:** the Copenhagen Badevandsudsigten measured-overflow archive, or
the per-structure knowledge level from the PULS API. Either converts a structural proxy
into an instrumented subset and moves the exposure out of error class 7.
"""


def main(argv):
    return 0 if draftkit.build(REL, TEXT) is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
