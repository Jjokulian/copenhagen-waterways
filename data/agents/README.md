# Agent findings, parked

Three agents ran in parallel while the main thread worked on the observing system.
Their outputs are here so the work survives the session, and so it can be picked up
deliberately rather than absorbed in passing.

**Nothing in this directory has been verified against primary sources by the main
thread.** Treat every claim in it as a lead, not a finding. That is the whole reason
it is parked: an earlier version of this project rewrote a live page on the strength
of a subagent's report, which is the same error as trusting a press release.

| agent | session id | wrote | status |
|---|---|---|---|
| Residual estimator explainer | `a3d74de0ffc483c26` | `docs/RESIDUAL.md` | published, reviewed |
| Politicians' verbatim claims | `ad74adbf09970f702` | `data/manual/politics.json` | committed, unreviewed |
| Science chain, data and model level | `a07c69a10b5af910f` | `data/manual/science_chain.json`, `docs/GRUNDLAGET.md` | committed, **unlinked and unreviewed** |

The `*.transcript.txt` files are each agent's full working transcript, including the
searches, the documents fetched and the reasoning. They are large; read them with a
specific question rather than end to end.

## Reactivating one

The agents are resumable within the session that spawned them, by session id:

    SendMessage(to: "a07c69a10b5af910f", message: "...")

Across sessions they are not resumable, and the transcripts here are what remains.
If a thread needs continuing later, spawn a fresh agent and give it the relevant
transcript as its starting context.

## What is owed on each

**science_chain** — reports that the DHI mechanistic layer (Erichsen & Kaas 2015,
Del 2) contains 3D stratification, full seasonality, sediment pools and oxygen at all
depths validated at R² = 0.83, and that only summer chlorophyll and summer Kd are
extracted from it because those are the EU-intercalibrated elements. If that holds it
is a significant correction to several pages, and a sharper argument than the one it
replaces. **It has not been checked against Del 2 in the original.** `OBSERVING.md`
carries an explicit scope note saying so. `docs/GRUNDLAGET.md` is committed but
deliberately absent from the site navigation until someone reads the source.

Also reports a number worth chasing first: DHI's Del 2 Tabel 3 putting Danish
land-based nitrogen at 2.8% of the chlorophyll indicator in Køge Bugt, and Del 1
Tabel 6 assigning København Havn 18% by the rule *"Øresund anvendt til at bestemme
indsats til KBH"* — the fallback for water bodies with neither data nor a model.

**politics** — 92 verbatim statements with speaker, date, source and claim class,
plus 17 party positions. Flags that no Folketinget floor transcript could be
retrieved (JavaScript rendering; the open referat XML dump would fix it), so chamber
quotations are quotations of press renderings and the file says so in `_caveats`.

**residual** — the only one already reviewed and published. Its two corrections
against the repo were applied at the time.
