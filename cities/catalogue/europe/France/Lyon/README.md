# Lyon — Urban Rail Network

**Country:** FR · **Population:** 1,436,354

This page contains only Lyon-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!NOTE]
> **Technical comparison only.** This model is retained for regression and engineering inspection.
> It is excluded from the developing-world programme, portfolio, national briefs, reader-book city evidence, and public examples.

**Current alignment, depot and production basis.** Core corridors change from **199.785 km to 155.611 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **69 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **283 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **283 metro-4car trainsets / 1132 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Lyon rail network on OpenStreetMap](lyon-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 69 / 12 |
| Route length | 221.1 km double track |
| Coverage / transfer reachability | 44.6% / 60% |
| Estimated station catchment | 640,613 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 283 × 4-car `metro-4car` trainsets (254 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 40.2 km | 13 | 64 | SE Outer ↔ NW Outer |
| line-2 | 35.2 km | 11 | 56 | SW Outer ↔ E Outer |
| line-3 | 21.0 km | 8 | 36 | NE Mid ↔ W Mid |
| line-4 | 37.4 km | 12 | 61 | S Outer ↔ N Outer |
| line-5 | 25.4 km | 9 | 42 | NW Outer ↔ SE Mid |
| line-6 | 61.9 km | 16 | 24 | NW Mid ↔ W Mid |
| **Total** | **221.1 km** | **69 unique** | **283** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 88,406 train-km/day |
| Annual traction demand | 557.6 GWh |
| Station/depot PV / storage | 45.3 MW / 316.5 MWh |
| Aggregate charging power | 85.5 MW |
| Dedicated solar plant | 366.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 12.5 km / 120 kWh |
| Lowest traversal charging margin | line-5: 185 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.89 bn |
| Stations | $311 M |
| Depots | $124 M |
| Rolling stock | $317 M |
| Dedicated solar plant | $293 M |
| Residual train control | $11 M |
| Charging microgrids | $18 M |
| EPC / project services | $187 M |
| **Total city programme** | **$3.15 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $660 M (21.0%) |
| Domestic / local capital | $2.49 bn (79.0%) |
| Annual public construction commitment | $255 M / yr for 3 years |
| Annual post-grace debt service | $127 M / yr |
| External capital saved vs default turnkey sensitivity | $5.01 bn |
| Capital + lifetime external interest saved | $11.05 bn |
| Annual OPEX | $182 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 20 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 670 assets / 3,764 tasks | [`lyon-operations-manifest.json`](operations/lyon-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lyon.toml`](lyon.toml) | Expanded simulator scenario |
| [`lyon.corridor.geojson`](lyon.corridor.geojson) | GIS corridor and stations |
| [`lyon.design-quality.yaml`](lyon.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lyon
```
