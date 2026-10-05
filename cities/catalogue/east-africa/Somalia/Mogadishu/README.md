# Mogadishu — Urban Rail Network

**Country:** SO · **Population:** 2,610,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mogadishu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.03 bn (90.0%) of external capital** and **$5.21 bn of external interest**. Capital plus saved interest totals **$9.24 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **98.589 km to 85.228 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **39 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **132 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **132 metro-4car trainsets / 528 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mogadishu rail network on OpenStreetMap](mogadishu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 39 / 6 |
| Route length | 107.1 km double track |
| Coverage / transfer reachability | 63.3% / 83% |
| Estimated station catchment | 1,652,130 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 132 × 4-car `metro-4car` trainsets (118 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.7 km | 11 | 51 | E Mid ↔ W Outer |
| line-2 | 20.7 km | 9 | 38 | E Mid ↔ SW Mid |
| line-3 | 14.6 km | 6 | 26 | NW Inner ↔ SE Inner |
| line-4 | 39.1 km | 13 | 17 | N Mid ↔ N Inner |
| **Total** | **107.1 km** | **39 unique** | **132** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 40,708 train-km/day |
| Annual traction demand | 256.8 GWh |
| Station/depot PV / storage | 29.6 MW / 208.0 MWh |
| Aggregate charging power | 54.0 MW |
| Dedicated solar plant | 100.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.6 km / 114 kWh |
| Lowest traversal charging margin | line-3: 170 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.84 bn |
| Stations | $172 M |
| Depots | $73 M |
| Rolling stock | $148 M |
| Dedicated solar plant | $81 M |
| Residual train control | $5.4 M |
| Charging microgrids | $11 M |
| EPC / project services | $158 M |
| **Total city programme** | **$2.49 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $448 M (18.0%) |
| Domestic / local capital | $2.04 bn (82.0%) |
| Annual public construction commitment | $306 M / yr for 10 years |
| Annual post-grace debt service | $276 M / yr |
| External capital saved vs default turnkey sensitivity | $4.03 bn |
| Capital + lifetime external interest saved | $9.24 bn |
| Annual OPEX | $51 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 16 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 351 assets / 1,884 tasks | [`mogadishu-operations-manifest.json`](operations/mogadishu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mogadishu.toml`](mogadishu.toml) | Expanded simulator scenario |
| [`mogadishu.corridor.geojson`](mogadishu.corridor.geojson) | GIS corridor and stations |
| [`mogadishu.design-quality.yaml`](mogadishu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mogadishu
```
