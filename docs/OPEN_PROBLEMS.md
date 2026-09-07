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

## 2. Whether "ikke registreret" means measured or unmeasured

DCE reports state no oxygen depletion registered in Køge Bugt, including in 2023, the worst
iltsvind year in twenty. That is probably accurate — the bay is shallow and may never
stratify long enough to qualify — but *"we measured and found nothing"* and *"it is not in
the survey"* produce the identical line in a report.

**What would settle it.** The station list behind the iltsvind mapping. Whether there are
monitoring positions inside Køge Bugt at all.

---

## 3. The potency term

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

## 4. Event-based measurement of overflow

The reporting method is modelled annual volume × a fixed concentration, quality-controlled
against that same concentration, with no flow rate recorded. Sediment resuspension in a
basin is a *threshold* in flow, so the mass is plausibly dominated by a handful of events
the method averages away.

**What would settle it.** Flow-proportional sampling at a handful of structures across a
range of event sizes — videnniveau 5 in Miljøstyrelsen's own scheme, 30% uncertainty. It is
defined, it is the best method in their hierarchy, and almost nobody does it.

---

## 5. The unquantified nitrogen pathways

Ten of twenty enumerated pathways carry no number. Two are tractable:

- **Submarine groundwater discharge** — measurable with radon and radium tracers or seepage
  meters, standard practice elsewhere, not a term in the Danish marine budget.
- **Internal regeneration** — measurable with benthic flux chambers, and done in Danish
  waters, just never compiled into a nutrient budget. Probably the largest single supply to
  the productive layer.

Until at least these two are filled, no denominator exists and no percentage is meaningful.

---

## 6. The autumn die-off

Soft-bottom fauna is sampled 1 March to 31 May. The annual mortality is observed only in
its aftermath, once recolonisation has begun, so the depth of the kill — and therefore the
ratchet by which each year's hypoxia removes more of the structural life — is never
measured.

**What would settle it.** Autumn sampling at a subset of existing stations. The stations
exist; only the timing would change.

---

## 7. Fedtemøg as a condition

There is no systematic national monitoring of the shore condition at all — not extent, not
biomass, not duration, not odour. What exists is bathing-water sampling in the bathing
season, municipal beach management and complaints, all concentrated where and when people
are on beaches.

This makes every seasonal claim about fedtemøg circular. A November phenomenon would leave
almost no trace.

**What would settle it.** Cheap. Fixed-position coastal cameras with a monthly index, or a
structured citizen-reporting scheme running year-round rather than in summer.

---

## 8. Trawling and bed integrity in the receiving bays

A loose, dead bed resuspends several times more often than a living one, and bottom
trawling removes structure-forming fauna directly. Whether the bays receiving urban
discharge are also being ploughed is a separate variable that nothing here addresses.

**What would settle it.** AIS-derived fishing effort — Global Fishing Watch publishes it,
subject to an access key.

---

## 9. Whether toxicant loading, not nutrients, gates recovery

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

## 10. The three unplaced flood sheets

Amager, Bispebjerg and København Vest did not register confidently and carry *more*
modelled flooding than the four that did. Two hand-placed control points each in
`viz/georef.html` extends the flood-versus-plan comparison beyond the inner city.

The smallest item on this list, and the only one that needs no new data.
