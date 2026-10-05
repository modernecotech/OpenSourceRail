# Meerut — Urban Rail Network

**Country:** IN · **Population:** 1,600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Meerut-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.10 bn (89.1%) of external capital** and **$3.81 bn of external interest**. Capital plus saved interest totals **$6.91 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **126.364 km to 114.037 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **46 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**4 line-local depots** provide **150 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **150 metro-4car trainsets / 600 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md).

## Network

![Meerut rail network on OpenStreetMap](meerut-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 4 / 46 / 10 |
| Route length | 127.2 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 150 × 4-car `metro-4car` trainsets (134 peak revenue) |
| Peak network throughput | 76,800 passengers/hour |
| Practical service capacity | 624,960 passenger-trips/day |
| Annual paid-trip planning range | 114.1–182.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 21.7 km | 10 | 40 | NW Outer ↔ SE Mid |
| line-2 | 26.9 km | 11 | 46 | N Outer ↔ S Outer |
| line-3 | 25.1 km | 8 | 41 | SW Outer ↔ NE Mid |
| line-4 | 53.4 km | 17 | 23 | N Mid ↔ NW Mid |
| **Total** | **127.2 km** | **46 unique** | **150** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,628 one-way journeys / 46,730 train-km/day |
| Annual traction demand | 294.7 GWh |
| Station/depot PV / storage | 31.1 MW / 215.5 MWh |
| Aggregate charging power | 61.5 MW |
| Dedicated solar plant | 119.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.6 km / 103 kWh |
| Lowest traversal charging margin | line-3: 156 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.20 bn |
| Stations | $258 M |
| Depots | $76 M |
| Rolling stock | $168 M |
| Dedicated solar plant | $95 M |
| Residual train control | $6.4 M |
| Charging microgrids | $13 M |
| EPC / project services | $120 M |
| **Total city programme** | **$1.93 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $378 M (19.6%) |
| Domestic / local capital | $1.55 bn (80.4%) |
| Annual public construction commitment | $169 M / yr for 5 years |
| Annual post-grace debt service | $120 M / yr |
| External capital saved vs default turnkey sensitivity | $3.10 bn |
| Capital + lifetime external interest saved | $6.91 bn |
| Annual OPEX | $45 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 405 assets / 2,167 tasks | [`meerut-operations-manifest.json`](operations/meerut-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`meerut.toml`](meerut.toml) | Expanded simulator scenario |
| [`meerut.corridor.geojson`](meerut.corridor.geojson) | GIS corridor and stations |
| [`meerut.design-quality.yaml`](meerut.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh meerut
```
