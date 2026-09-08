#!/usr/bin/env python3
"""Generate docs/PROGRAMME.md - the argument, kept deliberately separate from the
investigation.

Every other document here reports what the data says and stops there. This one says what
ought to be done, which is a different kind of claim and is labelled as one throughout.
Numbers are pulled from the investigation outputs so the two cannot drift apart, and
each is linked back to the page that established it.

Usage:  python3 scripts/programme.py   (after rivermap.py, currents.py, solutions.py)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, read_json

MANUAL = os.path.join(ROOT, "data", "manual")
RAWD = os.path.join(ROOT, "data", "raw")

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
# is the axis that decides whether adaptation and burial are available at all.
CHEM_TIERS = [
    ("Deep prior — essential elements", [
        ("Zinc", "galvanised surfaces, tyres, roofing",
         "**Essential micronutrient.** Life has transporters, metallothioneins and "
         "homeostasis for it, evolved over billions of years of exposure.",
         "Already terminal — it is an element. Binds to particles and buries.",
         "**Reduce the flux, and keep the sink working.** A building-regulation rule on "
         "roof and gutter materials costs nothing and compounds over the fifty-year "
         "life of a roof. Not a ban."),
        ("Copper", "brake pads, roofing, antifouling",
         "**Essential, but a narrow window.** Thinner than zinc's — copper is acutely "
         "toxic to bivalve larvae and to fish olfaction at very low concentrations, "
         "which is to say to exactly the filter feeders and grazers whose loss the rest "
         "of this argument turns on.",
         "Element; particle-bound, buried.",
         "A product standard for brake pads. California legislated copper out of them "
         "and the industry complied."),
    ]),
    ("Weak or no prior — elements with no biological role", [
        ("Cadmium, mercury, lead", "combustion, legacy paint and plumbing, industry",
         "**No metabolic function.** Being an element is not the same as having a "
         "prior; life has detoxification for these, not use.",
         "Element — but mercury methylates in anoxic sediment, so the sink partly "
         "converts it into a more bioavailable form.",
         "Already restricted, and the restrictions largely worked. What is left is the "
         "legacy stock in sediment, which is a bed-integrity question rather than a "
         "chemicals one."),
    ]),
    ("Novel, but the cascade lands back in the primed set — a transient", [
        ("6PPD / 6PPD-quinone", "tyre antiozonant and its oxidation product",
         "**No organism has met this molecule.** Acutely lethal to coho salmon at "
         "nanogram-per-litre concentrations, at levels no evolved tolerance covers. And "
         "note that 6PPD's *degradation product* is the toxic one — degrading is not by "
         "itself resolution.",
         "**Terminates in the primed set.** Microbially mediated in soil, half-life "
         "13.5–14.2 days for the quinone; the ring breaks, the carbon chain shortens, "
         "and the metabolites are assimilated and mineralised. Slower without light "
         "(~6 months) and slower anaerobically.",
         "Stop making it. A substance of concern under REACH since 2023, with a "
         "Dutch-Austrian restriction dossier in preparation. **The fastest payoff on "
         "this list**, because the terminus is reached in weeks — cut the input and the "
         "standing stock drains itself."),
    ]),
    ("Novo-chemical — novel, chronic, and the cascade never lands", [
        ("PFAS, and its precursors", "textiles, packaging, coatings, foams, cosmetics "
         "— and a small number of uses nothing else can do",
         "**No prior anywhere in the cascade.** The carbon–fluorine bond is the "
         "strongest single bond in organic chemistry.",
         "**Never terminates.** The precursors *do* degrade — and they degrade into "
         "PFCAs and PFSAs, which the literature calls the *terminal* transformation "
         "products, because that is where the chain stops. Complete mineralisation and "
         "deep defluorination remain unsolved. Degradation here moves the problem "
         "without ending it.",
         "**Restrict the mass use, not the molecule.** Reserve it for the cases that "
         "pass both tests in the section below."),
    ]),
]

# Where each captured stream can go. The route is decided by the same evolutionary
# prior that decides the source-control instrument - which is the point of the section.
DISPOSAL = [
    ("Organic matter — fat, solids, plant biomass",
     "Deepest prior of all: it is carbon.",
     "Digest it. Denmark already runs sludge digestion for biogas. The end state is CO₂ "
     "and a digestate, and the fat is the highest-yield fraction there is.",
     "resource"),
    ("Nitrogen and phosphorus",
     "The whole point of the biology.",
     "Harvest as biomass. Phosphorus especially is a finite mined resource and worth "
     "recovering rather than burying.",
     "resource"),
    ("Zinc, copper",
     "Deep prior — essential elements with transporters and homeostasis.",
     "**Let it become soil, below a concentration threshold.** Danish counties already "
     "set limit values for metals in sediment destined for reuse. Below the limit it "
     "re-enters the terrestrial cycle; above it, a lined cell.",
     "threshold"),
    ("Cadmium, mercury, lead",
     "Weak or no prior — detoxified, not used.",
     "Burial, but stabilised. Mercury methylates in anoxic sediment, so an anoxic "
     "destination is the wrong one for that fraction specifically.",
     "threshold"),
    ("6PPD-quinone and similar transients",
     "No prior, but the cascade terminates in the primed set.",
     "Residence time *is* the treatment. What the pond does not settle, it outlives.",
     "degrades"),
    ("PFAS — a novo-chemical",
     "No prior, and the cascade never terminates in one.",
     "**Destruction, to specification.** And mostly it is not captured at all — it is "
     "dissolved and mobile, so a settling pond does not collect it. Destruction applies "
     "to the concentrated streams: spent filter media, firefighting foam, industrial "
     "waste.",
     "destroy"),
]

# Destruction conditions, because "burn it" done badly makes fluorinated by-products.
DESTRUCTION = [
    ("High-temperature incineration", ">1,100 °C, 2–3 s residence, excess oxygen",
     ">99.99% mineralisation for AFFF and similar wastes",
     "Below that, the parent compound disappears but products of incomplete combustion "
     "form — perfluorocarboxylic acids, perfluoroalkanes, C₂F₆, CHF₃. Ordinary "
     "municipal waste incineration is **not** this."),
    ("Supercritical water oxidation", "650 °C, 22 MPa, ~11% excess O₂, 10–11 s",
     ">99.999% for all 12 PFAAs measured",
     "Also produces small volatile organofluorines including trifluoromethane, a potent "
     "greenhouse gas. Emerging, not yet at municipal scale."),
]

# The industrial-strategy numbers. Sources named inline in the section that uses them.
MARKET = {
    "dk_water_export_bn_dkk": [(2006, 12.5), (2015, 16.8), (2019, 20.0), (2022, 25.0)],
    "dk_target_2030_bn_dkk": 40.0,
    "dk_export_growth_vs_national": 3.0,
    "pfas_remediation_global_usd_bn": [(2025, 1.98), (2035, 3.54)],
    "pfas_remediation_na_usd_bn": [(2024, 2.5), (2033, 5.2)],
    "settlements_usd_bn": [("3M, public water systems", 10.5, 12.5),
                           ("DuPont / Chemours", 1.185, 1.185),
                           ("Tyco Fire Products", 0.75, 0.75)],
    "us_federal_pfas_usd_bn": 10.0,
}

# Passive stormwater treatment performance, from the pond and biofilter literature.
TREATMENT = [
    ("Suspended solids (TSS)", "76–84%",
     "76% mean across 72 ponds in Canada and the USA; 81% in a mature Swedish wetland; "
     "84% at a Norwegian highway pond"),
    ("Microplastics > 500 µm", "95%", "measured across Danish and Nordic stormwater ponds"),
    ("Microplastics < 500 µm", "88%", "same programme"),
    ("Tyre wear particles", "~95%",
     "below the detection limit in three of four pond effluents; found in every "
     "sediment sample"),
]


def main():
    riv = read_json(os.path.join(DERIVED, "rivermap.json"))
    ret = read_json(os.path.join(DERIVED, "currents_index.json"))["retention"]
    mon = read_json(os.path.join(MANUAL, "monitoring.json"))
    vol = mon["national_volumes_m3_per_year"]
    tt = mon["typetal_nutrients_mg_per_l"]

    o = []
    a = o.append

    a("# The problem and the solution\n")
    a("> **This page is an argument.** Every other document in this project reports what "
      "the data supports and stops there. This one says what ought to be done, which is "
      "a different kind of claim, and it is labelled as one from here to the bottom. "
      "The numbers are pulled from the investigation pages and linked back; the "
      "*conclusions drawn from them* are mine and the reader is entitled to reject "
      "them.\n")

    # ================================================================ PROBLEM
    a("## Part one — the problem\n")

    a("### The four words people actually use\n")
    a("This page takes its problem statement from the public, not from the "
      "monitoring programme, because the monitoring programme measures what it can "
      "and the public names what it minds. Across the recorded public argument "
      "([POLITICS.md](#POLITICS.md)) the damage is named with four words, and it is "
      "worth noticing that **no one in that record — on any side — says the water "
      "is fine.**\n")
    a("| what people call it | what they mean by it | what Denmark measures | where the word and the measurement come apart |")
    a("|---|---|---|---|")
    a("| **iltsvind** | the sea is suffocating | dissolved oxygen below 4 mg/l **in "
      "stratified bottom water** | it needs depth and a sealed layer. Køge Bugt is "
      "shallow and mixes, so it **cannot register iltsvind however bad it gets** "
      "([CURRENTS.md](#CURRENTS.md)) |")
    a("| **fedtemøg** | greasy, foul water and a shore you do not want to walk on | "
      "nothing | there is no instrument. It is not a scientific term and no "
      "programme carries it |")
    a("| **fiskedød** | dead fish, visibly, in numbers | no open register | the "
      "events happen and are recorded nowhere the public can read |")
    a("| **livet i fjordene** | the structural life is gone | eelgrass depth limit, "
      "some bottom fauna | measured — through a light proxy that censors itself in "
      "shallow water ([LIGHT.md](#LIGHT.md)) |")
    a("")
    a("**Three of the four have no usable measurement, and the fourth cannot be "
      "recorded in the bay next to Copenhagen.** That is not an argument against "
      "anyone. It is a statement of what is and is not known about the things "
      "people mind, and everything on this page is shaped by it.\n")

    a("### Where it is, which is not only the shore\n")
    a("The recorded phrase is *fjorde og indre farvande* — fjords and inner waters "
      "— and the damage people describe sits in at least four different kinds of "
      "place, which do not share a mechanism and will not share a fix:\n")
    a("- **The shore itself**, where the material lands, smells and is walked past.\n"
      "- **The fjords**, enclosed, shallow, slow to exchange, and the places the "
      "public argument is mostly about.\n"
      "- **The inner waters** — belts, sounds and bays, including the ones like "
      "Køge Bugt that retain rather than flush.\n"
      "- **The open sea around Denmark**, which people also call dead, and which "
      "has no shore attached to it at all.\n")
    a("[AREAS.md](#AREAS.md) is the reason this matters here: a fix that is true of "
      "Denmark is true of nowhere in it. Copenhagen appears throughout Part Two not "
      "because the problem is Copenhagen's, but because it is the one place where "
      "the flow paths, the constructed drainage and the receiving water are mapped "
      "well enough to say *which street, which volume, which site.* Everywhere else "
      "gets the same avenues with the specifics missing.\n")

    a("### What sits underneath those four words\n")
    a("The register keeps a separate list, arrived at from the other direction — "
      "not what people call the damage but what is actually lost when it happens. "
      "The two lists are the same subject in two vocabularies, and the join is the "
      "point of this section.\n")
    a("| | what is lost | which public word points at it |")
    a("|---|---|---|")
    a("| `T1` | the large, slow, long-lived organisms, and the structure the rest of "
      "the community lived inside | *livet i fjordene* |")
    a("| `T2` | the ability to come back — the loss now maintains itself | none. "
      "**Nobody has a word for this, and it is the one that decides whether any of "
      "the rest is reversible** |")
    a("| `T3` | water fit and pleasant to be in | *fedtemøg* |")
    a("| `T4` | fish, shellfish, and the living made from them | *fiskedød* |")
    a("| `T5` | the shore as a place to be | *fedtemøg*, again |")
    a("")
    a("Note what falls out of the table. **`iltsvind` is not on it** — oxygen "
      "deficit is a mechanism, not a loss, and it appears here only because it is "
      "the thing that got measured and so became the public name for everything. "
      "And `T2` has no public word at all: there is no everyday term for a system "
      "that has stopped being able to recover, which is precisely the state that "
      "determines whether spending money on any of Part Two is worth doing.\n")

    a("### Why the current framing does not reach those four words\n")
    a("> **This section is a placeholder and is marked as one.** An earlier version "
      "gave four reasons the present framing cannot fix the problem. They were "
      "reasonable arguments and they are gone, for two faults. They arrived with no "
      "context, so a reader had no idea what was being argued against. And they "
      "were **too narrow** — four objections, written before most of the "
      "investigation existed, standing in for a critique that has since grown well "
      "past them.\n"
      ">\n"
      "> What belongs here is not a fixed list of objections. It is the "
      "**synthesis of the findings**, drawn from the investigation pages and from "
      "the register, and weighted toward the ones that carry a political "
      "consequence — because those are the ones where being wrong costs something. "
      "That synthesis needs the field to be scored before it can be written "
      "honestly, and the field is not scored yet: "
      "[HYPOTHESES.md](#HYPOTHESES.md) states the mechanisms and explicitly "
      "declines to rank them.\n"
      ">\n"
      "> Writing it earlier would mean assembling whichever findings happen to "
      "exist into an argument and calling it a conclusion, which is the failure "
      "this site was built to notice. So it stays empty, visibly, until there is "
      "something to put in it.\n")

    a("### What this page can and cannot honestly claim\n")
    a("Because three of the four public words have no measurement, **the solutions "
      "below cannot currently verify their own success.** Rainwater rivers, a "
      "wetland outlet, treatment and source control can each be built, costed and "
      "monitored for the things that *are* instrumented — volumes, loads, "
      "concentrations. None of that would tell anyone whether the shore stopped "
      "smelling.\n")
    a("That gap is fixable and cheap, and it is the argument for `X19` and `X20` in "
      "[EXPERIMENTS.md](#EXPERIMENTS.md): a panel that reports on a schedule "
      "including the days nothing happens, and a structured record from the people "
      "who have watched the same ground for forty years. Without an outcome record "
      "the whole of Part Two is an argument from mechanism, and it should be read "
      "as one.\n")
    a("Two things deliberately not on this page. The public argument itself — who "
      "said what, when, and whether it was checkable — is [POLITICS.md](#POLITICS.md), "
      "and it is a different object of study. And *how pollution becomes visible to "
      "the public at all*, which is a real problem and a genuinely separate project, "
      "is [OPEN_PROBLEMS.md](#OPEN_PROBLEMS.md) item 9.\n")

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
    a("The 2012 flood model is usually read as a risk map. It is also a survey: at 10 m "
      "resolution, it is a record of where water in Copenhagen goes when you stop "
      "forcing it into a pipe. That is the natural drainage network of the city, and it "
      "has already been mapped.\n")
    a("**What this covers.** The 2012 model was published as seven PDF sheets with the "
      "georeferencing stripped out. Four registered automatically against the water in "
      "them. The other three — Amager, Bispebjerg, København Vest — were placed from "
      "control points reported by a resident, who found marked dots on a web map one at "
      f"a time. **All seven are now placed**, and everything below is "
      f"**{riv['flood_path_km2']:.2f} km² of modelled flood path** across the whole "
      "city.\n")
    a("The three assisted sheets are good to roughly ±90–140 m against 20–30 m for the "
      "automatic four, so treat the 50 m proximity band on those as indicative and the "
      "200 m band as sound. Provenance and per-sheet accuracy are in "
      "`data/derived/floodmaps/_georef.json`.\n")
    a("Measured against it:\n")
    a("| | Share of the *inner-city* modelled flood path |")
    a("|---|---:|")
    a(f"| Within 100 m of a planned **surface** route | **{riv['near_surface_conveyance_pct']:.0f}%** |")
    a(f"| Within 100 m of a planned **pipe** | {riv['near_buried_conveyance_pct']:.0f}% |")
    a(f"| Within 100 m of anything in the plan | {riv['near_anything_pct']:.0f}% |")
    a(f"| **With no surface route within 100 m** | **{riv['no_surface_route_pct']:.0f}%** |")
    a("")
    a(f"So the surprise is a positive one. Across the inner city, Copenhagen has "
      f"already drawn the river network: **{riv['near_surface_conveyance_pct']:.0f}% of "
      "the flood paths there have a surface alignment planned beside them.** The city's cloudburst plan is "
      "169 km of surface conveyance against 71 km of pipe "
      "([SOLUTIONS.md](#SOLUTIONS.md)). The idea is not missing. The alignments are not "
      "missing.\n")
    a("**What is missing is the connection.** A skybrudsvej is designed against a "
      "hundred-year event: it activates when the system is already overwhelmed, a "
      "handful of times a decade. Ordinary heavy rain — the rain that actually causes "
      "overflows, many times a year — still goes down the gully into the combined pipe "
      "exactly as before. The surface network was built to protect the city from water, "
      "not to protect the sea from the city.\n")
    a("**The ask is therefore small and specific:** connect the everyday rain to the "
      "surface network that has already been designed and partly built, instead of only "
      "the cloudburst rain. That is a change in inlet design and drainage regulation, "
      "not a new masterplan.\n")

    a("#### Where an open channel will not fit\n")
    a("Not every alignment can be a river. A dense street with no room to lose, a "
      "junction, a listed square — in those places the water still has to leave the "
      "sewage system, and the way to do it is vertical rather than horizontal.\n")
    a("![Street section: the combined sewer now, and the interceptor "
      "retrofit](retrofit_section.svg)\n")
    a("**Drop the foul sewer by about a metre and put a rain-only line into the space "
      "above it.** Same trench, same street, same gully. The manhole connects to the "
      "new line instead of the old one; the house drains stay on the foul sewer, which "
      "is now deeper and, with the rain taken out, never full.\n")
    a("What this buys is the thing that matters: **there is no longer a mixture to "
      "overflow.** An overflow structure on a foul-only sewer has nothing to spill in a "
      "storm, because the storm is not in that pipe. It is more expensive per metre than "
      "a channel and far cheaper than a parallel corridor, and it is the reason the "
      "proposal does not have to stop where the street narrows.\n")
    a(f"On this project's classification, **{riv['near_buried_conveyance_pct']:.0f}% of "
      "the modelled flood path already has a planned pipe within 100 m** — those "
      "alignments are the retrofit candidates, because the trench is going to be opened "
      "anyway.\n")
    if riv["corridors"]:
        a(f"And where no alignment exists — the {riv['no_surface_route_pct']:.0f}% — the "
          f"model names the places. {len(riv['corridors'])} corridor candidates come out "
          "of it: stretches with more than 0.5 m of modelled water, no surface route "
          "within 100 m, and enough length to be a channel rather than a puddle. They "
          "are circled on the map and listed in `data/derived/rivermap.json`.\n")

    # ---- 2
    a("### 2. An outlet that is not the sea\n")
    a("![Where a raindrop goes now, and where it would go](system_flow.svg)\n")
    a("A basin that overflows to the sea is a delay, not a solution. It holds the water "
      "until it fills, and then it releases both the water and the sediment that "
      "settled in it during every previous event — on a flow threshold, which is why "
      "the annual-average accounting cannot see it.\n")
    a("The alternative is a terminal water: an outlet that is a lake, a watercourse, a "
      "wetland or a quarry rather than the bay.\n")
    a("![Køge Bugt: what drains into it](koege_bugt_system.svg)\n")
    a("*Real: coastline, combined-sewer catchments, overflow structures, treatment "
      "plants, and the chalk quarry discussed below. Green and dashed: proposal, not "
      "data.*\n")
    a("**Case one: a flooded chalk quarry.** Karlstrup Kalkgrav sits behind Solrød "
      "Strand, separated from Køge Bugt by the motorway. Its water level is held "
      "**four metres below sea level** by a pump station that already removes about "
      "**600,000 m³ a year** and discharges it into the bay. As hydraulic geometry it "
      "looks close to ideal: a deep hole below sea level, next to the shore, with the "
      "pumping installed.\n")
    a("**It is the wrong site, and my first reason for saying so was out of date.** "
      "I originally rejected it as \"Zealand's clearest lake\", which is what the "
      "encyclopedia says. That claim carries no citation and no year. A resident who "
      "knows the place reports algal growth, an odour, a declining fishery where there "
      "had been a fishing culture, and accumulated plastic waste.\n")
    a("So the useful question is not whether the lake is clean. It is **what would "
      "have told us either way**, and the answer is close to nothing:\n")
    kk = mon["karlstrup_kalkgrav"]
    st = kk["official_status"]
    a("| | |")
    a("|---|---|")
    a(f"| Registered as | {kk['water_body']['registered_as']} "
      f"({kk['water_body']['id']}), {kk['water_body']['area_km2']} km², "
      f"catchment {kk['water_body']['catchment']} |")
    a(f"| Ecological status | **{st['ecological_status']}** — assessed on the "
      "phytoplankton element only, from chlorophyll |")
    a(f"| Chemical status | **{st['chemical_status']}** |")
    a(f"| Data window | **{st['data_window']}** |")
    a("| Bathing-water sampling | none — it is not a designated bathing water; the four "
      "within 3 km are all coastal |")
    a("| Litter, plastic, odour, fish kills | **not monitored by anything** |")
    a("")
    a("A lake carrying one number, from a chlorophyll series that ended around 2018, "
      "with chemical status never determined and no instrument at all for the things "
      "the resident describes. **The disagreement about its condition cannot be "
      "settled from published data**, and that is the same failure this project keeps "
      "finding: the condition people can smell is the condition nothing measures.\n")
    a("And there is a better reason to reject the site, which does not depend on how "
      "clean it is now. The lake is 14 m deep with **poor circulation** — cold water "
      "immediately below a warm surface layer. That is precisely the configuration "
      "that stratifies and goes anoxic under nutrient load. Directing stormwater into "
      "it would reproduce Køge Bugt in miniature, in fresh water, half a kilometre "
      "inland. **A deep, still hole is a bad treatment basin.** What treatment wants is "
      "the opposite: shallow, wide, and vegetated.\n")

    # ---- Vestamager
    sp = amager_split()
    am, ml = sp["Amager"], sp["mainland"]
    a("#### Case two: Vestamager, which is the right shape\n")
    a("Behind the Amager dyke is a polder. Between 1939 and 1943 a 14 km dyke four "
      "metres high was built across a shallow bay, channels were dug, and about "
      f"**{VESTAMAGER_HA/100:.0f} km² was pumped dry**. Two pump stations still keep it "
      "that way. It is Kalvebod Fælled, now part of Naturpark Amager.\n")
    a("Everything the quarry only pretended to offer is actually there:\n")
    a("| | |")
    a("|---|---|")
    a(f"| Area | ~{VESTAMAGER_HA:,.0f} ha, held below sea level |")
    a("| Hydraulics | already a pumped polder — the pumps, dyke and channels exist |")
    a("| Feed | gravity, from an island that sits above it |")
    a("| Shape | shallow, wide and vegetated — what settling and uptake actually want |")
    a("| Ownership | public |")
    a("")
    a("**And Amager is a third of the problem.** Splitting Copenhagen's "
      "combined-sewered impervious area by island:\n")
    a("| | Impervious hectares on the combined system |")
    a("|---|---:|")
    a(f"| **Amager** — upstream of the polder, no harbour to cross | **{am:,.0f} ha "
      f"({am/(am+ml)*100:.0f}%)** |")
    a(f"| Mainland Copenhagen | {ml:,.0f} ha ({ml/(am+ml)*100:.0f}%) |")
    a("")
    a("Stormwater treatment wetlands are conventionally sized at a few per cent of the "
      "impervious area draining to them. For Amager's share that is:\n")
    a("| Sizing | Treatment area | Share of Vestamager |")
    a("|---|---:|---:|")
    for f_, lbl in ((0.01, "1% — a lean wet pond"), (0.02, "2%"), (0.03, "3%"),
                    (0.05, "5% — generous, wetland-type")):
        a(f"| {lbl} | {am*f_:,.0f} ha | **{am*f_/VESTAMAGER_HA*100:.1f}%** |")
    a("")
    a(f"**Between half a per cent and three per cent of the polder would do it.** That "
      "is the difference between this and the quarry: the quarry was two orders of "
      "magnitude too small and the wrong shape; this is two orders of magnitude larger "
      "than needed and exactly the right shape.\n")

    a("*And the evidence, now that it exists.* This section used to sit on ground the "
      "flood model did not cover — Amager was one of three sheets that never "
      "registered. All three have since been placed from resident-reported control "
      "points, so **the island this section proposes to drain has its modelled flood "
      "paths in the analysis**. Adding the three took the surface-route coverage in "
      "section 1 from 72% to 57%, which is the honest direction: the four sheets that "
      "registered easily were also the best-served ones.\n")
    a("#### The objections, which are real\n")
    for h, t in [
        ("Natura 2000.",
         "A bird protection area occupies the south-western corner, with no public "
         "access. That is a binding legal constraint on siting — though not "
         "automatically an argument against, because a shallow treatment wetland *is* "
         "wader habitat and the polder's water levels are already managed for exactly "
         "that. The tension is real and it is about which hectares, not whether."),
        ("Contaminant banking.",
         "This is the serious one. Everything the treatment removes — metals, PAH, tyre "
         "wear, microplastics — accumulates in the sediment, and accumulating it inside "
         "a bird reserve puts it into a food chain. Treatment cells would have to sit "
         "outside the designated area, be lined, and be dredged on a schedule that is "
         "actually kept. A pond that is never dredged becomes the thing it was built to "
         "prevent, and doing that in a nature park would be worse than not building it."),
        ("It only serves a third of the city.",
         f"The mainland's {ml:,.0f} ha cannot reach the polder by gravity — the harbour "
         "is in the way. This is not the answer for Copenhagen. It is a good answer for "
         "Amager, and Amager is where a third of the combined-sewered surface is."),
        ("Groundwater and the polder's own water balance.",
         "Adding a large managed inflow to a basin whose level is maintained by pumping "
         "changes the pumping duty and the salinity gradient. Neither is exotic; both "
         "have to be modelled before anyone draws a line on a map."),
    ]:
        a(f"- **{h}** {t}")
    a("")
    a("*What this is:* the case that the site meets the physical criteria, which is a "
      "much weaker claim than that it should be built. Nobody has run the numbers, and "
      "the four objections above are where the argument would actually be won or lost.\n")

    a("#### The specification, generalised\n")
    a("What the two cases together establish is the shopping list:\n")
    for t in [
        "**shallow and wide, not deep and still** — settling and plant uptake need "
        "surface area, and a deep unmixed basin stratifies and goes anoxic",
        "**below the contributing catchment**, so the feed is gravity",
        "**not hydraulically connected to the sea**, so there is no threshold at which "
        "it discharges",
        "**an area of order 1–5% of the impervious catchment**",
        "**and a dredging obligation written down before it is built**",
    ]:
        a(f"- {t}")
    a("")
    a("Denmark has a public register of raw-material extraction areas and a great many "
      "low-lying reclaimed and drained areas. Screening them against that list is a "
      "desk exercise. It has not been done for this purpose, and that it has not been "
      "done is the finding.\n")
    a("*The standing objection.* Anything infiltrating toward the chalk aquifer is a "
      "groundwater question, and Copenhagen drinks its groundwater. A terminal water "
      "has to be lined, or sit where the aquifer is already written off, or discharge "
      "to a surface watercourse after treatment. That narrows the site list "
      "considerably. It does not empty it.\n\n")
    # ---- 3
    a("### 3. Light treatment at high throughput, which is a different machine\n")
    a("Separating rainwater does not mean discharging it raw. Untreated urban surface "
      "water is one of the main routes by which tyre particles, microplastics and "
      "metals reach the sea, and simply giving it its own pipe would move that problem "
      "rather than solve it.\n")
    a("But stormwater needs a **fundamentally lighter machine** than sewage does, and "
      "the reason is chemical rather than economic:\n")
    a("| | Sewage | Stormwater |")
    a("|---|---|---|")
    a(f"| Volume (national, rain-dependent) | {vol['combined_overflow_water']/1e6:,.0f} "
      f"million m³/yr overflow | {vol['separate_stormwater_discharged']/1e6:,.0f} "
      "million m³/yr |")
    a(f"| Strength (COD) | {tt['reference_raw_sewage']['COD']:,.0f} mg/l | "
      f"{tt['separate_stormwater']['COD']:,.0f} mg/l |")
    a(f"| Nitrogen | {tt['reference_raw_sewage']['Tot-N']:,.0f} mg/l | "
      f"{tt['separate_stormwater']['Tot-N']:,.0f} mg/l |")
    a("| Pollutants are mostly | dissolved and biological | **bound to particles** |")
    a("| So the removal mechanism is | biological process, aeration, energy | "
      "**gravity** |")
    a("")
    a("That last row is the whole argument. Metals, PAH, tyre wear and microplastics in "
      "runoff travel attached to sediment, and sediment settles on its own. A treatment "
      "train of gross-pollutant trap, forebay, wet pond and filter strip has no aeration "
      "basin, no sludge recirculation, no energy input, and no process to upset. Its "
      "throughput is limited by area, and area is the cheap input.\n")
    a("What that buys, from the pond literature:\n")
    a("| Removed | Efficiency | Evidence |")
    a("|---|---:|---|")
    for name, eff, src in TREATMENT:
        a(f"| {name} | **{eff}** | {src} |")
    a("")
    a("**95% of tyre wear material, by letting water sit still.** That is the strongest "
      "single number in this document, and it is the answer to the objection that "
      "separated stormwater would just be pollution with a shorter pipe.\n")
    a("Two honest limits. Ponds do not remove dissolved fractions — chloride from road "
      "salt, dissolved copper, PFAS — so they are a complement to source control and "
      "not a substitute for it. And their performance depends entirely on the sediment "
      "being *removed* periodically rather than left to accumulate and eventually "
      "scour, which is the identical failure mode as the sewer basins. A pond that is "
      "never dredged becomes the thing it was built to prevent.\n")

    # ---- 4
    a("### 4. Where the captured material goes, which the same taxonomy decides\n")
    a("### A note on the menu\n")
    a("One structural point belongs here rather than in the investigation, because "
      "it has no observable in the water and every entry there has to have one.\n")
    a("**The set of chemicals available to be used is not chosen by environmental "
      "comparison.** It is the output of a registration and commercialisation "
      "process. A compound reaches the market because someone patented it, took it "
      "through approval, and could sell it; once it is approved and coupled to a "
      "delivery system, the scale at which it is applied is set by economics. "
      "Comparative non-target profile is a constraint on entry, not the criterion "
      "for selection among the entrants.\n")
    a("Glyphosate is the clearest illustration. Its herbicide patent expired in "
      "2000, but engineering crops to survive it made herbicide and seed a single "
      "coupled product, and global use rose roughly fifteenfold between the "
      "mid-1990s and mid-2010s. So the compound applied more widely than any other "
      "in history is the one whose target pathway is shared by plants, bacteria and "
      "fungi — an antimicrobial at herbicide volumes. Denmark does not grow those "
      "crops and separately restricted glyphosate's pre-harvest use; the Danish "
      "connection is imported feed, and it is indirect.\n")
    a("The consequence for anything proposed on this page is concrete: **a "
      "chemical-load problem cannot be fixed by choosing better within a menu you "
      "did not write.** Substitution moves demand to the next compound on the same "
      "list, which was assembled by the same process. That is an argument for "
      "acting on total load and on the approval criteria, not for a better ranking "
      "of the existing options.\n")
    a("*What this deliberately does not claim.* Nothing about anyone's motives, "
      "national character or corporate culture. The agrochemical majors are a "
      "four-firm global oligopoly — Bayer, BASF, Syngenta, Corteva — of which two "
      "are German, one Swiss and Chinese-owned, and one American, so the "
      "common shorthand that this is an American arrangement is not accurate, and "
      "the structural argument does not need it. Motive claims are unquantifiable "
      "and would make the rest of this project dismissible for a reason unrelated "
      "to its evidence. The claim here is about how a menu is assembled, and it "
      "stands or falls on the approval record.\n")

    a("Sections 2 and 3 both end in the same objection, and it is a fair one. A "
      "treatment wetland concentrates contaminants in its sediment. Extractive "
      "aquaculture concentrates them in biomass. Neither is a solution if the answer to "
      "*and then what* is *we bank it somewhere and hope*.\n")
    a("The answer is that **the disposal route is decided by the same evolutionary "
      "prior that decides the source-control instrument.** It is one principle, applied "
      "twice:\n")
    a("> If life has met the substance before, the question is a **concentration**: "
      "there exists a level below which lifecycles absorb it and it becomes sediment "
      "and then soil. If life has never met it, there is no such level, and the only "
      "terminal option is **destruction**.\n")
    a("| Captured stream | Prior | Where it goes |")
    a("|---|---|---|")
    for name, prior, route, _kind in DISPOSAL:
        a(f"| **{name}** | {prior} | {route} |")
    a("")

    a("#### Why burial actually works on land and not in the bay\n")
    a("This is the part that makes the first half of the principle more than a hope, "
      "and it comes straight out of [SEABED.md](#SEABED.md).\n")
    a("Metals buried in **marine** sediment are held as sulphides in anoxic mud, and "
      "they are released again on re-oxidation. A dead bed crosses the resuspension "
      "threshold several times more often than a living one, so the marine sink is a "
      "store that storms keep re-opening — conditional on exactly the bed integrity "
      "that is failing.\n")
    a("**Soil does not resuspend under storm waves.** A terrestrial sink is terminal in "
      "a way a marine one is not. Which is a second, independent argument for "
      "intercepting the material on land: not only that it is easier to catch there, "
      "but that once caught, it stays caught.\n")

    a("#### And destruction has to mean destruction\n")
    a("The other half needs a specification, because burning a fluorinated compound "
      "badly does not destroy it — it makes different fluorinated compounds. The "
      "carbon–fluorine bond is the strongest single bond in organic chemistry, which is "
      "both why PFAS persists and why the conditions are extreme:\n")
    a("| Route | Conditions | Destruction | The catch |")
    a("|---|---|---|---|")
    for route, cond, eff, catch in DESTRUCTION:
        a(f"| {route} | {cond} | **{eff}** | {catch} |")
    a("")
    a("So *incinerate it* is not the policy, and neither is a temperature on a permit. "
      "**Roughly burning a fluorinated compound is worse than not burning it.**\n")
    a("The failure mode is specific and it is not a leak. Below the destruction "
      "condition the parent molecule disappears — a plant measuring only the parent "
      "reports success — while the fluorine leaves as volatile and ultrafine species "
      "through the stack. C₂F₆ has an atmospheric lifetime of the order of ten thousand "
      "years. CHF₃ is a greenhouse gas thousands of times more potent than CO₂. Partial "
      "combustion takes a water-borne problem that was at least *localised* and converts "
      "it into an airborne one that is global and permanent. That is a worse outcome "
      "than leaving it in the ground.\n")

    a("##### The verification is a fluorine mass balance, not a temperature\n")
    a("If the parent compound can vanish while the fluorine escapes, then measuring the "
      "parent compound proves nothing. The test has to follow the element:\n")
    a("| Measure | What it catches |")
    a("|---|---|")
    for m, w in [
        ("**Total fluorine in**, on the feed", "the denominator. Without it there is no "
         "balance and no claim."),
        ("**Fluoride captured**, in scrubber liquor and residue",
         "the fraction actually mineralised and held."),
        ("**Total organic fluorine in the stack**, not a target-analyte list",
         "the products of incomplete combustion, which by definition are compounds "
         "nobody put on the list."),
        ("**Ultrafine particulate**, with fluorine speciation",
         "the route the user of a bag filter is least likely to be looking at."),
        ("**The unaccounted remainder**", "presumed emitted. This is the number that "
         "matters and it is the one nobody reports."),
    ]:
        a(f"| {m} | {w} |")
    a("")
    a("A plant that cannot close its fluorine balance is not destroying PFAS. It is "
      "relocating it, and the new location is the atmosphere.\n")
    a("There is also a route with no stack at all. **Mechanochemical destruction** — "
      "milling PFAS with phosphate or silicate salts — recovers close to the full "
      "fluorine content as potassium or sodium fluoride at ambient temperature. No "
      "combustion, therefore no flue gas, therefore no products of incomplete "
      "combustion. It is laboratory and pilot scale rather than municipal scale, and it "
      "is the most direct answer to the objection above.\n")
    a("Which loops back to why the source-control instrument for PFAS is a use "
      "restriction rather than a treatment requirement. Destruction only works on a "
      "**collected, concentrated** stream. PFAS dispersed through textiles, packaging "
      "and coatings is never collected, so there is nothing to feed the furnace. "
      "**The taxonomy decides not only the disposal route but whether collection is "
      "possible at all** — and where it is not, the only lever left is upstream.\n")
    a("##### Does the capacity already exist? Not established.\n")
    a("Danish practice reportedly already runs this route: PFAS is concentrated onto "
      "granular activated carbon or ion-exchange resin, and the spent media go as "
      "hazardous waste to Fortum Waste Solutions in Nyborg — the former Kommunekemi — "
      "for incineration above 1,200 °C. Miljøstyrelsen published a feasibility study on "
      "on-site ion exchange with regeneration and destruction in 2024.\n")
    a("**None of that has been verified here, and it should not be assumed.** What "
      "exists is a reported practice and a reported temperature, from secondary "
      "sources. What would establish the capability is the list above: the plant's "
      "permitted conditions, and a fluorine mass balance across it. Danish waste-sector "
      "reporting describes PFAS as an open problem for incineration plants rather than "
      "a solved one, which is a reason to check rather than to assume.\n")
    a("The same caution applies locally and more sharply. **ARC / Amager Bakke** is a "
      "municipal energy-from-waste plant on Amager, owned by five of the municipalities "
      "that discharge into the bay, and it is the obvious thing to point at. Municipal "
      "EfW typically operates below the destruction condition. Pointing the flagged "
      "stream at it because it is nearby and municipally owned would be exactly the "
      "*roughly burn it* failure.\n")
    a("> The design consequence: **the destruction branch is the one part of this "
      "programme that must not be built on an assumption.** Everything else degrades "
      "gracefully if it is half-right. This one, done half-right, is worse than not "
      "doing it.\n")

    a("##### And the fluorine is worth money, which is the same measurement\n")
    a("Destroying PFAS properly produces fluoride — captured in the scrubber as calcium "
      "fluoride, or recovered directly as KF by the mechanochemical route. **Fluorspar "
      "is on the EU critical raw materials list**, it is the feedstock for essentially "
      "all fluorochemistry including pharmaceuticals, and its reserves are being mined "
      "down.\n")
    a("Which produces an unusually clean alignment:\n")
    for t in [
        "**the proof of destruction and the product are the same measurement.** "
        "Fluorine you can weigh in the residue is fluorine that did not go up the "
        "stack. A plant with a closed balance has both a compliance case and something "
        "to sell; a plant without one has neither, and the absence is visible on the "
        "same spreadsheet.",
        "**it makes the failure mode economically legible.** Under a temperature-based "
        "permit, incomplete combustion is invisible and costs the operator nothing. "
        "Under a fluorine balance it shows up as lost product.",
        "**and it makes the facility an export service rather than a cost centre.** "
        "Destruction capacity that can prove its balance is a scarce thing that other "
        "countries need, and the feedstock is a waste stream people pay to be rid of. "
        "That is a genuine industrial prospect and it is the argument that would fund "
        "building the thing properly rather than cheaply.",
    ]:
        a(f"- {t}")
    a("")
    a("*The caveats, because this is the part most likely to be over-sold.* Recovery as "
      "a saleable grade is demonstrated at laboratory and pilot scale, not at municipal "
      "scale. Scrubber residues from hazardous-waste incineration are themselves "
      "hazardous and Denmark currently exports air-pollution-control residue rather "
      "than using it. And an economic case for importing waste is an argument that runs "
      "away from you very easily — it is only a good one while the balance is closed "
      "and audited, which is the entire condition.\n")

    a("#### The dredged material has somewhere to go, and it is already being asked for\n")
    a("A wetland and its forebay have to be dredged, and section 4's threshold test says "
      "what happens next: below the Danish limit values for metals in sediment, the "
      "material is soil. The question is where soil is wanted.\n")
    a("On this coast, it is wanted now. **Avedøre Holme is 450 ha of existing "
      "reclamation** in Køge Bugt, and in January 2025 Hvidovre dropped the nine-island "
      "*Holmene* proposal in favour of a land-reclamation and storm-surge protection "
      "project — an engineered coastline with salt marsh, doing double duty as the "
      "flood defence. Køge Bugt Strandpark, further south, was built the same way "
      "between 1977 and 1980, and is the reason that shoreline has a dyke at all.\n")
    a("So the loop closes without anyone inventing a use: **a bay that needs its "
      "sediment intercepted, and a coast that needs fill for its own flood defence.** "
      "The material comes out of the treatment train and goes into the dyke.\n")
    a("*Two limits, and the second is firm.* Sediment above the threshold is not fill — "
      "it is a lined-cell problem, and the assay decides, not the convenience. And "
      "**incineration residue is not fill at all.** Air-pollution-control residue from "
      "hazardous-waste incineration is itself hazardous and Denmark currently exports "
      "it. A reclamation whose stated purpose is salt marsh and habitat is the last "
      "place to test that boundary — the fill has to clear the threshold on its own "
      "merits or go somewhere else.\n")

    a("#### Deciding which route, in real time\n")
    a("The two routes have very different costs, so the branch should be taken by "
      "measurement rather than by policy:\n")
    a("![Routing the rain by what is in it](routing_logic.svg)\n")
    a("A diversion node needs nothing exotic — turbidity, conductivity and flow "
      "continuously, with a grab sample triggered on threshold. Clean flow takes the "
      "cheap default: gravity to the wetland, settle, take up, dredge on schedule. "
      "Flow that trips the sensor is held for the expensive branch.\n")
    a("**And the expensive branch can be built later.** The wetland accumulates; it does "
      "not fail suddenly. Sediment concentrations rise over years, which means the "
      "sequence can be: build the wetland, instrument the inflow, and let the measured "
      "accumulation rate decide when — and whether — a heavy-duty facility is worth "
      "building at all. That is the opposite of the usual order, where the expensive "
      "asset is specified first from an assumption.\n")
    a("The honest gap: **nobody has set the threshold**, because nobody measures the "
      "events. Which returns, as everything here does, to section 7.\n")

    a("#### What this settles, and what it does not\n")
    a("It settles the objection raised against extractive aquaculture and against "
      "treatment wetlands: the harvested material is not an unanswered question. "
      "Organic matter is a fuel, nutrients are a resource, deep-prior metals are a "
      "concentration threshold with existing Danish limit values behind it, and the "
      "novel entities are a destruction problem on a stream small enough to handle.\n")
    a("It does not settle the cost, the logistics, or who pays for dredging a pond "
      "every fifteen years. Those are real and they are ordinary. The point is only "
      "that the material has somewhere to go, and that which somewhere is not a matter "
      "of preference — it follows from what the substance is.\n\n")

    # ---- 5
    a("### 5. Source control, sorted by what life has met before\n")
    a("The subsidy–stress argument in [CAUSATION.md](#CAUSATION.md) says nitrogen "
      "produces mush rather than meadow because the organisms that would have used it "
      "well are gone. If that is right, the substances that removed them sit upstream "
      "of the nutrient problem, and no amount of nutrient policy reaches them.\n")
    a("The useful way to sort those substances is **not by how toxic they are**, and "
      "not by half-life either. It is by whether life has an **evolutionary prior** for "
      "them — and, where it does not, whether the substance *breaks down into something "
      "it does*.\n")
    a("That second clause is the whole test, because degrading is not the same as "
      "resolving. A novel compound can degrade into another novel compound. 6PPD "
      "degrades into 6PPD-quinone, which is the toxic one. PFAS precursors degrade "
      "into PFCAs and PFSAs, which the literature calls **terminal** transformation "
      "products precisely because that is where the chain stops.\n")
    a("So the criterion is the **terminus**:\n")
    a("> **Novo-chemical**: a substance that is not evolutionarily primed, whose "
      "presence is lasting or chronic, and **whose degradation cascade does not "
      "terminate in something life is primed for.**\n")
    a("Everything else is a transient — a nuisance with a clock on it. A novo-chemical "
      "has no clock.\n")
    a("| Prior | Where the cascade ends | Adaptation? | Sink? | Instrument |")
    a("|---|---|---|---|---|")
    for tier, term, adapt, sink, instr in [
        ("**Deep** — essential elements (Zn, Cu)", "it is already an element",
         "Yes — transporters, homeostasis", "Particle-bound burial",
         "**reduce the flux**"),
        ("**Weak** — no biological role (Cd, Hg, Pb)", "element, but Hg methylates",
         "Detoxification only", "Burial, stabilised",
         "**restrict, guard the sediment**"),
        ("**None**, but *terminates* (6PPD-q)", "**mineralised, ~2 weeks in soil**",
         "No — but it does not need to", "Degradation", "**stop production**"),
        ("**None**, and *never terminates* — a novo-chemical (PFAS)",
         "**PFCAs / PFSAs, and stops there**", "No", "**None**",
         "**reserved use only**"),
    ]:
        a(f"| {tier} | {term} | {adapt} | {sink} | {instr} |")
    a("")
    a("That is a correction to an earlier draft of this page, twice over. The first "
      "draft put all four on one list with one remedy. The second split them by "
      "persistence, which is nearly right and gets 6PPD wrong — it is novel and "
      "acutely lethal and it still belongs in a different category from PFAS, because "
      "its metabolites are assimilated and mineralised within weeks. **Persistence is "
      "a symptom. The terminus is the property.**\n")
    a("*One interaction worth naming.* The terminus is reached by microbes, and reached "
      "slowly where there is no oxygen — 6PPD persists roughly fifty times longer "
      "anaerobically. So anoxic sediment does two things at once: it re-opens the metal "
      "store on every resuspension, and it stalls the clock on the transients. The bed "
      "condition is upstream of both.\n")
    a("*And where this sits against existing regulation.* REACH screens for PBT and "
      "vPvB, and PMT and vPvM were added as a category of substance of very high "
      "concern under the Chemicals Strategy for Sustainability. Those are the right "
      "instincts, but they are **threshold criteria on half-life, bioaccumulation and "
      "mobility**. Transformation products are assessed as an addendum rather than as "
      "the organising question. The terminus test makes it the organising question, "
      "and it is the test that separates 6PPD-quinone from a PFAS precursor — two "
      "substances that would score similarly on a half-life screen and belong in "
      "different regimes.\n")

    for tier, rows in CHEM_TIERS:
        a(f"#### {tier}\n")
        for name, source, prior, sink, ask in rows:
            a(f"**{name}** — *{source}*\n")
            a(f"- **Prior:** {prior}")
            a(f"- **Sink:** {sink}")
            a(f"- **Ask:** {ask}\n")

    a("#### What the law actually asks, and what it does not\n")
    a("It is worth being exact about the terminology, because the argument is often "
      "conducted with the wrong words and the distinction that matters is not the "
      "one people reach for.\n")
    a("**Hazard is the intrinsic capacity to harm. Risk is that capacity combined "
      "with exposure.** Most European chemicals regulation is risk-based, which "
      "means a substance known to be hazardous is permitted where exposure is "
      "judged low enough. Whether that judgement is right depends on an exposure "
      "estimate, and exposure estimates for a substance in wide dispersive use are "
      "exactly the thing this project has spent its length showing are weak.\n")
    a("The burden of proof runs the way the vocabulary suggests. REACH's own slogan "
      "is *no data, no market* — the duty is on the registrant — but the data "
      "required scales with tonnage, existing substances were largely grandfathered "
      "in, and ECHA's compliance checks routinely find dossiers incomplete. The "
      "principle is proof-of-safety; the practice is closer to **absence of "
      "demonstrated harm**, which is a different thing and a much lower bar.\n")
    a("Two places the law is stronger than that, and both are worth knowing:\n")
    a("- **Positive listing.** Pesticides and biocides work the opposite way round: "
      "only approved active substances may be used at all. Industrial chemicals "
      "under REACH are effectively negative-listed — registered means usable unless "
      "someone restricts it.\n")
    a("- **Hazard-based cut-offs.** For plant protection products, approval is "
      "refused outright for substances that are carcinogenic, mutagenic, toxic to "
      "reproduction, endocrine-disrupting, or **PBT / vPvB** — persistent, "
      "bioaccumulative and toxic, or very persistent and very bioaccumulative. No "
      "exposure argument rescues them.\n")
    a("> That last criterion is the important one for this section, because "
      "**persistence is already the regulatory proxy for an absent evolutionary "
      "prior.** *vPvB* is the law's way of saying *nothing has evolved to take this "
      "apart*, expressed as a half-life threshold instead of as a claim about "
      "biochemistry. The concept this page has been building is not foreign to "
      "European law; it is present, subordinate, and applied to individual "
      "approvals rather than to whether a substance should be ubiquitous.\n")

    a("#### Why the ecolabels are evidence\n")
    a("There is a straightforward test of whether a regulatory floor matches what "
      "people actually want, and Denmark runs it continuously.\n")
    a("**Svanemærket** — the Nordic Swan — is a lifecycle ecolabel with criteria set "
      "by a Nordic board, verified by third parties, tightened on a cycle, and "
      "awarded only to the better performers in a product category. **Astma-Allergi "
      "Danmark's Den Blå Krans** excludes fragrance allergens and specific "
      "preservatives. Both restrict substances that are **entirely legal**.\n")
    a("If the legal floor were where consumers wanted it, a label whose whole value "
      "proposition is *we removed things the law permits* would have no market. It "
      "has a large one, and it has had for decades. That is evidence about the "
      "floor rather than about the label.\n")
    a("*The fair objection, and the reason this is not conclusive.* Ecolabels also "
      "sell reassurance, distinction and brand, so their existence alone does not "
      "prove the floor is too low. What makes the argument more than commercial is "
      "*which* substances they exclude: the additions cluster on persistence, "
      "allergenicity and endocrine activity — the three places where the risk-based "
      "assessment above is weakest, because all three do their damage at doses and "
      "over timescales that an exposure estimate handles badly.\n")
    a("It is also worth being accurate about who is being suspected. The instinct to "
      "locate this problem in American corporate conduct is common and, for the "
      "agrochemical case, factually off: the majors are a four-firm global oligopoly "
      "of which two are German, one Swiss and Chinese-owned. The structural argument "
      "does not need a villain, and is stronger without one — **and the belief that "
      "European regulation already handles it is the more consequential error**, "
      "because it is the one that stops people asking.\n")

    a("#### Occupying the niche instead of poisoning it\n")
    a("There is a route that follows directly from how defence actually works in "
      "nature, and it is neither speculative nor new. If a resident community's "
      "main protective function is **occupancy** — being there, so that something "
      "else is not — then the alternative to killing a pest is **filling the space "
      "with something benign first**.\n")
    a("It is already deployed, at scale, and the flagship case is not marginal. "
      "*Wolbachia* introduced into mosquito populations blocks dengue transmission "
      "and has been released across whole cities; it is among the most successful "
      "vector-control interventions of the past decade. In agriculture, "
      "*Bacillus* and *Trichoderma* preparations are ordinary commercial products. "
      "In soil, take-all decline in wheat happens by itself: crop the same field "
      "long enough and *Pseudomonas* populations build up until the disease "
      "subsides without anyone doing anything. Aquaculture is replacing antibiotics "
      "with probiotics for the same reason.\n")
    a("Four advantages, and they follow from the mechanism rather than from "
      "enthusiasm:\n")
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
    a("*And one disadvantage that is worse than any of those is good, so it has to "
      "be said first in any proposal rather than last.* **An introduced organism "
      "cannot be recalled.** A chemical eventually degrades, or at worst persists "
      "unchanged; an organism reproduces, spreads, and evolves after release. The "
      "history of classical biological control contains real disasters, all of them "
      "from agents that did not stay on their intended target. And `T9` applies "
      "with full force: pathogen and mutualist are positions rather than kinds, so "
      "an organism benign in the context it was tested in can move along that "
      "spectrum in the context it was released into.\n")
    a("> Which gives a clean symmetry with this section's other argument, and it is "
      "worth holding both at once. **A novel chemical has no evolutionary prior and "
      "never degrades. A novel organism has a prior and never stops.** Both are "
      "irreversible, in different ways, and neither irreversibility is a reason to "
      "prefer the other by default. The test for an introduction is therefore the "
      "same shape as the test for a novo-chemical — host specificity demonstrated "
      "rather than assumed, and a bounded release rather than a dispersive one — "
      "and where the candidate is *already resident* and merely being restored to "
      "abundance, as in sediment inoculation, that test is largely already "
      "passed.\n")

    a("And there is a second reason to do it this way, which has nothing to do with "
      "ecology. **A substitution can be rolled out; a ban can only be imposed.** "
      "Because nobody has to absorb a loss to make it happen, it can be introduced "
      "catchment by catchment on a staggered schedule — which is simultaneously the "
      "intervention and the experiment. Each area is compared against its own "
      "record before it crosses over and against the areas that have not yet "
      "crossed, and no one is withheld from the treatment, only scheduled later. "
      "That design is `X17` in [EXPERIMENTS.md](#EXPERIMENTS.md), and it supplies "
      "the one thing the chemical argument has never had: **a counterfactual, at "
      "the scale the argument is made**. Every Danish catchment has been sprayed "
      "for decades, so there is currently nothing to compare against.\n")
    a("The agronomic outcome has to be measured with the same weight as the marine "
      "one, and published whichever way it falls. If biological substitution costs "
      "yield, that is a number this argument has to carry — not something for the "
      "people who farm to discover afterwards.\n")

    a("#### The instrument for a novo-chemical: reserved use\n")
    a("The instrument is the one used for antibiotics, and for the same reason. The "
      "harm from antibiotics never came from the molecule; it came from **volume and "
      "ubiquity**, which is what breeds resistance. So the response was not to ban "
      "them. It was to reserve them for cases where nothing else works, and to stop "
      "putting them in livestock feed as a growth promoter.\n")
    a("A novo-chemical needs the same treatment, and the test has **two prongs**, not "
      "one:\n")
    a("| | The test | Why it is necessary |")
    a("|---|---|---|")
    a("| **1. No substitute** | Does anything else do this job? | This is the "
      "*essential-use* concept, already in EU chemicals policy. It bounds the number of "
      "applications. |")
    a("| **2. Closed system** | Does the material stay somewhere it can be collected and "
      "destroyed at end of life? | This bounds the *dispersal*, and it is the prong "
      "usually left out. |")
    a("")
    a("The second prong is not decoration. Section 4 established that destruction only "
      "works on a **collected, concentrated** stream — >1,100 °C with adequate "
      "residence time, or supercritical water oxidation — and that dispersed material "
      "is never collected, so there is nothing to feed the furnace. **A closed system "
      "is the condition that makes the disposal route exist at all.**\n")
    a("Which sorts the applications cleanly:\n")
    a("| Use | No substitute? | Closed system? | |")
    a("|---|---|---|---|")
    for use, sub, closed, verdict in [
        ("Reactor and chemical-plant seals", "Yes", "Yes — inventoried, serviced, "
         "decommissioned under waste tracking", "**reserved**"),
        ("Medical implants and devices", "Yes", "Yes — explanted and disposed as "
         "clinical waste", "**reserved**"),
        ("Some aerospace and semiconductor process chemistry", "Largely",
         "Yes — closed process, captured waste streams", "**reserved, under review**"),
        ("Firefighting foam", "Substitutes now exist",
         "No — it is deployed by spraying it on the ground", "**out**"),
        ("Impregnated textiles, food packaging, cosmetics, ski wax",
         "No", "No — it is dispersed by design", "**out**"),
    ]:
        a(f"| {use} | {sub} | {closed} | {verdict} |")
    a("")
    a("Note what the second prong catches that the first does not. Firefighting foam "
      "has a serious argument on prong one — it saves lives, and the substitutes took "
      "decades. It fails absolutely on prong two, because the method of use *is* "
      "dispersal into the ground. **The volume and the containment are the policy "
      "variables; the chemistry is not.**\n")
    a("So: *banned as a mass-adopted material, reserved for special products in "
      "special facilities.* That is not a compromise between banning and permitting. "
      "It is the only formulation that matches what the substance actually is — "
      "irreplaceable in a few places, and irretrievable everywhere else.\n")

    a("#### Two caveats on the metals, which are this project's own findings\n")
    hz = mon["hazardous_substances"]
    zn, cu = hz["typetal_ug_per_l"]["Zink"], hz["typetal_ug_per_l"]["Kobber"]
    a(f"Zinc is the largest metal term in the Danish stormwater typetal by an order of "
      f"magnitude — **{zn[0]:,.0f} µg/l** in combined overflow and {zn[1]:,.0f} µg/l in "
      f"separate stormwater, against {cu[0]:,.0f} and {cu[1]:,.0f} for copper, with a "
      f"maximum observed of {zn[2]:,.0f}. The flux is not small.\n")
    a("**The sink is conditional, and the condition is failing.** Metals bury as "
      "sulphides in anoxic sediment and come back out on re-oxidation. "
      "[SEABED.md](#SEABED.md) computes that a dead bed crosses the resuspension "
      "threshold several times more often than a living one. So sediment is not a "
      "terminal sink — it is a store that the same degradation we are worried about "
      "keeps re-opening. Burial only counts while the bed stays intact, which ties "
      "metal policy directly to bed integrity and to trawling. The two cannot be "
      "argued separately.\n")
    a("**And adaptation has a specific price.** Communities do become metal-tolerant; "
      "the phenomenon is well documented and has a name, pollution-induced community "
      "tolerance. But tolerance at the community level is achieved by **losing the "
      "sensitive species**, and the sensitive ones are disproportionately the slow, "
      "structural, long-lived organisms. *Life adapts* and *the higher life is replaced "
      "by the simple life* are the same sentence read two ways — which is the "
      "mechanism this whole document is about, arriving from a different direction.\n")
    a("None of that makes zinc a PFAS. It makes the metal case an argument about "
      "**rate and community cost**, where the novel-entity case is an argument about "
      "**permanence**. Different arguments, different remedies, and conflating them "
      "weakens both.\n")

    a("#### The general principle\n")
    a("**You cannot filter out what you can decline to manufacture.** A substance "
      "regulated at the point of discharge has to be caught at 19,665 outfalls. The "
      "same substance regulated at the point of sale has to be caught once. Denmark "
      "regulates the outfall and imports the product.\n")
    a("*This remains the section furthest from what this project has measured.* We have "
      "not established that any of these is a binding constraint in Danish coastal "
      "water — only that the mechanisms are well founded, that the substances are "
      "present, and that the monitoring which would settle it rests on eleven stations "
      f"which in Miljøstyrelsen's own words are limiting for *{hz['excludes_heavy_catchments']}* "
      "— the industrial areas and heavily trafficked roads the substances come from. "
      f"The same programme reports {hz['counterpoint']}.\n")

    # ---- 6
    a("### 6. Rebuild the thing that used to absorb it\n")
    a("Load reduction assumes the receiving system will recover once the pressure comes "
      "off. Where the structural life has already gone, that assumption is doing a lot "
      "of unexamined work — a bay with no filter feeders, no eelgrass and a loose bed "
      "does not return to 1960 because the load returns to 1960.\n")
    a("### Why putting life back is not cosmetic\n")
    a("The obvious case for extractive aquaculture is a mass balance: mussels and "
      "seaweed take nitrogen up, you harvest them, the nitrogen leaves. True, and the "
      "weaker half of the argument. It treats a living bay as a filter, and predicts a "
      "benefit strictly proportional to the area farmed.\n")
    a("The stronger case is about **who is limited**. Liebig's law says growth is set "
      "by whichever necessary thing is scarcest — and the number of ways an organism "
      "can be stopped is the number of things it requires. Large, slow, structured "
      "life needs a particular substrate, particular partners, particular light, "
      "particular chemistry, a particular season, and years of quiet in which to "
      "mature. An opportunist needs carbon, some nutrient, and water.\n")
    a("So the competition is asymmetric, and not because one is fitter. **The "
      "low-requirement organism wins by being harder to stop.** Whatever goes wrong, "
      "it is more likely to have gone wrong for the demanding species than for the "
      "undemanding one, which is why every kind of damage ends in the same kind of "
      "community.\n")
    a("Which means a standing meadow or mussel bed is not a *symptom* of a healthy "
      "bay. It is a **cause** of one. It draws the surplus down, shades the water, "
      "filters the plankton, oxygenates and binds the sediment, and shelters the "
      "grazers that crop what is left. It manufactures scarcity for its competitor — "
      "it imposes Liebig limitation on the opportunists, which have almost none of "
      "their own.\n")
    a("And that is the same fact read backwards. Once the structural life is gone, "
      "nothing imposes the limitation any more, the surplus stays available, and the "
      "fast forms keep it. The state holds itself up, which is exactly why the load "
      "coming off does not bring the bay back.\n")
    a("> **The two arguments make different predictions, and the difference is "
      "testable.** Mass balance is linear in area: half the farm removes half the "
      "nitrogen. Imposed limitation is not — below some threshold of cover nothing "
      "changes, and above it the state flips and holds. If restoration turns out to be "
      "linear in area, aquaculture is a filter and should be costed as one. If it is "
      "threshold-shaped, it is a state change, and a small intervention in the right "
      "place is worth more than a large one spread thin.\n")
    a("*The honesty here.* This is well established in shallow lakes, where the "
      "clear-water plant-dominated state and the turbid algae-dominated state are "
      "documented alternative stable states with exactly this mechanism behind them. "
      "The coastal marine analogue is argued from the same ecology and is much less "
      "firmly demonstrated. It is a mechanism with good foundations, not a measured "
      "Danish result, and the experiment that would settle it — put it back where "
      "conditions are said to be adequate, and see whether it holds — is `X10` in "
      "[EXPERIMENTS.md](#EXPERIMENTS.md).\n")
    for t in [
        "**Extractive aquaculture.** Mussels and macroalgae remove nitrogen as biomass "
        "and are harvested rather than left to decay. At the loads computed for this "
        "bay, single-digit km² would match the overflow nitrogen. It is the only "
        "intervention on this list that removes what is already in the water rather "
        "than reducing what is added.",
        "**Eelgrass, where the light allows it.** Uptake, sediment stabilisation and "
        "habitat in one organism. Turbidity is the binding constraint, which links it "
        "directly to items 1 and 3.",
        "**Leave the bed alone where it is recovering.** A living bed resuspends "
        "several times less often than a dead one ([SEABED.md](#SEABED.md)), so bed "
        "integrity is not only a fisheries question — it changes how often the "
        "accumulated sulphide and metals come back into the water.",
        "**Harvest as a use, not a disposal.** Extracted biomass that is too "
        "contaminated for human consumption still has uses where accumulation is "
        "acceptable — which is a question about what we are willing to do with it, not "
        "a technical obstacle.",
    ]:
        a(f"- {t}")
    a("")
    a("*The disposal question* — extractive aquaculture concentrates metals and "
      "organic contaminants in the harvest — is answered in section 4, and the answer "
      "splits the harvest rather than the idea. Biomass carrying deep-prior metals has "
      "a threshold below which it re-enters the terrestrial cycle; biomass carrying "
      "cadmium or mercury does not, because those biomagnify and have no prior. So "
      "where a harvest goes has to be settled by assay, before it is scaled, not "
      "after.\n")

    # ---- 7
    a("### 7. Measure the six things that would settle the argument\n")
    a("This is first in priority and last in the list because it is the least "
      "satisfying. Everything above is contestable, and it is contestable because the "
      "measurements that would resolve it were never taken.\n")
    a("| Measure | Cost | What it settles |")
    a("|---|---|---|")
    for m, c, w in [
        ("Flow-proportional sampling at the 13 largest overflow structures",
         "weeks",
         "Whether load is as concentrated as volume is. 13 of 1,328 structures hold 24% "
         "of recorded storage; if load follows, most of the problem has 13 addresses."),
        ("Fat, oil, grease and total organic carbon added to the determinands", "trivial",
         "Whether the material the shore is named after is even in the discharge."),
        ("Autumn benthic sampling at existing stations", "one survey season",
         "The depth of the annual die-off, which the March–May window has never seen."),
        ("Fixed coastal cameras with a monthly index, year-round", "negligible",
         "Whether fedtemøg has the season everyone assumes. Currently unfalsifiable in "
         "either direction."),
        ("Iltsvind extent regressed on load, wind-work and temperature", "no new data",
         "Whether the extremes track load at all. All three series are already "
         "published by DCE."),
        ("A screen of disused extraction sites against the four criteria in item 2",
         "a desk week",
         "Whether terminal storage is available at all, before anyone argues about "
         "whether it is desirable."),
    ]:
        a(f"| {m} | **{c}** | {w} |")
    a("")

    # ================================================================ ORDER
    a("## The order of operations\n")
    a("The interventions above split cleanly by timescale, and the split is the "
      "argument for what to do this year:\n")
    a("| | Timescale |")
    a("|---|---|")
    for t, s_ in [
        ("Measure the tail; publish event-level flow", "weeks"),
        ("Empty basins before the season rather than letting flow scour them", "months"),
        ("Enforce grease separation at source", "months"),
        ("Screen extraction sites for terminal storage", "months"),
        ("Connect everyday rain to the existing surface network", "years"),
        ("Build the missing corridors and their treatment ponds", "years"),
        ("Product bans through REACH", "2–3 years, already started"),
        ("Genuine network separation", "decades — 13 of 300 catchments are planned for it"),
    ]:
        a(f"| {t} | **{s_}** |")
    a("")
    a("Which produces an uncomfortable conclusion for everyone. The people who want "
      "urgent action have to accept that the physical fix is a generational programme. "
      "The people who want to wait for better evidence have to accept that the evidence "
      "is cheap, available, and has been declined for decades.\n")
    a("**Is it solvable in a year?** Not the infrastructure. But the *measurement* is a "
      "season's work, the *operating* changes — basin emptying, grease enforcement, "
      "release timing — are a year's work and would act on exactly the pulsed, "
      "threshold-triggered discharge that the annual accounting is blind to. If the "
      "concentration in the register carries through to load, then a year of "
      "operational change on a few dozen structures is not a small intervention at "
      "all. Nobody knows whether it does, because nobody has measured it. That is the "
      "single most actionable sentence in this document.\n")

    # ================================================================ INDUSTRY
    a("## Is this a cost, or is it an industry?\n")
    a("The programme above reads as expenditure. It is worth asking whether it is "
      "actually the same shape as green energy was in 1990 — a cost centre that turns "
      "out to be a sector, and grows precisely because the problem does.\n")

    a("### The Danish precedent is exact, and it is not a metaphor\n")
    a("Denmark did this once already with wind, and is halfway through doing it again "
      "with water. Water technology export has gone from "
      f"**DKK {MARKET['dk_water_export_bn_dkk'][0][1]:.1f}bn in "
      f"{MARKET['dk_water_export_bn_dkk'][0][0]}** to roughly "
      f"**DKK {MARKET['dk_water_export_bn_dkk'][-1][1]:.0f}bn by "
      f"{MARKET['dk_water_export_bn_dkk'][-1][0]}**, growing at about "
      f"**{MARKET['dk_export_growth_vs_national']:.0f}× the rate of Danish exports "
      "overall**, with a stated national target of "
      f"DKK {MARKET['dk_target_2030_bn_dkk']:.0f}bn by 2030.\n")
    a("The mechanism in both cases was the same and it is the relevant one here: **a "
      "domestic requirement created a domestic market before the technology was "
      "competitive**, and the export followed the reference plants. Nobody bought "
      "Danish wind turbines because Denmark wrote a good report about wind.\n")

    a("### The demand signal is liability, not subsidy — which is stronger\n")
    a("Green energy needed a subsidy because it was selling a commodity that already "
      "had a price, and selling it dearer. Clean-up sells the absence of a harm, which "
      "has no price at all until somebody is made to pay for it. That is normally the "
      "fatal weakness of the sector.\n")
    a("For PFAS it has stopped being true:\n")
    a("| | USD |")
    a("|---|---:|")
    for name, lo, hi in MARKET["settlements_usd_bn"]:
        v = f"{lo:.2f}bn" if lo == hi else f"{lo:.1f}–{hi:.1f}bn"
        a(f"| {name} | **{v}** |")
    a(f"| US federal infrastructure allocation for PFAS in water systems | "
      f"{MARKET['us_federal_pfas_usd_bn']:.0f}bn |")
    g = MARKET["pfas_remediation_global_usd_bn"]
    a(f"| *For comparison — the entire global PFAS remediation market, {g[0][0]}* | "
      f"*{g[0][1]:.2f}bn/yr* |")
    a("")
    a("**The settlements are several times the size of the industry that would do the "
      "work.** Around USD 13.6bn is committed to public water systems in the United "
      "States against a global remediation sector of roughly two billion a year. That "
      "is a demand overhang, and a demand overhang is the condition under which an "
      "industry scales rather than merely persists.\n")
    a("And it is a more durable signal than a subsidy, because it does not depend on a "
      "government keeping its nerve. It depends on courts, and on a science base that "
      "is firming up rather than softening. Forecast growth is unremarkable — "
      f"{g[0][1]:.1f} to {g[1][1]:.1f}bn globally by {g[1][0]}, "
      f"{MARKET['pfas_remediation_na_usd_bn'][0][1]:.1f} to "
      f"{MARKET['pfas_remediation_na_usd_bn'][1][1]:.1f}bn in North America — but "
      "forecasts of a sector this young are the least reliable number on the page.\n")

    a("### The third demand curve, which is the one that matters\n")
    a("Liability demand is real and it is bounded — by what courts award, and by "
      "settlement deadlines that can be missed. There is a third kind, and it does not "
      "behave like a market at all.\n")
    a("PFAS is already in the rain. Cousins and colleagues (*Environmental Science & "
      "Technology*, 2022) compared four perfluoroalkyl acids — PFOA, PFOS, PFHxS, "
      "PFNA — in rainwater, soil and surface water worldwide against published guideline "
      "levels, and concluded that **the planetary boundary for chemical pollution has "
      "been exceeded**. Not regionally. The lowest PFOA concentration they recorded "
      "anywhere was on the Tibetan Plateau, and Antarctic rainwater is in the same "
      "condition. Their benchmark for the sum of the four is, as it happens, **the "
      "Danish drinking water limit value**, which rainwater across the planet routinely "
      "exceeds.\n")
    a("*The caveat this project owes its own standards.* \"Fourteen times the "
      "guideline\" is partly a statement about where the guideline was set — the US "
      "advisory level for PFOA was lowered in 2022 to a concentration below routine "
      "laboratory detection, so the multiple moved because the yardstick moved. The "
      "underlying observation does not depend on that: the compounds are present "
      "everywhere, including places with no source within thousands of kilometres, and "
      "the stock only grows.\n")
    a("What follows is an economic point rather than a toxicological one. A pollutant "
      "that is globally distributed, that accumulates, and whose effects propagate "
      "through food webs in ways nobody can currently bound, carries a **threshold "
      "risk**: a level at which some function — reproduction in a taxon, a fishery, a "
      "drinking water source — stops working. Nobody knows where that level is. The "
      "relevant feature is what happens to demand if it is reached:\n")
    a("| Demand type | Set by | Bounded by |")
    a("|---|---|---|")
    a("| **Elastic** — green energy | the price of the commodity it replaces | the "
      "commodity price |")
    a("| **Liability** — PFAS now | courts and settlements | what is awarded |")
    a("| **Threshold** — PFAS if a function fails | nothing | **nothing** |")
    a("")
    a("Under the third, willingness to pay stops being a variable. That is the *any "
      "cost* case, and it is the one the user of this document was pointing at.\n")

    a("#### Which creates an awkward asymmetry\n")
    a("**Capacity cannot be built at the moment it is needed.** Permitting and "
      "constructing high-temperature destruction is the better part of a decade. If the "
      "threshold arrives, the capacity that exists is the capacity someone built "
      "beforehand, and the rest is a queue.\n")
    a("That is an argument for building ahead of demonstrated need — which is exactly "
      "the argument made for renewables in 1990, and which turned out to be right. It "
      "also collides head-on with the moral hazard below, and the collision has a "
      "resolution: **size the capacity to the legacy stock, not to a projected flow.** "
      "What is already emitted is finite, already in the environment, and needs "
      "processing whether or not another gram is ever manufactured. It is a large "
      "enough job to justify serious capacity without requiring the production to "
      "continue.\n")
    a("And there is a second reason to move early that has nothing to do with cost. "
      "**Inelastic demand under crisis conditions produces bad procurement.** Things get "
      "deployed at scale because they are available, not because they were verified — "
      "which is how the world ends up discussing ocean iron fertilisation. The value of "
      "settling the fluorine mass balance standard now, calmly, is that when the hurry "
      "comes there is a method that has been checked, rather than whichever one sells "
      "fastest.\n")
    a("That, rather than any market forecast, is the strongest reason to treat this as "
      "an industry now: **not because it will be cheaper, but because a verified method "
      "is only buildable while there is still time to verify it.**\n")

    a("### Where the analogy breaks: two different cost curves\n")
    a("This is the part that decides what to build first, and it is usually skipped.\n")
    a("Solar got cheap because of Wright's law — cost falls a fixed percentage per "
      "doubling of cumulative production — and Wright's law applies to **manufactured, "
      "modular, repeated units**. It does not apply to bespoke civil engineering, which "
      "has historically shown the opposite: nuclear construction got *more* expensive "
      "with experience.\n")
    a("The programme above contains both, and they will behave differently:\n")
    a("| | Cost curve | Which parts |")
    a("|---|---|---|")
    a("| **Manufactured and modular** | falls with deployment | diversion sensors, "
      "ion-exchange and regeneration skids, mechanochemical destruction reactors, "
      "monitoring and telemetry, flow-proportional samplers |")
    a("| **Bespoke civil works** | flat or rising | the wetland and its forebay, the "
      "interceptor retrofit, open channels, land reclamation |")
    a("")
    a("Which produces the same sequencing as section 7 arrived at from a completely "
      "different direction: **do the instrumented, modular things first** — they are "
      "cheap now, they get cheaper, and they are the exportable part. **Do the civil "
      "works last** — they will not get cheaper and they need the measurements to be "
      "specified correctly anyway.\n")
    a("It also says which half is the industry. Nobody exports a Danish wetland. They "
      "export the sensor, the skid, the reactor and the standard.\n")

    a("### The failure mode this creates, said plainly\n")
    a("An industry whose revenue grows with the pollution acquires an interest in the "
      "pollution continuing. This is not a hypothetical: it is the standing critique of "
      "waste incineration, which needs a waste stream to burn and has lobbied "
      "accordingly, and of carbon offsetting.\n")
    a("Build import-fed destruction capacity in Denmark and you create a domestic "
      "constituency whose business case is that PFAS keeps being manufactured "
      "somewhere. That constituency will, in the ordinary way of things, turn up in the "
      "consultation on the restriction dossier.\n")
    a("The antidote is a sequencing condition, and it should be written down before "
      "anything is built:\n")
    a("> **Source restriction leads; destruction capacity follows.** Capacity sized to "
      "the legacy stock and the reserved uses, not to a projected flow. A destruction "
      "industry scaled to a *continuing* input is not a clean-up industry — it is a "
      "disposal service for a business model that should have ended.\n")
    a("The same test distinguishes the good version of the fluorspar argument from the "
      "bad one. Recovering fluorine from a **finite legacy stock** is mining a waste "
      "dump, which is unambiguously good. Recovering it from an **ongoing production "
      "stream** is a subsidy to that production, dressed as circularity.\n")

    # ================================================================ ASK
    a("## Who would have to do what\n")
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
        ("The bay's ten municipalities",
         "A joint body whose jurisdiction is the bay. There is currently none, and the "
         "asymmetry between who discharges and who receives is the reason there needs "
         "to be."),
        ("Miljøstyrelsen",
         "Raise the required videnniveau for large structures. Add FOG and TOC to the "
         "determinands. Extend benthic sampling into autumn. Fund a fedtemøg index."),
        ("Anyone organising locally",
         "A community screening is a licence request, not a campaign — ask the "
         "distributor's educational arm. And the more useful evening is the local one: "
         "Korsør, then a map of the bay, then the question of who decides."),
        ("Denmark, at EU level",
         "Support the 6PPD restriction dossier. Ask for a copper product standard for "
         "brake pads. Treat the PFAS limits as a floor."),
    ]:
        a(f"| **{lvl}** | {ask} |")
    a("")

    # ================================================================ HONEST
    a("## What would make this wrong\n")
    a("A programme that cannot be refuted is not a programme. Each of these would "
      "damage the argument above, and each is testable:\n")
    for t in [
        "**If flow-proportional sampling at the largest structures finds loads close to "
        "the typetal**, then the concentration argument fails, the overflow term really "
        "is 0.6%, and the priority should go back to diffuse sources.",
        "**If autumn benthic sampling finds no die-off beyond what the spring survey "
        "implies**, the ratchet mechanism is wrong and the March–May window was "
        "adequate after all.",
        "**If a year-round fedtemøg index shows a clean summer peak and a quiet "
        "November**, then the seasonal argument here is wrong and the existing "
        "monitoring windows were correctly placed.",
        "**If iltsvind extent regresses cleanly on load once weather is controlled "
        "for**, the nitrogen-dominant model is vindicated and the state-dependence "
        "argument is unnecessary.",
        "**If retention in Køge Bugt disappears on a 1 km regional model**, the "
        "accumulation mechanism loses its main quantitative support.",
    ]:
        a(f"- {t}")
    a("")
    a("Four of those five need no new instruments and no new money. That is the "
      "position this document is arguing from: not that it is right, but that it has "
      "been cheap to check for thirty years and nobody has checked.\n")

    a("## What we would be asking for, said plainly\n")
    a("Not a lower number. A coast, a fjord and an inner sea where the structural "
      "life comes back — where there is eelgrass to walk past, weed with a holdfast "
      "instead of a film, fish worth catching, and a November shoreline that does "
      "not smell of putrefaction. That is the goal, and it is `T1` through `T5` "
      "said without the letters.\n")
    a("Nitrogen loading is at most a proxy for it, and a poor one, because a system "
      "can hit its nitrogen target and stay dead. So can every other single number "
      "on this page. **The measure of success is the four words in Part One, and "
      "three of them are not yet measured** — which makes building the outcome "
      "record the first item, not the last.\n")

    a("---\n")
    a("*Figures generated by `scripts/programme.py`, `scripts/rivermap.py` and "
      "`scripts/programme_map.py`. Every number traces to an investigation page; the "
      "arguments do not. Sources for the treatment efficiencies are the stormwater "
      "pond and biofilter literature cited inline; sources for the chemical status are "
      "ECHA, the Danish Environmental Protection Agency and the September 2025 EU water "
      "agreement.*")

    path = os.path.join(ROOT, "docs", "PROGRAMME.md")
    text = "\n".join(o)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    log(f"wrote docs/PROGRAMME.md ({len(text):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
