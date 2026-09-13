#!/usr/bin/env python3
"""Numbers that carry their own derivation, and the compiler that refuses the rest.

THE RULE, as the project owner put it: every number on this site has a chain of
justification, and the compiler complains at any number that does not. No
allowance, no baseline, no debt carried quietly.

A number reaches a document one of three ways, and only the first two compile:

  LIVE      loaded from a data file through live_json(). It is a real float or
            int - arithmetic, comparison, sorting and round() all work - that also
            remembers where it came from: the file, the field, and every operation
            done to it since. Formatting it in an f-string emits an invisible
            marker, and write_doc() turns the marker into a link to the number's
            entry in docs/SOURCES.md: the source field, the script that produced
            it, how that script counted it, and - for a number the generator
            calculated - the arithmetic, each operand linked to its own entry.
            Nothing is registered by hand. The derivation is recorded by the act
            of computing.

  CLAIMED   fig('name'), for a number that is the subject of an argued claim,
            linked to CLAIMS.md with its dependency graph and assessment.

  BARE      typed into prose, or computed from something that did not come
            through live_json() - int(x), str(x), a literal. write_doc() refuses
            to write the document and names each one with its line and sentence.

JUSTIFICATIONS THAT ARE NOT DATA. Some numbers in a justification do not come
from a data file, and each gets its own kind of entry, because each goes stale in
its own way - or never does:

  reading(...)  a number read out of an external document pinned by the sha256
                of its text. It can be RECOMPUTED from the pinned copy - a count
                of a term, a phrase that must still be present - so the reading
                checks itself, and a changed document is detected by its hash.
  quoted(...)   what an earlier version of this site said, pinned to a commit.
                True permanently, since the past does not change; verified
                against `git show` so a misquotation is refused.
  stated(...)   a parameter chosen rather than measured - a threshold, a limit -
                shown as a choice, with the reason for it.

WHAT IS A NUMBER. Every run of digits in the prose, except those that are
references rather than quantities: years and dates, times of day, legal citations
(BEK 931, § 14, stk. 3), coordinate systems (EPSG:25832), identifiers with digits
glued to letters (A7, CO2, ID15, Emne_10_11), section and list numbering, and
anything inside code, a link target or a URL. A reference identifies a source and
is not a claim about the world; a quantity is a claim and needs one. An identifier
the patterns do not recognise - a station number, a place name with a number in
it - is written as `code`, which marks it as a name. Where a pattern draws the
line in the wrong place, the fix is to the list below, visibly, not to a document.

WHY MARKERS AND NOT LINKS. A live number is formatted in log lines, file names and
derived JSON as well as in documents, and a markdown link would corrupt all of
those. The marker is three private-use characters: log() and write_json() strip
them, and only write_doc() expands them into links.

WHY SUMS ARE SUMMARISED. Adding nine thousand farms' equity would otherwise build
a nine-thousand-node tree. Past eight terms an n-ary sum becomes a summary by
field - "Σ cvr_financials.json › *.*.equity, 707 terms" - which is both small and
a better description of what was done.
"""
import hashlib
import json
import operator
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT

OPEN, MID, CLOSE = "", "", ""
MARK = re.compile(OPEN + r"(F-[0-9a-f]{10})" + MID + r"(.*?)" + CLOSE, re.S)
INDEX = os.path.join(ROOT, "docs", "data", "sources_index.json")
SOURCES_MD = os.path.join(ROOT, "docs", "SOURCES.md")
BUILD = os.path.join(ROOT, "data", "manual", "build.json")
# SOURCES.md states each number beside its own chain: it is the chain. CLAIMS.md
# is NOT exempt - its texts are live and compiled like any other page.
EXEMPT = {"docs/SOURCES.md"}
_MAXKIDS = 8
_seen = {}
# A claim on a page: a span of prose the site asserts, marked so that the build can
# check the claims register holds it - for this page, confirmed against this very
# wording, and current. Numbers, references and species inside it stay live.
C_OPEN, C_MID, C_CLOSE = "\ue007", "\ue008", "\ue009"
CLAIM = re.compile(C_OPEN + r"(C-[A-Z0-9-]+)" + C_MID + r"(.*?)" + C_CLOSE, re.S)
SPANS = os.path.join(ROOT, "data", "derived", "claim_spans.json")


def claim(cid, text):
    """A span of prose the page asserts, as a checked claim (see CLAIM above)."""
    return claim_begin(cid) + text + C_CLOSE


def claim_begin(cid):
    """Opens a claim that runs over several written lines; CLAIM_END closes it."""
    if not re.fullmatch(r"C-[A-Z0-9-]+", cid):
        raise Unjustified(f"claim {cid}: a claim id is C- then capitals, digits, hyphens")
    return C_OPEN + cid + C_MID


CLAIM_END = C_CLOSE


def strip_marks(text):
    """The plain text a marker stands for - for logs, JSON, anything but a doc."""
    return MARK.sub(lambda m: m.group(2), text) if OPEN in text else text


# ---------------------------------------------------------------- derivations ---
def _split(path):
    """Path segments. A key that itself contains a dot - the "1.4" threshold in
    manure.json - is written in brackets, so it is not split into two."""
    return [t[1:-1] if t.startswith("[") else t
            for t in re.findall(r"\[[^\]]*\]|[^.]+", path or "")]


def _general(path):
    return ".".join("*" if p.isdigit() else p for p in _split(path)) if path else path


def _shape(n):
    """What identifies a derivation: its structure, not its current values, so a
    link survives the data changing underneath it."""
    t = n[0]
    if t == "const":
        return n
    if t == "leaf":
        return n[:3]
    if t in ("op", "nary", "step"):
        return [t, n[1], [_shape(k) for k in n[2]]]
    if t == "agg":
        return ["agg", n[1], sorted(n[2]), [_shape(k) for k in n[3]]]
    if t == "quote":
        return n[:5]              # a located quotation is identified by its locator too
    if t == "reading":
        return n[:4]
    if t == "stated":
        return n[:2]
    return n


def _id(node):
    return "F-" + hashlib.sha1(json.dumps(_shape(node), sort_keys=True,
                                          default=str).encode()).hexdigest()[:10]


def _parts(x):
    if isinstance(x, _Live):
        return x.src, x._v()
    return ["const", x], x


def _nary(sym, a, b):
    kids, vals, pat, others, extra = [], [], {}, [], 0
    for x in (a, b):
        s, v = _parts(x)
        if s[0] == "nary" and s[1] == sym:
            kids.extend(s[2])
            vals.extend(s[3])
        elif s[0] == "agg" and s[1] == sym:
            for k, n in s[2].items():
                pat[k] = pat.get(k, 0) + n
            others.extend(s[3])
            extra += s[4]
        elif s[0] == "const" and ((sym == "+" and s[1] == 0) or (sym == "*" and s[1] == 1)):
            continue
        else:
            kids.append(s)
            vals.append(v)
    if not pat and not others and not extra and len(kids) <= _MAXKIDS:
        return ["nary", sym, kids, vals]
    for s in kids:
        if s[0] == "leaf":
            key = s[1] + " › " + _general(s[2])
            pat[key] = pat.get(key, 0) + 1
        else:
            others.append(s)
    if len(others) > _MAXKIDS:
        extra += len(others) - _MAXKIDS
        others = others[:_MAXKIDS]
    return ["agg", sym, pat, others, extra]


def _mk(value, src):
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, int):
        o = LiveInt(value)
    elif isinstance(value, float):
        o = LiveFloat(value)
    else:
        return value
    o.src = src
    return o


def _remember(node, value):
    i = _id(node)
    _seen[i] = {"src": node, "value": value}
    if node[0] in ("op", "nary", "step"):
        for k, v in zip(node[2], node[3]):
            if k[0] != "const":
                _remember(k, v)
    elif node[0] == "agg":
        for k in node[3]:
            if k[0] != "const":
                _remember(k, None)
    return i


def _where():
    """The file and line where a number entered a document: the first frame on
    the stack that is not this module. That is the 'code that generated it'."""
    f = sys._getframe(1)
    engine = {os.path.join(os.path.dirname(os.path.abspath(__file__)), m) for m in
              ("live.py", "claims.py", "refs.py", "chem.py", "common.py")}
    while f is not None and os.path.abspath(f.f_code.co_filename) in engine:
        f = f.f_back
    return [_rel(f.f_code.co_filename), f.f_lineno] if f is not None else None


def set_where(marked, file, line):
    """Point a marked number at the text it was written from rather than the code
    that resolved it - claims.py uses this to name the line of claims.json."""
    m = MARK.search(marked)
    if m and m.group(1) in _seen:
        _seen[m.group(1)]["where"] = [file, line]


def _mark(node, value, shown):
    i = _id(node)
    _seen[i] = {"src": node, "value": value, "where": _where()}
    return OPEN + i + MID + shown + CLOSE


def reading(source_id, kind, arg, value, shown, meta):
    """A number read from a pinned external document. kind is 'count' (occurrences
    of arg in the pinned text) or 'phrase' (arg must be present in it)."""
    return _mark(["reading", source_id, kind, arg, meta], value, shown)


# A quotation is a REFERENCE into this site's history, not a copy: the generator
# names a commit, a file and a short phrase from that text with @@ where the value
# stands, and the value is read out of git when the page is built. Nothing is typed.
SLOT = "@@"
# Until every quotation in the repo is located, a typed one (quote("…", "80%"))
# still builds; once they are all converted this is True and a typed one is refused.
STRICT_QUOTES = True
_GIT = {}


def _git_text(commit, file):
    if (commit, file) not in _GIT:
        import subprocess
        r = subprocess.run(["git", "show", f"{commit}:{file}"], cwd=ROOT,
                           capture_output=True)
        _GIT[(commit, file)] = r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None
    return _GIT[(commit, file)]


def _locate_all(text, locator):
    """Every place `locator` matches `text`, whitespace-insensitively:
    [(value, start, end)] with the span of the value at the slot."""
    if locator.count(SLOT) != 1:
        raise Unjustified(f"locator '{locator}' must hold exactly one {SLOT}")
    before, after = locator.split(SLOT)
    words = lambda t: r"\s+".join(re.escape(w) for w in t.split())
    # cheap rejection first: both literal sides must occur somewhere at all
    for side in (before, after):
        if side.strip() and not re.search(words(side), text):
            return []
    # nothing before the slot: the value is the token the rest follows, not the line
    rx = words(before) + (r"\s+" if before[-1:].isspace() else "") if before.strip() \
        else r"(?<![^\s\"'“‘(\[*])"
    # a value never runs across a line break, which also keeps the search fast
    # after a phrase the value runs up to the next literal; with nothing before the
    # slot it is exactly one token, or the match could begin anywhere on the line
    rx += (r"([^\n]+?)" if before.strip() else r"(\S+?)") if after.strip() \
        else r"(\S+?)(?=[\s.,;:)\]]|$)"
    rx += (r"\s+" if after[:1].isspace() else "") + words(after)
    out = []
    for m in re.finditer(rx, text):
        v = m.group(1)
        strip = " *_\"'“”‘’([)]"                # emphasis and quote marks around a value
        lead = len(v) - len(v.lstrip(strip))
        core = v.strip(strip)
        out.append((core, m.start(1) + lead, m.start(1) + lead + len(core)))
    return out


def was(commit, file, locator):
    """What this site said at a past commit, as a located reference: the value at
    the @@ of `locator`, read out of `file` at `commit` when the page is built.
    Refused unless the locator finds exactly one place. scripts/quote_locate.py
    suggests a locator for a value."""
    text = _git_text(commit, file)
    if text is None:
        raise Unjustified(f"was: {file} does not exist at {commit}")
    hits = _locate_all(text, locator)
    if len(hits) != 1:
        raise Unjustified(f"was: '{locator}' locates {len(hits)} places in {file} at "
                          f"{commit} - it must locate exactly one; lengthen it "
                          "(scripts/quote_locate.py suggests one)")
    shown = hits[0][0]
    return _mark(["quote", commit, file, shown, locator], shown, shown)


def excerpt(commit, file, begin, end):
    """The words this site once published, from `begin` through `end`, read out of
    git - for the archive of retired claims, the one place where what the site said
    is exactly what is claimed. Old links are kept as their words; every quantity
    in the passage is a quotation, so nothing in it is typed."""
    text = _git_text(commit, file)
    if text is None:
        raise Unjustified(f"{file} does not exist at {commit}")
    flex = lambda p: r"\s+".join(re.escape(w) for w in p.split())
    at = [m.start() for m in re.finditer(flex(begin), text)]
    if len(at) != 1:
        raise Unjustified(f"'{begin}' occurs {len(at)} times in {file} at {commit} - "
                          "a retired passage must begin at one place")
    m = re.compile(flex(end)).search(text, at[0])
    if not m:
        raise Unjustified(f"'{end}' does not follow '{begin}' in {file} at {commit}")
    seg = re.sub(r"\[([^\]\n]*)\]\([^)\n]*\)", r"\1", text[at[0]:m.end()])
    if file.endswith((".html", ".js")):
        # a page built by script: its words sit in string literals joined with +,
        # with escapes and entities - read them as the reader saw them
        import html
        seg = re.sub(r"(['\"])\s*\+\s*\1", "", seg)
        seg = re.sub(r"\\u([0-9a-fA-F]{4})", lambda u: chr(int(u.group(1), 16)), seg)
        seg = html.unescape(seg)
    seg = re.sub(r"</?[A-Za-z][A-Za-z0-9:-]*(?:\s[^<>]*)?/?>", "", seg)     # tags are not words
    # a register ID in an old passage is part of what was said, not a live reference:
    # shown as a name, outside any code span the passage already has
    import refs
    seg = "".join(part if part.startswith("`") else
                  refs.TOKEN.sub(lambda t: "`" + t.group(1) + "`", part)
                  for part in re.split(r"(`[^`]*`)", seg))
    # so is a chemical formula: shown as written, not as a checked species (an old
    # passage may name one the species register does not hold)
    import chem

    def _formulas_as_names(part):
        rx = chem._ascii()
        hits = sorted(m.span() for m in (list(rx.finditer(part)) if rx else [])
                      + list(chem._SUB.finditer(part)))
        out, last = [], 0
        for a, b in hits:
            if a >= last and b > a:
                out += [part[last:a], "`" + part[a:b] + "`"]
                last = b
        return "".join(out) + part[last:]
    seg = "".join(part if part.startswith("`") else _formulas_as_names(part)
                  for part in re.split(r"(`[^`]*`)", seg))
    # bold is formatting, not wording, and a passage cut from inside it leaves a
    # stray marker at its edge
    seg = re.sub(r"\s+", " ", seg.replace("**", "")).strip()
    for _, a, _, tok in reversed(_quantity_spans(seg)):
        seg = (seg[:a] + _mark(["quote", commit, file, tok, f"{begin} … {end}"], tok, tok)
               + seg[a + len(tok):])
    return seg


def quoted(commit, file, shown):
    """What this site said at a past commit, given as a typed value. Superseded by
    was(): refused once STRICT_QUOTES is on."""
    if STRICT_QUOTES:
        raise Unjustified(f"quote of '{shown}' from {file} at {commit} is typed; a "
                          "quotation is a located reference now - write "
                          f"live.was(commit, file, 'phrase with {SLOT} where the value "
                          "stands'); scripts/quote_locate.py suggests the phrase")
    return _mark(["quote", commit, file, shown], shown, shown)


def quote(commit, file, shown):
    """quoted(), verified against git. Superseded by was()."""
    text = _git_text(commit, file)
    if text is None or shown not in text:
        raise Unjustified(f"quote: {file} at {commit} does not contain '{shown}' "
                          "- a misquotation")
    return quoted(commit, file, shown)


def stated(name, value, shown, reason):
    """A value chosen rather than measured, shown as a choice with its reason."""
    return _mark(["stated", name, reason], value, shown)


def stated_value(name, value, reason):
    """stated(), as a live number that can take part in arithmetic: 12 pairs times
    two windows is a calculation on two stated values, and should read as one."""
    return _mk(value, ["stated", name, reason])


def reading_value(source_id, kind, arg, value, meta):
    """reading(), as a live number: a value read out of a pinned document that
    can take part in arithmetic. The caller has checked the reading against the
    pin (claims.resolve does, for {read:} and {count:})."""
    return _mk(value, ["reading", source_id, kind, arg, meta])


def ref(i, title=False, family=None):
    """A reference to a hypothesis, observable, route or outcome, checked against
    the register and rendered with its current title. An ID two families share
    (T1-T5) must name its family. See scripts/refs.py."""
    import refs
    return refs.mark(i, title, family)


def chem(key):
    """A chemical species, checked against data/manual/species.json and rendered
    with its unicode formula and its key in the DOM. See scripts/chem.py."""
    import chem as _chem
    return _chem.mark(key)


def step(cid, x):
    """Mark a calculation as an application of a declared construction - reading a
    bound off between two runs, a share of a subset - so its model is declared,
    shown and checked with it instead of passing as plain arithmetic.
    data/manual/number_constructions.json must declare `cid` as a step."""
    if not isinstance(x, _Live):
        raise Unjustified(f"step {cid}: applied to a number with no chain")
    return _mk(x._v(), ["step", cid, [x.src], [x._v()]])


class _Live:
    def _v(self):
        return float(self) if isinstance(self, float) else int(self)

    def __format__(self, spec):
        v = self._v()
        shown = type(v).__format__(v, spec)
        i = _remember(self.src, v)
        _seen[i].setdefault("where", _where())
        return OPEN + i + MID + shown + CLOSE

    def __round__(self, n=None):
        v = self._v()
        r = round(v) if n is None else round(v, n)
        return _mk(r, ["op", "round", [self.src, ["const", n]], [v, n]])

    def __neg__(self):
        return _mk(-self._v(), ["op", "neg", [self.src], [self._v()]])

    def __abs__(self):
        return _mk(abs(self._v()), ["op", "abs", [self.src], [self._v()]])


def _bin(sym, fn, nary):
    def f(self, o):
        ov = o._v() if isinstance(o, _Live) else o
        if not isinstance(ov, (int, float)):
            return NotImplemented
        r = fn(self._v(), ov)
        return _mk(r, _nary(sym, self, o) if nary
                   else ["op", sym, [self.src, _parts(o)[0]], [self._v(), ov]])

    def rf(self, o):
        ov = o._v() if isinstance(o, _Live) else o
        if not isinstance(ov, (int, float)):
            return NotImplemented
        r = fn(ov, self._v())
        return _mk(r, _nary(sym, o, self) if nary
                   else ["op", sym, [_parts(o)[0], self.src], [ov, self._v()]])
    return f, rf


for _name, _sym, _fn, _n in (("add", "+", operator.add, True),
                             ("sub", "-", operator.sub, False),
                             ("mul", "*", operator.mul, True),
                             ("truediv", "/", operator.truediv, False),
                             ("floordiv", "//", operator.floordiv, False),
                             ("mod", "%", operator.mod, False),
                             ("pow", "**", operator.pow, False)):
    _f, _rf = _bin(_sym, _fn, _n)
    setattr(_Live, f"__{_name}__", _f)
    setattr(_Live, f"__r{_name}__", _rf)


class LiveFloat(_Live, float):
    pass


class LiveInt(_Live, int):
    pass


# ------------------------------------------------------------------ loading ---
def _join(path, k):
    k = str(k)
    if "." in k:
        k = f"[{k}]"
    return f"{path}.{k}" if path else k


def _wrap(v, file, path):
    if isinstance(v, (bool, str)) or v is None or isinstance(v, _Live):
        return v
    if isinstance(v, (int, float)):
        return _mk(v, ["leaf", file, path])
    if isinstance(v, dict) and not isinstance(v, LiveDict):
        return LiveDict(v, file, path)
    if isinstance(v, list) and not isinstance(v, LiveList):
        return LiveList(v, file, path)
    return v


class LiveDict(dict):
    """A dict whose numbers remember their field. Containers are wrapped on first
    access and stored back, so a mutation made through the wrapper persists and a
    large file is never wrapped all at once; numbers are wrapped fresh on every
    access and never stored, so nothing is multiplied in memory."""

    def __init__(self, data, file, path):
        dict.__init__(self, data)
        self._f, self._p = file, path

    def __getitem__(self, k):
        v = dict.__getitem__(self, k)
        w = _wrap(v, self._f, _join(self._p, k))
        if w is not v and isinstance(w, (LiveDict, LiveList)):
            dict.__setitem__(self, k, w)
        return w

    def get(self, k, d=None):
        return self[k] if k in self else d

    def items(self):
        return [(k, self[k]) for k in dict.keys(self)]

    def values(self):
        return [self[k] for k in dict.keys(self)]


class LiveList(list):
    def __init__(self, data, file, path):
        list.__init__(self, data)
        self._f, self._p = file, path

    def __getitem__(self, i):
        if isinstance(i, slice):
            return [self[j] for j in range(len(self))[i]]
        if i < 0:
            i += len(self)
        v = list.__getitem__(self, i)
        w = _wrap(v, self._f, _join(self._p, i))
        if w is not v and isinstance(w, (LiveDict, LiveList)):
            list.__setitem__(self, i, w)
        return w

    def __iter__(self):
        for j in range(len(self)):
            yield self[j]


def _rel(path):
    try:
        return os.path.relpath(path, ROOT)
    except ValueError:
        return path


def live_json(path):
    """Load a JSON file so that every number in it carries its file and field."""
    with open(path, encoding="utf-8") as f:
        return _wrap(json.load(f), _rel(path), "")


def live(value, file, path):
    """One value from a non-JSON source - a CSV cell, a counted row - with its origin."""
    return _mk(value, ["leaf", _rel(file) if os.path.isabs(file) else file, str(path)])


# ---------------------------------------------------------- what a number is ---
_UNIT_AHEAD = (r"(?!\s*(?:km|m\b|%|kg|kt|mg|µg|ha\b|DE\b|rows|stations|samples|"
               r"businesses|holdings|sites|MB|GB))")
EXEMPT_PATTERNS = [
    # a year-month ("2026-03") and a quarter code ("2026K3", "2026Q1")
    re.compile(r"\b(?:18|19|20)\d{2}-(?:0[1-9]|1[0-2])\b(?!-\d)|\b(?:18|19|20)\d{2}[KQ][1-4]\b"),
    re.compile(r"\b(?:18|19|20)\d{2}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?)?"),
    re.compile(r"\b(?:18|19|20)\d{6}\b"),
    re.compile(r"\b\d{1,2}[.-]\d{1,2}[.-](?:18|19|20)\d{2}\b"),
    re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b"),
    re.compile(r"\b(?:18|19|20)\d{2}(?:/\d{2,4})?s?\b" + _UNIT_AHEAD),
    re.compile(r"\b(?:BEK|LOV|[Bb]ekendtg\w*|[Ll]ov|[Rr]apport|[Rr]eport)\.?\s*"
               r"(?:nr\.?\s*)?\d+(?:/\d+)?"),
    re.compile(r"\b(?:nr|No)\.\s*\d+(?:/\d+)?"),
    # lists of citations: "sections 3 to 5", "§§ 6, 11", "Annexes 1-2", "section 2c", "p. 88"
    re.compile(r"(?:\b(?:[Ss]ections?|[Aa]nnex(?:es)?|[Bb]ilag|[Aa]rticles?|[Ss]tk|[Pp]ages?|pp?\.)|§§?)"
               r"\s*\d+(?:\.\d+)*[a-z]?(?:\(\d+\))*"
               r"(?:\s*(?:,|to|and|og|til|[-–])\s*\d+(?:\.\d+)*[a-z]?(?:\(\d+\))*)*"),
    re.compile(r"§+\s*\d+[a-z]?(?:\s*,?\s*stk\.\s*\d+)?(?:\s*,?\s*nr\.\s*\d+)?"),
    re.compile(r"\b[Ss]tk\.\s*\d+"),
    # a table or figure named with a letter or a dotted number: "Tabel C.1", "Figur 6.7"
    re.compile(r"\b(?:[Tt]ab(?:le|el)|[Ff]ig(?:ur|ure)?|[Ff]igure)\.?\s*[A-Z]?\.?\d+(?:\.\d+)*"),
    # names that carry a digit: a broadcaster, an article or box of a document
    re.compile(r"\bTV\s?2\b|\b(?:[Aa]rti[ck]el|[Aa]rticle|[Bb]oks|[Bb]ox)\s*\d+(?:\(\d+\))*"),
    # a date in words - "24 June 2024", "3. marts 2026" - is a date, not a quantity
    re.compile(r"\b\d{1,2}\.?\s+(?:[Jj]an(?:uary|uar)?|[Ff]eb(?:ruary|ruar)?|[Mm]ar(?:ch|ts)?|"
               r"[Aa]pr(?:il)?|[Mm]a[yj]|[Jj]un[ei]?|[Jj]ul[yi]?|[Aa]ug(?:ust)?|[Ss]ep(?:tember)?|"
               r"[Oo]kt(?:ober)?|[Oo]ct(?:ober)?|[Nn]ov(?:ember)?|[Dd]ec(?:ember)?|[Dd]ec)\b"),
    re.compile(r"\b(?:[Kk]ap|[Cc]hapter|[Ss]ection|[Ii]tem|[Ss]tep|[Ss]tage|[Pp]art|"
               r"[Tt]able|[Tt]abel|[Ff]igure|[Ff]ig|[Aa]ppendix|[Bb]ilag|[Aa]nnex|"
               r"[Pp]ages?|pp|[Vv]ol|[Vv]olume|[Ii]ssue|[Mm]ethod|[Cc]lass|[Tt]ier|"
               r"[Vv]ersion|[Vv]er|[Oo]ption|[Pp]hase)\.?\s*\d+(?:[.\-–]\d+)*\b"),
    re.compile(r"\bEPSG:\s*\d+|\bUTM\s*(?:zone\s*)?\d+[NS]?\b|\b[Zz]one\s+\d+\b"),
    # glued to a letter it is an identifier (UTM32, K1_si); after "/" it is not -
    # "2,589/443" is two numbers, and the second needs its chain as much as the first
    re.compile(r"(?<=[A-Za-zÆØÅæøåÄÖÜäöüé_^#@])\d+(?:[._]\d+)*"),
    re.compile(r"\b\d+(?:st|nd|rd|th|D)\b"),
    # an exponent or index written in braces, L^{-1}, x_{12}: notation, not a quantity
    re.compile(r"(?<=[\^_]\{)-?\d+(?:\.\d+)?(?=\})"),
    re.compile(r"\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b"),
    re.compile(r"\b\d+\(\d+\)"),
    re.compile(r"\b\d+:\s*\d+[–-]\d+\b"),
]
_JUSTIFIED = re.compile(r"\[[^\]\n]*\]\((?:\.\./)*(?:SOURCES\.md#F-[0-9a-f]{10}|"
                        r"CLAIMS\.md#C-[A-Za-z0-9\-_]+)\)")
_FENCE = re.compile(r"^```.*?^```", re.S | re.M)
_COMMENT = re.compile(r"<!--.*?-->", re.S)
_IMG = re.compile(r"!\[[^\]\n]*\]\([^)\n]*\)")
_CODE = re.compile(r"`[^`\n]*`")
_TAG = re.compile(r"<[^>\n]+>")
_URL = re.compile(r"https?://\S+|\bwww\.\S+|\b10\.\d{4,}/\S+")
_LINKTARGET = re.compile(r"\]\([^)\n]*\)")
_NUM = re.compile(r"\d+(?:[.,]\d+)*")
# The 1 that normalises a ratio - "2.37 to 1", "3:1" - is how a ratio is written,
# not a claim about the world. The compiler refused it on its very first run. It
# has to be recognised on the ORIGINAL text: by the time the exemption patterns
# run, a justified number in front of it has already been blanked, so a pattern
# that looks for the preceding digit never sees one.
_RATIO = re.compile(r"(?<=[\d)])\s*(?:to|:)\s*1\b(?![.,]\d)")


def _blank(m):
    return re.sub(r"[^\n]", " ", m.group(0))


def bare_numbers(text):
    """[(line, number, context)] for every quantity with no chain of justification."""
    orig = text.split("\n")
    out = []
    for ln, a, b, tok in _quantity_spans(text):
        src = orig[ln - 1] if ln - 1 < len(orig) else ""
        out.append((ln, tok, src[max(0, a - 45):b + 45].strip()))
    return out


def _quantity_spans(text):
    """(line, start, end, token) of every quantity in text that is not already
    justified - the tokens bare_numbers() names, with where they stand."""
    t = _RATIO.sub(_blank, text)
    for rx in (_FENCE, _COMMENT, _IMG, _JUSTIFIED, _CODE, _TAG, _URL, _LINKTARGET):
        t = rx.sub(_blank, t)
    out = []
    for ln, line in enumerate(t.split("\n"), 1):
        # a section number at the head of a heading ("## 2." / "### 2.3 "), never a
        # date that happens to open one ("## 2026-03-01")
        line = re.sub(r"^(\s*#+\s*)(\d+(?:\.\d+)*[a-z]?\.?)(?=\s)",
                      lambda m: m.group(1) + " " * len(m.group(2)), line)
        line = re.sub(r"^(\s*)(\d+)([.)]\s)",
                      lambda m: m.group(1) + " " * len(m.group(2)) + m.group(3), line)
        for rx in EXEMPT_PATTERNS:
            line = rx.sub(_blank, line)
        for m in _NUM.finditer(line):
            tok = m.group(0).rstrip(".,")
            if tok:
                out.append((ln, m.start(), m.end(), tok))
    return out


# ------------------------------------------------------------------ compiler ---
class Unjustified(ValueError):
    pass


def _prefix(rel):
    parts = rel.replace(os.sep, "/").split("/")
    return "../" * (len(parts) - 2) if parts[0] == "docs" and len(parts) > 2 else ""


def _message(rel, bad):
    lines = [f"{rel}: {len(bad)} number(s) with no chain of justification - "
             "the document was NOT written."]
    for ln, tok, ctx in bad[:12]:
        lines.append(f"  line {ln}: {tok:<12} ...{ctx}...")
    if len(bad) > 12:
        lines.append(f"  ... and {len(bad) - 12} more")
    lines.append("For each one: load it with live_json() so it carries its source, "
                 "compute it from values that do, link it with fig() if it is the "
                 "subject of a claim - or, if it is an identifier and not a "
                 "quantity, write it as `code`.")
    return "\n".join(lines)


def _said(text):
    """The words of a claim as a reader sees them - what a confirmation covers."""
    import chem
    import refs
    return re.sub(r"\s+", " ", chem.strip(refs.strip(strip_marks(text)))).strip()


def _record_spans(rel, found):
    """Which claims this page says, in which words - read by claims.py, so that a
    confirmation covers the wording and a reworded sentence goes stale."""
    from common import locked
    page = rel[len("docs/"):] if rel.startswith("docs/") else rel
    with locked("claim_spans"):
        try:
            d = json.load(open(SPANS, encoding="utf-8"))
        except (OSError, ValueError):
            d = {}
        new = dict(d)
        if found:
            new[page] = found
        else:
            new.pop(page, None)
        if new != d:
            tmp = f"{SPANS}.{os.getpid()}"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(new, f, ensure_ascii=False, indent=1, sort_keys=True)
                f.write("\n")
            os.replace(tmp, SPANS)


def _quotes_outside_history(text):
    """Quoted numbers standing outside a historical claim. What a construction
    licenses is part of it (K-QUOTE: "that the site once said this", not "that what
    it said was right"), and a number is refused where it is used for more."""
    quotes = [m for m in MARK.finditer(text)
              if (_seen.get(m.group(1)) or {}).get("src", [None])[0] == "quote"]
    if not quotes:
        return []
    import claims
    kinds = {c["id"]: c.get("kind") for c in claims.load()[0]["claims"]}
    ok = [(m.start(2), m.end(2)) for m in CLAIM.finditer(text)
          if kinds.get(m.group(1)) == "historical"]
    return [m.group(2) for m in quotes if not any(a <= m.start() < b for a, b in ok)]


def _claims(rel, pre, text):
    """Claim markers -> spans, refused unless each is one span inside one paragraph
    and the claims register holds it for this page, confirmed against this wording
    and current all the way down. The wording is recorded first, so that
    claims.py --reassess can read it."""
    if rel in EXEMPT:
        return text
    found, bad = {}, []
    for m in CLAIM.finditer(text):
        cid, body = m.group(1), m.group(2)
        if "\n\n" in body or C_OPEN in body:
            bad.append(f"{cid}: a claim is one span inside one paragraph")
        if cid in found:
            # only one wording can be confirmed: a second span would stand unread
            bad.append(f"{cid}: said twice on this page - one claim, one span; merge "
                       "the spans, or make the second its own claim")
        found.setdefault(cid, _said(body))
    rest = CLAIM.sub("", text)
    if C_OPEN in rest or C_CLOSE in rest:
        bad.append("a claim marker is left unclosed")
    loose = _quotes_outside_history(text)
    if loose:
        shown = ", ".join(repr(v) for v in loose[:8]) + (f" and {len(loose) - 8} more" if len(loose) > 8 else "")
        bad.append(f"{len(loose)} number(s) carried only as quotations of this site's past "
                   f"({shown}). A quotation licenses 'the site once said this', never "
                   "that it is so: derive each from data, a calculation or a pinned "
                   "document, or remove it. Only a historical claim - what this project "
                   "said, and why the reader should know - may quote.")
    _record_spans(rel, found)
    homes = {}
    if found:
        import claims
        bad += claims.said_problems(rel, found)
        homes = claims.homes(found)
    if bad:
        raise Unjustified(f"{rel}: {len(bad)} claim(s) the register does not justify - "
                          "the document was NOT written.\n  " + "\n  ".join(bad))

    def rep(m):
        cid, body = m.group(1), m.group(2).lstrip()
        # a list marker stays outside the span, or the line stops being a list item
        lead = re.match(r"(?:\d+[.)]|[-*+])\s+", body)
        head, body = (lead.group(0), body[lead.end():]) if lead else ("", body)
        return (f'{head}<span class="claim" data-claim="{cid}">{body}</span>'
                f'<sup class="claim-mark">[†]({pre}{homes.get(cid, "CLAIMS.md")}#{cid} '
                '"What this claim rests on")</sup>')
    return CLAIM.sub(rep, text)


def compile_doc(path, text):
    """Expand live markers into links, then refuse any number left without one."""
    rel = _rel(path).replace(os.sep, "/")
    pre = _prefix(rel)
    used = set()

    def rep(m):
        used.add(m.group(1))
        return f"[{m.group(2)}]({pre}SOURCES.md#{m.group(1)})"
    # claims first: each becomes a span tag, which every check below reads past
    text = _claims(rel, pre, text)
    # references to hypotheses go stale like numbers: checked, then rendered fresh
    import refs
    import chem
    stray = refs.bare(text) if rel not in EXEMPT else []
    loose = chem.bare(text) if rel not in EXEMPT else []
    text = chem.expand(refs.expand(rel, text))
    out = MARK.sub(rep, text)
    if rel not in EXEMPT:
        bad = bare_numbers(out)
        if bad:
            raise Unjustified(_message(rel, bad))
        if stray:
            raise Unjustified(refs.message(rel, stray))
        if loose:
            raise Unjustified(chem.message(rel, loose))
        # A source is not enough: what kind of number, built how, and allowed here?
        import constructions
        bad = constructions.enforce(rel, {i: _seen[i]["src"] for i in used if i in _seen})
        if bad:
            raise Unjustified(f"{rel}: {len(bad)} number(s) without a declared "
                              "construction, or on the wrong page\n" + "\n".join(bad)
                              + "\n  Declare it in data/manual/number_constructions.json; "
                              "constructions.py --uncovered lists every gap.")
    _record(rel, used)
    return out


# ------------------------------------------------------------ the register ---
def load_index():
    if os.path.exists(INDEX):
        try:
            return json.load(open(INDEX, encoding="utf-8"))
        except ValueError:
            pass
    return {"docs": {}, "entries": {}}


def _kids(node):
    if node[0] in ("op", "nary", "step"):
        return node[2]
    if node[0] == "agg":
        return node[3]
    return []


def _record(rel, used):
    """Under a lock: parallel generators all read-modify-write the one index."""
    from common import locked
    with locked("sources"):
        _record_unlocked(rel, used)


def _record_unlocked(rel, used):
    idx = load_index()
    ids, stack = set(), list(used)
    while stack:
        i = stack.pop()
        if i in ids:
            continue
        e = _seen.get(i) or idx["entries"].get(i)
        if not e:
            continue
        ids.add(i)
        keepw = e.get("where") or (idx["entries"].get(i) or {}).get("where")
        idx["entries"][i] = {"src": e["src"], "value": e["value"],
                             **({"where": keepw} if keepw else {})}
        stack.extend(_id(k) for k in _kids(e["src"]) if k[0] != "const")
    idx["docs"][rel] = sorted(ids)
    keep = {x for v in idx["docs"].values() for x in v}
    idx["entries"] = {k: v for k, v in idx["entries"].items() if k in keep}
    _enrich_all(idx)
    os.makedirs(os.path.dirname(INDEX), exist_ok=True)
    # atomic: a check reading the index while it is written must never see half a
    # file (it would read as empty, and every link would look broken)
    tmp = f"{INDEX}.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, INDEX)
    render_sources(idx)


def _build_steps():
    from common import load_build
    return load_build()["steps"]


def _producers():
    out = {}
    if os.path.exists(BUILD):
        for st in _build_steps():
            for o in st["outputs"]:
                out[o] = st["script"]
    return out


def _dig(doc, segs):
    for k in segs:
        if isinstance(doc, list):
            try:
                doc = doc[int(k)]
            except (ValueError, IndexError):
                return None
        elif isinstance(doc, dict):
            if k not in doc:
                return None
            doc = doc[k]
        else:
            return None
    return doc


def _short(v):
    if isinstance(v, dict):
        return "{… %d keys}" % len(v)
    if isinstance(v, list):
        return "[… %d items]" % len(v)
    t = json.dumps(v, ensure_ascii=False)
    return t if len(t) <= 80 else t[:77] + "…"


def _excerpt(parent, key, ppath):
    """The rows around a field in its data file, so the value can be seen among
    its neighbours rather than alone. Windowed, so a large object stays small."""
    rows = []
    if isinstance(parent, dict):
        keys = list(parent)
        if len(keys) > 30:
            at = keys.index(key) if key in keys else 0
            keys = keys[max(0, at - 12): at + 13]
        rows = [[str(k), _short(parent[k])] for k in keys]
    elif isinstance(parent, list):
        try:
            at = int(key)
        except ValueError:
            at = 0
        rows = [[str(j), _short(parent[j])]
                for j in range(max(0, at - 6), min(len(parent), at + 7))]
    return {"parent": ppath or "(top level)", "target": str(key), "rows": rows}


def _window(text, needle, width=260):
    at = text.lower().find(needle.lower())
    if at < 0:
        return None
    a, b = max(0, at - width), min(len(text), at + len(needle) + width)
    return {"text": re.sub(r"\s+", " ", text[a:b]).strip(), "mark": needle}


LINEAGE = os.path.join(ROOT, "docs", "data", "lineage")


def _lineages():
    """The numbers whose making is recorded (scripts/lineage.py, PROVENANCE_SPEC.md),
    as (matcher, lineage file relative to docs/ as the reader fetches it). A record
    names its own number by file and field, and under "also" the other entries that
    stand for the same figure - read from another file, printed in a pinned
    document, or quoted from this site's past - so that one figure opens one record
    wherever it is printed."""
    out = []
    if os.path.isdir(LINEAGE):
        for fn in sorted(os.listdir(LINEAGE)):
            if not fn.endswith(".json"):
                continue
            try:
                with open(os.path.join(LINEAGE, fn), encoding="utf-8") as f:
                    num = json.load(f)["number"]
                rel = "data/lineage/" + fn
                out.append((("leaf", num["file"], num["path"]), rel))
                out.extend((tuple(m), rel) for m in num.get("also", []))
            except (ValueError, KeyError, TypeError):
                continue
    return out


def _same_value(a, b):
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)


def _lineage_for(lin, e):
    """The record an entry opens: its own, or the one that names it as the same
    figure - a leaf by file and field, a reading by document and value, a quotation
    of this site's past by value."""
    n = e["src"]
    for m, rel in lin:
        if m[0] != n[0]:
            continue
        if m[0] == "leaf" and (n[1], n[2]) == (m[1], m[2]):
            return rel
        if m[0] == "reading" and n[1] == m[1] and _same_value(e["value"], m[2]):
            return rel
        if m[0] == "quote" and _same_value(e["value"], m[1]):
            return rel
    return None


def _enrich_all(idx):
    """Everything the views need, stored with the entry so the reader - which
    cannot open data/derived on the published site - has it to hand."""
    prod, files, pins = _producers(), {}, os.path.join(ROOT, "data", "derived", "pins")
    lin = _lineages()
    for i, e in idx["entries"].items():
        n = e["src"]
        t = n[0]
        rec = _lineage_for(lin, e)
        if rec:
            e["lineage"] = rec
        if t == "leaf":
            file, path = n[1], n[2]
            if prod.get(file):
                e["producer"] = prod[file]
            full = os.path.join(ROOT, file)
            if file.startswith("data/") and os.path.exists(full) \
                    and os.path.getsize(full) <= 20_000_000:
                if file not in files:
                    try:
                        files[file] = json.load(open(full, encoding="utf-8"))
                    except ValueError:
                        files[file] = None
                doc = files[file]
                if doc is not None:
                    segs = _split(path)
                    pv = (doc.get("_provenance") or {}).get(".".join(segs)) \
                        if isinstance(doc, dict) else None
                    if pv:
                        e["provenance"] = pv
                    e["excerpt"] = _excerpt(_dig(doc, segs[:-1]), segs[-1] if segs else "",
                                            ".".join(segs[:-1]))
        elif t == "reading":
            p = os.path.join(pins, n[1] + ".txt")
            if os.path.exists(p):
                text = open(p, encoding="utf-8").read()
                w = _window(text, n[3])
                if w:
                    e["excerpt"] = w
                if n[2] == "count":
                    # Every occurrence, by the rule claims.py counts with, so the
                    # reader sees what was counted as the same thing - including
                    # the compounds a substring count sweeps in.
                    hits = []
                    for m in re.finditer(re.escape(n[3]), text, re.I):
                        a, b = max(0, m.start() - 70), min(len(text), m.end() + 70)
                        hits.append([re.sub(r"\s+", " ", text[a:m.start()]),
                                     text[m.start():m.end()],
                                     re.sub(r"\s+", " ", text[m.end():b])])
                    e["hits"] = hits
        elif t == "quote":
            text = _git_text(n[1], n[2])
            if text is not None:
                # a passage from the archive has no slot: shown by the window around it
                hits = _locate_all(text, n[4]) if len(n) > 4 and n[4] and SLOT in n[4] else []
                if len(hits) == 1:
                    _, a, b = hits[0]
                    lo, hi = max(0, a - 200), min(len(text), b + 200)
                    e["excerpt"] = {"text": re.sub(r"\s+", " ", text[lo:hi]).strip(),
                                    "mark": text[a:b]}
                else:
                    w = _window(text, n[3], 200)
                    if w:
                        e["excerpt"] = w
        wh = e.get("where")
        if wh:
            src = os.path.join(ROOT, wh[0])
            if os.path.exists(src):
                lines = open(src, encoding="utf-8", errors="replace").read().split("\n")
                a = max(0, wh[1] - 7)
                e["code"] = {"file": wh[0], "line": wh[1], "first": a + 1,
                             "text": "\n".join(lines[a:wh[1] + 3])}
    import constructions
    constructions.annotate(idx)


def _fmt(v):
    if v is None:
        return "…"
    if isinstance(v, float):
        return f"{v:.6g}"
    return f"{v:,}" if isinstance(v, int) else str(v)


def _provenance(file, path, cache):
    if not file.startswith("data/derived/"):
        return None
    p = os.path.join(ROOT, file)
    if not os.path.exists(p) or os.path.getsize(p) > 20_000_000:
        return None
    if file not in cache:
        try:
            cache[file] = json.load(open(p, encoding="utf-8")).get("_provenance") or {}
        except (ValueError, AttributeError):
            cache[file] = {}
    return cache[file].get(path)


def _operand(node, entries):
    if node[0] == "const":
        return _fmt(node[1])
    i = _id(node)
    e = entries.get(i, {})
    label = _fmt(e.get("value")) if e.get("value") is not None else \
        (f"{node[1]} › {node[2]}" if node[0] == "leaf" else "a calculation")
    return f"[{label}](SOURCES.md#{i})"


def _kindline(w, e):
    k = e.get("kind")
    if not k:
        return
    cs = ", ".join(f"[`{c}`](#{c})" for c in e.get("constructions", []))
    w.append(f"- **Kind:** {k}" + (" · **built on simulation**" if e.get("synthetic") else "")
             + (f" · made by {cs}" if cs else ""))
    if (e.get("field") or {}).get("is"):
        w.append(f"- **What this field is:** {e['field']['is']}")


def _constructions(w, idx):
    cons = idx.get("constructions") or {}
    if not cons:
        return
    w.append("## How each kind of number was made")
    w.append("")
    w.append("Where a number came from is not the same as why it should be believed. "
             "Each declaration below says what kind of numbers a script or a step "
             "produces, the model behind them, why that model is justified, what "
             "nothing justifies yet, when they would be void, and what they may and "
             "may not be used to claim. It is held in "
             "`data/manual/number_constructions.json`, and a change in any file it watches "
             "makes it stale until it is read again.")
    w.append("")
    for cid, c in sorted(cons.items()):
        w.append(f'<a id="{cid}"></a>')
        w.append(f"### {c.get('title', cid)}")
        w.append("")
        conf = c.get("confirmed") or {}
        w.append(f"`{cid}` · covers {c.get('covers')} · **{c.get('status')}**"
                 + (f" · read by {conf.get('by')}, {conf.get('on')}" if conf else ""))
        w.append("")
        w.append(c.get("what", ""))
        w.append("")
        w.append(f"- **Model:** {c.get('model', '')}")
        for label, key in (("Assumes", "assumptions"), ("Justified because", "justified"),
                           ("Not justified by anything yet", "gaps"), ("Void if", "void_if")):
            for x in c.get(key) or []:
                if isinstance(x, dict):
                    ref = x.get("ref", "")
                    link = ref if ref.startswith("http") else f"../{ref.split(':')[0]}"
                    x = x["text"] + (f" ([{ref}]({link}))" if ref else "")
                w.append(f"- **{label}:** {x}")
        if key == "gaps" and not c.get("gaps"):
            pass
        w.append(f"- **May support:** {c.get('licenses', '')}")
        w.append(f"- **May not:** {c.get('not_licensed', '')}")
        w.append("")


def render_sources(idx=None):
    """SOURCES.md, and the number store the reader's menu loads. Each number used to
    get its own entry here with the same explanations repeated (3.9 MB); now this
    page lists once each what the menus draw on - the tables, and the sources of the
    numbers in running text - and every number is one small record in the store
    (scripts/numbers_store.py)."""
    import numbers_store
    idx = idx or load_index()
    tt = numbers_store.tables_and_text(idx["entries"])
    numbers_store.publish(idx, tt)
    w = numbers_store.sources_page(idx, tt)
    _constructions(w, idx)
    tmp = f"{SOURCES_MD}.{os.getpid()}"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(w).rstrip("\n") + "\n")
    os.replace(tmp, SOURCES_MD)


if __name__ == "__main__":
    render_sources()
    print(f"wrote {_rel(SOURCES_MD)} ({len(load_index()['entries'])} entries)")
