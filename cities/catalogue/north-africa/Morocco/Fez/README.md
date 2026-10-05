# Fez — Urban Rail Network

**Country:** MA · **Population:** 1,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Fez-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.39 bn (89.1%) of external capital** and **$2.93 bn of external interest**. Capital plus saved interest totals **$5.32 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **106.603 km to 87.637 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **40 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **115 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **115 metro-4car trainsets / 460 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Fez rail network on OpenStreetMap](fez-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 40 / 7 |
| Route length | 92.6 km double track |
| Direct transfers / reachable line pairs | 83.3% / 100.0% |
| Residents within 800 m radial station catchments | 428,900 (2020 raster; 30.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 115 × 4-car `metro-4car` trainsets (103 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 18.9 km | 9 | 36 | NE Mid ↔ SW Outer |
| line-2 | 15.0 km | 7 | 29 | W Outer ↔ SE Mid |
| line-3 | 17.8 km | 8 | 32 | E Outer ↔ W Mid |
| line-4 | 40.9 km | 16 | 18 | W Mid ↔ W Mid |
| **Total** | **92.6 km** | **40 unique** | **115** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 33,540 train-km/day |
| Annual traction demand | 211.5 GWh |
| Station/depot PV / storage | 30.5 MW / 212.5 MWh |
| Aggregate charging power | 58.5 MW |
| Dedicated solar plant | 86.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 7.0 km / 67 kWh |
| Lowest traversal charging margin | line-3: 204 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $888 M |
| Stations | $225 M |
| Depots | $68 M |
| Rolling stock | $129 M |
| Dedicated solar plant | $69 M |
| Residual train control | $4.6 M |
| Charging microgrids | $12 M |
| EPC / project services | $93 M |
| **Total city programme** | **$1.49 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $292 M (19.6%) |
| Domestic / local capital | $1.20 bn (80.4%) |
| Annual public construction commitment | $104 M / yr for 5 years |
| Annual post-grace debt service | $72 M / yr |
| External capital saved vs default turnkey sensitivity | $2.39 bn |
| Capital + lifetime external interest saved | $5.32 bn |
| Annual OPEX | $39 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 11 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 339 assets / 1,755 tasks | [`fez-operations-manifest.json`](operations/fez-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`fez.toml`](fez.toml) | Expanded simulator scenario |
| [`fez.corridor.geojson`](fez.corridor.geojson) | GIS corridor and stations |
| [`fez.design-quality.yaml`](fez.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh fez
```
