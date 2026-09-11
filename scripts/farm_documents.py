#!/usr/bin/env python3
"""The figures INCIDENCE.md takes from regulations and reports, read out of their pinned texts.

A legal threshold typed into a script is a typed number with a paragraph
reference beside it: nothing checks that the paragraph still says it. So every
such figure is read here from the text of its document, as pinned by sha256 in a
claims register (BEK 931/2024 in data/manual/claims.json; the others in
data/manual/claims.d/farm.json). Each is located by the document's own wording
around it, which must occur exactly once, and parsed from that match. A phrase
that is no longer in the pinned text refuses the run, so a re-pinned document
changes a figure only through this file, and visibly.

Two tables are parsed whole rather than transcribed:

  BEK 677/2026 Bilag 1   the targeted catch-crop percentage per coastal catchment
  NUAR Tabel 7.5         change in gross margin (DB2, kr/ha) by enterprise type and
                         quota model, Hjarbæk Fjord

Danish number format throughout: "10,7" is ten point seven, "1.122" is one
thousand one hundred and twenty-two.

    python3 scripts/farm_documents.py

Writes data/derived/farm_documents.json.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, ROOT, log
import claims

OUT = os.path.join(DERIVED, "farm_documents.json")

# (key, source, the document's own wording around the figure, with one group)
PHRASES = [
    ("bek931.ceiling_kg_n_ha", "BEK931-2024",
     r"divideret med (\d+) kg kvælstof pr\. hektar"),
    ("bek931.derogation_kg_n_ha", "BEK931-2024",
     r"tilladelse til at tildele organisk gødning i mængder svarende til (\d+) kg "
     r"kvælstof pr\. hektar harmoniareal"),
    ("bek673.catch_crop_pct", "BEK673-2026",
     r"Arealet med pligtige efterafgrøder skal udgøre mindst (\d+,\d+) pct\. af "
     r"virksomhedens efterafgrødegrundareal"),
    ("bek673.catch_crop_pct_high", "BEK673-2026",
     r"skal arealet med pligtige efterafgrøder dog mindst udgøre (\d+,\d+) pct\. af "
     r"efterafgrødegrundarealet"),
    ("bek673.threshold_low_kg_n_ha", "BEK673-2026",
     r"En virksomhed, der udbringer husdyrgødning og anden organisk gødning svarende til "
     r"(\d+) kg kvælstof eller derover pr\. hektar harmoniareal, skal udover"),
    ("bek673.threshold_high_kg_n_ha", "BEK673-2026",
     r"svarende til (\d+) kg kvælstof eller derover pr\. hektar harmoniareal: \d+ kg kvælstof"),
    ("bek673.quota_cut_below_kg_n_ha", "BEK673-2026",
     r"svarende til mindre end \d+ kg kvælstof pr\. hektar harmoniareal: (\d+) kg kvælstof"),
    ("bek673.quota_cut_above_kg_n_ha", "BEK673-2026",
     r"svarende til \d+ kg kvælstof eller derover pr\. hektar harmoniareal: (\d+) kg kvælstof"),
    ("bek677.min_base_ha", "BEK677-2026",
     r"efterafgrødegrundareal, som udgør mindre end (\d+) hektar"),
    ("bek130.priority_rotation_kr_ha", "BEK130-2026",
     r"vådområdepotentiale eller begge de nævnte arealer: 1\) Marker, der inden for "
     r"referenceperioden har haft en arealanvendelse, der er omfattet af en af "
     r"afgrødekoderne i bilag 1: (\d+\.\d+) kr\."),
    ("bek130.priority_grass_kr_ha", "BEK130-2026",
     r"afgrødekoderne i bilag 2: (\d+\.\d+) kr\. pr\. ha\. Stk\. 2\."),
    ("bek130.elsewhere_rotation_kr_ha", "BEK130-2026",
     r"ikke er omfattet af stk\. 1: 1\) Marker, der inden for referenceperioden har haft "
     r"en arealanvendelse, der er omfattet af en af afgrødekoderne i bilag 1: "
     r"(\d+\.\d+) kr\."),
    # the regulation's own typo - "hr. ha" for "pr. ha" - is part of its wording
    ("bek130.elsewhere_grass_kr_ha", "BEK130-2026",
     r"afgrødekoderne i bilag 2: (\d+\.\d+) kr\. hr\. ha"),
]

NUAR_ROWS = [("1. Økologi", "Organic"), ("2. Kvæg", "Cattle"),
             ("3. Specialiseret plante", "Specialised arable"),
             ("4. Svin og plante", "Pigs and arable"),
             ("5. Små / ikkespecial.", "Small / non-specialised"),
             ("6. Ekstensiverede", "Extensified"), ("Vægtet gennemsnit", "Weighted mean")]
NUAR_HEAD = "Flad Rodz Brak Visa Visu Visu2 MJØK hRODZ hVISA"


def dk(s):
    """Danish number text -> number: '10,7' -> 10.7, '1.122' -> 1122, '-994' -> -994."""
    s = s.replace("−", "-").replace(".", "").replace(",", ".")
    return float(s) if "." in s else int(s)


def norm(t):
    return re.sub(r"\s+", " ", t)


def put(out, key, value):
    a, b = key.split(".")
    out.setdefault(a, {})[b] = value


def bek677_annex(text):
    """Bilag 1: three columns that pdftotext emits one after the other - the
    catchment numbers, their names, then the percentages."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if "Krav om målrettede efterafgrøder i kystvandoplande" not in lines:
        raise SystemExit("BEK677-2026: Bilag 1 heading not found in the pinned text")
    i = lines.index("nummer (ID108)") + 1
    ids = []
    while i < len(lines) and re.fullmatch(r"\d+", lines[i]):
        ids.append(int(lines[i]))
        i += 1
    names = []
    while i < len(lines) and not lines[i].startswith("Efterafgrødekravets"):
        names.append(lines[i])
        i += 1
    pcts = [dk(l) for l in lines[i:] if re.fullmatch(r"\d+,\d", l)][:len(ids)]
    if not ids or not (len(ids) == len(names) == len(pcts)):
        raise SystemExit(f"BEK677-2026 Bilag 1: {len(ids)} numbers, {len(names)} names, "
                         f"{len(pcts)} percentages - the table did not parse")
    rows = [{"catchment_id": a, "name": n, "pct": p} for a, n, p in zip(ids, names, pcts)]
    top = max(pcts)
    return {"rows": rows, "n_catchments": len(rows),
            "n_at_ceiling": sum(1 for p in pcts if p == top)}


def nuar_t75(text):
    t = norm(text)
    head = ("Tabel 7.5. Omkostningsforskelle mellem kvotetildelingsmodellerne og referencen "
            "for bedriftstyperne i Hjarbæk Fjord opland.")
    if t.count(head) != 1:
        raise SystemExit("NUAR-2024: the Tabel 7.5 caption is not in the pinned text once")
    body = t[t.index(head):]
    if NUAR_HEAD not in body:
        raise SystemExit("NUAR-2024: Tabel 7.5 column header not found")
    for dk_label, _ in NUAR_ROWS:
        if dk_label not in body[:600]:
            raise SystemExit(f"NUAR-2024: row label '{dk_label}' not in Tabel 7.5")
    after = body[body.index(NUAR_HEAD) + len(NUAR_HEAD):]
    nums = re.findall(r"-?\d{1,3}(?:\.\d{3})*(?![\d,])", after)[:len(NUAR_ROWS) * 9]
    models = NUAR_HEAD.split()
    if len(nums) < len(NUAR_ROWS) * 9:
        raise SystemExit("NUAR-2024: Tabel 7.5 has fewer cells than rows x models")
    # pdftotext emits the first five rows whole and the last two - Ekstensiverede
    # and Vægtet gennemsnit - column by column, alternating; so the cells are split
    # accordingly, and a cross-check against the row labels is not possible, only
    # against the table's own arithmetic in the weighted-mean row, which the
    # construction declares as a gap.
    grid = [nums[r * 9:(r + 1) * 9] for r in range(5)]
    tail = nums[45:63]
    grid += [tail[0::2], tail[1::2]]
    rows = {}
    for (dk_label, en), cells in zip(NUAR_ROWS, grid):
        rows[en] = {"label_da": dk_label, **{m: dk(c) for m, c in zip(models, cells)}}
    return {"models": models[:6], "trading_models": models[6:], "rows": rows}


def main(argv):
    d, _, _ = claims.load()
    texts, evidence, out = {}, {}, {"_what": "Figures read from the pinned texts of the "
                                             "regulations and reports INCIDENCE.md cites, "
                                             "each by the document's own wording."}
    for key, sid, pattern in PHRASES:
        if sid not in texts:
            texts[sid] = norm(claims.pin_text(d, sid))
        hits = list(re.finditer(pattern, texts[sid]))
        if len(hits) != 1:
            raise SystemExit(f"{key}: the wording is in the pinned {sid} {len(hits)} times, "
                             "not once - read the document and fix the phrase")
        put(out, key, dk(hits[0].group(1)))
        evidence[key] = f"{sid}: ...{hits[0].group(0)}..."
    raw677 = claims.pin_text(d, "BEK677-2026")
    out["bek677"]["annex1"] = bek677_annex(raw677)
    out["nuar_t75"] = nuar_t75(claims.pin_text(d, "NUAR-2024"))
    evidence["bek677.annex1"] = "BEK677-2026: Bilag 1, parsed whole"
    evidence["nuar_t75"] = "NUAR-2024: Tabel 7.5, parsed whole"
    out["_evidence"] = evidence
    out["_pins"] = {sid: hashlib.sha256(claims.pin_text(d, sid).encode()).hexdigest()[:16]
                    for sid in sorted({s for _, s, _ in PHRASES} | {"NUAR-2024"})}
    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
        f.write("\n")
    log(f"wrote {os.path.relpath(OUT, ROOT)}: {len(PHRASES)} figures, "
        f"{out['bek677']['annex1']['n_catchments']} catchments, "
        f"{len(out['nuar_t75']['rows'])} NUAR rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
