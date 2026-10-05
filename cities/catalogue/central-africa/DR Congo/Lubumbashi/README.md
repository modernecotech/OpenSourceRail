# Lubumbashi — Urban Rail Network

**Country:** CD · **Population:** 2,829,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lubumbashi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.63 bn (88.8%) of external capital** and **$3.40 bn of external interest**. Capital plus saved interest totals **$6.04 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **110.198 km to 89.944 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **38 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **142 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **142 metro-4car trainsets / 568 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Lubumbashi rail network on OpenStreetMap](lubumbashi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 38 / 4 |
| Route length | 115.5 km double track |
| Coverage / transfer reachability | 39.2% / 30% |
| Estimated station catchment | 1,108,968 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 142 × 4-car `metro-4car` trainsets (127 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.8 km | 8 | 35 | NE Outer ↔ S Mid |
| line-2 | 16.9 km | 7 | 30 | W Mid ↔ E Mid |
| line-3 | 12.6 km | 4 | 20 | NE Mid ↔ W Mid |
| line-4 | 23.8 km | 8 | 39 | SE Mid ↔ N Outer |
| line-5 | 42.4 km | 11 | 18 | W Mid ↔ W Mid |
| **Total** | **115.5 km** | **38 unique** | **142** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 43,833 train-km/day |
| Annual traction demand | 276.5 GWh |
| Station/depot PV / storage | 34.0 MW / 245.0 MWh |
| Aggregate charging power | 52.5 MW |
| Dedicated solar plant | 142.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 11.2 km / 112 kWh |
| Lowest traversal charging margin | line-3: 107 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.03 bn |
| Stations | $139 M |
| Depots | $85 M |
| Rolling stock | $159 M |
| Dedicated solar plant | $114 M |
| Residual train control | $5.8 M |
| Charging microgrids | $11 M |
| EPC / project services | $100 M |
| **Total city programme** | **$1.65 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $334 M (20.2%) |
| Domestic / local capital | $1.32 bn (79.8%) |
| Annual public construction commitment | $178 M / yr for 10 years |
| Annual post-grace debt service | $161 M / yr |
| External capital saved vs default turnkey sensitivity | $2.63 bn |
| Capital + lifetime external interest saved | $6.04 bn |
| Annual OPEX | $36 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 360 assets / 1,955 tasks | [`lubumbashi-operations-manifest.json`](operations/lubumbashi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lubumbashi.toml`](lubumbashi.toml) | Expanded simulator scenario |
| [`lubumbashi.corridor.geojson`](lubumbashi.corridor.geojson) | GIS corridor and stations |
| [`lubumbashi.design-quality.yaml`](lubumbashi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lubumbashi
```
