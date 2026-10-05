# Indore — Urban Rail Network

**Country:** IN · **Population:** 3,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Indore-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.67 bn (87.8%) of external capital** and **$10.65 bn of external interest**. Capital plus saved interest totals **$19.32 bn**. See the common reference for interpretation and limitations.

**Current alignment, depot and production basis.** Core corridors change from **300.920 km to 268.176 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **126 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **516 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **516 metro-6car trainsets / 3096 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Indore rail network on OpenStreetMap](indore-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 126 / 20 |
| Route length | 328.2 km double track |
| Direct transfers / reachable line pairs | 85.7% / 100.0% |
| Residents within 800 m radial station catchments | unavailable — native population evidence required |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 516 × 6-car `metro-6car` trainsets (465 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 36.1 km | 17 | 74 | NE Mid ↔ SW Outer |
| line-2 | 34.9 km | 13 | 68 | S Outer ↔ N Mid |
| line-3 | 35.5 km | 12 | 69 | NW Mid ↔ S Outer |
| line-4 | 35.3 km | 15 | 67 | SE Outer ↔ NW Mid |
| line-5 | 38.6 km | 14 | 76 | S Inner ↔ NE Outer |
| line-6 | 29.2 km | 12 | 54 | NW Inner ↔ E Mid |
| line-7 | 35.8 km | 16 | 70 | SW Outer ↔ NE Inner |
| line-8 | 82.8 km | 27 | 38 | NW Mid ↔ NW Mid |
| **Total** | **328.2 km** | **126 unique** | **516** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,488 one-way journeys / 133,347 train-km/day |
| Annual traction demand | 1,261.6 GWh |
| Station/depot PV / storage | 69.7 MW / 518.0 MWh |
| Aggregate charging power | 212.0 MW |
| Dedicated solar plant | 582.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 19.6 km / 316 kWh |
| Lowest traversal charging margin | line-6: 201 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.92 bn |
| Stations | $620 M |
| Depots | $229 M |
| Rolling stock | $867 M |
| Dedicated solar plant | $466 M |
| Residual train control | $16 M |
| Charging microgrids | $43 M |
| EPC / project services | $328 M |
| **Total city programme** | **$5.48 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.21 bn (22.0%) |
| Domestic / local capital | $4.28 bn (78.0%) |
| Annual public construction commitment | $472 M / yr for 5 years |
| Annual post-grace debt service | $339 M / yr |
| External capital saved vs default turnkey sensitivity | $8.67 bn |
| Capital + lifetime external interest saved | $19.32 bn |
| Annual OPEX | $134 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 33 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,220 assets / 6,888 tasks | [`indore-operations-manifest.json`](operations/indore-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`indore.toml`](indore.toml) | Expanded simulator scenario |
| [`indore.corridor.geojson`](indore.corridor.geojson) | GIS corridor and stations |
| [`indore.design-quality.yaml`](indore.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh indore
```
