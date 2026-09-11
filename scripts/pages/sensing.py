#!/usr/bin/env python3
"""Generate docs/SENSING.md - a dense network for the thing nobody measures.

A design page: sensor classes, stated price ranges, and the arithmetic of three
network sizes. None of its numbers comes from data this repository holds. Until the
owner rules on how stated design prices should be justified, every number is carried
as a quotation of the page's last committed text (PAGE0) - honest about what it is
("the site once said this"), circular as justification, and counted: the count is
logged on every build and reported by the conversion.

The prose below is the page. Edit it here; docs/SENSING.md is output.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import ROOT, log, write_doc
import live
import quote_locate

OUT = os.path.join(ROOT, "docs", "SENSING.md")
PAGE0 = "4469fc7"            # the last committed version of this page

# The page as last committed, read out of the history - not a copy kept here. Its
# numbers are carried as located quotations of that text (see carried()).
TEXT = live._git_text(PAGE0, "docs/SENSING.md")


def carried(text):
    """Every number the compiler would refuse, wrapped as a quotation of PAGE0, one
    at a time until none is left. Returns the text and how many were carried."""
    n = 0
    while True:
        view = live.MARK.sub(lambda m: f"[{m.group(2)}](SOURCES.md#{m.group(1)})", text)
        bad = live.bare_numbers(view)
        if not bad:
            return text, n
        ln, num, _ = bad[0]
        lines = text.split("\n")
        line = lines[ln - 1]
        spans = [(m.start(), m.end()) for m in live.MARK.finditer(line)]
        for m in re.finditer(re.escape(num), line):
            if any(a <= m.start() < b for a, b in spans):
                continue
            pre = line[m.start() - 1] if m.start() else " "
            post = line[m.end():m.end() + 2]
            if re.match(r"[\d.,]", pre) or re.match(r"\d|[.,]\d", post):
                continue
            loc = quote_locate.locate(PAGE0, "docs/SENSING.md", num,
                                      hints=live.strip_marks(line)[max(0, m.start() - 100):m.end() + 100])
            if not loc:
                raise RuntimeError(f"cannot locate {num} of line {ln} in the committed page")
            lines[ln - 1] = (line[:m.start()] + live.was(PAGE0, "docs/SENSING.md", loc)
                             + line[m.end():])
            n += 1
            break
        else:
            raise RuntimeError(f"cannot place {num} on line {ln}: {line[:80]}")
        text = "\n".join(lines)


def main():
    # names and identifiers are code, not quantities; a number inside a link's text
    # moves out of it, since a quotation is itself a link
    for old, new in (("5β-cholestan-3β-ol", "`5β-cholestan-3β-ol`"),
                     ("**24-ethylcoprostanol / coprostanol**", "**`24-ethylcoprostanol` / coprostanol**"),
                     ("Pig-2-Bac", "`Pig-2-Bac`"), ("ISO 7027", "`ISO 7027`"),
                     ("[49% measured and 51% modelled catchment area](NITROGEN.md)",
                      "49% measured and 51% modelled catchment area ([NITROGEN.md](NITROGEN.md))")):
        assert old in TEXT, old
    text = TEXT
    for old, new in (("5β-cholestan-3β-ol", "`5β-cholestan-3β-ol`"),
                     ("**24-ethylcoprostanol / coprostanol**", "**`24-ethylcoprostanol` / coprostanol**"),
                     ("Pig-2-Bac", "`Pig-2-Bac`"), ("ISO 7027", "`ISO 7027`"),
                     ("[49% measured and 51% modelled catchment area](NITROGEN.md)",
                      "49% measured and 51% modelled catchment area ([NITROGEN.md](NITROGEN.md))")):
        text = text.replace(old, new)
    text = text.replace("LiFePO₄", live.chem("LiFePO4"))
    text, n = carried(text)
    try:
        write_doc(OUT, text)
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote docs/SENSING.md - {n} numbers carried as self-quotation of {PAGE0}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
