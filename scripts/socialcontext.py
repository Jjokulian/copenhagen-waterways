"""Who carries the nitrogen requirement, and who has no buffer left.

LANDBRUG.md argues about the *scientific basis* of the
requirement and NITROGEN.md section 2c works out the manure arithmetic. Neither asks
the question this script asks, which is the economic one: **given** that the
requirement exists and is now law, whose farm does it land on?

The answer is not uniform, and the interesting part is where it concentrates. Two
levels:

  1. Which *kinds* of farming - by enterprise type, stocking density, region, scale,
     organic status, tenure and debt structure.
  2. Which individual *profiles* run out of buffer - equity ratio, debt structure,
     biological assets, margin - as anonymised cohorts and distributions.

**The individual level is published as distributions only.** Danish sole
proprietorships (`Enkeltmandsvirksomhed`) are natural persons; naming holdings that a
model says will fail is a financial prediction about private individuals. The
registers underneath are public and a farmer can locate their own holding in the
distribution, but this page names none of them, and this script writes no identifying
field into its output.

Sources, all open, all read from the sibling project's fetched copies rather than
re-fetched here (the CVR account fetch is 1,630 XBRL documents and is not worth
repeating; the registers are the same primary sources documented in
`danish-livestock/docs/data-sources.md`):

  cvr_financials.json  filed annual accounts, per CVR, per financial year
  chr_2024.json        every livestock site: business, species, animal units, kommune
  land_by_cvr.json     declared field-parcel hectares per business, Marker 2025
  cvr_raw.jsonl        CVR master data: legal form, industry code, kommune
  kommuner.json        kommune -> region

Set DANISH_LIVESTOCK to that project's data directory if it is not `../danish-livestock/data`.

Peak memory depends on the number of livestock sites (57,860 dicts, held while
folding) plus one dict per CVR in each of five registers - about 27,000 entries at the
widest. `cvr_raw.jsonl` is 30 MB and is streamed a line at a time, keeping four fields
per business rather than the whole record; that is the difference between 30 MB and
about 3.

Writes docs/INCIDENCE.md and data/derived/socialcontext.json.
"""
import collections
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, ROOT, log

SIBLING = os.environ.get(
    "DANISH_LIVESTOCK",
    os.path.join(os.path.dirname(ROOT), "danish-livestock", "data"))

OUT_MD = os.path.join(ROOT, "docs", "INCIDENCE.md")
OUT_JSON = os.path.join(DERIVED, "socialcontext.json")

# Animal units per hectare, at four lines.
#
# 1.4 and 1.7 are the pre-2017 harmony limits, kept for continuity with NITROGEN.md and
# scripts/manure.py. They are HISTORIC: the word `dyreenhed` does not occur once in
# BEK 931/2024 (harmony), BEK 673/2026 (catch crops) or BEK 677/2026 (targeted catch
# crops) - checked against the texts, not assumed.
#
# 0.3 and 0.8 are indicative positions of the two thresholds the current rules DO turn
# on: 30 and 80 kg nitrogen per hectare harmoniareal in manure and other organic
# fertiliser (BEK 673/2026 section 4 subsections 3 and 4). The conversion used is
# 100 kg N per animal unit, which is the figure the pre-2017 unit was built on - the
# correspondence 1.4 DE/ha = 140 and 1.7 = 170 against the current 170 kg N/ha ceiling
# is the reason to believe it. **It is a stated conversion and it is not verified
# here**, and harmoniareal is not the same area as declared parcels, so these two lines
# locate the thresholds rather than test them.
REG_THRESHOLDS = (0.3, 0.8)          # the two current thresholds, located
HISTORIC_LIMITS = (1.4, 1.7, 2.3)    # the pre-2017 harmony ceilings, for continuity
LIMITS = REG_THRESHOLDS + HISTORIC_LIMITS

# Primary agriculture in the Danish NACE (DB07). 016xxx is *support* activities -
# contractors and hoof trimmers - and 682040 is property letting; both appear in the
# accounts set because the business happens to hold a livestock site, and both would
# drag every average if left in.
FARM_NACE = ("011", "012", "013", "014", "015")


def sib(name):
    p = os.path.join(SIBLING, name)
    if not os.path.exists(p):
        raise SystemExit(
            f"missing {p}\n"
            "This page is computed from the sibling project danish-livestock's fetched\n"
            "registers. Clone it beside this repo and run its fetch scripts, or point\n"
            "DANISH_LIVESTOCK at its data directory.")
    return p


def load(name):
    with open(sib(name), encoding="utf-8") as f:
        return json.load(f)


def q(v, p):
    """Exact percentile of a list, by position. Nan on empty rather than a raise,
    because several cohorts here are legitimately empty and the table says so."""
    if not v:
        return float("nan")
    v = sorted(v)
    return v[min(len(v) - 1, int(len(v) * p))]


def share(n, d):
    return 100.0 * n / d if d else float("nan")


# ---------------------------------------------------------------- the registers


def read_registers():
    """Everything the page needs, keyed on CVR, in one pass over each source."""
    de = collections.defaultdict(float)                       # animal units
    spec = collections.defaultdict(lambda: collections.defaultdict(float))
    virk = collections.defaultdict(lambda: collections.defaultdict(float))
    home = collections.defaultdict(collections.Counter)       # kommune, DE-weighted
    sites = 0
    for s in load("chr_2024.json"):
        sites += 1
        c = (s.get("CVRNR") or "").strip()
        if not c or c == "0":
            continue
        d = s.get("DE") or 0.0
        de[c] += d
        spec[c][s.get("DYRTEKST")] += d
        virk[c][s.get("VIRKART")] += d
        home[c][s.get("Kommune")] += d

    land = {}                                                 # cvr -> (ha, parcels, top crop)
    for c, v in load("land_by_cvr.json").items():
        land[c] = (float(v[0]), int(v[1]), v[2])

    # 30 MB of JSON lines, four fields kept per business.
    meta = {}
    with open(sib("cvr_raw.jsonl"), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if not r.get("ok"):
                continue
            d = r["d"]
            meta[str(r["cvr"])] = (d.get("form"), d.get("industrycode") or "",
                                   d.get("kommune"), (d.get("accounts") or 0) > 0)

    region = {}
    for feat in load("kommuner.json")["features"]:
        p = feat["properties"]
        region[p["navn"]] = p["region"]
    # Bornholm is its own region in the national division and is named as a
    # Regionskommune in the kommune layer, so it has no `region` row to join to.
    region.setdefault("Bornholms Regionskommune", "Region Hovedstaden")

    fin = load("cvr_financials.json")
    return de, spec, virk, home, land, meta, region, fin, sites


def enterprise_type(c, spec, virk):
    """Enterprise type from the physical herd, not from the industry code.

    The industry code is what the business registered itself as, sometimes decades
    ago; the animal units are what stands in the sheds on 1 June. Where they disagree
    the herd is the better guide to what a nitrogen rule does to the business. Dairy
    is separated from other cattle by the CHR's own `VIRKART` - the register marks a
    Malkekvaegsbesaetning as such - rather than by a guess from herd composition.
    """
    m = spec.get(c, {})
    t = sum(m.values())
    if t <= 0:
        return "no animal units"
    cattle = m.get("Kvæg", 0.0)
    pigs = m.get("Svin", 0.0)
    fowl = sum(v for k, v in m.items()
               if k and ("Høns" in k or k in ("Kalkuner", "Ænder", "Gæs")))
    if cattle / t >= 0.7:
        vm = virk.get(c, {})
        milk = sum(v for k, v in vm.items() if k and "alkekvæg" in k)
        return "dairy" if milk > cattle * 0.5 else "beef / other cattle"
    if pigs / t >= 0.7:
        return "pigs"
    if fowl / t >= 0.7:
        return "poultry"
    return "other / mixed livestock"


def organic_share(c, virk):
    """Share of a holding's animal units on herds the CHR marks as organic.

    This is the register's own flag on the *herd*, not a certification of the land, so
    it undercounts: a conventional herd on organically farmed land is invisible here,
    and so is an organic arable holding with no animals at all.
    """
    vm = virk.get(c, {})
    t = sum(vm.values())
    if t <= 0:
        return None
    return sum(v for k, v in vm.items() if k and k.startswith("Økologisk")) / t


# Danish crop names as the field-parcel register spells them, glossed on first use
# because this project has bilingual readers and the register has no English.
CROP_EN = {
    "Vinterhvede": "winter wheat",
    "Vårbyg": "spring barley",
    "Vårhavre": "spring oats",
    "Vinterhybridrug": "winter hybrid rye",
    "Vinterraps": "winter oilseed rape",
    "Vinterbyg": "winter barley",
    "Majshelsæd": "whole-crop maize",
    "Majshelsæd med græsudlæg": "whole-crop maize, grass undersown",
    "Græs med kløver/lucerne, under 50 % bælgpl. (omdrift)":
        "grass with clover or lucerne, under 50% legume, in rotation",
    "Permanent græs, normalt udbytte": "permanent grass, normal yield",
    "Miljøtilsagn græs (0 N), permanent":
        "permanent grass under an environmental commitment, zero nitrogen",
    "Miljøtilsagn, ej udtagning, ej landbrugsareal":
        "environmental commitment, not set-aside, not agricultural area",
    "Kartofler, stivelses-": "starch potatoes",
    "Silomajs": "silage maize",
}


# BEK 673/2026 Bilag 1 lists the crops that count into the efterafgrodegrundareal -
# the base area the catch-crop percentages are charged against: cereals spring and
# winter, rape, MAIZE, rybs, soya, mustard, peas, field beans, sunflower, oil flax, and
# other annual crops with no autumn nitrogen uptake in the harvest year. **Grass is not
# on the list and maize is**, which is the opposite of the usual summary and matters a
# great deal for cattle.
BASE_IN = ("hvede", "byg", "havre", "rug", "triticale", "majs", "raps", "rybs",
           "soja", "sennep", "ært", "hestebønne", "solsikke", "oliehør", "lupin",
           "boghvede", "spelt")
BASE_OUT = ("græs", "brak", "skov", "juletræ", "pyntegrønt", "pil", "poppel",
            "miljøtiltag", "miljøtilsagn, ej", "permanent", "udtagning", "eng",
            "natur", "vildt", "blomst", "rekreativ", "lucerne", "kløver")


def crop_base(name):
    """Whether a crop counts into the catch-crop base area.

    Matched on the register's crop name, which is a keyword rule and not the statute's
    own list, so a third bucket is kept for what the rule cannot place - mostly root
    crops and horticulture, about 3% of the declared area. The rule is applied to the
    *largest* declared crop of a business, because that is all the summary register
    carries, so it is a proxy: a holding whose largest crop is grass may still have
    cereal area, and this will overstate both ends.
    """
    c = (name or "").lower()
    for w in BASE_OUT:
        if w in c:
            return "outside"
    for w in BASE_IN:
        if w in c:
            return "in base"
    return "unclassified"


def crop_en(name):
    en = CROP_EN.get(name)
    return f"{name} — *{en}*" if en else name


# BEK 677 of 21 July 2026, Bilag 1: the mandatory targeted catch-crop requirement for
# planning year 2026/2027, as a percentage of the base area, per coastal catchment.
# Transcribed from the regulation text; twenty catchments carry a requirement and the
# rest carry none. Kept here as a literal because it IS the published allocation and a
# reader should be able to check it against the source without running anything.
BEK677_BILAG1 = [
    (29, "Kalundborg Fjord", 34.5), (36, "Dybsø Fjord", 18.3),
    (48, "Stege Bugt", 18.9), (72, "Kløven", 34.5),
    (82, "Aborg Minde Nor", 34.0), (85, "Kertinge Nor", 18.7),
    (87, "Helnæs Bugt", 34.5), (96, "Storebælt, NV", 24.6),
    (101, "Genner Bugt", 30.1), (103, "Als Fjord", 23.1),
    (105, "Augustenborg Fjord", 16.3), (107, "Juvre Dyb", 16.7),
    (109, "Hejlsminde Nor", 21.0), (120, "Knudedyb", 18.4),
    (124, "Kolding Fjord, indre", 14.8), (127, "Horsens Fjord, ydre", 25.3),
    (136, "Randers Fjord, indre", 24.4),
    (204, "Jammerland Bugt og Musholm Bugt", 21.3),
    (233, "Kås Bredning og Venø Bugt", 34.5), (234, "Løgstør Bredning", 25.3),
]

# NUAR Tabel 7.5: change in DB2 (gross margin) in kroner per hectare against the
# reference regulation, by enterprise type, for the Hjarbaek Fjord catchment, under six
# quota-allocation models. Transcribed from the report. This is the only published
# by-farm-type cost estimate for the discharge-based model this project has read in the
# primary source, and it is one catchment - the report says the pattern repeats in the
# other ten, and its Bilag 5 carries those tables.
NUAR_T75 = [
    ("Organic", 341, 523, 497, 506, 350, 435),
    ("Cattle", -994, -1122, -1149, -1129, -969, -1207),
    ("Specialised arable", -327, -476, -678, -554, -393, -552),
    ("Pigs and arable", -438, -489, -606, -546, -472, -603),
    ("Small / non-specialised", -434, -564, -548, -528, -437, -577),
    ("Extensified", 80, 86, 247, 140, 130, 129),
    ("Weighted mean", -460, -541, -586, -552, -468, -605),
]
NUAR_MODELS = ("Flad", "Rodz", "Brak", "Visa", "Visu", "Visu2")

# BEK 130 of 23 January 2026 section 18: the one-off payment per hectare for PERMANENT
# extensification, for the whole commitment period. Read from the regulation. The first
# pair applies where at least half the field is carbon-rich soil, or lies in an area of
# large nitrogen need with wetland potential; the second pair everywhere else. Within
# each pair the higher rate is for land that was in rotation and the lower for the crop
# codes in Annex 2, which is grass.
EXTENSIFICATION_KR_HA = {
    "rotation land, priority area": 82500,
    "grass, priority area": 35500,
    "rotation land, elsewhere": 59500,
    "grass, elsewhere": 27000,
}

TYPE_ORDER = ["dairy", "pigs", "beef / other cattle", "poultry",
              "other / mixed livestock", "no animal units"]


def order(d):
    return [t for t in TYPE_ORDER if t in d] + \
           [t for t in d if t not in TYPE_ORDER]


# ---------------------------------------------------------------- level 1: kinds


def by_type(de, spec, virk, land):
    """Stocking pressure per enterprise type, over every business with animals."""
    rows = {}
    total_de = sum(de.values())
    for c, d in de.items():
        if d <= 0:
            continue
        t = enterprise_type(c, spec, virk)
        r = rows.setdefault(t, {"n": 0, "de": 0.0, "ratios": [], "ha": 0.0,
                                "surplus": 0.0, "n_surplus": 0,
                                "landless_de": 0.0, "n_landless": 0})
        r["n"] += 1
        r["de"] += d
        ha = land.get(c, (0.0,))[0]
        if ha > 1:
            r["ha"] += ha
            r["ratios"].append(d / ha)
            s = d - LIMITS[0] * ha
            if s > 0:
                r["surplus"] += s
                r["n_surplus"] += 1
        else:
            r["landless_de"] += d
            r["n_landless"] += 1
    for t, r in rows.items():
        v = r["ratios"]
        r["n_ratio"] = len(v)
        r["med"] = q(v, 0.5)
        r["p90"] = q(v, 0.9)
        r["over"] = {str(l): share(sum(1 for x in v if x > l), len(v)) for l in LIMITS}
        r["share_de"] = share(r["de"], total_de)
    return rows, total_de


def by_place(de, home, land, region):
    """Where the density sits. The holding is placed at the kommune holding most of
    its animal units, which is not the same as the kommune holding most of its land -
    a distinction that matters for the few businesses that straddle a boundary and
    not at all for the median one."""
    reg = {}
    kom = {}
    unplaced = 0
    for c, d in de.items():
        if d <= 0:
            continue
        k = home[c].most_common(1)[0][0]
        r = region.get(k)
        if r is None:
            unplaced += 1
            continue
        ha = land.get(c, (0.0,))[0]
        for tgt, key in ((reg, r), (kom, k)):
            e = tgt.setdefault(key, {"n": 0, "de": 0.0, "ratios": [], "region": r})
            e["n"] += 1
            e["de"] += d
            if ha > 1:
                e["ratios"].append(d / ha)
    for tgt in (reg, kom):
        for e in tgt.values():
            v = e["ratios"]
            e["n_ratio"] = len(v)
            e["med"] = q(v, 0.5)
            e["over14"] = share(sum(1 for x in v if x > 1.4), len(v))
            del e["ratios"]
    return reg, kom, unplaced


def organic_split(de, spec, virk, land):
    """Cattle only, because the CHR's organic flag is a herd flag and cattle is where
    both a large organic sector and a binding density exist."""
    out = {}
    for c, d in de.items():
        if d <= 0:
            continue
        m = spec.get(c, {})
        if m.get("Kvæg", 0.0) / d < 0.7:
            continue
        vm = virk.get(c, {})
        milk = sum(v for k, v in vm.items() if k and "alkekvæg" in k)
        kind = "dairy" if milk > d * 0.5 else "beef / other cattle"
        o = organic_share(c, virk) or 0.0
        key = (kind, "organic" if o > 0.5 else "conventional")
        e = out.setdefault(key, {"n": 0, "de": 0.0, "ratios": []})
        e["n"] += 1
        e["de"] += d
        ha = land.get(c, (0.0,))[0]
        if ha > 1:
            e["ratios"].append(d / ha)
    for e in out.values():
        v = e["ratios"]
        e["n_ratio"] = len(v)
        e["med"] = q(v, 0.5)
        e["over14"] = share(sum(1 for x in v if x > 1.4), len(v))
        e["mean_de"] = e["de"] / e["n"]
        del e["ratios"]
    return out


def hectare_incidence(land, de, spec, virk, meta):
    """The same question asked of land rather than of animals, because a per-hectare
    allowance falls on hectares. Half of them turn out to have no animals over them."""
    total = sum(v[0] for v in land.values())
    byt = collections.defaultdict(lambda: {"n": 0, "ha": 0.0})
    byform = collections.defaultdict(lambda: {"n": 0, "ha": 0.0})
    byacc = collections.defaultdict(lambda: {"n": 0, "ha": 0.0})
    base = collections.defaultdict(lambda: collections.Counter())
    base_n = collections.defaultdict(lambda: collections.Counter())
    crops = collections.Counter()
    for c, (ha, _, crop) in land.items():
        t = enterprise_type(c, spec, virk) if de.get(c, 0.0) > 0 else "no animal units"
        base[t][crop_base(crop)] += ha
        base_n[t][crop_base(crop)] += 1
        byt[t]["n"] += 1
        byt[t]["ha"] += ha
        form, _ic, _k, acc = meta.get(c, (None, "", None, False))
        f = form or "(not in the CVR extract)"
        byform[f]["n"] += 1
        byform[f]["ha"] += ha
        byacc[acc]["n"] += 1
        byacc[acc]["ha"] += ha
        crops[crop] += ha
    sizes = sorted(v[0] for v in land.values())
    half, cum = None, 0.0
    for i, h in enumerate(reversed(sizes)):
        cum += h
        if cum >= total * 0.5:
            half = i + 1
            break
    return {"total_ha": total, "n_cvr": len(land), "by_type": dict(byt),
            "base": {t: dict(c) for t, c in base.items()},
            "base_n": {t: dict(c) for t, c in base_n.items()},
            "by_form": dict(byform), "by_accounts": {str(k): v for k, v in byacc.items()},
            "top_crops": crops.most_common(10),
            "median_ha": q(sizes, 0.5), "p90_ha": q(sizes, 0.9), "p99_ha": q(sizes, 0.99),
            "cvrs_holding_half_the_land": half}


def visibility(de, land, meta):
    """Who publishes a balance sheet at all. This is the sample frame for everything
    in level 2, and it is not a sample of Danish farming - it is the incorporated
    end of it."""
    total_de = sum(de.values())
    forms = collections.defaultdict(lambda: {"n": 0, "de": 0.0})
    acc = collections.defaultdict(lambda: {"n": 0, "de": 0.0})
    for c, d in de.items():
        form, _ic, _k, has = meta.get(c, (None, "", None, False))
        f = form or "(not in the CVR extract)"
        forms[f]["n"] += 1
        forms[f]["de"] += d
        acc[has]["n"] += 1
        acc[has]["de"] += d
    herd = sorted((x for x in de.values() if x > 0), reverse=True)
    T = sum(herd)
    conc, cum = {}, 0.0
    for i, x in enumerate(herd):
        cum += x
        for m in (0.25, 0.5, 0.75, 0.9):
            if cum >= T * m and (cum - x) < T * m:
                conc[str(m)] = {"holdings": i + 1, "pct_of_holdings": share(i + 1, len(herd))}
    return {"total_de": total_de, "n_animal_cvr": len(de),
            "by_form": dict(forms), "by_accounts": {str(k): v for k, v in acc.items()},
            "n_with_herd": len(herd), "median_de": q(herd, 0.5),
            "p90_de": q(herd, 0.9), "p99_de": q(herd, 0.99),
            "concentration": conc}


# ------------------------------------------------------------ level 2: balance sheets

# Traps in the filed accounts, each of which was found by checking rather than assumed:
#
#   `gross` is GrossResult / GrossProfitLoss - *bruttofortjeneste*, gross profit after
#   variable costs, NOT turnover. `Revenue` is a separate tag and is present on 5% of
#   filings, because a Danish class B company may omit it. So there is no turnover
#   column here and no margin-on-sales can be computed. Anything called a margin below
#   is per hectare or per animal unit, never per krone of sales.
#
#   A missing `lt_debt` is not a missing number, it is a zero - checked, not assumed:
#   where the tag is present the balance sheet identity closes to a median residual of
#   1.5% of assets, and where it is absent equity + short-term debt already reaches
#   assets to a median residual of 0.0%. 8.2% of the absent cases leave more than 5%
#   unexplained and those are wrong in the direction of understating leverage.
#
#   Periods are not all twelve months: 136 of 4,805 filings run from 2 to 18 months.
#   Stocks (equity, assets) survive that; flows (profit, EBIT) do not, so every flow
#   here is taken from a filing of 330-400 days and the rest are dropped.


def latest_full_year(recs):
    ok = [r for r in recs
          if 330 <= (datetime.date.fromisoformat(r["end"])
                     - datetime.date.fromisoformat(r["start"])).days <= 400]
    return max(ok, key=lambda r: r["end"]) if ok else None


def full_years(recs):
    ok = [r for r in recs
          if 330 <= (datetime.date.fromisoformat(r["end"])
                     - datetime.date.fromisoformat(r["start"])).days <= 400]
    return sorted(ok, key=lambda r: r["end"])


def balance_sheet_check(fin):
    """The check behind the comment above, recomputed rather than remembered."""
    both, absent = [], []
    for c, recs in fin.items():
        r = latest_full_year(recs)
        if not r or "assets" not in r or "equity" not in r or "st_debt" not in r:
            continue
        A = r["assets"]
        if A <= 0:
            continue
        if "lt_debt" in r:
            both.append((A - r["equity"] - r["lt_debt"] - r["st_debt"]) / A)
        else:
            absent.append((A - r["equity"] - r["st_debt"]) / A)
    out = {}
    for name, v in (("lt_debt present", both), ("lt_debt absent", absent)):
        out[name] = {"n": len(v), "median_residual": q(v, 0.5),
                     "pct_over_5pct": share(sum(1 for x in v if x > 0.05), len(v))}
    return out


def build_sample(fin, de, spec, virk, land, meta):
    """One row per business with a filed twelve-month balance sheet, restricted to
    primary agriculture. No identifying field is carried past this function."""
    rows, excluded = [], collections.Counter()
    for c, recs in fin.items():
        form, ic, _k, _a = meta.get(c, (None, "", None, False))
        if ic[:3] not in FARM_NACE:
            excluded["not primary agriculture (NACE)"] += 1
            continue
        r = latest_full_year(recs)
        if not r:
            excluded["no twelve-month filing"] += 1
            continue
        if "assets" not in r or "equity" not in r or r["assets"] <= 0:
            excluded["no usable balance sheet"] += 1
            continue
        ha = land.get(c, (0.0,))[0]
        d = de.get(c, 0.0)
        lt, st = r.get("lt_debt"), r.get("st_debt")
        debt = (lt or 0) + (st or 0)
        years = full_years(recs)
        rows.append({
            "type": enterprise_type(c, spec, virk),
            "form": form,
            "de": d, "ha": ha,
            "density": (d / ha) if (ha > 1 and d > 0) else None,
            "assets": r["assets"], "equity": r["equity"],
            "equity_ratio": r["equity"] / r["assets"],
            "profit": r.get("profit"), "ebit": r.get("ebit"),
            "gross": r.get("gross"),
            "biological": r.get("biological"),
            "lt": lt, "st": st, "debt": debt,
            "debt_ratio": debt / r["assets"],
            "n_filings": len(years),
            "equity_ratio_first": (years[0]["equity"] / years[0]["assets"])
                if (len(years) >= 3 and years[0].get("assets", 0) > 0
                    and "equity" in years[0]) else None,
            "profit_3y": sum(y["profit"] for y in years if "profit" in y)
                if len(years) >= 3 and all("profit" in y for y in years) else None,
        })
    return rows, excluded


def cohort_stats(rows):
    """Buffer indicators per enterprise type. Medians throughout, because one holding
    in this sample has an equity ratio of -39 and a mean would be its opinion."""
    out = {}
    for t in set(r["type"] for r in rows):
        v = [r for r in rows if r["type"] == t]
        eq = [r["equity_ratio"] for r in v]
        dens = [r["density"] for r in v if r["density"] is not None]
        prof = [r["profit"] for r in v if r["profit"] is not None]
        mh = [r["profit"] / r["ha"] for r in v if r["profit"] is not None and r["ha"] > 1]
        bio = [r["biological"] / r["assets"] for r in v if r["biological"] is not None]
        # Only where both debt tags are filed: see the worked example in the page.
        stsh = [r["st"] / (r["lt"] + r["st"]) for r in v
                if r["lt"] is not None and r["st"] is not None and (r["lt"] + r["st"]) > 0]
        traj = [r["equity_ratio"] - r["equity_ratio_first"] for r in v
                if r["equity_ratio_first"] is not None]
        p3 = [r["profit_3y"] for r in v if r["profit_3y"] is not None]
        out[t] = {
            "n": len(v),
            "median_de": q([r["de"] for r in v], 0.5),
            "median_assets": q([r["assets"] for r in v], 0.5),
            "median_equity_ratio": q(eq, 0.5),
            "pct_negative_equity": share(sum(1 for r in v if r["equity"] < 0), len(v)),
            "pct_loss": share(sum(1 for x in prof if x < 0), len(prof)),
            "n_profit": len(prof),
            "median_density": q(dens, 0.5), "n_density": len(dens),
            "median_profit_per_ha": q(mh, 0.5), "n_profit_per_ha": len(mh),
            "median_debt_ratio": q([r["debt_ratio"] for r in v], 0.5),
            "median_biological_share": q(bio, 0.5), "n_biological": len(bio),
            "median_st_share": q(stsh, 0.5), "n_st_share": len(stsh),
            "median_equity_trajectory": q(traj, 0.5), "n_trajectory": len(traj),
            "pct_trajectory_falling": share(sum(1 for x in traj if x < 0), len(traj)),
            "median_profit_3y": q(p3, 0.5), "n_profit_3y": len(p3),
            "pct_profit_3y_negative": share(sum(1 for x in p3 if x < 0), len(p3)),
        }
    return out


SHOCK_HA = (0, 500, 1000, 2000, 3000, 5000, 8000)
SHOCK_DE = (0, 250, 500, 1000, 2000, 4000)


def shock_ladder(rows):
    """How large an annual loss of margin, per hectare, takes each cohort into a loss.

    This is deliberately not a cost estimate. Nobody has published a per-hectare cost
    of the quota that this project has been able to verify, so the page states the
    *buffer* instead and lets the reader apply whatever cost they believe. A holding
    is counted as pushed into a loss when its last filed twelve-month profit, minus
    the shock times its declared hectares, is below zero.
    """
    out = {}
    for t in set(r["type"] for r in rows):
        v = [r for r in rows if r["type"] == t and r["ha"] > 1
             and r["profit"] is not None]
        if not v:
            continue
        be = [r["profit"] / r["ha"] for r in v]
        out[t] = {
            "n": len(v),
            "break_even_p25": q(be, 0.25),
            "break_even_median": q(be, 0.5),
            "break_even_p75": q(be, 0.75),
            "ladder": {str(s): share(sum(1 for r in v if r["profit"] - s * r["ha"] < 0),
                                     len(v)) for s in SHOCK_HA},
        }
    return out


def shock_ladder_de(rows):
    """The same test charged per animal unit rather than per hectare.

    It exists because the per-hectare ladder silently drops every landless holding -
    it has no hectares to multiply - and those are precisely the holdings section 3
    identifies as where a tightening allowance actually lands, through the price of a
    slurry placement contract rather than through an allowance of their own. Charging
    per animal unit puts them back in.
    """
    out = {}
    for t in set(r["type"] for r in rows):
        v = [r for r in rows if r["type"] == t and r["de"] > 0 and r["profit"] is not None]
        if not v:
            continue
        landless = [r for r in v if r["ha"] <= 1]
        be = [r["profit"] / r["de"] for r in v]
        out[t] = {
            "n": len(v),
            "n_landless": len(landless),
            "break_even_median": q(be, 0.5),
            "break_even_median_landless": q([r["profit"] / r["de"] for r in landless], 0.5),
            "ladder": {str(s): share(sum(1 for r in v if r["profit"] - s * r["de"] < 0),
                                     len(v)) for s in SHOCK_DE},
            "ladder_landless": {
                str(s): share(sum(1 for r in landless if r["profit"] - s * r["de"] < 0),
                              len(landless)) for s in SHOCK_DE},
            "n_with_land": len(v) - len(landless),
            "pct_loss_landless": share(sum(1 for r in landless if r["profit"] < 0),
                                       len(landless)),
            "pct_loss_with_land": share(
                sum(1 for r in v if r["ha"] > 1 and r["profit"] < 0),
                len(v) - len(landless)),
        }
    return out


def intersection(rows, line=0.8):
    """Exposed to the manure constraint *and* thin on equity.

    `line` is the indicative animal-unit position of the 80 kg N/ha threshold at which
    three of the four requirements step up - not the old 1.4 harmony figure, which has
    no legal force. A landless holding counts as exposed regardless, because it has no
    base area of its own and its whole position is a placement contract.
    """
    def exposed(r):
        return (r["density"] is not None and r["density"] >= line) or r["ha"] <= 1
    cells = collections.defaultdict(collections.Counter)
    for r in rows:
        cells[r["type"]][(exposed(r), r["equity_ratio"] < 0.20)] += 1
    both = [r for r in rows if exposed(r) and r["equity_ratio"] < 0.20]
    yte = [r["equity"] / (-r["profit"]) for r in both
           if r["equity"] > 0 and r["profit"] is not None and r["profit"] < 0]
    return {
        "line": line,
        "by_type": {t: {str(k): n for k, n in c.items()} for t, c in cells.items()},
        "n_both": len(both), "n_rows": len(rows),
        "de_held": sum(r["de"] for r in both),
        "median_de": q([r["de"] for r in both], 0.5),
        "median_equity_ratio": q([r["equity_ratio"] for r in both], 0.5),
        "n_loss": sum(1 for r in both if r["profit"] is not None and r["profit"] < 0),
        "n_negative_equity": sum(1 for r in both if r["equity"] < 0),
        "median_years_of_equity": q(yte, 0.5), "n_years_of_equity": len(yte),
    }


def st_share_artefact(rows):
    """The worked example of a plausible-but-wrong number.

    Treating an absent `lt_debt` tag as a zero when computing the *composition* of
    debt - rather than its level - forces the short-term share to 100% for every
    holding that did not file the tag, and those are not evenly spread across types.
    Both figures are computed so the page can show the size of the error.
    """
    out = {}
    for t in set(r["type"] for r in rows):
        v = [r for r in rows if r["type"] == t and r["st"] is not None and r["debt"] > 0]
        strict = [r for r in v if r["lt"] is not None and (r["lt"] + r["st"]) > 0]
        if len(strict) < 10:
            continue
        out[t] = {
            "n_naive": len(v),
            "naive_median": q([r["st"] / r["debt"] for r in v], 0.5),
            "n_strict": len(strict),
            "strict_median": q([r["st"] / (r["lt"] + r["st"]) for r in strict], 0.5),
            "pct_lt_filed": share(len(strict), len(v)),
        }
    return out


def compute():
    de, spec, virk, home, land, meta, region, fin, sites = read_registers()
    log(f"  {sites:,} livestock sites, {len(de):,} businesses with animals, "
        f"{len(land):,} declaring land, {len(meta):,} in the CVR extract")
    types, total_de = by_type(de, spec, virk, land)
    reg, kom, unplaced = by_place(de, home, land, region)
    rows, excluded = build_sample(fin, de, spec, virk, land, meta)
    animals = [r for r in rows if r["type"] != "no animal units" and r["de"] > 0]
    log(f"  accounts: {len(fin):,} businesses, {len(rows):,} in primary agriculture, "
        f"{len(animals):,} of those keeping animals")
    return {
        "_what": "Who carries Denmark's nitrogen requirement, on the open registers, "
                 "as cohorts and distributions only.",
        "_privacy": "No identifying field is written here. Every figure is an "
                    "aggregate over a named cohort with its n stated.",
        "_sources": {
            "from": "the sibling project danish-livestock's fetched registers",
            "chr": "Jordbrugsanalyser:CHR24 (Landbrugsstyrelsen GeoServer)",
            "marker": "Marker:Marker_2025",
            "accounts": "distribution.virk.dk/offentliggoerelser, XBRL",
            "cvr": "CVR master data",
        },
        "sites": sites,
        "visibility": visibility(de, land, meta),
        "types": types,
        "total_de": total_de,
        "regions": reg,
        "kommuner": kom,
        "unplaced_holdings": unplaced,
        "organic": {" / ".join(k): v for k, v in organic_split(de, spec, virk, land).items()},
        "hectares": hectare_incidence(land, de, spec, virk, meta),
        "accounts_sample": {
            "n_filed": len(fin),
            "n_primary_agriculture": len(rows),
            "n_keeping_animals": len(animals),
            "n_with_land": sum(1 for r in animals if r["ha"] > 1),
            "excluded": dict(excluded),
            "balance_sheet_check": balance_sheet_check(fin),
            "equity_deciles": [q([r["equity_ratio"] for r in rows], p / 10.0)
                               for p in range(1, 10)],
        },
        "cohorts": cohort_stats(animals),
        "shock": shock_ladder(animals),
        "shock_de": shock_ladder_de(animals),
        "intersection": intersection(animals),
        "debt_artefact": st_share_artefact(animals),
    }




# ------------------------------------------------------------------- the document

def f0(x):
    return "—" if x != x else f"{x:,.0f}"


def f2(x):
    return "—" if x != x else f"{x:,.2f}"


def pct(x, dp=1):
    return "—" if x != x else f"{x:.{dp}f}%"


HEAD = """# Who pays for the nitrogen requirement

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
"""


PRIVACY = """
## 0. Why there are no names on this page

Every register underneath this analysis is public. Anyone can look up a CVR number,
read the filed accounts, see the animal units and the declared hectares, and work out
what this page works out for one named business in an afternoon.

This page does not do that, and the rule is not negotiable.

**Most Danish farms are natural persons.** `Enkeltmandsvirksomhed` — sole
proprietorship — is not a company with limited liability and a boardroom; it is one
human being, and the CVR register carries their name, their home address and their
telephone number, because for a sole trader those are the same thing as the
business's. Of the {n_animal_form_ekm:,} businesses keeping animals whose legal form
this project could read, {n_ekm:,} are sole proprietorships, and they hold
{pct_ekm_de} of the national herd.

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
"""


POLICY = """
## 1. What the instrument is, and what that alone tells you about incidence

Two records are needed here and they are different in kind. The *political* record —
what was agreed, by whom, and what was said about it — is collected verbatim, dated and
sourced in [POLITICS.md](POLITICS.md). The *legal* record is the regulations in force
for the current planning year, and those were read directly for this page rather than
taken from press coverage. Where a paragraph number appears below, the text was fetched
and checked.

| When | What | Status |
|---|---|---|
| 24 June 2024 | **Grøn Trepart** — the Green Tripartite agreement | aftale |
| 31 July 2024 | The **kvægundtagelse** — the cattle derogation allowing 230 kg N/ha — lapses | expiry |
| 19 June 2025 | The **braklægningspunkt** fixed: *"det maksimale reguleringstryk i de enkelte vandoplande"* | aftale |
| 27 Aug 2025 | The new **retentionskort** published by GEUS and Aarhus University | model output |
| 3 Dec 2025 | The **kvælstofaftale** — the nitrogen agreement and its distribution model | aftale |
| 21 July 2026 | **BEK 673** and **BEK 677** — the catch-crop rules for planning year 2026/2027 | gældende ret |
| 3 Sept 2026 | **L5** passed 119–34, becoming **LOV nr. 759 af 8. september 2026**, the new *gødskningslov*. In force **1 January 2027** | vedtaget lov |
| 1 Sept 2026 | A *tillægsaftale* exempting vegetable-growing areas from the new model in 2027 | aftale |

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
a regulatory unit with the 1 August 2017 reform, and the 1.4, 1.7 and 2.3 DE/ha harmony
ceilings went with it.

The date is Landbrugsstyrelsen's; what was checked here is the present tense of it. The
word `dyreenhed` occurs **zero times** in each of the three regulations that carry the
current requirements — BEK 931 of 16 July 2024 on the use of fertiliser, and BEK 673 and
BEK 677 of 21 July 2026 on catch crops — and where the old rules set a ceiling in animal
units the current one sets it in kilograms. That is not an inference from a summary; the
texts were fetched and searched.

What replaced it is four separate requirements, and the first three all key on the same
two thresholds — 30 and 80 kilograms of nitrogen per hectare of *harmoniareal*, from
manure and other organic fertiliser.

| Requirement | The rule | Source |
|---|---|---|
| **Manure ceiling** | Total organic nitrogen divided by **170 kg N/ha** may not exceed the harmoniareal. One rate, no derogation. | [BEK 931/2024 §14](https://www.retsinformation.dk/eli/lta/2024/931) |
| **Compulsory catch crops** | At least **10.7%** of the base area — but **14.7%** for a holding applying **80 kg N/ha or more** | [BEK 673/2026 §4 stk. 3](https://www.retsinformation.dk/eli/lta/2026/673) |
| **Livestock catch crops** | An additional requirement, per catchment, for any holding applying **30 kg N/ha or more**. Organic holdings are exempt from this one | BEK 673/2026 §4 stk. 4 and stk. 5, Bilag 2 |
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
80 kg N/ha line: **110 kg N per hectare below it, 175 kg N above** (BEK 673/2026 §24
stk. 2). The alternative that lets a holding buy its way out costs a livestock holding
59% more per hectare than an arable one.

**And the cattle derogation is gone.** Denmark's *kvægundtagelse* permitted 230 kg N/ha
on qualifying cattle holdings for twenty-two years. It expired on 31 July 2024 and was
not renewed, so those holdings dropped to 170 — a **26% cut in what may be spread**,
already delivered, before L5 was drafted. Any account of the burden on Danish dairy that
starts in 2026 has missed the largest single step.

### Two exemptions that decide a great deal

BEK 677/2026 §1 stk. 3 exempts a holding from the targeted requirement entirely if it
has a base area under 10 hectares, **or if it was certified for organic production, or
had applied to be, on 1 February 2026**. BEK 673/2026 §4 stk. 5 exempts organic
holdings from the livestock catch-crop requirement as well.

That is not a marginal advantage of the kind arithmetic produces. It is a statutory
exemption from two of the four instruments, and [section 4](#4-where-it-lands-and-on-whom)
measures how much land sits behind it.

### The law that takes over in 2027, and the thing in it that changes everything

The act passed on 3 September 2026 is **LOV nr. 759 af 8. september 2026, *Lov om
bæredygtig forvaltning af næringsstoffer og drivhusgasser m.v. i land- og skovbruget***
([Lovtidende text](https://www.retsinformation.dk/eli/lta/2026/759/dan/pdf)). Three of
its provisions decide incidence, and all three were read here rather than taken from
coverage of them.

**It does not apply yet, and that is why this page is about catch crops.** §57 puts it
in force on 1 January 2027 and repeals the old fertiliser act; §57 stk. 3 then says the
act *"finder ikke anvendelse på forhold, der vedrører planperioden 2019-2020 til og med
planperioden 2026-2027"* — for those, *"finder de hidtil gældende regler anvendelse"*.
So the requirements measured in sections 3 to 5 are the ones that actually bind this
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
verified here.** That matters because, as the block below shows, transfer is worth about
a quarter of cattle's modelled loss.

**The state can also simply take the land.** §11 gives a power of expropriation to carry
out measures under the act, with *"fuldstændig erstatning"* — full compensation — where
the intervention is expropriatory. §65 inserts a second, wider power into the CAP
administration act: the minister or the municipal council *"kan ekspropriere
landbrugsarealer, hvis det er af væsentlig betydning at råde over disse arealer for at
gennemføre foranstaltninger, som iværksættes for at forbedre klimaet til opfyldelse af
bindende målsætninger i lov om klima"*, with one carve-out — *"[s]tk. 1 kan ikke anvendes
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
Fjord table the cattle loss narrows from −1,122 kr/ha under the root-zone model to −811
once trading is allowed.

So the trading question is not a technicality about market design. It is the difference
between the sector that carries the largest loss carrying about a quarter less of it.
The statute permits the minister to allow transfer; the regulation that would say on
what terms is the single document whose absence most changes this page's conclusions,
and it is listed first in [section 7](#7-what-this-cannot-establish-and-what-would).
</details>

### Three channels, with opposite incidence

| Channel | Binds on | Falls hardest on |
|---|---|---|
| **The catch-crop percentage** | the base area — cereals, maize, rape, pulses | holdings whose land is mostly in those crops, and holdings whose base area is small relative to their manure |
| **The manure ceiling and the two thresholds** | the slurry, which is not optional, because the animals exist | holdings applying over 80 kg N/ha, where three separate requirements step up at once |
| **Land conversion and the set-aside ceiling** | the hectare itself | whoever *owns* lowland in a badly-retaining catchment |

The second channel is the one this project can measure directly, because both halves of
it are in open registers that join on the company number. The first can now be measured
too, imperfectly, and [section 3](#3-the-base-area-is-the-thing-cattle-has-least-of)
does it. The third cannot be measured here at all, because ownership is not in the
registers fetched.
"""


def sec_visible(d):
    v, h = d["visibility"], d["hectares"]
    acc = v["by_accounts"]
    ha_acc = h["by_accounts"]
    forms = sorted(v["by_form"].items(), key=lambda x: -x[1]["de"])[:6]
    rows = "\n".join(
        f"| {k} | {e['n']:,} | {e['de']:,.0f} | {share(e['de'], v['total_de']):.1f}% "
        f"| {e['de']/e['n']:,.0f} |"
        for k, e in forms)
    conc = v["concentration"]
    return f"""
## 2. Before anything else: three quarters of the herd keeps no public accounts

Level 2 of this page — which holdings have no buffer — can only be asked of holdings
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
{rows}

Over the {v['n_animal_cvr']:,} businesses that keep animals at all:

| | Businesses | Animal units | Share of herd |
|---|---:|---:|---:|
| Files an annual account | {acc['True']['n']:,} | {acc['True']['de']:,.0f} | **{share(acc['True']['de'], v['total_de']):.1f}%** |
| Files none | {acc['False']['n']:,} | {acc['False']['de']:,.0f} | **{share(acc['False']['de'], v['total_de']):.1f}%** |

And over the {h['n_cvr']:,} businesses that declare field parcels:

| | Businesses | Declared hectares | Share of the declared area |
|---|---:|---:|---:|
| Files an annual account | {ha_acc['True']['n']:,} | {ha_acc['True']['ha']:,.0f} | **{share(ha_acc['True']['ha'], h['total_ha']):.1f}%** |
| Files none | {ha_acc['False']['n']:,} | {ha_acc['False']['ha']:,.0f} | **{share(ha_acc['False']['ha'], h['total_ha']):.1f}%** |

**{share(acc['False']['de'], v['total_de']):.0f}% of the Danish herd and
{share(ha_acc['False']['ha'], h['total_ha']):.0f}% of the declared Danish farmland is
operated by a business whose finances are not public.** No amount of care with the
{acc['True']['n']:,} filings that do exist changes that. It is not a sampling problem
that a larger fetch would fix; it is a legal fact about who has to file.

*What the visible end is biased towards.* The incorporated businesses are the large
ones — mean {v['by_form']['Anpartsselskab']['de']/v['by_form']['Anpartsselskab']['n']:,.0f}
animal units for an ApS and
{v['by_form']['Aktieselskab']['de']/v['by_form']['Aktieselskab']['n']:,.0f} for an A/S,
against {v['by_form']['Enkeltmandsvirksomhed']['de']/v['by_form']['Enkeltmandsvirksomhed']['n']:,.0f}
for a sole proprietorship. So section 6 is not a picture of Danish farming under
stress. **It is a picture of the largest, most capitalised, most professionally
financed quarter of it** — the end most likely to have a term loan, a treasurer and a
buffer. Every fragility figure in section 6 should be read as a floor on the fragility
of the whole.

<details class="work">
<summary>The herd is concentrated enough that a quota binding on animals binds on a few hundred businesses — {conc['0.5']['holdings']:,} of them hold half of it</summary>

Over the {v['n_with_herd']:,} businesses with a non-zero animal-unit count:

| | Holdings | Share of holdings |
|---|---:|---:|
| Hold 25% of the national herd | {conc['0.25']['holdings']:,} | {conc['0.25']['pct_of_holdings']:.1f}% |
| Hold 50% | {conc['0.5']['holdings']:,} | {conc['0.5']['pct_of_holdings']:.1f}% |
| Hold 75% | {conc['0.75']['holdings']:,} | {conc['0.75']['pct_of_holdings']:.1f}% |
| Hold 90% | {conc['0.9']['holdings']:,} | {conc['0.9']['pct_of_holdings']:.1f}% |

Median holding: {v['median_de']:,.1f} DE. 90th percentile: {v['p90_de']:,.0f}. 99th:
{v['p99_de']:,.0f}.

Land is concentrated too, though less so: the largest
{h['cvrs_holding_half_the_land']:,} of {h['n_cvr']:,} land-declaring businesses
({share(h['cvrs_holding_half_the_land'], h['n_cvr']):.1f}%) declare half the hectares,
and the median declaration is {h['median_ha']:.1f} ha against a 99th percentile of
{h['p99_ha']:,.0f}.

This cuts both ways for the argument. It means an instrument aimed at the herd has a
very small number of addressees, which makes it administrable and makes compensation
cheap to target. It also means the median animal-keeping business in Denmark is a
{v['median_de']:,.0f}-animal-unit holding that is almost invisible in any
herd-weighted average — including several in this document, which is why counts of
holdings are printed beside every share of the herd.
</details>
"""


def sec_types(d):
    t = d["types"]
    h = d["hectares"]
    ordered = [x for x in order(t) if x != "no animal units"]
    rows = "\n".join(
        f"| {k} | {t[k]['n']:,} | {t[k]['de']:,.0f} | {t[k]['share_de']:.1f}% "
        f"| {t[k]['n_ratio']:,} | **{t[k]['med']:.2f}** "
        f"| {t[k]['over']['0.3']:.0f}% | **{t[k]['over']['0.8']:.0f}%** "
        f"| {t[k]['over']['1.4']:.0f}% |"
        for k in ordered)
    base = h["base"]
    brows = "\n".join(
        f"| {k} | {sum(base[k].values()):,.0f} "
        f"| **{share(base[k].get('in base', 0), sum(base[k].values())):.1f}%** "
        f"| {share(base[k].get('outside', 0), sum(base[k].values())):.1f}% "
        f"| {share(base[k].get('unclassified', 0), sum(base[k].values())):.1f}% |"
        for k in order(base))
    sur = "\n".join(
        f"| {k} | {t[k]['surplus']:,.0f} | {t[k]['n_surplus']:,} "
        f"| {t[k]['landless_de']:,.0f} | {t[k]['n_landless']:,} "
        f"| {share(t[k]['surplus'] + t[k]['landless_de'], t[k]['de']):.0f}% |"
        for k in ordered)
    tot_sur = sum(t[k]["surplus"] for k in ordered)
    tot_land = sum(t[k]["landless_de"] for k in ordered)
    n_sur = sum(t[k]["n_surplus"] for k in ordered)
    n_land = sum(t[k]["n_landless"] for k in ordered)
    dbase = base["dairy"]
    pbase = base["pigs"]
    return f"""
## 3. The base area is the thing cattle has least of

Section 1 established that the requirement is *a percentage of the base area* and that
three of the four instruments step up at 80 kg of manure nitrogen per hectare. Both
halves of that can be measured, imperfectly, on the open registers — and together they
locate the burden somewhere a stocking-density table does not.

### Where the holdings sit relative to the thresholds the rules use

The registers carry animal units, not kilograms of nitrogen, so the two lines below are
placed by a **stated conversion of 100 kg N per animal unit** and are indicative rather
than a test. They locate roughly where a holding crosses from one regulatory band into
the next; they do not establish that any particular holding does.

| Enterprise type | Holdings | Animal units | Share of herd | With land | Median DE/ha | ≈30 kg N/ha | ≈80 kg N/ha | 1.4 (historic) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{rows}

**{t['dairy']['over']['0.8']:.0f}% of dairy holdings that declare land sit above the
higher of the two thresholds**, against {t['pigs']['over']['0.8']:.0f}% of pig holdings
and {t['beef / other cattle']['over']['0.8']:.0f}% of beef. Above that line three
things happen at once: the compulsory catch-crop percentage rises from 10.7% to 14.7%,
the livestock catch-crop requirement applies on top, and the quota-reduction escape
valve reprices from 110 to 175 kg N per hectare. **The instrument does not tighten
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
{brows}

**{share(dbase.get('in base', 0), sum(dbase.values())):.0f}% of dairy's declared
hectares are on holdings whose largest crop is inside the base area, against
{share(pbase.get('in base', 0), sum(pbase.values())):.0f}% of pigs'.** Dairy grows
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
> DCA rådgivningsnotat, 24 May 2024,
> [p. 88](https://pure.au.dk/ws/portalfiles/portal/379114234/NUAR-slutnotat_24._maj_2024.pdf)

Two independent routes to the same conclusion: the register says dairy's base area is
small, and the report says a small base area is why cattle carries the largest loss.

*What this does not establish.* The classification uses each business's **largest**
declared crop, because that is all the summary register carries. A dairy holding whose
largest crop is grass certainly has cereal area too, so the true base share for dairy is
higher than {share(dbase.get('in base', 0), sum(dbase.values())):.0f}% and the true
share for pigs lower than {share(pbase.get('in base', 0), sum(pbase.values())):.0f}%.
The direction is robust and the magnitudes are not. The full parcel-level crop
declaration would fix this and is in a register already fetched — see
[section 7](#7-what-this-cannot-establish-and-what-would).

### The shed with no field, and the field that is too small

The second channel — manure that has nowhere to go — splits the herd a different way:

| Enterprise type | Surplus DE above 1.4/ha | Holdings | DE on holdings declaring no land | Holdings | Share of that type's herd |
|---|---:|---:|---:|---:|---:|
{sur}

Nationally that is **{tot_sur:,.0f} animal units in surplus on {n_sur:,} holdings and a
further {tot_land:,.0f} on {n_land:,} holdings with no declared land at all** —
together {share(tot_sur + tot_land, d['total_de']):.0f}% of the Danish herd standing on
more animal units than its own declared ground would take at the old harmony density.
That is a measure of pressure and not a finding of non-compliance; the qualification at
the end of this section says why.

And the two halves belong to different animals.

* **Dairy is land-squeezed.** {t['dairy']['n_surplus']:,} dairy holdings carry
  {t['dairy']['surplus']:,.0f} surplus animal units — the largest surplus of any type —
  but only {t['dairy']['n_landless']:,} declare no land. The dairy holding has fields;
  it has slightly too many cows for them, and the wrong crops on them.
* **Pigs are landless.** {t['pigs']['n_landless']:,} pig holdings hold
  {t['pigs']['landless_de']:,.0f} animal units with no declared hectare underneath them
  at all — more than twice the surplus carried by the {t['pigs']['n_surplus']:,} pig
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
compliant in law. The 1.4 DE/ha column is the **pre-2017** unit, kept only for
continuity with [NITROGEN.md](NITROGEN.md); it has no legal force. And the ≈30 and ≈80
columns rest on the stated 100 kg N per animal unit conversion, which this page has not
verified.
"""


def sec_place(d):
    reg = sorted(d["regions"].items(), key=lambda x: -x[1]["de"])
    rrows = "\n".join(
        f"| {k} | {e['n']:,} | {e['de']:,.0f} | {share(e['de'], d['total_de']):.1f}% "
        f"| {e['n_ratio']:,} | {e['med']:.2f} | {e['over14']:.0f}% |" for k, e in reg)
    dense = sorted([x for x in d["kommuner"].items() if x[1]["n_ratio"] >= 100],
                   key=lambda x: -x[1]["med"])[:12]
    krows = "\n".join(
        f"| {k} | {e['region'].replace('Region ', '')} | {e['n_ratio']:,} "
        f"| **{e['med']:.2f}** | {e['over14']:.0f}% | {e['de']:,.0f} |" for k, e in dense)
    jutland = ("Region Syddanmark", "Region Midtjylland", "Region Nordjylland")
    jut = sum(e["de"] for k, e in reg if k in jutland)
    jmed = sorted(e["med"] for k, e in reg if k in jutland)
    b = sorted(BEK677_BILAG1, key=lambda x: -x[2])
    vals = sorted(x[2] for x in b)
    bmed = (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
    brows = "\n".join(f"| {n} | {p:.1f}% |" for _i, n, p in b)
    cap = [n for _i, n, p in b if p == max(vals)]
    o = d["organic"]
    label = {"dairy / conventional": "Dairy, conventional",
             "dairy / organic": "Dairy, organic",
             "beef / other cattle / conventional": "Beef and other cattle, conventional",
             "beef / other cattle / organic": "Beef and other cattle, organic"}
    orows = "\n".join(
        f"| {label[k]} | {o[k]['n']:,} | {o[k]['de']:,.0f} | {o[k]['mean_de']:,.0f} "
        f"| {o[k]['n_ratio']:,} | **{o[k]['med']:.2f}** | {o[k]['over14']:.0f}% |"
        for k in ("dairy / conventional", "dairy / organic",
                  "beef / other cattle / conventional", "beef / other cattle / organic")
        if k in o)
    dc, do = o["dairy / conventional"], o["dairy / organic"]
    org_de = sum(v["de"] for k, v in o.items() if k.endswith("organic"))
    org_n = sum(v["n"] for k, v in o.items() if k.endswith("organic"))
    return f"""
## 4. Where it lands, and on whom

### The published allocation, which is not where the animals are

The mandatory targeted requirement for 2026/2027 is a short list. Twenty coastal
catchments carry one; every other catchment in Denmark carries none, because the
subsidised voluntary round covered the need there. This is the whole of BEK 677/2026
Annex 1:

| Coastal catchment | Requirement, as % of the holding's base area |
|---|---:|
{brows}

Twenty catchments, from {min(vals):.1f}% to {max(vals):.1f}%, median {bmed:.2f}%.
{len(cap)} sit at the {max(vals):.1f}% ceiling: {", ".join(cap)}.

**Read the names.** Kalundborg Fjord, Dybsø Fjord, Stege Bugt, Jammerland Bugt and
Musholm Bugt are Zealand and Møn. Kløven, Helnæs Bugt, Kertinge Nor and Aborg Minde Nor
are Funen and the small islands. Als Fjord, Augustenborg Fjord, Genner Bugt and
Hejlsminde Nor are Sønderjylland's inner waters. This is not the west-Jutland livestock
belt, and three of the four catchments at the ceiling are on the islands.

Now set that against where the animals are:

| Region | Holdings | Animal units | Share of herd | With land | Median DE/ha | >1.4 |
|---|---:|---:|---:|---:|---:|---:|
{rrows}

**{share(jut, d['total_de']):.0f}% of the Danish herd is in Jutland**, and the region
carrying the least of it — {reg[3][0].replace("Region ", "")} at
{share(reg[3][1]['de'], d['total_de']):.1f}%, median {reg[3][1]['med']:.2f} DE/ha —
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

| Kommune, ranked by median stocking density | Region | Holdings with land | Median DE/ha | >1.4 | Animal units |
|---|---|---:|---:|---:|---:|
{krows}

*(minimum 100 holdings declaring land, so that a median means something)*

The three Jutland regions run from {jmed[0]:.2f} to {jmed[-1]:.2f} DE/ha at the median,
which is flat enough that the region is useless as a unit. The kommune is sharper and
names one belt: the sandy west and south of Jutland, plus Sønderjylland. That belt is
where the *manure* pressure is, and the manure pressure is a real burden — the two
thresholds in section 3 and the 170 kg N/ha ceiling all bite there. It is simply not
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
on 1 February 2026 is outside the targeted requirement altogether (BEK 677/2026 §1 stk.
3 nr. 2) and outside the livestock catch-crop requirement as well (BEK 673/2026 §4 stk.
5). Underneath that exemption there is also an arithmetic advantage, and the livestock
register can measure it on cattle:

| Cohort | Holdings | Animal units | Mean DE | With land | Median DE/ha | >1.4 |
|---|---:|---:|---:|---:|---:|---:|
{orows}

Organic dairy holdings farm substantially more land per cow, and only part of that is a
smaller herd: mean herd {do['mean_de']:,.0f} DE against {dc['mean_de']:,.0f}, which is
{abs(100*(do['mean_de']-dc['mean_de'])/dc['mean_de']):.0f}% smaller, but a median
stocking density of **{do['med']:.2f} against {dc['med']:.2f} DE/ha**, which is
{100*(1-do['med']/dc['med']):.0f}% lower. On beef the two are indistinguishable
({o['beef / other cattle / organic']['med']:.2f} against
{o['beef / other cattle / conventional']['med']:.2f}), which is what you would expect:
extensive beef is already below any threshold that binds.

The independent check agrees, and it is stronger than an exemption. In NUAR's modelling
of the discharge-based regulation across six allocation models, **organic holdings do
not merely lose less — they gain**, at between +341 and +523 kroner per hectare against
the reference, in a catchment where cattle lose between −969 and −1,207. That is the
only enterprise type in the table with a positive sign in every column.

*What this does not establish.* The livestock register's organic flag is on the
**herd**, not on the land, and the statutory exemption turns on certification of the
*holding*. A conventional herd grazing organically certified land is invisible here, and
an organic arable holding with no animals does not appear in this cut at all — which
matters, because an arable holding is exactly what the targeted requirement is aimed at.
The organic share of the national herd measured this way is
{share(org_de, d['total_de']):.1f}% on {org_n:,} cattle holdings, and that is a floor.
"""


def sec_hectares(d):
    h = d["hectares"]
    byt = h["by_type"]
    ordered = [x for x in order(byt)]
    rows = "\n".join(
        f"| {k} | {byt[k]['n']:,} | {byt[k]['ha']:,.0f} | "
        f"{share(byt[k]['ha'], h['total_ha']):.1f}% | {byt[k]['ha']/byt[k]['n']:,.0f} |"
        for k in ordered)
    crops = "\n".join(f"| {crop_en(c)} | {a:,.0f} | {share(a, h['total_ha']):.1f}% |"
                      for c, a in h["top_crops"][:8])
    zero_n = dict(h["top_crops"]).get("Miljøtilsagn græs (0 N), permanent", 0.0)
    no = byt["no animal units"]
    return f"""
## 5. Half the hectares have no animals over them

Sections 3 and 4 asked who keeps the animals and what they grow. Ask instead who holds
the hectares the percentage is charged on, and the population changes completely.

| Operator of the declared hectares | Businesses | Declared hectares | Share | Mean ha |
|---|---:|---:|---:|---:|
{rows}

**{share(no['ha'], h['total_ha']):.1f}% of Denmark's declared farmland —
{no['ha']:,.0f} hectares across {no['n']:,} businesses — is farmed by a business with
no animal units in the livestock register at all.** These are the arable holdings, and
section 3 showed that {share(d['hectares']['base']['no animal units'].get('in base', 0), sum(d['hectares']['base']['no animal units'].values())):.0f}%
of their hectares are on holdings whose largest crop is inside the base area. They are
the population the percentage is charged on most completely.

Two different costs reach them, one now and one from 2027, and they are not the same
kind of cost.

* **Today the instrument is a catch-crop percentage**, and the cost is a hectare of
  rotation given over to a crop that is not sold, on a base area that is nearly all of
  the farm. The 34.5% ceiling in section 4 means a third of the cereal ground.
* **From 2027 the quota is on discharge**, and then the constraint moves to the input
  the arable holding actually controls: the bag. That is the channel
  [NITROGEN.md section 2c](NITROGEN.md) predicts bites first — *mineral fertiliser is
  the free variable and manure is not.* The livestock holding meets a tightening quota
  by rearranging where the slurry goes; the arable holding meets it by buying less
  nitrogen and harvesting less wheat. One is a logistics cost and the other is a yield
  cut.

| Largest declared crop on the holding (hectare-weighted) | Hectares | Share |
|---|---:|---:|
{crops}

Winter wheat and spring barley alone account for
{share(h['top_crops'][0][1] + h['top_crops'][1][1], h['total_ha']):.0f}% of the
declared area under this measure, and both are cereals whose yield responds to applied
nitrogen over the range a quota would move it. One row is worth reading twice:
{zero_n:,.0f} hectares ({share(zero_n, h['total_ha']):.1f}%) are already on holdings
whose largest declared crop is grass under an environmental commitment that permits
**no nitrogen at all**. That land is not available to be tightened, and it is a
reminder that the baseline the quota is applied to is not a uniform one.

> **And there is not one arable balance sheet in this analysis.**
>
> The accounts in section 6 were fetched for businesses on the livestock map, so every
> one of the {d['accounts_sample']['n_filed']:,} filings is a business that keeps or
> kept animals. The sibling project is extending the fetch to crop holdings and that
> work is in progress; it is not in this data.
>
> So for the cohort carrying **half the hectares** and taking the most direct form of
> the burden, this page can describe the exposure and can say **nothing at all** about
> the buffer. That is a gap in the answer and not a hedge on it: a reader who wants to
> know whether Danish arable farming can absorb a per-hectare nitrogen cut will not
> find it here, and should not read section 6 as though it generalised.
"""


def sec_money(d):
    s = d["accounts_sample"]
    c = d["cohorts"]
    sh = d["shock"]
    it = d["intersection"]
    art = d["debt_artefact"]
    ordered = [x for x in order(c)]
    dec = s["equity_deciles"]
    crows = "\n".join(
        f"| {k} | {c[k]['n']:,} | {c[k]['median_de']:,.0f} "
        f"| {c[k]['median_assets']/1e6:,.1f} | **{c[k]['median_equity_ratio']:.2f}** "
        f"| {c[k]['pct_negative_equity']:.0f}% | {c[k]['pct_loss']:.0f}% "
        f"| {f0(c[k]['median_profit_per_ha'])} | {f2(c[k]['median_density'])} |"
        for k in ordered)
    lrows = "\n".join(
        f"| {k} | {sh[k]['n']:,} | {f0(sh[k]['break_even_median'])} | "
        + " | ".join(f"{sh[k]['ladder'][str(x)]:.0f}%" for x in SHOCK_HA) + " |"
        for k in order(sh))
    sd = d["shock_de"]
    drows = "\n".join(
        f"| {k} | {sd[k]['n']:,} | {sd[k]['n_landless']:,} | "
        f"{f0(sd[k]['break_even_median'])} | "
        + " | ".join(f"{sd[k]['ladder'][str(x)]:.0f}%" for x in SHOCK_DE) + " |"
        for k in order(sd))
    max_err = 100 * max(art[k]['naive_median'] - art[k]['strict_median'] for k in art)
    arows = "\n".join(
        f"| {k} | {art[k]['pct_lt_filed']:.0f}% | {100*art[k]['naive_median']:.0f}% "
        f"| {100*art[k]['strict_median']:.0f}% "
        f"| {100*(art[k]['naive_median']-art[k]['strict_median']):+.0f} pp |"
        for k in order(art))
    trows = "\n".join(
        f"| {k} | {c[k]['n_profit_3y']:,} | {c[k]['median_profit_3y']/1e6:,.1f} "
        f"| {c[k]['pct_profit_3y_negative']:.0f}% "
        f"| {c[k]['median_equity_trajectory']:+.3f} "
        f"| {c[k]['pct_trajectory_falling']:.0f}% |"
        for k in ordered if c[k]["n_profit_3y"] >= 10)
    E = EXTENSIFICATION_KR_HA
    def yrs(t, rate):
        m = sh.get(t, {}).get("break_even_median", float("nan"))
        return rate / m if m == m and m > 0 else None
    payback = "\n".join(
        "| " + t + f" | {f0(sh[t]['break_even_median'])} | "
        + " | ".join(
            (f"{yrs(t, r):.1f}" if yrs(t, r) is not None else "—")
            for r in (82500, 59500, 35500)) + " |"
        for t in sorted(sh, key=lambda x: -sh[x]["break_even_median"]))
    yr_beef = yrs("beef / other cattle", 35500) or float("nan")
    yr_dairy = yrs("dairy", 82500) or float("nan")
    nuar_models = " | ".join(NUAR_MODELS)
    nuar_dashes = "".join("---:|" for _ in NUAR_MODELS)
    nuar_rows = "\n".join(
        "| " + ("**" + r[0] + "**" if r[0] in ("Cattle", "Organic") else r[0]) + " | "
        + " | ".join(f"{v:+,}" for v in r[1:]) + " |"
        for r in NUAR_T75)
    ix = it["by_type"]

    def cell(t, k):
        return ix.get(t, {}).get(k, 0)
    irows = "\n".join(
        f"| {t} | {sum(ix[t].values()):,} | **{cell(t, '(True, True)')}** "
        f"({share(cell(t, '(True, True)'), sum(ix[t].values())):.0f}%) "
        f"| {cell(t, '(True, False)')} | {cell(t, '(False, True)')} "
        f"| {cell(t, '(False, False)')} |"
        for t in order(ix))
    return f"""
## 6. Which balance sheets have no buffer

### The sample, and what it is a sample of

| | |
|---|---:|
| Businesses with filed accounts in this data | {s['n_filed']:,} |
| …in primary agriculture (NACE 011–015) | {s['n_primary_agriculture']:,} |
| …keeping animals in the 2024 livestock register | **{s['n_keeping_animals']:,}** |
| …of those, also declaring field parcels | {s['n_with_land']:,} |

{s['excluded']['not primary agriculture (NACE)']:,} filings were dropped as not
primary agriculture. They are not noise to be tidied away — they are horse-keeping
businesses, property-letting companies, fish farms, livestock wholesalers and
non-financial holding companies that appear in the register because they happen to
hold a livestock site. Left in, the largest of them has assets of over fifty billion
kroner and would have set every mean on this page by itself. Medians are used
throughout anyway, and the exclusion is stated so the count can be checked.

Read section 2 before reading any figure below. This is the incorporated quarter of
the herd, it is the large end, and it is therefore the **most** resilient end.

### The distribution of equity

Equity ratio — equity over total assets — is the single number a bank looks at, and it
is the closest thing in a filed account to "how much can go wrong before this stops".
Across the {s['n_primary_agriculture']:,} agricultural filings:

| Decile | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Equity ratio | {dec[0]:.2f} | {dec[1]:.2f} | {dec[2]:.2f} | {dec[3]:.2f} | {dec[4]:.2f} | {dec[5]:.2f} | {dec[6]:.2f} | {dec[7]:.2f} | {dec[8]:.2f} |

**The bottom decile is already negative** — assets are worth less than the debts
against them — and the second decile sits at {dec[1]:.2f}, which is thin for a
business whose assets are mostly illiquid and whose income is a commodity price.

### By enterprise type

| Enterprise type | n | Median DE | Median assets (m. kr) | Median equity ratio | Negative equity | Loss last year | Median profit per ha (kr) | Median DE/ha |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{crows}

This table is the reason the page is organised the way it is. **The type under the most
regulatory pressure is the one in the best financial condition.** Dairy has the highest
stocking density of any type, the smallest catch-crop base area, and the lowest loss rate
({c['dairy']['pct_loss']:.0f}% of the {c['dairy']['n_profit']} dairy filings carrying
a profit figure), the lowest share with negative equity, and a median profit per
hectare {c['dairy']['median_profit_per_ha']/c['beef / other cattle']['median_profit_per_ha']:.1f}
times that of beef. Beef and other cattle have the *highest* median equity ratio
({c['beef / other cattle']['median_equity_ratio']:.2f}) and simultaneously the highest
loss rate of any real farming type ({c['beef / other cattle']['pct_loss']:.0f}%) — a
combination that describes an asset-rich, income-poor holding, which is what extensive
cattle on owned land is.

### How large a shock each cohort can take

The ladder assumes no cost at all; a published estimate is laid on it two subsections
below, once the shape of the buffer is established independently of it. The question
here is only: how many holdings in each cohort go from profit to loss as an annual
charge per declared hectare rises? The break-even column is the charge the median
holding could absorb exactly.

| Enterprise type | n | Break-even (kr/ha) | 0 | 500 | 1,000 | 2,000 | 3,000 | 5,000 | 8,000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{lrows}

*(share of the cohort making a loss once a charge of that many kroner per declared
hectare is applied to the last filed twelve-month profit)*

The gradients differ by more than the levels do. Dairy absorbs
{f0(sh['dairy']['break_even_median'])} kr/ha before the median holding turns, and even
at 8,000 kr/ha only {sh['dairy']['ladder']['8000']:.0f}% of the cohort is loss-making.
Beef starts at {sh['beef / other cattle']['ladder']['0']:.0f}% loss-making before
anything is applied and is at {sh['beef / other cattle']['ladder']['1000']:.0f}% by
1,000 kr/ha. **The cohort with the least room is the one the instrument is least
aimed at.**

That ladder has a hole in it, and the hole is the finding of section 3. A charge per
hectare cannot be applied to a holding with no hectares, so every landless unit drops
silently out of the table above — {sum(sd[k]['n_landless'] for k in sd):,} of the
{sum(sd[k]['n'] for k in sd):,} holdings with both a herd and a profit figure. Charging
per animal unit instead puts them back, and is anyway the better model of how the cost
reaches them: through the price of a slurry placement contract, which scales with the
slurry.

| Enterprise type | n | of which landless | Break-even (kr/DE) | 0 | 250 | 500 | 1,000 | 2,000 | 4,000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{drows}

*(share of the cohort making a loss once a charge of that many kroner per animal unit
is applied)*

**Changing the denominator swaps which cohort is thinnest, and it swaps pigs with
beef.** Ranked by what the median holding can absorb:

* per declared hectare — dairy {f0(sh['dairy']['break_even_median'])}, poultry
  {f0(sh['poultry']['break_even_median'])}, pigs {f0(sh['pigs']['break_even_median'])},
  **beef {f0(sh['beef / other cattle']['break_even_median'])}**;
* per animal unit — dairy {f0(sd['dairy']['break_even_median'])}, poultry
  {f0(sd['poultry']['break_even_median'])}, beef
  {f0(sd['beef / other cattle']['break_even_median'])}, **pigs
  {f0(sd['pigs']['break_even_median'])}**.

Dairy is the most resilient on both measures and by a similar factor, so nothing about
dairy turns on the choice. What turns on it is which of pigs and beef is the thin one.
Per hectare, beef looks like the sector with no room, because beef holds a great many
hectares against very little income. Per animal unit, pigs are, because a pig holding
concentrates a large herd on little or no land. **Whether the requirement is
denominated in hectares or in slurry decides which of those two sectors it is a crisis
for** — and that is a drafting choice, not a fact about farming.

And the landless holdings are not the healthy half of the pig cohort. Of the
{sd['pigs']['n_landless']} pig holdings with accounts and no declared land,
{sd['pigs']['pct_loss_landless']:.0f}% made a loss in their last filed year, against
{sd['pigs']['pct_loss_with_land']:.0f}% of the {sd['pigs']['n_with_land']} that do
declare land. The group most exposed to a repricing of placement contracts is also the
group already least able to absorb one.

### What a published cost estimate does to those ladders

The ladders above assume nothing. There is one published by-farm-type estimate this
project has read in its primary source, and putting it on the ladder is the point of
having built the ladder.

NUAR modelled the change in gross margin per hectare against the reference regulation,
by enterprise type, for the Hjarbæk Fjord catchment under six quota-allocation models:

| Enterprise type | {nuar_models} |
|---|{nuar_dashes}
{nuar_rows}

*(change in DB2, kroner per hectare, against a reference of compulsory and livestock
catch crops. Eriksen et al., NUAR, DCA rådgivningsnotat, 24 May 2024, Tabel 7.5. The
report states the pattern repeats across the other ten catchments analysed.)*

Three things follow, and the third is the one that matters.

**The magnitudes land on the low rungs of the ladder.** The losses run from about 330
to about 1,200 kroner per hectare. At 1,000 kr/ha this page's ladder puts
{sh['dairy']['ladder']['1000']:.0f}% of dairy holdings into a loss,
{sh['pigs']['ladder']['1000']:.0f}% of pigs and
{sh['beef / other cattle']['ladder']['1000']:.0f}% of beef and other cattle. A cost of
this size is absorbable by most of the sample — but the sample is the incorporated
quarter, and the ladder's zero column already shows
{sh['beef / other cattle']['ladder']['0']:.0f}% of beef holdings loss-making before
anything is added.

**Cattle carries two to three times the arable loss in every column**, which is the
mechanism section 3 measured from the other side. And **organic is positive in every
column** — not exempt-and-therefore-unaffected, but better off than the reference.

**And no allocation model rescues cattle.** This is the third thing, and it is the one
that matters, because six models is what the argument has been about. Cattle's loss
lands between −969 and −1,207 kroner per hectare in **every one of them** — a spread of
238 kr/ha, or 22% of its own loss, the narrowest relative range of any loss-making type
in the table. Specialised arable moves from −327 to −678 across the same six, a spread
of 351 kr/ha and 71% of its own loss.

So the choice being fought over is a real choice **for arable and a largely settled
question for cattle**. Picking a different quota-allocation model can roughly halve or
double what a specialised arable holding loses; it moves a cattle holding by about a
fifth and leaves it, in all six cases, losing two to three times what the arable holding
does. **The instrument the industry is arguing about is not the instrument that decides
cattle's position — the base area is**, and the base area is fixed by what grows on the
farm.

The one thing in the report that does move cattle materially is trading: the same table
narrows cattle's loss to −811 kr/ha once allowances can be exchanged, which is the
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
| Carbon-rich soil, or a high-nitrogen-need area with wetland potential | **{E["rotation land, priority area"]:,} kr/ha** | {E["grass, priority area"]:,} kr/ha |
| Everywhere else | {E["rotation land, elsewhere"]:,} kr/ha | {E["grass, elsewhere"]:,} kr/ha |

Set that against what a hectare currently earns, using the same medians as the ladder
above. The figure is the number of years of the cohort's median per-hectare profit that
the payment replaces:

| Enterprise type | Median profit per ha | 82,500 | 59,500 | 35,500 |
|---|---:|---:|---:|---:|
{payback}

**The same schedule is a very different offer depending on who is asked.** Taking each
cohort at the rate it would actually be offered — grass for beef, rotation land for
dairy — the payment replaces about **{yr_beef:.0f} years** of a beef hectare's margin
and about **{yr_dairy:.0f}** of a dairy hectare's. At an identical rate the gap is
wider still: 82,500 kr/ha is {yrs('beef / other cattle', 82500):.0f} years for beef
against {yr_dairy:.0f} for dairy. Against a farming horizon of a generation, one of
those is a good price and the other is not.

And the direction is the wrong way round for the nitrogen. **The holdings for which the
offer is most attractive are the extensive ones, whose hectares carry the least manure**
— beef at a median {d['cohorts']['beef / other cattle']['median_density']:.2f} DE/ha.
The holdings whose hectares carry the most are the ones for which it is worst value —
dairy at {d['cohorts']['dairy']['median_density']:.2f}.

There is a second reason dairy should decline, and it is the mechanism
[NITROGEN.md section 2c](NITROGEN.md) already predicted. **Selling a hectare out of a
land-squeezed holding raises its manure loading on every hectare that remains.** A dairy
holding at {d['cohorts']['dairy']['median_density']:.2f} DE/ha that converts land moves
*up* against the 80 kg N/ha threshold and the 170 kg N/ha ceiling, not down. The
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
{yr_beef/yr_dairy:.0f} between the two cattle sectors at the rates each would be
offered, and {yrs('beef / other cattle', 82500)/yr_dairy:.0f} at the same rate — and no
discount rate reverses a gap of that size.

### The overlap, which is the actual answer

Exposed means at or above the indicative {it['line']} DE/ha line — where section 1's
80 kg N/ha threshold sits, and where three of the four requirements step up at once — or
declaring no land at all. Thin means an equity ratio below 0.20.

| Enterprise type | n | Exposed **and** thin | Exposed, not thin | Thin, not exposed | Neither |
|---|---:|---:|---:|---:|---:|
{irows}

First, the size of the exposed column itself:
**{sum(cell(t, '(True, True)') + cell(t, '(True, False)') for t in ix):,} of
{it['n_rows']} animal-keeping holdings with accounts
({share(sum(cell(t, '(True, True)') + cell(t, '(True, False)') for t in ix), it['n_rows']):.0f}%)
are on the exposed side of the line.** Above the 80 kg N/ha threshold is where a
livestock holding normally is; that is not a finding about a stressed minority, it is
the ordinary condition of the sector. Which is why the second column matters more than
the first.

**{it['n_both']} of {it['n_rows']} ({share(it['n_both'], it['n_rows']):.0f}%) are both
exposed and thin**, and {share(it['n_both'], it['n_both'] + sum(cell(t, '(False, True)') for t in ix)):.0f}%
of every thin holding in the sample is also an exposed one. They hold
{it['de_held']:,.0f} animal units. That is {share(it['de_held'], d['total_de']):.1f}%
of the national herd, but the denominator is the wrong one to reassure with: this
cohort is drawn only from the {share(d['visibility']['by_accounts']['True']['de'], d['total_de']):.0f}%
of the herd whose owners publish accounts, and the other
{share(d['visibility']['by_accounts']['False']['de'], d['total_de']):.0f}% is not
known to be in better condition. The cohort has a median herd of {it['median_de']:,.0f} DE and a median equity
ratio of {it['median_equity_ratio']:.2f}. {it['n_negative_equity']} of them already
have negative equity and {it['n_loss']} made a loss in their last filed year. Of those
losing money while equity is still positive (n={it['n_years_of_equity']}), the median
holding has **{it['median_years_of_equity']:.1f} years of equity left at its current
loss rate** — before any nitrogen cost at all.

The profile, stated as a profile: **a pig holding of a few hundred to a few thousand
animal units, either landless or stocked above the higher manure threshold, with an
equity ratio under a fifth and a loss already on the last filed accounts.** Pigs are
{cell('pigs', '(True, True)')} of the {it['n_both']} — half the cohort — and
{share(cell('pigs', '(True, True)'), sum(ix['pigs'].values())):.0f}% of all pig
holdings with accounts sit there, against
{share(cell('dairy', '(True, True)'), sum(ix['dairy'].values())):.0f}% of dairy — and
dairy is *more* exposed by every physical measure in section 3. The difference is
entirely the balance sheet. **Dairy's problem is the base area; pigs' problem is the
equity**, and only one of those can be fixed by a transition scheme.

### Two qualifications that change the reading

**The accounts are measured at a cyclical high.** Over the three filed years:

| Enterprise type | n | Median 3-year cumulative profit (m. kr) | Negative over 3 years | Median change in equity ratio | Falling |
|---|---:|---:|---:|---:|---:|
{trows}

Equity ratios rose over the period for every type except the mixed remainder, and
median three-year cumulative profit is positive and large for dairy and pigs. **These
balance sheets entered the policy period rebuilt.** That is why the no-buffer cohort
is as small as it is, and it means the same measurement taken after two poor years
would find a materially larger one. It also means the buffers above are real and
should not be argued away.

**Biological assets are a buffer you cannot spend twice.** The herd is on the balance
sheet — median {pct(100*c['dairy']['median_biological_share'])} of assets for dairy
(n={c['dairy']['n_biological']}) and
{pct(100*c['pigs']['median_biological_share'])} for pigs
(n={c['pigs']['n_biological']}), where the tag is filed at all. It is the most liquid
large asset a livestock holding has and selling it is the same act as ceasing to
produce. A solvency ratio that counts it is counting the exit as the reserve.

<details class="work">
<summary>A worked example of the trap this project keeps falling into: a debt-structure finding that was a missing XBRL tag, and would have been wrong by up to {max_err:.0f} percentage points</summary>

An early version of this analysis found that beef holdings carried 68% of their debt
short-term against 24% for dairy, and read that as dairy being mortgage-financed while
beef lives on the overdraft. It is a plausible story and it fits the other findings.

It was mostly an artefact. `lt_debt` is
`LongtermLiabilitiesOtherThanProvisions`, and a filing that does not present the line
does not carry the tag. Treating an absent tag as a zero is correct for the *level* of
debt — the balance-sheet identity confirms it, below — and catastrophic for the
*composition*, because it forces the short-term share to 100% for every holding that
did not file the line. Those holdings are not spread evenly:

| Enterprise type | Filings carrying `lt_debt` | Short-term share, treating absent as zero | …restricted to filings carrying both tags | Error |
|---|---:|---:|---:|---:|
{arows}

The real spread is roughly {100*min(art[k]['strict_median'] for k in art):.0f}–{100*max(art[k]['strict_median'] for k in art):.0f}%
rather than {100*min(art[k]['naive_median'] for k in art):.0f}–{100*max(art[k]['naive_median'] for k in art):.0f}%,
and the shape survives only for poultry and the mixed remainder.

**And once corrected, the finding is gone.** Dairy, pigs and beef sit at
{100*art['dairy']['strict_median']:.0f}%, {100*art['pigs']['strict_median']:.0f}% and
{100*art['beef / other cattle']['strict_median']:.0f}% — a spread too narrow to carry
any argument about who is term-financed and who is on the overdraft. That is why no
debt-composition figure appears in any table on this page. The interesting version of
this note is not that a number was corrected; it is that **the correction deleted the
finding**, and a finding that survives only in its uncorrected form was never a finding.
One further caution even on the corrected column: `st_debt` is
`ShorttermLiabilitiesOtherThanProvisions`, which includes trade payables as well as bank
debt, so it is not a measure of how much of a holding's borrowing reprices annually.

**Why the level is still safe when the composition was not.** Where the tag is
present, assets minus equity minus both debts leaves a median residual of
{pct(100*d['accounts_sample']['balance_sheet_check']['lt_debt present']['median_residual'])}
of assets (n={d['accounts_sample']['balance_sheet_check']['lt_debt present']['n']:,});
where it is absent, assets minus equity minus short-term debt alone leaves
{pct(100*d['accounts_sample']['balance_sheet_check']['lt_debt absent']['median_residual'])}
(n={d['accounts_sample']['balance_sheet_check']['lt_debt absent']['n']:,}). The
identity closes either way, so the absent tag really is a zero — the number was right
and the ratio built from it was not.

**And one that no range check catches at all.** The `gross` column is
`GrossResult`/`GrossProfitLoss` — *bruttofortjeneste*, gross profit after variable
costs. It is **not turnover**. `Revenue` is a separate tag present on about one filing
in twenty, because a Danish class B company may omit it. Every figure it produces is
plausible, correctly signed and of the right order of magnitude; a "profit margin"
computed as profit over `gross` would be a real ratio of two real numbers and would
mean something different for every firm in the sample. There is therefore **no margin
on sales anywhere on this page**. Everything is per hectare or per animal unit.
</details>
"""


def sec_gaps(d):
    h = d["hectares"]
    return f"""
## 7. What this cannot establish, and what would

The house rule on this site is that an absence is reported as a count over a named
corpus. Here is the count. The middle column says what this page actually did, which
for several rows is *read the regulation*, and for several others is *not obtain the
data*.

| Question the brief asked | Answer here | What would answer it |
|---|---|---|
| **The allocation mechanism** | Established, from the regulations. It is a percentage of the base area, set per coastal catchment, with two manure thresholds at 30 and 80 kg N/ha and a 170 kg N/ha ceiling. The texts were fetched and read. | — |
| **Which catchments carry the largest mandatory requirement** | Established for 2026/2027, from BEK 677 Annex 1: twenty catchments, 14.8% to 34.5%. | — |
| **Whether high-density kommuner are also low-retention catchments** | **Not established, and not asserted.** Published evidence exists in both directions and this project has not obtained the retention grid. | The **kystvandopland** boundaries and the GEUS/AU retention grid of 27 Aug 2025, joined to the field-parcel geometry the sibling project already holds. Both are model outputs and both are published. Highest-value fetch on this list. |
| **On what terms discharge quotas may be transferred** | **Partly established.** LOV 759 §6 stk. 4 creates the power to permit transfer; the terms — who to whom, whether bounded within a catchment, at what price — are **not verified**. This is the most load-bearing gap on the page: transfer is worth roughly a quarter of cattle's modelled loss. | The implementing regulation under §6, once issued. |
| **Whether the implementing regulations under LOV 759 have been issued** | **Not established.** The act is a framework; every number that decides a holding's position is delegated. | Checking Lovtidende after the act commences on 1 January 2027. |
| **The numeric braklægningspunkt** | **Not established**, and there may be no single number: it is described as set per catchment. | The 18 June 2025 *delaftale* and the implementing act. |
| **Compensation and transition rates** | **Not established. No rate in kroner per hectare has been verified by this project.** Scheme names exist in the regulation index; a name is not a rate and is not published here as one. | A fresh pass over the *tilskud* regulations and their annexes. This one was not done. |
| **Owned versus rented land** | Not established at all. The field-parcel register records who *declares* a parcel, not who owns it. | The ownership register (*Ejerfortegnelsen*) or the land register (*Tingbogen*), joined on the property identifier. The sibling project holds the GraphQL schema and has not fetched it. This is also the join that would make individual identification easy, which is a reason to publish only the distribution. |
| **Uptake of the voluntary conversion schemes, by enterprise type** | Not obtained, which is why section 6's closing argument is labelled a prediction. | The published *tilsagn* lists for skovrejsning, permanent ekstensivering and the wetland schemes, joined on CVR to the livestock register. The commitments are administered by the state and the areas are registered. |
| **Crop mix per holding** | Only the single largest declared crop, which is why section 3's base-area split is a proxy with a stated direction and unstated magnitude. | The full parcel-level crop declaration, in the same Marker layer already fetched and reduced to a top-crop summary on the way in. Recoverable without a new source, and it would turn section 3's best finding from a direction into a number. |
| **Kilograms of manure nitrogen per hectare, per holding** | Not established. Animal units were converted at a **stated** 100 kg N per unit, and the declared area is not the *harmoniareal*. | The *gødningsregnskab*, which is filed by every holding and is not open. |
| **Balance sheets for arable holdings** | None exist in this data. Every filing here belongs to a livestock business — including, awkwardly, the population the targeted requirement is most aimed at. | The sibling project's crop-farmer extension, in progress. |
| **The finances of {share(d['visibility']['by_accounts']['False']['de'], d['visibility']['total_de']):.0f}% of the herd and {share(h['by_accounts']['False']['ha'], h['total_ha']):.0f}% of the land** | Not obtainable. | Nothing public. Sole proprietorships and partnerships have no filing duty. The only routes are the farm accountancy survey (*Regnskabsstatistik for jordbrug*, a sample, published in aggregate) or the advisory sector's benchmarking, which is not open. **This one does not close.** |
| **The inter-farm slurry placement contracts** | Not obtainable. Not in any register. | Nothing. These are private contracts. Their existence is inferable from the {sum(d['types'][t]['landless_de'] for t in d['types']):,.0f} animal units standing on holdings with no declared land; their terms are not. |
| **The CO2e tax on agricultural emissions** | **Out of scope, and it is not law.** It is a separate instrument with a different base — modelled greenhouse-gas emissions from digestion and manure handling, not nitrogen — and therefore a different incidence, which this page does not compute. It exists as a political agreement; no implementing bill was located in the Folketing record, and the government's own stated plan is to introduce one in 2027 for entry into force in 2030. Nothing on this page should be read as covering it, and nothing on this page assumes it. | An implementing bill, if one is introduced. Until then every farm-type cost analysis of it — and there are several in circulation — is an analysis of a proposal, generally at rates and without the basic deduction that the agreement actually specifies. |
| **The *bemærkninger* to LOV 759** | Not read. The enacted text was read — §§6, 11, 57 and 65 are quoted from Lovtidende — but the explanatory remarks, which is where the modelling behind the quota is described, were not. | Reading the bill's remarks. |
| **Whether the voluntary conversion programme is delivering at the rate its targets require** | Not established here. Section 6 predicts who should decline the offer; it does not measure whether they have. | The *tilsagn* registers, and the agency's own area accounting against the 250,000 ha afforestation and 140,000 ha lowland targets. |

### The one finding that would need a name, stated without one

The highest-density holdings in the register are extreme: {d['types']['poultry']['p90']:.1f}
animal units per declared hectare at the 90th percentile for poultry, and a national
99th percentile far above any density that could be an operating farm. A handful are, on
the face of it, businesses running thousands of animal units against a single declared
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
   cereals, maize, rape and pulses, set per coastal catchment, with step changes at 30
   and 80 kg of manure nitrogen per hectare and a flat 170 kg N/ha ceiling. The animal
   unit has had no legal force since 2017 and the cattle derogation lapsed in 2024.
2. **Dairy is the most exposed enterprise type, and not because of density.**
   {d['types']['dairy']['over']['0.8']:.0f}% of dairy holdings that declare land sit
   above the higher manure threshold (n={d['types']['dairy']['n_ratio']:,}), where three
   requirements step up at once — and only
   {share(d['hectares']['base']['dairy'].get('in base', 0), sum(d['hectares']['base']['dairy'].values())):.0f}%
   of dairy's hectares are on holdings whose largest crop is inside the base area the
   percentage is charged on. Largest load, smallest base. The technical basis for the
   regulation says the same thing in its own words.
3. **The exposure ranking and the fragility ranking are different rankings.** Dairy is
   the most exposed and the most solvent — {d['cohorts']['dairy']['pct_loss']:.0f}%
   loss-making, n={d['cohorts']['dairy']['n_profit']}. Beef and other cattle are the
   least exposed and the least solvent —
   {d['cohorts']['beef / other cattle']['pct_loss']:.0f}%, n={d['cohorts']['beef / other cattle']['n_profit']}.
   Any account that treats "hit hardest" as one quantity is wrong about one of them.
4. **No allocation model rescues cattle.** Across the six quota-allocation models in the
   published technical basis, cattle loses between 969 and 1,207 kroner per hectare — a
   spread of a fifth — while specialised arable moves by 71% of its own much smaller
   loss. The model choice the industry is arguing about changes arable's position and
   barely changes cattle's. Trading would; whether it exists is not established.
5. **The unit the charge is denominated in swaps which sector is thinnest.** Per hectare
   the thinnest is **beef** ({f0(d['shock']['beef / other cattle']['break_even_median'])}
   kr/ha against {f0(d['shock']['pigs']['break_even_median'])} for pigs); per animal
   unit it is **pigs** ({f0(d['shock_de']['pigs']['break_even_median'])} kr/DE against
   {f0(d['shock_de']['beef / other cattle']['break_even_median'])} for beef). Dairy is
   most resilient on both.
6. **The landless holding is invisible to the instrument and is where its cost lands**,
   through a slurry placement contract that no register records. It is also the sicker
   half of its own sector: {d['shock_de']['pigs']['pct_loss_landless']:.0f}% of landless
   pig holdings with accounts made a loss last year against
   {d['shock_de']['pigs']['pct_loss_with_land']:.0f}% of those with land.
7. **The mandatory allocation for 2026/2027 is not where the animals are.** Twenty
   catchments carry it, several on Zealand and the islands, and three of the four at the
   34.5% ceiling are on the islands — in the region holding
   {share(d['regions']['Region Sjælland']['de'], d['total_de']):.1f}% of the national
   herd at a median of {d['regions']['Region Sjælland']['med']:.2f} DE/ha. A percentage
   of a large base area on holdings with no manure is a real cost, and it falls on the
   population this page has no balance sheets for.
8. **The voluntary offer is worth least to the holdings whose land carries the most
   nitrogen.** Permanent extensification pays a one-off 82,500 kr/ha for rotation land
   in a priority area. That is about {82500/d['shock']['dairy']['break_even_median']:.0f}
   years of the median dairy hectare's profit and about
   {35500/d['shock']['beef / other cattle']['break_even_median']:.0f} years of the median
   beef hectare's at the grass rate. The engine buys extensive land cheaply and
   intensive land not at all — and a land-squeezed dairy holding that sells a hectare
   moves *up* against its own manure thresholds. That is a falsifiable prediction about
   uptake, not an observation.
9. **The act that takes over in 2027 permits quotas to be transferred, and the terms are
   not public.** LOV 759 §6 stk. 4 creates the power; the implementing regulation would
   set the terms; transfer is worth about a quarter of cattle's modelled loss. It also
   carries two expropriation powers, one of them not limited to this act's own measures.
10. **Four fifths of Danish farmland is farmed by businesses that publish nothing.** The
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
coverage of it: LOV nr. 759 af 8. september 2026 (§§6, 11, 57, 65), BEK 931/2024 (§14),
BEK 673/2026 (§§4, 24 and Annexes 1–2), BEK 677/2026 (§§1, 3, 6 and Annex 1) and
BEK 130/2026 (§18), all from
[retsinformation.dk](https://www.retsinformation.dk); and the NUAR figures from the
report itself. Where this page says something is not established, it means the document
was not obtained — not that it was skimmed.*
"""


def main():
    d = compute()
    v = d["visibility"]
    ekm = v["by_form"].get("Enkeltmandsvirksomhed", {"n": 0, "de": 0.0})
    doc = "".join([
        HEAD,
        PRIVACY.format(
            n_animal_form_ekm=sum(e["n"] for k, e in v["by_form"].items()
                                  if k != "(not in the CVR extract)"),
            n_ekm=ekm["n"],
            pct_ekm_de=f"{share(ekm['de'], v['total_de']):.0f}%"),
        POLICY,
        sec_visible(d),
        sec_types(d),
        sec_place(d),
        sec_hectares(d),
        sec_money(d),
        sec_gaps(d),
    ])
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(doc)
    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    log(f"  wrote {OUT_MD} ({len(doc):,} chars)")
    log(f"  wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
