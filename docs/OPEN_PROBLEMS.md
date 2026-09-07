# Open problems

What this project could not settle, why, and what would settle it. Hand-maintained rather
than generated — these are questions, not outputs.

Ordered roughly by how much the answer would change the picture.

---

## 1. The convergence in Køge Bugt

**The claim.** Wind-driven southward surface transport meets the northward Baltic outflow,
and the convergence accumulates fine sediment and floating material in Køge Bugt. The bay
functions as a collecting basin for material mobilised elsewhere, not only for its own
discharge.

**Why it matters.** Everything computed in `SEABED.md` is *local* resuspension from local
wind. If a large share of the sediment and its contaminant load arrives from outside the
bay, then local interventions cannot fix it, and the relevant catchment is far larger than
the one draining into it.

**What would settle it.** Baltic Sea physics reanalysis — Copernicus Marine (CMEMS) has
current fields at adequate resolution, behind free registration. With hourly currents plus
the wind record already fetched, a particle-tracking run would show directly whether
Køge Bugt is a convergence zone and where its material comes from.

**Second-best.** Sediment provenance. An accumulation zone shows fine grain size, high
organic content and elevated metals relative to its surroundings; fingerprinting could
distinguish locally-derived from imported material. Requires sediment samples.

---

## 2. Why the extremes did not respond to a halved load

Land-based nitrogen supply is down roughly 50% since 1990. September oxygen-depletion
extent in 2023 and 2024 was at or above the level of 1989, 2000 and 2002, when the load
was about double. Meanwhile 2025 came in at roughly a third of 2024's area. Neither the
absence of a trend nor the size of the year-to-year swing has an accepted explanation.

Three candidates — legacy lag, warming, loss of assimilative state — are laid out in
[CAUSATION.md](#CAUSATION.md). Lag fails on elapsed time. The other two have no term
anywhere in a source apportionment, because neither is a source.

**Why it matters.** This is the only empirical test of the nitrogen-dominant model that
anyone has actually run, and it has been running for thirty-five years. If load is not
the dominant control on the extremes, then the apportionment is answering a question
about attribution while the policy is asking a question about outcomes.

**What would settle it.** A regression of annual iltsvind extent on flow-normalised load,
wind-work over the stratified season, and bottom-water temperature anomaly — with an
interaction term for state. All three series are published by DCE. No new data, no new
instruments. The regression appears not to have been published.

---

## 3. Whether "ikke registreret" means measured or unmeasured

DCE reports state no oxygen depletion registered in Køge Bugt, including in 2023, the worst
iltsvind year in twenty. That is probably accurate — the bay is shallow and may never
stratify long enough to qualify — but *"we measured and found nothing"* and *"it is not in
the survey"* produce the identical line in a report.

**What would settle it.** The station list behind the iltsvind mapping. Whether there are
monitoring positions inside Køge Bugt at all.

---

## 4. The potency term

Nitrogen accounting has no equivalent of GWP. A kilogram delivered in February into a mixed
column counts identically to a kilogram delivered in July into a stratified fjord, though
vertical mixing across a summer pycnocline is roughly four orders of magnitude weaker.

An Oxygen Depletion Potential would need, per source and season: the fraction assimilated,
the fraction exported below the pycnocline, and the fraction remineralised where the water
is not ventilated. Each is between 0 and 1. None is computed anywhere.

**What would settle it.** Not a dataset — a modelling programme. But even a crude
seasonal weighting, applied to existing load figures, would be more informative than the
current implicit weight of 1.0 everywhere.

---

## 5. Event-based measurement of overflow

The reporting method is modelled annual volume × a fixed concentration, quality-controlled
against that same concentration, with no flow rate recorded. Sediment resuspension in a
basin is a *threshold* in flow, so the mass is plausibly dominated by a handful of events
the method averages away.

**What would settle it.** Flow-proportional sampling at a handful of structures across a
range of event sizes — videnniveau 5 in Miljøstyrelsen's own scheme, 30% uncertainty. It is
defined, it is the best method in their hierarchy, and almost nobody does it.

---

## 6. The unquantified nitrogen pathways

Ten of twenty enumerated pathways carry no number. Two are tractable:

- **Submarine groundwater discharge** — measurable with radon and radium tracers or seepage
  meters, standard practice elsewhere, not a term in the Danish marine budget.
- **Internal regeneration** — measurable with benthic flux chambers, and done in Danish
  waters, just never compiled into a nutrient budget. Probably the largest single supply to
  the productive layer.

Until at least these two are filled, no denominator exists and no percentage is meaningful.

---

## 7. The autumn die-off

Soft-bottom fauna is sampled 1 March to 31 May. The annual mortality is observed only in
its aftermath, once recolonisation has begun, so the depth of the kill — and therefore the
ratchet by which each year's hypoxia removes more of the structural life — is never
measured.

**What would settle it.** Autumn sampling at a subset of existing stations. The stations
exist; only the timing would change.

---

## 8. Fedtemøg as a condition

There is no systematic national monitoring of the shore condition at all — not extent, not
biomass, not duration, not odour. What exists is bathing-water sampling in the bathing
season, municipal beach management and complaints, all concentrated where and when people
are on beaches.

This makes every seasonal claim about fedtemøg circular. A November phenomenon would leave
almost no trace.

**What would settle it.** Cheap. Fixed-position coastal cameras with a monthly index, or a
structured citizen-reporting scheme running year-round rather than in summer.

---

## 9. There is no visual record of what high concentrations actually do

Danish monitoring produces concentrations. It does not produce images of consequence,
and the two are not substitutes.

**Korsør, 2021.** Fødevarestyrelsen found PFOS in calf meat at 156, 189 and 230 ng/g,
analysed 27 samples across beef, fish, fruit, berries, vegetables and honey, and offered
179 residents a health examination. Every one of those is a measurement of a
*concentration* — in the food, and then in the people. Nothing published records what
the animals looked like, whether they were examined beyond a meat assay, or what
symptoms if any they showed. The exposure was documented as a number in the food chain
and never as an effect in an organism.

**Parkersburg, 1998–2004**, is the counter-case, and it is the reason anyone outside a
toxicology department has heard of PFAS at all. Wilbur Tennant filmed his own herd over
years: more than 150 animals dead one at a time, blackened teeth, tumours, deformities,
calves born with white blind eyes, a creek running with foam and a discharge pipe from a
DuPont landfill. He made that record himself because no official programme covered what
was happening to him.

**Why it matters.** Dose–response at the high end is where a mechanism shows itself, and
whole-organism failure is a kind of evidence a hazard ratio cannot carry. It is also the
form of evidence that moves anything. And it is entirely absent from the Danish record —
which is this project's recurring finding arriving one layer further out: the thing that
is easy to count gets counted, and the thing that would show what it means does not.

**The asymmetry worth noting.** The *paper* record from that litigation is open. Bilott's
discovery documents were donated to UCSF's Industry Documents Library — free, fully
searchable, two PFAS collections spanning 1961–2006, including the 39 documents used in
*The Devil We Know*, alongside the tobacco and opioid archives. **The document archive is
public. The video archive is not**, and remains under copyright into the 2070s.

**What would settle it.**

- Locate the Tennant archive and establish who holds it. Both films licensed the footage,
  so a rights holder exists and has granted permission before.
- Ask Fødevarestyrelsen and DTU Fødevareinstituttet whether the Korsør animals were
  examined beyond the meat assay, and whether anything was photographed or necropsied.
- For everything since: a standing, provenanced archive of visual documentation of
  pollution effects, contributed by the people it happens to.

**This is larger than this project.** It is its own thing — *documenting pollution
effects* — and it needs an archive, a contribution standard, a provenance chain and a
licence model, none of which belong in a repository about Copenhagen's sewers. It is
recorded here because this project kept running into the gap and could not fill it. The
nearest thing here is `viz/log.html`, an offline field logger that records a shore
observation in the flood model's own vocabulary — the right shape, at approximately none
of the required scale.

---

## 10. Fat, and everything else with no nitrogen in it

*Fedtemøg* names a material. Triglycerides contain no nitrogen at all, carry roughly
2.9 g of oxygen demand per gram, float rather than settle, and do not disperse. Sewers
accumulate them as fedtpropper and release them on a flow threshold — the same hours in
which the flow bypasses the treatment works.

No national figure exists for how much leaves the system. One utility reported 25 tonnes
of fat arriving at its works in a year, which counts only the fraction that did *not*
overflow. There is no unit in which this would be reported, because the reporting unit
is nitrogen.

**What would settle it.** Composition sampling of overflow at a handful of structures
across a range of event sizes — the same flow-proportional campaign as item 5, with FOG
and total organic carbon added to the determinands. Utilities already record fedtprop
clearing operations; those records would give the retention side.

---

## 11. Trawling and bed integrity in the receiving bays

A loose, dead bed resuspends several times more often than a living one, and bottom
trawling removes structure-forming fauna directly. Whether the bays receiving urban
discharge are also being ploughed is a separate variable that nothing here addresses.

**What would settle it.** AIS-derived fishing effort — Global Fishing Watch publishes it,
subject to an access key.

---

## 12. Whether toxicant loading, not nutrients, gates recovery

Eelgrass partially recovered through the 1940s–60s after the 1930s wasting disease, then
declined again in the 1980s. That failure-to-recover window coincides with rising
industrial and agricultural chemical loading as well as with nutrients, and only the
nutrient explanation has been seriously pursued.

The mechanism is well founded: toxicants remove the grazers and filter feeders that would
otherwise control algal biomass, so the same nutrient load produces a different outcome.
Nitrogen sensitivity as a *derived* property of a chemically damaged system.

**What would settle it.** Hard. Mesocosm work exists in the literature; the Danish-specific
question of which factor gated recovery would need historical reconstruction of both
loadings against the eelgrass record.

---

## 13. The three unplaced flood sheets

Amager, Bispebjerg and København Vest did not register confidently and hold **4.79 km²
of extracted flooding against 0.92 km² on the four that did** — so roughly five sixths of
the recovered model is sitting on disk, classified and unusable, for want of a position.
Every figure derived from the model is therefore an inner-city figure, and the Vestamager
proposal in [PROGRAMME.md](#PROGRAMME.md) sits on the island whose sheet is missing.

**A second attempt was made and failed.** It is worth recording what it established,
because it changes what the third attempt should do. `scripts/floodcheck.py` came out of
it.

- **The scale bar is right.** Measured directly off the render: 534 px for 1000 m on
  Amager, 1:14,745. The 2× error that once put Amager in the wrong place is genuinely
  fixed, and scale is not the problem.
- **A sheet is a zoom, not a catchment.** The Amager sheet covers 4.2 × 5.7 km; the
  Amager og Christianshavn cloudburst catchment is 9.2 × 9.5 km. The sheet is a portion
  of its catchment, framed for A3. This is probably why matching against catchment
  outlines failed — the two were never the same shape.
- **The sea is painted, in exact palette colour.** A sample of open water returns
  (154, 199, 224) with zero variance — the 0.2–0.5 m band. So water can be pulled
  cleanly out of the band classification already on disk instead of guessed at from
  colour heuristics, and doing so lifted the best IoU from 0.08 to 0.25.
- **A family of candidate positions is ruled out.** Every high-scoring position put
  Øresund down the sheet's full eastern edge. The sheet's bottom-right corner is
  unambiguously suburban — housing, allotments, a running track, a railway — with the
  coast entering only at the top-right. Those positions are wrong regardless of what
  they score.
- **And no scoring rule settled it.** IoU rewards agreeing water but is indifferent to
  putting open sea where the sheet shows houses. A ±1 matched filter overcorrects and
  parks the frame where there is no water at all. ZNCC behaves sensibly and peaks at
  0.43, but not at a position that survives looking at it. Precision — of the water the
  sheet paints, how much is real — reaches 1.00, and reaches it at many positions,
  because a sea blob slides along a coast.

**What would settle it.** A person who can look at the sheet and name two features.
The obstacle is not the mathematics and no longer the extraction; it is that recognising
*this beach, that stadium* and giving each a coordinate is a human act. Two points per
sheet in `viz/georef.html`, or read off any map, and `scripts/floodmaps.py georef` does
the rest and reports its own residual.

Still the smallest item on this list, and still the only one needing no new data.
