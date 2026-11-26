# Baghdad · Population-led rings and cross-city trunks

The central ring encloses the mapped central districts on a convex alignment. The middle and outer rings are each fitted to residential population and the mapped walking network. Their separation varies around the city. The trunk search compares direct cross-city alignments from opposite sides of the outer ring. It checks tagged bridge approaches and possible new crossings against mapped river geometry.

The two-ring reference still supplies the proposal’s budget. The three-ring comparison shows the benefits of a simpler network and the districts where its access or journeys still fall short.

![Two Baghdad networks with full-colour lines, shared stations and cross-Tigris trunks](maps/baghdad-three-ring-comparison.png)

[Current proposal](PROPOSAL.md) · [Two-ring reference](STRAIGHT-THROUGH-NETWORK.md) · [Editable trial GIS](maps/baghdad-three-ring-trial.geojson) · [Machine results](three-ring-study.json.gz)

## Network and access

| Layout | Rings | Services | Short services | Cross-city trunks | Route-km | Station sites | Shared sites | Pairs of sites within 750 m | Parallel pair-km |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Two-ring reference | 2 | 36 | 8 | 2 | 785.14 | 641 | 115 | 379 | 24.98 |
| Three-ring core · M1 / O4 | 3 | 11 | 0 | 8 | 362.29 | 259 | 38 | 3 | 12.35 |
| Three rings with suburban extensions | 3 | 11 | 0 | 8 | 456.63 | 311 | 38 | 3 | 12.35 |

The passenger comparisons hold running supply at **282,650 train-km/day**. The housing test searches journeys with up to two changes. The wider metropolitan test assigns least-generalised-cost trips, then reports the share using up to two changes. Both population layers use the same retained street graph and a 1.3 km maximum walk.

| Layout | WorldPop within 1.3 km | GHSL within 1.3 km | WorldPop reached only via middle-ring sites | Housing ≤2 changes | Wider journeys ≤2 changes | Headway |
|---|---:|---:|---:|---:|---:|---:|
| Two-ring reference | 76.72% | 77.37% | 0 | 77.63% | 57.67% | 6.00 min |
| Three-ring core · M1 / O4 | 57.76% | 58.23% | 555,687 | 39.39% | 39.60% | 2.77 min |
| Three rings with suburban extensions | 60.03% | 61.68% | 555,687 | 40.92% | 40.90% | 3.49 min |

## Suburban extensions on the through services

The core search chose new termini within a 11 km band beyond the outer ring. It also discounted the approach score as length increased. The illustrated core's ordinary ends finished within 4.45 km of the ring, leaving much of the suburban catchment unserved.

The continuation search tests up to **20 km per trunk end**. It keeps the original stations and through services, screens new alignments for heading, water, station spacing and parallel duplication, and ranks the options by additional residents within a 1.3 km street walk on both population grids.

The resulting package extends **14 trunk ends** by **94.34 route-km** and adds **52 station sites**. It reaches **195,608 more WorldPop residents** and **253,643 more GHSL residents** than the same core. Passengers stay on the same service to cross the river and reach the rings.

The suburban shares below use the same territory outside the three-ring outer alignment for every case.

| Layout | WorldPop suburban walk reach | GHSL suburban walk reach |
|---|---:|---:|
| Two-ring reference | 53.78% | 56.02% |
| Three-ring core · M1 / O4 | 33.41% | 35.95% |
| Three rings with suburban extensions | 39.33% | 45.46% |

| Trunk | From former terminus | New terminus (nearby mapped place) | Added km | New sites | New WorldPop reach |
|---|---|---|---:|---:|---:|
| T01 | T01-S14 | T01-X2-04 (الشاعورة) | 7.54 | 4 | 35,831 |
| T05 | T05-S10 | T05-X2-07 (Nahrawan) | 15.66 | 7 | 53,608 |
| T08 | T08-S01 | T08-X1-05 (الكرامة) | 8.78 | 5 | 22,062 |
| T04 | T04-S14 | T04-X2-01 (قرية ۱ حزيران) | 2.00 | 1 | 8,905 |
| T04 | T04-S01 | T04-X1-03 (داود عيسى) | 4.31 | 3 | 10,558 |
| T06 | T06-S01 | T06-X1-10 (Hay Al-Mortada) | 18.10 | 10 | 17,153 |
| T07 | T07-S11 | T07-X2-05 (الكرامة) | 8.86 | 5 | 11,761 |
| T08 | T08-S12 | T08-X2-03 | 5.48 | 3 | 6,980 |
| T06 | T06-S15 | T06-X2-02 | 2.70 | 2 | 3,552 |
| T05 | T05-S01 | T05-X1-02 | 3.58 | 2 | 4,437 |
| T07 | T07-S01 | T07-X1-02 | 3.73 | 2 | 3,773 |
| T03 | T03-S11 | T03-X2-04 | 7.26 | 4 | 11,272 |
| T03 | T03-S01 | T03-X1-02 (As Salmaniyat) | 3.34 | 2 | 4,296 |
| T02 | T02-S10 | T02-X2-02 | 3.02 | 2 | 1,418 |

Per-extension gains are counted in selection order. The reported residents are unique across the package.


A resident is counted in the middle-ring-only column if they lose their 1.3 km access when stations exclusive to that ring are removed. Shared stations stay available in this test.

### Neighbourhoods previously served only by short routes

| Layout | Population grid | Former catchment | Still within 1.3 km | Of those, served only by middle-ring sites | Lost access |
|---|---|---:|---:|---:|---:|
| Two-ring reference | worldpop-2026 | 272,311 | 272,311 | 0 | 0 |
| Two-ring reference | ghsl-2025 | 216,037 | 216,037 | 0 | 0 |
| Three-ring core · M1 / O4 | worldpop-2026 | 272,311 | 218,618 | 28,571 | 53,693 |
| Three-ring core · M1 / O4 | ghsl-2025 | 216,037 | 166,957 | 19,734 | 49,080 |
| Three rings with suburban extensions | worldpop-2026 | 272,311 | 219,475 | 28,571 | 52,836 |
| Three rings with suburban extensions | ghsl-2025 | 216,037 | 167,252 | 19,734 | 48,785 |

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
| T01 | 39.61 | 1.027 | M15 (2), M09 (2), M16 (2) |
| T02 | 29.50 | 1.013 | M15 (2), M09 (2), M16 (2) |
| T03 | 36.89 | 1.024 | M15 (2), M09 (2), M16 (2) |
| T04 | 32.69 | 1.026 | M15 (1), M09 (2), M16 (1) |
| T05 | 44.45 | 1.020 | M15 (1), M09 (2), M16 (2) |
| T06 | 49.12 | 1.033 | M15 (1), M09 (2), M16 (1) |
| T07 | 38.15 | 1.039 | M15 (1), M09 (1), M16 (2) |
| T08 | 38.68 | 1.033 | M15 (1), M09 (1), M16 (1) |

Trunks serve both sides of the outer ring with one Tigris crossing each. Shared station sites are retained before adding local stops. Dedicated railway bridges, grades, junctions, accessible station entrances and operating headways require site and engineering work.


To evaluate an edited layout, change its line geometry and ordered station IDs in the trial GeoJSON. Omit any line to withdraw it. The evaluator rebuilds transfers, service and cost for the full network.

`./osr design railway baghdad-three-rings --layout revised.geojson --output build/baghdad-layout-trial`

## Like-for-like capital and service allowances

The priced cases use the same six-minute budget offer, unit rates and curved-stock method. The six-minute costing offer sets fleet and supply quantities separately from the matched train-km passenger comparison.

| Layout | Running-track km | Fleet | Standard casting, haul and erection hours | Base installed US$bn | Annual operation US$bn | 30-year present US$bn |
|---|---:|---:|---:|---:|---:|---:|
| Two-ring reference | 1,568.22 | 581 | 6,259,184 | 43.12 | 1.16 | 65.94 |
| Three-ring core · M1 / O4 | 724.58 | 242 | 2,581,192 | 18.54 | 0.50 | 28.37 |
| Three rings with suburban extensions | 913.27 | 293 | 3,827,328 | 22.56 | 0.61 | 34.65 |

| Layout | Concurrent yards | Last standard-stock day | Curved girder pieces | Route-km on unresolved beam or crossing forms |
|---|---:|---:|---:|---:|
| Two-ring reference | 8 | 3,202 | 2,382 | 269.27 |
| Three-ring core · M1 / O4 | 8 | 2,548 | 1,612 | 37.80 |
| Three rings with suburban extensions | 8 | 2,548 | 1,612 | 44.67 |

These allowances include the counted recurring stock and curved-piece premium. New bridges, station interfaces and other held structures need separate design and prices. The model leaves the project opening date open.

## Decision checks

- **Three-ring core · M1 / O4** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.
- **Three rings with suburban extensions** · WorldPop walk coverage is below the two-ring reference. GHSL walk coverage is below the two-ring reference. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance.

Reproduce with `OPENBLAS_NUM_THREADS=1 ./osr design railway baghdad-three-rings --check`.

Publication `506410ff16e35ca0db1f1299491e02dfdf075f034abe39ffcffde91d3951d23f`.
