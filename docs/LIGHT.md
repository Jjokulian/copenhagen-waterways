# Is there enough light at the bed?

Eelgrass has a requirement, not a preference. Below roughly **11–14% of surface light at the seabed** it does not grow slowly — it dies. The Danish light-attenuation target is built on the same number from the other direction: the environmental objective for Kd is derived by assuming eelgrass needs about 14% of surface irradiance at the depth it is supposed to reach.

So the indicator and the requirement are two ends of one calculation, and the calculation can be run from the raw record rather than inherited from an assessment. ODA publishes the attenuation coefficient per cast, with the fit quality of the regression that produced it. Two lines of arithmetic follow:

```
light at the bed   =  100 · exp(−Kd · bottom depth)
potential depth    =  −ln(0.11) / Kd      the deepest a plant could root
```

## What the record contains

| | |
|---|---:|
| Light casts in the record | 62,741 |
| …with a usable Kd regression (r ≥ 0.9) | 60,697 |
| …in the March–September growing season | 39,101 |
| Stations | 536 |
| Years covered | 1980–2026 |

Attenuation runs from Kd = 0.22 at the clearest tenth to 0.874 at the murkiest, median 0.35.

## The depth a plant could reach

Converting each cast to the deepest point still receiving 11% of surface light:

> Median **6.31 m**. The clearest tenth of casts reach 10.03 m; the murkiest tenth reach only 2.53 m. At the stricter 14% requirement the median falls to **5.62 m**.

That is the whole eelgrass question in one number per cast, and it is computed from a measurement rather than from a model of a reference condition.

## Has it improved?

This is the question thirty-five years of load reduction is supposed to have answered.

| | metres per decade | casts |
|---|---:|---:|
| All casts | -0.251 | 39,101 |
| Only stations present at both ends of the record (2 stations) | -0.068 | 900 |

The second row is the check that matters, and it is the one nobody runs. If a trend appears on all casts but not on the stations measured throughout, it is a trend in **where Denmark chose to measure**, not in the water — the `I1` hypothesis, tested rather than asserted.

## And does the light actually reach the bed?

Where the bottom depth under the ship is also recorded (30,806 casts), the share where the seabed receives at least 11% of surface light is **12%**.

## Station by station

Stations with at least eight years of growing-season casts, sorted by trend. A negative number is water getting darker.

| station | casts | years | median Kd | median depth at 11% | m/decade |
|---|---:|---|---:|---:|---:|
| 710 Øresund, syd, åbne del | 18 | 2007–2014 | 0.255 | 8.66 m | -4.74 |
| 321 Isefjord Yderbredning | 57 | 1989–2005 | 0.43 | 5.13 m | -3.49 |
| øst for Feddet | 186 | 1997–2009 | 0.3 | 7.36 m | -3.17 |
| DMU station 1008 | 38 | 2010–2026 | 0.196 | 11.25 m | -3.10 |
| DMU station 1007 | 34 | 2010–2026 | 0.195 | 11.33 m | -2.88 |
| Læsø rende | 244 | 1999–2012 | 0.23 | 9.6 m | -2.45 |
| DMU station 413 | 93 | 2011–2026 | 0.197 | 11.21 m | -2.43 |
| DMU station 1009 | 37 | 2010–2026 | 0.211 | 10.48 m | -2.42 |
| 910 Bornholm, åbne del | 71 | 2002–2026 | 0.24 | 9.18 m | -1.92 |
| DMU station 418 | 40 | 2011–2026 | 0.19 | 11.62 m | -1.91 |
| … | | | | | |
| 712 Køge Bugt | 37 | 1990–1997 | 0.29 | 7.61 m | +2.33 |
| BEGTRUP VIG | 36 | 2007–2014 | 0.24 | 9.2 m | +2.39 |
| Stationsnavn ej angivet | 37 | 2007–2014 | 0.23 | 9.6 m | +2.74 |
| 310 Hesselø Bugt, øst, åbne del | 26 | 2007–2014 | 0.18 | 12.26 m | +2.81 |
| VEJLBY HAGE | 40 | 2007–2014 | 0.27 | 8.18 m | +2.97 |
| SKÆRING STRAND | 38 | 2007–2014 | 0.27 | 8.18 m | +3.07 |
| 400 M SYD FOR BUGTRØRET | 33 | 2007–2014 | 0.26 | 8.49 m | +3.08 |
| FÆRGEHAVN | 33 | 2007–2014 | 0.25 | 8.83 m | +3.41 |
| Stationsnavn ej angivet | 34 | 2007–2014 | 0.24 | 9.2 m | +3.83 |
| Nordsøen | 15 | 2016–2025 | 0.212 | 10.43 m | +8.38 |

## What this does and does not settle

It settles the arithmetic, which was never in doubt, and it puts a number on the thing the Kd indicator is a proxy for. What it cannot settle is *why* the light is where it is. Kd is one broadband number and its causes do not separate — phytoplankton, resuspended mineral sediment, coloured dissolved organic matter and drifted detritus all darken water identically at this resolution. That is `Z8`, and it is why a Kd exceedance is attributed to algae by assumption rather than by measurement.

It also cannot see the shading that happens *after* the light has passed through the water. Epiphytes growing on the leaf shade the host at the blade surface, where no water-column measurement reaches (`Z9`), so the nutrient-to-light pathway can operate with every number on this page looking acceptable.

