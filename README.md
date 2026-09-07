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
  floodmaps.py            recovers the 2012 flood model out of its PDFs
  observations.py         validates and merges field observations
data/
  raw/                    downloaded, untouched
  derived/                constructions.geojson, registry.json, viewer/
  manual/                 codelists.json, constructions.json  (hand-curated, sourced)
docs/
  DATA_SOURCES.md         what is public, what is paywalled, what does not exist
  REGISTER.md             the register, generated
viz/
  index.html              the map
  georef.html             two-pane control-point tool for the flood sheets
  log.html                field logger, for a phone, offline
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

**Rainwater flow paths were modelled — the results just were not data.** Copenhagen ran
a 2D surface flood model and published `Oversvømmelsesscenarier for vandoplande`: depth
maps of a 100-year event for all seven catchments, banded 0.05–0.1 up to >2 m, from 2012
calculations. They are seven raster PDFs with the georeferencing stripped (checked — no
`/Measure`, `/GPTS` or `/Viewport` anywhere in the files). `scripts/floodmaps.py` turns
them back into depth rasters; see *Recovering the flood model* below for what is solid
and what is not.

**Nobody records where water is actually observed.** Miljøstyrelsen's technical standard
calibrates overflow models against measurements taken inside overflow structures — five
clearly separable events at the structure. Nothing in that chain observes a street. So
no dataset says whether the modelled 0.2 m at a given corner is really 0.4 m because a
gully has been blocked for years. `viz/log.html` and `scripts/observations.py` exist to
collect that layer on foot.

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

## Recovering the flood model

```bash
python3 scripts/floodmaps.py fetch render extract   # (run the three in turn)
python3 scripts/floodmaps.py status
```

**Solid.** The scale of every sheet is read from the PDF's own text layer, not guessed —
the sheets are at seven different scales (1:7,528 to 1:28,737) with 500 m or 1000 m scale
bars, and guessing put Amager out by a factor of two. The six depth-band colours were
sampled from the legend swatches and are the standard Blues ramp; `extract` re-reads each
sheet's legend labels and warns if one differs. The legend block is located from the text
layer and blanked, because it contains a filled rectangle per band — on Indre By the
"1–2 m" band was *entirely* legend swatch before that fix. Classification uses colour
plus a blue-cast test for the near-white palest band, which removes 95% of false hits
(363,940 raw matches down to 18,393 real ones on Indre By).

**Not solid: georeferencing.** Three automatic approaches were tried — matching the drawn
catchment outline, fitting on strict-black pixels, and water IoU against the city's own
vector water. The best landed 36% of the known catchment boundary on the drawn one
against an 11% chance level. None was good enough to trust, so none is used.

Instead `viz/georef.html` puts the sheet beside a reference map drawn from the city's own
vector layers and takes two control points per sheet — about two minutes each. It reports
the implied scale against the printed scale bar and the RMS residual, so a bad
registration is visible rather than silent. Paste the result into
`data/manual/floodmap_control.json` and run `floodmaps.py georef`.

Extracted flood area per sheet, before georeferencing: Bispebjerg 2.22 km², kbhvest
1.39 km², Amager 1.18 km², Ladegårdsåen 0.42, Nørrebro 0.36, Østerbro 0.10, Indre By 0.04.

## Logging what you actually see

Open `viz/log.html` on a phone and walk. It captures GPS with its accuracy, and records
depth in **the same six classes as the 2012 model**, so an observation compares to the
model directly instead of by eye. It also records whether the nearest drain is clear,
blocked, or *surcharging* — water rising out of the gully, which means the pipe below is
full. Everything is held in `localStorage`, so it works with no signal; export when home.

```bash
python3 scripts/observations.py import ~/Downloads/observations.import.json
python3 scripts/observations.py stats
python3 scripts/build_viewer_data.py     # they appear on the map
```

Import validates each record — class values, timestamp, and that the point is inside
Copenhagen — and de-duplicates, so re-importing the same export is harmless. Observations
live in `data/manual/` and are never touched by a fetch script.

## Where to take it next

- Set control points for the seven flood sheets and georeference them. Two points each.
- Walk somewhere in heavy rain with `log.html` open, then compare the observations
  against the recovered 2012 model. Disagreements are the interesting output.
- Wire up DHM and compute real flow accumulation — a 2026 answer to replace the 2012 one.
  Needs a machine with a few GB of RAM.
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
