"""One continuous time axis for the water-chemistry archive.

Time is continuous, and where the sun stood follows from an instant and a
position. The archive's `Startklok` breaks that: it is not UTC, as the technical
instruction asks, and it is not one thing. Measured by scripts/clockzone.py, per
supplier and era, it holds

  - filled-in DEFAULTS that are not times at all;
  - Danish wall-clock times with the summer or winter offset ADDED (the old era);
  - Danish wall-clock times (from the changeover on);

so every analysis that needs to know WHEN a sample was taken - where the sun
stood, whether it was dark - goes through instant() and nowhere else. It returns
one UTC instant, or says why there is none, and never guesses:

  observed    a real sampling time, converted by the convention its supplier and
              era were measured to use
  default     a filled-in value, not a time
  ambiguous   the supplier's convention in that era is mixed, or could not be
              tested and the era as a whole is mixed too
  untestable  before summer time existed a convention cannot be seen, and the
              value is not a known default
  none        no clock value

The conventions are measured, not assumed: this module reads
data/derived/clock_convention.json and refuses to run without it.
"""
import datetime as dt
import json
import os

from common import DERIVED

CONVENTION = os.path.join(DERIVED, "clock_convention.json")

# Eras, from the year-by-year test in clockzone.py: every year from the first
# summer time to the late nineties jumps one way, the next few years are mixed,
# and from then on the clock does not jump at all. The boundaries are the years
# where that happens; the per-year evidence is stored with the conventions.
ERAS = (("to-1980", 1980), ("1981-1998", 1998), ("1999-2001", 2001), ("2002-", 9999))
# Before the changeover ended, two values stand in for "no time": once the added
# offset is taken off they read exactly noon and three in the morning, local,
# and they alternate with summer time like everything else run through the same
# conversion. From then on the same clock readings are ordinary times.
DEFAULTS_UNTIL = 2001
DEFAULT_LOCAL = (12 * 60, 3 * 60)          # minutes after local midnight
CLASSES = ("observed", "default", "ambiguous", "untestable", "none")


def last_sunday(y, m):
    d = dt.date(y, m, 30 if m in (4, 6, 9, 11) else 31)
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def summer_time(y):
    """(start, end) of Danish summer time in year y, or None. None before 1980;
    1980 began on 6 April; it ended on the last Sunday of September until 1995
    and of October from 1996, when the EU rule was harmonised."""
    if y < 1980:
        return None
    start = dt.date(1980, 4, 6) if y == 1980 else last_sunday(y, 3)
    return start, last_sunday(y, 9 if y <= 1995 else 10)


def offset(d):
    """Hours Danish legal time is ahead of UTC on date d."""
    s = summer_time(d.year)
    return 2 if s and s[0] <= d < s[1] else 1


def changes(y):
    s = summer_time(y)
    return [("spring", s[0]), ("autumn", s[1])] if s else []


def era_of(y):
    return next(label for label, upper in ERAS if y <= upper)


def is_default_candidate(minutes, o):
    return (minutes - 60 * o) % 1440 in DEFAULT_LOCAL


def parse(klok):
    """'400' -> 240 minutes; '1330' -> 810. Blank or nonsense -> None."""
    s = (klok or "").strip()
    if not s.isdigit():
        return None
    h, m = divmod(int(s), 100)
    return h * 60 + m if h <= 23 and m <= 59 else None


_conv = {}


def _load():
    if "c" not in _conv:
        if not os.path.exists(CONVENTION):
            raise RuntimeError("data/derived/clock_convention.json is missing - run "
                               "scripts/clockzone.py first; clock conventions are "
                               "measured, not assumed")
        _conv["c"] = json.load(open(CONVENTION, encoding="utf-8"))
    return _conv["c"]


def convention(era, supplier):
    """(verdict, how it was reached) for one supplier in one era."""
    c = _load()
    cell = c["cells"].get(f"{era} | {supplier}")
    if cell and cell["verdict"] != "untested":
        return cell["verdict"], "measured for this supplier"
    return c["eras"][era]["verdict"], "inherited from the era"


def instant(supplier, startdato, startklok):
    """(UTC datetime or None, class) for one row of the water-chemistry extract."""
    d, minutes = (startdato or "").strip(), parse(startklok)
    if minutes is None or len(d) != 8 or not d.isdigit():
        return None, "none"
    try:
        day = dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))
    except ValueError:
        return None, "none"
    o = offset(day)
    if day.year <= DEFAULTS_UNTIL and is_default_candidate(minutes, o):
        return None, "default"
    verdict, _ = convention(era_of(day.year), (supplier or "").strip())
    back = {"wall": o, "offset-added": 2 * o, "utc": 0}.get(verdict)
    if back is None:
        return None, "untestable" if verdict == "no summer time" else "ambiguous"
    return dt.datetime.combine(day, dt.time()) + dt.timedelta(minutes=minutes - 60 * back), \
        "observed"
