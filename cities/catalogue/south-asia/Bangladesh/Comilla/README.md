# Comilla — Urban Rail Network

**Country:** BD · **Population:** 600,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Comilla-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$2.55 bn (88.2%) of external capital** and **$3.20 bn of external interest**. Capital plus saved interest totals **$5.76 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **9 lines**, including **6 additional residential lines**. **61.0%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **51.039 km to 68.396 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **60 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**9 line-local depots** provide **310 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **310 light-metro-3car trainsets / 930 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Comilla rail network on OpenStreetMap](comilla-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 9 / 60 / 10 |
| Route length | 86.9 km double track |
| Direct transfers / reachable line pairs | 25.0% / 100.0% |
| Residents within 800 m radial station catchments | 620,854 (2020 raster; 46.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 310 × 3-car `light-metro-3car` trainsets (276 peak revenue) |
| Peak network throughput | 129,600 passengers/hour |
| Practical service capacity | 1,205,280 passenger-trips/day |
| Annual paid-trip planning range | 220.0–351.9 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 15.6 km | 9 | 53 | NW Mid ↔ E Mid |
| line-2 | 16.8 km | 10 | 56 | SW Outer ↔ NE Inner |
| line-3 | 11.6 km | 8 | 37 | NE Mid ↔ W Mid |
| line-4 |  3.0 km | 3 | 14 | NW Mid ↔ W Mid |
| line-5 |  7.0 km | 8 | 30 | E Inner ↔ SE Mid |
| line-6 |  2.9 km | 2 | 11 | SW Inner ↔ S Inner |
| line-7 |  7.7 km | 4 | 26 | W Inner ↔ NW Outer |
| line-8 | 15.0 km | 11 | 56 | W Inner ↔ SE Outer |
| line-9 |  7.3 km | 5 | 27 | NE Mid ↔ N Outer |
| **Total** | **86.9 km** | **60 unique** | **310** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 4,185 one-way journeys / 40,432 train-km/day |
| Annual traction demand | 191.3 GWh |
| Station/depot PV / storage | 57.0 MW / 380.0 MWh |
| Aggregate charging power | 24.5 MW |
| Dedicated solar plant | 60.0 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-8: 7.7 km / 58 kWh |
| Lowest traversal charging margin | line-9: 22 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $754 M |
| Stations | $267 M |
| Depots | $149 M |
| Rolling stock | $279 M |
| Dedicated solar plant | $48 M |
| Residual train control | $4.3 M |
| Charging microgrids | $5.0 M |
| EPC / project services | $102 M |
| **Total city programme** | **$1.61 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $343 M (21.3%) |
| Domestic / local capital | $1.27 bn (78.7%) |
| Annual public construction commitment | $138 M / yr for 7 years |
| Annual post-grace debt service | $113 M / yr |
| External capital saved vs default turnkey sensitivity | $2.55 bn |
| Capital + lifetime external interest saved | $5.76 bn |
| Annual OPEX | $43 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 10 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 665 assets / 3,846 tasks | [`comilla-operations-manifest.json`](operations/comilla-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`comilla.toml`](comilla.toml) | Expanded simulator scenario |
| [`comilla.corridor.geojson`](comilla.corridor.geojson) | GIS corridor and stations |
| [`comilla.design-quality.yaml`](comilla.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh comilla
```
