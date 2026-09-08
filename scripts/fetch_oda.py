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

Written for a small machine. This VM has ~3 GB of RAM and /tmp is a 1 GB tmpfs, so
a response held in memory is a response competing with everything else. Every
download streams to disk in chunks and is never materialised as a single object;
each batch is appended to the output file and forgotten; the output file is replaced
at the start of a run rather than grown; and the run stops on its own if it would
exceed --max-mb or leave less than MIN_FREE_MB on the volume. Storage that must be
replaced rather than filled without care is the constraint, not an afterthought.

Topics (Hav):
    stations   Observationssted   the register: id, name, water body, UTM32, dates
    ctd        Feltmaaling/CTD    oxygen, temperature, salinity by depth
    kemi       Vandkemi           nutrients and chlorophyll
    sediment   Sedimentkemi       what is in the bed
    fauna      Bundfauna          the soft-bottom survey

Usage:
    python3 scripts/fetch_oda.py stations
    python3 scripts/fetch_oda.py ctd --from 1970-01-01 --to 2026-12-31 --years 5
"""
import argparse
import gzip
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


def option_list(field_id, sltype):
    """Every option in a multiselect, whatever its label looks like.

    station_list expects the station format, "number (name)". Parameter options are
    bare text - FDOM, Oxygen indhold, Salinitet - so matching on the station shape
    returns an empty list and the criterion is silently left unset, which the server
    reports as a header with no rows rather than as an error."""
    c, o = oda.call("SCL2_FillMultiSelectList",
                    {"srchStr": "", "SLType": sltype, "SelectBoxId": field_id,
                     "method": "SCL2_FillMultiSelectList"}, pause=1.2)
    return re.findall(r'id="(SCL2CB_\d+)"[^>]*/>\s*([^<]{1,80}?)\s*<',
                      html.unescape(o))


def select_stations(field_id, sltype, checkbox_ids):
    """Add these stations to the station criterion.

    Two traps live here, both learned the hard way.

    SCL2_SelectMultiSelectList *adds* to whatever is already selected rather than
    replacing it, so batching over stations re-downloads every earlier batch and the
    extract grows quadratically - the first run of this cost 1.46 GB to fetch 153 MB
    of register. HentData_NulstilCond does clear the criteria, but it also makes the
    server regenerate every criterion field with fresh ids, so a cached field id then
    points at a field that no longer exists and the selection silently does nothing.

    So: stations are selected once, in full, and batching is done over time instead,
    where setting a period replaces the previous one. Criterion ids are re-read from
    the pane on every use and never cached across a rebuild."""
    oda.call("SCL2_SelectMultiSelectList",
             {"SLType": sltype, "SelectBoxId": field_id},
             lists={"checkBoxes": {k: "true" for k in checkbox_ids}}, pause=1.2)
    c, o = oda.call("HentData_KritChanged", pause=0.8)
    # HentDataStor=true means the extract is too big to stream and must be ordered
    return "HentDataStor=true" in o


def dk_date(iso):
    """The datepicker round-trips Danish dd-mm-yyyy.

    Sending ISO silently produces an empty result rather than an error: the server
    accepts the string, fails to parse it into a range, and getcsv.aspx returns a
    header and no rows - indistinguishable from "no data in this period", which is
    how an afternoon goes missing."""
    if not iso:
        return ""
    p = iso.split("-")
    return f"{p[2]}-{p[1]}-{p[0]}" if len(p) == 3 else iso


def set_period(frm, to):
    if not frm and not to:
        return
    oda.call("SCL2_DatePicked", lists={"textFields": {
        "SCL2PeriodFrom": dk_date(frm), "SCL2PeriodTo": dk_date(to)}}, pause=0.8)
    oda.call("HentData_KritChanged", pause=0.6)


def select_all_output(datarun_html):
    ids = re.findall(r'<input type="checkbox" id="(OutFelt_\d+)"',
                     html.unescape(datarun_html))
    if ids:
        oda.call("HentData_GetOutput",
                 lists={"checkBoxes": {k: "true" for k in ids}}, pause=0.8)
    return len(ids)


CHUNK = 1 << 16
MIN_FREE_MB = 512      # never take the volume below this


def free_mb(path):
    st = os.statvfs(path)
    return st.f_bavail * st.f_frsize / 1e6


def stream_csv(out_fh, skip_header, budget_mb, timeout=900):
    """Stream one extract straight to an open file. Returns (rows, bytes, error).

    Never holds the response in memory: reads in 64 KB chunks, keeps only enough
    to find the first newline, and stops early if the batch would blow the budget.
    The server reports failures as a one-line CSV whose first field is a message,
    so the head of the stream is inspected before anything is written."""
    req = urllib.request.Request(oda.BASE + "getcsv.aspx?type=HentData",
                                 headers={"User-Agent": oda.UA})
    rows = written = 0
    head, checked, dropped_header = b"", False, not skip_header
    with oda._op.open(req, timeout=timeout) as r:
        while True:
            buf = r.read(CHUNK)
            if not buf:
                break
            if not checked:
                head += buf
                if len(head) < 400 and b"\n" not in head:
                    continue
                probe = head[:400].decode("iso-8859-1", "replace")
                if "msg " in probe or "Column " in probe or "Fejl" in probe:
                    return 0, 0, probe.strip()[:200]
                checked, buf, head = True, head, b""
            if not dropped_header:
                nl = buf.find(b"\n")
                if nl < 0:
                    continue
                buf, dropped_header = buf[nl + 1:], True
            rows += buf.count(b"\n")
            written += len(buf)
            out_fh.write(buf)
            if budget_mb and written / 1e6 > budget_mb:
                return rows, written, f"batch exceeded budget of {budget_mb:.0f} MB"
    return rows, written, None


def halve(a, b):
    """Split one period in two. Returns [] once it is down to a single day."""
    if not a or not b:
        return []
    import datetime as dt
    d0 = dt.date(*map(int, a.split("-")))
    d1 = dt.date(*map(int, b.split("-")))
    if (d1 - d0).days < 1:
        return []
    mid = d0 + (d1 - d0) // 2
    nxt = mid + dt.timedelta(days=1)
    return [(a, mid.isoformat()), (nxt.isoformat(), b)]


def split_periods(frm, to, years):
    """Slice the requested span into chunks of `years`, or one open request.

    Setting a period replaces the previous one, unlike the station criterion, so
    this is the axis it is safe to batch on."""
    if not years or not frm or not to:
        return [(frm, to)]
    y0, y1 = int(frm[:4]), int(to[:4])
    out = []
    y = y0
    while y <= y1:
        e = min(y + years - 1, y1)
        out.append((f"{y}-01-01" if y > y0 else frm,
                    f"{e}-12-31" if e < y1 else to))
        y = e + 1
    return out


def run(topic, frm, to, years, limit, max_mb):
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

    # The station list is period-dependent, and the default state offers only the
    # CURRENTLY ACTIVE network. For CTD that is 185 stations against 1,527 in the
    # record - so listing before setting the period silently discards seven eighths
    # of the history, which is exactly the era this project cares about. Set the
    # period first, always.
    set_period(frm, to)
    stations = station_list(field_id, sltype)
    log(f"  {len(stations):,} stations offered for {frm or 'start'}..{to or 'end'}")
    reg = os.path.join(DEST, f"{topic}_stations.tsv")
    with open(reg, "w", encoding="utf-8") as f:
        f.write("checkbox\tnr\tname\n")
        for r in stations:
            f.write("\t".join(r) + "\n")
    if limit:
        stations = stations[:limit]

    nfields = select_all_output(panes["HentData_FillDataRun"])
    log(f"  {nfields} output fields selected")

    # gzip on the way out. These extracts are wide, repetitive text - station name
    # and instrument metadata repeated on every row - and compress about tenfold,
    # which is the difference between fitting on this disk and not.
    out = os.path.join(DEST, f"{topic}.csv.gz")
    log(f"  {free_mb(DEST):,.0f} MB free; budget {max_mb:,} MB (compressed)")

    # One station selection for all of them; the criterion accumulates, so doing
    # this once is both correct and cheapest.
    select_stations(field_id, sltype, [c[0] for c in stations])

    # Some topics have more than one obligatory criterion. CTD needs Parameter set
    # as well as the station list: leave it empty and the server throws inside
    # GetCount building its WHERE clause, and getcsv.aspx returns a header with no
    # rows - which looks exactly like "there is no data for this period". Select
    # everything in every remaining multiselect.
    for label, (fid2, slt2) in crit.items():
        if fid2 == field_id:
            continue
        opts = option_list(fid2, slt2)
        if opts:
            oda.call("SCL2_SelectMultiSelectList",
                     {"SLType": slt2, "SelectBoxId": fid2},
                     lists={"checkBoxes": {o[0]: "true" for o in opts}}, pause=1.0)
            log(f"  {label}: all {len(opts)} selected")
    oda.call("HentData_KritChanged", pause=0.8)
    select_all_output(panes["HentData_FillDataRun"])

    # A work queue rather than a fixed list: a period the server refuses to stream
    # is halved and both halves go back on the queue. Data density varies enormously
    # across the record - the 1970s are thin and the 2000s are not - so a single
    # chunk size is either wasteful early or refused late.
    queue = list(reversed(split_periods(frm, to, years)))
    rows_total = bytes_total = 0
    done = 0
    with gzip.open(out, "wb", compresslevel=6) as fh:   # replace, never grow
        while queue:
            a, b = queue.pop()
            n = done + 1
            if a or b:
                set_period(a, b)
                select_all_output(panes["HentData_FillDataRun"])
            # The size flag is only meaningful once the period is applied - checked
            # before that, it describes the whole record and is always true.
            c, o = oda.call("HentData_KritChanged", pause=0.6)
            if "HentDataStor=true" in o:
                halves = halve(a, b)
                if halves:
                    log(f"  [{n}] {a}..{b} too large to stream; splitting")
                    queue.extend(reversed(halves))
                    continue
                log(f"  [{n}] {a}..{b} too large to stream and cannot be split "
                    f"further. The portal wants this ordered rather than streamed.")
                return 2
            room = min((max_mb - bytes_total) * 10, free_mb(DEST) - MIN_FREE_MB)
            if room <= 0:
                log(f"  [{n}] stopping: budget or free space exhausted "
                    f"({bytes_total:,.0f} MB written, "
                    f"{free_mb(DEST):,.0f} MB free)")
                break
            rows, nbytes, err = stream_csv(fh, skip_header=(done > 0), budget_mb=room)
            if err:
                log(f"  [{n}] {err}")
                return 3
            rows_total += rows
            done += 1
            fh.flush()
            bytes_total = os.path.getsize(out) / 1e6 if os.path.exists(out) else 0
            log(f"  [{n}, {len(queue)} left] {a or 'start'}..{b or 'end'}: "
                f"{rows:,} rows, {nbytes/1e6:,.1f} MB raw "
                f"({rows_total:,} rows, {bytes_total:,.0f} MB on disk)")
            time.sleep(2.0)
    log(f"\nwrote {out} ({os.path.getsize(out)/1e6:,.1f} MB, {rows_total:,} rows)")
    log(f"  {free_mb(DEST):,.0f} MB still free")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("topic", choices=sorted(TOPICS))
    ap.add_argument("--from", dest="frm", default=None, help="yyyy-mm-dd")
    ap.add_argument("--to", dest="to", default=None, help="yyyy-mm-dd")
    ap.add_argument("--years", type=int, default=0,
                    help="split the period into chunks of this many years "
                         "(needs --from and --to); 0 requests it in one go")
    ap.add_argument("--limit", type=int, default=0, help="stop after N stations")
    ap.add_argument("--max-mb", type=int, default=2000,
                    help="stop before the output exceeds this many MB")
    a = ap.parse_args(argv)
    return run(a.topic, a.frm, a.to, a.years, a.limit, a.max_mb)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
