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

The coefficients are arithmetic on balanced equations; the largest rests on the
Redfield-Ketchum-Richards composition of plankton, an average and so a model. The
coverage counts come from the national monitoring layers. Both are stored in
data/derived/oxygen.json and the page is rendered from what was stored, so every
coefficient prints with its derivation. Every assertion on the page is a claim in
data/manual/claims.d/w1-ob.json; nothing is carried as a quotation of the page's past.

Output: data/derived/oxygen.json, docs/OXYGEN.md

Usage:  python3 scripts/oxygen.py [--render]
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, read_json, write_doc, write_json
import claims
import live

OUT = os.path.join(ROOT, "docs", "OXYGEN.md")
OX_JSON = os.path.join(DERIVED, "oxygen.json")
CURRENTS_INDEX = os.path.join(DERIVED, "currents_index.json")
AREAS_JSON = os.path.join(DERIVED, "areas.json")
OBS_JSON = os.path.join(DERIVED, "observing.json")     # DCE's Tabel 3, parsed

# Molar masses, g/mol, so every coefficient below is derived and not asserted.
MASSES = {"O2": 31.998, "C": 12.011, "N": 14.007, "S": 32.06, "Fe": 55.845,
          "CH4": 16.043, "CH2O": 30.026, "tripalmitin": 807.3}
# Redfield-Ketchum-Richards, the standard remineralisation stoichiometry:
#   (CH2O)106(NH3)16H3PO4 + 138 O2 -> 106 CO2 + 16 HNO3 + H3PO4 + 122 H2O
RKR = {"O2": 138.0, "C": 106.0, "N": 16.0}
# Moles of O2 per mole of reductant in each balanced equation, and two stated values
MOLES = {"nitrification": 2, "sulphide": 2, "ferrous": 0.25, "methane": 2,
         "tripalmitin": 72.5}
STATED = {"o2_per_protein": 1.5,   # stored, not printed: no source was found for it
          "o2_per_cod": 1.0}       # COD is defined as oxygen demand


def coefficients():
    """Grams of O2 consumed per gram of each reductant, from the equations."""
    m, r, n = MASSES, RKR, MOLES
    per_c = m["O2"] / m["C"]                                   # CH2O + O2 -> CO2 + H2O
    return {
        "per_c": per_c,
        "per_n_growth": (r["C"] / r["N"]) * (m["C"] / m["N"]) * per_c,   # carbon route
        "per_n_nitrif": n["nitrification"] * m["O2"] / m["N"],  # NH4+ + 2 O2 -> NO3- ...
        "per_n_total": (r["O2"] / r["N"]) * m["O2"] / m["N"],   # both together
        "per_s": n["sulphide"] * m["O2"] / m["S"],              # HS- + 2 O2 -> SO4(2-) + H+
        "per_fe": n["ferrous"] * m["O2"] / m["Fe"],             # 4 Fe2+ + O2 + 4 H+ -> ...
        "per_ch4": n["methane"] * m["O2"] / m["CH4"],           # CH4 + 2 O2 -> CO2 + 2 H2O
        "per_fat": n["tripalmitin"] * m["O2"] / m["tripalmitin"],  # C51H98O6 + 72.5 O2
        "per_carb": m["O2"] / m["CH2O"],
    }


def render(d, kf, hl, t3):
    """d is oxygen.json loaded live; kf is Køge Bugt's flushing time; hl the national
    hazardous-substance layer counted by water type (areas.json); t3 DCE's Tabel 3
    parsed (observing.json). Every assertion is a claim, marked here."""
    cd, _, _ = claims.load()
    cache = {}
    R = lambda text: claims.resolve(cd, text, cache)[0]
    C, B, E = live.claim, live.claim_begin, live.CLAIM_END
    cf, st, hz = d["coefficients"], d["stated"], d["hazardous"]
    O2, CH4 = live.chem("O2"), live.chem("CH4")
    demand = [
        ("Respiration of algal biomass grown in place",
         f"{cf['per_n_total']:.1f} g {O2} per g N", True, "C-OB-OX-R1",
         "The route the requirement is built on. Nitrogen becomes carbon at Redfield "
         "stoichiometry, the carbon is respired, and the organic nitrogen is nitrified.",
         "load terms"),
        ("Respiration of organic matter that arrived already made",
         f"{st['o2_per_cod']:.1f} g {O2} per g COD", False, "C-OB-OX-R2",
         "Sewage organics, fat, riverine particulate carbon, anything washed off a "
         "surface. COD is its demand measured chemically, in grams of oxygen. It needs no "
         "growth step: fat and carbohydrate carry no nitrogen, and though sewage organics "
         "carry some, their oxygen demand does not wait on it.",
         "no"),
        ("Nitrification of ammonium",
         f"{cf['per_n_nitrif']:.2f} g {O2} per g N", True, "C-OB-OX-R3",
         "Nitrifying bacteria and archaea oxidise ammonium to nitrate, and the oxygen is "
         "gone. This is nitrogen acting as a *reductant*, not as a fertiliser: it needs no "
         "algal growth step.",
         "no"),
        ("Oxidation of sulphide from the sediment",
         f"{cf['per_s']:.2f} g {O2} per g S", False, "C-OB-OX-R4",
         "Reduced compounds made in anoxic sediment, sulphide among them, move up and are "
         "oxidised where they meet oxygen; in coastal sediments most of the oxygen consumed "
         "goes to such re-oxidation. A storm that stirs sulphidic water up does the same at "
         "once, and so would dredging or trawling that stirs the bed.",
         "no"),
        ("Oxidation of ferrous iron and manganese",
         f"{cf['per_fe']:.2f} g {O2} per g Fe", False, "C-OB-OX-R5",
         "The same upward route, smaller per gram: dissolved iron and manganese from the "
         "same reduced sediment.",
         "no"),
        ("Oxidation of methane",
         f"{cf['per_ch4']:.2f} g {O2} per g {CH4}", False, "C-OB-OX-R6",
         "Produced in anoxic sediment. Part of it can be oxidised on the way up without "
         "oxygen, by sulphate or nitrate; the coefficient applies to what reaches "
         "oxygenated water.",
         "no"),
        ("Decay following a kill of any cause",
         "as the material, above", False, "C-OB-OX-R7",
         "A toxicant, a salinity shock, a heat event, physical destruction. Whatever "
         "kills leaves a mass that decays, and the decay draws the oxygen down. The oxygen "
         "deficit is then downstream of the killing agent, and carries no information "
         "about it.",
         "no"),
    ]
    supply = [
        ("Warming reduces how much the water can hold", "C-OB-OX-S1",
         "Solubility, not biology: warmer water holds less oxygen. Water temperature is a "
         "candidate variable, as surface temperature, so this one is at least "
         "representable.", "temp"),
        ("Stratification blocks resupply from above", "C-OB-OX-S2",
         "A column that does not turn over does not refill. Water-column stability "
         f"(`vandsøjlestabilitet`) is a candidate variable and is selected in "
         f"{t3['with_bv']} of the {t3['models']} models in `Tabel 3`.", "BV"),
        ("Light attenuation cuts photosynthetic oxygen production", "C-OB-OX-S3",
         "The same turbidity that the Kd indicator measures also suppresses "
         "photosynthesis, the oxygen source. Kd is an indicator the models predict; it is "
         "not among the `Tabel 2` candidates.", "irr"),
        ("Reduced wind mixing", "C-OB-OX-S4",
         f"Wind stress is a candidate variable. It is selected in {t3['with_vind']} of the "
         f"{t3['models']} models, more often than phosphorus load ({t3['with_pload']}) and "
         f"less often than nitrogen load ({t3['with_nload']}).", "vind"),
    ]
    cells = [
        (True, True, True,
         "The assumed case. Nutrient enrichment, a bloom, its collapse, oxygen drawn "
         "down, the fauna killed. This one is real and does happen.", "yes"),
        (True, True, False,
         "Seasonal hypoxia in a system whose fauna is adapted to it, or a deficit short "
         "enough that mobile fauna leave and return.",
         "no — an oxygen trigger fires either way"),
        (True, False, True,
         "Nitrogen present, water well oxygenated, fauna gone anyway: toxicants, "
         "antifoulants, pharmaceutical residues, ammonia toxicity, or physical "
         "destruction by trawling and dredging. Oxygen is not the only way to kill.",
         "no"),
        (True, False, False,
         f"A loaded but well-flushed system. Køge Bugt's flushing time is {kf:.0f} days. "
         "The same load in a slower water is not the same pressure, and a load coefficient "
         "fitted in one water and transferred to another carries the first water's "
         "flushing with it.", "no"),
        (False, True, True,
         "Oxygen consumed by material that arrived already made — the toilet-flush case "
         "— or by sulphide from the sediment, or by decay after a kill of another cause. "
         "No nitrogen needed at any step.", "no"),
        (False, True, False,
         "A naturally hypoxic basin with its own community: silled basins and fjords with "
         "restricted circulation, the Black Sea among them, and the sediment just below "
         "any bed, where oxygen reaches from under a millimetre to a few centimetres.",
         "no"),
        (False, False, True,
         "A killed but oxygenated water: a toxic spill, a smothering, a dredged or "
         "trawled bed. Nothing in the nutrient chain is engaged.", "no"),
        (False, False, False,
         "Health, or a nutrient-poor water that was never productive. The chlorophyll "
         "indicator scores an unproductive water and a healthy one the same way.",
         "partly"),
    ]

    o = []
    a = o.append
    a("# What actually removes the oxygen\n")
    a(C("C-OB-OX-CHAIN", "The requirement rests on a chain: nitrogen feeds algae, dead "
        "organic matter draws the oxygen down, and low oxygen harms the life on the bed. "
        "DCE use the seasonal pattern of phosphate (DIP) and of chlorophyll as indicators "
        "of whether a water body suffers oxygen deficits, because low oxygen at the bottom "
        "releases phosphate from the sediment and feeds late-summer blooms; and they note "
        "that oxygen deficits affect, among other things, the bottom fauna.") + "\n")
    a(C("C-OB-OX-BASIS", "Every joint in that chain comes apart, and this page takes them "
        "one at a time. The coefficients below are arithmetic on balanced equations and "
        "molar masses; the largest rests on the Redfield–Ketchum–Richards composition of "
        "plankton, an average from which real plankton depart. The coverage counts come "
        "from the national monitoring layers.") + "\n")

    a("## 1. Oxygen is a balance, not a substance that nitrogen removes\n")
    a(C("C-OB-OX-BALANCE", "An oxygen deficit is what is left when demand exceeds supply. "
        "Both sides have many entry points, and most of those below need no nitrogen at "
        "all.") + "\n")
    a("### Routes that consume oxygen\n")
    a(C("C-OB-OX-DEMAND-TABLE", "Each coefficient is grams of oxygen per gram of the "
        "reductant, from its balanced equation and molar masses; the last column names the "
        "`Tabel 2` candidate, if any, that could carry the route in DCE's statistical "
        "models.") + "\n")
    a("| route | stoichiometry | needs N? | representable in the statistical layer? |")
    a("|---|---|:-:|---|")
    for name, stoich, needs_n, _, _, rep in demand:
        a(f"| {name} | {stoich} | {'yes' if needs_n else '**no**'} | {rep} |")
    a("")
    for name, _, _, cid, note, _ in demand:
        a(f"**{name}.** " + C(cid, note) + "\n")
    a("### Routes that fail to resupply oxygen\n")
    a(C("C-OB-OX-SUPPLY-TABLE", "No coefficient is given for these here; the last column "
        "names the `Tabel 2` candidate that could carry each.") + "\n")
    a("| route | representable? |")
    a("|---|---|")
    for name, _, _, rep in supply:
        a(f"| {name} | {rep} |")
    a("")
    for name, cid, note, _ in supply:
        a(f"**{name}.** " + C(cid, note) + "\n")

    a("## 2. The exchange rates\n")
    a(C("C-OB-OX-PRICES", "If oxygen is the currency, then every substance that consumes it "
        "has a price, and the prices differ by more than an order of magnitude. These "
        "follow from the balanced equations:") + "\n")
    a("| substance | oxygen consumed per kg | kg needed to equal a kilogram of nitrogen |")
    a("|---|---:|---:|")
    rows = [("Nitrogen, full remineralisation route", cf["per_n_total"]),
            ("Nitrogen, carbon route only", cf["per_n_growth"]),
            ("Nitrogen, nitrification only", cf["per_n_nitrif"]),
            ("Organic carbon", cf["per_c"]),
            ("Fat (tripalmitin)", cf["per_fat"]),
            ("Carbohydrate", cf["per_carb"]),
            ("Sulphide sulphur", cf["per_s"]),
            ("Methane", cf["per_ch4"]),
            ("Ferrous iron", cf["per_fe"]),
            ("COD, by definition", st["o2_per_cod"])]
    for lab, v in rows:
        a(f"| {lab} | {v:.2f} kg {O2} | {cf['per_n_total'] / v:.1f} |")
    a("")
    a(C("C-OB-OX-CEILING", "So a kilogram of nitrogen, taken all the way through growth and "
        f"remineralisation, consumes **{cf['per_n_total']:.1f} kg of oxygen** — the largest "
        "figure in the table, and the reason the nitrogen route is taken seriously. But "
        "that is a *ceiling reached only if every step completes*: the nitrogen must be "
        "bioavailable, must be limiting, must actually be taken up, the biomass must die "
        "in place rather than be exported or eaten, and it must decay where the oxygen "
        "matters.") + "\n")
    a(C("C-OB-OX-FAT", f"Fat pays **{cf['per_fat']:.2f} kg {O2} per kg** and skips every one "
        "of those conditions. It arrives already made. It does not need to be limiting, "
        f"taken up, or grown. Roughly **{cf['per_n_total'] / cf['per_fat']:.1f} kg of fat** "
        "matches the full theoretical oxygen demand of a kilogram of nitrogen — and **"
        f"{cf['per_n_nitrif'] / cf['per_fat']:.1f} kg** matches what a kilogram of ammonium "
        "consumes by nitrification alone.") + "\n")
    a("> " + C("C-OB-OX-ACCOUNTING", "The requirement is set in nitrogen: DCE compute it "
      "from each water body's relation between nitrogen input and total-nitrogen "
      "concentration. Danish input accounting does carry an oxygen-demand measure — DCE's "
      "marine strategy note reports organic matter as `BI5`, a biological oxygen demand, "
      "beside nitrogen and phosphorus — but organic matter is not among the candidate "
      "variables of the statistical models.") + "\n")

    a("## 3. Eight combinations\n")
    a(C("C-OB-OX-EIGHT", "Take the three things the chain joins — nitrogen loaded, oxygen "
        "low, higher life gone — and enumerate the eight combinations. A mechanism exists "
        "for each one; the table names one or more for each, and says whether the "
        "indicators tell it apart.") + "\n")
    a(f"| N loaded | {O2} low | life gone | what produces this state | do the indicators distinguish it? |")
    a("|:-:|:-:|:-:|---|---|")
    for n, ox, life, note, dist in cells:
        y = lambda b: "●" if b else "○"
        a(f"| {y(n)} | {y(ox)} | {y(life)} | {note} | {dist} |")
    a("")
    a(C("C-OB-OX-INDICATORS", "Reading down the last column: the indicator set responds to "
        "low oxygen and to high chlorophyll. It cannot tell a water killed by nutrients "
        "from a water killed by something else. The fauna indicator's soft-bottom survey, "
        "which the national programme runs between the first of March and the end of May, "
        "comes after the winter, before the summer, and months after an autumn kill.")
      + "\n")
    a(C("C-OB-OX-HAZARD", "And the toxicant column is not monitored in the sea in this "
        "layer. The water-plan register's hazardous-substance layer holds "
        f"{hl['points']} points: {hl['lake']} in lakes, {hl['river']} in rivers and "
        f"{hl['coast']} in coastal or marine water. Of Denmark's {hz['n_wb']} marine water "
        f"bodies, {hz['without']} have none, covering {hz['area_without']:,.0f} km² - "
        f"{hz['pct_without']:.0f}% of the sea. Across those freshwater points the matrices "
        f"measured are biota {hz['biota']}, water {hz['water']} and sediment "
        f"{hz['sediment']}.") + "\n")
    a(C("C-OB-OX-DOME", "The international ICES DOME archive holds Danish marine sediment "
        "contaminant data. This project's notes on its Danish sediment file record "
        "organotins, TBT among them, measured for a run of years and then almost not at "
        "all; the analysis behind those notes is not stored as a script.") + "\n")
    a(C("C-OB-OX-POISON-UNTESTED", "So a hypothesis in which the seabed was poisoned rather "
        "than suffocated is not tested by the programme that sets the requirement: no "
        "toxicant is among its candidate variables, and its hazardous-substance layer has "
        "no marine point.") + "\n")

    a("## 4. Low oxygen is not the same as no life\n")
    a(C("C-OB-OX-LOWLIFE", "This is the combination that sounds contrived, and it is well "
        "documented. In marine sediment oxygen reaches from under a millimetre in active "
        "mud to a few centimetres in permeable sand, and below that hypoxic and anoxic "
        "conditions are the norm. Where hypoxic water carries nitrate, sulphur-oxidising "
        "bacteria — *Beggiatoa*, *Thioploca* — often form thick mats that blanket the "
        "sediment: specific hypoxic ecosystems with their own specialised fauna. Under "
        "severe oxygen shortage, foraminifera, nematodes and soft-bodied worms are "
        "typically favoured.") + "\n")
    a(C("C-OB-OX-NOTFAUNA", "So an oxygen reading near zero is consistent with an active, "
        "specialised community. What it is not consistent with is the particular "
        "assemblage of large, slow, long-lived animals that people mean by a living "
        "seabed: the contribution of animals falls as oxygen drops, and sulphide is toxic "
        "to them. Those two statements are different, and the indicator makes only the "
        "first one.") + "\n")
    a(C("C-OB-OX-CHL", "The inverse holds as well. **Chlorophyll is a biomass measure.** A "
        "low chlorophyll reading scores as good status whether the water is healthy or too "
        "poor, too dark or too poisoned to produce anything, and a high reading scores as "
        "bad whether it comes from a nutrient-choked soup or a productive season in a "
        "healthy sea. DCE's indicator averages May to September, following the "
        "EU-intercalibrated chlorophyll indicator. By their account phosphorus mostly "
        "governs chlorophyll in spring, but because spring is outside that indicator, "
        "*\"er det kvælstoftilførslen, der oftest udvælges som forklaringsvariabel\"*.")
      + "\n")
    a("> " + C("C-OB-OX-QUANTITY", "Neither chlorophyll nor oxygen is a measure of "
      "ecological state. Both are measures of *quantity* — how much biomass, how much "
      "dissolved gas — standing in for a claim about *composition*: which organisms are "
      "there. A system can lose every large animal it had and still rise in both biomass "
      "and productivity.") + "\n")

    a("## 5. What follows\n")
    a(C("C-OB-OX-NMATTERS", "None of this shows that nitrogen does not matter. The full "
        "remineralisation route is the most oxygen-expensive line in the table, and where a "
        "system is nitrogen-limited and poorly flushed, reducing nitrogen will reduce "
        "oxygen demand. That much is sound.") + "\n")
    a(C("C-OB-OX-FOLLOWS", "What it shows is that the requirement is set in one currency, "
        "nitrogen, while the oxygen it protects has many debtors, and of the eight "
        "combinations the indicators single out one and partly a second. The fix is not a "
        "different target — it is an oxygen-demand budget alongside the nutrient budget, "
        "fauna surveys timed to catch a kill as well as the spring, and sediment toxicant "
        "measurement in the programme that actually sets the requirement.") + "\n")
    return "\n".join(o) + "\n"


def main(argv=()):
    if "--render" not in argv:
        A = read_json(os.path.join(DERIVED, "areas.json"))["areas"]
        tot = sum(r["area_km2"] for r in A.values())
        with_pts = [r for r in A.values() if r["observation"].get("hazardous")]
        without = [r for r in A.values() if not r["observation"].get("hazardous")]
        # Counts come from the layer itself, not from the subset that fell within the
        # 20 km assignment radius - mixing the two gave a five-of-205 that was five of
        # one denominator and 205 of another.
        feats = read_json(os.path.join(RAW, "national", "sw_mfs_tilstand.geojson"))
        props = [f["properties"] for f in feats["features"]]
        mats = {lab: sum(1 for p in props if p.get(k) == "Ja")
                for k, lab in (("maaltbiota", "biota"), ("maaltvand", "water"),
                               ("maaltsedim", "sediment"))}
        hz = {"n_wb": len(A), "with_points": len(with_pts), "without": len(without),
              "area_without": sum(r["area_km2"] for r in without),
              "pct_without": 100 * sum(r["area_km2"] for r in without) / tot,
              "total_points": len(props), **mats}
        write_json(OX_JSON, {"_what": "Oxygen-demand stoichiometry and hazardous-substance "
                                      "monitoring coverage, for docs/OXYGEN.md.",
                             "masses": MASSES, "rkr": RKR, "moles": MOLES,
                             "stated": STATED, "coefficients": coefficients(),
                             "hazardous": hz})
    kf = live.live_json(CURRENTS_INDEX)["retention"]["koege_bugt"]["flush_days_20km"]
    hl = live.live_json(AREAS_JSON)["hazardous_layer"]
    t3 = live.live_json(OBS_JSON)["dce_table3"]
    try:
        write_doc(OUT, render(live.live_json(OX_JSON), kf, hl, t3))
    except (live.Unjustified, claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote docs/OXYGEN.md ({os.path.getsize(OUT):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
