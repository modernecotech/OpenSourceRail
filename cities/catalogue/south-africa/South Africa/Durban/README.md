# Durban — Urban Rail Network

**Country:** ZA · **Population:** 3,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Durban-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.95 bn (87.5%) of external capital** and **$11.00 bn of external interest**. Capital plus saved interest totals **$19.95 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **306.330 km to 248.018 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **113 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **516 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **516 metro-6car trainsets / 3096 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Durban rail network on OpenStreetMap](durban-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 113 / 17 |
| Route length | 338.1 km double track |
| Coverage / transfer reachability | 73.6% / 39% |
| Estimated station catchment | 2,870,400 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 516 × 6-car `metro-6car` trainsets (465 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 48.9 km | 17 | 91 | NE Mid ↔ S Outer |
| line-2 | 35.4 km | 10 | 62 | SW Mid ↔ NE Mid |
| line-3 | 36.7 km | 12 | 67 | N Outer ↔ S Mid |
| line-4 | 20.5 km | 9 | 41 | SW Mid ↔ E Mid |
| line-5 | 33.8 km | 12 | 64 | E Mid ↔ NW Outer |
| line-6 | 28.3 km | 9 | 54 | W Mid ↔ SE Mid |
| line-7 | 28.5 km | 10 | 53 | NW Mid ↔ E Mid |
| line-8 | 24.2 km | 8 | 46 | W Mid ↔ E Inner |
| line-9 | 81.9 km | 26 | 38 | W Mid ↔ W Inner |
| **Total** | **338.1 km** | **113 unique** | **516** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 138,184 train-km/day |
| Annual traction demand | 1,307.3 GWh |
| Station/depot PV / storage | 72.3 MW / 542.0 MWh |
| Aggregate charging power | 200.0 MW |
| Dedicated solar plant | 775.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 14.7 km / 220 kWh |
| Lowest traversal charging margin | line-8: 206 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.06 bn |
| Stations | $508 M |
| Depots | $240 M |
| Rolling stock | $867 M |
| Dedicated solar plant | $620 M |
| Residual train control | $17 M |
| Charging microgrids | $41 M |
| EPC / project services | $331 M |
| **Total city programme** | **$5.68 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.28 bn (22.5%) |
| Domestic / local capital | $4.40 bn (77.5%) |
| Annual public construction commitment | $604 M / yr for 5 years |
| Annual post-grace debt service | $455 M / yr |
| External capital saved vs default turnkey sensitivity | $8.95 bn |
| Capital + lifetime external interest saved | $19.95 bn |
| Annual OPEX | $155 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 43 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,163 assets / 6,675 tasks | [`durban-operations-manifest.json`](operations/durban-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`durban.toml`](durban.toml) | Expanded simulator scenario |
| [`durban.corridor.geojson`](durban.corridor.geojson) | GIS corridor and stations |
| [`durban.design-quality.yaml`](durban.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh durban
```
