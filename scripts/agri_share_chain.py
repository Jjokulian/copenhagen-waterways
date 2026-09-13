#!/usr/bin/env python3
"""How the published agricultural share of nitrogen was made - their chain, recorded.

The figure is Miljøstyrelsen's: Tabel 1 of its memo of 24 January 2023 to
Folketinget, row "Landbrug". This project did not compute it and holds none of the
stream records under it. What it can do is lay out how it was made, step by step
from the stream samples to the decimal, in the words of those who made it: each step
with its kind (PROVENANCE_SPEC.md), what it imposes, their method, their reason, the
limits they state, what else could have been chosen, whether it was tested, and what
would settle it. Every Danish quotation is checked against the pinned document when
this runs; one that is not in its document stops the run.

No code is published for their steps, so where this project's own numbers show the
producer's source lines, these steps show the method in the authors' words, with an
English translation (ours). The reruns at the end are this project's computations
from their published numbers, and show their code.

    python3 scripts/agri_share_chain.py     # writes docs/data/lineage/agri_share.json
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import claims                     # noqa: E402  the pinned documents
import lineage                    # noqa: E402

ROOT = lineage.ROOT
D, _, _ = claims.load()
_FLAT = {}
MISSING = []


def _flat(sid):
    """A pinned text on one line: soft hyphens dropped, and a copy with words broken
    across a line by a hyphen joined again."""
    if sid not in _FLAT:
        t = claims.pin_text(D, sid).replace("\u00ad\n", "").replace("\u00ad", "")
        t = " ".join(t.split())
        _FLAT[sid] = (t, re.sub(r"(\w)- (\w)", r"\1\2", t))
    return _FLAT[sid]


def said(sid, da, en, role="method", where=None):
    """A quotation, held only while it stands in the pinned document."""
    q = " ".join(da.split())
    flat, joined = _flat(sid)
    if not (q in flat or q in joined or re.sub(r"(\w)- (\w)", r"\1\2", q) in joined):
        MISSING.append(f"{sid}: {q[:110]}")
    s = D["sources"][sid]
    return {"role": role, "source": sid, "title": s["title"], "url": s["url"],
            "where": where, "da": q, "en": en}


def dk(v):
    """A number as printed in Danish: 56.156,8 -> 56156.8."""
    return float(v.replace(".", "").replace(",", "."))


def mst_table():
    """Tabel 1 of the memo, row by row as printed. In the pinned text the labels come
    first and the values after them, in the same order."""
    raw = claims.pin_text(D, "MST-2023-MOF121")
    block = raw.split("Tabel 1.", 1)[1].split("Samlet procent", 1)[0]
    lines = [x.strip() for x in block.split("\n") if x.strip()][1:]     # [0]: the caption
    heads = {"Kilde", "Diffuse kilder", "Punktkilder", "Procentvis fordeling %"}
    values = [x for x in lines if re.fullmatch(r"\d+,\d", x)]
    labels = [x for x in lines if x not in heads and x not in values]
    if len(labels) != len(values):
        raise SystemExit(f"Tabel 1: {len(labels)} labels against {len(values)} values")
    total = re.search(r"perioden 2016-18 var ([\d.]+) tons kvælstof", raw)
    return ([{"Kilde": a, "Procentvis fordeling %": b} for a, b in zip(labels, values)],
            dk(total.group(1) + ",0"))


DISTRICTS = ["Jylland og Fyn (I)", "Sjælland (II)", "Bornholm (III)", "Internationalt (IV)",
             "Danmark"]


def vp3_table():
    """Tabel 3.28 of the final water plans: each row's label, then one value per
    district and one for the country, in the order of the table's head."""
    raw = claims.pin_text(D, "VP3-2023")
    a = raw.index("TABEL 3.28")
    block = raw[a:raw.index("3.2.4.2", a)]
    for name in ("Jylland og", "Sjælland", "Bornholm", "Internationalt", "Danmark"):
        if name not in block:
            raise SystemExit(f"Tabel 3.28: the head {name!r} is not in the pinned text")
    num = r"\d{1,3}(?:\.\d{3})*,\d"

    def row(after):
        i = block.index(after) + len(after)
        return re.findall(num, block[i:])[:5]
    return {"status": row("statusbelastningen vist."), "landbrug": row("Landbrug (%)"),
            "baggrund": row("Baggrund (%)"), "spredt": row("Spredt bebyggelse (%)")}


# ---- this project's reruns: the only computation on this chain --------------------
def with_air(agri_pct, land_t, air_t):
    """The agricultural tonnes the share implies, over the land-based total plus the
    nitrogen deposited from the air."""
    return round(agri_pct * land_t / (land_t + air_t), 1)


def undercounted(agri_pct, low_pct):
    """The share if the whole land-based total were low_pct per cent too low and all
    of the missing nitrogen fell into the remainder, as a residual method puts it."""
    return round((agri_pct + low_pct) / (100 + low_pct) * 100, 1)


def main():
    rows, land_t = mst_table()
    agri = dk(next(r["Procentvis fordeling %"] for r in rows if r["Kilde"] == "Landbrug"))
    reg = json.load(open(os.path.join(ROOT, "data", "manual", "nitrogen_readings.json"),
                         encoding="utf-8"))["pinned"]["apportion_agriculture"]
    if reg["value"] != agri:
        raise SystemExit(f"the site's register holds {reg['value']}, Tabel 1 prints {agri}")
    vp3 = vp3_table()
    # four values each rounded to a tenth: their sum may differ from the printed total by
    # up to 0.2 t without anything being wrong
    if abs(dk(vp3["status"][4]) - sum(dk(v) for v in vp3["status"][:4])) > 0.2:
        raise SystemExit(f"Tabel 3.28: the districts' loads do not add up to the country's: {vp3}")
    flat_vp3 = _flat("VP3-2023")[0]
    air_all = dk(re.search(r"opgjort til gennemsnitligt ca\. ?([\d.]+) ton kvælstof pr\. år "
                           r"\(2009-2020\)", flat_vp3).group(1) + ",0")
    air_inner = dk(re.search(r"inden for Skagen\) opgjort til ca\. ([\d.]+) ton", flat_vp3)
                   .group(1) + ",0")
    flat_vj = _flat("VJ-2018-N-VANDLOEB")[0]
    low_min = -dk(re.search(r"gennemsnitlig procent ?afvigelse på (-\d,\d) ?±", flat_vj).group(1))
    low_max = -dk(re.search(r"og (-\d,\d) ± \d,\d % \(ved en månedlig strategi\)", flat_vj).group(1))

    L = lineage.Lineage("agri_share", number={
        "file": "data/manual/nitrogen_readings.json",
        "path": "pinned.apportion_agriculture.value",
        "value": agri, "unit": "%",
        "says": "Agriculture's share of the nitrogen carried by water from Danish land to "
                "Danish coastal waters in 2016-18, normalised to average runoff - as printed "
                "in Tabel 1 of Miljøstyrelsen's memo of 24 January 2023 to Folketinget. This "
                "project did not compute it and holds none of the stream records under it.",
        "note": "Each step below is theirs, shown in their words with an English translation. "
                "What this project adds is each step's kind, what it imposes, what else could "
                "have been chosen, whether it was tested, and what would settle it. No "
                "uncertainty is printed with the share in any document read. The memo took "
                "its table from the proposal for the third water plans; the final plans print "
                f"{dk(vp3['landbrug'][4])}% for the same years (rerun R2).",
        "producer": "scripts/agri_share_chain.py", "page": "docs/NITROGEN.md",
        # the same figure wherever else the site prints it, so that it opens this record
        # there too: LANDBRUG's copy, the press and DANVA printing it, and this site's
        # own past quoted in the archive (every quoted 69.6 there is this figure)
        "also": [["leaf", "data/derived/landbrug.json", "agri_pct"],
                 ["reading", "DANVA-2024", agri], ["reading", "POL-DR-20260903", agri],
                 ["reading", "POL-GP-20260825", agri], ["quote", agri]]})
    lb = json.load(open(os.path.join(ROOT, "data", "derived", "landbrug.json"), encoding="utf-8"))
    if lb["agri_pct"] != agri:
        raise SystemExit(f"LANDBRUG's copy holds {lb['agri_pct']}, Tabel 1 prints {agri}")

    MST = os.path.join(claims.PINS, "MST-2023-MOF121.txt")
    L.record("mst-tabel-1", MST, rows, ["Kilde", "Procentvis fordeling %"],
             published_by="Miljøstyrelsen, notat of 24 January 2023 (J.nr. 2023-4725), "
                          "Tabel 1; sent to Folketinget as MOF Alm.del 2022-23 bilag 121",
             fetched_from=D["sources"]["MST-2023-MOF121"]["url"],
             pick=lambda r: list(range(len(r))),
             marked=["'normaliserede': recomputed as if runoff had been average - not what "
                     "arrived in any year (S13)",
                     "'landbaserede': from land, carried by water; the air and other "
                     "countries' waters are not in the total (S12, S17)",
                     "'Landbrug' is a remainder, not a measurement (S14-S16)"])
    vrows = [{"distrikt": DISTRICTS[i], "Statusbelastning (ton N)": vp3["status"][i],
              "Landbrug (%)": vp3["landbrug"][i], "Baggrund (%)": vp3["baggrund"][i],
              "Spredt bebyggelse (%)": vp3["spredt"][i]} for i in range(5)]
    L.record("vp3-tabel-3-28", os.path.join(claims.PINS, "VP3-2023.txt"), vrows,
             list(vrows[0]), published_by="Miljøministeriet, Vandområdeplanerne 2021-2027 "
             "(2023), Tabel 3.28", fetched_from=D["sources"]["VP3-2023"]["url"],
             pick=lambda r: list(range(len(r))),
             marked=["the same 2016-18 period as the memo, in the final plans rather than the "
                     "proposal"])

    NR = lineage.NO_REASON
    B1, B2, B3, B4 = ("in the stream", "the land without stations", "adding up",
                      "dividing it among causes")

    L.step("S1", "selection", "Water is sampled about eighteen times a year at fixed stations",
           [], branch=B1,
           imposes="What a stream carries between two sampling days is never seen: a flood "
                   "that passes between them enters only through the straight line of S3. "
                   "The stations are fixed points chosen by the programme.",
           inputs=["stream water at each station"], outputs={},
           counted_as_one="One station = one fixed point on one stream, its samples one "
                          "series for as long as it runs.",
           said=[said("SR681", "Ved hovedparten af stoftransportstationerne måles med en "
                      "frekvens på 18 prøver pr. år.",
                      "At most of the load stations, samples are taken at a frequency of 18 a "
                      "year."),
                 said("SR681", "Der er ligeledes gennemført en korrektion af total-kvælstof-"
                      "data målt fra 2009 til 2015, da data for denne periode er analyseret "
                      "med den samme forkerte metode",
                      "A correction has likewise been made to the total-nitrogen data measured "
                      "from 2009 to 2015, as the data for that period were analysed with the "
                      "same wrong method")],
           why=NR, alternative="continuous sensors at some stations, as the 2018 field study "
                               "used; sampling weighted towards high flow",
           tested="in three streams, against daily measurement - see S3",
           settle="Publish each station's sampling dates beside its discharge record, so a "
                  "reader can see which floods were sampled and which were not.")

    L.step("S2", "functional form", "Discharge is computed from the logged water level", [],
           branch=B1,
           imposes="The daily discharge comes from a relation between water level and flow, "
                   "fitted to occasional gaugings - a model of the stream bed, refitted as the "
                   "bed changes.",
           inputs=["water level at each gauge", "occasional gaugings"], outputs={},
           said=[said("SR681", "indgår måledata fra i alt 244 vandføringsmålestationer",
                      "measurements from a total of 244 discharge stations are included"),
                 said("SR681", "Den relative usikkerhed på opgørelsen af "
                      "ferskvandsafstrømningen er størst i små oplande, hvor der ofte kun er "
                      "en meget lille andel eller slet intet af arealet, der er dækket af "
                      "målestationer.",
                      "The relative uncertainty of the freshwater runoff estimate is largest "
                      "in small catchments, where often only a very small share of the area, "
                      "or none of it, is covered by stations.", role="limit")],
           why=NR, alternative="direct velocity measurement at the station",
           settle="Publish the rating curves with their gaugings and the spread of the "
                  "gaugings around them.")

    L.step("S3", "filling in", "Between samples, the concentration is drawn as a straight line",
           [], branch=B1,
           imposes="Each day's nitrogen is that day's discharge times a concentration drawn in a "
                   "straight line between two samples up to six weeks apart. A flood's "
                   "concentration is whatever the line says.",
           inputs=["the samples of S1", "the daily discharge of S2"], outputs={},
           said=[said("DCE-TA-DB01", "Ved denne metode interpoleres der mellem årets "
                      "koncentrationsmålinger af et givet stof for at generere "
                      "døgnkoncentrationer.",
                      "In this method, the year's concentration measurements of a substance "
                      "are interpolated to generate daily concentrations."),
                 said("DCE-TA-DB01", "Der må højst være 6 uger mellem to "
                      "koncentrationsmålinger",
                      "There may be at most 6 weeks between two concentration measurements"),
                 said("VJ-2018-N-VANDLOEB", "I de 3 undersøgte vandløb blev den "
                      "gennemsnitlige kvælstoftransport beregnet ud fra punktprøver dog altid "
                      "underestimeret",
                      "In the 3 streams studied, however, the average nitrogen transport "
                      "computed from grab samples was always underestimated", role="limit")],
           why=NR, alternative="flow-weighted or regression estimators of load; the bias "
                               "correction the 2018 study's authors raised",
           tested=f"Yes: the 2018 study compared it with daily measurement in three streams and "
                  f"found it always low - on average by {low_min}% in Jegstrup Bæk and by "
                  f"{low_max}% in Odder Å with monthly sampling (rerun R3).",
           settle="Apply the correction the study raised to the national loads, or publish why "
                  "it is not needed.")

    L.step("S4", "grouping", "The land upstream of the stations is drawn on a map and called "
           "measured", [], branch=B1,
           imposes="A catchment map assigns land to stations. The 'measured share of the "
                   "country' is an area on that map divided by the land area: nothing was "
                   "sampled on that land, and it is not a share of the load or of the "
                   "discharge. It moves when stations open and close.",
           inputs=["the ID15 catchment map", "the stations of S1"], outputs={},
           counted_as_one="All land drawn upstream of a station = 'measured', however far from "
                          "the station.",
           said=[said("SR353", "Det nye kortgrundlag er ID15v1.5, som består af >3100 "
                      "deloplande med en middelstørrelse på ca. 15 km2.",
                      "The new map is ID15v1.5, which consists of more than 3100 "
                      "sub-catchments with a mean size of about 15 km²."),
                 said("SR4", "Det areal, som derved er dækket af målestationer, er dermed "
                      "reduceret fra 21 478 km2 til 21 131 km2, svarende til 49 % af Danmarks "
                      "areal.",
                      "The area covered by stations is thereby reduced from 21,478 km² to "
                      "21,131 km², equal to 49% of Denmark's area.", where="Vandløb 2010"),
                 said("SR681", "for 2017 og tidligere år indgik 169 målestationer, som dækkede "
                      "et samlet opland på 24.380 km2, svarende til 57 % af landets samlede "
                      "areal.",
                      "for 2017 and earlier years 169 stations were included, covering a total "
                      "catchment of 24,380 km², equal to 57% of the country's total area."),
                 said("SR681", "er der anvendt data fra i alt 235 målestationer dækkende et "
                      "oplandsareal på 26.468 km2, hvilket svarer til ca. 62 % af landets "
                      "samlede areal.",
                      "data from a total of 235 stations are used, covering a catchment area "
                      "of 26,468 km², which equals about 62% of the country's total area.",
                      where="for 1990-2024")],
           why=NR, alternative="report the load per station catchment as measured, and the "
                               "modelled land separately - never as a share of a country",
           settle="Show the stations and the land drawn to each on a map, with the modelled "
                  "land visibly blank, instead of one national share.")

    L.step("S5", "filling in", "Months without samples are filled in", [], branch=B2,
           imposes="A station that closed, or opened late, still contributes a full series; its "
                   "missing months are model output, not measurements.",
           inputs=["stations without a continuous record"], outputs={},
           said=[said("SR681", "For 144 af de 235 målestationer er der ikke kontinuerte "
                      "måledata for hele perioden.",
                      "For 144 of the 235 stations there are no continuous measurements for the "
                      "whole period."),
                 said("SR681", "Den valgte metode hertil er beskrevet i Windolf m.fl. (2013).",
                      "The method chosen for this is described in Windolf et al. (2013).")],
           why=NR, alternative="use only measured months and report how much of each year "
                               "rests on filled ones",
           settle="Publish, per year, the share of the national total that rests on filled-in "
                  "months.")

    L.step("S6", "filling in", "Runoff from land without stations comes from the national "
           "water model", [], branch=B2,
           imposes="Where there is no gauge, the water is the DK-model's water. Its error in "
                   "land with gauges is assumed to hold in land without them.",
           inputs=["GEUS's DK-model"], outputs={},
           counted_as_one="Land without a station = land like the gauged land of its region.",
           said=[said("SR353", "afstrømninger fra det umålte opland (afstrømning fra områder "
                      "uden målestationer) nu opgøres på basis af modellerede afstrømninger "
                      "fra GEUSs DK-model (den nationale vandresourcemodel)",
                      "runoff from the unmeasured land (runoff from areas without stations) is "
                      "now computed from modelled runoff from GEUS's DK-model (the national "
                      "water resources model)"),
                 said("BA-SR527", "Da der ikke er målt afstrømning i umålt opland, kan disse "
                      "steder dog ikke identificeres med metoden",
                      "As no runoff is measured in the unmeasured land, however, these places "
                      "[where the model's error differs from that in gauged land] cannot be "
                      "identified with the method", role="limit")],
           why=NR, alternative="temporary gauging in a sample of unmeasured catchments",
           tested="Not possible with the method, by their own statement.",
           settle="Gauge a sample of unmeasured catchments for a few years and publish the "
                  "model's error there.")

    L.step("S7", "functional form", "Nitrogen in land without stations: a regression fitted "
           "to farm catchments", [], branch=B2,
           imposes="The monthly concentration in land without stations is what a regression "
                   "on soil, farming share, drainage, rain, temperature and the national field "
                   "surplus predicts.",
           inputs=["small farm catchments with stations", "maps of soil, land use and "
                   "drainage", "the national field surplus (S8)"], outputs={},
           said=[said("MSFD28", "Modellen har en samlet forklaringsgrad på 43 % for perioden "
                      "1990-2007.",
                      "The model has an overall explanatory power of 43% for 1990-2007."),
                 said("MSFD28", "simulerer måledata fra en række målte oplande "
                      "tilfredsstillende",
                      "simulates measured data from a number of measured catchments "
                      "satisfactorily", role="reason"),
                 said("SR681", "Derfor anvendes modellen til en vis grad uden for dens "
                      "modeldomæne.",
                      "The model is therefore used, to some extent, outside its model domain.",
                      role="limit")],
           why="It reproduces measured catchments it was not calibrated on, in their judgement.",
           author="DCE (MSFD notat 2.8, 2012)",
           alternative="report the unmeasured land's load as a range from the measured "
                       "catchments' spread",
           tested="against gauged catchments, in their words 'satisfactorily'; the fit explains "
                  "43% of what it was fitted to",
           settle="Publish the model's error on held-out catchments as a range on the "
                  "unmeasured land's load.")

    L.step("S8", "identity", "One national field surplus a year stands for every field", [],
           branch=B2,
           imposes="The field surplus - itself computed as nitrogen applied minus harvested, "
                   "from norms, not measured - enters as one number for the whole country each "
                   "year. It carries the trend over time, not the differences between places, "
                   "and it ties the modelled load to the farm accounts the share is then used "
                   "to judge.",
           inputs=["the national field balance"], outputs={},
           counted_as_one="Every field in Denmark = the national field surplus of that year.",
           said=[said("SR681", "En vigtig modelvariabel i DK-QNPv2-modellen til beregning af "
                      "tilførsel af totalt diffust kvælstof fra umålt opland er det beregnede "
                      "årlige nationale kvælstofoverskud på mark-niveau (markbalancen).",
                      "An important variable in the DK-QNPv2 model for computing the diffuse "
                      "nitrogen from unmeasured land is the calculated annual national "
                      "nitrogen surplus at field level (the field balance).")],
           why=NR, alternative="regional or farm-level balances",
           settle="Show how the modelled load changes with the surplus left out - how much of "
                  "the modelled farm load is the surplus itself.")

    L.step("S9", "correction", "The model is scaled to match the stations of its region", [],
           branch=B2,
           imposes="Month by month, the modelled concentrations are multiplied by the ratio of "
                   "measured to modelled at full-series stations in the same region, so the "
                   "unmeasured land follows the measured land's trend by construction.",
           inputs=["the full-series stations", "the model of S7"], outputs={},
           said=[said("SR353", "Forskelle i koncentration mellem målte og modellerede "
                      "værdier ses som en generel model-bias, som det er rimeligt at "
                      "korrigere.",
                      "Differences in concentration between measured and modelled values are "
                      "seen as a general model bias, which it is reasonable to correct.",
                      role="reason")],
           why="The differences between measured and modelled are taken as a general bias.",
           author="DCE (Vandløb 2018)",
           alternative="leave the model uncorrected and show both",
           tested="not tested: it assumes the bias in measured land is the bias in unmeasured "
                  "land (see S6)",
           settle="The same held-out gauging as S6 would test it.")

    L.step("S10", "functional form", "Nitrogen removed in lakes and streams is calculated and "
           "subtracted", [], branch=B2,
           imposes="Removal rates per hectare of stream, lake and wetland, averaged from the "
                   "literature, are applied throughout the unmeasured land.",
           inputs=["the gross load of S7-S9", "lake, stream and wetland areas"], outputs={},
           said=[said("MSFD28", "Nettoudledninger fra de umålte oplande fastlægges ved at "
                      "fratrække en beregnet retention i de enkelte umålte oplande.",
                      "The net discharges from the unmeasured catchments are found by "
                      "subtracting a calculated retention in each unmeasured catchment."),
                 said("MSFD28", "der må forventes at være en betydelig usikkerhed på de "
                      "beregnede kvælstofretentioner i vandløb",
                      "a considerable uncertainty must be expected in the calculated nitrogen "
                      "retentions in streams", role="limit")],
           why=NR, alternative="report the gross load and the retention separately",
           tested="No numeric uncertainty was found for this retention. The range of 6-27 "
                  "percentage points often quoted belongs to the National Nitrogen Model's "
                  "retention from root zone to coast: a different model and quantity.",
           settle="Publish the retention subtracted, in tonnes a year, with a range.")

    L.step("S11", "classification", "What counts as a point source, and as a direct discharge",
           [], branch=B3,
           imposes="A register decides which outlets are point sources - plants, industry, fish "
                   "farms, overflows - and a distance rule decides which reach the sea "
                   "directly. Missing early years are filled with the earliest known value.",
           inputs=["the point-source registers"], outputs={},
           said=[said("SR353", "koordinaterne for udledningspunktet enten ligger ude i havet "
                      "eller på land højst 100 meter fra kystlinjen",
                      "the coordinates of the discharge point lie either out at sea or on land "
                      "at most 100 metres from the coastline",
                      where="the rule for a direct discharge"),
                 said("SR353", "er det antaget, at udledningerne har været af samme størrelse "
                      "som den tidligst kendte udledning",
                      "it is assumed that the discharges were the same size as the earliest "
                      "known discharge")],
           why=NR, alternative="report the filled years separately",
           settle="Publish how much of each year's point-source total is filled rather than "
                  "reported.")

    L.step("S12", "convention", "The total: measured, plus modelled, plus direct discharges",
           [], branch=B3,
           imposes="The total is the nitrogen carried from Danish land by water. What comes "
                   "through the air, from other countries' rivers and seas, or up from the sea "
                   "floor is outside it by definition.",
           inputs=["S3-S4 (measured land)", "S5-S10 (land without stations)", "S11"],
           outputs={},
           said=[said("MSFD28", "Målte stoftransport (målt opland) + beregnet nettotransport "
                      "fra umålt opland + direkte spildevandsudledninger til pågældende "
                      "kystafsnit.",
                      "Measured transport (measured land) + calculated net transport from "
                      "unmeasured land + direct wastewater discharges to the coastal section "
                      "concerned."),
                 said("MSFD28", "på henholdsvis 20-25 % og ca. 20 %",
                      "of 20-25% and about 20% respectively [the uncertainty of the total "
                      "annual input of nitrogen and of phosphorus via streams and direct "
                      "discharges]", role="limit")],
           why=NR, alternative="a total that includes deposition and inflow from other seas",
           settle="Print the total with the 20-25% uncertainty their own 2012 note gives, "
                  "wherever the share is printed.")

    L.step("S13", "correction", "Each year is recomputed as if runoff had been average", [],
           branch=B3,
           imposes="The published tonnes are not what arrived in any year but what a model "
                   "says would have arrived at average runoff; three such years, 2016-18, are "
                   "averaged.",
           inputs=["the yearly totals", "the yearly runoff"], outputs={},
           said=[said("MST-2023-MOF121", "Med henblik på i videst muligt omfang at korrigere "
                      "for variation i nedbør og afstrømning beregnes, hvad der ville "
                      "forventes, hvis vandafstrømningen havde været den samme fra år til år",
                      "To correct as far as possible for variation in rain and runoff, what "
                      "would be expected if runoff had been the same from year to year is "
                      "computed", role="reason"),
                 said("SR353", "fitte en lineær model til logaritme transformerede "
                      "månedstransporter og månedsvandafstrømninger",
                      "fit a linear model to log-transformed monthly transports and monthly "
                      "runoffs"),
                 said("SR353", "den anvendte normaliseringsmetode ikke tager højde for alle "
                      "effekter af vejret på dyrkningen",
                      "the normalisation method used does not account for all effects of the "
                      "weather on farming", role="limit")],
           why="So that a wet year and a dry year can be compared.",
           author="Miljøstyrelsen (notat 2023)",
           alternative="report the actual loads beside the normalised ones",
           settle="Print the actual 2016-18 loads next to the normalised ones.")

    L.step("S14", "attribution", "Diffuse = the total minus the point sources", [], branch=B4,
           imposes="Whatever is in the water and not in the point-source register is called "
                   "diffuse: errors in the total, gaps in the register and every source with no "
                   "register all land in this remainder.",
           inputs=["the total of S12", "the point sources of S11"], outputs={},
           counted_as_one="Everything not registered as a point source = diffuse.",
           said=[said("SR681", "beregnes et diffust bidrag fra det åbne land som differencen "
                      "mellem punktkildebidraget og den samlede transport.",
                      "a diffuse contribution from the open land is calculated as the "
                      "difference between the point-source contribution and the total "
                      "transport."),
                 said("SR681", "Spildevand fra spredt bebyggelse henregnes i denne opgørelse "
                      "til det diffuse bidrag.",
                      "Wastewater from scattered housing is counted as diffuse in this "
                      "account.")],
           why=NR, alternative="estimate each diffuse source directly and report what is left "
                               "over as unexplained",
           settle="Carry the total's uncertainty and the register's gaps through to the "
                  "diffuse figure.")

    L.step("S15", "filling in", "The natural background is estimated from a few near-natural "
           "streams", [], branch=B4,
           imposes="Nobody measures what farmed land would yield without farming. Concentrations "
                   "from a few streams with little farming are spread over the country on a "
                   "grid and multiplied by runoff; this is the stand-in.",
           inputs=["near-natural streams", "a 5x5 km grid by landscape type", "runoff"],
           outputs={},
           said=[said("MSFD28", "som bestemmes i mindre oplande med lav antropogen påvirkning",
                      "which is determined in smaller catchments with little human influence"),
                 said("DCE-BAGGRUND-2014", "Ved beregning af en baggrundsbelastning fra et "
                      "givet opland skal den arealvægtede baggrundskoncentration i oplandet "
                      "multipliceres med en vandafstrømning",
                      "To compute a background load from a given catchment, the area-weighted "
                      "background concentration in the catchment is multiplied by a runoff"),
                 said("MSFD28", "baggrundsbidraget er dog sandsynligvis påvirket af en forhøjet "
                      "atmosfærisk deposition",
                      "the background contribution is, however, probably affected by elevated "
                      "deposition from the air", role="limit")],
           why=NR, alternative="a range of backgrounds, from the lowest to the highest "
                               "near-natural streams, carried to the share",
           settle="Publish the background as a range and carry it to the share: every tonne "
                  "moved out of the background moves the same tonne into agriculture.")

    L.step("S16", "attribution", "Agriculture = the diffuse remainder minus the background",
           [], branch=B4,
           imposes="Only two terms: once the background is taken out, all that remains is "
                   "called agriculture - including the errors of every earlier step and every "
                   "unregistered source. In the 2016-18 tables scattered housing is a separate "
                   "row, so the 2012 definition quoted here is not exactly the one used.",
           inputs=["the diffuse remainder of S14", "the background of S15"], outputs={},
           counted_as_one="All diffuse nitrogen not called background = agriculture.",
           said=[said("MSFD28", "Diffuse tilførsler (inkl. spredt bebyggelse) minus "
                      "baggrundsbidraget (diffus antropogen)",
                      "Diffuse inputs (incl. scattered housing) minus the background "
                      "contribution (diffuse anthropogenic)", where="2012"),
                 said("VP3-2023", "Den diffuse belastning fra landarealer udgøres af et "
                      "baggrundsbidrag og et landbrugsbidrag.",
                      "The diffuse load from land consists of a background contribution and an "
                      "agricultural contribution.", where="2023"),
                 said("VP3-2023", "Den altovervejende kilde til den diffuse kvælstoftransport i "
                      "vandløbene er tabet af kvælstof fra de dyrkede arealer.",
                      "By far the main source of the diffuse nitrogen transport in streams is "
                      "the loss of nitrogen from cultivated land.", role="reason"),
                 said("MSFD28", "retentionen alene er lagt på det diffuse antropogene bidrag",
                      "the retention is laid on the diffuse anthropogenic contribution alone",
                      role="limit", where="2012 tables")],
           why="Cultivated land is taken to be by far the main diffuse source.",
           author="Miljøministeriet (Vandområdeplanerne 2021-2027)",
           alternative="name the remainder 'diffuse, not background', and give agriculture a "
                       "range from direct estimates such as leaching measured under fields",
           tested="not tested directly: a remainder can only be checked against something "
                  "measured independently",
           settle="Test the agricultural load against leaching measured under fields rather "
                  "than by subtraction, and print the share with a range.")

    L.step("S17", "convention", "Divided by the land-based total, and carried to later years",
           [], branch=B4,
           imposes=f"The denominator is the land-based, normalised total of 2016-18, "
                   f"{land_t:,.0f} tonnes. Deposition from the air - which the water plans "
                   f"put at about {air_all:,.0f} tonnes a year on Danish coastal and "
                   f"territorial waters - is not in it. The share is printed to one decimal "
                   f"with no uncertainty, and assumed to hold for 2021.",
           inputs=["the agricultural remainder of S16", "the total of S12-S13"],
           outputs={"Landbrug": f"{agri}%", "total": f"{land_t:,.0f} t N"},
           said=[said("MST-2023-MOF121", "Tabel 1. Den procentvise kildefordeling af den "
                      "landbaserede normaliserede kvælstoftilførsel fra Danmark til "
                      "kystområderne.",
                      "Table 1. The percentage distribution by source of the land-based, "
                      "normalised nitrogen input from Denmark to the coastal areas."),
                 said("MST-2023-MOF121", "Fordelingen af den normaliserede udledning af "
                      "kvælstof med udgangspunkt i forslag til Vandområdeplan 3 er anført i "
                      "tabel 1 nedenfor.",
                      "The distribution of the normalised nitrogen discharge, based on the "
                      "proposal for Water Plan 3, is given in table 1 below."),
                 said("MST-2023-MOF121", "antages det i dette notat, at tallene for den mere "
                      "differentierede fordeling af kvælstofbelastningen på enkelte kilder "
                      "fra 2016-18 er retningsangivende for belastningen i 2021.",
                      "this memo assumes that the figures for the more detailed distribution of "
                      "the nitrogen load among sources in 2016-18 are indicative of the load "
                      "in 2021.", role="reason")],
           why="The total and the split between diffuse and point sources in 2021 did not "
               "differ much from the five years before, in their judgement.",
           author="Miljøstyrelsen (notat 2023)",
           alternative="a denominator including deposition and inflow from other seas "
                       "(reruns R1a, R1b)",
           settle="Print it as a share of the nitrogen carried by water from Danish land, with "
                  "its range, wherever it is printed - never as a share of 'the nitrogen'.")

    L.end("the published record", "record", "Tabel 1, row 'Landbrug', as printed in the memo",
          record="mst-tabel-1", author="Miljøstyrelsen", steps=["S17"])
    L.end("the published record", "record", "Tabel 3.28 of the final water plans, the same "
          "period by district", record="vp3-tabel-3-28", author="Miljøministeriet",
          steps=["S17"])
    L.end("in the stream", "record", "The stream samples and gauge readings at the stations, "
          "in the national database (ODA). Not held by this project.",
          author="DCE / Miljøstyrelsen", steps=["S1", "S2", "S3"])
    L.end("in the stream", "construction", "The ID15 catchment map that assigns land to "
          "stations", author="Aarhus University (DCE)", steps=["S4"])
    L.end("adding up", "construction", "The point-source register and the 100-metre rule for "
          "a direct discharge", author="the monitoring programme's data centres",
          steps=["S11"])
    L.end("adding up", "construction", "A total that counts only nitrogen carried by water "
          "from Danish land", author="the accounts' definition", steps=["S12", "S17"])
    L.end("dividing it among causes", "construction", "The two-term split of diffuse nitrogen "
          "into background and agriculture", author="the accounts' definition",
          steps=["S14", "S16"])
    for what, st in (("The DK-model's runoff where there is no gauge", ["S6"]),
                     ("The concentration model, fed by the national field surplus and scaled "
                      "to the measured stations", ["S7", "S8", "S9"]),
                     ("The retention subtracted in lakes, streams and wetlands", ["S10"]),
                     ("The months filled in at stations without a full record", ["S5"]),
                     ("The flow normalisation", ["S13"]),
                     ("The natural background grid", ["S15"])):
        L.end("model output", "model output", what, author="DCE / GEUS", steps=st)
    L.note("model_output", "Over the land without stations the load is model output at every "
           "step: runoff (S6), concentration (S7-S9) and retention (S10). The background (S15) "
           "is model output everywhere, and every published tonne is normalised (S13).")

    ag4 = [dk(v) for v in vp3["landbrug"][:4]]
    st4 = [dk(v) for v in vp3["status"][:4]]
    mix = round(sum(a * s for a, s in zip(ag4, st4)) / sum(st4), 1)
    bg4 = [dk(v) for v in vp3["baggrund"][:4]]
    bmix = round(sum(b * s for b, s in zip(bg4, st4)) / sum(st4), 1)
    L.spread(what=f"The same share in the four river-basin districts, from the final water "
                  f"plans' Tabel 3.28 (2016-18). They range from {min(ag4)}% to {max(ag4)}%; "
                  f"weighted by each district's load they give {mix}%, but the table prints "
                  f"{dk(vp3['landbrug'][4])}% for the country (the background column likewise "
                  f"mixes to {bmix}% against {dk(vp3['baggrund'][4])}% printed). The table "
                  f"does not say how its national column was computed.",
             table={"columns": ["district", "load, t N", "agriculture %", "background %",
                                "scattered housing %"],
                    "rows": [[r["distrikt"], r["Statusbelastning (ton N)"], r["Landbrug (%)"],
                              r["Baggrund (%)"], r["Spredt bebyggelse (%)"]] for r in vrows]},
             note="District IV is the Danish part of the river basin shared with Germany. "
                  "Below the districts the plans work per coastal catchment; those shares are "
                  "not in the documents read.")

    L.rerun("R1a", f"deposition from the air on Danish coastal and territorial waters "
            f"({air_all:,.0f} t a year, 2009-2020) added to the denominator",
            {"step": "S17", "air_t": air_all}, with_air(agri, land_t, air_all), None,
            step="S17", headline=True,
            note="Different waters: the land total goes to coastal waters, this deposition to "
                 "coastal and territorial waters. It shows how much the choice of denominator "
                 "decides, not a corrected share.",
            code=lineage.lines(with_air, "def with_air", "return"))
    L.rerun("R1b", f"deposition on the inner Danish waters only ({air_inner:,.0f} t a year) "
            f"added to the denominator", {"step": "S17", "air_t": air_inner},
            with_air(agri, land_t, air_inner), None, step="S17",
            note="The inner waters inside Skagen, as the water plans give them.",
            code=lineage.lines(with_air, "def with_air", "return"))
    L.rerun("R2", "the final water plans' table instead of the proposal's",
            {"step": "S17", "source": "VP3-2023 Tabel 3.28"}, dk(vp3["landbrug"][4]), None,
            step="S17", note="Same period, same accounts; neither document explains the "
                             "difference.")
    for rid, low, where in (("R3a", low_min, "Jegstrup Bæk"), ("R3b", low_max, "Odder Å")):
        L.rerun(rid, f"the whole total {low}% too low, as grab sampling ran low in {where} "
                     f"with monthly sampling, all of it falling into the remainder",
                {"step": "S3", "low_pct": low}, undercounted(agri, low), None, step="S3",
                note="This choice barely moves the share: it does not decide it.",
                code=lineage.lines(undercounted, "def undercounted", "return"))
    L.aside("the share's other printings on this site",
            "the same figure is printed on several pages and read from news articles and "
            "DANVA; this record is attached to NITROGEN's, read from the site's register")

    if MISSING:
        print(f"{len(MISSING)} quotation(s) not found in their pinned documents - nothing "
              "written:")
        for m in MISSING:
            print("  " + m)
        return 1
    p = L.write()
    print(f"wrote {os.path.relpath(p, ROOT)}: {len(L.doc['steps'])} steps, "
          f"{len(L.doc['robustness'])} reruns, {sum(len(s['said']) for s in L.doc['steps'])} "
          "quotations checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
