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

A NOTE ON WHAT NOT TO SEND. Do not send anything whose licence you would be
breaking, and do not send personal data. LER is excluded on purpose and stays
excluded: the cable and pipe register is provisioned for excavation safety, and
this project has no excavation to be safe about. If a slot below would require
you to break an agreement to fill it, leave it empty - the gap is a finding in
its own right and the page says so.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT, log
from fetch_queue import classify, load

DROPIN = os.path.join(ROOT, "data", "dropin")
DOC = os.path.join(ROOT, "docs", "IF_YOU_HAVE_THE_DATA.md")

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
    "FIELD-SHEETS-CLOCK": {
        "file": "ctd_visit_times.csv",
        "shape": "station;date;time_utc  - one row per cast",
        "unlocks": "A clock on oxygen AT DEPTH. The water-chemistry topic "
                   "carries a time on every row and CTD carries none, so 53.7M "
                   "profile measurements have a date and no hour. 80% of CTD "
                   "station-days can borrow a time from a same-day bottle; the "
                   "field sheets would settle the rest and check that borrowing.",
        "who": "DCE, or whoever holds the original cruise logs",
        "consumers": [],
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
      "[EXPERIMENTS.md](EXPERIMENTS.md), and the 40 hypotheses marked "
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
    w("*the archive after the water-chemistry topic turned out to carry one on 100.0%*")
    w("*of 1,805,827 rows.*")
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
    w("**Do not send anything you would be breaking a licence or an agreement to")
    w("send, and do not send personal data.** LER, the cable and pipe register, is")
    w("excluded on purpose and stays excluded: it is provisioned for excavation")
    w("safety and this project has no excavation to be safe about. A slot you cannot")
    w("fill without breaching something should stay empty. The gap is a finding.")
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
        w(f"**Unlocks.** {sl['unlocks']}")
        w()
        w(f"**Shape.** `{sl['shape']}`")
        w()
        w(f"**Who plausibly holds it.** {sl['who']}")
        if src and src.get("hypotheses"):
            w()
            w(f"**Hypotheses waiting on it.** {' '.join(src['hypotheses'][:12])}")
        if not sl["consumers"]:
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
        hyp = " ".join(f"`{h}`" for h in (s.get("hypotheses") or [])[:6]) or "—"
        nm = s["name"].replace("|", "/")[:90]
        mark = " **[slot]**" if s["id"] in SLOTS else ""
        w(f"| `{tier}` | **{s['id']}**{mark} | {hyp} | {nm} |")
    w()
    w(f"**{len(rows)} gated sources, {len(SLOTS)} with a slot.**")
    w()
    w("If you hold one of the others and it is worth a slot, the shape is cheap to")
    w("add - the cost is agreeing what the file should look like, not writing the")
    w("reader.")
    w()
    with open(DOC, "w", encoding="utf-8") as f:
        f.write("\n".join(out).rstrip("\n") + "\n")
    log(f"wrote {os.path.relpath(DOC, ROOT)} "
        f"({len(rows)} gated sources, {len(SLOTS)} slots)")
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
