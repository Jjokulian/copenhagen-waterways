#!/usr/bin/env python3
"""Render the two figures for docs/PROGRAMME.md.

  docs/koege_bugt_system.svg  - the real geography, with the real combined-sewer
                                catchments and the real overflow points, and the
                                proposed elements drawn in a way that cannot be mistaken
                                for a measurement (dashed, labelled INDICATIVE).
  docs/system_flow.svg        - where a raindrop goes now, and where it would go.

SVG rather than a raster because the whole point is that some of this is real and some
of it is a proposal, and that distinction has to survive being zoomed into.

Usage:  python3 scripts/programme_map.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RAW, ROOT, log, read_json

# Map window: Copenhagen at the top, Køge at the bottom, the whole bay in between.
W_LON, E_LON = 12.00, 12.82
S_LAT, N_LAT = 55.34, 55.78
PAD = 46
WIDTH = 980

BAY_MUNICIPALITIES = {"København", "Hvidovre", "Tårnby", "Brøndby", "Vallensbæk",
                      "Ishøj", "Greve", "Solrød", "Køge", "Stevns"}
COMBINED = "Fælleskloakeret"
KALKGRAV = (55.5478, 12.2088, "Karlstrup Kalkgrav")

# Plants discharging to the bay, from the register, with their approved capacity.
PLANT_NAMES = {"AVEDØRE", "KØGE", "TÅRNBY", "MOSEDE", "SOLRØD"}

CSS = """
.sea{fill:#dce8f0}
.land{fill:none;stroke:#8fa3b0;stroke-width:.8}
.comb{fill:#c0392b;fill-opacity:.30;stroke:#c0392b;stroke-width:.4;stroke-opacity:.5}
.ovf{fill:#8e2318;stroke:#fff;stroke-width:.7}
.sep{fill:#6b8fa6;fill-opacity:.55}
.plant{fill:#3d3d3d;stroke:#fff;stroke-width:1}
.pit{fill:#2e7d5b;stroke:#fff;stroke-width:1.4}
.prop{fill:none;stroke:#1f7a5a;stroke-width:2.6;stroke-dasharray:9 5;stroke-linecap:round}
.propfill{fill:#1f7a5a;fill-opacity:.13;stroke:#1f7a5a;stroke-width:1.6;stroke-dasharray:6 4}
.lbl{font:600 12px system-ui,sans-serif;fill:#22303a}
.lbl2{font:11px system-ui,sans-serif;fill:#4a5a66}
.big{font:700 16px system-ui,sans-serif;fill:#22303a}
.key{font:11.5px system-ui,sans-serif;fill:#22303a}
.note{font:italic 11px system-ui,sans-serif;fill:#6b7a85}
"""


def make_proj():
    k = math.cos(math.radians((S_LAT + N_LAT) / 2))
    span_x = (E_LON - W_LON) * k
    span_y = N_LAT - S_LAT
    inner = WIDTH - 2 * PAD
    scale = inner / span_x
    height = span_y * scale + 2 * PAD
    def p(lon, lat):
        return (PAD + (lon - W_LON) * k * scale,
                height - PAD - (lat - S_LAT) * scale)
    return p, WIDTH, height


def path_from(coords, p, close=False, min_px=1.2):
    """Build an SVG path from nested coordinate lists, clipped crudely to the window.

    Points closer together than min_px are dropped: the OSM coastline for this region is
    132,000 vertices and none of the detail below a pixel survives rendering anyway.
    """
    out = []
    def ring(cs):
        pts = []
        last = None
        for c in cs:
            if not (W_LON - 0.3 <= c[0] <= E_LON + 0.3 and S_LAT - 0.3 <= c[1] <= N_LAT + 0.3):
                if pts:
                    out.append(pts)
                    pts = []
                continue
            x, y = p(c[0], c[1])
            if last is not None and abs(x - last[0]) + abs(y - last[1]) < min_px:
                continue
            last = (x, y)
            pts.append(f"{x:.1f},{y:.1f}")
        if pts:
            out.append(pts)
    def walk(c):
        if not c:
            return
        if isinstance(c[0], (int, float)):
            return
        if isinstance(c[0][0], (int, float)):
            ring(c)
        else:
            for x in c:
                walk(x)
    walk(coords)
    segs = [f"M{' L'.join(s)}" + ("Z" if close else "") for s in out if len(s) > 1]
    return " ".join(segs)


def cmd_map():
    p, w, h = make_proj()
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
         f'width="{w:.0f}" height="{h:.0f}" role="img" '
         f'aria-label="Køge Bugt: the combined-sewer catchments that drain to it, '
         f'the overflow structures, and a proposed alternative">',
         f"<style>{CSS}</style>",
         f'<rect class="sea" x="0" y="0" width="{w:.0f}" height="{h:.0f}"/>']

    # --- coastline (real)
    coast = read_json(os.path.join(RAW, "osm", "coastline.json"))
    d = path_from(coast, p)
    s.append(f'<path class="land" d="{d}"/>')

    # --- combined-sewer catchments (real)
    n_comb = 0
    ds = []
    for f in read_json(os.path.join(RAW, "sp_kloakoplande.geojson"))["features"]:
        if (f["properties"].get("kloaksystem_status") or "") != COMBINED:
            continue
        if not f["geometry"]:
            continue
        n_comb += 1
        ds.append(path_from(f["geometry"]["coordinates"], p, close=True))
    s.append(f'<path class="comb" d="{" ".join(x for x in ds if x)}"/>')

    # --- discharge points (real)
    n_ovf = n_sep = 0
    ovf, sep = [], []
    for f in read_json(os.path.join(RAW, "national", "punkt_rbu_udl.geojson"))["features"]:
        pr = f["properties"]
        if pr.get("komm_navn") not in BAY_MUNICIPALITIES or not f["geometry"]:
            continue
        lon, lat = f["geometry"]["coordinates"][:2]
        if not (W_LON <= lon <= E_LON and S_LAT <= lat <= N_LAT):
            continue
        x, y = p(lon, lat)
        if str(pr.get("bgv_type", "")).startswith("O"):
            n_ovf += 1
            ovf.append(f'<circle class="ovf" cx="{x:.1f}" cy="{y:.1f}" r="3.4"/>')
        else:
            n_sep += 1
            sep.append(f'<circle class="sep" cx="{x:.1f}" cy="{y:.1f}" r="1.5"/>')
    s += sep + ovf

    # --- treatment plants (real)
    n_pl = 0
    for f in read_json(os.path.join(RAW, "national", "punkt_rens_udl.geojson"))["features"]:
        pr = f["properties"]
        if pr.get("komm_navn") not in BAY_MUNICIPALITIES or not f["geometry"]:
            continue
        if (pr.get("godk_pe") or 0) < 20000:
            continue
        lon, lat = f["geometry"]["coordinates"][:2]
        if not (W_LON <= lon <= E_LON and S_LAT <= lat <= N_LAT):
            continue
        x, y = p(lon, lat)
        n_pl += 1
        s.append(f'<rect class="plant" x="{x-4:.1f}" y="{y-4:.1f}" width="8" height="8"/>')
        s.append(f'<text class="lbl2" x="{x+8:.1f}" y="{y+4:.1f}">'
                 f'{pr.get("pkt_navn","").title()} · {pr.get("godk_pe"):,} PE</text>')

    # --- Karlstrup Kalkgrav (real location, existing pump station)
    kx, ky = p(KALKGRAV[1], KALKGRAV[0])
    s.append(f'<circle class="pit" cx="{kx:.1f}" cy="{ky:.1f}" r="7"/>')
    s.append(f'<text class="lbl" x="{kx-11:.1f}" y="{ky+4:.1f}" text-anchor="end">'
             f'{KALKGRAV[2]}</text>')
    s.append(f'<text class="lbl2" x="{kx-11:.1f}" y="{ky+18:.1f}" text-anchor="end">'
             f'held 4 m below sea level; already pumps</text>')
    s.append(f'<text class="lbl2" x="{kx-11:.1f}" y="{ky+31:.1f}" text-anchor="end">'
             f'600,000 m³/yr into the bay</text>')

    # --- PROPOSED, drawn so it cannot be read as a measurement
    ax0, ay0 = p(12.30, 55.44)
    ax1, ay1 = p(12.60, 55.60)
    s.append(f'<rect class="propfill" x="{ax0:.1f}" y="{ay1:.1f}" '
             f'width="{ax1-ax0:.1f}" height="{ay0-ay1:.1f}" rx="10"/>')
    s.append(f'<text class="lbl" x="{(ax0+ax1)/2:.1f}" y="{(ay0+ay1)/2:.1f}" '
             f'text-anchor="middle" fill="#1f7a5a">extractive aquaculture</text>')
    s.append(f'<text class="note" x="{(ax0+ax1)/2:.1f}" y="{(ay0+ay1)/2+15:.1f}" '
             f'text-anchor="middle">indicative zone — 1–6 km² would match</text>')
    s.append(f'<text class="note" x="{(ax0+ax1)/2:.1f}" y="{(ay0+ay1)/2+28:.1f}" '
             f'text-anchor="middle">the bay\'s own overflow nitrogen load</text>')

    # indicative surface-water corridors from the combined catchments inland
    for (a_lon, a_lat), (b_lon, b_lat) in [
        ((12.50, 55.700), (12.36, 55.660)),
        ((12.52, 55.665), (12.38, 55.620)),
        ((12.47, 55.640), (12.30, 55.600)),
    ]:
        x1, y1 = p(a_lon, a_lat)
        x2, y2 = p(b_lon, b_lat)
        s.append(f'<path class="prop" d="M{x1:.1f},{y1:.1f} '
                 f'Q{(x1+x2)/2:.1f},{(y1+y2)/2-18:.1f} {x2:.1f},{y2:.1f}"/>')
    lx, ly = p(12.28, 55.655)
    s.append(f'<text class="lbl" x="{lx:.1f}" y="{ly:.1f}" text-anchor="end" '
             f'fill="#1f7a5a">rainwater rivers, inland</text>')
    s.append(f'<text class="note" x="{lx:.1f}" y="{ly+14:.1f}" text-anchor="end">'
             f'indicative — direction, not alignment</text>')

    # --- title and key
    s.append(f'<text class="big" x="{PAD}" y="{PAD-16:.0f}">Køge Bugt: what drains into it</text>')
    ky0 = h - PAD - 96
    key = [
        ("comb", f"combined-sewer catchment ({n_comb} in Copenhagen)", "rect"),
        ("ovf", f"combined-sewer overflow structure ({n_ovf})", "circ"),
        ("sep", f"separate stormwater outfall ({n_sep})", "circ"),
        ("plant", f"treatment plant ≥20,000 PE ({n_pl})", "rect"),
        ("pit", "flooded chalk quarry", "circ"),
        ("propfill", "PROPOSED — not built, not sited", "rect"),
    ]
    s.append(f'<rect x="{PAD-8}" y="{ky0-16:.0f}" width="330" height="112" rx="6" '
             f'fill="#ffffff" fill-opacity=".82"/>')
    for i, (cls, lab, shape) in enumerate(key):
        yy = ky0 + i * 17
        if shape == "rect":
            s.append(f'<rect class="{cls}" x="{PAD}" y="{yy-8:.0f}" width="13" height="10"/>')
        else:
            s.append(f'<circle class="{cls}" cx="{PAD+6}" cy="{yy-3:.0f}" r="3.6"/>')
        s.append(f'<text class="key" x="{PAD+21}" y="{yy:.0f}">{lab}</text>')

    s.append(f'<text class="note" x="{w-PAD}" y="{h-14:.0f}" text-anchor="end">'
             f'Coastline: OpenStreetMap · catchments: Københavns Kommune · '
             f'outfalls: Miljøgis/PULS · green: proposal, not data</text>')
    s.append("</svg>")

    path = os.path.join(ROOT, "docs", "koege_bugt_system.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    log(f"wrote docs/koege_bugt_system.svg  ({n_comb} catchments, {n_ovf} overflows, "
        f"{n_sep} separate outfalls, {n_pl} plants)")


# --------------------------------------------------------------------- flow diagram

def box(x, y, w, h, label, sub, fill, stroke, tc="#1c2a33"):
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" '
         f'stroke="{stroke}" stroke-width="1.4"/>',
         f'<text x="{x+w/2}" y="{y+(20 if sub else h/2+5)}" text-anchor="middle" '
         f'font="600 13px system-ui" font-family="system-ui,sans-serif" '
         f'font-size="13" font-weight="600" fill="{tc}">{label}</text>']
    if sub:
        for i, line in enumerate(sub):
            o.append(f'<text x="{x+w/2}" y="{y+38+i*13}" text-anchor="middle" '
                     f'font-family="system-ui,sans-serif" font-size="11" '
                     f'fill="#55666f">{line}</text>')
    return o


def arrow(x1, y1, x2, y2, colour="#55666f", dash=""):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{colour}" stroke-width="2"{da} '
            f'marker-end="url(#a)"/>')


def cmd_flow():
    W, H = 980, 560
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" role="img" aria-label="Where a raindrop goes now, '
         f'and where it would go">',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
         'markerHeight="6" orient="auto-start-reverse">'
         '<path d="M0,0 L10,5 L0,10 z" fill="#55666f"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#fbfcfd"/>',
         '<text x="30" y="34" font-family="system-ui,sans-serif" font-size="17" '
         'font-weight="700" fill="#1c2a33">Where a raindrop goes</text>']

    # ---- NOW
    s.append('<text x="30" y="70" font-family="system-ui,sans-serif" font-size="13" '
             'font-weight="600" fill="#8e2318">NOW — 90.7% of Copenhagen</text>')
    y = 88
    s += box(30, y, 175, 52, "rain on a street", None, "#eef3f6", "#b9c8d2")
    s += box(30, y + 78, 175, 52, "gully", ["straight into the sewer"], "#eef3f6", "#b9c8d2")
    s += box(30, y + 156, 175, 64, "combined sewer",
             ["rain + sewage, one pipe"], "#f6e3e0", "#c0392b")
    s += box(30, y + 248, 175, 78, "basin",
             ["holds it — until it fills,", "then scours what settled"], "#f6e3e0", "#c0392b")
    s.append(arrow(117, y + 52, 117, y + 76, "#8e2318"))
    s.append(arrow(117, y + 130, 117, y + 154, "#8e2318"))
    s.append(arrow(117, y + 220, 117, y + 246, "#8e2318"))
    s += box(245, y + 156, 150, 64, "treatment works",
             ["dry weather only"], "#eef3f6", "#b9c8d2")
    s.append(arrow(205, y + 188, 243, y + 188))
    s += box(245, y + 262, 150, 64, "THE SEA",
             ["untreated, on a threshold"], "#f3cdc7", "#8e2318")
    s.append(arrow(205, y + 292, 243, y + 292, "#8e2318"))
    s.append('<text x="320" y="' + str(y + 348) + '" text-anchor="middle" '
             'font-family="system-ui,sans-serif" font-size="11" font-style="italic" '
             'fill="#8e2318">fat, solids, sludge, metals — all of it, in hours</text>')

    # ---- PROPOSED
    s.append('<text x="545" y="70" font-family="system-ui,sans-serif" font-size="13" '
             'font-weight="600" fill="#1f7a5a">PROPOSED</text>')
    s += box(545, y, 175, 52, "rain on a street", None, "#eef3f6", "#b9c8d2")
    s += box(545, y + 78, 175, 64, "surface channel",
             ["a river, not a gully"], "#e2f1ea", "#1f7a5a")
    s += box(545, y + 168, 175, 64, "wetland / basin",
             ["settles and takes up"], "#e2f1ea", "#1f7a5a")
    s.append(arrow(632, y + 52, 632, y + 76, "#1f7a5a"))
    s.append(arrow(632, y + 142, 632, y + 166, "#1f7a5a"))
    s += box(545, y + 258, 175, 78, "terminal water",
             ["quarry, lake, watercourse —", "an outlet that is not the sea"],
             "#e2f1ea", "#1f7a5a")
    s.append(arrow(632, y + 232, 632, y + 256, "#1f7a5a"))
    s += box(770, y + 78, 175, 64, "sewer",
             ["sewage only, always full"], "#eef3f6", "#b9c8d2")
    s += box(770, y + 168, 175, 64, "treatment works",
             ["never bypassed"], "#eef3f6", "#b9c8d2")
    s.append(arrow(857, y + 142, 857, y + 166))
    s += box(770, y + 258, 175, 78, "THE SEA",
             ["treated effluent only"], "#dfeef6", "#2b6f9c")
    s.append(arrow(857, y + 232, 857, y + 256))
    s.append('<text x="857" y="' + str(y + 358) + '" text-anchor="middle" '
             'font-family="system-ui,sans-serif" font-size="11" font-style="italic" '
             'fill="#2b6f9c">no threshold, no bypass, no scour event</text>')

    s.append(f'<text x="{W-30}" y="{H-14}" text-anchor="end" '
             f'font-family="system-ui,sans-serif" font-size="10.5" fill="#8c99a2">'
             f'The left column is Copenhagen as built. The right is an argument.</text>')
    s.append("</svg>")

    path = os.path.join(ROOT, "docs", "system_flow.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    log("wrote docs/system_flow.svg")


def main():
    cmd_flow()
    cmd_map()
    return 0


if __name__ == "__main__":
    sys.exit(main())
