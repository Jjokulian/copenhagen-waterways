"""How many animals, how fast they turn over, and what that is in nitrogen.

The nitrogen argument is conducted in kilograms per hectare, which is a way of not
saying what the kilograms came out of. This puts the animals back in it, from the
official counts rather than from anyone's rhetoric:

  SVIN     pigs standing, at a moment          Statistics Denmark, quarterly
  ANI5     pigs slaughtered and exported live  annual - the throughput, not the stock
  KVAEG5   cattle standing                     quarterly
  FOLK1A   people                              for the only comparison that matters

The stock and the throughput are different numbers and the difference is the point: a
Danish pig lives about six months, so the population at any instant is a fraction of
the population that passes through in a year. Quoting one for the other - in either
direction - is the commonest mistake in this argument.

Nitrogen is derived, and marked as derived: manure nitrogen per hectare comes from the
field balance in NITROGEN.md (DCE SR120, a norm product), multiplied by the current
agricultural area. Human sewage nitrogen uses a stated per-person convention so the
comparison can be redone with another one.

Writes data/derived/livestock.json.
"""
import csv
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, log, fetch

API = "https://api.statbank.dk/v1/data/{}/CSV?{}&delimiter=Semicolon"
# Stated, not measured. Ordinary design figures for sewage nitrogen per person-year;
# the range is what different sources give, and both ends are carried through.
HUMAN_N_KG_PER_YEAR = (4.4, 5.0)
# From the field balance: manure and sludge, kg N/ha, 2013, DCE SR120 Table 3.4.
MANURE_N_KG_PER_HA = 87
# Stated, and the weakest numbers on this page. The official throughput counts animals
# that reached a slaughterhouse or a lorry; animals that died on the farm are in no
# open series this project has found. Danish sow productivity is high and widely
# reported in this range - liveborn per sow-year, and the share of those that do not
# reach slaughter - so the birth figure is given as a range and never as a number.
LIVEBORN_PER_SOW_YEAR = (38.0, 42.0)
DIED_BEFORE_SLAUGHTER_SHARE = (0.20, 0.25)


def one(table, query):
    raw = fetch(API.format(table, query), timeout=120).decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(raw), delimiter=";"))
    for r in reversed(rows):
        if r and r[-1].replace(",", ".").replace("-", "").replace(".", "").isdigit():
            return float(r[-1].replace(",", ".")), r[-2]
    raise SystemExit(f"{table}: no value in {rows[:2]}")


def main():
    area_ha = json.load(open(os.path.join(DERIVED, "cropland.json"),
                             encoding="utf-8"))["years"]["2025"]["total_ha"]
    pigs_stock, t_pig = one("SVIN", "TYPE=D29&Tid=2026K3")
    sows, _ = one("SVIN", "TYPE=D181&Tid=2026K3")
    pigs_flow, t_flow = one("ANI5", "DYRKAT=SVINIALT&ENHED=SLAGEKS&Tid=2025")
    pig_meat, _ = one("ANI5", "DYRKAT=SVINIALT&ENHED=PROD&Tid=2025")
    cattle, t_cattle = one("KVAEG5", "OMR%C3%85DE=000&DYR=D17&Tid=2026K2")
    people, t_people = one("FOLK1A", "Tid=2026K3")

    manure_kt = MANURE_N_KG_PER_HA * area_ha / 1e6
    human_kt = tuple(people * k / 1e6 for k in HUMAN_N_KG_PER_YEAR)

    # Two independent ways at the same missing number, which is the only reason to
    # quote it at all: sows times liveborn, and slaughtered-plus-exported grossed up
    # for the ones that never got there. If they disagreed badly, neither would be
    # worth printing.
    born_from_sows = tuple(sows * 1000 * k for k in LIVEBORN_PER_SOW_YEAR)
    born_from_flow = tuple(pigs_flow * 1000 / (1 - d)
                           for d in DIED_BEFORE_SLAUGHTER_SHARE)
    died = tuple(b - pigs_flow * 1000 for b in sorted(born_from_flow))

    out = {
        "_what": "Danish livestock as counts, throughput and nitrogen.",
        "_measured": "Counts and production are Statistics Denmark, live API.",
        "_derived": "Manure nitrogen is the SR120 field-balance figure times the "
                    "current agricultural area; human sewage nitrogen uses a stated "
                    "per-person convention. Both are marked in the text.",
        "pigs_standing": pigs_stock * 1000, "pigs_standing_period": t_pig,
        "pigs_through_per_year": pigs_flow * 1000, "pigs_through_period": t_flow,
        # ANI5 reports production in million kg; keep it in the source unit and let
        # the reader of the JSON convert, rather than inventing a second one here.
        "pig_meat_million_kg_per_year": pig_meat,
        "cattle_standing": cattle, "cattle_period": t_cattle,
        "people": people, "people_period": t_people,
        "agricultural_ha": area_ha,
        "manure_n_kg_per_ha_stated": MANURE_N_KG_PER_HA,
        "manure_n_kt_per_year": manure_kt,
        "human_sewage_n_kg_per_person_year_stated": list(HUMAN_N_KG_PER_YEAR),
        "human_sewage_n_kt_per_year": list(human_kt),
        "manure_over_human": manure_kt / human_kt[0],
        "pig_years_per_pig_stated": 0.5,
        "sows_standing": sows * 1000,
        "liveborn_per_sow_year_stated": list(LIVEBORN_PER_SOW_YEAR),
        "died_before_slaughter_share_stated": list(DIED_BEFORE_SLAUGHTER_SHARE),
        "born_per_year_from_sows": list(born_from_sows),
        "born_per_year_from_throughput": list(sorted(born_from_flow)),
        "died_before_slaughter_per_year": list(died),
        "_mortality_note": "Not measured anywhere this project can reach. The "
                           "official series counts animals that arrived at a "
                           "slaughterhouse or on an export lorry; what died on the "
                           "farm leaves as rendering tonnage, and that is the "
                           "series to ask for.",
    }
    p = os.path.join(DERIVED, "livestock.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    log(f"  pigs {pigs_stock*1000:,.0f} standing ({t_pig}), "
        f"{pigs_flow*1000:,.0f} through the system in {t_flow}")
    log(f"  cattle {cattle:,.0f} ({t_cattle}); people {people:,.0f} ({t_people})")
    log(f"  manure N {manure_kt:,.0f} kt/yr vs human sewage N "
        f"{human_kt[0]:,.0f}-{human_kt[1]:,.0f} kt/yr — "
        f"{manure_kt/human_kt[0]:.1f}x")
    log(f"  sows {sows*1000:,.0f}; born/yr {born_from_sows[0]/1e6:.0f}-"
        f"{born_from_sows[1]/1e6:.0f} M from the sow herd, "
        f"{born_from_flow[0]/1e6:.0f}-{born_from_flow[1]/1e6:.0f} M from the "
        f"throughput; died before slaughter {died[0]/1e6:.0f}-{died[1]/1e6:.0f} M")
    log(f"  wrote {p}")


if __name__ == "__main__":
    main()
