# Ouagadougou — Urban Rail Network

**Country:** BF · **Population:** 2,531,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ouagadougou-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.63 bn (88.9%) of external capital** and **$5.98 bn of external interest**. Capital plus saved interest totals **$10.61 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **184.546 km to 164.810 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **77 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **262 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **262 metro-4car trainsets / 1048 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Ouagadougou rail network on OpenStreetMap](ouagadougou-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 77 / 15 |
| Route length | 194.4 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | 768,010 (2020 raster; 19.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 262 × 4-car `metro-4car` trainsets (235 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.9 km | 13 | 56 | SW Mid ↔ NE Outer |
| line-2 | 19.4 km | 11 | 41 | E Mid ↔ W Mid |
| line-3 | 25.5 km | 12 | 48 | S Outer ↔ NE Mid |
| line-4 | 27.7 km | 12 | 49 | NW Outer ↔ SE Mid |
| line-5 | 27.2 km | 9 | 42 | S Mid ↔ N Outer |
| line-6 | 60.7 km | 20 | 26 | W Mid ↔ W Mid |
| **Total** | **194.4 km** | **77 unique** | **262** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 76,310 train-km/day |
| Annual traction demand | 481.3 GWh |
| Station/depot PV / storage | 49.8 MW / 339.0 MWh |
| Aggregate charging power | 108.0 MW |
| Dedicated solar plant | 176.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 14.8 km / 165 kWh |
| Lowest traversal charging margin | line-5: 157 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.71 bn |
| Stations | $413 M |
| Depots | $119 M |
| Rolling stock | $293 M |
| Dedicated solar plant | $141 M |
| Residual train control | $9.7 M |
| Charging microgrids | $22 M |
| EPC / project services | $180 M |
| **Total city programme** | **$2.89 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $576 M (19.9%) |
| Domestic / local capital | $2.32 bn (80.1%) |
| Annual public construction commitment | $248 M / yr for 10 years |
| Annual post-grace debt service | $224 M / yr |
| External capital saved vs default turnkey sensitivity | $4.63 bn |
| Capital + lifetime external interest saved | $10.61 bn |
| Annual OPEX | $64 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 693 assets / 3,744 tasks | [`ouagadougou-operations-manifest.json`](operations/ouagadougou-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ouagadougou.toml`](ouagadougou.toml) | Expanded simulator scenario |
| [`ouagadougou.corridor.geojson`](ouagadougou.corridor.geojson) | GIS corridor and stations |
| [`ouagadougou.design-quality.yaml`](ouagadougou.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh ouagadougou
```
