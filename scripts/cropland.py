"""What Danish farmland grows, and therefore what the nitrogen on it is for.

The load apportionment has no livestock term - diffuse load is one bucket, and no
measurement in a stream can say whether a nitrate ion came from a bag or from a cow.
So the question *how much of this is because Denmark keeps animals* cannot be answered
downstream at all. It can only be answered on the input side, and there it has two
halves:

  1. **How much of the nitrogen applied is manure.** Already in NITROGEN.md from DCE
     SR120 Table 3.4 - a norm product, counts times regulatory coefficients.
  2. **What the rest of the nitrogen is applied to grow.** That is this script.
     Mineral fertiliser spread on a barley field grown for pigs is nitrogen spent on
     livestock as surely as the slurry beside it.

Source: Statistics Denmark table AFG6 (crop areas, 1982-), fetched live from the open
API. The classification below is **stated, not official** - Denmark's crop statistics
record what was grown, not what it was fed to - so the result is given as a floor and
a ceiling rather than as a number.

Writes data/derived/cropland.json.
"""
import csv
import io
import json
import os
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, log, fetch

API = "https://api.statbank.dk/v1/data/AFG6/CSV"
YEARS = ["1990", "2000", "2010", "2025"]

# The stated rule. Three tiers, because the honest answer is a range.
UNAMBIGUOUS = ["6. Græs og helsæd i omdrift", "9. Græs uden for omdrift",
               "3.3 Foderroer og anden rodfrugt til foder"]
MOSTLY_FEED = ["1. Korn til modenhed", "2. Bælgsæd til modenhed"]
PART_FEED = ["4.1 Raps"]                    # the meal is feed, the oil is not
DIRECT_FOOD = ["3.1 Kartofler", "3.2 Sukkerroer til fabrik", "7. Gartneriafgrøder"]
NEITHER = ["5. Frø til udsæd", "10. Braklægning", "9. Juletræer og pyntegrønt"]
TOTAL = "Landbrug og gartneri i alt"


def year(y):
    q = "AFGR%C3%98DE=*&ENHED=HA&AREAL1=AIALT&delimiter=Semicolon&Tid=" + y
    raw = fetch(API + "?" + q, timeout=120).decode("utf-8-sig")
    v = {}
    for r in csv.DictReader(io.StringIO(raw), delimiter=";"):
        n = (r.get("AFGRØDE") or "").strip()
        s = (r.get("INDHOLD") or "").strip()
        if n and s.lstrip("-").isdigit():
            v[n] = int(s)
    return v


def main():
    out = {
        "_what": "Danish crop area by what the crop is for, on a stated rule.",
        "_source": "Statistics Denmark AFG6, live API",
        "_rule": {
            "unambiguous_feed": UNAMBIGUOUS,
            "mostly_feed_in_denmark": MOSTLY_FEED,
            "part_feed": PART_FEED,
            "direct_human_food": DIRECT_FOOD,
            "neither": NEITHER,
            "_caveat": "Denmark's crop statistics record what was grown, not what it "
                       "was fed to. Cereals are the load-bearing assumption: most "
                       "Danish grain is fed to animals here or abroad, but some is "
                       "milled, malted or exported as grain, and the table cannot "
                       "separate them. Hence a floor and a ceiling.",
        },
        "years": {},
    }
    for y in YEARS:
        v = year(y)
        if TOTAL not in v:
            log(f"  {y}: no total, skipped")
            continue
        tot = v[TOTAL]
        g = lambda keys: sum(v.get(k, 0) for k in keys)
        row = {
            "total_ha": tot,
            "unambiguous_feed_ha": g(UNAMBIGUOUS),
            "mostly_feed_ha": g(MOSTLY_FEED),
            "part_feed_ha": g(PART_FEED),
            "direct_food_ha": g(DIRECT_FOOD),
            "neither_ha": g(NEITHER),
        }
        row["floor_pct"] = row["unambiguous_feed_ha"] / tot * 100
        row["central_pct"] = (row["unambiguous_feed_ha"] + row["mostly_feed_ha"]) / tot * 100
        row["ceiling_pct"] = (row["unambiguous_feed_ha"] + row["mostly_feed_ha"]
                              + row["part_feed_ha"]) / tot * 100
        row["direct_food_pct"] = row["direct_food_ha"] / tot * 100
        out["years"][y] = row
        log(f"  {y}: {tot:,} ha — feed {row['floor_pct']:.1f}% floor, "
            f"{row['central_pct']:.1f}% central, {row['ceiling_pct']:.1f}% ceiling; "
            f"direct human food {row['direct_food_pct']:.1f}%")
    p = os.path.join(DERIVED, "cropland.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    log(f"  wrote {p}")


if __name__ == "__main__":
    main()
