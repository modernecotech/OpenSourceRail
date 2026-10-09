# Douala — Urban Rail Network

**Country:** CM · **Population:** 3,900,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Douala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$14.54 bn (87.5%) of external capital** and **$18.23 bn of external interest**. Capital plus saved interest totals **$32.77 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **33 lines**, including **28 additional residential lines**. **71.5%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **170.992 km to 353.701 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **284 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**33 line-local depots** provide **986 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **986 metro-6car trainsets / 5916 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Douala rail network on OpenStreetMap](douala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 33 / 284 / 68 |
| Route length | 384.7 km double track |
| Direct transfers / reachable line pairs | 13.3% / 100.0% |
| Residents within 800 m radial station catchments | 2,105,765 (2020 raster; 56.6% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 986 × 6-car `metro-6car` trainsets (879 peak revenue) |
| Peak network throughput | 950,400 passengers/hour |
| Practical service capacity | 8,704,800 passenger-trips/day |
| Annual paid-trip planning range | 1588.6–2541.8 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 35.7 km | 31 | 109 | SE Outer ↔ NW Mid |
| line-2 | 39.5 km | 22 | 83 | NW Outer ↔ SE Mid |
| line-3 | 25.4 km | 19 | 71 | NE Mid ↔ S Mid |
| line-4 | 48.5 km | 30 | 107 | SE Inner ↔ NW Outer |
| line-5 | 43.9 km | 27 | 27 | NE Inner ↔ N Inner |
| line-6 |  4.5 km | 3 | 13 | SE Inner ↔ SE Inner |
| line-7 |  4.9 km | 5 | 18 | W Inner ↔ SW Inner |
| line-8 |  6.3 km | 4 | 17 | NW Mid ↔ NW Mid |
| line-9 |  4.7 km | 3 | 13 | NE Inner ↔ NE Mid |
| line-10 |  3.9 km | 3 | 13 | E Inner ↔ NE Inner |
| line-11 |  5.3 km | 4 | 16 | SE Mid ↔ S Inner |
| line-12 |  5.1 km | 4 | 15 | NW Mid ↔ W Mid |
| line-13 |  7.8 km | 4 | 18 | NE Inner ↔ N Inner |
| line-14 |  4.9 km | 5 | 18 | E Mid ↔ NE Mid |
| line-15 |  6.9 km | 11 | 35 | W Inner ↔ W Inner |
| line-16 |  6.6 km | 5 | 19 | E Inner ↔ SE Mid |
| line-17 |  8.4 km | 6 | 24 | SE Mid ↔ SE Inner |
| line-18 |  6.6 km | 5 | 17 | NW Mid ↔ W Outer |
| line-19 |  4.6 km | 4 | 16 | NE Mid ↔ NE Inner |
| line-20 |  5.3 km | 4 | 16 | S Mid ↔ S Inner |
| line-21 |  8.6 km | 5 | 21 | E Mid ↔ SE Mid |
| line-22 |  9.7 km | 8 | 30 | SW Inner ↔ S Mid |
| line-23 |  4.8 km | 3 | 13 | SE Mid ↔ S Mid |
| line-24 |  9.5 km | 8 | 29 | NE Inner ↔ S Inner |
| line-25 |  6.8 km | 4 | 17 | E Mid ↔ E Mid |
| line-26 |  4.9 km | 4 | 16 | NW Inner ↔ NE Inner |
| line-27 | 14.9 km | 21 | 67 | S Inner ↔ W Mid |
| line-28 |  6.8 km | 4 | 17 | N Inner ↔ NE Mid |
| line-29 |  4.3 km | 3 | 13 | E Inner ↔ E Mid |
| line-30 |  9.5 km | 7 | 27 | W Inner ↔ SW Inner |
| line-31 |  5.2 km | 4 | 16 | N Inner ↔ NE Inner |
| line-32 |  9.9 km | 7 | 27 | S Mid ↔ SE Mid |
| line-33 | 11.0 km | 7 | 28 | SE Mid ↔ SE Mid |
| **Total** | **384.7 km** | **284 unique** | **986** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 15,112 one-way journeys / 168,658 train-km/day |
| Annual traction demand | 1,595.6 GWh |
| Station/depot PV / storage | 234.3 MW / 1,782.0 MWh |
| Aggregate charging power | 528.0 MW |
| Dedicated solar plant | 777.9 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 10.9 km / 164 kWh |
| Lowest traversal charging margin | line-18: 153 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $4.05 bn |
| Stations | $1.57 bn |
| Depots | $641 M |
| Rolling stock | $1.66 bn |
| Dedicated solar plant | $622 M |
| Residual train control | $19 M |
| Charging microgrids | $106 M |
| EPC / project services | $563 M |
| **Total city programme** | **$9.23 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $2.08 bn (22.5%) |
| Domestic / local capital | $7.15 bn (77.5%) |
| Annual public construction commitment | $785 M / yr for 7 years |
| Annual post-grace debt service | $644 M / yr |
| External capital saved vs default turnkey sensitivity | $14.54 bn |
| Capital + lifetime external interest saved | $32.77 bn |
| Annual OPEX | $231 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 59 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 2,599 assets / 13,953 tasks | [`douala-operations-manifest.json`](operations/douala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`douala.toml`](douala.toml) | Expanded simulator scenario |
| [`douala.corridor.geojson`](douala.corridor.geojson) | GIS corridor and stations |
| [`douala.design-quality.yaml`](douala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh douala
```
