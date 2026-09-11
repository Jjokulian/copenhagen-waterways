#!/usr/bin/env python3
"""docs/GRUNDLAGET.md - what the Danish nitrogen requirement actually rests on.

The prose was hand-written from seven primary documents (the evidence, with verbatim
quotes, is data/manual/science_chain.json) and is carried here as it was committed.
Every figure in it is a checked entity:

  ⟦R¦SOURCE¦shown¦phrase⟧  a number read from a pinned document (data/derived/pins/,
                           sources in data/manual/claims.d/nitrogen.json). Refused
                           unless the phrase is in the pin AND the number shown is in
                           the phrase - claims.py checks only the first.
  ⟦Q¦SOURCE¦quotation⟧     a verbatim quotation, pieces joined by ' ... ', each piece
                           checked against the pin; every number in it is a reading.
  ⟦V¦key¦format⟧           a value kept, with its phrase, in nitrogen_readings.json,
                           where the page needs arithmetic on it ('pct' = x 100).
  ⟦X¦name⟧                 a figure computed in main() from V values.
  ⟦P¦SOURCE⟧               the page count of a pinned PDF: form feeds in its text.
  ⟦C¦species⟧              a chemical species, live.chem().
  ⟦W¦shown⟧                a quotation of this page's committed text, for figures
                           no pinnable document holds - this project's own tally of
                           DCE's Tabel 3, table cells the PDF extraction garbles, a
                           document that was never obtained. Honest ("the page said
                           this") and circular, so every one is counted in the log.

    python3 scripts/pages/grundlaget.py
"""
import html
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import MANUAL, ROOT, log, write_doc
import claims
import live

OUT = os.path.join(ROOT, "docs", "GRUNDLAGET.md")
PAGE = "docs/GRUNDLAGET.md"
THEN = "661ba26"            # the hand-written page this generator was made from
CL = claims.load()[0]
READ = live.live_json(os.path.join(MANUAL, "nitrogen_readings.json"))
MARK = re.compile(r"⟦(.*?)⟧")
_NUM = re.compile(r"\d+(?:[.,]\d+)*")
_pins, _cache, SELF = {}, {}, []


def _norm(t):
    """A pin as text: for a web page, entities decoded and tags dropped; for any pin,
    whitespace collapsed. (claims.py compares raw text, so a {read:} phrase that
    crosses a tag in an HTML pin can never match - those values come through rv().)"""
    head = t[:4000].lower()
    if "<html" in head or "<!doctype" in head:
        t = re.sub(r"<[^>]+>", " ", html.unescape(t))
    return re.sub(r"\s+", " ", t).strip()


def _pin(sid):
    if sid not in _pins:
        _pins[sid] = _norm(claims.pin_text(CL, sid))
    return _pins[sid]


def _nums(s):
    """The numbers in a text as values: '0,83' and '0.83' are one number, '41.988'
    (a Danish thousands point) is 41988."""
    out = set()
    for tok in _NUM.findall(s):
        if re.fullmatch(r"[1-9]\d{0,2}(?:[.,]\d{3})+", tok):
            out.add(float(re.sub(r"[.,]", "", tok)))
        else:
            out.add(float(tok.replace(",", ".")))
    return out


def R(sid, shown, phrase):
    """A number read from a pinned document, at the phrase it sits in. A range
    ('64–79') or a split ('3/4–1/4') is one reading per number, since a reading
    states one number; the separators are kept as written."""
    parts = re.split(r"(\d[\d.,]*\d|\d)", shown)
    if len(parts) > 3:
        return "".join(R(sid, p, phrase) if i % 2 else p for i, p in enumerate(parts))
    missing = _nums(shown) - _nums(phrase)
    if missing:
        raise live.Unjustified(f"{sid}: '{shown}' is not in the phrase '{phrase}'")
    return claims.resolve(CL, "{read:%s:%s|%s}" % (sid, shown, phrase), _cache)[0]


def Q(sid, quotation):
    """A verbatim quotation; each number in it read against the piece it sits in.
    Four-digit years are left as the compiler leaves them."""
    out = []
    for piece in quotation.split(" ... "):
        if _norm(piece) not in _pin(sid):
            raise live.Unjustified(f"quotation not found in the pinned text of {sid}: '{piece}'")
        out.append(_NUM.sub(lambda m: m.group(0) if re.fullmatch(r"(?:19|20)\d\d", m.group(0))
                            else R(sid, m.group(0), piece), piece))
    return " ... ".join(out)


def rv(key):
    """A value from nitrogen_readings.json - refused unless its phrase is in the pin
    and the value is printed in the phrase."""
    e = READ["pinned"][key]
    if _norm(e["phrase"]) not in _pin(e["source"]):
        raise live.Unjustified(f"nitrogen_readings.json pinned.{key}: the phrase "
                               f"'{e['phrase']}' is not in the pinned text of {e['source']}")
    if float(e["value"]) not in _nums(e["phrase"]):
        raise live.Unjustified(f"nitrogen_readings.json pinned.{key}: {float(e['value'])} "
                               f"is not in its phrase '{e['phrase']}'")
    return e["value"]


def pages(sid):
    """A pinned PDF's page count: pdftotext ends every page with a form feed."""
    n = claims.pin_text(CL, sid).count("\f")
    return live.reading(sid, "count", "form feeds (page ends) in the extracted text",
                        n, f"{n}", claims._meta(CL, sid))


def W(shown):
    SELF.append(shown)
    return live.was(THEN, PAGE, shown)


def main():
    comp = {}
    for n in ("kattegat", "bornholm", "koege", "oresund"):
        vp3, ic = rv(f"gm_{n}_vp3"), rv(f"gm_{n}_ic")
        comp["strict_" + n] = f"{(ic - vp3) / ic * 100:.0f}"      # how much stricter VP3 is
    vp3, ic = rv("gm_aalborg_vp3"), rv("gm_aalborg_ic")
    comp["looser_aalborg"] = f"{(vp3 - ic) / ic * 100:.0f}"       # shown with a minus sign

    def render(m):
        k, *a = m.group(1).split("¦")
        if k == "R":
            return R(*a)
        if k == "Q":
            return Q(*a)
        if k == "V":
            val = rv(a[0])
            return f"{val * 100:.0f}" if a[1] == "pct" else format(val, a[1])
        if k == "X":
            return comp[a[0]]
        if k == "P":
            return pages(a[0])
        if k == "C":
            return live.chem(a[0])
        if k == "W":
            return W(a[0])
        raise ValueError(f"unknown marker {m.group(0)}")

    try:
        text = MARK.sub(render, TEXT)
        write_doc(OUT, text)
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"wrote {PAGE} ({len(text):,} chars); carried as self-quotation: "
        f"{len(SELF)} ({len(set(SELF))} distinct)")
    return 0


TEXT = r'''# Grundlaget: what the Danish nitrogen requirement actually rests on

> **DRAFT — FOR REVIEW. NOT PUBLISHED.**
> Written by reading the primary method documents, not summaries of them. It contains four corrections to claims this project has already published, and those corrections have to be made before anything here goes on the site. Structured evidence with verbatim sources and per-claim verification flags is in `data/manual/science_chain.json`.

Hand-written from seven primary documents, five of which had never been opened by this project before. Generated by `scripts/pages/grundlaget.py`: every figure is read from a pinned copy of the document it comes from or, where no pinnable document holds it, quoted from this page's committed text and counted.

---

The most embarrassing possible outcome for this project would be to have spent months undermining a strawman. So this document does the opposite of what the rest of the site does. It reconstructs the case *for* the Danish nitrogen requirement, as carefully as its authors made it, at the level of what is measured and what is computed — never at the level of who signed off on it.

That rule cuts both ways and it has to. Two international expert panels endorsing something is not evidence about the something. Neither is a ministry-chaired taskforce criticising it. This project got that wrong once, in the direction of deference, and retracted a claim that turned out to be true. The correction below is in the other direction, and it is larger.

**Four claims this project has published are false.** They are listed in section 3 with what should replace them. Two of them are false in a way that makes the real argument *stronger*, which is the ordinary result of actually reading the source.

---

## 1. The data level: what is physically measured

Everything downstream comes from NOVANA, the national monitoring programme. The current programme, ⟦R¦NOVANA-2327¦2023–27¦NOVANA 2023-27⟧, is the one to read, and the numbers in it are specific.

### Water chemistry, chlorophyll and hydrography

| | |
|---|---|
| Stations | **⟦R¦NOVANA-2327¦114¦Målingerne udføres i alt på 114 stationer fordelt på 29 kontrolovervågede stationer hvert år og 85 operationelt overvågede stationer cirka hvert andet år i fjorde og kystvande⟧** |
| Sampled every year | ⟦R¦NOVANA-2327¦29¦Målingerne udføres i alt på 114 stationer fordelt på 29 kontrolovervågede stationer hvert år og 85 operationelt overvågede stationer cirka hvert andet år i fjorde og kystvande⟧ (control) |
| Sampled roughly every second year | ⟦R¦NOVANA-2327¦85¦Målingerne udføres i alt på 114 stationer fordelt på 29 kontrolovervågede stationer hvert år og 85 operationelt overvågede stationer cirka hvert andet år i fjorde og kystvande⟧ (operational) |
| Sampled in any given year | **⟦R¦NOVANA-2327¦64–79¦Årligt udføres målingerne således på 64-79 stationer i fjorde og kystvande⟧** |
| Frequency when sampled | **twice a month** |
| Water bodies to cover | **⟦R¦NOVANA-2327¦109¦Der er udpeget 109 vandområder inden for 1-sømilsgrænsen⟧** |
| Additional open-water stations | ⟦R¦NOVANA-2327¦18¦Derudover udføres profilmålinger på 18 stationer uden for 1-sømilegrænsen⟧, six times a year |

> *"⟦Q¦NOVANA-2327¦Målingerne udføres i alt på 114 stationer fordelt på 29 kontrolovervågede stationer hvert år og 85 operationelt overvågede stationer cirka hvert andet år i fjorde og kystvande.⟧"*

The chlorophyll indicator is a **May–September mean**. In a water body on the operational programme, that mean is built from roughly ten bottle samples, at one point in space, in alternate years.

### Oxygen

The iltsvind programme adds **⟦R¦NOVANA-2327¦92–107¦årligt med op mod yderligere 92-107 stationer⟧ more stations a year**, twice a month July–November (June–October in Limfjorden, where hypoxia starts earlier), monthly July–October in the open inner waters. Hydrogen sulphide is measured only *"når der er begrundet mistanke om forekomst heraf"*.

That window is set by mechanism — the stratified season is when stratification-driven hypoxia happens — so seasonal claims drawn from it are not circular. It does mean bottom-water oxygen from December to May is seen only through the routine stations.

### Sediment nutrient pools

Once, in **⟦R¦NOVANA-2327¦90¦prøver fra 90 af de 109 vandområder; årligt overvåges 16-19 stationer⟧ of ⟦R¦NOVANA-2327¦109¦prøver fra 90 af de 109 vandområder; årligt overvåges 16-19 stationer⟧** water bodies over five years, ⟦R¦NOVANA-2327¦16–19¦prøver fra 90 af de 109 vandområder; årligt overvåges 16-19 stationer⟧ stations a year, in **January–February**:

> *"Prøverne indsamles én gang på det tidspunkt af året, hvor sedimentet er mest oxideret (januar-februar)."*

The internal-loading pool is measured at its annual redox maximum, by design. That is the right choice for a comparable long-term pool measurement. It is also the state least like the warm, anoxic, releasing summer condition that the models say drives internal loading. The pool is measured; the flux is modelled.

### Biology

| What | Window | Stations / transects | Coverage |
|---|---|---|---|
| Eelgrass and flowering plants | once, **1 Jun – 30 Sep** | ⟦R¦NOVANA-2327¦502¦Undersøgelserne udføres på i alt 502 transekter, heraf 139 kontroltransekter hvert år⟧ transects; ⟦R¦NOVANA-2327¦139¦Undersøgelserne udføres på i alt 502 transekter, heraf 139 kontroltransekter hvert år⟧ annual | ⟦R¦NOVANA-2327¦103¦overvågning af ålegræs og andre blomsterplanter i 103 af de 109 vandområder⟧ of ⟦R¦NOVANA-2327¦109¦overvågning af ålegræs og andre blomsterplanter i 103 af de 109 vandområder⟧ water bodies |
| Macroalgae | once, **1 Jun – 31 Aug** | ⟦R¦NOVANA-2327¦120¦Undersøgelserne udføres på i alt 120 transekter, heraf 38 kontroltransekter hvert år⟧ transects; ⟦R¦NOVANA-2327¦38¦Undersøgelserne udføres på i alt 120 transekter, heraf 38 kontroltransekter hvert år⟧ annual | **⟦R¦NOVANA-2327¦38¦mens der overvåges for makroalger i 38 af de 109 vandområder⟧ of ⟦R¦NOVANA-2327¦109¦mens der overvåges for makroalger i 38 af de 109 vandområder⟧** |
| Soft-bottom fauna | **1 Mar – 31 May** | ⟦R¦NOVANA-2327¦110¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ stations; ⟦R¦NOVANA-2327¦15¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ annual, ⟦R¦NOVANA-2327¦95¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ every third year | ⟦R¦NOVANA-2327¦109¦overvågning af bundfauna i alle 109 vandområder inden for 1-sømilsgrænsen⟧, over five years |

> *"Overvågningen af blødbundsfaunaen gennemføres i tidsrummet 1. marts-31. maj."*

**This confirms, verbatim, the claim this project has been making.** The benthic community is counted in spring. An autumn kill is seen the following March at the earliest, after recolonisation has begun, and in most water bodies only every third year. In any given year **⟦R¦NOVANA-2327¦45–49¦I det enkelte år overvåges 45-49 stationer⟧ of ⟦R¦NOVANA-2327¦110¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧** stations are visited.

### And one thing that has to be said about the programme's own history

> *"⟦Q¦NOVANA-2327¦Dette er en opjustering i forhold til NOVANA 2017-21, hvor der ikke forekom overvågning af fytoplankton (her klorofyl) og bundfaunakvalitetselementet i alle vandområder.⟧"*

The VP3 indsatsbehov — the number now being turned into catchment quotas — was computed on the ⟦R¦NOVANA-2327¦2017–21¦NOVANA 2017-21⟧ programme, under which chlorophyll and benthic fauna were **not** monitored in every water body. The improvement is real and it postdates the numbers in force.

### What is not monitored at all

Fedtemøg as a shore condition: no extent, no biomass, no duration, no programme. Marine litter, microplastic and beach litter are monitored. Stranded decaying organic material is not.

---

## 2. The model level: three instruments, and what each one can do

The requirement for all ⟦R¦DHI-MODEL-DEL1-2015¦119¦de 119 danske marine vandområder⟧ (VP2) / ⟦R¦NOVANA-2327¦109¦Der er udpeget 109 vandområder inden for 1-sømilsgrænsen⟧ (VP3) marine water bodies is assembled from three different things.

| Instrument | Built by | Covers (VP2) | What it is |
|---|---|---:|---|
| Statistical models | DCE / Aarhus | **⟦R¦DCE-STATMOD-2015¦22¦Der er blevet udviklet statistiske modeller for 29 kystnære overvågningsstationer, som repræsenterer 22 vandområder⟧** water bodies, ⟦R¦DCE-STATMOD-2015¦29¦Der er blevet udviklet statistiske modeller for 29 kystnære overvågningsstationer, som repræsenterer 22 vandområder⟧ stations | Regressions on 1990–2012 station time series |
| Mechanistic models | DHI | **⟦R¦DHI-MODEL-DEL1-2015¦45¦I alt beskriver de mekanistiske modeller 45 vandområder⟧** water bodies | 3D hydrodynamic-ecological simulation, 2002–2011 |
| Meta-analysis | both | the remainder | Slopes borrowed from typologically similar water bodies |

Where there is neither data nor a model, rule ⟦R¦DHI-MODEL-DEL1-2015¦5¦5. I områder, hvor der hverken er data eller modeller, benyttes indsatsbehov for tilstødende vandområde⟧ applies:

> *"I områder, hvor der hverken er data eller modeller, benyttes indsatsbehov for tilstødende vandområde."*

Which is how **København Havn** gets an ⟦W¦Havn** gets an @@% requirement, with⟧% requirement, with the comment *"Øresund anvendt til at bestemme indsats til KBH"*.

### 2.1 The statistical models

Twenty-nine stations, twenty-two water bodies, requiring >⟦R¦DCE-STATMOD-2015¦15¦lange tidsserier (> 15 år)⟧-year series, on data from 1990–2012.

> *"For de fleste vandområder er der kun en enkelt moniteringsstation med tilstrækkelig datadækning til statistisk modellering, og derfor betragtes denne station som repræsentativ for vandområdet."*

The method: iterative cross-validated multiple linear regression, selecting on lowest RMSECV; then PLS on the selected variables; ⟦R¦DCE-STATMOD-2015¦3/4–1/4¦(3/4 af det totale datasæt) og et valideringssæt (1/4 af det totale datasæt)⟧ calibration/validation split for *selection*, with the final parametrisation fitted on the whole dataset. Candidate variables are N load, P load, freshwater, wind energy, irradiance, salinity, **water column stability (BV)** and **surface temperature**, each in ⟦R¦DCE-STATMOD-2015¦4¦Periode 4⟧-, ⟦R¦DCE-STATMOD-2015¦8¦8 eller 12 mdr.⟧- or ⟦R¦DCE-STATMOD-2015¦12¦Periode 4, 8 eller 12 mdr.⟧-month windows stepped back monthly — up to ⟦R¦DCE-STATMOD-2015¦43¦op til 43 månedsintervaller⟧ period combinations per variable, all tested.

Their own acceptance criteria: deviation ≤ ⟦R¦DCE-STATMOD-2015¦30¦Kriteriet for dette statistiske mål er tentativt sat til højst 30 %⟧%, R² ≥ ⟦R¦DCE-STATMOD-2015¦0.4¦kriteriet for dette statistiske mål er tentativt sat til mindst 0,4⟧, ≥ ⟦R¦DCE-STATMOD-2015¦15¦minimumsgrænsen tentativt sat til 15 datapunkter⟧ data points.

We re-extracted their Tabel 3 from the PDF and tallied it. Our totals reproduce their own summary — mean R² ⟦W¦mean R² @@ against their⟧ against their stated ⟦R¦DCE-STATMOD-2015¦0.56¦har et gennemsnit på 0,56⟧, mean deviation ⟦W¦mean deviation @@% against⟧% against their ~⟦R¦DCE-STATMOD-2015¦13¦gennemsnitlig absolut afvigelse på ca. 13 %⟧% — which is the check that the extraction is sound.

| | |
|---|---:|
| Fitted indicator-models | **⟦W¦Fitted indicator-models | **@@** | | Mean⟧** |
| Mean R² | ⟦W¦Mean R² | @@ | | Mean⟧ |
| Mean absolute deviation | ⟦W¦mean deviation @@% against⟧% |
| **Below their own R² ≥ ⟦R¦DCE-STATMOD-2015¦0.4¦kriteriet for dette statistiske mål er tentativt sat til mindst 0,4⟧ criterion** | **⟦W¦@@** | | Above their own⟧** |
| Above their own ⟦R¦DCE-STATMOD-2015¦30¦Kriteriet for dette statistiske mål er tentativt sat til højst 30 %⟧% deviation criterion | ⟦W¦deviation criterion | @@ | | **Flagged⟧ |
| **Flagged with systematic deviations** | **⟦W¦systematic deviations** | **@@** | | Failing⟧** |
| Failing at least one numeric criterion | ⟦W¦numeric criterion | @@ | The good⟧ |

The good ones are genuinely good: Ringkøbing TN R² ⟦W¦good: Ringkøbing TN R² @@, Vejle TP⟧, Vejle TP ⟦W¦R² 0.96, Vejle TP @@, Riisgårde TP 0.92,⟧, Riisgårde TP ⟦W¦TP 0.97, Riisgårde TP @@, Randers TN 0.86.⟧, Randers TN ⟦W¦Randers TN @@. The bad⟧. The bad ones are genuinely bad: Ringkøbing TP R² ⟦W¦bad: Ringkøbing TP R² @@, Nissum TP⟧, Nissum TP ⟦W¦Nissum TP @@, Odense chlorophyll⟧, Odense chlorophyll ⟦W¦Odense chlorophyll @@, Thisted⟧, Thisted chlorophyll ⟦W¦Thisted chlorophyll @@% deviation.⟧% deviation. Models below the threshold are carried forward, marked yellow rather than green — *"man skal være varsom ved anvendelse af modellen"*.

That is a defensible way to run a screening exercise. It is a different thing to use as the basis for a per-catchment quota, and the difference is entirely in what the number is subsequently asked to do.

**And then there is this sentence,** which is the most consequential in the document and appears in a parenthesis:

> *"Det er dog som hovedregel fosfortilførslen, der styrer klorofylkoncentrationen i forårsperioden (resultater ikke vist), men da denne periode ikke er inkluderet i den interkalibrerede klorofylindikator, er det kvælstoftilførslen, der oftest udvælges som forklaringsvariabel for klorofylkoncentrationen."*

Phosphorus governs spring chlorophyll. The intercalibrated chlorophyll indicator is May–September, which excludes spring. Nitrogen is therefore what gets selected. **The choice of indicator window is doing causal work**, the authors say so plainly, and the supporting results are not shown.

Their own stated limitation:

> *"Da modellerne er opstillet, kalibreret og valideret i en periode med relativt høje næringsstoftilførsler er beregningen af indsatsbehovet afhængig af, at de fundne relationer ... ikke ændres over tid f.eks. som følge af regimeskift, klimaændringer mm. Det er imidlertid ikke muligt at forudsige om og evt. hvornår der vil indtræffe f.eks. regimeskift bl.a. fordi det empiriske grundlag for oliogotrofieringsprocessen er mangelfuldt."*

### 2.2 The mechanistic models — the question this project had not checked

**Do the DHI models contain stratification, temperature and seasonality that the statistical models lack? Yes. All three, and more.**

Five models: one regional (inner Danish waters including the whole Baltic to Skagerrak), three local (Limfjorden, Odense Fjord, Roskilde Fjord), one North Sea hydrodynamic model. Four carry ecosystem modules.

| | |
|---|---|
| Dimensions | **⟦R¦DHI-MODEL-DEL2-2015¦3¦beskriver forholdene i 3 dimensioner⟧** |
| State variables | **more than ⟦R¦DHI-MODEL-DEL2-2015¦50¦mere end 50 primære tilstandsvariable, hvor ca. halvdelen er tilknyttet bunden⟧** primary, about half benthic |
| Time step | a few minutes |
| Output | every ⟦W¦Output | every @@ hours | |⟧ hours |
| Period | 2002–2011; first five years spin-up; 2007–2011 used |

**Stratification** is not a parameter but the emergent result of solving temperature and salinity in three dimensions, and it is validated as such — BIAS ≤ ⟦R¦DHI-MODEL-DEL2-2015¦1¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧ psu / ⟦R¦DHI-MODEL-DEL2-2015¦1¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧ °C and RMSE ≤ ⟦R¦DHI-MODEL-DEL2-2015¦2¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧ psu / ⟦R¦DHI-MODEL-DEL2-2015¦2¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧ °C for at least ⟦R¦DHI-MODEL-DEL2-2015¦80¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧% of surface *and bottom* measurements in open waters.

**Temperature:** *"Produktionen af fytoplankton (primærproduktionen) er bestemt af vandtemperaturen og tilgængeligheden af næringsstoffer og lys."*

**Seasonality:** *"kan modellerne simulere dag-til-dag, måned-til-måned og år-til-år variationer"*, with a chlorophyll:carbon ratio that varies over the year, and sediment N and P pools that accumulate in autumn and winter and release over summer.

**And oxygen:**

> *"De mekanistiske modeller beskriver iltkoncentrationerne i alle vanddybder gennem hele året, og inkluderer effekter af iltsvind på både ålegræs og filtrerende bunddyr."*

With redox chemistry underneath it: phosphate bound to ⟦C¦Fe3+⟧ under oxic conditions and released when the iron reduces; nitrate denitrified at low oxygen; ammonium efflux rising during hypoxia. And an eelgrass feedback: eelgrass biomass suppresses resuspension, which reduces light attenuation, which favours eelgrass.

The validation numbers for the inner Danish waters model, against **⟦R¦DHI-MODEL-DEL2-2015¦12¦Der er anvendt i alt 12 NOVANA målestationer til validering af vandkvaliteten, ligeligt fordelt⟧** NOVANA stations:

| Parameter | Result |
|---|---|
| TN | BIAS ~⟦R¦DHI-MODEL-DEL2-2015¦15¦gennemsnitlig BIAS-afvigelse på ~15% hhv. ~20%⟧% |
| TP | BIAS ~⟦R¦DHI-MODEL-DEL2-2015¦20¦gennemsnitlig BIAS-afvigelse på ~15% hhv. ~20%⟧% |
| DIN | BIAS ~⟦R¦DHI-MODEL-DEL2-2015¦15¦Opløst uorganisk kvælstof (DIN) modelleres også med en BIAS-afvigelse på ~15%⟧% |
| DIP | BIAS ~⟦R¦DHI-MODEL-DEL2-2015¦35¦mens afvigelsen på fosfat (DIP) er større © DHI - mvv_documentation_dhi_model_metode-slutrap-del2 / aer /2015-03-23 16 (~35%)⟧% |
| **Bottom-water oxygen** | **BIAS < ⟦R¦DHI-MODEL-DEL2-2015¦0.5¦Iltkoncentrationerne i bundvandet er beskrevet med en BIAS-afvigelse på <0,5 mg/l og med en høj forklaringsgrad (R2=0.83)⟧ mg/l, R² = ⟦R¦DHI-MODEL-DEL2-2015¦0.83¦Iltkoncentrationerne i bundvandet er beskrevet med en BIAS-afvigelse på <0,5 mg/l og med en høj forklaringsgrad (R2=0.83)⟧** |
| Chlorophyll, full year | BIAS < ⟦R¦DHI-MODEL-DEL2-2015¦30¦svarende til en BIAS-afvigelse på under 30%, og modellen kan forklare 36% af variationen i målingerne gennem perioden (R2=0,36)⟧%, R² = ⟦R¦DHI-MODEL-DEL2-2015¦0.36¦svarende til en BIAS-afvigelse på under 30%, og modellen kan forklare 36% af variationen i målingerne gennem perioden (R2=0,36)⟧ |
| Chlorophyll, summer indicator window | BIAS ⟦R¦DHI-MODEL-DEL2-2015¦0.3¦gennemsnitlig BIAS-afvigelse på 0,3 µg/l og en høj forklaringsgrad (R2=0.71)⟧ µg/l, **R² = ⟦R¦DHI-MODEL-DEL2-2015¦0.71¦gennemsnitlig BIAS-afvigelse på 0,3 µg/l og en høj forklaringsgrad (R2=0.71)⟧** |
| Kd | BIAS < ⟦R¦DHI-MODEL-DEL2-2015¦20¦I IDF modellen gengives Kd med en gennemsnitlig BIAS-afvigelse på under 20%⟧% |
| Eelgrass biomass | could not be validated systematically |

Twelve stations for a model spanning Kattegat, the Belts and the western Baltic is thin. But **bottom-water oxygen at R² ⟦R¦DHI-MODEL-DEL2-2015¦0.83¦Iltkoncentrationerne i bundvandet er beskrevet med en BIAS-afvigelse på <0,5 mg/l og med en høj forklaringsgrad (R2=0.83)⟧ is the best-validated ecological output in either document**, and it is for exactly the quantity this project has been claiming has no model.

### 2.3 How the slope is obtained — and what it is a slope of

Eight runs per model: present-day, six reduction runs, and a pre-industrial reference. The reduction levels are Danish nitrogen at **−⟦R¦DHI-MODEL-DEL2-2015¦15¦Nutid minus 15% Nutid minus 30% Nutid minus 60%⟧%, −⟦R¦DHI-MODEL-DEL2-2015¦30¦Nutid minus 15% Nutid minus 30% Nutid minus 60%⟧%, −⟦R¦DHI-MODEL-DEL2-2015¦60¦Nutid minus 15% Nutid minus 30% Nutid minus 60%⟧%**, crossed with phosphorus at present or −⟦R¦DHI-MODEL-DEL2-2015¦10–20¦reduktionerne varierer derfor i intervallet 10-20%⟧%.

> *"i en given modelkørsel reduceres alle danske kvælstoftilførsler med samme procenttal"*

The dose-response curve is then a **straight line through three simulated points**:

> *"⟦Q¦DHI-MODEL-DEL2-2015¦De 5 trendlinjer er baseret på resultaterne fra de 3 modelkørsler, hvor N er reduceret 15%, 30% eller 60% ift. nutid (2007-2011)⟧ ..."*
> *"Relationens trendlinje er vist som en ret linje. Reelt er den svagt buet (konkav), men inden for det spektrum, som er dækket af modelkørslerne, er forskellen fra en retlinjet funktion ikke signifikant."*

And in every run:

> *"Alle andre ydre forhold er fastholdt uændrede."*
> *"alt andet end næringstilførslerne er holdt konstant"*

Meteorology, climate, boundary hydrography, every other pressure: frozen at 2002–2011. Non-Danish Baltic loads reduced per HELCOM BSAP, assumed fulfilled by 2021 by decision of Naturstyrelsen. Atmospheric deposition reduced per the Gothenburg Protocol.

Phosphorus turned out not to matter for the two indicators, so the final figures use nitrogen-only runs.

**This is the right design for the question they were asked** — what does reducing Danish nitrogen do — and it is stated openly. It is the wrong instrument for the question the number is used to answer in public, which is *what caused the observed state*. A slope obtained by varying one input while freezing everything else is a partial derivative. It cannot attribute an observed change, because nothing else was allowed to vary.

### 2.4 Only two indicators come out

> *"Samlede indsatsbehov beregnes som gennemsnit af indsatsbehov for de to indikatorer"*

Summer chlorophyll and summer Kd. Nothing else. Why:

> *"den nuværende modeludvikling fokuserer udelukkende på de EU interkalibrerede kvalitetselementer fytoplankton og bundvegetation"*

The model computes oxygen at all depths year-round, validated at R² ⟦R¦DHI-MODEL-DEL2-2015¦0.83¦Iltkoncentrationerne i bundvandet er beskrevet med en BIAS-afvigelse på <0,5 mg/l og med en høj forklaringsgrad (R2=0.83)⟧, and none of it reaches the requirement. **The gate is not the physics and not the data. It is that only intercalibrated quality elements were in scope, and oxygen has no intercalibrated indicator.**

### 2.5 The Danish share — their number, for our bay

DHI computed, for each of the ⟦R¦DHI-MODEL-DEL2-2015¦45¦resultaterne for 45 vandområder accepteret⟧ water bodies, what fraction of each indicator can be explained by Danish land-based nitrogen.

| Water body | Chlorophyll | Kd |
|---|---:|---:|
| Hjarbæk Fjord | ⟦R¦DHI-MODEL-DEL2-2015¦93.9¦Hjarbæk Fjord 158 93,9 21,3⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦21.3¦Hjarbæk Fjord 158 93,9 21,3⟧% |
| Roskilde Fjord, indre | ⟦R¦DHI-MODEL-DEL2-2015¦85.3¦Roskilde Fjord, indre 2 85,3 100a⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦100¦Roskilde Fjord, indre 2 85,3 100a⟧% |
| Bjørnholms Bugt / Skive / Lovns | ⟦R¦DHI-MODEL-DEL2-2015¦83.2¦Skive Fjord, Lovns Bredning 157 83,2 33,6⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦33.6¦Skive Fjord, Lovns Bredning 157 83,2 33,6⟧% |
| Odense Fjord, ydre | ⟦R¦DHI-MODEL-DEL2-2015¦65.2¦Odense Fjord, ydre 92 65,2 57,5⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦57.5¦Odense Fjord, ydre 92 65,2 57,5⟧% |
| Limfjorden, central | ⟦R¦DHI-MODEL-DEL2-2015¦62.1¦Langeraka 156 62,1 20,5⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦20.5¦Langeraka 156 62,1 20,5⟧% |
| Kattegat, Nordsjælland | ⟦R¦DHI-MODEL-DEL2-2015¦5.2¦Kattegat, Nordsjælland 200 5,2 3,1⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦3.1¦Kattegat, Nordsjælland 200 5,2 3,1⟧% |
| **Køge Bugt** | **⟦R¦DHI-MODEL-DEL2-2015¦2.8¦Køge Bugt 201 2,8 2,7⟧%** | **⟦R¦DHI-MODEL-DEL2-2015¦2.7¦Køge Bugt 201 2,8 2,7⟧%** |
| Nordlige Øresund | ⟦W¦| Nordlige Øresund | @@% | 1.5% |⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦1.5¦Nordlige Øresund 6 2;6 1,5⟧% |
| Femerbælt | ⟦R¦DHI-MODEL-DEL2-2015¦1.9¦Femerbælt 208 1,9 3,2⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦3.2¦Femerbælt 208 1,9 3,2⟧% |
| Fakse Bugt | ⟦R¦DHI-MODEL-DEL2-2015¦1.0¦Fakse Bugt 46 1,0 0,7⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦0.7¦Fakse Bugt 46 1,0 0,7⟧% |
| Østersøen, Bornholm | ⟦R¦DHI-MODEL-DEL2-2015¦0.2¦Østersøen, Bornholm 56 0,2 0,3⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦0.3¦Østersøen, Bornholm 56 0,2 0,3⟧% |

> *"⟦Q¦DHI-MODEL-DEL2-2015¦Effekten af kvælstofreduktioner på indikatorerne varierer fra mindre end 5% til mere end 90%.⟧"*

This is the strongest single piece of evidence anywhere in the chain and **it is theirs, not ours**. The gradient is real, physically obvious and correctly modelled: closed fjords are dominated by their own catchment, open water is dominated by the Baltic. It is also almost entirely absent from how the national total is discussed.

Køge Bugt at ⟦R¦DHI-MODEL-DEL2-2015¦2.8¦Køge Bugt 201 2,8 2,7⟧%. Copenhagen Harbour with no model, taking Øresund's ⟦W¦model, taking Øresund's @@% by rule⟧% by rule ⟦R¦DHI-MODEL-DEL1-2015¦5¦5. I områder, hvor der hverken er data eller modeller, benyttes indsatsbehov for tilstødende vandområde⟧.

### 2.6 The uncertainty, and what it excludes

The ensemble method — comparing the two model types where both exist — is the correct approach when there is no ground truth, and it is this project's own principle of independent checks with unrelated failure modes, applied by them. It runs on **⟦R¦DHI-MODEL-DEL1-2015¦11¦For 11 områder findes der både statistiske og mekanistiske modeller⟧ of ⟦R¦DHI-MODEL-DEL1-2015¦119¦de 119 danske marine vandområder⟧** water bodies:

| Water body | Mechanistic | Statistical |
|---|---:|---:|
| Hjelm Bugt | ⟦R¦DHI-MODEL-DEL1-2015¦0¦Hjelm Bugt 135 0 18⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦18¦Hjelm Bugt 135 0 18⟧% |
| Roskilde Fjord, indre | ⟦R¦DHI-MODEL-DEL1-2015¦4¦Roskilde Fjord, indre 448 4 11⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦11¦Roskilde Fjord, indre 448 4 11⟧% |
| Århus Bugt | ⟦R¦DHI-MODEL-DEL1-2015¦7¦Århus Bugt, Kalø og Begtrup Vig 556 7 2⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦2¦Århus Bugt, Kalø og Begtrup Vig 556 7 2⟧% |
| Odense Fjord, ydre | ⟦R¦DHI-MODEL-DEL1-2015¦23¦Odense Fjord, ydre 132 23 26⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦26¦Odense Fjord, ydre 132 23 26⟧% |
| Storebælt NV | ⟦R¦DHI-MODEL-DEL1-2015¦34¦Storebælt, NV 163 34 44⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦44¦Storebælt, NV 163 34 44⟧% |
| Lillebælt syd | ⟦R¦DHI-MODEL-DEL1-2015¦36¦Lillebælt, syd 595 36 32⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦32¦Lillebælt, syd 595 36 32⟧% |
| Limfjorden vest | ⟦R¦DHI-MODEL-DEL1-2015¦37¦Nissum Bredning, Thisted Bredning, 9020Kås Bredning, 37 Løgstør Bredning, 31⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦31¦Nissum Bredning, Thisted Bredning, 9020Kås Bredning, 37 Løgstør Bredning, 31⟧% |
| Åbenrå Fjord | ⟦R¦DHI-MODEL-DEL1-2015¦41¦Åbenrå Fjord 138 41 50⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦50¦Åbenrå Fjord 138 41 50⟧% |
| Skive og Lovns | ⟦R¦DHI-MODEL-DEL1-2015¦52¦Skive Fjord52og Lovns Bredning 60⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦60¦Skive Fjord52og Lovns Bredning 60⟧% |
| Nordlige Lillebælt | ⟦R¦DHI-MODEL-DEL1-2015¦56¦834 56 58 367 350 359 224 Nordlige Lillebælt⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦58¦834 56 58 367 350 359 224 Nordlige Lillebælt⟧% |
| Det Sydfynske Øhav | ⟦R¦DHI-MODEL-DEL1-2015¦30¦Det Sydfynske Øhav 346 30 40⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦40¦Det Sydfynske Øhav 346 30 40⟧% |

Reported: ⟦R¦DHI-MODEL-DEL1-2015¦6–28¦for det enkelte vandområde er mellem 6% og 28%⟧% per water body, mean ⟦R¦DHI-MODEL-DEL1-2015¦16¦Den gennemsnitlige usikkerhed på målbelastningen for det enkelte vandområde er 16%⟧%; nationally ±⟦R¦DHI-MODEL-DEL1-2015¦9¦Og usikkerheden i % er derfor: 9%⟧% on the indsatsbehov. Three things about that figure, all of them stated by the authors:

> *"Da der ikke findes dokumentation for den 'rigtige' målbelastning, kan man ikke på traditionel vis bestemme, hvor sikkert modellerne estimerer målbelastningen."*

> *"Den usikkerhed, som er beregnet her, forholder sig udelukkende til usikkerheden på effekt i forhold til en reduktion i kvælstof, og det vil sige den model-tekniske usikkerhed. **Usikkerhedsanalysen inkluderer ikke eventuelle usikkerheder på målinger, fastlæggelse af statusværdier og bestemmelse af miljømål.**"*

> *"For illustrationens skyld kan man antage, at variansen estimeret for de ensemble modellerede områder kan overføres til de resterende områder ved skalering med målbelastningen."*

The national ±⟦R¦DHI-MODEL-DEL1-2015¦9¦Og usikkerheden i % er derfor: 9%⟧% is an illustration, on ⟦R¦DHI-MODEL-DEL1-2015¦11¦For 11 områder findes der både statistiske og mekanistiske modeller⟧ of ⟦R¦DHI-MODEL-DEL1-2015¦119¦de 119 danske marine vandområder⟧ water bodies, covering the slope and not the status value or the target value. It is a lower bound presented without that word.

### 2.7 How the requirement is actually assembled

```
indsatsbehov = 100 · ((Status − Miljømål) / Status) · (1 / hældning)
```

Five indicators, weighted, averaged:

| Indicator | Weight | How its requirement is derived |
|---|---:|---|
| Chlorophyll | **⟦R¦DCE-STATMOD-2015¦2¦(2𝑋1 + 𝑋2 + 𝑋3 + 𝑋4 + 2𝑋5 )/7⟧** | continuous, from the fitted slope |
| Kd / eelgrass proxy | **⟦R¦DCE-STATMOD-2015¦2¦(2𝑋1 + 𝑋2 + 𝑋3 + 𝑋4 + 2𝑋5 )/7⟧** | distance computed, then **binned into ⟦V¦kd_bin_0¦pct⟧, ⟦V¦kd_bin_1¦pct⟧, ⟦V¦kd_bin_2¦pct⟧ or ⟦V¦kd_bin_3¦pct⟧%** |
| Iltsvind | ⟦W¦| N-limitation | @@ | computed to⟧ | **binary trigger**, then a flat ⟦R¦DCE-STATMOD-2015¦25¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration⟧% cut in TN concentration |
| DIP + Chl-a seasonality | ⟦W¦| N-limitation | @@ | computed to⟧ | same trigger, same flat ⟦R¦DCE-STATMOD-2015¦25¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration⟧% |
| N-limitation | ⟦W¦| N-limitation | @@ | computed to⟧ | computed to reach a target number of N-limited days |

Averaging rather than taking the maximum is a deliberate choice, and an honest one:

> *"Hvis det skulle sikres, at alle indikatorer opnåede deres miljømål skulle det maksimale indsatsbehov anvendes i stedet for et gennemsnit ... Ved at anvende et gennemsnit ... minimeres risikoen for overimplementering."*

The consequence follows: **no water body is required to reach all five of its targets.**

**Oxygen.** The trigger is severe hypoxia ≥⟦R¦DCE-STATMOD-2015¦10¦kraftigt iltsvind ≥ 10 % af tiden ELLER, hvis der er moderat iltsvind ≥ 50 % af tiden⟧% of the time OR moderate hypoxia ≥⟦R¦DCE-STATMOD-2015¦50¦kraftigt iltsvind ≥ 10 % af tiden ELLER, hvis der er moderat iltsvind ≥ 50 % af tiden⟧% of the time. If triggered:

> *"⟦Q¦DCE-STATMOD-2015¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration ... det vurderes at en 25 % reduktion i TN-koncentrationen er minimumskrav for at ændre systemet.⟧"*

It is a ⟦R¦DCE-STATMOD-2015¦25¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration⟧% *concentration* cut, converted to a loading cut through the water body's fitted TN slope — which is why the oxygen column in their results shows ⟦W¦their results shows @@%, 67%, 70%,⟧%, ⟦W¦their results shows 79%, @@%, 70%, 0% rather⟧%, ⟦W¦results shows 79%, 67%, @@%, 0% rather than⟧%, ⟦W¦@@% rather than a uniform⟧% rather than a uniform ⟦R¦DCE-STATMOD-2015¦25¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration⟧. The variation comes from the TN model, not from the severity of the hypoxia. Two water bodies with identical hypoxia and different slopes get different requirements. **There is no dose-response between the oxygen condition and the required reduction, and DCE does not claim there is.** The indicator itself yields one value per six years.

**Kd.** Every Kd figure in their results tables is ⟦V¦kd_bin_0¦pct⟧, ⟦V¦kd_bin_1¦pct⟧, ⟦V¦kd_bin_2¦pct⟧ or ⟦V¦kd_bin_3¦pct⟧. That is not rounding — it is the equation. An indicator carrying two of seven weight units contributes one of four fixed values. And:

> *"Både brugen af Kd-indikatoren i stedet for ålegræssets dybdegrænse og kategoriseringen af indsatsbehov betyder, at der ikke nødvendigvis vil komme ålegræs til måldybden, selvom den danske kvælstoftilførsel reduceres i overensstemmelse med de beregnede reduktionskrav."*

In nine of the twenty-two meta-analysis water bodies the **target eelgrass depth exceeds the actual water depth**, so the Kd target is computed from the water depth instead. In several others the observed eelgrass shows better light than the Kd measurements, so Kd status is computed backwards from eelgrass. The proxy runs in both directions — Kd and eelgrass are not independent lines of evidence.

**N-limitation.** The most self-aware part of the method, and almost never quoted:

> *"⟦Q¦DCE-STATMOD-2015¦Empiriske analyser har vist, at algevæksten i kystnære havområder skal være kvælstofbegrænset i minimum 150 dage, før der kan ses en signifikant sammenhæng mellem klorofylkoncentrationer og kvælstofkoncentrationer⟧."*

Below ⟦R¦DCE-STATMOD-2015¦150¦skal være kvælstofbegrænset i minimum 150 dage⟧ N-limited days, their own central mechanism does not operate. Their response is not to exclude those water bodies but to add the reduction needed to *make* nitrogen limiting in the first place. That is a defensible engineering choice and also an admission that in those water bodies the requirement is not derived from a measured dose-response.

### 2.8 The targets

The chlorophyll target is the reference concentration from ensemble modelling times the EU-intercalibrated EQR of ⟦R¦DCE-STATMOD-2015¦0.6¦Ecological Quality Ratio (EQR) værdi på 0,6⟧. In the April 2015 method document, the supporting reference for it is:

> *"Notat om bestemmelse af grænseværdier for klorofyl (under udarbejdelse)"*

A note that had not been written. That does not make the value wrong; it means the derivation was not publicly checkable when the method was published.

And there is a live dispute about the values themselves, which is internal to the Danish process. The 2023 international panel found that the VP3 recalculation:

> *"har ... ført til uoverensstemmelser mellem de afledte G/M-grænseværdier og de interkalibrerede G/M-grænseværdier, som ligger til grund for EU-Kommissionsbeslutning 2018/229"*
> *"Det anbefales især at ophæve nedjustering af G/M-grænseværdierne i de åbne danske kystvande."*

| Water body | VP3 G/M | Intercalibrated | VP3 stricter by |
|---|---:|---:|---:|
| Kattegat, Nordsjælland >⟦R¦SO-BG-2024¦20¦205: Kattegat, Nordsjælland >20 m OW1 T.21: KVuDLSa 0,9 1,58 1,58⟧ m | ⟦V¦gm_kattegat_vp3¦.1f⟧ µg/l | ⟦V¦gm_kattegat_ic¦.2f⟧ | ⟦X¦strict_kattegat⟧% |
| Østersøen, Bornholm | ⟦V¦gm_bornholm_vp3¦.1f⟧ | ⟦V¦gm_bornholm_ic¦.2f⟧ | ⟦X¦strict_bornholm⟧% |
| **Køge Bugt** | **⟦V¦gm_koege_vp3¦.1f⟧** | **⟦V¦gm_koege_ic¦.2f⟧** | **⟦X¦strict_koege⟧%** |
| Nordlige Øresund | ⟦V¦gm_oresund_vp3¦.1f⟧ | ⟦V¦gm_oresund_ic¦.2f⟧ | ⟦X¦strict_oresund⟧% |
| Kattegat, Aalborg Bugt | ⟦V¦gm_aalborg_vp3¦.1f⟧ | ⟦V¦gm_aalborg_ic¦.2f⟧ | −⟦X¦looser_aalborg⟧% |

We take no position on which value is ecologically right — that is a dispute between qualified parties. We note only that the target sits in the numerator of the requirement equation, so this is not a marginal adjustment.

And that some targets are not reachable by Danish action at all:

> *"de danske klorofylmål i VP3 ikke vil være mulige at indfri uden yderligere indsatser fra andre lande eller supplerende indsatser målrettet atmosfærisk kvælstofdeposition, som vil ligge udover de reduktioner, som landene har forpligtet sig til"*

---

## 3. Our critique, audited

Be ruthless. Finding our own errors is a success.

### FALSE — must be corrected before anything else on this site is defended

**`F1`. "There is no coefficient anywhere between nitrogen and any outcome."**
*(LANDBRUG.md, the English summary at the foot of the page.)*
Contradicted by the correction banner at the top of the same page, and by ⟦W¦and by @@ fitted models⟧ fitted models and a validated 3D ecosystem model. This is a live internal inconsistency on a published page. **Fix immediately.**

**`F2`. "Nitrogen → oxygen depletion: no coefficient, NOT COMPUTED. No ventilation term, no state variable. A kilogram in February counts the same as a kilogram in July under a pycnocline."**
*(CAUSATION.md §2, NITROGEN.md §3, LANDBRUG.md §3.)*
False. The mechanistic models are 3D, run at minute time steps on real meteorology, resolve stratification, carry oxygen at all depths year-round, include sediment oxygen demand, redox-dependent phosphate release, denitrification and ammonium efflux — and validate bottom-water oxygen at **R² ⟦R¦DHI-MODEL-DEL2-2015¦0.83¦Iltkoncentrationerne i bundvandet er beskrevet med en BIAS-afvigelse på <0,5 mg/l og med en høj forklaringsgrad (R2=0.83)⟧**. Even the statistical models carry water-column stability and temperature as candidate variables, and select them.

**What should replace it, and it is stronger:**

1. In the **statistical route**, the oxygen requirement is a binary trigger plus a judged flat ⟦R¦DCE-STATMOD-2015¦25¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration⟧%, with no dose-response between hypoxia severity and required reduction. DCE writes *"det vurderes"*.
2. In the **mechanistic route**, oxygen is simulated and well validated and is *excluded from the indicator set* — only summer chlorophyll and summer Kd produce a requirement — because only intercalibrated quality elements were in scope.
3. In the **load accounting** that produces the ⟦V¦apportion_agriculture¦.1f⟧%, there is indeed no potency term of any kind.

The model that could compute this does compute it. The answer is excluded by the indicator set, not by the physics. That is a much better argument than the one we published.

**`F3`. "Atmospheric deposition ... is absent from every published apportionment."**
*(CAUSATION.md §1.)*
Too broad. Deposition is an explicit input to every mechanistic model and Gothenburg reductions are applied in every scenario run. **Correct claim:** it is absent from the source apportionment that produces the ⟦V¦apportion_agriculture¦.1f⟧%, which apportions the Danish land-based waterborne term only. Scope the sentence.

**`F4`. "Sediment regeneration is not a source at all in the accounting frame."**
*(CAUSATION.md §1, NITROGEN.md §1.)*
False as a statement about the evidence base. The mechanistic sediment module carries organic C, N and P pools, mineralisation, burial, iron-bound phosphate, denitrification and ammonium efflux, with seasonal accumulation and summer release. **Correct claim:** it has no row in the *load accounting*; and what NOVANA measures is the pool, once a year, in January–February when the sediment is most oxidised. The second half is new and is a better version of the point.

### NEEDS QUALIFYING

**Q1. "Nobody has published the regression of iltsvind extent on load, wind work and bottom temperature."**
A strong negative claim about the literature that we have not verified. Hansen & Rytter 2024, as quoted in the second opinion, states that *"Iltsvindets udvikling i løbet af året reguleres væsentligst af bundvandstemperaturen og de aktuelle vejrmæssige forhold, men udbredt iltsvind forudsætter en forudgående stor tilførsel af næringsstoffer"* — a summary of exactly that analysis. **Read it, or soften to "we have not found the coefficients published".** The demand itself is unaffected.

**Q2. "Halve the load and the extremes do not move."**
Three qualifications are missing. The comparison uses hand-picked years from a series whose interannual variance our own document calls the finding. The alternative hypothesis is not "no effect" but "worse without", and this comparison cannot separate them. And warming works against the load reduction over the same period, which our own §6 says. **Keep the observation, drop the word "test."** State it as: the extremes are not obviously tracking the load, the variance is dominated by year physics, and thirty-five years cannot distinguish the two readings. That is still a serious problem for a policy that has to justify a specific tonnage.

**Q3. "Most water bodies have one monitoring station."**
True and now precise — but say *which parameter*. One station per water body is right for the hydrography and water chemistry that feed the statistical models. The eelgrass programme runs ⟦R¦NOVANA-2327¦502¦Undersøgelserne udføres på i alt 502 transekter, heraf 139 kontroltransekter hvert år⟧ transects and the iltsvind programme adds ⟦R¦NOVANA-2327¦92–107¦årligt med op mod yderligere 92-107 stationer⟧ stations a year.

**Q4. "The models cannot represent state-dependence or alternative stable states."**
False for the mechanistic models, true for the statistical models and the accounting. DHI models eelgrass presence as a state with feedbacks onto light, resuspension and sediment nutrient release, and models *why* eelgrass fails to return — sandworm burial of seeds, drifting macroalgae damaging shoots, resuspension — with the note that in some areas *"forudsiger [modellen], at ålegræsvegetationen ikke genetableres i et omfang som registreret i tidligere tider. Skal der ske en genetablering i disse områder, skal nogle af de beskrevne stressfaktorer begrænses."*

That is our argument, in their document. **This is the single biggest available correction and it strengthens the project.** The alternative-stable-states case is not a heterodox objection to Danish marine science. It is inside the Danish model and it does not reach the policy instrument.

**Q5. The residual-estimator claims about the ⟦V¦apportion_agriculture¦.1f⟧%.** Not re-verified in this pass; they concern the load accounting, not the requirement chain. Out of scope here, left standing.

**Q6. "Køge Bugt cannot qualify for iltsvind however bad it gets."** The mechanism is right and better supported now. But "cannot however bad it gets" is our inference; the criterion is oxygen below ⟦R¦DCE-STATMOD-2015¦4¦koncentrationen af ilt i vandet er under 4 mg/L⟧ mg/l in bottom water. `monitoring.json` already records this as unresolved. Keep it that way.

### SURVIVES

- **Soft-bottom fauna is sampled 1 March – 31 May.** Confirmed verbatim, and strengthened: ⟦R¦NOVANA-2327¦45–49¦I det enkelte år overvåges 45-49 stationer⟧ of ⟦R¦NOVANA-2327¦110¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ stations in a given year.
- **The oxygen requirement is a judged figure, not a measured dose-response.** *"det vurderes."* This is the claim the project retracted under institutional pressure. **It was correct.** Restore it, with the mechanistic-route qualification attached.
- **Reaching the Kd target does not imply reaching the eelgrass target.** DCE says so.
- **Fedtemøg has no national monitoring.** Confirmed by exhaustion of the NOVANA programme.
- **Nitrogen mass is the wrong currency for an oxygen problem.** Unaffected.
- **Køge Bugt is the wrong shape for the national instrument.** Massively strengthened — by their number, not ours.

---

## 4. Their conclusions and ours, side by side

| Point | Theirs | Ours, corrected | Who is right |
|---|---|---|---|
| Is there a quantified nitrogen–outcome relationship? | Yes: ⟦W¦| Yes: @@ fitted models,⟧ fitted models, four validated 3D models, an ⟦R¦DHI-MODEL-DEL1-2015¦11¦For 11 områder findes der både statistiske og mekanistiske modeller⟧-water-body ensemble | Yes for summer chlorophyll and Kd. No for oxygen *as a policy quantity*. No for anything downstream of oxygen. | Both, about different links. Our error was saying "no coefficient" when we meant "not for the link the public argument turns on". |
| Stratification, temperature, seasonality in the models? | Yes, in 3D, at minute steps | Concede completely | **Them** |
| Is the slope causal? | It is the modelled response to changing Danish N, all else equal, presented as such | A partial derivative with everything else frozen — *"alt andet ... holdt konstant"*. Right instrument for "what would reducing do", wrong one for "what caused this". | **Us**, and their documents agree in their own words. A claim about *use*, not about the science. |
| Is the uncertainty adequate? | ~⟦R¦DHI-MODEL-DEL1-2015¦9¦Og usikkerheden i % er derfor: 9%⟧% nationally, from a genuine two-method ensemble | Method right, scope narrow, and they say so: ⟦R¦DHI-MODEL-DEL1-2015¦11¦For 11 områder findes der både statistiske og mekanistiske modeller⟧ of ⟦R¦DHI-MODEL-DEL1-2015¦119¦de 119 danske marine vandområder⟧, slope only, measurement/status/target excluded, national figure *"for illustrationens skyld"* | Us on scope, them on method. No dispute of fact. |
| Are the chlorophyll targets right? | Model group: VP3 values are most correct. Panel and taskforce: they diverge from the intercalibrated values and should be lifted. | No position. Note only that the target is in the numerator. | Internal Danish dispute. Report it, don't adjudicate it. |
| Is averaging five indicators right? | A deliberate choice to avoid over-implementation | Honest and defensible. Consequence: no water body must reach all five targets, and ⟦W¦five targets, and @@⟧ of ⟦R¦DCE-STATMOD-2015¦7¦(2𝑋1 + 𝑋2 + 𝑋3 + 𝑋4 + 2𝑋5 )/7⟧ weight units come from banded or judged values. | No factual dispute. |
| Is Køge Bugt in the frame? | Danish land N explains ⟦R¦DHI-MODEL-DEL2-2015¦2.8¦Køge Bugt 201 2,8 2,7⟧% of chlorophyll there | Same number | Agreement. It simply never appears in the public argument. |

---

## 5. Synthesis

### Common ground, stated honestly

- Nitrogen loading does affect summer chlorophyll and water clarity. Fitted in ⟦R¦DCE-STATMOD-2015¦22¦Der er blevet udviklet statistiske modeller for 29 kystnære overvågningsstationer, som repræsenterer 22 vandområder⟧ water bodies, simulated in ⟦R¦DHI-MODEL-DEL2-2015¦45¦resultaterne for 45 vandområder accepteret⟧ more, direction consistent everywhere.
- The effect is **strongly graded by geography** — ⟦V¦hjarbaek_chl¦.0f⟧% of the chlorophyll indicator in Hjarbæk Fjord, ⟦R¦DHI-MODEL-DEL2-2015¦0.2¦Østersøen, Bornholm 56 0,2 0,3⟧% off Bornholm. Reducing Danish nitrogen is nearly the whole story in closed fjords and nearly none of it in open water.
- Neither side has ground truth. There is no documented "right" target loading, and DHI says so.
- Hypoxia is a joint product of organic matter supply, weather and hydrography. DCE says it, the models implement it, we argue it.
- Eelgrass loss is self-reinforcing and may not reverse when light returns. DHI models it and warns of it.
- The published uncertainty covers the slope only.

### Where a reasonable person lands

The Danish evidence base is **much better than a critic who has read only the summaries would guess, and much narrower than a defender who has read only the summaries would guess.**

It supports a well-founded statement of this form:

> *Reducing Danish land-based nitrogen by X% would improve summer chlorophyll and water clarity in this water body by roughly Y%, assuming the climate does not change and our neighbours meet their commitments.*

It does not support *"nitrogen from agriculture causes N% of the oxygen depletion"*, and it says nothing about fedtemøg. **No document in the chain claims otherwise.** The gap between what the science says and what the politics says is where this project belongs — and it is a defensible place to stand precisely because the scientists' own caveats are the evidence for it.

### What would have to be true for them to be right and us wrong

- Summer chlorophyll and summer Kd would have to be adequate sufficient statistics for ecological status, so that fixing them fixes the rest. The WFD asserts this; the mechanistic models could test it and were not asked to.
- The fitted slopes would have to hold down to ⟦R¦DHI-MODEL-DEL2-2015¦30–60¦Nutid minus 15% Nutid minus 30% Nutid minus 60%⟧% reductions. Both DCE and DHI say this is unverifiable and warn that uncertainty grows with distance from the calibration domain.
- No regime shift. Both documents flag it and say it cannot be predicted.
- BSAP and the Gothenburg Protocol delivered by our neighbours, because every scenario assumes it.
- One station per water body spatially representative. DCE raises this and does not resolve it.
- The VP3 chlorophyll targets right rather than the intercalibrated ones.

### What would have to be true for us to be right and them wrong

- The unmeasured routes to shore biomass — direct organic delivery, killing in place, sediment regeneration — would have to be large relative to the growth route in the specific bays where damage is complained about. We have arithmetic suggesting it for combined sewer overflows and **no measurement**.
- The state term would have to dominate the load term. Mechanistically supported; quantified by nobody, **including us**.
- The extremes would have to be genuinely insensitive to load rather than merely noisy. Thirty-five years have not settled it.
- Fedtemøg would have to have a different driver or season from what is assumed. Currently unfalsifiable in either direction, because nothing measures it.

### The honest asymmetry

Their case rests on a documented method with stated limitations, applied beyond the range where those limitations were tested. Our case rests on identifying real omissions and has, so far, no measurement of its own for any of them.

**Those are not symmetrical positions.** The right conclusion is not that they are wrong. It is that the instrument is being asked a question it was not built for — and that the four cheapest measurements on our list would settle several of these arguments for less than the cost of a week of the policy.

---

## Sources

Structured, with verbatim quotes and per-claim `verified_by_reading` flags: `data/manual/science_chain.json`.

Primary documents read for this page:

1. Erichsen, Timmermann, Kaas, Markager, Christensen & Murray (2014, rev. 2015). *Modeller for Danske Fjorde og Kystnære Havområder – Del ⟦R¦DHI-MODEL-DEL1-2015¦1¦Havområder – Del 1 Metode til bestemmelse af målbelastning⟧. Metode til bestemmelse af målbelastning.* DHI/DCE for Naturstyrelsen. ⟦P¦DHI-MODEL-DEL1-2015⟧ pp. — [PDF](https://sgavmst.dk/media/hvomfapx/31-modeller-for-danske-fjorde-og-kystnaere-havomraader-del-1.pdf)
2. Erichsen & Kaas (2015). *… – Del ⟦R¦DHI-MODEL-DEL2-2015¦2¦Havområder – del 2 Mekanistiske modeller og metode til bestemmelse af indsatsbehov⟧. Mekanistiske modeller og metode til bestemmelse af indsatsbehov.* DHI. ⟦P¦DHI-MODEL-DEL2-2015⟧ pp. — [PDF](https://edit.mst.dk/media/lspfqzss/312-modeller-for-danske-fjorde-og-kystnaere-havomraader-del-2.pdf)
3. Timmermann, Christensen, Murray & Markager (2015). *… – Del ⟦R¦DCE-STATMOD-2015¦3¦Havområder – del 3 Statistiske modeller og metoder til bestemmelse af indsatsbehov⟧. Statistiske modeller og metoder til bestemmelse af indsatsbehov.* DCE/AU. ⟦P¦DCE-STATMOD-2015⟧ pp. — [PDF](https://dce.au.dk/fileadmin/dce.au.dk/Udgivelser/Notater_2015/Dokumentation_statistiske_modeller_metoder_del3_28042015.pdf)
4. Miljøstyrelsen (2023). *NOVANA. Det nationale overvågningsprogram for vandmiljø og natur ⟦R¦NOVANA-2327¦2023-27¦NOVANA 2023-27⟧.* — [PDF](https://www2.mst.dk/Udgiv/publikationer/2023/09/978-87-7038-556-5.pdf)
5. Finansministeriet m.fl. (Sept 2024). *Second opinion – Evaluering af det faglige grundlag for kvælstofindsatsen.*
6. Finansministeriet m.fl. (Nov 2024). *Second opinion – Baggrundsanalyser.* ⟦P¦SO-BG-2024⟧ pp.
7. Miljøministeriet. *Retningslinjer for udarbejdelse af vandområdeplaner 2021-2027.*

**Not obtained, and this limits the page.** Herman et al. 2017 and 2023 are quoted only through the ministries' Danish translation, which itself warns that editorial choices were made. Erichsen et al. 2023 — the VP3 model update to ⟦W¦update to @@ mechanistic models⟧ mechanistic models over ⟦W¦models over @@ water bodies⟧ water bodies — has not been read, so **every model-level number here is VP2-era unless marked otherwise**. Hansen & Rytter 2024, Timmermann et al. `2024a/b`, Erichsen et al. `2019/2020a/2020b` and Markager & Storm 2003 are cited from reference lists only.
'''


if __name__ == "__main__":
    sys.exit(main())
