#!/usr/bin/env python3
"""Writes docs/hypodrafts/F3.md: a hypothesis draft, as generated text.

Every hypothesis ID is a checked reference, every chemical species a checked
species, and every number either read live or quoted from the page as committed
({q:…@@…}, a located quotation - see draftkit.py) because nothing in the repository stores it yet.

    python3 scripts/pages/hypodraft_f3.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draftkit

REL = "docs/hypodrafts/F3.md"
TEXT = r"""# {ref:F3|title}

*Draft. Nothing here has been run. One dataset it needs is not yet in the repo; the
fetch is specified below and was not executed.*

## The observable consequence, stated so it can fail

{ref:F3} says vegetation loss is self-reinforcing: cover goes, the bed resuspends, the water
darkens, and the darkness prevents return. Two consequences follow that can each be
wrong.

**`C1` (the feedback).** At a transect, a drop in vegetation **cover** is followed by a
rise in local light attenuation, more strongly than a rise in attenuation is followed
by a drop in cover. *Falsified* if the cross-lagged asymmetry is zero or reversed
under the nulls below — which is what "the water darkened first, for its own reasons"
looks like.

**`C2` (the block).** Transects that lost cover stay light-limited: light at the bed
remains below the eelgrass requirement. *Falsified* by transects where light at the
bed has been adequate for five consecutive growth seasons and cover has not returned.

`C1` and `C2` are separable. `C1` can hold and `C2` fail — the feedback is real and something
else now holds the system down.

## Avoiding the circularity, and what stays circular

The eelgrass **depth limit** is Denmark's clarity indicator; regressing it on
attenuation tests the indicator's own construction, not {ref:F3}. Three defences:

1. **The response is cover, not depth limit.** `Dækningsgrad (%)` per species enters
   no clarity indicator. The depth-limit columns are used only as a covariate to check
   `C1` is not driven by them.
2. **Drop light-limited transects from the depth-limit checks.** ODA carries
   `Maks dybde begrænset af` — *why the transect stopped*. Where the answer is
   substrate or end-of-transect, the depth limit is not a light measurement by
   construction. This field must be counted for fill before it is trusted (error class
   {q:(error class @@, unfilled}, unfilled field); if it is largely empty, drop the depth-limit strand entirely.
3. **Clarity is measured, not inferred.** `LyssvækkelsesKoefficient` per cast, and
   CMEMS `transp` grid pixels, neither derived from vegetation.

**What stays circular and cannot be removed:** the {q:removed:** the @@ requirement used} requirement used in `C2` is
inherited physiology — the same physiology from which DCE derive the Kd target. I am
not using their fitted target, but if the requirement is wrong the adequacy call moves
with it. Mitigation: report `C2` across {q:across @@ rather than} rather than at one threshold.

## Data, with counts verified here

| Source | Verified | Error class |
|---|---|---|
| `data/raw/oda/lys.csv.gz` | **{fig:da_lys_rows} rows, {fig:da_lys_stations} stations with coordinates** (streamed, this session) | **`4`** — apparent Kd depends on cast start depth: median {q:depth: median @@ for casts} for casts starting above {q:starting above @@ below (`docs/LIGHT.md`).} below (`docs/LIGHT.md`). Two answers in one column. |
| ODA vegetation, **not in repo**: `Emne_3_182` Ålegræs plante, `Emne_3_181` makroalge, `Emne_3_180` bundfauna | {q:`Emne_3_180` bundfauna | @@ for 1970–2026 (repo} for 1970–2026 (repo record, `data/manual/data_sources_2.json`, authenticated enumeration 2026-09-08 — **not re-verified by me**) | **`7`** if the indicator's fitted depth limit is used instead of the per-transect observed one. Use the ODA field. |
| `data/raw/oda/stations.csv` | {fig:da_st_rows} rows, {fig:da_st_stations} stations; **{fig:da_st_transect} carry a transect end coordinate**, spanning {fig:da_st_first} to {fig:da_st_last} | **`4`** — this register shares only {q:shares only @@ station ids} station ids with the lys / maaledybde / ctd criterion lists. Namespaces differ. |
| `data/raw/oda/maaledybde.csv.gz` | {q:`data/raw/oda/maaledybde.csv.gz` | @@ offered; carries} offered; carries `BundDybde_m`, `SigtTilBund` | **{q:`BundDybde_m`, `SigtTilBund` | **@@** — Secchi censored}** — Secchi censored at the bed in shallow water |
| `data/raw/geus/seabed_sediment_dk.gpkg` | read via sqlite3 by `scripts/substrate.py` | — |
| `data/raw/cmems/grid/transp__{inner,arkona}__YYYY.nc` | {q:__YYYY.nc` | @@ files} files, {q:| 87 files, @@ each, 24 GB} each, {q:MB each, @@ total | stream} total | stream one year at a time |

**Not usable here:** `docs/data/areas/val_kd.bin` and the coverage cube are indexed by
`DKCOAST` water body (error class 3, and water bodies are a model assumption, not a
unit). Clarity must come from per-cast lys or per-pixel CMEMS.

**The join is spatial, not by id.** Transect ↔ lys station-id overlap is **{q:overlap is **@@**. Distance from}**.
Distance from each of the {q:each of the @@ transects to the} transects to the nearest light-cast station: p10
{q:light-cast station: p10 @@, median 2.42}, median {q:p10 0.82 km, median @@, p90 7.51 km}, p90 {q:2.42 km, p90 @@ — 941 within} — {q:7.51 km — @@ within 2 km,} within {q:— 941 within @@ within 5 km.} within {q:2 km, 1,823 within @@. So a 2}. So a
{q:km. So a @@-radius join retains}-radius join retains about {q:retains about @@ of transects;} of transects; below that, CMEMS pixels.

## The fetch, specified, not run

`scripts/fetch_oda.py` needs three `TOPICS` entries (`{"emne": "Emne_3_182"}` etc.);
nothing else changes. Run with explicit `--from 1970-01-01 --to 2026-12-31 --years 5`
— omitting the period silently returns only the currently active network ({q:network (@@ stations), and}
stations), and the script now raises rather than allow it. Expected tens of MB gzipped,
three sequential runs, well inside the VM budget. **I did not run it.**

## The null, computed under the constraint actually imposed

Nothing is quoted. Two nulls, because two things could fake the result.

**`N1`, temporal.** For `C1`: circularly shift each transect's cover series against its own
clarity series by a random whole number of years, {q:number of years, @@, preserving within-series}, preserving within-series
autocorrelation and the transect's mean. {q:transect's mean. @@ draws; the} draws; the null distribution of the median
cross-lagged asymmetry is computed, not assumed to centre on zero.

**`N2`, spatial, contiguity- and depth-preserving.** Eelgrass sites are clustered and
depth-constrained, so a free permutation is the wrong null: on this project's own
stations a contiguity-constrained null already agrees at **ARI {q:agrees at **ARI @@, not}, not {q:not @@** (`docs/data/areas/partition_contiguous.json`).}**
(`docs/data/areas/partition_contiguous.json`). So relabel cover-loss status only
*within* strata of (substrate class from GEUS × {q:GEUS × @@ bottom-depth band),} bottom-depth band), and only across
transects connected on a k-NN graph whose edges crossing the OSM coastline are removed
— the same water graph the partition work uses, never the water-body polygons. Report
the observed statistic as **lift over this null**, and report the null's own level.

## Procedure

1. Fetch the three vegetation topics. Count fill of `Maks dybde begrænset af`,
   `Dækningsgrad`, and both depth-limit columns before using any of them.
2. Per transect-year, growth season (Mar–Sep): median cover; nearest-cast Kd
   **stratified by cast start depth**, never pooled; bottom depth from the transect's
   own `Vanddybde maks`; light at bed = exp(−Kd·z).
3. `C1`: per-transect cross-lagged regression, lag {q:regression, lag @@, median}, median across transects,
   against `N1` and `N2`.
4. `C2`: count transect-years with {q:transect-years with @@ consecutive adequate} consecutive adequate growth seasons and cover
   below {q:cover below @@; sensitivity}; sensitivity over {q:5%; sensitivity over @@. 5. Repeat}.
5. Repeat with CMEMS `transp` pixels as the clarity source, streamed by year.

## What a result would and would not license

A positive `C1` with lift over `N2` licenses: *at these transects, cover change leads
clarity change*. It does **not** license a national statement, does not identify the
resuspension mechanism (no sediment flux is measured), and cannot separate eelgrass
from drifting macroalgae shading unless the epiphyte and drift columns are filled.

`C2` is the {ref:L4} discrimination. Finding light-adequate, cover-absent transects shows the
block is **not** light — it does not say what the block is (seed supply, substrate
mobility, wasting disease {ref:T3|hypotheses} all remain). Finding none is consistent with {ref:F3}'s feedback
*and* with light simply never having recovered; `C1` is what separates those, which is
why both are needed.

Failure of both leaves {ref:F3} unscored at these transects, not refuted elsewhere.
"""


def main(argv):
    return 0 if draftkit.build(REL, TEXT) is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
