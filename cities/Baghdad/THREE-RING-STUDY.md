# Baghdad · Population-led rings and cross-city trunks

The central ring encloses the mapped central districts on a convex alignment. The middle and outer rings are each fitted to residential population and the mapped walking network. Their separation varies around the city. The trunk search compares direct cross-city alignments from opposite sides of the outer ring. It checks tagged bridge approaches and possible new crossings against mapped river geometry.

The two-ring reference still supplies the proposal’s budget. The three-ring comparison shows the benefits of a simpler network and the districts where its access or journeys still fall short.

![Two Baghdad networks with full-colour lines, shared stations and cross-Tigris trunks](maps/baghdad-three-ring-comparison.png)

[Current proposal](PROPOSAL.md) · [Two-ring reference](STRAIGHT-THROUGH-NETWORK.md) · [Editable trial GIS](maps/baghdad-three-ring-trial.geojson) · [Machine results](three-ring-study.json.gz)

## Network and access

| Layout | Rings | Services | Short services | Cross-city trunks | Route-km | Station sites | Shared sites | Pairs of sites within 750 m | Parallel pair-km |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Three-ring core · M3 / O4 | 3 | 6 | 0 | 3 | 267.43 | 209 | 13 | 5 | 0.00 |
| Three rings with suburban extensions | 3 | 7 | 0 | 3 | 299.83 | 228 | 14 | 5 | 0.00 |
| Named suburbs and urban gap line | 3 | 8 | 0 | 3 | 307.16 | 232 | 16 | 5 | 0.00 |
| Two-ring reference | 2 | 36 | 8 | 2 | 785.14 | 641 | 115 | 379 | 24.98 |
| Retained trunks with named connections | 3 | 9 | 0 | 3 | 305.26 | 232 | 20 | 1 | 0.00 |
| Retained trunks with named connections and urban gap line | 3 | 10 | 0 | 3 | 312.99 | 237 | 23 | 2 | 0.00 |
| Retained spaced core | 3 | 6 | 0 | 3 | 266.93 | 212 | 17 | 1 | 0.00 |

The passenger comparisons hold running supply at **282,650 train-km/day**. The housing test searches journeys with up to two changes. The wider metropolitan test assigns least-generalised-cost trips, then reports the share using up to two changes. Both population layers use the same retained street graph and a 1.3 km maximum walk.

| Layout | WorldPop within 1.3 km | GHSL within 1.3 km | WorldPop reached only via middle-ring sites | Housing ≤2 changes | Wider journeys ≤2 changes | Headway |
|---|---:|---:|---:|---:|---:|---:|
| Three-ring core · M3 / O4 | 47.22% | 46.71% | 1,094,968 | 20.20% | 16.98% | 2.04 min |
| Three rings with suburban extensions | 48.15% | 47.35% | 1,094,968 | 20.63% | 17.23% | 2.29 min |
| Named suburbs and urban gap line | 49.69% | 48.29% | 1,054,437 | 21.14% | 17.82% | 2.35 min |
| Two-ring reference | 76.72% | 77.37% | 0 | 77.63% | 57.67% | 6.00 min |
| Retained trunks with named connections | 52.30% | 52.01% | 1,012,792 | 30.70% | 23.69% | 2.33 min |
| Retained trunks with named connections and urban gap line | 54.09% | 53.28% | 898,425 | 32.38% | 25.89% | 2.39 min |
| Retained spaced core | 50.49% | 50.55% | 1,012,792 | 28.93% | 22.10% | 2.04 min |

## Named suburban destinations

The table gives the shortest mapped street walk from each fixed anchor to a station. Nahrawan and Tajiyat use station locations retained from the earlier network. The Basmaya anchor is in the residential estate, east of the earlier M02 approach.
An em dash means the mapped walking graph did not establish a path within its search distance.

| Layout | Basmaya | Nahrawan | Tajiyat |
|---|---:|---:|---:|
| Three-ring core · M3 / O4 | 301 m | 39 m | — |
| Three rings with suburban extensions | 301 m | 39 m | 61 m |
| Named suburbs and urban gap line | 301 m | 39 m | 61 m |
| Two-ring reference | 2,382 m | 79 m | 121 m |
| Retained trunks with named connections | 534 m | 640 m | 61 m |
| Retained trunks with named connections and urban gap line | 534 m | 640 m | 61 m |
| Retained spaced core | — | — | — |

The comparison tests two ways to reach the named suburbs. One redraws through trunks around the destinations. The other keeps the previous spaced trunks and adds screened connections. Both test one additional line for urban coverage.

The named connections share exact outer-ring stations. The 5 km check uses the end of a short connector if it finishes before the dotted measurement contour.

| Destination | Service | Ring interchange | Added km | New station sites |
|---|---|---|---:|---:|
| Basmaya | RGN-Basmaya | M16-R35 | 14.35 | 8 |
| Nahrawan | RGN-Nahrawan | M16-A65750 | 19.73 | 10 |
| Tajiyat | RGN-Tajiyat | M16-A28000 | 4.25 | 2 |

## One line through the largest urban gaps

**U01** adds **7.73 route-km** inside the outer ring and 5 new station sites. It shares stations with M09, T01, T03 and adds 1.3 km walking access for **153,463 WorldPop residents** and **93,717 GHSL residents** inside the outer ring. The zero-additional-line case shows the effect of the change.


## Suburban extensions on the through services

The core search chose new termini within a 11 km band beyond the outer ring. It also discounted the approach score as length increased. The illustrated core's ordinary ends finished within 17.64 km of the ring, leaving much of the suburban catchment unserved.

The continuation search tests up to **20 km per trunk end**. It keeps the original stations and through services, screens new alignments for heading, water, station spacing and parallel duplication, and ranks the options by additional residents within a 1.3 km street walk on both population grids.

The diamonds mark former termini, which remain intermediate stops. The suburban screen checks routes running alongside each other within 5 km outside the outer ring for at least 1.5 continuous km. It checks the original approaches and added extensions together. Each trunk also crosses a contour 2.5 km beyond the ring at sites at least 5 km from those of every other trunk. This separates routes that fan out too late. The dense-city spacing checks still apply inside the ring.

The closest pair of suburban contour crossings in the extended trial is **6.46 km apart**.

The resulting package extends **5 trunk ends** by **28.15 route-km** and adds **17 station sites**. It reaches **73,174 more WorldPop residents** and **39,480 more GHSL residents** than the same core. Passengers stay on the same service to cross the river and reach the rings.

The suburban shares below use the same territory outside the three-ring outer alignment for every case.

| Layout | WorldPop suburban walk reach | GHSL suburban walk reach |
|---|---:|---:|
| Two-ring reference | 53.78% | 56.02% |
| Three-ring core · M3 / O4 | 26.76% | 28.06% |
| Three rings with suburban extensions | 29.18% | 29.83% |

| Trunk | From former terminus | New terminus (nearby mapped place) | Added km | New sites | New WorldPop reach |
|---|---|---|---:|---:|---:|
| T01 | T01-S23 | T01-X2-01 | 1.98 | 1 | 19,374 |
| T03 | T03-S13 | T03-X2-04 | 6.93 | 4 | 30,696 |
| T02 | T02-S22 | T02-X2-06 (AL-kalsha) | 10.36 | 6 | 14,385 |
| T02 | T02-S01 | T02-X1-03 | 4.56 | 3 | 4,614 |
| T03 | T03-S01 | T03-X1-03 (داود عيسى) | 4.31 | 3 | 4,104 |

Per-extension gains are counted in selection order. The reported residents are unique across the package.


A resident is counted in the middle-ring-only column if they lose their 1.3 km access when stations exclusive to that ring are removed. Shared stations stay available in this test.

### Neighbourhoods previously served only by short routes

| Layout | Population grid | Former catchment | Still within 1.3 km | Of those, served only by middle-ring sites | Lost access |
|---|---|---:|---:|---:|---:|
| Three-ring core · M3 / O4 | worldpop-2026 | 272,311 | 158,801 | 40,265 | 113,510 |
| Three-ring core · M3 / O4 | ghsl-2025 | 216,037 | 126,394 | 26,724 | 89,643 |
| Three rings with suburban extensions | worldpop-2026 | 272,311 | 158,801 | 40,265 | 113,510 |
| Three rings with suburban extensions | ghsl-2025 | 216,037 | 126,394 | 26,724 | 89,643 |
| Named suburbs and urban gap line | worldpop-2026 | 272,311 | 158,801 | 40,265 | 113,510 |
| Named suburbs and urban gap line | ghsl-2025 | 216,037 | 126,394 | 26,724 | 89,643 |
| Two-ring reference | worldpop-2026 | 272,311 | 272,311 | 0 | 0 |
| Two-ring reference | ghsl-2025 | 216,037 | 216,037 | 0 | 0 |
| Retained trunks with named connections | worldpop-2026 | 272,311 | 168,067 | 36,963 | 104,244 |
| Retained trunks with named connections | ghsl-2025 | 216,037 | 125,069 | 24,517 | 90,968 |
| Retained trunks with named connections and urban gap line | worldpop-2026 | 272,311 | 170,055 | 35,561 | 102,256 |
| Retained trunks with named connections and urban gap line | ghsl-2025 | 216,037 | 125,561 | 24,310 | 90,476 |
| Retained spaced core | worldpop-2026 | 272,311 | 165,970 | 36,963 | 106,341 |
| Retained spaced core | ghsl-2025 | 216,037 | 122,656 | 24,517 | 93,381 |

The map marks the largest areas where the trial loses existing walking access. The machine record also contains overall access gains and losses, named destinations and the 1.2 km walking sensitivity.

## Geometry and station placement

| Distance from inner alignment to next ring | 10th percentile | Median | 90th percentile |
|---|---:|---:|---:|
| Central to middle | 2.92 km | 4.02 km | 4.98 km |
| Middle to outer | 2.00 km | 2.78 km | 3.63 km |

The inner ring has **0.00 km** of close non-adjacent alignment, down from **4.60 km**. The screen counts reaches within 850 m of another point at least 1.5 km away along the ring.

Shared trunk stations provide the ring connections in the illustrated layout.

| Trunk | Route-km | Route ÷ chord | Shared stations on the three rings |
|---|---:|---:|---|
| T01 | 36.94 | 1.005 | M09 (2), M15 (2), M16 (2) |
| T02 | 30.44 | 1.072 | M09 (1), M15 (2), M16 (2) |
| T03 | 50.03 | 1.085 | M09 (2), M15 (1), M16 (2) |

Trunks serve both sides of the outer ring with one Tigris crossing each. Shared station sites are retained before adding local stops. Dedicated railway bridges, grades, junctions, accessible station entrances and operating headways require site and engineering work.


To evaluate an edited layout, change its line geometry and ordered station IDs in the trial GeoJSON. Omit any line to withdraw it. The evaluator rebuilds transfers, service and cost for the full network.

`./osr design railway baghdad-three-rings --layout revised.geojson --output build/baghdad-layout-trial`

## Like-for-like capital and service allowances

The priced cases use the same six-minute budget offer, unit rates and curved-stock method. The six-minute costing offer sets fleet and supply quantities separately from the matched train-km passenger comparison.

| Layout | Running-track km | Fleet | Standard casting, haul and erection hours | Base installed US$bn | Annual operation US$bn | 30-year present US$bn |
|---|---:|---:|---:|---:|---:|---:|
| Three-ring core · M3 / O4 | 534.87 | 181 | 1,832,888 | 13.73 | 0.38 | 21.29 |
| Three rings with suburban extensions | 599.67 | 199 | 2,289,400 | 15.20 | 0.43 | 23.57 |
| Named suburbs and urban gap line | 614.32 | 205 | 2,344,960 | 15.60 | 0.43 | 24.15 |
| Two-ring reference | 1,568.22 | 581 | 6,259,184 | 43.12 | 1.16 | 65.94 |
| Retained trunks with named connections | 610.52 | 205 | 2,152,568 | 15.63 | 0.43 | 24.15 |
| Retained trunks with named connections and urban gap line | 625.97 | 211 | 2,211,120 | 16.08 | 0.44 | 24.80 |
| Retained spaced core | 533.87 | 181 | 1,833,192 | 13.85 | 0.39 | 21.46 |

| Layout | Concurrent yards | Last standard-stock day | Curved girder pieces | Route-km on unresolved beam or crossing forms |
|---|---:|---:|---:|---:|
| Three-ring core · M3 / O4 | 8 | 2,612 | 1,530 | 28.11 |
| Three rings with suburban extensions | 8 | 2,612 | 1,556 | 30.50 |
| Named suburbs and urban gap line | 8 | 2,612 | 1,556 | 31.05 |
| Two-ring reference | 8 | 3,202 | 2,382 | 269.27 |
| Retained trunks with named connections | 8 | 2,612 | 1,562 | 31.04 |
| Retained trunks with named connections and urban gap line | 8 | 2,612 | 1,562 | 31.81 |
| Retained spaced core | 8 | 2,612 | 1,528 | 28.65 |

These allowances include the counted recurring stock and curved-piece premium. New bridges, station interfaces and other held structures need separate design and prices. The model leaves the project opening date open.

## Decision checks

- **Three-ring core · M3 / O4** · Named suburban destinations outside street walking catchment: Tajiyat. WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.
- **Three rings with suburban extensions** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.
- **Named suburbs and urban gap line** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.
- **Retained trunks with named connections** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.
- **Retained trunks with named connections and urban gap line** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.
- **Retained spaced core** · Named suburban destinations outside street walking catchment: Basmaya, Nahrawan, Tajiyat. WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.

## Reuse in larger cities

The shared metropolitan comparison checks named destinations and walking coverage, then compares installed and whole-life cost under matched service and price assumptions. It keeps research leads visible while adoption depends on the same access and engineering requirements. A city needs its own walkable streets, population grids, destinations and crossing constraints to run this search.

[Shared metropolitan method](../../docs/design-engine/current/METROPOLITAN-NETWORKS.md)

Reproduce with `OPENBLAS_NUM_THREADS=1 ./osr design railway baghdad-three-rings --check`.

Publication `b55ca941bcd28fdd091e511958fe7c0981c02b9e95454741d25f096675f515d0`.
