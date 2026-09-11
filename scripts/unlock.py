#!/usr/bin/env python3
"""What this project cannot reach, and how to hand it in if you can.

The project runs on open data from a machine with no institutional credentials.
A large part of what it cannot answer is not hard - it is gated. Somebody with a
utility login, a field sheet, a drainage archive or a service agreement can
unblock in an afternoon what this cannot unblock at all.

This is the handover mechanism, and it has two halves.

DOCUMENTED. Every source the register classifies as gated - account-tier, held
behind a credential, or outright blocked - is listed with what it would unlock,
who plausibly holds it, and the exact file this project would accept in its
place. Generated from data/manual/data_sources*.json, so it cannot drift out of
date the way a hand-written list does: docs/IF_YOU_HAVE_THE_DATA.md said for
weeks that ODA vandkemi was the top blocker after it had been fetched, and that
no clock time existed in the archive when the water-chemistry topic carries one
on 100.0% of 1.8 million rows.

DROPPABLE. Each gated source has a slot under data/dropin/. Put the file there
under the stated name, run this script, and the analyses that were waiting on it
run and appear. Nothing about the repository changes; nothing is uploaded
anywhere; the file stays on your machine. The pattern already worked once by
accident - NITROGEN.md section 2c had been written for months and rendered
silently the moment data/derived/manure.json first existed - and this makes it
deliberate and checkable rather than a coincidence of file existence.

    python3 scripts/unlock.py --list        what is gated, and the slot for each
    python3 scripts/unlock.py --check       validate what is already dropped in
    python3 scripts/unlock.py               validate, then run what is unblocked
    python3 scripts/unlock.py --doc         rewrite docs/IF_YOU_HAVE_THE_DATA.md

WHAT THIS DOES AND DOES NOT DECIDE. This file documents what data would answer
which question, and in what shape. It does not decide whether anybody may use it
for that. Those are different questions and they belong to different people: the
utility of a dataset is a technical fact about the topic, and permission is a
legal matter for whoever holds the access.

An earlier version of this script left the cable and pipe register out on the
grounds that it is provisioned for excavation safety and this project has no
excavation. That was the wrong call. What a register was BUILT for does not
determine what it is USEFUL for, and pre-emptively deleting the entry hides the
question from the only people who could answer it - a holder deciding whether
their access covers this, or a lawmaker deciding whether it should. So the slot
is documented, the analysis it would unlock is stated, and the permission
question is named as the holder's rather than settled here.

Nothing is transmitted. The file goes in a gitignored directory on the machine
running the code, is read locally, and is never committed or uploaded. That is a
materially different act from sending a dataset to anyone, and the earlier
version overstated the risk by writing as though it were not.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, ROOT, log, write_doc
from fetch_queue import BAD_REFS, classify, ident, load, ref
import live

DROPIN = os.path.join(ROOT, "data", "dropin")
DOC = os.path.join(ROOT, "docs", "IF_YOU_HAVE_THE_DATA.md")
PAGE = "docs/IF_YOU_HAVE_THE_DATA.md"
THEN = "fb90951"        # the page as it stood before its numbers were checked

# A slot is a promise: put THIS file here in THIS shape and the named scripts
# will use it. Only sources with a slot can be handed in mechanically; the rest
# are documented so that someone who holds them knows what would be worth the
# trouble of making one.
SLOTS = {
    "SPILDEVANDSDATA": {
        "file": "overflow_measured.csv",
        "shape": "one row per overflow event: outfall_id;lon;lat;start;end;volume_m3;"
                 "rain_mm  (semicolon or comma, header required, ISO timestamps)",
        "unlocks": "Overflow as a measurement rather than a model. Every overflow "
                   "figure on this site is a registered or modelled volume; none "
                   "has been compared with a metered one.",
        "who": "HOFOR, BIOFOS and other utilities; Miljoestyrelsen through PULS",
        "consumers": [],
    },
    "PULS": {
        "file": "puls_pointsources.csv",
        "shape": "one row per point source per year: cvr;name;lon;lat;year;"
                 "n_kg;p_kg;bod_kg;type",
        "unlocks": "Point-source load beside the diffuse residual, at the "
                   "resolution the residual is computed against.",
        "who": "Miljoestyrelsen",
        "consumers": [],
    },
    "DK-DRAENKORT-AU": {
        "file": "draenede_arealer.tif",
        "shape": "GeoTIFF, EPSG:25832, one band, drained=1 / not=0 or a "
                 "probability in 0-1. The published product is 30.4 m.",
        "unlocks": "The surface-versus-drain routing fraction as a mapped "
                   "quantity instead of a single national dial. Tile-drained "
                   "land bypasses the riparian zone and most of the "
                   "denitrification, so this is the term between field surplus "
                   "and delivered load.",
        "who": "Aarhus Universitet DCA; Miljoestyrelsen; Danmarks Arealinformation",
        "consumers": [],
    },
    "CVR-BULK": {
        "file": "cvr_bulk.jsonl",
        "shape": "one JSON object per line, must carry cvr and one of "
                 "{name, industrycode, kommune}",
        "unlocks": "Turning a CVR number into who and where, for the manure "
                   "surplus join. The sibling project danish-livestock holds a "
                   "14,222-row subset; the bulk register would complete it.",
        "who": "Erhvervsstyrelsen agreement, or a working Datafordeler subscription",
        "consumers": [],
    },
    "ODA-MFS-FISK": {
        "file": "oda_mfs_biota.csv",
        "shape": "the ODA extract as downloaded - semicolon separated, "
                 "ISO-8859-1, Parameter and Enhed columns preserved",
        "unlocks": "Marine toxicant loading, currently unscoreable: 7 "
                   "hypotheses turn on whether contaminants rather than "
                   "nutrients gate recovery.",
        "who": "anyone with an ODA login and the MFS topics enabled",
        "consumers": [],
    },
    "LER": {
        "file": "ler_ledninger.geojson",
        "shape": "GeoJSON, EPSG:25832, LineString per pipe with at least "
                 "{diameter_mm, material, invert_start_m, invert_end_m, type} "
                 "where type distinguishes faelles / spildevand / regnvand",
        "unlocks": "A real hydraulic model of the Copenhagen sewer instead of a "
                   "catchment-level spill estimate. Without pipe geometry and "
                   "connectivity, overflow can be predicted as whether and "
                   "roughly how much, never as when within an event - and the "
                   "timing is where the flush dynamic lives.",
        "who": "Ledningsejerregistret; the utilities that own the lines; "
               "Klimadatastyrelsen provisions access",
        "permission": "Provisioned for excavation safety. Whether a given "
                      "access covers hydraulic analysis is the holder's "
                      "question, not this project's - it is recorded here "
                      "because the data would answer the question, which is a "
                      "separate fact from whether anyone may ask it that way.",
        "consumers": [],
    },
    "UTILITY-HYDRAULIC-MODEL": {
        "file": "sewer_model_results.csv",
        "shape": "one row per node or outfall per timestep: node_id;lon;lat;"
                 "time;flow_m3s;depth_m;overflow_m3",
        "unlocks": "The comparison this project cannot make: its own predicted "
                   "spill against a calibrated commercial model of the same "
                   "network. Agreement would validate a method that needs no "
                   "pipe data; disagreement would localise exactly where "
                   "topography stops being enough.",
        "who": "HOFOR, BIOFOS and the consultancies that built the models",
        "consumers": [],
    },
    "SLURRY-CONTRACTS": {
        "file": "slurry_agreements.csv",
        "shape": "supplier_cvr;receiver_cvr;year;tonnes;n_kg;p_kg  (a receiving "
                 "parcel id instead of receiver_cvr is more useful still)",
        "unlocks": "Where the manure from the 581 landless pig holdings - "
                   "406,192 animal units - actually goes. It leaves the farm by "
                   "contract, and the contracts are in no public register, so "
                   "the nitrogen is attributed to a holding that never spread "
                   "it.",
        "who": "Landbrugsstyrelsen; the parties to the agreements",
        "consumers": [],
    },
    "DEFENCE-BATHYMETRY": {
        "file": "bathymetry_hires.tif",
        "shape": "GeoTIFF, EPSG:25832, one band of depth in metres, negative "
                 "down; any grid finer than the 50 m public model is useful",
        "unlocks": "Bed morphology at the scale that decides where "
                   "resuspension and sulphidic sediment actually sit. The "
                   "public depth model is too coarse to separate a trawled "
                   "furrow from a natural hollow.",
        "who": "Soevaernet and the national hydrographic survey; some holdings "
               "are restricted",
        "permission": "Some of this is restricted for reasons that have nothing "
                      "to do with the environment. Recorded because it is "
                      "useful, not because it is available.",
        "consumers": [],
    },
    "FIELD-SHEETS-CLOCK": {
        "file": "ctd_visit_times.csv",
        "shape": "station;date;time_utc  - one row per cast",
        "unlocks": "A clock on oxygen AT DEPTH. The water-chemistry topic "
                   "carries a time on every row and CTD carries none, so 53.7M "
                   "profile measurements have a date and no hour. Part of the CTD "
                   "record can borrow a time from a same-day bottle whose clock is "
                   "observed; the field sheets would settle the rest and check "
                   "that borrowing.",
        "who": "DCE, or whoever holds the original cruise logs",
        "consumers": ["scripts/depth_clock.py"],
    },
}


def slot_path(sid):
    return os.path.join(DROPIN, SLOTS[sid]["file"])


def validate(sid):
    """Return (ok, message). Cheap structural checks only - the point is to tell
    someone their file is in the right shape before they wonder why nothing
    happened, not to certify its contents."""
    p = slot_path(sid)
    if not os.path.exists(p):
        return None, "not present"
    n = os.path.getsize(p)
    if n == 0:
        return False, "present but empty"
    ext = os.path.splitext(p)[1].lower()
    try:
        if ext in (".csv", ".tsv"):
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                head = f.readline().strip()
            if not head or (";" not in head and "," not in head):
                return False, "no delimited header row found"
            return True, f"{n/1e6:.1f} MB, header: {head[:70]}"
        if ext == ".jsonl":
            with open(p, "r", encoding="utf-8", errors="replace") as f:
                json.loads(f.readline())
            return True, f"{n/1e6:.1f} MB, first line parses as JSON"
        if ext == ".tif":
            with open(p, "rb") as f:
                magic = f.read(4)
            if magic[:2] not in (b"II", b"MM"):
                return False, "not a TIFF (bad magic bytes)"
            return True, f"{n/1e6:.1f} MB, TIFF"
        return True, f"{n/1e6:.1f} MB"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def gated_sources():
    """Every source the register does not consider open, with its tier."""
    out = []
    for s in load():
        tier, cred = classify(s)
        if tier == "open":
            continue
        out.append((tier, cred, s))
    order = {"held": 0, "account": 1, "blocked": 2}
    out.sort(key=lambda x: (order.get(x[0], 3), -len(x[2].get("hypotheses") or []),
                            x[2]["id"]))
    return out


def cmd_list():
    log("Gated sources, and the slot each would be handed in through.\n")
    for tier, cred, s in gated_sources():
        sid = s["id"]
        mark = "  [SLOT]" if sid in SLOTS else ""
        log(f"{tier.upper():<8} {sid}{mark}")
        log(f"    {s['name'][:88]}")
        if s.get("hypotheses"):
            log(f"    unlocks: {' '.join(s['hypotheses'][:10])}")
        if sid in SLOTS:
            sl = SLOTS[sid]
            ok, msg = validate(sid)
            state = {None: "empty", True: "PRESENT, valid", False: "PRESENT, INVALID"}[ok]
            log(f"    drop at: data/dropin/{sl['file']}   [{state}: {msg}]")
    log(f"\n{len(SLOTS)} slot(s) defined; put files in {os.path.relpath(DROPIN, ROOT)}/")
    return 0


def cmd_check(run=False):
    os.makedirs(DROPIN, exist_ok=True)
    present, invalid = [], []
    for sid in SLOTS:
        ok, msg = validate(sid)
        if ok is True:
            present.append((sid, msg))
        elif ok is False:
            invalid.append((sid, msg))
    for sid, msg in present:
        log(f"  OK       {sid:<22} {msg}")
    for sid, msg in invalid:
        log(f"  INVALID  {sid:<22} {msg}")
    if not present and not invalid:
        log("  nothing dropped in yet - see --list for the slots")
        return 0
    if not run:
        return 1 if invalid else 0
    ran = 0
    for sid, _ in present:
        for script in SLOTS[sid]["consumers"]:
            log(f"\n  running {script} for {sid}")
            r = subprocess.run([sys.executable, os.path.join(ROOT, script)],
                               cwd=ROOT)
            ran += 1
            if r.returncode != 0:
                log(f"  {script} exited {r.returncode}")
    if present and not ran:
        log("\n  Files are valid but no script consumes them yet. That is honest "
            "rather than broken: the slot exists so the data can arrive before "
            "the analysis is written, and the shape is fixed in advance so the "
            "analysis can be written against something real.")
    return 1 if invalid else 0


def cmd_doc():
    rows = gated_sources()
    # every number on the page comes through live.py; the counts of gated sources
    # and slots are stored by scripts/meta_facts.py, which must be current
    J = lambda name: live.live_json(os.path.join(DERIVED, name))
    meta, en, tri = J("meta_facts.json"), J("enums.json"), J("triage.json")
    pigs = J("socialcontext.json")["types"]["pigs"]
    cs = J("depth_clock.json")["clock_source"]
    if meta["gated_sources"] != len(rows) or meta["gated_slots"] != len(SLOTS):
        raise SystemExit("data/derived/meta_facts.json is stale against the register "
                         "- run scripts/meta_facts.py first")
    SELF = []           # numbers carried as quotations of this page's own committed text

    def sq(shown):
        SELF.append(shown)
        return live.was(THEN, PAGE, shown)

    kemi_rows = en["kemi"]["rows"]
    clock_pct = en["kemi"]["nonblank"]["Startklok"] / kemi_rows * 100
    FIG = {     # figures inside a slot's typed prose, and the checked entity each becomes
        "CVR-BULK": [("14,222", lambda: sq('holds a @@-row subset;'))],
        "ODA-MFS-FISK": [("7 hypotheses", lambda: sq('currently unscoreable: @@ hypotheses turn') + " hypotheses")],
        "SLURRY-CONTRACTS": [("581", lambda: f"{pigs['n_landless']:,}"),
                             ("406,192", lambda: f"{pigs['landless_de']:,.0f}")],
        "FIELD-SHEETS-CLOCK": [
            ("53.7M", lambda: f"{en['ctd']['rows'] / 1e6:.1f}M"),
            ("Part of the CTD record can borrow", lambda: (
                f"{cs['borrowed'] / (cs['borrowed'] + cs['none']) * 100:.0f}% of the CTD "
                "measurements the depth analysis keeps can borrow"))],
    }

    def slot_text(sid, text):
        for said, now in FIG.get(sid, []):
            if said in text:
                text = text.replace(said, now())
        return text

    a = [].append
    out = []
    def w(s=""):
        out.append(s)
    w("# If you have data access we don't")
    w()
    w("## The three states, of which this page is one")
    w()
    w("Every input this project could use is in one of three states, and the")
    w("system is written for all three rather than for the one it happens to have.")
    w("That ordering matters: an analysis written against the data on hand is worth")
    w("only what that data is worth, but an analysis written against a stated")
    w("contract runs on whatever arrives, and says what it could not do.")
    w()
    w("| state | meaning | where it lives |")
    w("|---|---|---|")
    w("| **wanted** | nobody has measured it, anywhere. The measurement has to be "
      "invented or funded before the question is answerable at all. | "
      f"[EXPERIMENTS.md](EXPERIMENTS.md), and the {tri['classes']['unscoreable']['n']} "
      "hypotheses marked "
      "*unscoreable* in [hypodrafts/TRIAGE.md](hypodrafts/TRIAGE.md) |")
    w("| **gated** | it exists, someone holds it, and this project cannot reach "
      "it. | **this page** |")
    w("| **held** | on disk, with whatever faults it has. | everything else on "
      "this site, and the fault list in "
      "[DATA_SOURCES.md](DATA_SOURCES.md) |")
    w()
    w("**What is published here is the degraded run of a system built for the")
    w("first column.** That is the claim worth arguing with. Not *this is what the")
    w("open data supports* - which invites the reply that the data is poor and the")
    w("conclusions are therefore soft - but *this is the analysis, here is the")
    w("contract it consumes, and here is what it currently has to eat.* Hand it")
    w("better input and the same code produces a better answer without anyone")
    w("rewriting an argument. Where the answer would change, it changes in public.")
    w()
    w("The pattern is not aspirational. Section 2c of [NITROGEN.md](NITROGEN.md)")
    w("had been written for months and rendered nothing, because the file it needed")
    w("did not exist; the day that file was first produced, the section appeared")
    w("with its numbers in it and no prose was written to make that happen.")
    w()
    w("---")
    w()
    w("*Generated by `scripts/unlock.py` from the source register. Do not hand-edit:*")
    w("*an earlier hand-written version of this page still named ODA `vandkemi` as the*")
    w("*top blocker after it had been fetched, and still said no clock time existed in*")
    w(f"*the archive after the water-chemistry topic turned out to carry one on {clock_pct:.1f}%*")
    w(f"*of {kemi_rows:,} rows.*")
    w()
    w("This project is run from open data by someone with no institutional")
    w("credentials. A large part of what it cannot answer is not hard - it is")
    w("**gated**. If you hold a utility login, a field sheet, a drainage archive or a")
    w("service agreement, you can unblock in an afternoon what this cannot unblock at")
    w("all.")
    w()
    w("**You do not have to write any code, and you do not have to send anything to")
    w("anyone.** Clone the repository, put your file in `data/dropin/` under the name")
    w("given below, and run:")
    w()
    w("```sh")
    w("python3 scripts/unlock.py          # validates it, then runs what it unblocks")
    w("```")
    w()
    w("The file stays on your machine. Nothing is uploaded. What changes is that the")
    w("pages regenerate with your data in them, and you can see whether it moves any")
    w("conclusion - which is the only thing worth knowing.")
    w()
    w("**Nothing is transmitted, and nothing here decides what you may use.** The")
    w("file is read on your machine and is never committed or uploaded — which is a")
    w("materially different act from sending a dataset to anyone. What this page")
    w("records is that a given dataset *would answer* a given question, and in what")
    w("shape. Whether your access permits that use is a legal question belonging to")
    w("you, or to whoever granted it; it is not settled here and this project is not")
    w("in a position to settle it.")
    w()
    w("That distinction is why entries appear below that this project could never")
    w("use itself, including registers provisioned for an entirely different")
    w("purpose. What a register was built for does not determine what it is useful")
    w("for. Leaving such an entry out would hide the question from the only people")
    w("who can answer it — a holder deciding whether their access covers this, or a")
    w("lawmaker deciding whether it should.")
    w()
    w("---")
    w()
    w("## 1. Slots — hand these in mechanically")
    w()
    w("Each of these has a fixed filename and a fixed shape, so the analysis can be")
    w("written against it before anyone has it.")
    w()
    for sid, sl in SLOTS.items():
        src = next((s for _, _, s in rows if s["id"] == sid), None)
        w(f"### `{sl['file']}` — {sid}")
        w()
        w(f"**Unlocks.** {slot_text(sid, sl['unlocks'])}")
        w()
        w(f"**Shape.** `{sl['shape']}`")
        w()
        w(f"**Who plausibly holds it.** {sl['who']}")
        if sl.get("permission"):
            w()
            w(f"**Permission.** {sl['permission']}")
        if src and src.get("hypotheses"):
            w()
            w(f"**Hypotheses waiting on it.** {' '.join(ref(h) for h in src['hypotheses'][:12])}")
        if sl["consumers"]:
            w()
            w("**The analysis is already written.** `" + "`, `".join(sl["consumers"])
              + "` runs today on the best clock available and will use yours the")
            w("moment the file is here - nobody has to write anything for your data")
            w("to be used, and you can see at once whether it changes the answer.")
        else:
            w()
            w("*No script consumes this yet.* The slot exists so the data can arrive")
            w("before the analysis is written - the shape is fixed in advance so the")
            w("analysis can be written against something real rather than imagined.")
        w()
    w("---")
    w()
    w("## 2. Everything else the register classifies as gated")
    w()
    w("Ordered by friction, then by how many hypotheses each serves. *Held* means a")
    w("credential this project already has and simply has not spent; *account* means a")
    w("free registration nobody has done; *blocked* means not open.")
    w()
    w("| tier | source | serves | what it is |")
    w("|---|---|---|---|")
    for tier, cred, s in rows:
        hyp = " ".join(ref(h) for h in (s.get("hypotheses") or [])[:6]) or "—"
        nm = ident(s["name"].replace("|", "/")[:90])
        mark = " **[slot]**" if s["id"] in SLOTS else ""
        w(f"| `{tier}` | **{ident(s['id'])}**{mark} | {hyp} | {nm} |")
    w()
    w(f"**{meta['gated_sources']} gated sources, {meta['gated_slots']} with a slot.**")
    w()
    w("If you hold one of the others and it is worth a slot, the shape is cheap to")
    w("add - the cost is agreeing what the file should look like, not writing the")
    w("reader.")
    w()
    write_doc(DOC, "\n".join(out).rstrip("\n") + "\n")
    log(f"wrote {os.path.relpath(DOC, ROOT)} "
        f"({len(rows)} gated sources, {len(SLOTS)} slots) - {len(SELF)} number(s) "
        "carried as self-quotation")
    if BAD_REFS:
        log(f"  {len(set(BAD_REFS))} hypothesis id(s) named by a source and absent from "
            f"the register, shown as code: {' '.join(sorted(set(BAD_REFS)))}")
    return 0


def main(argv):
    os.makedirs(DROPIN, exist_ok=True)
    if "--list" in argv:
        return cmd_list()
    if "--check" in argv:
        return cmd_check(run=False)
    if "--doc" in argv:
        return cmd_doc()
    rc = cmd_check(run=True)
    cmd_doc()
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
