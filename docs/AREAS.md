# There is no Denmark

Every number in the national argument is an aggregate: one land-borne load, one 69.6%, one ladder of indsatsbehov, one 25% rule. Aggregation is where the information goes. Køge Bugt and Ringkøbing Fjord do not share a cause, a flushing time, a sediment, or a fix, and a figure true of Denmark is true of nowhere in it.

This page refuses the aggregate. One record per marine water body: what presses on it, what is observed in it, **over which years each of those streams exists**, and what cannot be modelled there. The last of those is the longest column, and that is the finding.

Assignment is by nearest point on the marine boundary, one rule for every layer, with the distance recorded on every assignment and anything beyond 20 km dropped.

## The state of knowledge, counted

| | areas | km² | share of sea |
|---|---:|---:|---:|
| All marine water bodies | 123 | 43,579 | 100.0% |
| …with a fitted load→indicator model | 28 | 2,492 | 5.7% |
| …with any repeated marine observation (bathing) | 70 | 17,900 | 41.1% |
| …where internal coherence can even be tested | 43 | 15,818 | 36.3% |
| …with neither a model nor an observation | 44 | 24,605 | 56.5% |

44 water bodies covering 24,605 km² (56% of Danish sea) carry neither a fitted model nor a repeated observation **in the two layers counted above** — bathing water and hazardous-substance status. They still receive a requirement.

> **A correction, and a caution about the whole class of statement.** An earlier version of this line said those water bodies carry "neither a fitted model nor a single repeated marine observation", which reads as a claim about marine observation in general. It is not one, and checked against a wider corpus it is false. **A claim of absence is only as wide as the search behind it**, and this search was two layers deep.
>
> The check: ODA's station register holds **6,258 positioned marine stations**, and assigned by point-in-polygon to the same boundaries used on this page, **every one of the 123 water bodies contains at least one.** Counted over that register: 3 water bodies contain no station visited in two or more distinct years, 8 contain none visited in five or more, and 22 contain none visited in ten or more.
>
> **Those are counts, and they are deliberately not percentages.** Saying *18% of the sea has no long observation* would be the missing-denominator error this project exists to point at, committed here. The denominator is known — the sea is 43,579 km². The numerator is not, because it is the extent of an absence, and an absence can only be measured against a search that was exhaustive. Ours was ODA plus two layers. ICES, EMODnet, university programmes, municipal monitoring and every unpublished series sit outside it.
>
> The line between the two kinds of figure is worth stating, because this page uses one of them freely and must not use the other:
>
> The test is whether **the category named is the same width as the corpus searched.**
>
> - **Same width — a percentage is fine, including of an absence.** *57 of 123 water bodies have no point in the national hazardous-substance monitoring programme, covering 70% of the sea.* The category is that programme, the register of it is complete, so its complement is exact. Same for *28 of 123 have a fitted model — 5.7% of sea area*: the models are published and the sea is measured, and nothing rests on having found anything else.
> - **Category wider than corpus — only a count is honest.** *56% of the sea has no marine observation* names a category — marine observation — far wider than the two layers actually searched. The leftover after subtracting what we happened to find is then reported as though it were measured, which is the operation [RESIDUAL.md](RESIDUAL.md) is about, and it does not become acceptable because we are the ones doing it.
>
> So absence is reported here as a count over a named corpus, and the corpus is named every time.
>
> **And the corpus is named together with what is missing from it.** A coverage figure has a numerator nobody can measure — the evidence that exists — so counting what we assembled gives a *lower bound on evidence* and therefore an *upper bound on absence*. That is only interpretable beside the terms we know belong in the numerator and cannot add. They are kept in `data/manual/coverage_gaps.json` and there are three kinds:


| | source | what it would add | why we do not have it |
|---|---|---|---|
| `closed` | **PULS** | The time axis for B1 and B2. Their discriminating test is oxygen and shore condition in the days after an overflow against that event's volume, which an annual total cannot do. | CVR-gated. Not merely a login: an access attempt with a private MitID was refused on the grounds that no CVR or VAT number attached to it was valid. Access appears to require a registered business or authority entity, so a private citizen cannot obtain it at all. |
| `closed` | **LER** | The drainage network itself, which open problem 16 says exists for exactly one Danish city and only by lucky archaeology. | Not open data. This project does not query it and no argument here depends on it. |
| `open_unassembled` | **MUNICIPAL-SPILDEVANDSPLANER** | Real catchment boundaries, which are the hard test for the inference method in X21. | None. Nobody has assembled them. Some are already in data/raw/plan_html/. |
| `open_unassembled` | **ICES-EMODNET** | Marine observation outside ODA entirely, including the cross-border series that a national extract cannot contain. | Free registration, not completed. |
| `absent` | **FISH-KILL-REGISTER** | The observable behind fiskedoed, one of the four words the public uses for the damage. | Checked and not found in open form. The surveillance is described publicly; no database is linked. |
| `closed` | **MECHANISTIC-MODEL-RUNS** | The ability to check the validation claims in GRUNDLAGET.md directly rather than through their authors' description of them. | Not published as data. The method reports are public; the runs are not. |

The distinction inside that table matters as much as the table. `closed` is a gap in the world's availability; `open_unassembled` is a gap in our effort and is nobody's fault but ours; `absent` is the only one where a search was actually run to exhaustion, and even that is bounded by the search. **PULS is the sharpest case.** It holds the per-event overflow volumes that `B1` calls the single most valuable missing series, and an access attempt with a private MitID was refused because no CVR or VAT number attached to it was valid — so this is not a login anyone has neglected to perform. It appears to require a registered business or authority, which means a private citizen cannot obtain it at all.

## Two meanings of "a body of water", and the switch between them

"Roskilde Fjord" is not an arbitrary line on a map, and it is worth saying so plainly before objecting to anything. It names a real hydrographic object: water largely bounded by land, with exchange restricted to a narrow mouth. That is a **claim about enclosure**, it is physical, and it is true.

The assessment then uses the same word to mean something else entirely: that a measurement taken anywhere in it stands for the whole of it. That is a **claim about homogeneity**, and it is statistical. One sense is about where the water is bounded; the other is about whether the water inside those bounds is alike. Nothing carries you from the first to the second, and the name does the carrying unnoticed because the same three words serve both.

**And the physics runs against the transfer, not with it.** Restricted exchange is exactly what *preserves* a gradient. A basin with freshwater entering at its head and a sill at its mouth holds a salinity, residence-time and oxygen gradient along its length precisely because it does not flush; open water erases such differences by mixing. So the better the enclosure, the weaker the homogeneity assumption becomes. The two senses are not merely distinct — **they pull in opposite directions**, and the enclosures that most deserve their names are the ones least entitled to be treated as single units.

The partition half-concedes this without following it through. Roskilde Fjord appears here as two water bodies, `DKCOAST1` (ydre, 71 km²) and `DKCOAST2` (indre, 52 km²) — an admission that one enclosure is at least two units. Nothing states why two is the right number, what test would have produced three, or what measurement would settle it. A boundary drawn somewhere inside a fjord is a hypothesis about where the water changes, and it is the kind of hypothesis this project can actually test: `X22` in [EXPERIMENTS.md](EXPERIMENTS.md) sets out how, using pairs of measurements at matched separation either side of a line.

> The practical rule that follows, and the reason the station-level series exist: **the unit of observation is a position.** Everything else — this page included — is an aggregate computed inside somebody's polygon, and should be read as a statement about that polygon as much as about the sea.

### The switch, measured in the fjord it is named after

The station-level series make this checkable rather than arguable. Both halves of Roskilde Fjord carry several stations, so for any month where three or more measured, the disagreement *between* stations can be set against the variation *across* months — which is the signal anyone is trying to detect.

| variable | basket | months with 3+ stations | spread between stations, same month | spread across months | ratio |
|---|---|---:|---:|---:|---:|
| bottom oxygen | indre `DKCOAST2` | 221 | sd 1.82, median range **3.35 mg/l** | 2.80 | **0.65** |
| bottom oxygen | ydre `DKCOAST1` | 113 | sd 0.81, range 0.80 | 3.20 | 0.25 |
| surface salinity | indre `DKCOAST2` | 222 | sd 0.49, range 1.06 | 1.71 | 0.29 |
| surface salinity | ydre `DKCOAST1` | 114 | sd 1.07, range 2.08 | 1.22 | **0.88** |
| bottom temperature | indre `DKCOAST2` | 224 | sd 1.64 | 5.36 | 0.31 |
| bottom temperature | ydre `DKCOAST1` | 113 | sd 0.44 | 6.64 | 0.07 |

**The inner fjord's own stations disagree about bottom oxygen by a median of 3.35 mg/l within a single month.** The iltsvind criterion is oxygen below 4 mg/l in bottom water. So the disagreement between stations inside one water body is very nearly the whole width of the threshold, and whether that body "has iltsvind" can depend on which of its own stations is read. The ratio says the same thing in another way: the spread between stations is **65% of the size of the entire seasonal signal** the monitoring exists to measure.

**And the two halves fail on different variables.** The inner fjord is unreliable for oxygen (0.65) and well behaved for salinity (0.29); the outer fjord is the reverse — fine for oxygen (0.25), poor for salinity (0.88). That is not a ranking of two baskets. It is a demonstration that **no single partition can serve both variables**, because the water is organised differently depending on what you measure. A boundary that is real for salinity is arbitrary for oxygen, and drawing one set of lines and using it for everything is the error, rather than drawing them in the wrong place.

Computed from `docs/data/areas/stations_series.*`, which carry no partition at all — the water-body assignment used here is loaded separately from `station_waterbody_overlay.json`, on purpose, so that using it is a deliberate act.

## What are the baskets predictive FOR? — and how easily that question is answered wrongly

A partition is not right or wrong in general; it is predictive *for a variable*. So the question is what the water bodies encode, and the statistic is the **intraclass correlation** computed within month: pick two stations at random in the same month — if they are in the same water body, how much more alike are they than two picked without regard to it? One means membership tells you everything; zero means it tells you nothing beyond the season.

Within month is essential. Every station in Denmark shares a season, so pooling across months puts the seasonal signal into the between-basket term and makes every partition look excellent, including an absurd one.

**The result depends almost entirely on what it is compared against, and three reasonable comparisons give three different answers.** This section reports that rather than a ranking, because an earlier version of this page reported the ranking and it was wrong.

| variable | real | shuffled | latitude stripes | size- and shape-matched | **lift over the last** |
|---|---:|---:|---:|---:|---:|
| surface oxygen saturation | 0.924 | 0.859 | 0.516 | 0.522 | **+0.402** |
| surface oxygen | 0.878 | 0.782 | 0.550 | 0.595 | **+0.283** |
| bottom oxygen saturation | 0.810 | 0.658 | 0.585 | 0.672 | +0.138 |
| surface salinity | 0.968 | 0.531 | 0.679 | 0.844 | +0.124 |
| bottom salinity | 0.916 | 0.538 | 0.640 | 0.798 | +0.118 |
| surface temperature | 0.830 | 0.510 | 0.618 | 0.734 | +0.096 |
| bottom oxygen | 0.790 | 0.639 | 0.602 | 0.698 | +0.092 |
| bottom temperature | 0.810 | 0.523 | 0.625 | 0.766 | +0.044 |
| fluorescence | 0.725 | 0.404 | 0.564 | 0.775 | **−0.050** |

The three nulls answer three different questions. **Shuffled** permutes station labels while keeping basket sizes, so it destroys geography and keeps the size structure; against it, salinity wins by a distance. **Latitude stripes** are equal-count horizontal bands, so they keep compactness and equal sizes but ignore hydrography; against them, surface oxygen saturation wins. **Size- and shape-matched** baskets have the same size distribution as the real ones and are grown from random seeds by nearest neighbour, so they are compact blobs of the right sizes following no hydrography at all — the only control that varies one thing at a time.

Against that last one the ordering **reverses**: oxygen gains most, salinity gains little, and fluorescence goes negative — random compact blobs of the same sizes predict it *better* than the official partition does.

There is a coherent reading. Salinity is spatially smooth, so any compact grouping predicts it well (0.844 from random blobs) and the real boundaries have little left to add. Oxygen is spatially rough, so blobs do poorly and boundaries that follow enclosure carry real information. A partition's value is not how well it predicts, but **how much better it predicts than the shape of it alone would**.

> **A correction, and the reason this section is written as a caution.** An earlier version said the water bodies "encode salinity strongly and oxygen almost not at all", from the shuffled control alone. Against a null matching both size and shape that is backwards. The claim was defensible, reproducible, and wrong — and it survived exactly as long as it took to compute a second control. Any single number here would have been publishable; the disagreement between the nulls is the finding.

> One further limit bounding every row: stations are not placed at random and are far denser in some baskets than others, so this scores the partition *as sampled*. It cannot distinguish a well-drawn basket from one whose stations happen to sit close together.

## The cum hoc estimate, across areas instead of across years

A national time series has one unit of replication. The areas have 65. So the only place an effect size can actually be estimated is across them.

This tests a sewage-driven outcome against sewage pressure — bathing quality against outfall and treatment-plant density — because that is the one predictor/outcome pair where both sides exist per area. It is **cum hoc**: a correlation across places at one time, with no control for coast type, flushing, or population. It is reported because it is computable and the national figure is not.

| predictor | outcome | r | R² | areas |
|---|---|---:|---:|---:|
| log10(1+outfalls_per_km2) | sub_excellent | +0.149 | 0.022 | 65 |
| log10(1+outfalls_per_km2) | mean_score | -0.136 | 0.019 | 65 |
| log10(1+pe_per_km2) | sub_excellent | +0.313 | 0.098 | 65 |
| log10(1+pe_per_km2) | mean_score | -0.288 | 0.083 | 65 |
| log10(1+basin_m3_per_km2) | sub_excellent | +0.139 | 0.019 | 65 |
| log10(1+basin_m3_per_km2) | mean_score | -0.151 | 0.023 | 65 |

## Every area, on its own terms

`model` — a fitted load→indicator relation exists (DCE 2015, fitted on 1990–2012). `bath` — bathing stations, and the years they span. `r` — how much those stations agree with each other, where there are enough to ask. `RBU` — rain-conditioned outfalls. `PE` — approved treatment-plant load.

| km² | area | model | bath (years) | r | RBU | PE | gaps |
|---:|---|:-:|---|---:|---:|---:|---:|
| 4,248.6 | Skagerrak, 12 sm | · | — | — | 0 | 0 | 4 |
| 3,831.4 | Bornholm, 12 sm | · | — | — | 0 | 0 | 4 |
| 3,703.1 | Vesterhavet, 12 sm | · | — | — | 0 | 0 | 4 |
| 2,495.8 | Nordlige Kattegat, 12 sm | · | — | — | 0 | 0 | 4 |
| 1,880.8 | Østersøen, 12 sm | · | — | — | 0 | 0 | 4 |
| 1,835.6 | Århus Bugt syd, Samsø og Nordlige Bælthav | · | 30 (1991–2018) | +0.12 | 130 | 72,413 | 2 |
| 1,766.8 | Kattegat, SV 12 sm | · | — | — | 0 | 0 | 4 |
| 1,526.1 | Anholt, 12 sm | · | — | — | 0 | 0 | 4 |
| 1,315.8 | Kattegat, SØ 12 sm | · | — | — | 0 | 0 | 4 |
| 1,217.9 | Smålandsfarvandet, åbne del | · | 27 (1991–2018) | +0.22 | 64 | 43,945 | 2 |
| 1,148.6 | Lillebælt, syd | · | 26 (1991–2018) | +0.19 | 118 | 115,906 | 2 |
| 1,052.5 | Kattegat, Aalborg Bugt | · | 14 (1991–2018) | +0.36 | 117 | 88,955 | 2 |
| 990.7 | Skagerrak | · | 33 (1991–2018) | +0.16 | 419 | 481,197 | 2 |
| 821.0 | Sejerø Bugt | · | 27 (1991–2018) | +0.24 | 104 | 71,550 | 2 |
| 721.2 | Kattegat, Nordsjælland | · | 34 (1991–2018) | +0.27 | 295 | 205,544 | 2 |
| 686.8 | Storebælt, nord 12 sm | · | — | — | 0 | 0 | 4 |
| 655.2 | Vesterhavet, syd | · | 12 (1991–2018) | — | 3 | 0 | 3 |
| 609.4 | Kattegat, Læsø | · | 6 (1991–2018) | +0.23 | 6 | 3,860 | 2 |
| 572.6 | Storebælt, syd 12 sm | · | — | — | 0 | 0 | 4 |
| 562.4 | Køge Bugt | · | 29 (1991–2018) | +0.21 | 865 | 681,555 | 2 |
| 554.6 | Kattegat, Nordsjælland >20 m | · | — | — | 0 | 0 | 4 |
| 551.0 | Fakse Bugt | · | 13 (1991–2018) | +0.18 | 78 | 152,578 | 2 |
| 497.0 | Femerbælt, 12 sm | · | — | — | 0 | 0 | 3 |
| 482.2 | Lillebælt, syd 12 sm | · | — | — | 0 | 0 | 3 |
| 459.5 | Hevring Bugt | · | 17 (1991–2018) | +0.40 | 76 | 165 | 2 |
| 458.4 | Nordlige Kattegat, Ålbæk Bugt | · | 16 (1991–2018) | +0.12 | 310 | 354,821 | 2 |
| 437.4 | Det sydfynske Øhav | · | 21 (1991–2018) | +0.20 | 334 | 72,370 | 2 |
| 407.5 | Løgstør Bredning | ✓ | — | — | 93 | 161,500 | 2 |
| 355.7 | Nordlige Øresund | · | 32 (1991–2018) | +0.17 | 1,418 | 1,605,986 | 2 |
| 343.4 | Hjelm Bugt | · | 9 (1991–2018) | +0.17 | 31 | 27,545 | 2 |
| 296.0 | Kås Bredning og Venø Bugt | · | — | — | 469 | 282,480 | 3 |
| 290.4 | Jammerland Bugt og Musholm Bugt | · | 9 (1991–2018) | +0.28 | 127 | 189,830 | 2 |
| 288.1 | Lillebælt, Bredningen | · | 32 (1991–2018) | +0.10 | 57 | 40,532 | 2 |
| 279.4 | Ringkøbing Fjord | ✓ | 9 (1991–2018) | +0.08 | 236 | 161,990 | 1 |
| 275.3 | Nordlige Lillebælt | · | 20 (1991–2018) | +0.11 | 191 | 15,150 | 2 |
| 247.1 | Smålandsfarvandet, syd | · | 11 (1991–2018) | +0.10 | 162 | 53,283 | 2 |
| 242.4 | Rødsand og Bredningen | · | 6 (1991–2018) | +0.28 | 115 | 12,107 | 2 |
| 238.2 | Nissum Bredning | ✓ | — | — | 84 | 114,015 | 2 |
| 231.6 | Århus Bugt og Begtrup Vig | · | 20 (1991–2018) | +0.04 | 772 | 578,019 | 2 |
| 228.6 | Langelandssund | · | 20 (1991–2018) | +0.39 | 54 | 119,500 | 2 |
| 227.9 | Isefjord, ydre | ✓ | 26 (1991–2018) | +0.23 | 71 | 22,404 | 1 |
| 222.1 | Bjørnholms Bugt, Riisgårde Bredning, Skive Fjord og Lovns Bredning | ✓ | 16 (1991–2018) | +0.12 | 299 | 90,355 | 1 |
| 214.6 | Vesterhavet, nord | · | 21 (1991–2018) | — | 48 | 430 | 3 |
| 211.6 | Anholt | · | 1 (1991–2018) | — | 0 | 0 | 3 |
| 211.4 | Østersøen, Bornholm | · | 23 (1991–2018) | +0.16 | 185 | 102,697 | 2 |
| 205.3 | Lister Dyb | · | 1 (1991–2018) | — | 192 | 56,105 | 3 |
| 199.1 | Femerbælt | · | 9 (1991–2018) | +0.29 | 82 | 25,561 | 2 |
| 175.2 | Djursland Øst | · | 10 (1991–2018) | +0.19 | 182 | 94,092 | 2 |
| 169.7 | Øresund, 12 sm | · | — | — | 0 | 0 | 3 |
| 165.9 | Nibe Bredning og Langerak | ✓ | — | — | 896 | 336,244 | 2 |
| 164.0 | Storebælt, SV | · | 14 (1991–2018) | — | 35 | 84,575 | 3 |
| 158.5 | Knudedyb | · | — | — | 138 | 30,850 | 3 |
| 151.0 | Thisted Bredning | ✓ | — | — | 96 | 97,876 | 2 |
| 149.9 | Flensborg Fjord, ydre | ✓ | 14 (1991–2018) | +0.10 | 103 | 10,465 | 1 |
| 131.8 | Stege Bugt | · | 5 (1991–2018) | +0.10 | 43 | 25,958 | 2 |
| 128.0 | Juvre Dyb | · | — | — | 31 | 1,475 | 3 |
| 124.0 | Grådyb | · | 8 (1991–2018) | +0.26 | 332 | 449,600 | 2 |
| 116.3 | Storebælt, NV | · | 12 (1991–2018) | — | 65 | 30,000 | 3 |
| 100.5 | Grønsund | · | 8 (1991–2018) | +0.14 | 116 | 48,103 | 2 |
| 92.0 | Vejle Fjord, ydre | ✓ | 11 (1991–2018) | +0.07 | 108 | 48,760 | 1 |
| 85.9 | Isefjord, indre | ✓ | 9 (1991–2018) | +0.17 | 280 | 119,877 | 1 |
| 84.5 | Ebeltoft Vig | · | 7 (1991–2018) | — | 27 | 0 | 3 |
| 77.7 | Kalø Vig | · | 6 (1991–2018) | +0.26 | 335 | 24,276 | 2 |
| 75.7 | Kalundborg Fjord | · | 11 (1991–2018) | +0.04 | 80 | 2,600 | 2 |
| 71.4 | Roskilde Fjord, ydre | ✓ | 13 (1991–2018) | +0.13 | 358 | 139,933 | 1 |
| 66.6 | Helnæs Bugt | · | 8 (1991–2018) | +0.47 | 131 | 20,300 | 2 |
| 65.7 | Lillebælt, Als-Ærø 12 sm | · | — | — | 0 | 0 | 3 |
| 59.7 | Lillebælt, Snævringen | · | — | — | 232 | 580,100 | 3 |
| 51.8 | Roskilde Fjord, indre | ✓ | 7 (1991–2018) | +0.50 | 393 | 217,960 | 1 |
| 51.2 | Guldborgsund | · | 3 (1991–2018) | — | 149 | 63,476 | 3 |
| 50.4 | Nakskov Fjord | · | 2 (1991–2018) | — | 117 | 28,921 | 3 |
| 45.8 | Odense Fjord, ydre | ✓ | — | — | 37 | 20,000 | 2 |
| 45.6 | Horsens Fjord, indre | ✓ | 4 (1991–2018) | +0.21 | 549 | 267,612 | 1 |
| 40.7 | Avnø Fjord | · | 1 (1991–2018) | — | 2 | 0 | 3 |
| 35.0 | Als Fjord | · | 3 (1991–2018) | — | 47 | 171 | 3 |
| 32.6 | Nissum Fjord, ydre | ✓ | — | — | 22 | 2,500 | 2 |
| 32.6 | Åbenrå Fjord | ✓ | 11 (1991–2018) | +0.18 | 229 | 87,500 | 1 |
| 32.6 | Horsens Fjord, ydre | ✓ | 4 (1991–2018) | — | 14 | 225 | 2 |
| 27.8 | Mariager Fjord, ydre | ✓ | 2 (1991–2018) | — | 114 | 450 | 2 |
| 24.5 | Hjarbæk Fjord | · | 2 (1991–2018) | — | 232 | 108,500 | 3 |
| 21.9 | Præstø Fjord | · | 2 (1991–2018) | — | 62 | 13,170 | 3 |
| 19.8 | Nissum Fjord, mellem | ✓ | 2 (1991–2018) | — | 12 | 0 | 2 |
| 18.9 | Østersøen, Christiansø | · | — | — | 0 | 0 | 3 |
| 18.1 | Randers Fjord, ydre | ✓ | 2 (1994–2018) | — | 45 | 4,631 | 2 |
| 17.6 | Mariager Fjord, indre | ✓ | 4 (1991–2018) | — | 245 | 14,850 | 2 |
| 17.0 | Dybsø Fjord | · | 1 (1991–2018) | — | 32 | 165 | 3 |
| 16.3 | Vejle Fjord, indre | ✓ | 7 (1991–2018) | +0.05 | 728 | 224,735 | 1 |
| 16.0 | Stavns Fjord | · | — | — | 6 | 25 | 3 |
| 15.7 | Karrebæk Fjord | · | — | — | 188 | 127,348 | 3 |
| 15.4 | Odense Fjord, Seden Strand | ✓ | — | — | 565 | 491,620 | 2 |
| 15.0 | Augustenborg Fjord | · | 2 (1991–2018) | — | 77 | 0 | 3 |
| 13.4 | Halkær Bredning | · | — | — | 109 | 71,475 | 3 |
| 12.9 | Flensborg Fjord, indre | ✓ | 6 (1991–2018) | +0.07 | 84 | 97,035 | 1 |
| 10.7 | Faaborg Fjord | · | 3 (1991–2018) | — | 83 | 0 | 3 |
| 10.6 | Lunkebugten | · | 2 (1991–2018) | — | 13 | 0 | 3 |
| 10.4 | Nissum Fjord, Felsted Kog | ✓ | — | — | 34 | 9,415 | 2 |
| 10.2 | Gamborg Fjord | · | 2 (1991–2018) | — | 38 | 22,000 | 3 |
| 10.1 | Kolding Fjord, ydre | ✓ | 4 (1991–2018) | — | 41 | 0 | 2 |
| 10.0 | Kløven | · | — | — | 13 | 3,500 | 3 |
| 9.5 | Basnæs Nor | · | — | — | 5 | 250 | 3 |
| 8.0 | Nyborg Fjord | · | — | — | 56 | 0 | 3 |
| 7.9 | Nybøl Nor | · | — | — | 65 | 100 | 3 |
| 7.8 | Korsør Nor | · | — | — | 95 | 2,000 | 3 |
| 7.4 | Knebel Vig | · | 1 (1992–2018) | — | 13 | 3,811 | 3 |
| 7.1 | Randers Fjord, indre | ✓ | — | — | 417 | 204,688 | 2 |
| 6.8 | Lindelse Nor | · | — | — | 2 | 0 | 3 |
| 6.5 | Holsteinborg Nor | · | — | — | 60 | 13,595 | 3 |
| 6.0 | Lillestrand | · | — | — | 0 | 0 | 3 |
| 5.5 | Als Sund | · | — | — | 38 | 94,055 | 3 |
| 5.3 | Kertinge Nor | · | — | — | 98 | 4,540 | 3 |
| 5.2 | Skælskør Fjord og Nor | · | — | — | 85 | 38,230 | 3 |
| 5.1 | Haderslev Fjord | · | — | — | 201 | 106,666 | 3 |
| 5.1 | Stege Nor | · | — | — | 12 | 0 | 3 |
| 5.0 | Genner Bugt | · | 6 (1991–2018) | — | 16 | 3,910 | 3 |
| 4.8 | Kolding Fjord, indre | ✓ | 2 (1991–2018) | — | 318 | 35,085 | 2 |
| 4.8 | Nærå Strand | · | — | — | 42 | 0 | 3 |
| 3.3 | Kerteminde Fjord | · | — | — | 22 | 0 | 3 |
| 1.9 | Hejlsminde Nor | · | — | — | 25 | 30,000 | 3 |
| 1.8 | Norsminde Fjord | · | — | — | 161 | 38,000 | 3 |
| 0.5 | Holckenhavn Fjord | · | — | — | 60 | 31,000 | 3 |
| 0.4 | Avnø Vig | · | — | — | 11 | 0 | 3 |
| 0.3 | Bredningen | · | — | — | 17 | 2,800 | 3 |
| 0.2 | Aborg Minde Nor | · | — | — | 51 | 17,800 | 3 |

The full record for each area — every pressure, every stream with its years, and the written-out list of what cannot be modelled there — is in `data/derived/areas.json`, which `scripts/areas.py` writes locally and the repository does not ship, and drawn with its timeline on [the map](areas.html).

## What this is not

It is not a causal model per area. It is the ledger you need before you can build one: which areas have enough observation to support a claim, which have none, and over which years each stream exists — so that an analysis published in 2025 cannot quietly rest on a relation fitted to 1990–2012 without a reader seeing the gap.

