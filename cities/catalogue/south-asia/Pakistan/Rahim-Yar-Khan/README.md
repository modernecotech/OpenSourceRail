# Rahim-Yar-Khan — Urban Rail Network

**Country:** PK · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Rahim-Yar-Khan-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.06 bn (88.4%) of external capital** and **$3.84 bn of external interest**. Capital plus saved interest totals **$6.90 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **10 lines**, including **7 additional residential lines**. **67.4%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **43.071 km to 77.384 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **73 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**10 line-local depots** provide **363 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **363 light-metro-3car trainsets / 1089 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Rahim-Yar-Khan rail network on OpenStreetMap](rahim-yar-khan-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 10 / 73 / 13 |
| Route length | 100.9 km double track |
| Direct transfers / reachable line pairs | 33.3% / 100.0% |
| Residents within 800 m radial station catchments | 616,735 (2020 raster; 53.4% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 363 × 3-car `light-metro-3car` trainsets (325 peak revenue) |
| Peak network throughput | 144,000 passengers/hour |
| Practical service capacity | 1,339,200 passenger-trips/day |
| Annual paid-trip planning range | 244.4–391.0 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 |  7.7 km | 7 | 30 | NE Inner ↔ SE Mid |
| line-2 | 18.0 km | 12 | 63 | S Mid ↔ NE Outer |
| line-3 | 25.3 km | 18 | 87 | NE Outer ↔ SW Outer |
| line-4 |  5.1 km | 4 | 18 | S Inner ↔ NW Inner |
| line-5 |  4.4 km | 3 | 15 | E Inner ↔ SE Inner |
| line-6 |  9.0 km | 6 | 30 | SW Inner ↔ NW Mid |
| line-7 |  3.0 km | 2 | 12 | NE Inner ↔ NE Mid |
| line-8 |  6.5 km | 5 | 24 | SW Mid ↔ W Inner |
| line-9 | 18.9 km | 12 | 68 | NE Inner ↔ SW Outer |
| line-10 |  3.0 km | 4 | 16 | NE Inner ↔ NW Inner |
| **Total** | **100.9 km** | **73 unique** | **363** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,650 one-way journeys / 46,938 train-km/day |
| Annual traction demand | 222.0 GWh |
| Station/depot PV / storage | 64.1 MW / 447.0 MWh |
| Aggregate charging power | 57.0 MW |
| Dedicated solar plant | 42.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-9: 10.4 km / 84 kWh |
| Lowest traversal charging margin | line-7: 71 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $905 M |
| Stations | $349 M |
| Depots | $169 M |
| Rolling stock | $327 M |
| Dedicated solar plant | $34 M |
| Residual train control | $5.0 M |
| Charging microgrids | $12 M |
| EPC / project services | $124 M |
| **Total city programme** | **$1.92 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $403 M (21.0%) |
| Domestic / local capital | $1.52 bn (79.0%) |
| Annual public construction commitment | $262 M / yr for 7 years |
| Annual post-grace debt service | $226 M / yr |
| External capital saved vs default turnkey sensitivity | $3.06 bn |
| Capital + lifetime external interest saved | $6.90 bn |
| Annual OPEX | $50 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 788 assets / 4,542 tasks | [`rahim-yar-khan-operations-manifest.json`](operations/rahim-yar-khan-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`rahim-yar-khan.toml`](rahim-yar-khan.toml) | Expanded simulator scenario |
| [`rahim-yar-khan.corridor.geojson`](rahim-yar-khan.corridor.geojson) | GIS corridor and stations |
| [`rahim-yar-khan.design-quality.yaml`](rahim-yar-khan.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh rahim-yar-khan
```
