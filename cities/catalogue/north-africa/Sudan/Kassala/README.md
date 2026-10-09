# Kassala — Urban Rail Network

**Country:** SD · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Kassala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.63 bn (89.0%) of external capital** and **$2.11 bn of external interest**. Capital plus saved interest totals **$3.74 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **8 lines**, including **5 additional residential lines**. **46.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **23.580 km to 41.220 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **31 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**8 line-local depots** provide **152 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **152 light-metro-3car trainsets / 456 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Kassala rail network on OpenStreetMap](kassala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 8 / 31 / 7 |
| Route length | 41.2 km double track |
| Direct transfers / reachable line pairs | 25.0% / 100.0% |
| Residents within 800 m radial station catchments | 170,518 (2020 raster; 34.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 152 × 3-car `light-metro-3car` trainsets (134 peak revenue) |
| Peak network throughput | 115,200 passengers/hour |
| Practical service capacity | 1,071,360 passenger-trips/day |
| Annual paid-trip planning range | 195.5–312.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  8.9 km | 5 | 28 | N Mid ↔ SW Outer |
| line-2 |  5.7 km | 5 | 21 | E Mid ↔ W Mid |
| line-3 |  6.3 km | 6 | 26 | NE Inner ↔ SW Outer |
| line-4 |  4.6 km | 3 | 17 | N Mid ↔ N Outer |
| line-5 |  2.3 km | 2 | 10 | SW Mid ↔ W Outer |
| line-6 |  5.4 km | 4 | 19 | E Inner ↔ E Outer |
| line-7 |  3.6 km | 3 | 14 | E Mid ↔ NE Outer |
| line-8 |  4.6 km | 3 | 17 | SW Mid ↔ S Outer |
| **Total** | **41.2 km** | **31 unique** | **152** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,720 one-way journeys / 19,167 train-km/day |
| Annual traction demand | 90.7 GWh |
| Station/depot PV / storage | 46.9 MW / 331.5 MWh |
| Aggregate charging power | 15.5 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 2.9 km / 23 kWh |
| Lowest traversal charging margin | line-8: 29 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $536 M |
| Stations | $160 M |
| Depots | $114 M |
| Rolling stock | $137 M |
| Residual train control | $2.1 M |
| Charging microgrids | $3.2 M |
| EPC / project services | $67 M |
| **Total city programme** | **$1.02 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $201 M (19.7%) |
| Domestic / local capital | $817 M (80.3%) |
| Annual public construction commitment | $123 M / yr for 10 years |
| Annual post-grace debt service | $112 M / yr |
| External capital saved vs default turnkey sensitivity | $1.63 bn |
| Capital + lifetime external interest saved | $3.74 bn |
| Annual OPEX | $24 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 347 assets / 1,925 tasks | [`kassala-operations-manifest.json`](operations/kassala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`kassala.toml`](kassala.toml) | Expanded simulator scenario |
| [`kassala.corridor.geojson`](kassala.corridor.geojson) | GIS corridor and stations |
| [`kassala.design-quality.yaml`](kassala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh kassala
```
