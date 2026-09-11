#!/usr/bin/env python3
"""What size of signal could this archive have seen? Synthetic recovery on the real schedule.

cycles.py found no diurnal variation in surface oxygen once season and site were
removed. That is a null, and a null is the weakest thing a measurement can
produce, because it cannot distinguish "the effect is absent" from "the
instrument could not have seen it".

This converts it into a bound, and it needs no model of how the sea works. The
method is to stipulate a signal - a diurnal cycle of known amplitude, keyed to
the sun's elevation, which is the shape photosynthesis would produce - impose it
on the REAL sample instants and positions, and run the estimator cycles.py runs.
If the estimator recovers most of a large amplitude and nothing of a small one,
the detection limit lies between, and the observed null says the true amplitude
is under it. Nothing here claims the sea behaves this way; the question is only
whether this schedule and this estimator could have SEEN it if it did.

APPLES TO APPLES. The comparison is fair only if the synthetic recovery is
measured exactly as the real spread is, so nothing here re-implements the
estimator. The samples come from cycles.read_samples() - the same filters, the
same clock - and the observed spread and every recovery come from
cycles.deviations(), with the same window, the same sun bins and the same rule
for which bins are thick enough to count. An earlier version used its own fixed
ten-day cells, coarser bins, a clock read as UTC, and an observed spread typed in
by hand from a run with different bins. Every one of those differences let the
simulation see more than the real estimator could.

THE CLOCK. Only instants scripts/clock.py classes as observed are used. A
filled-in default is not a sampling time, and a supplier whose clock convention
is mixed cannot be placed against the sun.

THE NOISE is measured, not assumed, and measured where the signal under test
cannot reach it: the residual of samples whose window neighbours all share their
sun bin, where no diurnal variance can enter whatever its size.

MANY DRAWS. Every amplitude is run on many noise draws, and the bound is where
the recovered spread reaches the observed one in nearly all of them. The draws
at zero amplitude are the null: how often no cycle at all produces a spread as
large as the one observed.

WHAT IT ALSO TESTS. The same synthetic signal is recovered twice, once on the
real instants and once with each sample's time of day redrawn uniformly, and the
difference is the cost of the working day - in mg/l, not in rhetoric.

    python3 scripts/detectable.py

Writes data/derived/detectable.json.
"""
import collections
import datetime as dt
from array import array
import json
import math
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, ROOT, log
from cycles import PARAMS, deviations, read_samples, sun_bin
from daylight import solar_elevation

OUT = os.path.join(DERIVED, "detectable.json")
AMPLITUDES = [0.0, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0, 2.0]
DRAWS = 40           # noise draws per amplitude on the real instants
EVEN_DRAWS = 10      # draws of redrawn times of day, for the cost of the working day
# The bound is the smallest amplitude whose recovered spread reaches the observed
# one in at least this share of draws. One draw per amplitude, as an earlier
# version used, cannot say where the observed spread falls: at a small amplitude
# a single draw lands anywhere across a range wider than the signal.
LEVEL = 0.95
WINDOW = 10          # +-days: cycles.py's tightest window
# A sun bin counts toward a spread only with at least this many samples; thinner
# bins are noise-dominated. The same rule is applied to the real samples and to
# every synthetic run, whose bins it therefore selects in exactly the same way.
MIN_BIN_N = 1000
BASE = 10.0          # mg/l; a constant, which every deviation removes


def spread(dev):
    """Largest minus smallest mean deviation across the bins thick enough to count."""
    use = {b: x["dev"] for b, x in dev.items() if x["n"] >= MIN_BIN_N}
    if len(use) < 2:
        return None, sorted(use)
    return max(use.values()) - min(use.values()), sorted(use)


def noise_where_no_signal(samples):
    """Residual sd from samples whose window neighbours all share their sun bin.

    A deviation from the mean of k neighbours has variance sd^2 * (1 + 1/k), and
    cycles.deviations() adds that same inflation to every synthetic value, so each
    residual is scaled by sqrt(k / (k + 1)) to recover the sd of one value."""
    by_station = collections.defaultdict(list)
    for s in samples:
        by_station[s[0]].append(s)
    devs, with_neighbours, single = [], 0, 0
    for rows in by_station.values():
        rows.sort(key=lambda r: r[1])
        ords = [r[1] for r in rows]
        lo = hi = 0
        for i, r in enumerate(rows):
            while ords[lo] < r[1] - WINDOW:
                lo += 1
            while hi < len(rows) and ords[hi] <= r[1] + WINDOW:
                hi += 1
            nb = [rows[j] for j in range(lo, hi) if j != i]
            if not nb:
                continue
            with_neighbours += 1
            if all(x[3]["sun"] == r[3]["sun"] for x in nb):
                single += 1
                k = len(nb)
                devs.append((r[2] - sum(x[2] for x in nb) / k) * math.sqrt(k / (k + 1)))
    sd = statistics.stdev(devs) if len(devs) > 100 else None
    return sd, len(devs), with_neighbours, single


def elevations(real, rng=None):
    """Sun elevation at every sample's instant - or, given an rng, at a time of day
    redrawn uniformly for each sample. Computed once and reused across amplitudes
    and draws: only the amplitude and the noise differ between runs."""
    out = array("f")
    for _, _, _, _, utc, (lon, lat) in real:
        when = utc if rng is None else (dt.datetime.combine(utc.date(), dt.time())
                                        + dt.timedelta(minutes=rng.randrange(1440)))
        out.append(solar_elevation(lat, lon, when))
    return out


def recover(real, els, amp, rng, noise):
    """Impose a cycle of amplitude `amp` at the given sun elevations, then run the
    real estimator on it. Returns the recovered spread, measured as the real one is."""
    synth = []
    for (st, o, _, _, _, _), el in zip(real, els):
        # proportional to sun above the horizon: the shape photosynthetic
        # production would impose. `amp` is the coefficient on the sine, not the
        # peak-to-trough swing: the swing from night to noon is amp times the sine
        # of that day's noon elevation, so it is less than amp on every Danish day.
        s = amp * (max(0.0, math.sin(math.radians(max(el, 0.0)))) - 0.5)
        synth.append((st, o, BASE + s + rng.gauss(0.0, noise), {"sun": sun_bin(el)}))
    dev, _ = deviations(synth, WINDOW, "sun")
    got, _ = spread(dev)
    return got if got is not None else 0.0


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(p * len(v)))]


def main(argv):
    log("reading the real sample set through cycles.read_samples()")
    store, info = read_samples({}, {"Oxygen indhold": PARAMS["Oxygen indhold"]})
    real = store["o2"]
    if not real:
        raise SystemExit("no surface oxygen samples with an observed clock")
    dev, _ = deviations(real, WINDOW, "sun")
    observed, bins_used = spread(dev)
    if observed is None:
        raise SystemExit("fewer than two sun bins are thick enough to measure a spread")
    noise, noise_n, with_nb, single = noise_where_no_signal(real)
    if noise is None:
        raise SystemExit("too few single-bin samples to measure the noise; refusing "
                         "to assume one")
    log(f"  {len(real):,} samples with an observed clock; observed spread "
        f"{observed:.4f} mg/l over {', '.join(bins_used)}")
    log(f"  noise sd {noise:.4f} mg/l from {noise_n:,} samples whose neighbours "
        f"share their sun bin ({single:,} of {with_nb:,} with a neighbour)")

    out = {"_what": "Recovery of a stipulated diurnal signal imposed on the REAL "
                    "sample instants and positions of the archive, measured with "
                    "the estimator cycles.py uses on the real data, over many noise "
                    "draws per amplitude.",
           "_not": "This claims nothing about how the sea behaves. It asks only "
                   "whether this schedule and this estimator could have SEEN a "
                   "signal of a given size.",
           "n_samples": len(real),
           "clock_excluded": {k: v for k, v in info["clock"].items() if k != "observed"},
           "noise_sd_mg_l": round(noise, 4),
           "noise_n": noise_n,
           "samples_with_neighbours": with_nb,
           "samples_single_bin": single,
           "window_days": WINDOW,
           "min_bin_n": MIN_BIN_N,
           "draws": DRAWS, "even_draws": EVEN_DRAWS, "level": LEVEL,
           "observed_real_spread_mg_l": round(observed, 4),
           "observed_bins": bins_used,
           "runs": []}

    log("  sun elevations: the real instants, and redrawn times of day")
    els_real = elevations(real)
    els_even = [elevations(real, random.Random(1000 + i)) for i in range(EVEN_DRAWS)]
    log(f"\n{'imposed':>9} {'recovered, real hours':>24} {'if round the clock':>19} "
        f"{'draws >= observed':>18}")
    for amp in AMPLITUDES:
        # draw i uses the same seed at every amplitude, so amplitudes differ by
        # the signal alone within a draw
        got = [recover(real, els_real, amp, random.Random(1 + i), noise) for i in range(DRAWS)]
        even = [recover(real, els_even[i], amp, random.Random(501 + i), noise)
                for i in range(EVEN_DRAWS)]
        reach = sum(g >= observed for g in got) / DRAWS
        r = {"imposed": amp,
             "recovered_real_hours": round(statistics.median(got), 4),
             "recovered_real_p05": round(q(got, 0.05), 4),
             "recovered_real_p95": round(q(got, 0.95), 4),
             "recovered_even_hours": round(statistics.median(even), 4),
             "share_at_or_above_observed": round(reach, 3)}
        r["fraction_recovered"] = round(r["recovered_real_hours"] / amp, 3) if amp else None
        out["runs"].append(r)
        log(f"{amp:9.2f} {r['recovered_real_hours']:10.4f} ({r['recovered_real_p05']:.4f}-"
            f"{r['recovered_real_p95']:.4f}) {r['recovered_even_hours']:12.4f} {reach:17.0%}")

    out["null_share_at_or_above_observed"] = out["runs"][0]["share_at_or_above_observed"]
    out["noise_ceiling_mg_l"] = out["runs"][0]["recovered_real_p95"]
    limit = next((r["imposed"] for r in out["runs"]
                  if r["imposed"] and r["share_at_or_above_observed"] >= LEVEL), None)
    out["detection_limit_mg_l"] = limit
    log(f"\nWith no cycle at all, {out['null_share_at_or_above_observed']:.0%} of draws "
        f"reach the observed spread of {observed:.4f} mg/l.")
    if limit is not None:
        log(f"An imposed cycle of {limit} mg/l reaches it in at least {LEVEL:.0%} of draws: "
            f"the real surface diurnal amplitude is below about {limit} mg/l.")
    else:
        log("No imposed amplitude reaches the observed spread reliably: this schedule "
            "cannot bound the diurnal cycle at all, which is itself the finding.")

    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"wrote {os.path.relpath(OUT, ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
