# Where a number comes from - the spec (draft for the owner to correct)

Status: approved by the owner on 2026-09-12 ("It looks good"), written from the
owner's own messages.

## Which numbers

Not every number earns a chain. Numbers that matter to what a page argues get the
full treatment. A family of numbers computed the same way - a table whose cells all
come from one computation - gets it once: one representative is traced end to end,
and the others note that they follow it. A number of no importance to the argument
is skipped. The point is to show how the numbers that carry weight were made, not
to certify every digit.

## What it replaces, and why

Each number's menu today shows the arithmetic done in the page generator, the line
of the page generator that prints it, and rows of the producer's output file. Every
view starts at the producer's output and looks forward to the page. None looks back
into the producer, where the data is selected, grouped, classified, thresholded,
corrected and aggregated - the steps where models enter and bias enters. The
string interpolation is the least interesting step of all.

## What every number must show

1. **The records it rests on, in their own words.** A terminal node is "file F, row
   N, published by P, says:" followed by the columns exactly as written
   (`ObservationsStedNr=…`, `Dato=…`, `Dybde (m)=…`, `Parameter="Oxygen indhold"`,
   `OriginalResultat=…`). No paraphrase into English nouns such as "sample",
   "station" or "water body": language does not separate a construction from a
   thing, so the bottom layer keeps the record's words. The terminal is "the record
   states", not "reality is".

2. **What was counted as one - the applefication - first.** For every step, what
   was treated as one thing, one kind, one member (statistical-methods, sections
   1-2). Identity is the most common model bias: a station number counted as one
   place across decades, a parameter name counted as one quantity across sensors
   and methods, a sonde label shared by unknown instruments.

3. **The computation - the code that computed it**, step by step from the records:
   the producer's actual source lines for each step, not the page's formatting. The
   page arithmetic, if any, is the last and smallest step.

4. **Why each step was done that way** - the model, the construction and its reason
   or author, attached to the step it justifies, not written as an essay beside it.

5. **Where the chain ends.** Every branch ends in either
   - a record (above), with the dataset's own constructions on it marked - a
     corrected value (`KorrigeretResultat` over `OriginalResultat`), a default
     clock, a category imposed at collection such as a water-body code; or
   - an irreducible construction, named as one: a polygon someone drew, a threshold
     someone set, a class rule someone chose; or
   - model output presented as data - a reanalysis, a modelled load, the city's
     flood model - named as a model, with what it was fitted to where that is known,
     and a mixed case showing its split (measured over this share, modelled over
     the rest).

## The kinds of modelling step - where bias enters

Each step in a chain is labelled with one of these, and arithmetic is shown as a
line, not a view of its own:

| kind | what it imposes |
|---|---|
| selection | which records count: filters, sample types, complete years |
| identity | what counts as the same thing |
| grouping | boundaries: water bodies, catchments, regions |
| classification | classes: seasons, summer-peaked, triage classes |
| convention | thresholds and definitions: bottom water, a limit, a boundary |
| correction | a model applied to the value itself |
| filling in | interpolation, model output where nothing was measured |
| functional form | the shape assumed: linear, a retention model, a fitted curve - which function, and why this one |
| attribution | assigning a remainder to one cause |

For every step: what it imposes, what else could reasonably have been chosen,
which way it could push the number, and whether anyone tested it.

## Aggregates

An aggregate is information nullification and model introduction (statistical-
methods section 4). It is allowed on four conditions and never shown alone:
- it states what it pooled as one kind;
- it reports what it dropped - the share of variation discarded (within the pooled
  members against between them) and the stability of the grouping;
- the distribution comes first, with its tails, and where the spread lives - split
  by place, time, depth and season;
- conclusions from it are checked against the distribution, within groups, and at
  the scale they are applied to.

The average is informative only where the members do not differ from it; every
distance from it is a distinction it deletes.

## Robustness

For each number, at least one rerun of the chain with an imposed choice changed or
removed - the boundary re-cut, the season class dropped, the sensor value used
instead of the corrected one. A finding that disappears when the boundary moves is
an artifact of the boundary, and saying so is the result.

## How it is recorded

Recording happens in the producer as it runs, not in the page: at every step the
producer records what went in (file, columns, row count), the step's source lines,
its kind from the table above with its reason, and what came out. The reader's menu
then shows, per number: Records, Counted as one, Computation, Why, Where it ends,
and the aggregate's spread where there is one.

## How the work proceeds

One number first, end to end, rendered, and shown to the owner before anything
scales. Then by computation chain, not by page, starting with stations ->
water bodies -> oxygen -> nitrogen -> the agricultural share. Each chain is built by
a worker agent and checked by a fresh mentor agent that reads this spec and the
worker's output - never the worker's summary - and asks, per number, whether its
end points are records in their own words, whether every category is marked as a
construction, and whether each modelling step's alternative was named and tried.
The parent checks samples; the owner checks the first chain.
