# Who pays for the nitrogen requirement

*The economic incidence of Denmark's nitrogen requirement — the rules in force now and
the discharge quota coming in 2027 — computed on the open registers and on the
regulations themselves. Cohorts and distributions only: no holding is named here, and
the generator writes no identifying field.*

Two other pages on this site argue about whether the requirement is well founded.
[LANDBRUG.md](LANDBRUG.md) puts that case in Danish to the people it lands on, and
[NITROGEN.md](NITROGEN.md) takes the national figure apart. **This page assumes the
requirement and asks a different question: it is law now, so whose farm does it land
on, and which farms have nothing left to absorb it with?**

Those are separable questions, and the answer to the first is not the answer to the
second. The enterprise type under the most regulatory pressure — dairy — is also the
most solvent in the accounts that exist. The type with the worst balance sheets — beef
and other cattle — is the least pressured. And at the threshold the rules actually turn
on, most of the sector is on the exposed side of the line, so the interesting question
is not *who is exposed* but **which of the exposed have anything left**. That is a
countable set and section 6 counts it.

The single thing most worth knowing before reading further is that **the Danish rules
do not count animals.** The animal unit stopped being a regulatory unit in 2017. What
the current requirements are charged on is a *base area* of cereals, maize, rape and
pulses — and grass is not in it. That one fact reorders the whole incidence question,
and it is why a page about a nitrogen rule spends as much time on what a farm grows as
on what it keeps.

> **What this page is not.** It is not a forecast of who will go bankrupt. What is
> computed is the **buffer** — how large an annual loss of margin each cohort could
> absorb before it goes negative — expressed in kroner per hectare and per animal unit,
> so that a reader with a different cost estimate can apply their own. One published
> by-farm-type cost estimate is then laid on that ladder, read from the primary source
> and quoted with its table.

## 0. Why there are no names on this page

Every register underneath this analysis is public. Anyone can look up a CVR number,
read the filed accounts, see the animal units and the declared hectares, and work out
what this page works out for one named business in an afternoon.

This page does not do that, and the rule is not negotiable.

**Most Danish farms are natural persons.** `Enkeltmandsvirksomhed` — sole
proprietorship — is not a company with limited liability and a boardroom; it is one
human being, and the CVR register carries their name, their home address and their
telephone number, because for a sole trader those are the same thing as the
business's. Of the [16,449](SOURCES.md#F-e9673f2999) businesses keeping animals whose legal form
this project could read, [12,725](SOURCES.md#F-a998566e98) are sole proprietorships, and they hold
[65](SOURCES.md#F-a97013bbfe)% of the national herd.

Publishing *these named people are going to lose the farm* is a financial prediction
about a private individual, made from a model, in public, with their address attached.
It would be wrong even if the model were good, and the model here is a distribution
rather than a diagnosis: it can say what fraction of a cohort has no buffer left, and
it cannot say which member of that cohort is the one whose bank has already agreed a
standstill.

So everything below is a cohort with its **n** stated. A farmer reading this can find
their own holding in the distribution — that is the point of stating the deciles — and
nobody can find anyone else's.

*Where a finding would genuinely need a name to be checked, it is stated without one
and the check is named instead.* There is one such finding, in
[section 7](#7-what-this-cannot-establish-and-what-would).

## 1. What the instrument is, and what that alone tells you about incidence

Two records are needed here and they are different in kind. The *political* record —
what was agreed, by whom, and what was said about it — is collected verbatim, dated and
sourced in [POLITICS.md](POLITICS.md). The *legal* record is the regulations in force
for the current planning year, and those were read directly for this page rather than
taken from press coverage. Where a paragraph number appears below, the text was fetched
and checked.

| When | What | Status |
|---|---|---|
| 2024-06-24 | **Grøn Trepart** — the Green Tripartite agreement | aftale |
| 2024-07-31 | The **kvægundtagelse** — the cattle derogation allowing [230](SOURCES.md#F-1f4fc9abe7) kg N/ha — lapses | expiry |
| 2025-06-19 | The **braklægningspunkt** fixed: *"det maksimale reguleringstryk i de enkelte vandoplande"* | aftale |
| 2025-08-27 | The new **retentionskort** published by GEUS and Aarhus University | model output |
| 2025-12-03 | The **kvælstofaftale** — the nitrogen agreement and its distribution model | aftale |
| 2026-07-21 | **BEK 673** and **BEK 677** — the catch-crop rules for planning year 2026/2027 | gældende ret |
| 2026-09-03 | **`L 5`** passed [119–34](SOURCES.md#F-195f7fba8a), becoming **LOV nr. 759 of 2026-09-08**, the new *gødskningslov*. In force **2027-01-01** | vedtaget lov |
| 2026-09-01 | A *tillægsaftale* exempting vegetable-growing areas from the new model in 2027 | aftale |

**Glossary, because the mechanism is unreadable without it.** *Kvælstof* is nitrogen.
*Efterafgrøde* is a catch crop — sown after harvest to take up nitrogen that would
otherwise leach over winter. *Efterafgrødegrundareal* is the base area the catch-crop
requirements are charged against. *Harmoniareal* is the area a holding may spread
manure on. *Kystvandopland* is a coastal water catchment. *Retention* is the fraction
of nitrogen leaving a field that is removed before it reaches the sea. *Udtagning* is
taking land out of production. *Braklægningspunkt* is the set-aside point — the maximum
regulatory pressure a catchment may be put under. *Indsatsbehov* is the modelled size
of the reduction needed.

### The unit is not the animal. It is the base area.

The first thing to get right, because almost every summary gets it wrong: **the Danish
nitrogen rules no longer count animals.** The *dyreenhed* — animal unit — ceased to be
a regulatory unit with the reform of 2017-08-01, and the [1.4](SOURCES.md#F-8a1f2ea7e8), [1.7](SOURCES.md#F-4fb071154d) and [2.3](SOURCES.md#F-52b6a408f9) DE/ha harmony
ceilings went with it.

The date is Landbrugsstyrelsen's; what was checked here is the present tense of it. The
word `dyreenhed` occurs **zero times** in each of the three regulations that carry the
current requirements — BEK 931 of 2024-07-16 on the use of fertiliser, and BEK 673 and
BEK 677 of 2026-07-21 on catch crops — and where the old rules set a ceiling in animal
units the current one sets it in kilograms. That is not an inference from a summary; the
texts were fetched and searched.

What replaced it is four separate requirements, and the first three all key on the same
two thresholds — [30](SOURCES.md#F-67989f7136) and [80](SOURCES.md#F-0277d7c7e6) kilograms of nitrogen per hectare of *harmoniareal*, from
manure and other organic fertiliser.

| Requirement | The rule | Source |
|---|---|---|
| **Manure ceiling** | Total organic nitrogen divided by **[170](SOURCES.md#F-ccab7b1fe3) kg N/ha** may not exceed the harmoniareal. One rate, no derogation. | [BEK 931/2024 §14](https://www.retsinformation.dk/eli/lta/2024/931) |
| **Compulsory catch crops** | At least **[10.7](SOURCES.md#F-4caa16bda4)%** of the base area — but **[14.7](SOURCES.md#F-4aa7012024)%** for a holding applying **[80](SOURCES.md#F-0277d7c7e6) kg N/ha or more** | [BEK 673/2026 §4 stk. 3](https://www.retsinformation.dk/eli/lta/2026/673) |
| **Livestock catch crops** | An additional requirement, per catchment, for any holding applying **[30](SOURCES.md#F-67989f7136) kg N/ha or more**. Organic holdings are exempt from this one | BEK 673/2026 §4 stk. 4 and stk. 5, Bilag 2 |
| **Targeted catch crops** | A further percentage of the base area, **set per coastal catchment** | [BEK 677/2026 §3 stk. 2](https://www.retsinformation.dk/eli/lta/2026/677), Bilag 1 |

The statutory wording of the last one is the allocation mechanism in one sentence:

> *"Arealet med målrettede efterafgrøder skal udgøre en procentdel af den del af
> virksomhedens efterafgrødegrundareal, der er beliggende i det pågældende
> kystvandopland. Procentdelen for de enkelte kystvandoplande er fastsat i bilag 1."*
>
> *(The area of targeted catch crops shall constitute a percentage of that part of the
> holding's base area which lies in the coastal catchment in question. The percentage
> for each coastal catchment is set in Annex 1.)*

So: **a percentage, of a base area, per coastal catchment.** Not per animal, not per
kilogram of nitrogen, and — a detail that is widely misreported — **not per ID15
catchment**. The ID15 areas do two narrower jobs: a field is assigned whole to the ID15
area it most overlaps and thence to that ID15's coastal catchment (§6 stk. 2), and in
the voluntary subsidised round the ID15 retention is what ranks applications, *"[m]arker
i et ID15-område med lavere retention går forud for marker i et ID15-område med højere
retention"* ([BEK 131/2026](https://www.retsinformation.dk/eli/lta/2026/131) §6 stk. 3).

**The escape valve is priced against livestock too.** A holding may substitute a cut in
its own nitrogen quota for catch crops, and the exchange rate depends on the same
[80](SOURCES.md#F-0277d7c7e6) kg N/ha line: **[110](SOURCES.md#F-fe6cd4c3cd) kg N per hectare below it, [175](SOURCES.md#F-35790b9b7a) kg N above** (BEK 673/2026 §24
stk. 2). The alternative that lets a holding buy its way out costs a livestock holding
[59](SOURCES.md#F-e92e26652e)% more per hectare than an arable one.

**And the cattle derogation is gone.** Denmark's *kvægundtagelse* permitted [230](SOURCES.md#F-1f4fc9abe7) kg N/ha
on qualifying cattle holdings for [twenty-two years](SOURCES.md#F-bdc0d5848b). It expired on 2024-07-31 and was
not renewed, so those holdings dropped to [170](SOURCES.md#F-ccab7b1fe3) — a **[26](SOURCES.md#F-5e5441df2c)% cut in what may be spread**,
already delivered, before `L 5` was drafted. Any account of the burden on Danish dairy that
starts in 2026 has missed the largest single step.

### Two exemptions that decide a great deal

BEK 677/2026 §1 stk. 3 exempts a holding from the targeted requirement entirely if it
has a base area under [10](SOURCES.md#F-15ea8b5deb) hectares, **or if it was certified for organic production, or
had applied to be, on 2026-02-01**. BEK 673/2026 §4 stk. 5 exempts organic
holdings from the livestock catch-crop requirement as well.

That is not a marginal advantage of the kind arithmetic produces. It is a statutory
exemption from two of the four instruments, and [section 4](#4-where-it-lands-and-on-whom)
measures how much land sits behind it.

### The law that takes over in 2027, and the thing in it that changes everything

The act passed on 2026-09-03 is **LOV nr. 759 of 2026-09-08, *Lov om
bæredygtig forvaltning af næringsstoffer og drivhusgasser m.v. i land- og skovbruget***
([Lovtidende text](https://www.retsinformation.dk/eli/lta/2026/759/dan/pdf)). Three of
its provisions decide incidence, and all three were read here rather than taken from
coverage of them.

**It does not apply yet, and that is why this page is about catch crops.** §57 puts it
in force on 2027-01-01 and repeals the old fertiliser act; §57 stk. 3 then says the
act *"finder ikke anvendelse på forhold, der vedrører planperioden 2019-2020 til og med
planperioden 2026-2027"* — for those, *"finder de hidtil gældende regler anvendelse"*.
So the requirements measured in section 3 through section 5 are the ones that actually bind this
year, and the discharge quota arrives on top of them, not instead of them.

**It is a framework act, so the numbers are not in it.** §6 stk. 2 empowers the minister
to set *"nærmere regler om udvaskningsgrænser og udledningskvoter og virkemidler til
opfyldelse heraf"*. Everything that decides a holding's position — the limits, the
quota, the conversion from leaching to discharge — is delegated to implementing
regulations. **This project has not verified that those have been issued.**

**And discharge quotas are transferable.** §6 stk. 4, last sentence:

> *"Ministeren kan endvidere fastsætte regler om overdragelse af udledningskvoter,
> herunder betingelser for overdragelse for at sikre den forudsatte miljøeffekt."*
>
> *(The minister may further set rules on the transfer of discharge quotas, including
> conditions for transfer so as to secure the presupposed environmental effect.)*

That is the statutory power, and it is enacted. What it does **not** settle is the
terms: who may sell to whom, whether transfer is bounded within a catchment, and at what
price. Those live in an implementing regulation this page has not read. So the honest
statement is narrower than "there is a market" and much stronger than "not established":
**the act contemplates transfer and creates the power to permit it; the terms are not
verified here.** That matters because, as the block below shows, transfer is worth [28](SOURCES.md#F-8581b578b3)%
of cattle's modelled loss.

**The state can also simply take the land.** §11 gives a power of expropriation to carry
out measures under the act, with *"fuldstændig erstatning"* — full compensation — where
the intervention is expropriatory. §65 inserts a second, wider power into the CAP
administration act: the minister or the municipal council *"kan ekspropriere
landbrugsarealer, hvis det er af væsentlig betydning at råde over disse arealer for at
gennemføre foranstaltninger, som iværksættes for at forbedre klimaet til opfyldelse af
bindende målsætninger i lov om klima"*, with one carve-out — the first subsection *"kan ikke anvendes
til at fremme statslig skovtilplantning"*. A voluntary programme with a compulsory floor
under it is a different offer from a voluntary programme without one, and section 6's
argument about who takes the money should be read with that in mind.

<details class="work">
<summary>Trading was argued about, priced by the model's own technical basis, and the group that would gain most from it is cattle — which is why the unread implementing regulation is the most load-bearing document on this page</summary>

Økologisk Landsforening's director stated after the December 2025 agreement that the
association had worked *"for, at konventionelle landbrug ikke skal have mulighed for at
købe de kvælstofudledningskvoter, som økologer ikke bruger, fordi de udleder langt
mindre kvælstof"* — to stop conventional farms buying the nitrogen quotas organic farms
do not use — and that *"[d]et var der ikke stemning for blandt de politiske partier"*.
An argument to prohibit a purchase is only made about a purchase someone expects to be
possible.

The DCA/AU **NUAR** report, which is the technical basis for the discharge-based model,
models trading explicitly and finds that **cattle holdings are the largest gainers from
it**: *"kvægbrugene er også dem med de største gevinster med handel"*. In its Hjarbæk
Fjord table the cattle loss narrows from [-1,122](SOURCES.md#F-36d363339a) kr/ha under the root-zone model to [-811](SOURCES.md#F-0faae0998f)
once trading is allowed.

So the trading question is not a technicality about market design. It is the difference
between the sector that carries the largest loss carrying [28](SOURCES.md#F-8581b578b3)% less of it.
The statute permits the minister to allow transfer; the regulation that would say on
what terms is the single document whose absence most changes this page's conclusions,
and it is listed first in [section 7](#7-what-this-cannot-establish-and-what-would).
</details>

### Three channels, with opposite incidence

| Channel | Binds on | Falls hardest on |
|---|---|---|
| **The catch-crop percentage** | the base area — cereals, maize, rape, pulses | holdings whose land is mostly in those crops, and holdings whose base area is small relative to their manure |
| **The manure ceiling and the two thresholds** | the slurry, which is not optional, because the animals exist | holdings applying over [80](SOURCES.md#F-0277d7c7e6) kg N/ha, where three separate requirements step up at once |
| **Land conversion and the set-aside ceiling** | the hectare itself | whoever *owns* lowland in a badly-retaining catchment |

The second channel is the one this project can measure directly, because both halves of
it are in open registers that join on the company number. The first can now be measured
too, imperfectly, and [section 3](#3-the-base-area-is-the-thing-cattle-has-least-of)
does it. The third cannot be measured here at all, because ownership is not in the
registers fetched.

## 2. Before anything else: [76](SOURCES.md#F-c338feb8e8)% of the herd keeps no public accounts

The second level of this page — which holdings have no buffer — can only be asked of holdings
that publish a balance sheet. That is a much smaller and much stranger set than
"Danish farming", and the size of the gap has to be established first, because
everything downstream inherits it.

Denmark's filing duty follows the legal form. A limited company (`Anpartsselskab`,
ApS) or a public company (`Aktieselskab`, A/S) must file an annual report, and it is
published in full and machine-readable. A sole proprietorship
(`Enkeltmandsvirksomhed`) and, in the ordinary case, a partnership
(`Interessentskab`, I/S) **must not and does not**. Danish agriculture is
overwhelmingly the second kind.

| Legal form of the business keeping the animals | Businesses | Animal units | Share of national herd | Mean DE |
|---|---:|---:|---:|---:|
| Enkeltmandsvirksomhed | [12,725](SOURCES.md#F-a998566e98) | [1,585,553](SOURCES.md#F-5f6be81c18) | [65.1](SOURCES.md#F-a97013bbfe)% | [125](SOURCES.md#F-6c50c5dad1) |
| Anpartsselskab | [1,259](SOURCES.md#F-66c468036c) | [378,199](SOURCES.md#F-fdc478713f) | [15.5](SOURCES.md#F-3de90db406)% | [300](SOURCES.md#F-26ab29fcaf) |
| Interessentskab | [1,315](SOURCES.md#F-1178e6852d) | [264,856](SOURCES.md#F-d5d521f85c) | [10.9](SOURCES.md#F-474112b896)% | [201](SOURCES.md#F-7d4f780cd1) |
| Aktieselskab | [290](SOURCES.md#F-b8da396b9a) | [172,286](SOURCES.md#F-bbfbeb59aa) | [7.1](SOURCES.md#F-bd27d2a448)% | [594](SOURCES.md#F-a44d4c3c5b) |
| Kommanditaktieselskab/Partnerselskab | [29](SOURCES.md#F-a1931fcce7) | [18,552](SOURCES.md#F-e9eba463ba) | [0.8](SOURCES.md#F-6cefc1aa13)% | [640](SOURCES.md#F-28eb1c5ca6) |
| Kommanditselskab | [13](SOURCES.md#F-58f18619f2) | [3,569](SOURCES.md#F-1fc3c73c70) | [0.1](SOURCES.md#F-2bca1ed8ee)% | [275](SOURCES.md#F-4f32d348e5) |

Over the [16,449](SOURCES.md#F-1851699b34) businesses that keep animals at all:

| | Businesses | Animal units | Share of herd |
|---|---:|---:|---:|
| Files an annual account | [1,637](SOURCES.md#F-8c93fcc349) | [576,172](SOURCES.md#F-32ce419b42) | **[23.7](SOURCES.md#F-4fc8a9d033)%** |
| Files none | [14,812](SOURCES.md#F-5563fb7a9e) | [1,858,481](SOURCES.md#F-d9c9804616) | **[76.3](SOURCES.md#F-c338feb8e8)%** |

And over the [26,922](SOURCES.md#F-daa69c1d45) businesses that declare field parcels:

| | Businesses | Declared hectares | Share of the declared area |
|---|---:|---:|---:|
| Files an annual account | [2,247](SOURCES.md#F-3e5f295b9e) | [497,075](SOURCES.md#F-4595dd32f0) | **[19.0](SOURCES.md#F-f5722eca50)%** |
| Files none | [24,675](SOURCES.md#F-d40072ea44) | [2,124,015](SOURCES.md#F-5b51d1bbc4) | **[81.0](SOURCES.md#F-c9155a1f23)%** |

**[76](SOURCES.md#F-c338feb8e8)% of the Danish herd and
[81](SOURCES.md#F-c9155a1f23)% of the declared Danish farmland is
operated by a business whose finances are not public.** No amount of care with the
[1,637](SOURCES.md#F-8c93fcc349) filings that do exist changes that. It is not a sampling problem
that a larger fetch would fix; it is a legal fact about who has to file.

*What the visible end is biased towards.* The incorporated businesses are the large
ones — mean [300](SOURCES.md#F-26ab29fcaf)
animal units for an ApS and
[594](SOURCES.md#F-a44d4c3c5b) for an A/S,
against [125](SOURCES.md#F-6c50c5dad1)
for a sole proprietorship. So section 6 is not a picture of Danish farming under
stress. **It is a picture of the largest, most capitalised, most professionally
financed [24](SOURCES.md#F-4fc8a9d033)% of it** — the end most likely to have a term loan, a treasurer and a
buffer. Every fragility figure in section 6 should be read as a floor on the fragility
of the whole.

<details class="work">
<summary>The herd is concentrated enough that a quota binding on animals binds on [a few hundred businesses](SOURCES.md#F-933da51e9b) — [835](SOURCES.md#F-1ade3ad928) of them hold [50](SOURCES.md#F-4fd63428a0)% of it</summary>

Over the [12,524](SOURCES.md#F-6083d714d1) businesses with a non-zero animal-unit count:

| | Holdings | Share of holdings |
|---|---:|---:|
| Hold [25](SOURCES.md#F-f9f9c57d65)% of the national herd | [252](SOURCES.md#F-8fe608769c) | [2.0](SOURCES.md#F-b87318ad59)% |
| Hold [50](SOURCES.md#F-4fd63428a0)% | [835](SOURCES.md#F-1ade3ad928) | [6.7](SOURCES.md#F-2d8d603610)% |
| Hold [75](SOURCES.md#F-50679b85d8)% | [1,931](SOURCES.md#F-05b179fc4e) | [15.4](SOURCES.md#F-808146f675)% |
| Hold [90](SOURCES.md#F-fcc0182fc2)% | [3,148](SOURCES.md#F-d00ff97cb7) | [25.1](SOURCES.md#F-96e1997544)% |

Median holding: [14.3](SOURCES.md#F-1fd6c19bdb) DE. 90th percentile: [585](SOURCES.md#F-c88b033d1b). 99th:
[2,048](SOURCES.md#F-3c07fe551e).

Land is concentrated too, though less so: the largest
[2,091](SOURCES.md#F-0ec8e2adc7) of [26,922](SOURCES.md#F-daa69c1d45) land-declaring businesses
([7.8](SOURCES.md#F-a046e2c2a3)%) declare half the hectares,
and the median declaration is [25.1](SOURCES.md#F-4d51cbe088) ha against a 99th percentile of
[958](SOURCES.md#F-314ecdd248).

This cuts both ways for the argument. It means an instrument aimed at the herd has a
very small number of addressees, which makes it administrable and makes compensation
cheap to target. It also means the median animal-keeping business in Denmark is a
[14](SOURCES.md#F-1fd6c19bdb)-animal-unit holding that is almost invisible in any
herd-weighted average — including several in this document, which is why counts of
holdings are printed beside every share of the herd.
</details>

## 3. The base area is the thing cattle has least of

Section 1 established that the requirement is *a percentage of the base area* and that
three of the four instruments step up at [80](SOURCES.md#F-0277d7c7e6) kg of manure nitrogen per hectare. Both
halves of that can be measured, imperfectly, on the open registers — and together they
locate the burden somewhere a stocking-density table does not.

### Where the holdings sit relative to the thresholds the rules use

The registers carry animal units, not kilograms of nitrogen, so the two lines below are
placed by a **stated conversion of [100](SOURCES.md#F-e96ae98eaf) kg N per animal unit** and are indicative rather
than a test. They locate roughly where a holding crosses from one regulatory band into
the next; they do not establish that any particular holding does.

| Enterprise type | Holdings | Animal units | Share of herd | With land | Median DE/ha | ≈[30](SOURCES.md#F-67989f7136) kg N/ha | ≈[80](SOURCES.md#F-0277d7c7e6) kg N/ha | [1.4](SOURCES.md#F-8a1f2ea7e8) (historic) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dairy | [1,965](SOURCES.md#F-09a38a155d) | [967,647](SOURCES.md#F-1c300013d6) | [39.7](SOURCES.md#F-704e566263)% | [1,728](SOURCES.md#F-b5bcac76f6) | **[1.83](SOURCES.md#F-8b666b64aa)** | [97](SOURCES.md#F-7fdc19f4ff)% | **[92](SOURCES.md#F-117f8f8d9a)%** | [72](SOURCES.md#F-3ea706ab3e)% |
| pigs | [1,873](SOURCES.md#F-a8cff5df7d) | [1,033,381](SOURCES.md#F-da58a010b9) | [42.4](SOURCES.md#F-650b861ffd)% | [1,292](SOURCES.md#F-428f28fcd4) | **[1.34](SOURCES.md#F-606422a81e)** | [93](SOURCES.md#F-fca5cc8797)% | **[77](SOURCES.md#F-c5ab2e496e)%** | [47](SOURCES.md#F-96d569c38d)% |
| beef / other cattle | [6,185](SOURCES.md#F-3a8ac55ac9) | [306,529](SOURCES.md#F-febc9509d2) | [12.6](SOURCES.md#F-e5d53dd5bf)% | [5,038](SOURCES.md#F-e122aebde6) | **[0.44](SOURCES.md#F-da38f00013)** | [64](SOURCES.md#F-42272010ae)% | **[28](SOURCES.md#F-e1f6a5927c)%** | [13](SOURCES.md#F-8e7f77441f)% |
| poultry | [429](SOURCES.md#F-6e3f9b57a5) | [101,566](SOURCES.md#F-6734c368b8) | [4.2](SOURCES.md#F-18b75e9461)% | [282](SOURCES.md#F-9143f424a0) | **[0.97](SOURCES.md#F-aa0c5a1eb0)** | [71](SOURCES.md#F-50aff168ee)% | **[53](SOURCES.md#F-583fbffff7)%** | [42](SOURCES.md#F-8da052e2e9)% |
| other / mixed livestock | [2,072](SOURCES.md#F-9a56443111) | [25,530](SOURCES.md#F-8085d4dcf7) | [1.0](SOURCES.md#F-862e71b7cc)% | [1,181](SOURCES.md#F-962a4827e0) | **[0.17](SOURCES.md#F-5b14072ec1)** | [33](SOURCES.md#F-3b5ee41bbb)% | **[10](SOURCES.md#F-5929d42652)%** | [4](SOURCES.md#F-d72f919f49)% |

**[92](SOURCES.md#F-117f8f8d9a)% of dairy holdings that declare land sit above the
higher of the two thresholds**, against [77](SOURCES.md#F-c5ab2e496e)% of pig holdings
and [28](SOURCES.md#F-e1f6a5927c)% of beef. Above that line three
things happen at once: the compulsory catch-crop percentage rises from [10.7](SOURCES.md#F-4caa16bda4)% to [14.7](SOURCES.md#F-4aa7012024)%,
the livestock catch-crop requirement applies on top, and the quota-reduction escape
valve reprices from [110](SOURCES.md#F-fe6cd4c3cd) to [175](SOURCES.md#F-35790b9b7a) kg N per hectare. **The instrument does not tighten
gradually with density. It steps, and dairy is almost entirely on the far side of the
step.**

### And the base it is charged against

Here is the part that a density table cannot see. The percentages are charged on the
*efterafgrødegrundareal*, and BEK 673/2026 Bilag 1 defines that as cereals, rape,
**maize**, rybs, soya, mustard, peas, field beans, sunflower, oil flax and other annual
crops with no autumn nitrogen uptake. **Grass is not on the list.**

Classifying each business by its largest declared crop:

| Operator of the declared hectares | Declared hectares | Largest crop inside the base | Outside it | Unclassified |
|---|---:|---:|---:|---:|
| dairy | [442,958](SOURCES.md#F-75bd84fe9a) | **[34.1](SOURCES.md#F-6841a6753c)%** | [64.3](SOURCES.md#F-43c37cc268)% | [1.6](SOURCES.md#F-868684ec42)% |
| pigs | [394,439](SOURCES.md#F-376bbb556a) | **[96.7](SOURCES.md#F-da9b8747fc)%** | [1.6](SOURCES.md#F-89e12a3c6f)% | [1.7](SOURCES.md#F-7d6741cdaa)% |
| beef / other cattle | [338,188](SOURCES.md#F-cfc97799dd) | **[54.5](SOURCES.md#F-4f93726c83)%** | [44.3](SOURCES.md#F-a5294bb332)% | [1.2](SOURCES.md#F-f352cc4146)% |
| poultry | [43,401](SOURCES.md#F-70ca8172c1) | **[89.2](SOURCES.md#F-fb26e8e29b)%** | [7.3](SOURCES.md#F-3bea58b642)% | [3.5](SOURCES.md#F-aa408d7f77)% |
| other / mixed livestock | [77,244](SOURCES.md#F-6194e49961) | **[51.0](SOURCES.md#F-9805d9f787)%** | [48.1](SOURCES.md#F-977e6e0e74)% | [0.9](SOURCES.md#F-82c7fe8468)% |
| no animal units | [1,324,860](SOURCES.md#F-77e0dedda3) | **[77.1](SOURCES.md#F-3d21deabef)%** | [18.4](SOURCES.md#F-661c6c942a)% | [4.5](SOURCES.md#F-92bb75b4a6)% |

**[34](SOURCES.md#F-6841a6753c)% of dairy's declared
hectares are on holdings whose largest crop is inside the base area, against
[97](SOURCES.md#F-da9b8747fc)% of pigs'.** Dairy grows
grass. Grass is not in the base. So the dairy holding carries the largest manure load,
sits above the higher threshold, and then has to find its catch-crop percentage out of
the fraction of its rotation that is cereals and maize — which is the fraction that
feeds the cows.

That is not this project's theory. It is the mechanism the technical basis for the new
regulation states in its own words. The DCA/Aarhus University **NUAR** report — the
analysis behind the discharge-based model — puts it exactly this way:

> *"Fælles for alle modellerne for de udvalgte kystvandoplande er, at kvægbrug er den
> bedriftstype, der har de største tab […] Kvægbrugene har som udgangspunkt en større
> kvælstofudledning, men et mindre efterafgrødegrundareal end de øvrige bedrifter."*
>
> *(Common to all the models for the selected coastal catchments is that cattle farming
> is the enterprise type with the largest losses […] Cattle farms have from the outset a
> larger nitrogen discharge, but a smaller catch-crop base area than the other
> holdings.)*
>
> — Eriksen et al., *Ny Udledningsbaseret Arealregulering for kvælstof (NUAR)*,
> DCA rådgivningsnotat, 2024-05-24,
> [page 88](https://pure.au.dk/ws/portalfiles/portal/379114234/NUAR-slutnotat_24._maj_2024.pdf)

Two independent routes to the same conclusion: the register says dairy's base area is
small, and the report says a small base area is why cattle carries the largest loss.

*What this does not establish.* The classification uses each business's **largest**
declared crop, because that is all the summary register carries. A dairy holding whose
largest crop is grass certainly has cereal area too, so the true base share for dairy is
higher than [34](SOURCES.md#F-6841a6753c)% and the true
share for pigs lower than [97](SOURCES.md#F-da9b8747fc)%.
The direction is robust and the magnitudes are not. The full parcel-level crop
declaration would fix this and is in a register already fetched — see
[section 7](#7-what-this-cannot-establish-and-what-would).

### The shed with no field, and the field that is too small

The second channel — manure that has nowhere to go — splits the herd a different way:

| Enterprise type | Surplus DE above [1.4](SOURCES.md#F-8e54e8529b)/ha | Holdings | DE on holdings declaring no land | Holdings | Share of that type's herd |
|---|---:|---:|---:|---:|---:|
| dairy | [266,820](SOURCES.md#F-7d317b4575) | [1,242](SOURCES.md#F-2ca32a8799) | [138,900](SOURCES.md#F-cebd231989) | [237](SOURCES.md#F-4db3161de2) | [42](SOURCES.md#F-5caa652f19)% |
| pigs | [198,827](SOURCES.md#F-d63beae417) | [610](SOURCES.md#F-6cd485eb40) | [406,192](SOURCES.md#F-eefa58fbf2) | [581](SOURCES.md#F-70de0de87a) | [59](SOURCES.md#F-ffd6dbdd8b)% |
| beef / other cattle | [104,991](SOURCES.md#F-2d46ff1216) | [641](SOURCES.md#F-ce0a8908dc) | [41,308](SOURCES.md#F-12bf920514) | [1,147](SOURCES.md#F-83e6d2f259) | [48](SOURCES.md#F-1d38d84214)% |
| poultry | [32,393](SOURCES.md#F-066478268b) | [118](SOURCES.md#F-694c00f2f5) | [34,854](SOURCES.md#F-d4a179d0b2) | [147](SOURCES.md#F-ea26fd8ec3) | [66](SOURCES.md#F-378a3e532f)% |
| other / mixed livestock | [2,944](SOURCES.md#F-acc0355a9b) | [52](SOURCES.md#F-2d95576a33) | [3,709](SOURCES.md#F-671cb75692) | [891](SOURCES.md#F-e80b213992) | [26](SOURCES.md#F-d30e8382ca)% |

Nationally that is **[605,975](SOURCES.md#F-3556854875) animal units in surplus on [2,663](SOURCES.md#F-ac2e4e9eac) holdings and a
further [624,963](SOURCES.md#F-910413aa8f) on [3,003](SOURCES.md#F-932825971f) holdings with no declared land at all** —
together [51](SOURCES.md#F-121ad74c67)% of the Danish herd standing on
more animal units than its own declared ground would take at the old harmony density.
That is a measure of pressure and not a finding of non-compliance; the qualification at
the end of this section says why.

And the two halves belong to different animals.

* **Dairy is land-squeezed.** [1,242](SOURCES.md#F-2ca32a8799) dairy holdings carry
  [266,820](SOURCES.md#F-7d317b4575) surplus animal units — the largest surplus of any type —
  but only [237](SOURCES.md#F-4db3161de2) declare no land. The dairy holding has fields;
  it has slightly too many cows for them, and the wrong crops on them.
* **Pigs are landless.** [581](SOURCES.md#F-70de0de87a) pig holdings hold
  [406,192](SOURCES.md#F-eefa58fbf2) animal units with no declared hectare underneath them
  at all — [2.0](SOURCES.md#F-21ce0539cd) times the surplus carried by the [610](SOURCES.md#F-6cd485eb40) pig
  holdings that do declare land.

That distinction decides who a percentage-of-base-area instrument reaches. A
land-squeezed holding is *inside* it: it has a base area and the percentage is charged
on it. A landless holding is **outside** — it has no base area to charge, and its entire
nitrogen position is a contract to place slurry on somebody else's harmoniareal.
Tighten the receiving farm's requirement and the price of that contract moves. The
landless unit is where the cost lands, and it lands there without the unit ever
appearing in a per-hectare table.

**Those contracts are the one part of this arrangement that is not public.** They are
not in the CVR register, not in the field-parcel register and not in the livestock
register. This is the single largest unmeasured quantity in the whole incidence
question, and it is a private contract rather than a missing dataset — so no fetch fixes
it.

*What this does not establish.* Declared area is land declared for area support, which
is neither the *harmoniareal* the manure thresholds are measured against nor the
*efterafgrødegrundareal* the percentages are charged on: rented-in land can be missing,
and a business buying spreading capacity from a neighbour looks land-poor here and is
compliant in law. The [1.4](SOURCES.md#F-8a1f2ea7e8) DE/ha column is the **pre-2017** unit, kept only for
continuity with [NITROGEN.md](NITROGEN.md); it has no legal force. And the ≈[30](SOURCES.md#F-67989f7136) and ≈[80](SOURCES.md#F-0277d7c7e6)
columns rest on the stated [100](SOURCES.md#F-e96ae98eaf) kg N per animal unit conversion, which this page has not
verified.

## 4. Where it lands, and on whom

### The published allocation, which is not where the animals are

The mandatory targeted requirement for 2026/2027 is a short list. [20](SOURCES.md#F-44aa2f6ee6) coastal
catchments carry one; every other catchment in Denmark carries none, because the
subsidised voluntary round covered the need there. This is the whole of BEK 677/2026
Annex 1:

| Coastal catchment | Requirement, as % of the holding's base area |
|---|---:|
| Kalundborg Fjord | [34.5](SOURCES.md#F-f250c5e843)% |
| Kløven | [34.5](SOURCES.md#F-08fef7cafb)% |
| Helnæs Bugt | [34.5](SOURCES.md#F-40c5425933)% |
| Kås Bredning og Venø Bugt | [34.5](SOURCES.md#F-d39e6457f2)% |
| Aborg Minde Nor | [34.0](SOURCES.md#F-39df169362)% |
| Genner Bugt | [30.1](SOURCES.md#F-c09fa0a47d)% |
| Horsens Fjord, ydre | [25.3](SOURCES.md#F-60cf65df24)% |
| Løgstør Bredning | [25.3](SOURCES.md#F-fb9d954cce)% |
| Storebælt, NV | [24.6](SOURCES.md#F-d5789cf5fb)% |
| Randers Fjord, indre | [24.4](SOURCES.md#F-d775da4713)% |
| Als Fjord | [23.1](SOURCES.md#F-7bf4e533dd)% |
| Jammerland Bugt og Musholm Bugt | [21.3](SOURCES.md#F-045b6b4553)% |
| Hejlsminde Nor | [21.0](SOURCES.md#F-4f57374fad)% |
| Stege Bugt | [18.9](SOURCES.md#F-f490d734e1)% |
| Kertinge Nor | [18.7](SOURCES.md#F-5da392bfeb)% |
| Knudedyb | [18.4](SOURCES.md#F-7e5e223628)% |
| Dybsø Fjord | [18.3](SOURCES.md#F-1a1b22ebaf)% |
| Juvre Dyb | [16.7](SOURCES.md#F-6fa7c633e4)% |
| Augustenborg Fjord | [16.3](SOURCES.md#F-4ac62fde5c)% |
| Kolding Fjord, indre | [14.8](SOURCES.md#F-9a4c5e24c8)% |

[20](SOURCES.md#F-44aa2f6ee6) catchments, from [14.8](SOURCES.md#F-9a4c5e24c8)% to [34.5](SOURCES.md#F-f250c5e843)%, median [23.75](SOURCES.md#F-25de19b6bc)%.
[4](SOURCES.md#F-ea59a51099) sit at the [34.5](SOURCES.md#F-f250c5e843)% ceiling: Kalundborg Fjord, Kløven, Helnæs Bugt, Kås Bredning og Venø Bugt.

**Read the names.** Kalundborg Fjord, Dybsø Fjord, Stege Bugt, Jammerland Bugt and
Musholm Bugt are Zealand and Møn. Kløven, Helnæs Bugt, Kertinge Nor and Aborg Minde Nor
are Funen and the small islands. Als Fjord, Augustenborg Fjord, Genner Bugt and
Hejlsminde Nor are Sønderjylland's inner waters. This is not the west-Jutland livestock
belt, and of the catchments at the ceiling only Kås Bredning og Venø Bugt is in Jutland.

Now set that against where the animals are:

| Region | Holdings | Animal units | Share of herd | With land | Median DE/ha | >[1.4](SOURCES.md#F-8a1f2ea7e8) |
|---|---:|---:|---:|---:|---:|---:|
| Region Syddanmark | [3,877](SOURCES.md#F-c02cbc42f7) | [864,103](SOURCES.md#F-6d661ff847) | [35.5](SOURCES.md#F-e4afb87453)% | [2,960](SOURCES.md#F-b0b3b501cb) | [0.79](SOURCES.md#F-ff023dfa52) | [32](SOURCES.md#F-8092fa309d)% |
| Region Midtjylland | [3,831](SOURCES.md#F-9c2ae5f77f) | [792,389](SOURCES.md#F-41fceff657) | [32.5](SOURCES.md#F-eba8017550)% | [2,970](SOURCES.md#F-8f5916ae6d) | [0.71](SOURCES.md#F-f602d7df08) | [29](SOURCES.md#F-8991b58115)% |
| Region Nordjylland | [2,662](SOURCES.md#F-7df04b0a34) | [572,711](SOURCES.md#F-7956094844) | [23.5](SOURCES.md#F-08365d5717)% | [2,096](SOURCES.md#F-e56ada3486) | [0.79](SOURCES.md#F-5f020b5145) | [31](SOURCES.md#F-f69c57d5c0)% |
| Region Sjælland | [1,541](SOURCES.md#F-a404d81733) | [162,620](SOURCES.md#F-56e68c1900) | [6.7](SOURCES.md#F-9fd83cf2c9)% | [1,059](SOURCES.md#F-e10b8a3d84) | [0.37](SOURCES.md#F-cd7d80c944) | [15](SOURCES.md#F-d18a334ecf)% |
| Region Hovedstaden | [613](SOURCES.md#F-8d4bd437a5) | [42,828](SOURCES.md#F-9e7df7e833) | [1.8](SOURCES.md#F-a42461f7b7)% | [436](SOURCES.md#F-2a1bda786d) | [0.35](SOURCES.md#F-7e0c39d2ac) | [12](SOURCES.md#F-9a33329277)% |

**[92](SOURCES.md#F-9a1ed9076c)% of the Danish herd is in Jutland**, and the region
carrying the least of it — Sjælland at
[6.7](SOURCES.md#F-9fd83cf2c9)%, median [0.37](SOURCES.md#F-cd7d80c944) DE/ha —
contains several of the catchments carrying the highest mandatory percentage.

That is not a paradox and it is not evidence that the allocation is wrong. It follows
from the design. The requirement is sized to a *catchment's* remaining reduction need
after the voluntary round, and it is charged on the *base area*, which is cereals. A
catchment of Zealand arable land has a large base area, few animals, and — on the
evidence of it appearing on this list — a need the voluntary round did not meet. **A
percentage of a large base area on holdings with no manure is a real cost, and it falls
on exactly the population section 6 has no balance sheets for.**

<details class="work">
<summary>The kommune-level density table, which is the wrong unit for this instrument and is printed anyway because it is the one this project can compute</summary>

| Kommune, ranked by median stocking density | Region | Holdings with land | Median DE/ha | >[1.4](SOURCES.md#F-8a1f2ea7e8) | Animal units |
|---|---|---:|---:|---:|---:|
| Tønder | Syddanmark | [311](SOURCES.md#F-5abbc4600a) | **[1.24](SOURCES.md#F-7e42c6429e)** | [44](SOURCES.md#F-623f8dc6c7)% | [121,907](SOURCES.md#F-00ba3a9068) |
| Haderslev | Syddanmark | [180](SOURCES.md#F-a649515990) | **[1.14](SOURCES.md#F-e370a52428)** | [40](SOURCES.md#F-b4afa9fb52)% | [63,241](SOURCES.md#F-a49b939828) |
| Lemvig | Midtjylland | [124](SOURCES.md#F-1046fc9da1) | **[1.10](SOURCES.md#F-067e522329)** | [44](SOURCES.md#F-558a16323b)% | [47,807](SOURCES.md#F-613efb5380) |
| Esbjerg | Syddanmark | [227](SOURCES.md#F-96c4dbee53) | **[1.09](SOURCES.md#F-7e68214501)** | [42](SOURCES.md#F-81531dba63)% | [75,549](SOURCES.md#F-9798310880) |
| Ringkøbing-Skjern | Midtjylland | [272](SOURCES.md#F-d5990ad622) | **[1.08](SOURCES.md#F-39c0bdcde7)** | [40](SOURCES.md#F-cbcc6ab9ad)% | [123,620](SOURCES.md#F-8f7cf1f8b9) |
| Vesthimmerlands | Nordjylland | [212](SOURCES.md#F-b3f6ba0581) | **[1.01](SOURCES.md#F-77b9e1fad5)** | [40](SOURCES.md#F-e5827b5fac)% | [81,831](SOURCES.md#F-fd1d649272) |
| Morsø | Nordjylland | [130](SOURCES.md#F-f0a1ff5c60) | **[0.99](SOURCES.md#F-f34d38b19f)** | [35](SOURCES.md#F-059f8a7115)% | [36,420](SOURCES.md#F-ad100acf47) |
| Aabenraa | Syddanmark | [285](SOURCES.md#F-d9150221ae) | **[0.97](SOURCES.md#F-70ef5992b9)** | [37](SOURCES.md#F-edf5aa927d)% | [92,948](SOURCES.md#F-492d934ff9) |
| Holstebro | Midtjylland | [165](SOURCES.md#F-d75b701b76) | **[0.96](SOURCES.md#F-d26e1d52d0)** | [38](SOURCES.md#F-e9e70b970a)% | [54,942](SOURCES.md#F-e4ff2b9d6d) |
| Hjørring | Nordjylland | [299](SOURCES.md#F-77b69dea24) | **[0.93](SOURCES.md#F-2c4f00a750)** | [35](SOURCES.md#F-a8e3daae4a)% | [83,140](SOURCES.md#F-887acb4633) |
| Herning | Midtjylland | [270](SOURCES.md#F-a49bfa9f9d) | **[0.92](SOURCES.md#F-59f3673762)** | [39](SOURCES.md#F-62463b547d)% | [82,908](SOURCES.md#F-161c587a3d) |
| Skive | Midtjylland | [202](SOURCES.md#F-49f79c3b7b) | **[0.91](SOURCES.md#F-6e3164ff83)** | [34](SOURCES.md#F-587761d3a7)% | [62,623](SOURCES.md#F-8cbc85ddaf) |

*(minimum [100](SOURCES.md#F-dd435484db) holdings declaring land, so that a median means something)*

The three Jutland regions run from [0.71](SOURCES.md#F-f602d7df08) to [0.79](SOURCES.md#F-ff023dfa52) DE/ha at the median,
which is flat enough that the region is useless as a unit. The kommune is sharper and
names one belt: the sandy west and south of Jutland, plus Sønderjylland. That belt is
where the *manure* pressure is, and the manure pressure is a real burden — the two
thresholds in section 3 and the [170](SOURCES.md#F-ccab7b1fe3) kg N/ha ceiling all bite there. It is simply not
the same burden as the targeted percentage in the table above, and mapping one onto the
other is the mistake this section exists to prevent.

**On retention, this page states less than it would like to.** The instrument weights
by modelled nitrogen retention, and the common summary — that sandy west Jutland is the
low-retention part of Denmark — is **not established** here and there is published
evidence against it. IFRO's paired figures put Ringkøbing Fjord, in the sandy west, at
*higher* retention than Odense Fjord's outer catchment on Funen, with the difference in
delivery to the coast coming from higher leaching rather than lower retention. The
producing institutions describe the mechanism as transport path length and redox depth
rather than soil texture. Two catchments are not a national gradient, and this project
has not obtained the retention grid, so it asserts no pattern. [Section 7](#7-what-this-cannot-establish-and-what-would)
says what would settle it.
</details>

### Organic holdings are exempt, and that is worth more than the arithmetic

Section 1 recorded the statutory exemptions: a holding certified for organic production
on 2026-02-01 is outside the targeted requirement altogether
(BEK 677/2026 §1 stk. 3 nr. 2) and outside the livestock catch-crop requirement as well
(BEK 673/2026 §4 stk. 5). Underneath that exemption there is also an arithmetic advantage, and the livestock
register can measure it on cattle:

| Cohort | Holdings | Animal units | Mean DE | With land | Median DE/ha | >[1.4](SOURCES.md#F-8a1f2ea7e8) |
|---|---:|---:|---:|---:|---:|---:|
| Dairy, conventional | [1,702](SOURCES.md#F-e5e7ab46e4) | [859,294](SOURCES.md#F-9346e63c33) | [505](SOURCES.md#F-dcc7b0ded0) | [1,487](SOURCES.md#F-bc90534225) | **[1.94](SOURCES.md#F-1be576bcfa)** | [78](SOURCES.md#F-50b71e4b81)% |
| Dairy, organic | [263](SOURCES.md#F-3dba9943be) | [108,353](SOURCES.md#F-f32a9227c5) | [412](SOURCES.md#F-d091217d60) | [241](SOURCES.md#F-ed863ab83c) | **[1.26](SOURCES.md#F-7a512c9d6b)** | [34](SOURCES.md#F-ec4bb00bf2)% |
| Beef and other cattle, conventional | [5,848](SOURCES.md#F-fa61933cf6) | [265,030](SOURCES.md#F-ad29e325f7) | [45](SOURCES.md#F-1e9b3a053d) | [4,720](SOURCES.md#F-fd850aa82a) | **[0.45](SOURCES.md#F-0f33d29bb3)** | [13](SOURCES.md#F-422af6891e)% |
| Beef and other cattle, organic | [337](SOURCES.md#F-93581dd574) | [41,499](SOURCES.md#F-1916c3b7f6) | [123](SOURCES.md#F-8cd9bedf70) | [318](SOURCES.md#F-7936a9f19c) | **[0.36](SOURCES.md#F-30da469b92)** | [15](SOURCES.md#F-a04de32bc4)% |

Organic dairy holdings farm substantially more land per cow, and only part of that is a
smaller herd: mean herd [412](SOURCES.md#F-d091217d60) DE against [505](SOURCES.md#F-dcc7b0ded0), which is
[18](SOURCES.md#F-997cd20471)% smaller, but a median
stocking density of **[1.26](SOURCES.md#F-7a512c9d6b) against [1.94](SOURCES.md#F-1be576bcfa) DE/ha**, which is
[35](SOURCES.md#F-c47f02d83e)% lower. On beef the two are indistinguishable
([0.36](SOURCES.md#F-30da469b92) against
[0.45](SOURCES.md#F-0f33d29bb3)), which is what you would expect:
extensive beef is already below any threshold that binds.

The independent check agrees, and it is stronger than an exemption. In NUAR's modelling
of the discharge-based regulation across six allocation models, **organic holdings do
not merely lose less — they gain**, at between [+341](SOURCES.md#F-9912211b69) and [+523](SOURCES.md#F-1d7056c61f) kroner per hectare against
the reference, in a catchment where cattle lose between [-969](SOURCES.md#F-1dcfc6e11f) and [-1,207](SOURCES.md#F-e90a8c79dc). That is the
only enterprise type in the table with a positive sign in every column.

*What this does not establish.* The livestock register's organic flag is on the
**herd**, not on the land, and the statutory exemption turns on certification of the
*holding*. A conventional herd grazing organically certified land is invisible here, and
an organic arable holding with no animals does not appear in this cut at all — which
matters, because an arable holding is exactly what the targeted requirement is aimed at.
The organic share of the national herd measured this way is
[6.2](SOURCES.md#F-6d2753ec51)% on [600](SOURCES.md#F-bd459b382e) cattle holdings, and that is a floor.

## 5. [51](SOURCES.md#F-f1f24b66aa)% of the hectares have no animals over them

Section 3 and section 4 asked who keeps the animals and what they grow. Ask instead who holds
the hectares the percentage is charged on, and the population changes completely.

| Operator of the declared hectares | Businesses | Declared hectares | Share | Mean ha |
|---|---:|---:|---:|---:|
| dairy | [1,729](SOURCES.md#F-f7e82761db) | [442,958](SOURCES.md#F-a6869ed201) | [16.9](SOURCES.md#F-68c61f8396)% | [256](SOURCES.md#F-db12c0f68e) |
| pigs | [1,292](SOURCES.md#F-bf2950c5c0) | [394,439](SOURCES.md#F-f19aabc996) | [15.0](SOURCES.md#F-8bbde7a5f5)% | [305](SOURCES.md#F-03830ef282) |
| beef / other cattle | [5,045](SOURCES.md#F-52581350fb) | [338,188](SOURCES.md#F-045f425711) | [12.9](SOURCES.md#F-7abffc963d)% | [67](SOURCES.md#F-3db9033032) |
| poultry | [283](SOURCES.md#F-1cf4324fc7) | [43,401](SOURCES.md#F-17c2db91b1) | [1.7](SOURCES.md#F-3f3b7ff4ce)% | [153](SOURCES.md#F-34f8efb2ab) |
| other / mixed livestock | [1,182](SOURCES.md#F-e76cc0e4e8) | [77,244](SOURCES.md#F-cc8361455f) | [2.9](SOURCES.md#F-2a7c6322e8)% | [65](SOURCES.md#F-d155a6139b) |
| no animal units | [17,391](SOURCES.md#F-226d83b801) | [1,324,860](SOURCES.md#F-49fc18ec45) | [50.5](SOURCES.md#F-f1f24b66aa)% | [76](SOURCES.md#F-3786d358c2) |

**[50.5](SOURCES.md#F-f1f24b66aa)% of Denmark's declared farmland —
[1,324,860](SOURCES.md#F-49fc18ec45) hectares across [17,391](SOURCES.md#F-226d83b801) businesses — is farmed by a business with
no animal units in the livestock register at all.** These are the arable holdings, and
section 3 showed that [77](SOURCES.md#F-3d21deabef)%
of their hectares are on holdings whose largest crop is inside the base area. They are
the population the percentage is charged on most completely.

Two different costs reach them, one now and one from 2027, and they are not the same
kind of cost.

* **Today the instrument is a catch-crop percentage**, and the cost is a hectare of
  rotation given over to a crop that is not sold, on a base area that is nearly all of
  the farm. The [34.5](SOURCES.md#F-f250c5e843)% ceiling in section 4 is that share of the cereal ground.
* **From 2027 the quota is on discharge**, and then the constraint moves to the input
  the arable holding actually controls: the bag. That is the channel
  [the manure section of NITROGEN.md](NITROGEN.md) predicts bites first — *mineral fertiliser is
  the free variable and manure is not.* The livestock holding meets a tightening quota
  by rearranging where the slurry goes; the arable holding meets it by buying less
  nitrogen and harvesting less wheat. One is a logistics cost and the other is a yield
  cut.

| Largest declared crop on the holding (hectare-weighted) | Hectares | Share |
|---|---:|---:|
| Vinterhvede — *winter wheat* | [835,757](SOURCES.md#F-d6a41e9732) | [31.9](SOURCES.md#F-d9d4626099)% |
| Vårbyg — *spring barley* | [679,058](SOURCES.md#F-788c7ad6e4) | [25.9](SOURCES.md#F-48422bcf21)% |
| `Græs med kløver/lucerne, under 50 % bælgpl. (omdrift)` — *`grass with clover or lucerne, under 50% legume, in rotation`* | [256,725](SOURCES.md#F-bc96ec0dad) | [9.8](SOURCES.md#F-fc56af2614)% |
| Majshelsæd med græsudlæg — *whole-crop maize, grass undersown* | [116,037](SOURCES.md#F-71635d8da4) | [4.4](SOURCES.md#F-20b7ef1ffc)% |
| Majshelsæd — *whole-crop maize* | [96,774](SOURCES.md#F-0ddfcdabfe) | [3.7](SOURCES.md#F-a409917552)% |
| `Miljøtilsagn græs (0 N), permanent` — *permanent grass under an environmental commitment, zero nitrogen* | [60,424](SOURCES.md#F-6b6cfd2a59) | [2.3](SOURCES.md#F-92a5d83387)% |
| Vinterhybridrug — *winter hybrid rye* | [59,951](SOURCES.md#F-ce3d8287dd) | [2.3](SOURCES.md#F-4746ceea12)% |
| Vårhavre — *spring oats* | [54,077](SOURCES.md#F-a72882f8d2) | [2.1](SOURCES.md#F-790d12592b)% |

Winter wheat and spring barley alone account for
[58](SOURCES.md#F-e3d21544c0)% of the
declared area under this measure, and both are cereals whose yield responds to applied
nitrogen over the range a quota would move it. One row is worth reading twice:
[60,424](SOURCES.md#F-6b6cfd2a59) hectares ([2.3](SOURCES.md#F-92a5d83387)%) are already on holdings
whose largest declared crop is grass under an environmental commitment that permits
**no nitrogen at all**. That land is not available to be tightened, and it is a
reminder that the baseline the quota is applied to is not a uniform one.

> **And there is not one arable balance sheet in this analysis.**
>
> The accounts in section 6 were fetched for businesses on the livestock map, so every
> one of the [1,630](SOURCES.md#F-ad67b02b0c) filings is a business that keeps or
> kept animals. The sibling project is extending the fetch to crop holdings and that
> work is in progress; it is not in this data.
>
> So for the cohort carrying **half the hectares** and taking the most direct form of
> the burden, this page can describe the exposure and can say **nothing at all** about
> the buffer. That is a gap in the answer and not a hedge on it: a reader who wants to
> know whether Danish arable farming can absorb a per-hectare nitrogen cut will not
> find it here, and should not read section 6 as though it generalised.

## 6. Which balance sheets have no buffer

### The sample, and what it is a sample of

| | |
|---|---:|
| Businesses with filed accounts in this data | [1,630](SOURCES.md#F-ad67b02b0c) |
| …in primary agriculture (NACE `011`–`015`) | [848](SOURCES.md#F-b0aa7408ca) |
| …keeping animals in the 2024 livestock register | **[707](SOURCES.md#F-4f10e67ffc)** |
| …of those, also declaring field parcels | [416](SOURCES.md#F-27f4f48c71) |

[748](SOURCES.md#F-4a48240280) filings were dropped as not
primary agriculture. They are not noise to be tidied away — they are horse-keeping
businesses, property-letting companies, fish farms, livestock wholesalers and
non-financial holding companies that appear in the register because they happen to
hold a livestock site. Left in, the largest of them has assets of [over fifty billion](SOURCES.md#F-ab05e13ced)
kroner and would have set every mean on this page by itself. Medians are used
throughout anyway, and the exclusion is stated so the count can be checked.

Read section 2 before reading any figure below. This is the incorporated [24](SOURCES.md#F-669764ddc8)% of
the herd, it is the large end, and it is therefore the **most** resilient end.

### The distribution of equity

Equity ratio — equity over total assets — is the single number a bank looks at, and it
is the closest thing in a filed account to "how much can go wrong before this stops".
Across the [848](SOURCES.md#F-b0aa7408ca) agricultural filings:

| Decile | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Equity ratio | [-0.05](SOURCES.md#F-fae421f06a) | [0.11](SOURCES.md#F-7c6fcecf45) | [0.21](SOURCES.md#F-61a2d5595e) | [0.27](SOURCES.md#F-32893aff7e) | [0.33](SOURCES.md#F-ea41f714c0) | [0.42](SOURCES.md#F-56a6f4357f) | [0.53](SOURCES.md#F-5f4d2524c6) | [0.66](SOURCES.md#F-c4e4c20910) | [0.80](SOURCES.md#F-2bb900f7bc) |

**The bottom decile is already negative** — assets are worth less than the debts
against them — and the second decile sits at [0.11](SOURCES.md#F-7c6fcecf45), which is thin for a
business whose assets are mostly illiquid and whose income is a commodity price.

### By enterprise type

| Enterprise type | n | Median DE | Median assets (m. kr) | Median equity ratio | Negative equity | Loss last year | Median profit per ha (kr) | Median DE/ha |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| dairy | [148](SOURCES.md#F-34d725627a) | [686](SOURCES.md#F-4649b3203b) | [51.1](SOURCES.md#F-f527c03b29) | **[0.31](SOURCES.md#F-038357e409)** | [4](SOURCES.md#F-5e5b56f65c)% | [5](SOURCES.md#F-c14a5994db)% | [12,285](SOURCES.md#F-e6d31d3852) | [2.00](SOURCES.md#F-2f98fa2450) |
| pigs | [303](SOURCES.md#F-2686daa891) | [729](SOURCES.md#F-95a9f292d3) | [38.4](SOURCES.md#F-e2fcf0dde8) | **[0.32](SOURCES.md#F-df5f56b180)** | [8](SOURCES.md#F-502e42ae83)% | [23](SOURCES.md#F-721fc8e272)% | [3,356](SOURCES.md#F-2fa27eb955) | [1.63](SOURCES.md#F-8f07cab4a3) |
| beef / other cattle | [148](SOURCES.md#F-29ad91ee03) | [29](SOURCES.md#F-995e5fc04a) | [13.5](SOURCES.md#F-f6e59f93d8) | **[0.45](SOURCES.md#F-a3287345b7)** | [11](SOURCES.md#F-664f7732df)% | [32](SOURCES.md#F-95ace3ff70)% | [1,374](SOURCES.md#F-de77c655bb) | [0.27](SOURCES.md#F-51b87fdcec) |
| poultry | [56](SOURCES.md#F-0e1a855f5a) | [305](SOURCES.md#F-921b39b3e6) | [20.2](SOURCES.md#F-6dca9391e1) | **[0.37](SOURCES.md#F-7e3a01b4eb)** | [9](SOURCES.md#F-12f7ff58f3)% | [14](SOURCES.md#F-bedb7a3a3a)% | [8,200](SOURCES.md#F-d3ec680bbe) | [1.72](SOURCES.md#F-bf0f276793) |
| other / mixed livestock | [52](SOURCES.md#F-2201634fa5) | [2](SOURCES.md#F-30edee37e8) | [6.5](SOURCES.md#F-39cb71c3a7) | **[0.25](SOURCES.md#F-0a304e6553)** | [23](SOURCES.md#F-3ae55913a0)% | [54](SOURCES.md#F-139dd4f682)% | [-688](SOURCES.md#F-4c066f38dc) | [0.11](SOURCES.md#F-dc962563b4) |

This table is the reason the page is organised the way it is. **The type under the most
regulatory pressure is the one in the best financial condition.** Dairy has the highest
stocking density of any type, the smallest catch-crop base area, and the lowest loss rate
([5](SOURCES.md#F-c14a5994db)% of the [148](SOURCES.md#F-abee910a66) dairy filings carrying
a profit figure), the lowest share with negative equity, and a median profit per
hectare [8.9](SOURCES.md#F-abfc275815)
times that of beef. Beef and other cattle have the *highest* median equity ratio
([0.45](SOURCES.md#F-a3287345b7)) and simultaneously the highest
loss rate of any real farming type ([32](SOURCES.md#F-95ace3ff70)%) — a
combination that describes an asset-rich, income-poor holding, which is what extensive
cattle on owned land is.

### How large a shock each cohort can take

The ladder assumes no cost at all; a published estimate is laid on it two subsections
below, once the shape of the buffer is established independently of it. The question
here is only: how many holdings in each cohort go from profit to loss as an annual
charge per declared hectare rises? The break-even column is the charge the median
holding could absorb exactly.

| Enterprise type | n | Break-even (kr/ha) | [0](SOURCES.md#F-5037a4d4b9) | [500](SOURCES.md#F-5a932ec3ea) | [1,000](SOURCES.md#F-dad9c88271) | [2,000](SOURCES.md#F-476c9318f3) | [3,000](SOURCES.md#F-67a8f74466) | [5,000](SOURCES.md#F-af3d21c718) | [8,000](SOURCES.md#F-6df796cf49) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dairy | [120](SOURCES.md#F-e6adac5ddd) | [12,285](SOURCES.md#F-28e68ef56a) | [6](SOURCES.md#F-ab548c316f)% | [8](SOURCES.md#F-31f0c48e95)% | [8](SOURCES.md#F-1482af7db1)% | [12](SOURCES.md#F-838a409210)% | [17](SOURCES.md#F-aa0e3bf205)% | [20](SOURCES.md#F-87ff897124)% | [30](SOURCES.md#F-dca104422e)% |
| pigs | [121](SOURCES.md#F-c51193eb5e) | [3,356](SOURCES.md#F-c08b65366b) | [17](SOURCES.md#F-fb231197d3)% | [25](SOURCES.md#F-319dd73b4f)% | [29](SOURCES.md#F-051d8308fd)% | [37](SOURCES.md#F-62a0b35fdf)% | [45](SOURCES.md#F-336d5039ff)% | [60](SOURCES.md#F-2c27414771)% | [72](SOURCES.md#F-b206e89b77)% |
| beef / other cattle | [113](SOURCES.md#F-336834b431) | [1,374](SOURCES.md#F-fc5c0046dc) | [30](SOURCES.md#F-f025305551)% | [41](SOURCES.md#F-519667d5da)% | [46](SOURCES.md#F-e4c78b5ac2)% | [54](SOURCES.md#F-7978ebfcd0)% | [58](SOURCES.md#F-4306b1852c)% | [65](SOURCES.md#F-560e1851d9)% | [71](SOURCES.md#F-a23fa84241)% |
| poultry | [29](SOURCES.md#F-6cc9ea7717) | [8,200](SOURCES.md#F-c7dc03e151) | [21](SOURCES.md#F-c61584886c)% | [24](SOURCES.md#F-aa2dd2e495)% | [24](SOURCES.md#F-2e8ae8bbf3)% | [28](SOURCES.md#F-3cdbf8423a)% | [28](SOURCES.md#F-48a71c6c70)% | [34](SOURCES.md#F-b6a147cf38)% | [48](SOURCES.md#F-7483a3b5ae)% |
| other / mixed livestock | [33](SOURCES.md#F-db3c04c465) | [-688](SOURCES.md#F-f9a8e09514) | [55](SOURCES.md#F-1c76350f0c)% | [58](SOURCES.md#F-2dbac4dc05)% | [58](SOURCES.md#F-9b69d76855)% | [61](SOURCES.md#F-27bd67c7e8)% | [61](SOURCES.md#F-f14af9c65f)% | [67](SOURCES.md#F-faf70cfded)% | [76](SOURCES.md#F-3f9077f741)% |

*(share of the cohort making a loss once a charge of that many kroner per declared
hectare is applied to the last filed twelve-month profit)*

The gradients differ by more than the levels do. Dairy absorbs
[12,285](SOURCES.md#F-28e68ef56a) kr/ha before the median holding turns, and even
at [8,000](SOURCES.md#F-6df796cf49) kr/ha only [30](SOURCES.md#F-dca104422e)% of the cohort is loss-making.
Beef starts at [30](SOURCES.md#F-f025305551)% loss-making before
anything is applied and is at [46](SOURCES.md#F-e4c78b5ac2)% by
[1,000](SOURCES.md#F-dad9c88271) kr/ha. **The cohort with the least room is the one the instrument is least
aimed at.**

That ladder has a hole in it, and the hole is the finding of section 3. A charge per
hectare cannot be applied to a holding with no hectares, so every landless unit drops
silently out of the table above — [291](SOURCES.md#F-f63fe07208) of the
[707](SOURCES.md#F-e2f79c5f02) holdings with both a herd and a profit figure. Charging
per animal unit instead puts them back, and is anyway the better model of how the cost
reaches them: through the price of a slurry placement contract, which scales with the
slurry.

| Enterprise type | n | of which landless | Break-even (kr/DE) | [0](SOURCES.md#F-00401c4921) | [250](SOURCES.md#F-7cd17fa018) | [500](SOURCES.md#F-ced1eac0be) | [1,000](SOURCES.md#F-1c77c177c2) | [2,000](SOURCES.md#F-8ae57f9c08) | [4,000](SOURCES.md#F-e80f4580fd) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dairy | [148](SOURCES.md#F-feebc51c45) | [28](SOURCES.md#F-3bd0ff4f3a) | [6,305](SOURCES.md#F-63fb8784cf) | [5](SOURCES.md#F-84e4a4e993)% | [7](SOURCES.md#F-89da9588bf)% | [9](SOURCES.md#F-f59f1a3f72)% | [11](SOURCES.md#F-e636ef995b)% | [16](SOURCES.md#F-aa6b470eda)% | [32](SOURCES.md#F-e171858057)% |
| pigs | [303](SOURCES.md#F-1631b8b96f) | [182](SOURCES.md#F-35bb9d81ec) | [1,524](SOURCES.md#F-2705ed382f) | [23](SOURCES.md#F-1e70e1be7f)% | [30](SOURCES.md#F-a395e05924)% | [34](SOURCES.md#F-0405772934)% | [43](SOURCES.md#F-e184454ba5)% | [56](SOURCES.md#F-c27a296fe4)% | [72](SOURCES.md#F-644a142e85)% |
| beef / other cattle | [148](SOURCES.md#F-d2d602b7b5) | [35](SOURCES.md#F-b9c95f7687) | [2,667](SOURCES.md#F-c6c8dd77e5) | [32](SOURCES.md#F-d0d36e1c33)% | [34](SOURCES.md#F-061c9b439e)% | [36](SOURCES.md#F-903a0f9e32)% | [40](SOURCES.md#F-fd8e8e4805)% | [47](SOURCES.md#F-4df46e1d8f)% | [59](SOURCES.md#F-a0a21f5ccc)% |
| poultry | [56](SOURCES.md#F-e0ee673dc1) | [27](SOURCES.md#F-634357f344) | [3,846](SOURCES.md#F-93e5810296) | [14](SOURCES.md#F-b3dffbaac2)% | [20](SOURCES.md#F-ba56830910)% | [29](SOURCES.md#F-d58da7122e)% | [30](SOURCES.md#F-52a8b8c26e)% | [38](SOURCES.md#F-0cfb5855b7)% | [52](SOURCES.md#F-cef2328cc4)% |
| other / mixed livestock | [52](SOURCES.md#F-f27168d0fb) | [19](SOURCES.md#F-f1ce5e7adc) | [-750](SOURCES.md#F-ddd8677726) | [54](SOURCES.md#F-6d803ded87)% | [54](SOURCES.md#F-57876d42c8)% | [54](SOURCES.md#F-80c50a12d5)% | [54](SOURCES.md#F-7bdb54733a)% | [56](SOURCES.md#F-cff1d0c987)% | [62](SOURCES.md#F-d422ea7881)% |

*(share of the cohort making a loss once a charge of that many kroner per animal unit
is applied)*

**Changing the denominator swaps which cohort is thinnest, and it swaps pigs with
beef.** Ranked by what the median holding can absorb:

* per declared hectare — dairy [12,285](SOURCES.md#F-28e68ef56a), poultry
  [8,200](SOURCES.md#F-c7dc03e151), pigs [3,356](SOURCES.md#F-c08b65366b),
  **beef [1,374](SOURCES.md#F-fc5c0046dc)**;
* per animal unit — dairy [6,305](SOURCES.md#F-63fb8784cf), poultry
  [3,846](SOURCES.md#F-93e5810296), beef
  [2,667](SOURCES.md#F-c6c8dd77e5), **pigs
  [1,524](SOURCES.md#F-2705ed382f)**.

Dairy is the most resilient on both measures and by a similar factor, so nothing about
dairy turns on the choice. What turns on it is which of pigs and beef is the thin one.
Per hectare, beef looks like the sector with no room, because beef holds a great many
hectares against very little income. Per animal unit, pigs are, because a pig holding
concentrates a large herd on little or no land. **Whether the requirement is
denominated in hectares or in slurry decides which of those two sectors it is a crisis
for** — and that is a drafting choice, not a fact about farming.

And the landless holdings are not the healthy half of the pig cohort. Of the
[182](SOURCES.md#F-35bb9d81ec) pig holdings with accounts and no declared land,
[26](SOURCES.md#F-d2a5fd1986)% made a loss in their last filed year, against
[17](SOURCES.md#F-ad690f0daa)% of the [121](SOURCES.md#F-b66ed28c93) that do
declare land. The group most exposed to a repricing of placement contracts is also the
group already least able to absorb one.

### What a published cost estimate does to those ladders

The ladders above assume nothing. There is one published by-farm-type estimate this
project has read in its primary source, and putting it on the ladder is the point of
having built the ladder.

NUAR modelled the change in gross margin per hectare against the reference regulation,
by enterprise type, for the Hjarbæk Fjord catchment under six quota-allocation models:

| Enterprise type | Flad | Rodz | Brak | Visa | Visu | Visu2 |
|---|---:|---:|---:|---:|---:|---:|
| **Organic** | [+341](SOURCES.md#F-9912211b69) | [+523](SOURCES.md#F-1d7056c61f) | [+497](SOURCES.md#F-ec7683abea) | [+506](SOURCES.md#F-736b07d984) | [+350](SOURCES.md#F-41c03cead1) | [+435](SOURCES.md#F-a986535343) |
| **Cattle** | [-994](SOURCES.md#F-723dd2d525) | [-1,122](SOURCES.md#F-36d363339a) | [-1,149](SOURCES.md#F-0995c90a60) | [-1,129](SOURCES.md#F-6ee01e400e) | [-969](SOURCES.md#F-1dcfc6e11f) | [-1,207](SOURCES.md#F-e90a8c79dc) |
| Specialised arable | [-327](SOURCES.md#F-8135e29ac6) | [-476](SOURCES.md#F-8a2bff07cc) | [-678](SOURCES.md#F-c3ed4f168b) | [-554](SOURCES.md#F-4b3037cd2e) | [-393](SOURCES.md#F-8443d9c200) | [-552](SOURCES.md#F-6ba9c56063) |
| Pigs and arable | [-438](SOURCES.md#F-a3799264e0) | [-489](SOURCES.md#F-b2eb0654b8) | [-606](SOURCES.md#F-1bddda9c4a) | [-546](SOURCES.md#F-9b254316eb) | [-472](SOURCES.md#F-11c73c8568) | [-603](SOURCES.md#F-fe89f34b6f) |
| Small / non-specialised | [-434](SOURCES.md#F-d42ce02d2a) | [-564](SOURCES.md#F-1778a558e0) | [-548](SOURCES.md#F-1806d3b96e) | [-528](SOURCES.md#F-cab0e21330) | [-437](SOURCES.md#F-bd10210d22) | [-577](SOURCES.md#F-641ed45b59) |
| Extensified | [+80](SOURCES.md#F-658a1ce70a) | [+86](SOURCES.md#F-939d75759e) | [+247](SOURCES.md#F-f57f013f51) | [+140](SOURCES.md#F-9f6ce84d40) | [+130](SOURCES.md#F-c25abba3c4) | [+129](SOURCES.md#F-5f9af1d3df) |
| Weighted mean | [-460](SOURCES.md#F-c49248ee88) | [-541](SOURCES.md#F-6707de368d) | [-586](SOURCES.md#F-392fb2268f) | [-552](SOURCES.md#F-9102f936f9) | [-468](SOURCES.md#F-cdcaa2f7a8) | [-605](SOURCES.md#F-d16aa502d2) |

*(change in DB2, kroner per hectare, against a reference of compulsory and livestock
catch crops. Eriksen et al., NUAR, DCA rådgivningsnotat, 2024-05-24, Tabel 7.5, read from
the pinned report. The report states the pattern repeats across the [other ten catchments](SOURCES.md#F-31e7b1cd40)
analysed.)*

Three things follow, and the third is the one that matters.

**The magnitudes land on the low rungs of the ladder.** The losses run from [327](SOURCES.md#F-610bbdb7fa)
to [1,207](SOURCES.md#F-3e6cc0cd42) kroner per hectare. At [1,000](SOURCES.md#F-dad9c88271) kr/ha this page's ladder puts
[8](SOURCES.md#F-1482af7db1)% of dairy holdings into a loss,
[29](SOURCES.md#F-051d8308fd)% of pigs and
[46](SOURCES.md#F-e4c78b5ac2)% of beef and other cattle. A cost of
this size is absorbable by most of the sample — but the sample is the incorporated
[24](SOURCES.md#F-669764ddc8)% of the herd, and the ladder's zero column already shows
[30](SOURCES.md#F-f025305551)% of beef holdings loss-making before
anything is added.

**Cattle carries [1.7](SOURCES.md#F-b9a39d5828) to [3.0](SOURCES.md#F-35e3cb19e4) times the arable loss across the columns**, which is the
mechanism section 3 measured from the other side. And **organic is positive in every
column** — not exempt-and-therefore-unaffected, but better off than the reference.

**And no allocation model rescues cattle.** This is the third thing, and it is the one
that matters, because six models is what the argument has been about. Cattle's loss
lands between [-969](SOURCES.md#F-1dcfc6e11f) and [-1,207](SOURCES.md#F-e90a8c79dc) kroner per hectare in **every one of them** — a spread of
[238](SOURCES.md#F-e45c5b4954) kr/ha, or [22](SOURCES.md#F-e3b255fc89)% of its own mean loss, the narrowest relative range of any
loss-making type in the table. Specialised arable moves from [-327](SOURCES.md#F-8135e29ac6) to [-678](SOURCES.md#F-c3ed4f168b) across the
same six, a spread of [351](SOURCES.md#F-8b2011474c) kr/ha and [71](SOURCES.md#F-bde8c64840)% of its own mean loss.

So the choice being fought over is a real choice **for arable and a largely settled
question for cattle**. Picking a different quota-allocation model changes what a specialised arable holding
loses by a factor of [2.1](SOURCES.md#F-a518ca23fa); it moves a cattle holding by [22](SOURCES.md#F-e3b255fc89)% of its mean loss
and leaves it, in all six cases, losing [1.7](SOURCES.md#F-b9a39d5828) to [3.0](SOURCES.md#F-35e3cb19e4) times what the arable holding
does. **The instrument the industry is arguing about is not the instrument that decides
cattle's position — the base area is**, and the base area is fixed by what grows on the
farm.

The one thing in the report that does move cattle materially is trading: the same table
narrows cattle's loss to [-811](SOURCES.md#F-0faae0998f) kr/ha once allowances can be exchanged, which is the
largest gain of any type. That is why [section 1](#1-what-the-instrument-is-and-what-that-alone-tells-you-about-incidence)
treats the unresolved trading question as load-bearing rather than technical.

### The other side of the ledger: what the voluntary offer is worth

The Tripartite's declared main engine is not the quota. It is **voluntary land
conversion**, bought with money. So the incidence question has a second half that a
burden analysis alone misses: to whom is the offer worth taking?

The rate is published. Permanent extensification pays a **one-off** sum per hectare for
the whole commitment period — the land does not come back —
[BEK 130/2026 §18](https://www.retsinformation.dk/eli/lta/2026/130):

| | Land that was in rotation | Land that was grass |
|---|---:|---:|
| Carbon-rich soil, or a high-nitrogen-need area with wetland potential | **[82,500](SOURCES.md#F-f50f05aec7) kr/ha** | [35,500](SOURCES.md#F-1846040664) kr/ha |
| Everywhere else | [59,500](SOURCES.md#F-6884d06110) kr/ha | [27,000](SOURCES.md#F-2268bc50db) kr/ha |

Set that against what a hectare currently earns, using the same medians as the ladder
above. The figure is the number of years of the cohort's median per-hectare profit that
the payment replaces:

| Enterprise type | Median profit per ha | [82,500](SOURCES.md#F-f50f05aec7) | [59,500](SOURCES.md#F-6884d06110) | [35,500](SOURCES.md#F-1846040664) |
|---|---:|---:|---:|---:|
| dairy | [12,285](SOURCES.md#F-28e68ef56a) | [6.7](SOURCES.md#F-b55be2409a) | [4.8](SOURCES.md#F-088902b6be) | [2.9](SOURCES.md#F-0f243baa9b) |
| poultry | [8,200](SOURCES.md#F-c7dc03e151) | [10.1](SOURCES.md#F-cbaae582b4) | [7.3](SOURCES.md#F-9c7fac7a68) | [4.3](SOURCES.md#F-46e2c3b5d4) |
| pigs | [3,356](SOURCES.md#F-c08b65366b) | [24.6](SOURCES.md#F-e6249ecf87) | [17.7](SOURCES.md#F-7b644c3eb3) | [10.6](SOURCES.md#F-8a4a79bf44) |
| beef / other cattle | [1,374](SOURCES.md#F-fc5c0046dc) | [60.0](SOURCES.md#F-f4cf5b5a89) | [43.3](SOURCES.md#F-8e432f4b3a) | [25.8](SOURCES.md#F-ac1cca143f) |
| other / mixed livestock | [-688](SOURCES.md#F-f9a8e09514) | — | — | — |

**The same schedule is a very different offer depending on who is asked.** Taking each
cohort at the rate it would actually be offered — grass for beef, rotation land for
dairy — the payment replaces about **[26](SOURCES.md#F-ac1cca143f) years** of a beef hectare's margin
and about **[7](SOURCES.md#F-b55be2409a)** of a dairy hectare's. At an identical rate the gap is
wider still: [82,500](SOURCES.md#F-f50f05aec7) kr/ha is [60](SOURCES.md#F-f4cf5b5a89) years for beef
against [7](SOURCES.md#F-b55be2409a) for dairy. Against a farming horizon of a generation, one of
those is a good price and the other is not.

And the direction is the wrong way round for the nitrogen. **The holdings for which the
offer is most attractive are the extensive ones, whose hectares carry the least manure**
— beef at a median [0.27](SOURCES.md#F-51b87fdcec) DE/ha.
The holdings whose hectares carry the most are the ones for which it is worst value —
dairy at [2.00](SOURCES.md#F-2f98fa2450).

There is a second reason dairy should decline, and it is the mechanism
[the manure section of NITROGEN.md](NITROGEN.md) already predicted. **Selling a hectare out of a
land-squeezed holding raises its manure loading on every hectare that remains.** A dairy
holding at [2.00](SOURCES.md#F-2f98fa2450) DE/ha that converts land moves
*up* against the [80](SOURCES.md#F-0277d7c7e6) kg N/ha threshold and the [170](SOURCES.md#F-ccab7b1fe3) kg N/ha ceiling, not down. The
voluntary scheme and the compulsory one push it in opposite directions, and it is paid
for going the way that makes its other problem worse.

That is a prediction rather than an observation, and it is falsifiable: it says
participation in the conversion schemes should be concentrated in extensive cattle and
in arable land, and scarce among high-loading dairy. The uptake data would settle it and
this project does not have it — see [section 7](#7-what-this-cannot-establish-and-what-would).

*What this does not establish.* The one-off payment is not a like-for-like substitute
for an annual margin: it is capital against income, the tax treatment differs, the land
retains some residual value and some of it can still be grazed. The ratio above is a
comparison of magnitudes, not a discounted valuation, and a reader who wants the second
should build it. It is printed because the magnitudes differ by a factor of
[4](SOURCES.md#F-0e4b355001) between the two cattle sectors at the rates each would be
offered, and [9](SOURCES.md#F-b36319ebea) at the same rate — and no
discount rate reverses a gap of that size.

### The overlap, which is the actual answer

Exposed means at or above the indicative [0.8](SOURCES.md#F-9c41cbba7c) DE/ha line — where section 1's
[80](SOURCES.md#F-0277d7c7e6) kg N/ha threshold sits, and where three of the four requirements step up at once — or
declaring no land at all. Thin means an equity ratio below [0.20](SOURCES.md#F-02eca32ffb).

| Enterprise type | n | Exposed **and** thin | Exposed, not thin | Thin, not exposed | Neither |
|---|---:|---:|---:|---:|---:|
| dairy | [148](SOURCES.md#F-56c6664063) | **[28](SOURCES.md#F-21b56b78cf)** ([19](SOURCES.md#F-e0aefcb84a)%) | [110](SOURCES.md#F-527b3b488e) | [3](SOURCES.md#F-5911efd785) | [7](SOURCES.md#F-f861d23ac9) |
| pigs | [303](SOURCES.md#F-d847f944de) | **[81](SOURCES.md#F-c66509406a)** ([27](SOURCES.md#F-460ab7ed9f)%) | [210](SOURCES.md#F-01acef4456) | [5](SOURCES.md#F-7e4371e66a) | [7](SOURCES.md#F-163360339a) |
| beef / other cattle | [148](SOURCES.md#F-fc6a74338c) | **[22](SOURCES.md#F-654fc27493)** ([15](SOURCES.md#F-b6ee96a3e7)%) | [44](SOURCES.md#F-173c374201) | [15](SOURCES.md#F-0ce6b63d01) | [67](SOURCES.md#F-4f6c348d7b) |
| poultry | [56](SOURCES.md#F-b344e672f3) | **[12](SOURCES.md#F-f3adab4da7)** ([21](SOURCES.md#F-b20bf0f53e)%) | [37](SOURCES.md#F-1b66c6a84f) | [2](SOURCES.md#F-308803ef5f) | [5](SOURCES.md#F-59a1ade2b6) |
| other / mixed livestock | [52](SOURCES.md#F-1990d1ef79) | **[11](SOURCES.md#F-4682769ba4)** ([21](SOURCES.md#F-6f868bedf1)%) | [14](SOURCES.md#F-8388f0faa8) | [11](SOURCES.md#F-33d534f9a5) | [16](SOURCES.md#F-37f8c92545) |

First, the size of the exposed column itself:
**[569](SOURCES.md#F-fda6663d80) of
[707](SOURCES.md#F-8c13fb2adc) animal-keeping holdings with accounts
([80](SOURCES.md#F-a5fe6d26b3)%)
are on the exposed side of the line.** Above the [80](SOURCES.md#F-0277d7c7e6) kg N/ha threshold is where a
livestock holding normally is; that is not a finding about a stressed minority, it is
the ordinary condition of the sector. Which is why the second column matters more than
the first.

**[154](SOURCES.md#F-d1ed488da6) of [707](SOURCES.md#F-8c13fb2adc) ([22](SOURCES.md#F-c59742aa3e)%) are both
exposed and thin**, and [81](SOURCES.md#F-d54135e944)%
of every thin holding in the sample is also an exposed one. They hold
[105,541](SOURCES.md#F-329f3540b3) animal units. That is [4.3](SOURCES.md#F-685fa91819)%
of the national herd, but the denominator is the wrong one to reassure with: this
cohort is drawn only from the [24](SOURCES.md#F-669764ddc8)%
of the herd whose owners publish accounts, and the other
[76](SOURCES.md#F-dbe843a840)% is not
known to be in better condition. The cohort has a median herd of [435](SOURCES.md#F-ba4c96cd93) DE and a median equity
ratio of [0.08](SOURCES.md#F-b04884ce81). [51](SOURCES.md#F-37d14ba4f4) of them already
have negative equity and [60](SOURCES.md#F-b10e909c62) made a loss in their last filed year. Of those
losing money while equity is still positive (n=[24](SOURCES.md#F-8c24e9dfdf)), the median
holding has **[1.9](SOURCES.md#F-a04b5dbab1) years of equity left at its current
loss rate** — before any nitrogen cost at all.

The profile, stated as a profile: **a pig holding of [a few hundred to a few thousand](SOURCES.md#F-7a0306350f)
animal units, either landless or stocked above the higher manure threshold, with an equity ratio under [0.20](SOURCES.md#F-02eca32ffb) and a loss already on the
last filed accounts.** Pigs are
[81](SOURCES.md#F-c66509406a) of the [154](SOURCES.md#F-d1ed488da6) — [53](SOURCES.md#F-34f4fd591c)% of the cohort — and
[27](SOURCES.md#F-460ab7ed9f)% of all pig
holdings with accounts sit there, against
[19](SOURCES.md#F-e0aefcb84a)% of dairy — and
dairy is *more* exposed by every physical measure in section 3. The difference is
entirely the balance sheet. **Dairy's problem is the base area; pigs' problem is the
equity**, and only one of those can be fixed by a transition scheme.

### Two qualifications that change the reading

**The accounts are measured at a cyclical high.** Over the three filed years:

| Enterprise type | n | Median three-year cumulative profit (m. kr) | Negative over three years | Median change in equity ratio | Falling |
|---|---:|---:|---:|---:|---:|
| dairy | [124](SOURCES.md#F-59fb3b25b2) | [7.1](SOURCES.md#F-980a913f5b) | [7](SOURCES.md#F-910bd2e99a)% | [+0.066](SOURCES.md#F-b5c538cd8d) | [18](SOURCES.md#F-9154b7c333)% |
| pigs | [266](SOURCES.md#F-87d203040b) | [4.9](SOURCES.md#F-b4c2a7bddf) | [17](SOURCES.md#F-90cb347f9c)% | [+0.022](SOURCES.md#F-b1d2e01717) | [42](SOURCES.md#F-105bb9e8c9)% |
| beef / other cattle | [137](SOURCES.md#F-642ccf6d8e) | [0.2](SOURCES.md#F-968699b575) | [38](SOURCES.md#F-075ac51505)% | [+0.015](SOURCES.md#F-275d702bda) | [42](SOURCES.md#F-e4b705b88e)% |
| poultry | [52](SOURCES.md#F-926b51523e) | [2.1](SOURCES.md#F-e393ef641f) | [17](SOURCES.md#F-0c4b572571)% | [+0.068](SOURCES.md#F-ed8f00f1c6) | [29](SOURCES.md#F-5c6af14d5d)% |
| other / mixed livestock | [49](SOURCES.md#F-ad340c05ae) | [-0.2](SOURCES.md#F-8dbde396cc) | [61](SOURCES.md#F-fe9619843b)% | [-0.013](SOURCES.md#F-ce556c7feb) | [55](SOURCES.md#F-08aacc85e2)% |

Equity ratios rose over the period for every type except the mixed remainder, and
median three-year cumulative profit is positive and large for dairy and pigs. **These
balance sheets entered the policy period rebuilt.** That is why the no-buffer cohort
is as small as it is, and it means the same measurement taken after two poor years
would find a materially larger one. It also means the buffers above are real and
should not be argued away.

**Biological assets are a buffer you cannot spend twice.** The herd is on the balance
sheet — median [8.5](SOURCES.md#F-6a35ec9912)% of assets for dairy
(n=[131](SOURCES.md#F-1ad9bc5599)) and
[7.0](SOURCES.md#F-bb5ad70f28)% for pigs
(n=[197](SOURCES.md#F-0873f9e698)), where the tag is filed at all. It is the most liquid
large asset a livestock holding has and selling it is the same act as ceasing to
produce. A solvency ratio that counts it is counting the exit as the reserve.

<details class="work">
<summary>A worked example of the trap this project keeps falling into: a debt-structure finding that was a missing XBRL tag, and would have been wrong by up to [42](SOURCES.md#F-c6ef652741) percentage points</summary>

An early version of this analysis found that beef holdings carried [68% of their debt](SOURCES.md#F-3423f8a779)
short-term against [24% for dairy](SOURCES.md#F-58666d9fb4), and read that as dairy being mortgage-financed while
beef lives on the overdraft. It is a plausible story and it fits the other findings.

It was mostly an artefact. `lt_debt` is
`LongtermLiabilitiesOtherThanProvisions`, and a filing that does not present the line
does not carry the tag. Treating an absent tag as a zero is correct for the *level* of
debt — the balance-sheet identity confirms it, below — and catastrophic for the
*composition*, because it forces the short-term share to the whole of the debt for every holding that
did not file the line. Those holdings are not spread evenly:

| Enterprise type | Filings carrying `lt_debt` | Short-term share, treating absent as zero | …restricted to filings carrying both tags | Error |
|---|---:|---:|---:|---:|
| dairy | [92](SOURCES.md#F-2835bd7055)% | [24](SOURCES.md#F-d7bd78bf73)% | [21](SOURCES.md#F-e61cd7a1b3)% | [+3](SOURCES.md#F-df3c5defea) pp |
| pigs | [75](SOURCES.md#F-c2cfbda108)% | [43](SOURCES.md#F-b2eda90bc0)% | [26](SOURCES.md#F-1163e8fe7c)% | [+17](SOURCES.md#F-a4b766ef91) pp |
| beef / other cattle | [67](SOURCES.md#F-40027078f4)% | [68](SOURCES.md#F-d92171de93)% | [30](SOURCES.md#F-e3c1b42f34)% | [+38](SOURCES.md#F-e41fee58a5) pp |
| poultry | [68](SOURCES.md#F-3dd3168b3c)% | [83](SOURCES.md#F-282ed15d3a)% | [49](SOURCES.md#F-1a76fd388d)% | [+35](SOURCES.md#F-682eb6b14e) pp |
| other / mixed livestock | [65](SOURCES.md#F-a241a2e661)% | [90](SOURCES.md#F-14dd79957e)% | [48](SOURCES.md#F-4cdf7379b3)% | [+42](SOURCES.md#F-c6ef652741) pp |

The real spread is roughly [21](SOURCES.md#F-e61cd7a1b3)–[49](SOURCES.md#F-1a76fd388d)%
rather than [24](SOURCES.md#F-d7bd78bf73)–[90](SOURCES.md#F-14dd79957e)%,
and the shape survives only for poultry and the mixed remainder.

**And once corrected, the finding is gone.** Dairy, pigs and beef sit at
[21](SOURCES.md#F-e61cd7a1b3)%, [26](SOURCES.md#F-1163e8fe7c)% and
[30](SOURCES.md#F-e3c1b42f34)% — a spread too narrow to carry
any argument about who is term-financed and who is on the overdraft. That is why no
debt-composition figure appears in any table on this page. The interesting version of
this note is not that a number was corrected; it is that **the correction deleted the
finding**, and a finding that survives only in its uncorrected form was never a finding.
One further caution even on the corrected column: `st_debt` is
`ShorttermLiabilitiesOtherThanProvisions`, which includes trade payables as well as bank
debt, so it is not a measure of how much of a holding's borrowing reprices annually.

**Why the level is still safe when the composition was not.** Where the tag is
present, assets minus equity minus both debts leaves a median residual of
[1.5](SOURCES.md#F-5750790e33)%
of assets (n=[975](SOURCES.md#F-6344728541));
where it is absent, assets minus equity minus short-term debt alone leaves
[0.0](SOURCES.md#F-540738605c)%
(n=[546](SOURCES.md#F-e38bbc3063)). The
identity closes either way, so the absent tag really is a zero — the number was right
and the ratio built from it was not.

**And one that no range check catches at all.** The `gross` column is
`GrossResult`/`GrossProfitLoss` — *bruttofortjeneste*, gross profit after variable
costs. It is **not turnover**. `Revenue` is a separate tag present on about [one filing](SOURCES.md#F-3a24fefa33)
[in twenty](SOURCES.md#F-cd42aab6f9), because a Danish class B company may omit it. Every figure it produces is
plausible, correctly signed and of the right order of magnitude; a "profit margin"
computed as profit over `gross` would be a real ratio of two real numbers and would
mean something different for every firm in the sample. There is therefore **no margin
on sales anywhere on this page**. Everything is per hectare or per animal unit.
</details>

## 7. What this cannot establish, and what would

The house rule on this site is that an absence is reported as a count over a named
corpus. Here is the count. The middle column says what this page actually did, which
for several rows is *read the regulation*, and for several others is *not obtain the
data*.

| Question the brief asked | Answer here | What would answer it |
|---|---|---|
| **The allocation mechanism** | Established, from the regulations. It is a percentage of the base area, set per coastal catchment, with two manure thresholds at [30](SOURCES.md#F-67989f7136) and [80](SOURCES.md#F-0277d7c7e6) kg N/ha and a [170](SOURCES.md#F-ccab7b1fe3) kg N/ha ceiling. The texts were fetched, pinned and read. | — |
| **Which catchments carry the largest mandatory requirement** | Established for 2026/2027, from BEK 677 Annex 1: [20](SOURCES.md#F-44aa2f6ee6) catchments, [14.8](SOURCES.md#F-9a4c5e24c8)% to [34.5](SOURCES.md#F-f250c5e843)%. | — |
| **Whether high-density kommuner are also low-retention catchments** | **Not established, and not asserted.** Published evidence exists in both directions and this project has not obtained the retention grid. | The **kystvandopland** boundaries and the GEUS/AU retention grid of 2025-08-27, joined to the field-parcel geometry the sibling project already holds. Both are model outputs and both are published. Highest-value fetch on this list. |
| **On what terms discharge quotas may be transferred** | **Partly established.** LOV 759 §6 stk. 4 creates the power to permit transfer; the terms — who to whom, whether bounded within a catchment, at what price — are **not verified**. This is the most load-bearing gap on the page: transfer is worth [28](SOURCES.md#F-8581b578b3)% of cattle's modelled loss. | The implementing regulation under §6, once issued. |
| **Whether the implementing regulations under LOV 759 have been issued** | **Not established.** The act is a framework; every number that decides a holding's position is delegated. | Checking Lovtidende after the act commences on 2027-01-01. |
| **The numeric braklægningspunkt** | **Not established**, and there may be no single number: it is described as set per catchment. | The 2025-06-18 *delaftale* and the implementing act. |
| **Compensation and transition rates** | **Established for permanent extensification only**, read from the pinned BEK 130/2026 §18 in section 6. The other *tilskud* schemes were not read, and no rate for them is published here. | A pass over the other *tilskud* regulations and their annexes. |
| **Owned versus rented land** | Not established at all. The field-parcel register records who *declares* a parcel, not who owns it. | The ownership register (*Ejerfortegnelsen*) or the land register (*Tingbogen*), joined on the property identifier. The sibling project holds the GraphQL schema and has not fetched it. This is also the join that would make individual identification easy, which is a reason to publish only the distribution. |
| **Uptake of the voluntary conversion schemes, by enterprise type** | Not obtained, which is why section 6's closing argument is labelled a prediction. | The published *tilsagn* lists for skovrejsning, permanent ekstensivering and the wetland schemes, joined on CVR to the livestock register. The commitments are administered by the state and the areas are registered. |
| **Crop mix per holding** | Only the single largest declared crop, which is why section 3's base-area split is a proxy with a stated direction and unstated magnitude. | The full parcel-level crop declaration, in the same Marker layer already fetched and reduced to a top-crop summary on the way in. Recoverable without a new source, and it would turn section 3's best finding from a direction into a number. |
| **Kilograms of manure nitrogen per hectare, per holding** | Not established. Animal units were converted at a **stated** [100](SOURCES.md#F-e96ae98eaf) kg N per unit, and the declared area is not the *harmoniareal*. | The *gødningsregnskab*, which is filed by every holding and is not open. |
| **Balance sheets for arable holdings** | None exist in this data. Every filing here belongs to a livestock business — including, awkwardly, the population the targeted requirement is most aimed at. | The sibling project's crop-farmer extension, in progress. |
| **The finances of [76](SOURCES.md#F-c338feb8e8)% of the herd and [81](SOURCES.md#F-c9155a1f23)% of the land** | Not obtainable. | Nothing public. Sole proprietorships and partnerships have no filing duty. The only routes are the farm accountancy survey (*Regnskabsstatistik for jordbrug*, a sample, published in aggregate) or the advisory sector's benchmarking, which is not open. **This one does not close.** |
| **The inter-farm slurry placement contracts** | Not obtainable. Not in any register. | Nothing. These are private contracts. Their existence is inferable from the [624,963](SOURCES.md#F-4cd1d7d7ff) animal units standing on holdings with no declared land; their terms are not. |
| **The CO2e tax on agricultural emissions** | **Out of scope, and it is not law.** It is a separate instrument with a different base — modelled greenhouse-gas emissions from digestion and manure handling, not nitrogen — and therefore a different incidence, which this page does not compute. It exists as a political agreement; no implementing bill was located in the Folketing record, and the government's own stated plan is to introduce one in 2027 for entry into force in 2030. Nothing on this page should be read as covering it, and nothing on this page assumes it. | An implementing bill, if one is introduced. Until then every farm-type cost analysis of it — and there are several in circulation — is an analysis of a proposal, generally at rates and without the basic deduction that the agreement actually specifies. |
| **The *bemærkninger* to LOV 759** | Not read. The enacted text was read — §6, §11, §57 and §65 are quoted from Lovtidende — but the explanatory remarks, which is where the modelling behind the quota is described, were not. | Reading the bill's remarks. |
| **Whether the voluntary conversion programme is delivering at the rate its targets require** | Not established here. Section 6 predicts who should decline the offer; it does not measure whether they have. | The *tilsagn* registers, and the agency's own area accounting against the [250,000 ha](SOURCES.md#F-c6a4c2c4a0) afforestation and [140,000 ha](SOURCES.md#F-e350bb64f2) lowland targets. |

### The one finding that would need a name, stated without one

The highest-density holdings in the register are extreme: [8.8](SOURCES.md#F-1212114eef)
animal units per declared hectare at the 90th percentile for poultry, and a national
99th percentile far above any density that could be an operating farm. [A handful are](SOURCES.md#F-aadac35963), on
the face of it, businesses running [thousands of animal units against a single declared](SOURCES.md#F-5e757da5d7)
hectare.

**Those are not findings about farming. They are almost certainly findings about the
join.** A holding company that owns the animals while an operating company declares the
land appears here as an impossibly dense holding beside an impossibly empty one, and
nothing in either register says the two are related. Naming them would publish a false
claim about a real business, with an address attached.

What it would take to verify: the CVR ownership graph, which is public, to test whether
each extreme site's business has a parent or sibling that declares land. Until that is
done the tail of this distribution is a data-quality question and is not read as an
economic one — which is why every table above reports medians and shares above a
threshold, and none reports a maximum.

## 8. What this page concludes

1. **The instrument does not count animals.** It charges a percentage on a base area of
   cereals, maize, rape and pulses, set per coastal catchment, with step changes at [30](SOURCES.md#F-67989f7136)
   and [80](SOURCES.md#F-0277d7c7e6) kg of manure nitrogen per hectare and a flat [170](SOURCES.md#F-ccab7b1fe3) kg N/ha ceiling. The animal
   unit has had no legal force since 2017 and the cattle derogation lapsed in 2024.
2. **Dairy is the most exposed enterprise type, and not because of density.**
   [92](SOURCES.md#F-117f8f8d9a)% of dairy holdings that declare land sit
   above the higher manure threshold (n=[1,728](SOURCES.md#F-b5bcac76f6)), where three
   requirements step up at once — and only
   [34](SOURCES.md#F-6841a6753c)%
   of dairy's hectares are on holdings whose largest crop is inside the base area the
   percentage is charged on. Largest load, smallest base. The technical basis for the
   regulation says the same thing in its own words.
3. **The exposure ranking and the fragility ranking are different rankings.** Dairy is
   the most exposed and the most solvent — [5](SOURCES.md#F-c14a5994db)%
   loss-making, n=[148](SOURCES.md#F-abee910a66). Beef and other cattle are the
   least exposed and the least solvent —
   [32](SOURCES.md#F-95ace3ff70)%, n=[148](SOURCES.md#F-bd7fb93b23).
   Any account that treats "hit hardest" as one quantity is wrong about one of them.
4. **No allocation model rescues cattle.** Across the six quota-allocation models in the
   published technical basis, cattle loses between [969](SOURCES.md#F-880d1dd1d0) and [1,207](SOURCES.md#F-3e6cc0cd42) kroner per hectare — a
   spread of [22](SOURCES.md#F-e3b255fc89)% of its mean loss — while specialised arable moves by [71](SOURCES.md#F-bde8c64840)% of its own
   much smaller loss. The model choice the industry is arguing about changes arable's position and
   barely changes cattle's. Trading would; whether it exists is not established.
5. **The unit the charge is denominated in swaps which sector is thinnest.** Per hectare
   the thinnest is **beef** ([1,374](SOURCES.md#F-fc5c0046dc)
   kr/ha against [3,356](SOURCES.md#F-c08b65366b) for pigs); per animal
   unit it is **pigs** ([1,524](SOURCES.md#F-2705ed382f) kr/DE against
   [2,667](SOURCES.md#F-c6c8dd77e5) for beef). Dairy is
   most resilient on both.
6. **The landless holding is invisible to the instrument and is where its cost lands**,
   through a slurry placement contract that no register records. It is also the sicker
   half of its own sector: [26](SOURCES.md#F-d2a5fd1986)% of landless
   pig holdings with accounts made a loss last year against
   [17](SOURCES.md#F-ad690f0daa)% of those with land.
7. **The mandatory allocation for 2026/2027 is not where the animals are.** [20](SOURCES.md#F-44aa2f6ee6)
   catchments carry it, several on Zealand and the islands, and of those at the
   [34.5](SOURCES.md#F-f250c5e843)% ceiling only Kås Bredning og Venø Bugt is in Jutland — Zealand's region holding
   [6.7](SOURCES.md#F-9fd83cf2c9)% of the national
   herd at a median of [0.37](SOURCES.md#F-cd7d80c944) DE/ha. A percentage
   of a large base area on holdings with no manure is a real cost, and it falls on the
   population this page has no balance sheets for.
8. **The voluntary offer is worth least to the holdings whose land carries the most
   nitrogen.** Permanent extensification pays a one-off [82,500](SOURCES.md#F-f50f05aec7) kr/ha for rotation land
   in a priority area. That is about [7](SOURCES.md#F-b55be2409a)
   years of the median dairy hectare's profit and about
   [26](SOURCES.md#F-ac1cca143f) years of the median
   beef hectare's at the grass rate. The engine buys extensive land cheaply and
   intensive land not at all — and a land-squeezed dairy holding that sells a hectare
   moves *up* against its own manure thresholds. That is a falsifiable prediction about
   uptake, not an observation.
9. **The act that takes over in 2027 permits quotas to be transferred, and the terms are
   not public.** LOV 759 §6 stk. 4 creates the power; the implementing regulation would
   set the terms; transfer is worth [28](SOURCES.md#F-8581b578b3)% of cattle's modelled loss. It also
   carries two expropriation powers, one of them not limited to this act's own measures.
10. **[81](SOURCES.md#F-c9155a1f23)% of Danish farmland is farmed by businesses that publish nothing.** The
   individual-level question is, for most of Danish agriculture, not answerable from
   public data — and that is a finding about the public record rather than a limitation
   of this analysis.

---

*Generated by `scripts/socialcontext.py`. Do not edit this file: a later run overwrites
it, and prose added here is silently lost. The prose lives in the generator.*

*The registers are read from the sibling project
[danish-livestock](https://jjokulian.github.io/danish-livestock/), which located and
documented them; the traps in each are recorded there and in `docs/data-sources.md` of
that repository. Following the house rule, this page cites that work rather than
restating it, and computes its own aggregates from the same primary sources rather than
copying its results.*

*Every legal provision quoted here was fetched and read for this page, not taken from
coverage of it: LOV nr. 759 of 2026-09-08 (§6, §11, §57, §65), BEK 931/2024 (§14),
BEK 673/2026 (§4, §24, Annex 1 and Annex 2), BEK 677/2026 (§1, §3, §6 and Annex 1) and
BEK 130/2026 (§18), all from
[retsinformation.dk](https://www.retsinformation.dk); and the NUAR figures from the
report itself. Where this page says something is not established, it means the document
was not obtained — not that it was skimmed.*
