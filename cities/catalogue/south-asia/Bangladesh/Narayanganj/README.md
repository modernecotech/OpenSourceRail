# Narayanganj — Urban Rail Network

**Country:** BD · **Population:** 950,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Narayanganj-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.94 bn (88.5%) of external capital** and **$6.20 bn of external interest**. Capital plus saved interest totals **$11.14 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **19 lines**, including **16 additional residential lines**. **77.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **49.865 km to 73.983 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **103 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**19 line-local depots** provide **533 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **533 light-metro-3car trainsets / 1599 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Narayanganj rail network on OpenStreetMap](narayanganj-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 19 / 103 / 23 |
| Route length | 150.0 km double track |
| Direct transfers / reachable line pairs | 12.9% / 100.0% |
| Residents within 800 m radial station catchments | 3,787,975 (2020 raster; 62.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 533 × 3-car `light-metro-3car` trainsets (472 peak revenue) |
| Peak network throughput | 273,600 passengers/hour |
| Practical service capacity | 2,544,480 passenger-trips/day |
| Annual paid-trip planning range | 464.4–743.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.5 km | 22 | 115 | SE Outer ↔ NW Outer |
| line-2 | 23.1 km | 13 | 72 | NW Outer ↔ E Outer |
| line-3 | 19.0 km | 12 | 64 | S Outer ↔ NE Mid |
| line-4 |  2.0 km | 2 | 10 | NW Mid ↔ N Mid |
| line-5 |  4.1 km | 3 | 15 | NW Mid ↔ NW Mid |
| line-6 |  3.9 km | 3 | 15 | NE Inner ↔ N Mid |
| line-7 |  6.7 km | 4 | 23 | N Mid ↔ SE Inner |
| line-8 |  6.3 km | 5 | 23 | NW Mid ↔ NW Outer |
| line-9 |  6.1 km | 4 | 21 | N Inner ↔ NE Mid |
| line-10 |  3.2 km | 3 | 14 | SE Inner ↔ S Inner |
| line-11 |  6.7 km | 4 | 23 | NE Mid ↔ NE Mid |
| line-12 |  3.5 km | 3 | 14 | SE Mid ↔ SE Mid |
| line-13 |  2.8 km | 2 | 11 | SE Outer ↔ S Outer |
| line-14 |  3.1 km | 2 | 12 | SE Inner ↔ SE Mid |
| line-15 |  3.0 km | 2 | 12 | NE Inner ↔ E Inner |
| line-16 |  3.6 km | 3 | 14 | S Outer ↔ S Outer |
| line-17 |  4.2 km | 4 | 17 | SW Inner ↔ S Inner |
| line-18 |  9.5 km | 8 | 37 | NW Mid ↔ NW Inner |
| line-19 |  5.9 km | 4 | 21 | E Outer ↔ E Outer |
| **Total** | **150.0 km** | **103 unique** | **533** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 8,835 one-way journeys / 69,770 train-km/day |
| Annual traction demand | 330.0 GWh |
| Station/depot PV / storage | 118.7 MW / 799.5 MWh |
| Aggregate charging power | 49.0 MW |
| Dedicated solar plant | 80.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-18: 6.4 km / 48 kWh |
| Lowest traversal charging margin | line-14: 23 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.49 bn |
| Stations | $556 M |
| Depots | $297 M |
| Rolling stock | $480 M |
| Dedicated solar plant | $64 M |
| Residual train control | $7.5 M |
| Charging microgrids | $10 M |
| EPC / project services | $199 M |
| **Total city programme** | **$3.10 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $643 M (20.7%) |
| Domestic / local capital | $2.46 bn (79.3%) |
| Annual public construction commitment | $267 M / yr for 7 years |
| Annual post-grace debt service | $217 M / yr |
| External capital saved vs default turnkey sensitivity | $4.94 bn |
| Capital + lifetime external interest saved | $11.14 bn |
| Annual OPEX | $81 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 26 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,162 assets / 6,654 tasks | [`narayanganj-operations-manifest.json`](operations/narayanganj-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`narayanganj.toml`](narayanganj.toml) | Expanded simulator scenario |
| [`narayanganj.corridor.geojson`](narayanganj.corridor.geojson) | GIS corridor and stations |
| [`narayanganj.design-quality.yaml`](narayanganj.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh narayanganj
```
