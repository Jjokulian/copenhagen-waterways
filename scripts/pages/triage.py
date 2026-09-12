#!/usr/bin/env python3
"""Writes docs/hypodrafts/TRIAGE.md: the triage of the hypothesis field.

The rows are data (scripts/pages/triage_rows.py); every count is a count over them
(scripts/triage_counts.py -> data/derived/triage.json), read live here; every
hypothesis is a checked reference to the register. Every assertion on the page is a
checked claim (LIVE_NUMBERS.md section 11), registered in
data/manual/claims.d/w3-tr.json with what it rests on. The table is claimed by its
rule (C-TR-RULE): each row's class is a judgement on its blocker, and a blocker says
only what the source register, the held files and the water-chemistry re-score
(data/derived/rescore.json) say. What the page once said and could not justify is in
docs/ARCHIVE.md, not here.

One count is the page's own: how many water-chemistry stations in the Belts and the
Sound carry total N, ortho-P and silicon, which the A5 row gives. It is counted here
from data/raw/oda/kemi.csv.gz and kept in data/derived/triage_sections.json, and
recounted only when the extract changes.

    python3 scripts/pages/triage.py
"""
import csv
import gzip
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from common import DERIVED, RAW, ROOT, log, write_doc
import claims
import live
import refs as _refs
# T1-T5 are both terminal outcomes and group T hypotheses; here they are hypotheses
_amb = _refs.ambiguous

import triage_rows as T

OUT = os.path.join(ROOT, "docs", "hypodrafts", "TRIAGE.md")
KEMI = os.path.join(RAW, "oda", "kemi.csv.gz")
SECTIONS = os.path.join(DERIVED, "triage_sections.json")
ORDER = list(T.CLASSES)
C = live.claim

# the sections the A5 row names, as the extract's locality names begin
SECTION_PREFIXES = ("Storebælt", "Lillebælt", "Øresund")
SECTION_PARAMETERS = ("Nitrogen,total N", "Ortho-phosphat-P", "Silicium")

# rescore.py's class strings
RS_TESTABLE = "testable now"
RS_PARTLY = "partly unblocked - a second blocker was behind the first"
# the hypotheses C-TR-SECOND names, by what stands behind the fetch
RS_SECOND = {"A1", "A2", "A5", "A7", "B4", "K1", "K2", "E11"}

PHYSICAL = ["C", "G", "Z", "I"]
BIOLOGY = ["F", "J", "T", "R"]


def sections():
    """Stations whose locality is in the Belts or the Sound and that carry all three
    nutrients the A5 row names. Streams the extract once, keeping a set of
    parameters per station; recounted only when the extract's size or time changes."""
    st = os.stat(KEMI)
    key = {"bytes": st.st_size, "mtime": int(st.st_mtime)}
    try:
        old = json.load(open(SECTIONS, encoding="utf-8"))
        if old.get("source") == key:
            return
    except (OSError, ValueError):
        pass
    have, where = {}, {}
    with gzip.open(KEMI, "rb") as fh:
        rd = csv.reader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";")
        head = next(rd)
        ip, il, ist = head.index("Parameter"), head.index("Lokalitetsnavn"), head.index("ObservationsStedNr")
        top = max(ip, il, ist)
        for row in rd:
            if len(row) <= top or row[ip] not in SECTION_PARAMETERS:
                continue
            loc = row[il]
            if not loc.startswith(SECTION_PREFIXES):
                continue
            have.setdefault(row[ist], set()).add(row[ip])
            where[row[ist]] = next(p for p in SECTION_PREFIXES if loc.startswith(p))
    full = sorted(s for s, v in have.items() if len(v) == len(SECTION_PARAMETERS))
    by = {p: sum(where[s] == p for s in full) for p in SECTION_PREFIXES}
    out = {"_what": "Water-chemistry stations whose Lokalitetsnavn begins with one of "
                    "the prefixes, and how many of them carry a row of every one of the "
                    "parameters; counted by scripts/pages/triage.py over "
                    "data/raw/oda/kemi.csv.gz.",
           "source": key, "prefixes": list(SECTION_PREFIXES),
           "parameters": list(SECTION_PARAMETERS),
           "n_stations_any": len(have), "n_stations": len(full),
           "by_prefix": by, "stations": full}
    with open(SECTIONS, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"  counted {len(full)} section stations; wrote {os.path.relpath(SECTIONS, ROOT)}")


def main(argv):
    sections()
    d, _, _ = claims.load()
    cache = {}
    R = lambda text: claims.resolve(d, text, cache)[0]
    tc = live.live_json(os.path.join(DERIVED, "triage.json"))
    rs = live.live_json(os.path.join(DERIVED, "rescore.json"))
    reg = json.load(open(os.path.join(DERIVED, "hypotheses.json"), encoding="utf-8"))
    n = tc["n_triaged"]
    cls = tc["classes"]
    gs = tc["groups"]
    share = lambda k: live.step("K-SUBSET-SHARE", cls[k]["n"] / n * 100)
    label = lambda k: f"**{T.CLASSES[k][0]}**" if T.CLASSES[k][1] else T.CLASSES[k][0]
    ref = lambda i: live.ref(i, family="hypotheses" if _amb(i) else None)

    def refs(ids):
        ids = [ref(i) for i in ids]
        return ids[0] if len(ids) == 1 else ", ".join(ids[:-1]) + " and " + ids[-1]

    cls_of = {r["id"]: r["cls"] for r in T.ROWS}
    # the page says every register entry is triaged, once
    if list(tc["orphans"]) or list(tc["untriaged"]) or int(n) != int(tc["n_register"]):
        raise live.Unjustified("TRIAGE: the rows and the register no longer match - "
                               f"orphans {list(tc['orphans'])}, untriaged {list(tc['untriaged'])}")
    # the re-score and the rows must agree on which of the nine are testable now
    mx = rs["matrix"]
    nine = T.CLUSTERS["vandkemi"]
    if sorted(mx) != sorted(nine):
        raise live.Unjustified(f"TRIAGE: rescore.json scores {sorted(mx)}, the rows name {sorted(nine)}")
    rs_t = [h for h in nine if mx[h]["class"] == RS_TESTABLE]
    rs_p = [h for h in nine if mx[h]["class"] == RS_PARTLY]
    bad = [h for h in nine if (cls_of[h] == "testable") != (h in rs_t)]
    if bad or set(rs_p) != RS_SECOND or len(rs_t) + len(rs_p) != len(nine):
        raise live.Unjustified(f"TRIAGE: the rows' classes for {bad or nine} no longer follow "
                               "rescore.json, or its partly-unblocked set is not the one the "
                               "page names")

    o = []
    w = o.append
    w("# Triage of the hypothesis field")
    w("")
    w(C("C-TR-ALL", f"This page puts **all {n} lettered hypotheses in "
        "[HYPOTHESES.md](../HYPOTHESES.md)** each in exactly one class, with the specific "
        "blocker."))
    w("")
    w(C("C-TR-ENTRIES", f"{tc['n_with_entry']} of them have a draft or an open-problem page "
        "of their own, and their identifiers link to it.") + " "
      + C("C-TR-NOTRESULT", "A classification says what testing a hypothesis would need and "
          "whether that is held here; it is not a test result."))
    w("")
    w(C("C-TR-COUNTS", "Counted over the rows, restricted to the identifiers the register "
        "holds, the classes stand at:"))
    w("")
    w("| class | n | share |")
    w("|---|---:|---:|")
    for k in ORDER:
        w(f"| {label(k)} | {cls[k]['n']} | {share(k):.0f}% |")
    w(f"| | **{n}** | |")
    w("")
    w(live.claim_begin("C-TR-CLASSES") + "**Class definitions.** *Testable now* — consequence, "
      "a source in hand, and a null computable")
    w("under the constraint imposed. *Blocked on a fetch* — named, with whether it needs "
      "credentials.")
    w("*Blocked on resolution* — needs depth, sub-monthly time, per-measurement position, or "
      "the")
    w("measurement-level store. *Unscoreable* — the deciding dimension has no column and "
      "never did;")
    w("**this is not a refutation**. *Needs an experiment* — no observational design reaches "
      "it.")
    w("*Not established* — I could not tell, and say so rather than guess." + live.CLAIM_END)
    w("")
    w("---")
    w("")
    w("## The table")
    w("")
    w(C("C-TR-RULE", "Each row's class is a judgement on its blocker: what the row's "
        "consequence needs, and whether this project holds it. A blocker says only what the "
        "source register (`data/manual/data_sources*.json`, the record of what each source "
        "holds and what its searches found), the files held here and, for the hypotheses that "
        "waited on the water-chemistry extract, `scripts/rescore.py` say. *Not found* means "
        "not found in the sources the register surveyed."))
    w("")
    for g in reg["groups"]:
        gid = g["id"]
        gc = gs[gid]
        rows = [r for r in T.ROWS if r["group"] == gid]
        if not rows:
            continue
        w(f"### {gid}. {g['name']}")
        w("")
        parts = [f"{gc[k]} {T.CLASSES[k][0]}" for k in ORDER if gc[k]]
        noun = "hypothesis" if gc["n"] == 1 else "hypotheses"
        w(C(f"C-TR-N-{gid}", f"*{gc['n']} {noun} — " + ", ".join(parts) + ".*"))
        w("")
        w("| id | consequence | class | blocker |")
        w("|---|---|---|---|")
        for r in rows:
            w(f"| **{ref(r['id'])}** | {R(r['consequence'])} | {label(r['cls'])} | {R(r['blocker'])} |")
        w("")
    w("---")
    w("")
    w("## What the shape of it says")
    w("")
    w("### Blocked on a fetch")
    w("")
    w(C("C-TR-FETCH", f"**{cls['fetch']['n']} of {n} ({share('fetch'):.0f}%) are blocked on a "
        "fetch**: what they need is named and is not held here.") + " "
      + C("C-TR-OPEN", "The source register records some of those sources as open without a "
          "login: the ICES swept-area-ratio product and HELCOM's fishing-intensity layers, ICES "
          "stock assessments, OBIS occurrences, and DMI's sea-level and weather series, "
          "unauthenticated in its testing. `Sentinel-1` scenes need a free account. ODA's "
          "bottom-fauna and vegetation topics need the ODA registration this project already "
          "uses, and are not in `fetch_oda.py`'s topic list. Phytoplankton counts need "
          "credentials: VanDa refused access, and the ICES route needs an account."))
    w("")
    vk, bf = tc["clusters"]["vandkemi"], tc["clusters"]["bundfauna"]
    tl = rs["tally"]
    one = int(tl[RS_TESTABLE]) == 1
    w("### The water-chemistry extract, re-scored")
    w("")
    w(C("C-TR-RESCORE", "The ODA water-chemistry extract (`vandkemi`, `Emne_10_11`) was named "
        f"in the blocker for {refs(nine)} — {vk['n']} hypotheses. It is now held, and "
        "`scripts/rescore.py` checks each against it: "
        f"**{tl[RS_TESTABLE]} {'has' if one else 'have'} every variable {'its' if one else 'their'} "
        f"consequence needs and {'is' if one else 'are'} testable "
        f"now, {refs(rs_t)}**; for the other {tl[RS_PARTLY]} a second blocker stood behind the "
        "first.") + " "
      + C("C-TR-SECOND", f"{refs(['A1', 'A2', 'A7'])} need river input, on ODA topics "
          f"`fetch_oda.py` does not reach; {ref('A5')} needs volume transport at the Belt and Sound "
          f"sections, which no open series the source register found carries; {ref('B4')} needs stream stations, outside the "
          f"marine topic; {refs(['K1', 'K2'])} need phytoplankton counts, which are not held; "
          f"and {ref('E11')} needs a temperature from the same bottle."))
    w("")
    ga = gs["A"]
    a_test = [r["id"] for r in T.ROWS if r["group"] == "A" and r["cls"] == "testable"]
    if len(a_test) != int(ga["testable"]):
        raise live.Unjustified("TRIAGE: group A's testable rows and its count disagree")
    rest = [T.CLASSES[k][0] for k in ORDER if k != "testable" and int(ga[k])]
    rest = rest[0] if len(rest) == 1 else ", ".join(rest[:-1]) + " or " + rest[-1]
    if a_test:
        verb = "is" if len(a_test) == 1 else "are"
        w(C("C-TR-GROUPA", f"In group A, the nutrient group, {ga['testable']} of {ga['n']} "
            f"{verb} testable now: {refs(a_test)}. The rest are {rest}."))
    else:
        w(C("C-TR-GROUPA", f"No hypothesis in group A, the nutrient group, is testable now; its "
            f"{ga['n']} are {rest}."))
    w("")
    if int(bf["fetch"]) != int(bf["n"]):
        raise live.Unjustified("TRIAGE: the page calls every bottom-fauna row a fetch not yet made")
    w(C("C-TR-BUNDFAUNA", "Of the fetches not yet made, ODA's bottom-fauna topic (`bundfauna`) "
        f"is named in the blocker for {bf['n']}: {refs(T.CLUSTERS['bundfauna'])}."))
    w("")
    mc, tx = tc["clusters"]["microbial"], tc["clusters"]["toxicant"]
    others = [int(tc["clusters"][c]["n"]) for c in T.CLUSTERS if c != "microbial"]
    extra = {k for k in ORDER if k not in ("unscoreable", "experiment", "fetch") and int(mc[k])}
    if extra or int(mc["n"]) <= max(others):
        raise live.Unjustified("TRIAGE: the microbial cluster no longer reads as the page says")
    tail = f"{mc['experiment']} need an experiment instead"
    if int(mc["fetch"]):
        tail += f" and {mc['fetch']} {'waits' if int(mc['fetch']) == 1 else 'wait'} on a fetch"
    w("### The largest named blocking dimension is not nutrients")
    w("")
    w(C("C-TR-MICROBIAL", f"**{mc['unscoreable']} hypotheses are unscoreable for one missing "
        "dimension: microbial, viral and fungal community composition** — among "
        f"{refs(T.CLUSTERS['microbial'])}; of the rest, {tail}.") + " "
      + C("C-TR-MICRO-REG", "National marine monitoring counts no viruses and monitors no "
          "microbial community composition; the Danish sequencing the source register found is "
          "research outside the programme, and for the unscoreable ones none of it records what "
          "they turn on. Of the clusters of blockers this page names, it is the largest."))
    w("")
    both = mc["unscoreable"] + tx["unscoreable"]
    w(C("C-TR-TOXICANT", f"A second cluster of {tx['n']} is **toxicant concentration in a "
        f"marine matrix** — {refs(T.CLUSTERS['toxicant'])} — "
        + R("where the national hazardous-substance layer holds {fig:da_mfs_total} stations, "
            "not one of them coastal.")) + " "
      + C("C-TR-TWO", f"Together those two dimensions account for **{both} of the "
          f"{cls['unscoreable']['n']} unscoreable** "
          f"({live.step('K-SUBSET-SHARE', both / cls['unscoreable']['n'] * 100):.0f}%)."))
    w("")
    beyond = cls["unscoreable"]["n"] + cls["experiment"]["n"]
    w(f"### {share('unscoreable'):.0f}% of the field cannot be scored with any source surveyed")
    w("")
    w(C("C-TR-UNSCOREABLE", f"**{cls['unscoreable']['n']} of {n} ({share('unscoreable'):.0f}%) "
        "are unscoreable**: the deciding measurement is in none of the sources this project "
        "surveyed.") + " "
      + C("C-TR-BEYOND", f"Add the {cls['experiment']['n']} that need an experiment and "
          f"**{live.step('K-SUBSET-SHARE', beyond / n * 100):.0f}% of the hypothesis field is "
          "beyond reach of any reanalysis of the data this project holds or has found.**"))
    w("")
    w(C("C-TR-CONTEST", "This is the number that matters for how the whole argument should be "
        "read. When a public debate settles on nutrients, it is not because nutrients won a "
        f"contest against the alternatives: {beyond} of these hypotheses have not been in a "
        "position to compete."))
    w("")
    frac = {k: int(v["testable"]) / int(v["n"]) for k, v in dict.items(gs) if int(v["n"])}
    ranked = sorted(frac, key=lambda k: -frac[k])
    majority = [k for k in ranked if frac[k] > 0.5]
    w("### Where the archive is strong")
    w("")
    strong = C("C-TR-STRONG", "Where most hypotheses are testable now: " + ", ".join(
        f"**{k}** ({gs[k]['testable']} of {gs[k]['n']})" for k in majority) + ".")
    if "C" in majority:
        strong += " " + C("C-TR-CTD", "In **C**, physical resupply, they are the ones the CTD "
                          "record, the depth soundings, the inflow indicator files and the "
                          "weather reanalysis held here measure: temperature, salinity, oxygen, "
                          "depth and wind.")
    w(strong)
    w("")
    phys = sum(gs[g]["testable"] for g in PHYSICAL)
    bio = sum(int(gs[g]["testable"]) for g in BIOLOGY)
    hard = sum(gs[g]["unscoreable"] + gs[g]["experiment"] for g in BIOLOGY + ["E"])
    if bio:
        raise live.Unjustified("TRIAGE: the page says the biology groups hold no testable entry")
    w(C("C-TR-PATTERN", "The pattern across groups: **the archive held here tests physics and "
        "itself, and the groups on biology hold no testable entry.** Groups C, G, Z and I hold "
        f"{phys} of the {cls['testable']['n']} testable-now entries. Groups F, J, T and R — "
        "biological structure, films, sediment sickness, decay — hold none of them, and E, "
        f"chemistry, holds {gs['E']['testable']}; those five groups hold {hard} of the "
        f"{beyond} entries that are unscoreable or need an experiment."))
    w("")
    w("### An honest caveat about this table")
    w("")
    w(C("C-TR-CAVEAT", "The classification is mine and is itself an untested partition, exactly "
        f"as the {tc['n_groups']} groups are (PLAN.md says so of them). Two judgements are "
        "load-bearing and contestable: I treated *not fetched but fetchable* as **blocked on a "
        "fetch** rather than unscoreable even where nobody has confirmed the topic contains what "
        "its name suggests; and I treated *measured somewhere in the world but not in Denmark* "
        "as unscoreable **for this archive**, which is a statement about Denmark's monitoring "
        f"rather than about nature. The {cls['unestablished']['n']} entries I could not place "
        "at all are marked *not established* rather than guessed."))
    w("")
    w(C("C-TR-SEARCH", "And per [KNOWN_AND_UNKNOWN.md](../KNOWN_AND_UNKNOWN.md): **every \"not "
        "measured\" in this table should be read as \"not found by a search whose sensitivity "
        "nobody has characterised.\"** Things this project had called absent have turned up "
        "before. The unscoreable column is an upper bound on what is missing, not a measurement "
        "of it."))
    try:
        write_doc(OUT, "\n".join(o).rstrip("\n") + "\n")
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except live.Unjustified as e:
        log(str(e))
        sys.exit(1)
