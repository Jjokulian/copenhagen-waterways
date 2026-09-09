# Fingerprinting Denmark

**The experiment that would end the argument, written so that both sides can commit to
it before it runs.**

Everything else on this site is an audit: it takes numbers that exist and asks what
they are estimators of. This page is the opposite. It is a design for producing
numbers that do not exist yet, aimed at the one question the whole dispute turns on
and nobody has ever measured directly:

> **When Danish fields receive slurry and then rain, what reaches the water — and
> whose is it?**

[SENSING.md](SENSING.md) constructs the instrument: the fingerprint that separates a
pig from a person from a road, and the two-tier network that could carry it.
[`X23`](EXPERIMENTS.md) is the entry in the register. **This page is the protocol** —
what is claimed, what would refute it, how many catchments and how many storms, and
the rules that have to be fixed before the first sampler is bolted to a culvert.

---

## 1. The three hypotheses, stated so they can lose

The point of writing them out is that each makes a different prediction about the same
measurements, so the data can pick.

| | Claim | Predicts |
|---|---|---|
| **H1 — the soil reactor** | The field consumes the payload. Labile carbon is respired, ammonium nitrifies, and what leaves is mobile nitrate | Faecal markers stay near baseline through the spreading window. Nitrate rises seasonally, smoothly, with drainage. No relationship between marker peaks and livestock density |
| **H2 — the bypass** | Preferential flow, tile drains and rain onto fresh slurry deliver the payload close to intact | Marker and copper peaks within days of spreading, **scaling with livestock density**, concentrated in the rising limb of storms |
| **H3 — the regime** | Both are true, in different conditions. The bypass opens only when the ground is frozen, saturated or tile-drained, and closes otherwise | Marker peaks appear at **some** sites and not others, predicted by soil type, drainage and antecedent wetness rather than by livestock density alone |

**H1 is the outcome that would embarrass this project**, since much of its argument
leans on the payload mattering. It is stated first on purpose, and the publication rule
below is written so that it cannot be quietly dropped.

---

## 2. What the calendar does for us

The manipulation already exists and is applied nationally: Danish rules forbid
spreading through the autumn and winter and open a window in spring. So the experiment
is **before-after on a fixed national schedule**, with a within-year control window
that needs no permission from anyone.

And the events can be counted in advance. From the 31-year hourly rainfall record used
elsewhere in this project, over Copenhagen, February–April:

| | Median days per season | Range |
|---|---:|---:|
| ≥ 2 mm in a day | **21** | 11–35 |
| ≥ 5 mm in a day | **9** | 2–15 |
| ≥ 10 mm in a day | **2** | 0–5 |

**That is the sample size, and it is the reason the design works.** A sampler on a
five-millimetre trigger catches something like nine events in a spreading season and a
comparable number in the autumn control window — enough for a paired comparison within
a single year, at a single site, without waiting a decade. *Caveat carried from the
source:* a reanalysis grid cell understates extremes, so the ≥10 mm row is a floor.

---

## 3. The design

**Paired catchments, matched on everything except the thing under test.**

- **12 pairs** — 24 catchments — matched on soil type, drainage class, area and slope,
  contrasted on **livestock density** from the national register. Small headwater
  catchments, so a signal is not diluted to nothing before it reaches the sensor.
- **Both tiers at every site**: continuous stage, turbidity, conductivity, temperature
  and fDOM; an autosampler on a flow-and-turbidity trigger.
- **Two windows a year**: the spreading window (February–April) and an autumn control
  window when spreading is forbidden. Same sites, same triggers, same laboratory.
- **End members sampled directly**: slurry from the tanks in each catchment, effluent
  from any plant in it, road gully sediment, and soil. **No conversion ratio is taken
  from the literature** — every one is measured on the material that is actually there.
- **Two full years.** One to establish the ratios and shake out the fouling, one to
  answer the question.

**What is analysed per event:** faecal sterols with the herbivore ratio,
host-specific microbial markers, crAssphage, acesulfame, one veterinary residue,
copper and zinc, COD and BOD, total and dissolved N and P, and δ¹⁵N with δ¹⁸O of
nitrate. Discharge at the same minute, or it is a concentration and not a load.

---

## 4. The decision rules, fixed before the first sample

These are the whole point of the page. A rule written afterwards is a story.

1. **H2 is accepted** if faecal-marker load in the spreading window exceeds the autumn
   control window by a factor stated in advance at **two thirds or more of the
   high-density sites**, and the effect scales with livestock density across the
   twelve pairs.
2. **H1 is accepted** if marker loads in the two windows are indistinguishable at the
   great majority of sites and nitrate is the only determinand that moves.
3. **H3 is accepted** if the effect is present at some sites and absent at others *and*
   is predicted by soil, drainage or antecedent wetness better than by density.
4. **The result is published whichever way it falls**, in full, with the raw series —
   and the pre-registration says so before the money is spent. **If H1 wins, this
   project's own emphasis was wrong and the page saying so will carry that sentence.**
5. **No composite index is reported without the series it came from**, and no residual
   is named after a source. That is the failure this whole site documents; reproducing
   it here would be unforgivable.

---

## 5. What would invalidate the experiment rather than answer it

Written down in advance, because each of these has ruined a monitoring programme
somewhere:

- **Fouled sensors reading confidently.** Servicing schedule and co-location against a
  reference instrument, or the continuous tier is decoration. This is [`X16`](EXPERIMENTS.md).
- **Decayed DNA.** Microbial markers fall away in days, so a marker absence at a site
  visited late is not evidence of absence. The sterols, which persist, are the check.
- **Unmeasured end members.** If the slurry in *these* tanks was never sampled, every
  fraction is a guess with a decimal point on it.
- **Storm-chasing bias.** Triggers are set in advance and left alone. An operator who
  decides which storms are interesting has destroyed the sample.
- **Catchments matched on the wrong thing.** If the high-density catchments are also
  the sandy ones, the design has confounded exactly what it set out to separate — and
  the pairing has to be published so somebody else can say so.

---

## 6. What it costs, and how it could be built

From the bill of materials in [SENSING.md](SENSING.md), at stated prices rather than
quotations:

| Phase | What | Stated cost |
|---|---|---:|
| **Pilot** — one season, 3 pairs | 6 nodes with fDOM, 2 samplers, ~60 bottles | **~0.4–0.6 M DKK** |
| **The experiment** — 2 years, 12 pairs | 24 nodes, 8 samplers, ~600 bottles, servicing | **~3–5 M DKK** |
| **The standing network afterwards** | a node on every outlet that reaches the sea | ~8.8 M DKK of hardware |

**The pilot is inside the reach of a foundation, a university department, or a
crowdfunded association.** The full experiment is the cost of one junction rebuild. The
comparison that matters is not to a research budget: it is to a national nitrogen
programme costing orders of magnitude more and producing **no test**.

---

### The number, put beside things that are not science

Because the figure is easy to lose next to a research budget, here it is next to
things people actually price:

| | Stated cost |
|---|---:|
| The **pilot** — three pairs, one season | ~0.5 M DKK, the price of a small flat outside the cities |
| The **experiment that settles it** — 12 pairs, two years | **3–5 M DKK, the price of a cheap house** |
| The **standing national network**, hardware | ~8.8 M DKK |
| One bored street shot, from the retrofit costing on this site | 0.16–0.64 M DKK |

**So the decisive experiment costs about what a house costs, and the capital for a
national network costs about what a good house in Copenhagen costs.** That is the
honest headline and it should be uncomfortable: the argument has run for forty years,
and the measurement that would settle a central part of it has never been bought at a
price a single wealthy person could pay.

**But do not mistake the capital for the programme.** Hardware is the cheap half and
saying otherwise is how these schemes die:

- **Servicing.** 800 nodes at four visits a year is on the order of **3–4 M DKK a
  year** — which is to say two to four people, permanently. A sensor that nobody
  visits produces confident wrong numbers, which is worse than no sensor.
- **Laboratory.** The tier-2 bottles at 1,500–4,000 DKK each are the largest single
  line in the experiment budget, and the only one that cannot be economised without
  losing the attribution.
- **Custody.** Somebody has to keep the archive, the calibration histories and the
  pre-registration for a decade, and that is a job rather than a server.

So: **a house to find out, and a few salaries a year to keep knowing.** The first
number is startlingly small. The second is the one a proposal has to be honest about,
because it is the one that gets cut in year three and takes the series with it.

### And the whole of it?

This page prices one question. The obvious next one is what it would cost to settle
the *field* — not the faecal channel alone, but enough of the twenty-three designs in
[EXPERIMENTS.md](EXPERIMENTS.md) to leave the Danish sea argument with measurements
where it currently has models. Adding up what this project has actually costed, and
marking clearly what it has not:

| Block | What it buys | Stated cost |
|---|---|---:|
| **This experiment** | whether the payload reaches the water, and whose it is | 3–5 M |
| **The standing stream network** | the same question everywhere, permanently, no extrapolation | 8.8 M hardware |
| **Instrumenting the 13 largest overflow structures** | flow rather than event counts — the largest single uncertainty on this site | ~1 M |
| **The cheap marine tier** — `X14`, `X15`, `X16` | oxygen and temperature at many points instead of monthly at few | 1–3 M |
| **The missing instruments** — `X19`, `X20` | a *fedtemøg* index and a structured record of what people have watched for forty years. Three of the four public words have no instrument; these are two of them | small — a panel and a protocol |
| **The desk work** — `X8`, `X21`, `X22` | analyses on data that already exists and has never been run | **nothing but time** |
| **A trials portfolio** — the meta-solution in [PROGRAMME.md](PROGRAMME.md) | whether the interventions work, in named places, reversibly | 6–24 M |

**Capital, in the order of 20–40 M DKK.** Which is a large villa, or a small apartment
building, or about one kilometre of urban motorway — and it is *not* the same as an
upper-middle-class house: that figure buys the decisive single experiment, not the
programme. Plus **5–10 M a year** to service, sample and keep custody, which is the
number that decides whether any of it survives to be a time series.

**And three honest deductions from that total.**

- **Ship time is not in it.** The autumn benthic extension and anything offshore needs
  a vessel and an institution, and this project cannot price either.
- **Some of it cannot be bought at all.** Forty of the 166 mechanisms in the register
  are unscoreable because the deciding measurement has no column anywhere; money buys
  the instrument, not the decades of record it should have been collecting.
- **And the cheapest block is the one nobody has done.** Three designs need no
  fieldwork and no funding — the data exists and the analysis has never been run. If
  the argument is that this is all too expensive, that block is the counter-example
  sitting in the open.

---

## 7. Who could do which part

| | Can do |
|---|---|
| **One person with a culvert and a soldering iron** | A node, a year of a real series from one stream, and the demonstration that it works |
| **A local association or a school** | A pair — one high-density catchment and its match — which is a whole experiment in miniature |
| **A municipality or a water utility** | The samplers and the laboratory line, which is the half that needs an institution |
| **A university group** | The end-member sampling and the isotope work, and the pre-registration that makes the rest admissible |
| **Anyone at all** | Hold the pre-registration to its publication rule when the result is inconvenient |

**Nothing above needs a change in the law, a data agreement, or anybody's permission
except the landowner's at each culvert.** That is unusual in this field and it is the
reason this page exists.

---

## 8. What it settles, and what it does not

**Settles.** Whether the payload reaches the water, in what quantity, in what season,
under what conditions, and whose it is — measured rather than modelled, at the point
where inland water becomes coastal water. Whether the spreading calendar is visible in
a stream. Whether the account's single channel is missing a second one, and by roughly
how much.

**Does not settle.** What the arriving material then does in the sea: that is the next
experiment and it is harder. Nor anything about constituents outside the analysed list.
Nor the marine oxygen question, which has [its own designs](EXPERIMENTS.md).

> **Why it would end the argument rather than extend it.** Every disputed number in
> Danish nutrient policy is a modelled quantity defended by the people who model it.
> This produces a measured quantity, at named places, on dates, with the raw series
> published and the decision rule fixed in advance — so the result is available to
> somebody who does not trust either party. **That is the only kind of number that
> ends a forty-year disagreement**, and the striking thing is how cheap it is.
