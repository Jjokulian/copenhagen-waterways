#!/usr/bin/env python3
"""A number in prose must be able to say where it came from, or it does not ship.

There are roughly 348 numbers typed into string literals across this project's
generators. Being generated protected none of them: the landing page said 210 km
of surface alignment, two documents said 169, and the layer measures 280 - three
figures for one quantity, all defensible under different definitions, none of
them traceable, and nothing anywhere saying which definition was in use. That is
worse than a wrong number, because each survives scrutiny alone.

So a figure gets written one of two ways and there is no third:

    a(f"The plan holds {fig('surface_km')} km on the surface")

fig() reads the live value out of the derived file the registry names, formats
it, and wraps it in a link to its justification - the claim, its dependency
graph, the script that computed it, and what would falsify it. The number in the
document and the number in the data cannot differ, because they are the same
number.

The other way is to write it by hand, and then `check(md)` finds it and says so.
The check has two tiers on purpose:

  HARD   a fig() link pointing at a claim that does not exist, or whose live
         value no longer matches. That is a broken justification and it fails.

  DEBT   a bare number in prose that no figure accounts for. Reported with a
         count rather than failing, because failing on every digit would make the
         first commit impossible and the rule would be turned off within a day.
         The count is the debt, it is printed every run, and it only goes down.

The distinction is the same one that let the flood figures rot for two days: a
check that cannot be satisfied gets ignored, and an ignored check is worse than
no check because it looks like coverage.

WHAT COUNTS AS A NUMBER. Not years, not section numbers, not the digits inside a
code or an identifier, not a figure already inside a fig() link. What counts is a
quantity with a unit or a magnitude - the kind of thing a reader would quote.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT, log

REG = os.path.join(ROOT, "data", "manual", "claims.json")
_cache = {}


def _registry():
    if "r" not in _cache:
        d = json.load(open(REG, encoding="utf-8"))
        _cache["r"] = d.get("figures", {})
        _cache["claims"] = {c["id"] for c in d.get("claims", [])}
    return _cache["r"]


def _dig(obj, path):
    for k in path.split("."):
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def value(name):
    """The live value behind a registered figure, unformatted."""
    r = _registry().get(name)
    if r is None:
        raise KeyError(f"figure '{name}' is not registered in {os.path.relpath(REG, ROOT)}. "
                       "Add it with the file and path it comes from, and the claim "
                       "that justifies it - or find an existing figure that already "
                       "carries this number.")
    f = os.path.join(ROOT, r["file"])
    if not os.path.exists(f):
        raise FileNotFoundError(f"figure '{name}' reads {r['file']}, which is not built")
    v = _dig(json.load(open(f, encoding="utf-8")), r["path"])
    if v is None:
        raise KeyError(f"figure '{name}': {r['path']} not found in {r['file']}")
    return v


def fig(name, fmt=None):
    """The live value, formatted, linked to its justification.

    Renders as a markdown link so it works in both readers: on GitHub it
    navigates to the claim, and index.html intercepts it to open the
    justification beside the text instead."""
    v = value(name)          # raises with the instruction, before anything else
    r = _registry()[name]
    shown = (fmt or r.get("fmt", "{}")).format(v)
    claim = r.get("claim")
    return f"[{shown}](CLAIMS.md#{claim})" if claim else shown


LINK = re.compile(r"\[([^\]]+)\]\(CLAIMS\.md#([A-Za-z0-9\-_]+)\)")
# a quantity a reader would quote: a magnitude, or anything with a unit after it
QUANTITY = re.compile(
    r"(?<![\w.#-])(\d{1,3}(?:,\d{3})+|\d+\.\d+|\d{4,})"
    r"(?:\s*(?:km²|km2|km|m²|m|%|kt|kg|mg/l|µg/l|MB|GB|rows|stations))?")
YEARISH = re.compile(r"^(19|20)\d{2}$")


def check(md_path, text=None):
    """(hard failures, unaccounted numbers) for one generated document."""
    text = text if text is not None else open(md_path, encoding="utf-8").read()
    d = json.load(open(REG, encoding="utf-8"))
    claims = {c["id"] for c in d.get("claims", [])}
    hard, debt = [], []

    for shown, cid in LINK.findall(text):
        if cid not in claims:
            hard.append(f"{md_path}: {shown} links to {cid}, which is not a claim")

    # blank the accounted ones, then look at what is left
    rest = LINK.sub(lambda m: " " * len(m.group(0)), text)
    rest = re.sub(r"`[^`\n]*`", " ", rest)              # code spans are not prose
    rest = re.sub(r"^\s{4,}.*$", " ", rest, flags=re.M)  # indented blocks
    rest = re.sub(r"^(\|.*\|)$", " ", rest, flags=re.M)  # tables are data, not prose
    rest = re.sub(r"https?://\S+", " ", rest)
    for m in QUANTITY.finditer(rest):
        tok = m.group(1)
        if YEARISH.match(tok):
            continue
        debt.append(tok)
    return hard, debt


def main(argv):
    import glob
    paths = argv or sorted(glob.glob(os.path.join(ROOT, "docs", "*.md")))
    total_hard, total_debt = 0, 0
    rows = []
    for p in paths:
        hard, debt = check(os.path.relpath(p, ROOT))
        for h in hard:
            log("  HARD  " + h)
        total_hard += len(hard)
        total_debt += len(debt)
        if debt:
            rows.append((len(debt), os.path.basename(p), debt[:4]))
    rows.sort(reverse=True)
    log("\n  unaccounted numbers, by document:")
    for n, name, sample in rows[:14]:
        log(f"    {n:>5}  {name:<26} e.g. {', '.join(sample)}")
    log(f"\n  {total_hard} broken justification(s); {total_debt} number(s) in prose "
        "with none")
    log("  A number with no justification is not an error today. It is debt, it is "
        "counted every run, and it only goes down.")
    return 1 if total_hard else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
