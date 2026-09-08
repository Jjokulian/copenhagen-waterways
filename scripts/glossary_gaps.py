#!/usr/bin/env python3
"""Find the words a reader will not know and the glossary does not yet cover.

The glossary in scripts/hypotheses.py was assembled by hand, which is why its
coverage was patchy: it caught the jargon somebody noticed and missed the
ordinary-looking nouns that carry a whole world of assumed knowledge. "Diatom" is
the diagnosis - a perfectly regular word that tells a reader nothing at all unless
they already know it is a single-celled alga building a glass box out of silica.

So this looks for candidates systematically instead. Three signals, and a word only
has to trip one:

  not-English   absent from the system's British-English dictionary, which is a
                blunt but honest proxy for "somebody had to learn this word"
  morpheme      built from a classical root that is opaque in English - -troph,
                -phyte, -benthos, -lysis, oo-, meio-, eu-, an-, and the rest
  eponym        a capitalised surname bound to a law, effect, ratio, cycle or
                number. These are the worst offenders, because the name carries
                *none* of the meaning: "Liebig's floor" is unparseable unless you
                already know it

Then it subtracts what the glossary covers and what a stoplist marks as ordinary,
and prints what is left, ranked by how often it appears. The output is a worklist
for a human, not a glossary - defining a term is a judgement about what a reader
needs, and that is not automatable.

Usage:  python3 scripts/glossary_gaps.py [--min-count 1] [--limit 120]
"""
import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, read_json

GLOSSARY = os.path.join(ROOT, "docs", "data", "glossary.json")
DICTS = ["/usr/share/hunspell/en_GB.dic", "/usr/share/hunspell/en_US.dic",
         "/usr/share/dict/words"]

# Classical roots that stay opaque in English. A word containing one of these is a
# word somebody had to be taught, however ordinary it looks on the page.
MORPHEMES = (
    r"troph|phyt|benth|plankt|pelag|lysis|clast|phag|vor(e|ous)|zoa|zoo|cyte|cyto|"
    r"myce|mycel|fung|bacter|viri|phage|genic|philic|phobic|morph|stat(ic)?$|"
    r"metry|meter$|graphy|logy$|osis$|itis$|aemia|emia$|ase$|ose$|oid$|"
    r"oo(cyt|myc|gen)|meio|oligo|eu(troph|xin)|an(oxi|aerob)|hypox|euxin|"
    r"allelo|hetero(troph|cyst)|endo(symb|crin)|exopoly|epiphy|epibenth|"
    r"chloroph|sulphid|sulphat|phosphat|silicat|ferrous|ferric|redox|"
    r"halocline|thermocline|pycnocline|osmo(tic|lar)|anion|cation|ligand|chelat|"
    r"sorpt|floccul|coagul|humic|fulvic|labile|recalcitr|senesc|detrit|necro|sapro|"
    r"nitrif|denitrif|anammox|remineral|mineralis|immobilis|auxotro|symbio"
)
MORPH_RE = re.compile(MORPHEMES, re.I)

# A surname bound to a law, effect, ratio, constant or number.
EPONYM_RE = re.compile(
    r"\b([A-Z][a-z]{3,})(?:'s)?\s+"
    r"(law|effect|ratio|cycle|number|constant|principle|equation|rule|"
    r"hypothesis|paradox|index|coefficient|process|reaction|feedback|"
    r"disease|syndrome|scale|test|shunt)\b")

# Ordinary English that happens to trip a morpheme rule.
STOP = set("""
about above across after against along among analysis another answer anything
discharge discharges discharging discharged remove removes removed removing
close closes closed closing phase phases locations location geometry biology
classification chronology deposition modelled modelling localised localise
irradiance disease diseases assumed arrive arrived arriving concentrated
separately reducing reduces oxygenated scored poison poisoned faster
application area areas around because become becomes before behind being below
between beyond both bring build building called cannot carry carrying change
changes changing collect collection common company complete computed concentration
condition conditions consider content context continue country current data
database decision decline described design detail different direct discussion
district doing during each early effect either element elements enough entire
error errors every example expect experiment explain explained factor field figure
final first follow following further general given group groups history however
important include including increase increased information instead interest
introduce issue itself known large larger largest later least length level levels
likely limit limited little local locate location long longer lower macro
maintain major making manage material matter measure measured measurement
measurements method micro middle might model models modern month months more most
much must nature nearly necessary need needed never nothing notice number numbers
object observation observations often only order other others outside over own
part particular pattern people perhaps period person place places point points
possible present pressure probably problem process processes produce product
program project provide public question range rather reach reason record records
reduce reduced reduction relate related relation release remain remains report
require required research resource response result results return review right
same sample samples scale science second section separate series service several
should side significant similar simple since single situation size small smaller
society some something sometimes source sources space special specific spent stage
standard start state states station stations still stop story structure study
subject substance such support surface system systems table taken temperature term
terms test tests than that their them then there these they thing things think
this those though three through time times together total toward under understand
until upon usual value values various very view volume water well were what when
where whether which while whole whose within without word work working world would
write year years
""".split())


def load_dictionary():
    words = set()
    for p in DICTS:
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                w = line.split("/", 1)[0].strip().lower()
                if w and w.isalpha():
                    words.add(w)
    return words


def base_forms(w):
    """Cheap morphology, so 'diatoms' does not count as a different word."""
    w = w.lower()
    out = {w}
    for suf, rep in (("ies", "y"), ("ied", "y"), ("iest", "y"), ("ier", "y"),
                     ("es", ""), ("s", ""), ("ing", ""), ("ing", "e"),
                     ("ed", ""), ("ed", "e"), ("er", ""), ("er", "e"),
                     ("est", ""), ("ly", ""), ("ally", "al"), ("ness", ""),
                     ("al", ""), ("ic", ""), ("ation", "ate"), ("ations", "ate"),
                     ("ors", "or"), ("ers", "er"), ("ment", ""), ("ments", "")):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            out.add(w[: -len(suf)] + rep)
    # doubled final consonant: stressed -> stress
    if len(w) > 4 and w[-1] == w[-2]:
        out.add(w[:-1])
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-count", type=int, default=1)
    ap.add_argument("--limit", type=int, default=120)
    a = ap.parse_args(argv)

    g = read_json(GLOSSARY)
    covered = set()
    for k in list(g.get("_terms") or {}):
        covered |= base_forms(k)
        # a multi-word key covers its parts: "photosystem II" answers "photosystem",
        # and an adjective form is the same term: mycorrhizal -> mycorrhiza
        for part in re.split(r"[ \-]", k):
            if len(part) > 3:
                covered |= base_forms(part)
                covered.add(part.lower().rstrip("a") + "al")
                covered.add(part.lower() + "al")
                covered.add(part.lower() + "ic")
    docs = g.get("_docs") or []
    english = load_dictionary()
    log(f"  dictionary: {len(english):,} words; glossary covers {len(g['_terms'])} terms")

    text = {}
    for f in docs:
        p = os.path.join(ROOT, "docs", f)
        if os.path.exists(p):
            text[f] = open(p, encoding="utf-8").read()
    joined = "\n".join(text.values())
    # a word capitalised only because it starts a sentence is not a proper noun
    lowercase_somewhere = set(re.findall(r"(?<![.!?]\s)\b([a-z]{4,})\b", joined))

    # eponyms first - these are the worst offenders and are easy to spot
    epo = collections.Counter()
    for m in EPONYM_RE.finditer(joined):
        name = m.group(1)
        # a surname is a capitalised word that is not ordinary English. That rules
        # out "That number" and "Every number" while keeping Liebig and Shelford.
        if name.lower() in STOP or (base_forms(name) & english):
            continue
        if base_forms(name) & covered:
            continue
        epo[f"{name} {m.group(2)}"] += 1

    # then single words
    counts = collections.Counter()
    acronyms = collections.Counter()
    propernouns = collections.Counter()
    where = collections.defaultdict(set)
    for f, s in text.items():
        s = re.sub(r"`[^`]*`", " ", s)          # ids are handled separately
        s = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", s)
        s = re.sub(r"^#+ .*$", " ", s, flags=re.M)      # headings
        s = re.sub(r"^\*\*[A-Z][a-z]+[^*]*\.\*\*", " ", s, flags=re.M)
        s = re.sub(r"\*\*(Predicts|Discriminated by|Needs|Manipulate|Control|"
                   r"Measure|Decide, in advance|Outcomes|Bears on)\.?\*\*", " ", s)
        s = re.sub(r"^\|.*\|$", " ", s, flags=re.M)   # table rows: ids and names
        for w in re.findall(r"[A-Za-zÆØÅæøå][A-Za-zÆØÅæøå]{4,}", s):
            lw = w.lower()
            if lw in STOP or base_forms(w) & covered:
                continue
            not_english = not (base_forms(w) & english)
            morpheme = bool(MORPH_RE.search(lw))
            if not (not_english or morpheme):
                continue
            lw = w.lower()
            key = w if w[0].isupper() else lw
            if w.isupper() and len(w) > 2:
                acronyms[key] += 1
                continue
            if w[0].isupper() and lw in lowercase_somewhere:
                w, key_is_lower = lw, True          # sentence-initial, not a name
            if w[0].isupper() and not MORPH_RE.search(w.lower()):
                propernouns[key] += 1     # place and body names: a different job
                continue
            counts[key] += 1
            where[key].add(f)

    rows = [(c, w) for w, c in counts.items() if c >= a.min_count]
    rows.sort(key=lambda r: (-r[0], r[1]))

    print(f"\n=== EPONYMS not in the glossary ({len(epo)}) "
          f"— the worst kind, the name carries no meaning\n")
    for name, c in epo.most_common(30):
        print(f"  {c:3}  {name}")

    print(f"\n=== WORDS not in the glossary ({len(rows)} candidates, showing "
          f"{min(a.limit, len(rows))})\n")
    print(f"  {'n':>3}  {'word':28} why flagged        appears in")
    for c, w in rows[: a.limit]:
        lw = w.lower()
        why = []
        if not (base_forms(w) & english):
            why.append("not-English")
        if MORPH_RE.search(lw):
            why.append("morpheme")
        print(f"  {c:3}  {w:28} {'+'.join(why):18} "
              f"{','.join(sorted(x.replace('.md', '') for x in where[w]))[:44]}")
    if acronyms:
        print(f"\n=== ACRONYMS ({len(acronyms)}) — expand on first use or gloss\n")
        print("  " + ", ".join(w for w, _ in acronyms.most_common(30)))
    if propernouns:
        print(f"\n=== PROPER NOUNS ({len(propernouns)}) — mostly Danish places; "
              f"a gazetteer job, not a glossary one\n")
        print("  " + ", ".join(w for w, _ in propernouns.most_common(25)))
    print(f"\n  {len(rows)} candidates total. This is a worklist, not a glossary — "
          f"deciding\n  what a reader needs is a judgement and is not automatable.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
