# Huye — Urban Rail Network

**Country:** RW · **Population:** 250,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Huye-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.08 bn (89.2%) of external capital** and **$2.61 bn of external interest**. Capital plus saved interest totals **$4.69 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **9 additional residential lines**. **60.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **30.945 km to 44.697 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **58 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **204 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **204 tram-2car trainsets / 408 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Huye rail network on OpenStreetMap](huye-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 58 / 14 |
| Route length | 76.4 km double track |
| Direct transfers / reachable line pairs | 25.8% / 100.0% |
| Residents within 800 m radial station catchments | 101,028 (2020 raster; 47.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 204 × 2-car `tram-2car` trainsets (176 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 1,071,360 passenger-trips/day |
| Annual paid-trip planning range | 195.5–312.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 14.5 km | 10 | 35 | SW Mid ↔ NE Outer |
| line-2 | 12.5 km | 10 | 32 | SE Outer ↔ W Mid |
| line-3 | 12.0 km | 8 | 29 | N Outer ↔ W Mid |
| line-4 |  2.4 km | 2 | 8 | S Outer ↔ S Mid |
| line-5 |  4.7 km | 3 | 12 | NE Inner ↔ NW Inner |
| line-6 |  5.5 km | 4 | 14 | S Mid ↔ S Outer |
| line-7 |  4.9 km | 4 | 14 | N Mid ↔ NW Mid |
| line-8 |  3.4 km | 3 | 11 | S Mid ↔ E Inner |
| line-9 |  2.5 km | 3 | 10 | SW Mid ↔ SW Inner |
| line-10 |  3.9 km | 4 | 13 | NE Outer ↔ NE Mid |
| line-11 |  5.8 km | 4 | 15 | NW Inner ↔ NW Outer |
| line-12 |  4.3 km | 3 | 11 | W Mid ↔ W Outer |
| **Total** | **76.4 km** | **58 unique** | **204** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,580 one-way journeys / 35,527 train-km/day |
| Annual traction demand | 112.0 GWh |
| Station/depot PV / storage | 71.1 MW / 498.5 MWh |
| Aggregate charging power | 24.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-11: 5.8 km / 29 kWh |
| Lowest traversal charging margin | line-11: 17 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $617 M |
| Stations | $307 M |
| Depots | $163 M |
| Rolling stock | $114 M |
| Residual train control | $3.8 M |
| Charging microgrids | $5.2 M |
| EPC / project services | $85 M |
| **Total city programme** | **$1.29 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $251 M (19.4%) |
| Domestic / local capital | $1.04 bn (80.6%) |
| Annual public construction commitment | $112 M / yr for 7 years |
| Annual post-grace debt service | $91 M / yr |
| External capital saved vs default turnkey sensitivity | $2.08 bn |
| Capital + lifetime external interest saved | $4.69 bn |
| Annual OPEX | $31 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 3 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 541 assets / 2,839 tasks | [`huye-operations-manifest.json`](operations/huye-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`huye.toml`](huye.toml) | Expanded simulator scenario |
| [`huye.corridor.geojson`](huye.corridor.geojson) | GIS corridor and stations |
| [`huye.design-quality.yaml`](huye.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh huye
```
