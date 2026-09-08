# The order of work

Seven stages, in order, each with a gate that must be passed before the next one means
anything. This page exists because the project drifted: a great deal of method was
built at stage 3 and stage 4 was never started, and without the order written down
that is invisible.

**Status is marked honestly, including where it is bad.**

| | stage | gate | status |
|---|---|---|---|
| 1 | Hypothesis landscape | broad enough that no test is a two-horse race | **done, with a stated flaw** |
| 2 | Data sources | provenance separated; independence counted | **done** |
| 3 | The view, held open | no basket assumed; destruction stated | **partly** |
| 4 | Testing hypotheses against data | each has an observable consequence and a null | **not started** |
| 5 | Mechanistic scoring | stability across independent measure-spaces | **not started** |
| 6 | Solution in its own spatiality | the unit follows the mechanism | **premature** |
| 7 | Relation to the social argument | claims in circulation, and what would move them | **partly** |

---

## 1. Hypothesis landscape — done, with a stated flaw

**182 mechanisms in 17 groups** ([HYPOTHESES.md](HYPOTHESES.md)).

**What "satisfactorily" means here.** Not exhaustive — the page says so in its first
heading, and there is no way to know how far off it is. The requirement is weaker and
achievable: *broad enough that no test is a contest between two candidates one of which
was chosen in advance.* A hypothesis scored against "nothing" is scored against a
strawman; it has to be scored against rivals that could actually win.

**The stated flaw.** The 17 groups are **our own untested partition**. Same error the
rest of the project audits, committed on our own list. The grouping has never been run
through a complement test, and it should be before stage 5 uses it.

**Gate:** passed. Enough rivals exist that stage 4 is a real contest.

---

## 2. Data sources — done

Fetched, with provenance separated rather than pooled:

- **ODA**: 53.7 M CTD measurements, 47 years, plus secchi, lys, maaledybde
- **CMEMS**: 6 indicators — **only 3 are independent** of national collection; the
  other 3 are reanalysis or in-situ TAC, i.e. the same Danish data wearing a European
  label. Counted as 3, not 6.
- **GEUS Jupiter**, OSM coastline, national geodata

**Independence is the quantity that matters, not volume.** Nine CTD channels are three
sensors: salinity is computed from conductivity and temperature, oxygen saturation from
oxygen, temperature and salinity. Genuinely independent production paths available
today: **CTD, satellite ocean colour, Secchi disc — three.**

**Missing and blocking:** ODA `vandkemi` (nitrogen and phosphorus). It is the one
variable the whole comparison needs and the one the viewer cannot show.

**Gate:** passed, except that stage 4 cannot test nutrient hypotheses without vandkemi.

---

## 3. The view, held open — partly

The point of this stage is to make the data usable *without* committing to anyone's
categories, so that stage 4 can test a hypothesis rather than inherit a model.

**Done.** [stations.html](stations.html) — every station-month at its own position,
nothing aggregated into a water body, nothing interpolated. Water bodies are an
optional overlay labelled as model. Interpolation is a reader control with a live count
of how many cells it invented. Outliers are ringed, not removed.

**Not done.** The measurement-level store: depth, time and *station identity* as
questions rather than columns. Our own pipeline still destroys at roughly **3,900:1** —
depth 896 values to 2 bins, day to month, casts to one median, instrument dropped. The
store that removes it is about **800 MB**, which the machine can hold. That is a
choice we made for convenience and have not yet unmade.

**Gate:** partly passed. Stage 4 can proceed on the collapsed view for hypotheses that
do not depend on depth, sub-monthly time, or within-station position. It cannot for the
others, and those must be marked rather than tested badly.

---

## 4. Testing hypotheses against the data — NOT STARTED

**This is the gap.** Everything built so far tests *the basketing*, not any hypothesis.
Feature-subspace stability, the complement test, the four null corrections — all of it
establishes what the units are and whether a partition means anything. None of it has
been pointed at a mechanism.

Each hypothesis needs three things before it can be tested, and most will fail at one:

1. **An observable consequence.** Not "X contributes to Y" but "if X, then this
   measurable quantity behaves this way and not that way."
2. **A source that carries it.** Named, with its error class ([the taxonomy](https://github.com/Jjokulian/statistical-methods#7b-rate-a-data-stream-by-the-errors-it-can-contain)).
3. **A null under the constraint actually imposed** — not the statistic's nominal null.
   Four separate times in this project the quoted null was wrong, once in the direction
   that favoured our own finding.

**The triage that has to happen first**, and it is most of the work:

- **testable now** — consequence, source and null all available
- **testable with vandkemi** — blocked on one fetch
- **testable only at measurement resolution** — blocked on stage 3's remaining half
- **unscoreable** — the deciding dimension has no column and never did. *Time of day is
  the worked example: oxygen swings diurnally, daylight at 55°N runs 7 to 17 hours, and
  no row in the archive carries a clock time.* These get marked **unscoreable**, not
  scored zero. An absent dimension is not evidence of absence.

**Gate:** stage 5 is meaningless until this triage exists.

---

## 5. Mechanistic scoring — NOT STARTED

"Mechanistic" is doing real work in that phrase. It does not mean *is there a
correlation*. It means: **does the mechanism's signature survive a change of
measure-space?**

A mechanism is a relation that holds when other things change. So the score is
invariance, not fit — and the machinery is already built and validated:

- the method **recovered Henry's law unprompted** from station data pointed at a
  different question, and kept recovering it after every derived channel was removed.
  That is a positive control on ground truth in the same dataset.
- the same method, same run, found the official water bodies add **nothing** beyond
  being connected regions of their size.

A detector with demonstrated sensitivity that returns a null is informative. That is
what makes stage 5 possible at all.

**Each hypothesis gets, and none of the five is droppable:**

> a stability coefficient · at a stated level of organisation · against a stated null ·
> for a named functional · at a stated point in the accumulation of measure-spaces

Drop any one and it is a verdict, which is a different kind of object than this
procedure can produce.

**And it never terminates.** Each new independently-produced measure-space is another
trial, so the score carries a time index and has no final value. Three environments
today; satellite and Secchi are fetched and unused; the 17% of measurements carrying a
named instrument are up to 34 more.

---

## 6. Solution in its own spatiality — PREMATURE

The requirement, and it is the reason this stage cannot be borrowed:

> **The unit follows the mechanism.** Not water bodies. Not municipalities. Not
> Denmark.

Every one of those is a model boundary that failed or was never tested. Water bodies
add nothing beyond contiguity by our own measurement. "Denmark" as the unit for a
marine account presupposes a closed system across which nitrogen visibly moves — the
same missing denominator, at national scale.

So the geometry of the answer is whatever the surviving mechanism has:

- if it is catchment-scale, the unit is the catchment
- if it is a shoreline gradient, the unit is distance from shore
- if it is residence time, the unit is exchange time and the map is not a map
- if it is sediment memory, the unit is depositional history and the axis is depth

**No national totals. No per-water-body allocations. No percentage of a residual.**

[PROGRAMME.md](PROGRAMME.md) already proposes interventions and is the most developed
document here — which is precisely the drift this page records. It was written before
stages 4 and 5. It should be re-read against them when they exist, and the parts that
assume an inherited geometry marked.

---

## 7. Relation to the social argument — partly

Last, and deliberately last: what is claimed in public, what each claim rests on, and
what would move it.

**Not** an argument against opponents. No ghost references, no unnamed adversaries —
the failure mode this project has already committed and corrected once.

**Done:** [GRUNDLAGET.md](GRUNDLAGET.md) audits the foundation documents;
[POLITICS.md](POLITICS.md) the social frame; [NITROGEN.md](NITROGEN.md) establishes
that the 69.6% attribution is a residual over an area 51% modelled, not a measurement.

**Outstanding:** GRUNDLAGET's F2/F3/F4/Q4 remain unverified against primary DCE and DHI
documents, and will not be applied on a subagent's word.

**And a standing rule this stage needs, learned the hard way.** Finding one bad
argument in one document does not establish that a claim is unevidenced. The
nitrogen attribution's circular figure was found, published, and then had to be
narrowed within the hour, because DCE qualify that figure themselves on the next
page and a paired-catchment study exists that would not be circular. **Before
reporting that a link fails, ask what the strongest version of the case would be
and whether it was looked for.** The sourcing a document presents is not the only
evidence there is for what it claims.

---

## The rule that governs all seven

Any output of this project takes the form of a coefficient with its qualifiers, or a
count with its individuation rule stated. **Not a verdict.** The procedure has no
output slot shaped like one — the space of groupings and functionals is open, so
"the result is in" is not false but referentless.

Method, and the audit of which parts survive their own rules:
[statistical-methods](https://github.com/Jjokulian/statistical-methods).
