#!/usr/bin/env python3
"""Generate docs/LANDBRUG.md - the audit, addressed to the people it is used against.

Everything else on this site is written for whoever turns up. This page is written for
one audience: farmers and the organisations that represent them, who are being handed a
quantified reduction target justified by a number this project has taken apart.

It is in Danish because the audience is Danish and an English document from an outsider
gets filed under "foreigner with opinions" before it is read.

The document concedes deliberately and early. An argument that admits what it cannot
show is much harder to dismiss than one that claims too much, and the claim being made
here is narrow and strong: not that agriculture is blameless, but that the evidential
chain from the published figure to the imposed measure has three missing links, each of
which is missing in the same direction.

Usage:  python3 scripts/landbrug.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, ROOT, log, read_json

MANUAL = os.path.join(ROOT, "data", "manual")
AGRI_PCT = 69.6
C_PER_COD = 0.375
C_PER_N = (106 * 12.011) / (16 * 14.007)


def main():
    paths = read_json(os.path.join(MANUAL, "nitrogen_pathways.json"))["pathways"]
    mon = read_json(os.path.join(MANUAL, "monitoring.json"))
    tt = mon["typetal_nutrients_mg_per_l"]
    hz = mon["hazardous_substances"]
    ov = mon["overflow_reporting"]

    land = [p for p in paths if p["pathway"].startswith("Danish land via")]
    land_lo = sum(p["lo"] for p in land)
    land_hi = sum(p["hi"] for p in land)
    agri_lo, agri_hi = land_lo * AGRI_PCT / 100, land_hi * AGRI_PCT / 100
    quant = [p for p in paths if p["lo"] is not None]
    unq = [p for p in paths if p["lo"] is None]
    tot_lo = sum(p["lo"] for p in quant)
    tot_hi = sum(p["hi"] for p in quant)
    ceil_hi = agri_hi / tot_lo * 100

    o = []
    a = o.append

    a("# Til landbruget: grundlaget for kravet\n")
    a("> ## Om denne sides p\u00e5stand om koefficienter\n")
    a("> En tidligere version af denne side sagde, at der *ikke findes nogen "
      "koefficient mellem kv\u00e6lstof og nogen \u00f8kologisk effekt*. Det er for bredt, "
      "og det er nu rettet til det, dokumenterne faktisk viser \u2014 en sk\u00e6rpelse, "
      "ikke en tilbagetr\u00e6kning.\n")
    a("> **For klorofyl og lyssv\u00e6kkelse findes der en koefficient.** DCE har "
      "opstillet statistiske relationer, og indsatsbehovet regnes ud af en h\u00e6ldning: "
      "hvor meget indikatoren \u00e6ndrer sig pr. \u00e6ndring i N-tilf\u00f8rsel.\n")
    a("> **For iltsvind findes der ingen.** Iltsvindsindikatoren er en *bin\u00e6r "
      "udl\u00f8ser*. Hvis \u00e9n eller flere iltsvindsindikatorer siger, at vandomr\u00e5det er "
      "ramt, s\u00e6ttes indsatsbehovet til en fast reduktion p\u00e5 **25 %** af den "
      "nuv\u00e6rende TN-koncentration \u2014 uanset hvor slemt iltsvindet er, hvor meget "
      "kv\u00e6lstof der tilf\u00f8res, eller hvordan omr\u00e5det er indrettet. DCE skriver selv, "
      "hvorfor: tallet er valgt, s\u00e5 det er *st\u00f8rre end de normale \u00e5r-til-\u00e5r "
      "variationer*, og \u201ddet **vurderes**, at en 25 % reduktion i TN-koncentrationen "
      "er minimumskrav for at \u00e6ndre systemet\u201d. Det er en fagligt begrundet "
      "tommelfingerregel, ikke en m\u00e5lt d\u00e6mpning. Den kan hverken falsificeres eller "
      "kalibreres, fordi der ingen respons-kurve er bag den.\n")
    a("> Det er iltsvind, der b\u00e6rer den offentlige begrundelse for aftalen. Og "
      "netop der er koefficienten et sk\u00f8n.\n")
    a("*Denne side er skrevet på dansk og henvender sig til landmænd og deres "
      "organisationer. Resten af sitet er på engelsk.* "
      "*[An English summary follows at the bottom.](#in-english)*\n")

    a("> **Hvad dette er, og hvad det ikke er.** Dette er ikke et partsindlæg for "
      "landbruget. Projektet her bruger det meste af sin plads på at tage byens egne "
      "udledninger fra hinanden — regnbetingede overløb, spildevandsplanens huller, "
      "hvad Københavns skybrudsplan faktisk dækker. Det er *samme* metode anvendt på "
      "kvælstoftallet, og resultatet er ubelejligt for flere end landbruget.\n")

    # ---------------------------------------------------------------- 1
    a("## 1. Hvad de 69,6 % faktisk er en andel af\n")
    a(f"Tallet er landbrugets andel af **den landbaserede, vandbårne post alene** — "
      "kvælstof, der når kysten gennem danske vandløb og umålte oplande. Det er to "
      "rækker ud af tyve i den opgørelse, projektet har lavet over alle veje, ad hvilke "
      "reaktivt kvælstof når danske havområder:\n")
    a("| Række | kt N/år | Grundlag |")
    a("|---|---:|---|")
    for p in land:
        st = {"PARTLY MEASURED": "delvist målt", "MODELLED": "modelleret"}.get(
            p["status"], p["status"].lower())
        a(f"| {p['pathway'].replace('Danish land via monitored streams', 'Dansk land via målte vandløb').replace('Danish land via unmonitored catchments', 'Dansk land via umålte oplande')} "
          f"| {p['lo']:.0f} – {p['hi']:.0f} | {st} |")
    a(f"| **Posten, procenten deler** | **{land_lo:.0f} – {land_hi:.0f}** | |")
    a(f"| **69,6 % af den** | **{agri_lo:.0f} – {agri_hi:.0f}** | |")
    a("")
    a(f"De **{len(unq)} af {len(paths)} veje har slet intet tal** — heriblandt "
      "atmosfærisk afsætning af organisk kvælstof, udsivning af grundvand under havet, "
      "og frigivelse fra sedimentet, som efter én undersøgelse leverer størstedelen af "
      "det, den årlige primærproduktion kræver. De veje, der *har* et tal, summerer til "
      f"**{tot_lo:.0f} – {tot_hi:.0f} kt N/år**.\n")
    a("En tom række kan kun lægge til. Nævneren har altså et gulv og intet loft, og "
      "enhver procent regnet mod den er et **loft, ikke et estimat**:\n")
    a(f"> Landbruget står for **højst {ceil_hi:.0f} %** af det opgjorte reaktive "
      "kvælstof, der når danske havområder. Udfyld én af de tomme rækker, og loftet "
      "falder. Det kan ikke stige.\n")
    a("Til sammenligning: **atmosfærisk afsætning direkte på havoverfladen er 45–65 kt "
      "N/år** — på størrelse med hele den landbaserede post — og optræder ikke i nogen "
      "offentliggjort fordeling.\n")

    # ---------------------------------------------------------------- 2
    a("## 2. Tallet er en restpost, ikke en måling\n")
    d = mon["diffuse_load"]
    a("Sådan fremkommer landbrugsandelen: målt-plus-modelleret total, minus modellerede "
      "punktkilder, minus modelleret naturligt baggrundsbidrag. Det, der bliver tilbage, "
      "kaldes landbrug.\n")
    a("| | |")
    a("|---|---|")
    a(f"| Måledækning | {d['area_measured_pct']} % af arealet måles, "
      f"{d['area_modelled_pct']} % modelleres |")
    a("| Målemetode | stikprøver med faste mellemrum, transport beregnet som sum af "
      "daglig vandføring gange lineært interpoleret koncentration |")
    a("| Dokumenteret skævhed | i alle tre vandløb i GUDP-undersøgelsen fra 2018 gav "
      "stikprøver **altid lavere** transport end højfrekvent måling |")
    a(f"| Retentionens usikkerhed | ± {d['retention_uncertainty_national_average_pct_points']} "
      "procentpoint på landsgennemsnittet |")
    a("| Estimatorens opførsel | i tørre år som 1996 og 2005 bliver det beregnede "
      "dyrkningsbidrag **negativt** |")
    a("")
    a("En størrelse, der kan blive negativ, er ikke en måling af en fysisk mængde. Den "
      "er residualet af to modeller, og den arver begges fejl med modsat fortegn.\n")

    # ---------------------------------------------------------------- 3
    a("## 3. Tre led mangler mellem tallet og skaden\n")
    a("Sætningen, der bruges politisk, er ikke *69,6 % af den landbaserede vandbårne "
      "kvælstofpost*. Den er *landbruget står for omkring 70 % af iltsvindet* — eller "
      "af fedtemøget. Mellem de to sætninger ligger tre led:\n")
    a("| Led | Koefficient |")
    a("|---|---|")
    a("| Kvælstof → iltsvind | **findes ikke.** Kvælstof er én af mindst seks iltforbrugende "
      "processer. Der er ingen potensfaktor: et kilo i februar i en opblandet vandsøjle "
      "tæller som et kilo i juli under et springlag |")
    a("| Iltsvind → tab af højere liv | **findes ikke.** Iltsvind er én vej blandt flere — "
      "miljøfremmede stoffer, trawl, turbiditet, svovlbrinte. Bundfaunaen prøvetages "
      "**1. marts – 31. maj**, så efterårets dødelighed ses aldrig |")
    a("| Tab af højere liv → fedtemøg | **findes ikke.** Fedtemøg overvåges ikke "
      "systematisk overhovedet — ikke udbredelse, ikke biomasse, ikke varighed |")
    a("")
    a("Hvert led er en reel årsagssammenhæng. Ingen af dem har et tal. **Et produkt af "
      "tre ukendte brøker er en ukendt brøk** — og det præsenteres som ét målt tal.\n")

    # ---------------------------------------------------------------- 4
    a("## 4. Prøven, der allerede er taget\n")
    tr = mon["load_trend_vs_outcome"]
    ld = tr["nitrogen_load"]
    a(f"Den landbaserede kvælstoftilførsel er faldet fra omkring "
      f"{ld['approx_1990_kt']:,} kt N/år i 1990 til omkring {ld['approx_recent_kt']:,} kt "
      f"— en reduktion på cirka {ld['reduction_pct_since_1990']} %. Luftbåren kvælstof "
      "til danske havområder er faldet tilsvarende. Det er den største miljøindsats i "
      "nyere dansk politik, og den er ikke omstridt.\n")
    a("Imens:\n")
    a("| År | Iltsvindets udbredelse i september |")
    a("|---|---|")
    for r in tr["iltsvind_extent"]["observations"]:
        km = r.get("km2_september") or r.get("km2_late_september")
        a(f"| {r['year']} | {'~' + format(km, ',') + ' km²' if km else '—'} |")
    a("")
    a("**Halvér tilførslen, og yderpunkterne rykker sig ikke.** 2023 og 2024 lå på "
      "niveau med 1989, 2000 og 2002, hvor belastningen var omtrent dobbelt så stor. "
      "Og 2025 kom ind på en tredjedel af 2024 — så udsvinget mellem to på hinanden "
      "følgende år er større end trenden over femogtredive.\n")
    a("Det er ikke bevis for, at kvælstof er ligegyldigt. Det er bevis for, at "
      "**udbredelsen styres af det enkelte års fysik og af havbundens tilstand**, med "
      "belastningen som en langsom baggrund. Ingen af de to ting kan en kildeopgørelse "
      "overhovedet udtrykke, for ingen af dem er en kilde.\n")

    # ---------------------------------------------------------------- 5
    a("## 5. Det, byen slipper for at få talt med\n")
    a("Samme metode på byens egne udledninger, så det er klart, at kritikken ikke kun "
      "peger én vej:\n")
    for t in [
        f"**Overløbsmængder er modellerede**, ikke målte. PULS registrerer antal overløb "
        f"og ingen vandføring. Massen beregnes som modelleret årsvolumen gange et fast "
        f"typetal — og kvalitetskontrolleres ved at tjekke, om koncentrationen ligger "
        f"tæt på det samme typetal. Usikkerheden på volumen er angivet til "
        f"{ov['knowledge_levels'][1]['uncertainty_pct']} % på det laveste videnniveau.",
        f"**Typetallene for miljøfarlige stoffer** hviler på "
        f"{hz['stations_combined_overflow']} målestationer for fællessystem og "
        f"{hz['stations_separate_stormwater']} for separat regnvand, anvendt på "
        f"{hz['applied_to_discharge_points_nationally']:,} udledningspunkter — i oplande "
        f"*valgt* til at repræsentere husholdninger og boligområder, og udtrykkeligt "
        f"afgrænset over for industriområder og stærkt trafikerede veje. Samme rapport "
        f"finder de højeste medianer for metaller i slam fra bassiner.",
        f"**Et fællessystemsoverløb leverer lige så meget organisk kulstof direkte, som "
        f"dets kvælstof kunne nå at producere.** Ved Redfield-forhold svarer "
        f"{tt['combined_overflow']['Tot-N']:.0f} mg N/l til "
        f"{tt['combined_overflow']['Tot-N']*C_PER_N:.0f} mg C/l; vandet bærer selv "
        f"{tt['combined_overflow']['COD']*C_PER_COD:.0f} mg C/l. Kun den ene halvdel "
        f"tælles, og den tælles til 0,6 % af en national kvælstoftotal.",
        "**Fedt indeholder intet kvælstof overhovedet.** Triglycerider er kulstof, "
        "brint og ilt. En kvælstofopgørelse kan ikke undervurdere det materiale — den "
        "kan slet ikke se det. Og det frigives på en flowtærskel, altså netop i de "
        "timer, hvor vandet går uden om renseanlægget.",
    ]:
        a(f"- {t}")
    a("")

    # ---------------------------------------------------------------- 6
    a("## 6. Hvad dette **ikke** viser\n")
    a("Dette afsnit står her, fordi et argument, der indrømmer hvad det ikke kan vise, "
      "er langt sværere at afvise end et, der påstår for meget.\n")
    for t in [
        "**Det viser ikke, at landbruget er uden andel.** At gange ukendte brøker giver "
        "en ukendt, ikke en lille. Landbruget er sandsynligvis stadig den største enkelte "
        "kvælstofkilde, belastningen er reel, og reduktioner har dokumenterede lokale "
        "gevinster.",
        "**Det viser ikke, at kvælstofpolitikken har fejlet.** *Nødvendig* og "
        "*utilstrækkelig* er to forskellige konklusioner, og forløbet siden 1990 er "
        "foreneligt med den anden.",
        "**Og det er ikke et argument for at gøre ingenting.** Det er et argument for at "
        "gøre noget andet — og for at måle det.",
    ]:
        a(f"- {t}")
    a("")
    a("Det, det *viser*, er snævrere og stærkere: **grundlaget for et kvantificeret, "
      "sektorspecifikt mål er ikke til stede.** Der findes ingen nævner, ingen "
      "potensfaktor, og ingen dokumenteret virkning på yderpunkterne efter femogtredive "
      "år. Et fejlspecificeret instrument er ikke kun urimeligt over for den regulerede "
      "— det er farligt for alle, fordi det bliver ved med at kræve mere af det samme, "
      "når det samme ikke virker.\n")

    # ---------------------------------------------------------------- 7
    a("## 7. Hvis begrænsningen er havets evne til at optage, bliver løsningsrummet større\n")
    a("Antag et øjeblik, at skaden ikke er *f(belastning)* men *f(belastning, tilstand)* "
      "— at det samme kilo kvælstof gør mere skade i 2025 end i 1990, fordi ålegræsset, "
      "filtratorerne og en sammenhængende havbund er væk. Så er der to håndtag, ikke ét, "
      "og det andet har hidtil ikke været i spil.\n")
    a("| Virkemiddel | Hvad det gør, som reduktion ikke gør |")
    a("|---|---|")
    a("| **Muslinge- og tangopdræt** | fjerner kvælstof, der **allerede er i vandet**, "
      "og høstes i stedet for at rådne. Det eneste virkemiddel, der arbejder på "
      "lageret frem for på tilførslen |")
    a("| **Ålegræs og bundintegritet** | genopretter optagelsen og stabiliserer "
      "sedimentet, så metaller og svovlbrinte bliver liggende |")
    a("| **Vådområder og efterafgrøder** | de kendte, og de virker — men kun på "
      "tilførslen |")
    a("")
    a("Det afgørende ved marin ekstraktion er, at det **er en produktion**. Muslingemel "
      "og tang er foder. Og foderet er selve miljøydelsen: kvælstoffet fjernes ved, at "
      "biomassen tages op.\n")

    # ---------------------------------------------------------------- 8
    a("## 8. Og dermed et led, der sjældent trækkes\n")
    a("Den bindende omkostning ved at lade et dyr leve længere er foder. Hvis et "
      "kvælstofvirkemiddel *producerer* foder og betales som miljøydelse, så kan den "
      "samme politik finansiere, at dyr lever længere, i stedet for at besætninger "
      "bliver mindre.\n")
    a("Det er ikke en omskrivning. Det er en ændring af, hvad betalingen er knyttet til. "
      "I den nuværende ordning falder dyrets værdi sammen med dets død, og jo tidligere "
      "jo bedre — tyrekalve, lam, orner. **Et foderflow, der betales for at fjerne "
      "kvælstof fra havet, afkobler betalingen fra aflivningen.**\n")
    a("Forbeholdene, som skal med, ellers er det reklame:\n")
    for t in [
        "Ekstraktivt opdræt opkoncentrerer metaller og organiske miljøfremmede stoffer. "
        "Hvor høsten må gå hen, afgøres af analyse, ikke af hensigt — og zink og kobber "
        "er ikke det samme som cadmium og kviksølv, som opkoncentreres op gennem "
        "fødekæden og som intet levende har et evolutionært beredskab over for.",
        "Ekstraktivt opdræt i den nødvendige skala er ikke økonomisk afprøvet. Der er "
        "ikke sket en effektivitetsrevolution endnu — men der er heller ikke gjort "
        "noget alvorligt forsøg.",
        "Og intet af dette fritager nogen. Det udvider listen over, hvad der kan gøres.",
    ]:
        a(f"- {t}")
    a("")

    # ---------------------------------------------------------------- 9
    a("## 9. Hvad man konkret kan forlange\n")
    a("Ikke *drop kravet*. Det er en tabt sag og en dårlig sag. I stedet fire ting, som "
      "alle er billige, og som ingen kan afvise uden at forklare hvorfor:\n")
    a("| Krav | Hvorfor det ikke kan afvises |")
    a("|---|---|")
    a("| **Offentliggør regressionen.** Iltsvindets årlige udbredelse mod "
      "flow-normaliseret belastning, vindarbejde i lagdelingssæsonen og "
      "bundvandstemperatur | alle tre serier er allerede offentliggjort af DCE. Det "
      "kræver ingen nye data, ingen nye målinger og ingen bevilling |")
    a(f"| **Udfyld nævneren.** Mindst de to tomme rækker, der kan måles med "
      "standardmetoder — udsivning af grundvand under havet med radon- og radiumsporing, "
      "og intern frigivelse fra sedimentet med bundkamre | begge er rutine i udlandet. "
      "Uden en nævner er der ingen procent |")
    a("| **Mål overløbene i hændelser.** Flowproportional prøvetagning på de største "
      "bygværker, over hændelser af forskellig størrelse | det er videnniveau 5 i "
      "Miljøstyrelsens egen skala, med 30 % usikkerhed mod 135 %. Metoden er defineret. "
      "Næsten ingen bruger den |")
    a("| **Finansiér marin ekstraktion som virkemiddel**, med krav om analyse af høsten | "
      "det er det eneste virkemiddel, der fjerner kvælstof, som allerede er i vandet |")
    a("")
    a("De tre første er krav om *måling*. Det er den stærkeste position, man kan indtage "
      "over for et tal, man mener er forkert: forlang ikke, at det ændres — forlang, at "
      "det bliver efterprøvet.\n")

    a("---\n")
    a("## In English\n")
    a("This page argues, in Danish and to a Danish agricultural audience, that the "
      "evidential chain from the published 69.6% figure to a quantified sector-specific "
      "reduction target has three missing links: there is no closed denominator (10 of "
      "20 enumerated nitrogen pathways carry no number), no dose-response behind the "
      "oxygen requirement — which is a binary trigger and a judged flat 25%, where "
      "chlorophyll and light attenuation do have fitted coefficients — and no "
      "detectable movement in the extremes after a "
      "35-year halving of the load. It states explicitly that this does not exonerate "
      "agriculture, that multiplying unknown fractions yields an unknown rather than a "
      "small one, and that it is not an argument for inaction. It applies the same "
      "scrutiny to urban discharge, where the numbers are worse. And it ends with four "
      "demands, three of which are demands for measurement rather than for a different "
      "answer.\n")
    a("The full audit is in [NITROGEN.md](#NITROGEN.md) and "
      "[CAUSATION.md](#CAUSATION.md); the argument about what to build instead is in "
      "[PROGRAMME.md](#PROGRAMME.md).\n")
    a("*Denne side er skrevet af en ikke-modersmålstalende og bør læses igennem af en "
      "dansker, før den citeres.*")

    path = os.path.join(ROOT, "docs", "LANDBRUG.md")
    text = "\n".join(o)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    log(f"wrote docs/LANDBRUG.md ({len(text):,} chars)")
    log(f"  ceiling on agriculture's share: {ceil_hi:.0f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
