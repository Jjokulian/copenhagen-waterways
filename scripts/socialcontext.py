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

from common import DERIVED, ROOT, log, write_doc
import live

SIBLING = os.environ.get(
    "DANISH_LIVESTOCK",
    os.path.join(os.path.dirname(ROOT), "danish-livestock", "data"))

OUT_MD = os.path.join(ROOT, "docs", "INCIDENCE.md")
OUT_JSON = os.path.join(DERIVED, "socialcontext.json")
DOCS_JSON = os.path.join(DERIVED, "farm_documents.json")   # scripts/farm_documents.py
DOC = None           # the pinned-document figures, read live by render()

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

# Values the page prints that are chosen rather than measured. Each is written into
# socialcontext.json under "params", so the page reads it live, and is declared as
# stipulated in data/manual/number_constructions.d/farm.json.
N_PER_DE_KG = 100                   # the stated conversion above: kg N per animal unit
SURPLUS_LINE = HISTORIC_LIMITS[0]   # the surplus is measured above the old harmony density
THIN_EQUITY_RATIO = 0.20            # below this equity ratio a balance sheet is "thin"
MIN_KOMMUNE_HOLDINGS = 100          # a kommune enters the density table with this many


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


def at(values, v):
    """The live element of a stored list equal to v - a ladder step, printed live."""
    return next(x for x in values if x == v)


def share(n, d):
    # n first: 100.0 * n would call float.__mul__ and drop a live number's chain
    return n * 100.0 / d if d else float("nan")


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
    # a register label with a digit in it is an identifier, not a quantity
    code = lambda x: f"`{x}`" if any(ch.isdigit() for ch in x) else x
    return f"{code(name)} — *{code(en)}*" if en else code(name)


# BEK 677/2026 Bilag 1, NUAR Tabel 7.5 and the BEK 130/2026 section 18 rates used to be
# transcribed here as literals. They are now read from the pinned texts by
# scripts/farm_documents.py into data/derived/farm_documents.json, which render()
# reads live; the parsed tables were checked against these transcriptions before
# they were removed, and agreed in every cell.

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
            # SURPLUS_LINE, by name: LIMITS[0] was 1.4 until the current thresholds
            # were put in front of it, after which this silently measured the
            # surplus above 0.3 while the page still said 1.4
            s = d - SURPLUS_LINE * ha
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
            e["over14"] = share(sum(1 for x in v if x > HISTORIC_LIMITS[0]), len(v))
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
        e["over14"] = share(sum(1 for x in v if x > HISTORIC_LIMITS[0]), len(v))
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
                conc[str(m)] = {"level": m, "holdings": i + 1,
                                "pct_of_holdings": share(i + 1, len(herd))}
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
        cells[r["type"]][(exposed(r), r["equity_ratio"] < THIN_EQUITY_RATIO)] += 1
    both = [r for r in rows if exposed(r) and r["equity_ratio"] < THIN_EQUITY_RATIO]
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
        "params": {
            "n_per_de_kg": N_PER_DE_KG,
            "reg_thresholds_de_ha": list(REG_THRESHOLDS),
            "historic_limits_de_ha": list(HISTORIC_LIMITS),
            "surplus_line_de_ha": SURPLUS_LINE,
            "thin_equity_ratio": THIN_EQUITY_RATIO,
            "min_kommune_holdings": MIN_KOMMUNE_HOLDINGS,
            "shock_ha_kr": list(SHOCK_HA),
            "shock_de_kr": list(SHOCK_DE),
        },
    }




# ------------------------------------------------------------------- the document
#
# Every paragraph that asserts something is a checked claim (live.claim, registered
# in data/manual/claims.d/w2-in.json). Nothing on the page quotes this page's own
# past: what could not be justified was retired to docs/ARCHIVE.md.

B, E = live.claim_begin, live.CLAIM_END


def C(cid, text):
    return live.claim(cid, text)


_CD, _CC = [], {}


def R(ph):
    """A reading from a pinned document, through the claims register - {read:} or
    {count:} - so a figure a regulation or an article states is read, not typed."""
    import claims
    if not _CD:
        _CD.append(claims.load()[0])
    return claims.resolve(_CD[0], ph, _CC)[0]


def f0(x):
    return "—" if x != x else f"{x:,.0f}"


def f2(x):
    return "—" if x != x else f"{x:,.2f}"


def pct(x, dp=1):
    return "—" if x != x else f"{x:.{dp}f}%"


def head():
    return f"""# Who pays for the nitrogen requirement

*{C("C-IN-SCOPE", "The economic incidence of Denmark's nitrogen requirement — the rules in force now and the discharge quota coming in 2027 — computed on the open registers and on the regulations themselves. Cohorts and distributions only: no holding is named here, and the generator writes no identifying field.")}*

Two other pages on this site argue about whether the requirement is well founded.
[LANDBRUG.md](LANDBRUG.md) puts that case in Danish to the people it lands on, and
[NITROGEN.md](NITROGEN.md) takes the national figure apart. {C("C-IN-QUESTION", "**This page assumes the requirement and asks a different question: it is law, so whose farm does it land on, and which farms have nothing left to absorb it with?**")}

{B("C-IN-SUMMARY")}Those are separable questions, and the answer to the first is not the answer to the
second. The enterprise type under the most regulatory pressure — dairy — is also the
one with the fewest loss-makers and the fewest negative-equity balance sheets in the
accounts that exist. The type with the weakest income — beef and other cattle, with the
highest loss rate of the farming types — is the least pressured of the cattle. And at
the threshold the rules turn on, most of the sector is on the exposed side of the line,
so the interesting question is not *who is exposed* but **which of the exposed have
anything left**. That is a countable set and section 6 counts it.{E}

{B("C-IN-NOANIMALS-HEAD")}The single thing most worth knowing before reading further is that **the Danish rules
do not count animals.** The animal unit is not a unit in the regulations that carry the
current requirements. What they are charged on is a *base area* of cereals, maize, rape
and pulses — and grass is not in it. That one fact reorders the whole incidence question,
and it is why a page about a nitrogen rule spends as much time on what a farm grows as
on what it keeps.{E}

> {C("C-IN-NOTFORECAST", "**What this page is not.** It is not a forecast of who will go bankrupt. What is computed is the **buffer** — how large an annual loss of margin each cohort could absorb before it goes negative — expressed in kroner per hectare and per animal unit, so that a reader with a different cost estimate can apply their own. One published by-farm-type cost estimate is then laid on that ladder, read from the primary source and quoted with its table.")}
"""


def privacy(v):
    ekm = v["by_form"].get("Enkeltmandsvirksomhed", {"n": 0, "de": 0.0})
    n_form = sum(e["n"] for k, e in v["by_form"].items() if k != "(not in the CVR extract)")
    return f"""
## 0. Why there are no names on this page

{C("C-IN-PUBLIC", "Every register underneath this analysis is public. Anyone can look up a CVR number, read the filed accounts, see the animal units and the declared hectares, and work out what this page works out for one named business.")}

{C("C-IN-NONAMES", "This page does not do that, and the rule is not negotiable.")}

{B("C-IN-PERSONS")}**Most businesses keeping animals are natural persons.** `Enkeltmandsvirksomhed` — sole
proprietorship — is not a company with limited liability and a boardroom; it is one
human being, and the CVR register carries the business's name, address and telephone
number, which for a sole trader are the person's own. Of the {n_form:,} businesses keeping
animals whose legal form this project could read, {ekm['n']:,} are sole proprietorships,
and they hold {share(ekm['de'], v['total_de']):.0f}% of the national herd.{E}

{B("C-IN-WHY-NO-NAMES")}Publishing *these named people are going to lose the farm* is a financial prediction
about a private individual, made from a model, in public, with their address attached.
It would be wrong even if the model were good, and the model here is a distribution
rather than a diagnosis: it can say what fraction of a cohort has no buffer left, and
it cannot say which member of that cohort is the one whose bank has already agreed a
standstill.{E}

{B("C-IN-COHORTS")}So everything below is a cohort with its **n** stated. A farmer reading this can find
their own holding in the distribution — that is the point of stating the deciles — and
nobody can find anyone else's. *Where a finding would genuinely need a name to be
checked, it is stated without one and the check is named instead.* There is one such
finding, in [section 7](#7-what-this-cannot-establish-and-what-would).{E}
"""


def policy(d):
    b931, b673, P = DOC["bek931"], DOC["bek673"], d["params"]
    h = P["historic_limits_de_ha"]
    ns = nuar_stats()
    vote = (R("{read:POL-TV2-20260903:119|119 medlemmer af Folketinget stemte for loven}") + "–"
            + R("{read:POL-TV2-20260903:34|mens 34 stemte imod}"))
    n931 = R("{count:BEK931-2024:dyreenhed}")
    n673 = R("{count:BEK673-2026:dyreenhed}")
    n677 = R("{count:BEK677-2026:dyreenhed}")
    cut = (1 - b931["ceiling_kg_n_ha"] / b931["derogation_kg_n_ha"]) * 100
    more = (b673["quota_cut_above_kg_n_ha"] / b673["quota_cut_below_kg_n_ha"] - 1) * 100
    return f"""
## 1. What the instrument is, and what that alone tells you about incidence

{B("C-IN-RECORDS")}Two records are needed here and they are different in kind. The *political* record —
what was agreed, by whom, and what was said about it — is collected, dated and sourced
in [POLITICS.md](POLITICS.md). The *legal* record is the regulations in force for the
current planning year, and those were read directly for this page rather than taken
from press coverage: every provision cited below is in a text pinned by its hash.{E}

| When | What | Status |
|---|---|---|
| 2024-06-24 | {C("C-IN-T-TREPART", "**Grøn Trepart** — the Green Tripartite agreement")} | aftale |
| 2024-07-31 | {C("C-IN-T-DEROG", f"The **kvægundtagelse** — the permission to apply {b931['derogation_kg_n_ha']} kg N/ha — ends: BEK 931 takes effect the next day with one ceiling")} | expiry |
| 2025-06-19 | {C("C-IN-T-PARTIAL", "A partial agreement on the coming nitrogen regulation")} | aftale |
| 2025-12-03 | {C("C-IN-T-AFTALE", "The **kvælstofaftale** — the nitrogen agreement and its distribution model")} | aftale |
| 2026-07-21 | {C("C-IN-T-BEK", "**BEK 673** and **BEK 677** — the catch-crop rules for planning year 2026/2027")} | gældende ret |
| 2026-09-03 | {C("C-IN-T-L5", f"**`L 5`** passed {vote}, becoming **LOV nr. 759 of 2026-09-08**, the new *gødskningslov*. In force **2027-01-01**")} | vedtaget lov |
| by 2026-09-03 | {C("C-IN-T-TILLAEG", "A *tillægsaftale* that, as Venstre described it, secured an exception for vegetable producers")} | aftale |

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

{B("C-IN-NOANIMALS")}**The Danish nitrogen rules in force do not count animals.** The word `dyreenhed` —
animal unit — occurs {n931} times in BEK 931 of 2024-07-16 on the use of fertiliser, and
{n673} and {n677} times in BEK 673 and BEK 677 of 2026-07-21 on catch crops: the three
regulations that carry the current requirements. The ceiling they set is in kilograms of
nitrogen per hectare, and the {h[0]}, {h[1]} and {h[2]} DE/ha harmony densities used
elsewhere on this site are not in them. The texts are pinned, and the count is made on
them each time this page is built.{E}

{C("C-IN-FOUR", f"The current rules carry four separate requirements. Two of them turn on thresholds of {b673['threshold_low_kg_n_ha']} and {b673['threshold_high_kg_n_ha']} kilograms of nitrogen per hectare of *harmoniareal*, from manure and other organic fertiliser, and the quota-reduction alternative is priced on the higher one.")}

| Requirement | The rule | Source |
|---|---|---|
| **Manure ceiling** | {C("C-IN-R-CEIL", f"Total organic nitrogen divided by **{b931['ceiling_kg_n_ha']} kg N/ha** may not exceed the harmoniareal. One rate, no derogation.")} | [BEK 931/2024 §14](https://www.retsinformation.dk/eli/lta/2024/931) |
| **Compulsory catch crops** | {C("C-IN-R-CC", f"At least **{b673['catch_crop_pct']:g}%** of the base area — but **{b673['catch_crop_pct_high']:g}%** for a holding applying **{b673['threshold_high_kg_n_ha']} kg N/ha or more**")} | [BEK 673/2026 §4 stk. 3](https://www.retsinformation.dk/eli/lta/2026/673) |
| **Livestock catch crops** | {C("C-IN-R-LIVE", f"An additional requirement, per catchment, for any holding applying **{b673['threshold_low_kg_n_ha']} kg N/ha or more**. Organic holdings are exempt from this one")} | BEK 673/2026 §4 stk. 4 and stk. 5, Bilag 2 |
| **Targeted catch crops** | {C("C-IN-R-TARGET", "A further percentage of the base area, **set per coastal catchment**")} | [BEK 677/2026 §3 stk. 2](https://www.retsinformation.dk/eli/lta/2026/677), Bilag 1 |

{C("C-IN-B677-WORDS", "The statutory wording of the last one is the allocation mechanism in one sentence:")}

> *"Arealet med målrettede efterafgrøder skal udgøre en procentdel af den del af
> virksomhedens efterafgrødegrundareal, der er beliggende i det pågældende
> kystvandopland. Procentdelen for de enkelte kystvandoplande er fastsat i bilag 1."*
>
> *(The area of targeted catch crops shall constitute a percentage of that part of the
> holding's base area which lies in the coastal catchment in question. The percentage
> for each coastal catchment is set in Annex 1.)*

{B("C-IN-ID15")}So: **a percentage, of a base area, per coastal catchment.** Not per animal, not per
kilogram of nitrogen, and not per ID15 catchment. The ID15 areas do two narrower jobs: a
field is assigned whole to the ID15 area it most overlaps and thence to that ID15's
coastal catchment (§6 stk. 2), and in the voluntary subsidised round the ID15 retention
is what ranks applications, *"[m]arker i et ID15-område med lavere retention går forud
for marker i et ID15-område med højere retention"*
([BEK 131/2026](https://www.retsinformation.dk/eli/lta/2026/131) §6 stk. 3).{E}

{B("C-IN-ESCAPE")}**The escape valve is priced against livestock too.** A holding may substitute a cut in
its own nitrogen quota for catch crops, and the exchange rate depends on the same
{b673['threshold_high_kg_n_ha']} kg N/ha line: **{b673['quota_cut_below_kg_n_ha']} kg N per hectare below it, {b673['quota_cut_above_kg_n_ha']} kg N above** (BEK 673/2026 §24
stk. 2). The alternative costs a holding above the line {more:.0f}% more per hectare
than one below it.{E}

{B("C-IN-DEROG")}**And the cattle derogation is gone.** The *kvægundtagelse* let qualifying holdings apply
{b931['derogation_kg_n_ha']} kg N/ha under the order BEK 931 repealed. BEK 931 took effect on 2024-08-01 with
one ceiling of {b931['ceiling_kg_n_ha']}; its transitional provision keeps the old conditions for holdings that
held the permission, not the permission itself. Those holdings dropped to {b931['ceiling_kg_n_ha']} — a
**{cut:.0f}% cut in what may be spread**, already delivered before `L 5` was passed. Any
account of the burden on Danish dairy that starts in 2026 has missed that step.{E}

### Two exemptions that decide a great deal

{B("C-IN-EXEMPT")}BEK 677/2026 §1 stk. 3 exempts a holding from the targeted requirement entirely if it
has a base area under {DOC['bek677']['min_base_ha']} hectares, **or if it was certified for organic production, or
had applied to be, on 2026-02-01**. BEK 673/2026 §4 stk. 5 exempts organic
holdings from the livestock catch-crop requirement as well.{E}

{C("C-IN-EXEMPT-WEIGHT", "That is not a marginal advantage of the kind arithmetic produces. It is a statutory exemption from two of the four instruments, and [section 4](#4-where-it-lands-and-on-whom) measures how many cattle holdings and animal units carry an organic flag.")}

### The law that takes over in 2027, and the thing in it that changes everything

{B("C-IN-LOV759")}The act passed on 2026-09-03 is **LOV nr. 759 of 2026-09-08, *Lov om
bæredygtig forvaltning af næringsstoffer og drivhusgasser m.v. i land- og skovbruget***
([Lovtidende text](https://www.retsinformation.dk/eli/lta/2026/759/dan/pdf)). The
provisions below that decide incidence are quoted from that text, which is pinned.{E}

{B("C-IN-NOTYET")}**It does not apply yet, and that is why this page is about catch crops.** §57 puts it
in force on 2027-01-01 and repeals the old fertiliser act; §57 stk. 3 then says the
act *"finder ikke anvendelse på forhold, der vedrører planperioden 2019-2020 til og med
planperioden 2026-2027"* — for those, *"finder de hidtil gældende regler anvendelse"*.
So the requirements measured in section 3 through section 5 are the ones that bind this
year, and the new act governs from the planning period after it.{E}

{B("C-IN-FRAMEWORK")}**It is a framework act, so the numbers are not in it.** §6 stk. 2 empowers the minister
to set *"nærmere regler om udvaskningsgrænser og udledningskvoter og virkemidler til
opfyldelse heraf"*. Everything that decides a holding's position — the limits, the
quota, the conversion from leaching to discharge — is delegated to implementing
regulations. **This project has not verified that those have been issued.**{E}

{C("C-IN-TRANSFER", "**And discharge quotas may be made transferable.** §6 stk. 4, last sentence:")}

> *"Ministeren kan endvidere fastsætte regler om overdragelse af udledningskvoter,
> herunder betingelser for overdragelse for at sikre den forudsatte miljøeffekt."*
>
> *(The minister may further set rules on the transfer of discharge quotas, including
> conditions for transfer so as to secure the presupposed environmental effect.)*

{B("C-IN-TRANSFER-TERMS")}That is the statutory power, and it is enacted. What it does **not** settle is the
terms: who may sell to whom, whether transfer is bounded within a catchment, and at what
price. Those would be in an implementing regulation this project has not found. So the
honest statement is: **the act creates the power to permit transfer; the terms are not
verified here.** That matters because, as the block below shows, transfer is worth
{ns['trade']:.0f}% of cattle's modelled loss.{E}

{B("C-IN-EXPROP")}**The state can also simply take the land.** §11 gives a power of expropriation to carry
out measures under the act, with *"fuldstændig erstatning"* — full compensation — where
the intervention is expropriatory. §65 inserts a second, wider power into the CAP
administration act: the minister or the municipal council *"kan ekspropriere
landbrugsarealer, hvis det er af væsentlig betydning at råde over disse arealer for at
gennemføre foranstaltninger, som iværksættes for at forbedre klimaet til opfyldelse af
bindende målsætninger i lov om klima"*, with one carve-out — the first subsection *"kan ikke anvendes
til at fremme statslig skovtilplantning"*.{E} {C("C-IN-OFFER", "A voluntary programme with a compulsory floor under it is a different offer from a voluntary programme without one, and section 6's argument about who takes the money should be read with that in mind.")}

<details class="work">
<summary>{C("C-IN-TRADE-SUM", "Trading is priced in the model's own technical basis, and the group that would gain most from it is cattle — which is why the unread implementing regulation is the most load-bearing document on this page")}</summary>

{B("C-IN-NUAR-TRADE")}The DCA/AU **NUAR** report, the technical basis for the discharge-based model, models
trading explicitly and finds that **cattle holdings are the largest gainers from it**:
*"kvægbrugene er også dem med de største gevinster med handel"*. In its Hjarbæk Fjord
table the cattle loss narrows from {ns['rodz']:,} kr/ha under the root-zone model to
{ns['hrodz']:,} once trading is allowed.{E}

{B("C-IN-TRADE-WHY")}So the trading question is not a technicality about market design. It is the difference
between the sector that carries the largest loss carrying {ns['trade']:.0f}% less of it.
The statute permits the minister to allow transfer; the regulation that would say on
what terms is the single document whose absence most changes this page's conclusions,
and it is in the list in [section 7](#7-what-this-cannot-establish-and-what-would).{E}
</details>

### Three channels, with opposite incidence

| Channel | Binds on | Falls hardest on |
|---|---|---|
| **The catch-crop percentage** | the base area — cereals, maize, rape, pulses | {C("C-IN-CH-CC", "holdings whose land is mostly in those crops, and holdings whose base area is small relative to their manure")} |
| **The manure ceiling and the two thresholds** | the slurry, which is not optional, because the animals exist | {C("C-IN-CH-MANURE", f"holdings applying over {b673['threshold_high_kg_n_ha']} kg N/ha, where the compulsory percentage and the quota-cut price both step up")} |
| **Land conversion and the set-aside ceiling** | the hectare itself | {C("C-IN-CH-LAND", "whoever *owns* lowland in a catchment where the land is wanted")} |

{B("C-IN-CHANNELS-MEAS")}The second channel is the one this project can measure directly, because both halves of
it are in open registers that join on the company number. The first can now be measured
too, imperfectly, and [section 3](#3-the-base-area-is-the-thing-cattle-has-least-of)
does it. The third cannot be measured here at all, because ownership is not in the
registers fetched.{E}
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
    two = v["by_form"]["Enkeltmandsvirksomhed"]["n"] + v["by_form"]["Interessentskab"]["n"]
    n_form = sum(e["n"] for k, e in v["by_form"].items() if k != "(not in the CVR extract)")
    return f"""
## 2. Before anything else: {share(acc['False']['de'], v['total_de']):.0f}% of the herd keeps no public accounts

{B("C-IN-VIS-WHY")}The second level of this page — which holdings have no buffer — can only be asked of holdings
that publish a balance sheet. That is a much smaller and much stranger set than
"Danish farming", and the size of the gap has to be established first, because
everything downstream inherits it.{E}

{B("C-IN-FILING")}Denmark's filing duty follows the legal form. A limited company (`Anpartsselskab`,
ApS) or a public company (`Aktieselskab`, A/S) must file an annual report, and it is
published in full and machine-readable. A sole proprietorship
(`Enkeltmandsvirksomhed`) and, in the ordinary case, a partnership
(`Interessentskab`, I/S) has no duty to publish one. Of the {n_form:,} businesses keeping
animals whose legal form could be read, {two:,} are one of those two kinds.{E}

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

{B("C-IN-GAP")}**{share(acc['False']['de'], v['total_de']):.0f}% of the Danish herd and
{share(ha_acc['False']['ha'], h['total_ha']):.0f}% of the declared Danish farmland is
operated by a business whose finances are not public.** No amount of care with the
{acc['True']['n']:,} filings that do exist changes that. It is not a sampling problem
that a larger fetch would fix; it follows from who has to file.{E}

{B("C-IN-BIAS")}*What the visible end is biased towards.* The incorporated businesses are the large
ones — mean {v['by_form']['Anpartsselskab']['de']/v['by_form']['Anpartsselskab']['n']:,.0f}
animal units for an ApS and
{v['by_form']['Aktieselskab']['de']/v['by_form']['Aktieselskab']['n']:,.0f} for an A/S,
against {v['by_form']['Enkeltmandsvirksomhed']['de']/v['by_form']['Enkeltmandsvirksomhed']['n']:,.0f}
for a sole proprietorship. So section 6 is not a picture of Danish farming under
stress. **It is a picture of the largest {share(acc['True']['de'], v['total_de']):.0f}% of it by herd**, and
nothing here shows the unfiled remainder to be in better or worse condition. Every
fragility figure in section 6 describes the filers only.{E}

<details class="work">
<summary>{C("C-IN-CONC-SUM", f"The herd is concentrated enough that a quota binding on animals binds on few addressees — {conc['0.5']['holdings']:,} of them hold {conc['0.5']['level'] * 100:.0f}% of it")}</summary>

Over the {v['n_with_herd']:,} businesses with a non-zero animal-unit count:

| | Holdings | Share of holdings |
|---|---:|---:|
| Hold {conc['0.25']['level'] * 100:.0f}% of the national herd | {conc['0.25']['holdings']:,} | {conc['0.25']['pct_of_holdings']:.1f}% |
| Hold {conc['0.5']['level'] * 100:.0f}% | {conc['0.5']['holdings']:,} | {conc['0.5']['pct_of_holdings']:.1f}% |
| Hold {conc['0.75']['level'] * 100:.0f}% | {conc['0.75']['holdings']:,} | {conc['0.75']['pct_of_holdings']:.1f}% |
| Hold {conc['0.9']['level'] * 100:.0f}% | {conc['0.9']['holdings']:,} | {conc['0.9']['pct_of_holdings']:.1f}% |

{C("C-IN-HERDDIST", f"Median holding: {v['median_de']:,.1f} DE. 90th percentile: {v['p90_de']:,.0f}. 99th: {v['p99_de']:,.0f}.")}

{B("C-IN-LANDCONC")}Land is concentrated too, though less so: the largest
{h['cvrs_holding_half_the_land']:,} of {h['n_cvr']:,} land-declaring businesses
({share(h['cvrs_holding_half_the_land'], h['n_cvr']):.1f}%) declare half the hectares,
and the median declaration is {h['median_ha']:.1f} ha against a 99th percentile of
{h['p99_ha']:,.0f}.{E}

{B("C-IN-CONC-IMPL")}This cuts both ways for the argument. It means an instrument aimed at the herd has a
small number of addressees, which makes it administrable and makes compensation
cheap to target. It also means the median animal-keeping business in Denmark is a
{v['median_de']:,.0f}-animal-unit holding that is almost invisible in any
herd-weighted average — including several in this document, which is why counts of
holdings are printed beside every share of the herd.{E}
</details>
"""


def sec_types(d):
    t = d["types"]
    h = d["hectares"]
    b673, P = DOC["bek673"], d["params"]
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

{C("C-IN-S3-INTRO", f"Section 1 established that the requirement is *a percentage of the base area* and that the compulsory percentage and the quota-cut price both step up at {b673['threshold_high_kg_n_ha']} kg of manure nitrogen per hectare. Both halves of that can be measured, imperfectly, on the open registers — and together they locate the burden somewhere a stocking-density table does not.")}

### Where the holdings sit relative to the thresholds the rules use

{C("C-IN-CONVERSION", f"The registers carry animal units, not kilograms of nitrogen, so the two lines below are placed by a **stated conversion of {P['n_per_de_kg']} kg N per animal unit** and are indicative rather than a test. They locate roughly where a holding crosses from one regulatory band into the next; they do not establish that any particular holding does.")}

| Enterprise type | Holdings | Animal units | Share of herd | With land | Median DE/ha | ≈{b673['threshold_low_kg_n_ha']} kg N/ha | ≈{b673['threshold_high_kg_n_ha']} kg N/ha | {P['historic_limits_de_ha'][0]} (historic) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{rows}

{B("C-IN-DAIRY-OVER")}**{t['dairy']['over']['0.8']:.0f}% of dairy holdings that declare land sit above the
higher of the two thresholds**, against {t['pigs']['over']['0.8']:.0f}% of pig holdings
and {t['beef / other cattle']['over']['0.8']:.0f}% of beef. Above that line two things change at once: the
compulsory catch-crop percentage rises from {b673['catch_crop_pct']:g}% to {b673['catch_crop_pct_high']:g}%, and the
quota-reduction escape valve reprices from {b673['quota_cut_below_kg_n_ha']} to {b673['quota_cut_above_kg_n_ha']} kg N per hectare — on top of
the livestock catch-crop requirement that already applies from {b673['threshold_low_kg_n_ha']}. **The instrument does not
tighten gradually with density. It steps, and dairy is almost entirely on the far side
of the step.**{E}

### And the base it is charged against

{B("C-IN-BASE-DEF")}Here is the part that a density table cannot see. The percentages are charged on the
*efterafgrødegrundareal*, and BEK 673/2026 Bilag 1 defines that as cereals, rape,
**maize**, rybs, soya, mustard, peas, field beans, sunflower, oil flax and other annual
crops with no autumn nitrogen uptake. **Grass is not on the list.**{E}

{C("C-IN-BASE-METHOD", "Classifying each business by its largest declared crop:")}

| Operator of the declared hectares | Declared hectares | Largest crop inside the base | Outside it | Unclassified |
|---|---:|---:|---:|---:|
{brows}

{B("C-IN-DAIRY-BASE")}**{share(dbase.get('in base', 0), sum(dbase.values())):.0f}% of dairy's declared
hectares are on holdings whose largest crop is inside the base area, against
{share(pbase.get('in base', 0), sum(pbase.values())):.0f}% of pigs'.** Dairy grows
grass. Grass is not in the base. So the dairy holding carries the largest manure surplus,
sits above the higher threshold, and then has to find its catch-crop percentage out of
the fraction of its rotation that is cereals and maize.{E}

{C("C-IN-NUAR-MECH", "The technical basis for the new regulation states the same mechanism in its own words. The DCA/Aarhus University **NUAR** report — the analysis behind the discharge-based model — puts it this way:")}

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
> [the report](https://pure.au.dk/ws/portalfiles/portal/379114234/NUAR-slutnotat_24._maj_2024.pdf)

{C("C-IN-TWO-ROUTES", "Two independent routes to the same conclusion: the register says dairy's base area is small, and the report names a smaller base area, with a larger discharge, as what sets cattle apart.")}

{B("C-IN-BASE-LIMIT")}*What this does not establish.* The classification uses each business's **largest**
declared crop, because that is all the summary register carries. A dairy holding whose
largest crop is grass can have cereal area too, and a pig holding whose largest crop is
a cereal can have grass, so the classification can overstate the gap between them by an
amount not measured here. The full parcel-level crop declaration would settle it and is
in a register already fetched — see
[section 7](#7-what-this-cannot-establish-and-what-would).{E}

### The shed with no field, and the field that is too small

The second channel — manure that has nowhere to go — splits the herd a different way:

| Enterprise type | Surplus DE above {P['surplus_line_de_ha']}/ha | Holdings | DE on holdings declaring no land | Holdings | Share of that type's herd |
|---|---:|---:|---:|---:|---:|
{sur}

{B("C-IN-SURPLUS")}Nationally that is **{tot_sur:,.0f} animal units in surplus on {n_sur:,} holdings and a
further {tot_land:,.0f} on {n_land:,} holdings with no declared land at all** —
together {share(tot_sur + tot_land, d['total_de']):.0f}% of the Danish herd standing on
more animal units than its own declared ground would take at the historic harmony
density. That is a measure of pressure and not a finding of non-compliance; the
qualification at the end of this section says why.{E}

And the two halves belong to different animals.

* {C("C-IN-DAIRY-SQUEEZE", f"**Dairy is land-squeezed.** {t['dairy']['n_surplus']:,} dairy holdings carry {t['dairy']['surplus']:,.0f} surplus animal units — the largest surplus of any type — but only {t['dairy']['n_landless']:,} declare no land. The dairy holding has fields; it has more animal units than the historic density allows on them, and most of its land outside the base.")}
* {C("C-IN-PIGS-LANDLESS", f"**The landless herd is mostly pigs.** {t['pigs']['n_landless']:,} pig holdings hold {t['pigs']['landless_de']:,.0f} animal units with no declared hectare underneath them at all — {t['pigs']['landless_de'] / t['pigs']['surplus']:.1f} times the surplus carried by the {t['pigs']['n_surplus']:,} pig holdings that do declare land, and {share(t['pigs']['landless_de'], tot_land):.0f}% of all landless animal units.")}

{B("C-IN-CONTRACT-MECH")}That distinction decides who a percentage-of-base-area instrument reaches. A
land-squeezed holding is *inside* it: it has a base area and the percentage is charged
on it. A landless holding is **outside** — it has no base area to charge, and its manure
has to go onto somebody else's harmoniareal or be dealt with another way. Tighten the
receiving farm's requirement and the price of that placement moves. The landless unit
is where that cost lands, and it lands there without the unit ever appearing in a
per-hectare table.{E}

{C("C-IN-CONTRACTS-PRIVATE", "**Those placement contracts are not public.** They are not in the CVR register, not in the field-parcel register and not in the livestock register, and they are private contracts rather than a missing dataset — so no fetch fixes it.")}

{B("C-IN-SEC3-LIMITS")}*What this does not establish.* Declared area is land declared for area support, which
is neither the *harmoniareal* the manure thresholds are measured against nor the
*efterafgrødegrundareal* the percentages are charged on: land a holding uses without
declaring it is missing, and a business buying spreading capacity from a neighbour looks
land-poor here and is compliant in law. The {P['historic_limits_de_ha'][0]} DE/ha column is the historic
harmony density, kept only for continuity with [NITROGEN.md](NITROGEN.md); it has no
legal force. And the ≈{b673['threshold_low_kg_n_ha']} and ≈{b673['threshold_high_kg_n_ha']} columns rest on the stated
{P['n_per_de_kg']} kg N per animal unit conversion, which this page has not verified.{E}
"""


def sec_place(d):
    reg = sorted(d["regions"].items(), key=lambda x: -x[1]["de"])
    rrows = "\n".join(
        f"| {k} | {e['n']:,} | {e['de']:,.0f} | {share(e['de'], d['total_de']):.1f}% "
        f"| {e['n_ratio']:,} | {e['med']:.2f} | {e['over14']:.0f}% |" for k, e in reg)
    dense = sorted([x for x in d["kommuner"].items() if x[1]["n_ratio"] >= MIN_KOMMUNE_HOLDINGS],
                   key=lambda x: -x[1]["med"])[:12]
    krows = "\n".join(
        f"| {k} | {e['region'].replace('Region ', '')} | {e['n_ratio']:,} "
        f"| **{e['med']:.2f}** | {e['over14']:.0f}% | {e['de']:,.0f} |" for k, e in dense)
    west = ("Region Syddanmark", "Region Midtjylland", "Region Nordjylland")
    wde = sum(e["de"] for k, e in reg if k in west)
    wmed = sorted(e["med"] for k, e in reg if k in west)
    sj = d["regions"]["Region Sjælland"]
    ann = DOC["bek677"]["annex1"]          # parsed from the pinned BEK 677, not typed
    b = sorted(ann["rows"], key=lambda x: -x["pct"])
    vals = sorted(x["pct"] for x in b)
    bmed = (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
    brows = "\n".join(f"| {x['name']} | {x['pct']:.1f}% |" for x in b)
    cap = [x["name"] for x in b if x["pct"] == max(vals)]
    P, ns = d["params"], nuar_stats()
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
    bc, bo = o["beef / other cattle / conventional"], o["beef / other cattle / organic"]
    org_de = sum(v["de"] for k, v in o.items() if k.endswith("organic"))
    org_n = sum(v["n"] for k, v in o.items() if k.endswith("organic"))
    return f"""
## 4. Where it lands, and on whom

### The published allocation, which is not where the animals are

{C("C-IN-ANNEX-INTRO", f"The mandatory targeted requirement for 2026/2027 is a short list. {ann['n_catchments']} coastal catchments carry one; every other catchment in Denmark carries none. This is the whole of BEK 677/2026 Annex 1:")}

| Coastal catchment | Requirement, as % of the holding's base area |
|---|---:|
{brows}

{C("C-IN-ANNEX-RANGE", f"{ann['n_catchments']} catchments, from {min(vals):.1f}% to {max(vals):.1f}%, median {bmed:.2f}%. {ann['n_at_ceiling']} sit at the {max(vals):.1f}% ceiling: {', '.join(cap)}.")}

{C("C-IN-NAMES", "**Read the names.** Kalundborg Fjord, Dybsø Fjord, Stege Bugt and Jammerland Bugt og Musholm Bugt are Zealand and Møn. Kløven, Helnæs Bugt, Kertinge Nor and Aborg Minde Nor are Funen and the small islands. Als Fjord, Augustenborg Fjord, Genner Bugt and Hejlsminde Nor are Sønderjylland's inner waters. Those twelve are most of the list, and of the catchments at the ceiling only Kås Bredning og Venø Bugt is in Jutland.")}

Now set that against where the animals are:

| Region | Holdings | Animal units | Share of herd | With land | Median DE/ha | >{P['historic_limits_de_ha'][0]} |
|---|---:|---:|---:|---:|---:|---:|
{rrows}

{C("C-IN-WEST", f"**{share(wde, d['total_de']):.0f}% of the Danish herd is in the three western regions** — Syddanmark, Midtjylland and Nordjylland, which is Jutland with Funen — and Region Sjælland, with {share(sj['de'], d['total_de']):.1f}% of it at a median {sj['med']:.2f} DE/ha, contains several of the catchments carrying the highest mandatory percentage.")}

{B("C-IN-DESIGN")}That is not a paradox and it is not evidence that the allocation is wrong. It follows
from what the requirement is charged on: the *base area*, which is cereals. A catchment
of Zealand arable land has a large base area and few animals. **A percentage of a large
base area on holdings with no manure is a real cost, and it falls on exactly the
population section 6 has no balance sheets for.**{E}

<details class="work">
<summary>{C("C-IN-KOMMUNE-SUM", "The kommune-level density table, which is the wrong unit for this instrument and is printed anyway because it is the one this project can compute")}</summary>

| Kommune, ranked by median stocking density | Region | Holdings with land | Median DE/ha | >{P['historic_limits_de_ha'][0]} | Animal units |
|---|---|---:|---:|---:|---:|
{krows}

*(minimum {P['min_kommune_holdings']} holdings declaring land, so that a median means something)*

{B("C-IN-WESTBELT")}The three western regions run from {wmed[0]:.2f} to {wmed[-1]:.2f} DE/ha at the median,
which is flat enough that the region is useless as a unit. The kommune is sharper and
names one belt: the west and south of Jutland, plus Sønderjylland. That belt is where
the *manure* pressure is, and the manure pressure is a real burden — the two thresholds
in section 3 and the {DOC['bek931']['ceiling_kg_n_ha']} kg N/ha ceiling all bite there. It is simply not the same
burden as the targeted percentage in the table above, and mapping one onto the other is
the mistake this section exists to prevent.{E}

{C("C-IN-RETENTION", "**On retention, this page asserts nothing.** The instrument weights by modelled nitrogen retention — in the voluntary round, lower-retention ID15 areas go first — and this project has not obtained the retention grid, so it asserts no geographic pattern in it. [Section 7](#7-what-this-cannot-establish-and-what-would) says what would settle it.")}
</details>

### Organic holdings are exempt, and that is worth more than the arithmetic

{B("C-IN-ORG-EXEMPT")}Section 1 recorded the statutory exemptions: a holding certified for organic production
on 2026-02-01 is outside the targeted requirement altogether (BEK 677/2026 §1 stk. 3
nr. 2), and one certified at the start of the planning period is outside the livestock
catch-crop requirement as well (BEK 673/2026 §4 stk. 5). Underneath that exemption there
is also an arithmetic advantage, and the livestock register can measure it on cattle:{E}

| Cohort | Holdings | Animal units | Mean DE | With land | Median DE/ha | >{P['historic_limits_de_ha'][0]} |
|---|---:|---:|---:|---:|---:|---:|
{orows}

{B("C-IN-ORG-DENSITY")}Organic dairy holdings farm substantially more land per cow, and only part of that is a
smaller herd: mean herd {do['mean_de']:,.0f} DE against {dc['mean_de']:,.0f}, which is
{abs(100*(do['mean_de']-dc['mean_de'])/dc['mean_de']):.0f}% smaller, but a median
stocking density of **{do['med']:.2f} against {dc['med']:.2f} DE/ha**, which is
{100*(1-do['med']/dc['med']):.0f}% lower. On beef both medians are low —
{bo['med']:.2f} organic against {bc['med']:.2f} conventional — near the lower threshold
and far below the higher one.{E}

{B("C-IN-ORG-NUAR")}The independent check agrees, and it is stronger than an exemption. In NUAR's modelling
of the discharge-based regulation across six allocation models, **organic holdings do
not merely lose less — they gain**, at between {ns['organic_lo']:+,} and {ns['organic_hi']:+,} kroner per hectare against
the reference, in a catchment where cattle lose between {-ns['cattle_best']:,} and {-ns['cattle_worst']:,}. Organic and
extensified holdings are the two types in the table with a positive sign in every
column.{E}

{B("C-IN-ORG-LIMIT")}*What this does not establish.* The livestock register's organic flag is on the
**herd**, not on the land, and the statutory exemption turns on certification of the
*holding*. A conventional herd grazing organically certified land is invisible here, and
an organic arable holding with no animals does not appear in this cut at all — which
matters, because an arable holding is exactly what the targeted requirement is aimed at.
The organic share of the national herd measured this way is
{share(org_de, d['total_de']):.1f}% on {org_n:,} cattle holdings, and that is a floor:
organic herds of other species are not counted.{E}
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
    def _en(c):                        # "Vinterhvede — *winter wheat*" -> "winter wheat"
        e = crop_en(c)
        return e.split("— *", 1)[1].rstrip("*") if "— *" in e else e
    c1, c2 = _en(h["top_crops"][0][0]).capitalize(), _en(h["top_crops"][1][0])
    return f"""
## 5. {share(no['ha'], h['total_ha']):.0f}% of the hectares have no animals over them

{C("C-IN-S5-INTRO", "Section 3 and section 4 asked who keeps the animals and what they grow. Ask instead who holds the hectares the percentage is charged on, and the population changes.")}

| Operator of the declared hectares | Businesses | Declared hectares | Share | Mean ha |
|---|---:|---:|---:|---:|
{rows}

{B("C-IN-ARABLE")}**{share(no['ha'], h['total_ha']):.1f}% of Denmark's declared farmland —
{no['ha']:,.0f} hectares across {no['n']:,} businesses — is farmed by a business with
no animal units in the livestock register at all.** These are the arable holdings, and
section 3 showed that {share(d['hectares']['base']['no animal units'].get('in base', 0), sum(d['hectares']['base']['no animal units'].values())):.0f}%
of their hectares are on holdings whose largest crop is inside the base area. They are
the population the percentage is charged on most completely.{E}

Two different costs reach them, one now and one from 2027, and they are not the same
kind of cost.

* {C("C-IN-COST-NOW", f"**Today the instrument is a catch-crop percentage**, and the cost is a share of the rotation given over to a crop that is not harvested for sale, on a base area that is most of the farm. The {max(x['pct'] for x in DOC['bek677']['annex1']['rows']):.1f}% ceiling in section 4 is that share of the cereal ground.")}
* {C("C-IN-COST-2027", "**From 2027 the quota is on discharge**, and then the constraint moves to the input the arable holding controls: the bag. That is the channel [NITROGEN.md](NITROGEN.md) predicts bites first — *the bag is the free variable.* The livestock holding meets a tightening quota by rearranging where the slurry goes; the arable holding meets it by buying less nitrogen. One is a logistics cost and the other is an input cut.")}

| Largest declared crop on the holding (hectare-weighted) | Hectares | Share |
|---|---:|---:|
{crops}

{B("C-IN-CROPS")}{c1} and {c2} alone account for
{share(h['top_crops'][0][1] + h['top_crops'][1][1], h['total_ha']):.0f}% of the
declared area under this measure, and both are cereals, so both are inside the base
area. One row is worth reading twice: {zero_n:,.0f} hectares ({share(zero_n, h['total_ha']):.1f}%)
are on holdings whose largest declared crop is grass under an environmental commitment
that permits **no nitrogen at all**. That land is not available to be tightened, and it
is a reminder that the baseline the quota is applied to is not a uniform one.{E}

> {C("C-IN-NO-ARABLE-BS", f"**And there is not one arable balance sheet in this analysis.** The accounts in section 6 were fetched for businesses on the livestock map, so every one of the {d['accounts_sample']['n_filed']:,} filings is a business that keeps or kept animals.")}
>
> {C("C-IN-NO-ARABLE-SO", f"So for the cohort carrying **{share(no['ha'], h['total_ha']):.0f}% of the hectares** and taking the most direct form of the burden, this page can describe the exposure and can say **nothing at all** about the buffer. That is a gap in the answer and not a hedge on it: a reader who wants to know whether Danish arable farming can absorb a per-hectare nitrogen cut will not find it here, and should not read section 6 as though it generalised.")}
"""


def sec_money(d):
    s = d["accounts_sample"]
    c = d["cohorts"]
    sh = d["shock"]
    it = d["intersection"]
    art = d["debt_artefact"]
    P, ns = d["params"], nuar_stats()
    lhead = " | ".join(f"{x:,}" for x in P["shock_ha_kr"])
    dhead = " | ".join(f"{x:,}" for x in P["shock_de_kr"])
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
    b130 = DOC["bek130"]                   # read from the pinned BEK 130, not typed
    E_ = {"rotation land, priority area": b130["priority_rotation_kr_ha"],
          "grass, priority area": b130["priority_grass_kr_ha"],
          "rotation land, elsewhere": b130["elsewhere_rotation_kr_ha"],
          "grass, elsewhere": b130["elsewhere_grass_kr_ha"]}

    def yrs(t, rate):
        m = sh.get(t, {}).get("break_even_median", float("nan"))
        return rate / m if m == m and m > 0 else None
    payback = "\n".join(
        "| " + t + f" | {f0(sh[t]['break_even_median'])} | "
        + " | ".join(
            (f"{yrs(t, r):.1f}" if yrs(t, r) is not None else "—")
            for r in (E_["rotation land, priority area"], E_["rotation land, elsewhere"],
                      E_["grass, priority area"])) + " |"
        for t in sorted(sh, key=lambda x: -sh[x]["break_even_median"]))
    yr_beef = yrs("beef / other cattle", E_["grass, priority area"]) or float("nan")
    yr_dairy = yrs("dairy", E_["rotation land, priority area"]) or float("nan")
    NR, NM = DOC["nuar_t75"]["rows"], DOC["nuar_t75"]["models"]   # the parsed Tabel 7.5
    nuar_models = " | ".join(NM)
    nuar_dashes = "".join("---:|" for _ in NM)
    nuar_rows = "\n".join(
        "| " + ("**" + t + "**" if t in ("Cattle", "Organic") else t) + " | "
        + " | ".join(f"{NR[t][m]:+,}" for m in NM) + " |"
        for t in NR)
    ix = it["by_type"]

    def cell(t, k):
        return ix.get(t, {}).get(k, 0)
    irows = "\n".join(
        f"| {t} | {sum(ix[t].values()):,} | **{cell(t, '(True, True)')}** "
        f"({share(cell(t, '(True, True)'), sum(ix[t].values())):.0f}%) "
        f"| {cell(t, '(True, False)')} | {cell(t, '(False, True)')} "
        f"| {cell(t, '(False, False)')} |"
        for t in order(ix))
    exposed = sum(cell(t, '(True, True)') + cell(t, '(True, False)') for t in ix)
    thin_not = sum(cell(t, '(False, True)') for t in ix)
    return f"""
## 6. Which balance sheets have no buffer

### The sample, and what it is a sample of

| | |
|---|---:|
| Businesses with filed accounts in this data | {s['n_filed']:,} |
| …in primary agriculture (NACE `011`–`015`) | {s['n_primary_agriculture']:,} |
| …keeping animals in the 2024 livestock register | **{s['n_keeping_animals']:,}** |
| …of those, also declaring field parcels | {s['n_with_land']:,} |

{C("C-IN-EXCLUDED", f"{s['excluded']['not primary agriculture (NACE)']:,} filings were dropped as not primary agriculture: businesses outside NACE `011`–`015` that appear in the livestock register because they hold a livestock site — support activities and property letting among them. Medians are used throughout, and the exclusion is stated so the count can be checked.")}

{C("C-IN-READ-S2", f"Read section 2 before reading any figure below. This is the incorporated {share(d['visibility']['by_accounts']['True']['de'], d['total_de']):.0f}% of the herd, the large end, and nothing here shows the rest to be in better condition.")}

### The distribution of equity

{C("C-IN-EQRATIO-DEF", f"Equity ratio — equity over total assets — is the closest thing in a filed account to \"how much can go wrong before this stops\". Across the {s['n_primary_agriculture']:,} agricultural filings:")}

| Decile | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th | 9th |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Equity ratio | {dec[0]:.2f} | {dec[1]:.2f} | {dec[2]:.2f} | {dec[3]:.2f} | {dec[4]:.2f} | {dec[5]:.2f} | {dec[6]:.2f} | {dec[7]:.2f} | {dec[8]:.2f} |

{C("C-IN-DECILES", f"**The bottom decile is already negative** — assets are worth less than the debts against them — and the second decile sits at {dec[1]:.2f}, which is thin for a business whose income is a commodity price.")}

### By enterprise type

| Enterprise type | n | Median DE | Median assets (m. kr) | Median equity ratio | Negative equity | Loss last year | Median profit per ha (kr) | Median DE/ha |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{crows}

{B("C-IN-DAIRY-BEST")}This table is the reason the page is organised the way it is. **The type under the most
regulatory pressure has the fewest loss-makers.** Dairy has the highest stocking density
of any type, the smallest share of its land inside the catch-crop base, and the lowest
loss rate ({c['dairy']['pct_loss']:.0f}% of the {c['dairy']['n_profit']} dairy filings carrying
a profit figure), the lowest share with negative equity, and a median profit per
hectare {c['dairy']['median_profit_per_ha']/c['beef / other cattle']['median_profit_per_ha']:.1f}
times that of beef. Beef and other cattle have the *highest* median equity ratio
({c['beef / other cattle']['median_equity_ratio']:.2f}) and at the same time the highest
loss rate of any farming type but the mixed remainder
({c['beef / other cattle']['pct_loss']:.0f}%) — a combination that describes an
asset-rich, income-poor holding.{E}

### How large a shock each cohort can take

{C("C-IN-LADDER-DEF", "The ladder assumes no cost at all; a published estimate is laid on it two subsections below, once the shape of the buffer is established independently of it. The question here is only: how many holdings in each cohort go from profit to loss as an annual charge per declared hectare rises? The break-even column is the charge the median holding could absorb exactly.")}

| Enterprise type | n | Break-even (kr/ha) | {lhead} |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{lrows}

*(share of the cohort making a loss once a charge of that many kroner per declared
hectare is applied to the last filed twelve-month profit)*

{B("C-IN-LADDER-READ")}Dairy absorbs {f0(sh['dairy']['break_even_median'])} kr/ha before the median holding turns,
and even at {P['shock_ha_kr'][-1]:,} kr/ha only {sh['dairy']['ladder']['8000']:.0f}% of the cohort is loss-making.
Beef starts at {sh['beef / other cattle']['ladder']['0']:.0f}% loss-making before
anything is applied and is at {sh['beef / other cattle']['ladder']['1000']:.0f}% by
{at(P['shock_ha_kr'], 1000):,} kr/ha. **Of the farming types, the cohort with the least room is the one the
instrument is least aimed at.**{E}

{B("C-IN-LANDLESS-HOLE")}That ladder has a hole in it, and the hole is the finding of section 3. A charge per
hectare cannot be applied to a holding with no hectares, so every landless unit drops
silently out of the table above — {sum(sd[k]['n_landless'] for k in sd):,} of the
{sum(sd[k]['n'] for k in sd):,} holdings with both a herd and a profit figure. Charging
per animal unit instead puts them back, and is the better model of how the cost reaches
them: through the price of placing slurry, which scales with the slurry.{E}

| Enterprise type | n | of which landless | Break-even (kr/DE) | {dhead} |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{drows}

*(share of the cohort making a loss once a charge of that many kroner per animal unit
is applied)*

{C("C-IN-SWAP", "**Changing the denominator swaps which cohort is thinnest, and it swaps pigs with beef.** Ranked by what the median holding can absorb:")}

* per declared hectare — dairy {f0(sh['dairy']['break_even_median'])}, poultry
  {f0(sh['poultry']['break_even_median'])}, pigs {f0(sh['pigs']['break_even_median'])},
  **beef {f0(sh['beef / other cattle']['break_even_median'])}**;
* per animal unit — dairy {f0(sd['dairy']['break_even_median'])}, poultry
  {f0(sd['poultry']['break_even_median'])}, beef
  {f0(sd['beef / other cattle']['break_even_median'])}, **pigs
  {f0(sd['pigs']['break_even_median'])}**.

{B("C-IN-SWAP-READ")}Dairy is the most resilient on both measures and by a similar factor, so nothing about
dairy turns on the choice. What turns on it is which of pigs and beef is the thin one.
Per hectare, beef looks like the sector with no room, because beef holds a great many
hectares against very little income. Per animal unit, pigs are, because a pig holding
concentrates a large herd on little or no land. **Whether the requirement is
denominated in hectares or in slurry decides which of those two sectors it is hardest
on** — and that is a drafting choice, not a fact about farming.{E}

{C("C-IN-LANDLESS-PIGS", f"And the landless holdings are not the healthy half of the pig cohort. Of the {sd['pigs']['n_landless']} pig holdings with accounts and no declared land, {sd['pigs']['pct_loss_landless']:.0f}% made a loss in their last filed year, against {sd['pigs']['pct_loss_with_land']:.0f}% of the {sd['pigs']['n_with_land']} that do declare land. The group most exposed to a repricing of slurry placement is also the group already least able to absorb one.")}

### What a published cost estimate does to those ladders

{C("C-IN-NUAR-INTRO", "The ladders above assume nothing. There is one published by-farm-type estimate this project has read in its primary source, and putting it on the ladder is the point of having built the ladder. NUAR modelled the change in gross margin per hectare against the reference regulation, by enterprise type, for the Hjarbæk Fjord catchment under six quota-allocation models:")}

| Enterprise type | {nuar_models} |
|---|{nuar_dashes}
{nuar_rows}

*{C("C-IN-NUAR-NOTE", "(change in DB2, kroner per hectare, against a reference of compulsory and livestock catch crops. Eriksen et al., NUAR, DCA rådgivningsnotat, 2024-05-24, Tabel 7.5, read from the pinned report. The report states that the pattern recurs in its other coastal catchments, where it is also cattle that carries the largest losses.)")}*

Three things follow, and the third is the one that matters.

{B("C-IN-NUAR-LOW")}**The magnitudes land on the low rungs of the ladder.** The losses run from {ns['loss_lo']:,}
to {ns['loss_hi']:,} kroner per hectare. At {at(P['shock_ha_kr'], 1000):,} kr/ha this page's ladder puts
{sh['dairy']['ladder']['1000']:.0f}% of dairy holdings into a loss,
{sh['pigs']['ladder']['1000']:.0f}% of pigs and
{sh['beef / other cattle']['ladder']['1000']:.0f}% of beef and other cattle. A cost of
this size is absorbable by most of the sample — but the sample is the incorporated
{share(d['visibility']['by_accounts']['True']['de'], d['total_de']):.0f}% of the herd, and the ladder's zero column already shows
{sh['beef / other cattle']['ladder']['0']:.0f}% of beef holdings loss-making before
anything is added.{E}

{C("C-IN-NUAR-RATIO", f"**Cattle carries {ns['ratio_lo']:.1f} to {ns['ratio_hi']:.1f} times the arable loss across the columns**, which is the mechanism section 3 measured from the other side. And **organic is positive in every column** — not exempt-and-therefore-unaffected, but better off than the reference.")}

{B("C-IN-NORESCUE")}**And no allocation model rescues cattle.** Cattle's loss lands between {-ns['cattle_best']:,} and
{-ns['cattle_worst']:,} kroner per hectare in **every one of the six** — a spread of
{ns['cattle_spread']:,} kr/ha, or {ns['cattle_rel']:.0f}% of its own mean loss, the narrowest relative range of any
loss-making type in the table. Specialised arable moves from {-ns['arable_best']:,} to {-ns['arable_worst']:,} across the
same six, a spread of {ns['arable_spread']:,} kr/ha and {ns['arable_rel']:.0f}% of its own mean loss.{E}

{B("C-IN-NORESCUE-READ")}So the allocation model is a real choice **for arable and a small one for cattle**.
Picking a different model changes what a specialised arable holding loses by a factor of
{ns['arable_factor']:.1f}; it moves a cattle holding by {ns['cattle_rel']:.0f}% of its mean loss and leaves it, in
all six cases, losing {ns['ratio_lo']:.1f} to {ns['ratio_hi']:.1f} times what the arable holding does. **What
sets cattle's position is the base area, not the allocation model**, and the base area
is set by what grows on the farm.{E}

{C("C-IN-TRADE-MOVES", f"The one thing in the report that does move cattle materially is trading: the same table narrows cattle's loss to {-ns['hrodz']:,} kr/ha once allowances can be exchanged, which is the largest gain of any type. That is why [section 1](#1-what-the-instrument-is-and-what-that-alone-tells-you-about-incidence) treats the unresolved trading question as load-bearing rather than technical.")}

### The other side of the ledger: what the voluntary offer is worth

{C("C-IN-TARGETS", "The Tripartite's other instrument is **voluntary land conversion**, bought with money: " + R("{read:POL-DMBIO-2026:250,000|plante 250.000 hektar ny dansk skov}") + " hectares of new forest and " + R("{read:POL-DMBIO-2026:140,000|udtage 140.000 hektar lavbundsjorde}") + " hectares of lowland taken out, as DM Bio's 2026 article on the agreement puts it. So the incidence question has a second half that a burden analysis alone misses: to whom is the offer worth taking?")}

{C("C-IN-B130", "The rate is published. Permanent extensification pays a **one-off** sum per hectare for the whole commitment period — [BEK 130/2026 §18](https://www.retsinformation.dk/eli/lta/2026/130):")}

| | Land that was in rotation | Land that was grass |
|---|---:|---:|
| Carbon-rich soil, or a high-nitrogen-need area with wetland potential | **{E_["rotation land, priority area"]:,} kr/ha** | {E_["grass, priority area"]:,} kr/ha |
| Everywhere else | {E_["rotation land, elsewhere"]:,} kr/ha | {E_["grass, elsewhere"]:,} kr/ha |

{C("C-IN-PAYBACK-DEF", "Set that against what a hectare currently earns, using the same medians as the ladder above. The figure is the number of years of the cohort's median per-hectare profit that the payment replaces:")}

| Enterprise type | Median profit per ha | {E_['rotation land, priority area']:,} | {E_['rotation land, elsewhere']:,} | {E_['grass, priority area']:,} |
|---|---:|---:|---:|---:|
{payback}

{B("C-IN-OFFER-GAP")}**The same schedule is a very different offer depending on who is asked.** Taking each
cohort at the rate it would most likely be offered — grass for beef, rotation land for
dairy — the payment replaces about **{yr_beef:.0f} years** of a beef hectare's margin
and about **{yr_dairy:.0f}** of a dairy hectare's. At an identical rate the gap is
wider still: {E_['rotation land, priority area']:,} kr/ha is {yrs('beef / other cattle', E_['rotation land, priority area']):.0f} years for beef
against {yr_dairy:.0f} for dairy. Against a farming horizon of a generation, one of
those is a good price and the other is not.{E}

{B("C-IN-OFFER-DIR")}And the direction is the wrong way round for the nitrogen. **The holdings for which the
offer is most attractive are the extensive ones, whose hectares carry the least manure**
— beef at a median {d['cohorts']['beef / other cattle']['median_density']:.2f} DE/ha.
The holdings whose hectares carry the most are the ones for which it is worst value —
dairy at {d['cohorts']['dairy']['median_density']:.2f}.{E}

{B("C-IN-DAIRY-UP")}There is a second reason dairy should decline. **Selling a hectare out of a land-squeezed
holding raises its manure loading on every hectare that remains.** A dairy holding at
{d['cohorts']['dairy']['median_density']:.2f} DE/ha that converts land moves *up* against the
{DOC['bek673']['threshold_high_kg_n_ha']} kg N/ha threshold and the {DOC['bek931']['ceiling_kg_n_ha']} kg N/ha ceiling, not down. The voluntary
scheme and the compulsory one push it in opposite directions, and it is paid for going
the way that makes its other problem worse.{E}

{C("C-IN-PREDICTION", "That is a prediction rather than an observation, and it is falsifiable: it says participation in the conversion schemes should be concentrated in extensive cattle and in arable land, and scarce among high-loading dairy. The uptake data would settle it and this project does not have it — see [section 7](#7-what-this-cannot-establish-and-what-would).")}

{B("C-IN-PAYBACK-LIMIT")}*What this does not establish.* The one-off payment is not a like-for-like substitute
for an annual margin: it is capital against income, and the land keeps some residual
value. The ratio above is a comparison of magnitudes, not a discounted valuation, and a
reader who wants the second should build it. It is printed because the magnitudes differ
by a factor of {yr_beef/yr_dairy:.0f} between the two cattle sectors at the rates each would
most likely be offered, and {yrs('beef / other cattle', E_['rotation land, priority area'])/yr_dairy:.0f} at the same rate.{E}

### The overlap, which is the actual answer

{C("C-IN-OVERLAP-DEF", f"Exposed means at or above the indicative {it['line']} DE/ha line — where section 1's {DOC['bek673']['threshold_high_kg_n_ha']} kg N/ha threshold sits, and where the compulsory percentage and the quota-cut price step up — or declaring no land at all. Thin means an equity ratio below {P['thin_equity_ratio']:.2f}.")}

| Enterprise type | n | Exposed **and** thin | Exposed, not thin | Thin, not exposed | Neither |
|---|---:|---:|---:|---:|---:|
{irows}

{B("C-IN-EXPOSED-NORM")}First, the size of the exposed column itself:
**{exposed:,} of {it['n_rows']} animal-keeping holdings with accounts
({share(exposed, it['n_rows']):.0f}%) are on the exposed side of the line.** Above the
{DOC['bek673']['threshold_high_kg_n_ha']} kg N/ha threshold is where a livestock holding normally is; that is not a finding
about a stressed minority, it is the ordinary condition of the sector. Which is why the
second column matters more than the first.{E}

{B("C-IN-BOTH")}**{it['n_both']} of {it['n_rows']} ({share(it['n_both'], it['n_rows']):.0f}%) are both
exposed and thin**, and {share(it['n_both'], it['n_both'] + thin_not):.0f}%
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
loss rate** — before any nitrogen cost at all.{E}

{B("C-IN-PROFILE")}**Most of that cohort is pigs** — {cell('pigs', '(True, True)')} of the {it['n_both']},
{share(cell('pigs', '(True, True)'), it['n_both']):.0f}% — either landless or stocked above the higher manure
threshold, with an equity ratio under {P['thin_equity_ratio']:.2f}.
{share(cell('pigs', '(True, True)'), sum(ix['pigs'].values())):.0f}% of all pig holdings with accounts sit there, against
{share(cell('dairy', '(True, True)'), sum(ix['dairy'].values())):.0f}% of dairy — and
dairy is *more* exposed by every physical measure in section 3. The difference is the
balance sheet. **Dairy's problem is the base area; pigs' problem is the equity**, and
only the second is the kind of problem money can fix.{E}

### Two qualifications that change the reading

{C("C-IN-STRENGTHENED", "**The balance sheets strengthened over the three filed years.**")}

| Enterprise type | n | Median three-year cumulative profit (m. kr) | Negative over three years | Median change in equity ratio | Falling |
|---|---:|---:|---:|---:|---:|
{trows}

{B("C-IN-REBUILT")}Equity ratios rose over the period for every type except the mixed remainder, and
median three-year cumulative profit is positive and large for dairy and pigs. **These
balance sheets entered the policy period rebuilt.** A measurement taken after poor years
could find a larger no-buffer cohort; this one is taken after the balance sheets
strengthened. It also means the buffers above are real and should not be argued away.{E}

{B("C-IN-BIOASSETS")}**Biological assets are a buffer you cannot spend twice.** The herd is on the balance
sheet — median {pct(100*c['dairy']['median_biological_share'])} of assets for dairy
(n={c['dairy']['n_biological']}) and
{pct(100*c['pigs']['median_biological_share'])} for pigs
(n={c['pigs']['n_biological']}), where the tag is filed at all. Selling it is the same
act as ceasing to produce. A solvency ratio that counts it is counting the exit as the
reserve.{E}

<details class="work">
<summary>{C("C-IN-DEBT-SUM", f"Why no debt-composition figure appears on this page: treating an absent XBRL tag as zero would move the short-term share by up to {max_err:.0f} percentage points")}</summary>

{B("C-IN-DEBT-TAG")}`lt_debt` is `LongtermLiabilitiesOtherThanProvisions`, and a filing that does not
present the line does not carry the tag. Treating an absent tag as a zero is correct for
the *level* of debt — the balance-sheet identity confirms it, below — and wrong for the
*composition*, because it forces the short-term share to the whole of the debt for every
holding that did not file the line. Those holdings are not spread evenly:{E}

| Enterprise type | Filings carrying `lt_debt` | Short-term share, treating absent as zero | …restricted to filings carrying both tags | Error |
|---|---:|---:|---:|---:|
{arows}

{C("C-IN-DEBT-SPREAD", f"The real spread is roughly {100*min(art[k]['strict_median'] for k in art):.0f}–{100*max(art[k]['strict_median'] for k in art):.0f}% rather than {100*min(art[k]['naive_median'] for k in art):.0f}–{100*max(art[k]['naive_median'] for k in art):.0f}%, and a difference between types survives only for poultry and the mixed remainder.")}

{B("C-IN-DEBT-GONE")}**And once corrected, there is no finding.** Dairy, pigs and beef sit at
{100*art['dairy']['strict_median']:.0f}%, {100*art['pigs']['strict_median']:.0f}% and
{100*art['beef / other cattle']['strict_median']:.0f}% — a spread too narrow to carry
any argument about who is term-financed and who is on the overdraft. That is why no
debt-composition figure appears in any table on this page. One further caution even on
the corrected column: `st_debt` is `ShorttermLiabilitiesOtherThanProvisions`, which
includes trade payables as well as bank debt, so it is not a measure of how much of a
holding's borrowing reprices annually.{E}

{B("C-IN-DEBT-LEVEL")}**Why the level is safe when the composition is not.** Where the tag is present, assets
minus equity minus both debts leaves a median residual of
{pct(100*d['accounts_sample']['balance_sheet_check']['lt_debt present']['median_residual'])}
of assets (n={d['accounts_sample']['balance_sheet_check']['lt_debt present']['n']:,});
where it is absent, assets minus equity minus short-term debt alone leaves
{pct(100*d['accounts_sample']['balance_sheet_check']['lt_debt absent']['median_residual'])}
(n={d['accounts_sample']['balance_sheet_check']['lt_debt absent']['n']:,}). The
identity closes either way, so the absent tag really is a zero — the level is right and
a ratio built from it is not.{E}

{B("C-IN-GROSS")}**And one that no range check catches at all.** The `gross` column is
`GrossResult`/`GrossProfitLoss` — *bruttofortjeneste*, gross profit after variable
costs. It is **not turnover**, and a Danish class B company may leave turnover out of its
report. Every figure `gross` produces is plausible, correctly signed and of the right
order of magnitude; a "profit margin" computed as profit over `gross` would be a real
ratio of two real numbers and would mean something different for every firm in the
sample. There is therefore **no margin on sales anywhere on this page**. Everything is
per hectare or per animal unit.{E}
</details>
"""


def sec_gaps(d):
    h = d["hectares"]
    P, b673, b931, b130, ns = d["params"], DOC["bek673"], DOC["bek931"], DOC["bek130"], nuar_stats()
    ann = DOC["bek677"]["annex1"]
    annv = [x["pct"] for x in ann["rows"]]
    forest = R("{read:POL-DMBIO-2026:250,000|plante 250.000 hektar ny dansk skov}")
    lowland = R("{read:POL-DMBIO-2026:140,000|udtage 140.000 hektar lavbundsjorde}")

    def row(q, cid, answer, would):
        return f"| {q} | {C(cid, answer)} | {would} |"
    rows = "\n".join([
        row("**The allocation mechanism**", "C-IN-G-MECH", f"Established, from the regulations. It is a percentage of the base area, set per coastal catchment, with two manure thresholds at {b673['threshold_low_kg_n_ha']} and {b673['threshold_high_kg_n_ha']} kg N/ha and a {b931['ceiling_kg_n_ha']} kg N/ha ceiling. The texts were fetched, pinned and read.", "—"),
        row("**Which catchments carry the largest mandatory requirement**", "C-IN-G-CATCH", f"Established for 2026/2027, from BEK 677 Annex 1: {ann['n_catchments']} catchments, {min(annv):.1f}% to {max(annv):.1f}%.", "—"),
        row("**Whether high-density kommuner are also low-retention catchments**", "C-IN-G-RET", "**Not established, and not asserted.** This project has not obtained the retention grid.", "The **kystvandopland** boundaries and the retention grid the regulation ranks by, joined to the field-parcel geometry the sibling project already holds. Highest-value fetch on this list."),
        row("**On what terms discharge quotas may be transferred**", "C-IN-G-TRANSFER", f"**Partly established.** LOV 759 §6 stk. 4 creates the power to permit transfer; the terms — who to whom, whether bounded within a catchment, at what price — are **not verified**. This is the most load-bearing gap on the page: transfer is worth {ns['trade']:.0f}% of cattle's modelled loss.", "The implementing regulation under §6, once issued."),
        row("**Whether the implementing regulations under LOV 759 have been issued**", "C-IN-G-IMPL", "**Not established.** The act is a framework; every number that decides a holding's position is delegated.", "Checking Lovtidende after the act commences on 2027-01-01."),
        row("**The numeric braklægningspunkt**", "C-IN-G-BRAK", "**Not established.**", "The text of the June 2025 partial agreement, and the implementing act."),
        row("**Compensation and transition rates**", "C-IN-G-RATES", "**Established for permanent extensification only**, read from the pinned BEK 130/2026 §18 in section 6. The other *tilskud* schemes were not read, and no rate for them is published here.", "A pass over the other *tilskud* regulations and their annexes."),
        row("**Owned versus rented land**", "C-IN-G-OWN", "Not established at all. The field-parcel register records who *declares* a parcel, not who owns it.", "The ownership register (*Ejerfortegnelsen*) or the land register (*Tingbogen*), joined on the property identifier. This is also the join that would make individual identification easy, which is a reason to publish only the distribution."),
        row("**Uptake of the voluntary conversion schemes, by enterprise type**", "C-IN-G-UPTAKE", "Not obtained, which is why section 6's closing argument is labelled a prediction.", "The *tilsagn* lists for the conversion schemes, if published, joined on CVR to the livestock register."),
        row("**Crop mix per holding**", "C-IN-G-CROPS", "Only the single largest declared crop, which is why section 3's base-area split is a proxy.", "The full parcel-level crop declaration, in the same Marker layer already fetched and reduced to a top-crop summary on the way in. It would turn section 3's split from a proxy into a measurement."),
        row("**Kilograms of manure nitrogen per hectare, per holding**", "C-IN-G-KGN", f"Not established. Animal units were converted at a **stated** {P['n_per_de_kg']} kg N per unit, and the declared area is not the *harmoniareal*.", "The *gødningsregnskab*, which is not open."),
        row("**Balance sheets for arable holdings**", "C-IN-G-ARABLE", "None exist in this data. Every filing here belongs to a livestock business — including, awkwardly, the population the targeted requirement is most aimed at.", "Accounts fetched for crop holdings."),
        row(f"**The finances of {share(d['visibility']['by_accounts']['False']['de'], d['visibility']['total_de']):.0f}% of the herd and {share(h['by_accounts']['False']['ha'], h['total_ha']):.0f}% of the land**", "C-IN-G-NONFILERS", "Not obtainable from public filings: sole proprietorships and partnerships have no duty to publish accounts. **This one does not close from the public record.**", "Nothing public at the level of the holding."),
        row("**The inter-farm slurry placement contracts**", "C-IN-G-CONTRACTS", f"Not obtainable. Not in any register. Their existence is inferable from the {sum(d['types'][t]['landless_de'] for t in d['types']):,.0f} animal units standing on holdings with no declared land; their terms are not.", "Nothing. These are private contracts."),
        row("**The CO2e tax on agricultural emissions**", "C-IN-G-CO2E", "**Out of scope.** It is a separate instrument with a different base — greenhouse-gas emissions, not nitrogen — and therefore a different incidence, which this page does not compute. Nothing on this page should be read as covering it.", "An implementing bill, if one is introduced."),
        row("**The *bemærkninger* to LOV 759**", "C-IN-G-REMARKS", "Not read. The enacted text was read — §6, §11, §57 and §65 are quoted from it — but the explanatory remarks, which is where the modelling behind the quota would be described, were not.", "Reading the bill's remarks."),
        row("**Whether the voluntary conversion programme is delivering at the rate its targets require**", "C-IN-G-DELIVERY", "Not established here. Section 6 predicts who should decline the offer; it does not measure whether they have.", f"The *tilsagn* registers, and the agency's own area accounting against the {forest} hectare afforestation and {lowland} hectare lowland targets."),
    ])
    return f"""
## 7. What this cannot establish, and what would

{C("C-IN-GAPS-INTRO", "The house rule on this site is that an absence is reported as a count over a named corpus. Here is the list. The middle column says what this page actually did, which for several rows is *read the regulation*, and for several others is *not obtain the data*.")}

| Question the brief asked | Answer here | What would answer it |
|---|---|---|
{rows}

### The one finding that would need a name, stated without one

{C("C-IN-EXTREME", f"The highest-density holdings in the register are extreme: {d['types']['poultry']['p90']:.1f} animal units per declared hectare at the 90th percentile for poultry.")}

{C("C-IN-JOIN", "**Those may well not be findings about farming but findings about the join.** A holding company that owns the animals while an operating company declares the land appears here as an impossibly dense holding beside an impossibly empty one, and nothing in either register says the two are related. Naming them would risk publishing a false claim about a real business, with an address attached.")}

{C("C-IN-VERIFY", "What it would take to verify: the CVR ownership graph, to test whether each extreme site's business has a parent or sibling that declares land. Until that is done the tail of this distribution is a data-quality question and is not read as an economic one — which is why every table above reports medians and shares above a threshold, and none reports a maximum.")}

## 8. What this page concludes

1. {B("C-IN-K1")}**The instrument does not count animals.** It charges a percentage on a base area of
   cereals, maize, rape and pulses, set per coastal catchment, with steps at {b673['threshold_low_kg_n_ha']}
   and {b673['threshold_high_kg_n_ha']} kg of manure nitrogen per hectare and a flat {b931['ceiling_kg_n_ha']} kg N/ha ceiling. The animal
   unit is not a unit in the regulations in force, and the cattle derogation ended in 2024.{E}
2. {B("C-IN-K2")}**Dairy is the most exposed enterprise type, and not because of density alone.**
   {d['types']['dairy']['over']['0.8']:.0f}% of dairy holdings that declare land sit
   above the higher manure threshold (n={d['types']['dairy']['n_ratio']:,}), where the compulsory
   percentage and the quota-cut price step up — and only
   {share(d['hectares']['base']['dairy'].get('in base', 0), sum(d['hectares']['base']['dairy'].values())):.0f}%
   of dairy's hectares are on holdings whose largest crop is inside the base area the
   percentage is charged on. Largest surplus, smallest base. The technical basis for the
   regulation says the same thing in its own words.{E}
3. {B("C-IN-K3")}**The exposure ranking and the fragility ranking are different rankings.** Dairy is
   the most exposed and has the fewest loss-makers — {d['cohorts']['dairy']['pct_loss']:.0f}%
   loss-making, n={d['cohorts']['dairy']['n_profit']}. Beef and other cattle are the
   least exposed of the main types and have the highest loss rate of the farming types —
   {d['cohorts']['beef / other cattle']['pct_loss']:.0f}%, n={d['cohorts']['beef / other cattle']['n_profit']}.
   Any account that treats "hit hardest" as one quantity is wrong about one of them.{E}
4. {B("C-IN-K4")}**No allocation model rescues cattle.** Across the six quota-allocation models in the
   published technical basis, cattle loses between {-ns['cattle_best']:,} and {-ns['cattle_worst']:,} kroner per hectare — a
   spread of {ns['cattle_rel']:.0f}% of its mean loss — while specialised arable moves by {ns['arable_rel']:.0f}% of its own
   much smaller loss. The allocation model changes arable's position and barely changes
   cattle's. Trading would; on what terms it will be allowed is not established.{E}
5. {B("C-IN-K5")}**The unit the charge is denominated in swaps which sector is thinnest.** Per hectare
   the thinnest is **beef** ({f0(d['shock']['beef / other cattle']['break_even_median'])}
   kr/ha against {f0(d['shock']['pigs']['break_even_median'])} for pigs); per animal
   unit it is **pigs** ({f0(d['shock_de']['pigs']['break_even_median'])} kr/DE against
   {f0(d['shock_de']['beef / other cattle']['break_even_median'])} for beef). Dairy is
   most resilient on both.{E}
6. {B("C-IN-K6")}**The landless holding is outside the per-hectare instrument, and its cost reaches it
   through slurry placement that no register records.** It is also the sicker half of its
   own sector: {d['shock_de']['pigs']['pct_loss_landless']:.0f}% of landless
   pig holdings with accounts made a loss last year against
   {d['shock_de']['pigs']['pct_loss_with_land']:.0f}% of those with land.{E}
7. {B("C-IN-K7")}**The mandatory allocation for 2026/2027 is not where the animals are.** {ann['n_catchments']}
   catchments carry it, most of them on Zealand, Funen and the inner waters of
   Sønderjylland, and of those at the {max(annv):.1f}% ceiling only Kås Bredning og Venø
   Bugt is in Jutland — Zealand's region holding
   {share(d['regions']['Region Sjælland']['de'], d['total_de']):.1f}% of the national
   herd at a median of {d['regions']['Region Sjælland']['med']:.2f} DE/ha. A percentage
   of a large base area on holdings with no manure is a real cost, and it falls on the
   population this page has no balance sheets for.{E}
8. {B("C-IN-K8")}**The voluntary offer is worth least to the holdings whose land carries the most
   nitrogen.** Permanent extensification pays a one-off {b130['priority_rotation_kr_ha']:,} kr/ha for rotation land
   in a priority area. That is about {b130['priority_rotation_kr_ha']/d['shock']['dairy']['break_even_median']:.0f}
   years of the median dairy hectare's profit and about
   {b130['priority_grass_kr_ha']/d['shock']['beef / other cattle']['break_even_median']:.0f} years of the median
   beef hectare's at the grass rate. The offer buys extensive land cheaply and intensive
   land at a poor price — and a land-squeezed dairy holding that sells a hectare moves
   *up* against its own manure thresholds. That is a falsifiable prediction about uptake,
   not an observation.{E}
9. {B("C-IN-K9")}**The act that takes over in 2027 permits quotas to be made transferable, and the
   terms are not public.** LOV 759 §6 stk. 4 creates the power; the implementing
   regulation would set the terms; transfer is worth {ns['trade']:.0f}% of cattle's modelled
   loss. It also carries two expropriation powers, one of them not limited to this act's
   own measures.{E}
10. {B("C-IN-K10")}**{share(h['by_accounts']['False']['ha'], h['total_ha']):.0f}% of Danish declared farmland is farmed by businesses
   that publish nothing.** The individual-level question is, for most of Danish
   agriculture, not answerable from public data — and that is a finding about the public
   record rather than a limitation of this analysis.{E}

---

*Generated by `scripts/socialcontext.py`. Do not edit this file: a later run overwrites
it, and prose added here is silently lost. The prose lives in the generator.*

*{C("C-IN-FOOT-SOURCES", "The registers are read from the fetched copies of the sibling project [danish-livestock](https://jjokulian.github.io/danish-livestock/), which located and documented them. Following the house rule, this page cites that work rather than restating it, and computes its own aggregates from the same primary sources rather than copying its results.")}*

*{C("C-IN-FOOT-LEGAL", "Every legal provision quoted here is in a text pinned by its hash and read for this page, not taken from coverage of it: LOV nr. 759 of 2026-09-08 (§6, §11, §57, §65), BEK 931/2024 (§14, §26), BEK 673/2026 (§4, §24, Annex 1 and Annex 2), BEK 677/2026 (§1, §3, §6 and Annex 1), BEK 131/2026 (§6) and BEK 130/2026 (§18), all from [retsinformation.dk](https://www.retsinformation.dk); and the NUAR figures from the report itself. Where this page says something is not established, it means the document was not obtained — not that it was skimmed.")}*
"""


def nuar_stats():
    """What the page says about NUAR Tabel 7.5, computed from the parsed table."""
    rows, models = DOC["nuar_t75"]["rows"], DOC["nuar_t75"]["models"]
    cat = [rows["Cattle"][m] for m in models]
    ara = [rows["Specialised arable"][m] for m in models]
    loss_types = ("Cattle", "Specialised arable", "Pigs and arable", "Small / non-specialised")
    losses = [-rows[t][m] for t in loss_types for m in models]
    org = [rows["Organic"][m] for m in models]

    def rel(t):
        v = [rows[t][m] for m in models]
        return (max(v) - min(v)) / (-sum(v) / len(v)) * 100
    return {
        "cattle_best": max(cat), "cattle_worst": min(cat),
        "cattle_spread": max(cat) - min(cat),
        "cattle_rel": rel("Cattle"),
        "arable_best": max(ara), "arable_worst": min(ara),
        "arable_spread": max(ara) - min(ara),
        "arable_rel": rel("Specialised arable"),
        "arable_factor": min(ara) / max(ara),
        "ratio_lo": min(c / a for c, a in zip(cat, ara)),
        "ratio_hi": max(c / a for c, a in zip(cat, ara)),
        "loss_lo": min(losses), "loss_hi": max(losses),
        "organic_lo": min(org), "organic_hi": max(org),
        "rodz": rows["Cattle"]["Rodz"], "hrodz": rows["Cattle"]["hRODZ"],
        "trade": (1 - rows["Cattle"]["hRODZ"] / rows["Cattle"]["Rodz"]) * 100,
        "rel_by_loss_type": {t: rel(t) for t in loss_types},
    }


ANNEX_NAMED = ("Kalundborg Fjord", "Dybsø Fjord", "Stege Bugt", "Jammerland Bugt og Musholm Bugt",
               "Kløven", "Helnæs Bugt", "Kertinge Nor", "Aborg Minde Nor",
               "Als Fjord", "Augustenborg Fjord", "Genner Bugt", "Hejlsminde Nor")


def check_positions(d):
    """The words on the page that rank or compare - largest, lowest, only, most -
    are checked against the numbers they describe. A page whose words no longer
    follow from its figures is refused."""
    P, b673 = d["params"], DOC["bek673"]
    want = (b673["threshold_low_kg_n_ha"] / P["n_per_de_kg"],
            b673["threshold_high_kg_n_ha"] / P["n_per_de_kg"])
    have = tuple(P["reg_thresholds_de_ha"])
    bad = []
    if any(abs(a - b) > 1e-9 for a, b in zip(want, have)):
        bad.append(f"the DE/ha lines {have} no longer follow from the pinned thresholds over "
                   f"the stated conversion {want}")
    t, c, o = d["types"], d["cohorts"], d["organic"]
    if max(t, key=lambda k: t[k]["surplus"]) != "dairy":
        bad.append("dairy no longer carries the largest surplus of any type")
    if min(c, key=lambda k: c[k]["pct_loss"]) != "dairy":
        bad.append("dairy no longer has the lowest loss rate")
    if min(c, key=lambda k: c[k]["pct_negative_equity"]) != "dairy":
        bad.append("dairy no longer has the lowest share with negative equity")
    if max(c, key=lambda k: c[k]["median_density"]) != "dairy":
        bad.append("dairy no longer has the highest median density in the accounts")
    if max(c, key=lambda k: c[k]["median_equity_ratio"]) != "beef / other cattle":
        bad.append("beef no longer has the highest median equity ratio")
    farm = [k for k in c if k != "other / mixed livestock"]
    if max(farm, key=lambda k: c[k]["pct_loss"]) != "beef / other cattle":
        bad.append("beef no longer has the highest loss rate of the farming types")
    base = d["hectares"]["base"]
    typed = [k for k in base if k != "no animal units"]
    if min(typed, key=lambda k: base[k].get("in base", 0) / sum(base[k].values())) != "dairy":
        bad.append("dairy no longer has the smallest share of land inside the base")
    if min(("dairy", "pigs", "beef / other cattle"), key=lambda k: t[k]["over"]["0.8"]) != "beef / other cattle":
        bad.append("beef is no longer the least exposed of the main types")
    sh, sd = d["shock"], d["shock_de"]
    for name, s in (("hectare", sh), ("animal unit", sd)):
        if max(s, key=lambda k: s[k]["break_even_median"]) != "dairy":
            bad.append(f"dairy is no longer the most resilient per {name}")
    if min(("pigs", "beef / other cattle"), key=lambda k: sh[k]["break_even_median"]) != "beef / other cattle":
        bad.append("beef is no longer the thinner of pigs and beef per hectare")
    if min(("pigs", "beef / other cattle"), key=lambda k: sd[k]["break_even_median"]) != "pigs":
        bad.append("pigs are no longer the thinner of pigs and beef per animal unit")
    if not sd["pigs"]["pct_loss_landless"] > sd["pigs"]["pct_loss_with_land"]:
        bad.append("landless pig holdings no longer make losses more often")
    landless = {k: t[k]["landless_de"] for k in t}
    if landless["pigs"] * 2 <= sum(landless.values()):
        bad.append("pigs no longer hold most of the landless herd")
    rows, models = DOC["nuar_t75"]["rows"], DOC["nuar_t75"]["models"]
    pos = sorted(k for k in rows if k != "Weighted mean" and all(rows[k][m] > 0 for m in models))
    if pos != ["Extensified", "Organic"]:
        bad.append(f"the types positive in every column are now {pos}")
    ns = nuar_stats()
    if min(ns["rel_by_loss_type"], key=ns["rel_by_loss_type"].get) != "Cattle":
        bad.append("cattle no longer has the narrowest relative range of the loss-making types")
    gain = {k: rows[k]["hRODZ"] - rows[k]["Rodz"] for k in rows if k != "Weighted mean"}
    if max(gain, key=gain.get) != "Cattle":
        bad.append("cattle no longer gains most from trading")
    ann = [x["name"] for x in DOC["bek677"]["annex1"]["rows"]]
    missing = [n for n in ANNEX_NAMED if n not in ann]
    if missing:
        bad.append(f"the page names {missing} as Annex 1 catchments; the annex does not list them")
    if len(ANNEX_NAMED) * 2 <= len(ann):
        bad.append("the named catchments are no longer most of the annex")
    top = [x["name"] for x in DOC["bek677"]["annex1"]["rows"]
           if x["pct"] == max(y["pct"] for y in DOC["bek677"]["annex1"]["rows"])]
    if "Kås Bredning og Venø Bugt" not in top:
        bad.append("Kås Bredning og Venø Bugt is no longer at the ceiling")
    tc = [x[0] for x in d["hectares"]["top_crops"][:2]]
    if not all(x in ("Vinterhvede", "Vårbyg", "Vinterbyg", "Vårhvede") for x in tc):
        bad.append(f"the two largest crops are now {tc}, not cereals")
    rs = sorted(d["regions"], key=lambda k: -d["regions"][k]["de"])
    if rs[3] != "Region Sjælland":
        bad.append(f"the region order changed: {rs}")
    cc = d["cohorts"]
    if not all(cc[k]["median_equity_trajectory"] > 0 for k in cc if k != "other / mixed livestock"):
        bad.append("equity ratios no longer rose for every type but the mixed remainder")
    if bad:
        raise live.Unjustified("INCIDENCE: the page's words no longer follow from its "
                               "figures:\n  " + "\n  ".join(bad))


def render(d):
    """The page, from the numbers as written to socialcontext.json and read back
    live, so every figure on it carries its field."""
    global DOC
    DOC = live.live_json(DOCS_JSON)
    check_positions(d)
    return "".join([
        head(),
        privacy(d["visibility"]),
        policy(d),
        sec_visible(d),
        sec_types(d),
        sec_place(d),
        sec_hectares(d),
        sec_money(d),
        sec_gaps(d),
    ])


def main(argv):
    """Compute from the sibling registers (heavy: run through scripts/heavy) and
    write socialcontext.json; then render the page from that file, read live.
    --render skips the compute and renders from the file as it stands."""
    if "--render" not in argv:
        d = compute()
        os.makedirs(DERIVED, exist_ok=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=1)
        log(f"  wrote {OUT_JSON}")
    doc = render(live.live_json(OUT_JSON))
    try:
        write_doc(OUT_MD, doc)
    except live.Unjustified as e:
        log(str(e))
        return 1
    log(f"  wrote {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
