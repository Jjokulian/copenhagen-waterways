#!/usr/bin/env python3
"""Generate docs/NITROGEN.md - what reaches the sea, and how the numbers are made.

The published figure everyone quotes is "agriculture 69.6% of nitrogen". This document
takes that apart, not by disputing the measurements but by asking three questions the
percentage cannot survive:

  * 69.6% of WHAT - what is the denominator, and is the set of sources even closed?
  * what is each number an estimator OF, as opposed to what it is labelled?
  * is nitrogen mass the right currency for oxygen depletion at all?

Everything computed here is reproducible from data/raw and data/manual. Where a bound is
our construction rather than a published figure it is marked as such.

Usage:  python3 scripts/nitrogen.py
"""
import json
import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, MANUAL, RAW, ROOT, log, read_json

MM = {"O2": 31.998, "N": 14.007, "S": 32.06, "CH4": 16.04, "Fe": 55.85}
O2_PER_N = (138 / 16) * MM["O2"] / MM["N"]      # Redfield remineralisation
O2_PER_P = (138 / 1) * MM["O2"] / 30.974
O2_NITRIF = 2 * MM["O2"] / MM["N"]              # NH4+ + 2O2 -> NO3-
O2_PER_S = 2 * MM["O2"] / MM["S"]               # H2S + 2O2 -> SO4(2-)
BOD5_ULT = 1.46

# The published apportionment, relabelled by what each number is an estimator of.
APPORTIONMENT = [
    ("Agriculture", 69.6,
     "**Residual.** (grab-sampled load over 49% of the area + model output over 51%) "
     "minus modelled point sources minus modelled natural background, with retention "
     "modelled at ±6-27 percentage points."),
    ("Natural background", 22.1,
     "Model output — and the subtrahend that determines the residual above."),
    ("Treatment plants", 4.8,
     "**Reported effluent monitoring.** Flow-metered, routinely sampled. The best-measured "
     "line in the table."),
    ("Aquaculture and marine farms", 1.5, "Reported, feed-balance based."),
    ("Separate stormwater", 0.7,
     "Modelled volume × a concentration from a **1990** measurement programme."),
    ("Rain-dependent overflow", 0.6,
     "Modelled volume (30-135% stated uncertainty) × an assumed concentration, "
     "quality-controlled **against that same assumed concentration**."),
    ("Industry", 0.5, "Reported."),
    ("Scattered dwellings", 0.2,
     "Modelled from dwelling counts × assumed per-capita loads."),
]

KOEGE = ["København", "Hvidovre", "Tårnby", "Brøndby", "Vallensbæk",
         "Ishøj", "Greve", "Solrød", "Køge", "Stevns"]
KOEGE_NORTH = {"København", "Hvidovre", "Tårnby", "Brøndby"}
KOEGE_BOX = (12.10, 55.28, 12.80, 55.66)


def fmt(n, dp=0):
    return f"{n:,.{dp}f}" if isinstance(n, (int, float)) else str(n)


def koege_tables():
    """Who can actually discharge into Køge Bugt, from the national register."""
    codes = read_json(os.path.join(MANUAL, "codelists.json"))["bygvaerkstype"]
    path = os.path.join(RAW, "national", "punkt_rbu_udl.geojson")
    if not os.path.exists(path):
        return None
    st = defaultdict(lambda: {"sep": 0, "comb": 0, "basin": 0, "vol": 0.0})
    for f in read_json(path)["features"]:
        p, c = f["properties"], f["geometry"]["coordinates"]
        k, t = p.get("komm_navn"), p.get("bgv_type")
        if k not in KOEGE:
            continue
        if not (KOEGE_BOX[0] <= c[0] <= KOEGE_BOX[2] and KOEGE_BOX[1] <= c[1] <= KOEGE_BOX[3]):
            continue
        if codes.get(t, {}).get("combined_sewer"):
            st[k]["comb"] += 1
            st[k]["vol"] += p.get("vol_sb") or 0
            if t != "OV":
                st[k]["basin"] += 1
        elif t in ("SE", "SF"):
            st[k]["sep"] += 1

    plants = []
    rp = os.path.join(RAW, "national", "punkt_rens_udl.geojson")
    if os.path.exists(rp):
        for f in read_json(rp)["features"]:
            p, c = f["properties"], f["geometry"]["coordinates"]
            if (p.get("komm_navn") in KOEGE and (p.get("godk_pe") or 0) >= 10000
                    and KOEGE_BOX[0] <= c[0] <= KOEGE_BOX[2]
                    and KOEGE_BOX[1] <= c[1] <= KOEGE_BOX[3]):
                plants.append((p.get("pkt_navn"), p.get("godk_pe"), p.get("komm_navn")))
    plants.sort(key=lambda x: -x[1])
    return st, plants


# Three passages that are read rather than computed: the audit of what field surplus
# is made of, the two subtractions behind the ~70%, and the transport analysis for
# Køge Bugt. They live here rather than in the markdown because they were once written
# straight into docs/NITROGEN.md, and running this script deleted all three - which is
# what a generator does to anything it does not know about.

SURPLUS_AUDIT = """### The model's deciding input is itself a residual, and the field is never measured

DCE's DK-QNP model computes the diffuse nitrogen load over the ungauged part of the
country. Its own methods chapter names the key input:

> *"En vigtig modelvariabel i DK-QNP modellen til beregning af tilførsel af total
> diffus kvælstof er det årligt beregnede kvælstofoverskud på 'mark-niveau'."*
> — Thodsen et al. 2019, [DCE SR353](https://dce2.au.dk/pub/SR353.pdf), p.34

The **field surplus** (*markoverskud*). And chapter 6 of the same report presents this
as a result:

> *"Der er således — for perioden som helhed — en meget stærk, signifikant lineær
> relation mellem det nationale markoverskud og den samlede, normaliserede
> kvælstoftransport fra diffuse kilder (Figur 6.7, D)."*

**A variable that is an input to the model is correlated with the model's output, and
the correlation is reported as a finding.** This does not make the attribution wrong.
It makes Figur 6.7 D unable to evidence it.

#### And that is a much narrower claim than it first looks

We checked one figure in one report and stopped. Two things found afterwards, both
of which cut against the simple reading:

**DCE qualify the figure themselves, on the very next page.** Immediately after
presenting the relation, SR353 says that not all fjord catchments respond equally
quickly — Mariager Fjord and parts of Limfjorden reduced their diffuse load *less* than
*"relationen vist i Figur 6.7 D indikerer"*, citing Windolf et al. 2012b and 2012c.
They are pointing at the figure's limits, not resting on it.

**We have now read it, and it refutes the broader reading.** Windolf,
Blicher-Mathiesen, Carstensen & Kronvang (2012), *Environmental Science and Policy*
24: 24–33, [10.1016/j.envsci.2012.08.009](https://doi.org/10.1016/j.envsci.2012.08.009).

The design is a **catchment↔estuary pairing** — 10 catchments covering 35% of Danish
land area with their estuaries, 1990–2009 — not the treated-versus-control paired
catchment experiment. On that, an earlier draft of this section guessed right and then
guessed wrong about what followed.

What matters is where the numbers come from:

| link | how it is obtained |
|---|---|
| catchment N surplus | the norm-product residual, as above |
| **stream N load** | **measured** on the gauged fraction — fortnightly total-N concentrations × daily discharge — and **modelled** on the rest per Windolf et al. (2011), the DK-QNP family |
| **estuary total N** | **measured.** Discrete samples, surface and bottom, 12–46×/year, upper/middle/lower reaches |

Gauged area runs from **22% (Isefjord) to 87% (Randers Fjord)**, median about 66%. So
the surplus↔load relation *is* partly circular, and unevenly so — at Isefjord more than
three quarters of the catchment is modelled, at Randers about an eighth.

**But two things in this paper are not circular at all**, and together they carry the
attribution:

1. **Estuary nitrogen is measured, and fell 24–62%.** It sits downstream of the load
   model and takes no input from *markoverskud*. Stream and upper-estuary concentrations
   *"nearly halved over the time frame investigated."*
2. **The catchments respond differently, and that is the tell.** Eight show a direct
   response under five years; two show a **decadal** delay attributed to nitrate
   surviving in oxic chalk aquifers. A relation manufactured by a shared input would
   give all ten the same response. The heterogeneity is a signature of real hydrology,
   and a construction does not produce it.

**So the position changes.** The narrow claim stands: Figur 6.7 D in SR353 cannot
evidence what it is used for, and this paper does not rescue that figure. The broad
claim — that the attribution lacks independent support — is now **positively refuted**,
not merely unestablished. Measured stream loads over a gauged majority, measured
estuary concentrations, and between-catchment heterogeneity are support that no
circularity in one monitoring-report figure touches.

Separately, Bøgestrand et al. (2009) evaluated DK-QNP and found a regional bias —
overestimating in western Denmark, underestimating in the east — which SR353 corrects
for. So model *evaluation* exists. Whether model *validation against held-out gauged
catchments* exists is what nobody here has established.

**So the established claim is narrow:** *one figure, in one monitoring report, is
structurally unable to support the inference it is used for.* The claim **not**
established is that the attribution lacks evidence. Testing that would mean reading
Windolf 2010/2011/2012a–c and Bøgestrand 2009 and asking whether DK-QNP is validated
against gauged catchments held out of its fitting — which is the honest next step and
is not done.

This is worth stating plainly because it is the error this project audits, committed
here twice in one hour, in both directions. First we found one bad argument and let it
stand for the case — a bad argument in a source does not mean there are no good ones.
Then, correcting that, we asserted from a *title* that a non-circular design existed.
**Softening an overclaim is still an overclaim.**

Reading the paper settled it, and against us. That is the steelman rule working as
intended: the strongest version of the case was looked for, found, and turned out to be
stronger than the finding. **The circularity is real and local. The attribution is not
unevidenced.** Both sentences are needed, and only the first was in the first draft.

#### What "field surplus" is, in facts and observations

It is an accounting identity, not a measurement. From
[DCE SR120](https://dce2.au.dk/pub/SR120.pdf) Table 3.4, kg N/ha, whole country:

| | 1991 | 2005 | 2013 |
|---|---|---|---|
| mineral fertiliser | 141 | 71 | 74 |
| manure + sludge | 91 | 84 | 87 |
| biological fixation | 16 | 15 | 16 |
| seed | 2 | 2 | 2 |
| atmospheric deposition | 22 | 16 | 13 |
| **total supplied** | **272** | **189** | **192** |
| harvested nitrogen | 124 | 106 | 110 |
| **= field surplus** | **148** | **87** | **84** |

And SR120's Bilag 3 says what each term is made of:

- **mineral fertiliser** — national sales statistics, **minus an estimated 5,000 t N**
  assumed to go to public grounds, forests and private gardens. A stated constant.
- **manure** — livestock **counts** by category, times a nutrient content per category
  that follows *"de til enhver tid gældende normer"* — **the norms in force at the
  time**, set by regulation.
- **yields** — the harvest census, with roughage known to be overestimated, so an
  assumed **10% shrinkage** for maize, grass and catch crops and **15%** for permanent
  grass.
- **crop nitrogen content** — **norm tables** from the *Fodermiddeltabeller* of 1992,
  1995 and 2000, with cereals corrected annually from analyses by the pig industry's
  own research centre.
- **atmospheric deposition** — modelled.

**No field is observed at any point.** Every term is a register count or an area times
a regulatory coefficient, and the surplus is what is left over. Nitrogen never touches
an instrument.

#### The consequence is documented in the sources themselves

Because the coefficients are administrative, the number moves when they move, with no
change in any field.

- **1999**: the nitrogen norm was cut 10%, dropping the quota by ~40,000 t N, while
  grass norms changed simultaneously, raising it ~15,000 t N. SR120 calls the result a
  *"spring"* — a step — in the compiled series.
- **2012**: the method for nutrients removed at harvest changed from dry-matter yield
  to feed units, and SR120 records that the net-input figures *"er steget lidt ift. de
  tidligere opgørelser"* — rose, from the method change.
- **2013**: the same year is published **twice**, differing only in which register the
  fertiliser figure came from — **84 kg N/ha** from the *gødningsregnskaber*, **81**
  from Danmarks Statistik.

That last one sets the scale. The surplus fell 148 → 84 kg N/ha over 22 years, about
−2.9 kg/ha/yr. **Choosing which register to read is worth roughly one year of the
trend.** Small against the whole decline; not small against a year of it, and it is
never carried as an uncertainty.

New Zealand's OVERSEER is the same pattern with an audit attached: successive versions
raised modelled nitrogen leaching by up to 60% with no change in on-farm practice, and
a 2021 review panel would not say whether the tool could tell a rise from a fall.

**So the chain reads:** norm tables × register counts → *markoverskud*, a residual →
input to DK-QNP → diffuse load over the ungauged area → summed into total diffuse
transport → correlated with *markoverskud* → "a very strong, significant linear
relation". Each step is defensible alone. The composite cannot evidence what the last
step is used to evidence.
"""

TWO_SUBTRACTIONS = """## 2b. Two subtractions, and the ~70% is not the one people think

It is easy — this document did it — to run together the **field balance** and the
**load apportionment**. They are different operations on different quantities, and the
headline share is the second, not the first.

| | **A — field surplus (*markoverskud*)** | **B — the ~70% share** |
|---|---|---|
| what it subtracts | harvest from inputs | point sources and background from river transport |
| units | kg N/ha | t N/yr, reported as a share |
| kind | **norm product** — counts × regulatory coefficients | **residual** — what is left after naming what could be named |
| fails when | a norm changes with no change in any field | an unnamed source exists |

They are coupled, which is why they get confused: **A is an input to DK-QNP, and DK-QNP
supplies B's river-transport term over the ungauged ~45–51% of the country.** So A
partly determines the minuend of B. But the ~70% itself is B.

### B, from its own methods note

The construction, in DCE's own words
([MSFD notat 2-8](https://dce.au.dk/fileadmin/dce.au.dk/Udgivelser/Havstrateginotater/2-8_MSFD_notat_tilfoersel_NPO.pdf)):

> *"Diffuse tilførsler (inkl. spredt bebyggelse) **minus** baggrundsbidraget (diffus
> antropogen)"*

with the two subtracted terms defined there as:

- **Natural background** — *"et mål for den diffuse tilførsel der vil komme fra
  oplandet, hvis der ikke var menneskelig aktivitet, og som **bestemmes i mindre oplande
  med lav antropogen påvirkning**."* Measured in *other* catchments and transferred in.
- **Diffuse load** — *"belastning fra dyrkede arealer **inkl. spredt bebyggelse, da
  tilførsler fra spredt bebyggelse ofte er svær at adskille fra øvrige diffuse
  kilder**."*

Three things follow, all from the document rather than from us:

1. **The category is defined as unseparated.** Scattered dwellings sit inside the
   agricultural term *because they could not be separated from it*. That is stated in
   the definition.
2. **The subtrahend is a transferred measurement.** Background is not measured in the
   catchment it is subtracted from. Small low-impact catchments stand in for the rest —
   a basket assumption at the centre of the arithmetic. (Windolf et al. 2012 gives that
   assumption its one strong check: the intercept of their measured regressions implies
   1.24 ± 0.46 mg N/L, against 1.27 ± 0.55 measured in nine minimally-disturbed streams.
   That agreement is real and is the best evidence the background term is not arbitrary.)
3. **The split is not annual.** *"For de enkelte år opdeles den diffuse belastning ikke
   i den naturlige baggrundsbelastning... men det for 5 års gennemsnit er lavet en
   opdeling."* The background/anthropogenic division is made **only on five-year
   averages**, because the split is too uncertain year by year. **So an annual
   agricultural share is not a thing this method produces**, and any year-on-year
   movement in a published share is an artefact of interpolating a quinquennial split.

### So how does the construction perform against things that were measured?

This is the question the rest of it turns on, and Windolf et al. (2012) answer it
per catchment. Over 1990–2009:

| catchment | field surplus fell | **measured** normalised diffuse load fell | pass-through |
|---|---|---|---|
| Horsens, Isefjord, Odense | 30–52 kg N ha⁻¹ yr⁻¹ | **10–14** | roughly ¼ to ⅓ |
| Randers, Roskilde | 24–50 | **3–5** | roughly a tenth |
| **Mariager** | fell as elsewhere | **no response traceable** | **zero** |

**The construction moves and the measurement mostly does not.** For every kilogram per
hectare the surplus fell, the measured diffuse load fell by something like 0.1 to 0.4
where it responded at all, and by nothing in one catchment of ten. The paper attributes
the spread to nitrogen removal in groundwater varying with geology, and the Mariager
failure to old oxic aquifers where nitrate survives.

Read carefully, that is three separate findings:

1. **Direction: good.** Nine of ten catchments show a significant relation. The surplus
   is not noise.
2. **Magnitude: poor.** The transfer coefficient ranges from 0 to about a third. A load
   reduction predicted from a surplus reduction would be **overestimated by a factor of
   three to ten**, or entirely, depending which catchment you are standing in.
3. **And the national figure hides exactly this.** Figur 6.7 D shows *"en meget stærk,
   signifikant lineær relation"* at national scale. That relation is an aggregate over
   catchments whose individual pass-through runs from zero to a third. **The strength of
   the national fit is not evidence that the local coefficient is stable — it is what
   aggregation does to a variable coefficient.**

Point 3 is this project's recurring finding arriving in the nitrogen account: a basket
looks tight from outside and is heterogeneous within, and the tightness is partly an
artefact of looking from outside. It is the same shape as the water bodies that carry no
within-basket signal, and the same shape as a national trend that tracks which stations
were reporting.

**None of which says the decline was not real.** Measured estuary nitrogen fell 24–62%
and measured inlet concentrations 18–55%. Something large happened. What the numbers do
not support is using the surplus as a quantitative instrument — sizing an intervention
on it, or converting a surplus target into an expected load.

### Which sharpens what the residual absorbs

Section 1 lists **10 of 20 pathways carrying no number at all**. Every one of them that
reaches a river — submarine groundwater discharge, drained organic soils, legacy
nitrogen in transit, foreign inflow to shared waters — lands inside B's leftover, and is
named agriculture by subtraction. That is the substantive weakness of the ~70%, and it
is separate from, and larger than, the circularity in §2.
"""

KOEGE_TRANSPORT = """### But "downstream" is a claim about water, and it has been tested

An earlier version of this section said the whole shoreline is downstream of the northern discharge. That was inferred from the shape of the bay, and this project has a transport analysis that both supports and qualifies it — which the section never cited. [CURRENTS.md](CURRENTS.md), on 35,064 hours where the rain record and the current record overlap:

| | southward transport in the southern Sound |
|---|---|
| baseline, all hours | **42%** |
| during overflow-scale rain (134 h) | **23.9%** — 18 points *below* baseline |
| +6 h after the event | 44.1% |
| **+12 h after the event** | **59.3%** — 17 points *above* |

So the geometry is right about the plume and wrong about the event. **While the city is overflowing, the water runs north** — heavy Copenhagen rain arrives with cyclonic southwesterlies that drive the Sound northward. Southward transport only exceeds baseline about twelve hours later, by which time the plume is diluted and no longer traceable to an outfall. And [CURRENTS.md](CURRENTS.md) separately finds that **Køge Bugt does not flush**, so what does arrive stays.

That matters for what this whole section can claim. A load entering a bay that does not flush is a different quantity from a load entering one that does — and the timing means an event-based attribution (this overflow, that shoreline) is not supported, while an accumulated one may be.

The same bay carries the largest release nobody argued about. [OPEN_PROBLEMS.md](OPEN_PROBLEMS.md) sets the Øresund fixed link's permitted spill — **up to 370,000 m³** of fines into the water column at the bay's northern entrance, 1995–2000 — against the **498 m³** actually released at Lynetteholm before dumping was stopped. Roughly **seven hundred times**, and the larger one was a permit condition met rather than a controversy. Where that material went has never been computed: the current field used above covers 2022–2026 only, and is about twice too slow in the straits by its own calibration.
"""




def manure_check(M):
    """The prediction in 2c, checked against two open registers instead of waited on."""
    o = []
    w = o.append
    lim = M["over_limit"]
    w("### The prediction is checkable, and the check has been run\n")
    w("*A quota transfers the constraint to the manure only when a holding's own land "
      "cannot take what its animals produce.* That is not something to wait for: both "
      "halves are in open registers and they join on the company number. The "
      "livestock register carries **animal units** — `DE`, the unit the manure "
      "regulation itself uses — against the business that runs each site; the "
      "field-parcel register carries the same business's declared hectares. "
      "`scripts/manure.py` fetches both and divides.\n")
    w(f"| | |\n|---|---:|")
    w(f"| Livestock sites | {M['sites']:,} |")
    w(f"| Businesses keeping animals | {M['cvrs_with_animals']:,} |")
    w(f"| …of which also declare land | **{M['cvrs_with_both']:,}** |")
    w(f"| Animal units, national | {M['animal_units_total']:,.0f} |")
    w(f"| …on businesses that declare land | {M['animal_units_on_matched']:,.0f} "
      f"({M['animal_units_on_matched']/M['animal_units_total']*100:.0f}%) |")
    w(f"| Median animal units per declared hectare | "
      f"{M['percentiles_de_per_ha']['50']:.2f} |")
    w(f"| 90th percentile | {M['percentiles_de_per_ha']['90']:.2f} |")
    w(f"| 99th percentile | {M['percentiles_de_per_ha']['99']:.1f} |")
    w("")
    a14, a17 = lim["1.4"], lim["1.7"]
    w(f"**Above the classic harmony limit of 1.4 animal units per hectare sit "
      f"{a14['businesses']:,} businesses — {a14['share_of_businesses_pct']:.0f}% of "
      f"those with land — and they hold "
      f"{a14['share_of_herd_pct']:.0f}% of the national herd.** At 1.7 it is "
      f"{a17['businesses']:,} businesses and {a17['share_of_herd_pct']:.0f}% of the "
      "herd. Read that plainly: **roughly half the animals in Denmark are on farms "
      "whose own declared land cannot take their own manure.** The export the law "
      "would force is not a future consequence of a quota. It is the arrangement "
      "already in place, held together by inter-farm contracts — and those contracts "
      "are the one part of it that is not public.\n")
    w("*What this does not establish.* Declared area is land declared for area "
      "support, which is not the same as every hectare a business may spread on: "
      "rented-in land can be missing, and a business that buys spreading capacity "
      "from a neighbour looks land-poor here and is compliant in law. "
      f"{100 - M['cvrs_with_both']/M['cvrs_with_animals']*100:.0f}% of "
      "animal-keeping businesses declare no land at all in this join, which is "
      "either genuine landlessness or a failed match through holding companies. And "
      "the thresholds are the pre-2017 harmony units: Denmark now regulates in "
      "kilograms of nitrogen per hectare, so these indicate the pressure rather than "
      "test compliance.\n")
    w("*Provenance.* Both layers are open and need no key. They were located and "
      "documented by the sibling project "
      "[danish-livestock](https://github.com/Jjokulian), which mapped all 57,860 "
      "sites; this project fetches them from the same primary source rather than "
      "copying its data, and the two traps it found — an encoding the server lies "
      "about, and herd-size columns that do not partition — are handled in "
      "`scripts/manure.py` because of that documentation.\n")
    return "\n".join(o)


def whose_nitrogen(cl):
    """Section 2c: the question the load apportionment cannot answer, and the two
    halves of the input side that can be counted instead."""
    y = cl["years"]
    last = y["2025"]
    o = []
    w = o.append
    w("## 2c. Whose nitrogen is it, and can the ledger say?\n")
    w("A question that gets asked constantly and has no answer downstream: **how much "
      "of this is because Denmark keeps animals?** The apportionment above has no "
      "livestock term. Diffuse load is one bucket — cultivated land *including "
      "scattered dwellings*, by DCE's own definition — and no measurement in a stream "
      "could separate the fractions anyway. A nitrate ion that passed through a pig "
      "is the same ion as one out of a bag. **The question cannot be answered by "
      "measuring, only by accounting**, and the accounting has two halves.\n")
    w("**Half one: what is applied.** From the field balance above — manure and "
      "sludge **87 kg N/ha** against mineral fertiliser **74** in 2013, out of 192 "
      "supplied. Manure has been the larger of the two since about 2000; in 1991 it "
      "was mineral 141 against manure 91. So a little under half of the nitrogen put "
      "on Danish fields arrives as manure, and that half is not optional in the way "
      "a bag is: it exists because the animals do, and it has to be spread, exported "
      "or processed.\n")
    w("**Half two: what the rest is spread on.** Mineral fertiliser on a barley field "
      "grown for pigs is nitrogen spent on livestock as surely as the slurry beside "
      "it. Danish crop statistics record what was grown rather than what it was fed "
      "to, so this is a range on a stated rule rather than a number "
      "(`scripts/cropland.py`, from Statistics Denmark table AFG6):\n")
    w("| | 1990 | 2000 | 2010 | 2025 |")
    w("|---|---:|---:|---:|---:|")
    for label, key in [
        ("Grass, whole-crop and fodder roots — **unambiguously feed**", "floor_pct"),
        ("…plus cereals and pulses to maturity", "central_pct"),
        ("…plus rapeseed, whose meal is feed", "ceiling_pct"),
        ("**Potatoes, sugar beet, horticulture — food people eat**", "direct_food_pct"),
    ]:
        w("| " + label + " | " + " | ".join(
            f"{y[k][key]:.1f}%" for k in ("1990", "2000", "2010", "2025")) + " |")
    w("")
    w(f"**Between two thirds and three quarters of Danish farmland grows feed, and "
      f"under five per cent of it grows food that people eat directly** — "
      f"{last['direct_food_pct']:.1f}% in 2025, against "
      f"{y['1990']['direct_food_pct']:.1f}% in 1990. The shares have barely moved in "
      "thirty-five years. Set that beside half one and the input-side answer is not "
      "close: **the herd is behind most of the nitrogen applied to Danish soil — the "
      "manure directly, and the majority of the mineral fertiliser through what it "
      "is spread on.**\n")
    w("*What this does not establish.* An input share is not a load share. This "
      "project's own comparison of *markoverskud* against measured load puts "
      "pass-through between **zero and about a third**, varying by catchment, so a "
      "share of what is applied cannot be converted into a share of what arrives. "
      "And the classification above is ours: the statistics do not record what a "
      "crop was fed to, cereals are the load-bearing assumption, and a reader who "
      "thinks Danish grain is mostly milled rather than fed should use the "
      f"{last['floor_pct']:.1f}% floor instead.\n")
    w("### Which is why biogas is a carbon technology and not a nitrogen one\n")
    w("The obvious hope is that digestion deals with it. It does not. **Anaerobic "
      "digestion removes carbon, not nitrogen**: methane and CO₂ leave, and "
      "essentially all the nitrogen stays in the digestate — with *more* of it as "
      "ammonium than before, because digestion mineralises organic N. That is useful "
      "as fertiliser value and it is the opposite of removal. **The field is still "
      "the endpoint.**\n")
    w("What a biogas plant does supply is the thing the manure never otherwise has: "
      "**a collection point**. The manure is already gathered, homogenised and "
      "pumped, which is where nitrogen can be taken out — and there are only three "
      "kinds of exit:\n")
    for h, t in [
        ("Capture it as a product.",
         "Separate the digestate into fibre and liquid, then strip ammonia from the "
         "liquid into an ammonium salt — a concentrated, transportable fertiliser "
         "that can leave the catchment or displace Haber-Bosch nitrogen. The "
         "nitrogen is not destroyed; it is made portable, which is what the field "
         "balance needs."),
        ("Destroy it, which is literally a reduction.",
         "Nitrify then **denitrify** the liquid fraction and the nitrogen leaves as "
         "N₂ — inert, and out of the reactive pool for good. This is the only true "
         "removal available, and it is the same reaction a constructed wetland "
         "performs slowly and for free. It costs energy, and a badly run plant "
         "emits N₂O instead, which trades a water problem for a climate one."),
        ("Burn the fibre.",
         "Destroys organic nitrogen and recovers phosphorus in ash, at the cost of "
         "flue-gas treatment. It is the P route more than the N route."),
    ]:
        w(f"- **{h}** {t}")
    w("")
    mp = os.path.join(DERIVED, "manure.json")
    if os.path.exists(mp):
        w(manure_check(read_json(mp)))
    w("### What the law does to the herd, if the arithmetic binds\n")
    w("The instruments are in the public record rather than in this analysis: L5 "
      "passed 119–34 on 3 September 2026 and puts **per-catchment nitrogen quotas on "
      "individual holdings from 2027**, with *frivillig arealomlægning* — voluntary "
      "land conversion — as the Tripartite's main engine and the quota model "
      "described by its own architects as the safety net under it "
      "([POLITICS.md](POLITICS.md)). **This project has not read the statute**, so "
      "what follows is inference from those instruments and from the balance above, "
      "and it is offered as a prediction that can be checked rather than as a "
      "reading of the law.\n")
    w("**A quota bites on mineral fertiliser first, because manure is not optional.** "
      "The bag is the free variable: a holding that must apply less nitrogen buys "
      "less of it. The slurry is already there, produced daily by animals that exist, "
      "and it has to be spread, stored, sold or processed. So the first years of a "
      "tightening quota look like a fertiliser reduction and leave the herd "
      "untouched.\n")
    w("**The constraint transfers when the quota falls below what the manure alone "
      "supplies.** At that point the arithmetic offers exactly four moves: fewer "
      "animals, more hectares to spread on, more nitrogen leaving in the crop, or "
      "**the manure nitrogen leaving the holding**. And this is where the design of "
      "the Tripartite matters more than its rhetoric: its main engine takes land "
      "*out* — wetland conversion, afforestation, set-aside — which raises manure "
      "nitrogen per remaining hectare with no change in any herd. **An area policy "
      "becomes a livestock policy without ever naming livestock.**\n")
    w("So yes: a byproduct that has to leave is the predictable consequence, and the "
      "market for it already half exists — inter-farm slurry contracts, separation "
      "plants, and the stripping route above, whose output is a concentrated "
      "ammonium salt that travels. **A quota is a demand curve for nitrogen "
      "capture**, in the same way the liability settlements are a demand curve for "
      "destruction ([PROGRAMME.md](PROGRAMME.md)) — regulation creating an industry "
      "rather than only a cost.\n")
    w("Three things have to be said with it, because each of them can make the "
      "prediction wrong:\n")
    for h, t in [
        ("The quota is per catchment, so the export has to cross a catchment line.",
         "Moving slurry from one farm to its neighbour changes whose paperwork it is "
         "and not what the receiving water gets. Only nitrogen that leaves the "
         "catchment — or leaves the reactive pool altogether — is a reduction where "
         "it is being counted."),
        ("The pressure is capped by design.",
         "The agreement fixes a *braklægningspunkt*, a maximum regulatory pressure, "
         "which is exactly the point at which the squeeze on land would start "
         "forcing the herd. Where that point is set decides whether any of the above "
         "ever happens."),
        ("And the load may not follow the input.",
         "This document's own comparison puts pass-through from field surplus to "
         "measured load between zero and about a third, varying by catchment and "
         "zero at Mariager. A herd reduction is an input reduction, and an input "
         "reduction is not yet a load reduction — which is the same objection this "
         "project makes to the standard account, applied to a measure it would "
         "otherwise be tempted to endorse."),
    ]:
        w(f"- **{h}** {t}")
    w("")
    w("So the answer to *can biogas fix it* is: not by itself, and yes as "
      "infrastructure. **Digestion without a nitrogen step returns every kilogram to "
      "the same fields in a more available form.** With separation and stripping, or "
      "with denitrification, the same plant becomes the only place in the chain "
      "where the nitrogen can be made to go somewhere else — which is the honest "
      "version of the claim that the herd sets a floor: it sets one **unless the "
      "manure nitrogen is given an exit that is not a field.**\n")
    return "\n".join(o)


def main():
    paths = read_json(os.path.join(MANUAL, "nitrogen_pathways.json"))["pathways"]
    mon = read_json(os.path.join(MANUAL, "monitoring.json"))
    o = []
    w = o.append

    w("# What the sea actually receives\n")
    w("Generated by `scripts/nitrogen.py`. Reproducible from `data/raw` and `data/manual`.\n")
    w("The figure in circulation is that agriculture accounts for **69.6% of nitrogen**. "
      "This document does not dispute the measurements behind it. It asks three questions "
      "the percentage does not survive.\n")

    # ---------------------------------------------------------------- 1. denominator
    w("## 1. There is no denominator\n")
    w("A percentage requires a closed set. Here is every pathway of reactive nitrogen to "
      "Danish marine waters we could enumerate.\n")
    w("| Pathway | kt N/yr | Basis |")
    w("|---|---:|---|")
    lo = hi = 0.0
    unq = 0
    for p in paths:
        if p["lo"] is None:
            unq += 1
            val = "**—**"
        else:
            lo += p["lo"]
            hi += p["hi"]
            val = f"{p['lo']:g} – {p['hi']:g}"
        note = (p.get("note") or "").replace("\n", " ").strip()
        name = f"**{p['pathway']}**" if p["lo"] is None else p["pathway"]
        w(f"| {name} | {val} | {p['status'].lower()} — {note} |")
    w("")
    w(f"**{unq} of {len(paths)} pathways carry no number at all**, including what is "
      "probably the largest supply to the productive layer — internal regeneration from "
      "sediment, which is not a \"source\" and so has no row in any apportionment.\n")
    w(f"The quantified subset sums to **{lo:.0f} – {hi:.0f} kt N/yr**. That is not a range "
      "for the total. With ten pathways empty the honest statement is:\n")
    w(f"> Total reactive nitrogen supply **≥ {lo:.0f} kt N/yr**, with no established upper bound.\n")
    w("A lower bound, not a range. And therefore no denominator, and no percentages — "
      "until the empty rows are filled.\n")
    w("Note the scale of what the apportionment omits. Atmospheric deposition to Danish "
      "marine waters is 45–90 kt N/yr, comparable to the entire land-based waterborne "
      "term, and appears in none of the published shares.\n")

    # ---------------------------------------------------- 2. estimator vs estimand
    w("## 2. The numbers are not estimators of what they are named\n")
    w("Each line of the published apportionment, relabelled by what actually produced it:\n")
    w("| Called | Actually is |")
    w("|---|---|")
    for name, pct, what in APPORTIONMENT:
        w(f"| **{name}, {pct}%** | {what} |")
    w("")
    w("Two of these are measurements. The rest are models, and the largest is a residual "
      "of models.\n")
    ql = mon["quality_control"]
    w("### The validation is circular\n")
    w(f"Reported nitrogen divided by reported volume must fall within "
      f"**{ql['acceptance_interval_combined_mg_per_l'][0]}–"
      f"{ql['acceptance_interval_combined_mg_per_l'][1]} mg/l** for combined sewers and "
      f"**{ql['acceptance_interval_separate_mg_per_l'][0]}–"
      f"{ql['acceptance_interval_separate_mg_per_l'][1]} mg/l** for separate ones. Outside "
      "that, *\"kontaktes den dataansvarlige med henblik på at få rettet eventuelle fejl\"* "
      "— the data owner is contacted to correct the error.\n")
    w(f"{ql['consequence']} **The assumed concentration cannot be falsified by data "
      "collected under it.**\n")
    w(SURPLUS_AUDIT)
    w("### And the estimator can return impossible values\n")
    dl = mon["diffuse_load"]
    w(f"{dl['estimator_pathology']} A residual whose error can exceed its own signal is "
      "published to one decimal place with no error bar.\n")
    w(f"Underneath it: **{dl['stream_stations']} stream stations** covering "
      f"**{dl['area_measured_pct']}%** of the country, the other "
      f"**{dl['area_modelled_pct']}%** modelled. Load is grab samples plus linear "
      "interpolation, and in all three streams of the 2018 validation study that method "
      f"**always underestimated** — annual deviations {dl['deviation_annual_pct'][0]}% to "
      f"{dl['deviation_annual_pct'][1]}%, monthly deviations reaching "
      f"{dl['deviation_monthly_pct'][1]:+.0f}%. Retention, the largest single term, carries "
      f"**±{dl['retention_uncertainty_pct_points'][0]}–"
      f"{dl['retention_uncertainty_pct_points'][1]} percentage points**.\n")
    ov = mon["overflow_reporting"]
    w("### Overflow is modelled, and the deciding variable is not collected\n")
    w("| Knowledge level | Method | Stated uncertainty |")
    w("|---|---|---:|")
    for lv in ov["knowledge_levels"]:
        u = f"{lv['uncertainty_pct']}%" if lv["uncertainty_pct"] else "—"
        w(f"| {lv['level']} | {lv['method']} | {u} |")
    w("")
    w(f"{ov['note_on_flow']}\n")
    w("That matters because sediment resuspension is a **threshold** in flow, not a "
      "frequency of events. Below the critical shear stress the deposit stays in the basin; "
      "above it, the accumulated sludge leaves — and the hazardous-substances programme "
      "reports the highest median metal concentrations precisely in basin sludge. Multiplying "
      "an annual volume by an average concentration cannot represent that, and the resulting "
      "error is one-directional and largest in the wettest years.\n")
    w(TWO_SUBTRACTIONS)
    cl_path = os.path.join(DERIVED, "cropland.json")
    if os.path.exists(cl_path):
        w(whose_nitrogen(read_json(cl_path)))

    # --------------------------------------------------------- 3. wrong currency
    w("## 3. Nitrogen mass is the wrong currency\n")
    w("Oxygen depletion is the damage. Nitrogen is one route to it. Converting everything "
      "to oxygen demand — Redfield stoichiometry, which is chemistry rather than judgement:\n")
    w("| Pathway | Oxygen demand |")
    w("|---|---:|")
    w(f"| Remineralisation of algal biomass | **{O2_PER_N:.2f} g O₂ per g N** |")
    w(f"| Remineralisation, via phosphorus | {O2_PER_P:.1f} g O₂ per g P |")
    w(f"| **Nitrification of delivered ammonium** | **{O2_NITRIF:.2f} g O₂ per g N** |")
    w(f"| **Sulphide oxidation** | **{O2_PER_S:.2f} g O₂ per g S** |")
    w(f"| Methane oxidation | {2*MM['O2']/MM['CH4']:.2f} g O₂ per g CH₄ |")
    w(f"| Direct BOD | {BOD5_ULT:.2f} g O₂ per g BOD₅ |")
    w("")
    w("Only the first line is modelled by the accounts. Three consequences:\n")
    w("**Ammonium carries its own demand.** An ammonium-rich discharge — which is what a "
      f"basin that has gone anaerobic produces — consumes {O2_NITRIF:.2f} g O₂ per g N on "
      "arrival, with no algae, no light and no delay. That pathway is absent from a "
      "nitrogen→algae→decay model entirely.\n")
    so4, o2sat = 2700.0, 8.0
    s_mgl = so4 * MM["S"] / (MM["S"] + 4 * 15.999)
    demand = s_mgl * O2_PER_S
    w(f"**Sulphate makes the debt effectively unbounded.** Seawater holds ~{so4:.0f} mg/l "
      f"sulphate = {s_mgl:.0f} mg/l as sulphur, against ~{o2sat:.0f} mg/l dissolved oxygen. "
      f"Fully reduced and later re-oxidised that is {demand:.0f} mg/l of demand — "
      f"**{demand/o2sat:.0f}× the oxygen in the water**. Reducing just "
      f"{o2sat/demand*100:.2f}% of the sulphate pool stores a debt equal to all of it. Once "
      "a basin goes anoxic the electron acceptor is effectively infinite, and every storm "
      "that mixes oxygen in spends it re-oxidising sulphide instead of restoring the water.\n")
    w("**And the ratio matters, not just the total.** Diatoms need silicon roughly 1:1 with "
      "nitrogen. Fertiliser and sewage add N and P; neither adds silicon, which comes from "
      "rock weathering. Enrichment therefore raises N:Si, and when silicon runs out the "
      "community shifts from diatoms to flagellates and dinoflagellates. A composition "
      "change driven by a ratio, invisible to any nitrogen total.\n")
    w("There is no potency term anywhere in the accounting. A kilogram delivered in "
      "February into a mixed column counts identically to a kilogram delivered in July into "
      "a stratified fjord — though vertical mixing across a summer pycnocline is roughly "
      "four orders of magnitude weaker, which is what decides whether the nitrogen is used "
      "or flushed.\n")

    # ------------------------------------------------------------- 4. blind spots
    w("## 4. What is not measured\n")
    w("| What | Window | Consequence |")
    w("|---|---|---|")
    for k, v in mon["monitoring_windows"].items():
        flag = " **(circular)**" if v.get("seasonal_claim_circular") else ""
        w(f"| {k.replace('_', ' ')} | {v['period']} | set by {v['window_set_by']}{flag} |")
    w("")
    w("The most consequential row is the second. **Soft-bottom fauna is sampled 1 March to "
      "31 May** — after the winter, before the summer. The annual die-off is observed only "
      "in its aftermath, months later, once recolonisation has begun. So the event that "
      "decides which organisms are present to receive the next year's nitrogen is the one "
      "thing nobody watches.\n")
    w("And any seasonal claim drawn from a seasonally-sampled record is circular unless the "
      "window was set by mechanism. Iltsvind's July–November window was; bathing water's "
      "June–September window was not.\n")
    mfs = mon["hazardous_substances"]
    w("### Toxicants: eleven stations\n")
    w(f"The national typetal for hazardous substances in rain-dependent discharges — applied "
      f"to all **{mfs['applied_to_discharge_points_nationally']:,}** discharge points — rest "
      f"on **{mfs['stations_combined_overflow']} combined-sewer overflows and "
      f"{mfs['stations_separate_stormwater']} separate stormwater outlets**, monitored "
      "2000–2020.\n")
    w(f"The catchments were {mfs['catchments_selected']}. The typetal cover only discharges "
      f"*{mfs['excludes_basins']}*, and the report states they are limiting for "
      f"*{mfs['excludes_heavy_catchments']}*.\n")
    w(f"Meanwhile {mfs['counterpoint']}. **The design excludes the worst cases, and says so.**\n")
    w("| µg/l | Combined overflow | Separate stormwater | Max observed |")
    w("|---|---:|---:|---:|")
    for m, v in mfs["typetal_ug_per_l"].items():
        if m.startswith("_"):
            continue
        w(f"| {m} | {v[0]} | {v[1]} | {v[2]} |")
    w("")
    w("Note that chromium, nickel and arsenic are **higher in separated stormwater than in "
      "sewage overflow** — and nationally there is "
      f"{mon['national_volumes_m3_per_year']['separate_stormwater_discharged']/1e6:.0f} "
      "million m³/yr of the former against "
      f"{mon['national_volumes_m3_per_year']['combined_overflow_water']/1e6:.0f} million m³/yr "
      "of the latter. Separating a sewer system solves the sewage overflow and delivers "
      "untreated road runoff instead.\n")

    # ---------------------------------------------------------------- 5. Køge Bugt
    kt = koege_tables()
    if kt:
        st, plants = kt
        w("## 5. A worked case: Køge Bugt\n")
        kb = mon["koege_bugt"]
        w(f"DCE's oxygen reports state, in both 2023 and 2025: *\"{kb['iltsvind_2025']}\"* — "
          "**no oxygen depletion registered**, including in 2023, the worst iltsvind year in "
          "two decades.\n")
        w(f"{kb['interpretation']}\n")
        w("### Who can discharge sewage into the bay\n")
        w("| Municipality | Separate outfalls | Combined overflows | % separated | Basin m³ |")
        w("|---|---:|---:|---:|---:|")
        tc = tv = 0
        for k in KOEGE:
            v = st.get(k)
            if not v or not (v["sep"] + v["comb"]):
                continue
            n = v["sep"] + v["comb"]
            tc += v["comb"]
            tv += v["vol"]
            bold = "**" if k in KOEGE_NORTH else ""
            w(f"| {bold}{k}{bold} | {v['sep']} | {v['comb']} | {v['sep']/n*100:.0f}% "
              f"| {v['vol']:,.0f} |")
        w("")
        nc = sum(st[k]["comb"] for k in KOEGE_NORTH if k in st)
        nv = sum(st[k]["vol"] for k in KOEGE_NORTH if k in st)
        w(f"Vallensbæk, Ishøj and Solrød have **zero** combined-sewer overflows; Greve has "
          "two. The shoreline communities separated their systems and physically cannot "
          "discharge sewage into the bay in a storm.\n")
        w(f"**{nv/tv*100:.0f}% of the bay's basin storage** ({nv:,.0f} of {tv:,.0f} m³) sits "
          f"in København, Hvidovre and Tårnby, along with {nc} of {tc} combined overflows. "
          # "downstream" was dropped here on purpose: the section that follows tests
          # the claim and finds it holds only in part, so asserting it first was
          # arguing ahead of the evidence.
          "The bay opens southeast, so the discharge enters at the northern end. "
          "**The municipality that built the storage is not the one that smells "
          "it.**\n")
        w(KOEGE_TRANSPORT)
        if plants:
            w("### Treatment capacity discharging to the bay\n")
            w("| Plant | PE | Municipality |")
            w("|---|---:|---|")
            for n, pe, k in plants:
                w(f"| {n} | {pe:,} | {k} |")
            w("")

    # ------------------------------------------------------------------- caveats
    w("## What this does and does not establish\n")
    w("**It does not establish that urban discharge is the dominant national source.** Under "
      "every reconstruction attempted, including ones stacked generously in that direction, "
      "agriculture remained the largest nitrogen term. Stacking every identified bias in the "
      "overflow figures reaches roughly 10% of the land-based term — material, far above the "
      "published 0.6%, and still not the driver.\n")
    w("**It does establish that the published percentage answers a different question than "
      "the one it is used for.** It answers: *of the nitrogen we observe arriving by stream "
      "from Danish land, how much do we attribute to farming after subtracting our models of "
      "everything else?* It is read as: *how much of Denmark's marine nitrogen problem is "
      "agriculture?*\n")
    w("Those differ by a closed set, a potency term, and a state variable. The accounts "
      "contain none of the three.\n")
    w("**Bounds marked as ours are ours.** Several ranges in section 1 are constructed here "
      "from the biases identified, not published figures. They are stated so they can be "
      "argued with.\n")

    path = os.path.join(ROOT, "docs", "NITROGEN.md")
    text = "\n".join(o)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    log(f"wrote docs/NITROGEN.md ({len(text):,} chars)")
    log(f"  {len(paths)} pathways, {unq} unquantified, quantified subset {lo:.0f}-{hi:.0f} kt N/yr")
    return 0


if __name__ == "__main__":
    sys.exit(main())
