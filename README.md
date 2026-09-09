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

python3 scripts/nitrogen.py             # -> docs/NITROGEN.md
python3 scripts/waves.py                # -> data/derived/waves.json
python3 scripts/seabed.py               # -> docs/SEABED.md   (after waves.py)
python3 scripts/causation.py            # -> docs/CAUSATION.md
./scripts/setup_venv.sh                 # NetCDF/satellite stack, if needed
python3 scripts/hypotheses.py           # -> docs/HYPOTHESES.md
python3 scripts/experiments.py          # -> docs/EXPERIMENTS.md
python3 scripts/fetch_queue.py          # -> docs/DATA_QUEUE.md
python3 scripts/observing.py            # -> docs/OBSERVING.md
python3 scripts/oxygen.py               # -> docs/OXYGEN.md
python3 scripts/areas.py                # -> docs/AREAS.md
python3 scripts/areamap.py              # -> docs/areas.html
python3 scripts/currents.py fetch       # marine + Baltic wind  (~10 min)
python3 scripts/currents.py validate && python3 scripts/currents.py index
python3 scripts/currents.py transport && python3 scripts/currents.py report
python3 scripts/solutions.py            # -> docs/SOLUTIONS.md
python3 scripts/rivermap.py             # -> docs/river_map.png
python3 scripts/programme_map.py        # -> docs/*.svg
python3 scripts/rivers3d.py             # -> viewer bundle + 2 SVGs
python3 scripts/streams.py              # -> data/derived/streams.json
python3 scripts/architecture.py         # -> docs/data/architecture.json
python3 scripts/section3d.py            # -> docs/data/section3d.json
python3 scripts/programme.py            # -> docs/PROGRAMME.md

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
  floodreg.py             locates the sheets on the map by matching water
  floodgap.py             compares modelled flooding against what was planned
  nitrogen.py             audits how the marine nitrogen figures are produced
  waves.py                31 yr of hourly wind -> wave-driven bed shear stress
  seabed.py               renders the wave results and the accumulation term
  causation.py            follows the nitrogen figure forward through its causal chain
  currents.py             retention, transport and the overflow-hour test
  solutions.py            what the city plans against what it has done
  rivermap.py             the flood model read as the city's natural drainage
  streams.py              the rain stream and the foul stream, as rates
  architecture.py         where the separated architecture acts, per catchment
  section3d.py            dimensions for the retrofit model, with their kinds
  programme_map.py        the two figures for the argument page
  programme.py            the argument - kept separate from the investigation
  landbrug.py             the same audit, in Danish, addressed to farmers
  export_flood.py         publishes the recovered model as a usable dataset
  rivers3d.py             the 3D scene, the retrofit section, the routing logic
  observations.py         validates and merges field observations
data/
  raw/                    downloaded, untouched
  derived/                constructions.geojson, registry.json, viewer/
  manual/                 hand-curated and sourced: codelists, constructions,
                          monitoring methodology, nitrogen pathways
docs/
  DATA_SOURCES.md         what is public, what is paywalled, what does not exist
  REGISTER.md             the register, generated
  FLOOD_GAP.md            modelled flooding vs the cloudburst plan, generated
  flood_gap_map.png       one picture of that comparison
  NITROGEN.md             where the marine nitrogen figures come from, generated
  CAUSATION.md            what survives between that figure and a claim about a shore
  HYPOTHESES.md           160 candidate causes, written down before any of them is scored
  EXPERIMENTS.md          18 proposals with controls and decision rules fixed in advance
  DATA_QUEUE.md           80 sources sorted by friction: fetch now, held, one form away, closed
  OBSERVING.md            what is measured, where, how often - and whether a "water body" is real
  OXYGEN.md               every route that removes oxygen, priced; and what the indicators conflate
  AREAS.md                one record per marine water body, and what cannot be modelled in each
  SEABED.md               wind, waves, and whether the bed stays put, generated
  CURRENTS.md             where the water goes, generated
  SOLUTIONS.md            the response, measured from the city's own layers
  OPEN_PROBLEMS.md        what this could not settle, hand-maintained
  PROGRAMME.md            THE ARGUMENT - what ought to be done, labelled as such
  LANDBRUG.md             the audit in Danish, for the audience it is used against
  section3d.html          the retrofit in 3D, dimensioned, with the hydraulic check
  architecture.html       the separated architecture: the graph, and the map of
                          which catchments it acts on
  data/flood2012/         the recovered flood model, georeferenced, for QGIS
  river_map.png           where the water wants to go vs what the plan allows
  index.html              renders the Markdown for GitHub Pages
viz/
  index.html              the map
  rivers3d.html           the proposal in 3D - rivers, retrofit, destinations
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
| ... that no page of the plan describes | **262** |

Three things worth knowing that were not obvious going in:

**The city's two records do not reference each other.** The statutory plan describes
projects by plan number (`A1.14`, `K1.57`); the map layers identify them by cloudburst
number (`klima_id`: `BIR7.5`, `KV86`). No published crosswalk connects them. The plan
pages happen to cite the klima_id in their titles, so `build_registry.py` recovers the
link by scanning for ids that actually exist in the geometry — 86 of 349 matched. The
other **262 mapped structures are not described anywhere in the plan.** That is checked
against the whole document, not just the project register: the other 117 pages —
appendices, status chapters, targets, the "aktuelle projekter" listings — are crawled and
scanned too, and they account for exactly one further id. The gap is preserved in
`registry.json` under `klima_id_without_documentation` rather than dropped.

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

**Georeferencing: four of seven, automatically.** `floodmaps.py autoref` locates a sheet
by cross-correlating the water visible in its orthophoto against the city's water
polygons, with FFT evaluating every offset at once. Three things had to be handled: the
flood bands are painted blue and swamp the water signal (18.8% of Bispebjerg) so they are
masked out; searching the whole city locks onto the wrong water (Bispebjerg landed at
latitude 55.61, south of the city) so the search is confined to the sheet's own catchment;
and the sheets do not share one orthophoto, so no single water detector survives all seven.

That last point is why it is an ensemble. Six detectors run independently and a position
is accepted only where they agree — agreement between methods that fail differently is
evidence, one confident answer is not. **indre-by, ladegaardsaaen, norrebro and osterbro**
were accepted and each confirmed by eye against the photographed quays and lake edges.
**amager, bispebjerg and kbhvest** were not; they need two hand-placed control points each
in `viz/georef.html`. kbhvest passed a looser threshold and its water outlines visibly do
not track the photograph, so the bar was raised rather than shipping a wrong registration.

An independent check backs this up: open water is 13.7% of the study area, so a wrong
registration would drop flooding into the harbour at about that rate. It lands there at
1.7–10.7% depending on depth band — below the baseline at every depth, and *least* often
for the deepest band, which also rules out its dark navy being confused with dark water.

Two approaches were tried and rejected: matching the drawn catchment outline (it turns out
the 2012 "Oplandsgrænser" is **not** today's `skp_skybrudsoplande` boundary — 13.6%
coverage against an 11% chance level even from a registration known to be correct), and
correlating against the OSM street network (too uniform; Indre By landed 9 km off).

Extracted flood area per sheet, before georeferencing: Bispebjerg 2.22 km², kbhvest
1.39 km², Amager 1.18 km², Ladegårdsåen 0.42, Nørrebro 0.36, Østerbro 0.10, Indre By 0.04.

## Does the plan go where the water goes?

`scripts/floodgap.py` puts the recovered model next to the cloudburst works and asks the
question the PDF format made awkward. Output: `docs/FLOOD_GAP.md` and
`docs/flood_gap_map.png`. Covering the four registered inner-city catchments and
1.521 km² of modelled flooding **on land** at 0.1 m or deeper (the sheets
also paint 0.148 km² over lakes and the harbour, excluded — water
standing on water is not something a basin fixes):

| Distance | Near *any* planned work | Near something **built or started** |
|---|---:|---:|
| within 50 m | 69.0% | 12.6% |
| within 100 m | 82.6% | 20.0% |
| within 200 m | 90.5% | 32.9% |

**The plan is aimed correctly and is largely unbuilt.** Nine tenths of the modelled
flooding has something planned within 200 m; a third has anything that has broken ground.
The distance is generous — being 50 m from a cloudburst road is not protection — which
makes the second column the more striking of the two.

Only 4 places have deep water (≥0.2 m) with nothing planned within 100 m, totalling 0.06 km² and roughly 42,260 m³. That small number is itself the finding: coverage is good,
delivery is not.

One number that looks like a finding and is not: 94% of this flooding sits over combined
sewer, where rain and sewage share a pipe — so the standing water is mixed with sewage.
But 87% of the mapped area *is* combined sewer, a ratio of 1.07. The consequence
is real; the correlation is not. The report states both.

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

- Set control points for amager, bispebjerg and kbhvest in `viz/georef.html` — two each —
  then re-run `floodgap.py` to extend the comparison beyond the inner city.
- Walk somewhere in heavy rain with `log.html` open, then compare the observations
  against the recovered 2012 model. Disagreements are the interesting output.
- Wire up DHM and compute real flow accumulation — a 2026 answer to replace the 2012 one.
  Needs a machine with a few GB of RAM.
- Attach measured overflow volumes and event counts per structure per year. These exist
  in PULS but not in the public VP3 extract; a municipal or utility account would reach them.
- Resolve the 45 unclassified m³ figures by hand and fold them into the register.
- Extend `data/manual/constructions.json` to the other cloudburst tunnels
  (Svanemøllen, Valby) with the same one-source-per-claim discipline.
- Chase the 262 undocumented `klima_id`s outside planer.kk.dk — committee papers, HOFOR
  project pages, the 2024/2025 addenda if they are ever published as pages. Everything on
  planer.kk.dk is already scanned.

## Sources and licensing

Detailed in `docs/DATA_SOURCES.md`. In short: Københavns Kommune's layers are published
as open data via opendata.dk; Miljøstyrelsen's are public-sector open data; the
Spildevandsplan pages are public statutory planning documents. Attribute all three if you
republish. Nothing here is behind authentication, and nothing here required any.
