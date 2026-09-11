# Audit of the drafts

*Numbers shown as quotations are carried from this page as committed at `7c4dd30`: nothing in the repository stores them yet, so each says what the page said, not that it was re-derived.*

Every file in `hypodrafts/` and `openproblems/`, checked against the standards in
[`../AGENT_BRIEF.md`](../AGENT_BRIEF.md) — which **none of their authors had**. They were
briefed on null discipline and their own hypothesis's trap; not on applefication, not on
naming what kind of thing a quantity is, and not on the steelman rule.

Verdicts are **sound** / **needs a stated fix** / **has an error**. Only defects are
listed. Nothing here rewrites a draft.

---

## Per draft

**[A1](../hypodrafts/A1.md "Danish land-based nitrogen load") — needs a stated fix.** Its primary-source work is correct and independently
verified: DK-QNP takes the field surplus as an input, and `SR353 ch.6` reports the
resulting correlation as a finding. Its scoping is also correct — *"this does not show
the attribution is wrong. It shows `Figur 6.7 D` cannot be what shows it is right."* But it
predates the Windolf reading and therefore does not know that the attribution **does**
have independent support (measured estuary N falling [24–62%](../SOURCES.md#F-ca6df210a3), heterogeneous
response timing). **Fix:** cross-reference `../NITROGEN.md` §2, so the draft cannot be
read as implying the attribution is unevidenced. Its null is arithmetic (publication
rounding), which is the right kind for a residual-growth test — the zero
permutation-count is not a defect.

**A1b — sound.** Written after the correction; states what it would not license.

**[B1](../hypodrafts/B1.md "Combined sewer overflow") — needs a stated fix.** The design is strong: exposure enters only as the
combined-vs-separate class of the nearest outfall and as an a-priori critical rainfall
depth, so rainfall cancels in the contrast. **But its central data claim is
unverified.** The parent queried `[latest].[timeseries_MonitoringResult]` at
`discodata.eea.europa.eu/sql` and got `Invalid object name`. Every figure in its data row
— [172,440 samples, 1,437 sites, 26,301](../SOURCES.md#F-ca3f46932e) at LOD — rests on that table resolving. **Fix:**
mark the EEA row unverified until the correct object name is established. The
`shortTermPollutionSample` claim, which is the most interesting thing in the draft, is
also unconfirmed.

**[C1](../hypodrafts/C1.md "Stratification strength") — sound, and the strongest single finding in the set.** It refused the published
iltsvind extent as a response variable because DCE's criterion is oxygen below [4 mg/l](../SOURCES.md#F-70418e26b0)
*in stratified bottom water* — stratification inside the definition of the dependent
variable. It names its own null as non-zero (fully-ventilated saturation) rather than
assuming zero.

**[C4](../hypodrafts/C4.md "Baltic inflow events") — sound.** It found the Gotland unit and provenance errors that the parent then
verified and fixed. Its p-floor of [1/32](../SOURCES.md#F-3c3fba6d75) is stated honestly against an effective event
count of [2–3](../SOURCES.md#F-76c86c6b4b).

**[C6](../hypodrafts/C6.md "Water temperature and solubility") — sound; best null work in the set.** Excluded archived `oxysat_bed` as an outcome
because it shares two of three inputs with the statistic, and used it only as a
consistency check. Its [23.6-fold / 15.5-fold](../SOURCES.md#F-c1f744fb1d) figures are the ones now carried in
`../CONSTRUCTED.md`; they supersede the parent's earlier [23/14](../SOURCES.md#F-fd257e97cf).

**[D1](../hypodrafts/D1.md "Bottom trawling") — sound.** Breaks the productivity confound three ways, including a substrate ×
effort interaction that the confound does not predict.

**[D7](../hypodrafts/D7.md "Storm-driven resuspension") — sound.** Correctly says the *monthly panel* carries no turbidity while identifying
`Turbiditet` in the raw CTD — those are not in conflict. Found the Secchi censoring the
parent then verified ([21.36%](../SOURCES.md#F-57fc4a7e54) shallow vs [0.36%](../SOURCES.md#F-7ce9bde1bd) deep).

**[F3](../hypodrafts/F3.md "Loss of eelgrass and macroalgae") — sound.** Avoids the clarity-indicator circularity by using cover rather than depth
limit, and states the part it could not remove.

**[G1](../hypodrafts/G1.md "Warming") — sound.** Independently re-derived the station split as [282/480](../SOURCES.md#F-1bbc85bcb4), explicitly flagged
the disagreement with the on-file [293/481](../SOURCES.md#F-a5c8865b89), and called it threshold-dependent. That is the
correct handling and the other two drafts should have done the same.

**[I1](../hypodrafts/I1.md "Changing station network") — needs a stated fix.** It inherits **[293](../SOURCES.md#F-87fe730a6b) summer-peaked / [481](../SOURCES.md#F-56757b79d4) year-round** as
established fact in its opening. That figure *is* reproducible — I recover exactly
[293/481](../SOURCES.md#F-7a15f42f16) under its stated rule (all [9 variables](../SOURCES.md#F-7614228928), [≥24 observations](../SOURCES.md#F-39285709a9), [R>0.5](../SOURCES.md#F-25e7161f30) with peak Jun–Sep
and [Z>3 / R<0.2](../SOURCES.md#F-91914414a2)) — but the draft neither states the rule nor notes that [G1](../hypodrafts/G1.md "Warming") and [L3](../hypodrafts/L3.md "The trend depends on the start year") derived
different numbers. **Fix:** state the definition inline and cite it as one convention
among several. Its own methodological work is sound: it dissolves the classification
circularity by defining the balanced panel on *presence*, which is observable per era.

**[I3](../hypodrafts/I3.md "Changing sampling frequency and season") — needs a stated fix.** Line [53](../SOURCES.md#F-83a912da8e) records *"Class 6: no time of day"* as a property of
the archive. That is true of the **CTD extract** and not established for ODA as a whole:
the topic enumeration records marine water chemistry (`Emne_10_11`) as carrying
`Startdato + Startklok`. **Fix:** scope the claim to the CTD extract and note the
unfetched topic. The rest — the inverted marginal, the [4.3](../SOURCES.md#F-800f61b99a)× swing from count alone — is
sound and was verified by its own pilot.

**[K1](../hypodrafts/K1.md "Silicon depletion and the diatom-to-flagellate shift") — sound.** The DIATO/CHL finding is correct; the parent verified within-bin ratio
spread at [6.3×10⁻⁴](../SOURCES.md#F-c0ef6843c1). Its claim that OBIS returns eMoF cell counts under `&mof=true`
remains unverified.

**[L3](../hypodrafts/L3.md "The trend depends on the start year") — HAS AN ERROR.** Its station split of **[426](../SOURCES.md#F-b6c9fe712d) summer-peaked / [427](../SOURCES.md#F-6f3ed35c75) year-round** is
impossible under the definition it states. Only **[488](../SOURCES.md#F-f9951e0722)** `oxy_bed` stations have [≥24](../SOURCES.md#F-9a49bc20ab)
observations; [426 + 427 = 853](../SOURCES.md#F-64cf34031c) exceeds that. The numbers are reachable only with **no
minimum observation count**, and at that setting the classification is meaningless:

| stations with [R>0.5](../SOURCES.md#F-25dc5d0276), no minimum | [644](../SOURCES.md#F-d0df378179) |
|---|---|
| of which N = [1](../SOURCES.md#F-db9aab4e55) observation | **[254](../SOURCES.md#F-e71dc01ea8)** |
| of which N ≤ [3](../SOURCES.md#F-67686353e9) | **[369](../SOURCES.md#F-bd66b78b68)** |
| median N in the group | **`3`** |

**With N = [1](../SOURCES.md#F-15ecb2eea1) the resultant length R is exactly [1](../SOURCES.md#F-ad83fedee7) by construction** — all the mass sits in
one calendar month. Over half of [L3](../hypodrafts/L3.md "The trend depends on the start year")'s "summer-peaked" group is stations where the
seasonality statistic measures nothing but scarcity. **Fix:** re-run the composition
check with a stated minimum ([≥24](../SOURCES.md#F-c2e133deea) gives [89/306](../SOURCES.md#F-a306a0633f) on `oxy_bed`), or drop the split arm and
rely on the [186](../SOURCES.md#F-79e0ae347d)-station core panel, which is unaffected. **The draft's headline result is
not touched by this** — the `AR(1)` finding that sign-flipping windows occur in [100%](../SOURCES.md#F-9cb56eb55a) of
no-trend simulations stands, and was independently reimplemented.

**[Z8](../hypodrafts/Z8.md "The attenuation budget is never partitioned") — sound.** Extracted TA M06 as a primary document rather than summarising it, and
names its residual honestly: *"nothing is in absorption units, so it is a variance
apportionment, not a budget."*

**[A7](../openproblems/A7.md "Sediment nutrient regeneration") — sound.** Downloaded and parsed the Zenodo flux dataset rather than citing it, then
established it is nearly useless for Denmark ([5 of 59 stations](../SOURCES.md#F-975f082649) west of [15.5°E](../SOURCES.md#F-663960dc88), none in
Kattegat, Belts, Sound or any fjord). A negative with numbers.

**[E7](../openproblems/E7.md "Pesticides and degradation products") — sound.** Pre-commits to a reclassification test that would make the file wrong.

**[J1](../openproblems/J1.md "Transparent exopolymer particles and marine gel") — sound.** Took the new-metric option seriously, wrote the metric down, then killed
it with four computed reasons rather than asserting absence. Its per-parameter counts
differ from the parent's full scan by [67–160 rows](../SOURCES.md#F-6fed023a03) (malformed-row handling); immaterial.

**[R6](../openproblems/R6.md "Sulphide locks the iron that would hold the phosphate") — sound.** Found that Denmark ran a national standard method for [R6](../openproblems/R6.md "Sulphide locks the iron that would hold the phosphate")'s own variables
1998–2003 and discontinued it, and states a reclassification test in advance.

---

## What the set gets systematically wrong

1. **Inherited figures are not re-derived, and the one convention that matters was never
fixed.** Three drafts use a summer/year-round station split and get [293/481, 282/480](../SOURCES.md#F-cf320e40b5) and
[426/427](../SOURCES.md#F-062ced6537). All three are defensible arithmetic on different rules; none of the rules is
written down anywhere as *the* convention. [G1](../hypodrafts/G1.md "Warming") flagged it, [L3](../hypodrafts/L3.md "The trend depends on the start year") flagged it and got it wrong
anyway, [I1](../hypodrafts/I1.md "Changing station network") inherited it silently. **This is the applefication failure in its purest form:
a category everyone uses and nobody defines.** A single line in `AGENT_BRIEF.md` fixing
the rule would remove a cross-draft contradiction and one hard error.

2. **Absence is scoped to the search, not the world — except where it isn't.** [D7](../hypodrafts/D7.md "Storm-driven resuspension") gets
this right ("the monthly panel carries no turbidity"), [I3](../hypodrafts/I3.md "Changing sampling frequency and season") gets it wrong ("no time of
day"). The difference is one clause. Every absence claim in these files should name the
*file* it is absent from, never "the archive".

3. **Quantity kinds are used correctly but almost never named.** The drafts avoid the
traps in practice — [C6](../hypodrafts/C6.md "Water temperature and solubility") excludes a derived channel, [C1](../hypodrafts/C1.md "Stratification strength") refuses a threshold class with the
predictor inside it, [Z8](../hypodrafts/Z8.md "The attenuation budget is never partitioned") calls its residual a variance apportionment — but they do it
case-by-case rather than by labelling. No draft carries a line saying *this quantity is a
norm product*, *this one is a residual*. The behaviour is right; the vocabulary that
would make it checkable by a reader is missing.

4. **The (B) files steelman better than the (A) files.** [E7](../openproblems/E7.md "Pesticides and degradation products") and [R6](../openproblems/R6.md "Sulphide locks the iron that would hold the phosphate") pre-commit to what
would make them wrong. [A7](../openproblems/A7.md "Sediment nutrient regeneration") and [J1](../openproblems/J1.md "Transparent exopolymer particles and marine gel") come close. Among the (A) drafts, only [C6](../hypodrafts/C6.md "Water temperature and solubility"), [B1](../hypodrafts/B1.md "Combined sewer overflow") and [C1](../hypodrafts/C1.md "Stratification strength")
seriously argue against their own design. **The asymmetry is backwards** — a draft that
proposes a test has more room to be wrong than one that declines to.

5. **Nobody checked anyone else.** Sixteen files, three incompatible station splits, and
one arithmetic impossibility that a single `wc`-scale check would have caught. The set was
written in parallel with no cross-reading, which is the right way to get independence and
the wrong way to get consistency. **This audit is the missing step, and it should run
after every batch rather than once.**
