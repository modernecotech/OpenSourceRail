# Phnom-Penh — Urban Rail Network

**Country:** KH · **Population:** 2,281,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Phnom-Penh-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.66 bn (89.1%) of external capital** and **$7.09 bn of external interest**. Capital plus saved interest totals **$12.75 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **180.759 km to 147.444 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **66 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **265 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **265 metro-4car trainsets / 1060 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Phnom-Penh rail network on OpenStreetMap](phnom-penh-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 66 / 13 |
| Route length | 210.8 km double track |
| Coverage / transfer reachability | 58.7% / 87% |
| Estimated station catchment | 1,338,947 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 265 × 4-car `metro-4car` trainsets (237 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.8 km | 9 | 46 | S Mid ↔ N Outer |
| line-2 | 25.8 km | 10 | 43 | W Mid ↔ SE Outer |
| line-3 | 36.6 km | 11 | 57 | SW Outer ↔ NE Outer |
| line-4 | 27.7 km | 10 | 45 | N Outer ↔ S Mid |
| line-5 | 29.4 km | 10 | 49 | NW Outer ↔ SE Mid |
| line-6 | 63.4 km | 16 | 25 | N Inner ↔ NW Mid |
| **Total** | **210.8 km** | **66 unique** | **265** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 83,277 train-km/day |
| Annual traction demand | 525.2 GWh |
| Station/depot PV / storage | 45.0 MW / 315.0 MWh |
| Aggregate charging power | 84.0 MW |
| Dedicated solar plant | 293.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 16.7 km / 166 kWh |
| Lowest traversal charging margin | line-4: 186 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.31 bn |
| Stations | $321 M |
| Depots | $121 M |
| Rolling stock | $297 M |
| Dedicated solar plant | $234 M |
| Residual train control | $11 M |
| Charging microgrids | $17 M |
| EPC / project services | $215 M |
| **Total city programme** | **$3.53 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $695 M (19.7%) |
| Domestic / local capital | $2.83 bn (80.3%) |
| Annual public construction commitment | $294 M / yr for 7 years |
| Annual post-grace debt service | $238 M / yr |
| External capital saved vs default turnkey sensitivity | $5.66 bn |
| Capital + lifetime external interest saved | $12.75 bn |
| Annual OPEX | $80 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 636 assets / 3,553 tasks | [`phnom-penh-operations-manifest.json`](operations/phnom-penh-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`phnom-penh.toml`](phnom-penh.toml) | Expanded simulator scenario |
| [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson) | GIS corridor and stations |
| [`phnom-penh.design-quality.yaml`](phnom-penh.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh phnom-penh
```
