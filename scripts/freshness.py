#!/usr/bin/env python3
"""A build graph over content hashes: what is stale, what was hand-edited, in what order to rerun.

A published number was wrong for two days and no rule this project had would have
caught it. docs/FLOOD_GAP.md is generated, nobody hand-edited it, and the
generator was correct. Its INPUT changed - the Noerrebro sheet was re-registered -
and the three scripts reading that georeferencing were never rerun. The site went
on saying 5.932 km2 when the figure was 5.847, and 53.5% when it was 50.1%, which
is the difference between the city having planned a surface route for MOST of the
flood path and for HALF of it.

Making every page generated does not fix that: the stale page already was. Moving
prose into Python does not fix it: a number typed into a string literal is
equally stale wherever it is written. What fixes it is knowing which files each
script eats and produces, and noticing when a thing it ate has changed since.

WHY HASHES AND NOT TIMESTAMPS. The first version of this file compared mtimes and
immediately reported three stale steps, two of which were a git checkout touching
files that had not changed. A check that cries wolf gets ignored, which is how
check_generated.py's warning came to be read as "do not regenerate". Content
hashes do not move when nothing moved, and they DO move when a file is rewritten
with an older timestamp.

TWO KINDS OF PROBLEM, kept apart because the remedies are opposite:

  STALE       an input's content differs from what it was when the output was
              last built. The output no longer follows from its data. Rerun.

  HAND-EDITED an output's content differs from what the generator last wrote.
              Someone edited a generated file, and rerunning will DESTROY that
              edit. Move the text into the generator first, then rerun.

Confusing those two is the exact error that let the flood figures rot: "your
output is stale" and "you are about to lose work" were reported in the same
words, and the cautious response to the second is the wrong response to the
first.

    python3 scripts/freshness.py           what is stale, what was hand-edited
    python3 scripts/freshness.py --fix     rerun stale steps, in dependency order
    python3 scripts/freshness.py --accept  record the current state as built
    python3 scripts/freshness.py --list    the manifest and its coverage

WHAT IT CANNOT SEE. A dependency nobody declared. The manifest is hand-written,
so a script whose inputs are unlisted is never reported stale, and the failure
mode is silence rather than a wrong answer. --list prints the coverage for that
reason.
"""
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import ROOT, log, read_json, load_build

MANIFEST = os.path.join(ROOT, "data", "manual", "build.json")
LOCK = os.path.join(ROOT, "data", "derived", "build.lock.json")
CHUNK = 1 << 20


def digest(rel):
    """sha256 of a file's content, or None if it is not there."""
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_lock():
    if os.path.exists(LOCK):
        try:
            return json.load(open(LOCK, encoding="utf-8"))
        except ValueError:
            pass
    return {"_what": "Content hashes as of the last accepted build. Written by "
                     "scripts/freshness.py; not hand-maintained.", "steps": {}}


def save_lock(lock):
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    with open(LOCK, "w", encoding="utf-8") as f:
        json.dump(lock, f, indent=1, sort_keys=True)
        f.write("\n")


def order(steps):
    """Topological: a step producing what another eats runs first.

    Cycles are reported rather than resolved - a build graph that feeds itself is
    the same defect as a claim that rests on itself, and guessing an order would
    hide it."""
    produced = {}
    for s in steps:
        for o in s["outputs"]:
            produced[o] = s["script"]
    by = {s["script"]: s for s in steps}
    deps = {s["script"]: {produced[i] for i in s["inputs"]
                          if i in produced and produced[i] != s["script"]}
            for s in steps}
    out, seen, stack = [], set(), set()

    def walk(n):
        if n in seen:
            return
        if n in stack:
            raise RuntimeError("build graph has a cycle at " + n)
        stack.add(n)
        for d in sorted(deps.get(n, ())):
            walk(d)
        stack.discard(n)
        seen.add(n)
        out.append(n)

    for s in steps:
        walk(s["script"])
    return [by[n] for n in out], deps


def status(steps, lock):
    stale, rebuilt, edited, unbuilt, ok = [], [], [], [], []
    for s in steps:
        rec = lock["steps"].get(s["script"])
        ins = {p: digest(p) for p in list(s["inputs"]) + [s["script"]]}
        outs = {p: digest(p) for p in s["outputs"]}
        if rec is None or any(v is None for v in outs.values()):
            unbuilt.append((s, [p for p, v in outs.items() if v is None]))
            continue
        moved = [p for p, v in ins.items() if rec["inputs"].get(p) != v]
        touched = [p for p, v in outs.items() if rec["outputs"].get(p) != v]
        # Three different states, and conflating them is the error this file
        # exists to prevent. Input AND output both moved: somebody reran the
        # generator without --accept, and calling that a hand-edit is a false
        # alarm of exactly the kind that trains a reader to ignore the check.
        # Output moved and input did not: nothing but a person could have done
        # that, and rerunning would destroy it.
        if moved and touched:
            rebuilt.append((s, touched))
        elif moved:
            stale.append((s, moved))
        elif touched:
            edited.append((s, touched))
        else:
            ok.append(s)
    return stale, rebuilt, edited, unbuilt, ok


def record(lock, s):
    lock["steps"][s["script"]] = {
        "inputs": {p: digest(p) for p in list(s["inputs"]) + [s["script"]]},
        "outputs": {p: digest(p) for p in s["outputs"]},
    }


def main(argv):
    steps = load_build()["steps"]          # build.json and its fragments in build.d/
    try:
        steps, deps = order(steps)
    except RuntimeError as e:
        log("  " + str(e))
        return 2
    lock = load_lock()

    if "--list" in argv:
        covered = set()
        for s in steps:
            log(f"  {s['script']}")
            for i in s["inputs"]:
                log(f"      eats  {i}")
            for o in s["outputs"]:
                log(f"      makes {o}")
                covered.add(o)
        log(f"\n  {len(steps)} step(s) in dependency order, "
            f"{len(covered)} declared output(s)")
        log("  Anything not listed is invisible to this check.")
        return 0

    if "--accept" in argv:
        for s in steps:
            record(lock, s)
        save_lock(lock)
        log(f"  recorded {len(steps)} step(s) as built")
        return 0

    stale, rebuilt, edited, unbuilt, ok = status(steps, lock)
    for s, outs in unbuilt:
        log(f"  NEVER BUILT  {s['script']} -> {', '.join(outs) or '(no record)'}")
    for s, outs in edited:
        log(f"  HAND-EDITED  {', '.join(outs)}")
        log(f"               differs from what {s['script']} last wrote. "
            "Rerunning DESTROYS that edit -")
        log("               move the text into the generator first.")
    for s, outs in rebuilt:
        log(f"  REBUILT      {s['script']} was rerun since the last accepted "
            "build - --accept records it, --fix reruns it to be certain")
    for s, moved in stale:
        log(f"  STALE        {s['script']}")
        log(f"               its input changed: {', '.join(moved[:3])}"
            + (f" (+{len(moved)-3} more)" if len(moved) > 3 else ""))
    if not stale and not rebuilt and not edited and not unbuilt:
        log(f"  every declared output follows from its inputs ({len(ok)} step(s))")
        return 0

    if "--fix" in argv:
        if edited:
            log("\n  refusing to rerun while a generated file carries a hand-edit: "
                "that is the one case where rerunning loses work")
            return 1
        # a rebuilt step is rerun too: it costs a run and makes the state certain,
        # where --accept would be taking the rerun on trust
        todo = ({s["script"] for s, _ in stale} | {s["script"] for s, _ in rebuilt}
                | {s["script"] for s, _ in unbuilt})
        # anything downstream of a rebuilt step is stale too, by construction
        changed = True
        while changed:
            changed = False
            for s in steps:
                if s["script"] in todo:
                    continue
                if deps.get(s["script"], set()) & todo:
                    todo.add(s["script"])
                    changed = True
        for s in steps:                       # already topologically ordered
            if s["script"] not in todo:
                continue
            log(f"\n  rerunning {s['script']}")
            # a step may need a subcommand ("currents.py report"): "args" in its entry
            r = subprocess.run([sys.executable, os.path.join(ROOT, s["script"])] + list(s.get("args", [])),
                               cwd=ROOT)
            if r.returncode != 0:
                log(f"  {s['script']} exited {r.returncode} - stopping")
                save_lock(lock)
                return 2
            record(lock, s)
        save_lock(lock)
        log("\n  rebuilt in dependency order; check the diff before committing")
        return 0

    log("\n  --fix reruns the stale ones in dependency order. An output behind "
        "its data is a published number that no longer follows from it.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
