#!/usr/bin/env python3
"""Client for ODA (Overfladevandsdatabasen), the raw NOVANA surface-water database.

This is the primary record - individual measurements, per station, per date, per
depth, with the instrument named - rather than anyone's aggregate of it. Getting at
it is the precondition for scoring competing hypotheses against the same data.


The portal is a JS app that talks to Services.asmx over SOAP 1.1 with a custom
generic envelope: every web method takes no typed parameters, and the arguments
travel inside <xmlDoc><varTrees><dTree>. Reconstructed from MonoRail/JScript/main.js
(MR.Request, addArg, stringify) rather than from the WSDL, which types nothing.

Polite by construction: one request at a time, a real User-Agent naming the project,
and a delay between calls.
"""
import http.cookiejar
import os
import re
import sys
import time
import urllib.request

BASE = "https://odaforalle.au.dk/"
SVC = BASE + "Services.asmx"
NS = "http://MonoRail.carlbro.dk"
UA = "copenhagen-waterways research (github.com/Jjokulian/copenhagen-waterways)"

JAR = os.path.join(os.path.expanduser("~"), ".oda-session-cookies")
_jar = http.cookiejar.MozillaCookieJar(JAR)
try:
    _jar.load(ignore_discard=True)
except Exception:
    pass
_op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_jar))


def reset():
    """Drop any stored session.

    The server keeps topic, tool, criterion and aggregation state per session, and
    criterion field ids are regenerated as that state changes. Reusing yesterday's
    cookie therefore starts a run inside somebody else's half-configured form, and
    the failure is silent: the criterion pane comes back without the fields you are
    looking for, or the extract returns a header and no rows. Always start clean."""
    _jar.clear()
    try:
        os.remove(JAR)
    except OSError:
        pass


def login(email, fresh=True):
    if fresh:
        reset()
    c, o = call("Login_DoLogin", lists={"textF": {"email": email}})
    try:
        _jar.save(ignore_discard=True)
    except Exception:
        pass
    return c, o


def save():
    _jar.save(ignore_discard=True)


def esc(v):
    return (str(v).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def envelope(method, dtree=None, lists=None):
    def kv(d):
        return "".join(f"<{k}>{esc(v)}</{k}>" for k, v in (d or {}).items())
    extra = "".join(f"<{name}>{kv(d)}</{name}>" for name, d in (lists or {}).items())
    return ('<?xml version="1.0" encoding="utf-8"?>'
            '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            ' xmlns:xsd="http://www.w3.org/2001/XMLSchema"'
            ' xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>'
            f'<{method} xmlns="{NS}"><xmlDoc><varTrees>'
            f'<dTree>{kv(dtree)}</dTree>{extra}'
            f'</varTrees></xmlDoc></{method}></soap:Body></soap:Envelope>')


def call(method, dtree=None, lists=None, pause=1.0, timeout=300, tries=4):
    """One SOAP call, with patience.

    Selecting 1,527 stations makes the server do real work before it answers, and
    a slow answer is not a failed one - an unretried read timeout throws away an
    hour of downloading. Retries back off, and only on transport errors: an HTTP
    error is a real answer and is returned as one."""
    body = envelope(method, dtree, lists).encode("utf-8")
    for attempt in range(tries):
        req = urllib.request.Request(SVC, data=body, headers={
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": NS + "/" + method,
            "User-Agent": UA,
        })
        try:
            with _op.open(req, timeout=timeout) as r:
                out = r.read().decode("utf-8", "replace")
                code = r.status
            break
        except urllib.error.HTTPError as e:
            out = e.read().decode("utf-8", "replace")
            code = e.code
            break
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(5 * (attempt + 1))
    time.sleep(pause)
    return code, out


def text(x, limit=900):
    x = re.sub(r"<script.*?</script>", " ", x, flags=re.S | re.I)
    x = re.sub(r"<[^>]+>", " ", x)
    x = re.sub(r"&lt;[^&]*?&gt;", " ", x)
    return re.sub(r"\s+", " ", x).strip()[:limit]


if __name__ == "__main__":
    m = sys.argv[1] if len(sys.argv) > 1 else "AboutWnd"
    args = dict(a.split("=", 1) for a in sys.argv[2:])
    c, o = call(m, args)
    print("HTTP", c, len(o), "bytes")
    print(text(o, 2000))
