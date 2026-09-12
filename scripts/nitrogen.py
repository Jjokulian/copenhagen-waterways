#!/usr/bin/env python3
"""Generate docs/NITROGEN.md - what reaches the sea, and how the numbers are made.

The published figure everyone quotes is that agriculture accounts for about seven
tenths of the nitrogen. This document takes that apart, not by disputing the
measurements but by asking three questions the percentage cannot survive:

  * a share of WHAT - what is the denominator, and is the set of sources closed?
  * what is each number an estimator OF, as opposed to what it is labelled?
  * is nitrogen mass the right currency for oxygen depletion at all?

Every number on the page is a checked entity (see LIVE_NUMBERS.md):

  * read from data - data/derived/*.json, data/raw/national/*, and the registers
    data/manual/monitoring.json and nitrogen_pathways.json;
  * read out of a document - data/manual/nitrogen_readings.json, or a {read:}
    reading. Each carries the exact phrase it sits in, and this script refuses to
    write the page unless that phrase occurs in the pinned text of the source;
  * a chemistry constant - data/manual/nitrogen_constants.json;
  * or arithmetic on those.

Every assertion is a checked claim (LIVE_NUMBERS.md section 11), registered in
data/manual/claims.d/w1-ni.json with what it rests on. Nothing is carried as a
quotation of this page's own past: what could not be justified was retired to
docs/ARCHIVE.md and replaced with what can be.

Quotations are checked against the pinned documents too: a number inside a quote
is a {read:} reading, and a quote without one is refused unless it occurs in the
pin.

Usage:  python3 scripts/nitrogen.py
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, MANUAL, RAW, ROOT, log, read_json, write_doc
import claims
import live

KOEGE = ["København", "Hvidovre", "Tårnby", "Brøndby", "Vallensbæk",
         "Ishøj", "Greve", "Solrød", "Køge", "Stevns"]
KOEGE_NORTH = {"København", "Hvidovre", "Tårnby", "Brøndby"}
KOEGE_BOX = (12.10, 55.28, 12.80, 55.66)
PLANT_MIN_PE = 10000
STRAITS = ("oresund_s", "drogden", "oresund_n", "storebaelt")
VOL = "Vand_(m3/ aar)"

CL = claims.load()[0]
READ = live.live_json(os.path.join(MANUAL, "nitrogen_readings.json"))
_pins = {}
# a claim the page asserts: one span inside one paragraph, registered in w1-ni.json
C, B, E = live.claim, live.claim_begin, live.CLAIM_END


def _norm(t):
    """A pin as text: for a web page, HTML entities decoded and tags dropped; for any
    pin, whitespace collapsed. (A PDF's text keeps its '<' and '>' - stripping
    "tags" there would eat the prose between a stray pair.)"""
    head = t[:4000].lower()
    if "<html" in head or "<!doctype" in head:
        t = re.sub(r"<[^>]+>", " ", html.unescape(t))
    return re.sub(r"\s+", " ", t).strip()


def _pin(sid):
    if sid not in _pins:
        _pins[sid] = _norm(claims.pin_text(CL, sid))
    return _pins[sid]


def rv(key):
    """A value read out of a pinned document - refused unless its phrase is there."""
    e = READ["pinned"][key]
    if _norm(e["phrase"]) not in _pin(e["source"]):
        raise live.Unjustified(f"nitrogen_readings.json pinned.{key}: the phrase "
                               f"'{e['phrase']}' is not in the pinned text of {e['source']}")
    return e["value"]


def quote(sid, phrase):
    """A verbatim quotation, refused unless it occurs in the pinned document."""
    if _norm(phrase) not in _pin(sid):
        raise live.Unjustified(f"quotation not found in the pinned text of {sid}: '{phrase}'")
    return phrase


def quote_n(sid, shown, phrase):
    """A verbatim quotation carrying a number: the number is a checked reading."""
    marked = claims.resolve(CL, "{read:%s:%s|%s}" % (sid, shown, phrase), {})[0]
    i = phrase.index(shown)
    return phrase[:i] + marked + phrase[i + len(shown):]


def reading(sid, shown, phrase):
    """A number read out of a pinned document, as a checked reading."""
    return claims.resolve(CL, "{read:%s:%s|%s}" % (sid, shown, phrase), {})[0]


def verify(sid, phrase, *shown):
    """A register value confirmed against the pinned document it came from."""
    quote(sid, phrase)
    for s in shown:
        if s not in phrase:
            raise live.Unjustified(f"{sid}: '{s}' is not in the checked phrase '{phrase}'")


def dk(v):
    """A value in Danish decimal notation, as the documents print it."""
    return f"{float(v):g}".replace(".", ",")


def param(name):
    return claims.resolve(CL, "{param:%s}" % name, {})[0]


_MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"


def ordinal_dates(s):
    """'1 March' -> '1st March': a calendar day, written as a date."""
    def o(m):
        n = int(m.group(1))
        suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suf} {m.group(2)}"
    return re.sub(rf"\b(\d{{1,2}}) ({_MONTHS})\b", o, s)


def koege_tables():
    """Who can actually discharge into Køge Bugt, from the national register.

    Counts and sums are computed here from the layer and carried as live values of
    that file (paths under `koege.`), declared in K-NITROGEN-KOEGE; the layer's
    feature count is `n_features`, declared in K-NI-RBU-POINTS."""
    codes = read_json(os.path.join(MANUAL, "codelists.json"))["bygvaerkstype"]
    path = os.path.join(RAW, "national", "punkt_rbu_udl.geojson")
    if not os.path.exists(path):
        return None
    raw = {k: {"sep": 0, "comb": 0, "vol": 0.0} for k in KOEGE}
    feats = read_json(path)["features"]
    n_points = live.live(len(feats), path, "n_features")
    for f in feats:
        p, c = f["properties"], f["geometry"]["coordinates"]
        k, t = p.get("komm_navn"), p.get("bgv_type")
        if k not in KOEGE:
            continue
        if not (KOEGE_BOX[0] <= c[0] <= KOEGE_BOX[2] and KOEGE_BOX[1] <= c[1] <= KOEGE_BOX[3]):
            continue
        if codes.get(t, {}).get("combined_sewer"):
            raw[k]["comb"] += 1
            raw[k]["vol"] += p.get("vol_sb") or 0
        elif t in ("SE", "SF"):
            raw[k]["sep"] += 1
    del feats
    st = {k: {m: live.live(v[m], path, f"koege.{k}.{m}") for m in v} for k, v in raw.items()}

    plants = []
    rp = os.path.join(RAW, "national", "punkt_rens_udl.geojson")
    if os.path.exists(rp):
        for f in live.live_json(rp)["features"]:
            p, c = f["properties"], f["geometry"]["coordinates"]
            if (p.get("komm_navn") in KOEGE and (p.get("godk_pe") or 0) >= PLANT_MIN_PE
                    and KOEGE_BOX[0] <= c[0] <= KOEGE_BOX[2]
                    and KOEGE_BOX[1] <= c[1] <= KOEGE_BOX[3]):
                plants.append((p.get("pkt_navn"), p["godk_pe"], p.get("komm_navn")))
    plants.sort(key=lambda x: -x[1])
    return st, plants, path, n_points


def surplus_audit(mon):
    """Section 2's audit of what field surplus is made of."""
    o = []
    w = o.append
    q1 = quote("SR353", "En vigtig modelvariabel i DK-QNP modellen til beregning af tilførsel "
                        "af total diffus kvælstof er det årligt beregnede kvælstofoverskud "
                        "på ’mark-niveau’.")
    q2 = quote_n("SR353", "6.7", "Der er således – for perioden som helhed - en meget stærk, "
                                 "signifikant lineær relation mellem det nationale markoverskud "
                                 "og den samlede, normaliserede kvælstoftransport fra diffuse "
                                 "kilder (Figur 6.7, D).")
    q3 = quote_n("SR353", "6.7", "relationen vist i Figur 6.7 D indikerer")
    w("### The model's deciding input is itself a residual, and no field's balance is measured\n")
    w(C("C-NI-SR353-INPUT", "DCE's DK-QNP model computes the diffuse nitrogen load over the ungauged "
        "part of the country. Its own methods chapter names the key input:") + "\n")
    w(f"> *\"{q1}\"*\n> — Thodsen et al. 2019, [DCE SR353](https://dce2.au.dk/pub/SR353.pdf), "
      "page 34\n")
    w("The **field surplus** (*markoverskud*). " + C("C-NI-SR353-RELATION", "And chapter 6 of the "
      "same report presents this as a result:") + "\n")
    w(f"> *\"{q2}\"*\n")
    w(C("C-NI-FIG67", "**A variable that is an input to the model is correlated with the model's "
        "output, and the correlation is reported as a finding.** This does not make the attribution "
        "wrong. It makes `Figur 6.7 D` unable to evidence it.") + "\n")
    w("#### And that is a much narrower claim than it first looks\n")
    w(C("C-NI-SR353-QUALIFY", "**DCE qualify the figure themselves.** Right after presenting the "
        "relation, SR353 says that not all fjord catchments respond equally quickly — Mariager Fjord "
        "and parts of Limfjorden reduced their diffuse load *less* than "
        f"*\"{q3}\"*, citing two papers by Windolf and colleagues from 2012. They are pointing at "
        "the figure's limits, not resting on it.") + "\n")
    w(C("C-NI-WINDOLF-UNREAD", "A catchment-and-estuary study by Windolf, Blicher-Mathiesen, "
        "Carstensen & Kronvang, *Environmental Science and Policy*, 2012 "
        "([10.1016/j.envsci.2012.08.009](https://doi.org/10.1016/j.envsci.2012.08.009)), addresses "
        "exactly how a fall in the surplus shows up in measured load. Its text could not be read "
        "here — the publisher's copy is paywalled and the one open copy listed for it has been "
        "withdrawn — so this page uses none of its findings.") + "\n")
    w(C("C-NI-BOGESTRAND", "DCE also record that the DK-QNP method has a regional bias — "
        "overestimating nitrogen concentrations in western Denmark, tending to underestimate in the "
        "east — and correct the modelled monthly loads for it by region.") + " "
      + C("C-NI-VALIDATION-OPEN", "So the model has been evaluated. Whether it is validated against "
          "gauged catchments held out of its fitting has not been established here.") + "\n")
    w(C("C-NI-NARROW", "**So the established claim is narrow:** *one figure, in one monitoring "
        "report, is structurally unable to support the inference it is used for.* The claim **not** "
        "established is that the attribution lacks evidence — and the independent support for it, "
        "which the studies above could supply, is not established here either.") + "\n")

    rows = [("mineral fertiliser", "mineral"), ("manure + sludge", "manure"),
            ("biological fixation", "fixation"), ("seed", "seed"),
            ("atmospheric deposition", "deposition")]
    y0, y1 = rv("t34_year_first"), rv("t34_year_last")
    total13 = sum(rv(f"t34_2013_{k}") for _, k in rows)
    w("#### What \"field surplus\" is, in facts and observations\n")
    w(C("C-NI-SURPLUS-IDENTITY", "It is an accounting identity, not a measurement.") + " From "
      "[DCE SR120](https://dce2.au.dk/pub/SR120.pdf) Table 3.4, kg N/ha, whole country "
      "(each value checked against the pinned report; the 2013 total is the sum of its inputs, "
      "because that cell extracts garbled):\n")
    w("| | 1991 | 2005 | 2013 |\n|---|---|---|---|")
    for label, k in rows:
        w(f"| {label} | {rv(f't34_1991_{k}')} | {rv(f't34_2005_{k}')} | {rv(f't34_2013_{k}')} |")
    w(f"| **total supplied** | **{rv('t34_1991_total')}** | **{rv('t34_2005_total')}** | **{total13}** |")
    w(f"| harvested nitrogen | {rv('t34_1991_harvest')} | {rv('t34_2005_harvest')} | {rv('t34_2013_harvest')} |")
    w(f"| **= field surplus** | **{rv('t34_1991_surplus')}** | **{rv('t34_2005_surplus')}** | **{rv('t34_2013_surplus')}** |")
    w("")
    w(C("C-NI-SURPLUS-TERMS", "And SR120 says what each term is made of: **mineral fertiliser** from "
        f"national sales statistics, minus an estimated {rv('public_grounds_t_n'):,} t N assumed to go "
        "to public grounds, forests and private gardens — a stated constant; **manure** from livestock "
        "**counts** by category, times a nutrient content per category that follows *\""
        f"{quote('SR120', 'de til en hver tid gældende normer')}\"* — the norms in force at the time, "
        "set by regulation; **yields** from the harvest census, with roughage known to be "
        f"overestimated, so an assumed {rv('shrinkage_fodder_pct')}% shrinkage for maize, grass and "
        f"catch crops and {rv('shrinkage_permanent_grass_pct')}% for permanent grass; **crop nitrogen "
        "content** from the norm tables of the *Fodermiddeltabeller* of 1992, 1995, 2000 and 2005, "
        "with cereals *\"" + quote("SR120", "korrigeres hvert år efter de analyser Videncenter for "
                                   "Svineproduktion foretager") + "\"* — corrected every year from "
        "analyses by the pig industry's own research centre; and **atmospheric deposition**, whose "
        "method is not read here.") + "\n")
    w(C("C-NI-NO-FIELD", "**No field's nitrogen balance is observed.** Every term is a register "
        "count, a sales total or an area times a coefficient, and the surplus is what is left over; "
        "the one measurement inside it is the annual analysis of cereal nitrogen.") + "\n")
    w("#### The consequence is documented in the sources themselves\n")
    w(C("C-NI-NORM-STEPS", "Because the coefficients are administrative, the published figures move "
        f"when they move, with no change in any field. In **1999** the nitrogen norm was cut "
        f"{rv('norm_cut_1999_pct')}%, dropping the quota by about {rv('norm_cut_1999_t_n'):,} t N, "
        f"while grass norms changed at the same time, raising it by about "
        f"{rv('grass_norm_1999_t_n'):,} t N a year; SR120 calls the result a *\""
        f"{quote('SR120', 'spring')}\"* — a step — in the compiled nitrogen quotas, the limit on what may be "
        "applied, not the field balance itself. In **2012** the method for "
        "nutrients removed at harvest changed from dry-matter yield to feed units, and SR120 records "
        f"that its phosphorus net-input figures *\"{quote('SR120', 'er steget lidt ift. de tidligere opgørelser')}\"* "
        "— rose, from the method change alone. And **2013** is published **twice**, differing only "
        f"in which register the fertiliser figure came from: **{rv('t34_2013_surplus')} kg N/ha** "
        f"from the *gødningsregnskaber*, **{rv('t34_2013_ds_surplus')}** from Danmarks Statistik.") + "\n")
    span = y1 - y0
    rate = (rv("t34_2013_surplus") - rv("t34_1991_surplus")) / span
    worth = (rv("t34_2013_surplus") - rv("t34_2013_ds_surplus")) / -rate
    w(C("C-NI-REGISTER-CHOICE", f"That last one sets the scale. The surplus fell "
        f"{rv('t34_1991_surplus')} → {rv('t34_2013_surplus')} kg N/ha over {span} years, "
        f"{rate:.1f} kg/ha/yr. **Choosing which register to read is worth {worth:.1f} years of the "
        "trend** — small against the whole decline, not small against a year of it.") + "\n")
    w(C("C-NI-OVERSEER", "A coefficient model of farm nitrogen has been reviewed as a whole "
        "elsewhere: New Zealand's Overseer. The review panel, in its ministry's words, *\""
        + quote("NI-MFE-OVERSEER", "concluded they did not have confidence in") + "\"* Overseer's "
        "estimates of nitrogen lost from farms across the full range of the country's climates, "
        "topographies and land uses.") + "\n")
    w(C("C-NI-CHAIN", "**So the chain reads:** norm tables × register counts → *markoverskud*, a "
        "residual → input to DK-QNP → diffuse load over the ungauged area → summed into total diffuse "
        "transport → correlated with *markoverskud* → \"a very strong, significant linear "
        "relation\". Each step is defensible alone. The composite cannot evidence what the last "
        "step is used to evidence.") + "\n")
    return "\n".join(o), (total13, rate)


def two_subtractions(mon, agri, dl):
    o = []
    w = o.append
    w(f"## 2b. Two subtractions, and the ~{agri:.0f}% is not the one people think\n")
    w(C("C-NI-TWO-SUBTRACTIONS", "It is easy to run together the **field balance** and the **load "
        "apportionment**. They are different operations on different quantities, and the headline "
        "share is the second, not the first.") + "\n")
    w(f"| | **A — field surplus (*markoverskud*)** | **B — the ~{agri:.0f}% share** |\n|---|---|---|")
    w("| what it subtracts | harvest from inputs | point sources and background from river transport |")
    w("| units | kg N/ha | t N/yr, reported as a share |")
    w("| kind | **norm product** — counts × regulatory coefficients | **residual** — what is left "
      "after naming what could be named |")
    w("| fails when | a norm changes with no change in any field | an unnamed source exists |")
    w("")
    w(C("C-NI-COUPLED", "They are coupled, which is why they get confused: **A is an input to "
        "DK-QNP, and DK-QNP supplies B's river-transport term over the modelled "
        f"{dl['area_modelled_pct']}% of the country.** So A partly determines the minuend of B. But "
        f"the ~{agri:.0f}% itself is B.") + "\n")
    w("### B, from its own methods note\n")
    w(C("C-NI-MSFD-DEF", "The construction, in DCE's own words ([`MSFD notat 2-8`](https://dce.au.dk/"
        "fileadmin/dce.au.dk/Udgivelser/Havstrateginotater/2-8_MSFD_notat_tilfoersel_NPO.pdf)):") + "\n")
    w(f"> *\"{quote('MSFD28', 'Diffuse tilførsler (inkl. spredt bebyggelse) minus baggrundsbidraget (diffus antropogen)')}\"*\n")
    w("with the subtracted terms defined there as:\n")
    w("- **Natural background** — *\"" + quote("MSFD28", "et mål for den diffuse tilførsel der "
      "vil komme fra oplandet, hvis der ikke var menneskelig aktivitet og som bestemmes i "
      "mindre oplande med lav antropogen påvirkning") + "\"*.")
    w("- **Diffuse load** — *\"" + quote("MSFD28", "belastning fra dyrkede arealer inkl. spredt "
      "bebyggelse, da tilførsler fra spredt bebyggelse ofte er svær at adskille fra øvrige "
      "diffuse kilder") + "\"*.\n")
    q = quote_n("MSFD28", "5", "For de enkelte år opdeles den diffuse belastning ikke i den "
                               "naturlige baggrundsbelastning og den diffuse belastning ikke, da "
                               "opdelingen specielt for fosfor og organisk stof er usikker, men "
                               "det for 5 års gennemsnit er lavet en opdeling.")
    w(C("C-NI-MSFD-FINDINGS", "Three things follow, all from the document rather than from us. **The "
        "category is defined as unseparated**: scattered dwellings sit inside the agricultural term "
        "*because they could not be separated from it*, as the definition states. **The subtrahend "
        "is a transferred measurement**: background is not measured in the catchment it is "
        "subtracted from — small low-impact catchments stand in for the rest, a basket assumption at "
        f"the centre of the arithmetic. And **the split is not annual**: *\"{q}\"* The "
        "background/anthropogenic division is made only on multi-year averages, because the split is "
        "too uncertain year by year, **so an annual agricultural share is not a thing this method "
        "produces**, and any year-on-year movement in a published share is an artefact of "
        "interpolating that split.") + "\n")
    w("### So how does the construction perform against things that were measured?\n")
    w(C("C-NI-PERFORMANCE-UNREAD", "This is the question the rest of it turns on: whether a fall in "
        "the surplus shows up as a fall in the measured load, catchment by catchment. DCE's own "
        "qualification above says it did not everywhere — Mariager Fjord and parts of Limfjorden "
        "responded less than the national relation indicates. The study that quantifies it per "
        "catchment could not be read here, so the size of the shortfall is not given on this "
        "page.") + "\n")
    return "\n".join(o)


def manure_check(M):
    """The prediction in 2c, checked against two open registers instead of waited on."""
    o = []
    w = o.append
    lim = M["over_limit"]
    a14, a17 = lim["1.4"], lim["1.7"]
    matched = live.step("K-SUBSET-SHARE", M["animal_units_on_matched"] / M["animal_units_total"] * 100)
    no_land = live.step("K-SUBSET-SHARE", (M["cvrs_with_animals"] - M["cvrs_with_both"])
                        / M["cvrs_with_animals"] * 100)
    w("### The prediction is checkable, and the check has been run\n")
    w(C("C-NI-JOIN", "*A quota transfers the constraint to the manure only when a holding's own land "
        "cannot take what its animals produce.* That is not something to wait for: both halves are in "
        "open registers and they join on the company number. The livestock register carries "
        "**animal units** — `DE` — against the business that runs each herd; the field-parcel "
        "register carries the same business's declared hectares. `scripts/manure.py` fetches both "
        "and divides.") + "\n")
    w("| | |\n|---|---:|")
    w(f"| Livestock register rows (a row is one herd registration, not a site) | {M['sites']:,} |")
    w(f"| Businesses keeping animals (distinct CVR numbers) | {M['cvrs_with_animals']:,} |")
    w(f"| …of which also have more than one declared hectare | **{M['cvrs_with_both']:,}** |")
    w(f"| Animal units on rows carrying a CVR number | {M['animal_units_total']:,.0f} |")
    w(f"| …on businesses with declared land | {M['animal_units_on_matched']:,.0f} ({matched:.0f}%) |")
    w(f"| Median animal units per declared hectare | {M['percentiles_de_per_ha']['50']:.2f} |")
    w(f"| 90th percentile | {M['percentiles_de_per_ha']['90']:.2f} |")
    w(f"| 99th percentile | {M['percentiles_de_per_ha']['99']:.1f} |")
    w("")
    w(C("C-NI-HARMONY", f"**Above the pre-2017 harmony line of {param('harmony_1_4')} animal units per "
        f"declared hectare sit {a14['businesses']:,} businesses — "
        f"{a14['share_of_businesses_pct']:.0f}% of the businesses with both animals and more than one "
        f"declared hectare — and they hold {a14['share_of_herd_pct']:.0f}% of the CVR-registered "
        "herd.** That share is a floor: herds on businesses with no matched land stay in its "
        f"denominator and can never count as above the line. At {param('harmony_1_7')} it is "
        f"{a17['businesses']:,} businesses and {a17['share_of_herd_pct']:.0f}% of that herd.") + "\n")
    w(C("C-NI-MANURE-READING", "Read it for what it is. The harmony line is a retired legal ceiling, "
        "not a measured capacity of the land, and declared area is not spreading area — so this "
        "describes manure pressure, not a physical necessity that the manure leave the holding. It "
        "suggests that export and inter-farm contracts carry a large part of the herd, and no public "
        "register of those contracts is known to this project.") + "\n")
    w(C("C-NI-JOIN-LIMITS", "*What this does not establish.* Declared area is land declared for area "
        "support, which is not the same as every hectare a business may spread on: rented-in land "
        "can be missing, and a business that buys spreading capacity from a neighbour looks "
        f"land-poor here and is compliant in law. {no_land:.0f}% of animal-keeping businesses have no "
        "more than one declared hectare in this join, which is either genuine landlessness or a "
        "failed match through holding companies. And the thresholds are the old harmony units: "
        "Denmark now regulates in kilograms of nitrogen per hectare, so these indicate the pressure "
        "rather than test compliance.") + "\n")
    w(C("C-NI-PROVENANCE", "*Provenance.* Both layers are open and need no key. They were located and "
        "documented by the sibling project [danish-livestock](https://github.com/Jjokulian), which "
        "mapped the livestock layer; this project fetches them from the same primary source rather "
        "than copying its data, and the two traps it found — an encoding the server lies about, and "
        "herd-size columns that do not partition — are handled in `scripts/manure.py` because of "
        "that documentation.") + "\n")
    return "\n".join(o)


def whose_nitrogen(cl, total13):
    """Section 2c: the question the load apportionment cannot answer, and the two halves of
    the input side that can be counted instead."""
    y = cl["years"]
    last = y["2025"]
    manure_share = rv("t34_2013_manure") / total13 * 100
    o = []
    w = o.append
    w("## 2c. Whose nitrogen is it, and can the ledger say?\n")
    w(C("C-NI-WHOSE", "**How much of this is because Denmark keeps animals?** The apportionment above "
        "has no livestock term. Diffuse load is one bucket — cultivated land *including scattered "
        "dwellings*, by DCE's own definition — and the national accounts do not separate the "
        "fractions by measurement: a nitrate ion that passed through a pig is the same ion as one "
        "out of a bag. **So the question is one for accounting**, and the accounting has two "
        "halves.") + "\n")
    w(C("C-NI-HALF-ONE", "**Half one: what is applied.** From the field balance above — manure and "
        f"sludge **{rv('t34_2013_manure')} kg N/ha** against mineral fertiliser "
        f"**{rv('t34_2013_mineral')}** in 2013, out of {total13} supplied; in 1991 it was mineral "
        f"{rv('t34_1991_mineral')} against manure {rv('t34_1991_manure')}. So {manure_share:.0f}% of "
        "the nitrogen put on Danish fields in 2013 arrived as manure, and that part is not optional "
        "in the way a bag is: it exists because the animals do, and it has to be spread, exported or "
        "processed.") + "\n")
    w(C("C-NI-FEED-RULE", "**Half two: what the rest is spread on.** Mineral fertiliser on a barley "
        "field grown for pigs is nitrogen spent on livestock as surely as the slurry beside it. "
        "Danish crop statistics record what was grown rather than what it was fed to, so this is a "
        "range on a stated rule rather than a number (`scripts/cropland.py`, from Statistics Denmark "
        "table `AFG6`):") + "\n")
    w("| | 1990 | 2000 | 2010 | 2025 |\n|---|---:|---:|---:|---:|")
    for label, key in [
        ("Grass, whole-crop and fodder roots — **unambiguously feed**", "floor_pct"),
        ("…plus cereals and pulses to maturity", "central_pct"),
        ("…plus rapeseed, whose meal is feed", "ceiling_pct"),
        ("**Potatoes, sugar beet, horticulture — food people eat**", "direct_food_pct"),
    ]:
        w("| " + label + " | " + " | ".join(
            f"{y[k][key]:.1f}%" for k in ("1990", "2000", "2010", "2025")) + " |")
    w("")
    w(C("C-NI-FEED-SHARE", f"**Between {last['central_pct']:.0f}% and {last['ceiling_pct']:.0f}% of "
        f"Danish farmland grows feed, and {last['direct_food_pct']:.1f}% of it grows food that people "
        f"eat directly** in 2025, against {y['1990']['direct_food_pct']:.1f}% in 1990. The shares have "
        "barely moved since 1990.") + " "
      + C("C-NI-HERD-INPUT", "Set that beside half one and, if mineral fertiliser is spread in "
          "proportion to area, the input-side answer is not close: **the herd is behind most of the "
          "nitrogen applied to Danish soil — the manure directly, and most of the mineral fertiliser "
          "through the feed crops it is spread on.**") + "\n")
    w(C("C-NI-NOT-LOAD", "*What this does not establish.* An input share is not a load share: how "
        "much of a surplus reaches the sea varies by catchment — DCE's own qualification above shows "
        "fjords responding less than the national relation — so a share of what is applied cannot be "
        "converted into a share of what arrives. And the classification above is ours: the "
        "statistics do not record what a crop was fed to, cereals are the load-bearing assumption, "
        "and a reader who thinks Danish grain is mostly milled rather than fed should use the "
        f"{last['floor_pct']:.1f}% floor instead.") + "\n")
    w("### Which is why biogas is a carbon technology and not a nitrogen one\n")
    w(C("C-NI-BIOGAS", "The obvious hope is that digestion deals with it. It does not. **Anaerobic "
        f"digestion removes carbon, not nitrogen**: methane and {live.chem('CO2')} leave, and "
        "essentially all the nitrogen stays in the digestate — with *more* of it as ammonium than "
        "before, because digestion mineralises organic N. That is useful as fertiliser value and it "
        "is the opposite of removal. **The field is still the endpoint.**") + "\n")
    w(C("C-NI-EXITS", "What a biogas plant does supply is the thing the manure never otherwise has: "
        "**a collection point**. The manure is already gathered, homogenised and pumped, which is "
        "where nitrogen can be taken out — and there are only three kinds of exit:") + "\n")
    w("- " + C("C-NI-EXIT-CAPTURE", "**Capture it as a product.** Separate the digestate into fibre "
               "and liquid, then strip ammonia from the liquid into an ammonium salt — a concentrated, "
               "transportable fertiliser that can leave the catchment or displace Haber-Bosch "
               "nitrogen. The nitrogen is not destroyed; it is made portable, which is what the field "
               "balance needs."))
    w("- " + C("C-NI-EXIT-DESTROY", "**Destroy it, which is literally a reduction.** Nitrify then "
               "**denitrify** the liquid fraction and the nitrogen leaves as "
               f"{live.chem('N2')} — inert, and out of the reactive pool for good. This is the only "
               "true removal available, and it is the same reaction a constructed wetland performs "
               "slowly and for free. It costs energy, and a badly run plant emits "
               f"{live.chem('N2O')} instead, which trades a water problem for a climate one."))
    w("- " + C("C-NI-EXIT-BURN", "**Burn the fibre.** Destroys organic nitrogen and recovers "
               "phosphorus in ash, at the cost of flue-gas treatment. It is the P route more than the "
               "N route."))
    w("")
    mp = os.path.join(DERIVED, "manure.json")
    if os.path.exists(mp):
        w(manure_check(live.live_json(mp)))
    w("### What the law does to the herd, if the arithmetic binds\n")
    w(C("C-NI-L5", "The instruments are in the public record rather than in this analysis. `L 5`, the "
        "fertilisation law, passed on 2026-09-03, "
        + quote_n("POL-TV2-20260903", "119", "119 medlemmer af Folketinget stemte for loven")
        + ", " + quote_n("POL-TV2-20260903", "34", "mens 34 stemte imod") + " (TV 2) — what TV 2 "
        "called *\"" + quote("POL-TV2-20260903", "et massivt politisk flertal") + "\"*, a massive "
        "political majority. The ministry's December 2025 announcement gives each holding a quota for its "
        "discharges set by how much its catchment must cut, from 2027 (*\""
        + quote("POL-MGTP-20251203", "en kvote for deres udledninger ud fra") + "\"*), and calls the "
        "agreement a safety net under the Tripartite's land conversion (*\""
        + quote("POL-MGTP-20251203", "et sikkerhedsnet under den") + "\"*). Under the law, "
        "emission-based regulation replaces field regulation from 2027, and its sharper step, "
        "the kvælstofhammer, cannot strike before 2028 ([POLITICS.md](POLITICS.md)).") + "\n")
    w(C("C-NI-NOT-READ", "**This project has not read the statute**, so what follows is inference "
        "from those instruments and from the balance above, and it is offered as a prediction that "
        "can be checked rather than as a reading of the law.") + "\n")
    w(C("C-NI-PREDICT-MINERAL", "**A quota bites on mineral fertiliser first, because manure is not "
        "optional.** The bag is the free variable: a holding that must apply less nitrogen buys less "
        "of it. The slurry is already there, produced daily by animals that exist, and it has to be "
        "spread, stored, sold or processed. So the first years of a tightening quota look like a "
        "fertiliser reduction and leave the herd untouched.") + "\n")
    w(C("C-NI-PREDICT-TRANSFER", "**The constraint transfers when the quota falls below what the "
        "manure alone supplies.** At that point the arithmetic offers exactly four moves: fewer "
        "animals, more hectares to spread on, more nitrogen leaving in the crop, or **the manure "
        "nitrogen leaving the holding**. And this is where the design of the Tripartite matters more "
        "than its rhetoric: its main engine takes land *out* — wetland conversion, afforestation, "
        "set-aside — which raises manure nitrogen per remaining hectare with no change in any herd. "
        "**An area policy becomes a livestock policy without ever naming livestock.**") + "\n")
    w(C("C-NI-DEMAND", "So a byproduct that has to leave is the predictable consequence, and the "
        "market for it already half exists — inter-farm slurry contracts, separation plants, and the "
        "stripping route above, whose output is a concentrated ammonium salt that travels. **A quota "
        "is a demand curve for nitrogen capture**, in the way [PROGRAMME.md](PROGRAMME.md) argues the "
        "liability settlements are a demand curve for destruction — regulation creating an industry "
        "rather than only a cost.") + "\n")
    w("Three things have to be said with it, because each of them can make the prediction wrong:\n")
    w("- " + C("C-NI-CAVEAT-CATCHMENT", "**The quota is per catchment, so the export has to cross a "
               "catchment line.** Moving slurry from one farm to its neighbour changes whose paperwork "
               "it is and not what the receiving water gets. Only nitrogen that leaves the catchment — "
               "or leaves the reactive pool altogether — is a reduction where it is being counted."))
    w("- " + C("C-NI-BRAK", "**The pressure is capped by design.** The agreement fixes a "
               "*braklægningspunkt*, which *\"" + quote("POL-GP-20250619", "fungerer som et fastsat loft for")
               + "\"* how high the regulatory pressure can go in each coastal catchment.") + " "
           + C("C-NI-CAVEAT-BRAK", "That is exactly the point at which the squeeze on land would "
               "start forcing the herd, so where it is set decides whether any of the above ever "
               "happens."))
    w("- " + C("C-NI-CAVEAT-LOAD", "**And the load may not follow the input.** How much of a surplus "
               "reaches the sea varies by catchment, and DCE's own qualification shows fjords that "
               "responded less than the national relation. A herd reduction is an input reduction, "
               "and an input reduction is not yet a load reduction — which is the same objection this "
               "project makes to the standard account, applied to a measure it would otherwise be "
               "tempted to endorse."))
    w("")
    w(C("C-NI-BIOGAS-ANSWER", "So the answer to *can biogas fix it* is: not by itself, and yes as "
        "infrastructure. **Digestion without a nitrogen step returns every kilogram to the same "
        "fields in a more available form.** With separation and stripping, or with denitrification, "
        "the same plant becomes the only place in the chain where the nitrogen can be made to go "
        "somewhere else — which is the honest version of the claim that the herd sets a floor: it "
        "sets one **unless the manure nitrogen is given an exit that is not a field.**") + "\n")
    return "\n".join(o)


def koege_transport(mon):
    tr = live.live_json(os.path.join(DERIVED, "currents_transport.json"))
    va = live.live_json(os.path.join(DERIVED, "currents_validate.json"))
    ix = live.live_json(os.path.join(DERIVED, "currents_index.json"))
    band = next(b for b in tr["bands"] if b["label"] == "overflow-scale")
    lag = {int(x["lag_h"]): x for x in tr["lag"]}
    l6, l12 = lag[6], lag[12]
    slow = [p["underestimate_factor"] for p in va["points"] if p["point"] in STRAITS]
    sed = mon["sediment_release_events"]
    link, lyn = sed["oresund_fixed_link"], sed["lynetteholm"]
    y0, y1 = tr["period"][0][:4], tr["period"][1][:4]
    kb, os_ = ix["retention"]["koege_bugt"], ix["retention"]["oresund_s"]
    o = []
    w = o.append
    w("### But \"downstream\" is a claim about water, and it has been tested\n")
    w(C("C-NI-TRANSPORT", f"[CURRENTS.md](CURRENTS.md), on {tr['n_hours']:,} hours where the rain "
        "record and the current record overlap, gives the southward transport in the southern "
        "Sound:") + "\n")
    w("| | southward transport in the southern Sound |\n|---|---|")
    w(f"| baseline, all hours | **{tr['baseline_southward_pct']:.0f}%** |")
    w(f"| during overflow-scale rain ({band['hours']} h) | **{band['southward_pct']:.1f}%** — "
      f"{-band['vs_baseline_pp']:.0f} points *below* baseline |")
    w(f"| +{l6['lag_h']} h after the event | {l6['southward_pct']:.1f}% |")
    w(f"| **+{l12['lag_h']} h after the event** | **{l12['southward_pct']:.1f}%** — "
      f"{l12['vs_baseline_pp']:.0f} points *above* |")
    w("")
    w(C("C-NI-TRANSPORT-READ", "So the geometry is right about the plume and wrong about the event. "
        "**While the city is overflowing, the water runs north**: southward transport falls below "
        "baseline during overflow-scale rain and only clearly exceeds it "
        f"{l12['lag_h']} hours later, by which time the plume is diluted and no longer traceable to "
        "an outfall.") + " "
      + C("C-NI-FLUSH", f"And the current field flushes mid Køge Bugt over {ix['flush_distance_km']:g} "
          f"km in about {kb['flush_days_20km']:.0f} days, against {os_['flush_days_20km']:.1f} in the "
          "southern Sound, so what does arrive stays for months.") + "\n")
    w(C("C-NI-EVENT-VS-ACCUM", "That matters for what this whole section can claim. A load entering a "
        "bay that flushes slowly is a different quantity from a load entering one that flushes fast — "
        "and the timing means an event-based attribution (this overflow, that shoreline) is not "
        "supported, while an accumulated one may be.") + "\n")
    ratio = link["spill_limit_m3"] / lyn["first_dumped_m3"]
    w(C("C-NI-SPILL", "The same bay carries the largest release nobody argued about. The Øresund "
        f"fixed link's permitted spill — **up to {link['spill_limit_m3']:,} m³** of fines into the "
        f"water column at the bay's northern entrance, {link['period']} — against the "
        f"**{lyn['first_dumped_m3']:,} m³** released at Lynetteholm before dumping was stopped: "
        f"**{ratio:.0f} times**, and the larger one, as recorded in [OPEN_PROBLEMS.md](OPEN_PROBLEMS.md), "
        "a permit condition met rather than a controversy. Where that material went has not been "
        f"computed here: the current field used above covers {y0}–{y1} only, and underestimates "
        f"published peak currents in the straits by a factor of {min(slow):.1f} to {max(slow):.1f} "
        "by its own calibration.") + "\n")
    return "\n".join(o)


def main():
    P = live.live_json(os.path.join(MANUAL, "nitrogen_pathways.json"))
    paths = list(P["pathways"])
    mon = live.live_json(os.path.join(MANUAL, "monitoring.json"))
    K = live.live_json(os.path.join(MANUAL, "nitrogen_constants.json"))
    OF = live.live_json(os.path.join(DERIVED, "outfalls.json"))["layers"]
    ql, dl, ov = mon["quality_control"], mon["diffuse_load"], mon["overflow_reporting"]
    lv = list(ov["knowledge_levels"])
    # the register's values that its sources print, checked against the pins
    verify("DP02", "Niveau for usikkerhed på udledt stofmængde 135 % 100 % Niveau 3 55 % "
                   "Niveau 4 45 % Niveau 5 30 %",
           *[f"{int(x['uncertainty_pct'])} %" for x in lv if x["uncertainty_pct"]])
    ci, si = ql["acceptance_interval_combined_mg_per_l"], ql["acceptance_interval_separate_mg_per_l"]
    verify("DP02", "Kvælstof/Vandmængde 10-12 mg/l", f"{dk(ci[0])}-{dk(ci[1])}")
    verify("DP02", "Kvælstof/Vandmængde 1,8 -2,2", f"{dk(si[0])} -{dk(si[1])}")
    agri = rv("apportion_agriculture")
    unc = [x["uncertainty_pct"] for x in lv if x["uncertainty_pct"]]
    # the pinned summary gives shares for three lines; the rest it calls "even smaller"
    apportionment = [
        ("Agriculture", agri,
         f"**Residual.** (grab-sampled load over {dl['area_measured_pct']}% of the area + model "
         f"output over {dl['area_modelled_pct']}%) minus point sources minus the natural "
         f"background, with retention modelled at ±{dl['retention_uncertainty_pct_points'][0]}"
         f"-{dl['retention_uncertainty_pct_points'][1]} percentage points."),
        ("Natural background", rv("apportion_background"),
         "Determined in small catchments with little human impact and transferred to the rest — "
         "and the subtrahend that determines the residual above."),
        ("Treatment plants", rv("apportion_plants"),
         "**Reported effluent monitoring.** Flow-metered, routinely sampled. The best-measured "
         "line in the table."),
        ("Aquaculture and marine farms", None, "Reported, feed-balance based."),
        ("Separate stormwater", None,
         "Modelled volume × a concentration from a **1990** measurement programme."),
        ("Rain-dependent overflow", None,
         f"Modelled volume ({min(unc)}-{max(unc)}% stated uncertainty) × an assumed "
         "concentration, quality-controlled **against that same assumed concentration**."),
        ("Industry", None, "Reported."),
        ("Scattered dwellings", None, "Modelled from dwelling counts × assumed per-capita loads."),
    ]
    o = []
    w = o.append

    w("# What the sea actually receives\n")
    w("Generated by `scripts/nitrogen.py`. Every number on this page is read from data, from a "
      "document pinned by its hash, or computed from those, and links to where it came from.\n")
    w(C("C-NI-HEADLINE", f"The figure in circulation is that agriculture accounts for **{agri}% of "
        "nitrogen**.") + " "
      + C("C-NI-THREE-QUESTIONS", "This document does not dispute the measurements behind it. It "
          "asks three questions the percentage, as it is used, does not survive.") + "\n")

    # ---------------------------------------------------------------- 1. denominator
    w("## 1. There is no denominator\n")
    w(C("C-NI-PATHWAYS", "A percentage requires a closed set. Here is every pathway of reactive "
        "nitrogen to Danish marine waters this project could enumerate; the ranges are its own "
        "compilation, and the register behind them gives no source for each.") + "\n")
    w("| Pathway | kt N/yr | Basis |\n|---|---:|---|")
    quant = [p for p in paths if p["lo"] is not None]
    unq = live.live(len(paths) - len(quant), P._f, "pathways.n_unquantified")
    n_all = live.live(len(paths), P._f, "pathways.n")
    lo, hi = sum(p["lo"] for p in quant), sum(p["hi"] for p in quant)
    for p in paths:
        val = "**—**" if p["lo"] is None else f"{p['lo']:g} – {p['hi']:g}"
        if p.get("note_t"):
            note = re.sub(r"\{(\w+)(?::([^}]*))?\}",
                          lambda m: format(p[m.group(1)], m.group(2) or "g"), p["note_t"])
        else:
            note = (p.get("note") or "").replace("\n", " ").strip()
        name = str(p["pathway"])
        if name.startswith("N2 "):
            name = live.chem("N2") + name[2:]
        name = f"**{name}**" if p["lo"] is None else name
        w(f"| {name} | {val} | {str(p['status']).lower()} — {note} |")
    w("")
    w(C("C-NI-UNQUANTIFIED", f"**{unq} of {n_all} pathways carry no number at all**, including "
        "internal regeneration from sediment, which is not a \"source\" and so has no row in the "
        "apportionment quoted below.") + "\n")
    w(C("C-NI-LOWER-BOUND", f"The quantified subset sums to **{lo:.0f} – {hi:.0f} kt N/yr**. That is "
        f"not a range for the total. With {unq} pathways empty the honest statement is a lower "
        f"bound — total reactive nitrogen supply **≥ {lo:.0f} kt N/yr**, with no established upper "
        "bound — and therefore no denominator, and no percentages, until the empty rows are "
        "filled.") + "\n")
    dep = next(p for p in paths if str(p["pathway"]).startswith("Atmospheric deposition"))
    land = [p for p in paths if str(p["pathway"]).startswith("Danish land via")]
    land_lo, land_hi = sum(p["lo"] for p in land), sum(p["hi"] for p in land)
    w(C("C-NI-DEPOSITION", "Note the scale of what the apportionment leaves out. Atmospheric "
        f"deposition to Danish marine waters is put at {dep['lo']:g}–{dep['hi']:g} kt N/yr above, "
        f"comparable to the land-based waterborne supply of {land_lo:g}–{land_hi:g} kt, and it is not "
        "a line in the apportionment quoted below, which divides discharges to coastal waters by "
        "source.") + "\n")

    # ---------------------------------------------------- 2. estimator vs estimand
    w("## 2. The numbers are not estimators of what they are named\n")
    w(C("C-NI-RELABEL", "Each line of the published apportionment, relabelled by what actually "
        "produced it. The pinned summary gives shares for the first three lines and calls the rest "
        "*\"" + quote("DANVA-2024", "endnu mindre andele") + "\"* — even smaller shares:") + "\n")
    w("| Called | Actually is |\n|---|---|")
    for name, pct, what in apportionment:
        called = f"**{name}, {pct}%**" if pct is not None else f"**{name}** — no share in the pinned source"
        w(f"| {called} | {what} |")
    w("")
    w(C("C-NI-MEASURED-LINES", "Only the treatment-plant and industry lines are reported "
        "measurements. The rest are estimates, and the largest is a residual of estimates.") + "\n")
    w("### The validation is circular\n")
    w(C("C-NI-QC-RULE", f"Reported nitrogen divided by reported volume must fall within **{ci[0]}–{ci[1]} "
        f"mg/l** for combined sewers and **{si[0]}–{si[1]} mg/l** for separate ones. Outside that, *\""
        f"{quote('DP02', 'kontaktes den dataansvarlige med henblik på at få rettet eventuelle fejl')}"
        "\"* — the data owner is contacted to correct the error.") + "\n")
    w(C("C-NI-QC-CIRCULAR", f"{ql['consequence']} **The assumed concentration cannot be falsified by "
        "data collected under it.**") + "\n")
    audit, (total13, _) = surplus_audit(mon)
    w(audit)
    w("### And the estimator can return impossible values\n")
    w(C("C-NI-NEGATIVE", "The monitoring register records, without a citation: "
        f"{dl['estimator_pathology']} A residual whose error can exceed its own "
        "signal is published to one decimal place with no error bar.") + "\n")
    w(C("C-NI-DIFFUSE-BASIS", "Underneath it, by the same register's uncited figures: "
        f"**{dl['stream_stations']} stream stations** covering "
        f"**{dl['area_measured_pct']}%** of the country, the other **{dl['area_modelled_pct']}%** "
        "modelled. Load is grab samples plus linear interpolation, and in all three streams of the "
        "2018 validation study that method **always underestimated** — annual deviations "
        f"{dl['deviation_annual_pct'][0]}% to {dl['deviation_annual_pct'][1]}%, monthly deviations "
        f"reaching {dl['deviation_monthly_pct'][1]:+.0f}%. Retention, the largest single term, "
        f"carries **±{dl['retention_uncertainty_pct_points'][0]}–"
        f"{dl['retention_uncertainty_pct_points'][1]} percentage points**.") + "\n")
    w("### Overflow is modelled, and the deciding variable is not collected\n")
    w("| Knowledge level | Method | Stated uncertainty |\n|---|---|---:|")
    for x in lv:
        u = f"{x['uncertainty_pct']}%" if x["uncertainty_pct"] else "—"
        w(f"| {x['level']} | {x['method']} | {u} |")
    w("")
    w(C("C-NI-DP02-LEVELS", "The overflow volume is modelled at one of these knowledge levels, each "
        "with the uncertainty Miljøstyrelsen's DP02 states for it.") + " "
      + C("C-NI-PULS-FIELDS", "Among the data DP02 requires in PULS for an overflow, the only "
          "per-event measure is *\"" + quote("DP02", "Antal overløb (antal/år)") + "\"* — the number "
          "of overflows a year. No flow rate, peak or threshold crossing is among them, so a "
          "high-flow event that scours accumulated basin sediment cannot be distinguished from a "
          "small dilute one.") + "\n")
    w(C("C-NI-THRESHOLD", "That matters because sediment resuspension is a **threshold** in flow, "
        "not a frequency of events. Below the critical shear stress the deposit stays in the basin; "
        "above it, the accumulated material leaves — and the typetal report finds that *\""
        + quote("TYPETAL22", "en væsentlig andel af de adsorberende stoffer bliver fanget i sedimentet "
                "i regnvandsbassiner") + "\"*, a significant share of the adsorbing substances caught "
        "in basin sediment. Multiplying an annual volume by an average concentration cannot "
        "represent that, and the resulting error is one-directional and largest in the wettest "
        "years.") + "\n")
    w(two_subtractions(mon, agri, dl))
    w("### Which sharpens what the residual absorbs\n")
    w(C("C-NI-RESIDUAL-ABSORBS", f"Section 1 lists **{unq} of {n_all} pathways carrying no number at "
        "all**. Every one of them that reaches a river — submarine groundwater discharge, drained "
        "organic soils, legacy nitrogen in transit, foreign inflow to shared waters — lands inside B's "
        f"leftover, and is named agriculture by subtraction. That is a weakness of the ~{agri:.0f}% "
        "separate from the circularity in §2.") + "\n")
    cl_path = os.path.join(DERIVED, "cropland.json")
    if os.path.exists(cl_path):
        w(whose_nitrogen(live.live_json(cl_path), total13))

    # --------------------------------------------------------- 3. wrong currency
    MM, R, S = K["molar_mass_g_per_mol"], K["redfield"], K["stoichiometry_mol_o2"]
    o2_per_n = R["o2_per_c106"] / R["n_per_c106"] * MM["O2"] / MM["N"]
    o2_per_p = R["o2_per_c106"] / R["p_per_c106"] * MM["O2"] / MM["P"]
    o2_nitrif = S["nitrification_per_n"] * MM["O2"] / MM["N"]
    o2_per_s = S["sulphide_oxidation_per_s"] * MM["O2"] / MM["S"]
    o2_per_ch4 = S["methane_oxidation_per_ch4"] * MM["O2"] / MM["CH4"]
    O2 = live.chem("O2")
    w("## 3. Nitrogen mass is the wrong currency\n")
    w(C("C-NI-CURRENCY", "Oxygen depletion is the damage. Nitrogen is one route to it.") + " "
      + C("C-NI-O2-TABLE", "Converting everything to oxygen demand — Redfield stoichiometry and the "
          "balanced reactions, which is chemistry rather than judgement "
          "(`data/manual/nitrogen_constants.json`):") + "\n")
    w("| Pathway | Oxygen demand |\n|---|---:|")
    w(f"| Remineralisation of algal biomass | **{o2_per_n:.2f} g {O2} per g N** |")
    w(f"| Remineralisation, via phosphorus | {o2_per_p:.1f} g {O2} per g P |")
    w(f"| **Nitrification of delivered ammonium** | **{o2_nitrif:.2f} g {O2} per g N** |")
    w(f"| **Sulphide oxidation** | **{o2_per_s:.2f} g {O2} per g S** |")
    w(f"| Methane oxidation | {o2_per_ch4:.2f} g {O2} per g {live.chem('CH4')} |")
    w(f"| Direct BOD | {K['bod5_to_ultimate']:.2f} g {O2} per g of five-day BOD |")
    w("")
    w(C("C-NI-ACCOUNTS-MASS", "The nitrogen apportionment counts nitrogen mass, which bears on the "
        "first line only. The mechanistic fjord models used to set the targets do describe the "
        "sediment's sulphate reduction — *\"" + quote("DHI-MODEL-DEL2-2015", "sker oxidationen overvejende "
        "ved sulfatreduktion med deraf følgende produktion af sulfid") + "\"* — but the share that "
        "circulates is a share of nitrogen. The consequences:") + "\n")
    w(C("C-NI-AMMONIUM", "**Ammonium carries its own demand.** An ammonium-rich discharge — which is "
        f"what a basin that has gone anaerobic produces — consumes {o2_nitrif:.2f} g {O2} per g N on "
        "arrival, with no algae, no light and no delay. That pathway is absent from a "
        "nitrogen→algae→decay model entirely.") + "\n")
    so4, o2sat = K["seawater_sulphate_mg_per_l"], K["dissolved_oxygen_mg_per_l"]
    s_mgl = so4 * MM["S"] / (MM["S"] + MM["O"] * 4)
    demand = s_mgl * o2_per_s
    w(C("C-NI-SULPHATE", "**Sulphate makes the debt effectively unbounded.** Full-strength seawater "
        f"holds ~{so4:.0f} mg/l sulphate = {s_mgl:.0f} mg/l as sulphur, against ~{o2sat:.0f} mg/l "
        f"dissolved oxygen. Fully reduced and later re-oxidised that is {demand:.0f} mg/l of demand — "
        f"**{demand / o2sat:.0f}× the oxygen in the water**. Reducing just "
        f"{o2sat / demand * 100:.2f}% of the sulphate pool stores a debt equal to all of it. Danish "
        "waters are brackish and hold proportionally less sulphate, which lowers the multiple and "
        "leaves the point. Once a basin goes anoxic the electron acceptor is effectively infinite, "
        "and every storm that mixes oxygen in spends it re-oxidising sulphide instead of restoring "
        "the water.") + "\n")
    w(C("C-NI-SILICON", "**And the ratio matters, not just the total.** Diatoms take up silicon and "
        f"nitrogen at a molar ratio of about {K['diatom_si_per_n']:g}. Fertiliser and sewage add N "
        "and P; neither adds silicon, which comes from rock weathering. Enrichment therefore raises "
        "N:Si, and when silicon runs out the community shifts from diatoms to flagellates and "
        "dinoflagellates. A composition change driven by a ratio, invisible to any nitrogen "
        "total.") + "\n")
    w(C("C-NI-POTENCY", "There is no potency term anywhere in the accounting. A kilogram delivered in "
        "February into a mixed column counts identically to a kilogram delivered in July into a "
        "stratified fjord.") + "\n")

    # ------------------------------------------------------------- 4. blind spots
    kt = koege_tables()
    w("## 4. What is not measured\n")
    w("| What | Window | Consequence |\n|---|---|---|")
    wins = mon["monitoring_windows"]
    for k, v in wins.items():
        flag = " **(circular)**" if v.get("seasonal_claim_circular") else ""
        w(f"| {k.replace('_', ' ')} | {ordinal_dates(v['period'])} | set by {v['window_set_by']}{flag} |")
    w("")
    fauna = ordinal_dates(wins["soft_bottom_fauna"]["period"]).replace(" - ", " to ")
    w(C("C-NI-NOVANA-FAUNA", "The most consequential row is the second. **The national programme "
        f"samples soft-bottom fauna {fauna}** — *\""
        + quote("NOVANA-2327", "Overvågningen af blødbundsfaunaen gennemføres i tidsrummet") + "\"* — "
        "after the winter, before the summer.") + " "
      + C("C-NI-DIEOFF", "So the late-summer die-off is observed only in its aftermath, months later, "
          "once recolonisation has begun, and the event that decides which organisms are present to "
          "receive the next year's nitrogen is the one the programme does not sample.") + "\n")
    w(C("C-NI-SEASONAL", "And any seasonal claim drawn from a seasonally-sampled record is circular "
        "unless the window was set by mechanism. Iltsvind's July–November window was; bathing "
        "water's June–September window was not.") + "\n")
    mfs = mon["hazardous_substances"]
    n_st = mfs["stations_combined_overflow"] + mfs["stations_separate_stormwater"]
    w(f"### Toxicants: {n_st} stations\n")
    points = (" " + C("C-NI-RBU-COUNT", f"The national register holds **{kt[3]:,}** rain-dependent "
                      "discharge points.")) if kt else ""
    w(C("C-NI-TYPETAL-BASIS", "The national typetal for hazardous substances in rain-dependent "
        f"discharges rest on **{mfs['stations_combined_overflow']} combined-sewer overflows and "
        f"{mfs['stations_separate_stormwater']} separate stormwater outlets** — *\""
        + quote("TYPETAL22", "fælleskloakerede spildevandsoverløb og fem separatkloakerede "
                "regnvandsudledninger") + "\"* — monitored 2000–2020 in catchments representing *\""
        + quote("TYPETAL22", "husholdninger og boligområder") + "\"*. They cover only discharges *\""
        + quote("TYPETAL22", "uden forudgående rensning i form af fx filtrering eller sedimentation i "
                "regnvandsbassiner") + "\"*, and the report calls them limited for *\""
        + quote("TYPETAL22", "industriområder og meget trafikerede veje") + "\"*.") + points + "\n")
    w(C("C-NI-TYPETAL-EXCLUDES", "A significant share of the adsorbing substances is caught in basin "
        "sediment, which the typetal do not cover. **The design excludes the worst cases, and says "
        "so.**") + "\n")
    w("| µg/l | Combined overflow | Separate stormwater | Max observed, combined overflow |\n|---|---:|---:|---:|")
    for m, v in mfs["typetal_ug_per_l"].items():
        if m.startswith("_"):
            continue
        w(f"| {m} | {v[0]} | {v[1]} | {v[2]} |")
    w("")
    sw, co = OF["separate_stormwater"], OF["combined_overflow"]
    sw_v, co_v = sw["totals"][VOL], co["totals"][VOL]
    w(C("C-NI-STORMWATER-METALS", "Note that chromium, nickel and arsenic are **higher in separated "
        "stormwater than in sewage overflow** — and the national outfall layers report "
        f"{sw_v['sum'] / 1e6:.0f} million m³/yr of the former, summed over the {sw_v['n']:,} of "
        f"{sw['n']:,} separate outfalls that give a volume, against {co_v['sum'] / 1e6:.1f} million "
        f"m³/yr of the latter over {co_v['n']:,} of {co['n']:,} combined-sewer overflows. Separating a "
        "sewer system solves the sewage overflow and delivers untreated runoff instead.") + "\n")

    # ---------------------------------------------------------------- 5. Køge Bugt
    if kt:
        st, plants, path, _ = kt
        w("## 5. A worked case: Køge Bugt\n")
        w(C("C-NI-KOEGE-DCE", "DCE's oxygen notes say for 2023 *\""
            + quote("NI-DCE-ILT-2023", "I Køge og Faxe Bugt blev der ikke registreret iltsvind")
            + "\"* and for 2025 *\""
            + quote("NI-DCE-ILT-2025", "I Køge Bugt og Faxe Bugt er der ikke registreret iltsvind i år")
            + "\"* — **no oxygen depletion registered**, in 2023 in the autumn after a mid-September "
            "extent the note calls *\"" + quote("NI-DCE-ILT-2023", "det hidtil næststørste registreret")
            + "\"*, the second largest registered.") + "\n")
        ilt = reading("NI-DCE-ILT-2025", "4", "iltkoncentrationen i vandet er mindre end 4 mg l-1")
        w(C("C-NI-ILTSVIND-DEF", f"DCE call it iltsvind when the oxygen concentration is below "
            f"**{ilt} mg/l**.") + " "
          + C("C-NI-KOEGE-MIX", "Køge Bugt mixes readily, so it may never meet that definition while "
              "still having anoxic sediment, sulphate reduction and a putrefying shoreline. 'Not "
              "registered' is probably accurate and says nothing about whether the bed is dead — and "
              "whether it means measured and absent, or not measured, the notes do not say.") + "\n")
        w("### Who can discharge sewage into the bay\n")
        w("| Municipality | Separate outfalls | Combined overflows | % separated | Basin m³ |\n|---|---:|---:|---:|---:|")
        shown = [k for k in KOEGE if (st[k]["sep"] + st[k]["comb"]) > 0]
        for k in shown:
            v = st[k]
            sep_pct = live.step("K-SUBSET-SHARE", v["sep"] / (v["sep"] + v["comb"]) * 100)
            bold = "**" if k in KOEGE_NORTH else ""
            w(f"| {bold}{k}{bold} | {v['sep']} | {v['comb']} | {sep_pct:.0f}% | {v['vol']:,.0f} |")
        w("")
        tc = sum(st[k]["comb"] for k in shown)
        tvol = sum(st[k]["vol"] for k in shown)
        nc = sum(st[k]["comb"] for k in KOEGE_NORTH if k in shown)
        nv = sum(st[k]["vol"] for k in KOEGE_NORTH if k in shown)
        none = [k for k in shown if k not in KOEGE_NORTH and st[k]["comb"] == 0]
        few = [k for k in shown if k not in KOEGE_NORTH and 0 < st[k]["comb"] and st[k]["vol"] == 0]
        w(C("C-NI-KOEGE-COMBINED", f"{', '.join(none[:-1])} and {none[-1]} have **no** combined-sewer "
            "overflow in the national register"
            + "".join(f"; {k} has {st[k]['comb']}" for k in few if k == "Greve") + ". So in a storm "
            "they cannot spill combined sewage through one — though pumping stations on a separate "
            "system can still have emergency overflows, which DANVA's own list of discharge types "
            "names: *\"" + quote("DANVA-2024", "Nødoverløb fra Pumpestationer") + "\"*.") + "\n")
        share = live.step("K-SUBSET-SHARE", nv / tvol * 100)
        w(C("C-NI-KOEGE-STORAGE", f"**{share:.0f}% of the bay's basin storage** ({nv:,.0f} of "
            f"{tvol:,.0f} m³) sits in the northern municipalities, along with {nc} of {tc} combined "
            "overflows. The bay opens southeast, so their discharge enters at the northern end.") + "\n")
        w(koege_transport(mon))
        if plants:
            w("### Treatment capacity discharging to the bay\n")
            w("| Plant | PE | Municipality |\n|---|---:|---|")
            for n, pe, k in plants:
                w(f"| {n} | {pe:,} | {k} |")
            w("")

    # ------------------------------------------------------------------- caveats
    ovr = next(p for p in paths if str(p["pathway"]).startswith("Rain-dependent overflow"))
    w("## What this does and does not establish\n")
    w(C("C-NI-NOT-URBAN", "**It does not establish that urban discharge is a large national "
        "source.** In the pathways register above, combined-sewer overflow is put at "
        f"{ovr['lo']:g}–{ovr['hi']:g} kt N/yr against {land_lo:g}–{land_hi:g} kt from Danish land by "
        "stream: a fraction even at its upper bound.") + "\n")
    w(C("C-NI-DIFFERENT-QUESTION", "**It does establish that the published percentage answers a "
        "different question than the one it is used for.** It answers: *of the nitrogen we observe "
        "arriving by stream from Danish land, how much do we attribute to farming after subtracting "
        "our models of everything else?* It is read as: *how much of Denmark's marine nitrogen "
        "problem is agriculture?*") + "\n")
    w(C("C-NI-THREE-DIFFERENCES", "Those differ by a closed set, a potency term, and a state "
        "variable. The accounts contain none of the three.") + "\n")
    w(C("C-NI-BOUNDS", "**Several ranges in section 1 are constructed here, not published figures, "
        "and the register does not mark which** — so every range there should be read as this "
        "project's unless a source is given. They are stated so they can be argued with.") + "\n")

    path = os.path.join(ROOT, "docs", "NITROGEN.md")
    text = "\n".join(o)
    try:
        write_doc(path, text)
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote docs/NITROGEN.md ({len(text):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
