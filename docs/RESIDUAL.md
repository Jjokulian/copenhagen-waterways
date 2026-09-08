# The number that was never measured

Hand-written rather than generated. This page explains one idea, and it is the idea the
rest of this site keeps running into. Nitrogen is the worked example. The idea is not
about nitrogen, and you do not need to care about Denmark to use it.

---

## A shop at closing time

A supermarket wants to know how much stock it lost to shoplifting last year.

Nobody can count shoplifting. By its nature it is the thing that happens when no one is
recording. So the shop does the only thing available: it works out what *should* be on the
shelves from its delivery records and its till records, counts what is *actually* there,
and calls the gap **shrinkage**.

Shrinkage is a real, useful, carefully produced number. Every large retailer computes it.
And then, reliably, it appears in the newspaper as *"shoplifting cost retailers £2.2bn"*.

Look at what happened in that sentence. Shrinkage is everything unaccounted for:

- customer theft
- staff theft
- damaged goods thrown out and not recorded
- spoilage
- deliveries short of the invoice
- items mispriced at the till
- someone typing 12 instead of 21
- and the plain error in both counts

Shoplifting is one item on that list. The number measures the list. The headline names
the item.

This page is about that move, why it is so easy to make, and how to notice it.

---

## What is actually going on

### An estimator is not the thing it estimates

The thing you care about — how much was shoplifted — is called the **estimand**. It is out
there in the world and you cannot see it.

What you can compute is an **estimator**: a recipe that takes measurements you *can* make
and produces a number you hope is close. Shrinkage is an estimator. Shoplifting is the
estimand.

Everything in science works this way and there is nothing wrong with it. A thermometer is
an estimator for temperature. The trouble starts when the estimator and the estimand swap
names, because then the assumptions that connected them stop travelling with the number.

### A residual is a particular kind of estimator, and the most fragile kind

Some estimators measure the thing directly, more or less. A residual estimator does the
opposite. It measures *everything else* and keeps the leftovers:

> **the thing I want = the total − all the parts I can account for**

Shrinkage is a residual. So is the Danish figure this site is about. So, as we will see,
are several numbers you have read this month.

### The errors add up. They do not cancel out

This is the part that surprises people, and it is the whole problem.

Suppose the shop's delivery records are 1% out, its till records are 1% out, and its
physical count is 1% out. You might hope those wobbles partly cancel. They do not — not
in the residual.

The residual is a *difference between large numbers*. If the shop turns over £50m and
shrinkage is £1m, then a 1% error in the £50m figure is £500,000 — half the answer. The
errors in each input are small **relative to that input**, and enormous **relative to the
leftovers**.

So a residual is always the noisiest quantity in the account. Not sometimes. Structurally,
by construction, every time. It absorbs the uncertainty of everything it was computed
from, and it has none of its own measurement to steady it.

### And it can never be checked

This is the deeper trouble, and it is easy to miss.

You would like to validate shrinkage: measure shoplifting some other way, and see if the
numbers agree. **You cannot.** If you had an independent way to measure shoplifting, you
would not have needed the residual in the first place. The reason a quantity is computed
as a leftover is precisely that it cannot be observed.

So a residual estimator is, by its own definition, **the one class of number that can
never be confirmed against the thing it claims to describe.** Every other number in the
account can be checked against something. This one cannot be checked against anything,
ever, in principle.

That is not a criticism of anyone's work. It is a property of the arithmetic. It becomes a
criticism only when such a number is handed a legal obligation.

### When it comes out impossible, that is the error bars talking

Sometimes a shop's stocktake finds *more* stock than the records allow. Negative
shrinkage. Everyone shrugs and calls it a counting error, and moves on.

They should not move on, because that excursion is doing something useful: it is telling
you **how big the errors are**.

A physical mass cannot be negative. So if your estimator produces a negative value, the
size of that negative number is a **lower bound on the error in your method** — not just
in that year, but in every year. The years that come out looking sensible are not more
accurate. They are the same method with the same noise, and the noise merely happened to
land somewhere plausible.

An estimator that can return an impossible answer has published its own error bars, and
almost nobody reads them.

---

## The ladder

Here is how a carefully qualified technical quantity becomes a claim about the world. Each
step is small. Each is individually defensible. Nobody along the way does anything they
would recognise as wrong.

| | The sentence | What quietly dropped |
|---|---|---|
| **0** | *The residual, after subtracting the modelled parts from the measured total, is X.* | — this is what was actually computed |
| **1** | *X is the shrinkage.* | the conditionality. X depends on every model that was subtracted, and those models are no longer mentioned |
| **2** | *Shoplifting cost us X.* | **the estimator becomes the estimand.** The leftovers are renamed as one of their possible causes |
| **3** | *Shoplifting is why our prices went up.* | a causal claim about an outcome, across a link nobody measured |
| **4** | *We need more security guards.* | a policy, sized to a number that was never a measurement of the thing the policy targets |

Step 2 is the load-bearing one, and it is the one that never gets argued, because it
happens in the choice of a word rather than in a claim. Nobody writes *"we hereby assume
the residual is entirely shoplifting."* They just start calling it shoplifting.

By step 4 the number has a life of its own. Anyone who questions it is questioning
arithmetic that was done correctly — which it was.

---

## The worked example

Denmark requires its farms to cut nitrogen. The figure everyone quotes is that
**agriculture accounts for 69.6% of nitrogen**.

That figure is a residual. It is produced like this:

> take the nitrogen measured and modelled arriving at the coast, subtract the modelled
> contribution of sewage works and industry, subtract the modelled natural background,
> and call what remains agriculture.

Everything about it that follows is discoverable **because the people who built it wrote
it down and published it**. That matters and this page returns to it at the end.

**The inputs it inherits.** Of the land area involved, 49% is measured and 51% is
modelled. The measured half uses grab samples at intervals, and a study of three streams
found that method gave *lower* transport than continuous measurement **every time** — a
documented one-directional bias. The natural background that gets subtracted is a model
output, and retention — the largest single term in it — carries an uncertainty of
**±6–27 percentage points**.

**It fails the impossibility test.** In dry years — 1996, 2005 — the calculated
agricultural contribution comes out **negative**. A mass of nitrogen cannot be less than
nothing. That excursion is the method telling you the size of its own error, in every year.

**It cannot be checked.** There is no independent measurement of "nitrogen from
agriculture" to compare it against. If there were, nobody would compute it as a leftover.

**And then it climbs the ladder.** *69.6% of the land-based waterborne term* becomes
*agriculture causes 70% of the nitrogen*, becomes *70% of the oxygen depletion*, becomes
*70% of the mess on the beach*. Two of those steps cross links where **no coefficient has
ever been calculated** — the audit of that chain is in [CAUSATION.md](#CAUSATION.md).

There is a second detail worth knowing, because it shows the same instinct in a different
place. The oxygen-depletion requirement in the Danish method is not derived from any
relationship between nitrogen and oxygen. If a water body is flagged as oxygen-affected,
the method applies **a flat 25% cut**, chosen — in the method document's own words — as a
figure judged large enough to shift the system. It is a considered engineering default,
honestly labelled as one. It is not a measurement, and by the time it reaches a press
release it is indistinguishable from one.

---

## You have read this number in other clothes

The pattern is not rare and it is not Danish. A short list, one line each, with no claim
that any of these is wrong:

- **The output gap** — the difference between what an economy produces and what it
  *could* produce. The second quantity is unobservable. The gap is a residual, and
  interest rates are set with reference to it.
- **NAIRU** — the unemployment rate below which inflation is said to accelerate. Not
  measurable. Backed out of other quantities.
- **Excess mortality** — actual deaths minus the deaths a model says you should have
  expected. Sound and widely useful; also a difference between large numbers, and it
  routinely goes negative.
- **Attributable fraction** in epidemiology — the share of cases said to be caused by an
  exposure. Computed from modelled risks, then reported as a count of people.
- **Safety factors** in toxicology — the 10s and 100s dividing an observed dose to reach a
  permitted one. Deliberate, disclosed, defensible engineering judgements. Also constants
  someone chose, which then propagate through everything downstream as if measured.

The test is never *does this contain a judgement?* Every applied number contains
judgements, and must. The test is three questions:

1. **Is the judgement disclosed?**
2. **Is the sensitivity to it reported** — what happens to the answer if it were 15%
   instead of 25%?
3. **Does the claim being made downstream respect it?**

In the nitrogen case the first is yes and the other two are no. And notice that only the
first is the scientists'. The other two failures happen after the document leaves the
building.

---

## What a checkable number looks like instead

The opposite of a residual is not a better model. It is **two methods that fail
differently, agreeing.**

This project can show one, from its own work. Copenhagen published its 2012 cloudburst
model as seven PDF maps with the geographical coordinates stripped out. Putting them back
on the map produced a number — where each sheet sits — and that number is believable for
reasons that have nothing to do with who computed it:

- **A person and an algorithm agreed.** Some sheets were placed by a resident clicking
  landmarks on a web map. Others were placed by correlating one sheet's photographed
  ground against its neighbour's, by FFT. When all seven were solved together, the
  human-placed sheets moved by **0.2 to 1.8 standard errors** — and the one that moved
  furthest was the sheet whose two control points sat at nearly the same height, so its
  north–south position was known in advance to be the weak one. The method corrected the
  axis that was already understood to be unconstrained. A tired person clicking and a
  cross-correlation fail in entirely unrelated ways, and they landed in the same place.
- **It converges.** Re-running the whole alignment after applying the answer asks for
  further corrections of **−1 to +1 m**, against the 100–360 m it applied the first time.
  A wrong registration keeps asking to move.
- **A check that was never optimised for.** Some of the model's painted flood depth falls
  on open water, which is an error by construction — water standing on water. Before the
  adjustment that was 1.56 km². After, **1.21 km², a 22% reduction.** Nothing in the
  alignment was trying to improve it. It is measured against the city's own water
  polygons, which the alignment never reads.

Three checks, three unrelated failure modes, all agreeing. That is what makes a number
load-bearing — not the authority of whoever produced it, and not the sophistication of the
method. And note what the same work did to the *previous* answer: four sheets that had
advertised an accuracy of "13–28 m" turned out to disagree with each other by 100–190 m.
That figure had been agreement between two detectors, not accuracy. Detectors agreeing on
a wrong answer is a thing that happens, and it is exactly what a check with a *related*
failure mode buys you — which is nothing.

A residual estimator can never have this. That is the argument of this page in one line.

---

## The same standard, turned around

It would be dishonest to describe this test and not apply it here. The following claims on
this site currently have **no independent check**, and should be read accordingly:

- **The ceiling of 30%** on agriculture's share of nitrogen reaching the sea. It depends
  entirely on our own enumeration of twenty pathways being right, and on our own bounds
  for the ten that carry numbers. Nobody has checked the enumeration.
- **The wave and bed-shear model.** Computed exceedance frequencies against literature
  values for critical shear stress. No observation of sediment actually moving. The
  live-bed versus dead-bed *ratio* is robust; the absolute hours are not.
- **The 73-day retention figure for Køge Bugt.** One coarse global model. And the same
  method put Det Sydfynske Øhav mid-range, which was against expectation — a result we
  reported rather than explained.
- **The 12-hour transport lag** between overflow-scale rain and southward flow. 145
  event-hours, six lags tested. The attempt to extend the four-year current record
  backwards using a wind index failed, and is reported as a negative result. Everything
  said here about currents is four years long.
- **The Nørrebro flood sheet.** Every attempt to correlate it against a neighbour came out
  flat. It has no control points either. It is the one sheet not known to be consistent
  with the other six, and it is marked as such.
- **The extractive-aquaculture area estimate.** A stoichiometric calculation. Never
  compared against what a working mussel farm actually removes.
- **The seasonal argument about fedtemøg.** It rests on wind records and on testimony.
  There is no monitoring of the shore condition anywhere in Denmark, which is the finding
  — and it also means our own seasonal claim cannot presently be checked either.

Several of those could be checked cheaply. That they have not been is a fact about this
project, not a defence of it.

---

## A note on who this is about

Every limitation described here was found by **reading a document that its authors wrote
and published**. The 25% is discoverable because the method document states it and
explains the reasoning. The averaging of indicators is discoverable because they wrote
down that it reduces the risk of over-implementation. The exclusion of eelgrass is
discoverable because they justified it, in print, by its slow response time. The sampling
exclusions in the toxicant figures are discoverable because the agency listed them.

That is people documenting their own limitations in public. It is what good work looks
like, and it is the only reason any of this could be audited at all.

It is also worth saying that this audit was cheap in a way it could not have been when the
work was done. Reading a methodology document against thirty-one years of hourly wind
records, a recovered flood model and four separate government reports — and holding all of
it at once — was months of specialist labour a decade ago. Holding past work to a standard
that did not exist when it was done is anachronism, not criticism.

**The criticism here is of the use of a number, not its production.** A method that states
in its own text that it averages indicators to avoid over-implementation, that the oxygen
requirement is a judged constant, and that most water bodies have a single monitoring
station, becomes *"agriculture causes 70% of the mess on the beach"* only after it leaves
the scientists' hands.

That distance — between what the document says and what the politics says — is the
finding. The document is the evidence for it, not the target.
