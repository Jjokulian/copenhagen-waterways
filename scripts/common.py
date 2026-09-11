"""Shared helpers. Stdlib only - this box has no pip and ~300 MB of free RAM."""
import math
import gzip
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
DERIVED = os.path.join(ROOT, "data", "derived")
MANUAL = os.path.join(ROOT, "data", "manual")

UA = "copenhagen-waterways/0.1 (open-data research; contact via repo)"
# Copenhagen + immediate surroundings, WGS84. Used to clip national datasets.
CPH_BBOX = (12.30, 55.50, 12.80, 55.80)
# Denmark, WGS84. Used to detect axis order: latitudes (54-58) fall outside the
# longitude range (7-16), so a swapped pair is unambiguous.
BBOX = (7.0, 54.4, 15.6, 58.0)


def log(*a):
    a = tuple(__import__("live").strip_marks(x) if isinstance(x, str) else x for x in a)
    print(*a, file=sys.stderr, flush=True)


def fetch(url, retries=3, timeout=120, accept=None):
    """GET a URL, following redirects, with backoff. Returns bytes."""
    headers = {"User-Agent": UA, "Accept-Encoding": "gzip"}
    if accept:
        headers["Accept"] = accept
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                data = r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                return data
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
            last = e
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"failed after {retries} tries: {url}\n  {last}")


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(__import__("live").strip_marks(
            json.dumps(obj, ensure_ascii=False, indent=1)))
    os.replace(tmp, path)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fragments(path):
    """A register and its fragments: `x.json`, then every JSON file in `x.d/`,
    sorted. Parallel workers each write their own fragment, so no two ever
    read-modify-write the same file."""
    d = path[:-5] + ".d" if path.endswith(".json") else path + ".d"
    out = [path] if os.path.exists(path) else []
    if os.path.isdir(d):
        out += sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".json"))
    return out


def load_build():
    """data/manual/build.json with its fragments merged: every build step."""
    # the same script declared in two files is one step with both sets of inputs
    # and outputs - never a silent replacement of one by the other
    steps, by = [], {}
    for f in fragments(os.path.join(MANUAL, "build.json")):
        for s in read_json(f).get("steps", []):
            if s["script"] in by:
                t = by[s["script"]]
                t["inputs"] = t["inputs"] + [x for x in s.get("inputs", []) if x not in t["inputs"]]
                t["outputs"] = t["outputs"] + [x for x in s.get("outputs", []) if x not in t["outputs"]]
                if s.get("args") and not t.get("args"):
                    t["args"] = s["args"]
            else:
                by[s["script"]] = t = dict(s, inputs=list(s.get("inputs", [])),
                                           outputs=list(s.get("outputs", [])))
                steps.append(t)
    return {"steps": steps}


class locked:
    """An exclusive lock across processes, around a read-modify-write of a file
    several generators share (the number index, SOURCES.md)."""

    def __init__(self, name):
        self.path = os.path.join(ROOT, "data", "derived", f".{name}.lock")

    def __enter__(self):
        import fcntl
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.fh = open(self.path, "w")
        fcntl.flock(self.fh, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        import fcntl
        fcntl.flock(self.fh, fcntl.LOCK_UN)
        self.fh.close()
        return False


def _first_coord(geom):
    """Depth-first descent to the first [x, y] pair in any GeoJSON geometry."""
    if not geom:
        return None
    c = geom.get("coordinates")
    while isinstance(c, list) and c and isinstance(c[0], list):
        c = c[0]
    if isinstance(c, list) and len(c) >= 2 and all(isinstance(v, (int, float)) for v in c[:2]):
        return c
    return None


def in_cph(geom):
    """True if a geometry's first vertex falls inside the Copenhagen bounding box."""
    c = _first_coord(geom)
    return bool(c and CPH_BBOX[0] <= c[0] <= CPH_BBOX[2] and CPH_BBOX[1] <= c[1] <= CPH_BBOX[3])


def axis_order_ok(features):
    """WFS 1.0.0 vs 1.1.0 disagree on EPSG:4326 axis order. Detect which we got.

    Returns True if coords look like [lon, lat], False if they look swapped,
    and None if we cannot tell (no usable coordinate found).
    """
    for f in features[:50]:
        c = _first_coord(f.get("geometry"))
        if not c:
            continue
        x, y = c[0], c[1]
        if BBOX[0] <= x <= BBOX[2] and BBOX[1] <= y <= BBOX[3]:
            return True
        if BBOX[0] <= y <= BBOX[2] and BBOX[1] <= x <= BBOX[3]:
            return False
    return None


def swap_axes(geom):
    """In-place lon/lat swap for a GeoJSON geometry."""
    def walk(c):
        if isinstance(c, list) and c and isinstance(c[0], (int, float)):
            c[0], c[1] = c[1], c[0]
        elif isinstance(c, list):
            for sub in c:
                walk(sub)
    if geom and "coordinates" in geom:
        walk(geom["coordinates"])
    return geom


def plain_r(r, thing="one", other="the other"):
    """Say what a correlation coefficient actually means, in words.

    r is not a spell. It is the average of (how far x sits above its own average,
    counted in units of x's own typical wobble) times the same for y. The divisor
    is the two SPREADS, not the two means:

        r = sum((x-xbar)*(y-ybar)) / sqrt(sum((x-xbar)^2) * sum((y-ybar)^2))

    Dividing by the means, as is tempting, would make it depend on where zero
    happens to sit. Dividing by the spreads is what makes it a pure co-wobble
    score between -1 and +1, and what makes r-squared readable as a share.

    Two honest translations, both reported here because they say different things:
      r^2                  the share of one's wobble you can account for from the other
      1 - sqrt(1 - r^2)    how much knowing one shrinks your error guessing the other
    """
    r2 = r * r
    rest = 1 - r2                         # ** 0.5 keeps a live number live; math.sqrt does not
    shrink = 1 - (rest if rest > 0 else 0.0) ** 0.5
    return (f"{100*r2:.1f}% of the wobble in {thing} is shared with {other}; "
            f"knowing {other} shrinks your error guessing {thing} by {100*shrink:.0f}%")


def plain_r2(r2):
    rest = 1 - r2
    shrink = 1 - (rest if rest > 0 else 0.0) ** 0.5
    return (f"accounts for {100*r2:.0f}% of the wobble; shrinks prediction error "
            f"by {100*shrink:.0f}% against just guessing the average")


def write_doc(path, text):
    """Write a generated Markdown document, refusing the escaping bugs.

    A literal backslash-n reaches the page as visible characters and silently
    welds two paragraphs together - which is what happens when a string is escaped
    twice, once for the generator and once for whatever wrote the generator. It has
    happened here more than once and is invisible in review, so it is checked."""
    # The compiler. Every number must carry a chain of justification: live
    # markers become links to docs/SOURCES.md, fig() links go to CLAIMS.md, and
    # any quantity left bare stops the document from being written at all.
    from live import compile_doc
    text = compile_doc(path, text)
    bad = text.count("\\n")
    if bad:
        import re as _re
        first = _re.search(r".{0,70}\\\\n.{0,20}", text)
        raise ValueError(
            f"{os.path.basename(path)}: {bad} literal backslash-n in the output "
            f"- a double-escaped newline. First at: ...{first.group(0) if first else ''}...")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return len(text)
