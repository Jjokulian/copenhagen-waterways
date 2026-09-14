"""Figures read out of pinned documents.

data/manual/nitrogen_readings.json holds each figure with the source it comes from and
the exact phrase it sits in; rv() refuses one whose phrase is no longer in the pinned
copy. diffuse() assembles the national diffuse-load figures the pages print, each from
the report that states it - one reader, used by every page that prints them.
"""
import html
import os
import re

import claims
import live
from common import MANUAL

READ = live.live_json(os.path.join(MANUAL, "nitrogen_readings.json"))
_pins = {}
_cl = []


def _norm(t):
    """A pin as text: for a web page, HTML entities decoded and tags dropped; for any
    pin, whitespace collapsed. (A PDF's text keeps its '<' and '>' - stripping
    "tags" there would eat the prose between a stray pair.)"""
    head = t[:4000].lower()
    if "<html" in head or "<!doctype" in head:
        t = re.sub(r"<[^>]+>", " ", html.unescape(t))
    return re.sub(r"\s+", " ", t).strip()


def _pin(sid):
    if sid not in _pins:
        if not _cl:
            _cl.append(claims.load()[0])
        _pins[sid] = _norm(claims.pin_text(_cl[0], sid))
    return _pins[sid]


def rv(key):
    """A value read out of a pinned document - refused unless its phrase is there."""
    e = READ["pinned"][key]
    if _norm(e["phrase"]) not in _pin(e["source"]):
        raise live.Unjustified(f"nitrogen_readings.json pinned.{key}: the phrase "
                               f"'{e['phrase']}' is not in the pinned text of {e['source']}")
    return e["value"]


def diffuse():
    """The national diffuse-load figures, each read from the report that states it: the
    stations behind the nitrogen load and their share of Denmark's area from DCE's stream
    report for 2018 (SR353); the grab-sample deviations from the 2018 comparison in Vand &
    Jord; the uncertainty of retention from the national nitrogen model's method report
    (NKM2020). The modelled share is what the stations do not cover."""
    meas = rv("sr353_n_area_pct")
    return {"stream_stations": rv("sr353_n_stations"),
            "area_measured_pct": meas, "area_modelled_pct": 100 - meas,
            "deviation_annual_pct": [rv("vj_dev_jegstrup_monthly"), rv("vj_dev_monthly")],
            "retention_uncertainty_pct_points": [rv("nkm_ret_lo"), rv("nkm_ret_hi")],
            "retention_uncertainty_national_average_pct_points": rv("nkm_ret_avg")}
