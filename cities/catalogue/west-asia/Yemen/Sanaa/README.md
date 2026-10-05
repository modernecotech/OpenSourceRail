# Sanaa — Urban Rail Network

**Country:** YE · **Population:** 3,937,500 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sanaa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.34 bn (87.8%) of external capital** and **$6.89 bn of external interest**. Capital plus saved interest totals **$12.23 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **192.451 km to 165.144 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **71 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **329 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **329 metro-6car trainsets / 1974 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Sanaa rail network on OpenStreetMap](sanaa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 71 / 9 |
| Route length | 211.8 km double track |
| Coverage / transfer reachability | 57.7% / 52% |
| Estimated station catchment | 2,271,937 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 329 × 6-car `metro-6car` trainsets (295 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 36.9 km | 12 | 72 | NW Outer ↔ SE Mid |
| line-2 | 18.0 km | 6 | 36 | N Mid ↔ SE Mid |
| line-3 | 29.2 km | 10 | 56 | NW Mid ↔ SE Outer |
| line-4 | 21.9 km | 8 | 40 | S Mid ↔ NE Mid |
| line-5 | 30.5 km | 10 | 58 | E Outer ↔ W Mid |
| line-6 | 19.6 km | 7 | 39 | W Outer ↔ SE Inner |
| line-7 | 55.7 km | 18 | 28 | N Mid ↔ N Mid |
| **Total** | **211.8 km** | **71 unique** | **329** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,022 one-way journeys / 85,542 train-km/day |
| Annual traction demand | 809.3 GWh |
| Station/depot PV / storage | 50.3 MW / 382.0 MWh |
| Aggregate charging power | 116.0 MW |
| Dedicated solar plant | 353.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 17.5 km / 253 kWh |
| Lowest traversal charging margin | line-6: 179 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.84 bn |
| Stations | $295 M |
| Depots | $165 M |
| Rolling stock | $553 M |
| Dedicated solar plant | $283 M |
| Residual train control | $11 M |
| Charging microgrids | $24 M |
| EPC / project services | $202 M |
| **Total city programme** | **$3.38 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $743 M (22.0%) |
| Domestic / local capital | $2.63 bn (78.0%) |
| Annual public construction commitment | $465 M / yr for 10 years |
| Annual post-grace debt service | $428 M / yr |
| External capital saved vs default turnkey sensitivity | $5.34 bn |
| Capital + lifetime external interest saved | $12.23 bn |
| Annual OPEX | $77 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 23 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 734 assets / 4,214 tasks | [`sanaa-operations-manifest.json`](operations/sanaa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sanaa.toml`](sanaa.toml) | Expanded simulator scenario |
| [`sanaa.corridor.geojson`](sanaa.corridor.geojson) | GIS corridor and stations |
| [`sanaa.design-quality.yaml`](sanaa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sanaa
```
