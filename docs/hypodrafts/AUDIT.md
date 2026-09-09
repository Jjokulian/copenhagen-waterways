# Audit of the drafts

Every file in `hypodrafts/` and `openproblems/`, checked against the standards in
[`../AGENT_BRIEF.md`](../AGENT_BRIEF.md) — which **none of their authors had**. They were
briefed on null discipline and their own hypothesis's trap; not on applefication, not on
naming what kind of thing a quantity is, and not on the steelman rule.

Verdicts are **sound** / **needs a stated fix** / **has an error**. Only defects are
listed. Nothing here rewrites a draft.

---

## Per draft

**A1 — needs a stated fix.** Its primary-source work is correct and independently
verified: DK-QNP takes the field surplus as an input, and SR353 ch.6 reports the
resulting correlation as a finding. Its scoping is also correct — *"this does not show
the attribution is wrong. It shows Figur 6.7 D cannot be what shows it is right."* But it
predates the Windolf reading and therefore does not know that the attribution **does**
have independent support (measured estuary N falling 24–62%, heterogeneous
response timing). **Fix:** cross-reference `../NITROGEN.md` §2, so the draft cannot be
read as implying the attribution is unevidenced. Its null is arithmetic (publication
rounding), which is the right kind for a residual-growth test — the zero
permutation-count is not a defect.

**A1b — sound.** Written after the correction; states what it would not license.

**B1 — needs a stated fix.** The design is strong: exposure enters only as the
combined-vs-separate class of the nearest outfall and as an a-priori critical rainfall
depth, so rainfall cancels in the contrast. **But its central data claim is
unverified.** The parent queried `[latest].[timeseries_MonitoringResult]` at
`discodata.eea.europa.eu/sql` and got `Invalid object name`. Every figure in its data row
— 172,440 samples, 1,437 sites, 26,301 at LOD — rests on that table resolving. **Fix:**
mark the EEA row unverified until the correct object name is established. The
`shortTermPollutionSample` claim, which is the most interesting thing in the draft, is
also unconfirmed.

**C1 — sound, and the strongest single finding in the set.** It refused the published
iltsvind extent as a response variable because DCE's criterion is oxygen below 4 mg/l
*in stratified bottom water* — stratification inside the definition of the dependent
variable. It names its own null as non-zero (fully-ventilated saturation) rather than
assuming zero.

**C4 — sound.** It found the Gotland unit and provenance errors that the parent then
verified and fixed. Its p-floor of 1/32 is stated honestly against an effective event
count of 2–3.

**C6 — sound; best null work in the set.** Excluded archived `oxysat_bed` as an outcome
because it shares two of three inputs with the statistic, and used it only as a
consistency check. Its 23.6-fold / 15.5-fold figures are the ones now carried in
`../CONSTRUCTED.md`; they supersede the parent's earlier 23/14.

**D1 — sound.** Breaks the productivity confound three ways, including a substrate ×
effort interaction that the confound does not predict.

**D7 — sound.** Correctly says the *monthly panel* carries no turbidity while identifying
`Turbiditet` in the raw CTD — those are not in conflict. Found the Secchi censoring the
parent then verified (21.36% shallow vs 0.36% deep).

**F3 — sound.** Avoids the clarity-indicator circularity by using cover rather than depth
limit, and states the part it could not remove.

**G1 — sound.** Independently re-derived the station split as 282/480, explicitly flagged
the disagreement with the on-file 293/481, and called it threshold-dependent. That is the
correct handling and the other two drafts should have done the same.

**I1 — needs a stated fix.** It inherits **293 summer-peaked / 481 year-round** as
established fact in its opening. That figure *is* reproducible — I recover exactly
293/481 under its stated rule (all 9 variables, ≥24 observations, R>0.5 with peak Jun–Sep
and Z>3 / R<0.2) — but the draft neither states the rule nor notes that G1 and L3 derived
different numbers. **Fix:** state the definition inline and cite it as one convention
among several. Its own methodological work is sound: it dissolves the classification
circularity by defining the balanced panel on *presence*, which is observable per era.

**I3 — needs a stated fix.** Line 53 records *"Class 6: no time of day"* as a property of
the archive. That is true of the **CTD extract** and not established for ODA as a whole:
the topic enumeration records marine water chemistry (`Emne_10_11`) as carrying
`Startdato + Startklok`. **Fix:** scope the claim to the CTD extract and note the
unfetched topic. The rest — the inverted marginal, the 4.3× swing from count alone — is
sound and was verified by its own pilot.

**K1 — sound.** The DIATO/CHL finding is correct; the parent verified within-bin ratio
spread at 6.3×10⁻⁴. Its claim that OBIS returns eMoF cell counts under `&mof=true`
remains unverified.

**L3 — HAS AN ERROR.** Its station split of **426 summer-peaked / 427 year-round** is
impossible under the definition it states. Only **488** `oxy_bed` stations have ≥24
observations; 426 + 427 = 853 exceeds that. The numbers are reachable only with **no
minimum observation count**, and at that setting the classification is meaningless:

| stations with R>0.5, no minimum | 644 |
|---|---|
| of which N = 1 observation | **254** |
| of which N ≤ 3 | **369** |
| median N in the group | **3** |

**With N = 1 the resultant length R is exactly 1 by construction** — all the mass sits in
one calendar month. Over half of L3's "summer-peaked" group is stations where the
seasonality statistic measures nothing but scarcity. **Fix:** re-run the composition
check with a stated minimum (≥24 gives 89/306 on `oxy_bed`), or drop the split arm and
rely on the 186-station core panel, which is unaffected. **The draft's headline result is
not touched by this** — the AR(1) finding that sign-flipping windows occur in 100% of
no-trend simulations stands, and was independently reimplemented.

**Z8 — sound.** Extracted TA M06 as a primary document rather than summarising it, and
names its residual honestly: *"nothing is in absorption units, so it is a variance
apportionment, not a budget."*

**A7 — sound.** Downloaded and parsed the Zenodo flux dataset rather than citing it, then
established it is nearly useless for Denmark (5 of 59 stations west of 15.5°E, none in
Kattegat, Belts, Sound or any fjord). A negative with numbers.

**E7 — sound.** Pre-commits to a reclassification test that would make the file wrong.

**J1 — sound.** Took the new-metric option seriously, wrote the metric down, then killed
it with four computed reasons rather than asserting absence. Its per-parameter counts
differ from the parent's full scan by 67–160 rows (malformed-row handling); immaterial.

**R6 — sound.** Found that Denmark ran a national standard method for R6's own variables
1998–2003 and discontinued it, and states a reclassification test in advance.

---

## What the set gets systematically wrong

**1. Inherited figures are not re-derived, and the one convention that matters was never
fixed.** Three drafts use a summer/year-round station split and get 293/481, 282/480 and
426/427. All three are defensible arithmetic on different rules; none of the rules is
written down anywhere as *the* convention. G1 flagged it, L3 flagged it and got it wrong
anyway, I1 inherited it silently. **This is the applefication failure in its purest form:
a category everyone uses and nobody defines.** A single line in `AGENT_BRIEF.md` fixing
the rule would remove a cross-draft contradiction and one hard error.

**2. Absence is scoped to the search, not the world — except where it isn't.** D7 gets
this right ("the monthly panel carries no turbidity"), I3 gets it wrong ("no time of
day"). The difference is one clause. Every absence claim in these files should name the
*file* it is absent from, never "the archive".

**3. Quantity kinds are used correctly but almost never named.** The drafts avoid the
traps in practice — C6 excludes a derived channel, C1 refuses a threshold class with the
predictor inside it, Z8 calls its residual a variance apportionment — but they do it
case-by-case rather than by labelling. No draft carries a line saying *this quantity is a
norm product*, *this one is a residual*. The behaviour is right; the vocabulary that
would make it checkable by a reader is missing.

**4. The (B) files steelman better than the (A) files.** E7 and R6 pre-commit to what
would make them wrong. A7 and J1 come close. Among the (A) drafts, only C6, B1 and C1
seriously argue against their own design. **The asymmetry is backwards** — a draft that
proposes a test has more room to be wrong than one that declines to.

**5. Nobody checked anyone else.** Sixteen files, three incompatible station splits, and
one arithmetic impossibility that a single `wc`-scale check would have caught. The set was
written in parallel with no cross-reading, which is the right way to get independence and
the wrong way to get consistency. **This audit is the missing step, and it should run
after every batch rather than once.**
