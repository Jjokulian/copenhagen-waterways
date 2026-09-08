#!/usr/bin/env python3
"""Generate docs/POLITICS.md - what was said in public, and what kind of claim each was.

Every other page on this site studies the sea, or studies how a claim about the sea was
assembled from measurements. This one studies a third object: the sentences themselves.
That is a legitimate object with its own evidentiary standard, and the standard is not
the same one. A public statement can be checked against the document it rests on. It
cannot be checked against the sea, and this page never tries.

Two disciplines govern every line of the output, and both are inherited from
docs/RESIDUAL.md:

  1. Naming is not blaming. Who said what, and when, is recorded exactly. Motive, bad
     faith and fault are not scientific operations and appear nowhere.

  2. A property of the reasoning is not a property of the sea. "The stated basis for
     this sentence is thinner than the sentence" is a fact about a document. "The sea is
     fine" is a fact about water. This page produces only the first kind, and says so
     wherever the second could be misread out of it.

And two that follow:

  3. Verbatim, dated and complete rather than curated. All 92 collected statements are
     printed in full, including the ones that make the least convenient reading in
     either direction. Nothing is excluded. The skew in the collection is reported as a
     finding rather than smoothed over.

  4. Danish stays Danish. Every quote is the source's own wording; the English beside it
     is a gloss supplied here and is never presented as a quotation of anyone.

Reads   data/manual/politics.json  (92 statements + 17 public positions, collected
                                    2026-09-08 by curl + text extraction of the cited
                                    pages; see its own _rule and _caveats keys)
Writes  data/derived/politics.json  (the tallies this page quotes)
        docs/POLITICS.md

Usage:  python3 scripts/politics.py
"""
import collections
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, MANUAL, ROOT, log, read_json, write_doc, write_json

SRC = os.path.join(MANUAL, "politics.json")
OUT = os.path.join(ROOT, "docs", "POLITICS.md")

MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

# Where a statement comes from, assigned by id prefix so the assignment is mechanical
# and auditable rather than a judgement made quote by quote. The camps are positions in
# the process - who was in the room - and carry no evaluation of anybody's argument.
CAMPS = [
    ("mgtp-",         "Government: ministries"),
    ("so-",           "Government: ministries"),
    ("bruus-",        "Government: ministers"),
    ("rabjerg-",      "Government: ministers"),
    ("lose-",         "Government: ministers"),
    ("valentin-",     "Parties inside the agreement"),
    ("blochmunster-", "Parties inside the agreement"),
    ("obo-",          "Parties inside the agreement"),
    ("vermund-",      "Parties inside the agreement"),
    ("bjerre-",       "Parties inside the agreement"),
    ("rv-",           "Parties inside the agreement"),
    ("s-2026",        "Parties inside the agreement"),
    ("v-2026",        "Parties inside the agreement"),
    ("sf-",           "Parties inside the agreement"),
    ("stojberg-",     "Parties outside the agreement"),
    ("messerschmidt-", "Parties outside the agreement"),
    ("rosenkilde-",   "Parties outside the agreement"),
    ("el-",           "Parties outside the agreement"),
    ("alt-",          "Parties outside the agreement"),
    ("dn-",           "Environmental organisations"),
    ("gp-",           "Environmental organisations"),
    ("dsf-",          "Environmental organisations"),
    ("hav-",          "Environmental organisations"),
    ("lf-",           "Agriculture and food organisations"),
    ("neergaard-",    "Agriculture and food organisations"),
    ("fdk-",          "Agriculture and food organisations"),
    ("tuborgh-",      "Agriculture and food organisations"),
    ("prehn-",        "Agriculture and food organisations"),
    ("geus-",         "Research institutions"),
    ("au-",           "Research institutions"),
    ("ritzau-",       "Media, agencies and other bodies"),
    ("dr-",           "Media, agencies and other bodies"),
    ("danva-",        "Media, agencies and other bodies"),
    ("eu-",           "Media, agencies and other bodies"),
]
CAMP_ORDER = ["Government: ministries", "Government: ministers",
              "Parties inside the agreement", "Parties outside the agreement",
              "Environmental organisations", "Agriculture and food organisations",
              "Research institutions", "Media, agencies and other bodies"]

# The three totals the "two thirds" fraction could be a fraction of, and the two
# reductions it could be a fraction with. Both sets are taken from the collected
# statements except 12,776, whose provenance is discussed on the page.
DENOMINATORS = [
    (12776, "named only in the collection's own caveat; no statement in the record quotes it"),
    (13780, "quoted by Greenpeace, 19 June 2025, as *et estimat*"),
    (14800, "quoted by Ritzau, 3 December 2025, as what *forskere vurderer*"),
]
NUMERATORS = [
    (10100, "nitrogen regulation **and** the agreed wastewater effort together (MGTP, 3 Dec 2025)"),
    (7900, "the nitrogen regulation alone (MGTP, 3 Dec 2025)"),
    (3500, "the previous regulation, for comparison (MGTP, 3 Dec 2025)"),
]

CLASS_CHECKABILITY = {
    "number_claim": (
        "The document the figure comes from, and the interval that document states.",
        "Checkable in principle. **No statement in the record attaches a numerical "
        "interval to any figure** - not one of the 92."),
    "causal_claim": (
        "A counterfactual: the same catchment, over the same years, without the policy.",
        "Not checkable now. Nobody is constructing the counterfactual, and the "
        "monitoring is not designed to yield one."),
    "state_claim": (
        "The monitoring programme.",
        "Two of the seven point at something a programme records. The rest are "
        "summaries or figures of speech, and are not the worse for it."),
    "certainty_claim": (
        "The technical documents, which are public.",
        "The most checkable class here, and the one where the disagreement is least "
        "about what the documents say and most about what weight they bear."),
    "necessity_claim": (
        "The directive, the case law, and the ministry's own reasoning.",
        "Partly checkable. One assertion in the record records its own gap in the "
        "same paragraph."),
}

FLAG_GLOSS = {
    "estimator_treated_as_estimand":
        "a modelled quantity stated as if it were measured",
    "uncertainty_acknowledged":
        "the speaker states a limit on what the models can support",
    "limitation_stated":
        "the speaker limits the policy claim, without addressing model uncertainty",
    "cited_as_settled_science":
        "invoked to close discussion of the technical basis",
    "eu_obligation_asserted":
        "asserts that EU law leaves no discretion",
    "hedged_in_source":
        "the technical document hedges where public statements do not",
    "contests_model_basis":
        "disputes that the model outputs can bear the regulatory weight placed on them",
    "unqualified_causal_chain":
        "nitrogen to oxygen depletion asserted with no other driver mentioned",
    "denominator_variant":
        "supplies one of the mutually inconsistent indsatsbehov totals",
}

# Short, factual labels for the dates that carry several statements. Every fact in them
# is stated in politics.json itself.
DAY_CONTEXT = {
    "2024-09-24": "the *second opinion* on the technical basis, chaired by Finansministeriet",
    "2025-06-19": "the set-aside point and the regulatory ceiling agreed",
    "2025-08-27": "the new retention map published by GEUS and Aarhus University",
    "2025-12-03": "the nitrogen agreement announced",
    "2025-12-05": "trade-press reaction to the agreement",
    "2026-01-30": "the European Commission opens an infringement procedure against Denmark",
    "2026-03": "written party answers to DM Bio's pre-election questionnaire",
    "2026-06-19": "the completed regulation model presented",
    "2026-06-23": "the *kvaelstofhammer* deferred to 2028",
    "2026-08-27": "the vegetable-growers dispute",
    "2026-08-31": "Landbrug & Fodevarer's stormode in Odense",
    "2026-09-01": "vegetables exempted for 2027",
    "2026-09-03": "third reading of L5; passed 119-34",
}


def camp_of(sid):
    best = ""
    camp = None
    for prefix, c in CAMPS:
        if sid.startswith(prefix) and len(prefix) > len(best):
            best, camp = prefix, c
    return camp


def fmt_date(d):
    if not d:
        return "undated"
    parts = d.split("-")
    if len(parts) == 3:
        return f"{int(parts[2])} {MONTHS[int(parts[1])]} {parts[0]}"
    if len(parts) == 2:
        return f"{MONTHS[int(parts[1])]} {parts[0]}"
    return d


def analyse(d):
    st = d["statements"]
    camps = collections.Counter()
    for s in st:
        c = camp_of(s["id"])
        if c is None:
            raise SystemExit(f"unassigned statement id: {s['id']} - extend CAMPS")
        s["_camp"] = c
        camps[c] += 1
    classes = collections.Counter(s["claim_class"] for s in st)
    flags = collections.Counter()
    for s in st:
        for f in s["flags"]:
            flags[f] += 1
    domains = collections.Counter(
        urllib.parse.urlparse(s["source_url"]).netloc for s in st)
    days = collections.Counter(s["date"] or "" for s in st)
    ratios = {f"{n}/{den}": 100.0 * n / den
              for n, _ in NUMERATORS for den, _ in DENOMINATORS}
    return {
        "n_statements": len(st),
        "n_speakers": len(set(s["speaker"] for s in st)),
        "n_sources": len(domains),
        "n_verbatim": sum(1 for s in st if s.get("verbatim")),
        "n_undated": sum(1 for s in st if not s["date"]),
        "camps": dict(camps),
        "classes": dict(classes),
        "flags": dict(flags),
        "domains": dict(domains),
        "days": dict(days),
        "two_thirds_ratios": ratios,
        "collected": d["_collected"],
    }


# --------------------------------------------------------------------------- render
def render(d, a):
    st = d["statements"]
    o = []
    w = o.append

    def pct(n, den):
        return f"{100.0 * n / den:.1f}%"

    # ------------------------------------------------------------------ the frame
    w("# What was actually said\n")
    w("Every other page here studies the sea, or studies how a public claim about the "
      "sea was assembled out of measurements. This page studies a third thing: **the "
      "sentences**. Not whether they were right - other pages do that, and this one "
      f"borrows none of their conclusions - but what precisely was asserted, by whom, "
      f"on what date, and what kind of claim each assertion is.\n")
    w(f"The material is {a['n_statements']} verbatim public statements about the Danish "
      "nitrogen agreement of 3 December 2025, the Green Tripartite it implements, and "
      "the law L5 (`gødskningsloven`) that the Folketing passed 119-34 on 3 September "
      f"2026. They come from {a['n_speakers']} distinct speakers across "
      f"{a['n_sources']} publishers, and were collected on {a['collected']} by "
      "fetching and extracting the cited pages. All of them are printed below in full.\n")

    w("## Two rules, and what they rule out\n")
    w("**Naming is not blaming.** Identifying who said what, and when, is the whole "
      "point of a record and is done here exactly. Assigning motive, bad faith or fault "
      "is not a scientific operation and is not attempted anywhere on this page. Where "
      "a sentence is observed to differ from the document behind it, that is an "
      "observation about two texts. It is not an accusation, and it does not become one "
      "by being repeated.\n")
    w("**A property of the reasoning is not a property of the sea.** This is the central "
      "idea of [RESIDUAL.md](#RESIDUAL.md) and the constraint that matters most here. "
      "*The stated basis for this claim is thinner than the claim* is a fact about a "
      "document. *The sea is fine* is a fact about water. The first never implies the "
      "second, in either political direction.\n")
    w("> **So, explicitly: nothing on this page is a claim about the condition of Danish "
      "coastal water.** Not one sentence below should be read as evidence that the "
      "marine environment is in better shape than anyone says, or in worse shape. A "
      "page about sentences cannot produce a finding about a fjord, and any reading "
      "that extracts one from here has crossed a line this page draws on purpose.\n")
    w("That cuts both ways and it is worth being blunt about the direction it cuts most "
      "often. The best-documented objections in this record - seven statements, six "
      "from agricultural and food organisations and one from the leader of the largest "
      "party that voted against - are objections to the **reasoning**: that model "
      "outputs cannot bear the regulatory weight put on them. Whether those objections "
      "are sound or not, they do not entail that the water is in acceptable condition, "
      "and, as it happens, **none of them claims that it is**. That is set out with the "
      "quotes in section 7.\n")

    # ------------------------------------------------------ completeness and balance
    w("## 1. The record is incomplete and it is skewed. Both, first, before anything else\n")
    w("A collection of public statements that is quoted only where convenient becomes "
      "the thing it audits. So the defects come first.\n")

    w("### 1.1 It is skewed toward the side that made the announcements\n")
    w("| Where the statement comes from | statements |")
    w("|---|---:|")
    for c in CAMP_ORDER:
        w(f"| {c} | {a['camps'].get(c, 0)} |")
    w(f"| **total** | **{a['n_statements']}** |")
    w("")
    gov = a["camps"].get("Government: ministries", 0) + a["camps"].get("Government: ministers", 0)
    inside = a["camps"].get("Parties inside the agreement", 0)
    outside = a["camps"].get("Parties outside the agreement", 0)
    industry = a["camps"].get("Agriculture and food organisations", 0)
    ngo = a["camps"].get("Environmental organisations", 0)
    w(f"The government and the parties inside the agreement account for **{gov + inside} "
      f"of {a['n_statements']}**. The parties that stood outside it or voted against L5 "
      f"account for **{outside}**, and the agricultural and food organisations for "
      f"**{industry}**. That is a ratio of roughly "
      f"{(gov + inside) / max(1, outside + industry):.1f} to 1.\n")
    w("Some of that is real and some of it is an artefact of the method. Ministries "
      "publish press releases and opposition parties often do not; the collection notes "
      "that almost no party published a standalone release on the 3 December 2025 "
      "agreement, so several party positions had to be taken from chamber reporting and "
      "from one pre-election questionnaire. And 119 of the 153 votes cast on L5 were in "
      "favour, so a record proportioned to the chamber would lean the same way. None of "
      "that makes the imbalance harmless: **a reader should assume the contesting case "
      "is under-represented here, and that the under-representation is worst for two "
      "of the three parties that voted against.** Dansk Folkeparti and Borgernes "
      "Parti voted "
      "against L5 and the record contains no substantive claim from either about the "
      "nitrogen figures. Moderaterne is a government party to the agreement and the "
      "record contains no separate statement from it at all.\n")
    w("The environmental organisations are counted separately for the same reason: they "
      f"contribute {ngo} statements and they are not a neutral party either. Every one "
      "of them argues the regulation should be at least as strict as it is, and one - "
      "Greenpeace - argues the target itself is too low by a wide margin. A record that "
      "reads as \"industry against everyone\" would be a false picture of a record in "
      "which the environmental case is also over-represented relative to the "
      "chamber.\n")
    w("One more asymmetry, in the opposite direction, which matters for reading section "
      "7: **the agricultural side is not one voice.** Økologisk Landsforening is "
      "counted among the agriculture and food organisations and contests the agreement "
      "from the other end - it wanted *maksimalt pres* on discharge and objected that "
      "conventional farms may buy organic farmers' unused quotas.\n")

    w("### 1.2 No floor transcript could be retrieved, so every chamber quote is at one remove\n")
    w("The collection records that `ft.dk` and `folketingstidende.dk` render the debate "
      "text through JavaScript and that the PDF path returns 403 behind Cloudflare. "
      "**Every quotation here from the floor of the Folketing is therefore a quotation "
      "of a press rendering** - TV 2, Ritzau, Maskinbladet, Effektivt Landbrug, "
      "Kristeligt Dagblad, Tidende - and not of the official record. Those renderings "
      "are ordinarily reliable and they are cited individually below, but the "
      "distinction is real: what is verified is that the publication printed those "
      "words, not that the official transcript contains them. Three of the quotes carry "
      "a spelling or typography oddity from the rendering, left as found and flagged.\n")
    w("Two related exclusions follow from the same problem, and both are stated in the "
      "entries themselves rather than silently applied:\n")
    w("- **Paraphrase is never printed as quotation.** DR writes that the minister "
      "*anerkender, at grundlaget for at beregne udvaskningen af kvælstof ved "
      "produktion af grøntsager er dårligere* than for grain; TV 2 writes that a "
      "Conservative MP *giver landbruget skylden*. Neither sentence is the speaker's, "
      "so neither is attributed to a speaker here. They are recorded as what the "
      "publication wrote.\n")
    w("- **Three entries were captured above a paywall.** The Altinget entries "
      "(`rabjerg-2026-09-03-b`, `rabjerg-2026-09-03-c`, `lose-2025-12-03`) are "
      "headline, standfirst and pull-quote text only; the surrounding sentences could "
      "not be read. They are printed, marked, and **no argument on this page rests on "
      "them**.\n")

    w("### 1.3 What is thin, undated, or unattributable\n")
    w(f"- **One entry has no date.** Danmarks Naturfredningsforening's campaign page "
      "carrying the 69 % figure was undated at capture, so it cannot be placed in any "
      "chronology, and it is not used in the dated sequence in section 4.\n")
    w("- **Two of the three competing totals have named sources; one does not.** The "
      "figures 13,780 t and 14,800 t are each quoted in a statement below. The third, "
      "12,776 t, appears only in the collection's own caveat and **no statement in this "
      "record quotes it**. It is carried through the arithmetic in section 5 with that "
      "provenance attached, and no further.\n")
    w("- **Both sides cite unnamed experts for a total.** Ritzau reports that "
      "*forskere vurderer* the need is 14,800 t; Greenpeace reports that *eksperter "
      "peger på* a real need above 20,000 t. Neither names a researcher or cites a "
      "report. From this record alone, the two are exactly equally uncheckable, and "
      "they point in opposite directions.\n")
    w("- **One date is approximate.** The FødevareDanmark release states only that it "
      "followed the first reading *i sidste uge*; first reading was 13 August 2026, so "
      "the entry is dated 20 August 2026 with that inference marked.\n")
    w("- **A working transcript exists and is not evidence.** "
      "`data/agents/politics.transcript.txt` is the collecting run's own working log. "
      "It is marked unverified and nothing in it is cited here, on this site's standing "
      "rule that an agent's report is not a primary document.\n")

    w("### 1.4 Nothing was excluded\n")
    w(f"All {a['n_statements']} collected statements are printed in section 10, "
      "including the entries that are least convenient in either direction. Nothing was "
      "dropped for being off-message, off-topic or embarrassing to any side. Every one "
      f"of the {a['n_verbatim']} is marked `verbatim` in the source data - the "
      "collection contains no paraphrase presented as a quotation - and where a quote "
      "elides text the elision is shown as `[...]` with the note saying what was "
      "skipped.\n")

    w("### 1.5 Where the sources are\n")
    w("| Publisher | statements |")
    w("|---|---:|")
    for dom, n in sorted(a["domains"].items(), key=lambda kv: (-kv[1], kv[0])):
        w(f"| `{dom}` | {n} |")
    w("")
    w("Fifteen come from the responsible ministry's own site and eighteen from the "
      "farming trade press (Effektivt Landbrug and Maskinbladet), which carry both the "
      "industry's statements and the minister's. That is not a balanced sample of "
      "Danish media; it is a sample of the outlets that published verbatim wording on "
      "these dates.\n")

    # ------------------------------------------------------------- claim classes
    w("## 2. Five kinds of claim, and which of them can be checked at all\n")
    w("The single most useful thing a record like this can do is refuse to treat all "
      "assertions as the same kind of object. A tonnage, a causal chain, a description "
      "of a seabed, a statement that the science is settled, and a statement that the "
      "law requires something are five different claims with five different truth "
      "conditions, and public argument routinely answers one with another.\n")
    w("The classification below is the collection's own, applied at capture time.\n")
    w("| Class | n | What it would have to be checked against | Status in this record |")
    w("|---|---:|---|---|")
    for cls in ["number_claim", "causal_claim", "certainty_claim", "necessity_claim",
                "state_claim"]:
        against, status = CLASS_CHECKABILITY[cls]
        w(f"| `{cls}` | {a['classes'].get(cls, 0)} | {against} | {status} |")
    w("")
    w("Three consequences worth stating plainly.\n")
    w("**No figure in this record carries an interval.** Fourteen statements assert a "
      "number. Hedging *words* are common and are used correctly - `skønnes`, `ca.`, "
      "`et estimat`, `op til`, `vurderer` - and one minister says outright that the "
      "policy does not reach the whole way. But across all 92 statements there is not a "
      "single `±`, not a single range, and not a single figure given with the spread "
      "the underlying document reports. The DCE/AU method report that produces the "
      "requirement does state one, and states in its own text that the accuracy of a "
      "target load cannot be established in the ordinary way because there is no "
      "documentation of the correct one. That interval survives inside the technical "
      "literature and does not appear in a single public sentence here, on any side.\n")
    w("**The largest class is the least checkable.** Twenty-eight statements assert that "
      "nitrogen causes an outcome, or that the policy will cause one. Deciding any of "
      "them needs a counterfactual - the same catchments, the same years, without the "
      "measure - and nothing in the Danish monitoring programme is designed to produce "
      "one. That is a limitation on *checking the sentence*, and again it is not a "
      "statement about what the sea will do.\n")
    w("**Value judgements are not defective claims.** `makværk`, `en falliterklæring`, "
      "`en stjernestund for folkestyret`, `noget nær perfekt`, `grundlæggende "
      "uanstændigt`, `et stort og vigtigt skridt` - none of these is checkable and none "
      "of them is pretending to be. They are collected in section 9 without comment. "
      "The failure mode is not that politicians make value claims; it is a value claim "
      "wearing a number's clothes, and that is what sections 4 to 6 are about.\n")

    # --------------------------------------------------------------------- flags
    w("## 3. The flags, and who they land on\n")
    w("| Flag | what it marks | n |")
    w("|---|---|---:|")
    for f, n in sorted(a["flags"].items(), key=lambda kv: (-kv[1], kv[0])):
        w(f"| `{f}` | {FLAG_GLOSS.get(f, '')} | {n} |")
    w("")
    est = [s for s in st if "estimator_treated_as_estimand" in s["flags"]]
    w(f"The flag this site cares about most is `estimator_treated_as_estimand`, and it "
      f"lands on {len(est)} statements. **They do not come from one side.** One is the "
      "responsible ministry's; the rest are two environmental organisations, the public "
      "broadcaster's own fact-checking desk, and the trade body for Danish water "
      "utilities:\n")
    for s in est:
        w(f"- `{s['id']}` - {s['speaker']}")
    w("")
    w("That distribution is the finding. Restating a modelled quantity as a measured one "
      "is not a partisan manoeuvre and not a habit of government communication. It is "
      "what happens to a number that travels, and it happens to everyone who carries "
      "it, including people whose interests point in opposite directions and including "
      "a desk whose entire job is checking claims.\n")
    contest = [s for s in st if "contests_model_basis" in s["flags"]]
    ack = [s for s in st if "uncertainty_acknowledged" in s["flags"]]
    w(f"The mirror-image flag, `contests_model_basis`, lands on {len(contest)} "
      "statements: six from agricultural and food organisations, and one from Inger "
      "Støjberg of Danmarksdemokraterne. "
      f"`uncertainty_acknowledged` lands on {len(ack)}, and three of those five are the "
      "institutions that built the models - GEUS and Aarhus University - with a fourth "
      "from a broadcaster's climate correspondent and a fifth from the minister, about "
      "one crop.\n")

    # ------------------------------------------------------------------ the ladder
    w("## 4. The ladder, with dates on it\n")
    w("[RESIDUAL.md](#RESIDUAL.md) describes a five-rung ladder by which a carefully "
      "qualified technical quantity becomes a claim about the world, each step small "
      "and individually defensible. This record contains the rungs as actual dated "
      "sentences, which is the reason it was collected.\n")
    w("The regulation rests on two different modelled quantities and the ladder has to "
      "keep them apart, because eliding them would be the same error one level up:\n")
    w("- **`målbelastning` / MAI** - how much nitrogen a water body can receive and "
      "still reach good status. A marine-model output. It sets *how much* reduction is "
      "needed nationally and per water body.\n")
    w("- **the retention map** - what fraction of nitrogen leaving a field is removed "
      "before it reaches the coast. A catchment-model output. It sets *which holdings* "
      "carry the pressure.\n")
    w("Both are model outputs. Neither is measured. They are different numbers and the "
      "rows below say which is which.\n")
    w("| | Sentence | Who, when | Quantity | What it is |")
    w("|---|---|---|---|---|")
    w("| **0** | *\"Kvælstofretentionen kan i praksis ikke måles direkte.\"* | GEUS and "
      "Aarhus University, 27 Aug 2025 | retention | The producing institutions state "
      "that the regulated quantity is not directly measurable |")
    w("| **0'** | *\"Da der ikke findes dokumentation for den 'rigtige' målbelastning, "
      "kan man ikke på traditionel vis bestemme, hvor sikkert modellerne estimerer "
      "målbelastningen.\"* | DCE/AU method report, 2015 | målbelastning | The other "
      "quantity's own authors, on why its accuracy cannot be established in the usual "
      "way. Not from this collection - it is from the method report, audited elsewhere "
      "in this repository |")
    w("| **1** | *\"Retentionskortet er et beslutningsstøtteværktøj – ikke en "
      "facitliste.\"* | Anker Lajer Højberg, GEUS, 27 Aug 2025 | retention | The model "
      "output, labelled by its project leader as decision support, three months before "
      "it became a basis for per-holding quotas |")
    w("| **2** | *\"...i takt med, at der kommer nye **målinger** af, hvor meget "
      "kvælstofudledning vandmiljøet kan klare\"* | Ministeriet for Grøn Trepart, "
      "3 Dec 2025 | målbelastning | *How much the water environment can tolerate* is "
      "the modelled target load. The sentence describes its updates with the ordinary "
      "Danish word for measurements |")
    w("| **3** | *\"...for meget kvælstof på landbrugets marker har ført til iltsvind "
      "og ødelagt levesteder for fisk, muslinger og planter\"* | Christian Rabjerg "
      "Madsen, 19 Jun 2026 | both | The causal chain stated with no other driver "
      "named - not stratification, weather, atmospheric deposition or transboundary "
      "load |")
    w("| **4** | L5 passed 119-34; per-catchment quotas from 2027 | Folketinget, "
      "3 Sep 2026 | both | A legal obligation on individual holdings, sized to the "
      "above |")
    w("")
    w("> **This is five sentences in date order. It is not a demonstrated chain of "
      "influence.** Nothing here shows that anyone at any rung read the rung below it, "
      "and no such claim is made. What the ordering shows is that the qualification was "
      "available in public, in Danish, from the institutions that produced the numbers, "
      "before the sentences that dropped it were written. Why it did not travel is not "
      "something this record can answer, and speculating would be exactly the move the "
      "page refuses.\n")
    w("Rung 2 is the load-bearing one, as it is in RESIDUAL. Notice that it is not an "
      "argument anybody made and lost - it is a **word choice**, in a subordinate "
      "clause, in a sentence about something else (how often quotas get adjusted). "
      "Nobody wrote *we hereby treat the model output as a measurement*. The move "
      "happens in the choice of `målinger`, and there is nothing in the sentence for a "
      "reader to disagree with.\n")
    w("And the exact same clause is, in its other half, a genuine limitation stated "
      "honestly: the quotas *are* adjusted as knowledge improves, which is more than "
      "many regulations promise. Both things are true of one sentence.\n")

    # ------------------------------------------------------------- the arithmetic
    w("## 5. One fraction, three possible denominators, two possible subjects\n")
    w("`Indsatsbehov` is the quantity the whole public argument is denominated in. It "
      "is not measured: it is a modelled target load subtracted from a modelled "
      "projection of what the load will be in 2027. The famous claim is that the "
      "agreement delivers **two thirds** of it. Three different totals circulate, and "
      "the fraction is stated with none of them attached.\n")
    w("| Total (`indsatsbehov`) | provenance in this record |")
    w("|---:|---|")
    for den, prov in DENOMINATORS:
        w(f"| {den:,} t | {prov} |")
    w("")
    w("So: is the two-thirds claim sensitive to which total is meant? The arithmetic is "
      "one line and it should be run rather than argued about.\n")
    w("| Reduction claimed | " + " | ".join(f"of {den:,} t" for den, _ in DENOMINATORS) + " |")
    w("|---|" + "---:|" * len(DENOMINATORS))
    for num, what in NUMERATORS:
        cells = " | ".join(pct(num, den) for den, _ in DENOMINATORS)
        w(f"| **{num:,} t** - {what} | {cells} |")
    w("")
    w("Two thirds is 66.7%. Read the table honestly and it says two things, and the "
      "first one favours the claim:\n")
    w(f"**The claim survives the ambiguity, for the package as a whole.** 10,100 t is "
      f"more than two thirds of every one of the three totals - "
      f"{pct(10100, 14800)} of the largest, {pct(10100, 12776)} of the smallest. "
      "Whichever total the ministry had in mind, *more than two thirds* is arithmetically "
      "true of the combined nitrogen-and-wastewater package. The missing denominator is "
      "a defect of the sentence, not a defect of its arithmetic, and it would be unfair "
      "to imply otherwise.\n")
    w(f"**It does not survive a change of subject.** The nitrogen regulation on its own "
      f"is 7,900 t, and that is {pct(7900, 12776)} of the smallest total and "
      f"{pct(7900, 14800)} of the largest. **On the ministry's own published figures, "
      "the nitrogen regulation alone does not reach two thirds of any of the three "
      "totals.** The 3 December 2025 release attaches the fraction correctly, to "
      "`kvælstofreguleringen og den aftalte spildevandsindsats` together. Six months "
      "later, the 19 June 2026 release from the successor ministry says *\"Den nye "
      "model ventes med ét hug at fjerne to tredjedele af de udledninger, vi skal have "
      "væk\"* - and *den nye model* is the regulation model, not the package.\n")
    w("That is the transformation this site exists to notice, and here it is in a "
      "form anyone can check with a calculator: **the same fraction, six months apart, "
      "attached to a different subject, with no figure changed.** Whether the second "
      "sentence is loose drafting or a different intended referent is not something the "
      "record settles, and this page does not guess.\n")
    w("One more figure that looks inconsistent and is not: Greenpeace stated in June "
      "2025 that the regulation reaches *op til 52 procent* of the way, against a total "
      "of 13,780 t. That is the June 2025 package, before December's, and 52% of 13,780 "
      "is about 7,200 t. It is a different measure of a different agreement at a "
      "different date, and it does not contradict the December figures. Scoring a point "
      "off it would be the same error as the one this section describes.\n")

    # --------------------------------------------------------------- the 69.6 %
    w("## 6. The 69.6 %, and the five places it is stated as a fact\n")
    w("The share attributed to agriculture is a **residual**: modelled natural "
      "background and reported point sources are subtracted from the load, and what "
      "remains is routed through the modelled retention map and called agriculture. "
      "[RESIDUAL.md](#RESIDUAL.md) is about why that class of number cannot be checked "
      "against anything, ever, in principle, and [NITROGEN.md](#NITROGEN.md) takes the "
      "apportionment apart line by line. This page's only job is to record how the "
      "figure is spoken.\n")
    w("Four of the five statements carrying the `estimator_treated_as_estimand` flag "
      "concern this share - the fifth is the ministry sentence in the ladder above, "
      "which is about a different modelled quantity. All four state the share with no "
      "qualification at all:\n")
    for s in est:
        if "69" not in s["quote_da"] and "91,7" not in s["quote_da"]:
            continue
        w(f"> *\"{s['quote_da']}\"*")
        w(f">")
        w(f"> — {s['speaker']}, {fmt_date(s['date'])}\n")
    w("The verbs are worth reading closely, because they are the whole content of the "
      "flag. `stammer fra` - comes from. `viser de seneste tal` - the latest figures "
      "show. `Ifølge data fra Miljøstyrelsen og Aarhus Universitet kommer 91,7 %` - "
      "according to data, 91.7% comes from. `det er videnskabeligt dokumenteret` - it "
      "is scientifically documented. Each is a verb of observation applied to a "
      "subtraction, and `mere præcist` in front of a residual quoted to one decimal "
      "place is the clearest single instance in the collection.\n")
    w("Two things must be said immediately after that, and they are not softening.\n")
    w("**First: none of this shows the figure is wrong.** A residual can be close to "
      "the truth. It cannot be *confirmed* to be, which is a different property, and "
      "the whole argument of RESIDUAL is about the difference. Nothing in this section "
      "licenses the sentence *agriculture's share is smaller than they say*, and "
      "anybody who reads it that way has committed the identical error in the opposite "
      "direction.\n")
    w("**Second: the qualification exists and is public.** DANVA's own sentence supplies "
      "the arithmetic that makes the residual visible - `naturlige baggrundskilder, som "
      "bidrager med 22,1 %` - in the same breath as the 69.6%. The 22.1% is itself a "
      "model output and it is the subtrahend that determines the 69.6%. A reader who "
      "knows what a residual is can see the whole construction in that one sentence. "
      "That is the qualification surviving in the text and not surviving in the "
      "reading.\n")

    # ---------------------------------------------------------- what is contested
    w("## 7. What the contesting statements actually contest\n")
    w("This section exists because it would be easy to write the previous three and "
      "leave the impression that one side of Danish politics is careless with model "
      "outputs and the other is not. The record does not support that, in either "
      "direction, and the reasons are worth setting out precisely.\n")
    w("**The seven statements flagged `contests_model_basis` are all about reasoning, "
      "and none of them asserts the sea is fine.** Here is what they say:\n")
    for s in contest:
        w(f"> *\"{s['quote_da']}\"*")
        w(f">")
        w(f"> — {s['speaker']}, {fmt_date(s['date'])} · `{s['id']}`\n")
    w("Read as a set, these make four distinct objections, and they are not the same "
      "objection: that a decision-support map is being used as an answer key for "
      "individual holdings; that the model's own reported explanatory power is low "
      "relative to the decisions taken on it; that physical measurement might later "
      "contradict a model on which a farm has already been closed; and that the "
      "reference condition the target is derived from is set thousands of years before "
      "Danish agriculture existed. Whether any of them is correct is a question about "
      "documents, and it is not answered here or anywhere else on this site by counting "
      "who said them.\n")
    w("What can be said from the record: **the leader of the largest opposing party "
      "states the environmental objective as common ground** - *\"Vi vil også have en "
      "grøn omstilling om landbruget, vi vil også have rent drikkevand, rene fjorde og "
      "havmiljø, men omstillingen skal være baseret på sund fornuft\"* - and no "
      "statement in this collection, from any speaker, asserts that Danish coastal "
      "water is in acceptable condition. Six of the seven `state_claim` entries "
      "describe the water as in poor condition - from a minister, an SF spokesperson, a "
      "think tank, and a joint count by two environmental organisations - and the "
      "seventh is a minister characterising his opponents rather than the sea. **Not "
      "one statement in the record disputes any of them.**\n")
    w("So the public disagreement recorded here is **not a disagreement about the state "
      "of the sea.** It is a disagreement about whether particular model outputs can "
      "carry particular legal consequences, and about how the cost should fall. That is "
      "a more tractable disagreement than the one the shouting implies, and noticing it "
      "is the most useful thing this collection does.\n")
    w("**The symmetry runs the other way too.** The objection that the framework is "
      "*insufficient* is made from the other end by Alternativet, which stated in the "
      "chamber that L5 will not meet the Water Framework Directive and voted for it "
      "anyway; by Enhedslisten, which is not in the tripartite, criticises its reliance "
      "on voluntary conversion, and also voted for it; and by Greenpeace, which puts "
      "the real requirement above 20,000 t against the government's estimate. One "
      "measure, contested from both directions, passed 119-34.\n")
    w("**And the hedge is dropped on both sides.** The technical document behind the "
      "policy writes `evt. iltsvind` - *possibly* oxygen depletion - inside its own "
      "definition of eutrophication. In the public sentences the *evt.* is gone: a "
      "minister says too much nitrogen *har ført til iltsvind*, and Greenpeace says "
      "decades of nitrogen pollution *har skabt voldsomt iltsvind og livløse danske "
      "fjorde*. Same dropped qualifier, opposite politics.\n")

    # ------------------------------------------------------------- law and necessity
    w("## 8. Necessity, the law, and the two things that are not the same case\n")
    w(f"Nineteen statements assert that the policy is required - by the directive, by "
      "law, or by circumstance. Two carry the flag `eu_obligation_asserted`, and read "
      "together they are a small lesson in reading a citation.\n")
    w("The Ministry of the Environment's assessment, in the *second opinion* of "
      "September 2024, is that Denmark cannot use Article 4(4) of the Water Framework "
      "Directive to postpone good status beyond 22 December 2027, so the necessary "
      "measures must be complete before then. **The same box adds:** *\"Det bemærkes, "
      "at EU-Domstolen ikke har taget direkte stilling til spørgsmålet.\"* An assertion "
      "that the law leaves no discretion, recording in its own text that the Court has "
      "not ruled on the point. That is not a contradiction and it is not a criticism of "
      "the ministry - it is a legal assessment doing exactly what a legal assessment "
      "should, which is to state its own limit. What is notable is that the limit "
      "travels no further than the box.\n")
    w("The second is a real infringement procedure. On 30 January 2026 the European "
      "Commission opened cases against Denmark, Italy and Luxembourg over the Water "
      "Framework Directive - `INFR(2025)2209` in Denmark's case. **That case concerns "
      "the review of water abstraction permits, not the nitrogen `indsatsbehov`.** Same "
      "directive, different obligation. It is recorded here precisely so that it is not "
      "available as evidence for something it is not evidence for, in either "
      "direction.\n")
    w("The most-invoked certainty claim is the *second opinion*'s own summary: that "
      "Danish experts and an international panel find the Danish approach to computing "
      "the `indsatsbehov` **robust**, and broadly endorse the choices and assumptions "
      "made. That sentence says what it says. It is a statement about the robustness of "
      "a *method*; it is not a statement about the numerical accuracy of any individual "
      "catchment's figure, and the regulation acts on catchments and on holdings. "
      "Distinguishing those two readings is a matter of reading the sentence, not of "
      "doubting the panel.\n")

    # -------------------------------------------------------------- value language
    w("## 9. The language that is not a claim about anything checkable\n")
    w("Collected without comment, because a record that quoted only the checkable "
      "sentences would be a curated record. All are verbatim; all are printed again in "
      "context in section 10.\n")
    vals = ["stojberg-2026-09-03-a", "stojberg-2026-09-03-e", "rabjerg-2026-09-03-d",
            "rabjerg-2026-09-03-c", "rabjerg-2026-09-03-b", "bruus-2025-12-03-d",
            "valentin-2026-09-01", "lf-sondergaard-2025-12-03-e", "tuborgh-2026-08-31",
            "obo-2026-09-03", "rv-2026-03-dmbio-a", "dn-gjerding-2025-12-03-a",
            "gp-fromberg-2025-06-19-b"]
    byid = {s["id"]: s for s in st}
    w("| Speaker | Danish | Gloss |")
    w("|---|---|---|")
    for vid in vals:
        s = byid[vid]
        q = s["quote_da"]
        if len(q) > 165:
            q = q[:162].rstrip() + "..."
        g = s["gloss_en"]
        if len(g) > 165:
            g = g[:162].rstrip() + "..."
        w(f"| {s['speaker'].split('(')[0].strip()}, {fmt_date(s['date'])} "
          f"| *{q}* | {g} |")
    w("")
    w("Nothing follows from this table. It is here because leaving it out would make "
      "the record look more technical than the argument was, and the argument was "
      "mostly this.\n")

    # ------------------------------------------------------------------ the record
    w("## 10. The record\n")
    w(f"All {a['n_statements']} statements, in date order. **Every `quote_da` is the "
      "source's own wording**, copied from the page or PDF cited. **Every gloss is a "
      "translation supplied here and is a quotation of nobody.** Elisions inside a "
      "quote are marked `[...]` and the note says what was skipped. Odd spelling and "
      "typography in a source is left as found and flagged.\n")
    order = sorted(st, key=lambda s: (s["date"] or "9999", s["id"]))
    last_day = None
    for s in order:
        day = s["date"] or ""
        if day != last_day:
            ctx = DAY_CONTEXT.get(day)
            head = fmt_date(s["date"])
            w(f"### {head}" + (f" - {ctx}" if ctx else ""))
            w("")
            last_day = day
        party = s.get("party")
        who = s["speaker"]
        bits = [b for b in [s.get("role"), party] if b]
        w(f"**{who}**" + (f" · {' · '.join(bits)}" if bits else ""))
        w("")
        w(f"> {s['quote_da']}")
        w("")
        w(f"*Gloss (supplied here, not a quotation):* {s['gloss_en']}")
        w("")
        meta = [f"`{s['claim_class']}`"]
        if s["flags"]:
            meta += [f"`{f}`" for f in s["flags"]]
        meta.append(f"[source]({s['source_url']})")
        meta.append(f"`{s['id']}`")
        w(" · ".join(meta) + "  ")
        if s.get("note"):
            w(f"*Note:* {s['note']}")
        w("")

    # ------------------------------------------------------------- party positions
    w("## 11. Where each party and organisation stood\n")
    w("From the collection's own summary of positions. `in_agreement` refers to the "
      "December 2025 nitrogen agreement or the 2024 Green Tripartite as stated; the L5 "
      "column is the third-reading vote of 3 September 2026, which passed 119-34.\n")
    w("| Party or body | In the agreement | Vote on L5 |")
    w("|---|---|---|")
    for p in d["public_positions"]:
        ia = p["in_agreement"]
        ia = "yes" if ia is True else ("no" if ia is False else str(ia))
        vote = p["voted_on_L5"] or "-"
        w(f"| {p['party']} | {ia} | {vote} |")
    w("")
    w("Three rows repay reading against each other. **Enhedslisten and Alternativet are "
      "not in the Green Tripartite, criticise it as insufficient, and both voted for "
      "L5.** **Five Venstre MPs voted against their own party's bill** - Søren Gade, "
      "Anni Matthiesen, Preben Bang Henriksen, Peter Juel-Jensen and Amanda Heitmann - "
      "while the party's own economy minister had called the regulation *meget, meget "
      "hård* in parts of the country. And **Landbrug & Fødevarer signed the June 2024 "
      "tripartite and opposes the December 2025 distribution model**, on the ground "
      "that it is harder than what that tripartite presupposed. None of those is a "
      "contradiction; each is a position with a shape, and flattening them into two "
      "sides would lose the shape.\n")
    for p in d["public_positions"]:
        w(f"**{p['party']}** — {p['position']}\n")

    # ------------------------------------------------------------------ conclusion
    w("## 12. What this page does and does not establish\n")
    w("**It does not establish anything whatsoever about the condition of Danish "
      "coastal water.** Not one finding here is a finding about a fjord. Every "
      "observation on this page is an observation about a text, a date, or a piece of "
      "arithmetic on published figures, and none of them travels to the sea. If a "
      "reader leaves this page believing the marine environment is in better condition "
      "than the government says, this page has been misread - and so has the record, in "
      "which nobody at all makes that claim.\n")
    w("**It does not establish that anyone acted in bad faith, and it makes no attempt "
      "to.** A word choice in a subordinate clause is not a deception; a fraction "
      "attached to a different subject six months later is not a lie; a residual quoted "
      "to one decimal place by a fact-checking desk is not corruption. These are the "
      "ordinary ways numbers behave when they travel, which is why they are worth "
      "cataloguing rather than prosecuting.\n")
    w("**It does not establish that the policy is right or wrong.** That would need the "
      "counterfactual nobody is building, and a judgement about cost that is not a "
      "scientific question at all.\n")
    w("What it does establish, and what is checkable by anyone with the same sources:\n")
    w("- The institutions that produced the retention map stated in public, in Danish, "
      "that the quantity cannot in practice be measured directly and that the map is a "
      "decision-support tool and not an answer key. Both statements are dated 27 August "
      "2025. The agreement that made the map a basis for per-holding quotas is dated 3 "
      "December 2025. The corresponding statement about the other regulating quantity, "
      "the target load, is in its authors' 2015 method report rather than in this "
      "collection.\n")
    w("- The responsible ministry's press release describes updates to a modelled target "
      "load as `nye målinger`.\n")
    w("- On that ministry's own published figures, *more than two thirds* holds for the "
      f"combined package against all three circulating totals ({pct(10100, 14800)} to "
      f"{pct(10100, 12776)}), and does not hold for the nitrogen regulation alone "
      f"against any of them ({pct(7900, 14800)} to {pct(7900, 12776)}). A later release "
      "attaches the fraction to the regulation model.\n")
    w("- Across all 92 statements, no figure is given with an interval, by anyone.\n")
    w("- Restating a modelled share as an observed one is done by the ministry, by two "
      "environmental organisations, by a broadcaster's fact-checking desk and by a "
      "utilities trade body. It is not a property of one side.\n")
    w("- No statement in the record asserts that the sea is in acceptable condition, "
      "and the objections that are made are objections to reasoning rather than to the "
      "diagnosis.\n")
    w("- The collection is skewed toward the government and the agreement parties by "
      f"about {(gov + inside) / max(1, outside + industry):.1f} to 1, contains no "
      "official floor transcript, and is empty of substantive numerical claims from two "
      "of the three parties that voted against.\n")
    w("The last of those is the one that most limits everything above it. **A record of "
      "public statements is an instrument, and this instrument is not evenly pointed.** "
      "Group `I` of [HYPOTHESES.md](#HYPOTHESES.md) applies to it exactly as it applies "
      "to a monitoring network: what you find depends on where you looked, and the "
      "cheapest way to improve this page is not more analysis of these 92 sentences but "
      "the Folketing transcript that could not be fetched.\n")

    return "\n".join(o) + "\n"


def main():
    d = read_json(SRC)
    a = analyse(d)
    write_json(os.path.join(DERIVED, "politics.json"), a)
    write_doc(OUT, render(d, a))
    log(f"wrote docs/POLITICS.md ({os.path.getsize(OUT):,} chars)")
    log(f"  {a['n_statements']} statements, {a['n_speakers']} speakers, "
        f"{a['n_sources']} publishers, {a['n_undated']} undated")
    log(f"  classes: {a['classes']}")
    log(f"  camps:   {a['camps']}")
    log(f"  10,100 t is {100*10100/14800:.1f}-{100*10100/12776:.1f}% of the three totals; "
        f"7,900 t is {100*7900/14800:.1f}-{100*7900/12776:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
