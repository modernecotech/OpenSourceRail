# Maiduguri — Urban Rail Network

**Country:** NG · **Population:** 1,200,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Maiduguri-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$8.60 bn (89.0%) of external capital** and **$10.78 bn of external interest**. Capital plus saved interest totals **$19.37 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **23 lines**, including **18 additional residential lines**. **80.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **149.223 km to 237.963 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **187 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**23 line-local depots** provide **537 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **537 metro-4car trainsets / 2148 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Maiduguri rail network on OpenStreetMap](maiduguri-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 23 / 187 / 49 |
| Route length | 258.1 km double track |
| Direct transfers / reachable line pairs | 21.3% / 100.0% |
| Residents within 800 m radial station catchments | 777,038 (2020 raster; 63.9% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 537 × 4-car `metro-4car` trainsets (472 peak revenue) |
| Peak network throughput | 441,600 passengers/hour |
| Practical service capacity | 4,017,600 passenger-trips/day |
| Annual paid-trip planning range | 733.2–1173.1 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 24.6 km | 17 | 58 | NW Outer ↔ SE Mid |
| line-2 | 21.6 km | 17 | 56 | W Mid ↔ E Mid |
| line-3 | 26.3 km | 17 | 57 | N Mid ↔ SW Outer |
| line-4 | 25.3 km | 15 | 48 | W Mid ↔ S Outer |
| line-5 | 59.8 km | 40 | 34 | W Mid ↔ W Mid |
| line-6 |  3.2 km | 3 | 11 | S Inner ↔ SW Inner |
| line-7 |  5.7 km | 6 | 19 | N Inner ↔ NE Inner |
| line-8 |  5.3 km | 4 | 15 | N Inner ↔ SE Inner |
| line-9 |  5.2 km | 4 | 15 | NE Inner ↔ N Inner |
| line-10 |  6.1 km | 4 | 15 | SE Inner ↔ SW Inner |
| line-11 |  7.0 km | 7 | 23 | NE Inner ↔ NE Mid |
| line-12 |  3.9 km | 4 | 14 | SE Inner ↔ S Inner |
| line-13 |  5.6 km | 6 | 18 | NE Mid ↔ NE Mid |
| line-14 |  3.5 km | 3 | 11 | SW Inner ↔ S Mid |
| line-15 |  6.0 km | 4 | 15 | SE Mid ↔ SE Mid |
| line-16 |  4.8 km | 4 | 14 | NE Mid ↔ N Mid |
| line-17 |  3.2 km | 3 | 11 | E Inner ↔ SE Inner |
| line-18 |  8.3 km | 6 | 20 | N Mid ↔ E Inner |
| line-19 |  6.6 km | 4 | 16 | W Inner ↔ W Mid |
| line-20 |  9.0 km | 6 | 19 | NE Mid ↔ NE Outer |
| line-21 |  3.8 km | 3 | 12 | E Inner ↔ NE Inner |
| line-22 |  3.3 km | 3 | 11 | N Inner ↔ NW Inner |
| line-23 | 10.1 km | 7 | 25 | SE Mid ↔ W Inner |
| **Total** | **258.1 km** | **187 unique** | **537** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 10,462 one-way journeys / 106,102 train-km/day |
| Annual traction demand | 669.2 GWh |
| Station/depot PV / storage | 157.9 MW / 1,134.5 MWh |
| Aggregate charging power | 249.0 MW |
| Dedicated solar plant | 142.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-4: 13.2 km / 147 kWh |
| Lowest traversal charging margin | line-20: 86 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $2.86 bn |
| Stations | $1.02 bn |
| Depots | $371 M |
| Rolling stock | $601 M |
| Dedicated solar plant | $114 M |
| Residual train control | $13 M |
| Charging microgrids | $50 M |
| EPC / project services | $344 M |
| **Total city programme** | **$5.37 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $1.06 bn (19.8%) |
| Domestic / local capital | $4.30 bn (80.2%) |
| Annual public construction commitment | $636 M / yr for 7 years |
| Annual post-grace debt service | $535 M / yr |
| External capital saved vs default turnkey sensitivity | $8.60 bn |
| Capital + lifetime external interest saved | $19.37 bn |
| Annual OPEX | $129 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 31 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 1,577 assets / 8,125 tasks | [`maiduguri-operations-manifest.json`](operations/maiduguri-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`maiduguri.toml`](maiduguri.toml) | Expanded simulator scenario |
| [`maiduguri.corridor.geojson`](maiduguri.corridor.geojson) | GIS corridor and stations |
| [`maiduguri.design-quality.yaml`](maiduguri.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh maiduguri
```
