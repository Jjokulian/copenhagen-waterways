#!/usr/bin/env python3
"""The number index, published once per thing, as static-async-data shards.

The reader's number menu used to download docs/data/sources_index.json whole (9.5 MB)
on the first click, and SOURCES.md printed every one of its ~7,400 entries with the
same explanations over and over. Here each number is one small record, and what
numbers share - what a field is, which script wrote a file, how a kind of number is
made, which table a cell sits in - is stored once, in the store's shared meta. The
page loads that meta once and one shard of about 20 KB per click, through the loader
of the sibling project static-async-data (https://github.com/Jjokulian/static-async-data).

A table is justified once. The numbers in its cells are read from the same data by
the same script, so the table has one record saying so, and each cell points to it.
Numbers in running text are listed by where they come from: a data file, a pinned
document, a stated choice, or arithmetic on the page.

Called by live.render_sources() whenever the index is written.
"""
import glob
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

from common import ROOT, log

DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(DOCS, "static-async-data")
SAD = os.path.normpath(os.path.join(ROOT, "..", "static-async-data"))
REGISTERS = {"CLAIMS.md", "ARCHIVE.md", "SOURCES.md"}
LINK = re.compile(r"SOURCES\.md#(F-[0-9a-f]{10})")
HEAD = re.compile(r"^#{1,6}\s+(.*)")
# not carried into a record: the page generator's printing line and where it sits
# (string interpolation, not how the number was made), and the field description,
# which goes to the shared meta once
DROP = {"code", "where", "field"}


def _plain(s):
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"<[^>]+>", "", s)
    return " ".join(s.replace("**", "").replace("`", "").replace("†", "").split())


def content_pages():
    for p in sorted(glob.glob(os.path.join(DOCS, "**", "*.md"), recursive=True)):
        rel = os.path.relpath(p, DOCS)
        if rel in REGISTERS or rel.startswith("static-async-data"):
            continue
        yield rel, open(p, encoding="utf-8").read()


def tables_and_text(entries):
    """Every table on a content page that holds numbers, with what its cells are read
    from; which table(s) each number sits in; and the numbers in running text."""
    import live
    tabs, cell_of, text_ids = {}, {}, set()
    for rel, body in content_pages():
        heading, block, header, k = "", None, None, 0
        for line in body.split("\n") + [""]:
            if line.lstrip().startswith("|"):
                if block is None:
                    block, header = [], [_plain(c) for c in line.strip().strip("|").split("|")]
                block.extend(LINK.findall(line))
                continue
            if block:
                k += 1
                tid = "T-" + hashlib.sha1(f"{rel}|{k}|{heading}".encode()).hexdigest()[:8]
                files, docs, calc, stated = {}, set(), 0, 0
                for i in block:
                    s = (entries.get(i) or {}).get("src") or ["?"]
                    if s[0] == "leaf":
                        files.setdefault(s[1], set()).add(live._general(s[2]))
                    elif s[0] == "reading":
                        docs.add(s[1])
                    elif s[0] == "stated":
                        stated += 1
                    else:
                        calc += 1
                    cell_of.setdefault(i, set()).add(tid)
                tabs[tid] = {"page": rel, "heading": heading, "columns": [c for c in header if c],
                             "cells": len(block),
                             "files": {f: sorted(p) for f, p in sorted(files.items())},
                             "documents": sorted(docs), "calculated": calc, "stated": stated}
            block = None
            m = HEAD.match(line)
            if m:
                heading = _plain(m.group(1))
            text_ids.update(LINK.findall(line))
    return tabs, cell_of, text_ids


def publish(idx, tt):
    """Write docs/static-async-data/numbers: one record per number, the shared meta
    once. Skipped, with a line in the log, where the loader's project is absent."""
    import live
    if not os.path.isdir(os.path.join(SAD, "sad")):
        log(f"  numbers store not rebuilt: {SAD} (static-async-data) is not beside this project")
        return
    if SAD not in sys.path:
        sys.path.insert(0, SAD)
    import sad
    tabs, cell_of, _ = tt
    entries = idx["entries"]
    pages = sorted(idx.get("docs", {}))
    pnum = {p: k for k, p in enumerate(pages)}
    used = {}
    for d, ids in idx.get("docs", {}).items():
        for i in ids:
            used.setdefault(i, []).append(pnum[d])
    fields, fkey, records = {}, {}, {}
    for i, e in entries.items():
        r = {k: v for k, v in e.items() if k not in DROP}
        desc = (e.get("field") or {}).get("is")
        if desc:
            key = fkey.setdefault(desc, f"d{len(fkey)}")
            fields[key] = desc
            r["f"] = key
        kids = [live._id(c) for c in live._kids(e["src"]) if c[0] != "const"]
        if kids:
            r["ch"] = kids
        if i in used:
            r["u"] = sorted(used[i])
        if i in cell_of:
            r["t"] = sorted(cell_of[i])
        if not r.get("synthetic"):
            r.pop("synthetic", None)
        records[i] = r
    meta = {"kinds": idx.get("kinds", {}), "constructions": idx.get("constructions", {}),
            "method_pages": idx.get("method_pages", []), "producers": live._producers(),
            "fields": fields, "pages": pages, "tables": tabs}
    fd, tmp = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump({"records": records, **meta}, f, ensure_ascii=False)
    try:
        sad.build_all([{"source": tmp, "name": "numbers", "records_key": "records",
                        "shard_size": 30,
                        "note": "one record per number on the site; shared text in meta"}],
                      OUT, quiet=True)
    finally:
        os.remove(tmp)
    shutil.copyfile(os.path.join(SAD, "sad", "sad.js"), os.path.join(OUT, "sad.js"))


def sources_page(idx, tt):
    """SOURCES.md: what the number menus draw on, each thing once."""
    tabs, cell_of, text_ids = tt
    entries, prod = idx["entries"], None
    import live
    prod = live._producers()
    w = ["# Where the numbers come from", "",
         "*Generated by `scripts/numbers_store.py` each time a page is written. Click any "
         "number on the site to open its menu: how it was made, where it was read from, "
         "and the data around it. This page lists, once each, what those menus draw on. "
         "A table is made by one piece of code from one source, so it is described once, "
         "not cell by cell.*", ""]
    w += ["## The tables", "", f"{len(tabs):,} tables hold numbers.", ""]
    for tid, t in sorted(tabs.items(), key=lambda x: (x[1]["page"], x[0])):
        w.append(f'<a id="{tid}"></a>')
        w.append(f"### [{t['page']}]({t['page']}) — {t['heading'] or 'untitled'}")
        w.append("")
        cols = ", ".join(f"*{c}*" for c in t["columns"])
        parts = [f"{t['cells']:,} numbers" + (f" in the columns {cols}" if cols else "") + "."]
        for f, ps in t["files"].items():
            by = f", written by [`{prod[f]}`](../{prod[f]})" if prod.get(f) else ""
            parts.append(f"Read from `{f}` (" + ", ".join(f"`{p}`" for p in ps) + f"){by}.")
        if t["documents"]:
            parts.append("Read from pinned documents: " + ", ".join(f"`{d}`" for d in t["documents"]) + ".")
        if t["calculated"]:
            parts.append(f"{t['calculated']:,} calculated on the page, each with its arithmetic in its menu.")
        if t["stated"]:
            parts.append(f"{t['stated']:,} stated choices.")
        w += [" ".join(parts), ""]
    prose = [i for i in text_ids if i in entries]
    by = {}
    for i in prose:
        s = entries[i]["src"]
        key = {"leaf": ("file", s[1]), "reading": ("doc", s[1] if len(s) > 1 else "?"),
               "stated": ("stated", i), "quote": ("quote", i)}.get(s[0], ("calc", ""))
        by.setdefault(key, []).append(i)
    w += ["## Numbers in running text, by where they come from", "",
          f"{len(prose):,} distinct numbers in running text, from these sources.", ""]
    files = sorted(k for k in by if k[0] == "file")
    if files:
        w += ["### From data files", ""]
        for k in files:
            f = k[1]
            descs = {(entries[i].get("field") or {}).get("is") for i in by[k]} - {None}
            line = f"- `{f}`" + (f", written by [`{prod[f]}`](../{prod[f]})" if prod.get(f) else "")
            line += f" — {len(by[k]):,} numbers."
            if len(descs) == 1:
                line += " " + next(iter(descs))
            w.append(line)
        w.append("")
    docs = sorted(k for k in by if k[0] == "doc")
    if docs:
        w += ["### From pinned documents", ""]
        for k in docs:
            m = (entries[by[k][0]]["src"][4] if len(entries[by[k][0]]["src"]) > 4 else None) or {}
            title = f"[{m.get('title', k[1])}]({m['url']})" if m.get("url") else k[1]
            w.append(f"- {title} (`{k[1]}`) — {len(by[k]):,} numbers, each read at its phrase "
                     "from the pinned text.")
        w.append("")
    st = [by[k][0] for k in by if k[0] == "stated"]
    if st:
        w += ["### Stated choices, not measured", ""]
        for i in sorted(st, key=lambda i: entries[i]["src"][1]):
            s = entries[i]["src"]
            w.append(f"- `{s[1]}` = {live._fmt(entries[i]['value'])} — {s[2]}")
        w.append("")
    calc = by.get(("calc", ""), [])
    if calc:
        w += ["### Calculated on a page", "",
              f"{len(calc):,} numbers are arithmetic on the numbers above; each shows its "
              "calculation, with every operand linked, in its menu.", ""]
    q = [by[k][0] for k in by if k[0] == "quote"]
    if q:
        w += ["### Quoted from an earlier version of this site", "",
              f"{len(q):,} numbers are what this site printed at a past commit, checked "
              "against its history.", ""]
    return w
