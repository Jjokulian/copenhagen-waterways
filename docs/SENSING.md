# A dense network for the thing nobody measures

[`X23`](EXPERIMENTS.md) asks whether the faecal payload reaches the water or is spent
in the soil, and answers it at a handful of paired catchments. This page asks the
harder version of the same question: **what would it take to measure it everywhere**,
so that no result anywhere has to be extrapolated to a place nobody visited.

That is the whole point. Denmark's load figure is a modelled surface stretched over
[49% measured and 51% modelled catchment area](NITROGEN.md), and the objection this
project keeps making is not that the model is bad but that **a partition is not a
measurement**. A network dense enough to have a node on every stream that reaches the
sea would end that argument by removing its subject.

**This page is a construction, not a proposal anyone has funded.** Prices are stated
ranges rather than quotations, the sensor choices are ordinary catalogue parts, and
nothing here has been built by this project. What it is for is to make the thing
costed and concrete enough that a disagreement about it is a disagreement about
numbers.

---

## The fingerprint, which is what replaces the sensor that does not exist

If no instrument reports *manure*, the alternative is to measure many things and ask
which combination only manure produces. That is a fingerprint: **not a measurement but
a position in a measurement space**, and the question for each candidate tracer is not
*is it present* but *what else could have put it there*.

### The tracers, and what each one rules out

| Tracer | Why it is faecal | What it is confounded with | What resolves that |
|---|---|---|---|
| **Coprostanol** (5β-cholestan-3β-ol) | Made by gut bacteria reducing cholesterol. Vertebrate guts make it; soil does not | Any warm-blooded gut, including humans and wildlife | the ratios below |
| **24-ethylcoprostanol / coprostanol** | Plant sterols reduced in a herbivore gut | — | **This ratio separates herbivore from human.** High ethyl form: cattle, pigs on plant feed. Low: human sewage |
| **Coprostanol / (coprostanol + cholestanol)** | Above ~0.7 is the accepted faecal threshold | in-situ reduction in anoxic sediment can mimic it slightly | pair with the marker below |
| **Host-specific *Bacteroidales* by qPCR** — Pig-2-Bac, BacR, HF183 | Gut microbiota are host-specific to the genus level | Nothing, in terms of source | **This is the attribution instrument.** DNA decays in days to weeks, so it reports *recent* input only |
| **crAssphage** | A human-gut bacteriophage | Nothing else has it | Establishes the human baseline, so the rest can be assigned elsewhere |
| **Acesulfame-K, carbamazepine** | Human diet and human medicine; conservative and persistent | Nothing agricultural | **Marks the human fraction independently of biology** — a chemical crosscheck on the microbial one |
| **Tylosin, tetracyclines, ivermectin** | Given to livestock, not to people at these volumes | Veterinary use in pets, at trivial scale | Quantifies the livestock fraction; VetStat holds the sales that would calibrate it |
| **Copper and zinc** | Feed additives, and conservative once in sediment | **Heavily**: brake pads, roofs, tyres, urban runoff | Useless alone in a mixed catchment; useful in a rural one, and useful as a *load* once the fraction is known |
| **δ¹⁵N of nitrate** | Manure and sewage nitrogen is isotopically heavy (+10 to +20‰); synthetic fertiliser sits near 0‰ | **Denitrification enriches δ¹⁵N too**, which has fooled people for decades | Measure **δ¹⁸O of nitrate alongside it**: denitrification moves both together on a known slope, a source change does not |
| **fDOM, tryptophan-like (peak T) vs humic-like (peak C)** | Protein-like fluorescence rises with fresh faecal and sewage organic matter; humic-like rises with soil | turbidity, temperature, iron | Correctable, and it is the only one of these that can run continuously — which is its whole value |

### The quantifier

**There is no single number that is "the faecal load", and a page that offered one
would be doing what this project spends its length objecting to.** What there is, is a
mixing model with an uncertainty on it:

1. Pick **end members** — pig slurry, cattle slurry, human sewage, soil organic matter,
   and if the catchment has one, treated effluent. Each is sampled directly, so its
   own fingerprint is measured rather than assumed.
2. Solve for the **fractions** that reproduce the observed tracer vector at the
   stream. With more tracers than sources the system is over-determined, which is what
   allows an *estimate of error* rather than only an answer.
3. Multiply the faecal fraction by the **measured load** — concentration times
   discharge at the same minute — to get mass per event, per season, per year.

So the quantifier is **kilograms of pig-derived organic matter past this point in this
storm**, with a confidence interval, and it decomposes into the same units for cattle,
for people, and for soil. That is the number the national account has never had, and
the reason it has never had it is that nobody measured the end members.

### General sensors give totals; discriminating tracers give shares

The two kinds of measurement do different jobs and the design needs both, which is
worth saying plainly because a network of only one kind is a waste of money.

- A **general observable** — turbidity, COD, total nitrogen, oxygen — measures *how
  much of something is here*, and cannot say where it came from. It is cheap,
  continuous, and it is the quantity that actually matters to a fjord.
- A **discriminating tracer** — coprostanol, Pig-2-Bac, acesulfame, δ¹⁵N — measures
  *whose it is*, and by itself says nothing about magnitude. It is expensive,
  episodic, and useless as a load.

**The product of the two is the thing nobody has.** A discriminating tracer that rises
in proportion to the material carrying it converts a total into a share: measure the
tracer, apply the ratio of tracer to bulk in that source, and you have the fraction of
the total that came from it — in kilograms, at that minute, past that point.

### Which lets you subtract, one source at a time

That is the operating principle, and it generalises past faeces to every pathway on
this site:

1. **Measure the totals continuously** with the cheap sensors, everywhere.
2. **Measure the fingerprint episodically** at the same points, and convert each
   resolved source into its contribution to each total.
3. **Subtract it.** What is left is a residual with one fewer explanation in it.
4. **Repeat for the next fingerprint** — road runoff by its own markers, human sewage
   by acesulfame and crAssphage, industrial by whatever is specific to it — and each
   subtraction cleans the residual the next estimate is made on.

Done across enough tracers, the outcome is a **decomposition of the load rather than
an attribution of it**: this much of tonight's oxygen demand was pig, this much human,
this much road, this much soil, and this much is still unexplained.

> **And the last number is the honest one.** This method is the residual method — the
> same operation the ~70% figure is built on, which this project spends
> [NITROGEN.md](NITROGEN.md) taking apart. It is only better if it obeys three rules
> the original does not: **every subtraction is a measurement rather than a model**,
> **the error propagates and is published with the number**, and **the final residual
> is never named after a source.** An unexplained remainder is an unexplained
> remainder. The moment it gets called *agriculture*, this becomes the thing it was
> built to replace.

**The proportionality is an assumption and has to be measured, not asserted.** The
ratio of coprostanol to organic matter in pig slurry varies with diet, storage and
digestion; DNA markers decay on a timescale of days; sterols do not. So each ratio is
established by sampling the end members directly — the tank, the plant effluent, the
road gully — and re-established when the system changes. A conversion factor taken
from a paper about another country's pigs is exactly the kind of borrowed coefficient
this project objects to everywhere else.

### Why a fingerprint is more trustworthy than any of its dimensions

Each tracer above has a confounder. The design answer is not a better tracer, it is
**agreement across independent measurement spaces**: sterol chemistry, microbial
genetics, pharmaceutical chemistry, stable isotopes and optics fail in unrelated ways,
so a source assignment that survives all five is not an artefact of any one of them.
A signal visible in one dimension and absent from the other four is noise wearing a
name — and the discipline that says so is the same one this project applies to
[partitions and baskets](../README.md): **a boundary that holds under every metric you
try is the only kind worth calling real.**

That has a practical consequence for the network below. The dense tier measures the
cheap, continuous, ambiguous dimensions; the sparse tier measures the expensive,
unambiguous ones; and **the calibration between them is per-site, not national**. The
continuous proxies are trusted only where the laboratory has stood in the same water.

---

## Which is why the architecture is forced

**There is no faecal sensor.** Nothing you can put in a stream reports "manure". What
exists is the fingerprint above — and it splits cleanly by what can be automated. The
continuous dimensions are cheap and ambiguous; the dimensions that identify a source
are laboratory measurements and cannot be put on a pole. So the architecture is forced,
and it is two-tier:

| | What it does | What it cannot do |
|---|---|---|
| **Tier 1 — dense, continuous, cheap** | says **when and where** something moved, at every site, all the time | say **what** it was |
| **Tier 2 — sparse, event-triggered, expensive** | says **what it was**, by laboratory attribution | be everywhere |

Tier 1 without tier 2 is a network of interesting wiggles. Tier 2 without tier 1 is the
existing monitoring programme: a fortnightly visit that misses the event. **The design
is the coupling** — tier 1 decides when tier 2 fires.

---

## Tier 1 — the node anyone can build

Five measurements, in rough order of value per krone.

| Sensor | What it is for | Stated cost, DKK |
|---|---|---:|
| **Water level** — ultrasonic ranger above the surface, or a vented pressure transducer | Without discharge there is no load, only a concentration. This is the sensor that turns the network from anecdote into accounting. Mounted above water, an ultrasonic head does not foul | 1,000–3,000 |
| **Turbidity** — nephelometric, 90°, with a wiper | The carrier. Metals, phosphorus, tyre wear and faecal particles all travel attached to sediment, so turbidity is the single best proxy for *payload in transit* | 1,500–6,000 |
| **Conductivity and temperature** | Separates dilution from delivery. A storm that dilutes conductivity while raising turbidity is surface wash; a rise in both is something else. Temperature is needed by every other reading | 500–2,000 |
| **fDOM — tryptophan-like fluorescence** | The one fingerprint dimension that can run continuously. Protein-like fluorescence tracks fresh faecal and sewage organic matter; measured against a humic-like channel it separates that from soil-derived matter. It is the cost driver, and the sensor that makes this network more than a turbidity network | 8,000–20,000 |
| **Dissolved oxygen** — optical | The receiving-water consequence, at the same minute as the cause | 3,000–8,000 |

**Logger, power and communications**, which are the boring part and the part that
decides whether the thing survives a winter:

| | | Stated cost, DKK |
|---|---|---:|
| Microcontroller, RTC, SD card, watchdog | ESP32 class; log locally as well as transmit, because the network is the thing that fails | 300–800 |
| Radio | LoRaWAN to a community gateway where one is in range; NB-IoT or LTE-M with a data SIM where none is | 200–700 |
| Power | 10–20 W panel, LiFePO₄, charge controller. Danish December is the design case, not July | 800–2,500 |
| Enclosure, mount, cable, desiccant | IP67, mounted to a road culvert or bridge parapet | 700–2,000 |

**A node comes to roughly 5,000–12,000 DKK without fDOM and 15,000–30,000 with it.**
One person can build one in an evening. The hard part was never the electronics.

---

## The shopping list

Everything above as a list of things to buy, because a cost is only real when it is a
purchase order. **Part names are examples of the class, not endorsements, and no price
here is a quotation** — they are the stated ranges a buyer should expect to find and
then replace with what a supplier actually says.

### The node — what one stream costs

| | Example of the class | What it is for | DKK |
|---|---|---|---:|
| **Stage, ultrasonic** | MaxBotix HRXL-WR class, IP67, mounted above the water on a bridge or culvert | Level → discharge, via a rating curve. **Mounted in air, so it cannot foul** — which is why it beats a pressure transducer for an unattended node | 900–1,800 |
| *or* **Stage, pressure** | vented submersible transducer, 0–2 m | Where there is no overhead mounting. Vented cable, or it reads the weather | 1,200–3,000 |
| **Turbidity, nephelometric** | ISO 7027 90° module; with a wiper if the budget reaches | The carrier for everything particulate. **The cheap analog boards sold for hobby use are presence/absence at best** — say so in the data or do not fit one | 1,500–6,000 |
| **Conductivity + temperature** | Atlas Scientific EZO-EC with a K=1.0 probe, or an industrial two-electrode cell | Separates dilution from delivery, and every other reading needs the temperature | 600–2,000 |
| **Dissolved oxygen, optical** | luminescent/optical DO probe — **not** a galvanic membrane cell, which drifts and dies | The consequence, measured at the same minute as the cause | 3,000–9,000 |
| **fDOM, tryptophan channel** | Turner Cyclops-7F class, tryptophan configuration, with a humic-like channel if affordable | The one fingerprint dimension that runs continuously. **This is the difference between a turbidity network and a fingerprint network** | 9,000–22,000 |
| **Logger + radio** | ESP32 with LoRaWAN, or with LTE-M/NB-IoT where no gateway is in range; RTC, microSD, watchdog | Logs locally *and* transmits. The radio is the least reliable part | 400–1,200 |
| **Power** | 10–20 W panel, MPPT controller, 12 V LiFePO₄ 20 Ah | Sized for December, not July | 800–2,500 |
| **Enclosure and mount** | IP67 box, cable glands, stainless bracket, desiccant, anti-theft | Survives a winter and a curious passer-by | 700–2,000 |

**A node without fDOM: 5,000–12,000 DKK. With it: 15,000–30,000.**

### The kit a group shares

| | Why | DKK |
|---|---|---:|
| Formazin turbidity standards, EC calibration solutions, DO zero solution | **A reading without a calibration record is not data.** This is the least glamorous line and the one that decides whether the network is admissible | 2,000–5,000 |
| A reference sonde, borrowed or shared, for co-location | [`X16`](EXPERIMENTS.md) — the check that ties cheap readings to the national record | 15,000–60,000, or borrowed |
| Spare probes, cable, glands, desiccant, one spare node | Field repairs happen in February in the rain | 5,000–10,000 |

### The sampler, which is where the answer comes from

| | | DKK |
|---|---|---:|
| Automatic sampler, 12–24 bottles, flow- and turbidity-triggered | Teledyne ISCO or Hach AS950 class; a used one is a perfectly good used one | 25,000–60,000 |
| Bottle analysis — sterols, host markers, crAssphage, acesulfame, one veterinary residue, Cu/Zn, COD/BOD, nutrients, δ¹⁵N + δ¹⁸O | **The real cost of the experiment.** Not every bottle needs the full panel; the cheap determinands go on all of them and the fingerprint on the ones the continuous tier says matter | 1,500–4,000 per bottle |

### What that means for the experiment on the next page

| | Quantity | DKK |
|---|---:|---:|
| Nodes with fDOM, 12 matched pairs | 24 | 360,000–720,000 |
| Samplers, rotating | 8 | 200,000–480,000 |
| Shared kit, three regional sets | 3 | 60,000–200,000 |
| Bottles analysed over two seasons | ~600 | 900,000–2,400,000 |
| **Hardware and laboratory, total** | | **1.5–3.8 M DKK** |

**So the sensors are not the expensive part — the bottles are**, and the bottles are
the part that cannot be economised without losing the attribution the whole design
exists for. A node is a weekend and a few thousand kroner. The laboratory is the
commitment.

---

## Tier 2 — the sampler that answers the question

An automatic sampler, triggered by tier 1 when stage or turbidity crosses a threshold,
filling bottles through the rising and falling limb of a storm. **This is where the
attribution comes from**, because it is a laboratory measurement and there is no
in-situ substitute:

- **faecal sterols — coprostanol, and its ratio to cholesterol**, which distinguishes
  faecal organic matter from soil organic matter;
- **host-specific microbial markers** (pig-, ruminant- and human-associated
  *Bacteroidales* by qPCR), which distinguish a pig from a person — the measurement
  that makes the whole argument attributable rather than suggestive;
- **copper and zinc**, conservative, and from feed;
- **one veterinary antiparasitic residue**, because the register that holds the sales
  data holds nothing about where it went;
- **COD and BOD**, to tie the fluorescence proxy to a standard number.

Stated: **25,000–60,000 DKK per sampler**, and **1,500–4,000 DKK per bottle analysed**,
which is why tier 2 is sparse and event-triggered rather than continuous. Twenty
samplers rotating around a network of hundreds of nodes is the realistic shape.

---

## What that costs, at three sizes

> **[Dial it yourself →](network.html)** — the density on a map of Denmark, what each
> node carries, the sampler ratio, the bottle price, the servicing interval and the
> years, with the total moving as you change them. The presets reproduce the stages
> in [SETTLE.md](SETTLE.md).


Every Danish stream that reaches the sea is the target that removes extrapolation
entirely. These are stated arithmetic, not a budget anybody has approved.

| | Nodes | Tier-1 hardware | fDOM on a subset | Samplers | Total hardware |
|---|---:|---:|---:|---:|---:|
| **A person, one catchment** | 5 | 40,000 | — | — | **~40,000 DKK** |
| **A club or a municipality** | 40 | 320,000 | 5 × 20,000 | 2 × 40,000 | **~500,000 DKK** |
| **Every outlet in the country** | 800 | 6.4 M | 80 × 20,000 | 20 × 40,000 | **~8.8 M DKK** |

For comparison, the same page that argues for this puts a single bored pipe shot at
160,000–640,000 DKK. **The national network is the price of about twenty streets.**

The recurring cost is not the hardware and never was:

- **Servicing.** A fouled sensor produces confident wrong numbers, which is worse than
  no sensor. Budget two to six visits a year per node, and prefer the sensor that
  fouls least even where it reads worst.
- **Calibration.** Every node needs a documented calibration history and a co-location
  against a reference instrument — which is [`X16`](EXPERIMENTS.md), already written.
- **Laboratory.** The tier-2 bottles, which is where the money actually goes.

---

## The data path, which is the easy part

    node ──LoRaWAN/NB-IoT──▶ gateway ──MQTT──▶ broker ──▶ time-series store
                                                            │
                                              raw archive ──┼──▶ public API
                                                            └──▶ static site

Concretely: an MQTT broker on a small VM, a time-series database, a nightly dump of
raw readings to object storage, and a static site generated from it — the same shape
as this repository, which is built from public data by scripts and costs nothing to
host. **Software is not the constraint and has not been for years.**

Five rules matter more than the stack:

1. **Log locally as well as transmit.** The radio is the least reliable component.
2. **Publish raw counts, not just calibrated values.** A recalibration must be
   reproducible after the fact, which means the uncalibrated series has to survive.
3. **Every reading carries its node's calibration state and last service date.** A
   series without that is not evidence.
4. **Public API from day one, and open licence.** The argument this network exists to
   settle is one that gated data created.
5. **Never publish an index without the series it came from.** That is the failure
   this whole project documents, and it would be humiliating to reproduce it.

---

## What one person can do, and what needs many

**One person can build a node, mount it on a culvert, and produce a defensible record
of one stream.** That is not a small thing: it is one place, measured, with a date —
and [the argument this project makes about plurality](PLACES.md) is that a place
measured is worth more than a place modelled.

**What one person cannot do is cover a country**, and the spread is the whole value.
The network's power is that it removes extrapolation, and it only removes it where
somebody stood in the water. So the shape of it is a hundred people with one node each
and a shared protocol, not one institution with a plan — which is also the only shape
that gets built without anybody's permission.

Three things would have to be shared for that to work and none of them is hard: **the
build**, so nodes are comparable; **the calibration protocol**, so their readings are;
and **the archive**, so a result belongs to everyone rather than to whoever hosted it.

---

## What this would and would not settle

**Would.** Whether the payload moves in events, where, how often, and in what season —
across the whole country rather than at 240 stations sampled on a calendar. Whether
the spreading window shows up in the water. Which catchments are quiet and which are
not, without a model in between.

**Would not.** Anything about the sea beyond the outlet: this measures what arrives,
not what it does. Anything the tier-2 list does not include. And **it does not abolish
inference** — attribution still travels from sampled events to unsampled ones, and
from a marker to a source. What it abolishes is *spatial* extrapolation, which is the
one this project has spent its length objecting to.

> **The honest summary.** The instruments exist, the protocol is ordinary, the cost is
> the price of twenty streets, and nobody has done it. That is not a technical finding.
> It is a statement about what the monitoring system was built to answer, and about
> who has been allowed to ask.
