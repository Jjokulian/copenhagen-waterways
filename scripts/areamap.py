#!/usr/bin/env python3
"""The map that shows when the data exists, not just what it says.

An analysis published in 2025 that rests on a relation fitted to 1990-2012 looks
exactly like an analysis published in 2025. The gap is invisible in the text and
invisible on a normal map. So this draws the third axis: for every marine water
body, which streams of observation exist there and over which years each one runs.

Two panels. The map colours each of the 123 areas by how much is actually known
about it - both a fitted model and a repeated observation, one of the two, or
neither. The timeline underneath draws the selected area's streams against a
calendar, with the 2012 line marked, because that is where the fitted window ends
and where several of the things it would need to explain begin.

Reads data/derived/areas.json (from scripts/areas.py) and the raw marine geometry.
Writes docs/data/areas/geometry.json and docs/areas.html.

Usage:  python3 scripts/areamap.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, read_json, write_json

NAT = os.path.join(RAW, "national")
DEST = os.path.join(ROOT, "docs", "data", "areas")
HTML = os.path.join(ROOT, "docs", "areas.html")

TOL = 0.0015        # Douglas-Peucker tolerance in degrees, ~110 m
MIN_RING_DEG2 = 2e-5  # drop rings smaller than this; islets, not water bodies
PREC = 4            # ~10 m


def perp(p, a, b):
    (x, y), (x1, y1), (x2, y2) = p, a, b
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(x - x1, y - y1)
    t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


def simplify(pts, tol):
    """Douglas-Peucker, iterative so a 100k-vertex ring does not blow the stack."""
    if len(pts) < 3:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        worst, wi = -1.0, None
        for k in range(i + 1, j):
            d = perp(pts[k], pts[i], pts[j])
            if d > worst:
                worst, wi = d, k
        if worst > tol:
            keep[wi] = True
            stack.append((i, wi))
            stack.append((wi, j))
    return [p for p, k in zip(pts, keep) if k]


def ring_area(r):
    return abs(sum(r[i][0] * r[i + 1][1] - r[i + 1][0] * r[i][1]
                   for i in range(len(r) - 1))) / 2.0


def build_geometry():
    feats = read_json(os.path.join(NAT, "marin_overordnet.geojson"))["features"]
    out, before, after = {}, 0, 0
    for f in feats:
        rings = []
        for poly in f["geometry"]["coordinates"]:
            for ring in poly:
                before += len(ring)
                if ring_area(ring) < MIN_RING_DEG2:
                    continue
                s = simplify(ring, TOL)
                if len(s) >= 4:
                    rings.append([[round(x, PREC), round(y, PREC)] for x, y in s])
                    after += len(s)
        if rings:
            rings.sort(key=lambda r: -ring_area(r))
            out[f["properties"]["ov_id"]] = rings
    log(f"  geometry: {before:,} -> {after:,} vertices ({100*after/before:.1f}%), "
        f"{len(out)} areas with drawable rings")
    return out


def bathing_points():
    """Station positions and their first/last year, for the shore dots."""
    yrs = [f"{y:02d}" for y in list(range(91, 100)) + list(range(0, 19))]
    num = {y: (1900 + int(y) if int(y) >= 91 else 2000 + int(y)) for y in yrs}
    ok = {"Excellent", "Good", "Good or Sufficient", "Sufficient", "Poor"}
    pts = []
    for p in (f["properties"] for f in
              read_json(os.path.join(NAT, "badevand.geojson"))["features"]):
        ys = [num[y] for y in yrs if p.get("quality_" + y) in ok]
        if ys:
            pts.append([round(p["longitude"], 4), round(p["latitude"], 4),
                        p.get("wbid") or "", min(ys), max(ys)])
    return pts


def main():
    os.makedirs(DEST, exist_ok=True)
    areas = read_json(os.path.join(DERIVED, "areas.json"))
    geom = build_geometry()
    bath = bathing_points()

    # Trim the per-area record to what the page draws.
    slim = {}
    for k, r in areas["areas"].items():
        if k not in geom:
            continue
        b = r["observation"].get("bathing") or {}
        slim[k] = {
            "n": r["name"], "a": r["area_km2"], "t": r["type"], "c": r["catchment"],
            "cat": r["category"], "m": 1 if r["has_statistical_model"] else 0,
            "bs": b.get("stations", 0), "bi": b.get("informative_stations", 0),
            "br": b.get("internal_r"), "bsub": b.get("sub_excellent_share"),
            "bfy": b.get("first_year"), "bly": b.get("last_year"),
            "rbu": (r["pressure"].get("rbu") or {}).get("n", 0),
            "vol": (r["pressure"].get("rbu") or {}).get("basin_m3", 0),
            "pe": (r["pressure"].get("rens") or {}).get("pe", 0),
            "rens": (r["pressure"].get("rens") or {}).get("n", 0),
            "hav": (r["pressure"].get("havdam") or {}).get("n", 0),
            "klap": (r["pressure"].get("klap") or {}).get("n", 0),
            "rst": (r["pressure"].get("raastof") or {}).get("n", 0),
            "hz": (r["observation"].get("hazardous") or {}).get("stations", 0),
            "hzy": (r["observation"].get("hazardous") or {}).get("first_year"),
            "streams": r["streams"], "gaps": r["not_modelled"],
        }
    payload = {"areas": slim, "geometry": geom, "bathing": bath,
               "cum_hoc": areas["cum_hoc"]["tests"]}
    write_json(os.path.join(DEST, "areas.json"), payload)
    size = os.path.getsize(os.path.join(DEST, "areas.json"))
    log(f"  wrote docs/data/areas/areas.json ({size/1e6:.1f} MB)")

    with open(HTML, "w", encoding="utf-8") as f:
        f.write(PAGE)
    log(f"  wrote docs/areas.html ({os.path.getsize(HTML):,} chars)")
    return 0


PAGE = r"""<!doctype html>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>What is known, where, and when</title>
<style>
:root{
  --ground:#f6f5f2; --panel:#fffefb; --ink:#1c1d22; --ink2:#54565f; --ink3:#8b8d97;
  --line:#dedcd6; --sea:#eceff1;
  --k0:#c9ccd1; --k1:#a8c4d8; --k2:#6f9fc4; --k3:#2f6a95;
  --warn:#b4532f; --accent:#2f6a95;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#15161a; --panel:#1c1e23; --ink:#e9e8e4; --ink2:#a6a8b1; --ink3:#70737d;
  --line:#2c2f36; --sea:#22252b;
  --k0:#3a3e46; --k1:#3f5d75; --k2:#5a8cb0; --k3:#8fbcd9;
  --warn:#e0866a; --accent:#8fbcd9;
}}
:root[data-theme="dark"]{
  --ground:#15161a; --panel:#1c1e23; --ink:#e9e8e4; --ink2:#a6a8b1; --ink3:#70737d;
  --line:#2c2f36; --sea:#22252b;
  --k0:#3a3e46; --k1:#3f5d75; --k2:#5a8cb0; --k3:#8fbcd9;
  --warn:#e0866a; --accent:#8fbcd9;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font:14px/1.55 ui-sans-serif,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
header{padding:26px 30px 16px;border-bottom:1px solid var(--line)}
h1{margin:0 0 6px;font-size:23px;font-weight:640;letter-spacing:-.01em;text-wrap:balance}
header p{margin:0;max-width:66ch;color:var(--ink2)}
header a{color:var(--accent)}
.wrap{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:0;align-items:stretch}
@media(max-width:900px){.wrap{grid-template-columns:1fr}}
#mapbox{position:relative;padding:14px 8px 0 18px;min-width:0}
svg{width:100%;height:auto;display:block}
.wb{stroke:var(--panel);stroke-width:.4;cursor:pointer}
.wb:hover{stroke:var(--ink);stroke-width:1.1}
.wb.sel{stroke:var(--ink);stroke-width:1.6}
.dot{fill:var(--ink2);opacity:.5;pointer-events:none}
aside{background:var(--panel);border-left:1px solid var(--line);padding:20px 20px 28px;
  min-width:0;overflow-wrap:anywhere}
@media(max-width:900px){aside{border-left:0;border-top:1px solid var(--line)}}
aside h2{margin:0 0 2px;font-size:17px;font-weight:640;letter-spacing:-.01em}
.sub{color:var(--ink3);font-size:12px;margin-bottom:14px}
dl{display:grid;grid-template-columns:auto 1fr;gap:3px 12px;margin:0 0 16px;font-size:13px}
dt{color:var(--ink3)} dd{margin:0;text-align:right;font-variant-numeric:tabular-nums}
.legend{display:flex;flex-wrap:wrap;gap:6px 14px;padding:10px 18px 14px;font-size:12px;
  color:var(--ink2)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:11px;height:11px;border-radius:2px;display:inline-block}
h3{font-size:12px;text-transform:uppercase;letter-spacing:.07em;color:var(--ink3);
  margin:18px 0 7px;font-weight:600}
.tl{position:relative;margin:0 0 4px;font-size:12px}
.tlrow{display:grid;grid-template-columns:1fr;margin-bottom:9px}
.tllab{color:var(--ink2);margin-bottom:2px}
.tlbar{position:relative;height:9px;background:var(--sea);border-radius:2px}
.tlbar i{position:absolute;top:0;bottom:0;background:var(--k2);border-radius:2px;
  display:block}
.axis{position:relative;height:15px;border-top:1px solid var(--line);margin-top:4px}
.axis b{position:absolute;top:2px;font-weight:400;color:var(--ink3);font-size:11px;
  transform:translateX(-50%)}
.cut{position:absolute;top:-4px;bottom:0;width:1px;background:var(--warn)}
.gaps{margin:0;padding-left:16px;font-size:12.5px;color:var(--ink2)}
.gaps li{margin-bottom:5px}
.none{color:var(--ink3);font-style:italic;font-size:12.5px}
.hint{padding:0 18px 18px;color:var(--ink3);font-size:12px;max-width:70ch}

/* explorer */
#explore h4{margin:16px 0 6px;font-size:12.5px;letter-spacing:.03em;
  text-transform:uppercase;color:var(--ink3);font-weight:640}
.cov{margin:0 0 9px}
.covlab{font-size:12px;color:var(--ink2);margin-bottom:2px}
.covlab b{font-weight:500;color:var(--warn);font-size:11px;cursor:help}
.covrow{display:flex;align-items:center;gap:6px;margin:1px 0}
.covrow span{width:38px;flex:0 0 auto;font-size:10.5px;color:var(--ink3)}
.covcells{display:grid;grid-template-columns:repeat(47,1fr);gap:1px;flex:1 1 auto}
.covcells.s12{grid-template-columns:repeat(12,1fr)}
.covcells i{display:block;height:9px;background:var(--k3);border-radius:1px}
.annual{font-size:11.5px;color:var(--ink2);border-left:2px solid var(--warn);
  padding-left:7px;margin:8px 0}
.pick{display:flex;gap:6px;margin:4px 0 10px}
.pick select{flex:1 1 0;min-width:0;font:inherit;font-size:11.5px;padding:3px 4px;
  background:var(--panel);color:var(--ink);border:1px solid var(--line);border-radius:4px}
.pane{margin:0 0 8px}
.plab{font-size:11.5px;color:var(--ink2);margin-bottom:1px}
.spark{width:100%;height:44px;display:block}
.spark .pts circle{fill:var(--k3)}
.scale{display:flex;justify-content:space-between;font-size:10px;color:var(--ink3)}
.tnote{font-size:11px;color:var(--ink3);margin:2px 0 10px;line-height:1.45}
.scat{position:relative;margin:6px 0 4px;padding:0 0 14px 4px}
.scat svg{width:100%;max-width:230px;height:auto;display:block;
  border-left:1px solid var(--line);border-bottom:1px solid var(--line)}
.scat .pts circle{fill:var(--k2);opacity:.75}
.axl{font-size:10px;color:var(--ink3)}
.axl.y{position:absolute;left:-2px;top:0;transform-origin:0 0;
  transform:rotate(90deg) translateY(-100%);white-space:nowrap}
.plain{font-size:12px;line-height:1.5;color:var(--ink2);
  background:var(--sea);border-radius:5px;padding:8px 9px;margin:6px 0 0}
.plain b{color:var(--ink)}

.sitefoot{margin:34px 0 0;padding:16px 30px 26px;border-top:1px solid var(--line);
  font-size:12.5px;line-height:1.6;color:var(--ink3)}
.sitefoot strong{color:var(--ink2);font-weight:600}
.sitefoot a{color:var(--accent)}
.sitefoot p{margin:0 0 5px;max-width:78ch}
</style>

<header>
  <h1>What is known, where, and when</h1>
  <p>Denmark's 123 marine water bodies, coloured by how much is actually known about
  each one, with the years each stream of observation covers. Click an area. The red
  line on the timeline is 2012 — where the fitted window ends, and where several of the
  things it is asked to explain begin. Method:
  <a href="./#OBSERVING.md">OBSERVING.md</a> and <a href="./#AREAS.md">AREAS.md</a>.</p>
</header>

<div class="legend">
  <span><i class="sw" style="background:var(--k3)"></i> fitted model and repeated observation</span>
  <span><i class="sw" style="background:var(--k2)"></i> fitted model only</span>
  <span><i class="sw" style="background:var(--k1)"></i> repeated observation only</span>
  <span><i class="sw" style="background:var(--k0)"></i> neither</span>
</div>

<div class="wrap">
  <div id="mapbox"><svg id="map" viewBox="0 0 640 560" role="img"
      aria-label="Map of Danish marine water bodies"></svg></div>
  <aside id="panel"><p class="none">Loading…</p></aside>
</div>
<p class="hint"><b>The water bodies on this map are a model assumption, not a
feature of the sea.</b> They are administrative polygons drawn for the Water
Framework Directive. Every figure computed inside one — including the colour — is a
statement about that partition as much as about the water, and whether the sea
changes where these lines run is an open question rather than a settled one. Even a
name as obviously singular as “Roskilde Fjord” is a claim about the water and not a
fact about it.</p>
<p class="hint"><b>Colour is coverage by two named layers, and nothing wider.</b>
“Fitted model” means DCE (2015) published a statistical relation between nutrient
load and an indicator for this area, fitted on 1990–2012 data. “Repeated
observation” means at least one bathing station with a multi-year record. Those two
layers are counted because they are what the water-plan assessment leans on — they
are <b>not</b> a census of what Denmark measures, and an earlier version of this
caption said they were.</p>
<p class="hint"><b>Two cautions, because this map is easy to over-read.</b> First,
the requirement does not rest only on what is coloured here. Alongside the fitted
relations sit 3D mechanistic models that resolve stratification and oxygen at depth,
an eelgrass transect programme, and an annual oxygen-deficit survey — reconstructed
from the primary method documents in <a href="../#GRUNDLAGET.md">Grundlaget</a>. A
map that showed only these two layers and called itself the state of knowledge would
be arguing against a thinner case than the one that exists.</p>
<p class="hint">Second, a pale area is a statement about <i>these layers</i> in
<i>this extract</i>, never about the sea. ODA’s own topic extracts carry light
casts back to 1980 and CTD profiles back to 1970 at stations this colouring does not
count, and what a coverage figure is missing is itemised in
<a href="../#AREAS.md">There is no Denmark</a>. The fitting window also ends in 2012,
which is fourteen years before the policy it is used to support — that gap is the
subject rather than a footnote.</p>

<script>
const T0 = 1985, T1 = 2026;
const $ = s => document.querySelector(s);
let D = null, sel = null;

fetch("data/areas/areas.json").then(r => r.json()).then(d => { D = d; draw(); });

function knowledge(a){ return (a.m ? 2 : 0) + (a.bs > 0 ? 1 : 0); }
const KCOL = ["var(--k0)","var(--k1)","var(--k2)","var(--k3)"];

function draw(){
  const svg = $("#map"), W = 640, H = 560, PAD = 12;
  let x0=99,x1=-99,y0=99,y1=-99;
  for(const rs of Object.values(D.geometry)) for(const r of rs) for(const [x,y] of r){
    if(x<x0)x0=x; if(x>x1)x1=x; if(y<y0)y0=y; if(y>y1)y1=y; }
  const midlat = (y0+y1)/2, kx = Math.cos(midlat*Math.PI/180);
  const sx = (W-2*PAD)/((x1-x0)*kx), sy = (H-2*PAD)/(y1-y0), s = Math.min(sx,sy);
  const ox = PAD + ((W-2*PAD) - (x1-x0)*kx*s)/2;
  const oy = PAD + ((H-2*PAD) - (y1-y0)*s)/2;
  const px = x => ox + (x-x0)*kx*s, py = y => oy + (y1-y)*s;

  const ids = Object.keys(D.geometry).sort((a,b)=> D.areas[b].a - D.areas[a].a);
  let out = "";
  for(const id of ids){
    const a = D.areas[id]; if(!a) continue;
    let dd = "";
    for(const r of D.geometry[id]){
      dd += "M" + r.map(([x,y]) => px(x).toFixed(1)+","+py(y).toFixed(1)).join("L") + "Z";
    }
    out += `<path class="wb" id="p_${id}" d="${dd}" fill="${KCOL[knowledge(a)]}"><title>${
      esc(a.n)} — ${a.a.toLocaleString()} km²</title></path>`;
  }
  for(const [x,y] of D.bathing) out += `<circle class="dot" cx="${px(x).toFixed(1)}" cy="${
    py(y).toFixed(1)}" r="1.3"/>`;
  svg.innerHTML = out;
  svg.querySelectorAll(".wb").forEach(p =>
    p.addEventListener("click", () => select(p.id.slice(2))));
  select(ids.find(i => D.areas[i] && D.areas[i].n.indexOf("Køge") === 0) || ids[0]);
}

const esc = s => String(s).replace(/[&<>]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));
const nm = v => v == null ? "—" : v.toLocaleString();

function select(id){
  if(sel) { const e = $("#p_"+sel); if(e) e.classList.remove("sel"); }
  sel = id; const e = $("#p_"+id); if(e) e.classList.add("sel");
  const a = D.areas[id];
  const pos = v => ((Math.min(Math.max(v,T0),T1) - T0) / (T1-T0) * 100);
  let tl = "";
  for(const s of a.streams){
    const from = pos(s.from), to = pos(s.to);
    tl += `<div class="tlrow"><div class="tllab">${esc(s.stream)}${
      s.n ? " · " + s.n : ""} <span style="color:var(--ink3)">${s.from}–${s.to}</span></div>
      <div class="tlbar"><i style="left:${from}%;width:${Math.max(1.2,to-from)}%"></i></div></div>`;
  }
  if(!a.streams.length) tl = `<p class="none">No stream of repeated marine observation
    exists for this area in the open data.</p>`;
  let ax = `<div class="axis"><div class="cut" style="left:${pos(2012)}%"></div>`;
  for(const y of [1990,2000,2010,2020]) ax += `<b style="left:${pos(y)}%">${y}</b>`;
  ax += `</div>`;

  $("#panel").innerHTML = `
    <h2>${esc(a.n)}</h2>
    <div class="sub">${esc(id)} · ${esc(a.cat)} · type ${esc(a.t)}${
      a.c ? " · " + esc(a.c) : ""}</div>
    <dl>
      <dt>Area</dt><dd>${a.a.toLocaleString()} km²</dd>
      <dt>Fitted load→indicator model</dt><dd>${a.m ? "yes (1990–2012)" : "none"}</dd>
      <dt>Bathing stations</dt><dd>${nm(a.bs)}${a.bfy ? ` (${a.bfy}–${a.bly})` : ""}</dd>
      <dt>…agreeing with each other</dt><dd>${a.br == null ? "untestable"
        : (a.br>0?"+":"") + a.br.toFixed(2)}</dd>
      <dt>Hazardous-substance points</dt><dd>${nm(a.hz)}</dd>
      <dt>Rain-conditioned outfalls</dt><dd>${nm(a.rbu)}</dd>
      <dt>Basin volume</dt><dd>${a.vol ? nm(a.vol)+" m³" : "—"}</dd>
      <dt>Treatment plants</dt><dd>${nm(a.rens)}${a.pe ? ` · ${nm(a.pe)} PE` : ""}</dd>
      <dt>Aquaculture outfalls</dt><dd>${nm(a.hav)}</dd>
      <dt>Dumping grounds</dt><dd>${nm(a.klap)}</dd>
      <dt>Extraction areas</dt><dd>${nm(a.rst)}</dd>
    </dl>
    <h3>When the data exists</h3>
    <div class="tl">${tl}${ax}</div>
    <h3>What cannot be modelled here</h3>
    ${a.gaps.length ? "<ul class='gaps'>" + a.gaps.map(g => "<li>"+esc(g)+"</li>").join("")
      + "</ul>" : "<p class='none'>Nothing flagged.</p>"}
    <h3>Explore the measurements</h3>
    <div id="explore"><p class="none">loading…</p></div>`;
  explore(id);
}

/* ------------------------------------------------------------------ explorer
   A map that shows where data exists and will not let you look at it is opaque.
   This loads the monthly series for the selected area and lets two variables be
   put against each other.

   Deliberately NOT a dual-axis chart. Two quantities on one frame with two
   different scales is the most reliable way to manufacture a relationship that
   is not there - the reader compares the drawn lines, and the drawing was
   chosen. Instead: two panels, one scale each, sharing a time axis, plus a
   scatter where the relationship can actually be read. */
let CUBE = null, SERIES = null, loading = null;

async function loadData(){
  if (SERIES) return;
  if (!loading) loading = (async () => {
    const [cj, cb, sj] = await Promise.all([
      fetch("data/areas/cube.json").then(r => r.json()),
      fetch("data/areas/cube.bin").then(r => r.arrayBuffer()),
      fetch("data/areas/series.json").then(r => r.json()),
    ]);
    CUBE = {meta: cj, bits: new Uint8Array(cb),
            idx: Object.fromEntries(cj.areas.map((a,i) => [a.id, i]))};
    SERIES = sj;
  })();
  await loading;
}

// bits are area-major within each stream, months LSB-first, ceil(months/8) per area
function hasData(streamIdx, areaIdx, month){
  const per = Math.ceil(CUBE.meta.months / 8);
  const base = (streamIdx * CUBE.meta.areas.length + areaIdx) * per;
  return (CUBE.bits[base + (month >> 3)] >> (month & 7)) & 1;
}

function coverageGrid(ai){
  const M = CUBE.meta.months, Y0 = CUBE.meta.year0, ny = M / 12;
  let out = "";
  CUBE.meta.streams.forEach((st, si) => {
    const perYear = [], perMonth = new Array(12).fill(0);
    for (let y = 0; y < ny; y++){
      let c = 0;
      for (let m = 0; m < 12; m++){
        if (hasData(si, ai, y*12 + m)) { c++; perMonth[m]++; }
      }
      perYear.push(c);
    }
    const tot = perYear.reduce((a,b) => a+b, 0);
    if (!tot) return;
    const cells = perYear.map((c,y) =>
      `<i style="opacity:${c ? 0.18 + 0.82*c/12 : 0}" title="${Y0+y}: ${c} month${
        c===1?"":"s"}"></i>`).join("");
    const maxm = Math.max(...perMonth);
    const seas = perMonth.map((c,m) =>
      `<i style="opacity:${c ? 0.18 + 0.82*c/maxm : 0}" title="${
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][m]
      }: ${c} year${c===1?"":"s"}"></i>`).join("");
    out += `<div class="cov"><div class="covlab">${esc(st.label)}${
      st.note ? ` <b title="${esc(st.note)}">declared, not sampled</b>` : ""}</div>
      <div class="covrow"><span>years</span><div class="covcells">${cells}</div></div>
      <div class="covrow"><span>season</span><div class="covcells s12">${seas}</div></div></div>`;
  });
  return out || `<p class="none">No stream in the cube reaches this area.</p>`;
}

function seriesFor(ai){
  const M = CUBE.meta.months;
  return SERIES.variables.map(v => {
    const col = SERIES.series[v.key], n = SERIES.series[v.key + "__n"] || [];
    const vals = col.slice(ai*M, (ai+1)*M), cnt = n.slice(ai*M, (ai+1)*M);
    const have = vals.filter(x => x != null).length;
    return {...v, vals, cnt, have};
  }).filter(v => v.have >= 6);
}

function spark(v, w, h){
  const M = CUBE.meta.months, pts = [];
  let lo = Infinity, hi = -Infinity;
  for (const x of v.vals) if (x != null){ if (x<lo) lo=x; if (x>hi) hi=x; }
  if (!isFinite(lo)) return "";
  if (hi === lo) { hi = lo + 1; }
  for (let m = 0; m < M; m++){
    const x = v.vals[m];
    if (x == null) continue;
    pts.push(`${(m/(M-1)*w).toFixed(1)},${(h - (x-lo)/(hi-lo)*h).toFixed(1)}`);
  }
  const dots = pts.map(p => `<circle cx="${p.split(",")[0]}" cy="${p.split(",")[1]}" r="1.1"/>`).join("");
  return `<svg viewBox="0 0 ${w} ${h}" class="spark" role="img"
    aria-label="${esc(v.label)} ${esc(v.depth)}, ${v.have} months">
    <g class="pts">${dots}</g></svg>
    <div class="scale"><span>${hi.toFixed(2)}</span><span>${lo.toFixed(2)} ${esc(v.unit)}</span></div>`;
}

/* Plain language, because "r = +0.49" is a spell rather than a sentence. */
function plainR(r, n, a, b){
  const s = Math.abs(r), dir = r >= 0 ? "the other tends to be high too"
                                      : "the other tends to be low";
  const strength = s < 0.2 ? "barely at all" : s < 0.4 ? "weakly"
    : s < 0.6 ? "moderately" : s < 0.8 ? "strongly" : "very strongly";
  const shrink = 1 - Math.sqrt(Math.max(0, 1 - r*r));
  return `<p class="plain">Across the <b>${n}</b> months where both were measured
    here, when <b>${esc(a)}</b> is above its own average, <b>${esc(b)}</b> ${dir} —
    ${strength} (r = ${r>=0?"+":""}${r.toFixed(2)}).
    Knowing one shrinks the error in guessing the other by
    <b>${(100*shrink).toFixed(0)}%</b> against just guessing its average.
    ${n < 24 ? "<b>Twelve to twenty-four points is very little</b>; a correlation this size arises by chance easily at that sample size." : ""}
    It says nothing about which causes which, or whether a third thing drives both —
    both are seasonal, and season alone will correlate almost anything with
    anything.</p>`;
}

function compare(vs, ka, kb){
  const A = vs.find(v => v.key === ka), B = vs.find(v => v.key === kb);
  if (!A || !B || ka === kb) return "";
  const xs = [], ys = [];
  for (let m = 0; m < A.vals.length; m++){
    if (A.vals[m] != null && B.vals[m] != null){ xs.push(A.vals[m]); ys.push(B.vals[m]); }
  }
  if (xs.length < 6) return `<p class="none">Only ${xs.length} month${
    xs.length===1?"":"s"} have both. Too few to compare.</p>`;
  const mean = a => a.reduce((x,y)=>x+y,0)/a.length;
  const mx = mean(xs), my = mean(ys);
  let sxy=0, sxx=0, syy=0;
  for (let i=0;i<xs.length;i++){ const dx=xs[i]-mx, dy=ys[i]-my; sxy+=dx*dy; sxx+=dx*dx; syy+=dy*dy; }
  const r = sxy / Math.sqrt(sxx*syy || 1);
  const x0=Math.min(...xs), x1=Math.max(...xs), y0=Math.min(...ys), y1=Math.max(...ys);
  const pts = xs.map((x,i) => `<circle cx="${((x-x0)/((x1-x0)||1)*100).toFixed(1)}"
    cy="${(100-(ys[i]-y0)/((y1-y0)||1)*100).toFixed(1)}" r="1.6"/>`).join("");
  const lab = v => `${v.label} ${v.depth}`;
  return `<div class="scat"><svg viewBox="-6 -6 112 112" role="img"
      aria-label="scatter of ${esc(lab(A))} against ${esc(lab(B))}">
      <g class="pts">${pts}</g></svg>
      <div class="axl x">${esc(lab(A))} →</div><div class="axl y">${esc(lab(B))} →</div>
    </div>${plainR(r, xs.length, lab(A), lab(B))}`;
}

async function explore(id){
  const host = $("#explore");
  try { await loadData(); } catch(e){
    host.innerHTML = `<p class="none">Could not load the series data.</p>`; return;
  }
  const ai = CUBE.idx[id];
  if (ai == null){ host.innerHTML = `<p class="none">Not in the cube.</p>`; return; }
  const vs = seriesFor(ai);
  const ann = CUBE.meta.annual_only || {};
  let html = `<h4>When each stream actually measured</h4>${coverageGrid(ai)}`;
  for (const k in ann) html += `<p class="annual"><b>${esc(k)}: annual only.</b> ${esc(ann[k])}</p>`;
  if (!vs.length){
    host.innerHTML = html + `<p class="none">No monthly series with at least six
      months reaches this area, so there is nothing here to plot.</p>`;
    return;
  }
  const opts = vs.map(v => `<option value="${v.key}">${esc(v.label)} ${esc(v.depth)} · ${v.have} mo</option>`).join("");
  html += `<h4>Put two against each other</h4>
    <div class="pick"><select id="va">${opts}</select><select id="vb">${opts}</select></div>
    <div id="panes"></div>`;
  host.innerHTML = html;
  const va = $("#va"), vb = $("#vb");
  vb.selectedIndex = Math.min(1, vs.length-1);
  const draw = () => {
    const A = vs.find(v => v.key === va.value), B = vs.find(v => v.key === vb.value);
    $("#panes").innerHTML =
      `<div class="pane"><div class="plab">${esc(A.label)} ${esc(A.depth)}</div>${spark(A,300,44)}</div>
       <div class="pane"><div class="plab">${esc(B.label)} ${esc(B.depth)}</div>${spark(B,300,44)}</div>
       <div class="tnote">Both panels share the same ${CUBE.meta.year0}–${CUBE.meta.year1}
         span, each with its own scale. They are drawn apart on purpose: one frame
         with two scales lets the drawing decide how related they look.</div>
       ${compare(vs, va.value, vb.value)}`;
  };
  va.onchange = vb.onchange = draw;
  draw();
}
</script>
<footer class="sitefoot">
  <p><strong>Have data access this project doesn't?</strong> Most of what cannot be
  answered here is gated rather than hard — PULS overflow volumes, the credential-gated
  ODA topics, an instrument identity, a sampling time.
  <a href="IF_YOU_HAVE_THE_DATA.md">If you have data access we don't</a> lists eight
  blocked items with exactly what unblocks each, and how to clone and run this yourself.
  Three of them need no credentials at all.</p>
  <p>Source and full history:
  <a href="https://github.com/Jjokulian/copenhagen-waterways">copenhagen-waterways</a> ·
  method: <a href="https://github.com/Jjokulian/statistical-methods">statistical-methods</a>.
  Errors this project found in itself are left visible in the pages and the git history
  rather than edited out.</p>
</footer>

"""


if __name__ == "__main__":
    sys.exit(main())
