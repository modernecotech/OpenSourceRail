# Lyon — Urban Rail Network

**Country:** FR · **Population:** 1,436,354

This page contains only Lyon-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!NOTE]
> **Technical comparison only.** This model is retained for regression and engineering inspection.
> It is excluded from the developing-world programme, portfolio, national briefs, reader-book city evidence, and public examples.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **33 lines**, including **27 additional residential lines**. **79.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **199.785 km to 326.020 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **327 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**33 line-local depots** provide **945 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **945 metro-4car trainsets / 3780 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Lyon rail network on OpenStreetMap](lyon-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 33 / 327 / 79 |
| Route length | 414.0 km double track |
| Direct transfers / reachable line pairs | 17.6% / 100.0% |
| Residents within 800 m radial station catchments | 994,388 (2020 raster; 63.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 945 × 4-car `metro-4car` trainsets (840 peak revenue) |
| Peak network throughput | 633,600 passengers/hour |
| Practical service capacity | 5,803,200 passenger-trips/day |
| Annual paid-trip planning range | 1059.1–1694.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 42.9 km | 26 | 84 | SE Outer ↔ NW Outer |
| line-2 | 36.9 km | 25 | 81 | SW Outer ↔ E Outer |
| line-3 | 20.5 km | 18 | 58 | NE Mid ↔ W Mid |
| line-4 | 39.8 km | 28 | 86 | S Outer ↔ N Outer |
| line-5 | 26.0 km | 16 | 53 | W Outer ↔ SE Mid |
| line-6 | 62.2 km | 44 | 37 | NW Mid ↔ W Mid |
| line-7 |  6.1 km | 6 | 19 | N Inner ↔ S Inner |
| line-8 |  6.0 km | 3 | 13 | NE Inner ↔ NE Inner |
| line-9 |  5.4 km | 4 | 15 | SE Inner ↔ E Mid |
| line-10 | 13.5 km | 16 | 48 | S Inner ↔ NW Inner |
| line-11 |  5.9 km | 5 | 17 | N Inner ↔ N Inner |
| line-12 |  5.7 km | 10 | 28 | W Inner ↔ SW Inner |
| line-13 |  5.0 km | 5 | 16 | E Mid ↔ E Mid |
| line-14 |  7.3 km | 8 | 24 | N Mid ↔ N Outer |
| line-15 |  8.0 km | 5 | 18 | SE Mid ↔ SE Inner |
| line-16 |  5.0 km | 4 | 14 | SW Mid ↔ SW Mid |
| line-17 | 12.8 km | 10 | 34 | N Mid ↔ E Mid |
| line-18 |  5.4 km | 7 | 21 | S Inner ↔ S Inner |
| line-19 |  6.9 km | 7 | 23 | W Inner ↔ N Inner |
| line-20 |  7.0 km | 5 | 16 | SE Mid ↔ SE Mid |
| line-21 |  5.5 km | 4 | 13 | W Mid ↔ W Outer |
| line-22 |  5.6 km | 6 | 19 | NW Mid ↔ W Inner |
| line-23 |  4.6 km | 4 | 14 | N Mid ↔ N Inner |
| line-24 |  7.6 km | 6 | 20 | S Mid ↔ SW Inner |
| line-25 |  5.5 km | 4 | 13 | E Mid ↔ E Mid |
| line-26 |  8.7 km | 7 | 20 | NE Mid ↔ NE Mid |
| line-27 |  6.1 km | 4 | 15 | W Inner ↔ S Inner |
| line-28 |  6.7 km | 10 | 29 | SE Inner ↔ W Inner |
| line-29 |  8.7 km | 8 | 24 | N Mid ↔ N Outer |
| line-30 |  7.8 km | 7 | 23 | S Mid ↔ S Mid |
| line-31 |  6.0 km | 4 | 13 | E Mid ↔ SE Mid |
| line-32 |  5.2 km | 4 | 14 | SW Mid ↔ SW Mid |
| line-33 |  7.6 km | 7 | 23 | NW Mid ↔ NW Inner |
| **Total** | **414.0 km** | **327 unique** | **945** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 15,112 one-way journeys / 178,032 train-km/day |
| Annual traction demand | 1,122.9 GWh |
| Station/depot PV / storage | 238.8 MW / 1,689.0 MWh |
| Aggregate charging power | 418.5 MW |
| Dedicated solar plant | 567.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.8 km / 104 kWh |
| Lowest traversal charging margin | line-20: 73 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.71 bn |
| Stations | $1.92 bn |
| Depots | $565 M |
| Rolling stock | $1.06 bn |
| Dedicated solar plant | $454 M |
| Residual train control | $21 M |
| Charging microgrids | $85 M |
| EPC / project services | $515 M |
| **Total city programme** | **$8.33 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.78 bn (21.4%) |
| Domestic / local capital | $6.55 bn (78.6%) |
| Annual public construction commitment | $674 M / yr for 3 years |
| Annual post-grace debt service | $336 M / yr |
| External capital saved vs default turnkey sensitivity | $13.22 bn |
| Capital + lifetime external interest saved | $29.17 bn |
| Annual OPEX | $629 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 27 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,739 assets / 14,240 tasks | [`lyon-operations-manifest.json`](operations/lyon-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lyon.toml`](lyon.toml) | Expanded simulator scenario |
| [`lyon.corridor.geojson`](lyon.corridor.geojson) | GIS corridor and stations |
| [`lyon.design-quality.yaml`](lyon.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lyon
```
