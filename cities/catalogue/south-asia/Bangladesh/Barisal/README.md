# Barisal — Urban Rail Network

**Country:** BD · **Population:** 550,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Barisal-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.13 bn (88.4%) of external capital** and **$3.93 bn of external interest**. Capital plus saved interest totals **$7.06 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **81.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **49.504 km to 68.005 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **68 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **347 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **347 light-metro-3car trainsets / 1041 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Barisal rail network on OpenStreetMap](barisal-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 68 / 13 |
| Route length | 91.5 km double track |
| Direct transfers / reachable line pairs | 28.9% / 100.0% |
| Residents within 800 m radial station catchments | 513,730 (2020 raster; 67.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 347 × 3-car `light-metro-3car` trainsets (310 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 13.7 km | 7 | 45 | N Mid ↔ S Mid |
| line-2 | 16.0 km | 10 | 53 | NE Mid ↔ S Outer |
| line-3 | 24.7 km | 17 | 87 | NW Outer ↔ SE Mid |
| line-4 |  3.8 km | 6 | 23 | NE Inner ↔ E Inner |
| line-5 |  3.5 km | 4 | 17 | S Mid ↔ S Inner |
| line-6 |  5.3 km | 4 | 21 | NW Mid ↔ N Outer |
| line-7 |  3.3 km | 3 | 14 | N Inner ↔ NE Mid |
| line-8 | 12.3 km | 7 | 45 | S Inner ↔ SW Outer |
| line-9 |  5.3 km | 4 | 19 | S Mid ↔ SE Mid |
| line-10 |  3.5 km | 6 | 23 | NW Inner ↔ NE Inner |
| **Total** | **91.5 km** | **68 unique** | **347** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 42,548 train-km/day |
| Annual traction demand | 201.3 GWh |
| Station/depot PV / storage | 64.1 MW / 447.0 MWh |
| Aggregate charging power | 57.0 MW |
| Dedicated solar plant | 58.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 9.4 km / 70 kWh |
| Lowest traversal charging margin | line-6: 87 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $950 M |
| Stations | $352 M |
| Depots | $167 M |
| Rolling stock | $312 M |
| Dedicated solar plant | $47 M |
| Residual train control | $4.6 M |
| Charging microgrids | $12 M |
| EPC / project services | $126 M |
| **Total city programme** | **$1.97 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $411 M (20.9%) |
| Domestic / local capital | $1.56 bn (79.1%) |
| Annual public construction commitment | $169 M / yr for 7 years |
| Annual post-grace debt service | $138 M / yr |
| External capital saved vs default turnkey sensitivity | $3.13 bn |
| Capital + lifetime external interest saved | $7.06 bn |
| Annual OPEX | $51 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 750 assets / 4,326 tasks | [`barisal-operations-manifest.json`](operations/barisal-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`barisal.toml`](barisal.toml) | Expanded simulator scenario |
| [`barisal.corridor.geojson`](barisal.corridor.geojson) | GIS corridor and stations |
| [`barisal.design-quality.yaml`](barisal.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh barisal
```
