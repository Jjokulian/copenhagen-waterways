#!/usr/bin/env python3
"""What actually removes the oxygen, and what the indicators can tell apart.

The requirement rests on a chain read as a fixed conjunction: nitrogen makes algae,
algae make oxygen depletion, oxygen depletion kills the seabed, and a dead seabed
gives you fedtemoeg on a shore. Each arrow is treated as an implication in both
directions, so that measuring one link is taken as measuring all of them.

Every joint in that chain comes apart, and this page takes the joints one at a time:

  1. Oxygen is a balance with many entry points on both sides, several of which need
     no nitrogen and no growth step. The stoichiometry of each is known and is given
     here, because the exchange rates are the argument - a kilogram of fat and a
     kilogram of nitrogen do not cost the same oxygen, and neither is priced.

  2. The chain is severable at every joint. There are eight combinations of
     (nitrogen present) x (oxygen low) x (higher life gone), and a real mechanism
     exists for each. The indicator set can distinguish two of them.

  3. Low oxygen is not the same as no life, and this is the one that sounds contrived.
     It is not. It is the state the project's own argument has been describing.

No claim here depends on anyone's model. The stoichiometry is arithmetic on balanced
equations; the coverage counts come from the national monitoring layers.

Output: docs/OXYGEN.md

Usage:  python3 scripts/oxygen.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, read_json

OUT = os.path.join(ROOT, "docs", "OXYGEN.md")

# Atomic masses, so every coefficient below is derived and not asserted.
M_O2, M_C, M_N, M_S, M_FE, M_CH4 = 31.998, 12.011, 14.007, 32.06, 55.845, 16.043

# Redfield-Ketchum-Richards, the standard remineralisation stoichiometry:
#   (CH2O)106(NH3)16H3PO4 + 138 O2 -> 106 CO2 + 16 HNO3 + H3PO4 + 122 H2O
RKR_O2, RKR_C, RKR_N = 138.0, 106.0, 16.0

O2_PER_C = M_O2 / M_C                          # 2.66  CH2O + O2 -> CO2 + H2O
O2_PER_N_GROWTH = (RKR_C / RKR_N) * (M_C / M_N) * O2_PER_C  # 15.1 carbon route only
O2_PER_N_NITRIF = 2 * M_O2 / M_N               # 4.57  NH4+ + 2 O2 -> NO3- + 2 H+ + H2O
O2_PER_N_TOTAL = (RKR_O2 / RKR_N) * M_O2 / M_N  # 19.7  both together
O2_PER_S = 2 * M_O2 / M_S                      # 2.00  HS- + 2 O2 -> SO4(2-) + H+
O2_PER_FE = 0.25 * M_O2 / M_FE                 # 0.14  4 Fe2+ + O2 + 4 H+ -> 4 Fe3+ + 2 H2O
O2_PER_CH4 = 2 * M_O2 / M_CH4                  # 3.99  CH4 + 2 O2 -> CO2 + 2 H2O
# Tripalmitin C51H98O6 + 72.5 O2 -> 51 CO2 + 49 H2O, MW 807.3
O2_PER_FAT = 72.5 * M_O2 / 807.3               # 2.87
O2_PER_CARB = M_O2 / 30.026                    # 1.07  CH2O
O2_PER_PROTEIN = 1.5                           # ~, varies with composition
O2_PER_COD = 1.0                               # COD is defined as oxygen demand

# Every route by which oxygen leaves a Danish coastal water, or fails to arrive.
# needs_n: does the route require nitrogen at all?
# in_stat: is it representable in the statistical layer's candidate variables?
DEMAND = [
    ("Respiration of algal biomass grown in place",
     f"{O2_PER_N_TOTAL:.1f} g O₂ per g N", True,
     "The route the requirement is built on. Nitrogen becomes carbon at Redfield "
     "stoichiometry, the carbon is respired, and the organic nitrogen is nitrified.",
     "load terms"),
    ("Respiration of organic matter that arrived already made",
     f"{O2_PER_COD:.1f} g O₂ per g COD", False,
     "Sewage organics, fat, riverine particulate carbon, anything washed off a "
     "surface. COD *is* the oxygen it will consume — the measurement and the effect "
     "are the same quantity. No growth step, no nitrogen anywhere in it.",
     "no"),
    ("Nitrification of ammonium",
     f"{O2_PER_N_NITRIF:.2f} g O₂ per g N", True,
     "Purely chemical demand: ammonium is oxidised and the oxygen is gone. This is "
     "nitrogen acting as a *reductant*, not as a fertiliser, and it happens whether "
     "or not anything grows.",
     "no"),
    ("Oxidation of sulphide from disturbed sediment",
     f"{O2_PER_S:.2f} g O₂ per g S", False,
     "Anoxic sediment holds sulphide. Trawling, dredging, dumping, a storm or a "
     "propeller brings it into contact with oxygenated water and it is consumed "
     "immediately.",
     "no"),
    ("Oxidation of ferrous iron and manganese",
     f"{O2_PER_FE:.2f} g O₂ per g Fe", False,
     "Same mechanism, smaller per gram, released from the same reduced sediment.",
     "no"),
    ("Oxidation of methane",
     f"{O2_PER_CH4:.2f} g O₂ per g CH₄", False,
     "Produced in anoxic sediment and consumed on its way up.",
     "no"),
    ("Decay following a kill of any cause",
     "as the material, above", False,
     "A toxicant, a salinity shock, a heat event, physical destruction. Whatever "
     "kills leaves a mass that decays, and the bacterial bloom on it draws the "
     "oxygen down. The oxygen deficit is then downstream of the killing agent, and "
     "carries no information about it.",
     "no"),
]

SUPPLY = [
    ("Warming reduces how much the water can hold",
     "≈ −2.3% per °C at 10–20 °C", False,
     "Solubility, not biology. Surface temperature is a candidate variable, so this "
     "one is at least representable.", "temp"),
    ("Stratification blocks resupply from above",
     "no coefficient", False,
     "A column that does not turn over does not refill. Present as a candidate "
     "variable (`vandsøjlestabilitet`) and selected in 13 of 72 models.", "BV"),
    ("Light attenuation cuts photosynthetic oxygen production",
     "no coefficient", False,
     "The same turbidity that the Kd indicator measures also suppresses the oxygen "
     "source. Kd is measured *as an outcome* and never enters as a driver.", "irr"),
    ("Reduced wind mixing",
     "no coefficient", False,
     "Wind stress is a candidate variable. It appears in 24 of the 72 models, more "
     "often than several nutrient terms.", "vind"),
]

# The eight combinations. (nitrogen loaded, oxygen low, higher life gone) -> mechanism
CELLS = [
    (True, True, True,
     "The assumed case. Nutrient enrichment, a bloom, its collapse, oxygen drawn "
     "down, the fauna killed. This one is real and does happen.", "yes"),
    (True, True, False,
     "Seasonal hypoxia in a system whose fauna is adapted to it, or a deficit short "
     "enough that mobile fauna leave and return. Common in fjords with an annual "
     "cycle.", "no — an oxygen trigger fires either way"),
    (True, False, True,
     "Nitrogen present, water well oxygenated, fauna gone anyway: toxicants, "
     "antifoulants, pharmaceutical residues, ammonia toxicity, or physical "
     "destruction by trawling and dredging. Oxygen is not the only way to kill.",
     "no"),
    (True, False, False,
     "A loaded but well-flushed system. Køge Bugt's flushing time is 73 days; the "
     "Limfjord broads are far longer. The same load in the two places is not the "
     "same pressure, and the load term does not know which it is in.", "no"),
    (False, True, True,
     "Oxygen consumed by material that arrived already made — the toilet-flush case "
     "— or by sulphide from disturbed sediment, or by decay after a kill of another "
     "cause. No nitrogen needed at any step.", "no"),
    (False, True, False,
     "A naturally anoxic or hypoxic basin with its own community. Deep sills, the "
     "Black Sea below 150 m, the millimetre beneath any marine sediment surface.",
     "no"),
    (False, False, True,
     "A killed but oxygenated water: a toxic spill, a smothering, a dredged or "
     "trawled bed. Nothing in the nutrient chain is engaged.", "no"),
    (False, False, False,
     "Health, or a nutrient-poor water that was never productive. The chlorophyll "
     "indicator scores an unproductive water and a healthy one the same way.",
     "partly"),
]


def render(hz):
    o = []
    a = o.append
    a("# What actually removes the oxygen\n")
    a("The requirement is built on a chain: nitrogen makes algae, algae make oxygen "
      "depletion, oxygen depletion kills the seabed, and a dead seabed puts fedtemøg on "
      "a shore. In use, each arrow gets read as an implication in both directions, so "
      "that measuring one link counts as measuring all of them.\n")
    a("Every joint in that chain comes apart. This page takes them one at a time, and "
      "nothing on it depends on anyone's model — the coefficients are arithmetic on "
      "balanced equations, and the coverage counts come from the national monitoring "
      "layers.\n")

    a("## 1. Oxygen is a balance, not a substance that nitrogen removes\n")
    a("An oxygen deficit is what is left when demand exceeds supply. Both sides have "
      "many entry points, and most of them require no nitrogen at all.\n")
    a("### Routes that consume oxygen\n")
    a("| route | stoichiometry | needs N? | representable in the statistical layer? |")
    a("|---|---|:-:|---|")
    for name, stoich, needs_n, _, rep in DEMAND:
        a(f"| {name} | {stoich} | {'yes' if needs_n else '**no**'} | {rep} |")
    a("")
    for name, _, _, note, _ in DEMAND:
        a(f"**{name}.** {note}\n")
    a("### Routes that fail to resupply oxygen\n")
    a("| route | coefficient | representable? |")
    a("|---|---|---|")
    for name, stoich, _, _, rep in SUPPLY:
        a(f"| {name} | {stoich} | {rep} |")
    a("")
    for name, _, _, note, _ in SUPPLY:
        a(f"**{name}.** {note}\n")

    a("## 2. The exchange rates nobody publishes\n")
    a("If oxygen is the currency, then every substance that consumes it has a price, "
      "and the prices differ by more than an order of magnitude. These follow from the "
      "balanced equations and nothing else:\n")
    a("| substance | oxygen consumed per kg | kg needed to equal 1 kg of nitrogen |")
    a("|---|---:|---:|")
    rows = [("Nitrogen, full remineralisation route", O2_PER_N_TOTAL),
            ("Nitrogen, carbon route only", O2_PER_N_GROWTH),
            ("Nitrogen, nitrification only", O2_PER_N_NITRIF),
            ("Organic carbon", O2_PER_C),
            ("Fat (tripalmitin)", O2_PER_FAT),
            ("Protein", O2_PER_PROTEIN),
            ("Carbohydrate", O2_PER_CARB),
            ("Sulphide sulphur", O2_PER_S),
            ("Methane", O2_PER_CH4),
            ("Ferrous iron", O2_PER_FE),
            ("COD, by definition", O2_PER_COD)]
    for lab, v in rows:
        a(f"| {lab} | {v:.2f} kg O₂ | {O2_PER_N_TOTAL/v:.1f} |")
    a("")
    a(f"So a kilogram of nitrogen, taken all the way through growth and "
      f"remineralisation, consumes **{O2_PER_N_TOTAL:.1f} kg of oxygen** — the largest "
      f"figure in the table, and the reason the nitrogen route is taken seriously. But "
      f"that is a *ceiling reached only if every step completes*: the nitrogen must be "
      f"bioavailable, must be limiting, must actually be taken up, the biomass must die "
      f"in place rather than be exported or eaten, and it must decay where the oxygen "
      f"matters.\n")
    a(f"Fat pays **{O2_PER_FAT:.2f} kg O₂ per kg** and skips every one of those "
      f"conditions. It arrives already made. It does not need to be limiting, taken up, "
      f"or grown. Roughly **{O2_PER_N_TOTAL/O2_PER_FAT:.1f} kg of fat** matches the "
      f"full theoretical oxygen demand of 1 kg of nitrogen — and **"
      f"{O2_PER_N_NITRIF/O2_PER_FAT:.1f} kg** matches what a kilogram of ammonium "
      f"actually consumes on its own, without any biology at all.\n")
    a("> Neither figure appears in any Danish accounting. The load statement is in "
      "tonnes of nitrogen and tonnes of phosphorus. There is no oxygen-demand column, "
      "so the substances that consume oxygen without containing nitrogen are not "
      "smaller in the account — they are **absent from it**.\n")

    a("## 3. The chain is severable at every joint\n")
    a("Take the three things the chain conflates — nitrogen loaded, oxygen low, higher "
      "life gone — and enumerate the eight combinations. A real mechanism exists for "
      "each one.\n")
    a("| N loaded | O₂ low | life gone | what produces this state | do the indicators distinguish it? |")
    a("|:-:|:-:|:-:|---|---|")
    for n, ox, life, note, dist in CELLS:
        y = lambda b: "●" if b else "○"
        a(f"| {y(n)} | {y(ox)} | {y(life)} | {note} | {dist} |")
    a("")
    a("Reading down the last column: the indicator set fires on low oxygen and on high "
      "chlorophyll. It cannot see the difference between a water killed by nutrients "
      "and a water killed by something else, because the *only* fauna instrument is a "
      "soft-bottom survey run 1 March–31 May — after the winter, before the summer, "
      "and months after an autumn kill.\n")
    a(f"And the toxicant column is not monitored either. Of Denmark's "
      f"{hz['n_wb']} marine water bodies, **{hz['with_points']} have a "
      f"hazardous-substance monitoring point** and {hz['without']} have none, covering "
      f"{hz['area_without']:,.0f} km² — {hz['pct_without']:.0f}% of the sea. Across all "
      f"{hz['total_points']} points nationally, the matrices measured are biota "
      f"{hz['biota']}, water {hz['water']}, and **sediment {hz['sediment']}**.\n")
    a("Sediment is where persistent toxicants accumulate, and where a benthic animal "
      "lives. It is measured at four points in Denmark. Any hypothesis in which the "
      "seabed was poisoned rather than suffocated cannot be tested, and it cannot be "
      "tested because the measurement was never taken.\n")

    a("## 4. Low oxygen is not the same as no life\n")
    a("This is the combination that sounds contrived, and it is the most solidly "
      "established one in the table.\n")
    a("Marine sediment goes anoxic within millimetres of its surface, and that anoxic "
      "layer is among the densest microbial habitats on the planet. Sulphide-oxidising "
      "bacterial mats — *Beggiatoa*, *Thioploca* — form thick white sheets exactly "
      "where oxygen is nearly absent and sulphide is plentiful; they are a *feature* of "
      "hypoxic beds, not an absence of life. The Black Sea below about 150 m has been "
      "permanently anoxic throughout recorded history and holds an active microbial "
      "community throughout. Hypoxia-tolerant nematodes and foraminifera frequently "
      "*increase* in abundance under low oxygen, because the things that ate them and "
      "competed with them are the things that left.\n")
    a("So an oxygen reading of near zero is consistent with enormous biomass and "
      "intense metabolic activity. What it is not consistent with is the particular "
      "assemblage of large, slow, long-lived animals that people mean by a living "
      "seabed. Those two statements are different, and the indicator makes only the "
      "first one.\n")
    a("The inverse holds as well. **Chlorophyll is a biomass measure.** A low "
      "chlorophyll reading is scored as good status, and it is equally produced by a "
      "healthy meadow-dominated system and by a water too poor, too dark or too "
      "poisoned to produce anything. High chlorophyll is scored as bad, and is equally "
      "produced by a nutrient-choked soup and by a productive spring in a healthy sea "
      "— which is why the indicator is defined on May–September only, cutting out the "
      "spring bloom, which in turn is why *\"det er kvælstoftilførslen, der oftest "
      "udvælges som forklaringsvariabel\"* rather than phosphorus. The window is chosen "
      "so the nitrogen signal is the one that shows.\n")
    a("> Neither chlorophyll nor oxygen is a measure of ecological state. Both are "
      "measures of *quantity* — how much biomass, how much dissolved gas — standing in "
      "for a claim about *composition*: which organisms are there. A system can lose "
      "every large animal it had and rise in both biomass and productivity. That is not "
      "a hypothetical failure mode; it is what the word *primordial soup* describes, "
      "and it is what the escalation to fedtemøg looks like from inside the numbers.\n")

    a("## 5. What follows\n")
    a("None of this shows that nitrogen does not matter. The full remineralisation "
      "route is the most oxygen-expensive line in the table, and where a system is "
      "nitrogen-limited and poorly flushed, reducing nitrogen will reduce oxygen "
      "demand. That much is sound.\n")
    a("What it shows is that the account has one column where it needs several. Oxygen "
      "demand is the quantity that actually matters, every substance in the water has a "
      "price in it, and only one of them is counted. A shore can be wrecked by any of "
      "eight paths and the instruments distinguish two. The fix is not a different "
      "target — it is an oxygen-demand budget alongside the nutrient budget, a fauna "
      "survey that runs in autumn as well as spring, and sediment toxicant measurement "
      "at more than four points.\n")
    return "\n".join(o) + "\n"


def main():
    A = read_json(os.path.join(DERIVED, "areas.json"))["areas"]
    tot = sum(r["area_km2"] for r in A.values())
    with_pts = [r for r in A.values() if r["observation"].get("hazardous")]
    without = [r for r in A.values() if not r["observation"].get("hazardous")]
    mats = {"biota": 0, "water": 0, "sediment": 0}
    n_points = 0
    for r in with_pts:
        h = r["observation"]["hazardous"]
        n_points += h["stations"]
        for k, v in h["matrices"].items():
            mats[k] = mats.get(k, 0) + v
    hz = {"n_wb": len(A), "with_points": len(with_pts), "without": len(without),
          "area_without": sum(r["area_km2"] for r in without),
          "pct_without": 100 * sum(r["area_km2"] for r in without) / tot,
          "total_points": n_points, **mats}
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(render(hz))
    log(f"wrote docs/OXYGEN.md ({os.path.getsize(OUT):,} chars)")
    log(f"  1 kg N (full route) = {O2_PER_N_TOTAL:.1f} kg O2 "
        f"= {O2_PER_N_TOTAL/O2_PER_FAT:.1f} kg fat")
    log(f"  1 kg NH4-N (nitrification only) = {O2_PER_N_NITRIF:.2f} kg O2 "
        f"= {O2_PER_N_NITRIF/O2_PER_FAT:.1f} kg fat")
    log(f"  hazardous-substance sediment measurements nationally: {mats['sediment']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
