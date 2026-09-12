# The fetch queue

<span class="claim" data-claim="C-DQ-Q-PURPOSE">The source register records what exists; this page sorts its entries by friction: what can be downloaded now, what sits behind a credential this project holds, what needs a registration it has not made, and what the register's access text does not show to be reachable.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-PURPOSE "What this claim rests on")</sup>

<span class="claim" data-claim="C-DQ-Q-COUNT">**[148](SOURCES.md#F-bfada8d583) sources**, from `data_sources.json` and `data_sources_2.json`. `data_sources_3.json`, also part of the register, is not read by this queue, so its entries are in none of the tiers below.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-COUNT "What this claim rests on")</sup> <span class="claim" data-claim="C-DQ-Q-UNLOCKS">*Unlocks* lists the hypotheses an entry names that no entry in an easier tier also names — a crude priority signal, and meant to be.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-UNLOCKS "What this claim rests on")</sup>

<span class="claim" data-claim="C-DQ-Q-TIERS">Each entry's tier is read from its access text by keyword, in this order: an ODA topic, or a source that names Dataforsyningen, is *held*; words for not public, request-only, FOI, provisioning, unverified or no download make it *blocked*; words for a registration, an account, a login or a token make it *account*; words for an open or key-free download make it *open*; and an entry that matches none of these is counted as *blocked*. Because the account words are tested before the open ones, an access text saying that no login or no registration is needed is counted as *account*. The tiers have not been checked by hand entry by entry, and the note under the credentials shows where they go wrong for the Copernicus entries.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-TIERS "What this claim rests on")</sup>

| tier | | sources |
|---|---|---:|
| `open` | Fetch it now | [59](SOURCES.md#F-a7cb1a9012) |
| `held` | Gated, but we hold the key | [22](SOURCES.md#F-46c5c33c27) |
| `account` | One free registration away | [30](SOURCES.md#F-542c824a5b) |
| `blocked` | Not open | [37](SOURCES.md#F-d3261ec77b) |

The credentials the queue counts as held:

- <span class="claim" data-claim="C-DQ-Q-ODA">**ODA / Overfladevandsdatabasen** — an email login, and a scripted SOAP extract in `scripts/oda_client.py`</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-ODA "What this claim rests on")</sup>
- <span class="claim" data-claim="C-DQ-Q-DF">**Dataforsyningen** — an API token, which `scripts/terraincheck.py` reads to fetch the national elevation model</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-DF "What this claim rests on")</sup>

<span class="claim" data-claim="C-DQ-Q-UNCOUNTED">The queue counts only these as held. This project's fetch scripts also read Copernicus Data Space client credentials (`scripts/fetch_satellite.py`) and Copernicus Marine credentials (`scripts/fetch_cmems.py`) from this machine, so the Copernicus entries are counted in tiers that say otherwise: `CDSE-SENTINEL1` `CMEMS-BAL-BGC` `CMEMS-BAL-PHY` `CMEMS-NWS-WAV` as *account*; `CMEMS-BAL-WAV` as *blocked*.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-UNCOUNTED "What this claim rests on")</sup>

<span class="claim" data-claim="C-DQ-Q-ROWS">In each tier below, entries are ordered by how many hypotheses they unlock. *Indexed by* is read from the entry's spatial and aggregation text by keyword: a position, a **region**, both (*mixed*), or `?` where neither matched. *What it is* is the entry's name, shortened where long.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-ROWS "What this claim rests on")</sup>

## Fetch it now — [59](SOURCES.md#F-a7cb1a9012)

<span class="claim" data-claim="C-DQ-Q-OPEN">*The access text reads as open — an open or direct download, a service asking no key or authentication, or an open licence — and names nothing that puts it in another tier.*</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-OPEN "What this claim rests on")</sup>

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **NOVANA-PROG** | [A7](openproblems/A7.md "Sediment nutrient regeneration") [E12](HYPOTHESES.md "Hydrogen sulphide toxicity") [F8](HYPOTHESES.md "Microbial shift to fast-growing forms") [G4](HYPOTHESES.md "Acidification") [H2](HYPOTHESES.md "Sediment legacy") [I4](HYPOTHESES.md "Changing indicator definition") | ? | NOVANA programme description 2023-2027 |
| **AL561-KATTEGAT-SKAGERRAK** | [A7](openproblems/A7.md "Sediment nutrient regeneration") [R5](HYPOTHESES.md "The terminal electron acceptor cascade, and why salt changes it") [R6](openproblems/R6.md "Sulphide locks the iron that would hold the phosphate") [R7](HYPOTHESES.md "Estuarine flocculation deposits river carbon at the coast") [T7](HYPOTHESES.md "Anaerobic phytotoxins other than sulphide") | ? | ALKOR AL561 (APOC) - Kattegat to Skagerrak particulate and porewater geochemistry with i |
| **GBIF** | [F10](HYPOTHESES.md "Vertebrate mass mortality") [F5](HYPOTHESES.md "Invasive species") [F6](HYPOTHESES.md "Jellyfish blooms") [F7](HYPOTHESES.md "Harmful algal blooms specifically") [F9](HYPOTHESES.md "Disease and parasite mass mortality") | position | GBIF occurrence API (dominated by the Danish national portal Arter.dk) |
| **SR634** | [E10](HYPOTHESES.md "Heavy metals") [E6](HYPOTHESES.md "Biocides and antifoulants") [E7](openproblems/E7.md "Pesticides and degradation products") [E8](HYPOTHESES.md "Pharmaceuticals and personal care products") [E9](HYPOTHESES.md "PFAS and persistent novo-chemicals") | ? | DCE Scientific Report `634` - Miljoefarlige forurenende stoffer 2023 |
| **DCE-ILTSVIND** | [B8](HYPOTHESES.md "Direct manure and slurry entry") [C4](hypodrafts/C4.md "Baltic inflow events") [F9](HYPOTHESES.md "Disease and parasite mass mortality") [O1](HYPOTHESES.md "Oxygen deficit") | position | DCE/NOVANA iltsvind (oxygen deficit) bulletin series |
| **DMI-METOBS** | [B1](hypodrafts/B1.md "Combined sewer overflow") [D7](hypodrafts/D7.md "Storm-driven resuspension") [G2](HYPOTHESES.md "Changing precipitation and runoff timing") [G3](HYPOTHESES.md "Changing wind climatology") | position | DMI Open Data - metObs and climateData |
| **DMI-OCEANOBS** | [C4](hypodrafts/C4.md "Baltic inflow events") [C9](HYPOTHESES.md "Sea level and tidal change") [D7](hypodrafts/D7.md "Storm-driven resuspension") [G6](HYPOTHESES.md "Sea level rise") | position | DMI Open Data - oceanObs (sea level) |
| **EMODNET-SEABED-HABITATS** | [D10](HYPOTHESES.md "Winnowing and armouring") [K12](HYPOTHESES.md "Loss of habitat-forming structure") [L5](HYPOTHESES.md "The reference sites are not references") [L6](HYPOTHESES.md "The degraded bed is classified as its own habitat type") | mixed | EMODnet Seabed Habitats - EUSeaMap/HELCOM HUB modelled habitat map, and the ground-truth |
| **GEUS-HAVBUNDSSEDIMENT** | [D10](HYPOTHESES.md "Winnowing and armouring") [L6](HYPOTHESES.md "The degraded bed is classified as its own habitat type") [R7](HYPOTHESES.md "Estuarine flocculation deposits river carbon at the coast") [S5](HYPOTHESES.md "Buffering scales with the volume of reactive medium") | position | Havbundssedimentkort - seabed surface sediment map of Danish waters |
| **HORSENS-EELGRASS-TRANSPLANT** | [F3](hypodrafts/F3.md "Loss of eelgrass and macroalgae") [K12](HYPOTHESES.md "Loss of habitat-forming structure") [L4](HYPOTHESES.md "Recovery is blocked by something other than the driver") [T4](HYPOTHESES.md "Marine replant failure: negative sediment feedback") | position | Bisholt, outer Horsens Fjord - large-scale eelgrass transplant with bare-bottom and natu |
| **ICES-CONTAM-BIOTA-OBIS** | [E10](HYPOTHESES.md "Heavy metals") [E6](HYPOTHESES.md "Biocides and antifoulants") [K8](HYPOTHESES.md "The narrow window between deficient and toxic") [K9](HYPOTHESES.md "Selenium") | position | ICES DOME contaminants and biological effects in biota, Danish subset, through OBIS and  |
| **ICES-DATRAS** | [F1](HYPOTHESES.md "Loss of filter feeders") [F4](HYPOTHESES.md "Trophic cascade from a removal far away") [F5](HYPOTHESES.md "Invasive species") [O3](HYPOTHESES.md "Loss of higher benthic life") | position | ICES DATRAS - trawl survey database |
| **ICES-OCEAN** | [A5](HYPOTHESES.md "Advected nutrients from outside Denmark") [C1](hypodrafts/C1.md "Stratification strength") [C4](hypodrafts/C4.md "Baltic inflow events") [C6](hypodrafts/C6.md "Water temperature and solubility") | position | ICES Oceanographic Database |
| **ICES-PHYTO-OBIS** | [A9](HYPOTHESES.md "Nitrogen fixation") [F7](HYPOTHESES.md "Harmful algal blooms specifically") [K1](hypodrafts/K1.md "Silicon depletion and the diatom-to-flagellate shift") [K2](HYPOTHESES.md "Stoichiometric imbalance decides who grows") | position | ICES Phytoplankton Community dataset, Danish subset, reachable through OBIS |
| **ICES-ZOOBENTHOS-OBIS** | [D11](HYPOTHESES.md "Stabilisers against destabilisers") [D9](HYPOTHESES.md "Fertility islands lost to homogenisation") [K10](HYPOTHESES.md "Salinity change and osmotic cost") [K14](HYPOTHESES.md "Genetic and functional diversity depletion") | position | ICES Zoobenthos Community dataset, Danish subset, through OBIS |
| **MILJOEGIS-RBU-SAML** | [A4](HYPOTHESES.md "Point-source discharge of nutrients") [B1](hypodrafts/B1.md "Combined sewer overflow") [B2](HYPOTHESES.md "Separate stormwater") [B3](HYPOTHESES.md "Treatment plant organic load") | position | MiljoeGIS VP3/VP4 rain-conditioned outfall layers with discharge fields (*_punkt_rbu_sam |
| **OBIS** | [F5](HYPOTHESES.md "Invasive species") [F6](HYPOTHESES.md "Jellyfish blooms") [F7](HYPOTHESES.md "Harmful algal blooms specifically") [O3](HYPOTHESES.md "Loss of higher benthic life") | position | OBIS occurrence API |
| **PUNKTKILDER-RAPPORT** | [A4](HYPOTHESES.md "Point-source discharge of nutrients") [B3](HYPOTHESES.md "Treatment plant organic load") [B5](HYPOTHESES.md "Industrial organic discharge") [E5](HYPOTHESES.md "Direct chemical oxygen demand of discharges") | mixed | Punktkilderapporten (annual Danish point-source report), Bilag `1` and `2` |
| **ASMALA-ROSKILDE-DOC** | [J7](HYPOTHESES.md "Exudate from senescing blooms") [R1](HYPOTHESES.md "The C:N threshold, and fat as a nitrogen sink") [R7](HYPOTHESES.md "Estuarine flocculation deposits river carbon at the coast") | ? | Roskilde Fjord water-column DOC, TOC, nutrients, chlorophyll and DOM optics, 2014-2015 |
| **BORNHOLM-SEDEX** | [H2](HYPOTHESES.md "Sediment legacy") [R6](openproblems/R6.md "Sulphide locks the iron that would hold the phosphate") [S4](HYPOTHESES.md "Total is not available") | **region** | IODP `347-M0065` Bornholm Basin - sequential phosphorus extraction (SEDEX) |
| **DCE-TA-M06-LYS** | [K11](HYPOTHESES.md "Light as a depleted resource") [L3](hypodrafts/L3.md "The trend depends on the start year") [O4](HYPOTHESES.md "Turbidity and phytoplankton biomass") | ? | NOVANA technical instruction M06 - Lyssvaekkelse: how Kd and Secchi are actually measure |
| **DCE-TA-M12-M18-GAP** | [F3](hypodrafts/F3.md "Loss of eelgrass and macroalgae") [K3](HYPOTHESES.md "Macronutrient excess inducing micronutrient deficiency") [T1](HYPOTHESES.md "Sulphide intrusion, gated by light") | ? | NOVANA technical instructions M18 (eelgrass) and M12 (macroalgae) - what the vegetation  |
| **DDM** | [C3](HYPOTHESES.md "Residence time") [C7](HYPOTHESES.md "Bathymetry, sills and depth") [D7](hypodrafts/D7.md "Storm-driven resuspension") | position | Danmarks Dybdemodel (Danish Depth Model) v2.0 |
| **EU-IED-TOC** | [B3](HYPOTHESES.md "Treatment plant organic load") [B5](HYPOTHESES.md "Industrial organic discharge") [R1](HYPOTHESES.md "The C:N threshold, and fat as a nitrogen sink") | **region** | EU Industrial Emissions / E-PRTR reporting - Total Organic Carbon to water, and the abse |
| **FOSSING-METROL-AARHUS** | [E12](HYPOTHESES.md "Hydrogen sulphide toxicity") [R5](HYPOTHESES.md "The terminal electron acceptor cascade, and why salt changes it") [T7](HYPOTHESES.md "Anaerobic phytotoxins other than sulphide") | ? | METROL Aarhus Bay cores - porewater sulphate, methane, hydrogen sulphide, TOC and TN by  |
| **GEUS-MARTA** | [D4](HYPOTHESES.md "Sand and gravel extraction") [K12](HYPOTHESES.md "Loss of habitat-forming structure") [L6](HYPOTHESES.md "The degraded bed is classified as its own habitat type") | position | GEUS Marta - marine raw material database (sand, gravel, stone) |
| **IOW-MBI** | [A5](HYPOTHESES.md "Advected nutrients from outside Denmark") [C1](hypodrafts/C1.md "Stratification strength") [C4](hypodrafts/C4.md "Baltic inflow events") | position | Major Baltic Inflow statistics (Mohrholz) |
| **ODENSE-FJORD-CN** | [A9](HYPOTHESES.md "Nitrogen fixation") [D8](HYPOTHESES.md "Loss of biostabilisation, and the mobile bed") [R1](HYPOTHESES.md "The C:N threshold, and fat as a nitrogen sink") | ? | Sediment resuspension and pelagic nitrogen fixation, Odense Fjord - core incubations wit |
| **PANGAEA-AARHUS-ORGANICACIDS** | [R2](HYPOTHESES.md "Priming of the old sediment pool by fresh carbon") [R5](HYPOTHESES.md "The terminal electron acceptor cascade, and why salt changes it") [T7](HYPOTHESES.md "Anaerobic phytotoxins other than sulphide") | position | PANGAEA - Aarhus Bay porewater organic acids, sulphate, methane and sulphate reduction r |
| **BOKNIS-ECK-SML** | [J1](openproblems/J1.md "Transparent exopolymer particles and marine gel") [J2](HYPOTHESES.md "Sea-surface microlayer enrichment") | ? | Seasonal variation of the sea-surface microlayer at Boknis Eck, Kiel Bight |
| **`EU-INTERCAL-2013-480`** | [I4](HYPOTHESES.md "Changing indicator definition") [L2](HYPOTHESES.md "The reference is a model output treated as a fact") | ? | Commission Decision 2013/480/EU - WFD intercalibration, Baltic GIG coastal types |
| **GEUS-NRETENTION** | [S1](HYPOTHESES.md "Retention is a property of the medium and varies by an order of magnitude") [S6](HYPOTHESES.md "Retention capacity is saturable, so the coefficient is not constant") | mixed | National nitrogen retention maps for Denmark, version 2026 |
| **HELCOM-DEPOSITION** | [A3](HYPOTHESES.md "Atmospheric deposition on the sea surface") [A5](HYPOTHESES.md "Advected nutrients from outside Denmark") | **region** | HELCOM atmospheric nitrogen deposition to the Baltic Sea 1990-2023 |
| **LABYRINTHULA-DK** | [T3](HYPOTHESES.md "Wasting disease with stress-modulated virulence") [T8](HYPOTHESES.md "Anaerobic conditions select the pathogens") | position | Labyrinthula in Denmark - one qPCR site and fifteen metabarcoding hits |
| **LFST-LANDINGS** | [F1](HYPOTHESES.md "Loss of filter feeders") [F4](HYPOTHESES.md "Trophic cascade from a removal far away") | **region** | Landbrugs- og Fiskeristyrelsen landings statistics |
| **MST-KLAP** | [D2](HYPOTHESES.md "Navigation dredging") [D3](HYPOTHESES.md "Dredged-material dumping") | ? | Miljoestyrelsen klaptilladelser (dumping permits), individual PDFs |
| **PSMSL** | [C9](HYPOTHESES.md "Sea level and tidal change") [G6](HYPOTHESES.md "Sea level rise") | ? | PSMSL Revised Local Reference monthly means |
| **SPILDEVANDSDATA** | [B1](hypodrafts/B1.md "Combined sewer overflow") [B2](HYPOTHESES.md "Separate stormwater") | position | spildevandsdata.dk - a PULS extract of overflow and stormwater outfalls |
| **DCE-DEPOSITION** | [A3](HYPOTHESES.md "Atmospheric deposition on the sea surface") | mixed | DCE 'Atmosfaerisk deposition' NOVANA reports (DEHM model) |
| **DMI-RADIA-GLOB** | [K11](HYPOTHESES.md "Light as a depleted resource") | ? | DMI Open Data metObs - global radiation (radia_glob) |
| **DST-AKV11** | [A8](HYPOTHESES.md "Marine aquaculture") | **region** | Danmarks Statistik AKV11 - aquaculture |
| **DST-RST01** | [D4](HYPOTHESES.md "Sand and gravel extraction") | **region** | Danmarks Statistik RST01/RST04 raw-material extraction |
| **DTU-MUSLING** | [F1](HYPOTHESES.md "Loss of filter feeders") | ? | DTU Aqua blue mussel stock assessments, Limfjorden |
| **ENS-STAMDATA** | [C8](HYPOTHESES.md "Constructed change to circulation") | position | Energistyrelsen Stamdataregister for vindmoeller |
| **GEUS-JORDART200K** | [S1](HYPOTHESES.md "Retention is a property of the medium and varies by an order of magnitude") | **region** | Jordartskort over Danmark `1:200.000` |
| **GEUS-JORDART25K** | [S1](HYPOTHESES.md "Retention is a property of the medium and varies by an order of magnitude") | mixed | Danmarks Digitale Jordartskort `1:25.000` (v7.1) |
| **GEUS-KVARTAERTYKKELSE** | [S5](HYPOTHESES.md "Buffering scales with the volume of reactive medium") | position | Kvartaerets tykkelse i Danmark (Quaternary thickness) |
| **HALOPHYTOPHTHORA-LIMFJORD** | [T8](HYPOTHESES.md "Anaerobic conditions select the pathogens") | position | Marine oomycetes isolated from Zostera marina, including Limfjorden |
| **HEREON-UVFILTERS** | [J4](HYPOTHESES.md "Sunscreen and UV filters") | position | Organic UV stabilisers and UV filters in North Sea and Baltic sediment, 2015-2017 |
| **ICES-CATCH** | [F4](HYPOTHESES.md "Trophic cascade from a removal far away") | **region** | ICES Official Nominal Catch Statistics |
| **K7-CARBONATE-CONTEXT** | [K7](HYPOTHESES.md "Carbonate ion depletion") | ? | The carbonate-system context around Denmark - no Danish station, neighbours' lines only |
| **MARIS** | [D4](HYPOTHESES.md "Sand and gravel extraction") | mixed | MARIS raw-material extraction API |
| **METHANE-LIT** | [E4](HYPOTHESES.md "Methane oxidation") | ? | Kattegat methane seeps (boblerev) - the literature |
| **MST-RAASTOF-PDF** | [D4](HYPOTHESES.md "Sand and gravel extraction") | ? | Miljoestyrelsen extraction volumes for faellesomraader (shared sand/gravel licence areas |
| **OBIS-GBIF-LUCINIDER** | [T2](HYPOTHESES.md "Loss of the sulphide-detoxifying symbiosis") | position | OBIS and GBIF occurrence counts for the sulphide-oxidising bivalves in Danish waters |
| **PANGAEA-BENTHIC-FLUX** | [A7](openproblems/A7.md "Sediment nutrient regeneration") | position | PANGAEA - in-situ benthic chamber nutrient flux (BIGO lander) |
| **PANGAEA-CORES** | [H2](HYPOTHESES.md "Sediment legacy") | position | PANGAEA - dated sediment cores, Skagerrak/Kattegat |
| **SGD-LIT** | [A6](HYPOTHESES.md "Submarine groundwater discharge") | position | Danish submarine groundwater discharge - the two campaigns that exist |
| **WFD-DEFINITIONS** | [I4](HYPOTHESES.md "Changing indicator definition") | ? | EU WFD intercalibration decisions and Danish miljoemaal bekendtgoerelser, with adoption  |

## Gated, but we hold the key — [22](SOURCES.md#F-46c5c33c27)

<span class="claim" data-claim="C-DQ-Q-HELD">*An ODA topic, or a service behind the Dataforsyningen token: behind a credential this project holds. Some are already on disk: the ODA extracts `kemi`, `ctd`, `lys` and `maaledybde`.*</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-HELD "What this claim rests on")</sup>

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **ODA-CTD** | [C2](HYPOTHESES.md "Wind work") [G1](hypodrafts/G1.md "Warming") [H1](HYPOTHESES.md "Alternative stable states and hysteresis") [H3](HYPOTHESES.md "Loss of resilience through diversity loss") [I1](hypodrafts/I1.md "Changing station network") [I2](HYPOTHESES.md "Changing analytical method") [I3](hypodrafts/I3.md "Changing sampling frequency and season") [I5](HYPOTHESES.md "Changing correction factors") [I6](HYPOTHESES.md "Changing custodian") | position | ODA - Hav / Feltmaaling / CTD |
| **ODA-BUNDFAUNA** | [D1](hypodrafts/D1.md "Bottom trawling") [F2](HYPOTHESES.md "Loss of bioturbators") [H3](HYPOTHESES.md "Loss of resilience through diversity loss") [I1](hypodrafts/I1.md "Changing station network") [I3](hypodrafts/I3.md "Changing sampling frequency and season") | position | ODA - Hav / Bundfauna / Artsliste + Sediment |
| **ODA-VANDKEMI-HAV** | [A1](hypodrafts/A1.md "Danish land-based nitrogen load") [A2](HYPOTHESES.md "Phosphorus load") [E11](HYPOTHESES.md "Ammonia toxicity") [E2](HYPOTHESES.md "Nitrification demand") [I5](HYPOTHESES.md "Changing correction factors") | position | ODA - Hav / Vandkemi / Naeringsstof og Miljoefarligt stof |
| **ODA-STOFTRANSPORT** | [A1](hypodrafts/A1.md "Danish land-based nitrogen load") [A2](HYPOTHESES.md "Phosphorus load") [B4](HYPOTHESES.md "Riverine particulate organic carbon") [C5](HYPOTHESES.md "Freshwater discharge buoyancy") | position | ODA - Vandloeb / Stoftransport / Maanedstransport |
| **ODA-TILFOERSEL** | [A1](hypodrafts/A1.md "Danish land-based nitrogen load") [A2](HYPOTHESES.md "Phosphorus load") [C5](HYPOTHESES.md "Freshwater discharge buoyancy") [H4](HYPOTHESES.md "Subsidy-stress") | **region** | ODA - Naeringsstoftilfoersel til havet (nutrient input to the sea) |
| **ODA-MARINE-NEGATIVES** | [J3](HYPOTHESES.md "Surfactants from detergents and personal care") [K5](HYPOTHESES.md "Cobalamin (B12) and cobalt limitation") [K6](HYPOTHESES.md "Iron bioavailability") | ? | The complete ODA marine parameter space - what is provably not in it |
| **ODA-AFFALD-PLASTIK** | [J5](HYPOTHESES.md "Microplastic and its biofilm") | position | ODA - Hav / Marint affald and Plastik i biota (schema present, no data exposed) |
| **ODA-BUNDFAUNA-SEDIMENT** | [R3](HYPOTHESES.md "The decay relay stalls when a stage is removed") | position | ODA - Hav / Bundfauna / Sediment (grain size and sediment character at the fauna station |
| **ODA-STATION-COUNTS-CORRECTION** | [R3](HYPOTHESES.md "The decay relay stalls when a stage is removed") | ? | ODA station counts are period-dependent - the numbers in data_sources.json are the wrong |
| **ODA-VEGETATION** | [H1](HYPOTHESES.md "Alternative stable states and hysteresis") | position | ODA - Hav / Vegetation (aalegraes bundfauna / makroalge / plante) |
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

## One free registration away — [30](SOURCES.md#F-542c824a5b)

<span class="claim" data-claim="C-DQ-Q-ACCOUNT">*The access text names a registration, an account, a login or a token that the queue does not count as held.*</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-ACCOUNT "What this claim rests on")</sup>

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **DMA-AIS** | [B7](HYPOTHESES.md "Shipping discharges") [D6](HYPOTHESES.md "Anchoring and propeller wash") | position | Danish Maritime Authority raw AIS archive |
| **EMODNET-VESSELDENSITY** | [B7](HYPOTHESES.md "Shipping discharges") [D6](HYPOTHESES.md "Anchoring and propeller wash") | position | EMODnet Human Activities vessel density |
| **`ENA-DK-COASTAL-16S`** | [J8](HYPOTHESES.md "Bacterial exopolymer from fast-growing communities") [T5](HYPOTHESES.md "Loss of sediment suppressiveness") | position | Danish coastal-water microbial sequence data in ENA |
| **ENA-MGNIFY-DK-SEDIMENT** | [T5](HYPOTHESES.md "Loss of sediment suppressiveness") [T6](HYPOTHESES.md "Enrichment dissolving the partnership") | position | Danish marine sediment microbial sequence data in ENA and MGnify |
| **GFW** | [B7](HYPOTHESES.md "Shipping discharges") [D6](HYPOTHESES.md "Anchoring and propeller wash") | position | Global Fishing Watch apparent fishing effort v3.0 |
| **PANGAEA-POREWATER** | [E1](HYPOTHESES.md "Sulphide oxidation") [E3](HYPOTHESES.md "Iron and manganese oxidation") | position | PANGAEA - sediment porewater chemistry, Danish and adjacent waters |
| **CDSE-SENTINEL1** | [J6](HYPOTHESES.md "Oil and hydrocarbon films") | **region** | `Sentinel-1` GRD SAR over Danish waters, Copernicus Data Space Ecosystem |
| **CMEMS-NWS-WAV** | [O2](HYPOTHESES.md "Fedtemøg") | ? | Copernicus Marine North-West Shelf Wave Reanalysis |
| **EMODNET-SEABED-USE** | [D5](HYPOTHESES.md "Cable and pipeline works") | mixed | EMODnet Human Activities seabed-use layers |
| **ICE** | [G5](HYPOTHESES.md "Changing ice cover") | mixed | Sea ice for Danish waters - no single confirmed source |
| **ICES-VMS-SAR** | [D6](HYPOTHESES.md "Anchoring and propeller wash") | **region** | ICES WGSFD VMS/logbook swept-area-ratio product |
| **LOOP** | [S2](HYPOTHESES.md "Phosphorus saturation, and legacy leakage") | mixed | LOOP - Landovervaagningsoplandene (agricultural catchment monitoring with root-zone and  |
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

## Not open — [37](SOURCES.md#F-d3261ec77b)

<span class="claim" data-claim="C-DQ-Q-BLOCKED">*The access text says not public, request-only, FOI, provisioned, unverified or without a download — or matches no tier word at all. Entries recording data confirmed not to exist are here too.*</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-BLOCKED "What this claim rests on")</sup> <span class="claim" data-claim="C-DQ-Q-PULSCLOSED">`PULS` is one whose data exists and is closed: the register records it as not public, reached through an organisation's IT coordinator.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-PULSCLOSED "What this claim rests on")</sup>

| source | unlocks | indexed by | what it is |
|---|---|---|---|
| **R2-R4-R8-R9-R10-GAP** | [R10](HYPOTHESES.md "Osmotic discontinuity for the decomposers themselves") [R4](HYPOTHESES.md "Nitrogen enrichment retards decay of the recalcitrant fraction") [R8](HYPOTHESES.md "Lipids are less soluble in seawater") [R9](HYPOTHESES.md "Home-field advantage, and novel material") | ? | Five decomposition experiments that have never been run in Danish water |
| **BADEVAND** | [B6](HYPOTHESES.md "Harbour and fish-processing waste") | position | Bathing water quality portal |
| **K4-M74-GAP** | [K4](HYPOTHESES.md "Thiamine (B1) deficiency") | ? | Thiamine deficiency and M74 - no Danish assay, and the Swedish series not opened |
| **K5-K6-K13-GAP** | [K13](HYPOTHESES.md "Food depletion for filter feeders and larvae") | ? | Cobalamin, iron speciation and particle size spectra in Danish waters - none found |
| **L1-GAP** | [L1](HYPOTHESES.md "The reference condition never existed") | ? | Dated diatom or pigment stratigraphy from Danish coastal sediment - confirmed absent fro |
| **S1-PAPERS** | [S3](HYPOTHESES.md "Sorption is hysteretic - a ratchet on the land side too") | ? | The Danish soil-and-sediment process papers that stand in for the missing datasets |
| **S2-GAP** | [S3](HYPOTHESES.md "Sorption is hysteretic - a ratchet on the land side too") | ? | Danish soil phosphorus status by area - confirmed absent as open data |
| **B8-GAP** | — | ? | Danish environmental incident / spill / fish-kill registers - confirmed absent in open f |
| **BIOTIC-MARLIN** | — | ? | BIOTIC - Biological Traits Information Catalogue |
| **CMEMS-BAL-WAV** | — | ? | Copernicus Marine Baltic Sea Wave Reanalysis |
| **D2-GAP** | — | ? | Danish navigation dredging permits - no working public register |
| **DAI-KYSTVANDOPLANDE** | — | **region** | Danmarks Arealinformation - kystvandoplande and deloplande, the catchment units nitrogen |
| **DANISH-PORTALS-BLOCKED** | — | ? | Danish research-portal infrastructure is closed to automated retrieval |
| **DK-DRAENKORT-AU** | — | position | Kortlaegning af draenede arealer i Danmark - national map of potentially drained agricul |
| **DK-DRAENUDLOEB** | — | ? | Draenudloeb and drain pipe networks - the outfalls themselves |
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

<span class="claim" data-claim="C-DQ-Q-RULE">The rule: a source is carried at the resolution it was taken — a position, a time, and where it exists a depth — and not at an administrative unit such as a water body, a catchment, a municipality or a sub-basin. This page flags each source by what it is indexed by; it does not enforce the rule.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-RULE "What this claim rests on")</sup>

<span class="claim" data-claim="C-DQ-Q-WHY">The reason is in [OBSERVING.md](OBSERVING.md): in bathing-water quality at stations with a long record, once the national year-to-year swing is removed, variation between water bodies is **[7.9](SOURCES.md#F-8f0c3bce24)%** of the whole, and between two stations in the same water body [4.1](SOURCES.md#F-7dc131660c)% of the wobble in one is shared with the other. A source already summed into those polygons would carry the unit back in, and everything computed from it would inherit it.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-WHY "What this claim rests on")</sup>

<span class="claim" data-claim="C-DQ-Q-INDEX">Counted by that keyword reading of each entry's spatial and aggregation text; `?` means the text matched no keyword, not that the source has no index.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-INDEX "What this claim rests on")</sup>

| indexed by | sources |
|---|---:|
| position | [69](SOURCES.md#F-5a6aa3c0d7) |
| **region** | [16](SOURCES.md#F-d7cb543694) |
| mixed | [12](SOURCES.md#F-92d73d1d05) |
| ? | [51](SOURCES.md#F-f2bd84c6b8) |

<span class="claim" data-claim="C-DQ-Q-TILF">A region-indexed source can still be the one to fetch: the monthly nutrient input to the sea, `ODA-TILFOERSEL`, is given per marine reference polygon, and the register records the stream stations behind it as available separately, in `ODA-STOFTRANSPORT`.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-TILF "What this claim rests on")</sup> <span class="claim" data-claim="C-DQ-Q-AGG">Under the rule such a source is used as somebody's aggregate of a measurement, never as the measurement.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-AGG "What this claim rests on")</sup>

> <span class="claim" data-claim="C-DQ-Q-WB">**What a water body actually is, if it is anything, is a question to be answered from the data rather than assumed by the schema.** Put the observations on the map with their own coordinates and times, see which move together, and check every proxy against an unrelated one. The administrative polygon is then an overlay to be tested against — not a container to pour things into.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-WB "What this claim rests on")</sup>

## What this does not tell you

<span class="claim" data-claim="C-DQ-Q-VALUE">Friction is not value. The tiers say what is easy to reach, and each register entry's hypotheses say what it would serve; they are different questions, and this page answers only the first.</span><sup class="claim-mark">[†](CLAIMS.md#C-DQ-Q-VALUE "What this claim rests on")</sup>

