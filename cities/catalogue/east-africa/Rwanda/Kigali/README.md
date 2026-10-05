# Kigali — Urban Rail Network

**Country:** RW · **Population:** 1,208,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kigali-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.64 bn (88.7%) of external capital** and **$4.57 bn of external interest**. Capital plus saved interest totals **$8.21 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **150.301 km to 118.815 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **55 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **191 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **191 metro-4car trainsets / 764 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kigali rail network on OpenStreetMap](kigali-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 55 / 11 |
| Route length | 155.4 km double track |
| Coverage / transfer reachability | 49.3% / 40% |
| Estimated station catchment | 595,544 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 191 × 4-car `metro-4car` trainsets (170 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.2 km | 9 | 42 | W Outer ↔ SE Outer |
| line-2 | 15.8 km | 8 | 31 | NW Mid ↔ E Mid |
| line-3 | 14.3 km | 6 | 26 | S Mid ↔ N Mid |
| line-4 | 21.1 km | 7 | 34 | NE Outer ↔ SW Mid |
| line-5 | 21.8 km | 7 | 35 | NW Outer ↔ SE Mid |
| line-6 | 55.2 km | 18 | 23 | W Mid ↔ W Mid |
| **Total** | **155.4 km** | **55 unique** | **191** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 59,434 train-km/day |
| Annual traction demand | 374.9 GWh |
| Station/depot PV / storage | 43.8 MW / 309.0 MWh |
| Aggregate charging power | 78.0 MW |
| Dedicated solar plant | 195.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 11.2 km / 112 kWh |
| Lowest traversal charging margin | line-5: 153 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.37 bn |
| Stations | $272 M |
| Depots | $106 M |
| Rolling stock | $214 M |
| Dedicated solar plant | $157 M |
| Residual train control | $7.8 M |
| Charging microgrids | $16 M |
| EPC / project services | $139 M |
| **Total city programme** | **$2.28 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $463 M (20.3%) |
| Domestic / local capital | $1.82 bn (79.7%) |
| Annual public construction commitment | $196 M / yr for 7 years |
| Annual post-grace debt service | $160 M / yr |
| External capital saved vs default turnkey sensitivity | $3.64 bn |
| Capital + lifetime external interest saved | $8.21 bn |
| Annual OPEX | $51 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 19 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 503 assets / 2,706 tasks | [`kigali-operations-manifest.json`](operations/kigali-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kigali.toml`](kigali.toml) | Expanded simulator scenario |
| [`kigali.corridor.geojson`](kigali.corridor.geojson) | GIS corridor and stations |
| [`kigali.design-quality.yaml`](kigali.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kigali
```
