#!/usr/bin/env python3
"""How every number was made, as one small graph of files and scripts, stored once.

A number on the site is read from a field of a data file. The build list
(data/manual/build.json and build.d/, the scanned part read from the scripts' own
code) says which script writes each file and which files that script reads. Walked
backwards from a number's file, that is the number's whole chain: script, the files
it read, the scripts that wrote those, down to where the chain ends - raw data as
downloaded, a hand-kept register, a pinned document, a sibling project, or a file no
script in this project writes (an open end, said as one).

Nothing is stored per number, per table or per claim. The store 'flows' holds each
file once (what kind it is, who writes it, which construction covers it, the code
lines that compute each of its fields) and each script once (what it reads and
writes, which constructions describe it). The page draws a number's graph by walking
from the number's file through these records, and each number already names its
file and field. The theory of a step is the construction that covers the file it
writes, or that watches the script (data/manual/number_constructions.json), shown
from the constructions the number store already carries.

Called by live.render_sources() whenever the index is written; run on its own to see
what it would publish:

    python3 scripts/flows_store.py
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load_build, log   # noqa: E402

CONS = os.path.join(ROOT, "data", "manual", "number_constructions.json")
# Files a script reads to write its page's words, not to compute a number: the claims
# registers, the pinned texts it quotes, the registers of constructions and of the build.
# They are kept on the step as what it reads for its text, and are not followed as data.
PAGE_TEXT = re.compile(r"^data/manual/(claims|number_constructions|build)[./]|^data/derived/pins/")
REGISTERS = [os.path.join(ROOT, "data", "manual", f) for f in
             ("data_sources.json", "data_sources_2.json", "data_sources_3.json")]


def kind_of(f, prod):
    """What a file is. Raw data stays raw data when a fetch script wrote it - the
    script is how it was downloaded, and is kept as the file's producer."""
    if f.startswith("data/raw/"):
        return "raw"
    if f.startswith("data/manual/"):
        return "register"
    if f.startswith("data/derived/pins/"):
        return "pinned"
    if f.startswith("..") or (f.startswith("/") and not f.startswith(ROOT + "/")):
        return "sibling"
    if f in prod:
        return "derived"
    return "open"


def _registry():
    """Registered sources that name a place on disk: prefix -> (id, name)."""
    out = []
    for p in REGISTERS:
        if not os.path.exists(p):
            continue
        j = json.load(open(p, encoding="utf-8"))
        rows = j if isinstance(j, list) else next((v for v in j.values() if isinstance(v, list)), [])
        for r in rows:
            u = str(r.get("url", "")) if isinstance(r, dict) else ""
            if u.startswith("data/raw/"):
                prefix = re.split(r"[*\s(]|YYYY", u, 1)[0].rstrip("/")
                prefix = prefix.rsplit("/", 1)[0] if "." in prefix.rsplit("/", 1)[-1] else prefix
                out.append((prefix, r.get("id"), r.get("name")))
    return out


def _statement(lines, i):
    """From line i, the lines up to the end of the statement (brackets balanced)."""
    depth, j = 0, i
    while j < len(lines) and j < i + 8:
        depth += sum(lines[j].count(c) for c in "([{") - sum(lines[j].count(c) for c in ")]}")
        if depth <= 0:
            break
        j += 1
    return i + 1, min(j, len(lines) - 1) + 1


def build_flows(idx):
    """The 'flows' records, and a count of what could not be completed."""
    import live
    steps = load_build()["steps"]
    prod = {o: s["script"] for s in steps for o in s["outputs"]}
    ins = {s["script"]: [i for i in s["inputs"] if not i.startswith("scripts/") and not PAGE_TEXT.match(i)]
           for s in steps}
    text_ins = {s["script"]: [i for i in s["inputs"] if PAGE_TEXT.match(i)] for s in steps}
    outs = {s["script"]: s["outputs"] for s in steps}
    unres = {s["script"]: s.get("unresolved_paths", 0) for s in steps}
    cons = json.load(open(CONS, encoding="utf-8"))
    cons = cons if isinstance(cons, list) else cons.get("constructions", [])
    covers, watches = {}, {}
    for c in cons:
        cv = c.get("covers") or {}
        for cf in (cv if isinstance(cv, list) else [cv]):
            if isinstance(cf, dict) and cf.get("file"):
                covers.setdefault(cf["file"], []).append(c["id"])
        for w in c.get("watches") or []:
            watches.setdefault(w, []).append(c["id"])
    import claims
    pinsrc = claims.load()[0].get("sources", {})
    reg = _registry()

    # the files numbers read, and every file and script upstream of them
    fields = {}
    for e in idx["entries"].values():
        if e["src"][0] == "leaf":
            fields.setdefault(e["src"][1], set()).add(live._general(e["src"][2]))
    files, scripts, todo = {}, set(), list(fields)
    while todo:
        f = todo.pop()
        if f in files:
            continue
        files[f] = kind_of(f, prod)
        s = prod.get(f)
        if s and s not in scripts:
            scripts.add(s)
            todo.extend(ins.get(s, []))

    src, recs, missing_lines = {}, {}, 0
    for f, k in files.items():
        r = {"k": k}
        s = prod.get(f)
        if s:
            r["by"] = s
        if covers.get(f):
            r["K"] = covers[f]
        if k == "pinned":
            sid = os.path.basename(f)[:-4]
            if sid in pinsrc:
                r["doc"] = [pinsrc[sid].get("title", sid), pinsrc[sid].get("url", "")]
        if k == "raw":
            m = [(p, i, n) for p, i, n in reg if f.startswith(p)]
            if m:
                p, i, n = max(m, key=lambda x: len(x[0]))
                r["reg"] = [i, n]
        # where each field numbers read is computed: the statement in the writing script
        if s and fields.get(f):
            if s not in src:
                try:
                    src[s] = open(os.path.join(ROOT, s), encoding="utf-8").read().split("\n")
                except OSError:
                    src[s] = []
            impl = {}
            for g in sorted(fields[f]):
                key = [p for p in re.split(r"\.|\[|\]", g) if p and p != "*" and not p.isdigit()]
                hit = None
                if key:
                    pat = re.compile(r"[\"']" + re.escape(key[-1]) + r"[\"']")
                    hit = next((i for i, line in enumerate(src[s]) if pat.search(line)), None)
                if hit is None:
                    missing_lines += 1
                    continue
                a, b = _statement(src[s], hit)
                impl[g] = [a, b, "\n".join(src[s][a - 1:b])]
            if impl:
                r["impl"] = impl
        recs["F:" + f] = r
    for s in scripts:
        recs["S:" + s] = {"in": ins.get(s, []), "text": text_ins.get(s, []), "out": outs.get(s, []),
                          "K": sorted(set(watches.get(s, []))), "unres": unres.get(s, 0)}
    stats = {"files": len(files), "scripts": len(scripts), "by_kind": {},
             "open_ends": sorted(f for f, k in files.items() if k == "open"),
             "fields_without_a_found_line": missing_lines}
    for k in files.values():
        stats["by_kind"][k] = stats["by_kind"].get(k, 0) + 1
    return recs, stats


def publish(idx):
    import numbers_store
    recs, stats = build_flows(idx)
    numbers_store.build("flows", recs, {"stats": stats}, 25,
                        "each data file and script once: who writes what, from what")
    return stats


if __name__ == "__main__":
    import live
    recs, stats = build_flows(live.load_index())
    size = len(json.dumps(recs, ensure_ascii=False))
    print(json.dumps({k: v for k, v in stats.items() if k != "open_ends"}, indent=1))
    print("open ends:", stats["open_ends"])
    print(f"{len(recs)} records, {size / 1e3:.0f} KB")
