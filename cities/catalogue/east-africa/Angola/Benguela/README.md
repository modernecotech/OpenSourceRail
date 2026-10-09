# Benguela — Urban Rail Network

**Country:** AO · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Benguela-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.79 bn (88.5%) of external capital** and **$3.43 bn of external interest**. Capital plus saved interest totals **$6.22 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **14 lines**, including **11 additional residential lines**. **68.6%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **40.874 km to 72.922 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **63 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**14 line-local depots** provide **333 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **333 light-metro-3car trainsets / 999 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Benguela rail network on OpenStreetMap](benguela-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 14 / 63 / 12 |
| Route length | 94.8 km double track |
| Direct transfers / reachable line pairs | 18.7% / 100.0% |
| Residents within 800 m radial station catchments | 237,395 (2020 raster; 51.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 333 × 3-car `light-metro-3car` trainsets (294 peak revenue) |
| Peak network throughput | 201,600 passengers/hour |
| Practical service capacity | 1,874,880 passenger-trips/day |
| Annual paid-trip planning range | 342.2–547.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.5 km | 10 | 64 | NE Outer ↔ SW Inner |
| line-2 | 16.6 km | 9 | 51 | NE Inner ↔ W Outer |
| line-3 | 10.8 km | 8 | 36 | NW Inner ↔ SE Mid |
| line-4 |  5.0 km | 4 | 18 | SW Inner ↔ SW Mid |
| line-5 |  3.3 km | 3 | 14 | W Outer ↔ SW Mid |
| line-6 |  2.6 km | 2 | 11 | SE Inner ↔ S Inner |
| line-7 |  3.4 km | 3 | 14 | N Inner ↔ N Inner |
| line-8 |  2.9 km | 3 | 12 | NE Outer ↔ NE Mid |
| line-9 |  5.7 km | 4 | 21 | SW Inner ↔ SW Mid |
| line-10 |  6.6 km | 4 | 24 | SW Inner ↔ S Inner |
| line-11 |  2.3 km | 2 | 10 | W Inner ↔ NW Inner |
| line-12 |  7.4 km | 5 | 27 | NE Mid ↔ NE Outer |
| line-13 |  5.5 km | 4 | 21 | SE Mid ↔ E Inner |
| line-14 |  2.2 km | 2 | 10 | SW Inner ↔ S Mid |
| **Total** | **94.8 km** | **63 unique** | **333** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,510 one-way journeys / 44,075 train-km/day |
| Annual traction demand | 208.5 GWh |
| Station/depot PV / storage | 80.8 MW / 578.0 MWh |
| Aggregate charging power | 25.0 MW |
| Dedicated solar plant | 8.1 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-12: 7.4 km / 61 kWh |
| Lowest traversal charging margin | line-10: 13 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $840 M |
| Stations | $271 M |
| Depots | $209 M |
| Rolling stock | $300 M |
| Dedicated solar plant | $6.5 M |
| Residual train control | $4.7 M |
| Charging microgrids | $5.2 M |
| EPC / project services | $114 M |
| **Total city programme** | **$1.75 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $362 M (20.7%) |
| Domestic / local capital | $1.39 bn (79.3%) |
| Annual public construction commitment | $200 M / yr for 5 years |
| Annual post-grace debt service | $151 M / yr |
| External capital saved vs default turnkey sensitivity | $2.79 bn |
| Capital + lifetime external interest saved | $6.22 bn |
| Annual OPEX | $50 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 714 assets / 4,087 tasks | [`benguela-operations-manifest.json`](operations/benguela-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`benguela.toml`](benguela.toml) | Expanded simulator scenario |
| [`benguela.corridor.geojson`](benguela.corridor.geojson) | GIS corridor and stations |
| [`benguela.design-quality.yaml`](benguela.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh benguela
```
