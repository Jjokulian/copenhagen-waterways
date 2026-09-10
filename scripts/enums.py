#!/usr/bin/env python3
"""Every distinct value in every enum-like column, across every extract.

Looking at the top six values of a column is how a rare sentinel survives. This
file found three that way: 9999999 for a missing y-intercept in the light data,
a depth of 99 on depth-integrated samples, and an oxygen saturation of 90,972%.
Each of them was a handful of rows in millions, and each would have moved a
published mean.

So: for every column of every extract, count the distinct values. Where a column
turns out to be categorical - a small closed set - print the whole set with
counts, because the whole set is the schema documentation nobody wrote. Where it
is a free measurement, print the range and the extremes instead, since that is
where a sentinel hides in a numeric column.

Counters are capped: a column that passes CARD_CAP distinct values is declared
high-cardinality and stops accumulating, so a 1.8 million row file cannot turn
into 1.8 million dict keys on a machine with 3 GB.

The numeric summary of those capped columns is a RESERVOIR sample, drawn evenly
across the file. The first version took the first 200,000 rows instead, and
these extracts are written in date order, so it reported the head of the record
as the range of the column: the light data, which runs 1980 to 2026, came back
with a 99th percentile of 2003 and looked like a truncated fetch. A summary from
a head sample is not a summary, and this file exists to catch exactly that kind
of quiet wrongness, so it should not have contained one.

    python3 scripts/enums.py              # every extract
    python3 scripts/enums.py kemi lys     # named ones

Writes data/derived/enums.json.
"""
import collections
import csv
import glob
import gzip
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, RAW, log

CARD_CAP = 300          # beyond this a column is not an enum
SHOW = 60               # print the full set up to this many values
OUT = os.path.join(DERIVED, "enums.json")


def numeric_summary(vals):
    """Range and extremes of a numeric column - where sentinels live."""
    nums = []
    for v in vals:
        try:
            nums.append(float(v.replace(",", ".")))
        except (ValueError, AttributeError):
            pass
    if len(nums) < 10:
        return None
    nums.sort()
    n = len(nums)
    return {"n_sampled": n, "min": nums[0], "p1": nums[n // 100], "p50": nums[n // 2],
            "p99": nums[99 * n // 100], "max": nums[-1],
            "top5_largest": nums[-5:]}


def scan(path, sample_numeric=200000):
    import random
    rng = random.Random(0)          # deterministic: the audit must be repeatable
    opener = gzip.open if path.endswith(".gz") else open
    counts, over, numsample = {}, set(), collections.defaultdict(list)
    rows = 0
    with opener(path, "rb") as fh:
        rd = csv.DictReader(io.TextIOWrapper(fh, encoding="latin-1"), delimiter=";")
        for row in rd:
            rows += 1
            for k, v in row.items():
                if k is None or k in over:
                    continue
                c = counts.setdefault(k, collections.Counter())
                c[v] += 1
                if len(c) > CARD_CAP:
                    over.add(k)
                    # keep a bounded numeric sample for the range summary
                    counts[k] = None
            # reservoir, not the head: an extract in date order would otherwise
            # report its own first year as the whole column's range
            for k in over:
                res = numsample[k]
                if len(res) < sample_numeric:
                    res.append(row.get(k))
                else:
                    j = rng.randrange(rows)
                    if j < sample_numeric:
                        res[j] = row.get(k)
    return rows, counts, over, numsample


def main(argv):
    files = sorted(glob.glob(os.path.join(RAW, "oda", "*.csv.gz")))
    files += [p for p in glob.glob(os.path.join(RAW, "oda", "*.csv"))]
    if argv:
        files = [f for f in files if any(a in os.path.basename(f) for a in argv)]
    out = {}
    for path in files:
        name = os.path.basename(path).split(".")[0]
        log(f"\n{'='*70}\n{name}  ({os.path.getsize(path)/1e6:.0f} MB)")
        rows, counts, over, numsample = scan(path)
        log(f"{rows:,} rows, {len(counts)} columns")
        rec = {"rows": rows, "categorical": {}, "high_cardinality": {}}
        for col in counts:
            if col in over:
                s = numeric_summary(numsample.get(col, []))
                rec["high_cardinality"][col] = s or "free text"
                if s:
                    log(f"  ~ {col:<32} numeric (sampled {s['n_sampled']:,})  "
                        f"min {s['min']:<12g} p50 {s['p50']:<12g} "
                        f"p99 {s['p99']:<12g} MAX {s['max']:g}")
                else:
                    log(f"  ~ {col:<32} free text / high cardinality")
                continue
            c = counts[col]
            rec["categorical"][col] = {str(k): v for k, v in c.most_common()}
            if len(c) <= SHOW:
                log(f"  = {col:<32} {len(c)} distinct")
                for v, n in c.most_common():
                    log(f"        {str(v)[:70]:<70} {n:>10,}")
            else:
                log(f"  = {col:<32} {len(c)} distinct (over {SHOW}, see json)")
        out[name] = rec

    os.makedirs(DERIVED, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log(f"\nwrote {os.path.relpath(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
