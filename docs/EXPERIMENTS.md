# Experiments, not studies

Most of what this project marks untestable is untestable **with existing monitoring**. That is a different claim, and a weaker one. A national observing programme answers questions about what is happening; a manipulation with a control answers questions about what causes what, and several of the open questions here would yield to one that fits in a season and a small boat.

The distinction matters because a study and an experiment fail differently. An analysis of existing data can always be argued with — the confounders are real, the record is short, the aggregation lost the signal. An experiment with a control and a decision rule fixed in advance either falsifies the hypothesis or does not.

So every entry below states its decision rule **before** anyone runs it, including what result would count against the hypothesis this project prefers.

> **The recurring design element is the sterilised control** — the same material, autoclaved or irradiated, run alongside the live one. Identical chemistry, no organisms. It separates *the chemistry of this stuff* from *the organisms in it* in a single step, and that is exactly the distinction the sediment-sickness and inoculation hypotheses turn on. Soil science has used it for a century.

## Three kinds of work, which are not interchangeable

**Constructive and investigative — `experiment`** (12 of 23 below). You change one thing and watch what follows. It *creates* the evidence, and it is the only kind that can establish causation, because the control is what rules out the alternatives. It costs money, time, access and usually permission.

**Investigative — `measurement`** (5 of 23 below). You observe something real that nobody recorded. It creates the *record* rather than the evidence: it can establish what is happening, where and when, but not why. Cheaper than an experiment and still requires being there. Most of the gaps in this project are of this kind - not unknowable, unrecorded.

**Build the means of measurement — `instrument`** (3 of 23 below). You make the thing that takes the reading, and put it where nobody was looking. It is a measurement project with a build phase, and it differs from the others in what it can be aimed at: **a network can be pointed at the assumptions of the existing monitoring**, not only at the sea. Whether one station can stand for a water body, whether monthly sampling sees a six-hour event, what an aggregation costs - all of those are questions about the instrument, and all of them are answerable by building a denser one beside it. It is also the kind with the clearest route to actually happening here: the Danish state is unusually willing to fund digital infrastructure, and a distributed sensor network is legible to it in a way that a request for more ship time is not.

**Armchair — `analysis`** (3 of 23 below). You work on what is already written down. It can establish consistency, bound magnitudes, expose contradictions and kill hypotheses - but it cannot establish causation, and it cannot recover a fact that was never recorded. **Almost everything this project has produced is of this kind.** That is worth saying plainly: its findings are of the form *your evidence does not support what you claim*, which is a real result and a limited one.

Naming them separately matters because they are not substitutes and they are not equally strong. Only an experiment establishes causation. Only a measurement can recover something nobody wrote down. Analysis is the cheapest and the weakest, and it is what a project like this one can do from a desk — so it should be honest that most of its output is of that kind, and that the step up in force comes from going and looking.

## What it would take

| | | experiments |
|---|---|---|
| `small` | A person with a boat, a season, and a few thousand kroner. No institution required. | X1, X18, X2, X7, X19, X20, X9, X10, X12, X14, X15, X16 |
| `lab` | A university lab, standard methods, one to two seasons. | X3, X4, X6, X11, X13 |
| `programme` | Needs a funded programme or ship time, but is still a bounded experiment rather than a monitoring commitment. | X5, X23, X17 |
| `desk` | No fieldwork at all. The data already exists; the analysis has not been run. | X21, X22, X8 |

**15 of 23 need no institution.** Two need no fieldwork or none of their own. The most consequential — X8, whether the national trends are in the sea or in the instruments — is a desk exercise on data that is already downloaded.

## Small — A person with a boat, a season, and a few thousand kroner. No institution required.

### X1 — Does eelgrass fail because the sediment is sick?

`experiment`

**Bears on:** [`T4`](#HYPOTHESES.md) Marine replant failure: negative sediment feedback, [`T5`](#HYPOTHESES.md) Loss of sediment suppressiveness, [`T2`](#HYPOTHESES.md) Loss of the sulphide-detoxifying symbiosis, [`T1`](#HYPOTHESES.md) Sulphide intrusion, gated by light

Restoration plantings fail in sediment whose chemistry looks adequate. Horticulture calls this replant disease and tests it the obvious way.

**Manipulate.** Transplant eelgrass into a site where restoration has failed, in six treatments: (a) as-is; (b) inoculum from a functioning bed in a **matched** setting - same salinity, sediment and thermal regime; (c) inoculum from a functioning but **mismatched** setting; (d) the matched inoculum autoclaved; (e) lucinid clams added; (f) matched inoculum plus clams.

**Control.** Two contrasts carry it. **Live against sterilised** (b vs d) separates a chemical effect from a biological one, because the two are identical in everything except their organisms. **Matched against mismatched** (b vs c) tests local adaptation: a community that has spent a million generations adapting to one setting is at a disadvantage in another, and the residents it has to displace are not. If donor origin matters, the practical rule follows immediately. Plus untransplanted plots and a transplant into a functioning bed as the upper bound.

**Measure.** Survival and shoot density at 3, 6 and 12 months; sulphide in root and rhizome tissue; porewater sulphide.

**Decide, in advance.** Live inoculum beats sterilised → the sediment's *biology* is the missing thing, and T5 holds: sediment inoculation is a restoration tool. Both inocula beat as-is equally → it is chemistry, not biology. Clams alone work → T2, and the intervention is fauna rather than sediment. Nothing works → sediment sickness is not why restoration fails here, and attention goes back to the water column.

*This is the cheapest decisive experiment in the register and nobody has run it. Denmark has failed eelgrass restorations to site it in.

The human analogue has already worked through the same problem. Faecal transplant restores a cleared gut, but donor material engrafts unevenly, some donors work far better than others, and the current frontier is **autologous banking** - freezing a person's own community before the antibiotic and giving it back afterwards, so the restored community is already adapted to that body. The marine version of the second half is impossible retroactively and urgent prospectively, which is `X18`.*

### X18 — Bank the communities that still work, before they stop working

`measurement`

**Bears on:** [`T5`](#HYPOTHESES.md) Loss of sediment suppressiveness, [`T11`](#HYPOTHESES.md) Occupancy is the function, [`W8`](#HYPOTHESES.md) Whoever founds the community keeps it, [`T4`](#HYPOTHESES.md) Marine replant failure: negative sediment feedback, [`L1`](#HYPOTHESES.md) The reference condition never existed

Restoring a community needs a source, and the best source is the same community from a matched setting. Medicine has reached the same conclusion and acted on it: stool banks exist, and the frontier is autologous banking - freezing a person's own community *before* the antibiotic. The marine equivalent of the autologous half is impossible after the fact, and the donor half degrades a little every year as more sites fail.

**Manipulate.** Nothing is manipulated. Collect and cryopreserve sediment and rhizosphere communities from the Danish sites that still function - eelgrass beds, mussel beds, undisturbed soft bottoms - with full physical metadata: salinity, sediment grain size, thermal regime, depth, exposure.

**Control.** The metadata *is* the design. Without matched conditions recorded, a bank is a freezer full of mud whose donors cannot be paired to a recipient site, and `X1` shows that pairing is exactly what decides whether an inoculum establishes.

**Measure.** Community composition by sequencing at the time of collection, so that what was banked is documented rather than assumed, and so the archive doubles as a baseline for `T10` and `W8`.

**Decide, in advance.** There is no hypothesis to falsify here, which is why it is filed as measurement rather than experiment. What it produces is **optionality**: every later restoration attempt, and every test of whether donor origin matters, needs source material that either exists or does not. It also supplies the pre-disturbance baseline that `T10` and `W8` both say is missing by construction.

***The only item in this register that gets harder every year it is not done.** Everything else here can be run later at the same cost; this one loses material permanently as sites degrade, and the sites that would be most valuable to have banked are the ones most likely to be gone. A freezer, a coring tube, and somebody's time.*

### X2 — Is eelgrass killed by darkness, or by sulphide that darkness lets in?

`experiment`

**Bears on:** [`T1`](#HYPOTHESES.md) Sulphide intrusion, gated by light, [`K11`](#HYPOTHESES.md) Light as a depleted resource

Eelgrass keeps sulphide out by leaking oxygen from its roots, powered by photosynthesis. If the leak is the mechanism, shading kills by poisoning rather than by starving.

**Manipulate.** Shade healthy eelgrass in situ with mesh screens at four light levels spanning the assumed requirement, for one growing season.

**Control.** Unshaded plots, and open-mesh frames that shade nothing - so the frame's own hydrodynamic effect is separated from the shading.

**Measure.** Tissue sulphide, shoot mortality, growth rate, and porewater sulphide, measured on the same schedule.

**Decide, in advance.** Tissue sulphide rises *before* growth falls → the proximate cause is sulphide intrusion, the light requirement is really a sulphide-defence requirement, and the number that matters is sediment sulphide rather than Kd. Growth falls with no sulphide rise → ordinary light limitation and the existing indicator is measuring the right thing.

*Distinguishes two mechanisms that make identical predictions for the indicator and completely different predictions for what to do about it.*

### X7 — Measure the greasy layer, at all

`measurement`

**Bears on:** [`J2`](#HYPOTHESES.md) Sea-surface microlayer enrichment, [`J3`](#HYPOTHESES.md) Surfactants from detergents and personal care, [`J1`](#HYPOTHESES.md) Transparent exopolymer particles and marine gel, [`J6`](#HYPOTHESES.md) Oil and hydrocarbon films

The greasiness people report after swimming is a property of the sea-surface microlayer, which concentrates surfactants and lipids by orders of magnitude over the bulk water. Denmark has never sampled it.

**Manipulate.** Nothing. This is a measurement, not a manipulation - but it is the first one of its kind here, and it is a glass plate and a squeegee.

**Control.** Paired bulk-water samples from the same station and moment, so every result is an enrichment factor rather than a concentration. Sampled across wind speeds, because wind destroys the film.

**Measure.** Surfactants, total lipid, TEP, and hydrocarbons in microlayer and bulk; wind speed; and a note of whether the water felt greasy.

**Decide, in advance.** Enrichment factors well above one on calm days, correlating with reported greasiness → the phenomenon is real, located, and has a chemical signature that can then be traced to a source. No enrichment → look elsewhere, and group J shrinks.

*Glass-plate microlayer sampling is a 1970s technique costing almost nothing. That it has never been done here, for a phenomenon the public reports constantly, is the finding.*

### X19 — A panel that reports nothing on the days nothing happens

`measurement`

**Bears on:** [`T1`](#HYPOTHESES.md) Sulphide intrusion, gated by light, [`T3`](#HYPOTHESES.md) Wasting disease with stress-modulated virulence, [`T5`](#HYPOTHESES.md) Loss of sediment suppressiveness, [`J2`](#HYPOTHESES.md) Sea-surface microlayer enrichment, [`O7`](#HYPOTHESES.md) Loss of rooted vegetation

The outcomes anyone actually cares about - greasy water, a foul shore, a bed with nothing structural left on it - are not measured by any Danish programme. There is no instrument for fedtemøg; the glossary entry says so, and it is not an oversight so much as a category the monitoring was never built to hold. The only observers are the people who swim, walk and fish there, and their observations are currently discarded as anecdote.

**Manipulate.** Nothing is manipulated. What is built is a reporting scheme, and its whole design rests on one decision: **a fixed panel that reports on a schedule, including on the days there is nothing to report.**

**Control.** That null is the control and the entire difference between a dataset and a complaints inbox. Open reporting - tell us when it is bad - produces a map of attention, and attention follows news coverage, so the resulting series measures publicity. A panel with a denominator produces a rate. It is the same failure as the satellite matchups: the observations that exist must not be selected on the variable being measured.

**Measure.** Per visit: position and time (a photograph carries both in EXIF, and fedtemøg is visible, so the image is a record of the outcome rather than a report about it); an ordinal odour intensity on a fixed scale, as used in odour-nuisance regulation; water appearance; whether anything structural is growing; and the null when none of it applies. Plus one control question about something unrelated to the outcome, to detect when a panel's reporting effort is rising rather than the phenomenon.

**Decide, in advance.** A rate per site per fortnight that can be laid against overflow events, rainfall and the satellite fields → the outcome variable finally has a time series. Reports that track news coverage rather than weather or discharge → the panel is measuring attention and the design has failed, which is itself worth knowing before anyone builds a bigger one.

*Cheap, and the cheapest part is the phone people already carry. The expensive part is recruiting observers who will keep reporting nothing, which is the part every citizen-science scheme underestimates.*

### X20 — Ask the people with the longest baseline, about dated events

`measurement`

**Bears on:** [`T1`](#HYPOTHESES.md) Sulphide intrusion, gated by light, [`T4`](#HYPOTHESES.md) Marine replant failure: negative sediment feedback, [`W2`](#HYPOTHESES.md) Settlement cue failure, [`D1`](#HYPOTHESES.md) Bottom trawling

Commercial and recreational fishermen hold the longest continuous observation of the Danish seabed that exists - decades of hauling gear across specific ground - and none of it is recorded anywhere as observation. Landings are recorded; what the bottom looked and smelled like is not.

**Manipulate.** Nothing. Structured interview against a chart, with the questions fixed in advance and the answers timestamped and positioned.

**Control.** The known failure mode is shifting baseline syndrome: each generation's normal is the previous generation's decline, so 'how was it back then' reliably understates change and does so more the older the respondent. The mitigation is to anchor every question on a **dated specific event** - what came up in that haul, in that autumn, on that ground - rather than on a remembered general state. Where two people fished the same ground in the same years, their accounts are a replicate.

**Measure.** Position and year of specific hauls; what was on the gear; bottom type as felt through the gear; smell; and the year a ground stopped being worth fishing, which is a sharper memory than any gradual change.

**Decide, in advance.** Dated accounts that agree between independent respondents on the same ground → a reconstructed history for places with no monitoring at all, testable against trawl-track records and the iltsvind bulletins. Accounts that disagree or that smooth into a single declining narrative regardless of ground → shifting baseline is dominating and the method gives history rather than data.

*This is the one item on the page that gets harder every year for a reason unrelated to funding, and it shares that with X18: the people who fished before the change are ageing out, and the baseline goes with them.*

### X9 — Does anything happen after an overflow?

`measurement`

**Bears on:** [`B1`](#HYPOTHESES.md) Combined sewer overflow, [`B2`](#HYPOTHESES.md) Separate stormwater, [`U2`](#HYPOTHESES.md) Acute peaks under chronic means, [`O9`](#HYPOTHESES.md) Bathing water failure

Denmark has 19,665 rain-conditioned outfalls and no per-event record of what they discharge or what follows. Monthly sampling cannot see a six-hour event.

**Manipulate.** Nothing. Moor a logger.

**Control.** A second logger at a comparable site with no outfall upstream, so the rain itself is separated from the discharge.

**Measure.** Oxygen, turbidity and temperature at 10-minute resolution through a season, with grab samples for faecal indicators and COD triggered by rainfall.

**Decide, in advance.** Oxygen sags and indicator spikes in the 48 hours after overflow events → the acute route of U2 is real, monthly monitoring is structurally blind to it, and the outfall register becomes a pressure map. Nothing detectable → B1 is smaller than argued and this project should say so.

*Two loggers and a season. The single largest measurement gap in Danish coastal water is per-event overflow impact, and it is closed by hardware costing less than a laptop.*

### X10 — Put it back and see if it holds

`experiment`

**Bears on:** [`L4`](#HYPOTHESES.md) Recovery is blocked by something other than the driver, [`H1`](#HYPOTHESES.md) Alternative stable states and hysteresis, [`T4`](#HYPOTHESES.md) Marine replant failure: negative sediment feedback

A target can be unreachable because the driver is still too high, or because something else is missing. From the outside these look identical, and thirty years of unexplained non-recovery sit between them.

**Manipulate.** Transplant eelgrass, and separately add mussel biomass, into areas where the official assessment says water quality is now adequate.

**Control.** The same transplant into an area assessed as inadequate, and into one assessed as good - bracketing the gradient.

**Measure.** Survival and persistence over three years.

**Decide, in advance.** It holds where conditions are called adequate → the water is no longer the constraint, recovery is limited by propagule supply or by a missing precondition, and the policy lever has been pulled far enough. It fails → the assessment's own standard is not sufficient for the organism it is defined by, which is equally publishable and rather more awkward.

*This is the only experiment that can distinguish 'not yet' from 'never, for another reason', and it is the question the whole nitrogen argument rests on.*

### X12 — Do the filter feeders clear the water?

`experiment`

**Bears on:** [`F1`](#HYPOTHESES.md) Loss of filter feeders, [`F2`](#HYPOTHESES.md) Loss of bioturbators

Filter-feeder loss is hypothesised to raise chlorophyll with no change in nutrient supply, which would make restoration an alternative to load reduction rather than a complement.

**Manipulate.** Enclosures with mussels added at a range of densities, in water of known nutrient status.

**Control.** Empty enclosures, and enclosures with dead shell at matched surface area - controlling for the structure rather than the animal.

**Measure.** Chlorophyll, turbidity, light at the bed, and sedimentation rate.

**Decide, in advance.** Chlorophyll clears at achievable densities → the same water-quality target is reachable by restoration at some ratio of effort to load reduction, and that ratio is computable. It does not → drop the argument.

*The dead-shell control matters: mussel beds change flow as well as filtering, and the two effects have different policy implications.*

### X14 — Can one station stand for a water body?

`instrument`

**Bears on:** [`I1`](#HYPOTHESES.md) Changing station network, [`I3`](#HYPOTHESES.md) Changing sampling frequency and season, [`H1`](#HYPOTHESES.md) Alternative stable states and hysteresis, [`C1`](#HYPOTHESES.md) Stratification strength, [`M1`](#HYPOTHESES.md) Depletion of something essential

The national assessment attaches one number to each water body, and the marine programme puts a median of one station in each - so the homogeneity that the whole framework assumes cannot be tested with the data that framework produces. Bathing water suggests a water body explains about 8% of the variation inside it, but bathing water measures faecal indicators, not the variables at issue.

**Manipulate.** Twenty to fifty logging sensors - temperature, salinity, pressure, oxygen, turbidity, light - deployed across a single water body for one stratified season, at spacings from hundreds of metres to tens of kilometres.

**Control.** One of them co-located with the existing NOVANA station, which is what makes everything else comparable to the official record rather than a separate universe of numbers.

**Measure.** The variance decomposition: how much of the variation is between sensors inside this one polygon, and how does agreement decay with distance.

**Decide, in advance.** Agreement stays high across the polygon → the water body is a coherent unit and one station is defensible after all, which would be a genuine result against this project's own argument. Agreement decays over a few kilometres → the unit is not the unit, and every per-water-body number is an average over things that are not alike.

***Precision is worth less than replication here.** A sensor with 10% error at forty points tells you more about whether a polygon is homogeneous than one perfect instrument does, because the question is about variance and not about level. That inverts the usual objection to cheap sensors, and it is the reason this is affordable.*

### X15 — What does the aggregation cost?

`instrument`

**Bears on:** [`I3`](#HYPOTHESES.md) Changing sampling frequency and season, [`I4`](#HYPOTHESES.md) Changing indicator definition, [`U2`](#HYPOTHESES.md) Acute peaks under chronic means, [`M1`](#HYPOTHESES.md) Depletion of something essential

The oxygen indicator is the share of time oxygen sits below a threshold in the worst month, computed from six years of data, yielding one value per water body per six years. Nobody has measured what that collapse discards, because doing so needs a continuous record to compare against.

**Manipulate.** Nothing in the water. Log one station continuously for two years at ten-minute resolution, then recompute the official indicator from the full record and again from monthly samples drawn out of it.

**Control.** The comparison is the control: identical water, identical sensor, two sampling regimes. Repeat the monthly draw a thousand times with different start dates to get the spread rather than one number.

**Measure.** The indicator under continuous sampling, and the distribution of its value under monthly sampling of the same water.

**Decide, in advance.** The monthly estimate is unbiased and tight → the aggregation is defensible and this line of criticism should be dropped. It is biased, or its spread spans the regulatory threshold → **the classification of a water body depends on which days somebody happened to sail**, and that is quantifiable to a probability rather than merely arguable.

*One sensor and two years. It is the cheapest way to put a number on the central claim of this whole project, and it works against us as easily as for us.*

### X16 — Do the cheap instruments agree with the expensive ones?

`instrument`

**Bears on:** [`I2`](#HYPOTHESES.md) Changing analytical method, [`I5`](#HYPOTHESES.md) Changing correction factors, [`I6`](#HYPOTHESES.md) Changing custodian

Any distributed network is worthless if its readings cannot be tied to the national record, and cheap sensors drift and foul. This is the calibration that makes X14 and X15 admissible rather than interesting.

**Manipulate.** Cheap loggers moored alongside a NOVANA station and beside the ship on every sampling visit, for a full year including a summer.

**Control.** The reference method itself - Winkler titration for oxygen, and the station's own sonde - measured at the same moment, which gives two independent comparisons rather than one.

**Measure.** Offset and drift over time, fouling rate, and how long a sensor stays inside a stated tolerance before servicing.

**Decide, in advance.** Drift is characterisable and correctable → the network's numbers can enter the same analyses as NOVANA's. It is not → the network still answers questions about *variance* and *timing*, which do not need absolute accuracy, and it should be scoped to those.

***Biofouling is the binding constraint on marine deployment, not cost.** Everything else is solved; a sensor left in Danish water grows a community within weeks. Wipers, copper guards and UV all work and all add cost and power, and the honest version of this proposal budgets for servicing rather than pretending a buoy is unattended infrastructure.*

## Lab — A university lab, standard methods, one to two seasons.

### X3 — Does fat lower measured nitrogen?

`experiment`

**Bears on:** [`R1`](#HYPOTHESES.md) The C:N threshold, and fat as a nitrogen sink, [`B1`](#HYPOTHESES.md) Combined sewer overflow

Fat has no nitrogen, so bacteria decomposing it must take nitrogen from the water. If so, a fat-loaded water reads as *less* eutrophic on the regulated indicator while being more degraded.

**Manipulate.** Mesocosms of natural seawater dosed with equal chemical oxygen demand as (a) fat, (b) carbohydrate, (c) algal biomass, (d) protein - four materials, same oxygen demand, C:N from infinite to about 5.

**Control.** Undosed seawater, and a dose of nitrate alone at the nitrogen content of the algal treatment.

**Measure.** Dissolved inorganic nitrogen, oxygen, and bacterial biomass, daily for three weeks.

**Decide, in advance.** DIN falls in the fat treatment → R1 holds, and the nitrogen indicator has a bias whose sign is opposite to what is assumed. DIN flat or rising → the immobilisation threshold does not operate here and the concern is void.

*A three-week bench experiment that would tell you whether one of the country's two regulated indicators can move the wrong way.*

### X4 — Does a small organic input unlock a large old one?

`experiment`

**Bears on:** [`R2`](#HYPOTHESES.md) Priming of the old sediment pool by fresh carbon, [`H2`](#HYPOTHESES.md) Sediment legacy

Priming: labile carbon gives microbes the energy to attack the recalcitrant pool, so an input's oxygen demand can exceed its own COD.

**Manipulate.** Intact sediment cores dosed with a small, precisely known quantity of labile carbon.

**Control.** Undosed cores, and cores dosed with an equal quantity of carbon that is already recalcitrant. Isotopically labelled dose if affordable, which lets you attribute the CO₂ to old or new carbon directly.

**Measure.** Cumulative oxygen consumption against the dose's own theoretical demand.

**Decide, in advance.** Consumption exceeds the dose's COD → priming is real here, the sediment legacy is not an inert stock, and every load figure understates its own effect. Consumption matches the dose → no priming, and the additive accounting is sound.

*Standard soil-science method applied to marine sediment. The equipment is a core tube and an oxygen optode.*

### X6 — Is silicon the limiting nutrient, and does adding it bring diatoms back?

`experiment`

**Bears on:** [`K1`](#HYPOTHESES.md) Silicon depletion and the diatom-to-flagellate shift, [`K2`](#HYPOTHESES.md) Stoichiometric imbalance decides who grows, [`J1`](#HYPOTHESES.md) Transparent exopolymer particles and marine gel

Si comes only from weathering, so N and P have risen and Si has not. If Si limits, the community shifts away from diatoms toward the flagellates and gel-formers.

**Manipulate.** Standard nutrient-addition bioassay on natural water: control, +N, +N+P, +N+P+Si, +Si alone.

**Control.** The control, and a dark bottle to separate growth from settling.

**Measure.** Diatom versus flagellate share, chlorophyll, and transparent exopolymer particles by Alcian blue.

**Decide, in advance.** +Si shifts the community toward diatoms → Si limitation is operative, and reducing N helps for a reason that has nothing to do with oxygen. TEP falls when Si is added → the gel of group J is a symptom of Si limitation, which connects fedtemøg to nutrient ratios rather than to nutrient amounts.

*A bottle experiment with a century of methodological pedigree. Silicate is already in the ODA record, so the observational half is free.*

### X11 — Does skewing the nutrient ratio make the gel?

`experiment`

**Bears on:** [`J1`](#HYPOTHESES.md) Transparent exopolymer particles and marine gel, [`K2`](#HYPOTHESES.md) Stoichiometric imbalance decides who grows, [`A9`](#HYPOTHESES.md) Nitrogen fixation

Gel and exopolymer are hypothesised to come from carbon overflow when cells fix carbon they cannot balance with N or P.

**Manipulate.** Chemostat or mesocosm cultures of natural assemblages at a matrix of N:P and Si:N ratios, at constant total nutrient supply.

**Control.** Constant-ratio cultures at matched total supply - so the effect of the ratio is separated from the effect of the amount.

**Measure.** TEP by Alcian blue, dissolved and colloidal organic carbon, community composition.

**Decide, in advance.** TEP peaks at skewed ratios rather than at high totals → the gel is a ratio phenomenon, and a policy that moves one nutrient alone can increase it. TEP tracks total supply → it is an enrichment phenomenon after all, and reducing load reduces it.

*Directly tests whether the intervention could make one outcome worse while improving another.*

### X13 — Does the muck build up because nothing is eating it?

`experiment`

**Bears on:** [`E13`](#HYPOTHESES.md) Biocides that remove the decomposers themselves, [`E14`](#HYPOTHESES.md) Veterinary antiparasitics in manure, [`E15`](#HYPOTHESES.md) Total biocide load, whatever its source, [`R3`](#HYPOTHESES.md) The decay relay stalls when a stage is removed, [`R11`](#HYPOTHESES.md) Marine fungi, the decomposers nobody counts

Turfgrass thatch - a greasy organic mat - forms when pesticides kill the earthworms and microbes that would incorporate the material. If fedtemøg is the same failure in sediment, then organic matter accumulates because the decomposers are gone, not because more is arriving.

**Manipulate.** Litter bags of standardised organic material buried in sediment mesocosms dosed with an environmentally realistic fungicide concentration, and with a veterinary avermectin, at several doses.

**Control.** Undosed sediment, and autoclaved sediment as the zero-biology floor. **The organic supply is identical in every treatment** - which is the whole point, because it makes the nutrient hypothesis unable to explain any difference that appears.

**Measure.** Mass loss from the litter bags over months; fungal and bacterial biomass; oxygen consumption; and whether a visible mat forms.

**Decide, in advance.** Decay slows with dose while supply is held constant → the accumulation route is biocidal rather than nutritional, `E13` holds, and fedtemøg has a cause that no nitrogen policy touches. Decay is unaffected → the marine decomposers are not sensitive at realistic concentrations, and the thatch analogy fails where it matters, which is worth publishing too.

*The cleanest discriminator in the register: two hypotheses that predict the same observed outcome are separated by holding the input fixed and varying only the processors. Standard litter-bag method, standard mesocosms, and the dose figures come from published sales and residue data.*

## Programme — Needs a funded programme or ship time, but is still a bounded experiment rather than a monitoring commitment.

### X5 — How long does a trawl track take to heal, and what does it release?

`experiment`

**Bears on:** [`D1`](#HYPOTHESES.md) Bottom trawling, [`D8`](#HYPOTHESES.md) Loss of biostabilisation, and the mobile bed, [`D11`](#HYPOTHESES.md) Stabilisers against destabilisers, [`E1`](#HYPOTHESES.md) Sulphide oxidation

Trawling is hypothesised to destroy the biostabilising surface skin and release sulphide. Both are measurable, and the disturbance can be applied on purpose.

**Manipulate.** One experimental trawl pass across an untrawled patch, with everything measured before, immediately after, and at intervals for two years.

**Control.** Adjacent untrawled patches, and a patch crossed by the vessel without gear deployed - which controls for the vessel rather than the trawl.

**Measure.** Critical erosion threshold, surface-sediment chlorophyll, porewater and water-column sulphide, oxygen demand, and macrofauna.

**Decide, in advance.** A sulphide and oxygen-demand pulse after the pass → trawling is an oxygen sink as well as a physical one, and belongs in the oxygen budget. Erosion threshold falls and recovers slowly → D8, and the recovery time constant is the number that decides whether current effort is sustainable.

*Requires a cooperative vessel and a closed area. Yields the one number - recovery time - that the whole trawling argument turns on.*

### X23 — Does the faecal load reach the water, or is it spent in the soil?

`experiment`

**Bears on:** [`E13`](#HYPOTHESES.md) Biocides that remove the decomposers themselves, [`E14`](#HYPOTHESES.md) Veterinary antiparasitics in manure, [`E15`](#HYPOTHESES.md) Total biocide load, whatever its source, [`A2`](#HYPOTHESES.md) Phosphorus load, [`G2`](#HYPOTHESES.md) Changing precipitation and runoff timing, [`O1`](#HYPOTHESES.md) Oxygen deficit

The load account carries nitrogen and phosphorus. Everything else that is spread — organic carbon, copper and zinc from feed, antiparasitics, antibiotics, resistance genes, pathogens — is unpriced, and its fate is genuinely unknown rather than known to be small. A field is a reactor: labile carbon is respired there, so the default assumption is that little arrives. But rain onto freshly spread ground, frozen or saturated soil, tile drains and macropores are documented bypasses, and **Denmark's own monitoring cannot see any of it**, because it samples on a calendar rather than on events and measures a determinand list that does not include the payload.

**Manipulate.** Nothing is manipulated: the spreading window is the manipulation, it happens every spring, and it is applied to the whole country at once. What is added is **event-based sampling** — flow-triggered automatic samplers on paired stream catchments, taking a series through the rising limb and the falling limb of each storm from February to April, and again in an autumn window when no spreading is permitted.

**Control.** Three controls, and the design needs all of them. **Time:** the same streams outside the spreading window. **Space:** catchments matched on soil, drainage and area but contrasting in livestock density, which is where the national register earns its place. **And source:** faecal sterols and host-specific microbial markers separate pig manure from human sewage and from soil organic matter, which is what turns a concentration into an attribution.

**Measure.** Per event: COD and BOD, particulate organic carbon, ammonium, total N and P, copper and zinc, coprostanol with a pig-specific marker, one antiparasitic residue, and discharge at the same minute so the result is a load and not a concentration.

**Decide, in advance.** **Markers and copper rise sharply in the days after spreading and scale with livestock density → the payload bypasses the soil**, the second channel is real and measurable, and the determinand list of the national programme is missing a term rather than merely being coarse. **Markers stay at baseline through the window → the soil reactor holds**, what reaches the sea from a field is essentially nitrate, and the nitrogen framing is right about *what arrives* even where this project disputes how much. **That second outcome is the one worth pre-committing to publish**, because it argues against the suspicion that motivated the design.

*The dense version of this - a node on every stream that reaches the sea, and the fingerprint panel behind it - is constructed and costed in [SENSING.md](#SENSING.md). This is the cheapest unbought answer in the whole document. The instruments are ordinary autosamplers and a lab list, the timing is fixed by a calendar everyone already knows, and the comparison catchments exist. It is also the one design here whose *negative* result would materially strengthen the official account — which is a reason to run it, not a reason to avoid it. **Grab sampling cannot substitute:** this project's own sources report that transport computed from grab samples was underestimated in all three streams of the 2018 GUDP study, and an event is exactly what a fortnightly visit misses.*

### X17 — Take the fungicides away, region by region, without ruining anyone

`experiment`

**Bears on:** [`E13`](#HYPOTHESES.md) Biocides that remove the decomposers themselves, [`E14`](#HYPOTHESES.md) Veterinary antiparasitics in manure, [`E15`](#HYPOTHESES.md) Total biocide load, whatever its source, [`E16`](#HYPOTHESES.md) Conserved targets: "selective" is a claim about dose, [`E17`](#HYPOTHESES.md) The microbiome is the exposed organ, [`R3`](#HYPOTHESES.md) The decay relay stalls when a stage is removed, [`R11`](#HYPOTHESES.md) Marine fungi, the decomposers nobody counts, [`T12`](#HYPOTHESES.md) Defence is outsourced, because the host cannot win the race

The register cannot say what agricultural biocides do to marine decomposers, because the counterfactual does not exist: every Danish catchment has been sprayed for decades. A ban would create one and would also be economic suicide for the people asked to absorb it, so it will not happen and should not.

**Manipulate.** Substitute rather than prohibit. Replace chemical control with biological control — the occupancy route — catchment by catchment on a **staggered schedule with the order randomised**, until every participating area has crossed over.

**Control.** A stepped wedge is its own control twice over. Each catchment is compared against its own record before crossover, and against the catchments that have not yet crossed. **Nobody is withheld from the treatment** — they receive it later — which is what makes it politically and ethically possible where a control group would not be.

**Measure.** In the sea: decomposition rate of standard material, sediment fungal biomass, benthic fauna, sediment organic content. On land, and with equal weight: yield, input cost, disease incidence and farm margin.

**Decide, in advance.** Marine decomposition recovers where crossover has happened and not where it has not → the biocide route of `E13` is real at landscape scale, and the substitution is the remedy. Nothing changes in the sea → the marine biocide hypothesis fails its largest test and this project should say so loudly. **And the agronomic outcome is a result in its own right, whichever way it falls** — if yields drop, that is the number the argument has to carry, not a detail to be discovered later by the people who farm.

*This is the only design here that is simultaneously an intervention, a national experiment, and survivable for the people inside it. It also supplies what nothing else can: **a real counterfactual for the chemical argument**, at the scale the argument is made. Denmark already has the administrative machinery — pesticide taxation, action plans, and protection zones around wellfields where spraying is restricted — so the instrument exists and only the randomisation and the marine measurement would be new. The general form of that observation is the meta-solution in [PLACES.md](#PLACES.md): a country that does one thing everywhere has spent the contrast that would have told it whether the thing worked, and the staggered order here is how you buy it back without withholding anything from anyone.*

## Desk — No fieldwork at all. The data already exists; the analysis has not been run.

### X21 — Reconstruct the catchments from the endpoints, nationally

`analysis`

**Bears on:** [`B1`](#HYPOTHESES.md) Combined sewer overflow, [`B2`](#HYPOTHESES.md) Separate stormwater, [`B3`](#HYPOTHESES.md) Treatment plant organic load, [`A4`](#HYPOTHESES.md) Point-source discharge of nutrients

Denmark has 20,402 outfalls with a position, an annual volume and a reported reduced impervious area, and no published map of which ground drains to which. The pipe geometry exists in a national register that is not open, so the network cannot be looked up. It may be inferable.

**Manipulate.** Nothing physical. Delineate catchments from the terrain model, then **constrain the delineation so each outfall's computed impervious area matches the reduced area already published for it**. Building footprints and construction years come from BBR, so impervious cover can be reconstructed for any year rather than only for today.

**Control.** The 20,402 reported areas are the control, and they were produced independently of any terrain analysis. A delineation that reproduces them is doing something right; one that cannot is falsified without fieldwork. Hold out a random tenth to fit nothing and check against those.

**Measure.** Terrain, building footprints with year built, and the outfall register - all open, all already fetched or fetchable. Plus, where a municipal wastewater plan publishes real catchment boundaries, those become a second and much harder test.

**Decide, in advance.** Catchments reproducing the published areas within a stated error → per-outfall connected area for the whole country, which is what B1 and B2 need and neither has. Systematic failure in some region or sewer type → that is informative too, because it localises where terrain stops predicting the network. Failure everywhere → the inference does not work and the register stays the only route.

*It produces a plausible network, not the real one, and every use must say so. But 97 of 98 municipalities currently have no catchment map at all, and a plausible one with a stated error beats nothing. Copenhagen's exists only because seven PDFs happened to be recoverable, which is archaeology rather than method.*

### X22 — Find the baskets, instead of accepting the ones that were drawn

`analysis`

**Bears on:** [`L5`](#HYPOTHESES.md) The reference sites are not references, [`I4`](#HYPOTHESES.md) Changing indicator definition, [`A1`](#HYPOTHESES.md) Danish land-based nitrogen load, [`Z8`](#HYPOTHESES.md) The attenuation budget is never partitioned

The Copenhagen map does not aggregate into administrative units. Its units are functional - a catchment is the ground that drains to one point, a flow path is where water actually goes - so the boundaries are consequences of the terrain rather than decisions about it. The marine map has no equivalent: it inherits 123 water bodies drawn for administration, and every statistic computed in them inherits that drawing. The question nobody asks is whether those lines are where the sea changes.

**Manipulate.** Nothing physical. The satellite record supplies a field with no station bias at all - daily 1 km ocean colour since 1997, every pixel measured the same way on the same day - so the partition can be derived from the water rather than imposed on it.

**Control.** **The null already exists and was measured**: similarity of log Kd490 against separation, pooled over 144 days, giving r = 0.97 at 1 km, 0.74 at 12 km, 0.50 at 31 km. Two points 12 km apart should agree at 0.74 wherever they are. So take pairs at a fixed separation that straddle an official boundary and pairs at the same separation that do not. A boundary that is real shows *less* agreement across it than the curve predicts; one that agrees more than the curve predicts is splitting water that behaves as one thing.

**Measure.** The gridded record already fetched, and the 123 polygons. Then the harder half: cluster the field on its own temporal correlation structure and compare the discovered partition to the official one - not to score it, but to produce a map of where the two disagree.

**Decide, in advance.** Boundaries that pass → the units are doing real work and aggregation inside them is defensible, which would be a genuine finding *for* the current framework. Boundaries that fail → named, located, and quantified in correlation units rather than argued about. A discovered partition that cuts across the official one → the strongest possible version of the argument, because it says not merely that the baskets are wrong but where the right ones are.

*Two limits stated in advance. The satellite sees the surface, and its retrieval fails hardest in exactly the fjords where the boundaries are densest, so the test is strongest in open water and weakest where it would matter most. And a partition discovered from one variable is a partition for that variable: the baskets for light need not be the baskets for oxygen, and finding that they differ would itself dispose of the idea that one set of lines can serve every purpose.*

### X8 — Are the trends in the sea or in the instruments?

`analysis`

**Bears on:** [`I1`](#HYPOTHESES.md) Changing station network, [`I2`](#HYPOTHESES.md) Changing analytical method, [`I3`](#HYPOTHESES.md) Changing sampling frequency and season, [`I5`](#HYPOTHESES.md) Changing correction factors, [`I6`](#HYPOTHESES.md) Changing custodian, [`L3`](#HYPOTHESES.md) The trend depends on the start year

The raw record carries the supplier, the sampling gear, the sonde, the technical instruction, and both the original and corrected result with the factor applied. No published analysis uses them.

**Manipulate.** Nothing. Recompute every national trend four ways: on all stations versus only stations present throughout; on OriginalResultat versus KorrigeretResultat; within versus across gear and sonde types; and split at the 2007 transfer from the counties to the state.

**Control.** The comparison is the control. Each pair differs in exactly one methodological choice.

**Measure.** The size and sign of every reported trend under each recomputation.

**Decide, in advance.** A trend that survives all four → it is in the sea. A trend that changes sign or vanishes under any one → it is in the instrument, and it has been reported as a fact about Denmark. Either result is worth having, and the second would be worth a great deal.

***No fieldwork and no permission required.** The data is downloaded. This is the highest ratio of consequence to cost in the register.*

## Why this list is short

It is short on purpose. Every entry had to clear three tests: a control that isolates one mechanism, a decision rule written before the result, and an outcome that would change what someone does. A great many interesting measurements fail the third test, and a great many proposals fail the first.

It is also worth saying what these experiments cannot do. None of them settles the national attribution question, because that is a question about a whole country over decades and no manipulation reaches it. What they settle is whether the *mechanisms* the attribution assumes actually operate — which is the part currently taken on trust in every direction, this project's included.

