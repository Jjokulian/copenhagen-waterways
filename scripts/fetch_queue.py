#!/usr/bin/env python3
"""Turn the source register into a queue you can actually work through.

data_sources.json records what exists. It does not say what to do on Monday. The
access field is free text written by whoever verified the source, which is right
for a record and useless for a work plan, so this classifies it into four tiers and
sorts by what would move the most hypotheses.

    open        fetch it now, no account, no permission
    held        gated, but this project already holds the credential
    account     a free registration stands between us and it
    blocked     not public, request-only, FOI, or unverified

The tiers are ordered by friction, not by value. A blocked source can matter more
than an open one - the queue says so in the notes rather than hiding it by sorting
it last.

"Unlocks" counts hypotheses in the register that name this source and have no
open-tier alternative. It is a crude priority signal and it is meant to be: the
point is to stop the register being a list of things nobody fetched.

THE RESOLUTION RULE, which this file also enforces.

Nothing is stored at an administrative unit. Not per water body, not per catchment,
not per municipality, not per sub-basin. Everything is carried at the resolution it
was actually taken: a position, a time, and where it exists a depth.

This is not fastidiousness. This project spent a page establishing that a "water
body" explains 7.9% of the variation in the one variable Denmark measures densely
enough to check, and that two stations inside one share about four percent of their
year-to-year variance. Loading a source that has already been summed into those
polygons would import the assumption straight back, and every result computed on it
would inherit a unit we had just shown is not a unit.

So each source is flagged by whether its spatial index is a *measurement position*
or an *administrative region*. The region ones are still worth having - they are
often the only version that exists - but they enter as somebody's aggregate of a
measurement, labelled as such, and never as the measurement.

What a water body actually is, if it is anything, is then a question to be answered
from the data rather than assumed by the schema: put the observations on the map
with their own coordinates and times, see which of them move together, and check
each proxy against an unrelated one. The administrative polygon becomes an overlay
to be tested against, not a container to pour things into.

Output: data/derived/fetch_queue.json, docs/DATA_QUEUE.md

Usage:  python3 scripts/fetch_queue.py
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, MANUAL, ROOT, log, read_json, write_json, write_doc
import live

OUT = os.path.join(ROOT, "docs", "DATA_QUEUE.md")
BAD_REFS = []       # hypothesis ids a source names that the register does not hold


def ident(text):
    """A source id or name with digits in it carries an identifier - a product
    version, a map scale in a title, an expedition number - not a quantity. Each
    such token is shown as code, so it is neither read as a number nor mistaken
    for one."""
    return " ".join(f"`{t}`" if live.bare_numbers(t) else t for t in text.split(" "))


def ref(h):
    """A hypothesis a source serves, as a checked reference; an id the register
    does not hold is shown as code and counted, not silently linked."""
    try:
        return live.ref(h)
    except Exception:
        BAD_REFS.append(h)
        return f"`{h}`"
FILES = ["data_sources.json", "data_sources_2.json"]

# Credentials this project already has working. A source behind one of these is
# not blocked, it is queued.
HELD = {
    "oda": ("ODA / Overfladevandsdatabasen", "email login, scripted SOAP extract "
            "working in scripts/oda_client.py"),
    "dataforsyningen": ("Dataforsyningen", "API token on this machine, orthophoto "
                        "WMS verified"),
}

# Spatial index words that mean "somebody already aggregated this for you".
ADMIN_UNIT = ("polygon", "water body", "waterbody", "vandomr", "reference",
              "sub-basin", "subbasin", "basin", "catchment", "opland",
              "municipality", "kommune", "region", "national", "country",
              "ices rectangle", "rectangle", "c-square", "csquare", "per port",
              "landing port", "agglomeration", "area-level", "per farm",
              "per permit", "per facility", "named facility", "per klapplads")
POINT_UNIT = ("point", "coordinate", "lat", "utm", "per station", "per cast",
              "per haul", "per grab", "per observation", "per sample", "transect",
              "grid", "cell", "m grid", "raster")


TIERS = [
    ("open", "Fetch it now", "No account, no permission, no negotiation."),
    ("held", "Gated, but we hold the key",
     "Behind a login this project already has working."),
    ("account", "One free registration away",
     "A form and an email address. Nothing is being withheld; it just has not been "
     "done."),
    ("blocked", "Not open",
     "Request-only, FOI, institutional provisioning, or unverified. These are the "
     "ones worth arguing about publicly, because for several of them the "
     "measurement exists and the public cannot see it."),
]


def spatial_kind(src):
    """Is this indexed by a place something was measured, or by a region?

    A region-indexed source is somebody's aggregate. It can still be the only thing
    that exists, and it is still worth fetching - but it must not be mistaken for a
    measurement, because the unit it was summed into is exactly the unit this
    project has shown is not coherent."""
    t = " ".join(str(src.get(k) or "") for k in ("spatial", "aggregation")).lower()
    admin = any(w in t for w in ADMIN_UNIT)
    point = any(w in t for w in POINT_UNIT)
    if point and not admin:
        return "position"
    if admin and not point:
        return "region"
    if admin and point:
        return "mixed"
    return "unknown"


def classify(src):
    a = (src.get("access") or "").lower()
    sid = (src.get("id") or "").lower()
    name = (src.get("name") or "").lower()
    if sid.startswith("oda") or "odaforalle" in (src.get("url") or "").lower() \
            or name.startswith("oda -") or "already working in this project" in a:
        return "held", "oda"
    if "dataforsyning" in a or "dataforsyning" in name:
        return "held", "dataforsyningen"
    if any(k in a for k in ("not public", "request only", "request-only", "foi",
                            "aktindsigt", "provisioned through")):
        return "blocked", None
    if any(k in a for k in ("unverified", "no bulk download", "no open download",
                            "no programmatic", "api layer unreachable",
                            "download mechanics")):
        return "blocked", None
    if any(k in a for k in ("registration", "free account", "login", "api token",
                            "cds account", "account required")):
        return "account", None
    if any(k in a for k in ("open", "no key", "no login", "no auth", "direct get",
                            "direct download", "cc-by", "cc by")):
        return "open", None
    return "blocked", None


def load():
    out, seen = [], set()
    for fn in FILES:
        p = os.path.join(MANUAL, fn)
        if not os.path.exists(p):
            log(f"  {fn}: not present yet, skipped")
            continue
        d = read_json(p)
        n = 0
        for s in d.get("sources") or []:
            if s.get("id") in seen:
                continue
            seen.add(s.get("id"))
            s["_file"] = fn
            out.append(s)
            n += 1
        log(f"  {fn}: {n} sources")
    return out


def main():
    srcs = load()
    if not srcs:
        log("no source register found")
        return 1
    for s in srcs:
        s["_tier"], s["_cred"] = classify(s)
        s["_spatial"] = spatial_kind(s)

    # a hypothesis is "unlocked" by a source only if nothing easier already serves it
    easiest = {}
    order = {t: i for i, (t, _, _) in enumerate(TIERS)}
    for s in srcs:
        for h in s.get("hypotheses") or []:
            if h not in easiest or order[s["_tier"]] < order[easiest[h]]:
                easiest[h] = s["_tier"]
    for s in srcs:
        s["_unlocks"] = sorted(h for h in (s.get("hypotheses") or [])
                               if easiest.get(h) == s["_tier"])

    by = collections.defaultdict(list)
    for s in srcs:
        by[s["_tier"]].append(s)
    for v in by.values():
        v.sort(key=lambda s: (-len(s["_unlocks"]), s["id"]))

    write_json(os.path.join(DERIVED, "fetch_queue.json"),
               {"n_sources": len(srcs),
                "by_tier": {t: len(by[t]) for t, _, _ in TIERS},
                "by_spatial": {k: sum(1 for s in srcs if s["_spatial"] == k)
                               for k in ("position", "region", "mixed", "unknown")},
                "tiers": [{"id": t, "label": l, "what": w} for t, l, w in TIERS],
                "credentials_held": {k: {"name": n, "how": h}
                                     for k, (n, h) in HELD.items()},
                "queue": [{"id": s["id"], "tier": s["_tier"],
                           "credential": s["_cred"], "name": s.get("name"),
                           "custodian": s.get("custodian"), "url": s.get("url"),
                           "hypotheses": s.get("hypotheses"),
                           "unlocks": s["_unlocks"], "temporal": s.get("temporal"),
                           "spatial": s.get("spatial"), "coverage": s.get("coverage"),
                           "past_2012": s.get("past_2012"), "size": s.get("size"),
                           "spatial_kind": s["_spatial"],
                           "access": s.get("access"), "caveat": s.get("caveat")}
                          for t, _, _ in TIERS for s in by[t]]})

    o = []
    a = o.append
    a("# The fetch queue\n")
    a("The source register records what exists. It does not say what to do on "
      "Monday. This is the same information sorted by friction: what can be "
      "downloaded now, what is behind a credential we already hold, what needs a "
      "free registration nobody has done, and what is genuinely closed.\n")
    # the counts are read back from the file just written, so each is a checked number
    q = live.live_json(os.path.join(DERIVED, "fetch_queue.json"))
    obs = live.live_json(os.path.join(DERIVED, "observing.json"))
    a(f"**{q['n_sources']} sources.** *Unlocks* counts hypotheses that this source "
      "serves and that nothing easier serves — a crude priority signal, and meant "
      "to be.\n")
    a("| tier | | sources |")
    a("|---|---|---:|")
    for t, label, _ in TIERS:
        a(f"| `{t}` | {label} | {q['by_tier'][t]} |")
    a("")
    for k, (n, h) in HELD.items():
        a(f"- **{n}** — {h}")
    a("")

    for t, label, what in TIERS:
        rows = by[t]
        if not rows:
            continue
        a(f"## {label} — {q['by_tier'][t]}\n")
        a(f"*{what}*\n")
        a("| source | unlocks | indexed by | what it is |")
        a("|---|---|---|---|")
        MARK = {"position": "position", "region": "**region**", "mixed": "mixed",
                "unknown": "?"}
        for s in rows:
            u = " ".join(ref(h) for h in s["_unlocks"]) or "—"
            a(f"| **{ident(s['id'])}** | {u} | {MARK[s['_spatial']]} "
              f"| {ident((s.get('name') or '')[:88])} |")
        a("")

    a("## The resolution rule\n")
    kinds = collections.Counter(s["_spatial"] for s in srcs)
    a("Nothing here is stored at an administrative unit — not per water body, not "
      "per catchment, not per municipality, not per sub-basin. Everything is "
      "carried at the resolution it was taken: a position, a time, and where it "
      "exists a depth.\n")
    a("That is not fastidiousness. [OBSERVING.md](OBSERVING.md) establishes that a "
      f"water body explains **{obs['variance']['share_between_wb'] * 100:.1f}%** of the "
      "variation in the one variable Denmark "
      "measures densely enough to check, and that two stations inside one share "
      "about four percent of their year-to-year variance. A source already summed "
      "into those polygons would carry the assumption straight back in, and "
      "everything computed from it would inherit a unit we had just shown is not "
      "one.\n")
    a("| indexed by | sources | |")
    a("|---|---:|---|")
    kinds = q["by_spatial"]
    a(f"| position | {kinds['position']} | a place something was measured |")
    a(f"| **region** | {kinds['region']} | somebody's aggregate; usable, but never "
      f"as a measurement |")
    a(f"| mixed | {kinds['mixed']} | carries both; take the position field |")
    a(f"| ? | {kinds['unknown']} | not stated clearly enough to tell |")
    a("")
    a("The region-indexed sources are often the only version that exists, and "
      "several matter a great deal — the monthly nutrient input series is per "
      "marine reference polygon, and there is no per-outfall alternative. They "
      "enter the panel labelled as somebody's aggregate of a measurement, and never "
      "as the measurement.\n")
    a("> **What a water body actually is, if it is anything, is a question to be "
      "answered from the data rather than assumed by the schema.** Put the "
      "observations on the map with their own coordinates and times, see which move "
      "together, and check every proxy against an unrelated one. The administrative "
      "polygon is then an overlay to be tested against — not a container to pour "
      "things into.\n")

    a("## What this does not tell you\n")
    a("Friction is not value. Several entries in the last tier matter more than "
      "anything in the first — per-event overflow volumes, monthly trawling effort, "
      "and marine phytoplankton species counts are each closed, and each of them "
      "would settle a hypothesis that currently cannot be ranked at all. The tiers "
      "say what is easy, and the register says what is important; they are "
      "different questions and this page is only the first one.\n")
    write_doc(OUT, "\n".join(o) + "\n")
    log(f"\nwrote docs/DATA_QUEUE.md ({os.path.getsize(OUT):,} chars)")
    if BAD_REFS:
        log(f"  {len(set(BAD_REFS))} hypothesis id(s) named by a source and absent from "
            f"the register, shown as code: {' '.join(sorted(set(BAD_REFS)))}")
    for t, label, _ in TIERS:
        log(f"  {t:9} {len(by[t]):>3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
