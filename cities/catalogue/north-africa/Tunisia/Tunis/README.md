# Tunis — Urban Rail Network

**Country:** TN · **Population:** 2,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tunis-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$16.23 bn (90.9%) of external capital** and **$19.96 bn of external interest**. Capital plus saved interest totals **$36.19 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **190.377 km to 179.240 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **70 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **246 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **246 metro-4car trainsets / 984 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tunis rail network on OpenStreetMap](tunis-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 70 / 12 |
| Route length | 201.6 km double track |
| Coverage / transfer reachability | 46.3% / 100% |
| Estimated station catchment | 1,342,700 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 246 × 4-car `metro-4car` trainsets (222 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.9 km | 15 | 61 | SE Outer ↔ W Outer |
| line-2 | 24.4 km | 10 | 42 | S Mid ↔ N Mid |
| line-3 | 39.9 km | 13 | 65 | W Outer ↔ NE Outer |
| line-4 | 28.1 km | 12 | 49 | SE Mid ↔ NW Outer |
| line-5 | 74.3 km | 20 | 29 | W Mid ↔ W Mid |
| **Total** | **201.6 km** | **70 unique** | **246** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 76,461 train-km/day |
| Annual traction demand | 482.3 GWh |
| Station/depot PV / storage | 43.0 MW / 290.0 MWh |
| Aggregate charging power | 97.5 MW |
| Dedicated solar plant | 226.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 13.8 km / 133 kWh |
| Lowest traversal charging margin | line-2: 281 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $8.36 bn |
| Stations | $331 M |
| Depots | $105 M |
| Rolling stock | $276 M |
| Dedicated solar plant | $181 M |
| Residual train control | $10 M |
| Charging microgrids | $20 M |
| EPC / project services | $637 M |
| **Total city programme** | **$9.92 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.63 bn (16.5%) |
| Domestic / local capital | $8.29 bn (83.5%) |
| Annual public construction commitment | $1.00 bn / yr for 5 years |
| Annual post-grace debt service | $721 M / yr |
| External capital saved vs default turnkey sensitivity | $16.23 bn |
| Capital + lifetime external interest saved | $36.19 bn |
| Annual OPEX | $204 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 28 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 637 assets / 3,474 tasks | [`tunis-operations-manifest.json`](operations/tunis-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tunis.toml`](tunis.toml) | Expanded simulator scenario |
| [`tunis.corridor.geojson`](tunis.corridor.geojson) | GIS corridor and stations |
| [`tunis.design-quality.yaml`](tunis.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tunis
```
