#!/usr/bin/env python3
"""Writes docs/hypodrafts/AUDIT.md: a hypothesis draft, as generated text.

Every hypothesis ID is a checked reference, every chemical species a checked
species, and every number either read live or quoted from the page as committed
({q:…@@…}, a located quotation - see draftkit.py) because nothing in the repository stores it yet.

    python3 scripts/pages/hypodraft_audit.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import draftkit

REL = "docs/hypodrafts/AUDIT.md"
TEXT = r"""# Audit of the drafts

Every file in `hypodrafts/` and `openproblems/`, checked against the standards in
[`../AGENT_BRIEF.md`](../AGENT_BRIEF.md) — which **none of their authors had**. They were
briefed on null discipline and their own hypothesis's trap; not on applefication, not on
naming what kind of thing a quantity is, and not on the steelman rule.

Verdicts are **sound** / **needs a stated fix** / **has an error**. Only defects are
listed. Nothing here rewrites a draft.

---

## Per draft

**{ref:A1} — needs a stated fix.** Its primary-source work is correct and independently
verified: DK-QNP takes the field surplus as an input, and `SR353 ch.6` reports the
resulting correlation as a finding. Its scoping is also correct — *"this does not show
the attribution is wrong. It shows `Figur 6.7 D` cannot be what shows it is right."* But it
predates the Windolf reading and therefore does not know that the attribution **does**
have independent support (measured estuary N falling {q:estuary N falling @@, heterogeneous response}, heterogeneous
response timing). **Fix:** cross-reference `../NITROGEN.md` §2, so the draft cannot be
read as implying the attribution is unevidenced. Its null is arithmetic (publication
rounding), which is the right kind for a residual-growth test — the zero
permutation-count is not a defect.

**A1b — sound.** Written after the correction; states what it would not license.

**{ref:B1} — needs a stated fix.** The design is strong: exposure enters only as the
combined-vs-separate class of the nearest outfall and as an a-priori critical rainfall
depth, so rainfall cancels in the contrast. **But its central data claim is
unverified.** The parent queried `[latest].[timeseries_MonitoringResult]` at
`discodata.eea.europa.eu/sql` and got `Invalid object name`. Every figure in its data row
— {q:data row — @@ at LOD —} at LOD — rests on that table resolving. **Fix:**
mark the EEA row unverified until the correct object name is established. The
`shortTermPollutionSample` claim, which is the most interesting thing in the draft, is
also unconfirmed.

**{ref:C1} — sound, and the strongest single finding in the set.** It refused the published
iltsvind extent as a response variable because DCE's criterion is oxygen below {q:oxygen below @@ *in stratified}
*in stratified bottom water* — stratification inside the definition of the dependent
variable. It names its own null as non-zero (fully-ventilated saturation) rather than
assuming zero.

**{ref:C4} — sound.** It found the Gotland unit and provenance errors that the parent then
verified and fixed. Its p-floor of {q:Its p-floor of @@ is stated honestly} is stated honestly against an effective event
count of {q:effective event count of @@}.

**{ref:C6} — sound; best null work in the set.** Excluded archived `oxysat_bed` as an outcome
because it shares two of three inputs with the statistic, and used it only as a
consistency check. Its {q:check. Its @@ figures are} figures are the ones now carried in
`../CONSTRUCTED.md`; they supersede the parent's earlier {q:the parent's earlier @@}.

**{ref:D1} — sound.** Breaks the productivity confound three ways, including a substrate ×
effort interaction that the confound does not predict.

**{ref:D7} — sound.** Correctly says the *monthly panel* carries no turbidity while identifying
`Turbiditet` in the raw CTD — those are not in conflict. Found the Secchi censoring the
parent then verified ({q:then verified (@@ shallow vs} shallow vs {q:(21.36% shallow vs @@ deep). **F3 —} deep).

**{ref:F3} — sound.** Avoids the clarity-indicator circularity by using cover rather than depth
limit, and states the part it could not remove.

**{ref:G1} — sound.** Independently re-derived the station split as {q:station split as @@, explicitly flagged}, explicitly flagged
the disagreement with the on-file {q:the on-file @@, and}, and called it threshold-dependent. That is the
correct handling and the other two drafts should have done the same.

**{ref:I1} — needs a stated fix.** It inherits **{q:inherits **@@ summer-peaked /} summer-peaked / {q:summer-peaked / @@ year-round** as} year-round** as
established fact in its opening. That figure *is* reproducible — I recover exactly
{q:recover exactly @@ under its} under its stated rule (all {q:stated rule (all @@, ≥24 observations,}, {q:(all 9 variables, @@, R>0.5 with}, {q:observations, @@ with peak} with peak Jun–Sep
and {q:Jun–Sep and @@) —}) — but the draft neither states the rule nor notes that {ref:G1} and {ref:L3} derived
different numbers. **Fix:** state the definition inline and cite it as one convention
among several. Its own methodological work is sound: it dissolves the classification
circularity by defining the balanced panel on *presence*, which is observable per era.

**{ref:I3} — needs a stated fix.** Line {q:fix.** Line @@ records *"Class} records *"Class 6: no time of day"* as a property of
the archive. That is true of the **CTD extract** and not established for ODA as a whole:
the topic enumeration records marine water chemistry (`Emne_10_11`) as carrying
`Startdato + Startklok`. **Fix:** scope the claim to the CTD extract and note the
unfetched topic. The rest — the inverted marginal, the {q:marginal, the @@× swing}× swing from count alone — is
sound and was verified by its own pilot.

**{ref:K1} — sound.** The DIATO/CHL finding is correct; the parent verified within-bin ratio
spread at {q:ratio spread at @@. Its claim}. Its claim that OBIS returns eMoF cell counts under `&mof=true`
remains unverified.

**{ref:L3} — HAS AN ERROR.** Its station split of **{q:split of **@@ summer-peaked /} summer-peaked / {q:summer-peaked / @@ year-round** is} year-round** is
impossible under the definition it states. Only **{q:Only **@@** `oxy_bed`}** `oxy_bed` stations have {q:stations have @@ observations;}
observations; {q:observations; @@ exceeds that.} exceeds that. The numbers are reachable only with **no
minimum observation count**, and at that setting the classification is meaningless:

| stations with {q:| stations with @@, no minimum}, no minimum | {q:no minimum | @@ | |---|---| |} |
|---|---|
| of which N = {q:|---|---| | of which N = @@} observation | **{q:1 observation | **@@** | | of}** |
| of which N ≤ {q:| | of which N ≤ @@} | **{q:≤ 3 | **@@** | | median}** |
| median N in the group | **`3`** |

**With N = {q:**With N = @@ the resultant length} the resultant length R is exactly {q:R is exactly @@ by construction** —} by construction** — all the mass sits in
one calendar month. Over half of {ref:L3}'s "summer-peaked" group is stations where the
seasonality statistic measures nothing but scarcity. **Fix:** re-run the composition
check with a stated minimum ({q:with a stated minimum (@@} gives {q:gives @@ on `oxy_bed`),} on `oxy_bed`), or drop the split arm and
rely on the {q:on the @@-station core}-station core panel, which is unaffected. **The draft's headline result is
not touched by this** — the `AR(1)` finding that sign-flipping windows occur in {q:windows occur in @@ of no-trend simulations} of
no-trend simulations stands, and was independently reimplemented.

**{ref:Z8} — sound.** Extracted TA M06 as a primary document rather than summarising it, and
names its residual honestly: *"nothing is in absorption units, so it is a variance
apportionment, not a budget."*

**{ref:A7} — sound.** Downloaded and parsed the Zenodo flux dataset rather than citing it, then
established it is nearly useless for Denmark ({q:for Denmark (@@ west of} west of {q:stations west of @@, none in}, none in
Kattegat, Belts, Sound or any fjord). A negative with numbers.

**{ref:E7} — sound.** Pre-commits to a reclassification test that would make the file wrong.

**{ref:J1} — sound.** Took the new-metric option seriously, wrote the metric down, then killed
it with four computed reasons rather than asserting absence. Its per-parameter counts
differ from the parent's full scan by {q:scan by @@ (malformed-row handling);} (malformed-row handling); immaterial.

**{ref:R6} — sound.** Found that Denmark ran a national standard method for {ref:R6}'s own variables
1998–2003 and discontinued it, and states a reclassification test in advance.

---

## What the set gets systematically wrong

1. **Inherited figures are not re-derived, and the one convention that matters was never
fixed.** Three drafts use a summer/year-round station split and get {q:and get @@ and} and
{q:@@. All three are}. All three are defensible arithmetic on different rules; none of the rules is
written down anywhere as *the* convention. {ref:G1} flagged it, {ref:L3} flagged it and got it wrong
anyway, {ref:I1} inherited it silently. **This is the applefication failure in its purest form:
a category everyone uses and nobody defines.** A single line in `AGENT_BRIEF.md` fixing
the rule would remove a cross-draft contradiction and one hard error.

2. **Absence is scoped to the search, not the world — except where it isn't.** {ref:D7} gets
this right ("the monthly panel carries no turbidity"), {ref:I3} gets it wrong ("no time of
day"). The difference is one clause. Every absence claim in these files should name the
*file* it is absent from, never "the archive".

3. **Quantity kinds are used correctly but almost never named.** The drafts avoid the
traps in practice — {ref:C6} excludes a derived channel, {ref:C1} refuses a threshold class with the
predictor inside it, {ref:Z8} calls its residual a variance apportionment — but they do it
case-by-case rather than by labelling. No draft carries a line saying *this quantity is a
norm product*, *this one is a residual*. The behaviour is right; the vocabulary that
would make it checkable by a reader is missing.

4. **The (B) files steelman better than the (A) files.** {ref:E7} and {ref:R6} pre-commit to what
would make them wrong. {ref:A7} and {ref:J1} come close. Among the (A) drafts, only {ref:C6}, {ref:B1} and {ref:C1}
seriously argue against their own design. **The asymmetry is backwards** — a draft that
proposes a test has more room to be wrong than one that declines to.

5. **Nobody checked anyone else.** Sixteen files, three incompatible station splits, and
one arithmetic impossibility that a single `wc`-scale check would have caught. The set was
written in parallel with no cross-reading, which is the right way to get independence and
the wrong way to get consistency. **This audit is the missing step, and it should run
after every batch rather than once.**
"""


def main(argv):
    return 0 if draftkit.build(REL, TEXT) is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
