"""A reference to a hypothesis goes stale the way a number does.

"K1" in a sentence means whatever the hypothesis register says K1 is today. If
the register renumbers, drops or rewrites it, a typed "K1" silently points at
something else - the same failure as a typed number. So references get the same
discipline:

  - a generator writes live.ref("K1"), or {ref:K1} in a claims register, which
    is checked against data/derived/hypotheses.json and rendered at build time
    as a link to where the hypothesis lives, carrying its CURRENT title;
  - live.ref("K1", title=True) / {ref:K1|title} prints the title as well;
  - write_doc() refuses a register ID typed bare in prose, and figures.py
    (the pre-commit hook) refuses a committed reference whose target or title no
    longer matches the register - so a stale reference can be neither built nor
    committed.

The register is written by scripts/hypotheses.py, which also writes
docs/HYPOTHESES.md; neither is edited without the owner's approval. A generator
that renders references lists data/derived/hypotheses.json among its build
inputs, so the build graph reruns it when the register changes.

Only IDs the register defines are references. "O2" is an observable there, and
plain O2 means only that; the molecule is a checked species, live.chem("O2"),
rendered O₂ (see chem.py). "B12" and "Q10" are not in the register and are left
alone. Group letters on their own ("group A") are not references.
"""
import json
import os
import re

from common import ROOT

REG = os.path.join(ROOT, "data", "derived", "hypotheses.json")
DOCS = os.path.join(ROOT, "docs")
FAMILIES = {"hypotheses": "hypothesis", "observables": "observable", "routes": "route",
            "terminal": "terminal outcome", "avenues": "avenue",
            "unquantifiable": "unquantifiable"}
ID = r"[A-Z][0-9]{1,2}[a-z]?"
OPEN, CLOSE = "\ue003", "\ue004"   # private-use: never in real text
MARK = re.compile(OPEN + f"({ID})" + r"(\|t)?(?:\|f=([a-z]+))?" + CLOSE)
# an ID right after "/" is a reference (O3/O7); one in a path (hypodrafts/K1.md) is not
TOKEN = re.compile(r"(?<![\w#.-])(" + ID + r")(?![\w-]|\.md)")
LINK = re.compile(r"\[(" + ID + r")(?: — ([^\]\n]*))?\]\(([^)\s]+)(?: \"([^\"]*)\")?\)")
_FENCE = re.compile(r"^```.*?^```", re.S | re.M)
_CODE = re.compile(r"`[^`\n]*`")
_LINKTARGET = re.compile(r"\]\([^)\n]*\)")
_URL = re.compile(r"https?://\S+")
_TAG = re.compile(r"<[^>\n]+>")
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_cache = {}


def entries():
    """{id: {family key: title}} - an ID two families share (T1-T5 are both terminal
    outcomes and group T hypotheses) keeps both, never the last one written."""
    if "e" not in _cache:
        e = {}
        if os.path.exists(REG):
            h = json.load(open(REG, encoding="utf-8"))
            for fam in FAMILIES:
                for x in h.get(fam, []):
                    i = x.get("id")
                    if isinstance(i, str) and re.fullmatch(ID, i):
                        e.setdefault(i, {})[fam] = (x.get("title") or x.get("name") or "").strip()
        _cache["e"] = e
    return _cache["e"]


def registry():
    """{id: {"family", "title", "families"}} - for an ID two families share, the
    first family (hypotheses) is listed, and "families" names every one."""
    if "r" not in _cache:
        _cache["r"] = {i: {"family": FAMILIES[next(iter(f))], "title": next(iter(f.values())),
                           "families": list(f)} for i, f in entries().items()}
    return _cache["r"]


def ambiguous(i):
    return len(entries().get(i, {})) > 1


def _family(i, family):
    fams = entries()[i]
    if family is None:
        if len(fams) > 1:
            import live
            raise live.Unjustified(
                f"reference {i}: {i} is both " + " and ".join(FAMILIES[f] for f in fams)
                + f" - say which: live.ref('{i}', family='{list(fams)[-1]}') or "
                f"{{ref:{i}|{list(fams)[-1]}}}")
        return next(iter(fams))
    key = {v: k for k, v in FAMILIES.items()}.get(family, family)
    if key not in fams:
        import live
        raise live.Unjustified(f"reference {i}: no {family} has this ID")
    return key


def target(i, fam="hypotheses"):
    """Where a reference points, relative to docs/: a hypothesis's own draft or
    open-problem page if it has one, else the register page."""
    if fam != "hypotheses":
        return "HYPOTHESES.md"
    for sub in ("hypodrafts", "openproblems"):
        if os.path.exists(os.path.join(DOCS, sub, i + ".md")):
            return f"{sub}/{i}.md"
    return "HYPOTHESES.md"


def mark(i, title=False, family=None):
    """A checked reference, as a marker write_doc() expands into a link. An ID two
    families share must say which it means (family="terminal", "hypotheses"...)."""
    import live
    if i not in registry():
        raise live.Unjustified(f"reference {i}: not in data/derived/hypotheses.json - "
                               "no such hypothesis, observable, route or outcome")
    fam = _family(i, family)
    if title and re.search(r"\d", entries()[i][fam]):
        raise live.Unjustified(f"reference {i}: its title carries a number, which would "
                               "print unjustified; use the plain form, which puts the "
                               "title on the link instead")
    return OPEN + i + ("|t" if title else "") + (f"|f={fam}" if ambiguous(i) else "") + CLOSE


def strip(text):
    """Markers -> the bare ID, for labels and plain-text uses."""
    return MARK.sub(lambda m: m.group(1), text)


def _link(i, title, pre, fam=None):
    fam = fam or next(iter(entries()[i]))
    t = entries()[i][fam].replace('"', "'")
    return f'[{i} — {t}]({pre}{target(i, fam)} "{t}")' if title else f'[{i}]({pre}{target(i, fam)} "{t}")'


def expand(rel, text):
    import live
    pre = live._prefix(rel)
    return MARK.sub(lambda m: _link(m.group(1), bool(m.group(2)), pre, m.group(3)), text)


def _blank(m):
    return re.sub(r"[^\n]", " ", m.group(0))


def bare(text):
    """Register IDs typed outside a checked reference: [(line, id, context)]."""
    reg = registry()
    t = text
    import chem
    for rx in (_COMMENT, _FENCE, _CODE, MARK, chem.MARK, chem.SPAN, _LINKTARGET, _URL, _TAG):
        t = rx.sub(_blank, t)
    lines = text.split("\n")
    out = []
    for m in TOKEN.finditer(t):
        if m.group(1) in reg:
            ln = t.count("\n", 0, m.start()) + 1
            out.append((ln, m.group(1), lines[ln - 1].strip()[:90]))
    return out


def check_links(rel, text):
    """For a committed document: (stale or misdirected references, bare ones).
    A reference link must point where its ID lives and carry the current title;
    a link without a title cannot be checked and counts as bare."""
    import live
    reg, pre = registry(), live._prefix(rel)
    hard, missing = [], []

    def rep(m):
        i, shown_title, tgt, attr = m.groups()
        if i not in reg:
            return m.group(0)
        if attr is None:
            return m.group(0)                  # left in place: bare() will count it
        # an ID two families share is right if it matches either family fully
        opts = [(pre + target(i, f), t.replace('"', "'")) for f, t in entries()[i].items()]
        hit = next(((w, c) for w, c in opts if w == tgt and c == attr), None)
        want, cur = hit or next(((w, c) for w, c in opts if w == tgt), opts[0])
        if tgt != want:
            hard.append(f"{rel}: reference {i} points at {tgt}, but {i} lives at {want}")
        elif attr != cur or (shown_title is not None and shown_title != cur):
            hard.append(f"{rel}: reference {i} carries the title '{attr}', but the "
                        f"register now says '{cur}' - regenerate the page")
        return " " * len(m.group(0))
    rest = LINK.sub(rep, text)
    rest = re.sub(r"\[(" + ID + r")\]\(", lambda m: m.group(1) + " (", rest)
    return hard, bare(rest)


def message(rel, stray):
    ex = "; ".join(f"{i} (line {ln}: {ctx[:50]})" for ln, i, ctx in stray[:4])
    return (f"{rel}: {len(stray)} reference(s) typed bare: {ex}. A reference goes stale "
            "like a number: write live.ref('ID') in the generator, or {ref:ID} in a "
            "claims register, so it is checked against the hypothesis register and "
            "carries its current title. The oxygen molecule is live.chem('O2'), never O2.")
