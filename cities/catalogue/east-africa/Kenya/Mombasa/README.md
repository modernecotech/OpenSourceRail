# Mombasa — Urban Rail Network

**Country:** KE · **Population:** 1,350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mombasa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.47 bn (88.9%) of external capital** and **$4.35 bn of external interest**. Capital plus saved interest totals **$7.82 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **147.687 km to 121.626 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **52 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **171 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **171 metro-4car trainsets / 684 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Mombasa rail network on OpenStreetMap](mombasa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 52 / 13 |
| Route length | 138.1 km double track |
| Coverage / transfer reachability | 56.7% / 47% |
| Estimated station catchment | 765,449 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 171 × 4-car `metro-4car` trainsets (153 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.6 km | 8 | 30 | E Mid ↔ W Mid |
| line-2 | 22.2 km | 8 | 37 | S Outer ↔ NE Outer |
| line-3 | 11.7 km | 5 | 21 | W Mid ↔ E Mid |
| line-4 | 17.3 km | 5 | 28 | S Mid ↔ N Outer |
| line-5 | 19.3 km | 8 | 34 | NW Outer ↔ S Mid |
| line-6 | 53.0 km | 18 | 21 | NW Mid ↔ W Mid |
| **Total** | **138.1 km** | **52 unique** | **171** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 51,903 train-km/day |
| Annual traction demand | 327.4 GWh |
| Station/depot PV / storage | 43.2 MW / 306.0 MWh |
| Aggregate charging power | 75.0 MW |
| Dedicated solar plant | 165.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 7.0 km / 70 kWh |
| Lowest traversal charging margin | line-4: 141 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.32 bn |
| Stations | $270 M |
| Depots | $102 M |
| Rolling stock | $192 M |
| Dedicated solar plant | $132 M |
| Residual train control | $6.9 M |
| Charging microgrids | $15 M |
| EPC / project services | $133 M |
| **Total city programme** | **$2.17 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $433 M (20.0%) |
| Domestic / local capital | $1.74 bn (80.0%) |
| Annual public construction commitment | $229 M / yr for 7 years |
| Annual post-grace debt service | $190 M / yr |
| External capital saved vs default turnkey sensitivity | $3.47 bn |
| Capital + lifetime external interest saved | $7.82 bn |
| Annual OPEX | $51 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 16 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 466 assets / 2,473 tasks | [`mombasa-operations-manifest.json`](operations/mombasa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mombasa.toml`](mombasa.toml) | Expanded simulator scenario |
| [`mombasa.corridor.geojson`](mombasa.corridor.geojson) | GIS corridor and stations |
| [`mombasa.design-quality.yaml`](mombasa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mombasa
```
