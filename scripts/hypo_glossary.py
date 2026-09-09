#!/usr/bin/env python3
"""Extract the hypothesis-field shorthand into a glossary the pages can tooltip.

The field is written in codes - A1, I3, O4, T2, "group C" - and a reader who has not
opened a 2,500-line source document cannot read a page that uses them. TRIAGE.md is
166 rows of nothing else.

Three things this has to get right, each found by getting it wrong:

  COLLISIONS ACROSS SCHEMES. REGISTER.md numbers outfalls U2 and U4; there are also
  hypotheses U2 and U4. GRUNDLAGET.md numbers its own findings F1-F4 beside
  hypotheses F1-F4. Those documents are excluded rather than mismarked.

  COLLISIONS WITHIN THE SOURCE. T1-T5 are BOTH terminal outcomes and hypotheses in
  group T. Both senses are emitted and the tooltip says the code is ambiguous. That
  is a defect in the shorthand, and hiding it by picking one would be worse.

  PLAN NUMBERS. `A1.14` and `K1.57` are plan references. A code must not match when
  followed by a dot and a digit.

Reads   docs/HYPOTHESES.md and every docs/**/*.md
Writes  docs/data/hypo_glossary.json
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, log, write_json

SRC = os.path.join(ROOT, "docs", "HYPOTHESES.md")
OUT = os.path.join(ROOT, "docs", "data", "hypo_glossary.json")
EXCLUDE = {"REGISTER.md", "GRUNDLAGET.md"}
KINDS = {"T": "terminal outcome", "V": "avenue", "O": "observable", "M": "route"}
CODE = re.compile(r"(?<![A-Za-z0-9])(group [A-Z]|[A-Z][0-9]{1,2})(?![A-Za-z0-9]|\.\d)")


def main():
    s = open(SRC, encoding="utf-8").read()
    senses = {}
    def add(key, **kw):
        senses.setdefault(key, []).append(kw)

    for m in re.finditer(r"^### ([A-Z]\d+) [—-] (.+)$", s, re.M):
        add(m.group(1), kind="hypothesis", label=m.group(2).strip())
    for m in re.finditer(r"^## ([A-Z])\. (.+)$", s, re.M):
        add("group " + m.group(1), kind="group", label=m.group(2).strip())
    for m in re.finditer(r"^\| *`([A-Z]\d+)` *\| *\*\*(.+?)\*\* *\|(.*?)\|", s, re.M):
        code, name = m.group(1), m.group(2).strip()
        note = re.sub(r"\*\*|`", "", m.group(3).strip())
        add(code, kind=KINDS.get(code[0], "code"), label=name,
            note=note[:140] + "…" if len(note) > 140 else note)

    terms = {}
    for k, v in senses.items():
        terms[k] = v[0] if len(v) == 1 else {
            "kind": "AMBIGUOUS", "label": " / ".join(x["label"] for x in v), "senses": v}
    amb = [k for k, v in senses.items() if len(v) > 1]

    docs = []
    for p in sorted(glob.glob(os.path.join(ROOT, "docs", "**", "*.md"), recursive=True)):
        rel = os.path.relpath(p, os.path.join(ROOT, "docs"))
        if rel in EXCLUDE:
            continue
        t = open(p, encoding="utf-8").read()
        if len({m.group(1) for m in CODE.finditer(t)} & set(terms)) >= 3:
            docs.append(rel)

    write_json(OUT, {
        "_what": "Shorthand used across these pages - hypothesis ids, group letters, and "
                 "the coded terminal outcomes, avenues, observables and routes.",
        "_ambiguous": "These codes carry two meanings in the source and both are given: "
                      + ", ".join(sorted(amb)) + ". A terminal outcome and a hypothesis in "
                      "group T share each of them. The collision is a defect in the "
                      "shorthand, not in this glossary.",
        "_excluded": "REGISTER.md numbers outfalls U2/U4 and GRUNDLAGET.md numbers findings "
                     "F1-F4, both colliding with hypotheses of the same name.",
        "_regex": CODE.pattern,
        "_docs": docs, "terms": terms})
    log(f"  {len(terms)} terms ({len(amb)} ambiguous) over {len(docs)} documents "
        f"-> docs/data/hypo_glossary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
