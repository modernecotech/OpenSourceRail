# Gazipur — Urban Rail Network

**Country:** BD · **Population:** 1,400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gazipur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.41 bn (88.4%) of external capital** and **$6.79 bn of external interest**. Capital plus saved interest totals **$12.20 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **164.718 km to 142.899 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **80 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **321 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **321 metro-4car trainsets / 1284 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Gazipur rail network on OpenStreetMap](gazipur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 80 / 14 |
| Route length | 244.8 km double track |
| Coverage / transfer reachability | 38.8% / 67% |
| Estimated station catchment | 543,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 321 × 4-car `metro-4car` trainsets (288 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.5 km | 11 | 51 | S Mid ↔ N Mid |
| line-2 | 33.8 km | 13 | 57 | W Mid ↔ E Outer |
| line-3 | 45.0 km | 13 | 72 | NE Outer ↔ SW Outer |
| line-4 | 42.9 km | 13 | 68 | SE Outer ↔ NW Outer |
| line-5 | 27.7 km | 9 | 46 | N Outer ↔ S Mid |
| line-6 | 63.9 km | 21 | 27 | W Mid ↔ W Mid |
| **Total** | **244.8 km** | **80 unique** | **321** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 98,968 train-km/day |
| Annual traction demand | 624.2 GWh |
| Station/depot PV / storage | 49.5 MW / 337.5 MWh |
| Aggregate charging power | 106.5 MW |
| Dedicated solar plant | 352.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 10.5 km / 105 kWh |
| Lowest traversal charging margin | line-5: 210 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.00 bn |
| Stations | $392 M |
| Depots | $132 M |
| Rolling stock | $360 M |
| Dedicated solar plant | $282 M |
| Residual train control | $12 M |
| Charging microgrids | $22 M |
| EPC / project services | $204 M |
| **Total city programme** | **$3.40 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $709 M (20.9%) |
| Domestic / local capital | $2.69 bn (79.1%) |
| Annual public construction commitment | $292 M / yr for 7 years |
| Annual post-grace debt service | $238 M / yr |
| External capital saved vs default turnkey sensitivity | $5.41 bn |
| Capital + lifetime external interest saved | $12.20 bn |
| Annual OPEX | $79 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 27 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 772 assets / 4,322 tasks | [`gazipur-operations-manifest.json`](operations/gazipur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gazipur.toml`](gazipur.toml) | Expanded simulator scenario |
| [`gazipur.corridor.geojson`](gazipur.corridor.geojson) | GIS corridor and stations |
| [`gazipur.design-quality.yaml`](gazipur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gazipur
```
