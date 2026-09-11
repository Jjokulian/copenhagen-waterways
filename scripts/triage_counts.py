#!/usr/bin/env python3
"""Counts over the hypothesis triage, so the triage page prints none by hand.

The triage (scripts/pages/triage_rows.py) puts every lettered hypothesis in one
class with its blocker. Every count the page states - per class, per group, in
the named clusters of blockers - is a count over those rows, done here and
stored in data/derived/triage.json. The rows are checked against the register
(data/derived/hypotheses.json): a triaged ID the register no longer holds is an
orphan, counted and named, never silently kept in a denominator it is not in.

    python3 scripts/triage_counts.py
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "pages"))

from common import DERIVED, ROOT, log
import triage_rows as T

REG = os.path.join(DERIVED, "hypotheses.json")
OUT = os.path.join(DERIVED, "triage.json")


def main(argv):
    h = json.load(open(REG, encoding="utf-8"))
    register = {x["id"] for x in h["hypotheses"]}
    rows = T.ROWS
    ids = [r["id"] for r in rows]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit(f"triage rows list {dup} twice")
    unknown = sorted({r["cls"] for r in rows} - set(T.CLASSES))
    if unknown:
        raise SystemExit(f"triage classes not declared: {unknown}")
    orphans = sorted(set(ids) - register)
    untriaged = sorted(register - set(ids))
    live = [r for r in rows if r["id"] in register]
    classes = {k: {"n": sum(r["cls"] == k for r in live)} for k in T.CLASSES}
    groups = {}
    for g in h["groups"]:
        gr = [r for r in live if r["group"] == g["id"]]
        groups[g["id"]] = {"n": len(gr), **{k: sum(r["cls"] == k for r in gr) for k in T.CLASSES}}
    clusters = {}
    for name, members in T.CLUSTERS.items():
        missing = [m for m in members if m not in ids]
        if missing:
            raise SystemExit(f"cluster {name} names untriaged {missing}")
        cls = collections.Counter(next(r["cls"] for r in rows if r["id"] == m) for m in members)
        clusters[name] = {"n": len(members), **{k: cls.get(k, 0) for k in T.CLASSES}}
    docs = os.path.join(ROOT, "docs")
    with_entry = sorted(i for i in register if any(
        os.path.exists(os.path.join(docs, sub, i + ".md")) for sub in ("hypodrafts", "openproblems")))
    out = {"_what": "Counts over the hypothesis triage (scripts/pages/triage_rows.py), "
                    "restricted to IDs the hypothesis register holds.",
           "n_rows": len(rows), "n_register": len(register), "n_triaged": len(live),
           "n_orphans": len(orphans), "orphans": orphans, "untriaged": untriaged,
           "n_groups": len(h["groups"]),
           "classes": classes, "groups": groups, "clusters": clusters,
           "n_with_entry": len(with_entry), "with_entry": with_entry}
    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"  {len(live)} triaged of {len(register)} in the register; orphans {orphans}; "
        f"untriaged {untriaged}")
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
