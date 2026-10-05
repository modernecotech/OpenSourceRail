# Coimbatore — Urban Rail Network

**Country:** IN · **Population:** 3,084,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Coimbatore-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.84 bn (87.6%) of external capital** and **$10.87 bn of external interest**. Capital plus saved interest totals **$19.71 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **252.240 km to 221.271 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **134 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **499 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **499 metro-6car trainsets / 2994 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Coimbatore rail network on OpenStreetMap](coimbatore-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 134 / 25 |
| Route length | 300.5 km double track |
| Coverage / transfer reachability | 58.2% / 83% |
| Estimated station catchment | 1,794,887 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 499 × 6-car `metro-6car` trainsets (449 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 42.9 km | 16 | 81 | SW Outer ↔ NE Outer |
| line-2 | 23.2 km | 10 | 47 | E Mid ↔ W Mid |
| line-3 | 26.5 km | 12 | 52 | N Outer ↔ SW Mid |
| line-4 | 29.5 km | 12 | 54 | S Mid ↔ NE Outer |
| line-5 | 26.3 km | 11 | 51 | NW Mid ↔ E Outer |
| line-6 | 32.4 km | 14 | 62 | S Outer ↔ NW Mid |
| line-7 | 20.8 km | 12 | 48 | W Outer ↔ SE Inner |
| line-8 | 26.5 km | 17 | 67 | S Mid ↔ N Outer |
| line-9 | 72.3 km | 30 | 37 | W Mid ↔ W Mid |
| **Total** | **300.5 km** | **134 unique** | **499** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 122,912 train-km/day |
| Annual traction demand | 1,162.8 GWh |
| Station/depot PV / storage | 77.1 MW / 574.0 MWh |
| Aggregate charging power | 232.0 MW |
| Dedicated solar plant | 674.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 18.2 km / 273 kWh |
| Lowest traversal charging margin | line-4: 232 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.74 bn |
| Stations | $857 M |
| Depots | $237 M |
| Rolling stock | $838 M |
| Dedicated solar plant | $540 M |
| Residual train control | $15 M |
| Charging microgrids | $49 M |
| EPC / project services | $332 M |
| **Total city programme** | **$5.61 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.26 bn (22.4%) |
| Domestic / local capital | $4.35 bn (77.6%) |
| Annual public construction commitment | $482 M / yr for 5 years |
| Annual post-grace debt service | $347 M / yr |
| External capital saved vs default turnkey sensitivity | $8.84 bn |
| Capital + lifetime external interest saved | $19.71 bn |
| Annual OPEX | $136 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,243 assets / 6,877 tasks | [`coimbatore-operations-manifest.json`](operations/coimbatore-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`coimbatore.toml`](coimbatore.toml) | Expanded simulator scenario |
| [`coimbatore.corridor.geojson`](coimbatore.corridor.geojson) | GIS corridor and stations |
| [`coimbatore.design-quality.yaml`](coimbatore.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh coimbatore
```
