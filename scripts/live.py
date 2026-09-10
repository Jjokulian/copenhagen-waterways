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


def strip_marks(text):
    """The plain text a marker stands for - for logs, JSON, anything but a doc."""
    return MARK.sub(lambda m: m.group(2), text) if OPEN in text else text


# ---------------------------------------------------------------- derivations ---
def _general(path):
    return ".".join("*" if p.isdigit() else p for p in path.split(".")) if path else path


def _shape(n):
    """What identifies a derivation: its structure, not its current values, so a
    link survives the data changing underneath it."""
    t = n[0]
    if t == "const":
        return n
    if t == "leaf":
        return n[:3]
    if t in ("op", "nary"):
        return [t, n[1], [_shape(k) for k in n[2]]]
    if t == "agg":
        return ["agg", n[1], sorted(n[2]), [_shape(k) for k in n[3]]]
    if t in ("reading", "quote"):
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
    if node[0] in ("op", "nary"):
        for k, v in zip(node[2], node[3]):
            if k[0] != "const":
                _remember(k, v)
    elif node[0] == "agg":
        for k in node[3]:
            if k[0] != "const":
                _remember(k, None)
    return i


def _mark(node, value, shown):
    i = _id(node)
    _seen[i] = {"src": node, "value": value}
    return OPEN + i + MID + shown + CLOSE


def reading(source_id, kind, arg, value, shown, meta):
    """A number read from a pinned external document. kind is 'count' (occurrences
    of arg in the pinned text) or 'phrase' (arg must be present in it)."""
    return _mark(["reading", source_id, kind, arg, meta], value, shown)


def quoted(commit, file, shown):
    """What this site said at a past commit. Permanently true; verified by caller."""
    return _mark(["quote", commit, file, shown], shown, shown)


def stated(name, value, shown, reason):
    """A value chosen rather than measured, shown as a choice with its reason."""
    return _mark(["stated", name, reason], value, shown)


class _Live:
    def _v(self):
        return float(self) if isinstance(self, float) else int(self)

    def __format__(self, spec):
        v = self._v()
        shown = type(v).__format__(v, spec)
        i = _remember(self.src, v)
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
    return f"{path}.{k}" if path else str(k)


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
    re.compile(r"\b(?:18|19|20)\d{2}-\d{2}-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2})?)?"),
    re.compile(r"\b(?:18|19|20)\d{6}\b"),
    re.compile(r"\b\d{1,2}[.-]\d{1,2}[.-](?:18|19|20)\d{2}\b"),
    re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b"),
    re.compile(r"\b(?:18|19|20)\d{2}(?:/\d{2,4})?s?\b" + _UNIT_AHEAD),
    re.compile(r"\b(?:BEK|LOV|[Bb]ekendtg\w*|[Ll]ov|[Rr]apport|[Rr]eport)\.?\s*"
               r"(?:nr\.?\s*)?\d+(?:/\d+)?"),
    re.compile(r"\b(?:nr|No)\.\s*\d+(?:/\d+)?"),
    re.compile(r"§+\s*\d+[a-z]?(?:\s*,?\s*stk\.\s*\d+)?(?:\s*,?\s*nr\.\s*\d+)?"),
    re.compile(r"\bstk\.\s*\d+"),
    re.compile(r"\b(?:[Kk]ap|[Cc]hapter|[Ss]ection|[Ii]tem|[Ss]tep|[Ss]tage|[Pp]art|"
               r"[Tt]able|[Tt]abel|[Ff]igure|[Ff]ig|[Aa]ppendix|[Bb]ilag|[Aa]nnex|"
               r"[Pp]ages?|pp|[Vv]ol|[Vv]olume|[Ii]ssue|[Mm]ethod|[Cc]lass|[Tt]ier|"
               r"[Vv]ersion|[Vv]er|[Oo]ption|[Pp]hase)\.?\s*\d+(?:[.\-–]\d+)*\b"),
    re.compile(r"\bEPSG:\s*\d+|\bUTM\s*(?:zone\s*)?\d+[NS]?\b|\b[Zz]one\s+\d+\b"),
    re.compile(r"(?<=[A-Za-zÆØÅæøåÄÖÜäöüé_^/#@])\d+(?:[._]\d+)*"),
    re.compile(r"\b\d+(?:st|nd|rd|th|D)\b"),
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
    t = _RATIO.sub(_blank, text)
    for rx in (_FENCE, _COMMENT, _IMG, _JUSTIFIED, _CODE, _TAG, _URL, _LINKTARGET):
        t = rx.sub(_blank, t)
    orig = text.split("\n")
    out = []
    for ln, line in enumerate(t.split("\n"), 1):
        line = re.sub(r"^(\s*#+\s*)([\d.]+)",
                      lambda m: m.group(1) + " " * len(m.group(2)), line)
        line = re.sub(r"^(\s*)(\d+)([.)]\s)",
                      lambda m: m.group(1) + " " * len(m.group(2)) + m.group(3), line)
        for rx in EXEMPT_PATTERNS:
            line = rx.sub(_blank, line)
        for m in _NUM.finditer(line):
            tok = m.group(0).rstrip(".,")
            if not tok:
                continue
            src = orig[ln - 1] if ln - 1 < len(orig) else ""
            at = max(0, m.start() - 45)
            ctx = src[at:m.end() + 45].strip()
            out.append((ln, tok, ctx))
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


def compile_doc(path, text):
    """Expand live markers into links, then refuse any number left without one."""
    rel = _rel(path).replace(os.sep, "/")
    pre = _prefix(rel)
    used = set()

    def rep(m):
        used.add(m.group(1))
        return f"[{m.group(2)}]({pre}SOURCES.md#{m.group(1)})"
    out = MARK.sub(rep, text)
    if rel not in EXEMPT:
        bad = bare_numbers(out)
        if bad:
            raise Unjustified(_message(rel, bad))
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
    if node[0] in ("op", "nary"):
        return node[2]
    if node[0] == "agg":
        return node[3]
    return []


def _record(rel, used):
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
        idx["entries"][i] = {"src": e["src"], "value": e["value"]}
        stack.extend(_id(k) for k in _kids(e["src"]) if k[0] != "const")
    idx["docs"][rel] = sorted(ids)
    keep = {x for v in idx["docs"].values() for x in v}
    idx["entries"] = {k: v for k, v in idx["entries"].items() if k in keep}
    os.makedirs(os.path.dirname(INDEX), exist_ok=True)
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    render_sources(idx)


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


def render_sources(idx=None):
    idx = idx or load_index()
    entries = idx["entries"]
    producers = {}
    if os.path.exists(BUILD):
        for st in json.load(open(BUILD, encoding="utf-8"))["steps"]:
            for o in st["outputs"]:
                producers[o] = st["script"]
    used_by = {}
    for doc, ids in idx["docs"].items():
        for i in ids:
            used_by.setdefault(i, []).append(doc)
    cache = {}
    w = []
    w.append("# Where each number comes from")
    w.append("")
    w.append("*Generated by `scripts/live.py` every time a document is written. Every "
             "number on this site that was computed from data links here, and each "
             "entry below is its chain: the field it was read from and the script "
             "that produced that field, or the calculation that made it, with every "
             "operand linked to its own entry. A number with no entry here and no "
             "claim in [CLAIMS.md](CLAIMS.md) cannot be published: the compiler "
             "refuses the document.*")
    w.append("")
    leaves = sorted(((i, e) for i, e in entries.items() if e["src"][0] == "leaf"),
                    key=lambda x: (x[1]["src"][1], x[1]["src"][2]))
    special = {"reading", "quote", "stated"}
    calcs = [(i, e) for i, e in entries.items()
             if e["src"][0] not in special and e["src"][0] != "leaf"]
    readings = [(i, e) for i, e in entries.items() if e["src"][0] == "reading"]
    quotes = [(i, e) for i, e in entries.items() if e["src"][0] == "quote"]
    stateds = [(i, e) for i, e in entries.items() if e["src"][0] == "stated"]
    if leaves:
        w.append("## Read from data")
        w.append("")
    for i, e in leaves:
        _, file, path = e["src"][:3]
        w.append(f'<a id="{i}"></a>')
        w.append(f"### `{file}` › `{path}`")
        w.append("")
        w.append(f"`{i}` · **read from data** · {_fmt(e['value'])}")
        w.append("")
        prod = producers.get(file)
        if prod:
            w.append(f"- **Produced by:** [`{prod}`](../{prod})")
        elif file.startswith("data/raw/"):
            w.append("- **Produced by:** a raw extract, as fetched - see "
                     "[DATA_SOURCES.md](DATA_SOURCES.md)")
        elif file.startswith(".."):
            w.append("- **Produced by:** a sibling project, read in place")
        pv = _provenance(file, path, cache)
        if pv:
            w.append(f"- **Counted as the same thing:** {pv.get('counts_as')}")
            w.append(f"- **Calculation:** {pv.get('calculation')}")
            for x in pv.get("excluded") or []:
                w.append(f"- **Excluded:** {x['reason']} ({_fmt(x['n'])})")
            if pv.get("alternatives"):
                w.append("- **Other defensible definitions:** " + "; ".join(
                    f"{a['definition']} → {_fmt(a['value'])}" for a in pv["alternatives"]))
        else:
            w.append("- *How this field was counted is not recorded by the script "
                     "that wrote it.*")
        if used_by.get(i):
            w.append("- **Used in:** " + ", ".join(
                f"[{d.split('/')[-1]}]({d.split('/')[-1]})" for d in sorted(used_by[i])))
        w.append("")
    if calcs:
        w.append("## Calculated in a generator")
        w.append("")
    for i, e in calcs:
        n = e["src"]
        t, sym = n[0], n[1]
        w.append(f'<a id="{i}"></a>')
        if t == "agg":
            total = sum(n[2].values()) + len(n[3]) + n[4]
            w.append(f"### {'Sum' if sym == '+' else 'Product'} over {_fmt(total)} "
                     f"terms = {_fmt(e['value'])}")
            w.append("")
            w.append(f"`{i}` · **calculated** · {_fmt(e['value'])}")
            w.append("")
            for k, c in sorted(n[2].items()):
                w.append(f"- `{k}` × {_fmt(c)}")
            for k in n[3]:
                w.append(f"- {_operand(k, entries)}")
            if n[4]:
                w.append(f"- … and {_fmt(n[4])} further calculated terms")
        else:
            ops = [_operand(k, entries) for k in n[2]]
            if t == "nary":
                expr = f" {sym} ".join(ops)
            elif sym in ("neg", "abs"):
                expr = f"{sym}({ops[0]})"
            elif sym == "round":
                expr = f"round({ops[0]}, {ops[1]})"
            else:
                expr = f"{ops[0]} {sym} {ops[1]}"
            w.append(f"### Calculated: {_fmt(e['value'])}")
            w.append("")
            w.append(f"`{i}` · **calculated** · {_fmt(e['value'])}")
            w.append("")
            w.append(f"- **Calculation:** {expr} = {_fmt(e['value'])}")
        if used_by.get(i):
            w.append("- **Used in:** " + ", ".join(
                f"[{d.split('/')[-1]}]({d.split('/')[-1]})" for d in sorted(used_by[i])))
        w.append("")
    def used(i):
        if used_by.get(i):
            w.append("- **Used in:** " + ", ".join(
                f"[{d.split('/')[-1]}]({d.split('/')[-1]})" for d in sorted(used_by[i])))
        w.append("")

    if readings:
        w.append("## Read from a pinned document")
        w.append("")
        w.append("Each of these was read out of an external document whose text is "
                 "pinned by its sha256. The reading is recomputed from the pinned copy "
                 "every time, and a change in the document is detected by its hash, "
                 "which makes every claim resting on it stale until reassessed.")
        w.append("")
    for i, e in sorted(readings, key=lambda x: (x[1]["src"][1], x[1]["src"][3])):
        _, sid, kind, arg, meta = e["src"][:5]
        meta = meta or {}
        what = f'occurrences of "{arg}"' if kind == "count" else f'the phrase "{arg}"'
        w.append(f'<a id="{i}"></a>')
        w.append(f"### `{sid}` — {what}")
        w.append("")
        w.append(f"`{i}` · **read from a pinned document** · {_fmt(e['value'])}")
        w.append("")
        if meta.get("url"):
            w.append(f"- **Document:** [{meta.get('title', sid)}]({meta['url']}), "
                     f"retrieved {meta.get('retrieved', '?')}")
        if meta.get("sha256"):
            w.append(f"- **Pinned text sha256:** `{meta['sha256'][:16]}…`")
        w.append(f"- **Reading:** {what}, recomputed from the pinned text")
        if meta.get("checked"):
            w.append(f"- **Last checked against the live document:** {meta['checked']}"
                     f" — {meta.get('status', 'unknown')}")
        used(i)
    if quotes:
        w.append("## Quoted from an earlier version of this site")
        w.append("")
        w.append("What this site said at a past commit. A quotation of the past is "
                 "permanently true, so it never goes stale; each is verified against "
                 "`git show` at that commit, so a misquotation is refused.")
        w.append("")
    for i, e in sorted(quotes, key=lambda x: x[1]["src"][1]):
        _, commit, file, shown = e["src"][:4]
        w.append(f'<a id="{i}"></a>')
        w.append(f"### As published at `{commit}` in `{file}`")
        w.append("")
        w.append(f"`{i}` · **quoted from an earlier version** · {shown}")
        w.append("")
        w.append(f"- **Where:** [`{file}` at `{commit}`]"
                 f"(https://github.com/Jjokulian/copenhagen-waterways/blob/{commit}/{file})")
        used(i)
    if stateds:
        w.append("## Stated, not measured")
        w.append("")
        w.append("Values chosen rather than measured - a threshold, a limit. They are "
                 "shown as choices, with the reason for each, because a result built "
                 "on one changes if the choice does.")
        w.append("")
    for i, e in sorted(stateds, key=lambda x: x[1]["src"][1]):
        _, name, reason = e["src"][:3]
        w.append(f'<a id="{i}"></a>')
        w.append(f"### Stated: `{name}`")
        w.append("")
        w.append(f"`{i}` · **stated, not measured** · {_fmt(e['value'])}")
        w.append("")
        w.append(f"- **Why this value:** {reason}")
        used(i)
    with open(SOURCES_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(w).rstrip("\n") + "\n")


if __name__ == "__main__":
    render_sources()
    print(f"wrote {_rel(SOURCES_MD)} ({len(load_index()['entries'])} entries)")
