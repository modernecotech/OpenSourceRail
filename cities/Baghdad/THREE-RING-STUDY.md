# Baghdad · Three rings and through routes

Test a third orbital outside M09, longer cross-city services and the removal of short routes. All alternatives use the same GIS, demand samples and running train-km.

**Third ring with G09 extension and short lines tested** is the illustrated trial. It has **6 routes up to 8 km** and **4 qualifying through services**. The published two-ring network has 8 short routes and 3 through services under the same definition, applied to its two rings.

The combined simplification and passenger-access screen holds the tested three-ring designs.

![Baghdad network comparison with ring transfers and cross-Tigris services](maps/baghdad-three-ring-comparison.png)

[Current proposal](PROPOSAL.md) · [Published two-ring study](STRAIGHT-THROUGH-NETWORK.md) · [Three-ring trial GIS](maps/baghdad-three-ring-trial.geojson) · [Simulation and source record](three-ring-study.json.gz)

## Network and access

| Layout | Rings | Services | Short lines ≤8 km | Qualifying through lines | Route-km | Sites | Parallel pair-km |
|---|---:|---:|---:|---:|---:|---:|---:|
| Published two rings | 2 | 36 | 8 | 3 | 785.14 | 641 | 24.98 |
| Compact third ring with existing lines | 3 | 37 | 8 | 1 | 877.11 | 695 | 64.27 |
| Wider third ring with existing lines | 3 | 37 | 8 | 1 | 890.82 | 699 | 35.06 |
| Road-assisted third ring | 3 | 37 | 8 | 0 | 886.12 | 701 | 34.87 |
| Third ring with additional trunks | 3 | 37 | 8 | 3 | 882.64 | 699 | 66.32 |
| Third ring with G09 extension | 3 | 37 | 8 | 4 | 903.62 | 714 | 85.08 |
| Two rings, short lines tested | 2 | 34 | 6 | 3 | 776.08 | 637 | 24.98 |
| Compact third ring with existing lines and short lines tested | 3 | 35 | 6 | 1 | 868.06 | 691 | 64.27 |
| Third ring with additional trunks and short lines tested | 3 | 35 | 6 | 3 | 873.58 | 695 | 66.32 |
| Third ring with G09 extension and short lines tested | 3 | 35 | 6 | 4 | 894.56 | 710 | 85.08 |
| Replaced inner ring | 3 | 37 | 8 | 2 | 879.07 | 702 | 72.30 |
| 29-line portfolio, three rings | 3 | 29 | 4 | 3 | 821.23 | 659 | 69.68 |
| 29-line portfolio, rings optional | 2 | 29 | 4 | 3 | 789.82 | 651 | 66.05 |

The passenger models use **282,650 scheduled train-km/day**. All stops are served in both directions. A longer route portfolio has a longer headway at this fixed running budget. The housing model explicitly searches paths with at most two changes. The wide-district column reports what share finds a least-generalised-cost route with up to two changes.

| Layout | WorldPop walk 1.3 km | GHSL walk 1.3 km | WorldPop beyond M09 served | Housing ≤2 changes | Wide-district ≤2 changes | Mean headway |
|---|---:|---:|---:|---:|---:|---:|
| Published two rings | 76.72% | 77.37% | 61.04% | 77.63% | 57.67% | 6.00 min |
| Compact third ring with existing lines | 77.50% | 78.15% | 62.84% | 77.90% | 59.40% | 6.70 min |
| Wider third ring with existing lines | 77.69% | 78.45% | 63.30% | 78.11% | 59.22% | 6.81 min |
| Road-assisted third ring | 77.67% | 78.38% | 63.26% | 78.17% | 60.49% | 6.77 min |
| Third ring with additional trunks | 77.50% | 78.15% | 62.85% | 78.08% | 60.07% | 6.75 min |
| Third ring with G09 extension | 78.06% | 78.72% | 62.84% | 78.48% | 61.46% | 6.91 min |
| Two rings, short lines tested | 76.47% | 77.22% | 61.04% | 77.63% | 55.98% | 5.93 min |
| Compact third ring with existing lines and short lines tested | 77.24% | 78.00% | 62.84% | 77.90% | 57.87% | 6.63 min |
| Third ring with additional trunks and short lines tested | 77.25% | 78.00% | 62.85% | 78.08% | 58.34% | 6.68 min |
| Third ring with G09 extension and short lines tested | 77.81% | 78.57% | 62.84% | 78.48% | 59.96% | 6.84 min |
| Replaced inner ring | 77.90% | 78.36% | 62.84% | 78.48% | 61.92% | 6.72 min |
| 29-line portfolio, three rings | 75.99% | 76.88% | 60.07% | 77.09% | 55.72% | 6.28 min |
| 29-line portfolio, rings optional | 76.17% | 76.58% | 61.67% | 77.15% | 57.48% | 6.04 min |

| Layout | WorldPop gained access | WorldPop lost access | GHSL gained access | GHSL lost access |
|---|---:|---:|---:|---:|
| Published two rings | 0 | 0 | 0 | 0 |
| Compact third ring with existing lines | 66,647 | 0 | 57,235 | 0 |
| Wider third ring with existing lines | 82,878 | 0 | 79,370 | 0 |
| Road-assisted third ring | 81,227 | 0 | 74,297 | 0 |
| Third ring with additional trunks | 67,062 | 0 | 57,498 | 0 |
| Third ring with G09 extension | 114,926 | 0 | 99,162 | 0 |
| Two rings, short lines tested | 0 | 22,042 | 0 | 11,139 |
| Compact third ring with existing lines and short lines tested | 66,647 | 22,042 | 57,235 | 11,139 |
| Third ring with additional trunks and short lines tested | 67,062 | 22,042 | 57,498 | 11,139 |
| Third ring with G09 extension and short lines tested | 114,926 | 22,042 | 99,162 | 11,139 |
| Replaced inner ring | 121,309 | 20,359 | 105,542 | 32,732 |
| 29-line portfolio, three rings | 114,926 | 177,808 | 99,162 | 135,165 |
| 29-line portfolio, rings optional | 114,926 | 162,792 | 99,162 | 157,207 |

Both population datasets use mapped street paths from the same regional window. The machine results include the 1.2 km sensitivity, named-centre access, trip and crowding diagnostics, actual removed-stop walks and the whole-route withdrawal assessments. Walking coverage and passenger weights are planning estimates.

## Third ring geometry

The buffered M16 candidate is **91.98 km** long with a **0.60 km** minimum gap to M09, 54 station sites and 12 shared passenger sites before the through-service edits. The search tests different setbacks and curve simplifications. It checks nesting, dry shared stations, mapped road proximity and potential water crossings.

The compact candidate calls for 2 new Tigris crossings. Major-road proximity supports part of the trace (10.7% under the directional screen). Land alignment, clearances, public access, hydraulic design and construction costs need route-level development.

| Orbital trace | Nominal setback | Minimum gap | Length | Distinct transfer lines | Major-road proximity | Provisional water contacts |
|---|---:|---:|---:|---:|---:|---:|
| Compact third ring with existing lines | 0.75 km | 0.60 km | 91.98 km | 11 | 10.7% | 24 |
| Wider third ring with existing lines | 3.50 km | 3.46 km | 105.68 km | 7 | 5.6% | 43 |
| Road-assisted third ring | 1.25 km | 0.57 km | 100.98 km | 8 | 38.4% | 21 |

## Rerouting and route withdrawal

The published plan is a comparator and an alignment library. The portfolio search starts with an empty set, then chooses connected routes by measured walking coverage and useful connections. It tests a three-ring requirement and a separate run with every ring optional. Named destinations, including the Airport terminal, need a street path to the proposed service. A route may serve that need under any geometry or identifier.

To evaluate a fully edited layout, export the current or trial GeoJSON and edit its line and station features. Omit any line to withdraw it. Give a rerouted line its new WGS84 path and ordered station IDs, with an individual point for each station. The evaluator rebuilds station memberships, shared transfers and route chainage. It prices the edited network alongside the published reference.

`./osr design railway baghdad-three-rings --layout revised.geojson --output build/baghdad-layout-trial`

A qualifying through route starts and ends beyond the outermost ring, crosses the mapped Tigris centreline, has actual shared passenger stations where it crosses all its rings and stays within 1.10 times its end-to-end chord. A qualifying crossing uses a shared platform site. Added routes use the existing bridge-approach and water screen.

- **Published two rings** qualifies M01, ST02-01, ST03-02 under the full through-route definition.
- **Third ring with G09 extension and short lines tested** qualifies G09, M01, ST02-01, ST03-02 under the full through-route definition.

| Withdrawal trial | Removed routes | Station sites taken out of service |
|---|---|---:|
| Two rings, short lines tested | T13, D-1033-929-34 | 4 |
| Compact third ring with existing lines and short lines tested | T13, D-1033-929-34 | 4 |
| Third ring with additional trunks and short lines tested | T13, D-1033-929-34 | 4 |
| Third ring with G09 extension and short lines tested | T13, D-1033-929-34 | 4 |

**29-line portfolio, three rings** omits 8 published routes (C2, D-1031-924-02, D-1033-929-34, D-1034-929-80, G07, M04, ST02-01, T13).

**29-line portfolio, rings optional** omits 8 published routes (D-1033-929-34, D-1034-929-80, D-1035-927-09, G07, G11, M15, ST03-02, T13).

A short route can be withdrawn only if the passenger graph remains connected, the protected lines and calls survive and each closed station has a mapped street walk to a remaining station within 1.3 km. Gross lost access is capped at 0.5% of the study population independently in each dataset before checking passenger journeys.

## Like-for-like capital and service allowances

The priced cases use the same six-minute budget offer, unit rates and curved-stock method. The six-minute costing offer sets fleet and supply quantities separately from the matched train-km passenger comparison.

| Layout | Running-track km | Fleet | Standard casting, haul and erection hours | Base installed US$bn | Annual operation US$bn | 30-year present US$bn |
|---|---:|---:|---:|---:|---:|---:|
| Published two rings | 1,568.22 | 581 | 6,259,184 | 43.12 | 1.16 | 65.94 |
| Two rings, short lines tested | 1,550.11 | 573 | 6,192,216 | 42.57 | 1.15 | 65.19 |
| Compact third ring with existing lines | 1,752.17 | 638 | 6,617,976 | 47.49 | 1.27 | 72.60 |
| Wider third ring with existing lines | 1,779.59 | 642 | 6,671,560 | 47.98 | 1.28 | 73.35 |
| Road-assisted third ring | 1,770.18 | 643 | 6,653,224 | 47.95 | 1.28 | 73.29 |
| Replaced inner ring | 1,757.54 | 644 | 6,813,816 | 47.83 | 1.28 | 73.10 |
| 29-line portfolio, three rings | 1,640.41 | 589 | 6,229,176 | 44.09 | 1.20 | 67.71 |
| 29-line portfolio, rings optional | 1,579.04 | 572 | 6,180,712 | 42.72 | 1.17 | 65.75 |
| Third ring with G09 extension and short lines tested | 1,787.07 | 649 | 6,839,752 | 48.39 | 1.30 | 74.01 |

These allowances include the counted recurring stock and curved-piece premium. New bridges, station interfaces and other held structures need separate design and prices. The model leaves the project opening date open.

## Decision checks

- **Compact third ring with existing lines** · Short-line count did not fall. Too few near-straight Tigris through lines with shared stations on all three rings. The layout increases sustained close parallel running.
- **Wider third ring with existing lines** · Short-line count did not fall. Too few near-straight Tigris through lines with shared stations on all three rings. The layout increases sustained close parallel running.
- **Road-assisted third ring** · Short-line count did not fall. Too few near-straight Tigris through lines with shared stations on all three rings. The layout increases sustained close parallel running.
- **Third ring with additional trunks** · Short-line count did not fall. Too few near-straight Tigris through lines with shared stations on all three rings. The layout increases sustained close parallel running.
- **Third ring with G09 extension** · Short-line count did not fall. The layout increases sustained close parallel running.
- **Two rings, short lines tested** · This comparison retains two rings. Too few near-straight Tigris through lines with shared stations on all three rings. Wide outer-district journeys with up to two changes fall below the service tolerance.
- **Compact third ring with existing lines and short lines tested** · Too few near-straight Tigris through lines with shared stations on all three rings. The layout increases sustained close parallel running.
- **Third ring with additional trunks and short lines tested** · Too few near-straight Tigris through lines with shared stations on all three rings. The layout increases sustained close parallel running.
- **Third ring with G09 extension and short lines tested** · The layout increases sustained close parallel running.
- **Replaced inner ring** · Short-line count did not fall. Too few near-straight Tigris through lines with shared stations on all three rings. The layout increases sustained close parallel running.
- **29-line portfolio, three rings** · Too few near-straight Tigris through lines with shared stations on all three rings. WorldPop walk coverage falls below the existing planning tolerance. Housing reach with up to two changes falls below the existing tolerance. Wide outer-district journeys with up to two changes fall below the service tolerance. The layout increases sustained close parallel running.
- **29-line portfolio, rings optional** · This comparison retains two rings. Too few near-straight Tigris through lines with shared stations on all three rings. WorldPop walk coverage falls below the existing planning tolerance. GHSL walk coverage falls below the existing planning tolerance. The layout increases sustained close parallel running.

Reproduce with `OPENBLAS_NUM_THREADS=1 ./osr design railway baghdad-three-rings --check`.

Publication `5566b3a0065d50ea69463fc533266e06960049b22aa3b2432ab46a072580b724`.
