#!/usr/bin/env python3
"""Crawl the Spildevandsplan 2018 project register on planer.kk.dk.

Every planned piece of Copenhagen's wastewater and cloudburst infrastructure has a
page there, keyed by a 'klima_id' (K1.57, BIR4.2, KV69 ...) which is the SAME key
used in the kk.dk WFS layers. That key is what lets us attach prose - claimed
volumes, depths, owners, affected land parcels - to actual geometry.

Usage:
    python3 scripts/fetch_plan_projects.py            # crawl (uses local HTML cache)
    python3 scripts/fetch_plan_projects.py --limit 20 # try a small slice first
    python3 scripts/fetch_plan_projects.py --refresh  # ignore the cache
"""
import gzip
import html
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RAW, fetch, log, write_json

SITEMAP = "https://planer.kk.dk/sitemap.xml"
PLAN = "https://planer.kk.dk/spildevandsplan-2018/projekter/"
CACHE = os.path.join(RAW, "plan_html")
DELAY = 0.7  # be a polite guest on a municipal server

# klima_id / project number as printed on the pages: K1.57, BIR4.2, KV69, AMA3.1a ...
ID_RE = re.compile(r"^[A-ZÆØÅ]{1,4}\s?\d+(?:\.\d+)*[a-zA-Z]?$")

MEASURES = [
    # A volume is only a volume if no rate marker follows it - "2.100 m3/t" is a pump
    # capacity, not a stored volume, and conflating the two badly distorts any total.
    ("volume_m3", r"(\d[\d.,]*)\s*(?:m3|m³|kubikmeter)\b(?!\s*(?:/|pr\.?\s|per\s))"),
    ("flow_m3_h", r"(\d[\d.,]*)\s*(?:m3|m³)\s*(?:/\s*t\b|/\s*h\b|pr\.?\s*time|per\s*time)"),
    ("flow_m3_s", r"(\d[\d.,]*)\s*(?:m3|m³)\s*(?:/\s*s\b|(?:vand\s*)?(?:i |pr\.? |per )?sekund)"),
    ("flow_l_s", r"(\d[\d.,]*)\s*l/s\b"),
    ("length_m", r"(\d[\d.,]*)\s*(?:meter|m)\s+lang"),
    ("length_km", r"(\d[\d.,]*)\s*km\b"),
    ("diameter_mm", r"(?:Ø|ø|diameter\D{0,15})\s*(\d{3,4})\b"),
    ("diameter_m", r"(?:diameter|i diameter|indvendig diameter)\D{0,20}?(\d[\d.,]*)\s*(?:meter|m)\b"),
    ("depth_m", r"(?:dybde|meters dybde|m\.u\.t\.|under terr[æa]n)\D{0,20}?(\d[\d.,]*)\s*(?:meter|m)\b"),
]


def strip_tags(fragment):
    fragment = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", fragment)
    fragment = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</tr>", "\n", fragment)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    txt = html.unescape(fragment)
    txt = re.sub(r"[ \t\xa0]+", " ", txt)
    return re.sub(r"\n\s*\n+", "\n", txt).strip()


# A period between digits is a Danish thousands separator, not a full stop, and
# Danish planning prose is thick with abbreviations ("ca. 15.100 m3", "bl.a.", "nr.").
# Python forbids variable-width lookbehind, so abbreviations are filtered after matching.
ABBREVS = {"ca", "bl.a", "m.fl", "nr", "pkt", "jf", "dvs", "osv", "inkl", "ekskl",
           "evt", "f.eks", "hhv", "stk", "m.v", "kap", "ø", "min", "maks"}
SENT_END = re.compile(r"(?<!\d)[.!?:\n](?=\s|$)")


def _is_real_boundary(text, pos):
    """True if the punctuation at `pos` ends a sentence rather than an abbreviation."""
    word = re.search(r"([\wÆØÅæøå.]+)$", text[max(0, pos - 12):pos])
    return not (word and word.group(1).rstrip(".").lower() in ABBREVS)


def sentence_around(text, start, end):
    """The sentence containing text[start:end], for human review of a scraped figure."""
    left = 0
    for m in SENT_END.finditer(text, 0, start):
        if _is_real_boundary(text, m.start()):
            left = m.end()
    right = min(len(text), end + 200)
    for m in SENT_END.finditer(text, end):
        if _is_real_boundary(text, m.start()):
            right = m.start() + 1
            break
    return re.sub(r"\s+", " ", text[left:right]).strip()[:400]


def parse_da_number(s):
    """'10.000' -> 10000.0 ; '2,4' -> 2.4 ; '1.234,5' -> 1234.5 (Danish convention)."""
    s = s.strip().rstrip(".,")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", s):
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def extract_measures(text):
    """Pull claimed physical quantities out of the prose.

    These are ADVERTISED figures scraped from planning text, not survey data.
    Every hit keeps the sentence it came from so a human can judge it.
    """
    out = {}
    for key, pat in MEASURES:
        for m in re.finditer(pat, text, re.I):
            val = parse_da_number(m.group(1))
            if val is None:
                continue
            ctx = sentence_around(text, m.start(), m.end())
            hit = {"value": val, "context": ctx}
            bucket = out.setdefault(key, [])
            if hit not in bucket:
                bucket.append(hit)
    for bucket in out.values():
        bucket.sort(key=lambda h: -h["value"])
    return out


def parse_tables(page):
    tables = []
    for tbl in re.findall(r"(?is)<table[^>]*>(.*?)</table>", page):
        rows = []
        for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", tbl):
            cells = [strip_tags(c) for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
            if any(c for c in cells):
                rows.append(cells)
        if len(rows) > 1:
            tables.append(rows)
    return tables


def parse_project(url, page):
    h1 = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", page)
    title = strip_tags(h1.group(1)) if h1 else None
    if title:
        title = re.sub(r"^[A-ZÆØÅ]{1,4}\s?\d+(?:\.\d+)*[a-zA-Z]?\s+", "", title).strip()

    sections, klima_id = {}, None
    for blk in re.findall(r'(?is)<div class="c-project-list">(.*?)</div>\s*</div>', page):
        fn = re.search(r'(?is)<div class="c-project-list__field-name">(.*?)</div>', blk)
        name = strip_tags(fn.group(1)) if fn else ""
        body = strip_tags(blk[fn.end():] if fn else blk)
        if not body:
            continue
        if not name:
            # the unlabelled block at the top of every page carries the project number
            first = body.split("\n")[0].strip()
            if ID_RE.match(first):
                klima_id = first
                continue
            name = "_intro"
        sections[name] = (sections.get(name, "") + "\n" + body).strip()

    parts = [p for p in url.replace(PLAN, "").split("/") if p]
    body_text = "\n".join(f"{k}\n{v}" for k, v in sections.items())

    return {
        "klima_id": klima_id,
        "title": title,
        "category": parts[0] if parts else None,
        "slug": parts[-1] if parts else None,
        "url": url,
        "sections": sections,
        "tables": parse_tables(page),
        "measures": extract_measures(body_text),
        "mentions_hofor": bool(re.search(r"\bHOFOR\b", body_text)),
        "text_chars": len(body_text),
    }


def cached_get(url, refresh=False):
    os.makedirs(CACHE, exist_ok=True)
    key = re.sub(r"[^a-z0-9]+", "_", url.replace(PLAN, "").lower()).strip("_") or "index"
    path = os.path.join(CACHE, key + ".html.gz")
    if os.path.exists(path) and not refresh:
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
            return f.read(), True
    page = fetch(url).decode("utf-8", "replace")
    with gzip.open(path, "wt", encoding="utf-8") as f:
        f.write(page)
    return page, False


def main():
    argv = sys.argv[1:]
    refresh = "--refresh" in argv
    limit = None
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])

    log("fetching sitemap ...")
    sm = fetch(SITEMAP).decode("utf-8", "replace")
    urls = sorted(set(re.findall(r"<loc>(%s[^<]+/[^<]+/)</loc>" % re.escape(PLAN), sm)))
    # Everything else in the plan: appendices, status chapters, targets, the
    # "aktuelle projekter" pages. Scanned so that "no plan page describes this
    # structure" means the WHOLE plan, not just the project register.
    other = sorted(set(re.findall(r"<loc>(https://planer\.kk\.dk/spildevandsplan-2018/[^<]*)</loc>", sm)))
    other = [u for u in other if "/projekter/" not in u]
    if limit:
        urls = urls[:limit]
    log(f"{len(urls)} project pages to read")

    projects, fetched = [], 0
    for i, url in enumerate(urls, 1):
        try:
            page, was_cached = cached_get(url, refresh)
            if not was_cached:
                fetched += 1
                time.sleep(DELAY)
            projects.append(parse_project(url, page))
        except Exception as e:
            log(f"  !! {url}: {e}")
        if i % 50 == 0:
            log(f"  {i}/{len(urls)} ({fetched} newly downloaded)")

    log(f"\nreading {len(other)} non-project pages of the plan ...")
    others = []
    for i, url in enumerate(other, 1):
        try:
            page, was_cached = cached_get(url, refresh)
            if not was_cached:
                time.sleep(DELAY)
            others.append({"url": url, "text": strip_tags(page)[:200000]})
        except Exception as e:
            log(f"  -- {url}: {e}")
    write_json(os.path.join(RAW, "plan_other_pages.json"), others)
    log(f"  {len(others)} pages -> data/raw/plan_other_pages.json")

    write_json(os.path.join(RAW, "plan_projects.json"), projects)
    with_id = sum(1 for p in projects if p["klima_id"])
    with_vol = sum(1 for p in projects if p["measures"].get("volume_m3"))
    log(f"\n{len(projects)} projects -> data/raw/plan_projects.json")
    log(f"  with klima_id: {with_id}   with a stated m3 volume: {with_vol}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
