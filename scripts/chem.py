"""A chemical species is a checked entity, like a number and a reference.

"O2" typed in prose is ambiguous: the observable O2 in the hypothesis register,
or the oxygen molecule. So a species is never typed. A generator writes
live.chem("O2") - or {chem:O2} in a claims register - which is checked against
data/manual/species.json (and its fragments in species.d/) and rendered as

    <span class="chem" data-chem="O2" title="dissolved oxygen">O₂</span>

- unicode subscripts in the markdown source, the species key in the DOM, the name
on hover. Plain "O2" stays free to mean the observable, which is itself a checked
reference (see refs.py).

write_doc() refuses a formula typed bare - ASCII (O2, CO2, NO3) or hand-typed
subscripts (O₂) - and figures.py refuses a committed chem span that no longer
matches the register.
"""
import json
import os
import re

from common import MANUAL, fragments

REG = os.path.join(MANUAL, "species.json")
OPEN, CLOSE = "\ue005", "\ue006"   # private-use: never in real text
MARK = re.compile(OPEN + "([^" + CLOSE + "]+)" + CLOSE)
SPAN = re.compile(r'<span class="chem" data-chem="([^"]+)" title="([^"]*)">([^<]*)</span>')
# a whole hand-typed formula - NO₃⁻, PO₄³⁻, H₂S - not just its last element
_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻"                 # ¹²³ sit apart from ⁰⁴-⁹ in unicode
_SUB = re.compile("(?<![\\w₀-₉" + _SUP + "])(?=[A-Za-z₀-₉" + _SUP + "]*[₀-₉" + _SUP + "])"
                  # superscript digits count only as a charge, which carries a sign
                  # (Fe²⁺, PO₄³⁻); without one they are an exponent (R², m²)
                  "(?:[A-Z][a-z]?[₀-₉]*)+(?:[" + _SUP[:10] + "]*[⁺⁻])?"
                  # a sign followed by a digit is an exponent (L⁻¹, m⁻²), not a charge
                  "(?![₀-₉" + _SUP + "])")      # the whole suffix, or it is not a formula
_FENCE = re.compile(r"^```.*?^```", re.S | re.M)
_CODE = re.compile(r"`[^`\n]*`")
_LINKTARGET = re.compile(r"\]\([^)\n]*\)")
_URL = re.compile(r"https?://\S+")
_TAG = re.compile(r"<[^>\n]+>")
_MATH = re.compile(r"\$[^$\n]+\$")
_cache = {}


def species():
    """{key: {"unicode", "name"}}: the register and its fragments."""
    if "s" not in _cache:
        s = {}
        for f in fragments(REG):
            for k, v in json.load(open(f, encoding="utf-8")).get("species", {}).items():
                s[k] = v
        _cache["s"] = s
    return _cache["s"]


def _ascii():
    cores = sorted({re.sub(r"[+-].*$|\s.*$", "", k) for k in species()}, key=len, reverse=True)
    cores = [c for c in cores if re.search(r"\d", c)]   # "Si", "Fe" alone are words
    return re.compile(r"(?<![\w/#.$\\-])(" + "|".join(map(re.escape, cores)) + r")(?![\w])") \
        if cores else None


def mark(key):
    import live
    if key not in species():
        raise live.Unjustified(f"species {key}: not in data/manual/species.json - add it "
                               "there (key, unicode form, name) before using it")
    return OPEN + key + CLOSE


def strip(text):
    return MARK.sub(lambda m: species()[m.group(1)]["unicode"], text)


def _span(key):
    s = species()[key]
    return (f'<span class="chem" data-chem="{key}" title="{s["name"]}">'
            f'{s["unicode"]}</span>')


def expand(text):
    return MARK.sub(lambda m: _span(m.group(1)), text)


def _blank(m):
    return re.sub(r"[^\n]", " ", m.group(0))


def bare(text):
    """Formulas typed outside a checked species: [(line, formula, context)]."""
    import refs
    t = refs.LINK.sub(_blank, text)          # [O2](… "title") is the observable
    for rx in (_FENCE, _CODE, MARK, refs.MARK, SPAN, _LINKTARGET, _URL, _MATH, _TAG):
        t = rx.sub(_blank, t)
    lines, out = text.split("\n"), []
    rx = _ascii()
    hits = list(rx.finditer(t)) if rx else []
    hits += list(_SUB.finditer(t))
    for m in sorted(hits, key=lambda m: m.start()):
        ln = t.count("\n", 0, m.start()) + 1
        out.append((ln, m.group(0), lines[ln - 1].strip()[:90]))
    return out


def check_spans(rel, text):
    """For a committed document: (spans that no longer match the register, bare)."""
    sp, hard = species(), []

    def rep(m):
        key, name, shown = m.groups()
        if key not in sp:
            hard.append(f"{rel}: species {key} is no longer in data/manual/species.json")
        elif shown != sp[key]["unicode"] or name != sp[key]["name"]:
            hard.append(f"{rel}: species {key} is shown as '{shown}' ({name}); the "
                        f"register now says '{sp[key]['unicode']}' ({sp[key]['name']})")
        return " " * len(m.group(0))
    return hard, bare(SPAN.sub(rep, text))


def message(rel, stray):
    ex = "; ".join(f"{f} (line {ln}: {ctx[:50]})" for ln, f, ctx in stray[:4])
    return (f"{rel}: {len(stray)} chemical formula(s) typed bare: {ex}. Write "
            "live.chem('O2') in the generator, or {chem:O2} in a claims register: the "
            "species is checked and rendered as O₂ with its key in the DOM. A bare O2 "
            "is the observable - live.ref('O2') - never the molecule.")
