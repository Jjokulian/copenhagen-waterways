# What is known, by whom

This project used to be headed *"What Denmark knows about its own coastal water."* That
was a claim we were not entitled to make, and this page is why.

We can characterise **what is in the data we fetched**. That is a different object from
what Denmark knows, and the difference is a whole quadrant wide.

---

## The four quadrants, and which one is dangerous

| | we know we have it | we don't know we have it |
|---|---|---|
| **it exists** | **known known** — the 53.7M CTD measurements, and everything computed from them | **UNKNOWN KNOWN** — data that exists, is held by someone, and is absent from our map |
| **we know it's missing** | **known unknown** — the eight gated items in [If you have data access we don't](IF_YOU_HAVE_THE_DATA.md) | **unknown unknown** — measurements nobody makes and nobody has thought to want |

**The unknown known is the dangerous one**, because it is indistinguishable from
absence when you are inside the archive. And we have three demonstrations from a single
day of work:

- `ctd.csv.gz` carries **17 distinct `Parameter` values**, including **Turbiditet** and
  **FDOM**. This project built its analysis on **nine**. Turbidity and coloured
  dissolved organic matter are directly relevant to hypotheses we had marked as needing
  new measurement.
- The ODA topic tree holds **Ålegræs plante** (1,990 stations, 1970–2026), **makroalge**
  and **bundfauna**. None is in the fetch script. Three one-line entries.
- `HYPOTHESES.md` called EU trawling effort *"the single most important missing layer in
  this whole register."* It is **23.1 MB, CC BY 4.0**, and covers 1,392 of our 1,415
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
line apart; a 23 MB public layer we called the most important missing one; a clock-time
field recorded twice in our own notes; a national sediment programme that ran for five
years and stopped; and a paper whose measured estuary series refuted a claim we had
already published. **Six.** Nothing about that rate suggests we are near the end of them.

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
| **absence → absence** | "we didn't find it" ⇒ "it isn't there" | the six above |
| **presence → evidence** | "there is a column" ⇒ "there is a measurement" | `hz` on 66 of 123 water bodies, built from freshwater points; 24 GB of six plankton fields that is one field relabelled |

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

- **`SondeNr` arrives as `999` on 83.5% of rows.** The probe number exists at the point
  of measurement — somebody held that instrument. It is lost between the ship and the
  archive, not absent from the world.
- **Time of day is absent from the CTD extract** — `Dato` is `YYYYMMDD` in all 53.7M
  rows, and every field sheet had one. *Within an hour of publishing this page a fourth
  unknown known surfaced, and it was partly ours: the topic enumeration records marine
  water chemistry (`Emne_10_11`) as carrying `Startdato + Startklok`, twice, and we have
  never fetched it.*
- **The 1999 norm change and the 2012 harvest-method change are documented in DCE's own
  reports** — and do not travel downstream as uncertainty on the numbers they moved.

Their known unknowns are stated openly and honestly, which deserves saying: retention
carries ±6–27 percentage points, component uncertainties run 30–135%, and the estimator
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
