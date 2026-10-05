# Tunis — Urban Rail Network

**Country:** TN · **Population:** 2,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Tunis-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.52 bn (89.0%) of external capital** and **$5.55 bn of external interest**. Capital plus saved interest totals **$10.07 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **190.377 km to 161.644 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **63 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **230 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **230 metro-4car trainsets / 920 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Tunis rail network on OpenStreetMap](tunis-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 63 / 9 |
| Route length | 197.5 km double track |
| Coverage / transfer reachability | 46.3% / 50% |
| Estimated station catchment | 1,342,700 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 230 × 4-car `metro-4car` trainsets (206 peak revenue) |
| Peak network throughput | 96,000 passengers/hour |
| Practical service capacity | 803,520 passenger-trips/day |
| Annual paid-trip planning range | 146.6–234.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.5 km | 13 | 56 | SE Outer ↔ W Outer |
| line-2 | 24.8 km | 8 | 39 | S Mid ↔ N Mid |
| line-3 | 38.2 km | 12 | 61 | W Outer ↔ NE Outer |
| line-4 | 29.3 km | 10 | 46 | SE Mid ↔ NW Outer |
| line-5 | 71.8 km | 20 | 28 | W Mid ↔ W Mid |
| **Total** | **197.5 km** | **63 unique** | **230** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 75,154 train-km/day |
| Annual traction demand | 474.0 GWh |
| Station/depot PV / storage | 40.9 MW / 279.5 MWh |
| Aggregate charging power | 87.0 MW |
| Dedicated solar plant | 224.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.4 km / 119 kWh |
| Lowest traversal charging margin | line-2: 179 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.81 bn |
| Stations | $264 M |
| Depots | $103 M |
| Rolling stock | $258 M |
| Dedicated solar plant | $180 M |
| Residual train control | $9.9 M |
| Charging microgrids | $18 M |
| EPC / project services | $173 M |
| **Total city programme** | **$2.82 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $560 M (19.9%) |
| Domestic / local capital | $2.26 bn (80.1%) |
| Annual public construction commitment | $278 M / yr for 5 years |
| Annual post-grace debt service | $203 M / yr |
| External capital saved vs default turnkey sensitivity | $4.52 bn |
| Capital + lifetime external interest saved | $10.07 bn |
| Annual OPEX | $70 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 28 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 584 assets / 3,202 tasks | [`tunis-operations-manifest.json`](operations/tunis-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`tunis.toml`](tunis.toml) | Expanded simulator scenario |
| [`tunis.corridor.geojson`](tunis.corridor.geojson) | GIS corridor and stations |
| [`tunis.design-quality.yaml`](tunis.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh tunis
```
