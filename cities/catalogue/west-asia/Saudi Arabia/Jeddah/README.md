# Jeddah — Urban Rail Network

**Country:** SA · **Population:** 4,700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jeddah-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.48 bn (87.7%) of external capital** and **$10.42 bn of external interest**. Capital plus saved interest totals **$18.90 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **310.121 km to 259.093 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **110 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **515 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **515 metro-6car trainsets / 3090 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Jeddah rail network on OpenStreetMap](jeddah-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 110 / 17 |
| Route length | 332.1 km double track |
| Coverage / transfer reachability | 60.1% / 42% |
| Estimated station catchment | 2,824,700 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 515 × 6-car `metro-6car` trainsets (463 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 45.0 km | 14 | 82 | S Mid ↔ NW Outer |
| line-2 | 25.6 km | 7 | 45 | S Mid ↔ NW Mid |
| line-3 | 38.1 km | 13 | 72 | N Outer ↔ SE Mid |
| line-4 | 39.8 km | 13 | 72 | N Mid ↔ SW Outer |
| line-5 | 32.1 km | 11 | 60 | E Outer ↔ W Mid |
| line-6 | 29.4 km | 10 | 54 | SE Outer ↔ W Inner |
| line-7 | 23.5 km | 8 | 46 | NE Outer ↔ S Inner |
| line-8 | 24.4 km | 9 | 48 | NE Mid ↔ SW Inner |
| line-9 | 74.2 km | 25 | 36 | NW Mid ↔ NW Mid |
| **Total** | **332.1 km** | **110 unique** | **515** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 137,174 train-km/day |
| Annual traction demand | 1,297.8 GWh |
| Station/depot PV / storage | 72.0 MW / 540.0 MWh |
| Aggregate charging power | 198.0 MW |
| Dedicated solar plant | 598.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 11.6 km / 186 kWh |
| Lowest traversal charging margin | line-2: 150 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.92 bn |
| Stations | $492 M |
| Depots | $238 M |
| Rolling stock | $865 M |
| Dedicated solar plant | $479 M |
| Residual train control | $17 M |
| Charging microgrids | $40 M |
| EPC / project services | $320 M |
| **Total city programme** | **$5.37 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.19 bn (22.1%) |
| Domestic / local capital | $4.18 bn (77.9%) |
| Annual public construction commitment | $371 M / yr for 5 years |
| Annual post-grace debt service | $260 M / yr |
| External capital saved vs default turnkey sensitivity | $8.48 bn |
| Capital + lifetime external interest saved | $18.90 bn |
| Annual OPEX | $234 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 45 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,149 assets / 6,620 tasks | [`jeddah-operations-manifest.json`](operations/jeddah-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jeddah.toml`](jeddah.toml) | Expanded simulator scenario |
| [`jeddah.corridor.geojson`](jeddah.corridor.geojson) | GIS corridor and stations |
| [`jeddah.design-quality.yaml`](jeddah.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jeddah
```
