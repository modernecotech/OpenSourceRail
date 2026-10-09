# Mecca — Urban Rail Network

**Country:** SA · **Population:** 2,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Mecca-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.85 bn (88.5%) of external capital** and **$10.88 bn of external interest**. Capital plus saved interest totals **$19.73 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **27 lines**, including **21 additional residential lines**. **80.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **182.907 km to 251.816 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **214 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**27 line-local depots** provide **646 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **646 metro-4car trainsets / 2584 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Mecca rail network on OpenStreetMap](mecca-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 27 / 214 / 52 |
| Route length | 324.8 km double track |
| Direct transfers / reachable line pairs | 15.4% / 100.0% |
| Residents within 800 m radial station catchments | 1,127,619 (2020 raster; 61.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 646 × 4-car `metro-4car` trainsets (571 peak revenue) |
| Peak network throughput | 518,400 passengers/hour |
| Practical service capacity | 4,731,840 passenger-trips/day |
| Annual paid-trip planning range | 863.6–1381.7 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 27.8 km | 16 | 58 | W Mid ↔ SE Outer |
| line-2 | 23.4 km | 15 | 53 | SE Outer ↔ W Mid |
| line-3 | 32.6 km | 18 | 64 | NE Outer ↔ SW Mid |
| line-4 | 30.2 km | 16 | 59 | N Mid ↔ S Outer |
| line-5 | 23.3 km | 15 | 52 | E Mid ↔ NW Outer |
| line-6 | 65.7 km | 40 | 35 | W Mid ↔ W Mid |
| line-7 |  6.4 km | 5 | 17 | NE Mid ↔ NE Outer |
| line-8 |  8.7 km | 7 | 24 | N Inner ↔ W Mid |
| line-9 |  4.8 km | 4 | 14 | E Inner ↔ SE Inner |
| line-10 |  4.9 km | 4 | 13 | NE Mid ↔ NE Outer |
| line-11 |  4.8 km | 4 | 13 | NW Mid ↔ NW Mid |
| line-12 |  5.7 km | 4 | 15 | SW Inner ↔ SW Mid |
| line-13 |  4.1 km | 3 | 12 | SE Outer ↔ SE Outer |
| line-14 |  6.5 km | 5 | 18 | E Mid ↔ SE Inner |
| line-15 |  7.6 km | 5 | 17 | W Mid ↔ W Outer |
| line-16 |  5.9 km | 3 | 13 | SE Inner ↔ SE Mid |
| line-17 |  9.5 km | 6 | 21 | SW Mid ↔ SW Mid |
| line-18 |  8.9 km | 6 | 19 | NE Mid ↔ NE Outer |
| line-19 |  4.4 km | 3 | 12 | W Inner ↔ W Mid |
| line-20 |  4.1 km | 3 | 12 | NW Inner ↔ N Mid |
| line-21 |  5.9 km | 4 | 14 | NW Mid ↔ NW Outer |
| line-22 |  5.2 km | 4 | 14 | W Mid ↔ W Mid |
| line-23 |  4.7 km | 6 | 18 | W Mid ↔ W Mid |
| line-24 |  6.3 km | 6 | 18 | NE Mid ↔ NE Mid |
| line-25 |  4.6 km | 5 | 16 | NE Mid ↔ NE Mid |
| line-26 |  4.7 km | 4 | 14 | W Inner ↔ E Inner |
| line-27 |  4.1 km | 3 | 11 | N Mid ↔ N Inner |
| **Total** | **324.8 km** | **214 unique** | **646** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 12,322 one-way journeys / 135,735 train-km/day |
| Annual traction demand | 856.1 GWh |
| Station/depot PV / storage | 182.4 MW / 1,317.0 MWh |
| Aggregate charging power | 277.5 MW |
| Dedicated solar plant | 239.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-6: 9.6 km / 103 kWh |
| Lowest traversal charging margin | line-18: 42 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.71 bn |
| Stations | $1.07 bn |
| Depots | $436 M |
| Rolling stock | $724 M |
| Dedicated solar plant | $192 M |
| Residual train control | $16 M |
| Charging microgrids | $56 M |
| EPC / project services | $351 M |
| **Total city programme** | **$5.56 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.15 bn (20.7%) |
| Domestic / local capital | $4.41 bn (79.3%) |
| Annual public construction commitment | $387 M / yr for 5 years |
| Annual post-grace debt service | $268 M / yr |
| External capital saved vs default turnkey sensitivity | $8.85 bn |
| Capital + lifetime external interest saved | $19.73 bn |
| Annual OPEX | $316 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 45 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,837 assets / 9,564 tasks | [`mecca-operations-manifest.json`](operations/mecca-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`mecca.toml`](mecca.toml) | Expanded simulator scenario |
| [`mecca.corridor.geojson`](mecca.corridor.geojson) | GIS corridor and stations |
| [`mecca.design-quality.yaml`](mecca.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh mecca
```
