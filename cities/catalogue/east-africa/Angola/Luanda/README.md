# Luanda — Urban Rail Network

**Country:** AO · **Population:** 9,085,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Luanda-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$24.42 bn (87.2%) of external capital** and **$30.02 bn of external interest**. Capital plus saved interest totals **$54.45 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **45 lines**, including **36 additional residential lines**. **75.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **315.474 km to 566.477 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **507 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**45 line-local depots** provide **1734 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **1734 metro-6car trainsets / 10404 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Luanda rail network on OpenStreetMap](luanda-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 45 / 507 / 147 |
| Route length | 686.6 km double track |
| Direct transfers / reachable line pairs | 17.2% / 100.0% |
| Residents within 800 m radial station catchments | 9,355,600 (2020 raster; 60.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 1734 × 6-car `metro-6car` trainsets (1555 peak revenue) |
| Peak network throughput | 1,296,000 passengers/hour |
| Practical service capacity | 11,918,880 passenger-trips/day |
| Annual paid-trip planning range | 2175.2–3480.3 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 52.4 km | 36 | 129 | NE Outer ↔ SW Outer |
| line-2 | 26.8 km | 25 | 86 | W Mid ↔ N Mid |
| line-3 | 39.2 km | 25 | 94 | SW Outer ↔ NE Mid |
| line-4 | 47.0 km | 29 | 111 | NW Mid ↔ SE Outer |
| line-5 | 37.9 km | 29 | 104 | SE Outer ↔ NW Mid |
| line-6 | 27.1 km | 20 | 71 | N Mid ↔ S Mid |
| line-7 | 31.7 km | 22 | 80 | E Outer ↔ NW Mid |
| line-8 | 31.7 km | 22 | 79 | NE Outer ↔ W Mid |
| line-9 | 65.8 km | 49 | 46 | NE Mid ↔ NE Mid |
| line-10 |  6.8 km | 7 | 25 | W Mid ↔ W Inner |
| line-11 |  6.9 km | 5 | 20 | N Inner ↔ N Mid |
| line-12 |  9.6 km | 7 | 27 | N Mid ↔ NW Mid |
| line-13 |  9.2 km | 8 | 29 | SE Inner ↔ N Inner |
| line-14 |  6.7 km | 5 | 18 | SW Mid ↔ SW Mid |
| line-15 |  6.8 km | 7 | 25 | W Mid ↔ W Inner |
| line-16 | 10.9 km | 7 | 28 | W Mid ↔ NW Mid |
| line-17 | 10.7 km | 7 | 28 | SE Inner ↔ W Inner |
| line-18 |  7.0 km | 6 | 21 | E Mid ↔ SE Mid |
| line-19 |  7.3 km | 8 | 28 | SE Mid ↔ E Mid |
| line-20 |  6.4 km | 5 | 19 | SE Inner ↔ NE Inner |
| line-21 | 11.4 km | 13 | 43 | NW Mid ↔ W Inner |
| line-22 |  6.8 km | 4 | 16 | SE Mid ↔ SE Mid |
| line-23 |  6.1 km | 5 | 18 | SE Inner ↔ S Mid |
| line-24 |  7.7 km | 6 | 21 | NE Outer ↔ NE Mid |
| line-25 |  9.9 km | 6 | 25 | W Mid ↔ SW Mid |
| line-26 |  6.2 km | 5 | 19 | N Mid ↔ N Mid |
| line-27 | 12.9 km | 9 | 35 | SW Inner ↔ E Mid |
| line-28 |  6.6 km | 6 | 21 | SE Mid ↔ E Mid |
| line-29 |  8.0 km | 6 | 20 | SW Outer ↔ SW Mid |
| line-30 |  9.7 km | 6 | 24 | SE Mid ↔ E Mid |
| line-31 |  7.4 km | 5 | 18 | SE Mid ↔ SE Mid |
| line-32 | 13.6 km | 11 | 40 | SW Inner ↔ NE Inner |
| line-33 | 11.4 km | 10 | 36 | SW Mid ↔ W Mid |
| line-34 |  6.1 km | 4 | 17 | NE Inner ↔ E Inner |
| line-35 |  7.8 km | 6 | 24 | SW Inner ↔ SE Inner |
| line-36 |  6.2 km | 4 | 16 | SW Outer ↔ SW Mid |
| line-37 | 11.2 km | 8 | 31 | E Mid ↔ N Inner |
| line-38 | 13.5 km | 9 | 36 | N Mid ↔ NE Mid |
| line-39 |  6.3 km | 6 | 21 | SW Inner ↔ W Mid |
| line-40 | 10.2 km | 8 | 30 | NE Mid ↔ N Inner |
| line-41 | 11.6 km | 6 | 26 | SW Mid ↔ SW Mid |
| line-42 | 10.4 km | 8 | 27 | SE Mid ↔ SE Mid |
| line-43 |  8.0 km | 5 | 19 | SE Outer ↔ SE Mid |
| line-44 | 12.4 km | 9 | 35 | S Inner ↔ W Mid |
| line-45 | 17.3 km | 13 | 48 | E Mid ↔ SE Inner |
| **Total** | **686.6 km** | **507 unique** | **1734** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 20,692 one-way journeys / 303,950 train-km/day |
| Annual traction demand | 2,875.6 GWh |
| Station/depot PV / storage | 348.3 MW / 2,622.0 MWh |
| Aggregate charging power | 912.0 MW |
| Dedicated solar plant | 1,487.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 9.8 km / 147 kWh |
| Lowest traversal charging margin | line-43: 64 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $6.11 bn |
| Stations | $3.22 bn |
| Depots | $969 M |
| Rolling stock | $2.91 bn |
| Dedicated solar plant | $1.19 bn |
| Residual train control | $34 M |
| Charging microgrids | $185 M |
| EPC / project services | $940 M |
| **Total city programme** | **$15.56 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $3.59 bn (23.1%) |
| Domestic / local capital | $11.97 bn (76.9%) |
| Annual public construction commitment | $1.74 bn / yr for 5 years |
| Annual post-grace debt service | $1.33 bn / yr |
| External capital saved vs default turnkey sensitivity | $24.42 bn |
| Capital + lifetime external interest saved | $54.45 bn |
| Annual OPEX | $406 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 41 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 4,568 assets / 24,652 tasks | [`luanda-operations-manifest.json`](operations/luanda-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`luanda.toml`](luanda.toml) | Expanded simulator scenario |
| [`luanda.corridor.geojson`](luanda.corridor.geojson) | GIS corridor and stations |
| [`luanda.design-quality.yaml`](luanda.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh luanda
```
