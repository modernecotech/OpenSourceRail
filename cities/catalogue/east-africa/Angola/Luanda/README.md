# Luanda — Urban Rail Network

**Country:** AO · **Population:** 9,085,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Luanda-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$19.88 bn (89.4%) of external capital** and **$24.44 bn of external interest**. Capital plus saved interest totals **$44.31 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **315.474 km to 293.705 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **149 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **601 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **601 metro-6car trainsets / 3606 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Luanda rail network on OpenStreetMap](luanda-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 149 / 19 |
| Route length | 359.6 km double track |
| Direct transfers / reachable line pairs | 88.9% / 100.0% |
| Residents within 800 m radial station catchments | 4,515,060 (2020 raster; 29.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 601 × 6-car `metro-6car` trainsets (543 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 52.4 km | 19 | 98 | NE Outer ↔ SW Outer |
| line-2 | 26.8 km | 12 | 54 | W Outer ↔ N Mid |
| line-3 | 39.2 km | 14 | 74 | SW Outer ↔ NE Mid |
| line-4 | 47.0 km | 18 | 85 | NW Mid ↔ SE Outer |
| line-5 | 37.9 km | 16 | 71 | SE Outer ↔ W Mid |
| line-6 | 27.1 km | 15 | 61 | N Mid ↔ S Outer |
| line-7 | 31.7 km | 13 | 59 | E Outer ↔ NW Mid |
| line-8 | 31.7 km | 17 | 69 | NE Outer ↔ W Mid |
| line-9 | 65.8 km | 25 | 30 | NE Mid ↔ NE Mid |
| **Total** | **359.6 km** | **149 unique** | **601** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 151,923 train-km/day |
| Annual traction demand | 1,437.3 GWh |
| Station/depot PV / storage | 81.6 MW / 604.0 MWh |
| Aggregate charging power | 262.0 MW |
| Dedicated solar plant | 849.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 14.9 km / 223 kWh |
| Lowest traversal charging margin | line-7: 261 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $8.72 bn |
| Stations | $844 M |
| Depots | $262 M |
| Rolling stock | $1.01 bn |
| Dedicated solar plant | $680 M |
| Residual train control | $18 M |
| Charging microgrids | $53 M |
| EPC / project services | $763 M |
| **Total city programme** | **$12.35 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.35 bn (19.0%) |
| Domestic / local capital | $10.00 bn (81.0%) |
| Annual public construction commitment | $1.43 bn / yr for 5 years |
| Annual post-grace debt service | $1.08 bn / yr |
| External capital saved vs default turnkey sensitivity | $19.88 bn |
| Capital + lifetime external interest saved | $44.31 bn |
| Annual OPEX | $268 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 26 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,436 assets / 8,081 tasks | [`luanda-operations-manifest.json`](operations/luanda-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`luanda.toml`](luanda.toml) | Expanded simulator scenario |
| [`luanda.corridor.geojson`](luanda.corridor.geojson) | GIS corridor and stations |
| [`luanda.design-quality.yaml`](luanda.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh luanda
```
