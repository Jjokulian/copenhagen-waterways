#!/usr/bin/env python3
"""docs/OPEN_PROBLEMS.md - what this project could not settle, why, and what would.

Every number on the page comes through live.py, and every assertion is a checked
claim (LIVE_NUMBERS.md section 11): registered in data/manual/claims.d/w2-op.json
with what it rests on, and confirmed against the words it is said in here. What
the page used to say and could not justify is in docs/ARCHIVE.md, not here - the
page does not narrate its own history.

    python3 scripts/pages/open_problems.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import DERIVED, MANUAL, ROOT, log, write_doc
import live

OUT = os.path.join(ROOT, "docs", "OPEN_PROBLEMS.md")
SUN_ORDER = ["night", "twilight", "0-10", "10-20", "20-30", "30-40", "40+"]
UP = ["0-10", "10-20", "20-30", "30-40", "40+"]


def J(*p):
    return live.live_json(os.path.join(*p))


def main():
    meta, mon = J(DERIVED, "meta_facts.json"), J(MANUAL, "monitoring.json")
    fa, fg, rm = J(DERIVED, "floodalign.json"), J(DERIVED, "floodgap.json"), J(DERIVED, "rivermap.json")
    of, cy, rs = J(DERIVED, "outfalls.json"), J(DERIVED, "cycles.json"), J(DERIVED, "rescore.json")
    en, cc = J(DERIVED, "enums.json"), J(DERIVED, "clock_convention.json")
    ct = J(DERIVED, "currents_transport.json")
    ref = live.ref
    C, B, E = live.claim, live.claim_begin, live.CLAIM_END

    import claims as _claims
    cd, cache = _claims.load()[0], {}

    def read(ph):
        return _claims.resolve(cd, ph, cache)[0]

    o = []

    def w(s=""):
        o.append(s)

    w("# Open problems")
    w()
    w(C("C-OP-INTRO", "What this project could not settle, why, and what would settle it. Generated "
        "by `scripts/pages/open_problems.py`: every number is read from the data it describes, and "
        "every assertion is a checked claim."))
    w()
    w(C("C-OP-ORDER", "Ordered roughly by how much the answer would change the picture."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 1
    first, last = str(ct["period"][0])[:4], str(ct["period"][1])[:4]
    w("## 1. The convergence in Køge Bugt")
    w()
    w(B("C-OP-1-OPEN") + "**The question.** Whether wind-driven southward surface transport meets the")
    w("northward Baltic outflow, so that Køge Bugt collects fine sediment and floating material")
    w("mobilised elsewhere and not only its own discharge, is not established." + E)
    w()
    w(B("C-OP-1-MATTERS") + "**Why it matters.** Everything computed in [SEABED.md](SEABED.md) is")
    w("resuspension from local wind. If a large share of the bay's sediment and its contaminant load")
    w("arrives from outside, local interventions cannot fix it, and the catchment that matters is far")
    w("larger than the one draining into the bay." + E)
    w()
    w(B("C-OP-1-SETTLE") + "**What would settle it.** A particle-tracking run on a current field,")
    w("together with the wind record already held, would show directly whether Køge Bugt collects")
    w(f"material and where it comes from. The hourly current field this project holds covers {first}")
    w(f"to {last} only; Copernicus Marine's Baltic physics reanalysis reaches back to the early")
    w("nineties, daily, behind a free account." + E)
    w()
    w(B("C-OP-1-PROVENANCE") + "**Second-best.** Sediment provenance. An accumulation zone shows fine")
    w("grain size, high organic content and elevated metals relative to its surroundings; fingerprinting")
    w("could tell locally derived from imported material. It needs sediment samples." + E)
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 2
    lt = mon["load_trend_vs_outcome"]
    nl, obs = lt["nitrogen_load"], list(lt["iltsvind_extent"]["observations"])
    year = {int(x["year"]): x for x in obs}
    a23, a24 = year[2023]["km2_september"], year[2024]["km2_september"]
    a25 = year[2025]["km2_late_september"]
    w("## 2. Why the extremes did not respond to a halved load")
    w()
    w(B("C-OP-2-LOAD") + f"Land-based nitrogen supply is down about {nl['reduction_pct_since_1990']}% since")
    w(f"1990 as DCE reports it, flow-normalised: from about {nl['approx_1990_kt']} to about")
    w(f"{nl['approx_recent_kt']} kt a year." + E + " " + B("C-OP-2-EXTENT") + "September oxygen-depletion")
    w(f"extent was {a23:,} km² in 2023 and {a24:,} km² in 2024 - by DCE's note on 2024 nearly half as")
    w("large again as 2023, and the second largest registered, exceeded only by 2002. By late")
    w(f"September 2025 it was {a25 / a24 * 100:.0f}% of 2024's area." + E)
    w()
    w(C("C-OP-2-NOTREND", "So the extremes have not fallen with a halved load, and the swing from one "
        "year to the next is large. No source this project holds explains either."))
    w()
    w(B("C-OP-2-CANDIDATES") + "Three candidates - legacy lag, warming, loss of assimilative state - are")
    w("laid out in [CAUSATION.md](CAUSATION.md). Lag fails on elapsed time: the lags the monitoring")
    w("register gives for the LOOP catchments are shorter than the time since 1990. The other two have")
    w("no term in a source apportionment, because neither is a source." + E)
    w()
    w(B("C-OP-2-MATTERS") + "**Why it matters.** The load series set against the outcome series is a")
    w("direct empirical test of the nitrogen-dominant model, and it has been running since 1990. If load")
    w("is not the dominant control on the extremes, the apportionment answers a question about")
    w("attribution while the policy asks one about outcomes." + E)
    w()
    w(B("C-OP-2-SETTLE") + "**What would settle it.** A regression of annual oxygen-depletion extent on")
    w("flow-normalised load, wind work over the stratified season and bottom-water temperature anomaly,")
    w("with an interaction term for state. Load and extent are published by DCE; wind work and bottom")
    w("temperature can be computed from the wind and CTD records this project holds. No new")
    w("instruments. This project found no published regression of that form." + E)
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 3
    w("## 3. Whether \"ikke registreret\" means measured or unmeasured")
    w()
    w(C("C-OP-3-DCE", "DCE's oxygen notes register no oxygen depletion in Køge Bugt, including in "
        "2023, the largest extent since 2002.") + " " + C("C-OP-3-AMBIG", "The bay may be too shallow "
        "to stratify long enough to qualify, but *\"we measured and found nothing\"* and *\"it is not in "
        "the survey\"* produce the identical line in a report."))
    w()
    w(C("C-OP-3-SETTLE", "**What would settle it.** The station list behind the oxygen-depletion "
        "mapping: whether there are monitoring positions inside Køge Bugt at all."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 4
    w("## 4. The potency term")
    w()
    w(C("C-OP-4-POTENCY", "The nitrogen accounts this project has examined weigh every kilogram alike: "
        "a kilogram delivered in February into a mixed column counts the same as one delivered in July "
        "into a stratified fjord."))
    w()
    w(C("C-OP-4-ODP", "An Oxygen Depletion Potential would need, per source and season: the fraction "
        "assimilated, the fraction exported below the pycnocline, and the fraction remineralised where "
        "the water is not ventilated. Each is a fraction. None is computed in any source this project "
        "holds."))
    w()
    w(C("C-OP-4-SETTLE", "**What would settle it.** Not a dataset - a modelling programme. But even a "
        "crude seasonal weighting, applied to existing load figures, would say more than the equal "
        "weight every kilogram implicitly carries now."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 5
    lv = mon["overflow_reporting"]["knowledge_levels"][-1]
    w("## 5. Event-based measurement of overflow")
    w()
    w(C("C-OP-5-METHOD", "The reporting method is modelled annual volume times a fixed concentration, "
        "checked against that same concentration, with no flow rate recorded.") + " "
      + C("C-OP-5-THRESHOLD", "Sediment resuspension in a basin is a *threshold* in flow, so the mass is "
          "plausibly dominated by a handful of events the method averages away."))
    w()
    w(B("C-OP-5-SETTLE") + "**What would settle it.** Flow-proportional sampling at a handful of structures")
    w(f"across a range of event sizes - videnniveau {lv['level']} in Miljøstyrelsen's own scheme,")
    w(f"{lv['uncertainty_pct']}% uncertainty, and the highest level in their hierarchy. How many structures")
    w("are measured this way is not in anything this project holds." + E)
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 6
    w("## 6. The unquantified nitrogen pathways")
    w()
    w(C("C-OP-6-COUNT", f"Of the {meta['pathways_total']} enumerated pathways, "
        f"{meta['pathways_unquantified']} carry no number.") + " Two could be measured:")
    w()
    w(C("C-OP-6-A6", f"- **Submarine groundwater discharge** ({ref('A6')}) - measurable with radon and "
        "radium tracers or seepage meters, and not a term in the Danish marine budget."))
    w(C("C-OP-6-A7", f"- **Regeneration from the sediment** ({ref('A7')}) - measurable with benthic flux "
        "chambers; no Danish nutrient budget this project holds includes it."))
    w()
    w(C("C-OP-6-DENOM", "Until they are measured, a percentage in an apportionment is a share of the "
        "quantified pathways, not of the supply."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 7
    w("## 7. The autumn die-off")
    w()
    w(C("C-OP-7-WINDOW", "Soft-bottom fauna is sampled from the start of March to the end of May.")
      + " " + C("C-OP-7-AFTERMATH", "The mortality is observed only in its aftermath, once "
                "recolonisation has begun, so the depth of the kill - and any ratchet by which each "
                "year's hypoxia removes more of the structural life - is not measured."))
    w()
    w(C("C-OP-7-SETTLE", "**What would settle it.** Autumn sampling at a subset of existing stations. "
        "The stations exist; only the timing would change."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 8
    w("## 8. Fedtemøg as a condition")
    w()
    w(C("C-OP-8-NONE", "No series of the shore condition - not extent, not biomass, not duration, not "
        "odour - was found in any source this project surveyed. What exists is bathing-water sampling in "
        "the bathing season."))
    w()
    w(C("C-OP-8-CIRCULAR", "So every seasonal claim about fedtemøg is circular: a November phenomenon "
        "would leave almost no trace."))
    w()
    w(C("C-OP-8-SETTLE", "**What would settle it.** Fixed-position coastal cameras with a monthly "
        "index, or a structured citizen-reporting scheme running year-round rather than in summer."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 9
    w("## 9. There is no visual record of what high concentrations actually do")
    w()
    w(C("C-OP-9", "The monitoring this project has profiled produces concentrations, not images of "
        "consequence, and the two are not substitutes. **This became its own page: "
        "[EXPOSURE.md](EXPOSURE.md).** No claim in the claims register rests on it."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 10
    w("## 10. Fat, and everything else with no nitrogen in it")
    w()
    w(C("C-OP-10-FAT", f"Taken as tripalmitin, a triglyceride is "
        f"{meta['fat_n_frac_pct']:.0f}% nitrogen and carries {meta['fat_cod_g_per_g']:.1f} g of oxygen "
        f"demand per gram ({ref('R1')}).") + " " + C("C-OP-10-SEWERS", "Sewers accumulate fat, oil and "
                                                    "grease as deposits - fedtpropper."))
    w()
    w(C("C-OP-10-NOFIGURE", "No figure for how much fat leaves the sewer system was found in any source "
        "this project holds.") + " " + C("C-OP-10-UNIT", "The national conversion counts organic matter "
                                         "as COD and `BI5` at fixed concentrations; fat has no determinand "
                                         "of its own in it."))
    w()
    w(C("C-OP-10-SETTLE", "**What would settle it.** Composition sampling of overflow at a handful of "
        "structures across a range of event sizes - the same flow-proportional campaign as item 5, with "
        "fat, oil and grease and total organic carbon added to the determinands."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 11
    w("## 11. Trawling and bed integrity in the receiving bays")
    w()
    w(C("C-OP-11-DEADBED", "A dead bed resuspends several times as often as a living one, as "
        "[SEABED.md](SEABED.md) computes from wind.") + f" {ref('D1')} proposes that bottom trawling "
      "removes the living structure directly. " + C("C-OP-11-UNADDRESSED", "Whether the bays receiving "
                                                   "urban discharge are also trawled is a separate "
                                                   "variable that nothing on this site computes."))
    w()
    w(C("C-OP-11-SETTLE", "**What would settle it.** AIS-derived fishing effort. Global Fishing "
        "Watch's is an open download, with a free token for its API; its public trawler class lumps "
        "bottom and pelagic trawls together, and it sees only vessels that carry AIS."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 12
    w("## 12. Whether toxicant loading, not nutrients, gates recovery")
    w()
    w(C("C-OP-12-LOSS", "Eelgrass was lost at large scale to the wasting disease of the 1930s.") + " "
      + C("C-OP-12-OPEN", "Whether toxicant loading, as well as nutrients, gated its recovery is not "
          f"established; {ref('E15')} would bear on it."))
    w()
    w(C("C-OP-12-MECH", "The mechanism proposed: toxicants remove the grazers and filter feeders that "
        "would otherwise control algal biomass, so the same nutrient load produces a different outcome. "
        "Nitrogen sensitivity would then be a *derived* property of a chemically damaged system."))
    w()
    w(C("C-OP-12-SETTLE", "**What would settle it.** Hard. The Danish question of which factor gated "
        "recovery would need a historical reconstruction of both loadings against the eelgrass record."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 13
    shifts = [v for pair in fa["shifts_m"].values() for v in pair]
    near = {int(m): m for m in fg["params"]["near_m"]}
    cov = fg["coverage"]
    c200, c100 = cov["within_200m_of_any_planned_work"], cov["within_100m_of_any_planned_work"]
    surf = rm["near_surface_conveyance_pct"]
    w("## 13. The flood sheets are placed; their absolute placement is still open")
    w()
    w(B("C-OP-13-PLACED") + "All seven sheets are placed. They are drawn on aerial photographs, so where")
    w("two overlap the pixels depict the same ground: `scripts/floodalign.py` resamples each overlapping")
    w("pair onto a common metric grid, masks out everything drawn and everything flat, reduces both to")
    w("gradient magnitude and correlates them. A bundle adjustment over the")
    w(f"{meta['floodalign_pairs']} usable pairs and the control points leaves pair residuals of")
    w(f"{fa['pair_rms_m']:.0f} m RMS." + E + " " + C("C-OP-13-CONVERGES", "Re-running the alignment after "
                                                       "applying the solution returns residual shifts of "
                                                       f"{min(shifts):+.0f} to {max(shifts):+.0f} m on every "
                                                       "sheet."))
    w()
    w(C("C-OP-13-NORREBRO", "Nørrebro gave no usable pair with any neighbour, and is placed from two "
        "reader-supplied control points; why it would not correlate is unresolved."))
    w()
    w(C("C-OP-13-WATER", "Painted depth that lands on open water - water standing on water - is measured "
        "against open-water polygons that `floodalign.py` never reads, so the bundle adjustment was not "
        "fitted to it."))
    w()
    w(C("C-OP-13-TABLE", "The current flood figures, read from `floodgap.py` and `rivermap.py`:"))
    w()
    w("| | **Now** |")
    w("|---|---:|")
    w(f"| Flood path on land | **{fg['flooded_area_km2']:.2f} km²** |")
    w(f"| Painted over open water | **{fg['flooded_over_water_km2']:.2f} km²** |")
    w(f"| Within {near[200]} m of a planned work | **{c200 * 100:.1f}%** |")
    w(f"| Within {near[100]} m | **{c100 * 100:.1f}%** |")
    w(f"| With a surface route nearby (`NEAR_M` in `rivermap.py`) | **{surf:.1f}%** |")
    w(f"| Corridor candidates | **{rm['corridor_candidates']}** |")
    w()
    if surf >= 52:
        verdict = "a planned surface route beside the flood path is still the majority case"
    elif surf >= 48:
        verdict = "a planned surface route beside the flood path is a coin flip"
    else:
        verdict = "a planned surface route beside the flood path is the minority case"
    w(C("C-OP-13-SURFACE", f"At {surf:.1f}% {verdict}, so an argument should not lean on *most*."))
    w()
    w(C("C-OP-13-ORTHO", "Registering each sheet against georeferenced aerial photographs of its own era "
        "would place all seven absolutely, with no anchors; whether such imagery is openly served was "
        "not checked for this page."))
    w()
    w(C("C-OP-13-OSM", "Matching against a street network does not do it: a dense, uniform mesh carries "
        "almost no positional information, because at any offset some streets line up with some "
        "streets. What carries position is whatever is rare and irregular, such as a coastline."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 14
    w("## 14. The flood model predates a substantial part of the city it is used to plan")
    w()
    w(C("C-OP-14-DATE", "The 2012 sheets model the city of the year their titles name, not the city of "
        "today.") + " " + C("C-OP-14-SINCE", "Copenhagen has built since - Nordhavn, much of Ørestad, "
                            "Sluseholmen and Teglholmen in Sydhavn among them - much of it on reclaimed "
                            "or re-levelled ground."))
    w()
    w(C("C-OP-14-GAP", "How much of today's impervious surface lies outside the seven sheets has not "
        "been computed by any stored script."))
    w()
    w(C("C-OP-14-MATTERS", "**Why it matters in both directions.** Districts built after the model add "
        "runoff it never routed, and they sit on made ground at levels its terrain does not have. Every "
        "figure in [FLOOD_GAP.md](FLOOD_GAP.md) is therefore a statement about the city the model "
        "describes; the plan built on it is being delivered into today's."))
    w()
    w(C("C-OP-14-SETTLE", "**What would settle it.** A re-run of the hydraulic model on current terrain "
        "and current impervious cover. Failing that, the ground outside the sheets can be computed and "
        "flagged rather than silently omitted."))
    w()
    w("### The time dimension, which is the more interesting version")
    w()
    w(C("C-OP-14-SNAPSHOT", "Everything here is a snapshot compared against another snapshot: a model of "
        "an earlier city against a later plan."))
    w(C("C-OP-14-LAYERS", "The materials for a fourth dimension are partly present: "
        "`skp_veje_tunneller_kk` carries an expected in-service year, `forventet_ibrugtagning`, on most "
        "of its features, running from the mid-2010s to the late 2030s; `lar_registreringer` carries "
        "permit and in-use status per installation; the sewer-catchment layer carries *status* and "
        "*plan* side by side."))
    w()
    w(C("C-OP-14-SPINE", "What is missing is the historical spine: when each basin, outfall, tunnel and "
        "reclamation actually entered service over recent decades. With that, the same maps become a "
        "sequence, and the questions worth asking are sequence questions. Did the shoreline's condition "
        "change when a given basin came online? Does overflow frequency track construction, or rainfall, "
        "or neither?"))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 15
    peak = max(list(ct["lag"]), key=lambda x: x["southward_pct"])
    ev = mon["sediment_release_events"]
    ofl, lyn = ev["oresund_fixed_link"], ev["lynetteholm"]
    w("## 15. The transport experiments that were already run, and nobody read")
    w()
    w(B("C-OP-15-LAG") + "[CURRENTS.md](CURRENTS.md) could not establish whether material from the")
    w("Copenhagen side reaches Køge Bugt. The best it managed was a statistical lag - during")
    w(f"overflow-scale rain the Sound runs *north*, and {peak['lag_h']} hours later it runs south, on")
    w(f"{peak['hours']} event-hours of the {first}-{last} record. That is suggestive and thin." + E)
    w()
    w(C("C-OP-15-EVENTS", "The monitoring register records two dated releases of seabed material near "
        "the bay, each with a quantity, a place and dates; it cites no source for them."))
    w()
    w("| | Øresund fixed link | Lynetteholm |")
    w("|---|---|---|")
    w(f"| When | {ofl['period']} | {lyn['period']} |")
    w("| Material | dredged seabed, Drogden and Saltholm | harbour gytje |")
    w(f"| Volume | **{ofl['dredged_m3'] / 1e6:.1f} million m³ dredged** | {lyn['planned_dump_m3'] / 1e6:.0f} million m³ planned to be dumped |")
    w(f"| Released to the water | spill limit **{ofl['spill_limit_pct_of_dredged']}%, up to {ofl['spill_limit_m3']:,} m³** | **{lyn['first_dumped_m3']:,} m³** before it was stopped |")
    w("| Where | the northern entrance to Køge Bugt | Køge Bugt, by permit |")
    w("| Outcome | limit reported met, *nulløsning* judged met | dumping dropped entirely; material built into the peninsula instead |")
    w("| Attention | project's own monitoring programme | national controversy, Swedish objection under the Espoo Convention |")
    w()
    w(B("C-OP-15-ASYM") + "**The asymmetry is the finding.** The permitted spill from the Øresund link -")
    w(f"up to {ofl['spill_limit_m3']:,} m³ of fines put into the water column at the mouth of Køge Bugt")
    w(f"between 1995 and 2000 - is **{ofl['spill_limit_m3'] / lyn['first_dumped_m3']:.0f} times** what")
    w("was dumped at Lynetteholm before the dumping was stopped. The recent, smaller project was halted")
    w("after a political fight. The older, far larger one was a permit condition that was met." + E)
    w()
    w(C("C-OP-15-LOOKED", "This is not an argument that the Øresund link was mishandled; its spill was "
        "reported against a limit and within it, which is more than most of the discharges in this "
        "project can say. It is an argument about **what gets looked at**: a release becomes "
        "controversial when it is called dumping and invisible when it is called spill."))
    w()
    w(C("C-OP-15-SETTLE", "**What would settle it.** Sediment cores from Køge Bugt, dated. Fine "
        "material released at the Drogden end between 1995 and 2000, and again from harbour works since, "
        "should appear as datable horizons if the transport is real, and be absent if it is not. That is "
        "a direct test of item 1, using events that have already happened, and it needs a boat and a lab "
        "rather than a model."))
    w()
    w(C("C-OP-15-WHERE", "Both events are recorded in `data/manual/monitoring.json` under "
        "`sediment_release_events`, without a cited source."))
    w()
    w("---")
    w()
    # ------------------------------------------------------------------- 16
    L = of["layers"]
    n_cso, n_sep = L["combined_overflow"]["n"], L["separate_stormwater"]["n"]
    vol_n = (L["combined_overflow"]["totals"]["Vand_(m3/ aar)"]["n"]
             + L["separate_stormwater"]["totals"]["Vand_(m3/ aar)"]["n"])
    n98 = read("{read:OP-WIKI-KOMMUNER:98|bestyrelserne i de 98 kommuner}")
    w("## 16. The drainage reconstruction exists for one city, and cannot currently be repeated")
    w()
    w(C("C-OP-16-ONECITY", "Item 14 is about the Copenhagen model. This is the larger version of the "
        "same problem: this project has such a reconstruction for Copenhagen only, and it exists there "
        f"because {meta['floodmap_pdfs']} PDFs were published and their georeferencing could be "
        "recovered. That is not a method. It is lucky archaeology."))
    w()
    w(C("C-OP-16-ENDPOINTS", "Everywhere else the view has **endpoints without a network**. The national "
        f"outfall extract holds {n_cso:,} combined-sewer overflow structures and {n_sep:,} separate "
        "stormwater outfalls, each with a position and a *reduced impervious area* behind it, and "
        f"{vol_n:,} of them with an annual volume.") + " "
      + C("C-OP-16-NOTAPS", "What it does not hold is which ground drains to which outfall, and no "
          f"national map of that was found: {n_cso + n_sep:,} catalogued spouts and no map of the taps."))
    w()
    w(C("C-OP-16-BLOCKS", f"**Why this blocks specific work.** {ref('B1')} and {ref('B2')} in the register "
        "both need what drains to an outfall, and none of it can be assembled from a point. The same gap "
        "stops any attempt to attribute a receiving water's condition to the ground behind it, which is "
        "the whole premise of a catchment-based directive."))
    w()
    w(C("C-OP-16-LER", "**What is closed.** Denmark's utility register, Ledningsejerregistret, holds "
        "pipe geometry and is not open data. This project does not query it and no argument here depends "
        "on it. It is recorded because it is why the gap looks strange: the data exists and is kept "
        "under law, and it is unavailable. The absence is administrative, not physical."))
    w()
    w("### What is open, and has not been tried here")
    w()
    w(C("C-OP-16-PLANS", f"- **Municipal wastewater plans.** Each of Denmark's {n98} municipalities adopts "
        "a *spildevandsplan* with the catchments it serves. Copenhagen's is in `data/raw/plan_html/`; this "
        "project found no national assembly of the rest."))
    w(C("C-OP-16-BBR", "- **The BBR building register**, which carries a construction year per building, "
        "would make impervious change since any date computable nationally rather than by hand, without "
        "a hydraulic model."))
    w(C("C-OP-16-TERRAIN", "- **Terrain.** Where sewers were laid in buried watercourses, surface flow "
        "accumulation over a terrain model is a prior on where the pipes run, not merely a separate "
        "question."))
    w(C("C-OP-16-MAPS", "- **Historic maps**, for the same reason: culverted streams are candidates for "
        "where the sewers are."))
    w()
    w("### The method that might work, stated so it can be attacked")
    w()
    w(C("C-OP-16-METHOD", "Delineate catchments from terrain, then **constrain the delineation so each "
        "outfall's computed impervious area matches the reduced area already reported for it**. The "
        "reported figure stops being an input and becomes the validation: a delineation that reproduces "
        f"{n_cso + n_sep:,} reported areas is doing something right, and one that cannot is falsified "
        "cheaply."))
    w()
    w(C("C-OP-16-INVERT", "That inverts the usual dependency. It needs no pipe geometry, only endpoints "
        "with sizes, terrain and building footprints, all of which are open. It would produce a "
        "*plausible* network rather than the real one, and the difference must be stated wherever it is "
        "used; but a plausible catchment with a stated error is worth more than no catchment at all."))
    w()
    w("### And the same principle for the rest of the 4D view")
    w()
    w(C("C-OP-16-BASIS", "The view should show the **basis** rather than the output. For every area and "
        "every year: what was actually measured, by whom, how often, and which of the modelled quantities "
        "rest on it. A map of model outputs is a map of somebody's confidence. A map of what was measured "
        "is a map of what is known, and the two differ most exactly where it matters."))
    w()
    w(C("C-OP-16-AREAS", "[AREAS.md](AREAS.md) counts that gap: for every water body, how many stations "
        "have data in two, five and ten or more distinct years - an absence reported as a count over a "
        "named corpus, not as a share of the sea."))
    w()
    # ------------------------------------------------------------------- 17
    rows, filled = en["kemi"]["rows"], en["kemi"]["nonblank"]["Startklok"]
    cls = cc["classes"]
    eras = list(cls.keys())
    visits = sum(cls[e][c] for e in eras for c in cls[e].keys())
    defaults = sum(cls[e]["default"] for e in eras if "default" in cls[e])
    mixed = sum(cls[e]["ambiguous"] for e in eras if "ambiguous" in cls[e])
    w9, s9, w13 = meta["sun_winter_0900"], meta["sun_summer_0900"], meta["sun_winter_1300"]
    windows = list(cy["windows_days"])
    sat = cy["results"]["sat"]["by_window"]
    o2 = cy["results"]["o2"]["by_window"]

    def dev(block, win, axis, b):
        x = block[str(int(win))][axis]
        return x[b]["dev"] if b in x else None
    w("## 17. The archive can see the day, and hardly ever visits the part that matters")
    w()
    w(B("C-OP-17-CLOCK") + "The water-chemistry extract carries a clock value on every genuine row - the")
    w(f"{rows - filled} of {rows:,} rows without one are fragments of a broken note field, not samples.")
    w("But a clock value is not always a time. `scripts/clockzone.py` tests every supplier and era at the")
    w(f"summer-time changes: of {visits:,} sampling visits, {defaults:,} carry a filled-in default rather")
    w(f"than a time, and {mixed:,} come from suppliers whose clock convention is mixed. Only the rest can")
    w("be placed against the sun." + E + " " + C("C-OP-17-CLOCKPY", "Every analysis that places a "
                                                   "water-chemistry sample in time reads the instant "
                                                   "through `scripts/clock.py`, which returns one UTC "
                                                   "instant or says why there is none."))
    w()
    w(B("C-OP-17-SUN") + f"A clock hour is not a light level at {meta['sun_reference_lat']:.1f}°N, so the")
    w("sun's elevation is computed per sample from its own position and instant (`scripts/daylight.py`,")
    w("the NOAA series). The difference is the whole point: **09:00 on the winter solstice is a sun")
    w(f"{w9:.1f}° above the horizon; 09:00 on the summer solstice is {s9:.1f}°.** At 13:00 in midwinter")
    w(f"the sun reaches {w13:.1f}° - {w13 / s9 * 100:.0f}% of the summer's 09:00 height." + E)
    w()
    w(B("C-OP-17-WINDOW") + "Oxygen concentration pooled over the year mixes the sun with the season: high")
    w("sun comes with summer and warm water, which holds less oxygen. Held inside a moving window at each")
    w("station - a continuous seasonal control, not calendar months, because a month is a step function")
    w("laid over a process with no steps - oxygen **saturation**, which divides out the solubility,")
    w("deviates from the station's own local mean like this (percentage points, by sun elevation bin and")
    w("window width):" + E)
    w()
    w("| sun elevation | " + " | ".join(f"±{x} days" for x in windows) + " |")
    w("|---|" + "---:|" * len(windows))
    for b in SUN_ORDER:
        cells = []
        for x in windows:
            v = dev(sat, x, "sun", b)
            cells.append("—" if v is None else f"{v:+.2f}")
        w(f"| `{b}` | " + " | ".join(cells) + " |")
    w()
    top = [dev(sat, x, "sun", "40+") for x in windows]
    tops = [t for t in top if t is not None]
    mono = all(all(dev(sat, x, "sun", a) is not None and dev(sat, x, "sun", c) is not None
                   and dev(sat, x, "sun", a) <= dev(sat, x, "sun", c) for a, c in zip(UP, UP[1:]))
               for x in windows)
    conc10 = max(abs(dev(o2, windows[0], "sun", b)) for b in SUN_ORDER if dev(o2, windows[0], "sun", b) is not None)
    conc_w = max(abs(dev(o2, windows[-1], "sun", b)) for b in SUN_ORDER if dev(o2, windows[-1], "sun", b) is not None)
    if tops and all(t > 0 for t in tops):
        hi = (f"The high-sun bin sits {min(tops):+.2f} to {max(tops):+.2f} percentage points above the "
              "station's local mean at every window width.")
    else:
        hi = "The high-sun bin does not sit above the station's local mean at every window width."
    lo = ("Below it the rise is monotone at every window width." if mono else
          "Below it the pattern is not monotone, and it shifts with the window width.")
    w(C("C-OP-17-HIGHSUN", hi + " " + lo) + " " + C("C-OP-17-CONC", "Oxygen **concentration** stays within "
                                                    f"±{conc10:.3f} mg/l of the local mean at the tightest "
                                                    f"window and within ±{conc_w:.3f} mg/l at the widest, "
                                                    "where more of the season leaks into the comparison."))
    w()
    sc = cy["results"]["o2"]["sun_counts"]
    recent = cc["observed_check"]["2002-"]
    w(B("C-OP-17-PREDAWN") + "**And it does not matter, for the reason that makes this an open problem.**")
    w(f"Of the {cy['results']['o2']['n']:,} surface oxygen samples with an observed time, {sc['night']:,}")
    w(f"were taken at night and {sc['twilight']:,} in twilight. In the record since 2002 the 5th and 95th")
    w(f"percentiles of observed sampling times are {recent['local_hour_p05']:.1f} h and")
    w(f"{recent['local_hour_p95']:.1f} h local time, and {recent['sun_below_horizon_pct']:.1f}% of those")
    w("visits were made with the sun below the horizon. The pre-dawn minimum - the value an oxygen")
    w("threshold is actually *about* - is essentially never visited." + E)
    w(C("C-OP-17-UNCONSTRAINED", "So the dimension is recorded, the water swings little inside the hours "
        "that are sampled, and nothing in the archive constrains the hours that decide whether a threshold "
        "was crossed. **This is not a missing column. It reflects when sampling is done, and no reanalysis "
        "can supply observations that were never taken.** Closing it needs moored sensors, or one season "
        "of deliberate pre-dawn sampling."))
    w()
    moon = [abs(dev(o2, x, "moon", b)) for x in windows for b in ("down", "up dark", "up half", "up bright")
            if dev(o2, x, "moon", b) is not None]
    flips = any(len({(dev(sat, x, "moon", b) or 0) > 0 for x in windows}) > 1
                for b in ("down", "up dark", "up half", "up bright"))
    neap = [dev(o2, x, "tide", "neap") for x in windows]
    neap_top = all(dev(o2, x, "tide", "neap") > max(dev(o2, x, "tide", "spring"), dev(o2, x, "tide", "mid"))
                   for x in windows)
    m_lo = read("{read:OP-WIKI-LUX:0.05|0.05–0.3 Full moon on a clear night}")
    m_hi = read("{read:OP-WIKI-LUX:0.3|0.05–0.3 Full moon on a clear night}")
    s_lo = read("{read:OP-WIKI-LUX:32,000|32,000–100,000 Direct sunlight}")
    s_hi = read("{read:OP-WIKI-LUX:100,000|32,000–100,000 Direct sunlight}")
    w(C("C-OP-17-MOON", "Two cycles were tested alongside the sun. **The moon does nothing detectable** - "
        f"every oxygen term stays within ±{max(moon):.3f} mg/l across the window widths"
        + (", and the saturation terms flip sign between window widths. " if flips else ". ")
        + f"That is the expected answer: a full moon on a clear night gives {m_lo}-{m_hi} lux against "
        f"{s_lo}-{s_hi} for direct sunlight, less than a hundred-thousandth, and cannot drive "
        "photosynthesis at any level these instruments resolve."))
    if neap_top:
        tide = ("**The spring-neap cycle is suggestive and no more**: neap comes out highest in oxygen at "
                "every window width (" + ", ".join(f"{v:+.3f}" for v in neap)
                + " mg/l), a consistent sign on a tiny effect.")
    else:
        tide = ("**The spring-neap cycle is suggestive and no more**: neap does not come out highest at "
                "every window width (" + ", ".join(f"{v:+.3f}" for v in neap) + " mg/l).")
    w(C("C-OP-17-TIDE", tide + " Lunar phase is *forcing*, not water level, and inferring height from "
        "phase would be a model of the moon presented as a measurement of the sea. DMI's open sea-level "
        "series, oceanObs, would settle it."))
    w()
    # ------------------------------------------------------------------- 18
    mx = rs["matrix"]
    hyps = list(mx.keys())
    testable = [h for h in hyps if mx[h]["class"] == "testable now"]
    partly = "partly unblocked - a second blocker was behind the first"
    k1 = rs["tests"]["K1_si_din_molar_surface"]
    dip = rs["tests"]["A7_bottom_dip_by_month"]
    e11 = rs["tests"]["E11_unionised_nh3_ug_l"]
    ss = mx["B4"]["fetch_supplied"]["ss"]
    total = sum(rs["tally"][k] for k in rs["tally"].keys())
    w(f"## 18. The vandkemi fetch: {rs['tally']['testable now']} of {total} hypotheses testable")
    w()
    w(C("C-OP-18-SET", "`scripts/rescore.py` takes the hypotheses listed as waiting on the ODA "
        "`vandkemi` fetch - " + ", ".join(ref(h) for h in hyps[:-1]) + f" and {ref(hyps[-1])} - and "
        "checks, per hypothesis, which of the variables its consequence needs are now in hand:"))
    w()
    w("| | |")
    w("|---|---|")
    w(f"| **testable now** | {rs['tally']['testable now']} — " + ", ".join(ref(h) for h in testable) + " |")
    w(f"| **partly unblocked; a second blocker was behind the first** | **{rs['tally'][partly]}** |")
    w()
    w(C("C-OP-18-LOCKS", f"**A blocker can hide a blocker.** {ref('A1')} and {ref('A2')} need river load, "
        "which lives on a different ODA endpoint that `fetch_oda.py` cannot currently reach: its `run()` "
        f"opens the Hav topic only. {ref('A7')}'s *without a matching river input* clause needs the same. "
        f"{ref('K1')} needs phytoplankton counts and {ref('K2')} a species assemblage, neither held. "
        f"{ref('E11')} needs temperature and salinity in the same bottle. {ref('B4')} needs *stream* "
        "stations, and this is the marine topic, so riverine particulate carbon was never going to be in "
        f"it: its {ss['n']:,} suspended-solids rows stop in {str(ss['years'])[-4:]} and sit at "
        f"{ss['stations']} stations.") + " " + C("C-OP-18-TRIAGE", "**That generalises: a triage counts "
                                                 "the blocker someone wrote down, not the number of locks "
                                                 "on the door.**"))
    w()
    w("Of what *is* now answerable, two results and one capability:")
    w()
    w(C("C-OP-18-K1", f"**The first look at {ref('K1')}'s driver does not test its premise.** {ref('K1')} "
        "predicts Si:DIN falls, so diatoms lose to flagellates. The pooled surface yearly median was "
        f"{k1['1985']['median']:.2f} in 1985, with {k1['1985']['share_below_1'] * 100:.0f}% of samples "
        f"below the silicon-limitation ratio of one, against {k1['2025']['median']:.2f} in 2025 with "
        f"{k1['2025']['share_below_1'] * 100:.0f}% below it. But the years between swing widely - the "
        f"median was {k1['1994']['median']:.2f} in 1994 - and the median pools every month, mixing the "
        "pre-bloom pool the hypothesis is about with bloom drawdown. Whether that pool moved is a separate "
        "question, and the assemblage half remains unscoreable."))
    w()
    rise = (dip["10"]["median"] / dip["4"]["median"] - 1) * 100
    w(C("C-OP-18-A7", f"**{ref('A7')}'s weak form is supported.** Median ortho-phosphate in bottom water, "
        f"below the depth cut in `rescore.py`, runs from {dip['4']['median']:.1f} µg/l in April to "
        f"**{dip['10']['median']:.1f} µg/l in October**, a {rise:.0f}% rise through the summer into "
        "autumn.") + " " + C("C-OP-18-A7-READ", "That is the pattern release from sediment under "
                             "stratification would give. The strong form, that it happens *without* a "
                             "matching river input, still needs the endpoint the code cannot reach."))
    w()
    w(C("C-OP-18-E11", f"**{ref('E11')} is answerable in principle.** {e11['n_bottles_with_both']:,} "
        "bottles carry both pH and ammonium. The un-ionised fraction, the toxic one, comes out at a median "
        f"of {e11['median']:.3f} µg/l, a 95th percentile of {e11['p95']:.1f} and a maximum of "
        f"{e11['max']:.0f} - indicative only, because the salinity and in-situ temperature corrections to "
        "the dissociation constant are not applied."))
    try:
        write_doc(OUT, "\n".join(o).rstrip("\n") + "\n")
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
