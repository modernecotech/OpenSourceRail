# Mandalay — Urban Rail Network

**Country:** MM · **Population:** 1,726,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mandalay-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.40 bn (88.9%) of external capital** and **$5.69 bn of external interest**. Capital plus saved interest totals **$10.09 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **153.094 km to 124.718 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **61 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **253 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **253 metro-4car trainsets / 1012 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mandalay rail network on OpenStreetMap](mandalay-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 61 / 11 |
| Route length | 199.2 km double track |
| Coverage / transfer reachability | 52.0% / 47% |
| Estimated station catchment | 897,520 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 253 × 4-car `metro-4car` trainsets (226 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 36.2 km | 12 | 58 | N Outer ↔ S Outer |
| line-2 | 29.8 km | 9 | 48 | NW Mid ↔ SE Outer |
| line-3 | 29.0 km | 9 | 46 | SW Outer ↔ NE Mid |
| line-4 | 21.6 km | 7 | 37 | W Inner ↔ NE Outer |
| line-5 | 23.8 km | 8 | 39 | E Mid ↔ S Outer |
| line-6 | 58.8 km | 16 | 25 | NW Mid ↔ NW Mid |
| **Total** | **199.2 km** | **61 unique** | **253** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 78,958 train-km/day |
| Annual traction demand | 498.0 GWh |
| Station/depot PV / storage | 42.0 MW / 300.0 MWh |
| Aggregate charging power | 69.0 MW |
| Dedicated solar plant | 193.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 22.1 km / 246 kWh |
| Lowest traversal charging margin | line-3: 98 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.74 bn |
| Stations | $257 M |
| Depots | $119 M |
| Rolling stock | $283 M |
| Dedicated solar plant | $154 M |
| Residual train control | $10.0 M |
| Charging microgrids | $14 M |
| EPC / project services | $170 M |
| **Total city programme** | **$2.75 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $547 M (19.9%) |
| Domestic / local capital | $2.20 bn (80.1%) |
| Annual public construction commitment | $298 M / yr for 10 years |
| Annual post-grace debt service | $269 M / yr |
| External capital saved vs default turnkey sensitivity | $4.40 bn |
| Capital + lifetime external interest saved | $10.09 bn |
| Annual OPEX | $62 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 15 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 592 assets / 3,333 tasks | [`mandalay-operations-manifest.json`](operations/mandalay-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mandalay.toml`](mandalay.toml) | Expanded simulator scenario |
| [`mandalay.corridor.geojson`](mandalay.corridor.geojson) | GIS corridor and stations |
| [`mandalay.design-quality.yaml`](mandalay.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mandalay
```
