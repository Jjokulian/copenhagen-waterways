#!/usr/bin/env python3
"""The landing page's words, generated like every other page.

The reading map in index.html used to carry its headline figures as JavaScript
string literals, and they went stale. The words now live here and are written
through write_doc() into docs/LANDING.md; index.html fetches that file, splits it at
the `<!-- landing:key -->` markers and places each section where the literal used to
be.

Every number is read live from data or a pinned document, and every assertion is a
checked claim (LIVE_NUMBERS.md section 11), registered in
data/manual/claims.d/w1-lr.json with what it rests on. What the landing once said and
could not justify is in docs/ARCHIVE.md, not here.

    python3 scripts/pages/landing.py

Writes docs/LANDING.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import DERIVED, ROOT, log, write_doc
import claims
import live

OUT = os.path.join(ROOT, "docs", "LANDING.md")
C, B, E = live.claim, live.claim_begin, live.CLAIM_END
# The triage groups counted as physical, by what the register names them: physical
# control of resupply, physical disturbance of the bed, renewal and rate, the
# physical fields. A-LR-PHYSGROUPS states the choice.
PHYSICAL = ("C", "D", "W", "Z")


def main(argv):
    J = lambda *p: live.live_json(os.path.join(*p))
    tri = J(DERIVED, "triage.json")
    sp = J(DERIVED, "station_places.json")["oxy_bed"]
    light = J(DERIVED, "light.json")
    meta = J(DERIVED, "meta_facts.json")
    obs = J(DERIVED, "observing.json")
    areas = J(DERIVED, "areas.json")
    conv = J(DERIVED, "conveyance.json")
    lf = J(DERIVED, "landing_facts.json")
    man = J(ROOT, "docs", "data", "flood2012", "manifest.json")
    ps = J(ROOT, "docs", "data", "areas", "partition_subspace.json")
    nr = J(ROOT, "data", "manual", "nitrogen_readings.json")["pinned"]
    ret = J(DERIVED, "currents_index.json")["retention"]
    fa = J(DERIVED, "floodalign.json")
    geo = J(DERIVED, "floodmaps", "_georef.json")
    cd, _, _ = claims.load()
    cache = {}
    dce4 = claims.resolve(cd, "{read:DCE-STATMOD-2015:4|iltkoncentration er under hhv. 4 mg/L}",
                          cache)[0]

    n_reg = tri["n_register"]
    cls = tri["classes"]
    testable, unscore, experiment = cls["testable"]["n"], cls["unscoreable"]["n"], cls["experiment"]["n"]
    a = tri["groups"]["A"]
    # the page states two things about group A; refuse it if either stops holding
    if a["testable"] != 0:
        raise live.Unjustified("landing: the page says no testable mechanism is a nutrient "
                               "hypothesis, but group A now has a testable one")
    if a["resolution"] or a["experiment"] or a["testable"]:
        raise live.Unjustified("landing: the page says every nutrient hypothesis waits on a "
                               "fetch, is unscoreable or unestablished - no longer true")
    phys = sum(tri["groups"][g]["testable"] for g in PHYSICAL)
    arch = tri["groups"]["I"]["testable"]
    regions = sorted(sp["regions"], key=lambda r: r["share_below_low"], reverse=True)
    times = regions[0]["share_below_low"] / regions[1]["share_below_low"]
    lo = sp["below_low_mg_l"]
    dk_obs = sum(r["observations"] for r in regions)
    dk_below = sum(r["observations"] * r["share_below_low"] for r in regions) / dk_obs * 100
    g = lf["gotland"]
    P = lf["params"]
    kb = ret["koege_bugt"]["flush_days_20km"]
    others = [v["flush_days_20km"] for k, v in ret.items() if k != "koege_bugt"]
    n_sub = sum(r["subsets"] for r in ps["results"])
    lifts = [r["derived_vs_official_lift"] for r in ps["results"]]
    tr = light["trend"]
    nb = geo["norrebro"]

    o = []
    w = o.append
    w("<!-- landing:hero -->")
    w("# " + C("C-LR-L-HERO", f"{n_reg} candidate mechanisms for a dying fjord. {testable} can "
                              "be tested."))
    w("")
    w(B("C-LR-L-TRIAGE") + "This project listed every mechanism it could find that would leave "
      "a Danish coastal water lifeless — nutrients, toxicants, trawling, sediment chemistry, "
      "warming, disease, film on the surface, and the rest — then asked which could be "
      f"tested against data that exists. **{testable} can. {unscore} cannot be tested with any "
      "source this project surveyed, because the deciding measurement is in none of them. "
      f"{experiment} more need an experiment that no surveyed source reports.**" + E)
    w("")
    w(C("C-LR-L-LEFTOVER", "**The farm share of the nitrogen reaching the sea is not measured.** "
      "It is what is left of the land-borne load once point sources and the natural background "
      "are subtracted: a leftover, which takes up every error in the terms subtracted. "
      "[Why that matters](RESIDUAL.md) · [på dansk, til landbruget](LANDBRUG.md)"))
    w("")
    lb = live.live_json(os.path.join(DERIVED, "landbrug.json"))
    w(C("C-LR-L-DENOM", "**And the share has no denominator.** Nitrogen reaches the sea by at least "
      f"{lb['n_pathways']} pathways, and {lb['n_unquantified']} of them carry no number at all. "
      "Without them there is no total, and no share of it can be stated."))
    w("")
    w(C("C-LR-L-ONELINK", "**Nor is nitrogen the whole chain.** It is one of several routes to oxygen "
      "depletion, which is one of many ways a sea bed and its life are lost, and both are among many "
      "causes of fedtemøg - the harms politicians and nature organisations name. "
      "[Link by link](CAUSATION.md)"))
    w("")
    w(C("C-LR-L-FIX", "*Found a mistake? [Report it](https://github.com/Jjokulian/copenhagen-waterways/issues). What this site has "
      "retracted, and why, is in its [archive](ARCHIVE.md).*"))
    w("")
    w("**But the question is not “what killed Danish coastal water”, because that is not "
      f"one thing.** {B('C-LR-L-MENU')}These are not {n_reg} rivals for a single prize: "
      f"where the evidence reaches, different places behave differently.{E} "
      f"{B('C-LR-L-MARIAGER')}Mariager Fjord's catchment cut its diffuse nitrogen by less than "
      "the national fall in field surplus would lead one to expect, as the national stream "
      f"report itself notes.{E} {B('C-LR-L-FLUSH')}The current model this project uses gives "
      f"Køge Bugt a flush time of {kb:.0f} days, against {min(others):.1f} to "
      f"{max(others):.1f} days for the other waters it was run for.{E} "
      f"{B('C-LR-L-BALTIC')}At the Gotland Deep, every oxygen value below {P['depth_m']:g} m "
      f"is under {P['o2_mg_l']:g} mg/l in **{g['months_all_below_pct']:.0f}%** of months, "
      f"while Danish inner waters are below {lo:g} mg/l in **{dk_below:.1f}%** of near-bed "
      f"observations — two different conditions under one word.{E} "
      "[there is no Denmark →](AREAS.md)")
    w("")
    w(f"{B('C-LR-L-NUTRIENTS')}**And none of the {testable} testable mechanisms is a nutrient "
      "hypothesis.** Every entry in that group is waiting on a data fetch, unscoreable, or "
      f"unestablished.{E} {B('C-LR-L-PHYSICS')}Of the testable ones, {phys} are physical — "
      "resupply, disturbance of the bed, renewal, the physical fields — and "
      f"{arch} are the monitoring archive auditing itself.{E} "
      f"{B('C-LR-L-MONITORED')}**So nutrients did not win an argument against the "
      "alternatives. Nutrients are the group that has a monitoring programme, and "
      f"{unscore + experiment} rival mechanisms have never been in a position to "
      f"compete.**{E} [the whole triage →](PLAN.md)")
    w("")
    w(f"{B('C-LR-L-CHECKABLE')}That is not a claim that nutrients are innocent, or that the "
      "policy is wrong. It is a claim about what the evidence can currently bear, and it is "
      "checkable: every figure here is read from published data or documents by scripts in "
      f"this repository, and links to how.{E} {B('C-LR-L-ERRORS')}The errors this project "
      "made itself are kept visible — [listed](KNOWN_AND_UNKNOWN.md), and in the [archive of "
      f"retired claims](ARCHIVE.md) — rather than edited out.{E}")
    w("")
    w("## The specific case: the chain behind the nitrogen figure")
    w("")
    w(B("C-LR-L-CHAIN") + "A field surplus becomes a modelled load, becomes a percentage, "
      "gets allocated to a water body, is judged against a threshold, and shows a trend. "
      "Every link is public and examined here. **Two do not hold, and a third rests on less "
      "than it appears to.**" + E)
    w("")
    w(f"- {B('C-LR-L-FIELD')}**No field is measured.** The *markoverskud* that drives the "
      "model is a balance — nitrogen supplied to the fields minus nitrogen harvested — "
      "computed from registers and statistics, not measured in any field. Change a rule and "
      f"the number moves with no change in any field: in 1999 the nitrogen norm was cut by "
      f"{nr['norm_cut_1999_pct']['value']}%, and the national report publishes 2013 twice, at "
      f"{nr['t34_2013_surplus']['value']} and {nr['t34_2013_ds_surplus']['value']} kg N/ha, "
      f"depending on which register supplied the mineral-fertiliser term.{E} "
      "[the construction, term by term →](NITROGEN.md)")
    w(f"- {B('C-LR-L-CIRCULAR')}**One published figure rests on less than it appears to.** "
      "The national stream report plots the field surplus against the normalised diffuse "
      "nitrogen load and calls the relation very strong and significant; the same report "
      "then notes that not all fjord catchments respond equally quickly, Mariager Fjord "
      "among them. Whether the modelled part of that load is itself computed from the "
      f"surplus is the question [what the sea actually receives](NITROGEN.md) takes up.{E}")
    w(f"- {B('C-LR-L-BOUNDARIES')}**The boundaries carry no measured signal.** Across all "
      f"{n_sub} feature subsets of the station record, the official water bodies agree with "
      "the partitions the data produce no better than random connected regions of the same "
      f"sizes agree with each other — lift {min(lifts):+.3f} to {max(lifts):+.3f} against "
      f"that contiguity-matched null.{E} [how that was tested →](AREAS.md)")
    w("")
    w("Each link above has its working, its null and its limits in [what the sea actually "
      "receives](NITROGEN.md). And for the question that follows — *so where, and what "
      "would actually help?* — [Places, not categories](PLACES.md) takes the coasts one at a "
      "time. " + C("C-LR-L-PLACES", f"In near-bed oxygen, one region is below {lo:g} mg/l "
                                     f"{times:.1f} times as often as the next."))
    w("")

    w("<!-- landing:fact:light-trend -->")
    w(f"{tr['all_casts_m_per_decade']:+.2f} <span>or</span> {tr['stable_stations_m_per_decade']:+.2f}")
    w("")
    ratio = tr["stable_stations_m_per_decade"] / tr["all_casts_m_per_decade"] * 100
    w(C("C-LR-L-LIGHTTREND", "metres per decade: how fast the depth useful light reaches is "
        "changing, over all casts, or only at the stations measured at both ends of the "
        f"record. Keeping only those shrinks the trend to {ratio:.0f}% of the all-cast "
        f"figure, and rests on {tr['n_stable_stations']} stations."))
    w("")
    w("<!-- landing:fact:light-depth -->")
    sd = light["start_depth"]
    w(f"{sd['z11_shallow_start']:.2f} <span>or</span> {sd['z11_deep_start']:.2f} m")
    w("")
    w(C("C-LR-L-LIGHTDEPTH", "How deep useful light reaches, as a median over the casts that "
        "began near the surface and over those that began deeper: the two differ by "
        f"{meta['light_start_depth_diff_pct']:.0f}%."))
    w("")
    w("<!-- landing:fact:partition -->")
    v = obs["variance"]
    w(f"{v['share_between_wb'] * 100:.1f}% <span>vs</span> "
      f"{v['share_between_st'] * 100:.1f}%")
    w("")
    w(C("C-LR-L-PARTITION", "Of the variation in bathing-water samples, the first share lies "
        "between water bodies and the second between beaches inside one water body. A water "
        "body explains less of it than the beaches within one differ from each other, so the "
        "unit the assessment is built on is not holding together."))
    w("")

    w("<!-- landing:word:iltsvind -->")
    w(C("C-LR-L-ILTSVIND", f"oxygen below {dce4} mg/l **in the bottom water**"))
    w("")

    w("<!-- landing:tool:areas -->")
    w(C("C-LR-L-AREAS", f"All {areas['summary']['sets']['all']['n']} marine water bodies "
        "coloured by how much is actually known about each, with the years every stream of "
        "observation covers. The red line is 2012, the end of the period DCE fitted their "
        "models on."))
    w("")
    s3 = lf["section3d"]
    w("<!-- landing:tool:section3d -->")
    w(C("C-LR-L-SECTION3D", "The street arrangement in three dimensions at its real sizes: the "
        "bored rain line, the sewer left where it is, the two-storey shaft and the pan that "
        f"serves both. {s3['stated']} of its {s3['total']} dimensions are stated conventions "
        "rather than measurements, marked as such and all adjustable, and the hydraulic "
        "panel shows whether a pipe that carries the flow is still fast enough to carry its "
        "own grit."))
    w("")
    w("<!-- landing:tool:baltic -->")
    w(C("C-LR-L-BALTIC-TOOL", "Oxygen at the Gotland Deep in the central Baltic, on a "
        "one-metre depth grid interpolated between discrete samples. In "
        f"{g['months_all_below_pct']:.0f}% of the months of a {g['span_years']:.0f}-year "
        f"record, every value below {P['depth_m']:g} m is under {P['o2_mg_l']:g} mg/l, against "
        f"{dk_below:.1f}% of Danish near-bed observations. Two things are being called by one "
        "word."))
    w("")
    w("<!-- landing:tool:rivers3d -->")
    w(C("C-LR-L-RIVERS", f"The proposal on the real city: {conv['surface_km']:.1f} km of "
        f"surface conveyance plus {conv['mix_km']:.1f} km of mixed alignment — "
        f"{conv['surface_plus_mix_km']:.1f} km that could carry a river — the interceptor "
        "retrofit where they cannot, and where the water ends up."))
    w("")
    w("<!-- landing:tool:viz -->")
    w(C("C-LR-L-VIZ", "Sewer catchments, cloudburst basins and tunnels, discharge points and "
        "the recovered flood overlays, every feature clickable to its own record: every "
        "stream in one spatial view, for one city, on a 2012 reconstruction.") +
      " What it would take to have this for the rest of the country is [an open "
      "problem](OPEN_PROBLEMS.md).")
    w("")
    w("<!-- landing:tool:viz:note -->")
    w(f"{lf['viz_mb']:.1f} MB · desktop · Copenhagen only")
    w("")
    w("<!-- landing:tool:flood2012 -->")
    w(C("C-LR-L-FLOOD2012", f"All {man['n_sheets']} 2012 cloudburst sheets as georeferenced "
        "rasters — PNG, world file and .prj — so they open straight in QGIS, with the "
        "coordinates put back."))
    w("")
    w("<!-- landing:tool:flood2012:note -->")
    w(f"{lf['flood2012_mb']:.1f} MB · EPSG:4326")
    w("")
    w("<!-- landing:tool:georef -->")
    w(C("C-LR-L-GEOREF", f"The sheets are tied together to {fa['pair_rms_m']:g} m RMS where "
        "they overlap. Nørrebro would not correlate with any neighbour, so it rests on "
        f"{nb['control_points']} reader-supplied control points alone."))
    w("")
    try:
        write_doc(OUT, "\n".join(o).rstrip("\n") + "\n")
    except (live.Unjustified, claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
