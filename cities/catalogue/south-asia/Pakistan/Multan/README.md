# Multan — Urban Rail Network

**Country:** PK · **Population:** 2,197,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Multan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.62 bn (89.1%) of external capital** and **$3.28 bn of external interest**. Capital plus saved interest totals **$5.90 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **107.847 km to 93.318 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **45 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **140 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **140 metro-4car trainsets / 560 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Multan rail network on OpenStreetMap](multan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 45 / 12 |
| Route length | 101.4 km double track |
| Coverage / transfer reachability | 52.6% / 90% |
| Estimated station catchment | 1,155,622 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 140 × 4-car `metro-4car` trainsets (125 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.6 km | 7 | 29 | NE Outer ↔ SW Outer |
| line-2 | 16.9 km | 9 | 35 | NE Outer ↔ SW Outer |
| line-3 | 14.6 km | 8 | 30 | S Mid ↔ N Outer |
| line-4 | 15.3 km | 7 | 29 | W Mid ↔ E Outer |
| line-5 | 39.0 km | 14 | 17 | N Outer ↔ N Mid |
| **Total** | **101.4 km** | **45 unique** | **140** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 38,096 train-km/day |
| Annual traction demand | 240.3 GWh |
| Station/depot PV / storage | 37.0 MW / 260.0 MWh |
| Aggregate charging power | 67.5 MW |
| Dedicated solar plant | 73.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 6.6 km / 73 kWh |
| Lowest traversal charging margin | line-1: 200 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $933 M |
| Stations | $278 M |
| Depots | $84 M |
| Rolling stock | $157 M |
| Dedicated solar plant | $59 M |
| Residual train control | $5.1 M |
| Charging microgrids | $14 M |
| EPC / project services | $103 M |
| **Total city programme** | **$1.63 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $322 M (19.7%) |
| Domestic / local capital | $1.31 bn (80.3%) |
| Annual public construction commitment | $225 M / yr for 7 years |
| Annual post-grace debt service | $193 M / yr |
| External capital saved vs default turnkey sensitivity | $2.62 bn |
| Capital + lifetime external interest saved | $5.90 bn |
| Annual OPEX | $38 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 395 assets / 2,074 tasks | [`multan-operations-manifest.json`](operations/multan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`multan.toml`](multan.toml) | Expanded simulator scenario |
| [`multan.corridor.geojson`](multan.corridor.geojson) | GIS corridor and stations |
| [`multan.design-quality.yaml`](multan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh multan
```
