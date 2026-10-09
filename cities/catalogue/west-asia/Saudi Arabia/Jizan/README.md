# Jizan — Urban Rail Network

**Country:** SA · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Jizan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.39 bn (88.3%) of external capital** and **$2.94 bn of external interest**. Capital plus saved interest totals **$5.33 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **71.9%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **38.866 km to 58.039 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **60 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **291 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **291 light-metro-3car trainsets / 873 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Jizan rail network on OpenStreetMap](jizan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 60 / 9 |
| Route length | 79.2 km double track |
| Direct transfers / reachable line pairs | 25.5% / 100.0% |
| Residents within 800 m radial station catchments | 51,580 (2020 raster; 56.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 291 × 3-car `light-metro-3car` trainsets (258 peak revenue) |
| Peak network throughput | 158,400 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 20.4 km | 14 | 69 | S Mid ↔ N Outer |
| line-2 |  7.4 km | 7 | 29 | W Mid ↔ NE Inner |
| line-3 | 17.5 km | 13 | 58 | SE Outer ↔ NW Mid |
| line-4 |  4.8 km | 3 | 17 | S Mid ↔ W Inner |
| line-5 |  6.8 km | 5 | 26 | NE Inner ↔ NE Outer |
| line-6 |  5.2 km | 4 | 21 | SE Outer ↔ SE Mid |
| line-7 |  2.6 km | 2 | 11 | N Inner ↔ E Inner |
| line-8 |  3.4 km | 3 | 14 | SE Outer ↔ SE Mid |
| line-9 |  3.6 km | 4 | 17 | W Inner ↔ NW Mid |
| line-10 |  2.8 km | 2 | 11 | S Inner ↔ SE Inner |
| line-11 |  4.8 km | 3 | 18 | N Inner ↔ N Mid |
| **Total** | **79.2 km** | **60 unique** | **291** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 36,813 train-km/day |
| Annual traction demand | 174.1 GWh |
| Station/depot PV / storage | 67.3 MW / 460.5 MWh |
| Aggregate charging power | 26.0 MW |
| Dedicated solar plant | 14.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 5.2 km / 42 kWh |
| Lowest traversal charging margin | line-11: 14 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $653 M |
| Stations | $303 M |
| Depots | $168 M |
| Rolling stock | $262 M |
| Dedicated solar plant | $11 M |
| Residual train control | $4.0 M |
| Charging microgrids | $5.4 M |
| EPC / project services | $98 M |
| **Total city programme** | **$1.50 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $316 M (21.0%) |
| Domestic / local capital | $1.19 bn (79.0%) |
| Annual public construction commitment | $105 M / yr for 5 years |
| Annual post-grace debt service | $73 M / yr |
| External capital saved vs default turnkey sensitivity | $2.39 bn |
| Capital + lifetime external interest saved | $5.33 bn |
| Annual OPEX | $100 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 9 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 650 assets / 3,678 tasks | [`jizan-operations-manifest.json`](operations/jizan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`jizan.toml`](jizan.toml) | Expanded simulator scenario |
| [`jizan.corridor.geojson`](jizan.corridor.geojson) | GIS corridor and stations |
| [`jizan.design-quality.yaml`](jizan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh jizan
```
