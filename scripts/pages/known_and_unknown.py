#!/usr/bin/env python3
"""docs/KNOWN_AND_UNKNOWN.md - what is known, by whom, and the discovery rate.

Every assertion on the page is a checked claim (LIVE_NUMBERS.md section 11), in
data/manual/claims.d/w2-kp.json. Counts come from the extracts' full-row counts
(scripts/ds_facts.py), the enumerations, the hypothesis facts and pinned
documents. The page is about this project's own record of what it did not know,
so some claims are historical - what was said and found, and when - and those
rest on this repository's history; only they quote a past commit. What the page
used to say and no longer can is in docs/ARCHIVE.md.

    python3 scripts/pages/known_and_unknown.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import DERIVED, ROOT, log, write_doc
import claims
import live

OUT = os.path.join(ROOT, "docs", "KNOWN_AND_UNKNOWN.md")
B, E, C = live.claim_begin, live.CLAIM_END, live.claim


def J(*p):
    return live.live_json(os.path.join(*p))


def main():
    en, cv, meta = J(DERIVED, "enums.json"), J(DERIVED, "convergence.json"), J(DERIVED, "meta_facts.json")
    ds, hf = J(DERIVED, "ds_facts.json"), J(DERIVED, "hypodraft_facts.json")
    tri = J(DERIVED, "triage.json")
    CL = claims.load()[0]
    cache = {}

    def pin(text):
        return claims.resolve(CL, text, cache)[0]

    def share(part, whole):
        return live.step("K-SUBSET-SHARE", part / whole * 100)

    ctd_rows = f"{en['ctd']['rows'] / 1e6:.1f}M"
    kemi_rows = en["kemi"]["rows"]
    sonde_pct = share(en["ctd"]["categorical"]["SondeNr"]["999"], en["ctd"]["rows"])
    ku = ds["kemi"]
    ortho = ku["units"]["Orthophosphat"]
    ortho_mg = share(ortho["mg/l"], ortho["mg/l"] + ortho["µg/l"])
    hz = hf["hazardous"]
    hirt = ds["maaledybde"]["hirtshals_15m"]
    dyreenhed = pin("{count:BEK931-2024:dyreenhed}")
    n170 = pin("{read:BEK931-2024:170|divideret med 170 kg}")
    drained = pin("{read:KP-DRAENKORT-DCA135:52|På det endelige kort er 52% af markarealet drænet}")
    res_m = pin("{read:KP-DRAENKORT-DCA135:30.4|Kortet har en opløsning på 30,4 x 30,4 meter og en nøjagtighed på 79%}")
    accuracy = pin("{read:KP-DRAENKORT-DCA135:79|Kortet har en opløsning på 30,4 x 30,4 meter og en nøjagtighed på 79%}")
    flood_before = live.was("5df1889", "docs/FLOOD_GAP.md", "Across @@ km² of modelled flooding")
    flood_after = live.was("c8e5a6b", "docs/FLOOD_GAP.md", "Across @@ km² of modelled flooding")
    nine = tri["clusters"]["vandkemi"]["n"]

    text = f"""# What is known, by whom

{C("C-KP-HEADLINE", "This project used to be headed *\"What Denmark knows about its own coastal water.\"* That was a claim we were not entitled to make, and this page is why.")}

{C("C-KP-FETCHED", "We can characterise **what is in the data we fetched**. That is a different object from what Denmark knows, and the difference is a whole quadrant wide.")}

---

## The four quadrants, and which one is dangerous

{C("C-KP-QUADRANTS", "The quadrants sort what this project holds and misses by two questions: whether a thing exists, and whether we know we have it.")}

| | we know we have it | we don't know we have it |
|---|---|---|
| **it exists** | **known known** — the {ctd_rows} CTD measurements, and everything computed from them | **UNKNOWN KNOWN** — data that exists, is held by someone, and is absent from our map |
| **we know it's missing** | **known unknown** — the {meta['gated_sources']} gated sources in [If you have data access we don't](IF_YOU_HAVE_THE_DATA.md), {meta['gated_slots']} of them with a slot the analysis is already written against | **unknown unknown** — measurements nobody makes and nobody has thought to want |

{C("C-KP-UNKNOWN-KNOWN", "**The unknown known is the dangerous one**, because it is indistinguishable from absence when you are inside the archive.")} Some of those we found:

- {C("C-KP-CTD-PARAMS", f"`ctd.csv.gz` carries **{meta['ctd_parameters']} distinct `Parameter` values**, including **Turbiditet** and **FDOM**; the station series this project analyses carry {hf['series']['variables']} variables, drawn from five of them.")}
- {C("C-KP-VEGETATION", "The ODA topic tree holds **eelgrass**, **macroalgae** and **bottom fauna** topics, and none is in the fetch script.")}
- {C("C-KP-FISHING", "Fishing effort is published openly: [Global Fishing Watch's apparent fishing effort](https://zenodo.org/records/14982712), version three, covering 2012–2024, as a direct download with no login.")}

{C("C-KP-NOTHIDDEN", "None of those was hidden; they were simply not looked for. **So any sentence in this project of the form \"Denmark does not measure X\" should be read as \"X is not in what we fetched\"** — and the two are not the same claim.")}

---

## What the discovery rate tells you

{C("C-KP-ESTIMATOR", "**A known unknown can be priced. An unknown known cannot** — by construction, since you would have to know it to count it. So there is only one estimator of its size: **the rate at which you keep finding them.**")}

{C("C-KP-RATE", "The first list of such finds, published on 9 September, held six. The second, published the next afternoon, held ten more, and nothing about that rate suggests we are near the end of them.")}

### The second list

| | what it was | where it had been the whole time |
|---|---|---|
| **A clock on every row** | {C("C-KP-T-NOCLOCK", "this project said *no row in the archive carries a clock time* and built a class of *unscoreable* on it")} | {C("C-KP-T-CLOCK", f"`Startklok`, on **all but {kemi_rows - en['kemi']['nonblank']['Startklok']} of {kemi_rows:,}** water-chemistry rows. The claim was true of the CTD extract and inferred from a topic nobody had fetched")} |
| **The topic itself** | {C("C-KP-T-TOPIC-BLOCK", f"{nine} hypotheses were blocked on it")} | {C("C-KP-T-TOPIC", "named in `fetch_oda.py`'s own docstring and missing from its `TOPICS` dict; it has since been fetched")} |
| **Two units in one column** | averages taken across them | {C("C-KP-T-UNITS", f"**{ku['parameters_multi_unit']} of {ku['parameters']} parameters**. `Orthophosphat` is in mg/l on {ortho_mg:.0f}% of its rows and in µg/l on the rest, a thousandfold apart; integrated primary production is spread over several units")} |
| **The flood sheets are photographs** | {C("C-KP-T-REG", f"registered by correlating against water polygons, at {cv['stated_error_min_m']:.0f}–{cv['stated_error_max_m']:.0f} m")} | {C("C-KP-T-PHOTOS", "they carry an **orthophoto basemap** — buildings, streets, Rådhuspladsen's fountain — so the strongest cue for placing them was not the one used")} |
| **Grid north is not north** | {C("C-KP-T-NORTHUP", "*\"every sheet has north up (the north arrow confirms it)\"*, as the placement code still says")} | {C("C-KP-T-NORTH", f"meridian convergence of **{cv['gamma_min_deg']:.2f}–{cv['gamma_max_deg']:.2f}°**, displacing corners **{cv['shift_min_m']:.0f}–{cv['shift_max_m']:.0f} m** — {cv['shift_over_error_min']:.1f} to {cv['shift_over_error_max']:.1f} times the registration error the pipeline reports for itself")} |
| **Censoring with no name** | read as measurements | {C("C-KP-T-CENSOR", f"`ResultatAttribut` = `<` on **{en['kemi']['categorical']['ResultatAttribut']['<']:,} rows**, where the value is the *detection limit*; `SigtTilBund` on {ds['maaledybde']['secchi_to_bottom']:,} Secchi readings that reached the bottom")} |
| **Values no instrument gave** | averaged | {C("C-KP-T-SENTINEL", f"depth exactly `99` on {ku['depth_exactly_99']:,} rows; a station named `Hirtshals 15 m` with bottom depths up to {hirt['max_m']:.1f} m (median {hirt['median_m']:.1f} m); oxygen saturation recorded up to {ku['saturation_max_pct']:,.0f}%")} |
| **The regulatory unit is void** | a headline figure framed on DE/ha | {C("C-KP-T-DE", f"`dyreenhed` occurs **{dyreenhed} times** in BEK 931/2024. The binding ceiling is {n170} kg N per hectare of harmoniareal")} |
| **A national drainage map** | *"drained areas are not mapped"* | {C("C-KP-T-DRAIN", f"mapped for Miljøstyrelsen at a {res_m} m resolution: {drained}% of agricultural land drained, with a stated accuracy of {accuracy}%, in a report we had not read")} |
| **One column, three meanings** | one guard written for all of them | {C("C-KP-T-KFAKTOR", "`KorrektionsFaktor` is a Winkler-to-electrode ratio for oxygen, a calibration against chlorophyll for fluorescence, and, for CTD temperature and salinity, a factor the instruction does not describe")} |

{C("C-KP-TEN", "**Ten, and worse than the first six**, because most are not things Denmark failed to publish. They are properties of files we already held and had already analysed. The first list was about the edge of the archive; the second was about its middle.")}

{C("C-KP-DID-NOT-FALL", "**The rate did not fall. That is the whole measurement.** Two samples is not a trend, but nothing here supports the belief that a second pass exhausts a first pass's blind spots, and the second pass was not even looking — it was fetching one topic and counting distinct values in columns.")}

### A sixth kind: the unknown known in your own output

{C("C-KP-OWN-OUTPUT", "One kind of unknown known does not fit the quadrants, because it is not about Denmark's data at all: a derived number of our own that has gone stale.")} {C("C-KP-FLOOD-STALE", f"After one flood sheet was re-registered, the figures computed from it stayed on the superseded placement until the scripts that read it were rerun: the modelled flood area this site published moved from {flood_before} to {flood_after} km² when they were.")}

{C("C-KP-GUARD", "What kept it stale is the part worth generalising. The tool that checks generated documents reported that regenerating would remove *substantial lines* — which reads as **your prose is about to be destroyed** — when the lines were ones whose numbers had changed and which the regeneration replaced. *This output is stale* and *you are about to lose something* came out in the same words, and the cautious response to the second is the wrong response to the first. The tool now tells a replaced line from a lost one.")}

{C("C-KP-OWN-ARTEFACTS", "**So the quadrants need a row for your own artefacts.** A derived number is held data too, it goes stale silently, and nothing in the archive tells you. The fix that generalises is not vigilance: it is making the tools tell the two cases apart.")}

### What was built in response

{C("C-KP-BUILT", "[CLAIMS.md](CLAIMS.md) is the structural half of the answer to this page. Every checked claim is registered with the graph of what it stands on, down to data, a pinned document, a stated assumption, a gap, code, this project's history or an explicit end of the trail; the graph is checked for cycles; and a claim goes stale when anything under it changes. What could not be justified is kept, in its own words, in [ARCHIVE.md](ARCHIVE.md). That does not find unknown knowns. It does stop a claim from quietly outliving the thing it rested on.")}

### The residual-growth test, turned on ourselves

{C("C-KP-RESIDUAL-GROWTH", "This project's method 6 says: move a part `P` out of a leftover, and the arithmetic must give `R_new = R_old − P`. If it doesn't shrink, the leftover was absorbing model error and was never a partition. Apply it to *\"what Denmark does not measure.\"* Each discovery moved a part out. Did the leftover shrink by that part? **No — it grew.** Finding a thing you should have known raises your estimate of what else you have missed; it does not lower it. A leftover that behaves that way was never a partition of the world. It was absorbing our own ignorance, and reporting it as a property of Denmark.")}

### Absence of evidence, priced

{C("C-KP-SENSITIVITY", "*\"We looked and found nothing\"* supports *\"there is nothing\"* exactly as far as **P(not found | it exists)** is small. That probability is the sensitivity of the search, and nobody states it — including us, until now. Ours was poor: the first list alone held six things the search had missed. So the inference was never licensed, whatever the topic.")}

> {C("C-KP-CALIBRATE", "**Calibrate the search with known positives.** Seed it with things you already know exist and count how many come back. That detection rate is the null for every absence claim built on it. Without it, \"not measured\" means \"not found by an uncharacterised procedure\", which supports nothing.")}

### The two failure modes are symmetric

| | reading | cases |
|---|---|---|
| **absence → absence** | "we didn't find it" ⇒ "it isn't there" | {C("C-KP-FM-ABSENCE", "the lists above, of which *\"no row carries a clock time\"* is the purest: a property of one unfetched topic, reported as a property of the archive")} |
| **presence → evidence** | "there is a column" ⇒ "there is a measurement" | {C("C-KP-FM-PRESENCE", f"the national hazardous-substance layer's {hz['total']} points are all freshwater — {hz['lake']} in lakes, {hz['river']} in rivers, none coastal — so a marine column built from it would carry only freshwater points")} |

{C("C-KP-FM-WORSE", "The second is worse, because it *adds* confidence. But they share a root: **treating the shape of a search result as a property of the world.**")}

---

## The same map, from three vantage points

{C("C-KP-VANTAGE", "The quadrants are not a property of the data. They are a property of who is standing where.")}

### The Danish authority (DCE, Miljøstyrelsen)

{C("C-KP-AUTHORITY", "Most of our unknown knowns are their known knowns. But they have their own, and the project has found some:")}

- {C("C-KP-SONDE", f"**`SondeNr` arrives as `999` on {sonde_pct:.1f}% of CTD rows.** The probe number exists at the point of measurement — somebody held that instrument. It is lost between the ship and the archive, not absent from the world.")}
- {C("C-KP-CTD-NOCLOCK", f"**Time of day is absent from the CTD extract** — its {ctd_rows} rows carry a date and no hour — though the field-sampling instruction has the station log record the clock time.")}

### Us

{C("C-KP-US", "Our known knowns are narrow and well characterised. Our known unknowns are enumerated, in [If you have data access we don't](IF_YOU_HAVE_THE_DATA.md). **Our unknown knowns are unbounded and we cannot estimate them** — the lists above were found largely by accident, and there is no reason to think the rate has stopped.")}

{C("C-KP-NO-OBLIGATION", "The one thing we have that the authority structurally lacks: **no obligation to produce a number.** An unscoreable hypothesis can be left unscoreable here.")}

### Other connectors

{C("C-KP-CONNECTORS", "Utilities may hold measured overflow where the national account holds reported annual volumes. ICES, HELCOM, EMODnet and Copernicus hold effort, wave and optical layers, some of which this project has since fetched. Farmers hold actual application records where the balance holds norm coefficients. Universities hold cores, incubations and porewater profiles for mechanisms this project has had to mark as needing an experiment. For each, the relationship is asymmetric in the useful direction: **their known known is our unknown known**, and one email may close it.")}

---

## What follows for the headline

{C("C-KP-HEADLINE-NOW", "\"What Denmark knows about its own coastal water\" is an estimate **we** made, of the known-known quadrant only, from one vantage point, using data we fetched ourselves. It is a finding of this project, and a contestable one — not its title.")}

{C("C-KP-AUDIT", "The site now leads with what it is: an audit of a record, by someone outside the institutions that produced it, with the method stated so the conclusions can be checked. The knowledge claim sits below, labelled as ours.")}

{C("C-KP-CONSTRUCTION", "That is the same discipline applied everywhere else here. A count is a construction before it is a fact; so is a headline.")}

---

*Generated by `scripts/pages/known_and_unknown.py`. Every assertion on this page opens what it rests on; what the page used to say and no longer can is in [ARCHIVE.md](ARCHIVE.md).*
"""
    try:
        write_doc(OUT, text)
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
