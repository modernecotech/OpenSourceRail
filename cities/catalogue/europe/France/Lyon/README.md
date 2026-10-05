# Lyon — Urban Rail Network

**Country:** FR · **Population:** 1,436,354

This page contains only Lyon-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!NOTE]
> **Technical comparison only.** This model is retained for regression and engineering inspection.
> It is excluded from the developing-world programme, portfolio, national briefs, reader-book city evidence, and public examples.

**Current alignment, depot and production basis.** Core corridors change from **199.785 km to 167.617 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **77 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **302 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **302 metro-4car trainsets / 1208 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Lyon rail network on OpenStreetMap](lyon-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 77 / 13 |
| Route length | 228.3 km double track |
| Coverage / transfer reachability | 44.6% / 80% |
| Estimated station catchment | 640,613 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 302 × 4-car `metro-4car` trainsets (272 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 42.9 km | 15 | 70 | SE Outer ↔ NW Outer |
| line-2 | 36.9 km | 13 | 62 | SW Outer ↔ E Outer |
| line-3 | 20.5 km | 9 | 38 | NE Mid ↔ W Mid |
| line-4 | 39.8 km | 12 | 65 | S Outer ↔ N Outer |
| line-5 | 26.0 km | 10 | 42 | NW Outer ↔ SE Mid |
| line-6 | 62.2 km | 18 | 25 | NW Mid ↔ W Inner |
| **Total** | **228.3 km** | **77 unique** | **302** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 91,727 train-km/day |
| Annual traction demand | 578.5 GWh |
| Station/depot PV / storage | 47.4 MW / 327.0 MWh |
| Aggregate charging power | 96.0 MW |
| Dedicated solar plant | 379.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 13.9 km / 133 kWh |
| Lowest traversal charging margin | line-5: 166 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.11 bn |
| Stations | $378 M |
| Depots | $128 M |
| Rolling stock | $338 M |
| Dedicated solar plant | $304 M |
| Residual train control | $11 M |
| Charging microgrids | $20 M |
| EPC / project services | $209 M |
| **Total city programme** | **$3.50 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $724 M (20.7%) |
| Domestic / local capital | $2.77 bn (79.3%) |
| Annual public construction commitment | $284 M / yr for 3 years |
| Annual post-grace debt service | $141 M / yr |
| External capital saved vs default turnkey sensitivity | $5.57 bn |
| Capital + lifetime external interest saved | $12.28 bn |
| Annual OPEX | $197 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 731 assets / 4,078 tasks | [`lyon-operations-manifest.json`](operations/lyon-operations-manifest.json) |

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
