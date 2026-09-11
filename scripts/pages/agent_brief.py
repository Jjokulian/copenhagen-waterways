#!/usr/bin/env python3
"""docs/AGENT_BRIEF.md - the standing brief given to every agent and contributor.

The brief was hand-written, and most of its numbers are examples of the rules it
states: a published share, two counts under an individuation rule, a threshold, a
table of nulls this project once quoted wrong, and the counts three drafts got
from one unstated category. The examples are only worth as much as their
numbers, so each comes through live.py: from the file that now holds it, from
the pinned document that states it, as a stated convention - or, where it
records what an earlier stage of the work found and no script stores it,
quoted from the page as first written.

    python3 scripts/pages/agent_brief.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import DERIVED, ROOT, log, write_doc
import claims
import live

OUT = os.path.join(ROOT, "docs", "AGENT_BRIEF.md")
PAGE = "docs/AGENT_BRIEF.md"
THEN = "db51741"        # the page as last written by hand


def J(*p):
    return live.live_json(os.path.join(*p))


def main():
    F, obs = J(DERIVED, "landbrug.json"), J(DERIVED, "observing.json")
    places = J(DERIVED, "station_places.json")
    CL = claims.load()[0]
    SELF = []           # numbers carried as quotations of this page's own committed text

    def sq(shown):
        SELF.append(shown)
        return live.was(THEN, PAGE, shown)

    CONV = "the station seasonality convention this brief sets"
    z = live.stated("seasonality_z", 3, "3", CONV + ": the Rayleigh cut")
    AGRI = f"{F['agri_pct']:.1f}"
    hypoxia = claims.resolve(
        CL, "{read:DCE-STATMOD-2015:4|iltkoncentration er under hhv. 4 mg/L}", {})[0]

    text = f"""# Standing brief

Given to every agent working on this project, and to anyone contributing. It is short
because it is meant to be obeyed rather than admired.

---

## 1. Nothing is given

Every count carries a rule for what counts as **one**, and that rule is invisible by
the time the count is a number. Call it the **applefication assumption**. Point at a
deck of cards and ask *how many?* — one deck, four suits, fifty-two cards, {sq('fifty-two cards, @@ atoms. There')} atoms.
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
it. Never write "X is {AGRI}%" when X is a residual over products of norm coefficients.

| kind | what it means | example from this project |
|---|---|---|
| **measurement** | an instrument was in contact with the thing | near-bed oxygen from a sonde |
| **derived** | arithmetic on measurements | salinity, computed from conductivity + temperature |
| **estimator** | a statistic meant to approximate an estimand — **name both** | monthly median as a stand-in for monthly state |
| **residual** | total minus known parts; absorbs every error in the parts | the {AGRI}% agricultural attribution |
| **construction** | a count under an individuation rule someone chose | "{obs['sizes']['n']} water bodies", "{places['coverage']['series_stations']:,} stations" |
| **norm product** | a register count × a regulatory coefficient | *markoverskud*: livestock counts × excretion norms |
| **model output** | produced by a model, possibly calibrated to measurements | DK-QNP diffuse load over the ungauged area |
| **threshold class** | a continuum cut at a number | "hypoxia" as oxygen below {hypoxia} mg/l |

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
| mean-square ratio MSB/(MSB+MSW) | {sq('MSB/(MSB+MSW) | @@ |')} | **{sq('| 0 | **@@** | | ARI,')}** |
| ARI, {sq('| | ARI, @@ groups vs 84')} groups vs {sq('12 groups vs @@ | max 1.0')} | max {sq('84 | max @@ | **max 0.132**')} | **max {sq('@@** | | ARI between contiguity-constrained')}** |
| ARI between contiguity-constrained partitions | {sq('MSB/(MSB+MSW) | @@ |')} | **{sq('@@** | | ARI between *derived*')}** |
| ARI between *derived* partitions | {sq('@@** | | ARI between *derived*')} | **{sq('@@** | | annual minimum vs sampling')}** |
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
*year-round* and got **{sq('and got **@@/481, 282/480 and')}/{sq('and got **293/@@, 282/480 and')}, {sq('and got **293/481, @@/480 and 426/427**')}/{sq('and got **293/481, 282/@@ and 426/427** — all')} and {sq('got **293/481, 282/480 and @@/427** — all defensible')}/{sq('**293/481, 282/480 and 426/@@** — all defensible')}** — all defensible arithmetic on
different unstated rules, one of them arithmetically impossible.

**The station seasonality convention, from here on:**

> Classify on the Rayleigh statistic **Z = N·R²**, never on raw R.
>
> - **seasonal** — Z > {z} (about p < {live.stated("seasonality_p", 0.05, "0.05", CONV + ": exp(−Z) at the cut, the Rayleigh tail probability")}) *and* mean direction in June–September
> - **year-round** — Z ≤ {z} *and* N ≥ {live.stated("seasonality_min_n", 24, "24", CONV + ": two years of monthly observations, so the test had the power to reject")}, so the test had the power to reject
> - **neither** — everything else. **A station with too few observations is not
>   year-round; it is unclassified.**
>
> State the variable basis, since it changes the answer: on all nine variables,
> {sq('all nine variables, > @@')} / {sq('has **@@ stations with')} / {sq('@@. On `oxy_bed` alone,')}. On `oxy_bed` alone, {sq('`oxy_bed` alone, @@ /')} / {sq('alone, 357 / @@ / 699. **Why')} / {sq('@@. **Why Z and not')}.

**Why Z and not R.** R is {live.stated("rayleigh_single_r", 1, "1", "the mean resultant length of a single unit vector, by definition")} whenever a station has a single observation — the direction
is perfectly concentrated because there is only one of it. `oxy_bed` has **{sq('has **@@ with exactly')}
with exactly one observation**, and a raw-R rule with no minimum put all of them in the
"strongly seasonal" group, where they were {sq('where they were @@ of it and')} of it and {sq('it and @@ had three')} had three observations or
fewer. The statistic was measuring scarcity. **Z = N·R² fixes this without an arbitrary
cutoff**, because a single observation gives Z = {live.stated("rayleigh_single_z", 1, "1", "N·R² with N and R both one")} and fails on its own.

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
"""
    write_doc(OUT, text)
    log(f"wrote {os.path.relpath(OUT, ROOT)} - {len(SELF)} number(s) carried as self-quotation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
