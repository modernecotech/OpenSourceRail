# Mandalay — Urban Rail Network

**Country:** MM · **Population:** 1,726,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mandalay-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.50 bn (88.8%) of external capital** and **$12.27 bn of external interest**. Capital plus saved interest totals **$21.77 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **20 lines**, including **14 additional residential lines**. **81.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **153.094 km to 211.132 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **223 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**20 line-local depots** provide **612 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **612 metro-4car trainsets / 2448 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mandalay rail network on OpenStreetMap](mandalay-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 20 / 223 / 50 |
| Route length | 334.8 km double track |
| Direct transfers / reachable line pairs | 26.3% / 100.0% |
| Residents within 800 m radial station catchments | 1,135,437 (2020 raster; 65.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 612 × 4-car `metro-4car` trainsets (547 peak revenue) |
| Peak network throughput | 384,000 passengers/hour |
| Practical service capacity | 3,481,920 passenger-trips/day |
| Annual paid-trip planning range | 635.5–1016.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.3 km | 23 | 76 | N Outer ↔ S Mid |
| line-2 | 30.8 km | 20 | 68 | NW Mid ↔ SE Outer |
| line-3 | 33.8 km | 21 | 68 | SW Outer ↔ NE Mid |
| line-4 | 21.8 km | 15 | 47 | NW Inner ↔ NE Outer |
| line-5 | 23.4 km | 14 | 50 | E Mid ↔ SW Mid |
| line-6 | 84.9 km | 51 | 42 | NW Mid ↔ NW Mid |
| line-7 |  7.0 km | 5 | 18 | NE Inner ↔ E Inner |
| line-8 |  4.9 km | 4 | 14 | SE Inner ↔ SE Mid |
| line-9 |  5.1 km | 6 | 17 | SW Mid ↔ SW Mid |
| line-10 |  8.0 km | 6 | 21 | N Inner ↔ W Inner |
| line-11 | 10.6 km | 7 | 24 | SE Inner ↔ S Mid |
| line-12 |  6.7 km | 6 | 19 | S Mid ↔ SW Mid |
| line-13 | 12.1 km | 9 | 29 | SE Mid ↔ NE Inner |
| line-14 |  9.1 km | 6 | 20 | SW Outer ↔ W Mid |
| line-15 |  5.4 km | 4 | 14 | SE Mid ↔ S Mid |
| line-16 |  9.2 km | 6 | 20 | S Mid ↔ SW Mid |
| line-17 |  4.8 km | 4 | 14 | E Mid ↔ E Mid |
| line-18 |  4.7 km | 4 | 14 | NE Mid ↔ N Mid |
| line-19 |  5.9 km | 6 | 18 | S Mid ↔ S Inner |
| line-20 |  8.5 km | 6 | 19 | NE Outer ↔ N Outer |
| **Total** | **334.8 km** | **223 unique** | **612** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 9,068 one-way journeys / 135,931 train-km/day |
| Annual traction demand | 857.3 GWh |
| Station/depot PV / storage | 145.3 MW / 1,026.5 MWh |
| Aggregate charging power | 256.5 MW |
| Dedicated solar plant | 248.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 21.7 km / 242 kWh |
| Lowest traversal charging margin | line-20: 43 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.10 bn |
| Stations | $1.17 bn |
| Depots | $348 M |
| Rolling stock | $685 M |
| Dedicated solar plant | $199 M |
| Residual train control | $17 M |
| Charging microgrids | $53 M |
| EPC / project services | $376 M |
| **Total city programme** | **$5.94 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.20 bn (20.2%) |
| Domestic / local capital | $4.74 bn (79.8%) |
| Annual public construction commitment | $642 M / yr for 10 years |
| Annual post-grace debt service | $580 M / yr |
| External capital saved vs default turnkey sensitivity | $9.50 bn |
| Capital + lifetime external interest saved | $21.77 bn |
| Annual OPEX | $138 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 31 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,806 assets / 9,344 tasks | [`mandalay-operations-manifest.json`](operations/mandalay-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mandalay.toml`](mandalay.toml) | Expanded simulator scenario |
| [`mandalay.corridor.geojson`](mandalay.corridor.geojson) | GIS corridor and stations |
| [`mandalay.design-quality.yaml`](mandalay.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mandalay
```
