#!/usr/bin/env python3
"""Generate docs/SENSING.md - a dense network for the thing nobody measures.

A design page: the fingerprint that would attribute a stream's load to its sources,
the two-tier network that could carry it, and what keeps it alive. Every number is
read from data or a pinned document, and every assertion is a checked claim
(LIVE_NUMBERS.md section 11), registered in data/manual/claims.d/w3-ss.json with what
it rests on. The page gives no prices, because none had a source; parts are named by
class, with an example only where the maker's own page is pinned. What the page once
said and could not justify is in docs/ARCHIVE.md, not here.

    python3 scripts/pages/sensing.py

Writes docs/SENSING.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import ROOT, log, write_doc
import claims as _claims
import live

OUT = os.path.join(ROOT, "docs", "SENSING.md")
C, B, E = live.claim, live.claim_begin, live.CLAIM_END
_REG = {}


def _cl():
    if "d" not in _REG:
        _REG["d"] = _claims.load()[0]
    return _REG["d"]


def RD(sid, value, phrase):
    """A number read from a pinned document, refused unless the pinned copy holds the
    phrase (tags set aside and entities read, as the claims register compares it).
    Each reading gets its own phrase: two readings with one phrase would share an id."""
    d = _cl()
    if _claims._flat(phrase) not in _claims._flat(_claims.pin_text(d, sid)):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    return live._mk(value, ["reading", sid, "phrase", phrase, _claims._meta(d, sid)])


def J(*parts):
    return live.live_json(os.path.join(ROOT, *parts))


def render():
    mon = J("data", "manual", "monitoring.json")["diffuse_load"]
    meas, mod, stations = mon["area_measured_pct"], mon["area_modelled_pct"], mon["stream_stations"]
    danva = RD("DANVA-2024", 69.6, "hvor landbruget alene står for 69,6 %")
    hi = RD("SS-WIKI-COPRO", 0.7,
            "Samples with ratios greater than 0.7 may be contaminated with human faecal matter")
    lo = RD("SS-WIKI-COPRO", 0.3, "samples with values less than 0.3 may be considered uncontaminated")
    ww = RD("SS-WIKI-COPRO", 2.6, "Community wastewater 2.6 – 4.1")
    ab = RD("SS-WIKI-COPRO", 0.9, "Abattoir – sheep, cattle 0.5 – 0.9")
    n10 = RD("SS-USGS-KENDALL", 10,
             "converted to nitrate with d 15 N values generally in the range of +10")
    n20 = RD("SS-USGS-KENDALL", 20, "values generally in the range of +10 to +20")
    n0 = RD("SS-USGS-KENDALL", 0, "fertilizers produced from atmospheric nitrogen with compositions of 0")
    sp_lo = RD("SS-PMC-MST-REV", 66, "Pig-2-Bac 75 – 100 66")
    sp_hi = RD("SS-PMC-MST-REV", 100, "Pig-2-Bac 75 – 100 66 – 100")
    lfp = live.chem("LiFePO4")

    o = []
    w = o.append
    w("# A dense network for the thing nobody measures")
    w("")
    w(B("C-SS-S-X23") + "[`X23`](EXPERIMENTS.md) asks whether the faecal payload reaches the "
      "water or is spent in the soil, and designs an answer from event sampling at paired "
      "stream catchments." + E + " " +
      C("C-SS-S-PURPOSE", "This page asks the harder version of the same question: **what "
        "would it take to measure it everywhere**, so that no result anywhere has to be "
        "extrapolated to a place nobody visited."))
    w("")
    w("That is the whole point. " +
      C("C-SS-S-AREA", f"Denmark's diffuse load figure rests on catchment area that is "
        f"{meas}% measured and {mod}% modelled ([NITROGEN.md](NITROGEN.md))") + ", and " +
      C("C-SS-S-OBJECTION", "the objection this project keeps making is not that the model "
        "is bad but that **a partition is not a measurement**. A network dense enough to have "
        "a node on every stream that reaches the sea would end that argument by removing its "
        "subject."))
    w("")
    w(C("C-SS-S-DESIGN", "**This page is a construction, not a proposal anyone has funded**, "
        "and nothing here has been built by this project.") + " " +
      C("C-SS-S-NOPRICE", "The parts are named by class, with an example where the maker's "
        "own page could be pinned, and no price is given: a price is worth printing only with "
        "its source, and what a buyer needs is a supplier's quotation. What the page is for is "
        "to make the thing concrete enough that a disagreement about it is a disagreement "
        "about parts and procedures."))
    w("")
    w("---")
    w("")
    w("## The fingerprint, in place of a sensor for the source")
    w("")
    w(C("C-SS-F-IDEA", "No sensor on this page reports *manure*, so the alternative is to "
        "measure many things and ask which combination only manure produces. That is a "
        "fingerprint: **not a measurement but a position in a measurement space**, and the "
        "question for each candidate tracer is not *is it present* but *what else could have "
        "put it there*."))
    w("")
    w("### The tracers, and what each one rules out")
    w("")
    w("- " + C("C-SS-F-COPRO", "**Coprostanol** (`5β-cholestan-3β-ol`). Intestinal bacteria "
               "make it from cholesterol in the gut of most higher animals, and it is used as a "
               "biomarker of human faecal matter. So it marks faeces, but any warm-blooded gut "
               "can have put it there; the ratios below narrow it down."))
    w("- " + C("C-SS-F-RATIO", "**Coprostanol / (coprostanol + cholestanol).** Cholestanol "
               "forms in the environment by bacteria and generally has no faecal origin, so the "
               f"share of coprostanol measures faecal contamination: above {hi} a sample may be "
               f"contaminated with human faecal matter, below {lo} it may be considered "
               "uncontaminated, and in between the ratio alone cannot place it."))
    w("- " + C("C-SS-F-ETHYL", "**Coprostanol / `24-ethylcoprostanol`.** Herbivores such as "
               "cows and sheep eat plant sterols, which their gut bacteria turn into "
               "`24-ethylcoprostanol`, a biomarker of herbivore faeces. In the values the source "
               f"tabulates, community wastewater has a ratio of {ww} or more and abattoir waste "
               f"from sheep and cattle {ab} or less, so the ratio separates human sewage from "
               "cattle and sheep. **Nothing found reports it for pigs**, which are not "
               "herbivores, so for pig slurry it is untested here."))
    w("- " + C("C-SS-F-HOST", "**Host-specific *Bacteroidales* by qPCR** — `HF183` for people, "
               "`Pig-2-Bac` for pigs. qPCR quantifies genetic markers specific to the host of "
               "the bacteria, and detects recent contamination rather than old. **This is the "
               "attribution instrument, and it is not clean**: the human method's own "
               "documentation warns that some non-human animals shed its target and asks for a "
               "specificity test on local source material, and validation studies report "
               f"`Pig-2-Bac`'s specificity anywhere from {sp_lo}% to {sp_hi}%."))
    w("- " + C("C-SS-F-CRASS", "**crAssphage.** CrAss-like phages are the most abundant "
               "viruses in the human gut and have been evaluated as a marker for sewage "
               "pollution. They establish the human baseline, so the rest can be assigned "
               "elsewhere."))
    w("- " + C("C-SS-F-HUMANCHEM", "**Acesulfame-K, carbamazepine.** Acesulfame is excreted "
               "largely unchanged, is hardly removed in treatment plants, and is used as a "
               "wastewater marker in surface water and groundwater; carbamazepine, an "
               "anticonvulsant medicine, has been found in treatment-plant effluent. They mark "
               "the human fraction independently of biology — a chemical crosscheck on the "
               "microbial one."))
    w("- " + C("C-SS-F-VET", "**Tylosin, tetracyclines, ivermectin.** Tylosin is an antibiotic "
               "feed additive of veterinary medicine; oxytetracycline is used in cattle, "
               "chickens, swine and turkeys; ivermectin was given massively to cattle, sheep and "
               "other animals. They mark the livestock fraction, and VetStat, the national "
               "statistics of veterinary medicine, holds the sales that would calibrate it — in "
               "public only by substance group, species and region."))
    w("- " + C("C-SS-F-METALS", "**Copper and zinc.** Zinc oxide has been given to piglets in "
               "their feed against post-weaning diarrhoea, and the European Medicines Agency's "
               "veterinary committee found that its benefit did not outweigh the risk to the "
               "environment; but copper is in brake pads and zinc on galvanised roofs. So the "
               "metals are useless alone in a mixed catchment, useful in a rural one, and useful "
               "as a *load* once the fraction is known."))
    w("- " + C("C-SS-F-D15N", "**δ¹⁵N of nitrate.** Nitrate from animal and human waste is "
               f"isotopically heavy, generally +{n10} to +{n20}‰, and fertiliser made from "
               f"atmospheric nitrogen sits near {n0}‰; human and animal waste are "
               "indistinguishable under most circumstances, so this separates waste from "
               "fertiliser, not pig from person. **Denitrification enriches δ¹⁵N too**, since it "
               "takes the lighter isotope and leaves the heavier. Measure **δ¹⁸O of nitrate "
               "alongside it**: during denitrification the two rise in an apparently constant "
               "ratio, and mixing of sources does not follow it."))
    w("- " + C("C-SS-F-FDOM", "**fDOM, tryptophan-like (peak T) against humic-like (peak "
               "C).** Protein-like fluorescence comes mostly from tryptophan and tyrosine; "
               "treatment-plant effluent is rich in it, manure leaves its own fluorescent "
               "fingerprint, and tryptophan-like fluorescence can indicate wastewater "
               "contamination, while peak C counts as a terrestrial source. Turbidity and "
               "temperature interfere and have to be corrected for. Field fluorometers read it "
               "continuously, which makes it the one dimension here that can run in the stream "
               "— which is its whole value."))
    w("")
    w("### The quantifier")
    w("")
    w(C("C-SS-Q-MIX", "**There is no single number that is \"the faecal load\", and a page "
        "that offered one would be doing what this project spends its length objecting to.** "
        "What there is, is a mixing model with an uncertainty on it:"))
    w("")
    w("1. " + C("C-SS-Q-1", "Pick **end members** — pig slurry, cattle slurry, human sewage, "
                "soil organic matter, and if the catchment has one, treated effluent. Each is "
                "sampled directly, so its own fingerprint is measured rather than assumed."))
    w("2. " + C("C-SS-Q-2", "Solve for the **fractions** that reproduce the observed tracer "
                "vector at the stream. With more tracers than sources the system is "
                "over-determined, which is what allows an *estimate of error* rather than only "
                "an answer."))
    w("3. " + C("C-SS-Q-3", "Multiply the faecal fraction by the **measured load** — "
                "concentration times discharge at the same minute — to get mass per event, per "
                "season, per year."))
    w("")
    w(C("C-SS-Q-KG", "So the quantifier is **kilograms of pig-derived organic matter past this "
        "point in this storm**, with a confidence interval, and it decomposes into the same "
        "units for cattle, for people, and for soil.") + " " +
      C("C-SS-Q-ABSENT", "None of the monitoring and data sources this project has profiled "
        "carries that number, and none measures a faecal sterol, a host-specific marker or "
        "crAssphage, so none holds the end members it needs."))
    w("")
    w("### General sensors give totals; discriminating tracers give shares")
    w("")
    w(C("C-SS-G-BOTH", "The two kinds of measurement do different jobs and the design needs "
        "both, which is worth saying plainly because a network of only one kind is a waste of "
        "money."))
    w("")
    w("- " + C("C-SS-G-GENERAL", "A **general observable** — turbidity, COD, total nitrogen, "
               "oxygen — measures *how much of something is here*, and cannot say where it came "
               "from. Where a sensor reads it, the sensor is bought once and reads "
               "continuously, and it is the quantity that actually matters to a fjord."))
    w("- " + C("C-SS-G-DISCRIM", "A **discriminating tracer** — coprostanol, `Pig-2-Bac`, "
               "acesulfame, δ¹⁵N — measures *whose it is*, and by itself says nothing about "
               "magnitude. Each reading is a laboratory analysis of a sample, so it is "
               "expensive per reading, episodic, and useless as a load."))
    w("")
    w(C("C-SS-G-PRODUCT", "**The product of the two is what none of the sources this project "
        "profiled has.** A discriminating tracer that rises in proportion to the material "
        "carrying it converts a total into a share: measure the tracer, apply the ratio of "
        "tracer to bulk in that source, and you have the fraction of the total that came from "
        "it — in kilograms, at that minute, past that point."))
    w("")
    w("### Which lets you subtract, one source at a time")
    w("")
    w(C("C-SS-G-SUBTRACT", "That is the operating principle, and it generalises past faeces to "
        "every pathway on this site:"))
    w("")
    w("1. " + C("C-SS-G-S1", "**Measure the totals continuously** with the cheap sensors, "
                "everywhere."))
    w("2. " + C("C-SS-G-S2", "**Measure the fingerprint episodically** at the same points, and "
                "convert each resolved source into its contribution to each total."))
    w("3. " + C("C-SS-G-S3", "**Subtract it.** What is left is a residual with one fewer "
                "explanation in it."))
    w("4. " + C("C-SS-G-S4", "**Repeat for the next fingerprint** — road runoff by its own "
                "markers, human sewage by acesulfame and crAssphage, industrial by whatever is "
                "specific to it — and each subtraction cleans the residual the next estimate is "
                "made on."))
    w("")
    w(C("C-SS-G-DECOMP", "Done across enough tracers, the outcome is a **decomposition of the "
        "load rather than an attribution of it**: this much of tonight's oxygen demand was pig, "
        "this much human, this much road, this much soil, and this much is still "
        "unexplained."))
    w("")
    w("> " + C("C-SS-G-RESIDUAL", "**And the last number is the honest one.** This method is "
               f"the residual method — the same operation the {danva}% figure is built on, "
               "which this project spends [NITROGEN.md](NITROGEN.md) taking apart. It is only "
               "better if it obeys rules the original does not: **every subtraction is a "
               "measurement rather than a model**, **the error propagates and is published with "
               "the number**, and **the final residual is never named after a source.** An "
               "unexplained remainder is an unexplained remainder. The moment it gets called "
               "*agriculture*, this becomes the thing it was built to replace."))
    w("")
    w(C("C-SS-G-PROPORTION", "**The proportionality is an assumption and has to be measured, "
        "not asserted.** Nothing guarantees that a tracer stands in the same ratio to the bulk "
        "in every tank, and the tracers age differently: host markers detect recent "
        "contamination, while coprostanol converts only slowly in the environment and in "
        "anaerobic sediment lasts long enough to record past faecal discharges. So each ratio "
        "is established by sampling the end members directly — the tank, the plant effluent, "
        "the road gully — and re-established when the system changes. A conversion factor "
        "taken from a paper about another country's pigs is exactly the kind of borrowed "
        "coefficient this project objects to everywhere else."))
    w("")
    w("### Why a fingerprint is more trustworthy than any of its dimensions")
    w("")
    w(C("C-SS-G-AGREE", "Each tracer above has a confounder. The design answer is not a better "
        "tracer, it is **agreement across independent measurement spaces**: sterol chemistry, "
        "microbial genetics, pharmaceutical chemistry, stable isotopes and optics fail in "
        "unrelated ways, so a source assignment that survives all of them is not an artefact "
        "of any one. A signal visible in one dimension and absent from the others is noise "
        "wearing a name — and the discipline that says so is the same one this project applies "
        "to [partitions and baskets](https://github.com/Jjokulian/statistical-methods): **a "
        "boundary that holds under every metric you try is the only kind worth calling "
        "real.**"))
    w("")
    w(C("C-SS-G-PERSITE", "That has a practical consequence for the network below. The dense "
        "tier measures the cheap, continuous, ambiguous dimensions; the sparse tier measures "
        "the expensive, unambiguous ones; and **the calibration between them is per-site, not "
        "national**. The continuous proxies are trusted only where the laboratory has stood in "
        "the same water."))
    w("")
    w("---")
    w("")
    w("## Which is why the architecture is forced")
    w("")
    w(C("C-SS-A-FORCED", "**No sensor in this design reports \"manure\".** What it has is the "
        "fingerprint above, and it splits cleanly by what can be automated: the continuous "
        "dimensions are cheap per reading and ambiguous; the dimensions that identify a source "
        "are laboratory analyses of a sample. So the architecture is forced, and it is "
        "two-tier:"))
    w("")
    w("- " + C("C-SS-A-T1", "**Tier 1 — dense, continuous, cheap per reading.** Says **when "
               "and where** something moved, at every site, all the time; cannot say **what** "
               "it was."))
    w("- " + C("C-SS-A-T2", "**Tier 2 — sparse, event-triggered, expensive per sample.** Says "
               "**what it was**, by laboratory attribution; cannot be everywhere."))
    w("")
    w(C("C-SS-A-COUPLING", "Tier 1 without tier 2 is a network of interesting wiggles. Tier 2 "
        "without tier 1 is the existing monitoring programme: grab samples at fixed intervals, "
        "from which transport came out underestimated against intensive daily measurement in "
        "every stream of the 2018 study this project records. **The design is the coupling** — "
        "tier 1 decides when tier 2 fires."))
    w("")
    w("---")
    w("")
    w("## Tier 1 — the node")
    w("")
    w(C("C-SS-N-INTRO", "The node carries these measurements, each for a reason:"))
    w("")
    w("- " + C("C-SS-N-STAGE", "**Water level** — an ultrasonic ranger above the surface, such "
               "as MaxBotix's weather-resistant `MB7389`, or a vented pressure transducer where "
               "there is no overhead mounting. Without discharge there is no load, only a "
               "concentration: this is the sensor that turns the network from anecdote into "
               "accounting. Mounted in air, an ultrasonic head is not in the water and cannot "
               "foul; a pressure transducer's cable must be vented, or it reads the weather."))
    w("- " + C("C-SS-N-TURB", "**Turbidity** — nephelometric, which measures light scattered "
               "at right angles, in the formazin units of the `ISO 7027` method, with a wiper. "
               "The carrier: viruses and bacteria attach to suspended solids, so turbidity is "
               "the proxy for *payload in transit*."))
    w("- " + C("C-SS-N-EC", "**Conductivity and temperature** — for example Atlas Scientific's "
               "EZO conductivity kit with a `K 1.0` probe. Separates dilution from delivery: a "
               "storm that dilutes conductivity while raising turbidity is surface wash; a rise "
               "in both is something else. Temperature corrects the other readings, fluorescence "
               "among them."))
    w("- " + C("C-SS-N-FDOM", "**fDOM — tryptophan-like fluorescence**, with a humic-like "
               "channel if affordable. The one fingerprint dimension that runs continuously, and "
               "the difference between a turbidity network and a fingerprint network."))
    w("- " + C("C-SS-N-DO", "**Dissolved oxygen** — an optode, which reads oxygen optically, "
               "not an electrochemical cell, which in larger sizes drifts as it consumes its "
               "electrolyte. The receiving-water consequence, at the same minute as the "
               "cause."))
    w("")
    w(C("C-SS-N-BORING", "**Logger, power and communications** are the boring part and the "
        "part that decides whether the thing survives a winter:"))
    w("")
    w("- " + C("C-SS-N-LOGGER", "**Logger and radio** — an `ESP32`-class microcontroller with a "
               "real-time clock, a memory card and a watchdog; LoRaWAN to a community gateway "
               "where one is in range, since LoRa carries far at low power, and a mobile data "
               "link where none is. It logs locally as well as transmits, so a dropped link "
               "loses no data."))
    w("- " + C("C-SS-N-POWER", f"**Power** — a solar panel, a charge controller and a {lfp} "
               "battery, sized for a Danish December, not July."))
    w("- " + C("C-SS-N-BOX", "**Enclosure and mount** — a sealed box (`IP67`), cable glands, a "
               "stainless bracket and desiccant, mounted to a road culvert or a bridge "
               "parapet."))
    w("")
    w(C("C-SS-N-KIT", "**The kit a group shares:** formazin turbidity standards, conductivity "
        "calibration solutions and an oxygen zero solution, because **a reading without a "
        "calibration record is not data**; a reference sonde, borrowed or shared, for "
        "co-location, which is [`X16`](EXPERIMENTS.md), the check that ties cheap readings to "
        "the national record; and spare probes, cable and one spare node, because field "
        "repairs happen in February in the rain."))
    w("")
    w(C("C-SS-N-SAMPLER", "**The sampler, which is where the answer comes from:** a field "
        "autosampler for water-quality samples, triggered by flow and turbidity, and the bottle "
        "analysis — sterols, host markers, crAssphage, acesulfame, one veterinary residue, "
        "copper and zinc, COD and BOD, nutrients, δ¹⁵N with δ¹⁸O. Not every bottle needs the "
        "full panel: the routine determinands go on all of them and the fingerprint on the "
        "ones the continuous tier says matter."))
    w("")
    w("---")
    w("")
    w("## Tier 2 — the sampler that answers the question")
    w("")
    w(C("C-SS-T2-ATTR", "An automatic sampler, triggered by tier 1 when stage or turbidity "
        "crosses a threshold, fills bottles through the rising and falling limb of a storm. "
        "**This is where the attribution comes from**, because the attributing measurements "
        "are laboratory analyses:"))
    w("")
    w("- " + C("C-SS-T2-STEROL", "**faecal sterols** — coprostanol, and its ratio to "
               "cholesterol, which marks faecal contamination;"))
    w("- " + C("C-SS-T2-HOST", "**host-specific microbial markers** (pig-, ruminant- and "
               "human-associated *Bacteroidales* by qPCR), which distinguish a pig from a person "
               "— the measurement that makes the argument attributable rather than suggestive, "
               "once its specificity is tested on local material;"))
    w("- " + C("C-SS-T2-METALS", "**copper and zinc**, zinc from piglet feed among its "
               "sources;"))
    w("- " + C("C-SS-T2-VET", "**one veterinary antiparasitic residue**, because the register "
               "that holds the sales data holds nothing about where it went;"))
    w("- " + C("C-SS-T2-COD", "**COD and BOD**, to tie the fluorescence proxy to a standard "
               "number."))
    w("")
    w(C("C-SS-T2-SPARSE", "Each bottle is a laboratory analysis paid for one at a time, which "
        "is why tier 2 is sparse and event-triggered rather than continuous: samplers rotate "
        "around a network of nodes."))
    w("")
    w("---")
    w("")
    w("## Does it really have to be bottles?")
    w("")
    w(C("C-SS-B-PARTLY", "Partly, and the honest answer is not one answer: some of it needs a "
        "laboratory, some is already automated, and some is being automated now."))
    w("")
    w(C("C-SS-B-LAB", "**What needs a laboratory.** The discriminating chemistry and genetics: "
        "faecal sterols extracted from the sample, host-specific markers by qPCR, veterinary "
        "residues by liquid chromatography, nitrate isotopes by mass spectrometry. At a stream "
        "node, attribution means a bottle."))
    w("")
    w(C("C-SS-B-AUTO", "**What is already automated and is not bottles at all.** The node's own "
        "sensors — level, turbidity, conductivity, temperature, optical oxygen and "
        "fluorescence — need no bottle: each reads a property of the water where it stands, "
        "continuously."))
    w("")
    w(C("C-SS-B-ROBOT", "**What is being automated now.** Robotic sample processors that "
        "collect and analyse water samples in place exist and are deployed: one was the first "
        "underwater instrument to detect a harmful algal species and its toxin autonomously. "
        "They are a different machine from this page's node, and this page does not price "
        "them."))
    w("")
    w("### Which changes what the bottles are *for*")
    w("")
    w("> " + C("C-SS-B-RULE", "**Bottles calibrate the network. They do not monitor it.**"))
    w("")
    w(C("C-SS-B-CALIBRATE", "That is the design's central rule. At a site, a season of event "
        "bottles establishes the local relation between the cheap continuous dimensions — "
        "fluorescence, turbidity, conductivity — and the laboratory panel. Once that relation "
        "holds, **the sensors carry the estimate between calibrations** and the bottles fall "
        "back to validation: enough to confirm the relation has not drifted, and a fresh round "
        "whenever something changes upstream."))
    w("")
    w(C("C-SS-B-SCALE", "So the bottle count scales with **sites × recalibrations**, not with "
        "events forever, and the bottle line bends down once the calibration phase ends rather "
        "than running flat.") + " " +
      C("C-SS-B-DIALS", "[The network page](network.html) has a dial for each — how long the "
        "calibration phase lasts, and what share of the sampling continues afterwards — because "
        "the honest answer depends on how stable the relation turns out to be, and none of the "
        "sources this project profiled reports that for a Danish stream."))
    w("")
    w(C("C-SS-B-RESULT", "**And if the relation never stabilises at a site, that is a result "
        "rather than a setback.** It would mean the payload arrives in forms the cheap sensors "
        "cannot see, which is worth knowing and is exactly the kind of thing a monitoring "
        "programme designed around a fixed determinand list would never discover."))
    w("")
    w("---")
    w("")
    w("## At every outlet")
    w("")
    w("> " + C("C-SS-Z-DIAL", "**[Dial it yourself →](network.html)** — the density on a map "
               "of Denmark, what each node carries, the sampler ratio, the bottle price, the "
               "servicing interval and the years, with a total that moves as you change them. "
               "Its default prices are the tool's own and have no source this project could "
               "find; replace them with quotations."))
    w("")
    w(C("C-SS-Z-TARGET", "A node on every Danish stream that reaches the sea is the target that "
        "removes extrapolation entirely. Whatever the hardware costs, it is bought once; what "
        "recurs is this:"))
    w("")
    w("- " + C("C-SS-Z-SERVICE", "**Servicing.** A fouled sensor produces confident wrong "
               "numbers, which is worse than no sensor. Visit on a schedule, and prefer the "
               "sensor that fouls least even where it reads worst."))
    w("- " + C("C-SS-Z-CALIB", "**Calibration.** Every node needs a documented calibration "
               "history and a co-location against a reference instrument — which is "
               "[`X16`](EXPERIMENTS.md), already written."))
    w("- " + C("C-SS-Z-LAB", "**Laboratory.** The tier-two bottles, a cost per analysis for as "
               "long as the network is calibrated."))
    w("")
    w("---")
    w("")
    w("## The data path, which is the easy part")
    w("")
    w("    node ──LoRaWAN/NB-IoT──▶ gateway ──MQTT──▶ broker ──▶ time-series store")
    w("                                                            │")
    w("                                              raw archive ──┼──▶ public API")
    w("                                                            └──▶ static site")
    w("")
    w(C("C-SS-D-STACK", "Concretely: an MQTT broker on a small VM, a time-series database, a "
        "nightly dump of raw readings to object storage, and a static site generated from it — "
        "the same shape as this repository, which is built from public data by scripts and "
        "hosted free as a static site. **Software is not the constraint.**"))
    w("")
    w(C("C-SS-D-RULES", "These rules matter more than the stack:"))
    w("")
    w("1. " + C("C-SS-D-R1", "**Log locally as well as transmit.** A link that drops then "
                "loses nothing."))
    w("2. " + C("C-SS-D-R2", "**Publish raw counts, not just calibrated values.** A "
                "recalibration must be reproducible after the fact, which means the uncalibrated "
                "series has to survive."))
    w("3. " + C("C-SS-D-R3", "**Every reading carries its node's calibration state and last "
                "service date.** A series without that is not evidence."))
    w("4. " + C("C-SS-D-R4", "**Public API from day one, and open licence.** An open record is "
                "one a reader who trusts neither side can check."))
    w("5. " + C("C-SS-D-R5", "**Never publish an index without the series it came from.** That "
                "is the failure this whole project documents, and it would be humiliating to "
                "reproduce it."))
    w("")
    w("---")
    w("")
    w("## What one person can do, and what needs many")
    w("")
    w(C("C-SS-P-ONE", "**One person can build a node, mount it on a culvert, and produce a "
        "defensible record of one stream.** That is not a small thing: it is one place, "
        "measured, with a date — and [the argument this project makes about "
        "plurality](PLACES.md) is that a place measured is worth more than a place "
        "modelled."))
    w("")
    w(C("C-SS-P-SHAPE", "**What one person cannot do is cover a country**, and the spread is "
        "the whole value. The network's power is that it removes extrapolation, and it only "
        "removes it where somebody stood in the water. So the shape of it is many people with "
        "one node each and a shared protocol, not one institution with a plan."))
    w("")
    w(C("C-SS-P-SHARED", "What would have to be shared for that to work is not hard: **the "
        "build**, so nodes are comparable; **the calibration protocol**, so their readings are; "
        "and **the archive**, so a result belongs to everyone rather than to whoever hosted "
        "it."))
    w("")
    w("---")
    w("")
    w("## What it becomes: a live picture, and the work as tasks")
    w("")
    w(C("C-SS-G-PICTURE", "**The goal of digitising the collection is one live, shared picture.** "
        "Every node's readings flow into one open archive as they are taken and appear on one map, "
        "each carrying its node, its time, its calibration state and its last service date."))
    w("")
    w(C("C-SS-G-WATCH", "**The picture is watched, not only stored.** A node that falls silent, drifts "
        "from its neighbours or passes its calibration date is flagged when it happens, not found at "
        "the end of a season."))
    w("")
    w(C("C-SS-G-TASKS", "**And the work the network needs is presented as tasks anyone can take:** "
        "a node to service, a sample to collect after a rain event, a calibration due, a stretch of "
        "water with no node at all - each with a place, a deadline and what it would add to the "
        "record."))
    w("")
    w(C("C-SS-G-SHAPE", "In shape this borrows from two kinds of system built outside science. "
        "Military command software fuses many sensors into one picture: Anduril's Lattice is "
        "described as a platform that classifies objects *by fusing data from disparate sensors*. "
        "Volunteer mapping gathers what no institution will: DeFlock *uses OpenStreetMap data to "
        "populate a map with crowdsourced locations* of licence-plate cameras. Pointed at the water, "
        "open, and with every reading traceable to the node that made it, the same shape is a "
        "crowdsourced platform for a scientific record."))
    w("")
    w("---")
    w("")
    w("## What this would and would not settle")
    w("")
    w(C("C-SS-W-WOULD", "**Would.** Whether the payload moves in events, where, how often, and "
        f"in what season — across the whole country rather than at {stations} stream stations "
        "sampled at fixed intervals. Whether the spreading window shows up in the water. Which "
        "catchments are quiet and which are not, without a model in between."))
    w("")
    w(C("C-SS-W-WOULDNOT", "**Would not.** Anything about the sea beyond the outlet: this "
        "measures what arrives, not what it does. Anything the tier-two list does not include. "
        "And **it does not abolish inference** — attribution still travels from sampled events "
        "to unsampled ones, and from a marker to a source. What it abolishes is *spatial* "
        "extrapolation, which is the one this project has spent its length objecting to."))
    w("")
    w("> " + C("C-SS-W-SUMMARY", "**The honest summary.** The instruments exist, the protocol "
               "is ordinary, and none of the sources this project profiled reports a network "
               "like it. That is not a technical finding. It is a statement about what the "
               "monitoring system was built to answer, and about who has been allowed to "
               "ask."))
    return "\n".join(o).rstrip("\n") + "\n"


def main():
    try:
        write_doc(OUT, render())
    except (live.Unjustified, _claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
