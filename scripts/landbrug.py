#!/usr/bin/env python3
"""Generate docs/LANDBRUG.md - the audit, addressed to the people it is used against.

Everything else on this site is written for whoever turns up. This page is written for
one audience: farmers and the organisations that represent them, who are being handed a
quantified reduction target justified by a number this project has taken apart.

It is in Danish because the audience is Danish and an English document from an outsider
gets filed under "foreigner with opinions" before it is read.

The document concedes deliberately and early. An argument that admits what it cannot
show is much harder to dismiss than one that claims too much. Every number on the page
is read from data, a pinned document or arithmetic on those, and every statement is a
checked claim (LIVE_NUMBERS.md section 11), registered in
data/manual/claims.d/w3-le.json with what it rests on. What the page once said and
could not justify is in docs/ARCHIVE.md, not here.

Usage:  python3 scripts/landbrug.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, read_json, write_doc
import claims as _claims
import live

MANUAL = os.path.join(ROOT, "data", "manual")
AGRI_PCT = 69.6           # the published agricultural share; declared, not pinned here
C_PER_COD = 0.375         # kg C per kg COD: one O2 (32) oxidises one C (12)
C_PER_N = (106 * 12.011) / (16 * 14.007)   # Redfield C:N 106:16, as a mass ratio
FACTS = os.path.join(DERIVED, "landbrug.json")

C, B, E = live.claim, live.claim_begin, live.CLAIM_END
_REG = {}

# empty rows the pathway register itself places inside other rows, or calls a timing
# term: filling them adds nothing to the total. The build refuses if the notes change.
INSIDE = {"Shipping NOx deposited locally": "inside the deposition total",
          "Drained organic soils / lowmoor peat": "inside the diffuse residual",
          "Legacy N still in transit": "not an extra source"}


def dk(marked):
    """Danish decimal comma in the shown text of a live number (ids carry no dot)."""
    return marked.replace(".", ",")


def dkt(marked):
    """Danish thousands separator in the shown text of a live number (ids carry no comma)."""
    return marked.replace(",", ".")


def _cl():
    if "d" not in _REG:
        _REG["d"] = _claims.load()[0]
    return _REG["d"]


def RD(sid, value, phrase):
    """A number read from a pinned document, refused unless the pinned copy holds the
    phrase. Each reading has its own phrase: two readings with one phrase share an id."""
    d = _cl()
    if _claims._flat(phrase) not in _claims._flat(_claims.pin_text(d, sid)):
        raise live.Unjustified(f"{sid}: the pinned text does not contain '{phrase}'")
    return live._mk(value, ["reading", sid, "phrase", phrase, _claims._meta(d, sid)])


def main():
    # the few numbers this page derives itself are stored, then read back live
    raw = read_json(os.path.join(MANUAL, "nitrogen_pathways.json"))["pathways"]
    os.makedirs(DERIVED, exist_ok=True)
    with open(FACTS, "w", encoding="utf-8") as f:
        json.dump({"_what": "Counts and constants LANDBRUG.md prints, written by "
                            "scripts/landbrug.py.",
                   "n_pathways": len(raw),
                   "n_unquantified": sum(1 for p in raw if p["lo"] is None),
                   "agri_pct": AGRI_PCT, "c_per_n": C_PER_N, "c_per_cod": C_PER_COD},
                  f, ensure_ascii=False, indent=1)
        f.write("\n")
    path = os.path.join(ROOT, "docs", "LANDBRUG.md")
    try:
        text = render()
        write_doc(path, text)
    except (live.Unjustified, _claims.Refused) as e:
        log(str(e))
        return 1
    log(f"wrote docs/LANDBRUG.md ({len(text):,} chars)")
    return 0


def render():
    F = live.live_json(FACTS)
    paths = live.live_json(os.path.join(MANUAL, "nitrogen_pathways.json"))["pathways"]
    mon = live.live_json(os.path.join(MANUAL, "monitoring.json"))
    tt = mon["typetal_nutrients_mg_per_l"]
    hz = mon["hazardous_substances"]
    ov = mon["overflow_reporting"]
    dl = mon["diffuse_load"]

    # the published share, read from DANVA's page; the arithmetic uses the same value as
    # stored in landbrug.json, and the page is refused if the two ever differ
    PCT = RD("DANVA-2024", 69.6, "hvor landbruget alene står for 69,6 %")
    if abs(float(PCT) - F["agri_pct"]) > 1e-9:
        raise live.Unjustified("landbrug: landbrug.json's agri_pct no longer matches DANVA's page")
    pct = dk(format(PCT, ".1f"))
    CUT = RD("DCE-STATMOD-2015", 25, "fastsættes et indsatsbehov på 25 %")
    CUTQ = RD("DCE-STATMOD-2015", 25, "det vurderes at en 25 % reduktion")
    RED = RD("SR353", 51, "The reductions are 51% and 72% for nitrogen and phosphorus")
    KM24 = RD("PC-DCE-ILT-2024", 11000, "udgjorde midt i september 11.000 km2")
    YES = RD("POL-TV2-20260903", 119, "119 medlemmer af Folketinget stemte for loven")
    NO = RD("POL-TV2-20260903", 34, "mens 34 stemte imod")

    land = [p for p in paths if p["pathway"].startswith("Danish land via")]
    land_lo = sum(p["lo"] for p in land)
    land_hi = sum(p["hi"] for p in land)
    agri_lo, agri_hi = land_lo * F["agri_pct"] / 100, land_hi * F["agri_pct"] / 100
    atm = next(p for p in paths if p["pathway"].startswith("Atmospheric deposition"))
    quant = [p for p in paths if p["lo"] is not None]
    tot_lo = sum(p["lo"] for p in quant)
    tot_hi = sum(p["hi"] for p in quant)
    ceil_hi = agri_hi / tot_lo * 100
    ceil_lo = agri_lo / tot_hi * 100
    cso = next(p for p in paths if p["pathway"].startswith("Rain-dependent overflow, combined"))
    cso_lo = cso["typetal_kt"] / land_hi * 100
    cso_hi = cso["typetal_kt"] / land_lo * 100
    for name, note in INSIDE.items():
        row = next((p for p in paths if p["pathway"] == name), None)
        if row is None or row["lo"] is not None or note not in str(row["note"]):
            raise live.Unjustified(f"landbrug: the register no longer says '{note}' of '{name}'")
    lv = {k["level"]: k for k in ov["knowledge_levels"]}
    n_unq, n_all = F["n_unquantified"], F["n_pathways"]
    ret = dl["retention_uncertainty_national_average_pct_points"]
    k12, d8, t4 = live.ref("K12"), live.ref("D8"), live.ref("T4", family="hypotheses")

    o = []
    a = o.append

    a("# Til landbruget: grundlaget for kravet\n")
    a("> " + C("C-LE-LEFTOVER", "**Landbrugets andel er ikke målt.** Den regnes som det, der er "
        "tilbage: den samlede kvælstoftilførsel fra land minus punktkilderne giver det diffuse "
        "bidrag, og det diffuse bidrag minus det naturlige baggrundsbidrag er det, der kaldes "
        "landbrugets andel. Det er en restpost - og alt, hvad der er regnet forkert eller mangler "
        "i de andre poster, havner i den. [Hvordan hver post er lavet](NITROGEN.md).") + "\n")
    a(C("C-LE-FIX", "*Har du fundet en fejl? [Skriv den her](https://github.com/Jjokulian/copenhagen-waterways/issues). Hvad sitet har "
        "trukket tilbage, står med begrundelse i [arkivet](ARCHIVE.md).*") + "\n")
    a("> ## Om koefficienterne\n")
    a("> " + C("C-LE-SLOPE", "**For klorofyl og lyssvækkelse findes der en koefficient.** DCE "
               "har opstillet statistiske relationer mellem kvælstoftilførslen og indikatorerne, "
               "og indsatsbehovet regnes ud af relationens hældning, som angiver, hvor følsom "
               "indikatoren er over for ændringer i N-tilførslen.") + "\n")
    a("> " + C("C-LE-TRIGGER", "**For iltsvind findes der ingen.** Iltsvindsindikatoren er en "
               "*binær udløser*: viser én eller flere af iltsvindsindikatorerne, at et vandområde "
               f"er ramt, sættes indsatsbehovet til en reduktion på **{CUT} %** af vandområdets "
               "nuværende TN-koncentration, uanset hvor slemt iltsvindet er. Hvor meget "
               "tilførslen så skal ned, regner DCE ud af vandområdets egen relation mellem "
               "N-tilførsel og TN-koncentration.") + "\n")
    a("> " + C("C-LE-WHY25", "DCE skriver selv, hvorfor tallet er valgt: det skal være "
               "tilstrækkeligt stort til at rykke systemet, *større end de normale år-til-år "
               f"variationer*, og ”det vurderes at en {CUTQ} % reduktion i TN-koncentrationen er "
               "minimumskrav for at ændre systemet”.") + " "
      + C("C-LE-JUDGED", "Det er en fagligt begrundet tommelfingerregel, ikke en målt dæmpning: "
          "begrundelsen er år-til-år-variationen og en vurdering, ikke en sammenhæng mellem "
          "kvælstof og ilt, og DCE skriver i samme rapport, at der ikke findes en interkalibreret "
          "indikator for ilt.") + "\n")
    a("> " + C("C-LE-MINISTER", "Da den nye reguleringsmodel blev fremlagt, sagde ministeren, at "
               "*”for meget kvælstof på landbrugets marker har ført til iltsvind og ødelagt "
               "levesteder for fisk, muslinger og planter”*.") + " "
      + C("C-LE-THERE", "Og netop for iltsvind er kravet en vurdering, ikke en fittet "
          "sammenhæng.") + "\n")
    a("*" + C("C-LE-LANG", "Denne side er skrevet på dansk og henvender sig til landmænd og deres "
              "organisationer. Resten af sitet er på engelsk.") + "* "
      "*[An English summary follows at the bottom.](#in-english)*\n")
    a("> " + C("C-LE-NOTPARTISAN", "**Hvad dette er, og hvad det ikke er.** Dette er ikke et "
               "partsindlæg for landbruget.") + " "
      + C("C-LE-CITY-TOO", "Projektet her tager også byens egne udledninger fra hinanden — "
          "regnbetingede overløb, spildevandsplanens huller, hvad Københavns skybrudsplan "
          "faktisk dækker.") + " "
      + C("C-LE-SAME", "Det er *samme* metode anvendt på kvælstoftallet, og resultatet er "
          "ubelejligt for flere end landbruget.") + "\n")

    # ---------------------------------------------------------------- 1
    a(f"## 1. Hvad de {pct} % faktisk er en andel af\n")
    a(C("C-LE-SCOPE", "Tallet er landbrugets andel af det kvælstof, der udledes til kystvandene, "
        "fordelt på kilder: **den landbaserede, vandbårne post** — kvælstof, der når kysten "
        f"gennem danske vandløb og umålte oplande. Det er to rækker ud af de {n_all} veje, ad "
        "hvilke reaktivt kvælstof når danske havområder, som projektet har kunnet opregne:") + "\n")
    a("| Række | kt N/år | Grundlag |")
    a("|---|---:|---|")
    for p in land:
        st = {"PARTLY MEASURED": "delvist målt", "MODELLED": "modelleret"}.get(
            p["status"], p["status"].lower())
        a(f"| {p['pathway'].replace('Danish land via monitored streams', 'Dansk land via målte vandløb').replace('Danish land via unmonitored catchments', 'Dansk land via umålte oplande')} "
          f"| {p['lo']:.0f} – {p['hi']:.0f} | {st} |")
    a(f"| **Posten, andelen deler** | **{land_lo:.0f} – {land_hi:.0f}** | |")
    a(f"| **{pct} % af den** | **{agri_lo:.0f} – {agri_hi:.0f}** | |")
    a("")
    a(C("C-LE-EMPTY", f"De **{n_unq} af {n_all} veje har slet intet tal** — heriblandt organisk "
        "kvælstof i den atmosfæriske afsætning, udsivning af grundvand under havet og frigivelse "
        "fra sedimentet. De veje, der *har* et tal, summerer til "
        f"**{tot_lo:.0f} – {tot_hi:.0f} kt N/år**.") + "\n")
    a(C("C-LE-FLOOR", "En tom række, der er en kilde for sig, kan kun lægge til. Nævneren har "
        "altså et gulv og intet loft, og enhver andel regnet mod den er et **loft, ikke et "
        "estimat**:") + "\n")
    a("> " + C("C-LE-CEILING", f"På projektets egne grænser står landbruget for **højst "
               f"{ceil_hi:.0f} %** af det opgjorte reaktive kvælstof, der når danske havområder, og "
               f"ved den brede ende af grænserne for ned til {ceil_lo:.0f} %. Grænserne har ikke en "
               "kilde for hver række, så loftet er ikke bedre end dem.") + "\n")
    a(C("C-LE-NOTADD", "Ikke alle tomme rækker lægger til. Kvælstof fra skibsfart, der afsættes "
        "lokalt, ligger allerede inde i afsætningen; drænede organiske jorde ligger inde i den "
        "diffuse restpost; og kvælstof, der stadig er undervejs, er en tidsforskydning af de andre "
        "rækker, ikke en ekstra kilde. De øvrige tomme rækker kan kun sænke loftet, når de bliver "
        "fyldt ud.") + "\n")
    a(C("C-LE-DEPOSITION", "Til sammenligning: **atmosfærisk afsætning direkte på havoverfladen "
        f"er {atm['lo']:.0f}–{atm['hi']:.0f} kt N/år** i projektets register — på størrelse med "
        "hele den landbaserede post — og den er ikke en linje i den fordeling, andelen kommer "
        "fra.") + "\n")

    # ---------------------------------------------------------------- 2
    a("## 2. Tallet er en restpost, ikke en måling\n")
    a(C("C-LE-RESIDUAL", "Sådan fremkommer landbrugsandelen: den målte og modellerede transport "
        "fra land, minus punktkilderne — renseanlæg og industri, som indberetter deres "
        "udledninger, og overløb og regnvand, som modelleres — minus et naturligt "
        "baggrundsbidrag, der bestemmes i små oplande med lille menneskelig påvirkning og overføres "
        "til resten. Det, der bliver tilbage, kaldes landbrug, og det rummer også den spredte "
        "bebyggelse, som ikke kan skilles ud.") + "\n")
    a("| | |")
    a("|---|---|")
    a("| Måledækning | " + C("C-LE-R-COVER", f"{dl['area_measured_pct']} % af arealet måles, "
                                f"{dl['area_modelled_pct']} % modelleres") + " |")
    a("| Målemetode | " + C("C-LE-R-METHOD", "stikprøver med faste mellemrum; transporten "
                               "beregnes som summen af daglig vandføring gange lineært "
                               "interpoleret koncentration") + " |")
    a("| Dokumenteret skævhed | " + C("C-LE-R-BIAS", "i alle tre vandløb i GUDP-undersøgelsen fra "
                                        "2018 gav stikprøverne **altid lavere** transport end "
                                        "intensiv daglig måling") + " |")
    a("| Retentionens usikkerhed | " + C("C-LE-R-RETENTION", f"± {ret} procentpoint på "
                                            "landsgennemsnittet") + " |")
    a("| Estimatorens opførsel | " + C("C-LE-R-DRY", "i tørre år som 1996 og 2005 er det "
                                          "beregnede dyrkningsbidrag kommet ud **negativt**") + " |")
    a("")
    a(C("C-LE-R-SOURCE", "Rækkerne står i projektets register over overvågningen, som ikke "
        "angiver, hvor de kommer fra; de dokumenter, de bygger på, er ikke fastholdt her.") + "\n")
    a(C("C-LE-NEGATIVE", "En beregnet størrelse, der bliver negativ, hvor den fysiske mængde ikke "
        "kan være det, har en fejl, der kan være større end selve signalet. Den er det, der bliver "
        "tilbage, når modellerede led trækkes fra en delvist modelleret total, og den arver "
        "fejlene i dem alle — og andelen offentliggøres med én decimal og uden usikkerhed.") + "\n")

    # ---------------------------------------------------------------- 3
    a("## 3. Tre led mangler mellem tallet og skaden\n")
    a(C("C-LE-FEDT", "*Fedtemøg* er en folkelig betegnelse for masseforekomster af løstliggende, "
        "trådformede brunalger, som kan ligge og rådne i vandkanten og på stranden.") + " "
      + C("C-LE-PUBLIC", "I den offentlige debat, som projektet har fastholdt, knyttes fedtemøg og "
          "iltsvind til landbrugets kvælstof. Den danske Wikipedia-artikel om fedtemøg skriver, at "
          "forekomsten ved danske kyster *”skyldes især landbrugets udledning af kvælstof”*, og "
          "Danmarks Naturfredningsforenings præsident sagde om kvælstofaftalen: *”År efter år har "
          "vi set forfærdeligt iltsvind og fedtemøg. Skal havet have en chance, må landbrugets "
          "kvælstofforurening ned.”*") + "\n")
    a(C("C-LE-JOIN", f"Andelen på {pct} % kommer fra en tredje kilde. Ingen af dem, der citeres "
        "her, ganger de to sammen, men argumentet indbyder læseren til det. Mellem andelen og "
        "skaden ligger disse led:") + "\n")
    a("| Led | Koefficient |")
    a("|---|---|")
    a("| Landbrug → den landbaserede, vandbårne kvælstofpost | "
      + C("C-LE-L1", f"**{pct} %, offentliggjort.** En restpost: målt og modelleret total minus "
          f"punktkilder minus modelleret baggrund, med en usikkerhed på retentionen på ± {ret} "
          "procentpoint i projektets register, som ikke angiver en kilde til den") + " |")
    a("| Den post → alt reaktivt kvælstof, der når havet | "
      + C("C-LE-L2", f"**ingen: mængden er åben.** {n_unq} af {n_all} opregnede veje har intet "
          "tal, heriblandt organisk kvælstof i afsætningen, udsivning af grundvand under havet og "
          "frigivelse fra sedimentet") + " |")
    a("| Kvælstof i havet → iltsvind | "
      + C("C-LE-L3", f"**ingen fittet koefficient.** DCE's krav er en vurderet reduktion på {CUT} % "
          "af TN-koncentrationen. Iltsvind opstår af et samspil mellem mængden af dødt organisk "
          "stof, klimatiske forhold og vandområdets hydrografi, og kvælstof er én vej til det døde "
          "stof blandt flere. Der er ingen potensfaktor: et kilo i februar i en opblandet "
          "vandsøjle tæller som et kilo i juli under et springlag") + " |")
    a("| Kvælstof i havet → algevækst → fedtemøg på en strand | "
      + C("C-LE-L4", "**intet beregnet.** Algerne vokser også på lys, fosfor, en sæson og noget at "
          "hæfte sig på, og på kvælstof, der frigives på stedet; trådene river sig løs, driver og "
          "strander, hvilket kræver vind og en kyst. Ingen serie over strandens tilstand er fundet "
          "i nogen af de kilder, projektet har gennemgået") + " |")
    a("")
    a(C("C-LE-EVERYLINK", "Hvert led er en reel årsagssammenhæng, og de tre sidste har intet tal "
        "her. Et produkt af ukendte brøker er en ukendt brøk — **ikke en lille**. Landbruget kan "
        "stadig være den største enkelte bidragyder i hvert led; det har projektet ikke regnet ud, "
        "og ingen kilde, det har, gør det.") + "\n")
    a(C("C-LE-FAUNA", "Selv hvor der er en sammenhæng, ser overvågningen den dårligt: bundfaunaen "
        "på blød bund prøvetages i tidsrummet 1. marts – 31. maj, så en dødelighed sidst på "
        "sommeren og om efteråret ses først bagefter, når genindvandringen er begyndt.") + "\n")

    # ---------------------------------------------------------------- 4
    a("## 4. Det, der er sket siden 1990\n")
    a(C("C-LE-REDUCTION", "**Indgrebet.** DCE's rapport om vandløbene opgør faldet i tilførslen "
        f"af kvælstof fra land til de danske kystvande i perioden 1990–2018 til {RED} %, beregnet "
        "på vandføringsvægtede årsmiddelkoncentrationer.") + " "
      + C("C-LE-NOTDISPUTED", "Denne side bestrider hverken faldet eller indsatsen bag det.") + "\n")
    a(C("C-LE-OUTCOME", "**Udfaldet.** DCE's notat fra efteråret 2023 kaldte iltsvindet i midten "
        "af september det hidtil næststørste registrerede. I midten af september 2024 dækkede "
        f"iltsvindet {dkt(format(KM24, ','))} km², og DCE kaldte det igen det hidtil næststørste "
        "registrerede, kun overgået af iltsvindet i 2002.") + "\n")
    a(C("C-LE-JUXTA", "**Side om side:** tilførslen fra land er omtrent halveret, og udbredelsen i "
        "september 2024 var den næststørste registrerede. Yderpunkterne følger ikke tydeligt "
        "belastningen. Men en sammenligning af udvalgte år kan ikke bære en trend i en serie med "
        "store udsving fra år til år, den kan ikke skelne *ingen virkning* fra *værre uden*, og "
        "varmere vand holder på mindre ilt og trækker dermed imod en lavere belastning. Det er en "
        "iagttagelse, ikke en test — det sidste afsnit siger, hvad der ville være en.") + "\n")
    a(C("C-LE-NOTIRRELEVANT", "Det er ikke bevis for, at kvælstof er ligegyldigt.") + " "
      + C("C-LE-WEATHER", "Det er heller ikke bevis for, hvad der så styrer udbredelsen. DCE "
          "forklarer, hvordan en iltsvindssæson udvikler sig, med årets vejr: vind, der blander "
          "vandsøjlen, bremser iltsvindet, og høj vandtemperatur fremmer det, fordi iltforbruget "
          "stiger med temperaturen, og iltens opløselighed falder. En belastningsserie, der er "
          "regnet, så vejret er taget ud, kan derfor ikke læses mod yderpunkterne år for år.") + " "
      + C("C-LE-STATE", f"Registret har desuden hypoteser om, at havbundens tilstand spiller ind: "
          f"{k12}, {d8} og {t4} beskriver hver en måde, hvorpå den samme belastning kan gøre mere "
          "skade nu end før.") + " "
      + C("C-LE-NOTSOURCE", "Ingen af de to ting kan en kildeopgørelse udtrykke, for ingen af dem "
          "er en kilde.") + "\n")

    # ---------------------------------------------------------------- 5
    a("## 5. Det, byen slipper for at få talt med\n")
    a(C("C-LE-C-INTRO", "Samme metode på byens egne udledninger, så det er klart, at kritikken "
        "ikke kun peger én vej:") + "\n")
    a("- " + C("C-LE-C-OVERFLOW", "**Overløbsmængder opgøres på videnniveauer**, fra en beregning "
               "i PULS over modeller til målebaseret overløbsestimering. PULS registrerer antal "
               "overløb og ingen vandføring. Stofmængden beregnes med typetal ud fra den "
               "indberettede vandmængde — og kvalitetskontrolleres ved at tjekke, om "
               "koncentrationen ligger inden for et interval omkring det samme typetal. "
               "Usikkerheden på den udledte stofmængde er angivet til "
               f"{lv[1]['uncertainty_pct']} % på videnniveau {lv[1]['level']}, en simpel "
               f"massebalance; for niveau {lv[0]['level']}, en beregning i PULS, er der ingen "
               "angivet."))
    a("- " + C("C-LE-C-TYPETAL", "**Typetallene for miljøfarlige stoffer** hviler på "
               f"{hz['stations_combined_overflow']} målestationer for fællessystem og "
               f"{hz['stations_separate_stormwater']} for separat regnvand — i oplande *valgt* til at "
               "repræsentere husholdninger og boligområder, og udtrykkeligt afgrænset over for "
               "industriområder og stærkt trafikerede veje. Samme rapport finder, at en væsentlig "
               "andel af de adsorberende stoffer bliver fanget i sedimentet i regnvandsbassiner, "
               "som typetallene ikke dækker."))
    a("- " + C("C-LE-C-CSO", "**Et fællessystemsoverløb leverer omtrent lige så meget organisk "
               "kulstof direkte, som dets kvælstof kunne nå at producere.** Ved typetallene i "
               "projektets register og Redfield-forholdet svarer "
               f"{tt['combined_overflow']['Tot-N']:.0f} mg N/l til "
               f"{tt['combined_overflow']['Tot-N'] * F['c_per_n']:.0f} mg C/l; vandet bærer selv "
               f"{tt['combined_overflow']['COD'] * F['c_per_cod']:.0f} mg C/l. Kvælstofopgørelsen "
               "tæller kun den ene halvdel, og i projektets register er overløbets kvælstof "
               f"{dk(format(cso_lo, '.1f'))}–{dk(format(cso_hi, '.1f'))} % af den landbaserede "
               "post."))
    a("- " + C("C-LE-C-FAT", "**Fedt indeholder intet kvælstof overhovedet.** Triglycerider "
               "består af kulstof, brint og ilt. En kvælstofopgørelse kan ikke undervurdere det "
               "materiale — den kan slet ikke se det. Kloakker samler fedt som aflejringer, og et "
               "overløb sker kun, når vandføringen overstiger en tærskel, altså i de timer, hvor "
               "vandet går uden om renseanlægget; hvor meget fedt der følger med ud, er ikke "
               "opgjort i nogen kilde, projektet har."))
    a("")

    # ---------------------------------------------------------------- 6
    a("## 6. Hvad dette **ikke** viser\n")
    a(C("C-LE-CONCEDE", "Dette afsnit står her, fordi et argument, der indrømmer, hvad det ikke kan "
        "vise, er langt sværere at afvise end et, der påstår for meget.") + "\n")
    a("- " + C("C-LE-NOTHOOK", "**Det viser ikke, at landbruget er uden andel.** At gange ukendte "
               "brøker giver en ukendt, ikke en lille. Landbruget er sandsynligvis stadig den "
               "største enkelte kvælstofkilde, og belastningen er reel."))
    a("- " + C("C-LE-NOTFAILED", "**Det viser ikke, at kvælstofpolitikken har fejlet.** "
               "*Nødvendig* og *utilstrækkelig* er to forskellige konklusioner, og forløbet siden "
               "1990 er foreneligt med den anden."))
    a("- " + C("C-LE-NOTNOTHING", "**Og det er ikke et argument for at gøre ingenting.** Det er et "
               "argument for at gøre noget andet — og for at måle det."))
    a("")
    a(C("C-LE-SHOWS", "Det, det *viser*, er snævrere: **den del af kravet, der hviler på iltsvind, "
        f"har ingen fittet sammenhæng bag sig; andelen på {pct} % er ikke en andel af alt det "
        "kvælstof, der når havet; og de seneste yderpunkter følger ikke tydeligt en belastning, der "
        "er omtrent halveret.** Hvis instrumentet er fejlspecificeret, kan det kun anbefale "
        "mere af det samme, når det samme ikke virker, for det er det eneste, en kildeopgørelse "
        "kan udtrykke.") + "\n")

    # ---------------------------------------------------------------- 7
    a("## 7. Hvis begrænsningen er havets evne til at optage, bliver løsningsrummet større\n")
    a(C("C-LE-7-SUPPOSE", "Antag et øjeblik, at skaden ikke er *f(belastning)* men "
        "*f(belastning, tilstand)* — at det samme kilo kvælstof gør mere skade i 2025 end i 1990, "
        "fordi ålegræsset, filtratorerne og en sammenhængende havbund er væk. Så er der to "
        "håndtag, ikke ét: tilførslen og havets egen tilstand.") + " "
      + C("C-LE-7-WEIGHED", "Det andet håndtag har været vejet. Ifølge den second opinion om det "
          "faglige grundlag for kvælstofindsatsen, som Ministeriet for Grøn Trepart offentliggjorde "
          "i 2024, valgte ingen af kystvandrådene at tage marine virkemidler direkte med i deres "
          "indstillede indsatsprogrammer, mens rådene for Odense Fjord og Limfjorden anbefalede "
          "enkle marine virkemidler som supplerende indsatser — som dog ikke vurderes at kunne "
          "erstatte andre indsatser. Og muslingeopdræt bruges i dag ikke som marint virkemiddel i "
          "vandområdeplanen, skriver projektet BalticMUPPETS.") + "\n")
    a("| Virkemiddel | Hvad det gør, som reduktion på land ikke gør |")
    a("|---|---|")
    a("| **Muslinge- og tangopdræt** | "
      + C("C-LE-7-MUSSEL", "optager kvælstof, der **allerede er i vandet**, og fjerner det, når "
          "høsten tages op: næringssalte fra land bygges ind i muslingerne og føres tilbage til "
          "land, når de høstes, og høstet tang tager næringsstofferne helt ud af havmiljøet") + " |")
    a("| **Ålegræs og bundintegritet** | "
      + C("C-LE-7-EELGRASS", "optager, stabiliserer og giver levested på én gang, hvor lyset "
          f"tillader det; registret har hypoteser om, hvad tabet af dem gør ved bunden ({k12}, "
          f"{d8}, {t4})") + " |")
    a("| **Vådområder og efterafgrøder** | "
      + C("C-LE-7-LAND", "virker på tilførslen fra land, før kvælstoffet når havet — ikke på det, "
          "der allerede er der") + " |")
    a("")
    a(C("C-LE-7-PRODUCTION", "Det særlige ved marin ekstraktion er, at den **er en produktion**: "
        "muslingemel er afprøvet som foder til grise og fjerkræ, og høstet tang kan bruges til "
        "foder. Hvor kvælstoffet fjernes ved, at biomassen tages op og bruges, er foderet selve "
        "miljøydelsen.") + "\n")

    # ---------------------------------------------------------------- 8
    a("## 8. Og dermed et led, der sjældent trækkes\n")
    a(C("C-LE-8-FEED", "Et dyr, der lever længere, skal fodres længere. Hvis et "
        "kvælstofvirkemiddel *producerer* foder og betales som miljøydelse, kan den samme politik "
        "betale en del af det foder, der skal til, for at dyr kan leve længere, i stedet for at "
        "besætninger bliver mindre.") + "\n")
    a(C("C-LE-8-DECOUPLE", "Det er ikke en omskrivning. Det er en ændring af, hvad betalingen er "
        "knyttet til: **et foderflow, der betales for at fjerne kvælstof fra havet, betaler for "
        "det, dyret spiser, mens det lever, ikke for det, det giver ved slagtning.**") + "\n")
    a(C("C-LE-8-CAVEATS", "Forbeholdene, som skal med, ellers er det reklame:") + "\n")
    a("- " + C("C-LE-8-METALS", "Muslinger ophober miljøfremmede stoffer fra omgivelserne — derfor "
               "bruges de til at overvåge havmiljøet. Hvor høsten må gå hen, afgøres af analyse, "
               "ikke af hensigt, og zink og kobber, som er nødvendige sporstoffer, er ikke det "
               "samme som cadmium, der ingen kendt funktion har i højere organismer, og kviksølv, "
               "der som methylkviksølv opkoncentreres op gennem fødekæderne i vand."))
    a("- " + C("C-LE-8-TESTED", "Kompensationsopdræt af muslinger er afprøvet i fuld skala i Skive "
               "Fjord, og DCE har regnet omkostningen pr. kilo fjernet kvælstof ud under de "
               "forhold, der blev testet. Alligevel bruges muslingeopdræt i dag ikke som marint "
               "virkemiddel i vandområdeplanen."))
    a("- " + C("C-LE-8-NOONE", "Og intet af dette fritager nogen. Det udvider listen over, hvad der "
               "kan gøres."))
    a("")

    # ---------------------------------------------------------------- 9
    a("## 9. Hvad man konkret kan forlange\n")
    a(C("C-LE-9-INTRO", "Ikke *drop kravet*. Det er en tabt sag og en dårlig sag: gødskningsloven "
        f"`L 5` blev vedtaget med {YES} stemmer mod {NO}, og belastningen er reel. I stedet fire "
        "ting, som ingen kan afvise uden at forklare hvorfor:") + "\n")
    a("| Krav | Hvorfor det ikke kan afvises |")
    a("|---|---|")
    a("| **Regn regressionen ud.** Iltsvindets årlige udbredelse mod belastningen, vindarbejdet i "
      "lagdelingssæsonen og bundvandets temperatur | "
      + C("C-LE-9-REGRESSION", "udbredelsen og belastningen offentliggøres af DCE, og vindarbejde "
          "og bundvandstemperatur kan regnes ud af de vind- og CTD-data, projektet har. Det kræver "
          "ingen nye målinger, og ingen offentliggjort regression af den slags er fundet i de "
          "kilder, projektet har") + " |")
    a("| **Udfyld nævneren.** "
      + C("C-LE-9-METHODS", "Mindst to af de tomme rækker har etablerede metoder — udsivning af "
          "grundvand under havet med radium som sporstof eller med sivemålere, og intern "
          "frigivelse fra sedimentet med bundkamre") + " | "
      + C("C-LE-9-DENOM", "begge kræver nye målinger. Uden en nævner er der ingen andel af "
          "helheden") + " |")
    a("| **Mål overløbene i hændelser.** Flowproportional prøvetagning på de største bygværker, "
      "over hændelser af forskellig størrelse | "
      + C("C-LE-9-LEVEL5", f"målebaseret overløbsestimering er videnniveau {lv[5]['level']} i "
          f"Miljøstyrelsens egen skala, med {lv[5]['uncertainty_pct']} % usikkerhed på den udledte "
          f"stofmængde mod {lv[1]['uncertainty_pct']} % på niveau {lv[1]['level']}. Metoden er "
          "defineret. Hvor mange bygværker der opgøres sådan, står ikke i noget, projektet har")
      + " |")
    a("| **Finansiér marin ekstraktion som virkemiddel**, med krav om analyse af høsten | "
      + C("C-LE-9-EXTRACT", "det virker på kvælstof, der allerede er i vandet, hvor reduktion på "
          "land kun virker på tilførslen") + " |")
    a("")
    a(C("C-LE-9-KIND", "De tre første er krav om at måle og efterprøve, ikke om et andet svar: "
        "forlang ikke, at tallet ændres — forlang, at det bliver efterprøvet. Det er en stærk "
        "position over for et tal, man mener er forkert.") + "\n")

    a("---\n")
    a("## In English\n")
    a(C("C-LE-EN", "This page argues, in Danish and to a Danish agricultural audience, that the "
        f"chain from the published {PCT:.1f}% figure to the damage it is used to explain has "
        "missing links. The figure is a residual share of one term of an open account "
        f"({n_unq} of {n_all} enumerated nitrogen pathways carry no number). The oxygen part of "
        f"the requirement is a binary trigger that sets a judged {CUT}% cut in total-nitrogen "
        "concentration, converted to a load through each water body's own relation, where "
        "chlorophyll and light attenuation have fitted slopes. And the recent extremes of oxygen "
        f"depletion do not obviously track a land-based supply that DCE put {RED}% lower - though "
        "a comparison of chosen years cannot tell no effect from worse without, and warming works "
        "against the reduction. "
        "The page states that this does not exonerate agriculture, that multiplying unknown "
        "fractions yields an unknown rather than a small one, and that it is not an argument for "
        "inaction. It applies the same scrutiny to the city's own discharges, and ends with four "
        "demands, three of which ask for measurement or a test rather than a different answer.")
      + "\n")
    a("The full audit is in [NITROGEN.md](NITROGEN.md) and [CAUSATION.md](CAUSATION.md); the "
      "argument about what to build instead is in [PROGRAMME.md](PROGRAMME.md).\n")
    a("*" + C("C-LE-NONNATIVE", "Denne side er skrevet af en ikke-modersmålstalende og bør læses "
              "igennem af en dansker, før den citeres.") + "*")
    return "\n".join(o)


if __name__ == "__main__":
    sys.exit(main())
