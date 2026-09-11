# A1b — Does the constructed surplus cohere with the measured load?

*Numbers shown as quotations are carried from this page as committed at `ac84f5b`: nothing in the repository stores them yet, so each says what the page said, not that it was re-derived.*

**Not in HYPOTHESES.md.** This test came out of a question about [A1](../hypodrafts/A1.md "Danish land-based nitrogen load") and is written here
because it is more specific than the hypothesis it serves: *the field surplus is a
construction and the stream and estuary nitrogen are measurements — do they move
together, and does the relation hold still?*

Companion to [`A1.md`](A1.md), which drafts the residual-growth test on the published
attribution. This one tests the **coupling**, not the accounting.

---

## The observable consequence

`markoverskud` contains at least two components that no field produced:

- **1999** — the nitrogen norm was cut [10%](../SOURCES.md#F-90ea3babec), dropping the quota [~40,000 t N](../SOURCES.md#F-b4b0b71ff4), while grass
  norms changed simultaneously, raising it [~15,000 t N](../SOURCES.md#F-655a29e90b). DCE's own report calls the
  result a *"spring"* in the compiled series.
- **2012** — the method for computing nutrients removed at harvest changed from
  dry-matter yield to feed units, and the net-input figures *"er steget lidt ift. de
  tidligere opgørelser."*

Both are **administrative events on known dates with no physical counterpart.** So:

> **If the constructed series steps at 1999 and the measured series does not, the
> surplus↔load relation must break at that date. The size of the break is a direct
> measurement of the construction's non-physical component.**

**Falsified if** the relation is stable across 1999 — which would mean either the norm
change passed through to real application, or the step is small relative to the noise,
and either way the construction is not carrying a spurious discontinuity.

**Confirmed if** a regression fitted before 1999 mispredicts after it, in the direction
and roughly the magnitude the norm change implies.

## Why this test and not a correlation

Windolf et al. (2012) already report significant linear relations between N surplus and
normalised diffuse load in nine of ten catchments, over 1990–2009. **They fit one line
per catchment over the whole window and never ask whether it holds in both halves** —
and that window straddles 1999. A correlation over the full period cannot distinguish a
real coupling from a coupling plus a shared administrative step; a discontinuity test
can, because only one of the two series should step.

This is the residual-growth logic applied sideways. There, a part is moved out of a
leftover and the arithmetic must close. Here, a part is moved *into* the construction by
an administrative decision, and the measurement must **not** move.

## Data

| | source | status |
|---|---|---|
| annual `markoverskud`, national, 1990– | DCE SR120 Bilag 1; recomputed each vintage | **public PDFs**, `pdftotext`-extractable |
| annual N surplus per catchment | Windolf et al. (2012) supplementary B | with the paper |
| normalised diffuse load per catchment | Windolf et al. (2012); DCE annual reports | published |
| **estuary total N, measured** | national monitoring 1989–, [12–46 samples](../SOURCES.md#F-f2237e06d9)/yr | the independent terminal series |
| stream N, gauged fraction | fortnightly total-N × daily discharge | measured; [22–87%](../SOURCES.md#F-441f17532d) of area by catchment |

**Error classes**: the surplus is a **norm product**; the load is **hybrid** — measured
on the gauged fraction, class 7 on the rest, since the ungauged part is DK-QNP output
whose input is the surplus itself. **Use the gauged fraction only**, or the test is
partly circular by construction. Estuary N is the cleanest series available and is
class 1–2 throughout.

## The null, which is not zero

A break-point test finds breaks in autocorrelated series with no breaks in them. The
null must be **matched-autocorrelation surrogates with no step**, and the reported
quantity is where the observed break sits in that distribution — not a p-value against
independence.

Two further controls, both cheap:

- **Placebo dates.** Fit the same break test at every year 1993–2006. If 1999 is not
  distinguished from its neighbours, there is no step to find.
- **Gauged-fraction stratification.** The circular component scales with the modelled
  share, so the effect should be **strongest at Isefjord ([22%](../SOURCES.md#F-623e3ac85d) gauged) and weakest at
  Randers ([87%](../SOURCES.md#F-97873341f0))**. That gradient is a prediction no rival explanation makes.

## What a result would and would not license

**Would**: a number for how much of the surplus series is administrative, on a stated
date, with the measured series as reference.

**Would not**: anything about whether agriculture causes hypoxia. This tests the
coherence of two series, one constructed and one measured. A clean break at 1999 would
say the construction carries a bookkeeping jump — not that the underlying load did not
fall. Windolf's measured estuary nitrogen fell [24–62%](../SOURCES.md#F-c02269d60b) regardless, and the intercept of
those regressions lands on independently measured background. **Both things can be true:
the construction is partly administrative, and the decline is real.**

## Status

Not run. The catchment-level series are in a paper supplement and DCE annual reports;
neither has been extracted. Nothing here has been computed.
