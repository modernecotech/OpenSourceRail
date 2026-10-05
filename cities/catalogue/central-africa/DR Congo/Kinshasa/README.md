# Kinshasa — Urban Rail Network

**Country:** CD · **Population:** 17,178,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kinshasa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.30 bn (87.4%) of external capital** and **$12.02 bn of external interest**. Capital plus saved interest totals **$21.32 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **323.681 km to 267.459 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **120 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **563 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **563 metro-6car trainsets / 3378 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kinshasa rail network on OpenStreetMap](kinshasa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 120 / 16 |
| Route length | 352.3 km double track |
| Coverage / transfer reachability | 41.9% / 44% |
| Estimated station catchment | 7,197,582 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 563 × 6-car `metro-6car` trainsets (507 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.4 km | 13 | 62 | NW Mid ↔ SE Mid |
| line-2 | 30.6 km | 12 | 58 | E Mid ↔ N Mid |
| line-3 | 30.5 km | 10 | 57 | SE Mid ↔ W Mid |
| line-4 | 26.9 km | 11 | 52 | S Mid ↔ N Mid |
| line-5 | 47.6 km | 15 | 91 | SW Outer ↔ E Outer |
| line-6 | 38.9 km | 13 | 75 | SE Mid ↔ NW Outer |
| line-7 | 37.3 km | 12 | 69 | NE Mid ↔ SW Outer |
| line-8 | 34.5 km | 10 | 63 | NE Mid ↔ W Outer |
| line-9 | 73.5 km | 24 | 36 | NW Mid ↔ NW Mid |
| **Total** | **352.3 km** | **120 unique** | **563** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 146,713 train-km/day |
| Annual traction demand | 1,388.0 GWh |
| Station/depot PV / storage | 74.7 MW / 558.0 MWh |
| Aggregate charging power | 216.0 MW |
| Dedicated solar plant | 825.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 21.1 km / 316 kWh |
| Lowest traversal charging margin | line-8: 216 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.12 bn |
| Stations | $531 M |
| Depots | $250 M |
| Rolling stock | $946 M |
| Dedicated solar plant | $660 M |
| Residual train control | $18 M |
| Charging microgrids | $44 M |
| EPC / project services | $344 M |
| **Total city programme** | **$5.91 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.34 bn (22.7%) |
| Domestic / local capital | $4.57 bn (77.3%) |
| Annual public construction commitment | $627 M / yr for 10 years |
| Annual post-grace debt service | $570 M / yr |
| External capital saved vs default turnkey sensitivity | $9.30 bn |
| Capital + lifetime external interest saved | $21.32 bn |
| Annual OPEX | $135 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 45 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,253 assets / 7,235 tasks | [`kinshasa-operations-manifest.json`](operations/kinshasa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kinshasa.toml`](kinshasa.toml) | Expanded simulator scenario |
| [`kinshasa.corridor.geojson`](kinshasa.corridor.geojson) | GIS corridor and stations |
| [`kinshasa.design-quality.yaml`](kinshasa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kinshasa
```
