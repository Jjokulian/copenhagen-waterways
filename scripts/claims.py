#!/usr/bin/env python3
"""What every claim rests on, as a graph, checked for the circularity it would hide.

Prose hides dependency. A sentence saying the diurnal amplitude is below half a
milligram reads like a measurement, and it is a bound derived from a synthetic
recovery run on a real schedule under a stipulated signal shape and a noise model
- four different kinds of thing, one of which is not data at all. A reader cannot
see that, and neither can the author six weeks later.

So every substantive claim is registered with the graph of what it stands on, and
the graph is drawn beside the claim rather than described. Node shape and colour
carry the kind, because the kind is the whole point: a claim resting on a
stipulation is a different object from one resting on a measurement, however
similar the two sentences look.

  held        a dataset on disk, with its faults
  external    somebody else's published number, used as input
  gap         data that exists and we cannot reach, or that nobody has measured
  synthetic   generated to test the method - licenses claims about the
              INSTRUMENT and never about the world
  assumption  stipulated, not measured. The claim is void if it is wrong
  script      the code
  claim       a statement on a page, which may rest on other claims

THE GRAPH IS CHECKED FOR CYCLES, which is the point of building it rather than
writing the dependencies in a list. A cycle in a claim graph is circular
reasoning made visible: A rests on B rests on A. That failure is silent in prose
and fatal in argument, and this refuses to generate a page containing one.

Diagrams are mermaid, which GitHub renders natively and index.html renders
through mermaid.js, so one source of truth serves both readers.

    python3 scripts/claims.py           # writes docs/CLAIMS.md
    python3 scripts/claims.py --check   # validate only, for the pre-commit hook

Other generators embed a single claim's foundation with foundation(claim_id).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT, log, read_json

SRC = os.path.join(ROOT, "data", "manual", "claims.json")
OUT = os.path.join(ROOT, "docs", "CLAIMS.md")

# shape carries kind, so the graph is readable without the legend
SHAPE = {
    "held":       ('[("', '")]'),      # cylinder: a store
    "external":   ('[("', '")]'),
    "gap":        ('{{"', '"}}'),      # hexagon: absent
    "synthetic":  ('>"', '"]'),        # flag: made up on purpose
    "assumption": ('{"', '"}'),        # rhombus: a decision
    "script":     ('["', '"]'),        # box: code
    "claim":      ('("', '")'),        # rounded: a statement
}
STYLE = {
    "held":       "fill:#1c4e70,stroke:#58a6ff,color:#e6edf3",
    "external":   "fill:#3d3357,stroke:#a58cf0,color:#e6edf3",
    "gap":        "fill:#5c2323,stroke:#ff7b72,color:#ffdcd7,stroke-dasharray:4 3",
    "synthetic":  "fill:#4a3a12,stroke:#e8a33d,color:#ffeccc",
    "assumption": "fill:#4a3a12,stroke:#e8a33d,color:#ffeccc,stroke-dasharray:3 2",
    "script":     "fill:#21262d,stroke:#8b949e,color:#c9d1d9",
    "claim":      "fill:#173a26,stroke:#3fb950,color:#d7ffe4",
}
KIND_NOTE = {
    "measured": "rests on measurement",
    "bounded": "a bound, not a point estimate",
    "simulated": "about the instrument, not the world",
    "provisional": "unchecked - see the graph for what would check it",
    "gap": "a statement that something cannot be established",
}


def load():
    d = read_json(SRC)
    nodes = {n["id"]: n for n in d["nodes"]}
    claims = {c["id"]: c for c in d["claims"]}
    return d, nodes, claims


def dig(obj, path):
    for k in path.split("."):
        if isinstance(obj, list):
            return None
        if not isinstance(obj, dict) or k not in obj:
            return None
        obj = obj[k]
    return obj


def check_figures(claims):
    """Does the number in the sentence still match the number in the data?

    Provenance says what a claim rests on. This says whether it still does. A
    claim may declare value_from = {file, path}, and the sentence must contain
    the value that path currently holds - so a figure that drifted from the data
    under it fails the build instead of being published.

    This is the half the dependency graph did not cover. The graph would have
    kept saying FLOOD_GAP rests on the sheets and the script, correctly, while
    the sentence said 5.932 and the data said 5.847."""
    bad = []
    for cid, c in claims.items():
        v = c.get("value_from")
        if not v:
            continue
        f = os.path.join(ROOT, v["file"])
        if not os.path.exists(f):
            if not v.get("optional"):
                bad.append(f"{cid}: {v['file']} does not exist, so its figure "
                           "cannot be checked")
            continue
        cur = dig(json.load(open(f, encoding="utf-8")), v["path"])
        if cur is None:
            bad.append(f"{cid}: {v['path']} not found in {v['file']}")
            continue
        shown = v.get("fmt", "{}").format(cur)
        if shown not in c["claim"]:
            bad.append(f"{cid}: the claim says something other than {shown}, "
                       f"which is what {v['file']}:{v['path']} holds now. "
                       "The sentence has drifted from its data.")
        # A figure is usually stated in more than one place, and index.html is
        # the least checked surface on the site: it is hand-maintained, it is not
        # generated by anything, and it is the first thing a reader sees. It said
        # 210 km of alignments where two documents said 169 and the layer
        # measures 280, all three typed by hand. appears_in closes that: the live
        # value must be present in every file that states it, generated or not.
        for where in c.get("appears_in", []):
            wp = os.path.join(ROOT, where)
            if not os.path.exists(wp):
                bad.append(f"{cid}: appears_in names {where}, which is missing")
                continue
            txt = open(wp, encoding="utf-8", errors="replace").read()
            if shown not in txt:
                bad.append(f"{cid}: {where} does not contain {shown}, the current "
                           f"value of {v['file']}:{v['path']}. A hand-maintained "
                           "page has drifted from the data.")
    return bad


def validate(nodes, claims):
    """Dangling references, cycles, and figures that no longer match their source."""
    bad = list(check_figures(claims))
    known = set(nodes) | set(claims)
    for cid, c in claims.items():
        for r in c["rests_on"]:
            if r not in known:
                bad.append(f"{cid} rests on {r}, which is not defined")
    # depth-first cycle detection over claim-to-claim edges
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
    return bad


def _node_line(nid, node):
    kind = node.get("kind", "claim")
    o, c = SHAPE.get(kind, SHAPE["claim"])
    label = node["label"] if "label" in node else node["claim"][:60]
    # mermaid does not read \n inside a quoted label - it would print literally
    label = label.replace("\\n", " · ").replace("\n", " · ").replace('"', "'")
    return f'  {nid}{o}{label}{c}'


def graph_for(cid, nodes, claims, depth=2):
    """Mermaid for one claim and everything under it."""
    seen, edges = {}, []

    def add(nid, d):
        if nid in seen or d < 0:
            return
        n = nodes.get(nid) or claims.get(nid)
        if not n:
            return
        seen[nid] = n if nid in nodes else dict(n, kind="claim",
                                                label=n["claim"][:58] + "...")
        for r in (claims.get(nid, {}).get("rests_on") or []):
            edges.append((r, nid))
            add(r, d - 1)

    add(cid, depth)
    out = ["```mermaid", "graph BT"]
    for nid, n in seen.items():
        out.append(_node_line(nid, n))
    for a, b in dict.fromkeys(edges):
        if a in seen and b in seen:
            out.append(f"  {a} --> {b}")
    for nid, n in seen.items():
        k = n.get("kind", "claim")
        out.append(f"  style {nid} {STYLE.get(k, STYLE['claim'])}")
    out.append("```")
    return "\n".join(out)


def foundation(cid, summary=None):
    """A drop-in fold for any generator: the claim's graph and what would break it."""
    d, nodes, claims = load()
    c = claims.get(cid)
    if not c:
        return ""
    head = summary or f"What this rests on ({KIND_NOTE.get(c['kind'], c['kind'])})"
    body = [graph_for(cid, nodes, claims), ""]
    for r in c["rests_on"]:
        n = nodes.get(r) or claims.get(r)
        if not n:
            continue
        kind = n.get("kind", "claim")
        lab = (n.get("label") or n.get("claim", ""))[:70].replace("\\n", " ")
        body.append(f"- **{kind}** — {lab}"
                    + (f". {n['detail']}" if n.get("detail") else ""))
    if c.get("note"):
        body += ["", c["note"]]
    return ('<details class="work">\n<summary>' + head + "\n\n"
            + "\n".join(body) + "\n\n</details>\n")


def main(argv):
    d, nodes, claims = load()
    bad = validate(nodes, claims)
    for b in bad:
        log("  " + b)
    if bad:
        log(f"\n{len(bad)} problem(s) — refusing to write a page with a broken graph")
        return 1
    log(f"  {len(nodes)} nodes, {len(claims)} claims, no cycles")
    if "--check" in argv:
        return 0

    o = []
    def w(s=""):
        o.append(s)
    w("# What each claim rests on")
    w()
    w("*Generated by `scripts/claims.py` from `data/manual/claims.json`. The graph")
    w("is checked for cycles before this page is written: a cycle in a claim graph")
    w("is circular reasoning, and the generator refuses to produce a page containing")
    w("one.*")
    w()
    w("Prose hides dependency. *The surface diurnal amplitude is below half a")
    w("milligram* reads like a measurement. It is a bound, derived from a synthetic")
    w("recovery run on a real sampling schedule, under a stipulated signal shape and")
    w("a noise model — four kinds of thing, one of which is not data at all. The")
    w("sentence cannot show you that. A graph can.")
    w()
    w("### How to read the shapes")
    w()
    w("| shape | kind | what it means for the claim above it |")
    w("|---|---|---|")
    w("| cylinder, blue | **held** | a dataset on disk, with whatever faults [DATA_SOURCES.md](DATA_SOURCES.md) records |")
    w("| cylinder, purple | **external** | somebody else's published number, taken as input |")
    w("| hexagon, red dashed | **gap** | data that exists and we cannot reach, or that nobody has measured. A claim resting on one of these is a statement about ignorance |")
    w("| flag, amber | **synthetic** | generated to test the method. Licenses claims about the *instrument*, never about the world |")
    w("| rhombus, amber dashed | **assumption** | stipulated rather than measured. **The claim is void if it is wrong** |")
    w("| box, grey | **script** | the code that does the work |")
    w("| rounded, green | **claim** | a statement on a page, which may rest on other claims |")
    w()
    w("---")
    w()
    by_page = {}
    for cid, c in claims.items():
        by_page.setdefault(c.get("page", "—"), []).append((cid, c))
    for page in sorted(by_page):
        w(f"## {page}")
        w()
        for cid, c in by_page[page]:
            w(f"### {c['claim']}")
            w()
            w(f"`{cid}` · **{c['kind']}** — {KIND_NOTE.get(c['kind'], '')}")
            w()
            w(graph_for(cid, nodes, claims))
            w()
            for r in c["rests_on"]:
                n = nodes.get(r) or claims.get(r)
                if not n:
                    continue
                kind = n.get("kind", "claim")
                lab = (n.get("label") or n.get("claim", ""))[:80].replace("\\n", " ")
                w(f"- **{kind}** — {lab}"
                  + (f". {n['detail']}" if n.get("detail") else ""))
            if c.get("note"):
                w()
                w(f"> {c['note']}")
            w()
    w("---")
    w()
    w("## What is missing from this register")
    w()
    w("It covers the claims this project has examined, not every sentence it has")
    w("written. A claim absent from here is not endorsed by its absence — it simply")
    w("has not been put through this yet, and that is the honest state of it.")
    w()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(o).rstrip("\n") + "\n")
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
