"""Shared by the generators of the hypothesis drafts (fork drafts-a).

A draft's prose lives in its generator as one text with claims-register
placeholders - {ref:ID}, {chem:KEY}, {fig:name}, {calc:...}, {param:name},
{read:SRC:shown|phrase} - plus one shorthand:

    {q:a phrase from the committed page with @@ where the value stands}

a located quotation of the page as committed at COMMITS[page], expanded to
{was:COMMIT:docs/hypodrafts/PAGE.md:phrase with @@}: the value is read out of
`git show` at build time, never typed here. What this site once said is not a
justification for saying it again, so the compiler accepts such a quotation only
inside a historical claim - the archive of retired claims, docs/ARCHIVE.md -
and refuses it on a page. A number nothing in the repository stores is not
printed: it is computed and stored, read from a pinned document, or retired.
No draft uses {q:} now. A {q:} without @@ is a typed copy and is refused.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from common import ROOT, log, write_doc
import claims
import live

Q = re.compile(r"\{q:([^{}]+)\}")
# The committed text each page's locators point into. Pinned, because once the
# generated page is itself committed its latest commit holds rendered links, not
# the words the locators were written against.
COMMITS = {
    "docs/hypodrafts/A1.md": "c601feb",
    "docs/hypodrafts/A1b.md": "ac84f5b",
    "docs/hypodrafts/AUDIT.md": "7c4dd30",
    "docs/hypodrafts/B1.md": "444fc74",
    "docs/hypodrafts/C1.md": "c601feb",
    "docs/hypodrafts/C4.md": "c601feb",
    "docs/hypodrafts/C6.md": "680eccf",
    "docs/hypodrafts/F3.md": "c601feb",
}


def RD(sid, shown, phrase):
    """A {read:} placeholder: the number `shown`, located by `phrase` in pin `sid`."""
    return "{read:%s:%s|%s}" % (sid, shown, phrase)


def reading(d, sid, shown, phrase, value):
    """A number read out of a pinned document, as a live value that can take part
    in arithmetic. It is checked exactly as {read:} is - the phrase must be in the
    pin and state the number shown - and `value` must be that number."""
    try:
        claims.resolve(d, RD(sid, shown, phrase), {})
    except claims.Refused as e:
        raise live.Unjustified(str(e))
    if re.sub(r"\D", "", shown) != re.sub(r"\D", "", str(value)):
        raise live.Unjustified(f"reading {sid}: the value {value} is not the {shown} the pin states")
    return live.reading_value(sid, "phrase", phrase, value, claims._meta(d, sid))


def commit_of(rel):
    r = subprocess.run(["git", "log", "-1", "--format=%h", "--", rel], cwd=ROOT,
                       capture_output=True, text=True)
    c = r.stdout.strip()
    if not c:
        raise SystemExit(f"{rel} has no committed version to quote")
    return c


def build(rel, text, commit=None):
    """Resolve and write one draft page. Returns the number of self-quotations."""
    commit = commit or COMMITS.get(rel) or commit_of(rel)
    typed = [m.group(1) for m in Q.finditer(text) if live.SLOT not in m.group(1)]
    if typed:
        log(f"  {rel}: {len(typed)} typed quotation(s), e.g. {typed[:3]} - a quotation is a "
            f"located reference: write {{q:phrase with {live.SLOT} where the value stands}}")
        return None
    n_quotes = len(Q.findall(text))
    text = Q.sub(lambda m: "{was:" + commit + ":" + rel + ":" + m.group(1) + "}", text)
    if n_quotes:
        head, _, rest = text.partition("\n")
        text = (head + "\n\n*Numbers shown as quotations are carried from this page as committed "
                f"at `{commit}`: nothing in the repository stores them yet, so each says what "
                "the page said, not that it was re-derived.*\n" + rest)
    d, _, _ = claims.load()
    try:
        out = claims.resolve(d, text, {})[0]
    except claims.Refused as e:
        log(f"  {rel}: {e}")
        return None
    try:
        write_doc(os.path.join(ROOT, rel), out)
    except live.Unjustified as e:
        log(str(e))
        return None
    log(f"wrote {rel} ({n_quotes} numbers carried as quotations of {commit})")
    return n_quotes
