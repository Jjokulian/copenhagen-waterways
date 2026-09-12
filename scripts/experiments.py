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
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, read_json, write_json, write_doc
import live
import refs as _refs
# T1-T5 are both terminal outcomes and group T hypotheses; here they are hypotheses
_amb = _refs.ambiguous

OUT = os.path.join(ROOT, "docs", "EXPERIMENTS.md")
PAGE = "docs/EXPERIMENTS.md"
REF = re.compile(r"`?\b([A-Z]{1,2}\d{1,2})\b`?")

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
     "Transplant eelgrass into a site where restoration has failed, in six "
     "treatments: (a) as-is; (b) inoculum from a functioning bed in a **matched** "
     "setting - same salinity, sediment and thermal regime; (c) inoculum from a "
     "functioning but **mismatched** setting; (d) the matched inoculum autoclaved; "
     "(e) lucinid clams added; (f) matched inoculum plus clams.",
     "Two contrasts carry it. **Live against sterilised** (b vs d) separates a "
     "chemical effect from a biological one, because the two are identical in "
     "everything except their organisms. **Matched against mismatched** (b vs c) "
     "tests local adaptation: a community that has spent a million generations "
     "adapting to one setting is at a disadvantage in another, and the residents "
     "it has to displace are not. If donor origin matters, the practical rule "
     "follows immediately. Plus untransplanted plots and a transplant into a "
     "functioning bed as the upper bound.",
     "Survival and shoot density at 3, 6 and 12 months; sulphide in root and "
     "rhizome tissue; porewater sulphide.",
     "Live inoculum beats sterilised → the sediment's *biology* is the missing "
     "thing, and T5 holds: sediment inoculation is a restoration tool. Both "
     "inocula beat as-is equally → it is chemistry, not biology. Clams alone "
     "work → T2, and the intervention is fauna rather than sediment. Nothing "
     "works → sediment sickness is not why restoration fails here, and attention "
     "goes back to the water column.",
     "This is the cheapest decisive experiment in the register and nobody has run "
     "it. Denmark has failed eelgrass restorations to site it in.\n\n"
     "The human analogue has already worked through the same problem. Faecal "
     "transplant restores a cleared gut, but donor material engrafts unevenly, "
     "some donors work far better than others, and the current frontier is "
     "**autologous banking** - freezing a person's own community before the "
     "antibiotic and giving it back afterwards, so the restored community is "
     "already adapted to that body. The marine version of the second half is "
     "impossible retroactively and urgent prospectively, which is `X18`."),

    ("X18", "Bank the communities that still work, before they stop working",
     "measurement", ["T5", "T11", "W8", "T4", "L1"], "small",
     "Restoring a community needs a source, and the best source is the same "
     "community from a matched setting. Medicine has reached the same conclusion "
     "and acted on it: stool banks exist, and the frontier is autologous banking - "
     "freezing a person's own community *before* the antibiotic. The marine "
     "equivalent of the autologous half is impossible after the fact, and the "
     "donor half degrades a little every year as more sites fail.",
     "Nothing is manipulated. Collect and cryopreserve sediment and rhizosphere "
     "communities from the Danish sites that still function - eelgrass beds, mussel "
     "beds, undisturbed soft bottoms - with full physical metadata: salinity, "
     "sediment grain size, thermal regime, depth, exposure.",
     "The metadata *is* the design. Without matched conditions recorded, a bank is "
     "a freezer full of mud whose donors cannot be paired to a recipient site, and "
     "`X1` shows that pairing is exactly what decides whether an inoculum "
     "establishes.",
     "Community composition by sequencing at the time of collection, so that what "
     "was banked is documented rather than assumed, and so the archive doubles as a "
     "baseline for `T10` and `W8`.",
     "There is no hypothesis to falsify here, which is why it is filed as "
     "measurement rather than experiment. What it produces is **optionality**: "
     "every later restoration attempt, and every test of whether donor origin "
     "matters, needs source material that either exists or does not. It also "
     "supplies the pre-disturbance baseline that `T10` and `W8` both say is "
     "missing by construction.",
     "**The only item in this register that gets harder every year it is not "
     "done.** Everything else here can be run later at the same cost; this one "
     "loses material permanently as sites degrade, and the sites that would be most "
     "valuable to have banked are the ones most likely to be gone. A freezer, a "
     "coring tube, and somebody's time."),

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

    ("X19", "A panel that reports nothing on the days nothing happens",
     "measurement",
     ["T1", "T3", "T5", "J2", "O7"], "small",
     "The outcomes anyone actually cares about - greasy water, a foul shore, a bed "
     "with nothing structural left on it - are not measured by any Danish "
     "programme. There is no instrument for fedtemøg; the glossary entry says so, "
     "and it is not an oversight so much as a category the monitoring was never "
     "built to hold. The only observers are the people who swim, walk and fish "
     "there, and their observations are currently discarded as anecdote.",
     "Nothing is manipulated. What is built is a reporting scheme, and its whole "
     "design rests on one decision: **a fixed panel that reports on a schedule, "
     "including on the days there is nothing to report.**",
     "That null is the control and the entire difference between a dataset and a "
     "complaints inbox. Open reporting - tell us when it is bad - produces a map "
     "of attention, and attention follows news coverage, so the resulting series "
     "measures publicity. A panel with a denominator produces a rate. It is the "
     "same failure as the satellite matchups: the observations that exist must not "
     "be selected on the variable being measured.",
     "Per visit: position and time (a photograph carries both in EXIF, and "
     "fedtemøg is visible, so the image is a record of the outcome rather than a "
     "report about it); an ordinal odour intensity on a fixed scale, as used in "
     "odour-nuisance regulation; water appearance; whether anything structural is "
     "growing; and the null when none of it applies. Plus one control question "
     "about something unrelated to the outcome, to detect when a panel's reporting "
     "effort is rising rather than the phenomenon.",
     "A rate per site per fortnight that can be laid against overflow events, "
     "rainfall and the satellite fields → the outcome variable finally has a time "
     "series. Reports that track news coverage rather than weather or discharge → "
     "the panel is measuring attention and the design has failed, which is itself "
     "worth knowing before anyone builds a bigger one.",
     "Cheap, and the cheapest part is the phone people already carry. The "
     "expensive part is recruiting observers who will keep reporting nothing, "
     "which is the part every citizen-science scheme underestimates."),

    ("X20", "Ask the people with the longest baseline, about dated events",
     "measurement",
     ["T1", "T4", "W2", "D1"], "small",
     "Commercial and recreational fishermen hold the longest continuous "
     "observation of the Danish seabed that exists - decades of hauling gear "
     "across specific ground - and none of it is recorded anywhere as observation. "
     "Landings are recorded; what the bottom looked and smelled like is not.",
     "Nothing. Structured interview against a chart, with the questions fixed in "
     "advance and the answers timestamped and positioned.",
     "The known failure mode is shifting baseline syndrome: each generation's "
     "normal is the previous generation's decline, so 'how was it back then' "
     "reliably understates change and does so more the older the respondent. The "
     "mitigation is to anchor every question on a **dated specific event** - what "
     "came up in that haul, in that autumn, on that ground - rather than on a "
     "remembered general state. Where two people fished the same ground in the "
     "same years, their accounts are a replicate.",
     "Position and year of specific hauls; what was on the gear; bottom type as "
     "felt through the gear; smell; and the year a ground stopped being worth "
     "fishing, which is a sharper memory than any gradual change.",
     "Dated accounts that agree between independent respondents on the same ground "
     "→ a reconstructed history for places with no monitoring at all, testable "
     "against trawl-track records and the iltsvind bulletins. Accounts that "
     "disagree or that smooth into a single declining narrative regardless of "
     "ground → shifting baseline is dominating and the method gives history rather "
     "than data.",
     "This is the one item on the page that gets harder every year for a reason "
     "unrelated to funding, and it shares that with X18: the people who fished "
     "before the change are ageing out, and the baseline goes with them."),

    ("X21", "Reconstruct the catchments from the endpoints, nationally",
     "analysis",
     ["B1", "B2", "B3", "A4"], "desk",
     "Denmark has 20,402 outfalls with a position, an annual volume and a reported "
     "reduced impervious area, and no published map of which ground drains to "
     "which. The pipe geometry exists in a national register that is not open, so "
     "the network cannot be looked up. It may be inferable.",
     "Nothing physical. Delineate catchments from the terrain model, then "
     "**constrain the delineation so each outfall's computed impervious area "
     "matches the reduced area already published for it**. Building footprints and "
     "construction years come from BBR, so impervious cover can be reconstructed "
     "for any year rather than only for today.",
     "The 20,402 reported areas are the control, and they were produced "
     "independently of any terrain analysis. A delineation that reproduces them is "
     "doing something right; one that cannot is falsified without fieldwork. Hold "
     "out a random tenth to fit nothing and check against those.",
     "Terrain, building footprints with year built, and the outfall register - all "
     "open, all already fetched or fetchable. Plus, where a municipal wastewater "
     "plan publishes real catchment boundaries, those become a second and much "
     "harder test.",
     "Catchments reproducing the published areas within a stated error → per-"
     "outfall connected area for the whole country, which is what B1 and B2 need "
     "and neither has. Systematic failure in some region or sewer type → that is "
     "informative too, because it localises where terrain stops predicting the "
     "network. Failure everywhere → the inference does not work and the register "
     "stays the only route.",
     "It produces a plausible network, not the real one, and every use must say "
     "so. But 97 of 98 municipalities currently have no catchment map at all, and a "
     "plausible one with a stated error beats nothing. Copenhagen's exists only "
     "because seven PDFs happened to be recoverable, which is archaeology rather "
     "than method."),

    ("X22", "Find the baskets, instead of accepting the ones that were drawn",
     "analysis",
     ["L5", "I4", "A1", "Z8"], "desk",
     "The Copenhagen map does not aggregate into administrative units. Its units "
     "are functional - a catchment is the ground that drains to one point, a flow "
     "path is where water actually goes - so the boundaries are consequences of "
     "the terrain rather than decisions about it. The marine map has no equivalent: "
     "it inherits 123 water bodies drawn for administration, and every statistic "
     "computed in them inherits that drawing. The question nobody asks is whether "
     "those lines are where the sea changes.",
     "Nothing physical. The satellite record supplies a field with no station bias "
     "at all - daily 1 km ocean colour since 1997, every pixel measured the same "
     "way on the same day - so the partition can be derived from the water rather "
     "than imposed on it.",
     "**The null already exists and was measured**: similarity of log Kd490 against "
     "separation, pooled over 144 days, giving r = 0.97 at 1 km, 0.74 at 12 km, "
     "0.50 at 31 km. Two points 12 km apart should agree at 0.74 wherever they "
     "are. So take pairs at a fixed separation that straddle an official boundary "
     "and pairs at the same separation that do not. A boundary that is real shows "
     "*less* agreement across it than the curve predicts; one that agrees more "
     "than the curve predicts is splitting water that behaves as one thing.",
     "The gridded record already fetched, and the 123 polygons. Then the harder "
     "half: cluster the field on its own temporal correlation structure and "
     "compare the discovered partition to the official one - not to score it, but "
     "to produce a map of where the two disagree.",
     "Boundaries that pass → the units are doing real work and aggregation inside "
     "them is defensible, which would be a genuine finding *for* the current "
     "framework. Boundaries that fail → named, located, and quantified in "
     "correlation units rather than argued about. A discovered partition that cuts "
     "across the official one → the strongest possible version of the argument, "
     "because it says not merely that the baskets are wrong but where the right "
     "ones are.",
     "Two limits stated in advance. The satellite sees the surface, and its "
     "retrieval fails hardest in exactly the fjords where the boundaries are "
     "densest, so the test is strongest in open water and weakest where it would "
     "matter most. And a partition discovered from one variable is a partition for "
     "that variable: the baskets for light need not be the baskets for oxygen, and "
     "finding that they differ would itself dispose of the idea that one set of "
     "lines can serve every purpose."),

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

    ("X23", "Does the faecal load reach the water, or is it spent in the soil?",
     "experiment", ["E13", "E14", "E15", "A2", "G2", "O1"], "programme",
     "The load account carries nitrogen and phosphorus. Everything else that is "
     "spread — organic carbon, copper and zinc from feed, antiparasitics, "
     "antibiotics, resistance genes, pathogens — is unpriced, and its fate is "
     "genuinely unknown rather than known to be small. A field is a reactor: labile "
     "carbon is respired there, so the default assumption is that little arrives. "
     "But rain onto freshly spread ground, frozen or saturated soil, tile drains "
     "and macropores are documented bypasses, and **Denmark's own monitoring cannot "
     "see any of it**, because it samples on a calendar rather than on events and "
     "measures a determinand list that does not include the payload.",
     "Nothing is manipulated: the spreading window is the manipulation, it happens "
     "every spring, and it is applied to the whole country at once. What is added "
     "is **event-based sampling** — flow-triggered automatic samplers on paired "
     "stream catchments, taking a series through the rising limb and the falling "
     "limb of each storm from February to April, and again in an autumn window when "
     "no spreading is permitted.",
     "Three controls, and the design needs all of them. **Time:** the same streams "
     "outside the spreading window. **Space:** catchments matched on soil, drainage "
     "and area but contrasting in livestock density, which is where the national "
     "register earns its place. **And source:** faecal sterols and host-specific "
     "microbial markers separate pig manure from human sewage and from soil organic "
     "matter, which is what turns a concentration into an attribution.",
     "Per event: COD and BOD, particulate organic carbon, ammonium, total N and P, "
     "copper and zinc, coprostanol with a pig-specific marker, one antiparasitic "
     "residue, and discharge at the same minute so the result is a load and not a "
     "concentration.",
     "**Markers and copper rise sharply in the days after spreading and scale with "
     "livestock density → the payload bypasses the soil**, the second channel is "
     "real and measurable, and the determinand list of the national programme is "
     "missing a term rather than merely being coarse. **Markers stay at baseline "
     "through the window → the soil reactor holds**, what reaches the sea from a "
     "field is essentially nitrate, and the nitrogen framing is right about *what "
     "arrives* even where this project disputes how much. **That second outcome is "
     "the one worth pre-committing to publish**, because it argues against the "
     "suspicion that motivated the design.",
     "The instrument is constructed in [SENSING.md](SENSING.md) and the full "
     "protocol - hypotheses that can lose, the decision rules fixed before the "
     "first sample, the twelve matched pairs and what invalidates the whole thing "
     "rather than answering it - is [SETTLE.md](SETTLE.md). "
     "This is the cheapest unbought answer in the whole document. The instruments "
     "are ordinary autosamplers and a lab list, the timing is fixed by a calendar "
     "everyone already knows, and the comparison catchments exist. It is also the "
     "one design here whose *negative* result would materially strengthen the "
     "official account — which is a reason to run it, not a reason to avoid it. "
     "**Grab sampling cannot substitute:** this project's own sources report that "
     "transport computed from grab samples was underestimated in all three streams "
     "of the 2018 GUDP study, and an event is exactly what a fortnightly visit "
     "misses."),

    ("X17", "Take the fungicides away, region by region, without ruining anyone",
     "experiment", ["E13", "E14", "E15", "E16", "E17", "R3", "R11", "T12"],
     "programme",
     "The register cannot say what agricultural biocides do to marine decomposers, "
     "because the counterfactual does not exist: every Danish catchment has been "
     "sprayed for decades. A ban would create one and would also be economic "
     "suicide for the people asked to absorb it, so it will not happen and should "
     "not.",
     "Substitute rather than prohibit. Replace chemical control with biological "
     "control — the occupancy route — catchment by catchment on a **staggered "
     "schedule with the order randomised**, until every participating area has "
     "crossed over.",
     "A stepped wedge is its own control twice over. Each catchment is compared "
     "against its own record before crossover, and against the catchments that have "
     "not yet crossed. **Nobody is withheld from the treatment** — they receive it "
     "later — which is what makes it politically and ethically possible where a "
     "control group would not be.",
     "In the sea: decomposition rate of standard material, sediment fungal biomass, "
     "benthic fauna, sediment organic content. On land, and with equal weight: "
     "yield, input cost, disease incidence and farm margin.",
     "Marine decomposition recovers where crossover has happened and not where it "
     "has not → the biocide route of `E13` is real at landscape scale, and the "
     "substitution is the remedy. Nothing changes in the sea → the marine biocide "
     "hypothesis fails its largest test and this project should say so loudly. "
     "**And the agronomic outcome is a result in its own right, whichever way it "
     "falls** — if yields drop, that is the number the argument has to carry, not a "
     "detail to be discovered later by the people who farm.",
     "This is the only design here that is simultaneously an intervention, a "
     "national experiment, and survivable for the people inside it. It also "
     "supplies what nothing else can: **a real counterfactual for the chemical "
     "argument**, at the scale the argument is made. Denmark already has the "
     "administrative machinery — pesticide taxation, action plans, and protection "
     "zones around wellfields where spraying is restricted — so the instrument "
     "exists and only the randomisation and the marine measurement would be new. "
     "The general form of that observation is the meta-solution in "
     "[PLACES.md](PLACES.md): a country that does one thing everywhere has spent "
     "the contrast that would have told it whether the thing worked, and the "
     "staggered order here is how you buy it back without withholding anything "
     "from anyone."),

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


# ---------------------------------------------------------------- the page ---
# Everything from here to main() writes docs/EXPERIMENTS.md. Every assertion on the
# page is a checked claim (LIVE_NUMBERS.md section 11), registered in
# data/manual/claims.d/w3-ea.json with what it rests on: a design is this project's
# own and stipulated, an argument is argued, a statement about the data rests on the
# data or a pinned document, and a hypothesis is referenced, never claimed. A
# paragraph the register entry X carries unchanged is rendered from it and marked
# C-EA-<id>-<part>; a paragraph the page words differently is in PAGE below. What the
# page once said and could not justify is in docs/ARCHIVE.md, not here.
import claims as _claims

C = live.claim
_REG = {}
# T1-T5 are both hypotheses and terminal outcomes. Everywhere on this page they are
# hypotheses, except in the two entries about the outcomes themselves - a panel for
# greasy water and a foul shore, and the fishermen's seabed - where they name outcomes.
OUTCOME_ENTRIES = ("X19", "X20")
CHOICE = " - a choice of this design, not a measurement"
PARTS = [("why", "WHY", ""), ("manipulate", "MANIP", "**Manipulate.** "),
         ("control", "CTRL", "**Control.** "), ("measure", "MEAS", "**Measure.** "),
         ("decide", "DECIDE", "**Decide, in advance.** "), ("note", "NOTE", "")]
SCALE_HEAD = {"small": "Small", "lab": "Lab", "programme": "Programme", "desk": "Desk"}


def _cl():
    if "d" not in _REG:
        _REG["d"] = _claims.load()[0]
    return _REG["d"]


def RD(sid, value, phrase):
    """A number read from a pinned document, refused unless the pinned copy holds the
    phrase. Each reading gets its own phrase: two readings with one phrase would
    share an id."""
    d = _cl()
    if _claims._flat(phrase) not in _claims._flat(_claims.pin_text(d, sid)):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    return live._mk(value, ["reading", sid, "phrase", phrase, _claims._meta(d, sid)])


def RS(placeholder):
    """A figure the claims register already defines, resolved through it."""
    return _claims.resolve(_cl(), placeholder, {})[0]


def R(i, title=False, family=None):
    return live.ref(i, title, family=family or ("hypotheses" if _amb(i) else None))


def O(i):
    """A terminal outcome, which T1-T5 also name."""
    return live.ref(i, family="terminal")


def stated(name, shown, reason):
    return live.stated(name, shown, shown, reason)


# Figures inside paragraphs rendered unchanged from the register entry.
FIGS = {
    "X1": [("3, 6 and 12 months", lambda v: stated(
        "x1_survey_months", "3, 6 and 12", "the survey times proposed" + CHOICE) + " months")],
    "X9": [("10-minute", lambda v: stated(
               "x9_logging_minutes", "10", "the logging interval proposed" + CHOICE) + "-minute"),
           ("48 hours", lambda v: stated(
               "x9_window_hours", "48", "the post-event window fixed in advance" + CHOICE) + " hours")],
    "X22": [("the 123 polygons", lambda v: f"the {v['wb']} polygons")],
}


def checked(xid, text, v):
    """A paragraph of the register entry with its references, figures and species as
    checked entities. References go first, on the typed text, so no marker is read
    back as an id."""
    fam = "terminal" if xid in OUTCOME_ENTRIES else "hypotheses"
    text = REF.sub(lambda m: R(m.group(1), family=fam if _amb(m.group(1)) else None)
                   if m.group(1) in v["known"] else m.group(0), text)
    for said, now in FIGS.get(xid, []):
        if said in text:
            text = text.replace(said, now(v))
    return text.replace("CO₂", live.chem("CO2"))


def page_words(v):
    """The paragraphs the page words differently from the register entry, by entry and
    part; a note is a list of paragraphs."""
    T = R
    return {
        "X1": {
            "why": C("C-EA-X1-WHY", f"{T('T4')} proposes that restoration plantings fail in "
                     "sediment whose chemistry looks adequate - the marine form of what "
                     "horticulture calls replant disease - and that the test is the one "
                     "horticulture uses."),
            "control": C("C-EA-X1-CTRL", "Two contrasts carry it. **Live against "
                         "sterilised** (b vs d) separates a chemical effect from a biological "
                         "one, because sterilising takes the organisms out and leaves the "
                         "material. **Matched against mismatched** (b vs c) tests local "
                         "adaptation: whether a community does worse in a setting unlike the "
                         "one it came from. If donor origin matters, the practical rule follows "
                         "immediately. Plus untransplanted plots and a transplant into a "
                         "functioning bed as the upper bound."),
            "note": [C("C-EA-X1-NOTE", "Among the sources this project surveyed, the nearest "
                       "Danish trial is an eelgrass transplant in outer Horsens Fjord with "
                       "bare-bottom and natural-bed controls. It followed the fauna that came "
                       "back, not eelgrass survival against sediment condition, so this "
                       "inoculation test was not found run in Denmark."),
                     C("C-EA-X1-NOTE2", "The human analogue is faecal microbiota transplant, "
                       "which moves the microbes of a healthy donor into an unhealthy person, "
                       "and stool banks now hold donor material for it. The marine version of "
                       "the bank is `X18`.")],
        },
        "X18": {
            "why": C("C-EA-X18-WHY", "Restoring a community needs a source, and `X1` asks "
                     "whether one from a matched setting works best. Medicine keeps such "
                     "sources: stool banks hold donor material for faecal transplant. A marine "
                     "bank of a site's own community cannot be made once that site has failed, "
                     "and each site that fails is one donor fewer."),
            "control": C("C-EA-X18-CTRL", "The metadata *is* the design. Without matched "
                         "conditions recorded, a bank is a freezer full of mud whose donors "
                         "cannot be paired to a recipient site, and `X1` is the test of whether "
                         "pairing decides if an inoculum establishes."),
            "decide": C("C-EA-X18-DECIDE", "There is no hypothesis to falsify here, which is "
                        "why it is filed as measurement rather than experiment. What it produces "
                        "is **optionality**: every later restoration attempt, and every test of "
                        "whether donor origin matters, needs source material that either exists "
                        "or does not. It also supplies a pre-disturbance baseline, which the "
                        f"source search for {T('T10')} found for no Danish marine "
                        "intervention."),
            "note": [C("C-EA-X18-NOTE", "**It gets harder every year it is not done:** each "
                       "site that degrades takes its community out of reach. A freezer, a "
                       "coring tube, and somebody's time.")],
        },
        "X2": {
            "why": C("C-EA-X2-WHY", f"{T('T1')} proposes that eelgrass keeps sulphide out by "
                     "leaking oxygen from its roots, powered by photosynthesis. If the leak is "
                     "the mechanism, shading kills by poisoning rather than by starving."),
        },
        "X7": {
            "why": C("C-EA-X7-WHY", f"On {T('J2')}, the greasiness people report after "
                     "swimming is a property of the sea-surface microlayer, where surfactants "
                     "and other surface-active matter are enriched over the bulk water.")
            + " " + C("C-EA-X7-NONE", "None of the sources this project surveyed holds a "
                      "Danish sample of that layer: in two searches, every Baltic microlayer "
                      "dataset that surfaced was German."),
            "manipulate": C("C-EA-X7-MANIP", "Nothing. This is a measurement, not a "
                            "manipulation, and its equipment is a glass plate and a squeegee."),
            "control": C("C-EA-X7-CTRL", "Paired bulk-water samples from the same station and "
                         "moment, so every result is an enrichment factor rather than a "
                         "concentration. Sampled across wind speeds, because "
                         f"{T('J2')} has wind destroying the film."),
            "note": [C("C-EA-X7-NOTE", "The glass-plate microlayer sampler was first described "
                       "in 1972 and is commonly used. That no Danish sample of the layer turned "
                       "up in two searches is itself the finding.")],
        },
        "X19": {
            "why": C("C-EA-X19-WHY", "Two of the outcomes the register ends in, water "
                     f"unpleasant to be in ({O('T3')}) and the shore lost as a place "
                     f"({O('T5')}), have no series in any source this project surveyed: none "
                     "holds shore condition or fedtemøg, and the site's glossary says "
                     "fedtemøg is not measured by anything.")
            + " " + C("C-EA-X19-WHO", "The people who swim, walk and fish there are the ones "
                      "placed to see them."),
            "control": C("C-EA-X19-CTRL", "That null is the control and the entire difference "
                         "between a dataset and a complaints inbox. Open reporting - tell us "
                         "when it is bad - produces a map of attention, and attention follows "
                         "news coverage, so the resulting series measures publicity. A panel "
                         "with a denominator produces a rate: the observations must not be "
                         "selected on the variable being measured."),
            "measure": C("C-EA-X19-MEAS", "Per visit: position and time (a phone photograph "
                         "can carry both in its EXIF metadata, and fedtemøg is visible, so the "
                         "image is a record of the outcome rather than a report about it); an "
                         "ordinal odour intensity on a fixed scale; water appearance; whether "
                         "anything structural is growing; and the null when none of it applies. "
                         "Plus one control question about something unrelated to the outcome, "
                         "to detect when a panel's reporting effort is rising rather than the "
                         "phenomenon."),
            "note": [C("C-EA-X19-NOTE", "The recording device is the phone observers already "
                       "carry. The hard part is recruiting observers who will keep reporting "
                       "nothing.")],
        },
        "X20": {
            "why": C("C-EA-X20-WHY", "Fishermen who have hauled gear across the same ground "
                     "for years have seen the bottom there, and none of the sources this "
                     "project surveyed records what they saw: its fisheries sources are "
                     "landings and swept area, not what the bottom looked and smelled like."),
            "control": C("C-EA-X20-CTRL", "The known failure mode is shifting baseline "
                         "syndrome: each generation redefines what is natural, so 'how was it "
                         "back then' is answered against a baseline that has already moved. The "
                         "mitigation is to anchor every question on a **dated specific event** - "
                         "what came up in that haul, in that autumn, on that ground - rather "
                         "than on a remembered general state. Where two people fished the same "
                         "ground in the same years, their accounts are a replicate."),
            "note": [C("C-EA-X20-NOTE", "Like `X18`, it gets harder every year it is not "
                       "done: the people who fished before the change are ageing, and what "
                       "they remember of the baseline goes with them.")],
        },
        "X9": {
            "why": C("C-EA-X9-WHY", f"The national register of rain-dependent discharge "
                     f"points holds {v['rbu']:,} of them. The utilities' outfall layers carry "
                     "one annual value per outfall, and a yearly count of overflows for "
                     f"{v['co_count']:,} of the {v['co_n']:,} combined-sewer overflows; among "
                     "the sources this project surveyed, a record of each overflow's count, "
                     "duration and volume exists for one small utility.")
            + " " + C("C-EA-X9-FREQ", "DCE note that oxygen is measured at a frequency that "
                      "need not catch short-lived oxygen depletion.")
            + " " + C("C-EA-X9-U2", f"{T('U2')} is about exactly such events: a discharge of "
                      "hours after a storm, invisible in an annual average."),
            "note": [C("C-EA-X9-NOTE", "Two loggers and a season. The register's "
                       f"{T('B1')} names per-event overflow volume and duration as the "
                       "single most valuable missing series.")],
        },
        "X10": {
            "why": C("C-EA-X10-WHY", "A target can be unreachable because the driver is still "
                     "too high, or because something else is missing "
                     f"({T('L4')}). From the outside these look identical."),
            "note": [C("C-EA-X10-NOTE", "It separates 'not yet' from 'never, for another "
                       "reason', which is what a load target needs to know about itself.")],
        },
        "X12": {
            "note": [C("C-EA-X12-NOTE", "The dead-shell control separates what the shells do "
                       "as structure from what the animals do by filtering, and the two would "
                       "call for different policies.")],
        },
        "X14": {
            "why": C("C-EA-X14-DCE", "DCE's statistical models for the coastal indicators were "
                     f"built for {v['dce29']} monitoring stations representing {v['dce22']} "
                     "water bodies.")
            + " " + C("C-EA-X14-ARG", "Where one station stands for a water body, the "
                      "homogeneity that assumes cannot be tested with the data it produces.")
            + " " + C("C-EA-X14-BATH", "In bathing-water samples, about "
                      f"{v['bath'] * 100:.0f}% of the variation, with years taken out, lies "
                      "between water bodies - but bathing water measures faecal indicators, "
                      "not the variables at issue."),
            "note": [C("C-EA-X14-NOTE", "**Precision is worth less than replication here.** A "
                       "sensor with " + stated("x14_sensor_error_pct", "10",
                                              "an illustrative sensor error" + CHOICE)
                       + "% error at forty points tells you more about whether a polygon is "
                       "homogeneous than one perfect instrument does, because the question is "
                       "about variance and not about level.")],
        },
        "X15": {
            "why": C("C-EA-X15-DCE", "DCE's oxygen indicator is the share of time oxygen is "
                     "below each of two thresholds in the month with the most days of low "
                     f"oxygen; {v['dce6a']} years of data go into the monthly frequencies, and "
                     f"one value results per {v['dce6b']}-year period.")
            + " " + C("C-EA-X15-ARG", "What that collapse discards can only be measured "
                      "against a continuous record."),
            "note": [C("C-EA-X15-NOTE", "One sensor and two years, and the answer can go "
                       "against this project's argument as easily as for it.")],
        },
        "X16": {
            "why": C("C-EA-X16-WHY", "Any distributed network is worthless if its readings "
                     "cannot be tied to the national record, and a sensor left in the water "
                     "fouls. This is the calibration that makes `X14` and `X15` admissible "
                     "rather than interesting."),
            "note": [C("C-EA-X16-NOTE", "**Biofouling affects underwater instruments**, so the "
                       "honest version of this proposal budgets for servicing rather than "
                       "pretending a buoy is unattended infrastructure.")],
        },
        "X3": {
            "why": C("C-EA-X3-WHY", f"{T('R1')} starts from fat carrying no nitrogen: "
                     "bacteria decomposing it must then take nitrogen from the water, so a "
                     "fat-loaded water would read as *less* eutrophic on the regulated "
                     "indicator while being more degraded."),
            "manipulate": C("C-EA-X3-MANIP", "Mesocosms of natural seawater dosed with equal "
                            "chemical oxygen demand as (a) fat, (b) carbohydrate, (c) algal "
                            "biomass, (d) protein - four materials, same oxygen demand, "
                            "carrying different amounts of nitrogen."),
            "note": [C("C-EA-X3-NOTE", "A three-week bench experiment that would tell you "
                       "whether a nitrogen indicator can move the wrong way.")],
        },
        "X4": {
            "why": C("C-EA-X4-WHY", f"{T('R2')} is priming: labile carbon gives microbes the "
                     "energy to attack the recalcitrant pool, so an input's oxygen demand can "
                     "exceed its own COD."),
            "note": [C("C-EA-X4-NOTE", "Priming is a soil-science idea - something added to "
                       "soil changing how fast its organic matter decomposes - applied here to "
                       "marine sediment. The equipment is a core tube and an oxygen optode.")],
        },
        "X6": {
            "manipulate": C("C-EA-X6-MANIP", "A nutrient-addition bioassay on natural water: "
                            "control, +N, +N+P, +N+P+Si, +Si alone."),
            "why": C("C-EA-X6-WHY", f"{T('K1')} starts from silicon coming from rock "
                     "weathering, so that N and P rise with human activity while Si does not. "
                     "If Si then limits, the community shifts away from diatoms toward the "
                     "flagellates and gel-formers."),
            "note": [C("C-EA-X6-NOTE", "A bottle experiment. Silicon is among the parameters "
                       "of the ODA water-chemistry extract held here, so the observational half "
                       "needs no fieldwork.")],
        },
        "X13": {
            "why": C("C-EA-X13-THATCH", "Turf thatch builds up for several reasons, among "
                     "them insecticides that reduce earthworm activity, acidic soils that "
                     "cannot support enough decomposing microorganisms, and too much nitrogen "
                     "fertiliser.")
            + " " + C("C-EA-X13-WHY", f"{T('E13')} and {T('R3')} propose that fedtemøg is "
                      "the same failure in sediment: organic matter accumulating because the "
                      "decomposers are gone, not because more is arriving."),
            "note": [C("C-EA-X13-NOTE", "Two hypotheses that predict the same observed outcome "
                       "are separated by holding the input fixed and varying only the "
                       "processors.")
                     + " " + C("C-EA-X13-DOSE", "What counts as a realistic dose needs Danish "
                               "use and residue figures, and this project could not locate "
                               "Danish pesticide use at any unit finer than the nation.")],
        },
        "X23": {
            "why": C("C-EA-X23-LOAD", "The national overflow and stormwater layers report "
                     "water, nitrogen and phosphorus per outfall, and nothing else of what "
                     "the water carries.")
            + " " + C("C-EA-X23-PAYLOAD", "What else goes onto fields with manure has no "
                      "such account: for veterinary drugs, VetStat holds what is dispensed, and "
                      "no manure, soil or sediment measurement of where they went was found.")
            + " " + C("C-EA-X23-REACTOR", "A field is a reactor: labile carbon is respired "
                      "there, so the default assumption is that little arrives. Rain onto "
                      "freshly spread ground, frozen or saturated soil, tile drains and "
                      "preferential flow are the ways it could arrive anyway.")
            + " " + C("C-EA-X23-BLIND", "**The stream monitoring this project records cannot "
                      "see it**: it samples at fixed intervals rather than on events, and "
                      "measures none of the faecal markers."),
            "control": C("C-EA-X23-CTRL", "Three controls, and the design needs all of them. "
                         "**Time:** the same streams outside the spreading window. **Space:** "
                         "catchments matched on soil, drainage and area but contrasting in "
                         "livestock density, which is where the national register earns its "
                         "place. **And source:** faecal sterols and host-specific microbial "
                         "markers, whose limits in telling a pig from a person "
                         "[SENSING.md](SENSING.md) sets out, are what would turn a "
                         "concentration into an attribution."),
            "note": [C("C-EA-X23-NAV", "The instrument is constructed in "
                       "[SENSING.md](SENSING.md), and the full protocol - hypotheses that can "
                       "lose, the decision rules fixed before the first sample, the matched "
                       "pairs and what invalidates the whole thing rather than answering it - "
                       "is [SETTLE.md](SETTLE.md).")
                     + " " + C("C-EA-X23-NEG", "It is a design whose *negative* result would "
                               "strengthen the official account — which is a reason to run it, "
                               "not a reason to avoid it.")
                     + " " + C("C-EA-X23-GRAB", "**Grab sampling cannot substitute:** in every "
                               "stream of the 2018 study this project records, transport "
                               "computed from grab samples came out underestimated against "
                               "intensive daily measurement, and an event is exactly what a "
                               "visit at fixed intervals misses.")],
        },
        "X17": {
            "why": C("C-EA-X17-WHY", "The register cannot say what agricultural biocides do "
                     "to marine decomposers: ODA's marine sediment topic carries no pesticide, "
                     "and this project could not locate Danish pesticide use at any unit finer "
                     "than the nation.")
            + " " + C("C-EA-X17-BAN", "A ban would create a comparison, and would put its "
                      "whole cost on the people asked to absorb it."),
            "note": [C("C-EA-X17-NOTE", "It would supply **a real counterfactual for the "
                       "chemical argument**, at the scale the argument is made, without "
                       "withholding the treatment from anyone.")
                     + " " + C("C-EA-X17-PLACES", "The general form of that observation is "
                               "the meta-solution in [PLACES.md](PLACES.md): a country that "
                               "does one thing everywhere has spent the contrast that would "
                               "have told it whether the thing worked, and a staggered order "
                               "is how you buy it back.")],
        },
        "X21": {
            "why": C("C-EA-X21-WHY", "The spildevandsdata.dk extract of the utilities' PULS "
                     f"reports holds {v['outfalls']:,} outfalls, each with a point position "
                     "and a reported reduced impervious area, and "
                     f"{v['with_volume']:,} of them with an annual volume. No national map of "
                     "which ground drains to which was found among the sources this project "
                     "surveyed.")
            + " " + C("C-EA-X21-LER", "The pipe geometry is held in Ledningsejerregistret, "
                      "which is not open data, so the network cannot be looked up here. It may "
                      "be inferable."),
            "control": C("C-EA-X21-CTRL", f"The {v['outfalls']:,} reported areas are the "
                         "control: they come from the utilities' reports, not from the terrain "
                         "analysis they would be compared with. A delineation that reproduces "
                         "them is doing something right; one that cannot is falsified without "
                         "fieldwork. Hold out a random tenth to fit nothing and check against "
                         "those."),
            "measure": C("C-EA-X21-MEAS", "Terrain, building footprints with year built, and "
                         "the outfall register. Plus, where a municipal wastewater plan "
                         "publishes real catchment boundaries, those become a second and much "
                         "harder test."),
            "note": [C("C-EA-X21-NOTE", "It produces a plausible network, not the real one, "
                       "and every use must say so. This project has a drainage reconstruction "
                       f"for Copenhagen only, because its {v['sheets']} flood PDFs were "
                       "published and their georeferencing could be recovered.")],
        },
        "X22": {
            "why": C("C-EA-X22-WHY", f"The marine map inherits the {v['wb']} water-body "
                     "polygons of the national layer, and every statistic computed in them "
                     "inherits that drawing. Across every subset of up to four station "
                     "variables, those water bodies agree with the partitions the data produce "
                     "no better than random connected regions of the same sizes.")
            + " " + C("C-EA-X22-Q", "The question is whether those lines are where the sea "
                      "changes."),
            "manipulate": C("C-EA-X22-MANIP", "Nothing physical. The satellite record supplies "
                            "a field with no station placement in it: Copernicus Marine's "
                            "Baltic ocean-colour product is daily, at "
                            f"{v['km']} km in its multi-sensor series, from 1997, merged from "
                            "sensors from SeaWiFS to OLCI - so the partition can be derived "
                            "from the water rather than imposed on it."),
            "control": C("C-EA-X22-CTRL", "**The null is to be measured first**: similarity of "
                         "log Kd490 against separation, pooled over days, says how much two "
                         "points a given distance apart should agree wherever they are. Take "
                         "pairs at a fixed separation that straddle an official boundary and "
                         "pairs at the same separation that do not. A boundary that is real "
                         "shows *less* agreement across it than the curve predicts; one that "
                         "agrees more than the curve predicts is splitting water that behaves "
                         "as one thing."),
            "note": [C("C-EA-X22-NOTE", "Two limits stated in advance. The satellite sees only "
                       "the surface. And a partition discovered from one variable is a "
                       "partition for that variable: the baskets for light need not be the "
                       "baskets for oxygen, and finding that they differ would itself dispose "
                       "of the idea that one set of lines can serve every purpose.")],
        },
        "X8": {
            "why": C("C-EA-X8-WHY", "The CTD extract carries the supplier, the sampling gear, "
                     "the sonde, the technical instruction used, and both the original and the "
                     "corrected result with the correction factor.")
            + " " + C("C-EA-X8-GEAR", f"The gear, though, is `Ketcher` on {v['ketcher']}% "
                      "of rows, and `SondeNr` is the `999` placeholder, probe unknown, on "
                      f"{v['s999']}%."),
            "note": [C("C-EA-X8-NOTE", "**No fieldwork and no permission required:** the "
                       "extract carrying these columns is on disk.")],
        },
    }


# The kinds of work and the scales, as the page words them. The register's own
# wording (KINDS, SCALES) carried a price, durations and shares in words that nothing
# counted; the page says what can be justified.
KIND_WORDS = {
    "measurement": "You observe something real that nobody recorded. It creates the "
                   "*record* rather than the evidence: it can establish what is happening, "
                   "where and when, but not why. It still requires being there.",
    "instrument": "You make the thing that takes the reading, and put it where nobody was "
                  "looking. It is a measurement project with a build phase, and it differs "
                  "from the others in what it can be aimed at: **a network can be pointed at "
                  "the assumptions of the existing monitoring**, not only at the sea. Whether "
                  "one station can stand for a water body, whether monthly sampling sees a "
                  "six-hour event, what an aggregation costs - all of those are questions "
                  "about the instrument, and all of them are answerable by building a denser "
                  "one beside it.",
    "analysis": "You work on what is already written down. It can establish consistency, "
                "bound magnitudes, expose contradictions and kill hypotheses - but it cannot "
                "establish causation, and it cannot recover a fact that was never recorded. "
                "**Everything this project has produced is of this kind**: none of the data "
                "it works on was measured by the project itself. A finding of the form *your "
                "evidence does not support what you claim* is a real result and a limited "
                "one.",
}
SCALE_WORDS = {
    "small": "Fieldwork one person or a small group could run, with no institution required.",
    "lab": "A university lab.",
    "programme": "A funded programme or ship time, but still a bounded experiment rather "
                 "than a monitoring commitment.",
    "desk": "No fieldwork of its own; the analysis has not been run here.",
}


def values(hyp):
    """The live values the page reads, by name."""
    J = lambda *p: live.live_json(os.path.join(*p))
    ej, tri = J(DERIVED, "experiments.json"), J(DERIVED, "triage.json")
    sol, obs, of = J(DERIVED, "solutions.json"), J(DERIVED, "observing.json"), J(DERIVED, "outfalls.json")
    man = J(ROOT, "docs", "data", "flood2012", "manifest.json")
    co, sw = of["layers"]["combined_overflow"], of["layers"]["separate_stormwater"]
    # the page says every outfall reports a reduced area; refuse it if that stops holding
    for lay in (co, sw):
        if lay["totals"]["Red areal"]["n"] != lay["n"]:
            raise live.Unjustified("experiments: not every outfall now reports a reduced area")
    dce = "DCE-STATMOD-2015"
    return {
        "known": ({h["id"] for h in hyp["hypotheses"]} | {u["id"] for u in hyp["unquantifiable"]}
                  | {o["id"] for o in hyp["observables"]} | {r["id"] for r in hyp["routes"]}
                  | {t["id"] for t in hyp["terminal"]}) - {r[0] for r in X},
        "ej": ej, "tri": tri,
        "rbu": sol["register"]["discharge_points"],
        "co_n": co["n"], "co_count": co["totals"]["Antal overløb"]["n"],
        "outfalls": co["n"] + sw["n"],
        "with_volume": co["totals"]["Vand_(m3/ aar)"]["n"] + sw["totals"]["Vand_(m3/ aar)"]["n"],
        "wb": obs["sizes"]["n"], "bath": obs["variance"]["share_between_wb"],
        "sheets": man["n_sheets"],
        "dce29": RD(dce, 29, "Der er blevet udviklet statistiske modeller for 29 kystnære "
                             "overvågningsstationer"),
        "dce22": RD(dce, 22, "som repræsenterer 22 vandområder"),
        "dce6a": RD(dce, 6, "Der bruges 6 års data til beregning af månedsfrekvenser"),
        "dce6b": RD(dce, 6, "Der fremkommer én indikator værdi pr. 6. år"),
        "km": RD("KD-CMEMS-OC133", 1, "Spatial resolution**: 1 km for"),
        "ketcher": RS("{calc@K-SUBSET-SHARE:hy_ctd_ketcher / hy_ctd_rows * 100|.1f}"),
        "s999": RS("{calc@K-SUBSET-SHARE:hy_ctd_999 / hy_ctd_rows * 100|.1f}"),
    }


def render(rows, hyp):
    v = values(hyp)
    ej, tri = v["ej"], v["tri"]
    words = page_words(v)
    o = []
    a = o.append
    by_scale = {}
    for r in rows:
        by_scale.setdefault(r[4], []).append(r)

    a("# Experiments, not studies\n")
    a(C("C-EA-I-TRIAGE", f"Of the {tri['n_triaged']} hypotheses this project triaged, "
        f"{tri['classes']['unscoreable']['n']} are unscoreable because the deciding "
        "measurement is in none of the sources it surveyed, and "
        f"{tri['classes']['experiment']['n']} more need an experiment that no surveyed source "
        "reports.") + " " +
      C("C-EA-I-WEAKER", "That is untestable **with the monitoring and data that exist**, "
        "which is a different claim from untestable, and a weaker one. A national observing "
        "programme answers questions about what is happening; a manipulation with a control "
        "answers questions about what causes what, and several of the open questions here "
        "would yield to one that fits in a season and a small boat.") + "\n")
    a(C("C-EA-I-FAIL", "The distinction matters because a study and an experiment fail "
        "differently. An analysis of existing data can always be argued with — the "
        "confounders are real, the record is short, the aggregation lost the signal. An "
        "experiment with a control and a decision rule fixed in advance either falsifies the "
        "hypothesis or does not.") + "\n")
    a(C("C-EA-I-RULE", "So every entry below states its decision rule **before** anyone runs "
        "it.") + "\n")
    a("> " + C("C-EA-I-STERILE", "**The recurring design element is the sterilised control** "
               "— the same material, autoclaved or irradiated, run alongside the live one: "
               "the organisms taken out, the material left. It separates *the chemistry of "
               "this stuff* from *the organisms in it* in a single step, and that is exactly "
               f"the distinction {R('T4')} and {R('T5')} turn on.") + "\n")

    a("## Three kinds of work, which are not interchangeable\n")
    for kid, label, what in KINDS:
        a(C(f"C-EA-K-{kid.upper()}", f"**{label} — `{kid}`** ({ej['by_kind'][kid]} of "
            f"{ej['n_experiments']} below). {KIND_WORDS.get(kid, what)}") + "\n")
    a(C("C-EA-K-NAMING", "Naming them separately matters because they are not substitutes "
        "and they are not equally strong. Only an experiment establishes causation. Only a "
        "measurement can recover something nobody wrote down. Analysis is the cheapest and "
        "the weakest, and it is what a project like this one can do from a desk — so it "
        "should be honest that its output is of that kind, and that the step up in force "
        "comes from going and looking.") + "\n")

    a("## What it would take\n")
    a("| | | experiments |")
    a("|---|---|---|")
    for key, _ in SCALES:
        ids = [r[0] for r in rows if r[4] == key]
        a(f"| `{key}` | {C('C-EA-S-' + key.upper(), SCALE_WORDS[key])} | "
          f"{', '.join(ids) if ids else '—'} |")
    a("")
    a(C("C-EA-S-COUNT", f"**{ej['no_institution']} of {ej['n_experiments']} need no "
        f"institution**, and {ej['by_scale']['desk']} need no fieldwork of their own.") + " " +
      C("C-EA-S-X8", "One of those, `X8` - whether the national trends are in the sea or in "
        "the instruments - runs on the CTD extract already on disk.") + "\n")

    for key, _ in SCALES:
        rs = by_scale.get(key, [])
        if not rs:
            continue
        a(f"## {SCALE_HEAD[key]}\n")
        for xid, title, kind, settles, _, why, manip, ctrl, meas, decide, note in rs:
            x = dict(zip([p[0] for p in PARTS], (why, manip, ctrl, meas, decide, note)))
            mine = words.get(xid, {})
            fam = "terminal" if xid in OUTCOME_ENTRIES else "hypotheses"
            a(f"### {xid} — {title}\n")
            named = ", ".join(R(h, True, fam if _amb(h) else None) for h in settles)
            a(C(f"C-EA-{xid}-FRAME", f"`{kind}` · **Bears on:** {named}") + "\n")
            for part, tag, lead in PARTS:
                if part in mine:
                    body = mine[part]
                else:
                    if "\n\n" in x[part]:
                        raise live.Unjustified(f"experiments: {xid} {part} is two paragraphs "
                                               "- give each its own claim in PAGE")
                    body = C(f"C-EA-{xid}-{tag}", checked(xid, x[part], v))
                if part == "note":
                    for p in (body if isinstance(body, list) else [body]):
                        a(f"*{p}*\n")
                else:
                    a(f"{lead}{body}\n")

    a("## What each entry has to have\n")
    a(C("C-EA-C-TESTS", "Each entry states a control, a decision rule written before the "
        "result, and an outcome that would change what someone does.") + "\n")
    a(C("C-EA-C-LIMIT", "It is also worth saying what these experiments cannot do. None of "
        "them settles the national attribution question, because that is a question about a "
        "whole country over decades and no manipulation reaches it. What they settle is "
        "whether the *mechanisms* the attribution assumes actually operate — which is the part "
        "currently taken on trust in every direction, this project's included.") + "\n")
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
               {"n_experiments": len(X),
                "by_kind": {k: sum(1 for r in X if r[2] == k) for k, _, _ in KINDS},
                "by_scale": {k: sum(1 for r in X if r[4] == k) for k, _ in SCALES},
                "no_institution": sum(1 for r in X if r[4] in ("small", "desk")),
                "scales": [{"id": k, "what": w} for k, w in SCALES],
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
