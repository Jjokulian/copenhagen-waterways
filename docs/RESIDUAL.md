# The number that was never measured

Written by hand, and generated only so that every number and every assertion in it
carries its chain: the prose is kept in `scripts/pages/residual.py`. <span class="claim" data-claim="C-LR-R-INTRO">This page
explains one idea, and it is the idea the rest of this site keeps running into. Nitrogen
is the worked example. The idea is not about nitrogen, and you do not need to care about
Denmark to use it.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-INTRO "What this claim rests on")</sup>

---

## A shop at closing time

A supermarket wants to know how much stock it lost to shoplifting last year.

<span class="claim" data-claim="C-LR-R-SHRINKAGE">Nobody can count shoplifting. By its nature it is the thing that happens
when no one is recording. So the shop does the only thing available: it works out what
*should* be on the shelves from its delivery records and its till records, counts what is
*actually* there, and calls the gap **shrinkage**.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-SHRINKAGE "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-HEADLINE">Shrinkage is a real, useful, carefully produced number. It is also easy
to picture it in a headline as *"shoplifting cost retailers £[2.2](SOURCES.md#F-01426e6b4e)bn"* - a figure this page
makes up for the example.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-HEADLINE "What this claim rests on")</sup>

Look at what happens in that sentence. <span class="claim" data-claim="C-LR-R-LIST">Shrinkage is everything unaccounted for:</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-LIST "What this claim rests on")</sup>

- customer theft
- staff theft
- damaged goods thrown out and not recorded
- spoilage
- deliveries short of the invoice
- items mispriced at the till
- someone typing `12` instead of `21`
- and the plain error in both counts

<span class="claim" data-claim="C-LR-R-MOVE">Shoplifting is one item on that list. The number measures the list. The
headline names the item.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-MOVE "What this claim rests on")</sup>

This page is about that move, why it is so easy to make, and how to notice it.

---

## What is actually going on

### An estimator is not the thing it estimates

<span class="claim" data-claim="C-LR-R-ESTIMAND">The thing you care about — how much was shoplifted — is called the
**estimand**. It is out there in the world and you cannot see it. What you can compute is
an **estimator**: a recipe that takes measurements you *can* make and produces a number you
hope is close. Shrinkage is an estimator. Shoplifting is the estimand.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-ESTIMAND "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-SWAP">Most measurement works this way and there is nothing wrong with it. A
thermometer is an estimator for temperature. The trouble starts when the estimator and the
estimand swap names, because then the assumptions that connected them stop travelling with
the number.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-SWAP "What this claim rests on")</sup>

### A residual is a particular kind of estimator, and the most fragile kind

<span class="claim" data-claim="C-LR-R-RESIDUAL">Some estimators measure the thing directly, more or less. A residual
estimator does the opposite. It measures *everything else* and keeps the leftovers:</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-RESIDUAL "What this claim rests on")</sup>

> **the thing I want = the total − all the parts I can account for**

<span class="claim" data-claim="C-LR-R-INSTANCES">Shrinkage is a residual. So is the Danish figure this site is about. So
are several widely used figures in economics and medicine, listed below.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-INSTANCES "What this claim rests on")</sup>

### Independent errors add up

This is the part that surprises people, and it is the whole problem.

<span class="claim" data-claim="C-LR-R-ERRORSADD">Suppose the shop's delivery records are [1](SOURCES.md#F-2fa1baa60b)% out, its till records
are [1](SOURCES.md#F-2fa1baa60b)% out, and its physical count is [1](SOURCES.md#F-2fa1baa60b)% out, each independently of the others. You
might hope those wobbles cancel. In the residual they do not: independent errors add, in
variance, whatever their signs. The residual is a *difference between large numbers*. If
the shop turns over £[50](SOURCES.md#F-01d5e66013)m and shrinkage is £[1](SOURCES.md#F-eea3489da6)m, then a [1](SOURCES.md#F-2fa1baa60b)% error
in the £[50](SOURCES.md#F-01d5e66013)m figure is £[500,000](SOURCES.md#F-e7cabbb980) — [50](SOURCES.md#F-f45b3770bd)% of the answer. The
errors in each input are small **relative to that input**, and enormous **relative to the
leftovers**.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-ERRORSADD "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-NOISIEST">So when the errors in its inputs are independent, a residual is noisier
than any of them. It absorbs the uncertainty of everything it was computed from, and it has
no measurement of its own to steady it.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-NOISIEST "What this claim rests on")</sup>

### And at any one moment it cannot be checked

<span class="claim" data-claim="C-LR-R-UNCHECKABLE">You would like to validate shrinkage: measure shoplifting some other
way, and see if the numbers agree. At any one moment, you cannot. If you had an independent
way to measure shoplifting, you would not have needed the residual in the first place. The
reason a quantity is computed as a leftover is precisely that it cannot be observed.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-UNCHECKABLE "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-NOTCRITICISM">That is not a criticism of anyone's work. It is a property of the
arithmetic. It becomes a criticism only when such a number is handed a legal obligation.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-NOTCRITICISM "What this claim rests on")</sup>

### Except across time, as the account grows — and that is a real test

A residual cannot be checked against an independent measurement of itself. It **can** be
checked against what happens when somebody measures one more of the parts.

    R  =  Total  −  Σ(known parts)

<span class="claim" data-claim="C-LR-R-SHRINKBY">Measure a new part *P* that was previously inside the leftover. The
arithmetic makes a prediction, and it is exact: the residual must shrink by precisely the
size of what was moved out of it, *R_new = R_old − P*, and nothing else may move.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-SHRINKBY "What this claim rests on")</sup>

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

<span class="claim" data-claim="C-LR-R-ACROSSTIME">**So a residual is not unfalsifiable. It is unfalsifiable *at a point
in time*.** Give it a history — successive versions of the account, as pathways get
measured — and it makes a checkable prediction at every revision. A residual that has
survived several such additions, shrinking correctly each time, has earned considerably more
than one that has never been tested.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-ACROSSTIME "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-SEQUENCE">This also says what to ask for, and it is cheap: **not the current
number, but the sequence.** What was the leftover in each published version, what was
measured in between, and does the arithmetic close? That is an archival question,
answerable from documents that already exist, and it requires no new fieldwork.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-SEQUENCE "What this claim rests on")</sup>

It is the same move as the feature-space test in [CATEGORY.md](CATEGORY.md), applied to a
number rather than a category: a quantity that cannot be checked against anything can still
be checked against what happens when the measured space grows.

### When it comes out impossible, that is the error bars talking

Sometimes a shop's stocktake finds *more* stock than the records allow. Negative shrinkage.

<span class="claim" data-claim="C-LR-R-NEGATIVE">That excursion is doing something useful: it is telling you **how big
the errors are**. A physical mass cannot be negative, so if your estimator produces a
negative value, the size of that negative number is at least that year's error. And since
the method and its noise are the same every year, errors that large can sit, unseen, in the
years that come out looking sensible too.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-NEGATIVE "What this claim rests on")</sup>

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

<span class="claim" data-claim="C-LR-R-LADDER">Step `2` is the load-bearing one, and it is the one that rarely gets
argued, because it happens in the choice of a word rather than in a claim. Nobody writes
*"we hereby assume the residual is entirely shoplifting."* They just start calling it
shoplifting. By step `4` the number has a life of its own. Anyone who questions it is
questioning arithmetic that was done correctly — which it was.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-LADDER "What this claim rests on")</sup>

---

## The worked example

<span class="claim" data-claim="C-LR-R-DKFIGURE">Denmark requires its farms to cut nitrogen. The figure quoted — here by
the water utilities' association DANVA, from the environment agency's accounts — is that
**agriculture accounts for [69.6](SOURCES.md#F-7e1b8a8a83)% of nitrogen**.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-DKFIGURE "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-DKRESIDUAL">That figure is a residual. It is produced like this:</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-DKRESIDUAL "What this claim rests on")</sup>

> take the nitrogen measured and modelled arriving at the coast, subtract the modelled
> contribution of sewage works and industry, subtract the modelled natural background,
> and call what remains agriculture.

<span class="claim" data-claim="C-LR-R-DKDOCUMENTED">Everything about it that follows is discoverable **because the
people who built it wrote it down and published it**. That matters, and this page returns to
it at the end.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-DKDOCUMENTED "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-DKINPUTS">**The inputs it inherits.** Of the land area involved, [49](SOURCES.md#F-d90ee38f36)% is
measured and [51](SOURCES.md#F-e986da2740)% is modelled. The measured part uses grab samples at intervals, and a
2018 study of streams measured intensively alongside found that method gave *lower*
transport than continuous measurement in every stream it covered — a documented
one-directional bias. The natural background that gets subtracted is a model output, and
retention — the largest single term in it — carries an uncertainty of **±[6](SOURCES.md#F-fb507b62c6)–[27](SOURCES.md#F-11ea8dab17)
percentage points**.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-DKINPUTS "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-DKNEGATIVE">**It fails the impossibility test.** In dry years — 1996, 2005 — the
calculated agricultural contribution comes out **negative**. A mass of nitrogen cannot be less
than nothing, so that excursion is at least that year's error, from a method whose noise is
the same in every year.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-DKNEGATIVE "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-DKNOCHECK">**It cannot be checked at a single moment.** There is no independent
measurement of "nitrogen from agriculture" to compare it against: if there were, nobody would
compute it as a leftover.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-DKNOCHECK "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-DKCLIMB">**And the ladder is there for it to climb.** *[69.6](SOURCES.md#F-7e1b8a8a83)% of the land-based
waterborne term* can become *agriculture causes [70](SOURCES.md#F-7e1b8a8a83)% of the nitrogen*, then
*[70](SOURCES.md#F-7e1b8a8a83)% of the oxygen depletion*, then *[70](SOURCES.md#F-7e1b8a8a83)% of the mess on the beach*. The last two
of those steps cross links for which no coefficient is computed in anything this project has
read — the audit of that chain is in [CAUSATION.md](CAUSATION.md).</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-DKCLIMB "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-DKCUT">There is a second detail worth knowing, because it shows the same instinct in
a different place. The oxygen-depletion requirement in the Danish method is not derived from
any relationship between nitrogen and oxygen. If a water body is flagged as oxygen-affected,
the method applies **a flat [25](SOURCES.md#F-8be24edb3a)% cut** to its nitrogen concentration, chosen — in the
method document's own words — to be large enough to shift the system, that is, larger than
the normal variation from year to year. It is a considered engineering default, honestly
labelled as one. It is not a measurement.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-DKCUT "What this claim rests on")</sup>

---

## You have read this number in other clothes

The pattern is not rare and it is not Danish. A short list, one line each, with no claim
that any of these is wrong:

- <span class="claim" data-claim="C-LR-R-OUTPUTGAP">**The output gap** — the difference between what an economy produces and its *potential* output, which is estimated rather than observed.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OUTPUTGAP "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-NAIRU">**NAIRU** — the unemployment rate below which inflation is said to accelerate. It is estimated from other quantities, not measured.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-NAIRU "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-EXCESS">**Excess mortality** — actual deaths minus the deaths expected under normal conditions. Sound and widely useful; also a difference between large numbers.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-EXCESS "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-PAF">**Attributable fraction** in epidemiology — the proportion of cases in a population attributed to an exposure, computed from relative risks.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-PAF "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-SAFETY">**Safety factors** in toxicology — the factors an observed dose is divided by to reach a permitted one. Deliberate, disclosed engineering judgements, and constants someone chose, which then propagate through everything downstream.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-SAFETY "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-THREEQ">The test is never *does this contain a judgement?* Every applied number
contains judgements, and must. The test is three questions:</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-THREEQ "What this claim rests on")</sup>

1. **Is the judgement disclosed?**
2. **Is the sensitivity to it reported** — what happens to the answer if it were [15](SOURCES.md#F-be7e443028)%
   instead of [25](SOURCES.md#F-8be24edb3a)%?
3. **Does the claim being made downstream respect it?**

<span class="claim" data-claim="C-LR-R-THREEQ-DK">In the nitrogen case the first is yes: the method document states the
[25](SOURCES.md#F-8be24edb3a)% and its reason. The second is not answered in the method document. The third is a
question about what happens after the document leaves the building, and only the first is
the scientists' to answer.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-THREEQ-DK "What this claim rests on")</sup>

---

## When somebody attacks the gap on purpose

<span class="claim" data-claim="C-LR-R-ATTACK">Everything above treats the gap between an estimator and the thing it
estimates as an honest hazard — a place where error accumulates unnoticed. It is also an
*attack surface*, and once you see that, two well-documented cases stop looking like scandals
about dishonesty and start looking like scandals about measurement.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-ATTACK "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-PROTEIN">**Protein in milk.** Protein content is not measured directly. Nitrogen
is measured, by the Kjeldahl or a similar method, and multiplied by a conversion factor,
because protein is on average about [16](SOURCES.md#F-c60f52e4c0)% nitrogen. The estimator is nitrogen; the
estimand is protein.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-PROTEIN "What this claim rests on")</sup> <span class="claim" data-claim="C-LR-R-MELAMINE">Melamine is [66.6](SOURCES.md#F-8551abdaee)% nitrogen by mass and
contains no protein whatsoever. Adding it to diluted milk raises the measured value without
raising the real one — **the estimator moves and the estimand does not.**</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-MELAMINE "What this claim rests on")</sup>
<span class="claim" data-claim="C-LR-R-MELAMINE-2008">In China in 2008, [300,000](SOURCES.md#F-5ae291e71c) affected children were identified, [54,000](SOURCES.md#F-ef847c75d7)
of them in hospital, with kidney damage, and the deaths of six babies were officially
concluded to be related to the contaminated milk.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-MELAMINE-2008 "What this claim rests on")</sup> Nobody had to defeat a laboratory. The
substitution was in the definition of the test.

<span class="claim" data-claim="C-LR-R-EMISSIONS">**Emissions in a car.** Regulated emissions are measured on a defined
test cycle, which is the estimator for real-world emissions. Software that recognises the
test and behaves differently on it defeats the estimator while leaving the estimand
untouched.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-EMISSIONS "What this claim rests on")</sup> <span class="claim" data-claim="C-LR-R-ADBLUE">The same logic runs one layer down in the exhaust system,
where the reagent that makes NOx reduction work is a consumable with a running cost. The
register's [A10](HYPOTHESES.md "Exhaust-treatment reagent: nitrogen added to remove nitrogen") is that pathway.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-ADBLUE "What this claim rests on")</sup>

The two cases share a shape worth naming, because it is the practical reason any of this
matters:

> <span class="claim" data-claim="C-LR-R-SHAPE">**Wherever a quantity is estimated by proxy and something depends on the number, the gap between proxy and quantity is a place where value can be extracted.** It does not require a conspiracy. It requires only that somebody notice the gap before the people relying on the number do.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-SHAPE "What this claim rests on")</sup>

Which gives a fourth question to add to the three above, and it is not a scientific
question at all:

4. **Who benefits if the estimator moves without the estimand?**

<span class="claim" data-claim="C-LR-R-FOURTH">If the answer is "nobody", the gap is only a hazard. If somebody does
benefit, the gap is a mechanism, and its size stops being an academic matter. None of this
is an accusation about any Danish number. It is the reason to *ask* — and asking is cheap,
which is the whole argument of this page.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-FOURTH "What this claim rests on")</sup>

---

## What a checkable number looks like instead

<span class="claim" data-claim="C-LR-R-OPPOSITE">The opposite of a residual is not a better model. It is **two methods that fail differently, agreeing.**</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OPPOSITE "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-ALIGN">This project can show one, from its own work. Copenhagen published its 2012
cloudburst model as [7](SOURCES.md#F-4c27a47dfd) PDF maps with no geographical coordinates. Putting them back on
the map produced a number — where each sheet sits — and that number can be checked in ways
that have nothing to do with who computed it:</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-ALIGN "What this claim rests on")</sup>

- <span class="claim" data-claim="C-LR-R-SOLVED">**Two methods, solved together.** Some sheets were placed by a resident
  clicking landmarks on a web map. Others were placed by correlating one sheet's
  photographed ground against its neighbour's, by FFT. All [7](SOURCES.md#F-4c27a47dfd) were then solved
  together, and where they overlap they now agree to [22.6](SOURCES.md#F-69c790d829) m RMS.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-SOLVED "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-CONVERGE">**It converges.** Re-running the whole alignment after applying the
  answer asks for further corrections of **[-1](SOURCES.md#F-f12df7b192) to [+1](SOURCES.md#F-fb4bae9860) m**. A wrong
  registration keeps asking to move.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-CONVERGE "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-WATERCHECK">**A check that was never optimised for.** Some of the model's
  painted flood depth falls on open water, which is an error by construction — water standing
  on water. Before the adjustment that was [1.56](SOURCES.md#F-d3fae26113) km². After, **[1.21](SOURCES.md#F-2b9526ca3f) km², a
  [22](SOURCES.md#F-d5f71a3c01)% reduction.** Nothing in the alignment was trying to
  improve it. It is measured against the city's own water polygons, which the alignment
  never reads. The current build reports [1.31](SOURCES.md#F-fcd8ec8568) km².</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-WATERCHECK "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-LOADBEARING">Checks with unrelated failure modes, agreeing: that is what makes a
number load-bearing — not the authority of whoever produced it, and not the sophistication of
the method.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-LOADBEARING "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-NEVERTHIS">A residual estimator can never have this. That is the argument of this page in one line.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-NEVERTHIS "What this claim rests on")</sup>

---

## The same standard, turned around

<span class="claim" data-claim="C-LR-R-OWN-INTRO">It would be dishonest to describe this test and not apply it here. The
following claims on this site currently have **no independent check**, and should be read
accordingly:</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OWN-INTRO "What this claim rests on")</sup>

- <span class="claim" data-claim="C-LR-R-OWN-CEILING">**The ceiling of [30](SOURCES.md#F-bf6bf591f1)%** on agriculture's share of nitrogen
  reaching the sea. It depends entirely on our own enumeration of [20](SOURCES.md#F-c09b9f4a15) pathways being
  right, and on our own bounds for the [10](SOURCES.md#F-af476ddfa6) that carry numbers. No independent check
  of the enumeration is recorded.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OWN-CEILING "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-OWN-WAVES">**The wave and bed-shear model.** Computed exceedance frequencies
  against literature values for critical shear stress. No observation of sediment actually
  moving. The live-bed versus dead-bed *ratio* is robust; the absolute hours are not.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OWN-WAVES "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-OWN-FLUSH">**The [73](SOURCES.md#F-d44427aa79)-day retention figure for Køge Bugt.** One coarse
  global model. And the same method put Det Sydfynske Øhav mid-range, at [8.7](SOURCES.md#F-401df48142) days.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OWN-FLUSH "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-OWN-LAG">**The [12](SOURCES.md#F-c6c72c26e2)-hour transport lag** between overflow-scale rain
  and southward flow: [145](SOURCES.md#F-d5db6302f0) event-hours, at lags from [0](SOURCES.md#F-73d4cb66dc) to [72](SOURCES.md#F-2b1ffa732a) hours. The
  attempt to extend the current record backwards using a wind index failed, and is reported
  as a negative result. Everything said here about currents rests on [4](SOURCES.md#F-be18832190) years of
  record.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OWN-LAG "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-OWN-NORREBRO">**The Nørrebro flood sheet.** Every attempt to correlate it against a neighbour came out flat. It has since been placed from [2](SOURCES.md#F-fee62b85f5) control points a reader supplied, with a standard error of [14](SOURCES.md#F-ca81107c43) m, but it is still the one sheet not known to be consistent with the other [6](SOURCES.md#F-402f7d05dd), and it is marked as such.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OWN-NORREBRO "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-OWN-MUSSEL">**The extractive-aquaculture area estimate.** A stoichiometric
  calculation, not compared against what a working mussel farm actually removes.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OWN-MUSSEL "What this claim rests on")</sup>
- <span class="claim" data-claim="C-LR-R-OWN-FEDTEMOG">**The seasonal argument about fedtemøg.** No shore-condition
  series was found in any source this project surveyed, so the seasonal claim cannot
  presently be checked either.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OWN-FEDTEMOG "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-OWN-CLOSE">Several of those could be checked cheaply. That they have not been is a
fact about this project, not a defence of it.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-OWN-CLOSE "What this claim rests on")</sup>

---

## A note on who this is about

<span class="claim" data-claim="C-LR-R-WHO-DOCS">Every limitation of the Danish method described here was found by
**reading a document that its authors wrote and published**. The [25](SOURCES.md#F-8be24edb3a)% is discoverable
because the method document states it and explains the reasoning. The averaging of
indicators is discoverable because they wrote down that it reduces the risk of
over-implementation. The exclusion of eelgrass is discoverable because they justified it, in
print, by its slow response time. The sampling exclusions in the toxicant figures are
discoverable because the agency listed them.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-WHO-DOCS "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-WHO-GOOD">That is people documenting their own limitations in public. It is what
good work looks like, and it is the only reason any of this could be audited at all.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-WHO-GOOD "What this claim rests on")</sup>
<span class="claim" data-claim="C-LR-R-ANACHRONISM">Holding past work to a standard that did not exist when it was done is anachronism, not criticism.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-ANACHRONISM "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-USE">**The criticism here is of the use of a number, not its production.** A method
that states in its own text that it averages indicators to avoid over-implementation, and
that the oxygen requirement is a judged constant, can become *"agriculture causes
[70](SOURCES.md#F-7e1b8a8a83)% of the mess on the beach"* only after it leaves the scientists' hands.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-USE "What this claim rests on")</sup>

<span class="claim" data-claim="C-LR-R-DISTANCE">That distance — between what the document says and what is then said with it — is the finding. The document is the evidence for it, not the target.</span><sup class="claim-mark">[†](CLAIMS.md#C-LR-R-DISTANCE "What this claim rests on")</sup>
