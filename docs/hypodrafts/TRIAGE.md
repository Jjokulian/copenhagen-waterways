# Triage of the hypothesis field

PLAN.md's triage stage is "most of the work", and the stage after it is
meaningless until it exists. This is it: **all [166](../SOURCES.md#F-4196d405de) lettered hypotheses in [HYPOTHESES.md](../HYPOTHESES.md)**,
each in exactly one class, with the specific blocker.

[18](../SOURCES.md#F-2e51f8b7c4) already have a draft or an open-problem entry; those are marked and cite it rather
than being redone. **Nothing here has been run.** A classification is a claim about what could be done, not a result.

*Numbers shown as quotations are carried from this page as committed at `4469fc7`: nothing in the repository stores them yet, so each says what the page said, not that it was re-derived. Every other number is read live.*

*Classified before the water-chemistry extract was fetched on 2026-09-10. `scripts/rescore.py` re-scores the hypotheses that fetch unblocks; the classes below are as triaged.*

| class | n | share |
|---|---:|---:|
| **testable now** | [24](../SOURCES.md#F-e786dfc514) | [14](../SOURCES.md#F-aff8947a9f)% |
| blocked on a fetch | [61](../SOURCES.md#F-15045ed0fb) | [37](../SOURCES.md#F-00ac661b28)% |
| blocked on resolution | [18](../SOURCES.md#F-ab9e2895d5) | [11](../SOURCES.md#F-0d520cad5c)% |
| **unscoreable** | [40](../SOURCES.md#F-198b20fb90) | [24](../SOURCES.md#F-935d9e0296)% |
| needs an experiment | [20](../SOURCES.md#F-64bb5d44db) | [12](../SOURCES.md#F-42f0fd7709)% |
| not established | [3](../SOURCES.md#F-6f2641deb0) | [2](../SOURCES.md#F-3307597d2e)% |
| | **[166](../SOURCES.md#F-4196d405de)** | |

**Class definitions.** *Testable now* — consequence, a source in hand, and a null computable
under the constraint imposed. *Blocked on a fetch* — named, with whether it needs credentials.
*Blocked on resolution* — needs depth, sub-monthly time, per-measurement position, or the
measurement-level store. *Unscoreable* — the deciding dimension has no column and never did;
**this is not a refutation**. *Needs an experiment* — no observational design reaches it.
*Not established* — I could not tell, and say so rather than guess.

---

## The table

### A. Nutrient-driven production in place

*[10](../SOURCES.md#F-b17d38223a) hypotheses — [8](../SOURCES.md#F-cd21100ace) blocked on a fetch, [1](../SOURCES.md#F-0528ea00b7) unscoreable, [1](../SOURCES.md#F-1bbb2adcef) not established.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[A1](../hypodrafts/A1.md "Danish land-based nitrogen load")** | Load up -> summer chlorophyll up -> bottom <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> down, per area per month | blocked on a fetch | ODA vandkemi `Emne_10_11` (N, P, chlorophyll) — ODA login. Land load additionally needs `STOFTRANSPORT`/`TILFOERSEL`, which require a **code change**: `run()` hardcodes the Hav endpoint |
| **[A2](../HYPOTHESES.md "Phosphorus load")** | P flux up -> spring chlorophyll up | blocked on a fetch | same vandkemi fetch |
| **[A3](../HYPOTHESES.md "Atmospheric deposition on the sea surface")** | Deposition over sea up -> production up where land load is low | blocked on a fetch | DEHM marine-grid deposition, monthly, incl. the organic-N fraction that is generally not reported |
| **[A10](../HYPOTHESES.md "Exhaust-treatment reagent: nitrogen added to remove nitrogen")** | Urea-derived N from exhaust treatment enters the budget it abates | not established | A mass-balance argument, not an observable here. Whether any reaches the sea is not established |
| **[A4](../HYPOTHESES.md "Point-source discharge of nutrients")** | Plant discharge down at upgrade date -> local N down stepwise | blocked on a fetch | per-plant monthly N/P/COD with upgrade dates. `punkt_rens_udl.geojson` gives locations only |
| **[A5](../HYPOTHESES.md "Advected nutrients from outside Denmark")** | Nutrients at Belt/Sound sections co-vary with inner-water state | blocked on a fetch | vandkemi at section stations. CMEMS Baltic indicators are held but carry no nutrients |
| **[A6](../HYPOTHESES.md "Submarine groundwater discharge")** | SGD delivers N where no stream does | **unscoreable** | **Submarine groundwater discharge is not a term in the national account.** No Danish SGD survey exists at all |
| **[A7](../openproblems/A7.md "Sediment nutrient regeneration")** | Bottom-water DIP rises in summer without a matching river input | blocked on a fetch | vandkemi `Emne_10_11` (ortho-P, now held: [650](../SOURCES.md#F-53c0aaacfb) stations in the extract carry it) + sedimentkemi `Emne_12_19` ([39 stations](../SOURCES.md#F-9a8f0de490)). `openproblems/A7.md`: armchair for the weak form, measurement for the strong |
| **[A8](../HYPOTHESES.md "Marine aquaculture")** | Sediment near pens enriched vs matched controls | blocked on a fetch | per-farm production and feed by month. `punkt_havdam_udl.geojson` gives farm locations only |
| **[A9](../HYPOTHESES.md "Nitrogen fixation")** | Cyanobacteria abundance up where N:P is low | blocked on a fetch | phytoplankton counts — OBIS eMoF carries [103,005 Danish abundance records](../SOURCES.md#F-82d0025ffc), open REST, **no credentials** (`hypodrafts/K1.md`) |

### B. Oxygen demand that arrived already made

*[8](../SOURCES.md#F-14ca135518) hypotheses — [1](../SOURCES.md#F-6b6b8f73b9) testable now, [4](../SOURCES.md#F-1ec2922bf1) blocked on a fetch, [1](../SOURCES.md#F-36488d1ed1) blocked on resolution, [2](../SOURCES.md#F-a7ec13c7e5) unscoreable.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[B1](../hypodrafts/B1.md "Combined sewer overflow")** | Bathing indicator up downstream of combined outfalls after rain, not separate ones | **testable now** | **Draft exists** (`hypodrafts/B1.md`). Uses combined-vs-separate class and an a priori critical rainfall depth, never modelled volume. Its EEA WISE claim is unverified |
| **[B2](../HYPOTHESES.md "Separate stormwater")** | First-flush concentration x volume exceeds the annual-total assumption | blocked on resolution | event-resolved concentration and volume at the outfall. Annual totals over [16,185](../SOURCES.md#F-f88f6ae3cd) separate stormwater outfalls cannot test a first-flush claim |
| **[B3](../HYPOTHESES.md "Treatment plant organic load")** | Plant COD/BOD up -> local oxygen demand up | blocked on a fetch | per-plant monthly COD/BOD |
| **[B4](../HYPOTHESES.md "Riverine particulate organic carbon")** | Riverine POC up -> sediment organic content up at the receiving coast | blocked on a fetch | suspended solids and organic carbon at stream stations (vandkemi / stoftransport) |
| **[B5](../HYPOTHESES.md "Industrial organic discharge")** | Industrial organic load co-locates with local demand | blocked on a fetch | industrial discharge permits and reported loads per site per year |
| **[B6](../HYPOTHESES.md "Harbour and fish-processing waste")** | Harbour water shows a demand signature the open coast does not | **unscoreable** | **Harbour water quality measurements are largely absent.** No column anywhere held |
| **[B7](../HYPOTHESES.md "Shipping discharges")** | Scrubber and bilge discharge along tracks -> local demand | blocked on a fetch | AIS tracks are obtainable; **discharge volumes essentially do not exist**, so the second half is unscoreable |
| **[B8](../HYPOTHESES.md "Direct manure and slurry entry")** | Incident-linked slurry entry -> local spike | **unscoreable** | **No public environmental incident register with date and location** |

### C. Physical control of resupply

*[9](../SOURCES.md#F-89669b4a5d) hypotheses — [5](../SOURCES.md#F-0596b7e6b1) testable now, [2](../SOURCES.md#F-f5117cda81) blocked on a fetch, [2](../SOURCES.md#F-1ef9a0c61b) blocked on resolution.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[C1](../hypodrafts/C1.md "Stratification strength")** | Hypoxia is near-zero in well-mixed water at matched depth | **testable now** | **Draft exists** (`hypodrafts/C1.md`). [133,509](../SOURCES.md#F-48d6afcb0d) station-days with at least [4](../SOURCES.md#F-6c91311fd6) depth levels of T and S plus bottom oxygen, from the raw CTD |
| **[C2](../HYPOTHESES.md "Wind work")** | Wind work up -> stratification broken -> bottom <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> up | **testable now** | hourly wind held (`data/raw/weather/`, [31](../SOURCES.md#F-bec24964f0) years) joined to CTD profiles |
| **[C3](../HYPOTHESES.md "Residence time")** | Long residence time -> lower <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> at matched load | blocked on resolution | per-area residence time held only coarsely — the [9 km](../SOURCES.md#F-42e5714106) field is too slow in the straits by its own calibration: at Drogden its peak speed falls short of the published peak by a factor of [1.9](../SOURCES.md#F-014acc7128) |
| **[C4](../hypodrafts/C4.md "Baltic inflow events")** | Inflow -> deep <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> pulse, lagged, ordered Belts->Arkona->Bornholm->Gotland | **testable now** | **Draft exists** (`hypodrafts/C4.md`). MBI indicator and Gotland profiles held; the published inflow record is not, so a wind-derived instrument substitutes |
| **[C5](../HYPOTHESES.md "Freshwater discharge buoyancy")** | Freshwater pulse -> stratification up -> bottom <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> down | blocked on a fetch | daily freshwater discharge per catchment |
| **[C6](../hypodrafts/C6.md "Water temperature and solubility")** | Deficit vs saturation separates solubility from consumption | **testable now** | **Draft exists** (`hypodrafts/C6.md`). [76,305 station-months](../SOURCES.md#F-2569b0a818) carrying <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span>, T and S near-bed |
| **[C7](../HYPOTHESES.md "Bathymetry, sills and depth")** | Deeper and silled areas go hypoxic at lower load | **testable now** | bottom depth per visit in `maaledybde` ([151,203](../SOURCES.md#F-5683df4d6c) rows); sill geometry from `marin_overordnet.geojson` |
| **[C8](../HYPOTHESES.md "Constructed change to circulation")** | Construction changed exchange -> step in local state at the works date | blocked on resolution | construction chronology partial; needs works dates and footprints joined to sub-monthly state |
| **[C9](../HYPOTHESES.md "Sea level and tidal change")** | Sea level and tidal change alter exchange | blocked on a fetch | DMI oceanObs tide gauges — [10-minute from 1889](../SOURCES.md#F-56b62f9d5b), `CC BY 4.0`, **no API key required since 2026-03-26** |

### D. Physical disturbance of the bed

*[11](../SOURCES.md#F-374e783817) hypotheses — [1](../SOURCES.md#F-7b66b1ce10) testable now, [8](../SOURCES.md#F-a7d44831d4) blocked on a fetch, [1](../SOURCES.md#F-decb4f89ff) unscoreable, [1](../SOURCES.md#F-ada657e8a8) needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[D1](../hypodrafts/D1.md "Bottom trawling")** | Effort up -> near-bed <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> down, strongest on fine substrate, absent [>20 m](../SOURCES.md#F-5666403060) | blocked on a fetch | ICES/HELCOM swept-area ratio, `figshare 20310255` — **[23.1 MB](../SOURCES.md#F-b097822783), `CC BY 4.0`, no credentials**. Draft exists (`hypodrafts/D1.md`) |
| **[D2](../HYPOTHESES.md "Navigation dredging")** | Dredging event -> local turbidity and demand spike | blocked on a fetch | dredging permits with dates, volumes and locations |
| **[D3](../HYPOTHESES.md "Dredged-material dumping")** | A dumping ground shows a signature its surroundings do not | blocked on a fetch | `klappladser.geojson` gives the grounds. Per-ground volume, date and material chemistry are in MST-KLAP as individual PDFs |
| **[D4](../HYPOTHESES.md "Sand and gravel extraction")** | An extraction area differs from matched unextracted seabed | blocked on a fetch | `raastofomr.geojson` gives the areas; per-area extracted volume by year is not held |
| **[D5](../HYPOTHESES.md "Cable and pipeline works")** | Cable route works -> local disturbance signature | blocked on a fetch | route and installation-date registers |
| **[D6](../HYPOTHESES.md "Anchoring and propeller wash")** | Anchorage seabed differs from matched non-anchorage | blocked on a fetch | AIS anchoring events and anchorage designations |
| **[D7](../hypodrafts/D7.md "Storm-driven resuspension")** | Transparency deficit lags critical bed shear, only in shallow water | **testable now** | **Draft exists** (`hypodrafts/D7.md`). [96,709 dated Secchi+depth visits](../SOURCES.md#F-ca2cc6af30), `Turbiditet` [1,076,915](../SOURCES.md#F-85266abfd1) rows, wind held. The monthly panel cannot resolve events, so the draft runs on the dated raw record |
| **[D8](../HYPOTHESES.md "Loss of biostabilisation, and the mobile bed")** | A biostabilised bed resists erosion to higher shear | needs an experiment | **erodibility measurement (cohesive strength meter or flume) with matched surface-sediment chlorophyll.** Standard method, not in Danish monitoring |
| **[D9](../HYPOTHESES.md "Fertility islands lost to homogenisation")** | Within-area fauna variance collapses under homogenisation | **unscoreable** | **One grab per station by design.** Within-area variance cannot be estimated from a design that samples one point per area |
| **[D10](../HYPOTHESES.md "Winnowing and armouring")** | Grain size coarsens where fines are winnowed | blocked on a fetch | ODA sediment grain size as a time series. `seabed_sediment_dk.gpkg` is a static [108](../SOURCES.md#F-5c1dccef56)-polygon mosaic from [19](../SOURCES.md#F-5a9ac13e75) mapping programmes, at scale denominators from [5,000](../SOURCES.md#F-0827f1f9d3) to [500,000](../SOURCES.md#F-d20841b0ec) |
| **[D11](../HYPOTHESES.md "Stabilisers against destabilisers")** | Stabiliser:destabiliser ratio predicts bed state | blocked on a fetch | ODA bundfauna `Emne_3_180`, then a desk trait assignment |

### E. Chemical demand and toxicity

*[20](../SOURCES.md#F-4ea953ea01) hypotheses — [6](../SOURCES.md#F-4c1023c5f4) blocked on a fetch, [1](../SOURCES.md#F-8693013085) blocked on resolution, [11](../SOURCES.md#F-6534048aeb) unscoreable, [1](../SOURCES.md#F-52cfe2e72d) needs an experiment, [1](../SOURCES.md#F-0f8c435d44) not established.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[E1](../HYPOTHESES.md "Sulphide oxidation")** | Sulphide oxidation consumes <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> where redox is low | blocked on a fetch | sedimentkemi `Emne_12_19`; sediment redox and sulphide are rarely measured even there |
| **[E2](../HYPOTHESES.md "Nitrification demand")** | Nitrification demand scales with ammonium | blocked on a fetch | **ammonium is NOT in the CTD file.** The Needs line saying 'in the ODA water chemistry' means unfetched — vandkemi `Emne_10_11` |
| **[E3](../HYPOTHESES.md "Iron and manganese oxidation")** | Fe/Mn oxidation consumes <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> at the redox front | needs an experiment | porewater chemistry, very rare, and the mechanism is millimetre-scale |
| **[E4](../HYPOTHESES.md "Methane oxidation")** | Methane oxidation consumes <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> above seeps | **unscoreable** | **Essentially no Danish coastal methane flux record** |
| **[E5](../HYPOTHESES.md "Direct chemical oxygen demand of discharges")** | Discharge COD carried into a marine budget changes the balance | blocked on a fetch | per-outlet COD — measured in discharge monitoring and never carried through |
| **[E6](../HYPOTHESES.md "Biocides and antifoulants")** | Antifoulant concentration up -> decomposer function down | **unscoreable** | **Sediment measured at [5](../SOURCES.md#F-8bf5ff138f) of [256](../SOURCES.md#F-aee5a58e2f) national hazardous-substance stations — and not one is coastal** ([152](../SOURCES.md#F-4e20821308) lake, [104](../SOURCES.md#F-53860b0f29) river, [0](../SOURCES.md#F-929f2dcc25) coastal; `sw_mfs_tilstand.geojson`) |
| **[E7](../openproblems/E7.md "Pesticides and degradation products")** | Pesticide load co-varies with N and acts separately | **unscoreable** | **No toxicant column in [53,710,760](../SOURCES.md#F-4df017f985) CTD rows, none in [679,422](../SOURCES.md#F-7769a94f7a) station-months.** `openproblems/E7.md` classifies it measurement |
| **[E8](../HYPOTHESES.md "Pharmaceuticals and personal care products")** | Pharmaceutical residues alter microbial function | **unscoreable** | almost no Danish marine pharmaceutical monitoring |
| **[E9](../HYPOTHESES.md "PFAS and persistent novo-chemicals")** | PFAS persists and accumulates in biota | blocked on a fetch | some biota data exists (ICES DOME); sediment barely. A fetch would establish the extent |
| **[E10](../HYPOTHESES.md "Heavy metals")** | Metal concentration up -> benthic function down | blocked on a fetch | ICES DOME holds Danish Fe/S/PTOT — **[47 samples at 12 positions, all 1990-91](../SOURCES.md#F-4971d11aa7)** (`openproblems/R6.md`) |
| **[E11](../HYPOTHESES.md "Ammonia toxicity")** | Un-ionised ammonia is toxic at high pH and temperature | blocked on a fetch | **pH is held ([237,496](../SOURCES.md#F-9b03a32d66) rows); ammonium is not.** vandkemi fetch |
| **[E12](../HYPOTHESES.md "Hydrogen sulphide toxicity")** | Free sulphide is toxic to fauna above a threshold | blocked on resolution | `Dihydrogensulfid` is [2,601](../SOURCES.md#F-153d19187a) rows and **[2,598](../SOURCES.md#F-906d8ca940) come from one station** (Mariager, `93610032`). Usable for one silled basin, not a series |
| **[E13](../HYPOTHESES.md "Biocides that remove the decomposers themselves")** | Fungicides remove decomposers -> decay stalls | **unscoreable** | **Neither fungicide in sediment nor fungal biomass is measured.** `R11` records that the fungi are not counted anywhere |
| **[E14](../HYPOTHESES.md "Veterinary antiparasitics in manure")** | Antiparasitic residues in manure reach water and act | **unscoreable** | not routinely measured in Danish soil, runoff or sediment |
| **[E15](../HYPOTHESES.md "Total biocide load, whatever its source")** | Total biocide load, not per-substance, predicts effect | **unscoreable** | **Nothing assembles national sales data into an environmental load by catchment** |
| **[E16](../HYPOTHESES.md "Conserved targets: 'selective' is a claim about dose")** | High-tonnage compounds act on conserved targets at realistic dose | **unscoreable** | marine concentrations of the actual high-tonnage compounds are not monitored |
| **[E18](../HYPOTHESES.md "Tyre-wear transformation products")** | `6PPD-quinone` is lethal to salmonids at road-runoff concentrations | **unscoreable** | **`6PPD-quinone` is not measured in Danish monitoring.** Danish sea-trout sensitivity is also unestablished |
| **[E20](../HYPOTHESES.md "Fuel oxygenates and additives")** | Fuel oxygenates reach coastal water | not established | groundwater monitoring covers some; whether any is reported for coastal discharge is not established |
| **[E19](../HYPOTHESES.md "The sentinel species decides what is detectable")** | Standard test batteries miss locally present sensitive species | **unscoreable** | **No panel of locally present species exists**, so this cannot be checked for any compound |
| **[E17](../HYPOTHESES.md "The microbiome is the exposed organ")** | The microbiome is the exposed organ | **unscoreable** | **No host-associated microbial community data for any Danish marine organism** |

### F. Biological structure and feedback

*[14](../SOURCES.md#F-6d7e02bdc1) hypotheses — [6](../SOURCES.md#F-5dc96c18dc) blocked on a fetch, [1](../SOURCES.md#F-f6b2b6fd6a) blocked on resolution, [7](../SOURCES.md#F-1e069ecf65) unscoreable.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[F1](../HYPOTHESES.md "Loss of filter feeders")** | Filter-feeder loss -> clearance down -> chlorophyll up | blocked on a fetch | ODA bundfauna `Emne_3_180`; shellfish stock assessments |
| **[F2](../HYPOTHESES.md "Loss of bioturbators")** | Bioturbator loss -> sediment <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> penetration down | blocked on a fetch | ODA bundfauna `Emne_3_180`, species-level abundance and biomass |
| **[F3](../hypodrafts/F3.md "Loss of eelgrass and macroalgae")** | Cover falls where light is adequate -> the block is not light | blocked on a fetch | ODA `Emne_3_182` aalegraes, [1,990 stations](../SOURCES.md#F-cc3e6bc0a9) 1970-2026 — **three one-line TOPICS entries, no extra credentials**. Draft exists (`hypodrafts/F3.md`) |
| **[F4](../HYPOTHESES.md "Trophic cascade from a removal far away")** | Distant stock removal -> cascade to local grazing | blocked on a fetch | ICES stock assessments and Danish landings by area and year — **both open, already in the fetch queue** |
| **[F5](../HYPOTHESES.md "Invasive species")** | Invasive arrival -> function change at the arrival date | blocked on a fetch | species observation records with date and position (OBIS/GBIF, open) |
| **[F6](../HYPOTHESES.md "Jellyfish blooms")** | Jellyfish blooms alter the pathway | **unscoreable** | **Essentially no jellyfish monitoring in Denmark** |
| **[F7](../HYPOTHESES.md "Harmful algal blooms specifically")** | HAB species specifically, not chlorophyll, drive the harm | blocked on a fetch | phytoplankton species counts — collected, and OBIS eMoF carries [103,005 Danish abundance records](../SOURCES.md#F-4cc467c80e) |
| **[F8](../HYPOTHESES.md "Microbial shift to fast-growing forms")** | Community shifts to fast-growing forms under enrichment | **unscoreable** | **Microbial community composition is not monitored at all** |
| **[F9](../HYPOTHESES.md "Disease and parasite mass mortality")** | Disease mortality event -> structural loss | **unscoreable** | the marine mortality event register is ad hoc; no systematic column |
| **[F10](../HYPOTHESES.md "Vertebrate mass mortality")** | Vertebrate mass mortality signals a pathway | blocked on resolution | stranding networks are partial; needs event dates joined to state |
| **[F11](../HYPOTHESES.md "Viral lysis and the viral shunt")** | Viral lysis short-circuits the food web | **unscoreable** | **Marine viral counts are not in Danish monitoring at any station** — a standard method [since the 1990s](../SOURCES.md#F-7efa1f7a4c) |
| **[F13](../HYPOTHESES.md "The organisms that fall between the folk categories")** | Organisms between the folk categories go unrecorded | **unscoreable** | **No eDNA survey with an open taxonomic frame.** The categories on the existing forms are the cause |
| **[F14](../HYPOTHESES.md "Viruses as structure, not only as mortality")** | Viruses are structure, not only mortality | **unscoreable** | **Not measured at any Danish station.** Flagged in-register as the most likely location of the mycorrhizal gap |
| **[F12](../HYPOTHESES.md "The micropathogens nobody catalogues")** | Micropathogens of invertebrates are uncatalogued | **unscoreable** | **Denmark has no marine mortality response capability for invertebrates** |

### G. Climate and long-term drivers

*[6](../SOURCES.md#F-b296cd70dd) hypotheses — [2](../SOURCES.md#F-dafd9a8d83) testable now, [3](../SOURCES.md#F-4b41d0c1a1) blocked on a fetch, [1](../SOURCES.md#F-2a5b45d5cb) blocked on resolution.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[G1](../hypodrafts/G1.md "Warming")** | d<span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span>/dt = dC_sat/dt − dD/dt; the deficit widens or it does not | **testable now** | **Draft exists** (`hypodrafts/G1.md`). [76,264 five-way joined station-months](../SOURCES.md#F-d18bfaa666); Weiss makes the solubility channel exact rather than estimated |
| **[G2](../HYPOTHESES.md "Changing precipitation and runoff timing")** | Runoff timing shifts -> load timing shifts -> state shifts | blocked on a fetch | daily discharge and concentration, not annual sums |
| **[G3](../HYPOTHESES.md "Changing wind climatology")** | Wind climatology change -> mixing change | **testable now** | hourly wind held, [31](../SOURCES.md#F-bec24964f0) years. The trend null must be matched-autocorrelation, not independence |
| **[G4](../HYPOTHESES.md "Acidification")** | Acidification alters carbonate saturation for calcifiers | blocked on resolution | pH is held ([237,496](../SOURCES.md#F-9b03a32d66) rows) but the **carbonate system needs two of pH / alkalinity / DIC / p<span class="chem" data-chem="CO2" title="carbon dioxide">CO₂</span>**, and only one is held |
| **[G5](../HYPOTHESES.md "Changing ice cover")** | Ice cover change alters seasonal mixing | blocked on a fetch | ice records — available, not fetched |
| **[G6](../HYPOTHESES.md "Sea level rise")** | Sea level rise alters exchange and inundation | blocked on a fetch | DMI tide gauges — long, open, not fetched |

### H. State, memory and regime

*[4](../SOURCES.md#F-a5ec7810c4) hypotheses — [3](../SOURCES.md#F-7b6ee61308) blocked on a fetch, [1](../SOURCES.md#F-cf209f6aad) blocked on resolution.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[H1](../HYPOTHESES.md "Alternative stable states and hysteresis")** | State does not retrace the load path — hysteresis | blocked on resolution | needs long paired load-and-state through **both** directions; the load half is unfetched and the reversal may not have occurred |
| **[H2](../HYPOTHESES.md "Sediment legacy")** | Sediment legacy sustains demand after load falls | blocked on a fetch | sediment organic content and accumulation rates, and **dated cores** |
| **[H3](../HYPOTHESES.md "Loss of resilience through diversity loss")** | Diversity loss -> variance of response up | blocked on a fetch | ODA bundfauna `Emne_3_180`, long species-level series |
| **[H4](../HYPOTHESES.md "Subsidy-stress")** | Response is non-monotone across the load gradient | blocked on a fetch | the [123](../SOURCES.md#F-173d507c7a) areas supply the gradient; the **load axis is the unfetched half** |

### J. Surface film, gel and the greasy water itself

*[9](../SOURCES.md#F-ca1cf2a63d) hypotheses — [1](../SOURCES.md#F-1efd11344c) blocked on a fetch, [2](../SOURCES.md#F-ba16162ea9) blocked on resolution, [5](../SOURCES.md#F-048c9341ee) unscoreable, [1](../SOURCES.md#F-51f28a1b04) not established.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[J1](../openproblems/J1.md "Transparent exopolymer particles and marine gel")** | Attenuation residual after chlorophyll, CDOM and particles is gel | **unscoreable** | **TEP is not measured at all**, and `Lysdaempning` is a bare `pct` with **no path length recorded**, so the total has no physical units. `openproblems/J1.md` |
| **[J2](../HYPOTHESES.md "Sea-surface microlayer enrichment")** | Microlayer enrichment concentrates surfactants and toxicants | **unscoreable** | **No sea-surface microlayer sampling in Danish monitoring** |
| **[J3](../HYPOTHESES.md "Surfactants from detergents and personal care")** | Surfactant load -> film -> gas exchange down | **unscoreable** | essentially no marine surfactant measurements |
| **[J4](../HYPOTHESES.md "Sunscreen and UV filters")** | UV filters accumulate in nearshore water | **unscoreable** | **No marine UV-filter monitoring in Denmark** |
| **[J9](../HYPOTHESES.md "Fragmentation as a source term, and the inventory that omits it")** | Fragmentation is a source term the inventory omits | not established | the national inventory gives [5,500-13,900 t/yr released and 600-3,100 t/yr to sea](../SOURCES.md#F-33cad98ad5); whether fragmentation is separable within it is not established |
| **[J5](../HYPOTHESES.md "Microplastic and its biofilm")** | Microplastic biofilm alters the microlayer | blocked on resolution | some Danish microplastic data exists; microlayer-specific, none |
| **[J6](../HYPOTHESES.md "Oil and hydrocarbon films")** | Oil films in SAR co-locate with the greasy-water reports | blocked on a fetch | **`Sentinel-1` SAR is free and covers the whole period.** The register's own Needs line says this one is testable now — it is a fetch away |
| **[J7](../HYPOTHESES.md "Exudate from senescing blooms")** | Bloom collapse -> DOC pulse -> film | blocked on resolution | **DOC at sub-monthly resolution.** The sampling frequency is the binding constraint |
| **[J8](../HYPOTHESES.md "Bacterial exopolymer from fast-growing communities")** | Fast-growing communities exude more polymer | **unscoreable** | microbial community data is not monitored |

### K. Depletion and imbalance of what life requires

*[14](../SOURCES.md#F-eb0e417241) hypotheses — [2](../SOURCES.md#F-ef76059756) testable now, [4](../SOURCES.md#F-eb1cc571c1) blocked on a fetch, [1](../SOURCES.md#F-22ddb6e7b6) blocked on resolution, [6](../SOURCES.md#F-9c7c58c0f7) unscoreable, [1](../SOURCES.md#F-8254bef792) needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[K1](../hypodrafts/K1.md "Silicon depletion and the diatom-to-flagellate shift")** | Si:DIN falls -> diatom share falls -> flagellates rise | blocked on a fetch | **silicate is NOT in the CTD file** — vandkemi `Emne_10_11`; phytoplankton via OBIS eMoF. Draft exists (`hypodrafts/K1.md`); the CMEMS DIATO field is a relabelling of CHL and cannot bear it |
| **[K2](../HYPOTHESES.md "Stoichiometric imbalance decides who grows")** | N:P:Si ratio, not absolute load, selects the assemblage | blocked on a fetch | same vandkemi fetch plus species counts |
| **[K3](../HYPOTHESES.md "Macronutrient excess inducing micronutrient deficiency")** | Macronutrient excess induces micronutrient deficiency in tissue | needs an experiment | **tissue elemental analysis of algae and eelgrass is not collected** |
| **[K4](../HYPOTHESES.md "Thiamine (B1) deficiency")** | Thiamine deficiency propagates up the food web | **unscoreable** | **No Danish marine thiamine assays.** Swedish and Finnish work exists |
| **[K5](../HYPOTHESES.md "Cobalamin (B12) and cobalt limitation")** | Vitamin `B12` and cobalt limit the auxotrophs | **unscoreable** | **No marine `B12` measurements in Denmark** |
| **[K6](../HYPOTHESES.md "Iron bioavailability")** | Iron bioavailability limits production or detoxification | **unscoreable** | iron speciation is not monitored |
| **[K7](../HYPOTHESES.md "Carbonate ion depletion")** | Carbonate ion depletion impairs calcification | blocked on resolution | needs two carbonate-system variables; one is held |
| **[K8](../HYPOTHESES.md "The narrow window between deficient and toxic")** | The window between deficient and toxic is narrow and crossed | **unscoreable** | trace elements with matched biological response; sediment metals at four national points |
| **[K9](../HYPOTHESES.md "Selenium")** | Selenium status limits or intoxicates | **unscoreable** | selenium in Danish marine biota is not routinely measured |
| **[K10](../HYPOTHESES.md "Salinity change and osmotic cost")** | Salinity change imposes osmotic cost at the range edge | **testable now** | salinity by station, date and depth is in the CTD record — [7,474,645](../SOURCES.md#F-cf5c72a98d) rows |
| **[K11](../HYPOTHESES.md "Light as a depleted resource")** | Light at the bed = f(Kd, depth), and the product is rarely formed | **testable now** | **Both halves held**: `lys` [2,370,091](../SOURCES.md#F-d9b22c989d) rows and bottom depth in `maaledybde`, [96,708](../SOURCES.md#F-e51550bdc9) paired. Carries the Kd start-depth artefact, and Secchi censoring at the bed: [36.9](../SOURCES.md#F-46aa1895a2)% of paired readings in water shallower than [5](../SOURCES.md#F-7f0e8a949b) m reach the bed |
| **[K12](../HYPOTHESES.md "Loss of habitat-forming structure")** | Structure removal -> habitat loss independent of water quality | blocked on a fetch | stone extraction records, reef restoration locations and dates |
| **[K13](../HYPOTHESES.md "Food depletion for filter feeders and larvae")** | Particle spectra shift below the filter-feeder window | **unscoreable** | **Particle size spectra and larval condition indices are not monitored** |
| **[K14](../HYPOTHESES.md "Genetic and functional diversity depletion")** | Functional diversity falls before species richness does | blocked on a fetch | ODA bundfauna `Emne_3_180` |

### W. Renewal and rate

*[8](../SOURCES.md#F-9777cbd65a) hypotheses — [1](../SOURCES.md#F-e5193dafdc) testable now, [3](../SOURCES.md#F-68e0354bdb) blocked on a fetch, [2](../SOURCES.md#F-ef0f98c5fb) blocked on resolution, [2](../SOURCES.md#F-0bd0994607) needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[W1](../HYPOTHESES.md "Propagule supply and connectivity")** | Recovery fails where propagule supply is cut | blocked on resolution | source populations plus particle tracking; the held circulation model is [9 km](../SOURCES.md#F-2f08917523) and [~2x slow](../SOURCES.md#F-a939d23b80) in the straits |
| **[W2](../HYPOTHESES.md "Settlement cue failure")** | Unconditioned substrate fails to recruit | needs an experiment | **settlement plates with and without conditioning.** Cheap, and connects to the sediment-inoculation experiment `X1` |
| **[W3](../HYPOTHESES.md "Phenological mismatch")** | Bloom and larval peak drift apart | blocked on resolution | **sub-monthly plankton series.** The register itself states sampling frequency is the binding constraint, not the parameters |
| **[W4](../HYPOTHESES.md "Allee effects at low density")** | Below a density threshold reproduction fails | blocked on a fetch | ODA bundfauna carries densities; the analysis is then a desk exercise |
| **[W5](../HYPOTHESES.md "Recovery slower than the disturbance interval")** | Disturbance interval shorter than recovery time | blocked on a fetch | **trawling effort at monthly or finer.** The ICES/HELCOM layer is quarterly; finer is the closed dataset |
| **[W6](../HYPOTHESES.md "Change outrunning acclimation")** | Rate of change exceeds acclimation rate | **testable now** | **high-frequency records exist and are analysed for means rather than rates.** The CTD record supports a rate analysis now |
| **[W8](../HYPOTHESES.md "Whoever founds the community keeps it")** | The founder community determines the endpoint | needs an experiment | composition immediately after disturbance and through recovery at the same place — requires having sampled before |
| **[W7](../HYPOTHESES.md "Too little variation left to respond with")** | Too little standing variation is left to respond with | blocked on a fetch | long species-level fauna is in ODA; **genetic data nobody has**, so that half is unscoreable |

### Z. The physical fields and their windows

*[11](../SOURCES.md#F-bd58527cd6) hypotheses — [3](../SOURCES.md#F-5a90478e4b) testable now, [2](../SOURCES.md#F-22cf725cc7) blocked on a fetch, [3](../SOURCES.md#F-56f1715935) blocked on resolution, [2](../SOURCES.md#F-2c1d0d090e) unscoreable, [1](../SOURCES.md#F-03944105f9) needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[Z1](../HYPOTHESES.md "Light: too little, and too much")** | Light at the bed outside the window -> loss | **testable now** | the same product as [K11](../HYPOTHESES.md "Light as a depleted resource"); both halves held |
| **[Z2](../HYPOTHESES.md "Light quality, not quantity: browning")** | Browning shifts the spectrum, not just the quantity | blocked on resolution | **Kd is a single broadband number.** FDOM ([890,921](../SOURCES.md#F-acb2b229c0) rows, from [2021](../SOURCES.md#F-281b3dc6e4) onward only) is a CDOM proxy on the same cast — [6](../SOURCES.md#F-d7f71d585c) years of in-situ CDOM |
| **[Z3](../HYPOTHESES.md "Photoperiod and timing as a cue")** | Photoperiod cue decouples from temperature cue | **unscoreable** | **Effectively no phenological observations for Danish marine invertebrates** |
| **[Z4](../HYPOTHESES.md "Temperature: window, and rate")** | Rate of temperature change, not level, exceeds tolerance | blocked on resolution | bottom temperature at high frequency; the monthly product aliases it, the raw record may not |
| **[Z5](../HYPOTHESES.md "Hydrodynamic energy has a floor as well as a ceiling")** | Energy has a floor — too still is also a failure | **testable now** | bed shear already computed here from [31](../SOURCES.md#F-bec24964f0) years of wind; the floor is testable against the same state variables |
| **[Z6](../HYPOTHESES.md "Sound, as a cue and as a stressor")** | Sound masks settlement cues | **unscoreable** | **essentially no noise measurement tied to invertebrate settlement** |
| **[Z7](../HYPOTHESES.md "Electromagnetic fields")** | EMF from cables alters behaviour | blocked on resolution | cable routes and energisation dates are available; **biological response is not measured** |
| **[Z8](../hypodrafts/Z8.md "The attenuation budget is never partitioned")** | The attenuation budget is never partitioned | **testable now** | **Draft exists** (`hypodrafts/Z8.md`). Kd plus chlorophyll, CDOM and particle proxies on the same cast, [9,717 casts with all four](../SOURCES.md#F-ca83bd8c3e) — but `Lysdaempning` has no path length, so it is a variance apportionment, not a budget |
| **[Z9](../HYPOTHESES.md "Epiphyte shading, which bypasses the water column")** | Epiphytes shade the plant regardless of water clarity | blocked on a fetch | epiphyte biomass on eelgrass — in research programmes, not routine monitoring |
| **[Z10](../HYPOTHESES.md "Mineral plumes from works")** | Works plumes exceed natural turbidity long enough to matter | blocked on a fetch | works chronology plus the turbidity monitoring large projects must do and rarely reanalyse |
| **[Z11](../HYPOTHESES.md "The weakened host")** | A weakened host fails at a stress a healthy one survives | needs an experiment | carbohydrate reserves, tissue sulphide and pathogen load on the same plants |

### T. Sediment sickness: symbionts, pathogens and why nothing grows back

*[12](../SOURCES.md#F-73622a0de3) hypotheses — [1](../SOURCES.md#F-5166c930a6) blocked on a fetch, [4](../SOURCES.md#F-4facca4cbd) unscoreable, [7](../SOURCES.md#F-c0a12d6978) needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[T1](../HYPOTHESES.md "Sulphide intrusion, gated by light")** | Sulphide intrudes when light cannot power the defence | needs an experiment | tissue sulphide, porewater sulphide and light at the bed on the same plants; a research method, not monitoring |
| **[T2](../HYPOTHESES.md "Loss of the sulphide-detoxifying symbiosis")** | Lucinid bivalves absent -> sulphide detoxification lost | blocked on a fetch | **infaunal bivalve records within seagrass beds are in ODA bundfauna if anyone looks** |
| **[T3](../HYPOTHESES.md "Wasting disease with stress-modulated virulence")** | Labyrinthula virulence rises with host stress | needs an experiment | Labyrinthula screening in Danish eelgrass; not routine |
| **[T4](../HYPOTHESES.md "Marine replant failure: negative sediment feedback")** | Replanting fails on conditioned sediment and succeeds on clean | needs an experiment | **restoration trials with sediment treatments.** A handful of Danish eelgrass trials exist; this design does not |
| **[T5](../HYPOTHESES.md "Loss of sediment suppressiveness")** | Suppressive sediment resists invasion; degraded does not | needs an experiment | sediment microbial composition **and transfer experiments** — neither exists |
| **[T6](../HYPOTHESES.md "Enrichment dissolving the partnership")** | Enrichment dissolves the partnership by making it unnecessary | needs an experiment | rhizosphere community composition along the gradient |
| **[T7](../HYPOTHESES.md "Anaerobic phytotoxins other than sulphide")** | Anaerobic phytotoxins beyond sulphide | needs an experiment | porewater chemistry beyond the standard nutrients |
| **[T8](../HYPOTHESES.md "Anaerobic conditions select the pathogens")** | Anaerobia selects for the pathogens | **unscoreable** | **essentially no marine oomycete or labyrinthulid surveys** |
| **[T9](../HYPOTHESES.md "Pathogen and partner are not kinds of organism")** | Pathogen and partner are not kinds of organism | **unscoreable** | host-associated microbial and viral community data through a stress gradient — **absent for every Danish marine species** |
| **[T12](../HYPOTHESES.md "Defence is outsourced, because the host cannot win the race")** | Defence is outsourced; a biocide disarms the host | **unscoreable** | host-associated community data with matched disease outcomes — absent |
| **[T11](../HYPOTHESES.md "Occupancy is the function")** | Occupancy is the function; the empty niche is the risk | needs an experiment | **challenge experiments on intact versus disturbed communities.** Standard in medical and soil microbiology, not applied in Danish marine work |
| **[T10](../HYPOTHESES.md "Removing an organism whose role is unknown is not neutral")** | Removing an unknown-role organism is not neutral | **unscoreable** | **baseline composition before intervention is almost never collected**, which makes the comparison impossible by construction |

### S. The land side: the medium, not the input

*[6](../SOURCES.md#F-2104dff7ad) hypotheses — [1](../SOURCES.md#F-4c72183da7) testable now, [3](../SOURCES.md#F-3adc3860b2) blocked on a fetch, [1](../SOURCES.md#F-cacfb07b20) blocked on resolution, [1](../SOURCES.md#F-716b15c6a7) needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[S1](../HYPOTHESES.md "Retention is a property of the medium and varies by an order of magnitude")** | Retention varies an order of magnitude with the medium | blocked on a fetch | the soil map exists; the paired drainage validation largely does not |
| **[S2](../HYPOTHESES.md "Phosphorus saturation, and legacy leakage")** | Legacy soil P leaks after inputs stop | blocked on a fetch | **Denmark holds soil P status and it is not carried into the marine argument** — a fetch and a join |
| **[S3](../HYPOTHESES.md "Sorption is hysteretic - a ratchet on the land side too")** | Sorption is hysteretic — a ratchet on the land side too | needs an experiment | sorption-desorption experiments on Danish soils; standard method |
| **[S4](../HYPOTHESES.md "Total is not available")** | Total P is not available P | blocked on a fetch | fractionated sediment P — sedimentkemi `Emne_12_19` carries Fe-adsorbed P at [39 stations](../SOURCES.md#F-2b3e2eacf3) |
| **[S5](../HYPOTHESES.md "Buffering scales with the volume of reactive medium")** | Buffering scales with the volume of reactive medium | blocked on resolution | bathymetry is held; **sediment thickness is not** |
| **[S6](../HYPOTHESES.md "Retention capacity is saturable, so the coefficient is not constant")** | The retention coefficient is not constant — it saturates | **testable now** | the register's own Needs line: **'Requires no new measurement at all'** — the same catchment flux data split by period. Blocked only insofar as the flux series is the unfetched input |

### R. Decay, and the community that does it

*[11](../SOURCES.md#F-29f7a52cc5) hypotheses — [3](../SOURCES.md#F-4e8b726836) blocked on a fetch, [1](../SOURCES.md#F-0dcf689add) blocked on resolution, [1](../SOURCES.md#F-8f5ab0863b) unscoreable, [6](../SOURCES.md#F-da712995c6) needs an experiment.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[R11](../HYPOTHESES.md "Marine fungi, the decomposers nobody counts")** | Marine fungi decompose and nobody counts them | **unscoreable** | **essentially no marine fungal surveys in Danish waters** |
| **[R1](../HYPOTHESES.md "The C:N threshold, and fat as a nitrogen sink")** | C:N of discharged material decides whether it is a sink | blocked on a fetch | **both numbers exist in discharge monitoring and the ratio is never formed** — a fetch and one arithmetic step |
| **[R2](../HYPOTHESES.md "Priming of the old sediment pool by fresh carbon")** | Fresh carbon primes the old sediment pool | needs an experiment | sediment incubation with and without labile addition |
| **[R3](../HYPOTHESES.md "The decay relay stalls when a stage is removed")** | The decay relay stalls when a stage is removed | blocked on a fetch | sediment organic content with matched fauna — **both in ODA and never analysed together** |
| **[R4](../HYPOTHESES.md "Nitrogen enrichment retards decay of the recalcitrant fraction")** | N enrichment retards decay of the recalcitrant fraction | needs an experiment | litter-bag or incubation studies with characterised organic fractions |
| **[R5](../HYPOTHESES.md "The terminal electron acceptor cascade, and why salt changes it")** | The electron-acceptor cascade shifts with salinity | blocked on resolution | porewater sulphide and methane by station; rarely measured |
| **[R6](../openproblems/R6.md "Sulphide locks the iron that would hold the phosphate")** | Sulphide locks the iron that would hold the phosphate | needs an experiment | **classified experiment-constructive** in `openproblems/R6.md`. NOVA teknisk anvisning `kap. 14` ran exactly this method 1998-2003 and it was discontinued |
| **[R7](../HYPOTHESES.md "Estuarine flocculation deposits river carbon at the coast")** | Flocculation deposits river carbon at the coast | blocked on a fetch | sediment organic content with matched salinity — the register calls it obtainable |
| **[R8](../HYPOTHESES.md "Lipids are less soluble in seawater")** | Lipids are less soluble in seawater, so they deposit | needs an experiment | lipid fractionation by salinity |
| **[R9](../HYPOTHESES.md "Home-field advantage, and novel material")** | Novel material decays slower — no home-field advantage | needs an experiment | comparative decomposition assays |
| **[R10](../HYPOTHESES.md "Osmotic discontinuity for the decomposers themselves")** | Osmotic discontinuity stalls the decomposers themselves | needs an experiment | cross-transplant incubations |

### L. The baseline and the counterfactual

*[6](../SOURCES.md#F-0e6fbfe636) hypotheses — [2](../SOURCES.md#F-2587fccf66) testable now, [4](../SOURCES.md#F-3b1387751f) blocked on a fetch.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[L6](../HYPOTHESES.md "The degraded bed is classified as its own habitat type")** | The degraded bed is classified as its own habitat type | blocked on a fetch | historical seabed charts, old fisheries records and trawling effort — **the history a classification key discards** |
| **[L1](../HYPOTHESES.md "The reference condition never existed")** | The reference condition never existed | blocked on a fetch | dated sediment cores with diatom and pigment stratigraphy; some exist and are not what the reference derives from |
| **[L2](../HYPOTHESES.md "The reference is a model output treated as a fact")** | The reference is a model output treated as a fact | **testable now** | **Archival, not statistical.** The reference model's assumptions and the indsatsbehov recomputed across their plausible range; DCE reports are public, text-extractable PDFs |
| **[L3](../hypodrafts/L3.md "The trend depends on the start year")** | The trend depends on the start year | **testable now** | **Draft exists and was run** (`hypodrafts/L3.md`). [406 admissible windows; sign-flipping occurs in 100% of matched-AR nulls](../SOURCES.md#F-4454983787), so [L3](../hypodrafts/L3.md "The trend depends on the start year")'s strong reading is **not established** for bed oxygen |
| **[L4](../HYPOTHESES.md "Recovery is blocked by something other than the driver")** | Recovery is blocked by something other than the driver | blocked on a fetch | restoration trials with controls — a handful exist in Denmark and are not treated as decisive |
| **[L5](../HYPOTHESES.md "The reference sites are not references")** | The reference sites are not references | blocked on a fetch | trawling, dumping and contaminant coverage for the areas used as references. The trawling layer is a [23 MB](../SOURCES.md#F-1e3ba73c87) open fetch |

### I. Observation and measurement

*[7](../SOURCES.md#F-f540337e22) hypotheses — [6](../SOURCES.md#F-c53557ff04) testable now, [1](../SOURCES.md#F-812d915348) blocked on resolution.*

| id | consequence | class | blocker |
|---|---|---|---|
| **[I1](../hypodrafts/I1.md "Changing station network")** | Apparent change concentrates where the network changed | **testable now** | **Draft exists** (`hypodrafts/I1.md`). [64 stations present in all eight 5-year eras, 8,485 station-months](../SOURCES.md#F-ff324d5307). The register cannot supply lifespans; presence comes from the observation record |
| **[I2](../HYPOTHESES.md "Changing analytical method")** | Step changes at probe changeover, shared across geography | blocked on resolution | **`SondeNr` is `999` on [25.6](../SOURCES.md#F-18d47162ce)% of rows** in the whole CTD extract. The rest carries [81](../SOURCES.md#F-9c2bc4c9bc) identified probes and is where [I2](../HYPOTHESES.md "Changing analytical method") is testable |
| **[I3](../hypodrafts/I3.md "Changing sampling frequency and season")** | Apparent severity scales with visit count and window | **testable now** | **Draft exists** (`hypodrafts/I3.md`). The count-and-window half is fully testable; **the diel half is carved out as `class 6`, unscoreable** |
| **[I4](../HYPOTHESES.md "Changing indicator definition")** | Status shifts at definition changes with no measurement change | **testable now** | the definitions with their adoption dates — archival, and the recomputation runs on held data |
| **[I5](../HYPOTHESES.md "Changing correction factors")** | Trends present in corrected but not original results | **testable now** | **Held.** `KorrektionsFaktor` is exactly one on [94.76](../SOURCES.md#F-f5eeb40780)% of rows, and Original differs from Korrigeret on [5.21](../SOURCES.md#F-0146c2b052)% of those carrying both |
| **[I6](../HYPOTHESES.md "Changing custodian")** | Discontinuities at 2007 shared across stations that changed hands | **testable now** | `Dataleverandoer` and `TekniskAnvisningAnvendt` are in the raw record — but over the whole CTD extract they carry [2](../SOURCES.md#F-69e562d658) and [1](../SOURCES.md#F-9530b4b76f) distinct values, so the contrast may be empty |
| **[I7](../HYPOTHESES.md "Batch defects in ingest or processing")** | Implausible values cluster in time across unrelated custodians | **testable now** | **Worked case already found**: [11](../SOURCES.md#F-c8b8b1dcfd) station-months at [6](../SOURCES.md#F-4ed890d0d9) stations, [4 custodian prefixes, May-June 2005](../SOURCES.md#F-341654246a), recorded in `flags.json` |

---

## What the shape of it says

### Half the field is not blocked on money or effort

**[61](../SOURCES.md#F-15045ed0fb) of [166](../SOURCES.md#F-4196d405de) ([37](../SOURCES.md#F-00ac661b28)%) are blocked on a fetch**, and most of those fetches are
small. The ones that need no credentials at all: the ICES/HELCOM trawling layer ([23 MB](../SOURCES.md#F-ec39be7864), `CC BY 4.0`), the three ODA
vegetation and fauna topics (three one-line `TOPICS` entries), OBIS phytoplankton via the eMoF extension (open
REST), DMI tide gauges and wind (no key since March 2026), `Sentinel-1` SAR, and ICES stock assessments.
**A day of fetching would move a large fraction of this table.**

### One fetch unblocks the most

**ODA `vandkemi` (`Emne_10_11`)** is the single highest-value fetch: it carries nitrogen,
phosphorus, silicate, ammonium and chlorophyll, and it is named in the blocker for **[A1](../hypodrafts/A1.md "Danish land-based nitrogen load"), [A2](../HYPOTHESES.md "Phosphorus load"), [A5](../HYPOTHESES.md "Advected nutrients from outside Denmark"), [A7](../openproblems/A7.md "Sediment nutrient regeneration"), [B4](../HYPOTHESES.md "Riverine particulate organic carbon"), [E2](../HYPOTHESES.md "Nitrification demand"), [E11](../HYPOTHESES.md "Ammonia toxicity"), [K1](../hypodrafts/K1.md "Silicon depletion and the diatom-to-flagellate shift"), [K2](../HYPOTHESES.md "Stoichiometric imbalance decides who grows")** — [9](../SOURCES.md#F-b5ea195365) hypotheses, including the entire nutrient-limitation
argument. When this was written it was also the fetch `fetch_oda.py` advertised in its docstring and did not
implement. Second is **ODA bundfauna (`Emne_3_180`)** at [7](../SOURCES.md#F-7495c59f85) — [D11](../HYPOTHESES.md "Stabilisers against destabilisers"), [F1](../HYPOTHESES.md "Loss of filter feeders"), [F2](../HYPOTHESES.md "Loss of bioturbators"), [H3](../HYPOTHESES.md "Loss of resilience through diversity loss"), [K14](../HYPOTHESES.md "Genetic and functional diversity depletion"), [T2](../HYPOTHESES.md "Loss of the sulphide-detoxifying symbiosis"), [W4](../HYPOTHESES.md "Allee effects at low density").

Note what that means for group A. **Not one hypothesis in the nutrient group is testable
now.** The group the entire public argument rests on is the group whose data this project
had not fetched.

### The largest single blocking dimension is not nutrients

**[12](../SOURCES.md#F-e661888b83) hypotheses are unscoreable for one missing dimension: microbial, viral and fungal
community composition** — of [E13](../HYPOTHESES.md "Biocides that remove the decomposers themselves"), [E17](../HYPOTHESES.md "The microbiome is the exposed organ"), [F8](../HYPOTHESES.md "Microbial shift to fast-growing forms"), [F11](../HYPOTHESES.md "Viral lysis and the viral shunt"), [F12](../HYPOTHESES.md "The micropathogens nobody catalogues"), [F13](../HYPOTHESES.md "The organisms that fall between the folk categories"), [F14](../HYPOTHESES.md "Viruses as structure, not only as mortality"), [J8](../HYPOTHESES.md "Bacterial exopolymer from fast-growing communities"), [R11](../HYPOTHESES.md "Marine fungi, the decomposers nobody counts"), [T5](../HYPOTHESES.md "Loss of sediment suppressiveness"), [T6](../HYPOTHESES.md "Enrichment dissolving the partnership"), [T8](../HYPOTHESES.md "Anaerobic conditions select the pathogens"), [T9](../HYPOTHESES.md "Pathogen and partner are not kinds of organism"), [T12](../HYPOTHESES.md "Defence is outsourced, because the host cannot win the race"), all but [2](../SOURCES.md#F-5fe1f1a7ae), which need an experiment instead.
Not one Danish marine station counts viruses, sequences a microbial community, or surveys
fungi. That is a whole functional layer with no column anywhere, and it blocks more of this
register than any other single absence.

A second cluster of [7](../SOURCES.md#F-7a78427d2e) is **toxicant concentration in a marine matrix** — [E7](../openproblems/E7.md "Pesticides and degradation products"), [E8](../HYPOTHESES.md "Pharmaceuticals and personal care products"), [E18](../HYPOTHESES.md "Tyre-wear transformation products"), [J3](../HYPOTHESES.md "Surfactants from detergents and personal care"), [J4](../HYPOTHESES.md "Sunscreen and UV filters"), [K8](../HYPOTHESES.md "The narrow window between deficient and toxic"), [K9](../HYPOTHESES.md "Selenium") —
where the national hazardous-substance layer turns out to hold [256](../SOURCES.md#F-aee5a58e2f) stations, not one of them coastal.
Together those two dimensions account for **[19](../SOURCES.md#F-0df9013823) of the [40](../SOURCES.md#F-198b20fb90) unscoreable** ([48](../SOURCES.md#F-7270c02bc1)%), and neither is expensive to start
measuring. eDNA and Alcian-blue TEP are cheap standard methods; the register says so itself in several places.

### [24](../SOURCES.md#F-935d9e0296)% of the field cannot be scored at all, and that is the finding

**[40](../SOURCES.md#F-198b20fb90) of [166](../SOURCES.md#F-4196d405de) ([24](../SOURCES.md#F-935d9e0296)%) are unscoreable** — the deciding dimension has no
column and never did. Add the [20](../SOURCES.md#F-64bb5d44db) that need an experiment and **[36](../SOURCES.md#F-2cc76f7f45)% of the hypothesis field is
beyond reach of any reanalysis of existing data.** No amount of cleverness with the archive
touches them.

This is the number that matters for how the whole argument should be read. When a public
debate settles on nutrients, it is not because nutrients won a contest against the
alternatives. **It is because nutrients are in group A, and group A has a monitoring
programme.** [60](../SOURCES.md#F-38d4f3aa11) of these hypotheses have never been in a position to compete.

### Where the archive is strong

Where most hypotheses are testable now: **I** ([6](../SOURCES.md#F-c53557ff04) of [7](../SOURCES.md#F-f540337e22)), **C** ([5](../SOURCES.md#F-0596b7e6b1) of [9](../SOURCES.md#F-89669b4a5d)).
**C** (physical resupply) is next at [5](../SOURCES.md#F-0596b7e6b1) of [9](../SOURCES.md#F-89669b4a5d),
because temperature, salinity, depth and wind are exactly what a CTD and a weather reanalysis
give you.

The pattern across groups is blunt: **this archive can see physics and it cannot see biology.**
Groups C, G, Z and I hold most of the testable-now entries. Groups E, F, J, T and R — chemistry,
biological structure, films, sediment sickness, decay — hold almost none, and hold nearly all
of the unscoreable and experimental ones.

### An honest caveat about this table

The classification is mine and is itself an untested partition, exactly as the [17](../SOURCES.md#F-b36383859a) groups are
(PLAN.md says so of them). Two judgements are load-bearing and contestable: I treated *not
fetched but fetchable* as **blocked on a fetch** rather than unscoreable even where nobody has
confirmed the topic contains what its name suggests; and I treated *measured somewhere in the
world but not in Denmark* as unscoreable **for this archive**, which is a statement about
Denmark's monitoring rather than about nature. The [3](../SOURCES.md#F-6f2641deb0) entries I could not place at all are
marked *not established* rather than guessed.

And per [KNOWN_AND_UNKNOWN.md](../KNOWN_AND_UNKNOWN.md): **every "not measured" in this table
should be read as "not found by a search whose sensitivity nobody has characterised."** Six
things this project called absent turned out to exist in one day. The unscoreable column is
an upper bound on what is missing, not a measurement of it.
