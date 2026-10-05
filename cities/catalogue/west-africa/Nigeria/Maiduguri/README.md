# Maiduguri — Urban Rail Network

**Country:** NG · **Population:** 1,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Maiduguri-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$13.41 bn (90.9%) of external capital** and **$16.81 bn of external interest**. Capital plus saved interest totals **$30.21 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **149.223 km to 142.872 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **58 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **191 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **191 metro-4car trainsets / 764 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Maiduguri rail network on OpenStreetMap](maiduguri-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 58 / 11 |
| Route length | 157.6 km double track |
| Direct transfers / reachable line pairs | 90.0% / 100.0% |
| Residents within 800 m radial station catchments | 241,355 (2020 raster; 19.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 191 × 4-car `metro-4car` trainsets (172 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 24.6 km | 9 | 41 | NW Mid ↔ SE Outer |
| line-2 | 21.6 km | 10 | 40 | W Mid ↔ E Mid |
| line-3 | 26.3 km | 10 | 43 | N Mid ↔ SW Mid |
| line-4 | 25.3 km | 9 | 42 | NW Inner ↔ SE Outer |
| line-5 | 59.8 km | 20 | 25 | W Mid ↔ W Mid |
| **Total** | **157.6 km** | **58 unique** | **191** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 59,382 train-km/day |
| Annual traction demand | 374.5 GWh |
| Station/depot PV / storage | 39.1 MW / 270.5 MWh |
| Aggregate charging power | 78.0 MW |
| Dedicated solar plant | 136.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 13.2 km / 147 kWh |
| Lowest traversal charging margin | line-4: 144 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $6.91 bn |
| Stations | $313 M |
| Depots | $94 M |
| Rolling stock | $214 M |
| Dedicated solar plant | $109 M |
| Residual train control | $7.9 M |
| Charging microgrids | $16 M |
| EPC / project services | $529 M |
| **Total city programme** | **$8.19 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.34 bn (16.3%) |
| Domestic / local capital | $6.85 bn (83.7%) |
| Annual public construction commitment | $996 M / yr for 7 years |
| Annual post-grace debt service | $830 M / yr |
| External capital saved vs default turnkey sensitivity | $13.41 bn |
| Capital + lifetime external interest saved | $30.21 bn |
| Annual OPEX | $163 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 513 assets / 2,751 tasks | [`maiduguri-operations-manifest.json`](operations/maiduguri-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`maiduguri.toml`](maiduguri.toml) | Expanded simulator scenario |
| [`maiduguri.corridor.geojson`](maiduguri.corridor.geojson) | GIS corridor and stations |
| [`maiduguri.design-quality.yaml`](maiduguri.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh maiduguri
```
