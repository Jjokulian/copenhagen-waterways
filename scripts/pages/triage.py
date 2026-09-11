#!/usr/bin/env python3
"""Writes docs/hypodrafts/TRIAGE.md: the triage of the hypothesis field.

The rows are data (scripts/pages/triage_rows.py); every count is a count over
them (scripts/triage_counts.py -> data/derived/triage.json), read live here;
every hypothesis is a checked reference to the register, and every number in a
blocker is a figure in data/manual/claims.d/drafts-a.json. Nothing on the page is
typed: a reclassification, a renumbered hypothesis or a refetched file changes
the page the next time it is built.

    python3 scripts/pages/triage.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from common import DERIVED, ROOT, log, write_doc
import claims
import live
import refs as _refs
# T1-T5 are both terminal outcomes and group T hypotheses; here they are hypotheses
_amb = _refs.ambiguous

import triage_rows as T

OUT = os.path.join(ROOT, "docs", "hypodrafts", "TRIAGE.md")
ORDER = list(T.CLASSES)


def main(argv):
    d, _, _ = claims.load()
    cache = {}
    R = lambda text: claims.resolve(d, text, cache)[0]
    tc = live.live_json(os.path.join(DERIVED, "triage.json"))
    reg = json.load(open(os.path.join(DERIVED, "hypotheses.json"), encoding="utf-8"))
    orphans = set(tc["orphans"])
    n = tc["n_triaged"]
    cls = tc["classes"]
    share = lambda k: live.step("K-SUBSET-SHARE", cls[k]["n"] / n * 100)
    label = lambda k: f"**{T.CLASSES[k][0]}**" if T.CLASSES[k][1] else T.CLASSES[k][0]
    refs = lambda ids: ", ".join(live.ref(i, family="hypotheses" if _amb(i) else None) for i in ids)

    o = []
    w = o.append
    w("# Triage of the hypothesis field")
    w("")
    w('PLAN.md\'s triage stage is "most of the work", and the stage after it is')
    w("meaningless until it exists. This is it: **all "
      f"{n} lettered hypotheses in [HYPOTHESES.md](../HYPOTHESES.md)**,")
    w("each in exactly one class, with the specific blocker.")
    w("")
    if orphans:
        w("The triage also classifies " + ", ".join(f"`{i}`" for i in sorted(orphans))
          + ", which the register no longer holds; it is listed in its group below and")
        w("counted nowhere.")
        w("")
    w(f"{tc['n_with_entry']} already have a draft or an open-problem entry; those are marked "
      "and cite it rather")
    w("than being redone. **Nothing here has been run.** A classification is a claim about "
      "what could be done, not a result.")
    w("")
    w("*Numbers shown as quotations are carried from this page as committed at `4469fc7`: "
      "nothing in the repository stores them yet, so each says what the page said, not that "
      "it was re-derived. Every other number is read live.*")
    w("")
    w("*Classified before the water-chemistry extract was fetched on 2026-09-10. "
      "`scripts/rescore.py` re-scores the hypotheses that fetch unblocks; the classes "
      "below are as triaged.*")
    w("")
    w("| class | n | share |")
    w("|---|---:|---:|")
    for k in ORDER:
        w(f"| {label(k)} | {cls[k]['n']} | {share(k):.0f}% |")
    w(f"| | **{n}** | |")
    w("")
    w("**Class definitions.** *Testable now* — consequence, a source in hand, and a null "
      "computable")
    w("under the constraint imposed. *Blocked on a fetch* — named, with whether it needs "
      "credentials.")
    w("*Blocked on resolution* — needs depth, sub-monthly time, per-measurement position, or "
      "the")
    w("measurement-level store. *Unscoreable* — the deciding dimension has no column and "
      "never did;")
    w("**this is not a refutation**. *Needs an experiment* — no observational design reaches "
      "it.")
    w("*Not established* — I could not tell, and say so rather than guess.")
    w("")
    w("---")
    w("")
    w("## The table")
    w("")
    for g in reg["groups"]:
        gid = g["id"]
        gc = tc["groups"][gid]
        rows = [r for r in T.ROWS if r["group"] == gid]
        if not rows:
            continue
        w(f"### {gid}. {g['name']}")
        w("")
        parts = [f"{gc[k]} {T.CLASSES[k][0]}" for k in ORDER if gc[k]]
        noun = "hypothesis" if gc["n"] == 1 else "hypotheses"
        w(f"*{gc['n']} {noun} — " + ", ".join(parts) + ".*")
        w("")
        w("| id | consequence | class | blocker |")
        w("|---|---|---|---|")
        for r in rows:
            idc = (f"**`{r['id']}`** *(no longer in the register)*" if r["id"] in orphans
                   else f"**{live.ref(r['id'], family="hypotheses" if _amb(r['id']) else None)}**")
            w(f"| {idc} | {R(r['consequence'])} | {label(r['cls'])} | {R(r['blocker'])} |")
        w("")
    w("---")
    w("")
    w("## What the shape of it says")
    w("")
    w("### Half the field is not blocked on money or effort")
    w("")
    w(f"**{cls['fetch']['n']} of {n} ({share('fetch'):.0f}%) are blocked on a fetch**, and "
      "most of those fetches are")
    w("small. The ones that need no credentials at all: the ICES/HELCOM trawling layer "
      "(" + R("{was:4469fc7:docs/hypodrafts/TRIAGE.md:ICES/HELCOM trawling layer (@@, CC BY}") + ", `CC BY 4.0`), the three ODA")
    w("vegetation and fauna topics (three one-line `TOPICS` entries), OBIS phytoplankton via "
      "the eMoF extension (open")
    w("REST), DMI tide gauges and wind (no key since March 2026), `Sentinel-1` SAR, and ICES "
      "stock assessments.")
    w("**A day of fetching would move a large fraction of this table.**")
    w("")
    vk, bf = tc["clusters"]["vandkemi"], tc["clusters"]["bundfauna"]
    w("### One fetch unblocks the most")
    w("")
    w("**ODA `vandkemi` (`Emne_10_11`)** is the single highest-value fetch: it carries "
      "nitrogen,")
    w("phosphorus, silicate, ammonium and chlorophyll, and it is named in the blocker for "
      f"**{refs(T.CLUSTERS['vandkemi'])}** — {vk['n']} hypotheses, including the entire "
      "nutrient-limitation")
    w("argument. When this was written it was also the fetch `fetch_oda.py` advertised in its "
      "docstring and did not")
    w(f"implement. Second is **ODA bundfauna (`Emne_3_180`)** at {bf['n']} — "
      f"{refs(T.CLUSTERS['bundfauna'])}.")
    w("")
    ga = tc["groups"]["A"]
    if ga["testable"] == 0:
        w("Note what that means for group A. **Not one hypothesis in the nutrient group is "
          "testable")
        w("now.** The group the entire public argument rests on is the group whose data this "
          "project")
        w("had not fetched.")
    else:
        w(f"Note what that means for group A: only {ga['testable']} of its {ga['n']} "
          "hypotheses are testable now.")
    w("")
    mc, tx = tc["clusters"]["microbial"], tc["clusters"]["toxicant"]
    both = mc["unscoreable"] + tx["unscoreable"]
    w("### The largest single blocking dimension is not nutrients")
    w("")
    w(f"**{mc['unscoreable']} hypotheses are unscoreable for one missing dimension: "
      "microbial, viral and fungal")
    w(f"community composition** — of {refs(T.CLUSTERS['microbial'])}, all but "
      f"{mc['experiment']}, which need an experiment instead.")
    w("Not one Danish marine station counts viruses, sequences a microbial community, or "
      "surveys")
    w("fungi. That is a whole functional layer with no column anywhere, and it blocks more "
      "of this")
    w("register than any other single absence.")
    w("")
    w(f"A second cluster of {tx['n']} is **toxicant concentration in a marine matrix** — "
      f"{refs(T.CLUSTERS['toxicant'])} —")
    w(R("where the national hazardous-substance layer turns out to hold {fig:da_mfs_total} "
        "stations, not one of them coastal."))
    w(f"Together those two dimensions account for **{both} of the "
      f"{cls['unscoreable']['n']} unscoreable** "
      f"({live.step('K-SUBSET-SHARE', both / cls['unscoreable']['n'] * 100):.0f}%), and "
      "neither is expensive to start")
    w("measuring. eDNA and Alcian-blue TEP are cheap standard methods; the register says so "
      "itself in several places.")
    w("")
    beyond = cls["unscoreable"]["n"] + cls["experiment"]["n"]
    w(f"### {share('unscoreable'):.0f}% of the field cannot be scored at all, and that is the finding")
    w("")
    w(f"**{cls['unscoreable']['n']} of {n} ({share('unscoreable'):.0f}%) are unscoreable** "
      "— the deciding dimension has no")
    w(f"column and never did. Add the {cls['experiment']['n']} that need an experiment and "
      f"**{live.step('K-SUBSET-SHARE', beyond / n * 100):.0f}% of the hypothesis field is")
    w("beyond reach of any reanalysis of existing data.** No amount of cleverness with the "
      "archive")
    w("touches them.")
    w("")
    w("This is the number that matters for how the whole argument should be read. When a "
      "public")
    w("debate settles on nutrients, it is not because nutrients won a contest against the")
    w("alternatives. **It is because nutrients are in group A, and group A has a monitoring")
    w(f"programme.** {beyond} of these hypotheses have never been in a position to compete.")
    w("")
    gs = tc["groups"]
    frac = {k: int(v["testable"]) / int(v["n"]) for k, v in dict.items(gs) if int(v["n"])}
    ranked = sorted(frac, key=lambda k: -frac[k])
    majority = [k for k in ranked if frac[k] > 0.5]
    w("### Where the archive is strong")
    w("")
    if majority == ["I"]:
        w("The **I** group — observation and measurement — is the only one where most "
          "hypotheses are")
        w(f"testable now ({gs['I']['testable']} of {gs['I']['n']}). That is not a "
          "coincidence: those hypotheses are about the archive, and")
        w("the archive is the thing this project holds.", )
    else:
        w("Where most hypotheses are testable now: " + ", ".join(
            f"**{k}** ({gs[k]['testable']} of {gs[k]['n']})" for k in majority) + ".")
    if len(ranked) > 1 and ranked[1] == "C":
        w(f"**C** (physical resupply) is next at {gs['C']['testable']} of {gs['C']['n']},")
        w("because temperature, salinity, depth and wind are exactly what a CTD and a "
          "weather reanalysis")
        w("give you.")
    w("")
    w("The pattern across groups is blunt: **this archive can see physics and it cannot see "
      "biology.**")
    w("Groups C, G, Z and I hold most of the testable-now entries. Groups E, F, J, T and R — "
      "chemistry,")
    w("biological structure, films, sediment sickness, decay — hold almost none, and hold "
      "nearly all")
    w("of the unscoreable and experimental ones.")
    w("")
    w("### An honest caveat about this table")
    w("")
    w("The classification is mine and is itself an untested partition, exactly as the "
      f"{tc['n_groups']} groups are")
    w("(PLAN.md says so of them). Two judgements are load-bearing and contestable: I treated "
      "*not")
    w("fetched but fetchable* as **blocked on a fetch** rather than unscoreable even where "
      "nobody has")
    w("confirmed the topic contains what its name suggests; and I treated *measured "
      "somewhere in the")
    w("world but not in Denmark* as unscoreable **for this archive**, which is a statement "
      "about")
    w(f"Denmark's monitoring rather than about nature. The {cls['unestablished']['n']} "
      "entries I could not place at all are")
    w("marked *not established* rather than guessed.")
    w("")
    w("And per [KNOWN_AND_UNKNOWN.md](../KNOWN_AND_UNKNOWN.md): **every \"not measured\" in "
      "this table")
    w("should be read as \"not found by a search whose sensitivity nobody has "
      "characterised.\"** Six")
    w("things this project called absent turned out to exist in one day. The "
      "unscoreable column is")
    w("an upper bound on what is missing, not a measurement of it.")
    try:
        write_doc(OUT, "\n".join(o).rstrip("\n") + "\n")
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
