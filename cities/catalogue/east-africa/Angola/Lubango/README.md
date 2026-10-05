# Lubango — Urban Rail Network

**Country:** AO · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lubango-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.22 bn (88.6%) of external capital** and **$1.50 bn of external interest**. Capital plus saved interest totals **$2.72 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **48.707 km to 40.372 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **14 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**3 line-local depots** provide **138 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **138 light-metro-3car trainsets / 414 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Lubango rail network on OpenStreetMap](lubango-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 3 / 14 / 2 |
| Route length | 44.8 km double track |
| Direct transfers / reachable line pairs | 66.7% / 100.0% |
| Residents within 800 m radial station catchments | 54,948 (2020 raster; 9.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 138 × 3-car `light-metro-3car` trainsets (124 peak revenue) |
| Peak network throughput | 43,200 passengers/hour |
| Practical service capacity | 401,760 passenger-trips/day |
| Annual paid-trip planning range | 73.3–117.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.4 km | 4 | 42 | NW Mid ↔ E Mid |
| line-2 | 20.1 km | 6 | 61 | SW Mid ↔ NE Outer |
| line-3 | 11.3 km | 4 | 35 | W Mid ↔ SE Mid |
| **Total** | **44.8 km** | **14 unique** | **138** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 1,395 one-way journeys / 20,828 train-km/day |
| Annual traction demand | 98.5 GWh |
| Station/depot PV / storage | 18.0 MW / 130.0 MWh |
| Aggregate charging power | 13.0 MW |
| Dedicated solar plant | 27.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.4 km / 95 kWh |
| Lowest traversal charging margin | line-3: 157 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $442 M |
| Stations | $68 M |
| Depots | $55 M |
| Rolling stock | $124 M |
| Dedicated solar plant | $22 M |
| Residual train control | $2.2 M |
| Charging microgrids | $2.9 M |
| EPC / project services | $49 M |
| **Total city programme** | **$764 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $156 M (20.5%) |
| Domestic / local capital | $608 M (79.5%) |
| Annual public construction commitment | $87 M / yr for 5 years |
| Annual post-grace debt service | $66 M / yr |
| External capital saved vs default turnkey sensitivity | $1.22 bn |
| Capital + lifetime external interest saved | $2.72 bn |
| Annual OPEX | $20 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 235 assets / 1,502 tasks | [`lubango-operations-manifest.json`](operations/lubango-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lubango.toml`](lubango.toml) | Expanded simulator scenario |
| [`lubango.corridor.geojson`](lubango.corridor.geojson) | GIS corridor and stations |
| [`lubango.design-quality.yaml`](lubango.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lubango
```
