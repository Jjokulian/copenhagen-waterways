# Live numbers, references and species — how every entity on this site is checked

This is the working guide for converting a page of this site to the discipline it
now enforces. It is written for someone arriving fresh: read it end to end once,
then use sections 5–7 as the procedure. Nothing here is optional; the compiler
and the pre-commit hook refuse what this guide says to avoid.

## 1. The rule

**Every number, every reference to a hypothesis, and every chemical species on a
published page is a checked entity.** It reaches the page through a function that
knows where it came from, and the page compiler refuses anything typed by hand.

Why: typed values go stale silently. The flood area moved from one value to
another when a sheet was re-registered, and three scripts that printed it were
never rerun. A method-lab bound compared a simulation with an observation
measured a different way, and the check looked as if it passed. A clock column
turned out to hold filled-in defaults, not times, for most of the old record.
Every one of those was a typed or hand-copied value that nothing re-derived.

A published page is **generated**. Prose lives in a Python generator; the
markdown in `docs/` is output. Editing a generated page by hand is lost at the
next build (`scripts/check_generated.py` and `scripts/freshness.py` flag it).

## 2. The three checked entities

| entity | in a generator | in a claims register | rendered as | checked against |
|---|---|---|---|---|
| number from data | `d = live.live_json(path)` then `f"{d['field']:,}"` | `{fig:name}` | `[91,093](SOURCES.md#F-…)` | the field in `data/derived/*.json`, and its **construction** |
| number from arithmetic | arithmetic on live values: `a / b * 100` | `{calc:a / b * 100\|.1f}` | a link to the calculation | every operand |
| a calculation that is itself a model | `live.step("K-SUBSET-SHARE", a / b * 100)` | `{calc@K-SUBSET-SHARE:a / b * 100}` | the calculation, labelled with its construction | the step's declaration |
| number from an external document | — | `{read:SRC:shown\|phrase}`, `{count:SRC:term}` | a link to the pinned passage | the document's text, pinned by sha256 |
| what this site said before | `live.was(commit, file, "gave the lower figure as @@,")` | `{was:commit:file:gave the lower figure as @@,}` | the value, read out of git at build time, linked to the commit | the phrase must locate exactly one place in `git show commit:file`. **Licensed only inside a historical claim** - in practice, the archive (section 11). Never a justification for a fact |
| a value chosen, not measured | `live.stated(name, v, shown, reason)`; `live.stated_value(name, v, reason)` when it takes part in arithmetic | `{param:name}` | the value, with its reason | the params register |
| reference to a hypothesis, observable, route, outcome | `live.ref("K1")`, `live.ref("K1", title=True)` | `{ref:K1}`, `{ref:K1\|title}` | `[K1](hypodrafts/K1.md "current title")` | `data/derived/hypotheses.json` |
| chemical species | `live.chem("O2")` | `{chem:O2}` | `<span class="chem" data-chem="O2" title="…">O₂</span>` | `data/manual/species.json` |

Write the page with `common.write_doc(path, text)`. It expands the markers into
links and **refuses the page** if anything is left unchecked:

- a digit sequence that is not a live number and not exempt (section 3);
- a number whose field or step has no declared construction (section 4);
- a number built on simulation, on a page that is not a method page;
- a register ID (`K1`, `A7`, `O2`, `M1`…) typed bare;
- a chemical formula typed bare, whether in ASCII (`O2`, `CO2`) or with
  hand-typed subscripts (`O₂`).

**Labels that look like entities.** A statistical label such as `N1`/`N2`
(null hypotheses) or `H0` reads as a species or a register ID; write it as code.
So does a Danish bill number (`L 5`).

**`O2` versus O₂.** Plain `O2` means only the observable O2 in the hypothesis
register, as a checked reference (`live.ref("O2")`). The oxygen molecule is
always `live.chem("O2")`, rendered O₂. Inside a formula, use `$\mathrm{O_2}$`.

## 3. What the compiler does not count as a number

It lives in `live.EXEMPT_PATTERNS` and `live.bare_numbers()`. Exempt are:

- years, dates and clock times;
- legal citations (`§ 14`, `stk. 3`, `BEK 931/2024`);
- EPSG codes, and identifiers with the digits glued on (`UTM32`, `K1_si_din`);
- ordinals, hashes, `vol(issue)` citations, and ratios written "N to 1";
- anything inside `` `code` ``, URLs and link targets;
- inside `$math$`, only exponents and indices (`^{-1}`, `_{2}`, `^2`). **Any
  other number in math on a page is still a number** - print it live, or it is
  refused. (In construction declarations, math is exempt entirely: there it
  defines a model, and its constants are part of the definition.)

Everything else is a number and needs a chain.

**The blind spot is words.** "About half", "roughly a quarter", "a handful",
"twenty-fold" are unjustified quantities that the digit check cannot see. In a
construction declaration the checker refuses the approximate ones. On a page,
don't write them either: compute the value and print it live, or say what is
true without a quantity.

## 4. Constructions: what kind of number, and why believe it

Where a number came from is lineage; why it should be believed is its
**construction**. Every data field a page prints must be covered by a declaration
in `data/manual/number_constructions.json` or a fragment in
`data/manual/number_constructions.d/`. `scripts/constructions.py` is the checker.
The reader shows declarations in the "Construction and model" view of every
number.

A declaration, one per producing script (or per step):

```json
{
 "id": "K-EXAMPLE",
 "title": "short noun phrase",
 "covers": {"file": "data/derived/x.json", "fields": {
   "n_things": {"kind": "counted", "is": "what one thing is, what was counted as the same, what was excluded"},
   "runs.*.value": {"kind": "simulated", "is": "…"}}},
 "what": "what the script computes",
 "model": "how raw inputs become the number; formulas as $…$, with the code form beside them in backticks",
 "assumptions": ["…"],
 "justified": [{"text": "a reason to believe it", "ref": "scripts/x.py:120 or docs/X.md or a URL already cited in the repo"}],
 "gaps": ["what nothing justifies - be candid; an empty list is a claim too"],
 "void_if": ["when the number stops meaning what it says"],
 "licenses": "what it can support",
 "not_licensed": "what it cannot",
 "watches": ["scripts/x.py", "data/derived/y.json", "data/manual/claims.json#params"]
}
```

Here is what each part means.

- **Kinds:** measured, counted, estimated, computed, share, simulated,
  stipulated, bound, modelled (somebody's model of the world, such as the city's
  flood map), document, quoted. A calculation's kind comes from its operands.
  Anything built on a `synthetic` field is refused off the method pages
  (`method_pages` in the register).
- **Steps:** `covers: {"step": true}` plus `produces: <kind>`. The generator
  wraps the calculation in `live.step("K-ID", …)`.
- **Prose rules:**
  - No digits outside `` ` `` or `$`: name the field in backticks.
  - No approximate quantities in words.
  - Every "justified" entry cites a file and line you actually read. If the
    docstring and the code disagree, the code wins and you record the
    disagreement as a gap.
- **Watches:** a declaration goes STALE when any file it watches changes. Use
  `file.json#key` to watch one part of a JSON file. Watching a whole file that
  is edited all the time, like the claims register, makes it stale constantly.
- **Confirmation:** after writing or re-reading a declaration against the
  current code, run
  `python3 scripts/constructions.py --reassess K-ID --by "<who> (<what you did>, <date>; not yet read by the project owner)"`.
  A confirmation is somebody's; say honestly who did the reading.

The commands:

```
python3 scripts/constructions.py --check        staleness, confirmations, prose rules
python3 scripts/constructions.py --uncovered    fields in use with no declaration
```

## 5. Converting a page — the procedure

1. **Find out whether the page is generated.** Look at `data/manual/build.json`
   and `data/manual/build.d/*.json`, then run `grep -l "PAGE.md" scripts/*.py`.
   If a script writes it, you edit that script, never the markdown.
2. **If the page is hand-written,** create a generator,
   `scripts/pages/<slug>.py`. Put `sys.path.insert(0, <scripts dir>)` in it so it
   can import `common`, `live` and friends. First move the prose in **verbatim**,
   as `w("…")` lines or one triple-quoted block per section, and make it write
   the page through `write_doc`. Run it. It will refuse, and the refusal lists
   every unchecked entity. That list is your work queue.
3. **Work through the queue, one entity at a time,** using the decision tree in
   section 6.
4. **When a value you need isn't stored anywhere,** find the script that computes
   it:
   - Make it store the value in its derived JSON. This is an *additive* edit: a
     new field, never a changed one.
   - Rerun it. Anything that reads `data/raw/` or the sibling project's data goes
     through `scripts/heavy`, which serialises memory-heavy jobs.
   - Declare the new field's construction.
   - Never copy a value from one file into another by hand. A number typed into
     a script is the same failure as one typed into prose (the observed-spread
     incident).
5. **Register the generator** in your build fragment, `data/manual/build.d/<slug>.json`:
   `{"steps": [{"script": "scripts/pages/<slug>.py", "inputs": […], "outputs": ["docs/PAGE.md"]}]}` (add `"args": ["report"]` if the script needs a subcommand to write the page).
   Inputs are every derived file the generator reads. Add
   `data/derived/hypotheses.json` if it renders references,
   `data/manual/species.json` if it renders species, and the claims or
   construction files it depends on.
6. **Check:**

   ```
   python3 scripts/pages/<slug>.py                      # must write the page, no refusal
   python3 -c "import sys; sys.path.insert(0,'scripts'); import figures; print(figures.check('docs/PAGE.md'))"
   python3 scripts/constructions.py --check
   python3 scripts/constructions.py --uncovered
   python3 scripts/claims.py --check                    # only if you touched a claims fragment
   ```

   `figures.check` must return `([], [])`. That means nothing broken, and no
   unchecked number, reference or species.
7. **Confirm your declarations** (section 4) and any claims you added
   (`python3 scripts/claims.py --reassess C-ID --by "…"`), each after reading
   what it now says.

## 6. Decision tree for one unchecked entity

- **It's an identifier, not a quantity** (a station number, a layer name, a file
  name): write it as `` `code` ``.
- **It's a register ID** (`K1`, `A7`, `O2`…): `live.ref("K1")`. Use
  `live.ref("K1", title=True)` where the sentence names the hypothesis.
- **It's a chemical formula:** `live.chem("NO3-")`. If the species isn't in
  `data/manual/species.json`, add it to your fragment
  `data/manual/species.d/<slug>.json` as
  `{"species": {"key": {"unicode": "…", "name": "…"}}}`.
- **A script in this repo computes it:** read it through `live_json` from the
  derived file the script writes, and declare the field's construction. If the
  script doesn't store it yet, see step 5.4.
- **It's arithmetic on such values:** do the arithmetic in the generator on the
  live values. If the arithmetic is itself a modelling choice (a share, a
  read-off, an interpolation), wrap it in `live.step` and declare the step.
- **It comes from an external document** (a law, a report, a paper): add the
  source to your claims fragment, pin it, then use
  `{read:SRC:shown|exact phrase}` or `{count:SRC:term}` through
  `claims.resolve`.
  - The fragment is `data/manual/claims.d/<slug>.json`, with `sources`,
    `figures`, `params`, `nodes` and `claims`, merged with `claims.json`.
  - Pin with `python3 scripts/claims.py --repin SRC`. It needs the network.
  - Never cite a document you haven't read. Never invent a source.
- **It's what this site said at a past commit:** a quotation is a *reference*, not a
  copy. Write `live.was(commit, file, "a phrase from that text with @@ where the
  value stands")` - the value is read out of `git show commit:file` when the page is
  built, so the generator never types it. The phrase must find exactly one place.
  `python3 scripts/quote_locate.py COMMIT FILE "value" hint words` suggests the
  shortest such phrase, preferring one without other digits. A typed quotation
  (`live.quote(commit, file, "80%")`) is refused once every quotation is located.
- **It's a value chosen rather than measured** (a threshold): a `param` in your
  claims fragment, with its reason, printed via `{param:name}` or `live.stated(…)`. If it takes part in arithmetic, use `live.stated_value(name, value, reason)`: it returns a live number, so `n_pairs * n_windows` shows as a calculation on stated values rather than a typed product.
- **None of these apply:** the number has no chain. Delete it, or rewrite the
  sentence so it says what is true without it. Don't keep it with an allowance;
  there is none.

**When a live value differs from the typed one,** the sentence must follow the
live value. If that changes a conclusion, rewrite it honestly and list the change
in your report under "conclusions that changed". That is a finding, not a
failure.

## 7. Traps already hit in this repo

- **Apples and oranges.**
  - A share's part and whole must be counted by the same rule. The earlier
    manure share's denominator was not what its sentence said.
  - Two counts presented side by side must use the same filters. The clock
    source counts were taken before and after the quality filters.
  - A simulation must be measured exactly as the observation it is compared
    with: same code, bins, window and clock. Say which counting rule a number
    uses in its construction's `is`.
- **Time.** Never read `Startklok` or any other clock directly: go through
  `clock.instant(supplier, date, klok)`, which returns one UTC instant or says
  why there is none. The archive's clock is a filled-in default for much of the
  pre-1999 record and a wall clock afterwards (`scripts/clockzone.py`).
- **`float * LiveInt` loses the chain.** Python lets `float` handle a plain
  `int` subclass itself, so `0.5 * n` with a live integer `n` is a bare float
  (the compiler then refuses it). Put the live operand first (`n * 0.5`) or make
  the constant a stated value.
- **Single draws.** A simulated number from one noise draw carries an error of
  unknown size. Report medians and spreads over draws.
- **Quantities in words** hide unjustified numbers (section 3).
- **`docs/HYPOTHESES.md` and `scripts/hypotheses.py` are the owner's.** Never edit
  them without explicit approval, even to fix a verified error. Report it instead.
- **Look before you write to a path.** A register was once written over an
  unrelated hand-curated file with the same name
  (`data/manual/constructions.json`, the sewer structures). Read an existing
  file before replacing it.
- **Memory.** The machine has 4–5 GB and is shared by parallel workers.
  - Run data-heavy scripts through `scripts/heavy`, which runs one at a time
    under a cap.
  - Never use `pkill -f` on a pattern that appears in your own command line.
    It kills your own shell.
  - See the "Memory" section of `CLAUDE.md`.
- **Absence.** A claim of absence is a count over a named corpus, never a share
  of everything (`CLAUDE.md`, "Claims").
- **Don't commit.** Commits are the owner's call.

- **Self-quotation is not a justification.** In the first conversion wave,
  converters carried 1,937 numbers on 55 pages as quotations of the page's own
  earlier version: a typed number with a date attached. A quotation licenses
  "the site once said this" and nothing more, and the compiler now refuses a
  quoted number outside a historical claim. Derive the number, cite a pinned
  document, or retire the sentence (section 11).

## 8. Working in parallel with others

Several workers may convert pages at the same time, so:

- **Your slug** names everything you create: `scripts/pages/<slug>.py`, and a
  fragment of your own in each register:
  - `data/manual/number_constructions.d/<slug>.json` for construction declarations
  - `data/manual/claims.d/<slug>.json` for sources, figures, params, nodes and claims
  - `data/manual/build.d/<slug>.json` for build steps
  - `data/manual/species.d/<slug>.json` for chemical species

  Loaders merge fragments with the main file, and saving writes each item back
  to the file it came from.
- **IDs:**
  - Prefix new construction IDs `K-<SLUG>-…` and new claim or node IDs
    `C-<SLUG>-…` / `N-<SLUG>-…`.
  - A duplicate ID across fragments is refused, and so is a duplicate name for a
    source, figure or param.
- **Don't edit the shared engine:** `live.py`, `claims.py`, `constructions.py`,
  `refs.py`, `chem.py`, `figures.py`, `freshness.py`, `common.py`, `clock.py`,
  `index.html`, or the main register files. If you need an engine change,
  describe it in your report.
- **Producer scripts** (`scripts/*.py` that write `data/derived/`) may be shared
  between pages. Edit them additively only, using the Edit tool, which fails if
  somebody changed the file after you read it; then re-read and retry. Rerun
  them through `scripts/heavy`.
- **Generated shared outputs**
  (`docs/SOURCES.md`, `docs/data/sources_index.json`, `docs/CLAIMS.md`) are
  written under a lock by every build. Never edit them. They are regenerated at
  the end.
- **Touch only your own pages.**

## 9. Done, for one page

- Its generator writes it with no refusal, and
  `figures.check("docs/PAGE.md") == ([], [])`.
- `constructions.py --check` reports nothing about your K-IDs;
  `constructions.py --uncovered` lists nothing of yours.
- The generator is registered in your build fragment, with honest inputs.
- Every declaration and claim you wrote or changed is confirmed, by name.
- Your report lists:
  - the pages done and not done, with the reason for each one not done;
  - conclusions that changed;
  - defects found in producer scripts;
  - engine changes you needed.

## 10. Not yet in scope

- **`docs/HYPOTHESES.md`**: its wording belongs to the owner. Converting it is
  allowed; retiring or rewording a hypothesis is not, without asking.

## 11. Claims — every assertion is checked too

**The rule, as the owner put it: go through everything, and if we cannot make a
good justification for a claim, we do not claim it any more.** We replace it with
what we can still justify, and the new claim's justification says that it
replaced an earlier claim, now retired to the archive. A number is one kind of
claim; so is "the working day costs most of the signal", "the sheets are a model
output", "DCE accept a model at this $R^2$" and "an earlier version said X".

**What counts as a claim.** Any statement a reader could doubt: about the world,
the data, the code, other people's documents, or this project's own history.
Not claims: headings, navigation ("see X"), the definition of a term the page
itself sets, instructions to the reader. When in doubt it is a claim. One claim
per thing a reader could doubt separately; a paragraph that is one argument can
be one argued claim resting on its premises.

**Marking it on the page.** In the generator, `live.claim("C-ID", text)`, or
`live.claim_begin("C-ID")` … `live.CLAIM_END` across several written lines. A
claim is one span inside one paragraph. `write_doc()` refuses the page unless
the claims register holds the claim for this page, confirmed against this very
wording and current, with everything under it current too. It renders as
`<span class="claim" data-claim="C-ID">…</span>` plus a `†` link to the claim's
entry; in the reader the sentence itself opens what it rests on, and numbers
inside it still open their own chains. The wording is recorded in
`data/derived/claim_spans.json`, so rewording a sentence, or a number in it
changing, makes the claim stale until someone reads it again.

**The register entry** (`data/manual/claims.json` or a fragment in
`claims.d/`):

```json
{"id": "C-ML-...", "page": "METHOD_LAB.md",
 "kind": "measured | bounded | simulated | modelled | provisional | gap | argued | attributed | historical | stipulated | code",
 "stance": "ours | theirs",
 "holder": "whose claim it is - theirs only",
 "claim": "the statement; placeholders, no typed numbers",
 "because": "ours: why it follows from what it rests on. theirs: the reasons THEY give, as far as found",
 "rests_on": ["nodes and other claims"],
 "replaces": ["the retired claim it replaces, if any"]}
```

**Where a chain may end.** Every path down from a claim ends in one of these, and
the build refuses one that does not:

| kind | what it is | checked |
|---|---|---|
| `held` | data on disk | its numbers' constructions |
| `external` | a published document; give `source` (a pinned source) and `said` (a phrase in it) for somebody else's claim | the phrase must be in the pinned text |
| `assumption` | stipulated; the claim is void if it is wrong | - |
| `gap` | data that exists and cannot be reached, or was never measured | - |
| `synthetic` | generated to test a method | method pages only |
| `script` | the code that does the work | - |
| `history` | what this project did or said at a commit: `commit`, `file`, `said` | the phrase must be in `git show commit:file` |
| `untraced` | **the trail ends here**: what was searched, where and when, and that nothing further was found | a `detail` is required |

A `said` phrase locates a passage and is shown verbatim, so it holds no digits; a
number quoted from a document goes through `{read:}`. An `argued` claim, or a `stipulated`
rule, may rest on nothing only if its `because` is the whole argument or reason.

**Ours and theirs.** Our own claim says why it follows. Somebody else's claim -
kept because the site steelmans rather than strawmans - is credited to its
`holder` and rests on their document (pinned, with the phrase they said) or on an
`untraced` node saying where the trail ran out. **Never fabricate a
justification.** Record what could be found and nothing more.

**Hypotheses are not claims.** A hypothesis in `docs/HYPOTHESES.md` says that a
mechanism is possible or plausible; its justification is the mechanism and the
reasoning behind it, not a measurement. The owner: "It is hypo-thesis, it is
some notion of how things may work together, some foundational justification for
why we may believe this a possible or perhaps plausible explanatory dynamic." So:

- No hypothesis is retired, and none is marked as a claim.
- A hypothesis carries no measurement. What the data holds for it is a claim
  like any other and lives on an evidence page, linked from the hypothesis.
- A constant of the mechanism - a stoichiometry, a seawater concentration, the
  threshold that defines an outcome - is part of the plausibility argument and
  stays, as a stated or derived value with its source.
- References to hypotheses are live (`live.ref`, `{ref:}`): the title shown is
  the current one, and a page citing an ID that no longer exists is refused. A
  claim that names a hypothesis, observable or outcome records that entry, and
  goes stale when its content - anything but its data needs - changes.

**Retire and replace.** When a published claim cannot be justified:

1. Add it to the register as a retired claim: kind `historical`, page
   `ARCHIVE.md`, and `"retired": {"on", "from", "commit", "file", "begin", "end",
   "why"}`. The commit is the last *committed* version that published the
   wording; `begin` and `end` are phrases that locate the passage (they may hold a number, since
   they are never shown)
   there (`live.excerpt()` reads it out of git, every quantity in it a
   quotation). They locate only - the passage shown is read out of git - so
   they may hold a number where the passage starts or ends on one. `why` is the reason, plainly - most often "its justification was
   not recorded properly".
2. Write the replacement: only what can be justified, as a normal claim with
   `"replaces": [...]`, and `"replaced_by"` on the retired one. If nothing can be
   justified in its place, `"replaced_by": []` and the page drops it.
3. The page says only the replacement. It does not narrate its own history
   ("an earlier version said…"); that lives in the archive and in the
   replacement's entry in CLAIMS.md.

Wording that was never committed was never published: change it, no archive
entry. A published claim reworded but still justified - it says the same
thing, better - is not retired either: it is still claimed. `scripts/claims.py` writes both `docs/CLAIMS.md` and `docs/ARCHIVE.md`.

Found in the METHOD_LAB pilot:

- A claim's `note` is part of the claim. "An earlier version of this note
  said…" inside it is history too: retire the old wording, drop the sentence,
  and add `replaces`.
- The archive links a replacement by its ID and never restates it: a
  replacement may carry simulated numbers, which stand only on method pages.
- An archive passage is shown without bold markers. A passage cut from inside
  bold text would otherwise leave a stray marker at its edge.
- A span cannot run across list items or table cells: the markup would open
  in one item and close in another. Give each item its own claim, or make the
  list a paragraph. A span may begin with an item's marker (`1.`, `-`): the
  compiler keeps the marker outside the span, so the line stays a list item.
- Duplicate ids are refused within one register fragment as well as across
  fragments.
- A claim already in the main register is marked on a page only if it is
  registered for that page. Otherwise the page's own claim rests on it, and the
  register change goes to the parent.
- A retired claim's `from` is the page path under `docs/` (`hypodrafts/K1.md`),
  and its `file` the repository path (`docs/hypodrafts/K1.md`).
- Texts that are rendered - a claim, its `because`, `note`, `holder`, a node's
  `label` and `detail`, a retired claim's `why` - are checked like a page: a
  number in them needs a placeholder, or is an identifier set as code. A
  confirmation's by-line is shown verbatim as code, so it may hold anything.
- A `said` phrase is matched against the pinned text as extracted: tags are set
  aside and entities read as characters, but in a JSON or API pin the markup and
  escapes are part of the text. A response that changes on every request cannot
  be pinned; cite the register entry that records it, and say so.
- One claim, one span per page. A second span with the same ID is refused,
  since only one wording can be confirmed; merge them or make two claims.
- A published table that cannot be justified is retired like a sentence: one
  retired claim whose passage runs from a phrase in its header row to one in
  its last row, replaced by what can be justified. A dropped vague word ("much
  of") that changes what is asserted is a retirement; one that changes nothing
  is an edit.
- Retired claims are confirmed twice, and the second time only after
  `claims.py` has written ARCHIVE.md - the parent does that round. An agent
  confirms each retired claim once, by id. Never `--reassess all`: it would
  sign every other agent's claims.
- Two numbers read from the same quoted phrase share an identity. Read each
  from its own phrase (`{read:SRC:119|119 medlemmer ...}`, `{read:SRC:34|mens
  34 stemte imod}`).
- Node ids carry their kind in the prefix only by convention (`D-` held data,
  `H-` history, `E-` external, `U-` untraced, `A-` assumption, `X-` script,
  `G-` gap); the checker reads `kind`. A page generator writing its own
  `data/derived` file is part of the page, not a producer.
- An agent working a page runs its builds and confirmations in the foreground,
  with a long timeout, and finishes: ending a turn to wait on a background loop
  leaves the page half-confirmed and nobody to finish it.
- Confirming takes two rounds for anything newly marked. The first build
  records the wording and refuses; confirm against it; build again.

**Procedure for a page.**

1. List every assertion on it.
2. For each, dig: follow each support down until it ends in one of the kinds
   above. Read the code, the data, the pinned documents and the history - do not
   infer.
3. Where the chain holds, register the claim and mark its span.
4. Where it does not, retire the published wording and write the replacement,
   or drop it.
5. Build the page. It refuses until each claim is confirmed against its wording:
   read it, then `python3 scripts/claims.py --reassess C-ID --by "<who, what was read>"`.
6. Report what was retired and why, and every page sentence that changed.

## Where things are

## Where things are

| file | what |
|---|---|
| `scripts/live.py` | live values, markers, `write_doc` compiler, `step`, `quote`, `stated`, `ref`, `chem`, the number index and SOURCES.md |
| `scripts/claims.py` | claims register, placeholders, pinned sources, staleness, structure checks, CLAIMS.md and ARCHIVE.md |
| `scripts/constructions.py` | construction declarations, kinds, the simulation rule, staleness |
| `scripts/refs.py`, `scripts/chem.py` | references and species |
| `scripts/clock.py`, `scripts/clockzone.py` | the one way to read a sampling time, and the evidence behind it |
| `scripts/figures.py` | the pre-commit check of committed pages |
| `scripts/freshness.py` | the build graph: STALE, REBUILT, HAND-EDITED |
| `scripts/heavy` | run a memory-heavy job, one at a time |
| `scripts/methodlab.py` | a fully converted generator to copy from |
| `index.html` | the reader, including the per-number views (construction, source, graph, derivation, calculation, code, data) |
