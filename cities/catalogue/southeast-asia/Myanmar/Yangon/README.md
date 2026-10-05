# Yangon — Urban Rail Network

**Country:** MM · **Population:** 5,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Yangon-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.61 bn (87.4%) of external capital** and **$12.41 bn of external interest**. Capital plus saved interest totals **$22.02 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **321.816 km to 262.402 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **117 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **580 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **580 metro-6car trainsets / 3480 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Yangon rail network on OpenStreetMap](yangon-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 117 / 15 |
| Route length | 363.1 km double track |
| Coverage / transfer reachability | 53.3% / 36% |
| Estimated station catchment | 2,771,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 580 × 6-car `metro-6car` trainsets (523 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.9 km | 11 | 65 | N Mid ↔ S Outer |
| line-2 | 30.9 km | 10 | 57 | S Outer ↔ N Mid |
| line-3 | 38.7 km | 12 | 72 | SE Outer ↔ NW Mid |
| line-4 | 47.2 km | 15 | 90 | NE Outer ↔ SW Outer |
| line-5 | 37.7 km | 13 | 71 | SE Mid ↔ NW Outer |
| line-6 | 34.5 km | 11 | 63 | SW Mid ↔ NE Outer |
| line-7 | 35.3 km | 12 | 67 | W Outer ↔ E Mid |
| line-8 | 32.6 km | 12 | 63 | NW Mid ↔ SE Outer |
| line-9 | 71.3 km | 21 | 32 | NW Mid ↔ NW Mid |
| **Total** | **363.1 km** | **117 unique** | **580** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 152,267 train-km/day |
| Annual traction demand | 1,440.6 GWh |
| Station/depot PV / storage | 73.2 MW / 548.0 MWh |
| Aggregate charging power | 206.0 MW |
| Dedicated solar plant | 861.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 14.1 km / 211 kWh |
| Lowest traversal charging margin | line-3: 244 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.31 bn |
| Stations | $469 M |
| Depots | $254 M |
| Rolling stock | $974 M |
| Dedicated solar plant | $689 M |
| Residual train control | $18 M |
| Charging microgrids | $42 M |
| EPC / project services | $354 M |
| **Total city programme** | **$6.11 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.38 bn (22.7%) |
| Domestic / local capital | $4.72 bn (77.3%) |
| Annual public construction commitment | $648 M / yr for 10 years |
| Annual post-grace debt service | $589 M / yr |
| External capital saved vs default turnkey sensitivity | $9.61 bn |
| Capital + lifetime external interest saved | $22.02 bn |
| Annual OPEX | $141 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 55 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,255 assets / 7,328 tasks | [`yangon-operations-manifest.json`](operations/yangon-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`yangon.toml`](yangon.toml) | Expanded simulator scenario |
| [`yangon.corridor.geojson`](yangon.corridor.geojson) | GIS corridor and stations |
| [`yangon.design-quality.yaml`](yangon.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh yangon
```
