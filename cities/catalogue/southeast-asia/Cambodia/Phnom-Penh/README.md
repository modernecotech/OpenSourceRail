# Phnom-Penh — Urban Rail Network

**Country:** KH · **Population:** 2,281,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Phnom-Penh-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$12.88 bn (88.6%) of external capital** and **$16.15 bn of external interest**. Capital plus saved interest totals **$29.03 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **25 lines**, including **19 additional residential lines**. **80.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **180.759 km to 281.566 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **289 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**25 line-local depots** provide **828 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **828 metro-4car trainsets / 3312 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Phnom-Penh rail network on OpenStreetMap](phnom-penh-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 25 / 289 / 56 |
| Route length | 383.2 km double track |
| Direct transfers / reachable line pairs | 22.7% / 100.0% |
| Residents within 800 m radial station catchments | 1,913,459 (2020 raster; 66.1% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 828 × 4-car `metro-4car` trainsets (737 peak revenue) |
| Peak network throughput | 480,000 passengers/hour |
| Practical service capacity | 4,374,720 passenger-trips/day |
| Annual paid-trip planning range | 798.4–1277.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.3 km | 19 | 63 | S Mid ↔ N Mid |
| line-2 | 26.1 km | 21 | 63 | W Inner ↔ E Outer |
| line-3 | 55.0 km | 50 | 146 | SW Mid ↔ NE Outer |
| line-4 | 36.9 km | 30 | 93 | N Outer ↔ S Mid |
| line-5 | 34.7 km | 24 | 73 | NW Outer ↔ SE Mid |
| line-6 | 64.5 km | 42 | 36 | NW Inner ↔ NW Inner |
| line-7 |  4.9 km | 3 | 12 | SW Inner ↔ S Inner |
| line-8 |  6.3 km | 5 | 17 | SW Inner ↔ S Inner |
| line-9 |  8.4 km | 7 | 24 | SW Inner ↔ N Inner |
| line-10 |  6.0 km | 6 | 19 | SE Inner ↔ SE Mid |
| line-11 |  5.1 km | 4 | 14 | W Mid ↔ W Mid |
| line-12 |  5.0 km | 3 | 12 | NW Inner ↔ N Mid |
| line-13 |  6.0 km | 4 | 13 | S Mid ↔ SE Outer |
| line-14 |  6.5 km | 6 | 19 | SW Mid ↔ SW Mid |
| line-15 |  5.5 km | 5 | 17 | SW Inner ↔ SW Inner |
| line-16 |  7.6 km | 7 | 23 | NW Inner ↔ E Inner |
| line-17 |  5.2 km | 3 | 13 | SE Mid ↔ SE Mid |
| line-18 | 11.1 km | 8 | 28 | SE Inner ↔ SE Mid |
| line-19 |  6.1 km | 4 | 14 | SW Mid ↔ W Mid |
| line-20 | 17.3 km | 11 | 36 | N Mid ↔ W Mid |
| line-21 |  5.3 km | 3 | 12 | SW Mid ↔ SW Mid |
| line-22 |  8.5 km | 8 | 26 | N Inner ↔ S Inner |
| line-23 |  5.7 km | 5 | 17 | SW Mid ↔ SW Inner |
| line-24 | 11.9 km | 7 | 24 | SW Mid ↔ S Mid |
| line-25 |  6.3 km | 4 | 14 | SE Mid ↔ SE Outer |
| **Total** | **383.2 km** | **289 unique** | **828** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 11,392 one-way journeys / 163,192 train-km/day |
| Annual traction demand | 1,029.3 GWh |
| Station/depot PV / storage | 189.5 MW / 1,322.5 MWh |
| Aggregate charging power | 360.0 MW |
| Dedicated solar plant | 457.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-5: 17.4 km / 174 kWh |
| Lowest traversal charging margin | line-24: 77 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $4.14 bn |
| Stations | $1.60 bn |
| Depots | $448 M |
| Rolling stock | $927 M |
| Dedicated solar plant | $366 M |
| Residual train control | $19 M |
| Charging microgrids | $73 M |
| EPC / project services | $504 M |
| **Total city programme** | **$8.08 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.66 bn (20.5%) |
| Domestic / local capital | $6.42 bn (79.5%) |
| Annual public construction commitment | $669 M / yr for 7 years |
| Annual post-grace debt service | $543 M / yr |
| External capital saved vs default turnkey sensitivity | $12.88 bn |
| Capital + lifetime external interest saved | $29.03 bn |
| Annual OPEX | $198 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 37 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,398 assets / 12,506 tasks | [`phnom-penh-operations-manifest.json`](operations/phnom-penh-operations-manifest.json) |

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
