# Aleppo — Urban Rail Network

**Country:** SY · **Population:** 1,639,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Aleppo-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$7.43 bn (88.5%) of external capital** and **$9.59 bn of external interest**. Capital plus saved interest totals **$17.02 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **22 lines**, including **16 additional residential lines**. **78.2%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **160.184 km to 201.349 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **167 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**22 line-local depots** provide **503 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **503 metro-4car trainsets / 2012 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Aleppo rail network on OpenStreetMap](aleppo-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 22 / 167 / 46 |
| Route length | 255.6 km double track |
| Direct transfers / reachable line pairs | 21.2% / 100.0% |
| Residents within 800 m radial station catchments | 2,078,582 (2020 raster; 62.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 503 × 4-car `metro-4car` trainsets (444 peak revenue) |
| Peak network throughput | 422,400 passengers/hour |
| Practical service capacity | 3,839,040 passenger-trips/day |
| Annual paid-trip planning range | 700.6–1121.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.6 km | 15 | 50 | SW Outer ↔ E Mid |
| line-2 | 24.2 km | 15 | 52 | SE Outer ↔ NW Outer |
| line-3 | 13.2 km | 9 | 31 | NE Inner ↔ SW Mid |
| line-4 | 20.7 km | 13 | 46 | W Outer ↔ E Mid |
| line-5 | 23.9 km | 15 | 52 | N Mid ↔ S Outer |
| line-6 | 54.4 km | 33 | 29 | W Mid ↔ W Mid |
| line-7 |  6.5 km | 5 | 18 | W Inner ↔ NW Inner |
| line-8 |  6.9 km | 5 | 18 | NE Mid ↔ NE Inner |
| line-9 |  5.2 km | 3 | 13 | SE Inner ↔ S Mid |
| line-10 |  6.4 km | 4 | 15 | NE Mid ↔ NE Outer |
| line-11 |  3.3 km | 3 | 11 | E Mid ↔ E Outer |
| line-12 |  4.7 km | 3 | 11 | SW Mid ↔ W Outer |
| line-13 |  7.6 km | 5 | 18 | NW Mid ↔ SW Inner |
| line-14 |  4.5 km | 4 | 14 | E Mid ↔ NE Mid |
| line-15 |  4.8 km | 3 | 11 | NE Mid ↔ N Outer |
| line-16 |  4.4 km | 3 | 12 | N Mid ↔ N Inner |
| line-17 |  6.3 km | 6 | 19 | NW Inner ↔ NE Inner |
| line-18 |  3.9 km | 3 | 12 | NE Mid ↔ NE Outer |
| line-19 | 10.0 km | 7 | 25 | S Mid ↔ E Inner |
| line-20 |  7.8 km | 4 | 16 | W Outer ↔ SW Outer |
| line-21 |  3.9 km | 3 | 11 | NW Mid ↔ NW Outer |
| line-22 |  9.5 km | 6 | 19 | E Mid ↔ E Outer |
| **Total** | **255.6 km** | **167 unique** | **503** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 9,998 one-way journeys / 106,208 train-km/day |
| Annual traction demand | 669.9 GWh |
| Station/depot PV / storage | 148.1 MW / 1,070.5 MWh |
| Aggregate charging power | 223.5 MW |
| Dedicated solar plant | 213.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 7.2 km / 69 kWh |
| Lowest traversal charging margin | line-22: 96 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.24 bn |
| Stations | $978 M |
| Depots | $353 M |
| Rolling stock | $563 M |
| Dedicated solar plant | $171 M |
| Residual train control | $13 M |
| Charging microgrids | $46 M |
| EPC / project services | $294 M |
| **Total city programme** | **$4.66 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $963 M (20.7%) |
| Domestic / local capital | $3.70 bn (79.3%) |
| Annual public construction commitment | $709 M / yr for 10 years |
| Annual post-grace debt service | $653 M / yr |
| External capital saved vs default turnkey sensitivity | $7.43 bn |
| Capital + lifetime external interest saved | $17.02 bn |
| Annual OPEX | $104 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 19 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,439 assets / 7,469 tasks | [`aleppo-operations-manifest.json`](operations/aleppo-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`aleppo.toml`](aleppo.toml) | Expanded simulator scenario |
| [`aleppo.corridor.geojson`](aleppo.corridor.geojson) | GIS corridor and stations |
| [`aleppo.design-quality.yaml`](aleppo.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh aleppo
```
