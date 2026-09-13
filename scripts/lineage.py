#!/usr/bin/env python3
"""Where a number comes from, recorded by the producer while it runs.

PROVENANCE_SPEC.md asks every number that carries weight to show, looking
backward from the number: what was counted as one, the records it rests on in
their own words, each step with the producer's own source lines, why each step
was done that way, where every branch ends, the spread under an aggregate, and at
least one rerun with an imposed choice changed.

The producer calls this recorder at each step, so the account is written by the
code that did the work and cannot drift from it: source lines are read out of the
running module by `inspect`, located by text rather than by line number, and a
marker that is missing or ambiguous stops the run instead of recording a stale
excerpt. The recorder writes only its own file, never the producer's output.

    import lineage
    L = lineage.Lineage("cum_hoc_r", number={"file": ..., "path": ..., "value": ...})
    L.record("badevand", path, features, columns=[...], published_by=...)
    L.step("S1", "selection", "title", code=lineage.lines(fn, "first", "last"),
           imposes=..., inputs=[...], outputs={...}, why=..., author=...,
           alternative=..., tested=..., counted_as_one=...)
    L.end("branch", "record" | "construction" | "model output", "what", author=...)
    L.spread(pairs=[...], ...)
    L.rerun("what was imposed instead", changed={...}, value=..., n=...)
    L.write()                                   # docs/data/lineage/cum_hoc_r.json

The kinds are the spec's table and nothing else: a step given another kind is an
error, because the kind is where bias enters and a new word would hide it. A step
with no recorded reason says so in those words; nothing here supplies one.
"""
import inspect
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "data", "lineage")

KINDS = {
    "selection": "which records count: filters, sample types, complete years",
    "identity": "what counts as the same thing",
    "grouping": "boundaries: water bodies, catchments, regions",
    "classification": "classes: seasons, summer-peaked, triage classes",
    "convention": "thresholds and definitions: bottom water, a limit, a boundary",
    "correction": "a model applied to the value itself",
    "filling in": "interpolation, model output where nothing was measured",
    "functional form": "the shape assumed: linear, a retention model, a fitted curve",
    "attribution": "assigning a remainder to one cause",
}
END_TYPES = ("record", "construction", "model output")
NO_REASON = "no reason recorded"
NO_AUTHOR = "not recorded"


def _rel(path):
    return os.path.relpath(os.path.abspath(path), ROOT)


def lines(obj, first, last=None, until=None):
    """The source lines of one step: from the line containing `first` to the next
    line containing `last` (or just the one line), inside a function, class or
    module object, or inside a file given by path. Returns the file, the line
    range and the text itself. `until` ends the scope searched at the first line
    containing it, so a producer can search its own file above the code that
    records it (whose call literals would otherwise match too).

    Located by text, so an edit elsewhere never shifts the excerpt. `first` must
    occur exactly once in the scope searched, or this raises: an excerpt that
    might be the wrong one is worse than none."""
    if isinstance(obj, str):
        path = obj if os.path.isabs(obj) else os.path.join(ROOT, obj)
        with open(path, encoding="utf-8") as f:
            src = f.read().split("\n")
        start = 1
    else:
        path = inspect.getsourcefile(obj)
        src, start = inspect.getsourcelines(obj)
        src = [s.rstrip("\n") for s in src]
        start = max(start, 1)          # a module reports 0; its first line is 1
    if until:
        cut = [i for i, s in enumerate(src) if until in s]
        if not cut:
            raise LookupError(f"lineage: {until!r} not found in {_rel(path)}")
        src = src[:cut[0]]
    hits = [i for i, s in enumerate(src) if first in s]
    if len(hits) != 1:
        raise LookupError(f"lineage: {first!r} occurs {len(hits)} times in the scope "
                          f"searched in {_rel(path)}; it must occur once")
    a = hits[0]
    b = a
    if last:
        after = [i for i, s in enumerate(src) if last in s and i >= a]
        if not after:
            raise LookupError(f"lineage: {last!r} not found after {first!r} in {_rel(path)}")
        b = after[0]
    return {"file": _rel(path), "first": start + a, "last": start + b,
            "text": "\n".join(src[a:b + 1])}


def quote(obj, first, last=None, until=None):
    """A reason as the code states it: the lines themselves, stripped of
    indentation and comment marks, with where they are."""
    ref = lines(obj, first, last, until)
    text = " ".join(s.strip().lstrip("#").strip() for s in ref["text"].split("\n"))
    return text.strip().strip('"').strip(), ref


def _plain(v):
    """A value as the file holds it, made JSON-safe without changing it."""
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, (list, tuple)):
        return [_plain(x) for x in v]
    if isinstance(v, dict):
        return {str(k): _plain(x) for k, x in v.items()}
    return repr(v)


class Lineage:
    def __init__(self, name, number):
        self.name = name
        self.doc = {"number": number, "counted_as_one": [], "records": [],
                    "steps": [], "ends": [], "notes": {}, "spread": None,
                    "robustness": [], "not_on_this_chain": [], "kinds": KINDS}

    def record(self, rid, path, rows, columns, published_by, fetched_from=None,
               pick=None, props=lambda r: r, where=None, marked=None, file_meta=None):
        """A terminal: file F, rows as written. `rows` is the full list the
        producer read; a handful are copied verbatim - every column, under its own
        name - with the total count. `pick` chooses which rows (default: the first
        four); `props` takes a row's columns (for GeoJSON, its properties); `where`
        says how the row's geometry was read."""
        idx = pick(rows) if pick else list(range(min(4, len(rows))))
        sample = []
        for i in idx:
            s = {"row": i, "fields": _plain(props(rows[i]))}
            if where:
                s["where"] = _plain(where(rows[i]))
            sample.append(s)
        self.doc["records"].append({
            "id": rid, "file": _rel(path), "rows": len(rows),
            "columns_used": list(columns), "published_by": published_by,
            "fetched_from": fetched_from, "file_meta": _plain(file_meta or {}),
            "constructions_on_record": marked or [], "sample": sample})

    def step(self, sid, kind, title, code, imposes, inputs, outputs, branch=None,
             why=NO_REASON, why_ref=None, author=NO_AUTHOR, alternative=None,
             tested=None, counted_as_one=None, said=None, settle=None):
        """`said` carries a step that somebody else did and published no code for:
        their method, reason and stated limits in their own words, each checked
        against the pinned document by the caller. `settle` is what would close the
        question the step leaves open."""
        if kind not in KINDS:
            raise ValueError(f"lineage: {kind!r} is not a kind in PROVENANCE_SPEC.md")
        self.doc["steps"].append({
            "id": sid, "kind": kind, "branch": branch, "title": title,
            "imposes": imposes, "counted_as_one": counted_as_one,
            "inputs": _plain(inputs), "code": code if isinstance(code, list) else [code],
            "said": _plain(said or []), "settle": settle,
            "why": {"reason": why or NO_REASON, "ref": why_ref, "author": author or NO_AUTHOR},
            "alternative": alternative, "tested": tested or "not tested",
            "outputs": _plain(outputs)})
        if counted_as_one:
            self.doc["counted_as_one"].append({"what": counted_as_one, "step": sid})

    def end(self, branch, typ, what, record=None, author=NO_AUTHOR, steps=()):
        if typ not in END_TYPES:
            raise ValueError(f"lineage: an end is one of {END_TYPES}, not {typ!r}")
        self.doc["ends"].append({"branch": branch, "type": typ, "what": what,
                                 "record": record, "author": author, "steps": list(steps)})

    def note(self, key, text):
        self.doc["notes"][key] = text

    def spread(self, **kw):
        self.doc["spread"] = _plain(kw)

    def rerun(self, rid, imposed, changed, value, n, step=None, headline=False, note=None,
              code=None):
        self.doc["robustness"].append({"id": rid, "imposed": imposed, "changed": changed,
                                       "value": value, "n": n, "step": step,
                                       "headline": headline, "note": note, "code": code})

    def graph(self, regions, nodes, edges):
        """The same chain as nodes, edges and regions (the owner's model, 2026-09-13):
        a node is a result, a record or a construction, with what it means and its
        caveats; an edge is one recorded step - the computation from its inputs to its
        output - so its method, reason and limits are the step's own, not repeated;
        a region is the theory several steps work within, written once. Every step is
        one edge in exactly one region, and every node an edge names exists."""
        steps = [s["id"] for s in self.doc["steps"]]
        ids = {n["id"] for n in nodes}
        rids = {r["id"] for r in regions}
        placed = [e for r in regions for e in r["edges"]]
        drawn = [e["step"] for e in edges]
        if sorted(placed) != sorted(steps) or sorted(drawn) != sorted(steps):
            raise ValueError("lineage graph: every step must be one edge in exactly one region")
        for e in edges:
            for x in list(e["from"]) + [e["to"]]:
                if x not in ids:
                    raise ValueError(f"lineage graph: {e['step']} names {x!r}, which is no node")
        for n in nodes:
            if n["region"] not in rids:
                raise ValueError(f"lineage graph: node {n['id']!r} is in no region")
        self.doc["graph"] = _plain({"regions": regions, "nodes": nodes, "edges": edges})

    def aside(self, what, why):
        self.doc["not_on_this_chain"].append({"what": what, "why": why})

    def write(self):
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, self.name + ".json")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.doc, f, ensure_ascii=False, indent=1)
            f.write("\n")
        os.replace(tmp, path)
        return path
