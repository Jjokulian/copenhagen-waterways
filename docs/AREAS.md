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
> - **Category wider than corpus — only a count is honest.** *56% of the sea has no marine observation* names a category — marine observation — far wider than the two layers actually searched. The leftover after subtracting what we happened to find is then reported as though it were measured, which is the operation [RESIDUAL.md](#RESIDUAL.md) is about, and it does not become acceptable because we are the ones doing it.
>
> So absence is reported here as a count over a named corpus, and the corpus is named every time. Anyone who knows of a marine series this project has not assembled is holding a correction, and it is wanted.

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
| 1,148.6 | Lillebælt, syd | · | 26 (1991–2018) | +0.19 | 118 | 115,906 | 1 |
| 1,052.5 | Kattegat, Aalborg Bugt | · | 14 (1991–2018) | +0.36 | 117 | 88,955 | 1 |
| 990.7 | Skagerrak | · | 33 (1991–2018) | +0.16 | 419 | 481,197 | 1 |
| 821.0 | Sejerø Bugt | · | 27 (1991–2018) | +0.24 | 104 | 71,550 | 1 |
| 721.2 | Kattegat, Nordsjælland | · | 34 (1991–2018) | +0.27 | 295 | 205,544 | 1 |
| 686.8 | Storebælt, nord 12 sm | · | — | — | 0 | 0 | 4 |
| 655.2 | Vesterhavet, syd | · | 12 (1991–2018) | — | 3 | 0 | 2 |
| 609.4 | Kattegat, Læsø | · | 6 (1991–2018) | +0.23 | 6 | 3,860 | 2 |
| 572.6 | Storebælt, syd 12 sm | · | — | — | 0 | 0 | 4 |
| 562.4 | Køge Bugt | · | 29 (1991–2018) | +0.21 | 865 | 681,555 | 1 |
| 554.6 | Kattegat, Nordsjælland >20 m | · | — | — | 0 | 0 | 4 |
| 551.0 | Fakse Bugt | · | 13 (1991–2018) | +0.18 | 78 | 152,578 | 1 |
| 497.0 | Femerbælt, 12 sm | · | — | — | 0 | 0 | 3 |
| 482.2 | Lillebælt, syd 12 sm | · | — | — | 0 | 0 | 3 |
| 459.5 | Hevring Bugt | · | 17 (1991–2018) | +0.40 | 76 | 165 | 1 |
| 458.4 | Nordlige Kattegat, Ålbæk Bugt | · | 16 (1991–2018) | +0.12 | 310 | 354,821 | 2 |
| 437.4 | Det sydfynske Øhav | · | 21 (1991–2018) | +0.20 | 334 | 72,370 | 1 |
| 407.5 | Løgstør Bredning | ✓ | — | — | 93 | 161,500 | 1 |
| 355.7 | Nordlige Øresund | · | 32 (1991–2018) | +0.17 | 1,418 | 1,605,986 | 1 |
| 343.4 | Hjelm Bugt | · | 9 (1991–2018) | +0.17 | 31 | 27,545 | 2 |
| 296.0 | Kås Bredning og Venø Bugt | · | — | — | 469 | 282,480 | 2 |
| 290.4 | Jammerland Bugt og Musholm Bugt | · | 9 (1991–2018) | +0.28 | 127 | 189,830 | 1 |
| 288.1 | Lillebælt, Bredningen | · | 32 (1991–2018) | +0.10 | 57 | 40,532 | 2 |
| 279.4 | Ringkøbing Fjord | ✓ | 9 (1991–2018) | +0.08 | 236 | 161,990 | 0 |
| 275.3 | Nordlige Lillebælt | · | 20 (1991–2018) | +0.11 | 191 | 15,150 | 1 |
| 247.1 | Smålandsfarvandet, syd | · | 11 (1991–2018) | +0.10 | 162 | 53,283 | 1 |
| 242.4 | Rødsand og Bredningen | · | 6 (1991–2018) | +0.28 | 115 | 12,107 | 1 |
| 238.2 | Nissum Bredning | ✓ | — | — | 84 | 114,015 | 1 |
| 231.6 | Århus Bugt og Begtrup Vig | · | 20 (1991–2018) | +0.04 | 772 | 578,019 | 2 |
| 228.6 | Langelandssund | · | 20 (1991–2018) | +0.39 | 54 | 119,500 | 2 |
| 227.9 | Isefjord, ydre | ✓ | 26 (1991–2018) | +0.23 | 71 | 22,404 | 1 |
| 222.1 | Bjørnholms Bugt, Riisgårde Bredning, Skive Fjord og Lovns Bredning | ✓ | 16 (1991–2018) | +0.12 | 299 | 90,355 | 0 |
| 214.6 | Vesterhavet, nord | · | 21 (1991–2018) | — | 48 | 430 | 2 |
| 211.6 | Anholt | · | 1 (1991–2018) | — | 0 | 0 | 3 |
| 211.4 | Østersøen, Bornholm | · | 23 (1991–2018) | +0.16 | 185 | 102,697 | 1 |
| 205.3 | Lister Dyb | · | 1 (1991–2018) | — | 192 | 56,105 | 2 |
| 199.1 | Femerbælt | · | 9 (1991–2018) | +0.29 | 82 | 25,561 | 1 |
| 175.2 | Djursland Øst | · | 10 (1991–2018) | +0.19 | 182 | 94,092 | 2 |
| 169.7 | Øresund, 12 sm | · | — | — | 0 | 0 | 3 |
| 165.9 | Nibe Bredning og Langerak | ✓ | — | — | 896 | 336,244 | 1 |
| 164.0 | Storebælt, SV | · | 14 (1991–2018) | — | 35 | 84,575 | 2 |
| 158.5 | Knudedyb | · | — | — | 138 | 30,850 | 2 |
| 151.0 | Thisted Bredning | ✓ | — | — | 96 | 97,876 | 1 |
| 149.9 | Flensborg Fjord, ydre | ✓ | 14 (1991–2018) | +0.10 | 103 | 10,465 | 1 |
| 131.8 | Stege Bugt | · | 5 (1991–2018) | +0.10 | 43 | 25,958 | 2 |
| 128.0 | Juvre Dyb | · | — | — | 31 | 1,475 | 2 |
| 124.0 | Grådyb | · | 8 (1991–2018) | +0.26 | 332 | 449,600 | 1 |
| 116.3 | Storebælt, NV | · | 12 (1991–2018) | — | 65 | 30,000 | 3 |
| 100.5 | Grønsund | · | 8 (1991–2018) | +0.14 | 116 | 48,103 | 1 |
| 92.0 | Vejle Fjord, ydre | ✓ | 11 (1991–2018) | +0.07 | 108 | 48,760 | 0 |
| 85.9 | Isefjord, indre | ✓ | 9 (1991–2018) | +0.17 | 280 | 119,877 | 0 |
| 84.5 | Ebeltoft Vig | · | 7 (1991–2018) | — | 27 | 0 | 3 |
| 77.7 | Kalø Vig | · | 6 (1991–2018) | +0.26 | 335 | 24,276 | 2 |
| 75.7 | Kalundborg Fjord | · | 11 (1991–2018) | +0.04 | 80 | 2,600 | 2 |
| 71.4 | Roskilde Fjord, ydre | ✓ | 13 (1991–2018) | +0.13 | 358 | 139,933 | 0 |
| 66.6 | Helnæs Bugt | · | 8 (1991–2018) | +0.47 | 131 | 20,300 | 1 |
| 65.7 | Lillebælt, Als-Ærø 12 sm | · | — | — | 0 | 0 | 3 |
| 59.7 | Lillebælt, Snævringen | · | — | — | 232 | 580,100 | 3 |
| 51.8 | Roskilde Fjord, indre | ✓ | 7 (1991–2018) | +0.50 | 393 | 217,960 | 0 |
| 51.2 | Guldborgsund | · | 3 (1991–2018) | — | 149 | 63,476 | 2 |
| 50.4 | Nakskov Fjord | · | 2 (1991–2018) | — | 117 | 28,921 | 2 |
| 45.8 | Odense Fjord, ydre | ✓ | — | — | 37 | 20,000 | 2 |
| 45.6 | Horsens Fjord, indre | ✓ | 4 (1991–2018) | +0.21 | 549 | 267,612 | 0 |
| 40.7 | Avnø Fjord | · | 1 (1991–2018) | — | 2 | 0 | 3 |
| 35.0 | Als Fjord | · | 3 (1991–2018) | — | 47 | 171 | 3 |
| 32.6 | Nissum Fjord, ydre | ✓ | — | — | 22 | 2,500 | 2 |
| 32.6 | Åbenrå Fjord | ✓ | 11 (1991–2018) | +0.18 | 229 | 87,500 | 0 |
| 32.6 | Horsens Fjord, ydre | ✓ | 4 (1991–2018) | — | 14 | 225 | 2 |
| 27.8 | Mariager Fjord, ydre | ✓ | 2 (1991–2018) | — | 114 | 450 | 2 |
| 24.5 | Hjarbæk Fjord | · | 2 (1991–2018) | — | 232 | 108,500 | 2 |
| 21.9 | Præstø Fjord | · | 2 (1991–2018) | — | 62 | 13,170 | 2 |
| 19.8 | Nissum Fjord, mellem | ✓ | 2 (1991–2018) | — | 12 | 0 | 1 |
| 18.9 | Østersøen, Christiansø | · | — | — | 0 | 0 | 3 |
| 18.1 | Randers Fjord, ydre | ✓ | 2 (1994–2018) | — | 45 | 4,631 | 2 |
| 17.6 | Mariager Fjord, indre | ✓ | 4 (1991–2018) | — | 245 | 14,850 | 1 |
| 17.0 | Dybsø Fjord | · | 1 (1991–2018) | — | 32 | 165 | 3 |
| 16.3 | Vejle Fjord, indre | ✓ | 7 (1991–2018) | +0.05 | 728 | 224,735 | 0 |
| 16.0 | Stavns Fjord | · | — | — | 6 | 25 | 3 |
| 15.7 | Karrebæk Fjord | · | — | — | 188 | 127,348 | 2 |
| 15.4 | Odense Fjord, Seden Strand | ✓ | — | — | 565 | 491,620 | 1 |
| 15.0 | Augustenborg Fjord | · | 2 (1991–2018) | — | 77 | 0 | 3 |
| 13.4 | Halkær Bredning | · | — | — | 109 | 71,475 | 2 |
| 12.9 | Flensborg Fjord, indre | ✓ | 6 (1991–2018) | +0.07 | 84 | 97,035 | 0 |
| 10.7 | Faaborg Fjord | · | 3 (1991–2018) | — | 83 | 0 | 2 |
| 10.6 | Lunkebugten | · | 2 (1991–2018) | — | 13 | 0 | 2 |
| 10.4 | Nissum Fjord, Felsted Kog | ✓ | — | — | 34 | 9,415 | 2 |
| 10.2 | Gamborg Fjord | · | 2 (1991–2018) | — | 38 | 22,000 | 2 |
| 10.1 | Kolding Fjord, ydre | ✓ | 4 (1991–2018) | — | 41 | 0 | 1 |
| 10.0 | Kløven | · | — | — | 13 | 3,500 | 3 |
| 9.5 | Basnæs Nor | · | — | — | 5 | 250 | 2 |
| 8.0 | Nyborg Fjord | · | — | — | 56 | 0 | 3 |
| 7.9 | Nybøl Nor | · | — | — | 65 | 100 | 2 |
| 7.8 | Korsør Nor | · | — | — | 95 | 2,000 | 3 |
| 7.4 | Knebel Vig | · | 1 (1992–2018) | — | 13 | 3,811 | 3 |
| 7.1 | Randers Fjord, indre | ✓ | — | — | 417 | 204,688 | 1 |
| 6.8 | Lindelse Nor | · | — | — | 2 | 0 | 3 |
| 6.5 | Holsteinborg Nor | · | — | — | 60 | 13,595 | 2 |
| 6.0 | Lillestrand | · | — | — | 0 | 0 | 3 |
| 5.5 | Als Sund | · | — | — | 38 | 94,055 | 3 |
| 5.3 | Kertinge Nor | · | — | — | 98 | 4,540 | 2 |
| 5.2 | Skælskør Fjord og Nor | · | — | — | 85 | 38,230 | 2 |
| 5.1 | Haderslev Fjord | · | — | — | 201 | 106,666 | 2 |
| 5.1 | Stege Nor | · | — | — | 12 | 0 | 3 |
| 5.0 | Genner Bugt | · | 6 (1991–2018) | — | 16 | 3,910 | 3 |
| 4.8 | Kolding Fjord, indre | ✓ | 2 (1991–2018) | — | 318 | 35,085 | 1 |
| 4.8 | Nærå Strand | · | — | — | 42 | 0 | 2 |
| 3.3 | Kerteminde Fjord | · | — | — | 22 | 0 | 3 |
| 1.9 | Hejlsminde Nor | · | — | — | 25 | 30,000 | 2 |
| 1.8 | Norsminde Fjord | · | — | — | 161 | 38,000 | 2 |
| 0.5 | Holckenhavn Fjord | · | — | — | 60 | 31,000 | 2 |
| 0.4 | Avnø Vig | · | — | — | 11 | 0 | 3 |
| 0.3 | Bredningen | · | — | — | 17 | 2,800 | 3 |
| 0.2 | Aborg Minde Nor | · | — | — | 51 | 17,800 | 2 |

The full record for each area — every pressure, every stream with its years, and the written-out list of what cannot be modelled there — is in [`data/derived/areas.json`](data/derived/areas.json), and drawn with its timeline on [the map](areas.html).

## What this is not

It is not a causal model per area. It is the ledger you need before you can build one: which areas have enough observation to support a claim, which have none, and over which years each stream exists — so that an analysis published in 2025 cannot quietly rest on a relation fitted to 1990–2012 without a reader seeing the gap.

