# Colombo — Urban Rail Network

**Country:** LK · **Population:** 5,648,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Colombo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.27 bn (87.4%) of external capital** and **$9.12 bn of external interest**. Capital plus saved interest totals **$16.39 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **217.561 km to 171.514 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **98 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **426 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **426 metro-6car trainsets / 2556 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Colombo rail network on OpenStreetMap](colombo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 98 / 20 |
| Route length | 277.5 km double track |
| Coverage / transfer reachability | 61.0% / 39% |
| Estimated station catchment | 3,445,280 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 426 × 6-car `metro-6car` trainsets (384 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.5 km | 11 | 52 | SW Mid ↔ NE Outer |
| line-2 | 23.5 km | 9 | 45 | NW Outer ↔ S Mid |
| line-3 | 34.9 km | 11 | 65 | N Outer ↔ SE Outer |
| line-4 | 22.5 km | 9 | 43 | NE Outer ↔ SW Mid |
| line-5 | 29.2 km | 9 | 52 | W Mid ↔ SE Outer |
| line-6 | 27.4 km | 10 | 54 | NE Outer ↔ W Mid |
| line-7 | 24.6 km | 9 | 46 | W Mid ↔ SE Outer |
| line-8 | 20.4 km | 7 | 37 | NW Mid ↔ S Outer |
| line-9 | 66.4 km | 23 | 32 | NW Mid ↔ NW Mid |
| **Total** | **277.5 km** | **98 unique** | **426** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 113,595 train-km/day |
| Annual traction demand | 1,074.7 GWh |
| Station/depot PV / storage | 70.5 MW / 530.0 MWh |
| Aggregate charging power | 188.0 MW |
| Dedicated solar plant | 624.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 10.1 km / 151 kWh |
| Lowest traversal charging margin | line-8: 186 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.38 bn |
| Stations | $492 M |
| Depots | $217 M |
| Rolling stock | $716 M |
| Dedicated solar plant | $499 M |
| Residual train control | $14 M |
| Charging microgrids | $39 M |
| EPC / project services | $270 M |
| **Total city programme** | **$4.62 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.05 bn (22.7%) |
| Domestic / local capital | $3.58 bn (77.3%) |
| Annual public construction commitment | $535 M / yr for 7 years |
| Annual post-grace debt service | $454 M / yr |
| External capital saved vs default turnkey sensitivity | $7.27 bn |
| Capital + lifetime external interest saved | $16.39 bn |
| Annual OPEX | $113 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 39 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 993 assets / 5,617 tasks | [`colombo-operations-manifest.json`](operations/colombo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`colombo.toml`](colombo.toml) | Expanded simulator scenario |
| [`colombo.corridor.geojson`](colombo.corridor.geojson) | GIS corridor and stations |
| [`colombo.design-quality.yaml`](colombo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh colombo
```
