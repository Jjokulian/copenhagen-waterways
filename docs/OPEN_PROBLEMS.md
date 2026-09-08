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

## 13. The flood sheets — solved by matching the photographs to each other

**All seven placed, and now mutually consistent to 23 m.**

The sheets are tiles of one aerial survey, so where two overlap the pixels depict the same
ground. That makes registration an image-to-image problem rather than a landmark hunt —
and image-to-image is the thing that works. `scripts/floodalign.py` resamples an
overlapping pair onto a common metric grid, discards everything that was *drawn* rather
than photographed, reduces both to gradient magnitude, locally normalises, and runs a
masked normalised cross-correlation by FFT over every offset.

Three details did the work, and each was suggested by someone looking at the problem
rather than by the code:

- **Match structure, not tone.** Gradient magnitude survives a change of season, exposure
  or print. It lifted a typical pair's peak-to-rival ratio from 12.7 to 16.0 while
  returning the identical shift.
- **Exclude everything drawn.** The depth palette, the black *Oplandsgrænser* outline and
  the legend are each sheet's *own* annotation, so leaving them in correlates one sheet's
  notes against another's. Masking them by exact palette colour, by saturation, and by
  near-black and near-white took the best pair's NCC from 0.43 to 0.64. Discarding
  photograph is cheap; admitting overlay is not.
- **Then exclude everything flat.** Auditing what survived the colour masking found
  regions of perfect uniformity still in it — 7.1% of indre-by's remaining area, almost
  all of it dark harbour water. Some are overlay fills that missed the palette test and
  some are genuinely photographed but featureless: open water, a flat roof, a bare field.
  The distinction does not matter, because neither carries positional information and
  both inflate the correlation's denominator. A local-range test catches both without
  needing to know which is which.
- **Solve all seven at once.** Sheet-by-sheet placement cannot notice that the frame
  itself is loose. A global bundle adjustment — every overlapping pair as one equation,
  the resident control points as the absolute anchors — produced **11 usable pairs, pair
  residuals of 23 m RMS and 41 m worst.**

### What it revealed about the earlier work

The four automatically registered sheets were **not** mutually consistent: pairwise they
disagreed by 100–190 m. Their advertised "13–28 m" was *agreement between detectors*,
never accuracy, and detectors agreeing on a wrong answer is a thing that happens. Every
one of them moved: østerbro by 195 m east and 135 m south, indre-by by 123 and 217,
ladegårdsåen by 25 and 182.

The control points held up. Amager moved 0.2σ in easting and 1.8σ in northing; København
Vest 1.0σ and 1.7σ. Bispebjerg's moved furthest — and Bispebjerg is precisely the sheet
whose two points sat at almost the same height, so its northing was never constrained.
The adjustment corrected the axis that was known to be weak, which is the behaviour that
makes it believable.

**And it converges.** Re-running the alignment after applying the solution returns
residual shifts of −1 to +1 m on every sheet, against the 100–360 m corrections it
originally applied. A registration that did not converge would keep asking to move.

**An independent check, not used in the fitting.** Some of the painted depth lands on
open water, which is an error — water standing on water. Before the adjustment that was
1.56 km²; after, **1.21 km²**, a 22% reduction. Nothing about the bundle optimised for
it; it uses the city's own water polygons, which the alignment never saw.

### What it changed

| | Before all seven | After the adjustment |
|---|---:|---:|
| Flood path on land | 1.52 km² | **5.93 km²** |
| Within 200 m of a planned work | 90.5% | **85.8%** |
| Within 100 m | 82.6% | **67.4%** |
| With a surface route within 100 m | 72% | **53.5%** |
| Corridor candidates | 4 | **33** |

### What remains

**Nørrebro is the one sheet the adjustment could not touch.** Every pairing with it came
out flat — peak-to-rival ratios of 1.02 to 1.06 — so it has no usable pair, and it has no
control points either. It keeps its original automatic position and is now the only sheet
not known to be consistent with the rest. Why it refuses to correlate is unresolved; it
is the smallest sheet and the most heavily painted of the inner four, but neither fully
explains it.

Two control points on Nørrebro would settle it, or the orthophoto route below would settle
everything at once.

### The route that would have avoided all of this

These are aerial photographs, so the right reference is another aerial photograph with
known georeferencing. SDFI / Dataforsyningen publishes GeoDanmark Ortofoto as WMS and
WMTS under an open licence, **including historical spring imagery for 2004–2011**, the era
of these sheets. The machinery in `floodalign.py` would work unchanged against it and
would place all seven absolutely rather than relatively, to a few metres, with no human
and no anchors. It needs a free API key.

The earlier attempt to match the OSM road network is kept here as a negative result: peak
0.051 against a nearest rival of 0.046, a ratio of 1.12. A dense uniform mesh carries
almost no positional information, because at any offset some streets line up with some
streets. What carries position is whatever is rare and irregular — which is why the
sheets with coastline registered themselves and the inland ones did not.

---

## 14. The flood model predates a substantial part of the city it is used to plan

The 2012 sheets model a 2010 scenario on 2010 imagery. Copenhagen has since built
Nordhavn, most of Ørestad, Sluseholmen and Teglholmen in Sydhavn, and a good deal of
Refshaleøen and the Amager waterfront — much of it on reclaimed or re-levelled ground,
all of it impervious, none of it in the model.

**Quantified against today's sewer catchments:** 37 of 766 catchments, holding **344 ha
of impervious surface (8.1% of the city's total)**, fall outside every one of the seven
sheet footprints. The largest sit at Nordhavn, Refshaleøen, Ørestad Syd and the
south-western edge.

And the composition gives it away. Across the city, catchments of the type
*Separatkloakeret, tag- og vejvand til recipient* are 14.4% of impervious area. Among the
catchments the model never covered they are **65.3% — a 4.5× enrichment.** New districts
are built separately sewered. So the ground outside the model is disproportionately the
ground built after it.

**Why it matters in both directions.** Those districts add impervious surface, so runoff
that the model never routed; and they sit on made ground at engineered levels, so the
terrain the model used is wrong there even where it has coverage. Every figure in
[FLOOD_GAP.md](#FLOOD_GAP.md) is therefore a statement about the 2010 city. The plan
built on it is being delivered into a 2026 one.

**What would settle it.** A re-run of the hydraulic model on current terrain and current
impervious cover — which the city presumably could do in an afternoon and has not
published. Failing that, the 344 ha can at least be flagged rather than silently omitted.

### The time dimension, which is the more interesting version

Everything here is a snapshot compared against another snapshot: a 2010 model against a
2018 plan, read in 2026. The materials for a fourth dimension are partly present and
unused — `skp_veje_tunneller_kk` carries `forventet_ibrugtagning`, an expected
in-service year running from 2014 to 2038; `lar_registreringer` carries permit and
in-use status per installation; the sewer layer carries *status* and *plan* side by side.

What is missing is the historical spine: when each basin, outfall, tunnel and reclamation
actually entered service over the last thirty years. With that, the same maps become a
sequence — and the questions worth asking are sequence questions. Did the shoreline's
condition change when a given basin came online? Does overflow frequency track
construction, or rainfall, or neither?

---

## 15. The transport experiments that were already run, and nobody read

[CURRENTS.md](#CURRENTS.md) could not establish whether material from the Copenhagen side
reaches Køge Bugt. The best it managed was a statistical lag — during overflow-scale rain
the Sound runs *north*, and twelve hours later it runs south, on 145 event-hours of a
four-year record. That is suggestive and thin.

It is also unnecessary, because the experiment has been run several times with a known
quantity of sediment released at a known place on known dates.

| | Øresund fixed link | Lynetteholm |
|---|---|---|
| When | 1995–2000 | 2021–22 |
| Material | dredged seabed, Drogden and Saltholm | harbour gytje |
| Volume | **7.4 million m³ dredged** | 2 million m³ planned to be dumped |
| Released to the water | spill limit **5%, up to 370,000 m³** | **498 m³** before it was stopped |
| Where | the northern entrance to Køge Bugt | Køge Bugt, by permit |
| Outcome | limit reported met, *nulløsning* judged met | dumping dropped entirely; material built into the peninsula instead |
| Attention | project's own monitoring programme | national controversy, Swedish objection under the Espoo Convention |

**The asymmetry is the finding.** The permitted spill from the Øresund link — up to
370,000 m³ of fines put into the water column at the mouth of Køge Bugt over five years —
is on the order of **seven hundred times** what was actually dumped at Lynetteholm before
the dumping was stopped. The recent, smaller project was halted after a political fight.
The older, far larger one was a permit condition that was met.

This is not an argument that the Øresund link was mishandled; its spill was measured
against a limit and reported within it, which is more than most of the discharges in this
project can say. It is an argument about **what gets looked at**. A release becomes
controversial when it is called dumping and invisible when it is called spill.

**What would settle it.** Sediment cores from Køge Bugt, dated. Fine material released at
the Drogden end between 1995 and 2000, and again from harbour works since, should appear
as datable horizons if the transport is real — and should be absent if it is not. That is
a direct test of the convergence claim in item 1, using events that have already
happened, and it needs a boat and a lab rather than a model.

Provenance for both events is in `data/manual/monitoring.json` under
`sediment_release_events`.
