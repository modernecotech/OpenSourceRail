# Quetta — Urban Rail Network

**Country:** PK · **Population:** 1,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Quetta-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.31 bn (88.7%) of external capital** and **$6.65 bn of external interest**. Capital plus saved interest totals **$11.96 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **22 lines**, including **18 additional residential lines**. **72.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **112.474 km to 152.098 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **123 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**22 line-local depots** provide **367 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **367 metro-4car trainsets / 1468 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Quetta rail network on OpenStreetMap](quetta-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 22 / 123 / 36 |
| Route length | 173.6 km double track |
| Direct transfers / reachable line pairs | 15.6% / 100.0% |
| Residents within 800 m radial station catchments | 482,928 (2020 raster; 53.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 367 × 4-car `metro-4car` trainsets (315 peak revenue) |
| Peak network throughput | 422,400 passengers/hour |
| Practical service capacity | 3,839,040 passenger-trips/day |
| Annual paid-trip planning range | 700.6–1121.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.8 km | 13 | 47 | SW Outer ↔ N Mid |
| line-2 | 21.2 km | 14 | 46 | S Mid ↔ NE Outer |
| line-3 | 12.0 km | 7 | 26 | SW Mid ↔ N Mid |
| line-4 | 49.6 km | 28 | 26 | N Mid ↔ NW Mid |
| line-5 |  4.2 km | 3 | 12 | N Mid ↔ N Mid |
| line-6 |  4.6 km | 5 | 16 | S Mid ↔ S Mid |
| line-7 |  4.1 km | 4 | 14 | SE Mid ↔ S Inner |
| line-8 |  3.8 km | 3 | 12 | E Inner ↔ SE Inner |
| line-9 |  3.8 km | 3 | 12 | NE Mid ↔ NE Mid |
| line-10 |  2.8 km | 2 | 9 | NE Inner ↔ N Inner |
| line-11 |  6.4 km | 4 | 15 | N Mid ↔ NW Outer |
| line-12 |  2.8 km | 2 | 9 | NE Mid ↔ NE Mid |
| line-13 |  3.6 km | 3 | 11 | SW Mid ↔ S Mid |
| line-14 |  5.2 km | 4 | 13 | NW Mid ↔ NW Outer |
| line-15 |  2.3 km | 2 | 9 | E Mid ↔ NE Mid |
| line-16 |  3.9 km | 6 | 18 | S Mid ↔ S Outer |
| line-17 |  3.0 km | 4 | 13 | S Mid ↔ SW Mid |
| line-18 |  2.8 km | 2 | 9 | NW Inner ↔ N Inner |
| line-19 |  3.1 km | 3 | 11 | NW Mid ↔ N Inner |
| line-20 |  6.3 km | 6 | 18 | S Mid ↔ S Outer |
| line-21 |  4.9 km | 3 | 12 | N Mid ↔ NE Mid |
| line-22 |  2.4 km | 2 | 9 | SW Inner ↔ S Inner |
| **Total** | **173.6 km** | **123 unique** | **367** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 9,998 one-way journeys / 69,200 train-km/day |
| Annual traction demand | 436.5 GWh |
| Station/depot PV / storage | 137.3 MW / 1,016.5 MWh |
| Aggregate charging power | 169.5 MW |
| Dedicated solar plant | 63.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 6.1 km / 58 kWh |
| Lowest traversal charging margin | line-14: 92 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.60 bn |
| Stations | $672 M |
| Depots | $326 M |
| Rolling stock | $411 M |
| Dedicated solar plant | $51 M |
| Residual train control | $8.7 M |
| Charging microgrids | $34 M |
| EPC / project services | $214 M |
| **Total city programme** | **$3.32 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $674 M (20.3%) |
| Domestic / local capital | $2.65 bn (79.7%) |
| Annual public construction commitment | $455 M / yr for 7 years |
| Annual post-grace debt service | $391 M / yr |
| External capital saved vs default turnkey sensitivity | $5.31 bn |
| Capital + lifetime external interest saved | $11.96 bn |
| Annual OPEX | $82 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,071 assets / 5,465 tasks | [`quetta-operations-manifest.json`](operations/quetta-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`quetta.toml`](quetta.toml) | Expanded simulator scenario |
| [`quetta.corridor.geojson`](quetta.corridor.geojson) | GIS corridor and stations |
| [`quetta.design-quality.yaml`](quetta.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh quetta
```
