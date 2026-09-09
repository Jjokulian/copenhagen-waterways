# Triage of the hypothesis field

PLAN.md stage 4 says the triage is "most of the work" and that stage 5 is meaningless
until it exists. This is it: **all 166 lettered hypotheses in [HYPOTHESES.md](../HYPOTHESES.md)**,
each in exactly one class, with the specific blocker.

Nineteen already have a draft or an open-problem entry; those are marked and cite it rather
than being redone. **Nothing here has been run.** A classification is a claim about what
could be done, not a result.

| class | n | share |
|---|---:|---:|
| **testable now** | 24 | 14% |
| blocked on a fetch | 61 | 37% |
| blocked on resolution | 18 | 11% |
| **unscoreable** | 40 | 24% |
| needs an experiment | 20 | 12% |
| not established | 3 | 2% |
| | **166** | |

**Class definitions.** *Testable now* — consequence, a source in hand, and a null computable
under the constraint imposed. *Blocked on a fetch* — named, with whether it needs credentials.
*Blocked on resolution* — needs depth, sub-monthly time, per-measurement position, or the
measurement-level store. *Unscoreable* — the deciding dimension has no column and never did;
**this is not a refutation**. *Needs an experiment* — no observational design reaches it.
*Not established* — I could not tell, and say so rather than guess.

---

## The table

### A. Nutrient-driven production in place

*10 hypotheses — 8 blocked on a fetch, 1 unscoreable, 1 not established.*

| id | consequence | class | blocker |
|---|---|---|---|
| **A1** | Load up -> summer chlorophyll up -> bottom O2 down, per area per month | blocked on a fetch | ODA vandkemi `Emne_10_11` (N, P, chlorophyll) — ODA login. Land load additionally needs `STOFTRANSPORT`/`TILFOERSEL`, which require a **code change**: `run()` hardcodes the Hav endpoint |
| **A2** | P flux up -> spring chlorophyll up | blocked on a fetch | same vandkemi fetch |
| **A3** | Deposition over sea up -> production up where land load is low | blocked on a fetch | DEHM marine-grid deposition, monthly, incl. the organic-N fraction that is generally not reported |
| **A10** | Urea-derived N from exhaust treatment enters the budget it abates | not established | A mass-balance argument, not an observable here. Whether any reaches the sea is not established |
| **A4** | Plant discharge down at upgrade date -> local N down stepwise | blocked on a fetch | per-plant monthly N/P/COD with upgrade dates. `punkt_rens_udl.geojson` gives locations only |
| **A5** | Nutrients at Belt/Sound sections co-vary with inner-water state | blocked on a fetch | vandkemi at section stations. CMEMS Baltic indicators are held but carry no nutrients |
| **A6** | SGD delivers N where no stream does | **unscoreable** | **Submarine groundwater discharge is not a term in the national account.** No Danish SGD survey exists at all |
| **A7** | Bottom-water DIP rises in summer without a matching river input | blocked on a fetch | vandkemi `Emne_10_11` (ortho-P, 1,125 stations) + sedimentkemi `Emne_12_19` (39 stations). `openproblems/A7.md`: armchair for the weak form, measurement for the strong |
| **A8** | Sediment near pens enriched vs matched controls | blocked on a fetch | per-farm production and feed by month. `punkt_havdam_udl.geojson` gives farm locations only |
| **A9** | Cyanobacteria abundance up where N:P is low | blocked on a fetch | phytoplankton counts — OBIS eMoF carries 103,005 Danish abundance records, open REST, **no credentials** (`hypodrafts/K1.md`) |

### B. Oxygen demand that arrived already made

*8 hypotheses — 1 testable now, 4 blocked on a fetch, 1 blocked on resolution, 2 unscoreable.*

| id | consequence | class | blocker |
|---|---|---|---|
| **B1** | Bathing indicator up downstream of combined outfalls after rain, not separate ones | **testable now** | **Draft exists** (`hypodrafts/B1.md`). Uses combined-vs-separate class and an a priori critical rainfall depth, never modelled volume. Its EEA WISE claim is unverified |
| **B2** | First-flush concentration x volume exceeds the annual-total assumption | blocked on resolution | event-resolved concentration and volume at the outfall. Annual totals over 16,185 outfalls cannot test a first-flush claim |
| **B3** | Plant COD/BOD up -> local oxygen demand up | blocked on a fetch | per-plant monthly COD/BOD |
| **B4** | Riverine POC up -> sediment organic content up at the receiving coast | blocked on a fetch | suspended solids and organic carbon at stream stations (vandkemi / stoftransport) |
| **B5** | Industrial organic load co-locates with local demand | blocked on a fetch | industrial discharge permits and reported loads per site per year |
| **B6** | Harbour water shows a demand signature the open coast does not | **unscoreable** | **Harbour water quality measurements are largely absent.** No column anywhere held |
| **B7** | Scrubber and bilge discharge along tracks -> local demand | blocked on a fetch | AIS tracks are obtainable; **discharge volumes essentially do not exist**, so the second half is unscoreable |
| **B8** | Incident-linked slurry entry -> local spike | **unscoreable** | **No public environmental incident register with date and location** |

### C. Physical control of resupply

*9 hypotheses — 5 testable now, 2 blocked on a fetch, 2 blocked on resolution.*

| id | consequence | class | blocker |
|---|---|---|---|
| **C1** | Hypoxia is near-zero in well-mixed water at matched depth | **testable now** | **Draft exists** (`hypodrafts/C1.md`). 133,501 station-days with 4+ depth levels of T and S plus bottom oxygen, from the raw CTD |
| **C2** | Wind work up -> stratification broken -> bottom O2 up | **testable now** | hourly wind held (`data/raw/weather/`, 31 yr) joined to CTD profiles |
| **C3** | Long residence time -> lower O2 at matched load | blocked on resolution | per-area residence time held only coarsely — the 9 km field is ~2x too slow in the straits by its own calibration |
| **C4** | Inflow -> deep O2 pulse, lagged, ordered Belts->Arkona->Bornholm->Gotland | **testable now** | **Draft exists** (`hypodrafts/C4.md`). MBI indicator and Gotland profiles held; the published inflow record is not, so a wind-derived instrument substitutes |
| **C5** | Freshwater pulse -> stratification up -> bottom O2 down | blocked on a fetch | daily freshwater discharge per catchment |
| **C6** | Deficit vs saturation separates solubility from consumption | **testable now** | **Draft exists** (`hypodrafts/C6.md`). 76,305 station-months carrying O2, T and S near-bed |
| **C7** | Deeper and silled areas go hypoxic at lower load | **testable now** | bottom depth per visit in `maaledybde` (151,203 rows); sill geometry from `marin_overordnet.geojson` |
| **C8** | Construction changed exchange -> step in local state at the works date | blocked on resolution | construction chronology partial; needs works dates and footprints joined to sub-monthly state |
| **C9** | Sea level and tidal change alter exchange | blocked on a fetch | DMI oceanObs tide gauges — 10-minute from 1889, CC BY 4.0, **no API key required since 2026-03-26** |

### D. Physical disturbance of the bed

*11 hypotheses — 1 testable now, 8 blocked on a fetch, 1 unscoreable, 1 needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **D1** | Effort up -> near-bed O2 down, strongest on fine substrate, absent >20 m | blocked on a fetch | ICES/HELCOM swept-area ratio, figshare 20310255 — **23.1 MB, CC BY 4.0, no credentials**. Draft exists (`hypodrafts/D1.md`) |
| **D2** | Dredging event -> local turbidity and demand spike | blocked on a fetch | dredging permits with dates, volumes and locations |
| **D3** | A dumping ground shows a signature its surroundings do not | blocked on a fetch | `klappladser.geojson` gives the grounds. Per-ground volume, date and material chemistry are in MST-KLAP as individual PDFs |
| **D4** | An extraction area differs from matched unextracted seabed | blocked on a fetch | `raastofomr.geojson` gives the areas; per-area extracted volume by year is not held |
| **D5** | Cable route works -> local disturbance signature | blocked on a fetch | route and installation-date registers |
| **D6** | Anchorage seabed differs from matched non-anchorage | blocked on a fetch | AIS anchoring events and anchorage designations |
| **D7** | Transparency deficit lags critical bed shear, only in shallow water | **testable now** | **Draft exists** (`hypodrafts/D7.md`). 96,709 dated Secchi+depth visits, `Turbiditet` 1,076,915 rows, wind held. The monthly panel cannot resolve events, so the draft runs on the dated raw record |
| **D8** | A biostabilised bed resists erosion to higher shear | needs an experiment | **erodibility measurement (cohesive strength meter or flume) with matched surface-sediment chlorophyll.** Standard method, not in Danish monitoring |
| **D9** | Within-area fauna variance collapses under homogenisation | **unscoreable** | **One grab per station by design.** Within-area variance cannot be estimated from a design that samples one point per area |
| **D10** | Grain size coarsens where fines are winnowed | blocked on a fetch | ODA sediment grain size as a time series. `seabed_sediment_dk.gpkg` is a static 108-polygon mosaic from 22 campaigns at 1:5,000-1:500,000 |
| **D11** | Stabiliser:destabiliser ratio predicts bed state | blocked on a fetch | ODA bundfauna `Emne_3_180`, then a desk trait assignment |

### E. Chemical demand and toxicity

*20 hypotheses — 6 blocked on a fetch, 1 blocked on resolution, 11 unscoreable, 1 needs an experiment, 1 not established.*

| id | consequence | class | blocker |
|---|---|---|---|
| **E1** | Sulphide oxidation consumes O2 where redox is low | blocked on a fetch | sedimentkemi `Emne_12_19`; sediment redox and sulphide are rarely measured even there |
| **E2** | Nitrification demand scales with ammonium | blocked on a fetch | **ammonium is NOT in the CTD file.** The Needs line saying 'in the ODA water chemistry' means unfetched — vandkemi `Emne_10_11` |
| **E3** | Fe/Mn oxidation consumes O2 at the redox front | needs an experiment | porewater chemistry, very rare, and the mechanism is millimetre-scale |
| **E4** | Methane oxidation consumes O2 above seeps | **unscoreable** | **Essentially no Danish coastal methane flux record** |
| **E5** | Discharge COD carried into a marine budget changes the balance | blocked on a fetch | per-outlet COD — measured in discharge monitoring and never carried through |
| **E6** | Antifoulant concentration up -> decomposer function down | **unscoreable** | **Sediment measured at 4 of 256 national hazardous-substance points — and all 256 are freshwater** (152 lake, 104 river, 0 marine), verified in this project |
| **E7** | Pesticide load co-varies with N and acts separately | **unscoreable** | **No toxicant column in 53.7M CTD rows, none in 679,422 station-months.** `openproblems/E7.md` classifies it measurement |
| **E8** | Pharmaceutical residues alter microbial function | **unscoreable** | almost no Danish marine pharmaceutical monitoring |
| **E9** | PFAS persists and accumulates in biota | blocked on a fetch | some biota data exists (ICES DOME); sediment barely. A fetch would establish the extent |
| **E10** | Metal concentration up -> benthic function down | blocked on a fetch | ICES DOME holds Danish Fe/S/PTOT — **47 samples at 12 positions, all 1990-91** (`openproblems/R6.md`) |
| **E11** | Un-ionised ammonia is toxic at high pH and temperature | blocked on a fetch | **pH is held (237,496 rows); ammonium is not.** vandkemi fetch |
| **E12** | Free sulphide is toxic to fauna above a threshold | blocked on resolution | `Dihydrogensulfid` is 2,601 rows and **2,598 come from one station** (Mariager, 93610032). Usable for one silled basin, not a series |
| **E13** | Fungicides remove decomposers -> decay stalls | **unscoreable** | **Neither fungicide in sediment nor fungal biomass is measured.** `R11` records that the fungi are not counted anywhere |
| **E14** | Antiparasitic residues in manure reach water and act | **unscoreable** | not routinely measured in Danish soil, runoff or sediment |
| **E15** | Total biocide load, not per-substance, predicts effect | **unscoreable** | **Nothing assembles national sales data into an environmental load by catchment** |
| **E16** | High-tonnage compounds act on conserved targets at realistic dose | **unscoreable** | marine concentrations of the actual high-tonnage compounds are not monitored |
| **E18** | 6PPD-quinone is lethal to salmonids at road-runoff concentrations | **unscoreable** | **6PPD-q is not measured in Danish monitoring.** Danish sea-trout sensitivity is also unestablished |
| **E20** | Fuel oxygenates reach coastal water | not established | groundwater monitoring covers some; whether any is reported for coastal discharge is not established |
| **E19** | Standard test batteries miss locally present sensitive species | **unscoreable** | **No panel of locally present species exists**, so this cannot be checked for any compound |
| **E17** | The microbiome is the exposed organ | **unscoreable** | **No host-associated microbial community data for any Danish marine organism** |

### F. Biological structure and feedback

*14 hypotheses — 6 blocked on a fetch, 1 blocked on resolution, 7 unscoreable.*

| id | consequence | class | blocker |
|---|---|---|---|
| **F1** | Filter-feeder loss -> clearance down -> chlorophyll up | blocked on a fetch | ODA bundfauna `Emne_3_180`; shellfish stock assessments |
| **F2** | Bioturbator loss -> sediment O2 penetration down | blocked on a fetch | ODA bundfauna `Emne_3_180`, species-level abundance and biomass |
| **F3** | Cover falls where light is adequate -> the block is not light | blocked on a fetch | ODA `Emne_3_182` aalegraes, 1,990 stations 1970-2026 — **three one-line TOPICS entries, no extra credentials**. Draft exists (`hypodrafts/F3.md`) |
| **F4** | Distant stock removal -> cascade to local grazing | blocked on a fetch | ICES stock assessments and Danish landings by area and year — **both open, already in the fetch queue** |
| **F5** | Invasive arrival -> function change at the arrival date | blocked on a fetch | species observation records with date and position (OBIS/GBIF, open) |
| **F6** | Jellyfish blooms alter the pathway | **unscoreable** | **Essentially no jellyfish monitoring in Denmark** |
| **F7** | HAB species specifically, not chlorophyll, drive the harm | blocked on a fetch | phytoplankton species counts — collected, and OBIS eMoF carries 103,005 Danish abundance records |
| **F8** | Community shifts to fast-growing forms under enrichment | **unscoreable** | **Microbial community composition is not monitored at all** |
| **F9** | Disease mortality event -> structural loss | **unscoreable** | the marine mortality event register is ad hoc; no systematic column |
| **F10** | Vertebrate mass mortality signals a pathway | blocked on resolution | stranding networks are partial; needs event dates joined to state |
| **F11** | Viral lysis short-circuits the food web | **unscoreable** | **Marine viral counts are not in Danish monitoring at any station** — a standard method since the 1990s |
| **F13** | Organisms between the folk categories go unrecorded | **unscoreable** | **No eDNA survey with an open taxonomic frame.** The categories on the existing forms are the cause |
| **F14** | Viruses are structure, not only mortality | **unscoreable** | **Not measured at any Danish station.** Flagged in-register as the most likely location of the mycorrhizal gap |
| **F12** | Micropathogens of invertebrates are uncatalogued | **unscoreable** | **Denmark has no marine mortality response capability for invertebrates** |

### G. Climate and long-term drivers

*6 hypotheses — 2 testable now, 3 blocked on a fetch, 1 blocked on resolution.*

| id | consequence | class | blocker |
|---|---|---|---|
| **G1** | dO2/dt = dCsat/dt - dD/dt; the deficit widens or it does not | **testable now** | **Draft exists** (`hypodrafts/G1.md`). 76,264 five-way joined station-months; Weiss makes the solubility channel exact rather than estimated |
| **G2** | Runoff timing shifts -> load timing shifts -> state shifts | blocked on a fetch | daily discharge and concentration, not annual sums |
| **G3** | Wind climatology change -> mixing change | **testable now** | hourly wind held, 31 years. The trend null must be matched-autocorrelation, not independence |
| **G4** | Acidification alters carbonate saturation for calcifiers | blocked on resolution | pH is held (237,496 rows) but the **carbonate system needs two of pH / alkalinity / DIC / pCO2**, and only one is held |
| **G5** | Ice cover change alters seasonal mixing | blocked on a fetch | ice records — available, not fetched |
| **G6** | Sea level rise alters exchange and inundation | blocked on a fetch | DMI tide gauges — long, open, not fetched |

### H. State, memory and regime

*4 hypotheses — 3 blocked on a fetch, 1 blocked on resolution.*

| id | consequence | class | blocker |
|---|---|---|---|
| **H1** | State does not retrace the load path — hysteresis | blocked on resolution | needs long paired load-and-state through **both** directions; the load half is unfetched and the reversal may not have occurred |
| **H2** | Sediment legacy sustains demand after load falls | blocked on a fetch | sediment organic content and accumulation rates, and **dated cores** |
| **H3** | Diversity loss -> variance of response up | blocked on a fetch | ODA bundfauna `Emne_3_180`, long species-level series |
| **H4** | Response is non-monotone across the load gradient | blocked on a fetch | the 123 areas supply the gradient; the **load axis is the unfetched half** |

### J. Surface film, gel and the greasy water

*9 hypotheses — 1 blocked on a fetch, 2 blocked on resolution, 5 unscoreable, 1 not established.*

| id | consequence | class | blocker |
|---|---|---|---|
| **J1** | Attenuation residual after chlorophyll, CDOM and particles is gel | **unscoreable** | **TEP is not measured at all**, and `Lysdaempning` is a bare `pct` with **no path length recorded**, so the total has no physical units. `openproblems/J1.md` |
| **J2** | Microlayer enrichment concentrates surfactants and toxicants | **unscoreable** | **No sea-surface microlayer sampling in Danish monitoring** |
| **J3** | Surfactant load -> film -> gas exchange down | **unscoreable** | essentially no marine surfactant measurements |
| **J4** | UV filters accumulate in nearshore water | **unscoreable** | **No marine UV-filter monitoring in Denmark** |
| **J9** | Fragmentation is a source term the inventory omits | not established | the national inventory gives 5,500-13,900 t/yr released and 600-3,100 t/yr to sea; whether fragmentation is separable within it is not established |
| **J5** | Microplastic biofilm alters the microlayer | blocked on resolution | some Danish microplastic data exists; microlayer-specific, none |
| **J6** | Oil films in SAR co-locate with the greasy-water reports | blocked on a fetch | **Sentinel-1 SAR is free and covers the whole period.** The register's own Needs line says this one is testable now — it is a fetch away |
| **J7** | Bloom collapse -> DOC pulse -> film | blocked on resolution | **DOC at sub-monthly resolution.** The sampling frequency is the binding constraint |
| **J8** | Fast-growing communities exude more polymer | **unscoreable** | microbial community data is not monitored |

### K. Depletion and imbalance

*14 hypotheses — 2 testable now, 4 blocked on a fetch, 1 blocked on resolution, 6 unscoreable, 1 needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **K1** | Si:DIN falls -> diatom share falls -> flagellates rise | blocked on a fetch | **silicate is NOT in the CTD file** — vandkemi `Emne_10_11`; phytoplankton via OBIS eMoF. Draft exists (`hypodrafts/K1.md`); the CMEMS DIATO field is a relabelling of CHL and cannot bear it |
| **K2** | N:P:Si ratio, not absolute load, selects the assemblage | blocked on a fetch | same vandkemi fetch plus species counts |
| **K3** | Macronutrient excess induces micronutrient deficiency in tissue | needs an experiment | **tissue elemental analysis of algae and eelgrass is not collected** |
| **K4** | Thiamine deficiency propagates up the food web | **unscoreable** | **No Danish marine thiamine assays.** Swedish and Finnish work exists |
| **K5** | B12 and cobalt limit the auxotrophs | **unscoreable** | **No marine B12 measurements in Denmark** |
| **K6** | Iron bioavailability limits production or detoxification | **unscoreable** | iron speciation is not monitored |
| **K7** | Carbonate ion depletion impairs calcification | blocked on resolution | needs two carbonate-system variables; one is held |
| **K8** | The window between deficient and toxic is narrow and crossed | **unscoreable** | trace elements with matched biological response; sediment metals at four national points |
| **K9** | Selenium status limits or intoxicates | **unscoreable** | selenium in Danish marine biota is not routinely measured |
| **K10** | Salinity change imposes osmotic cost at the range edge | **testable now** | salinity by station, date and depth is in the CTD record — 7,474,645 rows |
| **K11** | Light at the bed = f(Kd, depth), and the product is rarely formed | **testable now** | **Both halves held**: `lys` 2.37M rows and bottom depth in `maaledybde`, 96,708 paired. Carries the Kd start-depth artefact and 21.4% shallow Secchi censoring |
| **K12** | Structure removal -> habitat loss independent of water quality | blocked on a fetch | stone extraction records, reef restoration locations and dates |
| **K13** | Particle spectra shift below the filter-feeder window | **unscoreable** | **Particle size spectra and larval condition indices are not monitored** |
| **K14** | Functional diversity falls before species richness does | blocked on a fetch | ODA bundfauna `Emne_3_180` |

### W. Renewal and rate

*8 hypotheses — 1 testable now, 3 blocked on a fetch, 2 blocked on resolution, 2 needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **W1** | Recovery fails where propagule supply is cut | blocked on resolution | source populations plus particle tracking; the held circulation model is 9 km and ~2x slow in the straits |
| **W2** | Unconditioned substrate fails to recruit | needs an experiment | **settlement plates with and without conditioning.** Cheap, and connects to the sediment-inoculation experiment X1 |
| **W3** | Bloom and larval peak drift apart | blocked on resolution | **sub-monthly plankton series.** The register itself states sampling frequency is the binding constraint, not the parameters |
| **W4** | Below a density threshold reproduction fails | blocked on a fetch | ODA bundfauna carries densities; the analysis is then a desk exercise |
| **W5** | Disturbance interval shorter than recovery time | blocked on a fetch | **trawling effort at monthly or finer.** The ICES/HELCOM layer is quarterly; finer is the closed dataset |
| **W6** | Rate of change exceeds acclimation rate | **testable now** | **high-frequency records exist and are analysed for means rather than rates.** The CTD record supports a rate analysis now |
| **W8** | The founder community determines the endpoint | needs an experiment | composition immediately after disturbance and through recovery at the same place — requires having sampled before |
| **W7** | Too little standing variation is left to respond with | blocked on a fetch | long species-level fauna is in ODA; **genetic data nobody has**, so that half is unscoreable |

### Z. The physical fields and their windows

*11 hypotheses — 3 testable now, 2 blocked on a fetch, 3 blocked on resolution, 2 unscoreable, 1 needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **Z1** | Light at the bed outside the window -> loss | **testable now** | the same product as K11; both halves held |
| **Z2** | Browning shifts the spectrum, not just the quantity | blocked on resolution | **Kd is a single broadband number.** FDOM (890,921 rows, 2021 onward only) is a CDOM proxy on the same cast — five years of in-situ CDOM |
| **Z3** | Photoperiod cue decouples from temperature cue | **unscoreable** | **Effectively no phenological observations for Danish marine invertebrates** |
| **Z4** | Rate of temperature change, not level, exceeds tolerance | blocked on resolution | bottom temperature at high frequency; the monthly product aliases it, the raw record may not |
| **Z5** | Energy has a floor — too still is also a failure | **testable now** | bed shear already computed here from 31 years of wind; the floor is testable against the same state variables |
| **Z6** | Sound masks settlement cues | **unscoreable** | **essentially no noise measurement tied to invertebrate settlement** |
| **Z7** | EMF from cables alters behaviour | blocked on resolution | cable routes and energisation dates are available; **biological response is not measured** |
| **Z8** | The attenuation budget is never partitioned | **testable now** | **Draft exists** (`hypodrafts/Z8.md`). Kd plus chlorophyll, CDOM and particle proxies on the same cast, 9,717 casts with all four — but `Lysdaempning` has no path length, so it is a variance apportionment, not a budget |
| **Z9** | Epiphytes shade the plant regardless of water clarity | blocked on a fetch | epiphyte biomass on eelgrass — in research programmes, not routine monitoring |
| **Z10** | Works plumes exceed natural turbidity long enough to matter | blocked on a fetch | works chronology plus the turbidity monitoring large projects must do and rarely reanalyse |
| **Z11** | A weakened host fails at a stress a healthy one survives | needs an experiment | carbohydrate reserves, tissue sulphide and pathogen load on the same plants |

### T. Sediment sickness

*12 hypotheses — 1 blocked on a fetch, 4 unscoreable, 7 needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **T1** | Sulphide intrudes when light cannot power the defence | needs an experiment | tissue sulphide, porewater sulphide and light at the bed on the same plants; a research method, not monitoring |
| **T2** | Lucinid bivalves absent -> sulphide detoxification lost | blocked on a fetch | **infaunal bivalve records within seagrass beds are in ODA bundfauna if anyone looks** |
| **T3** | Labyrinthula virulence rises with host stress | needs an experiment | Labyrinthula screening in Danish eelgrass; not routine |
| **T4** | Replanting fails on conditioned sediment and succeeds on clean | needs an experiment | **restoration trials with sediment treatments.** A handful of Danish eelgrass trials exist; this design does not |
| **T5** | Suppressive sediment resists invasion; degraded does not | needs an experiment | sediment microbial composition **and transfer experiments** — neither exists |
| **T6** | Enrichment dissolves the partnership by making it unnecessary | needs an experiment | rhizosphere community composition along the gradient |
| **T7** | Anaerobic phytotoxins beyond sulphide | needs an experiment | porewater chemistry beyond the standard nutrients |
| **T8** | Anaerobia selects for the pathogens | **unscoreable** | **essentially no marine oomycete or labyrinthulid surveys** |
| **T9** | Pathogen and partner are not kinds of organism | **unscoreable** | host-associated microbial and viral community data through a stress gradient — **absent for every Danish marine species** |
| **T12** | Defence is outsourced; a biocide disarms the host | **unscoreable** | host-associated community data with matched disease outcomes — absent |
| **T11** | Occupancy is the function; the empty niche is the risk | needs an experiment | **challenge experiments on intact versus disturbed communities.** Standard in medical and soil microbiology, not applied in Danish marine work |
| **T10** | Removing an unknown-role organism is not neutral | **unscoreable** | **baseline composition before intervention is almost never collected**, which makes the comparison impossible by construction |

### S. The land side: the medium

*6 hypotheses — 1 testable now, 3 blocked on a fetch, 1 blocked on resolution, 1 needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **S1** | Retention varies an order of magnitude with the medium | blocked on a fetch | the soil map exists; the paired drainage validation largely does not |
| **S2** | Legacy soil P leaks after inputs stop | blocked on a fetch | **Denmark holds soil P status and it is not carried into the marine argument** — a fetch and a join |
| **S3** | Sorption is hysteretic — a ratchet on the land side too | needs an experiment | sorption-desorption experiments on Danish soils; standard method |
| **S4** | Total P is not available P | blocked on a fetch | fractionated sediment P — sedimentkemi `Emne_12_19` carries Fe-adsorbed P at 39 stations |
| **S5** | Buffering scales with the volume of reactive medium | blocked on resolution | bathymetry is held; **sediment thickness is not** |
| **S6** | The retention coefficient is not constant — it saturates | **testable now** | the register's own Needs line: **'Requires no new measurement at all'** — the same catchment flux data split by period. Blocked only insofar as the flux series is the unfetched input |

### R. Decay and the community that does it

*11 hypotheses — 3 blocked on a fetch, 1 blocked on resolution, 1 unscoreable, 6 needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **R11** | Marine fungi decompose and nobody counts them | **unscoreable** | **essentially no marine fungal surveys in Danish waters** |
| **R1** | C:N of discharged material decides whether it is a sink | blocked on a fetch | **both numbers exist in discharge monitoring and the ratio is never formed** — a fetch and one arithmetic step |
| **R2** | Fresh carbon primes the old sediment pool | needs an experiment | sediment incubation with and without labile addition |
| **R3** | The decay relay stalls when a stage is removed | blocked on a fetch | sediment organic content with matched fauna — **both in ODA and never analysed together** |
| **R4** | N enrichment retards decay of the recalcitrant fraction | needs an experiment | litter-bag or incubation studies with characterised organic fractions |
| **R5** | The electron-acceptor cascade shifts with salinity | blocked on resolution | porewater sulphide and methane by station; rarely measured |
| **R6** | Sulphide locks the iron that would hold the phosphate | needs an experiment | **classified experiment-constructive** in `openproblems/R6.md`. NOVA teknisk anvisning kap.14 ran exactly this method 1998-2003 and it was discontinued |
| **R7** | Flocculation deposits river carbon at the coast | blocked on a fetch | sediment organic content with matched salinity — the register calls it obtainable |
| **R8** | Lipids are less soluble in seawater, so they deposit | needs an experiment | lipid fractionation by salinity |
| **R9** | Novel material decays slower — no home-field advantage | needs an experiment | comparative decomposition assays |
| **R10** | Osmotic discontinuity stalls the decomposers themselves | needs an experiment | cross-transplant incubations |

### L. The baseline and the counterfactual

*6 hypotheses — 2 testable now, 4 blocked on a fetch.*

| id | consequence | class | blocker |
|---|---|---|---|
| **L6** | The degraded bed is classified as its own habitat type | blocked on a fetch | historical seabed charts, old fisheries records and trawling effort — **the history a classification key discards** |
| **L1** | The reference condition never existed | blocked on a fetch | dated sediment cores with diatom and pigment stratigraphy; some exist and are not what the reference derives from |
| **L2** | The reference is a model output treated as a fact | **testable now** | **Archival, not statistical.** The reference model's assumptions and the indsatsbehov recomputed across their plausible range; DCE reports are public, text-extractable PDFs |
| **L3** | The trend depends on the start year | **testable now** | **Draft exists and was run** (`hypodrafts/L3.md`). 406 admissible windows; sign-flipping occurs in 100% of matched-AR nulls, so L3's strong reading is **not established** for bed oxygen |
| **L4** | Recovery is blocked by something other than the driver | blocked on a fetch | restoration trials with controls — a handful exist in Denmark and are not treated as decisive |
| **L5** | The reference sites are not references | blocked on a fetch | trawling, dumping and contaminant coverage for the areas used as references. The trawling layer is a 23 MB open fetch |

### I. Observation and measurement

*7 hypotheses — 6 testable now, 1 blocked on resolution.*

| id | consequence | class | blocker |
|---|---|---|---|
| **I1** | Apparent change concentrates where the network changed | **testable now** | **Draft exists** (`hypodrafts/I1.md`). 64 stations present in all eight 5-year eras, 8,485 station-months. The register cannot supply lifespans; presence comes from the observation record |
| **I2** | Step changes at probe changeover, shared across geography | blocked on resolution | **`SondeNr` is `999` on 83.5% of rows.** The usable 16.5% carries 33 real probes and is where I2 is testable |
| **I3** | Apparent severity scales with visit count and window | **testable now** | **Draft exists** (`hypodrafts/I3.md`). The count-and-window half is fully testable; **the diel half is carved out as class 6, unscoreable** |
| **I4** | Status shifts at definition changes with no measurement change | **testable now** | the definitions with their adoption dates — archival, and the recomputation runs on held data |
| **I5** | Trends present in corrected but not original results | **testable now** | **Held.** `KorrektionsFaktor` is 1 on 99.76% of rows and Original differs from Korrigeret on 0.24% |
| **I6** | Discontinuities at 2007 shared across stations that changed hands | **testable now** | `Dataleverandoer` and `TekniskAnvisningAnvendt` are in the raw record — but both are **near-constant** (one value each in a 1.2M-row sample), so the contrast may be empty |
| **I7** | Implausible values cluster in time across unrelated custodians | **testable now** | **Worked case already found**: 11 station-months, 6 stations, 4 custodian prefixes, May-June 2005, recorded in `flags.json` |

---

## What the shape of it says

### Half the field is not blocked on money or effort

**61 of 166 (37%) are blocked on a fetch**, and most of those fetches are
small. The ones that need no credentials at all: the ICES/HELCOM trawling layer (23 MB, CC BY
4.0), the three ODA vegetation and fauna topics (three one-line `TOPICS` entries), OBIS
phytoplankton via the eMoF extension (open REST), DMI tide gauges and wind (no key since March
2026), Sentinel-1 SAR, and ICES stock assessments. **A day of fetching would move a large
fraction of this table.**

### One fetch unblocks the most

**ODA `vandkemi` (`Emne_10_11`)** is the single highest-value fetch: it carries nitrogen,
phosphorus, silicate, ammonium and chlorophyll, and it is named in the blocker for **A1, A2,
A5, A7, B4, E2, E11, K1 and K2** — nine hypotheses, including the entire nutrient-limitation
argument. It is also the fetch that `fetch_oda.py` advertises in its docstring and never
implements. Second is **ODA bundfauna (`Emne_3_180`)** at seven — D11, F1, F2, H3, K14, T2, W4.

Note what that means for group A. **Not one hypothesis in the nutrient group is testable
now.** The group the entire public argument rests on is the group whose data this project
has not fetched.

### The largest single blocking dimension is not nutrients

**Twelve hypotheses are unscoreable for one missing dimension: microbial, viral and fungal
community composition** — E13, E17, F8, F11, F12, F13, F14, J8, R11, T5, T6, T8, T9, T12.
Not one Danish marine station counts viruses, sequences a microbial community, or surveys
fungi. That is a whole functional layer with no column anywhere, and it blocks more of this
register than any other single absence.

A second cluster of seven is **toxicant concentration in a marine matrix** — E7, E8, E18, J3,
J4, K8, K9 — where the national hazardous-substance layer turns out to hold 256 points, all
freshwater. Together those two dimensions account for **19 of the 40 unscoreable**, nearly
half, and neither is expensive to start measuring. eDNA and Alcian-blue TEP are cheap
standard methods; the register says so itself in several places.

### A quarter of the field cannot be scored at all, and that is the finding

**40 of 166 (24%) are unscoreable** — the deciding dimension has no
column and never did. Add the 20 that need an experiment and **36% of the hypothesis field is
beyond reach of any reanalysis of existing data.** No amount of cleverness with the archive
touches them.

This is the number that matters for how the whole argument should be read. When a public
debate settles on nutrients, it is not because nutrients won a contest against the
alternatives. **It is because nutrients are in group A, and group A has a monitoring
programme.** Sixty of these hypotheses have never been in a position to compete.

### Where the archive is strong

The **I** group — observation and measurement — is the only one where most hypotheses are
testable now (6 of 7). That is not a coincidence: those hypotheses are about the archive, and
the archive is the thing this project holds. **C** (physical resupply) is next at 5 of 9,
because temperature, salinity, depth and wind are exactly what a CTD and a weather reanalysis
give you.

The pattern across groups is blunt: **this archive can see physics and it cannot see biology.**
Groups C, G, Z and I hold most of the testable-now entries. Groups E, F, J, T and R — chemistry,
biological structure, films, sediment sickness, decay — hold almost none, and hold nearly all
of the unscoreable and experimental ones.

### An honest caveat about this table

The classification is mine and is itself an untested partition, exactly as the 17 groups are
(PLAN.md says so of them). Two judgements are load-bearing and contestable: I treated *not
fetched but fetchable* as **blocked on a fetch** rather than unscoreable even where nobody has
confirmed the topic contains what its name suggests; and I treated *measured somewhere in the
world but not in Denmark* as unscoreable **for this archive**, which is a statement about
Denmark's monitoring rather than about nature. Three entries I could not place at all are
marked *not established* rather than guessed.

And per [KNOWN_AND_UNKNOWN.md](../KNOWN_AND_UNKNOWN.md): **every "not measured" in this table
should be read as "not found by a search whose sensitivity nobody has characterised."** Six
things this project called absent turned out to exist in one day. The unscoreable column is
an upper bound on what is missing, not a measurement of it.
