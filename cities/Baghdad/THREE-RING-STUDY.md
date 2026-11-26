# Baghdad · Suburban rings and through routes

The middle ring targets neighbourhoods previously served by small standalone lines. The planning target is about 2.5 km from the outer ring, with routes adapted to the areas they serve. A direct shared ring station on each bank shortens trips across the orbital network.

**Suburban rings aligned to mapped roads** is the illustrated trial. It has **0 standalone routes up to 8 km**, **3 straight cross-Tigris services connecting the central and suburban rings**, and **95 shared station sites**. The published two-ring network has 8 short routes.

The published two-ring plan remains the planning reference while the trial’s open checks are resolved.

![Baghdad network comparison with direct ring transfers and cross-Tigris services](maps/baghdad-three-ring-comparison.png)

[Current proposal](PROPOSAL.md) · [Two-ring reference](STRAIGHT-THROUGH-NETWORK.md) · [Editable trial GIS](maps/baghdad-three-ring-trial.geojson) · [Machine results](three-ring-study.json.gz)

## Network and access

| Layout | Rings | Services | Short routes | Cross-Tigris links to inner and middle rings | Full through services | Route-km | Sites | Shared sites | Parallel pair-km |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Published two rings | 2 | 36 | 8 | 6 | 3 | 785.14 | 641 | 115 | 24.98 |
| Suburban rings, short routes removed | 3 | 29 | 0 | 2 | 0 | 833.06 | 664 | 83 | 38.56 |
| Suburban rings with consolidated stations | 3 | 29 | 0 | 4 | 1 | 833.06 | 655 | 97 | 38.56 |
| Suburban rings aligned to mapped roads | 3 | 29 | 0 | 3 | 0 | 852.16 | 666 | 95 | 35.22 |

The passenger models use **282,650 scheduled train-km/day**. All stops are served in both directions. A longer route portfolio has a longer headway at this fixed running budget. The housing model explicitly searches paths with at most two changes. The wide-district column reports what share finds a least-generalised-cost route with up to two changes.

| Layout | WorldPop walk 1.3 km | GHSL walk 1.3 km | WorldPop beyond M09 served | Housing ≤2 changes | Wide-district ≤2 changes | Mean headway |
|---|---:|---:|---:|---:|---:|---:|
| Published two rings | 76.72% | 77.37% | 61.04% | 77.63% | 57.67% | 6.00 min |
| Suburban rings, short routes removed | 75.03% | 75.90% | 62.09% | 75.89% | 50.81% | 6.37 min |
| Suburban rings with consolidated stations | 75.02% | 75.88% | 62.07% | 76.26% | 52.90% | 6.37 min |
| Suburban rings aligned to mapped roads | 75.80% | 76.76% | 62.41% | 75.69% | 52.30% | 6.51 min |

### Neighbourhoods previously served by short lines

This subset could walk to a short-line stop within 1.3 km on the published network and had no other station within the same walking distance. The final column counts residents who rely on standalone middle-ring sites in the trial. Shared stations that already exist on a long route are assigned to that route’s catchment.

| Layout | Population grid | Former short-line catchment | Still within 1.3 km | Middle-ring-only replacement | Lost access |
|---|---|---:|---:|---:|---:|
| Published two rings | worldpop-2026 | 272,311 | 272,311 | 0 | 0 |
| Published two rings | ghsl-2025 | 216,037 | 216,037 | 0 | 0 |
| Suburban rings, short routes removed | worldpop-2026 | 272,311 | 101,816 | 58,891 | 170,495 |
| Suburban rings, short routes removed | ghsl-2025 | 216,037 | 75,038 | 38,061 | 140,999 |
| Suburban rings with consolidated stations | worldpop-2026 | 272,311 | 101,816 | 58,891 | 170,495 |
| Suburban rings with consolidated stations | ghsl-2025 | 216,037 | 75,038 | 38,061 | 140,999 |
| Suburban rings aligned to mapped roads | worldpop-2026 | 272,311 | 136,990 | 89,185 | 135,321 |
| Suburban rings aligned to mapped roads | ghsl-2025 | 216,037 | 94,349 | 50,911 | 121,688 |

The map marks the largest remaining gaps in former short-line catchments on a 1 km grid. The machine results include the coordinates, metropolitan gains and losses, a 1.2 km walking sensitivity, and access to named destinations.

## Ring spacing and direct interchanges

The median distance from middle to outer ring is **2.50 km**, with the central 80% of sampled points between **1.95 and 3.21 km**. The distance can fall to zero at a mapped shared station. Both tracks retain their own alignment.

The inner ring’s close non-adjacent reaches fall from **4.60 km** to **0.00 km**. The screen compares points within 850 m of each other and at least 1.5 km apart along the ring.

| Bank | Shared station | Rings | Coordinates |
|---|---|---|---|
| Karkh | Karkh orbital interchange (X-RING-KARKH) | M15 / M09 | 44.34354° E, 33.26269° N |
| Rusafa | Rusafa orbital interchange (X-RING-RUSAFA) | M09 / M16 | 44.47371° E, 33.41199° N |

## Route withdrawal and station consolidation

The trial removes **42.42 route-km** across **8 short routes**. Of 29 former stop sites that close, 12 lack a replacement street walk within 1.3 km.

Consolidation changes 677 sites to 666 sites and 86 shared stations to 95. A shared station requires an actual mapped connection and reconciled calls. Nearby sites that cannot be combined remain visible in the GIS.

The straight trunk screen requires a Tigris crossing and a route within 1.10 times its end-to-end chord. The full through-service count additionally requires shared stations on all rings and both terminals outside the outermost ring.

- **Published two rings** qualifies M01, ST02-01, ST03-02.
- **Suburban rings aligned to mapped roads** qualifies no routes.

Mapped major-road alignment support is 95.6% on M15, 58.4% on M09, 38.1% on M16. Each proposed crossing and elevated alignment requires site design.


New trunk transfers to the rings use exact intersections on dry mapped streets. Nearby single-service calls are folded into the interchange only when their replacement walk is mapped.

- **M07 to M09** · X-M09-M07-f8f2c582.
- **G02 to M16** · X-M16-G02-c4556168.

To evaluate an edited layout, change its line geometry and ordered station IDs in the trial GeoJSON. Omit any line to withdraw it. The evaluator rebuilds transfers, service and cost for the full network.

`./osr design railway baghdad-three-rings --layout revised.geojson --output build/baghdad-layout-trial`

## Like-for-like capital and service allowances

The priced cases use the same six-minute budget offer, unit rates and curved-stock method. The six-minute costing offer sets fleet and supply quantities separately from the matched train-km passenger comparison.

| Layout | Running-track km | Fleet | Standard casting, haul and erection hours | Base installed US$bn | Annual operation US$bn | 30-year present US$bn |
|---|---:|---:|---:|---:|---:|---:|
| Published two rings | 1,568.22 | 581 | 6,259,184 | 43.12 | 1.16 | 65.94 |
| Suburban rings, short routes removed | 1,665.54 | 588 | 6,299,608 | 44.09 | 1.21 | 67.95 |
| Suburban rings with consolidated stations | 1,665.54 | 590 | 6,299,608 | 44.20 | 1.20 | 67.91 |
| Suburban rings aligned to mapped roads | 1,703.74 | 601 | 6,374,160 | 45.03 | 1.23 | 69.20 |

| Layout | Concurrent yards | Last standard-stock day | Curved girder pieces | Route-km on unresolved beam or crossing forms |
|---|---:|---:|---:|---:|
| Published two rings | 8 | 3,202 | 2,382 | 269.27 |
| Suburban rings, short routes removed | 8 | 4,712 | 4,470 | 232.09 |
| Suburban rings with consolidated stations | 8 | 4,712 | 4,418 | 232.77 |
| Suburban rings aligned to mapped roads | 8 | 4,965 | 5,522 | 244.08 |

These allowances include the counted recurring stock and curved-piece premium. New bridges, station interfaces and other held structures need separate design and prices. The model leaves the project opening date open.

## Decision checks

- **Suburban rings, short routes removed** · WorldPop walk coverage falls below the existing planning tolerance. GHSL walk coverage falls below the existing planning tolerance. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance. The layout increases sustained close parallel running.
- **Suburban rings with consolidated stations** · WorldPop walk coverage falls below the existing planning tolerance. GHSL walk coverage falls below the existing planning tolerance. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance. The layout increases sustained close parallel running.
- **Suburban rings aligned to mapped roads** · WorldPop walk coverage falls below the existing planning tolerance. GHSL walk coverage falls below the existing planning tolerance. Housing reach with up to two changes falls below the existing tolerance. At least one named central destination loses too much access. Wide outer-district journeys with up to two changes fall below the service tolerance. The layout increases sustained close parallel running.

Reproduce with `OPENBLAS_NUM_THREADS=1 ./osr design railway baghdad-three-rings --check`.

Publication `22f11656cfaf037359a5b6d817edcd2a4ff0881158d5bb287df55c552dc325ee`.
