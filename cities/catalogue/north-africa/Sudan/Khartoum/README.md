# Khartoum — Urban Rail Network

**Country:** SD · **Population:** 5,829,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Khartoum-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$39.20 bn (90.6%) of external capital** and **$50.64 bn of external interest**. Capital plus saved interest totals **$89.84 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **357.668 km to 341.554 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **160 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **598 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **598 metro-6car trainsets / 3588 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Khartoum rail network on OpenStreetMap](khartoum-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 160 / 25 |
| Route length | 382.6 km double track |
| Coverage / transfer reachability | 47.7% / 81% |
| Estimated station catchment | 2,780,433 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 598 × 6-car `metro-6car` trainsets (538 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 39.6 km | 17 | 79 | SE Mid ↔ NW Mid |
| line-2 | 29.4 km | 17 | 69 | E Mid ↔ W Mid |
| line-3 | 50.3 km | 16 | 91 | N Mid ↔ SE Outer |
| line-4 | 25.6 km | 17 | 65 | NW Mid ↔ SE Mid |
| line-5 | 34.0 km | 14 | 64 | N Mid ↔ S Mid |
| line-6 | 28.8 km | 12 | 56 | S Mid ↔ NE Mid |
| line-7 | 36.0 km | 14 | 67 | W Outer ↔ E Mid |
| line-8 | 30.2 km | 13 | 58 | SW Mid ↔ N Outer |
| line-9 | 108.7 km | 40 | 49 | NW Mid ↔ NW Mid |
| **Total** | **382.6 km** | **160 unique** | **598** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 152,633 train-km/day |
| Annual traction demand | 1,444.0 GWh |
| Station/depot PV / storage | 87.3 MW / 642.0 MWh |
| Aggregate charging power | 300.0 MW |
| Dedicated solar plant | 657.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 13.8 km / 223 kWh |
| Lowest traversal charging margin | line-8: 247 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $19.70 bn |
| Stations | $922 M |
| Depots | $258 M |
| Rolling stock | $1.00 bn |
| Dedicated solar plant | $526 M |
| Residual train control | $19 M |
| Charging microgrids | $61 M |
| EPC / project services | $1.54 bn |
| **Total city programme** | **$24.03 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.06 bn (16.9%) |
| Domestic / local capital | $19.98 bn (83.1%) |
| Annual public construction commitment | $2.98 bn / yr for 10 years |
| Annual post-grace debt service | $2.68 bn / yr |
| External capital saved vs default turnkey sensitivity | $39.20 bn |
| Capital + lifetime external interest saved | $89.84 bn |
| Annual OPEX | $476 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 41 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,495 assets / 8,283 tasks | [`khartoum-operations-manifest.json`](operations/khartoum-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`khartoum.toml`](khartoum.toml) | Expanded simulator scenario |
| [`khartoum.corridor.geojson`](khartoum.corridor.geojson) | GIS corridor and stations |
| [`khartoum.design-quality.yaml`](khartoum.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh khartoum
```
