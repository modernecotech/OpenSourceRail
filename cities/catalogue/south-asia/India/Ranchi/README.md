# Ranchi — Urban Rail Network

**Country:** IN · **Population:** 1,400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Ranchi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$5.07 bn (88.8%) of external capital** and **$6.23 bn of external interest**. Capital plus saved interest totals **$11.30 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **179.054 km to 168.000 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **78 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **264 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **264 metro-4car trainsets / 1056 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates.

## Network

![Ranchi rail network on OpenStreetMap](ranchi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 78 / 17 |
| Route length | 205.1 km double track |
| Coverage / transfer reachability | 45.8% / 93% |
| Estimated station catchment | 641,200 residents |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 264 × 4-car `metro-4car` trainsets (236 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.0 km | 14 | 56 | NE Outer ↔ SW Mid |
| line-2 | 23.8 km | 11 | 45 | N Mid ↔ S Outer |
| line-3 | 20.8 km | 10 | 40 | E Mid ↔ W Mid |
| line-4 | 27.8 km | 9 | 46 | E Outer ↔ SW Mid |
| line-5 | 25.0 km | 11 | 46 | NW Outer ↔ SE Mid |
| line-6 | 75.8 km | 23 | 31 | NW Mid ↔ NW Mid |
| **Total** | **205.1 km** | **78 unique** | **264** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 77,770 train-km/day |
| Annual traction demand | 490.5 GWh |
| Station/depot PV / storage | 49.2 MW / 336.0 MWh |
| Aggregate charging power | 103.5 MW |
| Dedicated solar plant | 265.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 13.9 km / 139 kWh |
| Lowest traversal charging margin | line-4: 210 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.88 bn |
| Stations | $438 M |
| Depots | $122 M |
| Rolling stock | $296 M |
| Dedicated solar plant | $212 M |
| Residual train control | $10 M |
| Charging microgrids | $21 M |
| EPC / project services | $194 M |
| **Total city programme** | **$3.17 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $642 M (20.2%) |
| Domestic / local capital | $2.53 bn (79.8%) |
| Annual public construction commitment | $276 M / yr for 5 years |
| Annual post-grace debt service | $197 M / yr |
| External capital saved vs default turnkey sensitivity | $5.07 bn |
| Capital + lifetime external interest saved | $11.30 bn |
| Annual OPEX | $74 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 697 assets / 3,768 tasks | [`ranchi-operations-manifest.json`](operations/ranchi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`ranchi.toml`](ranchi.toml) | Expanded simulator scenario |
| [`ranchi.corridor.geojson`](ranchi.corridor.geojson) | GIS corridor and stations |
| [`ranchi.design-quality.yaml`](ranchi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh ranchi
```
