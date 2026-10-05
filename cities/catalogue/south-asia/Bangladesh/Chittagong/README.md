# Chittagong — Urban Rail Network

**Country:** BD · **Population:** 5,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Chittagong-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.98 bn (87.7%) of external capital** and **$10.00 bn of external interest**. Capital plus saved interest totals **$17.97 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **257.102 km to 217.329 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **90 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **445 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **445 metro-6car trainsets / 2670 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Chittagong rail network on OpenStreetMap](chittagong-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 90 / 16 |
| Route length | 288.7 km double track |
| Coverage / transfer reachability | 60.1% / 46% |
| Estimated station catchment | 3,125,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 445 × 6-car `metro-6car` trainsets (402 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.0 km | 12 | 73 | S Mid ↔ NW Outer |
| line-2 | 22.9 km | 8 | 41 | S Mid ↔ N Mid |
| line-3 | 41.9 km | 12 | 76 | N Mid ↔ S Outer |
| line-4 | 28.4 km | 10 | 53 | NE Mid ↔ SW Inner |
| line-5 | 31.4 km | 11 | 61 | SW Inner ↔ NE Outer |
| line-6 | 26.0 km | 8 | 48 | W Inner ↔ SE Mid |
| line-7 | 34.0 km | 9 | 63 | W Inner ↔ SE Outer |
| line-8 | 66.2 km | 20 | 30 | NW Mid ↔ NW Mid |
| **Total** | **288.7 km** | **90 unique** | **445** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,488 one-way journeys / 118,850 train-km/day |
| Annual traction demand | 1,124.4 GWh |
| Station/depot PV / storage | 60.1 MW / 454.0 MWh |
| Aggregate charging power | 150.0 MW |
| Dedicated solar plant | 668.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 20.5 km / 307 kWh |
| Lowest traversal charging margin | line-6: 160 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.81 bn |
| Stations | $407 M |
| Depots | $210 M |
| Rolling stock | $748 M |
| Dedicated solar plant | $535 M |
| Residual train control | $14 M |
| Charging microgrids | $31 M |
| EPC / project services | $296 M |
| **Total city programme** | **$5.05 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.12 bn (22.2%) |
| Domestic / local capital | $3.93 bn (77.8%) |
| Annual public construction commitment | $430 M / yr for 7 years |
| Annual post-grace debt service | $353 M / yr |
| External capital saved vs default turnkey sensitivity | $7.98 bn |
| Capital + lifetime external interest saved | $17.97 bn |
| Annual OPEX | $119 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 25 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 962 assets / 5,606 tasks | [`chittagong-operations-manifest.json`](operations/chittagong-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`chittagong.toml`](chittagong.toml) | Expanded simulator scenario |
| [`chittagong.corridor.geojson`](chittagong.corridor.geojson) | GIS corridor and stations |
| [`chittagong.design-quality.yaml`](chittagong.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh chittagong
```
