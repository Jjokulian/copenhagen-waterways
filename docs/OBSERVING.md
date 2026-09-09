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

## 3. What the statistical layer is allowed to consider

The models in Tabel 3 — the ones that produce the per-area numbers — draw their explanatory variables from a fixed list of eight, given in Tabel 2: nutrient loads (N and P), freshwater flow, wind stress, irradiance, salinity, water-column stability, and **surface** water temperature. Bottom-water temperature is not on the list. Stratification appears only as `vandsøjlestabilitet`, selected in 13 of the 72 models.

That list is worth reading for what is not on it. An oxygen deficit is a balance — what removes oxygen against what resupplies it — and the routes on both sides are many. Imported organic matter exerts its demand directly, with no nitrogen and no growth step in between. Ammonium exerts a demand chemically, by being oxidised. Sulphide released from disturbed sediment consumes oxygen the moment it meets it. A kill event of any cause leaves a decaying mass and a bacterial bloom on it. Warmer water holds less; a column that does not turn over does not refill. None of those is a candidate variable, so whatever share belongs to them has nowhere to go but into the coefficients on the variables that are there. The enumeration is in [OXYGEN.md](OXYGEN.md).

The oxygen requirement itself comes from no regression at all. It is a **binary trigger** on an indicator that is the share of time oxygen sits below 4 mg/L and 2 mg/L **in the single month where low-oxygen days are most numerous**, computed from six years of measurements, yielding **one value per water body per six years**. Oxygen is sampled far more often than that; this is about what survives the aggregation. Eleven months of every year are discarded before the number is formed, and the six-year collapse removes what is left of the temporal signal — including any trend, and including whatever happened in the years the shore actually got worse.

DCE state plainly that the sampling misses the events: *"målingerne af ilt foretages med en frekvens, som ikke nødvendigvis fanger kortvarige iltsvind"*. If the trigger fires, the requirement is a flat 25% cut in total nitrogen concentration, chosen because it is *"større end de normale år-til-år variationer"* and because *"det **vurderes**"* to be the minimum that will move the system. A judged round number, not a fitted response.

> **Scope of this section.** Everything above is read from the statistical modelling report (Timmermann et al. 2015) and its Tabel 2 and Tabel 3. A second, mechanistic modelling layer exists (DHI, Erichsen & Kaas 2015) which this project has not yet read in the original. Nothing here should be taken as a claim about what that layer does or does not contain.

## 4. The window closes where the problem starts

The models are fitted on **1990-2012**. Over that window essentially every candidate driver declined monotonically - nitrogen load, phosphorus load, point-source discharge, atmospheric deposition. A regression on co-declining series cannot separate them; it awards the shared variance to whichever is entered.

DCE report the symptom without drawing the inference:

> *"TN-modellerne har generelt en tendens til systematiske afvigelser over tid, idet de høje TN-koncentrationer observeret i starten af 1990'erne underestimeres, mens de lave TN-koncentrationer i sidste del af perioden overestimeres."*

A predicted range compressed against a monotone observed trend is the signature of a missing monotone covariate. Their own explanation names one and leaves it out of the model: *"tidsforsinkelsen pga. ophobning af organisk bundet kvælstof i sedimenterne"* - an unmodelled state variable with memory.

And several things that plausibly matter *change regime after 2012* and are therefore outside the fit entirely: the national basin-and-separation programme that followed the 2011 cloudburst, the construction wave (Nordhavn, Ørestad, Sluseholmen, Lynetteholm), and trawling effort. None of them can be estimated from a series that stops in 2012 - not because their effect is absent, but because the data end.

The acceptance criterion is **R² ≥ 0.4**, described in the report as *tentativt sat*. R² is the squared normalised cross-covariance between fitted and observed. No out-of-sample validation is reported.

### What that criterion returns when there is nothing there

Their design is documented precisely enough to test the criterion directly. Each data point is *"gennemsnit af målinger for en sæson (år)"* — one seasonal mean per year — with a stated minimum of 15 points. Tabel 2 offers 8 candidate explanatory variables. Tabel 3 shows one to three selected per model, chosen as those *"som giver den største forklaringskraft"*. That is a best-subset search over **92 candidate models fitted to about 20 points**.

So the question is not whether R² = 0.57 is high. It is what that search returns **when there is no relation there at all**. Simulating exactly their design, 400 times per case:

| condition | median R² | 75th | 90th | share clearing R² ≥ 0.4 |
|---|---:|---:|---:|---:|
| 20 points, white noise | 0.34 | 0.43 | 0.51 | 33% |
| 20 points, autocorrelated (phi=0.5) | 0.43 | 0.53 | 0.62 | 59% |
| 20 points, autocorrelated + shared decline | 0.56 | 0.66 | 0.74 | 82% |
| 15 points (their stated minimum), same | 0.66 | 0.75 | 0.82 | 90% |

Annual marine and climate series are autocorrelated, and over 1990–2012 every candidate declined together. Those are the bottom two rows. Under the conditions their own data satisfy, **the median R² from pure noise is 0.56–0.66, and 82–90% of noise models clear their acceptance criterion.**

DCE report a mean R² of **0.56** across all 72 models; the median of the table as parsed here is **0.57**.

> That is not distinguishable from the noise floor of their own selection procedure.

This does **not** show the relations are false. Several are probably real — the phosphorus models in particular are strong and mechanistically expected. What it shows is that the reported R² carries no evidence either way, because the threshold was set below the null distribution of the search that produced it. The fix is cheap and standard: hold out years, or report the R² of the N-load term alone against a model containing only the climate variables. Neither is reported for any of the 72.

Two caveats, stated because they matter. The simulation assumes all 8 candidates were offered to every model; if variables were pre-screened on mechanistic grounds the inflation is smaller — though *"største forklaringskraft"* describes a search, not a screen. And the shared-decline case assumes a 2-SD monotone drift across the window, which is the right order for Danish nitrogen load but is a choice; the autocorrelation-only row is the conservative version and still puts the median at 0.43.

## 5. Is a water body a real thing? A test

Bathing water is the only long, dense, spatially replicated marine record Denmark has: 1,026 stations, one quality class per year from 1991 to 2018, each carrying the id of the water body it sits in. That is enough replication to ask the question directly.

Take all 19,714 beach-year observations across 728 stations in 70 water bodies. Remove the national year-to-year swing first, so a warm wet summer everywhere does not count as structure. Split what is left three ways:

| where the variation lives | share |
|---|---:|
| between water bodies | **7.9%** |
| between beaches *inside* one water body | **13.3%** |
| year to year at a single beach | 78.8% |

*(In plain words: if you had to guess how one beach did in one year, knowing which water body it is in gets you 8% of the way. Knowing which beach — inside that same water body — gets you 13%, nearly twice as much. The unit that policy treats as uniform explains less than the differences within it.)*

The last row is large partly because a four-class ordinal is a noisy instrument, and that noise falls on all three shares equally. The load-bearing comparison is the first two rows against each other, and they do not depend on the noise level at all.

### The same thing said as correlations

Restricting to stations with at least 15 years of record and at least 3 years below *Excellent* (so there is something to correlate), and to water bodies with at least 3 such stations — **42 water bodies**:

> Mean pairwise correlation between two stations **inside the same water body**: **r = +0.203**.

*(In plain words: r is not a verdict, it is a co-wobble score — the average of how far one beach sits above its own usual, in units of its own usual wobble, times the same for the other beach. The divisor is the two **spreads**, not the two means, which is what keeps it between −1 and +1 and lets r² be read as a share. Here that means: 4.1% of the wobble in one beach is shared with the other; knowing the other shrinks your error guessing one beach by 2%.)*

The threshold a model must clear to be accepted as a description of that same water body is R² ≥ 0.4 — which accounts for 40% of the wobble; shrinks prediction error by 23% against just guessing the average. The water body does not cohere to a tenth of the standard its own model is held to.

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

## What the observing system is actually built to see

Set the two records side by side. Denmark's densest, longest, most replicated marine observation is of **faecal contamination** — is it safe to swim. The chain policy acts on — nitrogen to algae to oxygen to a dead seabed — is observed far more thinly, and the oxygen end of it most thinly of all.

| | stations | water bodies | years | data points entering the analysis |
|---|---:|---:|---|---:|
| Bathing water (faecal indicator) | 728 | 70 | 1991–2018 | 19,714 station-years |
| Nutrient/chlorophyll/Kd models | 29 | 22 | 1990–2012 | ~1,440 seasonal means (72 models × ≥15 points) |
| Oxygen indicator | — | per water body | rolling 6-year | **1 value per water body per 6 years** |

Roughly **fourteen times as many observations** stand behind the faecal record as behind every nutrient model in the country combined, they are spread over three times as many water bodies, and they run thirteen years further forward — through exactly the period the fitted window excludes.

That is not a small technical asymmetry. It means the sewage pathway is the one Denmark can actually measure, and the nutrient pathway is the one Denmark acts on. The two hypotheses about what wrecks a Danish shore are not being weighed against each other on comparable evidence — one has an observing system and the other has a model.

## What this does and does not show

The bathing analysis above **cannot adjudicate the nitrogen chain**. It measures *E. coli* and enterococci, not chlorophyll, so the finding that a water body is internally incoherent is a finding about faecal contamination and is not proof that chlorophyll behaves the same way inside one.

But that limit cuts both directions, and the second direction is the one usually left out. The bathing record is not a *weak proxy* for the nutrient question — it is a *strong direct measurement of a competing one*. Whatever it shows about sewage reaching Danish shores, it shows with fourteen times the observational support of anything said about nitrogen, and it keeps showing it after 2012.

Whether the water body is a coherent unit **for chlorophyll** cannot be tested at all: 29 stations across 22 water bodies is a median of one each, and one station cannot disagree with itself. The homogeneity is asserted by the delineation and demonstrated nowhere.

The constructive version is not "scrap the water bodies". It is that the partition is an empirical question with an empirical answer, and the data to answer it would be one more monitoring station in each of the bodies that currently have one. That is a smaller ask than a nitrogen reduction.

