# Amman — Urban Rail Network

**Country:** JO · **Population:** 4,007,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Amman-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.03 bn (87.8%) of external capital** and **$9.87 bn of external interest**. Capital plus saved interest totals **$17.90 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **274.882 km to 224.953 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **107 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **479 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **479 metro-6car trainsets / 2874 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Amman rail network on OpenStreetMap](amman-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 107 / 17 |
| Route length | 311.8 km double track |
| Coverage / transfer reachability | 52.5% / 47% |
| Estimated station catchment | 2,103,675 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 479 × 6-car `metro-6car` trainsets (431 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.4 km | 14 | 74 | SW Outer ↔ NE Outer |
| line-2 | 39.5 km | 13 | 73 | N Outer ↔ S Outer |
| line-3 | 23.4 km | 8 | 42 | S Outer ↔ NW Mid |
| line-4 | 18.8 km | 6 | 36 | N Inner ↔ S Mid |
| line-5 | 29.5 km | 11 | 53 | W Outer ↔ SE Mid |
| line-6 | 31.6 km | 10 | 59 | E Mid ↔ W Outer |
| line-7 | 25.5 km | 10 | 49 | E Mid ↔ NW Outer |
| line-8 | 29.0 km | 11 | 57 | NE Outer ↔ SW Mid |
| line-9 | 76.0 km | 24 | 36 | W Mid ↔ W Mid |
| **Total** | **311.8 km** | **107 unique** | **479** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 127,310 train-km/day |
| Annual traction demand | 1,204.5 GWh |
| Station/depot PV / storage | 72.3 MW / 542.0 MWh |
| Aggregate charging power | 200.0 MW |
| Dedicated solar plant | 549.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 11.7 km / 189 kWh |
| Lowest traversal charging margin | line-3: 172 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.77 bn |
| Stations | $480 M |
| Depots | $229 M |
| Rolling stock | $805 M |
| Dedicated solar plant | $439 M |
| Residual train control | $16 M |
| Charging microgrids | $41 M |
| EPC / project services | $304 M |
| **Total city programme** | **$5.08 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.12 bn (22.0%) |
| Domestic / local capital | $3.96 bn (78.0%) |
| Annual public construction commitment | $447 M / yr for 5 years |
| Annual post-grace debt service | $322 M / yr |
| External capital saved vs default turnkey sensitivity | $8.03 bn |
| Capital + lifetime external interest saved | $17.90 bn |
| Annual OPEX | $148 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 45 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,096 assets / 6,252 tasks | [`amman-operations-manifest.json`](operations/amman-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`amman.toml`](amman.toml) | Expanded simulator scenario |
| [`amman.corridor.geojson`](amman.corridor.geojson) | GIS corridor and stations |
| [`amman.design-quality.yaml`](amman.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh amman
```
