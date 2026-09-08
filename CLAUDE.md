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

**The machine now defends itself, so a runaway is a hint rather than a crash.**
This was set up after a runaway script took the VM down and cost a session restore.

`earlyoom` is installed and enabled, and kills on **swap exhaustion**: SIGTERM once
the 10 GiB swapfile is half consumed, SIGKILL at three quarters. It prefers
`python3` and avoids the session, the shell and `claude`, and it writes a dated line
to `/var/log/earlyoom/kills.log` (root-readable only) so a killed job is
diagnosable instead of vanishing. The non-obvious mechanism: earlyoom acts only when
memory **and** swap are both under threshold, so making swap the gate means making
the memory condition permissive (`-m 95,90`), not removing it.

    sudo oom-policy show      # thresholds in force
    sudo oom-policy swap      # default: let the buffer be used, kill when it goes
    sudo oom-policy memory    # fallback: kill under ~700 MB available, before paging

Switch to `memory` if the VM ever becomes unresponsive again despite the buffer —
that would mean the spiral starts before free swap reaches 50%. It is deliberately
over-protective and will kill jobs that would have finished.

Swap is 10 GiB on root with `vm.swappiness=10`, so it is an emergency buffer rather
than a working store. It was grown from 1 GiB partly for headroom and partly as a
diagnostic: with only 1 GiB it was never possible to tell whether swapping worked or
merely thrashed.

**For a job you already know is large, cap it rather than relying on the net.**
`scripts/runbig` puts the job in its own cgroup, so the kernel SIGKILLs exactly that
job at the limit — no heuristic about who the runaway is:

    scripts/runbig -m 4G -- ~/.venvs/marine/bin/python scripts/series.py

Exit 137 means the cap was hit. `MemorySwapMax=0` inside it is not optional: with
`MemoryMax` alone the cgroup reclaims into swap instead of dying. Measured — the
same allocation reached 400 MB under a 200 MB cap with swap allowed, and was killed
at the cap without it.

Do **not** guard long runs with an RSS-polling loop. `pkill -f <script>` matches the
watching shell's own command line and kills the watcher; that happened four times
before this was replaced.

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
