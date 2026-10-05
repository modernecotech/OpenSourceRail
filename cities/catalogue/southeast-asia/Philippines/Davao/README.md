# Davao — Urban Rail Network

**Country:** PH · **Population:** 1,827,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Davao-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.75 bn (89.1%) of external capital** and **$8.30 bn of external interest**. Capital plus saved interest totals **$15.04 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **179.279 km to 149.217 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **87 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **305 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **305 metro-4car trainsets / 1220 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Davao rail network on OpenStreetMap](davao-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 87 / 12 |
| Route length | 247.7 km double track |
| Coverage / transfer reachability | 34.5% / 47% |
| Estimated station catchment | 630,315 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 305 × 4-car `metro-4car` trainsets (275 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 41.1 km | 15 | 65 | NE Outer ↔ SW Outer |
| line-2 | 35.8 km | 13 | 57 | NW Outer ↔ SE Mid |
| line-3 | 32.0 km | 12 | 53 | E Outer ↔ W Mid |
| line-4 | 30.6 km | 11 | 49 | W Mid ↔ E Outer |
| line-5 | 29.1 km | 11 | 49 | NW Outer ↔ SE Mid |
| line-6 | 79.2 km | 25 | 32 | NW Mid ↔ NW Mid |
| **Total** | **247.7 km** | **87 unique** | **305** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 96,782 train-km/day |
| Annual traction demand | 610.4 GWh |
| Station/depot PV / storage | 52.2 MW / 351.0 MWh |
| Aggregate charging power | 120.0 MW |
| Dedicated solar plant | 340.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 10.7 km / 107 kWh |
| Lowest traversal charging margin | line-2: 195 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.78 bn |
| Stations | $395 M |
| Depots | $128 M |
| Rolling stock | $342 M |
| Dedicated solar plant | $273 M |
| Residual train control | $12 M |
| Charging microgrids | $25 M |
| EPC / project services | $257 M |
| **Total city programme** | **$4.21 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $824 M (19.6%) |
| Domestic / local capital | $3.38 bn (80.4%) |
| Annual public construction commitment | $340 M / yr for 5 years |
| Annual post-grace debt service | $238 M / yr |
| External capital saved vs default turnkey sensitivity | $6.75 bn |
| Capital + lifetime external interest saved | $15.04 bn |
| Annual OPEX | $102 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 43 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 790 assets / 4,309 tasks | [`davao-operations-manifest.json`](operations/davao-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`davao.toml`](davao.toml) | Expanded simulator scenario |
| [`davao.corridor.geojson`](davao.corridor.geojson) | GIS corridor and stations |
| [`davao.design-quality.yaml`](davao.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh davao
```
