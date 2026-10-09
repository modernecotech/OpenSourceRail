# Gujranwala — Urban Rail Network

**Country:** PK · **Population:** 2,300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Gujranwala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$10.45 bn (88.4%) of external capital** and **$13.10 bn of external interest**. Capital plus saved interest totals **$23.56 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **33 lines**, including **28 additional residential lines**. **80.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **149.144 km to 250.219 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **266 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**33 line-local depots** provide **777 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **777 metro-4car trainsets / 3108 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Gujranwala rail network on OpenStreetMap](gujranwala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 33 / 266 / 69 |
| Route length | 351.8 km double track |
| Direct transfers / reachable line pairs | 14.8% / 100.0% |
| Residents within 800 m radial station catchments | 2,245,989 (2020 raster; 63.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 777 × 4-car `metro-4car` trainsets (686 peak revenue) |
| Peak network throughput | 633,600 passengers/hour |
| Practical service capacity | 5,803,200 passenger-trips/day |
| Annual paid-trip planning range | 1059.1–1694.5 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 37.3 km | 26 | 82 | NW Mid ↔ S Outer |
| line-2 | 31.4 km | 22 | 73 | NE Outer ↔ SW Inner |
| line-3 | 18.4 km | 15 | 49 | NW Mid ↔ S Mid |
| line-4 | 28.7 km | 18 | 58 | NW Mid ↔ SE Outer |
| line-5 | 60.0 km | 41 | 36 | NW Mid ↔ NW Mid |
| line-6 |  4.1 km | 7 | 20 | SW Inner ↔ S Inner |
| line-7 |  4.3 km | 3 | 11 | S Mid ↔ S Mid |
| line-8 | 11.0 km | 10 | 32 | W Inner ↔ NW Inner |
| line-9 |  5.1 km | 4 | 14 | S Mid ↔ S Mid |
| line-10 |  5.6 km | 5 | 17 | SE Inner ↔ N Inner |
| line-11 |  8.8 km | 5 | 17 | S Mid ↔ S Mid |
| line-12 |  5.1 km | 4 | 13 | SW Inner ↔ SW Mid |
| line-13 |  6.1 km | 4 | 14 | NW Mid ↔ NW Mid |
| line-14 |  6.2 km | 4 | 15 | S Inner ↔ SW Inner |
| line-15 | 10.1 km | 8 | 27 | W Inner ↔ NE Inner |
| line-16 |  5.0 km | 4 | 14 | NE Mid ↔ NE Mid |
| line-17 |  8.5 km | 5 | 19 | W Inner ↔ SW Inner |
| line-18 |  4.5 km | 3 | 11 | W Mid ↔ W Mid |
| line-19 |  3.6 km | 3 | 11 | N Mid ↔ N Outer |
| line-20 |  6.4 km | 5 | 17 | S Inner ↔ SE Inner |
| line-21 |  4.0 km | 4 | 13 | S Mid ↔ S Mid |
| line-22 |  8.5 km | 10 | 30 | S Inner ↔ SW Inner |
| line-23 | 12.8 km | 9 | 29 | NE Outer ↔ NE Mid |
| line-24 |  4.1 km | 3 | 12 | N Inner ↔ NW Inner |
| line-25 |  7.2 km | 5 | 16 | S Mid ↔ S Mid |
| line-26 |  4.6 km | 5 | 16 | NW Inner ↔ NW Inner |
| line-27 |  4.1 km | 4 | 13 | S Mid ↔ S Mid |
| line-28 |  3.7 km | 3 | 12 | W Mid ↔ SW Inner |
| line-29 |  7.9 km | 5 | 17 | NW Mid ↔ N Mid |
| line-30 |  3.8 km | 5 | 16 | W Inner ↔ W Inner |
| line-31 | 13.3 km | 10 | 28 | NE Outer ↔ NE Outer |
| line-32 |  3.9 km | 3 | 12 | SE Inner ↔ N Inner |
| line-33 |  3.8 km | 4 | 13 | S Mid ↔ S Mid |
| **Total** | **351.8 km** | **266 unique** | **777** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 15,112 one-way journeys / 149,629 train-km/day |
| Annual traction demand | 943.7 GWh |
| Station/depot PV / storage | 222.9 MW / 1,609.5 MWh |
| Aggregate charging power | 339.0 MW |
| Dedicated solar plant | 239.2 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-31: 12.0 km / 129 kWh |
| Lowest traversal charging margin | line-25: 62 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.92 bn |
| Stations | $1.55 bn |
| Depots | $532 M |
| Rolling stock | $870 M |
| Dedicated solar plant | $191 M |
| Residual train control | $18 M |
| Charging microgrids | $70 M |
| EPC / project services | $417 M |
| **Total city programme** | **$6.57 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.37 bn (20.9%) |
| Domestic / local capital | $5.20 bn (79.1%) |
| Annual public construction commitment | $896 M / yr for 7 years |
| Annual post-grace debt service | $771 M / yr |
| External capital saved vs default turnkey sensitivity | $10.45 bn |
| Capital + lifetime external interest saved | $23.56 bn |
| Annual OPEX | $162 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 25 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,249 assets / 11,637 tasks | [`gujranwala-operations-manifest.json`](operations/gujranwala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`gujranwala.toml`](gujranwala.toml) | Expanded simulator scenario |
| [`gujranwala.corridor.geojson`](gujranwala.corridor.geojson) | GIS corridor and stations |
| [`gujranwala.design-quality.yaml`](gujranwala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh gujranwala
```
