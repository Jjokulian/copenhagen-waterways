# Triage of the hypothesis field

<span class="claim" data-claim="C-TR-ALL">This page puts **all [166](../SOURCES.md#F-4196d405de) lettered hypotheses in [HYPOTHESES.md](../HYPOTHESES.md)** each in exactly one class, with the specific blocker.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-ALL "What this claim rests on")</sup>

<span class="claim" data-claim="C-TR-ENTRIES">[18](../SOURCES.md#F-2e51f8b7c4) of them have a draft or an open-problem page of their own, and their identifiers link to it.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-ENTRIES "What this claim rests on")</sup> <span class="claim" data-claim="C-TR-NOTRESULT">A classification says what testing a hypothesis would need and whether that is held here; it is not a test result.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-NOTRESULT "What this claim rests on")</sup>

<span class="claim" data-claim="C-TR-COUNTS">Counted over the rows, restricted to the identifiers the register holds, the classes stand at:</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-COUNTS "What this claim rests on")</sup>

| class | n | share |
|---|---:|---:|
| **testable now** | [23](../SOURCES.md#F-e786dfc514) | [14](../SOURCES.md#F-aff8947a9f)% |
| blocked on a fetch | [62](../SOURCES.md#F-15045ed0fb) | [37](../SOURCES.md#F-00ac661b28)% |
| blocked on resolution | [15](../SOURCES.md#F-ab9e2895d5) | [9](../SOURCES.md#F-0d520cad5c)% |
| **unscoreable** | [42](../SOURCES.md#F-198b20fb90) | [25](../SOURCES.md#F-935d9e0296)% |
| needs an experiment | [20](../SOURCES.md#F-64bb5d44db) | [12](../SOURCES.md#F-42f0fd7709)% |
| not established | [4](../SOURCES.md#F-6f2641deb0) | [2](../SOURCES.md#F-3307597d2e)% |
| | **[166](../SOURCES.md#F-4196d405de)** | |

<span class="claim" data-claim="C-TR-CLASSES">**Class definitions.** *Testable now* — consequence, a source in hand, and a null computable
under the constraint imposed. *Blocked on a fetch* — named, with whether it needs credentials.
*Blocked on resolution* — needs depth, sub-monthly time, per-measurement position, or the
measurement-level store. *Unscoreable* — the deciding dimension has no column and never did;
**this is not a refutation**. *Needs an experiment* — no observational design reaches it.
*Not established* — I could not tell, and say so rather than guess.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-CLASSES "What this claim rests on")</sup>

---

## The table

<span class="claim" data-claim="C-TR-RULE">Each row's class is a judgement on its blocker: what the row's consequence needs, and whether this project holds it. A blocker says only what the source register (`data/manual/data_sources*.json`, the record of what each source holds and what its searches found), the files held here and, for the hypotheses that waited on the water-chemistry extract, `scripts/rescore.py` say. *Not found* means not found in the sources the register surveyed.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-RULE "What this claim rests on")</sup>

### A. Nutrient-driven production in place

<span class="claim" data-claim="C-TR-N-A">*[10](../SOURCES.md#F-b17d38223a) hypotheses — [8](../SOURCES.md#F-cd21100ace) blocked on a fetch, [1](../SOURCES.md#F-0528ea00b7) unscoreable, [1](../SOURCES.md#F-1bbb2adcef) not established.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-A "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[A1](../hypodrafts/A1.md "Danish land-based nitrogen load")** | Load up -> summer chlorophyll up -> bottom <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> down, per area per month | blocked on a fetch | Chlorophyll and oxygen are in the held water-chemistry extract. The land load is on ODA's `STOFTRANSPORT` and `TILFOERSEL` topics, which need a **code change**: `fetch_oda.py`'s `run()` opens the Hav topic only. Draft exists (`hypodrafts/A1.md`) |
| **[A2](../HYPOTHESES.md "Phosphorus load")** | P flux up -> spring chlorophyll up | blocked on a fetch | Total P, ortho-P and chlorophyll are in the held extract; the river P flux is on `STOFTRANSPORT`, the same unreached topic |
| **[A3](../HYPOTHESES.md "Atmospheric deposition on the sea surface")** | Deposition over sea up -> production up where land load is low | blocked on a fetch | Monthly gridded deposition (EMEP) is open and not fetched; Denmark's DEHM product is published as annual totals per sea area, and the organic-N fraction the hypothesis names is in none of the products the source register found |
| **[A10](../HYPOTHESES.md "Exhaust-treatment reagent: nitrogen added to remove nitrogen")** | Urea-derived N from exhaust treatment enters the budget it abates | not established | A mass-balance argument, not an observable here: roadside ammonia, the measurement it rests on, sits behind interfaces that refused automated access. Whether any reaches the sea is not established |
| **[A4](../HYPOTHESES.md "Point-source discharge of nutrients")** | Plant discharge down at upgrade date -> local N down stepwise | blocked on a fetch | Per-plant discharge with upgrade dates: the source register found per-plant loads as annual totals only, and upgrade dates in no source. `punkt_rens_udl.geojson` gives the plants' positions and approved capacity, no discharges |
| **[A5](../HYPOTHESES.md "Advected nutrients from outside Denmark")** | Nutrients at Belt/Sound sections co-vary with inner-water state | blocked on a fetch | Volume transport at the Belt and Sound sections, which the hypothesis itself names as a need: the source register found no open series of it. The concentration half is held - total N, ortho-P and silicon are all in the water-chemistry extract, and [30](../SOURCES.md#F-38f2d8758b) of its stations in Storebælt, Lillebælt and Øresund carry all three |
| **[A6](../HYPOTHESES.md "Submarine groundwater discharge")** | SGD delivers N where no stream does | **unscoreable** | **No coastwide survey of submarine groundwater discharge** was found; what exists is site studies in fjords |
| **[A7](../openproblems/A7.md "Sediment nutrient regeneration")** | Bottom-water DIP rises in summer without a matching river input | blocked on a fetch | Ortho-P and oxygen are in the held extract ([650](../SOURCES.md#F-53c0aaacfb) stations carry ortho-P), enough for the weak form. The *without a matching river input* clause needs river input from `STOFTRANSPORT`, unreached; direct benthic flux measurement was found only on a Skagerrak cruise |
| **[A8](../HYPOTHESES.md "Marine aquaculture")** | Sediment near pens enriched vs matched controls | blocked on a fetch | Per-farm production and feed by month: the source register found a national annual tonnage by farm type only. `punkt_havdam_udl.geojson` gives farm positions only |
| **[A9](../HYPOTHESES.md "Nitrogen fixation")** | Cyanobacteria abundance up where N:P is low | blocked on a fetch | Phytoplankton species counts: collected under NOVANA and held in VanDa, whose data endpoints refused access, so they need **credentials**; not held here. No N-fixation rate measurement for Danish water was found |

### B. Oxygen demand that arrived already made

<span class="claim" data-claim="C-TR-N-B">*[8](../SOURCES.md#F-14ca135518) hypotheses — [1](../SOURCES.md#F-6b6b8f73b9) testable now, [4](../SOURCES.md#F-1ec2922bf1) blocked on a fetch, [1](../SOURCES.md#F-36488d1ed1) blocked on resolution, [2](../SOURCES.md#F-a7ec13c7e5) unscoreable.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-B "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[B1](../hypodrafts/B1.md "Combined sewer overflow")** | Bathing indicator up downstream of combined outfalls after rain, not separate ones | **testable now** | **Draft exists** (`hypodrafts/B1.md`). It uses the combined-versus-separate class and a critical rainfall depth from each structure's storage, not modelled volume: per-event overflow volume is in no national source |
| **[B2](../HYPOTHESES.md "Separate stormwater")** | First-flush concentration x volume exceeds the annual-total assumption | blocked on resolution | Event-resolved concentration and volume at the outfall. Annual totals over [16,185](../SOURCES.md#F-f88f6ae3cd) separate stormwater outfalls cannot test a first-flush claim |
| **[B3](../HYPOTHESES.md "Treatment plant organic load")** | Plant COD/BOD up -> local oxygen demand up | blocked on a fetch | Per-plant monthly COD/BOD: the source register found per-plant BOD only, and only as annual totals |
| **[B4](../HYPOTHESES.md "Riverine particulate organic carbon")** | Riverine POC up -> sediment organic content up at the receiving coast | blocked on a fetch | The held extract is the marine topic. Suspended solids, their loss on ignition and COD at the stream stations, beside total N, are on ODA's `STOFTRANSPORT` topic, not fetched; so is sediment organic content at the receiving coast |
| **[B5](../HYPOTHESES.md "Industrial organic discharge")** | Industrial organic load co-locates with local demand | blocked on a fetch | Per-site loads: the source register found annual per-company loads and the EU industrial-emissions portal, both annual; not fetched |
| **[B6](../HYPOTHESES.md "Harbour and fish-processing waste")** | Harbour water shows a demand signature the open coast does not | **unscoreable** | **No water quality inside harbour basins** in any open source the register surveyed; bathing-water sampling measures faecal bacteria only |
| **[B7](../HYPOTHESES.md "Shipping discharges")** | Scrubber and bilge discharge along tracks -> local demand | blocked on a fetch | AIS tracks and vessel density are open; **no source for discharge volumes** was found, so the second half is unscoreable |
| **[B8](../HYPOTHESES.md "Direct manure and slurry entry")** | Incident-linked slurry entry -> local spike | **unscoreable** | **No public environmental incident register with date and location** was found |

### C. Physical control of resupply

<span class="claim" data-claim="C-TR-N-C">*[9](../SOURCES.md#F-89669b4a5d) hypotheses — [5](../SOURCES.md#F-0596b7e6b1) testable now, [2](../SOURCES.md#F-f5117cda81) blocked on a fetch, [2](../SOURCES.md#F-1ef9a0c61b) blocked on resolution.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-C "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[C1](../hypodrafts/C1.md "Stratification strength")** | Hypoxia is near-zero in well-mixed water at matched depth | **testable now** | **Draft exists** (`hypodrafts/C1.md`). [133,509](../SOURCES.md#F-48d6afcb0d) station-days with at least [4](../SOURCES.md#F-6c91311fd6) depth levels of T and S plus bottom oxygen, from the raw CTD |
| **[C2](../HYPOTHESES.md "Wind work")** | Wind work up -> stratification broken -> bottom <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> up | **testable now** | Hourly wind held (`data/raw/weather/`, [31](../SOURCES.md#F-bec24964f0) years) joined to CTD profiles |
| **[C3](../HYPOTHESES.md "Residence time")** | Long residence time -> lower <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> at matched load | blocked on resolution | No per-area residence time is published; it must be modelled, and the held current field is a coarse global model that `currents.py` itself says does not resolve the Danish straits |
| **[C4](../hypodrafts/C4.md "Baltic inflow events")** | Inflow -> deep <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> pulse, lagged, ordered Belts->Arkona->Bornholm->Gotland | **testable now** | **Draft exists** (`hypodrafts/C4.md`). The MBI indicator files are held; the Belt section transports are not open |
| **[C5](../HYPOTHESES.md "Freshwater discharge buoyancy")** | Freshwater pulse -> stratification up -> bottom <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> down | blocked on a fetch | Freshwater discharge per stream station is open (Vandah) and monthly freshwater input per water body is on `TILFOERSEL`; neither is fetched |
| **[C6](../hypodrafts/C6.md "Water temperature and solubility")** | Deficit vs saturation separates solubility from consumption | **testable now** | **Draft exists** (`hypodrafts/C6.md`). <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span>, T and S near the bed are in the CTD record |
| **[C7](../HYPOTHESES.md "Bathymetry, sills and depth")** | Deeper and silled areas go hypoxic at lower load | **testable now** | Bottom depth per visit in `maaledybde` ([151,203](../SOURCES.md#F-5683df4d6c) rows); sill geometry from `marin_overordnet.geojson` |
| **[C8](../HYPOTHESES.md "Constructed change to circulation")** | Construction changed exchange -> step in local state at the works date | blocked on resolution | Works dates and footprints: dated for offshore wind only, the rest found only as narrative pages; needs them joined to sub-monthly state |
| **[C9](../HYPOTHESES.md "Sea level and tidal change")** | Sea level and tidal change alter exchange | blocked on a fetch | DMI oceanObs tide gauges: an open API, unauthenticated in the register's testing; not fetched |

### D. Physical disturbance of the bed

<span class="claim" data-claim="C-TR-N-D">*[11](../SOURCES.md#F-374e783817) hypotheses — [1](../SOURCES.md#F-7b66b1ce10) testable now, [9](../SOURCES.md#F-a7d44831d4) blocked on a fetch, [1](../SOURCES.md#F-ada657e8a8) needs an experiment.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-D "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[D1](../hypodrafts/D1.md "Bottom trawling")** | Effort up -> near-bed <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> down, strongest on fine substrate | blocked on a fetch | The monthly gear-specific layer is not public; the ICES swept-area-ratio product is open, **no credentials**, annual, and not fetched. Draft exists (`hypodrafts/D1.md`) |
| **[D2](../HYPOTHESES.md "Navigation dredging")** | Dredging event -> local turbidity and demand spike | blocked on a fetch | Dredging permits with dates, volumes and locations: not obtainable programmatically since the permit archive moved |
| **[D3](../HYPOTHESES.md "Dredged-material dumping")** | A dumping ground shows a signature its surroundings do not | blocked on a fetch | `klappladser.geojson` gives the grounds. Per-event disposed tonnage per ground is in OSPAR's disposal records, not fetched |
| **[D4](../HYPOTHESES.md "Sand and gravel extraction")** | An extraction area differs from matched unextracted seabed | blocked on a fetch | `raastofomr.geojson` gives the areas and their permitted quantities; extracted volume by area and year is published for the shared areas only, and the endpoint that holds the rest refused access |
| **[D5](../HYPOTHESES.md "Cable and pipeline works")** | Cable route works -> local disturbance signature | blocked on a fetch | Route and installation-date registers: no Danish cable layer was found, so it would have to be compiled from project pages |
| **[D6](../HYPOTHESES.md "Anchoring and propeller wash")** | Anchorage seabed differs from matched non-anchorage | blocked on a fetch | AIS anchoring events: derivable from the open raw AIS; no open anchorage polygons were found |
| **[D7](../hypodrafts/D7.md "Storm-driven resuspension")** | Transparency deficit lags critical bed shear, only in shallow water | **testable now** | **Draft exists** (`hypodrafts/D7.md`). `Turbiditet` [1,076,915](../SOURCES.md#F-85266abfd1) rows in the CTD extract, wind held. The monthly panel cannot resolve events, so the draft runs on the dated raw record |
| **[D8](../HYPOTHESES.md "Loss of biostabilisation, and the mobile bed")** | A biostabilised bed resists erosion to higher shear | needs an experiment | **Erodibility measurement (cohesive strength meter or flume) with matched surface-sediment chlorophyll.** Neither is in Danish monitoring |
| **[D9](../HYPOTHESES.md "Fertility islands lost to homogenisation")** | Within-area fauna variance collapses under homogenisation | blocked on a fetch | ODA bundfauna, not fetched. The source register found replicate grabs per visit, each with its own position, so within-station variance is computable |
| **[D10](../HYPOTHESES.md "Winnowing and armouring")** | Grain size coarsens where fines are winnowed | blocked on a fetch | ODA sediment grain size as a time series. `seabed_sediment_dk.gpkg` is a static [108](../SOURCES.md#F-5c1dccef56)-polygon mosaic from [19](../SOURCES.md#F-5a9ac13e75) mapping programmes, at scale denominators from [5,000](../SOURCES.md#F-0827f1f9d3) to [500,000](../SOURCES.md#F-d20841b0ec) |
| **[D11](../HYPOTHESES.md "Stabilisers against destabilisers")** | Stabiliser:destabiliser ratio predicts bed state | blocked on a fetch | ODA bundfauna, then a desk trait assignment; erodibility to test the ratio against is measured nowhere in Denmark |

### E. Chemical demand and toxicity

<span class="claim" data-claim="C-TR-N-E">*[20](../SOURCES.md#F-4ea953ea01) hypotheses — [1](../SOURCES.md#F-8e56e09dff) testable now, [4](../SOURCES.md#F-4c1023c5f4) blocked on a fetch, [2](../SOURCES.md#F-8693013085) blocked on resolution, [10](../SOURCES.md#F-6534048aeb) unscoreable, [1](../SOURCES.md#F-52cfe2e72d) needs an experiment, [2](../SOURCES.md#F-0f8c435d44) not established.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-E "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[E1](../HYPOTHESES.md "Sulphide oxidation")** | Sulphide oxidation consumes <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> where redox is low | blocked on a fetch | Sedimentkemi `Emne_12_19`, not fetched; no sediment redox or sulphide monitoring series was found |
| **[E2](../HYPOTHESES.md "Nitrification demand")** | Nitrification demand scales with ammonium | **testable now** | Ammonium and oxygen by station, date and depth are both in the held water-chemistry extract. The nitrification rate is not measured, so the demand is inferred from the stoichiometry |
| **[E3](../HYPOTHESES.md "Iron and manganese oxidation")** | Fe/Mn oxidation consumes <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> at the redox front | needs an experiment | Porewater chemistry, very rare, and the mechanism is millimetre-scale |
| **[E4](../HYPOTHESES.md "Methane oxidation")** | Methane oxidation consumes <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> above seeps | **unscoreable** | **No Danish coastal methane flux record** beyond an isolated point measurement was found |
| **[E5](../HYPOTHESES.md "Direct chemical oxygen demand of discharges")** | Discharge COD carried into a marine budget changes the balance | blocked on a fetch | Per-outlet COD: measured in discharge monitoring, annually, and never carried through |
| **[E6](../HYPOTHESES.md "Biocides and antifoulants")** | Antifoulant concentration up -> decomposer function down | **unscoreable** | **Sediment measured at [5](../SOURCES.md#F-8bf5ff138f) of [256](../SOURCES.md#F-aee5a58e2f) national hazardous-substance stations — and not one is coastal** ([152](../SOURCES.md#F-4e20821308) lake, [104](../SOURCES.md#F-53860b0f29) river, [0](../SOURCES.md#F-929f2dcc25) coastal; `sw_mfs_tilstand.geojson`) |
| **[E7](../openproblems/E7.md "Pesticides and degradation products")** | Pesticide load co-varies with N and acts separately | **unscoreable** | **No toxicant column in [53,710,760](../SOURCES.md#F-4df017f985) CTD rows, none in [679,422](../SOURCES.md#F-7769a94f7a) station-months.** Current-use pesticides are measured in streams; the marine programme measures legacy organochlorines, in fish |
| **[E8](../HYPOTHESES.md "Pharmaceuticals and personal care products")** | Pharmaceutical residues alter microbial function | **unscoreable** | Pharmaceuticals are measured in streams and in effluent, never in marine water or sediment, in the sources surveyed |
| **[E9](../HYPOTHESES.md "PFAS and persistent novo-chemicals")** | PFAS persists and accumulates in biota | blocked on a fetch | PFAS in fish liver (ODA, ICES DOME), not fetched; no marine sediment PFAS dataset was found |
| **[E10](../HYPOTHESES.md "Heavy metals")** | Metal concentration up -> benthic function down | blocked on a fetch | ICES DOME's Danish sediment metals stop in 2016, apart from a 2022 campaign; metals continue in mussel tissue. Not fetched |
| **[E11](../HYPOTHESES.md "Ammonia toxicity")** | Un-ionised ammonia is toxic at high pH and temperature | blocked on resolution | Ammonium and pH are in the held extract, together in [25,988](../SOURCES.md#F-135749f431) bottles. Temperature is on [1,316](../SOURCES.md#F-17cdaab156) of its rows, so the temperature for each bottle comes from the CTD record by station, day and depth, not the same hour |
| **[E12](../HYPOTHESES.md "Hydrogen sulphide toxicity")** | Free sulphide is toxic to fauna above a threshold | blocked on resolution | `Dihydrogensulfid` is [2,601](../SOURCES.md#F-153d19187a) rows and **[2,598](../SOURCES.md#F-906d8ca940) come from the station `93610032`**. Usable for one silled basin, not a series |
| **[E13](../HYPOTHESES.md "Biocides that remove the decomposers themselves")** | Fungicides remove decomposers -> decay stalls | **unscoreable** | **Neither fungicide in marine sediment nor fungal biomass is measured** in the sources surveyed |
| **[E14](../HYPOTHESES.md "Veterinary antiparasitics in manure")** | Antiparasitic residues in manure reach water and act | **unscoreable** | No residue measurement in manure, soil, runoff or sediment was found; sales are public at regional and quarterly resolution, not per herd |
| **[E15](../HYPOTHESES.md "Total biocide load, whatever its source")** | Total biocide load, not per-substance, predicts effect | not established | The national pesticide sales statistics could not be found at any working address and the spray journals were not pursued, so whether a load by catchment can be built is not established |
| **[E16](../HYPOTHESES.md "Conserved targets: 'selective' is a claim about dose")** | High-tonnage compounds act on conserved targets at realistic dose | **unscoreable** | No marine concentration of the high-tonnage compound classes was found; the national status network for them has no coastal station |
| **[E18](../HYPOTHESES.md "Tyre-wear transformation products")** | `6PPD-quinone` is lethal to salmonids at road-runoff concentrations | **unscoreable** | **No `6PPD-quinone` measurement in road runoff or the sea was found**; a national analyte code exists for groundwater and drinking water. Danish sea-trout sensitivity is also unestablished |
| **[E20](../HYPOTHESES.md "Fuel oxygenates and additives")** | Fuel oxygenates reach coastal water | not established | Groundwater monitoring codes some of them; whether any is reported for coastal discharge is not established |
| **[E19](../HYPOTHESES.md "The sentinel species decides what is detectable")** | Standard test batteries miss locally present sensitive species | **unscoreable** | **No test panel of locally present species** was found, so this cannot be checked for any compound; the register records the absence as a lead |
| **[E17](../HYPOTHESES.md "The microbiome is the exposed organ")** | The microbiome is the exposed organ | **unscoreable** | Danish eelgrass host-microbiome datasets exist; **none records biocide exposure or host condition** |

### F. Biological structure and feedback

<span class="claim" data-claim="C-TR-N-F">*[14](../SOURCES.md#F-6d7e02bdc1) hypotheses — [7](../SOURCES.md#F-5dc96c18dc) blocked on a fetch, [1](../SOURCES.md#F-f6b2b6fd6a) blocked on resolution, [6](../SOURCES.md#F-1e069ecf65) unscoreable.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-F "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[F1](../HYPOTHESES.md "Loss of filter feeders")** | Filter-feeder loss -> clearance down -> chlorophyll up | blocked on a fetch | ODA bundfauna, with filter-feeder biomass per grab; shellfish stock surveys are published as whole-fjord tonnages |
| **[F2](../HYPOTHESES.md "Loss of bioturbators")** | Bioturbator loss -> sediment <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> penetration down | blocked on a fetch | ODA bundfauna, species-level abundance and biomass; sediment <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> penetration is measured nowhere in the Danish record, so the fauna side only |
| **[F3](../hypodrafts/F3.md "Loss of eelgrass and macroalgae")** | Cover falls where light is adequate -> the block is not light | blocked on a fetch | ODA `Emne_3_182` aalegraes: a topic `fetch_oda.py` does not list, under the ODA registration it already uses. Draft exists (`hypodrafts/F3.md`) |
| **[F4](../HYPOTHESES.md "Trophic cascade from a removal far away")** | Distant stock removal -> cascade to local grazing | blocked on a fetch | ICES stock assessments are open, **no credentials**; Danish landings by rectangle and month are inside ICES or on request |
| **[F5](../HYPOTHESES.md "Invasive species")** | Invasive arrival -> function change at the arrival date | blocked on a fetch | Species observation records with date and position (OBIS/GBIF, open) |
| **[F6](../HYPOTHESES.md "Jellyfish blooms")** | Jellyfish blooms alter the pathway | **unscoreable** | **No Danish jellyfish monitoring** was found; only citizen sightings with no effort |
| **[F7](../HYPOTHESES.md "Harmful algal blooms specifically")** | HAB species specifically, not chlorophyll, drive the harm | blocked on a fetch | Phytoplankton species counts: collected, and held in VanDa, whose data endpoints refused access; HAB event records carry no coordinates or toxin concentrations |
| **[F8](../HYPOTHESES.md "Microbial shift to fast-growing forms")** | Community shifts to fast-growing forms under enrichment | **unscoreable** | **Microbial community composition is not in the NOVANA programme** |
| **[F9](../HYPOTHESES.md "Disease and parasite mass mortality")** | Disease mortality event -> structural loss | **unscoreable** | No marine mortality event register in open form was found; fish kills are not centrally recorded |
| **[F10](../HYPOTHESES.md "Vertebrate mass mortality")** | Vertebrate mass mortality signals a pathway | blocked on resolution | Stranding records are published as annual summaries; per-event dates and positions are on request |
| **[F11](../HYPOTHESES.md "Viral lysis and the viral shunt")** | Viral lysis short-circuits the food web | **unscoreable** | **No in-situ marine viral count at any Danish station** was found; the only Danish counts were made in a pressure-chamber experiment |
| **[F13](../HYPOTHESES.md "The organisms that fall between the folk categories")** | Organisms between the folk categories go unrecorded | blocked on a fetch | Open-frame metabarcoding exists outside NOVANA: ARMS-MBON sequencing published through GBIF, and a boulder-reef eDNA pilot. Whether organisms between the categories appear in it is unchecked, and none of it is held |
| **[F14](../HYPOTHESES.md "Viruses as structure, not only as mortality")** | Viruses are structure, not only mortality | **unscoreable** | **No Danish marine virome** was found |
| **[F12](../HYPOTHESES.md "The micropathogens nobody catalogues")** | Micropathogens of invertebrates are uncatalogued | **unscoreable** | DTU Aqua is the national reference laboratory for mollusc disease; what it covers could not be established, and **no catalogue of micropathogens of non-commercial invertebrates** was found |

### G. Climate and long-term drivers

<span class="claim" data-claim="C-TR-N-G">*[6](../SOURCES.md#F-b296cd70dd) hypotheses — [2](../SOURCES.md#F-dafd9a8d83) testable now, [3](../SOURCES.md#F-4b41d0c1a1) blocked on a fetch, [1](../SOURCES.md#F-2a5b45d5cb) blocked on resolution.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-G "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[G1](../hypodrafts/G1.md "Warming")** | d<span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span>/dt = dC_sat/dt − dD/dt; the deficit widens or it does not | **testable now** | **Draft exists** (`hypodrafts/G1.md`). Bottom temperature, salinity and <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> by station and date are in the CTD record |
| **[G2](../HYPOTHESES.md "Changing precipitation and runoff timing")** | Runoff timing shifts -> load timing shifts -> state shifts | blocked on a fetch | Daily discharge and concentration, not annual sums: open at station level, not fetched |
| **[G3](../HYPOTHESES.md "Changing wind climatology")** | Wind climatology change -> mixing change | **testable now** | Hourly wind held, [31](../SOURCES.md#F-bec24964f0) years. The trend null must be matched-autocorrelation, not independence |
| **[G4](../HYPOTHESES.md "Acidification")** | Acidification alters carbonate saturation for calcifiers | blocked on resolution | pH ([40,657](../SOURCES.md#F-ec30fa9198) rows) and total alkalinity ([22,897](../SOURCES.md#F-83b38d8529) rows) are both in the held water-chemistry extract; the current programme takes them at its primary-production stations only, a thin basis for a trend, with no p<span class="chem" data-chem="CO2" title="carbon dioxide">CO₂</span> to check it against |
| **[G5](../HYPOTHESES.md "Changing ice cover")** | Ice cover change alters seasonal mixing | blocked on a fetch | Ice records: no Danish-waters ice chart archive was located, and the satellite products are too coarse for the Belts and the Sound |
| **[G6](../HYPOTHESES.md "Sea level rise")** | Sea level rise alters exchange and inundation | blocked on a fetch | DMI tide gauges: long, open, not fetched |

### H. State, memory and regime

<span class="claim" data-claim="C-TR-N-H">*[4](../SOURCES.md#F-a5ec7810c4) hypotheses — [4](../SOURCES.md#F-7b6ee61308) blocked on a fetch.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-H "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[H1](../HYPOTHESES.md "Alternative stable states and hysteresis")** | State does not retrace the load path — hysteresis | blocked on a fetch | Long paired load and state through **both** directions: the monthly load per water body is on `TILFOERSEL`, unreached, and the reversal may not have occurred |
| **[H2](../HYPOTHESES.md "Sediment legacy")** | Sediment legacy sustains demand after load falls | blocked on a fetch | Sediment organic content is in ICES DOME and ODA, not fetched; **dated cores** inside Danish fjords were found nowhere |
| **[H3](../HYPOTHESES.md "Loss of resilience through diversity loss")** | Diversity loss -> variance of response up | blocked on a fetch | ODA bundfauna, long species-level series |
| **[H4](../HYPOTHESES.md "Subsidy-stress")** | Response is non-monotone across the load gradient | blocked on a fetch | The [123](../SOURCES.md#F-173d507c7a) areas supply the gradient; the **load axis is the unfetched half** |

### J. Surface film, gel and the greasy water itself

<span class="claim" data-claim="C-TR-N-J">*[9](../SOURCES.md#F-ca1cf2a63d) hypotheses — [1](../SOURCES.md#F-1efd11344c) blocked on a fetch, [1](../SOURCES.md#F-ba16162ea9) blocked on resolution, [6](../SOURCES.md#F-048c9341ee) unscoreable, [1](../SOURCES.md#F-51f28a1b04) not established.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-J "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[J1](../openproblems/J1.md "Transparent exopolymer particles and marine gel")** | Attenuation residual after chlorophyll, CDOM and particles is gel | **unscoreable** | **No TEP measurement in Danish water** was found, and `Lysdaempning` is a bare `pct` with **no path length recorded**, so the total has no physical units |
| **[J2](../HYPOTHESES.md "Sea-surface microlayer enrichment")** | Microlayer enrichment concentrates surfactants and toxicants | **unscoreable** | **No sea-surface microlayer sample from Danish water** was found |
| **[J3](../HYPOTHESES.md "Surfactants from detergents and personal care")** | Surfactant load -> film -> gas exchange down | **unscoreable** | No surfactant measurement in any ODA module or in HELCOM's hazardous-substance programme |
| **[J4](../HYPOTHESES.md "Sunscreen and UV filters")** | UV filters accumulate in nearshore water | **unscoreable** | **No UV-filter measurement in Danish water** was found; bathing-water sampling measures faecal bacteria only |
| **[J9](../HYPOTHESES.md "Fragmentation as a source term, and the inventory that omits it")** | Fragmentation is a source term the inventory omits | not established | Miljøstyrelsen's microplastic inventory gives release by source; whether fragmentation is separable within it is not established |
| **[J5](../HYPOTHESES.md "Microplastic and its biofilm")** | Microplastic biofilm alters the microlayer | **unscoreable** | **No water-column or microlayer microplastic measurement in Danish water** was found; what is counted is macro litter |
| **[J6](../HYPOTHESES.md "Oil and hydrocarbon films")** | Oil films in SAR co-locate with the greasy-water reports | blocked on a fetch | **`Sentinel-1` SAR covers Danish waters from October 2014**, downloaded with a free account; HELCOM's aerial spill records carry position, time and wind. The register's own Needs line says this one is testable now — it is a fetch away |
| **[J7](../HYPOTHESES.md "Exudate from senescing blooms")** | Bloom collapse -> DOC pulse -> film | blocked on resolution | **DOC at sub-monthly resolution.** The held water-chemistry extract carries total organic carbon on [5,389](../SOURCES.md#F-1e5fc5d4c6) rows and no parameter named as dissolved organic carbon; the only Danish marine DOC series found is a Roskilde Fjord study, 2014-2015 |
| **[J8](../HYPOTHESES.md "Bacterial exopolymer from fast-growing communities")** | Fast-growing communities exude more polymer | **unscoreable** | Microbial community composition is not in the monitoring; the Danish research sequencing found measures no exopolymer production |

### K. Depletion and imbalance of what life requires

<span class="claim" data-claim="C-TR-N-K">*[14](../SOURCES.md#F-eb0e417241) hypotheses — [2](../SOURCES.md#F-ef76059756) testable now, [4](../SOURCES.md#F-eb1cc571c1) blocked on a fetch, [1](../SOURCES.md#F-22ddb6e7b6) blocked on resolution, [6](../SOURCES.md#F-9c7c58c0f7) unscoreable, [1](../SOURCES.md#F-8254bef792) needs an experiment.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-K "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[K1](../hypodrafts/K1.md "Silicon depletion and the diatom-to-flagellate shift")** | Si:DIN falls -> diatom share falls -> flagellates rise | blocked on a fetch | Silicon, nitrite+nitrate and ammonium are in the held extract. **Phytoplankton cell counts are not held**: they need an ICES account, or VanDa, which refused access. Draft exists (`hypodrafts/K1.md`); the CMEMS plankton types are satellite retrievals derived from chlorophyll and cannot bear it |
| **[K2](../HYPOTHESES.md "Stoichiometric imbalance decides who grows")** | N:P:Si ratio, not absolute load, selects the assemblage | blocked on a fetch | Total N, total P and silicon are in the held extract; species-level counts are not held, as for [K1](../hypodrafts/K1.md "Silicon depletion and the diatom-to-flagellate shift") |
| **[K3](../HYPOTHESES.md "Macronutrient excess inducing micronutrient deficiency")** | Macronutrient excess induces micronutrient deficiency in tissue | needs an experiment | **Tissue elemental analysis of algae and eelgrass is not in the NOVANA protocols** |
| **[K4](../HYPOTHESES.md "Thiamine (B1) deficiency")** | Thiamine deficiency propagates up the food web | **unscoreable** | **No Danish marine thiamine assay** was found. Swedish work exists |
| **[K5](../HYPOTHESES.md "Cobalamin (B12) and cobalt limitation")** | Vitamin `B12` and cobalt limit the auxotrophs | **unscoreable** | **No marine `B12` or dissolved cobalt measurement for Danish water** was found |
| **[K6](../HYPOTHESES.md "Iron bioavailability")** | Iron bioavailability limits production or detoxification | **unscoreable** | No iron speciation for Danish water was found |
| **[K7](../HYPOTHESES.md "Carbonate ion depletion")** | Carbonate ion depletion impairs calcification | blocked on resolution | pH and total alkalinity are both in the held water-chemistry extract; the temperature and salinity for each bottle come from the CTD record by station and day, not the same hour |
| **[K8](../HYPOTHESES.md "The narrow window between deficient and toxic")** | The window between deficient and toxic is narrow and crossed | **unscoreable** | No dissolved trace metal in the water column in routine monitoring; metals are measured in mussel tissue |
| **[K9](../HYPOTHESES.md "Selenium")** | Selenium status limits or intoxicates | **unscoreable** | Selenium was not confirmed as a determinand in Danish marine biota; mercury is measured |
| **[K10](../HYPOTHESES.md "Salinity change and osmotic cost")** | Salinity change imposes osmotic cost at the range edge | **testable now** | Salinity by station, date and depth is in the CTD record — [7,474,645](../SOURCES.md#F-cf5c72a98d) rows |
| **[K11](../HYPOTHESES.md "Light as a depleted resource")** | Light at the bed = f(Kd, depth), and the product is rarely formed | **testable now** | **Both halves held**: `lys` [2,370,091](../SOURCES.md#F-d9b22c989d) rows and bottom depth in `maaledybde`, [96,708](../SOURCES.md#F-e51550bdc9) paired. Carries the Kd start-depth artefact, and Secchi censoring at the bed: [36.9](../SOURCES.md#F-46aa1895a2)% of paired readings in water shallower than [5](../SOURCES.md#F-7f0e8a949b) m reach the bed |
| **[K12](../HYPOTHESES.md "Loss of habitat-forming structure")** | Structure removal -> habitat loss independent of water quality | blocked on a fetch | Stone extraction records, reef restoration locations and dates: not published as data, to be obtained from the projects |
| **[K13](../HYPOTHESES.md "Food depletion for filter feeders and larvae")** | Particle spectra shift below the filter-feeder window | **unscoreable** | **No particle size spectrum or larval condition index for Danish water** was found, by a keyword search |
| **[K14](../HYPOTHESES.md "Genetic and functional diversity depletion")** | Functional diversity falls before species richness does | blocked on a fetch | ODA bundfauna, joined to a trait table |

### W. Renewal and rate

<span class="claim" data-claim="C-TR-N-W">*[8](../SOURCES.md#F-9777cbd65a) hypotheses — [1](../SOURCES.md#F-e5193dafdc) testable now, [4](../SOURCES.md#F-68e0354bdb) blocked on a fetch, [1](../SOURCES.md#F-ef0f98c5fb) blocked on resolution, [2](../SOURCES.md#F-0bd0994607) needs an experiment.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-W "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[W1](../HYPOTHESES.md "Propagule supply and connectivity")** | Recovery fails where propagule supply is cut | blocked on resolution | Source populations plus particle tracking: no national eelgrass or mussel-bed layer was reachable, no connectivity matrix is deposited, and the held current field does not resolve the straits |
| **[W2](../HYPOTHESES.md "Settlement cue failure")** | Unconditioned substrate fails to recruit | needs an experiment | **Settlement plates with and without conditioning.** Connects to the sediment-inoculation experiment `X1` |
| **[W3](../HYPOTHESES.md "Phenological mismatch")** | Bloom and larval peak drift apart | blocked on a fetch | Plankton counts: NOVANA samples plankton through the growing season at its primary-production stations, and the counts are in VanDa, which refused access; not held |
| **[W4](../HYPOTHESES.md "Allee effects at low density")** | Below a density threshold reproduction fails | blocked on a fetch | ODA bundfauna carries densities per grab; the analysis is then a desk exercise |
| **[W5](../HYPOTHESES.md "Recovery slower than the disturbance interval")** | Disturbance interval shorter than recovery time | blocked on a fetch | **Trawling effort at monthly or finer.** Every public product found is annual; the timestamped VMS positions are inside ICES |
| **[W6](../HYPOTHESES.md "Change outrunning acclimation")** | Rate of change exceeds acclimation rate | **testable now** | The CTD record supports a rate analysis over years; genuinely high-frequency temperature is at tide gauges, not at the bed |
| **[W8](../HYPOTHESES.md "Whoever founds the community keeps it")** | The founder community determines the endpoint | needs an experiment | Composition immediately after disturbance and through recovery at the same place — requires having sampled before |
| **[W7](../HYPOTHESES.md "Too little variation left to respond with")** | Too little standing variation is left to respond with | blocked on a fetch | Long species-level fauna is in ODA; **no genetic time series for any Danish marine species** was found, so that half is unscoreable |

### Z. The physical fields and their windows

<span class="claim" data-claim="C-TR-N-Z">*[11](../SOURCES.md#F-bd58527cd6) hypotheses — [3](../SOURCES.md#F-5a90478e4b) testable now, [2](../SOURCES.md#F-22cf725cc7) blocked on a fetch, [2](../SOURCES.md#F-56f1715935) blocked on resolution, [3](../SOURCES.md#F-2c1d0d090e) unscoreable, [1](../SOURCES.md#F-03944105f9) needs an experiment.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-Z "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[Z1](../HYPOTHESES.md "Light: too little, and too much")** | Light at the bed outside the window -> loss | **testable now** | The same product as [K11](../HYPOTHESES.md "Light as a depleted resource"); both halves held |
| **[Z2](../HYPOTHESES.md "Light quality, not quantity: browning")** | Browning shifts the spectrum, not just the quantity | blocked on resolution | **Kd is a single broadband number.** FDOM ([890,921](../SOURCES.md#F-acb2b229c0) rows, from [2021](../SOURCES.md#F-281b3dc6e4) onward only) is a CDOM proxy on the same cast — [6](../SOURCES.md#F-d7f71d585c) years of in-situ CDOM |
| **[Z3](../HYPOTHESES.md "Photoperiod and timing as a cue")** | Photoperiod cue decouples from temperature cue | **unscoreable** | **No phenological observation series for Danish marine invertebrates** was found |
| **[Z4](../HYPOTHESES.md "Temperature: window, and rate")** | Rate of temperature change, not level, exceeds tolerance | blocked on resolution | Bottom temperature at high frequency; the monthly product aliases it, and the raw bed record resolves multi-year rates, not event onset |
| **[Z5](../HYPOTHESES.md "Hydrodynamic energy has a floor as well as a ceiling")** | Energy has a floor — too still is also a failure | **testable now** | Bed shear already computed here from [31](../SOURCES.md#F-bec24964f0) years of wind; the floor is testable against the same state variables |
| **[Z6](../HYPOTHESES.md "Sound, as a cue and as a stressor")** | Sound masks settlement cues | **unscoreable** | Ambient noise is monitored; **no settlement or recruitment measurement** was found to test it against |
| **[Z7](../HYPOTHESES.md "Electromagnetic fields")** | EMF from cables alters behaviour | **unscoreable** | No Danish national cable layer with energisation dates was found, and **the biological response is not measured** |
| **[Z8](../hypodrafts/Z8.md "The attenuation budget is never partitioned")** | The attenuation budget is never partitioned | **testable now** | **Draft exists** (`hypodrafts/Z8.md`). Kd plus chlorophyll, CDOM and particle proxies on the same casts — but `Lysdaempning` has no path length, so the draft apportions variance, not a budget |
| **[Z9](../HYPOTHESES.md "Epiphyte shading, which bypasses the water column")** | Epiphytes shade the plant regardless of water clarity | blocked on a fetch | Epiphyte biomass on eelgrass: ODA records epiphyte cover per transect point, not biomass, and no biomass series was found |
| **[Z10](../HYPOTHESES.md "Mineral plumes from works")** | Works plumes exceed natural turbidity long enough to matter | blocked on a fetch | Works chronology plus the turbidity monitoring large projects must do: dated pile-driving events are in the ICES noise register; project turbidity monitoring was at no public endpoint |
| **[Z11](../HYPOTHESES.md "The weakened host")** | A weakened host fails at a stress a healthy one survives | needs an experiment | Carbohydrate reserves, tissue sulphide and pathogen load on the same plants |

### T. Sediment sickness: symbionts, pathogens and why nothing grows back

<span class="claim" data-claim="C-TR-N-T">*[12](../SOURCES.md#F-73622a0de3) hypotheses — [1](../SOURCES.md#F-5166c930a6) blocked on a fetch, [4](../SOURCES.md#F-4facca4cbd) unscoreable, [7](../SOURCES.md#F-c0a12d6978) needs an experiment.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-T "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[T1](../HYPOTHESES.md "Sulphide intrusion, gated by light")** | Sulphide intrudes when light cannot power the defence | needs an experiment | Tissue sulphide, porewater sulphide and light at the bed on the same plants; a research method, not monitoring |
| **[T2](../HYPOTHESES.md "Loss of the sulphide-detoxifying symbiosis")** | Lucinid bivalves absent -> sulphide detoxification lost | blocked on a fetch | **Lucinid and thyasirid taxa are in ODA bundfauna**; the fauna stations are not placed in seagrass beds, so it needs a join to the vegetation transects |
| **[T3](../HYPOTHESES.md "Wasting disease with stress-modulated virulence")** | Labyrinthula virulence rises with host stress | needs an experiment | Labyrinthula screening in Danish eelgrass; not routine, and nothing measures host stress alongside it |
| **[T4](../HYPOTHESES.md "Marine replant failure: negative sediment feedback")** | Replanting fails on conditioned sediment and succeeds on clean | needs an experiment | **Restoration trials with sediment treatments.** Danish eelgrass transplant trials exist; this design does not |
| **[T5](../HYPOTHESES.md "Loss of sediment suppressiveness")** | Suppressive sediment resists invasion; degraded does not | needs an experiment | Danish sediment microbial samples exist, none from inside a seagrass bed, **and no transfer experiment** |
| **[T6](../HYPOTHESES.md "Enrichment dissolving the partnership")** | Enrichment dissolves the partnership by making it unnecessary | needs an experiment | Rhizosphere community composition along the gradient |
| **[T7](../HYPOTHESES.md "Anaerobic phytotoxins other than sulphide")** | Anaerobic phytotoxins beyond sulphide | needs an experiment | Porewater chemistry beyond the standard nutrients: no Fe(II) or Mn(II) speciation for any Danish site was found |
| **[T8](../HYPOTHESES.md "Anaerobic conditions select the pathogens")** | Anaerobia selects for the pathogens | **unscoreable** | **No pairing of oomycete or labyrinthulid abundance with sediment redox** was found |
| **[T9](../HYPOTHESES.md "Pathogen and partner are not kinds of organism")** | Pathogen and partner are not kinds of organism | **unscoreable** | Danish eelgrass microbiome datasets exist; **none records host condition or disease** |
| **[T12](../HYPOTHESES.md "Defence is outsourced, because the host cannot win the race")** | Defence is outsourced; a biocide disarms the host | **unscoreable** | No defence phenotype measured against microbiome composition was found |
| **[T11](../HYPOTHESES.md "Occupancy is the function")** | Occupancy is the function; the empty niche is the risk | needs an experiment | **Challenge experiments on intact versus disturbed communities**, not run in Danish marine work |
| **[T10](../HYPOTHESES.md "Removing an organism whose role is unknown is not neutral")** | Removing an unknown-role organism is not neutral | **unscoreable** | **No pre-intervention community baseline** for any Danish marine intervention was found, which makes the comparison impossible by construction |

### S. The land side: the medium, not the input

<span class="claim" data-claim="C-TR-N-S">*[6](../SOURCES.md#F-2104dff7ad) hypotheses — [3](../SOURCES.md#F-3adc3860b2) blocked on a fetch, [1](../SOURCES.md#F-cacfb07b20) blocked on resolution, [1](../SOURCES.md#F-bea7d92022) unscoreable, [1](../SOURCES.md#F-716b15c6a7) needs an experiment.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-S "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[S1](../HYPOTHESES.md "Retention is a property of the medium and varies by an order of magnitude")** | Retention varies an order of magnitude with the medium | blocked on a fetch | The soil map exists; the paired leaching measurements are in the catchment monitoring programme, whose raw rows are in ODA and not fetched |
| **[S2](../HYPOTHESES.md "Phosphorus saturation, and legacy leakage")** | Legacy soil P leaks after inputs stop | **unscoreable** | **No open layer of Danish soil P status at any spatial unit** was found |
| **[S3](../HYPOTHESES.md "Sorption is hysteretic - a ratchet on the land side too")** | Sorption is hysteretic — a ratchet on the land side too | needs an experiment | Sorption-desorption experiments on Danish soils; standard method |
| **[S4](../HYPOTHESES.md "Total is not available")** | Total P is not available P | blocked on a fetch | Fractionated sediment P: ODA's sediment chemistry (`Emne_12_19`) carries total P and an Fe-adsorbed fraction only; not fetched |
| **[S5](../HYPOTHESES.md "Buffering scales with the volume of reactive medium")** | Buffering scales with the volume of reactive medium | blocked on resolution | Bathymetry is held; **sediment thickness is not**, and the Quaternary thickness raster merges till with mud |
| **[S6](../HYPOTHESES.md "Retention capacity is saturable, so the coefficient is not constant")** | The retention coefficient is not constant — it saturates | blocked on a fetch | The register's own Needs line: **'Requires no new measurement at all'** — the national retention map and the monthly catchment flux series in ODA, which is not fetched |

### R. Decay, and the community that does it

<span class="claim" data-claim="C-TR-N-R">*[11](../SOURCES.md#F-29f7a52cc5) hypotheses — [2](../SOURCES.md#F-4e8b726836) blocked on a fetch, [1](../SOURCES.md#F-0dcf689add) blocked on resolution, [2](../SOURCES.md#F-8f5ab0863b) unscoreable, [6](../SOURCES.md#F-da712995c6) needs an experiment.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-R "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[R11](../HYPOTHESES.md "Marine fungi, the decomposers nobody counts")** | Marine fungi decompose and nobody counts them | **unscoreable** | **No marine fungal biomass measurement** was found, and the Danish marine fungal barcode record is an ARMS deployment at Læsø |
| **[R1](../HYPOTHESES.md "The C:N threshold, and fat as a nitrogen sink")** | C:N of discharged material decides whether it is a sink | blocked on a fetch | Organic carbon is reported for large industry and N and COD at stream stations; **fat is not a reported pollutant** |
| **[R2](../HYPOTHESES.md "Priming of the old sediment pool by fresh carbon")** | Fresh carbon primes the old sediment pool | needs an experiment | Sediment incubation with and without labile addition |
| **[R3](../HYPOTHESES.md "The decay relay stalls when a stage is removed")** | The decay relay stalls when a stage is removed | blocked on a fetch | Sediment organic content and fauna are both in ODA, **at different stations**, not fetched |
| **[R4](../HYPOTHESES.md "Nitrogen enrichment retards decay of the recalcitrant fraction")** | N enrichment retards decay of the recalcitrant fraction | needs an experiment | Litter-bag or incubation studies with characterised organic fractions |
| **[R5](../HYPOTHESES.md "The terminal electron acceptor cascade, and why salt changes it")** | The electron-acceptor cascade shifts with salinity | blocked on resolution | Porewater sulphide and methane by station: published for Aarhus Bay and a basin transect, neither spanning the salinity gradient |
| **[R6](../openproblems/R6.md "Sulphide locks the iron that would hold the phosphate")** | Sulphide locks the iron that would hold the phosphate | needs an experiment | **A paired sequential iron and sulphur extraction** was found for no Danish sediment |
| **[R7](../HYPOTHESES.md "Estuarine flocculation deposits river carbon at the coast")** | Flocculation deposits river carbon at the coast | **unscoreable** | **No sediment organic carbon along a Danish river-mouth salinity transect** was found; the organic carbon stations in ODA are not arranged as one |
| **[R8](../HYPOTHESES.md "Lipids are less soluble in seawater")** | Lipids are less soluble in seawater, so they deposit | needs an experiment | Lipid fractionation by salinity |
| **[R9](../HYPOTHESES.md "Home-field advantage, and novel material")** | Novel material decays slower — no home-field advantage | needs an experiment | Comparative decomposition assays |
| **[R10](../HYPOTHESES.md "Osmotic discontinuity for the decomposers themselves")** | Osmotic discontinuity stalls the decomposers themselves | needs an experiment | Cross-transplant incubations |

### L. The baseline and the counterfactual

<span class="claim" data-claim="C-TR-N-L">*[6](../SOURCES.md#F-0e6fbfe636) hypotheses — [1](../SOURCES.md#F-2587fccf66) testable now, [4](../SOURCES.md#F-3b1387751f) blocked on a fetch, [1](../SOURCES.md#F-158598441b) unscoreable.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-L "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[L6](../HYPOTHESES.md "The degraded bed is classified as its own habitat type")** | The degraded bed is classified as its own habitat type | blocked on a fetch | Historical seabed charts, old fisheries records and trawling effort — **the history a classification key discards**; likely an archive request |
| **[L1](../HYPOTHESES.md "The reference condition never existed")** | The reference condition never existed | **unscoreable** | **No dated sediment core with diatom or pigment stratigraphy from the Danish coast** was found |
| **[L2](../HYPOTHESES.md "The reference is a model output treated as a fact")** | The reference is a model output treated as a fact | blocked on a fetch | **Archival, not statistical.** The eelgrass boundaries are readable in the EU decision; the papers documenting the reference model are paywalled, so they need **credentials** |
| **[L3](../hypodrafts/L3.md "The trend depends on the start year")** | The trend depends on the start year | **testable now** | **Draft exists** (`hypodrafts/L3.md`), and its test has not been run |
| **[L4](../HYPOTHESES.md "Recovery is blocked by something other than the driver")** | Recovery is blocked by something other than the driver | blocked on a fetch | Restoration trials with controls: the Horsens Fjord transplant is published as summary statistics, and no per-replicate data from any Danish trial was found |
| **[L5](../HYPOTHESES.md "The reference sites are not references")** | The reference sites are not references | blocked on a fetch | Trawling, dumping and contaminant coverage for the areas used as references; the list of those areas was not located |

### I. Observation and measurement

<span class="claim" data-claim="C-TR-N-I">*[7](../SOURCES.md#F-f540337e22) hypotheses — [6](../SOURCES.md#F-c53557ff04) testable now, [1](../SOURCES.md#F-812d915348) blocked on resolution.*</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-N-I "What this claim rests on")</sup>

| id | consequence | class | blocker |
|---|---|---|---|
| **[I1](../hypodrafts/I1.md "Changing station network")** | Apparent change concentrates where the network changed | **testable now** | **Draft exists** (`hypodrafts/I1.md`). The register cannot supply lifespans; presence comes from the observation record |
| **[I2](../HYPOTHESES.md "Changing analytical method")** | Step changes at probe changeover, shared across geography | blocked on resolution | **`SondeNr` is `999` on [25.6](../SOURCES.md#F-18d47162ce)% of rows** in the whole CTD extract. The rest carries [81](../SOURCES.md#F-9c2bc4c9bc) identified probes and is where [I2](../HYPOTHESES.md "Changing analytical method") is testable |
| **[I3](../hypodrafts/I3.md "Changing sampling frequency and season")** | Apparent severity scales with visit count and window | **testable now** | **Draft exists** (`hypodrafts/I3.md`). Every visit carries its date |
| **[I4](../HYPOTHESES.md "Changing indicator definition")** | Status shifts at definition changes with no measurement change | **testable now** | The definitions with their adoption dates — archival, and the recomputation runs on held data |
| **[I5](../HYPOTHESES.md "Changing correction factors")** | Trends present in corrected but not original results | **testable now** | **Held.** `KorrektionsFaktor` is exactly one on [94.76](../SOURCES.md#F-f5eeb40780)% of rows, and Original differs from Korrigeret on [5.21](../SOURCES.md#F-0146c2b052)% of those carrying both |
| **[I6](../HYPOTHESES.md "Changing custodian")** | Discontinuities at 2007 shared across stations that changed hands | **testable now** | `Dataleverandoer` and `TekniskAnvisningAnvendt` are in the raw record — but over the whole CTD extract they carry [2](../SOURCES.md#F-69e562d658) and [1](../SOURCES.md#F-9530b4b76f) distinct values, so the contrast may be empty |
| **[I7](../HYPOTHESES.md "Batch defects in ingest or processing")** | Implausible values cluster in time across unrelated custodians | **testable now** | **Worked case already found**: [11](../SOURCES.md#F-c8b8b1dcfd) station-months at [6](../SOURCES.md#F-4ed890d0d9) stations, recorded in `flags.json` |

---

## What the shape of it says

### Blocked on a fetch

<span class="claim" data-claim="C-TR-FETCH">**[62](../SOURCES.md#F-15045ed0fb) of [166](../SOURCES.md#F-4196d405de) ([37](../SOURCES.md#F-00ac661b28)%) are blocked on a fetch**: what they need is named and is not held here.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-FETCH "What this claim rests on")</sup> <span class="claim" data-claim="C-TR-OPEN">The source register records some of those sources as open without a login: the ICES swept-area-ratio product and HELCOM's fishing-intensity layers, ICES stock assessments, OBIS occurrences, and DMI's sea-level and weather series, unauthenticated in its testing. `Sentinel-1` scenes need a free account. ODA's bottom-fauna and vegetation topics need the ODA registration this project already uses, and are not in `fetch_oda.py`'s topic list. Phytoplankton counts need credentials: VanDa refused access, and the ICES route needs an account.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-OPEN "What this claim rests on")</sup>

### The water-chemistry extract, re-scored

<span class="claim" data-claim="C-TR-RESCORE">The ODA water-chemistry extract (`vandkemi`, `Emne_10_11`) was named in the blocker for [A1](../hypodrafts/A1.md "Danish land-based nitrogen load"), [A2](../HYPOTHESES.md "Phosphorus load"), [A5](../HYPOTHESES.md "Advected nutrients from outside Denmark"), [A7](../openproblems/A7.md "Sediment nutrient regeneration"), [B4](../HYPOTHESES.md "Riverine particulate organic carbon"), [E2](../HYPOTHESES.md "Nitrification demand"), [E11](../HYPOTHESES.md "Ammonia toxicity"), [K1](../hypodrafts/K1.md "Silicon depletion and the diatom-to-flagellate shift") and [K2](../HYPOTHESES.md "Stoichiometric imbalance decides who grows") — [9](../SOURCES.md#F-b5ea195365) hypotheses. It is now held, and `scripts/rescore.py` checks each against it: **[1](../SOURCES.md#F-f392c48f94) has every variable its consequence needs and is testable now, [E2](../HYPOTHESES.md "Nitrification demand")**; for the other [8](../SOURCES.md#F-1b7430e469) a second blocker stood behind the first.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-RESCORE "What this claim rests on")</sup> <span class="claim" data-claim="C-TR-SECOND">[A1](../hypodrafts/A1.md "Danish land-based nitrogen load"), [A2](../HYPOTHESES.md "Phosphorus load") and [A7](../openproblems/A7.md "Sediment nutrient regeneration") need river input, on ODA topics `fetch_oda.py` does not reach; [A5](../HYPOTHESES.md "Advected nutrients from outside Denmark") needs volume transport at the Belt and Sound sections, which no open series the source register found carries; [B4](../HYPOTHESES.md "Riverine particulate organic carbon") needs stream stations, outside the marine topic; [K1](../hypodrafts/K1.md "Silicon depletion and the diatom-to-flagellate shift") and [K2](../HYPOTHESES.md "Stoichiometric imbalance decides who grows") need phytoplankton counts, which are not held; and [E11](../HYPOTHESES.md "Ammonia toxicity") needs a temperature from the same bottle.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-SECOND "What this claim rests on")</sup>

<span class="claim" data-claim="C-TR-GROUPA">No hypothesis in group A, the nutrient group, is testable now; its [10](../SOURCES.md#F-b17d38223a) are blocked on a fetch, unscoreable or not established.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-GROUPA "What this claim rests on")</sup>

<span class="claim" data-claim="C-TR-BUNDFAUNA">Of the fetches not yet made, ODA's bottom-fauna topic (`bundfauna`) is named in the blocker for [8](../SOURCES.md#F-7495c59f85): [D9](../HYPOTHESES.md "Fertility islands lost to homogenisation"), [D11](../HYPOTHESES.md "Stabilisers against destabilisers"), [F1](../HYPOTHESES.md "Loss of filter feeders"), [F2](../HYPOTHESES.md "Loss of bioturbators"), [H3](../HYPOTHESES.md "Loss of resilience through diversity loss"), [K14](../HYPOTHESES.md "Genetic and functional diversity depletion"), [W4](../HYPOTHESES.md "Allee effects at low density") and [T2](../HYPOTHESES.md "Loss of the sulphide-detoxifying symbiosis").</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-BUNDFAUNA "What this claim rests on")</sup>

### The largest named blocking dimension is not nutrients

<span class="claim" data-claim="C-TR-MICROBIAL">**[11](../SOURCES.md#F-e661888b83) hypotheses are unscoreable for one missing dimension: microbial, viral and fungal community composition** — among [E13](../HYPOTHESES.md "Biocides that remove the decomposers themselves"), [E17](../HYPOTHESES.md "The microbiome is the exposed organ"), [F8](../HYPOTHESES.md "Microbial shift to fast-growing forms"), [F11](../HYPOTHESES.md "Viral lysis and the viral shunt"), [F12](../HYPOTHESES.md "The micropathogens nobody catalogues"), [F13](../HYPOTHESES.md "The organisms that fall between the folk categories"), [F14](../HYPOTHESES.md "Viruses as structure, not only as mortality"), [J8](../HYPOTHESES.md "Bacterial exopolymer from fast-growing communities"), [R11](../HYPOTHESES.md "Marine fungi, the decomposers nobody counts"), [T5](../HYPOTHESES.md "Loss of sediment suppressiveness"), [T6](../HYPOTHESES.md "Enrichment dissolving the partnership"), [T8](../HYPOTHESES.md "Anaerobic conditions select the pathogens"), [T9](../HYPOTHESES.md "Pathogen and partner are not kinds of organism") and [T12](../HYPOTHESES.md "Defence is outsourced, because the host cannot win the race"); of the rest, [2](../SOURCES.md#F-5fe1f1a7ae) need an experiment instead and [1](../SOURCES.md#F-487ebdc741) waits on a fetch.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-MICROBIAL "What this claim rests on")</sup> <span class="claim" data-claim="C-TR-MICRO-REG">National marine monitoring counts no viruses and monitors no microbial community composition; the Danish sequencing the source register found is research outside the programme, and for the unscoreable ones none of it records what they turn on. Of the clusters of blockers this page names, it is the largest.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-MICRO-REG "What this claim rests on")</sup>

<span class="claim" data-claim="C-TR-TOXICANT">A second cluster of [7](../SOURCES.md#F-7a78427d2e) is **toxicant concentration in a marine matrix** — [E7](../openproblems/E7.md "Pesticides and degradation products"), [E8](../HYPOTHESES.md "Pharmaceuticals and personal care products"), [E18](../HYPOTHESES.md "Tyre-wear transformation products"), [J3](../HYPOTHESES.md "Surfactants from detergents and personal care"), [J4](../HYPOTHESES.md "Sunscreen and UV filters"), [K8](../HYPOTHESES.md "The narrow window between deficient and toxic") and [K9](../HYPOTHESES.md "Selenium") — where the national hazardous-substance layer holds [256](../SOURCES.md#F-aee5a58e2f) stations, not one of them coastal.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-TOXICANT "What this claim rests on")</sup> <span class="claim" data-claim="C-TR-TWO">Together those two dimensions account for **[18](../SOURCES.md#F-0df9013823) of the [42](../SOURCES.md#F-198b20fb90) unscoreable** ([43](../SOURCES.md#F-7270c02bc1)%).</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-TWO "What this claim rests on")</sup>

### [25](../SOURCES.md#F-935d9e0296)% of the field cannot be scored with any source surveyed

<span class="claim" data-claim="C-TR-UNSCOREABLE">**[42](../SOURCES.md#F-198b20fb90) of [166](../SOURCES.md#F-4196d405de) ([25](../SOURCES.md#F-935d9e0296)%) are unscoreable**: the deciding measurement is in none of the sources this project surveyed.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-UNSCOREABLE "What this claim rests on")</sup> <span class="claim" data-claim="C-TR-BEYOND">Add the [20](../SOURCES.md#F-64bb5d44db) that need an experiment and **[37](../SOURCES.md#F-2cc76f7f45)% of the hypothesis field is beyond reach of any reanalysis of the data this project holds or has found.**</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-BEYOND "What this claim rests on")</sup>

<span class="claim" data-claim="C-TR-CONTEST">This is the number that matters for how the whole argument should be read. When a public debate settles on nutrients, it is not because nutrients won a contest against the alternatives: [62](../SOURCES.md#F-38d4f3aa11) of these hypotheses have not been in a position to compete.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-CONTEST "What this claim rests on")</sup>

### Where the archive is strong

<span class="claim" data-claim="C-TR-STRONG">Where most hypotheses are testable now: **I** ([6](../SOURCES.md#F-c53557ff04) of [7](../SOURCES.md#F-f540337e22)), **C** ([5](../SOURCES.md#F-0596b7e6b1) of [9](../SOURCES.md#F-89669b4a5d)).</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-STRONG "What this claim rests on")</sup> <span class="claim" data-claim="C-TR-CTD">In **C**, physical resupply, they are the ones the CTD record, the depth soundings, the inflow indicator files and the weather reanalysis held here measure: temperature, salinity, oxygen, depth and wind.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-CTD "What this claim rests on")</sup>

<span class="claim" data-claim="C-TR-PATTERN">The pattern across groups: **the archive held here tests physics and itself, and the groups on biology hold no testable entry.** Groups C, G, Z and I hold [16](../SOURCES.md#F-8a51a62310) of the [23](../SOURCES.md#F-e786dfc514) testable-now entries. Groups F, J, T and R — biological structure, films, sediment sickness, decay — hold none of them, and E, chemistry, holds [1](../SOURCES.md#F-8e56e09dff); those five groups hold [42](../SOURCES.md#F-4a26ebdff7) of the [62](../SOURCES.md#F-38d4f3aa11) entries that are unscoreable or need an experiment.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-PATTERN "What this claim rests on")</sup>

### An honest caveat about this table

<span class="claim" data-claim="C-TR-CAVEAT">The classification is mine and is itself an untested partition, exactly as the [17](../SOURCES.md#F-b36383859a) groups are (PLAN.md says so of them). Two judgements are load-bearing and contestable: I treated *not fetched but fetchable* as **blocked on a fetch** rather than unscoreable even where nobody has confirmed the topic contains what its name suggests; and I treated *measured somewhere in the world but not in Denmark* as unscoreable **for this archive**, which is a statement about Denmark's monitoring rather than about nature. The [4](../SOURCES.md#F-6f2641deb0) entries I could not place at all are marked *not established* rather than guessed.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-CAVEAT "What this claim rests on")</sup>

<span class="claim" data-claim="C-TR-SEARCH">And per [KNOWN_AND_UNKNOWN.md](../KNOWN_AND_UNKNOWN.md): **every "not measured" in this table should be read as "not found by a search whose sensitivity nobody has characterised."** Things this project had called absent have turned up before. The unscoreable column is an upper bound on what is missing, not a measurement of it.</span><sup class="claim-mark">[†](../CLAIMS.md#C-TR-SEARCH "What this claim rests on")</sup>
