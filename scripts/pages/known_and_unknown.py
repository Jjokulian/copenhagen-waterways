#!/usr/bin/env python3
"""docs/KNOWN_AND_UNKNOWN.md - what is known, by whom, and the discovery rate.

The page was hand-written, and one of its numbers had already gone wrong in the
way the page itself warns about: "`SondeNr` arrives as `999` on 83.5% of rows"
was measured on a sample, and the full CTD extract counted by scripts/enums.py
says a quarter. The prose is kept here; every number comes through live.py.

Numbers that describe what an earlier stage of the work found - the flood
figure before and after a re-registration, the counts a one-off audit took -
are stored by no script. Those are quoted from the commit that first published
the page, and the count of them is logged.

    python3 scripts/pages/known_and_unknown.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import DERIVED, MANUAL, ROOT, log, write_doc
import claims
import live

OUT = os.path.join(ROOT, "docs", "KNOWN_AND_UNKNOWN.md")
PAGE = "docs/KNOWN_AND_UNKNOWN.md"
THEN = "3d71dde"        # the page as last written by hand


def J(*p):
    return live.live_json(os.path.join(*p))


def main():
    en, cv = J(DERIVED, "enums.json"), J(DERIVED, "convergence.json")
    meta, mon = J(DERIVED, "meta_facts.json"), J(MANUAL, "monitoring.json")
    CL = claims.load()[0]
    SELF = []           # numbers carried as quotations of this page's own committed text

    def sq(shown):
        SELF.append(shown)
        return live.was(THEN, PAGE, shown)

    def pin(text):
        return claims.resolve(CL, text, {})[0]

    ctd_rows = f"{en['ctd']['rows'] / 1e6:.1f}M"
    kemi_rows = en["kemi"]["rows"]
    clock_pct = en["kemi"]["nonblank"]["Startklok"] / kemi_rows * 100
    sonde_pct = en["ctd"]["categorical"]["SondeNr"]["999"] / en["ctd"]["rows"] * 100
    unc = [k["uncertainty_pct"] for k in mon["overflow_reporting"]["knowledge_levels"]
           if k["uncertainty_pct"] is not None]
    dyreenhed = pin("{count:BEK931-2024:dyreenhed}")
    n170 = pin("{read:BEK931-2024:170|divideret med 170 kg}")
    n230 = pin("{read:BEK931-2024:230|230 kg kvælstof}")

    text = f"""# What is known, by whom

This project used to be headed *"What Denmark knows about its own coastal water."* That
was a claim we were not entitled to make, and this page is why.

We can characterise **what is in the data we fetched**. That is a different object from
what Denmark knows, and the difference is a whole quadrant wide.

---

## The four quadrants, and which one is dangerous

| | we know we have it | we don't know we have it |
|---|---|---|
| **it exists** | **known known** — the {ctd_rows} CTD measurements, and everything computed from them | **UNKNOWN KNOWN** — data that exists, is held by someone, and is absent from our map |
| **we know it's missing** | **known unknown** — the {meta['gated_sources']} gated sources in [If you have data access we don't](IF_YOU_HAVE_THE_DATA.md), {meta['gated_slots']} of them with a slot the analysis is already written against | **unknown unknown** — measurements nobody makes and nobody has thought to want |

**The unknown known is the dangerous one**, because it is indistinguishable from
absence when you are inside the archive. And we have three demonstrations from a single
day of work:

- `ctd.csv.gz` carries **{meta['ctd_parameters']} distinct `Parameter` values**, including **Turbiditet** and
  **FDOM**. This project built its analysis on **nine**. Turbidity and coloured
  dissolved organic matter are directly relevant to hypotheses we had marked as needing
  new measurement.
- The ODA topic tree holds **Ålegræs plante** ({sq('**Ålegræs plante** (@@ stations, 1970–2026), **makroalge**')} stations, 1970–2026), **makroalge**
  and **bundfauna**. None is in the fetch script. Three one-line entries.
- `HYPOTHESES.md` called EU trawling effort *"the single most important missing layer in
  this whole register."* It is **{sq('register."* It is **@@, CC BY 4.0**,')}, `CC BY 4.0`**, and covers {sq('and covers @@ of our')} of our {sq('of our @@ stations. - **Denmark')}
  stations.
- **Denmark wrote a national standard method for sediment sulphide front, sulphide
  buffer capacity, oxidised iron and iron-bound phosphorus** — NOVA teknisk anvisning
  kap. 14 (1998) — **ran it from 1998 to 2003, and discontinued it.** The register said
  no iron speciation existed for any Danish site. That is wrong for 1998–2003 and right
  for everything since. A measurement programme that existed and stopped is a fifth kind
  of unknown known, and the hardest to find, because nothing in the current archive
  records that it ever ran.

None of those was hidden. All three were simply not looked for. **So any sentence in
this project of the form "Denmark does not measure X" should be read as "X is not in
what we fetched"** — and the two are not the same claim.

---

## What the discovery rate tells you

**A known unknown can be priced. An unknown known cannot** — by construction, since
you would have to know it to count it. So there is only one estimator of its size: **the
rate at which you keep finding them.**

Ours, in a single day: turbidity and CDOM sitting in a file we held; three ODA topics a
line apart; a {sq('apart; a @@ public layer')} public layer we called the most important missing one; a clock-time
field recorded twice in our own notes; a national sediment programme that ran for five
years and stopped; and a paper whose measured estuary series refuted a claim we had
already published. **Six.** Nothing about that rate suggests we are near the end of them.

### The rate, measured a second time

A day later, the estimator was run again by accident — one fetch and one audit — and it
came back higher, not lower:

| | what it was | where it had been the whole time |
|---|---|---|
| **A clock on every row** | this project said *no row in the archive carries a clock time* and built a whole class of *unscoreable* on it | `Startklok`, on **{clock_pct:.1f}% of {kemi_rows:,}** water-chemistry rows. The claim was true of the CTD extract and inferred from a topic **nobody had fetched** |
| **The topic itself** | nine hypotheses were blocked on it for months | named in `fetch_oda.py`'s own docstring and missing from its `TOPICS` dict. No credential we lacked. One dict entry |
| **Two units in one column** | averages taken across them | **{sq('them | **14 of @@7 parameters**. `Orthophosphat` is')} of {meta['kemi_parameters']} parameters**. `Orthophosphat` is {sq('parameters**. `Orthophosphat` is @@ of its rows')} of its rows a thousandfold from the rest; integrated primary production splits between per-area and per-volume, which cannot be reconciled at all |
| **The flood sheets are photographs** | registered by correlating against water polygons, at {cv['stated_error_min_m']:.0f}–{cv['stated_error_max_m']:.0f} m | they carry an **orthophoto basemap** — buildings, streets, Rådhuspladsen's fountain. The signal was thrown away and the weakest cue kept |
| **Grid north is not north** | *"every sheet has north up (the north arrow confirms it)"* | meridian convergence of **{cv['gamma_min_deg']:.2f}–{cv['gamma_max_deg']:.2f}°**, displacing corners **{cv['shift_min_m']:.0f}–{cv['shift_max_m']:.0f} m** — {cv['shift_over_error_min']:.1f} to {cv['shift_over_error_max']:.1f} times the registration error the pipeline reports for itself |
| **Censoring with no name** | read as measurements | `ResultatAttribut` = `<` on **{en['kemi']['categorical']['ResultatAttribut']['<']:,} rows**, where the value is the *detection limit*; `SigtTilBund` on {sq('`SigtTilBund` on @@ Secchi readings')} Secchi readings that hit the bottom |
| **Sentinels, undeclared** | averaged | `9999999` for a missing intercept, depth `99` on {sq('depth `99` on @@ rows, 2300 m')} rows, {sq('on 4,332 rows, @@ of water in')} of water in a {sq('water in a @@ trench, 90,972% oxygen')} trench, {sq('m trench, @@ oxygen saturation')} oxygen saturation |
| **The regulatory unit is void** | a headline figure framed on DE/ha | `dyreenhed` occurs **{dyreenhed} times** in BEK 931/2024. The binding rule is {n170} kg N/ha, and the {n230} kg derogation lapsed in 2024 |
| **A national drainage map** | *"drained areas are not mapped"* | mapped for Miljøstyrelsen at {sq('mapped for Miljøstyrelsen at @@, 52% of agricultural')}, {sq('@@ of agricultural land, published')} of agricultural land, published in a report we had not read |
| **One column, three meanings** | one guard written for all of them | `KorrektionsFaktor` is a Winkler calibration for oxygen, a biological rescale for fluorescence — where large values are *correct* — and undocumented for temperature |

**Ten, and worse than the first six**, because most are not things Denmark failed to
publish. They are properties of files we already held and had already analysed. The
first day's discoveries were about the edge of the archive; these were about its middle.

**The rate did not fall. That is the whole measurement.** Two samples is not a trend,
but nothing here supports the belief that a second pass exhausts a first pass's
blind spots, and the second pass was not even looking — it was fetching one topic and
counting distinct values in columns.

### A sixth kind: the unknown known in your own output

One of the day's findings does not fit the quadrants, because it is not about Denmark's
data at all. Three scripts read a georeferencing that had been corrected; none was
rerun; and every flood figure on this site was computed from a superseded placement of
one sheet for two days. The number moved — {sq('number moved — @@ to 5.847 km²,')} to {sq('@@ km², and a headline proximity')} km², and a headline proximity
share from {sq('proximity share from @@ to 50.1%, which')} to {sq('@@, which crosses from')}, which crosses from *most* to *half*.

What kept it stale is the part worth generalising. The tool that checks generated
documents reported that regenerating would *"remove {sq('would *"remove @@ substantial lines"*')} substantial lines"* — which reads
as **your prose is about to be destroyed**. All ten were lines whose numbers had changed
and which the regeneration replaced. A guard against losing work had become the reason
not to update, because *this output is stale* and *you are about to lose something* came
out in the same words, and the cautious response to the second is the wrong response to
the first.

**So the quadrants need a row for your own artefacts.** A derived number is held data
too, it goes stale silently, and nothing in the archive tells you. The fix that
generalises is not vigilance: it is making the tool distinguish a replaced line from a
lost one, which it now does.

### What was built in response

[CLAIMS.md](CLAIMS.md) is the structural half of the answer to this page. Every
substantive claim is registered with the graph of what it stands on, and the node shapes
distinguish a measurement from a gap from a simulation from a stipulation — so a
sentence that reads like a measurement and is actually a bound under two assumptions
shows it. The graph is checked for cycles, because a cycle is circular reasoning made
mechanical. That does not find unknown knowns. It does stop a claim from quietly
outliving the thing it rested on.

### The residual-growth test, turned on ourselves

This project's method 6 says: move a part `P` out of a leftover, and the arithmetic
must give `R_new = R_old − P`. If it doesn't shrink, the leftover was absorbing model
error and was never a partition.

Apply it to *"what Denmark does not measure."* Each discovery moved a part out. Did the
leftover shrink by that part? **No — it grew.** Finding a thing you should have known
raises your estimate of what else you have missed; it does not lower it. A leftover that
behaves that way was never a partition of the world. It was absorbing our own ignorance,
and reporting it as a property of Denmark.

### Absence of evidence, priced

*"We looked and found nothing"* supports *"there is nothing"* exactly as far as
**P(not found | it exists)** is small. That probability is the sensitivity of the
search, and nobody states it — including us, until now.

Ours was poor: six known-positives missed in one day. So the inference was never
licensed, whatever the topic. This is the null-discipline rule in a different costume —
**you do not quote a search's sensitivity, you measure it** — and it has the same fix.

> **Calibrate the search with known positives.** Seed it with things you already know
> exist and count how many come back. That detection rate is the null for every absence
> claim built on it. Without it, "not measured" means "not found by an uncharacterised
> procedure", which supports nothing.

### The two failure modes are symmetric

| | reading | today's cases |
|---|---|---|
| **absence → absence** | "we didn't find it" ⇒ "it isn't there" | the six above, and all ten of the second day — of which *"no row carries a clock time"* is the purest: a property of one unfetched topic, reported as a property of the archive |
| **presence → evidence** | "there is a column" ⇒ "there is a measurement" | `hz` on {sq('is a measurement" | `hz` on @@')} of {sq('@@ water bodies, built')} water bodies, built from freshwater points; {sq('freshwater points; @@ of six')} of six plankton fields that is one field relabelled |

The second is worse, because it *adds* confidence — class 7, and the reason that class is
separate. But they share a root: **treating the shape of a search result as a property of
the world.**

---

## The same map, from three vantage points

The quadrants are not a property of the data. They are a property of who is standing
where.

### The Danish authority (DCE, Miljøstyrelsen)

Most of our unknown knowns are their known knowns. But they have their own, and the
project has found some:

- **`SondeNr` arrives as `999` on {sonde_pct:.1f}% of rows.** The probe number exists at the point
  of measurement — somebody held that instrument. It is lost between the ship and the
  archive, not absent from the world. *This page said {sq('@@ of rows.** The probe')} until its numbers were
  checked: that was a sample of the extract, and the full count says otherwise.*
- **Time of day is absent from the CTD extract** — `Dato` is `YYYYMMDD` in all {ctd_rows}
  rows, and every field sheet had one. *Within an hour of publishing this page a fourth
  unknown known surfaced, and it was partly ours: the topic enumeration records marine
  water chemistry (`Emne_10_11`) as carrying `Startdato + Startklok`, twice, and we have
  never fetched it.*
- **The 1999 norm change and the 2012 harvest-method change are documented in DCE's own
  reports** — and do not travel downstream as uncertainty on the numbers they moved.

Their known unknowns are stated openly and honestly, which deserves saying: retention
carries {sq('retention carries @@ percentage points,')} percentage points, component uncertainties run {min(unc)}–{max(unc)}%, and the estimator
is described in the literature as returning meaningless negative values in dry years.

### Us

Our known knowns are narrow and well characterised. Our known unknowns are now
enumerated. **Our unknown knowns are unbounded and we cannot estimate them** — the three
above were found by accident, in one day, and there is no reason to think that rate has
stopped.

The one thing we have that the authority structurally lacks: **no obligation to produce
a number.** An unscoreable hypothesis can be left unscoreable here.

### Other connectors

- **Utilities** hold measured overflow where the national account holds modelled volume.
- **ICES, HELCOM, EMODnet, Copernicus** hold effort, wave and optical layers that are
  open and unfetched.
- **Farmers** hold actual application records where the balance holds norm coefficients.
- **Universities** hold cores, incubations and porewater profiles for mechanisms this
  project has had to mark as needing an experiment.

For each, the relationship is asymmetric in the useful direction: **their known known is
our unknown known**, and one email closes it.

---

## What follows for the headline

"What Denmark knows about its own coastal water" is an estimate **we** made, of the
known-known quadrant only, from one vantage point, using data we fetched ourselves. It
is a finding of this project, and a contestable one — not its title.

The page now leads with what it is: an audit of a record, by someone outside the
institutions that produced it, with the method stated so the conclusions can be
checked. The knowledge claim sits below, labelled as ours.

That is the same discipline applied everywhere else here. A count is a construction
before it is a fact; so is a headline.

---

*Generated by `scripts/pages/known_and_unknown.py`. Figures that describe what an
earlier stage of the work found are quoted from this page as it was first published.*
"""
    write_doc(OUT, text)
    log(f"wrote {os.path.relpath(OUT, ROOT)} - {len(SELF)} number(s) carried as self-quotation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
