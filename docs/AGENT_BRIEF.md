# Standing brief

Given to every agent working on this project, and to anyone contributing. It is short
because it is meant to be obeyed rather than admired.

---

## 1. Nothing is given

Every count carries a rule for what counts as **one**, and that rule is invisible by
the time the count is a number. Call it the **applefication assumption**. Point at a
deck of cards and ask *how many?* — one deck, four suits, fifty-two cards, [10²⁴](SOURCES.md#F-9949d955e7) atoms.
There is no answer until somebody has said what a one is.

So for any quantity you handle, three questions in order:

1. **What is the individuation?** What was treated as one thing, one kind, one member?
2. **Is it reasonable** for the use it is being put to?
3. **Is it stable?** — the only one with an empirical answer.

A number is where this hides best, because a number looks like the least theory-laden
object in a dataset. Its theory happened upstream, at counting time, and nothing in the
digit records it.

---

## 2. Say what kind of thing a quantity is

**This is the rule broken most often, including here.** When you name a quantity, label
it. Never write "X is [69.6](SOURCES.md#F-0666c7bdae)%" when X is a residual over products of norm coefficients.

| kind | what it means | example from this project |
|---|---|---|
| **measurement** | an instrument was in contact with the thing | near-bed oxygen from a sonde |
| **derived** | arithmetic on measurements | salinity, computed from conductivity + temperature |
| **estimator** | a statistic meant to approximate an estimand — **name both** | monthly median as a stand-in for monthly state |
| **residual** | total minus known parts; absorbs every error in the parts | the [69.6](SOURCES.md#F-0666c7bdae)% agricultural attribution |
| **construction** | a count under an individuation rule someone chose | "[123](SOURCES.md#F-8b12d8de95) water bodies", "[1,415](SOURCES.md#F-5fb04be1c0) stations" |
| **norm product** | a register count × a regulatory coefficient | *markoverskud*: livestock counts × excretion norms |
| **model output** | produced by a model, possibly calibrated to measurements | DK-QNP diffuse load over the ungauged area |
| **threshold class** | a continuum cut at a number | "hypoxia" as oxygen below [4](SOURCES.md#F-dad8fcad81) mg/l |

Two compounds are especially dangerous and both occur here:

- **A residual of norm products, used as a model input, then correlated with that
  model's output** and reported as a finding. The correlation is structural.
- **A threshold class whose defining variable is deterministically coupled to another**
  — an oxygen concentration threshold is partly a thermometer, because solubility is a
  function of temperature and salinity.

---

## 3. Compute your null, never quote it

A statistic's published null is the null of the model it was derived under, **not of the
constraint you actually imposed.** Five times in this project a quoted null was wrong:

| statistic | quoted | actual |
|---|---|---|
| mean-square ratio MSB/(MSB+MSW) | [0](SOURCES.md#F-13d3570fb8) | **[0.5](SOURCES.md#F-03b0a1406f)** |
| ARI, [12](SOURCES.md#F-05b0f12767) groups vs [84](SOURCES.md#F-6ec6f04bb2) | max [1.0](SOURCES.md#F-d9f40cbf06) | **max [0.132](SOURCES.md#F-be3cd8b1f3)** |
| ARI between contiguity-constrained partitions | [0](SOURCES.md#F-13d3570fb8) | **[0.337](SOURCES.md#F-63b0e94602)** |
| ARI between *derived* partitions | [0.337](SOURCES.md#F-63b0e94602) | **[0.12](SOURCES.md#F-63ceaa9074)** |
| annual minimum vs sampling effort | falls with effort | **rises** |

**One of those ran against the finding.** The direction is not guessable in advance,
which is the whole argument for measuring rather than quoting.

---

## 4. The rest

- **Water bodies are a model assumption, not a unit.** Do not aggregate into them.
  "Denmark" is not a closed system either.
- **An absent dimension makes a hypothesis unscoreable, not refuted.** Do not let "no
  data" become "no effect".
- **Flag, never delete.** Outliers are the only observable sample from the error
  process. Trimming them destroys the sole estimator of the archive's own error rate
  while making it look cleaner.
- **Say what a number is a distribution of.** A single figure asserts that everything
  it summarises was one kind of thing — and a distribution of the wrong thing is as
  uninterpretable as a mean.
- **The data you have found is not all there is.** Stage 2 of [PLAN.md](PLAN.md) is
  unfinished. Independence between sources matters more than volume: nine archive
  variables are three sensors.
- **Do not fabricate.** "Not established" is a valid and expected answer. A source you
  cannot verify is a source you say you could not verify.
- **Steelman before you report a failure.** A bad argument in a document does not mean
  there are no good ones elsewhere. Ask what the strongest version of the case would
  be, look for it, and say whether you looked. This project published a circularity
  finding and had to narrow it within the hour: the authors qualified the figure
  themselves on the next page, and a paired-catchment study existed that nobody here
  had read.

## 4b. Stated conventions

A category everyone uses and nobody defines is the applefication failure in its purest
form. Three drafts in this project split the stations into *summer-peaked* and
*year-round* and got **[293](SOURCES.md#F-fca172462e)/[481](SOURCES.md#F-e098ccb226), [282](SOURCES.md#F-15dccff240)/[480](SOURCES.md#F-d79ef0cf11) and [426](SOURCES.md#F-179879634c)/[427](SOURCES.md#F-0380496fd0)** — all defensible arithmetic on
different unstated rules, one of them arithmetically impossible.

**The station seasonality convention, from here on:**

> Classify on the Rayleigh statistic **Z = N·R²**, never on raw R.
>
> - **seasonal** — Z > [3](SOURCES.md#F-b49622f395) (about p < [0.05](SOURCES.md#F-bae8d9078a)) *and* mean direction in June–September
> - **year-round** — Z ≤ [3](SOURCES.md#F-b49622f395) *and* N ≥ [24](SOURCES.md#F-22b645cad0), so the test had the power to reject
> - **neither** — everything else. **A station with too few observations is not
>   year-round; it is unclassified.**
>
> State the variable basis, since it changes the answer: on all nine variables,
> [885](SOURCES.md#F-4fa2069646) / [254](SOURCES.md#F-20304cbe50) / [276](SOURCES.md#F-636cc985b4). On `oxy_bed` alone, [357](SOURCES.md#F-439213ca66) / [271](SOURCES.md#F-f33d294e76) / [699](SOURCES.md#F-46715ffbdd).

**Why Z and not R.** R is [1](SOURCES.md#F-ae1c59a95e) whenever a station has a single observation — the direction
is perfectly concentrated because there is only one of it. `oxy_bed` has **[254 stations](SOURCES.md#F-8095c96da8)
with exactly one observation**, and a raw-R rule with no minimum put all of them in the
"strongly seasonal" group, where they were [39%](SOURCES.md#F-131475f764) of it and [57%](SOURCES.md#F-ed1d3ad63d) had three observations or
fewer. The statistic was measuring scarcity. **Z = N·R² fixes this without an arbitrary
cutoff**, because a single observation gives Z = [1](SOURCES.md#F-22ff675aa2) and fails on its own.

The general rule this is an instance of:

> **If a category decides a result, its definition is part of the result.** Write it
> down, state the parameter that moves it, and report what the answer is under the
> alternatives. A category used by three analyses under three unstated rules is not one
> category.

## 5. What may be emitted

A coefficient, at a stated level of organisation, against a stated null, for a named
functional, at a stated point in the accumulation of measure-spaces. **Five qualifiers,
none droppable.** Drop any and you have produced a verdict, which is a different kind of
object than this procedure can make.

Not emittable: *"X is real"*, *"X is not real"*, *"the result is in"*. Those are not
false — they have no referent, because the space of groupings and functionals is open.

Full method: [statistical-methods](https://github.com/Jjokulian/statistical-methods).

---

*Generated by `scripts/pages/agent_brief.py`. The table of nulls and the seasonality
counts record what earlier work found; no script stores them, so they are quoted from
this page as it was first written.*
