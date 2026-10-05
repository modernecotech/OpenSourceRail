# Mombasa — Urban Rail Network

**Country:** KE · **Population:** 1,350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mombasa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$76.81 bn (91.4%) of external capital** and **$96.29 bn of external interest**. Capital plus saved interest totals **$173.10 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **147.687 km to 210.676 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **144 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **382 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **382 metro-4car trainsets / 1528 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Mombasa rail network on OpenStreetMap](mombasa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 144 / 24 |
| Route length | 266.1 km double track |
| Direct transfers / reachable line pairs | 86.7% / 100.0% |
| Residents within 800 m radial station catchments | 548,887 (2020 raster; 35.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 382 × 4-car `metro-4car` trainsets (344 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 34.5 km | 16 | 64 | E Outer ↔ NW Mid |
| line-2 | 21.6 km | 8 | 36 | S Outer ↔ NE Outer |
| line-3 | 17.0 km | 20 | 59 | W Inner ↔ E Mid |
| line-4 | 61.5 km | 34 | 124 | S Mid ↔ N Outer |
| line-5 | 18.6 km | 15 | 49 | NW Outer ↔ SE Mid |
| line-6 | 113.0 km | 51 | 50 | NW Mid ↔ NW Inner |
| **Total** | **266.1 km** | **144 unique** | **382** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 97,477 train-km/day |
| Annual traction demand | 614.8 GWh |
| Station/depot PV / storage | 69.9 MW / 439.5 MWh |
| Aggregate charging power | 208.5 MW |
| Dedicated solar plant | 323.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 9.7 km / 97 kWh |
| Lowest traversal charging margin | line-2: 204 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $41.71 bn |
| Stations | $1.06 bn |
| Depots | $143 M |
| Rolling stock | $428 M |
| Dedicated solar plant | $259 M |
| Residual train control | $13 M |
| Charging microgrids | $43 M |
| EPC / project services | $3.04 bn |
| **Total city programme** | **$46.70 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $7.25 bn (15.5%) |
| Domestic / local capital | $39.45 bn (84.5%) |
| Annual public construction commitment | $5.08 bn / yr for 7 years |
| Annual post-grace debt service | $4.16 bn / yr |
| External capital saved vs default turnkey sensitivity | $76.81 bn |
| Capital + lifetime external interest saved | $173.10 bn |
| Annual OPEX | $895 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 12 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,166 assets / 6,048 tasks | [`mombasa-operations-manifest.json`](operations/mombasa-operations-manifest.json) |

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
