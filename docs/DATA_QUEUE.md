# The fetch queue

The source register records what exists. It does not say what to do on Monday. This is the same information sorted by friction: what can be downloaded now, what is behind a credential we already hold, what needs a free registration nobody has done, and what is genuinely closed.

**80 sources.** *Unlocks* counts hypotheses that this source serves and that nothing easier serves — a crude priority signal, and meant to be.

| tier | | sources |
|---|---|---:|
| `open` | Fetch it now | 31 |
| `held` | Gated, but we hold the key | 11 |
| `account` | One free registration away | 24 |
| `blocked` | Not open | 14 |

- **ODA / Overfladevandsdatabasen** — email login, scripted SOAP extract working in scripts/oda_client.py
- **Dataforsyningen** — API token on this machine, orthophoto WMS verified

## Fetch it now — 31

*No account, no permission, no negotiation.*

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **NOVANA-PROG** | `A7` `E12` `F8` `G4` `H2` `I4` | ? | NOVANA programme description 2023-2027 |
| **GBIF** | `F10` `F5` `F6` `F7` `F9` | position | GBIF occurrence API (dominated by the Danish national portal Arter.dk) |
| **SR634** | `E10` `E6` `E7` `E8` `E9` | ? | DCE Scientific Report 634 - Miljoefarlige forurenende stoffer 2023 |
| **DCE-ILTSVIND** | `B8` `C4` `F9` `O1` | position | DCE/NOVANA iltsvind (oxygen deficit) bulletin series |
| **DMI-METOBS** | `B1` `D7` `G2` `G3` | position | DMI Open Data - metObs and climateData |
| **DMI-OCEANOBS** | `C4` `C9` `D7` `G6` | position | DMI Open Data - oceanObs (sea level) |
| **ICES-DATRAS** | `F1` `F4` `F5` `O3` | position | ICES DATRAS - trawl survey database |
| **ICES-OCEAN** | `A5` `C1` `C4` `C6` | position | ICES Oceanographic Database |
| **MILJOEGIS-RBU-SAML** | `A4` `B1` `B2` `B3` | position | MiljoeGIS VP3/VP4 rain-conditioned outfall layers with discharge fields (*_punkt_rbu_sam |
| **OBIS** | `F5` `F6` `F7` `O3` | position | OBIS occurrence API |
| **PUNKTKILDER-RAPPORT** | `A4` `B3` `B5` `E5` | mixed | Punktkilderapporten (annual Danish point-source report), Bilag 1 and 2 |
| **DDM** | `C3` `C7` `D7` | position | Danmarks Dybdemodel (Danish Depth Model) v2.0 |
| **IOW-MBI** | `A5` `C1` `C4` | position | Major Baltic Inflow statistics (Mohrholz) |
| **HELCOM-DEPOSITION** | `A3` `A5` | **region** | HELCOM atmospheric nitrogen deposition to the Baltic Sea 1990-2023 |
| **LFST-LANDINGS** | `F1` `F4` | **region** | Landbrugs- og Fiskeristyrelsen landings statistics |
| **MST-KLAP** | `D2` `D3` | ? | Miljoestyrelsen klaptilladelser (dumping permits), individual PDFs |
| **PSMSL** | `C9` `G6` | ? | PSMSL Revised Local Reference monthly means |
| **SPILDEVANDSDATA** | `B1` `B2` | position | spildevandsdata.dk - a PULS extract of overflow and stormwater outfalls |
| **DCE-DEPOSITION** | `A3` | mixed | DCE 'Atmosfaerisk deposition' NOVANA reports (DEHM model) |
| **DST-AKV11** | `A8` | **region** | Danmarks Statistik AKV11 - aquaculture |
| **DST-RST01** | `D4` | **region** | Danmarks Statistik RST01/RST04 raw-material extraction |
| **DTU-MUSLING** | `F1` | ? | DTU Aqua blue mussel stock assessments, Limfjorden |
| **ENS-STAMDATA** | `C8` | position | Energistyrelsen Stamdataregister for vindmoeller |
| **ICES-CATCH** | `F4` | **region** | ICES Official Nominal Catch Statistics |
| **MARIS** | `D4` | mixed | MARIS raw-material extraction API |
| **METHANE-LIT** | `E4` | ? | Kattegat methane seeps (boblerev) - the literature |
| **MST-RAASTOF-PDF** | `D4` | ? | Miljoestyrelsen extraction volumes for faellesomraader (shared sand/gravel licence areas |
| **PANGAEA-BENTHIC-FLUX** | `A7` | position | PANGAEA - in-situ benthic chamber nutrient flux (BIGO lander) |
| **PANGAEA-CORES** | `H2` | position | PANGAEA - dated sediment cores, Skagerrak/Kattegat |
| **SGD-LIT** | `A6` | position | Danish submarine groundwater discharge - the two campaigns that exist |
| **WFD-DEFINITIONS** | `I4` | ? | EU WFD intercalibration decisions and Danish miljoemaal bekendtgoerelser, with adoption  |

## Gated, but we hold the key — 11

*Behind a login this project already has working.*

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **ODA-CTD** | `C2` `G1` `H1` `H3` `I1` `I2` `I3` `I5` `I6` | position | ODA - Hav / Feltmaaling / CTD |
| **ODA-VANDKEMI-HAV** | `A1` `A2` `E11` `E2` `I5` `O4` | position | ODA - Hav / Vandkemi / Naeringsstof og Miljoefarligt stof |
| **ODA-BUNDFAUNA** | `D1` `F2` `H3` `I1` `I3` | position | ODA - Hav / Bundfauna / Artsliste + Sediment |
| **ODA-STOFTRANSPORT** | `A1` `A2` `B4` `C5` | position | ODA - Vandloeb / Stoftransport / Maanedstransport |
| **ODA-TILFOERSEL** | `A1` `A2` `C5` `H4` | **region** | ODA - Naeringsstoftilfoersel til havet (nutrient input to the sea) |
| **ODA-VEGETATION** | `F3` `H1` `O4` | position | ODA - Hav / Vegetation (aalegraes bundfauna / makroalge / plante) |
| **ODA-MFS-FISK** | — | position | ODA - Hav / MFS i biota / Fisk |
| **ODA-MFS-MUSLING** | — | position | ODA - Hav / MFS i biota / Musling (Mytilus edulis soft parts) |
| **ODA-SEDKEMI-MFS** | — | position | ODA - Hav / Sedimentkemi / MFS Sporstof (hazardous substances in sediment) |
| **ODA-SEDKEMI-SPOR** | — | position | ODA - Hav / Sedimentkemi / Sporstof |
| **ODA-VANDLOEB-MFS** | — | position | ODA - Vandloeb / Vandkemi / Miljoefarligt stof |

## One free registration away — 24

*A form and an email address. Nothing is being withheld; it just has not been done.*

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **DMA-AIS** | `B7` `D6` | position | Danish Maritime Authority raw AIS archive |
| **EMODNET-VESSELDENSITY** | `B7` `D6` | position | EMODnet Human Activities vessel density |
| **GFW** | `B7` `D6` | position | Global Fishing Watch apparent fishing effort v3.0 |
| **PANGAEA-POREWATER** | `E1` `E3` | position | PANGAEA - sediment porewater chemistry, Danish and adjacent waters |
| **CMEMS-NWS-WAV** | `O2` | ? | Copernicus Marine North-West Shelf Wave Reanalysis |
| **EMODNET-SEABED-USE** | `D5` | mixed | EMODnet Human Activities seabed-use layers |
| **ICE** | `G5` | mixed | Sea ice for Danish waters - no single confirmed source |
| **ICES-VMS-SAR** | `D6` | **region** | ICES WGSFD VMS/logbook swept-area-ratio product |
| **BSH-MARNET** | — | ? | BSH MARNET automatic monitoring network |
| **CMEMS-BAL-BGC** | — | ? | Copernicus Marine Baltic Sea Biogeochemistry Reanalysis |
| **CMEMS-BAL-PHY** | — | position | Copernicus Marine Baltic Sea Physics Reanalysis |
| **EEA-INDUSTRY** | — | mixed | EU Industrial Emissions Portal (formerly E-PRTR / IED reporting) |
| **EEA-UWWTD** | — | position | Waterbase - UWWTD (Discharge Points, Agglomerations) |
| **EFAS** | — | ? | EFAS historical river discharge (LISFLOOD) |
| **EMEP** | — | mixed | EMEP MSC-W modelled deposition |
| **EMODNET-BATHY** | — | ? | EMODnet Bathymetry DTM |
| **EMODNET-FISHING** | — | **region** | EMODnet Human Activities fishing intensity WFS layers |
| **ERA5** | — | position | ERA5 reanalysis, single levels |
| **HELCOM-FISHING-INTENSITY** | — | **region** | HELCOM MADS fishing intensity layers (ICES WGSFD product, HELCOM-processed) |
| **ICES-DOME-BIOTA** | — | position | ICES DOME - contaminants in biota, Denmark |
| **ICES-DOME-SED** | — | position | ICES DOME - contaminants in sediment, Denmark |
| **ICES-SAG** | — | position | ICES Stock Assessment Graphs (SAG) web service |
| **OSPAR-ODIMS** | — | **region** | OSPAR dumped-materials (dredged material disposal) submissions |
| **VANDAH** | — | position | Vandah - hydrometric REST API (Dmp.Hydro.Api) |

## Not open — 14

*Request-only, FOI, institutional provisioning, or unverified. These are the ones worth arguing about publicly, because for several of them the measurement exists and the public cannot see it.*

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **BADEVAND** | `B6` | position | Bathing water quality portal |
| **SHARK** | `A9` | position | SHARK - Swedish marine environmental monitoring data |
| **VANDA-API** | `A9` | position | VanDa REST API - the successor surface-water database |
| **B8-GAP** | — | ? | Danish environmental incident / spill / fish-kill registers - confirmed absent in open f |
| **CMEMS-BAL-WAV** | — | ? | Copernicus Marine Baltic Sea Wave Reanalysis |
| **D2-GAP** | — | ? | Danish navigation dredging permits - no working public register |
| **F8-GAP** | — | ? | Microbial community composition in Danish coastal waters - confirmed blank |
| **FIMUS-STRANDINGS** | — | ? | Beredskabet for havpattedyr - Danish marine mammal stranding records |
| **HAEDAT** | — | position | HAEDAT - Harmful Algae Event Database |
| **HELCOM-PLC** | — | mixed | HELCOM PLC (Pollution Load Compilation) data portal |
| **IOW-ODIN** | — | ? | IOW ODIN2 data portal / Arkona and Darss Sill observatories |
| **MST-HAVBRUG** | — | position | Miljoestyrelsen havbrug permits and egenkontrol reporting |
| **NYBORG-OVERLOEB** | — | position | Nyborg Forsyning combined-sewer overflow telemetry (Grafana) |
| **PULS** | — | position | PULS - Punktkilder og spildevand |

## The resolution rule

Nothing here is stored at an administrative unit — not per water body, not per catchment, not per municipality, not per sub-basin. Everything is carried at the resolution it was taken: a position, a time, and where it exists a depth.

That is not fastidiousness. [OBSERVING.md](#OBSERVING.md) establishes that a water body explains **7.9%** of the variation in the one variable Denmark measures densely enough to check, and that two stations inside one share about four percent of their year-to-year variance. A source already summed into those polygons would carry the assumption straight back in, and everything computed from it would inherit a unit we had just shown is not one.

| indexed by | sources | |
|---|---:|---|
| position | 43 | a place something was measured |
| **region** | 10 | somebody's aggregate; usable, but never as a measurement |
| mixed | 8 | carries both; take the position field |
| ? | 19 | not stated clearly enough to tell |

The region-indexed sources are often the only version that exists, and several matter a great deal — the monthly nutrient input series is per marine reference polygon, and there is no per-outfall alternative. They enter the panel labelled as somebody's aggregate of a measurement, and never as the measurement.

> **What a water body actually is, if it is anything, is a question to be answered from the data rather than assumed by the schema.** Put the observations on the map with their own coordinates and times, see which move together, and check every proxy against an unrelated one. The administrative polygon is then an overlay to be tested against — not a container to pour things into.

## What this does not tell you

Friction is not value. Several entries in the last tier matter more than anything in the first — per-event overflow volumes, monthly trawling effort, and marine phytoplankton species counts are each closed, and each of them would settle a hypothesis that currently cannot be ranked at all. The tiers say what is easy, and the register says what is important; they are different questions and this page is only the first one.

