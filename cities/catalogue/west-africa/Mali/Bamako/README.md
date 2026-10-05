# Bamako — Urban Rail Network

**Country:** ML · **Population:** 2,929,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bamako-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.09 bn (89.4%) of external capital** and **$6.57 bn of external interest**. Capital plus saved interest totals **$11.66 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **178.463 km to 152.365 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **64 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **233 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **233 metro-4car trainsets / 932 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bamako rail network on OpenStreetMap](bamako-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 64 / 9 |
| Route length | 193.2 km double track |
| Coverage / transfer reachability | 40.9% / 47% |
| Estimated station catchment | 1,197,961 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 233 × 4-car `metro-4car` trainsets (209 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 39.0 km | 14 | 61 | NW Outer ↔ SE Mid |
| line-2 | 24.5 km | 8 | 38 | SW Mid ↔ NE Mid |
| line-3 | 17.0 km | 7 | 30 | SW Mid ↔ NE Inner |
| line-4 | 28.6 km | 11 | 47 | W Mid ↔ SE Outer |
| line-5 | 19.4 km | 7 | 32 | N Inner ↔ S Mid |
| line-6 | 64.8 km | 17 | 25 | N Mid ↔ NW Mid |
| **Total** | **193.2 km** | **64 unique** | **233** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 74,778 train-km/day |
| Annual traction demand | 471.6 GWh |
| Station/depot PV / storage | 45.9 MW / 319.5 MWh |
| Aggregate charging power | 88.5 MW |
| Dedicated solar plant | 175.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 12.1 km / 134 kWh |
| Lowest traversal charging margin | line-4: 140 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.15 bn |
| Stations | $265 M |
| Depots | $116 M |
| Rolling stock | $261 M |
| Dedicated solar plant | $141 M |
| Residual train control | $9.7 M |
| Charging microgrids | $18 M |
| EPC / project services | $198 M |
| **Total city programme** | **$3.16 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $601 M (19.0%) |
| Domestic / local capital | $2.56 bn (81.0%) |
| Annual public construction commitment | $273 M / yr for 10 years |
| Annual post-grace debt service | $245 M / yr |
| External capital saved vs default turnkey sensitivity | $5.09 bn |
| Capital + lifetime external interest saved | $11.66 bn |
| Annual OPEX | $68 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 29 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 594 assets / 3,244 tasks | [`bamako-operations-manifest.json`](operations/bamako-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bamako.toml`](bamako.toml) | Expanded simulator scenario |
| [`bamako.corridor.geojson`](bamako.corridor.geojson) | GIS corridor and stations |
| [`bamako.design-quality.yaml`](bamako.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bamako
```
