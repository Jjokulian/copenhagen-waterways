# What Denmark measures, and where

The nitrogen requirement is computed **per water body**. Status, environmental target and indsatsbehov are each one number attached to one polygon, and the whole chain assumes that polygon is uniform enough for one number to describe it. This page asks where the instruments actually are, what they sample, and whether the polygon is a real thing.

Sources: DCE/Aarhus Universitet's method report for the marine indsatsbehov (2015), and the national VP3 layers - 123 marine water bodies and 1,026 bathing stations carrying annual quality 1991-2018, each tagged with the water body it sits in.

## 1. The unit spans four orders of magnitude

These are all *one water body*, each with one status and one requirement:

| km² | name | type |
|---:|---|---|
| 0.2 | Aborg Minde Nor | FjVuF-T38 |
| 0.3 | Bredningen | FjVuF-T38 |
| 0.4 | Avnø Vig | FjVu2-T8 |
| 0.5 | Holckenhavn Fjord | FjVu3-T33 |
|  | … |  |
| 2,495.8 | Nordlige Kattegat, 12 sm | Ej relevant |
| 3,703.1 | Vesterhavet, 12 sm | Ej relevant |
| 3,831.4 | Bornholm, 12 sm | Ej relevant |
| 4,248.6 | Skagerrak, 12 sm | Ej relevant |

123 polygons, 43,579 km², 41 distinct type codes, of which 14 are typed `Ej relevant`. Median 84.5 km², mean 354.3 km² - the mean is four times the median because a handful of open-sea polygons carry most of the area.

## 2. The statistical models cover 5.7% of the sea, and all of it is fjord

DCE built statistical models for **29 coastal stations representing 22 water bodies**, on data from **1990-2012**, requiring series longer than 15 years. The caption on their own validation table calls them *fjordmodellerne*.

Matching every station area named in that table against the national polygon set gives **2,492 km² of 43,579 km² - 5.7% of Danish marine water-body area**.

The largest water bodies with no statistical model at all:

| km² | name |
|---:|---|
| 4,248.6 | Skagerrak, 12 sm |
| 3,831.4 | Bornholm, 12 sm |
| 3,703.1 | Vesterhavet, 12 sm |
| 2,495.8 | Nordlige Kattegat, 12 sm |
| 1,880.8 | Østersøen, 12 sm |
| 1,835.6 | Århus Bugt syd, Samsø og Nordlige Bælthav |
| 1,766.8 | Kattegat, SV 12 sm |
| 1,526.1 | Anholt, 12 sm |
| 1,315.8 | Kattegat, SØ 12 sm |
| 1,217.9 | Smålandsfarvandet, åbne del |
| 1,148.6 | Lillebælt, syd |
| 1,052.5 | Kattegat, Aalborg Bugt |

Køge Bugt — `DKCOAST201`, 562 km², the water this project is about — has no statistical model. Whatever coefficient is applied to it is transferred from fjords, and a fjord is the one marine setting whose flushing, stratification and residence time are least like an open bay's.

## 3. The instruments are at the surface, and oxygen is sampled once per six years

The candidate explanatory variables are nutrient loads, freshwater flow, wind stress, irradiance, salinity, water-column stability and **surface** water temperature. Bottom-water temperature is not a candidate anywhere. Stratification enters only as `vandsøjlestabilitet`, and is selected in 13 of the 72 published models.

Iltsvind is a bottom-water phenomenon, and so is the terminus of the fedtemøg cycle. Neither has a bottom-water driver in the model.

> The oxygen indicator itself, from DCE's Tabel 4: the share of time oxygen is below 4 mg/L and 2 mg/L **in the single month where low-oxygen days are most numerous**; six years of data go into the monthly frequencies; **one indicator value emerges per six years**.

DCE also state plainly that the sampling misses the events: *"målingerne af ilt foretages med en frekvens, som ikke nødvendigvis fanger kortvarige iltsvind"*. That single number per six years is not fitted to anything. It is a **binary trigger**: if it fires, the requirement is a flat 25% cut in total nitrogen concentration, chosen because it is *"større end de normale år-til-år variationer"* and because *"det **vurderes**"* to be the minimum that will move the system.

## 4. The window closes where the problem starts

The models are fitted on **1990-2012**. Over that window essentially every candidate driver declined monotonically - nitrogen load, phosphorus load, point-source discharge, atmospheric deposition. A regression on co-declining series cannot separate them; it awards the shared variance to whichever is entered.

DCE report the symptom without drawing the inference:

> *"TN-modellerne har generelt en tendens til systematiske afvigelser over tid, idet de høje TN-koncentrationer observeret i starten af 1990'erne underestimeres, mens de lave TN-koncentrationer i sidste del af perioden overestimeres."*

A predicted range compressed against a monotone observed trend is the signature of a missing monotone covariate. Their own explanation names one and leaves it out of the model: *"tidsforsinkelsen pga. ophobning af organisk bundet kvælstof i sedimenterne"* - an unmodelled state variable with memory.

And several things that plausibly matter *change regime after 2012* and are therefore outside the fit entirely: the national basin-and-separation programme that followed the 2011 cloudburst, the construction wave (Nordhavn, Ørestad, Sluseholmen, Lynetteholm), and trawling effort. None of them can be estimated from a series that stops in 2012 - not because their effect is absent, but because the data end.

The acceptance criterion is **R² ≥ 0.4**, described in the report as *tentativt sat*. R² is the squared normalised cross-covariance between fitted and observed. Two monotone declining series clear |r| ≥ 0.63 without any causal connection between them. No out-of-sample validation is reported, and the explanatory variables were selected per station as the best-performing subset, which inflates R² further.

## 5. Is a water body a real thing? A test

Bathing water is the only long, dense, spatially replicated marine record Denmark has: 1,026 stations, one quality class per year from 1991 to 2018, each carrying the id of the water body it sits in. If the polygon is a real unit, its own stations should co-vary.

Restricting to stations with at least 15 years of record and at least 3 years below *Excellent* (so there is something to correlate), and to water bodies with at least 3 such stations - **42 water bodies**:

> Mean pairwise correlation between two stations **inside the same water body**: **r = +0.203**, i.e. **R² = 0.041**.

Two stations in one legally-uniform water body share about four percent of their year-to-year variance. The model acceptance threshold for describing that same water body is ten times higher.

It is not an artefact of size. The least internally coherent bodies include some of the smallest:

| km² | water body | stations | mean r |
|---:|---|---:|---:|
| 75.7 | Kalundborg Fjord | 8 | +0.037 |
| 231.6 | Århus Bugt og Begtrup Vig | 5 | +0.042 |
| 16.3 | Vejle Fjord, indre | 6 | +0.049 |
| 92.0 | Vejle Fjord, ydre | 5 | +0.066 |
| 12.9 | Flensborg Fjord, indre | 5 | +0.072 |
| 279.4 | Ringkøbing Fjord | 8 | +0.077 |

Matched on separation, against pairs that straddle a boundary:

| separation | same water body | different water bodies |
|---|---|---|
| 2–5 km | +0.269 (288) | +0.116 (40) |
| 5–10 km | +0.214 (374) | +0.137 (224) |
| 10–25 km | +0.152 (892) | +0.138 (1,948) |

The boundary carries a little information at 2–10 km and **none past 10 km**. Beyond ten kilometres, knowing that two points are in the same water body tells you nothing about whether they behave alike.

## 6. Boundaries that separate things which behave alike

Of 20 adjacent water-body pairs with enough stations to test, **7 (35%)** have stations that agree *across* the boundary more than either body's own stations agree among themselves. For those pairs the boundary carries negative information.

| across | own A | own B | pairs | A │ B |
|---:|---:|---:|---:|---|
| +0.318 | +0.225 | +0.241 | 21 | Isefjord, ydre │ Sejerø Bugt |
| +0.303 | +0.280 | +0.241 | 8 | Jammerland Bugt og Musholm Bugt │ Sejerø Bugt |
| +0.287 | +0.130 | +0.272 | 8 | Roskilde Fjord, ydre │ Kattegat, Nordsjælland |
| +0.232 | +0.098 | +0.112 | 34 | Lillebælt, Bredningen │ Nordlige Lillebælt |
| +0.174 | +0.072 | +0.101 | 17 | Flensborg Fjord, indre │ Flensborg Fjord, ydre |
| +0.130 | +0.066 | +0.112 | 25 | Vejle Fjord, ydre │ Nordlige Lillebælt |
| +0.115 | +0.066 | +0.049 | 23 | Vejle Fjord, ydre │ Vejle Fjord, indre |

Two of those are a single fjord cut into *indre* and *ydre*, where the cut is worse than no cut - and both Vejle Fjord and Flensborg Fjord carry statistical models and separate requirements for each half.

## 7. Køge Bugt is at least two things

Køge Bugt is one water body with 24 informative bathing stations - enough to ask whether it is one thing. Searching every north/south cut for the one that best separates it:

> The cut falls at **55.581°N**, at *Greve Badehotel*. North of it (5 stations) and south of it (19 stations) each cohere at **r = +0.267**; across the cut, **r = +0.107** - less than half.

The northern group is KBS, ud for Hyldetangen; Vallensbæk strand, ved Skrubben; Ishøj strand, Ud for Jæger sø; Strandparken, Hundigevej; Amager Sydstrand — the Køge Bugt Strandpark lagoon chain and the Amager outfall shore. The administrative polygon treats them and the open southern coast as one water with one status. The data say they are two.

## What this does and does not show

Bathing quality is a faecal indicator measure. Its variance is driven by local rain and outfalls, so **low spatial coherence here is not proof that chlorophyll is equally incoherent inside a water body.** That test cannot be run: the marine monitoring programme puts 29 stations across 22 modelled water bodies — a median of one each — so there is no replication to run it on.

What it does show is that the water body is not, in general, a unit within which measurable marine state is homogeneous - and that the one variable Denmark does measure at enough points to check the assumption does not support it. Homogeneity is asserted by the delineation, not demonstrated by it. The burden belongs on the side making the assertion, and it is discharged nowhere in the method documents.

The constructive version is not "scrap the water bodies". It is that the partition is an empirical question with an empirical answer, and the data to answer it would be one more monitoring station in each of the bodies that currently have one. That is a smaller ask than a nitrogen reduction.

