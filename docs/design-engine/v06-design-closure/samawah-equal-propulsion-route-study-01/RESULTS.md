# Samawah route geometry comparison — fixed propulsion and service

## Finding

The geometry proposal shortens the five Samawah lines by **3.265 km (5.64%)**, keeps every station coordinate fixed, and reduces the modeled fleet from **71 to 68 trainsets**. Under the current conditional Class-C cost model, however, base installed capital rises from **$1.034 billion to $1.130 billion (+$95.9 million, 9.27%)** and 30-year NPV rises from **$2.077 billion to $2.140 billion (+$63.6 million, 3.06%)**.

The main reason is a proposal-specific construction allowance of **$97.93 million base** for unverified right-of-way, access and crossing risk. The model adds that allowance to the revised route, not the published route. It is not a supplier quote or measured site cost. The direct guideway and fleet quantities fall, but this conditional risk allowance more than offsets those modeled savings. Do not read this result as proof that a straighter route is inherently more expensive; the route needs survey, crossing, utility and access evidence before that comparison can be settled.

## Comparable inputs

| Input | Both cases |
|---|---:|
| Physical vehicle candidate | `756a6887…` |
| Body candidate | `9489e4f2…` |
| Lines / formation | Same five Samawah lines; six-car train |
| Peak demand assumption | 4,000 passengers/hour/direction on each line; not a surveyed forecast |
| Planning occupancy / availability | 85% / 99%; assumptions, not achieved values |
| Modeled headway | 200 seconds on all five lines |
| Speed cap / acceleration | 20 m/s (72 km/h) / 1.0 m/s² |
| Propulsion policy | `powered-axle-continuous-research` on all five lines |
| Propulsion allowance | 1,000 kg/car, 100 kg/car rotating-equivalent mass, four motors/car |
| Rated power hypothesis | 749 kW/car; no available-force map is attached |
| Cost basis | `project-make-buy`, Class C, USD; no confirmed quote or project-volume discount |

No demand, occupancy, vehicle, station, speed-cap, acceleration-policy, propulsion-family or pricing override differs between the two requests. The 200-second headway is fixed in both cases. Route-dependent runtime and adaptive dwell are recalculated, so the resulting dwell times can differ; this is an equal-input planning comparison, not a guarantee of identical service trajectories. The geometry case fixes all published station coordinates and simplifies each route between adjacent stops with symmetric 5 m samples and a 20 m maximum deviation tolerance.

## Route and service result

| Line | Published route | Simplified route | Length change | Headway both | Trainsets before → after |
|---|---:|---:|---:|---:|---:|
| 1 | 26.603 km | 24.280 km | −2.323 km | 200 s | 28 → 27 |
| 2 | 12.753 km | 12.135 km | −0.618 km | 200 s | 17 → 15 |
| 3 | 8.789 km | 8.585 km | −0.204 km | 200 s | 13 → 13 |
| 4 | 5.444 km | 5.360 km | −0.084 km | 200 s | 7 → 7 |
| 5 | 4.284 km | 4.248 km | −0.035 km | 200 s | 6 → 6 |
| **Total** | **57.873 km** | **54.608 km** | **−3.265 km** | — | **71 → 68** |

Each line retained its existing operational stops. No close stations were merged in this experiment. Maximum sampled deviation was **19.345 m**; the route was not checked against a surveyed right-of-way, obstacles, utilities, geotechnical data, noise-sensitive sites or construction access.

## Calculated prices

| Measure | Published route | Simplified route | Change |
|---|---:|---:|---:|
| Installed capital, low | $284.89m | $300.35m | +$15.46m (+5.43%) |
| Installed capital, base | $1,034.15m | $1,130.03m | +$95.89m (+9.27%) |
| Installed capital, high | $6,345.70m | $7,080.65m | +$734.95m (+11.58%) |
| 30-year NPV, low | $584.80m | $590.57m | +$5.77m (+0.99%) |
| 30-year NPV, base | $2,076.80m | $2,140.42m | +$63.62m (+3.06%) |
| 30-year NPV, high | $12,188.06m | $12,772.95m | +$584.88m (+4.80%) |
| Base installed capital per route-km | $17.87m/km | $20.69m/km | +15.81% |

Both cases contain the same fourteen low/base/high scope accounts. In the revised route, base guideway cost falls **$4.02m**, rolling-stock cost falls **$10.04m**, and modeled network electricity NPV falls **$14.89m**. The revised-alignment access/crossing risk allowance adds **$97.93m** in the construction scope; contingency and prototype/review allowances also rise with the larger modeled direct package. Operations and recovery scopes are unchanged.

The estimate remains highly uncertain. It uses transferred process rates and site/class assumptions, not local bids, route surveys or negotiated bulk purchasing. The high case is particularly broad. The risk allowance is an explicit model input and should be replaced by route-specific evidence, not removed merely to make the option look cheaper.

The allowance is **$21.75m / $97.93m / $603.13m** low/base/high. Its quantity basis is an assumed **20 m right-of-way width** over 54,608 m (1,092,167 m²) and an assumed **5% bridge-risk fraction** (2,730 m). The model adds no access walkway quantity. This is a Class C risk reserve derived from transferred rates; it does not mean the alignment has been surveyed, the land acquired, crossings designed or bridges built.

## Propulsion and maturity

Both cases hold the same research propulsion family across all five lines. The model assigns its provisional equipment mass, continuous-feed route and cost, but **`actual_available_force_map` is null**. The study therefore has a completed calculated outline under its declared assumptions; it does not demonstrate that the trains can achieve these motions. Physical journey, engineering, manufacturing and operating acceptance remain false.

This is a Samawah route sensitivity only. It does not establish prices for the other 265 city projects, validate the city demand forecast, select powered-axle propulsion, or close the wider vehicle, civil and safety evidence gaps.

## Evidence identities

| Evidence | Identity |
|---|---|
| Source epoch | `bfa3cbd3abb8336e3c35981cf5991811662b1065` |
| Current 266-city publication manifest | `332e3362c179462fd000af41965dfc1b75096ff11d00b7c109521d5c6bd166b5` |
| Current Samawah planning seed | `d11009e11222e27968cd797e949fbdc853358d38c35ef37c66ac3ea0e6228dba` |
| Baseline city study | `1fecdd2bde9d8cfa390359abb7eff140` |
| Revised-route city study | `0f4bde982b8d4950cb45f8959c1032ad` |
| Route generation | `191ece2baca9eb36d438ce09d9269dd18dcad4a432fa47084218a8c77f92cb68` |
| Comparison packet | `73c731e3de633814e743ba7e227ba871633e185f72ea13e6bb4f1e81e4de68ed` |
| Packet manifest | `965bad783ed4a773d7cf39793ec6daeb1a3418dd3e0733c3972a830189ebdbcd` |

Both studies were newly calculated, then replay-verified; neither exact study cache was reused. The wider 266-city source refresh was also independently replayed. Process resource limits were recorded, but no OS-enforced sandbox was used.
