#!/usr/bin/env python3
"""Generate docs/SOLUTIONS.md - what would actually stop the discharge, from the city's
own data.

Everything else in this project measures the problem. This measures the response: how
much of Copenhagen still drains sewage and rain down the same pipe, how much the plan
proposes to change that, how much has actually been disconnected, and what the city
built instead.

The one result that decides where to start: the register of overflow structures is
extremely concentrated. A small number of them hold most of the volume, which means a
small number of interventions - and a small number of measurements - would cover most of
the problem. It also means a sample designed to be representative cannot estimate the
mean, which is what the national concentration figures are built on.

Two stages. compute() reads the city's layers and the national register and writes
data/derived/solutions.json; the page is written from that file read live, so every
number on it links to the field it came from. Cloudburst lengths are not measured
here: they come from data/derived/conveyance.json. This script once measured the same
layer with its own metres-per-degree constants and printed different kilometres from
the rest of the site.

Usage:  python3 scripts/solutions.py           compute, then write the page
        python3 scripts/solutions.py --page    the page alone, from the stored result
"""
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, MANUAL, RAW, ROOT, log, read_json, write_doc, write_json
import live

OUT = os.path.join(DERIVED, "solutions.json")
CONVEYANCE = os.path.join(DERIVED, "conveyance.json")
MONITORING = os.path.join(MANUAL, "monitoring.json")
# Quantities in words that nothing in the repo stores are quoted from the committed
# page (live.quote): the site once said this, which is not the same as its being right.
PAGE_COMMIT = "86ecfe6"
SURFACE = {"Grønne veje", "Skybrudsveje", "Forsinkelsesveje"}     # as conveyance.py
# Categories in kloaksystem_status/_plan, grouped by what they mean for the sea.
COMBINED = "Fælleskloakeret"
RECONNECTED = "Separatkloakeretopland tilkoblet fællessystemet"
TAIL = (0.01, 0.05, 0.10, 0.20, 0.50)      # shares of structures, largest first
MINOR_HA, MINOR_PE = 0.5, 100              # systems smaller than both are not tabulated


def geo(name):
    return read_json(os.path.join(RAW, f"{name}.geojson"))["features"]


def num(v):
    try:
        return float(str(v).strip().replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def short(s, n=44):
    s = str(s)
    return s if len(s) <= n else s[:n - 1] + "…"


def compute():
    catch = [x["properties"] for x in geo("sp_kloakoplande")]

    def agg(key, areakey, pekey):
        A, P, N = collections.defaultdict(float), collections.defaultdict(float), collections.Counter()
        for p in catch:
            k = p.get(key) or "ikke oplyst"
            A[k] += p.get(areakey) or 0
            P[k] += p.get(pekey) or 0
            N[k] += 1
        return A, P, N
    As, Ps, Ns = agg("kloaksystem_status", "befaestet_areal_status", "pe_status")
    Ap, Pp, Np = agg("kloaksystem_plan", "befaestet_areal_plan", "pe_plan")

    trans = collections.Counter((p.get("kloaksystem_status"), p.get("kloaksystem_plan"))
                                for p in catch)
    leaving = [(b, n) for (aa, b), n in trans.items() if aa == COMBINED and b != COMBINED]

    lar = [x["properties"] for x in geo("lar_registreringer")]
    lar_tot = sum(num(p.get("afkoblet_areal_m2")) for p in lar)
    inuse = sum(num(p.get("afkoblet_areal_m2")) for p in lar
                if str(p.get("tilladelse_taget_i_brug")).strip().lower() == "ja")

    # The national register, not the Copenhagen clip - the sampling argument is national.
    pts = [x["properties"] for x in
           read_json(os.path.join(RAW, "national", "punkt_rbu_udl.geojson"))["features"]]
    cph_pts = geo("vp3_basis_2019_punkt_rbu_udl")
    vols = sorted((v for v in ((p.get("vol_sb") or 0) for p in pts) if v > 0), reverse=True)
    tot_v = sum(vols)
    tail = []
    for frac in TAIL:
        n = max(1, int(len(vols) * frac))
        tail.append({"share_of_structures": frac, "count": n,
                     "share_of_volume": round(sum(vols[:n]) / tot_v, 4)})

    res = {
        "_what": "The response to Copenhagen's combined sewer, from the city's catchment "
                 "and infiltration layers and the national overflow register. Written by "
                 "scripts/solutions.py; read by it to write docs/SOLUTIONS.md.",
        "systems": [{"name": k, "catchments": Ns[k], "impervious_ha": round(As[k], 2),
                     "pe": round(Ps[k])}
                    for k in sorted(As, key=lambda x: -As[x])
                    if not (As[k] < MINOR_HA and Ps[k] < MINOR_PE)],
        "impervious_total_ha": round(sum(As.values()), 2),
        "pe_total": round(sum(Ps.values())),
        "combined": {"impervious_ha": round(As[COMBINED], 2), "pe": round(Ps[COMBINED]),
                     "impervious_plan_ha": round(Ap[COMBINED], 2)},
        "reconnected_plan_ha": round(Ap.get(RECONNECTED, 0), 2),
        "catchments": {"combined": sum(n for (aa, _b), n in trans.items() if aa == COMBINED),
                       "stay_combined": trans[(COMBINED, COMBINED)],
                       "reconnected": trans.get((COMBINED, RECONNECTED), 0),
                       "separated": sum(n for b, n in leaving if b != RECONNECTED)},
        "lar": {"installations": len(lar), "disconnected_ha": round(lar_tot / 1e4, 2),
                "in_use_ha": round(inuse / 1e4, 2)},
        "register": {"discharge_points": len(pts),
                     "municipalities": len({p.get("komm_navn") for p in pts}),
                     "copenhagen_points": len(cph_pts), "with_volume": len(vols),
                     "largest_m3": round(vols[0]), "median_m3": round(vols[len(vols) // 2]),
                     "tail": tail},
    }
    write_json(OUT, res)
    return res


def page():
    r, cv, mon = live.live_json(OUT), live.live_json(CONVEYANCE), live.live_json(MONITORING)

    def share(part, whole):
        return live.step("K-SUBSET-SHARE", part / whole * 100)

    def q(text):
        return live.was(PAGE_COMMIT, "docs/SOLUTIONS.md", text)   # text: a locator
    o = []
    a = o.append
    comb, ta, tp = r["combined"], r["impervious_total_ha"], r["pe_total"]

    a("# What would actually stop it\n")
    a("Generated by `scripts/solutions.py` from Københavns Kommune's own catchment and "
      "cloudburst layers and the national overflow register. Everything else here "
      "measures the problem; this measures the response.\n")

    a("## 1. Copenhagen is a combined sewer\n")
    a("Rain that falls on a Copenhagen street mostly does not go to a river. It goes "
      "into the same pipe as the sewage, and when that pipe fills, the mixture leaves "
      "through an overflow structure without passing a treatment works.\n")
    a("| Sewer system | Catchments | Impervious area | Population equivalent |")
    a("|---|---:|---:|---:|")
    for s in r["systems"]:
        a(f"| `{short(s['name'])}` | {s['catchments']:,} | {s['impervious_ha']:,.0f} ha "
          f"({share(s['impervious_ha'], ta):.1f}%) | {s['pe']:,.0f} "
          f"({share(s['pe'], tp):.1f}%) |")
    a("")
    a(f"**{share(comb['pe'], tp):.1f}% of the city's population equivalent, and "
      f"{share(comb['impervious_ha'], ta):.1f}% of its impervious area, sits on a combined "
      f"system.** That is {comb['impervious_ha']:,.0f} hectares of roof and pavement whose "
      "runoff is, by design, mixed with sewage before it can go anywhere.\n")
    a("It is the single most consequential fact about the city's relationship with the "
      "sea, and it is not a fact about agriculture, nutrients or nitrogen. It is a "
      f"plumbing decision made {q("plumbing decision made @@. ##")}.\n")

    c = r["catchments"]
    a("## 2. The plan does not separate it\n")
    a(f"Every catchment carries both a current sewer type and a planned one. Of the "
      f"**{c['combined']} combined catchments**:\n")
    a("| Planned outcome | Catchments | What it means for the sea |")
    a("|---|---:|---|")
    a(f"| Stays combined | **{c['stay_combined']}** | nothing changes |")
    a(f"| *Separatkloakeret opland tilkoblet fællessystemet* | **{c['reconnected']}** | "
      "separated inside the catchment — **and reconnected to the combined system.** "
      "The rain is still in the sewage pipe by the time it reaches an overflow. |")
    a(f"| Genuine separation, stormwater to a recipient | **{c['separated']}** | the rain "
      "leaves the sewage system |")
    a("")
    a("The middle row is the finding, and the category's own name says it. Separating "
      "the pipes within a catchment and then joining them again upstream of the overflow "
      "changes what happens inside the block and changes nothing at the outfall.\n")
    net = comb["impervious_ha"] - comb["impervious_plan_ha"] - r["reconnected_plan_ha"]
    a(f"By impervious area: combined drops from {comb['impervious_ha']:,.0f} ha to "
      f"{comb['impervious_plan_ha']:,.0f} ha, but {r['reconnected_plan_ha']:,.0f} ha of that "
      "goes into the reconnected category. **Net area actually leaving the combined "
      f"system: about {net:,.0f} ha, or {share(net, comb['impervious_ha']):.1f}%.**\n")

    L = r["lar"]
    lo, hi = share(L["in_use_ha"], comb["impervious_ha"]), share(L["disconnected_ha"], comb["impervious_ha"])
    a("## 3. What has actually been disconnected\n")
    a("The other route off the combined system is local infiltration — soakaways, rain "
      "gardens, green roofs — each of which takes a specific area of roof or pavement "
      "off the sewer. The city registers them individually, with the disconnected area "
      "in square metres.\n")
    a("| | |")
    a("|---|---:|")
    a(f"| Registered installations | {L['installations']:,} |")
    a(f"| Total disconnected area | **{L['disconnected_ha']:,.0f} ha** |")
    a(f"| Of which confirmed in use | {L['in_use_ha']:,.0f} ha |")
    a(f"| Combined-sewered impervious area | {comb['impervious_ha']:,.0f} ha |")
    a(f"| **Share disconnected** | **{hi:.1f}%** (confirmed in use: {lo:.1f}%) |")
    a("")
    a(f"So after however many years of the policy, between {lo:.1f}% (confirmed in use) "
      f"and {hi:.1f}% (registered) of the relevant area has been taken off the pipe. At the "
      f"pace implied by the confirmed figure this is a {q("this is a @@, and nothing")}, and "
      "nothing about that is a criticism of infiltration as a technique — it is a "
      "statement about scale.\n")

    by = cv["by_typologi"]
    a("## 4. Copenhagen did build rivers — for the wrong rain\n")
    a("The cloudburst plan is not mostly pipes. It is mostly surface: streets reshaped "
      "into channels, green roads, squares that hold water. Deliberate rainwater rivers, "
      "at city scale, already designed and partly built.\n")
    a("| Type | Segments | Length | |")
    a("|---|---:|---:|---|")
    for k, v in by.items():
        tag = "**surface**" if k in SURFACE else ("pipe" if "ledning" in k.lower() else "mixed")
        a(f"| {k} | {v['features']:,} | {v['km']:,.1f} km | {tag} |")
    a(f"| **Total** | **{cv['features']:,}** | **{cv['total_km']:,.1f} km** | |")
    a("")
    a(f"**{cv['surface_km']:,.0f} km of surface conveyance against {cv['pipe_km']:,.0f} km "
      f"of pipe — {cv['surface_to_pipe']:.1f} to 1.** The idea is not missing from "
      "Copenhagen's plan. It is the plan's dominant form. Lengths are those of "
      "`scripts/conveyance.py`, the one length table for this layer.\n")
    a("### But a skybrudsvej is sized for the rain that does not cause overflows\n")
    a(f"The cloudburst plan is designed against a {q("designed against a @@. A skybrudsvej")}. A skybrudsvej is "
      "a route for water that has nowhere else to go — it activates when the system is "
      f"already overwhelmed, {q("already overwhelmed, @@. Overflows")}.\n")
    a(f"Overflows are not a {q("are not a @@. They happen")}. They happen on ordinary heavy rain, "
      "many times a year, and that rain still goes down the gully into the combined "
      "pipe exactly as it always did. The surface network was built for the flood risk "
      "to the city, which is a different problem with a different design storm.\n")
    a(f"The everyday-rain component is the green roads and the infiltration — "
      f"{by['Grønne veje']['km']:,.0f} km and {L['disconnected_ha']:,.0f} ha respectively — "
      f"against {comb['impervious_ha']:,.0f} ha that needs disconnecting.\n")
    a(f"Delivery, on the city's own expected-in-service dates: "
      f"**{cv['in_service_by_cutoff_km']:,.0f} km by the end of {cv['delivery_cutoff_year']}**, "
      f"{cv['scheduled_after_cutoff_km']:,.0f} km scheduled through "
      f"{cv['last_scheduled_year']}, and {cv['undated_km']:,.0f} km with no date at all.\n")

    g, h = r["register"], mon["hazardous_substances"]
    t0 = g["tail"][0]
    a("## 5. Why a representative sample cannot measure this\n")
    a(f"The national register holds **{g['discharge_points']:,} rain-dependent discharge "
      f"points** across {g['municipalities']} municipalities ({g['copenhagen_points']:,} "
      "of them inside the Copenhagen clip used elsewhere here). Only "
      f"**{g['with_volume']:,}** of them carry a recorded basin volume; the other "
      f"{g['discharge_points'] - g['with_volume']:,} have the field empty. Among those "
      "that do have a number, the distribution is extreme:\n")
    a("| Share of structures | Count | Share of stored volume |")
    a("|---|---:|---:|")
    for t in g["tail"]:
        a(f"| top {t['share_of_structures'] * 100:.0f}% | {t['count']:,} | "
          f"**{t['share_of_volume'] * 100:.1f}%** |")
    a("")
    a(f"**{t0['count']} structures hold {t0['share_of_volume'] * 100:.0f}% of the recorded "
      f"volume.** The largest is {g['largest_m3']:,.0f} m³; the median is "
      f"{g['median_m3']:,.0f} m³. That is a heavy tail, and heavy tails break sampling.\n")
    a("The national pollutant concentrations — the typetal, which Miljøstyrelsen applies "
      f"to {h['applied_to_discharge_points_nationally']:,} discharge points — come from "
      f"**{h['stations_combined_overflow']} combined-overflow stations and "
      f"{h['stations_separate_stormwater']} stormwater stations**, in catchments "
      "*deliberately chosen* to represent households and residential areas, and "
      "explicitly excluding industrial areas and heavily trafficked roads. The same "
      "report notes the highest median metal concentrations in sludge from basins, and "
      "the typetal explicitly cover only discharges without prior settling.\n")
    a("Put those together. In a heavy-tailed distribution the mean is set by the tail, "
      "so an estimate of the mean is an estimate of the tail. This sampling design "
      "removed the tail on purpose, then used the remainder to estimate the mean, then "
      "multiplied it by every discharge point in the country.\n")
    a("The same structure is well known in the ocean-plastic literature, where a small "
      "minority of rivers carries the large majority of the input, and any uniform "
      f"per-river assumption is wrong by {q("assumption is wrong by @@. There is no")}. There is no reason a "
      "sewer network should be "
      "more evenly behaved than a river network, and this register says it is not.\n")

    levels = list(mon["overflow_reporting"]["knowledge_levels"])
    best = next(x for x in levels if x["method"] == "Measurement-based")
    simple = next(x for x in levels if x["method"] == "Simple mass balance")
    a("## 6. How fast could any of this move?\n")
    a("The concentration in section 5 cuts both ways. It is what makes the measurement "
      "invalid, and it is also what makes the problem tractable — because if a few "
      "structures dominate, then a few interventions cover most of it.\n")
    a("| | Timescale | Why |")
    a("|---|---|---|")
    a(f"| Measure the tail | **weeks** | Flow-proportional samplers on the largest "
      f"{t0['count']} structures. That is videnniveau {best['level']}, the best method in "
      f"Miljøstyrelsen's own hierarchy, at {best['uncertainty_pct']}% uncertainty "
      f"instead of {simple['uncertainty_pct']}% for a simple mass balance. It has never "
      "been done because nobody is required to. |")
    a("| Publish event-level data | **weeks** | The event counts are already recorded in "
      "PULS. The flow rates are not recorded at all, which is a decision, not a limit. |")
    a("| Empty basins before the season | **months** | Accumulated sludge is exported "
      "when flow scours it. Removing it in advance is an operating procedure, not "
      "construction. |")
    a("| Intercept fat at source | **months** | Grease separators are already a legal "
      "requirement for food businesses. Enforcement is regulatory. |")
    a(f"| Disconnect roofs at scale | **years to decades** | {lo:.1f}–{hi:.1f}% done. |")
    a(f"| Genuinely separate the network | **decades** | {c['separated']} of the "
      f"{c['combined']} combined catchments are planned for it. |")
    a(f"| Deliver the surface network | **to {cv['last_scheduled_year']}** | on the city's "
      "own dates |")
    a("")
    a("So the honest answer to *how fast* is that it splits in two. **The measurement "
      "problem could be fixed in a season**, and until it is, nobody can say which of "
      "the slow interventions is worth the money. **The infrastructure problem cannot "
      "be fixed quickly by anyone**, and the plan on the books does not attempt it — "
      "it holds water back rather than routing it away.\n")
    a("Which is the case for doing the cheap thing first. Instrument the tail, find out "
      f"whether {q("out whether @@, and")}"
      ", and the argument about what to build next becomes an argument with evidence in it.\n")

    a("---\n")
    a("*Sources: `sp_kloakoplande`, `lar_registreringer` and `skp_veje_tunneller_kk` "
      "from Københavns Kommune's WFS; `vp3_basis_2019_punkt_rbu_udl` from Miljøgis; the "
      "national register `punkt_rbu_udl`. Typetal and knowledge-level provenance in "
      "`data/manual/monitoring.json`. Lengths are computed from the geometries by "
      "`scripts/conveyance.py`; areas and volumes are the values the publishers "
      "recorded.*")
    write_doc(os.path.join(ROOT, "docs", "SOLUTIONS.md"), "\n".join(o))
    log("wrote docs/SOLUTIONS.md")


def main(argv):
    if "--page" not in argv:
        compute()
        log(f"wrote {os.path.relpath(OUT, ROOT)}")
    page()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
