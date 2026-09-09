"""Every link in the site, resolved the way each reader actually resolves it.

This project is read in two places and they disagree about what a link means, which
is how a page ends up with a link that works for the person who wrote it and not for
anybody else:

  * **the reader** (index.html) renders docs/*.md from the repository root, and
    rewrites relative links against the document's own directory. A bare `#NAME.md`
    is a document link there.
  * **GitHub** renders the same file in place. A bare `#NAME.md` is a *fragment* on
    the current page - so it is broken - while a relative `NAME.md` is a file link
    and works.

So there is one form that is right in both: **a relative path**. `NAME.md`, not
`#NAME.md`. This checks that rule and everything else that can break.

  python3 scripts/check_links.py            report
  python3 scripts/check_links.py --fix      rewrite #NAME.md -> NAME.md in the
                                            generators and the hand-written pages

External http(s) links are listed but not fetched; that is a different job with a
different failure mode.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
FOLDED = {"æ": "ae", "ø": "oe", "å": "aa", "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
MD_LINK = re.compile(r'(?<!\!)\[[^\]]*\]\(([^)\s]+)\)')
IMG_LINK = re.compile(r'!\[[^\]]*\]\(([^)\s]+)\)')
HREF = re.compile(r'(?:href|src)="([^"]+)"')


def slugify(text, used):
    import unicodedata
    base = text.lower()
    for k, v in FOLDED.items():
        base = base.replace(k, v)
    base = unicodedata.normalize("NFKD", base)
    base = "".join(c for c in base if not unicodedata.combining(c))
    base = re.sub(r"[^a-z0-9]+", "-", base).strip("-") or "section"
    out = base
    n = 2
    while out in used:
        out = f"{base}-{n}"
        n += 1
    used.add(out)
    return out


def headings(path):
    """Slugs the reader will generate for one markdown file, in document order."""
    used = set()
    out = set()
    fence = False
    for line in open(path, encoding="utf-8"):
        if line.startswith("```"):
            fence = not fence
        if fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if m:
            text = re.sub(r"[`*_\[\]]|\(#?[^)]*\)", "", m.group(2))
            out.add(slugify(text, used))
    return out


def doc_names():
    """The documents the reader will render, read out of index.html's own list."""
    src = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    block = src[src.index("const GROUPS"):src.index("const DOCS")]
    return set(re.findall(r'\["([^"]+\.md)"', block))


def check():
    docs = doc_names()
    problems = []
    md_files = []
    for base, _, names in os.walk(DOCS):
        for n in names:
            if n.endswith(".md"):
                md_files.append(os.path.join(base, n))
    heads = {p: headings(p) for p in md_files}

    for path in sorted(md_files):
        rel = os.path.relpath(path, ROOT)
        here = os.path.relpath(path, DOCS)
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            for m in list(MD_LINK.finditer(line)) + list(IMG_LINK.finditer(line)):
                t = m.group(1)
                if t.startswith(("http://", "https://", "mailto:", "tel:")):
                    continue
                if t.startswith("#"):
                    frag = t[1:]
                    if frag in docs:
                        problems.append((rel, i, t, "document link written as a "
                                         "fragment - breaks on GitHub; use "
                                         + frag))
                    elif frag not in heads[path]:
                        problems.append((rel, i, t, "no heading with that slug in "
                                         "this file"))
                    continue
                target, _, frag = t.partition("#")
                if not target:
                    continue
                p = os.path.normpath(os.path.join(os.path.dirname(path), target))
                if not os.path.exists(p):
                    problems.append((rel, i, t, "file does not exist"))
                elif target.endswith(".md"):
                    name = os.path.relpath(p, DOCS)
                    if name not in docs and name not in {os.path.relpath(x, DOCS)
                                                         for x in md_files}:
                        problems.append((rel, i, t, "not a document the reader lists"))

    for name in sorted(os.listdir(ROOT)) + ["index.html"]:
        pass
    for path in [os.path.join(ROOT, "index.html")] + [
            os.path.join(DOCS, f) for f in sorted(os.listdir(DOCS))
            if f.endswith(".html")] + [
            os.path.join(ROOT, "viz", f) for f in sorted(os.listdir(os.path.join(ROOT, "viz")))
            if f.endswith(".html")]:
        rel = os.path.relpath(path, ROOT)
        for i, line in enumerate(open(path, encoding="utf-8"), 1):
            for m in HREF.finditer(line):
                t = m.group(1)
                if t.startswith(("http://", "https://", "mailto:", "tel:", "data:",
                                 "#", "javascript:")):
                    continue
                # hrefs assembled in JavaScript are not links, they are code
                if any(c in t for c in "'+`$") or " " in t:
                    continue
                target = t.split("?")[0].split("#")[0]
                if not target:
                    continue
                p = os.path.normpath(os.path.join(os.path.dirname(path), target))
                if not os.path.exists(p):
                    problems.append((rel, i, t, "file does not exist"))

    # A page in docs/hypodrafts/ or docs/openproblems/ is deliberately not in the
    # reading map; a page sitting directly in docs/ and unlisted is one nobody placed.
    def unpublished(name):
        """A page can say it is not ready, and then not being listed is the point."""
        head = open(os.path.join(DOCS, name), encoding="utf-8").read(600).upper()
        return "NOT PUBLISHED" in head or "DRAFT" in head.split("\n")[2:4][0] \
            if head.count("\n") > 3 else "NOT PUBLISHED" in head
    orphans = sorted(n for n in ({os.path.relpath(p, DOCS) for p in md_files} - docs)
                     if os.sep not in n and not unpublished(n))
    return problems, orphans


def fix():
    """Rewrite #NAME.md as NAME.md, in the generators as well as the pages.

    The generators are where most of them live, so fixing only the output would
    reintroduce every one of them on the next run.
    """
    docs = doc_names()
    changed = 0
    targets = []
    for base, _, names in os.walk(ROOT):
        if any(x in base for x in (".git", "data/raw", "node_modules")):
            continue
        for n in names:
            if n.endswith((".md", ".py")) and "/data/" not in base:
                targets.append(os.path.join(base, n))
    for path in targets:
        src = open(path, encoding="utf-8").read()
        out = src
        # A document in docs/hypodrafts/ reaches its siblings through ../, and a
        # generator writes for whatever directory its output lands in - which is
        # docs/ for all of them. Getting this wrong is how the first pass turned
        # working fragment links into broken relative ones.
        rel = os.path.relpath(path, DOCS)
        depth = rel.count(os.sep) if path.startswith(DOCS) and rel != "." else 0
        up = "../" * depth
        for name in docs:
            out = out.replace(f"](#{name})", f"]({up}{name})")
        if out != src:
            open(path, "w", encoding="utf-8").write(out)
            changed += 1
            print("  rewrote", os.path.relpath(path, ROOT))
    print(f"{changed} file(s) changed")


if __name__ == "__main__":
    if "--fix" in sys.argv:
        fix()
    else:
        problems, orphans = check()
        by_kind = {}
        for rel, line, target, why in problems:
            by_kind.setdefault(why, []).append((rel, line, target))
        for why, items in sorted(by_kind.items(), key=lambda x: -len(x[1])):
            print(f"\n{len(items)} × {why}")
            for rel, line, target in items[:6]:
                print(f"    {rel}:{line}  {target}")
            if len(items) > 6:
                print(f"    … and {len(items)-6} more")
        if orphans:
            print(f"\n{len(orphans)} document(s) not listed in index.html: "
                  + ", ".join(orphans))
        print(f"\n{len(problems)} problem(s)")
        sys.exit(1 if problems else 0)
