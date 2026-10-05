# Madurai — Urban Rail Network

**Country:** IN · **Population:** 1,600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Madurai-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.71 bn (88.8%) of external capital** and **$5.79 bn of external interest**. Capital plus saved interest totals **$10.49 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **176.984 km to 147.650 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **63 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **247 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **247 metro-4car trainsets / 988 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Madurai rail network on OpenStreetMap](madurai-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 63 / 8 |
| Route length | 198.6 km double track |
| Coverage / transfer reachability | 54.1% / 47% |
| Estimated station catchment | 865,600 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 247 × 4-car `metro-4car` trainsets (220 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.6 km | 11 | 57 | NE Outer ↔ SW Outer |
| line-2 | 25.8 km | 10 | 45 | NE Outer ↔ SW Inner |
| line-3 | 26.9 km | 9 | 46 | NW Inner ↔ SE Outer |
| line-4 | 22.7 km | 7 | 35 | S Inner ↔ NW Outer |
| line-5 | 22.5 km | 9 | 37 | W Outer ↔ E Inner |
| line-6 | 66.1 km | 17 | 27 | NW Mid ↔ W Mid |
| **Total** | **198.6 km** | **63 unique** | **247** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 76,952 train-km/day |
| Annual traction demand | 485.4 GWh |
| Station/depot PV / storage | 43.5 MW / 307.5 MWh |
| Aggregate charging power | 75.0 MW |
| Dedicated solar plant | 268.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 22.0 km / 220 kWh |
| Lowest traversal charging margin | line-4: 142 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.88 bn |
| Stations | $251 M |
| Depots | $118 M |
| Rolling stock | $277 M |
| Dedicated solar plant | $215 M |
| Residual train control | $9.9 M |
| Charging microgrids | $15 M |
| EPC / project services | $179 M |
| **Total city programme** | **$2.94 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $593 M (20.1%) |
| Domestic / local capital | $2.35 bn (79.9%) |
| Annual public construction commitment | $256 M / yr for 5 years |
| Annual post-grace debt service | $182 M / yr |
| External capital saved vs default turnkey sensitivity | $4.71 bn |
| Capital + lifetime external interest saved | $10.49 bn |
| Annual OPEX | $69 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 19 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 599 assets / 3,327 tasks | [`madurai-operations-manifest.json`](operations/madurai-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`madurai.toml`](madurai.toml) | Expanded simulator scenario |
| [`madurai.corridor.geojson`](madurai.corridor.geojson) | GIS corridor and stations |
| [`madurai.design-quality.yaml`](madurai.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh madurai
```
