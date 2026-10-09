# Damietta — Urban Rail Network

**Country:** EG · **Population:** 400,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Damietta-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.53 bn (88.3%) of external capital** and **$4.34 bn of external interest**. Capital plus saved interest totals **$7.88 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **11 lines**, including **8 additional residential lines**. **84.8%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **47.639 km to 64.941 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **83 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**11 line-local depots** provide **421 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **421 light-metro-3car trainsets / 1263 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Damietta rail network on OpenStreetMap](damietta-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 11 / 83 / 17 |
| Route length | 121.9 km double track |
| Direct transfers / reachable line pairs | 30.9% / 100.0% |
| Residents within 800 m radial station catchments | 591,442 (2020 raster; 67.7% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 421 × 3-car `light-metro-3car` trainsets (377 peak revenue) |
| Peak network throughput | 158,400 passengers/hour |
| Practical service capacity | 1,473,120 passenger-trips/day |
| Annual paid-trip planning range | 268.8–430.2 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.1 km | 15 | 79 | N Outer ↔ S Outer |
| line-2 | 17.8 km | 11 | 61 | SE Mid ↔ NW Mid |
| line-3 | 27.3 km | 16 | 85 | SW Outer ↔ NE Outer |
| line-4 |  2.8 km | 2 | 11 | E Inner ↔ E Mid |
| line-5 |  3.0 km | 2 | 12 | SW Inner ↔ SE Inner |
| line-6 |  6.4 km | 6 | 25 | SW Mid ↔ W Inner |
| line-7 |  5.8 km | 4 | 21 | S Outer ↔ SW Outer |
| line-8 |  3.4 km | 4 | 16 | NE Outer ↔ NE Outer |
| line-9 |  4.1 km | 3 | 15 | NE Mid ↔ E Mid |
| line-10 | 13.2 km | 10 | 43 | SE Inner ↔ SW Outer |
| line-11 | 15.1 km | 10 | 53 | S Mid ↔ NE Inner |
| **Total** | **121.9 km** | **83 unique** | **421** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 5,115 one-way journeys / 56,677 train-km/day |
| Annual traction demand | 268.1 GWh |
| Station/depot PV / storage | 73.9 MW / 471.5 MWh |
| Aggregate charging power | 37.0 MW |
| Dedicated solar plant | 55.8 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-7: 5.8 km / 47 kWh |
| Lowest traversal charging margin | line-7: 14 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $1000 M |
| Stations | $454 M |
| Depots | $189 M |
| Rolling stock | $379 M |
| Dedicated solar plant | $45 M |
| Residual train control | $6.1 M |
| Charging microgrids | $7.8 M |
| EPC / project services | $143 M |
| **Total city programme** | **$2.22 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $468 M (21.1%) |
| Domestic / local capital | $1.75 bn (78.9%) |
| Annual public construction commitment | $239 M / yr for 5 years |
| Annual post-grace debt service | $179 M / yr |
| External capital saved vs default turnkey sensitivity | $3.53 bn |
| Capital + lifetime external interest saved | $7.88 bn |
| Annual OPEX | $62 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 18 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 914 assets / 5,278 tasks | [`damietta-operations-manifest.json`](operations/damietta-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`damietta.toml`](damietta.toml) | Expanded simulator scenario |
| [`damietta.corridor.geojson`](damietta.corridor.geojson) | GIS corridor and stations |
| [`damietta.design-quality.yaml`](damietta.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh damietta
```
