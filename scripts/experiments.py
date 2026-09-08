#!/usr/bin/env python3
"""Things you could just go and do, with a control, and know the answer.

Most of what this project has marked untestable is untestable *with existing
monitoring*, which is a different claim. A national observing programme answers
questions about what is happening. A manipulation with a control answers questions
about what causes what, and several of the open questions here yield to one that
would fit in a season and a small boat.

The distinction matters because a study and an experiment fail differently. A study
of existing data can always be argued with - the confounders are real, the record
is short, the aggregation lost the signal. An experiment with a control and a
decision rule written in advance either falsifies the hypothesis or does not.

So each entry names, before anything is run:

    settles       which hypotheses in HYPOTHESES.md it bears on
    manipulate    the thing you change
    controls      the thing you change it against - and the controls are the design
    measure       the observable
    decide        what each outcome means, fixed in advance
    scale         who could run it, and roughly what it costs

The recurring design element is the **sterilised control**: the same material,
autoclaved or gamma-irradiated, alongside the live one. It separates "the chemistry
of this stuff" from "the organisms in it" in a single step, and that is precisely
the distinction the sediment-sickness and inoculation hypotheses turn on. Soil
science has used it for a century.

Output: docs/EXPERIMENTS.md, data/derived/experiments.json

Usage:  python3 scripts/experiments.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, read_json, write_json, write_doc

OUT = os.path.join(ROOT, "docs", "EXPERIMENTS.md")

# Three kinds of work, which are not interchangeable and are not equally strong.
KINDS = [
    ("experiment", "Constructive and investigative",
     "You change one thing and watch what follows. It *creates* the evidence, and "
     "it is the only kind that can establish causation, because the control is what "
     "rules out the alternatives. It costs money, time, access and usually "
     "permission."),
    ("measurement", "Investigative",
     "You observe something real that nobody recorded. It creates the *record* "
     "rather than the evidence: it can establish what is happening, where and when, "
     "but not why. Cheaper than an experiment and still requires being there. Most "
     "of the gaps in this project are of this kind - not unknowable, unrecorded."),
    ("instrument", "Build the means of measurement",
     "You make the thing that takes the reading, and put it where nobody was "
     "looking. It is a measurement project with a build phase, and it differs from "
     "the others in what it can be aimed at: **a network can be pointed at the "
     "assumptions of the existing monitoring**, not only at the sea. Whether one "
     "station can stand for a water body, whether monthly sampling sees a six-hour "
     "event, what an aggregation costs - all of those are questions about the "
     "instrument, and all of them are answerable by building a denser one beside "
     "it. It is also the kind with the clearest route to actually happening here: "
     "the Danish state is unusually willing to fund digital infrastructure, and a "
     "distributed sensor network is legible to it in a way that a request for more "
     "ship time is not."),
    ("analysis", "Armchair",
     "You work on what is already written down. It can establish consistency, bound "
     "magnitudes, expose contradictions and kill hypotheses - but it cannot "
     "establish causation, and it cannot recover a fact that was never recorded. "
     "**Almost everything this project has produced is of this kind.** That is worth "
     "saying plainly: its findings are of the form *your evidence does not support "
     "what you claim*, which is a real result and a limited one."),
]

SCALES = [
    ("small", "A person with a boat, a season, and a few thousand kroner. No "
              "institution required."),
    ("lab", "A university lab, standard methods, one to two seasons."),
    ("programme", "Needs a funded programme or ship time, but is still a bounded "
                  "experiment rather than a monitoring commitment."),
    ("desk", "No fieldwork at all. The data already exists; the analysis has not "
             "been run."),
]

X = [
    ("X1", "Does eelgrass fail because the sediment is sick?", "experiment",
     ["T4", "T5", "T2", "T1"], "small",
     "Restoration plantings fail in sediment whose chemistry looks adequate. "
     "Horticulture calls this replant disease and tests it the obvious way.",
     "Transplant eelgrass into a site where restoration has failed, in five "
     "treatments: (a) as-is; (b) with sediment inoculum from a functioning bed; "
     "(c) with the same inoculum autoclaved; (d) with lucinid clams added; "
     "(e) inoculum plus clams.",
     "Treatment (c) is the whole experiment. Live and sterilised inoculum carry "
     "identical chemistry and differ only in their organisms, so the contrast "
     "between them separates a chemical effect from a biological one. Plus "
     "untransplanted plots and a transplant into a functioning bed as the upper "
     "bound.",
     "Survival and shoot density at 3, 6 and 12 months; sulphide in root and "
     "rhizome tissue; porewater sulphide.",
     "Live inoculum beats sterilised → the sediment's *biology* is the missing "
     "thing, and T5 holds: sediment inoculation is a restoration tool. Both "
     "inocula beat as-is equally → it is chemistry, not biology. Clams alone "
     "work → T2, and the intervention is fauna rather than sediment. Nothing "
     "works → sediment sickness is not why restoration fails here, and attention "
     "goes back to the water column.",
     "This is the cheapest decisive experiment in the register and nobody has run "
     "it. Denmark has failed eelgrass restorations to site it in."),

    ("X2", "Is eelgrass killed by darkness, or by sulphide that darkness lets in?", "experiment",
     ["T1", "K11"], "small",
     "Eelgrass keeps sulphide out by leaking oxygen from its roots, powered by "
     "photosynthesis. If the leak is the mechanism, shading kills by poisoning "
     "rather than by starving.",
     "Shade healthy eelgrass in situ with mesh screens at four light levels "
     "spanning the assumed requirement, for one growing season.",
     "Unshaded plots, and open-mesh frames that shade nothing - so the frame's own "
     "hydrodynamic effect is separated from the shading.",
     "Tissue sulphide, shoot mortality, growth rate, and porewater sulphide, "
     "measured on the same schedule.",
     "Tissue sulphide rises *before* growth falls → the proximate cause is "
     "sulphide intrusion, the light requirement is really a sulphide-defence "
     "requirement, and the number that matters is sediment sulphide rather than "
     "Kd. Growth falls with no sulphide rise → ordinary light limitation and the "
     "existing indicator is measuring the right thing.",
     "Distinguishes two mechanisms that make identical predictions for the "
     "indicator and completely different predictions for what to do about it."),

    ("X3", "Does fat lower measured nitrogen?", "experiment",
     ["R1", "B1"], "lab",
     "Fat has no nitrogen, so bacteria decomposing it must take nitrogen from the "
     "water. If so, a fat-loaded water reads as *less* eutrophic on the regulated "
     "indicator while being more degraded.",
     "Mesocosms of natural seawater dosed with equal chemical oxygen demand as "
     "(a) fat, (b) carbohydrate, (c) algal biomass, (d) protein - four materials, "
     "same oxygen demand, C:N from infinite to about 5.",
     "Undosed seawater, and a dose of nitrate alone at the nitrogen content of the "
     "algal treatment.",
     "Dissolved inorganic nitrogen, oxygen, and bacterial biomass, daily for three "
     "weeks.",
     "DIN falls in the fat treatment → R1 holds, and the nitrogen indicator has a "
     "bias whose sign is opposite to what is assumed. DIN flat or rising → the "
     "immobilisation threshold does not operate here and the concern is void.",
     "A three-week bench experiment that would tell you whether one of the "
     "country's two regulated indicators can move the wrong way."),

    ("X4", "Does a small organic input unlock a large old one?", "experiment",
     ["R2", "H2"], "lab",
     "Priming: labile carbon gives microbes the energy to attack the recalcitrant "
     "pool, so an input's oxygen demand can exceed its own COD.",
     "Intact sediment cores dosed with a small, precisely known quantity of labile "
     "carbon.",
     "Undosed cores, and cores dosed with an equal quantity of carbon that is "
     "already recalcitrant. Isotopically labelled dose if affordable, which lets "
     "you attribute the CO₂ to old or new carbon directly.",
     "Cumulative oxygen consumption against the dose's own theoretical demand.",
     "Consumption exceeds the dose's COD → priming is real here, the sediment "
     "legacy is not an inert stock, and every load figure understates its own "
     "effect. Consumption matches the dose → no priming, and the additive "
     "accounting is sound.",
     "Standard soil-science method applied to marine sediment. The equipment is a "
     "core tube and an oxygen optode."),

    ("X5", "How long does a trawl track take to heal, and what does it release?", "experiment",
     ["D1", "D8", "D11", "E1"], "programme",
     "Trawling is hypothesised to destroy the biostabilising surface skin and "
     "release sulphide. Both are measurable, and the disturbance can be applied on "
     "purpose.",
     "One experimental trawl pass across an untrawled patch, with everything "
     "measured before, immediately after, and at intervals for two years.",
     "Adjacent untrawled patches, and a patch crossed by the vessel without gear "
     "deployed - which controls for the vessel rather than the trawl.",
     "Critical erosion threshold, surface-sediment chlorophyll, porewater and "
     "water-column sulphide, oxygen demand, and macrofauna.",
     "A sulphide and oxygen-demand pulse after the pass → trawling is an oxygen "
     "sink as well as a physical one, and belongs in the oxygen budget. Erosion "
     "threshold falls and recovers slowly → D8, and the recovery time constant is "
     "the number that decides whether current effort is sustainable.",
     "Requires a cooperative vessel and a closed area. Yields the one number - "
     "recovery time - that the whole trawling argument turns on."),

    ("X6", "Is silicon the limiting nutrient, and does adding it bring diatoms back?", "experiment",
     ["K1", "K2", "J1"], "lab",
     "Si comes only from weathering, so N and P have risen and Si has not. If Si "
     "limits, the community shifts away from diatoms toward the flagellates and "
     "gel-formers.",
     "Standard nutrient-addition bioassay on natural water: control, +N, +N+P, "
     "+N+P+Si, +Si alone.",
     "The control, and a dark bottle to separate growth from settling.",
     "Diatom versus flagellate share, chlorophyll, and transparent exopolymer "
     "particles by Alcian blue.",
     "+Si shifts the community toward diatoms → Si limitation is operative, and "
     "reducing N helps for a reason that has nothing to do with oxygen. TEP falls "
     "when Si is added → the gel of group J is a symptom of Si limitation, which "
     "connects fedtemøg to nutrient ratios rather than to nutrient amounts.",
     "A bottle experiment with a century of methodological pedigree. Silicate is "
     "already in the ODA record, so the observational half is free."),

    ("X7", "Measure the greasy layer, at all", "measurement",
     ["J2", "J3", "J1", "J6"], "small",
     "The greasiness people report after swimming is a property of the sea-surface "
     "microlayer, which concentrates surfactants and lipids by orders of magnitude "
     "over the bulk water. Denmark has never sampled it.",
     "Nothing. This is a measurement, not a manipulation - but it is the first one "
     "of its kind here, and it is a glass plate and a squeegee.",
     "Paired bulk-water samples from the same station and moment, so every result "
     "is an enrichment factor rather than a concentration. Sampled across wind "
     "speeds, because wind destroys the film.",
     "Surfactants, total lipid, TEP, and hydrocarbons in microlayer and bulk; wind "
     "speed; and a note of whether the water felt greasy.",
     "Enrichment factors well above one on calm days, correlating with reported "
     "greasiness → the phenomenon is real, located, and has a chemical signature "
     "that can then be traced to a source. No enrichment → look elsewhere, and "
     "group J shrinks.",
     "Glass-plate microlayer sampling is a 1970s technique costing almost nothing. "
     "That it has never been done here, for a phenomenon the public reports "
     "constantly, is the finding."),

    ("X8", "Are the trends in the sea or in the instruments?", "analysis",
     ["I1", "I2", "I3", "I5", "I6", "L3"], "desk",
     "The raw record carries the supplier, the sampling gear, the sonde, the "
     "technical instruction, and both the original and corrected result with the "
     "factor applied. No published analysis uses them.",
     "Nothing. Recompute every national trend four ways: on all stations versus "
     "only stations present throughout; on OriginalResultat versus "
     "KorrigeretResultat; within versus across gear and sonde types; and split at "
     "the 2007 transfer from the counties to the state.",
     "The comparison is the control. Each pair differs in exactly one "
     "methodological choice.",
     "The size and sign of every reported trend under each recomputation.",
     "A trend that survives all four → it is in the sea. A trend that changes sign "
     "or vanishes under any one → it is in the instrument, and it has been reported "
     "as a fact about Denmark. Either result is worth having, and the second would "
     "be worth a great deal.",
     "**No fieldwork and no permission required.** The data is downloaded. This is "
     "the highest ratio of consequence to cost in the register."),

    ("X9", "Does anything happen after an overflow?", "measurement",
     ["B1", "B2", "U2", "O9"], "small",
     "Denmark has 19,665 rain-conditioned outfalls and no per-event record of what "
     "they discharge or what follows. Monthly sampling cannot see a six-hour event.",
     "Nothing. Moor a logger.",
     "A second logger at a comparable site with no outfall upstream, so the rain "
     "itself is separated from the discharge.",
     "Oxygen, turbidity and temperature at 10-minute resolution through a season, "
     "with grab samples for faecal indicators and COD triggered by rainfall.",
     "Oxygen sags and indicator spikes in the 48 hours after overflow events → the "
     "acute route of U2 is real, monthly monitoring is structurally blind to it, "
     "and the outfall register becomes a pressure map. Nothing detectable → B1 is "
     "smaller than argued and this project should say so.",
     "Two loggers and a season. The single largest measurement gap in Danish "
     "coastal water is per-event overflow impact, and it is closed by hardware "
     "costing less than a laptop."),

    ("X10", "Put it back and see if it holds", "experiment",
     ["L4", "H1", "T4"], "small",
     "A target can be unreachable because the driver is still too high, or because "
     "something else is missing. From the outside these look identical, and thirty "
     "years of unexplained non-recovery sit between them.",
     "Transplant eelgrass, and separately add mussel biomass, into areas where the "
     "official assessment says water quality is now adequate.",
     "The same transplant into an area assessed as inadequate, and into one "
     "assessed as good - bracketing the gradient.",
     "Survival and persistence over three years.",
     "It holds where conditions are called adequate → the water is no longer the "
     "constraint, recovery is limited by propagule supply or by a missing "
     "precondition, and the policy lever has been pulled far enough. It fails → "
     "the assessment's own standard is not sufficient for the organism it is "
     "defined by, which is equally publishable and rather more awkward.",
     "This is the only experiment that can distinguish 'not yet' from 'never, for "
     "another reason', and it is the question the whole nitrogen argument rests "
     "on."),

    ("X11", "Does skewing the nutrient ratio make the gel?", "experiment",
     ["J1", "K2", "A9"], "lab",
     "Gel and exopolymer are hypothesised to come from carbon overflow when cells "
     "fix carbon they cannot balance with N or P.",
     "Chemostat or mesocosm cultures of natural assemblages at a matrix of N:P and "
     "Si:N ratios, at constant total nutrient supply.",
     "Constant-ratio cultures at matched total supply - so the effect of the ratio "
     "is separated from the effect of the amount.",
     "TEP by Alcian blue, dissolved and colloidal organic carbon, community "
     "composition.",
     "TEP peaks at skewed ratios rather than at high totals → the gel is a ratio "
     "phenomenon, and a policy that moves one nutrient alone can increase it. TEP "
     "tracks total supply → it is an enrichment phenomenon after all, and reducing "
     "load reduces it.",
     "Directly tests whether the intervention could make one outcome worse while "
     "improving another."),

    ("X12", "Do the filter feeders clear the water?", "experiment",
     ["F1", "F2"], "small",
     "Filter-feeder loss is hypothesised to raise chlorophyll with no change in "
     "nutrient supply, which would make restoration an alternative to load "
     "reduction rather than a complement.",
     "Enclosures with mussels added at a range of densities, in water of known "
     "nutrient status.",
     "Empty enclosures, and enclosures with dead shell at matched surface area - "
     "controlling for the structure rather than the animal.",
     "Chlorophyll, turbidity, light at the bed, and sedimentation rate.",
     "Chlorophyll clears at achievable densities → the same water-quality target "
     "is reachable by restoration at some ratio of effort to load reduction, and "
     "that ratio is computable. It does not → drop the argument.",
     "The dead-shell control matters: mussel beds change flow as well as filtering, "
     "and the two effects have different policy implications."),

    ("X14", "Can one station stand for a water body?", "instrument",
     ["I1", "I3", "H1", "C1", "M1"], "small",
     "The national assessment attaches one number to each water body, and the "
     "marine programme puts a median of one station in each - so the homogeneity "
     "that the whole framework assumes cannot be tested with the data that "
     "framework produces. Bathing water suggests a water body explains about 8% of "
     "the variation inside it, but bathing water measures faecal indicators, not "
     "the variables at issue.",
     "Twenty to fifty logging sensors - temperature, salinity, pressure, oxygen, "
     "turbidity, light - deployed across a single water body for one stratified "
     "season, at spacings from hundreds of metres to tens of kilometres.",
     "One of them co-located with the existing NOVANA station, which is what makes "
     "everything else comparable to the official record rather than a separate "
     "universe of numbers.",
     "The variance decomposition: how much of the variation is between sensors "
     "inside this one polygon, and how does agreement decay with distance.",
     "Agreement stays high across the polygon → the water body is a coherent unit "
     "and one station is defensible after all, which would be a genuine result "
     "against this project's own argument. Agreement decays over a few kilometres "
     "→ the unit is not the unit, and every per-water-body number is an average "
     "over things that are not alike.",
     "**Precision is worth less than replication here.** A sensor with 10% error at "
     "forty points tells you more about whether a polygon is homogeneous than one "
     "perfect instrument does, because the question is about variance and not about "
     "level. That inverts the usual objection to cheap sensors, and it is the "
     "reason this is affordable."),

    ("X15", "What does the aggregation cost?", "instrument",
     ["I3", "I4", "U2", "M1"], "small",
     "The oxygen indicator is the share of time oxygen sits below a threshold in "
     "the worst month, computed from six years of data, yielding one value per "
     "water body per six years. Nobody has measured what that collapse discards, "
     "because doing so needs a continuous record to compare against.",
     "Nothing in the water. Log one station continuously for two years at "
     "ten-minute resolution, then recompute the official indicator from the full "
     "record and again from monthly samples drawn out of it.",
     "The comparison is the control: identical water, identical sensor, two "
     "sampling regimes. Repeat the monthly draw a thousand times with different "
     "start dates to get the spread rather than one number.",
     "The indicator under continuous sampling, and the distribution of its value "
     "under monthly sampling of the same water.",
     "The monthly estimate is unbiased and tight → the aggregation is defensible "
     "and this line of criticism should be dropped. It is biased, or its spread "
     "spans the regulatory threshold → **the classification of a water body "
     "depends on which days somebody happened to sail**, and that is quantifiable "
     "to a probability rather than merely arguable.",
     "One sensor and two years. It is the cheapest way to put a number on the "
     "central claim of this whole project, and it works against us as easily as "
     "for us."),

    ("X16", "Do the cheap instruments agree with the expensive ones?", "instrument",
     ["I2", "I5", "I6"], "small",
     "Any distributed network is worthless if its readings cannot be tied to the "
     "national record, and cheap sensors drift and foul. This is the calibration "
     "that makes X14 and X15 admissible rather than interesting.",
     "Cheap loggers moored alongside a NOVANA station and beside the ship on every "
     "sampling visit, for a full year including a summer.",
     "The reference method itself - Winkler titration for oxygen, and the "
     "station's own sonde - measured at the same moment, which gives two "
     "independent comparisons rather than one.",
     "Offset and drift over time, fouling rate, and how long a sensor stays inside "
     "a stated tolerance before servicing.",
     "Drift is characterisable and correctable → the network's numbers can enter "
     "the same analyses as NOVANA's. It is not → the network still answers "
     "questions about *variance* and *timing*, which do not need absolute "
     "accuracy, and it should be scoped to those.",
     "**Biofouling is the binding constraint on marine deployment, not cost.** "
     "Everything else is solved; a sensor left in Danish water grows a community "
     "within weeks. Wipers, copper guards and UV all work and all add cost and "
     "power, and the honest version of this proposal budgets for servicing rather "
     "than pretending a buoy is unattended infrastructure."),

    ("X13", "Does the muck build up because nothing is eating it?", "experiment",
     ["E13", "E14", "E15", "R3", "R11"], "lab",
     "Turfgrass thatch - a greasy organic mat - forms when pesticides kill the "
     "earthworms and microbes that would incorporate the material. If fedtemøg is "
     "the same failure in sediment, then organic matter accumulates because the "
     "decomposers are gone, not because more is arriving.",
     "Litter bags of standardised organic material buried in sediment mesocosms "
     "dosed with an environmentally realistic fungicide concentration, and with a "
     "veterinary avermectin, at several doses.",
     "Undosed sediment, and autoclaved sediment as the zero-biology floor. **The "
     "organic supply is identical in every treatment** - which is the whole point, "
     "because it makes the nutrient hypothesis unable to explain any difference "
     "that appears.",
     "Mass loss from the litter bags over months; fungal and bacterial biomass; "
     "oxygen consumption; and whether a visible mat forms.",
     "Decay slows with dose while supply is held constant → the accumulation route "
     "is biocidal rather than nutritional, `E13` holds, and fedtemøg has a cause "
     "that no nitrogen policy touches. Decay is unaffected → the marine decomposers "
     "are not sensitive at realistic concentrations, and the thatch analogy fails "
     "where it matters, which is worth publishing too.",
     "The cleanest discriminator in the register: two hypotheses that predict the "
     "same observed outcome are separated by holding the input fixed and varying "
     "only the processors. Standard litter-bag method, standard mesocosms, and the "
     "dose figures come from published sales and residue data."),
]


def render(rows, hyp):
    o = []
    a = o.append
    by_scale = {}
    for r in rows:
        by_scale.setdefault(r[4], []).append(r)
    titles = {h["id"]: h["title"] for h in hyp["hypotheses"]}
    titles.update({u["id"]: u["name"] for u in hyp["unquantifiable"]})
    titles.update({o["id"]: o["name"] for o in hyp["observables"]})
    titles.update({r["id"]: r["name"] for r in hyp["routes"]})

    a("# Experiments, not studies\n")
    a("Most of what this project marks untestable is untestable **with existing "
      "monitoring**. That is a different claim, and a weaker one. A national "
      "observing programme answers questions about what is happening; a "
      "manipulation with a control answers questions about what causes what, and "
      "several of the open questions here would yield to one that fits in a season "
      "and a small boat.\n")
    a("The distinction matters because a study and an experiment fail differently. "
      "An analysis of existing data can always be argued with — the confounders are "
      "real, the record is short, the aggregation lost the signal. An experiment "
      "with a control and a decision rule fixed in advance either falsifies the "
      "hypothesis or does not.\n")
    a("So every entry below states its decision rule **before** anyone runs it, "
      "including what result would count against the hypothesis this project "
      "prefers.\n")
    a("> **The recurring design element is the sterilised control** — the same "
      "material, autoclaved or irradiated, run alongside the live one. Identical "
      "chemistry, no organisms. It separates *the chemistry of this stuff* from "
      "*the organisms in it* in a single step, and that is exactly the distinction "
      "the sediment-sickness and inoculation hypotheses turn on. Soil science has "
      "used it for a century.\n")

    a("## Three kinds of work, which are not interchangeable\n")
    counts = {}
    for r in rows:
        counts[r[2]] = counts.get(r[2], 0) + 1
    for kid, label, what in KINDS:
        a(f"**{label} — `{kid}`** ({counts.get(kid, 0)} of {len(rows)} below). {what}\n")
    a("Naming them separately matters because they are not substitutes and they are "
      "not equally strong. Only an experiment establishes causation. Only a "
      "measurement can recover something nobody wrote down. Analysis is the cheapest "
      "and the weakest, and it is what a project like this one can do from a desk — "
      "so it should be honest that most of its output is of that kind, and that the "
      "step up in force comes from going and looking.\n")

    a("## What it would take\n")
    a("| | | experiments |")
    a("|---|---|---|")
    for key, what in SCALES:
        ids = [r[0] for r in rows if r[4] == key]
        a(f"| `{key}` | {what} | {', '.join(ids) if ids else '—'} |")
    a("")
    cheap = [r for r in rows if r[4] in ("small", "desk")]
    a(f"**{len(cheap)} of {len(rows)} need no institution.** Two need no fieldwork "
      f"or none of their own. The most consequential — X8, whether the national "
      f"trends are in the sea or in the instruments — is a desk exercise on data "
      f"that is already downloaded.\n")

    for key, what in SCALES:
        rs = by_scale.get(key, [])
        if not rs:
            continue
        a(f"## {key.capitalize()} — {what}\n")
        for xid, title, kind, settles, _, why, manip, ctrl, meas, decide, note in rs:
            a(f"### {xid} — {title}\n")
            a(f"`{kind}`\n")
            named = ", ".join(f"[`{h}`](#HYPOTHESES.md) {titles.get(h, '')}"
                              for h in settles)
            a(f"**Bears on:** {named}\n")
            a(f"{why}\n")
            a(f"**Manipulate.** {manip}\n")
            a(f"**Control.** {ctrl}\n")
            a(f"**Measure.** {meas}\n")
            a(f"**Decide, in advance.** {decide}\n")
            a(f"*{note}*\n")

    a("## Why this list is short\n")
    a("It is short on purpose. Every entry had to clear three tests: a control that "
      "isolates one mechanism, a decision rule written before the result, and an "
      "outcome that would change what someone does. A great many interesting "
      "measurements fail the third test, and a great many proposals fail the "
      "first.\n")
    a("It is also worth saying what these experiments cannot do. None of them "
      "settles the national attribution question, because that is a question about "
      "a whole country over decades and no manipulation reaches it. What they "
      "settle is whether the *mechanisms* the attribution assumes actually operate — "
      "which is the part currently taken on trust in every direction, this "
      "project's included.\n")
    return "\n".join(o) + "\n"


def main():
    hyp = read_json(os.path.join(DERIVED, "hypotheses.json"))
    # ids may come from any of the register's namespaces: hypotheses, the
    # unquantifiable routes, or the observables. An experiment that bears on an
    # observable or on a route we said we could not quantify is worth flagging as
    # such, not treating as a typo.
    known = ({h["id"] for h in hyp["hypotheses"]}
             | {u["id"] for u in hyp["unquantifiable"]}
             | {o["id"] for o in hyp["observables"]}
             | {r["id"] for r in hyp["routes"]}
             | {t["id"] for t in hyp["terminal"]})
    bad = [(r[0], h) for r in X for h in r[3] if h not in known]
    if bad:
        log(f"  WARNING: unknown hypothesis ids referenced: {bad}")
    write_json(os.path.join(DERIVED, "experiments.json"),
               {"scales": [{"id": k, "what": w} for k, w in SCALES],
                "kinds": [{"id": a_, "label": b_, "what": c_} for a_, b_, c_ in KINDS],
                "experiments": [{"id": a_, "title": b_, "kind": k_, "settles": c_,
                                 "scale": d_, "why": e_, "manipulate": f_,
                                 "control": g_, "measure": h_, "decide": i_,
                                 "note": j_}
                                for a_, b_, k_, c_, d_, e_, f_, g_, h_, i_, j_ in X]})
    write_doc(OUT, render(X, hyp))
    log(f"wrote docs/EXPERIMENTS.md ({os.path.getsize(OUT):,} chars)")
    cheap = sum(1 for r in X if r[4] in ("small", "desk"))
    log(f"  {len(X)} experiments; {cheap} need no institution")
    log(f"  covering {len({h for r in X for h in r[3]})} ids across the register")
    return 0


if __name__ == "__main__":
    sys.exit(main())
