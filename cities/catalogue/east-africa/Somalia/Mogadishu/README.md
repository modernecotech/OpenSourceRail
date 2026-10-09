# Mogadishu — Urban Rail Network

**Country:** SO · **Population:** 2,610,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mogadishu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$4.33 bn (88.6%) of external capital** and **$5.59 bn of external interest**. Capital plus saved interest totals **$9.92 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **12 lines**, including **8 additional residential lines**. **78.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **98.589 km to 109.055 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 1 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **105 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**12 line-local depots** provide **296 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **296 metro-4car trainsets / 1184 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mogadishu rail network on OpenStreetMap](mogadishu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 12 / 105 / 23 |
| Route length | 156.9 km double track |
| Direct transfers / reachable line pairs | 31.8% / 100.0% |
| Residents within 800 m radial station catchments | 537,049 (2020 raster; 61.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 296 × 4-car `metro-4car` trainsets (261 peak revenue) |
| Peak network throughput | 230,400 passengers/hour |
| Practical service capacity | 2,053,440 passenger-trips/day |
| Annual paid-trip planning range | 374.8–599.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.4 km | 21 | 69 | SE Inner ↔ W Outer |
| line-2 | 22.0 km | 15 | 52 | E Mid ↔ SW Mid |
| line-3 | 13.9 km | 8 | 30 | NW Mid ↔ S Inner |
| line-4 | 45.1 km | 25 | 23 | N Mid ↔ N Inner |
| line-5 |  3.6 km | 5 | 15 | E Inner ↔ E Inner |
| line-6 |  4.9 km | 4 | 13 | E Inner ↔ NE Mid |
| line-7 |  4.0 km | 3 | 12 | S Inner ↔ SW Mid |
| line-8 |  8.5 km | 6 | 19 | E Inner ↔ E Mid |
| line-9 |  4.0 km | 3 | 11 | E Inner ↔ NE Mid |
| line-10 |  3.2 km | 3 | 11 | SE Inner ↔ SE Inner |
| line-11 |  7.4 km | 5 | 18 | S Inner ↔ SE Inner |
| line-12 |  6.8 km | 7 | 23 | NE Inner ↔ SE Inner |
| **Total** | **156.9 km** | **105 unique** | **296** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,348 one-way journeys / 62,481 train-km/day |
| Annual traction demand | 394.1 GWh |
| Station/depot PV / storage | 83.7 MW / 598.5 MWh |
| Aggregate charging power | 135.0 MW |
| Dedicated solar plant | 110.7 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-1: 11.8 km / 127 kWh |
| Lowest traversal charging margin | line-6: 89 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1.34 bn |
| Stations | $546 M |
| Depots | $198 M |
| Rolling stock | $332 M |
| Dedicated solar plant | $89 M |
| Residual train control | $7.8 M |
| Charging microgrids | $28 M |
| EPC / project services | $172 M |
| **Total city programme** | **$2.71 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $557 M (20.5%) |
| Domestic / local capital | $2.16 bn (79.5%) |
| Annual public construction commitment | $327 M / yr for 10 years |
| Annual post-grace debt service | $297 M / yr |
| External capital saved vs default turnkey sensitivity | $4.33 bn |
| Capital + lifetime external interest saved | $9.92 bn |
| Annual OPEX | $62 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 26 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 875 assets / 4,505 tasks | [`mogadishu-operations-manifest.json`](operations/mogadishu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mogadishu.toml`](mogadishu.toml) | Expanded simulator scenario |
| [`mogadishu.corridor.geojson`](mogadishu.corridor.geojson) | GIS corridor and stations |
| [`mogadishu.design-quality.yaml`](mogadishu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mogadishu
```
