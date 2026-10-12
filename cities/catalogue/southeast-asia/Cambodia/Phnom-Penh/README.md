# Phnom-Penh — Urban Rail Network

**Country:** KH · **Population:** 2,281,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Phnom-Penh-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$9.04 bn (88.7%) of external capital** and **$11.34 bn of external interest**. Capital plus saved interest totals **$20.38 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-12).** The controlled planning inventory contains **9 lines**, including **3 additional residential lines**. **44.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **180.759 km to 228.060 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **159 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **515 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **515 metro-4car trainsets / 2060 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Phnom-Penh rail network on OpenStreetMap](phnom-penh-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 159 / 32 |
| Route length | 298.5 km double track |
| Direct transfers / reachable line pairs | 61.1% / 100.0% |
| Residents within 800 m radial station catchments | 935,744 (2020 raster; 32.3% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 515 × 4-car `metro-4car` trainsets (462 peak revenue) |
| Peak network throughput | 172,800 passengers/hour |
| Practical service capacity | 1,517,760 passenger-trips/day |
| Annual paid-trip planning range | 277.0–443.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 30.9 km | 15 | 58 | S Mid ↔ N Outer |
| line-2 | 33.0 km | 29 | 91 | W Mid ↔ SE Outer |
| line-3 | 59.4 km | 27 | 105 | SW Outer ↔ NE Outer |
| line-4 | 36.8 km | 19 | 71 | N Outer ↔ S Mid |
| line-5 | 39.4 km | 32 | 100 | NW Outer ↔ SE Mid |
| line-6 | 67.5 km | 21 | 27 | NW Mid ↔ W Mid |
| line-7 |  6.5 km | 3 | 13 | SW Inner ↔ SW Mid |
| line-8 |  5.4 km | 2 | 11 | W Mid ↔ W Outer |
| line-9 | 19.8 km | 11 | 39 | SE Outer ↔ S Inner |
| **Total** | **298.5 km** | **159 unique** | **515** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 3,952 one-way journeys / 123,131 train-km/day |
| Annual traction demand | 776.6 GWh |
| Station/depot PV / storage | 85.5 MW / 562.5 MWh |
| Aggregate charging power | 216.0 MW |
| Dedicated solar plant | 411.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 20.2 km / 202 kWh |
| Lowest traversal charging margin | line-8: 88 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $3.08 bn |
| Stations | $1.07 bn |
| Depots | $203 M |
| Rolling stock | $577 M |
| Dedicated solar plant | $329 M |
| Residual train control | $15 M |
| Charging microgrids | $44 M |
| EPC / project services | $349 M |
| **Total city programme** | **$5.67 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.15 bn (20.4%) |
| Domestic / local capital | $4.51 bn (79.6%) |
| Annual public construction commitment | $470 M / yr for 7 years |
| Annual post-grace debt service | $381 M / yr |
| External capital saved vs default turnkey sensitivity | $9.04 bn |
| Capital + lifetime external interest saved | $20.38 bn |
| Annual OPEX | $133 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 8 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,390 assets / 7,486 tasks | [`phnom-penh-operations-manifest.json`](operations/phnom-penh-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`phnom-penh.toml`](phnom-penh.toml) | Expanded simulator scenario |
| [`phnom-penh.corridor.geojson`](phnom-penh.corridor.geojson) | GIS corridor and stations |
| [`phnom-penh.design-quality.yaml`](phnom-penh.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh phnom-penh
```
