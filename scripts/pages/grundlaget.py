#!/usr/bin/env python3
"""docs/GRUNDLAGET.md - what the Danish nitrogen requirement actually rests on.

The case for the Danish nitrogen requirement, read from its primary method documents
(pinned in data/derived/pins/; sources in data/manual/claims.d/). Every figure is a
checked entity, and every assertion a checked claim (LIVE_NUMBERS.md section 11),
registered in data/manual/claims.d/w3-gc.json with what it rests on. What the page once
said and could not justify is in docs/ARCHIVE.md, not here.

Markers in TEXT:

  ⟦R¦SOURCE¦shown¦phrase⟧  a number read from a pinned document. Refused unless the
                           phrase is in the pin AND the number shown is in the phrase.
  ⟦Q¦SOURCE¦quotation⟧     a verbatim quotation, pieces joined by ' ... ', each piece
                           checked against the pin; every number in it is a reading.
  ⟦V¦key¦format⟧           a value kept, with its phrase, in nitrogen_readings.json,
                           where the page needs arithmetic on it ('pct' = x 100).
  ⟦X¦name⟧                 a figure computed in main() from read values.
  ⟦T¦field¦format⟧         a figure of the Tabel 3 tally in data/derived/grundlaget.json.
  ⟦N¦SOURCE¦term⟧          how many times a term occurs in a pinned document.
  ⟦P¦SOURCE⟧               the page count of a pinned PDF: form feeds in its text.
  ⟦C¦species⟧              a chemical species, live.chem().
  ⟦B¦C-ID⟧ ... ⟦E⟧         a checked claim.

The Tabel 3 tally is computed here from the pinned text of DCE's statistical-model
report (tabel3()) and stored in data/derived/grundlaget.json. Peak memory: one pinned
text.

    python3 scripts/pages/grundlaget.py
"""
import html
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import DERIVED, MANUAL, ROOT, log, read_json, write_doc, write_json
import claims
import live

OUT = os.path.join(ROOT, "docs", "GRUNDLAGET.md")
TALLY = os.path.join(DERIVED, "grundlaget.json")
PAGE = "docs/GRUNDLAGET.md"
DCE = "DCE-STATMOD-2015"
CL = claims.load()[0]
READ = live.live_json(os.path.join(MANUAL, "nitrogen_readings.json"))
MARK = re.compile(r"⟦(.*?)⟧")
_NUM = re.compile(r"\d+(?:[.,]\d+)*")
_pins, _cache = {}, {}


def _norm(t):
    """A pin as text: for a web page, entities decoded and tags dropped; for any pin,
    whitespace collapsed."""
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


def rval(sid, value, phrase):
    """A number read from a pinned document as a live value, for arithmetic: refused
    unless the phrase is in the pin and the value is printed in the phrase."""
    if _norm(phrase) not in _pin(sid):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    if float(value) not in _nums(phrase):
        raise live.Unjustified(f"{sid}: {value} is not in the phrase '{phrase}'")
    return live.reading_value(sid, "phrase", phrase, value, claims._meta(CL, sid))


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


def tabel3():
    """Tabel 3 of DCE's statistical-model report, tallied from its pinned text.

    The extraction lists each block of the table as its variable lists, then the
    block's deviations, then its R2 values, then its ja/nej for systematic deviation,
    column by column, so within a block the k-th deviation, the k-th R2 and the k-th
    ja/nej are one model. A block is refused unless it holds exactly two numbers per
    ja/nej; each half of the table is refused unless its variable lists match its
    models; and the whole is refused unless its model count matches observing.py's
    independent parse. The two acceptance criteria are read from the report's own
    sentences, not typed."""
    t = claims._norm(claims.pin_text(CL, DCE))
    a = t.find("Tabel 3: Oversigt")
    b = t.find("De forklaringsvariable, som giver den bedste beskrivelse")
    if a < 0 or b < a:
        raise live.Unjustified(f"Tabel 3 not found in the pinned text of {DCE}")
    var = r"(?:N-load|P-load|temp|vind|salt|irr|BV|Q)"
    grp = re.compile(r"%s(?:,%s)*,?" % (var, var))
    models, lists = [], []
    for part in t[a:b].split("Tabel 3 fortsat"):
        body = part[part.find("vurdering") + len("vurdering"):]
        rows, groups, dec, yn, cur = [], [], [], [], None

        def close():
            if yn:
                if len(dec) != 2 * len(yn):
                    raise live.Unjustified(f"Tabel 3 of {DCE}: a block holds {len(dec)} "
                                           f"numbers for {len(yn)} ja/nej")
                rows.extend(zip(dec[:len(yn)], dec[len(yn):], yn))
                dec.clear()
                yn.clear()
        for tk in body.split():
            if re.fullmatch(r"\d+\.\d+", tk):
                close()
                dec.append(float(tk))
                continue
            if tk in ("ja", "nej"):
                yn.append(tk)
                continue
            close()
            if grp.fullmatch(tk):
                if cur is not None and cur.endswith(","):
                    cur += " " + tk
                else:
                    if cur is not None:
                        groups.append(cur)
                    cur = tk
                continue
            if cur is not None:
                groups.append(cur)
                cur = None
        close()
        if cur is not None:
            groups.append(cur)
        if len(groups) != len(rows):
            raise live.Unjustified(f"Tabel 3 of {DCE}: {len(groups)} variable lists "
                                   f"for {len(rows)} models in one half")
        models += rows
        lists += [set(re.findall(var, g)) for g in groups]
    if not models or any(not 0 <= r2 <= 1 for _, r2, _ in models):
        raise live.Unjustified(f"Tabel 3 of {DCE}: an R2 outside 0-1, or no models")
    other = read_json(os.path.join(DERIVED, "observing.json"))["dce_table3"]
    if other["models"] != len(models) or other["with_bv"] != sum("BV" in s for s in lists):
        raise live.Unjustified(f"Tabel 3 of {DCE}: this parse finds {len(models)} models, "
                               f"observing.py {other['models']}")

    def crit(rx):
        m = re.search(rx, t)
        if not m:
            raise live.Unjustified(f"{DCE}: criterion '{rx}' not found")
        return float(m.group(1).replace(",", "."))
    r2c = crit(r"kriteriet for dette statistiske mål er tentativt sat til mindst (\d+,\d+)")
    devc = crit(r"Kriteriet for dette statistiske mål er tentativt sat til højst (\d+) %")
    dev = [m[0] for m in models]
    r2 = [m[1] for m in models]
    return {"_what": "DCE's Tabel 3 (statistical-model report, 2015) tallied from its "
                     "pinned text by scripts/pages/grundlaget.py: one entry per fitted "
                     "indicator-model.",
            "source": DCE, "models": len(models),
            "mean_r2": statistics.mean(r2),
            "mean_dev_pct": statistics.mean(dev),
            "r2_criterion": r2c, "dev_criterion_pct": devc,
            "below_r2": sum(1 for x in r2 if x < r2c),
            "above_dev": sum(1 for x in dev if x > devc),
            "sys_dev": sum(1 for m in models if m[2] == "ja"),
            "failing_one": sum(1 for d_, r_, _ in models if r_ < r2c or d_ > devc),
            "r2_min": min(r2), "r2_max": max(r2), "dev_min": min(dev), "dev_max": max(dev),
            "with_bv": sum(1 for s in lists if "BV" in s),
            "with_temp": sum(1 for s in lists if "temp" in s)}


def main():
    try:
        write_json(TALLY, tabel3())
        T = live.live_json(TALLY)
        comp = {}
        for n in ("kattegat", "bornholm", "koege", "oresund"):
            vp3, ic = rv(f"gm_{n}_vp3"), rv(f"gm_{n}_ic")
            comp["strict_" + n] = f"{(ic - vp3) / ic * 100:.0f}"      # how much stricter VP3 is
        vp3, ic = rv("gm_aalborg_vp3"), rv("gm_aalborg_ic")
        comp["looser_aalborg"] = f"{(vp3 - ic) / ic * 100:.0f}"       # shown with a minus sign
        # the weight units of the banded (Kd) and judged (the two oxygen) indicators:
        # Kd's coefficient in DCE's formula, and the oxygen indicators' in their Tabel 5
        kd = rval(DCE, 2, "(2𝑋1 + 𝑋2 + 𝑋3 + 𝑋4 + 2𝑋5 )/7")
        one = rval(DCE, 1, "Vægt 2 1 sæsonfordeling (iltsvindseffekt) grænsning 1 1 2")
        comp["banded_judged"] = f"{kd + one + one}"

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
            if k == "T":
                return format(T[a[0]], a[1])
            if k == "N":
                return claims.resolve(CL, "{count:%s:%s}" % (a[0], a[1]), _cache)[0]
            if k == "P":
                return pages(a[0])
            if k == "C":
                return live.chem(a[0])
            if k == "B":
                return live.claim_begin(a[0])
            if k == "E":
                return live.CLAIM_END
            raise ValueError(f"unknown marker {m.group(0)}")

        text = MARK.sub(render, TEXT)
        write_doc(OUT, text)
    except (live.Unjustified, claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote {PAGE} ({len(text):,} chars)")
    return 0


TEXT = r'''# Grundlaget: what the Danish nitrogen requirement actually rests on

⟦B¦C-GC-G-READ⟧Read from the primary method documents, not from summaries of them. Every figure on this page is read from, or computed on, a pinned copy of the document it comes from, and the notes the page was first written from, with verbatim sources and per-claim verification flags, are in `data/manual/science_chain.json`.⟦E⟧ ⟦B¦C-GC-G-GEN⟧Generated by `scripts/pages/grundlaget.py`, which refuses to write the page if a reading is not in its pinned document.⟦E⟧

---

⟦B¦C-GC-G-PURPOSE⟧This page reconstructs the case *for* the Danish nitrogen requirement, as carefully as its authors made it, at the level of what is measured and what is computed — never at the level of who signed off on it. The outcome it guards against is a critique of a strawman.⟦E⟧

⟦B¦C-GC-G-ENDORSE⟧That rule cuts both ways and it has to. An international expert panel endorsing something is not evidence about the something. Neither is a ministry-chaired taskforce criticising it.⟦E⟧

⟦B¦C-GC-G-AUDIT-LEAD⟧Section 3 holds this project's own arguments up against these documents. Some do not survive as they were first stated, and the narrower versions that do are stronger, which is the ordinary result of actually reading the source.⟦E⟧

---

## 1. The data level: what is physically measured

⟦B¦C-GC-G-NOVANA⟧The measurements come from NOVANA, the national monitoring programme: DCE's modelled indicators are NOVANA data, and DHI used NOVANA data to calibrate and validate its models. The current programme, ⟦R¦NOVANA-2327¦2023–27¦NOVANA 2023-27⟧, is the one to read, and the numbers in it are specific.⟦E⟧

### Water chemistry, chlorophyll and hydrography

⟦B¦C-GC-G-CHEM⟧The water-chemistry and hydrography stations, as the programme sets them out:⟦E⟧

| | |
|---|---|
| Stations | **⟦R¦NOVANA-2327¦114¦Målingerne udføres i alt på 114 stationer fordelt på 29 kontrolovervågede stationer hvert år og 85 operationelt overvågede stationer cirka hvert andet år i fjorde og kystvande⟧** |
| Sampled every year | ⟦R¦NOVANA-2327¦29¦Målingerne udføres i alt på 114 stationer fordelt på 29 kontrolovervågede stationer hvert år og 85 operationelt overvågede stationer cirka hvert andet år i fjorde og kystvande⟧ (control) |
| Sampled roughly every second year | ⟦R¦NOVANA-2327¦85¦Målingerne udføres i alt på 114 stationer fordelt på 29 kontrolovervågede stationer hvert år og 85 operationelt overvågede stationer cirka hvert andet år i fjorde og kystvande⟧ (operational) |
| Sampled in any given year | **⟦R¦NOVANA-2327¦64–79¦Årligt udføres målingerne således på 64-79 stationer i fjorde og kystvande⟧** |
| Frequency when sampled | **twice a month** |
| Water bodies to cover | **⟦R¦NOVANA-2327¦109¦Der er udpeget 109 vandområder inden for 1-sømilsgrænsen⟧** |
| Additional open-water stations | ⟦R¦NOVANA-2327¦18¦Derudover udføres profilmålinger på 18 stationer uden for 1-sømilegrænsen⟧, six times a year |

> ⟦B¦C-GC-G-CHEM-Q⟧*"⟦Q¦NOVANA-2327¦Målingerne udføres i alt på 114 stationer fordelt på 29 kontrolovervågede stationer hvert år og 85 operationelt overvågede stationer cirka hvert andet år i fjorde og kystvande.⟧"*⟦E⟧

⟦B¦C-GC-G-CHLMEAN⟧The chlorophyll indicator is a **May–September mean**. In a water body on the operational programme, that mean is built from samples taken about twice a month, in the years the water body is monitored — about every second year.⟦E⟧

### Oxygen

⟦B¦C-GC-G-ILT⟧The iltsvind programme adds **⟦R¦NOVANA-2327¦92–107¦årligt med op mod yderligere 92-107 stationer⟧ more stations a year**, twice a month July–November (June–October in Limfjorden, where hypoxia starts earlier), monthly July–October in the open inner waters. Hydrogen sulphide is measured only *"når der er begrundet mistanke om forekomst heraf"*.⟦E⟧

⟦B¦C-GC-G-WINDOW⟧That window is set by mechanism — the stratified season is when stratification-driven hypoxia happens — so seasonal claims drawn from it are not circular. It does mean bottom-water oxygen from December to May is seen only through the routine stations.⟦E⟧

### Sediment nutrient pools

⟦B¦C-GC-G-SED⟧Once, in **⟦R¦NOVANA-2327¦90¦prøver fra 90 af de 109 vandområder; årligt overvåges 16-19 stationer⟧ of ⟦R¦NOVANA-2327¦109¦prøver fra 90 af de 109 vandområder; årligt overvåges 16-19 stationer⟧** water bodies over five years, ⟦R¦NOVANA-2327¦16–19¦prøver fra 90 af de 109 vandområder; årligt overvåges 16-19 stationer⟧ stations a year, in **January–February**:⟦E⟧

> ⟦B¦C-GC-G-SED-Q⟧*"Prøverne indsamles én gang på det tidspunkt af året, hvor sedimentet er mest oxideret (januar-februar)."*⟦E⟧

⟦B¦C-GC-G-POOL⟧The internal-loading pool is measured at its annual redox maximum, by design. That is the right choice for a comparable long-term pool measurement. It is also the state least like the warm, anoxic, releasing summer condition that the models say drives internal loading. The pool is measured; the flux is modelled.⟦E⟧

### Biology

⟦B¦C-GC-G-BIO⟧The biological programme, as it is set out:⟦E⟧

| What | Window | Stations / transects | Coverage |
|---|---|---|---|
| Eelgrass and flowering plants | once, **1 Jun – 30 Sep** | ⟦R¦NOVANA-2327¦502¦Undersøgelserne udføres på i alt 502 transekter, heraf 139 kontroltransekter hvert år⟧ transects; ⟦R¦NOVANA-2327¦139¦Undersøgelserne udføres på i alt 502 transekter, heraf 139 kontroltransekter hvert år⟧ annual | ⟦R¦NOVANA-2327¦103¦overvågning af ålegræs og andre blomsterplanter i 103 af de 109 vandområder⟧ of ⟦R¦NOVANA-2327¦109¦overvågning af ålegræs og andre blomsterplanter i 103 af de 109 vandområder⟧ water bodies |
| Macroalgae | once, **1 Jun – 31 Aug** | ⟦R¦NOVANA-2327¦120¦Undersøgelserne udføres på i alt 120 transekter, heraf 38 kontroltransekter hvert år⟧ transects; ⟦R¦NOVANA-2327¦38¦Undersøgelserne udføres på i alt 120 transekter, heraf 38 kontroltransekter hvert år⟧ annual | **⟦R¦NOVANA-2327¦38¦mens der overvåges for makroalger i 38 af de 109 vandområder⟧ of ⟦R¦NOVANA-2327¦109¦mens der overvåges for makroalger i 38 af de 109 vandområder⟧** |
| Soft-bottom fauna | **1 Mar – 31 May** | ⟦R¦NOVANA-2327¦110¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ stations; ⟦R¦NOVANA-2327¦15¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ annual, ⟦R¦NOVANA-2327¦95¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ every third year | ⟦R¦NOVANA-2327¦109¦overvågning af bundfauna i alle 109 vandområder inden for 1-sømilsgrænsen⟧, over five years |

> ⟦B¦C-GC-G-FAUNA-Q⟧*"Overvågningen af blødbundsfaunaen gennemføres i tidsrummet 1. marts-31. maj."*⟦E⟧

⟦B¦C-GC-G-SPRING⟧**The benthic community is counted in spring.** An autumn kill is seen the following March at the earliest, after recolonisation has begun, and at the operational stations — ⟦R¦NOVANA-2327¦95¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ of ⟦R¦NOVANA-2327¦110¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ — only every third year. In any given year **⟦R¦NOVANA-2327¦45–49¦I det enkelte år overvåges 45-49 stationer⟧** of those stations are visited.⟦E⟧

### And one thing that has to be said about the programme's own history

> ⟦B¦C-GC-G-HIST-Q⟧*"⟦Q¦NOVANA-2327¦Dette er en opjustering i forhold til NOVANA 2017-21, hvor der ikke forekom overvågning af fytoplankton (her klorofyl) og bundfaunakvalitetselementet i alle vandområder.⟧"*⟦E⟧

⟦B¦C-GC-G-PREDATES⟧The VP3 requirement predates that improvement: the second opinion gives VP3's status loads as the 2016–2018 mean, and its model slopes as fitted on load data up to 2016. The improvement is real and it postdates the numbers in force.⟦E⟧

### What is not monitored at all

⟦B¦C-GC-G-FEDTE⟧Fedtemøg as a shore condition: no extent, no biomass, no duration, no programme. Marine litter, microplastic and beach litter are monitored. Stranded decaying organic material is not.⟦E⟧

---

## 2. The model level: three instruments, and what each one can do

⟦B¦C-GC-G-THREE⟧The VP2 requirement for the ⟦R¦DHI-MODEL-DEL1-2015¦119¦de 119 danske marine vandområder⟧ marine water bodies was assembled from three different things, and from a neighbour's requirement where none of them reaches.⟦E⟧

| Instrument | Built by | Covers (VP2) | What it is |
|---|---|---:|---|
| Statistical models | DCE / Aarhus | **⟦R¦DCE-STATMOD-2015¦22¦Der er blevet udviklet statistiske modeller for 29 kystnære overvågningsstationer, som repræsenterer 22 vandområder⟧** water bodies, ⟦R¦DCE-STATMOD-2015¦29¦Der er blevet udviklet statistiske modeller for 29 kystnære overvågningsstationer, som repræsenterer 22 vandområder⟧ stations | Regressions on 1990–2012 station time series |
| Mechanistic models | DHI | **⟦R¦DHI-MODEL-DEL1-2015¦45¦I alt beskriver de mekanistiske modeller 45 vandområder⟧** water bodies | 3D hydrodynamic-ecological simulation, 2002–2011 |
| Meta-analysis | both | ⟦R¦DHI-MODEL-DEL1-2015¦29¦Derudover er der brugt en meta-analyse tilgang for i alt 29 vandområder⟧ water bodies | Slopes borrowed from typologically similar water bodies |

⟦B¦C-GC-G-RULE5⟧Where there is neither data nor a model, rule ⟦R¦DHI-MODEL-DEL1-2015¦5¦5. I områder, hvor der hverken er data eller modeller, benyttes indsatsbehov for tilstødende vandområde⟧ applies:⟦E⟧

> ⟦B¦C-GC-G-RULE5-Q⟧*"I områder, hvor der hverken er data eller modeller, benyttes indsatsbehov for tilstødende vandområde."*⟦E⟧

⟦B¦C-GC-G-KBH⟧Which is how **København Havn** gets its requirement, with the comment *"Øresund anvendt til at bestemme indsats til KBH"*.⟦E⟧

### The statistical models

⟦B¦C-GC-G-STATBASE⟧⟦R¦DCE-STATMOD-2015¦29¦Der er blevet udviklet statistiske modeller for 29 kystnære overvågningsstationer, som repræsenterer 22 vandområder⟧ stations, ⟦R¦DCE-STATMOD-2015¦22¦Der er blevet udviklet statistiske modeller for 29 kystnære overvågningsstationer, som repræsenterer 22 vandområder⟧ water bodies, requiring >⟦R¦DCE-STATMOD-2015¦15¦lange tidsserier (> 15 år)⟧-year series, on data from 1990–2012.⟦E⟧

> ⟦B¦C-GC-G-ONESTATION-Q⟧*"For de fleste vandområder er der kun en enkelt moniteringsstation med tilstrækkelig datadækning til statistisk modellering, og derfor betragtes denne station som repræsentativ for vandområdet."*⟦E⟧

⟦B¦C-GC-G-METHOD⟧The method: iterative cross-validated multiple linear regression, selecting on lowest RMSECV; then PLS on the selected variables; ⟦R¦DCE-STATMOD-2015¦3/4–1/4¦(3/4 af det totale datasæt) og et valideringssæt (1/4 af det totale datasæt)⟧ calibration/validation split for *selection*, with the final parametrisation fitted on the whole dataset. Candidate variables are N load, P load, freshwater, wind energy, irradiance, salinity, **water column stability (BV)** and **surface temperature**, each in ⟦R¦DCE-STATMOD-2015¦4¦Periode 4⟧-, ⟦R¦DCE-STATMOD-2015¦8¦8 eller 12 mdr.⟧- or ⟦R¦DCE-STATMOD-2015¦12¦Periode 4, 8 eller 12 mdr.⟧-month windows stepped back monthly — up to ⟦R¦DCE-STATMOD-2015¦43¦op til 43 månedsintervaller⟧ period combinations per variable, all tested.⟦E⟧

⟦B¦C-GC-G-CRIT⟧Their own acceptance criteria: deviation ≤ ⟦R¦DCE-STATMOD-2015¦30¦Kriteriet for dette statistiske mål er tentativt sat til højst 30 %⟧%, R² ≥ ⟦R¦DCE-STATMOD-2015¦0.4¦kriteriet for dette statistiske mål er tentativt sat til mindst 0,4⟧, ≥ ⟦R¦DCE-STATMOD-2015¦15¦minimumsgrænsen tentativt sat til 15 datapunkter⟧ data points.⟦E⟧

⟦B¦C-GC-G-TALLY⟧We re-extracted their Tabel 3 from the PDF and tallied it. Our totals reproduce their own summary — mean R² ⟦T¦mean_r2¦.3f⟧ against their stated ⟦R¦DCE-STATMOD-2015¦0.56¦har et gennemsnit på 0,56⟧, mean deviation ⟦T¦mean_dev_pct¦.1f⟧% against their ~⟦R¦DCE-STATMOD-2015¦13¦gennemsnitlig absolut afvigelse på ca. 13 %⟧% — which is the check that the extraction is sound.⟦E⟧

| | |
|---|---:|
| Fitted indicator-models | **⟦T¦models¦d⟧** |
| Mean R² | ⟦T¦mean_r2¦.3f⟧ |
| Mean absolute deviation | ⟦T¦mean_dev_pct¦.1f⟧% |
| **Below their own R² ≥ ⟦R¦DCE-STATMOD-2015¦0.4¦kriteriet for dette statistiske mål er tentativt sat til mindst 0,4⟧ criterion** | **⟦T¦below_r2¦d⟧** |
| Above their own ⟦R¦DCE-STATMOD-2015¦30¦Kriteriet for dette statistiske mål er tentativt sat til højst 30 %⟧% deviation criterion | ⟦T¦above_dev¦d⟧ |
| **Flagged with systematic deviations** | **⟦T¦sys_dev¦d⟧** |
| Failing at least one numeric criterion | ⟦T¦failing_one¦d⟧ |

⟦B¦C-GC-G-RANGE⟧The spread is wide: R² runs from ⟦T¦r2_min¦.2f⟧ to ⟦T¦r2_max¦.2f⟧ across the models, and the deviation from ⟦T¦dev_min¦.1f⟧% to ⟦T¦dev_max¦.1f⟧%.⟦E⟧ ⟦B¦C-GC-G-COLOURS⟧DCE mark each model green, meaning a good reproduction of the data and trust that the model describes the system correctly, or yellow, meaning *"man skal være varsom ved anvendelse af modellen"*.⟦E⟧

⟦B¦C-GC-G-SCREENING⟧That is a defensible way to run a screening exercise. It is a different thing to use as the basis for a per-catchment quota, and the difference is entirely in what the number is subsequently asked to do.⟦E⟧

⟦B¦C-GC-G-SPRINGP-LEAD⟧**And then there is this sentence**, whose supporting results are not shown:⟦E⟧

> ⟦B¦C-GC-G-SPRINGP-Q⟧*"Det er dog som hovedregel fosfortilførslen, der styrer klorofylkoncentrationen i forårsperioden (resultater ikke vist), men da denne periode ikke er inkluderet i den interkalibrerede klorofylindikator, er det kvælstoftilførslen, der oftest udvælges som forklaringsvariabel for klorofylkoncentrationen."*⟦E⟧

⟦B¦C-GC-G-SPRINGP⟧Phosphorus governs spring chlorophyll. The intercalibrated chlorophyll indicator is May–September, which excludes spring. Nitrogen is therefore what gets selected. **The choice of indicator window is doing causal work**, the authors say so plainly, and the supporting results are not shown.⟦E⟧

Their own stated limitation:

> ⟦B¦C-GC-G-LIMIT-Q⟧*"Da modellerne er opstillet, kalibreret og valideret i en periode med relativt høje næringsstoftilførsler er beregningen af indsatsbehovet afhængig af, at de fundne relationer ... ikke ændres over tid f.eks. som følge af regimeskift, klimaændringer mm. Det er imidlertid ikke muligt at forudsige om og evt. hvornår der vil indtræffe f.eks. regimeskift bl.a. fordi det empiriske grundlag for oliogotrofieringsprocessen er mangelfuldt."*⟦E⟧

### The mechanistic models

⟦B¦C-GC-G-DHI-YES⟧**Do the DHI models contain stratification, temperature and seasonality as mechanism, rather than as candidate variables? Yes. All three, and more.**⟦E⟧

⟦B¦C-GC-G-FIVE⟧Five models: one regional (inner Danish waters including the whole Baltic to Skagerrak), three local (Limfjorden, Odense Fjord, Roskilde Fjord), one North Sea hydrodynamic model. Four carry ecosystem modules.⟦E⟧

⟦B¦C-GC-G-SPEC⟧Their ecosystem models, as DHI describe them:⟦E⟧

| | |
|---|---|
| Dimensions | **⟦R¦DHI-MODEL-DEL2-2015¦3¦beskriver forholdene i 3 dimensioner⟧** |
| State variables | **more than ⟦R¦DHI-MODEL-DEL2-2015¦50¦mere end 50 primære tilstandsvariable, hvor ca. halvdelen er tilknyttet bunden⟧** primary, about half benthic |
| Period | 2002–2011; the first ⟦R¦DHI-MODEL-DEL2-2015¦5¦De første 5 år anses derfor for at være⟧ years spin-up; 2007–2011 used |

⟦B¦C-GC-G-STRAT⟧**Stratification** is not a parameter but the emergent result of solving temperature and salinity in three dimensions, and it is validated as such — BIAS ≤ ⟦R¦DHI-MODEL-DEL2-2015¦1¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧ psu / ⟦R¦DHI-MODEL-DEL2-2015¦1¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧ °C and RMSE ≤ ⟦R¦DHI-MODEL-DEL2-2015¦2¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧ psu / ⟦R¦DHI-MODEL-DEL2-2015¦2¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧ °C for at least ⟦R¦DHI-MODEL-DEL2-2015¦80¦BIAS ≤ 1psu/1°C og RMSE ≤ 2psu/2°C for mindst 80% af alle overflade- og bundmålinger i de åbne farvande⟧% of surface *and bottom* measurements in open waters.⟦E⟧

⟦B¦C-GC-G-TEMP⟧**Temperature:** *"Produktionen af fytoplankton (primærproduktionen) er bestemt af vandtemperaturen og tilgængeligheden af næringsstoffer og lys."*⟦E⟧

⟦B¦C-GC-G-SEASON⟧**Seasonality:** *"kan modellerne simulere dag-til-dag, måned-til-måned og år-til-år variationer"*, with a chlorophyll:carbon ratio that varies over the year, and sediment N and P pools that accumulate in autumn and winter and release over summer.⟦E⟧

**And oxygen:**

> ⟦B¦C-GC-G-OX-Q⟧*"De mekanistiske modeller beskriver iltkoncentrationerne i alle vanddybder gennem hele året, og inkluderer effekter af iltsvind på både ålegræs og filtrerende bunddyr."*⟦E⟧

⟦B¦C-GC-G-REDOX⟧With redox chemistry underneath it: phosphate bound to ⟦C¦Fe3+⟧ under oxic conditions and released when the iron reduces; nitrate denitrified at low oxygen; ammonium efflux rising during hypoxia. And an eelgrass feedback: eelgrass biomass suppresses resuspension, which reduces light attenuation, which favours eelgrass.⟦E⟧

⟦B¦C-GC-G-VALID⟧The validation numbers for the inner Danish waters model, against **⟦R¦DHI-MODEL-DEL2-2015¦12¦Der er anvendt i alt 12 NOVANA målestationer til validering af vandkvaliteten, ligeligt fordelt⟧** NOVANA stations:⟦E⟧

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

⟦B¦C-GC-G-OXBEST⟧⟦R¦DHI-MODEL-DEL2-2015¦12¦Der er anvendt i alt 12 NOVANA målestationer til validering af vandkvaliteten, ligeligt fordelt⟧ stations for a model spanning Kattegat, the Belts and the western Baltic is thin. But **bottom-water oxygen, at R² ⟦R¦DHI-MODEL-DEL2-2015¦0.83¦Iltkoncentrationerne i bundvandet er beskrevet med en BIAS-afvigelse på <0,5 mg/l og med en høj forklaringsgrad (R2=0.83)⟧, has the highest R² in DHI's validation of that model.**⟦E⟧

### How the slope is obtained — and what it is a slope of

⟦B¦C-GC-G-RUNS⟧⟦R¦DHI-MODEL-DEL2-2015¦8¦Resultaterne fra de 8 modelkørsler er anvendt i screeningsværktøjet⟧ runs per model: present-day, ⟦R¦DHI-MODEL-DEL2-2015¦6¦6 modelkørsler pr. model med prædefinerede reduktioner i N- og P-tilførsel⟧ reduction runs, and a reference run. The reduction levels are Danish nitrogen at **−⟦R¦DHI-MODEL-DEL2-2015¦15¦Nutid minus 15% Nutid minus 30% Nutid minus 60%⟧%, −⟦R¦DHI-MODEL-DEL2-2015¦30¦Nutid minus 15% Nutid minus 30% Nutid minus 60%⟧%, −⟦R¦DHI-MODEL-DEL2-2015¦60¦Nutid minus 15% Nutid minus 30% Nutid minus 60%⟧%**, crossed with phosphorus at present or −⟦R¦DHI-MODEL-DEL2-2015¦10–20¦reduktionerne varierer derfor i intervallet 10-20%⟧%.⟦E⟧

> ⟦B¦C-GC-G-EQUAL-Q⟧*"i en given modelkørsel reduceres alle danske kvælstoftilførsler med samme procenttal"*⟦E⟧

⟦B¦C-GC-G-LINE⟧The dose-response curve is then a **straight line through three simulated points**:⟦E⟧

> ⟦B¦C-GC-G-LINE-Q⟧*"⟦Q¦DHI-MODEL-DEL2-2015¦De 5 trendlinjer er baseret på resultaterne fra de 3 modelkørsler, hvor N er reduceret 15%, 30% eller 60% ift. nutid (2007-2011)⟧ ..."* *"Relationens trendlinje er vist som en ret linje. Reelt er den svagt buet (konkav), men inden for det spektrum, som er dækket af modelkørslerne, er forskellen fra en retlinjet funktion ikke signifikant."*⟦E⟧

And in every run:

> ⟦B¦C-GC-G-FROZEN-Q⟧*"Alle andre ydre forhold er fastholdt uændrede."* *"alt andet end næringstilførslerne er holdt konstant"*⟦E⟧

⟦B¦C-GC-G-FROZEN⟧Meteorology, climate, boundary hydrography, every other pressure: frozen at 2002–2011. Non-Danish Baltic loads reduced per HELCOM BSAP, assumed fulfilled by 2021 by decision of Naturstyrelsen. Atmospheric deposition reduced per the Gothenburg Protocol.⟦E⟧

⟦B¦C-GC-G-PONLY⟧Phosphorus turned out not to matter for the two indicators, so the final figures use nitrogen-only runs.⟦E⟧

⟦B¦C-GC-G-PARTIAL⟧**This is the right design for the question they were asked** — what does reducing Danish nitrogen do — and it is stated openly. It is the wrong instrument for the question the number is used to answer in public, which is *what caused the observed state*. A slope obtained by varying one input while freezing everything else is a partial derivative. It cannot attribute an observed change, because nothing else was allowed to vary.⟦E⟧

### Only two indicators come out

> ⟦B¦C-GC-G-TWO-Q⟧*"Samlede indsatsbehov beregnes som gennemsnit af indsatsbehov for de to indikatorer"*⟦E⟧

⟦B¦C-GC-G-TWO⟧Summer chlorophyll and summer Kd. Nothing else. Why:⟦E⟧

> ⟦B¦C-GC-G-SCOPE-Q⟧*"den nuværende modeludvikling fokuserer udelukkende på de EU interkalibrerede kvalitetselementer fytoplankton og bundvegetation"*⟦E⟧

⟦B¦C-GC-G-GATE⟧The model computes oxygen at all depths year-round, validated at R² ⟦R¦DHI-MODEL-DEL2-2015¦0.83¦Iltkoncentrationerne i bundvandet er beskrevet med en BIAS-afvigelse på <0,5 mg/l og med en høj forklaringsgrad (R2=0.83)⟧, and none of it reaches the requirement. **The gate is not the physics and not the data. It is that only intercalibrated quality elements were in scope, and oxygen has no intercalibrated indicator.**⟦E⟧

### The Danish share — their number, for our bay

⟦B¦C-GC-G-SHARE⟧DHI computed, for each of the ⟦R¦DHI-MODEL-DEL2-2015¦45¦resultaterne for 45 vandområder accepteret⟧ water bodies, what fraction of each indicator can be explained by Danish land-based nitrogen.⟦E⟧

| Water body | Chlorophyll | Kd |
|---|---:|---:|
| Hjarbæk Fjord | ⟦R¦DHI-MODEL-DEL2-2015¦93.9¦Hjarbæk Fjord 158 93,9 21,3⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦21.3¦Hjarbæk Fjord 158 93,9 21,3⟧% |
| Roskilde Fjord, indre | ⟦R¦DHI-MODEL-DEL2-2015¦85.3¦Roskilde Fjord, indre 2 85,3 100a⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦100¦Roskilde Fjord, indre 2 85,3 100a⟧% |
| Skive Fjord, Lovns Bredning | ⟦R¦DHI-MODEL-DEL2-2015¦83.2¦Skive Fjord, Lovns Bredning 157 83,2 33,6⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦33.6¦Skive Fjord, Lovns Bredning 157 83,2 33,6⟧% |
| Odense Fjord, ydre | ⟦R¦DHI-MODEL-DEL2-2015¦65.2¦Odense Fjord, ydre 92 65,2 57,5⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦57.5¦Odense Fjord, ydre 92 65,2 57,5⟧% |
| Langerak | ⟦R¦DHI-MODEL-DEL2-2015¦62.1¦Langeraka 156 62,1 20,5⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦20.5¦Langeraka 156 62,1 20,5⟧% |
| Kattegat, Nordsjælland | ⟦R¦DHI-MODEL-DEL2-2015¦5.2¦Kattegat, Nordsjælland 200 5,2 3,1⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦3.1¦Kattegat, Nordsjælland 200 5,2 3,1⟧% |
| **Køge Bugt** | **⟦R¦DHI-MODEL-DEL2-2015¦2.8¦Køge Bugt 201 2,8 2,7⟧%** | **⟦R¦DHI-MODEL-DEL2-2015¦2.7¦Køge Bugt 201 2,8 2,7⟧%** |
| Nordlige Øresund | under ⟦R¦DHI-MODEL-DEL2-2015¦5¦vandområde 6 (Nordlige Øresund) er påvirkningen mindre end 5%⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦1.5¦Nordlige Øresund 6 2;6 1,5⟧% |
| Femerbælt | ⟦R¦DHI-MODEL-DEL2-2015¦1.9¦Femerbælt 208 1,9 3,2⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦3.2¦Femerbælt 208 1,9 3,2⟧% |
| Fakse Bugt | ⟦R¦DHI-MODEL-DEL2-2015¦1.0¦Fakse Bugt 46 1,0 0,7⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦0.7¦Fakse Bugt 46 1,0 0,7⟧% |
| Østersøen, Bornholm | ⟦R¦DHI-MODEL-DEL2-2015¦0.2¦Østersøen, Bornholm 56 0,2 0,3⟧% | ⟦R¦DHI-MODEL-DEL2-2015¦0.3¦Østersøen, Bornholm 56 0,2 0,3⟧% |

> ⟦B¦C-GC-G-SHARE-Q⟧*"⟦Q¦DHI-MODEL-DEL2-2015¦Effekten af kvælstofreduktioner på indikatorerne varierer fra mindre end 5% til mere end 90%.⟧"*⟦E⟧

⟦B¦C-GC-G-GRADIENT⟧**The gradient is theirs, not ours**, and DHI state it plainly: in water bodies such as Østersøen, Bornholm and Nordlige Øresund the influence of Danish nitrogen on the chlorophyll indicator is under ⟦R¦DHI-MODEL-DEL2-2015¦5¦I vandområder som vandområde 56 (Østersøen, Bornholm) eller vandområde 6 (Nordlige Øresund) er påvirkningen mindre end 5%⟧%, while in the more closed areas such as the three Limfjorden water bodies it is between ⟦R¦DHI-MODEL-DEL2-2015¦60¦mens den i de mere lukkede områder som de tre vandområder i Limfjorden er mellem 60-90%⟧ and ⟦R¦DHI-MODEL-DEL2-2015¦90¦mens den i de mere lukkede områder som de tre vandområder i Limfjorden er mellem 60-90%⟧%.⟦E⟧

⟦B¦C-GC-G-KOEGE⟧Køge Bugt at ⟦R¦DHI-MODEL-DEL2-2015¦2.8¦Køge Bugt 201 2,8 2,7⟧%. Copenhagen Harbour, with no model, takes Øresund's requirement by rule ⟦R¦DHI-MODEL-DEL1-2015¦5¦5. I områder, hvor der hverken er data eller modeller, benyttes indsatsbehov for tilstødende vandområde⟧.⟦E⟧

### The uncertainty, and what it excludes

⟦B¦C-GC-G-ENSEMBLE⟧DHI call ensemble modelling — comparing the two model types where both exist — the best method for estimating the uncertainty of model scenarios, where there is no documented "right" target load to compare with. It runs on **⟦R¦DHI-MODEL-DEL1-2015¦11¦For 11 områder findes der både statistiske og mekanistiske modeller⟧ of ⟦R¦DHI-MODEL-DEL1-2015¦119¦de 119 danske marine vandområder⟧** water bodies, where the two model types give these nitrogen reductions:⟦E⟧

| Water body | Mechanistic | Statistical |
|---|---:|---:|
| Hjelm Bugt | ⟦R¦DHI-MODEL-DEL1-2015¦0¦Hjelm Bugt 135 0 18⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦18¦Hjelm Bugt 135 0 18⟧% |
| Roskilde Fjord, indre | ⟦R¦DHI-MODEL-DEL1-2015¦4¦Roskilde Fjord, indre 448 4 11⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦11¦Roskilde Fjord, indre 448 4 11⟧% |
| Århus Bugt, Kalø og Begtrup Vig | ⟦R¦DHI-MODEL-DEL1-2015¦7¦Århus Bugt, Kalø og Begtrup Vig 556 7 2⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦2¦Århus Bugt, Kalø og Begtrup Vig 556 7 2⟧% |
| Odense Fjord, ydre | ⟦R¦DHI-MODEL-DEL1-2015¦23¦Odense Fjord, ydre 132 23 26⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦26¦Odense Fjord, ydre 132 23 26⟧% |
| Storebælt, NV | ⟦R¦DHI-MODEL-DEL1-2015¦34¦Storebælt, NV 163 34 44⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦44¦Storebælt, NV 163 34 44⟧% |
| Lillebælt, syd | ⟦R¦DHI-MODEL-DEL1-2015¦36¦Lillebælt, syd 595 36 32⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦32¦Lillebælt, syd 595 36 32⟧% |
| Nissum, Thisted, Kås, Løgstør and Nibe Bredning and Langerak | ⟦R¦DHI-MODEL-DEL1-2015¦37¦Nissum Bredning, Thisted Bredning, 9020Kås Bredning, 37 Løgstør Bredning, 31⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦31¦Nissum Bredning, Thisted Bredning, 9020Kås Bredning, 37 Løgstør Bredning, 31⟧% |
| Åbenrå Fjord | ⟦R¦DHI-MODEL-DEL1-2015¦41¦Åbenrå Fjord 138 41 50⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦50¦Åbenrå Fjord 138 41 50⟧% |
| Bjørnholms Bugt, Riisgårde Bredning, Skive Fjord and Lovns Bredning | ⟦R¦DHI-MODEL-DEL1-2015¦52¦Skive Fjord52og Lovns Bredning 60⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦60¦Skive Fjord52og Lovns Bredning 60⟧% |
| Nordlige Lillebælt | ⟦R¦DHI-MODEL-DEL1-2015¦56¦834 56 58 367 350 359 224 Nordlige Lillebælt⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦58¦834 56 58 367 350 359 224 Nordlige Lillebælt⟧% |
| Det Sydfynske Øhav | ⟦R¦DHI-MODEL-DEL1-2015¦30¦Det Sydfynske Øhav 346 30 40⟧% | ⟦R¦DHI-MODEL-DEL1-2015¦40¦Det Sydfynske Øhav 346 30 40⟧% |

⟦B¦C-GC-G-REPORTED⟧Reported: ⟦R¦DHI-MODEL-DEL1-2015¦6–28¦for det enkelte vandområde er mellem 6% og 28%⟧% per water body, mean ⟦R¦DHI-MODEL-DEL1-2015¦16¦Den gennemsnitlige usikkerhed på målbelastningen for det enkelte vandområde er 16%⟧%; nationally ±⟦R¦DHI-MODEL-DEL1-2015¦9¦Og usikkerheden i % er derfor: 9%⟧% on the indsatsbehov. Three things about that figure, all of them stated by the authors:⟦E⟧

> ⟦B¦C-GC-G-UNC-Q1⟧*"Da der ikke findes dokumentation for den ”rigtige” målbelastning, kan man ikke på traditionel vis bestemme, hvor sikkert modellerne estimerer målbelastningen."*⟦E⟧

> ⟦B¦C-GC-G-UNC-Q2⟧*"Den usikkerhed, som er beregnet her, forholder sig udelukkende til usikkerheden på effekt i forhold til en reduktion i kvælstof, og det vil sige den model-tekniske usikkerhed. **Usikkerhedsanalysen inkluderer ikke eventuelle usikkerheder på målinger, fastlæggelse af statusværdier og bestemmelse af miljømål.**"*⟦E⟧

> ⟦B¦C-GC-G-UNC-Q3⟧*"For illustrationens skyld kan man antage, at variansen estimeret for de ensemble modellerede områder kan overføres til de resterende områder ved skalering med målbelastningen."*⟦E⟧

⟦B¦C-GC-G-LOWER⟧The national ±⟦R¦DHI-MODEL-DEL1-2015¦9¦Og usikkerheden i % er derfor: 9%⟧% is an illustration, on ⟦R¦DHI-MODEL-DEL1-2015¦11¦For 11 områder findes der både statistiske og mekanistiske modeller⟧ of ⟦R¦DHI-MODEL-DEL1-2015¦119¦de 119 danske marine vandområder⟧ water bodies, covering the slope and not the status value or the target value. It is a lower bound presented without that word.⟦E⟧

### How the requirement is actually assembled

⟦B¦C-GC-G-FORMULA⟧DCE compute each indicator's requirement, in per cent of the present load, from its status, its target and the fitted slope:⟦E⟧

```
indsatsbehov = 100 · ((Status − Miljømål) / Status) · (1 / hældning)
```

⟦B¦C-GC-G-WEIGHTS⟧Five indicators, weighted, averaged:⟦E⟧

| Indicator | Weight | How its requirement is derived |
|---|---:|---|
| Chlorophyll | **⟦R¦DCE-STATMOD-2015¦2¦(2𝑋1 + 𝑋2 + 𝑋3 + 𝑋4 + 2𝑋5 )/7⟧** | continuous, from the fitted slope |
| Kd / eelgrass proxy | **⟦R¦DCE-STATMOD-2015¦2¦(2𝑋1 + 𝑋2 + 𝑋3 + 𝑋4 + 2𝑋5 )/7⟧** | distance computed, then **binned into ⟦V¦kd_bin_0¦pct⟧, ⟦V¦kd_bin_1¦pct⟧, ⟦V¦kd_bin_2¦pct⟧ or ⟦V¦kd_bin_3¦pct⟧%** |
| Iltsvind | ⟦R¦DCE-STATMOD-2015¦1¦Vægt 2 1 sæsonfordeling (iltsvindseffekt) grænsning 1 1 2⟧ | **binary trigger**, then a flat ⟦R¦DCE-STATMOD-2015¦25¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration⟧% cut in TN concentration |
| DIP + Chl-a seasonality | ⟦R¦DCE-STATMOD-2015¦1¦Vægt 2 1 sæsonfordeling (iltsvindseffekt) grænsning 1 1 2⟧ | same trigger, same flat ⟦R¦DCE-STATMOD-2015¦25¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration⟧% |
| N-limitation | ⟦R¦DCE-STATMOD-2015¦1¦Vægt 2 1 sæsonfordeling (iltsvindseffekt) grænsning 1 1 2⟧ | computed to reach a target number of N-limited days |

⟦B¦C-GC-G-AVERAGE-LEAD⟧Averaging rather than taking the maximum is a deliberate choice, and an honest one:⟦E⟧

> ⟦B¦C-GC-G-AVERAGE-Q⟧*"Hvis det skulle sikres, at alle indikatorer opnåede deres miljømål skulle det maksimale indsatsbehov anvendes i stedet for et gennemsnit ... Ved at anvende et gennemsnit ... hvilket minimerer risikoen for overimplementering."*⟦E⟧

⟦B¦C-GC-G-ALLFIVE⟧The consequence follows: **no water body is required to reach all five of its targets.**⟦E⟧

⟦B¦C-GC-G-TRIGGER⟧**Oxygen.** The trigger is severe hypoxia ≥⟦R¦DCE-STATMOD-2015¦10¦kraftigt iltsvind ≥ 10 % af tiden ELLER, hvis der er moderat iltsvind ≥ 50 % af tiden⟧% of the time OR moderate hypoxia ≥⟦R¦DCE-STATMOD-2015¦50¦kraftigt iltsvind ≥ 10 % af tiden ELLER, hvis der er moderat iltsvind ≥ 50 % af tiden⟧% of the time. If triggered:⟦E⟧

> ⟦B¦C-GC-G-TRIGGER-Q⟧*"⟦Q¦DCE-STATMOD-2015¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration ... det vurderes at en 25 % reduktion i TN-koncentrationen er minimumskrav for at ændre systemet.⟧"*⟦E⟧

⟦B¦C-GC-G-OXCUT⟧It is a ⟦R¦DCE-STATMOD-2015¦25¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration⟧% *concentration* cut, converted to a loading cut through the water body's own relation between nitrogen input and TN concentration, so water bodies that the trigger treats alike get different loading requirements. The variation comes from the TN model, not from the severity of the hypoxia. Two water bodies with identical hypoxia and different slopes get different requirements. **There is no dose-response between the oxygen condition and the required reduction, and DCE does not claim there is.** The indicator itself yields one value per ⟦R¦DCE-STATMOD-2015¦6¦Der bruges 6 års data til beregning af månedsfrekvenser⟧ years.⟦E⟧

⟦B¦C-GC-G-KD⟧**Kd.** Every Kd figure in their results tables is ⟦V¦kd_bin_0¦pct⟧, ⟦V¦kd_bin_1¦pct⟧, ⟦V¦kd_bin_2¦pct⟧ or ⟦V¦kd_bin_3¦pct⟧. That is not rounding — it is the equation. An indicator carrying ⟦R¦DCE-STATMOD-2015¦2¦(2𝑋1 + 𝑋2 + 𝑋3 + 𝑋4 + 2𝑋5 )/7⟧ of ⟦R¦DCE-STATMOD-2015¦7¦(2𝑋1 + 𝑋2 + 𝑋3 + 𝑋4 + 2𝑋5 )/7⟧ weight units contributes one of four fixed values. And:⟦E⟧

> ⟦B¦C-GC-G-KD-Q⟧*"Både brugen af Kd-indikatoren i stedet for ålegræssets dybdegrænse og kategoriseringen af indsatsbehov betyder, at der ikke nødvendigvis vil komme ålegræs til måldybden, selvom den danske kvælstoftilførsel reduceres i overensstemmelse med de beregnede reduktionskrav."*⟦E⟧

⟦B¦C-GC-G-PROXY⟧In some water bodies the target eelgrass depth exceeds the actual water depth, so the Kd target is computed from the water depth instead. In others the observed eelgrass shows better light than the Kd measurements, so Kd status is computed backwards from eelgrass. The proxy runs in both directions — Kd and eelgrass are not independent lines of evidence.⟦E⟧

⟦B¦C-GC-G-NLIM-LEAD⟧**N-limitation.** The most self-aware part of the method:⟦E⟧

> ⟦B¦C-GC-G-NLIM-Q⟧*"⟦Q¦DCE-STATMOD-2015¦Empiriske analyser har vist, at algevæksten i kystnære havområder skal være kvælstofbegrænset i minimum 150 dage, før der kan ses en signifikant sammenhæng mellem klorofylkoncentrationer og kvælstofkoncentrationer⟧."*⟦E⟧

⟦B¦C-GC-G-NLIM⟧Below ⟦R¦DCE-STATMOD-2015¦150¦skal være kvælstofbegrænset i minimum 150 dage⟧ N-limited days, their own central mechanism does not operate. Their response is not to exclude those water bodies but to add the reduction needed to *make* nitrogen limiting in the first place. That is a defensible engineering choice and also an admission that in those water bodies the requirement is not derived from a measured dose-response.⟦E⟧

### The targets

⟦B¦C-GC-G-EQR⟧The chlorophyll target is set from the reference concentration from ensemble modelling and the EU-intercalibrated EQR of ⟦R¦DCE-STATMOD-2015¦0.6¦Ecological Quality Ratio (EQR) værdi på 0,6⟧, the ratio between the reference value and the good/moderate boundary. In the April 2015 method document, the supporting reference for it is:⟦E⟧

> ⟦B¦C-GC-G-NOTE-Q⟧*"Notat om bestemmelse af grænseværdier for klorofyl (under udarbejdelse)"*⟦E⟧

⟦B¦C-GC-G-NOTE⟧A note still in preparation. That does not make the value wrong; it means the derivation was not publicly checkable when the method was published.⟦E⟧

⟦B¦C-GC-G-DISPUTE⟧And there is a live dispute about the values themselves, which is internal to the Danish process. The 2023 international panel found that the VP3 recalculation:⟦E⟧

> ⟦B¦C-GC-G-PANEL-Q⟧*"har ... ført til uoverensstemmelser mellem de afledte G/M-grænseværdier og de interkalibrerede G/M-grænseværdier, som ligger til grund for EU-Kommissionsbeslutning 2018/229"* *"Det anbefales især at ophæve nedjustering af G/M-grænseværdierne i de åbne danske kystvande."*⟦E⟧

⟦B¦C-GC-G-GM⟧The second opinion's background analyses give the chlorophyll good/moderate boundaries, in µg/l, as in VP3 and as refitted to the intercalibrated values:⟦E⟧

| Water body | VP3 G/M | Intercalibrated | VP3 stricter by |
|---|---:|---:|---:|
| Kattegat, Nordsjælland >⟦R¦SO-BG-2024¦20¦205: Kattegat, Nordsjælland >20 m OW1 T.21: KVuDLSa 0,9 1,58 1,58⟧ m | ⟦V¦gm_kattegat_vp3¦.1f⟧ µg/l | ⟦V¦gm_kattegat_ic¦.2f⟧ | ⟦X¦strict_kattegat⟧% |
| Østersøen, Bornholm | ⟦V¦gm_bornholm_vp3¦.1f⟧ | ⟦V¦gm_bornholm_ic¦.2f⟧ | ⟦X¦strict_bornholm⟧% |
| **Køge Bugt** | **⟦V¦gm_koege_vp3¦.1f⟧** | **⟦V¦gm_koege_ic¦.2f⟧** | **⟦X¦strict_koege⟧%** |
| Nordlige Øresund | ⟦V¦gm_oresund_vp3¦.1f⟧ | ⟦V¦gm_oresund_ic¦.2f⟧ | ⟦X¦strict_oresund⟧% |
| Kattegat, Aalborg Bugt | ⟦V¦gm_aalborg_vp3¦.1f⟧ | ⟦V¦gm_aalborg_ic¦.2f⟧ | −⟦X¦looser_aalborg⟧% |

⟦B¦C-GC-G-NOPOSITION⟧We take no position on which value is ecologically right — that is a dispute between qualified parties. We note only that the target sits in the numerator of the requirement equation, so this is not a marginal adjustment.⟦E⟧

⟦B¦C-GC-G-UNREACH-LEAD⟧And that, in some open coastal waters, the analysis finds signs that the targets cannot be met by Danish action alone:⟦E⟧

> ⟦B¦C-GC-G-UNREACH-Q⟧*"de danske klorofylmål i VP3 ikke vil være mulige at indfri uden yderligere indsatser fra andre lande eller supplerende indsatser målrettet atmosfærisk kvælstofdeposition, som vil ligge udover de reduktioner, som landene har forpligtet sig til"*⟦E⟧

---

## 3. Our critique, audited

⟦B¦C-GC-G-RUTHLESS⟧Be ruthless. Finding our own errors is a success.⟦E⟧

### False as first stated

⟦B¦C-GC-G-F1⟧**`F1`. "There is no coefficient anywhere between nitrogen and any outcome."** False: DCE's Tabel 3 lists ⟦T¦models¦d⟧ fitted indicator-models, and DHI's ecosystem model is validated against measurements, bottom-water oxygen among them.⟦E⟧

⟦B¦C-GC-G-F2⟧**`F2`. "Nitrogen → oxygen depletion: no coefficient, no ventilation term, no state variable. A kilogram in February counts the same as a kilogram in July under a pycnocline."** False for the mechanistic models, which are 3D, run on meteorology, resolve stratification, carry oxygen at all depths year-round, include oxygen consumption, redox-dependent phosphate release, denitrification and ammonium efflux — and validate bottom-water oxygen at **R² ⟦R¦DHI-MODEL-DEL2-2015¦0.83¦Iltkoncentrationerne i bundvandet er beskrevet med en BIAS-afvigelse på <0,5 mg/l og med en høj forklaringsgrad (R2=0.83)⟧**. Even the statistical models carry water-column stability and temperature as candidate variables, and select them: stability in ⟦T¦with_bv¦d⟧ of the ⟦T¦models¦d⟧ fitted models, water temperature in ⟦T¦with_temp¦d⟧.⟦E⟧

⟦B¦C-GC-G-F2-LEAD⟧**What survives is narrower, and it is stronger:**⟦E⟧

1. ⟦B¦C-GC-G-F2-1⟧In the **statistical route**, the oxygen requirement is a binary trigger plus a judged flat ⟦R¦DCE-STATMOD-2015¦25¦fastsættes et indsatsbehov på 25 % af den nuværende TN-koncentration⟧%, with no dose-response between hypoxia severity and required reduction. DCE writes *"det vurderes"*.⟦E⟧
2. ⟦B¦C-GC-G-F2-2⟧In the **mechanistic route**, oxygen is simulated and well validated and is *excluded from the indicator set* — only summer chlorophyll and summer Kd produce a requirement — because only intercalibrated quality elements were in scope.⟦E⟧
3. ⟦B¦C-GC-G-F2-3⟧In the **load accounting** that produces the ⟦V¦apportion_agriculture¦.1f⟧%, there is indeed no potency term of any kind.⟦E⟧

⟦B¦C-GC-G-F2-EXCLUDED⟧The model that could compute this does compute it. The answer is excluded by the indicator set, not by the physics.⟦E⟧

⟦B¦C-GC-G-F3⟧**`F3`. "Atmospheric deposition ... is absent from every published apportionment."** Too broad. Deposition is an explicit input to the mechanistic models, and the Gothenburg reductions are applied in every reduction run. What holds is narrower: it is not a line in the source apportionment that produces the ⟦V¦apportion_agriculture¦.1f⟧%, which apportions the discharge to coastal waters by source.⟦E⟧

⟦B¦C-GC-G-F4⟧**`F4`. "Sediment regeneration is not a source at all in the accounting frame."** False as a statement about the evidence base. DHI's sediment module carries C, N and P pools, mineralisation, iron-bound phosphate, denitrification and ammonium release, accumulating in autumn and winter and released over summer. What holds is narrower: sediment regeneration has no row in the *load accounting*, and what NOVANA measures is the pool, sampled once in the year when the sediment is most oxidised, January–February.⟦E⟧

### Needs qualifying

⟦B¦C-GC-G-Q1⟧**`Q1`. "Nobody has published the regression of iltsvind extent on load, wind work and bottom temperature."** A strong negative claim about the literature, not verified here. The second opinion's background analyses summarise Hansen & Rytter 2024 as saying that *"Iltsvindets udvikling i løbet af året reguleres væsentligst af bundvandstemperaturen og de aktuelle vejrmæssige forhold, men udbredt iltsvind forudsætter en forudgående stor tilførsel af næringsstoffer"* — a summary of exactly that analysis. The paper itself has not been read here, so what can be said is that we have not found the coefficients published.⟦E⟧

⟦B¦C-GC-G-Q2⟧**`Q2`. "Halve the load and the extremes do not move."** Three qualifications are missing. A comparison of chosen years cannot carry a trend in a series whose variance between years is large. The alternative to "no effect" is "worse without", which such a comparison cannot separate. And warmer water holds less oxygen, so a warming over the same period would work against the load reduction. Keep the observation and drop the word "test": the extremes are not obviously tracking the load, and a comparison of extremes cannot tell the two readings apart.⟦E⟧

⟦B¦C-GC-G-Q3⟧**`Q3`. "Most water bodies have one monitoring station."** True and now precise — but say *which parameter*. One station per water body is right for the hydrography and water chemistry that feed the statistical models. The eelgrass programme runs ⟦R¦NOVANA-2327¦502¦Undersøgelserne udføres på i alt 502 transekter, heraf 139 kontroltransekter hvert år⟧ transects and the iltsvind programme adds ⟦R¦NOVANA-2327¦92–107¦årligt med op mod yderligere 92-107 stationer⟧ stations a year.⟦E⟧

⟦B¦C-GC-G-Q4⟧**`Q4`. "The models cannot represent state-dependence or alternative stable states."** False for the mechanistic models, true for the statistical models and the accounting. DHI model eelgrass as a state with feedbacks onto light and resuspension, and model *why* eelgrass fails to return — sandworm burial of seeds, drifting macroalgae damaging shoots, resuspension — noting that in some areas the model *"forudsiger, at ålegræsvegetationen ikke genetableres i et omfang som registreret i tidligere tider. Skal der ske en genetablering i disse områder, skal nogle af de beskrevne stressfaktorer begrænses."*⟦E⟧

⟦B¦C-GC-G-Q4-OURS⟧That is our argument, in their document. The alternative-stable-states case is not a heterodox objection to Danish marine science: it is inside the Danish model, and it does not reach the policy instrument, which takes only summer chlorophyll and summer Kd.⟦E⟧

⟦B¦C-GC-G-Q5⟧**`Q5`. The residual-estimator claims about the ⟦V¦apportion_agriculture¦.1f⟧%** concern the load accounting, not the requirement chain, and are out of scope here; [NITROGEN.md](NITROGEN.md) takes them up.⟦E⟧

⟦B¦C-GC-G-Q6⟧**`Q6`. "Køge Bugt cannot qualify for iltsvind however bad it gets."** The mechanism is plausible, but "cannot, however bad it gets" is our inference, not DCE's. Their criterion is oxygen below ⟦R¦DCE-STATMOD-2015¦4¦koncentrationen af ilt i vandet er under 4 mg/L⟧ mg/l in the bottom water, and their notes record no iltsvind in Køge Bugt in their 2023 and 2025 periods; whether the bay can meet the criterion at all is unresolved.⟦E⟧

### Survives

- ⟦B¦C-GC-G-S-FAUNA⟧**Soft-bottom fauna is sampled 1 March – 31 May.** Confirmed verbatim, and strengthened: ⟦R¦NOVANA-2327¦45–49¦I det enkelte år overvåges 45-49 stationer⟧ of ⟦R¦NOVANA-2327¦110¦Undersøgelserne udføres på i alt 110 stationer, heraf 15 kontrolstationer hvert år og 95 operationelle stationer hvert tredje år⟧ stations in a given year.⟦E⟧
- ⟦B¦C-GC-G-S-JUDGED⟧**The oxygen requirement is a judged figure, not a measured dose-response.** *"det vurderes."* It holds with the mechanistic-route qualification attached.⟦E⟧
- ⟦B¦C-GC-G-S-KD⟧**Reaching the Kd target does not imply reaching the eelgrass target.** DCE says so.⟦E⟧
- ⟦B¦C-GC-G-S-FEDTE⟧**Fedtemøg has no national monitoring.** Confirmed by exhaustion of the NOVANA programme.⟦E⟧
- ⟦B¦C-GC-G-S-CURRENCY⟧**Nitrogen mass is the wrong currency for an oxygen problem.** Unaffected.⟦E⟧
- ⟦B¦C-GC-G-S-SHAPE⟧**Køge Bugt is the wrong shape for the national instrument.** Strengthened — by their number, not ours: Danish land-based nitrogen explains ⟦R¦DHI-MODEL-DEL2-2015¦2.8¦Køge Bugt 201 2,8 2,7⟧% of its chlorophyll indicator.⟦E⟧

---

## 4. Their conclusions and ours, side by side

- ⟦B¦C-GC-G-SB-COEF⟧**Is there a quantified nitrogen–outcome relationship?** Theirs: yes — ⟦T¦models¦d⟧ fitted models, four ecosystem models, an ⟦R¦DHI-MODEL-DEL1-2015¦11¦For 11 områder findes der både statistiske og mekanistiske modeller⟧-water-body ensemble. Ours, corrected: yes for summer chlorophyll and Kd; no for oxygen *as a policy quantity*; no for anything downstream of oxygen. Both are right, about different links: our error was saying "no coefficient" when we meant "not for the link the public argument turns on".⟦E⟧
- ⟦B¦C-GC-G-SB-STRAT⟧**Stratification, temperature, seasonality in the models?** Theirs: yes, in three dimensions. Ours: concede completely. **Them.**⟦E⟧
- ⟦B¦C-GC-G-SB-SLOPE⟧**Is the slope causal?** Theirs: it is the modelled response to changing Danish N, all else equal, presented as such. Ours: a partial derivative with everything else frozen — *"alt andet ... holdt konstant"* — the right instrument for "what would reducing do", the wrong one for "what caused this". **Us**, and their documents agree in their own words: a claim about *use*, not about the science.⟦E⟧
- ⟦B¦C-GC-G-SB-UNC⟧**Is the uncertainty adequate?** Theirs: ±⟦R¦DHI-MODEL-DEL1-2015¦9¦Og usikkerheden i % er derfor: 9%⟧% nationally, from a genuine two-method ensemble. Ours: method right, scope narrow, and they say so — ⟦R¦DHI-MODEL-DEL1-2015¦11¦For 11 områder findes der både statistiske og mekanistiske modeller⟧ of ⟦R¦DHI-MODEL-DEL1-2015¦119¦de 119 danske marine vandområder⟧ water bodies, slope only, measurement, status and target excluded, the national figure *"For illustrationens skyld"*. Us on scope, them on method; no dispute of fact.⟦E⟧
- ⟦B¦C-GC-G-SB-TARGET⟧**Are the chlorophyll targets right?** The model group: the VP3 values are the scientifically most correct. The taskforce, in line with the international panel: they diverge from the intercalibrated values and should be refitted. Ours: no position; the target is in the numerator. An internal Danish dispute, to be reported, not adjudicated.⟦E⟧
- ⟦B¦C-GC-G-SB-AVG⟧**Is averaging five indicators right?** Theirs: a deliberate choice to avoid over-implementation. Ours: honest and defensible; the consequence is that no water body must reach all five targets, and ⟦X¦banded_judged⟧ of ⟦R¦DCE-STATMOD-2015¦7¦(2𝑋1 + 𝑋2 + 𝑋3 + 𝑋4 + 2𝑋5 )/7⟧ weight units come from banded or judged values. No factual dispute.⟦E⟧
- ⟦B¦C-GC-G-SB-KOEGE⟧**Is Køge Bugt in the frame?** Theirs: Danish land nitrogen explains ⟦R¦DHI-MODEL-DEL2-2015¦2.8¦Køge Bugt 201 2,8 2,7⟧% of chlorophyll there. Ours: the same number. Agreement.⟦E⟧

---

## 5. Synthesis

### Common ground, stated honestly

- ⟦B¦C-GC-G-CG-CHL⟧Nitrogen loading does affect summer chlorophyll and water clarity: fitted in ⟦R¦DCE-STATMOD-2015¦22¦Der er blevet udviklet statistiske modeller for 29 kystnære overvågningsstationer, som repræsenterer 22 vandområder⟧ water bodies, simulated in ⟦R¦DHI-MODEL-DEL2-2015¦45¦resultaterne for 45 vandområder accepteret⟧.⟦E⟧
- ⟦B¦C-GC-G-CG-GRADED⟧The effect is **strongly graded by geography** — ⟦V¦hjarbaek_chl¦.0f⟧% of the chlorophyll indicator in Hjarbæk Fjord, ⟦R¦DHI-MODEL-DEL2-2015¦0.2¦Østersøen, Bornholm 56 0,2 0,3⟧% off Bornholm.⟦E⟧
- ⟦B¦C-GC-G-CG-TRUTH⟧Neither side has ground truth. There is no documented "right" target loading, and DHI says so.⟦E⟧
- ⟦B¦C-GC-G-CG-HYPOXIA⟧Hypoxia is a joint product of organic matter supply, weather and hydrography. DCE says it, the models implement it, we argue it.⟦E⟧
- ⟦B¦C-GC-G-CG-EELGRASS⟧Eelgrass loss is self-reinforcing and may not reverse when light returns. DHI models it and warns of it.⟦E⟧
- ⟦B¦C-GC-G-CG-SLOPE⟧The published uncertainty covers the slope only.⟦E⟧

### Where a reasonable person lands

⟦B¦C-GC-G-LANDS⟧The Danish evidence base is **much better than a critic who has read only the summaries would guess, and much narrower than a defender who has read only the summaries would guess.**⟦E⟧

⟦B¦C-GC-G-SUPPORTS⟧It supports a well-founded statement of this form:⟦E⟧

> *Reducing Danish land-based nitrogen by X% would improve summer chlorophyll and water clarity in this water body by roughly Y%, assuming the climate does not change and our neighbours meet their commitments.*

⟦B¦C-GC-G-NOTSUPPORT⟧It does not support *"nitrogen from agriculture causes N% of the oxygen depletion"*, and it says nothing about fedtemøg: none of the six pinned documents in the chain names it. The gap between what the science says and what the politics says is where this project belongs — and it is a defensible place to stand precisely because the scientists' own caveats are the evidence for it.⟦E⟧

### What would have to be true for them to be right and us wrong

- ⟦B¦C-GC-G-TR-STATS⟧Summer chlorophyll and summer Kd would have to be adequate sufficient statistics for ecological status, so that fixing them fixes the rest. The mechanistic models compute oxygen and were not asked to produce a requirement from it.⟦E⟧
- ⟦B¦C-GC-G-TR-SLOPES⟧The fitted slopes would have to hold down to ⟦R¦DHI-MODEL-DEL2-2015¦30–60¦Nutid minus 15% Nutid minus 30% Nutid minus 60%⟧% reductions. Both DCE and DHI say this is unverifiable and warn that uncertainty grows with distance from the calibration domain.⟦E⟧
- ⟦B¦C-GC-G-TR-REGIME⟧No regime shift. Both documents flag it and say it cannot be predicted.⟦E⟧
- ⟦B¦C-GC-G-TR-BSAP⟧BSAP and the Gothenburg Protocol delivered by our neighbours, because every scenario assumes it.⟦E⟧
- ⟦B¦C-GC-G-TR-STATION⟧One station per water body spatially representative. DCE raises this and does not resolve it.⟦E⟧
- ⟦B¦C-GC-G-TR-TARGETS⟧The VP3 chlorophyll targets right rather than the intercalibrated ones.⟦E⟧

### What would have to be true for us to be right and them wrong

- ⟦B¦C-GC-G-US-ROUTES⟧The unmeasured routes to shore biomass — direct organic delivery, killing in place, sediment regeneration — would have to be large relative to the growth route in the specific bays where damage is complained about. This project has no measurement of any of them.⟦E⟧
- ⟦B¦C-GC-G-US-STATE⟧The state term would have to dominate the load term. Mechanistically supported; this project holds it as a hypothesis and has not quantified it.⟦E⟧
- ⟦B¦C-GC-G-US-EXTREMES⟧The extremes would have to be genuinely insensitive to load rather than merely noisy, and a comparison of extremes cannot tell the two apart.⟦E⟧
- ⟦B¦C-GC-G-US-FEDTE⟧Fedtemøg would have to have a different driver or season from what is assumed. Currently unfalsifiable in either direction, because no programme this project has found measures it.⟦E⟧

### The honest asymmetry

⟦B¦C-GC-G-ASYM⟧Their case rests on a documented method with stated limitations, applied beyond the range where those limitations were tested. Our case rests on identifying real omissions and has, so far, no measurement of its own for any of them.⟦E⟧

⟦B¦C-GC-G-ASYM2⟧**Those are not symmetrical positions.** The right conclusion is not that they are wrong. It is that the instrument is being asked a question it was not built for.⟦E⟧

---

## Sources

⟦B¦C-GC-G-CHAINFILE⟧Structured, with verbatim quotes and per-claim `verified_by_reading` flags: `data/manual/science_chain.json`.⟦E⟧

⟦B¦C-GC-G-DOCS⟧Primary documents read for this page:⟦E⟧

1. Erichsen, Timmermann, Kaas, Markager, Christensen & Murray (2014, rev. 2015). *Modeller for Danske Fjorde og Kystnære Havområder – Del ⟦R¦DHI-MODEL-DEL1-2015¦1¦Havområder – Del 1 Metode til bestemmelse af målbelastning⟧. Metode til bestemmelse af målbelastning.* DHI/DCE for Naturstyrelsen. ⟦P¦DHI-MODEL-DEL1-2015⟧ pp. — [PDF](https://sgavmst.dk/media/hvomfapx/31-modeller-for-danske-fjorde-og-kystnaere-havomraader-del-1.pdf)
2. Erichsen & Kaas (2015). *… – Del ⟦R¦DHI-MODEL-DEL2-2015¦2¦Havområder – del 2 Mekanistiske modeller og metode til bestemmelse af indsatsbehov⟧. Mekanistiske modeller og metode til bestemmelse af indsatsbehov.* DHI. ⟦P¦DHI-MODEL-DEL2-2015⟧ pp. — [PDF](https://edit.mst.dk/media/lspfqzss/312-modeller-for-danske-fjorde-og-kystnaere-havomraader-del-2.pdf)
3. Timmermann, Christensen, Murray & Markager (2015). *… – Del ⟦R¦DCE-STATMOD-2015¦3¦Havområder – del 3 Statistiske modeller og metoder til bestemmelse af indsatsbehov⟧. Statistiske modeller og metoder til bestemmelse af indsatsbehov.* DCE/AU. ⟦P¦DCE-STATMOD-2015⟧ pp. — [PDF](https://dce.au.dk/fileadmin/dce.au.dk/Udgivelser/Notater_2015/Dokumentation_statistiske_modeller_metoder_del3_28042015.pdf)
4. Miljøstyrelsen (2023). *NOVANA. Det nationale overvågningsprogram for vandmiljø og natur ⟦R¦NOVANA-2327¦2023-27¦NOVANA 2023-27⟧.* — [PDF](https://www2.mst.dk/Udgiv/publikationer/2023/09/978-87-7038-556-5.pdf)
5. Finansministeriet m.fl. (Sept 2024). *Second opinion – Evaluering af det faglige grundlag for kvælstofindsatsen.*
6. Finansministeriet m.fl. (Nov 2024). *Second opinion – Baggrundsanalyser.* ⟦P¦SO-BG-2024⟧ pp.
7. Miljøministeriet. *Retningslinjer for udarbejdelse af vandområdeplaner 2021-2027.*

⟦B¦C-GC-G-NOTOBTAINED⟧**Not obtained, and this limits the page.** Herman et al. 2017 and 2023 are quoted only through the ministries' Danish translation, which itself warns that editorial choices were made. Erichsen et al. 2023, the VP3 model update, has not been read, so **every model-level number here is VP2-era unless marked otherwise**. Hansen & Rytter 2024, Timmermann et al. `2024a/b`, Erichsen et al. `2019/2020a/2020b` and Markager & Storm 2003 are cited from reference lists only.⟦E⟧
'''


if __name__ == "__main__":
    sys.exit(main())
