# Fingerprinting Denmark

<span class="claim" data-claim="C-SS-T-LEAD">**The experiment that would end the argument, written so that both sides can commit to it before it runs.**</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-LEAD "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-DESIGN">This page is not an audit of numbers that exist. It is a design for producing numbers that do not exist yet, aimed at a question the dispute turns on and that none of the monitoring this project has profiled measures directly:</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-DESIGN "What this claim rests on")</sup>

> **When Danish fields receive slurry and then rain, what reaches the water — and
> whose is it?**

<span class="claim" data-claim="C-SS-T-NAV">[SENSING.md](SENSING.md) constructs the instrument: the fingerprint meant to separate a pig from a person from a road, and the two-tier network that could carry it.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-NAV "What this claim rests on")</sup> [`X23`](EXPERIMENTS.md) is the entry in the register. **This page is the protocol** — what is claimed, what would refute it, how many catchments and how many storms, and the rules that have to be fixed before the first sampler is bolted to a culvert.

---

## 1. The [3](SOURCES.md#F-ff0b4d5203) hypotheses, stated so they can lose

<span class="claim" data-claim="C-SS-T-HYPS">The point of writing them out is that each makes a different prediction about the same measurements, so the data can pick. They are hypotheses, not findings: this page asserts none of them.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-HYPS "What this claim rests on")</sup>

| | Hypothesis | Predicts |
|---|---|---|
| **The soil reactor** | The field consumes the payload. Labile carbon is respired, ammonium nitrifies, and what leaves is mobile nitrate | Faecal markers stay near baseline through the spreading window. Nitrate rises seasonally, smoothly, with drainage. No relationship between marker peaks and livestock density |
| **The bypass** | Preferential flow, tile drains and rain onto fresh slurry deliver the payload close to intact | Marker and copper peaks within days of spreading, **scaling with livestock density**, concentrated in the rising limb of storms |
| **The regime** | Both are true, in different conditions. The bypass opens only when the ground is frozen, saturated or tile-drained, and closes otherwise | Marker peaks appear at **some** sites and not others, predicted by soil type, drainage and antecedent wetness rather than by livestock density alone |

<span class="claim" data-claim="C-SS-T-EMBARRASS">**The soil reactor is the outcome that would embarrass this project**, since part of its argument leans on the payload mattering. It is stated first on purpose, and the publication rule below is written so that it cannot be quietly dropped.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-EMBARRASS "What this claim rests on")</sup>

---

## 2. What the calendar does for us

<span class="claim" data-claim="C-SS-T-CALENDAR">The manipulation already exists and is applied nationally: Danish rules forbid spreading liquid organic manure and nitrogen fertiliser from after harvest, at the latest the start of October, until February, with exceptions they list.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-CALENDAR "What this claim rests on")</sup> <span class="claim" data-claim="C-SS-T-BEFOREAFTER">So the experiment is **before-after on a fixed national schedule**, with a within-year control window that needs no permission from anyone.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-BEFOREAFTER "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-RAIN">And the events can be counted in advance. In the hourly rainfall record used elsewhere in this project, over Copenhagen, [1995](SOURCES.md#F-78ec4e8ca1)–[2025](SOURCES.md#F-352dc99498), these are the days of each February–April season with at least a given daily total, over its [31](SOURCES.md#F-3f40b547c1) seasons:</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-RAIN "What this claim rests on")</sup>

| Daily total | Median days per season | Range |
|---|---:|---:|
| ≥ [2](SOURCES.md#F-52bdd86b0e) mm | **[21](SOURCES.md#F-535d402cc0)** | [11](SOURCES.md#F-c66170df8f)–[35](SOURCES.md#F-7dda9d14f4) |
| ≥ [5](SOURCES.md#F-9fc767e7c7) mm | **[9](SOURCES.md#F-550ea7f6a2)** | [2](SOURCES.md#F-7d7084f844)–[15](SOURCES.md#F-e89e918a27) |
| ≥ [10](SOURCES.md#F-6b7787ed42) mm | **[2](SOURCES.md#F-3cc2ed8528)** | [0](SOURCES.md#F-271239eab0)–[5](SOURCES.md#F-ddcaac4658) |

<span class="claim" data-claim="C-SS-T-SAMPLE">**That is the sample size, and it is the reason the design works.** A sampler that fires on days of [5](SOURCES.md#F-9fc767e7c7) mm or more would see a median of [9](SOURCES.md#F-550ea7f6a2) such days in a spreading season — a day being a UTC day, so a storm that spans two days counts twice — enough for a paired comparison within a single year, at a single site.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-SAMPLE "What this claim rests on")</sup> <span class="claim" data-claim="C-SS-T-FLOOR">ERA5, the reanalysis behind the record, has a spatial resolution of [31](SOURCES.md#F-f6c410a4f2) km, so each value is an average over a grid cell, which smooths a local downpour: the counts at the higher thresholds are more likely to understate what one catchment sees than to overstate it.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-FLOOR "What this claim rests on")</sup>

---

## 3. The design

**Paired catchments, matched on everything except the thing under test.**

- <span class="claim" data-claim="C-SS-T-D-PAIRS">**[12](SOURCES.md#F-df03937f6f) pairs** — [24](SOURCES.md#F-95eb3d8182) catchments — matched on soil type, drainage class, area and slope, contrasted on **livestock density** from the national register. Small headwater catchments, so a signal is not diluted to nothing before it reaches the sensor.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-D-PAIRS "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-D-TIERS">**Both tiers at every site**: continuous stage, turbidity, conductivity, temperature and fDOM; an autosampler on a flow-and-turbidity trigger.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-D-TIERS "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-D-WINDOWS">**[Two](SOURCES.md#F-c81a8e735b) windows a year**: the spreading window (February–April) and an autumn control window when liquid manure may not be spread. Same sites, same triggers, same laboratory.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-D-WINDOWS "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-D-ENDS">**End members sampled directly**: slurry from the tanks in each catchment, effluent from any plant in it, road gully sediment, and soil. **No conversion ratio is taken from the literature** — every one is measured on the material that is actually there.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-D-ENDS "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-D-YEARS">**[Two](SOURCES.md#F-6e613878d3) full years.** One to establish the ratios and shake out the fouling, one to answer the question.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-D-YEARS "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-D-PANEL">**What is analysed per event:** faecal sterols with the herbivore ratio, host-specific microbial markers, crAssphage, acesulfame, one veterinary residue, copper and zinc, COD and BOD, total and dissolved N and P, and δ¹⁵N with δ¹⁸O of nitrate. Discharge at the same minute, or it is a concentration and not a load.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-D-PANEL "What this claim rests on")</sup>

---

## 4. The decision rules, fixed before the first sample

<span class="claim" data-claim="C-SS-T-R0">These are the whole point of the page. A rule written afterwards is a story.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-R0 "What this claim rests on")</sup>

1. <span class="claim" data-claim="C-SS-T-R1">**The bypass is accepted** if faecal-marker load in the spreading window exceeds the autumn control window by a factor stated in advance at **[two thirds](SOURCES.md#F-ab772b3b88) or more of the high-density sites**, and the effect scales with livestock density across the [twelve](SOURCES.md#F-df03937f6f) pairs.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-R1 "What this claim rests on")</sup>
2. <span class="claim" data-claim="C-SS-T-R2">**The soil reactor is accepted** if marker loads in the two windows are indistinguishable, by a criterion stated in advance, at the sites the first rule looks at, and nitrate is the only determinand that moves.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-R2 "What this claim rests on")</sup>
3. <span class="claim" data-claim="C-SS-T-R3">**The regime is accepted** if the effect is present at some sites and absent at others *and* is predicted by soil, drainage or antecedent wetness better than by density.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-R3 "What this claim rests on")</sup>
4. <span class="claim" data-claim="C-SS-T-R4">**The result is published whichever way it falls**, in full, with the raw series — and the pre-registration says so before the money is spent. **If the soil reactor wins, this project's own emphasis was wrong and the page saying so will carry that sentence.**</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-R4 "What this claim rests on")</sup>
5. <span class="claim" data-claim="C-SS-T-R5">**No composite index is reported without the series it came from**, and no residual is named after a source. That is the failure this whole site documents; reproducing it here would be unforgivable.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-R5 "What this claim rests on")</sup>

---

## 5. What would invalidate the experiment rather than answer it

<span class="claim" data-claim="C-SS-T-INVALID">Written down in advance, so that none of them can be found afterwards as an excuse:</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-INVALID "What this claim rests on")</sup>

- <span class="claim" data-claim="C-SS-T-I-FOUL">**Fouled sensors reading confidently.** Servicing schedule and co-location against a reference instrument, or the continuous tier is decoration. This is [`X16`](EXPERIMENTS.md).</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-I-FOUL "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-DNA">**Decayed DNA.** Host markers detect recent contamination, so a marker absence at a site visited late is not evidence of absence. The sterols, which change slowly, are the check.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-DNA "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-I-ENDS">**Unmeasured end members.** If the slurry in *these* tanks was never sampled, every fraction is a guess with a decimal point on it.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-I-ENDS "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-I-CHASE">**Storm-chasing bias.** Triggers are set in advance and left alone. An operator who decides which storms are interesting has destroyed the sample.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-I-CHASE "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-I-MATCH">**Catchments matched on the wrong thing.** If the high-density catchments are also the sandy ones, the design has confounded exactly what it set out to separate — and the pairing has to be published so somebody else can say so.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-I-MATCH "What this claim rests on")</sup>

---

## 6. What it needs, and how it could be built

<span class="claim" data-claim="C-SS-T-PHASES">[SENSING.md](SENSING.md) lists what to buy: the node, the sampler, the shared kit and the laboratory panel. No price is given there or here: the design says what to buy, and a supplier's quotation says what it costs. The laboratory is a cost per bottle and the sensors a purchase made once, so the bottles are the line that grows with the design, and the one that cannot be economised without losing the attribution the design exists for.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-PHASES "What this claim rests on")</sup>

### The proof of concept, which tests the instrument and not the hypothesis

<span class="claim" data-claim="C-SS-T-POC">**One pair of catchments, one spreading season, and a deliberately narrow question.** The distinction matters: a single pair cannot answer whether the payload reaches Danish water — the sample is one pair and the result would be a number people fight over. What it *can* do is establish that the method works, which is what has to be true before anybody buys [24](SOURCES.md#F-95eb3d8182) of anything.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-POC "What this claim rests on")</sup>

**What it has to prove, and the go/no-go on each:**

- <span class="claim" data-claim="C-SS-T-G1">**A cheap node survives.** Passes if one node returns a continuous record through a Danish February, with gaps that are explainable; fails if the enclosure floods, the panel ices, or the radio drops the winter.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-G1 "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-G2">**Its readings mean something.** Passes if, co-located against a reference sonde, turbidity and conductivity track it within a stated tolerance and the drift is characterisable; fails if drift is larger than the seasonal signal, in which case the continuous tier is a trigger only and must be described as one.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-G2 "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-G3">**The trigger catches events.** Passes if the sampler fires on the rising limb and fills bottles across the storm, unattended, [three](SOURCES.md#F-97b831e706) times; fails if it fires on noise, or misses the events the rain record says happened.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-G3 "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-G4">**The panel discriminates *here*.** Passes if the sterol ratio and host markers separate this catchment's slurry from its sewage effluent and from its soil; fails otherwise — **and this is the one that kills the national design.** If the end members are not separable in one Danish catchment, [twelve](SOURCES.md#F-df03937f6f) pairs will not fix it.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-G4 "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-G5">**The chain closes.** Passes if a reading taken at a culvert appears in a public series with its calibration state attached; fails if anything in the path needs a person to copy a file.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-G5 "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-FOURTH">**Note the fourth test.** It is the only one whose failure means *do not build the national network*. Everything else on this page is downstream of it, which is an argument for doing it first and alone.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-FOURTH "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-STAGED">**A staged path, with a decision at each step:**</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-STAGED "What this claim rests on")</sup>

- <span class="claim" data-claim="C-SS-T-S0">**Stage `0` — one node**: a single stream, no sampler. Does the hardware survive and report?</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-S0 "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-S1">**Stage `1` — proof of concept**: one pair, one season, one sampler. Does the method discriminate, here?</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-S1 "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-S2">**Stage `2` — regional**: pairs in more than one region, both windows. Is the effect visible at all, and how variable?</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-S2 "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-S3">**Stage `3` — the experiment**: [twelve](SOURCES.md#F-df03937f6f) pairs, [two](SOURCES.md#F-6e613878d3) years. Which of the [3](SOURCES.md#F-ff0b4d5203) hypotheses is right?</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-S3 "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-S4">**Stage `4` — the network**: every outlet that reaches the sea. The same answer everywhere, permanently.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-S4 "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-NOWASTE">**No stage is wasted if the next one is never funded.** Stage `0` is a real series from a real stream. Stage `1` is a publishable methods result either way. Stage `2` is a regional finding. That property is the reason to stage it like this rather than to write one large proposal that has to be accepted whole.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-NOWASTE "What this claim rests on")</sup>

### What recurs

<span class="claim" data-claim="C-SS-T-RECUR">**Do not mistake the hardware for the programme.** Hardware is bought once, and saying that it is the cost is how these schemes die:</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-RECUR "What this claim rests on")</sup>

- <span class="claim" data-claim="C-SS-T-RC-SERV">**Servicing.** A sensor that nobody visits produces confident wrong numbers, which is worse than no sensor.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-RC-SERV "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-RC-LAB">**Laboratory.** The tier-two bottles are paid for one analysis at a time, and are the only line that cannot be economised without losing the attribution.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-RC-LAB "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-RC-CUST">**Custody.** Somebody has to keep the archive, the calibration histories and the pre-registration for as long as the series runs, and that is a job rather than a server.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-RC-CUST "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-RC-SO">So: **a purchase to find out, and salaries to keep knowing.** The recurring part is the one a proposal has to be honest about, because it is the one that gets cut and takes the series with it.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-RC-SO "What this claim rests on")</sup>

### And the whole of it?

<span class="claim" data-claim="C-SS-T-FIELD">This page designs the answer to one question. The obvious next one is what it would take to settle the *field* — not the faecal channel alone, but enough of the [23](SOURCES.md#F-1a851cdb55) designs in [EXPERIMENTS.md](EXPERIMENTS.md) to put measurements where the argument now has models. The blocks, without prices:</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-FIELD "What this claim rests on")</sup>

- <span class="claim" data-claim="C-SS-T-B-THIS">**This experiment**: whether the payload reaches the water, and whose it is.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-B-THIS "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-B-NET">**The standing stream network** in [SENSING.md](SENSING.md): the same question everywhere, permanently, with no extrapolation.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-B-NET "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-B-CSO">**Instrumenting the [13](SOURCES.md#F-8b39dac318) largest overflow structures**: flow rather than event counts, at the structures that hold [24](SOURCES.md#F-21d33a092b)% of the volume reported by the [1,328](SOURCES.md#F-56459bfcad) that report one.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-B-CSO "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-B-MARINE">**The marine tier** — `X14`, `X15`, `X16`: oxygen and temperature at many points in one water body, to test whether one station can stand for it.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-B-MARINE "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-B-MISSING">**The missing instruments** — `X19`, `X20`: a panel for the outcomes no source this project profiled measures, and a record of dated events from the people with the longest baseline, for damage that has no instrument behind it.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-B-MISSING "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-B-DESK">**The desk work** — `X8`, `X21`, `X22`: analyses of data that already exists.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-B-DESK "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-B-TRIALS">**A trials portfolio** — the meta-solution in [PROGRAMME.md](PROGRAMME.md): whether the interventions work, in named places, reversibly.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-B-TRIALS "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-CAPITAL">Each block is hardware bought once and a bill for service, sampling and custody that recurs, and the recurring part is the one that decides whether any of it survives to be a time series.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-CAPITAL "What this claim rests on")</sup>

**And what money cannot do.**

- <span class="claim" data-claim="C-SS-T-L-SHIP">**Ship time is not in it.** The autumn benthic extension and anything offshore needs a vessel and an institution, and this page provides neither.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-L-SHIP "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-UNSCOREABLE">**Some of it cannot be bought at all.** [42](SOURCES.md#F-198b20fb90) of the [166](SOURCES.md#F-4196d405de) mechanisms in the register cannot be tested with any source this project surveyed, because the deciding measurement is in none of them; money buys the instrument, not the record it should have been collecting.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-UNSCOREABLE "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-DESK">**And one block needs no fieldwork.** [3](SOURCES.md#F-3121ff95a9) designs are desk analyses of data that already exists. If the argument is that this is all too expensive, that block is the counter-example sitting in the open.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-DESK "What this claim rests on")</sup>

---

## 7. Who could do which part

- <span class="claim" data-claim="C-SS-T-W-ONE">**One person with a culvert and a soldering iron**: a node, a year of a real series from one stream, and the demonstration that it works.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-W-ONE "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-W-ASSOC">**A local association or a school**: a pair — one high-density catchment and its match — which is a whole experiment in miniature.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-W-ASSOC "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-W-MUNI">**A municipality or a water utility**: the samplers and the laboratory line, which is the half that needs an institution.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-W-MUNI "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-W-UNI">**A university group**: the end-member sampling and the isotope work, and the pre-registration that makes the rest admissible.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-W-UNI "What this claim rests on")</sup>
- <span class="claim" data-claim="C-SS-T-W-ANY">**Anyone at all**: hold the pre-registration to its publication rule when the result is inconvenient.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-W-ANY "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-PERMISSION">The stream measurements need a landowner's permission at each culvert, and the end-member samples need the farms and plants that hold them to agree.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-PERMISSION "What this claim rests on")</sup>

---

## 8. What it settles, and what it does not

<span class="claim" data-claim="C-SS-T-SETTLES">**Settles.** Whether the payload reaches the water, in what quantity, in what season, under what conditions, and whose it is — measured rather than modelled, at the point where inland water becomes coastal water. Whether the spreading calendar is visible in a stream. Whether the account's single channel is missing a second one, and by roughly how much.</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-SETTLES "What this claim rests on")</sup>

<span class="claim" data-claim="C-SS-T-NOTSETTLE">**Does not settle.** What the arriving material then does in the sea: that is the next experiment and it is harder. Nor anything about constituents outside the analysed list. Nor the marine oxygen question, which has [its own designs](EXPERIMENTS.md).</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-NOTSETTLE "What this claim rests on")</sup>

> <span class="claim" data-claim="C-SS-T-WHYEND">**Why it would end the argument rather than extend it.** The disputed agricultural share is a modelled residual. This produces a measured quantity, at named places, on dates, with the raw series published and the decision rule fixed in advance — so the result is available to somebody who does not trust either party. **That is the kind of number that can end a disagreement.**</span><sup class="claim-mark">[†](CLAIMS.md#C-SS-T-WHYEND "What this claim rests on")</sup>
