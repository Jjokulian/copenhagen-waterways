#!/usr/bin/env python3
"""docs/AGENT_BRIEF.md - the standing brief given to every agent and contributor.

Most of the brief's numbers are examples of the rules it states: a published share,
two counts under an individuation rule, a threshold, two nulls this project once read
wrong, and the station seasonality convention with its counts. Each comes through
live.py: from the file that holds it, from a pinned document, as a stated convention,
or computed here. The seasonality counts are computed from the monthly station series
(docs/data/areas/stations_series.json and .bin) under the convention the brief sets,
and written to data/derived/agent_brief.json. The splits three drafts worked with are
quoted from the drafts as committed, inside a historical claim. Every assertion is a
checked claim (LIVE_NUMBERS.md section 11), registered in
data/manual/claims.d/w3-ea.json with what it rests on. What the brief once said and
could not justify is in docs/ARCHIVE.md, not here.

    python3 scripts/pages/agent_brief.py

Writes data/derived/agent_brief.json and docs/AGENT_BRIEF.md. Peak memory: the station
series file (a few MB) and one byte per station-month of every variable, held per
station.
"""
import array
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import DERIVED, ROOT, log, read_json, write_doc, write_json
import claims
import live

OUT = os.path.join(ROOT, "docs", "AGENT_BRIEF.md")
DATA = os.path.join(DERIVED, "agent_brief.json")
SERIES = os.path.join(ROOT, "docs", "data", "areas", "stations_series")
DRAFTS = "1f5c1c9"      # the hypothesis drafts as committed before the convention was set
C, B, E = live.claim, live.claim_begin, live.CLAIM_END

# The station seasonality convention this brief sets. An observation is one station-
# month in the series, placed on the circle by its calendar month.
Z_CUT = 3               # seasonal above, year-round at or below
MIN_N = 24              # year-round needs this many observations
SUMMER = (5, 6, 7, 8)   # calendar months counted from January as 0: June to September
RAW_R_CUT = 0.5         # the raw-R rule with no minimum that the convention replaces
CONV = "the station seasonality convention this brief sets"


def classify(months):
    """(class, N, R) for one station's calendar months (0 = January): the Rayleigh
    statistic Z = N·R² on unit vectors at the months, and the mean direction rounded
    to the nearest month."""
    n = len(months)
    c = sum(math.cos(2 * math.pi * m / 12) for m in months)
    s = sum(math.sin(2 * math.pi * m / 12) for m in months)
    r = math.hypot(c, s) / n
    z = n * r * r
    mean = round(math.atan2(s, c) / (2 * math.pi) * 12) % 12
    if z > Z_CUT and mean in SUMMER:
        return "seasonal", n, r
    if z <= Z_CUT and n >= MIN_N:
        return "year_round", n, r
    return "neither", n, r


def seasonality():
    """Classify every station in the monthly series under the convention, on all nine
    variables pooled and on `oxy_bed` alone, and count the raw-R rule it replaces.
    Written to data/derived/agent_brief.json."""
    if sys.byteorder != "little":
        raise live.Unjustified("agent_brief: the series is little-endian; this reader is not")
    meta = read_json(SERIES + ".json")
    raw = open(SERIES + ".bin", "rb").read()
    pooled, bed = defaultdict(lambda: array.array("B")), defaultdict(lambda: array.array("B"))
    for var in meta["variables"]:
        n, off = var["n"], var["offset"]
        st = array.array("H")
        st.frombytes(raw[off:off + 2 * n])
        mo = array.array("H")
        mo.frombytes(raw[off + 2 * n:off + 4 * n])
        for s, m in zip(st, mo):
            pooled[s].append(m % 12)
            if var["key"] == "oxy_bed":
                bed[s].append(m % 12)
    del raw

    def count(obs):
        out = {"stations": len(obs), "seasonal": 0, "year_round": 0, "neither": 0}
        for ms in obs.values():
            out[classify(ms)[0]] += 1
        return out
    oxy = count(bed)
    rows = [classify(ms) for ms in bed.values()]
    raw_r = [n for _, n, r in rows if r > RAW_R_CUT]
    oxy.update({"at_least_min_n": sum(1 for _, n, _ in rows if n >= MIN_N),
                "raw_r_group": len(raw_r),
                "raw_r_single": sum(1 for n in raw_r if n == 1),
                "raw_r_at_most_three": sum(1 for n in raw_r if n <= 3)})
    write_json(DATA, {
        "_what": "The station seasonality convention of docs/AGENT_BRIEF.md applied to the "
                 "monthly station series, by scripts/pages/agent_brief.py.",
        "rule": {"z_cut": Z_CUT, "min_n": MIN_N, "summer": "June-September",
                 "raw_r_cut": RAW_R_CUT,
                 "observation": "one station-month of the series, at its calendar month"},
        "all_nine": count(pooled), "oxy_bed": oxy})
    return live.live_json(DATA)


def main():
    J = lambda *p: live.live_json(os.path.join(*p))
    F, obs = J(DERIVED, "landbrug.json"), J(DERIVED, "observing.json")
    places = J(DERIVED, "station_places.json")
    sub = J(ROOT, "docs", "data", "areas", "partition_subspace.json")
    CL = claims.load()[0]
    sea = seasonality()
    allv, oxy = sea["all_nine"], sea["oxy_bed"]

    def was(file, locator):
        return live.was(DRAFTS, f"docs/hypodrafts/{file}", locator)

    z = live.stated("seasonality_z", Z_CUT, f"{Z_CUT}", CONV + ": the Rayleigh cut")
    n_min = live.stated("seasonality_min_n", MIN_N, f"{MIN_N}", CONV + ": two years of "
                        "monthly observations, so the test had the power to reject")
    AGRI = f"{F['agri_pct']:.1f}"
    hypoxia = claims.resolve(
        CL, "{read:DCE-STATMOD-2015:4|iltkoncentration er under hhv. 4 mg/L}", {})[0]
    msr = live.stated("msr_chance", 0.5, "0.5", "The chance value of the mean-square ratio "
                      "MSB/(MSB+MSW): under random labels both mean squares estimate the same "
                      "variance, so the ratio centres on one half. scripts/partition_score.py "
                      "states it and records a simulation at that value.")
    single = live.step("K-SUBSET-SHARE", oxy["raw_r_single"] / oxy["raw_r_group"] * 100)
    few = live.step("K-SUBSET-SHARE", oxy["raw_r_at_most_three"] / oxy["raw_r_group"] * 100)

    text = f"""# Standing brief

{C("C-EA-B-FOR", "Given to every agent working on this project, and to anyone contributing.")}
{C("C-EA-B-SHORT", "It is short because it is meant to be obeyed rather than admired.")}

---

## 1. Nothing is given

{C("C-EA-B-ONE", "Every count carries a rule for what counts as **one**, and that rule is "
   "invisible by the time the count is a number.")} Call it the **applefication
assumption**. {C("C-EA-B-DECK", "Point at a deck of cards and ask *how many?* — one deck, "
   "four suits, fifty-two cards, or however many atoms are in them. There is no answer "
   "until somebody has said what a one is.")}

So for any quantity you handle, three questions in order:

1. **What is the individuation?** What was treated as one thing, one kind, one member?
2. **Is it reasonable** for the use it is being put to?
3. **Is it stable?** — {C("C-EA-B-STABLE", "the only one with an empirical answer.")}

{C("C-EA-B-HIDES", "A number is where this hides best, because a number looks like the "
   "least theory-laden object in a dataset. Its theory happened upstream, at counting "
   "time, and nothing in the digit records it.")}

---

## 2. Say what kind of thing a quantity is

{C("C-EA-B-BROKEN", "**This project has broken this rule itself**: a mean-square ratio was "
   "labelled an intraclass correlation and read with that statistic's zero.")}
{C("C-EA-B-LABEL", f"When you name a quantity, label it. Never write \"X is {AGRI}%\" when X "
   "is a residual over products of norm coefficients.")}

| kind | what it means | example from this project |
|---|---|---|
| **measurement** | an instrument was in contact with the thing | {C("C-EA-B-EX-MEAS", "near-bed oxygen from a sonde")} |
| **derived** | arithmetic on measurements | {C("C-EA-B-EX-DERIVED", "salinity, computed from conductivity + temperature")} |
| **estimator** | a statistic meant to approximate an estimand — **name both** | {C("C-EA-B-EX-EST", "monthly median as a stand-in for monthly state")} |
| **residual** | total minus known parts; absorbs every error in the parts | {C("C-EA-B-EX-RESID", f"the {AGRI}% agricultural attribution")} |
| **construction** | a count under an individuation rule someone chose | {C("C-EA-B-EX-CONSTR", f"\"{obs['sizes']['n']} water bodies\", \"{places['coverage']['series_stations']:,} stations\"")} |
| **norm product** | a register count × a regulatory coefficient | {C("C-EA-B-EX-NORM", "*markoverskud*, whose manure term is livestock counts × excretion norms")} |
| **model output** | produced by a model, possibly calibrated to measurements | {C("C-EA-B-EX-MODEL", "DK-QNP diffuse load over the ungauged area")} |
| **threshold class** | a continuum cut at a number | {C("C-EA-B-EX-THRESH", f"\"hypoxia\" as oxygen below {hypoxia} mg/l")} |

{C("C-EA-B-COMPOUNDS", "Two compounds are especially dangerous and both occur here:")}

- {C("C-EA-B-COMP1", "**A residual of norm products, used as a model input, then correlated "
     "with that model's output** and reported as a finding. The correlation is "
     "structural.")}
- {C("C-EA-B-COMP2", "**A threshold class whose defining variable is deterministically "
     "coupled to another** — an oxygen concentration threshold is partly a thermometer, "
     "because solubility is a function of temperature and salinity.")}

---

## 3. Compute your null, never quote it

{C("C-EA-B-NULL", "A statistic's published null is the null of the model it was derived "
   "under, **not of the constraint you actually imposed.**")}
{C("C-EA-B-NULLS", "This project has quoted the wrong null itself. Two of the cases are "
   "recorded in the files its analyses write:")}

- {C("C-EA-B-NULL-MSR", "The mean-square ratio MSB/(MSB+MSW), reported as an intraclass "
     "correlation, was read as if chance were zero. Under random labels both mean squares "
     f"estimate the same variance, so its chance value is {msr}.")}
- {C("C-EA-B-NULL-ARI", "The adjusted Rand index reads zero as chance, but between two "
     "random *connected* partitions of the stations with the official group sizes, chance "
     f"is {sub['contiguous_null_ari']:.3f}: contiguity alone makes partitions agree.")}

{C("C-EA-B-DIRECTION", "Both came out above the zero that was quoted. A null's value is not "
   "guessable from the statistic's name, which is the whole argument for computing it "
   "rather than quoting it.")}

---

## 4. The rest

- {C("C-EA-B-R-WB", "**Water bodies are a model assumption, not a unit.** Do not aggregate "
     "into them. \"Denmark\" is not a closed system either.")}
- {C("C-EA-B-R-ABSENT", "**An absent dimension makes a hypothesis unscoreable, not "
     "refuted.** Do not let \"no data\" become \"no effect\".")}
- {C("C-EA-B-R-FLAG", "**Flag, never delete.** Outliers are the only observable sample from "
     "the error process. Trimming them destroys the sole estimator of the archive's own "
     "error rate while making it look cleaner.")}
- {C("C-EA-B-R-DIST", "**Say what a number is a distribution of.** A single figure asserts "
     "that everything it summarises was one kind of thing — and a distribution of the "
     "wrong thing is as uninterpretable as a mean.")}
- {C("C-EA-B-R-FOUND", "**The data you have found is not all there is.** `fetch_oda.py` "
     "lists an ODA topic, `iltkor`, with no file on disk, and does not list the eelgrass, "
     "macroalgae and bottom-fauna topics at all. Independence between sources matters "
     "more than volume: a derived channel - salinity from conductivity and temperature, "
     "oxygen saturation from oxygen, temperature and salinity - is not an independent "
     "measurement.")}
- {C("C-EA-B-R-FAB", "**Do not fabricate.** \"Not established\" is a valid and expected "
     "answer. A source you cannot verify is a source you say you could not verify.")}
- {C("C-EA-B-R-STEEL", "**Steelman before you report a failure.** A bad argument in a "
     "document does not mean there are no good ones elsewhere. Ask what the strongest "
     "version of the case would be, look for it, and say whether you looked.")}
  {C("C-EA-B-R-CIRC", "This project published a circularity finding and had to narrow it "
     "within the hour: the authors qualified the figure themselves on the next page, and "
     "a paired-catchment study existed that nobody here had read.")}

## 4b. Stated conventions

{C("C-EA-B-CAT", "A category everyone uses and nobody defines is the applefication failure "
   "in its purest form.")}
{C("C-EA-B-DRAFTS", "Three drafts in this project split the stations into *summer-peaked* "
   "and *year-round* and worked with three different splits: "
   f"**{was('I1.md', 'exist (@@ summer-peaked,')}/{was('I1.md', 'summer-peaked, @@ year-round,')}**, "
   "a figure on file that one draft built on; "
   f"**{was('G1.md', '\"summer-peaked\"): **@@ summer-peaked vs')}/{was('G1.md', 'summer-peaked vs @@ year-round**, the')}**, "
   "on another draft's own rule; and "
   f"**{was('L3.md', 'Rayleigh classification (@@ summer /')}/{was('L3.md', 'summer / @@ year-round) is')}**, "
   "on a third's Rayleigh classification.")}
{C("C-EA-B-L3", f"The last is larger, taken together, than the {oxy['at_least_min_n']} "
   f"`oxy_bed` stations with at least {n_min} observations, so it was reached with a lower "
   "minimum or none.")}

**The station seasonality convention, from here on:**

> {C("C-EA-B-CONV-Z", "Classify on the Rayleigh statistic **Z = N·R²**, never on raw R.")}
>
> - {C("C-EA-B-CONV-SEAS", f"**seasonal** — Z > {z} (about p < " + live.stated(
    "seasonality_p", 0.05, "0.05", CONV + ": exp(−Z) at the cut, the Rayleigh tail "
    "probability") + ") *and* mean direction in June–September")}
> - {C("C-EA-B-CONV-YEAR", f"**year-round** — Z ≤ {z} *and* N ≥ {n_min}, so the test had "
    "the power to reject")}
> - {C("C-EA-B-CONV-NEITHER", "**neither** — everything else. **A station with too few "
    "observations is not year-round; it is unclassified.**")}
>
> {C("C-EA-B-BASIS", "State the variable basis, since it changes the answer: on all nine "
  f"variables, {allv['seasonal']} / {allv['year_round']} / {allv['neither']}. On `oxy_bed` "
  f"alone, {oxy['seasonal']} / {oxy['year_round']} / {oxy['neither']}.")}

**Why Z and not R.** {C("C-EA-B-WHYR", "R is " + live.stated(
    "rayleigh_single_r", 1, "1", "the mean resultant length of a single unit vector, by "
    "definition") + " whenever a station has a single observation — the direction is "
    "perfectly concentrated because there is only one of it.")}
{C("C-EA-B-SCARCITY", f"`oxy_bed` has **{oxy['raw_r_single']} stations with exactly one "
   "observation**, and a raw-R rule with no minimum put all of them in the \"strongly "
   f"seasonal\" group, where they were {single:.0f}% of it and {few:.0f}% had three "
   "observations or fewer.")}
{C("C-EA-B-FIX", "The statistic was measuring scarcity. **Z = N·R² fixes this without an "
   "arbitrary cutoff**, because a single observation gives Z = " + live.stated(
    "rayleigh_single_z", 1, "1", "N·R² with N and R both one") + " and fails on its own.")}

The general rule this is an instance of:

> {C("C-EA-B-RULE", "**If a category decides a result, its definition is part of the "
  "result.** Write it down, state the parameter that moves it, and report what the answer "
  "is under the alternatives. A category used by three analyses under three unstated "
  "rules is not one category.")}

## 5. What may be emitted

{C("C-EA-B-EMIT", "A coefficient, at a stated level of organisation, against a stated null, "
   "for a named functional, at a stated point in the accumulation of measure-spaces. "
   "**Five qualifiers, none droppable.** Drop any and you have produced a verdict, which "
   "is a different kind of object than this procedure can make.")}

{C("C-EA-B-NOTEMIT", "Not emittable: *\"X is real\"*, *\"X is not real\"*, *\"the result is "
   "in\"*.")} {C("C-EA-B-NOREFERENT", "Those are not false — they have no referent, because "
   "the space of groupings and functionals is open.")}

Full method: [statistical-methods](https://github.com/Jjokulian/statistical-methods).

---

*{C("C-EA-B-FOOT", "Generated by `scripts/pages/agent_brief.py`, which computes the "
   "seasonality counts from the monthly station series and writes them to "
   "`data/derived/agent_brief.json`.")}*
"""
    try:
        write_doc(OUT, text)
    except (live.Unjustified, claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
