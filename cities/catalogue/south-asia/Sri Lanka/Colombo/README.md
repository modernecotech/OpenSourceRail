# Colombo — Urban Rail Network

**Country:** LK · **Population:** 5,648,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Colombo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.30 bn (87.4%) of external capital** and **$10.40 bn of external interest**. Capital plus saved interest totals **$18.70 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **217.561 km to 191.472 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **139 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **482 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **482 metro-6car trainsets / 2892 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Colombo rail network on OpenStreetMap](colombo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 139 / 26 |
| Route length | 285.7 km double track |
| Direct transfers / reachable line pairs | 77.8% / 100.0% |
| Residents within 800 m radial station catchments | 816,224 (2020 raster; 27.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 482 × 6-car `metro-6car` trainsets (434 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 29.4 km | 12 | 54 | SW Mid ↔ NE Outer |
| line-2 | 23.1 km | 10 | 47 | NW Mid ↔ S Mid |
| line-3 | 37.5 km | 17 | 76 | N Outer ↔ SE Outer |
| line-4 | 22.8 km | 11 | 49 | NE Outer ↔ SW Mid |
| line-5 | 29.2 km | 13 | 58 | NW Mid ↔ SE Outer |
| line-6 | 27.1 km | 13 | 57 | NE Outer ↔ W Mid |
| line-7 | 25.1 km | 15 | 60 | W Mid ↔ SE Outer |
| line-8 | 20.2 km | 9 | 41 | NW Mid ↔ S Outer |
| line-9 | 71.1 km | 39 | 40 | NW Mid ↔ NW Mid |
| **Total** | **285.7 km** | **139 unique** | **482** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 116,302 train-km/day |
| Annual traction demand | 1,100.3 GWh |
| Station/depot PV / storage | 82.2 MW / 608.0 MWh |
| Aggregate charging power | 266.0 MW |
| Dedicated solar plant | 627.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 11.0 km / 164 kWh |
| Lowest traversal charging margin | line-1: 234 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.43 bn |
| Stations | $922 M |
| Depots | $229 M |
| Rolling stock | $810 M |
| Dedicated solar plant | $502 M |
| Residual train control | $14 M |
| Charging microgrids | $55 M |
| EPC / project services | $312 M |
| **Total city programme** | **$5.27 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.19 bn (22.6%) |
| Domestic / local capital | $4.08 bn (77.4%) |
| Annual public construction commitment | $611 M / yr for 7 years |
| Annual post-grace debt service | $518 M / yr |
| External capital saved vs default turnkey sensitivity | $8.30 bn |
| Capital + lifetime external interest saved | $18.70 bn |
| Annual OPEX | $130 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 23 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,261 assets / 6,860 tasks | [`colombo-operations-manifest.json`](operations/colombo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`colombo.toml`](colombo.toml) | Expanded simulator scenario |
| [`colombo.corridor.geojson`](colombo.corridor.geojson) | GIS corridor and stations |
| [`colombo.design-quality.yaml`](colombo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh colombo
```
