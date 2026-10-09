# Kandy — Urban Rail Network

**Country:** LK · **Population:** 650,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kandy-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.35 bn (88.4%) of external capital** and **$5.45 bn of external interest**. Capital plus saved interest totals **$9.81 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **18 lines**, including **15 additional residential lines**. **64.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **58.907 km to 80.249 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **97 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**18 line-local depots** provide **473 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **473 light-metro-3car trainsets / 1419 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kandy rail network on OpenStreetMap](kandy-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 18 / 97 / 23 |
| Route length | 125.5 km double track |
| Direct transfers / reachable line pairs | 17.0% / 100.0% |
| Residents within 800 m radial station catchments | 337,507 (2020 raster; 48.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 473 × 3-car `light-metro-3car` trainsets (419 peak revenue) |
| Peak network throughput | 259,200 passengers/hour |
| Practical service capacity | 2,410,560 passenger-trips/day |
| Annual paid-trip planning range | 439.9–703.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 22.2 km | 21 | 85 | E Outer ↔ W Outer |
| line-2 | 21.3 km | 15 | 73 | SW Outer ↔ NE Mid |
| line-3 | 19.4 km | 11 | 65 | E Mid ↔ NW Outer |
| line-4 |  2.5 km | 2 | 11 | N Outer ↔ N Outer |
| line-5 |  2.1 km | 2 | 10 | N Inner ↔ N Inner |
| line-6 |  2.3 km | 2 | 10 | NE Mid ↔ N Mid |
| line-7 |  2.4 km | 2 | 10 | N Mid ↔ NW Inner |
| line-8 |  3.3 km | 3 | 14 | SW Mid ↔ W Mid |
| line-9 |  5.6 km | 4 | 21 | SW Outer ↔ SW Mid |
| line-10 |  4.5 km | 4 | 18 | E Mid ↔ NE Mid |
| line-11 |  6.5 km | 5 | 23 | NE Inner ↔ SE Inner |
| line-12 |  5.7 km | 3 | 20 | N Mid ↔ NW Inner |
| line-13 |  5.2 km | 6 | 24 | E Mid ↔ E Outer |
| line-14 |  8.2 km | 5 | 30 | W Mid ↔ SW Outer |
| line-15 |  2.2 km | 3 | 13 | SW Inner ↔ SW Inner |
| line-16 |  4.8 km | 3 | 18 | W Outer ↔ W Mid |
| line-17 |  3.8 km | 3 | 14 | E Inner ↔ NE Mid |
| line-18 |  3.7 km | 3 | 14 | SW Inner ↔ SW Inner |
| **Total** | **125.5 km** | **97 unique** | **473** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 8,370 one-way journeys / 58,380 train-km/day |
| Annual traction demand | 276.2 GWh |
| Station/depot PV / storage | 110.7 MW / 754.5 MWh |
| Aggregate charging power | 43.5 MW |
| Dedicated solar plant | 54.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-14: 8.2 km / 61 kWh |
| Lowest traversal charging margin | line-16: 18 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.22 bn |
| Stations | $578 M |
| Depots | $276 M |
| Rolling stock | $426 M |
| Dedicated solar plant | $43 M |
| Residual train control | $6.3 M |
| Charging microgrids | $9.2 M |
| EPC / project services | $176 M |
| **Total city programme** | **$2.73 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $569 M (20.8%) |
| Domestic / local capital | $2.16 bn (79.2%) |
| Annual public construction commitment | $321 M / yr for 7 years |
| Annual post-grace debt service | $271 M / yr |
| External capital saved vs default turnkey sensitivity | $4.35 bn |
| Capital + lifetime external interest saved | $9.81 bn |
| Annual OPEX | $75 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,056 assets / 5,980 tasks | [`kandy-operations-manifest.json`](operations/kandy-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kandy.toml`](kandy.toml) | Expanded simulator scenario |
| [`kandy.corridor.geojson`](kandy.corridor.geojson) | GIS corridor and stations |
| [`kandy.design-quality.yaml`](kandy.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kandy
```
