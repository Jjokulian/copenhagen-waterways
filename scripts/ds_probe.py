#!/usr/bin/env python3
"""Whether the services docs/DATA_SOURCES.md describes answer as it says - asked, dated,
stored.

A catalogue says "this server needs no authentication", "that host answers 403", "the
old geoserver no longer resolves". Each is true on the day somebody looked. This asks
again and writes what came back, with the date, so the page states an observation it
can show rather than one it remembers. The two WFS servers' GetCapabilities are also
counted: how many layers each offers, anonymously.

    python3 scripts/ds_probe.py      # -> data/derived/ds_probes.json (needs the network)
"""
import datetime
import os
import re
import socket
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, log, write_json

OUT = os.path.join(DERIVED, "ds_probes.json")
UA = "copenhagen-waterways research (github.com/Jjokulian/copenhagen-waterways)"
PROBES = {
    "kbhkort_wfs": "https://wfs-kbhkort.kk.dk/k101/ows?service=WFS&version=1.1.0&request=GetCapabilities",
    "vp3_wfs": "https://wfs2-miljoegis.mim.dk/vp3basis2019/ows?service=WFS&version=1.1.0&request=GetCapabilities",
    "opendata_admin_api": "https://admin.opendata.dk/api/3/action/package_search?q=organization:city-of-copenhagen",
    "opendata_www_api": "https://www.opendata.dk/api/3/action/package_search?q=organization:city-of-copenhagen",
    "miljoeportal_support": "https://support.miljoeportal.dk/",
}
RESOLVE = {"old_puls_geoserver": "b0902-prod-dist-app.azurewebsites.net"}


def ask(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:                      # no answer is an answer too
        return None, type(e).__name__.encode()


def main():
    today = datetime.date.today().isoformat()
    out = {"_what": "What each service answered to an anonymous request, and when.",
           "checked": today}
    for name, url in PROBES.items():
        status, body = ask(url)
        rec = {"url": url, "status": status}
        if status is None:
            rec["error"] = body.decode()
        if name.endswith("_wfs") and status == 200:
            rec["layers"] = len(re.findall(rb"<(?:wfs:)?FeatureType[\s>]", body))
        out[name] = rec
        log(f"  {name}: {status}" + (f", {rec['layers']} layers" if "layers" in rec else ""))
    for name, host in RESOLVE.items():
        try:
            socket.getaddrinfo(host, 443)
            ok = True
        except socket.gaierror:
            ok = False
        out[name] = {"host": host, "resolves": ok}
        log(f"  {name}: resolves={ok}")
    write_json(OUT, out)
    log(f"wrote {os.path.relpath(OUT)}")


if __name__ == "__main__":
    main()
