# The category that was never measured

Hand-written rather than generated. This is the companion to
[RESIDUAL.md](#RESIDUAL.md), and the same shape of mistake one column to the left.
That page is about a *number* nobody measured being treated as one. This is about a
*category* nobody measured being treated as one.

You do not need to care about Denmark to use it.

---

## The tell

Open any dataset. The continuous columns carry error: salinity 12.4 ± 0.2 ‰, oxygen
4.1 ± 0.3 mg/l, a detection limit, a calibration date, a sonde serial number.

Now look at the categorical columns. Water body `DKCOAST2`. Citizenship `DK`. Sector
`C10.51`. Diagnosis `E11.9`. Species *Fucus vesiculosus*. Land use `arable`.

**Not one of them has an error bar, and not one of them was measured.**

Each is the output of a model — a polygon someone drew, a legal test someone
applied, a classification someone wrote down — presented in the same table, in the
same typeface, as the quantities that came off an instrument. The instrument reading
is an observation with a known error. The category is a claim with an unstated one.

## What the category is actually doing

Every basket carries two things that are easy to conflate, and the conflation is the
whole problem:

1. **A membership rule.** Who is in. This is usually sound, often precise, and
   frequently a genuine fact about the world. Roskilde Fjord really is an enclosure.
   Danish citizenship really is a determinate legal status. A postcode really is a
   postcode.
2. **An attribution.** What members are taken to share. This is a *statistical*
   claim, and nothing in the membership rule establishes it.

The name serves both functions, so the switch between them goes unnoticed. Asking
"is this a real category?" answers question 1 and is almost always yes. The question
that has content is different:

> **Does membership predict the thing you are using it to predict — and does it
> predict better than a same-shaped arbitrary grouping would?**

## The measurement

There is a standard statistic for this and it is not new: the **intraclass
correlation**. Pick two members of the population at random. If they are in the same
basket, how much more alike are they than two picked without regard to basket? One
means membership tells you everything; zero means it tells you nothing.

Two things make it usable rather than decorative.

**Condition on what everything shares.** Every marine station in Denmark experiences
the same season. Pool across months and the seasonal signal lands in the
between-basket term and *every* partition scores well — including a deliberately
absurd one. The same applies wherever a common driver exists: compare within year,
within cohort, within whatever the members hold in common regardless of basket.

**Compare against a null that matches the basket's shape.** This is the part that
gets skipped, and skipping it is how a defensible number comes out backwards.

## The statistic is a model too, and on its own it is circular

The measurement above has a defect that has to be stated before the worked example,
because it applies to every number on this page.

**The intraclass correlation takes the partition as an input.** So does F<sub>ST</sub>,
which is the same statistic in population-genetics clothing:
F<sub>ST</sub> = (H<sub>T</sub> − H<sub>S</sub>) / H<sub>T</sub>, and
H<sub>S</sub> — the variation *within subpopulations* — cannot be computed until the
subpopulations have been declared. Citing an F<sub>ST</sub> value as evidence that
populations are distinct is therefore reasoning in a circle: the number was
manufactured by assuming them.

In practice the circle is tighter still, because the partition usually comes from the
**sampling design**. Collect fifty Danes and fifty Dutch and "Danish" and "Dutch" are
your groups by construction; the statistic then reports on a boundary the fieldwork
drew. Nor is it one statistic — Wright's original, Nei's G<sub>ST</sub>, Weir and
Cockerham's θ and Hudson's estimator return different numbers from identical data,
and the choice of loci and weighting are modelling decisions taken before any of them
runs. It is an aggregation function over a chosen metric, presented as an observable.

**This is why the null is not a refinement. It is the thing that rescues the
measurement.**

A circular statistic compared against a *shape-matched null* stops being circular,
because the null partitions were not chosen to be real. Each number separately is
contaminated by the assumption; the **difference** between them is not. That is the
whole argument for the exercise below, and it is why a single reported value — a bare
F<sub>ST</sub>, a bare ICC, a bare R² between groups — carries almost no information
about whether the groups are anything.

## Three nulls, three answers — a worked example

Denmark's marine water bodies, scored for nine measured variables, within month:

| null | what it holds fixed | what it destroys | which variable "wins" |
|---|---|---|---|
| shuffled labels | basket sizes | geography entirely | salinity, by a distance |
| latitude stripes | compactness, equal sizes | hydrography | surface oxygen saturation |
| size- and shape-matched blobs | **both** sizes and compactness | hydrography only | surface oxygen saturation |

The first two disagree, and not marginally: surface oxygen saturation gains **+0.065**
over the shuffle and **+0.408** over the stripes. Only the third varies one thing at
a time, and against it the ordering from the first is **reversed** — oxygen gains
most, salinity little, and fluorescence goes *negative*, meaning random compact blobs
of the same sizes predict it better than the official partition does.

This page exists partly because this project published the first answer and had to
withdraw it. It was defensible, reproducible, and wrong, and it survived exactly as
long as it took to compute a second control.

The reading that survives is not about which variable matters:

> **A partition's value is not how well it predicts, but how much better it predicts
> than its own shape alone would.**

Salinity is spatially smooth, so *any* compact grouping predicts it well and real
boundaries have nothing left to add. Oxygen is rough, so shape alone fails and
boundaries that follow enclosure carry real information.

## Two methods, and the condition that chooses between them

The null comparison above is not the strongest test available. It is the strongest
test available *when the feature space is small*, and that is why it became standard.

A null answers: **given these measurements, does this grouping beat chance?** The
answer is still conditioned on which measurements were taken, so it cannot separate a
property of the entities from an artifact of what someone chose to record.

There is a test that can, and it assumes no partition at all:

> Cluster the entities using a **random subset** of the measured features.
> Cluster them again using a **disjoint** random subset.
> Ask how much the two agree — and whether agreement **rises** as the subsets grow.

A grouping that appears only when one particular measurement is included is an
artifact of that measurement. A grouping that appears whichever features are drawn is
a property of the entities. Convergence as the subsets widen is the signal; flat
agreement near chance means there is nothing to converge on. The official partition is
then scored on the same axis — its agreement with each derivation — so it is one
candidate among them rather than the standard they are marked against.

**Why this was not the historical default.** When these statistics were developed, a
study had three or four measurements. You cannot split a feature space that small
into disjoint halves; there is nothing to hold out. The null was not a compromise, it
was the only thing available.

That condition has quietly reversed. Measurement is now automatic and cumulative:
many groups measure many things on the same entities, and the columns accumulate
independently of any one question. Where that has happened, the stronger test is
available and the weaker one is a habit.

**So the rule is a threshold, not a preference.** Below roughly a dozen independent
features, use a shape-matched null and accept that it cannot distinguish the entities
from the instrument. Above that, split the feature space, because you can.

*This page's own worked example sits at the bottom of that range — nine variables,
so four per half — which is why the marine result is reported as suggestive. The
method wants a case with dozens of characters per entity, which is what
`../organism` exists to try.*

## You have read this category in other clothes

Not rare, and not Danish. One line each, with no claim that any is wrong — only that
each has a membership rule doing one job and an attribution doing another:

- **Citizenship.** A determinate legal status, acquired by birth, descent or
  naturalisation. Used as a proxy for population, culture, ancestry, or behaviour —
  none of which the membership rule tracks. The rule is *legal*; the attribution is
  usually *biological or cultural*.
- **Race.** The literature's central dispute is exactly this statistic. Lewontin
  (1972) partitioned human genetic variance: ~85% within populations, ~15% between —
  an ICC of 0.15. Edwards (2003) replied that correlated loci make classification
  accurate anyway, which is true and is *our compact-null finding*: high
  classifiability is what a smooth cline gives you wherever you cut it. Rosenberg et
  al. (2002) is cited for finding clusters; Serre & Pääbo (2004) sampled the same
  geography continuously and got gradients. Sampling design, again.
- **Species.** Biological, morphological and phylogenetic species concepts are three
  different membership rules over the same organisms, and they do not agree. Which
  one is "correct" has no answer; which one predicts a given trait does.
- **Industrial sector** (SIC, NACE). A firm's code is assigned, often by the firm.
  Productivity and emissions are then compared "within sector".
- **Diagnosis codes.** A membership rule built for billing, used as a phenotype.
- **Deprivation by postcode.** An area statistic attributed to the individuals in it
  — which is the ecological fallacy, and the same error
  [AREAS.md](#AREAS.md) reports for Denmark.

## What to demand instead

Not that categories be abandoned — they are how anything gets counted. Three
questions, and they are cheap:

1. **What is the membership rule?** Say it out loud. Legal, geometric,
   administrative, self-reported?
2. **What is being attributed to members?** And is that the same kind of thing as
   the rule?
3. **What is the lift over a same-shaped null?** Not the raw statistic — the raw
   statistic took the category as an input and cannot testify about it. The lift.

If the answer to 3 is unknown, the category is being used as data when it is a
model, and any figure computed inside it is a statement about the basket at least as
much as about the world.

---

*Companion pages: [RESIDUAL.md](#RESIDUAL.md) for the same error committed on a
number, [AREAS.md](#AREAS.md) for the measured Danish case, `X22` in
[EXPERIMENTS.md](#EXPERIMENTS.md) for the test that would settle it here. And the
obvious self-application: this project sorts 165 mechanisms into 17 groups, which is
a partition nobody has scored either.*
