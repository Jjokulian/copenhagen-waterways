# copenhagen-waterways

## Memory: use it, but do not churn it

**The budget is 4–5 GB.** That is the working figure, not a ceiling to creep up on.
RAM is balloon-managed and grows toward it, so a slow steady climb is granted where
a sudden spike may not be — but within that budget, memory is not a scarce resource
and should not be treated as one.

**Never degrade a method to save memory.** This has already gone wrong once in the
other direction: a run was killed at 844 MB, and the reflex was to replace an exact
median with a running mean. That was the wrong trade twice over — the machine had
gigabytes free, and the actual defect was the *container* rather than the statistic.
A Python float in a list costs about 60 bytes; the same value in `array("f")` costs
4. Changing the container kept the median and cut the footprint fifteenfold. If a
statistic looks unaffordable, the container is usually the reason.

So: pick the right statistic first, then make it cheap.

**Prefer in place over reallocating.** This is about allocation churn, not headroom.

- numpy: `out += x`, not `out = out + x`. Reuse buffers across a loop rather than
  allocating per iteration. Choose the narrowest dtype the precision allows.
- Typed containers over Python object graphs — `array`, `bytes`, numpy — wherever
  the data is homogeneous numbers. The saving is large and costs nothing.
- Stream the raw extracts: `for line in fh` over gzip, never `read()` or
  `readlines()`, and never `json.load()` on a raw file. Not for the ceiling; because
  building a 51-million-element object graph is slow as well as large.
- Group-by is a flush, not a dict, where the groups are contiguous — *check that
  they are* and count any key that reopens rather than assuming.
- Open one netCDF year at a time and close it.

**What genuinely must not happen** is an allocation that grows without bound in the
input and has no idea where it stops. Say what a script's peak depends on: "the
number of retained CTD measurements times four bytes" is a bound. "Every cast, in a
dict" is not.

**Guard long runs at 4.5 GB**, and kill **by PID** — `pkill -f <script>` matches the
watching shell's own command line and kills the watcher, which has happened four
times:

    until [ -f OUT ]; do
      sleep 20
      pid=$(pgrep -f "bin/python SCRIPT" | head -1); [ -z "$pid" ] && break
      r=$(ps -o rss= -p "$pid" | awk '{printf "%.0f", $1/1024}')
      [ "$r" -gt 4500 ] && kill "$pid" && echo "ABORT rss ${r}MB" && break
    done

**Scratch space is on disk.** `TMPDIR` points at `~/.cache/claude-tmp` on the 197 GB
volume; `/tmp` is a 1 GB tmpfs, so anything written there is held in RAM and lost on
reboot.

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
