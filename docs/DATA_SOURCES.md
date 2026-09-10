# Data sources for Copenhagen's water system

What is public, what is paywalled, what does not exist in open form, and what each
thing is actually good for. Everything marked **fetched** is pulled by the scripts in
`scripts/` and lands in `data/raw/`.

## 1. Københavns Kommune — Kbhkort WFS  *(fetched)*

`https://wfs-kbhkort.kk.dk/k101/ows` — GeoServer, ~481 layers, no authentication.
Discovered via the CKAN catalogue at `https://admin.opendata.dk/api/3/action/package_search?q=organization:city-of-copenhagen`
(note: `www.opendata.dk/api` 404s; the working API host is `admin.opendata.dk`).

Layer names are not documented anywhere central — get them from
`?service=WFS&version=1.1.0&request=GetCapabilities`. The 21 we use are in
`scripts/layers.json`; the rest are mostly unrelated municipal themes.

| Layer | What it is | Why it matters |
|---|---|---|
| `sp_kloakoplande` | 766 sewer catchments | The backbone. Tells you whether a block is **fælleskloakeret** (combined — sewage and rain in one pipe, so heavy rain means sewage overflow) or **separatkloakeret**, plus the receiving treatment plant and impervious fraction. |
| `skp_bassiner_pladser_kk` | 176 cloudburst basins and retention squares | Planned storage. Carries `klima_id`. |
| `skp_veje_tunneller_kk` | 976 cloudburst roads, pipes, tunnels | Alignments including the skybrudsledninger. Carries `klima_id`. |
| `skp_skybrudsoplande` / `skp_deloplande` | 7 catchments / 21 sub-catchments | The organising unit of the whole cloudburst plan. |
| `skp_terraenaend` | 147 planned terrain modifications | Where the street surface itself is reshaped to steer water. |
| `skp_igangsatte_prj_kk` / `skp_afsluttede_prj_kk` | 90 in progress / 50 completed | Build status. Both carry the key (`klima_id`, and `klimaid` on the completed layer — note the spelling difference). |
| `lar_registreringer` | 1444 local infiltration installations | The decentralised half of the rainwater story. |
| `dp_regnvandsafledning_p/l/f` | 2235 points, 697 lines, 148 polygons | Surface conveyance in public space: gullies, swales, channels. |
| `grundvand_pejlinger_2021`, `grundvand_potentialelinjer_2021`, `terraen_minus_gvs` | Groundwater observations, contours, depth-to-water | The practical ceiling on how deep anything can be dug. |
| `vand_oversigtskort`, `havn`, `kbh_kysttyper` | Lakes, watercourses, harbour, coast | Where the invisible system finally discharges. |
| `hmax263_dige`, `hmax285_dige` | Storm surge dike lines at 2.63 m and 2.85 m | 101 MB of the 131 MB raw total. Coastal flooding, not rainfall — peripheral to this project. |

**Gotcha:** this server speaks WFS 1.0.0 and returns `EPSG:4326` as `[lon, lat]`, but
1.1.0 flips the axis order. `scripts/common.py` detects and normalises this rather
than trusting either.

## 2. Miljøstyrelsen MiljøGIS — Vandområdeplan 3 basisanalyse  *(fetched)*

`https://wfs2-miljoegis.mim.dk/vp3basis2019/ows` — national, 47 layers, no auth.

This is the **discharge end** of the system, and the single most valuable open source
for "where does sewage actually come out". Derived from PULS (see §3), so it is the
open shadow of a database that is not itself open.

| Layer | Metro Copenhagen | Notes |
|---|---|---|
| `vp3_basis_2019_punkt_rbu_udl` | **680 points** (392 in København) | Rain-dependent discharges: combined sewer overflow structures and stormwater outfalls. `bgv_type` gives the structure type, `vol_sb` the attached basin volume in m³. 47 points carry a volume, totalling **314,176 m³**. |
| `vp3_basis_2019_punkt_rens_udl` | 5 | Treatment plants — Lynetten, Damhusåen, Avedøre and neighbours. `godk_pe` = approved capacity in person-equivalents. |
| `vp3_basis_2019_punkt_ind_udl` | 31 | Industrial discharges. |
| `vp3_basis_2019_punkt_spredt_udl` | 4622 | Scattered dwellings — mostly peri-urban. |
| `vp3basis2019_badevand` | 36 | Bathing water stations: the public-health consequence, useful for sanity-checking overflow claims. |

Layers here are national, so `fetch_wfs.py` clips them — by `komm_navn` where that
column exists, otherwise by bounding box. Three layers have no municipality column and
would silently come back empty without the bbox fallback.

**`bgv_type` decoding** is in `data/manual/codelists.json`, taken from Miljøstyrelsen's
[Datateknisk anvisning DP02 v4 (2024)](https://mst.dk/media/bnkdidho/dta-dp02-rbu-version-4-2024.pdf),
table 2. `OV`/`OS`/`OF`/`OK`/`Bypass`/`Skybrud` are authoritative from that table.
`SE` and `SF` (487 of our 680 points) are **not** in it — they belong to the separate-sewer
outfall list and our reading is flagged `inferred: true`. Do not report those two as fact.

The same document's table 1 gives the national median concentrations for overflow water
(BI₅ 30, COD 180, Tot-N 12, Tot-P 2.0 mg/l), which is how you turn a volume into a load.

## 3. Spildevandsplan 2018 project register — planer.kk.dk  *(fetched)*

`https://planer.kk.dk/spildevandsplan-2018/projekter/` — 357 project pages, enumerable
from `https://planer.kk.dk/sitemap.xml`. Categories: byudvikling (140), skybrudssikring
(102), afløbssystem (61), klimatilpasning-af-kloakken (51), renseanlæg (3).

This is the prose record of every claimed construction: purpose, dimensions, stated
volumes, ownership, and the affected land parcels by matrikel number. `fetch_plan_projects.py`
parses it into structured JSON and pulls out stated quantities with the sentence each
came from, so a human can judge the figure.

**The join problem.** Copenhagen keys these two worlds differently and publishes no
mapping:

* plan pages use a plan number — `A1.14`, `K1.57`
* the map layers use a cloudburst number — `klima_id`: `BIR7.5`, `KV86`, `VEL45`

The pages *cite* the klima_id in their titles and body text ("A3.3 Regnvandsledning i
Bispebjerg Bakke, BIR 7.5"). `build_registry.py` recovers the link by scanning for ids
that actually exist in the geometry, which stops stray tokens inventing matches. The
recovered mapping is a **reconstruction, not an official crosswalk** — treat it as such.

The project map on each page renders through `cowi.mapcentia.com/api/v2/` (a MapCentia
GC2 instance). Its SQL endpoint answers trivial queries but returns nothing for schema
introspection, so per-project geometry is not reachable that way.

## 4. PULS — Punktkilder og spildevand  *(not directly accessible)*

The national point-source database behind §2, run by Danmarks Miljøportal. Municipalities
report roughly 4,500 overflow structures and ~20,000 rain-dependent discharge points
annually, including measured or modelled overflow volumes and event counts per year.

Read access to the PULS UI needs a Miljøportal account provisioned through an
organisation's IT coordinator; there is no anonymous API. The VP3 layers in §2 are a
periodic public extract, which is why they carry structure types and basin volumes but
not the year-by-year overflow quantities.

The support host `support.miljoeportal.dk` returns 403 to automated fetches, and the
`b0902-prod-dist-app.azurewebsites.net` geoserver quoted in older guides no longer
resolves. The Miljøstyrelsen dTA PDFs are the reliable documentation.

## 5. LER — Ledningsejerregistret  *(deliberately not used)*

The actual as-built pipe geometry, with depths, lives here. It is **not open data and
we do not attempt to obtain it.** Access requires eID identification as a *graveaktør*
(excavation actor) and is granted for the purpose of an intended excavation; utility
owners then have five days to return data. Querying it without genuine intent to dig
would be a misuse of the register, and the returned data is licensed for that dig, not
for republication.

This is the honest limit on the 3D ambition: **no open source gives surveyed invert
levels for Copenhagen's sewers.** Depths in this project come from what the plan
documents state in prose, and are labelled as claims.

## 6. HOFOR  *(narrative only)*

The utility that owns and operates the system. Publishes project descriptions and
figures — tunnel lengths, diameters, pump capacities, storage volumes — but no GIS
downloads. `hofor.dk` is a citation source for the manual register, not a data source.
It directs pipe-location requests to LER.

## 7. Elevation — Dataforsyningen  *(available, not yet wired)*

`https://api.dataforsyningen.dk` is up and serves DHM (Danmarks Højdemodel), including
the 0.4 m terrain model, via WMS/WCS. A free API token is required.

This is the missing input for **actually modelling where rain flows**: fill the DEM
sinks, compute flow direction and accumulation, and you get surface flow paths and
ponding depressions directly, rather than inferring them from the plan. It needs a
raster stack this VM cannot hold — see the note in the README.

## 8. Modelled flood extents — published as pictures  *(not yet recovered)*

`Oversvømmelsesscenarier for vandoplande` on opendata.dk: the output of Copenhagen's 2D
surface flood model, showing inundation depth for a 100-year event across all seven water
catchments, banded 0.05–0.1 / 0.1–0.2 / 0.2–0.5 / 0.5–1 / 1–2 / >2 m.

It is published as **seven raster PDFs** — amager, bispebjerg, indre-by, kbhvest,
ladegaardsaaen, norrebro, osterbro — roughly 8 MB each, aerial photo with the depth bands
painted over it. The dataset description states the calculations are from 2012, for a 2010
scenario.

This is the most important thing in this catalogue and the least usable. The modelling
question — *where does rain actually pond in Copenhagen* — was answered at municipal scale
and then flattened into an image. There is no georeferencing, so it cannot be overlaid; no
vector extents, so nothing can be intersected with it; no depth values, so nothing can be
queried. A person wanting the answer must re-derive it from terrain, or walk around in the
rain.

**Recovered** by `scripts/floodmaps.py`. Findings from doing it:

* The georeferencing is genuinely absent, not merely unadvertised — the files contain no
  `/Measure`, `/GPTS`, `/LPTS`, `/Viewport` or projection string, compressed or otherwise.
* The seven sheets are at **seven different scales**, 1:7,528 (Nørrebro) to 1:28,737
  (KBH Vest), with 500 m or 1000 m scale bars. Each sheet carries a real text layer, so
  the bar length is read rather than guessed; guessing it put Amager out by 2x.
* The depth ramp is the standard Blues palette: `#f7fbff #d1e2f2 #9ac7e0 #519ccc #1c6bb0
  #08306b` for the six bands. Identical on every sheet (verified from each sheet's own
  legend labels).
* The legend must be masked before export, or its swatches become fictional deep water:
  on Indre By the entire "1-2 m" band was legend, nothing else. Its position moves
  between sheets (top-right on KBH Vest, bottom-right elsewhere), so it is located from
  the text layer.
* The palest band is nearly white and matches every pale roof on colour alone. Its blue
  cast (B-R = +8) separates it: 363,940 raw matches on Indre By, 18,393 real.

Extracted flooded area: Bispebjerg 2.22 km2, KBH Vest 1.39, Amager 1.18, Ladegårdsåen
0.42, Nørrebro 0.36, Østerbro 0.10, Indre By 0.04.

Georeferencing is automatic for four of the seven sheets (`floodmaps.py autoref`), by
cross-correlating orthophoto water against the city's water polygons with an ensemble of
six detectors; a position is accepted only where independent detectors agree. Two further
findings from that work:

* The **"Oplandsgraenser" drawn on these 2012 sheets is not today's catchment boundary**.
  Registering on water and then testing against the drawn outline gives 13.6% coverage
  against an 11% chance level. The catchments were redrawn between 2012 and the current
  `skp_skybrudsoplande`. Do not use the drawn outline to georeference or validate.
* The **sheets do not share one orthophoto**. Exposures differ enough that a water
  detector tuned on Indre By finds 0.1% of Bispebjerg, whose lakes render near-black with
  no blue cast at all.

The three unresolved sheets (amager, bispebjerg, kbhvest) take hand-placed control points
in `viz/georef.html`, which reports residuals so a bad registration is visible.

CKAN id: `oversvommelsesscenarier-for-vandoplande`.

## 9. Observed surface water  *(does not exist; we collect it)*

There is no open dataset of where water is actually seen standing or running in
Copenhagen streets. The gap is structural rather than accidental: Miljøstyrelsen's
technical standard (dTA DP02, section 3.1.1) defines model calibration as measurement
*at the overflow structure* — five clearly separable overflow events. Calibration happens
inside the pipes. Nothing in the reporting chain observes a street surface.

So a modelled 0.2 m at a corner is never checked against the 0.4 m that is actually there
because a gully has been blocked since 2019. `viz/log.html` (a phone-friendly, offline
field logger) and `scripts/observations.py` collect that layer. Records use the same six
depth classes as the 2012 model so the two compare directly, and flag drains that are
*surcharging* — water rising out of the gully, meaning the pipe below is full.

Stored in `data/manual/observations.geojson`, hand-collected, never overwritten by a
fetch script.

## 10. ODA — what the archive does not warn you about  *(fetched; read this before using it)*

Four extracts are on disk: `kemi` (water chemistry, 1,805,827 rows), `ctd`
(53,710,760), `lys` (light attenuation, 2,370,091) and `maaledybde` (151,203), all
spanning 1970–2026 and none truncated. `scripts/enums.py` counts every distinct value
of every column of each, because reading the top few values of a column is how a rare
sentinel survives. What it found is below. None of it is documented in the download.

**Units are per row, not per parameter. 14 of 147 parameters carry more than one.**
Not all of them are strays. `Orthophosphat` is 565 rows in µg/l against 353 in mg/l —
38% of them a thousandfold from the rest. Integrated primary production splits 5,068
mg/(m²·d) against 62,831 mg/(m³·d), *per area against per volume*, which cannot be
reconciled at all without a depth. PFAS sums run ng/l against µg/l. `Klorofyl a` is
185,313 rows in µg/l and exactly one in mg/l — and no range filter can catch that,
because a plausible mg/l value is also a plausible µg/l value. **Check `Enhed` on
every row.** Oxygen (mg/l), saturation (pct) and total nitrogen (µg/l) are
single-valued throughout, which is luck rather than a guarantee.

**Sentinels, undeclared.** `YIntercept` is `9999999` where the source lacked it,
admitted only in a free-text note on the row itself. `GennemsnitsDybde_m` is exactly
`99` on 4,332 rows — a real depth in the Skagerrak and a suspicious round number
everywhere else, with nothing distinguishing the two. `BundDybde_m` reaches 2300 m at
Læsø rende, a Kattegat trench about 50 m deep, and 292.3 m at a station named
`Hirtshals 15 m`, where the station's own name refutes the value. `Lysprocent` exceeds
110% of surface light on 21,348 rows and peaks at 58,438. Oxygen saturation reaches
90,972%.

**Censoring hidden behind column names that do not say so.** `ResultatAttribut` is
`<` on 85,035 rows, where `Resultat` holds *the detection limit, not the measurement* —
read as a value it biases the parameter high. (`ikke påvist`, 80 rows, is different and
is a real measured zero: all 80 are PFAS sums that were analysed and found empty.)
`SigtTilBund` is true on 26,380 Secchi readings, meaning the disc reached the bottom
and the water was clearer than the number says. `SigtDybdeMedVandkikkert` marks 6,104
readings taken through a water telescope, a different instrument.

**Columns that carry nothing.** `TekniskAnvisningAnvendt` and `Afsluttet` are
single-valued across every row of every extract, so neither can be used to filter for
protocol compliance — which is the only reason anyone reaches for them.

**Sample type decides what a depth means.** Per [Teknisk anvisning for marin
overvågning, Kap. 5](https://ecos.au.dk/fileadmin/ecos/Fagdatacentre/Marin/TA_NOVA_1998/Kap05.doc)
a `Blandingsprøve` is several bottles at *the same depth*, pooled — not over time and
not over depth — so it behaves as a point sample. A `Dybdeintegreret prøve` integrates
0–10 m, 0–25 m or the whole photic zone; 2,265 of them carry a nominal depth of 3 m or
less and will enter a surface filter as though they were point measurements. An
integral is not a measurement at its midpoint.

**Two things the instruction requires that the archive does not deliver.** Times are
to be reported in UTC (*"Prøvetagningsdato og tidspunkt i UTC"*) — useful, because
`Startklok` is present on 100.0% of `kemi` rows and absent from every other topic, and
ODA offers no clock field at all for `ctd`, `lys` or `maaledybde`. And values below
the detection limit are to be reported as measured, negatives included — yet there is
**not one negative value in 1.8 million rows**, so either that was never followed or
the numbers were cleaned before ODA received them.

**`KorrektionsFaktor` is not one thing.** `KorrigeretResultat` is exactly
`OriginalResultat × KorrektionsFaktor` — verified on 199,999 of 199,999 rows carrying
all three — so a wrong factor corrupts the value silently and by construction. But what
the factor *means* differs per parameter, and the technical instructions say so:

* **Oxygen** ([Kap. 4](https://ecos.au.dk/fileadmin/ecos/Fagdatacentre/Marin/TA_NOVA_1998/Kap04.doc)):
  genuine instrument bias compensation. *"Faktor: O₂-Winkler/O₂-elektrode"* — the
  electrochemical sonde is checked against a Winkler iodometric titration on a bottle
  from 1 m, and if they disagree by more than 0.3 mg O₂/l the entire profile is
  multiplied by the ratio. Where the Winkler bottle fell inside a gradient, the profile
  is corrected instead by *the mean factor from other stations the same day* — so some
  corrected oxygen carries a calibration derived at a different station.
* **Fluorescence** ([Kap. 2](https://ecos.au.dk/fileadmin/ecos/Fagdatacentre/Marin/TA_NOVA_1998/Kap02.doc)):
  **not** bias compensation, and its large factors are correct. The instruction states
  that a fluorescence signal *"kan derfor ikke direkte omsættes til en pigment
  koncentration, selvom mange fabrikater i deres programmer angiver, at udlæsninger er
  i µg Chl l⁻¹"* — the manufacturers' claim is wrong — and that fluorescence per
  chlorophyll varies biologically, so *"et varierende FChl forhold [er] ikke et udtryk
  for instrument problemer"*. The factor is a unit conversion plus a live calibration
  against measured chlorophyll. Its 156,974 rows (2.3%) outside 0.5–2.0, to a maximum
  of 201×, are data and not faults. **Do not filter fluorescence on this column.**
* **CTD temperature, conductivity, pressure** ([Kap. 1](https://ecos.au.dk/fileadmin/ecos/Fagdatacentre/Marin/TA_NOVA_1998/Kap01.doc)):
  calibration coefficients live inside the sensor, estimated by the manufacturer or the
  institution, with annual recalibration and tank and in-situ checks. **No post-hoc
  multiplicative factor is described.** So the 606 temperature rows with a factor up to
  80×, and the 79 salinity rows up to 2346×, are not a documented procedure applied
  badly — they have no basis in the instruction at all.

A physical range check will not catch a bad factor: 0.5 applied to 18 °C gives 9 °C,
an unremarkable Danish sea temperature that happens to be wrong.

**A workaround worth knowing.** 99% of `kemi` station-days carry a single clock time,
and 123,866 of 155,182 `ctd` station-days (80%) have a matching `kemi` visit. A station-day
is effectively one moment, so the clock can be lent from one extract to the other —
which is the only route to putting a time on oxygen at depth.

## Practical notes

* `pip` is unavailable and RAM is ~1 GB, so every script is standard-library only and
  the viewer loads MapLibre from a CDN. No GDAL, no geopandas.
* Nothing here is authenticated. Re-running the fetch scripts reproduces `data/raw/`
  from scratch; only `data/manual/` is hand-authored.
* Licensing: the Copenhagen layers are published as open data via opendata.dk; the
  Miljøstyrelsen layers are public-sector open data. Attribute both if you republish.
