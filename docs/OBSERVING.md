# What Denmark measures, and where

<span class="claim" data-claim="C-OB-UNIT">The nitrogen requirement is computed **per water body**. Status, environmental target and indsatsbehov are each one number attached to one polygon, and the chain assumes that polygon is uniform enough for one number to describe it.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-UNIT "What this claim rests on")</sup> This page asks where the instruments actually are, what they sample, and whether the polygon behaves as one thing.

<span class="claim" data-claim="C-OB-SOURCES">Sources: DCE/Aarhus Universitet's method report for the marine indsatsbehov (2015), and the national VP3 layers - [123](SOURCES.md#F-8b12d8de95) marine water bodies and [1,026](SOURCES.md#F-dbca3955b7) bathing stations with annual quality 1991-2018, [791](SOURCES.md#F-b0191dba4c) of them tagged with a marine water body.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-SOURCES "What this claim rests on")</sup>

## 1. Sizes

These are all *one water body* each:

| km² | name | type |
|---:|---|---|
| [0.2](SOURCES.md#F-4e4265c83e) | Aborg Minde Nor | `FjVuF-T38` |
| [0.3](SOURCES.md#F-b8d7d18518) | Bredningen | `FjVuF-T38` |
| [0.4](SOURCES.md#F-fab5e6ce24) | Avnø Vig | `FjVu2-T8` |
| [0.5](SOURCES.md#F-5dcbcc5c5c) | Holckenhavn Fjord | `FjVu3-T33` |
| | … | |
| [2,495.8](SOURCES.md#F-7b43d4edd8) | `Nordlige Kattegat, 12 sm` | `Ej relevant` |
| [3,703.1](SOURCES.md#F-999218fd71) | `Vesterhavet, 12 sm` | `Ej relevant` |
| [3,831.4](SOURCES.md#F-ee134a262b) | `Bornholm, 12 sm` | `Ej relevant` |
| [4,248.6](SOURCES.md#F-e4431deeb7) | `Skagerrak, 12 sm` | `Ej relevant` |

<span class="claim" data-claim="C-OB-SIZES">The largest is [24,992](SOURCES.md#F-c18d72c531) times the smallest. [123](SOURCES.md#F-8b12d8de95) polygons, [43,579](SOURCES.md#F-273b6ca8d3) km², [41](SOURCES.md#F-53fdb1cd66) distinct type codes, of which [14](SOURCES.md#F-327e352a8c) are typed `Ej relevant`. Median [84.5](SOURCES.md#F-4ccd68e59b) km², mean [354.3](SOURCES.md#F-498766aa4c) km² - the mean is [4.2](SOURCES.md#F-f129e7043f) times the median because the [14](SOURCES.md#F-327e352a8c) open-sea polygons typed `Ej relevant` carry [53](SOURCES.md#F-f779aa1c01)% of the area.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-SIZES "What this claim rests on")</sup>

## 2. Where the statistical models are

<span class="claim" data-claim="C-OB-DCE-SCOPE">DCE built statistical models for **[29](SOURCES.md#F-d19671c79f) coastal stations representing [22](SOURCES.md#F-8878751ad3) water bodies**, on data from **1990-2012**, where series longer than [15](SOURCES.md#F-e114c12750) years exist. The caption on their own validation table calls them *fjordmodellerne*.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-DCE-SCOPE "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-COVERAGE">Matching every station area named in that table against the national polygon set by name gives **[2,492](SOURCES.md#F-ddf87f7943) km² of [43,579](SOURCES.md#F-8099a948c8) km² - [5.7](SOURCES.md#F-629791ba72)% of Danish marine water-body area**. The match takes in [28](SOURCES.md#F-3d072a2e28) polygons where DCE count [22](SOURCES.md#F-8878751ad3) water bodies, so it may include polygons DCE did not model: the share is what the names give, not DCE's own figure.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-COVERAGE "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-UNMODELLED">The largest water bodies the name match finds no statistical model for:</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-UNMODELLED "What this claim rests on")</sup>

| km² | name |
|---:|---|
| [4,248.6](SOURCES.md#F-58a425f213) | `Skagerrak, 12 sm` |
| [3,831.4](SOURCES.md#F-1743836d0d) | `Bornholm, 12 sm` |
| [3,703.1](SOURCES.md#F-542e5508f5) | `Vesterhavet, 12 sm` |
| [2,495.8](SOURCES.md#F-422157afb4) | `Nordlige Kattegat, 12 sm` |
| [1,880.8](SOURCES.md#F-cbc17a9b9d) | `Østersøen, 12 sm` |
| [1,835.6](SOURCES.md#F-b81915f0fe) | Århus Bugt syd, Samsø og Nordlige Bælthav |
| [1,766.8](SOURCES.md#F-d03a9b814f) | `Kattegat, SV 12 sm` |
| [1,526.1](SOURCES.md#F-798c165128) | `Anholt, 12 sm` |
| [1,315.8](SOURCES.md#F-02690fccdf) | `Kattegat, SØ 12 sm` |
| [1,217.9](SOURCES.md#F-c42eaa7dc7) | Smålandsfarvandet, åbne del |
| [1,148.6](SOURCES.md#F-97bc08a0fc) | Lillebælt, syd |
| [1,052.5](SOURCES.md#F-c3bbf08758) | Kattegat, Aalborg Bugt |

<span class="claim" data-claim="C-OB-KOEGE-MODEL">Køge Bugt — `DKCOAST201`, [562](SOURCES.md#F-b5696cb3f7) km², the water this project is about — has no statistical model. Its requirement comes from DHI's mechanistic model instead: DHI's table of computed requirements lists it under that model (`MEK`). DCE's meta-analysis, which transfers what is known from modelled water bodies to similar unmodelled ones, is for water bodies that neither kind of model covers.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-KOEGE-MODEL "What this claim rests on")</sup>

## 3. What the statistical layer is allowed to consider

<span class="claim" data-claim="C-OB-TABEL2">The models in `Tabel 3` draw their explanatory variables from a fixed list given in `Tabel 2` (*vind, temp, salt, irr, BV, Q, N-load og P-load*): nutrient loads (N and P), freshwater flow, wind stress, irradiance, salinity, water-column stability, and **surface** water temperature. Bottom-water temperature is not on the list. Stratification appears only as `vandsøjlestabilitet`, selected in [13](SOURCES.md#F-1ba0e8d176) of the [79](SOURCES.md#F-598345fdb6) models in `Tabel 3`.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-TABEL2 "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-NOT-ON-LIST">That list is worth reading for what is not on it. An oxygen deficit is a balance — what removes oxygen against what resupplies it — and the routes on both sides are many. Imported organic matter exerts its demand directly, with no growth step in between. Ammonium exerts a demand by being oxidised. Sulphide from disturbed sediment consumes oxygen as it is oxidised. A kill of any cause leaves a decaying mass. None of those is a candidate variable; warming and stratification are, as surface temperature and water-column stability. What belongs to a missing driver shows up, if anywhere, in the coefficients of candidates that move with it, or in what the model leaves unexplained. The enumeration is in [OXYGEN.md](OXYGEN.md).</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-NOT-ON-LIST "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-OXYGEN-TRIGGER">The oxygen requirement itself comes from no regression at all. It is a **binary trigger** on an indicator that is the share of time oxygen sits below [4](SOURCES.md#F-dad8fcad81) mg/L and [2](SOURCES.md#F-845a5522fd) mg/L **in the single month where low-oxygen days are most numerous**, computed from [6](SOURCES.md#F-e59dfab87e) years of measurements, yielding **one value per water body per [6](SOURCES.md#F-72bbf95ec1) years**. Oxygen is sampled far more often than that; this is about what survives the aggregation. Every month but one of every year is set aside before the number is formed, and the collapse over years removes what is left of the temporal signal, including any trend within the window.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-OXYGEN-TRIGGER "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-SAMPLING">DCE state that oxygen is measured at a frequency that does not necessarily catch short deficits: *"målingerne af ilt foretages med en frekvens, som ikke nødvendigvis fanger kortvarige iltsvind"*.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-SAMPLING "What this claim rests on")</sup> <span class="claim" data-claim="C-OB-FLAT-CUT">If the trigger fires, the requirement is a flat [25](SOURCES.md#F-8be24edb3a)% cut in total nitrogen concentration, chosen because it is *"større end de normale år-til-år variationer"* and because *"det vurderes"* to be the minimum that will move the system. A judged round number, not a fitted response.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-FLAT-CUT "What this claim rests on")</sup>

> **Scope of this section.** <span class="claim" data-claim="C-OB-SCOPE">Everything above is read from the statistical modelling report (Timmermann et al. 2015), its `Tabel 2` and `Tabel 3`, except the line on Køge Bugt, which is read from DHI's table. The mechanistic modelling layer itself (DHI; Erichsen and co-authors) is among this project's pinned sources but is not examined here, so nothing here is a claim about what it does.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-SCOPE "What this claim rests on")</sup>

## 4. The fitting window ends in 2012

<span class="claim" data-claim="C-OB-DECLINE">The models are fitted on **1990-2012**. Over most of that window Danish nutrient inputs fell: DCE's marine strategy note puts the fall from 1990 to 2010 in total nitrogen input to the coastal waters at [48](SOURCES.md#F-d7a317aa42)%, and in total phosphorus input at [62](SOURCES.md#F-0d53cd5d41)%.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-DECLINE "What this claim rests on")</sup> <span class="claim" data-claim="C-OB-COLLINEAR">A regression on candidates that fall together cannot tell them apart: a stepwise selection gives their shared variance to whichever it picks first.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-COLLINEAR "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-DCE-TNDRIFT">DCE report that the TN models *"har generelt en tendens til systematiske afvigelser over tid, idet de høje TN-koncentrationer observeret i starten af 1990’erne underestimeres"*, and that the low concentrations late in the period are overestimated. The other indicators show it less, which DCE attribute to *"tidsforsinkelsen pga. ophobning af organisk bundet kvælstof i sedimenterne"* — the time lag from nitrogen accumulating in the sediments.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-DCE-TNDRIFT "What this claim rests on")</sup> <span class="claim" data-claim="C-OB-MISSING-COVARIATE">A predicted range compressed against a trending observed series is what a missing trending variable would produce, and the one DCE name is not among the candidates in `Tabel 2`.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-MISSING-COVARIATE "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-AFTER2012">Whatever changed after 2012 — in the sewers, on the coast or at sea — cannot be estimated from a series that stops in 2012: not because its effect is absent, but because the data end.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-AFTER2012 "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-R2DEF">One of several acceptance criteria is **$R^2$ ≥ [0.4](SOURCES.md#F-3a11e5693e)**, described in the report as *tentativt sat*. DCE define $R^2$ as one minus the sum of squared differences between model and observation over the sum of squared deviations of the observations from their mean.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-R2DEF "What this claim rests on")</sup> <span class="claim" data-claim="C-OB-R2-NOTCORR">That is not the square of a correlation: a model whose predictions are biased or compressed scores lower on it, and it can fall below zero.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-R2-NOTCORR "What this claim rests on")</sup>

### What that criterion returns when there is nothing there

<span class="claim" data-claim="C-OB-DCE-DESIGN">Each data point is *"gennemsnit af målinger for en sæson (år)"* — one seasonal mean per year — with a stated minimum of [15](SOURCES.md#F-e48e67ff4f) points. `Tabel 3` shows the few variables selected per model, chosen as those *"som giver den største forklaringskraft"*: stepwise, by cross-validated regression on a calibration part of the data, with each candidate offered over many period windows, then evaluated on held-out data. [The method lab](METHOD_LAB.md) sets out the procedure as the report describes it.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-DCE-DESIGN "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-QUESTION">So the question is not whether a mean $R^2$ of [0.56](SOURCES.md#F-63372240e0) is high. It is what a search like this returns **when there is no relation there at all** - and whether the reported $R^2$ was measured on data the search did not see.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-QUESTION "What this claim rests on")</sup>

> What a simplified version of that search returns from pure noise is simulated, so it is shown on the method page: [the noise floor of an acceptance criterion](METHOD_LAB.md), computed by `noise_floor()` in `scripts/observing.py`.

<span class="claim" data-claim="C-OB-DCE-MEAN">DCE report a mean $R^2$ of **[0.56](SOURCES.md#F-63372240e0)** across all their models.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-DCE-MEAN "What this claim rests on")</sup>

> <span class="claim" data-claim="C-OB-R2-OPEN">[The method lab](METHOD_LAB.md) simulates a simpler, exhaustive in-sample search on pure noise, which clears this criterion more often than not on autocorrelated series. Whether DCE's reported $R^2$ carries evidence depends on whether it was measured on their held-out data, which the report does not say.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-R2-OPEN "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-NOT-FALSE">None of this shows the relations are false.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-NOT-FALSE "What this claim rests on")</sup> <span class="claim" data-claim="C-OB-NTEST">A test that would speak to the nitrogen term specifically is the $R^2$ of the N-load term alone against a model containing only the climate variables.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-NTEST "What this claim rests on")</sup>

## 5. Is a water body one thing? A test

<span class="claim" data-claim="C-OB-BATHING">Bathing water is a long, dense, spatially replicated marine record: [1,026](SOURCES.md#F-dbca3955b7) stations, one quality class per year from 1991 to 2018, [791](SOURCES.md#F-b0191dba4c) of them tagged with the marine water body they sit in. That is enough replication to ask the question directly.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-BATHING "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-VARIANCE">Take all [19,714](SOURCES.md#F-e2b98a8bca) beach-year observations of the [728](SOURCES.md#F-bffddf673d) stations with at least [15](SOURCES.md#F-8ffefb9e51) years of record, in [70](SOURCES.md#F-6a3b63bd99) water bodies. Remove the national year-to-year swing first, so a warm wet summer everywhere does not count as structure. Split what is left three ways:</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-VARIANCE "What this claim rests on")</sup>

| where the variation lives | share |
|---|---:|
| between water bodies | **[7.9](SOURCES.md#F-146cbc8115)%** |
| between beaches *inside* one water body | **[13.3](SOURCES.md#F-ae74e014e2)%** |
| year to year at a single beach | [78.8](SOURCES.md#F-d4b498963d)% |

*(<span class="claim" data-claim="C-OB-VARIANCE-PLAIN">In plain words: if you had to guess how one beach did in one year, knowing which water body it is in gets you [8](SOURCES.md#F-146cbc8115)% of the way. Knowing which beach — inside that same water body — gets you [13](SOURCES.md#F-ae74e014e2)%, [1.7](SOURCES.md#F-6e5031a553) times as much. The unit that policy treats as uniform explains less than the differences within it.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-VARIANCE-PLAIN "What this claim rests on")</sup>)*

<span class="claim" data-claim="C-OB-NOISE">The last row is large partly because a four-class grade is a coarse instrument. Grading noise enters that row in full, and the first two only through averages over each beach's years and each water body's beaches, where it is small; the comparison that carries the argument is the first two rows against each other.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-NOISE "What this claim rests on")</sup>

### The same thing said as correlations

<span class="claim" data-claim="C-OB-INTERNAL">Restricting to stations with at least [15](SOURCES.md#F-8ffefb9e51) years of record and at least [3](SOURCES.md#F-55c094fc1c) years below *Excellent* (so there is something to correlate), and to water bodies with at least [3](SOURCES.md#F-99a3611519) pairs of such stations — **[42](SOURCES.md#F-fc31493caa) water bodies**:</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-INTERNAL "What this claim rests on")</sup>

> <span class="claim" data-claim="C-OB-MEANR">Mean pairwise correlation between two stations **inside the same water body**: **r = [+0.203](SOURCES.md#F-9d9cd6f616)**.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-MEANR "What this claim rests on")</sup>

*(<span class="claim" data-claim="C-OB-R-PLAIN">In plain words: r is not a verdict, it is a co-wobble score — the average of how far one beach sits above its own usual, in units of its own usual wobble, times the same for the other beach. The divisor is the two **spreads**, not the two means, which is what keeps it between minus one and plus one and lets $r^2$ be read as a share. Here that means: [4.1](SOURCES.md#F-eff8eff368)% of the wobble in one beach is shared with the other; knowing the other shrinks your error guessing one beach by [2](SOURCES.md#F-fb6e54bdbb)%</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-R-PLAIN "What this claim rests on")</sup>.)*

<span class="claim" data-claim="C-OB-SMALLEST">The least internally coherent water bodies include the two smallest tested:</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-SMALLEST "What this claim rests on")</sup>

| km² | water body | stations | mean r |
|---:|---|---:|---:|
| [75.7](SOURCES.md#F-e9112247b4) | Kalundborg Fjord | [8](SOURCES.md#F-2abae61af6) | [+0.037](SOURCES.md#F-7bb02a4d25) |
| [231.6](SOURCES.md#F-92a35e0021) | Århus Bugt og Begtrup Vig | [5](SOURCES.md#F-43fc14068e) | [+0.042](SOURCES.md#F-e2dcce0a79) |
| [16.3](SOURCES.md#F-69a0c2e559) | Vejle Fjord, indre | [6](SOURCES.md#F-f47837539d) | [+0.049](SOURCES.md#F-5caba0c8dd) |
| [92.0](SOURCES.md#F-b49691511f) | Vejle Fjord, ydre | [5](SOURCES.md#F-ebc0a40132) | [+0.066](SOURCES.md#F-1b12d5a497) |
| [12.9](SOURCES.md#F-a19712c92b) | Flensborg Fjord, indre | [5](SOURCES.md#F-b99eba6447) | [+0.072](SOURCES.md#F-198bb850cd) |
| [279.4](SOURCES.md#F-f5e2e776c6) | Ringkøbing Fjord | [8](SOURCES.md#F-25e685c2d0) | [+0.077](SOURCES.md#F-7ed58568af) |

Matched on separation, against pairs that straddle a boundary:

| separation | same water body | different water bodies |
|---|---|---|
| [2](SOURCES.md#F-7749c92f5f)–[5](SOURCES.md#F-302225b842) km | [+0.269](SOURCES.md#F-59ac1d5921) ([288](SOURCES.md#F-c523b8e42c)) | [+0.116](SOURCES.md#F-dfac05c958) ([40](SOURCES.md#F-4ce004cee3)) |
| [5](SOURCES.md#F-59a92a4ab5)–[10](SOURCES.md#F-e9eb7c0cc4) km | [+0.214](SOURCES.md#F-ef0f28cf83) ([374](SOURCES.md#F-fac34492e9)) | [+0.137](SOURCES.md#F-8fda19ce2a) ([224](SOURCES.md#F-e76e5a6c8d)) |
| [10](SOURCES.md#F-f3f74835fa)–[25](SOURCES.md#F-0bce6e132c) km | [+0.152](SOURCES.md#F-376b590218) ([892](SOURCES.md#F-8c4efadd25)) | [+0.138](SOURCES.md#F-81f1d78d7d) ([1,948](SOURCES.md#F-9703c7379f)) |

<span class="claim" data-claim="C-OB-DISTANCE">The boundary carries some information at the shorter separations and almost **none past [10](SOURCES.md#F-f3f74835fa) km**, where two stations in the same water body correlate at [+0.152](SOURCES.md#F-376b590218) and two in different ones at [+0.138](SOURCES.md#F-81f1d78d7d). At that range, knowing that two points are in the same water body tells you little about whether they behave alike.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-DISTANCE "What this claim rests on")</sup>

## 6. Boundaries that separate things which behave alike

<span class="claim" data-claim="C-OB-BOUNDARIES">Of [20](SOURCES.md#F-c5ae30f223) pairs of water bodies with at least [6](SOURCES.md#F-d3d6599b3a) station pairs within [15](SOURCES.md#F-e06ea46b73) km of each other across the boundary, **[7](SOURCES.md#F-ef4e6c1a97) ([35](SOURCES.md#F-783827fbb3)%)** have stations that agree *across* the boundary more than either body's own stations agree among themselves. For those pairs the boundary carries negative information.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-BOUNDARIES "What this claim rests on")</sup>

| across | own A | own B | pairs | A │ B |
|---:|---:|---:|---:|---|
| [+0.318](SOURCES.md#F-a2c131e003) | [+0.225](SOURCES.md#F-011ff36876) | [+0.241](SOURCES.md#F-35a4946996) | [21](SOURCES.md#F-fd0f709444) | Isefjord, ydre │ Sejerø Bugt |
| [+0.303](SOURCES.md#F-2c3f673c57) | [+0.280](SOURCES.md#F-cd05df55bc) | [+0.241](SOURCES.md#F-a5d00d0d94) | [8](SOURCES.md#F-4bf0452c6d) | Jammerland Bugt og Musholm Bugt │ Sejerø Bugt |
| [+0.287](SOURCES.md#F-3b70b3d128) | [+0.130](SOURCES.md#F-f8bee7ef75) | [+0.272](SOURCES.md#F-7786b673c0) | [8](SOURCES.md#F-12bd510804) | Roskilde Fjord, ydre │ Kattegat, Nordsjælland |
| [+0.232](SOURCES.md#F-c768f5a59c) | [+0.098](SOURCES.md#F-e93c762584) | [+0.112](SOURCES.md#F-068c7a4b6a) | [34](SOURCES.md#F-91d9ec5b14) | Lillebælt, Bredningen │ Nordlige Lillebælt |
| [+0.174](SOURCES.md#F-bc7ac530dd) | [+0.072](SOURCES.md#F-1f232194da) | [+0.101](SOURCES.md#F-2501c43a59) | [17](SOURCES.md#F-fd71845e9d) | Flensborg Fjord, indre │ Flensborg Fjord, ydre |
| [+0.130](SOURCES.md#F-f81dcfaa63) | [+0.066](SOURCES.md#F-d87328de5e) | [+0.112](SOURCES.md#F-886957921b) | [25](SOURCES.md#F-0c43d1a45d) | Vejle Fjord, ydre │ Nordlige Lillebælt |
| [+0.115](SOURCES.md#F-d0648d065d) | [+0.066](SOURCES.md#F-3f1f1e7a80) | [+0.049](SOURCES.md#F-710aa3fe6f) | [23](SOURCES.md#F-c4aeeec927) | Vejle Fjord, ydre │ Vejle Fjord, indre |

<span class="claim" data-claim="C-OB-FJORDS">Among them, Flensborg Fjord and Vejle Fjord are each one fjord divided into an inner and an outer water body, and in both the division fails this test. DCE have one model station in each of the two fjords (`KFF2` in Flensborg Fjord, `4273` in Vejle Fjord).</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-FJORDS "What this claim rests on")</sup>

## 7. Køge Bugt, cut north and south

<span class="claim" data-claim="C-OB-KOEGE-SEARCH">Køge Bugt is one water body with [24](SOURCES.md#F-4a1c8cf29c) informative bathing stations. Searching every north/south cut for the one that best separates them:</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-KOEGE-SEARCH "What this claim rests on")</sup>

> <span class="claim" data-claim="C-OB-KOEGE-CUT">The cut falls at **[55.581](SOURCES.md#F-2509324540)°N**, at *Greve Badehotel*, with [5](SOURCES.md#F-782a6f9086) stations north of it and [19](SOURCES.md#F-59723a9ad2) south. Pairs on the same side correlate at **r = [+0.267](SOURCES.md#F-85e4d6cb43)** on average; pairs across the cut at **r = [+0.107](SOURCES.md#F-57707ddc0e)** - [0.40](SOURCES.md#F-80a35796ee) of it.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-KOEGE-CUT "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-KOEGE-CAVEAT">Because the cut is the best of every one tried, its contrast is the largest these stations allow, and some contrast would appear even in a water that behaves as one; nothing here measures how much. The northern stations are KBS, ud for Hyldetangen; Vallensbæk strand, ved Skrubben; Ishøj strand, Ud for Jæger sø; Strandparken, Hundigevej; Amager Sydstrand.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-KOEGE-CAVEAT "What this claim rests on")</sup>

## Two records side by side

| | stations | water bodies | years | data points entering the analysis |
|---|---:|---:|---|---:|
| Bathing water (faecal indicator) | [728](SOURCES.md#F-bffddf673d) | [70](SOURCES.md#F-6a3b63bd99) | 1991–2018 | [19,714](SOURCES.md#F-e2b98a8bca) station-years |
| Nutrient/chlorophyll/Kd models | [29](SOURCES.md#F-d19671c79f) | [22](SOURCES.md#F-8878751ad3) | 1990–2012 | at least [15](SOURCES.md#F-e48e67ff4f) seasonal means per model, [79](SOURCES.md#F-598345fdb6) models |
| Oxygen indicator | — | per water body | rolling [6](SOURCES.md#F-e59dfab87e)-year | **one value per water body per [6](SOURCES.md#F-72bbf95ec1) years** |

<span class="claim" data-claim="C-OB-TWO-RECORDS">The bathing record's [19,714](SOURCES.md#F-e2b98a8bca) station-years cover [70](SOURCES.md#F-6a3b63bd99) water bodies against the models' [22](SOURCES.md#F-8878751ad3), and run to 2018 rather than 2012.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-TWO-RECORDS "What this claim rests on")</sup> <span class="claim" data-claim="C-OB-ARCHIVE-LARGER">Neither is the whole of what Denmark measures in the sea: the national monitoring archive this project holds - [1,805,827](SOURCES.md#F-9fa9c3c21c) water-chemistry rows and [53,710,760](SOURCES.md#F-4df017f985) CTD rows - is larger than both. The comparison here is only about replication inside water bodies.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-ARCHIVE-LARGER "What this claim rests on")</sup>

## What this does and does not show

<span class="claim" data-claim="C-OB-CANNOT-ADJUDICATE">The bathing analysis above **cannot adjudicate the nitrogen chain**. It grades bathing quality from faecal indicator bacteria, not chlorophyll, so the finding that a water body is internally incoherent is a finding about faecal contamination and is not proof that chlorophyll behaves the same way inside one.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-CANNOT-ADJUDICATE "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-SEWAGE">The bathing record is also a direct measurement of something else: faecal contamination reaching the shore, recorded at [728](SOURCES.md#F-bffddf673d) stations in [70](SOURCES.md#F-6a3b63bd99) water bodies and through 2018 - more stations, and later years, than the nutrient models were fitted on.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-SEWAGE "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-CHL-UNTESTED">Whether a water body is a coherent unit **for chlorophyll** is not tested here. DCE fitted models only where series ran longer than [15](SOURCES.md#F-e114c12750) years, and with [29](SOURCES.md#F-d19671c79f) stations across [22](SOURCES.md#F-8878751ad3) water bodies most of those water bodies have one such station — one station cannot disagree with itself.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-CHL-UNTESTED "What this claim rests on")</sup>

<span class="claim" data-claim="C-OB-PROPOSAL">The constructive version is not "scrap the water bodies". It is that the partition is an empirical question with an empirical answer, and the data to answer it for chlorophyll would be a second long series in each water body that has one.</span><sup class="claim-mark">[†](CLAIMS.md#C-OB-PROPOSAL "What this claim rests on")</sup>

