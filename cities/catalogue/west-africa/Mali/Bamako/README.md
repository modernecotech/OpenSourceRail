# Bamako — Urban Rail Network

**Country:** ML · **Population:** 2,929,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bamako-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$11.00 bn (88.9%) of external capital** and **$14.21 bn of external interest**. Capital plus saved interest totals **$25.21 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **22 lines**, including **16 additional residential lines**. **80.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **178.463 km to 269.394 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **237 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**22 line-local depots** provide **691 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **691 metro-4car trainsets / 2764 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Bamako rail network on OpenStreetMap](bamako-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 22 / 237 / 57 |
| Route length | 331.4 km double track |
| Direct transfers / reachable line pairs | 21.6% / 100.0% |
| Residents within 800 m radial station catchments | 3,289,571 (2020 raster; 66.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 691 × 4-car `metro-4car` trainsets (616 peak revenue) |
| Peak network throughput | 422,400 passengers/hour |
| Practical service capacity | 3,839,040 passenger-trips/day |
| Annual paid-trip planning range | 700.6–1121.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 40.8 km | 25 | 83 | NW Outer ↔ SE Mid |
| line-2 | 23.8 km | 18 | 60 | SW Mid ↔ NE Mid |
| line-3 | 16.4 km | 11 | 39 | SW Mid ↔ NE Inner |
| line-4 | 56.9 km | 40 | 129 | W Mid ↔ SE Outer |
| line-5 | 19.8 km | 14 | 48 | N Inner ↔ S Mid |
| line-6 | 64.9 km | 41 | 36 | N Mid ↔ NW Mid |
| line-7 |  8.2 km | 7 | 24 | S Inner ↔ E Inner |
| line-8 |  6.1 km | 5 | 17 | NE Mid ↔ NE Mid |
| line-9 |  8.6 km | 6 | 20 | SE Inner ↔ E Mid |
| line-10 |  5.1 km | 7 | 20 | N Inner ↔ N Mid |
| line-11 |  4.8 km | 4 | 14 | W Mid ↔ NW Inner |
| line-12 |  4.9 km | 5 | 16 | S Mid ↔ S Inner |
| line-13 |  5.3 km | 4 | 13 | SE Mid ↔ SE Mid |
| line-14 |  8.5 km | 7 | 24 | S Mid ↔ SW Inner |
| line-15 |  7.3 km | 5 | 16 | NE Mid ↔ NE Mid |
| line-16 |  6.5 km | 5 | 18 | S Inner ↔ S Mid |
| line-17 |  5.5 km | 4 | 14 | SW Mid ↔ SW Mid |
| line-18 |  5.1 km | 3 | 12 | NW Mid ↔ NW Outer |
| line-19 | 10.8 km | 8 | 28 | N Inner ↔ NE Mid |
| line-20 |  7.7 km | 5 | 17 | SE Mid ↔ SE Mid |
| line-21 |  8.9 km | 9 | 28 | NE Inner ↔ N Mid |
| line-22 |  5.7 km | 4 | 15 | SW Mid ↔ SW Mid |
| **Total** | **331.4 km** | **237 unique** | **691** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 9,998 one-way journeys / 139,018 train-km/day |
| Annual traction demand | 876.8 GWh |
| Station/depot PV / storage | 167.6 MW / 1,168.0 MWh |
| Aggregate charging power | 321.0 MW |
| Dedicated solar plant | 232.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 8.8 km / 98 kWh |
| Lowest traversal charging margin | line-20: 53 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.66 bn |
| Stations | $1.34 bn |
| Depots | $388 M |
| Rolling stock | $774 M |
| Dedicated solar plant | $186 M |
| Residual train control | $17 M |
| Charging microgrids | $65 M |
| EPC / project services | $437 M |
| **Total city programme** | **$6.87 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.37 bn (19.9%) |
| Domestic / local capital | $5.50 bn (80.1%) |
| Annual public construction commitment | $590 M / yr for 10 years |
| Annual post-grace debt service | $532 M / yr |
| External capital saved vs default turnkey sensitivity | $11.00 bn |
| Capital + lifetime external interest saved | $25.21 bn |
| Annual OPEX | $156 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 40 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,000 assets / 10,429 tasks | [`bamako-operations-manifest.json`](operations/bamako-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bamako.toml`](bamako.toml) | Expanded simulator scenario |
| [`bamako.corridor.geojson`](bamako.corridor.geojson) | GIS corridor and stations |
| [`bamako.design-quality.yaml`](bamako.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bamako
```
