# Copenhagen 2012 cloudburst flood model, georeferenced

Modelled inundation depth for a 100-year rainfall event on the 2010 city, from Københavns Kommune's Skybrudsplan. Recovered from the seven published PDF sheets, whose geospatial metadata had been stripped, and placed back on the map.

## How to load it

Open any `<sheet>.png` in QGIS. The matching `.pgw` world file and `.prj` sit beside it,
so it lands in the right place in EPSG:4326 with no further steps.

Pixel values are depth bands, not metres:

| value | depth |
|---|---|
| 1 | 0.05-0.1 m |
| 2 | 0.1-0.2 m |
| 3 | 0.2-0.5 m |
| 4 | 0.5-1 m |
| 5 | 1-2 m |
| 6 | over 2 m |
| 0 | no modelled flooding, or outside the sheet |

## Where it came from

- Depth bands read by exact match against the printed legend palette.
- Scale from each sheet's own scale bar, via the PDF text layer.
- Position: an ensemble water cross-correlation for four sheets; control points located on a web map by a resident for three; then sheet-to-sheet image registration on masked gradient images and a bundle adjustment over all seven together.

## How accurate it is

Mutually consistent to 23 m RMS across overlapping sheets, tied to the ground by control points with standard errors of 58-91 m. Nørrebro is the exception: no overlapping pair produced a usable correlation peak and it has no control points, so it keeps its original automatic position and is not known to be consistent with the rest.

## What to be careful of

- The model is a 2012 calculation of a 2010 scenario. Nordhavn, most of Ørestad, Sluseholmen and Teglholmen, and much of Refshaleøen have been built since and are not in it - 344 ha of today's impervious surface, 8.1% of the city, lies outside every sheet.
- The sheets paint depth over lakes and the harbour as well as over land. Water standing on water is not modelled flooding; filter it against a water layer if that matters to you.
- This is a recovery of a published figure, not a hydraulic model run. Errors in the recovery are ours, not the city's.

## Licence

The underlying model is Københavns Kommune's, published as open data via opendata.dk. This georeferencing is offered on the same terms. Attribute both.

Method, code and the arguments built on it: https://jjokulian.github.io/copenhagen-waterways/
