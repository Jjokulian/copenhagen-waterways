# What actually removes the oxygen

The requirement is built on a chain: nitrogen makes algae, algae make oxygen depletion, oxygen depletion kills the seabed, and a dead seabed puts fedtemøg on a shore. In use, each arrow gets read as an implication in both directions, so that measuring one link counts as measuring all of them.

Every joint in that chain comes apart. This page takes them one at a time, and nothing on it depends on anyone's model — the coefficients are arithmetic on balanced equations, and the coverage counts come from the national monitoring layers.

## 1. Oxygen is a balance, not a substance that nitrogen removes

An oxygen deficit is what is left when demand exceeds supply. Both sides have many entry points, and most of them require no nitrogen at all.

### Routes that consume oxygen

| route | stoichiometry | needs N? | representable in the statistical layer? |
|---|---|:-:|---|
| Respiration of algal biomass grown in place | 19.7 g O₂ per g N | yes | load terms |
| Respiration of organic matter that arrived already made | 1.0 g O₂ per g COD | **no** | no |
| Nitrification of ammonium | 4.57 g O₂ per g N | yes | no |
| Oxidation of sulphide from disturbed sediment | 2.00 g O₂ per g S | **no** | no |
| Oxidation of ferrous iron and manganese | 0.14 g O₂ per g Fe | **no** | no |
| Oxidation of methane | 3.99 g O₂ per g CH₄ | **no** | no |
| Decay following a kill of any cause | as the material, above | **no** | no |

**Respiration of algal biomass grown in place.** The route the requirement is built on. Nitrogen becomes carbon at Redfield stoichiometry, the carbon is respired, and the organic nitrogen is nitrified.

**Respiration of organic matter that arrived already made.** Sewage organics, fat, riverine particulate carbon, anything washed off a surface. COD *is* the oxygen it will consume — the measurement and the effect are the same quantity. No growth step, no nitrogen anywhere in it.

**Nitrification of ammonium.** Purely chemical demand: ammonium is oxidised and the oxygen is gone. This is nitrogen acting as a *reductant*, not as a fertiliser, and it happens whether or not anything grows.

**Oxidation of sulphide from disturbed sediment.** Anoxic sediment holds sulphide. Trawling, dredging, dumping, a storm or a propeller brings it into contact with oxygenated water and it is consumed immediately.

**Oxidation of ferrous iron and manganese.** Same mechanism, smaller per gram, released from the same reduced sediment.

**Oxidation of methane.** Produced in anoxic sediment and consumed on its way up.

**Decay following a kill of any cause.** A toxicant, a salinity shock, a heat event, physical destruction. Whatever kills leaves a mass that decays, and the bacterial bloom on it draws the oxygen down. The oxygen deficit is then downstream of the killing agent, and carries no information about it.

### Routes that fail to resupply oxygen

| route | coefficient | representable? |
|---|---|---|
| Warming reduces how much the water can hold | ≈ −2.3% per °C at 10–20 °C | temp |
| Stratification blocks resupply from above | no coefficient | BV |
| Light attenuation cuts photosynthetic oxygen production | no coefficient | irr |
| Reduced wind mixing | no coefficient | vind |

**Warming reduces how much the water can hold.** Solubility, not biology. Surface temperature is a candidate variable, so this one is at least representable.

**Stratification blocks resupply from above.** A column that does not turn over does not refill. Present as a candidate variable (`vandsøjlestabilitet`) and selected in 13 of 72 models.

**Light attenuation cuts photosynthetic oxygen production.** The same turbidity that the Kd indicator measures also suppresses the oxygen source. Kd is measured *as an outcome* and never enters as a driver.

**Reduced wind mixing.** Wind stress is a candidate variable. It appears in 24 of the 72 models, more often than several nutrient terms.

## 2. The exchange rates nobody publishes

If oxygen is the currency, then every substance that consumes it has a price, and the prices differ by more than an order of magnitude. These follow from the balanced equations and nothing else:

| substance | oxygen consumed per kg | kg needed to equal 1 kg of nitrogen |
|---|---:|---:|
| Nitrogen, full remineralisation route | 19.70 kg O₂ | 1.0 |
| Nitrogen, carbon route only | 15.13 kg O₂ | 1.3 |
| Nitrogen, nitrification only | 4.57 kg O₂ | 4.3 |
| Organic carbon | 2.66 kg O₂ | 7.4 |
| Fat (tripalmitin) | 2.87 kg O₂ | 6.9 |
| Protein | 1.50 kg O₂ | 13.1 |
| Carbohydrate | 1.07 kg O₂ | 18.5 |
| Sulphide sulphur | 2.00 kg O₂ | 9.9 |
| Methane | 3.99 kg O₂ | 4.9 |
| Ferrous iron | 0.14 kg O₂ | 137.5 |
| COD, by definition | 1.00 kg O₂ | 19.7 |

So a kilogram of nitrogen, taken all the way through growth and remineralisation, consumes **19.7 kg of oxygen** — the largest figure in the table, and the reason the nitrogen route is taken seriously. But that is a *ceiling reached only if every step completes*: the nitrogen must be bioavailable, must be limiting, must actually be taken up, the biomass must die in place rather than be exported or eaten, and it must decay where the oxygen matters.

Fat pays **2.87 kg O₂ per kg** and skips every one of those conditions. It arrives already made. It does not need to be limiting, taken up, or grown. Roughly **6.9 kg of fat** matches the full theoretical oxygen demand of 1 kg of nitrogen — and **1.6 kg** matches what a kilogram of ammonium actually consumes on its own, without any biology at all.

> Neither figure appears in any Danish accounting. The load statement is in tonnes of nitrogen and tonnes of phosphorus. There is no oxygen-demand column, so the substances that consume oxygen without containing nitrogen are not smaller in the account — they are **absent from it**.

## 3. The chain is severable at every joint

Take the three things the chain conflates — nitrogen loaded, oxygen low, higher life gone — and enumerate the eight combinations. A real mechanism exists for each one.

| N loaded | O₂ low | life gone | what produces this state | do the indicators distinguish it? |
|:-:|:-:|:-:|---|---|
| ● | ● | ● | The assumed case. Nutrient enrichment, a bloom, its collapse, oxygen drawn down, the fauna killed. This one is real and does happen. | yes |
| ● | ● | ○ | Seasonal hypoxia in a system whose fauna is adapted to it, or a deficit short enough that mobile fauna leave and return. Common in fjords with an annual cycle. | no — an oxygen trigger fires either way |
| ● | ○ | ● | Nitrogen present, water well oxygenated, fauna gone anyway: toxicants, antifoulants, pharmaceutical residues, ammonia toxicity, or physical destruction by trawling and dredging. Oxygen is not the only way to kill. | no |
| ● | ○ | ○ | A loaded but well-flushed system. Køge Bugt's flushing time is 73 days; the Limfjord broads are far longer. The same load in the two places is not the same pressure, and the load term does not know which it is in. | no |
| ○ | ● | ● | Oxygen consumed by material that arrived already made — the toilet-flush case — or by sulphide from disturbed sediment, or by decay after a kill of another cause. No nitrogen needed at any step. | no |
| ○ | ● | ○ | A naturally anoxic or hypoxic basin with its own community. Deep sills, the Black Sea below 150 m, the millimetre beneath any marine sediment surface. | no |
| ○ | ○ | ● | A killed but oxygenated water: a toxic spill, a smothering, a dredged or trawled bed. Nothing in the nutrient chain is engaged. | no |
| ○ | ○ | ○ | Health, or a nutrient-poor water that was never productive. The chlorophyll indicator scores an unproductive water and a healthy one the same way. | partly |

Reading down the last column: the indicator set fires on low oxygen and on high chlorophyll. It cannot see the difference between a water killed by nutrients and a water killed by something else, because the *only* fauna instrument is a soft-bottom survey run 1 March–31 May — after the winter, before the summer, and months after an autumn kill.

And the toxicant column is not monitored either — not in this layer. Of Denmark's 123 marine water bodies, **0 have a hazardous-substance monitoring point in the water-plan register** and 123 have none, covering 43,579 km² — 100% of the sea. Across all 256 points nationally, the matrices measured are biota 253, water 174, and **sediment 5**.

Sediment is where persistent toxicants accumulate, and where a benthic animal actually lives. In the water-plan layer it is flagged at five of those 256 points; biota carries almost all of the rest.

> **A correction, and a narrowing.** An earlier version of this page said sediment is measured at four points *in Denmark*. That generalised one layer — the VP3 hazardous-substance stations — to the whole country, and it was wrong on both counts. The count in that layer is five, and a separate international archive (ICES DOME) holds a longer Danish marine sediment record that this project has not yet verified for itself. The defensible claim is narrower: **the national water-plan monitoring that feeds the assessment looks at biota and water and almost never at the bed**, which is a statement about what the assessment can see rather than about what exists somewhere.

Either way a hypothesis in which the seabed was poisoned rather than suffocated is not tested by the programme that sets the requirement.

## 4. Low oxygen is not the same as no life

This is the combination that sounds contrived, and it is the most solidly established one in the table.

Marine sediment goes anoxic within millimetres of its surface, and that anoxic layer is among the densest microbial habitats on the planet. Sulphide-oxidising bacterial mats — *Beggiatoa*, *Thioploca* — form thick white sheets exactly where oxygen is nearly absent and sulphide is plentiful; they are a *feature* of hypoxic beds, not an absence of life. The Black Sea below about 150 m has been permanently anoxic throughout recorded history and holds an active microbial community throughout. Hypoxia-tolerant nematodes and foraminifera frequently *increase* in abundance under low oxygen, because the things that ate them and competed with them are the things that left.

So an oxygen reading of near zero is consistent with enormous biomass and intense metabolic activity. What it is not consistent with is the particular assemblage of large, slow, long-lived animals that people mean by a living seabed. Those two statements are different, and the indicator makes only the first one.

The inverse holds as well. **Chlorophyll is a biomass measure.** A low chlorophyll reading is scored as good status, and it is equally produced by a healthy meadow-dominated system and by a water too poor, too dark or too poisoned to produce anything. High chlorophyll is scored as bad, and is equally produced by a nutrient-choked soup and by a productive spring in a healthy sea — which is why the indicator is defined on May–September only, cutting out the spring bloom, which in turn is why *"det er kvælstoftilførslen, der oftest udvælges som forklaringsvariabel"* rather than phosphorus. The window is chosen so the nitrogen signal is the one that shows.

> Neither chlorophyll nor oxygen is a measure of ecological state. Both are measures of *quantity* — how much biomass, how much dissolved gas — standing in for a claim about *composition*: which organisms are there. A system can lose every large animal it had and rise in both biomass and productivity. That is not a hypothetical failure mode; it is what the word *primordial soup* describes, and it is what the escalation to fedtemøg looks like from inside the numbers.

## 5. What follows

None of this shows that nitrogen does not matter. The full remineralisation route is the most oxygen-expensive line in the table, and where a system is nitrogen-limited and poorly flushed, reducing nitrogen will reduce oxygen demand. That much is sound.

What it shows is that the account has one column where it needs several. Oxygen demand is the quantity that actually matters, every substance in the water has a price in it, and only one of them is counted. A shore can be wrecked by any of eight paths and the instruments distinguish two. The fix is not a different target — it is an oxygen-demand budget alongside the nutrient budget, a fauna survey that runs in autumn as well as spring, and sediment toxicant measurement in the programme that actually sets the requirement.

