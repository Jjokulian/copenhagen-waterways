# Copenhagen 2012 cloudburst flood model, georeferenced

Modelled inundation depth for a [100-year](../../SOURCES.md#F-8045f86e1c) rainfall event on the 2010 city, from Københavns Kommune's Skybrudsplan. Recovered from the [7](../../SOURCES.md#F-13d1b87901) published PDF sheets, whose geospatial metadata had been stripped, and placed back on the map.

## How to load it

Open any `<sheet>.png` in QGIS. The matching `.pgw` world file and `.prj` sit beside it, so it lands in the right place in `EPSG:4326` with no further steps.

Pixel values are depth bands, not metres:

| value | depth |
|---|---|
| `1` | [0.05](../../SOURCES.md#F-b72f677f80)–[0.1](../../SOURCES.md#F-554faf5a00) m |
| `2` | [0.1](../../SOURCES.md#F-c7dc27d5c0)–[0.2](../../SOURCES.md#F-6d94ba76df) m |
| `3` | [0.2](../../SOURCES.md#F-77002080ac)–[0.5](../../SOURCES.md#F-5187388230) m |
| `4` | [0.5](../../SOURCES.md#F-28360d417a)–[1](../../SOURCES.md#F-6012071389) m |
| `5` | [1](../../SOURCES.md#F-a309b93986)–[2](../../SOURCES.md#F-d6cd3ab573) m |
| `6` | over [2](../../SOURCES.md#F-4085947e64) m |
| `0` | no modelled flooding, or outside the sheet |

## Where it came from

- Depth bands read against the printed legend palette.
- Scale from each sheet's own scale bar, via the PDF text layer.
- Position: an ensemble water cross-correlation for [3](../../SOURCES.md#F-f9cc0f3951) sheets; control points located on a web map by a resident for [4](../../SOURCES.md#F-4c92fc9f16); then sheet-to-sheet image registration on masked gradient images and a bundle adjustment over the sheets that overlap usefully.

## How accurate it is

Mutually consistent to [22.6](../../SOURCES.md#F-854ee6fdbb) m RMS across overlapping sheets, tied to the ground by control points with standard errors of [14.3](../../SOURCES.md#F-8ea8b5359c)–[91](../../SOURCES.md#F-de581817fc) m.
Nørrebro is the exception: no overlapping pair produced a usable correlation peak, so the bundle adjustment could not tie it to the rest; its position rests on its own control points alone.

## What to be careful of

- The model is a 2012 calculation of a 2010 scenario. Nordhavn, most of Ørestad, Sluseholmen and Teglholmen, and much of Refshaleøen have been built since and are not in it - [344 ha of today](../../SOURCES.md#F-df93efae48)'s impervious surface, [8.1% of the city](../../SOURCES.md#F-16cf74a181), lies outside every sheet.
- The sheets paint depth over lakes and the harbour as well as over land. Water standing on water is not modelled flooding; filter it against a water layer if that matters to you.
- This is a recovery of a published figure, not a hydraulic model run. Errors in the recovery are ours, not the city's.

## Licence

The underlying model is Københavns Kommune's, published as open data via opendata.dk. This georeferencing is offered on the same terms. Attribute both.

Method, code and the arguments built on it: https://jjokulian.github.io/copenhagen-waterways/
