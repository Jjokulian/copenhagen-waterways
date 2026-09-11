#!/usr/bin/env python3
"""Writes docs/hypodrafts/C1.md: a hypothesis draft, as generated text.

Every hypothesis ID is a checked reference, every chemical species a checked
species, and every number either read live or quoted from the page as committed
({q:…@@…}, a located quotation - see draftkit.py) because nothing in the repository stores it yet.

    python3 scripts/pages/hypodraft_c1.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draftkit

REL = "docs/hypodrafts/C1.md"
TEXT = r"""# {ref:C1|title}

**Testable. This is a draft; nothing here has been run.**

`C1` predicts deficit "tracks the strength and persistence of the pycnocline, and is near
zero in well-mixed water whatever the load."

**Scope cut first.** *Persistence* is not testable here. A cast is a snapshot, sampling is
roughly monthly, and whether a pycnocline held between visits is unobserved (class 6).
What follows tests **strength only**; persistence needs a moored T/S chain for one
stratified season — an instrument, not an analysis.

## 1. The observable consequence

Two claims of different strength, treated separately.

**C1a (gradient).** Within one station and calendar month, casts with stronger density
structure have less oxygen in the bottom metre.

**C1b (floor).** Well-mixed casts do not show low bottom oxygen — the strong claim, and
the falsifiable one.

> **Falsifies C1b:** a non-trivial count of casts with stratification in the lowest
> quintile *and* low bottom oxygen. One is an outlier; hundreds mean a mixed column can
> also run out, and "near zero in well-mixed water" is false as stated.
>
> **Falsifies C1a:** the association between the potential energy anomaly φ and bottom
> oxygen does not exceed the computed null of §3.

**What is not the test.** DCE's iltsvind criterion is oxygen below {q:oxygen below @@ *in stratified} *in stratified
bottom water* ([CURRENTS.md](../CURRENTS.md)), so regressing the published iltsvind extent
on stratification tests nothing — stratification is inside the response's definition.
Class 7, circular by construction. Only raw per-measurement oxygen is used.

## 2. The data, and the circularity check

**Source:** `data/raw/oda/ctd.csv.gz` ({q:`data/raw/oda/ctd.csv.gz` (@@ gzipped), one} gzipped), one row per measurement, with
`Dybde (m)` and coordinates. Verified by a full streaming pass:

| quantity | count |
|---|---|
| station-days with both a `Temperatur` and a `Salinitet` value | **{fig:dc1_ts}** |
| … with ≥{fig:da_c1_min_levels} depth levels of each | **{fig:dc1_levels}** |
| … and an `Oxygen indhold` value (mg/l) | **{fig:da_c1_days}** |
| … joined to a recorded `BundDybde_m` in `maaledybde.csv.gz` | **{fig:dc1_bottom}** |
| … of those, profile reaching ≥{fig:dc1_deep_m} m | **{fig:dc1_bottom_deep}** |
| deepest {chem:O2} within {fig:dc1_near_m} m of deepest T (of {fig:dc1_ts}) | **{fig:dc1_near}** |
| distinct stations / span | **{fig:dc1_stations}** / {fig:dc1_first}–{fig:dc1_last} |

`maaledybde.csv.gz`: {fig:dc1_maal_days} distinct station-days, {fig:dc1_maal_bottom} carrying `BundDybde_m`.
**Primary sample: the {fig:dc1_bottom}.** `stations_series.bin` cannot be used: it is a monthly
*median* of surface and bed separately, which breaks the pairing a cast needs — class 3.

**Circularity.** φ is computed from density, and density is a function of T and S.

1. `oxysat_*` is computed from oxygen, temperature and salinity — two of three inputs
   shared with φ. **Not used.** Only `Oxygen indhold` in mg/l.
2. Salinity is computed from conductivity and temperature, so φ rests on two sensor
   channels and oxygen is a third. Not circular — but φ's error and T_bed's error are
   correlated wherever T_bed is a covariate.
3. **The residual coupling is thermodynamic, and is the whole difficulty.** Oxygen
   *solubility* is a deterministic function of T_bed and S_bed: a warm stratified summer
   has high φ and low saturation concentration for reasons that are `C6`, not `C1`. Not
   removable by a covariate; measured instead, in §3.

**Error classes.** Depth quantised to {q:Depth quantised to @@ below ~5 m} below {q:1 m below @@ (0.2/0.5 m nearer} ({q:m (@@ nearer the surface)} nearer the surface) —
class 2, boundable by recomputing φ on sub-metre casts against their own {q:their own @@-decimated copies.}-decimated
copies. `SondeNavn` is `999 - Ukendt` on most rows of all three parameters (over the whole extract: {fig:dc1_unk_t} Temperatur, {fig:dc1_unk_s} Salinitet, {fig:dc1_unk_o} Oxygen rows; in the
earlier {q:parameters (@@ decompressed sample:} sample the next-largest instrument had {q:next-largest instrument has @@k) — class}k) — class 5: Winkler cannot be separated from optode, nor
salinometer from CTD. `Salinitet` is one Parameter over both production paths with no
distinguishing column — class 4, not boundable, and it enters φ directly. **No time-of-day
column exists anywhere** — class 6. A midday cast carries a diurnal warm surface layer a
dawn cast does not, inflating φ with no ventilation meaning; this attenuates C1a (making
it conservative) and inflates the mixed set for C1b (making it anti-conservative). Neither
countable nor correctable.

## 3. The null — computed, never quoted

Statistic: **Spearman ρ between φ and bottom oxygen C_bed**, pooled over eligible casts.
Three nulls, because the quoted null of zero is wrong under every constraint imposed here.

**Null A — the thermodynamic surrogate.** Replace each cast's observed C_bed with
C_sat(T_bed, S_bed): what a fully ventilated, non-respiring column would hold. Recompute
ρ. This is the association φ has with bottom oxygen under **no ventilation limitation at
all**, arising purely from shared T and S — an empirical number, plausibly large and
negative, and **the floor the observed ρ must beat.** Bootstrap over stations, {q:over stations, @@ draws. **Null} draws.

**Null B — the design null.** Strata = station × calendar month × decile of recorded
bottom depth. Shuffle φ within strata, recompute the *pooled* ρ, {q:*pooled* ρ, @@ times. The} times. The result
is not centred on zero: it retains the between-stratum association depth, season and place
produce on their own. Its distance from zero is the size of the confounding — a result
worth reporting by itself.

**Null C — for C1b.** Let *p* = the fraction of casts in the lowest φ quintile (within
depth decile) whose C_bed falls below the 5th percentile of C_bed in its own station ×
calendar-month stratum. C1b predicts *p* ≈ {q:predicts *p* ≈ @@. Null C is}. Null C is *p* under the same stratified
shuffle as Null B — near {q:B — near @@, but **not}, but **not assumed to be {q:assumed to be @@**: the two}**: the two stratifications
interact. Report the permutation distribution.

## 4. Procedure

1. Stream `ctd.csv.gz` once, emitting `(station, date, depth, parameter, value)` for the
   three parameters. Intermediate {q:parameters. Intermediate @@ on disk;} on disk; never load the archive into memory.
2. Keep casts with {q:casts with @@ paired T/S} paired T/S levels, a bottom {chem:O2} within {q:bottom O2 within @@ of the deepest} of the deepest T, and a
   `BundDybde_m` join. Never aggregate into water bodies — station and position are the units.
3. Potential density per level, under **both** `EOS-80` and `TEOS-10`, reporting the difference
   as a bound rather than picking one; then φ = (g/h)∫(ρ̄ − ρ(z))·z dz over the cast.
4. C_sat(T_bed, S_bed) for Null A. Compute the statistic and all three nulls. Report ρ
   **beside** Null A and Null B, never beside zero.
5. Report the count and station list of lowest-quintile-φ casts with C_bed below {q:C_bed below @@ (a borrowed}
   (a borrowed threshold, flagged as such), plus the full distribution.

## 5. What a result would and would not license

**A positive C1a result licenses:** within a station and month, stronger density structure
accompanies lower bottom oxygen by more than shared thermodynamics explains. **It does not
license** causation — wind (`C2`), bottom temperature (`C6`), residence time (`C3`) and
load all covary with φ — nor anything about persistence, nor weighting a nitrogen
coefficient by stratification, since load is absent (ODA `vandkemi` is not fetched).

**A falsification of C1b** — hypoxic casts in well-mixed columns — is the strongest thing
available here, and it is one-directional. Finding them refutes "near zero in well-mixed
water whatever the load." *Not* finding them confirms nothing, because well-mixed Danish
columns are also mostly shallow, and the class 6 timing gap means some casts labelled
mixed were merely sampled at dawn.

**Nothing here licenses a share.** φ explaining variance in C_bed is a within-field
statement about one of {fig:da_n_register} enumerated mechanisms, not a decomposition.
"""


def main(argv):
    return 0 if draftkit.build(REL, TEXT) is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
