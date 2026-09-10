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
| **we know it's missing** | **known unknown** — the 89 gated sources in [If you have data access we don't](IF_YOU_HAVE_THE_DATA.md), 10 of them with a slot the analysis is already written against | **unknown unknown** — measurements nobody makes and nobody has thought to want |

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

### The rate, measured a second time

A day later, the estimator was run again by accident — one fetch and one audit — and it
came back higher, not lower:

| | what it was | where it had been the whole time |
|---|---|---|
| **A clock on every row** | this project said *no row in the archive carries a clock time* and built a whole class of *unscoreable* on it | `Startklok`, on **100.0% of 1,805,827** water-chemistry rows. The claim was true of the CTD extract and inferred from a topic **nobody had fetched** |
| **The topic itself** | nine hypotheses were blocked on it for months | named in `fetch_oda.py`'s own docstring and missing from its `TOPICS` dict. No credential we lacked. One dict entry |
| **Two units in one column** | averages taken across them | **14 of 147 parameters**. `Orthophosphat` is 38% of its rows a thousandfold from the rest; integrated primary production splits between per-area and per-volume, which cannot be reconciled at all |
| **The flood sheets are photographs** | registered by correlating against water polygons, at 14–91 m | they carry an **orthophoto basemap** — buildings, streets, Rådhuspladsen's fountain. The signal was thrown away and the weakest cue kept |
| **Grid north is not north** | *"every sheet has north up (the north arrow confirms it)"* | meridian convergence of **2.90–2.98°**, displacing corners **94–350 m** — four to ten times the registration error the pipeline reports for itself |
| **Censoring with no name** | read as measurements | `ResultatAttribut` = `<` on **85,035 rows**, where the value is the *detection limit*; `SigtTilBund` on 26,380 Secchi readings that hit the bottom |
| **Sentinels, undeclared** | averaged | `9999999` for a missing intercept, depth `99` on 4,332 rows, 2300 m of water in a 50 m trench, 90,972% oxygen saturation |
| **The regulatory unit is void** | a headline figure framed on DE/ha | `dyreenhed` occurs **zero times** in BEK 931/2024. The binding rule is 170 kg N/ha, and the 230 kg derogation lapsed in 2024 |
| **A national drainage map** | *"drained areas are not mapped"* | mapped for Miljøstyrelsen at 30.4 m, 52% of agricultural land, published in a report we had not read |
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
one sheet for two days. The number moved — 5.932 to 5.847 km², and a headline proximity
share from 53.5% to 50.1%, which crosses from *most* to *half*.

What kept it stale is the part worth generalising. The tool that checks generated
documents reported that regenerating would *"remove 10 substantial lines"* — which reads
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
