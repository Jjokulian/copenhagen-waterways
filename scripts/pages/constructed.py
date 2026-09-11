#!/usr/bin/env python3
"""Generate docs/CONSTRUCTED.md - constructions held against measurements.

A register of comparisons run elsewhere in this project. Where an entry's numbers
are stored in data/derived, they are read live (the Secchi row, the Nørrebro
sheet's current placement). Most entries were computed in analyses that never
stored their result; until they do, their numbers are carried as quotations of
this register's committed text (live.quote), whose construction says only that
the site once said this, not that it was right. The register's own size is
counted from the rows below and stored in data/derived/constructed.json.

    python3 scripts/pages/constructed.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from common import DERIVED, ROOT, log, write_doc, write_json
import live

PAGE = "docs/CONSTRUCTED.md"
COMMIT = "169b06e"            # the committed register the unstored numbers are quoted from
OUT = os.path.join(DERIVED, "constructed.json")


def q(text):
    return live.was(COMMIT, PAGE, text)   # text: a locator, @@ at the value


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
    return [
        ("**`markoverskud`** — field surplus, a norm product",
         "measured normalised diffuse load, per catchment, 1990–2009",
         q('1990–2009 | @@ | **sign') + "**",
         "**sign good, coefficient not usable.** A load predicted from a surplus is "
         f"overestimated {q("surplus is overestimated @@, or entirely")}, or entirely", False),
        ("the same, **at national scale**", "the same, pooled",
         "*\"en meget stærk, signifikant lineær relation\"*",
         "**the pooled fit is tight because the coefficient varies.** The aggregation step "
         "failing in public", False),
        (f"**{q("public | | **@@** — a drawn")}** — a drawn partition",
         f"measured station similarity, {q("station similarity, @@, contiguity-matched")}, contiguity-matched null",
         f"lift **{q("null | lift **@@** | adds nothing")}**",
         "adds nothing beyond being a connected region of its size", False),
        ("**pooled oxygen trend**", "the same trend on year-round stations only",
         q('only | @@ | the') + "**",
         "the pooled wobble is **network composition**, not water", False),
        ("**`< 4 mg/l` hypoxia threshold**", "the same seasonality on a saturation threshold",
         "**" + q("threshold | **@@** against **15.5-fold**") + "** against **" + q("@@** | roughly a third of the") + "**",
         f"{q("against **15.5-fold** | @@ of the seasonal")} of the seasonal signal is oxygen solubility — the threshold is "
         "partly a thermometer", False),
        (f"**`DIATO`, `DINO`, `PICO`, `NANO`** — {q("`PICO`, `NANO`** — @@ of plankton fields")} of plankton fields",
         "`CHL`, the same file",
         f"ratio functionally determined by CHL; within-bin spread **{q("within-bin spread **@@** against a")}** against a "
         f"range of {q("a range of @@ | **six fields")}",
         f"**{q("of 0.33–0.43 | **@@.** Composition change at")}.** Composition change at constant biomass is "
         "unrepresentable", False),
        (f"**`hz`, marine hazardous-substance coverage on {q("hazardous-substance coverage on @@** — ours")}** — ours",
         "the source layer's own geography",
         f"**{q("own geography | **@@** (152 lake, 104")}** ({q("are marine** (@@) | withdrawn;")})",
         "withdrawn; the coverage was manufactured by proximity", True),
        ("**`SigtDybde_m`, Secchi depth**",
         f"`BundDybde_m`, bottom depth, {L['n_paired']:,} paired rows",
         f"seen-to-bottom on **{sh:.1f}%** of readings where the water is {split:g} m deep or "
         f"less, and **{dp:.1f}%** deeper",
         f"right-censored, **{sh / dp:.0f}× more in shallow water**; any clarity-vs-depth "
         "comparison is partly the censoring", False),
        ("**ρ\\*, the mean-square ratio reported as ICC**", "its own null, simulated",
         q("null, simulated | @@ | every raw"), "every raw value was unreadable as published", False),
        ("**ARI across mismatched granularities**", "its attainable maximum",
         q("attainable maximum | @@ | an observed"),
         q("vs 84 | @@ | | **`confident`"), False),
        ("**`confident` on the Nørrebro flood sheet** — ours, a quality flag",
         "the spread over *all* registration variants, not just the agreeing ones",
         q("ones | @@ | **the"),
         "**the confidence statistic was conditioned on the selection it validated.** "
         "Withdrawn at the time. Since re-registered from resident-reported control points, "
         f"standard error {se:g} m"
         + ("." if tied else "; the bundle adjustment still cannot tie it to the other sheets."),
         True),
        ("**\"summer-peaked\" vs \"year-round\" stations** — ours, a category",
         "its own definition, varied",
         q("varied | @@ | **the"),
         "**the category was never defined.** Under a raw-R rule with no minimum, "
         + "**" + q("minimum, **@@ stations with") + " stations with one observation** score `R = 1` and became " + q("and became @@ of the")
         + " of the \"seasonal\" group", True),
        ("**a structure register with a type column** — `k101:rist`, `k101:broend`, the "
         "city's own", "its own field",
         f"**{q("field | **@@**, while every")}**, while every one "
         "carries a centimetre-resolution elevation and a registration date",
         "**an unfilled field, not an absent dimension.** The column exists, the survey "
         "happened, the value was never entered — so a contractor planning a bore knows where "
         "every lid is and not what one of them is", False),
    ]


def main():
    rs = rows()
    write_json(OUT, {"_what": "The size of the constructions register, counted from the rows "
                              "scripts/pages/constructed.py prints.",
                     "entries": len(rs), "ours": sum(1 for r in rs if r[4])})
    n = live.live_json(OUT)
    o = []
    w = o.append
    w("# Constructions, held against measurements\n")
    w("A constructed quantity — a residual, a norm product, a partition, a threshold, a model "
      "output — should be held against something that was measured, and **the relation "
      "between them stated as a number.** Almost none ever is.\n")
    w("This page is the register of every such comparison this project has actually run. It "
      "is meant to be added to. Generated by `scripts/pages/constructed.py`; where an entry's "
      "result is not yet stored by the analysis that produced it, the number is quoted from "
      "the register's committed text and links to that commit.\n")
    w("---\n")
    w("## The check\n")
    w("Given a construction `C` and a measurement `M` that ought to track it:\n")
    w("1. **Sign** — do they move together at all?")
    w("2. **Coefficient** — is the ratio `ΔM/ΔC` stable across strata, or does it range?")
    w("3. **Discontinuity** — does `C` step on a date where `M` does not? A step with an")
    w("   administrative cause and no measured counterpart is the construction's non-physical")
    w("   component, and its size is measurable.")
    w("4. **Aggregation** — does the pooled relation look tighter than the stratified one? If")
    w("   so, the tightness is partly the pooling.\n")
    w("Most published constructions have had the sign check done and stop there. **The "
      "coefficient and aggregation checks are where they fail**, and they fail in a way that "
      "a good sign hides.\n")
    w("---\n")
    w("## The register\n")
    w("| construction | held against | result | verdict |")
    w("|---|---|---|---|")
    for c, m_, r, v, _ in rows():
        w(f"| {c} | {m_} | {r} | {v} |")
    w("")
    w(f"Ours are marked as ours. {n['ours']} of the {n['entries']} entries are this project's "
      "own constructions failing its own check, which is the point of keeping the register "
      "rather than a list of other people's errors.\n")
    w("---\n")
    w("## What the register shows\n")
    w("**Sign is cheap and coefficient is not.** Every construction here passes the sign "
      "check. Most fail the coefficient or the aggregation check — the direction is right and "
      "the magnitude is not transferable. That is the failure mode a correlation cannot "
      "detect and a published relation almost never reports.\n")
    w("**Aggregation is where the failure hides.** `markoverskud` at national scale looks "
      f"strong and at catchment scale {q("catchment scale @@. The")}. The water bodies "
      "look like a partition and carry no within-basket signal. The pooled oxygen trend looks "
      "like water and is network composition. In each case **the pooled statistic is tighter "
      "than any of its parts, and the tightness is what aggregation does to a variable "
      "coefficient.**\n")
    w("**And a good sign licenses a claim about direction only.** \"Nitrogen surplus fell and "
      "load fell\" is supported. \"Cutting the surplus by `X` will cut the load by `0.7X`\" is "
      "not, anywhere in this data.\n")
    w("---\n")
    w("## Adding to it\n")
    w("An entry needs four things: the construction, the measurement it was held against, the "
      "number, and what the comparison licenses. If a check was run and passed, that belongs "
      "here too — a register of only failures would be a construction with its own selection "
      "problem. A new entry's number should come from a stored result, not from this page.\n")
    w("Method, and the audit of which parts of it survive their own rules:")
    w("[statistical-methods](https://github.com/Jjokulian/statistical-methods).")
    write_doc(os.path.join(ROOT, PAGE), "\n".join(o) + "\n")
    log(f"wrote {PAGE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
