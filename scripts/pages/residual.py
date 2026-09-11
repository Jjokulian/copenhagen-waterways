#!/usr/bin/env python3
"""Generate docs/RESIDUAL.md - the number that was never measured.

The page was written by hand and still is: the prose below is the page, edited here,
and docs/RESIDUAL.md is output. Every number in it is read from data, a calculation,
a pinned document or a stated value, and every assertion is a checked claim
(LIVE_NUMBERS.md section 11), registered in data/manual/claims.d/w1-lr.json with what
it rests on. The worked analogy's figures are stated values with their reasons in
data/manual/claims.d/politics.json; the atomic masses are stated in w1-lr.json. What
the page once said and could not justify is in docs/ARCHIVE.md, not here.

Usage:  python3 scripts/pages/residual.py
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import ROOT, log, write_doc
import claims as _claims
import live

OUT = os.path.join(ROOT, "docs", "RESIDUAL.md")
C, B, E = live.claim, live.claim_begin, live.CLAIM_END
_REG = {}


def _cl():
    if "d" not in _REG:
        _REG["d"] = _claims.load()[0]
    return _REG["d"]


def P(name):
    """A value the page chooses for its worked analogy, declared with its reason."""
    p = _cl()["params"]["politics_" + name]
    return live._mk(p["value"], ["stated", "politics_" + name, p["reason"]])


def S(name):
    """A stated value this page's fork declared, with its reason."""
    p = _cl()["params"][name]
    return live._mk(p["value"], ["stated", name, p["reason"]])


def RD(sid, value, phrase):
    """A number read from a pinned document, refused unless the pinned copy holds the
    phrase (tags set aside, as the claims register compares it)."""
    d = _cl()
    if _claims._flat(phrase) not in _claims._flat(_claims.pin_text(d, sid)):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    return live._mk(value, ["reading", sid, "phrase", phrase, _claims._meta(d, sid)])


def QN(commit, file, shown, value):
    """A number a data file held at a past commit, verified against git. A quotation:
    it stands only inside a historical claim."""
    r = subprocess.run(["git", "show", f"{commit}:{file}"], cwd=ROOT, capture_output=True)
    if r.returncode or shown not in r.stdout.decode("utf-8", "replace"):
        raise live.Unjustified(f"{file} at {commit} does not contain '{shown}'")
    return live._mk(value, ["quote", commit, file, shown])


def J(*parts):
    return live.live_json(os.path.join(ROOT, *parts))


def render():
    diff = J("data", "manual", "monitoring.json")["diffuse_load"]
    ci = J("data", "derived", "currents_index.json")
    ct = J("data", "derived", "currents_transport.json")
    fa = J("data", "derived", "floodalign.json")
    fg = J("data", "derived", "floodgap.json")
    geo = J("data", "derived", "floodmaps", "_georef.json")
    prog = J("data", "derived", "programme.json")
    NP = J("data", "manual", "nitrogen_pathways.json")

    # The nitrogen worked example.
    S696 = RD("DANVA-2024", 69.6, "69,6 %")
    CUT = RD("DCE-STATMOD-2015", 25,
             "fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration")
    meas, mod = diff["area_measured_pct"], diff["area_modelled_pct"]
    ru = diff["retention_uncertainty_pct_points"]
    paths = NP["pathways"]
    quant = [p for p in paths if p["lo"] is not None]
    n_all = live.live(len(paths), NP._f, "pathways.n")
    n_unq = live.live(len(paths) - len(quant), NP._f, "pathways.n_unquantified")
    # the ceiling on agriculture's share, as scripts/causation.py computes it: the
    # land-based term's upper bound times the published share, over the lower bound
    # of everything enumerated - a denominator that can only grow
    land_hi = sum(p["hi"] for p in paths if p["pathway"].startswith("Danish land via"))
    tot_lo = sum(p["lo"] for p in quant)
    ceil = land_hi * S696 / 100 / tot_lo * 100

    # The shop.
    head, turn = P("shop_headline_gbp_bn"), P("shop_turnover_gbp")
    shr, err = P("shop_shrinkage_gbp"), P("shop_error")
    e_gbp = turn * err
    alt = P("residual_alt_cut_pct")

    # Protein and melamine.
    PROT = RD("FAO-2003-PROTEIN", 16, "was found to be about 16 percent")
    mc, mh, mn = S("lr_mass_c"), S("lr_mass_h"), S("lr_mass_n")
    MEL = live.step("K-LR-MASSFRAC", 6 * mn / (3 * mc + 6 * mh + 6 * mn) * 100)   # C3H6N6
    KIDS = RD("WIKI-MILK-2008", 300000, "300,000 affected children were identified")
    HOSP = RD("WIKI-MILK-2008", 54000, "among which 54,000 were hospitalized")

    # The flood model, now and at the commits the page describes.
    sheets = prog["flood_sheets"]["total"]
    shifts = [c for v in fa["shifts_m"].values() for c in v]
    s_lo, s_hi = min(shifts), max(shifts)
    before = QN("2f0d9c7", "data/derived/floodgap.json",
                '"flooded_over_water_km2": 1.556', 1.556)
    after = QN("9406c9b", "data/derived/floodgap.json",
               '"flooded_over_water_km2": 1.212', 1.212)
    now = fg["flooded_over_water_km2"]
    nb = geo["norrebro"]
    nb_flat = "norrebro" in list(fa["unconstrained"])

    flush = ci["retention"]["koege_bugt"]["flush_days_20km"]
    sydfyn = ci["retention"]["sydfynske"]["flush_days_20km"]
    best = max(ct["lag"], key=lambda r: r["vs_baseline_pp"])
    lag_lo = min(r["lag_h"] for r in ct["lag"])
    lag_hi = max(r["lag_h"] for r in ct["lag"])
    years = ct["n_hours"] / (365.25 * 24)

    def Er():
        return f"{err * 100:.0f}%"

    if nb_flat and "control_points" in nb:
        norrebro = ("- " + C("C-LR-R-OWN-NORREBRO", "**The Nørrebro flood sheet.** Every attempt "
                    "to correlate it against a neighbour came out flat. It has since been placed "
                    f"from {nb['control_points']} control points a reader supplied, with a "
                    f"standard error of {nb['standard_error_m']:.0f} m, but it is still the one "
                    f"sheet not known to be consistent with the other {sheets - 1}, and it is "
                    "marked as such."))
    elif nb_flat:
        norrebro = ("- " + C("C-LR-R-OWN-NORREBRO", "**The Nørrebro flood sheet.** Every attempt "
                    "to correlate it against a neighbour came out flat. It has no control points "
                    f"either. It is the one sheet not known to be consistent with the other "
                    f"{sheets - 1}, and it is marked as such."))
    else:
        norrebro = ("- " + C("C-LR-R-OWN-NORREBRO", "**The Nørrebro flood sheet.** It once "
                    "correlated with no neighbour; it now does, and is no longer the exception."))

    return f"""# The number that was never measured

Written by hand, and generated only so that every number and every assertion in it
carries its chain: the prose is kept in `scripts/pages/residual.py`. {B('C-LR-R-INTRO')}This page
explains one idea, and it is the idea the rest of this site keeps running into. Nitrogen
is the worked example. The idea is not about nitrogen, and you do not need to care about
Denmark to use it.{E}

---

## A shop at closing time

A supermarket wants to know how much stock it lost to shoplifting last year.

{B('C-LR-R-SHRINKAGE')}Nobody can count shoplifting. By its nature it is the thing that happens
when no one is recording. So the shop does the only thing available: it works out what
*should* be on the shelves from its delivery records and its till records, counts what is
*actually* there, and calls the gap **shrinkage**.{E}

{B('C-LR-R-HEADLINE')}Shrinkage is a real, useful, carefully produced number. It is also easy
to picture it in a headline as *"shoplifting cost retailers £{head:.1f}bn"* - a figure this page
makes up for the example.{E}

Look at what happens in that sentence. {C('C-LR-R-LIST', 'Shrinkage is everything unaccounted for:')}

- customer theft
- staff theft
- damaged goods thrown out and not recorded
- spoilage
- deliveries short of the invoice
- items mispriced at the till
- someone typing `12` instead of `21`
- and the plain error in both counts

{B('C-LR-R-MOVE')}Shoplifting is one item on that list. The number measures the list. The
headline names the item.{E}

This page is about that move, why it is so easy to make, and how to notice it.

---

## What is actually going on

### An estimator is not the thing it estimates

{B('C-LR-R-ESTIMAND')}The thing you care about — how much was shoplifted — is called the
**estimand**. It is out there in the world and you cannot see it. What you can compute is
an **estimator**: a recipe that takes measurements you *can* make and produces a number you
hope is close. Shrinkage is an estimator. Shoplifting is the estimand.{E}

{B('C-LR-R-SWAP')}Most measurement works this way and there is nothing wrong with it. A
thermometer is an estimator for temperature. The trouble starts when the estimator and the
estimand swap names, because then the assumptions that connected them stop travelling with
the number.{E}

### A residual is a particular kind of estimator, and the most fragile kind

{B('C-LR-R-RESIDUAL')}Some estimators measure the thing directly, more or less. A residual
estimator does the opposite. It measures *everything else* and keeps the leftovers:{E}

> **the thing I want = the total − all the parts I can account for**

{B('C-LR-R-INSTANCES')}Shrinkage is a residual. So is the Danish figure this site is about. So
are several widely used figures in economics and medicine, listed below.{E}

### Independent errors add up

This is the part that surprises people, and it is the whole problem.

{B('C-LR-R-ERRORSADD')}Suppose the shop's delivery records are {Er()} out, its till records
are {Er()} out, and its physical count is {Er()} out, each independently of the others. You
might hope those wobbles cancel. In the residual they do not: independent errors add, in
variance, whatever their signs. The residual is a *difference between large numbers*. If
the shop turns over £{turn / 1e6:.0f}m and shrinkage is £{shr / 1e6:.0f}m, then a {Er()} error
in the £{turn / 1e6:.0f}m figure is £{e_gbp:,.0f} — {e_gbp / shr * 100:.0f}% of the answer. The
errors in each input are small **relative to that input**, and enormous **relative to the
leftovers**.{E}

{B('C-LR-R-NOISIEST')}So when the errors in its inputs are independent, a residual is noisier
than any of them. It absorbs the uncertainty of everything it was computed from, and it has
no measurement of its own to steady it.{E}

### And at any one moment it cannot be checked

{B('C-LR-R-UNCHECKABLE')}You would like to validate shrinkage: measure shoplifting some other
way, and see if the numbers agree. At any one moment, you cannot. If you had an independent
way to measure shoplifting, you would not have needed the residual in the first place. The
reason a quantity is computed as a leftover is precisely that it cannot be observed.{E}

{B('C-LR-R-NOTCRITICISM')}That is not a criticism of anyone's work. It is a property of the
arithmetic. It becomes a criticism only when such a number is handed a legal obligation.{E}

### Except across time, as the account grows — and that is a real test

A residual cannot be checked against an independent measurement of itself. It **can** be
checked against what happens when somebody measures one more of the parts.

    R  =  Total  −  Σ(known parts)

{B('C-LR-R-SHRINKBY')}Measure a new part *P* that was previously inside the leftover. The
arithmetic makes a prediction, and it is exact: the residual must shrink by precisely the
size of what was moved out of it, *R_new = R_old − P*, and nothing else may move.{E}

Three failures, each diagnostic:

- **The residual does not shrink.** Then it was not the sum of the unmeasured parts.
  It was absorbing something else — model error, unit mismatch, a scaling factor —
  and *P* was never inside it.
- **The residual shrinks by less than P.** Something was double-counted: *P* overlapped
  a part already named, so the account was never a partition.
- **The total moves instead.** The "total" was itself estimated in a way that depends
  on the parts, and the account is circular. This is the same circularity as a
  variance statistic that takes its own partition as an input — see
  [CATEGORY.md](CATEGORY.md).

{B('C-LR-R-ACROSSTIME')}**So a residual is not unfalsifiable. It is unfalsifiable *at a point
in time*.** Give it a history — successive versions of the account, as pathways get
measured — and it makes a checkable prediction at every revision. A residual that has
survived several such additions, shrinking correctly each time, has earned considerably more
than one that has never been tested.{E}

{B('C-LR-R-SEQUENCE')}This also says what to ask for, and it is cheap: **not the current
number, but the sequence.** What was the leftover in each published version, what was
measured in between, and does the arithmetic close? That is an archival question,
answerable from documents that already exist, and it requires no new fieldwork.{E}

It is the same move as the feature-space test in [CATEGORY.md](CATEGORY.md), applied to a
number rather than a category: a quantity that cannot be checked against anything can still
be checked against what happens when the measured space grows.

### When it comes out impossible, that is the error bars talking

Sometimes a shop's stocktake finds *more* stock than the records allow. Negative shrinkage.

{B('C-LR-R-NEGATIVE')}That excursion is doing something useful: it is telling you **how big
the errors are**. A physical mass cannot be negative, so if your estimator produces a
negative value, the size of that negative number is at least that year's error. And since
the method and its noise are the same every year, errors that large can sit, unseen, in the
years that come out looking sensible too.{E}

---

## The ladder

Here is how a carefully qualified technical quantity becomes a claim about the world. Each
step is small. Each is individually defensible. Nobody along the way does anything they
would recognise as wrong.

| | The sentence | What quietly dropped |
|---|---|---|
| `0` | *The residual, after subtracting the modelled parts from the measured total, is X.* | — this is what was actually computed |
| `1` | *X is the shrinkage.* | the conditionality. X depends on every model that was subtracted, and those models are no longer mentioned |
| `2` | *Shoplifting cost us X.* | **the estimator becomes the estimand.** The leftovers are renamed as one of their possible causes |
| `3` | *Shoplifting is why our prices went up.* | a causal claim about an outcome, across a link nobody measured |
| `4` | *We need more security guards.* | a policy, sized to a number that was never a measurement of the thing the policy targets |

{B('C-LR-R-LADDER')}Step `2` is the load-bearing one, and it is the one that rarely gets
argued, because it happens in the choice of a word rather than in a claim. Nobody writes
*"we hereby assume the residual is entirely shoplifting."* They just start calling it
shoplifting. By step `4` the number has a life of its own. Anyone who questions it is
questioning arithmetic that was done correctly — which it was.{E}

---

## The worked example

{B('C-LR-R-DKFIGURE')}Denmark requires its farms to cut nitrogen. The figure quoted — here by
the water utilities' association DANVA, from the environment agency's accounts — is that
**agriculture accounts for {S696:.1f}% of nitrogen**.{E}

{C('C-LR-R-DKRESIDUAL', 'That figure is a residual. It is produced like this:')}

> take the nitrogen measured and modelled arriving at the coast, subtract the modelled
> contribution of sewage works and industry, subtract the modelled natural background,
> and call what remains agriculture.

{B('C-LR-R-DKDOCUMENTED')}Everything about it that follows is discoverable **because the
people who built it wrote it down and published it**. That matters, and this page returns to
it at the end.{E}

{B('C-LR-R-DKINPUTS')}**The inputs it inherits.** Of the land area involved, {meas:.0f}% is
measured and {mod:.0f}% is modelled. The measured part uses grab samples at intervals, and a
2018 study of streams measured intensively alongside found that method gave *lower*
transport than continuous measurement in every stream it covered — a documented
one-directional bias. The natural background that gets subtracted is a model output, and
retention — the largest single term in it — carries an uncertainty of **±{ru[0]:.0f}–{ru[1]:.0f}
percentage points**.{E}

{B('C-LR-R-DKNEGATIVE')}**It fails the impossibility test.** In dry years — 1996, 2005 — the
calculated agricultural contribution comes out **negative**. A mass of nitrogen cannot be less
than nothing, so that excursion is at least that year's error, from a method whose noise is
the same in every year.{E}

{B('C-LR-R-DKNOCHECK')}**It cannot be checked at a single moment.** There is no independent
measurement of "nitrogen from agriculture" to compare it against: if there were, nobody would
compute it as a leftover.{E}

{B('C-LR-R-DKCLIMB')}**And the ladder is there for it to climb.** *{S696:.1f}% of the land-based
waterborne term* can become *agriculture causes {S696:.0f}% of the nitrogen*, then
*{S696:.0f}% of the oxygen depletion*, then *{S696:.0f}% of the mess on the beach*. The last two
of those steps cross links for which no coefficient is computed in anything this project has
read — the audit of that chain is in [CAUSATION.md](CAUSATION.md).{E}

{B('C-LR-R-DKCUT')}There is a second detail worth knowing, because it shows the same instinct in
a different place. The oxygen-depletion requirement in the Danish method is not derived from
any relationship between nitrogen and oxygen. If a water body is flagged as oxygen-affected,
the method applies **a flat {CUT:.0f}% cut** to its nitrogen concentration, chosen — in the
method document's own words — to be large enough to shift the system, that is, larger than
the normal variation from year to year. It is a considered engineering default, honestly
labelled as one. It is not a measurement.{E}

---

## You have read this number in other clothes

The pattern is not rare and it is not Danish. A short list, one line each, with no claim
that any of these is wrong:

- {C('C-LR-R-OUTPUTGAP', '**The output gap** — the difference between what an economy produces and its *potential* output, which is estimated rather than observed.')}
- {C('C-LR-R-NAIRU', '**NAIRU** — the unemployment rate below which inflation is said to accelerate. It is estimated from other quantities, not measured.')}
- {C('C-LR-R-EXCESS', '**Excess mortality** — actual deaths minus the deaths expected under normal conditions. Sound and widely useful; also a difference between large numbers.')}
- {C('C-LR-R-PAF', '**Attributable fraction** in epidemiology — the proportion of cases in a population attributed to an exposure, computed from relative risks.')}
- {C('C-LR-R-SAFETY', '**Safety factors** in toxicology — the factors an observed dose is divided by to reach a permitted one. Deliberate, disclosed engineering judgements, and constants someone chose, which then propagate through everything downstream.')}

{B('C-LR-R-THREEQ')}The test is never *does this contain a judgement?* Every applied number
contains judgements, and must. The test is three questions:{E}

1. **Is the judgement disclosed?**
2. **Is the sensitivity to it reported** — what happens to the answer if it were {alt:.0f}%
   instead of {CUT:.0f}%?
3. **Does the claim being made downstream respect it?**

{B('C-LR-R-THREEQ-DK')}In the nitrogen case the first is yes: the method document states the
{CUT:.0f}% and its reason. The second is not answered in the method document. The third is a
question about what happens after the document leaves the building, and only the first is
the scientists' to answer.{E}

---

## When somebody attacks the gap on purpose

{B('C-LR-R-ATTACK')}Everything above treats the gap between an estimator and the thing it
estimates as an honest hazard — a place where error accumulates unnoticed. It is also an
*attack surface*, and once you see that, two well-documented cases stop looking like scandals
about dishonesty and start looking like scandals about measurement.{E}

{B('C-LR-R-PROTEIN')}**Protein in milk.** Protein content is not measured directly. Nitrogen
is measured, by the Kjeldahl or a similar method, and multiplied by a conversion factor,
because protein is on average about {PROT:.0f}% nitrogen. The estimator is nitrogen; the
estimand is protein.{E} {B('C-LR-R-MELAMINE')}Melamine is {MEL:.1f}% nitrogen by mass and
contains no protein whatsoever. Adding it to diluted milk raises the measured value without
raising the real one — **the estimator moves and the estimand does not.**{E}
{B('C-LR-R-MELAMINE-2008')}In China in 2008, {KIDS:,} affected children were identified, {HOSP:,}
of them in hospital, with kidney damage, and the deaths of six babies were officially
concluded to be related to the contaminated milk.{E} Nobody had to defeat a laboratory. The
substitution was in the definition of the test.

{B('C-LR-R-EMISSIONS')}**Emissions in a car.** Regulated emissions are measured on a defined
test cycle, which is the estimator for real-world emissions. Software that recognises the
test and behaves differently on it defeats the estimator while leaving the estimand
untouched.{E} {B('C-LR-R-ADBLUE')}The same logic runs one layer down in the exhaust system,
where the reagent that makes NOx reduction work is a consumable with a running cost. The
register's {live.ref("A10")} is that pathway.{E}

The two cases share a shape worth naming, because it is the practical reason any of this
matters:

> {B('C-LR-R-SHAPE')}**Wherever a quantity is estimated by proxy and something depends on the number, the gap between proxy and quantity is a place where value can be extracted.** It does not require a conspiracy. It requires only that somebody notice the gap before the people relying on the number do.{E}

Which gives a fourth question to add to the three above, and it is not a scientific
question at all:

4. **Who benefits if the estimator moves without the estimand?**

{B('C-LR-R-FOURTH')}If the answer is "nobody", the gap is only a hazard. If somebody does
benefit, the gap is a mechanism, and its size stops being an academic matter. None of this
is an accusation about any Danish number. It is the reason to *ask* — and asking is cheap,
which is the whole argument of this page.{E}

---

## What a checkable number looks like instead

{C('C-LR-R-OPPOSITE', 'The opposite of a residual is not a better model. It is **two methods that fail differently, agreeing.**')}

{B('C-LR-R-ALIGN')}This project can show one, from its own work. Copenhagen published its 2012
cloudburst model as {sheets} PDF maps with no geographical coordinates. Putting them back on
the map produced a number — where each sheet sits — and that number can be checked in ways
that have nothing to do with who computed it:{E}

- {B('C-LR-R-SOLVED')}**Two methods, solved together.** Some sheets were placed by a resident
  clicking landmarks on a web map. Others were placed by correlating one sheet's
  photographed ground against its neighbour's, by FFT. All {sheets} were then solved
  together, and where they overlap they now agree to {fa['pair_rms_m']:g} m RMS.{E}
- {B('C-LR-R-CONVERGE')}**It converges.** Re-running the whole alignment after applying the
  answer asks for further corrections of **{s_lo:+.0f} to {s_hi:+.0f} m**. A wrong
  registration keeps asking to move.{E}
- {B('C-LR-R-WATERCHECK')}**A check that was never optimised for.** Some of the model's
  painted flood depth falls on open water, which is an error by construction — water standing
  on water. Before the adjustment that was {before:.2f} km². After, **{after:.2f} km², a
  {(1 - after / before) * 100:.0f}% reduction.** Nothing in the alignment was trying to
  improve it. It is measured against the city's own water polygons, which the alignment
  never reads. The current build reports {now:.2f} km².{E}

{B('C-LR-R-LOADBEARING')}Checks with unrelated failure modes, agreeing: that is what makes a
number load-bearing — not the authority of whoever produced it, and not the sophistication of
the method.{E}

{C('C-LR-R-NEVERTHIS', 'A residual estimator can never have this. That is the argument of this page in one line.')}

---

## The same standard, turned around

{B('C-LR-R-OWN-INTRO')}It would be dishonest to describe this test and not apply it here. The
following claims on this site currently have **no independent check**, and should be read
accordingly:{E}

- {B('C-LR-R-OWN-CEILING')}**The ceiling of {ceil:.0f}%** on agriculture's share of nitrogen
  reaching the sea. It depends entirely on our own enumeration of {n_all} pathways being
  right, and on our own bounds for the {n_all - n_unq} that carry numbers. No independent check
  of the enumeration is recorded.{E}
- {B('C-LR-R-OWN-WAVES')}**The wave and bed-shear model.** Computed exceedance frequencies
  against literature values for critical shear stress. No observation of sediment actually
  moving. The live-bed versus dead-bed *ratio* is robust; the absolute hours are not.{E}
- {B('C-LR-R-OWN-FLUSH')}**The {flush:.0f}-day retention figure for Køge Bugt.** One coarse
  global model. And the same method put Det Sydfynske Øhav mid-range, at {sydfyn:.1f} days.{E}
- {B('C-LR-R-OWN-LAG')}**The {best['lag_h']}-hour transport lag** between overflow-scale rain
  and southward flow: {best['hours']} event-hours, at lags from {lag_lo} to {lag_hi} hours. The
  attempt to extend the current record backwards using a wind index failed, and is reported
  as a negative result. Everything said here about currents rests on {years:.0f} years of
  record.{E}
{norrebro}
- {B('C-LR-R-OWN-MUSSEL')}**The extractive-aquaculture area estimate.** A stoichiometric
  calculation, not compared against what a working mussel farm actually removes.{E}
- {B('C-LR-R-OWN-FEDTEMOG')}**The seasonal argument about fedtemøg.** No shore-condition
  series was found in any source this project surveyed, so the seasonal claim cannot
  presently be checked either.{E}

{B('C-LR-R-OWN-CLOSE')}Several of those could be checked cheaply. That they have not been is a
fact about this project, not a defence of it.{E}

---

## A note on who this is about

{B('C-LR-R-WHO-DOCS')}Every limitation of the Danish method described here was found by
**reading a document that its authors wrote and published**. The {CUT:.0f}% is discoverable
because the method document states it and explains the reasoning. The averaging of
indicators is discoverable because they wrote down that it reduces the risk of
over-implementation. The exclusion of eelgrass is discoverable because they justified it, in
print, by its slow response time. The sampling exclusions in the toxicant figures are
discoverable because the agency listed them.{E}

{B('C-LR-R-WHO-GOOD')}That is people documenting their own limitations in public. It is what
good work looks like, and it is the only reason any of this could be audited at all.{E}
{C('C-LR-R-ANACHRONISM', 'Holding past work to a standard that did not exist when it was done is anachronism, not criticism.')}

{B('C-LR-R-USE')}**The criticism here is of the use of a number, not its production.** A method
that states in its own text that it averages indicators to avoid over-implementation, and
that the oxygen requirement is a judged constant, can become *"agriculture causes
{S696:.0f}% of the mess on the beach"* only after it leaves the scientists' hands.{E}

{C('C-LR-R-DISTANCE', 'That distance — between what the document says and what is then said with it — is the finding. The document is the evidence for it, not the target.')}
"""


def main():
    try:
        write_doc(OUT, render())
    except (live.Unjustified, _claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
