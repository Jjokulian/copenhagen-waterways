#!/usr/bin/env python3
"""What each source's bytes actually mean, declared rather than guessed.

Two silent format bugs cost this project real work in one day. `float("8,47")`
raised, a bare `except` returned None, and every coordinate in a 2.4-million-row
file vanished so that the file read as empty rather than broken. Then a fast split
left `'"19890830"'` quoted, the date never parsed, and a coverage cube reported
zero for three streams without erroring. Both were guesses about format that
happened to be wrong.

So: every source declares its format, and the declaration is checked against the
bytes instead of trusted.

**On the thousands separator, which turns out not to be a problem.** The worry is
that "8,473" might be eight thousand four hundred and seventy-three. It is not,
and the reason is stronger than a heuristic: grouping separators are a *display*
convention. They appear in reports, HTML tables and PDFs, and essentially never in
a machine export, because the export is written by a serialiser rather than a
formatter.

Checked rather than assumed, over about 950,000 rows of three ODA extracts:

    lys.csv.gz          400,000 rows    0 grouped
    maaledybde.csv.gz   151,167 rows    0 grouped

ODA ctd.csv.gz MIXES UNITS WITHIN A PARAMETER COLUMN, AND ONE OF THEM MATTERS.
Full-file scan, 53,710,760 rows, 0 malformed, 17 named Parameter values:

    Konduktivitet   mS/cm 4,425,685   mS/m   743,747   <-- FACTOR OF 100, UNFLAGGED
    Vaegtfylde      g/l   3,412,290   kg/m3  917,384   <-- cosmetic: same magnitude
    Fluorescens     Ingen 6,783,693   ug/l        83   <-- 97 rows, plus 14 'Ikke oplyst'

Only conductivity is a hazard: 14% of its rows are in mS/m and converting the column
without reading Enhed per row is a hundredfold error on that seventh. Density is mixed
in NAME only - 1 g/l and 1 kg/m3 are the same quantity - so it costs nothing but will
fail a naive equality check on the unit string. Always read Enhed per row; never per
column, and never per file.

ROW COUNTS, for anyone sizing a job (same scan):
    Temperatur 7,501,421 | Salinitet 7,474,645 | Oxygen indhold 7,147,012
    Fluorescens 6,783,790 | Oxygenmaetning 6,598,319 | Lysdaempning 5,217,377
    Konduktivitet 5,169,432 | Vaegtfylde 4,329,674 | Turbiditet 1,076,915
    FDOM 890,921 | Photometer maaling 576,179 | Photometer reference 531,071
    pH 237,496 | Stroemhastighed 84,734 | Stroemretning 84,572
    Farvestof 4,601 | Dihydrogensulfid 2,601

Turbiditet and FDOM are worth naming because this project spent a long time treating
turbidity and CDOM as absent. They are not absent. Turbiditet runs 1994-2026 over 252
stations; FDOM only from 2021-04-19 over 211. Neither reaches the derived monthly cube.
Neither is an independent production path either - same cast, same vessel, often the
same sonde as the oxygen channel.

SECCHI IS RIGHT-CENSORED AT THE BED, AND THE CENSORING IS 59x STRONGER IN SHALLOW
WATER. Verified over the 96,708 rows carrying both SigtDybde_m and BundDybde_m:
SigtTilBund - the disc was still visible on the bottom - is True on 21.36% of readings
where the bottom is at or above 10 m, and on 0.36% of readings deeper than 10 m. In
shallow water the disc hits bottom before it disappears, so the recorded value is a
lower bound on clarity, not a measurement of it.

Consequence for anyone using this file: a regression of Secchi depth on bottom depth,
or any comparison of clarity between shallow and deep stations, is partly a
measurement of the censoring. Fit it censored (Tobit, or a survival model with
SigtTilBund as the event indicator) or restrict to SigtTilBund = False and say that
the restriction removes the clearest shallow water. Substituting the bottom depth for
the missing value, or dropping the flagged rows silently, both manufacture the result.
    ctd.csv.gz          400,000 rows    0 grouped

Every value that *looked* grouped under a naive pattern - 39,196 of them in the
light file alone - was a decimal with exactly three places, which is what a
coordinate or a corrected result looks like.

That gives a rule with no ambiguity left in it:

  * **One separator: it is the decimal separator.** Always, whatever follows it.
    A three-digit tail is not evidence of grouping; it is evidence of three
    decimal places.
  * **Two or more separators, or `.` and `,` in the same number: grouping.** This
    is the only ambiguous case, and it does not occur in any machine export here.
    Where it does occur, the stream was formatted for a human and needs a
    declaration rather than a parser.

`audit()` counts the second case. It is a validator, not a fallback: if it ever
fires on a source declared machine-readable, the declaration is wrong and the
right response is to look, not to add a branch.
"""
import re

# Two or more separators, or a mixture of both characters. The only real evidence
# of grouping, and the only case a single-separator rule cannot decide.
GROUPED = re.compile(r"^-?\d+[.,]\d+[.,]|^-?[\d.]*\.[\d,]*,|^-?[\d,]*,[\d.]*\.")

FORMATS = {
    "oda": {
        "what": "Overfladevandsdatabasen CSV extracts",
        "encoding": "iso-8859-1", "delimiter": ";", "quote": '"',
        "decimal": ",", "grouping": None,
        "date": "YYYYMMDD",
        "traps": ["Every field is quoted; a split that does not unquote leaves "
                  "dates unparseable.",
                  "Decimal comma; float() raises rather than returning something "
                  "wrong, so a bare except empties the column.",
                  "The station list is period-dependent: with no period set the "
                  "server returns only the currently active network.",
                  "Column count varies across rows in a few thousandths of a "
                  "percent; those rows must be skipped, not read at shifted "
                  "offsets."],
    },
    "geojson_dk": {
        "what": "Danish national GeoJSON layers (vandplandata, MiljøGIS)",
        "encoding": "utf-8", "delimiter": None, "quote": None,
        "decimal": ".", "grouping": None, "date": "YYYY-MM-DD",
        "traps": ["Coordinate order is lon,lat and the CRS is declared in the "
                  "file; some Danish layers are EPSG:25832 and some 4326."],
    },
    "spildevandsdata": {
        "what": "spildevandsdata.dk Leaflet layer exports (a PULS extract)",
        "encoding": "utf-8", "delimiter": None, "quote": None,
        "decimal": ".", "grouping": None, "date": None,
        "traps": ["Overflow layers store numbers as numbers and the treatment "
                  "plant layers store the same quantities as strings.",
                  "Field names are truncated to ten BYTES by an upstream "
                  "shapefile step, which split a two-byte UTF-8 character and "
                  "froze U+FFFD into one name permanently."],
    },
    "geus_gpkg": {
        "what": "GEUS GeoPackage (seabed substrate)",
        "encoding": "utf-8", "delimiter": None, "quote": None,
        "decimal": ".", "grouping": None, "date": None,
        "traps": ["Geometry is MultiPolygon ZM - type 3006 - so every point "
                  "carries four doubles. Reading two yields no polygons and no "
                  "error."],
    },
    "cmems": {
        "what": "Copernicus Marine NetCDF",
        "encoding": None, "delimiter": None, "quote": None,
        "decimal": ".", "grouping": None, "date": "ISO-8601",
        "traps": ["Some OMI datasets publish no original files, so get() reports "
                  "success having written nothing; omi-arco still has the data.",
                  "Several products are reanalysis or the in-situ TAC regridded, "
                  "so they are downstream of the same national measurements and "
                  "are not independent checks."],
    },
}


def num(v, source="oda"):
    """Parse one numeric field according to the source's declared format."""
    if v is None:
        return None
    s = str(v).strip()
    if len(s) > 1 and s[0] == '"' and s[-1] == '"':
        s = s[1:-1].strip()
    if not s:
        return None
    dec = FORMATS.get(source, {}).get("decimal", ".")
    if dec == ",":
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def audit(values, source="oda"):
    """Check a sample of raw fields against the declaration.

    Returns counts, not a verdict. `grouped` is the one that matters: a non-zero
    count on a source declared machine-readable means the declaration is wrong.
    """
    out = {"n": 0, "numeric": 0, "grouped": 0, "wrong_separator": 0,
           "tail3": 0, "examples": []}
    dec = FORMATS.get(source, {}).get("decimal", ".")
    other = "." if dec == "," else ","
    for v in values:
        s = str(v).strip().strip('"').strip()
        out["n"] += 1
        if not s or not (s[0].isdigit() or s[0] == "-"):
            continue
        if not re.match(r"^-?\d+([.,]\d+)*$", s):
            continue
        out["numeric"] += 1
        if GROUPED.match(s):
            out["grouped"] += 1
            if len(out["examples"]) < 5:
                out["examples"].append(s)
            continue
        if other in s:
            out["wrong_separator"] += 1
        if re.match(r"^-?\d+[.,]\d{3}$", s):
            out["tail3"] += 1
    return out
