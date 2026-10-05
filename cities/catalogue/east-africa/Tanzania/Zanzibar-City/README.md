# Zanzibar-City — Urban Rail Network

**Country:** TZ · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Zanzibar-City-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.38 bn (90.5%) of external capital** and **$4.24 bn of external interest**. Capital plus saved interest totals **$7.62 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **50.072 km to 32.691 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **15 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **128 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **128 light-metro-3car trainsets / 384 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Zanzibar-City rail network on OpenStreetMap](zanzibar-city-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 2 |
| Route length | 41.0 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 222,981 (2020 raster; 27.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 128 × 3-car `light-metro-3car` trainsets (115 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.0 km | 5 | 43 | N Outer ↔ SW Mid |
| line-2 | 11.3 km | 4 | 35 | NW Mid ↔ E Mid |
| line-3 | 15.7 km | 6 | 50 | SE Outer ↔ N Mid |
| **Total** | **41.0 km** | **15 unique** | **128** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 19,081 train-km/day |
| Annual traction demand | 90.3 GWh |
| Station/depot PV / storage | 18.0 MW / 125.0 MWh |
| Aggregate charging power | 6.5 MW |
| Dedicated solar plant | 38.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 11.4 km / 85 kWh |
| Lowest traversal charging margin | line-2: 38 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.67 bn |
| Stations | $68 M |
| Depots | $53 M |
| Rolling stock | $115 M |
| Dedicated solar plant | $31 M |
| Residual train control | $2.1 M |
| Charging microgrids | $1.4 M |
| EPC / project services | $134 M |
| **Total city programme** | **$2.07 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $353 M (17.0%) |
| Domestic / local capital | $1.72 bn (83.0%) |
| Annual public construction commitment | $196 M / yr for 7 years |
| Annual post-grace debt service | $158 M / yr |
| External capital saved vs default turnkey sensitivity | $3.38 bn |
| Capital + lifetime external interest saved | $7.62 bn |
| Annual OPEX | $43 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 228 assets / 1,425 tasks | [`zanzibar-city-operations-manifest.json`](operations/zanzibar-city-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`zanzibar-city.toml`](zanzibar-city.toml) | Expanded simulator scenario |
| [`zanzibar-city.corridor.geojson`](zanzibar-city.corridor.geojson) | GIS corridor and stations |
| [`zanzibar-city.design-quality.yaml`](zanzibar-city.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh zanzibar-city
```
