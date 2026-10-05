# Lusaka — Urban Rail Network

**Country:** ZM · **Population:** 3,037,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lusaka-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.66 bn (87.5%) of external capital** and **$8.35 bn of external interest**. Capital plus saved interest totals **$15.01 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **231.320 km to 202.464 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **100 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **384 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **384 metro-6car trainsets / 2304 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Lusaka rail network on OpenStreetMap](lusaka-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 100 / 19 |
| Route length | 240.8 km double track |
| Coverage / transfer reachability | 49.2% / 79% |
| Estimated station catchment | 1,494,204 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 384 × 6-car `metro-6car` trainsets (345 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.6 km | 13 | 67 | NE Outer ↔ W Mid |
| line-2 | 21.3 km | 9 | 42 | E Mid ↔ SW Mid |
| line-3 | 25.5 km | 12 | 53 | SE Outer ↔ W Mid |
| line-4 | 17.9 km | 11 | 45 | E Mid ↔ NW Mid |
| line-5 | 20.4 km | 10 | 45 | N Inner ↔ S Outer |
| line-6 | 27.7 km | 12 | 53 | NE Outer ↔ W Mid |
| line-7 | 25.2 km | 10 | 47 | N Mid ↔ SW Outer |
| line-8 | 69.2 km | 23 | 32 | N Outer ↔ N Mid |
| **Total** | **240.8 km** | **100 unique** | **384** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,488 one-way journeys / 95,868 train-km/day |
| Annual traction demand | 907.0 GWh |
| Station/depot PV / storage | 65.2 MW / 488.0 MWh |
| Aggregate charging power | 184.0 MW |
| Dedicated solar plant | 520.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 13.0 km / 195 kWh |
| Lowest traversal charging margin | line-7: 239 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.11 bn |
| Stations | $564 M |
| Depots | $195 M |
| Rolling stock | $645 M |
| Dedicated solar plant | $416 M |
| Residual train control | $12 M |
| Charging microgrids | $37 M |
| EPC / project services | $249 M |
| **Total city programme** | **$4.23 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $949 M (22.5%) |
| Domestic / local capital | $3.28 bn (77.5%) |
| Annual public construction commitment | $569 M / yr for 7 years |
| Annual post-grace debt service | $491 M / yr |
| External capital saved vs default turnkey sensitivity | $6.66 bn |
| Capital + lifetime external interest saved | $15.01 bn |
| Annual OPEX | $100 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 21 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 949 assets / 5,256 tasks | [`lusaka-operations-manifest.json`](operations/lusaka-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lusaka.toml`](lusaka.toml) | Expanded simulator scenario |
| [`lusaka.corridor.geojson`](lusaka.corridor.geojson) | GIS corridor and stations |
| [`lusaka.design-quality.yaml`](lusaka.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lusaka
```
