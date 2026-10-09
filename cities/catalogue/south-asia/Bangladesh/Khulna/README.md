# Khulna — Urban Rail Network

**Country:** BD · **Population:** 1,500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Khulna-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.71 bn (88.7%) of external capital** and **$10.92 bn of external interest**. Capital plus saved interest totals **$19.63 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **16 lines**, including **10 additional residential lines**. **79.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **163.275 km to 219.489 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **188 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**16 line-local depots** provide **531 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **531 metro-4car trainsets / 2124 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Khulna rail network on OpenStreetMap](khulna-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 16 / 188 / 41 |
| Route length | 259.0 km double track |
| Direct transfers / reachable line pairs | 25.8% / 100.0% |
| Residents within 800 m radial station catchments | 1,116,140 (2020 raster; 66.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 531 × 4-car `metro-4car` trainsets (474 peak revenue) |
| Peak network throughput | 307,200 passengers/hour |
| Practical service capacity | 2,767,680 passenger-trips/day |
| Annual paid-trip planning range | 505.1–808.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 28.7 km | 19 | 65 | NW Outer ↔ S Mid |
| line-2 | 32.5 km | 27 | 82 | SW Mid ↔ NE Outer |
| line-3 | 31.6 km | 21 | 71 | SE Outer ↔ N Mid |
| line-4 | 16.6 km | 11 | 37 | NW Mid ↔ S Mid |
| line-5 | 24.8 km | 20 | 63 | E Outer ↔ NW Mid |
| line-6 | 59.1 km | 36 | 32 | NW Mid ↔ NW Mid |
| line-7 |  4.0 km | 4 | 14 | S Inner ↔ SE Mid |
| line-8 |  5.3 km | 5 | 17 | SW Inner ↔ N Inner |
| line-9 |  5.4 km | 4 | 13 | SE Mid ↔ SE Mid |
| line-10 |  5.8 km | 5 | 17 | SE Mid ↔ S Inner |
| line-11 | 12.7 km | 10 | 34 | NE Inner ↔ NW Mid |
| line-12 |  5.6 km | 4 | 13 | SE Outer ↔ SE Mid |
| line-13 |  7.4 km | 5 | 16 | SW Mid ↔ W Outer |
| line-14 |  5.3 km | 4 | 15 | SE Inner ↔ E Mid |
| line-15 |  3.9 km | 5 | 16 | NW Outer ↔ NW Outer |
| line-16 | 10.1 km | 8 | 26 | S Inner ↔ SW Mid |
| **Total** | **259.0 km** | **188 unique** | **531** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 7,208 one-way journeys / 106,696 train-km/day |
| Annual traction demand | 673.0 GWh |
| Station/depot PV / storage | 125.6 MW / 868.0 MWh |
| Aggregate charging power | 252.0 MW |
| Dedicated solar plant | 297.3 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 9.6 km / 96 kWh |
| Lowest traversal charging margin | line-13: 66 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.87 bn |
| Stations | $1.06 bn |
| Depots | $289 M |
| Rolling stock | $595 M |
| Dedicated solar plant | $238 M |
| Residual train control | $13 M |
| Charging microgrids | $51 M |
| EPC / project services | $341 M |
| **Total city programme** | **$5.46 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.11 bn (20.3%) |
| Domestic / local capital | $4.35 bn (79.7%) |
| Annual public construction commitment | $470 M / yr for 7 years |
| Annual post-grace debt service | $382 M / yr |
| External capital saved vs default turnkey sensitivity | $8.71 bn |
| Capital + lifetime external interest saved | $19.63 bn |
| Annual OPEX | $130 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 36 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,562 assets / 8,113 tasks | [`khulna-operations-manifest.json`](operations/khulna-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`khulna.toml`](khulna.toml) | Expanded simulator scenario |
| [`khulna.corridor.geojson`](khulna.corridor.geojson) | GIS corridor and stations |
| [`khulna.design-quality.yaml`](khulna.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh khulna
```
