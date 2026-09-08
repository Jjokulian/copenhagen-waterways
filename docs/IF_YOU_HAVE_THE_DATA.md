# If you have data access we don't

This project is run from open data by someone with no institutional credentials. A
large part of what it cannot answer is not hard — it is **gated**, and if you hold a
login, a field sheet or an internal series, you can unblock in an afternoon what we
cannot unblock at all.

This page is the handover: what is blocked, on exactly what, and how to run the thing
yourself so your answer lands in the same shape as everything else here.

---

## 1. What is blocked, and on what

Ordered by how much is unlocked per unit of effort.

| # | Blocked | What unblocks it | Who plausibly has it |
|---|---|---|---|
| 1 | **The whole nutrient half of the hypothesis field** | ODA `vandkemi`, plus `ODA-STOFTRANSPORT` and `ODA-TILFOERSEL` | anyone with an ODA login |
| 2 | **Overflow as anything but a model** | PULS measured overflow volumes, not modelled ones | utilities, Miljøstyrelsen |
| 3 | **Marine toxicants — currently unscoreable** | the parameter lists of the credential-gated ODA MFS topics | DCE, Miljøstyrelsen |
| 4 | **Instrument bias (I2)** | `SondeNr` is `999` on 83.5% of rows | DCE, or whoever holds the originals |
| 5 | **The diel confound (I3)** | **time of day.** No column exists in 53.7M rows | whoever holds the field sheets |
| 6 | **Eelgrass, macroalgae, benthic fauna (F3)** | ODA topics `Emne_3_182`, `Emne_3_181`, `Emne_3_180` | open, just unfetched — see §3 |
| 7 | **Trawling (D1)** | ICES/HELCOM swept-area ratio, figshare 20310255 | open, 23 MB, CC BY 4.0 |
| 8 | **The residual growth test on the 69.6%** | the published DCE vintages of the same year | open, `dce2.au.dk/pub/SR<n>.pdf` |

**Items 6, 7 and 8 need no credentials at all.** They are simply not done. If you have
an hour and no special access, start there.

### The two that would change the most

**`vandkemi` is not reachable by the fetch script as written.** `scripts/fetch_oda.py`
has five topics in `TOPICS`, and `argparse` rejects anything else, so the docstring
advertises a topic the dict never implements. Worse, `run()` hardcodes
`topic.aspx?id=h&t=h` (Hav) — so the two land-load topics need a **code change**, not a
config entry. Whoever fixes that unblocks item 1 for everyone.

**Time of day may not be lost after all — and finding out is one fetch.** Oxygen swings
diurnally; daylight at 55°N runs 7 to 17 hours across the year; so if sampling happens
in working hours the diel phase sampled shifts systematically with season. There is no
clock-time column in the **CTD extract**, verified across all four fetched exports.
**But our own topic enumeration records ODA marine water chemistry (`Emne_10_11`) as
carrying `Startdato + Startklok` — a clock time per sample — in two independent passes,
and we have never fetched it.** If that holds, and if chemistry samples share cruises
with CTD casts, it bounds the CTD sampling hour and the diel confound stops being
uncountable. A NOVANA technical instruction would do the same. **Neither has been
checked. One is a fetch; the other is one document.**

---

## 2. Run it

```bash
git clone https://github.com/Jjokulian/copenhagen-waterways
cd copenhagen-waterways
python3 -m venv .venv && . .venv/bin/activate
pip install requests xarray netCDF4 numpy         # that is the whole dependency list
```

Nothing needs a GPU, a cluster, or more than a few GB of RAM. The heaviest step
streams a 20.5 GB CSV and peaks under 300 MB.

**Memory discipline matters here** — this was developed on a VM that could be killed by
a careless allocation. Long jobs go through a cgroup cap:

```bash
scripts/runbig -m 3G -- python scripts/series.py     # SIGKILL at the cap, no thrash
```

Exit code 137 means you hit it. Prefer typed containers (`array`, numpy) over Python
object graphs, and stream raw extracts rather than reading them whole. **Never trade a
statistic for memory** — fix the container, not the method.

---

## 3. Add a data source

Fetches live in `scripts/fetch_*.py`. For a new ODA topic, one line:

```python
TOPICS = {
    ...
    "aalegraes": {"emne": "Emne_3_182", "what": "Ålegræs plante, transect surveys"},
}
```

```bash
python scripts/fetch_oda.py aalegraes --from 1980-01-01 --to 2026-12-31
```

**Pass the period explicitly.** With no `--from/--to`, ODA silently returns only the
*currently active* network — for one topic that was 345 stations instead of 1,990, and
the truncation is invisible in the output. The script now refuses to run without a
period for exactly this reason.

Then register what you added in **`docs/data/atlas.json`**, which is the machine-readable
index of every source: its provenance, its error classes, and — the field that matters
most — **whether it is a separate production path**. Nine of the archive's variables
are three sensors, because salinity is computed from conductivity and temperature and
oxygen saturation from oxygen, temperature and salinity. Independence is the scarce
thing, not volume.

---

## 4. The rules that make a result usable here

These are not style preferences; a result that skips them cannot be read.

1. **Compute your null, never quote it.** Five times in this project a statistic's
   quoted null was not its null under the constraint actually imposed — a mean-square
   ratio whose null is 0.5 not 0; an ARI whose maximum was 0.132 not 1.0; contiguity-
   constrained partitions agreeing at 0.337 not 0; derived partitions floored at 0.12
   not 0.337. **One of those ran against the finding**, so the direction is not
   guessable in advance.
2. **Water bodies are a model assumption, not a unit.** Do not aggregate into them.
   Feature-subspace stability found they add nothing beyond being connected regions of
   their size distribution. "Denmark" is not a closed system either.
3. **Flag, never delete.** `docs/data/areas/flags.json` records judgements and their
   evidence and removes nothing. The visible outliers are the only observable sample
   from the error process; trimming them destroys the sole estimator of the archive's
   own error rate while making it look cleaner.
4. **An absent dimension makes a hypothesis unscoreable, not refuted.** Do not let
   "no data" become "no effect".
5. **State what your number is a distribution of.** A single figure asserts that
   everything it summarises was one kind of thing.
6. **Report the five qualifiers**, none droppable: a coefficient, at a stated level of
   organisation, against a stated null, for a named functional, at a stated point in
   the accumulation of measure-spaces. Drop any and you have made a verdict, which is a
   different kind of object than this can produce.

Full method, and an audit of which parts survive their own rules:
[statistical-methods](https://github.com/Jjokulian/statistical-methods).

---

## 5. Send it back

A pull request, an issue, or a link to a dataset — all three are useful. What is most
useful is the thing nobody here can produce:

- **a series with an instrument identity attached**, so I2 becomes testable
- **a sampling time**, so I3's diel half stops being unscoreable
- **a measured overflow volume**, so B1 stops being a model correlated with a model
- **any marine toxicant analyte at all**, so group E stops being unscoreable at eleven
  stations against 76,926 station-months of oxygen

And if you find that something here is wrong, that is the most useful contribution of
all. Several of the errors this project has caught were its own — a marine coverage
claim built from freshwater monitoring points, an oxygen series labelled mg/l that was
ml/l, four nulls quoted instead of computed. They are left visible in the pages and in
the git history rather than edited out, and yours would be too.
