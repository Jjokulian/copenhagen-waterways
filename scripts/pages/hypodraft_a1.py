#!/usr/bin/env python3
"""Writes docs/hypodrafts/A1.md: a hypothesis draft, as generated text.

Every hypothesis ID is a checked reference, every chemical species a checked
species, and every number either read live or quoted from the page as committed
({q:…@@…}, a located quotation - see draftkit.py) because nothing in the repository stores it yet.

    python3 scripts/pages/hypodraft_a1.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draftkit

REL = "docs/hypodrafts/A1.md"
TEXT = r"""# {ref:A1|title}

**Draft, not a result. Nothing here has been run.**

{ref:A1} as written ("deficit scales with current-year N load") cannot be tested today: it
needs catchment N flux per water body per month, and this project has none — see
*Still blocked*. What **can** be tested is its precondition. The {q:its precondition. The @@ is a residual,} is a residual,
and a residual cannot be validated against itself ([`../RESIDUAL.md`](../RESIDUAL.md),
which states the growth test at line {q:test at line @@). This drafts}). This drafts that growth test against the
archive, which turns out to be obtainable.

## A primary-source finding, obtained on the way

The unverified claim — that DK-QNP, covering the ungauged half of Denmark, takes the
national field nitrogen surplus as an input — **is correct, and DCE state it.** From
*Vandløb 2018 NOVANA* (Thodsen et al. 2019, DCE Videnskabelig rapport nr. 353),
methods chapter:

> "En vigtig modelvariabel i DK-QNP modellen til beregning af tilførsel af total
> diffus kvælstof er det årligt beregnede kvælstofoverskud på 'mark-niveau'."

The field balance is computed per Blicher-Mathiesen et al. (2015). Chapter 6 of the
same report then offers as a *result*:

> "Der er således – for perioden som helhed - en meget stærk, signifikant lineær
> relation mellem det nationale markoverskud og den samlede, normaliserede
> kvælstoftransport fra diffuse kilder (Figur {read:SR353:6.7|Figur 6.7}, D)."

A farming statistic is an input to the model generating the diffuse load over {q:load over @@ of the} of
the country, and its correlation with that load is then reported as evidence — **error
class 7, model-as-datum**, exactly. This does not show the attribution is wrong. It
shows Figur {read:SR353:6.7|Figur 6.7} D cannot be what shows it is right.

## Observable consequence, stated so it can be falsified

DCE recompute the whole 1990-present series under the current method every year ("fra
1990, således at den nyeste version af modellen anvendes", SR353), so a fixed year *y*
exists in many published vintages. When a version change moves a part **P**
out of the leftover, and the account is a partition:

> **R_new(y) = R_old(y) − P** and **T_new(y) = T_old(y)**

**Falsified if:** R does not move; R moves by materially less than P; or the **total**
T moves instead. Any of the three means the published share is not a share of
anything.

## Data, named, with counts I verified

| Source | Verified here | Error class |
|---|---|---|
| DCE `Vandløb <year>. NOVANA`, `https://dce2.au.dk/pub/SR<n>.pdf` | SR353 = Vandløb 2018, {q:Vandløb 2018, @@, **text-extractable**:}, **text-extractable**: `pdftotext -layout` yields {q:-layout` yields @@ chars; `pdfinfo`} chars; `pdfinfo` shows Distiller {q:`pdfinfo` shows Distiller @@, 2019-12-02. SR527}, 2019-12-02. SR527 (Vandløb 2021) and SR532 share the URL shape | {q:-layout` yields 17@@,210 chars; `pdfinfo`}, published to {q:2, published to @@ | | SR353} |
| SR353 figures | 2018 land→coast ≈ **{read:SR353:50.000|Tilførslen fra land til kystvandene er for 2018 beregnet til hhv. ca. 50.000 tons kvælstof} t N/yr**, point sources ≈ **{read:SR353:5.200|på ca. 5.200 tons i 2018} t N/yr**; **{read:SR353:209|Beregningerne dette år er baseret på målinger fra 209 kystnære målestationer}** coastal stream stations plus a model for the rest; **{read:SR353:240|anvendes 240 målestationer}** discharge gauges in the 1990-2018 run; field surplus **{read:SR353:186.000|varieret mellem 186.000 – 240.000 tons N}–{read:SR353:240.000|varieret mellem 186.000 – 240.000 tons N} t N** over five agrohydrological years | {q:agrohydrological years | @@, then}, then {q:`data/raw/national/hovedoplande.geojson` | **@@4** features, including} |
| `data/raw/national/hovedoplande.geojson` | **{fig:da_hov_features}** features, including `DK` *"Int vidå-kruså"* beside `DK4.1` *"Vidå-kruså"* — a transboundary catchment named as such | {q:as such | @@, no foreign-inflow}, no foreign-inflow term |
| `docs/data/areas/stations_series.json` | **{fig:da_series_months}** station-months (summed over {fig:da_series_vars} variables, {q:over 9 variables, @@ … 84,668), 1,415} … {q:9 variables, 60,460 … @@), 1,415 stations, 564}), {fig:da_series_stations} stations, {fig:da_series_nmonths} months from 1980. **No nutrients** | {q:**No nutrients** | @@ | | `data/raw/oda/ctd.csv.gz`} |
| `data/raw/oda/ctd.csv.gz` | {fig:da_ctd_bytes} bytes, {fig:da_ctd_columns} columns; first {q:columns; first @@ compressed =} compressed = **{q:MB compressed = **@@** rows ⇒ ~1.35×10⁵}** rows ⇒ {q:rows ⇒ @@⁵ rows per}⁵ rows per compressed MB ⇒ {q:compressed MB ⇒ @@⁷ total, consistent}⁷ total, consistent with the stated {q:with the stated @@ M |} M | {q:53.7 M | @@ | Only the} |

Only the first two rows are used by the test. The last two are what {ref:A1} would otherwise
be tested on; neither carries nitrogen.

## The null under the constraint I actually impose

The constraint is **arithmetic identity across two publications**, not sampling: there
is no estimator distribution, and n is the number of version changes, which is small.
The only noise under the null is publication rounding, which I compute rather than
quote. Totals appear to {q:appear to @@ significant figures,} significant figures, so half-widths are h = {q:are h = @@ on a 50,000} on a
{q:t on a @@ total and h} total and h = {q:and h = @@ on a 5,200} on a {q:50 t on a @@ point-source figure. Four published} point-source figure. Four published quantities
enter each comparison (T_old, T_new, P_old, P_new):

- worst-case bound: {q:worst-case bound: @@ =} = **{q:+ 50 = **@@** - independent-uniform s.d.:}**
- independent-uniform s.d.: √({q:- independent-uniform s.d.: √(@@·(500/√3)² + 2·(50/√3)²) =}·({q:- independent-uniform s.d.: √(2·(@@/√3)² + 2·(50/√3)²) =}/√{q:- independent-uniform s.d.: √(2·(500/√@@)² + 2·(50/√3)²) =})² + {q:- independent-uniform s.d.: √(@@·(500/√3)² + 2·(50/√3)²) =}·({q:- independent-uniform s.d.: √(2·(@@0/√3)² + 2·(50/√3)²) =}/√{q:s.d.: √(2·(500/√3)² + 2·(50/√@@)²) = **410 t})²) = **{q:+ 2·(50/√3)²) = **@@** I impose the}**

I impose the worst case. **Reject only when |ΔR + P| > {q:|ΔR + P| > @@** — which is}** — which is also the
design's honest limit: **no power against reallocations under {q:against reallocations under @@**, a fifth}**, a fifth of
the whole point-source term. More power needs the underlying tables at full precision,
not the report text.

Use the **actual** (aktuel) series, never the climate-normalised one: normalisation is
a model applied to the total (SR353 records it running {read:SR353:1%|var 1% højere end de aktuelle tilførsler} above actual over 1990-2017),
so it moves T by itself and would contaminate the third failure mode.

## Procedure

1. Fetch the `Vandløb <year> NOVANA` vintages 2013-2024 (SR numbers looked up per
   year; SR353 and SR527 confirmed) — {q:SR527 confirmed) — @@ PDFs, ~8 MB} PDFs, {q:PDFs, @@ each, streamed} each, streamed to disk, then
   `pdftotext -layout` locally.
2. From each, for every *y* ≥ 1990: total land→coast TN, point sources, diffuse
   remainder — actual, not normalised.
3. Read each vintage's methods chapter for declared changes. SR353 declares two
   unprompted: a **new** regional bias correction of DK-QNP monthly loads
   ("Bias-korrektionen … er ny i forhold til de foregående år"), and a correction of TN
   and TP measured 2016–Apr 2017 by a wrong analytical method, plus a smaller one for
   2007-2014. Each is a candidate *P* with a stated year.
4. For each, form ΔR and ΔT across the vintage boundary and compare to the {q:compare to the @@ bound. ## What}
   bound.

## What a result would and would not license

**Would.** Three or more declared changes with ΔR = −P inside the bound and ΔT ≈ {q:and ΔT ≈ @@ licenses one narrow}
licenses one narrow statement: *the account behaves as a partition under revision.* A
single failure of the third kind — T moving with R — licenses the opposite and
stronger one: the share is circular.

**Would not.** Nothing here licenses a claim about the sea: no mechanism, no N-load
coefficient, no oxygen. Nor whether "Denmark" is a closed box — the account carries no
foreign-inflow term though the national catchment layer names the transboundary unit
outright. A partition that balances is still a partition of a quantity whose boundary
was assumed.

## Still blocked, and by what exactly

ODA `vandkemi` **is not fetchable by `scripts/fetch_oda.py` as it stands.** `TOPICS`
holds five keys — `stations`, `ctd`, `lys`, `iltkor`, `maaledybde` — and
`argparse(choices=sorted(TOPICS))` rejects `kemi`: the docstring advertises the topic,
the dict does not implement it. Missing is one `Emne_<n>_<m>` node id,
discoverable with the `expand()` helper already in the file. Separately, `run()`
hardcodes `topic.aspx?id=h&t=h` — **Hav** — so `ODA-STOFTRANSPORT` (Vandløb /
Stoftransport / Månedstransport) and `ODA-TILFOERSEL`, the two that actually carry
{ref:A1}'s load term, need a code change, not merely a table entry.

Size, estimated and not measured: vandkemi is bottle samples, a few depths × tens of
parameters per visit, against CTD's hundreds of depth bins × {q:depth bins × @@ — so one} — so one to two orders
of magnitude fewer rows than ctd's {q:rows than ctd's @@⁷: **10⁶–10⁷ rows,}⁷: **{q:than ctd's ~5×@@⁷: **10⁶–10⁷ rows,}⁶–{q:ctd's ~5×10⁷: **@@⁶–10⁷ rows, roughly}⁷ rows, roughly {q:rows, roughly @@ gzipped**, streamed} gzipped**,
streamed in {q:gzipped**, streamed in @@ KB chunks under} KB chunks under the existing `--max-mb 2000` guard. Not a multi-GB job.
I did not run it.

And the warning: marine vandkemi is nitrogen **concentration in the sea**, a state and
a response. Substituting it for a land load commits the very class-{q:very class-@@ error this} error this
hypothesis stands charged with.
"""


def main(argv):
    return 0 if draftkit.build(REL, TEXT) is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
