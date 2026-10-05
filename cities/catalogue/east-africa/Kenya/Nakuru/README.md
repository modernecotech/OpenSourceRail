# Nakuru — Urban Rail Network

**Country:** KE · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nakuru-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.13 bn (90.3%) of external capital** and **$3.92 bn of external interest**. Capital plus saved interest totals **$7.05 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **45.561 km to 39.557 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **17 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **152 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **152 light-metro-3car trainsets / 456 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Nakuru rail network on OpenStreetMap](nakuru-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 17 / 2 |
| Route length | 48.1 km double track |
| Coverage / transfer reachability | 30.4% / 67% |
| Estimated station catchment | 212,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 152 × 3-car `light-metro-3car` trainsets (137 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 11.5 km | 4 | 36 | NW Mid ↔ E Mid |
| line-2 | 20.4 km | 7 | 65 | NE Mid ↔ SW Outer |
| line-3 | 16.2 km | 6 | 51 | E Outer ↔ W Mid |
| **Total** | **48.1 km** | **17 unique** | **152** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 22,368 train-km/day |
| Annual traction demand | 105.8 GWh |
| Station/depot PV / storage | 18.6 MW / 132.0 MWh |
| Aggregate charging power | 15.0 MW |
| Dedicated solar plant | 29.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.0 km / 91 kWh |
| Lowest traversal charging margin | line-1: 156 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.50 bn |
| Stations | $75 M |
| Depots | $57 M |
| Rolling stock | $137 M |
| Dedicated solar plant | $24 M |
| Residual train control | $2.4 M |
| Charging microgrids | $3.3 M |
| EPC / project services | $124 M |
| **Total city programme** | **$1.92 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $334 M (17.4%) |
| Domestic / local capital | $1.59 bn (82.6%) |
| Annual public construction commitment | $207 M / yr for 7 years |
| Annual post-grace debt service | $170 M / yr |
| External capital saved vs default turnkey sensitivity | $3.13 bn |
| Capital + lifetime external interest saved | $7.05 bn |
| Annual OPEX | $42 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 265 assets / 1,680 tasks | [`nakuru-operations-manifest.json`](operations/nakuru-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nakuru.toml`](nakuru.toml) | Expanded simulator scenario |
| [`nakuru.corridor.geojson`](nakuru.corridor.geojson) | GIS corridor and stations |
| [`nakuru.design-quality.yaml`](nakuru.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nakuru
```
