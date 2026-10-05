# Kinshasa — Urban Rail Network

**Country:** CD · **Population:** 17,178,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kinshasa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$137.77 bn (91.0%) of external capital** and **$177.96 bn of external interest**. Capital plus saved interest totals **$315.73 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **323.681 km to 443.068 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **483 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **1440 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **1440 metro-6car trainsets / 8640 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Kinshasa rail network on OpenStreetMap](kinshasa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 483 / 31 |
| Route length | 558.0 km double track |
| Direct transfers / reachable line pairs | 97.2% / 100.0% |
| Residents within 800 m radial station catchments | 2,875,676 (2020 raster; 38.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 1440 × 6-car `metro-6car` trainsets (1306 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 62.8 km | 70 | 228 | N Mid ↔ SE Outer |
| line-2 | 66.9 km | 74 | 241 | E Outer ↔ N Mid |
| line-3 | 31.8 km | 32 | 108 | SE Outer ↔ W Mid |
| line-4 | 64.1 km | 68 | 225 | S Mid ↔ NE Mid |
| line-5 | 48.6 km | 20 | 97 | SW Outer ↔ E Outer |
| line-6 | 49.4 km | 53 | 172 | SE Mid ↔ NW Outer |
| line-7 | 91.7 km | 55 | 215 | NE Outer ↔ S Outer |
| line-8 | 36.0 km | 16 | 71 | E Mid ↔ SW Mid |
| line-9 | 106.7 km | 95 | 83 | N Inner ↔ N Inner |
| **Total** | **558.0 km** | **483 unique** | **1440** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 234,685 train-km/day |
| Annual traction demand | 2,220.3 GWh |
| Station/depot PV / storage | 184.2 MW / 1,288.0 MWh |
| Aggregate charging power | 946.0 MW |
| Dedicated solar plant | 1,245.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 17.5 km / 262 kWh |
| Lowest traversal charging margin | line-8: 452 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $71.01 bn |
| Stations | $3.59 bn |
| Depots | $477 M |
| Rolling stock | $2.42 bn |
| Dedicated solar plant | $996 M |
| Residual train control | $28 M |
| Charging microgrids | $191 M |
| EPC / project services | $5.44 bn |
| **Total city programme** | **$84.14 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $13.69 bn (16.3%) |
| Domestic / local capital | $70.45 bn (83.7%) |
| Annual public construction commitment | $9.35 bn / yr for 10 years |
| Annual post-grace debt service | $8.36 bn / yr |
| External capital saved vs default turnkey sensitivity | $137.77 bn |
| Capital + lifetime external interest saved | $315.73 bn |
| Annual OPEX | $1.64 bn / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 31 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 4,078 assets / 21,801 tasks | [`kinshasa-operations-manifest.json`](operations/kinshasa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kinshasa.toml`](kinshasa.toml) | Expanded simulator scenario |
| [`kinshasa.corridor.geojson`](kinshasa.corridor.geojson) | GIS corridor and stations |
| [`kinshasa.design-quality.yaml`](kinshasa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kinshasa
```
