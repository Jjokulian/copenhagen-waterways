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

None of those was hidden. All three were simply not looked for. **So any sentence in
this project of the form "Denmark does not measure X" should be read as "X is not in
what we fetched"** — and the two are not the same claim.

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
- **Time of day is never recorded.** Every field sheet had one. `Dato` is `YYYYMMDD` in
  all 53.7M rows, and no column exists.
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
