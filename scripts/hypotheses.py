#!/usr/bin/env python3
"""Every causal route we can think of to a wrecked Danish shore, as a field.

Showing that a hypothesis rests on poor grounds reduces its political actionability.
It does not show it is wrong, and it does not tell you what is right. The scientific
move is different: enumerate the field of mechanisms that could produce the
observed outcomes, relate every one of them to the same evidence, and score them.

This is step one - the field itself, written down before any of it is scored, so
that the enumeration cannot be quietly trimmed to whatever the data happened to
support. Every entry is stated at full strength, in the same format, and no entry
is introduced as the one the others are alternatives to.

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
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, write_json, write_doc

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
     "M8", "W", "closed", "nearly closed"),
    ("V8", "Rate exceeded",
     "The change is survivable in magnitude but not in speed. Adaptation, "
     "acclimation, migration and recovery all have rates, and a disturbance "
     "returning faster than recovery completes is a different thing from the same "
     "disturbance once.",
     "M9", "W, H1", "closed", "inherits the others"),
]


# Words a reader should not have to already know. Two kinds earn the space.
# Eponyms, where the name carries none of the meaning - "Liebig's floor" tells you
# nothing unless you already know. And words whose morphemes are opaque in English:
# turbid is from Latin turba, a commotion, the same root as turbine and disturb, so
# cloudiness is named after the stirring that causes it.
#
# term -> (what it means, why it is called that)
TERMS = {
    'acetylcholine': (
        'The signalling molecule nerves use at many junctions. Its receptors and the enzyme that clears it are targets for several insecticide classes, and both are universal in animals.',
        'Acetyl plus choline, its chemical parts.'),
    'actinomycete': (
        'A group of soil bacteria that produce most of the antibiotics in clinical use. They have been fighting fungi and each other for hundreds of millions of years, and the pharmacy is their armoury.',
        'The narrow sample of the microbial war that modern medicine happens to have read. The marine equivalent is close to unexplored.'),
    'aerobe': (
        'An organism that needs oxygen to live. Most animals, and many bacteria.',
        'Greek aer (air) plus bios (life). Its opposite is an anaerobe.'),
    'AIS': (
        'Automatic identification system - the transponder ships broadcast for collision avoidance, which incidentally records where everything went.',
        'Designed for safety, useful as an activity archive.'),
    'Alcian blue': (
        'A dye that stains the sticky sugar-based gel algae secrete, which is otherwise transparent. It is the only reason anybody knows the gel is there.',
        'Without it, transparent exopolymer particles are invisible - which is why they went unnoticed until the 1990s.'),
    'algae': (
        'Photosynthetic organisms that are not plants - from single cells drifting in water to seaweeds metres long. Not a single family, just everything green that was left over.',
        'Latin alga, seaweed. A category defined by exclusion, which is why it holds unrelated things.'),
    'Allee': (
        'Below a certain population density, reproduction fails - mates are not found, spawning does not coincide, group defences stop working. The decline then feeds itself.',
        'Warder Clyde Allee, 1930s. The counterintuitive half of population ecology: rarity itself can be the cause of further rarity.'),
    'allelopathy': (
        'One plant chemically suppressing another. Some macrophytes release compounds that inhibit the algae competing with them.',
        'Greek allelon (of each other) plus pathos (suffering).'),
    'ammonium': (
        'The simplest form of dissolved nitrogen, the form in sewage and in decaying material. Bacteria oxidise it to nitrate, consuming oxygen; in alkaline water it converts to ammonia, which is acutely toxic.',
        'From ammonia, ultimately from the temple of Amun in Egypt, near which the salt was collected.'),
    'anaerobic': (
        'Without oxygen - either an environment with none, or an organism that lives without it. Anaerobic decay produces different, often toxic, products.',
        'Greek an- (without) plus aer. Anaerobiosis is the state; anaerobes are the organisms.'),
    'anammox': (
        'Bacteria combining ammonium and nitrite directly into nitrogen gas without needing oxygen. Another route by which nitrogen leaves permanently.',
        'Contraction of anaerobic ammonium oxidation. Only discovered in the 1990s.'),
    'Andosol': (
        'A soil formed on volcanic ash. It fixes phosphate more strongly than any other soil type - fertiliser can disappear from availability almost entirely.',
        'From Japanese an (dark) and do (soil).'),
    'anoxia': (
        'No oxygen at all, as opposed to too little.',
        'Greek an- (without). The step past hypoxia, and chemically a different world - sulphate reduction takes over.'),
    'anoxic': (
        'Containing no oxygen at all, as distinct from merely low. In marine sediment the switch to anoxic is also a switch to a different chemistry, producing sulphide.',
        'Greek an- (without) plus the root of oxygen.'),
    'archaea': (
        'A third domain of life alongside bacteria and eukaryotes - superficially bacteria-like, biochemically very different, and responsible for much methane and ammonia cycling.',
        'Greek archaios, ancient.'),
    'Arenosol': (
        'A sandy soil: little clay, little organic matter, holds almost no water or nutrients, leaches heavily.',
        'Latin arena, sand - the same word as the sand-floored arenas of Rome.'),
    'autoclave': (
        'To sterilise by steam under pressure. Autoclaved material has identical chemistry to the original and no living organisms, which is how you separate a chemical effect from a biological one.',
        'Greek auto (self) plus Latin clavis (key) - the lid seals itself as pressure rises.'),
    'autologous': (
        "From the same individual. An autologous transplant returns a person's own material - banked before a treatment that would destroy it - rather than a donor's.",
        'Greek autos (self) plus logos here meaning relation. The marine version cannot be done after the fact, only before.'),
    'autotroph': (
        'An organism that builds its body from carbon dioxide rather than from other organisms. Plants and algae by photosynthesis, and many bacteria by chemistry.',
        'Greek autos (self) plus trophe (nourishment): self-feeding.'),
    'auxotroph': (
        'An organism that cannot make some essential compound for itself and must obtain it ready-made. Most marine algae are auxotrophs for vitamin B12.',
        'Greek auxein (to grow) plus trophe (nourishment): needs feeding to grow.'),
    'azole': (
        'The largest class of agricultural and medical fungicides. They block sterol synthesis at an enzyme every eukaryote shares, so their selectivity comes from dose and uptake rather than from the target being absent.',
        'Named for the five-membered nitrogen ring they contain.'),
    'bacteria': (
        'Single-celled organisms without a nucleus - the most abundant life on Earth, and in the sea the principal recyclers of everything that dies.',
        'Greek bakterion, a little rod, after the shape of the first ones seen.'),
    'bacteriocin': (
        'A protein weapon one bacterium makes to kill closely related bacteria. Narrower than an antibiotic and aimed at competitors for the same niche.',
        'The diagonal of the microbial war: same against same, because the closest competitor is the most direct threat.'),
    'bacteriophage': (
        'A virus that infects bacteria. The most numerous biological entities on the planet, and in the sea they lyse a large share of the bacterial population every day.',
        'Greek phagein, to eat - literally bacteria-eater.'),
    'bathymetry': (
        'The shape of the seabed - underwater topography. It determines which basins can ventilate and which cannot.',
        'Greek bathys (deep) plus metron (measure).'),
    'Beggiatoa': (
        'A sulphide-eating bacterium that forms thick white mats on oxygen-poor sediment. Its presence is a visible sign that the bed has gone sulphidic.',
        'Named after Francesco Secchi di Beggiato, a 19th-century Italian physician.'),
    'benthic': (
        'Of the seabed - the animals, plants and processes on or in the bottom.',
        'Greek benthos, the depths.'),
    'benthos': (
        'Everything living on or in the seabed, taken together.',
        'Greek benthos, the depths.'),
    'bicarbonate': (
        "The dissolved form most of the ocean's carbon takes. Plants can use it for photosynthesis, and it buffers the water against pH change.",
        "The carbonate system's middle state, between dissolved CO2 and carbonate ion."),
    'bioaccumulative': (
        'Building up in an organism faster than it is excreted, so body burden rises over a lifetime. Distinct from biomagnification, which is the further concentration at each step up the food chain.',
        'One of the three legs of the PBT test, and the reason persistence matters biologically rather than just chemically.'),
    'bioavailability': (
        'The fraction of a substance an organism can actually take up, as against how much is present. Phosphate locked to iron oxide is present and unavailable; so is iron bound to organic molecules.',
        'The reason a total concentration can be almost uninformative about whether anything is short of it.'),
    'biocide': (
        'Any substance intended to kill living things - the umbrella covering pesticides, fungicides, herbicides, antifoulants, disinfectants and wood preservatives.',
        'Literally life-killer. The word is honest in a way the specific ones are not.'),
    'biocontrol': (
        'Using one organism to suppress another instead of using a chemical. It cannot be evaded by a point mutation the way a single-target molecule can.',
        'The practical form of letting the microbial arms race do the work.'),
    'biocrust': (
        'A living skin of cyanobacteria, lichens and mosses binding a desert soil surface. Break it and the sand mobilises.',
        'Biological soil crust. Its marine counterpart is microphytobenthos.'),
    'biofouling': (
        'The community of organisms that colonises any surface left in the sea - within weeks. It is the binding constraint on long instrument deployment, not cost.',
        'Everything in the water is looking for somewhere to attach, and a clean sensor is an opportunity.'),
    'biogenic': (
        'Made by living things. Biogenic structure means reefs, beds and burrows built by organisms rather than by geology.',
        'Greek bios (life) plus genes (born of).'),
    'biomagnification': (
        'A substance becoming more concentrated at each step up the food chain, because predators accumulate everything their prey had. Mercury and some organics do this; most metals do not.',
        'Distinct from bioaccumulation, which is build-up within one organism over its life.'),
    'bioturbation': (
        'The churning of sediment by animals burrowing, feeding and irrigating their tunnels. It mixes oxygen down into the bed.',
        'Bio- plus the same turba: life doing the stirring.'),
    'bioturbator': (
        'An animal that churns sediment by burrowing, feeding or irrigating its tunnels, mixing oxygen down into the bed. Worms, clams and shrimp mostly.',
        'Bio plus Latin turba, a commotion - the same root as turbid and turbine.'),
    'bivalve': (
        'A shellfish with two hinged shells - mussel, clam, oyster, cockle. Most filter their food from the water, which incidentally clears it.',
        'Two valves, meaning the two halves of the shell.'),
    'BOD': (
        'Biochemical oxygen demand - the share of COD that microbes will actually consume, usually measured over five days.',
        'The biologically available part of the oxygen demand.'),
    'brackish': (
        'Water between fresh and fully marine. The Danish straits are brackish, and few species tolerate it, so the communities there are unusually species-poor.',
        'From Dutch brak, salty.'),
    'bundfauna': (
        "Danish for seabed animals - the standard term for the soft-bottom fauna survey that is Denmark's main biological measure of seabed condition.",
        'Bund is bottom. It is what the ODA topic of that name contains.'),
    'carbonic anhydrase': (
        'The zinc-containing enzyme that lets an organism convert bicarbonate into usable carbon dioxide. Without zinc, photosynthesis is throttled however much carbon is around.',
        'Anhydrase: it removes water from carbonic acid.'),
    'CDOM': (
        'Coloured dissolved organic matter - the brown, tea-like tint that dissolved plant material gives water. It absorbs light, especially blue.',
        'Its rise across northern waters is called browning, and it is driven by land use and hydrology rather than nutrients.'),
    'Charney': (
        "A feedback where losing vegetation raises the ground's reflectivity, which weakens the rising air that makes rain, which costs more vegetation.",
        'Jule Charney proposed it for the Sahel in 1975. One of the first climate feedbacks anyone wrote down.'),
    'chemolithotroph': (
        'An organism that lives on energy from inorganic chemical reactions - oxidising hydrogen, sulphide, ammonium, iron or methane. No light, no eating.',
        'Chemo (chemical) plus litho (rock) plus troph (feeding). A way of making a living that has no eukaryotic equivalent at all.'),
    'chemosynthesis': (
        'Building organic matter using energy from chemical reactions instead of from light. The counterpart to photosynthesis, and far older.',
        'It is how the primary producers at hydrothermal vents live, and it is why sulphide can be an energy source rather than only a poison.'),
    'chitin': (
        'The tough material of fungal cell walls and of crustacean and insect shells. After cellulose it is the most abundant biological polymer, and relatively few organisms can digest it.',
        'Greek chiton, a tunic.'),
    'chlorophyll': (
        'The green pigment that captures light for photosynthesis. Measuring it is the standard way to estimate how much algae is in the water - it is a proxy for biomass, not for health.',
        'Greek chloros (pale green) plus phyllon (leaf).'),
    'classical biological control': (
        'Introducing one organism to suppress another. It works, and its failures are the standard cautionary tale, because an agent that does not stay on its intended target cannot be recalled.',
        'The reason a release needs host specificity demonstrated rather than assumed.'),
    'Clostridioides difficile': (
        'The bacterium that takes over a gut whose community antibiotics have cleared. The harm comes from the vacancy rather than from the drug.',
        'The clearest demonstration that occupancy itself was doing the work.'),
    'cobalamin': (
        'Vitamin B12. Built around a cobalt atom, made only by bacteria and archaea, required by most algae.',
        'Cobalt plus amine, after the metal at its centre.'),
    'COD': (
        'Chemical oxygen demand - how much oxygen a substance will consume when fully oxidised. Measured in the same units as the oxygen it removes.',
        'The measurement and the effect are the same quantity, which is unusual and useful.'),
    'cold seep': (
        'A seafloor site where methane or sulphide-rich fluid escapes slowly rather than hot. Like a vent, it supports a community running on chemistry rather than light.',
        'Slower, cooler, and more widespread than vents - including in the North Sea.'),
    'colonisation resistance': (
        'The protection an established community gives simply by occupying the space and consuming the resources, so that an incomer cannot establish. In gut, skin and root zone it is the main protective function the community performs.',
        'A function with no product: nothing is made, nothing is secreted. It is visible only when it is removed.'),
    'commensalism': (
        'A relationship in which one partner benefits and the other is unaffected. In practice the middle of a spectrum rather than a distinct category, and the hardest to demonstrate.',
        'Latin com plus mensa, table: eating at the same table.'),
    'copepod': (
        'A small shrimp-like crustacean, a millimetre or two long, and the main link between algae and fish. Probably the most numerous animal on Earth - and an arthropod, like the insects that insecticides are designed for.',
        'Greek kope (oar) plus pous (foot).'),
    'counterfactual': (
        'What would have happened without the thing you are studying. Most environmental arguments lack one, because the treatment was applied everywhere at once and there is nothing left to compare against.',
        'The reason a staggered rollout is worth more than a simultaneous one, even when the simultaneous one is easier.'),
    'CRISPR': (
        'A bacterial immune system that stores fragments of past viral infections and uses them to recognise and cut the same virus again. Repurposed as the standard gene-editing tool.',
        'An antiviral of bacterial variety - and, like restriction enzymes before it, a weapon captured from the bacteria-phage war and turned into laboratory equipment.'),
    'cross-protection': (
        'Deliberately infecting a plant with a mild virus strain so a severe one cannot establish. Deployed against citrus and papaya viruses.',
        'Vaccination by occupancy rather than by immunity - and it works in organisms that have no immune system to vaccinate.'),
    'cryopreservation': (
        'Freezing living material so that it can be revived later. It is how a community can be banked while it still works, against a future when it does not.',
        'The only technique in this project that buys time rather than information.'),
    'CTD': (
        'The standard instrument lowered through the water column, recording conductivity, temperature and depth continuously - and usually oxygen too. It gives a profile rather than a single value.',
        'Named for the three things it measures. Salinity is calculated from conductivity.'),
    'cyanobacteria': (
        'Photosynthetic bacteria, often called blue-green algae although they are not algae. Some fix nitrogen directly from the air, which lets them grow when nitrogen is scarce, and several make toxins.',
        'The ancestor of one of them was captured and became the chloroplast, which is how plants photosynthesise at all.'),
    'CYP51': (
        'The enzyme that makes sterols - cholesterol in animals, ergosterol in fungi, phytosterols in plants. Azole fungicides work by blocking it, and every eukaryote has one.',
        'A cytochrome P450, numbered by family. The number is the only name it has.'),
    'decomposer': (
        'An organism that breaks down dead material - bacteria, fungi, and the animals that shred it first. Together they are the reason the world is not knee-deep in corpses.',
        'Named for the job rather than for any relationship between the organisms doing it.'),
    'decomposition': (
        'The breakdown of dead material back to simpler substances. It is a relay run by different organisms at each stage, not a single process, which is why removing one link stalls the whole thing.',
        'Latin de- (apart) plus componere (to put together): the undoing of assembly.'),
    'defective interfering particle': (
        'A virus genome missing part of itself, which cannot replicate alone but hijacks the machinery of complete viruses and outcompetes them.',
        'A parasite of a parasite, and one of the ways a viral infection limits itself.'),
    'denitrification': (
        'Bacteria converting nitrate to nitrogen gas, which leaves the water permanently. The only process that actually removes nitrogen from a system.',
        'Undoing nitrification. It needs the nitrate that nitrification makes, so stopping one stops the other.'),
    'denitrifying': (
        'Converting nitrate to nitrogen gas, which removes it from the water permanently. The only process that actually gets rid of nitrogen rather than moving it.',
        'Un-doing nitrification. It requires low oxygen and available carbon.'),
    'desertification': (
        'Land degrading toward desert - a process with many causes and one appearance, which is why attributing it to a single culprit went badly wrong for thirty years.',
        'The parallel this project borrows its cautionary lessons from.'),
    'detritivore': (
        'An animal that eats dead organic material rather than living prey or plants.',
        'Latin detritus (worn away) plus vorare (to devour).'),
    'diatom': (
        'A single-celled alga that builds itself a rigid glass box out of silica. They need dissolved silicon to grow at all, they are the preferred food of most marine grazers, and they sink fast when they die.',
        'Greek diatomos, cut in two - the shell comes in two halves that fit like a petri dish. The name describes the box, not the organism.'),
    'dinoflagellate': (
        'A single-celled alga that swims with two tails and often wears armour plating. Several make toxins, and some cause red tides.',
        'Greek dinos, whirling - they spin as they swim.'),
    'dysbiosis': (
        'A microbial community shifted away from the composition its host functions with. Defined by what it is not, because the healthy state is often uncharacterised.',
        'Greek dys (bad) plus biosis (way of life).'),
    'ECHA': (
        'The European Chemicals Agency, which runs REACH. Its compliance checks routinely find registration dossiers incomplete.',
        'Based in Helsinki. It evaluates what industry submits rather than testing independently.'),
    'ecotoxicology': (
        'The study of how chemicals affect organisms and ecosystems. In regulatory practice it usually means acute mortality tests on a few standard species.',
        'Ecology plus toxicology - a young field, and its standard methods predate most of what is now known about symbiosis.'),
    'eDNA': (
        'Environmental DNA - genetic material shed into water or sediment by whatever passed through. It lets you survey a community without catching anything.',
        'The method that most directly bypasses the problem of a form with the wrong columns on it.'),
    'eelgrass': (
        'A true flowering plant that lives fully submerged in the sea, forming meadows on soft bottoms. It roots in the sediment, needs light at the bed, and shelters everything else. Danish: alegras.',
        'Named for its long ribbon leaves. Zostera marina is the Danish species.'),
    'efflux pump': (
        'A protein that pushes unwanted molecules back out of a cell. Bacteria carry them for their own reasons and they confer resistance to many drugs as a side effect - which is why resistance can appear almost immediately.',
        'The machinery was already there. Selection only had to favour it.'),
    'endocrine disruption': (
        "Interference with an organism's hormone system, often at concentrations far below those that kill. Effects show as failed reproduction and altered development rather than as death.",
        'The endocrine system is the hormonal one - Greek endo (within) plus krinein (to separate).'),
    'endocrine disruptor': (
        'A substance that interferes with hormone systems, often at concentrations far below those that kill. Effects appear as failed reproduction and altered development rather than as death.',
        'One of the few grounds on which European approval is refused on hazard alone, without an exposure argument.'),
    'endogenous retrovirus': (
        'A virus that inserted itself into a host genome long ago and stayed, becoming inherited. Roughly eight per cent of human DNA is of this origin.',
        'One of them supplies the protein that builds the placenta - mammalian pregnancy depends on a domesticated virus.'),
    'endophyte': (
        "A fungus or bacterium living inside a plant's tissues without causing disease, often conferring resistance to pests or stress on its host.",
        'Greek endon (within) plus phyton (plant). Another partnership invisible to a survey that counts plants.'),
    'endosymbiosis': (
        'One organism living inside another, permanently. Mitochondria and chloroplasts are both captured free-living bacteria, so every plant and animal is a former merger.',
        'The origin of the eukaryotic cell, and the reason the boundary between organism and community is not sharp.'),
    'engraftment': (
        'Whether transplanted organisms actually establish and persist rather than being displaced. It varies enormously between donors and recipients, which is the practical problem with any transplant.',
        'The reason donor matching matters, in a gut and in a sediment alike.'),
    'epibenthic': (
        'Living on the surface of the seabed rather than buried in it.',
        'Epi- (upon) plus benthos.'),
    'epiphyte': (
        'A plant or alga growing on another plant, using it as a surface rather than feeding on it.',
        'Greek epi- (upon) plus phyton (plant). On eelgrass they shade the leaf they sit on.'),
    'EQR': (
        'Ecological quality ratio: the observed value divided by the value expected in an unimpacted reference state, scaled so that 1 is pristine.',
        'An EU device for making incomparable national measurements comparable. Its denominator is modelled, not measured.'),
    'erg': (
        'A sand sea - the dune-covered kind of desert, as opposed to stony or salt desert.',
        "Arabic 'irq, a dune field. What makes it hostile is that the surface moves, not that it is dry."),
    'error threshold': (
        'The mutation rate above which a lineage can no longer preserve its own information and collapses. RNA viruses sit just below it, which is the fastest possible search that still permits replication.',
        'Deliberately pushing a virus over it is a real antiviral strategy, called lethal mutagenesis.'),
    'essential use': (
        'A proposed rule that the most harmful substances should be permitted only where they are genuinely necessary and no substitute exists - rather than wherever the exposure looks acceptable.',
        'The concept borrowed from how antibiotics are managed, and the closest existing idea to reserving a chemical rather than banning it.'),
    'eukaryote': (
        'An organism whose cells keep their DNA in a nucleus - animals, plants, fungi, and the enormous majority of microbial diversity that is none of the three.',
        'Greek eu (well) plus karyon (kernel). Bacteria and archaea are the ones that do not.'),
    'eutrophic': (
        'Over-fed: a water body receiving more nutrient than it can process.',
        'Greek eu- (well) plus trophe (nourishment) - literally well-nourished, which is why the word sounds like praise and means the opposite.'),
    'eutrophication': (
        'Over-feeding of a water body: so much nutrient that production outruns what the system can process.',
        'Greek eu- (well) plus trophe (nourishment). Literally well-nourished, which is why the word sounds positive and means the opposite.'),
    'euxinic': (
        'Water that is both oxygen-free and carries free sulphide. The worst case.',
        'From Pontus Euxinus, the Roman name for the Black Sea, whose deep water has been like this throughout recorded history.'),
    'exopolymer': (
        'Sticky long-chain sugars secreted outside the cell. It binds sediment, forms marine gel, and is what makes water feel slippery.',
        'Exo- (outside) plus polymer. Marine biologists count it as TEP.'),
    'extremophile': (
        'An organism thriving in conditions that would kill most life - extremes of heat, salt, acidity, pressure or chemistry. The word records our own expectations rather than anything about the organism.',
        'To the organism the conditions are not extreme. They are simply where it lives.'),
    'faecal microbiota transplant': (
        'Treating a cleared gut by putting a whole functioning community back, without anyone needing to know which member does the work. Cure rates around ninety per cent.',
        'The same design as putting healthy sediment into failed sediment - proven in one domain and never tried in the other.'),
    'fedtemog': (
        'Danish, roughly fat-muck: the greasy, foul organic material that accumulates in the water and along the shore. Not a scientific term, and not measured by anything.',
        'Fedt is fat, mog is muck or dung. A word from people who swim, not from a monitoring programme.'),
    'Feltmåling': (
        'Danish for field measurement - the ODA category holding instrument profiles taken in the water: CTD casts, light attenuation, oxygen.',
        'Felt (field) plus måling (measurement).'),
    'Ferralsol': (
        'A deeply weathered tropical soil dominated by iron and aluminium oxides, which lock phosphate up so tightly that fertiliser vanishes from availability within weeks.',
        'Ferrum (iron) plus aluminium: named for what is left after everything else has weathered away.'),
    'flagellate': (
        'A single-celled organism that swims using a whip-like tail. In these waters they are the algae that take over when diatoms cannot grow, and they are poorly eaten.',
        'Latin flagellum, a whip.'),
    'flocculation': (
        'Fine particles and dissolved organic matter clumping together and settling out, which happens abruptly where fresh water meets salt.',
        'Latin floccus, a tuft of wool. What the clumps look like.'),
    'folk taxonomy': (
        'A classification based on how things look and what they do, rather than on how they are related. Plants, animals and fungi is one; it predates evolutionary biology and still organises most monitoring.',
        'Useful and intuitive, and it systematically hides organisms that fall between its categories.'),
    'foraminifera': (
        'Single-celled organisms that build tiny chambered shells. Abundant in sediment, and their shells preserve, which makes them a record of past conditions.',
        'Latin foramen (hole) plus ferre (to bear) - the shells are perforated.'),
    'founder effect': (
        'The outsized influence of whoever establishes a population first. Their descendants make up everything that follows, so what they happened to be matters more than what would have suited the place.',
        'After a crash the survivors are not a random sample - they are whoever tolerated the thing that did the killing, and then they have the place to themselves.'),
    'frustule': (
        'The two-part silica shell of a diatom.',
        'Latin frustulum, a little piece.'),
    'fungi': (
        'A kingdom of life separate from plants and animals, feeding by absorbing what they have digested outside themselves. On land they are the principal decomposers of tough material; in the sea they are barely studied.',
        'Latin fungus, mushroom - though most fungi never make anything you would recognise as one.'),
    'fungicide': (
        'A chemical designed to kill fungi. Applied in agriculture by the thousand tonnes, and acting on enzyme systems that fungi share with most other life.',
        'The -cide ending is Latin caedere, to kill - as in pesticide, biocide, herbicide.'),
    'gene duplication': (
        'A copy of a gene arising, leaving one to keep doing the original job while the other is free to change. The main route by which genuinely new functions appear.',
        'It is why what already exists constrains what can evolve next.'),
    'generation time': (
        'How long between one generation and the next. It sets the ceiling on how fast a population can adapt, and it differs between a marine bacterium and an eelgrass meadow by roughly five orders of magnitude.',
        'The single most important number in deciding who wins under a novel pressure.'),
    'glyphosate': (
        "The world's most used herbicide. Its target enzyme is absent in animals but present in plants, bacteria and fungi, which makes it an antimicrobial as well as a weedkiller.",
        'From glycine and phosphonate, its chemical parts.'),
    'grab': (
        'A sampling device dropped to the seabed that bites out a fixed area of sediment and brings it up. One grab is one sample, and it is how nearly all seabed fauna data is collected.',
        'It grabs. The fixed area is what makes counts comparable.'),
    'grandfathered': (
        'Permitted to continue under old rules because it was already in use when new rules arrived. Most industrial chemicals in Europe entered the system this way.',
        'From American voting law of the 1890s, where a grandfather clause exempted people whose grandfathers had voted - the origin is not a happy one.'),
    'Great Oxidation Event': (
        'The point around 2.4 billion years ago when oxygen produced by cyanobacteria accumulated in the atmosphere, poisoning most of the biosphere that had produced it and making all later aerobic life possible.',
        'The largest mass extinction there has ever been, caused by a waste product. It is also the clearest case of adapted survivors remaking the conditions for everything after them.'),
    'griseofulvin': (
        'An antifungal drug made by a Penicillium mould to kill other fungi.',
        "One fungus's weapon against its relatives, borrowed for human medicine."),
    'hazard': (
        'The intrinsic capacity of something to cause harm, independent of whether anyone is exposed to it. A shark in an aquarium is a hazard; a shark in your bath is a risk.',
        'Kept strictly separate from risk in regulatory language, and routinely conflated everywhere else.'),
    'Hedley fractionation': (
        'A sequence of chemical extractions that separates soil phosphorus into pools by how easily it can be released - from immediately available to permanently locked away.',
        'The standard soil-science method, and the reason soil scientists never quote total phosphorus alone.'),
    'helminth': (
        'A parasitic worm. Their removal from human populations is implicated in immune dysregulation, which is the standard cautionary case for eliminating an organism whose full role was unknown.',
        'Greek helmins, worm.'),
    'heterotroph': (
        'An organism that gets its carbon by consuming organic matter made by something else. All animals and fungi, and most bacteria.',
        'Greek heteros (other): fed by others.'),
    'holobiont': (
        'An organism considered together with all the microbes living in and on it, as one functioning unit - because for many purposes that is what it actually is.',
        'Greek holos (whole) plus bios. A word that exists because the older picture of an organism turned out to be incomplete.'),
    'horizontal gene transfer': (
        'Genes moving sideways between unrelated organisms rather than down from parent to offspring. Bacteria do it routinely, which is why a resistance evolved once can appear everywhere.',
        'The reason prokaryotic adaptation is not limited by the lineage that happened to invent it. Eukaryotes have almost no equivalent.'),
    'humus': (
        'The dark, stable remains of decayed organic matter in soil, after everything easily eaten has gone.',
        'Latin humus, ground or earth - the same root as human and humble.'),
    'hydrogeology': (
        'The study of how water moves through rock and soil underground. Nitrogen retention is a hydrogeological quantity as much as a biological one.',
        'Water plus geology.'),
    'hydrophobic': (
        'Water-repelling. Such substances leave the water and gather at surfaces - which is why they concentrate in the microlayer and in fatty tissue.',
        'Greek hydor (water) plus phobos (fear).'),
    'hydrothermal vent': (
        'A seafloor hot spring where water heated by rock emerges carrying hydrogen sulphide and metals. The communities around them run entirely on chemical energy, with no sunlight anywhere in the food chain.',
        'Discovered in 1977, which overturned the assumption that all life ultimately depends on the sun.'),
    'hypovirulence': (
        'A pathogen made less harmful, usually by its own infection with something else. The basis of using a virus to control a fungal disease of plants.',
        'Not killing the pathogen but taking its weapons away.'),
    'hypoxia': (
        'Not enough oxygen. Conventionally below 4 mg per litre in marine work, with 2 mg/l as severe.',
        'Greek hypo- (under) plus oxys, the root in oxygen.'),
    'hysteresis': (
        'A system that does not retrace its path: the conditions that would restore it are not the conditions that broke it. Easy to enter, hard to leave.',
        'Greek hysteresis, a shortcoming or lagging behind.'),
    'idempotent': (
        'Doing it again changes nothing. A niche is either occupied or it is not, so there is no dose to escalate and no gradient for anything to adapt along.',
        'Borrowed from mathematics and computing, and unusually apt: it names exactly what distinguishes exclusion from a chemical weapon.'),
    'iltsvind': (
        'Danish for oxygen depletion - literally oxygen-dwindling. The word used in Danish public debate for what happens when the seabed suffocates.',
        'Ilt is Danish for oxygen, coined by H.C. Orsted from ild, fire.'),
    'immobilisation': (
        'The opposite of mineralisation: microbes taking dissolved nutrient out of the water or soil to build their own bodies. High-carbon, low-nitrogen material causes it.',
        'The nutrient is not destroyed, just made unavailable while it sits inside a bacterium.'),
    'in situ': (
        'In place - an experiment or measurement made where the thing actually lives, rather than in a laboratory.',
        'Latin, literally in position.'),
    'indsatsbehov': (
        'Danish for the required effort - the calculated size of the reduction a water body needs to reach its target. The central number of the whole nitrogen policy.',
        'Indsats (effort, intervention) plus behov (need).'),
    'infauna': (
        'Animals living inside the sediment rather than on top of it - worms, clams, the things a grab sample catches.',
        'Latin in- plus fauna. The ones you have to dig for.'),
    'innate immunity': (
        'The defence system built in advance to recognise general signatures of infection, as against the adaptive system that learns individual ones. Plants and invertebrates have only this - and much of it turns out to be homologous to bacterial anti-phage machinery.',
        'Which makes part of our own immune system a captured weapon from the microbial war.'),
    'inoculum': (
        'A small quantity of living material introduced deliberately to establish a community - a spoonful of healthy sediment, a starter culture.',
        'Latin inoculare, to graft in. The plural is inocula.'),
    'invertebrate': (
        'An animal without a backbone - worms, molluscs, crustaceans, insects. The overwhelming majority of animal species, and nearly everything on a seabed.',
        'Latin in- (not) plus vertebra. Defined by what it lacks, which tells you who wrote the category.'),
    'IoT': (
        'Internet of things - cheap networked devices that report readings without anyone visiting them. In an environmental context the appeal is replication rather than precision.',
        'For testing whether one station can represent an area, forty rough sensors beat one perfect one, because the question is about variance.'),
    'isotherm': (
        "A curve showing how much of a substance a material will hold at each concentration, measured at one temperature. The standard way to describe a soil's capacity to hold phosphate.",
        'Greek isos (equal) plus therme (heat) - the temperature is held constant.'),
    'Kd': (
        'The light attenuation coefficient: how fast light dies away with depth. Higher Kd means darker at the bottom.',
        'One broadband number standing in for a whole spectrum, which is why its cause cannot be read off it.'),
    'kill the winner': (
        'The model in which whichever organism is most abundant is the easiest target for its own specific virus, so cropping falls hardest on the winner and diversity is maintained by predation rather than by competition.',
        'It makes viruses a structuring force rather than only a destructive one.'),
    'klapplads': (
        'Danish for a licensed site where dredged material is dumped at sea. There are 114 of them.',
        'Klappe, to tip or dump; plads, place.'),
    'Krebs cycle': (
        'The central loop of metabolism, by which cells extract energy from food. Present in essentially all aerobic life.',
        'Hans Krebs, 1937. Also called the citric acid cycle, after the first compound in it.'),
    'labile': (
        'Easily and quickly broken down. Sugars and fresh algal material are labile.',
        'Latin labilis, liable to slip or fall. Its opposite here is recalcitrant.'),
    'Labyrinthula': (
        'The slime-mould-like organism that causes eelgrass wasting disease. It destroyed most Atlantic eelgrass in the 1930s and is still present.',
        'Named for the labyrinth of tracks its cells glide along.'),
    'labyrinthulid': (
        'A group of marine organisms that glide along self-made slime tracks and decompose organic matter - and include the one that causes eelgrass wasting disease. Neither fungi nor animals nor plants.',
        'Named for the labyrinth of tracks their cells move along. Barely studied, and almost certainly under-appreciated.'),
    'Leptosol': (
        'A very shallow soil, under about 25 cm to rock. Almost no capacity to buffer anything.',
        'Greek leptos, thin.'),
    'lethal mutagenesis': (
        'Pushing a virus above its error threshold on purpose, so that it mutates itself out of existence. It works because the strategy that makes RNA viruses fast is also the thing that can be turned against them.',
        'One of the few antiviral approaches that a pathogen cannot straightforwardly evolve around.'),
    'Liebig': (
        'The law of the minimum: growth is set by whichever necessary thing is scarcest, not by the total of everything supplied. Ten nutrients in surplus and one missing gives you no growth.',
        'Justus von Liebig, the 19th-century chemist who argued it for crops. The name carries none of the meaning, which is why it is worth spelling out.'),
    'lignin': (
        'The rigid material that makes wood woody. It is the hardest common biological molecule to break down, and mainly fungi do it.',
        'Latin lignum, wood. Nitrogen enrichment suppresses the enzymes that degrade it, which is why it accumulates.'),
    'local adaptation': (
        'A population fitted to the specific conditions it has lived in, often over very many generations. It is why a transplanted community is at a disadvantage against residents on their own ground.',
        'And why a donor community has to come from a matched setting, or the survivors it must displace simply win.'),
    'lucinid': (
        'A family of clams that host sulphide-oxidising bacteria in their gills. In seagrass beds they keep the root zone habitable.',
        'The three-way partnership of plant, clam and bacterium was only described in 2012.'),
    'Lysprocent': (
        'Danish for light percentage - the share of surface light still present at a given depth, already computed in the ODA record. Eelgrass needs roughly 11 to 14 percent.',
        'Lys (light) plus procent. It is the number the eelgrass requirement is written in.'),
    'macroalgae': (
        'Seaweed - algae large enough to see, attached to rock or shell rather than drifting.',
        'Macro, large, as against the microscopic plankton.'),
    'macrofauna': (
        'The animals big enough to be caught on a one-millimetre sieve - worms, clams, crustaceans. What a seabed sample is counted as.',
        'Macro, large. Below them are meiofauna, below those, microbes.'),
    'MARPOL': (
        'The international convention governing pollution from ships. It sets what a vessel may legally discharge at sea - sewage, greywater, food waste, scrubber washwater - and where.',
        'MARine POLlution, contracted. Compliance is the baseline, not the absence of discharge.'),
    'meiofauna': (
        'The very small animals between sand grains - nematodes and tiny crustaceans. Too big to be microbes, too small for the sieves used on macrofauna.',
        'Greek meion, smaller.'),
    'mesocosm': (
        'An experimental container big enough to hold a working piece of an ecosystem, but small enough to control - a tank, an enclosure, a bag in the sea.',
        'Greek mesos (middle) plus kosmos (world): between a test tube and the real thing.'),
    'mesozooplankton': (
        'The middle size class of drifting animals, chiefly copepods - between a fifth of a millimetre and two centimetres. The link between algae and fish.',
        'Greek mesos, middle.'),
    'metabarcoding': (
        'Sequencing DNA from a bulk sample to list what organisms are present, without anyone having to identify them by eye. Taxonomically agnostic by construction, which is exactly why it finds things the categories missed.',
        'Barcoding is identifying one specimen by a short DNA sequence; meta- is doing it to a whole community at once.'),
    'microbiome': (
        'The community of microbes living in and on an organism, which for many purposes is part of that organism - performing digestion, defence and nutrition it cannot perform alone.',
        'Micro plus biome. A word that exists because the older picture of an individual organism turned out to be incomplete.'),
    'microlayer': (
        'The top few micrometres of the sea, which concentrate surfactants, fats and hydrophobic pollutants far above their concentration in the bulk water.',
        "It is the layer a swimmer's skin actually passes through."),
    'micronutrient': (
        'An element needed in tiny amounts but needed absolutely - iron, zinc, copper, cobalt, molybdenum, selenium. Absence is as fatal as absence of nitrogen.',
        'As against macronutrients: carbon, nitrogen, phosphorus, and the rest needed in bulk.'),
    'microphytobenthos': (
        'Microscopic algae living on the sediment surface. Their secreted polymer glues the grains together and raises the current needed to erode the bed.',
        'Micro (small) plus phyton (plant) plus benthos (the depths): the tiny plants of the bottom.'),
    'mineralisation': (
        'The breakdown of organic material back into simple inorganic compounds - releasing the nutrients that were locked in tissue.',
        'Turning organic matter back into minerals. Remineralisation is the same word for material that was mineral to start with.'),
    'mitochondria': (
        'The compartments in which eukaryotic cells carry out respiration. Descended from captured bacteria, and present in fungi, plants and animals alike - which is why respiratory poisons are rarely selective.',
        'Greek mitos (thread) plus chondros (grain), from how they look under a microscope.'),
    'mor': (
        'Raw, matted, unincorporated humus sitting on top of the soil because the fauna that would mix it in are absent or excluded.',
        'Also from Danish, meaning mould in the other sense. The terrestrial version of an organic mat on the seabed.'),
    'mucus layer': (
        'The gel coating animal surfaces exposed to the outside. It is enriched in bacteriophage, which attack incoming bacteria - a defence delivered by something classified as a parasite.',
        'Which is the pathogen-and-partner distinction failing again, in the place a body meets the world.'),
    'mull': (
        'Humus that soil animals have worked into the mineral soil - crumbly, fast-cycling, well mixed.',
        'From Danish and German muld, mould or loose earth. Its degraded counterpart is mor.'),
    'mutation rate': (
        'How often the genetic code changes when it is copied. Combined with population size it sets how much variation a lineage generates per unit time, and therefore how quickly it can meet something new.',
        'A large population with a short generation explores more possibilities in a year than a small slow one does in a century.'),
    'mutational bias': (
        'The fact that mutation is not uniform across a genome. Rates vary with chromatin state, transcription and sequence context; stress induces mutagenesis; recombination concentrates at hotspots.',
        'Variation is structured, and the structure is itself an evolved product of what the lineage has met before - which is priming, one level down.'),
    'mutualism': (
        'A relationship in which both partners benefit. The word English lacks is a common antonym for pathogen - we named the harmful relationships and left the rest to be called symbionts, which technically covers all of them.',
        'The vocabulary itself is biased toward harm, which is worth noticing when reading any list of species.'),
    'mycobiome': (
        'The fungal community of a place or a host, as distinct from its bacteria. Marine sediments are turning out to hold far more fungal diversity than anyone expected.',
        'Myco (fungus) on the pattern of microbiome. The word is recent because the recognition is recent.'),
    'mycoparasitism': (
        'A fungus parasitising another fungus. It is how Trichoderma protects crops, and it is the fungal diagonal of the same matrix.',
        'Fungi against fungi, sold in a bag.'),
    'mycorrhiza': (
        'The partnership between plant roots and fungi that feeds the plant phosphorus in exchange for carbon. Heavy fertilising suppresses it.',
        'Greek mykes (fungus) plus rhiza (root).'),
    'mycovirus': (
        'A virus that infects fungi. Some weaken their host rather than killing it, and one that weakens chestnut blight is a deployed biocontrol agent - a virus protecting a tree by disarming a fungus.',
        'Antifungals of viral variety, and a working demonstration that the whole matrix is real.'),
    'målbelastning': (
        'Danish for target load - how much nitrogen a water body may receive and still meet its environmental objective.',
        'Mål (target) plus belastning (load).'),
    'natural experiment': (
        'A change imposed by circumstance rather than by a researcher, which happens to create a comparison. Dated construction works, staggered policy adoption and closures all qualify.',
        'The nearest thing to an experiment available when the system is too large to manipulate on purpose.'),
    'necromass': (
        'Dead biomass. In soil, dead microbes themselves make up a large share of the lasting organic matter.',
        'Greek nekros, corpse.'),
    'nematode': (
        'A roundworm. In sediment they are microscopic, enormously abundant, and among the last animals left when conditions get bad.',
        'Greek nema, thread.'),
    'neonicotinoid': (
        'The most widely used insecticide class. It acts on acetylcholine receptors, which every animal with a nervous system has, including all marine invertebrates.',
        'Nicotine-like, and acting at the same receptor nicotine does.'),
    'nitrate': (
        'The oxidised, stable form of dissolved nitrogen, and the form that leaches from farmland into groundwater and streams.',
        'Same root as nitre, saltpetre.'),
    'nitrification': (
        'Bacteria oxidising ammonium to nitrate. It consumes oxygen - 4.57 grams per gram of nitrogen - without anything growing.',
        'From nitre, saltpetre, the old name for nitrate salts.'),
    'nitrogenase': (
        'The enzyme that lets some bacteria pull nitrogen straight out of the air. It requires molybdenum or vanadium, and it is destroyed by oxygen.',
        'The -ase ending marks an enzyme throughout biochemistry.'),
    'NOVANA': (
        "Denmark's national programme for monitoring water and nature. Almost every Danish environmental number ultimately comes from it.",
        'Danish acronym: the national programme for monitoring of the aquatic environment and nature.'),
    'occlusion': (
        'Sorbed material becoming physically enclosed inside a mineral, so it can no longer be released at all. The one-way end of sorption.',
        'Latin occludere, to shut up or close off.'),
    'oligotrophic': (
        'Nutrient-poor, low production, usually clear water.',
        'Greek oligos, few. The other end of the same scale as eutrophic.'),
    'oomycete': (
        'A fungus-like group including Pythium and Phytophthora - water moulds that swim as spores and attack stressed roots. They are not actually fungi despite living like them.',
        'Greek oon (egg) plus mykes (fungus).'),
    'opisthokont': (
        'The branch containing animals and fungi together. They are sister lineages: a mushroom is a closer relative of yours than of a plant.',
        'Greek opisthen (behind) plus kontos (pole), after the single rear-facing tail on a sperm cell and a fungal spore alike.'),
    'optode': (
        "An oxygen sensor that measures how a dye's glow is quenched by oxygen. It replaced chemical titration, and the two do not always agree.",
        'Optical electrode.'),
    'overløb': (
        'Danish for a sewer overflow - untreated sewage discharged directly when rain overwhelms a combined system.',
        'Over plus løb (run). Denmark has 19,665 registered outfall points.'),
    'parasitism': (
        "A relationship in which one partner benefits at the other's expense. The same organism can be a parasite in one host or one condition and harmless in another.",
        "Greek parasitos, one who eats beside another - originally a hanger-on at somebody else's dinner."),
    'pathobiont': (
        'A resident organism that is harmless most of the time and becomes harmful when conditions change - the host is stressed, the community shifts, a barrier fails.',
        'The word exists because the pathogen and non-pathogen categories could not hold.'),
    'PBT': (
        'Persistent, Bioaccumulative and Toxic - the three-part test that gets a substance refused outright in some European approvals, with no exposure argument allowed to rescue it.',
        'vPvB is the stronger version: very Persistent and very Bioaccumulative, where persistence alone carries the case.'),
    'PE': (
        "Population equivalent - the standard unit of sewage load, one person's daily contribution. Industrial discharges are expressed in how many people they equal.",
        'Lets a dairy and a town be added together.'),
    'pelagic': (
        'Of the open water column, as opposed to the bed.',
        'Greek pelagos, the open sea. Its counterpart is benthic.'),
    'peroxidase': (
        'An enzyme that neutralises reactive oxygen inside a cell. The selenium-dependent version is why selenium is essential.',
        'It disposes of peroxides, which would otherwise do damage.'),
    'phage therapy': (
        'Treating a bacterial infection with the viruses that attack that bacterium. Used clinically in Georgia and Poland for decades and being revived against resistant infections.',
        'Antibacterials of viral variety - the matrix of microbial warfare filled in from a direction Western medicine largely skipped.'),
    'pharmacokinetic': (
        'To do with how much of a substance an organism takes up, where it goes, and how fast it is broken down - as opposed to what it does once it arrives.',
        'Greek pharmakon (drug) plus kinesis (movement). Selectivity that is pharmacokinetic is selectivity of exposure, not of mechanism.'),
    'phenology': (
        'The timing of biological events through the year - when things spawn, bloom, migrate - and whether two events that need to coincide still do.',
        'Greek phainein, to appear. The study of when things show up.'),
    'phosphate': (
        'The dissolved form of phosphorus. It binds tightly to iron oxides in oxygenated sediment and is released again when the sediment loses its oxygen.',
        'That release is the single strongest feedback loop in a eutrophic system.'),
    'photoinhibition': (
        'Too much light damaging the photosynthetic machinery. The ceiling of the light window.',
        'Light doing the inhibiting - the reason clearest is not always best.'),
    'photosynthesis': (
        'Building organic matter from carbon dioxide using light, releasing oxygen. Respiration is the same reaction run backwards, which is why the two gases move in opposite directions.',
        'Greek phos (light) plus synthesis (putting together).'),
    'photosystem II': (
        'The protein complex that splits water and starts photosynthesis. Triazine and urea herbicides block it, which makes them equally effective against algae.',
        'The second of two photosystems, named in the order they were discovered rather than the order they act.'),
    'Phytophthora': (
        'A genus of water mould that destroys plant roots. The potato blight that caused the Irish famine was one of these.',
        'Greek: literally the plant-destroyer.'),
    'phytoplankton': (
        'The drifting microscopic plants of the water column - diatoms, flagellates, cyanobacteria. Everything else in the sea ultimately eats them or eats something that did.',
        'Greek phyton (plant) plus planktos (wandering, drifting).'),
    'phytotoxin': (
        'A substance that poisons plants. Waterlogged ground makes several of its own - organic acids, ethylene, sulphide, and reduced iron and manganese.',
        'Greek phyton (plant) plus toxikon (poison).'),
    'picomolar': (
        'A concentration of one trillionth of a mole per litre. Vitamins and some trace metals matter to marine life at concentrations this small.',
        'The prefix pico means a trillionth.'),
    'picoplankton': (
        'The smallest plankton, under two thousandths of a millimetre. Too small for most grazers to catch, so what eats them is mostly viruses.',
        'Pico, a trillionth - here just meaning very small indeed.'),
    'plankton': (
        'Anything living in the water column that drifts rather than swims against the current, from bacteria to jellyfish.',
        'Greek planktos, wandering. It describes a way of life, not a group of relatives.'),
    'polychaete': (
        'A marine bristle worm. Many build tubes that stabilise sediment; others burrow and mix it. A large share of what a seabed sample contains.',
        'Greek poly (many) plus chaite (hair).'),
    'polymerase': (
        "The enzyme that copies genetic material. How accurately it does so sets a lineage's mutation rate, and therefore which of the two adaptive strategies is available to it.",
        'From polymer plus -ase, the enzyme ending.'),
    'porewater': (
        'The water in the spaces between sediment grains. Its chemistry is often wholly different from the water above, and it is what a buried animal actually lives in.',
        'The pores of the sediment.'),
    'precautionary principle': (
        'The idea that action to prevent harm need not wait for full scientific certainty. Written into EU law, and constrained in practice by requirements of proportionality.',
        'Article 191 of the Treaty on the Functioning of the European Union. Invoked more often than it decides anything.'),
    'priming': (
        'Having machinery already close to what a new situation requires. New biological capabilities almost never arise from nothing - they arise by duplicating and modifying something that already worked - so the distance from existing machinery to the needed function matters more than the supply of mutations.',
        'Antibiotic resistance appeared in years because soil bacteria had competed with antibiotic-making fungi for hundreds of millions of years, so efflux pumps and degrading enzymes were already in the shared gene pool. Nylon-oligomer digestion appeared within decades of nylon existing, on an entirely synthetic substrate, because amide hydrolysis is ordinary chemistry that everything already does.'),
    'priority effect': (
        'Arriving first being worth more than being well suited. It means the composition of a recovered community records its history as much as its conditions.',
        'The reason a degraded state can persist after the conditions that caused it have gone, with no other mechanism required.'),
    'probiotic': (
        'A live organism given deliberately to establish or restore a community. Used in aquaculture in place of antibiotics for the same reason it works in a gut.',
        'Literally for-life, coined against antibiotic, against-life.'),
    'prokaryote': (
        'An organism whose cell has no nucleus - bacteria and archaea. They run essentially every chemical transformation in the sea that is not photosynthesis or animal respiration.',
        'Greek pro (before) plus karyon (kernel): named for lacking the thing eukaryotes have, which tells you who was doing the naming.'),
    'proofreading': (
        'The error-correcting step a polymerase performs while copying genetic material. RNA viruses mostly lack it, which is why they mutate orders of magnitude faster than anything cellular.',
        'The absence is not a defect. It is what makes their strategy possible.'),
    'propagule': (
        'Whatever a species uses to start a new individual somewhere else - a larva, a seed, a spore, a fragment.',
        'Latin propagare, to propagate. The unit of arrival.'),
    'protist': (
        'A catch-all for single-celled organisms with a nucleus that are not animals, plants or fungi. Includes most marine algae and many parasites.',
        'Greek protos, first.'),
    'pycnocline': (
        'The depth at which density changes sharply, separating lighter water above from denser water below. It acts as a lid: below it, oxygen is not replaced.',
        'Greek pyknos (dense) plus klinein (to slope).'),
    'pyrethroid': (
        'A synthetic insecticide acting on voltage-gated sodium channels - universal in animals. Crustaceans are extremely sensitive, being arthropods like the intended targets.',
        'Modelled on pyrethrins from chrysanthemum flowers.'),
    'Pythium': (
        'A water mould that rots seedlings and roots, thriving where soil or sediment is waterlogged and low in oxygen.',
        'The classic damping-off disease of a wet greenhouse.'),
    'Q10': (
        'How much faster a biological process runs for every ten degrees of warming. Around two for most decay, meaning respiration roughly doubles.',
        'A rule of thumb old enough to have no better name.'),
    'quasispecies': (
        'A population that exists as a cloud of related variants rather than as a defined genotype, because it mutates faster than selection can purify it. Selection then acts on the cloud rather than on any individual sequence.',
        'The normal condition for RNA viruses, and the reason a virus is better thought of as a distribution than as a thing.'),
    'r-selected': (
        'Organisms that bet on speed and numbers - short lives, fast growth, many offspring, few requirements. They dominate disturbed and unstable conditions.',
        'From r, the growth-rate term in the population equation. Its counterpart is K-selected: slow, large, long-lived, competitive in stable conditions.'),
    'radial oxygen loss': (
        'Rooted plants leaking oxygen from their roots into the sediment, which keeps sulphide away from the root. It is powered by photosynthesis, so shade shuts it off.',
        'Radial because it moves outward from the root, not along it.'),
    'REACH': (
        "The EU regulation governing industrial chemicals. Its slogan is 'no data, no market' - the duty to supply safety data sits with whoever wants to sell the substance.",
        'Registration, Evaluation, Authorisation and restriction of CHemicals. The data required scales with tonnage, so small-volume substances are barely characterised.'),
    'recalcitrant': (
        'Resistant to decay. Lignin, humic material, and most synthetic compounds.',
        'Latin recalcitrare, to kick back - literally to dig the heels in.'),
    'recombination': (
        'The shuffling of genetic material during sexual reproduction. It concentrates at particular locations rather than falling evenly, and mate choice ahead of it is under selection - so none of it is a lottery.',
        'The popular picture of random variation is wrong at every stage of this.'),
    'Redfield': (
        'The roughly fixed ratio of carbon to nitrogen to phosphorus in marine plankton, about 106:16:1 by atoms. It lets you convert one nutrient into an expected amount of biomass, or of oxygen demand.',
        'Alfred Redfield noticed in 1934 that plankton and seawater share the ratio, which is either a coincidence or the plankton setting the chemistry of the ocean.'),
    'redox': (
        'Whether the chemistry of a place is oxidising or reducing - broadly, whether oxygen is available. It governs which reactions run and which metals stay put.',
        'Contraction of reduction-oxidation.'),
    'reductase': (
        'An enzyme that reduces a compound - adds electrons to it. Nitrate reductase is the one that lets an organism use nitrate.',
        'Also an enzyme, named for what it does.'),
    'remineralisation': (
        'Decay: organic matter broken back down to its dissolved inorganic constituents, releasing the nutrients and consuming oxygen.',
        'Turning organic material back into minerals.'),
    'replication': (
        'Taking more than one measurement of the same thing, so that variability can be told apart from difference. Without it, one sample is indistinguishable from a whole area.',
        'The single most common thing missing from environmental monitoring designs.'),
    'residual estimator': (
        'A quantity computed as whatever is left after subtracting everything you did model from a measured total. It is never itself measured, and it absorbs every error in every other term.',
        'Which is why such a figure can come out negative, and why a negative one is the method reporting its own error bars.'),
    'resistance': (
        'The evolved ability to survive a dose that would once have been lethal. Its appearance is simultaneously evidence that the organism was exposed and that the exposure was selecting.',
        'The same phenomenon in bacteria facing antibiotics, fungi facing fungicides, and weeds facing herbicides - and for the same reason.'),
    'respiration': (
        'Extracting energy from organic matter, consuming oxygen and releasing carbon dioxide. The reverse of photosynthesis, and what decay is at the chemical level.',
        'The reason every corpse relieves a carbon shortage and deepens an oxygen one.'),
    'restriction enzyme': (
        'A bacterial protein that cuts foreign DNA at a specific sequence, defending against phage. Its discovery made molecular biology possible.',
        'The other great tool taken off the same battlefield.'),
    'resuspension': (
        'Sediment lifted back into the water by waves, currents or gear, after having settled.',
        'It returns buried material, and its chemistry, to circulation.'),
    'retention': (
        'The share of nitrogen applied on land that never reaches the sea, because it is taken up, denitrified or stored on the way. The largest single number in the whole account, and one its own producers say cannot be measured directly.',
        'Latin retinere, to hold back. It is a modelled quantity presented as a map.'),
    'return interval': (
        'How long between one disturbance and the next. Compared against how long recovery takes, it decides whether a system persists in an early state permanently or reaches maturity between hits.',
        'The number that matters for trawling, and the one an annual effort figure cannot express.'),
    'rhizosphere': (
        'The thin zone of soil or sediment immediately around a root, chemically and biologically quite unlike the bulk material a few millimetres away.',
        'Greek rhiza (root) plus sphaira. Where the plant and the microbial world actually meet.'),
    'råstof': (
        'Danish for raw material - here, licensed extraction of sand and gravel from the seabed. 305 areas are designated.',
        'Rå (raw) plus stof (substance).'),
    'salinity': (
        'How much salt is dissolved in water. Open ocean is about 35 grams per kilogram; the Baltic is a fraction of that.',
        'The gradient through Danish waters is one of the sharpest anywhere.'),
    'salting-out': (
        'Substances becoming less soluble as salinity rises, so they come out of solution into films, droplets and aggregates.',
        'Adding salt pushes things out of the water. It is why fats behave differently in the sea than in a lake.'),
    'saprotroph': (
        'An organism that feeds on dead material, breaking it down. Most fungi are saprotrophs, and they handle the tough fractions bacteria leave behind.',
        'Greek sapros (rotten) plus trophe (nourishment).'),
    'SDHI': (
        'A fungicide class blocking succinate dehydrogenase, which is simultaneously complex II of the respiratory chain and a step in the Krebs cycle. Conserved wherever there are mitochondria.',
        'Succinate dehydrogenase inhibitor. The target does two jobs, so blocking it stops two processes.'),
    'seagrass': (
        "A true flowering plant that lives submerged in the sea, rooted in sediment - not a seaweed. Eelgrass is Denmark's species.",
        'Grass-like in appearance only; it is more closely related to lilies than to grass.'),
    'Secchi': (
        'The oldest instrument in oceanography: a white disc lowered until it disappears. The depth at which it vanishes is a measure of water clarity, and the record goes back over a century.',
        'Angelo Secchi, papal astronomer, 1865. Still in use because it is simple and comparable.'),
    'sediment sickness': (
        'Ground in which a plant will not grow although the chemistry looks adequate, because of accumulated pathogens, lost symbionts, or autotoxic residues.',
        'Horticulture calls the same thing replant disease and tests it by swapping the soil.'),
    'sedimentation': (
        'Particles settling out of the water onto the bed.',
        'The opposite process to resuspension, and the two together decide what the bed is made of.'),
    'Sedimentkemi': (
        'Danish for sediment chemistry - the ODA category holding what has been measured in the bed itself, as opposed to the water above it.',
        'The category this project repeatedly finds nearly empty of the analytes that matter.'),
    'selection pressure': (
        "Any condition that kills or hinders some individuals more than others, so that the survivors' traits become more common. Applying a biocide is applying one deliberately.",
        'A dose too low to kill outright is not neutral - it is the regime in which selection is strongest, because it kills enough to matter and spares enough to breed.'),
    'self-amplifying': (
        'A feedback where the effect makes its own cause stronger. Oxygen depletion is one: the casualties decay, the decay consumes more oxygen.',
        'Also called positive feedback, which is misleading because nothing about it is good.'),
    'self-correcting': (
        'A feedback where the effect undoes its own cause. Carbon dioxide depletion is one: whatever dies of it decays and puts the carbon back.',
        'Also called negative feedback. The two words are about direction, not about desirability.'),
    'Shelford': (
        'The law of tolerance: every requirement has a ceiling as well as a floor. Too much of a needed thing kills as surely as too little.',
        'Victor Shelford, an American ecologist, 1913. Liebig gives you the floor; Shelford gives you the roof.'),
    'shikimate': (
        'A biochemical pathway that makes aromatic amino acids. Plants, bacteria and fungi have it; animals do not, and must eat those amino acids instead.',
        'Named after shikimi, the Japanese star anise from which the acid was first isolated.'),
    'silicate': (
        'Dissolved silicon. Diatoms need it to build their shells, and it comes only from rock weathering, so human activity raises nitrogen and phosphorus but never this.',
        'The changing ratio is why diatoms give way to flagellates.'),
    'sill': (
        'An underwater ridge across the mouth of a basin. Water below the sill depth cannot flow out or be replaced from the side, so it stagnates.',
        'The same word as a door sill - a threshold you have to get over.'),
    'sonde': (
        'An instrument lowered into water to record conditions as it descends. The record names which sonde was used, which is what makes instrument changes testable.',
        'French sonde, a sounding line - the rope with a weight that measured depth before electronics.'),
    'sorption': (
        'A substance sticking to a solid surface, covering both adsorption onto it and absorption into it. Phosphate sorbs to iron oxides, which is how soil holds it.',
        'The umbrella term when you do not want to commit to which of the two is happening.'),
    'speciation': (
        'In chemistry, which chemical form an element is in - dissolved, bound to a particle, complexed with an organic molecule. Toxicity and availability both depend on it, and a total measurement hides it.',
        'Nothing to do with the biological sense of new species arising.'),
    'stepped wedge': (
        'A trial design in which every participant eventually receives the treatment, but the order is randomised. Each is its own control before crossover, and a control for the others after.',
        'It makes a randomised comparison possible where withholding the treatment from anyone would be politically or ethically impossible.'),
    'sterol': (
        'A class of molecules that stiffen cell membranes - cholesterol in animals, ergosterol in fungi, phytosterols in plants. Every eukaryote makes one, by broadly the same route.',
        'Which is why azole fungicides, which block that route, cannot be selective for fungi in principle.'),
    'stoichiometry': (
        'The fixed proportions in which substances combine, and so how much of one thing a given amount of another can produce or consume.',
        'Greek stoicheion (element) plus metron (measure).'),
    'stramenopile': (
        'A major branch of the eukaryotic tree containing diatoms, brown algae and kelp, oomycetes and labyrinthulids. Its members look like plants, fungi and moulds respectively, and are none of those things.',
        'Latin stramen (straw) plus pilus (hair), after the fine hairs on one of their two swimming tails. Also called heterokonts, for the same reason.'),
    'stratification': (
        'Water settled into layers that do not mix, because the upper water is warmer or fresher and therefore lighter.',
        'Latin stratum, a layer. It is what makes deep water run out of oxygen.'),
    'stressor': (
        'Anything that pushes an organism or system away from the conditions it functions in. The ecological term of art for a cause of harm.',
        'Borrowed from physiology, where it means the same and was equally vague.'),
    'strobilurin': (
        'A major fungicide class that blocks complex III of the mitochondrial respiratory chain - the machinery by which anything with mitochondria breathes.',
        'Derived from a compound made by the fungus Strobilurus, which uses it against its competitors.'),
    'sublethal': (
        'An effect that does not kill: impaired growth, reproduction, behaviour or immunity. Standard toxicity testing measures death, so sublethal harm is systematically under-recorded.',
        'Below the lethal dose. The organism is counted as a survivor.'),
    'sulphate': (
        'The dissolved sulphur compound that makes up a large part of sea salt. Harmless in itself, and the raw material bacteria turn into sulphide once oxygen is gone.',
        'Seawater holds about 2.7 grams per litre; fresh water holds a hundredth of that.'),
    'sulphide': (
        'The chemical made when bacteria breathe sulphate instead of oxygen. It smells of rotten eggs, is toxic to almost everything, and consumes oxygen the moment it meets any.',
        'Seawater carries so much sulphate that once oxygen runs out, sulphide production is effectively unlimited.'),
    'sulphidic': (
        'Containing free sulphide. A sulphidic sediment is one where sulphate reduction has taken over and the bed has turned toxic.',
        'The condition that follows anoxia in salt water, and does not follow it in fresh.'),
    'superinfection exclusion': (
        'A cell already infected by one virus resisting infection by another. The resident virus defends its host, in its own interest.',
        'Virus against virus - and the basis of deliberately infecting a crop with a mild strain to keep a severe one out.'),
    'suppressive': (
        'A soil whose microbial community actively prevents disease. The property is transferable: mix a little into a diseased soil and it becomes suppressive too.',
        'Suppressive of the pathogen, not of the plant.'),
    'surfactant': (
        'A substance that lowers surface tension and gathers at the air-water boundary. Detergents, and many natural molecules.',
        'Contraction of surface-active agent.'),
    'Svanemærket': (
        'The Nordic Swan ecolabel. A lifecycle standard with criteria set by a Nordic board, verified by third parties, tightened periodically, and awarded only to the better performers in a category.',
        'It restricts substances that are entirely legal, which is what makes its existence evidence about where the legal floor sits.'),
    'swept-area': (
        'How much of the seabed fishing gear has dragged across, expressed as a ratio: 2 means the area was covered twice over in a year.',
        'The standard measure of trawling pressure. Published annually, which cannot show how often a given patch is hit.'),
    'symbiont': (
        'One partner in a symbiosis. Often the smaller and less visible one, and often the one a survey does not count.',
        'From symbiosis: Greek syn (together) plus bios (life).'),
    'symbiosis': (
        'Two species living in close, lasting partnership. It ranges from both benefiting to one exploiting the other, and much of it was invisible to science until molecular methods arrived.',
        'Greek syn (together) plus bios (life).'),
    'syncytin': (
        'The protein that fuses cells into the layer through which a mammalian placenta exchanges nutrients. It is a viral envelope gene, captured and kept.',
        'The single clearest case of a pathogen becoming essential.'),
    'take-all decline': (
        'A wheat disease that subsides on its own if the same field is cropped long enough, because Pseudomonas populations build up in the soil until they suppress it.',
        'Suppressive soil arising spontaneously - the field cures itself, given time and no fumigation.'),
    'TEP': (
        'Transparent exopolymer particles - sticky invisible gel produced by algae and bacteria, which aggregates into marine snow and, at scale, mucilage.',
        'Stained with Alcian blue to be seen at all, which is why it went unnoticed until the 1990s.'),
    'terminal electron acceptor': (
        'The molecule an organism finally dumps electrons onto to extract energy from food. Oxygen is the best, and when it runs out life switches down a ladder - nitrate, manganese, iron, sulphate, then carbon dioxide.',
        'Each step yields less energy, and each produces a different waste product. The sulphate step is why marine anoxia turns toxic.'),
    'thatch': (
        'A greasy organic mat that builds up in turf when material is produced faster than it decays. Caused by heavy fertilising, pesticides killing earthworms, and compaction.',
        'The ordinary roofing word. Greenkeepers treat it by restoring the soil fauna, not by feeding the grass less.'),
    'thraustochytrid': (
        'Marine microbes in the same group as labyrinthulids, increasingly recognised as major decomposers of organic matter at sea - and farmed commercially for omega-3 oil.',
        'Neither fungi nor algae nor animals, and absent from every category on a monitoring form.'),
    'toxicant': (
        'A poisonous substance, especially a manufactured one. Distinguished from a toxin, which strictly means a poison made by a living thing.',
        'The distinction matters in the literature and is routinely ignored elsewhere.'),
    'transduction': (
        'Genes moved between bacteria by a virus carrying them from one host to the next. A principal route of horizontal gene transfer, which makes viruses a cause of adaptation as well as of death.',
        'One of three classical routes, alongside conjugation and taking up loose DNA from the water.'),
    'transect': (
        'A line along which measurements are taken at intervals - here, usually running from the shore into deeper water to find how deep plants still grow.',
        'Latin trans (across) plus secare (to cut).'),
    'Trichoderma': (
        'A soil fungus sold commercially to protect crops, working partly by producing antifungal compounds and partly by occupying the space a pathogen would need.',
        'An ordinary agricultural product that is also a working demonstration of colonisation resistance.'),
    'trophic': (
        'To do with feeding - who eats whom, and at what level of the food web.',
        'Greek trophe, nourishment. The same root as eutrophic and auxotroph.'),
    'trophic cascade': (
        'A change at one level of the food web propagating down through the levels beneath it - removing a predator releases its prey, which suppresses the level below.',
        'Greek trophe again, nourishment. Cascade because it falls through the levels.'),
    'turbid': (
        'Cloudy - water with enough suspended material in it to block light.',
        'From Latin turba, a crowd or commotion: stirred-up. The same root gives turbine, a thing spun, and disturb. Cloudiness named after the stirring that causes it.'),
    'Type VI secretion system': (
        'A molecular spear one bacterium uses to inject toxins into a neighbour on contact. Bacteria do not only poison each other chemically; they stab.',
        'Contact-dependent, targeted, and aimed overwhelmingly at close relatives competing for the same space.'),
    'Vandkemi': (
        'Danish for water chemistry - the ODA category holding nutrient and contaminant concentrations from water samples.',
        'Straightforwardly water plus chemistry.'),
    'vandområde': (
        'Danish for water body - the administrative unit Danish water policy is written in. There are 119 marine ones, and this project argues at length that the unit is not a natural one.',
        'Vand (water) plus område (area).'),
    'viral shunt': (
        'Viruses bursting bacteria and algae so that their carbon returns to dissolved organic matter instead of being eaten by something larger.',
        'A shunt in the electrical sense: the current is diverted before it reaches the load.'),
    'virion': (
        'A single complete virus particle outside a cell. Marine water holds roughly ten million of them per millilitre.',
        'The unit you would count, as against the infection, which is what they do.'),
    'virioplankton': (
        'The viruses drifting in seawater - roughly ten million in every millilitre, and the most numerous biological entities in the ocean.',
        'Virus plus plankton. Their existence at this scale was only established in 1989.'),
    'virome': (
        'All the viruses in or on an organism or in an environment. Most are uncharacterised, including the ones nearly every human carries permanently with no known effect.',
        'By count the largest part of any microbiome, and the least understood.'),
    'VMS': (
        'Vessel monitoring system - satellite position reports that fishing vessels are required to transmit, used to map where gear was actually worked.',
        'The record exists; the fine-resolution version is not public.'),
    'washwater': (
        'Water used to scrub pollutants out of ship exhaust, then discharged to sea. It is acidic and carries metals and hydrocarbons, and discharging it is legal.',
        'Exhaust gas cleaning moves the pollution from the air to the water; whether that is an improvement depends on which you were measuring.'),
    'Winkler': (
        'The chemical titration for dissolved oxygen, in use since 1888 and still the reference method against which sensors are checked.',
        'Lajos Winkler, who published it as a doctoral student.'),
    'Wolbachia': (
        'A bacterium introduced into mosquito populations to block dengue transmission. Released across whole cities and among the most successful vector-control interventions of the past decade.',
        'The flagship case of replacing a pesticide with an occupant rather than a poison.'),
    'zooplankton': (
        'The drifting animals - copepods, larvae, jellyfish - that eat phytoplankton and are eaten by fish.',
        'Greek zoon (animal) plus planktos.'),
}


# Every written form of a term a reader might meet, generated here rather than
# guessed by a regex in the browser. Suffix-guessing cannot get "mycorrhizal" from
# "mycorrhiza" - it needs to drop the final vowel first - and it has no way at all
# to reach "fungi" from "fungus" or "algae" from "alga".
IRREGULAR = {
    "fungi": ["fungus", "fungal"], "bacteria": ["bacterium", "bacterial"],
    "algae": ["alga", "algal"], "archaea": ["archaeon", "archaeal"],
    "mitochondria": ["mitochondrion", "mitochondrial"],
    "meiofauna": ["meiofaunal"], "macrofauna": ["macrofaunal"],
    "benthos": ["benthic"], "plankton": ["planktonic"],
    "necromass": [], "erg": ["ergs"],
}


def variants(term):
    """The forms of one term. Case-insensitive downstream, so all lowercase."""
    t = term.lower()
    out = {t}
    out.update(IRREGULAR.get(t, []))
    if " " in t or "-" in t:            # multi-word terms take no inflection
        return sorted(out)
    stem = t
    for drop in ("a", "e", "us", "um", "on", "is"):
        if t.endswith(drop) and len(t) - len(drop) >= 4:
            stem = t[: -len(drop)]
            break
    for w in (t, stem):
        out |= {w + "s", w + "es", w + "al", w + "ic", w + "ical", w + "ous",
                w + "ing", w + "ed", w + "ation", w + "ity"}
    if t.endswith("y"):
        out.add(t[:-1] + "ies")
    if t.endswith("us"):
        out.add(t[:-2] + "i")
    if t.endswith("a"):
        out.add(t + "e")                # alga -> algae
    if t.endswith("um"):
        out.add(t[:-2] + "a")           # inoculum -> inocula
    if t.endswith("is"):
        out.add(t[:-2] + "es")          # symbiosis -> symbioses
    return sorted(w for w in out if len(w) > 3)

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
     "here, and group `K` works through them. **A depletion is selective, not "
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
    ("M8", "Failure of renewal",
     "The population is not killed; it fails to replace itself. No propagules, no "
     "connectivity, no settlement cue, wrong timing, or too few left to find each "
     "other. Every individual can be healthy and the population still ends."),
    ("M9", "Change faster than response",
     "The magnitude is survivable and the rate is not. Acclimation, adaptation, "
     "migration and recovery all take time, and a disturbance that returns before "
     "recovery completes is a different thing from the same disturbance once."),
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
     "group is organised by where the nutrient comes from — land, air, sea, bed, "
     "or fixed in place — because that is what distinguishes the entries from each "
     "other. All nine are treated identically."),
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
     "rather than by suffocation. One thing governs the toxic half of the group and "
     "is worth stating before any of it: "
     "**a biocide's molecular target is almost always ancient and shared.** "
     "Selectivity is a matter of dose, uptake and metabolism, not of the target "
     "being absent elsewhere. Azole fungicides inhibit the sterol enzyme CYP51, "
     "which every eukaryote has. Strobilurins block complex III of the "
     "mitochondrial respiratory chain, and SDHIs block complex II, which is also a "
     "Krebs-cycle enzyme - so both are respiratory poisons for anything that "
     "breathes. Neonicotinoids act on acetylcholine receptors and pyrethroids on "
     "sodium channels, both universal in animals, and for these purposes a copepod "
     "is an insect. Triazine herbicides block photosystem II, which is what an alga "
     "photosynthesises with. Glyphosate's target is absent in animals but present "
     "in plants, bacteria and fungi, which makes it an antimicrobial. Naming a "
     "compound after the taxon it is sold to kill describes the market, not the "
     "biochemistry."),
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
    ("W", "Renewal and rate",
     "A population can end without anything killing an individual, and a system can "
     "fail at a magnitude it would survive if it arrived more slowly. This group "
     "exists because the categorical avenues had two entries - failure to replace "
     "itself, and rate exceeded - with almost nothing under them in a register of "
     "127. That absence was not a judgement that these do not matter; nobody had "
     "thought to look."),
    ("Z", "The physical fields and their windows",
     "Light starvation is the same argument as chemical deficiency, one physical "
     "layer up - and the layer behaves differently in a way that matters. A "
     "chemical has one axis: how much. A field has several, and each carries its "
     "own floor and ceiling. Light is not only how much, but of what wavelengths, "
     "for how long, and when. So the exhaustive treatment of the physical avenue is "
     "a small cross-product - the fields are enumerable, their dimensions are "
     "enumerable, and each dimension admits exactly the same two failure modes as "
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
    ("M8", "Failure of renewal",
     "adults are removed or the cue is lost → no successful settlement → the local "
     "population thins → fewer propagules produced and fewer partners found → "
     "settlement falls further",
     "closes because reproduction is density-dependent, so thinning accelerates"),
    ("M9", "Change faster than response",
     "disturbance returns before recovery completes → the system is permanently in "
     "an early successional state → the slow-growing structure-formers never "
     "mature → recovery gets slower still",
     "closes by never allowing the slow half of the community to exist"),
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
     "Compounds with no degradation terminus accumulating in biota and sediment. "
     "For the perfluorinated ones the reason is chemical before it is biological: "
     "the C–F bond is the strongest in organic chemistry and the fluorines shield "
     "the carbon backbone, leaving nothing for an enzyme to attack. That inertness "
     "is the property the materials were selected for.",
     "Monotone accumulation independent of any annual driver.",
     "Biota and sediment time series.",
     "Some biota data exists. Sediment barely."),
    ("E10", "E", "Heavy metals", ["O3"],
     "From harbours, industry, dumping and historic contamination.",
     "Localised, persistent, and redistributed by exactly the dredging and dumping "
     "in group `D`.",
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

    ("E13", "E", "Biocides that remove the decomposers themselves",
     ["O2", "O1", "O3"],
     "Not toxicity in general, but toxicity aimed at the guild whose job is to "
     "break organic matter down. Fungicides are applied by the thousand tonnes and "
     "are designed to kill fungi; fungi are the organisms that degrade the tough "
     "fractions - lignin, chitin - that bacteria leave behind.",
     "**This is the thatch mechanism, and thatch is what fedtemøg looks like on "
     "land.** A greasy organic mat forms on turf when production outruns "
     "decomposition, and the classic causes are heavy nitrogen *and pesticides that "
     "kill the earthworms and microbes doing the incorporating*. Greenkeepers treat "
     "it by restoring the soil life. If the same holds in sediment, organic matter "
     "accumulates with no change in nutrient supply at all — the input is normal "
     "and the processing has stopped.",
     "Decomposition rate of standard organic material along a biocide gradient, "
     "with fungal and bacterial biomass measured alongside. The discriminator "
     "against the nutrient hypothesis is that supply is held constant.",
     "Fungicide concentrations in sediment, and fungal biomass. Neither is measured "
     "in Danish marine monitoring, and `R11` records that the fungi are not counted "
     "anywhere."),
    ("E14", "E", "Veterinary antiparasitics in manure", ["O2", "O1", "O3"],
     "Avermectins given to livestock pass through the animal and remain active in "
     "its dung. Dung from treated cattle is measurably slower to break down because "
     "the insects that break it down are killed by the residue - documented since "
     "the 1980s.",
     "A worked, published example of exactly the mechanism above, on land, in "
     "agriculture: **the material is not different, the organisms that process it "
     "are gone.** That dung goes on fields, and what runs off fields reaches water. "
     "The register has no other entry where the terrestrial case is this well "
     "established.",
     "Antiparasitic residues in manure, runoff and sediment, against decomposition "
     "rate of standard material.",
     "Veterinary pharmaceutical residues in Danish soil, runoff or sediment. Not "
     "routinely measured."),
    ("E15", "E", "Total biocide load, whatever its source", ["O3", "O2", "O1"],
     "Household, agricultural and industrial biocides reach the same water and act "
     "on the same organisms. Antifoulants, wood preservatives, agricultural "
     "fungicides and insecticides, disinfectants, veterinary products, and the "
     "antibacterials in ordinary consumer goods.",
     "**For the effect, only the load matters; the source split is politically "
     "interesting and mechanistically irrelevant.** That is the exact inverse of "
     "how nitrogen is handled, where the source split is the entire public argument "
     "and the effect coefficient does not exist. Here there is a plausible effect "
     "and nobody has added the load up. And there is hard evidence the agricultural "
     "fraction does reach environmental organisms at active concentrations: "
     "azole-resistant *Aspergillus* has arisen in the Netherlands and Denmark from "
     "agricultural azole use, which means those fungicides are selecting on "
     "non-target environmental fungal populations. Resistance is proof of exposure.",
     "Summed biocidal load per catchment against decomposer biomass and "
     "decomposition rate — the sum, not any single substance against its own "
     "threshold, which is the `U1` problem.",
     "A total biocide load figure for Denmark by catchment. Sales data exists by "
     "substance nationally; nothing assembles it into an environmental load. *Why* "
     "the load has the composition it has is a question about markets rather than "
     "about water, so it is argued in "
     "[PROGRAMME.md](#PROGRAMME.md) and deliberately not here — every entry in this "
     "register has to name an observable in the sea, and that one cannot."),

    ("E16", "E", "Conserved targets: \"selective\" is a claim about dose",
     ["O3", "O4", "O6", "O7"],
     "The molecular machinery agricultural biocides attack is shared far beyond the "
     "taxon on the label. Azoles inhibit CYP51, the sterol enzyme of every "
     "eukaryote, and other cytochrome P450s including the vertebrate ones that make "
     "steroid hormones. Strobilurins block respiratory complex III and SDHIs block "
     "complex II, which is simultaneously a Krebs-cycle enzyme - conserved wherever "
     "there are mitochondria. Neonicotinoids act on acetylcholine receptors and "
     "pyrethroids on voltage-gated sodium channels, both universal in animals. "
     "Triazines block photosystem II, which is what algae photosynthesise with.",
     "**Selectivity is pharmacokinetic, not mechanistic** - a matter of who takes "
     "the dose up and how fast they break it down, not of the target being absent. "
     "So the marine effect is not a surprising off-target finding requiring special "
     "evidence; it is the default expectation, and its absence would be what needed "
     "explaining. Two consequences bite hard here: for a sodium-channel or "
     "acetylcholine poison **a copepod is an insect**, and copepods are the base of "
     "the food web; and for a photosystem II inhibitor **an alga is a weed**.",
     "Body burdens and sublethal endpoints in non-target marine taxa chosen by "
     "*target conservation* rather than by convenience - copepods for the "
     "neuroactives, algae for the photosynthesis inhibitors, fungi and sterol "
     "synthesis for the azoles.",
     "Marine concentrations of the actual high-tonnage compounds, with endpoints "
     "matched to their mechanism. Danish marine monitoring covers few of them and "
     "tests mortality rather than the conserved pathway."),
    ("E17", "E", "The microbiome is the exposed organ", ["O3", "O7", "O6"],
     "Animals and plants carry the target taxa inside them. A fungicide reaching a "
     "marine invertebrate meets that animal's fungal and bacterial symbionts; a "
     "shikimate-pathway herbicide meets its gut bacteria. The host's own cells may "
     "be untouched while the organisms it depends on are not.",
     "**A host can be killed through its symbionts, and no toxicity test on the "
     "host would see it.** This is the same structure as `T2`, where seagrass "
     "depends on clams that depend on sulphide-oxidising bacteria - three organisms "
     "and only one of them visible in a survey. It also predicts that damage "
     "appears as failure to thrive, failure to reproduce, or susceptibility to "
     "disease rather than as acute mortality, which is precisely what standard "
     "ecotoxicology is worst at detecting.",
     "Symbiont community composition and function in exposed versus unexposed "
     "hosts, with host survival as a *secondary* endpoint rather than the primary "
     "one.",
     "Host-associated microbial community data for Danish marine organisms. None."),

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
     "`J` and for the oxygen demand of `M1`. A shunted system looks productive and "
     "feeds nothing.",
     "Viral abundance and lysis rate against the share of production reaching "
     "mesozooplankton - the ratio, not either alone.",
     "Marine viral counts. Standard method since the 1990s; not in Danish "
     "monitoring at any station."),
    ("F13", "F", "The organisms that fall between the folk categories",
     ["O3", "O7", "O2", "O1"],
     "Danish marine monitoring is organised as *bundfauna*, *vegetation* and "
     "*phytoplankton* — animals, plants, and small green things. That is a folk "
     "taxonomy, and it does not match the tree of life. Labyrinthulids, which cause "
     "eelgrass wasting disease, are stramenopiles: more closely related to kelp and "
     "diatoms than to any fungus, despite living like one. Oomycetes are in the same "
     "group. Animals and fungi are sister lineages, so a mushroom is a closer "
     "relative of yours than of a plant. Plants, animals and fungi are three "
     "branches out of many, and most eukaryotic diversity — nearly all of it marine "
     "and microbial — sits in groups with no common name.",
     "**A survey organised by folk categories has no column for an organism that "
     "does not fit them.** The absence is then read as absence in the sea rather "
     "than absence from the form. This is the mycorrhizal problem made "
     "administrative: not a mechanism rejected, a mechanism with nowhere to be "
     "recorded. The specific casualties here are the ones that matter most for "
     "decay and disease — labyrinthulids, thraustochytrids, oomycetes, marine "
     "fungi.",
     "Molecular community surveys — sequencing what is present rather than sorting "
     "it into the categories the form provides. Metabarcoding is standard, cheap and "
     "taxonomically agnostic by construction.",
     "Sediment and water eDNA surveys with an open taxonomic frame. None in Danish "
     "routine monitoring, and the categories on the existing forms are why."),
    ("F14", "F", "Viruses as structure, not only as mortality",
     ["O4", "O3", "O1", "O2"],
     "`F11` counts viruses as a killer, which is how they are usually filed. They "
     "are at least three other things at once. They **structure the community**: "
     "the most abundant bacterium is the easiest target for its own phage, so "
     "cropping falls hardest on whoever is winning, and diversity is maintained by "
     "predation rather than by competition. They **move genes**: transduction by "
     "phage is a principal vector of the horizontal transfer that makes prokaryotic "
     "adaptation fast. And in animals they appear to **defend**: mucus layers are "
     "enriched in phage that attack incoming bacteria, which is a host benefit "
     "delivered by something classified as a parasite.",
     "The same entities are simultaneously the largest agent of mortality, the "
     "thing that keeps any one lineage from taking over, and the delivery mechanism "
     "for the adaptation that lets prokaryotes outrun everything else. **Which "
     "means they cannot be scored on one axis at all** — removing viral pressure "
     "would not simply reduce mortality, it would collapse diversity and slow "
     "adaptation together.",
     "Community diversity and gene-transfer rates against viral abundance, rather "
     "than mortality against viral abundance.",
     "Marine viral counts and viral community composition. Not measured at any "
     "Danish station, and the marine RNA virosphere in particular was largely "
     "undescribed until the last few years. **This is the most likely present "
     "location of the mycorrhizal gap** — a whole functional layer filed under "
     "*pathogen* and therefore never examined for what else it does."),
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
     "the principal producers of the gel in group `J`. Enhanced production also buries "
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
     "Most algae cannot make vitamin B12 for themselves and have to get it "
     "ready-made from bacteria — they are *auxotrophs* for it. "
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
     "Lose the clams - to trawling, to hypoxia, to anything in group `D` - and the "
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
     "hypoxia, trawling and toxicants each do independently of any nutrient. The "
     "chemical route to that is `E13`, `E14` and `E15`; this entry is the mechanism, "
     "those are the agents.",
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
     "a link between group `B`'s imported fat and group `J`'s surface film.",
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

    # ---- W ----------------------------------------------------------------
    ("W1", "W", "Propagule supply and connectivity", ["O7", "O3"],
     "Recolonisation needs propagules to arrive. If the source populations are gone "
     "or the currents no longer connect them, a site with perfect conditions stays "
     "empty.",
     "Recovery fails at sites where every measured variable is adequate, and it "
     "fails as a function of *distance from a surviving population* rather than of "
     "local quality. Constructed changes to circulation (`C8`) can sever "
     "connections without changing water quality anywhere.",
     "Recovery rate against distance to the nearest source population and modelled "
     "larval connectivity, holding local conditions fixed.",
     "Source population locations, and particle-tracking connectivity from the "
     "existing circulation models."),
    ("W2", "W", "Settlement cue failure", ["O7", "O3"],
     "Larvae of many species choose where to settle using chemical and acoustic "
     "cues from existing habitat. A degraded bed does not smell or sound like "
     "habitat, so larvae that arrive do not stay.",
     "A positive feedback with no physiology in it: the absence of the community is "
     "itself what prevents the community returning. Explains why restoration "
     "sometimes works only above a threshold density.",
     "Settlement rates onto degraded versus conditioned substrate at the same site "
     "- the standard settlement assay.",
     "Settlement plates with and without conditioning. Cheap, and connects directly "
     "to the sediment-inoculation experiment `X1`."),
    ("W3", "W", "Phenological mismatch", ["O6", "O3", "O4"],
     "Larval release, spawning and the spring bloom are timed by different cues - "
     "temperature, photoperiod, stratification onset. Warming moves them at "
     "different rates, so the food and the mouths that need it drift apart.",
     "Recruitment collapses with no change in total production. The classic "
     "match-mismatch mechanism, and it is invisible to any indicator computed as a "
     "seasonal mean - which is how both Danish indicators are computed.",
     "Timing of bloom peak against timing of larval abundance, over years.",
     "Sub-monthly plankton time series. The sampling frequency is the binding "
     "constraint, not the parameters."),
    ("W4", "W", "Allee effects at low density", ["O3", "O7"],
     "Below a density threshold, reproduction fails - broadcast spawners do not "
     "fertilise, mates are not found, group defences stop working.",
     "The decline becomes self-sustaining below a threshold, so a stressor removed "
     "after the threshold is crossed produces no recovery. Indistinguishable from "
     "'the stressor is still present' unless density is the variable examined.",
     "Recruitment per adult against adult density, which should fall rather than "
     "flatten at the low end.",
     "Density-resolved reproductive success. The fauna data has densities; the "
     "analysis is not run."),
    ("W5", "W", "Recovery slower than the disturbance interval", ["O3", "O7"],
     "A bed trawled every few months, or dredged on a maintenance cycle, is held "
     "permanently in early succession. The slow-growing, structure-forming, "
     "long-lived species never reach maturity.",
     "**The same total disturbance produces a different outcome depending only on "
     "its spacing.** An annual effort figure cannot represent this, and annual "
     "effort figures are the only ones published. The community is defined by the "
     "return interval relative to its own generation times.",
     "Community composition against disturbance *interval*, not annual intensity.",
     "Trawling effort at monthly or finer resolution - which the data-source hunt "
     "confirmed is the single most important closed dataset."),
    ("W6", "W", "Change outrunning acclimation", ["O3", "O6"],
     "Organisms acclimate and populations adapt, and both have rates. A warming or "
     "freshening survivable over a century can be lethal over a decade.",
     "Mortality at magnitudes the tolerance curve says are survivable, because the "
     "tolerance curve was measured at equilibrium.",
     "Response to rate of change, holding the magnitude of change fixed.",
     "High-frequency records, which exist, analysed for rates rather than means, "
     "which is not done."),
    ("W8", "W", "Whoever founds the community keeps it", ["O3", "O7", "O4"],
     "After a crash, the survivors are not a random sample — they are whoever "
     "tolerated the thing that did the killing. And they are then the **founder "
     "population**: everything that follows is their descendants competing among "
     "themselves, on a bed with no one else on it. Arriving first is worth more "
     "than being well suited, which community ecology calls a priority effect.",
     "**So the composition of a degraded system is partly historical accident, not "
     "a reading of the new conditions.** It records what happened to survive one "
     "event, amplified by having had the place to itself afterwards. Which means "
     "the state can persist after the conditions that produced it have gone — no "
     "hysteresis mechanism required beyond who got there first — and it explains "
     "why removing the original stressor often changes nothing.",
     "Whether recolonisation composition tracks current conditions or tracks the "
     "identity of the survivors of the last disturbance. Two very different "
     "predictions from the same starting point.",
     "Community composition immediately after a disturbance and through recovery, "
     "at the same place. Requires having sampled before, which is `T10`'s problem "
     "in another form."),
    ("W7", "W", "Too little variation left to respond with", ["O3"],
     "Repeated mortality selects survivors down to a narrow genetic and functional "
     "set, and a narrow set has fewer ways to meet the next disturbance.",
     "Declining resilience with no change in any concentration: the same stressor "
     "produces a larger effect than it did, and the system's own history is the "
     "variable.",
     "Functional and genetic diversity through time, against the effect size of "
     "comparable disturbances in different eras.",
     "Long species-level fauna series, which ODA holds; genetic data, which nobody "
     "has."),

    ("T9", "T", "Pathogen and partner are not kinds of organism",
     ["O3", "O7", "O6"],
     "Parasite, commensal and mutualist are positions on a spectrum, not classes of "
     "creature, and an organism moves along it with the context. The clearest "
     "demonstrations are the largest: mitochondria and chloroplasts were "
     "free-living bacteria; roughly eight per cent of the human genome is retroviral "
     "in origin; and the protein that builds the mammalian placenta is a captured "
     "viral envelope gene, so **mammalian pregnancy runs on a domesticated virus**. "
     "In the other direction, most of the viruses and microbes carried by any "
     "animal have no characterised effect at all.",
     "**Sign is a property of the relationship, not of the species** — so a survey "
     "that lists which organisms are present cannot report the state of the "
     "relationships between them, which is where the function lives. And stress "
     "flips the sign: `T3` is exactly this, a resident organism becoming lethal "
     "when the host is shaded or sulphide-stressed. The same reading applies to "
     "`T2`, `T5` and `T6`, where what was lost was a partnership rather than a "
     "population.",
     "Host condition against symbiont community composition under a stress "
     "gradient, rather than presence-or-absence of any named organism.",
     "Host-associated microbial and viral community data through a stress gradient. "
     "Absent for every Danish marine species."),
    ("T12", "T", "Defence is outsourced, because the host cannot win the race",
     ["O3", "O7", "O6"],
     "Pasteur and Joubert saw microbes suppressing each other in 1877, and Fleming's "
     "*Penicillium* was the same phenomenon fifty years later. Nearly every "
     "antibiotic in use is a weapon taken off that battlefield — mostly from soil "
     "actinomycetes, which have been fighting fungi and each other for hundreds of "
     "millions of years. There is no reason the war stops at fungi and bacteria: "
     "phage against bacteria, bacteria against phage, fungi against both, all of "
     "them at generation times the host cannot approach. The matrix fills in almost "
     "completely and most of it is documented: fungi make antibacterials "
     "(penicillin); bacteria make antifungals (nystatin, amphotericin, both from "
     "*Streptomyces*); viruses make antibacterials, which is phage therapy; viruses "
     "make antifungals, and a mycovirus that weakens chestnut blight is a deployed "
     "biocontrol agent; and bacteria make antivirals — restriction enzymes, CRISPR, "
     "and a fast-growing list of anti-phage systems.\n\n"
     "**And the diagonal of that matrix — same against same — is the most complete "
     "row of all**, which is not a curiosity. Bacteria against bacteria is most of "
     "the pharmacy, plus bacteriocins and the secretion systems with which they "
     "physically stab each other. Fungi against fungi gives griseofulvin, the "
     "echinocandins, and the strobilurins — named for the fungus that makes them to "
     "kill other fungi — as well as *Trichoderma*, sold commercially, which "
     "parasitises its relatives directly. Virus against virus is superinfection "
     "exclusion, defective interfering particles, and mild-strain cross-protection, "
     "which is deployed in agriculture against citrus and papaya viruses.\n\n"
     "The reason the diagonal is richest is the same reason it is useful: **the "
     "closest competitor is the most effective antagonist**, because niche overlap "
     "is maximal. Anything that can exclude a pathogen by needing exactly what it "
     "needs is doing colonisation resistance and chemical warfare at once, which "
     "makes the diagonal the natural place to look for an agent under `T11`. "
     "Most strikingly, several "
     "components of our own innate immunity are homologous to those bacterial "
     "anti-phage systems, so the vertebrate immune system is itself partly a "
     "captured weapon from that war.",
     "**So a slow organism cannot defend itself by evolving.** It has two options, "
     "and it uses both. It can carry *generalisable priming* — machinery built in "
     "advance to recognise and label whatever turns up, which is what an immune "
     "system is, and which vertebrates push to the point of running mutation and "
     "selection somatically inside one body because the germline is far too slow. "
     "Or it can **outsource**: host the microbial combatants and let their arms "
     "race supply the defence. Eelgrass, mussels and every invertebrate on a Danish "
     "seabed have no adaptive immune system at all, so for them the second route is "
     "not a supplement. It is the defence.",
     "Host susceptibility against the composition of its associated microbial "
     "community, rather than against any property of the host itself.",
     "Host-associated community data with matched disease outcomes. Absent. **And "
     "the consequence is the sharp end of group `E`**: a broad-spectrum biocide "
     "does not merely kill pests, it disarms the host by removing its garrison — "
     "and the host cannot re-evolve the defence, because being unable to compete on "
     "adaptive terms is why it was outsourced in the first place. It can only "
     "re-acquire the allies, which is `T5`, `T11` and `X1` again.\n\n"
     "There is a constructive corollary, and it belongs on the record even though "
     "it is not a hypothesis about Danish water. **That war is a chemical library "
     "a billion years old, and it has barely been read.** Nearly every antibiotic "
     "in clinical use came from one narrow sample of it — soil actinomycetes — and "
     "the marine equivalent is close to unexplored, while restriction enzymes and "
     "CRISPR, the two tools modern biology is built on, both came from the "
     "bacteria-phage front of the same conflict. Anything this project might want "
     "for restoration — a targeted antifungal, a phage against a specific pathogen, "
     "a hypovirulence agent — is more likely to be found there than synthesised, "
     "and a compound taken from that war has an evolutionary prior by "
     "construction."),
    ("T11", "T", "Occupancy is the function", ["O3", "O7", "O6"],
     "A body is an environment, and so is a sediment surface, a leaf, a root, a "
     "mucus layer. What lives there is competing for space and resources against "
     "everything else able to live there — so a resident's benefit to its host is "
     "often not anything it produces. It is that **it is there, and therefore "
     "something else is not**. This is colonisation resistance, and in gut, skin "
     "and rhizosphere it is the main protective function the community performs.",
     "**A function with no product cannot be found by looking for one.** No "
     "metabolite, no signal, no service — just an occupied niche. It is invisible "
     "to any survey asking what an organism does, and visible only in what happens "
     "when it is removed. Which makes it structurally the same problem as `T10`, "
     "and explains why removals so often surprise: the thing lost was the "
     "occupancy.",
     "Invasion or infection success in an intact community against a depleted one, "
     "with the community otherwise matched. The classic design, and the same one as "
     "the sediment inoculation of `T5`.",
     "Challenge experiments on intact versus disturbed communities. Standard method "
     "in medical and soil microbiology, not applied in Danish marine work. **The "
     "human case is the strongest evidence in this whole register that the "
     "mechanism is real and the remedy works.** A course of antibiotics clears the "
     "gut community, *Clostridioides difficile* moves into the vacancy, and the "
     "harm comes from the emptiness rather than from the drug. The treatment is "
     "faecal microbiota transplant — putting a whole functioning community back, "
     "with cure rates around ninety per cent, and without anyone needing to know "
     "which member did the work. That is precisely the design of `X1`, already "
     "proven in one domain and never tried in the sediment.\n\n"
     "**And occupancy has a property no chemical intervention has: nothing can "
     "evolve resistance to a space being taken.** A biocide is a single molecular "
     "target, so it selects for whoever can alter that target, and the earlier "
     "section makes the winners predictable in advance. Exclusion offers no target "
     "at all — the incomer has to out-compete an entire established community for "
     "resources it also needs, which is not a mutation but a whole strategy. It is "
     "also *idempotent*: the niche is either occupied or it is not, adding more "
     "changes nothing, and there is no dose to escalate. That is why faecal "
     "transplant does not breed resistance the way the antibiotic that created the "
     "vacancy does.\n\n"
     "**The idempotency holds only while turnover is slow relative to the "
     "intervention**, and that qualification is not small. A community of "
     "fast-dividing organisms is not a static occupancy; it is a contest being "
     "re-run continuously, and then *who founded it* matters more than who is "
     "suited to it — which is `W8`.\n\n"
     "The honest limit: exclusion can still be defeated, by displacement or by an "
     "incomer occupying a slightly different niche. It is harder rather than "
     "impossible. But **an intervention that cannot be evaded by a point mutation "
     "is a different class of thing from one that can**, and that difference is a "
     "reason to prefer restoration over chemistry which owes nothing to sentiment."),
    ("T10", "T", "Removing an organism whose role is unknown is not neutral",
     ["O3", "O7", "O6"],
     "Biocides and pest control remove organisms classified as harmful. That "
     "classification is made on the harm somebody noticed, and most residents of "
     "any host or sediment have never been characterised at all.",
     "The default assumption that removal is safe unless harm is demonstrated is "
     "the same burden-of-proof inversion the chemicals argument turns on, applied "
     "to organisms instead of substances. There is precedent for it going wrong: "
     "loss of helminths is implicated in human immune dysregulation, and the phages "
     "removed alongside their bacterial hosts regulate the community that remains "
     "(`F11`).",
     "Community function - decomposition rate, disease resistance, recruitment - "
     "before and after a removal, rather than the target organism's abundance.",
     "Baseline community composition before any intervention. Almost never "
     "collected, which makes the comparison impossible afterwards by construction."),

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
      "what is right. So this page does the other thing: it enumerates the "
      "mechanisms that could produce the outcomes below, all of them stated at full "
      "strength, so that each can be related to the same evidence and scored.\n")
    a(f"**{len(rows)} mechanisms in {len(by_group)} groups.** No entry here is the "
      "subject of the page and the rest its alternatives. The grouping is "
      "alphabetical for reference, which is an ordering and not a ranking; the "
      "letters carry no priority, and `A1` is first for the same reason `Z8` is "
      "last.\n")
    a("**Some entries have a political history attached to them and some do not, "
      "and that history is not a property of the mechanism.** A mechanism that has "
      "been legislated about is not thereby more likely; one that nobody has "
      "campaigned on is not thereby more likely either. Where an entry names an "
      "industry, a practice or a public work, it names it as the physical source of "
      "a flux, in the same way `C4` names an inflow event — the entry is about what "
      "enters the water, never about who is at fault for it. Attribution of blame "
      "is not a scientific operation and is not performed anywhere on this page.\n")
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
      "and some — group `I` especially — are not about the sea at all but about the "
      "instrument. They do not tile anything.\n")
    a("**The entries are not independent.** Sulphur alone appears as an oxygen "
      "sink (`E1`), as reduced bed chemistry (`M7`), as the reason the marine "
      "electron-acceptor cascade differs from the freshwater one (`R5`), as the "
      "release mechanism for sediment phosphate (`R6`), and as the poison that "
      "kills eelgrass from below (`T1`). That is one element seen from five sides, "
      "not five causes. **Counting entries therefore says nothing about weight**, "
      "and a group with fourteen entries is not thereby more important than one "
      "with four.\n")
    a("**A mechanism has to be conceivable before it can be a hypothesis, and "
      "conceivability has a history.** The clearest precedent is mycorrhizal "
      "symbiosis. Something like nine in ten land plants feed through a fungal "
      "partner; the arrangement is four hundred million years old; and for most "
      "plants it is the primary organ of nutrient acquisition. It entered the "
      "scientific picture properly within living memory. Every soil textbook before "
      "that was wrong about how plants eat, and nobody knew they were wrong — the "
      "mechanism was not rejected, it was **unimagined**, and no amount of care in "
      "enumerating the known causes would have produced it.\n")
    a("There is good reason to think the marine version of that gap is open right "
      "now, and that it sits in the same place: fungi, oomycetes and "
      "labyrinthulids. Molecular surveys keep finding far more fungal diversity in "
      "marine sediment than anyone expected, the group that causes eelgrass wasting "
      "disease is one of these, and none of them appears in Danish marine "
      "monitoring at all (`R11`, `F12`, `T8`). The lucinid clam symbiosis of `T2` "
      "makes the same point on a smaller scale: it was described in 2012, and "
      "before that its loss was not a hypothesis anyone could have held.\n")
    a("So the honest reading of this register's size is not *we have thought of a "
      "lot*. It is that the entries are drawn from what the literature has so far "
      "been able to imagine, and the history of that literature is a history of "
      "whole functional domains arriving late.\n")
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
    a("> For any chemical species there are exactly **two** ways it can harm: "
      "**below the floor** of what is needed, or **above the ceiling** of what is "
      "tolerated. That is a partition of the real line by an interval. Nothing can "
      "hide between the cases and there is no third.\n")
    a("Liebig's floor and Shelford's ceiling, and the essential trace metals sit on "
      "both — copper is required and copper is a biocide, within about one order of "
      "magnitude. What differs between substances is not the number of failure "
      "modes but **where the interval's ends are**. A substance nothing needs has "
      "its floor at zero, so only the ceiling can be crossed. A substance harmful "
      "at any dose has its ceiling at zero, so only that side exists. Both are the "
      "same two rules with an endpoint at the origin, and treating either as a "
      "separate case is a wobble rather than a subtlety.\n")
    a("**This applies to nitrogen exactly as it applies to copper.** Nitrogen is "
      "not a pollutant; it is a requirement with a window, and it has both a floor "
      "and a ceiling like every other element on the list. Which means a policy "
      "expressed only as *less is better* is a one-tailed treatment of a two-tailed "
      "quantity — the same error as *more is better*, pointed the other way.\n")
    a("That is not an argument that Danish coastal water needs more nitrogen. In "
      "many places the load is plainly above the optimum and reduction plainly "
      "helps. The point is structural and has two consequences. The optimum is a "
      "*position in a window*, so the benefit of reduction depends on where an area "
      "currently sits, and that position differs by area — which is the argument of "
      "[AREAS.md](#AREAS.md) arriving from the chemistry rather than from the "
      "statistics.\n")
    a("**And the window is not a property of the substance. It is a property of the "
      "whole mixture.** Both ends move with everything else present, by at least "
      "four routes, and none of them is exotic:\n")
    a("- **Bioavailability.** What matters is the fraction an organism can actually "
      "take up, not the total. Phosphate bound to iron oxide is present and "
      "unavailable (`S4`); iron bound to organic ligands is present and unavailable "
      "(`K6`); metal toxicity depends on speciation rather than concentration. A "
      "measurement of the total says almost nothing about where in the window the "
      "organism is.\n")
    a("- **Antagonism.** Excess of one nutrient blocks uptake of another and induces "
      "a deficiency that looks nothing like enrichment — high nitrogen suppressing "
      "copper and boron, high phosphorus inducing zinc deficiency (`K3`). The "
      "floor of one element rises because the ceiling of another was crossed.\n")
    a("- **Ratios rather than amounts.** Whether nitrogen limits at all depends on "
      "the silicon and phosphorus beside it, and the community that results depends "
      "on the ratio rather than the total (`K1`, `K2`).\n")
    a("- **Conditions.** pH decides how much ammonium is the toxic un-ionised "
      "form; redox decides whether iron holds phosphate or releases it; "
      "temperature moves every rate. The chemistry's window sits inside the "
      "physical window of group `Z`.\n")
    a("So there is no single tolerable figure for nitrogen even in one place on one "
      "day, and a national number is a summary of a quantity that does not exist. "
      "This is also why `U1`, mixture effects, is not a fringe caveat: **the "
      "mixture is what sets the window**, and testing substances one at a time "
      "against fixed thresholds assumes precisely what is false.\n")
    a("Nobody has published where each Danish area sits in that window, and the "
      "flat 25% rule of the iltsvind trigger assumes the answer is the same "
      "everywhere.\n")
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
      "dimensions × the same two failure modes** — and all three factors are "
      "enumerable. That makes it the most nearly closable part of the register, and "
      "group `Z` exists to work through it. Denmark already measures most of the "
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
      "enumeration, and it is why group `D` can be checked nearly to the end.\n")
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
    a("**These are derived, not chosen.** An earlier version of this page listed "
      "seven routes arrived at by asking what could produce the terminal outcomes — "
      "a question with no natural stopping point, and no principle saying why those "
      "seven and not others. They were plausible and arbitrary. Each route is now "
      "the instantiation of one or more of the avenues above, and the mapping is "
      "what justifies the list.\n")
    a("Running the mapping the other way found the same hole the hypothesis "
      "register had: `V7` and `V8` had **no route at all**. A population that fails "
      "to replace itself, and a disturbance returning faster than recovery, were "
      "not representable anywhere in the structure. `M8` and `M9` exist because the "
      "avenues demanded them, which is the second time the procedure has produced "
      "something the intuition missed.\n")
    a("They are still not disjoint — `M7` is partly a special case of `M2`, `M5` "
      "ends by feeding `M3`, and `M9` is a rate applied to any of the others. Where "
      "the mapping to an avenue is poor, it is the route list that should change.\n")
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
      "removes the algae that cannot make vitamin B12 for themselves and leaves the "
      "bacteria that make it for them. Carbonate "
      "depletion removes calcifiers and no one else. Light starvation removes what "
      "is rooted at depth. Each is a filter with its own specific shape.\n")
    a("**And the number of ways an organism can be stopped is the number of things "
      "it requires.** That is Liebig's law read as a counting argument. Large, slow, "
      "structured life needs a particular substrate, particular partners, particular "
      "light, particular chemistry, a particular season, and years of quiet in which "
      "to mature — a dozen windows, any one of which closing is fatal. An "
      "opportunist needs carbon, some nutrient, and water. Whatever goes wrong, it "
      "is more likely to have gone wrong for the demanding species, and the "
      "asymmetry is not about fitness: **the low-requirement organism wins by being "
      "harder to stop.**\n")
    a("Which has a consequence that reverses the usual reading. A standing meadow or "
      "mussel bed is not a *symptom* of a healthy system — it is a **cause** of one. "
      "It draws the surplus down, shades the water, filters the plankton, oxygenates "
      "and binds the sediment, and shelters the grazers. It manufactures scarcity "
      "for its competitor: it imposes Liebig limitation on organisms that have "
      "almost none of their own. Read backwards, that is the whole of the hysteresis "
      "in `H1` — once the structural life is gone nothing imposes the limitation, "
      "the surplus stays available, and the fast forms keep it.\n")
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

    a("### Not every depletion feeds itself — and the difference is decay\n")
    a("The selection argument above is too tidy, and the correction sharpens it. "
      "Depletions are not interchangeable, because **what dies leaves a body, and "
      "decay has a gas signature**. Whether a shortage worsens or cures itself "
      "depends on whether the decomposers consume the missing thing or release "
      "it.\n")
    a("Take the two great gases and run them against each other.\n")
    a("| | what it kills | what decay then does | feedback |")
    a("|---|---|---|---|")
    a("| **Oxygen depletion** | aerobes — most animals | consumes more oxygen, "
      "releases CO₂ | **self-amplifying** |")
    a("| **CO₂ depletion** | photosynthesisers | releases CO₂, consumes oxygen "
      "| **self-correcting** |")
    a("")
    a("The asymmetry is complete and it is not a coincidence. Respiration and "
      "photosynthesis are the same reaction run in opposite directions, so every "
      "corpse that decays *relieves* a carbon shortage and *deepens* an oxygen one. "
      "A carbon dioxide shortage cures itself, because everything that dies of it "
      "puts the carbon back. An oxygen shortage is fed by its own casualties.\n")
    a("This is not hypothetical at either end. Inside a dense bloom, CO₂ really is "
      "drawn down far enough to push pH above 9 — which is the carbon entry in the "
      "element sweep below, and the reason a bloom can poison water by consuming "
      "carbon rather than by producing anything. It corrects within a day, as soon "
      "as respiration resumes. Bottom-water oxygen depletion does not correct at "
      "all; it compounds.\n")
    a("**And the sign of that feedback depends on light and mixing, not on biology "
      "alone.** In shallow lit water the survivors of an oxygen crash are "
      "photosynthetic, so daylight restores oxygen and the system oscillates rather "
      "than ratchets. Below a pycnocline in the dark the survivors are sulphate "
      "reducers and methanogens, whose metabolism restores nothing and adds a "
      "poison. Same depletion, same selection logic, opposite outcome — decided by "
      "whether photons reach the survivors.\n")
    a("### The winners do remake the world, on the wrong timescale\n")
    a("The deeper objection is right, and it deserves stating at full strength: "
      "**organisms that can function in a depleted state come to dominate it, and "
      "in dominating it they change the conditions.** Adaptation is not only a "
      "response to the environment; it is a cause of the next one.\n")
    a("The extreme case is the whole reason any of this exists. Cyanobacteria "
      "adapted to an anoxic, carbon-rich world, and in filling it they released "
      "oxygen — which poisoned most of the biosphere that had produced them and "
      "created the conditions for every aerobic thing since, the authors of this "
      "page included. That is the objection at planetary scale, and it is not a "
      "metaphor: the winners of a depletion rebuilt the atmosphere.\n")
    a("> **It took roughly two billion years.** Which is the whole of the "
      "consolation and the whole of the problem. Life does rebalance, reliably, and "
      "on a timescale that has no relationship to a policy cycle, a fishery, a "
      "human life, or the persistence of anything anybody is trying to protect. "
      "*The system recovers* and *the recovery is available to us* are different "
      "claims, and only the first one is true.\n")
    a("So the convergence argument survives with a boundary drawn around it. It "
      "describes what happens on the timescale of decades, in a system that is "
      "being pushed continuously and given no interval in which to run the slow "
      "half of the cycle. `W5` and `M9` are that boundary stated as mechanisms: it "
      "is the *return interval* relative to the recovery rate that decides the "
      "outcome, not the total disturbance.\n")

    a("### Who makes the window, and how fast they can move it\n")
    a("One more layer under all of this, and it is the one that decides the "
      "direction of everything above.\n")
    a("**A tolerance window is not a constant of nature. It is an evolved "
      "property** — the accumulated result of every ancestor that met a condition "
      "and survived it. So the window is made by life, and it can move. Four things "
      "decide how fast, and they are not equally weighted:\n")
    a("| | | |")
    a("|---|---|---|")
    a("| **What is primed** | Is there existing machinery already close to "
      "sufficient? | The dominant term, and the one usually left out |")
    a("| **Mutational bias** | *Where* variation arises, not how much | Mutation is "
      "not uniform, and recombination is not random |")
    a("| **Mutation rate** | How much raw variation per copy | Secondary for "
      "cellular life — **and the whole strategy for some things** |")
    a("| **Generational turnover** | How often selection gets to act | Differs "
      "across organisms by five orders of magnitude |")
    a("")
    a("**Priming carries most of the weight.** New capabilities almost never arise "
      "from nothing; they arise by duplicating and modifying something that already "
      "worked. So what decides whether a lineage can meet a new condition is not "
      "the supply of mutations but the *distance* from its existing machinery to "
      "the required function.\n")
    a("**Antibiotic resistance appears within years**, because the machinery "
      "pre-existed: soil bacteria have competed with antibiotic-producing fungi for "
      "hundreds of millions of years, and efflux pumps and degrading enzymes were "
      "already sitting in the shared gene pool. The same holds for a wholly "
      "synthetic substrate when the chemistry is ordinary — nylon oligomers were "
      "invented in 1935 and organisms digesting them were isolated by the 1970s, "
      "because an amide bond is something almost everything already hydrolyses.\n")
    a("> **A correction, because this page used to run that argument through PFAS "
      "and the argument does not survive it.** The earlier text said perfluorinated "
      "compounds resist degradation because the carbon-fluorine bond *has no prior "
      "anywhere*, and that the contrast with antibiotics was decided *entirely* by "
      "priming. Both halves are wrong.\n"
      ">\n"
      "> There is a prior. Biology both makes and breaks carbon-fluorine bonds: "
      "*Streptomyces cattleya* synthesises fluoroacetate and 4-fluorothreonine using "
      "a dedicated fluorinase, fluoroacetate is a natural plant toxin, and "
      "fluoroacetate dehalogenase — an enzyme whose whole job is cleaving C–F — is "
      "characterised down to its crystal structure. Monofluorinated carbon is "
      "within reach of existing machinery and always has been.\n"
      ">\n"
      "> And the barrier is not only biological. The C–F bond is the strongest "
      "single bond in organic chemistry, roughly 480–530 kJ/mol, and it gets "
      "*stronger* as more fluorines crowd onto the same carbon. In a perfluoroalkyl "
      "chain the fluorine atoms are small, unpolarisable and packed around the "
      "carbon backbone, so there is no polarisable handle for an enzyme to attack "
      "and no exposed carbon to attack it on. **That inertness is not incidental to "
      "PFAS — it is the property the material was selected for**, first for seals "
      "and gaskets in uranium enrichment, later for cookware. The persistence and "
      "the usefulness are the same fact.\n"
      ">\n"
      "> So the pair varies two things at once — what machinery existed, and "
      "whether the substrate is chemically attackable at all — and a comparison "
      "that moves two variables cannot attribute the outcome to either. PFAS is "
      "not the control for the priming thesis; it is a case where priming and "
      "chemistry point the same way and cannot be separated. The claim of "
      "*entirely* is withdrawn, and the register is weaker for it. That is the "
      "correct outcome: the same standard applied elsewhere on this site applies "
      "here.\n"
      ">\n"
      "> One narrower statement does survive, and it is what E9 actually needs: no "
      "organism has been shown to mineralise a perfluoroalkyl chain at rates that "
      "matter in an environment. Partial reductive defluorination has been reported "
      "under specific engineered conditions; whole-chain breakdown in the field has "
      "not.\n")
    a("**And mutation is not random**, which most tellings of this get wrong. Rates "
      "vary by orders of magnitude across a genome with chromatin state, "
      "transcription and sequence context; stress induces mutagenesis in bacteria; "
      "recombination concentrates at hotspots rather than falling evenly; and "
      "meiosis, hybridisation and mate choice are themselves under selection and "
      "in no sense a lottery. Horizontal transfer is biased hardest of all — it "
      "delivers whatever the local gene pool happens to hold. Variation is "
      "**structured**, and the structure is itself an evolved product of what the "
      "lineage has met before. Which is priming again, one level down.\n")
    a("**The exception is real and it is not small: RNA viruses adapt the opposite "
      "way round.** Their polymerase does not proofread, so they mutate several "
      "orders of magnitude faster than anything cellular — close to the highest "
      "rate that still permits replication at all. The consequence is that most "
      "progeny are non-viable and die immediately, and the lineage exists not as a "
      "genotype but as a *cloud* of variants around one, with selection acting on "
      "the cloud. With populations of billions inside a single host and generations "
      "in hours, the waste is affordable and the sequence space explored per day is "
      "enormous.\n")
    a("So there are two adaptive strategies, and they are near-opposites. One "
      "conserves and modifies what already works, and is limited by priming. The "
      "other searches by brute force and pays for it in dead offspring, and is "
      "limited by how high the mutation rate can go before replication fails. **For "
      "the second, rate is not a secondary term — it is the entire mechanism**, and "
      "it is tuned right up against its own ceiling.\n")
    a("That has a consequence this register should carry, because it applies to "
      "`T3`, `F11` and `F12`. **A pathogen adapts faster than its host, "
      "structurally and always** — not because it is cleverer but because it sits "
      "at the far end of every one of the four terms while its host sits at the "
      "near end. Eelgrass meets its wasting disease with generations in years; the "
      "pathogen answers in days. Any argument that assumes host and parasite are "
      "racing on comparable terms is wrong before it starts.\n")
    a("These differ across organisms in the *same direction* as everything else in "
      "this section. A marine bacterium divides in hours, lives at a billion cells "
      "per millilitre, and can acquire a working gene from an unrelated species. An "
      "eelgrass meadow, a mussel bed, a long-lived bivalve: generations in years, "
      "populations in thousands, and no mechanism for borrowing an adaptation from "
      "a neighbour at all.\n")
    a("It also settles a phrase used loosely above. Calling a degraded bay "
      "*reverted to an older configuration* is right only when the state it lands "
      "in is one life is thoroughly primed for — anoxic sulphidic chemistry is "
      "ancient, universally primed, and reachable in days, so that really is "
      "reversion. A system pushed by something with no prior is not reverting to "
      "anything; there is no configuration waiting. **Whether a disturbance produces "
      "reversion or produces nothing at all is decided by what is primed**, not by "
      "how hard it is pushed.\n")
    a("> **So under any sustained novel pressure, the ceiling rises for the fast "
      "and stays put for the slow.** The gap between them widens by itself, without "
      "the pressure needing to increase. That is the asymmetry of requirements "
      "again, one level down and running on a clock.\n")
    a("Which reframes what a biocide programme is. **Applying a compound at "
      "national scale is an evolutionary selection experiment**, and the winners "
      "are decided in advance by those four terms: best primed, most biased "
      "toward the useful variation, fastest turnover. Precisely the organisms nobody "
      "intended to favour. The azole-resistant *Aspergillus* arising from "
      "agricultural fungicide use (`E15`) is not an unlucky side effect — it is the "
      "experiment working exactly as its design requires, and the resistance is "
      "simultaneously proof of exposure and proof of selection.\n")
    a("### How wide the window really is, and what that costs the argument\n")
    a("It is worth going to the far end of this, because it disciplines a phrase "
      "this project has used loosely.\n")
    a("At hydrothermal vents and cold seeps there are dense, productive, "
      "structurally complex communities living with **no sunlight at any point in "
      "the food chain**. The primary producers are chemolithotrophs oxidising "
      "hydrogen sulphide, hydrogen or methane, and the tube worms and clams above "
      "them are hosts to bacterial symbionts doing the chemistry inside their "
      "tissues. Sulphide, which is the poison in `M7` and `E12` and the thing that "
      "kills eelgrass from below in `T1`, is there the *energy source*.\n")
    a("So the window for **life** is enormously wider than the window for **the "
      "life we are talking about**. Anoxic, sulphidic, lightless water is not "
      "outside the range of the possible; it is an ancient and entirely viable mode "
      "of living, and it predates the oxygenated one by a long way.\n")
    a("> Which means *dead water* is the wrong phrase, and this project should stop "
      "reaching for it. **A degraded Danish bay is not lifeless. It has reverted to "
      "an older configuration** — one that needs fewer of the recent innovations, "
      "runs on chemistry rather than light, and supports biomass without supporting "
      "structure. That is what the convergence above is converging on, and it is "
      "not a failure of life. It is a failure of the particular arrangement we "
      "arrived in the middle of and depend on.\n")
    a("Stating it that way costs the rhetoric something and is worth it, because "
      "the alternative invites an easy and correct rebuttal — *there is plenty of "
      "life in that water* — which is true, and which a careless argument has no "
      "answer to. The claim that survives is narrower and harder to dismiss: not "
      "that life ends, but that **the slow, structured, long-lived, oxygen- and "
      "light-dependent part of it does**, and that this part is the one carrying "
      "everything anybody values.\n")

    a("It also sharpens the dose argument. A concentration too low to kill the "
      "target is not thereby harmless: **sublethal is the regime where selection is "
      "strongest**, because it kills enough to matter and spares enough to breed. "
      "Which is why total load and ubiquity matter more than per-application "
      "concentration, and why the antibiotic instrument — reserve it, do not "
      "disperse it — is the right shape of response.\n")
    a("And it is the exact argument behind the evolutionary-prior framework in "
      "[PROGRAMME.md](#PROGRAMME.md). A molecule life has met before has left "
      "machinery for handling it somewhere in the biosphere; a genuinely novel one "
      "has not, and there is no prior to draw on. The difference between those two "
      "is not chemistry — it is history.\n")

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

    a("### Who actually runs the chemistry\n")
    a("A note on which organisms this register is about, because the categories in "
      "use mislead. Eukaryotes — plants, animals, fungi, and the microbial "
      "supergroups with no common name — dominate two things: the catalogue of "
      "described species, and visible form. On every other measure the prokaryotes "
      "win, and it is not close.\n")
    a("**Metabolically it is not a contest.** Eukaryotes do essentially two things: "
      "aerobic respiration, and oxygenic photosynthesis borrowed wholesale from a "
      "captured cyanobacterium. Bacteria and archaea do everything else. Every "
      "redox step in this entire register is theirs — nitrification, "
      "denitrification, anammox, sulphate reduction, sulphide oxidation, iron and "
      "manganese reduction, methanogenesis, methane oxidation. The electron "
      "acceptor cascade of `R5`, the sediment phosphate release of `R6`, the "
      "nitrogen sink that flips to a source under hypoxia — all prokaryotic, and "
      "**none of it done by anything any Danish marine survey counts**.\n")
    a("The species count runs the other way — roughly two million described "
      "eukaryotes against some twenty thousand formally described prokaryotes — but "
      "that is an artefact of the species concept and of what will grow in a dish. "
      "Over ninety-nine per cent of prokaryotes will not, and they do not have "
      "biological species in the first place.\n")
    a("**And this axis does close.** Metabolic type is a cross-product of four "
      "short, enumerable factors, which is the same shape of argument as the "
      "chemical window:\n")
    a("| factor | the options | |")
    a("|---|---|---|")
    a("| Energy source | light, or chemical reaction | *photo-* / *chemo-* |")
    a("| Electron donor | inorganic, or organic | *litho-* / *organo-* |")
    a("| Carbon source | CO₂, or organic carbon | *auto-* / *hetero-* |")
    a("| Terminal electron acceptor | O₂ → NO₃⁻ → Mn(IV) → Fe(III) → SO₄²⁻ → S⁰ → "
      "CO₂ | in falling energy yield |")
    a("")
    a("Eight combinations of the first three, of which about six are realised in "
      "nature, times a terminal-acceptor list that is essentially complete for "
      "natural waters. **That is an exhaustive classification of how anything makes "
      "a living**, and unlike the taxonomy it does not depend on anyone having "
      "named the organism. It is the right level at which to argue about "
      "biogeochemistry, and the wrong level is the one the monitoring forms use.\n")
    a("The taxonomic list, for completeness and with the caveat that the eukaryote "
      "part is genuinely unsettled: **Bacteria**; **Archaea**; and **Eukarya**, "
      "which divides into Amorphea (animals and fungi together, plus amoebae), "
      "Archaeplastida (plants and the green and red algae), SAR (stramenopiles, "
      "alveolates, rhizarians — diatoms, kelp, oomycetes, labyrinthulids, "
      "dinoflagellates, ciliates, foraminifera), and several smaller groups whose "
      "placement moves between papers. **Viruses** sit outside the tree entirely and "
      "are, by `F11`, a major agent of mortality regardless.\n")

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
      "the error lay in the assumed original state. That is group `L`, and it is the "
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

    # One glossary, generated from the same tuples the pages are, so a definition
    # exists in exactly one place and every reference to it anywhere on the site
    # stays in step. The reader looks ids up in this at render time rather than
    # the documents carrying their definitions inline.
    gloss = {}

    def add(i, kind, label, text):
        gloss[i] = {"kind": kind, "label": label, "text": " ".join(text.split())}

    for i, n, w in TERMINAL:
        add(i, "terminal outcome", n, w)
    for i, n, w, r, g, cm, ce in AVENUES:
        add(i, "categorical avenue", n, w)
    for i, n, w in ROUTES:
        add(i, "route", n, w)
    for i, n, w in UNQUANTIFIABLE:
        add(i, "unquantifiable", n, w)
    for i, n, w in OUTCOMES:
        add(i, "observable", n, w)
    for g, n, t in GROUPS:
        add(g, "group", n, t)
    for h, g, t, o, m, p_, d_, nd in rows:
        add(h, f"hypothesis ({g})", t, m)

    # Scoped on purpose. Register ids are short and collide with real identifiers
    # elsewhere on the site - REGISTER.md lists sewer outfalls called U2 and U4,
    # and glossing those as "acute peaks under chronic means" would be worse than
    # no tooltip at all. Only documents that speak this vocabulary opt in.
    gloss["_docs"] = ["HYPOTHESES.md", "EXPERIMENTS.md", "DATA_QUEUE.md",
                      "OXYGEN.md", "OBSERVING.md", "AREAS.md",
                      "PROGRAMME.md", "LIGHT.md"]
    # variants() is generous on purpose - it is easier to over-generate and then
    # discard than to guess the right morphology. So keep only the forms that
    # actually occur in the documents; the glossary then carries the words a
    # reader will really meet, and the browser's regex stays small.
    corpus = ""
    for f in gloss["_docs"]:
        fp = os.path.join(ROOT, "docs", f)
        if os.path.exists(fp):
            corpus += open(fp, encoding="utf-8").read().lower() + "\n"
    present = set(re.findall(r"[a-zæøå]+", corpus))
    gloss["_terms"] = {}
    for t, (a_, b_) in TERMS.items():
        forms = [v for v in variants(t)
                 if all(w in present for w in v.split()) or v.lower() in corpus]
        gloss["_terms"][t] = {"text": a_, "why": b_,
                              "forms": sorted(set(forms) | {t.lower()})}
    write_json(os.path.join(ROOT, "docs", "data", "glossary.json"), gloss)
    log(f"  glossary: {len(gloss) - 2} ids, {len(TERMS)} terms")
    write_doc(OUT, render(rows))
    log(f"wrote docs/HYPOTHESES.md ({os.path.getsize(OUT):,} chars)")
    log(f"  {len(rows)} hypotheses across {len(GROUPS)} groups, "
        f"{len(OUTCOMES)} outcomes kept apart")
    from collections import Counter
    for g, n in sorted(Counter(r[1] for r in rows).items()):
        log(f"    {g}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
