# Chittagong — Urban Rail Network

**Country:** BD · **Population:** 5,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Chittagong-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$12.28 bn (87.6%) of external capital** and **$15.40 bn of external interest**. Capital plus saved interest totals **$27.68 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **12 lines**, including **4 additional residential lines**. **48.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **257.102 km to 316.570 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **191 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **725 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **725 metro-6car trainsets / 4350 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Chittagong rail network on OpenStreetMap](chittagong-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 191 / 42 |
| Route length | 380.6 km double track |
| Direct transfers / reachable line pairs | 43.9% / 100.0% |
| Residents within 800 m radial station catchments | 1,967,609 (2020 raster; 35.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 725 × 6-car `metro-6car` trainsets (653 peak revenue) |
| Peak network throughput | 345,600 passengers/hour |
| Practical service capacity | 3,080,160 passenger-trips/day |
| Annual paid-trip planning range | 562.1–899.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 47.1 km | 13 | 87 | S Mid ↔ NW Outer |
| line-2 | 31.9 km | 35 | 115 | S Mid ↔ N Mid |
| line-3 | 61.2 km | 40 | 150 | N Mid ↔ SE Outer |
| line-4 | 34.1 km | 15 | 68 | NE Outer ↔ SW Inner |
| line-5 | 36.6 km | 14 | 72 | SW Inner ↔ NE Outer |
| line-6 | 26.5 km | 9 | 50 | NW Inner ↔ E Mid |
| line-7 | 34.4 km | 14 | 68 | W Inner ↔ SE Outer |
| line-8 | 72.8 km | 36 | 39 | N Mid ↔ NW Inner |
| line-9 | 13.5 km | 7 | 30 | NE Mid ↔ N Inner |
| line-10 |  6.4 km | 2 | 13 | NE Inner ↔ NE Mid |
| line-11 |  7.8 km | 3 | 17 | N Mid ↔ N Outer |
| line-12 |  8.4 km | 3 | 16 | N Mid ↔ NE Inner |
| **Total** | **380.6 km** | **191 unique** | **725** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,348 one-way journeys / 160,048 train-km/day |
| Annual traction demand | 1,514.2 GWh |
| Station/depot PV / storage | 108.9 MW / 806.0 MWh |
| Aggregate charging power | 350.0 MW |
| Dedicated solar plant | 868.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 20.9 km / 313 kWh |
| Lowest traversal charging margin | line-11: 68 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.74 bn |
| Stations | $1.26 bn |
| Depots | $327 M |
| Rolling stock | $1.22 bn |
| Dedicated solar plant | $695 M |
| Residual train control | $19 M |
| Charging microgrids | $71 M |
| EPC / project services | $464 M |
| **Total city programme** | **$7.79 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.74 bn (22.3%) |
| Domestic / local capital | $6.05 bn (77.7%) |
| Annual public construction commitment | $663 M / yr for 7 years |
| Annual post-grace debt service | $544 M / yr |
| External capital saved vs default turnkey sensitivity | $12.28 bn |
| Capital + lifetime external interest saved | $27.68 bn |
| Annual OPEX | $187 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 13 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,796 assets / 9,970 tasks | [`chittagong-operations-manifest.json`](operations/chittagong-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`chittagong.toml`](chittagong.toml) | Expanded simulator scenario |
| [`chittagong.corridor.geojson`](chittagong.corridor.geojson) | GIS corridor and stations |
| [`chittagong.design-quality.yaml`](chittagong.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh chittagong
```
