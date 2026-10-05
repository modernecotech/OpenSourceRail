# Beirut — Urban Rail Network

**Country:** LB · **Population:** 2,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Beirut-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.74 bn (88.6%) of external capital** and **$3.47 bn of external interest**. Capital plus saved interest totals **$6.22 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **110.202 km to 82.946 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **47 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **174 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **174 metro-4car trainsets / 696 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Beirut rail network on OpenStreetMap](beirut-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 47 / 6 |
| Route length | 118.5 km double track |
| Coverage / transfer reachability | 42.8% / 53% |
| Estimated station catchment | 941,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 174 × 4-car `metro-4car` trainsets (155 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.2 km | 9 | 46 | SW Outer ↔ NE Outer |
| line-2 | 13.7 km | 7 | 28 | NW Mid ↔ S Mid |
| line-3 | 17.4 km | 8 | 32 | W Mid ↔ NE Outer |
| line-4 | 15.9 km | 7 | 29 | E Mid ↔ W Mid |
| line-5 | 15.5 km | 6 | 26 | NW Inner ↔ SE Mid |
| line-6 | 28.8 km | 10 | 13 | NE Mid ↔ NE Inner |
| **Total** | **118.5 km** | **47 unique** | **174** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 48,408 train-km/day |
| Annual traction demand | 305.3 GWh |
| Station/depot PV / storage | 41.7 MW / 298.5 MWh |
| Aggregate charging power | 67.5 MW |
| Dedicated solar plant | 126.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 9.9 km / 95 kWh |
| Lowest traversal charging margin | line-5: 131 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $976 M |
| Stations | $221 M |
| Depots | $103 M |
| Rolling stock | $195 M |
| Dedicated solar plant | $102 M |
| Residual train control | $5.9 M |
| Charging microgrids | $14 M |
| EPC / project services | $106 M |
| **Total city programme** | **$1.72 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $355 M (20.6%) |
| Domestic / local capital | $1.37 bn (79.4%) |
| Annual public construction commitment | $324 M / yr for 8 years |
| Annual post-grace debt service | $295 M / yr |
| External capital saved vs default turnkey sensitivity | $2.74 bn |
| Capital + lifetime external interest saved | $6.22 bn |
| Annual OPEX | $44 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 445 assets / 2,411 tasks | [`beirut-operations-manifest.json`](operations/beirut-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`beirut.toml`](beirut.toml) | Expanded simulator scenario |
| [`beirut.corridor.geojson`](beirut.corridor.geojson) | GIS corridor and stations |
| [`beirut.design-quality.yaml`](beirut.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh beirut
```
