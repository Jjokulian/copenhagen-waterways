# Copenhagen 2012 cloudburst flood model, georeferenced

<span class="claim" data-claim="C-DQ-F-WHAT">Modelled inundation depth at a [100](../../SOURCES.md#F-89b4887632)-year event in 2010, as the Amager sheet's title names it, from the flood scenarios of Københavns Kommune's cloudburst plans.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-WHAT "What this claim rests on")</sup> <span class="claim" data-claim="C-DQ-F-RECOVERED">Recovered from the [7](../../SOURCES.md#F-13d1b87901) published PDF sheets and placed back on the map.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-RECOVERED "What this claim rests on")</sup>

## How to load it

Open any `<sheet>.png` in QGIS. <span class="claim" data-claim="C-DQ-F-FILES">Beside it the export writes a `.pgw` world file, holding the pixel size and the centre of the top-left pixel, and a `.prj` naming `WGS 84`, `EPSG:4326`.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-FILES "What this claim rests on")</sup>

<span class="claim" data-claim="C-DQ-F-COLOURS">Each pixel is a depth band's legend colour, fully opaque where a band was read and fully transparent where none was. The colours stand for these bands:</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-COLOURS "What this claim rests on")</sup>

| colour | depth |
|---|---|
| `#f7fbff` | [0.05](../../SOURCES.md#F-b72f677f80)–[0.1](../../SOURCES.md#F-554faf5a00) m |
| `#d1e2f2` | [0.1](../../SOURCES.md#F-c7dc27d5c0)–[0.2](../../SOURCES.md#F-6d94ba76df) m |
| `#9ac7e0` | [0.2](../../SOURCES.md#F-77002080ac)–[0.5](../../SOURCES.md#F-5187388230) m |
| `#519ccc` | [0.5](../../SOURCES.md#F-28360d417a)–[1](../../SOURCES.md#F-6012071389) m |
| `#1c6bb0` | [1](../../SOURCES.md#F-a309b93986)–[2](../../SOURCES.md#F-d6cd3ab573) m |
| `#08306b` | over [2](../../SOURCES.md#F-4085947e64) m |
| transparent | no band read |

## Where it came from

- <span class="claim" data-claim="C-DQ-F-BANDS">Depth bands read against the printed legend palette.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-BANDS "What this claim rests on")</sup>
- <span class="claim" data-claim="C-DQ-F-SCALE">Scale from each sheet's own scale bar, via the PDF text layer.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-SCALE "What this claim rests on")</sup>
- <span class="claim" data-claim="C-DQ-F-POSITION">Position: an ensemble water cross-correlation for [3](../../SOURCES.md#F-f9cc0f3951) sheets; control points reported by a resident for [4](../../SOURCES.md#F-4c92fc9f16); then sheet-to-sheet image registration on masked gradient images and a bundle adjustment over the sheets that overlap usefully.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-POSITION "What this claim rests on")</sup>

## How accurate it is

<span class="claim" data-claim="C-DQ-F-ACC">Mutually consistent to [22.6](../../SOURCES.md#F-854ee6fdbb) m RMS across overlapping sheets, tied to the ground by control points with standard errors of [14.3](../../SOURCES.md#F-8ea8b5359c)–[91](../../SOURCES.md#F-de581817fc) m.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-ACC "What this claim rests on")</sup>
<span class="claim" data-claim="C-DQ-F-NORREBRO">Nørrebro is the exception: no overlapping pair produced a usable correlation peak, so the bundle adjustment could not tie it to the rest; its position rests on its own control points alone.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-NORREBRO "What this claim rests on")</sup>

## What to be careful of

- <span class="claim" data-claim="C-DQ-F-YEARS">The model is a 2012 calculation of a 2010 scenario.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-YEARS "What this claim rests on")</sup> <span class="claim" data-claim="C-DQ-F-SINCE">Anything built after the calculation is not in it.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-SINCE "What this claim rests on")</sup>
- <span class="claim" data-claim="C-DQ-F-WATER">The sheets paint depth over open water as well as over land: [1.31](../../SOURCES.md#F-fcd8ec8568) km² of it falls on the open-water polygons `floodgap.py` checks against. Water standing on water is not modelled flooding; filter it against a water layer if that matters to you.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-WATER "What this claim rests on")</sup>
- <span class="claim" data-claim="C-DQ-F-RECOVERY">This is a recovery of a published figure, not a hydraulic model run. Errors in the recovery are ours, not the city's.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-RECOVERY "What this claim rests on")</sup>

## Licence

<span class="claim" data-claim="C-DQ-F-LICENCE">The underlying model is Københavns Kommune's, published as open data via opendata.dk.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-LICENCE "What this claim rests on")</sup> <span class="claim" data-claim="C-DQ-F-TERMS">This georeferencing is offered on the same terms. Attribute both.</span><sup class="claim-mark">[†](../../CLAIMS.md#C-DQ-F-TERMS "What this claim rests on")</sup>

Method, code and the arguments built on it: https://jjokulian.github.io/copenhagen-waterways/
