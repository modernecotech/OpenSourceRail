# Omdurman — Urban Rail Network

**Country:** SD · **Population:** 2,800,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Omdurman-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$14.51 bn (88.4%) of external capital** and **$18.74 bn of external interest**. Capital plus saved interest totals **$33.26 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **40 lines**, including **34 additional residential lines**. **65.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **193.147 km to 270.849 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **350 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**40 line-local depots** provide **1054 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **1054 metro-4car trainsets / 4216 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Omdurman rail network on OpenStreetMap](omdurman-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 40 / 350 / 91 |
| Route length | 487.7 km double track |
| Direct transfers / reachable line pairs | 13.8% / 100.0% |
| Residents within 800 m radial station catchments | 1,395,536 (2020 raster; 50.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 1054 × 4-car `metro-4car` trainsets (939 peak revenue) |
| Peak network throughput | 768,000 passengers/hour |
| Practical service capacity | 7,053,120 passenger-trips/day |
| Annual paid-trip planning range | 1287.2–2059.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 32.5 km | 23 | 78 | SE Outer ↔ N Mid |
| line-2 | 40.1 km | 24 | 83 | NE Mid ↔ SW Outer |
| line-3 | 33.6 km | 20 | 72 | N Outer ↔ SE Outer |
| line-4 | 29.6 km | 23 | 74 | W Mid ↔ E Outer |
| line-5 | 23.4 km | 16 | 56 | E Outer ↔ W Mid |
| line-6 | 81.5 km | 50 | 45 | W Mid ↔ W Mid |
| line-7 |  5.0 km | 4 | 14 | SE Mid ↔ S Mid |
| line-8 |  5.7 km | 5 | 17 | NW Mid ↔ NW Inner |
| line-9 |  6.5 km | 7 | 21 | SE Mid ↔ SE Outer |
| line-10 |  7.3 km | 6 | 20 | W Mid ↔ W Mid |
| line-11 |  5.7 km | 4 | 15 | W Inner ↔ NW Inner |
| line-12 |  5.1 km | 5 | 16 | E Mid ↔ E Mid |
| line-13 |  6.9 km | 5 | 18 | SE Mid ↔ S Mid |
| line-14 |  6.8 km | 4 | 16 | NW Inner ↔ NW Mid |
| line-15 |  6.8 km | 4 | 16 | N Inner ↔ N Mid |
| line-16 |  8.9 km | 9 | 28 | SE Mid ↔ SE Outer |
| line-17 |  7.1 km | 4 | 16 | SE Mid ↔ SE Inner |
| line-18 |  6.2 km | 7 | 20 | W Mid ↔ W Outer |
| line-19 |  7.3 km | 6 | 18 | W Mid ↔ W Mid |
| line-20 |  4.9 km | 4 | 13 | N Mid ↔ N Outer |
| line-21 |  7.3 km | 5 | 17 | NW Mid ↔ NW Outer |
| line-22 | 12.4 km | 8 | 28 | W Mid ↔ NW Mid |
| line-23 | 10.6 km | 5 | 20 | S Mid ↔ SE Outer |
| line-24 |  7.6 km | 5 | 17 | N Outer ↔ N Outer |
| line-25 |  5.4 km | 5 | 15 | SE Outer ↔ SE Outer |
| line-26 |  7.6 km | 4 | 15 | N Mid ↔ NW Outer |
| line-27 |  7.6 km | 6 | 20 | SW Mid ↔ W Mid |
| line-28 | 11.6 km | 9 | 30 | SE Mid ↔ SE Outer |
| line-29 |  9.2 km | 7 | 23 | W Mid ↔ W Outer |
| line-30 |  8.0 km | 9 | 27 | W Mid ↔ NW Mid |
| line-31 |  9.5 km | 6 | 20 | SE Outer ↔ S Mid |
| line-32 |  7.0 km | 6 | 19 | W Mid ↔ W Outer |
| line-33 | 10.7 km | 9 | 27 | W Mid ↔ NW Outer |
| line-34 |  4.9 km | 4 | 14 | N Mid ↔ NE Mid |
| line-35 |  6.0 km | 6 | 18 | SE Outer ↔ SE Outer |
| line-36 |  5.5 km | 4 | 15 | N Mid ↔ NW Outer |
| line-37 |  5.9 km | 7 | 20 | SE Mid ↔ SE Mid |
| line-38 |  6.5 km | 5 | 17 | N Mid ↔ N Mid |
| line-39 |  6.6 km | 5 | 18 | SE Mid ↔ E Mid |
| line-40 |  6.9 km | 5 | 18 | E Inner ↔ E Inner |
| **Total** | **487.7 km** | **350 unique** | **1054** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 18,368 one-way journeys / 207,834 train-km/day |
| Annual traction demand | 1,310.9 GWh |
| Station/depot PV / storage | 283.4 MW / 2,017.0 MWh |
| Aggregate charging power | 477.0 MW |
| Dedicated solar plant | 362.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-33: 7.6 km / 82 kWh |
| Lowest traversal charging margin | line-24: 57 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $4.06 bn |
| Stations | $2.21 bn |
| Depots | $668 M |
| Rolling stock | $1.18 bn |
| Dedicated solar plant | $290 M |
| Residual train control | $24 M |
| Charging microgrids | $100 M |
| EPC / project services | $578 M |
| **Total city programme** | **$9.12 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.90 bn (20.9%) |
| Domestic / local capital | $7.22 bn (79.1%) |
| Annual public construction commitment | $1.10 bn / yr for 10 years |
| Annual post-grace debt service | $996 M / yr |
| External capital saved vs default turnkey sensitivity | $14.51 bn |
| Capital + lifetime external interest saved | $33.26 bn |
| Annual OPEX | $212 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 54 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 3,010 assets / 15,695 tasks | [`omdurman-operations-manifest.json`](operations/omdurman-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`omdurman.toml`](omdurman.toml) | Expanded simulator scenario |
| [`omdurman.corridor.geojson`](omdurman.corridor.geojson) | GIS corridor and stations |
| [`omdurman.design-quality.yaml`](omdurman.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh omdurman
```
