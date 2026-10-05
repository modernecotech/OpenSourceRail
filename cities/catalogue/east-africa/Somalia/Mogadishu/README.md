# Mogadishu — Urban Rail Network

**Country:** SO · **Population:** 2,610,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mogadishu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$35.60 bn (91.5%) of external capital** and **$45.99 bn of external interest**. Capital plus saved interest totals **$81.59 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **98.589 km to 95.990 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **45 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **139 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **139 metro-4car trainsets / 556 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Mogadishu rail network on OpenStreetMap](mogadishu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 45 / 6 |
| Route length | 114.5 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 231,271 (2020 raster; 26.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 139 × 4-car `metro-4car` trainsets (125 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.4 km | 12 | 53 | E Inner ↔ NW Outer |
| line-2 | 22.0 km | 10 | 41 | E Mid ↔ SW Mid |
| line-3 | 13.9 km | 6 | 26 | NW Inner ↔ SE Inner |
| line-4 | 45.1 km | 17 | 19 | N Mid ↔ N Inner |
| **Total** | **114.5 km** | **45 unique** | **139** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 42,756 train-km/day |
| Annual traction demand | 269.7 GWh |
| Station/depot PV / storage | 31.4 MW / 217.0 MWh |
| Aggregate charging power | 63.0 MW |
| Dedicated solar plant | 105.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 11.4 km / 122 kWh |
| Lowest traversal charging margin | line-3: 179 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $19.67 bn |
| Stations | $215 M |
| Depots | $73 M |
| Rolling stock | $156 M |
| Dedicated solar plant | $84 M |
| Residual train control | $5.7 M |
| Charging microgrids | $13 M |
| EPC / project services | $1.41 bn |
| **Total city programme** | **$21.63 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.32 bn (15.4%) |
| Domestic / local capital | $18.30 bn (84.6%) |
| Annual public construction commitment | $2.71 bn / yr for 10 years |
| Annual post-grace debt service | $2.43 bn / yr |
| External capital saved vs default turnkey sensitivity | $35.60 bn |
| Capital + lifetime external interest saved | $81.59 bn |
| Annual OPEX | $409 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 389 assets / 2,056 tasks | [`mogadishu-operations-manifest.json`](operations/mogadishu-operations-manifest.json) |

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
