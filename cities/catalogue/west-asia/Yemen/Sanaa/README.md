# Sanaa — Urban Rail Network

**Country:** YE · **Population:** 3,937,500 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Sanaa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$6.47 bn (88.2%) of external capital** and **$8.35 bn of external interest**. Capital plus saved interest totals **$14.82 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **192.451 km to 180.924 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **91 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**7 line-local depots** provide **347 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **347 metro-6car trainsets / 2082 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Sanaa rail network on OpenStreetMap](sanaa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 7 / 91 / 12 |
| Route length | 214.1 km double track |
| Direct transfers / reachable line pairs | 81.0% / 100.0% |
| Residents within 800 m radial station catchments | 1,267,499 (2020 raster; 45.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 347 × 6-car `metro-6car` trainsets (312 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 37.3 km | 13 | 72 | NW Outer ↔ SE Mid |
| line-2 | 18.0 km | 9 | 39 | N Mid ↔ SE Mid |
| line-3 | 29.3 km | 12 | 56 | NW Mid ↔ SE Outer |
| line-4 | 22.1 km | 12 | 50 | S Mid ↔ NE Mid |
| line-5 | 31.0 km | 15 | 63 | E Outer ↔ W Mid |
| line-6 | 20.4 km | 9 | 39 | W Outer ↔ SE Inner |
| line-7 | 56.0 km | 21 | 28 | N Mid ↔ N Mid |
| **Total** | **214.1 km** | **91 unique** | **347** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,022 one-way journeys / 86,548 train-km/day |
| Annual traction demand | 818.8 GWh |
| Station/depot PV / storage | 56.6 MW / 424.0 MWh |
| Aggregate charging power | 158.0 MW |
| Dedicated solar plant | 351.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 17.3 km / 250 kWh |
| Lowest traversal charging margin | line-6: 200 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.28 bn |
| Stations | $462 M |
| Depots | $170 M |
| Rolling stock | $583 M |
| Dedicated solar plant | $281 M |
| Residual train control | $11 M |
| Charging microgrids | $32 M |
| EPC / project services | $248 M |
| **Total city programme** | **$4.07 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $863 M (21.2%) |
| Domestic / local capital | $3.21 bn (78.8%) |
| Annual public construction commitment | $565 M / yr for 10 years |
| Annual post-grace debt service | $518 M / yr |
| External capital saved vs default turnkey sensitivity | $6.47 bn |
| Capital + lifetime external interest saved | $14.82 bn |
| Annual OPEX | $91 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 23 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 856 assets / 4,743 tasks | [`sanaa-operations-manifest.json`](operations/sanaa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`sanaa.toml`](sanaa.toml) | Expanded simulator scenario |
| [`sanaa.corridor.geojson`](sanaa.corridor.geojson) | GIS corridor and stations |
| [`sanaa.design-quality.yaml`](sanaa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh sanaa
```
