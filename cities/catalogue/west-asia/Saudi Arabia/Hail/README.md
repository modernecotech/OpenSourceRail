# Hail — Urban Rail Network

**Country:** SA · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Hail-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.21 bn (88.3%) of external capital** and **$3.95 bn of external interest**. Capital plus saved interest totals **$7.16 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **14 lines**, including **11 additional residential lines**. **68.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **50.306 km to 78.861 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **76 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **392 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **392 light-metro-3car trainsets / 1176 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Hail rail network on OpenStreetMap](hail-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 76 / 16 |
| Route length | 110.9 km double track |
| Direct transfers / reachable line pairs | 19.8% / 100.0% |
| Residents within 800 m radial station catchments | 119,581 (2020 raster; 50.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 392 × 3-car `light-metro-3car` trainsets (348 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,874,880 passenger-trips/day |
| Annual paid-trip planning range | 342.2–547.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.5 km | 11 | 71 | S Outer ↔ N Outer |
| line-2 | 19.6 km | 17 | 70 | SW Outer ↔ NE Mid |
| line-3 | 14.5 km | 8 | 46 | N Outer ↔ E Mid |
| line-4 |  5.6 km | 4 | 19 | N Inner ↔ W Mid |
| line-5 |  2.3 km | 2 | 10 | SW Inner ↔ W Inner |
| line-6 |  8.2 km | 5 | 28 | N Mid ↔ NE Outer |
| line-7 |  3.9 km | 3 | 14 | SE Inner ↔ SE Mid |
| line-8 |  4.1 km | 3 | 16 | SW Mid ↔ SW Outer |
| line-9 |  3.4 km | 3 | 14 | E Mid ↔ NE Mid |
| line-10 |  5.3 km | 4 | 21 | E Mid ↔ SE Outer |
| line-11 | 10.0 km | 6 | 35 | SW Mid ↔ NW Mid |
| line-12 |  5.6 km | 4 | 21 | N Mid ↔ NW Mid |
| line-13 |  4.0 km | 4 | 16 | SW Outer ↔ SW Outer |
| line-14 |  2.9 km | 2 | 11 | NE Mid ↔ NE Mid |
| **Total** | **110.9 km** | **76 unique** | **392** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,510 one-way journeys / 51,547 train-km/day |
| Annual traction demand | 243.8 GWh |
| Station/depot PV / storage | 85.3 MW / 585.5 MWh |
| Aggregate charging power | 32.5 MW |
| Dedicated solar plant | 29.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-11: 6.7 km / 54 kWh |
| Lowest traversal charging margin | line-8: 12 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $905 M |
| Stations | $378 M |
| Depots | $218 M |
| Rolling stock | $353 M |
| Dedicated solar plant | $24 M |
| Residual train control | $5.5 M |
| Charging microgrids | $6.8 M |
| EPC / project services | $131 M |
| **Total city programme** | **$2.02 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $425 M (21.0%) |
| Domestic / local capital | $1.60 bn (79.0%) |
| Annual public construction commitment | $140 M / yr for 5 years |
| Annual post-grace debt service | $97 M / yr |
| External capital saved vs default turnkey sensitivity | $3.21 bn |
| Capital + lifetime external interest saved | $7.16 bn |
| Annual OPEX | $131 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 849 assets / 4,869 tasks | [`hail-operations-manifest.json`](operations/hail-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`hail.toml`](hail.toml) | Expanded simulator scenario |
| [`hail.corridor.geojson`](hail.corridor.geojson) | GIS corridor and stations |
| [`hail.design-quality.yaml`](hail.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh hail
```
