# Standing brief

Given to every agent working on this project, and to anyone contributing. It is short
because it is meant to be obeyed rather than admired.

---

## 1. Nothing is given

Every count carries a rule for what counts as **one**, and that rule is invisible by
the time the count is a number. Call it the **applefication assumption**. Point at a
deck of cards and ask *how many?* — one deck, four suits, fifty-two cards, 10²⁴ atoms.
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
it. Never write "X is 69.6%" when X is a residual over products of norm coefficients.

| kind | what it means | example from this project |
|---|---|---|
| **measurement** | an instrument was in contact with the thing | near-bed oxygen from a sonde |
| **derived** | arithmetic on measurements | salinity, computed from conductivity + temperature |
| **estimator** | a statistic meant to approximate an estimand — **name both** | monthly median as a stand-in for monthly state |
| **residual** | total minus known parts; absorbs every error in the parts | the 69.6% agricultural attribution |
| **construction** | a count under an individuation rule someone chose | "123 water bodies", "1,415 stations" |
| **norm product** | a register count × a regulatory coefficient | *markoverskud*: livestock counts × excretion norms |
| **model output** | produced by a model, possibly calibrated to measurements | DK-QNP diffuse load over the ungauged area |
| **threshold class** | a continuum cut at a number | "hypoxia" as oxygen below 4 mg/l |

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
| mean-square ratio MSB/(MSB+MSW) | 0 | **0.5** |
| ARI, 12 groups vs 84 | max 1.0 | **max 0.132** |
| ARI between contiguity-constrained partitions | 0 | **0.337** |
| ARI between *derived* partitions | 0.337 | **0.12** |
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

## 5. What may be emitted

A coefficient, at a stated level of organisation, against a stated null, for a named
functional, at a stated point in the accumulation of measure-spaces. **Five qualifiers,
none droppable.** Drop any and you have produced a verdict, which is a different kind of
object than this procedure can make.

Not emittable: *"X is real"*, *"X is not real"*, *"the result is in"*. Those are not
false — they have no referent, because the space of groupings and functionals is open.

Full method: [statistical-methods](https://github.com/Jjokulian/statistical-methods).
