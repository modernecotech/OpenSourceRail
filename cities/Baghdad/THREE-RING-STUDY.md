# Baghdad · Population-led rings and cross-city trunks

The central ring encloses the mapped central districts on a convex alignment. The middle and outer rings are each fitted to residential population and the mapped walking network. Their separation varies around the city. The trunk search compares direct cross-city alignments from opposite sides of the outer ring. It checks tagged bridge approaches and possible new crossings against mapped river geometry.

The two-ring reference still supplies the proposal’s budget. The three-ring comparison shows the benefits of a simpler network and the districts where its access or journeys still fall short.

![Two Baghdad networks with full-colour lines, shared stations and cross-Tigris trunks](maps/baghdad-three-ring-comparison.png)

[Current proposal](PROPOSAL.md) · [Two-ring reference](STRAIGHT-THROUGH-NETWORK.md) · [Editable trial GIS](maps/baghdad-three-ring-trial.geojson) · [Machine results](three-ring-study.json.gz)

## Network and access

| Layout | Rings | Services | Short services | Cross-city trunks | Route-km | Station sites | Shared sites | Pairs of sites within 750 m | Parallel pair-km |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Two-ring reference | 2 | 36 | 8 | 2 | 785.14 | 641 | 115 | 379 | 24.98 |
| Three rings · M1 / O4 | 3 | 11 | 0 | 8 | 362.29 | 259 | 38 | 3 | 12.35 |
| Three rings · M3 / O4 | 3 | 9 | 0 | 6 | 317.23 | 242 | 31 | 2 | 0.00 |

The passenger comparisons hold running supply at **282,650 train-km/day**. The housing test searches journeys with up to two changes. The wider metropolitan test assigns least-generalised-cost trips, then reports the share using up to two changes. Both population layers use the same retained street graph and a 1.3 km maximum walk.

| Layout | WorldPop within 1.3 km | GHSL within 1.3 km | WorldPop reached only via middle-ring sites | Housing ≤2 changes | Wider journeys ≤2 changes | Headway |
|---|---:|---:|---:|---:|---:|---:|
| Two-ring reference | 76.72% | 77.37% | 0 | 77.63% | 57.67% | 6.00 min |
| Three rings · M1 / O4 | 57.76% | 58.23% | 555,687 | 39.39% | 39.60% | 2.77 min |
| Three rings · M3 / O4 | 56.12% | 56.23% | 771,335 | 29.33% | 37.24% | 2.42 min |

A resident is counted in the middle-ring-only column if they lose their 1.3 km access when stations exclusive to that ring are removed. Shared stations stay available in this test.

### Neighbourhoods previously served only by short routes

| Layout | Population grid | Former catchment | Still within 1.3 km | Of those, served only by middle-ring sites | Lost access |
|---|---|---:|---:|---:|---:|
| Two-ring reference | worldpop-2026 | 272,311 | 272,311 | 0 | 0 |
| Two-ring reference | ghsl-2025 | 216,037 | 216,037 | 0 | 0 |
| Three rings · M1 / O4 | worldpop-2026 | 272,311 | 218,618 | 28,571 | 53,693 |
| Three rings · M1 / O4 | ghsl-2025 | 216,037 | 166,957 | 19,734 | 49,080 |
| Three rings · M3 / O4 | worldpop-2026 | 272,311 | 191,869 | 26,632 | 80,442 |
| Three rings · M3 / O4 | ghsl-2025 | 216,037 | 137,750 | 17,558 | 78,287 |

The map marks the largest areas where the trial loses existing walking access. The machine record also contains overall access gains and losses, named destinations and the 1.2 km walking sensitivity.

## Geometry and station placement

| Distance from inner alignment to next ring | 10th percentile | Median | 90th percentile |
|---|---:|---:|---:|
| Central to middle | 2.63 km | 3.60 km | 4.33 km |
| Middle to outer | 2.02 km | 3.43 km | 3.88 km |

The inner ring has **0.00 km** of close non-adjacent alignment, down from **4.60 km**. The screen counts reaches within 850 m of another point at least 1.5 km away along the ring.

Shared trunk stations provide the ring connections in the illustrated layout.

The deterministic search generated 12 nested orbital combinations and built 3 complete-layout trials. For the illustrated fit, 487 cross-city alignments passed the geometric pool screens. The planner prioritised the Airport, then added coverage while checking station separation and parallel running. The full layouts are ranked on 1.3 km walking reach across both population grids.

| Trunk | Route-km | Route ÷ chord | Shared stations on the three rings |
|---|---:|---:|---|
| T01 | 32.08 | 1.004 | M15 (2), M09 (2), M16 (2) |
| T02 | 26.48 | 1.006 | M15 (2), M09 (2), M16 (2) |
| T03 | 26.29 | 1.017 | M15 (2), M09 (2), M16 (2) |
| T04 | 26.38 | 1.018 | M15 (1), M09 (2), M16 (1) |
| T05 | 25.21 | 1.005 | M15 (1), M09 (2), M16 (2) |
| T06 | 28.32 | 1.011 | M15 (1), M09 (2), M16 (1) |
| T07 | 25.56 | 1.052 | M15 (1), M09 (1), M16 (2) |
| T08 | 24.42 | 1.015 | M15 (1), M09 (1), M16 (1) |

Trunks serve both sides of the outer ring with one Tigris crossing each. Shared station sites are retained before adding local stops. Dedicated railway bridges, grades, junctions, accessible station entrances and operating headways require site and engineering work.


To evaluate an edited layout, change its line geometry and ordered station IDs in the trial GeoJSON. Omit any line to withdraw it. The evaluator rebuilds transfers, service and cost for the full network.

`./osr design railway baghdad-three-rings --layout revised.geojson --output build/baghdad-layout-trial`

## Like-for-like capital and service allowances

The priced cases use the same six-minute budget offer, unit rates and curved-stock method. The six-minute costing offer sets fleet and supply quantities separately from the matched train-km passenger comparison.

| Layout | Running-track km | Fleet | Standard casting, haul and erection hours | Base installed US$bn | Annual operation US$bn | 30-year present US$bn |
|---|---:|---:|---:|---:|---:|---:|
| Two-ring reference | 1,568.22 | 581 | 6,259,184 | 43.12 | 1.16 | 65.94 |
| Three rings · M1 / O4 | 724.58 | 242 | 2,581,192 | 18.54 | 0.50 | 28.37 |
| Three rings · M3 / O4 | 634.46 | 216 | 2,167,192 | 16.45 | 0.45 | 25.33 |

| Layout | Concurrent yards | Last standard-stock day | Curved girder pieces | Route-km on unresolved beam or crossing forms |
|---|---:|---:|---:|---:|
| Two-ring reference | 8 | 3,202 | 2,382 | 269.27 |
| Three rings · M1 / O4 | 8 | 2,548 | 1,612 | 37.80 |
| Three rings · M3 / O4 | 8 | 2,612 | 1,618 | 34.49 |

These allowances include the counted recurring stock and curved-piece premium. New bridges, station interfaces and other held structures need separate design and prices. The model leaves the project opening date open.

## Decision checks

- **Three rings · M1 / O4** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.
- **Three rings · M3 / O4** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.

Reproduce with `OPENBLAS_NUM_THREADS=1 ./osr design railway baghdad-three-rings --check`.

Publication `c01580f48b4e01b1677c658c32a80438db85d9f014624161cdc53f3df4c6da4a`.
