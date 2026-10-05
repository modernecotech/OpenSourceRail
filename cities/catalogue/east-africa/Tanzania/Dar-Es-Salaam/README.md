# Dar-Es-Salaam — Urban Rail Network

**Country:** TZ · **Population:** 7,404,689 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Dar-Es-Salaam-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.73 bn (87.3%) of external capital** and **$12.20 bn of external interest**. Capital plus saved interest totals **$21.92 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **336.440 km to 272.905 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **113 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **601 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **601 metro-6car trainsets / 3606 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Dar-Es-Salaam rail network on OpenStreetMap](dar-es-salaam-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 113 / 14 |
| Route length | 379.3 km double track |
| Coverage / transfer reachability | 47.4% / 50% |
| Estimated station catchment | 3,509,822 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 601 × 6-car `metro-6car` trainsets (543 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 43.9 km | 13 | 82 | S Outer ↔ N Mid |
| line-2 | 49.7 km | 15 | 95 | SE Mid ↔ NW Outer |
| line-3 | 45.2 km | 13 | 85 | W Inner ↔ SE Outer |
| line-4 | 39.6 km | 11 | 71 | N Mid ↔ S Mid |
| line-5 | 27.9 km | 10 | 54 | S Mid ↔ NE Inner |
| line-6 | 31.5 km | 10 | 62 | NW Outer ↔ S Inner |
| line-7 | 28.0 km | 9 | 53 | NE Inner ↔ W Mid |
| line-8 | 32.9 km | 10 | 61 | NE Inner ↔ SW Mid |
| line-9 | 80.6 km | 22 | 38 | NW Inner ↔ W Mid |
| **Total** | **379.3 km** | **113 unique** | **601** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 157,628 train-km/day |
| Annual traction demand | 1,491.3 GWh |
| Station/depot PV / storage | 69.3 MW / 522.0 MWh |
| Aggregate charging power | 180.0 MW |
| Dedicated solar plant | 899.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 22.2 km / 333 kWh |
| Lowest traversal charging margin | line-7: 225 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.33 bn |
| Stations | $452 M |
| Depots | $262 M |
| Rolling stock | $1.01 bn |
| Dedicated solar plant | $719 M |
| Residual train control | $19 M |
| Charging microgrids | $37 M |
| EPC / project services | $358 M |
| **Total city programme** | **$6.19 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.41 bn (22.8%) |
| Domestic / local capital | $4.78 bn (77.2%) |
| Annual public construction commitment | $563 M / yr for 7 years |
| Annual post-grace debt service | $465 M / yr |
| External capital saved vs default turnkey sensitivity | $9.73 bn |
| Capital + lifetime external interest saved | $21.92 bn |
| Annual OPEX | $146 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 42 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,251 assets / 7,413 tasks | [`dar-es-salaam-operations-manifest.json`](operations/dar-es-salaam-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`dar-es-salaam.toml`](dar-es-salaam.toml) | Expanded simulator scenario |
| [`dar-es-salaam.corridor.geojson`](dar-es-salaam.corridor.geojson) | GIS corridor and stations |
| [`dar-es-salaam.design-quality.yaml`](dar-es-salaam.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh dar-es-salaam
```
