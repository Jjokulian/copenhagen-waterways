#!/usr/bin/env python3
"""What kind of number is this, and why should the way it was made be believed?

live.py answers *where a number came from*: the field, the file, the arithmetic.
That is lineage, and lineage is not warrant. A number read faithfully out of a
simulation is still a simulated number; a share whose part was counted under a
different rule from its whole is still wrong however well it is linked. This
module holds the other half - the construction - declared in
data/manual/number_constructions.json:

  - every field a page prints is covered by a declaration that names its KIND
    and, for a count or a share, what was counted as one;
  - every declaration says what the producing code computes, the model it
    rests on, why that model is justified, the gaps nothing justifies, when the
    numbers would be void, and what they may and may not be used to claim;
  - a calculation that is itself a model - reading a bound off between two
    runs, a share of a subset - is wrapped with live.step() and has its own
    declaration, so it is not passed off as plain arithmetic.

Two refusals, at compile time and again in the pre-commit hook:

  1. a number with any part of its construction undeclared is refused, exactly
     as a number with no source is;
  2. a number built on simulation is refused on any page that is not a method
     page - the METHOD_LAB separation as a compiler rule rather than a habit.

A declaration is assessed prose, so it goes stale the way a claim does: it
records the hash of every file it watches when somebody confirms it, and a
change in any of them makes it STALE until it is read again.

    constructions.py --check                    staleness, confirmations, prose
    constructions.py --uncovered                fields in use with no declaration
    constructions.py --reassess K-ID|all --by NAME
"""
import datetime
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT, fragments, log
import live

REG = os.path.join(ROOT, "data", "manual", "number_constructions.json")

KINDS = {
    "measured": "an instrument or map reading, as recorded",
    "counted": "a number of things, under a stated rule of what counts as one",
    "estimated": "a statistic computed from measurements; it has sampling error",
    "computed": "a deterministic consequence of stated inputs; no sampling error",
    "share": "a part of something as a fraction of the whole",
    "simulated": "produced by a simulation; it can speak about the method, not the world",
    "stipulated": "chosen, not measured",
    "bound": "an inferred limit, not a value",
    "modelled": "the output of somebody's model of the world, not an observation of it",
    "document": "stated in a pinned external document",
    "quoted": "what this site said at an earlier commit",
    "calculated": "arithmetic on other numbers, each with a kind of its own",
}
# The digit check cannot see a quantity written in words, and in a declaration
# that is where one hides - "roughly a quarter of the herd". A count that
# describes the code ("the two layers", "a twelve-month filing") is checkable
# against the reference beside it; an approximate size of the DATA is an estimate
# that no script computed. So what is refused is the approximated quantity.
# "One" is left out: "more than one clock time" is a rule, not an estimate.
_NUMWORD = (r"(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|twenty|"
            r"thirty|forty|fifty|sixty|seventy|eighty|ninety|hundreds?|thousands?|"
            r"millions?|billions?|half|a\s+half|a\s+quarter|quarters?|a\s+third|thirds?|"
            r"a\s+tenth|tenths?|a\s+hundredth|hundredths?|a\s+thousandth|dozens?|"
            r"twice|thrice|double|triple|\w+fold)")
_WORDNUM = re.compile(r"\b(?:roughly|about|around|nearly|almost|approximately|some|"
                      r"close\s+to|well\s+(?:under|over|below|above)|more\s+than|"
                      r"fewer\s+than|less\s+than|over|under|up\s+to)\s+" + _NUMWORD
                      + r"\b|\b(?:a\s+)?handful\b|\bthe\s+majority\b", re.I)
PROSE = ("title", "what", "model", "assumptions", "justified", "gaps", "void_if",
         "licenses", "not_licensed")
_cache = {}


_ORIGIN = {}      # construction id -> the file it came from


def load():
    """The register and its fragments in number_constructions.d/, merged.
    Parallel workers each declare their constructions in a fragment of their own."""
    if "reg" not in _cache:
        reg = (json.load(open(REG, encoding="utf-8"))
               if os.path.exists(REG) else {"constructions": []})
        _ORIGIN.clear()
        for c in reg["constructions"]:
            _ORIGIN[c["id"]] = REG
        for f in fragments(REG)[1:]:
            for c in json.load(open(f, encoding="utf-8")).get("constructions", []):
                reg["constructions"].append(c)
                _ORIGIN.setdefault(c["id"], f)
        _cache["reg"] = reg
    return _cache["reg"]


def save(reg, files=None):
    """Write declarations back to the file each came from - only `files`, when
    given, so a worker confirming its own declaration never rewrites a file
    somebody else has edited since it was read."""
    for f in fragments(REG):
        if files is not None and f not in files:
            continue
        raw = json.load(open(f, encoding="utf-8"))
        raw["constructions"] = [c for c in reg["constructions"] if _ORIGIN.get(c["id"], REG) == f]
        # atomic: many workers read these files while others write them
        tmp = f"{f}.{os.getpid()}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(raw, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        os.replace(tmp, f)
    _cache.pop("reg", None)


def by_id(cid):
    return next((c for c in load()["constructions"] if c["id"] == cid), None)


def _matches(pattern, path):
    a, b = live._split(pattern), live._split(path)
    return len(a) == len(b) and all(x == "*" or x == y for x, y in zip(a, b))


def cover(file, path):
    """The declaration and field spec covering one field, or (None, None)."""
    for c in load()["constructions"]:
        cv = c.get("covers") or {}
        if cv.get("file") != file:
            continue
        for pat, spec in (cv.get("fields") or {}).items():
            if _matches(pat, path):
                return c, spec
    return None, None


def _node_construction(key):
    return next((c for c in load()["constructions"]
                 if (c.get("covers") or {}).get("node") == key), None)


def describe(node):
    """Kind, whether simulation is anywhere beneath it, the constructions it
    rests on (its own step first), and anything left undeclared."""
    out = {"kind": None, "synthetic": False, "constructions": [], "uncovered": [],
           "rests_on": {}}

    def rest(kind, synthetic):
        out["rests_on"][kind] = out["rests_on"].get(kind, 0) + 1
        out["synthetic"] = out["synthetic"] or synthetic

    def use(cid):
        if cid not in out["constructions"]:
            out["constructions"].append(cid)

    def walk(n, top):
        t = n[0]
        if t == "const":
            return
        if t == "leaf":
            c, spec = cover(n[1], n[2])
            if not c:
                out["uncovered"].append(f"{n[1]} › {n[2]}")
                return
            use(c["id"])
            synthetic = spec.get("synthetic", spec["kind"] == "simulated")
            rest(spec["kind"], synthetic)
            if top:
                out["kind"] = spec["kind"]
                out["field"] = {"kind": spec["kind"], "is": spec.get("is"),
                                "synthetic": synthetic}
            return
        if t in ("reading", "quote", "stated"):
            key = {"reading": f"reading-{n[2]}", "quote": "quote", "stated": "stated"}[t]
            c = _node_construction(key)
            if not c:
                out["uncovered"].append(f"a {key} (no declaration covers this kind)")
                return
            use(c["id"])
            rest(c["produces"], False)
            if top:
                out["kind"] = c["produces"]
            return
        if t == "step":
            c = by_id(n[1])
            if not c or not (c.get("covers") or {}).get("step"):
                out["uncovered"].append(f"step {n[1]} (not declared as a step)")
            else:
                use(c["id"])
                if top:
                    out["kind"] = c["produces"]
            for k in n[2]:
                walk(k, False)
            return
        if top:
            out["kind"] = "calculated"
        if t == "agg":
            for key in n[2]:
                file, _, path = key.partition(" › ")
                c, spec = cover(file, path)
                if not c:
                    out["uncovered"].append(key)
                else:
                    use(c["id"])
                    rest(spec["kind"], spec.get("synthetic", spec["kind"] == "simulated"))
            for k in n[3]:
                walk(k, False)
            return
        for k in n[2]:
            walk(k, False)

    walk(node, True)
    return out


# ----------------------------------------------------------------- the pages ---
def _page(p):
    p = p.replace(os.sep, "/")
    return p if p.startswith("docs/") or p == "index.html" else "docs/" + p


def synthetic_allowed(rel):
    reg = load()
    return _page(rel) in set(reg.get("method_pages", [])) | set(reg.get("meta_pages", []))


def enforce(rel, srcs):
    """Problems with the numbers about to be written into `rel`: {id: src}."""
    problems, seen = [], set()
    for i, src in sorted(srcs.items()):
        d = describe(src)
        for u in d["uncovered"]:
            if u not in seen:
                seen.add(u)
                problems.append(f"  {i}: no construction declared for {u}")
        if d["synthetic"] and not synthetic_allowed(rel):
            problems.append(f"  {i}: built on simulation, and {rel} is not a method "
                            "page. A simulation speaks about the method, not the world.")
    return problems


# ---------------------------------------------------------------- staleness ---
_HASHES = os.path.join(ROOT, "data", "derived", ".construction_hashes.json")


def _file_sha(p):
    """Streamed, and remembered by size and mtime: a declaration may watch a raw
    extract of several hundred megabytes, and every build asks about it."""
    st = os.stat(p)
    if "hashes" not in _cache:
        try:
            _cache["hashes"] = json.load(open(_HASHES, encoding="utf-8"))
        except (OSError, ValueError):
            _cache["hashes"] = {}
    key, stamp = os.path.relpath(p, ROOT), [st.st_size, st.st_mtime_ns]
    got = _cache["hashes"].get(key)
    if got and got[:2] == stamp:
        return got[2]
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    _cache["hashes"][key] = stamp + [h.hexdigest()[:16]]
    os.makedirs(os.path.dirname(_HASHES), exist_ok=True)
    tmp = f"{_HASHES}.{os.getpid()}"          # atomic: many builds write this at once
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(_cache["hashes"], f, indent=0, sort_keys=True)
    os.replace(tmp, _HASHES)
    return _cache["hashes"][key][2]


def _sha(rel):
    """Hash of a watched file - or of one part of a JSON file, written
    file.json#key.sub, so that a declaration about the params is not made stale
    by every confirmation written elsewhere in the same file."""
    rel, _, part = rel.partition("#")
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return "missing"
    if not part:
        return _file_sha(p)
    raw = open(p, "rb").read()
    if part:
        try:
            obj = json.loads(raw)
            for k in part.split("."):
                obj = obj[k]
        except (ValueError, KeyError, TypeError):
            return "missing"
        raw = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def _expand(w):
    """A watch may name a glob - data/manual/claims.d/*.json#params - so that a
    fragment added later is watched without anyone remembering to add it."""
    path, sep, part = w.partition("#")
    if "*" not in path:
        return [w]
    import glob
    return [os.path.relpath(p, ROOT) + sep + part
            for p in sorted(glob.glob(os.path.join(ROOT, path)))
            if not part or _sha(os.path.relpath(p, ROOT) + sep + part) not in ("missing", _EMPTY)]


# the hash of an empty part ({}): a fragment that adds nothing to what is watched
# (a claims fragment with no params) is not a change to it
_EMPTY = hashlib.sha256(b"{}").hexdigest()[:16]


def observe(c):
    return {f: _sha(f) for w in c.get("watches", []) for f in _expand(w)}


def status(c):
    conf = c.get("confirmed")
    if not conf:
        return "unconfirmed"
    was, now = conf.get("saw", {}), observe(c)
    changed = sorted(f for f in set(was) | set(now) if was.get(f) != now.get(f))
    return "stale: " + ", ".join(changed) + " changed since it was read" if changed \
        else "current"


def reassess(c, by):
    c["confirmed"] = {"by": by, "on": datetime.date.today().isoformat(),
                      "saw": observe(c)}


def _texts(c):
    for k in PROSE:
        v = c.get(k)
        for t in (v if isinstance(v, list) else [v]):
            if isinstance(t, dict):
                t = t.get("text")
            if t:
                yield k, t
    for pat, spec in ((c.get("covers") or {}).get("fields") or {}).items():
        yield f"field {pat}", spec.get("is") or ""


def problems(c):
    """What is wrong with one declaration, apart from staleness."""
    out = []
    for where, t in _texts(c):
        # a formula's constants belong to its definition, as code's do: $...$ is
        # set aside like `...`, and both the reader and GitHub typeset it
        t = re.sub(r"\$[^$\n]+\$", "", t)
        bad = live.bare_numbers(t)
        if bad:
            out.append(f"{c['id']} {where}: a number in the prose ({bad[0][1]}) - name "
                       "the field in backticks instead")
        words = _WORDNUM.findall(re.sub(r"`[^`]*`", "", t))
        if words:
            out.append(f"{c['id']} {where}: a quantity in words ('{words[0]}') - it needs "
                       "a chain of justification like any number; name the field in "
                       "backticks, or say what is true without the quantity")
    for pat, spec in ((c.get("covers") or {}).get("fields") or {}).items():
        if spec.get("kind") not in KINDS:
            out.append(f"{c['id']} field {pat}: kind '{spec.get('kind')}' is not one of "
                       + ", ".join(KINDS))
        if not spec.get("is"):
            out.append(f"{c['id']} field {pat}: says nothing about what it is")
    if "produces" in c and c["produces"] not in KINDS:
        out.append(f"{c['id']}: produces '{c['produces']}', which is not a kind")
    for k in ("what", "model", "justified", "licenses", "not_licensed"):
        if not c.get(k):
            out.append(f"{c['id']}: no '{k}'")
    if "gaps" not in c:
        out.append(f"{c['id']}: no 'gaps' - an empty list is a claim too, so write one")
    for f in [x for w in c.get("watches", []) if "*" not in w.partition("#")[0] for x in [w]]:
        if _sha(f) == "missing":
            out.append(f"{c['id']}: watches {f}, which does not exist")
    return out


# ------------------------------------------------------------- for the index ---
def public(c):
    keep = ("id", "title", "what", "model", "assumptions", "justified", "gaps",
            "void_if", "licenses", "not_licensed", "produces", "watches")
    v = {k: c[k] for k in keep if k in c}
    cv = c.get("covers") or {}
    v["covers"] = cv.get("file") or ("a step" if cv.get("step") else cv.get("node"))
    v["status"] = status(c)
    conf = c.get("confirmed")
    v["confirmed"] = {"by": conf.get("by"), "on": conf.get("on")} if conf else None
    return v


def annotate(idx):
    """Give every entry its kind and constructions, and the index the declarations."""
    used = set()
    for e in idx["entries"].values():
        d = describe(e["src"])
        for k in ("kind", "synthetic", "constructions", "rests_on", "field", "uncovered"):
            e.pop(k, None)
        e.update(kind=d["kind"], synthetic=d["synthetic"],
                 constructions=d["constructions"], rests_on=d["rests_on"])
        if d.get("field"):
            e["field"] = d["field"]
        if d["uncovered"]:
            e["uncovered"] = d["uncovered"]
        used.update(d["constructions"])
    idx["constructions"] = {c["id"]: public(c) for c in load()["constructions"]
                            if c["id"] in used}
    idx["kinds"] = KINDS
    idx["method_pages"] = load().get("method_pages", [])


# ---------------------------------------------------------------------- cli ---
def main(argv):
    reg = load()
    cs = reg["constructions"]
    if "--reassess" in argv:
        target = argv[argv.index("--reassess") + 1]
        by = argv[argv.index("--by") + 1] if "--by" in argv else None
        if not by:
            log("  --reassess needs --by <name>: a confirmation is somebody's")
            return 2
        chosen = cs if target == "all" else [c for c in cs if c["id"] == target]
        if not chosen:
            log(f"  no construction {target}")
            return 1
        bad = [p for c in chosen for p in problems(c)]
        if bad:
            log("\n".join("  " + b for b in bad))
            log("  refusing to confirm declarations that fail their own checks")
            return 1
        for c in chosen:
            reassess(c, by)
        save(reg, {_ORIGIN.get(c["id"], REG) for c in chosen})
        log(f"  confirmed {len(chosen)} construction(s) as of today, by {by}")
        return 0
    if "--uncovered" in argv:
        idx = live.load_index()
        miss = sorted({u for e in idx["entries"].values() for u in describe(e["src"])["uncovered"]})
        log("\n".join("  " + m for m in miss) if miss else "  every field in use is declared")
        return 1 if miss else 0
    bad = []
    ids = [c["id"] for c in cs]
    bad += [f"{i}: declared twice" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for c in cs:
        bad += problems(c)
        s = status(c)
        if s != "current":
            bad.append(f"{c['id']}: {s}. Read it again against the code, then "
                       f"constructions.py --reassess {c['id']} --by <name>")
    for b in bad:
        log("  " + b)
    if bad:
        log(f"\n  {len(bad)} problem(s) in data/manual/number_constructions.json")
        return 1
    log(f"  {len(cs)} constructions: every one confirmed, current and free of "
        "unjustified numbers")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
