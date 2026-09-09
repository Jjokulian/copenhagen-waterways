# The fetch queue

The source register records what exists. It does not say what to do on Monday. This is the same information sorted by friction: what can be downloaded now, what is behind a credential we already hold, what needs a free registration nobody has done, and what is genuinely closed.

**145 sources.** *Unlocks* counts hypotheses that this source serves and that nothing easier serves — a crude priority signal, and meant to be.

| tier | | sources |
|---|---|---:|
| `open` | Fetch it now | 59 |
| `held` | Gated, but we hold the key | 22 |
| `account` | One free registration away | 30 |
| `blocked` | Not open | 34 |

- **ODA / Overfladevandsdatabasen** — email login, scripted SOAP extract working in scripts/oda_client.py
- **Dataforsyningen** — API token on this machine, orthophoto WMS verified

## Fetch it now — 59

*No account, no permission, no negotiation.*

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **NOVANA-PROG** | `A7` `E12` `F8` `G4` `H2` `I4` | ? | NOVANA programme description 2023-2027 |
| **AL561-KATTEGAT-SKAGERRAK** | `A7` `R5` `R6` `R7` `T7` | ? | ALKOR AL561 (APOC) - Kattegat to Skagerrak particulate and porewater geochemistry with i |
| **GBIF** | `F10` `F5` `F6` `F7` `F9` | position | GBIF occurrence API (dominated by the Danish national portal Arter.dk) |
| **SR634** | `E10` `E6` `E7` `E8` `E9` | ? | DCE Scientific Report 634 - Miljoefarlige forurenende stoffer 2023 |
| **DCE-ILTSVIND** | `B8` `C4` `F9` `O1` | position | DCE/NOVANA iltsvind (oxygen deficit) bulletin series |
| **DMI-METOBS** | `B1` `D7` `G2` `G3` | position | DMI Open Data - metObs and climateData |
| **DMI-OCEANOBS** | `C4` `C9` `D7` `G6` | position | DMI Open Data - oceanObs (sea level) |
| **EMODNET-SEABED-HABITATS** | `D10` `K12` `L5` `L6` | mixed | EMODnet Seabed Habitats - EUSeaMap/HELCOM HUB modelled habitat map, and the ground-truth |
| **GEUS-HAVBUNDSSEDIMENT** | `D10` `L6` `R7` `S5` | position | Havbundssedimentkort - seabed surface sediment map of Danish waters |
| **HORSENS-EELGRASS-TRANSPLANT** | `F3` `K12` `L4` `T4` | position | Bisholt, outer Horsens Fjord - large-scale eelgrass transplant with bare-bottom and natu |
| **ICES-CONTAM-BIOTA-OBIS** | `E10` `E6` `K8` `K9` | position | ICES DOME contaminants and biological effects in biota, Danish subset, through OBIS and  |
| **ICES-DATRAS** | `F1` `F4` `F5` `O3` | position | ICES DATRAS - trawl survey database |
| **ICES-OCEAN** | `A5` `C1` `C4` `C6` | position | ICES Oceanographic Database |
| **ICES-PHYTO-OBIS** | `A9` `F7` `K1` `K2` | position | ICES Phytoplankton Community dataset, Danish subset, reachable through OBIS |
| **ICES-ZOOBENTHOS-OBIS** | `D11` `D9` `K10` `K14` | position | ICES Zoobenthos Community dataset, Danish subset, through OBIS |
| **MILJOEGIS-RBU-SAML** | `A4` `B1` `B2` `B3` | position | MiljoeGIS VP3/VP4 rain-conditioned outfall layers with discharge fields (*_punkt_rbu_sam |
| **OBIS** | `F5` `F6` `F7` `O3` | position | OBIS occurrence API |
| **PUNKTKILDER-RAPPORT** | `A4` `B3` `B5` `E5` | mixed | Punktkilderapporten (annual Danish point-source report), Bilag 1 and 2 |
| **ASMALA-ROSKILDE-DOC** | `J7` `R1` `R7` | ? | Roskilde Fjord water-column DOC, TOC, nutrients, chlorophyll and DOM optics, 2014-2015 |
| **BORNHOLM-SEDEX** | `H2` `R6` `S4` | **region** | IODP 347-M0065 Bornholm Basin - sequential phosphorus extraction (SEDEX) |
| **DCE-TA-M06-LYS** | `K11` `L3` `O4` | ? | NOVANA technical instruction M06 - Lyssvaekkelse: how Kd and Secchi are actually measure |
| **DCE-TA-M12-M18-GAP** | `F3` `K3` `T1` | ? | NOVANA technical instructions M18 (eelgrass) and M12 (macroalgae) - what the vegetation  |
| **DDM** | `C3` `C7` `D7` | position | Danmarks Dybdemodel (Danish Depth Model) v2.0 |
| **EU-IED-TOC** | `B3` `B5` `R1` | **region** | EU Industrial Emissions / E-PRTR reporting - Total Organic Carbon to water, and the abse |
| **FOSSING-METROL-AARHUS** | `E12` `R5` `T7` | ? | METROL Aarhus Bay cores - porewater sulphate, methane, hydrogen sulphide, TOC and TN by  |
| **GEUS-MARTA** | `D4` `K12` `L6` | position | GEUS Marta - marine raw material database (sand, gravel, stone) |
| **IOW-MBI** | `A5` `C1` `C4` | position | Major Baltic Inflow statistics (Mohrholz) |
| **ODENSE-FJORD-CN** | `A9` `D8` `R1` | ? | Sediment resuspension and pelagic nitrogen fixation, Odense Fjord - core incubations wit |
| **PANGAEA-AARHUS-ORGANICACIDS** | `R2` `R5` `T7` | position | PANGAEA - Aarhus Bay porewater organic acids, sulphate, methane and sulphate reduction r |
| **BOKNIS-ECK-SML** | `J1` `J2` | ? | Seasonal variation of the sea-surface microlayer at Boknis Eck, Kiel Bight |
| **EU-INTERCAL-2013-480** | `I4` `L2` | ? | Commission Decision 2013/480/EU - WFD intercalibration, Baltic GIG coastal types |
| **GEUS-NRETENTION** | `S1` `S6` | mixed | National nitrogen retention maps for Denmark, version 2026 |
| **HELCOM-DEPOSITION** | `A3` `A5` | **region** | HELCOM atmospheric nitrogen deposition to the Baltic Sea 1990-2023 |
| **LABYRINTHULA-DK** | `T3` `T8` | position | Labyrinthula in Denmark - one qPCR site and fifteen metabarcoding hits |
| **LFST-LANDINGS** | `F1` `F4` | **region** | Landbrugs- og Fiskeristyrelsen landings statistics |
| **MST-KLAP** | `D2` `D3` | ? | Miljoestyrelsen klaptilladelser (dumping permits), individual PDFs |
| **PSMSL** | `C9` `G6` | ? | PSMSL Revised Local Reference monthly means |
| **SPILDEVANDSDATA** | `B1` `B2` | position | spildevandsdata.dk - a PULS extract of overflow and stormwater outfalls |
| **DCE-DEPOSITION** | `A3` | mixed | DCE 'Atmosfaerisk deposition' NOVANA reports (DEHM model) |
| **DMI-RADIA-GLOB** | `K11` | ? | DMI Open Data metObs - global radiation (radia_glob) |
| **DST-AKV11** | `A8` | **region** | Danmarks Statistik AKV11 - aquaculture |
| **DST-RST01** | `D4` | **region** | Danmarks Statistik RST01/RST04 raw-material extraction |
| **DTU-MUSLING** | `F1` | ? | DTU Aqua blue mussel stock assessments, Limfjorden |
| **ENS-STAMDATA** | `C8` | position | Energistyrelsen Stamdataregister for vindmoeller |
| **GEUS-JORDART200K** | `S1` | **region** | Jordartskort over Danmark 1:200.000 |
| **GEUS-JORDART25K** | `S1` | mixed | Danmarks Digitale Jordartskort 1:25.000 (v7.1) |
| **GEUS-KVARTAERTYKKELSE** | `S5` | position | Kvartaerets tykkelse i Danmark (Quaternary thickness) |
| **HALOPHYTOPHTHORA-LIMFJORD** | `T8` | position | Marine oomycetes isolated from Zostera marina, including Limfjorden |
| **HEREON-UVFILTERS** | `J4` | position | Organic UV stabilisers and UV filters in North Sea and Baltic sediment, 2015-2017 |
| **ICES-CATCH** | `F4` | **region** | ICES Official Nominal Catch Statistics |
| **K7-CARBONATE-CONTEXT** | `K7` | ? | The carbonate-system context around Denmark - no Danish station, neighbours' lines only |
| **MARIS** | `D4` | mixed | MARIS raw-material extraction API |
| **METHANE-LIT** | `E4` | ? | Kattegat methane seeps (boblerev) - the literature |
| **MST-RAASTOF-PDF** | `D4` | ? | Miljoestyrelsen extraction volumes for faellesomraader (shared sand/gravel licence areas |
| **OBIS-GBIF-LUCINIDER** | `T2` | position | OBIS and GBIF occurrence counts for the sulphide-oxidising bivalves in Danish waters |
| **PANGAEA-BENTHIC-FLUX** | `A7` | position | PANGAEA - in-situ benthic chamber nutrient flux (BIGO lander) |
| **PANGAEA-CORES** | `H2` | position | PANGAEA - dated sediment cores, Skagerrak/Kattegat |
| **SGD-LIT** | `A6` | position | Danish submarine groundwater discharge - the two campaigns that exist |
| **WFD-DEFINITIONS** | `I4` | ? | EU WFD intercalibration decisions and Danish miljoemaal bekendtgoerelser, with adoption  |

## Gated, but we hold the key — 22

*Behind a login this project already has working.*

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **ODA-CTD** | `C2` `G1` `H1` `H3` `I1` `I2` `I3` `I5` `I6` | position | ODA - Hav / Feltmaaling / CTD |
| **ODA-BUNDFAUNA** | `D1` `F2` `H3` `I1` `I3` | position | ODA - Hav / Bundfauna / Artsliste + Sediment |
| **ODA-VANDKEMI-HAV** | `A1` `A2` `E11` `E2` `I5` | position | ODA - Hav / Vandkemi / Naeringsstof og Miljoefarligt stof |
| **ODA-STOFTRANSPORT** | `A1` `A2` `B4` `C5` | position | ODA - Vandloeb / Stoftransport / Maanedstransport |
| **ODA-TILFOERSEL** | `A1` `A2` `C5` `H4` | **region** | ODA - Naeringsstoftilfoersel til havet (nutrient input to the sea) |
| **ODA-MARINE-NEGATIVES** | `J3` `K5` `K6` | ? | The complete ODA marine parameter space - what is provably not in it |
| **ODA-AFFALD-PLASTIK** | `J5` | position | ODA - Hav / Marint affald and Plastik i biota (schema present, no data exposed) |
| **ODA-BUNDFAUNA-SEDIMENT** | `R3` | position | ODA - Hav / Bundfauna / Sediment (grain size and sediment character at the fauna station |
| **ODA-STATION-COUNTS-CORRECTION** | `R3` | ? | ODA station counts are period-dependent - the numbers in data_sources.json are the wrong |
| **ODA-VEGETATION** | `H1` | position | ODA - Hav / Vegetation (aalegraes bundfauna / makroalge / plante) |
| **ODA-BUNDFAUNA-LUCINIDER** | — | ? | ODA bundfauna taxon list - the sulphide-oxidising bivalves are in it |
| **ODA-BUNDFAUNA-REPLICATES** | — | position | ODA - Hav / Bundfauna / Artsliste, at replicate-grab resolution |
| **ODA-LYSSVAEKKELSE** | — | position | ODA - Hav / Feltmaaling / Lyssvaekkelse (light attenuation profiles) |
| **ODA-MAALEDYBDE** | — | position | ODA - Hav / Maaledybde (Secchi depth and bottom depth) |
| **ODA-MFS-FISK** | — | position | ODA - Hav / MFS i biota / Fisk |
| **ODA-MFS-MUSLING** | — | position | ODA - Hav / MFS i biota / Musling (Mytilus edulis soft parts) |
| **ODA-SECCHI-LONG** | — | position | The Danish Secchi record in ODA, once the period is set - 1983 to 2024, continuous |
| **ODA-SEDKEMI-MFS** | — | position | ODA - Hav / Sedimentkemi / MFS Sporstof (hazardous substances in sediment) |
| **ODA-SEDKEMI-SPOR** | — | position | ODA - Hav / Sedimentkemi / Sporstof |
| **ODA-SI-N-P** | — | position | ODA marine water chemistry as a ratio source - Si, N, P, pH and alkalinity in one table |
| **ODA-VANDLOEB-MFS** | — | position | ODA - Vandloeb / Vandkemi / Miljoefarligt stof |
| **ODA-VEGETATION-FELTER** | — | position | ODA - Hav / Vegetation, at field level (three separate topics) |

## One free registration away — 30

*A form and an email address. Nothing is being withheld; it just has not been done.*

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **DMA-AIS** | `B7` `D6` | position | Danish Maritime Authority raw AIS archive |
| **EMODNET-VESSELDENSITY** | `B7` `D6` | position | EMODnet Human Activities vessel density |
| **ENA-DK-COASTAL-16S** | `J8` `T5` | position | Danish coastal-water microbial sequence data in ENA |
| **ENA-MGNIFY-DK-SEDIMENT** | `T5` `T6` | position | Danish marine sediment microbial sequence data in ENA and MGnify |
| **GFW** | `B7` `D6` | position | Global Fishing Watch apparent fishing effort v3.0 |
| **PANGAEA-POREWATER** | `E1` `E3` | position | PANGAEA - sediment porewater chemistry, Danish and adjacent waters |
| **CDSE-SENTINEL1** | `J6` | **region** | Sentinel-1 GRD SAR over Danish waters, Copernicus Data Space Ecosystem |
| **CMEMS-NWS-WAV** | `O2` | ? | Copernicus Marine North-West Shelf Wave Reanalysis |
| **EMODNET-SEABED-USE** | `D5` | mixed | EMODnet Human Activities seabed-use layers |
| **ICE** | `G5` | mixed | Sea ice for Danish waters - no single confirmed source |
| **ICES-VMS-SAR** | `D6` | **region** | ICES WGSFD VMS/logbook swept-area-ratio product |
| **LOOP** | `S2` | mixed | LOOP - Landovervaagningsoplandene (agricultural catchment monitoring with root-zone and  |
| **BSH-MARNET** | — | ? | BSH MARNET automatic monitoring network |
| **CMEMS-BAL-BGC** | — | ? | Copernicus Marine Baltic Sea Biogeochemistry Reanalysis |
| **CMEMS-BAL-PHY** | — | position | Copernicus Marine Baltic Sea Physics Reanalysis |
| **EEA-INDUSTRY** | — | mixed | EU Industrial Emissions Portal (formerly E-PRTR / IED reporting) |
| **EEA-UWWTD** | — | position | Waterbase - UWWTD (Discharge Points, Agglomerations) |
| **EFAS** | — | ? | EFAS historical river discharge (LISFLOOD) |
| **EMEP** | — | mixed | EMEP MSC-W modelled deposition |
| **EMODNET-BATHY** | — | ? | EMODnet Bathymetry DTM |
| **EMODNET-FISHING** | — | **region** | EMODnet Human Activities fishing intensity WFS layers |
| **EMODNET-LITTER-DK** | — | position | EMODnet Chemistry marine litter - Danish beach and seafloor records, and the microlitter |
| **ERA5** | — | position | ERA5 reanalysis, single levels |
| **HELCOM-FISHING-INTENSITY** | — | **region** | HELCOM MADS fishing intensity layers (ICES WGSFD product, HELCOM-processed) |
| **HOLMER-SULFIDE-FIGSHARE** | — | position | Sulfide intrusion and detoxification in Zostera marina - the raw data |
| **ICES-DOME-BIOTA** | — | position | ICES DOME - contaminants in biota, Denmark |
| **ICES-DOME-SED** | — | position | ICES DOME - contaminants in sediment, Denmark |
| **ICES-SAG** | — | position | ICES Stock Assessment Graphs (SAG) web service |
| **OSPAR-ODIMS** | — | **region** | OSPAR dumped-materials (dredged material disposal) submissions |
| **VANDAH** | — | position | Vandah - hydrometric REST API (Dmp.Hydro.Api) |

## Not open — 34

*Request-only, FOI, institutional provisioning, or unverified. These are the ones worth arguing about publicly, because for several of them the measurement exists and the public cannot see it.*

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **R2-R4-R8-R9-R10-GAP** | `R10` `R4` `R8` `R9` | ? | Five decomposition experiments that have never been run in Danish water |
| **BADEVAND** | `B6` | position | Bathing water quality portal |
| **K4-M74-GAP** | `K4` | ? | Thiamine deficiency and M74 - no Danish assay, and the Swedish series not opened |
| **K5-K6-K13-GAP** | `K13` | ? | Cobalamin, iron speciation and particle size spectra in Danish waters - none found |
| **L1-GAP** | `L1` | ? | Dated diatom or pigment stratigraphy from Danish coastal sediment - confirmed absent fro |
| **S1-PAPERS** | `S3` | ? | The Danish soil-and-sediment process papers that stand in for the missing datasets |
| **S2-GAP** | `S3` | ? | Danish soil phosphorus status by area - confirmed absent as open data |
| **B8-GAP** | — | ? | Danish environmental incident / spill / fish-kill registers - confirmed absent in open f |
| **BIOTIC-MARLIN** | — | ? | BIOTIC - Biological Traits Information Catalogue |
| **CMEMS-BAL-WAV** | — | ? | Copernicus Marine Baltic Sea Wave Reanalysis |
| **D2-GAP** | — | ? | Danish navigation dredging permits - no working public register |
| **DANISH-PORTALS-BLOCKED** | — | ? | Danish research-portal infrastructure is closed to automated retrieval |
| **DOME-METALS-WATERCOLUMN-GAP** | — | ? | Dissolved trace metals in the Danish marine water column - confirmed absent |
| **EMSA-CLEANSEANET-GAP** | — | ? | EMSA CleanSeaNet oil-slick detections - restricted to national authorities |
| **F8-GAP** | — | ? | Microbial community composition in Danish coastal waters - confirmed blank |
| **FIMUS-STRANDINGS** | — | ? | Beredskabet for havpattedyr - Danish marine mammal stranding records |
| **HAEDAT** | — | position | HAEDAT - Harmful Algae Event Database |
| **HELCOM-OILSPILLS** | — | position | HELCOM detected spills of mineral oil and other substances - aerial surveillance, per ob |
| **HELCOM-PLC** | — | mixed | HELCOM PLC (Pollution Load Compilation) data portal |
| **ICES-DOME-EXTRACTION-GAP** | — | ? | ICES DOME direct extraction - where the numbers are, and why they did not come out |
| **IOW-ODIN** | — | ? | IOW ODIN2 data portal / Arkona and Darss Sill observatories |
| **J1-J2-J3-GAP** | — | ? | TEP, sea-surface microlayer and surfactants in Danish waters - confirmed absent, twice o |
| **K12-STENREV-GAP** | — | ? | Danish stone-reef removal and restoration as data - not located |
| **L2-DERIVATION** | — | **region** | The Danish reference-condition derivation chain, as papers |
| **L4-DEPOSIT-GAP** | — | ? | Named Danish restoration projects with no deposited data - NOVAGRASS, ReMAPP, Laesoe Tri |
| **L6-GAP** | — | ? | Historical Danish seabed structure - charts, stenfiskeri records and oyster beds, not lo |
| **MST-HAVBRUG** | — | position | Miljoestyrelsen havbrug permits and egenkontrol reporting |
| **NYBORG-OVERLOEB** | — | position | Nyborg Forsyning combined-sewer overflow telemetry (Grafana) |
| **PULS** | — | position | PULS - Punktkilder og spildevand |
| **R1-FEDT-GAP** | — | ? | Fat and lipid as a reported Danish discharge parameter - unresolved |
| **R6-FE-S-GAP** | — | ? | Paired sequential iron AND sulphur extraction on Danish sediment - confirmed absent |
| **R7-TOC-MAP-GAP** | — | ? | A sediment organic-carbon map for Danish waters - confirmed absent from the national pro |
| **SHARK** | — | position | SHARK - Swedish marine environmental monitoring data |
| **VANDA-API** | — | position | VanDa REST API - the successor surface-water database |

## The resolution rule

Nothing here is stored at an administrative unit — not per water body, not per catchment, not per municipality, not per sub-basin. Everything is carried at the resolution it was taken: a position, a time, and where it exists a depth.

That is not fastidiousness. [OBSERVING.md](OBSERVING.md) establishes that a water body explains **7.9%** of the variation in the one variable Denmark measures densely enough to check, and that two stations inside one share about four percent of their year-to-year variance. A source already summed into those polygons would carry the assumption straight back in, and everything computed from it would inherit a unit we had just shown is not one.

| indexed by | sources | |
|---|---:|---|
| position | 68 | a place something was measured |
| **region** | 15 | somebody's aggregate; usable, but never as a measurement |
| mixed | 12 | carries both; take the position field |
| ? | 50 | not stated clearly enough to tell |

The region-indexed sources are often the only version that exists, and several matter a great deal — the monthly nutrient input series is per marine reference polygon, and there is no per-outfall alternative. They enter the panel labelled as somebody's aggregate of a measurement, and never as the measurement.

> **What a water body actually is, if it is anything, is a question to be answered from the data rather than assumed by the schema.** Put the observations on the map with their own coordinates and times, see which move together, and check every proxy against an unrelated one. The administrative polygon is then an overlay to be tested against — not a container to pour things into.

## What this does not tell you

Friction is not value. Several entries in the last tier matter more than anything in the first — per-event overflow volumes, monthly trawling effort, and marine phytoplankton species counts are each closed, and each of them would settle a hypothesis that currently cannot be ranked at all. The tiers say what is easy, and the register says what is important; they are different questions and this page is only the first one.

