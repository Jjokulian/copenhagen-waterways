#!/usr/bin/env python3
"""Every causal route we can think of to a wrecked Danish shore, as a field.

Showing that a hypothesis rests on poor grounds reduces its political actionability.
It does not show it is wrong, and it does not tell you what is right. The scientific
move is different: put the hypothesis into a field of rivals, relate every one of
them to the same evidence, and score them.

This is step one - the field itself, written down before any of it is scored, so
that the enumeration cannot be quietly trimmed to whatever the data happened to
support. The nutrient-load hypothesis is A1. It is one of eighty-odd, and it is
stated here at full strength.

Each entry carries:
    mechanism    what physically happens
    predicts     the signature it would leave, which is what makes it testable
    discriminate the observable that separates it from its neighbours
    needs        the measurement required, at the resolution required

The "needs" field is the point. A hypothesis nobody can test is not thereby false;
it is unranked, and a ranking that silently omits its unranked members is a ranking
of what is convenient to measure.

Group I is included deliberately. Changes in who sampled, with what instrument, how
often, and under which technical instruction are rival explanations for an apparent
trend, and the raw ODA record carries the metadata to test them - DataLeverandoer,
Proevetagningsudstyr, SondeNr, TekniskAnvisninganvendt, KorrektionsFaktor - which
almost no published analysis uses.

Output: docs/HYPOTHESES.md, data/derived/hypotheses.json

Usage:  python3 scripts/hypotheses.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, write_json

OUT = os.path.join(ROOT, "docs", "HYPOTHESES.md")

# Three layers, because collapsing them is how a measurement becomes a goal.
#
# TERMINAL is what anyone actually values. Nobody values a dissolved gas
# concentration. An earlier version of this file listed oxygen deficit as an
# outcome, which reproduced the exact error the project exists to criticise:
# promoting the measured intermediate to the thing of interest, because it is the
# thing that is measured.
#
# ROUTES are the sufficient paths to a terminal outcome. Oxygen deficit is one of
# them. It is neither necessary nor sufficient on its own, and several of the
# others leave no oxygen signature at all.
#
# OBSERVABLES are what can be seen, reported or instrumented. Each belongs to a
# route, and the mapping is many-to-many.

TERMINAL = [
    ("T1", "A living seabed lost",
     "The large, slow, long-lived organisms gone, and with them the structure the "
     "rest of the community sits in."),
    ("T2", "A degraded state that maintains itself",
     "The feedback closed: the loss of vegetation, filter feeders and bioturbators "
     "each make the conditions that removed them more likely. This is the outcome "
     "that matters most and the one nothing in the monitoring is designed to detect, "
     "because it is a property of the system's dynamics rather than of any sample."),
    ("T3", "Water unfit or unpleasant to be in",
     "Greasy, foul, foaming, or unsafe. The outcome people experience directly, and "
     "the reason any of this is politically live."),
    ("T4", "Provisioning lost",
     "Fish, shellfish and the livelihoods on them."),
    ("T5", "The shore lost as a place",
     "Smell, appearance, and the ordinary use of a coastline."),
]

ROUTES = [
    ("M1", "Oxygen deficit",
     "Respiration and chemical demand exceed resupply. Well measured, heavily "
     "modelled, and the only route the requirement acts on."),
    ("M2", "Toxic exposure",
     "Something is poisoned. The dose makes the poison, so this route is acutely "
     "sensitive to peak concentration rather than to any annual mean — and annual "
     "means are what is reported. Leaves a fully oxygenated dead water."),
    ("M3", "Physical destruction and burial",
     "The habitat removed, crushed, dredged or covered. Needs no chemistry at all."),
    ("M4", "Food-web restructuring",
     "Removal or addition of a species changes what everything else does. "
     "Overfishing, invasion, disease."),
    ("M5", "Light starvation",
     "Rooted vegetation shaded out by turbidity, which then removes the thing that "
     "was holding the sediment down."),
    ("M6", "Surface film and gel",
     "The water itself becomes a different medium: greasy, foaming, mucilaginous."),
    ("M7", "Reduced chemistry at the bed",
     "Sulphide and its relatives, toxic in their own right and an oxygen sink "
     "besides. The bed becomes hostile before the water column shows anything."),
]

# Routes we can name and cannot quantify. Listing them is not a rhetorical move: an
# unquantified route that goes unlisted becomes, in every summary downstream, an
# absent one - and "no evidence of an effect" is then read as "evidence of no
# effect". These belong to M2 and have no entry in the scored field below because
# no method exists that would let them be scored fairly.
UNQUANTIFIABLE = [
    ("U1", "Mixture and cocktail effects",
     "Toxicity is assessed one substance at a time against one threshold at a time. "
     "Real exposure is simultaneous, and effects combine additively at best and "
     "synergistically often. The number of pairs alone, let alone higher orders, "
     "exceeds what could ever be tested. There is no defensible way to compute the "
     "combined effect, and equally none to argue it is zero."),
    ("U2", "Acute peaks under chronic means",
     "The dose makes the poison, and the dose that kills arrives in an event. "
     "Monitoring reports means over months; an outfall discharging for six hours "
     "after a storm is invisible in an annual average and entirely visible to "
     "whatever was living below it."),
    ("U3", "Floor and ceiling effects",
     "Where a community has already lost its sensitive members, adding stress "
     "produces no further measurable change — so the most degraded places return "
     "the smallest effect sizes, and a naive analysis reads that as evidence the "
     "stressor does not matter."),
    ("U4", "Substances on no monitoring list",
     "Tens of thousands of chemicals are in commerce; a few dozen are measured. A "
     "substance absent from the list is absent from every finding, whatever it is "
     "doing."),
    ("U5", "Sublethal and transgenerational effects",
     "Impaired reproduction, behaviour and development leave no corpse to count. "
     "The survey counts individuals present, not individuals functioning."),
]

# The outcomes. Conflating these is the original error, so they are kept apart.
OUTCOMES = [
    ("O1", "Oxygen deficit", "Dissolved oxygen below 4 or 2 mg/L, by depth, "
     "duration and extent. **An observable on route M1, not an outcome.** Nobody "
     "values a gas concentration; it earns its place only through what it causes, "
     "and it is neither necessary nor sufficient for any of T1-T5."),
    ("O2", "Fedtemøg", "Greasy organic matter in the water and on the shore. It has "
     "at least three manifestations and they are not the same measurement: **O2a** "
     "accumulation at the waterline, a transport-and-deposition outcome; **O2b** the "
     "greasy film on skin after swimming, which is a property of the water column "
     "and of the sea-surface microlayer, present without any shore deposit and "
     "reported at different times of year; **O2c** the smell, which is a chemical "
     "signature (sulphide, amines, volatile fatty acids) and the thing the public "
     "actually reports. Denmark measures none of the three."),
    ("O3", "Loss of higher benthic life", "The large, slow, long-lived animals "
     "going. Reachable by suffocation, poisoning, burial or physical destruction."),
    ("O4", "Turbidity and phytoplankton biomass", "Chlorophyll and light "
     "attenuation. Measures of quantity, standing in for claims about composition."),
    ("O5", "Foam", "Persistent foam on the water and along the strandline. A "
     "surfactant and protein phenomenon, and a different measurement from either "
     "greasiness or shore deposit."),
    ("O6", "Mass mortality events", "Fish kills, and die-offs of any other "
     "conspicuous group. Sudden, dateable, and the clearest possible evidence that "
     "*something* happened — reachable by hypoxia, toxin, pathogen or heat."),
    ("O7", "Loss of rooted vegetation", "Eelgrass and macroalgal depth limit and "
     "cover. The WFD's own biological indicator, and the one that has conspicuously "
     "failed to recover as loads fell."),
    ("O8", "Visible discolouration", "Water turned brown, red or milky. What people "
     "photograph and report, and what the chlorophyll indicator averages away."),
    ("O9", "Bathing water failure", "Closures and quality downgrades. The one "
     "outcome Denmark measures densely, over a long period, at 1,026 points."),
]

# The list above is open on purpose. These are phenomena, not a taxonomy, and the
# names people use for them overlap and shift - "fedtemøg" alone covers at least
# three distinct measurements. Adding an outcome is cheap; discovering afterwards
# that the analysis could only see the ones somebody had already named is not.

GROUPS = [
    ("A", "Nutrient-driven production in place",
     "Nutrients arrive, something grows, it dies, its decay consumes oxygen. The "
     "official hypothesis is A1; the rest of the group are its siblings and are "
     "treated no differently."),
    ("B", "Oxygen demand that arrived already made",
     "Organic matter imported ready to decay. No growth step, and for most of the "
     "group no nitrogen at any point."),
    ("C", "Physical control of resupply",
     "Oxygen deficit is a balance. Half of it is whether the water is refilled."),
    ("D", "Physical disturbance of the bed",
     "Reduced sediment brought into contact with oxygen, and the fauna removed "
     "mechanically."),
    ("E", "Chemical demand and toxicity",
     "Oxygen consumed by chemistry rather than biology, and life removed by poison "
     "rather than by suffocation."),
    ("F", "Biological structure and feedback",
     "What the community itself does to the water, and what its loss stops doing."),
    ("G", "Climate and long-term drivers",
     "Slow forcings that change the baseline every other hypothesis sits on."),
    ("H", "State, memory and regime",
     "Hypotheses in which the current year's drivers are not the explanation."),
    ("J", "Surface film, gel and the greasy water itself",
     "Fedtemøg as a property of the water rather than of the shore. These are the "
     "mechanisms that produce a greasy film on skin, and they are the ones that can "
     "operate in a sea with no Danish catchment at all."),
    ("I", "Observation and measurement",
     "Rival explanations for an apparent trend that live in the instrument rather "
     "than the sea. Omitting these is not neutrality; it is an assumption."),
]

H = [
    # ---- A ----------------------------------------------------------------
    ("A1", "A", "Danish land-based nitrogen load", ["O1", "O4", "O3", "O7"],
     "Waterborne N from Danish land reaches a coastal water, is taken up in summer "
     "when N limits growth, the biomass sinks, and its remineralisation draws down "
     "bottom oxygen.",
     "Deficit scales with current-year N load, strongest where N-limitation is long "
     "and flushing is slow. A load reduction should show within a few years.",
     "The N-load coefficient after controlling for wind work, stratification and "
     "imported COD - not the R² of a bundle containing all of them.",
     "Catchment N flux per water body per month; summer chlorophyll; oxygen by "
     "depth; N-limitation days."),
    ("A2", "A", "Phosphorus load", ["O4", "O1"],
     "P drives the spring bloom, whose sinking biomass sets the organic pool that "
     "the summer deficit draws on.",
     "Spring chlorophyll tracks P, and the summer deficit tracks spring chlorophyll "
     "better than it tracks summer N.",
     "Spring (March-May) chlorophyll against P load, and the deficit against spring "
     "rather than summer production. DCE exclude spring from the indicator.",
     "Monthly P flux; chlorophyll with the spring months kept."),
    ("A3", "A", "Atmospheric deposition on the sea surface", ["O1", "O4"],
     "Reactive N deposited directly onto the water, bypassing every catchment and "
     "every retention term.",
     "Deposition is spatially smooth and largely foreign in origin, so it should "
     "appear as a shared component across areas that share no catchment.",
     "The common factor across water bodies with unrelated catchments.",
     "Wet and dry N deposition on a marine grid, monthly. Organic N fraction "
     "specifically, which is generally not reported."),
    ("A4", "A", "Point-source discharge of nutrients", ["O1", "O4"],
     "Treatment plants and industry discharging N and P directly.",
     "Step changes at plant upgrades; a distance-decay signal from the outfall.",
     "Deficit against per-plant discharge, exploiting upgrade dates as natural "
     "experiments.",
     "Per-plant monthly discharge of N, P and COD with the upgrade dates."),
    ("A5", "A", "Advected nutrients from outside Denmark", ["O1", "O4"],
     "Baltic outflow, German, Swedish and Polish rivers, and North Sea water "
     "carrying nutrients into Danish areas.",
     "Signal enters at the boundaries and propagates inward with the circulation; "
     "correlates with Baltic inflow events, not with Danish load.",
     "Boundary nutrient concentration and transport against interior deficit.",
     "Nutrient concentration at the Belt and Sound sections; transport estimates."),
    ("A6", "A", "Submarine groundwater discharge", ["O1", "O4"],
     "Nitrate-bearing groundwater entering the sea beneath the shoreline, counted "
     "in no catchment budget.",
     "Localised, chemically distinctive (radon, radium, salinity anomalies), and "
     "decoupled from river flow.",
     "Radon-222 or radium isotope surveys along the coast.",
     "Any Danish SGD survey at all. This is a known blank."),
    ("A7", "A", "Sediment nutrient regeneration", ["O1", "O4"],
     "The bed releasing stored N and P back into the water in summer, often "
     "supplying most of what primary production consumes.",
     "Summer DIP rising above the annual mean - which DCE already use as an "
     "iltsvind indicator, i.e. they measure the mechanism and treat it as a symptom.",
     "Benthic flux chambers, or the DIP seasonality ratio against the sediment "
     "organic pool.",
     "Benthic flux measurements; sediment organic content by station and date."),
    ("A8", "A", "Marine aquaculture", ["O1", "O3"],
     "Net-pen fish farms discharging dissolved nutrients and particulate feed and "
     "faeces directly to the water column and the bed beneath.",
     "Sharp local gradient in sediment organic content and fauna within a few "
     "hundred metres; seasonal with the production cycle.",
     "Sediment and fauna transects radiating from each of the 26 licensed sites.",
     "Per-farm production and feed use by month; sediment stations near farms."),
    ("A9", "A", "Nitrogen fixation", ["O4", "O1", "O8"],
     "Cyanobacteria fixing atmospheric N, adding nitrogen the load account cannot "
     "see and which increases when N is scarce relative to P.",
     "Fixation rises as the N:P ratio falls, so reducing N load can *increase* total "
     "N supply. This is the strongest internal objection to A1.",
     "Cyanobacterial biomass and fixation rate against the ambient N:P ratio.",
     "Species-level phytoplankton counts; N-fixation rate measurements."),

    # ---- B ----------------------------------------------------------------
    ("B1", "B", "Combined sewer overflow", ["O1", "O2", "O3", "O9", "O5"],
     "Rain overwhelms a combined system and raw sewage discharges directly: "
     "organics, fat, faecal solids, at 1 g O₂ demand per g COD.",
     "Event-timed. Deficit and shore fouling follow rainfall by hours to days, not "
     "seasons, and concentrate near outfalls.",
     "Oxygen and shore condition in the days after overflow events, against "
     "per-outfall discharge volume.",
     "Per-outfall overflow volume and duration per event. Denmark has 19,665 "
     "registered outfalls and this is the single most valuable missing series."),
    ("B2", "B", "Separate stormwater", ["O1", "O2", "O9"],
     "Road and roof runoff carrying organics, hydrocarbons, tyre wear and metals "
     "through a pipe that was built to skip treatment.",
     "Event-timed like B1 but chemically distinct - hydrocarbons and 6PPD-quinone "
     "rather than faecal indicators.",
     "Faecal indicator against hydrocarbon signature in the same event.",
     "Per-outfall stormwater volume; road-runoff chemistry."),
    ("B3", "B", "Treatment plant organic load", ["O1", "O5"],
     "Continuous discharge of residual COD and BOD from 750 plants.",
     "Steady rather than event-driven; scales with population equivalent.",
     "Deficit against PE density, controlling for treatment stage.",
     "Per-plant monthly COD/BOD discharge."),
    ("B4", "B", "Riverine particulate organic carbon", ["O1"],
     "Soil, plant material and manure-derived carbon washed off land and delivered "
     "as particles that decay in the receiving water.",
     "Scales with discharge and erosion, so it co-varies with N load and is "
     "systematically misattributed to it.",
     "POC flux measured alongside N flux at the same stations. Almost never done.",
     "Suspended solids and organic carbon at stream monitoring stations."),
    ("B5", "B", "Industrial organic discharge", ["O1"],
     "Slaughterhouses, dairies, fish processing and breweries discharging "
     "high-strength organic effluent.",
     "Very high COD per unit volume; localised; tied to production schedules.",
     "Per-permit COD discharge against local deficit.",
     "Industrial discharge permits and reported loads, per site per year."),
    ("B6", "B", "Harbour and fish-processing waste", ["O2", "O1"],
     "Fish waste, bilge, and organic debris concentrated in enclosed basins with "
     "poor exchange.",
     "Extreme local deficit in harbours; a plausible direct source of shore fat.",
     "Oxygen and organic content inside harbour basins, which are rarely monitored.",
     "Harbour water quality measurements. Largely absent."),
    ("B7", "B", "Shipping discharges", ["O1", "O2"],
     "Sewage, greywater, food waste and scrubber washwater discharged legally "
     "under MARPOL along shipping lanes.",
     "Follows traffic density and lane geometry rather than any catchment; "
     "scrubber washwater is acidic and metal-bearing.",
     "Deficit and contaminant signature against AIS traffic density.",
     "AIS vessel tracks; scrubber discharge volumes. Traffic data exists; discharge "
     "volumes essentially do not."),
    ("B8", "B", "Direct manure and slurry entry", ["O1", "O2"],
     "Spills, tank failures, over-application before rain, and field drains "
     "carrying slurry to a watercourse.",
     "Extreme, brief, local. Fish kills. Under-reported by construction.",
     "Reported pollution incidents against fish-kill records.",
     "Environmental incident register with date and location."),

    # ---- C ----------------------------------------------------------------
    ("C1", "C", "Stratification strength", ["O1"],
     "A density boundary that cuts the bottom water off from the atmosphere.",
     "Deficit tracks the strength and persistence of the pycnocline, and is near "
     "zero in well-mixed water whatever the load.",
     "Potential energy anomaly from CTD profiles against deficit.",
     "CTD profiles - temperature and salinity by depth. Now obtainable from ODA."),
    ("C2", "C", "Wind work", ["O1"],
     "Mixing energy that breaks stratification and re-ventilates the bottom.",
     "Calm summers produce deficits; windy ones do not, at identical load.",
     "Cumulative wind work over the stratified season against deficit.",
     "Hourly wind. Already held: 31 years."),
    ("C3", "C", "Residence time", ["O1", "O4"],
     "How long water and its cargo stay before being flushed.",
     "The same load produces very different outcomes at different flushing times, "
     "so any load coefficient that is not normalised by residence time is wrong.",
     "Deficit against load divided by flushing time, rather than against load.",
     "Per-area residence time. Partially held; coarse."),
    ("C4", "C", "Baltic inflow events", ["O1"],
     "Dense saline pulses through the Belts that both ventilate deep basins and "
     "strengthen stratification above them.",
     "Episodic, large, and entirely exogenous to Danish policy.",
     "Deep salinity and oxygen against inflow event chronology.",
     "Belt section salinity and transport; the published inflow record."),
    ("C5", "C", "Freshwater discharge buoyancy", ["O1"],
     "River flow stratifying the surface independently of what it carries.",
     "The physical effect of discharge is confounded with the nutrients in it, and "
     "the two have never been separated.",
     "Discharge volume as a predictor separate from discharge concentration.",
     "Daily freshwater discharge per catchment."),
    ("C6", "C", "Water temperature and solubility", ["O1"],
     "Warmer water holds less oxygen and respires faster: roughly −2.3% saturation "
     "per °C, and demand rising with Q10.",
     "Deficit rises with bottom temperature even at constant organic supply.",
     "Deficit against *bottom* temperature. Not a candidate variable in the "
     "statistical models, which carry surface temperature only.",
     "Bottom temperature by station and date. In the CTD record."),
    ("C7", "C", "Bathymetry, sills and depth", ["O1"],
     "Basins below a sill cannot ventilate laterally whatever the wind does.",
     "Deficit is a function of geometry, and is where it always was.",
     "Deficit against sill depth and basin volume below the pycnocline.",
     "Bathymetry. Available."),
    ("C8", "C", "Constructed change to circulation", ["O1", "O2", "O3"],
     "Bridges, tunnels, causeways, reclamation, harbour works and wind farms "
     "altering exchange - the Øresund link, Storebælt, Lynetteholm, Nordhavn.",
     "Step changes at construction dates, localised downstream of the works. "
     "Testable as natural experiments with known dates.",
     "Before-and-after deficit at fixed stations either side of each work.",
     "Construction chronology with dates and footprints. Partially held."),
    ("C9", "C", "Sea level and tidal change", ["O1"],
     "Changed exchange volume through straits and over sills.",
     "Slow, monotone, and confounded with every other trend.",
     "Exchange volume reconstruction against deficit.",
     "Tide gauge records. Available and long."),

    # ---- D ----------------------------------------------------------------
    ("D1", "D", "Bottom trawling", ["O3", "O1", "O2", "O7"],
     "Gear dragged across the bed destroys structure and fauna directly, and "
     "resuspends reduced sediment whose sulphide consumes oxygen on contact.",
     "Fauna loss follows effort spatially with no oxygen anomaly needed; turbidity "
     "and oxygen demand spike along tracks.",
     "Fauna and sediment redox against trawling effort at fine spatial resolution.",
     "VMS/AIS-derived trawling effort rasters by month. Exists at EU level; the "
     "single most important missing layer in this whole register."),
    ("D2", "D", "Navigation dredging", ["O3", "O1"],
     "Channel maintenance removing the bed and suspending it.",
     "Localised, dated, permitted - therefore highly testable.",
     "Before-and-after at fixed stations near dredging campaigns.",
     "Dredging permits with dates, volumes and locations."),
    ("D3", "D", "Dredged-material dumping", ["O3", "O1", "O2"],
     "Sediment, and whatever is in it, deposited at 114 licensed grounds.",
     "Burial of fauna at the ground; a plume; contaminants redistributed.",
     "Fauna and sediment chemistry at and downstream of dumping grounds against "
     "dumping volume and date.",
     "Per-ground dumping volume, date and material chemistry."),
    ("D4", "D", "Sand and gravel extraction", ["O3", "O1"],
     "Removal of the bed itself at 305 licensed areas.",
     "Permanent habitat loss; persistent turbidity; altered local hydrodynamics.",
     "Fauna inside against outside extraction areas, over time.",
     "Per-area extracted volume by year. Permits are public; volumes less so."),
    ("D5", "D", "Cable and pipeline works", ["O3"],
     "Trenching across the bed for power, data and gas.",
     "Linear disturbance with known route and date.",
     "Fauna along versus away from routes, before and after.",
     "Route and installation date registers."),
    ("D6", "D", "Anchoring and propeller wash", ["O3", "O1"],
     "Shallow-water disturbance concentrated in anchorages and approaches.",
     "Follows anchorage polygons and vessel draught.",
     "Bed condition inside versus outside designated anchorages.",
     "AIS anchoring events; anchorage designations."),
    ("D7", "D", "Storm-driven resuspension", ["O1", "O2"],
     "Waves stirring the bed in shallow water, releasing reduced material and "
     "moving deposited organics shoreward.",
     "Follows wave bed shear stress, and is the mechanism most likely to *deliver* "
     "fedtemøg to a shore rather than create it.",
     "Shore fouling reports against modelled bed shear stress.",
     "Wave hindcast. Partially held: bed shear already modelled from 31 years of "
     "wind."),

    # ---- E ----------------------------------------------------------------
    ("E1", "E", "Sulphide oxidation", ["O1"],
     "Reduced sulphur from anoxic sediment consuming 2 g O₂ per g S the moment it "
     "meets oxygenated water.",
     "A large, fast oxygen sink that is entirely decoupled from current-year "
     "nutrient supply, and is triggered by disturbance.",
     "Sediment sulphide pools and porewater against oxygen demand.",
     "Sediment redox and sulphide by station. Rarely measured."),
    ("E2", "E", "Nitrification demand", ["O1"],
     "Ammonium oxidised to nitrate, consuming 4.57 g O₂ per g N with no biology "
     "of interest in between.",
     "Nitrogen exerting oxygen demand *chemically*, so an N reduction helps here "
     "for a reason unrelated to A1 - and the two are not distinguished.",
     "Ammonium concentration and nitrification rate against deficit.",
     "Ammonium by station, date and depth. In the ODA water chemistry."),
    ("E3", "E", "Iron and manganese oxidation", ["O1"],
     "Reduced metals from sediment consuming oxygen on contact.",
     "Small per gram but large in total where sediment is iron-rich.",
     "Porewater Fe(II) flux against deficit.",
     "Sediment porewater chemistry. Very rare."),
    ("E4", "E", "Methane oxidation", ["O1"],
     "Methane from anoxic sediment consuming 4 g O₂ per g on its way up.",
     "Seep-associated, localised, and invisible to nutrient accounting.",
     "Methane flux surveys.",
     "Essentially no Danish coastal methane flux record."),
    ("E5", "E", "Direct chemical oxygen demand of discharges", ["O1"],
     "Reduced chemicals discharged in industrial or municipal effluent.",
     "Consumes oxygen without any organic matter or nutrient involved.",
     "COD measured on discharges as such.",
     "Discharge COD, which is measured, and almost never carried into a marine "
     "budget."),
    ("E6", "E", "Biocides and antifoulants", ["O3"],
     "TBT historically, copper and modern boosters now, killing benthic life "
     "directly at oxygenated sites.",
     "Fauna loss concentrated near marinas, harbours and lanes with no oxygen "
     "anomaly at all. TBT imposex is a documented Danish effect.",
     "Fauna and sediment biocide concentration together at the same stations.",
     "Sediment biocide concentrations. Sediment is measured at 4 of 256 hazardous-"
     "substance points nationally."),
    ("E7", "E", "Pesticides and degradation products", ["O3", "O4"],
     "Agricultural chemicals reaching the sea and acting on non-target organisms, "
     "including the algae the indicators count.",
     "The same agricultural intensity that produces the nitrogen also produces "
     "these, so they are perfectly confounded with A1 and never separated.",
     "Marine pesticide concentrations against fauna, holding nutrient load fixed.",
     "Marine pesticide monitoring. Thin."),
    ("E8", "E", "Pharmaceuticals and personal care products", ["O3"],
     "Continuous low-dose exposure from treatment plant effluent, which is not "
     "designed to remove them.",
     "Scales with PE, not with agriculture; effects are sublethal and chronic.",
     "Effluent and receiving-water concentrations against fauna condition.",
     "Marine pharmaceutical monitoring. Almost none."),
    ("E9", "E", "PFAS and persistent novo-chemicals", ["O3"],
     "Compounds with no degradation terminus accumulating in biota and sediment.",
     "Monotone accumulation independent of any annual driver.",
     "Biota and sediment time series.",
     "Some biota data exists. Sediment barely."),
    ("E10", "E", "Heavy metals", ["O3"],
     "From harbours, industry, dumping and historic contamination.",
     "Localised, persistent, and redistributed by exactly the dredging and dumping "
     "in group D.",
     "Sediment metal concentration against fauna composition.",
     "Sediment metals. Four national points."),
    ("E11", "E", "Ammonia toxicity", ["O3", "O6"],
     "Un-ionised ammonia toxic to fauna at concentrations well below those that "
     "matter for growth, and more toxic as pH and temperature rise.",
     "Kills without hypoxia; worst in warm alkaline water near outfalls.",
     "Un-ionised ammonia calculated from ammonium, pH and temperature.",
     "Ammonium with simultaneous pH and temperature. In the ODA record."),
    ("E12", "E", "Hydrogen sulphide toxicity", ["O3", "O2", "O6"],
     "Sulphide toxic to fauna in its own right, and the source of the smell people "
     "actually report.",
     "Kills at the bed before oxygen reaches zero; produces the sensory signature "
     "that generates public complaints.",
     "Porewater and bottom-water sulphide against fauna and complaint records.",
     "Sulphide measurements. Rare."),

    # ---- F ----------------------------------------------------------------
    ("F1", "F", "Loss of filter feeders", ["O4", "O1"],
     "Mussel and oyster beds clearing the water column; their removal leaves the "
     "phytoplankton uncleared.",
     "Chlorophyll rises with no change in nutrient supply. Reversible by "
     "restoration, which makes it a testable intervention.",
     "Filter-feeder biomass against chlorophyll at fixed nutrient load.",
     "Benthic biomass surveys; shellfish stock assessments."),
    ("F2", "F", "Loss of bioturbators", ["O1", "O3"],
     "Burrowing fauna irrigate the sediment and oxygenate its upper layer; without "
     "them the bed goes anoxic sooner and stays.",
     "A positive feedback: hypoxia kills bioturbators, whose loss deepens hypoxia. "
     "Explains hysteresis without invoking anything else.",
     "Bioturbation potential index from fauna data against sediment oxygen "
     "penetration depth.",
     "Species-level fauna with abundance and biomass. In the ODA bundfauna data."),
    ("F3", "F", "Loss of eelgrass and macroalgae", ["O1", "O4", "O2", "O7"],
     "Rooted vegetation produces oxygen, stabilises sediment and competes for "
     "nutrients; its loss removes all three at once.",
     "Turbidity and resuspension rise together after vegetation loss, which then "
     "prevents recovery. DHI model this explicitly.",
     "Vegetation depth limit against turbidity, with the direction of causation "
     "tested by lag.",
     "Eelgrass depth limit and cover by station and year. In ODA vegetation."),
    ("F4", "F", "Overfishing and trophic cascade", ["O4", "O3"],
     "Removing predatory fish releases zooplanktivores, which release "
     "phytoplankton.",
     "Chlorophyll rises with no nutrient change; the signal is in the fish, and "
     "fishing effort is documented.",
     "Chlorophyll against fish stock assessments, controlling for load.",
     "ICES stock assessments; Danish landings by area and year."),
    ("F5", "F", "Invasive species", ["O4", "O3"],
     "Comb jelly, Pacific oyster, round goby and others restructuring the food web.",
     "Step changes at arrival dates, spreading spatially from an introduction point.",
     "Community composition before and after documented arrivals.",
     "Species observation records with date and position."),
    ("F6", "F", "Jellyfish blooms", ["O4", "O1"],
     "Gelatinous predators removing zooplankton and depositing rapidly-decaying "
     "biomass.",
     "Episodic; the carcass fall is a concentrated oxygen sink.",
     "Jellyfish abundance against subsequent deficit.",
     "Jellyfish monitoring. Essentially none in Denmark."),
    ("F7", "F", "Harmful algal blooms specifically", ["O3", "O1", "O6", "O8"],
     "Toxin-producing species killing fauna directly, distinct from biomass.",
     "Kills at chlorophyll levels that the indicator scores as acceptable, because "
     "the indicator counts biomass and not identity.",
     "Species-level phytoplankton composition against mortality events.",
     "Phytoplankton species counts. Collected; rarely used in the assessment."),
    ("F8", "F", "Microbial shift to fast-growing forms", ["O1", "O2"],
     "When the slow, large and long-lived are gone, what remains are the organisms "
     "that turn nutrient into biomass fastest and decay fastest.",
     "High productivity and high biomass with low diversity - which the chlorophyll "
     "indicator cannot distinguish from health, and which is what fedtemøg is.",
     "Diversity and turnover rate alongside biomass.",
     "Microbial community composition. Not monitored at all."),
    ("F9", "F", "Disease and parasite mass mortality", ["O3", "O1", "O2", "O6"],
     "A pathogen killing a dominant species, leaving a decaying mass.",
     "Sudden, species-specific, and not preceded by any oxygen anomaly.",
     "Mortality event records with species and date.",
     "Marine mortality event register. Ad hoc."),
    ("F10", "F", "Vertebrate mass mortality", ["O2", "O1", "O6"],
     "Seal, bird or fish die-offs depositing large local organic loads.",
     "Local, sudden, and a direct route to shore fouling.",
     "Stranding and die-off records.",
     "Stranding networks. Partial."),

    # ---- G ----------------------------------------------------------------
    ("G1", "G", "Warming", ["O1", "O3", "O4", "O6"],
     "Less oxygen held, faster respiration, stronger and longer stratification - "
     "three effects in the same direction.",
     "Monotone worsening independent of load, and it explains why load reduction "
     "has not produced the expected recovery.",
     "Deficit against bottom temperature, and the load coefficient estimated within "
     "temperature strata.",
     "Bottom temperature by station and date, long. In the CTD record."),
    ("G2", "G", "Changing precipitation and runoff timing", ["O1", "O4"],
     "More intense rain moves the same annual load into fewer, larger events, and "
     "drives more overflow.",
     "Event concentration rises even as annual totals fall - so a falling annual "
     "load can coexist with rising peak impact.",
     "Flux delivered in the top decile of days, as a fraction, over time.",
     "Daily discharge and concentration, not annual sums."),
    ("G3", "G", "Changing wind climatology", ["O1"],
     "Less storminess or a shift in direction reducing mixing in the critical "
     "season.",
     "Deficit worsens with no change in load or temperature.",
     "Trend in seasonal wind work over the record.",
     "Hourly wind. Held."),
    ("G4", "G", "Acidification", ["O3"],
     "Lower pH impairing calcifying fauna, and shifting the ammonia equilibrium "
     "toward the toxic form.",
     "Chronic, monotone, worst for shelled species.",
     "Carbonate chemistry against calcifier condition.",
     "Marine pH and alkalinity time series. Thin."),
    ("G5", "G", "Changing ice cover", ["O1"],
     "Less winter ice changes both winter ventilation and the spring bloom timing.",
     "Shifts in the phenology of the whole annual cycle.",
     "Ice extent against bloom timing.",
     "Ice records. Available."),
    ("G6", "G", "Sea level rise", ["O1"],
     "Changed exchange volumes and altered shallow-water dynamics.",
     "Slow and confounded, but affects the geometry every other hypothesis assumes.",
     "Exchange reconstruction.",
     "Tide gauges. Long and available."),

    # ---- H ----------------------------------------------------------------
    ("H1", "H", "Alternative stable states and hysteresis", ["O1", "O3", "O4"],
     "The system has more than one self-maintaining configuration, and having been "
     "pushed into the degraded one it stays there at load levels that would never "
     "have caused it.",
     "Recovery requires a much larger reduction than the one that caused the "
     "collapse, and the response is not a function of the current year's load at "
     "all. Consistent with the observed failure of load reduction to restore "
     "eelgrass.",
     "Whether the load-response relation differs between the declining and "
     "recovering phases - a test nobody has published.",
     "Long paired series of load and state through both directions."),
    ("H2", "H", "Sediment legacy", ["O1"],
     "The organic pool accumulated over decades sets the current deficit; this "
     "year's load is a small increment on it.",
     "Deficit correlates with cumulative past load, not current load, and lags by "
     "years to decades. DCE name this mechanism as the reason their own models "
     "drift, and then leave it out of the models.",
     "Cumulative load with a fitted decay against current load.",
     "Sediment organic content and accumulation rates; dated cores."),
    ("H3", "H", "Loss of resilience through diversity loss", ["O3"],
     "A simplified community absorbs less disturbance, so the same stress now "
     "produces a collapse it once would not have.",
     "The dose-response steepens over time at constant stressor.",
     "Whether the fitted coefficient changes across eras.",
     "Long species-level fauna series. In ODA bundfauna."),
    ("H4", "H", "Subsidy-stress", ["O4", "O3"],
     "The same nutrient is a subsidy at low dose and a stressor at high, so the "
     "response is non-monotone and a linear coefficient is the wrong shape.",
     "A hump. Fitting a straight line through three simulated points, as the "
     "official method does, cannot recover it.",
     "Non-parametric response of production and diversity to load.",
     "Load and response across a wide gradient - which the 123 areas supply."),

    # ---- J ----------------------------------------------------------------
    ("J1", "J", "Transparent exopolymer particles and marine gel", ["O2", "O1", "O3", "O5", "O8"],
     "Phytoplankton and bacteria exude sticky polysaccharide gel - TEP - especially "
     "under nutrient imbalance, when cells fix carbon they cannot balance with N or "
     "P and dump the excess as extracellular carbon. The gel aggregates into marine "
     "snow and, at scale, into mucilage.",
     "Gel production rises when the N:P ratio is skewed *in either direction*, so "
     "reducing one nutrient without the other can increase it. This is the "
     "mechanism behind Adriatic mucilage events, and it is the best available "
     "physical candidate for what fedtemøg actually is.",
     "TEP concentration against the ambient N:P ratio and bloom senescence stage - "
     "not against nutrient load.",
     "TEP measurements. Not in Danish monitoring at all; the method is standard and "
     "cheap (Alcian blue)."),
    ("J2", "J", "Sea-surface microlayer enrichment", ["O2"],
     "The top micrometres of the sea concentrate surfactants, lipids, proteins and "
     "hydrophobic pollutants by orders of magnitude over the bulk water, and "
     "convergence lines concentrate that film further.",
     "This is the layer a swimmer's skin actually passes through. It explains "
     "greasiness with no shore deposit and no unusual bulk concentration, and it is "
     "destroyed by wind - so the effect is calm-weather and episodic.",
     "Microlayer sampling (glass plate or screen) against bulk water at the same "
     "station, with wind speed.",
     "Sea-surface microlayer sampling. None in Danish monitoring."),
    ("J3", "J", "Surfactants from detergents and personal care", ["O2", "O5"],
     "Anionic and non-ionic surfactants passing through treatment plants and "
     "storm outfalls, which are surface-active by design and accumulate in the "
     "microlayer.",
     "Scales with population equivalent, not with agriculture; concentrates in the "
     "film; and directly produces a slippery feel.",
     "Surfactant concentration in the microlayer near outfalls.",
     "Marine surfactant measurements. Essentially none."),
    ("J4", "J", "Sunscreen and UV filters", ["O2", "O3"],
     "Oily and silicone-based personal care products applied directly by bathers "
     "and delivered at the exact place and season people swim.",
     "Peaks at bathing beaches in bathing season, which is precisely when and where "
     "greasiness is reported, and is invisible to every catchment model.",
     "UV filter concentrations at bathing beaches across the season, against "
     "visitor numbers.",
     "Marine UV filter monitoring. None in Denmark."),
    ("J5", "J", "Microplastic and its biofilm", ["O2", "O3"],
     "Particles that carry a biofilm and sorb hydrophobic organics, concentrating "
     "in the same surface film.",
     "Accumulates monotonically, is globally shared, and is enriched in the "
     "microlayer along with everything else hydrophobic.",
     "Microplastic counts in microlayer versus bulk water.",
     "Some Danish microplastic data. Microlayer-specific: none."),
    ("J6", "J", "Oil and hydrocarbon films", ["O2", "O3"],
     "Operational discharges, bilge, road runoff and scrubber washwater leaving "
     "thin films that spread over large areas from small volumes.",
     "Follows shipping lanes and urban outfalls; a litre spreads over hectares; "
     "detectable by satellite SAR as slicks.",
     "SAR slick detections against traffic density and outfall locations.",
     "Sentinel-1 SAR is free and covers the whole period. This one is testable now."),
    ("J7", "J", "Exudate from senescing blooms", ["O2", "O1"],
     "A bloom that is dying releases far more dissolved and colloidal organic "
     "carbon than a bloom that is growing.",
     "The greasy phase follows the collapse of a bloom, not its peak - so it is "
     "offset in time from the chlorophyll maximum the indicator measures, and can "
     "occur in a season the May-September window scores as fine.",
     "Dissolved and colloidal organic carbon against bloom phase, not bloom size.",
     "DOC with sufficient temporal resolution to resolve bloom collapse."),
    ("J8", "J", "Bacterial exopolymer from fast-growing communities", ["O2", "O1"],
     "When the large and slow are gone, what remains are r-selected bacteria that "
     "produce copious extracellular polymer.",
     "Greasiness as a *symptom of the degraded state itself* rather than of any "
     "current-year input - which would explain why it persists after loads fall.",
     "Bacterial community composition and exopolymer production against community "
     "diversity.",
     "Microbial community data. Not monitored."),

    # ---- I ----------------------------------------------------------------
    ("I1", "I", "Changing station network", ["O1", "O3", "O4"],
     "Stations added, moved and dropped over the record, so a trend can be a trend "
     "in where you looked.",
     "Apparent change concentrated at times when the network changed.",
     "Recompute every trend on the subset of stations present throughout.",
     "Station start and end dates. Now held: the ODA register carries them."),
    ("I2", "I", "Changing analytical method", ["O1", "O4"],
     "Winkler titration to optode sondes for oxygen; changing chlorophyll methods. "
     "Different instruments have different biases.",
     "Step changes at method transitions, shared across all stations using the same "
     "method regardless of geography.",
     "Result against sampling gear and sonde, which the raw record names.",
     "Prøvetagningsudstyr, SondeNr, SondeNavn per measurement. In the ODA CTD "
     "record and, as far as we can tell, used by nobody."),
    ("I3", "I", "Changing sampling frequency and season", ["O1"],
     "A deficit indicator built from the worst month is biased by how often you "
     "sampled that month. More visits find more extremes.",
     "Apparent severity scales with visit count.",
     "Indicator against sampling effort per station-season.",
     "Date of every visit per station. In the raw record."),
    ("I4", "I", "Changing indicator definition", ["O1", "O4"],
     "The indicator itself was redefined - intercalibration, EQR thresholds, "
     "seasonal windows - so a change in status can be a change in the ruler.",
     "Status shifts at definition changes with no change in any measurement.",
     "Recompute historical status under each successive definition.",
     "The definitions, with their adoption dates."),
    ("I5", "I", "Changing correction factors", ["O1"],
     "The record carries both an original and a corrected result plus the factor "
     "applied. Corrections are a modelling choice inside the raw data.",
     "Trends present in corrected but not original results.",
     "Recompute everything on OriginalResultat.",
     "OriginalResultat, KorrigeretResultat and KorrektionsFaktor. Held."),
    ("I6", "I", "Changing custodian", ["O1", "O3", "O4"],
     "The 2007 structural reform moved monitoring from the counties to the state; "
     "the raw record names the supplier and the technical instruction used.",
     "Discontinuities at 2007 shared across all stations that changed hands.",
     "Result against DataLeverandoer and TekniskAnvisninganvendt.",
     "Both fields are in the raw record. Also held."),
]


def render(rows):
    o = []
    a = o.append
    by_group = {}
    for r in rows:
        by_group.setdefault(r[1], []).append(r)

    a("# The field of hypotheses\n")
    a("Showing that a claim rests on poor grounds reduces its political "
      "actionability. It does not show the claim is wrong, and it does not tell you "
      "what is right. So this page does the other thing: it puts the official "
      "hypothesis into a field of rivals, all of them stated at full strength, so "
      "that each can be related to the same evidence and scored.\n")
    a(f"**{len(rows)} mechanisms in {len(by_group)} groups.** The nutrient-load "
      "hypothesis is **A1**. It is stated as strongly as we can state it, and it is "
      "not privileged anywhere below.\n")
    a("The register is written down *before* anything is scored, so that the field "
      "cannot be quietly trimmed to whatever the data turned out to support. Each "
      "entry names the signature it would leave and the measurement that would "
      "separate it from its neighbours. Where that measurement does not exist in "
      "Denmark, the entry says so — a hypothesis nobody can test is not thereby "
      "false, it is **unranked**, and a ranking that omits its unranked members is "
      "a ranking of what was convenient to measure.\n")

    a("## What is actually at stake\n")
    a("Nobody values a dissolved gas concentration. An earlier version of this page "
      "listed oxygen deficit as an outcome, which reproduced the exact error the "
      "project exists to criticise — promoting the measured intermediate to the "
      "thing of interest, because it is the thing that is measured. So the "
      "structure here is three layers.\n")
    a("### Terminal outcomes — what anyone actually cares about\n")
    a("| | outcome | what it is |")
    a("|---|---|---|")
    for i, n, w in TERMINAL:
        a(f"| `{i}` | **{n}** | {w} |")
    a("")
    a("### Routes — the sufficient paths to those outcomes\n")
    a("Oxygen deficit is **one** of these. It is neither necessary nor sufficient "
      "for any terminal outcome, and several of the others leave no oxygen "
      "signature at all — a poisoned water can be fully oxygenated.\n")
    a("| | route | what it is |")
    a("|---|---|---|")
    for i, n, w in ROUTES:
        a(f"| `{i}` | **{n}** | {w} |")
    a("")
    a("### Routes we can name and cannot quantify\n")
    a("Listing these is not a rhetorical move. An unquantified route that goes "
      "unlisted becomes an absent one in every summary downstream, and *no evidence "
      "of an effect* is then read as *evidence of no effect*. None of them appears "
      "in the scored field below, because no method exists that would score them "
      "fairly. That is a statement about the method, not about the sea.\n")
    a("| | | |")
    a("|---|---|---|")
    for i, n, w in UNQUANTIFIABLE:
        a(f"| `{i}` | **{n}** | {w} |")
    a("")
    a("### Observables — what can be seen, reported or instrumented\n")
    a("These are what the hypotheses below are scored against. Each belongs to one "
      "or more routes, and the mapping is many-to-many.\n")
    a("| | observable | what it is |")
    a("|---|---|---|")
    for i, name, what in OUTCOMES:
        a(f"| `{i}` | **{name}** | {what} |")
    a("")

    for gid, gname, gnote in GROUPS:
        rs = by_group.get(gid, [])
        a(f"## {gid}. {gname}\n")
        a(f"*{gnote}*\n")
        for hid, _, title, outs, mech, pred, disc, needs in rs:
            a(f"### {hid} — {title}\n")
            a(f"**Outcomes:** {', '.join(outs)}\n")
            a(f"{mech}\n")
            a(f"**Predicts.** {pred}\n")
            a(f"**Discriminated by.** {disc}\n")
            a(f"**Needs.** {needs}\n")

    a("## What comes next\n")
    a("1. Find, for every entry, a data source at **measurement resolution** — one "
      "row per observation with its time and its position — not an aggregate. "
      "Aggregates are where the discriminating information goes.\n")
    a("2. Build the area-period panel: every observable, per water body, per period, "
      "with the gaps left visible as gaps rather than interpolated away.\n")
    a("3. Express each hypothesis as a model over that panel, with a common "
      "interface so that none of them is advantaged by its formulation.\n")
    a("4. Score them out of sample — held-out years and held-out areas — and rank. "
      "Report the unrankable separately and by name.\n")
    a("A1 may well win. That would be a far stronger result for it than the one it "
      "currently has, because it would have been tested against rivals rather than "
      "fitted alone.\n")
    return "\n".join(o) + "\n"


def main():
    rows = H
    ids = [r[0] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate hypothesis id"
    payload = {
        "terminal": [{"id": i, "name": n, "what": w} for i, n, w in TERMINAL],
        "routes": [{"id": i, "name": n, "what": w} for i, n, w in ROUTES],
        "unquantifiable": [{"id": i, "name": n, "what": w}
                           for i, n, w in UNQUANTIFIABLE],
        "observables": [{"id": i, "name": n, "what": w} for i, n, w in OUTCOMES],
        "groups": [{"id": g, "name": n, "note": t} for g, n, t in GROUPS],
        "hypotheses": [{"id": h, "group": g, "title": t, "outcomes": o,
                        "mechanism": m, "predicts": p, "discriminated_by": d,
                        "needs": nd}
                       for h, g, t, o, m, p, d, nd in rows],
    }
    write_json(os.path.join(DERIVED, "hypotheses.json"), payload)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(rows))
    log(f"wrote docs/HYPOTHESES.md ({os.path.getsize(OUT):,} chars)")
    log(f"  {len(rows)} hypotheses across {len(GROUPS)} groups, "
        f"{len(OUTCOMES)} outcomes kept apart")
    from collections import Counter
    for g, n in sorted(Counter(r[1] for r in rows).items()):
        log(f"    {g}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
