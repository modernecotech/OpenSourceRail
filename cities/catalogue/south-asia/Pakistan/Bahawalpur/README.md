# Bahawalpur — Urban Rail Network

**Country:** PK · **Population:** 900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Bahawalpur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$959 M (88.4%) of external capital** and **$1.20 bn of external interest**. Capital plus saved interest totals **$2.16 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **39.814 km to 29.460 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **15 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **116 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **116 light-metro-3car trainsets / 348 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Bahawalpur rail network on OpenStreetMap](bahawalpur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 15 / 1 |
| Route length | 37.5 km double track |
| Coverage / transfer reachability | 33.2% / 33% |
| Estimated station catchment | 298,800 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 116 × 3-car `light-metro-3car` trainsets (105 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.5 km | 5 | 43 | SW Outer ↔ NE Mid |
| line-2 | 13.0 km | 5 | 41 | NW Outer ↔ SE Inner |
| line-3 | 10.1 km | 5 | 32 | E Outer ↔ W Inner |
| **Total** | **37.5 km** | **15 unique** | **116** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 17,457 train-km/day |
| Annual traction demand | 82.6 GWh |
| Station/depot PV / storage | 18.3 MW / 125.5 MWh |
| Aggregate charging power | 7.0 MW |
| Dedicated solar plant | 22.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 7.0 km / 56 kWh |
| Lowest traversal charging margin | line-2: 32 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $332 M |
| Stations | $56 M |
| Depots | $51 M |
| Rolling stock | $104 M |
| Dedicated solar plant | $18 M |
| Residual train control | $1.9 M |
| Charging microgrids | $1.6 M |
| EPC / project services | $38 M |
| **Total city programme** | **$603 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $126 M (20.8%) |
| Domestic / local capital | $477 M (79.2%) |
| Annual public construction commitment | $82 M / yr for 7 years |
| Annual post-grace debt service | $71 M / yr |
| External capital saved vs default turnkey sensitivity | $959 M |
| Capital + lifetime external interest saved | $2.16 bn |
| Annual OPEX | $15 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 215 assets / 1,319 tasks | [`bahawalpur-operations-manifest.json`](operations/bahawalpur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`bahawalpur.toml`](bahawalpur.toml) | Expanded simulator scenario |
| [`bahawalpur.corridor.geojson`](bahawalpur.corridor.geojson) | GIS corridor and stations |
| [`bahawalpur.design-quality.yaml`](bahawalpur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh bahawalpur
```
