# Biratnagar — Urban Rail Network

**Country:** NP · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Biratnagar-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$1.56 bn (89.9%) of external capital** and **$1.96 bn of external interest**. Capital plus saved interest totals **$3.52 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **6 lines**, including **3 additional residential lines**. **69.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **26.684 km to 32.991 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **31 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**6 line-local depots** provide **119 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **119 tram-2car trainsets / 238 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Biratnagar rail network on OpenStreetMap](biratnagar-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 6 / 31 / 4 |
| Route length | 49.4 km double track |
| Direct transfers / reachable line pairs | 26.7% / 66.7% |
| Residents within 800 m radial station catchments | 239,594 (2020 raster; 51.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 119 × 2-car `tram-2car` trainsets (105 peak revenue) |
| Peak network throughput | 57,600 passengers/hour |
| Practical service capacity | 535,680 passenger-trips/day |
| Annual paid-trip planning range | 97.8–156.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.0 km | 7 | 27 | S Outer ↔ NE Outer |
| line-2 |  4.3 km | 3 | 12 | SE Outer ↔ E Mid |
| line-3 |  9.0 km | 6 | 23 | SW Outer ↔ NE Mid |
| line-4 |  6.4 km | 4 | 16 | NE Mid ↔ NW Mid |
| line-5 |  9.2 km | 5 | 21 | W Mid ↔ N Outer |
| line-6 |  8.5 km | 6 | 20 | NE Inner ↔ SW Outer |
| **Total** | **49.4 km** | **31 unique** | **119** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 2,790 one-way journeys / 22,978 train-km/day |
| Annual traction demand | 72.5 GWh |
| Station/depot PV / storage | 35.4 MW / 249.0 MWh |
| Aggregate charging power | 12.0 MW |
| Dedicated solar plant | 6.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 9.2 km / 46 kWh |
| Lowest traversal charging margin | line-4: 14 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $619 M |
| Stations | $122 M |
| Depots | $84 M |
| Rolling stock | $67 M |
| Dedicated solar plant | $5.5 M |
| Residual train control | $2.5 M |
| Charging microgrids | $2.6 M |
| EPC / project services | $63 M |
| **Total city programme** | **$965 M** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $176 M (18.2%) |
| Domestic / local capital | $790 M (81.8%) |
| Annual public construction commitment | $78 M / yr for 7 years |
| Annual post-grace debt service | $63 M / yr |
| External capital saved vs default turnkey sensitivity | $1.56 bn |
| Capital + lifetime external interest saved | $3.52 bn |
| Annual OPEX | $22 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 298 assets / 1,601 tasks | [`biratnagar-operations-manifest.json`](operations/biratnagar-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`biratnagar.toml`](biratnagar.toml) | Expanded simulator scenario |
| [`biratnagar.corridor.geojson`](biratnagar.corridor.geojson) | GIS corridor and stations |
| [`biratnagar.design-quality.yaml`](biratnagar.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh biratnagar
```
