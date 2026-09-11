#!/usr/bin/env python3
"""Find a locator for a quotation: a short phrase from the old text, with @@ where
the value stands, that finds that value exactly once.

A quotation of this site's past is a located reference (live.was, or
{was:COMMIT:FILE:phrase with @@} in a claims register): the value is read out of
git when the page is built, so the generator never types it. This suggests the
phrase.

    python3 scripts/quote_locate.py COMMIT FILE "80%" [hint words ...]

For every place the value occurs it prints the shortest locator that is unique in
the file, preferring context without digits (a locator full of other numbers is
a typed number by another name). Hint words - from the sentence the value sits in
now - rank the occurrences, best first.

    from quote_locate import locate
    locate(commit, file, "80%", hints="CTD station-days borrow")   # -> locator or None
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import live

MAX_WORDS = 9


def _occurrences(text, shown):
    rx = r"\s+".join(re.escape(w) for w in shown.split())
    return [m.span() for m in re.finditer(rx, text)]


def _candidates(text, a, b):
    """Locators around the value at text[a:b], shortest first."""
    left = re.findall(r"\S+", text[max(0, a - 400):a])
    right = re.findall(r"\S+", text[b:b + 400])
    glued_l = not text[a - 1:a].isspace() if a else False
    glued_r = not text[b:b + 1].isspace()
    for n in range(1, MAX_WORDS + 1):
        for kl, kr in ((n, n), (n, n - 1), (n - 1, n), (n, 0), (0, n)):
            if kl > len(left) or kr > len(right) or (kl == 0 and kr == 0):
                continue
            before = " ".join(left[len(left) - kl:]) if kl else ""
            after = " ".join(right[:kr]) if kr else ""
            if glued_l and before:          # "(" or "**" glued to the value
                before = before
            loc = (before + ("" if glued_l else " ") if before else "") + live.SLOT \
                + (("" if glued_r else " ") + after if after else "")
            yield loc


def suggestions(commit, file, shown, hints=""):
    text = live._git_text(commit, file)
    if text is None:
        raise SystemExit(f"{file} does not exist at {commit}")
    hint = {w.lower() for w in re.findall(r"[A-Za-zÆØÅæøå]{3,}", hints)}
    out = []
    for a, b in _occurrences(text, shown):
        best = None
        for loc in _candidates(text, a, b):
            try:
                hits = live._locate_all(text, loc)
            except live.Unjustified:
                continue
            # a reader sees the locator: it must read as a phrase, not as punctuation
            if len(re.findall(r"[A-Za-zÆØÅæøå]{3,}", loc)) < 3 and loc.count(" ") < 6:
                continue
            if len(hits) == 1 and hits[0][0].replace(" ", "") == shown.replace(" ", ""):
                clean = not re.search(r"\d", loc.replace(live.SLOT, ""))
                if best is None or (clean and not best[1]):
                    best = (loc, clean)
                if clean:
                    break
        ctx = set(w.lower() for w in re.findall(r"[A-Za-zÆØÅæøå]{3,}", text[max(0, a - 300):b + 300]))
        if best:
            out.append((len(hint & ctx), best[1], best[0], a))
    out.sort(key=lambda x: (-x[0], not x[1], len(x[2])))
    return out


def locate(commit, file, shown, hints=""):
    s = suggestions(commit, file, shown, hints)
    if not s:
        return None
    if len(s) > 1 and s[0][0] == s[1][0] and not hints:
        return None                      # ambiguous without hints: the caller must choose
    return s[0][2]


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    commit, file, shown, hints = argv[0], argv[1], argv[2], " ".join(argv[3:])
    s = suggestions(commit, file, shown, hints)
    if not s:
        print(f"  '{shown}' does not occur in {file} at {commit}, or no unique locator "
              f"within {MAX_WORDS} words either side")
        return 1
    for score, clean, loc, at in s:
        print(f"  hint match {score:2d}  {'digit-free' if clean else 'has digits'}  {loc!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
