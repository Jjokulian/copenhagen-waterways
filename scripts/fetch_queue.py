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
    does not hold is shown as code and counted, not silently linked. The source
    registers serve the hypotheses of data/derived/hypotheses.json, so an id two
    families share (T1-T5 are also terminal outcomes) is the hypothesis."""
    import refs
    try:
        if h in refs.entries() and refs.ambiguous(h):
            return live.ref(h, family="hypotheses")
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

    # The page. Every assertion on it is a checked claim, registered with what it
    # rests on in data/manual/claims.d/w3-dq.json (LIVE_NUMBERS.md section 11), and
    # every count is read back from the file just written. What it once said and
    # could not justify is in docs/ARCHIVE.md, not here.
    C = live.claim
    q = live.live_json(os.path.join(DERIVED, "fetch_queue.json"))
    obs = live.live_json(os.path.join(DERIVED, "observing.json"))
    if set(HELD) != {"oda", "dataforsyningen"}:
        raise SystemExit("HELD has changed: rewrite the page's list of held credentials")
    read = " and ".join(f"`{f}`" for f in FILES)
    unread = sorted(f for f in os.listdir(MANUAL)
                    if f.startswith("data_sources") and f.endswith(".json") and f not in FILES)
    # entries behind credentials the fetch scripts use but HELD does not name
    cop = [(s["id"], s["_tier"]) for s in srcs if s["id"].startswith(("CMEMS-", "CDSE-"))]
    o = []
    a = o.append
    a("# The fetch queue\n")
    a(C("C-DQ-Q-PURPOSE", "The source register records what exists; this page sorts its "
        "entries by friction: what can be downloaded now, what sits behind a credential this "
        "project holds, what needs a registration it has not made, and what the register's "
        "access text does not show to be reachable.") + "\n")
    count = f"**{q['n_sources']} sources**, from {read}."
    if unread:
        names = " and ".join(f"`{f}`" for f in unread)
        count += (f" {names}, also part of the register, "
                  + ("is" if len(unread) == 1 else "are") + " not read by this queue, so "
                  + ("its" if len(unread) == 1 else "their") + " entries are in none of the "
                  "tiers below.")
    a(C("C-DQ-Q-COUNT", count) + " " +
      C("C-DQ-Q-UNLOCKS", "*Unlocks* lists the hypotheses an entry names that no entry in an "
        "easier tier also names — a crude priority signal, and meant to be.") + "\n")
    a(C("C-DQ-Q-TIERS", "Each entry's tier is read from its access text by keyword, in this "
        "order: an ODA topic, or a source that names Dataforsyningen, is *held*; words for not "
        "public, request-only, FOI, provisioning, unverified or no download make it *blocked*; "
        "words for a registration, an account, a login or a token make it *account*; words for "
        "an open or key-free download make it *open*; and an entry that matches none of these "
        "is counted as *blocked*. Because the account words are tested before the open ones, "
        "an access text saying that no login or no registration is needed is counted as "
        "*account*. The tiers have not been checked by hand entry by entry, and the note under "
        "the credentials shows where they go wrong for the Copernicus entries.") + "\n")
    a("| tier | | sources |")
    a("|---|---|---:|")
    for t, label, _ in TIERS:
        a(f"| `{t}` | {label} | {q['by_tier'][t]} |")
    a("")
    a("The credentials the queue counts as held:\n")
    a("- " + C("C-DQ-Q-ODA", "**ODA / Overfladevandsdatabasen** — an email login, and a "
               "scripted SOAP extract in `scripts/oda_client.py`"))
    a("- " + C("C-DQ-Q-DF", "**Dataforsyningen** — an API token, which "
               "`scripts/terraincheck.py` reads to fetch the national elevation model"))
    a("")
    parts = []
    for t in ("open", "account", "blocked"):
        ids = sorted(i for i, tt in cop if tt == t)
        if ids:
            parts.append(" ".join(f"`{i}`" for i in ids) + f" as *{t}*")
    if parts:
        a(C("C-DQ-Q-UNCOUNTED", "The queue counts only these as held. This project's fetch "
            "scripts also read Copernicus Data Space client credentials "
            "(`scripts/fetch_satellite.py`) and Copernicus Marine credentials "
            "(`scripts/fetch_cmems.py`) from this machine, so the Copernicus entries are "
            "counted in tiers that say otherwise: " + "; ".join(parts) + ".") + "\n")
    a(C("C-DQ-Q-ROWS", "In each tier below, entries are ordered by how many hypotheses they "
        "unlock. *Indexed by* is read from the entry's spatial and aggregation text by keyword: "
        "a position, a **region**, both (*mixed*), or `?` where neither matched. *What it is* "
        "is the entry's name, shortened where long.") + "\n")
    DESC = {
        "open": C("C-DQ-Q-OPEN", "*The access text reads as open — an open or direct "
                  "download, a service asking no key or authentication, or an open licence — "
                  "and names nothing that puts it in another tier.*"),
        "held": C("C-DQ-Q-HELD", "*An ODA topic, or a service behind the Dataforsyningen "
                  "token: behind a credential this project holds. Some are already on disk: "
                  "the ODA extracts `kemi`, `ctd`, `lys` and `maaledybde`.*"),
        "account": C("C-DQ-Q-ACCOUNT", "*The access text names a registration, an account, "
                     "a login or a token that the queue does not count as held.*"),
        "blocked": C("C-DQ-Q-BLOCKED", "*The access text says not public, request-only, FOI, "
                     "provisioned, unverified or without a download — or matches no tier word "
                     "at all. Entries recording data confirmed not to exist are here too.*")
                   + " " + C("C-DQ-Q-PULSCLOSED", "`PULS` is one whose data exists and is "
                             "closed: the register records it as not public, reached through "
                             "an organisation's IT coordinator."),
    }
    MARK = {"position": "position", "region": "**region**", "mixed": "mixed",
            "unknown": "?"}
    for t, label, _ in TIERS:
        rows = by[t]
        if not rows:
            continue
        a(f"## {label} — {q['by_tier'][t]}\n")
        a(DESC[t] + "\n")
        a("| source | unlocks | indexed by | what it is |")
        a("|---|---|---|---|")
        for s in rows:
            u = " ".join(ref(h) for h in s["_unlocks"]) or "—"
            a(f"| **{ident(s['id'])}** | {u} | {MARK[s['_spatial']]} "
              f"| {ident((s.get('name') or '')[:88])} |")
        a("")

    a("## The resolution rule\n")
    a(C("C-DQ-Q-RULE", "The rule: a source is carried at the resolution it was taken — a "
        "position, a time, and where it exists a depth — and not at an administrative unit "
        "such as a water body, a catchment, a municipality or a sub-basin. This page flags each "
        "source by what it is indexed by; it does not enforce the rule.") + "\n")
    wb = obs["variance"]["share_between_wb"] * 100
    mr = obs["internal"]["mean_r"]
    a(C("C-DQ-Q-WHY", "The reason is in [OBSERVING.md](OBSERVING.md): in bathing-water "
        "quality at stations with a long record, once the national year-to-year swing is "
        f"removed, variation between water bodies is **{wb:.1f}%** of the whole, and between "
        f"two stations in the same water body {mr * mr * 100:.1f}% of the wobble in one is "
        "shared with the other. A source already summed into those polygons would carry the "
        "unit back in, and everything computed from it would inherit it.") + "\n")
    kinds = q["by_spatial"]
    a(C("C-DQ-Q-INDEX", "Counted by that keyword reading of each entry's spatial and "
        "aggregation text; `?` means the text matched no keyword, not that the source has no "
        "index.") + "\n")
    a("| indexed by | sources |")
    a("|---|---:|")
    a(f"| position | {kinds['position']} |")
    a(f"| **region** | {kinds['region']} |")
    a(f"| mixed | {kinds['mixed']} |")
    a(f"| ? | {kinds['unknown']} |")
    a("")
    a(C("C-DQ-Q-TILF", "A region-indexed source can still be the one to fetch: the monthly "
        "nutrient input to the sea, `ODA-TILFOERSEL`, is given per marine reference polygon, "
        "and the register records the stream stations behind it as available separately, in "
        "`ODA-STOFTRANSPORT`.") + " " +
      C("C-DQ-Q-AGG", "Under the rule such a source is used as somebody's aggregate of a "
        "measurement, never as the measurement.") + "\n")
    a("> " + C("C-DQ-Q-WB", "**What a water body actually is, if it is anything, is a question "
               "to be answered from the data rather than assumed by the schema.** Put the "
               "observations on the map with their own coordinates and times, see which move "
               "together, and check every proxy against an unrelated one. The administrative "
               "polygon is then an overlay to be tested against — not a container to pour "
               "things into.") + "\n")

    a("## What this does not tell you\n")
    a(C("C-DQ-Q-VALUE", "Friction is not value. The tiers say what is easy to reach, and each "
        "register entry's hypotheses say what it would serve; they are different questions, "
        "and this page answers only the first.") + "\n")
    try:
        write_doc(OUT, "\n".join(o) + "\n")
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"\nwrote docs/DATA_QUEUE.md ({os.path.getsize(OUT):,} chars)")
    if BAD_REFS:
        log(f"  {len(set(BAD_REFS))} hypothesis id(s) named by a source and absent from "
            f"the register, shown as code: {' '.join(sorted(set(BAD_REFS)))}")
    for t, label, _ in TIERS:
        log(f"  {t:9} {len(by[t]):>3}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
