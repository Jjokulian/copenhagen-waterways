# What is known, by whom

<span class="claim" data-claim="C-KP-HEADLINE">This project used to be headed *"What Denmark knows about its own coastal water."* That was a claim we were not entitled to make, and this page is why.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-HEADLINE "What this claim rests on")</sup>

<span class="claim" data-claim="C-KP-FETCHED">We can characterise **what is in the data we fetched**. That is a different object from what Denmark knows, and the difference is a whole quadrant wide.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-FETCHED "What this claim rests on")</sup>

---

## The four quadrants, and which one is dangerous

<span class="claim" data-claim="C-KP-QUADRANTS">The quadrants sort what this project holds and misses by two questions: whether a thing exists, and whether we know we have it.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-QUADRANTS "What this claim rests on")</sup>

| | we know we have it | we don't know we have it |
|---|---|---|
| **it exists** | **known known** — the [53.7](SOURCES.md#F-4c570f3335)M CTD measurements, and everything computed from them | **UNKNOWN KNOWN** — data that exists, is held by someone, and is absent from our map |
| **we know it's missing** | **known unknown** — the [89](SOURCES.md#F-000ac8d87b) gated sources in [If you have data access we don't](IF_YOU_HAVE_THE_DATA.md), [10](SOURCES.md#F-fe0618057d) of them with a slot the analysis is already written against | **unknown unknown** — measurements nobody makes and nobody has thought to want |

<span class="claim" data-claim="C-KP-UNKNOWN-KNOWN">**The unknown known is the dangerous one**, because it is indistinguishable from absence when you are inside the archive.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-UNKNOWN-KNOWN "What this claim rests on")</sup> Some of those we found:

- <span class="claim" data-claim="C-KP-CTD-PARAMS">`ctd.csv.gz` carries **[17](SOURCES.md#F-779d628231) distinct `Parameter` values**, including **Turbiditet** and **FDOM**; the station series this project analyses carry [9](SOURCES.md#F-cb09ee93d7) variables, drawn from five of them.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-CTD-PARAMS "What this claim rests on")</sup>
- <span class="claim" data-claim="C-KP-VEGETATION">The ODA topic tree holds **eelgrass**, **macroalgae** and **bottom fauna** topics, and none is in the fetch script.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-VEGETATION "What this claim rests on")</sup>
- <span class="claim" data-claim="C-KP-FISHING">Fishing effort is published openly: [Global Fishing Watch's apparent fishing effort](https://zenodo.org/records/14982712), version three, covering 2012–2024, as a direct download with no login.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-FISHING "What this claim rests on")</sup>

<span class="claim" data-claim="C-KP-NOTHIDDEN">None of those was hidden; they were simply not looked for. **So any sentence in this project of the form "Denmark does not measure X" should be read as "X is not in what we fetched"** — and the two are not the same claim.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-NOTHIDDEN "What this claim rests on")</sup>

---

## What the discovery rate tells you

<span class="claim" data-claim="C-KP-ESTIMATOR">**A known unknown can be priced. An unknown known cannot** — by construction, since you would have to know it to count it. So there is only one estimator of its size: **the rate at which you keep finding them.**</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-ESTIMATOR "What this claim rests on")</sup>

<span class="claim" data-claim="C-KP-RATE">The first list of such finds, published on 9 September, held six. The second, published the next afternoon, held ten more, and nothing about that rate suggests we are near the end of them.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-RATE "What this claim rests on")</sup>

### The second list

| | what it was | where it had been the whole time |
|---|---|---|
| **A clock on every row** | <span class="claim" data-claim="C-KP-T-NOCLOCK">this project said *no row in the archive carries a clock time* and built a class of *unscoreable* on it</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-NOCLOCK "What this claim rests on")</sup> | <span class="claim" data-claim="C-KP-T-CLOCK">`Startklok`, on **all but [22](SOURCES.md#F-c20885b069) of [1,805,827](SOURCES.md#F-9fa9c3c21c)** water-chemistry rows. The claim was true of the CTD extract and inferred from a topic nobody had fetched</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-CLOCK "What this claim rests on")</sup> |
| **The topic itself** | <span class="claim" data-claim="C-KP-T-TOPIC-BLOCK">[9](SOURCES.md#F-b5ea195365) hypotheses were blocked on it</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-TOPIC-BLOCK "What this claim rests on")</sup> | <span class="claim" data-claim="C-KP-T-TOPIC">named in `fetch_oda.py`'s own docstring and missing from its `TOPICS` dict; it has since been fetched</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-TOPIC "What this claim rests on")</sup> |
| **Two units in one column** | averages taken across them | <span class="claim" data-claim="C-KP-T-UNITS">**[14](SOURCES.md#F-cb89b765bd) of [146](SOURCES.md#F-da414cb2c0) parameters**. `Orthophosphat` is in mg/l on [38](SOURCES.md#F-0f04693c5a)% of its rows and in µg/l on the rest, a thousandfold apart; integrated primary production is spread over several units</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-UNITS "What this claim rests on")</sup> |
| **The flood sheets are photographs** | <span class="claim" data-claim="C-KP-T-REG">registered by correlating against water polygons, at [14](SOURCES.md#F-857821cb67)–[91](SOURCES.md#F-3e1120ac9a) m</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-REG "What this claim rests on")</sup> | <span class="claim" data-claim="C-KP-T-PHOTOS">they carry an **orthophoto basemap** — buildings, streets, Rådhuspladsen's fountain — so the strongest cue for placing them was not the one used</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-PHOTOS "What this claim rests on")</sup> |
| **Grid north is not north** | <span class="claim" data-claim="C-KP-T-NORTHUP">*"every sheet has north up (the north arrow confirms it)"*, as the placement code still says</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-NORTHUP "What this claim rests on")</sup> | <span class="claim" data-claim="C-KP-T-NORTH">meridian convergence of **[2.90](SOURCES.md#F-501f30a23e)–[2.98](SOURCES.md#F-fc0fde2bc8)°**, displacing corners **[94](SOURCES.md#F-ab2d7eefd2)–[350](SOURCES.md#F-348096b730) m** — [2.4](SOURCES.md#F-44a0407afe) to [7.5](SOURCES.md#F-bd0568af5a) times the registration error the pipeline reports for itself</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-NORTH "What this claim rests on")</sup> |
| **Censoring with no name** | read as measurements | <span class="claim" data-claim="C-KP-T-CENSOR">`ResultatAttribut` = `<` on **[85,035](SOURCES.md#F-208361ba97) rows**, where the value is the *detection limit*; `SigtTilBund` on [26,380](SOURCES.md#F-d626dd3578) Secchi readings that reached the bottom</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-CENSOR "What this claim rests on")</sup> |
| **Values no instrument gave** | averaged | <span class="claim" data-claim="C-KP-T-SENTINEL">depth exactly `99` on [4,332](SOURCES.md#F-3b39e7a914) rows; a station named `Hirtshals 15 m` with bottom depths up to [292.3](SOURCES.md#F-708e892f0c) m (median [17.5](SOURCES.md#F-fd4b1ba41e) m); oxygen saturation recorded up to [90,972](SOURCES.md#F-b78fe39caf)%</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-SENTINEL "What this claim rests on")</sup> |
| **The regulatory unit is void** | a headline figure framed on DE/ha | <span class="claim" data-claim="C-KP-T-DE">`dyreenhed` occurs **[0](SOURCES.md#F-dc51124c36) times** in BEK 931/2024. The binding ceiling is [170](SOURCES.md#F-bb5f71323f) kg N per hectare of harmoniareal</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-DE "What this claim rests on")</sup> |
| **A national drainage map** | *"drained areas are not mapped"* | <span class="claim" data-claim="C-KP-T-DRAIN">mapped for Miljøstyrelsen at a [30.4](SOURCES.md#F-d0b274b132) m resolution: [52](SOURCES.md#F-f6d841dc22)% of agricultural land drained, with a stated accuracy of [79](SOURCES.md#F-d0b274b132)%, in a report we had not read</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-DRAIN "What this claim rests on")</sup> |
| **One column, three meanings** | one guard written for all of them | <span class="claim" data-claim="C-KP-T-KFAKTOR">`KorrektionsFaktor` is a Winkler-to-electrode ratio for oxygen, a calibration against chlorophyll for fluorescence, and, for CTD temperature and salinity, a factor the instruction does not describe</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-T-KFAKTOR "What this claim rests on")</sup> |

<span class="claim" data-claim="C-KP-TEN">**Ten, and worse than the first six**, because most are not things Denmark failed to publish. They are properties of files we already held and had already analysed. The first list was about the edge of the archive; the second was about its middle.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-TEN "What this claim rests on")</sup>

<span class="claim" data-claim="C-KP-DID-NOT-FALL">**The rate did not fall. That is the whole measurement.** Two samples is not a trend, but nothing here supports the belief that a second pass exhausts a first pass's blind spots, and the second pass was not even looking — it was fetching one topic and counting distinct values in columns.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-DID-NOT-FALL "What this claim rests on")</sup>

### A sixth kind: the unknown known in your own output

<span class="claim" data-claim="C-KP-OWN-OUTPUT">One kind of unknown known does not fit the quadrants, because it is not about Denmark's data at all: a derived number of our own that has gone stale.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-OWN-OUTPUT "What this claim rests on")</sup> <span class="claim" data-claim="C-KP-FLOOD-STALE">After one flood sheet was re-registered, the figures computed from it stayed on the superseded placement until the scripts that read it were rerun: the modelled flood area this site published moved from [5.932](SOURCES.md#F-8ec238aa8e) to [5.847](SOURCES.md#F-0156368344) km² when they were.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-FLOOD-STALE "What this claim rests on")</sup>

<span class="claim" data-claim="C-KP-GUARD">What kept it stale is the part worth generalising. The tool that checks generated documents reported that regenerating would remove *substantial lines* — which reads as **your prose is about to be destroyed** — when the lines were ones whose numbers had changed and which the regeneration replaced. *This output is stale* and *you are about to lose something* came out in the same words, and the cautious response to the second is the wrong response to the first. The tool now tells a replaced line from a lost one.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-GUARD "What this claim rests on")</sup>

<span class="claim" data-claim="C-KP-OWN-ARTEFACTS">**So the quadrants need a row for your own artefacts.** A derived number is held data too, it goes stale silently, and nothing in the archive tells you. The fix that generalises is not vigilance: it is making the tools tell the two cases apart.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-OWN-ARTEFACTS "What this claim rests on")</sup>

### What was built in response

<span class="claim" data-claim="C-KP-BUILT">[CLAIMS.md](CLAIMS.md) is the structural half of the answer to this page. Every checked claim is registered with the graph of what it stands on, down to data, a pinned document, a stated assumption, a gap, code, this project's history or an explicit end of the trail; the graph is checked for cycles; and a claim goes stale when anything under it changes. What could not be justified is kept, in its own words, in [ARCHIVE.md](ARCHIVE.md). That does not find unknown knowns. It does stop a claim from quietly outliving the thing it rested on.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-BUILT "What this claim rests on")</sup>

### The residual-growth test, turned on ourselves

<span class="claim" data-claim="C-KP-RESIDUAL-GROWTH">This project's method 6 says: move a part `P` out of a leftover, and the arithmetic must give `R_new = R_old − P`. If it doesn't shrink, the leftover was absorbing model error and was never a partition. Apply it to *"what Denmark does not measure."* Each discovery moved a part out. Did the leftover shrink by that part? **No — it grew.** Finding a thing you should have known raises your estimate of what else you have missed; it does not lower it. A leftover that behaves that way was never a partition of the world. It was absorbing our own ignorance, and reporting it as a property of Denmark.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-RESIDUAL-GROWTH "What this claim rests on")</sup>

### Absence of evidence, priced

<span class="claim" data-claim="C-KP-SENSITIVITY">*"We looked and found nothing"* supports *"there is nothing"* exactly as far as **P(not found | it exists)** is small. That probability is the sensitivity of the search, and nobody states it — including us, until now. Ours was poor: the first list alone held six things the search had missed. So the inference was never licensed, whatever the topic.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-SENSITIVITY "What this claim rests on")</sup>

> <span class="claim" data-claim="C-KP-CALIBRATE">**Calibrate the search with known positives.** Seed it with things you already know exist and count how many come back. That detection rate is the null for every absence claim built on it. Without it, "not measured" means "not found by an uncharacterised procedure", which supports nothing.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-CALIBRATE "What this claim rests on")</sup>

### The two failure modes are symmetric

| | reading | cases |
|---|---|---|
| **absence → absence** | "we didn't find it" ⇒ "it isn't there" | <span class="claim" data-claim="C-KP-FM-ABSENCE">the lists above, of which *"no row carries a clock time"* is the purest: a property of one unfetched topic, reported as a property of the archive</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-FM-ABSENCE "What this claim rests on")</sup> |
| **presence → evidence** | "there is a column" ⇒ "there is a measurement" | <span class="claim" data-claim="C-KP-FM-PRESENCE">the national hazardous-substance layer's [256](SOURCES.md#F-aee5a58e2f) points are all freshwater — [152](SOURCES.md#F-4e20821308) in lakes, [104](SOURCES.md#F-53860b0f29) in rivers, none coastal — so a marine column built from it would carry only freshwater points</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-FM-PRESENCE "What this claim rests on")</sup> |

<span class="claim" data-claim="C-KP-FM-WORSE">The second is worse, because it *adds* confidence. But they share a root: **treating the shape of a search result as a property of the world.**</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-FM-WORSE "What this claim rests on")</sup>

---

## The same map, from three vantage points

<span class="claim" data-claim="C-KP-VANTAGE">The quadrants are not a property of the data. They are a property of who is standing where.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-VANTAGE "What this claim rests on")</sup>

### The Danish authority (DCE, Miljøstyrelsen)

<span class="claim" data-claim="C-KP-AUTHORITY">Most of our unknown knowns are their known knowns. But they have their own, and the project has found some:</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-AUTHORITY "What this claim rests on")</sup>

- <span class="claim" data-claim="C-KP-SONDE">**`SondeNr` arrives as `999` on [25.6](SOURCES.md#F-18d47162ce)% of CTD rows.** The probe number exists at the point of measurement — somebody held that instrument. It is lost between the ship and the archive, not absent from the world.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-SONDE "What this claim rests on")</sup>
- <span class="claim" data-claim="C-KP-CTD-NOCLOCK">**Time of day is absent from the CTD extract** — its [53.7](SOURCES.md#F-4c570f3335)M rows carry a date and no hour — though the field-sampling instruction has the station log record the clock time.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-CTD-NOCLOCK "What this claim rests on")</sup>

### Us

<span class="claim" data-claim="C-KP-US">Our known knowns are narrow and well characterised. Our known unknowns are enumerated, in [If you have data access we don't](IF_YOU_HAVE_THE_DATA.md). **Our unknown knowns are unbounded and we cannot estimate them** — the lists above were found largely by accident, and there is no reason to think the rate has stopped.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-US "What this claim rests on")</sup>

<span class="claim" data-claim="C-KP-NO-OBLIGATION">The one thing we have that the authority structurally lacks: **no obligation to produce a number.** An unscoreable hypothesis can be left unscoreable here.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-NO-OBLIGATION "What this claim rests on")</sup>

### Other connectors

<span class="claim" data-claim="C-KP-CONNECTORS">Utilities may hold measured overflow where the national account holds reported annual volumes. ICES, HELCOM, EMODnet and Copernicus hold effort, wave and optical layers, some of which this project has since fetched. Farmers hold actual application records where the balance holds norm coefficients. Universities hold cores, incubations and porewater profiles for mechanisms this project has had to mark as needing an experiment. For each, the relationship is asymmetric in the useful direction: **their known known is our unknown known**, and one email may close it.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-CONNECTORS "What this claim rests on")</sup>

---

## What follows for the headline

<span class="claim" data-claim="C-KP-HEADLINE-NOW">"What Denmark knows about its own coastal water" is an estimate **we** made, of the known-known quadrant only, from one vantage point, using data we fetched ourselves. It is a finding of this project, and a contestable one — not its title.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-HEADLINE-NOW "What this claim rests on")</sup>

<span class="claim" data-claim="C-KP-AUDIT">The site now leads with what it is: an audit of a record, by someone outside the institutions that produced it, with the method stated so the conclusions can be checked. The knowledge claim sits below, labelled as ours.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-AUDIT "What this claim rests on")</sup>

<span class="claim" data-claim="C-KP-CONSTRUCTION">That is the same discipline applied everywhere else here. A count is a construction before it is a fact; so is a headline.</span><sup class="claim-mark">[†](CLAIMS.md#C-KP-CONSTRUCTION "What this claim rests on")</sup>

---

*Generated by `scripts/pages/known_and_unknown.py`. Every assertion on this page opens what it rests on; what the page used to say and no longer can is in [ARCHIVE.md](ARCHIVE.md).*
