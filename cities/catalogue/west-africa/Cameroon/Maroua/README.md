# Maroua — Urban Rail Network

**Country:** CM · **Population:** 500,000 · [National brief](../NATIONAL-BRIEF.md)

This page contains only Maroua-specific results. Shared routing, service, energy, civil, cost, finance, QA and validation methods are defined once in the [deployment planning reference](../../../../../docs/deployment-planning-reference.md).

> [!IMPORTANT]
> **Foreign-capital advantage:** against the default equivalent foreign-turnkey sensitivity, this local plan avoids **$3.02 bn (88.7%) of external capital** and **$3.79 bn of external interest**. Capital plus saved interest totals **$6.82 bn**. See the common reference for interpretation and limitations.

**Population-led network revision (2026-10-09).** The controlled planning inventory contains **13 lines**, including **10 additional residential lines**. **61.3%** of retained 2020 bbox residents are within a 1 km circle of the actual emitted station coordinates. The working target is 80%; remaining areas and station/access alternatives remain in the review. These are distance screens, not current census, surveyed walksheds or fare demand. New common corridor cells have identified junction/structure and access design requirements; no track switch or site approval is inferred. Country fleet, depot, civil, energy, staffing and financing models use the regenerated inventory, with installed quotations and operating acceptance still open. [Line additions and priorities](engineering/alignment/residential-line-expansion.json) · [Actual station coverage and source receipts](engineering/alignment/residential-expansion-evaluation.json).

**Current alignment, depot and production basis.** Core corridors change from **44.342 km to 68.810 km**, with elevated land sections, water-aware radial routes and separately engineered bridge candidates at short water crossings. 0 core fragments retain raster geometry for further curve review. The centre is a design-centroid screen; survey, property, obstacles, foundations and geometry releases remain open. All **66 platform points** pass the retained water-mask screen; footprints, bank stability and access remain open. [Alignment controls](engineering/alignment/core-realignment.json) · [Before/after map](engineering/alignment/core-alignment-comparison.png) · [Water screen](engineering/alignment/station-water-screen.json).

**13 line-local depots** provide **332 full-fleet storage slots**, separate from workshop bays. Fleet length and workload set quantities; PV/storage is included once in depot capital. Site acceptance and installed/land/utility quotations remain open. [Depot costs](engineering/line-depots/README.md). The factory requires **332 light-metro-3car trainsets / 996 cars**, with **18-month facility readiness**, then qualification and manufacture. Integrated openings wait for fleet readiness where production or test paths constrain them. Shared factory capital is counted once; concurrent national loading and supplier commitments remain open. [Factory and dates](engineering/factory/README.md).

Station staffing uses two posts, two normal eight-hour shifts, plus service-window, leave and training cover. Basic wages start at 1.5 times the retained country income proxy, with higher technical/management grades and employer allowances. [Staff](engineering/delivery/README.md) · [Finance](engineering/finance/summary.json). Finance retains country-specific fixed-price, steady-state assumptions; Baghdad’s indexed cashflows are separate.

Auto-planned by the OpenSourceRail design pipeline from the controlled city catalogue, source-locked geospatial inputs and shared templates. Population is counted once within the union of station circles; this is potential radial access, not a verified walkshed or fare-demand estimate. Reachable line pairs include transfers through intermediate lines. [Population radii, denominator and transfer paths](engineering/access/README.md) · [Viaduct beam, foundation and terrain checks](engineering/clearance/README.md). Capital figures are base planning allowances: route-search scores are excluded from money, while special structures and installed-price gaps remain open. [Cost boundary](../../../../../docs/finance/civil-allowance-boundary.md).

## Network

![Maroua rail network on OpenStreetMap](maroua-network-map.png)

| Local measure | Value |
|---|---:|
| Lines / unique stations / interchanges | 13 / 66 / 11 |
| Route length | 90.9 km double track |
| Direct transfers / reachable line pairs | 19.2% / 100.0% |
| Residents within 800 m radial station catchments | 141,400 (2020 raster; 49.2% of bbox) |
| Service span / peak headway | 05:30–02:00 / 3 min |
| Fleet | 332 × 3-car `light-metro-3car` trainsets (294 peak revenue) |
| Peak network throughput | 187,200 passengers/hour |
| Practical service capacity | 1,740,960 passenger-trips/day |
| Annual paid-trip planning range | 317.7–508.4 M |

### Lines

| Line | Length | Stations | Trainsets | Termini |
|---|---:|---:|---:|---|
| line-1 | 23.8 km | 16 | 81 | NE Outer ↔ SW Outer |
| line-2 | 14.5 km | 9 | 47 | N Inner ↔ SW Outer |
| line-3 |  7.4 km | 8 | 32 | W Inner ↔ E Inner |
| line-4 |  6.4 km | 4 | 23 | W Inner ↔ W Mid |
| line-5 |  2.9 km | 2 | 11 | NE Mid ↔ E Mid |
| line-6 |  2.6 km | 2 | 11 | N Inner ↔ NE Inner |
| line-7 |  3.2 km | 3 | 14 | SW Inner ↔ E Inner |
| line-8 |  5.6 km | 4 | 21 | SW Outer ↔ SW Outer |
| line-9 |  5.8 km | 4 | 21 | E Inner ↔ E Mid |
| line-10 |  5.8 km | 4 | 19 | W Inner ↔ W Mid |
| line-11 |  3.4 km | 3 | 14 | SW Mid ↔ SW Inner |
| line-12 |  6.3 km | 4 | 24 | NE Mid ↔ E Mid |
| line-13 |  3.2 km | 3 | 14 | NE Mid ↔ NE Mid |
| **Total** | **90.9 km** | **66 unique** | **332** | |

## Energy

| Local measure | Value |
|---|---:|
| Scheduled service | 6,045 one-way journeys / 42,270 train-km/day |
| Annual traction demand | 200.0 GWh |
| Station/depot PV / storage | 78.5 MW / 542.5 MWh |
| Aggregate charging power | 29.0 MW |
| Dedicated solar plant | 6.6 MW |
| Residual grid/PPA import | 0.0 GWh/yr |
| Worst powered-stop gap | line-12: 6.3 km / 53 kWh |
| Lowest traversal charging margin | line-8: 14 kWh |

## Capital And Funding

| Local CAPEX bucket | Planning value |
|---|---:|
| Civil works | $951 M |
| Stations | $306 M |
| Depots | $198 M |
| Rolling stock | $299 M |
| Dedicated solar plant | $5.3 M |
| Residual train control | $4.5 M |
| Charging microgrids | $6.0 M |
| EPC / project services | $124 M |
| **Total city programme** | **$1.89 bn** |

| Local funding measure | Planning value |
|---|---:|
| Imported / external capital | $384 M (20.3%) |
| Domestic / local capital | $1.51 bn (79.7%) |
| Annual public construction commitment | $163 M / yr for 7 years |
| Annual post-grace debt service | $133 M / yr |
| External capital saved vs default turnkey sensitivity | $3.02 bn |
| Capital + lifetime external interest saved | $6.82 bn |
| Annual OPEX | $49 M / yr |

## Local Evidence

| Package | Current status | Evidence |
|---|---|---|
| Finance | pass | [`summary.json`](engineering/finance/summary.json) |
| Native simulation + degraded cases | pass | [`validation-summary.json`](engineering/simulation/validation-summary.json) |
| SUMO timetable | pass | [`summary.json`](engineering/sumo/summary.json) |
| Independent OSR/SUMO running-time cross-check | pass; junction/authority gate open | [`operations-crosscheck.md`](engineering/simulation/operations-crosscheck.md) |
| GIS package | pass | [`summary.json`](engineering/gis/summary.json) |
| Solar/storage snapshot (operating duty unverified) | pass; 0 findings; 14 grid-only diagnostics | [`summary.json`](engineering/energy/summary.json) |
| Operations, QA and maintenance | 731 assets / 4,155 tasks | [`maroua-operations-manifest.json`](operations/maroua-operations-manifest.json) |

## Local Files And Regeneration

| File | Local role |
|---|---|
| [`design.toml`](design.toml) | Authoritative generated city design |
| [`maroua.toml`](maroua.toml) | Expanded simulator scenario |
| [`maroua.corridor.geojson`](maroua.corridor.geojson) | GIS corridor and stations |
| [`maroua.design-quality.yaml`](maroua.design-quality.yaml) | Coverage, source and civil-quality gates |

```bash
tools/automation/regenerate-city.sh maroua
```
