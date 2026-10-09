# Nacala — Urban Rail Network

**Country:** MZ · **Population:** 300,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Nacala-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.01 bn (89.1%) of external capital** and **$2.60 bn of external interest**. Capital plus saved interest totals **$4.61 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **78.1%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **31.277 km to 44.970 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **57 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **220 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **220 tram-2car trainsets / 440 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Nacala rail network on OpenStreetMap](nacala-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 57 / 12 |
| Route length | 86.4 km double track |
| Direct transfers / reachable line pairs | 24.4% / 100.0% |
| Residents within 800 m radial station catchments | 136,852 (2020 raster; 60.0% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 220 × 2-car `tram-2car` trainsets (188 peak revenue) |
| Peak network throughput | 124,800 passengers/hour |
| Practical service capacity | 1,160,640 passenger-trips/day |
| Annual paid-trip planning range | 211.8–338.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 10.8 km | 6 | 24 | SE Inner ↔ NE Outer |
| line-2 | 23.6 km | 15 | 53 | E Inner ↔ W Outer |
| line-3 |  9.7 km | 6 | 23 | NE Mid ↔ S Mid |
| line-4 |  3.2 km | 3 | 10 | S Mid ↔ SE Mid |
| line-5 |  3.9 km | 3 | 11 | N Outer ↔ NE Mid |
| line-6 |  4.6 km | 3 | 12 | NE Mid ↔ N Inner |
| line-7 |  2.0 km | 2 | 8 | W Mid ↔ NW Outer |
| line-8 |  6.2 km | 4 | 15 | NE Mid ↔ NE Outer |
| line-9 |  2.8 km | 2 | 9 | NE Outer ↔ N Outer |
| line-10 |  5.0 km | 3 | 13 | SW Inner ↔ S Mid |
| line-11 |  2.6 km | 2 | 9 | W Mid ↔ W Outer |
| line-12 |  9.2 km | 6 | 24 | E Inner ↔ S Outer |
| line-13 |  2.8 km | 2 | 9 | SW Mid ↔ S Mid |
| **Total** | **86.4 km** | **57 unique** | **220** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 40,188 train-km/day |
| Annual traction demand | 126.7 GWh |
| Station/depot PV / storage | 74.3 MW / 535.5 MWh |
| Aggregate charging power | 22.0 MW |
| Dedicated solar plant | 0.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-2: 11.6 km / 58 kWh |
| Lowest traversal charging margin | line-12: 23 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $592 M |
| Stations | $271 M |
| Depots | $178 M |
| Rolling stock | $123 M |
| Residual train control | $4.3 M |
| Charging microgrids | $4.7 M |
| EPC / project services | $82 M |
| **Total city programme** | **$1.26 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $247 M (19.7%) |
| Domestic / local capital | $1.01 bn (80.3%) |
| Annual public construction commitment | $140 M / yr for 10 years |
| Annual post-grace debt service | $127 M / yr |
| External capital saved vs default turnkey sensitivity | $2.01 bn |
| Capital + lifetime external interest saved | $4.61 bn |
| Annual OPEX | $31 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 2 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 552 assets / 2,948 tasks | [`nacala-operations-manifest.json`](operations/nacala-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`nacala.toml`](nacala.toml) | Expanded simulator scenario |
| [`nacala.corridor.geojson`](nacala.corridor.geojson) | GIS corridor and stations |
| [`nacala.design-quality.yaml`](nacala.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh nacala
```
