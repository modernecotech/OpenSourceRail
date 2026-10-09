# Dodoma — Urban Rail Network

**Country:** TZ · **Population:** 800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Dodoma-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.85 bn (88.7%) of external capital** and **$3.57 bn of external interest**. Capital plus saved interest totals **$6.42 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **14 lines**, including **11 additional residential lines**. **73.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **44.390 km to 80.293 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **63 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **314 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **314 light-metro-3car trainsets / 942 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Dodoma rail network on OpenStreetMap](dodoma-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 63 / 14 |
| Route length | 88.2 km double track |
| Direct transfers / reachable line pairs | 18.7% / 100.0% |
| Residents within 800 m radial station catchments | 176,139 (2020 raster; 57.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 314 × 3-car `light-metro-3car` trainsets (275 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,874,880 passenger-trips/day |
| Annual paid-trip planning range | 342.2–547.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.0 km | 9 | 41 | S Mid ↔ N Mid |
| line-2 | 14.6 km | 8 | 46 | S Mid ↔ E Outer |
| line-3 | 16.5 km | 12 | 58 | NW Outer ↔ SE Mid |
| line-4 |  4.7 km | 4 | 18 | S Mid ↔ NW Inner |
| line-5 |  2.5 km | 2 | 11 | W Inner ↔ NW Inner |
| line-6 |  4.2 km | 3 | 15 | NE Inner ↔ E Mid |
| line-7 |  3.0 km | 2 | 12 | W Inner ↔ SW Inner |
| line-8 |  3.4 km | 3 | 14 | E Mid ↔ E Mid |
| line-9 |  6.4 km | 5 | 23 | S Inner ↔ SW Mid |
| line-10 |  4.2 km | 3 | 15 | N Mid ↔ NE Inner |
| line-11 |  6.4 km | 4 | 23 | N Inner ↔ E Mid |
| line-12 |  3.4 km | 3 | 14 | SE Mid ↔ SE Mid |
| line-13 |  3.5 km | 3 | 14 | W Mid ↔ NW Mid |
| line-14 |  2.3 km | 2 | 10 | W Mid ↔ W Mid |
| **Total** | **88.2 km** | **63 unique** | **314** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,510 one-way journeys / 40,991 train-km/day |
| Annual traction demand | 193.9 GWh |
| Station/depot PV / storage | 83.5 MW / 582.5 MWh |
| Aggregate charging power | 29.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 6.2 km / 52 kWh |
| Lowest traversal charging margin | line-13: 17 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $848 M |
| Stations | $320 M |
| Depots | $207 M |
| Rolling stock | $283 M |
| Residual train control | $4.4 M |
| Charging microgrids | $6.0 M |
| EPC / project services | $117 M |
| **Total city programme** | **$1.79 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $364 M (20.4%) |
| Domestic / local capital | $1.42 bn (79.6%) |
| Annual public construction commitment | $165 M / yr for 7 years |
| Annual post-grace debt service | $135 M / yr |
| External capital saved vs default turnkey sensitivity | $2.85 bn |
| Capital + lifetime external interest saved | $6.42 bn |
| Annual OPEX | $46 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 702 assets / 3,950 tasks | [`dodoma-operations-manifest.json`](operations/dodoma-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`dodoma.toml`](dodoma.toml) | Expanded simulator scenario |
| [`dodoma.corridor.geojson`](dodoma.corridor.geojson) | GIS corridor and stations |
| [`dodoma.design-quality.yaml`](dodoma.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh dodoma
```
