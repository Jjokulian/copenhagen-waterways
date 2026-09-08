#!/usr/bin/env python3
"""A coverage cube: which area, which month, which stream actually has data.

The 4D map stored each observation stream as a span and a count — "bathing water,
1991-2018, n=13" — which cannot say *which* thirteen years, so seasonal bias and
temporal shifts in effort were invisible. A span is an aggregate, and aggregation is
where the information goes.

This replaces the span with a time axis. For every marine water body, every month
from 1980 to 2026, and every stream, one bit: was anything observed. Then, for the
variables where a number is meaningful, one Int16 per area-month.

The sizes are the reason this is worth doing rather than agonising over. 123 areas x
564 months x N streams as a bitfield is about 87 KB for ten streams. A monthly value
series is 139 KB per variable at Int16. The whole thing lands under two megabytes,
which a static host serves without noticing, and none of it needs a third-party
request — so the CORS question never arises.

**What this deliberately does NOT do.** Some sources are published only as annual
totals: the outfall extract carries cubic metres per year and a count of overflows
per year, and nothing finer exists outside the CVR-gated PULS application. Those
appear in the cube as a distinct state — `ANNUAL_ONLY` — rather than as a value
smeared across twelve months. A total that implies a resolution we do not have is
the same overclaim this project spends its time removing.

Reads   data/raw/oda/*.csv.gz, data/raw/national/marin_overordnet.geojson,
        data/derived/areas.json
Writes  docs/data/areas/cube.bin, cube.json, val_<variable>.bin

Usage:  ~/.venvs/marine/bin/python scripts/cube.py
"""
import collections
import csv
import gzip
import json
import math
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DERIVED, RAW, ROOT, log, read_json, write_json

OUT = os.path.join(ROOT, "docs", "data", "areas")
Y0, Y1 = 1980, 2026
NMON = (Y1 - Y0 + 1) * 12
NODATA = -32768


def num(x):
    x = (x or "").strip().replace(",", ".")
    try:
        return float(x)
    except ValueError:
        return None


def utm32_to_wgs84(x, y):
    """ODA positions are UTM32N; the water-body polygons are WGS84. Inverse
    transverse Mercator, written out rather than imported because this box has no
    pyproj and one projection does not justify a dependency."""
    k0, a, f = 0.9996, 6378137.0, 1 / 298.257223563
    e2 = f * (2 - f)
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    x -= 500000.0
    mu = (y / k0) / (a * (1 - e2 / 4 - 3 * e2 * e2 / 64 - 5 * e2 ** 3 / 256))
    p1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
          + (21 * e1 * e1 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
          + (151 * e1 ** 3 / 96) * math.sin(6 * mu))
    C1 = (e2 / (1 - e2)) * math.cos(p1) ** 2
    T1 = math.tan(p1) ** 2
    N1 = a / math.sqrt(1 - e2 * math.sin(p1) ** 2)
    R1 = a * (1 - e2) / (1 - e2 * math.sin(p1) ** 2) ** 1.5
    D = x / (N1 * k0)
    lat = p1 - (N1 * math.tan(p1) / R1) * (
        D * D / 2 - (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * e2 / (1 - e2)) * D ** 4 / 24
        + (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 252 * e2 / (1 - e2)
           - 3 * C1 * C1) * D ** 6 / 720)
    lon = (D - (1 + 2 * T1 + C1) * D ** 3 / 6
           + (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * e2 / (1 - e2)
              + 24 * T1 * T1) * D ** 5 / 120) / math.cos(p1)
    return math.degrees(lon) + 9.0, math.degrees(lat)


def load_polygons():
    d = read_json(os.path.join(RAW, "national", "marin_overordnet.geojson"))
    out = []
    for ft in d["features"]:
        g = ft["geometry"]
        rings = []
        parts = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in parts:
            for i, ring in enumerate(poly):
                xs = [c[0] for c in ring]
                ys = [c[1] for c in ring]
                rings.append((i == 0, ring, (min(xs), min(ys), max(xs), max(ys))))
        out.append({"id": ft["properties"]["ov_id"],
                    "name": ft["properties"]["ov_navn"],
                    "km2": float(ft["properties"]["ov_stoe"]), "rings": rings})
    return out


def inside(ring, x, y):
    c, n, j = False, len(ring), len(ring) - 1
    for i in range(n):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def locate(polys, x, y):
    for k, p in enumerate(polys):
        hit = False
        for shell, ring, (x0, y0, x1, y1) in p["rings"]:
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                continue
            if inside(ring, x, y):
                hit = True if shell else False
        if hit:
            return k
    return None


def station_areas(polys):
    """Every ODA marine station placed in a water body, once."""
    seen, idx = set(), {}
    p = os.path.join(RAW, "oda", "stations.csv")
    with open(p, encoding="iso-8859-1") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            if (row.get("Observationsstedtype") or "").strip() != "Hav":
                continue
            nr = (row.get("ObservationsstedNr") or "").strip()
            if nr in seen:
                continue
            seen.add(nr)
            X, Y = num(row.get("X_UTM32")), num(row.get("Y_UTM32"))
            if X is None or Y is None or X < 100000 or Y < 5_000_000:
                continue
            k = locate(polys, *utm32_to_wgs84(X, Y))
            if k is not None:
                idx[nr] = k
    return idx


def mon(datestr):
    d = (datestr or "").strip()
    if len(d) < 6 or not d[:6].isdigit():
        return None
    y, m = int(d[:4]), int(d[4:6])
    if not (Y0 <= y <= Y1 and 1 <= m <= 12):
        return None
    return (y - Y0) * 12 + (m - 1)


def scan_oda(fname, station_col, date_col, idx, nareas):
    """One pass per topic, collapsing straight into area-months so a 51-million-row
    file never lands in memory."""
    p = os.path.join(RAW, "oda", fname)
    if not os.path.exists(p):
        return None, 0
    bits = [bytearray(NMON) for _ in range(nareas)]
    n = 0
    # csv.DictReader builds a dict per row, which over 51 million CTD rows costs
    # more than everything else here combined. Only two columns are needed, so
    # split the line and index them, and collapse to (station, year-month) before
    # any further work - the CTD file is one row per depth, so the same cell is
    # hit dozens of times per cast.
    with gzip.open(p, "rt", encoding="iso-8859-1") as fh:
        head = fh.readline().rstrip("\r\n").split(";")
        try:
            si, di = head.index(station_col), head.index(date_col)
        except ValueError:
            log(f"    columns {station_col}/{date_col} not found in {fname}")
            return None, 0
        need = max(si, di)
        seen = set()
        for line in fh:
            f = line.split(";")
            if len(f) <= need:
                continue
            key = (f[si], f[di][:6])
            if key in seen:
                continue
            seen.add(key)
            k = idx.get(f[si].strip())
            if k is None:
                continue
            m = mon(f[di])
            if m is None:
                continue
            bits[k][m] = 1
            n += 1
    return bits, n


def monthly_median(fname, station_col, date_col, value_col, idx, nareas, dedupe=None):
    """Median of one variable per area-month. Values are held per cell only for as
    long as the pass runs; the output is one Int16 per cell."""
    p = os.path.join(RAW, "oda", fname)
    if not os.path.exists(p):
        return None
    acc = collections.defaultdict(list)
    seen = set()
    with gzip.open(p, "rt", encoding="iso-8859-1") as fh:
        for row in csv.DictReader(fh, delimiter=";"):
            k = idx.get((row.get(station_col) or "").strip())
            if k is None:
                continue
            m = mon(row.get(date_col))
            if m is None:
                continue
            v = num(row.get(value_col))
            if v is None:
                continue
            if dedupe:
                key = tuple((row.get(c) or "").strip() for c in dedupe)
                if key in seen:
                    continue
                seen.add(key)
            acc[(k, m)].append(v)
    return acc


def pack_vals(acc, nareas, scale):
    out = bytearray()
    vals = []
    for k in range(nareas):
        for m in range(NMON):
            v = acc.get((k, m))
            if not v:
                vals.append(NODATA)
                continue
            v.sort()
            med = v[len(v) // 2]
            iv = int(round(med * scale))
            vals.append(max(-32767, min(32767, iv)))
    for v in vals:
        out += struct.pack("<h", v)
    return bytes(out), sum(1 for v in vals if v != NODATA)


def main():
    os.makedirs(OUT, exist_ok=True)
    polys = load_polygons()
    n = len(polys)
    log(f"  {n} water bodies")
    idx = station_areas(polys)
    log(f"  {len(idx):,} marine stations placed")

    # ---- presence streams -------------------------------------------------
    streams, layers = [], []

    def add(key, label, bits, note=""):
        streams.append({"key": key, "label": label, "note": note})
        layers.append(bits)

    for key, label, fn, sc, dc in (
            ("ctd", "CTD profiles", "ctd.csv.gz", "ObservationsStedNr", "Dato"),
            ("lys", "Light attenuation", "lys.csv.gz", "ObservationsStedNr", "Dato"),
            ("secchi", "Secchi and bottom depth", "maaledybde.csv.gz",
             "ObservationsstedNr", "StartDato")):
        bits, cnt = scan_oda(fn, sc, dc, idx, n)
        if bits is None:
            log(f"    {key:8} MISSING {fn}")
            continue
        add(key, label, bits)
        log(f"    {key:8} {cnt:,} rows -> "
            f"{sum(sum(b) for b in bits):,} area-months")

    # Streams whose source publishes only a span or an annual figure. They are
    # recorded as coverage over their stated window, and flagged, so the map can
    # draw them differently instead of implying a monthly cadence nobody published.
    ar = read_json(os.path.join(DERIVED, "areas.json"))["areas"]
    byid = {p["id"]: i for i, p in enumerate(polys)}
    for key, label, match, note in (
            ("bathing", "Bathing water class", "Bathing water",
             "Published as an annual class. The bit marks the bathing season of each "
             "year in the stated span, not months anyone sampled."),
            ("model", "DCE statistical model", "DCE statistical model",
             "Fitted once over a window. The bit marks the fitting window, which is "
             "not observation."),
            ("hz", "Hazardous substances", "Hazardous",
             "Sparse campaigns; the span is stated, the individual dates are not in "
             "this extract.")):
        bits = [bytearray(NMON) for _ in range(n)]
        hits = 0
        for aid, rec in ar.items():
            k = byid.get(aid)
            if k is None:
                continue
            for st in (rec.get("streams") or []):
                if match.lower() not in str(st.get("stream", "")).lower():
                    continue
                fr, to = st.get("from"), st.get("to")
                if not fr or not to:
                    continue
                for y in range(max(Y0, int(fr)), min(Y1, int(to)) + 1):
                    months = range(5, 9) if key == "bathing" else range(0, 12)
                    for mm in months:
                        bits[k][(y - Y0) * 12 + mm] = 1
                        hits += 1
        add(key, label, bits, note)
        log(f"    {key:8} {hits:,} area-months (span-derived)")

    # ---- pack the bitfield ------------------------------------------------
    buf = bytearray()
    for bits in layers:
        for k in range(n):
            row = bits[k]
            acc = 0
            for m in range(NMON):
                acc |= (row[m] & 1) << (m % 8)
                if m % 8 == 7:
                    buf.append(acc)
                    acc = 0
            if NMON % 8:
                buf.append(acc)
    with open(os.path.join(OUT, "cube.bin"), "wb") as f:
        f.write(bytes(buf))
    log(f"  cube.bin {len(buf):,} bytes "
        f"({len(streams)} streams x {n} areas x {NMON} months)")

    # ---- monthly values ---------------------------------------------------
    vars_out = []
    for key, label, fn, sc, dc, vc, scale, unit, ded in (
            ("kd", "Light attenuation Kd", "lys.csv.gz", "ObservationsStedNr", "Dato",
             "LyssvaekkelsesKoefficient", 1000, "per m",
             ("ObservationsStedNr", "Dato", "UndersøgelseNr")),
            ("secchi", "Secchi depth", "maaledybde.csv.gz", "ObservationsstedNr",
             "StartDato", "SigtDybde_m", 100, "m", None),
            ("bottom", "Bottom depth", "maaledybde.csv.gz", "ObservationsstedNr",
             "StartDato", "BundDybde_m", 100, "m", None)):
        acc = monthly_median(fn, sc, dc, vc, idx, n, ded)
        if acc is None:
            continue
        blob, filled = pack_vals(acc, n, scale)
        with open(os.path.join(OUT, f"val_{key}.bin"), "wb") as f:
            f.write(blob)
        vars_out.append({"key": key, "label": label, "scale": scale, "unit": unit,
                         "filled": filled})
        log(f"    val_{key}.bin {len(blob):,} bytes, {filled:,} filled cells")

    write_json(os.path.join(OUT, "cube.json"), {
        "_what": "Coverage cube for the 4D map. One bit per area, month and stream "
                 "in cube.bin; one Int16 per area and month in each val_*.bin, "
                 "divided by the variable's scale, with -32768 meaning no data.",
        "_order": "Bits are packed area-major within each stream, months "
                  "least-significant-bit first, ceil(months/8) bytes per area.",
        "year0": Y0, "year1": Y1, "months": NMON,
        "areas": [{"id": p["id"], "name": p["name"], "km2": p["km2"]} for p in polys],
        "streams": streams,
        "variables": vars_out,
        "annual_only": {
            "outfalls": "The published extract carries cubic metres per year and a "
                        "count of overflows per year. Nothing finer exists outside "
                        "the CVR-gated PULS application, so the map shows no time "
                        "axis for it rather than a total spread over months. This "
                        "is B1's missing series, drawn as the hole it is."},
    })
    log(f"  wrote {OUT}/cube.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
