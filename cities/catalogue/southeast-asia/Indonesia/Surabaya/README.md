# Surabaya — Urban Rail Network

**Country:** ID · **Population:** 3,009,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Surabaya-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.78 bn (87.5%) of external capital** and **$8.33 bn of external interest**. Capital plus saved interest totals **$15.11 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **234.615 km to 183.823 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **85 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **391 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **391 metro-6car trainsets / 2346 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Surabaya rail network on OpenStreetMap](surabaya-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 85 / 15 |
| Route length | 247.3 km double track |
| Coverage / transfer reachability | 50.5% / 61% |
| Estimated station catchment | 1,519,545 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 391 × 6-car `metro-6car` trainsets (352 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.6 km | 11 | 52 | N Outer ↔ SE Mid |
| line-2 | 29.4 km | 10 | 54 | NE Outer ↔ S Mid |
| line-3 | 30.0 km | 8 | 54 | NE Mid ↔ SW Outer |
| line-4 | 23.2 km | 8 | 45 | N Mid ↔ S Outer |
| line-5 | 29.6 km | 8 | 54 | E Mid ↔ NW Outer |
| line-6 | 19.7 km | 8 | 39 | SW Mid ↔ E Mid |
| line-7 | 19.4 km | 7 | 38 | NW Outer ↔ E Mid |
| line-8 | 17.6 km | 6 | 31 | E Inner ↔ W Mid |
| line-9 | 50.8 km | 19 | 24 | W Mid ↔ W Mid |
| **Total** | **247.3 km** | **85 unique** | **391** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 103,170 train-km/day |
| Annual traction demand | 976.1 GWh |
| Station/depot PV / storage | 65.4 MW / 496.0 MWh |
| Aggregate charging power | 154.0 MW |
| Dedicated solar plant | 565.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 14.0 km / 209 kWh |
| Lowest traversal charging margin | line-8: 168 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.26 bn |
| Stations | $424 M |
| Depots | $209 M |
| Rolling stock | $657 M |
| Dedicated solar plant | $452 M |
| Residual train control | $12 M |
| Charging microgrids | $31 M |
| EPC / project services | $252 M |
| **Total city programme** | **$4.30 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $966 M (22.5%) |
| Domestic / local capital | $3.33 bn (77.5%) |
| Annual public construction commitment | $356 M / yr for 5 years |
| Annual post-grace debt service | $255 M / yr |
| External capital saved vs default turnkey sensitivity | $6.78 bn |
| Capital + lifetime external interest saved | $15.11 bn |
| Annual OPEX | $110 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 24 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 884 assets / 5,047 tasks | [`surabaya-operations-manifest.json`](operations/surabaya-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`surabaya.toml`](surabaya.toml) | Expanded simulator scenario |
| [`surabaya.corridor.geojson`](surabaya.corridor.geojson) | GIS corridor and stations |
| [`surabaya.design-quality.yaml`](surabaya.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh surabaya
```
