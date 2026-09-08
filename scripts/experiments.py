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
from common import DERIVED, ROOT, log, read_json, write_json

OUT = os.path.join(ROOT, "docs", "EXPERIMENTS.md")

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
    ("X1", "Does eelgrass fail because the sediment is sick?",
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

    ("X2", "Is eelgrass killed by darkness, or by sulphide that darkness lets in?",
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

    ("X3", "Does fat lower measured nitrogen?",
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

    ("X4", "Does a small organic input unlock a large old one?",
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

    ("X5", "How long does a trawl track take to heal, and what does it release?",
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

    ("X6", "Is silicon the limiting nutrient, and does adding it bring diatoms back?",
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

    ("X7", "Measure the greasy layer, at all",
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

    ("X8", "Are the trends in the sea or in the instruments?",
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

    ("X9", "Does anything happen after an overflow?",
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

    ("X10", "Put it back and see if it holds",
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

    ("X11", "Does skewing the nutrient ratio make the gel?",
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

    ("X12", "Do the filter feeders clear the water?",
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
]


def render(rows, hyp):
    o = []
    a = o.append
    by_scale = {}
    for r in rows:
        by_scale.setdefault(r[3], []).append(r)
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

    a("## What it would take\n")
    a("| | | experiments |")
    a("|---|---|---|")
    for key, what in SCALES:
        ids = [r[0] for r in rows if r[3] == key]
        a(f"| `{key}` | {what} | {', '.join(ids) if ids else '—'} |")
    a("")
    cheap = [r for r in rows if r[3] in ("small", "desk")]
    a(f"**{len(cheap)} of {len(rows)} need no institution.** Two need no fieldwork "
      f"or none of their own. The most consequential — X8, whether the national "
      f"trends are in the sea or in the instruments — is a desk exercise on data "
      f"that is already downloaded.\n")

    for key, what in SCALES:
        rs = by_scale.get(key, [])
        if not rs:
            continue
        a(f"## {key.capitalize()} — {what}\n")
        for xid, title, settles, _, why, manip, ctrl, meas, decide, note in rs:
            a(f"### {xid} — {title}\n")
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
    bad = [(r[0], h) for r in X for h in r[2] if h not in known]
    if bad:
        log(f"  WARNING: unknown hypothesis ids referenced: {bad}")
    write_json(os.path.join(DERIVED, "experiments.json"),
               {"scales": [{"id": k, "what": w} for k, w in SCALES],
                "experiments": [{"id": a_, "title": b_, "settles": c_, "scale": d_,
                                 "why": e_, "manipulate": f_, "control": g_,
                                 "measure": h_, "decide": i_, "note": j_}
                                for a_, b_, c_, d_, e_, f_, g_, h_, i_, j_ in X]})
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(X, hyp))
    log(f"wrote docs/EXPERIMENTS.md ({os.path.getsize(OUT):,} chars)")
    cheap = sum(1 for r in X if r[3] in ("small", "desk"))
    log(f"  {len(X)} experiments; {cheap} need no institution")
    log(f"  covering {len({h for r in X for h in r[2]})} hypotheses")
    return 0


if __name__ == "__main__":
    sys.exit(main())
