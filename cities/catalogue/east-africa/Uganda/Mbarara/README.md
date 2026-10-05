# Mbarara — Urban Rail Network

**Country:** UG · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mbarara-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.33 bn (88.4%) of external capital** and **$1.66 bn of external interest**. Capital plus saved interest totals **$2.99 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **48.265 km to 43.316 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **18 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **150 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **150 light-metro-3car trainsets / 450 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mbarara rail network on OpenStreetMap](mbarara-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 18 / 3 |
| Route length | 48.0 km double track |
| Direct transfers / reachable line pairs | 100.0% / 100.0% |
| Residents within 800 m radial station catchments | 54,661 (2020 raster; 22.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 150 × 3-car `light-metro-3car` trainsets (135 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.2 km | 4 | 31 | E Mid ↔ SW Mid |
| line-2 | 13.0 km | 6 | 40 | NW Outer ↔ SE Inner |
| line-3 | 24.7 km | 8 | 79 | SW Outer ↔ NE Outer |
| **Total** | **48.0 km** | **18 unique** | **150** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 22,298 train-km/day |
| Annual traction demand | 105.5 GWh |
| Station/depot PV / storage | 18.9 MW / 126.5 MWh |
| Aggregate charging power | 8.0 MW |
| Dedicated solar plant | 47.5 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 10.1 km / 75 kWh |
| Lowest traversal charging margin | line-1: 30 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $461 M |
| Stations | $87 M |
| Depots | $57 M |
| Rolling stock | $135 M |
| Dedicated solar plant | $38 M |
| Residual train control | $2.4 M |
| Charging microgrids | $1.8 M |
| EPC / project services | $52 M |
| **Total city programme** | **$834 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $175 M (21.0%) |
| Domestic / local capital | $659 M (79.0%) |
| Annual public construction commitment | $100 M / yr for 7 years |
| Annual post-grace debt service | $85 M / yr |
| External capital saved vs default turnkey sensitivity | $1.33 bn |
| Capital + lifetime external interest saved | $2.99 bn |
| Annual OPEX | $20 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 4 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 268 assets / 1,680 tasks | [`mbarara-operations-manifest.json`](operations/mbarara-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mbarara.toml`](mbarara.toml) | Expanded simulator scenario |
| [`mbarara.corridor.geojson`](mbarara.corridor.geojson) | GIS corridor and stations |
| [`mbarara.design-quality.yaml`](mbarara.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mbarara
```
