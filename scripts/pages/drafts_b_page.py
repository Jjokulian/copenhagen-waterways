"""Shared by the generators of the hypothesis drafts and open problems (fork drafts-b).

A draft's prose lives in its generator as a template with the claims register's
placeholders - {fig:}, {calc:}, {was:…@@…}, {param:}, {ref:}, {chem:} - resolved here
against the register and its fragments, then written through write_doc(), which
refuses anything left unchecked.

Two kinds of number appear in these pages, and the difference is the point:
counts of files held in this repository are read live ({fig:} over
data/derived/drafts_b_counts.json and data/derived/enums.json); counts an earlier
session made from external sources are quotations of the draft as it was committed
({was:COMMIT:FILE:phrase with @@}) - located references: the value is read out of
git at the phrase's slot when the page is built, never typed, and not re-derived.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import claims
import live
from common import ROOT, log, write_doc


def render(rel, text):
    """Resolve the template and write the page; 1 if the compiler refuses it."""
    try:
        d, _, _ = claims.load()
        out, _ = claims.resolve(d, text, {})
        write_doc(os.path.join(ROOT, rel), out)
    except (claims.Refused, live.Unjustified) as e:
        log(str(e))
        return 1
    log(f"wrote {rel}")
    return 0
