# Karachi — Urban Rail Network

**Country:** PK · **Population:** 20,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Karachi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$42.75 bn (90.6%) of external capital** and **$53.59 bn of external interest**. Capital plus saved interest totals **$96.35 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **366.727 km to 386.416 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **193 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **700 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **700 metro-6car trainsets / 4200 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Karachi rail network on OpenStreetMap](karachi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 193 / 35 |
| Route length | 462.4 km double track |
| Direct transfers / reachable line pairs | 83.3% / 100.0% |
| Residents within 800 m radial station catchments | 5,388,866 (2020 raster; 33.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 700 × 6-car `metro-6car` trainsets (632 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,276,640 passenger-trips/day |
| Annual paid-trip planning range | 415.5–664.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 43.6 km | 16 | 84 | E Outer ↔ W Mid |
| line-2 | 34.2 km | 17 | 72 | N Outer ↔ SW Mid |
| line-3 | 46.5 km | 20 | 89 | W Outer ↔ E Outer |
| line-4 | 27.8 km | 11 | 53 | E Mid ↔ NW Mid |
| line-5 | 39.0 km | 15 | 78 | NE Outer ↔ S Mid |
| line-6 | 40.0 km | 16 | 74 | N Outer ↔ SE Mid |
| line-7 | 41.1 km | 20 | 83 | NW Outer ↔ S Mid |
| line-8 | 47.3 km | 24 | 102 | NE Outer ↔ SW Mid |
| line-9 | 143.1 km | 54 | 65 | NW Mid ↔ NW Mid |
| **Total** | **462.4 km** | **193 unique** | **700** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 181,749 train-km/day |
| Annual traction demand | 1,719.5 GWh |
| Station/depot PV / storage | 96.0 MW / 700.0 MWh |
| Aggregate charging power | 358.0 MW |
| Dedicated solar plant | 723.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 16.9 km / 283 kWh |
| Lowest traversal charging margin | line-6: 245 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $21.26 bn |
| Stations | $1.16 bn |
| Depots | $287 M |
| Rolling stock | $1.18 bn |
| Dedicated solar plant | $578 M |
| Residual train control | $23 M |
| Charging microgrids | $73 M |
| EPC / project services | $1.68 bn |
| **Total city programme** | **$26.23 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $4.46 bn (17.0%) |
| Domestic / local capital | $21.77 bn (83.0%) |
| Annual public construction commitment | $3.70 bn / yr for 7 years |
| Annual post-grace debt service | $3.15 bn / yr |
| External capital saved vs default turnkey sensitivity | $42.75 bn |
| Capital + lifetime external interest saved | $96.35 bn |
| Annual OPEX | $528 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 45 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,773 assets / 9,794 tasks | [`karachi-operations-manifest.json`](operations/karachi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`karachi.toml`](karachi.toml) | Expanded simulator scenario |
| [`karachi.corridor.geojson`](karachi.corridor.geojson) | GIS corridor and stations |
| [`karachi.design-quality.yaml`](karachi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh karachi
```
