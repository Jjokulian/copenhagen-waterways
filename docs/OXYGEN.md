# What actually removes the oxygen

<span class="claim" data-claim="C-OB-OX-CHAIN">The requirement rests on a chain: nitrogen feeds algae, dead organic matter draws the oxygen down, and low oxygen harms the life on the bed. DCE use the seasonal pattern of phosphate (DIP) and of chlorophyll as indicators of whether a water body suffers oxygen deficits, because low oxygen at the bottom releases phosphate from the sediment and feeds late-summer blooms; and they note that oxygen deficits affect, among other things, the bottom fauna.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-CHAIN "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-OX-BASIS">Every joint in that chain comes apart, and this page takes them one at a time. The coefficients below are arithmetic on balanced equations and molar masses; the largest rests on the Redfield–Ketchum–Richards composition of plankton, an average from which real plankton depart. The coverage counts come from the national monitoring layers.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-BASIS "What this claim rests on")</sup>

## 1. Oxygen is a balance, not a substance that nitrogen removes

<span class="claim" data-claim="C-OB-OX-BALANCE">An oxygen deficit is what is left when demand exceeds supply. Both sides have many entry points, and most of those below need no nitrogen at all.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-BALANCE "What this claim rests on")</sup>

### Routes that consume oxygen

<span class="claim" data-claim="C-OB-OX-DEMAND-TABLE">Each coefficient is grams of oxygen per gram of the reductant, from its balanced equation and molar masses; the last column names the `Tabel 2` candidate, if any, that could carry the route in DCE's statistical models.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-DEMAND-TABLE "What this claim rests on")</sup>

| route | stoichiometry | needs N? | representable in the statistical layer? |
|---|---|:-:|---|
| Respiration of algal biomass grown in place | [19.7](SOURCES.md#F-4a2fc9ec3d) g <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> per g N | yes | load terms |
| Respiration of organic matter that arrived already made | [1.0](SOURCES.md#F-a6a1dd69b6) g <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> per g COD | **no** | no |
| Nitrification of ammonium | [4.57](SOURCES.md#F-48153903b6) g <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> per g N | yes | no |
| Oxidation of sulphide from the sediment | [2.00](SOURCES.md#F-244f52a3b5) g <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> per g S | **no** | no |
| Oxidation of ferrous iron and manganese | [0.14](SOURCES.md#F-c4f316f3ea) g <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> per g Fe | **no** | no |
| Oxidation of methane | [3.99](SOURCES.md#F-9379552aed) g <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> per g <span class="chem" data-chem="CH4" title="methane">CH₄</span> | **no** | no |
| Decay following a kill of any cause | as the material, above | **no** | no |

**Respiration of algal biomass grown in place.** <span class="claim" data-claim="C-OB-OX-R1">The route the requirement is built on. Nitrogen becomes carbon at Redfield stoichiometry, the carbon is respired, and the organic nitrogen is nitrified.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-R1 "What this claim rests on")</sup>

**Respiration of organic matter that arrived already made.** <span class="claim" data-claim="C-OB-OX-R2">Sewage organics, fat, riverine particulate carbon, anything washed off a surface. COD is its demand measured chemically, in grams of oxygen. It needs no growth step: fat and carbohydrate carry no nitrogen, and though sewage organics carry some, their oxygen demand does not wait on it.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-R2 "What this claim rests on")</sup>

**Nitrification of ammonium.** <span class="claim" data-claim="C-OB-OX-R3">Nitrifying bacteria and archaea oxidise ammonium to nitrate, and the oxygen is gone. This is nitrogen acting as a *reductant*, not as a fertiliser: it needs no algal growth step.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-R3 "What this claim rests on")</sup>

**Oxidation of sulphide from the sediment.** <span class="claim" data-claim="C-OB-OX-R4">Reduced compounds made in anoxic sediment, sulphide among them, move up and are oxidised where they meet oxygen; in coastal sediments most of the oxygen consumed goes to such re-oxidation. A storm that stirs sulphidic water up does the same at once, and so would dredging or trawling that stirs the bed.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-R4 "What this claim rests on")</sup>

**Oxidation of ferrous iron and manganese.** <span class="claim" data-claim="C-OB-OX-R5">The same upward route, smaller per gram: dissolved iron and manganese from the same reduced sediment.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-R5 "What this claim rests on")</sup>

**Oxidation of methane.** <span class="claim" data-claim="C-OB-OX-R6">Produced in anoxic sediment. Part of it can be oxidised on the way up without oxygen, by sulphate or nitrate; the coefficient applies to what reaches oxygenated water.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-R6 "What this claim rests on")</sup>

**Decay following a kill of any cause.** <span class="claim" data-claim="C-OB-OX-R7">A toxicant, a salinity shock, a heat event, physical destruction. Whatever kills leaves a mass that decays, and the decay draws the oxygen down. The oxygen deficit is then downstream of the killing agent, and carries no information about it.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-R7 "What this claim rests on")</sup>

### Routes that fail to resupply oxygen

<span class="claim" data-claim="C-OB-OX-SUPPLY-TABLE">No coefficient is given for these here; the last column names the `Tabel 2` candidate that could carry each.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-SUPPLY-TABLE "What this claim rests on")</sup>

| route | representable? |
|---|---|
| Warming reduces how much the water can hold | temp |
| Stratification blocks resupply from above | BV |
| Light attenuation cuts photosynthetic oxygen production | irr |
| Reduced wind mixing | vind |

**Warming reduces how much the water can hold.** <span class="claim" data-claim="C-OB-OX-S1">Solubility, not biology: warmer water holds less oxygen. Water temperature is a candidate variable, as surface temperature, so this one is at least representable.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-S1 "What this claim rests on")</sup>

**Stratification blocks resupply from above.** <span class="claim" data-claim="C-OB-OX-S2">A column that does not turn over does not refill. Water-column stability (`vandsøjlestabilitet`) is a candidate variable and is selected in [13](SOURCES.md#F-1ba0e8d176) of the [79](SOURCES.md#F-598345fdb6) models in `Tabel 3`.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-S2 "What this claim rests on")</sup>

**Light attenuation cuts photosynthetic oxygen production.** <span class="claim" data-claim="C-OB-OX-S3">The same turbidity that the Kd indicator measures also suppresses photosynthesis, the oxygen source. Kd is an indicator the models predict; it is not among the `Tabel 2` candidates.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-S3 "What this claim rests on")</sup>

**Reduced wind mixing.** <span class="claim" data-claim="C-OB-OX-S4">Wind stress is a candidate variable. It is selected in [24](SOURCES.md#F-d0dc0be47c) of the [79](SOURCES.md#F-598345fdb6) models, more often than phosphorus load ([21](SOURCES.md#F-b942d93bdc)) and less often than nitrogen load ([49](SOURCES.md#F-41020bdbbd)).</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-S4 "What this claim rests on")</sup>

## 2. The exchange rates

<span class="claim" data-claim="C-OB-OX-PRICES">If oxygen is the currency, then every substance that consumes it has a price, and the prices differ by more than an order of magnitude. These follow from the balanced equations:</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-PRICES "What this claim rests on")</sup>

| substance | oxygen consumed per kg | kg needed to equal a kilogram of nitrogen |
|---|---:|---:|
| Nitrogen, full remineralisation route | [19.70](SOURCES.md#F-4a2fc9ec3d) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [1.0](SOURCES.md#F-eb6fd0b3fa) |
| Nitrogen, carbon route only | [15.13](SOURCES.md#F-36abe384e1) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [1.3](SOURCES.md#F-ad341af349) |
| Nitrogen, nitrification only | [4.57](SOURCES.md#F-48153903b6) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [4.3](SOURCES.md#F-c13f1469ec) |
| Organic carbon | [2.66](SOURCES.md#F-a93bf4456d) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [7.4](SOURCES.md#F-1bc29f8ca0) |
| Fat (tripalmitin) | [2.87](SOURCES.md#F-51d1d0c8a0) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [6.9](SOURCES.md#F-801899860f) |
| Carbohydrate | [1.07](SOURCES.md#F-f6908db63e) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [18.5](SOURCES.md#F-358a37c243) |
| Sulphide sulphur | [2.00](SOURCES.md#F-244f52a3b5) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [9.9](SOURCES.md#F-95f134ea58) |
| Methane | [3.99](SOURCES.md#F-9379552aed) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [4.9](SOURCES.md#F-c5de7907b0) |
| Ferrous iron | [0.14](SOURCES.md#F-c4f316f3ea) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [137.5](SOURCES.md#F-fac91a73b2) |
| COD, by definition | [1.00](SOURCES.md#F-a6a1dd69b6) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> | [19.7](SOURCES.md#F-3508ae6346) |

<span class="claim" data-claim="C-OB-OX-CEILING">So a kilogram of nitrogen, taken all the way through growth and remineralisation, consumes **[19.7](SOURCES.md#F-4a2fc9ec3d) kg of oxygen** — the largest figure in the table, and the reason the nitrogen route is taken seriously. But that is a *ceiling reached only if every step completes*: the nitrogen must be bioavailable, must be limiting, must actually be taken up, the biomass must die in place rather than be exported or eaten, and it must decay where the oxygen matters.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-CEILING "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-OX-FAT">Fat pays **[2.87](SOURCES.md#F-51d1d0c8a0) kg <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> per kg** and skips every one of those conditions. It arrives already made. It does not need to be limiting, taken up, or grown. Roughly **[6.9](SOURCES.md#F-801899860f) kg of fat** matches the full theoretical oxygen demand of a kilogram of nitrogen — and **[1.6](SOURCES.md#F-e876fe8041) kg** matches what a kilogram of ammonium consumes by nitrification alone.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-FAT "What this claim rests on")</sup>

> <span class="claim" data-claim="C-OB-OX-ACCOUNTING">The requirement is set in nitrogen: DCE compute it from each water body's relation between nitrogen input and total-nitrogen concentration. Danish input accounting does carry an oxygen-demand measure — DCE's marine strategy note reports organic matter as `BI5`, a biological oxygen demand, beside nitrogen and phosphorus — but organic matter is not among the candidate variables of the statistical models.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-ACCOUNTING "What this claim rests on")</sup>

## 3. Eight combinations

<span class="claim" data-claim="C-OB-OX-EIGHT">Take the three things the chain joins — nitrogen loaded, oxygen low, higher life gone — and enumerate the eight combinations. A mechanism exists for each one; the table names one or more for each, and says whether the indicators tell it apart.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-EIGHT "What this claim rests on")</sup>

| N loaded | <span class="chem" data-chem="O2" title="oxygen (dissolved, as a molecule)">O₂</span> low | life gone | what produces this state | do the indicators distinguish it? |
|:-:|:-:|:-:|---|---|
| ● | ● | ● | The assumed case. Nutrient enrichment, a bloom, its collapse, oxygen drawn down, the fauna killed. This one is real and does happen. | yes |
| ● | ● | ○ | Seasonal hypoxia in a system whose fauna is adapted to it, or a deficit short enough that mobile fauna leave and return. | no — an oxygen trigger fires either way |
| ● | ○ | ● | Nitrogen present, water well oxygenated, fauna gone anyway: toxicants, antifoulants, pharmaceutical residues, ammonia toxicity, or physical destruction by trawling and dredging. Oxygen is not the only way to kill. | no |
| ● | ○ | ○ | A loaded but well-flushed system. Køge Bugt's flushing time is [73](SOURCES.md#F-d44427aa79) days. The same load in a slower water is not the same pressure, and a load coefficient fitted in one water and transferred to another carries the first water's flushing with it. | no |
| ○ | ● | ● | Oxygen consumed by material that arrived already made — the toilet-flush case — or by sulphide from the sediment, or by decay after a kill of another cause. No nitrogen needed at any step. | no |
| ○ | ● | ○ | A naturally hypoxic basin with its own community: silled basins and fjords with restricted circulation, the Black Sea among them, and the sediment just below any bed, where oxygen reaches from under a millimetre to a few centimetres. | no |
| ○ | ○ | ● | A killed but oxygenated water: a toxic spill, a smothering, a dredged or trawled bed. Nothing in the nutrient chain is engaged. | no |
| ○ | ○ | ○ | Health, or a nutrient-poor water that was never productive. The chlorophyll indicator scores an unproductive water and a healthy one the same way. | partly |

<span class="claim" data-claim="C-OB-OX-INDICATORS">Reading down the last column: the indicator set responds to low oxygen and to high chlorophyll. It cannot tell a water killed by nutrients from a water killed by something else. The fauna indicator's soft-bottom survey, which the national programme runs between the first of March and the end of May, comes after the winter, before the summer, and months after an autumn kill.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-INDICATORS "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-OX-HAZARD">And the toxicant column is not monitored in the sea in this layer. The water-plan register's hazardous-substance layer holds [256](SOURCES.md#F-9edac16b2c) points: [152](SOURCES.md#F-076f9f4115) in lakes, [104](SOURCES.md#F-0b7a823dec) in rivers and [0](SOURCES.md#F-7730f288be) in coastal or marine water. Of Denmark's [123](SOURCES.md#F-9b5234765d) marine water bodies, [123](SOURCES.md#F-0547fd3d18) have none, covering [43,579](SOURCES.md#F-4b32a6117c) km² - [100](SOURCES.md#F-97ad0adf55)% of the sea. Across those freshwater points the matrices measured are biota [253](SOURCES.md#F-bd4eb32548), water [174](SOURCES.md#F-6f95225e78) and sediment [5](SOURCES.md#F-21ba8df2cc).</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-HAZARD "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-OX-DOME">The international ICES DOME archive holds Danish marine sediment contaminant data. This project's notes on its Danish sediment file record organotins, TBT among them, measured for a run of years and then almost not at all; the analysis behind those notes is not stored as a script.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-DOME "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-OX-POISON-UNTESTED">So a hypothesis in which the seabed was poisoned rather than suffocated is not tested by the programme that sets the requirement: no toxicant is among its candidate variables, and its hazardous-substance layer has no marine point.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-POISON-UNTESTED "What this claim rests on")</sup>

## 4. Low oxygen is not the same as no life

<span class="claim" data-claim="C-OB-OX-LOWLIFE">This is the combination that sounds contrived, and it is well documented. In marine sediment oxygen reaches from under a millimetre in active mud to a few centimetres in permeable sand, and below that hypoxic and anoxic conditions are the norm. Where hypoxic water carries nitrate, sulphur-oxidising bacteria — *Beggiatoa*, *Thioploca* — often form thick mats that blanket the sediment: specific hypoxic ecosystems with their own specialised fauna. Under severe oxygen shortage, foraminifera, nematodes and soft-bodied worms are typically favoured.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-LOWLIFE "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-OX-NOTFAUNA">So an oxygen reading near zero is consistent with an active, specialised community. What it is not consistent with is the particular assemblage of large, slow, long-lived animals that people mean by a living seabed: the contribution of animals falls as oxygen drops, and sulphide is toxic to them. Those two statements are different, and the indicator makes only the first one.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-NOTFAUNA "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-OX-CHL">The inverse holds as well. **Chlorophyll is a biomass measure.** A low chlorophyll reading scores as good status whether the water is healthy or too poor, too dark or too poisoned to produce anything, and a high reading scores as bad whether it comes from a nutrient-choked soup or a productive season in a healthy sea. DCE's indicator averages May to September, following the EU-intercalibrated chlorophyll indicator. By their account phosphorus mostly governs chlorophyll in spring, but because spring is outside that indicator, *"er det kvælstoftilførslen, der oftest udvælges som forklaringsvariabel"*.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-CHL "What this claim rests on")</sup>

> <span class="claim" data-claim="C-OB-OX-QUANTITY">Neither chlorophyll nor oxygen is a measure of ecological state. Both are measures of *quantity* — how much biomass, how much dissolved gas — standing in for a claim about *composition*: which organisms are there. A system can lose every large animal it had and still rise in both biomass and productivity.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-QUANTITY "What this claim rests on")</sup>

## 5. What follows

<span class="claim" data-claim="C-OB-OX-NMATTERS">None of this shows that nitrogen does not matter. The full remineralisation route is the most oxygen-expensive line in the table, and where a system is nitrogen-limited and poorly flushed, reducing nitrogen will reduce oxygen demand. That much is sound.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-NMATTERS "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-OX-FOLLOWS">What it shows is that the requirement is set in one currency, nitrogen, while the oxygen it protects has many debtors, and of the eight combinations the indicators single out one and partly a second. The fix is not a different target — it is an oxygen-demand budget alongside the nutrient budget, fauna surveys timed to catch a kill as well as the spring, and sediment toxicant measurement in the programme that actually sets the requirement.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OX-FOLLOWS "What this claim rests on")</sup>

