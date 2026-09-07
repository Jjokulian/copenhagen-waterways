# Copenhagen Waterways

Mapping what runs under Copenhagen: the sewer system (*spildevand*), the cloudburst
infrastructure built to keep rain out of it, and the points where the two end up in the
harbour. Assembled entirely from open data, with the provenance of every figure kept.

The project has two halves:

1. **A register.** Every claimed construction — basins, cloudburst tunnels, retention
   squares, overflow structures — with its location, its stated volume, and a link to
   the document that claims it. Where a claim cannot be attributed to a specific
   structure, it is recorded as unattributed rather than quietly assigned.
2. **A viewer.** A 3D map of the sewer catchments, the planned structures and the
   discharge points, built to make the *shape* of the system legible.

## Quickstart

No dependencies. Standard-library Python 3 and a browser.

```bash
cd copenhagen-waterways

python3 scripts/fetch_wfs.py            # ~28 GIS layers  ->  data/raw/      (~131 MB)
python3 scripts/fetch_plan_projects.py  # 357 plan pages  ->  data/raw/      (~8 min, polite crawl)
python3 scripts/build_registry.py       # join prose to geometry
python3 scripts/report.py               # -> docs/REGISTER.md
python3 scripts/build_viewer_data.py    # -> data/derived/viewer/ (13 MB)

python3 -m http.server 8000             # then open http://localhost:8000/viz/
```

Every fetch step caches, so re-running is cheap; `--force` (WFS) and `--refresh`
(crawler) bypass the cache. `data/raw/` and `data/derived/` are reproducible and
git-ignored; only `data/manual/` is hand-authored.

## What is in here

```
scripts/
  common.py               HTTP, JSON, and WGS84 axis-order handling
  layers.json             the layer catalogue - the useful half of this project
  fetch_wfs.py            downloads and clips the GIS layers
  fetch_plan_projects.py  crawls the Spildevandsplan 2018 project register
  build_registry.py       reconstructs the prose <-> geometry join
  build_viewer_data.py    compacts 131 MB into a 13 MB browser bundle
  report.py               renders docs/REGISTER.md
data/
  raw/                    downloaded, untouched
  derived/                constructions.geojson, registry.json, viewer/
  manual/                 codelists.json, constructions.json  (hand-curated, sourced)
docs/
  DATA_SOURCES.md         what is public, what is paywalled, what does not exist
  REGISTER.md             the register, generated
viz/index.html            the map
```

## What came out of it

Numbers as of the last run; regenerate with `scripts/report.py`.

| | |
|---|---:|
| Sewer catchments | 766 |
| Cloudburst basins and retention squares | 176 |
| Cloudburst roads, pipes and tunnel alignments | 976 |
| Rain-dependent discharge points, metro area | 680 (392 in København) |
| Spildevandsplan project pages parsed | 357 |
| Distinct mapped structures (`klima_id`) | 349 |
| ... that no plan page describes | **263** |

Three things worth knowing that were not obvious going in:

**The city's two records do not reference each other.** The statutory plan describes
projects by plan number (`A1.14`, `K1.57`); the map layers identify them by cloudburst
number (`klima_id`: `BIR7.5`, `KV86`). No published crosswalk connects them. The plan
pages happen to cite the klima_id in their titles, so `build_registry.py` recovers the
link by scanning for ids that actually exist in the geometry — 86 of 349 matched. The
other **263 mapped structures have no project page at all.** That gap is a finding, and
it is preserved in `registry.json` under `klima_id_without_documentation` rather than
dropped.

**"m³" in this corpus means two different things.** A page saying 550,000 m³ may be
describing an annual pumped volume, not a tank. Summing them naively inflated the total
storage to 812,105 m³; classifying each figure by its surrounding sentence brings the
attributable storage to 139,580 m³, with 937,600 m³/year correctly separated as flow.
Figures the classifier cannot resolve are counted and left for a human.

**Most "basins" are shallow, not deep.** Dividing claimed volume by footprint gives
implied mean depths of 0.05–0.6 m for most of them. These are parks and squares designed
to flood a few centimetres deep, not cisterns. The viewer shows this directly, which is
why it needs vertical exaggeration to be legible at all.

Separately, the national register lists **314,176 m³** of detention-basin volume attached
to metro-area overflow structures — a different and better-attributed inventory than the
plan prose, since each volume belongs to a single named structure.

## Limits worth stating plainly

**There is no open source of surveyed sewer depths.** The as-built pipe geometry lives in
LER (Ledningsejerregistret), which requires eID identification as an excavation actor and
is granted for the purpose of an intended dig. This project does not attempt to obtain it,
and the data would not be republishable if it did. Every depth here comes from what a
planning document *states*, and is labelled as a claim. A genuinely surveyed 3D model of
Copenhagen's sewers cannot be built from open data.

**Rainwater flow paths were modelled — the results just are not data.** Copenhagen ran a
2D surface flood model and published `Oversvømmelsesscenarier for vandoplande`: depth maps
of a 100-year event for all seven catchments, banded 0.05–0.1 up to >2 m. They are seven
**raster PDFs**. No georeferencing, no vector extents, no queryable depths, and the
calculations date from 2012 for a 2010 scenario. The knowledge exists and is public; the
data was never released. Recovering it means warping the images to a coordinate system and
classifying the depth bands back into polygons — feasible here (numpy, PIL and pdftoppm are
present), not yet done.

Building it fresh instead means the 0.4 m terrain model (DHM, on Dataforsyningen — reachable,
needs a free token), sink-filling, and flow accumulation: a raster job wanting several GB of
RAM, which this machine does not have. Either way, the cloudburst catchments and planned
alignments currently in the viewer are the city's *intended* flow paths, not where water
goes. `docs/DATA_SOURCES.md` §7–8 has the details.

**The plan is from 2018, with later addenda.** Project status and completion years drift;
`skp_igangsatte_prj_kk` and `skp_afsluttede_prj_kk` are the layers to trust for build state.

**The viewer has not been rendered on this machine.** Its JavaScript is syntax-checked,
its data loads over HTTP, and its geometry math is unit-tested against the real basin
data — but headless Firefox needs more RAM than this VM has, so it has not been seen in a
browser here. Check it before trusting the visuals.

**Two structure-type codes are inferred.** `SE` and `SF` cover 487 of the 680 discharge
points but do not appear in Miljøstyrelsen's published code table. They are flagged
`inferred: true` in `data/manual/codelists.json` and marked in the report. Do not cite
them as fact.

## Where to take it next

- Wire up DHM and compute real flow accumulation — the single biggest upgrade, and the
  one thing that would answer "where does rain actually go" rather than "where is it
  meant to go". Needs a machine with a few GB of RAM.
- Attach measured overflow volumes and event counts per structure per year. These exist
  in PULS but not in the public VP3 extract; a municipal or utility account would reach them.
- Resolve the 45 unclassified m³ figures by hand and fold them into the register.
- Extend `data/manual/constructions.json` to the other cloudburst tunnels
  (Svanemøllen, Valby) with the same one-source-per-claim discipline.
- Cross-check the 263 undocumented `klima_id`s against the 2024/2025 plan addenda; some
  may be described in supplements the 2018 sitemap does not cover.

## Sources and licensing

Detailed in `docs/DATA_SOURCES.md`. In short: Københavns Kommune's layers are published
as open data via opendata.dk; Miljøstyrelsen's are public-sector open data; the
Spildevandsplan pages are public statutory planning documents. Attribute all three if you
republish. Nothing here is behind authentication, and nothing here required any.
