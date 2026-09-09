# Constructions, held against measurements

A constructed quantity — a residual, a norm product, a partition, a threshold, a model
output — should be held against something that was measured, and **the relation between
them stated as a number.** Almost none ever is.

This page is the register of every such comparison this project has actually run. It is
meant to be added to.

---

## The check

Given a construction `C` and a measurement `M` that ought to track it:

1. **Sign** — do they move together at all?
2. **Coefficient** — is the ratio `ΔM/ΔC` stable across strata, or does it range?
3. **Discontinuity** — does `C` step on a date where `M` does not? A step with an
   administrative cause and no measured counterpart is the construction's non-physical
   component, and its size is measurable.
4. **Aggregation** — does the pooled relation look tighter than the stratified one? If
   so, the tightness is partly the pooling.

Most published constructions have had step 1 done and stop there. **Steps 2 and 4 are
where they fail**, and they fail in a way that a good sign hides.

---

## The register

| construction | held against | result | verdict |
|---|---|---|---|
| **`markoverskud`** — field surplus, a norm product | measured normalised diffuse load, per catchment, 1990–2009 | pass-through **0 to ~⅓**; 10–14 kg N/ha of load per 30–52 of surplus in three catchments, 3–5 per 24–50 in two, **zero at Mariager** | **sign good, coefficient not usable.** A load predicted from a surplus is overestimated 3–10×, or entirely |
| the same, **at national scale** | the same, pooled | *"en meget stærk, signifikant lineær relation"* | **the pooled fit is tight because the coefficient varies.** Step 4 failing in public |
| **123 water bodies** — a drawn partition | measured station similarity, all 255 feature subsets, contiguity-matched null | lift **−0.026 to −0.014** | adds nothing beyond being a connected region of its size |
| **pooled oxygen trend** | the same trend on year-round stations only | pooled median dips to **7.42** when the summer network is 32% of observations and rebounds to **7.77** at 12%; year-round subset moves **7.82 → 7.90** | the pooled wobble is **network composition**, not water |
| **`< 4 mg/l` hypoxia threshold** | the same seasonality on a saturation threshold | **23.6-fold** against **15.5-fold** | roughly a third of the seasonal signal is oxygen solubility — the threshold is partly a thermometer |
| **`DIATO`, `DINO`, `PICO`, `NANO`** — 24 GB of plankton fields | `CHL`, the same file | ratio functionally determined by CHL; within-bin spread **6.3×10⁻⁴** against a range of 0.33–0.43 | **six fields that are one field.** Composition change at constant biomass is unrepresentable |
| **`hz`, marine hazardous-substance coverage on 66 of 123 water bodies** — ours | the source layer's own geography | **0 of 256 points are marine** (152 lake, 104 river) | withdrawn; the coverage was manufactured by proximity |
| **`SigtDybde_m`, Secchi depth** | `BundDybde_m`, bottom depth, 96,708 paired rows | seen-to-bottom on **21.36%** of readings ≤10 m and **0.36%** deeper | right-censored, **59× more in shallow water**; any clarity-vs-depth comparison is partly the censoring |
| **ρ\*, the mean-square ratio reported as ICC** | its own null, simulated | null is **0.5**, not 0 | every raw value was unreadable as published |
| **ARI across mismatched granularities** | its attainable maximum | max **0.132** at 12 groups vs 84 | an observed 0.117 was 88% of ceiling, not near-floor |
| **`confident` on the Nørrebro flood sheet** — ours, a quality flag | the spread over *all* registration variants, not just the agreeing ones | agreeing-spread **12.7 m**, the tightest in the set; **all-variant spread 3,115 m**, against 27–28 m for the good sheets; agreement a bare 3/6; the bundle adjustment could not touch it | **the confidence statistic was conditioned on the selection it validated.** Withdrawn; sheet withheld from the viewer |
| **"summer-peaked" vs "year-round" stations** — ours, a category | its own definition, varied | three analyses gave **293/481, 282/480, 426/427**; the last is impossible, since only 488 `oxy_bed` stations have ≥24 observations | **the category was never defined.** Under a raw-R rule with no minimum, **254 stations with one observation** score R=1 and became 39% of the "seasonal" group |

Ours are marked as ours. Four of the ten entries are this project's own constructions
failing its own check, which is the point of keeping the register rather than a list of
other people's errors.

---

## What the register shows

**Sign is cheap and coefficient is not.** Every construction here passes step 1. Most
fail step 2 or step 4 — the direction is right and the magnitude is not transferable.
That is the failure mode a correlation cannot detect and a published relation almost
never reports.

**Aggregation is where the failure hides.** `markoverskud` at national scale looks
strong and at catchment scale ranges from zero to a third. The water bodies look like a
partition and carry no within-basket signal. The pooled oxygen trend looks like water
and is network composition. In each case **the pooled statistic is tighter than any of
its parts, and the tightness is what aggregation does to a variable coefficient.**

**And a good sign licenses a claim about direction only.** "Nitrogen surplus fell and
load fell" is supported. "Cutting the surplus by X will cut the load by 0.7X" is not,
anywhere in this data.

---

## Adding to it

An entry needs four things: the construction, the measurement it was held against, the
number, and what the comparison licenses. If a check was run and passed, that belongs
here too — a register of only failures would be a construction with its own selection
problem.

Method, and the audit of which parts of it survive their own rules:
[statistical-methods](https://github.com/Jjokulian/statistical-methods).
