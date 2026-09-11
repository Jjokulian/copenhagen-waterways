#!/usr/bin/env python3
"""Generate docs/SETTLE.md - the experiment that would end the argument.

The prose is this page's, moved here from the committed markdown. Numbers that no
script in the repo stores - the rainfall statistics, the costing, the staging - are
carried as quotations of the page's committed text, written [[...]] below and
rendered by live.was(): their construction says the site once said this, not
that it was right. The design's own choices are stated with their reasons
(live.stated), and counts the repo does hold are read live: {{name}} below.

    python3 scripts/pages/settle.py
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common import DERIVED, ROOT, log, read_json, write_doc, write_json
import live

PAGE = "docs/SETTLE.md"
COMMIT = "aa3f2b5"          # the committed page the unstored numbers are quoted from
OUT = os.path.join(DERIVED, "settle.json")

TEXT = r"""# Fingerprinting Denmark

**The experiment that would end the argument, written so that both sides can commit to
it before it runs.**

Everything else on this site is an audit: it takes numbers that exist and asks what
they are estimators of. This page is the opposite. It is a design for producing
numbers that do not exist yet, aimed at the one question the whole dispute turns on
and nobody has ever measured directly:

> **When Danish fields receive slurry and then rain, what reaches the water — and
> whose is it?**

[SENSING.md](SENSING.md) constructs the instrument: the fingerprint that separates a
pig from a person from a road, and the two-tier network that could carry it.
[`X23`](EXPERIMENTS.md) is the entry in the register. **This page is the protocol** —
what is claimed, what would refute it, how many catchments and how many storms, and
the rules that have to be fixed before the first sampler is bolted to a culvert.

---

## 1. The {{hypotheses}} hypotheses, stated so they can lose

The point of writing them out is that each makes a different prediction about the same
measurements, so the data can pick.

| | Claim | Predicts |
|---|---|---|
| **The soil reactor** | The field consumes the payload. Labile carbon is respired, ammonium nitrifies, and what leaves is mobile nitrate | Faecal markers stay near baseline through the spreading window. Nitrate rises seasonally, smoothly, with drainage. No relationship between marker peaks and livestock density |
| **The bypass** | Preferential flow, tile drains and rain onto fresh slurry deliver the payload close to intact | Marker and copper peaks within days of spreading, **scaling with livestock density**, concentrated in the rising limb of storms |
| **The regime** | Both are true, in different conditions. The bypass opens only when the ground is frozen, saturated or tile-drained, and closes otherwise | Marker peaks appear at **some** sites and not others, predicted by soil type, drainage and antecedent wetness rather than by livestock density alone |

**The soil reactor is the outcome that would embarrass this project**, since much of its argument
leans on the payload mattering. It is stated first on purpose, and the publication rule
below is written so that it cannot be quietly dropped.

---

## 2. What the calendar does for us

The manipulation already exists and is applied nationally: Danish rules forbid
spreading through the autumn and winter and open a window in spring. So the experiment
is **before-after on a fixed national schedule**, with a within-year control window
that needs no permission from anyone.

And the events can be counted in advance. From the [[From the @@-year hourly]]-year hourly rainfall record used
elsewhere in this project, over Copenhagen, February–April:

| | Median days per season | Range |
|---|---:|---:|
| ≥ [[|---|---:|---:| | ≥ @@ mm in a]] mm in a day | **[[a day | **@@** | 11–35 |]]** | [[| **21** | @@ | | ≥]] |
| ≥ [[| **9** | 2–1@@ | | ≥ 10]] mm in a day | **[[a day | **@@** | 2–15 |]]** | [[| **9** | @@ | | ≥]] |
| ≥ [[2–15 | | ≥ @@ mm in a day]] mm in a day | **[[|---|---:|---:| | ≥ @@ mm in a]]** | [[@@ | **That is the sample]] |

**That is the sample size, and it is the reason the design works.** A sampler on a
[[sampler on a @@ trigger catches something]] trigger catches [[five-millimetre trigger catches @@ in a spreading]] in a spreading season and a
comparable number in the autumn control window — enough for a paired comparison within
a single year, at a single site, without waiting a decade. *Caveat carried from the
source:* a reanalysis grid cell understates extremes, so the ≥[[extremes, so the ≥@@ mm row is a]] mm row is a floor.

---

## 3. The design

**Paired catchments, matched on everything except the thing under test.**

- **{{pairs}} pairs** — {{catchments}} catchments — matched on soil type, drainage class, area and slope,
  contrasted on **livestock density** from the national register. Small headwater
  catchments, so a signal is not diluted to nothing before it reaches the sensor.
- **Both tiers at every site**: continuous stage, turbidity, conductivity, temperature
  and fDOM; an autosampler on a flow-and-turbidity trigger.
- **{{windows}} windows a year**: the spreading window (February–April) and an autumn control
  window when spreading is forbidden. Same sites, same triggers, same laboratory.
- **End members sampled directly**: slurry from the tanks in each catchment, effluent
  from any plant in it, road gully sediment, and soil. **No conversion ratio is taken
  from the literature** — every one is measured on the material that is actually there.
- **{{years}} full years.** One to establish the ratios and shake out the fouling, one to
  answer the question.

**What is analysed per event:** faecal sterols with the herbivore ratio,
host-specific microbial markers, crAssphage, acesulfame, one veterinary residue,
copper and zinc, COD and BOD, total and dissolved N and P, and δ¹⁵N with δ¹⁸O of
nitrate. Discharge at the same minute, or it is a concentration and not a load.

---

## 4. The decision rules, fixed before the first sample

These are the whole point of the page. A rule written afterwards is a story.

1. **The bypass is accepted** if faecal-marker load in the spreading window exceeds the autumn
   control window by a factor stated in advance at **{{threshold}} or more of the
   high-density sites**, and the effect scales with livestock density across the
   {{pairs_word}} pairs.
2. **The soil reactor is accepted** if marker loads in the two windows are indistinguishable at the
   great majority of sites and nitrate is the only determinand that moves.
3. **The regime is accepted** if the effect is present at some sites and absent at others *and*
   is predicted by soil, drainage or antecedent wetness better than by density.
4. **The result is published whichever way it falls**, in full, with the raw series —
   and the pre-registration says so before the money is spent. **If the soil reactor wins, this
   project's own emphasis was wrong and the page saying so will carry that sentence.**
5. **No composite index is reported without the series it came from**, and no residual
   is named after a source. That is the failure this whole site documents; reproducing
   it here would be unforgivable.

---

## 5. What would invalidate the experiment rather than answer it

Written down in advance, because each of these has ruined a monitoring programme
somewhere:

- **Fouled sensors reading confidently.** Servicing schedule and co-location against a
  reference instrument, or the continuous tier is decoration. This is [`X16`](EXPERIMENTS.md).
- **Decayed DNA.** Microbial markers fall away in days, so a marker absence at a site
  visited late is not evidence of absence. The sterols, which persist, are the check.
- **Unmeasured end members.** If the slurry in *these* tanks was never sampled, every
  fraction is a guess with a decimal point on it.
- **Storm-chasing bias.** Triggers are set in advance and left alone. An operator who
  decides which storms are interesting has destroyed the sample.
- **Catchments matched on the wrong thing.** If the high-density catchments are also
  the sandy ones, the design has confounded exactly what it set out to separate — and
  the pairing has to be published so somebody else can say so.

---

## 6. What it costs, and how it could be built

From the bill of materials in [SENSING.md](SENSING.md), at stated prices rather than
quotations:

**The purchase order is in [SENSING.md](SENSING.md)** — every sensor, an example part
of its class, and what to expect to pay. The short version: a node is [[node is @@ DKK without]] DKK
without the fluorometer and [[fluorometer and @@ with it,]] with it, and **the sensors are not the
expensive part. The laboratory bottles are** — [[are** — @@ DKK each,]] DKK each, and they are the
line that cannot be economised without losing the attribution the design exists for.

| Phase | What | Stated cost |
|---|---|---:|
| **Pilot** — one season, [[one season, @@ pairs |]] pairs | [[pairs | @@ nodes with]] nodes with fDOM, [[with fDOM, @@ samplers,]] samplers, ~[[8 samplers, ~@@0 bottles, servicing]] bottles | **~[[bottles | **~@@ M DKK** | |]] M DKK** |
| **The experiment** — {{years_n}} years, {{pairs}} pairs | [[12 pairs | @@ nodes, 8 samplers,]] nodes, [[reaches the sea | ~@@]] samplers, ~[[samplers, ~@@ bottles, servicing]] bottles, servicing | **~[[bottles, servicing | **~@@ M DKK** | |]] M DKK** |
| **The standing network afterwards** | a node on every outlet that reaches the sea | ~[[the sea | ~@@ M DKK of hardware]] M DKK of hardware |

**The pilot is inside the reach of a foundation, a university department, or a
crowdfunded association.** The full experiment is the cost of one junction rebuild. The
comparison that matters is not to a research budget: it is to a national nitrogen
programme costing [[programme costing @@ and producing]] and producing **no test**.

---

### The proof of concept, which tests the instrument and not the hypothesis

**One pair of catchments, one spreading season, and a deliberately narrow question.**
The distinction matters more than the money: a single pair cannot answer whether the
payload reaches Danish water — the sample is one pair and the result would be a number
people fight over. What it *can* do is establish that the method works, which is what
has to be true before anybody buys {{catchments}} of anything.

**What it has to prove, and the go/no-go on each:**

| | Passes if | Fails if |
|---|---|---|
| **A cheap node survives** | one node returns a continuous record through a Danish February, with gaps that are explainable | the enclosure floods, the panel ices, or the radio drops the winter |
| **Its readings mean something** | co-located against a reference sonde, turbidity and EC track it within a stated tolerance and the drift is characterisable | drift is larger than the seasonal signal, in which case the continuous tier is a trigger only and must be described as one |
| **The trigger catches events** | the sampler fires on the rising limb and fills bottles across the storm, unattended, [[the storm, unattended, @@ | it fires]] | it fires on noise, or misses the events the rain record says happened |
| **The panel discriminates *here*** | the sterol ratio and host markers separate this catchment's slurry from its sewage effluent and from its soil | **this is the one that kills the national design.** If the end members are not separable in one Danish catchment, {{pairs_word}} pairs will not fix it |
| **The chain closes** | a reading taken at a culvert appears in a public series with its calibration state attached | anything in the path needs a person to copy a file |

**Note the fourth row.** It is the only test whose failure means *do not build the
national network*, and it costs [[and it costs @@ to run. Everything]] to run. Everything else
on this page is downstream of it, which is an argument for doing it first and alone.

**What it costs, item by item:**

| | | DKK |
|---|---|---:|
| [[DKK | |---|---|---:| | @@ nodes with fDOM |]] nodes with fDOM | one high-density catchment and its match | [[its match | @@ | | 1]] |
| [[@@ automatic sampler | rotated]] automatic sampler | rotated between the two, or fixed on the high-density one | [[high-density one | @@ | | Calibration]] |
| Calibration standards, spares, mounts | the shared kit, smallest version | [[smallest version | @@ | | Reference]] |
| Reference sonde for co-location | **borrowed** from a utility or a department, which most will lend for a season | [[lend for a season | @@]], or [[@@ to buy | | End-member]] to buy |
| End-member samples — [[samples — @@ slurry tanks,]] slurry tanks, [[plant effluent, @@ road gully,]] plant effluent, [[plant effluent, @@ road gully,]] road gully, [[road gully, @@ soils |]] soils | full fingerprint panel on each. **This is the row that decides the fourth test** | [[fourth test** | @@ | | Event]] |
| Event bottles — [[Event bottles — @@ events ×]] events × [[events × @@ | full panel]] | full panel on [[events × @@ | full panel]] of them, cheap determinands on the rest | [[the rest | @@ | | Servicing,]] |
| Servicing, travel, a server | one person, [[| one person, @@, a small]], a small VM | [[small VM | @@ | | **Total**]] |
| **Total** | one pair, one season, one person | **[[person | **@@ DKK** | **Which]] DKK** |

**Which is a used car, not a house** — and it is the number that matters, because it
is the one somebody can actually decide to spend. The full experiment is only worth
funding if this comes back clean, and if it does not, the money saved is the whole
[[is the whole @@. **A staged]].

**A staged path, with a decision at each step** — and it is
[dialable on a map](network.html), where each preset below reproduces the row beside
it:

| Stage | Scope | Cost | The question it answers |
|---|---|---:|---|
| **`0` — one node** | a single stream, no sampler | [[no sampler | @@ | does the]] | does the hardware survive and report? |
| **`1` — proof of concept** | one pair, one season, one sampler | [[one sampler | @@ | does the]] | does the method discriminate, here? |
| **`2` — regional** | [[— regional** | @@, both windows]], both windows | [[both windows | @@ M | is]] M | is the effect visible at all, and how variable? |
| **`3` — the experiment** | {{pairs_word}} pairs, {{years_lower}} years | [[two years | @@ M | which]] M | which of the {{hypotheses}} hypotheses is right |
| **`4` — the network** | every outlet that reaches the sea | [[the sea | @@ M + operating]] M + operating | the same answer everywhere, permanently |

**No stage is wasted if the next one is never funded.** Stage 0 is a real series from a
real stream. Stage 1 is a publishable methods result either way. Stage 2 is a regional
finding. That property is not an accident of the costing — it is the reason to stage
it like this rather than to write one large proposal that has to be accepted whole.

### The number, put beside things that are not science

Because the figure is easy to lose next to a research budget, here it is next to
things people actually price:

| | Stated cost |
|---|---:|
| The **pilot** — [[The **pilot** — @@, one season]], one season | ~[[season | ~@@ M DKK, the]] M DKK, the price of a small flat outside the cities |
| The **experiment that settles it** — {{pairs}} pairs, {{years_lower}} years | **[[years | **@@ M DKK, the]] M DKK, the price of a cheap house** |
| The **standing national network**, hardware | ~[[network**, hardware | ~@@ M DKK | |]] M DKK |
| One bored street shot, from the retrofit costing on this site | [[this site | @@ M DKK |]] M DKK |

**So the decisive experiment costs about what a house costs, and the capital for a
national network costs about what a good house in Copenhagen costs.** That is the
honest headline and it should be uncomfortable: the argument has run for [[run for @@, and]],
and the measurement that would settle a central part of it has never been bought at a
price a single wealthy person could pay.

**But do not mistake the capital for the programme.** Hardware is the cheap half and
saying otherwise is how these schemes die:

- **Servicing.** [[die: - **Servicing.** @@ nodes at four]] nodes at [[800 nodes at @@ is on the]] is on the order of **[[the order of **@@ M DKK a year**]] M DKK a
  year** — which is to say [[which is to say @@, permanently. A sensor]], permanently. A sensor that nobody
  visits produces confident wrong numbers, which is worse than no sensor.
- **Laboratory.** The tier-[[The tier-@@ bottles at]] bottles at [[bottles at @@ DKK each]] DKK each are the largest single
  line in the experiment budget, and the only one that cannot be economised without
  losing the attribution.
- **Custody.** Somebody has to keep the archive, the calibration histories and the
  pre-registration for a decade, and that is a job rather than a server.

So: **a house to find out, and a few salaries a year to keep knowing.** The first
number is startlingly small. The second is the one a proposal has to be honest about,
because it is the one that gets cut in [[cut in @@ and takes]] and takes the series with it.

### And the whole of it?

This page prices one question. The obvious next one is what it would cost to settle
the *field* — not the faecal channel alone, but enough of the {{designs}} designs in
[EXPERIMENTS.md](EXPERIMENTS.md) to leave the Danish sea argument with measurements
where it currently has models. Adding up what this project has actually costed, and
marking clearly what it has not:

| Block | What it buys | Stated cost |
|---|---|---:|
| **This experiment** | whether the payload reaches the water, and whose it is | [[it is | @@ M | |]] M |
| **The standing stream network** | the same question everywhere, permanently, no extrapolation | [[no extrapolation | @@ M hardware |]] M hardware |
| **Instrumenting the [[**Instrumenting the @@ largest overflow]] largest overflow structures** | flow rather than event counts — the largest single uncertainty on this site | ~[[this site | ~@@ M | | **The]] M |
| **The cheap marine tier** — `X14`, `X15`, `X16` | oxygen and temperature at many points instead of monthly at few | [[at few | @@ M | |]] M |
| **The missing instruments** — `X19`, `X20` | a *fedtemøg* index and a structured record of what people have watched for [[watched for @@. Three]]. [[forty years. @@ | small]] | small — a panel and a protocol |
| **The desk work** — `X8`, `X21`, `X22` | analyses on data that already exists and has never been run | **nothing but time** |
| **A trials portfolio** — the meta-solution in [PROGRAMME.md](PROGRAMME.md) | whether the interventions work, in named places, reversibly | [[places, reversibly | @@ M | **Capital,]] M |

**Capital, in the order of [[the order of @@ M DKK.** Which]] M DKK.** Which is a large villa, or a small apartment
building, or about one kilometre of urban motorway — and it is *not* the same as an
upper-middle-class house: that figure buys the decisive single experiment, not the
programme. Plus **[[programme. Plus **@@ M a year**]] M a year** to service, sample and keep custody, which is the
number that decides whether any of it survives to be a time series.

**And three honest deductions from that total.**

- **Ship time is not in it.** The autumn benthic extension and anything offshore needs
  a vessel and an institution, and this project cannot price either.
- **Some of it cannot be bought at all.** {{unscoreable}} of the {{mechanisms}} mechanisms in the register
  are unscoreable because the deciding measurement has no column anywhere; money buys
  the instrument, not the decades of record it should have been collecting.
- **And the cheapest block is the one nobody has done.** {{desk}} designs need no
  fieldwork and no funding — the data exists and the analysis has never been run. If
  the argument is that this is all too expensive, that block is the counter-example
  sitting in the open.

---

## 7. Who could do which part

| | Can do |
|---|---|
| **One person with a culvert and a soldering iron** | A node, a year of a real series from one stream, and the demonstration that it works |
| **A local association or a school** | A pair — one high-density catchment and its match — which is a whole experiment in miniature |
| **A municipality or a water utility** | The samplers and the laboratory line, which is the half that needs an institution |
| **A university group** | The end-member sampling and the isotope work, and the pre-registration that makes the rest admissible |
| **Anyone at all** | Hold the pre-registration to its publication rule when the result is inconvenient |

**Nothing above needs a change in the law, a data agreement, or anybody's permission
except the landowner's at each culvert.** That is unusual in this field and it is the
reason this page exists.

---

## 8. What it settles, and what it does not

**Settles.** Whether the payload reaches the water, in what quantity, in what season,
under what conditions, and whose it is — measured rather than modelled, at the point
where inland water becomes coastal water. Whether the spreading calendar is visible in
a stream. Whether the account's single channel is missing a second one, and by roughly
how much.

**Does not settle.** What the arriving material then does in the sea: that is the next
experiment and it is harder. Nor anything about constituents outside the analysed list.
Nor the marine oxygen question, which has [its own designs](EXPERIMENTS.md).

> **Why it would end the argument rather than extend it.** Every disputed number in
> Danish nutrient policy is a modelled quantity defended by the people who model it.
> This produces a measured quantity, at named places, on dates, with the raw series
> published and the decision rule fixed in advance — so the result is available to
> somebody who does not trust either party. **That is the only kind of number that
> ends a [[ends a @@ disagreement**, and]] disagreement**, and the striking thing is how cheap it is.
"""


HYPOTHESES = ("the soil reactor", "the bypass", "the regime")
R_PAIRS = ("The design's choice, fixed before the experiment: enough matched pairs to see "
           "whether the effect scales with livestock density across soil and drainage "
           "types, at the cost set out in section 6.")
R_CATCH = "Two catchments per pair, one of high and one of low livestock density."
R_YEARS = ("One year to establish the conversion ratios and shake out the fouling, one to "
           "answer the question.")
R_WINDOWS = ("The spreading window and an autumn control window, when spreading is forbidden, "
             "at the same sites with the same triggers.")
R_THRESH = ("Fixed before the first sample, so that the acceptance rule cannot be tuned to "
            "the result.")


def values():
    """The live values the page reads, by name. Counts of registers this page
    describes are taken from them and stored; the design's choices are stated."""
    e = read_json(os.path.join(DERIVED, "experiments.json"))
    write_json(OUT, {"_what": "Counts docs/SETTLE.md states, taken from the registers they "
                              "describe by scripts/pages/settle.py.",
                     "designs": len(e["experiments"]),
                     "desk_designs": sum(1 for x in e["experiments"] if x.get("scale") == "desk"),
                     "hypotheses": len(HYPOTHESES)})
    c = live.live_json(OUT)
    t = live.live_json(os.path.join(DERIVED, "triage.json"))
    return {
        "pairs": live.stated("settle_pairs", 12, "12", R_PAIRS),
        "pairs_word": live.stated("settle_pairs", 12, "twelve", R_PAIRS),
        "catchments": live.stated("settle_catchments", 24, "24", R_CATCH),
        "years": live.stated("settle_years", 2, "Two", R_YEARS),
        "years_lower": live.stated("settle_years", 2, "two", R_YEARS),
        "years_n": live.stated("settle_years", 2, "2", R_YEARS),
        "windows": live.stated("settle_windows", 2, "Two", R_WINDOWS),
        "threshold": live.stated("settle_threshold", 2 / 3, "two thirds", R_THRESH),
        "hypotheses": f"{c['hypotheses']}", "designs": f"{c['designs']}",
        "desk": f"{c['desk_designs']}",
        "unscoreable": f"{t['classes']['unscoreable']['n']}", "mechanisms": f"{t['n_triaged']}",
    }


def render(text, v):
    # [[phrase with @@]]: a located reference, the value read out of git
    text = re.sub(r"\[\[(.+?)\]\]", lambda m: live.was(COMMIT, PAGE, m.group(1)), text)
    return re.sub(r"\{\{(\w+)\}\}", lambda m: v[m.group(1)], text)


def main():
    write_doc(os.path.join(ROOT, PAGE), render(TEXT, values()))
    log(f"wrote {PAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
