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


# The categorical layer, above the routes.
#
# Enumerating mechanisms one at a time has no stopping rule - the register went
# from 71 to 127 in an afternoon and would go further. Enumerating the *kinds* of
# way a living thing can fail is a smaller problem, and it gives a procedure: for
# each avenue, each requirement, and each functional group, ask whether an instance
# is in the register. Gaps then show up by construction rather than by luck.
#
# An organism is a system that maintains itself against entropy using flows. It can
# fail because a flow it needs stops, because something arrives that harms it,
# because the field it sits in leaves its tolerable range, because it is physically
# destroyed, because something eats or infects it, because a partner it depends on
# goes, because it fails to replace itself, or because the change outruns its
# capacity to adjust. We do not claim that list is closed either - but it is a far
# better level at which to attempt closure than the level of instances.
# Each avenue has two axes, and they close differently. "modes" is whether the
# ways of failing along that axis can be enumerated; "entities" is whether the
# things it can happen to can be. An avenue is only as closed as its weaker axis.
AVENUES = [
    ("V1", "Deficiency",
     "A required input falls below what is needed. Energy, an element, light, an "
     "edible particle, a vitamin, a service performed by something else.",
     "M1", "K, R1, A (as its inverse)", "closed", "OPEN"),
    ("V2", "Excess and toxicity",
     "An input exceeds what can be tolerated - including too much of a required "
     "thing. Shelford's ceiling, not Liebig's floor.",
     "M2", "E, K8, A (nutrients as stressor)", "closed", "OPEN"),
    ("V3", "Condition outside the envelope",
     "A physicochemical field - temperature, salinity, pH, redox, pressure, "
     "hydrodynamic energy - moves outside the range the organism tolerates. "
     "Distinct from V2 because it is a state, not a substance arriving.",
     "M1, M7", "C, G, K10", "closed", "nearly closed"),
    ("V4", "Mechanical destruction and burial",
     "Structure removed, crushed, smothered, abraded or mobilised. No chemistry "
     "required at any point.",
     "M3", "D", "closed", "closed"),
    ("V5", "Biotic attack",
     "Predation, grazing, disease, parasitism, competition, invasion. Something "
     "else does the killing.",
     "M4", "F, T3, T8, F11", "closed", "bounded, badly catalogued"),
    ("V6", "Loss of a partner or a performed function",
     "The organisms whose activity the focal organism depends on are gone - "
     "symbionts, facilitators, and the ones that were conditioning the environment "
     "for everyone.",
     "M4, M7", "T2, T5, T6, F1, F2, F3", "nearly closed", "bounded, badly catalogued"),
    ("V7", "Failure to replace itself",
     "The population dies without any individual being killed: no propagules, no "
     "connectivity, no settlement cue, wrong timing, too little genetic variation. "
     "**The register was almost empty here until the avenues were written down.**",
     "—", "W (added because this avenue was empty)", "closed", "nearly closed"),
    ("V8", "Rate exceeded",
     "The change is survivable in magnitude but not in speed. Adaptation, "
     "acclimation, migration and recovery all have rates, and a disturbance "
     "returning faster than recovery completes is a different thing from the same "
     "disturbance once.",
     "—", "W, H1", "closed", "inherits the others"),
]

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
    ("M1", "Depletion of something essential",
     "Anything life requires falls below what some part of the community needs. "
     "Oxygen is the famous instance and the only one the requirement acts on, but "
     "it is an instance: silicon, light at the bed, carbonate ion, cobalamin, "
     "thiamine, available iron and edible particles of the right size all belong "
     "here, and group K works through them. **A depletion is selective, not "
     "general** - it removes whoever needed the missing thing and releases whoever "
     "did not."),
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
    ("K", "Depletion and imbalance of what life requires",
     "The policy frame is that there is too much of something. The plant-nutrition "
     "literature is about there being too little, and about ratios. Liebig's law of "
     "the minimum says growth is set by the scarcest essential resource, not by the "
     "sum; Shelford's law of tolerance says every requirement has a ceiling as well "
     "as a floor; and horticultural antagonism says an excess of one nutrient "
     "*induces deficiency* of another by blocking its uptake. Under those three, "
     "\"too much nitrogen\" and \"depleted of something else\" are not opposite "
     "diagnoses. They are the same one."),
    ("Z", "The physical fields and their windows",
     "Light starvation is the same argument as chemical deficiency, one physical "
     "layer up - and the layer behaves differently in a way that matters. A "
     "chemical has one axis: how much. A field has several, and each carries its "
     "own floor and ceiling. Light is not only how much, but of what wavelengths, "
     "for how long, and when. So the exhaustive treatment of the physical avenue is "
     "a small cross-product - the fields are enumerable, their dimensions are "
     "enumerable, and each dimension admits exactly the same three failure modes as "
     "a chemical does. This is the most nearly closable part of the whole register, "
     "and among the least examined."),
    ("T", "Sediment sickness: symbionts, pathogens and why nothing grows back",
     "Horticulture has a name for ground where a plant will not grow although the "
     "nutrients are adequate: replant disease, or soil sickness. Its causes are "
     "biological - accumulated specialist pathogens, autotoxic exudates, and the "
     "loss of the symbionts and the suppressive microbial community that made the "
     "plant resilient. The sea has the same thing, it has been documented largely by "
     "Danish researchers, and it does not appear in the assessment because the "
     "assessment measures the medium's chemistry and not its biology."),
    ("S", "The land side: the medium, not the input",
     "Retention - the fraction of applied nutrient that never reaches the sea - is "
     "the largest single number in the whole account, and GEUS state it *\"kan i "
     "praksis ikke måles direkte\"*. It is a property of soil and hydrogeology, and "
     "soil properties vary over metres. The tropical-soil literature is the "
     "cautionary case: phosphate fixation by iron and aluminium oxides in Ferralsols "
     "and Andosols is the *same reaction* as the marine sediment phosphate trap, and "
     "seventy years of work on it has produced a vocabulary - sorption capacity, "
     "saturation, occlusion, hysteresis - that marine assessment does not use."),
    ("R", "Decay, and the community that does it",
     "Decomposition ecology has spent a century on the question this project is "
     "asking: what happens when organic matter arrives faster than it can be "
     "processed, and what breaks when the processors go. Almost none of it appears "
     "in marine nutrient policy, which treats decay as a rate constant. It is a "
     "relay of organisms, and relays stall. The soil and horticultural literature is "
     "the better guide here, and the one difference that does not transfer - the "
     "sulphate reservoir - turns out to explain why marine anoxia is a different and "
     "worse thing than freshwater anoxia."),
    ("L", "The baseline and the counterfactual",
     "Not rival causes of degradation, but rival accounts of whether the degradation "
     "and its remedy are correctly specified at all. The reference condition is a "
     "*modelled* state, and the target is derived from it, so an error there moves "
     "every requirement in the country without touching a single measurement. This "
     "is the failure mode that took African desertification research thirty years to "
     "find: Fairhead and Leach's forest patches in Guinea, read by colonial and "
     "successor science as relics of a destroyed forest, had been created by the "
     "villagers. The causal arrow was backwards, and the error was in the assumed "
     "original state."),
    ("I", "Observation and measurement",
     "Rival explanations for an apparent trend that live in the instrument rather "
     "than the sea. Omitting these is not neutrality; it is an assumption."),
]


# Each route has its own cascade, and they converge. This is the structural fact
# that makes attribution hard, and it is why the terminal state carries almost no
# information about which route produced it.
CASCADES = [
    ("M1", "Depletion of something essential (oxygen shown)",
     "demand exceeds resupply → the organisms that needed it die → the functions "
     "they performed stop → conditions worsen for whoever is left → in the oxygen "
     "case: burrowing and irrigation stop, the sediment goes anoxic, sulphide and "
     "phosphate are released, production rises, demand rises",
     "closes on itself through whatever the lost organisms were doing - for oxygen, "
     "through the sediment they were ventilating"),
    ("M2", "Toxic exposure",
     "sensitive species die first → grazers and filter feeders are lost "
     "disproportionately, being larger and longer-lived → nothing crops the fast "
     "growers → biomass turns over faster → more material to decay",
     "closes through the loss of control from above"),
    ("M3", "Physical destruction",
     "structure removed → the biostabilising surface skin is broken → sediment "
     "mobilises → abrasion and burial kill the neighbours → nothing settles on a "
     "moving bed → the skin is not rebuilt",
     "closes through substrate mobility, the same way a desert holds itself open "
     "once its crust is broken"),
    ("M4", "Food-web restructuring",
     "a predator or grazer is removed → its prey is released → the level below that "
     "is suppressed → primary producers are uncontrolled",
     "closes through trophic release"),
    ("M5", "Light starvation",
     "light at the bed falls below the plant's requirement → rooted vegetation dies "
     "→ sediment is no longer held → resuspension rises → light falls further",
     "closes through the sediment the plants were holding"),
    ("M6", "Surface film and gel",
     "nutrient imbalance drives carbon overflow → gel and exopolymer are produced → "
     "aggregates form, resist grazing, and sink → smothering and decay → more "
     "imbalance",
     "closes by being inedible"),
    ("M7", "Reduced chemistry at the bed",
     "sulphide accumulates → fauna die at the sediment surface → irrigation stops → "
     "the oxidised surface layer thins → sulphide reaches the water",
     "closes through the loss of the animals that kept the bed oxidised"),
]


# Every element life requires, put through the same two questions we ask about
# oxygen: can it be depleted here, and is there a loop that makes the depletion
# feed itself? Oxygen is famous for having one. It is not alone, and it is not even
# the best documented.
#
# "loop" is the self-reinforcing mechanism, where one exists. "evidence" is how well
# established that loop is in the literature, not how likely it is to matter here.
ELEMENTS = [
    ("C", "Carbon", "CO₂ and bicarbonate; the vast DIC pool",
     "Rarely limiting in bulk, but drawn down inside a dense bloom, where pH can "
     "rise above 9.",
     "High pH shifts ammonium toward un-ionised ammonia, which is acutely toxic. A "
     "bloom therefore poisons the water by consuming carbon — a kill with no "
     "hypoxia in it at all.",
     "established"),
    ("O", "Oxygen", "dissolved gas, resupplied from air and photosynthesis",
     "Yes, and it is the one the requirement acts on.",
     "The known one: deficit kills fauna, fauna stop irrigating the bed, the bed "
     "goes anoxic, phosphate and sulphide are released, production rises, demand "
     "rises.",
     "established"),
    ("N", "Nitrogen", "nitrate, ammonium, organic N",
     "Yes — drawn to near zero in summer surface water, which is what N-limitation "
     "means.",
     "**Two loops, in opposite directions.** Hypoxia stops nitrification, which "
     "starves denitrification of nitrate, so the sediment stops permanently "
     "removing N and starts releasing ammonium instead: the bed flips from an N "
     "sink to an N source. And as N falls relative to P, cyanobacterial fixation "
     "rises and puts N back — so reducing the load can increase the internal supply "
     "while selecting for the least desirable producers.",
     "established"),
    ("P", "Phosphorus", "phosphate, largely bound to iron oxides in oxic sediment",
     "Yes, and famously reversible.",
     "The best-documented loop in the whole system, better than the oxygen–fauna "
     "one: anoxia reduces Fe(III) to Fe(II), the iron-bound phosphate dissolves, "
     "production rises, oxygen falls, more phosphate is released. Denmark's own "
     "assessment cites this to explain why the Skive and Lovns phosphorus models "
     "fail.",
     "established"),
    ("S", "Sulphur", "sulphate, ~2.7 g/L — effectively unlimited",
     "Never depleted. Its abundance is the problem.",
     "Once oxygen and nitrate are gone, sulphate becomes the terminal electron "
     "acceptor, and there is so much of it that sulphide production is unbounded. "
     "Sulphide kills fauna, fauna stop irrigating, the oxidised surface layer thins, "
     "more sulphide reaches the water. This is why marine hypoxia is worse than "
     "freshwater hypoxia: the ocean carries its own poison reservoir.",
     "established"),
    ("Si", "Silicon", "dissolved silicate, supplied only by rock weathering",
     "Yes — and uniquely, human activity does not replace it.",
     "Enhanced production buries silica faster in diatom frustules; the Si:N ratio "
     "falls; diatoms give way to flagellates and cyanobacteria, which need no Si, "
     "are poorly grazed, and produce the gel. Less grazing means more sinking "
     "organic matter, which means more of the hypoxia that started it.",
     "established"),
    ("Fe", "Iron", "required for photosynthesis and nitrate reduction; also the "
     "sediment's phosphate trap",
     "Coastal water is iron-rich in total, but the *sediment's* iron pool is "
     "depletable and its bioavailability depends on redox and organic ligands.",
     "The iron shuttle: repeated anoxia reduces and mobilises sediment iron, which "
     "is exported or buried elsewhere. The bed permanently loses its capacity to "
     "bind phosphate, so each hypoxic episode leaves the system more prone to the "
     "next. A ratchet rather than a cycle — this one does not reverse when oxygen "
     "returns.",
     "established"),
    ("Mn", "Manganese", "enzyme cofactor; redox-cycling like iron",
     "Cycles between oxidation states with the redox front rather than depleting.",
     "Shares the iron shuttle, and its oxides also consume oxygen on reoxidation.",
     "established"),
    ("Mo", "Molybdenum", "cofactor for nitrate reductase and for nitrogenase",
     "Yes, in sulphidic water specifically.",
     "Sulphide converts molybdate to thiomolybdate, which is scavenged and buried. "
     "A euxinic basin therefore strips itself of the cofactor that both nitrogen "
     "fixation and nitrate reduction require — hypoxia disabling two of the "
     "nitrogen cycle's own valves.",
     "established"),
    ("Co", "Cobalt", "the metal at the centre of vitamin B12",
     "Scarce, and its availability is mediated by the bacteria that make B12.",
     "Most eukaryotic algae cannot make B12 and depend on bacteria for it. A shift "
     "in the bacterial community changes which algae can grow at all, with no "
     "change in any nutrient anyone measures.",
     "established"),
    ("Ca", "Calcium", "abundant as an ion; the limiting quantity is carbonate "
     "saturation, not calcium",
     "Calcium never depletes. Carbonate ion does, as acidification proceeds.",
     "Shell dissolution currently buffers pH — a stabilising feedback that is being "
     "spent. When the shells are gone the buffer goes with them.",
     "established"),
    ("Cu", "Copper", "essential cofactor, and a deliberate biocide",
     "Not depleted; the risk is the ceiling, not the floor.",
     "Antifouling copper puts an essential micronutrient into its toxic range on "
     "purpose, in exactly the harbours and lanes where exchange is worst.",
     "established"),
    ("Zn", "Zinc", "cofactor for carbonic anhydrase, needed for carbon uptake",
     "Can limit in some marine settings; some diatoms substitute cadmium for it.",
     "Zinc limitation impairs carbon acquisition, which interacts with the carbon "
     "drawdown loop above. Weakly studied in coastal water.",
     "partly"),
    ("Se", "Selenium", "glutathione peroxidase; protective against mercury",
     "Deficiency documented in other systems; the essential-to-toxic window is "
     "among the narrowest of any element.",
     "Interacts with mercury burden, so neither is interpretable alone.",
     "partly"),
    ("B1", "Thiamine", "vitamin, not an element, but a hard requirement",
     "Yes. Baltic salmon M74 syndrome is mass fry mortality from thiamine "
     "deficiency, documented since the 1970s.",
     "Deficiency is transmitted through the diet, so it follows the same community "
     "shift as silicon depletion, at a life stage no survey counts.",
     "established"),
    ("K", "Potassium", "~400 mg/L in seawater",
     "No. Never limiting.",
     "None.",
     "n/a"),
    ("Mg", "Magnesium", "~1.3 g/L in seawater",
     "No.",
     "None.",
     "n/a"),
    ("Cl", "Chlorine", "the dominant anion in seawater",
     "No.",
     "None.",
     "n/a"),
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

    ("D8", "D", "Loss of biostabilisation, and the mobile bed", ["O3", "O4", "O7"],
     "Benthic diatoms and cyanobacteria secrete extracellular polymer that glues the "
     "sediment surface, raising the critical erosion threshold by a measured factor "
     "of two to five. It is the marine homologue of desert biocrust - the fragile "
     "living skin that holds an *erg* still - and it is destroyed by the same thing: "
     "surface disturbance.",
     "**A seabed can become a desert without being poisoned or suffocated.** Once "
     "the skin is broken the bed mobilises, abrasion and burial kill the neighbours, "
     "and the damage propagates laterally - the crust-and-vehicle-track story "
     "exactly. The state then holds itself, because mobility prevents recolonisation "
     "and recolonisation is what would restabilise it.",
     "Critical erosion threshold and microphytobenthic biomass against disturbance "
     "history, rather than against nutrients.",
     "Sediment erodibility measurement (cohesive strength meter or flume) with "
     "matched chlorophyll in the surface sediment. Standard methods; not in Danish "
     "monitoring."),
    ("D9", "D", "Fertility islands lost to homogenisation", ["O3", "O7"],
     "Desert vegetation traps sand and concentrates nutrients into mounds with "
     "barren interspace - a two-phase mosaic where almost all the biological "
     "activity is in a small fraction of the area. Mussel beds, tube-worm fields and "
     "eelgrass do the same on a seabed.",
     "Removing the structure does not average the system; it collapses it to the "
     "barren phase, which is a lower-productivity *stable* state rather than an "
     "intermediate one. A survey reporting means across an area cannot see the "
     "difference between a mosaic and its barren half.",
     "Spatial variance of fauna and organic matter, not their mean. A mosaic and a "
     "homogenised flat can share a mean and differ completely in variance.",
     "Fauna sampled with enough spatial replication to estimate variance within an "
     "area. Present design gives one grab per station."),
    ("D10", "D", "Winnowing and armouring", ["O3", "O1"],
     "Currents remove fine sediment and its organic matter, leaving a coarse lag - "
     "the marine desert pavement. The bed that remains has different chemistry, "
     "different permeability and different fauna.",
     "Sediment composition shifts permanently with no change in supply, and the "
     "organic matter removed is deposited somewhere else, concentrating demand "
     "elsewhere.",
     "Grain size distribution through time at fixed stations.",
     "Sediment grain size by station and date. Collected historically; rarely "
     "analysed as a time series."),
    ("D11", "D", "Stabilisers against destabilisers", ["O3", "O4"],
     "Burrowing fauna destabilise sediment; microphytobenthos and tube-builders "
     "stabilise it. Which side dominates decides whether the bed is erodible at all, "
     "and the two respond differently to every stressor in this register.",
     "Erodibility is a biological property with a sign that can flip. Neither side "
     "of the balance appears in nutrient assessment, so a bed can change from "
     "stable to mobile with no measured change in anything.",
     "The ratio of bioturbating to biostabilising biomass against measured "
     "erodibility.",
     "Species-level fauna with functional traits assigned. The fauna data exists in "
     "ODA; the trait assignment is a desk exercise."),

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
    ("F4", "F", "Trophic cascade from a removal far away", ["O4", "O3", "O1"],
     "Removing one level releases the next and suppresses the one below that. The "
     "Baltic case is documented: cod were fished down through the 1980s and 90s, "
     "sprat were released, their grazing suppressed the large copepods, and the "
     "system moved into a state that has not reverted. Cod and sprat now appear to "
     "hold each other in alternative stable configurations.",
     "**The cause is displaced from the effect in trophic distance and in time.** A "
     "fishery removes a predator; two levels down and fifteen years later the "
     "plankton community is different, and nothing in the water chemistry ever "
     "changed. Any search for causes confined to water quality cannot find this, "
     "and a load coefficient fitted through such a period absorbs it.",
     "Chlorophyll and zooplankton composition against stock assessments, with lags "
     "of years, holding nutrient load fixed.",
     "ICES stock assessments and Danish landings by area and year - both open, and "
     "already in the fetch queue."),
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

    ("F11", "F", "Viral lysis and the viral shunt", ["O1", "O2", "O4"],
     "Marine viruses run to about ten million particles per millilitre and lyse a "
     "large share of the bacterial and algal standing stock every day. Lysis does "
     "not pass carbon up the food chain - it returns it to dissolved and colloidal "
     "organic matter, to be respired by bacteria again. That short-circuit is the "
     "viral shunt.",
     "Carbon is retained in the microbial loop instead of reaching anything larger, "
     "so the same primary production supports less higher life and leaves more "
     "dissolved organic matter behind - which is the substrate for the gel of group "
     "J and for the oxygen demand of `M1`. A shunted system looks productive and "
     "feeds nothing.",
     "Viral abundance and lysis rate against the share of production reaching "
     "mesozooplankton - the ratio, not either alone.",
     "Marine viral counts. Standard method since the 1990s; not in Danish "
     "monitoring at any station."),
    ("F12", "F", "The micropathogens nobody catalogues", ["O3", "O6", "O7"],
     "Viruses, bacteria, protists, fungi and oomycetes cause mass mortality in "
     "marine organisms routinely - eelgrass wasting, sea star wasting, oyster "
     "herpesvirus, crustacean and bivalve pathogens. The set of possible attackers "
     "is bounded by the biota, but the catalogue is worst exactly at the small end.",
     "A mortality event with no chemical or oxygen signature and no obvious "
     "predator. Attribution defaults to whatever *was* measured, which is a "
     "guarantee that pathogens are under-attributed rather than evidence they are "
     "unimportant.",
     "Pathogen screening of mortality events at the time they occur, which requires "
     "someone to be looking within days.",
     "A marine mortality event response capability. Denmark has none for "
     "invertebrates."),

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

    # ---- K ----------------------------------------------------------------
    ("K1", "K", "Silicon depletion and the diatom-to-flagellate shift",
     ["O4", "O2", "O8", "O1"],
     "Diatoms build frustules of silica and cannot grow without dissolved silicon. "
     "Si comes from rock weathering, so human activity does not raise it, while N "
     "and P have risen severalfold. When Si runs out first, diatoms are replaced by "
     "flagellates and cyanobacteria - poorly grazed, prone to harmful blooms, and "
     "the principal producers of the gel in group J. Enhanced production also buries "
     "Si faster, so the depletion reinforces itself.",
     "Total biomass need not change at all; the *composition* does. This is a "
     "mechanism where reducing nitrogen genuinely helps, for a reason that has "
     "nothing to do with oxygen and that the chlorophyll indicator cannot see, "
     "because it counts biomass and the change is in who the biomass is.",
     "The Si:N ratio through time against diatom share of the community. Both are "
     "measurable and the ratio is almost never reported.",
     "Dissolved silicate alongside N and P at the same stations and dates, and "
     "species-level phytoplankton counts. Silicate is in the ODA record."),
    ("K2", "K", "Stoichiometric imbalance decides who grows", ["O4", "O2", "O8"],
     "Redfield C:N:P at 106:16:1 and roughly Si:N at 1:1 for diatoms are "
     "requirements, not averages. Skewing the ratios changes which organisms can "
     "complete their life cycle, independently of how much of anything there is.",
     "Community composition tracks ratios; total biomass tracks absolute supply. A "
     "policy that moves one nutrient alone necessarily moves every ratio it appears "
     "in, and the direction of that effect is not signed in advance.",
     "Community composition against N:P and Si:N, with absolute concentrations held "
     "fixed - which the 123 areas make possible.",
     "Simultaneous N, P and Si with species-level counts."),
    ("K3", "K", "Macronutrient excess inducing micronutrient deficiency",
     ["O4", "O3", "O6"],
     "Standard horticultural antagonism: high nitrogen suppresses uptake of copper "
     "and boron, high phosphorus induces zinc deficiency, high potassium blocks "
     "magnesium and calcium. The excess starves the organism of something else.",
     "Damage that looks like deficiency arising from enrichment, so the same load "
     "reduction helps for a mechanism nobody named. Routine in glasshouse practice "
     "and, as far as we can find, entirely absent from Danish marine assessment.",
     "Tissue micronutrient content in marine primary producers along a nutrient "
     "gradient - the standard horticultural diagnostic, applied to the sea.",
     "Tissue elemental analysis of algae and eelgrass. Not collected."),
    ("K4", "K", "Thiamine (B1) deficiency", ["O6", "O3"],
     "Thiamine deficiency causes mass mortality of fry and adults; Baltic salmon M74 "
     "syndrome is documented from the 1970s onward, and similar deficiency has been "
     "implicated in bird and fish die-offs across the region.",
     "Kills at a life stage nobody surveys, with no poison and no hypoxia. Linked to "
     "diet composition, so it is downstream of the same community shift as K1.",
     "Thiamine status in fish eggs and prey species against community composition.",
     "Thiamine assays. Swedish and Finnish work exists; Danish marine monitoring has "
     "none."),
    ("K5", "K", "Cobalamin (B12) and cobalt limitation", ["O4", "O8"],
     "Most eukaryotic algae are B12 auxotrophs and depend on bacteria to supply it. "
     "The vitamin, and the cobalt at its centre, is a limiting resource produced by "
     "one part of the community for another.",
     "Change the bacterial community and you change what algae can grow, with no "
     "change in any nutrient that is measured.",
     "B12 concentration and auxotroph share against bacterial community "
     "composition.",
     "Marine B12 measurements. None in Denmark."),
    ("K6", "K", "Iron bioavailability", ["O4"],
     "Iron is required for photosynthesis and nitrate reduction. Coastal water is "
     "usually iron-replete in total, but availability depends on redox state and on "
     "organic ligands, both of which change with hypoxia and with organic loading.",
     "Availability, not total concentration, is the limiting quantity - so a "
     "measurement of total iron can be flat while the available fraction moves.",
     "Dissolved and ligand-bound iron speciation, not total iron.",
     "Iron speciation. Not monitored."),
    ("K7", "K", "Carbonate ion depletion", ["O3", "O6"],
     "Acidification is usually framed as pH falling. For a calcifying organism the "
     "operative quantity is the depletion of carbonate ion and the fall in aragonite "
     "and calcite saturation - a resource being removed, not a toxin arriving.",
     "Shell-forming larvae fail first, in the season when saturation is lowest, "
     "which need not be the season anything is measured.",
     "Aragonite saturation state against larval recruitment of calcifiers.",
     "Carbonate system measurements - two of pH, alkalinity, DIC or pCO₂ together. "
     "Thin in Danish coastal water."),
    ("K8", "K", "The narrow window between deficient and toxic", ["O3", "O4"],
     "Copper, zinc, manganese, nickel, selenium and boron are all essential and all "
     "toxic, often within an order of magnitude. Shelford's law of tolerance, in the "
     "elements.",
     "Both tails kill, so a linear dose-response is the wrong shape and a threshold "
     "set on one side says nothing about the other. Antifouling copper puts a "
     "micronutrient into the toxic tail on purpose.",
     "Response across the full gradient rather than against a single threshold.",
     "Trace element concentrations with matched biological response. Sediment metals "
     "are measured at four points nationally."),
    ("K9", "K", "Selenium", ["O3", "O6"],
     "Required for the glutathione peroxidase system, protective against mercury, "
     "and toxic in modest excess. Deficiency has been implicated in fish and bird "
     "mortality elsewhere.",
     "Interacts with mercury burden, so neither element's effect is interpretable "
     "without the other.",
     "Selenium and mercury together in biota, as a ratio.",
     "Selenium in Danish marine biota. Not routinely measured."),
    ("K10", "K", "Salinity change and osmotic cost", ["O3", "O4", "O6"],
     "The Danish straits are a salinity gradient, and every organism in them sits "
     "near an edge of its tolerance. Changing freshwater delivery or Baltic inflow "
     "moves the whole community's position in that range.",
     "Species drop out at boundaries that have nothing to do with nutrients, and the "
     "Baltic's low-diversity brackish fauna is already at a minimum where small "
     "shifts have large effects.",
     "Community composition against salinity variance, not mean.",
     "Salinity by station, date and depth. In the CTD record."),
    ("K11", "K", "Light as a depleted resource", ["O7", "O4"],
     "Distinct from turbidity as a symptom: for a rooted plant, light at the bed is "
     "a resource with a hard requirement - roughly 11-14% of surface irradiance for "
     "eelgrass - and below it the plant does not grow slowly, it dies.",
     "A threshold, not a gradient. Explains why vegetation recovery is abrupt and "
     "why intermediate improvement produces no response at all.",
     "Light at the bed against the requirement, per area, rather than Kd as an "
     "index.",
     "Kd with water depth, which together give light at the bed. Both are in the "
     "record and the product is rarely formed."),
    ("K12", "K", "Loss of habitat-forming structure", ["O3", "T1"],
     "Mussel beds, eelgrass, stone reefs and biogenic structure are a resource in "
     "themselves - surface, refuge, and hydrodynamic shelter. Denmark's stone reefs "
     "were physically removed for construction stone through the twentieth century.",
     "Species requiring hard substrate cannot return whatever the water quality "
     "does, because the substrate is gone. Testable: reef restoration is a dated, "
     "located intervention.",
     "Fauna at restored reefs against unrestored controls.",
     "Stone extraction records and reef restoration locations and dates."),
    ("K13", "K", "Food depletion for filter feeders and larvae", ["O3", "O4"],
     "Filter feeders and larvae need the right particles in the right size range at "
     "the right time. A shift from diatoms to picoplankton or gel can leave high "
     "chlorophyll and nothing edible.",
     "Starvation amid apparent abundance. The chlorophyll indicator would score this "
     "water as over-productive.",
     "Larval condition and growth against particle size spectrum, not chlorophyll.",
     "Particle size spectra and larval condition indices. Not monitored."),
    ("K14", "K", "Genetic and functional diversity depletion", ["O3"],
     "Repeated mortality events select the survivors down to a narrow set, and a "
     "narrow set has fewer ways to respond to the next disturbance.",
     "Declining resilience with no change in any concentration - the same stressor "
     "produces a larger effect than it once did.",
     "Functional diversity indices through time from the fauna record.",
     "Species-level fauna with abundance, which the ODA bundfauna data carries."),

    # ---- T ----------------------------------------------------------------
    ("T1", "T", "Sulphide intrusion, gated by light", ["O7", "O3"],
     "Eelgrass detoxifies sediment sulphide by leaking oxygen from its roots into "
     "the rhizosphere - radial oxygen loss, the same mechanism wetland plants use. "
     "That leak is powered by photosynthesis. Under low light it weakens, sulphide "
     "enters the roots and rhizome, and the plant is poisoned from below.",
     "**A light-and-sulphide interaction that is neither a nutrient effect nor a "
     "water-column oxygen effect.** Both indicators can read acceptably while the "
     "plant dies, because the lethal condition is in the sediment and the trigger is "
     "at the surface. Explains dieback in water whose measured oxygen never fell.",
     "Sulphide in eelgrass tissue against light at the bed and sediment sulphide - "
     "the three together, which is the whole point.",
     "Tissue sulphide, porewater sulphide, and light at the bed at the same "
     "stations. Danish research groups have done this; monitoring does not."),
    ("T2", "T", "Loss of the sulphide-detoxifying symbiosis", ["O7", "O3"],
     "Seagrass beds host lucinid clams whose gill bacteria oxidise sulphide, keeping "
     "the rhizosphere habitable. Plant, clam and bacterium are a three-way "
     "partnership.",
     "Lose the clams - to trawling, to hypoxia, to anything in group D - and the "
     "seagrass loses its sulphide protection **with no change in any nutrient**. "
     "This is the mycorrhizal story with the partner outside the plant, and it makes "
     "vegetation loss a consequence of fauna loss rather than of water quality.",
     "Lucinid presence and sulphide-oxidising activity in beds that persist against "
     "beds that failed, at matched water quality.",
     "Infaunal bivalve records within seagrass beds. In the ODA fauna data if "
     "anyone looks for it."),
    ("T3", "T", "Wasting disease with stress-modulated virulence", ["O7"],
     "*Labyrinthula zosterae* destroyed most Atlantic eelgrass in the 1930s and is "
     "still present. Virulence depends on host condition: plants under low light, "
     "heat or sulphide stress are far more susceptible.",
     "The proximate cause of death is a pathogen; the reason it succeeded is a "
     "stressor. Attribution to either alone is wrong, and a survey recording only "
     "the die-off sees neither.",
     "Pathogen prevalence alongside host stress indicators, rather than either "
     "alone.",
     "Labyrinthula screening in Danish eelgrass. Not routine."),
    ("T4", "T", "Marine replant failure: negative sediment feedback", ["O7", "O3"],
     "Restoration plantings fail in sediment whose chemistry looks adequate - the "
     "marine form of replant disease. Candidate causes are the accumulated "
     "pathogens, the missing symbionts of T2, the lost binding of D8, and autotoxic "
     "residues.",
     "Recovery is blocked by a property of the *medium* rather than of the water, so "
     "improving water quality produces nothing. Directly testable, and the test is "
     "the same one horticulture uses: does the plant grow in this ground, and does "
     "it grow if you replace or inoculate the ground?",
     "Transplant trials into failed sites, with and without sediment inoculation "
     "from a functioning bed.",
     "Restoration trials with sediment treatments. A handful of Danish eelgrass "
     "trials exist; this design does not."),
    ("T5", "T", "Loss of sediment suppressiveness", ["O7", "O3"],
     "Some soils suppress disease purely through their microbial community, and "
     "suppressiveness is transferable - mix 1-10% of a suppressive soil into a "
     "conducive one and it becomes suppressive. Anaerobiosis and fumigation destroy "
     "it.",
     "A sediment can lose a protective property that no chemical measurement "
     "detects, and regain it only by re-inoculation. If marine sediments behave the "
     "same way, sediment transplantation is a plausible intervention nobody has "
     "tried.",
     "Whether sediment from a healthy bed confers resistance when mixed into a "
     "failed one - the standard transfer assay.",
     "Sediment microbial community composition, and transfer experiments. Neither "
     "exists here."),
    ("T6", "T", "Enrichment dissolving the partnership", ["O7", "O4"],
     "High phosphorus suppresses mycorrhizal colonisation: a well-fed plant stops "
     "maintaining the symbiosis that was feeding it and protecting its roots.",
     "Enrichment removes resilience through a *partner* rather than through an ion - "
     "the same shape as the antagonism of K3, one level up in biological "
     "organisation. A nutrient-rich system can be less able to withstand stress "
     "precisely because it is nutrient-rich.",
     "Symbiont abundance along a nutrient gradient, and host stress tolerance with "
     "and without the symbiont.",
     "Rhizosphere community composition along the gradient. Not measured."),
    ("T7", "T", "Anaerobic phytotoxins other than sulphide", ["O7", "O3"],
     "Waterlogged soil generates organic acids, ethylene, and reduced iron and "
     "manganese at toxic concentrations - a suite of phytotoxins well known in "
     "agronomy and distinct from oxygen shortage itself.",
     "Plants die in anoxic sediment for several reasons at once, only one of which "
     "is lack of oxygen. A model with an oxygen term and nothing else attributes all "
     "of it to oxygen.",
     "Porewater organic acids and reduced metals alongside sulphide.",
     "Porewater chemistry beyond the standard nutrients. Rare."),
    ("T8", "T", "Anaerobic conditions select the pathogens", ["O7", "O3", "O6"],
     "Oomycetes - the Pythium and Phytophthora group - swim as zoospores, need "
     "water, and thrive where roots are stressed and oxygen is low. Marine "
     "oomycetes and labyrinthulids exist and are barely studied.",
     "Hypoxia does not only weaken the host; it favours the pathogen. Two effects in "
     "the same direction, so the observed damage exceeds what an oxygen-tolerance "
     "curve predicts.",
     "Pathogen abundance against sediment redox, and host mortality against both.",
     "Marine oomycete and labyrinthulid surveys. Essentially none."),

    ("R11", "R", "Marine fungi, the decomposers nobody counts", ["O1", "O2", "O3"],
     "Fungi are the principal degraders of refractory material on land - lignin, "
     "chitin, cellulose - and the reason a forest floor does not simply accumulate. "
     "Marine fungi exist, are diverse, degrade the same recalcitrant fractions, and "
     "are absent from essentially every marine monitoring programme including "
     "Denmark's.",
     "A whole functional guild in the decay relay of R3 is unobserved. If the "
     "recalcitrant fraction is accumulating - which R4 predicts under nitrogen "
     "enrichment - the organisms that would have degraded it are the ones nobody is "
     "looking at, and their loss would be invisible by construction.",
     "Fungal biomass and community composition in sediment against the recalcitrant "
     "organic fraction. Standard molecular methods; the question is simply not "
     "asked.",
     "Marine fungal surveys. Essentially none in Danish waters."),

    # ---- S ----------------------------------------------------------------
    ("S1", "S", "Retention is a property of the medium and varies by an order of "
     "magnitude", ["O1", "O4"],
     "Denmark is split between sandy glacial outwash in western Jutland - low clay, "
     "low organic matter, low exchange capacity, high leaching, the Arenosol case - "
     "and clayey moraine in the east. The same application leaches very differently "
     "from each.",
     "A single national retention figure, or a coefficient fitted to national "
     "averages, describes nowhere. The regulatory pressure assigned to an individual "
     "farm is a soil model output wearing a water-policy label, for a quantity its "
     "own producers say cannot be measured directly.",
     "Measured leaching from paired sites on contrasting soils under the same "
     "management - which is the only thing that would validate the map.",
     "Soil type at field resolution with matched drainage measurements. The soil map "
     "exists; the paired validation largely does not."),
    ("S2", "S", "Phosphorus saturation, and legacy leakage", ["O1", "O4"],
     "Sorption sites are finite. Degree of phosphorus saturation is already used in "
     "Dutch and Danish regulation, and soils in high-livestock areas are saturated "
     "after decades of manure. Past that point, applied P goes straight to runoff.",
     "**Legacy P leaks regardless of current application.** Stopping today does not "
     "stop the flux, so a load reduction produces no response for reasons that have "
     "nothing to do with the sea - which is indistinguishable, from the marine end, "
     "from the sediment legacy of H2 or the missing precondition of L4.",
     "Degree of phosphorus saturation by catchment against measured P flux, and the "
     "flux's response to application changes.",
     "Soil P status by area. Denmark holds this; it is not carried into the marine "
     "argument."),
    ("S3", "S", "Sorption is hysteretic - a ratchet on the land side too", ["O4"],
     "Phosphate enters the sorbed and occluded pools far more readily than it "
     "leaves. In the most weathered soils occlusion is effectively irreversible.",
     "The land stores nutrient on a different timescale from the one policy operates "
     "on, in both directions - slow to fill and slow to empty. Symmetrical with the "
     "iron shuttle in the sediment, and for the same mineralogical reason.",
     "Desorption isotherms alongside the sorption ones, which are the half usually "
     "measured.",
     "Sorption-desorption experiments on Danish soils. Standard method."),
    ("S4", "S", "Total is not available", ["O1", "O4"],
     "Soil science distinguishes resin, bicarbonate, hydroxide, acid and residual "
     "phosphorus pools by sequential extraction, because total P says almost nothing "
     "about what an organism can get. Marine sediment P is generally reported as a "
     "bulk total.",
     "A sediment can be P-rich and P-poor at once. Any budget built on totals "
     "mis-states both the stock and the flux, and the error is not small.",
     "Sequential fractionation of marine sediment phosphorus, the standard soil "
     "method applied to the bed.",
     "Fractionated sediment P. The method is seventy years old and is not routine "
     "in marine monitoring."),
    ("S5", "S", "Buffering scales with the volume of reactive medium", ["O1", "O3"],
     "The Leptosol lesson: a soil under 25 cm deep has almost no capacity to absorb "
     "a shock, because buffering is proportional to the volume of material doing the "
     "buffering.",
     "Shallow water bodies and thin sediment layers swing further on the same load, "
     "so depth belongs in the load coefficient rather than as a covariate - and the "
     "areas most likely to be shallow are the ones people swim in.",
     "Response amplitude against water depth and sediment thickness, at matched "
     "load per unit area.",
     "Bathymetry and sediment thickness per area. Bathymetry is held; sediment "
     "thickness is not."),
    ("S6", "S", "Retention capacity is saturable, so the coefficient is not "
     "constant", ["O1", "O4"],
     "Retention is treated as a fixed fraction. If the mechanisms behind it - "
     "denitrification capacity, sorption sites, organic matter - are finite and have "
     "been loaded for decades, the fraction falls over time.",
     "The same application delivers more to the sea now than it did in 1990, so a "
     "coefficient fitted on the early record over-states present retention and "
     "under-states present delivery. Fitting a constant to a declining quantity also "
     "produces exactly the systematic drift DCE report in their own TN models.",
     "Retention estimated separately by era, rather than fitted once across the "
     "whole record.",
     "The same catchment flux data, split by period. Requires no new measurement at "
     "all."),

    ("L6", "L", "The degraded bed is classified as its own habitat type",
     ["O3", "O7"],
     "A chronically trawled seabed and a naturally sandy one look the same in a "
     "sediment sample, and habitat classification records both as sand. The "
     "flattened state is then enshrined as a habitat *type* with its own expected "
     "community, against which it scores as healthy.",
     "The most thoroughly degraded areas are graded against the standard their own "
     "degradation set. This is the shifting baseline made administrative, and it is "
     "not a metaphor - it is what a classification key does when it types states "
     "rather than histories.",
     "Habitat classification against disturbance history, not against present "
     "sediment. Any area classified as sand whose historical charts or fisheries "
     "records show structure is a positive case.",
     "Historical seabed charts, old fisheries records, and trawling effort - the "
     "history, which is exactly what a classification key discards."),

    # ---- R ----------------------------------------------------------------
    ("R1", "R", "The C:N threshold, and fat as a nitrogen sink", ["O1", "O2", "O4"],
     "Decomposer microbes build biomass near C:N 8-10 at about 40% carbon-use "
     "efficiency, so there is a threshold near C:N 25: below it decay releases "
     "mineral nitrogen, above it decay consumes it. Straw at C:N 80 starves the next "
     "crop. Fat has no nitrogen at all.",
     "**An input with zero nitrogen content lowers measured nitrogen**, because the "
     "bacteria decomposing it scavenge dissolved N from the water to build "
     "themselves. A fat-loaded water can read as less eutrophic on the regulated "
     "indicator while being more degraded, and the direction of that bias is "
     "opposite to what everyone assumes.",
     "Dissolved inorganic nitrogen drawdown following organic-carbon inputs of known "
     "C:N, against inputs of the same carbon with nitrogen in them.",
     "C:N of the material actually discharged, not just its N and COD separately. "
     "Both numbers exist in discharge monitoring and the ratio is never formed."),
    ("R2", "R", "Priming of the old sediment pool by fresh carbon", ["O1"],
     "Adding labile carbon to soil accelerates decomposition of the old recalcitrant "
     "pool, because the microbes gain the energy to attack the hard fraction. "
     "Decades of soil science; not applied to marine sediment in assessment.",
     "An input's oxygen demand exceeds its own COD, because it unlocks stored "
     "carbon. The measured load understates its effect, and the sediment legacy of "
     "H2 stops being an inert stock.",
     "Oxygen demand following a labile input, against the input's own COD.",
     "Sediment incubation experiments with and without labile addition. Standard "
     "method, not run here."),
    ("R3", "R", "The decay relay stalls when a stage is removed", ["O2", "O1", "O3"],
     "Decomposition is a relay - leaching, fragmentation by detritivores, microbial "
     "catabolism, humification - and removing a link leaves material unprocessed. "
     "Australian cattle dung sat on the ground until dung beetles were imported.",
     "The terrestrial homologue is **thatch** in turfgrass: a greasy organic mat "
     "that forms when production outruns decomposition, whose classic causes are "
     "heavy nitrogen, pesticides that kill earthworms, and compaction - and which is "
     "treated by restoring the fauna, not by feeding the grass less. Also mull humus "
     "turning to mor: fauna-worked and incorporated, becoming raw and matted. If "
     "fedtemøg is a stalled relay, it forms when the *fragmenters* go, which is what "
     "hypoxia, trawling and toxicants each do independently of any nutrient.",
     "Deposited organic matter and its processing state against macrofaunal biomass, "
     "not against nutrient load.",
     "Sediment organic content with matched fauna, at the same stations. Both are in "
     "the ODA record and are not analysed together."),
    ("R4", "R", "Nitrogen enrichment retards decay of the recalcitrant fraction",
     ["O1", "O2"],
     "Well established in soil: nitrogen accelerates decay of labile litter but "
     "suppresses the lignin-degrading enzymes of white-rot fungi, so recalcitrant "
     "material decays *slower* under high nitrogen and the persistent pool grows.",
     "Enrichment builds the refractory reservoir even as it speeds the easy "
     "fraction - so nutrient loading and sediment legacy are not two independent "
     "problems but one, with a sign nobody has checked in the sea.",
     "Decay rate of refractory versus labile marine organic matter along a nutrient "
     "gradient.",
     "Litter-bag or incubation studies with characterised organic fractions. Common "
     "in soil science, rare in marine work."),
    ("R5", "R", "The terminal electron acceptor cascade, and why salt changes it",
     ["O1", "O3"],
     "Decay runs down a ladder of electron acceptors - O₂, then nitrate, then "
     "manganese, then iron, then sulphate, then CO₂ - each yielding less energy. "
     "Freshwater carries 5-30 mg/L of sulphate and so passes it quickly to "
     "methanogenesis. Seawater carries 2,700 mg/L, a hundred to five hundred times "
     "more, and sulphate reducers outcompete methanogens for hydrogen and acetate.",
     "**Marine anoxia poisons as well as suffocates; freshwater anoxia mostly just "
     "suffocates.** Anoxic lake sediment makes methane. Anoxic marine sediment makes "
     "sulphide, without limit, because the reservoir is effectively infinite. Every "
     "intuition carried over from freshwater eutrophication understates the marine "
     "case by exactly this mechanism.",
     "Sulphide and methane production rates against salinity along the Danish "
     "gradient, which spans the transition.",
     "Porewater sulphide and methane by station. Rarely measured."),
    ("R6", "R", "Sulphide locks the iron that would hold the phosphate", ["O1", "O4"],
     "Sulphide precipitates FeS, removing the iron oxides that bind phosphate in "
     "oxic sediment. A salt-specific step, because freshwater lacks the sulphate to "
     "make enough sulphide.",
     "Marine sediments release far more phosphate under anoxia than freshwater ones, "
     "so the Baltic phosphorus feedback is strong *because of the salt*. Combined "
     "with the iron shuttle, each episode leaves less iron and less binding capacity "
     "than the last.",
     "Sediment Fe:S and Fe:P ratios against phosphate release rate.",
     "Sequential iron and sulphur extraction on sediment. Not routine here."),
    ("R7", "R", "Estuarine flocculation deposits river carbon at the coast",
     ["O1", "O2"],
     "Dissolved organic matter and clay from fresh water flocculate on meeting salt "
     "and drop out of suspension, concentrated in the mixing zone.",
     "Riverine organic carbon does not disperse - it is deposited in a band right at "
     "the coast, which places the oxygen demand exactly where the shallow, stratified "
     "water and the bathing beaches are. A load figure at the river mouth therefore "
     "understates the local concentration of its effect.",
     "Sediment organic carbon along a salinity transect from each river mouth.",
     "Sediment organic content with matched salinity. Obtainable."),
    ("R8", "R", "Lipids are less soluble in seawater", ["O2"],
     "Salting-out: dissolved organics, and lipids especially, are less soluble at "
     "high ionic strength and partition preferentially into films, aggregates and "
     "the surface microlayer.",
     "The same fat load produces more film and aggregate in salt water than in "
     "fresh - a candidate reason greasiness is a marine and brackish complaint, and "
     "a link between group B's imported fat and group J's surface film.",
     "Partitioning of lipid between dissolved, particulate and microlayer fractions "
     "across the salinity gradient.",
     "Lipid fractionation by salinity. Not measured."),
    ("R9", "R", "Home-field advantage, and novel material", ["O1", "O2"],
     "Litter decomposes fastest in the community adapted to it. Material a community "
     "has never encountered - novel chemicals, invasive species' tissue, synthetic "
     "polymers - decomposes slower and accumulates.",
     "Accumulation with no change in loading rate, simply because what arrives has "
     "changed. Connects the novo-chemical argument to the decay argument: a "
     "substance with no degradation terminus is a decay relay with no final stage.",
     "Decay rate of local versus novel organic material in the same water.",
     "Comparative decomposition assays. Not run."),
    ("R10", "R", "Osmotic discontinuity for the decomposers themselves", ["O1"],
     "Freshwater and marine decomposer communities are different organisms, and "
     "neither functions well in the other's water. The salinity front is a "
     "discontinuity in the decomposition machinery, not only in the chemistry.",
     "Organic matter crossing the front is briefly processed by neither community, "
     "so the mixing zone is a decay bottleneck as well as a deposition zone - "
     "compounding R7 at the same place.",
     "Decomposition rate as a function of salinity, holding material constant.",
     "Cross-transplant incubations. Not run."),

    # ---- L ----------------------------------------------------------------
    ("L1", "L", "The reference condition never existed", ["O4", "O7"],
     "Environmental targets are set against a modelled pre-impact state. If that "
     "state is wrong - if the coast was never as clear, as vegetated or as "
     "oligotrophic as the model supposes - then the gap being closed is partly an "
     "artefact of the model rather than a loss.",
     "The target is unreachable, and effort produces no measured improvement no "
     "matter how much is spent. Indistinguishable, from inside, from a system that "
     "is responding too slowly.",
     "Independent evidence of past state: sediment cores, historic charts, "
     "photographs, fisheries and harbour records, and accounts of what the water "
     "looked like.",
     "Dated sediment cores with diatom and pigment stratigraphy. Some exist; they "
     "are not what the reference condition is derived from."),
    ("L2", "L", "The reference is a model output treated as a fact", ["O4", "O7"],
     "Denmark's chlorophyll target is computed by ensemble modelling of a reference "
     "situation, then scaled by an EU-agreed ratio of 0.6. Both halves are choices, "
     "and neither is a measurement.",
     "The requirement moves when the model or the ratio is revised, with no change "
     "in the sea. This is the residual-estimator problem relocated to the target "
     "instead of the source.",
     "The sensitivity of the national indsatsbehov to the reference model's "
     "assumptions and to the EQR value - a one-line calculation nobody publishes.",
     "The reference model's assumptions, and the indsatsbehov recomputed across "
     "their plausible range."),
    ("L3", "L", "The trend depends on the start year", ["O1", "O4", "O7"],
     "Almost every Danish series begins in the 1970s or later, at or near the "
     "historical maximum of nutrient loading. A trend measured from a peak is a "
     "recovery; the same data from a different start is something else.",
     "The direction and size of every reported change is a function of where the "
     "record was cut, and the cut is set by when monitoring began rather than by "
     "anything about the sea.",
     "Every trend recomputed across all plausible start years, reported as a "
     "surface rather than a single number.",
     "The longest available series, and the pre-monitoring evidence from L1."),
    ("L4", "L", "Recovery is blocked by something other than the driver",
     ["O7", "O3"],
     "A target can be unreachable because a *different* thing is missing - seed "
     "stock, substrate, the bioturbators, the iron the sediment lost - while the "
     "driver being managed is already at the required level.",
     "Load falls to target and the indicator does not follow. Attributed to lag; "
     "equally consistent with a missing precondition that no amount of load "
     "reduction supplies.",
     "Transplant and restoration experiments: put the vegetation or the fauna back "
     "where conditions are said to be adequate and see whether it holds.",
     "Restoration trials with controls. A handful exist in Denmark; they are "
     "decisive evidence and are not treated as such."),
    ("L5", "L", "The reference sites are not references", ["O3", "O4"],
     "Where the reference is spatial rather than historical - a comparable "
     "unimpacted area - the comparison assumes such an area exists. In a sea with "
     "no unfished, undredged, undeposited water anywhere, it may not.",
     "Every site is degraded relative to an unobservable baseline, so the gradient "
     "between them understates the total change and the fitted coefficient is "
     "biased toward zero. The floor effect of U3, applied to the whole country.",
     "Whether any candidate reference area is genuinely unimpacted on the D and E "
     "routes, not merely on nutrients.",
     "Trawling, dumping and contaminant coverage for the areas used as references."),

    # ---- Z ----------------------------------------------------------------
    ("Z1", "Z", "Light: too little, and too much", ["O7", "O4", "O3"],
     "The floor is the eelgrass requirement, roughly 11-14% of surface irradiance. "
     "The ceiling is real too: photoinhibition and UV damage at the surface, which "
     "is why some species do worse in the clearest water.",
     "Both tails, as with every window. A management target expressed only as *more "
     "light is better* is the same error as a nutrient target expressed only as "
     "*less is better*.",
     "Response across the full irradiance range, not against a single threshold.",
     "Kd and water depth together give light at the bed. Both are in the record; "
     "the product is rarely formed."),
    ("Z2", "Z", "Light quality, not quantity: browning", ["O7", "O4"],
     "Water attenuates red first, then blue, and coloured dissolved organic matter "
     "shifts the surviving spectrum brown-green. Photosynthetic pigments are tuned "
     "to particular wavelengths, so **which** organisms can photosynthesise changes "
     "even at constant total irradiance. CDOM export from catchments has been rising "
     "across Nordic waters - the browning phenomenon - and it is driven by land use, "
     "hydrology and recovery from acidification rather than by nutrients.",
     "Community composition shifts with no change in Kd's magnitude, because Kd is "
     "one number where the mechanism is a spectrum. A wholly separate driver, "
     "arriving from the same catchments and correlated with nutrient load, which "
     "makes it a confounder as well as a cause.",
     "Spectral attenuation, or at minimum CDOM absorbance, alongside Kd.",
     "Spectral light measurement or CDOM. Kd is measured as a single "
     "broadband number."),
    ("Z3", "Z", "Photoperiod and timing as a cue", ["O7", "O6", "O3"],
     "Day length is a signal as well as an energy supply - it triggers spawning, "
     "settlement, germination and migration. Turbidity changes the effective "
     "photoperiod at depth without changing the calendar.",
     "The organism's clock and its environment come apart, which is a failure of "
     "`V7` rather than of energy supply. Nothing dies of darkness; the population "
     "simply stops reproducing on time.",
     "Timing of reproductive events against light climate at depth, over years.",
     "Phenological observations. Effectively none for Danish marine "
     "invertebrates."),
    ("Z4", "Z", "Temperature: window, and rate", ["O3", "O6", "O7"],
     "A floor, a ceiling, and - separately - a maximum rate of change that "
     "acclimation can follow. The Danish straits sit at the southern edge for "
     "boreal species and the northern edge for others, so both tails are populated.",
     "Warming is usually treated as a mean shift. The lethal events are extremes "
     "and rates, which a mean cannot represent, and the survivable-magnitude "
     "argument is the `V8` avenue.",
     "Response against temperature extremes and rates of change, not annual means.",
     "Bottom temperature at high frequency. In the CTD record now being "
     "downloaded."),
    ("Z5", "Z", "Hydrodynamic energy has a floor as well as a ceiling",
     ["O3", "O1", "O7"],
     "Too much and organisms are dislodged, abraded and buried; too little and "
     "filter feeders are not delivered food, larvae are not dispersed, and nothing "
     "is flushed.",
     "Both a sheltered artificial basin and an exposed dredged channel fail, for "
     "opposite reasons, and neither failure is chemical. Construction changes this "
     "field directly, which connects `C8` to a mechanism.",
     "Bed shear stress distribution against community composition - the whole "
     "distribution, since both tails matter.",
     "Wave and current modelling. Bed shear already computed here from 31 years of "
     "wind."),
    ("Z6", "Z", "Sound, as a cue and as a stressor", ["O3", "O6", "O7"],
     "Larvae of many marine invertebrates and fish orient to reef sound when "
     "choosing where to settle. Shipping noise and pile driving mask it, and "
     "impulsive noise injures directly.",
     "A settlement failure with no chemical, thermal or oxygen signature - the "
     "habitat is fine and nothing arrives, because the signal that would have "
     "guided them is drowned. Another `V7` mechanism, and it follows shipping lanes "
     "and construction rather than catchments.",
     "Settlement rates against ambient noise, and against construction events with "
     "known dates.",
     "Underwater noise measurement. Some exists for marine mammals; essentially "
     "none tied to invertebrate settlement."),
    ("Z7", "Z", "Electromagnetic fields", ["O3"],
     "Subsea power cables generate magnetic and induced electric fields. Elasmo"
     "branchs and some invertebrates use electroreception for navigation and prey "
     "detection.",
     "Behavioural effects along cable routes, which are dated and mapped - so this "
     "is testable even though it is speculative.",
     "Distribution and behaviour against cable routes, before and after "
     "installation.",
     "Cable route and energisation dates. Available. Biological response: not "
     "measured."),

    ("Z8", "Z", "The attenuation budget is never partitioned", ["O7", "O4", "O3"],
     "Kd is one broadband number. Ocean optics decomposes it as a sum of "
     "independent contributions - pure water, phytoplankton pigment, coloured "
     "dissolved organic matter, mineral particles, and non-algal detritus - each "
     "with its own spectral signature, and the partition is standard practice with "
     "a spectroradiometer.",
     "**Kd is measured and its cause is assumed.** A Kd exceedance is attributed to "
     "phytoplankton because phytoplankton is what the framework is about, but the "
     "same number is produced by resuspended mineral sediment, by browning, by a "
     "dredging plume, or by detritus that grew somewhere else and drifted in. This "
     "is the residual-estimator problem in the light indicator: the quantity is "
     "real and measured, and the attribution behind it is not.",
     "Spectral attenuation partitioned into its components, against each candidate "
     "source separately.",
     "Spectral irradiance or absorbance. Denmark measures broadband Kd, which "
     "cannot be partitioned even in principle."),
    ("Z9", "Z", "Epiphyte shading, which bypasses the water column", ["O7"],
     "Nutrient enrichment promotes algae growing directly *on* the eelgrass leaf. "
     "The host is shaded at the blade surface, where no water-column measurement "
     "reaches.",
     "A nutrient effect on light that produces no change in Kd at all, because the "
     "shading happens after the light has passed through the water. So the "
     "nutrient-to-light pathway can operate with the light indicator reading "
     "normally - and grazers that would have cropped the epiphytes are the ones "
     "removed by every other route here.",
     "Epiphyte load per unit leaf area against nutrient status and grazer "
     "abundance.",
     "Epiphyte biomass on eelgrass. Recorded in some research programmes; not in "
     "routine monitoring."),
    ("Z10", "Z", "Mineral plumes from works", ["O7", "O4", "O3"],
     "Dredging, extraction, dumping, cable laying and construction all put mineral "
     "particles into suspension. They attenuate light, abrade, and settle on leaves "
     "and gills, and none of it involves a nutrient.",
     "Turbidity with a known date, a known position and a known operator - so this "
     "is one of the few attenuation sources that is a natural experiment rather "
     "than a background condition.",
     "Turbidity and vegetation response near works, before and after, against "
     "controls at distance.",
     "Works chronology with dates and footprints, and turbidity monitoring - which "
     "large projects are typically required to do and which is rarely reanalysed."),
    ("Z11", "Z", "The weakened host", ["O7", "O3", "O6"],
     "Light starvation need not kill directly. A shaded plant photosynthesises "
     "less, leaks less oxygen from its roots, carries less reserve, and is then "
     "more susceptible to sulphide intrusion (`T1`), to wasting disease whose "
     "virulence tracks host stress (`T3`), and to ordinary starvation.",
     "The proximate cause of death is a pathogen or a poison, and the reason it "
     "succeeded is shade. Attribution to either alone is wrong, and the "
     "conventional analysis - which records the die-off and the nutrient level - "
     "sees neither.",
     "Host condition indices measured alongside both the stressor and the "
     "pathogen, rather than any one of the three.",
     "Carbohydrate reserves, tissue sulphide and pathogen load on the same plants. "
     "Done in research; not in monitoring."),

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

    a("## This list is not exhaustive, and we have no way to know how far off it is\n")
    a(f"There are {len(rows)} entries below. That number should not be read as a "
      "decomposition of the problem, and the field should not be read as closed.\n")
    a("**The direct evidence that it is incomplete is its own history.** The first "
      "version had 71 entries and was written to be thorough. It reached "
      f"{len(rows)} within a single afternoon, and every addition came from an "
      "analogy raised in passing — soil sickness, desertification, sandy deserts, "
      "compost going anaerobic, turfgrass thatch, replant disease. None of those "
      "came from searching the marine literature. A list that grows by three "
      "quarters in one conversation is not a list anyone should call complete, and "
      "there is no reason to think the next conversation would add fewer.\n")
    a("Three further problems, which matter for what can be concluded:\n")
    a("**It is not a partition.** The groups sit at different levels of "
      "abstraction and cut across each other. Some entries are mechanisms, some are "
      "conditions that let a mechanism operate, some are descriptions of a state, "
      "and some — group I especially — are not about the sea at all but about the "
      "instrument. They do not tile anything.\n")
    a("**The entries are not independent.** Sulphur alone appears as an oxygen "
      "sink (`E1`), as reduced bed chemistry (`M7`), as the reason the marine "
      "electron-acceptor cascade differs from the freshwater one (`R5`), as the "
      "release mechanism for sediment phosphate (`R6`), and as the poison that "
      "kills eelgrass from below (`T1`). That is one element seen from five sides, "
      "not five causes. **Counting entries therefore says nothing about weight**, "
      "and a group with fourteen entries is not thereby more important than one "
      "with four.\n")
    a("**Some causes may not separate at all.** Several of these plausibly have no "
      "independent existence and occur only in combination — the light-and-sulphide "
      "interaction of `T1`, the mixture effects of `U1`. Listing them as separable "
      "items imposes a structure the world may not have.\n")
    a("> **The consequence for scoring.** Any ranking computed over this field is a "
      "ranking *within the field*, not a decomposition of reality. A statement of "
      "the form \"mechanism X accounts for n% of the problem\" would require the "
      "field to be complete, disjoint and independent, and it is none of the three. "
      "Making that claim anyway would be the residual-estimator error of "
      "[RESIDUAL.md](#RESIDUAL.md) committed one level up — treating what is left "
      "over after our own enumeration as if it were a measurement of the world.\n")
    a("What the register is for is narrower and still worth having. It converts "
      "*the cause is X* into *X is one of at least a hundred and twenty-seven, and "
      "here is the observable that would tell it apart from its neighbours*. It is "
      "written down before anything is scored so that it cannot be trimmed "
      "afterwards to whatever the data happened to support. Absence from this list "
      "is not evidence of absence, and additions are wanted.\n")

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
    a("### The categorical avenues\n")
    a("Enumerating mechanisms one at a time has no stopping rule. Enumerating the "
      "*kinds* of way a living thing can fail is a smaller problem, and it converts "
      "exhaustiveness from a hope into a procedure: for each avenue, each "
      "requirement, and each functional group, ask whether an instance is in the "
      "register. Gaps then appear by construction rather than by luck.\n")
    a("An organism is a system that maintains itself against entropy using flows. "
      "It fails when a flow it needs stops, when something arrives that harms it, "
      "when the field it sits in leaves its tolerable range, when it is physically "
      "destroyed, when something eats or infects it, when a partner goes, when it "
      "fails to replace itself, or when the change outruns its capacity to "
      "adjust.\n")
    a("| | avenue | | failure modes | the things it happens to | where it lives below |")
    a("|---|---|---|---|---|---|")
    for i, n, w, rt, gr, cm, ce in AVENUES:
        a(f"| `{i}` | **{n}** | {w} | {cm} | {ce} | {gr} |")
    a("")
    a("### Where this actually closes\n")
    a("The chemical avenues are the clean case, and they are worth stating exactly "
      "because they are the only place the argument reaches genuine "
      "exhaustiveness.\n")
    a("> For any chemical species there are exactly **three** ways it can harm: "
      "below the floor of what is needed, above the ceiling of what is tolerated, "
      "or present at all where the tolerated amount is zero. That is a partition of "
      "the real line against a tolerance window. Nothing can hide between the "
      "cases, and there is no fourth.\n")
    a("Liebig's floor and Shelford's ceiling are the first two, and the essential "
      "trace metals sit on both — copper is required and copper is a biocide, "
      "within about one order of magnitude. The window is the whole story, and "
      "*outside the window* is completely enumerated by those three.\n")
    a("**What does not close is the list of chemicals.** Tens of thousands are in "
      "commerce and a few dozen are measured (`U4`). So `V1` and `V2` have "
      "exhaustive failure modes over an open set of substances: complete on one "
      "axis, unbounded on the other, and an avenue is only as closed as its weaker "
      "axis.\n")
    a("`V3` is the most nearly closed of all, and is the one worth pushing on. The "
      "physicochemical fields an organism sits in are a short list — light, "
      "temperature, salinity, pressure, pH, redox potential, hydrodynamic energy, "
      "sound, electromagnetic field — and it is close to complete.\n")
    a("But a field is not a chemical, and the difference matters. **A chemical has "
      "one axis: how much. A field has several, each carrying its own floor and "
      "ceiling.** Light is not only how much, but of what wavelengths, for how "
      "long, and when — and browning changes the second without changing the first, "
      "while turbidity changes the third at depth without changing the calendar. "
      "Temperature has a window and, separately, a maximum rate of change. "
      "Hydrodynamic energy has a floor as well as a ceiling: too little and filter "
      "feeders starve, too much and everything is abraded off.\n")
    a("So the exhaustive treatment here is a small cross-product — **fields × "
      "dimensions × the same three failure modes** — and all three factors are "
      "enumerable. That makes it the most nearly closable part of the register, and "
      "group **Z** exists to work through it. Denmark already measures most of the "
      "fields; what is missing is mostly the extra dimensions, which is a cheaper "
      "gap to close than any other on this page.\n")
    a("**`V4` and `V5` close better than the chemical ones, for a reason worth "
      "stating.** Destruction and attack are both done *by* something, and the set "
      "of possible agents is drawn from the biota. That set is bounded by what "
      "exists. The chemical set is not: substances are manufactured, tens of "
      "thousands are in commerce, and the list grows every year by decision. One "
      "set is discovered, the other is invented, and only the invented one is "
      "genuinely unbounded.\n")
    a("For physical destruction the agent list is startlingly short. Humans, with a "
      "finite inventory of gear — trawl, dredge, anchor, propeller, cable plough, "
      "extraction head, dumped spoil, construction plant. Then storms, ice, "
      "currents, and the bioturbators and bioeroders. That is close to a complete "
      "enumeration, and it is why group D can be checked nearly to the end.\n")
    a("For biotic attack the set is bounded but **badly catalogued**, and the gap "
      "is concentrated at the small end: viruses, bacteria, protists, fungi and "
      "oomycetes. Marine virioplankton runs to roughly ten million particles per "
      "millilitre and lyses a large share of the bacterial standing stock every "
      "day, and Danish marine monitoring counts none of it. The limit here is "
      "record-keeping rather than principle, which is a better problem to have than "
      "the chemical one.\n")
    a("`V6` remains the hardest: the failure modes are enumerable and the organisms "
      "are bounded, but the *relationships between them* are not, and a partnership "
      "nobody has described cannot be missed from a list. The lucinid clam "
      "symbiosis of `T2` was published in 2012; before that, its loss was an "
      "unrepresentable cause.\n")

    a("**This immediately found a hole.** `V7`, failure to replace itself, had "
      "almost no instances in a register of 127 — no propagule supply, no "
      "connectivity, no settlement cues, no phenological mismatch, no Allee "
      "effects. A population can go extinct locally without a single individual "
      "being killed by anything on the list, and the register could not represent "
      "it. `V8`, rate exceedance, was similarly thin: a disturbance returning "
      "faster than recovery completes is not the same thing as the same disturbance "
      "once, and nothing said so. Group **W** exists because these two avenues were "
      "empty, which is the procedure working.\n")
    a("We do not claim the avenue list is closed either. But it is a much better "
      "level at which to attempt closure than the level of instances, and unlike "
      "the instance list it suggests where to look next.\n")

    a("### Routes — the sufficient paths to those outcomes\n")
    a("Oxygen deficit is **one** of these. It is neither necessary nor sufficient "
      "for any terminal outcome, and several of the others leave no oxygen "
      "signature at all — a poisoned water can be fully oxygenated.\n")
    a("These seven are not claimed to be all of them either, and they are not even "
      "cleanly separable from one another: `M7` is partly a special case of `M2`, "
      "and `M5` ends by feeding `M3`. They were arrived at by asking what could "
      "produce the terminal outcomes, which is a question with no natural stopping "
      "point. Treat them as seven routes we could name, not as the routes there "
      "are.\n")
    a("| | route | what it is |")
    a("|---|---|---|")
    for i, n, w in ROUTES:
        a(f"| `{i}` | **{n}** | {w} |")
    a("")
    a("### The cascades, and where they converge\n")
    a("Iltsvind is one *kind* of dying out, with one particular chain of "
      "consequences. Every other route has its own chain, and each of them closes "
      "into a loop that sustains itself.\n")
    a("| route | the cascade | why it does not stop |")
    a("|---|---|---|")
    for i, n, chain, why in CASCADES:
        a(f"| `{i}` **{n}** | {chain} | {why} |")
    a("")
    a("### Why they converge\n")
    a("The convergence is not a coincidence and it is not vagueness about the "
      "damage. It follows from what a depletion actually does.\n")
    a("**A depletion does not kill indiscriminately. It removes exactly those "
      "organisms that required the missing thing, and releases those that did "
      "not.** Oxygen depletion kills aerobes and releases anaerobes. Silicon "
      "depletion removes diatoms and releases flagellates. Cobalamin depletion "
      "removes the auxotrophs and leaves the bacteria that make it. Carbonate "
      "depletion removes calcifiers and no one else. Light starvation removes what "
      "is rooted at depth. Each is a filter with its own specific shape.\n")
    a("But every filter selects in the same direction, because what survives a "
      "filter is whatever had the fewest requirements to begin with — fast, small, "
      "short-lived, unselective, needing no structure and no partner and no "
      "particular chemistry. Run any filter and you enrich for that. Run several "
      "and you enrich harder.\n")
    a("> So it is not that all damage looks alike. It is that **all selection runs "
      "the same way**, and the endpoint is the set of organisms that no filter "
      "removes. That is what the phrase *primordial soup* is reaching for, and it "
      "is why an outcome can be reached from a dozen unrelated directions and look "
      "identical from every one of them.\n")
    a("### The cause need not be near the effect\n")
    a("A cascade moves the cause away from the effect, in two directions at once.\n")
    a("**In trophic distance.** Remove a predator and the change appears two levels "
      "down. The Baltic cod collapse of the 1980s and 90s released sprat, whose "
      "grazing suppressed the large copepods, and the plankton community that "
      "resulted has not reverted. Nothing in the water chemistry moved. A search "
      "for causes confined to water quality cannot find this, and a coefficient "
      "fitted across the period absorbs it silently.\n")
    a("**In time.** The removal can be decades old and permanent. If the current "
      "state is held in place by a predator fished out in 1990, no measurement "
      "taken now — of anything — will contain the cause.\n")
    a("Together those mean the search radius has to include things that do not look "
      "like water quality at all: fishing effort, stone extraction, a bridge, a "
      "disease outbreak in a bivalve, a species introduced from a ballast tank.\n")
    a("> And the Yellowstone wolves are worth keeping in mind for a second reason. "
      "That cascade — wolves to elk to willow to beaver to the shape of the rivers "
      "— became the standard textbook illustration, and it has since been "
      "substantially challenged: the elk decline had other causes running at the "
      "same time, and the willow recovery was patchy and confounded. A compelling "
      "cascade narrative outran its evidence, in a well-studied system, watched by "
      "everyone. That is the same failure this project attributes to the nitrogen "
      "account, and it is available to us on exactly the same terms.\n")

    a("It also explains why the state maintains itself. The survivors of the filter "
      "are precisely the organisms that do not perform the functions — irrigating "
      "sediment, filtering water, holding it down, providing structure, "
      "detoxifying sulphide — whose loss made conditions worse in the first "
      "place.\n")
    a("They converge. Whichever chain runs, the organisms left standing are the ones "
      "with the highest maximum growth rate, the lowest resource requirement, the "
      "shortest generation time and the least dependence on structure — fast, small, "
      "unselective, ungrazed. Every route ends in the same place, and that place is "
      "what the word *primordial soup* is reaching for: not an absence of life but "
      "an abundance of the lowest forms of it, which is why it registers as high "
      "biomass and high productivity on instruments built to treat those as health.\n")
    a("> **The terminal state is multiply realisable, so observing it identifies no "
      "cause.** A dead, greasy, over-productive water looks the same whether it was "
      "suffocated, poisoned, dredged, fished out, shaded, gelled or soured. "
      "Attribution has to come from the *discriminating* observables — the ones each "
      "hypothesis below names — and never from the end state, however carefully the "
      "end state is measured.\n")
    a("This is also why a well-measured route is not thereby the route taken. Oxygen "
      "is the best-instrumented of the seven by a wide margin. That is a fact about "
      "Danish monitoring, not about Danish water.\n")

    a("### Every requirement, put through the oxygen questions\n")
    a("Oxygen is famous for having a feedback loop. That is a fact about how much "
      "attention it has had, not about how unusual it is. Taking the standard list "
      "of what a plant or an alga requires, and asking of each the same two "
      "questions — *can it be depleted here*, and *is there a loop that makes the "
      "depletion feed itself* — the answer is yes far more often than the framing "
      "suggests, and two of the loops are better established than the oxygen one.\n")
    a("| | requirement | can it deplete? | the loop | evidence |")
    a("|---|---|---|---|---|")
    for sym, name, role, dep, loop, ev in ELEMENTS:
        a(f"| `{sym}` | **{name}** — {role} | {dep} | {loop} | {ev} |")
    a("")
    a("Three things fall out of that table.\n")
    a("**Phosphorus and iron have the strongest loops, not oxygen.** The anoxic "
      "release of iron-bound phosphate is textbook, and Denmark's own assessment "
      "invokes it to explain why the Skive and Lovns phosphorus models fail. The "
      "iron shuttle is worse still, because it is a *ratchet* rather than a cycle: "
      "each hypoxic episode permanently exports sediment iron, so the bed loses "
      "phosphate-binding capacity that does not come back when the oxygen does.\n")
    a("**Two of the loops run against the policy.** Hypoxia stops nitrification and "
      "so disables denitrification, flipping the sediment from a nitrogen sink to a "
      "nitrogen source; and falling N relative to P selects for cyanobacteria, which "
      "fix nitrogen from the air. Both mean the internal supply can rise while the "
      "external load falls — which is a candidate explanation, on their own "
      "mechanism, for why thirty-five years of load reduction has not produced the "
      "expected recovery.\n")
    a("**Sulphur is the one that makes marine hypoxia different.** Seawater carries "
      "2.7 g/L of sulphate. Once oxygen and nitrate are exhausted it becomes the "
      "terminal electron acceptor, and the supply is effectively unlimited — so the "
      "sea manufactures its own poison, without limit, as soon as the oxygen goes. "
      "Freshwater has no comparable reservoir.\n")

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

    a("## Borrowed from a field that already made this mistake\n")
    a("The structure here — a degraded end state reachable by many routes, "
      "self-reinforcing loops, a ratchet that does not reverse, and a confident "
      "single-cause account with a politically available culprit — is not new. It is "
      "the shape of the African desertification narrative, and that field spent "
      "thirty years correcting it.\n")
    a("What it corrected with is worth copying:\n")
    a("- **Non-equilibrium dynamics.** Ellis and Swift showed that in arid systems "
      "rainfall variance dominates density-dependent processes, so *carrying "
      "capacity* and *overstocking* were the wrong model class rather than the wrong "
      "numbers. That objection took longest to land and mattered most. Here it is "
      "H1 and H4.\n")
    a("- **Longer, spatially replicated measurement.** Satellite records showed the "
      "Sahel greening while the desertification narrative was at its peak. The "
      "measurement reversed the finding. Here that is 6,288 stations and the full "
      "record rather than 29 stations and a window closing in 2012.\n")
    a("- **Checking whether the baseline was ever real.** Fairhead and Leach found "
      "that forest patches in Guinea, read as relics of a destroyed forest, had been "
      "*created* by the villagers living in them. The causal arrow was backwards and "
      "the error lay in the assumed original state. That is group L, and it is the "
      "class of hypothesis this project was missing entirely until the parallel was "
      "pointed out.\n")
    a("The parallel is structural and it is not an argument that either narrative is "
      "false. Land degradation in the Sahel is real in places, and nutrient "
      "enrichment in Danish water is real in places. What the desertification "
      "literature establishes is that a real problem, a confident single-cause "
      "story, and a wrong attribution coexist comfortably for decades — and that the "
      "cost of the error is paid by whoever the available culprit turns out to be.\n")

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
    a("And whatever comes out of that, the caveat at the top holds: the ranking "
      "will be a ranking within this field. The field is open, it is not a "
      "partition, its entries are not independent, and its own history says it is "
      "incomplete.\n")
    a("A1 may well win. That would be a far stronger result for it than the one it "
      "currently has, because it would have been tested against rivals rather than "
      "fitted alone.\n")
    return "\n".join(o) + "\n"


def main():
    rows = H
    ids = [r[0] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate hypothesis id"
    payload = {
        "_completeness": {
            "exhaustive": False,
            "why": "The first version had 71 entries and was written to be "
                   "thorough; it reached 127 in a single afternoon, entirely from "
                   "analogies raised in passing. No reason to believe the present "
                   "list is closer to complete than that one was.",
            "is_partition": False,
            "entries_independent": False,
            "note": "Counting entries says nothing about weight - sulphur alone "
                    "appears as E1, M7, R5, R6 and T1, which is one element seen "
                    "from five sides. Any ranking over this field is a ranking "
                    "within the field, not a decomposition of reality.",
        },
        "avenues": [{"id": i, "name": n, "what": w, "routes": r, "groups": g,
                     "modes_closed": cm, "entities_closed": ce}
                    for i, n, w, r, g, cm, ce in AVENUES],
        "terminal": [{"id": i, "name": n, "what": w} for i, n, w in TERMINAL],
        "routes": [{"id": i, "name": n, "what": w} for i, n, w in ROUTES],
        "cascades": [{"route": i, "name": n, "chain": c, "closes": w}
                     for i, n, c, w in CASCADES],
        "elements": [{"symbol": a_, "name": b_, "role": c_, "depletable": d_,
                      "loop": e_, "evidence": f_}
                     for a_, b_, c_, d_, e_, f_ in ELEMENTS],
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
