# Khulna — Urban Rail Network

**Country:** BD · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Khulna-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.70 bn (89.1%) of external capital** and **$5.89 bn of external interest**. Capital plus saved interest totals **$10.59 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **163.275 km to 135.163 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **63 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **223 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **223 metro-4car trainsets / 892 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Khulna rail network on OpenStreetMap](khulna-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 63 / 9 |
| Route length | 172.5 km double track |
| Coverage / transfer reachability | 52.1% / 47% |
| Estimated station catchment | 781,500 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 223 × 4-car `metro-4car` trainsets (201 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.3 km | 13 | 52 | NW Outer ↔ S Mid |
| line-2 | 27.8 km | 8 | 43 | SW Mid ↔ NE Outer |
| line-3 | 24.1 km | 11 | 42 | SE Outer ↔ N Mid |
| line-4 | 16.4 km | 6 | 28 | NW Mid ↔ S Outer |
| line-5 | 24.1 km | 8 | 38 | SE Outer ↔ NW Mid |
| line-6 | 52.0 km | 17 | 20 | NW Mid ↔ W Mid |
| **Total** | **172.5 km** | **63 unique** | **223** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 68,145 train-km/day |
| Annual traction demand | 429.8 GWh |
| Station/depot PV / storage | 45.9 MW / 319.5 MWh |
| Aggregate charging power | 88.5 MW |
| Dedicated solar plant | 229.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.3 km / 102 kWh |
| Lowest traversal charging margin | line-2: 148 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.90 bn |
| Stations | $281 M |
| Depots | $112 M |
| Rolling stock | $250 M |
| Dedicated solar plant | $183 M |
| Residual train control | $8.6 M |
| Charging microgrids | $18 M |
| EPC / project services | $180 M |
| **Total city programme** | **$2.93 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $578 M (19.7%) |
| Domestic / local capital | $2.35 bn (80.3%) |
| Annual public construction commitment | $253 M / yr for 7 years |
| Annual post-grace debt service | $206 M / yr |
| External capital saved vs default turnkey sensitivity | $4.70 bn |
| Capital + lifetime external interest saved | $10.59 bn |
| Annual OPEX | $66 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 24 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 579 assets / 3,139 tasks | [`khulna-operations-manifest.json`](operations/khulna-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`khulna.toml`](khulna.toml) | Expanded simulator scenario |
| [`khulna.corridor.geojson`](khulna.corridor.geojson) | GIS corridor and stations |
| [`khulna.design-quality.yaml`](khulna.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh khulna
```
