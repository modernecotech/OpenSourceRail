# Yaounde — Urban Rail Network

**Country:** CM · **Population:** 4,100,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Yaounde-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.00 bn (87.6%) of external capital** and **$6.26 bn of external interest**. Capital plus saved interest totals **$11.26 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **179.501 km to 161.694 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **68 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**5 line-local depots** provide **281 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **281 metro-6car trainsets / 1686 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Yaounde rail network on OpenStreetMap](yaounde-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 5 / 68 / 10 |
| Route length | 191.9 km double track |
| Coverage / transfer reachability | 45.3% / 90% |
| Estimated station catchment | 1,857,300 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 281 × 6-car `metro-6car` trainsets (253 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,205,280 passenger-trips/day |
| Annual paid-trip planning range | 220.0–351.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 38.7 km | 13 | 75 | NE Mid ↔ SW Outer |
| line-2 | 43.6 km | 14 | 81 | SE Mid ↔ NW Outer |
| line-3 | 30.0 km | 11 | 58 | E Outer ↔ W Mid |
| line-4 | 16.6 km | 9 | 38 | SE Mid ↔ W Mid |
| line-5 | 63.0 km | 21 | 29 | NW Mid ↔ NW Mid |
| **Total** | **191.9 km** | **68 unique** | **281** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,092 one-way journeys / 74,572 train-km/day |
| Annual traction demand | 705.5 GWh |
| Station/depot PV / storage | 40.6 MW / 304.0 MWh |
| Aggregate charging power | 112.0 MW |
| Dedicated solar plant | 416.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 18.1 km / 271 kWh |
| Lowest traversal charging margin | line-3: 273 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.71 bn |
| Stations | $307 M |
| Depots | $131 M |
| Rolling stock | $472 M |
| Dedicated solar plant | $333 M |
| Residual train control | $9.6 M |
| Charging microgrids | $23 M |
| EPC / project services | $185 M |
| **Total city programme** | **$3.17 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $707 M (22.3%) |
| Domestic / local capital | $2.46 bn (77.7%) |
| Annual public construction commitment | $270 M / yr for 7 years |
| Annual post-grace debt service | $221 M / yr |
| External capital saved vs default turnkey sensitivity | $5.00 bn |
| Capital + lifetime external interest saved | $11.26 bn |
| Annual OPEX | $75 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 20 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 662 assets / 3,735 tasks | [`yaounde-operations-manifest.json`](operations/yaounde-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`yaounde.toml`](yaounde.toml) | Expanded simulator scenario |
| [`yaounde.corridor.geojson`](yaounde.corridor.geojson) | GIS corridor and stations |
| [`yaounde.design-quality.yaml`](yaounde.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh yaounde
```
