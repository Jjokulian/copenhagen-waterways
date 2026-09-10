#!/usr/bin/env python3
"""Where the moon was, for rows that carry a clock.

Three cycles are laid over a Danish water sample and only one of them is the
sun. The synodic month moves moonlight, which drives the diel vertical migration
of zooplankton - the grazers - and it moves the tide, because spring tides fall
near new and full moon and neap tides near the quarters. The inner Danish waters
are close to microtidal (a few tens of centimetres in the Kattegat and the belts)
so the tidal term is small there; the North Sea coast is not, and the Wadden Sea
runs one and a half to two metres. A cycle being small is not the same as it
being absent, and it has never been looked for in this record.

WHAT IS HONESTLY COMPUTABLE HERE, and what is not.

Computable from the date alone, to well inside what matters:
  * the illuminated fraction of the moon's disc - the moonlight term
  * the phase angle, and so where in the spring-neap cycle a sample sits

Computable only because vandkemi carries a clock:
  * the moon's altitude above the horizon at the moment of sampling, which is
    what decides whether that moonlight reached the water at all, and which is
    also the lunar hour angle the semi-diurnal tide runs on

NOT computable here, and it should not be faked: the actual water level. A real
tide is the harmonic constituents of a particular place, and inferring height
from lunar phase alone would be a model of the moon presented as a measurement
of the sea. The right source is observation - DMI's oceanObs sea-level series,
already in DATA_QUEUE.md as an open fetch - joined on station and hour. Until
that is fetched, what is here is the forcing, not the response.

Meeus, low-precision series: about 10 arcminutes in longitude and 4 in latitude,
which is four hundred times finer than the question being asked of it.
"""
import datetime as dt
import math

D2R = math.pi / 180.0


def julian_century(when_utc):
    jd = (when_utc - dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + 2451545.0
    return (jd - 2451545.0) / 36525.0


def _moon_elements(t):
    """Mean elements, degrees. Meeus ch. 47."""
    return {
        "Lp": 218.3164477 + 481267.88123421 * t - 0.0015786 * t * t,
        "D":  297.8501921 + 445267.1114034 * t - 0.0018819 * t * t,
        "M":  357.5291092 + 35999.0502909 * t - 0.0001536 * t * t,
        "Mp": 134.9633964 + 477198.8675055 * t + 0.0087414 * t * t,
        "F":   93.2720950 + 483202.0175233 * t - 0.0036539 * t * t,
    }


def moon_ecliptic(t):
    """Apparent ecliptic longitude, latitude (degrees) and distance (km)."""
    e = _moon_elements(t)
    Lp, D, M, Mp, F = (e["Lp"], e["D"] * D2R, e["M"] * D2R, e["Mp"] * D2R, e["F"] * D2R)
    lon = (Lp
           + 6.288774 * math.sin(Mp)
           + 1.274027 * math.sin(2 * D - Mp)
           + 0.658314 * math.sin(2 * D)
           + 0.213618 * math.sin(2 * Mp)
           - 0.185116 * math.sin(M)
           - 0.114332 * math.sin(2 * F)
           + 0.058793 * math.sin(2 * D - 2 * Mp)
           + 0.057066 * math.sin(2 * D - M - Mp)
           + 0.053322 * math.sin(2 * D + Mp)
           + 0.045758 * math.sin(2 * D - M)
           - 0.040923 * math.sin(M - Mp)
           - 0.034720 * math.sin(D)
           - 0.030383 * math.sin(M + Mp))
    lat = (5.128122 * math.sin(F)
           + 0.280602 * math.sin(Mp + F)
           + 0.277693 * math.sin(Mp - F)
           + 0.173237 * math.sin(2 * D - F)
           + 0.055413 * math.sin(2 * D - Mp + F)
           + 0.046271 * math.sin(2 * D - Mp - F)
           + 0.032573 * math.sin(2 * D + F))
    dist = (385000.56
            - 20905.355 * math.cos(Mp)
            - 3699.111 * math.cos(2 * D - Mp)
            - 2955.968 * math.cos(2 * D)
            - 569.925 * math.cos(2 * Mp))
    return lon % 360.0, lat, dist


def _obliquity(t):
    return 23.439291 - 0.0130042 * t - 1.64e-7 * t * t + 5.04e-7 * t ** 3


def _gmst_deg(when_utc):
    """Greenwich mean sidereal time in degrees."""
    jd = (when_utc - dt.datetime(2000, 1, 1, 12)).total_seconds() / 86400.0 + 2451545.0
    t = (jd - 2451545.0) / 36525.0
    return (280.46061837 + 360.98564736629 * (jd - 2451545.0)
            + 0.000387933 * t * t) % 360.0


def moon_altitude(lat_deg, lon_deg, when_utc):
    """Moon's geometric altitude in degrees (centre, no refraction)."""
    t = julian_century(when_utc)
    lam, beta, _ = moon_ecliptic(t)
    eps = _obliquity(t) * D2R
    lam_r, beta_r = lam * D2R, beta * D2R
    ra = math.atan2(math.sin(lam_r) * math.cos(eps)
                    - math.tan(beta_r) * math.sin(eps), math.cos(lam_r))
    dec = math.asin(math.sin(beta_r) * math.cos(eps)
                    + math.cos(beta_r) * math.sin(eps) * math.sin(lam_r))
    ha = (_gmst_deg(when_utc) + lon_deg) * D2R - ra
    phi = lat_deg * D2R
    return math.degrees(math.asin(
        math.sin(phi) * math.sin(dec) + math.cos(phi) * math.cos(dec) * math.cos(ha)))


def moon_illumination(when_utc):
    """(illuminated fraction 0-1, phase angle in degrees).

    Phase angle 0 is full, 180 is new; the fraction is what a person sees."""
    t = julian_century(when_utc)
    e = _moon_elements(t)
    D, M, Mp = e["D"] * D2R, e["M"] * D2R, e["Mp"] * D2R
    i = (180.0 - e["D"] % 360.0
         - 6.289 * math.sin(Mp)
         + 2.100 * math.sin(M)
         - 1.274 * math.sin(2 * D - Mp)
         - 0.658 * math.sin(2 * D)
         - 0.214 * math.sin(2 * Mp)
         - 0.110 * math.sin(D)) % 360.0
    return (1.0 + math.cos(i * D2R)) / 2.0, i


def spring_neap(frac):
    """Where in the spring-neap cycle. Springs follow new and full by a day or
    two; this names the forcing, not the observed range at any given coast."""
    if frac > 0.90 or frac < 0.10:
        return "spring"
    if 0.35 < frac < 0.65:
        return "neap"
    return "mid"
