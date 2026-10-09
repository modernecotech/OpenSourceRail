# Gulu — Urban Rail Network

**Country:** UG · **Population:** 350,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gulu-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.35 bn (88.3%) of external capital** and **$4.20 bn of external interest**. Capital plus saved interest totals **$7.55 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **15 lines**, including **12 additional residential lines**. **65.7%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **48.304 km to 88.197 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **74 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**15 line-local depots** provide **383 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **383 light-metro-3car trainsets / 1149 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Gulu rail network on OpenStreetMap](gulu-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 15 / 74 / 21 |
| Route length | 108.5 km double track |
| Direct transfers / reachable line pairs | 21.9% / 100.0% |
| Residents within 800 m radial station catchments | 140,548 (2020 raster; 49.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 383 × 3-car `light-metro-3car` trainsets (338 peak revenue) |
| Peak network throughput | 216,000 passengers/hour |
| Practical service capacity | 2,008,800 passenger-trips/day |
| Annual paid-trip planning range | 366.6–586.6 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 12.3 km | 9 | 40 | SW Mid ↔ E Mid |
| line-2 | 26.3 km | 15 | 89 | SE Outer ↔ NW Outer |
| line-3 | 16.4 km | 10 | 52 | W Mid ↔ NE Mid |
| line-4 |  2.7 km | 2 | 11 | SE Inner ↔ SE Inner |
| line-5 |  5.4 km | 4 | 19 | S Inner ↔ W Inner |
| line-6 |  5.9 km | 4 | 19 | E Inner ↔ NW Inner |
| line-7 |  2.6 km | 2 | 11 | SW Inner ↔ S Inner |
| line-8 |  3.6 km | 3 | 14 | NE Inner ↔ NW Inner |
| line-9 |  6.8 km | 4 | 25 | W Mid ↔ SW Inner |
| line-10 |  6.6 km | 5 | 23 | SE Inner ↔ NE Mid |
| line-11 |  5.3 km | 4 | 21 | W Inner ↔ NW Mid |
| line-12 |  6.0 km | 5 | 23 | E Mid ↔ SE Mid |
| line-13 |  4.4 km | 3 | 16 | W Mid ↔ W Outer |
| line-14 |  2.0 km | 2 | 10 | SE Mid ↔ SE Mid |
| line-15 |  2.2 km | 2 | 10 | NW Mid ↔ N Mid |
| **Total** | **108.5 km** | **74 unique** | **383** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,975 one-way journeys / 50,431 train-km/day |
| Annual traction demand | 238.6 GWh |
| Station/depot PV / storage | 89.7 MW / 649.0 MWh |
| Aggregate charging power | 64.0 MW |
| Dedicated solar plant | 53.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 8.3 km / 62 kWh |
| Lowest traversal charging margin | line-13: 61 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $945 M |
| Stations | $392 M |
| Depots | $230 M |
| Rolling stock | $345 M |
| Dedicated solar plant | $43 M |
| Residual train control | $5.4 M |
| Charging microgrids | $13 M |
| EPC / project services | $135 M |
| **Total city programme** | **$2.11 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $446 M (21.1%) |
| Domestic / local capital | $1.66 bn (78.9%) |
| Annual public construction commitment | $254 M / yr for 7 years |
| Annual post-grace debt service | $215 M / yr |
| External capital saved vs default turnkey sensitivity | $3.35 bn |
| Capital + lifetime external interest saved | $7.55 bn |
| Annual OPEX | $53 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 6 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 832 assets / 4,752 tasks | [`gulu-operations-manifest.json`](operations/gulu-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gulu.toml`](gulu.toml) | Expanded simulator scenario |
| [`gulu.corridor.geojson`](gulu.corridor.geojson) | GIS corridor and stations |
| [`gulu.design-quality.yaml`](gulu.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gulu
```
