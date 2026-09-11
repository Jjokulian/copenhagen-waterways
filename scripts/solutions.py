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
OUTFALLS = os.path.join(DERIVED, "outfalls.json")      # the national overflow layer, counted
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
    import claims
    r, cv, mon = live.live_json(OUT), live.live_json(CONVEYANCE), live.live_json(MONITORING)
    ov = live.live_json(OUTFALLS)["layers"]["combined_overflow"]["totals"]["Antal overløb"]
    cd, _, _ = claims.load()
    cache = {}

    def rd(ph):
        return claims.resolve(cd, ph, cache)[0]

    def share(part, whole):
        return live.step("K-SUBSET-SHARE", part / whole * 100)
    B, E, C = live.claim_begin, live.CLAIM_END, live.claim
    hundred = rd("{read:FLOOD2012-AMAGER:100|ved en 100 års hændelse}")
    outlets = rd("{read:MEIJER-2021:100,887|Of the total 100,887 outlets of rivers and streams}")
    rivers = rd("{read:MEIJER-2021:1656|emitted by 1656 rivers in total}")
    pct80 = rd("{read:MEIJER-2021:80|More than 1000 rivers account for 80% of global riverine plastic emissions}")
    o = []
    a = o.append
    comb, ta, tp = r["combined"], r["impervious_total_ha"], r["pe_total"]

    a("# What would actually stop it\n")
    a(C("C-CS-S-SOURCE", "Generated by `scripts/solutions.py` from Københavns Kommune's own "
        "catchment and cloudburst layers and the national overflow register.")
      + " This page measures the response.\n")

    a("## 1. Copenhagen is a combined sewer\n")
    a(B("C-CS-S-COMBINED") + "Rain that falls on a Copenhagen street mostly does not go to a "
      "river. It goes into the same pipe as the sewage, and when that pipe fills, the mixture "
      "leaves through an overflow structure without passing a treatment works." + E + "\n")
    a("| Sewer system | Catchments | Impervious area | Population equivalent |")
    a("|---|---:|---:|---:|")
    for s_ in r["systems"]:
        a(f"| `{short(s_['name'])}` | {s_['catchments']:,} | {s_['impervious_ha']:,.0f} ha "
          f"({share(s_['impervious_ha'], ta):.1f}%) | {s_['pe']:,.0f} "
          f"({share(s_['pe'], tp):.1f}%) |")
    a("")
    a(B("C-CS-S-SHARE") + f"**{share(comb['pe'], tp):.1f}% of the city's population equivalent, "
      f"and {share(comb['impervious_ha'], ta):.1f}% of its impervious area, sits on a combined "
      f"system.** That is {comb['impervious_ha']:,.0f} hectares of roof and pavement whose runoff "
      "is, by design, mixed with sewage before it can go anywhere." + E + "\n")
    a(C("C-CS-S-PLUMBING", "It is a fact about plumbing, not about agriculture, nutrients or "
        "nitrogen.") + "\n")

    c = r["catchments"]
    a("## 2. The plan does not separate it\n")
    a(C("C-CS-S-PLAN-INTRO", "Every catchment carries both a current sewer type and a planned "
        f"one. Of the **{c['combined']} combined catchments**:") + "\n")
    a("| Planned outcome | Catchments | What it means for the sea |")
    a("|---|---:|---|")
    a(f"| Stays combined | **{c['stay_combined']}** | nothing changes |")
    a(f"| *Separatkloakeret opland tilkoblet fællessystemet* | **{c['reconnected']}** | "
      + C("C-CS-S-RECONNECT", "separated inside the catchment - **and reconnected to the "
          "combined system.** The rain is still in the sewage pipe by the time it reaches an "
          "overflow.") + " |")
    a(f"| Genuine separation, stormwater to a recipient | **{c['separated']}** | the rain "
      "leaves the sewage system |")
    a("")
    a(B("C-CS-S-MIDDLE") + "The middle row is the finding, and the category's own name says it. "
      "Separating the pipes within a catchment and joining them again upstream of the overflow "
      "changes what happens inside the block and nothing at the outfall." + E + "\n")
    net = comb["impervious_ha"] - comb["impervious_plan_ha"] - r["reconnected_plan_ha"]
    a(B("C-CS-S-NET") + f"By impervious area: combined drops from {comb['impervious_ha']:,.0f} ha "
      f"to {comb['impervious_plan_ha']:,.0f} ha, but {r['reconnected_plan_ha']:,.0f} ha of that "
      "goes into the reconnected category. **Net area actually leaving the combined system: "
      f"about {net:,.0f} ha, or {share(net, comb['impervious_ha']):.1f}%.**" + E + "\n")

    L = r["lar"]
    lo, hi = share(L["in_use_ha"], comb["impervious_ha"]), share(L["disconnected_ha"], comb["impervious_ha"])
    a("## 3. What has actually been disconnected\n")
    a(B("C-CS-S-LAR-WHAT") + "The other route off the combined system is local infiltration - "
      "soakaways, rain gardens, green roofs - each of which takes a specific area of roof or "
      "pavement off the sewer. The city registers them individually, with the disconnected area "
      "in square metres." + E + "\n")
    a("| | |")
    a("|---|---:|")
    a(f"| Registered installations | {L['installations']:,} |")
    a(f"| Total disconnected area | **{L['disconnected_ha']:,.0f} ha** |")
    a(f"| Of which confirmed in use | {L['in_use_ha']:,.0f} ha |")
    a(f"| Combined-sewered impervious area | {comb['impervious_ha']:,.0f} ha |")
    a(f"| **Share disconnected** | **{hi:.1f}%** (confirmed in use: {lo:.1f}%) |")
    a("")
    a(B("C-CS-S-LAR") + f"So between {lo:.1f}% (confirmed in use) and {hi:.1f}% (registered) of "
      "the relevant area has been taken off the pipe. That is a statement about scale, not a "
      "criticism of infiltration as a technique." + E + "\n")

    by = cv["by_typologi"]
    a("## 4. Copenhagen did build rivers - for the wrong rain\n")
    a(B("C-CS-S-SURFACE-WHAT") + "The cloudburst plan is not mostly pipes. It is mostly surface: "
      "streets reshaped into channels, green roads, squares that hold water - rainwater rivers "
      "at city scale, designed and partly built." + E + "\n")
    a("| Type | Segments | Length | |")
    a("|---|---:|---:|---|")
    for k, v in by.items():
        tag = "**surface**" if k in SURFACE else ("pipe" if "ledning" in k.lower() else "mixed")
        a(f"| {k} | {v['features']:,} | {v['km']:,.1f} km | {tag} |")
    a(f"| **Total** | **{cv['features']:,}** | **{cv['total_km']:,.1f} km** | |")
    a("")
    a(B("C-CS-S-RATIO") + f"**{cv['surface_km']:,.0f} km of surface conveyance against "
      f"{cv['pipe_km']:,.0f} km of pipe - {cv['surface_to_pipe']:.1f} to 1.** The idea is not "
      "missing from Copenhagen's plan; it is the plan's dominant form. Lengths are those of "
      "`scripts/conveyance.py`, the one length table for this layer." + E + "\n")
    a("### But a skybrudsvej is sized for the rain that does not cause overflows\n")
    a(B("C-CS-S-DESIGN") + f"The city's flood scenarios for the cloudburst plan are for a "
      f"{hundred}-year event. A skybrudsvej carries water only when the pipes are already "
      "overwhelmed; ordinary heavy rain still goes into the combined pipe." + E + "\n")
    a(B("C-CS-S-OFTEN") + "Overflows are counted in years, not centuries: in the national layer, "
      f"the {ov['n']:,} combined-sewer overflow structures that fill in the count report a median "
      f"of {ov['median']:,.0f} overflows a year." + E + " "
      + C("C-CS-S-DIFFERENT", "The surface network answers the flood risk to the city, which is "
          "a different problem with a different design storm.") + "\n")
    a(B("C-CS-S-EVERYDAY") + "The everyday-rain component is the green roads and the "
      f"infiltration - {by['Grønne veje']['km']:,.0f} km and {L['disconnected_ha']:,.0f} ha "
      f"respectively - against {comb['impervious_ha']:,.0f} ha that needs disconnecting." + E + "\n")
    a(B("C-CS-S-DELIVERY") + "Delivery, on the city's own expected-in-service dates: "
      f"**{cv['in_service_by_cutoff_km']:,.0f} km by the end of {cv['delivery_cutoff_year']}**, "
      f"{cv['scheduled_after_cutoff_km']:,.0f} km scheduled through {cv['last_scheduled_year']}, "
      f"and {cv['undated_km']:,.0f} km with no date at all." + E + "\n")

    g, h = r["register"], mon["hazardous_substances"]
    t0 = g["tail"][0]
    a("## 5. Why a representative sample cannot measure this\n")
    a(B("C-CS-S-REGISTER") + f"The national register holds **{g['discharge_points']:,} "
      f"rain-dependent discharge points** across {g['municipalities']} municipalities "
      f"({g['copenhagen_points']:,} of them inside the Copenhagen clip used elsewhere here). Only "
      f"**{g['with_volume']:,}** of them carry a recorded basin volume; the other "
      f"{g['discharge_points'] - g['with_volume']:,} have the field empty. Among those that do "
      "have a number, the distribution is extreme:" + E + "\n")
    a("| Share of structures | Count | Share of stored volume |")
    a("|---|---:|---:|")
    for t in g["tail"]:
        a(f"| top {t['share_of_structures'] * 100:.0f}% | {t['count']:,} | "
          f"**{t['share_of_volume'] * 100:.1f}%** |")
    a("")
    a(B("C-CS-S-TAIL") + f"**{t0['count']} structures hold {t0['share_of_volume'] * 100:.0f}% of "
      f"the recorded volume.** The largest is {g['largest_m3']:,.0f} m³; the median is "
      f"{g['median_m3']:,.0f} m³. That is a heavy tail." + E + "\n")
    a(B("C-CS-S-TYPETAL") + "The national concentrations for hazardous substances in these "
      f"discharges - the typetal - come from **{h['stations_combined_overflow']} combined-overflow "
      f"stations and {h['stations_separate_stormwater']} stormwater stations** in catchments "
      "chosen to represent households and residential areas. They cover only discharges "
      "without prior treatment such as settling in basins, and not industrial areas or heavily "
      "trafficked roads, which the report says typically carry more; and the report finds that "
      "a significant share of the adsorbing substances is caught in basin sediment." + E + "\n")
    a(B("C-CS-S-TAILARG") + "Put those together. The stored volume is concentrated in a few "
      "structures; the concentrations describe the typical residential case and leave out the "
      "discharge types the report itself expects to carry more. A national load built as volume "
      "times typetal therefore rests on the typical case. Whether the load, like the volume, is "
      "concentrated in a few structures is not measured." + E + "\n")
    a(C("C-CS-S-PLASTIC", f"A similar concentration is documented for plastic in rivers: of "
        f"{outlets} river outlets in a global model, {rivers} account for {pct80}% of the plastic "
        "emitted to the ocean ([Meijer et al., *Science Advances*, "
        "2021](https://doi.org/10.1126/sciadv.aaz5803)).") + " "
      + C("C-CS-S-ANALOGY", "A sewer network need not be more evenly behaved than a river "
          "network, and this register's storage is not.") + "\n")

    levels = list(mon["overflow_reporting"]["knowledge_levels"])
    best = next(x for x in levels if x["method"] == "Measurement-based")
    simple = next(x for x in levels if x["method"] == "Simple mass balance")
    a("## 6. How fast could any of this move?\n")
    a(B("C-CS-S-TRACTABLE") + "The concentration in section 5 cuts both ways. It is what makes a "
      "typical-case estimate weak, and it is also what makes the problem tractable: if a few "
      "structures dominate, a few interventions cover most of it." + E + "\n")
    a(C("C-CS-S-TIMESCALES", "The timescales below are this page's estimates, from what each step "
        "involves - equipment, an operating procedure, regulation, construction - not from any "
        "costed plan.") + "\n")
    a("| | Timescale | Why |")
    a("|---|---|---|")
    a("| Measure the tail | **weeks** | " + C("C-CS-S-MEASURE", "Flow-proportional samplers on "
      f"the largest {t0['count']} structures. That is videnniveau {best['level']}, the best "
      f"method in Miljøstyrelsen's own hierarchy, at {best['uncertainty_pct']}% uncertainty "
      f"instead of {simple['uncertainty_pct']}% for a simple mass balance.") + " |")
    a("| Publish event-level data | **weeks** | " + C("C-CS-S-PULS", "PULS already holds the "
      "number of overflows a year. No flow rate is recorded at all, which is a decision about "
      "the format, not a limit of the instruments.") + " |")
    a("| Empty basins before the season | **months** | " + C("C-CS-S-BASINS", "Material caught "
      "in basin sediment can be carried out when a high flow scours it. Removing it in advance "
      "is an operating procedure, not construction.") + " |")
    a("| Intercept fat at source | **months** | " + C("C-CS-S-FAT", "A grease separator sits at "
      "the business, so this is regulation and enforcement, not construction.") + " |")
    a("| Disconnect roofs at scale | **years to decades** | " + C("C-CS-S-ROW-DISCONNECT",
      f"{lo:.1f}-{hi:.1f}% done.") + " |")
    a("| Genuinely separate the network | **decades** | " + C("C-CS-S-ROW-SEPARATE",
      f"{c['separated']} of the {c['combined']} combined catchments are planned for it.") + " |")
    a(f"| Deliver the surface network | **to {cv['last_scheduled_year']}** | on the city's own "
      "dates |")
    a("")
    a(B("C-CS-S-SPLIT") + "So the answer to *how fast* splits in two. **The measurement problem "
      "could be addressed within a season**, and until it is, nobody can say which of the slow "
      "interventions is worth the money. **The infrastructure problem cannot be fixed quickly "
      "by anyone**, and the sewer plan on the books leaves most combined catchments combined." + E + "\n")
    a(B("C-CS-S-FIRST") + "Which is the case for doing the cheap thing first. Instrument the "
      "tail, find out whether a handful of structures dominates the load the way a handful "
      "dominates the volume, and the argument about what to build next becomes an argument with "
      "evidence in it." + E + "\n")

    a("---\n")
    a("*" + C("C-CS-S-SOURCES", "Sources: `sp_kloakoplande`, `lar_registreringer` and "
      "`skp_veje_tunneller_kk` from Københavns Kommune's WFS; `vp3_basis_2019_punkt_rbu_udl` from "
      "Miljøgis; the national register `punkt_rbu_udl`; the national overflow layer from "
      "spildevandsdata.dk. Typetal and knowledge-level provenance in "
      "`data/manual/monitoring.json`. Lengths are computed from the geometries by "
      "`scripts/conveyance.py`; areas and volumes are the values the publishers recorded.") + "*")
    try:
        write_doc(os.path.join(ROOT, "docs", "SOLUTIONS.md"), "\n".join(o))
    except (live.Unjustified, claims.Refused) as e:
        log(str(e))
        return 1
    log("wrote docs/SOLUTIONS.md")
    return 0


def main(argv):
    if "--page" not in argv:
        compute()
        log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return page()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
