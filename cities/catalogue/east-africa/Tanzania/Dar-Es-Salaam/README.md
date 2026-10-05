# Dar-Es-Salaam — Urban Rail Network

**Country:** TZ · **Population:** 7,404,689 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Dar-Es-Salaam-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$61.39 bn (90.7%) of external capital** and **$76.95 bn of external interest**. Capital plus saved interest totals **$138.34 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **336.440 km to 368.245 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **212 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **764 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **764 metro-6car trainsets / 4584 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Dar-Es-Salaam rail network on OpenStreetMap](dar-es-salaam-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 212 / 31 |
| Route length | 479.0 km double track |
| Direct transfers / reachable line pairs | 86.1% / 100.0% |
| Residents within 800 m radial station catchments | 2,205,889 (2020 raster; 32.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 764 × 6-car `metro-6car` trainsets (691 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 44.2 km | 20 | 89 | S Outer ↔ N Mid |
| line-2 | 92.3 km | 43 | 182 | SE Mid ↔ NW Outer |
| line-3 | 46.6 km | 19 | 93 | NW Inner ↔ SE Outer |
| line-4 | 38.9 km | 17 | 76 | N Mid ↔ S Mid |
| line-5 | 29.1 km | 18 | 71 | S Mid ↔ NE Inner |
| line-6 | 33.7 km | 12 | 65 | NW Outer ↔ SW Inner |
| line-7 | 27.6 km | 16 | 63 | NE Inner ↔ W Mid |
| line-8 | 33.0 km | 14 | 63 | NE Inner ↔ SW Mid |
| line-9 | 133.6 km | 53 | 62 | NW Mid ↔ W Mid |
| **Total** | **479.0 km** | **212 unique** | **764** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 191,685 train-km/day |
| Annual traction demand | 1,813.5 GWh |
| Station/depot PV / storage | 99.3 MW / 722.0 MWh |
| Aggregate charging power | 380.0 MW |
| Dedicated solar plant | 1,076.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 23.8 km / 356 kWh |
| Lowest traversal charging margin | line-6: 230 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $31.32 bn |
| Stations | $1.32 bn |
| Depots | $301 M |
| Rolling stock | $1.28 bn |
| Dedicated solar plant | $861 M |
| Residual train control | $24 M |
| Charging microgrids | $77 M |
| EPC / project services | $2.40 bn |
| **Total city programme** | **$37.59 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $6.28 bn (16.7%) |
| Domestic / local capital | $31.31 bn (83.3%) |
| Annual public construction commitment | $3.56 bn / yr for 7 years |
| Annual post-grace debt service | $2.87 bn / yr |
| External capital saved vs default turnkey sensitivity | $61.39 bn |
| Capital + lifetime external interest saved | $138.34 bn |
| Annual OPEX | $742 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 30 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,934 assets / 10,690 tasks | [`dar-es-salaam-operations-manifest.json`](operations/dar-es-salaam-operations-manifest.json) |

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
