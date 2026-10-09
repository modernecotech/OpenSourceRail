# Homs — Urban Rail Network

**Country:** SY · **Population:** 775,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Homs-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.16 bn (88.6%) of external capital** and **$2.79 bn of external interest**. Capital plus saved interest totals **$4.94 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **60.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **39.981 km to 63.839 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **46 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **234 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **234 light-metro-3car trainsets / 702 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Homs rail network on OpenStreetMap](homs-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 46 / 11 |
| Route length | 66.3 km double track |
| Direct transfers / reachable line pairs | 24.4% / 100.0% |
| Residents within 800 m radial station catchments | 531,280 (2020 raster; 46.8% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 234 × 3-car `light-metro-3car` trainsets (206 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.1 km | 7 | 32 | W Mid ↔ SE Mid |
| line-2 | 10.7 km | 8 | 36 | SW Outer ↔ NE Mid |
| line-3 | 12.5 km | 8 | 41 | NW Outer ↔ E Mid |
| line-4 |  3.0 km | 2 | 12 | SW Inner ↔ SE Inner |
| line-5 |  2.2 km | 2 | 10 | S Inner ↔ S Mid |
| line-6 |  2.9 km | 3 | 13 | SW Mid ↔ SW Mid |
| line-7 |  7.0 km | 4 | 23 | W Mid ↔ E Inner |
| line-8 |  6.2 km | 4 | 23 | SE Mid ↔ S Outer |
| line-9 |  5.6 km | 4 | 21 | N Mid ↔ N Outer |
| line-10 |  6.1 km | 4 | 23 | E Mid ↔ NE Outer |
| **Total** | **66.3 km** | **46 unique** | **234** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 30,809 train-km/day |
| Annual traction demand | 145.7 GWh |
| Station/depot PV / storage | 59.9 MW / 416.5 MWh |
| Aggregate charging power | 21.5 MW |
| Dedicated solar plant | 14.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 4.2 km / 30 kWh |
| Lowest traversal charging margin | line-8: 25 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $658 M |
| Stations | $227 M |
| Depots | $149 M |
| Rolling stock | $211 M |
| Dedicated solar plant | $12 M |
| Residual train control | $3.3 M |
| Charging microgrids | $4.5 M |
| EPC / project services | $88 M |
| **Total city programme** | **$1.35 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $277 M (20.5%) |
| Domestic / local capital | $1.07 bn (79.5%) |
| Annual public construction commitment | $206 M / yr for 10 years |
| Annual post-grace debt service | $190 M / yr |
| External capital saved vs default turnkey sensitivity | $2.16 bn |
| Capital + lifetime external interest saved | $4.94 bn |
| Annual OPEX | $32 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 518 assets / 2,928 tasks | [`homs-operations-manifest.json`](operations/homs-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`homs.toml`](homs.toml) | Expanded simulator scenario |
| [`homs.corridor.geojson`](homs.corridor.geojson) | GIS corridor and stations |
| [`homs.design-quality.yaml`](homs.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh homs
```
