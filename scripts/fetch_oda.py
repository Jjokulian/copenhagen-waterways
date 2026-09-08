#!/usr/bin/env python3
"""Pull the primary marine record out of ODA, before anyone has aggregated it.

Every number this project has argued with so far arrived pre-digested: an indicator
averaged over May-September, an oxygen value collapsed to one per water body per six
years, a national percentage. Those are somebody's summary of a measurement. This
fetches the measurement.

ODA (Overfladevandsdatabasen, DCE/Aarhus) holds the NOVANA record itself - one row
per station, per date, per depth, per parameter, carrying the sampling gear, the
sonde number, the correction factor applied, the raw result beside the corrected
one, and a QA level. That is the level at which competing hypotheses about what
removes the oxygen can be scored against the same evidence.

The portal is a JS app over a SOAP endpoint; scripts/oda_client.py reconstructs the
protocol. This drives the extract workflow:

    topic -> tool -> criteria (stations, period, parameters) -> getcsv.aspx

Politeness: stations are requested in batches with a pause between them, the client
sends a User-Agent naming the project, and nothing here runs concurrently. The
station register is fetched first because it is small and indexes everything else.

Topics (Hav):
    stations   Observationssted   the register: id, name, water body, UTM32, dates
    ctd        Feltmaaling/CTD    oxygen, temperature, salinity by depth
    kemi       Vandkemi           nutrients and chlorophyll
    sediment   Sedimentkemi       what is in the bed
    fauna      Bundfauna          the soft-bottom survey

Usage:
    python3 scripts/fetch_oda.py stations
    python3 scripts/fetch_oda.py ctd --from 1970-01-01 --to 2026-12-31 [--batch 200]
"""
import argparse
import html
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oda_client as oda
from common import RAW, log

DEST = os.path.join(RAW, "oda")
EMAIL = "nulling933@gmail.com"

# emne radio id, and the criterion field that carries the station multiselect.
TOPICS = {
    "stations": {"emne": "Emne_26_162", "what": "Observationssted register"},
    "ctd":      {"emne": "Emne_11_154", "what": "Feltmåling / CTD profiles"},
    "lys":      {"emne": "Emne_11_155", "what": "Feltmåling / light attenuation"},
    "iltkor":   {"emne": "Emne_11_156", "what": "Feltmåling / oxygen correction"},
}


def expand(node):
    """Expand one topic-tree node and return its (id, label) children."""
    c, o = oda.call("EmneNodeClick", lists={"hiddenFields": {
        "TreeviewId": "Emne", "WebMethod": "EmneNodeClick", "NodeId": node,
        "Level": "0", "ReplaceDivId": f"Emne_{node}_sub", "Expand": "1"}})
    s = html.unescape(o)
    return re.findall(r'<input id="(Emne_[0-9_]+)"[^>]*/>\s*([^<]{1,60}?)\s*<', s)


def open_topic(emne, tool="HDVaerktoej_0"):
    """Select a topic and a tool, then let the server rebuild both panes.

    ChangeVaerktoej is sent explicitly even when the tool has not changed: the
    server keeps aggregation state per session, and a tool switch earlier in the
    session otherwise leaks into the SQL and returns an ORDER BY/GROUP BY error
    instead of data."""
    oda.call("HentData_ChangeTopic",
             lists={"radioButtons": {"Emne_rbgroup": emne, "Vaerktoej": tool}})
    oda.call("HentData_ChangeVaerktoej",
             lists={"radioButtons": {"Emne_rbgroup": emne, "Vaerktoej": tool}})
    out = {}
    for m in ("HentData_FillKriterium", "HentData_FillKriteriumRun",
              "HentData_FillData", "HentData_FillDataRun"):
        c, o = oda.call(m, pause=0.6)
        out[m] = o
    return out


def criterion_ids(kriterium_html):
    """Map criterion label -> (field id, select-list type)."""
    s = html.unescape(kriterium_html)
    out = {}
    for m in re.finditer(
            r'<div id="(HDKrit_(\d+))_div"[^>]*>\s*<div class="SelectLabel">([^<]+)</div>', s):
        out[m.group(3).strip()] = (m.group(1), m.group(2))
    return out


def station_list(field_id, sltype):
    """Every station the current topic offers: (checkbox id, number, name)."""
    c, o = oda.call("SCL2_FillMultiSelectList",
                    {"srchStr": "", "SLType": sltype, "SelectBoxId": field_id,
                     "method": "SCL2_FillMultiSelectList"}, pause=1.5)
    s = html.unescape(o)
    return re.findall(r'id="(SCL2CB_\d+)"[^>]*/>\s*(\d{3,12})\s*\(([^)]*)\)', s)


def select_stations(field_id, sltype, checkbox_ids):
    oda.call("SCL2_SelectMultiSelectList",
             {"SLType": sltype, "SelectBoxId": field_id},
             lists={"checkBoxes": {k: "true" for k in checkbox_ids}}, pause=1.2)
    c, o = oda.call("HentData_KritChanged", pause=0.8)
    # HentDataStor=true means the extract is too big to stream and must be ordered
    return "HentDataStor=true" in o


def set_period(frm, to):
    if not frm and not to:
        return
    oda.call("SCL2_DatePicked", lists={"textFields": {
        "SCL2PeriodFrom": frm or "", "SCL2PeriodTo": to or ""}}, pause=0.8)
    oda.call("HentData_KritChanged", pause=0.6)


def select_all_output(datarun_html):
    ids = re.findall(r'<input type="checkbox" id="(OutFelt_\d+)"',
                     html.unescape(datarun_html))
    if ids:
        oda.call("HentData_GetOutput",
                 lists={"checkBoxes": {k: "true" for k in ids}}, pause=0.8)
    return len(ids)


def download_csv(timeout=600):
    req = urllib.request.Request(oda.BASE + "getcsv.aspx?type=HentData",
                                 headers={"User-Agent": oda.UA})
    with oda._op.open(req, timeout=timeout) as r:
        return r.read()


def looks_like_error(data):
    head = data[:400].decode("iso-8859-1", "replace")
    return data.count(b"\n") <= 1 and ("msg " in head or "Column " in head)


def run(topic, frm, to, batch, limit):
    os.makedirs(DEST, exist_ok=True)
    spec = TOPICS[topic]
    log(f"logging in as {EMAIL}")
    oda.login(EMAIL)
    oda.save()
    urllib.request.Request  # session is warmed by main.aspx below
    req = urllib.request.Request(oda.BASE + "topic.aspx?id=h&t=h",
                                 headers={"User-Agent": oda.UA})
    oda._op.open(req, timeout=60).read()
    oda.call("topic_MakeTabsBar", lists={"hiddenFields": {"tab": ""}}, pause=0.8)

    log(f"topic: {spec['what']}")
    panes = open_topic(spec["emne"])
    crit = criterion_ids(panes["HentData_FillKriteriumRun"])
    log("  criteria: " + ", ".join(f"{k}={v[0]}" for k, v in crit.items()))
    key = next((k for k in crit if "ObservationsstedNr" in k), None)
    if not key:
        log("  no station criterion; aborting")
        return 1
    field_id, sltype = crit[key]

    stations = station_list(field_id, sltype)
    log(f"  {len(stations):,} stations offered")
    reg = os.path.join(DEST, f"{topic}_stations.tsv")
    with open(reg, "w", encoding="utf-8") as f:
        f.write("checkbox\tnr\tname\n")
        for r in stations:
            f.write("\t".join(r) + "\n")
    if limit:
        stations = stations[:limit]

    nfields = select_all_output(panes["HentData_FillDataRun"])
    log(f"  {nfields} output fields selected")

    parts, rows_total = [], 0
    for i in range(0, len(stations), batch):
        chunk = stations[i:i + batch]
        big = select_stations(field_id, sltype, [c[0] for c in chunk])
        set_period(frm, to)
        select_all_output(panes["HentData_FillDataRun"])
        if big:
            log(f"  [{i//batch+1}] server flags this extract as large; "
                f"reduce --batch and retry")
            return 2
        data = download_csv()
        if looks_like_error(data):
            log(f"  [{i//batch+1}] server error: "
                f"{data[:200].decode('iso-8859-1','replace').strip()}")
            return 3
        lines = data.decode("iso-8859-1").splitlines()
        parts.append(lines if not parts else lines[1:])
        rows_total += len(lines) - 1
        log(f"  [{i//batch+1}/{(len(stations)+batch-1)//batch}] "
            f"stations {i+1}-{i+len(chunk)}: {len(lines)-1:,} rows "
            f"({rows_total:,} total)")
        time.sleep(2.0)

    out = os.path.join(DEST, f"{topic}.csv")
    with open(out, "w", encoding="utf-8") as f:
        for p in parts:
            f.write("\n".join(p) + "\n")
    log(f"\nwrote {out} ({os.path.getsize(out)/1e6:.1f} MB, {rows_total:,} rows)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic", choices=sorted(TOPICS))
    ap.add_argument("--from", dest="frm", default=None, help="yyyy-mm-dd")
    ap.add_argument("--to", dest="to", default=None, help="yyyy-mm-dd")
    ap.add_argument("--batch", type=int, default=250, help="stations per request")
    ap.add_argument("--limit", type=int, default=0, help="stop after N stations")
    a = ap.parse_args(argv)
    return run(a.topic, a.frm, a.to, a.batch, a.limit)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
