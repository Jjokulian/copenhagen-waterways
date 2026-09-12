#!/usr/bin/env python3
"""docs/hypodrafts/B1.md - what the data held here, and the public records named, can
and cannot show about B1 (combined sewer overflow).

Every number is read from data (live_json), from a pinned document ({read:}, or
draftkit.reading where it takes part in arithmetic), or is a stated design value with
its reason; every assertion is a checked claim (LIVE_NUMBERS.md section 11), registered
in data/manual/claims.d/w3-ba.json with what it rests on. The counts of the EEA
bathing-water tables are readings of pinned DISCODATA queries. What the draft once said
and could not justify is in docs/ARCHIVE.md, not here.

    python3 scripts/pages/hypodraft_b1.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import draftkit  # noqa: E402
from draftkit import RD  # noqa: E402
import claims  # noqa: E402
import live  # noqa: E402
from common import DERIVED, RAW  # noqa: E402

REL = "docs/hypodrafts/B1.md"
C, R = live.claim, live.ref
DP = "DTA-DP02-2024"
TAX = "https://github.com/Jjokulian/statistical-methods#7b-rate-a-data-stream-by-the-errors-it-can-contain"
ODD_CSO = {"UR", "OVI", "OSI", "OKI"}
ODD_RBU = ODD_CSO | {"ikke oplyst"}


def J(name):
    return live.live_json(os.path.join(DERIVED, name))


def refuse(msg):
    raise live.Unjustified("B1: " + msg)


def text():
    d = claims.load()[0]

    def P(name):
        """A design value the test chooses, declared with its reason."""
        p = d["params"][name]
        return live.stated_value(name, p["value"], p["reason"])

    def rd(sid, shown, phrase, value):
        return draftkit.reading(d, sid, shown, phrase, value)

    def pinj(sid):
        return json.loads(claims.pin_text(d, sid))["results"]

    # --- the EEA bathing-water tables, as pinned -------------------------------
    SAM = '"samples":172440,"sites":1437,"first_season":2008,"last_season":2024'
    n_s = rd("BA-WISE-DK-SAMPLES", "172,440", SAM, 172440)
    n_ids = rd("BA-WISE-DK-SAMPLES", "1,437", SAM, 1437)
    first = rd("BA-WISE-DK-SAMPLES", "2008", SAM, 2008)
    last = rd("BA-WISE-DK-SAMPLES", "2024", SAM, 2024)
    EC = '"escherichiaColiStatus":"limitOfDetectionValue","n":26301,"with_value":26301'
    lod = rd("BA-WISE-DK-ECOLI", "26,301", EC, 26301)
    DAT = '"samples":130773,"dates":1425,"seasons":14'
    s_dat = rd("BA-WISE-DK-DATES", "130,773", DAT, 130773)
    dates = rd("BA-WISE-DK-DATES", "1,425", DAT, 1425)
    seas_dat = rd("BA-WISE-DK-DATES", "14", DAT, 14)
    NOTD = '"sites_never_delisted":1049'
    never = rd("BA-WISE-DK-NOTDELISTED", "1,049", NOTD, 1049)

    s0 = pinj("BA-WISE-DK-SAMPLES")[0]
    if s0["ecoli_null"] or s0["entero_null"]:
        refuse("the pinned table now has empty counts; the page says it has none")
    schema = pinj("BA-WISE-DK-SCHEMA")[0]
    if (len(str(schema.get("sampleDate", ""))) != 10
            or any(("time" in k.lower() or "hour" in k.lower()) for k in schema)):
        refuse("the pinned record no longer shows a bare date and no time column")
    table_ids = {r["bathingWaterIdentifier"] for r in pinj("BA-WISE-DK-SITES")}
    if len(table_ids) != int(n_ids):
        refuse("the pinned list of identifiers does not match the pinned count")
    layer = json.load(open(os.path.join(RAW, "national", "badevand.geojson"),
                           encoding="utf-8"))["features"]
    layer_ids = {f["properties"]["id"] for f in layer}
    if not all(i.startswith("DKBW") for i in layer_ids):
        refuse("an identifier in the bathing-site layer does not begin DKBW")
    if not layer_ids <= table_ids:
        refuse(f"{len(layer_ids - table_ids)} identifiers of the bathing-site layer are not "
               "among the EEA table's; the page says every one is")

    b = J("hypodraft_b1.json")
    if int(never) <= int(b["sites"]):
        refuse("the table no longer holds more never-delisted identifiers than the layer holds sites")
    if not ODD_CSO <= set(b["cso"]["type"]) or not ODD_RBU <= set(b["rbu"]["type"]):
        refuse("the overflow files no longer carry the type codes the page names")
    cso, rbu, dep, near = b["cso"], b["rbu"], b["critical_depth_mm"], b["nearest"]

    per_season = n_s / (last - first + 1)
    lod_pct = live.step("K-SUBSET-SHARE", lod / n_s * 100)
    spill_pct = live.step("K-SUBSET-SHARE", cso["spills_null"] / cso["n"] * 100)
    per_date = s_dat / dates
    days_season = dates / seas_dat
    shifts = last - first
    k = shifts + 1
    floor = 1 / k
    seasons = last - first + 1

    strata, draws = P("ba_b1_strata_km"), P("ba_b1_draws")
    ring_m, ring_km = P("ba_b1_ring_m"), P("ba_b1_ring_km")
    lags = [P(n) for n in ("ba_b1_lag_a_h", "ba_b1_lag_b_h", "ba_b1_lag_c_h", "ba_b1_lag_d_h")]

    # the episode log's rows, each located by its whole row in the pin
    PHR = {t: f'"periodType":"{t}","n":{n},"first_season":{a},"last_season":{z}'
           for t, n, a, z in (("shortTermPollution", 1208, 2011, 2024),
                              ("bathingProhibition", 755, 2017, 2024),
                              ("abnormalSituation", 76, 2011, 2024),
                              ("cyanobacteriaBloom", 76, 2019, 2024))}

    def PR(t, shown):
        return RD("BA-WISE-DK-PERIODS", shown, PHR[t])

    o = []
    w = o.append
    w(f"# {R('B1', title=True)}")
    w("")
    w("*Generated by `scripts/pages/hypodraft_b1.py`: what the data held here, and the "
      "public records named, can and cannot show about the hypothesis. Each marked "
      "statement links to what it rests on.*")
    w("")
    w("**Draft, not a result.** "
      + C("C-BA-B1-STATUS", "The test this page specifies has not been run: no script in "
          "this repository fetches the bathing-water samples, joins a rain series to them, "
          "or computes either consequence."))
    w("")
    w("## The observable consequence")
    w("")
    w(C("C-BA-B1-VOLUME", f"{R('B1')} is to be discriminated *against per-outfall discharge "
        "volume*. That volume is reported to PULS at one of the knowledge levels "
        "Miljøstyrelsen's DP02 sets, from a PULS calculation to measurement-based "
        "estimation, and how many structures report a measured volume is not known here; "
        "below the measured level it is a model output driven by rainfall, which drives "
        "every rival too, so regressing a rainfall-driven response on it tests rainfall.")
      + " "
      + C("C-BA-B1-HALF", "This draft takes a **weaker, falsifiable half**: combined systems "
          "deliver *raw sewage* to the shore, event-timed, on a schedule set by their own "
          "storage. Two consequences follow, neither using a modelled volume."))
    w("")
    w(C("C-BA-B1-C1", "**`C1` — the class contrast.** At bathing sites whose nearest "
        "rain-conditioned outfall is **combined** (`OV/OS/OF/OK/Bypass`), the "
        "faecal-indicator response to antecedent rainfall is **steeper** than where the "
        "nearest is **separate** stormwater (`SE/SF`), at equal distance, region, month and "
        "rainfall.")
      + " "
      + C("C-BA-B1-TYPETAL", "The typetal in DP02 put total nitrogen at "
          f"{RD(DP, '12', 'Tot-N 10 43 12')} mg/l in overflow water and "
          f"{RD(DP, '43', 'Tot-N 10 43 12')} mg/l in sewage, against "
          f"{RD(DP, '2', 'Regnvandsudløb (mg/l) BI5 6 COD 50 Tot-N 2')} mg/l at a separate "
          "system's stormwater outlet.")
      + " "
      + C("C-BA-B1-SEWAGE", "Overflow water carries sewage and separate stormwater is meant "
          "to carry none, so a faecal indicator should rise more with rain where the nearest "
          "outfall is combined — though runoff can bring animal faeces into both arms.")
      + " "
      + C("C-BA-B1-C1-FALSIFY", "*Falsified if the class × rain interaction is inside the "
          f"null below, or negative.* {R('B2')} alone predicts a rain main effect in "
          f"**both** arms and a null interaction — so this is the {R('B1')}/{R('B2')} "
          "discrimination."))
    w("")
    w(C("C-BA-B1-C2", "**`C2` — the storage kink.** A combined structure spills once rain "
        "exceeds what it stores. `(vol_sb + vol_fbas)` over `Red areal` gives a **critical "
        "rainfall depth in mm** per structure, from engineering attributes that do not move "
        f"with the weather. {R('B1')} predicts a **kink** at that site-specific, *a-priori* "
        "depth, with no free breakpoint. *Falsified if the kink amplitude at each site's own "
        "threshold sits inside the null from permuting thresholds.*"))
    w("")
    w(C("C-BA-B1-CONFOUND", "**How the shared-rainfall confound breaks.** Rainfall enters "
        "both arms of `C1` identically and cancels in the contrast. In `C2` the *location* "
        "of the threshold is the signal, and it varies for reasons the weather does not "
        "know: runoff, riverine particulate organic carbon, buoyancy, resuspension and "
        "bather density are all smooth in rainfall and none carries a basin volume. No "
        "modelled overflow volume enters either statistic."))
    w("")
    w("## The data, counted here")
    w("")
    w(C("C-BA-B1-TAXONOMY", "Error classes are those of [a taxonomy that rates a data "
        f"stream by the errors it can contain]({TAX}): `2` is quantisation, among it "
        "censoring at a threshold; `4` schema conflation, one column pooling "
        "incommensurables; `6` an absent dimension, no column at all; `7` model-as-datum, "
        "a modelled value in a column shaped like a measured one."))
    w("")
    ecl = ('"escherichiaColiStatus":"missingValue","n":688,"with_value":688')
    enl = ('"intestinalEnterococciStatus":"limitOfDetectionValue","n":31478,"with_value":31478')
    enm = ('"intestinalEnterococciStatus":"missingValue","n":723,"with_value":723')
    w("- " + C("C-BA-B1-WISE", "**Bathing-water samples.** The EEA's WISE table "
               "`timeseries_MonitoringResult`, queried through `discodata.eea.europa.eu/sql`, "
               f"holds {n_s:,} Danish samples, each dated and each with an E. coli and an "
               f"enterococci count, under {n_ids:,} site identifiers over the seasons "
               f"{first}–{last}: {per_season:,.0f} a season on average. No count is empty. "
               f"E. coli is flagged at the limit of detection on {lod:,} samples and as a "
               f"missing value on {RD('BA-WISE-DK-ECOLI', '688', ecl)} that still carry a "
               f"number (enterococci: {RD('BA-WISE-DK-ENTERO', '31,478', enl)} and "
               f"{RD('BA-WISE-DK-ENTERO', '723', enm)}). A record has a sample date and no "
               "time of day.")
      + " "
      + C("C-BA-B1-WISE-CLASS", "The detection-limit flag is censoring, class `2`: boundable, "
          "not recoverable. The missing time of day is class `6`, an absent dimension, which "
          "no processing can restore."))
    w("- " + C("C-BA-B1-PERIODS", "**The dated episode log**, `timeseries_SeasonalPeriod`, "
               f"holds for Danish sites {PR('shortTermPollution', '1,208')} "
               f"`shortTermPollution` periods ({PR('shortTermPollution', '2011')}–"
               f"{PR('shortTermPollution', '2024')}), {PR('bathingProhibition', '755')} "
               f"`bathingProhibition` (from {PR('bathingProhibition', '2017')}), "
               f"{PR('abnormalSituation', '76')} `abnormalSituation` and "
               f"{PR('cyanobacteriaBloom', '76')} `cyanobacteriaBloom` periods."))
    stp = '"sampleStatus":"shortTermPollutionSample","n":1272'
    rep = '"sampleStatus":"replacementSample","n":1205'
    pre = '"sampleStatus":"preSeasonSample","n":22912'
    w("- " + C("C-BA-B1-FLAGS", "**Sample flags** over the same samples: "
               f"{RD('BA-WISE-DK-SAMPLESTATUS', '1,272', stp)} `shortTermPollutionSample`, "
               f"{RD('BA-WISE-DK-SAMPLESTATUS', '1,205', rep)} `replacementSample`, "
               f"{RD('BA-WISE-DK-SAMPLESTATUS', '22,912', pre)} `preSeasonSample`. The table "
               "keeps all of them; which of them a compliance assessment may set aside is the "
               "Directive's rule, which was not read here."))
    w("- " + C("C-BA-B1-LAYER", "**Bathing sites.** `data/raw/national/badevand.geojson` "
               f"holds {b['sites']:,} sites with latitude, longitude and a `DKBW…` "
               "identifier, and every one of its identifiers is among the Danish identifiers "
               f"of the EEA table. The table holds more — {n_ids:,} with samples, {never:,} of "
               "them never marked delisted — so delisting does not account for all of the "
               "difference."))
    w("- " + C("C-BA-B1-CSO", "**Combined overflows.** "
               f"`data/raw/spildevand/combined_overflow.geojson` holds {cso['n']:,} structures "
               "with `Red areal`, an annual volume and `Antal overløb`; `Antal overløb` is "
               f"empty for {cso['spills_null']:,} of them ({spill_pct:.1f}%), the volume empty "
               f"for {cso['volume_null']:,} and zero for {cso['volume_zero']:,}.")
      + " "
      + C("C-BA-B1-CSO-VOLUME", "The annual volume is modelled wherever it is not measured "
          "— class `7` there — and is not used here."))
    w("- " + C("C-BA-B1-RBU", "**The national register** "
               f"`data/raw/national/punkt_rbu_udl.geojson` holds {rbu['n']:,} rain-conditioned "
               f"outfall points: `vol_sb` is filled on {rbu['vol_sb_nonnull']:,} "
               f"({rbu['vol_sb_zero']:,} of them zero), `vol_fbas` on "
               f"{rbu['vol_fbas_nonnull']:,} ({rbu['vol_fbas_zero']:,} zero)."))
    w("- " + C("C-BA-B1-JOIN", f"**The two together.** {b['join']['matched']:,} of "
               f"{b['join']['cso_names']:,} distinct overflow names equal a register "
               "`pkt_navn`. The two files disagree on how many structures there are of a type "
               f"— `OV` {cso['type']['OV']:,} against {rbu['type']['OV']:,}, `OF` "
               f"{cso['type']['OF']:,} against {rbu['type']['OF']:,} — and both carry type "
               "codes that are not among DP02's structure codes: `UR`, `OVI`, `OSI` and "
               "`OKI`, and in the register `ikke oplyst`.")
      + " "
      + C("C-BA-B1-JOIN-CLASS", "A code outside DP02's lists is a column holding what its "
          "schema does not define: class `4`, not boundable from inside the files."))
    w("- " + C("C-BA-B1-DEPTH", "**Derived here: critical rainfall depth.** "
               f"{dep['n']:,} overflows have a name matching exactly one register point, "
               "positive storage and positive reduced area; their depth is "
               f"{dep['p10']:g} mm at the tenth percentile, {dep['median']:g} mm at the "
               f"median, {dep['p90']:g} mm at the ninetieth and {dep['max']:,} mm at the "
               "most.")
      + " "
      + C("C-BA-B1-TAIL", f"A basin that stores {dep['max']:,} mm of rain over its reduced "
          "area is implausible, so the tail is taken as a unit error and trimmed above the "
          "`p95`."))
    w("- " + C("C-BA-B1-NEAREST", "**Derived here: the nearest outfall.** Of the "
               f"{b['sites']:,} bathing sites, {near['combined']:,} have a combined structure "
               f"nearest and {near['separate']:,} a separate outlet; the median distance is "
               f"{near['median_km']:g} km, {near['within_1km']:,} lie within a kilometre "
               f"(`within_1km`) and {near['within_2km']:,} within two (`within_2km`)."))
    w("- " + C("C-BA-B1-RAIN", "**Rainfall is the gap.** No rain-gauge series is held. The "
               "rain record held, under `data/raw/weather`, is hourly ERA5 reanalysis over "
               "Copenhagen from Open-Meteo, and the Baltic winds under `data/raw/marine` are "
               "ERA5 too; a reanalysis in place of gauges would be class `7`.")
      + " "
      + C("C-BA-B1-DMI", "DMI's metObs API serves station precipitation at ten-minute and "
          "hourly steps (`precip_past10min`, `precip_past1h`); the source register records "
          "test queries answered with no API key, contradicting older documentation, and "
          "says to confirm the key policy before building on it."))
    w("")
    w("**Other sources, and whether each is a production path separate from modelled "
      "volume.** "
      + C("C-BA-B1-NONATIONAL", "No national series of measured overflow is held or was "
          "found here: the public extract carries each structure's reported annual volume "
          "and number of overflows, and how many of those volumes were measured is not "
          "known."))
    w("")
    w("- " + C("C-BA-B1-SRC-WISE", "**WISE bathing water** (above) — **a separate path**: "
               "counts per dated sample and the periods authorities report, with no "
               "hydraulic model in the chain."))
    w("- " + C("C-BA-B1-SRC-VHF", "**Vesthimmerlands Forsyning** "
               "(`/spildevand/overloebsdata`) publishes, for the "
               f"{RD('BA-VHF-OVERLOEB', '11', 'I Vesthimmerland er der kun 11&nbsp;registrerede')} "
               "registered overflow points on its combined systems, monthly counts and "
               "volumes of overflow for 2025 with an archive of earlier years; the points "
               "carry sensors that measure overflow, and some discharge to the Limfjord.")
      + " "
      + C("C-BA-B1-SRC-VHF-LEVEL", "So a measured set, but a small one — and whether its "
          "volumes meet DP02's measurement-based level, whose examples add measured "
          "substance to measured flow, the page does not say."))
    w("- " + C("C-BA-B1-SRC-KBH", "**Copenhagen's bathing-water forecast** — whether it "
               "keeps a public archive of measured overflow is not established: its host "
               "`kbh.badevand.dk` did not resolve from here."))
    w("- " + C("C-BA-B1-SRC-PULS", "**PULS**, where every rain-dependent discharge is "
               "reported with its volume graded by how it was found, would name an "
               "instrumented subset; access goes through an organisation's IT coordinator, "
               "and this project reads only the public extract."))
    w("- " + C("C-BA-B1-SRC-DP02", "**DP02** states the uncertainty of a reported volume by "
               "knowledge level, from "
               f"{RD(DP, '135', 'Niveau for usikkerhed på udledt stofmængde 135 % 100 %')}% for "
               f"a simple mass balance to {RD(DP, '30', 'Niveau 5 30 %')}% for "
               "measurement-based estimation: the citation for class `7`, not data."))
    w("- " + C("C-BA-B1-SRC-UWWTD", "**Waterbase-UWWTD** reports discharge points and "
               "agglomerations of the urban waste-water directive per reporting cycle; the "
               f"source register lists it for {R('B3')} and {R('A4')}, not for overflow."))
    w("- " + C("C-BA-B1-SRC-VP3", "**MiljøGIS `vp3basis2019`**: the national VP3 web "
               "feature service answered an anonymous capabilities request when this project "
               "probed it."))
    w("")
    w("## The null, under the constraint imposed")
    w("")
    w(C("C-BA-B1-CLUSTER", f"The nominal null for {n_s:,} samples is wrong: sampling is "
        "day-clustered. Over the seasons 2011–2024 the table's "
        f"{s_dat:,} Danish samples fall on {dates:,} distinct dates, {per_date:,.0f} per "
        f"date and {days_season:,.0f} sampling days a season. Weather is common within a day "
        "and correlated across the country, so the independent unit is the **site-day "
        "cluster**, and even those dates are not independent draws on weather."))
    w("")
    w("- " + C("C-BA-B1-N1", "**`N1` (primary, `C1`): permute the class label** across "
               "sites within strata of (distance decile × region × outfall count within "
               f"{strata} km), {draws:,} draws — destroys the combined/separate contrast, "
               "preserves rainfall, geography, season and site baselines."))
    w("- " + C("C-BA-B1-N2", "**`N2` (`C1`): circular shift of the daily rainfall field by "
               f"whole years**, {shifts} non-zero shifts over the seasons {first}–{last}, "
               "preserving seasonality, day-clustering and autocorrelation. **The smallest "
               f"attainable p is one in {k}, {floor:.3f} — state it, never exceed it.** Report "
               "the more conservative of `N1` and `N2`."))
    w("- " + C("C-BA-B1-N3", "**`N3` (`C2`): permute the predicted threshold** across "
               "structures within a spill-volume stratum: keeps the kink, destroys the link "
               "to a site's own storage."))
    w("- " + C("C-BA-B1-CENSOR", f"**Left-censoring is not small**: {lod:,} of {n_s:,} "
               f"E. coli values sit at the limit of detection ({lod_pct:.1f}%). Fit a "
               "censored-normal on log10 counts; a substitution rule invents the effect."))
    w("- " + C("C-BA-B1-POSITIONS", "**Sites are positions, not replicates**, never "
               "aggregated into water bodies: the unit is outfall-to-site distance, which is "
               "what the mechanism has."))
    w("")
    w("## Procedure")
    w("")
    w("1. " + C("C-BA-B1-P1", "Stream the Danish subset of `timeseries_MonitoringResult` and "
                "`timeseries_SeasonalPeriod` from DISCODATA; join to `badevand.geojson` on "
                "its `DKBW…` identifiers."))
    w("2. " + C("C-BA-B1-P2", "Per site: nearest combined and nearest separate register "
                f"point, and counts within {ring_m} m, {ring_km} km and {strata} km. Keep the "
                "geometry; aggregate nothing."))
    w("3. " + C("C-BA-B1-P3", "Rainfall: confirm DMI's key policy, then antecedent depth "
                f"over {lags[0]}, {lags[1]}, {lags[2]} and {lags[3]} h before each sample at "
                "the nearest gauge. Until then the design is stated, not run."))
    w("4. " + C("C-BA-B1-P4", "**`C1`:** censored regression of log10 E. coli on rain × "
                "class, with site fixed effects, month, distance and year. Report the "
                "interaction. Repeat on enterococci — a second organism, not a second "
                "dataset."))
    w("5. " + C("C-BA-B1-P5", f"**`C2`:** for the {dep['n']:,} threshold-bearing structures "
                "and their nearest sites, test the jump at each site's own predicted depth, "
                "standardised and summed across sites."))
    w("6. " + C("C-BA-B1-P6", "**Anchor:** samples inside a declared `shortTermPollution` "
                "period against matched samples at the same site and month outside one — the "
                "arm that uses no rain model at all."))
    w("7. " + C("C-BA-B1-P7", "Null under `N1`, `N2` and `N3`."))
    w("")
    w("## What a result would and would not license")
    w("")
    w(C("C-BA-B1-WOULD", "**Would.** That combined systems deliver sewage-borne "
        f"contamination to the shore, event-timed, near their outfalls, across {seasons} "
        f"seasons and {b['sites']:,} sites — and via `C2` that the timing is set by storage, "
        f"not weather alone. It separates {R('B1')} from {R('B2')} on a signature rather "
        "than a shared driver."))
    w("")
    w("**Would not.** "
      + C("C-BA-B1-NOT-OXYGEN", f"(a) **Nothing about oxygen.** This is {R('B1')}'s delivery "
          f"limb, bearing on {R('O9')}, not on {R('O1')}: faecal indicators are not COD, so "
          "the oxygen claim stays unscored — and they are not the rotting algae that "
          f"fedtemøg names, so {R('O2')} stays unscored too.")
      + " "
      + C("C-BA-B1-NOT-LOAD", "(b) No load, no volume, no attribution — there is no "
          "denominator, so any *share of* is out of reach by construction.")
      + " "
      + C("C-BA-B1-NOT-WINDOW", "(c) The window is **bathing season only**, set by human "
          "use and so circular, as [NITROGEN.md](../NITROGEN.md) argues.")
      + " "
      + C("C-BA-B1-NOT-SELECTED", "(d) Sampling may be **selected against the exposure** — "
          "if visits avoid storms, and since the table flags replacement samples beside "
          "short-term-pollution ones — which would attenuate the effect toward zero, so a "
          "positive result survives it but a null does **not** license *no effect*.")
      + " "
      + C("C-BA-B1-NOT-TWO", "(e) E. coli and enterococci are two counts from one sample "
          "and one visit: one piece of evidence, not two."))
    w("")
    w(C("C-BA-B1-IMPROVE", "**Smallest improvement:** the per-structure knowledge level "
        "from PULS, or a measured-overflow record such as Vesthimmerlands Forsyning "
        "publishes. Either converts a structural proxy into an instrumented subset and moves "
        "the exposure out of class `7`."))
    return "\n".join(o) + "\n"


def main(argv):
    try:
        page = text()
    except live.Unjustified as e:
        print(e, file=sys.stderr)
        return 1
    return 0 if draftkit.build(REL, page) is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
