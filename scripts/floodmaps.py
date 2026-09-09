#!/usr/bin/env python3
"""Recover Copenhagen's 2012 flood model from the PDFs it was buried in.

`Oversvoemmelsesscenarier for vandoplande` is a 2D surface flood model of a 100-year
event, published as seven raster PDFs: an aerial photo with six depth bands painted on
top, no georeferencing, no values. This turns each sheet back into a depth raster.

Pipeline:
    fetch      download the seven PDFs
    render     PDF -> PNG at 200 dpi, locate the map frame and read the scale bar
    extract    classify the six depth bands -> a depth-coded PNG with transparency
    autoref    locate each sheet automatically by matching water (FFT correlation)
    georef     apply control points -> world file + corner coordinates, with residuals
    check      render a visual overlay per sheet so a human can confirm the fit
    status     what is done and what still needs control points

Georeferencing (`autoref`) works by matching water. The orthophoto's water has a strong
signature - dark, with G-R and B-R both around +18 - and the city publishes water as
vector polygons, so the sheet can be located by cross-correlating the two. FFT does it
over the whole city at once rather than searching offsets one at a time.

An earlier attempt matched the drawn catchment outline instead and failed badly. The
reason turned out to be interesting: the "Oplandsgraenser" drawn on these 2012 sheets is
NOT the boundary in today's skp_skybrudsoplande. Registering on water and then testing
against the drawn outline gives 13.6% coverage against an 11% chance level - the
registration is right (the vector coastline traces the photographed quays exactly) and
the boundary is what changed. Do not use the catchment outline to validate.

`georef` remains available for hand-placed control points via viz/georef.html, as a
fallback and for any sheet where autoref's confidence is low.

Usage:
    python3 scripts/floodmaps.py fetch
    python3 scripts/floodmaps.py render [sheet ...]
    python3 scripts/floodmaps.py extract [sheet ...]
    python3 scripts/floodmaps.py autoref [sheet ...]
    python3 scripts/floodmaps.py georef [sheet ...]
    python3 scripts/floodmaps.py check [sheet ...]
    python3 scripts/floodmaps.py status
"""
import itertools
import json
import math
import re
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, MANUAL, RAW, ROOT, fetch, log, read_json, write_json

CKAN = ("https://admin.opendata.dk/api/3/action/package_show"
        "?id=oversvommelsesscenarier-for-vandoplande")
PDFDIR = os.path.join(RAW, "floodmaps")
OUTDIR = os.path.join(DERIVED, "floodmaps")
CONTROL = os.path.join(MANUAL, "floodmap_control.json")
DPI = 200

# Sheet -> the catchment in skp_skybrudsoplande (opland_kort_navn). The seven sheets
# correspond exactly to the seven cloudburst catchments.
SHEETS = {
    "amager": "Amager",
    "bispebjerg": "Bispebjerg",
    "indre-by": "Indre By",
    "kbhvest": "København Vest",
    "ladegaardsaaen": "Ladegårdsåen",
    "norrebro": "Nørrebro",
    "osterbro": "Østerbro",
}

# The legend ramp, sampled from the legend swatches of indre-by.pdf at 200 dpi.
# All six swatches measured 1537-1590 px, i.e. identical rectangles, and the values are
# the standard ArcGIS/ColorBrewer "Blues" ramp - the same symbology on every sheet.
# `extract` verifies all six are present per sheet rather than assuming it.
BANDS = [
    {"rgb": (247, 251, 255), "lo": 0.05, "hi": 0.1,  "label": "0.05-0.1 m"},
    {"rgb": (209, 226, 242), "lo": 0.1,  "hi": 0.2,  "label": "0.1-0.2 m"},
    {"rgb": (154, 199, 224), "lo": 0.2,  "hi": 0.5,  "label": "0.2-0.5 m"},
    {"rgb": (81, 156, 204),  "lo": 0.5,  "hi": 1.0,  "label": "0.5-1 m"},
    {"rgb": (28, 107, 176),  "lo": 1.0,  "hi": 2.0,  "label": "1-2 m"},
    {"rgb": (8, 48, 107),    "lo": 2.0,  "hi": None, "label": ">2 m"},
]

# Search window for autoref: Copenhagen plus a margin, in WGS84.
SEARCH = (12.28, 55.48, 12.82, 55.82)
LATM = 111320.0
# Water in these orthophotos: dark, and markedly greener/bluer than red.
WATER_GR = 9      # min (G - R)
WATER_BR = 9      # min (B - R)
WATER_LUM = 70    # max mean luminance

COLOUR_TOL = 26.0   # euclidean RGB distance; the sheets are JPEG so exact match is rare
FLATNESS = 20.0     # max local std-dev, applied only to the five darker bands
BLUE_CAST = 3       # min (B - R) for the palest band


def _np():
    import numpy as np
    return np


def _pil():
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    return Image


# ----------------------------------------------------------------------------- fetch
def cmd_fetch(args):
    os.makedirs(PDFDIR, exist_ok=True)
    meta = json.loads(fetch(CKAN).decode("utf-8"))["result"]
    urls = {r["url"].rsplit("/", 1)[-1]: r["url"]
            for r in meta["resources"] if r["format"].upper() == "PDF"}
    write_json(os.path.join(PDFDIR, "_urls.json"), urls)
    for name, url in urls.items():
        dst = os.path.join(PDFDIR, name)
        if os.path.exists(dst):
            log(f"  have {name}")
            continue
        data = fetch(url, timeout=300)
        with open(dst, "wb") as f:
            f.write(data)
        log(f"  got  {name}  {len(data)/1e6:.1f} MB")
    log(f"\nnotes: {meta.get('notes', '').strip()[:200]}")
    return 0


# ---------------------------------------------------------------------------- render
def longest_run(mask_row, np):
    idx = np.flatnonzero(mask_row)
    if len(idx) == 0:
        return (0, 0)
    parts = np.split(idx, np.where(np.diff(idx) != 1)[0] + 1)
    best = max(parts, key=len)
    return (int(best[0]), len(best))


SCALEBAR_RE = re.compile(r"\b0\s+(\d[\d.,]*)\s+(\d[\d.,]*)\s*m\b")
BAND_LABELS = ["0,05-0,1", "0,1-0,2", "0,2-0,5", "0,5-1", "1-2", ">2"]


def pdf_text(pdf):
    """The sheets carry a real text layer - the scale bar label is in it, so the bar
    length never has to be guessed. Guessing it put Amager out by a factor of two."""
    return subprocess.run(["pdftotext", "-f", "1", "-l", "1", pdf, "-"],
                          capture_output=True, text=True, check=True).stdout


def scalebar_metres(text, sheet):
    m = SCALEBAR_RE.search(" ".join(text.split()))
    if not m:
        raise RuntimeError(f"{sheet}: no scale bar label in the PDF text layer")
    return float(m.group(2).replace(".", "").replace(",", "."))


def check_bands(text, sheet):
    """Confirm this sheet uses the same six-band legend the palette was sampled from."""
    flat = " ".join(text.split())
    missing = [b for b in BAND_LABELS if b not in flat]
    if missing:
        log(f"  !! {sheet}: legend labels missing {missing} - palette may not apply")
    return not missing


def measure_sheet(png, pdf, sheet, np, Image):
    """Locate the map frame and read the scale bar. Returns metres-per-pixel."""
    text = pdf_text(pdf)
    bar_m = scalebar_metres(text, sheet)
    same_legend = check_bands(text, sheet)
    a = np.asarray(Image.open(png).convert("RGB"))
    h, w, _ = a.shape
    white = (a >= 250).all(axis=2)

    # the page margin below the map is fully white across its whole width
    margin = [y for y in range(int(h * 0.85), h) if white[y].mean() > 0.9]
    frame_bottom = margin[0] - 1 if margin else h - 1

    content = ~white
    rows = np.flatnonzero(content[:frame_bottom].mean(axis=1) > 0.5)
    cols = np.flatnonzero(content[:frame_bottom].mean(axis=0) > 0.5)
    fy0, fy1 = int(rows[0]), int(rows[-1])
    fx0, fx1 = int(cols[0]), int(cols[-1])

    # scale bar: the longest horizontal black run below the frame, spanning 500 m
    black = (a < 70).all(axis=2)
    best = (0, 0, 0)
    for y in range(frame_bottom + 1, h):
        s, ln = longest_run(black[y], np)
        if ln > best[2]:
            best = (y, s, ln)
    bar_px = best[2]
    if bar_px < 50:
        raise RuntimeError("could not find the scale bar")
    mpp = bar_m / bar_px
    return {
        "size": [int(w), int(h)],
        "frame": [fx0, fy0, fx1, fy1],
        "scalebar_px": int(bar_px),
        "scalebar_m": bar_m,
        "m_per_px": mpp,
        "map_scale": round(mpp / (0.0254 / DPI)),
        "standard_legend": same_legend,
    }


def cmd_render(args):
    np, Image = _np(), _pil()
    os.makedirs(OUTDIR, exist_ok=True)
    out = {}
    for sheet in (args or SHEETS):
        pdf = os.path.join(PDFDIR, f"{sheet}.pdf")
        if not os.path.exists(pdf):
            log(f"  -- {sheet}: no PDF, run `fetch` first")
            continue
        png = os.path.join(OUTDIR, f"{sheet}.render.png")
        if not os.path.exists(png):
            subprocess.run(["pdftoppm", "-r", str(DPI), "-png", "-f", "1", "-l", "1",
                            pdf, png[:-4]], check=True)
            os.replace(png[:-4] + "-1.png", png)
        m = measure_sheet(png, pdf, sheet, np, Image)
        # a browser-sized copy of just the map frame, for the control-point tool
        fx0, fy0, fx1, fy1 = m["frame"]
        frame_w, frame_h = fx1 - fx0 + 1, fy1 - fy0 + 1
        prev_w = min(1500, frame_w)
        prev = Image.open(png).convert("RGB").crop((fx0, fy0, fx1 + 1, fy1 + 1))
        prev = prev.resize((prev_w, max(1, round(frame_h * prev_w / frame_w))), Image.LANCZOS)
        prev.save(os.path.join(OUTDIR, f"{sheet}.preview.jpg"), quality=82, optimize=True)
        m["preview"] = {"file": f"data/derived/floodmaps/{sheet}.preview.jpg",
                        "size": [prev.width, prev.height],
                        "scale_to_frame": frame_w / prev.width}
        m["sheet"] = sheet
        m["catchment"] = SHEETS[sheet]
        out[sheet] = m
        fx0, fy0, fx1, fy1 = m["frame"]
        fw, fh = fx1 - fx0 + 1, fy1 - fy0 + 1
        log(f"  {sheet:16} bar {m['scalebar_m']:>5.0f} m / {m['scalebar_px']:>4} px"
            f"  -> {m['m_per_px']:.3f} m/px  ~1:{m['map_scale']:,}"
            f"  frame {fw*m['m_per_px']/1000:.2f}x{fh*m['m_per_px']/1000:.2f} km"
            .replace("{fw}", "") )

    path = os.path.join(OUTDIR, "_sheets.json")
    existing = read_json(path) if os.path.exists(path) else {}
    existing.update(out)
    write_json(path, existing)
    log(f"\n{len(existing)} sheet(s) measured -> data/derived/floodmaps/_sheets.json")
    return 0


# --------------------------------------------------------------------------- extract
def classify(a, np):
    """Assign each pixel to a depth band, or 0 for 'not flooded'.

    The palest band (247,251,255) is barely off-white, so on colour alone it matches
    every white roof on the sheet - 363,940 hits on Indre By against 18,393 real ones.
    What separates it is the blue cast: the fill keeps B-R = +8 where paint and concrete
    are neutral. That one test removes 95% of the false positives.

    A local-flatness test (vector fill is flat, aerial photo is not) helps the darker
    bands, but must NOT be applied to the pale band: those are 2-8 px streaks threading
    along streets, so almost every pixel is an edge pixel and flatness deletes them.
    Applying it everywhere cut Indre By's flooded area by a factor of three.
    """
    h, w, _ = a.shape
    f = a.astype(np.float32)

    # local std over a 3x3 window, via shifted sums (no scipy on this box)
    pad = np.pad(f.mean(axis=2), 1, mode="edge")
    s1 = np.zeros((h, w), np.float32)
    s2 = np.zeros((h, w), np.float32)
    for dy in (0, 1, 2):
        for dx in (0, 1, 2):
            v = pad[dy:dy + h, dx:dx + w]
            s1 += v
            s2 += v * v
    flat = np.sqrt(np.maximum(s2 / 9.0 - (s1 / 9.0) ** 2, 0)) < FLATNESS
    blue_cast = a[:, :, 2].astype(np.int16) - a[:, :, 0].astype(np.int16) >= BLUE_CAST

    best_d = np.full((h, w), 1e9, np.float32)
    band = np.zeros((h, w), np.uint8)
    for i, b in enumerate(BANDS, start=1):
        r, g, bl = b["rgb"]
        d = np.sqrt((f[:, :, 0] - r) ** 2 + (f[:, :, 1] - g) ** 2 + (f[:, :, 2] - bl) ** 2)
        ok = (d < COLOUR_TOL) & (d < best_d)
        ok &= blue_cast if i == 1 else flat
        band[ok] = i
        best_d = np.where(ok, d, best_d)
    return band


def cmd_extract(args):
    np, Image = _np(), _pil()
    sheets = read_json(os.path.join(OUTDIR, "_sheets.json"))
    report = {}
    for sheet in (args or SHEETS):
        if sheet not in sheets:
            log(f"  -- {sheet}: not rendered yet")
            continue
        m = sheets[sheet]
        png = os.path.join(OUTDIR, f"{sheet}.render.png")
        a = np.asarray(Image.open(png).convert("RGB"))
        fx0, fy0, fx1, fy1 = m["frame"]

        band = classify(a, np)
        band[:fy0] = 0
        band[fy1 + 1:] = 0
        band[:, :fx0] = 0
        band[:, fx1 + 1:] = 0

        # the legend sits inside the frame and contains all six colours as big blocks;
        # blank it so the swatches are not exported as flooded ground
        legend = find_legend(os.path.join(PDFDIR, f"{sheet}.pdf"), (a.shape[1], a.shape[0]))
        if legend:
            lx0, ly0, lx1, ly1 = legend
            band[ly0:ly1, lx0:lx1] = 0

        px_m2 = m["m_per_px"] ** 2
        counts = {}
        for i, b in enumerate(BANDS, start=1):
            n = int((band == i).sum())
            counts[b["label"]] = {"pixels": n, "area_m2": round(n * px_m2)}
        missing = [b["label"] for i, b in enumerate(BANDS, start=1) if counts[b["label"]]["pixels"] == 0]

        # depth-coded PNG: band index in R, 255 alpha where flooded
        rgba = np.zeros((a.shape[0], a.shape[1], 4), np.uint8)
        for i, b in enumerate(BANDS, start=1):
            sel = band == i
            rgba[sel] = (*b["rgb"], 255)
        crop = rgba[fy0:fy1 + 1, fx0:fx1 + 1]
        outpng = os.path.join(OUTDIR, f"{sheet}.depth.png")
        Image.fromarray(crop, "RGBA").save(outpng, optimize=True)

        idx = np.zeros((a.shape[0], a.shape[1]), np.uint8)
        idx[:] = band
        np.save(os.path.join(OUTDIR, f"{sheet}.band.npy"), idx[fy0:fy1 + 1, fx0:fx1 + 1])

        total = sum(c["area_m2"] for c in counts.values())
        frame_m2 = (fx1 - fx0 + 1) * (fy1 - fy0 + 1) * px_m2
        report[sheet] = {"bands": counts, "flooded_m2": total,
                         "frame_m2": round(frame_m2),
                         "flooded_fraction": round(total / frame_m2, 4),
                         "missing_bands": missing,
                         "legend_blanked": legend}
        log(f"  {sheet:16} flooded {total/1e6:6.2f} km2  "
            f"({total/frame_m2*100:4.1f}% of frame)"
            + (f"   MISSING: {missing}" if missing else ""))

    path = os.path.join(OUTDIR, "_extract.json")
    existing = read_json(path) if os.path.exists(path) else {}
    existing.update(report)
    write_json(path, existing)
    return 0


WORD_RE = re.compile(
    r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>')
PAGE_RE = re.compile(r'<page width="([\d.]+)" height="([\d.]+)"')


def find_legend(pdf, size):
    """Legend bounding box in pixels, from the PDF's own text positions.

    The legend contains one filled rectangle per depth band, so leaving it in the
    export paints a block of fictional deep flooding at the legend's location - on
    Indre By the '1-2 m' and '>2 m' bands were otherwise ENTIRELY legend swatches.
    A pixel heuristic kept missing it; the text layer gives the position exactly.
    """
    xml = subprocess.run(["pdftotext", "-bbox", "-f", "1", "-l", "1", pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    pm = PAGE_RE.search(xml)
    if not pm:
        return None
    pw, ph = float(pm.group(1)), float(pm.group(2))
    words = [(float(a), float(b), float(c), float(d), t)
             for a, b, c, d, t in WORD_RE.findall(xml)]
    title = next((w for w in words if w[4].strip() == "Tegnforklaring"), None)
    if not title:
        return None
    tx0, ty0 = title[0], title[1]
    # everything below and roughly right of the legend title belongs to the legend;
    # this excludes the sheet title (above) and the scale bar labels (far left)
    leg = [w for w in words if w[1] >= ty0 - 4 and w[0] >= tx0 - 80]
    if not leg:
        return None
    x0 = min(w[0] for w in leg) - 55    # the colour swatches sit left of their labels
    y0 = min(w[1] for w in leg) - 12
    x1 = max(w[2] for w in leg) + 12
    y1 = max(w[3] for w in leg) + 12
    W, H = size
    sx, sy = W / pw, H / ph
    return [max(0, int(x0 * sx)), max(0, int(y0 * sy)),
            min(W, int(x1 * sx)), min(H, int(y1 * sy))]


# --------------------------------------------------------------------------- autoref
def cmd_autoref(args):
    """Locate each sheet by matching water, using several detectors and their agreement.

    See scripts/floodreg.py for why it is an ensemble rather than one algorithm: the
    sheets do not share an orthophoto, and no single water detector survives all seven.
    A sheet is only accepted when independent detectors land in the same place.
    """
    np, Image = _np(), _pil()
    import floodreg
    sheets = read_json(os.path.join(OUTDIR, "_sheets.json"))
    path = os.path.join(OUTDIR, "_georef.json")
    out = read_json(path) if os.path.exists(path) else {}

    for sheet in (args or SHEETS):
        if sheet not in sheets:
            log(f"  -- {sheet}: not rendered")
            continue
        m = sheets[sheet]
        log(f"  {sheet}:")
        res = floodreg.register(OUTDIR, sheet, m, SHEETS[sheet], np, Image)
        if not res or not res.get("resolved"):
            log(f"    unresolved: {(res or {}).get('reason', 'no agreement')}")
            out.pop(sheet, None)
            continue

        fx0, fy0, fx1, fy1 = m["frame"]
        mpp = m["m_per_px"]
        west, north = res["lon_nw"], res["lat_nw"]
        east = west + (fx1 - fx0 + 1) * mpp / floodreg.LONM
        south = north - (fy1 - fy0 + 1) * mpp / floodreg.LATM
        # Accept only on agreement between detectors that fail differently. A lone
        # confident answer is exactly what produced the earlier wrong registrations.
        # Thresholds set by inspecting the overlays: kbhvest passed a looser bar at
        # 57 m spread / IoU 0.117, and its magenta water outlines visibly do not track
        # the photographed water. Accepting it would have shipped a wrong registration.
        # spread_m is measured over the AGREEING variants only, so it is small by
        # construction once agreement has selected a cluster - a statistic conditioned
        # on the thing it is meant to test. norrebro shipped with the tightest
        # agreeing-spread in the set (12.7 m) and a 3,115 m spread across all variants,
        # on a bare 3/6 agreement, and was published as confident. Require a majority,
        # and measure the spread over EVERY variant that ran.
        oks = [v for v in res["variants"] if v.get("ok")]
        spread_all = 0.0
        for a, b in itertools.combinations(oks, 2):
            dx = (a["lon_nw"] - b["lon_nw"]) * floodreg.LONM
            dy = (a["lat_nw"] - b["lat_nw"]) * floodreg.LATM
            spread_all = max(spread_all, (dx * dx + dy * dy) ** 0.5)
        confident = (res["agree"] >= 4 and res["spread_m"] <= 40
                     and res["best_iou"] >= 0.12 and spread_all <= 600)
        out[sheet] = {
            "method": "autoref: ensemble water cross-correlation",
            "agree": res["agree"], "variants_run": res["variants_run"],
            "spread_m": res["spread_m"], "spread_all_m": round(spread_all, 1),
            "best_iou": res["best_iou"],
            "m_per_px_from_scalebar": round(mpp, 4),
            "bounds_wgs84": {"west": west, "east": east, "south": south, "north": north},
            "corners_for_maplibre": [[west, north], [east, north], [east, south], [west, south]],
            "image": f"data/derived/floodmaps/{sheet}.depth.png",
            "confident": bool(confident),
            "variants": res["variants"],
        }
        log(f"    => {res['agree']}/{res['variants_run']} agree within "
            f"{res['spread_m']:.0f} m, best IoU {res['best_iou']:.3f}  "
            f"{'ACCEPTED' if confident else 'NOT CONFIDENT - verify or use georef.html'}")

    write_json(path, out)
    ok = sum(1 for v in out.values() if v.get("confident"))
    log(f"\n{ok}/{len(SHEETS)} sheets accepted. Run `check` and look at the overlays:")
    log("the magenta water outlines must trace the photographed quays and lake edges.")
    return 0


def cmd_check(args):
    """Draw the city's water outlines onto each registered sheet.

    The only honest confirmation. If the magenta lines trace the photographed quays, the
    registration is right; if they float, it is not.
    """
    np, Image = _np(), _pil()
    from PIL import ImageDraw
    import floodreg
    sheets = read_json(os.path.join(OUTDIR, "_sheets.json"))
    geo_path = os.path.join(OUTDIR, "_georef.json")
    if not os.path.exists(geo_path):
        log("nothing georeferenced yet - run `autoref` or `georef` first")
        return 0
    geo = read_json(geo_path)
    lonm = floodreg.LONM
    for sheet in (args or SHEETS):
        if sheet not in geo:
            continue
        m, g = sheets[sheet], geo[sheet]
        fx0, fy0, fx1, fy1 = m["frame"]
        mpp = m["m_per_px"]
        w0 = g["bounds_wgs84"]["west"]
        n0 = g["bounds_wgs84"]["north"]
        im = Image.open(os.path.join(OUTDIR, f"{sheet}.render.png")).convert("RGB")
        im = im.crop((fx0, fy0, fx1 + 1, fy1 + 1))
        dr = ImageDraw.Draw(im)
        for ring in floodreg.water_rings():
            pts = [((lon - w0) * lonm / mpp, (n0 - lat) * floodreg.LATM / mpp)
                   for lon, lat in ring]
            if all(x < -60 or x > im.width + 60 or y < -60 or y > im.height + 60
                   for x, y in pts):
                continue
            dr.line(pts + [pts[0]], fill=(255, 0, 255), width=max(2, int(6 / mpp)))
        sc = 1400 / im.width
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        dst = os.path.join(OUTDIR, f"{sheet}.check.jpg")
        im.save(dst, quality=80, optimize=True)
        tag = "accepted" if g.get("confident") else "NOT accepted"
        log(f"  {sheet:16} [{tag}] -> {os.path.relpath(dst, ROOT)}")
    return 0


# ---------------------------------------------------------------------------- georef
def cmd_georef(args):
    """Turn hand-placed control points into corner coordinates and a world file."""
    sheets = read_json(os.path.join(OUTDIR, "_sheets.json"))
    control = read_json(CONTROL) if os.path.exists(CONTROL) else {}
    out = {}
    for sheet in (args or SHEETS):
        pts = (control.get(sheet) or {}).get("points") or []
        if len(pts) < 2:
            log(f"  -- {sheet}: {len(pts)} control point(s); need 2. Use viz/georef.html")
            continue
        m = sheets[sheet]
        fx0, fy0, fx1, fy1 = m["frame"]

        # Solve lon = a*px + b, lat = c*py + d by least squares over the control points.
        # No rotation: every sheet has north up (the north arrow confirms it), so two
        # points determine the mapping and more than two let us report a residual.
        px = [p["px"] for p in pts]
        py = [p["py"] for p in pts]
        lon = [p["lon"] for p in pts]
        lat = [p["lat"] for p in pts]

        def fit(u, v):
            n = len(u)
            su, sv = sum(u), sum(v)
            suu = sum(x * x for x in u)
            suv = sum(x * y for x, y in zip(u, v))
            den = n * suu - su * su
            if abs(den) < 1e-9:
                raise RuntimeError("control points are collinear in this axis")
            a = (n * suv - su * sv) / den
            b = (sv - a * su) / n
            return a, b

        ax, bx = fit(px, lon)
        ay, by = fit(py, lat)

        res = []
        for p in pts:
            dlon = (ax * p["px"] + bx) - p["lon"]
            dlat = (ay * p["py"] + by) - p["lat"]
            latm = 111320.0
            lonm = 111320.0 * math.cos(math.radians(p["lat"]))
            res.append(math.hypot(dlon * lonm, dlat * latm))
        rms = math.sqrt(sum(r * r for r in res) / len(res))

        # implied scale from the fit, cross-checked against the printed scale bar
        lonm = 111320.0 * math.cos(math.radians(sum(lat) / len(lat)))
        implied = abs(ax) * lonm
        drift = (implied - m["m_per_px"]) / m["m_per_px"] * 100

        west = ax * fx0 + bx
        east = ax * (fx1 + 1) + bx
        north = ay * fy0 + by
        south = ay * (fy1 + 1) + by
        out[sheet] = {
            "control_points": len(pts),
            "rms_residual_m": round(rms, 1),
            "m_per_px_from_fit": round(implied, 4),
            "m_per_px_from_scalebar": round(m["m_per_px"], 4),
            "scale_drift_pct": round(drift, 2),
            "bounds_wgs84": {"west": west, "east": east, "south": south, "north": north},
            "corners_for_maplibre": [[west, north], [east, north], [east, south], [west, south]],
            "image": f"data/derived/floodmaps/{sheet}.depth.png",
        }
        flag = ""
        if rms > 40:
            flag = "  <-- residual is large, re-check the points"
        elif abs(drift) > 4:
            flag = "  <-- disagrees with the scale bar, re-check the points"
        log(f"  {sheet:16} {len(pts)} pts  rms {rms:6.1f} m  "
            f"scale drift {drift:+5.1f}%{flag}")

        wf = os.path.join(OUTDIR, f"{sheet}.depth.pgw")
        with open(wf, "w") as f:
            f.write(f"{ax}\n0.0\n0.0\n{ay}\n{ax*fx0+bx}\n{ay*fy0+by}\n")

    path = os.path.join(OUTDIR, "_georef.json")
    existing = read_json(path) if os.path.exists(path) else {}
    existing.update(out)
    write_json(path, existing)
    if out:
        log(f"\n{len(existing)} sheet(s) georeferenced -> data/derived/floodmaps/_georef.json")
    return 0


# ---------------------------------------------------------------------------- status
def cmd_status(args):
    def load(p):
        return read_json(p) if os.path.exists(p) else {}
    sheets = load(os.path.join(OUTDIR, "_sheets.json"))
    extr = load(os.path.join(OUTDIR, "_extract.json"))
    geo = load(os.path.join(OUTDIR, "_georef.json"))
    ctrl = load(CONTROL)

    log(f"{'sheet':16}{'pdf':>4}{'render':>8}{'extract':>10}{'points':>8}  georef")
    for s in SHEETS:
        pdf = "yes" if os.path.exists(os.path.join(PDFDIR, f"{s}.pdf")) else "-"
        r = "yes" if s in sheets else "-"
        e = f"{extr[s]['flooded_m2']/1e6:.2f}km2" if s in extr else "-"
        n = len((ctrl.get(s) or {}).get("points") or [])
        g = geo.get(s)
        if not g:
            gtxt = "-"
        elif "rms_residual_m" in g:
            gtxt = f"control points, rms {g['rms_residual_m']:.0f} m"
        elif g.get("control_points"):
            gtxt = (f"assisted, {g['control_points']} control points, "
                    f"SE {g['standard_error_m']:.0f} m")
        elif g.get("confident"):
            gtxt = (f"auto, {g['agree']}/{g['variants_run']} detectors agree "
                    f"within {g['spread_m']:.0f} m")
        else:
            gtxt = (f"NOT accepted ({g.get('agree', 0)}/{g.get('variants_run', 0)} agree, "
                    f"spread {g.get('spread_m', 0):.0f} m) - needs control points")
        log(f"{s:16}{pdf:>4}{r:>8}{e:>10}{n:>8}  {gtxt}")

    ready = [s for s in SHEETS if geo.get(s, {}).get("confident") or
             "rms_residual_m" in geo.get(s, {})]
    log(f"\n{len(ready)}/{len(SHEETS)} sheets georeferenced.")
    if len(ready) < len(SHEETS):
        missing = [s for s in SHEETS if s not in ready]
        log(f"Still needed: {', '.join(missing)}. Set two control points each in "
            "viz/georef.html, then run `georef`.")
    return 0


COMMANDS = {"fetch": cmd_fetch, "render": cmd_render, "extract": cmd_extract,
            "autoref": cmd_autoref, "georef": cmd_georef, "check": cmd_check,
            "status": cmd_status}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        return 1
    return COMMANDS[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
