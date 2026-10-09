# Lubumbashi — Urban Rail Network

**Country:** CD · **Population:** 2,829,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Lubumbashi-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.16 bn (88.4%) of external capital** and **$9.25 bn of external interest**. Capital plus saved interest totals **$16.40 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **30 lines**, including **25 additional residential lines**. **55.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **110.198 km to 199.465 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **159 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**30 line-local depots** provide **508 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **508 metro-4car trainsets / 2032 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Lubumbashi rail network on OpenStreetMap](lubumbashi-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 30 / 159 / 40 |
| Route length | 231.6 km double track |
| Direct transfers / reachable line pairs | 11.5% / 100.0% |
| Residents within 800 m radial station catchments | 1,712,216 (2020 raster; 40.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 508 × 4-car `metro-4car` trainsets (436 peak revenue) |
| Peak network throughput | 576,000 passengers/hour |
| Practical service capacity | 5,267,520 passenger-trips/day |
| Annual paid-trip planning range | 961.3–1538.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 19.5 km | 12 | 43 | NE Mid ↔ S Mid |
| line-2 | 16.4 km | 9 | 35 | W Mid ↔ E Mid |
| line-3 | 12.3 km | 10 | 34 | N Mid ↔ W Mid |
| line-4 | 24.5 km | 15 | 49 | SE Mid ↔ N Outer |
| line-5 | 43.8 km | 26 | 24 | NW Mid ↔ W Mid |
| line-6 |  6.4 km | 4 | 15 | E Inner ↔ SW Inner |
| line-7 |  2.4 km | 2 | 9 | E Mid ↔ E Mid |
| line-8 |  3.1 km | 3 | 11 | S Inner ↔ S Mid |
| line-9 |  3.6 km | 3 | 11 | N Inner ↔ NW Inner |
| line-10 |  3.6 km | 3 | 11 | S Inner ↔ S Mid |
| line-11 |  3.3 km | 3 | 11 | SW Inner ↔ W Inner |
| line-12 |  4.7 km | 4 | 14 | N Inner ↔ N Mid |
| line-13 |  3.1 km | 2 | 9 | E Inner ↔ SE Inner |
| line-14 |  3.3 km | 3 | 10 | W Mid ↔ W Mid |
| line-15 |  2.8 km | 3 | 10 | SW Mid ↔ SW Mid |
| line-16 |  2.4 km | 2 | 9 | NW Inner ↔ NW Mid |
| line-17 |  4.3 km | 3 | 11 | S Mid ↔ SE Mid |
| line-18 |  6.4 km | 5 | 17 | E Mid ↔ E Outer |
| line-19 |  9.7 km | 6 | 23 | N Mid ↔ NE Mid |
| line-20 |  4.1 km | 4 | 14 | SW Inner ↔ W Inner |
| line-21 |  2.6 km | 2 | 9 | S Mid ↔ SW Mid |
| line-22 |  2.9 km | 2 | 9 | S Mid ↔ S Mid |
| line-23 | 10.8 km | 7 | 26 | S Mid ↔ SW Inner |
| line-24 |  4.3 km | 3 | 12 | E Mid ↔ SE Mid |
| line-25 |  6.9 km | 6 | 20 | E Mid ↔ NE Mid |
| line-26 |  4.9 km | 3 | 11 | W Mid ↔ SW Mid |
| line-27 |  3.7 km | 3 | 11 | S Mid ↔ S Outer |
| line-28 |  5.9 km | 5 | 16 | N Mid ↔ N Mid |
| line-29 |  5.0 km | 3 | 12 | SE Mid ↔ SE Mid |
| line-30 |  4.9 km | 3 | 12 | NW Inner ↔ NW Mid |
| **Total** | **231.6 km** | **159 unique** | **508** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 13,718 one-way journeys / 97,540 train-km/day |
| Annual traction demand | 615.2 GWh |
| Station/depot PV / storage | 184.2 MW / 1,371.0 MWh |
| Aggregate charging power | 216.0 MW |
| Dedicated solar plant | 192.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 9.7 km / 97 kWh |
| Lowest traversal charging margin | line-29: 92 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.15 bn |
| Stations | $840 M |
| Depots | $446 M |
| Rolling stock | $569 M |
| Dedicated solar plant | $154 M |
| Residual train control | $12 M |
| Charging microgrids | $44 M |
| EPC / project services | $284 M |
| **Total city programme** | **$4.50 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $936 M (20.8%) |
| Domestic / local capital | $3.56 bn (79.2%) |
| Annual public construction commitment | $484 M / yr for 10 years |
| Annual post-grace debt service | $437 M / yr |
| External capital saved vs default turnkey sensitivity | $7.16 bn |
| Capital + lifetime external interest saved | $16.40 bn |
| Annual OPEX | $105 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 23 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,424 assets / 7,359 tasks | [`lubumbashi-operations-manifest.json`](operations/lubumbashi-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`lubumbashi.toml`](lubumbashi.toml) | Expanded simulator scenario |
| [`lubumbashi.corridor.geojson`](lubumbashi.corridor.geojson) | GIS corridor and stations |
| [`lubumbashi.design-quality.yaml`](lubumbashi.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh lubumbashi
```
