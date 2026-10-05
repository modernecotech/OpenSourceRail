# Kampala — Urban Rail Network

**Country:** UG · **Population:** 1,875,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kampala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.27 bn (89.5%) of external capital** and **$7.86 bn of external interest**. Capital plus saved interest totals **$14.13 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **174.304 km to 149.814 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 3 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **67 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **242 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **242 metro-4car trainsets / 968 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Kampala rail network on OpenStreetMap](kampala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 67 / 13 |
| Route length | 187.4 km double track |
| Direct transfers / reachable line pairs | 93.3% / 100.0% |
| Residents within 800 m radial station catchments | 743,365 (2020 raster; 19.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 242 × 4-car `metro-4car` trainsets (217 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 982,080 passenger-trips/day |
| Annual paid-trip planning range | 179.2–286.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.5 km | 13 | 54 | E Outer ↔ SW Outer |
| line-2 | 22.3 km | 9 | 38 | S Mid ↔ N Outer |
| line-3 | 25.3 km | 10 | 42 | S Mid ↔ N Outer |
| line-4 | 27.0 km | 11 | 46 | NW Outer ↔ E Mid |
| line-5 | 22.5 km | 9 | 39 | NE Mid ↔ S Outer |
| line-6 | 57.9 km | 15 | 23 | W Mid ↔ W Mid |
| **Total** | **187.4 km** | **67 unique** | **242** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,558 one-way journeys / 73,701 train-km/day |
| Annual traction demand | 464.8 GWh |
| Station/depot PV / storage | 46.2 MW / 321.0 MWh |
| Aggregate charging power | 88.5 MW |
| Dedicated solar plant | 252.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 10.2 km / 102 kWh |
| Lowest traversal charging margin | line-4: 194 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.68 bn |
| Stations | $349 M |
| Depots | $117 M |
| Rolling stock | $271 M |
| Dedicated solar plant | $202 M |
| Residual train control | $9.4 M |
| Charging microgrids | $18 M |
| EPC / project services | $241 M |
| **Total city programme** | **$3.89 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $736 M (18.9%) |
| Domestic / local capital | $3.16 bn (81.1%) |
| Annual public construction commitment | $477 M / yr for 7 years |
| Annual post-grace debt service | $402 M / yr |
| External capital saved vs default turnkey sensitivity | $6.27 bn |
| Capital + lifetime external interest saved | $14.13 bn |
| Annual OPEX | $83 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 17 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 618 assets / 3,373 tasks | [`kampala-operations-manifest.json`](operations/kampala-operations-manifest.json) |

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
