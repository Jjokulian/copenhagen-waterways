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

| source | unlocks | what it is | resolution |
|---|---|---|---|
| **NOVANA-PROG** | `A7` `E12` `F8` `G4` `H2` `I4` | NOVANA programme description 2023-2027 | n/a - this is the design document / n/a |
| **GBIF** | `F10` `F5` `F6` `F7` `F9` | GBIF occurrence API (dominated by the Danish national portal Arter.dk) | PER OBSERVATION with its own eventDate / per observation with its own lat/lon (a |
| **SR634** | `E10` `E6` `E7` `E8` `E9` | DCE Scientific Report 634 - Miljoefarlige forurenende stoffer 2023 | n/a - annual assessment report / n/a |
| **DCE-ILTSVIND** | `B8` `C4` `F9` `O1` | DCE/NOVANA iltsvind (oxygen deficit) bulletin series | biweekly, weeks 26-49 each year, plus quarterly syntheses / static maps of affec |
| **DMI-METOBS** | `B1` `D7` `G2` `G3` | DMI Open Data - metObs and climateData | 10-MINUTE raw (precip_past10min, precip_dur_past10min, precip_past1h, precip_dur |
| **DMI-OCEANOBS** | `C4` `C9` `D7` `G6` | DMI Open Data - oceanObs (sea level) | 10-MINUTE for modern data; 15-minute by 1990; hourly for digitised historical re |
| **ICES-DATRAS** | `F1` `F4` `F5` `O3` | ICES DATRAS - trawl survey database | PER HAUL, with Year/Month/Day and TimeShot / ShootLat/ShootLong and HaulLat/Haul |
| **ICES-OCEAN** | `A5` `C1` `C4` `C6` | ICES Oceanographic Database | per cast / point with coordinates |
| **MILJOEGIS-RBU-SAML** | `A4` `B1` `B2` `B3` | MiljoeGIS VP3/VP4 rain-conditioned outfall layers with discharge fields (*_punkt_rbu_saml) | one ANNUAL value per point per publication vintage (field 'aar') / point with co |
| **OBIS** | `F5` `F6` `F7` `O3` | OBIS occurrence API | per observation / per observation with coordinates |
| **PUNKTKILDER-RAPPORT** | `A4` `B3` `B5` `E5` | Punktkilderapporten (annual Danish point-source report), Bilag 1 and 2 | ANNUAL / named facility + municipality; no coordinates in the tables (those are  |
| **DDM** | `C3` `C7` `D7` | Danmarks Dybdemodel (Danish Depth Model) v2.0 | static composite; source surveys 1993-2024 / 50 m grid, 98,045 km2 of the Danish |
| **IOW-MBI** | `A5` `C1` `C4` | Major Baltic Inflow statistics (Mohrholz) | DAILY barotropic transport series, plus a discrete event list with dates, volume |
| **HELCOM-DEPOSITION** | `A3` `A5` | HELCOM atmospheric nitrogen deposition to the Baltic Sea 1990-2023 | annual / HELCOM sub-basin |
| **LFST-LANDINGS** | `F1` `F4` | Landbrugs- og Fiskeristyrelsen landings statistics | WEEKLY for the industrifisk tables / by landing PORT, not by ICES rectangle |
| **MST-KLAP** | `D2` `D3` | Miljoestyrelsen klaptilladelser (dumping permits), individual PDFs | per permit, with validity dates / named klapplads |
| **PSMSL** | `C9` `G6` | PSMSL Revised Local Reference monthly means | MONTHLY means / tide gauge station |
| **SPILDEVANDSDATA** | `B1` `B2` | spildevandsdata.dk - a PULS extract of overflow and stormwater outfalls | ANNUAL, calendar year 2020 only / point (WGS84) |
| **DCE-DEPOSITION** | `A3` | DCE 'Atmosfaerisk deposition' NOVANA reports (DEHM model) | ANNUAL / report tables per NAMED water body (Kattegat dansk/svensk del, Nordlige |
| **DST-AKV11** | `A8` | Danmarks Statistik AKV11 - aquaculture | ANNUAL / none - national totals by farm-type category |
| **DST-RST01** | `D4` | Danmarks Statistik RST01/RST04 raw-material extraction | ANNUAL / municipality / region |
| **DTU-MUSLING** | `F1` | DTU Aqua blue mussel stock assessments, Limfjorden | per survey year / Limfjorden as a whole in the published figures |
| **ENS-STAMDATA** | `C8` | Energistyrelsen Stamdataregister for vindmoeller | per turbine, with 'dato for oprindelig nettilslutning' (original grid connection |
| **ICES-CATCH** | `F4` | ICES Official Nominal Catch Statistics | ANNUAL / ICES subarea/division/subdivision |
| **MARIS** | `D4` | MARIS raw-material extraction API | per report period (the reports endpoint is closed) / polygon per extraction site |
| **METHANE-LIT** | `E4` | Kattegat methane seeps (boblerev) - the literature | one flux measurement, 1990s / one site |
| **MST-RAASTOF-PDF** | `D4` | Miljoestyrelsen extraction volumes for faellesomraader (shared sand/gravel licence areas) | PER QUARTER / per named area code (79 areas, e.g. 548-AA) |
| **PANGAEA-BENTHIC-FLUX** | `A7` | PANGAEA - in-situ benthic chamber nutrient flux (BIGO lander) | per timestep within each chamber incubation / point |
| **PANGAEA-CORES** | `H2` | PANGAEA - dated sediment cores, Skagerrak/Kattegat | per depth in core; derived record covers the last ~100 years / point per core st |
| **SGD-LIT** | `A6` | Danish submarine groundwater discharge - the two campaigns that exist | repeated seasonal campaigns 2011-2019 at Ringkoebing; one survey at Horsens / se |
| **WFD-DEFINITIONS** | `I4` | EU WFD intercalibration decisions and Danish miljoemaal bekendtgoerelser, with adoption da | dated legal instruments / n/a |

## Gated, but we hold the key — 11

*Behind a login this project already has working.*

| source | unlocks | what it is | resolution |
|---|---|---|---|
| **ODA-CTD** | `C2` `G1` `H1` `H3` `I1` `I2` `I3` `I5` `I6` | ODA - Hav / Feltmaaling / CTD | per cast, per depth bin (profile) / point, X/Y_UTM32 + lat/lon |
| **ODA-VANDKEMI-HAV** | `A1` `A2` `E11` `E2` `I5` `O4` | ODA - Hav / Vandkemi / Naeringsstof og Miljoefarligt stof | per sample (Startdato + Startklok) / point + GennemsnitsDybde_m per sample |
| **ODA-BUNDFAUNA** | `D1` `F2` `H3` `I1` `I3` | ODA - Hav / Bundfauna / Artsliste + Sediment | per grab, per date+time / point per grab (own lat/lon and UTM) |
| **ODA-STOFTRANSPORT** | `A1` `A2` `B4` `C5` | ODA - Vandloeb / Stoftransport / Maanedstransport | MONTHLY per station / point, X/Y_UTM32 per station |
| **ODA-TILFOERSEL** | `A1` `A2` `C5` `H4` | ODA - Naeringsstoftilfoersel til havet (nutrient input to the sea) | MONTHLY (output carries Aar and Maaned) / marine reference polygon; 387 referenc |
| **ODA-VEGETATION** | `F3` `H1` `O4` | ODA - Hav / Vegetation (aalegraes bundfauna / makroalge / plante) | per transect survey, per date / transect point |
| **ODA-MFS-FISK** | — | ODA - Hav / MFS i biota / Fisk | per sample, per date / point |
| **ODA-MFS-MUSLING** | — | ODA - Hav / MFS i biota / Musling (Mytilus edulis soft parts) | per sample, per date / point |
| **ODA-SEDKEMI-MFS** | — | ODA - Hav / Sedimentkemi / MFS Sporstof (hazardous substances in sediment) | per core, per date / point + sediment layer depth |
| **ODA-SEDKEMI-SPOR** | — | ODA - Hav / Sedimentkemi / Sporstof | per core, per date / point + SedimentLag Fra/Til (cm) |
| **ODA-VANDLOEB-MFS** | — | ODA - Vandloeb / Vandkemi / Miljoefarligt stof | per sample / point |

## One free registration away — 24

*A form and an email address. Nothing is being withheld; it just has not been done.*

| source | unlocks | what it is | resolution |
|---|---|---|---|
| **DMA-AIS** | `B7` `D6` | Danish Maritime Authority raw AIS archive | PER AIS MESSAGE (sub-minute), packaged as monthly zips for 2006-~2018 and DAILY  |
| **EMODNET-VESSELDENSITY** | `B7` `D6` | EMODnet Human Activities vessel density | MONTHLY, plus yearly averages / 1 km x 1 km raster |
| **GFW** | `B7` `D6` | Global Fishing Watch apparent fishing effort v3.0 | DAILY (0.01 and 0.1 deg) and MONTHLY (0.1 deg) / 0.01 deg or 0.1 deg grid cells |
| **PANGAEA-POREWATER** | `E1` `E3` | PANGAEA - sediment porewater chemistry, Danish and adjacent waters | one campaign each / point per core, per depth |
| **CMEMS-NWS-WAV** | `O2` | Copernicus Marine North-West Shelf Wave Reanalysis | hourly / 0.0135 x 0.0303 deg (~1.5 km), WAVEWATCH III, ERA5-forced |
| **EMODNET-SEABED-USE** | `D5` | EMODnet Human Activities seabed-use layers | varies by layer; mostly a status snapshot / points and polygons |
| **ICE** | `G5` | Sea ice for Danish waters - no single confirmed source | daily (satellite product) / 25 km satellite grid; SMHI ice charts are polygons |
| **ICES-VMS-SAR** | `D6` | ICES WGSFD VMS/logbook swept-area-ratio product | ANNUAL. Year is a required path parameter and there is no month field in this pr |
| **BSH-MARNET** | — | BSH MARNET automatic monitoring network | hourly / 9 automatic stations + 7 buoys, German Bight and western Baltic (Darss  |
| **CMEMS-BAL-BGC** | — | Copernicus Marine Baltic Sea Biogeochemistry Reanalysis | daily/monthly / 2 x 2 km, 56 depth levels |
| **CMEMS-BAL-PHY** | — | Copernicus Marine Baltic Sea Physics Reanalysis | daily / monthly / yearly / 2 x 2 km grid, 56 depth levels |
| **EEA-INDUSTRY** | — | EU Industrial Emissions Portal (formerly E-PRTR / IED reporting) | ANNUAL / point per facility with coordinates |
| **EEA-UWWTD** | — | Waterbase - UWWTD (Discharge Points, Agglomerations) | annual reporting cycles / point with coordinates |
| **EFAS** | — | EFAS historical river discharge (LISFLOOD) | 6-hourly / 1 x 1 arcmin (~1.5 km) river network |
| **EMEP** | — | EMEP MSC-W modelled deposition | MONTHLY (also daily and annual files) / 0.1 deg x 0.1 deg grid, 520 x 1200 cells |
| **EMODNET-BATHY** | — | EMODnet Bathymetry DTM | static, 2024 release / 1/16 arcmin (~115 m); some HR tiles finer |
| **EMODNET-FISHING** | — | EMODnet Human Activities fishing intensity WFS layers | published per fo_year (2020, 2021 seen) but the VALUE is a FOUR-YEAR ROLLING MEA |
| **ERA5** | — | ERA5 reanalysis, single levels | hourly / ~0.25 deg global grid |
| **HELCOM-FISHING-INTENSITY** | — | HELCOM MADS fishing intensity layers (ICES WGSFD product, HELCOM-processed) | PER YEAR (field 'Year'), one layer per gear class per year / c-square polygons,  |
| **ICES-DOME-BIOTA** | — | ICES DOME - contaminants in biota, Denmark | per specimen/pool per station per date / point |
| **ICES-DOME-SED** | — | ICES DOME - contaminants in sediment, Denmark | one row per sample per station per date / point with Latitude/Longitude, plus DE |
| **ICES-SAG** | — | ICES Stock Assessment Graphs (SAG) web service | ANNUAL / whole stock area (ICES subdivision/subarea), not gridded |
| **OSPAR-ODIMS** | — | OSPAR dumped-materials (dredged material disposal) submissions | PER DUMPING EVENT, within an annual submission / per klapplads (Deposit_Site_Cod |
| **VANDAH** | — | Vandah - hydrometric REST API (Dmp.Hydro.Api) | 10-MINUTE (verified: consecutive 23:40 / 23:50 / 00:00 records) / point, UTM32 ( |

## Not open — 14

*Request-only, FOI, institutional provisioning, or unverified. These are the ones worth arguing about publicly, because for several of them the measurement exists and the public cannot see it.*

| source | unlocks | what it is | resolution |
|---|---|---|---|
| **BADEVAND** | `B6` | Bathing water quality portal | per sample in season, plus a seasonal classification / ~1,039 named bathing site |
| **SHARK** | `A9` | SHARK - Swedish marine environmental monitoring data | per sample / point |
| **VANDA-API** | `A9` | VanDa REST API - the successor surface-water database | per sample / point |
| **B8-GAP** | — | Danish environmental incident / spill / fish-kill registers - confirmed absent in open for | n/a / n/a |
| **CMEMS-BAL-WAV** | — | Copernicus Marine Baltic Sea Wave Reanalysis | hourly / 2 x 2 km (WAM cycle 4.6/4.7, ERA5-forced) |
| **D2-GAP** | — | Danish navigation dredging permits - no working public register | n/a / n/a |
| **F8-GAP** | — | Microbial community composition in Danish coastal waters - confirmed blank | n/a / n/a |
| **FIMUS-STRANDINGS** | — | Beredskabet for havpattedyr - Danish marine mammal stranding records | per stranding event / per event location |
| **HAEDAT** | — | HAEDAT - Harmful Algae Event Database | per EVENT / by locality/area description, not point coordinates |
| **HELCOM-PLC** | — | HELCOM PLC (Pollution Load Compilation) data portal | ANNUAL (form offers year_begin/year_end, min 1995 max 2024) / per river / monito |
| **IOW-ODIN** | — | IOW ODIN2 data portal / Arkona and Darss Sill observatories | high frequency / fixed station, T and S at 8 depths (2-43 m) |
| **MST-HAVBRUG** | — | Miljoestyrelsen havbrug permits and egenkontrol reporting | annual reporting deadlines (15 Feb, 1 Jun, 1 Sep) / per licensed site |
| **NYBORG-OVERLOEB** | — | Nyborg Forsyning combined-sewer overflow telemetry (Grafana) | PER EVENT / near-real-time / point per overflow structure |
| **PULS** | — | PULS - Punktkilder og spildevand | annual per point (reported) / point |

## What this does not tell you

Friction is not value. Several entries in the last tier matter more than anything in the first — per-event overflow volumes, monthly trawling effort, and marine phytoplankton species counts are each closed, and each of them would settle a hypothesis that currently cannot be ranked at all. The tiers say what is easy, and the register says what is important; they are different questions and this page is only the first one.

