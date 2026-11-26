# Baghdad · Population-led rings and cross-city trunks

The central ring encloses the mapped central districts on a convex alignment. The middle and outer rings are each fitted to residential population and the mapped walking network. Their separation varies around the city. The trunk search compares direct cross-city alignments from opposite sides of the outer ring. It checks tagged bridge approaches and possible new crossings against mapped river geometry.

The two-ring reference still supplies the proposal’s budget. The three-ring comparison shows the benefits of a simpler network and the districts where its access or journeys still fall short.

![Two Baghdad networks with full-colour lines, shared stations and cross-Tigris trunks](maps/baghdad-three-ring-comparison.png)

[Current proposal](PROPOSAL.md) · [Two-ring reference](STRAIGHT-THROUGH-NETWORK.md) · [Editable trial GIS](maps/baghdad-three-ring-trial.geojson) · [Machine results](three-ring-study.json.gz)

## Network and access

| Layout | Rings | Services | Short services | Cross-city trunks | Route-km | Station sites | Shared sites | Pairs of sites within 750 m | Parallel pair-km |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Two-ring reference | 2 | 36 | 8 | 2 | 785.14 | 641 | 115 | 379 | 24.98 |
| Three-ring core · M3 / O4 | 3 | 6 | 0 | 3 | 239.84 | 198 | 17 | 1 | 0.00 |
| Three rings with suburban extensions | 3 | 6 | 0 | 3 | 266.93 | 212 | 17 | 1 | 0.00 |

The passenger comparisons hold running supply at **282,650 train-km/day**. The housing test searches journeys with up to two changes. The wider metropolitan test assigns least-generalised-cost trips, then reports the share using up to two changes. Both population layers use the same retained street graph and a 1.3 km maximum walk.

| Layout | WorldPop within 1.3 km | GHSL within 1.3 km | WorldPop reached only via middle-ring sites | Housing ≤2 changes | Wider journeys ≤2 changes | Headway |
|---|---:|---:|---:|---:|---:|---:|
| Two-ring reference | 76.72% | 77.37% | 0 | 77.63% | 57.67% | 6.00 min |
| Three-ring core · M3 / O4 | 49.79% | 49.74% | 1,012,792 | 28.37% | 21.87% | 1.83 min |
| Three rings with suburban extensions | 50.49% | 50.55% | 1,012,792 | 28.93% | 22.10% | 2.04 min |

## Suburban extensions on the through services

The core search chose new termini within a 11 km band beyond the outer ring. It also discounted the approach score as length increased. The illustrated core's ordinary ends finished within 6.35 km of the ring, leaving much of the suburban catchment unserved.

The continuation search tests up to **20 km per trunk end**. It keeps the original stations and through services, screens new alignments for heading, water, station spacing and parallel duplication, and ranks the options by additional residents within a 1.3 km street walk on both population grids.

The diamonds mark former termini, which remain intermediate stops. The suburban screen checks routes running alongside each other within 5 km outside the outer ring for at least 1.5 continuous km. It checks the original approaches and added extensions together. Each trunk also crosses a contour 2.5 km beyond the ring at sites at least 5 km from those of every other trunk. This separates routes that fan out too late. The dense-city spacing checks still apply inside the ring.

The closest pair of suburban contour crossings in the extended trial is **5.66 km apart**.

The resulting package extends **4 trunk ends** by **27.10 route-km** and adds **14 station sites**. It reaches **59,921 more WorldPop residents** and **59,254 more GHSL residents** than the same core. Passengers stay on the same service to cross the river and reach the rings.

The suburban shares below use the same territory outside the three-ring outer alignment for every case.

| Layout | WorldPop suburban walk reach | GHSL suburban walk reach |
|---|---:|---:|
| Two-ring reference | 53.78% | 56.02% |
| Three-ring core · M3 / O4 | 27.57% | 28.38% |
| Three rings with suburban extensions | 29.38% | 30.61% |

| Trunk | From former terminus | New terminus (nearby mapped place) | Added km | New sites | New WorldPop reach |
|---|---|---|---:|---:|---:|
| T03 | T03-S01 | T03-X1-09 (Mahmoudiyah) | 19.37 | 9 | 51,568 |
| T03 | T03-S12 | T03-X2-02 (قرية ۱ حزيران) | 2.95 | 2 | 3,534 |
| T02 | T02-S01 | T02-X1-01 | 1.99 | 1 | 3,307 |
| T01 | T01-S17 | T01-X2-02 (بيوت الاصلاح قرية) | 2.78 | 2 | 1,512 |

Per-extension gains are counted in selection order. The reported residents are unique across the package.


A resident is counted in the middle-ring-only column if they lose their 1.3 km access when stations exclusive to that ring are removed. Shared stations stay available in this test.

### Neighbourhoods previously served only by short routes

| Layout | Population grid | Former catchment | Still within 1.3 km | Of those, served only by middle-ring sites | Lost access |
|---|---|---:|---:|---:|---:|
| Two-ring reference | worldpop-2026 | 272,311 | 272,311 | 0 | 0 |
| Two-ring reference | ghsl-2025 | 216,037 | 216,037 | 0 | 0 |
| Three-ring core · M3 / O4 | worldpop-2026 | 272,311 | 165,970 | 36,963 | 106,341 |
| Three-ring core · M3 / O4 | ghsl-2025 | 216,037 | 122,656 | 24,517 | 93,381 |
| Three rings with suburban extensions | worldpop-2026 | 272,311 | 165,970 | 36,963 | 106,341 |
| Three rings with suburban extensions | ghsl-2025 | 216,037 | 122,656 | 24,517 | 93,381 |

The map marks the largest areas where the trial loses existing walking access. The machine record also contains overall access gains and losses, named destinations and the 1.2 km walking sensitivity.

## Geometry and station placement

| Distance from inner alignment to next ring | 10th percentile | Median | 90th percentile |
|---|---:|---:|---:|
| Central to middle | 2.92 km | 4.02 km | 4.98 km |
| Middle to outer | 2.00 km | 2.78 km | 3.63 km |

The inner ring has **0.00 km** of close non-adjacent alignment, down from **4.60 km**. The screen counts reaches within 850 m of another point at least 1.5 km away along the ring.

Shared trunk stations provide the ring connections in the illustrated layout.

The deterministic search generated 12 nested orbital combinations and built 3 complete-layout trials. For the illustrated fit, 492 cross-city alignments passed the geometric pool screens. The planner prioritised the Airport, then added coverage while checking station separation and parallel running. The full layouts are ranked on 1.3 km walking reach across both population grids.

| Trunk | Route-km | Route ÷ chord | Shared stations on the three rings |
|---|---:|---:|---|
| T01 | 36.94 | 1.005 | M15 (2), M09 (2), M16 (2) |
| T02 | 30.44 | 1.072 | M15 (2), M09 (1), M16 (2) |
| T03 | 50.03 | 1.085 | M15 (1), M09 (2), M16 (2) |

Trunks serve both sides of the outer ring with one Tigris crossing each. Shared station sites are retained before adding local stops. Dedicated railway bridges, grades, junctions, accessible station entrances and operating headways require site and engineering work.


To evaluate an edited layout, change its line geometry and ordered station IDs in the trial GeoJSON. Omit any line to withdraw it. The evaluator rebuilds transfers, service and cost for the full network.

`./osr design railway baghdad-three-rings --layout revised.geojson --output build/baghdad-layout-trial`

## Like-for-like capital and service allowances

The priced cases use the same six-minute budget offer, unit rates and curved-stock method. The six-minute costing offer sets fleet and supply quantities separately from the matched train-km passenger comparison.

| Layout | Running-track km | Fleet | Standard casting, haul and erection hours | Base installed US$bn | Annual operation US$bn | 30-year present US$bn |
|---|---:|---:|---:|---:|---:|---:|
| Two-ring reference | 1,568.22 | 581 | 6,259,184 | 43.12 | 1.16 | 65.94 |
| Three-ring core · M3 / O4 | 479.67 | 166 | 1,455,504 | 12.71 | 0.36 | 19.68 |
| Three rings with suburban extensions | 533.87 | 181 | 1,833,192 | 13.85 | 0.39 | 21.46 |

| Layout | Concurrent yards | Last standard-stock day | Curved girder pieces | Route-km on unresolved beam or crossing forms |
|---|---:|---:|---:|---:|
| Two-ring reference | 8 | 3,202 | 2,382 | 269.27 |
| Three-ring core · M3 / O4 | 8 | 2,612 | 1,528 | 26.98 |
| Three rings with suburban extensions | 8 | 2,612 | 1,528 | 28.65 |

These allowances include the counted recurring stock and curved-piece premium. New bridges, station interfaces and other held structures need separate design and prices. The model leaves the project opening date open.

## Decision checks

- **Three-ring core · M3 / O4** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.
- **Three rings with suburban extensions** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.

Reproduce with `OPENBLAS_NUM_THREADS=1 ./osr design railway baghdad-three-rings --check`.

Publication `e5161a6756229776acb5c45c3d6a8fee9d1382ee78df51a29d19937c8445f260`.
