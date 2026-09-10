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

THE RATCHET. A bare number in prose with neither kind of justification is not
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
BASELINE = os.path.join(ROOT, "data", "manual", "figure_debt.json")
# The register itself states each claim once, in full - its numbers ARE the
# claims. Counting them as unreferenced would be asking the index to cite itself.
EXEMPT = {"docs/CLAIMS.md"}
_cache = {}


def _reg():
    if "d" not in _cache:
        _cache["d"] = json.load(open(REG, encoding="utf-8"))
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


LINK = re.compile(r"\[([^\]]+)\]\(CLAIMS\.md#([A-Za-z0-9\-_]+)\)")
# A quantity: any number with a unit after it, whatever its size - "28%",
# "4 mg/l", "500 km" are exactly what a reader quotes - plus any bare number
# large or precise enough to be one (thousands separator, decimal, four digits).
# The first version required the second shape for everything, so every integer
# percentage on the site walked straight past the ratchet.
UNIT = (r"km²|km2|km|m²|%|pp|kt|kg|mg/l|µg/l|mg|MB|GB|ha|DE|rows|stations|"
        r"businesses|holdings|sites|parcels|sources|hypotheses|samples|years")
QUANTITY = re.compile(
    r"(?<![\w.#/-])("
    r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d{4,}"
    r"|\d+(?=\s*(?:" + UNIT + r")(?![a-zA-Z]))"
    r")")
YEARISH = re.compile(r"^(19|20)\d{2}$")


def _numbers(text):
    rest = LINK.sub(lambda m: " " * len(m.group(0)), text)
    rest = re.sub(r"`[^`\n]*`", " ", rest)
    rest = re.sub(r"^\s{4,}.*$", " ", rest, flags=re.M)
    rest = re.sub(r"^(\|.*\|)$", " ", rest, flags=re.M)
    rest = re.sub(r"https?://\S+", " ", rest)
    return [m.group(1) for m in QUANTITY.finditer(rest)
            if not YEARISH.match(m.group(1))]


def _landing_prose(html):
    """The reader-facing text of index.html: its long string literals.

    index.html is not generated, so fig() cannot reach it. A number there is
    accounted for when it is the live value of a registered figure whose claim
    lists index.html in appears_in - which claims.py then checks stays true."""
    lits = re.findall(r'"((?:[^"\\]|\\.){30,400})"', html)
    return "\n".join(l for l in lits
                     if re.search(r"[a-z]{3,}\s+[a-z]{3,}", l)
                     and "http" not in l and "{" not in l and ";" not in l)


def _landing_accounted():
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
    """(hard failures, unreferenced numbers) for one document."""
    path = os.path.join(ROOT, rel)
    text = text if text is not None else open(path, encoding="utf-8").read()
    claims = {c["id"] for c in _reg().get("claims", [])}
    hard = [f"{rel}: {s} links to {cid}, which is not a claim"
            for s, cid in LINK.findall(text) if cid not in claims]
    if rel in EXEMPT:
        return hard, []
    if rel == "index.html":
        ok = _landing_accounted()
        return hard, [n for n in _numbers(_landing_prose(text)) if n not in ok]
    return hard, _numbers(text)


def targets():
    return sorted(os.path.relpath(p, ROOT)
                  for p in glob.glob(os.path.join(ROOT, "docs", "*.md"))) + ["index.html"]


def census():
    out, hard = {}, []
    for rel in targets():
        h, d = check(rel)
        hard += h
        out[rel] = d
    return out, hard


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
    if argv and argv[0] == "--find":
        if len(argv) < 2:
            log("usage: figures.py --find <value>")
            return 2
        hits = find(argv[1])
        log("\n".join(hits) if hits else
            f"  nothing registered holds {argv[1]}. Register it in "
            "data/manual/claims.json - a computed figure with file and path, "
            "or an assessed claim with its reasoning.")
        return 0

    counts, hard = census()
    base = json.load(open(BASELINE, encoding="utf-8")) if os.path.exists(BASELINE) \
        else None

    if "--census" in argv or base is None or "--ratchet" in argv:
        rows = sorted(((len(v), k) for k, v in counts.items() if v), reverse=True)
        for n, k in rows[:20]:
            log(f"  {n:>5}  {k}")
        log(f"  {sum(len(v) for v in counts.values())} unreferenced number(s)")

    if base is None or "--ratchet" in argv:
        old = (base or {}).get("docs", {})
        new = {}
        for k, v in counts.items():
            n = len(v)
            new[k] = min(n, old[k]) if k in old else n
        lowered = [k for k in new if k in old and new[k] < old[k]]
        with open(BASELINE, "w", encoding="utf-8") as f:
            json.dump({"_what": "Unreferenced numbers each document is allowed "
                                "to carry. The build fails above these. They "
                                "only go down: --ratchet never raises one.",
                       "total": sum(new.values()), "docs": new},
                      f, indent=1, sort_keys=True)
            f.write("\n")
        log(f"\n  baseline {'written' if base is None else 'ratcheted'}: "
            f"{sum(new.values())} total"
            + (f"; lowered for {len(lowered)} document(s)" if lowered else ""))
        return 1 if hard else 0

    over = []
    docs = base.get("docs", {})
    for k, v in counts.items():
        allowed = docs.get(k, 0)
        if len(v) > allowed:
            over.append((k, len(v), allowed, v))
    for h in hard:
        log("  BROKEN   " + h)
    for k, n, allowed, v in over:
        log(f"  REFUSED  {k}: {n} unreferenced number(s), baseline {allowed}")
        extra = [x for x in v]
        log(f"           new ones are among: {', '.join(extra[-min(5, n-allowed):])}")
        log("           For each: `python3 scripts/figures.py --find <value>` to "
            "reuse a registered figure, or register it - computed (file + path, "
            "via fig()) or assessed (a claim with its reasoning).")
    if over or hard:
        return 1
    total = sum(len(v) for v in counts.values())
    log(f"  no new unreferenced numbers ({total} carried as debt, "
        f"baseline {base.get('total')})")
    if total < base.get("total", total):
        log("  debt has gone down - run --ratchet to lock it in")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
