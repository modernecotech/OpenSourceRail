# Lusaka — Urban Rail Network

**Country:** ZM · **Population:** 3,037,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lusaka-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$13.91 bn (87.3%) of external capital** and **$17.44 bn of external interest**. Capital plus saved interest totals **$31.35 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **32 lines**, including **24 additional residential lines**. **78.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **231.320 km to 334.967 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **292 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**32 line-local depots** provide **962 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **962 metro-6car trainsets / 5772 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Lusaka rail network on OpenStreetMap](lusaka-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 32 / 292 / 87 |
| Route length | 405.8 km double track |
| Direct transfers / reachable line pairs | 18.3% / 100.0% |
| Residents within 800 m radial station catchments | 1,947,193 (2020 raster; 61.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 962 × 6-car `metro-6car` trainsets (860 peak revenue) |
| Peak network throughput | 921,600 passengers/hour |
| Practical service capacity | 8,436,960 passenger-trips/day |
| Annual paid-trip planning range | 1539.7–2463.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.6 km | 20 | 76 | NE Outer ↔ W Mid |
| line-2 | 21.3 km | 14 | 54 | E Mid ↔ SW Mid |
| line-3 | 25.5 km | 18 | 67 | SE Outer ↔ W Mid |
| line-4 | 17.9 km | 13 | 49 | E Mid ↔ NW Mid |
| line-5 | 20.4 km | 13 | 50 | N Inner ↔ S Outer |
| line-6 | 27.7 km | 20 | 71 | NE Outer ↔ W Mid |
| line-7 | 25.1 km | 18 | 63 | N Mid ↔ SW Outer |
| line-8 | 69.2 km | 50 | 45 | N Outer ↔ N Mid |
| line-9 |  5.9 km | 5 | 19 | NW Mid ↔ N Mid |
| line-10 |  6.9 km | 6 | 23 | W Mid ↔ SW Inner |
| line-11 |  5.1 km | 5 | 18 | NE Mid ↔ NE Inner |
| line-12 |  5.7 km | 4 | 16 | SE Inner ↔ SE Mid |
| line-13 |  7.2 km | 6 | 23 | N Inner ↔ NW Inner |
| line-14 |  5.0 km | 4 | 16 | SW Inner ↔ SW Inner |
| line-15 |  5.0 km | 3 | 14 | NW Mid ↔ NW Mid |
| line-16 |  5.6 km | 5 | 18 | E Mid ↔ E Mid |
| line-17 |  6.1 km | 4 | 16 | SW Mid ↔ S Outer |
| line-18 |  6.0 km | 5 | 19 | N Inner ↔ NE Mid |
| line-19 |  7.0 km | 5 | 19 | SW Mid ↔ S Outer |
| line-20 |  5.2 km | 3 | 14 | SE Mid ↔ S Mid |
| line-21 |  6.3 km | 6 | 21 | NW Mid ↔ NW Mid |
| line-22 |  6.7 km | 4 | 17 | N Inner ↔ N Mid |
| line-23 |  6.4 km | 6 | 21 | SW Mid ↔ W Mid |
| line-24 |  6.9 km | 5 | 20 | NE Mid ↔ NE Mid |
| line-25 | 16.2 km | 10 | 38 | SE Mid ↔ SW Mid |
| line-26 | 15.1 km | 11 | 42 | W Mid ↔ N Mid |
| line-27 |  8.8 km | 6 | 24 | S Mid ↔ W Inner |
| line-28 |  5.9 km | 4 | 17 | SW Mid ↔ S Outer |
| line-29 |  5.8 km | 5 | 19 | E Mid ↔ E Mid |
| line-30 |  5.2 km | 4 | 16 | S Inner ↔ SW Inner |
| line-31 |  5.3 km | 5 | 18 | E Mid ↔ E Mid |
| line-32 |  5.7 km | 5 | 19 | W Inner ↔ SW Inner |
| **Total** | **405.8 km** | **292 unique** | **962** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 14,648 one-way journeys / 172,599 train-km/day |
| Annual traction demand | 1,632.9 GWh |
| Station/depot PV / storage | 229.0 MW / 1,740.0 MWh |
| Aggregate charging power | 522.0 MW |
| Dedicated solar plant | 808.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 11.5 km / 172 kWh |
| Lowest traversal charging margin | line-17: 96 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.56 bn |
| Stations | $1.75 bn |
| Depots | $624 M |
| Rolling stock | $1.62 bn |
| Dedicated solar plant | $647 M |
| Residual train control | $20 M |
| Charging microgrids | $106 M |
| EPC / project services | $537 M |
| **Total city programme** | **$8.86 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.03 bn (22.9%) |
| Domestic / local capital | $6.83 bn (77.1%) |
| Annual public construction commitment | $1.19 bn / yr for 7 years |
| Annual post-grace debt service | $1.03 bn / yr |
| External capital saved vs default turnkey sensitivity | $13.91 bn |
| Capital + lifetime external interest saved | $31.35 bn |
| Annual OPEX | $222 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 31 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,600 assets / 13,841 tasks | [`lusaka-operations-manifest.json`](operations/lusaka-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lusaka.toml`](lusaka.toml) | Expanded simulator scenario |
| [`lusaka.corridor.geojson`](lusaka.corridor.geojson) | GIS corridor and stations |
| [`lusaka.design-quality.yaml`](lusaka.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lusaka
```
