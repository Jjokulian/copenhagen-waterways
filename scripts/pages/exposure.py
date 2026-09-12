#!/usr/bin/env python3
"""Generate docs/EXPOSURE.md - documenting what pollution does to a body.

A project outline, not a findings page. Every number on it is read from a pinned
document, and every statement is a checked claim (LIVE_NUMBERS.md section 11),
registered in data/manual/claims.d/w3-le.json with what it rests on. What the page
once said and could not justify is in docs/ARCHIVE.md, not here. The page names no
private individual: the Parkersburg case is described at the level of the case.

    python3 scripts/pages/exposure.py

Writes docs/EXPOSURE.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import ROOT, log, write_doc
import claims as _claims
import live

OUT = os.path.join(ROOT, "docs", "EXPOSURE.md")
C, B, E = live.claim, live.claim_begin, live.CLAIM_END
_REG = {}


def _cl():
    if "d" not in _REG:
        _REG["d"] = _claims.load()[0]
    return _REG["d"]


def RD(sid, value, phrase):
    """A number read from a pinned document, refused unless the pinned copy holds the
    phrase (tags set aside and entities read, as the claims register compares it).
    Each reading has its own phrase: two readings with one phrase would share an id."""
    d = _cl()
    if _claims._flat(phrase) not in _claims._flat(_claims.pin_text(d, sid)):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    return live._mk(value, ["reading", sid, "phrase", phrase, _claims._meta(d, sid)])


def render():
    m1 = RD("LE-FVST-KORSOR-PR", 156, "kalvekød er på hhv. 156")
    m2 = RD("LE-FVST-KORSOR-PR", 189, "hhv. 156, 189 og")
    m3 = RD("LE-FVST-KORSOR-PR", 230, "189 og 230 nanogram pr. gram kød")
    n_samples = RD("LE-FVST-KORSOR-27", 27, "analyseret 27 prøver fra Korsør")
    n_residents = RD("LE-BEREDSKAB-179", 179, "179 borgere skal undersøges for")
    n_docs = RD("LE-UCSF-LIB", 39, "The first collection includes 39 documents")

    o = []
    w = o.append
    w("# Documenting what pollution does to a body")
    w("")
    w(C("C-LE-X-KIND", "**This is a documentation project, not an investigation page.**") + " "
      + C("C-LE-X-OTHERS", "The investigation pages of this site work on Danish coastal water "
          "and report what its data supports.") + " "
      + C("C-LE-X-QUESTION", "This page works on a different question — *what does high "
          "exposure actually do to a living organism, and who has ever recorded it*") + " — "
      + C("C-LE-X-SEPARATE", "and it is kept separate because nothing here depends on it. It is "
          "related to the rest of the reading and is a prerequisite for none of it."))
    w("")
    w(C("C-LE-X-EXISTS", "It exists because the recurring finding of this project arrives one "
        "layer further out here. The thing that is easy to count gets counted, and the thing "
        "that would show what the count *means* does not."))
    w("")
    w("## The problem")
    w("")
    w(C("C-LE-X-CONC", "The Danish monitoring this project has profiled produces concentrations. "
        "It does not produce images of consequence, and the two are not substitutes."))
    w("")
    w("**Korsør, 2021.** "
      + C("C-LE-X-KOR-MEAT", f"Fødevarestyrelsen reported PFOS in three samples of meat from "
          f"cattle from Korsør Nor at {m1}, {m2} and {m3} ng/g — its press release calls them "
          "calf meat, while its final report lists the same three values under beef cuts, "
          "beside a separate calf sample.") + " "
      + C("C-LE-X-KOR-27", f"It analysed {n_samples} samples from Korsør that year, among them "
          "beef, fish, fruit, berries, vegetables and honey,") + " "
      + C("C-LE-X-KOR-179", f"and {n_residents} residents who had eaten meat from cattle that "
          "grazed near the fire school in Korsør were to be examined for PFOS in their "
          "bodies.") + " "
      + C("C-LE-X-KOR-CONC", "Every one of those is a measurement of a *concentration* — in the "
          "food, and then in the people.") + " "
      + C("C-LE-X-KOR-NOTHING", "In the sources searched — the agency's results page, final "
          "report and press release, and the news reports found — nothing records what the "
          "animals looked like, whether they were examined beyond a meat assay, or what "
          "symptoms if any they showed. The exposure is on record as a number in the food chain, "
          "not as an effect in an organism."))
    w("")
    w(C("C-LE-X-PKB", "**Parkersburg, West Virginia**: a farmer whose cattle were dying, on land "
        "downstream from a landfill where DuPont had been dumping, filmed his herd, and his "
        "footage is in the documentary *The Devil We Know*.") + " "
      + C("C-LE-X-PKB-COUNTER", "It is the counter-case: there the harm was recorded as an effect "
          "in whole animals, by the person it happened to."))
    w("")
    w(C("C-LE-X-WHY", "**Why it matters.** Dose–response at the high end is where a mechanism "
        "shows itself, and whole-organism failure is a kind of evidence a hazard ratio cannot "
        "carry.") + " "
      + C("C-LE-X-WHY-ABSENT", "None of the Danish sources this project has profiled holds a "
          "record of that kind."))
    w("")
    w(C("C-LE-X-PAPER", "**The asymmetry worth noting.** The *paper* record from that litigation "
        "is open. Documents from it, dating from 1961 to 2006, were given to the producers of "
        "*The Devil We Know*, who donated them to UCSF's Chemical Industry Documents Library, "
        f"where the first of its two PFAS collections holds the {n_docs} documents featured in "
        "the film; the library is best known for its tobacco archive and its growing opioid "
        "archive.") + " "
      + C("C-LE-X-VIDEO", "**The video is another matter:** who holds the farmer's footage, and on "
          "what terms, is not in any source found."))
    w("")
    w("**What would settle it.**")
    w("")
    w("- " + C("C-LE-X-SETTLE-1", "Locate the farmer's film archive and establish who holds it."))
    w("- " + C("C-LE-X-SETTLE-2", "Ask Fødevarestyrelsen and DTU Fødevareinstituttet whether the "
               "Korsør animals were examined beyond the meat assay, and whether anything was "
               "photographed or necropsied."))
    w("- " + C("C-LE-X-SETTLE-3", "For everything since: a standing, provenanced archive of visual "
               "documentation of pollution effects, contributed by the people it happens to."))
    w("")
    w(C("C-LE-X-LARGER", "**This is larger than this project.** It is its own thing — "
        "*documenting pollution effects* — and it needs an archive, a contribution standard, a "
        "provenance chain and a licence model, none of which belong in a repository about "
        "Copenhagen's sewers. It is recorded here because this project kept running into the gap "
        "and could not fill it.") + " "
      + C("C-LE-X-LOG", "The nearest thing here is `viz/log.html`, an offline field log for rain "
          "and flooding, built for one hand on a phone and kept in the browser so that it works "
          "with no signal, whose depth options are the bands of the 2012 flood model sheets — the "
          "right shape, for one observer at a time."))
    w("")
    w("## Why it is its own project")
    w("")
    w(C("C-LE-X-THREE", "Three reasons it does not belong inside a repository about Danish coastal "
        "water, and one reason it belongs beside it."))
    w("")
    w(C("C-LE-X-OBJECT", "**It is a different object of study.** The investigation pages study the "
        "sea; the public record studies what was said about it; this studies whole-organism "
        "effect and its documentation. Those have different evidentiary standards and mixing them "
        "lets a claim about one borrow credibility from another."))
    w("")
    w(C("C-LE-X-NOTDANISH", "**It is not Danish.** The one whole-organism record this page names "
        "is American, and it was made by the farmer, not by an institution; the Danish case it "
        "names is on record only as concentrations."))
    w("")
    w(C("C-LE-X-NODEP", "**It has no dependency in either direction.** Nothing in the "
        "investigation needs it, and it needs nothing from the investigation. Read it or do not; "
        "the argument about Danish water is unchanged either way."))
    w("")
    w(C("C-LE-X-BESIDE", "**And it belongs beside it** because it asks the question the rest of "
        "the site keeps raising and cannot settle: what would it take for a harm nobody is "
        "measuring to become visible at all. [`X19` and `X20`](EXPERIMENTS.md) ask it for Danish "
        "water — a panel that reports on a schedule, including the days nothing happens, and "
        "dated accounts from the people with the longest baseline."))
    w("")
    w("## What would go in it")
    w("")
    w(C("C-LE-X-NOTDONE", "Nothing here is done. The scope, if it is ever built:"))
    w("")
    w("- " + C("C-LE-X-SCOPE-1", "**The archives that are already open**, and what is in them."))
    w("- " + C("C-LE-X-SCOPE-2", "**The asymmetry between paper and image** in what reaches public "
               "archives after litigation, and the reasons for it."))
    w("- " + C("C-LE-X-SCOPE-3", "**The cases where a whole-organism record exists**, what made "
               "those different, and who made the record. In the one case named here it was the "
               "affected farmer."))
    w("- " + C("C-LE-X-SCOPE-4", "**The Danish equivalent, which this project has not found.** No "
               "open register of fish kills, no photographic record of a fouled shore and no "
               "examination of an affected animal beyond a residue assay turned up in the sources "
               "searched."))
    w("- " + C("C-LE-X-SCOPE-5", "**What a deliberately-built record would need** to be evidence "
               "rather than a gallery: the null, the date, the position, and a defined observable "
               "— the things `X19` turns on."))
    w("")
    w("---")
    w("")
    w("*" + C("C-LE-X-FOOTER", "Every statement on this page is a checked claim, with what it rests "
              "on in [CLAIMS.md](CLAIMS.md). Read it as a project outline rather than as "
              "findings.") + "*")
    return "\n".join(o).rstrip("\n") + "\n"


def main(argv):
    try:
        write_doc(OUT, render())
    except (live.Unjustified, _claims.Refused) as e:
        log(str(e))
        return 1
    log("wrote docs/EXPOSURE.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
