#!/usr/bin/env python3
"""Generate docs/CONSTRUCTED.md - constructions held against measurements.

A register of comparisons run elsewhere in this project. An entry stands only where
its result is read live from stored data (the water-body partition, the hazardous-
substance layer, the Secchi rows, the city's structure register, the Nørrebro sheet's
placement) or rests on a claim checked on another page; every assertion on the page is
a checked claim (LIVE_NUMBERS.md section 11), registered in
data/manual/claims.d/w3-gc.json. What the register once said and could not justify is
in docs/ARCHIVE.md. The register's own size is counted from the rows below and stored
in data/derived/constructed.json.

    python3 scripts/pages/constructed.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common import DERIVED, ROOT, log, write_doc, write_json
import claims as _claims
import live

PAGE = "docs/CONSTRUCTED.md"
OUT = os.path.join(DERIVED, "constructed.json")
C, B, E = live.claim, live.claim_begin, live.CLAIM_END


def rows():
    """(construction, held against, result, verdict, ours) - ours marks the project's own."""
    L = live.live_json(os.path.join(DERIVED, "light.json"))["secchi"]
    bands = list(L["bands"])
    split = bands[1]["to"]
    shallow = [b for b in bands if b["to"] <= split]
    deep = [b for b in bands if b["to"] > split]
    sh = sum(b["n"] * b["at_bed_pct"] for b in shallow) / sum(b["n"] for b in shallow)
    dp = sum(b["n"] * b["at_bed_pct"] for b in deep) / sum(b["n"] for b in deep)
    m = live.live_json(os.path.join(ROOT, "docs", "data", "flood2012", "manifest.json"))
    se = m["sheets"]["norrebro"]["standard_error_m"]
    tied = "norrebro" not in list((m.get("bundle_adjustment") or {}).get("unconstrained") or [])
    ar = live.live_json(os.path.join(DERIVED, "areas.json"))
    hz = ar["hazardous_layer"]
    n_wb = ar["summary"]["sets"]["all"]["n"]
    ps = live.live_json(os.path.join(ROOT, "docs", "data", "areas", "partition_subspace.json"))
    n_sub = sum(r["subsets"] for r in ps["results"])
    lifts = [r["derived_vs_official_lift"] for r in ps["results"]]
    st = live.live_json(os.path.join(ROOT, "docs", "data", "architecture.json"))["structures"]
    return [
        ("**`markoverskud`** — field surplus, a norm product",
         "measured normalised diffuse load, nationally and per catchment",
         C("C-GC-C-MARK-R", "nationally *\"en meget stærk, signifikant lineær relation\"*; per "
           "catchment, DCE themselves note that not all fjord catchments respond equally fast"),
         C("C-GC-C-MARK-V", "**a strong national relation says nothing about any one "
           "catchment's coefficient.** The study that sizes the catchment coefficients could "
           "not be read here"), False),
        (f"**the official water bodies** — a drawn partition of {n_wb} polygons",
         f"measured station similarity, all {n_sub} feature subsets, contiguity-matched null",
         C("C-GC-C-WB-R", f"lift **{min(lifts):+.3f} to {max(lifts):+.3f}**"),
         C("C-GC-C-WB-V", "adds nothing beyond being a connected region of its size"), False),
        ("**`DIATO`, `DINO`, `PICO`, `NANO`** — plankton functional-type fields",
         "`CHL`, the same files",
         C("C-GC-C-PFT-R", "each field is derived from chlorophyll, by the provider's own note "
           "in the files"),
         C("C-GC-C-PFT-V", "**composition change at constant biomass is unrepresentable**"),
         False),
        ("**`hz`, marine hazardous-substance coverage** — ours",
         "the source layer's own geography",
         C("C-GC-C-HZ-R", f"**{hz['coast']} of {hz['points']} points are marine** "
           f"({hz['lake']} lake, {hz['river']} river)"),
         C("C-GC-C-HZ-V", "withdrawn; the coverage was manufactured by proximity"), True),
        ("**`SigtDybde_m`, Secchi depth**",
         f"`BundDybde_m`, bottom depth, {L['n_paired']:,} paired rows",
         C("C-GC-C-SECCHI-R", f"seen-to-bottom on **{sh:.1f}%** of readings where the water is "
           f"{split:g} m deep or less, and **{dp:.1f}%** deeper"),
         C("C-GC-C-SECCHI-V", f"right-censored, **{sh / dp:.0f}× more in shallow water**; any "
           "clarity-vs-depth comparison is partly the censoring"), False),
        ("**ρ\\*, the mean-square ratio reported as ICC**", "its own null",
         C("C-GC-C-RHO-R", "labels that carry no information score near one half, not zero"),
         C("C-GC-C-RHO-V", "no raw value is readable on its own"), False),
        ("**`confident` on the Nørrebro flood sheet** — ours, a quality flag",
         "the spread over *all* registration variants, not just the agreeing ones",
         C("C-GC-C-NB-R", "the flag's spread was measured over the agreeing variants only"),
         C("C-GC-C-NB-V", "**the confidence statistic was conditioned on the selection it "
           "validated.** The rule now needs a majority and measures the spread over every "
           "variant. Since placed from resident-reported control points, standard error "
           f"{se:g} m"
           + ("." if tied else "; the bundle adjustment still cannot tie it to the other "
              "sheets.")), True),
        ("**a structure register with a type column** — `k101:rist`, `k101:broend`, the "
         "city's own", "its own field",
         C("C-GC-C-ST-R", f"**empty on {st['rist']['type_field_empty_pct']:.0f}% of "
           f"{st['rist']['total']:,} gratings and {st['broend']['type_field_empty_pct']:.0f}% "
           f"of {st['broend']['total']:,} wells**, while every one carries an elevation"),
         C("C-GC-C-ST-V", "**an unfilled field, not an absent dimension.** The column exists, "
           "the survey happened, the value was never entered — so a contractor planning a bore "
           "knows where every lid is and not what one of them is"), False),
    ]


def main():
    try:
        rs = rows()
        write_json(OUT, {"_what": "The size of the constructions register, counted from the "
                                  "rows scripts/pages/constructed.py prints.",
                         "entries": len(rs), "ours": sum(1 for r in rs if r[4])})
        n = live.live_json(OUT)
        o = []
        w = o.append
        w("# Constructions, held against measurements\n")
        w(C("C-GC-C-HOLD", "A constructed quantity — a residual, a norm product, a partition, "
            "a threshold, a model output — should be held against something that was "
            "measured, and **the relation between them stated as a number.**") + "\n")
        w(C("C-GC-C-REGISTER", "This page is a register of such comparisons this project has "
            "run. It is meant to be added to. Generated by `scripts/pages/constructed.py`, "
            "which reads each entry's result from stored data or rests it on a claim checked "
            "elsewhere on the site.") + "\n")
        w("---\n")
        w("## The check\n")
        w("Given a construction `C` and a measurement `M` that ought to track it:\n")
        w("1. **Sign** — do they move together at all?")
        w("2. **Coefficient** — is the ratio `ΔM/ΔC` stable across strata, or does it range?")
        w("3. " + B("C-GC-C-CHECK3") + "**Discontinuity** — does `C` step on a date where "
          "`M` does not? A step with an")
        w("   administrative cause and no measured counterpart is the construction's "
          "non-physical")
        w("   component, and its size is measurable." + E)
        w("4. " + B("C-GC-C-CHECK4") + "**Aggregation** — does the pooled relation look "
          "tighter than the stratified one? If")
        w("   so, the tightness is partly the pooling." + E + "\n")
        w(C("C-GC-C-SIGNHIDES", "**The coefficient and aggregation checks are where a "
            "construction can pass the sign check and still fail**, and a good sign hides "
            "that failure.") + "\n")
        w("---\n")
        w("## The register\n")
        w("| construction | held against | result | verdict |")
        w("|---|---|---|---|")
        for c, m_, r, v, _ in rs:
            w(f"| {c} | {m_} | {r} | {v} |")
        w("")
        w(C("C-GC-C-OURS", f"Ours are marked as ours. {n['ours']} of the {n['entries']} "
            "entries are this project's own constructions failing its own check, which is "
            "the point of keeping the register rather than a list of other people's "
            "errors.") + "\n")
        w("---\n")
        w("## What the register shows\n")
        w(C("C-GC-C-SIGN", "**Sign is cheap and coefficient is not.** A relation that gets "
            "the direction right says nothing about whether its magnitude transfers from one "
            "stratum to another, and that is the failure a correlation cannot detect.") + "\n")
        w(C("C-GC-C-AGG", "**Aggregation is where the failure hides.** `markoverskud` at "
            "national scale looks strong, and DCE's own report says the catchments did not "
            "all follow it. The water bodies look like a partition and carry no within-basket "
            "signal. **A pooled statistic can be tighter than any of its parts, because "
            "pooling averages over a coefficient that varies.**") + "\n")
        w(C("C-GC-C-DIRECTION", "**And a good sign licenses a claim about direction only.** "
            "\"Nitrogen surplus fell and load fell\" is supported nationally. \"Cutting the "
            "surplus by `X` will cut the load by `0.7X`\" needs a catchment's own "
            "coefficient, which this register does not hold.") + "\n")
        w("---\n")
        w("## Adding to it\n")
        w(C("C-GC-C-ADD", "An entry needs four things: the construction, the measurement it "
            "was held against, the result — a number wherever one is stored — and what the "
            "comparison licenses. If a check was run and passed, that belongs here too — a "
            "register of only failures would be a construction with its own selection "
            "problem. A new entry's number should come from a stored result, not from this "
            "page.") + "\n")
        w(C("C-GC-C-METHOD", "Method, and the audit of which parts of it survive their own "
            "rules: [statistical-methods](https://github.com/Jjokulian/statistical-methods)."))
        write_doc(os.path.join(ROOT, PAGE), "\n".join(o) + "\n")
    except (live.Unjustified, _claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote {PAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
