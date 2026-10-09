# Zarqa — Urban Rail Network

**Country:** JO · **Population:** 700,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Zarqa-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.84 bn (88.8%) of external capital** and **$4.72 bn of external interest**. Capital plus saved interest totals **$8.56 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **77.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **53.070 km to 75.125 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **75 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **391 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **391 light-metro-3car trainsets / 1173 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Zarqa rail network on OpenStreetMap](zarqa-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 75 / 20 |
| Route length | 112.1 km double track |
| Direct transfers / reachable line pairs | 23.1% / 100.0% |
| Residents within 800 m radial station catchments | 754,864 (2020 raster; 62.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 391 × 3-car `light-metro-3car` trainsets (347 peak revenue) |
| Peak network throughput | 187,200 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.4 km | 18 | 92 | NE Outer ↔ SW Outer |
| line-2 | 26.6 km | 17 | 86 | SW Outer ↔ NE Outer |
| line-3 | 11.9 km | 7 | 39 | N Mid ↔ E Outer |
| line-4 |  5.0 km | 4 | 18 | SW Inner ↔ SE Inner |
| line-5 |  4.5 km | 4 | 18 | SW Mid ↔ SW Mid |
| line-6 |  3.7 km | 3 | 14 | NE Inner ↔ NE Mid |
| line-7 |  6.9 km | 4 | 25 | SW Mid ↔ W Inner |
| line-8 |  6.1 km | 4 | 24 | SW Inner ↔ SW Mid |
| line-9 |  6.5 km | 4 | 23 | N Inner ↔ SE Inner |
| line-10 |  2.8 km | 2 | 11 | NE Mid ↔ NE Mid |
| line-11 |  2.7 km | 2 | 11 | N Inner ↔ N Inner |
| line-12 |  4.6 km | 3 | 17 | E Inner ↔ SE Mid |
| line-13 |  2.6 km | 3 | 13 | SW Mid ↔ W Mid |
| **Total** | **112.1 km** | **75 unique** | **391** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 52,132 train-km/day |
| Annual traction demand | 246.6 GWh |
| Station/depot PV / storage | 81.5 MW / 547.5 MWh |
| Aggregate charging power | 34.0 MW |
| Dedicated solar plant | 35.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 6.1 km / 49 kWh |
| Lowest traversal charging margin | line-8: 20 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.20 bn |
| Stations | $442 M |
| Depots | $207 M |
| Rolling stock | $352 M |
| Dedicated solar plant | $29 M |
| Residual train control | $5.6 M |
| Charging microgrids | $7.2 M |
| EPC / project services | $155 M |
| **Total city programme** | **$2.40 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $486 M (20.2%) |
| Domestic / local capital | $1.92 bn (79.8%) |
| Annual public construction commitment | $213 M / yr for 5 years |
| Annual post-grace debt service | $153 M / yr |
| External capital saved vs default turnkey sensitivity | $3.84 bn |
| Capital + lifetime external interest saved | $8.56 bn |
| Annual OPEX | $81 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 11 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 845 assets / 4,861 tasks | [`zarqa-operations-manifest.json`](operations/zarqa-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`zarqa.toml`](zarqa.toml) | Expanded simulator scenario |
| [`zarqa.corridor.geojson`](zarqa.corridor.geojson) | GIS corridor and stations |
| [`zarqa.design-quality.yaml`](zarqa.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh zarqa
```
