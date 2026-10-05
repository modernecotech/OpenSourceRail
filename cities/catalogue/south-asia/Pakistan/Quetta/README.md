# Quetta — Urban Rail Network

**Country:** PK · **Population:** 1,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Quetta-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.40 bn (89.3%) of external capital** and **$3.01 bn of external interest**. Capital plus saved interest totals **$5.41 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **112.474 km to 98.503 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **33 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **113 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **113 metro-4car trainsets / 452 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Quetta rail network on OpenStreetMap](quetta-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 33 / 6 |
| Route length | 103.7 km double track |
| Direct transfers / reachable line pairs | 50.0% / 100.0% |
| Residents within 800 m radial station catchments | 191,169 (2020 raster; 21.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 113 × 4-car `metro-4car` trainsets (101 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.8 km | 9 | 38 | SW Outer ↔ N Mid |
| line-2 | 21.3 km | 6 | 36 | S Mid ↔ NE Outer |
| line-3 | 12.0 km | 4 | 19 | SW Mid ↔ N Mid |
| line-4 | 49.6 km | 14 | 20 | NW Mid ↔ NW Mid |
| **Total** | **103.7 km** | **33 unique** | **113** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 36,689 train-km/day |
| Annual traction demand | 231.4 GWh |
| Station/depot PV / storage | 28.4 MW / 202.0 MWh |
| Aggregate charging power | 48.0 MW |
| Dedicated solar plant | 84.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 8.2 km / 79 kWh |
| Lowest traversal charging margin | line-3: 118 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $985 M |
| Stations | $139 M |
| Depots | $68 M |
| Rolling stock | $127 M |
| Dedicated solar plant | $68 M |
| Residual train control | $5.2 M |
| Charging microgrids | $10 M |
| EPC / project services | $93 M |
| **Total city programme** | **$1.49 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $288 M (19.3%) |
| Domestic / local capital | $1.21 bn (80.7%) |
| Annual public construction commitment | $207 M / yr for 7 years |
| Annual post-grace debt service | $177 M / yr |
| External capital saved vs default turnkey sensitivity | $2.40 bn |
| Capital + lifetime external interest saved | $5.41 bn |
| Annual OPEX | $34 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 16 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 301 assets / 1,610 tasks | [`quetta-operations-manifest.json`](operations/quetta-operations-manifest.json) |

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
