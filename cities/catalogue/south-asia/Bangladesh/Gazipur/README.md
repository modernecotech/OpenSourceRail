# Gazipur — Urban Rail Network

**Country:** BD · **Population:** 1,400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gazipur-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$15.66 bn (88.3%) of external capital** and **$19.63 bn of external interest**. Capital plus saved interest totals **$35.29 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **41 lines**, including **35 additional residential lines**. **76.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **164.718 km to 251.654 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **365 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**41 line-local depots** provide **1122 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **1122 metro-4car trainsets / 4488 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Gazipur rail network on OpenStreetMap](gazipur-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 41 / 365 / 86 |
| Route length | 506.9 km double track |
| Direct transfers / reachable line pairs | 11.8% / 100.0% |
| Residents within 800 m radial station catchments | 3,281,598 (2020 raster; 60.5% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 1122 × 4-car `metro-4car` trainsets (1000 peak revenue) |
| Peak network throughput | 787,200 passengers/hour |
| Practical service capacity | 7,231,680 passenger-trips/day |
| Annual paid-trip planning range | 1319.8–2111.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 33.1 km | 27 | 87 | S Mid ↔ NE Mid |
| line-2 | 34.3 km | 23 | 76 | NW Mid ↔ E Outer |
| line-3 | 46.9 km | 30 | 97 | NE Outer ↔ SW Outer |
| line-4 | 45.2 km | 30 | 97 | SE Outer ↔ NW Outer |
| line-5 | 27.8 km | 20 | 68 | N Outer ↔ S Mid |
| line-6 | 66.0 km | 38 | 34 | NW Mid ↔ W Mid |
| line-7 |  6.8 km | 7 | 23 | S Mid ↔ S Mid |
| line-8 |  5.2 km | 4 | 15 | S Inner ↔ S Inner |
| line-9 |  5.1 km | 4 | 15 | N Inner ↔ N Inner |
| line-10 |  5.9 km | 4 | 15 | S Mid ↔ S Mid |
| line-11 |  5.2 km | 4 | 15 | SW Mid ↔ W Mid |
| line-12 |  6.1 km | 5 | 17 | SW Mid ↔ SW Mid |
| line-13 |  6.7 km | 5 | 18 | NE Inner ↔ W Inner |
| line-14 |  5.7 km | 4 | 14 | NW Mid ↔ NW Mid |
| line-15 | 12.9 km | 9 | 28 | SW Mid ↔ S Mid |
| line-16 |  6.7 km | 5 | 18 | NE Inner ↔ NE Mid |
| line-17 |  6.0 km | 5 | 17 | SE Mid ↔ SE Inner |
| line-18 |  7.7 km | 5 | 18 | N Mid ↔ N Outer |
| line-19 |  5.2 km | 6 | 19 | SE Inner ↔ SW Inner |
| line-20 |  6.0 km | 5 | 16 | W Mid ↔ W Mid |
| line-21 |  7.7 km | 7 | 21 | SW Mid ↔ SW Mid |
| line-22 |  8.2 km | 4 | 17 | S Mid ↔ SE Mid |
| line-23 |  6.7 km | 5 | 17 | NW Mid ↔ NW Mid |
| line-24 |  5.1 km | 3 | 12 | SW Mid ↔ SW Mid |
| line-25 |  7.3 km | 6 | 20 | SE Mid ↔ S Inner |
| line-26 |  7.3 km | 5 | 16 | E Outer ↔ SE Outer |
| line-27 | 10.9 km | 10 | 27 | NE Mid ↔ NE Outer |
| line-28 |  6.6 km | 5 | 18 | NE Mid ↔ E Inner |
| line-29 | 12.3 km | 7 | 24 | NW Mid ↔ N Mid |
| line-30 |  8.3 km | 4 | 16 | SE Mid ↔ SE Mid |
| line-31 |  7.4 km | 6 | 20 | SW Mid ↔ W Mid |
| line-32 |  5.1 km | 4 | 15 | S Mid ↔ SW Inner |
| line-33 |  7.5 km | 7 | 21 | NE Mid ↔ N Outer |
| line-34 |  9.7 km | 8 | 27 | NE Inner ↔ SE Mid |
| line-35 |  6.2 km | 7 | 20 | NW Mid ↔ N Mid |
| line-36 |  7.0 km | 5 | 17 | NW Mid ↔ W Mid |
| line-37 |  5.5 km | 4 | 14 | N Outer ↔ N Outer |
| line-38 |  9.1 km | 7 | 24 | SW Mid ↔ S Inner |
| line-39 | 10.4 km | 9 | 29 | W Mid ↔ SW Inner |
| line-40 |  5.2 km | 5 | 17 | SE Inner ↔ S Inner |
| line-41 |  8.7 km | 7 | 23 | SW Outer ↔ SW Mid |
| **Total** | **506.9 km** | **365 unique** | **1122** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 18,832 one-way journeys / 220,364 train-km/day |
| Annual traction demand | 1,389.9 GWh |
| Station/depot PV / storage | 286.9 MW / 2,049.5 MWh |
| Aggregate charging power | 471.0 MW |
| Dedicated solar plant | 582.4 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-3: 12.0 km / 120 kWh |
| Lowest traversal charging margin | line-30: 56 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $4.48 bn |
| Stations | $2.23 bn |
| Depots | $694 M |
| Rolling stock | $1.26 bn |
| Dedicated solar plant | $466 M |
| Residual train control | $25 M |
| Charging microgrids | $99 M |
| EPC / project services | $614 M |
| **Total city programme** | **$9.86 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.08 bn (21.1%) |
| Domestic / local capital | $7.77 bn (78.9%) |
| Annual public construction commitment | $845 M / yr for 7 years |
| Annual post-grace debt service | $690 M / yr |
| External capital saved vs default turnkey sensitivity | $15.66 bn |
| Capital + lifetime external interest saved | $35.29 bn |
| Annual OPEX | $244 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 51 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 3,146 assets / 16,508 tasks | [`gazipur-operations-manifest.json`](operations/gazipur-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gazipur.toml`](gazipur.toml) | Expanded simulator scenario |
| [`gazipur.corridor.geojson`](gazipur.corridor.geojson) | GIS corridor and stations |
| [`gazipur.design-quality.yaml`](gazipur.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gazipur
```
