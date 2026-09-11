#!/usr/bin/env python3
"""Generate docs/PROGRAMME.md - the argument, kept deliberately separate from the
investigation.

Every other document here reports what the data says and stops there. This one says what
ought to be done, which is a different kind of claim and is labelled as one throughout.
Numbers are pulled from the investigation outputs so the two cannot drift apart, and
each is linked back to the page that established it.

Every number, hypothesis reference and chemical species on the page is a checked
entity (LIVE_NUMBERS.md): read live from the file that computes it, read from a pinned
document, or declared as a stated value with its reason in the claims register. What
this page computes for itself - the Amager split, the tail of the overflow register,
the triage and register counts - it writes to data/derived/programme.json and reads
back, so those numbers have a field too.

Every assertion is a checked claim too (LIVE_NUMBERS.md section 11): CL() marks it, and
data/manual/claims.d/w1-pg.json holds what it rests on. What could not be justified
when the page was swept on 2026-09-11 - literature figures carried only as quotations
of this page's own earlier text, among them - is no longer said here; it is in
docs/ARCHIVE.md with the reason.

Usage:  scripts/heavy python3 scripts/programme.py   (after rivermap.py, currents.py,
        solutions.py; heavy because facts() reads the national overflow register)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figures import fig
from common import DERIVED, ROOT, log, read_json, write_doc, write_json
import claims as _claims
import live

MANUAL = os.path.join(ROOT, "data", "manual")
RAWD = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "docs", "PROGRAMME.md")
FACTS = os.path.join(DERIVED, "programme.json")
_REG = {}


def P(name):
    """A value this page chooses rather than measures - a design convention, a scale,
    an order-of-magnitude cost - declared once with its reason in the claims register
    (data/manual/claims.d/politics.json), and live, so arithmetic on it keeps its chain."""
    if "d" not in _REG:
        _REG["d"] = _claims.load()[0]
    p = _REG["d"]["params"]["politics_" + name]
    return live._mk(p["value"], ["stated", "politics_" + name, p["reason"]])


def CL(cid, text):
    """A claim this page makes, marked so the build checks it against the register. A
    trailing newline stays outside the span: a paragraph break is never inside a claim."""
    t = text.rstrip("\n")
    return live.claim(cid, t) + text[len(t):]


def RD(ph):
    """A number read from a pinned document - {read:SOURCE:shown|phrase} - held only
    while the phrase is still in the pinned text."""
    if "d" not in _REG:
        _REG["d"] = _claims.load()[0]
    return _claims.resolve(_REG["d"], ph, _REG.setdefault("cache", {}))[0]


_OX_FIELDS = {"O2_PER_N_NITRIF": ("coefficients", "per_n_nitrif"),
              "O2_PER_N_TOTAL": ("coefficients", "per_n_total"),
              "O2_PER_S": ("coefficients", "per_s"),
              "O2_PER_FAT": ("coefficients", "per_fat"),
              "O2_PER_COD": ("stated", "o2_per_cod")}


def OX(name):
    """A stoichiometric coefficient, as scripts/oxygen.py computes it from atomic masses
    and writes it to data/derived/oxygen.json - read live from there."""
    if "ox" not in _REG:
        _REG["ox"] = live.live_json(os.path.join(DERIVED, "oxygen.json"))
    group, key = _OX_FIELDS[name]
    return _REG["ox"][group][key]


R, C = live.ref, live.chem
# a count of rows in one of this page's own tables, written as a word: the table is the
# evidence and sits beside the sentence, so the count is not a number to look up
WORD = dict(enumerate("none one two three four five six seven eight nine ten eleven "
                      "twelve".split()))

# Amager island, traced by hand from the coastline. Used only to split Copenhagen's
# catchments into "could reach Vestamager by gravity" and "the harbour is in the way".
AMAGER = [(12.585, 55.700), (12.640, 55.700), (12.665, 55.640), (12.660, 55.590),
          (12.610, 55.545), (12.545, 55.575), (12.545, 55.630), (12.565, 55.665),
          (12.570, 55.686)]
VESTAMAGER_HA = 2000.0     # the 1939-43 reclamation, ~20 km2


def _inside(x, y, poly):
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def amager_split():
    """Combined-sewered impervious hectares, on Amager and on the mainland."""
    out = {"Amager": 0.0, "mainland": 0.0}
    for f in read_json(os.path.join(RAWD, "sp_kloakoplande.geojson"))["features"]:
        p, g = f["properties"], f.get("geometry")
        if not g or (p.get("kloaksystem_status") or "") != "Fælleskloakeret":
            continue
        xs, ys = [], []
        def walk(c):
            if isinstance(c[0], (int, float)):
                xs.append(c[0]); ys.append(c[1])
            else:
                for q in c:
                    walk(q)
        walk(g["coordinates"])
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        key = "Amager" if _inside(cx, cy, AMAGER) else "mainland"
        out[key] += p.get("befaestet_areal_status") or 0
    return out


# Source control targets, sorted by EVOLUTIONARY PRIOR rather than by toxicity - which
# is the axis that decides whether adaptation and burial are available at all. Each
# statement rests on a pinned source (C-PG-5-TIERS); what none could support was
# removed rather than kept on trust.
def chem_tiers():
    return [
    ("Deep prior — essential elements", [
        ("Zinc", "",
         "**An essential trace element** for humans, animals, plants and "
         "microorganisms, stored and passed on in metallothioneins.",
         "Already terminal — it is an element, and it does not degrade.",
         "**Reduce the flux, and keep the sink working.** A building-regulation rule on "
         "roof and gutter materials compounds over the life of a roof. Not a ban."),
        ("Copper", "brake pads",
         "**Essential, but harmful to aquatic life at high levels** — enough for two US "
         "states to restrict it in brake pads.",
         "Element; it does not degrade.",
         "A product standard for brake pads. Washington and California restricted copper "
         "in them under their *Better Brakes* rules."),
    ]),
    ("Weak or no prior — elements with no known role", [
        ("Cadmium, mercury, lead", "",
         "**Detoxified, not used.** Cadmium has no known function in higher organisms, "
         "and lead no confirmed biological role.",
         "Element — but mercury is methylated by sulphate-reducing bacteria in anoxic "
         "sediment, so the sink partly converts it into a more bioavailable form.",
         "What is left is the stock in sediment, which is a bed-integrity question "
         "rather than a chemicals one."),
    ]),
    ("Novel — and where the cascade ends is not established here", [
        ("`6PPD` / `6PPD-quinone`", "tyre antiozonant and its oxidation product",
         "**No organism met it before tyres did**: a synthetic, in tyres since the "
         "mid-1970s. Its oxidation product `6PPD-quinone` kills coho salmon before they "
         "spawn — the degradation product is the toxic one, so degrading is not by "
         "itself resolution.",
         "**Not established here.** Where its degradation cascade ends — and so whether "
         "it is a transient or a novo-chemical — is in no source this project could "
         "read.",
         "Replace it. The US EPA is funding the development of lower-concern "
         "antidegradants."),
    ]),
    ("Novo-chemical — novel, chronic, and the cascade never lands", [
        ("PFAS, and its precursors", "consumer products, coatings, firefighting foam",
         "**No prior anywhere in the cascade.** The carbon–fluorine bond is the "
         "strongest single bond in organic chemistry.",
         "**Never terminates.** The precursors *do* degrade — into PFCAs and PFSAs, "
         "which persist, and that is where the chain stops. Degradation here moves the "
         "problem without ending it.",
         "**Restrict the mass use, not the molecule.** Reserve it for the cases that "
         "pass both tests in the section below."),
    ]),
]

# Where each captured stream can go. The route is decided by the same evolutionary
# prior that decides the source-control instrument - which is the point of the section.
def disposal():
    return [
    ("Organic matter — fat, solids, plant biomass",
     "Deepest prior of all: it is carbon.",
     "Digest it, and burn the gas. What is left is a digestate.",
     "resource"),
    ("Nitrogen and phosphorus",
     "The whole point of the biology.",
     "Harvest as biomass, and recover rather than bury.",
     "resource"),
    ("Zinc, copper",
     "Deep prior — essential elements.",
     "**Let it become soil, below a concentration threshold.** Below it the material "
     "re-enters the terrestrial cycle; above it, a lined cell. The assay decides.",
     "threshold"),
    ("Cadmium, mercury, lead",
     "Weak or no prior — detoxified, not used.",
     "Burial, but stabilised. Mercury is methylated in anoxic sediment, so an anoxic "
     "destination is the wrong one for that fraction specifically.",
     "threshold"),
    ("`6PPD-quinone`",
     "Novel; where its cascade ends is not established here.",
     "Not settled. Whether a pond's residence time treats it depends on that terminus.",
     "unknown"),
    ("PFAS — a novo-chemical",
     "No prior, and the cascade never terminates in one.",
     "**Destruction, to specification.** And mostly it is not captured at all — it is "
     "dissolved and mobile, so a settling pond does not collect it. Destruction applies "
     "to the concentrated streams: spent filter media, firefighting foam, industrial "
     "waste.",
     "destroy"),
]

# Destruction conditions, because "burn it" done badly makes fluorinated by-products -
# from the US EPA's 2024 interim guidance, pinned and read.
def destruction():
    t = RD("{read:PG-EPA-PFAS:1,100|higher temperatures >1,100°C4, well mixed, and "
           "adequate residence time}")
    return [
        ("High-temperature incineration",
         f"above {t} °C, well mixed, with adequate residence time",
         "may destroy PFAS and limit the products of incomplete combustion — on data "
         "EPA calls limited",
         "Below those conditions the parent compound can vanish while products of "
         "incomplete combustion form; " + C("C2F6") + " and " + C("CHF3") + " are among "
         "the fluorinated species EPA discusses."),
        ("Supercritical water oxidation",
         "an emerging technology",
         "promising in the studies EPA reviewed; further work needed",
         "Not yet shown at the scale of a waste stream."),
    ]


# A design storm rather than a measurement: 10 mm in an hour is ordinary heavy rain
# in Copenhagen, well below a cloudburst, and 0.8 is the conventional runoff
# coefficient for paved surface. Both are stated so the arithmetic below can be
# redone with other numbers - nothing here rests on the exact pair.
RAIN_MM_H, RUNOFF_C = 10.0, 0.8


def koege_basins():
    """Registered spare-basin volume and rain-conditioned outfalls on Køge Bugt.

    From the national outfall register by way of docs/data/areas/areas.json, which
    is the published copy and is in the repository - `vol` is summed `vol_sb`.
    Registered, so it is a floor: a basin nobody entered is a basin that is not here.
    """
    r = live.live_json(os.path.join(ROOT, "docs", "data", "areas", "areas.json"))
    r = r["areas"]["DKCOAST201"]
    return {"m3": r["vol"], "outfalls": r["rbu"], "name": r["n"]}


# The triage's classes, under the names this page prints and the keys
# data/derived/triage.json uses.
TRIAGE_CLASSES = {"testable now": "testable", "blocked on a fetch": "fetch",
                  "blocked on resolution": "resolution", "unscoreable": "unscoreable",
                  "needs an experiment": "experiment", "not established": "unestablished"}
# The city's own plan for a combined catchment, in the classes architecture.py uses,
# that takes it out of the combined system. `separate_into_combined` stays combined.
SEPARATING = {"separate", "three_pipe", "foul_only", "part_separate"}


def triage():
    """The hypothesis triage, restricted to the IDs the register holds, read live from
    data/derived/triage.json - not from the triage page's table, because a page reading
    another page is a hand-copy by another name. Returns the class counts under this
    page's names, and the whole file for the register and group counts."""
    if "tri" not in _REG:
        T = live.live_json(os.path.join(DERIVED, "triage.json"))
        _REG["tri"] = ({k: T["classes"][v]["n"] for k, v in TRIAGE_CLASSES.items()}, T)
    return _REG["tri"]


def facts():
    """What this page computes for itself, written to data/derived/programme.json and
    read back live, so each number it prints has a field to point at."""
    sp = amager_split()
    pts = [x["properties"] for x in
           read_json(os.path.join(RAWD, "national", "punkt_rbu_udl.geojson"))["features"]]
    vols = sorted((v for v in ((p.get("vol_sb") or 0) for p in pts) if v > 0), reverse=True)
    n1 = max(1, int(len(vols) * 0.01))
    ar = read_json(os.path.join(ROOT, "docs", "data", "architecture.json"))
    comb = [c for c in ar["catchments"] if c["c"] == "combined"]
    prov = read_json(os.path.join(DERIVED, "terraincheck.json"))["provenance"]
    riv = read_json(os.path.join(DERIVED, "rivermap.json"))
    out = {
        "_what": "Counts and sums PROGRAMME.md computes for itself (scripts/programme.py, "
                 "facts()), stored so the page reads them back as live values.",
        "amager_split": {"amager_ha": sp["Amager"], "mainland_ha": sp["mainland"]},
        "rbu_register": {"points": len(pts), "with_volume": len(vols),
                         "top_one_pct_n": n1,
                         "top_one_pct_share_pct": sum(vols[:n1]) / sum(vols) * 100},
        "combined_catchments": {"n": len(comb),
                                "planned_to_separate": sum(1 for c in comb
                                                           if c.get("p") in SEPARATING)},
        "flood_sheets": {"total": len(prov),
                         "automatic": sum(1 for v in prov.values()
                                          if v.get("method", "").startswith("autoref")),
                         "assisted": sum(1 for v in prov.values()
                                         if v.get("method", "").startswith("assisted"))},
        "assisted_sheets": sorted(k for k, v in prov.items()
                                  if v.get("method", "").startswith("assisted")),
        "rivermap_corridors": len(riv["corridors"]),
    }
    write_json(FACTS, out)
    return live.live_json(FACTS)



def livestock_section(F):
    """The animals, put back into an argument that is conducted in kg per hectare.

    Every count here is official and live (scripts/livestock.py); the nitrogen
    comparison is derived and says so. The last two paragraphs are a value rather
    than a finding, and are labelled as one - this page is licensed for argument and
    that licence does not extend to pretending an ethical claim is an inference.
    """
    L = live.live_json(os.path.join(DERIVED, "livestock.json"))
    cl = live.live_json(os.path.join(DERIVED, "cropland.json"))["years"]["2025"]
    tri = triage()[0]
    o = []
    a = o.append
    a("### The word the framing leaves out\n")
    a(CL("C-PG-LS-INTRO", "Every number above is in kilograms of nitrogen per hectare, which "
         "is a way of not saying what the kilograms came out of. So, from the official "
         "counts rather than from anyone's rhetoric:\n"))
    a("| | |")
    a("|---|---:|")
    a(f"| Pigs standing in Denmark, at a moment (`{L['pigs_standing_period']}`) | "
      f"**{L['pigs_standing']/1e6:.1f} million** |")
    a(f"| Pigs slaughtered or exported live, in a year (`{L['pigs_through_period']}`) | "
      f"**{L['pigs_through_per_year']/1e6:.1f} million** |")
    a(f"| Cattle standing (`{L['cattle_period']}`) | {L['cattle_standing']/1e6:.2f} "
      "million |")
    a(f"| Pig meat produced in a year | "
      f"{L['pig_meat_million_kg_per_year']/1000:.2f} million tonnes |")
    a(f"| Sows standing (`{L['pigs_standing_period']}`) | "
      f"{L['sows_standing']/1e3:,.0f} thousand |")
    a(f"| **Born in a year** — *estimated, two ways, below* | "
      f"**{min(L['born_per_year_from_sows'])/1e6:.0f}–"
      f"{max(L['born_per_year_from_throughput'])/1e6:.0f} million** |")
    a(f"| **Died before reaching a slaughterhouse** — *estimated* | "
      f"**{L['died_before_slaughter_per_year'][0]/1e6:.0f}–"
      f"{L['died_before_slaughter_per_year'][1]/1e6:.0f} million** |")
    a(f"| People living in Denmark (`{L['people_period']}`) | "
      f"{L['people']/1e6:.2f} million |")
    a("")
    a(CL("C-PG-LS-THROUGH", "**The official throughput does not count the ones that die on "
         f"the way.** *Slaughtered or exported live* means exactly that: "
         f"{L['pigs_through_per_year']/1e6:.1f} million animals arrived at a slaughterhouse "
         "or on a lorry. Pigs that died in the barn are in no open series this project has "
         "found, so the two estimated rows above are **derived on stated conventions**, by "
         "two routes that are meant to check each other:\n"))
    a(f"- **From the sow herd.** {L['sows_standing']/1e3:,.0f} thousand sows at "
      f"{L['liveborn_per_sow_year_stated'][0]:.0f}–"
      f"{L['liveborn_per_sow_year_stated'][1]:.0f} liveborn per sow-year → "
      f"**{L['born_per_year_from_sows'][0]/1e6:.0f}–"
      f"{L['born_per_year_from_sows'][1]/1e6:.0f} million born**.\n"
      f"- **From the throughput.** {L['pigs_through_per_year']/1e6:.1f} million "
      f"arriving, grossed up for a "
      f"{L['died_before_slaughter_share_stated'][0]*100:.0f}–"
      f"{L['died_before_slaughter_share_stated'][1]*100:.0f}% loss before slaughter "
      f"→ **{L['born_per_year_from_throughput'][0]/1e6:.0f}–"
      f"{L['born_per_year_from_throughput'][1]/1e6:.0f} million born**.\n")
    a(CL("C-PG-LS-GAP", "**The two do not quite meet, and that is worth leaving visible** "
         "rather than splitting the difference: the sow route gives a lower figure than the "
         "throughput route, so either productivity sits at the top of its range or "
         "mortality sits at the bottom of its. What both routes agree on is the order of "
         f"the missing number — **something like {L['died_before_slaughter_per_year'][0]/1e6:.0f} "
         f"to {L['died_before_slaughter_per_year'][1]/1e6:.0f} million pigs a year die "
         "before the count that gets published**, which is between "
         f"{L['died_before_slaughter_per_year'][0]/L['pigs_through_per_year']*100:.0f}% and "
         f"{L['died_before_slaughter_per_year'][1]/L['pigs_through_per_year']*100:.0f}% as "
         "many again as the published throughput. They ate, they excreted, and their "
         "nitrogen is in the manure figure whether or not they appear in the production "
         "statistics.\n"))
    a(CL("C-PG-LS-STOCK", "**The stock and the throughput are different numbers, and the "
         f"difference is the fact.** On the stated convention a Danish pig lives about "
         f"{L['pig_years_per_pig_stated']*12:.0f} months, so the population at any instant — "
         f"{L['pigs_standing']/1e6:.1f} million — is a fraction of the "
         f"{L['pigs_through_per_year']/1e6:.0f} million that pass through in a year. Quoting "
         "one for the other describes a standing biomass as if it were a rate, or the "
         "reverse, and the nitrogen follows the rate.\n"))
    a(CL("C-PG-LS-MANURE", "**Because that is what the nitrogen is.** An animal is a device "
         "for turning feed into meat and excrement, and the excrement is the load. Taking "
         "the field balance's manure figure at the current area, **about "
         f"{L['manure_n_kt_per_year']:,.0f} kt of manure nitrogen goes onto Danish land in a "
         f"year**, against **{L['human_sewage_n_kt_per_year'][0]:,.0f}–"
         f"{L['human_sewage_n_kt_per_year'][1]:,.0f} kt** in the sewage of everyone who lives "
         f"here — a factor of about **{L['manure_over_human']:.0f}**, before a treatment "
         "plant removes most of the human half and nothing removes the other. *Derived, and "
         "marked as such:* the manure figure is a norm product times an area, and the human "
         "figure uses a stated per-person convention, so both can be redone with different "
         "assumptions and neither is a measurement of a river.\n"))
    a(CL("C-PG-LS-LAND", "**And the land is the same fact in another unit.** "
         f"{cl['central_pct']:.0f}% of Danish farmland grows feed and "
         f"{cl['direct_food_pct']:.1f}% grows food people eat directly, which is why the "
         "mineral fertiliser is not a separate story: most of it is spread to grow what the "
         "animals eat. [NITROGEN.md](NITROGEN.md) works the attribution through and "
         "concludes that **the herd is behind most of the nitrogen applied to Danish soil — "
         "the manure directly, and the majority of the bag through what it is spread "
         "on.**\n"))
    a(CL("C-PG-LS-FRAMING", "So the public argument is conducted as a dispute about "
         "fertiliser policy, quotas and farmers, and the arithmetic underneath it is a "
         f"question about how many animals a country of {L['people']/1e6:.0f} million people "
         "keeps, and what happens to what they excrete. A quota regulates the bag first, "
         "because the bag is the part that can be reduced without anybody deciding anything "
         "about animals.\n"))
    a("### And agriculture has the same flush, on a calendar instead of a threshold\n")
    a(CL("C-PG-LS-TWO", "Two things follow from counting the animals, and the second one "
         "is the structural point of this whole document arriving from an unexpected "
         "direction.\n"))
    a(CL("C-PG-LS-MIXTURE", "**First: nitrogen is one constituent of a mixture, and it is "
         "the only one the ledger prices.** What leaves an animal is not nitrogen, it is "
         "faeces — phosphorus and potassium, organic carbon that is oxygen demand by another "
         "name, ammonium that consumes oxygen as a reductant rather than feeding anything, "
         "sulphide, the copper and zinc that go into feed, the veterinary antibiotics and "
         "antiparasitics that go into the animals, pathogens, and the disinfectants used to "
         "clean the barn. [OXYGEN.md](OXYGEN.md) prices the ones that take oxygen — the "
         "organic matter, the ammonium, the sulphide and the fat — in grams of "
         + C("O2") + " per gram, and **none of them needs nitrogen to work**. The load "
         "account carries the nitrogen and the phosphorus; the antiparasitics are held in a "
         "sales register with no measurement of what became of them.\n"))
    a(CL("C-PG-LS-SLURRY", "**Second, and this is the part that should be uncomfortable for "
         "the argument in section 2: slurry storage is a basin.** Danish rules require a "
         "slurry tank that holds months of production, so the material accumulates, goes "
         "anoxic as a sewer basin does, and is then emptied onto fields when the rules "
         "allow. **Stored, reduced, concentrated, and released on a schedule.** The only "
         "difference from the flush this document spends section 2 attacking is what opens "
         "the valve: rainfall there, a calendar and a regulation here.\n"))
    a(CL("C-PG-LS-PULSE", "And the same two consequences follow. The delivery is a "
         "**pulse**, so an annual average cannot see it — the same objection this page "
         "makes to the overflow accounting, applied to the larger of the two sources. And "
         "the material that arrives is **reduced**, so its first act in a receiving water is "
         "to take oxygen rather than to feed anything, which is a different mechanism from "
         "the fertilisation story the whole framework is built on. The transport event is "
         "the first heavy rain onto a field that has just received it.\n"))
    a(CL("C-PG-LS-NOTEST", "*What this does not establish.* No slurry chemistry has been "
         "measured by this project, no spreading-to-stream transport event has been "
         "observed in it, and the argument is a mechanism rather than a finding — the same "
         "status as the basin flush before anybody instruments one. What it does establish "
         "is that **the two systems have the same shape**, so an accounting that cannot "
         "price a pulse is not failing at the margin of this problem. It is failing at both "
         "ends of it.\n"))
    a("#### Which means a kilogram is not a kilogram\n")
    a(CL("C-PG-LS-KG", "Put the two sources side by side at the same nitrogen mass — one "
         "kilogram of N as calcium ammonium nitrate, one kilogram of N as slurry — and the "
         "ledger records them identically. They are not identical, and the differences all "
         "run one way:\n"))
    a("| | A kilogram of N from a bag | A kilogram of N from an animal |")
    a("|---|---|---|")
    for a_, b_, c_ in [
        ("What else arrives with it", "essentially nothing",
         "organic carbon, phosphorus, potassium, sulphide, copper and zinc from "
         "feed, veterinary residues, pathogens"),
        ("How it becomes oxygen demand",
         f"**only if something grows** — through biomass, at "
         f"{OX('O2_PER_N_TOTAL'):.1f} g {C('O2')} per g N, "
         "conditional on light, season and every other requirement",
         f"**partly without anything growing**: the organic fraction is "
         f"{OX('O2_PER_COD'):.1f} g {C('O2')} per g COD on arrival, and ammonium takes "
         f"{OX('O2_PER_N_NITRIF'):.2f} g {C('O2')} per g N as a reductant "
         "whether or not it ever feeds a cell"),
        ("How it travels", "dissolved, with drainage, spread over the season",
         "partly as particles, in the first heavy rain after spreading — a slug rather "
         "than a season"),
        ("What is lost to the air", "little, except from urea",
         "ammonia at spreading, which injecting the slurry into the soil reduces "
         "markedly"),
    ]:
        a(f"| **{a_}** | {b_} | {c_} |")
    a("")
    a(CL("C-PG-LS-SAMENUMBER", "**So the same number in the account is not the same event "
         "in the water.** The mineral kilogram is a fertiliser and nothing else: it does "
         "harm by feeding something, which requires the something to be there and the light "
         "to be right. The animal kilogram is a fertiliser *and* an oxygen demand *and* a "
         "delivery vehicle for everything else in the mixture, and two of those three act "
         "without waiting for a growing season. That is [§3 of NITROGEN.md](NITROGEN.md) — "
         "nitrogen mass is the wrong currency — with the two sources named.\n"))
    a(CL("C-PG-LS-QUOTA", "It has a direct consequence for the instrument. **A quota written "
         "in kilograms of nitrogen treats the two as interchangeable, so a holding can meet "
         "it by swapping a bag kilogram for a slurry kilogram** and, on the account, have "
         "complied — while increasing every constituent the account does not carry. It is "
         "the direction the arithmetic already pushes, because the slurry is there and has "
         "to go somewhere and the bag is the part that can be cut.\n"))
    a(CL("C-PG-LS-NOTEST2", "*What this does not establish.* Nothing here measures "
         "comparative leaching, and once a nitrate ion is dissolved in a stream its origin "
         "is unrecoverable and irrelevant — a nitrate is a nitrate. The claim is about **what "
         "accompanies each kilogram and how it arrives**, not about the ion, and it rests on "
         "the route table in OXYGEN.md rather than on any measurement this project has made "
         "of a Danish field.\n"))
    a("#### The inference this invites, and why it does not follow\n")
    a(CL("C-PG-LS-INVITE", "Read the three sections above quickly and an attractive "
         "conclusion suggests itself: *the agricultural damage is mostly the faeces, not the "
         "nitrogen.* **That does not follow, and it is worth saying why at length, because "
         "the shape of it is exactly what this project keeps catching other people "
         "doing.**\n"))
    a(CL("C-PG-LS-SOIL", "The missing step is soil. Slurry is not discharged into a stream; "
         "it is spread on a field, and the field is a reactor. **Labile organic carbon is "
         f"largely respired there** — mostly to {C('CO2')} — so the oxygen demand that would "
         "have been so damaging in water is spent on land, where it does no harm to a fjord. "
         "Ammonium nitrifies. What survives the soil and reaches the sea in quantity is the "
         "mobile, conservative fraction, and that fraction is dominated by **nitrate** — "
         "which acts by fertilising, exactly as the standard account says.\n"))
    a(CL("C-PG-LS-SEQ", "So on the evidence available here, the sequence is not *faeces beats "
         "nitrogen*. It is:\n"))
    for cid, h, t in [
        ("C-PG-LS-SEQ1", "The nitrogen route is real and probably does dominate what arrives.",
         "The standard account is right about the pathway. This document's quarrel "
         "with it is about the size of the coefficient, the residual construction, "
         f"and the {tri['unscoreable'] + tri['needs an experiment']} mechanisms that "
         "never competed — not about whether nitrate fertilises."),
        ("C-PG-LS-SEQ2", "The faecal payload is a second channel that nobody prices at all.",
         "Copper and zinc, veterinary antiparasitics and antibiotics, pathogens. These do "
         "**not** respire away in a soil the way carbon does: the metals are elements and do "
         "not degrade. Whatever reaches water, stays."),
        ("C-PG-LS-SEQ3", "And its route to water is episodic rather than seasonal.",
         "Slurry that meets heavy rain, frozen or saturated ground, a tile drain or a "
         "macropore arrives close to intact. That is the case where the payload acts *as* "
         "faeces rather than as nitrate — and it is the least measured thing in the entire "
         "chain."),
    ]:
        a("- " + CL(cid, f"**{h}** {t}"))
    a("")
    a(CL("C-PG-LS-INSTR", "**Which is a statement about instruments, not about magnitudes.** "
         "Nobody in this project can say whether channel two is a tenth of channel one or a "
         "hundredth, because **the measurements do not exist**: Danish marine monitoring "
         "measures no dissolved trace metal in the water column at all, only metals in "
         "mussel tissue. The honest position is the uncomfortable one: **the second channel "
         "is unpriced, not small.** An unmeasured quantity is not a zero, and it is not a "
         "large number either.\n"))
    a(CL("C-PG-LS-X23", "**So it is an open problem, and it has a design.** [`X23` in "
         "EXPERIMENTS.md](EXPERIMENTS.md) states it: flow-triggered samplers on paired "
         "stream catchments through the spreading window and again in a window when nothing "
         "is spread, matched on soil and drainage and contrasted on livestock density, "
         "measuring the payload rather than only the nutrients — and using faecal sterols "
         "and host-specific markers, which is what turns a concentration into an "
         "attribution. **The spreading window is the manipulation**; it recurs every year, "
         "so the experiment is mostly a matter of being there with a sampler when it does. "
         "Grab sampling on a fixed schedule cannot substitute, because an event is exactly "
         "what a scheduled visit misses.\n"))
    a(CL("C-PG-LS-SENSING", "And the dense version — a node on every stream that reaches the "
         "sea, so that no result anywhere has to be extrapolated to a place nobody visited — "
         "is constructed in [SENSING.md](SENSING.md), down to the sensors and the "
         "fingerprint that separates a pig from a person from a road. **[The protocol is "
         "written out](SETTLE.md)**: hypotheses stated so they can lose, the decision rules "
         "fixed before the first sample, matched catchment pairs, and a pilot inside the "
         "reach of one association.\n"))
    a(CL("C-PG-LS-SETTLE", "The three things that would settle it are in none of the "
         "monitoring this project has profiled: event-based sampling in the "
         "days after spreading, copper and zinc with veterinary residues in stream and "
         "marine sediment rather than in mussels alone, and the rendering and slurry-tank "
         "volumes that would say how much material is in the system in the first place. "
         "Until then the correct sentence is **not** *the faeces are the problem*. It is: "
         "**the account has one channel, the source has two, and only the first has ever "
         "been weighed.**\n"))
    a("> " + CL("C-PG-LS-VALUE", "**A value, stated as one.** The author of this page would "
         "like the herd to be smaller for a reason that has nothing to do with fjords: an "
         f"animal that lives about {L['pig_years_per_pig_stated']*12:.0f} months in "
         f"confinement and is one of {L['pigs_through_per_year']/1e6:.0f} million is owed "
         "something the arrangement cannot give it. **That is not a finding and nothing in "
         "this project measures it.** It is stated here rather than left implied, because a "
         "reader is entitled to know which conclusions are carried by evidence and which by "
         "the person writing — and because the two reasons point the same way, which is "
         "worth noticing but proves nothing on its own.\n"))
    a(CL("C-PG-LS-HERD", "It does have one consequence that *is* analytic, and it belongs in "
         "the solution scope: **instruments differ in whether they touch the herd at all.** "
         "A quota met by exporting processed manure nitrogen out of the catchment delivers "
         "the fjord and leaves the animals where they are. A smaller herd delivers both. A "
         "reader who holds only the first goal should still want to know which of the two "
         "they are buying, and the current framing does not make that visible.\n"))
    return "\n".join(o)


def fold(summary, body):
    """Put a run of evidence behind one line that says what is in it.

    A case here is a verdict of three sentences standing on three tables, and the
    tables are the part a reader wants second. `<details>` is native on GitHub and
    styled by the reader, so the page reads the same in both places. The summary
    carries the finding rather than a label - what is deferred is the working, and
    a fold that hides its own conclusion would be hiding evidence rather than
    ordering it. The blank lines are load-bearing: without them the markdown
    inside an HTML block is not parsed as markdown.
    """
    return ('<details class="work">\n<summary>' + summary + "</summary>\n\n"
            + body.strip("\n") + "\n\n</details>\n")


def framing_gap(F):
    """The four findings. Every count is read from the triage or the register; every
    statement about DCE's method is a phrase in a pinned DCE report."""
    tri, T = triage()
    reg, done = T["n_register"], T["n_triaged"]
    never = tri["unscoreable"] + tri["needs an experiment"]
    grpA = T["groups"]["A"]
    a_ok = grpA["testable"]
    scope = (f"all {done} mechanisms in [the register](HYPOTHESES.md)"
             if int(done) == int(reg) else
             f"{done} of the {reg} mechanisms in [the register](HYPOTHESES.md)")
    if int(a_ok) == 0:
        rest = [name for name, key in TRIAGE_CLASSES.items()
                if key != "testable" and int(grpA.get(key, 0) or 0) > 0]
        nutrient = ("**and not one of them is in the nutrient group**, where every entry "
                    "is " + (", ".join(rest[:-1]) + " or " + rest[-1] if len(rest) > 1
                             else rest[0]) + ".")
    else:
        nutrient = f"**and {a_ok} of them are in the nutrient group.**"
    o = []
    a = o.append
    a("### Why the current framing does not reach those four words\n")
    a(CL("C-PG-FIVE", "The four words name losses. The public framing names one mechanism — "
         "nitrogen, to oxygen, to damage — and then measures the mechanism. Four findings "
         "say why that does not reach the losses, each stated with what it does **not** "
         "establish.\n"))
    a(CL("C-PG-F1", "**First: the nutrient account never beat the alternatives; it is the one "
         f"with a monitoring programme.** The [triage](hypodrafts/TRIAGE.md) classifies "
         f"{scope} against the data that exists. {tri['testable now']} are testable now — "
         f"{nutrient} {tri['unscoreable']} mechanisms cannot be tested at all because the "
         f"deciding measurement has no column anywhere, and {tri['needs an experiment']} "
         f"more need an experiment nobody has run. **{never} of them have never been in a "
         "position to compete.** *Does not establish:* that nutrients are innocent. It "
         "establishes that the contest the framing implies has not been run.\n"))
    a(CL("C-PG-F2-DCE", "**Second: the national relation is strong, and a national relation "
         "cannot show the local one.** DCE report *\"en meget stærk, signifikant lineær "
         "relation\"* between the national field surplus and the normalised diffuse "
         "nitrogen transport.") + " "
      + CL("C-PG-F2-AGG", "**The strength of a national fit is not evidence that the "
           "coefficient is stable in any one catchment**: an aggregate over catchments can be "
           "tight while the catchments differ, which is what aggregation does. A load "
           "reduction predicted from a surplus reduction depends on how much they differ, "
           "and nothing on this page measures it.\n"))
    a(CL("C-PG-F3", "**Third: the method does not produce an annual share.** DCE's split of the "
         "load into background and diffuse parts is made on five-year averages, because "
         "year by year the split is uncertain — especially, they say, for phosphorus and "
         "organic matter. Any yearly movement in a published percentage interpolates "
         "between them. And the diffuse term includes scattered dwellings *because they are "
         "hard to separate from it* — the category is a mixture by its own definition.\n"))
    a(CL("C-PG-F4", "**Fourth: three of the four words have no instrument.** *Fedtemøg* has no "
         "measurement. *Fiskedød* has no open register. *Liv i fjorden* is a claim about "
         "structure that a gas concentration does not address. **A framing that measures "
         "oxygen cannot report progress on three of the four things people are actually "
         "complaining about** — and [Køge Bugt](PLACES.md) had no registered *iltsvind* in "
         "2023 or 2025.\n"))
    return "\n".join(o)


def part_two_turn(F):
    reg = triage()[1]["n_register"]
    o = []
    a = o.append
    a("### What this changes about Part Two\n")
    a(CL("C-PG-TURN", "Not much, and that is the point. **Every intervention below was "
         "chosen to act on what arrives rather than on what it causes** — keeping rainwater "
         "out of the combined system, an outlet that is not the bay, source control on what "
         "the water carries. Those hold whichever of the register's mechanisms driven by "
         "what the water carries dominates, which is why they survive a finding that the "
         "field cannot be resolved.\n"))
    a(CL("C-PG-TURN2", "What the findings do change is the *order*: [Places, not "
         "categories](PLACES.md) takes the coasts one at a time, because a result on one "
         "coast says nothing about another until the coefficient that joins land to water "
         "is known for both.\n"))
    return "\n".join(o)


def render():
    F = facts()
    riv = live.live_json(os.path.join(DERIVED, "rivermap.json"))
    ret = read_json(os.path.join(DERIVED, "currents_index.json"))["retention"]
    mon = live.live_json(os.path.join(MANUAL, "monitoring.json"))
    st2 = live.live_json(os.path.join(DERIVED, "streams.json"))
    # written by scripts/architecture.py, which has to run before this
    arch = live.live_json(os.path.join(ROOT, "docs", "data", "architecture.json"))
    G = live.live_json(os.path.join(DERIVED, "floodmaps", "_georef.json"))
    SP = live.live_json(os.path.join(DERIVED, "station_places.json"))
    VEST = arch["polder"]["ha"]
    RAIN = st2["amager"]["design_intensity_mm_h_stated"]
    RUNC = st2["amager"]["runoff_coefficient_stated"]
    NEAR = P("rivermap_near_m")
    tri, T = triage()
    tri_total = T["n_triaged"]
    rb = F["rbu_register"]
    gs = [G[k] for k in G.keys()]
    mpp = [g["m_per_px_from_scalebar"] for g in gs]
    ses = [g["standard_error_m"] for g in gs if "standard_error_m" in g]
    sprs = [g["spread_m"] for g in gs if "spread_m" in g]
    mpp_lo, mpp_hi, se_lo, se_hi = min(mpp), max(mpp), min(ses), max(ses)
    sp_lo, sp_hi = min(sprs), max(sprs)
    vol = mon["national_volumes_m3_per_year"]
    tt = mon["typetal_nutrients_mg_per_l"]

    o = []
    a = o.append

    a("# The problem and the solution\n")
    a("> " + CL("C-PG-ARGUMENT", "**This page is an argument.** The investigation pages "
         "report what the data supports. This one says what ought to be done, which is a "
         "different kind of claim, and every claim on it is marked: each opens what it "
         "rests on. The *conclusions drawn* are the author's, and the reader is entitled to "
         "reject them.\n"))

    # ================================================================ PROBLEM
    a("## Part one — the problem\n")

    a("### The four words people actually use\n")
    a(CL("C-PG-FOUR-WORDS", "This page takes its problem statement from the public, not from "
         "the monitoring programme, because the monitoring programme measures what it can "
         "and the public names what it minds. In the recorded public argument "
         "([POLITICS.md](POLITICS.md)) the damage is named with four words.\n"))
    a("| what people call it | what they mean by it | what Denmark measures | where the word and the measurement come apart |")
    a("|---|---|---|---|")
    a(f"| **iltsvind** | the sea is suffocating | dissolved oxygen below "
      f"{P('iltsvind_mg_l'):g} mg/l **in "
      "stratified bottom water** | it needs depth and a sealed layer. Køge Bugt is "
      "shallow, mixes, and had no registered iltsvind in 2023 or 2025 "
      "([CURRENTS.md](CURRENTS.md)). Whether the criterion is *structurally* "
      "unreachable there is our inference and is not settled |")
    a("| **fedtemøg** | greasy, foul water and a shore you do not want to walk on | "
      "nothing | there is no instrument: no parameter in the monitoring this project has "
      "profiled carries it |")
    a("| **fiskedød** | dead fish, visibly, in numbers | no open register | no register "
      "of fish kills appears in the monitoring this project has profiled |")
    a("| **liv i fjorden** | the structural life is gone | eelgrass depth limit, "
      "some bottom fauna | measured — through a light proxy that censors itself in "
      "shallow water ([LIGHT.md](LIGHT.md)) |")
    a("")
    a(CL("C-PG-UNMEASURED", "**Three of the four have no usable measurement, and the fourth "
         "has never been registered in the bay next to Copenhagen — which may not be able to "
         "register it at all.** Everything on this page is shaped by that: the things people "
         "mind are, for the most part, unmeasured, and any solution below has to be judged "
         "without being able to watch them improve.\n"))

    a("### Where it is\n")
    a(CL("C-PG-WHERE", "A phrase that recurs in the record is *fjorde og indre farvande* — "
         "fjords and inner waters. The places people describe fall into four kinds, and "
         "they share neither a mechanism nor a fix:\n"))
    a("- **Fjords** — enclosed, shallow, slow to exchange, and the setting for most "
      "of the public argument.\n"
      "- **Inner waters** — the belts, sounds and bays, including ones like Køge "
      "Bugt that hold water rather than exchange it.\n"
      "- **The open sea around Denmark.**\n"
      "- **The shoreline**, where material from any of the above lands, sits and "
      "smells, and where most people meet the problem directly.\n")
    a(CL("C-PG-AREAS", "[AREAS.md](AREAS.md) is why the distinction earns a section: a fix "
         "that is true of Denmark is true of nowhere in it. Copenhagen carries the specifics "
         "in Part Two because it is the one place this project has mapped closely enough — "
         "flow paths, constructed drainage and receiving water — to name *which street, "
         "which volume, which site.* The same avenues apply elsewhere with the particulars "
         "still to be filled in.\n"))

    a("### What sits underneath those four words\n")
    a(CL("C-PG-TERMINAL", "The register keeps a separate list, arrived at from the other "
         "direction — not what people call the damage but what is actually lost when it "
         "happens. The two lists are the same subject in two vocabularies, and the join is "
         "the point of this section.\n"))
    a("| | what is lost | which public word points at it |")
    a("|---|---|---|")
    a(f"| {R('T1', family='terminal')} | the large, slow, long-lived organisms, and the structure the rest of "
      "the community lived inside | *liv i fjorden* |")
    a(f"| {R('T2', family='terminal')} | the ability to come back — the loss now maintains itself | none. "
      "**Nobody has a word for this, and it is the one that decides whether any of "
      "the rest is reversible** |")
    a(f"| {R('T3', family='terminal')} | water fit and pleasant to be in | *fedtemøg* |")
    a(f"| {R('T4', family='terminal')} | fish, shellfish, and the living made from them | *fiskedød* |")
    a(f"| {R('T5', family='terminal')} | the shore as a place to be | *fedtemøg*, again |")
    a("")
    a(CL("C-PG-ILTSVIND-MECH", "Note what falls out of the table. **`iltsvind` is not on "
         "it** — oxygen deficit is a mechanism, not a loss, and it appears in the public "
         "vocabulary because it is the thing that got measured. "
         f"And {R('T2', family='terminal')} has no public word at all: there is no everyday "
         "term for a system that has stopped being able to recover, which is precisely the "
         "state that determines whether spending money on any of Part Two is worth "
         "doing.\n"))

    a(framing_gap(F))
    a(livestock_section(F))
    a(part_two_turn(F))

    a("### What this page can and cannot honestly claim\n")
    a(CL("C-PG-CANNOT", "Because three of the four public words have no measurement, **the "
         "solutions below cannot currently verify their own success.** Rainwater rivers, a "
         "wetland outlet, treatment and source control can each be built, costed and "
         "monitored for the things that *are* instrumented — volumes, loads, "
         "concentrations. None of that would tell anyone whether the shore stopped "
         "smelling.\n"))
    a(CL("C-PG-X19", "That gap is fixable and cheap, and it is the argument for `X19` and "
         "`X20` in [EXPERIMENTS.md](EXPERIMENTS.md): a panel that reports on a schedule "
         "including the days nothing happens, and a structured record from the people who "
         "have watched the same ground longest. Without an outcome record the whole of Part "
         "Two is an argument from mechanism, and it should be read as one.\n"))
    a("Two things deliberately not on this page. The public argument itself — who "
      "said what, when, and whether it was checkable — is [POLITICS.md](POLITICS.md), "
      "and it is a different object of study. And *how pollution becomes visible to "
      "the public at all*, which is a separate project, is "
      "[OPEN_PROBLEMS.md](OPEN_PROBLEMS.md) item 9.\n")

    # ================================================================ SOLUTION
    a("## Part two — the solution\n")
    a("Seven things. They are ordered by how much evidence stands behind them, not by "
      "how appealing they are.\n")
    a("> **[Open the 3D view →](../viz/rivers3d.html)** — the whole proposal on the real "
      "city: buildings, terrain, the recovered flood paths, which alignments become open "
      "channels, which get the interceptor retrofit, and where the wetland sits. Real, "
      "recovered and proposed are labelled separately throughout.\n")

    # ---- 1
    a("### 1. Rainwater rivers — and the alignments already exist\n")
    a("![Where the water wants to go, and whether the plan lets it](river_map.png)\n")
    a("*The recovered 2012 cloudburst model against the cloudburst plan, with the plan "
      "split into routes where the water would be visible and routes where it stays in "
      "a pipe. Generated by `scripts/rivermap.py`.*\n")
    a(CL("C-PG-1-SURVEY", "The 2012 flood sheets are published as flood maps for a "
         "hundred-year event. Read with care they are also a map of where that event puts "
         "the water — and, if the model behind them follows the terrain, of the city's "
         "natural drainage network. Whether it does is tested next.\n"))
    tc_path = os.path.join(DERIVED, "terraincheck.json")
    if os.path.exists(tc_path):
        tc = live.live_json(tc_path)
        rows = []
        for name, rec in tc["sheets"].items():
            w = rec["windows"].get("50")
            if w:
                rows.append((name,
                             tc["provenance"].get(name, {}).get("method", "?")
                             .split(":")[0],
                             w["lift_pct_points"], w["flooded_below_local_pct"],
                             w["background_below_local_pct"]))
        rows.sort(key=lambda r: -r[2])
        auto = [r[2] for r in rows if r[1] == "autoref"]
        asst = [r[2] for r in rows if r[1] == "assisted"]
        a(CL("C-PG-1-TERRAIN-Q", "**And the model has been held against something "
             "independent.** The national elevation model is available on a token, so each "
             "recovered sheet can be asked the obvious question: does the modelled water sit "
             "where the ground is low? The comparison has to be local — a citywide one would "
             "only rediscover that Copenhagen slopes — and **it has to compare streets with "
             "streets.** A bare-earth model interpolates the ground under buildings, and the "
             "modelled flooding is on streets; sampling the background uniformly would "
             "measure the difference between roads and roofs. So both samples are drawn from "
             "the road network (`scripts/terraincheck.py`).\n"))
        a("| sheet | placed by | flooded below local ground | streets below local "
          "ground | difference |")
        a("|---|---|---:|---:|---:|")
        for name, method, lift, f, b in rows:
            a(f"| **{name}** | {method} | {f:.0f}% | {b:.0f}% | **{lift:+.0f} pp** |")
        a("")
        same = all(r[2] < 0 for r in rows)
        a(CL("C-PG-1-TERRAIN-R", "**Read the middle column first: Copenhagen's streets sit "
             "below their own surroundings, and the modelled flooding does not.** Between "
             f"{min(r[4] for r in rows):.0f}% and {max(r[4] for r in rows):.0f}% of street "
             f"cells are lower than the median ground within {P('terrain_window_m'):.0f} m "
             "of them, which is what a street is — a cut through a built-up block. But "
             f"only {min(r[3] for r in rows):.0f}–{max(r[3] for r in rows):.0f}% of the "
             "*flooded* cells are, and "
             + (f"**every one of the {F['flood_sheets']['total']} sheets goes the same way**"
                if same else "**not every sheet goes the same way**")
             + f", by {min(-r[2] for r in rows):.0f} to {max(-r[2] for r in rows):.0f} "
             "percentage points. Modelled flooding is not sitting in the low streets. It "
             "is sitting in the ordinary ones.\n"))
        a(CL("C-PG-1-THREE", "*Three explanations survive this, and the data cannot "
             "separate them.* **One:** the model behind the sheets may include the **sewer "
             "network** as well as the surface, so the extent may follow where pipes "
             "surcharge rather than where ground collects — in which case the flood map is "
             "partly a drainage map, which would sharpen the argument of this section rather "
             f"than weaken it. **Two:** the sheets are a {mpp_lo:.1f}–{mpp_hi:.1f} m/px render "
             "of a model, so a painted edge can spill onto ground the model never flooded. "
             f"**Three:** they are tied to the ground with standard errors of "
             f"{se_lo:.0f}–{se_hi:.0f} m.\n"))
        a(CL("C-PG-1-THIRD", "**The third explanation is the one the data argues against, "
             f"which is why it was worth running on all {F['flood_sheets']['total']}.** A "
             "positional error scatters flooding onto neighbouring cells at random, so it "
             "pushes the difference toward zero — it does not push it negative. And the "
             "sheets placed the tighter way, by water cross-correlation, average "
             f"{sum(auto)/len(auto):+.0f} points against {sum(asst)/len(asst):+.0f} for the "
             "ones placed from resident control points: better registration moves the "
             "number toward zero exactly as an offset should, and leaves it there. "
             "**Something beyond the georeferencing is putting that water on higher "
             "streets.**\n"))

    fsh = F["flood_sheets"]
    a(CL("C-PG-1-COVERS", f"**What this covers.** The 2012 model was published as "
         f"{fsh['total']} PDF sheets with the georeferencing stripped out. "
         f"{fsh['automatic']} registered automatically against the water in them. The other "
         f"{fsh['assisted']} — {', '.join('`' + n + '`' for n in F['assisted_sheets'])} — "
         "were placed from control points reported by a resident, who found marked dots on "
         f"a web map one at a time. **All {fsh['total']} are now placed**, and everything "
         f"below is **{riv['flood_path_km2']:.2f} km² of modelled flood path** across the "
         "whole city.\n"))
    a(CL("C-PG-1-BANDS", f"The {fsh['assisted']} assisted sheets are tied to the ground with "
         f"standard errors of {se_lo:.0f}–{se_hi:.0f} m, against an ensemble spread of "
         f"{sp_lo:.0f}–{sp_hi:.0f} m for the {fsh['automatic']} automatic ones, so treat the "
         f"{P('terrain_window_m'):.0f} m proximity band on those as indicative and the "
         f"{P('terrain_window_wide_m'):.0f} m band as sound. Provenance and per-sheet "
         "accuracy are in `data/derived/floodmaps/_georef.json`.\n"))
    a(CL("C-PG-1-COVERAGE", "Measured against the cloudburst plan:\n"))
    a("| | Share of the *inner-city* modelled flood path |")
    a("|---|---:|")
    a(f"| Within {NEAR:.0f} m of a planned **surface** route | **{riv['near_surface_conveyance_pct']:.0f}%** |")
    a(f"| Within {NEAR:.0f} m of a planned **pipe** | {riv['near_buried_conveyance_pct']:.0f}% |")
    a(f"| Within {NEAR:.0f} m of anything in the plan | {riv['near_anything_pct']:.0f}% |")
    a(f"| **With no surface route within {NEAR:.0f} m** | **{riv['no_surface_route_pct']:.0f}%** |")
    a("")
    a(CL("C-PG-1-POSITIVE", f"So the finding is a positive one. Across the inner city, "
         f"Copenhagen has already drawn the river network: **{riv['near_surface_conveyance_pct']:.0f}% of "
         "the flood paths there have a surface alignment planned beside them.** The city's "
         f"cloudburst plan is {fig('surface_km')} km of surface conveyance against "
         f"{fig('pipe_km')} km of pipe, {fig('surface_ratio')} to 1 "
         "([SOLUTIONS.md](SOLUTIONS.md)). The idea is not missing. The alignments are not "
         "missing.\n"))
    a(CL("C-PG-1-CONNECTION", "**What is missing is the connection.** A skybrudsvej is "
         "drawn for the extreme event — the scenarios the plan was drawn from are for a "
         "hundred-year event — and it carries water only when the pipes are already "
         "overwhelmed. Ordinary heavy rain, the rain that actually causes overflows, still "
         "goes down the gully into the combined pipe exactly as before. The surface network "
         "was built to protect the city from water, not to protect the sea from the city.\n"))
    a(CL("C-PG-1-ASK", "**The ask is therefore small and specific:** connect the everyday "
         "rain to the surface network that has already been designed and partly built, "
         "instead of only the cloudburst rain. That is a change in inlet design and "
         "drainage regulation, not a new masterplan.\n"))

    a("#### Where an open channel will not fit\n")
    a(CL("C-PG-1-NOFIT", "Not every alignment can be a river. A dense street with no room to "
         "lose, a junction, a listed square — in those places the water still has to leave "
         "the sewage system, and the way to do it is vertical rather than horizontal.\n"))
    a("![Street section: the combined sewer now, and the interceptor "
      "retrofit](retrofit_section.svg)\n")
    a(CL("C-PG-1-DROP", "**Drop the foul sewer by about a metre and put a rain-only line "
         "into the space above it.** Same trench, same street, same gully. The manhole "
         "connects to the new line instead of the old one; the house drains stay on the "
         "foul sewer, which is now deeper and, with the rain taken out, never full — which "
         "is a mixed blessing, and the next section but one is about why.\n"))
    a(CL("C-PG-1-NOMIX", "What this buys is the thing that matters: **there is no longer a "
         "mixture to overflow.** An overflow structure on a foul-only sewer has nothing to "
         "spill in a storm, because the storm is not in that pipe. It is the reason the "
         "proposal does not have to stop where the street narrows.\n"))
    a(CL("C-PG-1-LIGHT", "**But the drawing above is the heavy version of the idea, and it "
         "should not be the first one tried.** The lighter version is to leave the sewer "
         "exactly where it is and thread a small rain line into the space that already "
         "exists between the street and the pipe. Nothing on the foul side is touched: the "
         "sewer keeps its depth, every house drain keeps its connection, and the only change "
         "is that the gullies are cut off the sewer and put onto the new line. That is "
         "strictly less work than dropping a sewer under live connections.\n"))
    a(CL("C-PG-1-SIZE", "It works because **the new line does not have to carry the "
         "cloudburst.** The cloudburst already has a route — the surface network in the "
         "previous section, drawn for exactly that event. What has to come out of the "
         "combined system is the ordinary rain that fills it many times a year. Sizing for "
         "the frequent rain rather than the hundred-year one is a much smaller pipe, and it "
         "turns the question from *can a storm sewer be fitted here* into *which rain do we "
         "take out of the sea* — a priced decision with a return period on it, rather than a "
         "structural impossibility. The residue is explicit: rain above that size still "
         "meets sewage in the old pipe and can still spill, so this variant reduces "
         "overflow frequency and volume, and does not abolish them the way a full "
         "separation does.\n"))
    a(CL("C-PG-1-BORE", "**And it does not have to be dug in.** A trench means the road "
         "opened along its whole length, the traffic, the reinstatement, and everything "
         "else in the ground found the hard way. A shallow line can be **bored or driven "
         "instead** — a pit at one manhole, a pit at the next, and the pipe pushed through "
         "the ground between them. The road is then opened only at the manholes, which are "
         "the places the work has to happen anyway. For a gravity line the method has to "
         "hold the line's fall over the whole shot, and the shots are short, manhole to "
         "manhole.\n"))
    street_m_all = arch["street_m"]["amager"] + arch["street_m"]["mainland"]
    ri = sum(c.get("ri", 0) for c in arch["catchments"]
             if c["c"].startswith("combined") or c["c"] == "separate_into_combined")
    br = sum(c.get("br", 0) for c in arch["catchments"]
             if c["c"].startswith("combined") or c["c"] == "separate_into_combined")
    a(CL("C-PG-1-LENGTH", "**And the length of the job is a length of street, which can be "
         "counted.** Road centreline inside Copenhagen's combined-sewered catchments comes to "
         f"**{(arch['street_m']['amager']+arch['street_m']['mainland'])/1000:,.0f} km** "
         f"({arch['street_m']['amager']/1000:,.0f} of it on Amager) — about "
         f"{(arch['street_m']['amager']+arch['street_m']['mainland'])/arch['totals']['combined']['ha']:,.0f} "
         "m of street for every impervious hectare drained. At a manhole every "
         f"{P('manhole_spacing_m'):.0f} m that is on the order of "
         f"**{street_m_all / P('manhole_spacing_m'):,.0f} shots**, and not one of them needs "
         "a new pit: a shot starts and ends at a shaft that is already there. *Upper bound* "
         "— the road extract carries no classification, so paths and service roads are "
         "counted with the carriageways, and a real programme works down from that figure "
         "as streets are ruled out rather than up from a guess. The same scope in "
         f"structures rather than in metres: **{ri:,} gully gratings to cut over and {br:,} "
         "chambers standing in the way of, or available to, the work** — which is the "
         "number a programme is actually planned in. What a metre costs is the utility's "
         "number and not this project's; [the architecture view](architecture.html) takes a "
         "rate and gives back the total, the figure per person equivalent, and what that is "
         "a year over the life of the asset.\n"))
    a(CL("C-PG-1-BLIND", "It is not free of the thing it avoids. **Open-cut finds an "
         "unmapped cable; a bore hits it.** Working blind in the busiest metre of the "
         "ground raises the value of everything that says what is down there — the utility "
         "register, a survey, and a trial hole at each crossing — so the method makes the "
         "information problem below more acute rather than less.\n"))
    if arch.get("structures"):
        st_r = arch["structures"]["rist"]
        st_b = arch["structures"]["broend"]
        km = (arch["street_m"]["amager"] + arch["street_m"]["mainland"]) / 1000
        a(CL("C-PG-1-DENSITY", "**And the density of that problem can now be counted rather "
             "than asserted.** The city publishes its own structures — "
             f"{st_r['total']:,} gully gratings and {st_b['total']:,} manholes and wells, "
             f"each with an elevation, maintained to {st_b['last'][:4]}. Inside the "
             f"combined-sewered catchments that is **{ri:,} gratings and {br:,} chambers**, "
             f"against {km:,.0f} km of street: **a grating about every {km*1000/ri:.0f} m and "
             f"a chamber about every {km*1000/br:.0f} m.** A bore is not threading an empty "
             f"metre. It is threading a metre with a lid in it about every "
             f"{km*1000/(ri + br):.0f} m, and each lid is a thing that goes down.\n"))
        a(CL("C-PG-1-TYPEEMPTY", "**The same register also shows what it does not know.** "
             "Both layers carry a type column — `ristetype`, `broendtype` — and it is empty "
             f"on **{st_r['type_field_empty_pct']:.0f}% of the gratings and "
             f"{st_b['type_field_empty_pct']:.0f}% of the wells.** The city knows where its "
             "structures are, to the centimetre in the vertical, and its own record does not "
             "say what any of them is: which lid is a sewer manhole, which is a gully pot, "
             "which belongs to water, gas or telecom. That is the [unfilled-field "
             "class](CONSTRUCTED.md) of this project's error taxonomy, in the register a "
             "contractor would plan from — and it is the concrete form of the objection "
             "above. The instrument that would answer it is the utility register, which is "
             "not open.\n"))
    a("> **[The arrangement in three dimensions →](section3d.html)** — the same "
      "street at its real sizes: the bored line, the sewer left where it is, the "
      "shaft with its pan, and the liner. Every dimension is a named parameter that "
      "says whether it is measured or merely stated, and all of them move.\n")
    a(CL("C-PG-1-SHAFT", "**The junction is where this gets interesting: one shaft, two "
         "floors.** At every existing street connection the shaft carries on through the new "
         "rain line rather than stopping at it. At rain-line level a **watertight pan forms "
         "the floor of that storey**: what comes off the street lands on it and is turned "
         "into the rain pipe, while the shaft below it stays a shaft. To reach the sewer, "
         "the pan is lifted — held down by its own weight the rest of the time — and the "
         "manhole is a manhole again. One opening in the road, one asset to maintain, the "
         "gully keeps its sand trap, and nothing about access to the foul sewer is given "
         "up.\n"))
    a(CL("C-PG-1-CONDS", "Four conditions decide whether that detail is sound, and they are "
         "stated here as conditions rather than as answers:\n"))
    for i, (h, t) in enumerate([
        ("It must not be liftable from below.",
         "A pan held by gravity seals downward and is defeated by pressure upward — "
         "which is exactly the fault case, a surcharged sewer, and would put foul "
         "water into the rain line at every manhole at once. The seat has to be "
         "latched, or shaped so back-pressure seats it harder rather than lifting "
         "it. The separation is physical or it is not there."),
        ("It is a sump, so it is on a cleaning schedule or it is a problem.",
         "Grit and leaves collect on a flat pan. Emptied with the gully, that is a "
         "feature and the first thing the rain line would otherwise carry. Not "
         "emptied, it is the basin argument again at the scale of one shaft."),
        ("Sealing a storey removes a vent.",
         "A foul sewer is ventilated through its shafts, and a watertight floor at "
         "rain level closes one. The ventilation has to be re-made deliberately, or "
         "hydrogen sulphide accumulates in the place nobody now opens."),
        ("Entry gets harder, not easier.",
         "Lifting a pan while standing over a live sewer, possibly with rain running "
         "in, is a confined-space job with a new step in it. It needs a lifting "
         "point, a way to secure the pan open, and a rule about when the storey "
         "above can be running."),
    ], 1):
        a("- " + CL(f"C-PG-1-COND{i}", f"**{h}** {t}"))
    a("")
    fb = []
    fa = fb.append
    fa(CL("C-PG-1-BLOCK", "**A small pipe blocks. That is its failure mode, and it is the "
          "right one to have.** A combined sewer that blocks backs sewage into a basement. A "
          "rain line that blocks puts rainwater on the street it came from — visible, "
          "local, and nobody's floor. The design question is therefore not whether it can "
          "block but whether the blockage is findable and reachable, and the construction "
          "method settles most of that: with a shot from shaft to shaft, **no point on the "
          "line is more than half a spacing from an opening**, and a jetting hose can be put "
          "in at either end.\n"))
    fa(CL("C-PG-1-ACC", "What actually accumulates:\n"))
    for i, (h, t) in enumerate([
        ("Street grit and winter sand.",
         "Caught before the pipe if the gully keeps its sand trap — which it does, "
         "because the gully is not being rebuilt. The pan in the shaft is a second trap, "
         "and a *designed* one: material that settles there has reached the one place in "
         "the system with a lid, a lorry and a schedule."),
        ("Leaves.",
         "Seasonal, and an argument for street sweeping before the autumn rather "
         "than for a larger pipe."),
        ("Fat and fibre, if greywater is admitted.",
         "Laundry lint and kitchen fat come from fixtures rather than from streets. This "
         "is the second argument for the fixture standard in section 2: the kitchen sink "
         "is the one greywater fixture that should stay on the foul line."),
        ("Roots.",
         "A shallow line under a street with trees. Root entry is a joint problem, "
         "and a bored or driven line is fused or welded rather than socketed — so "
         "the construction method that makes it cheap is also the one that gives "
         "roots nothing to enter."),
    ], 1):
        fa("- " + CL(f"C-PG-1-ACC{i}", f"**{h}** {t}"))
    fa("")
    fa(CL("C-PG-1-SCOUR", "**And a small pipe is better at keeping itself clean than a "
          "large one**, which is the part that reads backwards. A gravity line scours at "
          f"roughly {P('scour_lo_m_s'):g}–{P('scour_hi_m_s'):g} m/s, and velocity comes from "
          "filling the bore. A line sized for the ordinary rain fills often; a line sized "
          "for the hundred-year storm runs as a trickle in a wide invert almost every time "
          "it runs at all, and drops its load. Sizing for the frequent rain is not only the "
          "cheaper choice, it is the self-cleansing one — the design condition is that the "
          "scouring velocity is reached at some stated frequency, not that the pipe is "
          "large.\n"))
    fa(CL("C-PG-1-MORE", "Three more that belong in the same list, because they are what "
          "would actually be argued about:\n"))
    for i, (h, t) in enumerate([
        ("Frost, and low points.",
         "A shallow line with standing water in a sag is a freeze plug. The requirement "
         "is cover and continuous fall — no sag between shafts."),
        ("Deformation at installation.",
         "Driving a pipe through mixed urban fill can leave voids and joint offsets, "
         "and an offset is a sediment trap for the life of the asset. That is what a "
         "camera survey after installation is for, as an acceptance test rather than as "
         "a maintenance activity."),
        ("Misconnection — and the detector that greywater costs you.",
         "In a separated system a foul pipe can end up in the rain line. The cheapest "
         "detector is the simplest: **a rain line should be dry in dry weather**, so "
         "anything flowing is a misconnection. Admitting greywater deliberately puts a "
         "legitimate dry-weather flow into that pipe and takes the test away. It does not "
         "make detection impossible — flow with the wrong chemistry is still detectable, "
         "and the fixture standard means the expected dry-weather flow is known — but it is "
         "a real cost of the greywater idea and it belongs beside its benefits."),
    ], 1):
        fa("- " + CL(f"C-PG-1-MORE{i}", f"**{h}** {t}"))
    fa("")
    fa(CL("C-PG-1-FAT", "**And the air matters as much as the water**, which is the part "
          "that connects blockage to the thing everybody has heard of. Fat congeals as it "
          "cools, and in a sewer it *saponifies*: free fatty acids take up calcium — the "
          "lining of the pipe is one source — and become a solid soap that no jet of water "
          "dissolves. The reaction wants fat, calcium and water together. A rain line "
          "supplies none of the fat if the kitchen stays on the foul side; it supplies it "
          "if it does not.\n"))
    for i, (h, t) in enumerate([
        ("The rain line has to breathe too.",
         "A line whose every inlet is water-sealed is a closed pipe of standing humid "
         "air. With rain alone that is tolerable. With a greywater baseflow it is a weak "
         "foul pipe with no ventilation, which is a biofilm and an odour complaint — so "
         "admitting greywater means providing air, at the shafts, deliberately."),
        ("The pan closes a shaft that was doing that job.",
         "This is the third condition on the two-storey shaft, arriving from the other "
         "direction: the foul sewer below is ventilated through its shafts, and a "
         "watertight floor at rain level takes one out of service. The vent has to be "
         "re-made through or around the pan, and it is easier to design in than to "
         "retrofit into a lid somebody already cast."),
    ], 1):
        fa("- " + CL(f"C-PG-1-AIR{i}", f"**{h}** {t}"))
    fa("")
    fa(CL("C-PG-1-UNSETTLED", "*None of this is settled here.* Cover depth, gradient, "
          "diameter and the cleaning interval are design outputs, and this project has "
          "computed none of them. What it can say is which of them decide the outcome, "
          "which is the list above.\n"))
    a(fold("Technical concerns about a small rain line — what makes it block, why a "
           "smaller pipe blocks less, and the one detector greywater costs you",
           "\n".join(fb)))
    a("#### Never full is also never scoured, and that decides which pipe gets which "
      "stream\n")
    a(CL("C-PG-1-NEVERFULL", "Taking the rain out of a combined sewer leaves a pipe sized "
         "for rain carrying only sewage. **The same sentence read the other way is the "
         "problem:** a bore that never fills never reaches a scouring velocity, so solids "
         "settle, the flow goes septic in the deposit, and sulphide comes off it — the smell "
         "of a sewer. Fat behaves the same way: it congeals in a slow flow and has time to "
         "saponify.\n"))
    a(CL("C-PG-1-VENT", "It also loses a ventilation mechanism. Storm flow is a piston: it "
         "pushes the air in front of it and drags fresh air behind it, so a combined system "
         "is aired by its storms. Take the rain out and the air in the pipe stops moving "
         "with it — in the same system that has just become more septic. The retrofit "
         "therefore has to say how the foul line breathes, and the two-storey shaft above "
         "makes that sharper rather than softer, because a watertight pan closes a shaft "
         "that was part of the answer.\n"))
    a(CL("C-PG-1-ARRANGE", "Which is why the arrangement question is really **which pipe "
         "gets which stream**, and there are three answers, not one:\n"))
    a("| | What is built | What it costs | What it gets wrong |")
    a("|---|---|---|---|")
    a("| **Light** | a small bored rain line above; the old pipe keeps the sewage | "
      "nothing on private ground | the old pipe is now enormously oversized for what it "
      "carries |")
    a("| **Heavy** | drop the sewer a metre, rain line into the space | a relaid "
      "sewer under live connections | pays for relaying, and then relays the same "
      "wrong diameter unless it is downsized on the way |")
    a("| **Swapped** | keep the big pipe for the rain it was sized for; bore a small "
      "new **foul** line | every house drain has to be moved onto it | the work "
      "crosses the property line, which is what makes separation slow |")
    a(CL("C-PG-1-FOURTH", "**And there is a fourth that takes the good half of each.** The "
         "old combined sewer does not have to be abandoned at its diameter: it can be "
         "**lined down to a foul-sized bore from the same shafts**, using the pipe that is "
         "there as the duct. The rain goes in the new shallow line, the sewage goes in a "
         "bore sized to scour itself, no house drain moves, and no trench is opened for "
         "either. It is the same trenchless logic applied twice — once to add a pipe, once "
         "to shrink one — and it is the arrangement this section would actually argue "
         "for.\n"))
    a(CL("C-PG-1-STATED", "*Stated, not established:* this project has not costed lining, "
         "has not checked the condition of any sewer that would receive it, and has "
         "computed no diameters. What the argument does establish is the **criterion**: a "
         "pipe should be sized for the stream it carries, and the retrofit that leaves a "
         "rain-sized pipe carrying sewage has solved the overflow and created a maintenance "
         "liability in the same move.\n"))
    a(CL("C-PG-1-WHATTHIS", "*What this is:* an arrangement and a construction method, not a "
         "design. No clearance has been checked, no diameter or gradient computed, and it "
         "concerns an asset owned by a utility that would have to decide it. It is here "
         "because it changes what the retrofit costs — and because the two-storey shaft is "
         "the detail that makes the light version buildable at the point where every "
         "street already connects.\n"))
    a(CL("C-PG-1-FIRSTMETRE", "**What decides between the two is the first metre under the "
         "street, and this project cannot see it.** Water mains, district heating, gas, "
         "telecom and the gully leads themselves occupy that zone, and whether a new line "
         "clears them — with frost cover above and a continuous fall to its outlet — is a "
         "question the utility register answers and no public dataset here does. So the "
         "section is drawn as an arrangement, not as a design, and the sizing above is "
         "stated as the decision to be taken rather than as a diameter. Both variants stay "
         "on the public side of the property line; neither requires entering a building, "
         "which is the thing that makes conventional separation slow.\n"))
    a(CL("C-PG-1-ALIGN", f"On this project's classification, **{riv['near_buried_conveyance_pct']:.0f}% of "
         f"the modelled flood path has a planned pipe within {NEAR:.0f} m** — and that "
         "sentence has to be read narrowly, because it is a statement about **alignment "
         "and nothing else**. A *skybrudsledning* is conveyance for the extreme event: "
         "sized for it, and meant to get water off the city when it comes. **It is not a "
         "river through the city to an inland settling ground, and that is the difference "
         "this whole section is about.** What a shared alignment buys is the trench, the "
         "corridor reservation and the disruption. It does not buy the pipe, the diameter "
         "or the outlet.\n"))
    if arch.get("plan_pipe_ends"):
        pe = arch["plan_pipe_ends"]
        a(CL("C-PG-1-PIPEENDS", "And where each planned pipe discharges is not in the "
             f"layer. The plan geometry is **segmented rather than routed**: of {pe['n']} "
             f"planned cloudburst pipe segments, {pe['within_50m']} have an end within "
             f"{P('pipe_end_near_m'):.0f} m of the shore or the harbour and the median "
             f"segment's nearest end is {pe['median_m']/1000:,.1f} km from water. That "
             "measures the segmentation, not the destinations — a segment normally ends at "
             "the next segment. Tracing where any given route actually comes out means "
             "reading the project pages one at a time, and it is exactly what would decide "
             "whether an alignment can be reused as it stands or only as a trench.\n"))
    if riv["corridors"]:
        a(CL("C-PG-1-CORRIDORS", f"And where no alignment exists — the "
             f"{riv['no_surface_route_pct']:.0f}% — the model names the places. "
             f"{F['rivermap_corridors']} corridor candidates come out of it: stretches with "
             f"more than {P('rivermap_deep_m'):g} m of modelled water, no surface route within "
             f"{NEAR:.0f} m, and enough length to be a channel rather than a puddle. They are "
             "circled on the map and listed in `data/derived/rivermap.json`.\n"))

    # ---- 2
    kb = koege_basins()
    rr, fl, fs = st2["rain_record"], st2["amager"]["flow_m3_s"], st2["foul_stated"]
    am, ml = F["amager_split"]["amager_ha"], F["amager_split"]["mainland_ha"]
    amager_ha = am
    hour_m3 = amager_ha * 1e4 * RAIN / 1000 * RUNC
    a("### 2. An outlet that is not the sea\n")
    a("![Where a raindrop goes now, and where it would go](system_flow.svg)\n")
    a("> **[The same architecture, on the city →](architecture.html)** — the graph "
      "with every path that changes, and a map of which sewer catchments it acts "
      "on, each one carrying its own impervious area, person equivalents and the "
      "city's own plan for it.\n")
    a(CL("C-PG-2-TWO", "Section 1 does not improve the combined system. It ends it, and what "
         "is left is **two systems with different jobs**. A foul line: small, steady, "
         "running every hour of the year, going to a treatment plant. And a rain line: "
         "intermittent, far larger at the moment it arrives, carrying the surface of the "
         "city rather than the inside of a building. Everything below follows from keeping "
         "those two apart, and most of the existing argument about basins and overflows is "
         "an argument about the mixture that no longer exists.\n"))
    a(CL("C-PG-2-RATES", "**How much larger is worth doing in rates rather than in "
         "adjectives, because a year is exactly the window that hides it.** Sewage is "
         "produced at roughly the rate people live: taking the ordinary design figures — "
         f"{fs['dwf_l_per_person_day']:.0f} litres per person per day, and a morning peak "
         f"of {fs['morning_peak_factor']:.0f}× that — a thousand people peak at about "
         f"{fs['morning_peak_m3_s_per_1000_people']*1000:.0f} litres a second, and they do "
         "it at the same hour every day, which is a load a plant can be built for. Rain is "
         f"not like that. Against {rr['years']} years of hourly rainfall over Copenhagen, "
         f"**one hectare of paved surface in a {st2['amager']['design_intensity_mm_h_stated']:.0f} "
         f"mm hour matches the morning peak of about {fs['people_matched_per_impervious_ha_in_design_hour']:,.0f} "
         f"people**. Amager's {amager_ha:,.0f} combined-sewered impervious hectares come to "
         f"**{fl['design_hour']:.0f} m³/s — the morning peak of "
         f"{fs['people_matched_by_amager_in_design_hour']/1e6:.1f} million people**, from an "
         f"island. Even the *median* hour with rain in it, {rr['median_wet_hour_mm']:.1f} mm, "
         f"is {fl['median_wet_hour']:.2f} m³/s: the morning peak of "
         f"{fs['people_matched_by_amager_at_median_wet_hour']/1000:.0f} thousand. The two "
         "streams are not the same size; putting them in one pipe is what makes the small "
         "one uncontrollable.\n"))
    era5 = RD("{read:PG-WIKI-ERA5:31|features a spatial resolution of 31 km}")
    fb = []
    fa = fb.append
    fa(CL("C-PG-2-RAINREC", "Rain is the measured side. Hourly ERA5 precipitation over "
          f"Copenhagen, {rr['years']} years, {rr['hours']:,} hours, recomputed by "
          "`scripts/streams.py`:\n"))
    fa("| | |")
    fa("|---|---:|")
    fa(f"| Mean annual rainfall | {rr['mean_annual_mm']:.0f} mm |")
    fa(f"| Hours a year with any rain | {rr['wet_hours_per_year']:.0f} |")
    fa(f"| Median hour that has rain in it | {rr['median_wet_hour_mm']:.1f} mm |")
    fa(f"| Hours a year at or above {P('rain_threshold_a_mm'):g} mm | "
       f"{rr['hours_per_year_at_or_above_mm']['2']:.0f} |")
    fa(f"| Hours a year at or above {P('rain_threshold_b_mm'):g} mm | "
       f"{rr['hours_per_year_at_or_above_mm']['5']:.1f} |")
    fa(f"| Wettest hour in the record | {rr['max_hour_mm']:.1f} mm |")
    fa("")
    fa(CL("C-PG-2-ERA5", "**The last row is a warning about the instrument, not a fact about "
          f"Copenhagen.** ERA5 is a reanalysis with a spatial resolution of {era5} km, and a "
          "cell mean cannot produce a cloudburst. So the record is used here for **ordinary "
          "rain**, which is what the system is being sized for and what causes the "
          f"overflows, and the {RAIN:.0f} mm design hour above is a stated convention. "
          "Cloudburst intensities have to come from the rain-gauge network (SVK), which this "
          "project has not fetched.\n"))
    fa(CL("C-PG-2-FOULCONV", "The foul side carries no population figure on purpose. Nobody "
          "here has sourced one for the island, so the comparison is written as an "
          "equivalence — *how many people's morning peak* a hectare of rain matches — which "
          "needs no census. The dry-weather flow per person and the peak factor are design "
          "conventions and are named as such.\n"))
    a(fold(f"The rain record behind those rates — {rr['years']} years of hourly Copenhagen "
           "rainfall, and why its wettest hour is an artefact", "\n".join(fb)))
    a(CL("C-PG-2-BASINS", "**So the basins retire.** A spare basin is an organ of the "
         "combined system: it exists to hold a mixture back until the plant can take it. "
         "Take the rain out and there is no mixture, the foul flow arrives at the rate it is "
         "produced, and the plant treats it as it comes. A basin then has nothing to buffer. "
         "It is not the instrument for the rain stream either, and the scale says why: the "
         f"entire registered spare-basin volume on **{kb['name']}** — every basin in the "
         f"water body, across {kb['outfalls']:,} rain-conditioned outfalls — is "
         f"**{kb['m3']:,.0f} m³**. One hour of {RAIN:.0f} mm of rain on Amager's "
         f"{amager_ha:,.0f} combined-sewered impervious hectares alone is about "
         f"**{hour_m3:,.0f} m³** at a runoff coefficient of {RUNC}. The whole registered "
         f"basin volume of the bay is about {kb['m3']/hour_m3*60:.0f} minutes of that one "
         "hour, from one island. Basins were never storage for the rain; they are a device "
         "for postponing a spill.\n"))
    a(CL("C-PG-2-POSTPONE", "**And postponement is where the material concentrates**, which "
         "is the reason not to answer this with more of them. Most rain fills a basin "
         "without ever spilling it: the water is held, drains back to the plant, and what "
         "it carried settles out and stays. So the store builds through every event that "
         "does **not** flush, and it leaves in the one that does. The overflow releases the "
         "water of that storm together with the accumulated sediment of the quiet ones "
         "before it. It is a flow threshold, which is why the annual-average accounting "
         "cannot see it: the ledger averages a quantity that is delivered in the few hours "
         "a year the threshold is crossed.\n"))
    a(CL("C-PG-2-ANOXIC", "**And what is held between flushes is not the water that went "
         "in.** A basin holding settled sewage solids goes anoxic in the sediment, and what "
         "leaves in the flush is the reduced product of everything that settled since the "
         "last one. [OXYGEN.md](OXYGEN.md) prices those routes and none of them is "
         "fertilisation: organic matter that arrived already made consumes "
         f"**{OX('O2_PER_COD'):.1f} g {C('O2')} per g COD** with no growth step, ammonium "
         f"consumes **{OX('O2_PER_N_NITRIF'):.2f} g {C('O2')} per g N** as a reductant rather "
         f"than a nutrient, sulphide out of reduced sediment **{OX('O2_PER_S'):.2f} g "
         f"{C('O2')} per g S**, and fat about **{OX('O2_PER_FAT'):.1f} g {C('O2')} per g** — "
         "all of it immediate, and all of it arriving as a pulse rather than a season. The "
         f"same anoxia releases iron-bound phosphate ({R('A2')}), so the flush delivers the "
         "nutrient too. Not one of these routes is representable in a load ledger written "
         "in tonnes of nitrogen a year: they are oxygen demand, not nitrogen supply, and "
         "they land in hours.\n"))
    routes = [
        ("Oxygen demand — COD, ammonium, sulphide, fat",
         "dissolved oxygen, and everything that needs it",
         "**yes** — the oxygen series, at station-months", "well"),
        ("The material itself — fat, solids, fibre, wipes",
         "what a person meets at the shore", "**nothing**", "none"),
        ("Odour", "whether the place is usable", "**nothing**", "none"),
        ("Pathogens", "bathing risk, for the days after",
         "partly — bathing water, in season, at designated points only", "partly"),
        (f"Unionised ammonia ({C('NH3')}, set by pH and temperature)",
         "gill-breathing animals, directly and quickly",
         "as total ammonium sometimes; as toxicity, no", "partly"),
        (f"Phosphate, released as the sediment reduces ({R('A2')})",
         "production weeks later, elsewhere",
         "in some series; never attributed to an event", "blind"),
        ("Turbidity, and the light it takes ([LIGHT.md](LIGHT.md))",
         f"eelgrass, which needs light to keep sulphide out ({R('T1', family='hypotheses')})",
         "Secchi — which this project found **right-censored** at shallow stations", "blind"),
        ("An organic blanket on the bed",
         f"benthic fauna, and the skin that stabilises sediment ({R('D8')})",
         "bundfauna surveys, infrequent and rarely after an event", "blind"),
        ("Metals, PAH, tyre wear, microplastics", "a food chain, over years",
         "almost nowhere in a receiving water", "none"),
        ("A kill, and then the decay of what it killed ([CAUSATION.md](CAUSATION.md))",
         "the standing stock, which becomes the next oxygen demand",
         "**nothing** — no open register of fish kills", "none"),
        ("Timing — a pulse into warm, stratified, still water",
         "everything above, at the worst hour of the year for it",
         "no instrument has a time axis this short", "none"),
    ]
    n_of = {k: sum(1 for r in routes if r[3] == k) for k in ("well", "partly", "blind", "none")}
    fb = []
    fa = fb.append
    fa(CL("C-PG-2-STOICH", "**Oxygen is not the consequence. It is the one consequence that "
          f"has a stoichiometry.** The paragraph above prices the flush in grams of {C('O2')} "
          "per gram because that is the channel the ledger can be argued in. That is a "
          "property of the instrument, not of the event. What actually leaves the basin acts "
          "along several routes at once, and the oxygen one is simply the only one anybody "
          "can carry through an arithmetic.\n"))
    fa(CL("C-PG-2-SUBSTANCE", "**Start with the route that needs no chain at all: it is the "
          "substance.** What comes out is fat, solids, fibre, wipes and the sediment they "
          "were lying in. A person who meets that in the water is not encountering a "
          "downstream effect of an oxygen deficit — they are encountering the discharge, "
          "diluted. **That is *fedtemøg* in the sense the word is actually used**, and on "
          "this page's own count it is one of the three public words with no instrument "
          "behind it.\n"))
    fa(CL("C-PG-2-REST", "The rest, with what each acts on and whether anything in Denmark "
          "records it:\n"))
    fa("| The flush also delivers | Which acts on | Recorded by |")
    fa("|---|---|---|")
    for a_, b_, c_, _k in routes:
        fa(f"| {a_} | {b_} | {c_} |")
    fa("")
    fa(CL("C-PG-2-THIRDCOL", f"Read down the third column. **{WORD[n_of['well']].capitalize()} "
          f"route is measured well, {WORD[n_of['partly']]} partly, {WORD[n_of['blind']]} by "
          "records that exist but cannot see an event, and "
          f"{WORD[n_of['none']]} not at all** — and the ones not recorded at all include both "
          "the direct human encounter and the kill. An annual nitrogen ledger sees none of "
          "them. An oxygen series sees the first and reports it as a monthly value at a "
          "station that may be kilometres away.\n"))
    fa(CL("C-PG-2-NOTSAY", "*What this does not say:* that any of these happened at any "
          "Danish overflow. Nothing here quantifies a single event, and several rows are "
          "mechanisms rather than findings. What it establishes is narrower and harder to "
          "argue with — **the event is wider than the instrument**, so a defence of the "
          "current framing that rests on the oxygen record has already discarded most of the "
          "question.\n"))
    a(fold("The flush does more than take oxygen — the other routes it takes, and how many "
           "of them anything in Denmark records", "\n".join(fb)))
    a(CL("C-PG-2-NOTBASIN", "*Does not establish:* what any particular basin holds. Nobody "
         "in this project has measured basin sediment, and the composition would be "
         "site-specific if they had. What the arithmetic does establish is that a delayed, "
         "concentrated, reduced discharge cannot be priced by the quantity the accounting "
         "measures — which is the same failure as [the annual average](RESIDUAL.md), one "
         "storey down.\n"))
    a(CL("C-PG-2-OUTLET", "**If the treated effluent is still not good enough for the water "
         "it enters, that is an argument about where the outlet is, not about how many "
         "basins there are.** A plant whose effluent a bay cannot absorb should discharge "
         "into a water that can hold it and work on it — the same terminal-water logic, "
         "applied to the small stream instead of the large one.\n"))
    a(CL("C-PG-2-RAINSTREAM", "**The stream that actually needs somewhere to go is the "
         "rain.** It is the larger one, it arrives all at once, and what it carries is the "
         "city's surface: road sediment, metals, tyre particles — a major component of the "
         "pollutants in urban stormwater runoff — microplastics, road salt, litter, and the "
         "flush of everything that settled on it since the last rain. That is a different "
         "problem from sewage and it wants a different receiver: shallow, wide, vegetated, "
         "and able to keep what it settles.\n"))
    a(CL("C-PG-2-UNCONNECTED", "**And it must stay unconnected.** The proposal below "
         "receives rain and never sewage. A break, a blockage or a misconnection is the one "
         "path by which foul water could reach it, so the separation has to be **physical "
         "rather than administrative**: no cross-connection to open in an emergency, and a "
         "fault that fails toward the plant or toward holding rather than toward the "
         "polder. A receiving water that can be used as an overflow once will be used as one "
         "again.\n"))
    a(CL("C-PG-2-PLUMBING", "**A note on household plumbing, and an argument against leaving "
         "it to the household.** Once there are two pipes in the street a building can put "
         "a fixture on either one, and greywater — a shower, a washing machine, a sink — "
         "would sit well on the rain line, where the worst thing in it is soap. Every litre "
         "moved that way is a litre the plant does not treat, and it makes the foul flow "
         "smaller and steadier. It should still be a **fixture standard rather than a "
         "householder's discretion**: a pipe whose contents depend on who owns the building "
         "is a pipe nobody can characterise. If greywater is admitted it is admitted by rule "
         "and for named fixtures, and the wetland is then sized knowing it has surfactants "
         "to deal with.\n"))
    a(CL("C-PG-2-TERMINAL", "The alternative is therefore a terminal water for the rain: an "
         "outlet that is a lake, a watercourse, a wetland or a quarry rather than the "
         "bay.\n"))
    a("![Køge Bugt: what drains into it](koege_bugt_system.svg)\n")
    a("*Real: coastline, combined-sewer catchments, overflow structures, treatment "
      "plants, and the chalk quarry discussed below. Green and dashed: proposal, not "
      "data.*\n")
    kk = mon["karlstrup_kalkgrav"]
    st = kk["official_status"]
    a(CL("C-PG-2-KARL", "**Case one: a flooded chalk quarry.** Karlstrup Kalkgrav, in "
         f"{kk['water_body']['municipality']}, is a lake whose water level is held **four "
         "metres below the level of Køge Bugt** by a pump house that removes about "
         f"**{kk['physical_setting']['pumped_to_sea_m3_per_year']:,.0f} m³ a year** into the "
         "bay. As hydraulic geometry it looks close to ideal: a deep hole below sea level, "
         "next to the shore, with the pumping installed.\n"))
    a(CL("C-PG-2-WRONG", "**It is the wrong site.**\n"))
    fb = []
    fa = fb.append
    fa(CL("C-PG-2-CLEAREST", "The encyclopedia calls it the clearest lake on Zealand, "
          "without a citation or a year for the claim. A resident who knows the place "
          "reports algal growth, an odour, a declining fishery where there had been a "
          "fishing culture, and accumulated plastic waste.\n"))
    fa(CL("C-PG-2-WHATWOULD", "So the useful question is not whether the lake is clean. It "
          "is **what would have told us either way**, and the answer is close to "
          "nothing:\n"))
    fa("| | |")
    fa("|---|---|")
    fa(f"| Registered as | {kk['water_body']['registered_as']} "
       f"({kk['water_body']['id']}), {kk['water_body']['area_km2']} km², "
       f"catchment {kk['water_body']['catchment']} |")
    fa(f"| Ecological status | **{st['ecological_status']}** — assessed on the "
       "phytoplankton element only, from chlorophyll |")
    fa(f"| Chemical status | **{st['chemical_status']}** |")
    fa(f"| Data window | **{st['data_window']}** |")
    fa("| Bathing-water sampling | none — it is not a designated bathing water, and the "
       "nearest designated ones are all coastal |")
    fa("| Litter, plastic, odour, fish kills | **not monitored by anything this project "
       "has profiled** |")
    fa("")
    fa(CL("C-PG-2-ONENUMBER", "A lake carrying one number, from a chlorophyll series that "
          "ended around 2018, with chemical status never determined and no instrument at "
          "all for the things the resident describes. That is the same failure this project "
          "keeps finding: the condition people can smell is the condition nothing "
          "measures.\n"))
    a(fold("The evaluation — is the lake actually clean? Nothing published can settle "
           "it, and this is everything that was checked", "\n".join(fb)))
    a(CL("C-PG-2-DEEP", "And there is a better reason to reject the site, which does not "
         "depend on how clean it is now. The lake is "
         f"{kk['physical_setting']['depth_m']:.0f} m deep with **poor circulation** — the "
         "water just under the surface is cold even when the surface is warm. That is the "
         "configuration that stratifies and goes anoxic under nutrient load. Directing "
         "stormwater into it would reproduce Køge Bugt in miniature, in fresh water, just "
         "inland. **A deep, still hole is a bad treatment basin.** What treatment wants is "
         "the opposite: shallow, wide, and vegetated.\n"))

    # ---- Vestamager
    a("#### Case two: Vestamager, which is the right shape\n")
    a(CL("C-PG-2-VEST", "Behind the Amager dyke is a polder. A law to embank Kalvebodstrand "
         "was passed in 1939, the work was done during the Second World War, and about "
         f"**{VEST/100:.0f} km²** was embanked. Two pump stations keep it dry. It is "
         "Kalvebod Fælled, part of Naturpark Amager.\n"))
    a(CL("C-PG-2-RIGHTSHAPE", "Everything the quarry only seemed to offer is actually "
         "there: the polder is already pumped, fed by gravity from the island above it, and "
         "wet, low-lying and open — which is the shape settling and uptake want.\n"))
    fb = []
    fa = fb.append
    fa("| | |")
    fa("|---|---|")
    fa(f"| Area | ~{VEST:,.0f} ha, held below sea level |")
    fa("| Hydraulics | already a pumped polder — two pump stations keep it dry |")
    fa("| Feed | gravity, from an island that sits above it |")
    fa("| Shape | wet and low-vegetated — what settling and uptake want |")
    fa("")
    fa(CL("C-PG-2-AMAGERSHARE", f"**And Amager is {am/(am+ml)*100:.0f}% of the problem.** "
          "Splitting Copenhagen's combined-sewered impervious area by island:\n"))
    fa("| | Impervious hectares on the combined system |")
    fa("|---|---:|")
    fa(f"| **Amager** — upstream of the polder, no harbour to cross | **{am:,.0f} ha "
       f"({am/(am+ml)*100:.0f}%)** |")
    fa(f"| Mainland Copenhagen | {ml:,.0f} ha ({ml/(am+ml)*100:.0f}%) |")
    fa("")
    fa(CL("C-PG-2-SIZING", "Stormwater treatment wetlands are sized here at the stated "
          "conventions — a few per cent of the impervious area draining to them. For "
          "Amager's share that is:\n"))
    fa("| Sizing | Treatment area | Share of Vestamager |")
    fa("|---|---:|---:|")
    sizes = [(P("pond_size_lean"), " — a lean wet pond"), (P("pond_size_b"), ""),
             (P("pond_size_c"), ""), (P("pond_size_generous"), " — generous, wetland-type")]
    for f_, lbl in sizes:
        fa(f"| {f_*100:.0f}%{lbl} | {am*f_:,.0f} ha | **{am*f_/VEST*100:.1f}%** |")
    fa("")
    a(fold(f"The evaluation — the polder's own numbers, Amager's {am/(am+ml)*100:.0f}% "
           "share of the combined-sewered city, and what a wetland for it would need",
           "\n".join(fb)))
    need_lo, need_hi = am * sizes[0][0], am * sizes[-1][0]
    quarry_ha = kk["water_body"]["area_km2"] * 100
    a(CL("C-PG-2-POLDERFIT", f"**Between {need_lo/VEST*100:.1f}% and {need_hi/VEST*100:.1f}% "
         "of the polder would do it.** That is the difference between this and the quarry. "
         f"By surface, which is what settling needs, the quarry is {need_lo/quarry_ha:.0f} to "
         f"{need_hi/quarry_ha:.0f} times too small and the wrong shape; the polder is "
         f"{VEST/need_hi:.0f} to {VEST/need_lo:.0f} times larger than needed and the right "
         "shape.\n"))
    if "Amager" in F["assisted_sheets"]:
        a(CL("C-PG-2-EVIDENCE", "*And the evidence exists.* Amager was one of the "
             f"{fsh['assisted']} sheets that never registered automatically; it has been "
             "placed from resident-reported control points, so **the island this section "
             "proposes to drain has its modelled flood paths in the analysis**.\n"))
    a("#### The objections, which are real\n")
    for cid, h, t in [
        ("C-PG-2-OBJ1", "A bird reserve.",
         "The south-western part, around Klydesøen, is a bird reserve with no public "
         "access. That is a binding constraint on siting — though not automatically an "
         "argument against, because a shallow treatment wetland is wader habitat, and "
         "waders already favour the polder's wet, low ground. The tension is about which "
         "hectares, not whether."),
        ("C-PG-2-OBJ2", "Contaminant banking.",
         "This is the serious one. Everything the treatment removes accumulates in the "
         "sediment, and accumulating it inside a bird reserve puts it into a food chain. "
         "Treatment cells would have to sit outside the reserve, be lined, and be dredged "
         "on a schedule that is actually kept. A pond that is never dredged becomes the "
         "thing it was built to prevent."),
        ("C-PG-2-OBJ3", f"It only serves {am/(am+ml)*100:.0f}% of the city.",
         f"The mainland's {ml:,.0f} ha cannot reach the polder by gravity — the harbour "
         "is in the way. This is not the answer for Copenhagen. It is a good answer for "
         f"Amager, and Amager is where {am/(am+ml)*100:.0f}% of the combined-sewered "
         "surface is."),
        ("C-PG-2-OBJ4", "Groundwater and the polder's own water balance.",
         "Adding a large managed inflow to a basin whose level is maintained by pumping "
         "changes the pumping duty and the salinity gradient. Neither is exotic; both "
         "have to be modelled before anyone draws a line on a map."),
    ]:
        a("- " + CL(cid, f"**{h}** {t}"))
    a("")
    a(CL("C-PG-2-WHATIS", "*What this is:* the case that the site meets the physical "
         "criteria, which is a much weaker claim than that it should be built. Nobody has "
         "run the numbers, and the objections above are where the argument would actually "
         "be won or lost.\n"))
    a("#### The specification, generalised\n")
    a(CL("C-PG-2-SPEC", "What the two cases together establish is the shopping list:\n"))
    for t in [
        "**shallow and wide, not deep and still** — settling and plant uptake need "
        "surface area, and a deep unmixed basin stratifies and goes anoxic",
        "**below the contributing catchment**, so the feed is gravity",
        "**not hydraulically connected to the sea**, so there is no threshold at which "
        "it discharges",
        f"**an area of order {sizes[0][0]*100:.0f}–{sizes[-1][0]*100:.0f}% of the "
        "impervious catchment**",
        "**and a dredging obligation written down before it is built**",
    ]:
        a(f"- {t}")
    a("")
    a(CL("C-PG-2-SCREEN", "Screening Denmark's extraction areas and drained lowlands against "
         "that list is a desk exercise, and this project has not done it.\n"))
    a(CL("C-PG-2-GROUNDWATER", "*The standing objection.* Anything infiltrating toward an "
         "aquifer is a groundwater question. A terminal water has to be lined, or sit where "
         "no aquifer is drawn on, or discharge to a surface watercourse after treatment. "
         "That narrows the site list. It does not empty it.\n\n"))
    # ---- 3
    a("### 3. Light treatment at high throughput, which is a different machine\n")
    a(CL("C-PG-3-NOTRAW", "Separating rainwater does not mean discharging it raw. Tyre "
         "particles are a major component of the pollutants in urban stormwater runoff, and "
         "simply giving that water its own pipe would move the problem rather than solve "
         "it.\n"))
    a(CL("C-PG-3-LIGHTER", "But stormwater needs a **lighter machine** than sewage does, and "
         "the reason is what it carries:\n"))
    a("| | Sewage | Stormwater |")
    a("|---|---|---|")
    a(f"| Volume (national, rain-dependent) | {vol['combined_overflow_water']/1e6:,.0f} "
      f"million m³/yr overflow | {vol['separate_stormwater_discharged']/1e6:,.0f} "
      "million m³/yr |")
    a(f"| Strength (COD) | {tt['reference_raw_sewage']['COD']:,.0f} mg/l | "
      f"{tt['separate_stormwater']['COD']:,.0f} mg/l |")
    a(f"| Nitrogen | {tt['reference_raw_sewage']['Tot-N']:,.0f} mg/l | "
      f"{tt['separate_stormwater']['Tot-N']:,.0f} mg/l |")
    a("")
    a(CL("C-PG-3-SPLIT", "**What decides how much a pond can do is how much of each "
         "pollutant rides on particles, which settle, and how much is dissolved, which does "
         "not.** For tyre particles and their chemicals, an open review finds removal "
         "expected only in systems that take out fine solids or dissolved pollutants — and "
         "that soil- and wetland-based systems would likely outperform many retention-pond "
         "designs ([Mayer et al., "
         "2024](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11214769/)).\n"))
    a(CL("C-PG-3-PASSIVE", "A treatment train of gross-pollutant trap, forebay, wet pond and "
         "filter strip has no aeration basin, no sludge recirculation, no energy input, and "
         "no process to upset. Its throughput is limited by area, and on the polder of "
         "section 2 area is what there is.\n"))
    a(CL("C-PG-3-UNREAD", "**How much a pond actually keeps is site-specific, and the figures "
         "that would say it could not be read.** The Danish and Nordic removal figures this "
         "page used to print are not in any open copy this project could reach, so they are "
         "not printed. What could be read is narrower: pond sediment is a key sink for "
         "microplastics, and a transient one ([Corcoran et al., "
         "2025](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12547433/)); and for tyre "
         "particles, the review above expects soil- and wetland-based systems to do "
         "better.\n"))
    # The impression is embedded rather than only linked, because the objection this
    # section keeps meeting is not an argument, it is a picture: sewage ponds in a
    # bird reserve. The frame is hidden on a narrow screen by the reader's CSS, and
    # the link below it is what a phone gets - and what GitHub gets, since it strips
    # the iframe and keeps the link.
    a('<div class="embedfig">\n'
      '<iframe src="rainwater_river.html?embed=1" loading="lazy" '
      'title="An artist’s impression: the rain above ground, and the reed cells '
      'that settle what the streets gave it"></iframe>\n'
      '</div>\n')
    a("> " + CL("C-PG-3-IMPRESSION", "**[What it would look like from the bank "
         "→](rainwater_river.html)** — the same arrangement at eye level, drawn because "
         "*light treatment on Amager* is easy to hear as sewage ponds in a bird reserve. It "
         "is not that. What runs in it is rain, the sediment the rain carries, and — if what "
         "people put down a drain is dealt with at source — the water from a shower or a "
         "washing machine. The toilet and the kitchen are in a different pipe, and that "
         "pipe is drawn too.\n"))
    a(CL("C-PG-3-LIMITS", "Two honest limits. A pond does not remove what does not settle — "
         "chloride from road salt, dissolved metals, PFAS — so it is a complement to source "
         "control and not a substitute for it. And its performance depends on the sediment "
         "being *removed* periodically rather than left to accumulate: pond sediment is a "
         "transient sink, which is the identical failure mode as the sewer basins. A pond "
         "that is never dredged becomes the thing it was built to prevent.\n"))

    a("#### How big, and the answer is: that depends on whether you store first\n")
    pond = st2["ponds"]
    a(CL("C-PG-3-STOKES", "For what does settle, the size of the machine is set by one "
         "number — how fast a grain falls — and a pond catches what has time to reach the "
         "bottom while the water crosses it. Settling velocity goes with the **square** of "
         "grain size, so the pond that catches sand is trivial and the pond that catches "
         f"silt is not. Taking Amager's {amager_ha:,.0f} combined-sewered impervious "
         "hectares as the catchment and Stokes settling in still water at the temperature "
         "`scripts/streams.py` states:\n"))
    a("| Grain | Falls at | Pond area to catch it **at the design hour** | The same "
      "filter **fed steadily all year** |")
    a("|---|---:|---:|---:|")
    for r in pond:
        a(f"| {r['grain_um']} µm | {r['settling_m_per_h']:,.2f} m/h | "
          f"{r['area_ha_at_design_hour']:,.1f} ha | "
          f"{r['area_ha_if_fed_steadily']*1e4:,.0f} m² |")
    a("")
    g20 = [r for r in pond if r['grain_um'] == 20][0]
    a(CL("C-PG-3-STORAGE", "**The two right-hand columns are the same filter, and they "
         f"differ by a factor of about {g20['area_ha_at_design_hour'] / g20['area_ha_if_fed_steadily']:,.0f}.** "
         f"A pond sized to take {fl['design_hour']:.0f} m³/s as it arrives needs "
         f"{g20['area_ha_at_design_hour']:.1f} ha to catch {g20['grain_um']} µm silt. The "
         "same pond, fed at a steady rate with the same water spread over the year, needs "
         f"{g20['area_ha_if_fed_steadily']*1e4:,.0f} m². **So the design variable is not "
         "filter area. It is storage** — somewhere to put the hour so the filter can have "
         "the week. That is the argument for the polder in one line: Vestamager is not "
         f"primarily a treatment area, it is {VEST:,.0f} ha of the thing that makes a small "
         "treatment area work.\n"))
    a(CL("C-PG-3-ROTATION", "It also settles how the ponds are run. Cells in **rotation**, "
         "fed by gravity, with one cell out of service being drained and dredged while the "
         "others take the flow: with *n* cells that costs a factor of `n/(n-1)` in area, "
         "and it is the only way the periodic-removal condition above gets met in practice "
         "rather than in a maintenance plan. A cell that cannot be taken offline will not "
         "be cleaned.\n"))
    a("#### What leaves on a lorry, and how often\n")
    sed = st2["sediment"]
    city_t = sed["t_per_impervious_ha_per_year"] * arch["totals"]["combined"]["ha"]
    city_m3 = sed["m3_per_impervious_ha_per_year"] * arch["totals"]["combined"]["ha"]
    lean_ha = amager_ha * P("pond_size_lean")
    mm_yr = sed["m3_per_impervious_ha_per_year"] * amager_ha / (lean_ha * 1e4) * 1000
    cadence = P('cell_fill_mm') / mm_yr
    a(CL("C-PG-3-LORRY", "The disposal argument in the next section is about a quantity "
         "nobody had sized, so here it is. Rain carries suspended solids at something like "
         f"**{sed['tss_mg_per_l_stated']:.0f} mg/l** off paved surface — a stated convention "
         f"— and a pond is taken to keep **{sed['capture_fraction_stated']*100:.0f}%** of "
         f"them, also stated. On Amager's {amager_ha:,.0f} impervious hectares that is "
         f"**{sed['solids_caught_t_per_year']:,.0f} tonnes a year**, or about "
         f"{sed['solids_caught_m3_per_year']:,.0f} m³ settled in place; across the whole "
         f"combined city, **{city_t:,.0f} tonnes** and {city_m3:,.0f} m³.\n"))
    a(CL("C-PG-3-CADENCE", "**Which sets the cadence, and it is slower than the word "
         f"*dredging* suggests.** Spread over the lean {lean_ha:,.0f} ha sizing from the table "
         f"above, that is **about {mm_yr:.0f} mm a year** of accumulation. A cell reaches "
         f"{P('cell_fill_mm'):.0f} mm in about {cadence:.0f} years. So the rotation is not a "
         "permanent industrial operation in a nature park — it is a cell out of service for "
         "a season, on a cycle measured in years, with the material leaving on ordinary "
         "lorries.\n"))
    a(CL("C-PG-3-LARGER", "**And it is the local end of a much larger question.** Where "
         "those tonnes go is decided by assay rather than by category — deep-prior metals "
         "below a threshold become soil, cadmium and mercury do not, and a novo-chemical has "
         "to be destroyed rather than buried, which is the taxonomy in the next section. "
         "Whether any Danish facility closes its fluorine balance has not been checked here, "
         "which is why [the industry question](#is-this-a-cost-or-is-it-an-industry) is not "
         "a coda to this document but a scheduling constraint on it. This is the quantity "
         f"that would make it concrete: about {city_t:,.0f} tonnes a year, from one city, of "
         "material whose destination nobody has yet had to decide.\n"))
    a(CL("C-PG-3-FLOORS", "*Stated, not measured:* the runoff coefficient, the design hour, "
         "the solids concentration, the capture fraction and Stokes settling in still water. "
         "Real ponds are not still — wind and short-circuiting both cut capture — so these "
         "areas are **floors**, and what a built pond achieves has to be measured. "
         "`scripts/streams.py` writes the arithmetic.\n"))

    a("#### Where the load ends up is a choice, and the sea is the other option\n")
    a(CL("C-PG-3-CHOICE", "The objection that a pond banks contaminants is right, and it is "
         "not an argument against the pond. **The city's surface load settles somewhere in "
         "every version of this**, including the one where nothing is built. Left to the "
         "outfall, it settles on the seabed of the bay it discharges into — which is banking "
         "too, in a basin nobody can drain, with no schedule and no operator.\n"))
    a(CL("C-PG-3-NEXT", "The difference is what happens next. Sediment on a seabed is not at "
         "rest: a storm, a trawl, a propeller or a dredging campaign lifts it back into the "
         f"water, and [OXYGEN.md](OXYGEN.md) prices that route at **{OX('O2_PER_S'):.2f} g "
         f"{C('O2')} per g of sulphide** oxidised on the way up — a demand that needs no "
         "nitrogen and appears in no load ledger. Anoxic sediment also releases the "
         f"iron-bound phosphate it was holding ({R('A2')}). And the metals and particles "
         "that came off the street are then in a food chain instead of in a bucket.\n"))
    a(CL("C-PG-3-OPERATOR", "A pond cell is the same material in a place with an operator, a "
         "schedule and a lorry. That is the whole of the claim — not that treatment makes "
         "the load disappear, but that it decides **where the load accumulates and whether "
         "anyone can lift it out again**. The condition attached is the one in the "
         "objections: a cell that is never dredged is the seabed with a fence around it.\n"))

    # ---- 4
    a("### 4. Where the captured material goes, which the same taxonomy decides\n")
    # The digression about how the menu of chemicals is assembled is structurally
    # load-bearing; it sits behind one line that says what it concludes.
    gly_fold = RD("{read:PG-BENBROOK-2016:15|glyphosate use has risen almost 15-fold since}")
    fb = []
    fa = fb.append
    fa(CL("C-PG-4-MENU0", "One structural point belongs here rather than in the "
          "investigation, because it has no observable in the water and every entry there "
          "has to have one.\n"))
    fa(CL("C-PG-4-MENU1", "**The set of chemicals available to be used is not chosen by "
          "environmental comparison.** It is the output of a registration and "
          "commercialisation process. A compound reaches the market because someone "
          "developed it, took it through registration or approval, and could sell it; once "
          "it is on the market and coupled to a delivery system, the scale at which it is "
          "applied is set by economics. Comparative non-target profile is a constraint on "
          "entry, not the criterion for selection among the entrants.\n"))
    fa(CL("C-PG-4-GLYPHOSATE", "Glyphosate is the clearest illustration. Its last "
          "commercially relevant US patent expired in 2000, but crops engineered to survive "
          "it made herbicide and seed a coupled product, and global use has risen almost "
          f"{gly_fold}-fold since those crops were introduced in 1996. Its target is the "
          "shikimate pathway, which plants share with microorganisms — an antimicrobial mode "
          "of action, at herbicide volumes.\n"))
    fa(CL("C-PG-4-MENU2", "The consequence for anything proposed on this page is concrete: "
          "**a chemical-load problem cannot be fixed by choosing better within a menu you did "
          "not write.** Substitution moves demand to the next compound on the same list, which "
          "was assembled by the same process. That is an argument for acting on total load "
          "and on the approval criteria, not for a better ranking of the existing "
          "options.\n"))
    fa(CL("C-PG-4-MOTIVES", "*What this deliberately does not claim.* Nothing about anyone's "
          "motives, national character or corporate culture. Syngenta, whose main "
          "competitors include BASF and Bayer, is headquartered in Basel and owned by the "
          "Chinese state group Sinochem, so the shorthand that this is an American "
          "arrangement is not accurate, and the structural argument does not need it. Motive "
          "claims are unquantifiable and would make the rest of this project dismissible for "
          "a reason unrelated to its evidence. The claim here is about how a menu is "
          "assembled, and it stands or falls on the approval record.\n"))
    MENU_FOLD = fold("Why the list of chemicals to choose between is not a list of "
                     "the best ones — and why substitution therefore does not fix a "
                     "chemical-load problem", "\n".join(fb))

    a(CL("C-PG-4-INTRO", "The second and third sections both end in the same objection, and "
         "it is a fair one. A treatment wetland concentrates contaminants in its sediment. "
         "Extractive aquaculture concentrates them in biomass. Neither is a solution if the "
         "answer to *and then what* is *we bank it somewhere and hope*.\n"))
    a(CL("C-PG-4-PRINCIPLE", "The answer is that **the disposal route is decided by the same "
         "evolutionary prior that decides the source-control instrument.** It is one "
         "principle, applied twice:\n"))
    a("> " + CL("C-PG-4-RULE", "If life has met the substance before, the question is a "
         "**concentration**: there exists a level below which lifecycles absorb it and it "
         "becomes sediment and then soil. If life has never met it, there is no such level, "
         "and the only terminal option is **destruction**.\n"))
    a("| Captured stream | Prior | Where it goes |")
    a("|---|---|---|")
    for name, prior, route, _kind in disposal():
        a(f"| **{name}** | {prior} | {route} |")
    a("")

    a("#### Why burial works on land and not in the bay\n")
    a(CL("C-PG-4-MARINE", "This is the part that makes the first half of the principle more "
         "than a hope, and it comes out of [SEABED.md](SEABED.md). Metals buried in "
         "**marine** sediment stay only while the bed does. A dead bed crosses the "
         "resuspension threshold several times more often than a living one, so the marine "
         "sink is a store that storms keep re-opening — conditional on exactly the bed "
         "integrity that is failing.\n"))
    a(CL("C-PG-4-LAND", "**Soil does not resuspend under storm waves.** A terrestrial sink "
         "is terminal in a way a marine one is not. Which is a second, independent argument "
         "for intercepting the material on land: not only that it is easier to catch there, "
         "but that once caught, it stays caught.\n"))

    fb = []
    fa = fb.append
    fa(CL("C-PG-4-SPEC", "The other half needs a specification, because burning a "
          "fluorinated compound badly does not destroy it — it can make other fluorinated "
          "compounds. The carbon–fluorine bond is the strongest single bond in organic "
          "chemistry, which is why PFAS persists and why the conditions are demanding. The "
          "US EPA's 2024 interim guidance sets out what is known:\n"))
    fa("| Route | Conditions | Destruction | The catch |")
    fa("|---|---|---|---|")
    for route, cond, eff, catch in destruction():
        fa(f"| {route} | {cond} | **{eff}** | {catch} |")
    fa("")
    c2f6 = RD("{read:PG-WIKI-C2F6:10,000|with an atmospheric lifetime of 10,000 years}")
    c2f6_alt = RD("{read:PG-WIKI-C2F6:500|other sources: 500 years}")
    chf3 = RD("{read:PG-WIKI-CHF3:14,800|is slightly larger at 14,800 for HFC-23}")
    fa(CL("C-PG-4-FAILURE", "So *incinerate it* is not the policy, and neither is a "
          "temperature on a permit. The failure mode is specific and it is not a leak. Below "
          "the destruction condition the parent molecule can disappear — a plant measuring "
          "only the parent reports success — while the fluorine leaves as other species "
          f"through the stack. {C('C2F6')}, one of the species EPA discusses, is an extremely "
          f"stable greenhouse gas: its atmospheric lifetime is given as {c2f6} years, though "
          f"other sources give {c2f6_alt}. {C('CHF3')} warms, over a hundred years, "
          f"{chf3} times as much as the same mass of {C('CO2')}. That is how partial "
          "combustion can turn a water-borne problem into an airborne one.\n"))
    fa("##### The verification is a fluorine mass balance, not a temperature\n")
    fa(CL("C-PG-4-BALANCE", "If the parent compound can vanish while the fluorine escapes, "
          "then measuring the parent compound proves nothing. The test has to follow the "
          "element:\n"))
    fa("| Measure | What it catches |")
    fa("|---|---|")
    for m, w in [
        ("**Total fluorine in**, on the feed", "the denominator. Without it there is no "
         "balance and no claim."),
        ("**Fluoride captured**, in scrubber liquor and residue",
         "the fraction actually mineralised and held."),
        ("**Total organic fluorine in the stack**, not a target-analyte list",
         "the products of incomplete combustion, which by definition are compounds "
         "nobody put on the list."),
        ("**Ultrafine particulate**, with fluorine speciation",
         "a route a stack filter can miss."),
        ("**The unaccounted remainder**", "presumed emitted. This is the number that "
         "matters."),
    ]:
        fa(f"| {m} | {w} |")
    fa("")
    fa(CL("C-PG-4-RELOCATE", "A plant that cannot close its fluorine balance cannot show "
          "that it is destroying PFAS rather than relocating it.\n"))
    fa(CL("C-PG-4-MECHANO", "There is also a route with no stack at all. **Mechanochemical "
          "degradation** — milling the contaminated material in a ball mill — is among the "
          "emerging destruction technologies EPA reviews. No combustion, therefore no flue "
          "gas, therefore no products of incomplete combustion. It is at the scale of "
          "proof-of-concept studies, not of a waste stream.\n"))
    fa(CL("C-PG-4-COLLECT", "Which loops back to why the source-control instrument for PFAS is "
          "a use restriction rather than a treatment requirement. Destruction only works on a "
          "**collected, concentrated** stream. PFAS dispersed through textiles, packaging and "
          "coatings is never collected, so there is nothing to feed the furnace. **The "
          "taxonomy decides not only the disposal route but whether collection is possible at "
          "all** — and where it is not, the only lever left is upstream.\n"))
    fa("##### Does the capacity already exist? Not established.\n")
    fa(CL("C-PG-4-CAPACITY", "Whether any Danish plant meets the destruction condition and "
          "closes a fluorine balance has not been verified here. What would establish it is "
          "the list above: a plant's permitted conditions, and a fluorine mass balance across "
          "it.\n"))
    fa(CL("C-PG-4-ARC", "The same caution applies locally and more sharply. **Amager Bakke**, "
          "the waste incineration plant on Amager, is the obvious thing to point at. Whether "
          "it meets the destruction condition has not been checked, and pointing the flagged "
          "stream at it because it is nearby would be exactly the *roughly burn it* "
          "failure.\n"))
    fa("> " + CL("C-PG-4-ASSUME", "The design consequence: **the destruction branch is the one "
          "part of this programme that must not be built on an assumption.** The other parts "
          "fail toward holding the material; this one fails toward the air.\n"))
    fa("##### And the fluorine is worth money, which is the same measurement\n")
    fa(CL("C-PG-4-FLUORSPAR", "Destroying PFAS properly produces fluoride — captured in the "
          "scrubber as calcium fluoride, for instance. **Fluorspar is on the EU critical raw "
          "materials list.**\n"))
    fa(CL("C-PG-4-ALIGN", "Which produces an unusually clean alignment:\n"))
    for i, t in enumerate([
        "**the proof of destruction and the product are the same measurement.** Fluorine "
        "you can weigh in the residue is fluorine that did not go up the stack. A plant "
        "with a closed balance has both a compliance case and something to sell; a plant "
        "without one has neither, and the absence is visible on the same spreadsheet.",
        "**it makes the failure mode economically legible.** Under a temperature-based "
        "permit, incomplete combustion is invisible and costs the operator nothing. Under a "
        "fluorine balance it shows up as lost product.",
        "**and it makes the facility a service rather than a cost centre.** Destruction "
        "capacity that can prove its balance can be offered to others, and the feedstock is "
        "a waste stream people pay to be rid of. That is the argument that would fund "
        "building the thing properly rather than cheaply.",
    ], 1):
        fa("- " + CL(f"C-PG-4-ALIGN{i}", t))
    fa("")
    fa(CL("C-PG-4-CAVEATS", "*The caveat, because this is the part most likely to be "
          "over-sold.* Recovery as a saleable grade has not been shown here at any scale. And "
          "an economic case for importing waste is an argument that runs away from you very "
          "easily — it is only a good one while the balance is closed and audited, which is "
          "the entire condition.\n"))
    a(fold("Burning a fluorinated compound badly does not destroy it — the "
           "specification that would, the fluorine mass balance that "
           "verifies it, and why this is the one branch that must not be "
           "built on an assumption", "\n".join(fb)))

    avedore = RD("{read:PG-WIKI-AVEDORE:450|Området er på 450 hektar}")
    a("#### The dredged material has somewhere to go, and it is already being asked for\n")
    a(CL("C-PG-4-DREDGE", "A wetland and its forebay have to be dredged, and section 4's "
         "threshold test says what happens next: below a concentration threshold for "
         "metals, the material is soil. The question is where soil is wanted.\n"))
    a(CL("C-PG-4-HOLME", "On this coast, it is wanted now. **Avedøre Holme is "
         f"{avedore} hectares of land embanked in Køge Bugt** in the 1960s, and on 28 January "
         "2025 Hvidovre's council dropped the nine-island *Holmene* proposal in favour of "
         "land reclamation and storm-surge protection — a natural coastline with salt "
         "marsh, continuing the storm-surge protection of Køge Bugt Strandpark further south, "
         "which was built from 1976 to 1979 and opened in 1980.\n"))
    a(CL("C-PG-4-LOOP", "So the loop closes without anyone inventing a use: **a bay that needs "
         "its sediment intercepted, and a coast that needs fill for its own flood defence.** "
         "The material comes out of the treatment train and goes into the dyke.\n"))
    a(CL("C-PG-4-LIMITS", "*Two limits, and the second is firm.* Sediment above the threshold "
         "is not fill — it is a lined-cell problem, and the assay decides, not the "
         "convenience. And **incineration residue is not fill at all.** A reclamation whose "
         "stated purpose is salt marsh and habitat is the last place to test that boundary — "
         "the fill has to clear the threshold on its own merits or go somewhere else.\n"))

    a("#### Deciding which route, in real time\n")
    a(CL("C-PG-4-ROUTE", "The two routes have very different costs, so the branch should be "
         "taken by measurement rather than by policy:\n"))
    a("![Routing the rain by what is in it](routing_logic.svg)\n")
    a(CL("C-PG-4-NODE", "A diversion node needs nothing exotic — turbidity, conductivity and "
         "flow continuously, with a grab sample triggered on threshold. Clean flow takes the "
         "cheap default: gravity to the wetland, settle, take up, dredge on schedule. Flow "
         "that trips the sensor is held for the expensive branch.\n"))
    a(CL("C-PG-4-LATER", "**And the expensive branch can be built later.** The wetland "
         "accumulates; it does not fail suddenly. Sediment concentrations rise over years, "
         "which means the sequence can be: build the wetland, instrument the inflow, and let "
         "the measured accumulation rate decide when — and whether — a heavy-duty facility "
         "is worth building at all. That is the opposite of the usual order, where the "
         "expensive asset is specified first from an assumption.\n"))
    a(CL("C-PG-4-GAP", "The honest gap: **no threshold is set here, because the events are "
         "not measured.** Which returns, as everything here does, to section 7.\n"))

    a("#### What this settles, and what it does not\n")
    a(CL("C-PG-4-SETTLES", "It settles the objection raised against extractive aquaculture "
         "and against treatment wetlands: the harvested material is not an unanswered "
         "question. Organic matter is a fuel, nutrients are a resource, deep-prior metals "
         "are a concentration threshold, and the novel entities are a destruction problem on "
         "a stream small enough to handle.\n"))
    a(CL("C-PG-4-NOTSETTLE", "It does not settle the cost, the logistics, or who pays for "
         f"dredging a pond every {cadence:.0f} years or so. Those are real and they are "
         "ordinary. The point is only that the material has somewhere to go, and that which "
         "somewhere is not a matter of preference — it follows from what the substance "
         "is.\n\n"))

    # ---- 5
    a(CL("C-PG-4-ONEMORE", "**One more thing decides whether any of this is enough, and it is "
         "not in the water.** Every route above chooses where a substance ends up. None of "
         "them chooses which substances exist to be routed — that list is assembled somewhere "
         "else, by a process with no environmental comparison in it, which is why the next "
         "section is about source control rather than about better sorting.\n"))
    a(MENU_FOLD)

    a("### 5. Source control, sorted by what life has met before\n")
    a(CL("C-PG-5-SUBSIDY", "The subsidy–stress argument in [CAUSATION.md](CAUSATION.md) says "
         "nitrogen produces mush rather than meadow because the organisms that would have "
         "used it well are gone. If that is right, the substances that removed them sit "
         "upstream of the nutrient problem, and no amount of nutrient policy reaches "
         "them.\n"))
    a(CL("C-PG-5-SORT", "The useful way to sort those substances is **not by how toxic they "
         "are**, and not by half-life either. It is by whether life has an **evolutionary "
         "prior** for them — and, where it does not, whether the substance *breaks down into "
         "something it does*.\n"))
    a(CL("C-PG-5-TERMINUS", "That second clause is the whole test, because degrading is not "
         "the same as resolving. A novel compound can degrade into another novel compound. "
         "`6PPD` oxidises to `6PPD-quinone`, which is the toxic one. PFAS precursors degrade "
         "into PFCAs and PFSAs, and the chain stops there.\n"))
    a(CL("C-PG-5-CRITERION", "So the criterion is the **terminus**:\n"))
    a("> " + CL("C-PG-5-DEF", "**Novo-chemical**: a substance that is not evolutionarily "
         "primed, whose presence is lasting or chronic, and **whose degradation cascade does "
         "not terminate in something life is primed for.**\n"))
    a(CL("C-PG-5-CLOCK", "Everything else is a transient — a nuisance with a clock on it. A "
         "novo-chemical has no clock.\n"))
    a("| Prior | Where the cascade ends | Adaptation? | Sink? | Instrument |")
    a("|---|---|---|---|---|")
    for tier, term, adapt, sink, instr in [
        ("**Deep** — essential elements (Zn, Cu)", "it is already an element",
         "Yes — transporters, homeostasis", "Burial, while the bed holds",
         "**reduce the flux**"),
        ("**Weak** — no known role (Cd, Hg, Pb)", "element, but Hg methylates",
         "Detoxification only", "Burial, stabilised",
         "**restrict, guard the sediment**"),
        ("**None** (`6PPD-q`)", "**not established here**", "No", "not established",
         "**replace it**"),
        ("**None**, and *never terminates* — a novo-chemical (PFAS)",
         "**PFCAs / PFSAs, and stops there**", "No", "**None**",
         "**reserved use only**"),
    ]:
        a(f"| {tier} | {term} | {adapt} | {sink} | {instr} |")
    a("")
    a(CL("C-PG-5-REACH", "*And where this sits against existing regulation.* Among REACH's "
         "criteria for a substance of very high concern are PBT and vPvB — persistent, "
         "bioaccumulative and toxic, or very persistent and very bioaccumulative. Those are "
         "the right instincts, but they are **thresholds on how long a substance lasts and "
         "how much it accumulates**. The terminus test asks a different question: not how "
         "long a substance lasts, but what it becomes.\n"))
    a(CL("C-PG-5-TIERS", "The four tiers, substance by substance:\n"))
    for tier, rows in chem_tiers():
        a(f"#### {tier}\n")
        for name, source, prior, sink, ask in rows:
            a(f"**{name}**" + (f" — *{source}*" if source else "") + "\n")
            a(f"- **Prior:** {prior}")
            a(f"- **Sink:** {sink}")
            a(f"- **Ask:** {ask}\n")

    a("#### What the law actually asks, and what it does not\n")
    a(CL("C-PG-5-HAZARD", "It is worth being exact about the terminology. **Hazard is the "
         "intrinsic capacity to harm. Risk is that capacity combined with exposure.** Under a "
         "risk-based rule, a substance known to be hazardous is permitted where exposure is "
         "judged low enough, and whether that judgement is right depends on an exposure "
         "estimate — for a substance in wide dispersive use, the kind of estimate the "
         "monitoring this project has profiled is least able to support.\n"))
    a(CL("C-PG-5-NODATA", "REACH's own principle is *no data, no market*: a substance may not "
         "be placed on the European market without registration, and the data are the "
         "registrant's to supply.\n"))
    a("> " + CL("C-PG-5-PROXY", "That is the criterion that matters for this section, because "
         "**persistence is already the regulatory proxy for an absent evolutionary prior.** "
         "*vPvB* is, in effect, the law's way of saying *nothing has evolved to take this "
         "apart*, expressed as a persistence threshold instead of as a claim about "
         "biochemistry. The concept this page has been building is not foreign to European "
         "law; it is present, subordinate, and applied to individual substances rather than "
         "to whether a substance should be ubiquitous.\n"))
    a(CL("C-PG-5-VILLAIN", "It is also worth being accurate about who is being suspected. The "
         "structural argument does not need a villain, and is stronger without one — **and "
         "the belief that European regulation already handles it is the more consequential "
         "error**, because it is the one that stops people asking.\n"))

    a("#### Occupying the niche instead of poisoning it\n")
    a(CL("C-PG-5-NICHE", "There is a route that follows directly from how defence actually "
         "works in nature. If a resident community's main protective function is "
         "**occupancy** — being there, so that something else is not — then the alternative "
         "to killing a pest is **filling the space with something benign first**.\n"))
    a(CL("C-PG-5-DEPLOYED", "It is already deployed. *Wolbachia* introduced into mosquito "
         "populations is used against dengue: the World Mosquito Program released infected "
         "mosquitoes across the Australian city of Townsville from 2014, in a trial called "
         "the strongest evidence yet for the technique, and later in Niterói in Brazil. In "
         "agriculture, *Trichoderma* species are used against plant pathogens, and "
         "formulations of *Bacillus thuringiensis* against insect pests. In soil, take-all "
         "decline in wheat happens by itself: cropped long enough, the disease rises to a "
         "peak and then declines.\n"))
    a(CL("C-PG-5-FOUR", "Four advantages, and they follow from the mechanism rather than from "
         "enthusiasm:\n"))
    a("| | |\n|---|---|")
    a("| **No target to mutate** | A biocide is one molecular target, so it selects "
      "for whoever can change it. Exclusion offers nothing to alter — an incomer "
      "has to out-compete a whole community for resources it also needs. |")
    a("| **Idempotent** | The niche is occupied or it is not. No dose to escalate, "
      "no residue, no gradient for anything to adapt along. |")
    a("| **Self-maintaining** | If the organism establishes, it does not need "
      "reapplying. |")
    a("| **Has a prior by construction** | The agent is something life already "
      "made, so the degradation question that governs every novo-chemical does not "
      "arise. |")
    a(CL("C-PG-5-RECALL", "*And one disadvantage that is worse than any of those is good, so "
         "it has to be said first in any proposal rather than last.* **An introduced "
         "organism cannot be recalled.** A chemical eventually degrades, or at worst persists "
         "unchanged; an organism reproduces, spreads, and evolves after release. The history "
         "of biological control includes introductions that went wrong — the cane toad in "
         "Australia is the best known — and attacks on species other than the target. And "
         f"{R('T9')} applies with full force: pathogen and mutualist are positions rather "
         "than kinds, so an organism benign in the context it was tested in can move along "
         "that spectrum in the context it was released into.\n"))
    a("> " + CL("C-PG-5-SYMMETRY", "Which gives a clean symmetry with this section's other "
         "argument, and it is worth holding both at once. **A novel chemical has no "
         "evolutionary prior and may never degrade. A novel organism has a prior and never "
         "stops.** Both are irreversible, in different ways, and neither irreversibility is a "
         "reason to prefer the other by default. The test for an introduction is therefore "
         "the same shape as the test for a novo-chemical — host specificity demonstrated "
         "rather than assumed, and a bounded release rather than a dispersive one — and "
         "where the candidate is *already resident* and merely being restored to abundance, "
         "as in sediment inoculation, that test is largely already passed.\n"))
    a(CL("C-PG-5-ROLLOUT", "And there is a second reason to do it this way, which has nothing "
         "to do with ecology. **A substitution can be rolled out; a ban can only be "
         "imposed.** Because nobody has to absorb a loss to make it happen, it can be "
         "introduced catchment by catchment on a staggered schedule — which is "
         "simultaneously the intervention and the experiment. Each area is compared against "
         "its own record before it crosses over and against the areas that have not yet "
         "crossed, and no one is withheld from the treatment, only scheduled later. That "
         "design is `X17` in [EXPERIMENTS.md](EXPERIMENTS.md), and it supplies the one thing "
         "the chemical argument lacks: **a counterfactual, at the scale the argument is "
         "made**.\n"))
    a(CL("C-PG-5-AGRONOMY", "The agronomic outcome has to be measured with the same weight as "
         "the marine one, and published whichever way it falls. If biological substitution "
         "costs yield, that is a number this argument has to carry — not something for the "
         "people who farm to discover afterwards.\n"))

    a("#### The instrument for a novo-chemical: reserved use\n")
    a(CL("C-PG-5-ANTIBIOTICS", "The instrument is the one used for antibiotics in livestock, "
         "and for the same reason: selection for resistance grows with volume and ubiquity, "
         "and the use of antibiotics as growth promoters in feed was banned in the European "
         "Union from 2006.\n"))
    a(CL("C-PG-5-TWOPRONG", "A novo-chemical needs the same treatment, and the test has **two "
         "prongs**, not one:\n"))
    a("| | The test | Why it is necessary |")
    a("|---|---|---|")
    a("| **No substitute** | Does anything else do this job? | This is the *essential-use* "
      "idea. It bounds the number of applications. |")
    a("| **Closed system** | Does the material stay somewhere it can be collected and "
      "destroyed at end of life? | This bounds the *dispersal*, and it is the prong "
      "usually left out. |")
    a("")
    t_inc = RD("{read:PG-EPA-PFAS:1,100|higher temperatures >1,100°C4, well mixed, and "
               "adequate residence time}")
    a(CL("C-PG-5-SECONDPRONG", "The second prong is not decoration. Section 4 established "
         "that destruction only works on a **collected, concentrated** stream — "
         f"high-temperature incineration above {t_inc} °C with adequate residence time, or "
         "the emerging routes EPA reviews — and that dispersed material is never collected, "
         "so there is nothing to feed the furnace. **A closed system is the condition that "
         "makes the disposal route exist at all.**\n"))
    a(CL("C-PG-5-SORTS", "Which sorts the applications:\n"))
    a("| Use | No substitute? | Closed system? | |")
    a("|---|---|---|---|")
    for use, sub_, closed, verdict in [
        ("Reactor and chemical-plant seals", "Yes", "Yes — inventoried, serviced, "
         "decommissioned under waste tracking", "**reserved**"),
        ("Medical implants and devices", "Yes", "Yes — explanted and disposed as "
         "clinical waste", "**reserved**"),
        ("Some aerospace and semiconductor process chemistry", "Largely",
         "Yes — closed process, captured waste streams", "**reserved, under review**"),
        ("Firefighting foam", "Contested",
         "No — it is deployed by spraying it on the ground", "**out**"),
        ("Impregnated textiles, food packaging, cosmetics, ski wax",
         "No", "No — it is dispersed by design", "**out**"),
    ]:
        a(f"| {use} | {sub_} | {closed} | {verdict} |")
    a("")
    a(CL("C-PG-5-FOAM", "Note what the second prong catches that the first does not. "
         "Firefighting foam has a serious argument on prong one — it saves lives. It fails "
         "absolutely on prong two, because the method of use *is* dispersal into the ground. "
         "**The volume and the containment are the policy variables; the chemistry is "
         "not.**\n"))
    a(CL("C-PG-5-SO", "So: *banned as a mass-adopted material, reserved for special products "
         "in special facilities.* That is not a compromise between banning and permitting. It "
         "is the formulation that matches what the substance actually is — irreplaceable in a "
         "few places, and irretrievable everywhere else.\n"))
    a("> " + CL("C-PG-5-DEPOSIT", "**And there is a way to arrive at reserved use without a "
         "prohibition.** Price the failure to return rather than the sale: a deposit whose "
         "tail is uncapped makes a substance that never degrades uneconomic to place on the "
         "market, and it does it through a member state's tax code rather than through the "
         "harmonised market. It also turns *free of the substance* from a marketing claim "
         "into a fiscal declaration, which is auditable and punishable. [The externality "
         "expense economy →](EXTERNALITY.md)\n"))
    a("#### Two caveats on the metals, which are this project's own findings\n")
    hz = mon["hazardous_substances"]
    tt_metal = hz["typetal_ug_per_l"]
    zn, cu = tt_metal["Zink"], tt_metal["Kobber"]
    # some typetal cells are text ("<" a detection limit); compare the numeric ones
    numeric = {k: v[0] for k, v in tt_metal.items() if isinstance(v[0], (int, float))}
    biggest = max(numeric, key=numeric.get)
    a(CL("C-PG-5-ZINC", (f"Zinc is the largest metal term in the Danish stormwater typetal — "
                         if biggest == "Zink" else "Zinc is a large metal term in the Danish "
                         "stormwater typetal — ")
         + f"**{zn[0]:,.0f} µg/l** in combined overflow and {zn[1]:,.0f} µg/l in separate "
         f"stormwater, against {cu[0]:,.0f} and {cu[1]:,.0f} for copper, with a maximum "
         f"observed of {zn[2]:,.0f}. The flux is not small.\n"))
    a(CL("C-PG-5-SINK", "**The sink is conditional, and the condition is failing.** Metals "
         "bury in sediment and come back out when it is disturbed. [SEABED.md](SEABED.md) "
         "computes that a dead bed crosses the resuspension threshold several times more "
         "often than a living one. So sediment is not a terminal sink — it is a store that "
         "the same degradation we are worried about keeps re-opening. Burial only counts "
         "while the bed stays intact, which ties metal policy directly to bed integrity and "
         "to trawling. The two cannot be argued separately.\n"))
    a(CL("C-PG-5-PICT", "**And adaptation has a specific price.** Communities do become "
         "metal-tolerant; the phenomenon has a name, pollution-induced community tolerance, "
         "and one of the ways it happens is the replacement of sensitive species by tolerant "
         "ones. *Life adapts* and *the sensitive life is replaced* are then the same "
         "sentence read two ways — which is the mechanism this whole document is about, "
         "arriving from a different direction.\n"))
    a(CL("C-PG-5-NOTPFAS", "None of that makes zinc a PFAS. It makes the metal case an "
         "argument about **rate and community cost**, where the novel-entity case is an "
         "argument about **permanence**. Different arguments, different remedies, and "
         "conflating them weakens both.\n"))

    a("#### The general principle\n")
    a(CL("C-PG-5-PRINCIPLE", "**You cannot filter out what you can decline to manufacture.** A "
         f"substance regulated at the point of discharge has to be caught at "
         f"{hz['applied_to_discharge_points_nationally']:,} outfalls. The same substance "
         "regulated at the point of sale has to be caught once.\n"))
    a(CL("C-PG-5-FURTHEST", "*This remains the section furthest from what this project has "
         "measured.* We have not established that any of these is a binding constraint in "
         "Danish coastal water — only that the mechanisms are well founded, that the "
         "substances are present, and that the monitoring which would settle it rests on "
         f"{hz['stations_combined_overflow'] + hz['stations_separate_stormwater']} stations "
         f"which in Miljøstyrelsen's own words are limiting for *{hz['excludes_heavy_catchments']}* "
         "— the industrial areas and heavily trafficked roads the substances come from. The "
         f"same programme reports {hz['counterpoint']}.\n"))

    # ---- 6
    a("### 6. Rebuild the thing that used to absorb it\n")
    a(CL("C-PG-6-ASSUME", "Load reduction assumes the receiving system will recover once the "
         "pressure comes off. Where the structural life has already gone, that assumption is "
         "doing a lot of unexamined work — a bay with no filter feeders, no eelgrass and a "
         "loose bed does not return to its old state because the load returns to its old "
         "level.\n"))
    a("### Why putting life back is not cosmetic\n")
    a(CL("C-PG-6-MASSBAL", "The obvious case for extractive aquaculture is a mass balance: "
         "mussels and seaweed take nitrogen up, you harvest them, the nitrogen leaves. True, "
         "and the weaker half of the argument. It treats a living bay as a filter, and "
         "predicts a benefit strictly proportional to the area farmed.\n"))
    a(CL("C-PG-6-LIEBIG", "The stronger case is about **who is limited**. Liebig's law says "
         "growth is set by the scarcest resource — and the number of ways an organism can be "
         "stopped is the number of things it requires. Large, slow, structured life needs a "
         "particular substrate, particular partners, particular light, particular chemistry, "
         "a particular season, and years of quiet in which to mature. An opportunist needs "
         "carbon, some nutrient, and water.\n"))
    a(CL("C-PG-6-ASYM", "So the competition is asymmetric, and not because one is fitter. **The "
         "low-requirement organism wins by being harder to stop.** Whatever goes wrong, it is "
         "more likely to have gone wrong for the demanding species than for the undemanding "
         "one, which is why every kind of damage ends in the same kind of community.\n"))
    a(CL("C-PG-6-CAUSE", "Which means a standing meadow or mussel bed is not a *symptom* of a "
         "healthy bay. It is a **cause** of one. It draws the surplus down, shades the water, "
         "filters the plankton, oxygenates and binds the sediment, and shelters the grazers "
         "that crop what is left. It manufactures scarcity for its competitor — it imposes "
         "Liebig limitation on the opportunists.\n"))
    a(CL("C-PG-6-BACKWARDS", "And that is the same fact read backwards. Once the structural "
         "life is gone, nothing imposes the limitation any more, the surplus stays available, "
         "and the fast forms keep it. The state holds itself up, which is exactly why the "
         "load coming off does not bring the bay back.\n"))
    a("> " + CL("C-PG-6-PREDICT", "**The two arguments make different predictions, and the "
         "difference is testable.** Mass balance is linear in area: half the farm removes half "
         "the nitrogen. Imposed limitation is not — below some threshold of cover nothing "
         "changes, and above it the state flips and holds. If restoration turns out to be "
         "linear in area, aquaculture is a filter and should be costed as one. If it is "
         "threshold-shaped, it is a state change, and a small intervention in the right "
         "place is worth more than a large one spread thin.\n"))
    a(CL("C-PG-6-HONESTY", "*The honesty here.* Shifts between a clear-water, plant-dominated "
         "state and a turbid, algae-dominated one are documented in shallow temperate lakes, "
         "with this mechanism behind them. The coastal marine analogue is argued from the "
         "same ecology and is less firmly demonstrated. It is a mechanism with good "
         "foundations, not a measured Danish result, and the experiment that would settle it "
         "— put it back where conditions are said to be adequate, and see whether it holds — "
         "is `X10` in [EXPERIMENTS.md](EXPERIMENTS.md).\n"))
    for cid, t in [
        ("C-PG-6-B1", "**Extractive aquaculture.** Mussels and macroalgae remove nitrogen as "
         "biomass and are harvested rather than left to decay. It is the only intervention on "
         "this list that removes what is already in the water rather than reducing what is "
         "added."),
        ("C-PG-6-B2", "**Eelgrass, where the light allows it.** Uptake, sediment stabilisation "
         "and habitat in one organism. Turbidity is the binding constraint, which links it "
         "directly to the first and third items."),
        ("C-PG-6-B3", "**Leave the bed alone where it is recovering.** A living bed resuspends "
         "several times less often than a dead one ([SEABED.md](SEABED.md)), so bed integrity "
         "is not only a fisheries question — it changes how often the accumulated sulphide "
         "and metals come back into the water."),
        ("C-PG-6-B4", "**Harvest as a use, not a disposal.** Extracted biomass that is too "
         "contaminated for human consumption still has uses where accumulation is acceptable "
         "— which is a question about what we are willing to do with it, not a technical "
         "obstacle."),
    ]:
        a("- " + CL(cid, t))
    a("")
    a(CL("C-PG-6-DISPOSAL", "*The disposal question* — extractive aquaculture concentrates "
         "metals and organic contaminants in the harvest — is answered in section 4, and the "
         "answer splits the harvest rather than the idea. Biomass carrying deep-prior metals "
         "has a threshold below which it re-enters the terrestrial cycle; biomass carrying "
         "cadmium or mercury does not, because those have no prior. So where a harvest goes "
         "has to be settled by assay, before it is scaled, not after.\n"))

    # ---- 7
    a("### 7. Measure the six things that would settle the argument\n")
    a(CL("C-PG-7-INTRO", "This is first in priority and last in the list because it is the "
         "least satisfying. Everything above is contestable, and it is contestable because "
         "the measurements that would resolve it were never taken:\n"))
    a("| Measure | Cost | What it settles |")
    a("|---|---|---|")
    for m, c, w in [
        (f"Flow-proportional sampling at the {rb['top_one_pct_n']} largest overflow "
         "structures",
         "weeks",
         f"Whether load is as concentrated as volume is. {rb['top_one_pct_n']} of "
         f"{rb['with_volume']:,} structures hold {rb['top_one_pct_share_pct']:.0f}% of "
         f"recorded storage; if load follows, much of the problem has "
         f"{rb['top_one_pct_n']} addresses."),
        ("Fat, oil, grease and total organic carbon added to the determinands", "trivial",
         "Whether the material the shore is named after is even in the discharge."),
        ("Autumn benthic sampling at existing stations", "one survey season",
         "The depth of the annual die-off, which the spring sampling window does not see."),
        ("Fixed coastal cameras with a monthly index, year-round", "negligible",
         "Whether fedtemøg has the season everyone assumes. Currently unfalsifiable in "
         "either direction."),
        ("Iltsvind extent regressed on load, wind-work and temperature", "desk work",
         "Whether the extremes track load at all."),
        ("A screen of disused extraction sites against the criteria in item 2",
         "a desk week",
         "Whether terminal storage is available at all, before anyone argues about "
         "whether it is desirable."),
    ]:
        a(f"| {m} | **{c}** | {w} |")
    a("")

    # ================================================================ ORDER
    a("## The order of operations\n")
    a(CL("C-PG-O-SPLIT", "The interventions above split by timescale, and the split is the "
         "argument for what to do this year:\n"))
    a("| | Timescale |")
    a("|---|---|")
    for t, s_ in [
        ("Measure the tail; publish event-level flow", "weeks"),
        ("Empty basins before the season rather than letting flow scour them", "months"),
        ("Enforce grease separation at source", "months"),
        ("Screen extraction sites for terminal storage", "months"),
        ("Connect everyday rain to the existing surface network", "years"),
        ("Build the missing corridors and their treatment ponds", "years"),
        ("Product restrictions through REACH", "years — and see below, because that row is "
         "at the wrong level"),
        ("Genuine network separation",
         f"decades — {F['combined_catchments']['planned_to_separate']} of "
         f"{F['combined_catchments']['n']} combined catchments are planned for it"),
    ]:
        a(f"| {t} | **{s_}** |")
    a("")
    a("#### The REACH row is at the wrong level, and that is a structural point\n")
    a(CL("C-PG-O-REACHLEVEL", "A restriction under REACH is a decision about **market "
         "access**, taken once, for the whole single market. It is the right instrument for "
         "the thing it does and it is the only row in that table nobody local can start. "
         "Which is worth saying plainly, because the rest of this document argues that acting "
         "in different places in different ways is how anything gets learned, and here is an "
         "instrument built to make that impossible on purpose: **a single market is a market "
         "where the same products are available everywhere, which is the definition of no "
         "contrast.**\n"))
    a(CL("C-PG-O-LEVELS", "But *banning a product from the market* and *refusing to buy or "
         "permit it* are different acts, and only the first is harmonised. What is left to "
         "the lower levels is not nothing:\n"))
    a("| Level | Cannot | Can |")
    a("|---|---|---|")
    for lvl, cannot, can in [
        ("A household", "affect what is sold",
         "not buy it — which is the whole of the greywater argument in section 2: "
         "what goes down the drain is chosen at the point of purchase"),
        ("A city", "ban a product from its shops",
         "refuse it in its own procurement, forbid its use on land it owns, and "
         "attach conditions to leases, permits and contracts"),
        ("A region or a utility", "override an EU authorisation",
         "make use conditions in discharge permits and abstraction-zone rules"),
        ("A member state", "unilaterally close its market",
         "tax, restrict a *use*, and apply for a derogation or safeguard"),
    ]:
        a(f"| **{lvl}** | {cannot} | {can} |")
    a("")
    a(CL("C-PG-O-LOCAL", "**So the achievable local instrument is a use and purchase "
         "restriction, not a ban** — and it happens to be the one that produces the "
         "counterfactual. A municipality that stops buying a compound, on a date, with the "
         "date written down, has created exactly the contrast that [`X17`](EXPERIMENTS.md) "
         "needs.\n"))
    a(CL("C-PG-O-BRITTLE", "The brittleness is worth naming because it is systemic rather "
         "than particular. **Harmonisation puts the decision at the slowest level and removes "
         "the variation that would inform it**, and the two failures compound: the safeguard "
         "route exists but demands evidence of harm to a standard that is hard to reach "
         "precisely because nobody was allowed to vary the treatment. That circle — *no "
         "derogation without evidence, no evidence without a derogation* — is the same shape "
         "as the nutrient argument on this page, where the contest was never run. It is an "
         "argument for keeping the use and procurement levers deliberately open at every "
         "level below the market, not for leaving the EU's, which does the one thing no city "
         "can.\n"))
    a(CL("C-PG-O-NOTLEGAL", "*What this does not claim.* This project has not read the case "
         "law, and the boundary between a lawful national use restriction and an unlawful "
         "barrier to trade is exactly where the arguing happens. The point stands at the "
         "level of design rather than of legal advice: **the levers that survive "
         "harmonisation are purchase, permission and use, and those are the levers that make "
         "places differ.**\n"))
    a("> " + CL("C-PG-O-FISCAL", "There is a fourth lever of that kind, and it is fiscal "
         "rather than prohibitive: a levy that behaves as a **deposit with an uncapped "
         "tail**, keyed to what a substance does when it disperses, and wrapped in a lease so "
         "that somebody still owns the thing. It is set nationally, it is border-adjustable, "
         "and it prices non-return rather than banning sale — which is why it survives "
         "harmonisation. [The externality expense economy →](EXTERNALITY.md)\n"))
    a(CL("C-PG-O-UNCOMF", "Which produces an uncomfortable conclusion for everyone. The "
         "people who want urgent action have to accept that the physical fix is a "
         "generational programme. The people who want to wait for better evidence have to "
         "accept that the evidence is cheap and has not been gathered.\n"))
    a(CL("C-PG-O-YEAR", "**Is it solvable in a year?** Not the infrastructure. But the "
         "*measurement* is a season's work, and the *operating* changes — basin emptying, "
         "grease enforcement, release timing — are a year's work and would act on exactly the "
         "pulsed, threshold-triggered discharge that the annual accounting is blind to. If "
         "the concentration in the register carries through to load, then a year of "
         "operational change on a few dozen structures is not a small intervention at all. "
         "Nobody knows whether it does, because nobody has measured it. That is the single "
         "most actionable sentence in this document.\n"))

    # ================================================================ INDUSTRY
    a("## Is this a cost, or is it an industry?\n")
    a(CL("C-PG-I-COST", "The programme above reads as expenditure. It is worth asking whether "
         "it is the same shape as green energy was — a cost centre that turned out to be a "
         "sector, and grew because the problem did.\n"))
    tm = RD("{read:PG-WIKI-3M:10.3|3M reached an agreement to pay a $10.3bn settlement}")
    a("### The demand signal is liability, not subsidy — which is stronger\n")
    a(CL("C-PG-I-SUBSIDY", "Green energy needed a subsidy because it was selling a commodity "
         "that already had a price, and selling it dearer. Clean-up sells the absence of a "
         "harm, which has no price at all until somebody is made to pay for it. That is "
         "normally the fatal weakness of the sector.\n"))
    a(CL("C-PG-I-PFAS", "For PFAS it has stopped being true. In 2023 `3M` agreed to pay "
         f"**USD {tm}bn** to settle lawsuits by US public water systems over PFAS "
         "contamination.\n"))
    a(CL("C-PG-I-DURABLE", "And liability is a more durable signal than a subsidy, because "
         "it does not depend on a government keeping its nerve. It depends on courts.\n"))
    a("### The third demand curve, which is the one that matters\n")
    a(CL("C-PG-I-THIRD", "Liability demand is real and it is bounded — by what courts award, "
         "and by settlement deadlines that can be missed. There is a third kind, and it does "
         "not behave like a market at all.\n"))
    a(CL("C-PG-I-COUSINS", "PFAS is already in the rain. Cousins and colleagues "
         "(*Environmental Science & Technology*, 2022) compared four perfluoroalkyl acids — "
         "PFOA, PFOS, PFHxS, PFNA — in rainwater, soil and surface water against guideline "
         "levels, and concluded that *the global spread of these four in the atmosphere has "
         "led to the planetary boundary for chemical pollution being exceeded*.\n"))
    a(CL("C-PG-I-CAVEAT", "*The caveat this project owes its own standards.* Whether a "
         "concentration exceeds a boundary depends on where the guideline was set, and "
         "guidelines move. The paper itself could not be read here, only the sentence quoted "
         "from it; its detail is not repeated on this page.\n"))
    a(CL("C-PG-I-THRESHOLD", "What follows is an economic point rather than a toxicological "
         "one. A pollutant that is globally distributed, that accumulates, and whose effects "
         "propagate through food webs in ways nobody can currently bound, carries a "
         "**threshold risk**: a level at which some function — reproduction in a taxon, a "
         "fishery, a drinking water source — stops working. Nobody knows where that level "
         "is. The relevant feature is what happens to demand if it is reached:\n"))
    a("| Demand type | Set by | Bounded by |")
    a("|---|---|---|")
    a("| **Elastic** — green energy | the price of the commodity it replaces | the "
      "commodity price |")
    a("| **Liability** — PFAS now | courts and settlements | what is awarded |")
    a("| **Threshold** — PFAS if a function fails | nothing | **nothing** |")
    a("")
    a(CL("C-PG-I-ANYCOST", "Under the third, willingness to pay stops being a variable. That "
         "is the *any cost* case.\n"))
    a("#### Which creates an awkward asymmetry\n")
    a(CL("C-PG-I-CAPACITY", "**Capacity cannot be built at the moment it is needed.** "
         "Permitting and constructing high-temperature destruction takes years. If the "
         "threshold arrives, the capacity that exists is the capacity someone built "
         "beforehand, and the rest is a queue.\n"))
    a(CL("C-PG-I-AHEAD", "That is an argument for building ahead of demonstrated need. It "
         "also collides head-on with the moral hazard below, and the collision has a "
         "resolution: **size the capacity to the legacy stock, not to a projected flow.** "
         "What is already emitted is finite, already in the environment, and needs "
         "processing whether or not another gram is ever manufactured. It is a large enough "
         "job to justify serious capacity without requiring the production to continue.\n"))
    a(CL("C-PG-I-PROCURE", "And there is a second reason to move early that has nothing to "
         "do with cost. **Inelastic demand under crisis conditions produces bad "
         "procurement.** Things get deployed at scale because they are available, not "
         "because they were verified. The value of settling the fluorine mass balance "
         "standard now, calmly, is that when the hurry comes there is a method that has been "
         "checked, rather than whichever one sells fastest.\n"))
    a(CL("C-PG-I-STRONGEST", "That, rather than any market forecast, is the strongest reason "
         "to treat this as an industry now: **not because it will be cheaper, but because a "
         "verified method is only buildable while there is still time to verify it.**\n"))
    a("### Where the analogy breaks: two different cost curves\n")
    a(CL("C-PG-I-WRIGHT", "This is the part that decides what to build first, and it is "
         "usually skipped. Solar got cheap on an experience curve — Wright's law, cost "
         "falling a fixed proportion with each doubling of cumulative production — and that "
         "curve belongs to **manufactured, modular, repeated units**. Bespoke construction "
         "can show the opposite: France's nuclear scale-up has been studied as a case of "
         "*negative* learning, getting more expensive with experience.\n"))
    a(CL("C-PG-I-BOTH", "The programme above contains both, and they will behave "
         "differently:\n"))
    a("| | Cost curve | Which parts |")
    a("|---|---|---|")
    a("| **Manufactured and modular** | falls with deployment | diversion sensors, "
      "ion-exchange and regeneration skids, mechanochemical destruction reactors, "
      "monitoring and telemetry, flow-proportional samplers |")
    a("| **Bespoke civil works** | flat or rising | the wetland and its forebay, the "
      "interceptor retrofit, open channels, land reclamation |")
    a("")
    a(CL("C-PG-I-SEQ", "Which produces the same sequencing as section 7 arrived at from a "
         "completely different direction: **do the instrumented, modular things first** — "
         "they are cheap now, they get cheaper, and they are the exportable part. **Do the "
         "civil works last** — they will not get cheaper and they need the measurements to "
         "be specified correctly anyway.\n"))
    a(CL("C-PG-I-EXPORT", "It also says which half is the industry. Nobody exports a Danish "
         "wetland. They export the sensor, the skid, the reactor and the standard.\n"))
    a("### The failure mode this creates, said plainly\n")
    a(CL("C-PG-I-INTEREST", "An industry whose revenue grows with the pollution acquires an "
         "interest in the pollution continuing.\n"))
    a(CL("C-PG-I-CONSTITUENCY", "Build import-fed destruction capacity in Denmark and you "
         "create a domestic constituency whose business case is that PFAS keeps being "
         "manufactured somewhere. That constituency will, in the ordinary way of things, "
         "turn up in the consultation on any restriction.\n"))
    a(CL("C-PG-I-ANTIDOTE", "The antidote is a sequencing condition, and it should be written "
         "down before anything is built:\n"))
    a("> " + CL("C-PG-I-RULE", "**Source restriction leads; destruction capacity follows.** "
         "Capacity sized to the legacy stock and the reserved uses, not to a projected flow. "
         "A destruction industry scaled to a *continuing* input is not a clean-up industry — "
         "it is a disposal service for a business model that should have ended.\n"))
    a(CL("C-PG-I-LEVY", "There is also an instrument that would create the missing demand "
         "directly, rather than waiting for a court to. A purchase levy that is refunded on "
         "return, and billed in full when the object does not come back, puts the price of "
         "unmanaged dispersal above the price of managed destruction **on the day of sale** "
         "— which is the demand curve this section says the sector does not have. It is set "
         "nationally, so it is available where a product ban is not. [The externality "
         "expense economy →](EXTERNALITY.md)\n"))
    a(CL("C-PG-I-FLUORSPARTEST", "The same test distinguishes the good version of the "
         "fluorspar argument from the bad one. Recovering fluorine from a **finite legacy "
         "stock** is mining a waste dump, which is unambiguously good. Recovering it from an "
         "**ongoing production stream** is a subsidy to that production, dressed as "
         "circularity.\n"))

    # ================================================================ ASK
    a("## Who would have to do what\n")
    a(CL("C-PG-ASK", "Each ask follows from a section above:\n"))
    a("| Level | The ask |")
    a("|---|---|")
    for lvl, ask in [
        ("Utility (HOFOR, Biofos, and the bay's others)",
         "Instrument the largest structures. Publish flow, not just event counts. Empty "
         "basins ahead of the season."),
        ("Københavns Kommune",
         "In the next spildevandsplan revision: connect everyday rain to the surface "
         "network already designed, and report the separation figure net of "
         "*Separatkloakeret opland tilkoblet fællessystemet*."),
        ("The bay's municipalities",
         "A joint body whose jurisdiction is the bay. There is currently none, and the "
         "asymmetry between who discharges and who receives is the reason there needs "
         "to be."),
        ("Miljøstyrelsen",
         "Raise the required videnniveau for large structures. Add FOG and TOC to the "
         "determinands. Extend benthic sampling into autumn. Fund a fedtemøg index."),
        ("Denmark, at EU level",
         "Support restricting `6PPD`. Ask for a copper product standard for brake pads. "
         "Treat the PFAS limits as a floor."),
    ]:
        a(f"| **{lvl}** | {ask} |")
    a("")

    # -------------------------------------------------------- WHO CAN CONTRIBUTE
    a("## Who can contribute without being told to\n")
    a(CL("C-PG-C-INTRO", "The table above is a list of asks addressed to people who would "
         "have to be persuaded, funded or compelled. It is the slow half. This is the other "
         "one: **things that can be started by whoever already owns the ground, the asset or "
         "the decision** — no new authority, no statutory change, and in several cases a "
         "revenue rather than a cost.\n"))
    a(CL("C-PG-C-CONTROL", "It matters for a reason beyond willingness. Every entry here "
         "creates a place that did something different, on a date — which is the "
         "[counterfactual](PLACES.md) the whole field is short of. A voluntary contributor is "
         "not a smaller version of a regulated one. It is the control arm.\n"))
    a("| Who | What they can start | What it costs them | What it would show |")
    a("|---|---|---|---|")
    for who, what, cost, show in [
        ("**A farmer with a coastal outfall**",
         "Run the uptake as well as the discharge: mussel lines or macroalgae in front of "
         "the catchment they farm. The nitrogen that left the field is harvested as biomass "
         "rather than argued about",
         "capital and a licence — and it is a **crop**, with feed, fertiliser and food "
         "markets at the end of it",
         "whether extractive aquaculture removes at the loads that actually arrive here, "
         "which section 6 says is the weaker of its two arguments and the one nobody has "
         "measured locally"),
        ("**A landowner upstream**",
         "Take a wet corner out of production and let it be a wetland again",
         "the margin on the worst field on the farm",
         "retention on a real catchment, against its own record"),
        ("**A municipality**",
         "Refuse a compound in its own procurement and on its own ground, and write the date "
         "down. Put everyday rain from one street on the surface route already designed",
         "procurement effort; one street's civil works",
         "the use-restriction lever that survives harmonisation, and a street-scale "
         "before-and-after"),
        ("**A utility**",
         "Instrument one large overflow structure for flow rather than for events, and "
         "publish the series",
         "one sensor package and the will to publish it",
         "whether the concentration argument or the volume argument is right — which is the "
         "largest single uncertainty in this document"),
        ("**A sports club or a school**",
         "Ask what happens to the infill on their own pitch, and put the answer in the "
         "contract at renewal",
         "nothing, at renewal",
         "whether the return obligation in [EXTERNALITY.md](EXTERNALITY.md) is "
         "administratively real or only elegant"),
        ("**A housing association**",
         "Disconnect roofs from the combined sewer into a courtyard basin or a raingarden; "
         "agree a fixture standard for what may go to the rain line",
         "a courtyard's worth of work",
         "the greywater case in section 2, at a scale where the plumbing is one owner's "
         "decision"),
        ("**A boat club**",
         "Mechanical hull cleaning instead of antifouling, for the club's own moorings",
         "a haul-out routine",
         "whether occupying the niche beats poisoning it, on copper, in one harbour"),
        ("**Anyone with a phone**",
         "Record what the shore looked like, dated and located — the "
         "[field log](../viz/log.html) exists for exactly this",
         "an evening",
         "the only route to an instrument for *fedtemøg*, which is one of the three public "
         "words with nothing behind it"),
        ("**Anyone with data access this project lacks**",
         "Run the queries in [IF_YOU_HAVE_THE_DATA.md](IF_YOU_HAVE_THE_DATA.md) and publish "
         "what comes back",
         "an afternoon and a login",
         f"{tri['blocked on a fetch']} of the {tri_total} triaged mechanisms are blocked on "
         "a fetch, not on a thought"),
    ]:
        a(f"| {who} | {what} | {cost} | {show} |")
    a("")
    a(CL("C-PG-C-FARMER", "**The farmer row is the one worth arguing about**, so it is stated "
         "plainly rather than buried in a table. The standard framing sets the farm against "
         "the bay: the farm emits, the bay receives, and the instrument is a restriction on "
         "the farm. Extractive aquaculture is the only intervention in this document that "
         "**puts the removal in the same hands as the emission and pays for it** — the same "
         "business harvests what left the field, and sells it. That does not make the "
         "emission acceptable and it is not an offset scheme; the nitrogen still has to come "
         "down. It makes the remedy a crop rather than a penalty, which is a different "
         "politics — and it is testable on one farm, in one season, by one person who decides "
         "to.\n"))

    # ------------------------------------------------------------ META-SOLUTION
    a("## The last step: stop analysing and try things\n")
    a(CL("C-PG-L-LAST", "**This is the last step of the solution scope and not a shortcut "
         "past it.** Said first, *just try things* is the oldest way to avoid an argument. "
         "Said after the hypotheses have been laid out, the data queued and the field "
         "triaged, it is something else: the recognition that **the observational route to an "
         f"answer may not exist**. {tri['unscoreable']} of the {tri_total} triaged mechanisms "
         "cannot be scored at all, because the deciding measurement has no column anywhere; "
         f"{tri['needs an experiment']} more need an experiment nobody has run. No amount of "
         f"further collection reaches those {tri['unscoreable'] + tri['needs an experiment']}.\n"))
    a(CL("C-PG-L-ENTITLE", "So the entitlement is earned, and the instrument is the one "
         "[PLACES.md](PLACES.md) sets out: **fund trials of solution models, in named places, "
         "with pre-stated outcomes, and let the results decide** — with the anti-delay "
         "conditions attached there, because this argument is also exactly what somebody who "
         "wanted to stall would say.\n"))
    a(CL("C-PG-L-BILL", "What this page adds is the shape of the bill. Two properties make it "
         "affordable to be wrong:\n"))
    a("- " + CL("C-PG-L-REVERSIBLE", "**Non-destructive.** Every trial below is reversible. A "
         "mussel line comes up, a wet corner drains again, a bored pipe is capped, a "
         "monitoring station is unbolted. Nothing here changes a coast irreversibly, which "
         "means the cost of a failed trial is the capital and not the place.") + "\n"
      "- " + CL("C-PG-L-LEGIBLE", "**Instrumented, so the failure is legible.** Trials of "
         "this kind settle nothing when nobody measured beyond what the public could already "
         "see. Sensors are now the cheap part.") + "\n")
    a("### What it would cost to just try it\n")
    a(CL("C-PG-L-STATED", "**Stated, not quoted.** No tender has been sought and none of these "
         "figures came from a supplier. They are order-of-magnitude, in Danish kroner, meant "
         "to be replaced by a utility's real numbers — and published in this form precisely "
         "so that replacing them is easy and the argument survives it.\n"))
    a("| Trial unit | Low | High | What it settles |")
    a("|---|---:|---:|---|")
    sp_m, ha1 = P("manhole_spacing_m"), P("trial_area_ha")
    trials = [
        (f"One bored rain line, shaft to shaft ({sp_m:.0f} m)",
         sp_m * P("bore_rate_lo_kr_m"), sp_m * P("bore_rate_hi_kr_m"),
         "whether the light retrofit works in a real street, at "
         f"{P('bore_rate_lo_kr_m'):,.0f}–{P('bore_rate_hi_kr_m'):,.0f} kr/m"),
        ("Cutting one street's gullies over, with the two-storey shafts",
         P("trial_cutover_lo_kr"), P("trial_cutover_hi_kr"), "the junction detail, under traffic"),
        (f"One shallow treatment cell, {ha1:g} ha, in an existing polder",
         P("trial_cell_lo_kr"), P("trial_cell_hi_kr"), "capture, planting and the dredging cadence"),
        ("Repurposing one spare basin as rain-line buffer",
         P("trial_basin_lo_kr"), P("trial_basin_hi_kr"),
         "whether the retired basins are an asset or a stranded cost"),
        (f"Mussel or macroalgae line, {ha1:g} ha, in front of one catchment",
         P("trial_mussel_lo_kr"), P("trial_mussel_hi_kr"),
         "uptake at the loads that actually arrive — and it is a crop"),
        (f"Rewetting one wet corner, {ha1:g} ha",
         P("trial_wetcorner_lo_kr"), P("trial_wetcorner_hi_kr"),
         "retention on a real catchment against its own record"),
        ("Mechanical hull cleaning for one club's moorings",
         P("trial_hull_lo_kr"), P("trial_hull_hi_kr"),
         "occupying the niche instead of poisoning it, on copper"),
    ]
    for unit, lo, hi, settles in trials:
        a(f"| {unit} | {lo:,.0f} | {hi:,.0f} | {settles} |")
    a("")
    a("> **[Which catchments, and how much of the city →](architecture.html)** — the "
      "architecture view scopes a trial before it is priced: every combined "
      "catchment with its impervious area, its person equivalents and the city's "
      "own plan for it.\n")
    a("### And the documentation, which is now the cheap half\n")
    a(CL("C-PG-L-DOC", "The hardware for one monitoring station, at the same stated order of "
         "magnitude:\n"))
    a("| Instrument | Hardware, per station | What it records |")
    a("|---|---:|---|")
    sensors = [
        ("Multiparameter sonde — oxygen, temperature, conductivity, turbidity", "sonde",
         "the variables the national programme samples monthly, at minutes"),
        ("Logger, telemetry and solar", "logger", "the series arriving without anybody visiting"),
        ("Mount, enclosure, anti-fouling wiper", "mount", "whether it is still reading in August"),
        ("Level and velocity at an overflow structure", "flow",
         "**flow**, which is the single largest uncertainty in this document"),
    ]
    for inst, key, what in sensors:
        a(f"| {inst} | {P('sensor_' + key + '_lo_kr'):,.0f}–"
          f"{P('sensor_' + key + '_hi_kr'):,.0f} | {what} |")
    a("")
    a(CL("C-PG-L-SOFTWARE", "**Software is assumed free.** Not because it is worthless but "
         "because ingestion, storage, alerting and a public page are now a small job for one "
         "competent person with a model to help. This project is itself the evidence: "
         "everything on this site was generated from public data by scripts in one "
         "repository, and the scripts are not the expensive part.\n"))
    a(CL("C-PG-L-RECURRING", "**The recurring cost is not the hardware, and pretending "
         "otherwise is how these schemes die.** A water sensor fouls. It needs cleaning and "
         "recalibration on a schedule, and a series nobody maintained is worse than no series "
         "because it looks like data. Budget the visits, or fit the wiper and budget fewer of "
         "them, but budget them.\n"))
    a("### Which makes the whole proposal one sentence\n")
    t_lo, t_hi = sum(t[1] for t in trials), sum(t[2] for t in trials)
    s_lo = sum(P("sensor_" + k + "_lo_kr") for _, k, _ in sensors)
    s_hi = sum(P("sensor_" + k + "_hi_kr") for _, k, _ in sensors)
    a("> " + CL("C-PG-L-SENTENCE", "**This solution page could be implemented on trial, "
         f"non-destructively, at roughly {t_lo/1e6:.1f}–{t_hi/1e6:.1f} million kroner per "
         "site** — the trial units above, summed — with the effects documented beyond what "
         f"the public can see for **{s_lo:,.0f}–{s_hi:,.0f} kroner of sensing hardware per "
         "site** — and every part of it removable if it fails. That is the price of finding "
         "out.\n"))
    a(CL("C-PG-L-BEFORE", "It would produce before-and-after evidence of a kind the "
         "monitoring does not, and **the expensive half of that design already exists**: "
         f"near-bed oxygen at {SP['coverage']['series_stations']:,} stations is the *before*, "
         "and it is paid for.\n"))

    a("## What would make this wrong\n")
    a(CL("C-PG-W-INTRO", "A programme that cannot be refuted is not a programme. Each of these "
         "would damage the argument above, and each is testable:\n"))
    for cid, t in [
        ("C-PG-W1", "**If flow-proportional sampling at the largest structures finds loads "
         "close to the typetal**, then the concentration argument fails, the overflow term "
         "really is small, and the priority should go back to diffuse sources."),
        ("C-PG-W2", "**If autumn benthic sampling finds no die-off beyond what the spring "
         "survey implies**, the ratchet mechanism is wrong and the spring window was adequate "
         "after all."),
        ("C-PG-W3", "**If a year-round fedtemøg index shows a clean summer peak and a quiet "
         "November**, then the seasonal argument here is wrong and the existing monitoring "
         "windows were correctly placed."),
        ("C-PG-W4", "**If iltsvind extent regresses cleanly on load once weather is "
         "controlled for**, the nitrogen-dominant model is vindicated and the "
         "state-dependence argument is unnecessary."),
        ("C-PG-W5", "**If retention in Køge Bugt disappears on a regional model**, the "
         "accumulation mechanism loses its main quantitative support."),
    ]:
        a("- " + CL(cid, t))
    a("")
    a(CL("C-PG-W-CHECK", "That is the position this document argues from: not that it is "
         "right, but that it can be checked.\n"))

    a("## What we would be asking for, said plainly\n")
    a(CL("C-PG-A-GOAL", "Not a lower number. A coast, a fjord and an inner sea where the "
         "structural life comes back — where there is eelgrass to walk past, weed with a "
         "holdfast instead of a film, fish worth catching, and a November shoreline that does "
         f"not smell of putrefaction. That is the goal, and it is {R('T1', family='terminal')} "
         f"through {R('T5', family='terminal')} said without the letters.\n"))
    a(CL("C-PG-A-PROXY", "Nitrogen loading is at most a proxy for it, and a poor one, because "
         "a system can hit its nitrogen target and stay dead. So can every other single "
         "number on this page. **The measure of success is the four words in Part One, and "
         "three of them are not yet measured** — which makes building the outcome record the "
         "first item, not the last.\n"))

    a("---\n")
    a("*Generated by `scripts/programme.py`, with figures from `scripts/rivermap.py` and "
      "`scripts/programme_map.py`. Every number and every claim on this page is checked: "
      "each opens what it rests on. What could not be justified when the page was swept is "
      "in [ARCHIVE.md](ARCHIVE.md), with the reason.*")

    return "\n".join(o) + "\n"


def main():
    try:
        write_doc(OUT, render())
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
