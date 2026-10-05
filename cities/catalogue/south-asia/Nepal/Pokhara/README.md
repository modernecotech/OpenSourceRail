# Pokhara — Urban Rail Network

**Country:** NP · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Pokhara-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.75 bn (88.4%) of external capital** and **$2.20 bn of external interest**. Capital plus saved interest totals **$3.95 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **58.854 km to 47.237 km**, with elevated land sections, straight radial tangents and bridges at water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **24 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **217 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **217 light-metro-3car trainsets / 651 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Pokhara rail network on OpenStreetMap](pokhara-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 24 / 1 |
| Route length | 71.7 km double track |
| Coverage / transfer reachability | 47.5% / 33% |
| Estimated station catchment | 285,000 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 217 × 3-car `light-metro-3car` trainsets (196 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 26.2 km | 9 | 80 | SE Mid ↔ NW Outer |
| line-2 | 20.4 km | 7 | 61 | NW Mid ↔ SE Outer |
| line-3 | 25.1 km | 8 | 76 | NW Outer ↔ SE Outer |
| **Total** | **71.7 km** | **24 unique** | **217** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 33,358 train-km/day |
| Annual traction demand | 157.8 GWh |
| Station/depot PV / storage | 20.7 MW / 129.5 MWh |
| Aggregate charging power | 11.0 MW |
| Dedicated solar plant | 56.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 9.7 km / 70 kWh |
| Lowest traversal charging margin | line-2: 67 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $633 M |
| Stations | $88 M |
| Depots | $67 M |
| Rolling stock | $195 M |
| Dedicated solar plant | $45 M |
| Residual train control | $3.6 M |
| Charging microgrids | $2.4 M |
| EPC / project services | $69 M |
| **Total city programme** | **$1.10 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $231 M (20.9%) |
| Domestic / local capital | $872 M (79.1%) |
| Annual public construction commitment | $88 M / yr for 7 years |
| Annual post-grace debt service | $71 M / yr |
| External capital saved vs default turnkey sensitivity | $1.75 bn |
| Capital + lifetime external interest saved | $3.95 bn |
| Annual OPEX | $27 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 375 assets / 2,401 tasks | [`pokhara-operations-manifest.json`](operations/pokhara-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`pokhara.toml`](pokhara.toml) | Expanded simulator scenario |
| [`pokhara.corridor.geojson`](pokhara.corridor.geojson) | GIS corridor and stations |
| [`pokhara.design-quality.yaml`](pokhara.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh pokhara
```
