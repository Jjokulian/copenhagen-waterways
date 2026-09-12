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

# A slot is a promise: put THIS file here in THIS shape and the named scripts
# will use it. Only sources with a slot can be handed in mechanically; the rest
# are documented so that someone who holds them knows what would be worth the
# trouble of making one. What each slot would unlock, and who holds it, is page
# text: cmd_doc() writes it as checked claims (data/manual/claims.d/w3-dq.json).
SLOTS = {
    "SPILDEVANDSDATA": {
        "file": "overflow_measured.csv",
        "shape": "one row per overflow event: outfall_id;lon;lat;start;end;volume_m3;"
                 "rain_mm  (semicolon or comma, header required, ISO timestamps)",
        "consumers": [],
    },
    "PULS": {
        "file": "puls_pointsources.csv",
        "shape": "one row per point source per year: cvr;name;lon;lat;year;"
                 "n_kg;p_kg;bod_kg;type",
        "consumers": [],
    },
    "DK-DRAENKORT-AU": {
        "file": "draenede_arealer.tif",
        "shape": "GeoTIFF, EPSG:25832, one band, drained=1 / not=0 or a "
                 "probability in 0-1",
        "consumers": [],
    },
    "CVR-BULK": {
        "file": "cvr_bulk.jsonl",
        "shape": "one JSON object per line, must carry cvr and one of "
                 "{name, industrycode, kommune}",
        "consumers": [],
    },
    "ODA-MFS-FISK": {
        "file": "oda_mfs_biota.csv",
        "shape": "the ODA extract as downloaded - semicolon separated, "
                 "ISO-8859-1, Parameter and Enhed columns preserved",
        "consumers": [],
    },
    "LER": {
        "file": "ler_ledninger.geojson",
        "shape": "GeoJSON, EPSG:25832, LineString per pipe with at least "
                 "{diameter_mm, material, invert_start_m, invert_end_m, type} "
                 "where type distinguishes faelles / spildevand / regnvand",
        "consumers": [],
    },
    "UTILITY-HYDRAULIC-MODEL": {
        "file": "sewer_model_results.csv",
        "shape": "one row per node or outfall per timestep: node_id;lon;lat;"
                 "time;flow_m3s;depth_m;overflow_m3",
        "consumers": [],
    },
    "SLURRY-CONTRACTS": {
        "file": "slurry_agreements.csv",
        "shape": "supplier_cvr;receiver_cvr;year;tonnes;n_kg;p_kg  (a receiving "
                 "parcel id instead of receiver_cvr is more useful still)",
        "consumers": [],
    },
    "DEFENCE-BATHYMETRY": {
        "file": "bathymetry_hires.tif",
        "shape": "GeoTIFF, EPSG:25832, one band of depth in metres, negative "
                 "down; any grid finer than the public depth model, DDM",
        "consumers": [],
    },
    "FIELD-SHEETS-CLOCK": {
        "file": "ctd_visit_times.csv",
        "shape": "station;date;time_utc  - one row per cast",
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


def _reading(sid, value, phrase):
    """A number read from a pinned document, refused unless the pinned copy holds the
    phrase (tags set aside and entities read, as the claims register compares it).
    Each reading gets its own phrase: two readings with one phrase would share an id."""
    import claims as _claims
    d = _claims.load()[0]
    if _claims._flat(phrase) not in _claims._flat(_claims.pin_text(d, sid)):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    return live._mk(value, ["reading", sid, "phrase", phrase, _claims._meta(d, sid)])


def cmd_doc():
    """Write docs/IF_YOU_HAVE_THE_DATA.md. Every number comes through live.py, and every
    assertion is a checked claim registered in data/manual/claims.d/w3-dq.json with what
    it rests on (LIVE_NUMBERS.md section 11). What the page once said and could not
    justify is in docs/ARCHIVE.md, not here."""
    from fetch_queue import FILES
    rows = gated_sources()
    J = lambda name: live.live_json(os.path.join(DERIVED, name))
    meta, en, tri = J("meta_facts.json"), J("enums.json"), J("triage.json")
    q = J("fetch_queue.json")
    pigs = J("socialcontext.json")["types"]["pigs"]
    cs = J("depth_clock.json")["clock_source"]
    if meta["gated_sources"] != len(rows) or meta["gated_slots"] != len(SLOTS):
        raise SystemExit("data/derived/meta_facts.json is stale against the register "
                         "- run scripts/meta_facts.py first")
    gated = q["by_tier"]["held"] + q["by_tier"]["account"] + q["by_tier"]["blocked"]
    if gated != len(rows):
        raise SystemExit("data/derived/fetch_queue.json is stale against the register "
                         "- run scripts/fetch_queue.py first")
    # where each slot is filed in the register - read here, never typed, and the
    # sentences that name a tier refuse to stand once it has moved
    tier_of = {s["id"]: classify(s)[0] for s in load()}
    open_slots = [sid for sid in SLOTS if tier_of.get(sid) == "open"]
    loose_slots = [sid for sid in SLOTS if sid not in tier_of]
    for sid, t in (("SPILDEVANDSDATA", "open"), ("DK-DRAENKORT-AU", "blocked")):
        if tier_of.get(sid) != t:
            raise SystemExit(f"the page says {sid} is in the {t} tier and it no longer is "
                             "- reword its slot")
    C = live.claim
    files = " and ".join(f"`{f}`" for f in FILES)
    ler_hours = _reading("LER-GRAVE", 2, "Ledningsejere har 2 timer til at besvare din søgning")
    drain_res = _reading("KP-DRAENKORT-DCA135", 30.4,
                         "Kortet har en opløsning på 30,4 x 30,4 meter")
    drain_acc = _reading("KP-DRAENKORT-DCA135", 79, "og en nøjagtighed på 79%")

    PAGE = {
        "SPILDEVANDSDATA": {
            "unlocks": C("C-DQ-S-OVERFLOW", "Overflow measured event by event. The register's "
                         "entry under this id is the public spildevandsdata extract, which gives "
                         "one annual volume and one annual event count per outfall, with no "
                         "per-event dates or durations, and which the fetch queue puts in its "
                         "open tier."),
            "who": C("C-DQ-W-OVERFLOW", "Not found for Copenhagen. The register's only "
                     "per-event overflow entry is Nyborg Forsyning's telemetry, which it treats "
                     "as request-only; the open extracts are annual, and PULS is closed."),
        },
        "PULS": {
            "unlocks": C("C-DQ-S-PULS", "The point-source register itself, per source and year. "
                         "The source register records it as not public and names its public "
                         "extracts, `MILJOEGIS-RBU-SAML` and `SPILDEVANDSDATA`."),
            "who": C("C-DQ-W-PULS", "Miljoestyrelsen and Danmarks Miljøportal, the custodians "
                     "the register records; DP02 puts the system's operation and support with "
                     "Danmarks Miljøportal."),
        },
        "DK-DRAENKORT-AU": {
            "unlocks": C("C-DQ-S-DRAIN", "Which agricultural land is drained, as a map: the "
                         "national map gives the probable extent of drained and undrained land "
                         f"at a resolution of {drain_res} m, with an accuracy of {drain_acc}%, "
                         "and a layer of the probability of drainage.") + " " +
                       C("C-DQ-S-DRAIN-ROUTE", "The register has not located a route to the "
                         "raster, and with no access text recorded, the fetch queue counts it "
                         "as blocked."),
            "who": C("C-DQ-W-DRAIN", "Aarhus Universitet, DCA, which made it for "
                     "Miljoestyrelsen, as the register records; where the raster is "
                     "distributed was not found."),
        },
        "CVR-BULK": {
            "unlocks": C("C-DQ-S-CVR", "Turning a CVR number into who and where, for the "
                         "manure surplus join. The sibling project danish-livestock holds CVR "
                         "records for part of it; the bulk register would complete it."),
            "who": C("C-DQ-W-CVR", "Not recorded: the source register has no entry for it, so "
                     "how the bulk register is reached, and on what terms, is not on file."),
        },
        "ODA-MFS-FISK": {
            "unlocks": C("C-DQ-S-MFS", "Contaminants measured in fish tissue: the ODA topic "
                         "*MFS i biota / Fisk*, for the hypotheses the register names below."),
            "who": C("C-DQ-W-MFS", "Possibly this project: the register lists the topic behind "
                     "a registration and a scripted extract, as for the ODA topics already "
                     "fetched with this project's login, and it has not been fetched."),
        },
        "LER": {
            "unlocks": C("C-DQ-S-LER", "Pipe geometry and connectivity for the Copenhagen "
                         "sewer. None of the open sources in [DATA_SOURCES.md](DATA_SOURCES.md) "
                         "gives surveyed invert levels for it, and a hydraulic model of the "
                         "network needs them. Whether LER's answers carry diameters and invert "
                         "levels was not found."),
            "who": C("C-DQ-W-LER", "The line owners, who answer an inquiry made through LER. "
                     f"LER's page for excavators gives them {ler_hours} hours to answer, and "
                     "digging waits until all of them have."),
            "permission": C("C-DQ-P-LER", "An inquiry to LER is a dig inquiry, made before "
                            "digging. This project plans no dig and does not query LER. LER's "
                            "site also lists access for authorities and researchers "
                            "(*Myndigheds- og forskeradgang*), whose terms this project has not "
                            "read. Whether a given access covers hydraulic analysis is the "
                            "holder's question, not this project's."),
        },
        "UTILITY-HYDRAULIC-MODEL": {
            "unlocks": C("C-DQ-S-HYDRO", "A calibrated model's results for Copenhagen's "
                         "network: flow, depth and overflow per node and time step. This project "
                         "makes no spill prediction of its own to set beside them; DP02 "
                         "calibrates such a model on measurement at the structure."),
            "who": C("C-DQ-W-HYDRO", "Not recorded: the source register has no entry for it. "
                     "DP02 says the structure data such a model needs should be derivable from "
                     "the utilities' pipe records."),
        },
        "SLURRY-CONTRACTS": {
            "unlocks": C("C-DQ-S-SLURRY", f"Where the manure from the {pigs['n_landless']:,} "
                         f"landless pig holdings - {pigs['landless_de']:,.0f} animal units - "
                         "actually goes. It leaves the farm by contract, and the contracts are "
                         "in no public register, so the nitrogen is attributed to a holding "
                         "that never spread it."),
            "who": C("C-DQ-W-SLURRY", "The parties to the contracts, which are in no register "
                     "this project could find."),
        },
        "DEFENCE-BATHYMETRY": {
            "unlocks": C("C-DQ-S-BATHY", "Bed morphology finer than the public depth model, "
                         "`DDM`, which the register records as a single current-state grid "
                         "with the per-survey dates and accuracies composited away."),
            "who": C("C-DQ-W-BATHY", "Not recorded: the register has no entry for the surveys "
                     "the public model is composited from. Its custodian is "
                     "Klimadatastyrelsen, the Danish Hydrographic Office."),
        },
        "FIELD-SHEETS-CLOCK": {
            "unlocks": C("C-DQ-S-CLOCK", "A clock on oxygen at depth. The water-chemistry "
                         "topic carries a clock value on every genuine row; CTD has no clock "
                         f"field, so its {en['ctd']['rows'] / 1e6:.1f}M readings have a date "
                         f"and no hour. `scripts/depth_clock.py` places {cs['borrowed']:,} CTD "
                         "oxygen measurements with the observed clock of a same-day "
                         "water-chemistry visit, counted after its quality filters; "
                         f"{cs['none']:,} rows have no such clock to borrow, counted before "
                         "them, so the two are not shares of one whole. The field sheets would "
                         "time the casts directly and check the borrowing."),
            "who": C("C-DQ-W-CLOCK", "DCE, or whoever holds the original cruise logs"),
            "consumer": C("C-DQ-S-CONSUMER", "**Read by `scripts/depth_clock.py`.** It runs "
                          "today on the borrowed clock; when this file is present its times "
                          "take precedence, and the offset between them and the borrowed clock "
                          "is measured wherever a station-day has both, so the borrowing is "
                          "checked rather than trusted."),
        },
    }
    if set(PAGE) != set(SLOTS) or any(bool(PAGE[s].get("consumer")) != bool(SLOTS[s]["consumers"])
                                      for s in SLOTS):
        raise SystemExit("the page's slot texts no longer match SLOTS - write the missing ones")

    out = []

    def w(s=""):
        out.append(s)
    w("# If you have data access we don't")
    w()
    w("## The three states, of which this page is one")
    w()
    w(C("C-DQ-U-STATES", "This page sorts what the project could use into three states. An "
        "analysis written against the data on hand is worth only what that data is worth; one "
        "written against a stated file shape runs on whatever arrives in that shape."))
    w()
    w("| state | meaning | where it lives |")
    w("|---|---|---|")
    w("| **wanted** | nobody has measured it, anywhere. The measurement has to be invented or "
      "funded before the question is answerable at all. | [EXPERIMENTS.md](EXPERIMENTS.md), "
      "and " + C("C-DQ-U-UNSCORE", f"the {tri['classes']['unscoreable']['n']} hypotheses "
                 "marked *unscoreable* in [hypodrafts/TRIAGE.md](hypodrafts/TRIAGE.md)") + " |")
    w("| **gated** | it exists, and sits behind a credential, a registration or a closed "
      "door. | **this page** |")
    w("| **held** | on disk, with whatever faults it has. | everything else on this site, and "
      "the fault list in [DATA_SOURCES.md](DATA_SOURCES.md) |")
    w()
    w(C("C-DQ-U-WRITTEN", "Where a slot has a script that reads it, better input gives a better "
        "answer without anyone rewriting an argument: `scripts/depth_clock.py` reads the CTD "
        "visit-time slot when a file is there, and counts the measurements each clock placed. "
        "The other slots fix a file shape so that the analysis can be written against "
        "something real."))
    w()
    w("---")
    w()
    w(C("C-DQ-U-GENERATED", f"*Generated by `scripts/unlock.py` from {files} and the slots "
        "the script defines.*") + " *Do not hand-edit.*")
    w()
    w(C("C-DQ-U-CREDS", "This project runs on what can be fetched openly and with the "
        "credentials its fetch scripts read from this machine, which [the fetch "
        "queue](DATA_QUEUE.md) lists.") + " " +
      C("C-DQ-U-HOLD", "Some of what it cannot answer waits on data that exists and is "
        "**gated**: if you hold a utility login, a field sheet, a drainage archive or a service "
        "agreement, you may be able to supply it."))
    w()
    w(C("C-DQ-U-NOCODE", "**You do not have to write any code, and you do not have to send "
        "anything to anyone.**") + " Clone the repository, put your file in `data/dropin/` "
      "under the name given below, and run:")
    w()
    w("```sh")
    w("python3 scripts/unlock.py          # validates it, then runs what it unblocks")
    w("```")
    w()
    w(C("C-DQ-U-RUNS", "The file stays on your machine. `unlock.py` checks its shape, runs the "
        "scripts that read that slot, and rewrites this page; the pages that read what those "
        "scripts write change when the site is rebuilt."))
    w()
    w(C("C-DQ-U-LOCAL", "**Nothing is transmitted, and nothing here decides what you may use.** "
        "The file is read on your machine and is never committed or uploaded — which is a "
        "materially different act from sending a dataset to anyone.") + " " +
      C("C-DQ-U-PERMISSION", "What this page records is that a given dataset *would answer* a "
        "given question, and in what shape. Whether your access permits that use is a legal "
        "question belonging to you, or to whoever granted it; it is not settled here and this "
        "project is not in a position to settle it."))
    w()
    w(C("C-DQ-U-WHYLISTED", "That distinction is why entries appear below that this project "
        "could never use itself, including registers provisioned for an entirely different "
        "purpose. What a register was built for does not determine what it is useful for. "
        "Leaving such an entry out would hide the question from the only people who can answer "
        "it — a holder deciding whether their access covers this, or a lawmaker deciding "
        "whether it should."))
    w()
    w("---")
    w()
    w("## 1. Slots — hand these in mechanically")
    w()
    consumed = [f"`{sl['file']}`" for sl in SLOTS.values() if sl["consumers"]]
    w(C("C-DQ-U-SLOTS", "Each slot has a fixed file name and a fixed shape, so an analysis can "
        "be written against it before anyone has the file. Today only " + " and ".join(consumed)
        + (" has" if len(consumed) == 1 else " have") + " such an analysis, marked below; for "
        "the others the slot exists so the data can arrive before the analysis is written.")
      + " " + C("C-DQ-U-HYPLIST", "Where a slot is filed under a register entry the fetch "
                "queue does not class as open, the hypotheses the entry names are listed with "
                "it."))
    w()
    for sid, sl in SLOTS.items():
        src = next((s for _, _, s in rows if s["id"] == sid), None)
        pt = PAGE[sid]
        w(f"### `{sl['file']}` — {sid}")
        w()
        w(f"**Unlocks.** {pt['unlocks']}")
        w()
        w(f"**Shape.** `{sl['shape']}`")
        w()
        w(f"**Who holds it.** {pt['who']}")
        if pt.get("permission"):
            w()
            w(f"**Permission.** {pt['permission']}")
        if src and src.get("hypotheses"):
            w()
            w(f"**Hypotheses waiting on it.** {' '.join(ref(h) for h in src['hypotheses'])}")
        if pt.get("consumer"):
            w()
            w(pt["consumer"])
        w()
    w("---")
    w()
    w("## 2. Everything else the register classifies as gated")
    w()
    w(C("C-DQ-U-TABLE", f"Every entry of {files} that the fetch queue does not class as open, "
        "ordered by tier, then by how many hypotheses the entry names, with every hypothesis "
        "it names.") + " " +
      C("C-DQ-U-TIERS", "*Held* means behind a credential this project holds, and some of "
        "those topics are already on disk; *account* means a registration, an account, a login "
        "or a token the fetch queue does not count as held; *blocked* means the access text "
        "says it is closed or unverified, or matches no tier word."))
    w()
    w("| tier | source | serves | what it is |")
    w("|---|---|---|---|")
    for tier, cred, s in rows:
        hyp = " ".join(ref(h) for h in (s.get("hypotheses") or [])) or "—"
        nm = ident(s["name"].replace("|", "/")[:90])
        mark = " **[slot]**" if s["id"] in SLOTS else ""
        w(f"| `{tier}` | **{ident(s['id'])}**{mark} | {hyp} | {nm} |")
    w()
    tail = []
    if loose_slots:
        tail.append("no register entry")
    if open_slots:
        tail.append("an entry in the open tier (" + ", ".join(f"`{x}`" for x in open_slots)
                    + ")")
    w(C("C-DQ-U-COUNT", f"**{gated} entries are not classed open.** The ones a slot is filed "
        "under are marked **[slot]**" + ("; the other slots match " + " or ".join(tail)
                                          if tail else "") + "."))
    w()
    w(C("C-DQ-U-ADD", "If you hold one of the others and it is worth a slot, the shape is "
        "cheap to add - the cost is agreeing what the file should look like, not writing the "
        "reader."))
    w()
    try:
        write_doc(DOC, "\n".join(out).rstrip("\n") + "\n")
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(DOC, ROOT)} ({len(rows)} gated sources, {len(SLOTS)} slots)")
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
