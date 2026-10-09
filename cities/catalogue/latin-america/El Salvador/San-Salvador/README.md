# San-Salvador — Urban Rail Network

**Country:** SV · **Population:** 1,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only San-Salvador-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.61 bn (88.3%) of external capital** and **$11.82 bn of external interest**. Capital plus saved interest totals **$21.43 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **21 lines**, including **15 additional residential lines**. **80.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **188.033 km to 246.631 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **227 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**21 line-local depots** provide **659 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **659 metro-4car trainsets / 2636 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![San-Salvador rail network on OpenStreetMap](san-salvador-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 21 / 227 / 50 |
| Route length | 349.8 km double track |
| Direct transfers / reachable line pairs | 24.8% / 100.0% |
| Residents within 800 m radial station catchments | 1,340,870 (2020 raster; 62.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 659 × 4-car `metro-4car` trainsets (589 peak revenue) |
| Peak network throughput | 403,200 passengers/hour |
| Practical service capacity | 3,660,480 passenger-trips/day |
| Annual paid-trip planning range | 668.0–1068.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.2 km | 19 | 64 | W Outer ↔ E Mid |
| line-2 | 33.0 km | 20 | 69 | N Mid ↔ SW Outer |
| line-3 | 34.5 km | 21 | 70 | SE Outer ↔ W Mid |
| line-4 | 36.2 km | 24 | 76 | SW Mid ↔ NE Outer |
| line-5 | 29.5 km | 18 | 62 | S Mid ↔ NW Outer |
| line-6 | 74.8 km | 45 | 38 | NW Mid ↔ NW Mid |
| line-7 |  6.6 km | 7 | 23 | NE Inner ↔ NW Inner |
| line-8 |  5.0 km | 4 | 14 | E Mid ↔ SE Inner |
| line-9 |  8.4 km | 5 | 19 | N Mid ↔ N Mid |
| line-10 |  5.8 km | 4 | 15 | E Mid ↔ E Mid |
| line-11 |  5.5 km | 4 | 13 | E Mid ↔ E Outer |
| line-12 |  5.1 km | 4 | 15 | E Inner ↔ NE Inner |
| line-13 |  7.1 km | 5 | 18 | S Inner ↔ S Inner |
| line-14 |  6.1 km | 4 | 13 | SW Outer ↔ SW Outer |
| line-15 | 10.0 km | 8 | 27 | NE Inner ↔ W Inner |
| line-16 | 14.1 km | 9 | 32 | E Inner ↔ N Mid |
| line-17 |  9.1 km | 6 | 21 | W Inner ↔ SW Mid |
| line-18 |  5.8 km | 5 | 15 | N Mid ↔ NW Outer |
| line-19 | 10.1 km | 6 | 21 | N Mid ↔ NE Mid |
| line-20 |  8.1 km | 4 | 17 | SE Mid ↔ S Mid |
| line-21 |  7.6 km | 5 | 17 | SE Outer ↔ SE Outer |
| **Total** | **349.8 km** | **227 unique** | **659** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 9,532 one-way journeys / 145,244 train-km/day |
| Annual traction demand | 916.1 GWh |
| Station/depot PV / storage | 156.0 MW / 1,095.0 MWh |
| Aggregate charging power | 285.0 MW |
| Dedicated solar plant | 421.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 13.6 km / 136 kWh |
| Lowest traversal charging margin | line-21: 63 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.92 bn |
| Stations | $1.23 bn |
| Depots | $371 M |
| Rolling stock | $738 M |
| Dedicated solar plant | $338 M |
| Residual train control | $17 M |
| Charging microgrids | $59 M |
| EPC / project services | $374 M |
| **Total city programme** | **$6.05 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.28 bn (21.1%) |
| Domestic / local capital | $4.77 bn (78.9%) |
| Annual public construction commitment | $687 M / yr for 5 years |
| Annual post-grace debt service | $522 M / yr |
| External capital saved vs default turnkey sensitivity | $9.61 bn |
| Capital + lifetime external interest saved | $21.43 bn |
| Annual OPEX | $161 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 42 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,898 assets / 9,907 tasks | [`san-salvador-operations-manifest.json`](operations/san-salvador-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`san-salvador.toml`](san-salvador.toml) | Expanded simulator scenario |
| [`san-salvador.corridor.geojson`](san-salvador.corridor.geojson) | GIS corridor and stations |
| [`san-salvador.design-quality.yaml`](san-salvador.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh san-salvador
```
