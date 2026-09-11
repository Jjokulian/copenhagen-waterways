#!/usr/bin/env python3
"""What every claim rests on, as a graph - and whether what it says is still true.

Prose hides dependency. A sentence saying the diurnal amplitude is below half a
milligram reads like a measurement, and it is a bound derived from a synthetic
recovery run on a real schedule under a stipulated signal shape and a noise model
- four different kinds of thing, one of which is not data at all. So every
substantive claim is registered with the graph of what it rests on, drawn beside
it, with node shape and colour carrying the kind.

THE GRAPH IS CHECKED FOR CYCLES. A cycle in a claim graph is circular reasoning
made visible, and this refuses to write a page containing one.

LIVE TEXT. No number is typed into a claim, a note, an assessment or a node
description. Each is a placeholder resolved when the page is built:

  {fig:name}                    a registered figure, read live from its data file
  {fig:name|.2f}                the same, formatted
  {calc:a / (a + b) * 100|.1f}  arithmetic over registered figures, rendered as a
                                calculation with each operand linked
  {count:SOURCE:term}           occurrences of a term in a pinned document's text
  {read:SOURCE:170|divideret med 170 kg}
                                a number read from a pinned document, held only
                                while the phrase is still present in it
  {was:COMMIT:FILE:210}         what this site said at a past commit, verified
                                against git so a misquotation is refused
  {param:name}                  a stated value, shown as a choice with its reason

The page is written through write_doc(), so a number typed straight into any of
those texts stops it being written, exactly as it would for any other page.

STALENESS. A justification is itself a claim, and it goes stale when anything it
rested on changes. Each claim records what it SAW when someone last confirmed it:
the resolved value of every placeholder in its text, its note, its assessment and
the descriptions of what it rests on, and the hash of every pinned document it
reads. When any of that changes the claim is STALE and the page is not written
until someone reads it again and runs --reassess. A number that updates silently
inside prose that no longer follows from it is the failure this exists for.

    python3 scripts/claims.py                   build the page; refuse if stale
    python3 scripts/claims.py --check           validate only
    python3 scripts/claims.py --reassess C-ID --by NAME     (or: all)
    python3 scripts/claims.py --recheck         refetch pinned documents
    python3 scripts/claims.py --repin SOURCE    adopt a document that changed

A confirmation is somebody's act, so --reassess requires --by.
"""
import ast
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT, log, read_json, write_doc, fragments
import live

SRC = os.path.join(ROOT, "data", "manual", "claims.json")
OUT = os.path.join(ROOT, "docs", "CLAIMS.md")
ARCHIVE = os.path.join(ROOT, "docs", "ARCHIVE.md")
PINS = os.path.join(ROOT, "data", "derived", "pins")
UA = "copenhagen-waterways research (github.com/Jjokulian/copenhagen-waterways)"

SHAPE = {
    "held":       ('[("', '")]'),
    "external":   ('[("', '")]'),
    "gap":        ('{{"', '"}}'),
    "synthetic":  ('>"', '"]'),
    "assumption": ('{"', '"}'),
    "script":     ('["', '"]'),
    "history":    ('[/"', '"/]'),
    "untraced":   ('(("', '"))'),
    "claim":      ('("', '")'),
}
STYLE = {
    "held":       "fill:#1c4e70,stroke:#58a6ff,color:#e6edf3",
    "external":   "fill:#3d3357,stroke:#a58cf0,color:#e6edf3",
    "gap":        "fill:#5c2323,stroke:#ff7b72,color:#ffdcd7,stroke-dasharray:4 3",
    "synthetic":  "fill:#4a3a12,stroke:#e8a33d,color:#ffeccc",
    "assumption": "fill:#4a3a12,stroke:#e8a33d,color:#ffeccc,stroke-dasharray:3 2",
    "script":     "fill:#21262d,stroke:#8b949e,color:#c9d1d9",
    "history":    "fill:#1f2a3a,stroke:#7d8fa8,color:#dce6f2",
    "untraced":   "fill:#262626,stroke:#ff7b72,color:#e6edf3,stroke-dasharray:2 2",
    "claim":      "fill:#173a26,stroke:#3fb950,color:#d7ffe4",
}
KIND_NOTE = {
    "measured": "rests on measurement",
    "bounded": "a bound, not a point estimate",
    "simulated": "about the instrument, not the world",
    "modelled": "the output of somebody's model of the world, not an observation of it",
    "provisional": "unchecked - see the graph for what would check it",
    "gap": "a statement that something cannot be established",
    "argued": "follows by reasoning from what it rests on - the argument is given in full",
    "attributed": "somebody else's claim, shown with what could be found behind it",
    "historical": "what this project itself did or said, checked against its own history",
    "stipulated": "a rule this project sets itself, with its reason",
    "code": "what this project's code does, read from the code",
}
# Where a chain may end. A claim rests on these or on other claims, and every path
# down from a claim ends in one of them: data, a document, a stipulation, a gap,
# code, this project's own history - or an honest "untraced": what was searched,
# and that nothing further was found. Nothing below an untraced node is claimed.
TERMINAL = {"held", "external", "gap", "synthetic", "assumption", "script", "history",
            "untraced"}


class Refused(Exception):
    pass


_ORIGIN = {}      # (collection, id) -> the file it came from


def load():
    """claims.json and its fragments in claims.d/, merged. Parallel workers each
    add figures, params, sources, nodes and claims in a fragment of their own."""
    d = read_json(SRC)
    _ORIGIN.clear()
    for f in fragments(SRC)[1:]:
        frag = read_json(f)
        for k in ("figures", "params", "sources"):
            for name, v in frag.get(k, {}).items():
                if name in d.setdefault(k, {}):
                    if d[k][name] == v:
                        continue            # the same source pinned twice: one entry
                    raise Refused(f"{os.path.relpath(f, ROOT)}: {k} '{name}' is already "
                                  "defined elsewhere, differently - pick another name")
                d[k][name] = v
                _ORIGIN[(k, name)] = f
        for k in ("nodes", "claims"):
            have = {x["id"] for x in d.setdefault(k, [])}
            for x in frag.get(k, []):
                if x["id"] in have:
                    raise Refused(f"{os.path.relpath(f, ROOT)}: {k[:-1]} '{x['id']}' is "
                                  "already defined - elsewhere, or earlier in this file")
                have.add(x["id"])
                d[k].append(x)
                _ORIGIN[(k, x["id"])] = f
    return d, {n["id"]: n for n in d["nodes"]}, {c["id"]: c for c in d["claims"]}


def save(d, files=None):
    """Write items back to the file each came from - only `files`, when given, so
    a worker confirming its own claim never rewrites a file somebody else has
    edited since it was read."""
    for f in fragments(SRC):
        if files is not None and f not in files:
            continue
        raw = read_json(f)
        for k in ("figures", "params", "sources"):
            if k in raw or any(_ORIGIN.get((k, n), SRC) == f for n in d.get(k, {})):
                raw[k] = {n: v for n, v in d.get(k, {}).items() if _ORIGIN.get((k, n), SRC) == f}
        for k in ("nodes", "claims"):
            if k in raw or any(_ORIGIN.get((k, x["id"]), SRC) == f for x in d.get(k, [])):
                raw[k] = [x for x in d.get(k, []) if _ORIGIN.get((k, x["id"]), SRC) == f]
        with open(f, "w", encoding="utf-8") as fh:
            json.dump(raw, fh, indent=1, ensure_ascii=False)
            fh.write("\n")


# ------------------------------------------------------------ pinned documents ---
def _fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def _extract(raw):
    if raw[:4] != b"%PDF":
        return raw.decode("utf-8", "replace")
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as t:
        t.write(raw)
        name = t.name
    try:
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", name, "-"],
                           capture_output=True)
        return r.stdout.decode("utf-8", "replace")
    finally:
        os.remove(name)


def pin_text(d, sid):
    """The text of a document as it was when pinned. Fetched and verified if not
    cached; refused if the live document no longer matches the pin."""
    p = os.path.join(PINS, sid + ".txt")
    if not os.path.exists(p):
        s = d["sources"][sid]
        text = _extract(_fetch(s["url"]))
        if hashlib.sha256(text.encode()).hexdigest() != s["sha256"]:
            raise Refused(f"{sid}: the live document no longer matches its pin and no "
                          f"pinned copy is cached. Run --recheck, read it, then "
                          f"--repin {sid}.")
        os.makedirs(PINS, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
    return open(p, encoding="utf-8").read()


def recheck(d):
    today = datetime.date.today().isoformat()
    for sid, s in d.get("sources", {}).items():
        try:
            text = _extract(_fetch(s["url"]))
        except Exception as e:                      # a source going dark is news too
            s["checked"], s["status"] = today, f"could not fetch: {type(e).__name__}"
            log(f"  {sid}: {s['status']}")
            continue
        s["checked"] = today
        if hashlib.sha256(text.encode()).hexdigest() == s["sha256"]:
            s["status"] = "unchanged since pinned"
        else:
            s["status"] = "CHANGED since pinned"
            os.makedirs(PINS, exist_ok=True)
            with open(os.path.join(PINS, sid + ".new.txt"), "w", encoding="utf-8") as f:
                f.write(text)
        log(f"  {sid}: {s['status']}")
    save(d, {_ORIGIN.get(("sources", k), SRC) for k in d.get("sources", {})})


def repin(d, sid):
    p = os.path.join(PINS, sid + ".new.txt")
    if not os.path.exists(p):
        raise Refused(f"{sid}: nothing to adopt - run --recheck first")
    text = open(p, encoding="utf-8").read()
    s = d["sources"][sid]
    s["sha256"] = hashlib.sha256(text.encode()).hexdigest()
    s["retrieved"] = datetime.date.today().isoformat()
    s["status"] = "re-pinned; every claim reading it must be reassessed"
    os.replace(p, os.path.join(PINS, sid + ".txt"))
    save(d, {_ORIGIN.get(("sources", sid), SRC)})


# ----------------------------------------------------------------- live text ---
# {calc@K-ID:expr} applies a declared construction step to the calculation
# {ref:K1} / {ref:K1|title} a checked reference to the hypothesis register;
# {chem:O2} a checked chemical species - both entities, like numbers
PH = re.compile(r"\{(fig|calc(?:@K-[A-Z0-9-]+)?|count|read|was|param|ref|chem):([^{}]+)\}")


def _meta(d, sid):
    s = d["sources"][sid]
    return {k: s.get(k) for k in ("title", "url", "retrieved", "sha256",
                                  "checked", "status")}


def _path(r):
    return r["path"] if isinstance(r["path"], list) else r["path"].split(".")


def _figure(d, name, cache):
    r = d.get("figures", {}).get(name)
    if r is None:
        raise Refused(f"figure '{name}' is not registered in claims.json")
    f = r["file"]
    if f not in cache:
        full = os.path.join(ROOT, f)
        if not os.path.exists(full):
            raise Refused(f"figure '{name}' reads {f}, which is not built")
        cache[f] = live.live_json(full)
    node = cache[f]
    for k in _path(r):
        try:
            node = node[int(k)] if isinstance(node, list) else node[k]
        except (KeyError, IndexError, ValueError, TypeError):
            raise Refused(f"figure '{name}': {r['path']} not found in {f}")
    return node, r.get("fmt", "{}")


_OPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b}


def _calc(d, expr, cache):
    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.BinOp) and type(n.op) in _OPS:
            return _OPS[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
            return -ev(n.operand)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) \
                and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.Name):
            return _figure(d, n.id, cache)[0]
        raise Refused(f"calc '{expr}': only + - * / over registered figures")
    try:
        return ev(ast.parse(expr, mode="eval"))
    except SyntaxError:
        raise Refused(f"calc '{expr}' does not parse")


def _git_show(commit, file):
    r = subprocess.run(["git", "show", f"{commit}:{file}"], cwd=ROOT,
                       capture_output=True)
    if r.returncode != 0:
        raise Refused(f"{file} does not exist at {commit}")
    return r.stdout.decode("utf-8", "replace")


def _norm(t):
    return re.sub(r"\s+", " ", t)


def resolve(d, text, cache):
    """Placeholders -> justified numbers. (text with live markers, {placeholder: shown})."""
    seen = {}

    def rep(m):
        kind, arg, key = m.group(1), m.group(2).strip(), m.group(0)
        if kind == "fig":
            name, _, spec = arg.partition("|")
            v, fmt = _figure(d, name.strip(), cache)
            s = ("{:" + spec + "}").format(v) if spec else fmt.format(v)
        elif kind.startswith("calc"):
            expr, _, spec = arg.partition("|")
            v = _calc(d, expr.strip(), cache)
            if "@" in kind:
                try:
                    v = live.step(kind.partition("@")[2], v)
                except live.Unjustified as e:
                    raise Refused(f"{key}: {e}")
            s = ("{:" + (spec or "g") + "}").format(v)
        elif kind == "count":
            sid, _, term = arg.partition(":")
            n = len(re.findall(re.escape(term), pin_text(d, sid), re.I))
            s = live.reading(sid, "count", term, n, f"{n:,}", _meta(d, sid))
        elif kind == "read":
            sid, _, rest = arg.partition(":")
            shown, _, phrase = rest.partition("|")
            # an HTML pin: a phrase may run across a tag, so real tags are set aside -
            # only real ones: a plain-text pin may hold a literal "<" (SR353 does)
            tag = r"</?[A-Za-z][A-Za-z0-9:-]*(?:\s[^<>]*)?/?>"
            pinned = _norm(re.sub(tag, " ", pin_text(d, sid)))
            if not phrase or _norm(re.sub(tag, " ", phrase)) not in pinned:
                raise Refused(f"{key}: the pinned text of {sid} does not contain "
                              f"'{phrase}', so this reading is unsupported")
            # and the number shown must be one the document states - compared as a
            # number, whatever the separators: Danish "50.000" is English "50,000"
            num = lambda t: re.sub(r"\D", "", t)      # digits only: "1%" states 1
            # each whitespace-separated number is a candidate - a table row "158 93,9
            # 21,3" is three cells, not one number - and so is a short run of them,
            # because Danish may group thousands with a space ("58 367")
            toks = re.findall(r"\d[\d.,]*\d|\d", phrase)
            cands = {num(t) for t in toks}
            cands |= {num("".join(toks[i:i + k])) for k in (2, 3) for i in range(len(toks) - k + 1)}
            if num(shown) not in cands:
                raise Refused(f"{key}: '{shown}' is not a number the quoted phrase "
                              f"'{phrase}' states - the reading would print a number the "
                              "document does not")
            s = live.reading(sid, "phrase", phrase, shown, shown, _meta(d, sid))
        elif kind == "was":
            parts = arg.split(":", 2)
            if len(parts) != 3:
                raise Refused(f"{key}: expected {{was:COMMIT:FILE:TEXT}}")
            commit, file, shown = parts
            try:
                if live.SLOT in shown:          # a located reference: nothing typed
                    s = live.was(commit, file, shown)
                else:
                    if shown not in _git_show(commit, file):
                        raise Refused(f"{key}: {file} at {commit} does not contain "
                                      f"'{shown}' - a misquotation")
                    s = live.quoted(commit, file, shown)
            except live.Unjustified as e:
                raise Refused(f"{key}: {e}")
        elif kind in ("ref", "chem"):
            import chem
            import refs
            i, _, form = arg.partition("|")
            opts = [o.strip() for o in form.split(",") if o.strip()]
            try:
                s = refs.mark(i.strip(), "title" in opts,
                              next((o for o in opts if o != "title"), None)) if kind == "ref" \
                    else chem.mark(i.strip())
            except live.Unjustified as e:
                raise Refused(f"{key}: {e}")
        else:
            p = d.get("params", {}).get(arg)
            if p is None:
                raise Refused(f"{key}: no such parameter in claims.json")
            s = live.stated(arg, p["value"], p["shown"], p["reason"])
        seen[key] = live.strip_marks(s)
        if kind == "ref":           # a reference is stale when its target's title moves
            import refs
            seen[key] = f"{arg.partition('|')[0].strip()}: " \
                        f"{refs.registry()[arg.partition('|')[0].strip()]['title']}"
        at = _placeholder_line(key)
        if at:
            live.set_where(s, *at)
        return s
    return PH.sub(rep, text), seen


_SRC_LINES = {}


def _placeholder_line(key):
    """(file, line) a placeholder was written on, across the register and its
    fragments - for the code view."""
    for f in fragments(SRC):
        if f not in _SRC_LINES:
            _SRC_LINES[f] = open(f, encoding="utf-8").read().split("\n")
        for n, line in enumerate(_SRC_LINES[f], 1):
            if key in line:
                return os.path.relpath(f, ROOT), n
    return None


def plain(d, text, cache):
    import chem
    import refs
    return chem.strip(refs.strip(live.strip_marks(resolve(d, text, cache)[0])))


# ---------------------------------------------------------------- staleness ---
def _texts(c, nodes):
    """Every text rendered in a claim's section - what a confirmation covers."""
    t = {"claim": c["claim"], "note": c.get("note", ""),
         "because": c.get("because", ""), "holder": c.get("holder", "")}
    for k, v in (c.get("assessment") or {}).items():
        t["assessment." + k] = v
    for r in c["rests_on"]:
        n = nodes.get(r)
        if n:
            t[r + ".label"] = n.get("label", "")
            t[r + ".detail"] = n.get("detail", "")
    return t


def observe(d, c, nodes, cache):
    saw = {}
    texts = _texts(c, nodes)
    for field, text in texts.items():
        for k, v in resolve(d, text, cache)[1].items():
            saw[f"{field} {k}"] = v
    for sid in set(re.findall(r"\{(?:count|read):([^:{}]+):", " ".join(texts.values()))):
        s = d["sources"][sid]
        saw[f"pinned {sid}"] = s["sha256"][:16] + (
            " CHANGED" if "CHANGED" in (s.get("status") or "") else "")
    # the words, not only the numbers in them: the sentence on each page that says
    # the claim, the claim's own texts, and what each thing it rests on says
    for page, said in _said_on(c["id"]).items():
        saw[f"said on {page}"] = said
    # a hypothesis, observable or outcome the claim names: it leans on that entry, so
    # it goes stale when the entry's content changes (its data needs excepted)
    for i in sorted(_refs_named(c)):
        saw[f"hypothesis {i}"] = _ref_digest(i)
    saw["texts"] = _digest({k: c.get(k) for k in OWN})
    allc = {x["id"]: x for x in d.get("claims", [])}
    for r in c["rests_on"]:
        if r in allc:
            saw[f"rests on {r}"] = _digest({k: allc[r].get(k) for k in OWN})
        elif r in nodes:
            n = nodes[r]
            saw[f"node {r}"] = _digest(n)
            s = d.get("sources", {}).get(n.get("source") or "")
            if s:
                saw[f"pinned {n['source']}"] = s["sha256"][:16] + (
                    " CHANGED" if "CHANGED" in (s.get("status") or "") else "")
    return saw


OWN = ("claim", "because", "holder", "stance", "kind", "rests_on", "note",
       "assessment", "page", "said_on")
# Observed only since 2026-09-11. A confirmation made before recorded none of these,
# so their absence there means "not observed then", not "changed since".
_LATER = re.compile(r"texts$|rests on |node |hypothesis ")
_HYP = {}


def _refs_named(c):
    """Register IDs a claim names: {ref:} in its own texts, and checked references in
    the wording a page says it in (an ID set as code is a name, not a reference)."""
    import refs
    reg = refs.registry()
    texts = [c.get(k) or "" for k in ("claim", "because", "note", "holder")]
    texts += [v for v in (c.get("assessment") or {}).values() if isinstance(v, str)]
    out = {m.split("|")[0].strip() for t in texts for m in re.findall(r"\{ref:([^{}]+)\}", t)}
    for said in _said_on(c["id"]).values():
        out |= {m.group(1) for m in refs.TOKEN.finditer(said)
                if m.group(1) in reg and said[max(0, m.start() - 1):m.start()] != "`"}
    return out


def _ref_digest(i):
    """What a claim leans on in a register entry: everything but its data needs."""
    if "d" not in _HYP:
        _HYP["d"] = read_json(os.path.join(ROOT, "data", "derived", "hypotheses.json"))
    found = [{k: v for k, v in e.items() if k != "needs"}
             for fam in _HYP["d"].values() if isinstance(fam, list)
             for e in fam if isinstance(e, dict) and e.get("id") == i]
    return _digest(found) if found else "missing"


def _digest(x):
    return hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False)
                          .encode()).hexdigest()[:16]


def _spans():
    try:
        return json.load(open(live.SPANS, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _said_on(cid):
    """{page: the words} for every page that says this claim, as last written."""
    return {page: said[cid] for page, said in _spans().items() if cid in said}


def _pages(c):
    return [p for p in [c.get("page")] + list(c.get("said_on", [])) if p]


def staleness(d, nodes, claims, cache):
    out = []
    for cid, c in claims.items():
        try:
            now = observe(d, c, nodes, cache)
        except Refused as e:
            out.append(f"{cid}: {e}")
            continue
        conf = c.get("confirmed")
        if not conf:
            out.append(f"{cid}: never confirmed. Read it, then: "
                       f"claims.py --reassess {cid} --by <name>")
            continue
        was = conf.get("saw", {})
        diff = sorted(k for k in set(was) | set(now) if was.get(k) != now.get(k)
                      and not (k not in was and _LATER.match(k)))
        if diff:
            ex = "; ".join(f"{k}: {was.get(k)} -> {now.get(k)}" for k in diff[:3])
            out.append(f"{cid}: STALE since it was confirmed {conf.get('on')} - "
                       f"{ex}. Read it again, then --reassess {cid}")
    return out


def synthetic_on_findings(d, nodes, claims, cache):
    """A claim resting on a simulated number may stand only on a method page -
    including every page it appears_in, and the nodes it hangs from."""
    import constructions
    out = []
    for cid, c in claims.items():
        pages = [p for p in [c.get("page")] + list(c.get("appears_in", [])) if p]
        wrong = [p for p in pages if not constructions.synthetic_allowed(p)]
        if not wrong:
            continue
        for field, text in _texts(c, nodes).items():
            for fid, shown in live.MARK.findall(resolve(d, text, cache)[0]):
                if constructions.describe(live._seen[fid]["src"])["synthetic"]:
                    out.append(f"{cid}: '{shown}' in {field} is built on simulation, "
                               f"and the claim stands on {', '.join(wrong)} - not a "
                               "method page")
    return out


def reassess(d, c, nodes, by):
    c["confirmed"] = {"on": datetime.date.today().isoformat(), "by": by,
                      "saw": observe(d, c, nodes, {})}


# --------------------------------------------------------------- validation ---
def dig(obj, path):
    for k in (path if isinstance(path, list) else path.split(".")):
        if isinstance(obj, list):
            try:
                obj = obj[int(k)]
                continue
            except (ValueError, IndexError):
                return None
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def check_figures(d, claims, cache):
    """value_from/appears_in: the live value must appear wherever it is stated,
    including index.html, which nothing generates and so only this can reach."""
    bad = []
    for cid, c in claims.items():
        v = c.get("value_from")
        if not v:
            continue
        f = os.path.join(ROOT, v["file"])
        if not os.path.exists(f):
            if not v.get("optional"):
                bad.append(f"{cid}: {v['file']} does not exist")
            continue
        cur = dig(json.load(open(f, encoding="utf-8")), v["path"])
        if cur is None:
            bad.append(f"{cid}: {v['path']} not found in {v['file']}")
            continue
        shown = v.get("fmt", "{}").format(cur)
        if shown not in plain(d, c["claim"], cache):
            bad.append(f"{cid}: the claim does not show {shown}, the current value "
                       f"of {v['file']}:{v['path']}")
        for where in c.get("appears_in", []):
            wp = os.path.join(ROOT, where)
            if not os.path.exists(wp) or shown not in open(wp, encoding="utf-8").read():
                bad.append(f"{cid}: {where} does not contain {shown}, the current "
                           f"value of {v['file']}:{v['path']}")
    return bad


def _flat(t):
    """Text as compared for a phrase: tags set aside, entities read as the
    characters they stand for, whitespace collapsed."""
    import html
    t = html.unescape(re.sub(r"</?[A-Za-z][A-Za-z0-9:-]*(?:\s[^<>]*)?/?>", " ", t))
    return re.sub(r"\s+", " ", t).strip()


def node_problems(d, n):
    nid, kind = n["id"], n.get("kind")
    if kind not in TERMINAL:
        return [f"{nid}: kind '{kind}' is not one a chain can end in - one of "
                f"{', '.join(sorted(TERMINAL))}"]
    said = n.get("said")
    if said and re.search(r"\d", said):
        return [f"{nid}: 'said' locates a passage and is shown verbatim, so it holds no "
                "digits - a number quoted from it goes through {read:} or {was:}"]
    if kind == "history":
        if not (n.get("commit") and n.get("file") and said):
            return [f"{nid}: a history node names a commit, a file and what it said there"]
        text = live._git_text(n["commit"], n["file"])
        if text is None:
            return [f"{nid}: {n['file']} does not exist at {n['commit']}"]
        if _flat(said) not in _flat(text):
            return [f"{nid}: {n['file']} at {n['commit']} does not say '{said}'"]
    if kind == "untraced" and not n.get("detail"):
        return [f"{nid}: an untraced node says what was searched, where and when - "
                "the end of a trail is a finding too"]
    if n.get("source"):
        sid = n["source"]
        if sid not in d.get("sources", {}):
            return [f"{nid}: no pinned source {sid}"]
        if said:
            try:
                pinned = pin_text(d, sid)
            except Refused as e:
                return [f"{nid}: {e}"]
            if _flat(said) not in _flat(pinned):
                return [f"{nid}: the pinned text of {sid} does not contain '{said}'"]
    return []


def structure(d, nodes, claims, allc=None):
    """What a claim must have besides a current confirmation: something it rests
    on, the argument if it is argued, and - if it is somebody else's - whose it is
    and where their document is, or where the trail ran out."""
    allc = allc or claims
    bad = []
    for cid, c in claims.items():
        rs = c.get("rests_on") or []
        for r in rs:
            if r not in nodes and r not in allc:
                bad.append(f"{cid} rests on {r}, which is not defined")
        if c.get("kind") == "argued" and not c.get("because"):
            bad.append(f"{cid}: an argued claim needs 'because' - the argument itself")
        if c.get("retired"):
            bad += _retired_problems(cid, c, allc)
        for o in c.get("replaces", []):
            if o not in allc or not allc[o].get("retired"):
                bad.append(f"{cid} replaces {o}, which is not a retired claim")
        # an argument, or a rule this project sets itself, may stand on its reasoning alone
        if not rs and not c.get("retired") and not (c.get("kind") in ("argued", "stipulated")
                                                     and c.get("because")):
            bad.append(f"{cid}: rests on nothing. Name what it rests on - or, if nothing "
                       "could be found, an untraced node saying what was searched")
        stance = c.get("stance", "ours")
        if stance not in ("ours", "theirs"):
            bad.append(f"{cid}: stance is 'ours' or 'theirs', not '{stance}'")
        if stance == "theirs":
            if not c.get("holder"):
                bad.append(f"{cid}: somebody else's claim needs 'holder' - whose it is")
            if not any(r in nodes and (nodes[r].get("kind") == "untraced"
                                       or nodes[r].get("source")) for r in rs):
                bad.append(f"{cid}: somebody else's claim rests on their document - a "
                           "node with a pinned source and what they said there - or on an "
                           "untraced node saying where the trail ran out")
    for nid in sorted({r for c in claims.values() for r in c.get("rests_on", []) if r in nodes}):
        bad += node_problems(d, nodes[nid])
    return bad


def _retired_problems(cid, c, allc):
    """A retired claim: what the site once published, where, and why it is no longer
    claimed. The passage must still be found at that commit."""
    r, bad = c["retired"], []
    if c.get("kind") != "historical" or c.get("page") != "ARCHIVE.md":
        bad.append(f"{cid}: a retired claim is historical and lives on ARCHIVE.md")
    miss = [k for k in ("on", "from", "commit", "file", "begin", "end", "why") if not r.get(k)]
    if miss:
        return bad + [f"{cid}: 'retired' needs {', '.join(miss)}"]
    for k in ("begin", "end"):
        if re.search(r"\d", r[k]):
            bad.append(f"{cid}: retired.{k} locates a passage, so it holds no digits")
    try:
        live.excerpt(r["commit"], r["file"], r["begin"], r["end"])
    except live.Unjustified as e:
        bad.append(f"{cid}: {e}")
    for x in c.get("replaced_by", []):
        if x not in allc:
            bad.append(f"{cid}: replaced by {x}, which is not defined")
    return bad


def homes(cids):
    """Where each claim is explained: CLAIMS.md, or ARCHIVE.md once retired."""
    claims = load()[2]
    return {c: "ARCHIVE.md" if (claims.get(c) or {}).get("retired") else "CLAIMS.md"
            for c in cids}


def said_problems(rel, found):
    """For write_doc(): each claim a page marks must be registered for that page,
    and it and everything under it, all the way down, sound and current."""
    page = rel[len("docs/"):] if rel.startswith("docs/") else rel
    d, nodes, claims = load()
    bad, todo = [], []
    for cid in found:
        c = claims.get(cid)
        if not c:
            bad.append(f"{cid}: not in the claims register")
        elif page not in _pages(c):
            bad.append(f"{cid}: registered for {c.get('page')}, not {page}")
        else:
            todo.append(cid)
    chain = set()
    while todo:
        cid = todo.pop()
        if cid not in chain:
            chain.add(cid)
            todo += [r for r in claims[cid].get("rests_on", []) if r in claims]
    sub = {k: claims[k] for k in sorted(chain)}
    return bad + structure(d, nodes, sub, claims) + staleness(d, nodes, sub, {})


def validate(d, nodes, claims, cache):
    bad = structure(d, nodes, claims)
    for page, said in _spans().items():
        for cid in said:
            if cid not in claims:
                bad.append(f"{page} says {cid}, which the register no longer holds - "
                           "rebuild the page, or restore the claim")
    WHITE, GREY, BLACK = 0, 1, 2
    colour = {cid: WHITE for cid in claims}

    def walk(cid, path):
        colour[cid] = GREY
        for r in claims[cid]["rests_on"]:
            if r not in claims:
                continue
            if colour[r] == GREY:
                bad.append("CIRCULAR: " + " -> ".join(path + [cid, r]))
            elif colour[r] == WHITE:
                walk(r, path + [cid])
        colour[cid] = BLACK
    for cid in claims:
        if colour[cid] == WHITE:
            walk(cid, [])
    bad += check_figures(d, claims, cache)
    bad += staleness(d, nodes, claims, cache)
    return bad


# ------------------------------------------------------------------ the page ---
def _node_line(nid, kind, label):
    o, c = SHAPE.get(kind, SHAPE["claim"])
    label = label.replace("\\n", " · ").replace("\n", " · ").replace('"', "'")
    return f"  {nid}{o}{label}{c}"


def graph_for(cid, nodes, claims, lab, depth=2):
    seen, edges = {}, []

    def add(nid, dd):
        if nid in seen or dd < 0:
            return
        n = nodes.get(nid) or claims.get(nid)
        if not n:
            return
        seen[nid] = n.get("kind", "claim") if nid in nodes else "claim"
        for r in (claims.get(nid, {}).get("rests_on") or []):
            edges.append((r, nid))
            add(r, dd - 1)
    add(cid, depth)
    out = ["```mermaid", "graph BT"]
    for nid, kind in seen.items():
        out.append(_node_line(nid, kind, lab(nid)))
    for a, b in dict.fromkeys(edges):
        if a in seen and b in seen:
            out.append(f"  {a} --> {b}")
    for nid, kind in seen.items():
        out.append(f"  style {nid} {STYLE.get(kind, STYLE['claim'])}")
    out.append("```")
    return "\n".join(out)


def _node_item(d, n, cache):
    kind = n.get("kind")
    label = resolve(d, n.get("label", n["id"]), cache)[0].replace("\\n", " ")
    detail = resolve(d, n.get("detail", ""), cache)[0]
    if kind == "history":
        s = (f"- **history** — {label}: `{n['file']}` at `{n['commit'][:7]}` "
             f"says “{n['said']}”")
    elif kind == "untraced":
        s = f"- **trail ends here** — {label}"
    elif n.get("source"):
        src = d["sources"][n["source"]]
        s = (f"- **{kind}** — {label}" + (f": “{n['said']}”" if n.get("said") else "")
             + f" ([`{n['source']}`]({src['url']}), pinned)")
    else:
        s = f"- **{kind}** — {label}"
    return s + (f". {detail}" if detail else "")


def justification(d, cid, c, cache):
    out = []
    if c.get("basis") == "computed":
        provs = []
        for name, r in d.get("figures", {}).items():
            if r.get("claim") != cid:
                continue
            full = os.path.join(ROOT, r["file"])
            if not os.path.exists(full):
                continue
            if r["file"] not in cache:
                cache[r["file"]] = live.live_json(full)
            prov = cache[r["file"]].get("_provenance") or {}
            p = prov.get(".".join(_path(r)))
            if p:
                provs.append((name, r, p))
        out.append("**Computed** — the chain is what was coded, and the script that "
                   "computes it records how it counted.")
        if not provs:
            out += ["", "*The script behind this does not yet record how it counted "
                    "it. That is a gap in the justification, not a property of the "
                    "number.*"]
        for name, r, p in provs:
            out += ["", f"**`{name}`** — `{r['file']}` → `{'.'.join(_path(r))}`", ""]
            out.append(f"- **Counted as the same thing:** {p['counts_as']}")
            out.append(f"- **Calculation:** {p['calculation']}")
            if p.get("n_in") is not None and p.get("n_used") is not None:
                out.append(f"- **Rows:** {p['n_in']:,} in, {p['n_used']:,} used")
            for e in p.get("excluded") or []:
                out.append(f"- **Excluded:** {e['reason']} ({e['n']:,})")
            if p.get("alternatives"):
                out.append("- **Other defensible definitions, and what each gives:** "
                           + "; ".join(f"{a['definition']} → {a['value']:g}"
                                       for a in p["alternatives"]))
            src = p["code"].split(":")[0]
            out.append(f"- **Code:** [`{p['code']}`](../{src})")
    else:
        a = c.get("assessment")
        out.append("**Assessed** — no script computes this. It is a reading or a "
                   "judgement, assessed by a person.")
        if not a and not c.get("because"):
            out += ["", "*Assessment not yet written.*"]
        elif a:
            out.append("")
            for k, labl in (("counts_as", "What it counts"),
                            ("reasoning", "Why it is believed"),
                            ("confidence", "How confident"),
                            ("would_change", "What would change it")):
                if a.get(k):
                    out.append(f"- **{labl}:** {resolve(d, a[k], cache)[0]}")
    conf = c.get("confirmed") or {}
    # the by-line is a record of who read what, shown verbatim - as code, so a count
    # or an identifier in it is not taken for a claim about the world
    by = (conf.get("by") or "nobody").replace("`", "'")
    out += ["", f"*Confirmed {conf.get('on', 'never')} by* `{by}`. *If anything shown here "
            "changes, this claim is refused until it is read again.*"]
    return out


def main(argv):
    d, nodes, claims = load()
    if "--recheck" in argv:
        recheck(d)
        return 0
    if "--repin" in argv:
        try:
            repin(d, argv[argv.index("--repin") + 1])
        except Refused as e:
            log("  " + str(e))
            return 1
        return 0
    if "--reassess" in argv:
        target = argv[argv.index("--reassess") + 1]
        by = argv[argv.index("--by") + 1] if "--by" in argv else None
        if not by:
            log("  --reassess needs --by <name>: a confirmation is somebody's")
            return 2
        ids = list(claims) if target == "all" else [target]
        for i in ids:
            try:
                reassess(d, claims[i], nodes, by)
            except Refused as e:
                log(f"  {i}: {e}")
                return 1
        save(d, {_ORIGIN.get(("claims", i), SRC) for i in ids})
        log(f"  confirmed {len(ids)} claim(s) as of today, by {by}")
        return 0

    cache = {}
    bad = validate(d, nodes, claims, cache)
    bad += synthetic_on_findings(d, nodes, claims, cache)
    for b in bad:
        log("  " + b)
    if bad:
        log(f"\n  {len(bad)} problem(s) - refusing to write the page")
        return 1
    log(f"  {len(nodes)} nodes, {len(claims)} claims: no cycles, every one "
        "confirmed and current")
    if "--check" in argv:
        return 0

    def lab(nid):
        if nid in nodes:
            return plain(d, nodes[nid].get("label", nid), cache)
        return plain(d, claims[nid]["claim"], cache)[:58] + "..."

    o = []
    w = o.append
    w("# What each claim rests on")
    w("")
    w("*Generated by `scripts/claims.py` from `data/manual/claims.json`. No number on "
      "this page is typed: every one is resolved from data, a pinned document, a "
      "past commit or a stated parameter, and links to where it came from. Each "
      "claim also records what it saw when it was last confirmed, and the page is "
      "refused if anything has changed since.*")
    w("")
    w("Prose hides dependency. *The surface diurnal amplitude is below half a "
      "milligram* reads like a measurement. It is a bound, derived from a synthetic "
      "recovery run on a real sampling schedule, under a stipulated signal shape and "
      "a noise model — four kinds of thing, one of which is not data at all. The "
      "sentence cannot show you that. A graph can.")
    w("")
    w("### How to read the shapes")
    w("")
    w("| shape | kind | what it means for the claim above it |")
    w("|---|---|---|")
    w("| cylinder, blue | **held** | a dataset on disk, with whatever faults "
      "[DATA_SOURCES.md](DATA_SOURCES.md) records |")
    w("| cylinder, purple | **external** | somebody else's published document, "
      "pinned by its hash |")
    w("| hexagon, red dashed | **gap** | data that exists and we cannot reach, or that "
      "nobody has measured |")
    w("| flag, amber | **synthetic** | generated to test the method. Licenses claims "
      "about the *instrument*, never about the world |")
    w("| rhombus, amber dashed | **assumption** | stipulated rather than measured. "
      "**The claim is void if it is wrong** |")
    w("| box, grey | **script** | the code that does the work |")
    w("| rounded, green | **claim** | a statement on a page, which may rest on other "
      "claims |")
    w("| slanted, slate | **history** | what this project itself did or said at a past "
      "commit, checked against its history |")
    w("| circle, red dotted | **untraced** | where the trail ends: what was searched and "
      "not found. Nothing below it is claimed |")
    w("")
    w("A claim is either this project's own or somebody else's. Ours says why it "
      "follows from what it rests on. Somebody else's is credited to whoever holds it "
      "and shows only what could be found behind it - their document, pinned, and "
      "the reasons they give - and where the trail ran out, it says so. Every path "
      "down from a claim ends in one of the kinds above; the build refuses one that "
      "does not.")
    w("")
    w("---")
    w("")
    by_page = {}
    for cid, c in claims.items():
        if not c.get("retired"):
            by_page.setdefault(c.get("page", "—"), []).append((cid, c))
    for page in sorted(by_page):
        w(f"## {page}")
        w("")
        for cid, c in by_page[page]:
            w(f'<a id="{cid}"></a>')
            w(f"### {resolve(d, c['claim'], cache)[0]}")
            w("")
            w(f"`{cid}` · **{c['kind']}** — {KIND_NOTE.get(c['kind'], '')}")
            w("")
            if c.get("stance") == "theirs":
                w(f"**Somebody else's claim** — held by {resolve(d, c['holder'], cache)[0]}. "
                  "What follows is what could be found behind it, and no more.")
                w("")
            said = _said_on(cid)
            if said:
                w("Said on " + ", ".join(f"[{p}]({p})" for p in sorted(said)) + ".")
                w("")
            if c.get("because"):
                lead = ("Their reasons, as far as they could be found"
                        if c.get("stance") == "theirs" else "Why it follows")
                w(f"**{lead}:** {resolve(d, c['because'], cache)[0]}")
                w("")
            for old in c.get("replaces", []):
                r = claims[old]["retired"]
                w(f"**Replaces an earlier claim**, retired on {r['on']} to the "
                  f"[archive](ARCHIVE.md#{old}): {resolve(d, r['why'], cache)[0]}")
                w("")
            if c["rests_on"]:
                w(graph_for(cid, nodes, claims, lab, depth=4))
                w("")
            for r in c["rests_on"]:
                n = nodes.get(r)
                if n:
                    w(_node_item(d, n, cache))
                elif r in claims:
                    w(f"- **claim** — {resolve(d, claims[r]['claim'], cache)[0]} "
                      f"([`{r}`](CLAIMS.md#{r}))")
            if not c["rests_on"]:
                w("- **the argument alone** — nothing further is cited: the reasoning "
                  "above is the whole of it, for the reader to judge")
            w("")
            for line in justification(d, cid, c, cache):
                w(line)
            if c.get("note"):
                w("")
                w(f"> {resolve(d, c['note'], cache)[0]}")
            w("")
    w("---")
    w("")
    w("## What is missing from this register")
    w("")
    w("It covers the claims this project has examined, not every sentence it has "
      "written. A claim absent from here is not endorsed by its absence — it simply "
      "has not been put through this yet.")
    try:
        write_doc(OUT, "\n".join(o).rstrip("\n") + "\n")
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return write_archive(d, claims, cache)


def write_archive(d, claims, cache):
    """ARCHIVE.md: every claim the site no longer makes, in the words it was
    published in, with why it was retired and what, if anything, replaced it."""
    o = []
    w = o.append
    w("# Retired claims")
    w("")
    w("*Generated by `scripts/claims.py` from the claims register. Each passage below "
      "is read out of this repository's history at the commit named, so it is what "
      "the site actually published, not a paraphrase.*")
    w("")
    w("A claim is retired when no good justification for it can be given - most often "
      "because its justification was never recorded properly. It is not quietly "
      "deleted: it is kept here, in its own words, with the reason, and the page that "
      "made it now says only what can be justified. Nothing on this page is claimed "
      "to be true. What is claimed is that the site once said it.")
    w("")
    retired = sorted(((cid, c) for cid, c in claims.items() if c.get("retired")),
                     key=lambda x: (x[1]["retired"]["from"], x[0]))
    if not retired:
        w("*Nothing has been retired yet.*")
    by_page = {}
    for cid, c in retired:
        by_page.setdefault(c["retired"]["from"], []).append((cid, c))
    for page in by_page:
        w(f"## {page}")
        w("")
        for cid, c in by_page[page]:
            r = c["retired"]
            w(f'<a id="{cid}"></a>')
            w(f"### {resolve(d, c['claim'], cache)[0]}")
            w("")
            w(f"`{cid}` · retired {r['on']} from [{r['from']}]({r['from']}) · as "
              f"published in `{r['commit'][:7]}`")
            w("")
            w("> " + live.claim(cid, live.excerpt(r["commit"], r["file"], r["begin"], r["end"])))
            w("")
            w(f"**Why it was retired:** {resolve(d, r['why'], cache)[0]}")
            w("")
            if c.get("replaced_by"):
                # by id: a replacement's own numbers belong on its own page (a
                # simulated one only on a method page), not restated here
                w("**Replaced by:** " + ", ".join(
                    f"[`{x}`](CLAIMS.md#{x})" for x in c["replaced_by"])
                  + " — each opens what it rests on.")
            else:
                w("**Not replaced** — nothing that could be justified was found to say "
                  "in its place.")
            w("")
    try:
        write_doc(ARCHIVE, "\n".join(o).rstrip("\n") + "\n")
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(ARCHIVE, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
