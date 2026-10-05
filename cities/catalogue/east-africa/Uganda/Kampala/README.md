# Kampala — Urban Rail Network

**Country:** UG · **Population:** 1,875,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kampala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.01 bn (90.0%) of external capital** and **$10.04 bn of external interest**. Capital plus saved interest totals **$18.05 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **174.304 km to 137.490 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 3 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **57 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **235 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **235 metro-4car trainsets / 940 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Kampala rail network on OpenStreetMap](kampala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 57 / 10 |
| Route length | 187.0 km double track |
| Coverage / transfer reachability | 54.4% / 40% |
| Estimated station catchment | 1,020,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 235 × 4-car `metro-4car` trainsets (210 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 31.6 km | 11 | 53 | E Outer ↔ SW Outer |
| line-2 | 22.5 km | 8 | 37 | S Mid ↔ N Outer |
| line-3 | 25.1 km | 8 | 41 | S Mid ↔ N Outer |
| line-4 | 27.3 km | 9 | 45 | NW Outer ↔ E Outer |
| line-5 | 22.8 km | 7 | 35 | NE Mid ↔ S Outer |
| line-6 | 57.7 km | 14 | 24 | W Mid ↔ W Mid |
| **Total** | **187.0 km** | **57 unique** | **235** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 73,529 train-km/day |
| Annual traction demand | 463.8 GWh |
| Station/depot PV / storage | 43.2 MW / 306.0 MWh |
| Aggregate charging power | 73.5 MW |
| Dedicated solar plant | 254.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 9.6 km / 96 kWh |
| Lowest traversal charging margin | line-5: 142 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.78 bn |
| Stations | $244 M |
| Depots | $116 M |
| Rolling stock | $263 M |
| Dedicated solar plant | $204 M |
| Residual train control | $9.3 M |
| Charging microgrids | $15 M |
| EPC / project services | $310 M |
| **Total city programme** | **$4.94 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $886 M (17.9%) |
| Domestic / local capital | $4.06 bn (82.1%) |
| Annual public construction commitment | $610 M / yr for 7 years |
| Annual post-grace debt service | $512 M / yr |
| External capital saved vs default turnkey sensitivity | $8.01 bn |
| Capital + lifetime external interest saved | $18.05 bn |
| Annual OPEX | $102 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 19 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 560 assets / 3,129 tasks | [`kampala-operations-manifest.json`](operations/kampala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kampala.toml`](kampala.toml) | Expanded simulator scenario |
| [`kampala.corridor.geojson`](kampala.corridor.geojson) | GIS corridor and stations |
| [`kampala.design-quality.yaml`](kampala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kampala
```
