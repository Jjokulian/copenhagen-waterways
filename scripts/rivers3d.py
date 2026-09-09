#!/usr/bin/env python3
"""Build the 3D scene for viz/rivers3d.html - Copenhagen with the rainwater rivers in it.

This is the proposal drawn on the real city. Three things are shown together, and the
distinction between them is the whole point of the rendering:

  REAL      buildings (OSM), coastline, water, the cloudburst plan's actual alignments,
            the combined-sewer catchments, the polder behind the Amager dyke.
  RECOVERED the 2012 flood model's paths - where water goes when nothing forces it into
            a pipe. Not a proposal; a survey nobody has used this way.
  PROPOSED  which alignments become open channels, which get an interceptor retrofit
            instead, where the diversion nodes sit, and where the two destinations are.

Outputs:
  data/derived/viewer/rivers3d.geojson   the scene
  data/derived/viewer/buildings3d.geojson
  docs/retrofit_section.svg              the manhole / interceptor / sewer arrangement
  docs/routing_logic.svg                 the real-time diversion decision

Usage:  python3 scripts/rivers3d.py     (after rivermap.py)
"""
import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, read_json, write_json

VIEWER = os.path.join(DERIVED, "viewer")
LONM = 111320.0 * math.cos(math.radians(55.68))

SURFACE = {"Skybrudsveje", "Grønne veje", "Forsinkelsesveje", "mix"}
BURIED = {"Skybrudsledning"}
LEVEL_M = 3.2          # metres per storey where only building:levels is tagged
DEFAULT_H = 11.0       # Copenhagen's ordinary 3-4 storey block, where nothing is tagged

# The two destinations, and the diversion nodes between them.
AMAGER_WETLAND = [  # indicative cells on the northern edge of the polder, OUTSIDE the
                    # Natura 2000 corner in the south-west. Indicative, not sited.
    [[12.5620, 55.6100], [12.5880, 55.6100], [12.5880, 55.6230], [12.5620, 55.6230]],
]
KALKGRAV = (12.2088, 55.5478)

# Facilities the routing would use. "status" is the epistemic label and it is the point:
# a location being real is not the same as a capability being verified, and nothing in
# this list has had its permit or its performance checked by this project.
FACILITIES = [
    {"name": "ARC / Amager Bakke",
     "lon": 12.61854, "lat": 55.68458,
     "role": "energy from waste",
     "status": "REAL LOCATION — CAPABILITY NOT VERIFIED",
     "note": "Municipal energy-from-waste, owned by Dragør, Frederiksberg, Hvidovre, "
             "København and Tårnby — the same municipalities that discharge into the "
             "bay. Municipal EfW typically runs below the >1,100 °C / 2-3 s condition "
             "that PFAS destruction needs, and Danish trade reporting describes PFAS as "
             "a live problem for incineration plants rather than a solved one. "
             "**Treat as unsuitable for the destruction branch until its permit and a "
             "fluorine mass balance say otherwise.**"},
    {"name": "SMOKA (approximate)",
     "lon": 12.6350, "lat": 55.6845,
     "role": "hazardous waste reception",
     "status": "REAL FACILITY — LOCATION APPROXIMATE, ROLE NOT VERIFIED",
     "note": "The capital's hazardous-waste receiving station, co-owned by ARC. It is a "
             "reception and transfer point, not a destruction facility. Included because "
             "the collection step has to land somewhere and this is where it already "
             "lands. Coordinates are approximate — geocoding failed and this was placed "
             "from the Prøvestenen area."},
]

# Off the map, and the one that matters most.
NYBORG_NOTE = (
    "Fortum Waste Solutions, Nyborg (the former Kommunekemi, founded 1971) is where "
    "Danish practice already sends spent PFAS media. Secondary sources describe capture "
    "on granular activated carbon and ion-exchange resin followed by high-temperature "
    "incineration above 1,200 °C. **This project has not verified that.** It is a "
    "reported practice, not a measured performance, and the difference is the whole "
    "subject of this section."
)


def line_len(coords):
    return sum(math.hypot((b[0] - a[0]) * LONM, (b[1] - a[1]) * 111320.0)
               for a, b in zip(coords, coords[1:]))


def simplify(ring, min_m=7.0):
    out, last = [], None
    for c in ring:
        if last is not None:
            if math.hypot((c[0] - last[0]) * LONM, (c[1] - last[1]) * 111320.0) < min_m:
                continue
        last = c
        out.append([round(c[0], 5), round(c[1], 5)])
    return out


# --------------------------------------------------------------------- buildings

def build_buildings():
    src = os.path.join(RAW, "osm", "buildings.json")
    if not os.path.exists(src):
        log("no data/raw/osm/buildings.json - skipping buildings")
        return
    els = read_json(src)["elements"]
    feats = []
    for e in els:
        g = e.get("geometry")
        if not g or len(g) < 4:
            continue
        t = e.get("tags", {})
        h = None
        if t.get("height"):
            try:
                h = float(str(t["height"]).split()[0].replace(",", "."))
            except ValueError:
                h = None
        if h is None and t.get("building:levels"):
            try:
                h = float(str(t["building:levels"]).replace(",", ".")) * LEVEL_M
            except ValueError:
                h = None
        if h is None:
            h = DEFAULT_H
        ring = simplify([[p["lon"], p["lat"]] for p in g])
        if len(ring) < 4:
            continue
        # Drop sheds, garages and bike stores. 63,910 buildings across Amager and the
        # inner city is 36 MB of GeoJSON; the small stuff is most of the count and none
        # of the skyline.
        if _ring_area(ring) < 150:
            continue
        if ring[0] != ring[-1]:
            ring.append(ring[0])
        # `a` is the footprint in square metres, carried so the viewer can decide
        # what to draw at a given zoom rather than drawing all 19,000 at every zoom.
        # A skyline needs the large ones; the small ones are only legible close up.
        feats.append({"type": "Feature",
                      "properties": {"h": round(min(max(h, 3.0), 120.0), 1),
                                     "a": int(_ring_area(ring))},
                      "geometry": {"type": "Polygon", "coordinates": [ring]}})
    out = {"type": "FeatureCollection", "features": feats}
    p = os.path.join(VIEWER, "buildings3d.geojson")
    write_json(p, out)
    log(f"  buildings3d.geojson  {len(feats):,} features, "
        f"{os.path.getsize(p)/1e6:.1f} MB")


# --------------------------------------------------------------------- ground

# The scene extent: Copenhagen, Amager, and far enough south to reach Karlstrup.
SCENE = (12.15, 55.50, 12.75, 55.76)     # west, south, east, north


def _clip_ok(ring):
    w, s_, e, n = SCENE
    for x, y in ring:
        if w <= x <= e and s_ <= y <= n:
            return True
    return False


def _simp(ring, min_m):
    out, last = [], None
    for c in ring:
        if last is not None and math.hypot((c[0] - last[0]) * LONM,
                                          (c[1] - last[1]) * 111320.0) < min_m:
            continue
        last = c
        out.append([round(c[0], 5), round(c[1], 5)])
    return out


def _ring_area(ring):
    """Shoelace in metres, good enough for a size filter."""
    a = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        a += (x1 * LONM) * (y2 * 111320.0) - (x2 * LONM) * (y1 * 111320.0)
    return abs(a) / 2


def build_ground():
    """Compact green, water, coast and roads into the committed viewer bundle.

    viz/rivers3d.html cannot read data/raw - it is git-ignored, so it does not exist on
    the deployed site. Everything the page needs has to live in data/derived/viewer/.
    """
    osm = os.path.join(RAW, "osm")
    out = {}

    lc = os.path.join(osm, "landcover.json")
    if os.path.exists(lc):
        feats = []
        for r in read_json(lc):
            ring = r.get("ring") or []
            if len(ring) < 4 or not _clip_ok(ring):
                continue
            if _ring_area(ring) < 2500:
                continue
            g = _simp(ring, 9.0)
            if len(g) < 4:
                continue
            if g[0] != g[-1]:
                g.append(g[0])
            feats.append({"type": "Feature", "properties": {"k": r.get("kind")},
                          "geometry": {"type": "Polygon", "coordinates": [g]}})
        out["ground3d.geojson"] = {"type": "FeatureCollection", "features": feats}

    cl = os.path.join(osm, "coastline.json")
    if os.path.exists(cl):
        feats = []
        for w in read_json(cl):
            if len(w) < 2 or not _clip_ok(w):
                continue
            g = _simp(w, 12.0)
            if len(g) > 1:
                feats.append({"type": "Feature", "properties": {},
                              "geometry": {"type": "LineString", "coordinates": g}})
        out["coast3d.geojson"] = {"type": "FeatureCollection", "features": feats}

    rd = os.path.join(osm, "roads.json")
    if os.path.exists(rd):
        feats = []
        for w in read_json(rd):
            if len(w) < 2 or not _clip_ok(w):
                continue
            if line_len(w) < 220:
                continue
            g = _simp(w, 30.0)
            if len(g) > 1:
                feats.append({"type": "Feature", "properties": {},
                              "geometry": {"type": "LineString", "coordinates": g}})
        out["roads3d.geojson"] = {"type": "FeatureCollection", "features": feats}

    for name, fc in out.items():
        p = os.path.join(VIEWER, name)
        write_json(p, fc)
        log(f"  {name:22} {len(fc['features']):>7,} features, "
            f"{os.path.getsize(p)/1e6:.1f} MB")


# --------------------------------------------------------------------- the scene

def build_scene():
    feats = []
    add = feats.append

    # ---- the cloudburst plan's alignments, reclassified by what they could carry
    counts = collections.Counter()
    lengths = collections.defaultdict(float)
    for f in read_json(os.path.join(RAW, "skp_veje_tunneller_kk.geojson"))["features"]:
        g = f.get("geometry")
        if not g:
            continue
        typ = f["properties"].get("typologi")
        if typ in SURFACE:
            role, note = "open_channel", "planned surface route — could carry a river"
        elif typ in BURIED:
            role, note = "interceptor", "planned as a pipe — retrofit candidate"
        else:
            continue
        lines = ([g["coordinates"]] if g["type"] == "LineString"
                 else g["coordinates"] if g["type"] == "MultiLineString" else [])
        for ln in lines:
            if len(ln) < 2:
                continue
            counts[role] += 1
            lengths[role] += line_len(ln)
            add({"type": "Feature",
                 "properties": {"kind": "river", "role": role, "typologi": typ,
                                "note": note, "klima_id": f["properties"].get("klima_id")},
                 "geometry": {"type": "LineString",
                              "coordinates": [[round(c[0], 6), round(c[1], 6)] for c in ln]}})

    # ---- the gaps: deep modelled water with no surface route planned
    riv = read_json(os.path.join(DERIVED, "rivermap.json"))
    for c in riv["corridors"]:
        add({"type": "Feature",
             "properties": {"kind": "gap", "role": "missing",
                            "area_m2": c["area_m2"], "length_m": c["length_m"],
                            "note": "flood path deeper than 0.5 m with no surface "
                                    "route within 100 m — a river is indicated here "
                                    "and none is planned"},
             "geometry": {"type": "Point", "coordinates": [c["lon"], c["lat"]]}})

    # ---- diversion nodes: real overflow structures on Amager, proposed new function.
    # These are where the combined system already discharges, so they are where a
    # diversion would go. The locations are data; the function is a proposal.
    amager = (12.53, 55.55, 12.70, 55.70)
    n_div = 0
    for f in read_json(os.path.join(RAW, "national", "punkt_rbu_udl.geojson"))["features"]:
        pr, g = f["properties"], f.get("geometry")
        if not g or not str(pr.get("bgv_type", "")).startswith("O"):
            continue
        lon, lat = g["coordinates"][:2]
        if not (amager[0] <= lon <= amager[2] and amager[1] <= lat <= amager[3]):
            continue
        n_div += 1
        add({"type": "Feature",
             "properties": {"kind": "node", "role": "diversion",
                            "name": pr.get("pkt_navn") or "overflow structure",
                            "note": "REAL combined-sewer overflow structure. PROPOSED "
                                    "diversion node: turbidity, conductivity and flow "
                                    "continuously, grab sample on threshold. Clean flow "
                                    "to the wetland, flagged flow held."},
             "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]}})

    # ---- facilities
    for fac in FACILITIES:
        add({"type": "Feature",
             "properties": {"kind": "facility", "role": fac["role"],
                            "name": fac["name"], "status": fac["status"],
                            "note": fac["note"]},
             "geometry": {"type": "Point", "coordinates": [fac["lon"], fac["lat"]]}})

    # ---- a forebay at the wetland inlet: the coarse half of the treatment train
    add({"type": "Feature",
         "properties": {"kind": "destination", "role": "forebay",
                        "name": "Sedimentation forebay",
                        "note": "INDICATIVE. Gross-pollutant trap and a deep, small "
                                "settling cell ahead of the wetland — the part that is "
                                "dredged often, so the wetland behind it is dredged "
                                "rarely."},
         "geometry": {"type": "Polygon",
                      "coordinates": [[[12.5590, 55.6180], [12.5620, 55.6180],
                                       [12.5620, 55.6230], [12.5590, 55.6230],
                                       [12.5590, 55.6180]]]}})

    # ---- destinations
    add({"type": "Feature",
         "properties": {"kind": "destination", "role": "sedimentation",
                        "name": "Vestamager sedimentation wetland",
                        "note": "INDICATIVE. Northern edge of the 1939-43 polder, away "
                                "from the Natura 2000 corner. 11-53 ha would match "
                                "Amager's 1,052 ha of combined-sewered surface."},
         "geometry": {"type": "Polygon",
                      "coordinates": [AMAGER_WETLAND[0] + [AMAGER_WETLAND[0][0]]]}})
    add({"type": "Feature",
         "properties": {"kind": "destination", "role": "heavy_duty",
                        "name": "Karlstrup Kalkgrav",
                        "note": "REJECTED as a receiving water — 14 m deep with poor "
                                "circulation, it would stratify. Shown because it is "
                                "where the heavy-duty branch was proposed, and because "
                                "the four siting criteria came out of assessing it."},
         "geometry": {"type": "Point", "coordinates": list(KALKGRAV)}})

    out = {"type": "FeatureCollection",
           "features": feats,
           "meta": {
               "open_channel_km": round(lengths["open_channel"] / 1000, 1),
               "interceptor_km": round(lengths["interceptor"] / 1000, 1),
               "gaps": len(riv["corridors"]),
               "flood_path_km2": riv["flood_path_km2"],
               "near_surface_pct": riv["near_surface_conveyance_pct"],
               "diversion_nodes": n_div,
               "nyborg_note": NYBORG_NOTE,
           }}
    p = os.path.join(VIEWER, "rivers3d.geojson")
    write_json(p, out)
    log(f"  diversion nodes on Amager: {n_div}")
    log(f"  rivers3d.geojson     {len(feats):,} features, "
        f"{out['meta']['open_channel_km']:,.0f} km open channel, "
        f"{out['meta']['interceptor_km']:,.0f} km interceptor candidate")
    return out["meta"]


# --------------------------------------------------------------------- section

def svg_section():
    """The retrofit: a shallow rain line, how it gets in, and the shaft that serves it.

    Three panels rather than two, because the argument in PROGRAMME.md now leads with
    the light version - leave the sewer where it is - and the detail that makes it
    buildable is the shaft, not the pipe. The heavy variant (drop the sewer a metre)
    stays in the prose; it needs no drawing once the light one is drawn.
    """
    W, H = 1180, 560
    GROUND = 132
    BROWN, BLUE, SOIL = "#7d3a30", "#2f7fb5", "#e6ded2"
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" role="img" aria-label="Street cross-section: the combined '
         f'sewer now, the shallow rain line that leaves it in place, and the '
         f'two-storey shaft with a liftable watertight pan that serves both">',
         '<style>'
         '.t{font:600 13px system-ui,sans-serif;fill:#1c2a33}'
         '.s{font:11px system-ui,sans-serif;fill:#55666f}'
         '.n{font:italic 10.5px system-ui,sans-serif;fill:#7a8892}'
         '.h{font:700 12px system-ui,sans-serif;letter-spacing:.09em}'
         '.dim{stroke:#8b98a2;stroke-width:1;fill:none}'
         '</style>',
         f'<rect width="{W}" height="{H}" fill="#fbfcfd"/>']

    def head(x0, title, colour, sub):
        s.append(f'<text class="h" x="{x0}" y="34" fill="{colour}">{title}</text>')
        s.append(f'<text class="s" x="{x0}" y="52">{sub}</text>')

    def street(x0, w):
        s.append(f'<rect x="{x0}" y="{GROUND}" width="{w}" height="352" fill="{SOIL}"/>')
        s.append(f'<rect x="{x0}" y="{GROUND-12}" width="{w}" height="12" fill="#63707a"/>')
        s.append(f'<text class="s" x="{x0+6}" y="{GROUND-20}">street surface</text>')

    def pipe(cx, cy, r, fill, stroke, lines):
        s.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="3"/>')
        y = cy - (len(lines) - 1) * 8 + 4
        for ln in lines:
            s.append(f'<text class="t" x="{cx}" y="{y}" text-anchor="middle" '
                     f'fill="#fff">{ln}</text>')
            y += 16

    def caption(x0, y, lines):
        for ln in lines:
            s.append(f'<text class="s" x="{x0}" y="{y}">{ln}</text>')
            y += 17

    # ---------------------------------------------------------------- NOW
    x0 = 30
    head(x0, "NOW", "#8e2318", "one pipe, and it fills")
    street(x0, 330)
    s.append(f'<rect x="{x0+52}" y="{GROUND-12}" width="26" height="12" fill="#2b3840"/>')
    s.append(f'<rect x="{x0+54}" y="{GROUND}" width="22" height="152" fill="#c8bda9"/>')
    s.append(f'<text class="n" x="{x0+86}" y="{GROUND+16}">gully &amp; shaft</text>')
    pipe(x0 + 175, GROUND + 182, 42, BROWN, "#5a2620", ["combined", "sewer"])
    s.append(f'<path d="M{x0+65},{GROUND+152} L{x0+65},{GROUND+182} L{x0+133},{GROUND+182}" '
             f'stroke="{BROWN}" stroke-width="9" fill="none"/>')
    s.append(f'<path d="M{x0+310},{GROUND} L{x0+310},{GROUND+182} L{x0+219},{GROUND+182}" '
             f'stroke="#a8705f" stroke-width="6" fill="none"/>')
    s.append(f'<text class="n" x="{x0+304}" y="{GROUND+38}" text-anchor="end">house drain</text>')
    caption(x0, GROUND + 286, ["Rain and sewage share the pipe.",
                               "When it fills, the mixture leaves",
                               "through an overflow, untreated."])

    # -------------------------------------------------------- LIGHT RETROFIT
    x0 = 420
    head(x0, "THE LIGHT VERSION", "#1f7a5a", "the sewer is not touched")
    street(x0, 330)
    s.append(f'<rect x="{x0+52}" y="{GROUND-12}" width="26" height="12" fill="#2b3840"/>')
    s.append(f'<rect x="{x0+54}" y="{GROUND}" width="22" height="238" fill="#c8bda9"/>')
    pipe(x0 + 175, GROUND + 76, 27, BLUE, "#1d5a85", ["rain"])
    s.append(f'<path d="M{x0+65},{GROUND+62} L{x0+65},{GROUND+76} L{x0+146},{GROUND+76}" '
             f'stroke="{BLUE}" stroke-width="9" fill="none"/>')
    s.append(f'<rect x="{x0+54}" y="{GROUND+86}" width="22" height="5" fill="#8b98a2"/>')
    s.append(f'<text class="n" x="{x0+86}" y="{GROUND+94}">pan: the floor of the '
             f'upper storey</text>')
    pipe(x0 + 175, GROUND + 182, 42, BROWN, "#5a2620", ["foul", "sewer"])
    s.append(f'<path class="dim" d="M{x0+232},{GROUND+140} L{x0+232},{GROUND+182}" '
             f'stroke-dasharray="4 3"/>')
    s.append(f'<text class="n" x="{x0+240}" y="{GROUND+166}">same invert as before</text>')
    s.append(f'<path d="M{x0+310},{GROUND} L{x0+310},{GROUND+182} L{x0+219},{GROUND+182}" '
             f'stroke="#a8705f" stroke-width="6" fill="none"/>')
    s.append(f'<text class="n" x="{x0+304}" y="{GROUND+38}" text-anchor="end">house drain,</text>')
    s.append(f'<text class="n" x="{x0+304}" y="{GROUND+52}" text-anchor="end">unchanged</text>')
    caption(x0, GROUND + 286, ["The gully moves to the rain line; nothing",
                               "on the foul side moves at all. Bored shaft",
                               "to shaft, so the road opens at the shafts."])

    # ------------------------------------------------------------ THE SHAFT
    x0 = 810
    head(x0, "THE SHAFT", "#1c2a33", "two storeys, one opening")
    street(x0, 330)
    LX, RX = x0 + 96, x0 + 186          # shaft walls
    s.append(f'<rect x="{LX}" y="{GROUND}" width="{RX-LX}" height="300" fill="#fbfcfd" '
             f'stroke="#8b98a2" stroke-width="2"/>')
    s.append(f'<rect x="{LX-6}" y="{GROUND-12}" width="{RX-LX+12}" height="12" fill="#2b3840"/>')
    s.append(f'<text class="n" x="{RX+10}" y="{GROUND+4}">cover</text>')
    # upper storey: the rain line and the pan
    PAN = GROUND + 118
    s.append(f'<rect x="{LX-70}" y="{PAN-26}" width="70" height="26" fill="{BLUE}" '
             f'stroke="#1d5a85" stroke-width="2"/>')
    s.append(f'<text class="n" x="{LX-70}" y="{PAN-34}">rain line</text>')
    s.append(f'<path d="M{LX+2},{PAN} L{RX-2},{PAN-10}" stroke="#55666f" '
             f'stroke-width="6" fill="none"/>')
    s.append(f'<text class="s" x="{RX+10}" y="{PAN-4}">watertight pan,</text>')
    s.append(f'<text class="s" x="{RX+10}" y="{PAN+13}">falling to the pipe</text>')
    # the lift
    s.append(f'<path d="M{LX+30},{PAN-24} L{LX+30},{PAN-66}" stroke="#1f7a5a" '
             f'stroke-width="2" fill="none" marker-end="url(#up)"/>')
    s.append(f'<path d="M{LX+6},{PAN-72} L{RX-6},{PAN-82}" stroke="#1f7a5a" '
             f'stroke-width="4" stroke-dasharray="6 4" fill="none"/>')
    s.append(f'<text class="n" x="{RX+10}" y="{PAN-76}">lifted, to enter</text>')
    # lower storey
    s.append(f'<path d="M{LX-70},{GROUND+250} L{RX+70},{GROUND+250}" stroke="{BROWN}" '
             f'stroke-width="26" fill="none"/>')
    s.append(f'<text class="n" x="{LX-70}" y="{GROUND+282}">foul sewer, live below</text>')
    for k in range(5):                                  # ladder
        yy = PAN + 22 + k * 24
        s.append(f'<path d="M{RX-26},{yy} L{RX-6},{yy}" stroke="#8b98a2" '
                 f'stroke-width="2" fill="none"/>')
    caption(x0, GROUND + 320, ["Gravity holds the pan down, which is the",
                               "wrong way round for a surcharged sewer:",
                               "it has to be seated by back-pressure, not",
                               "lifted by it. Sealing this storey also closes",
                               "one of the sewer's vents."])

    s.append('<defs><marker id="up" viewBox="0 0 10 10" refX="5" refY="5" '
             'markerWidth="5" markerHeight="5" orient="auto-start-reverse">'
             '<path d="M0,0 L10,5 L0,10 z" fill="#1f7a5a"/></marker></defs>')
    s.append(f'<text class="n" x="{W-30}" y="{H-14}" text-anchor="end">Schematic. Depths '
             f'and diameters are illustrative; the arrangement is the point.</text>')
    s.append("</svg>")
    p = os.path.join(ROOT, "docs", "retrofit_section.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    log("  docs/retrofit_section.svg")


# --------------------------------------------------------------------- routing

def svg_routing():
    W, H = 960, 430
    def box(x, y, w, h, t, sub, fill, stroke):
        o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
             f'stroke="{stroke}" stroke-width="1.6"/>',
             f'<text x="{x+w/2}" y="{y+(22 if sub else h/2+5)}" text-anchor="middle" '
             f'font-family="system-ui,sans-serif" font-size="13" font-weight="600" '
             f'fill="#1c2a33">{t}</text>']
        for i, ln in enumerate(sub or []):
            o.append(f'<text x="{x+w/2}" y="{y+40+i*14}" text-anchor="middle" '
                     f'font-family="system-ui,sans-serif" font-size="11" '
                     f'fill="#55666f">{ln}</text>')
        return o
    def arr(x1, y1, x2, y2, col="#55666f", lab=None):
        o = [f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{col}" stroke-width="2.2" '
             f'marker-end="url(#a)" fill="none"/>']
        if lab:
            o.append(f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2-8}" text-anchor="middle" '
                     f'font-family="system-ui,sans-serif" font-size="11" '
                     f'font-weight="600" fill="{col}">{lab}</text>')
        return o

    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" role="img" aria-label="Real-time routing: clean rainwater to '
         f'the sedimentation wetland, contaminated rainwater to heavy-duty treatment">',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
         'markerHeight="6" orient="auto-start-reverse">'
         '<path d="M0,0 L10,5 L0,10 z" fill="#55666f"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#fbfcfd"/>',
         '<text x="30" y="34" font-family="system-ui,sans-serif" font-size="17" '
         'font-weight="700" fill="#1c2a33">Routing the rain by what is in it</text>']
    s += box(30, 70, 180, 74, "rainwater river", ["surface channel", "or interceptor line"],
             "#e2f1ea", "#1f7a5a")
    s += box(30, 190, 180, 92, "diversion node", ["turbidity, conductivity,", "flow — continuous",
                                                 "grab sample on threshold"],
             "#eef3f6", "#2f7fb5")
    s += arr(120, 144, 120, 188, "#1f7a5a")
    s += box(300, 120, 200, 96, "below threshold", ["no novo-chemical signal", "above the",
                                                   "accumulating background"],
             "#e2f1ea", "#1f7a5a")
    s += box(300, 262, 200, 96, "above threshold", ["a signal, or an unknown", "peak — divert"],
             "#f6e3e0", "#c0392b")
    s += arr(212, 214, 296, 168, "#1f7a5a", "clean")
    s += arr(212, 256, 296, 302, "#c0392b")
    s.append('<text x="240" y="298" font-family="system-ui,sans-serif" font-size="11" '
             'font-weight="600" fill="#c0392b">flagged</text>')
    s += box(590, 120, 200, 96, "Vestamager wetland", ["gravity, passive", "settling and uptake",
                                                      "dredged on schedule"],
             "#e2f1ea", "#1f7a5a")
    s += box(590, 262, 200, 96, "heavy-duty branch", ["holding, then treatment", "and destruction",
                                                     "at specification"],
             "#f6e3e0", "#c0392b")
    s += arr(502, 168, 586, 168, "#1f7a5a")
    s += arr(502, 310, 586, 310, "#c0392b")
    s.append('<text x="690" y="234" text-anchor="middle" font-family="system-ui,sans-serif" '
             'font-size="11" font-style="italic" fill="#7a8892">the cheap default</text>')
    s.append('<text x="690" y="380" text-anchor="middle" font-family="system-ui,sans-serif" '
             'font-size="11" font-style="italic" fill="#7a8892">the expensive exception — '
             'and it can be built later</text>')
    s.append(f'<text x="{W-30}" y="{H-14}" text-anchor="end" font-family="system-ui,sans-serif" '
             f'font-size="10.5" fill="#8c99a2">The threshold is the part nobody has set, '
             f'because nobody measures the events.</text>')
    s.append("</svg>")
    p = os.path.join(ROOT, "docs", "routing_logic.svg")
    with open(p, "w", encoding="utf-8") as f:
        f.write("\n".join(s))
    log("  docs/routing_logic.svg")


def main():
    os.makedirs(VIEWER, exist_ok=True)
    meta = build_scene()
    build_ground()
    build_buildings()
    svg_section()
    svg_routing()
    log(f"\nscene: {meta['open_channel_km']:,.0f} km could be open channel, "
        f"{meta['interceptor_km']:,.0f} km is planned as pipe, "
        f"{meta['gaps']} corridors have neither")
    return 0


if __name__ == "__main__":
    sys.exit(main())
