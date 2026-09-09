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
    pigs_flow, t_flow = one("ANI5", "DYRKAT=SVINIALT&ENHED=SLAGEKS&Tid=2025")
    pig_meat, _ = one("ANI5", "DYRKAT=SVINIALT&ENHED=PROD&Tid=2025")
    cattle, t_cattle = one("KVAEG5", "OMR%C3%85DE=000&DYR=D17&Tid=2026K2")
    people, t_people = one("FOLK1A", "Tid=2026K3")

    manure_kt = MANURE_N_KG_PER_HA * area_ha / 1e6
    human_kt = tuple(people * k / 1e6 for k in HUMAN_N_KG_PER_YEAR)

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
    log(f"  wrote {p}")


if __name__ == "__main__":
    main()
