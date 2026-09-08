# copenhagen-waterways

## The machine will die if a script is careless with memory

This runs on a Qubes standalone VM. Memory is **balloon-managed and elastic** —
it grows automatically to roughly 4 GB, and can reach about 6 GB, but only when the
other qubes are closed and dom0 is willing. In practice the figure at any moment is
2.5–3.5 GB total with **under 1.2 GB actually available**.

**The elasticity is a trap, not a safety margin.** The balloon inflates with
latency, and qmemman has to decide to grant. A process that allocates faster than
the balloon can respond hits the ceiling that exists *now* rather than the one that
would exist in a few seconds. So the headroom cannot be planned against — a script
must be bounded at a size that fits the pessimistic case, and a slow steady climb
is far safer than a spike even when the totals are identical.

It has already taken the box down once. `series.py` accumulated every CTD cast in a
dict, reached 541 MB and climbing, and the machine went with journald thrashing on
memory flush. The rewrite streamed the casts correctly and *still* had to be killed
at 844 MB, because the output accumulator — a dict keyed over every
(variable, area, month) holding every value — was unbounded in exactly the same
way, one level down. Fixing the obvious accumulator is not the same as bounding the
script.

The raw data is far larger than the machine: `ctd.csv.gz` alone is 51.4 million
rows, the plankton grid ~7 GB, KD490 ~3 GB. So memory discipline is not an
optimisation here. It is the difference between a result and a reboot.

**Design for a stated peak, and state it.** Every script that touches a raw extract
declares its expected peak memory in its docstring. If you cannot say what the peak
is, the design is wrong.

**Stream; never accumulate over the dataset.**

- Iterate `for line in fh` over gzip directly. Never `fh.read()`, never
  `json.load()` on a raw extract, never `readlines()`.
- Group-by is a flush, not a dict. Rows for one group are usually contiguous —
  *check that they are*, then complete each group and discard it as the key
  changes, and count any key that reopens rather than assuming it cannot.
- An accumulator keyed over the whole dataset is the same mistake as reading the
  file, one level down. `{(var, area, month): [every value]}` is unbounded.
  Reduce as you go: running sum and count, or a fixed-size reservoir per cell.
- Output grids allocated once at a known size are fine — the coverage bitfield is
  123 × 564 × 6 bits and costs 52 KB. Fixed and small is not the problem;
  proportional to input is.

**Prefer in-place and fixed-width.**

- numpy: allocate once, operate in place (`out += x`, not `out = out + x`),
  `float32`/`int16` where the precision is not needed, and never hold two copies
  of a grid to compare them.
- Pack results as bytes rather than lists of Python floats. A Python float in a
  list costs about 60 bytes; the same number as `int16` costs 2.
- Open one netCDF year at a time and close it. Do not hold a decade.

**Guard the long ones.** Anything expected to run for minutes over a raw extract
runs in the background with an RSS check that kills it before the kernel does.
Kill by **PID**, never `pkill -f` on the script name — the pattern matches the
watching shell's own command line and kills the watcher instead, which has happened
repeatedly:

    until [ -f OUT ] || ! pgrep -f SCRIPT >/dev/null; do
      sleep 15
      pid=$(pgrep -f "bin/python SCRIPT" | head -1); [ -z "$pid" ] && break
      r=$(ps -o rss= -p "$pid" | awk '{printf "%.0f", $1/1024}')
      [ "$r" -gt 900 ] && kill "$pid" && echo "ABORT rss ${r}MB" && break
    done

**Scratch space is on disk now, not in RAM.** `TMPDIR` points at
`~/.cache/claude-tmp` on the 197 GB volume. `/tmp` is a 1 GB tmpfs, so anything
written there is held in memory and lost on reboot. Do not write large files to
`/tmp` explicitly.

## Data format is declared, not guessed

`scripts/formats.py` holds the format of every source and the traps found in each.
Two silent bugs cost a day between them: `float("8,47")` raising on the Danish
decimal comma so a bare `except` emptied a column, and a fast split leaving
`'"19890830"'` quoted so dates never parsed and a coverage cube reported zero
without erroring. Use `formats.num()`. If a source is new, add it to `FORMATS`
first and run `audit()` on a sample before trusting a parse.

## Claims

Absence is reported as a count over a named corpus, never as a share of the whole,
unless the category named is exactly as wide as the search performed. See the
correction block in `docs/AREAS.md`. A share of a documented positive set is fine;
a share of an absence is a residual.
