# Is there enough light at the bed?

Eelgrass has a requirement, not a preference. Below roughly **[11](SOURCES.md#F-e0cd5a53f8)–[14](SOURCES.md#F-5621596820)% of surface light at the seabed** it does not grow slowly — it dies. The Danish light-attenuation target is built on the same number from the other direction: the environmental objective for Kd is derived by assuming eelgrass needs about [14](SOURCES.md#F-5621596820)% of surface irradiance at the depth it is supposed to reach.

So the indicator and the requirement are two ends of one calculation, and the calculation can be run from the raw record rather than inherited from an assessment. ODA publishes the attenuation coefficient per cast, with the fit quality of the regression that produced it. Two lines of arithmetic follow:

```
light at the bed   =  100 · exp(−Kd · bottom depth)
potential depth    =  −ln(r) / Kd      r the light requirement: the deepest a plant could root
```

## What the record contains

| | |
|---|---:|
| Light casts in the record | [62,741](SOURCES.md#F-e98d356567) |
| …with a usable Kd regression (r ≥ [0.9](SOURCES.md#F-aba786ac0d), or no fit reported) | [60,697](SOURCES.md#F-7e31872a83) |
| …in the March–September growing season | [39,101](SOURCES.md#F-30f79a7c76) |
| Stations | [536](SOURCES.md#F-f092698376) |
| Years covered | [1980](SOURCES.md#F-a8cef07c63)–[2026](SOURCES.md#F-4e008ddd04) |

Attenuation runs from Kd = [0.22](SOURCES.md#F-de8a9ea4a1) (p10, the clearest casts) to [0.874](SOURCES.md#F-fb41ea2418) (p90, the murkiest), median [0.35](SOURCES.md#F-e3f61c1a83).

## The depth a plant could reach

Converting each cast to the deepest point still receiving [11](SOURCES.md#F-e0cd5a53f8)% of surface light:

> Median **[6.31](SOURCES.md#F-757e12357a) m**. The clearest casts (p90) reach [10.03](SOURCES.md#F-c1eb42b27e) m; the murkiest (p10) reach only [2.53](SOURCES.md#F-c2c4e6102a) m. At the stricter [14](SOURCES.md#F-5621596820)% requirement the median falls to **[5.62](SOURCES.md#F-3af5febcd2) m**.

That is the whole eelgrass question in one number per cast, and it is computed from a measurement rather than from a model of a reference condition.

## Has it improved?

This is the question decades of load reduction are supposed to have answered.

| | metres per decade | casts |
|---|---:|---:|
| All casts | [-0.251](SOURCES.md#F-f1e2b1dc23) | [39,101](SOURCES.md#F-59463d4225) |
| Only stations present at both ends of the record ([2](SOURCES.md#F-0f944d1be8) stations) | [-0.068](SOURCES.md#F-01527b7dec) | [900](SOURCES.md#F-52775c8607) |

*Both ends* means casts in the first and in the last [5](SOURCES.md#F-bbe1fbaea3) years of the record; [2](SOURCES.md#F-0f944d1be8) stations qualify, so the second row rests on those alone.

The second row is the check that matters, and it is the one nobody runs. If a trend appears on all casts but not on the stations measured throughout, it is a trend in **where Denmark chose to measure**, not in the water — hypothesis [I1 — Changing station network](hypodrafts/I1.md "Changing station network"), put to the record rather than asserted.

## And does the light actually reach the bed?

Where a bottom depth is known ([39,094](SOURCES.md#F-bbf74582b8) casts: [36,933](SOURCES.md#F-4c385f6b6f) from a sounding on the same day, [2,161](SOURCES.md#F-c3b1c5c6a0) from the station's median sounding), the share where the seabed receives at least [11](SOURCES.md#F-e0cd5a53f8)% of surface light is **[12](SOURCES.md#F-9193fc1d54)%**.

## Station by station

Stations with at least [8](SOURCES.md#F-9a94079511) years of growing-season casts, sorted by trend: the darkening end and the brightening end. A negative number is water getting darker.

| station | casts | years | median Kd | median depth at [11](SOURCES.md#F-e0cd5a53f8)% | m/decade |
|---|---:|---|---:|---:|---:|
| `710 Øresund, syd, åbne del` | [18](SOURCES.md#F-d25e2ab005) | [2007](SOURCES.md#F-ccc89ed7e7)–[2014](SOURCES.md#F-34468bbbb5) | [0.255](SOURCES.md#F-aba088883f) | [8.66](SOURCES.md#F-0f8dba9d4d) m | [-4.74](SOURCES.md#F-748dd7b741) |
| `321 Isefjord Yderbredning` | [57](SOURCES.md#F-2170b92a9b) | [1989](SOURCES.md#F-78bff007e7)–[2005](SOURCES.md#F-255a36be87) | [0.43](SOURCES.md#F-c080c90a43) | [5.13](SOURCES.md#F-40db33b6ef) m | [-3.49](SOURCES.md#F-0069e3a006) |
| øst for Feddet | [186](SOURCES.md#F-fce8d27064) | [1997](SOURCES.md#F-50fad5215b)–[2009](SOURCES.md#F-b59a6f5409) | [0.3](SOURCES.md#F-bb342bafde) | [7.36](SOURCES.md#F-15cfa3d86c) m | [-3.17](SOURCES.md#F-91d2e90a36) |
| `DMU station 1008` | [38](SOURCES.md#F-028f5ad457) | [2010](SOURCES.md#F-7d40906d47)–[2026](SOURCES.md#F-9c287a61d6) | [0.196](SOURCES.md#F-150d17b65e) | [11.25](SOURCES.md#F-2f723e15a1) m | [-3.10](SOURCES.md#F-88ca56308a) |
| `DMU station 1007` | [34](SOURCES.md#F-d9c0c6b55a) | [2010](SOURCES.md#F-f48bb18b39)–[2026](SOURCES.md#F-9a0cbb44e7) | [0.195](SOURCES.md#F-739ac844b5) | [11.33](SOURCES.md#F-0b5fa6fc82) m | [-2.88](SOURCES.md#F-f612bdae43) |
| Læsø rende | [244](SOURCES.md#F-877fe955ff) | [1999](SOURCES.md#F-fa1df2662f)–[2012](SOURCES.md#F-58aefe2490) | [0.23](SOURCES.md#F-06a115021c) | [9.6](SOURCES.md#F-f41c7d409f) m | [-2.45](SOURCES.md#F-9b44cc013b) |
| `DMU station 413` | [93](SOURCES.md#F-a6cdd13307) | [2011](SOURCES.md#F-3b618be85a)–[2026](SOURCES.md#F-94d877ae30) | [0.197](SOURCES.md#F-f772b94bfb) | [11.21](SOURCES.md#F-5c280327fc) m | [-2.43](SOURCES.md#F-ce11fb1885) |
| `DMU station 1009` | [37](SOURCES.md#F-cd70d9395b) | [2010](SOURCES.md#F-8c45d1965d)–[2026](SOURCES.md#F-ea555a9ab2) | [0.211](SOURCES.md#F-d6b4352718) | [10.48](SOURCES.md#F-ef3f6afb5a) m | [-2.42](SOURCES.md#F-7e0a7cf012) |
| `910 Bornholm, åbne del` | [71](SOURCES.md#F-04344d4fd9) | [2002](SOURCES.md#F-f3269a0b36)–[2026](SOURCES.md#F-2ca2258f49) | [0.24](SOURCES.md#F-7e877b2201) | [9.18](SOURCES.md#F-94f11958b8) m | [-1.92](SOURCES.md#F-7663a11b77) |
| `DMU station 418` | [40](SOURCES.md#F-cc5893a120) | [2011](SOURCES.md#F-55376f1e65)–[2026](SOURCES.md#F-ffe3c6b06b) | [0.19](SOURCES.md#F-b6a8c21c61) | [11.62](SOURCES.md#F-0a05b189e7) m | [-1.91](SOURCES.md#F-4d71acad9f) |
| … | | | | | |
| `712 Køge Bugt` | [37](SOURCES.md#F-beb3bf461d) | [1990](SOURCES.md#F-b19f4ced91)–[1997](SOURCES.md#F-1e7c4302f9) | [0.29](SOURCES.md#F-665af74a97) | [7.61](SOURCES.md#F-46192378cc) m | [+2.33](SOURCES.md#F-0012fc065b) |
| BEGTRUP VIG | [36](SOURCES.md#F-d2bd7bafde) | [2007](SOURCES.md#F-07ded2ed76)–[2014](SOURCES.md#F-bf007555cb) | [0.24](SOURCES.md#F-77263d4b12) | [9.2](SOURCES.md#F-1ae7c3cf26) m | [+2.39](SOURCES.md#F-75b3f2b2ee) |
| Stationsnavn ej angivet | [37](SOURCES.md#F-d3ef6365aa) | [2007](SOURCES.md#F-3b93d2f52e)–[2014](SOURCES.md#F-95b1a251f2) | [0.23](SOURCES.md#F-13c0d96b92) | [9.6](SOURCES.md#F-d2175b3709) m | [+2.74](SOURCES.md#F-2ee738b3cc) |
| `310 Hesselø Bugt, øst, åbne del` | [26](SOURCES.md#F-ae98695cbe) | [2007](SOURCES.md#F-be7d4b2659)–[2014](SOURCES.md#F-e5faa3d346) | [0.18](SOURCES.md#F-017e363d66) | [12.26](SOURCES.md#F-f99f4f7ea7) m | [+2.81](SOURCES.md#F-9fd9222e43) |
| VEJLBY HAGE | [40](SOURCES.md#F-2a8ac25791) | [2007](SOURCES.md#F-31ffb1fe15)–[2014](SOURCES.md#F-cee8395534) | [0.27](SOURCES.md#F-0bb687b538) | [8.18](SOURCES.md#F-de153c90e9) m | [+2.97](SOURCES.md#F-bcc9731e35) |
| SKÆRING STRAND | [38](SOURCES.md#F-b7e8dacea5) | [2007](SOURCES.md#F-ad0a490cf9)–[2014](SOURCES.md#F-a397b5e229) | [0.27](SOURCES.md#F-316e4f013f) | [8.18](SOURCES.md#F-4e3d261edb) m | [+3.07](SOURCES.md#F-0e0de65ee6) |
| `400 M SYD FOR BUGTRØRET` | [33](SOURCES.md#F-a1cd2a5ccd) | [2007](SOURCES.md#F-c755667a68)–[2014](SOURCES.md#F-4e76bc0fa3) | [0.26](SOURCES.md#F-7769907eda) | [8.49](SOURCES.md#F-ac380b929d) m | [+3.08](SOURCES.md#F-519c501e02) |
| FÆRGEHAVN | [33](SOURCES.md#F-f175e1ad2c) | [2007](SOURCES.md#F-9983299a27)–[2014](SOURCES.md#F-6b6d65d10b) | [0.25](SOURCES.md#F-874e2857b4) | [8.83](SOURCES.md#F-a69258b248) m | [+3.41](SOURCES.md#F-ce7a499b63) |
| Stationsnavn ej angivet | [34](SOURCES.md#F-43af75fad8) | [2007](SOURCES.md#F-3de3126d89)–[2014](SOURCES.md#F-a233cc02d4) | [0.24](SOURCES.md#F-9f0fccd2a7) | [9.2](SOURCES.md#F-1a3a98be37) m | [+3.83](SOURCES.md#F-90b9f1d591) |
| Nordsøen | [15](SOURCES.md#F-bdc5a94faf) | [2016](SOURCES.md#F-6fac28c0f4)–[2025](SOURCES.md#F-e28fcc62f1) | [0.212](SOURCES.md#F-4db0f5a200) | [10.43](SOURCES.md#F-9e0a9d44b5) m | [+8.38](SOURCES.md#F-563e1fb20f) |

## The number depends on where the sensor started

Every figure above rests on Kd, and Kd is a straight line fitted to the logarithm of light against depth. That fit assumes attenuation is the same all the way down. ODA publishes the measurements the line was fitted to, so the assumption can be checked rather than granted: refit the top half of each profile against the bottom half. [53,468](SOURCES.md#F-9fe3c8054f) casts carry enough points to allow it — at least [8](SOURCES.md#F-01b05b63d6) readings spanning at least [2.0](SOURCES.md#F-d6886e449e) m.

| profile starts at | casts | Kd top half | Kd bottom half | ratio | steepens with depth |
|---|---:|---:|---:|---:|---:|
| [0.0](SOURCES.md#F-5e827a9f78) – [0.6](SOURCES.md#F-8a6e7ba403) m | [11,515](SOURCES.md#F-1eaad9c7e5) | [0.361](SOURCES.md#F-a976216222) | [0.317](SOURCES.md#F-631d29e239) | **[0.879](SOURCES.md#F-efdd02dc1e)** | [26.3](SOURCES.md#F-59d136eb92)% |
| [0.6](SOURCES.md#F-b3101491f8) – [1.1](SOURCES.md#F-265f110ca5) m | [11,630](SOURCES.md#F-3eab7d5577) | [0.425](SOURCES.md#F-6c32d2d635) | [0.366](SOURCES.md#F-beab386587) | **[0.878](SOURCES.md#F-88e0e92d4f)** | [22.1](SOURCES.md#F-3dc96d7c4c)% |
| [1.1](SOURCES.md#F-8ac54e8c52) – [2.1](SOURCES.md#F-a63796f3ed) m | [5,360](SOURCES.md#F-eb4811b1ff) | [0.313](SOURCES.md#F-d8f2ad513b) | [0.285](SOURCES.md#F-6441aaf0d8) | **[0.909](SOURCES.md#F-380a3f121c)** | [25.0](SOURCES.md#F-e1bde7f15c)% |
| [2.1](SOURCES.md#F-b7a2826633) – [3.1](SOURCES.md#F-74a4ec6896) m | [2,215](SOURCES.md#F-12701506b9) | [0.293](SOURCES.md#F-54dd28cc13) | [0.269](SOURCES.md#F-c8e62f2efd) | **[0.93](SOURCES.md#F-dda2db9f27)** | [29.7](SOURCES.md#F-816416b7ed)% |
| [3.1](SOURCES.md#F-78b8b110b3) – [5.1](SOURCES.md#F-9513cd4612) m | [2,236](SOURCES.md#F-f7030706f2) | [0.275](SOURCES.md#F-a5964ad222) | [0.261](SOURCES.md#F-64fc0eb5ab) | **[0.962](SOURCES.md#F-d19103596b)** | [40.0](SOURCES.md#F-5dc30d87db)% |
| [5.1](SOURCES.md#F-944f1be009) – [30.0](SOURCES.md#F-8daddb836e) m | [1,066](SOURCES.md#F-b5ea286603) | [0.242](SOURCES.md#F-d55e9d975d) | [0.239](SOURCES.md#F-7fa85e9c38) | **[0.987](SOURCES.md#F-976556d48d)** | [47.5](SOURCES.md#F-56d90df78e)% |

**The bottom half attenuates less, and the gap closes the deeper the profile begins.** That ordering is the whole result. It runs opposite to resuspension — a turbid layer over the bed would make the bottom half steeper, and it does so in only [22](SOURCES.md#F-3dc96d7c4c)–[48](SOURCES.md#F-56d90df78e)% of casts, outweighed on average by something else.

The something else is that a PAR sensor counts photons across the whole band without distinguishing them, and water absorbs the band unevenly - as an earlier version of this page put it, [roughly 0.5 per metre at 700 nm against 0.015 per metre at 450 nm](SOURCES.md#F-1161b27adb). The red part of the light is gone near the surface, and what continues downward is the fraction water attenuates least. So the apparent broadband Kd falls with depth **in perfectly uniform water**, purely because the surviving spectrum has shifted. If that is the mechanism, the effect must fade for profiles that begin below the red-absorbing layer, because the red is already gone. It does: the ratio runs from [0.879](SOURCES.md#F-efdd02dc1e) for profiles starting at the surface to [0.987](SOURCES.md#F-976556d48d) for those starting below [5.1](SOURCES.md#F-944f1be009) m, rising overall though not at every step.

> **What follows is that Kd measured this way is not a property of the water.** It is a property of the water and the depth window jointly. Two casts in identical water, one begun near the surface and one begun deeper, return different numbers. The indicator, the target derived from it, and every figure on this page inherit that.

Splitting the growth-season casts on where they started: [26,662](SOURCES.md#F-b0fb024790) began above [2.0](SOURCES.md#F-5a6a77bc92) m and give a median Kd of [0.35](SOURCES.md#F-f8f56b7f48) and a median depth reaching [11](SOURCES.md#F-e0cd5a53f8)% of [6.31](SOURCES.md#F-b5f33a89f8) m; [7,360](SOURCES.md#F-fbfab234d5) began below [2.0](SOURCES.md#F-5a6a77bc92) m and give [0.27](SOURCES.md#F-341b020904) and [8.18](SOURCES.md#F-301a45c3f7) m. Neither is the true number. They are two answers from one record, separated by a choice nobody documents making.

The measurement that would separate the two explanations — spectral attenuation rather than one broadband coefficient — is not made anywhere in the Danish programme. A single number cannot say whether the light stopped because something was in the water or because water is red-absorbing and the sensor started shallow. That is [Z8 — The attenuation budget is never partitioned](hypodrafts/Z8.md "The attenuation budget is never partitioned") again, one layer below where it is stated.

## The other optical record measures the seabed when the water is shallow

Kd is not the only transparency number Denmark holds. There is also Secchi depth — a white disc lowered until it disappears — [144,208](SOURCES.md#F-d422132c90) readings, [96,708](SOURCES.md#F-e51550bdc9) of them paired with a bottom depth, [1980](SOURCES.md#F-f944d2516c)–[2026](SOURCES.md#F-ef805012bf). It has one hard limit: **a disc cannot be seen deeper than the bottom.** Where the water is shallower than the water is clear, the number recorded is the depth of the seabed.

ODA is straightforward about this and publishes the flag — `SigtTilBund`, sight-to-bottom — which is the only reason any of this can be checked. It is set on [26,380](SOURCES.md#F-1499c2f79d) of [144,208](SOURCES.md#F-d422132c90) readings.

| bottom depth | readings | median Secchi | disc reached the bed |
|---|---:|---:|---:|
| [0](SOURCES.md#F-ad68e454df)–[5](SOURCES.md#F-7f0e8a949b) m | [23,160](SOURCES.md#F-6ce45ba3d4) | [2.0](SOURCES.md#F-c50a014452) m | **[36.9](SOURCES.md#F-46aa1895a2)%** |
| [5](SOURCES.md#F-1c5d691c01)–[10](SOURCES.md#F-5723eac741) m | [20,392](SOURCES.md#F-21dcc91cb3) | [3.9](SOURCES.md#F-6d714d2ea7) m | **[10.0](SOURCES.md#F-2ff095ec97)%** |
| [10](SOURCES.md#F-db815ba183)–[20](SOURCES.md#F-4ed303263b) m | [31,981](SOURCES.md#F-c8d07c0744) | [6.0](SOURCES.md#F-a0ce429432) m | **[0.8](SOURCES.md#F-9a973f2830)%** |
| [20](SOURCES.md#F-94a38e5aba)–[40](SOURCES.md#F-9d63bd2b8f) m | [17,454](SOURCES.md#F-5f906c87db) | [6.5](SOURCES.md#F-870fbeae3b) m | **[0.2](SOURCES.md#F-dbc1d51af8)%** |
| [40](SOURCES.md#F-dc99d4a6e5)–[200](SOURCES.md#F-0a91013e45) m | [3,714](SOURCES.md#F-f5de4748e9) | [8.0](SOURCES.md#F-c6dd3bc60d) m | **[0.0](SOURCES.md#F-68bac1a7d0)%** |

So in water under [5](SOURCES.md#F-7f0e8a949b) m, [36.9](SOURCES.md#F-46aa1895a2)% of the readings are measurements of bathymetry wearing the units of clarity. From [10](SOURCES.md#F-db815ba183) m down it essentially stops happening ([0.8](SOURCES.md#F-9a973f2830)%). The censoring is not an error — it is what the instrument does — but it is **one-sided**: it can only make the water look less clear than it is, never more, and only in the shallows.

**And the censored share is not constant, which is the part that matters for any series built from it.**

| period | readings | disc reached the bed | in water under [5](SOURCES.md#F-b5c79d9a68) m |
|---|---:|---:|---:|
| [1980](SOURCES.md#F-432c8e78e3)–[1994](SOURCES.md#F-41080b98e0) | [16,460](SOURCES.md#F-7579bb638c) | [16.6](SOURCES.md#F-667e46e360)% | [39.3](SOURCES.md#F-20bcdfa918)% |
| [1995](SOURCES.md#F-33f8ff2ad2)–[2004](SOURCES.md#F-ef0880df85) | [24,094](SOURCES.md#F-9422cbe11b) | [9.2](SOURCES.md#F-87dc607923)% | [29.6](SOURCES.md#F-1b81b42b93)% |
| [2005](SOURCES.md#F-a96752daea)–[2014](SOURCES.md#F-9c44527afc) | [27,599](SOURCES.md#F-d9fd8a5405) | [7.3](SOURCES.md#F-899b4fbbed)% | [28.0](SOURCES.md#F-9ae4b8940d)% |
| [2015](SOURCES.md#F-a08c8ea9b5)–[2026](SOURCES.md#F-01dc098679) | [28,555](SOURCES.md#F-88ec06c0f8) | [13.6](SOURCES.md#F-7f08413681)% | [47.2](SOURCES.md#F-d44ffeb8f9)% |

A time-varying censored fraction is a time-varying bias, so a Secchi trend computed across these eras is partly a trend in how often the instrument hit the ground. **Why it varies is not settled here.** Cleaner water would raise it, because a disc that can be seen further reaches the bed more often; so would a shift of effort toward shallower stations; so would a change in field practice. Those are not separable from this table, and the direction of the resulting bias is uncomfortable: a genuine improvement in clarity partly hides itself, because the readings that would show it are the ones that get capped.

The same caution as the Kd section, arrived at from the other side. Neither of Denmark's two transparency records is a clean measurement of the water alone — one depends on where the sensor started, the other on how deep the sea is underneath it.

## What this does and does not settle

It settles the arithmetic, which was never in doubt, and it puts a number on the thing the Kd indicator is a proxy for. What it cannot settle is *why* the light is where it is. Kd is one broadband number and its causes do not separate — phytoplankton, resuspended mineral sediment, coloured dissolved organic matter and drifted detritus all darken water identically at this resolution. That is [Z8](hypodrafts/Z8.md "The attenuation budget is never partitioned"), and it is why a Kd exceedance is attributed to algae by assumption rather than by measurement.

It also cannot see the shading that happens *after* the light has passed through the water. Epiphytes growing on the leaf shade the host at the blade surface, where no water-column measurement reaches ([Z9 — Epiphyte shading, which bypasses the water column](HYPOTHESES.md "Epiphyte shading, which bypasses the water column")), so the nutrient-to-light pathway can operate with every number on this page looking acceptable.

