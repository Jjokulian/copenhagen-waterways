#!/usr/bin/env python3
"""Generate docs/EXPOSURE.md - documenting what pollution does to a body.

The prose lives here, verbatim from the page as committed at 4469fc7; the page is
output. The figures on it come from sources this repository does not hold, so each
is carried as a quotation of the page as committed - verified against git, and
honest about what it is: the site once said this, not that it was right. Every such
figure is counted in the conversion report, until a source is pinned for it.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import ROOT, log, write_doc
import live

OUT = os.path.join(ROOT, "docs", "EXPOSURE.md")
COMMIT = "4469fc7"

TEXT = "# Documenting what pollution does to a body\n\n**This is a documentation project, not an investigation page.** Everything else on this\nsite works on Danish coastal water and reports what its data supports. This page works on\na different question — *what does high exposure actually do to a living organism, and who\nhas ever recorded it* — and it is kept separate because nothing here depends on it. It is\nrelated to the rest of the reading and is a prerequisite for none of it.\n\nIt exists because the recurring finding of this project arrives one layer further out\nhere. The thing that is easy to count gets counted, and the thing that would show what\nthe count *means* does not.\n\n## The problem\n\nDanish monitoring produces concentrations. It does not produce images of consequence,\nand the two are not substitutes.\n\n**Korsør, 2021.** Fødevarestyrelsen found PFOS in calf meat at [[calf meat at @@ ng/g, analysed]] ng/g,\nanalysed [[ng/g, analysed @@ samples across]] samples across beef, fish, fruit, berries, vegetables and honey, and offered\n[[and offered @@ residents a]] residents a health examination. Every one of those is a measurement of a\n*concentration* — in the food, and then in the people. Nothing published records what\nthe animals looked like, whether they were examined beyond a meat assay, or what\nsymptoms if any they showed. The exposure was documented as a number in the food chain\nand never as an effect in an organism.\n\n**Parkersburg, 1998–2004**, is the counter-case, and it is the reason anyone outside a\ntoxicology department has heard of PFAS at all. Wilbur Tennant filmed his own herd over\nyears: more than [[more than @@ animals dead]] animals dead one at a time, blackened teeth, tumours, deformities,\ncalves born with white blind eyes, a creek running with foam and a discharge pipe from a\nDuPont landfill. He made that record himself because no official programme covered what\nwas happening to him.\n\n**Why it matters.** Dose–response at the high end is where a mechanism shows itself, and\nwhole-organism failure is a kind of evidence a hazard ratio cannot carry. It is also the\nform of evidence that moves anything. And it is entirely absent from the Danish record —\nwhich is this project's recurring finding arriving one layer further out: the thing that\nis easy to count gets counted, and the thing that would show what it means does not.\n\n**The asymmetry worth noting.** The *paper* record from that litigation is open. Bilott's\ndiscovery documents were donated to UCSF's Industry Documents Library — free, fully\nsearchable, two PFAS collections spanning 1961–2006, including the [[including the @@ documents used]] documents used in\n*The Devil We Know*, alongside the tobacco and opioid archives. **The document archive is\npublic. The video archive is not**, and remains under copyright into the 2070s.\n\n**What would settle it.**\n\n- Locate the Tennant archive and establish who holds it. Both films licensed the footage,\n  so a rights holder exists and has granted permission before.\n- Ask Fødevarestyrelsen and DTU Fødevareinstituttet whether the Korsør animals were\n  examined beyond the meat assay, and whether anything was photographed or necropsied.\n- For everything since: a standing, provenanced archive of visual documentation of\n  pollution effects, contributed by the people it happens to.\n\n**This is larger than this project.** It is its own thing — *documenting pollution\neffects* — and it needs an archive, a contribution standard, a provenance chain and a\nlicence model, none of which belong in a repository about Copenhagen's sewers. It is\nrecorded here because this project kept running into the gap and could not fill it. The\nnearest thing here is `viz/log.html`, an offline field logger that records a shore\nobservation in the flood model's own vocabulary — the right shape, at approximately none\nof the required scale.\n\n## Why it is its own project\n\nThree reasons it does not belong inside a repository about Danish coastal water, and one\nreason it belongs beside it.\n\n**It is a different object of study.** The investigation pages study the sea; the public\nrecord studies what was said about it; this studies whole-organism effect and its\ndocumentation. Those have different evidentiary standards and mixing them lets a claim\nabout one borrow credibility from another.\n\n**It is not Danish, and mostly cannot be.** The cases that carry the evidence are\nelsewhere, and the reason they are elsewhere is itself part of the finding: the exposure\nhad to be extreme and unregulated before anyone was moved to record it.\n\n**It has no dependency in either direction.** Nothing in the investigation needs it, and\nit needs nothing from the investigation. Read it or do not; the argument about Danish\nwater is unchanged either way.\n\n**And it belongs beside it** because it answers the question the rest of the site keeps\nraising and cannot settle: what would it take for a harm nobody is measuring to become\nvisible at all. That is the same question as `X19` and `X20` in\n[EXPERIMENTS.md](EXPERIMENTS.md), asked at a different scale.\n\n## What would go in it\n\nNothing here is done. The scope, if it is ever built:\n\n- **The archives that are already open**, and what is in them.\n- **The asymmetry between paper and image** — discovery documents are routinely donated\n  to public libraries after litigation; film and photographs almost never are, and the\n  reasons are legal rather than scientific.\n- **The cases where a whole-organism record exists**, what made those different, and who\n  made the record. In the known instances it was the affected party, not an institution.\n- **The Danish equivalent, which does not exist.** No open register of fish kills, no\n  photographic record of a fouled shore, no examination of an affected animal beyond a\n  residue assay.\n- **What a deliberately-built record would need** to be evidence rather than a gallery:\n  the null, the date, the position, and a defined observable — the same four things `X19`\n  turns on.\n\n---\n\n*Hand-written. Extracted from `OPEN_PROBLEMS.md` item 9, which now points here. Nothing\nin this page has been verified beyond what that item already stated, and it should be\nread as a project outline rather than as findings.*\n"

# (the passage as committed, the figure within it that is carried as a quotation)
QUOTED = []   # quotations are [[locator]] marks in TEXT now

# identifiers written in words, so the compiler does not take them for quantities
REWORDED = []


def build():
    t = TEXT
    # a quotation is a located reference: [[phrase with @@]] is read out of git
    t = re.sub(r"\[\[(.+?)\]\]", lambda m: live.was(COMMIT, "docs/EXPOSURE.md", m.group(1)), t)
    for old, new in REWORDED:
        assert t.count(old) == 1, old
        t = t.replace(old, new)
    return t


def main(argv):
    try:
        write_doc(OUT, build())
    except live.Unjustified as e:
        log(str(e))
        return 1
    log("wrote docs/EXPOSURE.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
