#!/usr/bin/env python3
"""Generate docs/SETTLE.md - the experiment that would end the argument.

The protocol for the paired-catchment experiment that SENSING.md constructs the
instrument for. Every number is read from data, a pinned document or a stated design
choice (live.stated, with its reason), and every assertion is a checked claim
(LIVE_NUMBERS.md section 11), registered in data/manual/claims.d/w3-ss.json with what
it rests on. The page gives no prices, because none had a source. What the page once
said and could not justify is in docs/ARCHIVE.md, not here.

The rainfall table is counted here from the ERA5 hourly record that streams.py and
currents.py read (data/raw/weather), and stored in data/derived/settle.json with the
counts of the registers the page describes.

    python3 scripts/pages/settle.py

Writes data/derived/settle.json and docs/SETTLE.md. Peak memory: one raw weather file
(a few MB of JSON) at a time, plus one float per calendar day of the record.
"""
import calendar
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common import DERIVED, RAW, ROOT, log, read_json, write_doc, write_json
import claims as _claims
import live

PAGE = "docs/SETTLE.md"
OUT = os.path.join(DERIVED, "settle.json")
WEATHER = os.path.join(RAW, "weather")
C, B, E = live.claim, live.claim_begin, live.CLAIM_END

HYPOTHESES = ("the soil reactor", "the bypass", "the regime")
SEASON_MONTHS = (2, 3, 4)            # February-April, the spreading window
THRESHOLDS_MM = (2, 5, 10)           # daily totals the table counts days at
TRIGGER_MM = 5                       # the row the sampler's trigger is read against

R_PAIRS = ("The design's choice, fixed before the experiment: enough matched pairs to see "
           "whether the effect scales with livestock density across soil and drainage "
           "types.")
R_CATCH = "Two catchments per pair, one of high and one of low livestock density."
R_YEARS = ("One year to establish the conversion ratios and shake out the fouling, one to "
           "answer the question.")
R_WINDOWS = ("The spreading window and an autumn control window, when liquid manure may not "
             "be spread, at the same sites with the same triggers.")
R_THRESH = ("Fixed before the first sample, so that the acceptance rule cannot be tuned to "
            "the result.")
R_POC = ("The page's choice for the proof of concept, so that a pass needs the trigger to "
         "work on more than one storm; no reason for this number rather than another was "
         "recorded.")
_REG = {}


def _cl():
    if "d" not in _REG:
        _REG["d"] = _claims.load()[0]
    return _REG["d"]


def RD(sid, value, phrase):
    """A number read from a pinned document, refused unless the pinned copy holds the
    phrase (tags set aside and entities read, as the claims register compares it)."""
    d = _cl()
    if _claims._flat(phrase) not in _claims._flat(_claims.pin_text(d, sid)):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    return live._mk(value, ["reading", sid, "phrase", phrase, _claims._meta(d, sid)])


def rain_days():
    """Days of each February-April season with at least each daily total, from the
    hourly ERA5 record: hourly precipitation summed per calendar day of the record's
    own clock (GMT, so UTC days - refused if the record says otherwise), missing hours
    skipped, one raw file at a time. A season must be whole or the page is refused."""
    day, zones = {}, set()
    for f in sorted(os.listdir(WEATHER)):
        if not f.startswith("wind_"):
            continue
        d = read_json(os.path.join(WEATHER, f))
        zones.add((d.get("timezone"), d.get("utc_offset_seconds")))
        h = d["hourly"]
        for t, p in zip(h["time"], h.get("precipitation") or []):
            if p is not None:
                day[t[:10]] = day.get(t[:10], 0.0) + float(p)
        del d, h
    if zones != {("GMT", 0)}:
        raise live.Unjustified(f"settle: the rain record's clock is {sorted(zones)}, not GMT "
                               "- the page counts UTC days")
    seasons = {}
    for k, v in day.items():
        if int(k[5:7]) in SEASON_MONTHS:
            seasons.setdefault(int(k[:4]), []).append(v)
    for y, vals in seasons.items():
        whole = sum(calendar.monthrange(y, m)[1] for m in SEASON_MONTHS)
        if len(vals) != whole:
            raise live.Unjustified(f"settle: the {y} season has {len(vals)} of {whole} days")
    years = sorted(seasons)
    rows = []
    for t in THRESHOLDS_MM:
        n = [sum(1 for v in seasons[y] if v >= t) for y in years]
        med = statistics.median(n)
        rows.append({"mm": t, "median_days": int(med) if med == int(med) else med,
                     "min_days": min(n), "max_days": max(n)})
    return {"source": "ERA5 hourly via Open-Meteo, data/raw/weather/wind_*.json "
                      "(the point streams.py names)",
            "day_clock": "UTC", "months": "February-April",
            "first_year": years[0], "last_year": years[-1], "seasons": len(years),
            "by_threshold": rows}


def values():
    """The live values the page reads, by name."""
    e = read_json(os.path.join(DERIVED, "experiments.json"))
    write_json(OUT, {"_what": "Counts docs/SETTLE.md states, taken from the registers they "
                              "describe, and the February-April rain-day counts of the ERA5 "
                              "record, by scripts/pages/settle.py.",
                     "designs": len(e["experiments"]),
                     "desk_designs": sum(1 for x in e["experiments"] if x.get("scale") == "desk"),
                     "hypotheses": len(HYPOTHESES),
                     "rain": rain_days()})
    c = live.live_json(OUT)
    x = live.live_json(os.path.join(DERIVED, "experiments.json"))
    t = live.live_json(os.path.join(DERIVED, "triage.json"))
    rb = live.live_json(os.path.join(DERIVED, "programme.json"))["rbu_register"]
    rain = c["rain"]
    trig = [r for r in rain["by_threshold"] if r["mm"] == TRIGGER_MM][0]
    return {
        "pairs": live.stated("settle_pairs", 12, "12", R_PAIRS),
        "pairs_word": live.stated("settle_pairs", 12, "twelve", R_PAIRS),
        "catchments": live.stated("settle_catchments", 24, "24", R_CATCH),
        "years": live.stated("settle_years", 2, "Two", R_YEARS),
        "years_lower": live.stated("settle_years", 2, "two", R_YEARS),
        "windows": live.stated("settle_windows", 2, "Two", R_WINDOWS),
        "threshold": live.stated("settle_threshold", 2 / 3, "two thirds", R_THRESH),
        "poc_events": live.stated("settle_poc_events", 3, "three", R_POC),
        "hypotheses": f"{c['hypotheses']}",
        "designs": f"{x['n_experiments']}", "desk": f"{x['by_scale']['desk']}",
        "unscoreable": f"{t['classes']['unscoreable']['n']}", "mechanisms": f"{t['n_triaged']}",
        "cso_n": f"{rb['top_one_pct_n']}", "cso_share": f"{rb['top_one_pct_share_pct']:.0f}",
        "cso_with": f"{rb['with_volume']:,}",
        "seasons": f"{rain['seasons']}", "first": f"{rain['first_year']}",
        "last": f"{rain['last_year']}",
        "rows": [(f"{r['mm']}", f"{r['median_days']}", f"{r['min_days']}", f"{r['max_days']}")
                 for r in rain["by_threshold"]],
        "trig_mm": f"{trig['mm']}", "trig_days": f"{trig['median_days']}",
        "era5_km": f"{RD('PG-WIKI-ERA5', 31, 'features a spatial resolution of 31 km')}",
    }


def render(v):
    o = []
    w = o.append
    w("# Fingerprinting Denmark")
    w("")
    w(C("C-SS-T-LEAD", "**The experiment that would end the argument, written so that both "
        "sides can commit to it before it runs.**"))
    w("")
    w(C("C-SS-T-DESIGN", "This page is not an audit of numbers that exist. It is a design for "
        "producing numbers that do not exist yet, aimed at a question the dispute turns on and "
        "that none of the monitoring this project has profiled measures directly:"))
    w("")
    w("> **When Danish fields receive slurry and then rain, what reaches the water — and")
    w("> whose is it?**")
    w("")
    w(C("C-SS-T-NAV", "[SENSING.md](SENSING.md) constructs the instrument: the fingerprint "
        "meant to separate a pig from a person from a road, and the two-tier network that could "
        "carry it.") + " [`X23`](EXPERIMENTS.md) is the entry in the register. **This page is "
      "the protocol** — what is claimed, what would refute it, how many catchments and how many "
      "storms, and the rules that have to be fixed before the first sampler is bolted to a "
      "culvert.")
    w("")
    w("---")
    w("")
    w(f"## 1. The {v['hypotheses']} hypotheses, stated so they can lose")
    w("")
    w(C("C-SS-T-HYPS", "The point of writing them out is that each makes a different prediction "
        "about the same measurements, so the data can pick. They are hypotheses, not findings: "
        "this page asserts none of them."))
    w("")
    w("| | Hypothesis | Predicts |")
    w("|---|---|---|")
    w("| **The soil reactor** | The field consumes the payload. Labile carbon is respired, "
      "ammonium nitrifies, and what leaves is mobile nitrate | Faecal markers stay near baseline "
      "through the spreading window. Nitrate rises seasonally, smoothly, with drainage. No "
      "relationship between marker peaks and livestock density |")
    w("| **The bypass** | Preferential flow, tile drains and rain onto fresh slurry deliver the "
      "payload close to intact | Marker and copper peaks within days of spreading, **scaling "
      "with livestock density**, concentrated in the rising limb of storms |")
    w("| **The regime** | Both are true, in different conditions. The bypass opens only when the "
      "ground is frozen, saturated or tile-drained, and closes otherwise | Marker peaks appear "
      "at **some** sites and not others, predicted by soil type, drainage and antecedent "
      "wetness rather than by livestock density alone |")
    w("")
    w(C("C-SS-T-EMBARRASS", "**The soil reactor is the outcome that would embarrass this "
        "project**, since part of its argument leans on the payload mattering. It is stated "
        "first on purpose, and the publication rule below is written so that it cannot be "
        "quietly dropped."))
    w("")
    w("---")
    w("")
    w("## 2. What the calendar does for us")
    w("")
    w(C("C-SS-T-CALENDAR", "The manipulation already exists and is applied nationally: Danish "
        "rules forbid spreading liquid organic manure and nitrogen fertiliser from after "
        "harvest, at the latest the start of October, until February, with exceptions they "
        "list.") + " " +
      C("C-SS-T-BEFOREAFTER", "So the experiment is **before-after on a fixed national "
        "schedule**, with a within-year control window that needs no permission from "
        "anyone."))
    w("")
    w(C("C-SS-T-RAIN", "And the events can be counted in advance. In the hourly rainfall "
        f"record used elsewhere in this project, over Copenhagen, {v['first']}–{v['last']}, "
        f"these are the days of each February–April season with at least a given daily total, "
        f"over its {v['seasons']} seasons:"))
    w("")
    w("| Daily total | Median days per season | Range |")
    w("|---|---:|---:|")
    for mm, med, lo, hi in v["rows"]:
        w(f"| ≥ {mm} mm | **{med}** | {lo}–{hi} |")
    w("")
    w(C("C-SS-T-SAMPLE", "**That is the sample size, and it is the reason the design works.** "
        f"A sampler that fires on days of {v['trig_mm']} mm or more would see a median of "
        f"{v['trig_days']} such days in a spreading season — a day being a UTC day, so a storm "
        "that spans two days counts twice — enough for a paired comparison within a single "
        "year, at a single site.") + " " +
      C("C-SS-T-FLOOR", f"ERA5, the reanalysis behind the record, has a spatial resolution of "
        f"{v['era5_km']} km, so each value is an average over a grid cell, which smooths a "
        "local downpour: the counts at the higher thresholds are more likely to understate "
        "what one catchment sees than to overstate it."))
    w("")
    w("---")
    w("")
    w("## 3. The design")
    w("")
    w("**Paired catchments, matched on everything except the thing under test.**")
    w("")
    w("- " + C("C-SS-T-D-PAIRS", f"**{v['pairs']} pairs** — {v['catchments']} catchments — "
               "matched on soil type, drainage class, area and slope, contrasted on **livestock "
               "density** from the national register. Small headwater catchments, so a signal is "
               "not diluted to nothing before it reaches the sensor."))
    w("- " + C("C-SS-T-D-TIERS", "**Both tiers at every site**: continuous stage, turbidity, "
               "conductivity, temperature and fDOM; an autosampler on a flow-and-turbidity "
               "trigger."))
    w("- " + C("C-SS-T-D-WINDOWS", f"**{v['windows']} windows a year**: the spreading window "
               "(February–April) and an autumn control window when liquid manure may not be "
               "spread. Same sites, same triggers, same laboratory."))
    w("- " + C("C-SS-T-D-ENDS", "**End members sampled directly**: slurry from the tanks in "
               "each catchment, effluent from any plant in it, road gully sediment, and soil. "
               "**No conversion ratio is taken from the literature** — every one is measured on "
               "the material that is actually there."))
    w("- " + C("C-SS-T-D-YEARS", f"**{v['years']} full years.** One to establish the ratios "
               "and shake out the fouling, one to answer the question."))
    w("")
    w(C("C-SS-T-D-PANEL", "**What is analysed per event:** faecal sterols with the herbivore "
        "ratio, host-specific microbial markers, crAssphage, acesulfame, one veterinary residue, "
        "copper and zinc, COD and BOD, total and dissolved N and P, and δ¹⁵N with δ¹⁸O of "
        "nitrate. Discharge at the same minute, or it is a concentration and not a load."))
    w("")
    w("---")
    w("")
    w("## 4. The decision rules, fixed before the first sample")
    w("")
    w(C("C-SS-T-R0", "These are the whole point of the page. A rule written afterwards is a "
        "story."))
    w("")
    w("1. " + C("C-SS-T-R1", "**The bypass is accepted** if faecal-marker load in the spreading "
                "window exceeds the autumn control window by a factor stated in advance at "
                f"**{v['threshold']} or more of the high-density sites**, and the effect scales "
                f"with livestock density across the {v['pairs_word']} pairs."))
    w("2. " + C("C-SS-T-R2", "**The soil reactor is accepted** if marker loads in the two "
                "windows are indistinguishable, by a criterion stated in advance, at the sites "
                "the first rule looks at, and nitrate is the only determinand that moves."))
    w("3. " + C("C-SS-T-R3", "**The regime is accepted** if the effect is present at some sites "
                "and absent at others *and* is predicted by soil, drainage or antecedent wetness "
                "better than by density."))
    w("4. " + C("C-SS-T-R4", "**The result is published whichever way it falls**, in full, with "
                "the raw series — and the pre-registration says so before the money is spent. "
                "**If the soil reactor wins, this project's own emphasis was wrong and the page "
                "saying so will carry that sentence.**"))
    w("5. " + C("C-SS-T-R5", "**No composite index is reported without the series it came "
                "from**, and no residual is named after a source. That is the failure this whole "
                "site documents; reproducing it here would be unforgivable."))
    w("")
    w("---")
    w("")
    w("## 5. What would invalidate the experiment rather than answer it")
    w("")
    w(C("C-SS-T-INVALID", "Written down in advance, so that none of them can be found "
        "afterwards as an excuse:"))
    w("")
    w("- " + C("C-SS-T-I-FOUL", "**Fouled sensors reading confidently.** Servicing schedule and "
               "co-location against a reference instrument, or the continuous tier is "
               "decoration. This is [`X16`](EXPERIMENTS.md)."))
    w("- " + C("C-SS-T-DNA", "**Decayed DNA.** Host markers detect recent contamination, so a "
               "marker absence at a site visited late is not evidence of absence. The sterols, "
               "which change slowly, are the check."))
    w("- " + C("C-SS-T-I-ENDS", "**Unmeasured end members.** If the slurry in *these* tanks "
               "was never sampled, every fraction is a guess with a decimal point on it."))
    w("- " + C("C-SS-T-I-CHASE", "**Storm-chasing bias.** Triggers are set in advance and left "
               "alone. An operator who decides which storms are interesting has destroyed the "
               "sample."))
    w("- " + C("C-SS-T-I-MATCH", "**Catchments matched on the wrong thing.** If the "
               "high-density catchments are also the sandy ones, the design has confounded "
               "exactly what it set out to separate — and the pairing has to be published so "
               "somebody else can say so."))
    w("")
    w("---")
    w("")
    w("## 6. What it needs, and how it could be built")
    w("")
    w(C("C-SS-T-PHASES", "[SENSING.md](SENSING.md) lists what to buy: the node, the sampler, "
        "the shared kit and the laboratory panel. No price is given there or here: the design "
        "says what to buy, and a supplier's quotation says what it costs. The laboratory is a "
        "cost per bottle and the sensors a purchase made once, so the bottles are the line that "
        "grows with the design, and the one that cannot be economised without losing the "
        "attribution the design exists for."))
    w("")
    w("### The proof of concept, which tests the instrument and not the hypothesis")
    w("")
    w(C("C-SS-T-POC", "**One pair of catchments, one spreading season, and a deliberately "
        "narrow question.** The distinction matters: a single pair cannot answer whether the "
        "payload reaches Danish water — the sample is one pair and the result would be a number "
        "people fight over. What it *can* do is establish that the method works, which is what "
        f"has to be true before anybody buys {v['catchments']} of anything."))
    w("")
    w("**What it has to prove, and the go/no-go on each:**")
    w("")
    w("- " + C("C-SS-T-G1", "**A cheap node survives.** Passes if one node returns a continuous "
               "record through a Danish February, with gaps that are explainable; fails if the "
               "enclosure floods, the panel ices, or the radio drops the winter."))
    w("- " + C("C-SS-T-G2", "**Its readings mean something.** Passes if, co-located against a "
               "reference sonde, turbidity and conductivity track it within a stated tolerance "
               "and the drift is characterisable; fails if drift is larger than the seasonal "
               "signal, in which case the continuous tier is a trigger only and must be "
               "described as one."))
    w("- " + C("C-SS-T-G3", "**The trigger catches events.** Passes if the sampler fires on the "
               "rising limb and fills bottles across the storm, unattended, "
               f"{v['poc_events']} times; fails if it fires on noise, or misses the events the "
               "rain record says happened."))
    w("- " + C("C-SS-T-G4", "**The panel discriminates *here*.** Passes if the sterol ratio and "
               "host markers separate this catchment's slurry from its sewage effluent and from "
               "its soil; fails otherwise — **and this is the one that kills the national "
               "design.** If the end members are not separable in one Danish catchment, "
               f"{v['pairs_word']} pairs will not fix it."))
    w("- " + C("C-SS-T-G5", "**The chain closes.** Passes if a reading taken at a culvert "
               "appears in a public series with its calibration state attached; fails if "
               "anything in the path needs a person to copy a file."))
    w("")
    w(C("C-SS-T-FOURTH", "**Note the fourth test.** It is the only one whose failure means *do "
        "not build the national network*. Everything else on this page is downstream of it, "
        "which is an argument for doing it first and alone."))
    w("")
    w(C("C-SS-T-STAGED", "**A staged path, with a decision at each step:**"))
    w("")
    w("- " + C("C-SS-T-S0", "**Stage `0` — one node**: a single stream, no sampler. Does the "
               "hardware survive and report?"))
    w("- " + C("C-SS-T-S1", "**Stage `1` — proof of concept**: one pair, one season, one "
               "sampler. Does the method discriminate, here?"))
    w("- " + C("C-SS-T-S2", "**Stage `2` — regional**: pairs in more than one region, both "
               "windows. Is the effect visible at all, and how variable?"))
    w("- " + C("C-SS-T-S3", f"**Stage `3` — the experiment**: {v['pairs_word']} pairs, "
               f"{v['years_lower']} years. Which of the {v['hypotheses']} hypotheses is "
               "right?"))
    w("- " + C("C-SS-T-S4", "**Stage `4` — the network**: every outlet that reaches the sea. "
               "The same answer everywhere, permanently."))
    w("")
    w(C("C-SS-T-NOWASTE", "**No stage is wasted if the next one is never funded.** Stage `0` is "
        "a real series from a real stream. Stage `1` is a publishable methods result either way. "
        "Stage `2` is a regional finding. That property is the reason to stage it like this "
        "rather than to write one large proposal that has to be accepted whole."))
    w("")
    w("### What recurs")
    w("")
    w(C("C-SS-T-RECUR", "**Do not mistake the hardware for the programme.** Hardware is bought "
        "once, and saying that it is the cost is how these schemes die:"))
    w("")
    w("- " + C("C-SS-T-RC-SERV", "**Servicing.** A sensor that nobody visits produces confident "
               "wrong numbers, which is worse than no sensor."))
    w("- " + C("C-SS-T-RC-LAB", "**Laboratory.** The tier-two bottles are paid for one "
               "analysis at a time, and are the only line that cannot be economised without "
               "losing the attribution."))
    w("- " + C("C-SS-T-RC-CUST", "**Custody.** Somebody has to keep the archive, the "
               "calibration histories and the pre-registration for as long as the series runs, "
               "and that is a job rather than a server."))
    w("")
    w(C("C-SS-T-RC-SO", "So: **a purchase to find out, and salaries to keep knowing.** The "
        "recurring part is the one a proposal has to be honest about, because it is the one "
        "that gets cut and takes the series with it."))
    w("")
    w("### And the whole of it?")
    w("")
    w(C("C-SS-T-FIELD", "This page designs the answer to one question. The obvious next one is "
        "what it would take to settle the *field* — not the faecal channel alone, but enough of "
        f"the {v['designs']} designs in [EXPERIMENTS.md](EXPERIMENTS.md) to put measurements "
        "where the argument now has models. The blocks, without prices:"))
    w("")
    w("- " + C("C-SS-T-B-THIS", "**This experiment**: whether the payload reaches the water, "
               "and whose it is."))
    w("- " + C("C-SS-T-B-NET", "**The standing stream network** in [SENSING.md](SENSING.md): "
               "the same question everywhere, permanently, with no extrapolation."))
    w("- " + C("C-SS-T-B-CSO", f"**Instrumenting the {v['cso_n']} largest overflow "
               "structures**: flow rather than event counts, at the structures that hold "
               f"{v['cso_share']}% of the volume reported by the {v['cso_with']} that report "
               "one."))
    w("- " + C("C-SS-T-B-MARINE", "**The marine tier** — `X14`, `X15`, `X16`: oxygen and "
               "temperature at many points in one water body, to test whether one station can "
               "stand for it."))
    w("- " + C("C-SS-T-B-MISSING", "**The missing instruments** — `X19`, `X20`: a panel for the "
               "outcomes no source this project profiled measures, and a record of dated events "
               "from the people with the longest baseline, for damage that has no instrument "
               "behind it."))
    w("- " + C("C-SS-T-B-DESK", "**The desk work** — `X8`, `X21`, `X22`: analyses of data that "
               "already exists."))
    w("- " + C("C-SS-T-B-TRIALS", "**A trials portfolio** — the meta-solution in "
               "[PROGRAMME.md](PROGRAMME.md): whether the interventions work, in named places, "
               "reversibly."))
    w("")
    w(C("C-SS-T-CAPITAL", "Each block is hardware bought once and a bill for service, sampling "
        "and custody that recurs, and the recurring part is the one that decides whether any of "
        "it survives to be a time series."))
    w("")
    w("**And what money cannot do.**")
    w("")
    w("- " + C("C-SS-T-L-SHIP", "**Ship time is not in it.** The autumn benthic extension and "
               "anything offshore needs a vessel and an institution, and this page provides "
               "neither."))
    w("- " + C("C-SS-T-UNSCOREABLE", f"**Some of it cannot be bought at all.** "
               f"{v['unscoreable']} of the {v['mechanisms']} mechanisms in the register cannot "
               "be tested with any source this project surveyed, because the deciding "
               "measurement is in none of them; money buys the instrument, not the record it "
               "should have been collecting."))
    w("- " + C("C-SS-T-DESK", f"**And one block needs no fieldwork.** {v['desk']} designs are "
               "desk analyses of data that already exists. If the argument is that this is all "
               "too expensive, that block is the counter-example sitting in the open."))
    w("")
    w("---")
    w("")
    w("## 7. Who could do which part")
    w("")
    w("- " + C("C-SS-T-W-ONE", "**One person with a culvert and a soldering iron**: a node, a "
               "year of a real series from one stream, and the demonstration that it works."))
    w("- " + C("C-SS-T-W-ASSOC", "**A local association or a school**: a pair — one "
               "high-density catchment and its match — which is a whole experiment in "
               "miniature."))
    w("- " + C("C-SS-T-W-MUNI", "**A municipality or a water utility**: the samplers and the "
               "laboratory line, which is the half that needs an institution."))
    w("- " + C("C-SS-T-W-UNI", "**A university group**: the end-member sampling and the "
               "isotope work, and the pre-registration that makes the rest admissible."))
    w("- " + C("C-SS-T-W-ANY", "**Anyone at all**: hold the pre-registration to its "
               "publication rule when the result is inconvenient."))
    w("")
    w(C("C-SS-T-PERMISSION", "The stream measurements need a landowner's permission at each "
        "culvert, and the end-member samples need the farms and plants that hold them to "
        "agree."))
    w("")
    w("---")
    w("")
    w("## 8. What it settles, and what it does not")
    w("")
    w(C("C-SS-T-SETTLES", "**Settles.** Whether the payload reaches the water, in what "
        "quantity, in what season, under what conditions, and whose it is — measured rather "
        "than modelled, at the point where inland water becomes coastal water. Whether the "
        "spreading calendar is visible in a stream. Whether the account's single channel is "
        "missing a second one, and by roughly how much."))
    w("")
    w(C("C-SS-T-NOTSETTLE", "**Does not settle.** What the arriving material then does in the "
        "sea: that is the next experiment and it is harder. Nor anything about constituents "
        "outside the analysed list. Nor the marine oxygen question, which has [its own "
        "designs](EXPERIMENTS.md)."))
    w("")
    w("> " + C("C-SS-T-WHYEND", "**Why it would end the argument rather than extend it.** The "
               "disputed agricultural share is a modelled residual. This produces a measured "
               "quantity, at named places, on dates, with the raw series published and the "
               "decision rule fixed in advance — so the result is available to somebody who "
               "does not trust either party. **That is the kind of number that can end a "
               "disagreement.**"))
    return "\n".join(o).rstrip("\n") + "\n"


def main():
    try:
        write_doc(os.path.join(ROOT, PAGE), render(values()))
    except (live.Unjustified, _claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote {PAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
