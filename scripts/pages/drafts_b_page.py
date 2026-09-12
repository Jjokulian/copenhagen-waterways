"""Shared by the generators of the hypothesis drafts and open problems (fork drafts-b).

A draft's prose lives in its generator as a template with the claims register's
placeholders - {fig:}, {calc:}, {was:…@@…}, {param:}, {ref:}, {chem:} - resolved here
against the register and its fragments, then written through write_doc(), which
refuses anything left unchecked.

Numbers are read live ({fig:} over data/derived/drafts_b_counts.json,
data/derived/enums.json and the other stored results) or from pinned documents
({read:}). A quotation of the draft as it was once committed ({was:…@@…}) is not a
justification for printing a number again: the compiler accepts it only inside a
historical claim, in the archive of retired claims (docs/ARCHIVE.md). Counts an
earlier session made from external sources and never stored were retired there.
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
