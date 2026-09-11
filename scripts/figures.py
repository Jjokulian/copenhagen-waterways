#!/usr/bin/env python3
"""A number in prose must say where it came from, or the build refuses it.

There were roughly 348 numbers typed into string literals across the generators,
and being generated protected none of them. The landing page said 210 km of
surface alignment, two documents said 169, and the layer measures 280 - three
figures for one quantity, all defensible, none traceable, nothing saying which
definition of "surface" each one used. That is worse than a wrong number,
because each survives scrutiny on its own.

TWO KINDS OF NUMBER, with two kinds of justification, because they are
different objects:

  COMPUTED  written through fig(), which reads the live value from a derived
            file and links it to its justification. The script that made the
            file knows exactly what it did, so it records that itself with
            provenance(): what was counted as the same thing, the calculation,
            how many rows went in and were used, what was excluded and why, and
            what the other defensible definitions would have given. The chain is
            narrow - it is what was coded - and it is written by the code.

  ASSESSED  a number carried in prose that no script computes: somebody else's
            published figure, a reading of a document, a judgement. It cannot be
            re-derived, so it is assessed by a person instead - what it counts,
            why it is believed, how confident, what would change it - in the
            claim register.

THE RATCHET THAT WAS HERE, AND WHY IT WENT. A bare number in prose with neither kind of justification is not
allowed in. Every document has a baseline count of such numbers, recorded in
data/manual/figure_debt.json, and the build FAILS if any document goes above its
baseline. So a new unreferenced number is a hard error from the moment the
baseline exists, the numbers already published are carried as debt rather than
blocking every commit, and a baseline can only go down: --ratchet lowers it to
the current count and never raises it. A document with no baseline has a
baseline of zero.

That is the resolution of a real tension. Failing on all 711 existing numbers
would make the next commit impossible, and a rule that cannot be satisfied is
switched off within a day - which is how check_generated.py's warning came to be
read as "do not regenerate". Counting without failing lets new debt in. The
ratchet does neither.

A WRITER WHO NEEDS A NUMBER has two options, and the error message says both:

    python3 scripts/figures.py --find 168.1     is it already registered?
    then fig('name') in the generator, or register it in claims.json

    python3 scripts/figures.py                  check against baselines
    python3 scripts/figures.py --ratchet        lower baselines to current
    python3 scripts/figures.py --census         the debt, by document

WHAT COUNTS AS A NUMBER. A quantity a reader would quote: a magnitude, or
anything with a unit. Not years, not section numbers, not code spans, not
tables (data, not prose), not a number already inside a justification link. The
detector under-counts, so the debt is a floor.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT, log

REG = os.path.join(ROOT, "data", "manual", "claims.json")
# The register itself states each claim once, in full - its numbers ARE the
# claims. Counting them as unreferenced would be asking the index to cite itself.
EXEMPT = {"docs/CLAIMS.md"}
_cache = {}


def _reg():
    """claims.json with its fragments in claims.d/ merged."""
    if "d" not in _cache:
        from common import fragments
        d = json.load(open(REG, encoding="utf-8"))
        for f in fragments(REG)[1:]:
            frag = json.load(open(f, encoding="utf-8"))
            for k in ("figures", "params", "sources"):
                d.setdefault(k, {}).update(frag.get(k, {}))
            for k in ("claims", "nodes"):
                d.setdefault(k, []).extend(frag.get(k, []))
        _cache["d"] = d
    return _cache["d"]


def _dig(obj, path):
    for k in path.split("."):
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def provenance(counts_as, calculation, code, n_in=None, n_used=None,
               excluded=None, alternatives=None, unit=None):
    """What a computed figure is, written by the code that computed it.

    counts_as     the class: what was treated as the same thing, so as to be
                  counted together. The decision that made three conveyance
                  figures disagree lives here and nowhere else.
    calculation   the arithmetic, in words a reader can check.
    code          file:function, so the chain can be followed to the line.
    excluded      [(reason, n)] - what was left out, and how much.
    alternatives  [(definition, value)] - the other defensible readings, and
                  what each would have given. A figure without this implies its
                  definition was the only one available, which is rarely true.
    """
    return {"counts_as": counts_as, "calculation": calculation, "code": code,
            "unit": unit, "n_in": n_in, "n_used": n_used,
            "excluded": [{"reason": r, "n": n} for r, n in (excluded or [])],
            "alternatives": [{"definition": d, "value": v}
                             for d, v in (alternatives or [])]}


def value(name):
    figs = _reg().get("figures", {})
    r = figs.get(name)
    if r is None:
        raise KeyError(
            f"figure '{name}' is not registered in "
            f"{os.path.relpath(REG, ROOT)}. Run `python3 scripts/figures.py "
            "--find <value>` to see whether it already exists under another "
            "name, or register it with the file and path it comes from and the "
            "claim that justifies it.")
    f = os.path.join(ROOT, r["file"])
    if not os.path.exists(f):
        raise FileNotFoundError(f"figure '{name}' reads {r['file']}, which is "
                                "not built - run its generator first")
    v = _dig(json.load(open(f, encoding="utf-8")), r["path"])
    if v is None:
        raise KeyError(f"figure '{name}': {r['path']} not found in {r['file']}")
    return v


def shown(name):
    return _reg()["figures"][name].get("fmt", "{}").format(value(name))


def fig(name, fmt=None):
    """The live value, formatted, linked to its justification."""
    v = value(name)
    r = _reg()["figures"][name]
    s = (fmt or r.get("fmt", "{}")).format(v)
    return f"[{s}](CLAIMS.md#{r['claim']})" if r.get("claim") else s



import live

CLAIMLINK = re.compile(r"\[([^\]]+)\]\((?:\.\./)*CLAIMS\.md#([A-Za-z0-9\-_]+)\)")
SRCLINK = re.compile(r"\[([^\]]+)\]\((?:\.\./)*SOURCES\.md#(F-[0-9a-f]{10})\)")


def _landing_prose(html):
    """The reader-facing text of index.html: its long string literals."""
    # code comments are not prose a reader sees
    html = re.sub(r"/\*.*?\*/", "", html, flags=re.S)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"(?m)^\s*//.*$", "", html)
    lits = re.findall(r'"((?:[^"\\]|\\.){30,400})"', html)
    return "\n".join(l for l in lits
                     if re.search(r"[a-z]{3,}\s+[a-z]{3,}", l)
                     and "http" not in l and "{" not in l and ";" not in l)


def _landing_accounted():
    """index.html is not generated, so fig() cannot reach it. A number there is
    justified when it is the live value of a registered figure whose claim lists
    index.html in appears_in - which claims.py separately keeps true."""
    ok = set()
    claims = {c["id"]: c for c in _reg().get("claims", [])}
    for name, r in _reg().get("figures", {}).items():
        c = claims.get(r.get("claim"))
        if c and "index.html" in c.get("appears_in", []):
            try:
                ok.add(shown(name))
            except (KeyError, FileNotFoundError):
                pass
    return ok


def check(rel, text=None):
    """(broken justifications, unjustified numbers) for one document."""
    path = os.path.join(ROOT, rel)
    text = text if text is not None else open(path, encoding="utf-8").read()
    claims = {c["id"] for c in _reg().get("claims", [])}
    entries = live.load_index().get("entries", {})
    hard = [f"{rel}: {s} links to {cid}, which is not a claim"
            for s, cid in CLAIMLINK.findall(text) if cid not in claims]
    hard += [f"{rel}: {s} links to {fid}, which SOURCES.md does not hold"
             for s, fid in SRCLINK.findall(text) if fid not in entries]
    # a source is not enough: the construction must be declared, and a number
    # built on simulation may stand only on a method page
    import constructions
    for s, fid in SRCLINK.findall(text):
        e = entries.get(fid) or {}
        if e.get("uncovered"):
            hard.append(f"{rel}: {s} ({fid}) has no declared construction for "
                        + "; ".join(e["uncovered"]))
        if e.get("synthetic") and not constructions.synthetic_allowed(rel):
            hard.append(f"{rel}: {s} ({fid}) is built on simulation, and {rel} is not "
                        "a method page")
    if rel in live.EXEMPT:
        return hard, []
    # references and chemical species are checked entities too: a committed one
    # must still match its register, and none may be typed bare
    import chem
    import refs
    body = _landing_prose(text) if rel == "index.html" else text
    rh, rb = refs.check_links(rel, body)
    ch, cb = chem.check_spans(rel, body)
    hard += rh + ch
    extra = [(l, "ref " + t, c) for l, t, c in rb] + [(l, "chem " + t, c) for l, t, c in cb]
    if rel == "index.html":
        # the landing is generated now (scripts/pages/landing.py -> docs/LANDING.md,
        # checked like every page); a number typed into index.html's own strings is
        # refused outright - no value-matching exemption any more
        return hard, live.bare_numbers(body) + extra
    return hard, live.bare_numbers(text) + extra


def targets():
    docs = glob.glob(os.path.join(ROOT, "docs", "**", "*.md"), recursive=True)
    return sorted(os.path.relpath(p, ROOT).replace(os.sep, "/") for p in docs) \
        + ["index.html"]


def staged():
    import subprocess
    r = subprocess.run(["git", "diff", "--cached", "--name-only"], cwd=ROOT,
                       capture_output=True, text=True)
    names = set(r.stdout.split())
    return [t for t in targets() if t in names]


def find(q):
    """Is this number already registered? Search live values and claim text."""
    q = q.replace(",", "")
    hits = []
    for name, r in _reg().get("figures", {}).items():
        try:
            s = shown(name)
        except (KeyError, FileNotFoundError):
            continue
        if q in s.replace(",", ""):
            hits.append(f"  fig('{name}') = {s}   [{r['file']}:{r['path']}]"
                        f" -> {r.get('claim')}")
    for c in _reg().get("claims", []):
        if q in c["claim"].replace(",", ""):
            hits.append(f"  claim {c['id']}: {c['claim'][:90]}")
    return hits


def main(argv):
    """Every number must have a chain of justification. No allowance.

        figures.py                  the whole site; exit 1 if any number is bare
        figures.py --staged         only the documents being committed (the hook)
        figures.py --find 168.1     is this number already registered?
    """
    if argv and argv[0] == "--find":
        if len(argv) < 2:
            log("usage: figures.py --find <value>")
            return 2
        hits = find(argv[1])
        log("\n".join(hits) if hits else
            f"  nothing registered holds {argv[1]}. Load it with live_json() in "
            "its generator, or register it in data/manual/claims.json.")
        return 0
    docs = staged() if "--staged" in argv else targets()
    total, failing, hard_all = 0, [], []
    for rel in docs:
        hard, bare = check(rel)
        hard_all += hard
        if bare:
            failing.append((rel, bare))
            total += len(bare)
    for h in hard_all:
        log("  BROKEN   " + h)
    for rel, bare in sorted(failing, key=lambda x: -len(x[1])):
        ex = ", ".join(b[1] for b in bare[:4])
        log(f"  {len(bare):>5}  {rel:<34} e.g. {ex}")
    if not failing and not hard_all:
        log(f"  every number in {len(docs)} document(s) has a chain of justification")
        return 0
    log(f"\n  {total} unchecked entit(ies) in {len(failing)} document(s): numbers "
        "without a chain of justification, references typed bare ('ref K1'), and "
        "chemical formulas typed bare ('chem O2'). See LIVE_NUMBERS.md.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
